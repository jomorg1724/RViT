"""
RViT+ RL heads — actor and critic that read the encoder's final memory states.

Architectural intent (user spec, 2026-05-21):

  *"Just like we take ALL 3 hidden states for the autoencoder, we will also
   send all 3 hidden states to the actor, and to the critic. Then, we will
   use conv networks bring all recurrent states to the same size. Then
   concatenate channels. Then reduce to the appropriate output dimension
   using mostly conv reduction networks. Both the critic and actor have
   these internal networks."*

So both the actor and the critic are independent modules with the same
structural pattern (parallel to the decoder, but downsampling rather than
upsampling and ending at a finite-dimensional output rather than pixels):

  1. Per-memory-state downsample pyramids reduce each Cᵢ from its native
     grid size to a common target size — the deepest level's (h₃, w₃) by
     default (3×3 in the reference architecture). All-conv, stride-2 blocks.
  2. The three downsampled feature maps are concatenated along the channel
     axis → (B, 3·per_state_channels, h₃, w₃).
  3. A small "reducer" CNN mixes channels at the common spatial size, then
     a final Conv2d with kernel=h₃ and no padding collapses spatial to (1, 1).
     Output is squeezed to (B, output_dim).

  * ActorHead: output_dim = n_actions (discrete logits)
  * CriticHead: output_dim = n_quantiles (scalar V when n_quantiles=1,
    distributional QR-DQN-style when >1)

No `nn.Linear` in the architecture; the final reduction is a Conv2d that
happens to collapse (3, 3) → (1, 1). Everything else is convolutional.
Initial logit/value outputs are small (final-conv std=0.02 init).

This module is self-contained — neither head touches the encoder weights;
they only read its final memory states. That lets the training procedure
mix gradient sources freely (reconstruction + policy + value all attached
to the same encoder).
"""
from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


_GN_GROUPS = 8


def _gn_groups(channels: int) -> int:
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


def _conv_block(in_ch: int, out_ch: int, kernel_size: int = 3, stride: int = 1,
                padding: int = 1) -> nn.Sequential:
    """Conv2d + GroupNorm + GELU. The all-conv building block of these heads."""
    return nn.Sequential(
        nn.Conv2d(in_ch, out_ch, kernel_size=kernel_size, stride=stride, padding=padding),
        nn.GroupNorm(_gn_groups(out_ch), out_ch),
        nn.GELU(),
    )


# Predefined down-chains: how to halve spatial from each supported encoder grid
# to each supported target. (in_h, target_h) → list of (stage_in, stage_out).
# Stride-2 conv (k=3, s=2, p=1) maps H → ⌈H/2⌉, which gives:
#     12 → 6 → 3, and 6 → 3, and 3 → 3 (no halving needed; channel-adapt only).
_DOWN_CHAINS = {
    (3, 3): [],            # identity spatially; channel adapter only
    (6, 3): [(6, 3)],
    (12, 3): [(12, 6), (6, 3)],
    (12, 6): [(12, 6)],
}


class MemoryDownsamplePyramid(nn.Module):
    """Downsample one encoder memory state to the target spatial size via
    stride-2 conv blocks. The structural counterpart of decoder.MemoryUpsamplePyramid
    used in the autoencoder decoder.

    Args
    ----
    in_channels    : memory state channel count.
    in_hw          : (h, w) of this memory state (assumed square).
    out_channels   : output channels after the pyramid.
    target_hw      : (h, w) target — defaults to (3, 3), the deepest encoder
                     level in the reference architecture.

    Channel schedule: in_channels → out_channels, geometric across stages
    (rounded to multiples of _GN_GROUPS=8 for clean GroupNorm groups).
    """

    def __init__(
        self,
        in_channels: int,
        in_hw: Tuple[int, int],
        out_channels: int,
        target_hw: Tuple[int, int] = (3, 3),
    ) -> None:
        super().__init__()
        h_in, w_in = in_hw
        h_t, w_t = target_hw
        if h_in != w_in or h_t != w_t:
            raise NotImplementedError(
                "MemoryDownsamplePyramid currently assumes square grids and targets"
            )
        key = (h_in, h_t)
        if key not in _DOWN_CHAINS:
            raise NotImplementedError(
                f"Downsample chain from {h_in} → {h_t} not defined; "
                f"supported: {sorted(_DOWN_CHAINS)}"
            )

        chain = _DOWN_CHAINS[key]
        n_stages = max(len(chain), 1)

        # Channel schedule.
        channels = [in_channels]
        if n_stages == 1:
            channels.append(out_channels)
        elif n_stages > 1:
            ratio = (out_channels / in_channels) ** (1 / n_stages)
            for k in range(1, n_stages):
                ch = max(_GN_GROUPS, int(round(in_channels * ratio ** k)))
                ch = max(_GN_GROUPS, (ch // _GN_GROUPS) * _GN_GROUPS)
                channels.append(ch)
            channels.append(out_channels)

        layers = []
        if len(chain) == 0:
            # No spatial change — channel adapter only.
            layers.append(_conv_block(in_channels, out_channels,
                                       kernel_size=1, stride=1, padding=0))
        else:
            for stage_idx, (h_in_s, h_out_s) in enumerate(chain):
                in_ch = channels[stage_idx]
                out_ch = channels[stage_idx + 1]
                # Stride-2 conv with k=3, p=1 halves spatial: ⌈H/2⌉.
                layers.append(_conv_block(in_ch, out_ch,
                                           kernel_size=3, stride=2, padding=1))

        self.layers = nn.Sequential(*layers)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.in_hw = in_hw
        self.target_hw = target_hw

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 4:
            raise ValueError(f"MemoryDownsamplePyramid expects 4D; got {tuple(x.shape)}")
        if x.shape[-2:] != self.in_hw:
            raise ValueError(
                f"Input HW {tuple(x.shape[-2:])} != expected {self.in_hw}"
            )
        out = self.layers(x)
        if out.shape[-2:] != self.target_hw:
            raise ValueError(
                f"Output HW {tuple(out.shape[-2:])} != target {self.target_hw}"
            )
        return out


class _ConvReductionHead(nn.Module):
    """Shared backbone for actor and critic heads.

    Architecture:
        final_states (C₁, C₂, C₃)
           │
           ├─► MemoryDownsamplePyramid (each Cᵢ → per_state_channels @ target_hw)
           │       — three independent pyramids, one per memory state
           │
           └─► concat channels → (B, 3·per_state_channels, target_h, target_w)
                 │
                 └─► cnn_reducer (3×3 conv + GN + GELU × 2, then final 3×3 conv
                                  with no padding to collapse target_hw → 1×1)
                       │
                       └─► (B, output_dim, 1, 1) → squeeze → (B, output_dim)

    Args
    ----
    state_channels      : (c1, c2, c3) encoder per-layer channel counts.
    grid_hw             : ((h1,w1),(h2,w2),(h3,w3)) per-layer spatial sizes.
    target_hw           : common spatial size after the downsample pyramids;
                          defaults to the deepest level (3, 3).
    per_state_channels  : channels after each pyramid (before concat). Default 32.
    cnn_hidden          : channels in the reducer CNN's hidden layers. Default 64.
    output_dim          : number of output scalars (n_actions for actor,
                          n_quantiles for critic).
    final_init_std      : Gaussian std for the final-conv init. Small (default
                          0.02) so initial logits/values are near-zero rather
                          than randomly opinionated.
    """

    def __init__(
        self,
        state_channels: Tuple[int, int, int] = (64, 96, 128),
        grid_hw: Tuple[Tuple[int, int], ...] = ((12, 12), (6, 6), (3, 3)),
        target_hw: Tuple[int, int] = (3, 3),
        per_state_channels: int = 32,
        cnn_hidden: int = 64,
        output_dim: int = 1,
        final_init_std: float = 0.02,
    ) -> None:
        super().__init__()
        c1, c2, c3 = state_channels

        self.state_channels = state_channels
        self.grid_hw = grid_hw
        self.target_hw = target_hw
        self.per_state_channels = per_state_channels
        self.cnn_hidden = cnn_hidden
        self.output_dim = output_dim

        # Per-memory-state downsample pyramids.
        self.down_c1 = MemoryDownsamplePyramid(c1, grid_hw[0], per_state_channels, target_hw)
        self.down_c2 = MemoryDownsamplePyramid(c2, grid_hw[1], per_state_channels, target_hw)
        self.down_c3 = MemoryDownsamplePyramid(c3, grid_hw[2], per_state_channels, target_hw)

        cat_channels = 3 * per_state_channels
        t_h, t_w = target_hw

        # CNN reducer: mix at target_hw, then collapse to 1×1.
        # The final conv is sized so that no padding produces (1, 1) output.
        self.cnn_reducer = nn.Sequential(
            nn.Conv2d(cat_channels, cnn_hidden, kernel_size=3, padding=1),
            nn.GroupNorm(_gn_groups(cnn_hidden), cnn_hidden), nn.GELU(),
            nn.Conv2d(cnn_hidden, cnn_hidden, kernel_size=3, padding=1),
            nn.GroupNorm(_gn_groups(cnn_hidden), cnn_hidden), nn.GELU(),
            # Final collapse — kernel = target_hw, padding=0 → (1, 1).
            nn.Conv2d(cnn_hidden, output_dim, kernel_size=t_h, padding=0),
        )

        # Small-Gaussian init on the final layer so initial outputs are
        # near-zero (uniform-ish policy for the actor; near-zero V for the
        # critic). Avoids early opinionatedness without being exactly zero
        # (which can trap optimizers via dead-bias dynamics like run-7).
        final_conv = self.cnn_reducer[-1]
        nn.init.normal_(final_conv.weight, mean=0.0, std=final_init_std)
        nn.init.zeros_(final_conv.bias)

    def forward(self, final_states: Tuple[torch.Tensor, torch.Tensor, torch.Tensor]):
        """Returns the main head's output: (B, output_dim)."""
        c1, c2, c3 = final_states
        u1 = self.down_c1(c1)
        u2 = self.down_c2(c2)
        u3 = self.down_c3(c3)
        cat = torch.cat([u1, u2, u3], dim=1)
        out = self.cnn_reducer(cat).flatten(start_dim=1)   # (B, output_dim)
        return out


class ActorHead(_ConvReductionHead):
    """Discrete-action policy head.

    Output: logits of shape (B, n_actions). Apply a softmax / Categorical
    distribution at the training/sampling site, not here.

    Args
    ----
    n_actions          : action-space size (default 2 — Posner press/wait).
    All other args are forwarded to _ConvReductionHead.
    """

    def __init__(self, n_actions: int = 2, init_action_bias: Optional[list] = None,
                 **kwargs) -> None:
        super().__init__(output_dim=n_actions, **kwargs)
        self.n_actions = n_actions
        # Optional per-action initial bias. Standard RL trick for envs with a
        # "wait" default (e.g. Posner change-detection): bias toward action 0
        # so the initial policy is ~mostly-waiting rather than ~uniform. Without
        # this the model presses immediately on every step → 0 reward → no
        # gradient signal to learn from. The HRA project derived
        # init_action_bias = [0.0, -4.0] empirically (press prob ≈ 0.02 at init).
        if init_action_bias is not None:
            if len(init_action_bias) != n_actions:
                raise ValueError(
                    f"init_action_bias has length {len(init_action_bias)} but "
                    f"n_actions = {n_actions}"
                )
            with torch.no_grad():
                self.cnn_reducer[-1].bias.copy_(
                    torch.tensor(init_action_bias, dtype=torch.float32)
                )

    def forward(self, final_states: Tuple[torch.Tensor, ...]) -> torch.Tensor:
        """Returns logits of shape (B, n_actions)."""
        return super().forward(final_states)


class CriticHead(_ConvReductionHead):
    """Action-conditional distributional value head — QR-DQN style.

    Predicts the return distribution Q(s, a) as N quantiles per (state, action)
    pair. Total output: (B, n_actions, n_quantiles).

    V(s) is *derived* from Q(s, a) and the actor's policy π via expected SARSA
    with stop-gradient on the policy:

        V(s) = Σ_a sg[π(a|s)] · Q(s, a)         (distributional)
        V_scalar(s) = mean over quantiles of V(s)

    The stop-gradient on π is the key correction from PRISM v2's `Q_CRITIC.md`
    §2.4: without it, the actor learns to push π toward whichever action has
    the lowest predicted Q (a circular failure mode where the critic's
    predictions become a target for the actor to game).

    Quantile midpoints τ_i = (i + 0.5) / N are stored as a buffer for use by
    the quantile-Huber loss at training time.

    Args
    ----
    n_actions          : number of discrete actions (must match ActorHead).
    n_quantiles        : N quantiles per (s, a). Default 51 (QR-DQN paper).
                         Setting n_quantiles=1 reduces to a scalar Q per action.
    All other args are forwarded to _ConvReductionHead.
    """

    def __init__(self, n_actions: int = 2, n_quantiles: int = 51, **kwargs) -> None:
        super().__init__(output_dim=n_actions * n_quantiles, **kwargs)
        self.n_actions = n_actions
        self.n_quantiles = n_quantiles
        # Quantile midpoints τ_i = (i + 0.5) / N — used by the quantile-Huber loss.
        taus = (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles
        self.register_buffer("taus", taus)

    def forward(self, final_states: Tuple[torch.Tensor, ...]):
        """Returns Q-distribution of shape (B, n_actions, n_quantiles)."""
        flat = super().forward(final_states)
        B = flat.shape[0]
        return flat.view(B, self.n_actions, self.n_quantiles)

    def derive_V(
        self,
        q_dist: torch.Tensor,
        actor_logits: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Expected-SARSA V from Q and π, stop-grad on π.

            V_dist(s)     = Σ_a sg[π(a|s)] · Q(s, a, :)         shape (B, n_quantiles)
            V_scalar(s)   = mean over quantiles of V_dist          shape (B,)

        Use V_scalar as the baseline in advantage estimation (GAE / TD-λ).
        Use V_dist if a distributional baseline is needed (e.g. for a
        distributional advantage function downstream).

        Args
        ----
        q_dist        : (B, n_actions, n_quantiles) — from this head's forward().
        actor_logits  : (B, n_actions)              — from ActorHead.forward().

        Returns
        -------
        V_dist        : (B, n_quantiles) — per-quantile expected value.
        V_scalar      : (B,)             — scalar expected value.
        """
        if q_dist.dim() != 3:
            raise ValueError(f"q_dist must be (B, n_actions, n_quantiles); got {tuple(q_dist.shape)}")
        if actor_logits.dim() != 2:
            raise ValueError(f"actor_logits must be (B, n_actions); got {tuple(actor_logits.shape)}")
        pi = torch.softmax(actor_logits, dim=-1)            # (B, n_actions)
        pi_sg = pi.detach()                                  # stop-grad — Q_CRITIC.md §2.4
        # V_dist = Σ_a sg[π(a)] · Q(s, a, :) — broadcast across quantile dim.
        V_dist = (pi_sg.unsqueeze(-1) * q_dist).sum(dim=1)   # (B, n_quantiles)
        V_scalar = V_dist.mean(dim=-1)                       # (B,)
        return V_dist, V_scalar


class PredictiveCodingHead(nn.Module):
    """Project a deep specialist state at time ``t-1`` to a prediction of the
    shared shallower state at time ``t``.

    Used by the predictive-coding auxiliary loss: per branch X ∈ {actor, critic},
    we want the actor's / critic's own C₃_X representation to be predictive of
    the next-timestep C₂. The match metric is cosine similarity computed in
    PPO update; the head simply produces a tensor with C₂'s shape from a
    tensor with C₃'s shape.

    Architecture (per spec):
        ConvTranspose2d(c_in, c_in, kernel=4, stride=2, padding=1)   # 3×3 → 6×6
        → Conv3x3(c_in, c_out) + GroupNorm + GELU
        → Conv3x3(c_out, c_out)

    Args
    ----
    c_in           : channels of C_{3, X} (e.g. 128).
    c_out          : channels of C_2 (e.g. 96).
    spatial_in     : (h_in, w_in) of C_{3, X} (e.g. (3, 3)).
    spatial_out    : (h_out, w_out) of C_2 (e.g. (6, 6)).
                     Must be exactly 2× spatial_in for the stride-2 upsample.
    """

    def __init__(
        self,
        c_in: int,
        c_out: int,
        spatial_in: Tuple[int, int] = (3, 3),
        spatial_out: Tuple[int, int] = (6, 6),
    ) -> None:
        super().__init__()
        if (spatial_in[0] * 2, spatial_in[1] * 2) != spatial_out:
            raise ValueError(
                f"PredictiveCodingHead currently only supports 2× spatial upsample; "
                f"got {spatial_in} → {spatial_out}"
            )
        self.upsample = nn.ConvTranspose2d(
            c_in, c_in, kernel_size=4, stride=2, padding=1, bias=True,
        )
        self.refine = nn.Sequential(
            nn.Conv2d(c_in, c_out, kernel_size=3, padding=1, bias=True),
            nn.GroupNorm(_gn_groups(c_out), c_out),
            nn.GELU(),
            nn.Conv2d(c_out, c_out, kernel_size=3, padding=1, bias=True),
        )
        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, c3_prev: torch.Tensor) -> torch.Tensor:
        x = self.upsample(c3_prev)
        x = self.refine(x)
        return x                                          # (B, c_out, h_out, w_out)


# ─────────────────────────────────────────────────────────────────────────
# Quantile Huber loss — utility for QR-DQN-style critic training.
# ─────────────────────────────────────────────────────────────────────────

def quantile_huber_loss(
    predicted_q: torch.Tensor,
    target_q: torch.Tensor,
    taus: torch.Tensor,
    kappa: float = 1.0,
) -> torch.Tensor:
    """QR-DQN's asymmetric Huber loss between predicted and target quantiles.

    Args
    ----
    predicted_q : (B, n_quantiles) — current critic's quantile predictions
                  for the executed action: q_dist[arange(B), actions, :].
    target_q    : (B, n_quantiles_target) — TD-target quantiles (typically
                  the next-state critic's predictions reweighted by reward
                  + γ · V_next). The two N may differ (the target is often
                  a fixed-N estimate).
    taus        : (n_quantiles,) — quantile midpoints of `predicted_q`.
    kappa       : Huber threshold (default 1.0 from the QR-DQN paper).

    Returns
    -------
    scalar loss (mean over batch and quantile pairs).

    Reference: Dabney et al. 2018 (QR-DQN), eq. (10).
    Cross-reference: `Prism/docs/PRISM_V2/Q_CRITIC.md` for our derivation.
    """
    if predicted_q.dim() != 2 or target_q.dim() != 2:
        raise ValueError("predicted_q and target_q must both be (B, n_quantiles)")
    # Pairwise quantile residuals: (B, n_pred, n_target)
    delta = target_q.unsqueeze(1) - predicted_q.unsqueeze(2)
    abs_delta = delta.abs()
    # Element-wise Huber.
    huber = torch.where(
        abs_delta <= kappa,
        0.5 * delta.pow(2),
        kappa * (abs_delta - 0.5 * kappa),
    )
    # Asymmetric quantile weighting |τ - 𝟙(δ<0)|.
    # taus shape (n_pred,) → reshape to (1, n_pred, 1) for broadcast against delta.
    tau_b = taus.view(1, -1, 1)
    weight = (tau_b - (delta < 0).to(delta.dtype)).abs()
    loss = (weight * huber / kappa).mean()
    return loss
