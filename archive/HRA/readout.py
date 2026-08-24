"""
Readout heads — produce action logits (actor), state value (critic), and
optionally pixel reconstructions (for Track B video prediction).

Track A (Posner change-detection) uses ActorHead + CriticHead reading from a
DecisionReadout summary of all three GridCell layer hidden states.

Track B (video prediction) uses the PixelDecoder from decoder.py directly off
the C_1 layer's hidden state; the actor/critic are unused.

Both tracks share the same model.py backbone; this file provides the heads
that swap in for each.
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


def _gn_groups_for(channels: int) -> int:
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


class LayerHead(nn.Module):
    """
    Per-layer reduction module. Maps a single layer's recurrent state to a
    fixed-dim summary vector that both the actor and critic can consume.

    For (C, H, W) inputs with H, W > 3, applies repeated stride-2 conv blocks
    (with GroupNorm + GELU) until the spatial dims are ≤ 3, then flattens and
    applies a linear projection to ``head_dim``. For inputs that are already
    flat or ≤ 3×3 spatially, just flattens + linear. (No information is
    discarded by global average pooling — the brain's columnar/topographic
    structure is preserved through the conv reduction.)

    Args
    ----
    in_channels : channel count of the input state
    in_h, in_w  : spatial dims (use in_h = in_w = 1 for already-flat inputs)
    head_dim    : output dimensionality
    """

    def __init__(self, in_channels: int, in_h: int, in_w: int, head_dim: int) -> None:
        super().__init__()
        layers: List[nn.Module] = []
        c, h, w = in_channels, in_h, in_w
        while h > 3 or w > 3:
            # Stride-2 conv keeps channel count constant. PyTorch's floor
            # formula with k=3, p=1, s=2 gives H_out = (H + 2 − 3) // 2 + 1
            # = floor((H − 1) / 2) + 1 = ceil(H / 2).
            layers.append(nn.Conv2d(c, c, kernel_size=3, stride=2, padding=1))
            layers.append(nn.GroupNorm(_gn_groups_for(c), c))
            layers.append(nn.GELU())
            h = (h + 1) // 2
            w = (w + 1) // 2
        self.conv = nn.Sequential(*layers) if layers else nn.Identity()
        self.flat = nn.Flatten()
        self.linear = nn.Linear(c * h * w, head_dim)

        # Tracking output shape for downstream construction.
        self.head_dim = head_dim
        self._reduced_hw = (h, w)
        self._reduced_c = c

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        x = self.conv(state)
        x = self.flat(x)
        return self.linear(x)


class DecisionReadout(nn.Module):
    """
    Combine per-layer hidden states into a single decision vector that BOTH
    the actor and the critic read from.

    Replacement for the old "mean-pool each layer + concat" readout, which
    discarded spatial structure and (on the iter-1999 post-mortem) was
    drowned in noise from frozen deeper layers. The new design gives each
    layer a conv-based reduction (LayerHead) so spatial structure is
    preserved, then concatenates the per-layer summaries and applies a final
    linear mix to ``decision_dim``.

    The user's brief explicitly required: "all layer recurrent states go to
    both actor and critic networks. They can be reduced using conv networks
    if they are shape (n_channels, H, W). We can use linear layers
    otherwise."  This module is the operationalisation.

    Args
    ----
    layer_specs   : list of (C_ℓ, H_ℓ, W_ℓ) describing each layer's hidden state.
    decision_dim  : output dim, fed to both actor and critic (default 64).
    head_dim      : per-layer LayerHead output dim (default decision_dim).
    """

    def __init__(
        self,
        layer_specs: Sequence[Tuple[int, int, int]],
        decision_dim: int = 64,
        head_dim: int | None = None,
    ) -> None:
        super().__init__()
        head_dim = head_dim or decision_dim
        self.heads = nn.ModuleList(
            [LayerHead(c, h, w, head_dim) for (c, h, w) in layer_specs]
        )
        self.mix = nn.Linear(len(layer_specs) * head_dim, decision_dim)
        self.decision_dim = decision_dim
        self.head_dim = head_dim

    def forward(self, layer_states: List[torch.Tensor]) -> torch.Tensor:
        if len(layer_states) != len(self.heads):
            raise ValueError(
                f"DecisionReadout expects {len(self.heads)} layer states; "
                f"got {len(layer_states)}"
            )
        outs = [head(s) for head, s in zip(self.heads, layer_states)]
        return self.mix(torch.cat(outs, dim=-1))

    def per_layer_contributions(self, layer_states: List[torch.Tensor]) -> List[torch.Tensor]:
        """For interpretability: returns each layer's head output before
        concat+mix, so analysis can ablate one layer at a time."""
        return [head(s) for head, s in zip(self.heads, layer_states)]


class ActorHead(nn.Module):
    """
    Policy logits. Two-layer MLP.

    init_logit_bias: optional per-action bias added to the *output* logits at
    init. For ChangeDetectionEnv with actions [wait, press], setting
    init_logit_bias = [0.0, -4.0] makes the initial policy strongly prefer
    "wait" so episodes don't terminate at t=0 with a false-alarm press before
    the model has learned anything (matches PRISM v1's convention).
    """

    def __init__(
        self,
        decision_dim: int,
        hidden_dim: int = 64,
        n_actions: int = 2,
        init_logit_bias=None,
    ) -> None:
        super().__init__()
        self.fc1 = nn.Linear(decision_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, n_actions)
        if init_logit_bias is not None:
            bias = torch.as_tensor(init_logit_bias, dtype=torch.float32)
            if bias.shape != (n_actions,):
                raise ValueError(
                    f"init_logit_bias must have shape ({n_actions},); got {tuple(bias.shape)}"
                )
            with torch.no_grad():
                self.fc2.bias.copy_(bias)

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.fc2(torch.relu(self.fc1(h)))


class CriticHead(nn.Module):
    """
    Scalar state-value head V(s). Two-layer MLP.

    Kept for ablation purposes — the default HRAModel uses
    DistributionalQHead instead (see Q_CRITIC.md and MODEL_DESIGN.md §6, D6).
    Swap this in by passing critic_kind="scalar" to HRAModel.
    """

    def __init__(self, decision_dim: int, hidden_dim: int = 64) -> None:
        super().__init__()
        self.fc1 = nn.Linear(decision_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.fc2(torch.relu(self.fc1(h))).squeeze(-1)


class DistributionalQHead(nn.Module):
    """
    Action-conditional distributional Q head, QR-DQN style.

    Implements the design in ../Prism/docs/PRISM_V2/Q_CRITIC.md §2.2.

    Outputs N quantile estimates per (state, action) pair:

        Q_φ(s, a; τ_i) ∈ ℝ^{B × |A| × N},   τ_i = (2i − 1)/(2N).

    Mean over quantiles per action:

        Q_φ(s, a) = (1/N) Σ_i Q_φ(s, a; τ_i)    ∈ ℝ^{B × |A|}.

    State value via expected-SARSA with stop-gradient on the policy probs:

        V_φ(s) = Σ_a  sg[π_θ(a|s)] · Q_φ(s, a)   ∈ ℝ^{B}.

    The stop-gradient prevents value-loss gradients from leaking into the
    actor through the V baseline (see Q_CRITIC.md §2.4). Critic-loss is
    computed externally on the executed action's quantile slice using
    losses.quantile_huber_loss.

    Args
    ----
    decision_dim : input dim from DecisionReadout
    hidden_dim   : MLP hidden width (default 64)
    n_actions    : |A| (default 2)
    n_quantiles  : N — number of quantile estimates per action (default 51,
                   matching the PRISM v2 default and C51 conventions)
    """

    def __init__(
        self,
        decision_dim: int,
        hidden_dim: int = 64,
        n_actions: int = 2,
        n_quantiles: int = 51,
    ) -> None:
        super().__init__()
        self.n_actions = n_actions
        self.n_quantiles = n_quantiles

        self.fc1 = nn.Linear(decision_dim, hidden_dim)
        # fc2 outputs |A| · N values flattened, reshaped to (B, |A|, N) below.
        self.fc2 = nn.Linear(hidden_dim, n_actions * n_quantiles)

    def forward(self, h: torch.Tensor, action_logits: torch.Tensor) -> dict:
        """
        h             : (B, decision_dim)
        action_logits : (B, n_actions) — actor's raw logits (NOT softmaxed). Used
                        with detach() inside this head to form V via expected-SARSA.

        Returns dict:
            q_dist   : (B, n_actions, n_quantiles)
            q_values : (B, n_actions)              — mean over quantiles
            value    : (B,)                        — V = Σ sg[π] · Q
        """
        if action_logits.shape[-1] != self.n_actions:
            raise ValueError(
                f"action_logits last dim {action_logits.shape[-1]} != n_actions {self.n_actions}"
            )
        B = h.shape[0]
        z = torch.relu(self.fc1(h))
        q_flat = self.fc2(z)  # (B, |A| · N)
        q_dist = q_flat.view(B, self.n_actions, self.n_quantiles)

        q_values = q_dist.mean(dim=-1)  # (B, |A|)

        # Stop-gradient on π in V = Σ sg[π] · Q. Use log_softmax → exp for
        # numerically stable conversion of logits → probs.
        probs = torch.log_softmax(action_logits, dim=-1).exp().detach()  # (B, |A|)
        value = (probs * q_values).sum(dim=-1)  # (B,)

        return {
            "q_dist": q_dist,    # (B, |A|, N) — full distribution; consumed by quantile_huber_loss
            "q_values": q_values,  # (B, |A|)   — mean-Q, used for diagnostics (e.g. dQ)
            "value": value,      # (B,)         — GAE baseline
        }
