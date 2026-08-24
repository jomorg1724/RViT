"""
Hierarchical decision readout + actor/critic heads.

Spec: §3.9 of ../Prism/docs/PRISM_V2_PROPOSAL.md.

The decision readout pools from BOTH memory levels (M_fast and M_slow), each
with its own multi-head saliency map (S_V1 and S_V2). The pooling produces
a fixed-dimensional state vector s_t consumed by the actor and critic.

Per-level pooling
-----------------
For each level (fast at 12×12, slow at 6×6):
  d^level_t = Conv_{1×1}^{C_M → D}(M^level_t)   evidence projection (D channels)

Three pools:
  Global pool:
    g^level_t = mean_{H,W}(d^level_t)    ∈ ℝ^(B, D)
  Per-head saliency-weighted pool:
    e^level_(k)_t = Σ_{i,j} S^(k)_t(i,j) · d^level_t(:, i, j) / Σ S^(k)
                                          ∈ ℝ^(B, K, D)
  Coarse-grid pool (only at fast level; slow is already 6×6):
    c^fast_(k)_t = AdaptivePool_{2×2}(S^(k) ⊙ d^fast) / AdaptivePool_{2×2}(S^(k))
                                          ∈ ℝ^(B, K, D, 2, 2)

s_t = concat( g^fast, flatten(e^fast), flatten(c^fast),
              g^slow, flatten(e^slow) )           ∈ ℝ^(B, decision_dim)

With defaults D=8, K_fast=K_slow=4:
  decision_dim = D + K_fast·D + K_fast·D·4   +  D + K_slow·D
               = 8 +     32   +    128       +  8 +     32
               = 208

Why per-head pooling
--------------------
The per-head saliency-weighted pools give the actor distinct downstream
signatures from each saliency head. Without per-head pooling, head
specialization is wasted at the decision interface — the actor would only
see an aggregated summary that loses head-distinctness.

The coarse-grid pool (G=2 at the fast level) gives the actor *spatial*
localization of where surprise is concentrated within each head, in addition
to the per-head magnitude that the saliency-weighted pool provides. We do not
add a coarse-grid pool at the slow level because the slow grid is already
small (6×6) and a 2×2 pool of 6×6 adds little spatial structure the global
pool doesn't already capture.

Biological correlate
--------------------
Cortical decision areas — lateral intraparietal area, frontal eye field,
parietal area 5 — integrate spatially organized inputs into action-relevant
summary signals. The pooling here uses derived saliency weights as the
integration kernel, mirroring the saliency-weighted integration documented
in primate LIP (Bisley & Goldberg 2010).
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


# ─────────────────────────────────────────────────────────────────────────────
# Helper: per-head saliency-weighted pool of an evidence volume
# ─────────────────────────────────────────────────────────────────────────────


def saliency_weighted_pool_per_head(
    d: torch.Tensor,            # (B, D, H, W)        evidence volume
    S_per_head: torch.Tensor,   # (B, K, H, W)         per-head saliency
    eps: float = 1e-6,
) -> torch.Tensor:
    """Per-head saliency-weighted spatial mean of an evidence volume.

    For each head k, computes a D-dimensional pooled vector:
        e^(k)_d = Σ_{i,j} S^(k)(i,j) · d_(d,i,j) / (Σ_{i,j} S^(k)(i,j) + ε)

    Returns
    -------
    e_per_head : (B, K, D)
    """
    B, D, H, W = d.shape
    K = S_per_head.shape[1]
    # Broadcast: (B, K, 1, H, W) · (B, 1, D, H, W) → (B, K, D, H, W)
    weighted = S_per_head.unsqueeze(2) * d.unsqueeze(1)
    num = weighted.sum(dim=(-1, -2))                         # (B, K, D)
    denom = S_per_head.sum(dim=(-1, -2)).unsqueeze(-1) + eps  # (B, K, 1)
    return num / denom                                        # (B, K, D)


class SaliencyCoarseGridPerHead(nn.Module):
    """Per-head saliency-weighted features on a (G, G) coarse grid using a
    LEARNED strided conv as the spatial pool.

    For each head k:
        sd_grid = StridedConv(S_k * d)        # learned spatial reduction
        s_grid  = StridedConv_S(S_k)          # learned spatial reduction
        cell_k  = sd_grid / (s_grid + ε)

    The two strided convs are depthwise (one per input channel) so we don't
    introduce cross-channel mixing — this preserves the per-channel decomposition
    the upstream multi-head structure depends on. Initialized to uniform 1/(stride²)
    kernels so the operation is mean-equivalent at init.

    Args
    ----
    decision_channels : D, the channel count of the evidence volume
    spatial_h, spatial_w : input spatial dims (must be divisible by grid)
    grid : G, output grid size (default 2)
    """

    def __init__(self, decision_channels: int, spatial_h: int, spatial_w: int, grid: int = 2) -> None:
        super().__init__()
        if spatial_h % grid != 0 or spatial_w % grid != 0:
            raise ValueError(
                f"spatial_h ({spatial_h}) and spatial_w ({spatial_w}) must be divisible by grid ({grid})"
            )
        self.D = decision_channels
        self.G = grid
        kh, kw = spatial_h // grid, spatial_w // grid
        # Depthwise pool over (D, kh, kw) — D output channels, no channel mixing.
        self.pool_d = nn.Conv2d(
            decision_channels, decision_channels,
            kernel_size=(kh, kw), stride=(kh, kw),
            groups=decision_channels, bias=False,
        )
        # Single-channel pool for the saliency weights (same kernel size).
        self.pool_s = nn.Conv2d(1, 1, kernel_size=(kh, kw), stride=(kh, kw), bias=False)
        # Init: uniform 1/(kh·kw) kernels — equivalent to adaptive_avg_pool at init.
        with torch.no_grad():
            self.pool_d.weight.fill_(1.0 / (kh * kw))
            self.pool_s.weight.fill_(1.0 / (kh * kw))

    def forward(
        self,
        d: torch.Tensor,            # (B, D, H, W)
        S_per_head: torch.Tensor,   # (B, K, H, W)
        eps: float = 1e-6,
    ) -> torch.Tensor:
        K = S_per_head.shape[1]
        out = []
        for k in range(K):
            s_k = S_per_head[:, k:k+1]                 # (B, 1, H, W)
            sd = (s_k * d)                              # (B, D, H, W)
            sd_grid = self.pool_d(sd)                   # (B, D, G, G)
            s_grid = self.pool_s(s_k)                   # (B, 1, G, G)
            out.append(sd_grid / (s_grid + eps))
        return torch.stack(out, dim=1)                  # (B, K, D, G, G)


def saliency_coarse_grid_per_head(
    d: torch.Tensor,
    S_per_head: torch.Tensor,
    grid: int = 2,
    eps: float = 1e-6,
) -> torch.Tensor:
    """Legacy unweighted-pool function preserved for backward compatibility with
    any caller that imports it directly. The model uses SaliencyCoarseGridPerHead
    instead so the spatial reduction is learned. This function still uses the
    parameter-free adaptive average pool.
    """
    B, D, H, W = d.shape
    K = S_per_head.shape[1]
    out = []
    for k in range(K):
        s_k = S_per_head[:, k:k+1]
        sd = (s_k * d)
        sd_grid = F.adaptive_avg_pool2d(sd, grid)
        s_grid = F.adaptive_avg_pool2d(s_k, grid)
        out.append(sd_grid / (s_grid + eps))
    return torch.stack(out, dim=1)


# ─────────────────────────────────────────────────────────────────────────────
# HierarchicalDecisionReadout
# ─────────────────────────────────────────────────────────────────────────────


class HierarchicalDecisionReadout(nn.Module):
    """
    Pools from M_fast and M_slow with per-head saliency weights.

    Args
    ----
    fast_memory_channels  : C_M^fast (default 32)
    slow_memory_channels  : C_M^slow (default 64)
    decision_channels     : D, evidence projection per level (default 8)
    n_heads_fast          : K_fast (default 4)
    n_heads_slow          : K_slow (default 4)
    coarse_grid_fast      : G for the fast-level coarse-grid pool (default 2)
    """

    def __init__(
        self,
        fast_memory_channels: int = 32,
        slow_memory_channels: int = 64,
        decision_channels: int = 8,
        n_heads_fast: int = 4,
        n_heads_slow: int = 4,
        coarse_grid_fast: int = 2,
        fast_h: int = 12,
        fast_w: int = 12,
        slow_h: int = 6,
        slow_w: int = 6,
    ) -> None:
        super().__init__()
        self.fast_memory_channels = fast_memory_channels
        self.slow_memory_channels = slow_memory_channels
        self.decision_channels = decision_channels
        self.n_heads_fast = n_heads_fast
        self.n_heads_slow = n_heads_slow
        self.coarse_grid_fast = coarse_grid_fast
        self.fast_h, self.fast_w = fast_h, fast_w
        self.slow_h, self.slow_w = slow_h, slow_w

        # Per-level 1×1 evidence projections.
        self.d_proj_fast = nn.Conv2d(fast_memory_channels, decision_channels, kernel_size=1, bias=True)
        self.d_proj_slow = nn.Conv2d(slow_memory_channels, decision_channels, kernel_size=1, bias=True)
        for c in (self.d_proj_fast, self.d_proj_slow):
            nn.init.kaiming_uniform_(c.weight, a=0, mode="fan_in", nonlinearity="relu")
            nn.init.zeros_(c.bias)

        # LEARNED global pools (replaces F.adaptive_avg_pool2d to (1,1)).
        # Depthwise conv with kernel = full spatial size, stride = full → 1×1
        # output. Each output is a learned linear combo of all spatial positions
        # for its channel. Init to uniform 1/(H·W) for mean-equivalence at init.
        self.gap_fast = nn.Conv2d(
            decision_channels, decision_channels,
            kernel_size=(fast_h, fast_w), stride=(fast_h, fast_w),
            groups=decision_channels, bias=False,
        )
        self.gap_slow = nn.Conv2d(
            decision_channels, decision_channels,
            kernel_size=(slow_h, slow_w), stride=(slow_h, slow_w),
            groups=decision_channels, bias=False,
        )
        with torch.no_grad():
            self.gap_fast.weight.fill_(1.0 / (fast_h * fast_w))
            self.gap_slow.weight.fill_(1.0 / (slow_h * slow_w))

        # LEARNED coarse-grid pool for the fast level (replaces adaptive_avg_pool2d to (G,G)).
        self.coarse_pool_fast = SaliencyCoarseGridPerHead(
            decision_channels=decision_channels,
            spatial_h=fast_h, spatial_w=fast_w,
            grid=coarse_grid_fast,
        )

    @property
    def output_dim(self) -> int:
        D = self.decision_channels
        K_f, K_s = self.n_heads_fast, self.n_heads_slow
        G = self.coarse_grid_fast
        # Fast: GAP (D) + per-head sal-pool (K_f·D) + per-head coarse (K_f·D·G²)
        # Slow: GAP (D) + per-head sal-pool (K_s·D)
        return D + K_f * D + K_f * D * G * G + D + K_s * D

    def forward(
        self,
        M_fast: torch.Tensor,        # (B, C_M^fast, 12, 12)
        S_V1_per_head: torch.Tensor,  # (B, K_fast, 12, 12)
        M_slow: torch.Tensor,        # (B, C_M^slow, 6, 6)
        S_V2_per_head: torch.Tensor,  # (B, K_slow, 6, 6)
    ) -> torch.Tensor:
        """Returns s_t : (B, output_dim)."""
        # Fast level evidence projection.
        d_fast = self.d_proj_fast(M_fast)  # (B, D, 12, 12)
        # LEARNED global pool (replaces adaptive_avg_pool2d).
        g_fast = self.gap_fast(d_fast).flatten(start_dim=1)                        # (B, D)
        e_fast = saliency_weighted_pool_per_head(d_fast, S_V1_per_head)            # (B, K_f, D)
        c_fast = self.coarse_pool_fast(d_fast, S_V1_per_head)                      # (B, K_f, D, G, G)
        e_fast_flat = e_fast.flatten(start_dim=1)
        c_fast_flat = c_fast.flatten(start_dim=1)

        # Slow level evidence projection.
        d_slow = self.d_proj_slow(M_slow)  # (B, D, 6, 6)
        # LEARNED global pool for slow level.
        g_slow = self.gap_slow(d_slow).flatten(start_dim=1)                        # (B, D)
        e_slow = saliency_weighted_pool_per_head(d_slow, S_V2_per_head)            # (B, K_s, D)
        e_slow_flat = e_slow.flatten(start_dim=1)

        s_t = torch.cat([g_fast, e_fast_flat, c_fast_flat, g_slow, e_slow_flat], dim=-1)
        return s_t


# ─────────────────────────────────────────────────────────────────────────────
# Actor / Critic heads (extended from PRISM v1 with optional bias init)
# ─────────────────────────────────────────────────────────────────────────────


class HeadCompressionBackbone(nn.Module):
    """Learned compression module that takes the raw memory states (M_fast and
    M_slow) plus the readout's saliency-weighted features and produces a
    compact embedding for the actor/critic heads.

    Rationale: instead of relying on unweighted spatial pools to compress the
    memory states, we let the heads see the memories directly through a
    LEARNED compression CNN. This gives the actor/critic full spatial
    information to draw on, with the compression itself trained jointly with
    the policy/value losses.

    Architecture (per memory level):
      M_fast (B, C_M_fast, 12, 12)
        → conv 3×3 stride 2 → (B, C_h, 6, 6)
        → GroupNorm + GELU
        → conv 3×3 stride 2 → (B, C_h, 3, 3)
        → GroupNorm + GELU
        → flatten → (B, C_h · 9)

      M_slow (B, C_M_slow, 6, 6)
        → conv 3×3 stride 2 → (B, C_h, 3, 3)
        → GroupNorm + GELU
        → flatten → (B, C_h · 9)

    Plus the readout's saliency-weighted feature vector s_readout, all
    concatenated and projected to the head input dim.

    Args
    ----
    fast_memory_channels : C_M_fast (default 32)
    slow_memory_channels : C_M_slow (default 64)
    readout_dim          : dim of the input s_readout vector
    hidden_channels      : C_h, intermediate compression conv width (default 32)
    output_dim           : final head input dim (default 256)
    """

    def __init__(
        self,
        fast_memory_channels: int = 32,
        slow_memory_channels: int = 64,
        readout_dim: int = 208,
        hidden_channels: int = 32,
        output_dim: int = 256,
        gn_groups: int = 8,
    ) -> None:
        super().__init__()
        if hidden_channels % gn_groups != 0:
            raise ValueError(
                f"hidden_channels ({hidden_channels}) must be divisible by gn_groups ({gn_groups})"
            )

        # Fast-memory compression: 12×12 → 6×6 → 3×3
        self.fast_conv1 = nn.Conv2d(fast_memory_channels, hidden_channels, kernel_size=3, stride=2, padding=1)
        self.fast_gn1 = nn.GroupNorm(gn_groups, hidden_channels)
        self.fast_conv2 = nn.Conv2d(hidden_channels, hidden_channels, kernel_size=3, stride=2, padding=1)
        self.fast_gn2 = nn.GroupNorm(gn_groups, hidden_channels)

        # Slow-memory compression: 6×6 → 3×3
        self.slow_conv1 = nn.Conv2d(slow_memory_channels, hidden_channels, kernel_size=3, stride=2, padding=1)
        self.slow_gn1 = nn.GroupNorm(gn_groups, hidden_channels)

        # Final projection: concat(fast_flat, slow_flat, readout) → output_dim
        # 12→6→3 with stride-2/k=3/p=1 conv: ⌊(12+2-3)/2⌋+1 = 6, ⌊(6+2-3)/2⌋+1 = 3.
        # 6→3 with stride-2/k=3/p=1 conv: ⌊(6+2-3)/2⌋+1 = 3.
        fast_flat = hidden_channels * 3 * 3
        slow_flat = hidden_channels * 3 * 3
        concat_dim = fast_flat + slow_flat + readout_dim
        self.fc_proj = nn.Linear(concat_dim, output_dim)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_uniform_(m.weight, a=0, mode="fan_in", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=2.0**0.5)
                nn.init.zeros_(m.bias)

        self.output_dim = output_dim

    def forward(
        self,
        M_fast: torch.Tensor,    # (B, C_M_fast, 12, 12)
        M_slow: torch.Tensor,    # (B, C_M_slow, 6, 6)
        s_readout: torch.Tensor, # (B, readout_dim)
    ) -> torch.Tensor:
        """Returns (B, output_dim)."""
        f = F.gelu(self.fast_gn1(self.fast_conv1(M_fast)))     # (B, C_h, 6, 6)
        f = F.gelu(self.fast_gn2(self.fast_conv2(f)))          # (B, C_h, 3, 3)
        f_flat = f.flatten(start_dim=1)                        # (B, C_h·9)

        s = F.gelu(self.slow_gn1(self.slow_conv1(M_slow)))     # (B, C_h, 3, 3)
        s_flat = s.flatten(start_dim=1)                        # (B, C_h·9)

        concat = torch.cat([f_flat, s_flat, s_readout], dim=-1)
        return F.gelu(self.fc_proj(concat))                    # (B, output_dim)


class ActorHead(nn.Module):
    """2-layer MLP over s_t producing action logits.

    init_action_logit_bias: if provided, sets the output-layer bias values
    explicitly. For ChangeDetectionEnv, [0.0, -4.0] is essential to avoid
    bootstrapping starvation (see PRISM v1 readout.py for full discussion).
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        n_actions: int = 2,
        init_action_logit_bias: list[float] | None = None,
    ) -> None:
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, n_actions)

        nn.init.orthogonal_(self.fc1.weight, gain=2.0**0.5)
        nn.init.zeros_(self.fc1.bias)
        nn.init.orthogonal_(self.fc2.weight, gain=0.01)
        nn.init.zeros_(self.fc2.bias)

        if init_action_logit_bias is not None:
            if len(init_action_logit_bias) != n_actions:
                raise ValueError(
                    f"init_action_logit_bias length {len(init_action_logit_bias)} != n_actions {n_actions}"
                )
            with torch.no_grad():
                self.fc2.bias.copy_(torch.tensor(init_action_logit_bias, dtype=torch.float32))

        self.n_actions = n_actions

    def forward(self, s_t: torch.Tensor) -> torch.Tensor:
        h = F.gelu(self.fc1(s_t))
        return self.fc2(h)


class CriticHead(nn.Module):
    r"""2-layer MLP producing a *distributional, action-conditional* critic
    Q_φ(s, a; τ_i) ∈ ℝ^{B × |A| × N_quantiles}.

    Why action-conditional
    ----------------------
    A state-value head V(s) is by construction the policy-marginal
    V_π(s) = Σ_a π(a|s) Q_π(s, a). Under a near-deterministic policy
    (π(a₀) ≈ 0.98 from `init_action_logit_bias=[0,-4]`), V(s) ≈ Q(s, a₀)
    and the critic carries NO information about the value of the alternative
    action — so PPO advantages cannot tell the actor "this action you almost
    never take is actually good." Making Q action-conditional gives the
    critic an internal slot for every action's value, even ones the policy
    rarely picks.

    Why keep distributional
    -----------------------
    The auxiliary `quantile_huber_loss` was already in `losses.py` and is a
    strictly stronger learning signal than scalar MSE: it penalises
    asymmetrically per quantile, so the critic is forced to represent the
    *spread* of returns under the policy, not just the mean. Combining
    distributional + action-conditional gives us a "QR-Q" head:

        Q_φ(s, a; τ_i)   shape  (B, |A|, N)

    Derived quantities (no learnable params)
    ----------------------------------------
        Q_φ(s, a)  =  (1/N) Σ_i Q_φ(s, a; τ_i)             shape (B, |A|)
        V_φ(s)     =  Σ_a sg[π(a|s)] · Q_φ(s, a)            shape (B,)

    The `sg[·]` (stop-gradient) on π is essential: it ensures the value
    loss does NOT flow back through the actor logits — the actor is updated
    only by the PPO surrogate, the critic only by quantile-Huber on Q(s, a_t).

    Architecture
    ------------
        s_t  → Linear(input_dim → hidden_dim) → GELU
             → Linear(hidden_dim → |A| · N_quantiles)
             → reshape to (B, |A|, N_quantiles)

    Args
    ----
    input_dim   : feature dim of s_t (head_backbone.output_dim).
    hidden_dim  : MLP hidden width.
    n_actions   : |A|.
    n_quantiles : N. Quantile levels are fixed at τ_i = (2i−1)/(2N).

    References
    ----------
    [1] Dabney et al. (2018) "Distributional Reinforcement Learning with
        Quantile Regression" (QR-DQN), Eqs. 5–6.
    [2] Wang et al. (2016) "Dueling Network Architectures" — discrete-action
        decomposition Q(s,a) = V(s) + A(s,a) − mean A(s,a). We don't use
        the dueling parameterisation here; we just expose Q(s,a) directly
        and derive V analytically as Σ π Q.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        n_actions: int = 2,
        n_quantiles: int = 51,
    ) -> None:
        super().__init__()
        self.n_actions = n_actions
        self.n_quantiles = n_quantiles
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        # fc2 maps to |A| · N quantile values; we reshape in forward.
        self.fc2 = nn.Linear(hidden_dim, n_actions * n_quantiles)
        nn.init.orthogonal_(self.fc1.weight, gain=2.0**0.5)
        nn.init.zeros_(self.fc1.bias)
        # Small gain on the output: predictions start near 0 so the policy
        # gradient isn't dominated by unrelated value noise during burn-in.
        nn.init.orthogonal_(self.fc2.weight, gain=0.1)
        nn.init.zeros_(self.fc2.bias)

    # ---------------------------------------------------------------- forward

    def forward(self, s_t: torch.Tensor) -> torch.Tensor:
        """Returns the full distributional Q tensor.

        Shape : (B, n_actions, n_quantiles)
        """
        h = F.gelu(self.fc1(s_t))
        q = self.fc2(h)                              # (B, |A|·N)
        # Reshape to (B, |A|, N). Use .view since fc2 output is contiguous.
        return q.view(q.shape[0], self.n_actions, self.n_quantiles)

    # --------------------------------------------------------- helpers --------

    def q_values(self, s_t: torch.Tensor) -> torch.Tensor:
        """Mean over quantiles: Q(s, a) = E_τ[Q(s, a; τ)]. Shape (B, |A|)."""
        return self.forward(s_t).mean(dim=-1)

    @staticmethod
    def state_value(
        q_values: torch.Tensor,         # (B, |A|)
        action_logits: torch.Tensor,    # (B, |A|)
        detach_policy: bool = True,
    ) -> torch.Tensor:
        r"""Compute V(s) = Σ_a π(a|s) · Q(s, a).

        With `detach_policy=True` (default), the policy probabilities are
        detached so this V is a baseline that does NOT propagate gradient
        into the actor. The actor is supervised only by the PPO surrogate.

        Returns
        -------
        v : (B,)
        """
        log_probs = F.log_softmax(action_logits, dim=-1)
        probs = log_probs.exp()
        if detach_policy:
            probs = probs.detach()
        return (probs * q_values).sum(dim=-1)

    # ------------------------------------------------------- legacy alias ----

    def mean_value(self, s_t: torch.Tensor) -> torch.Tensor:
        """Backward-compat shim: returns V via uniform-policy averaging.

        Mostly for old test-code paths that just want a scalar critic output.
        Real training code should use `state_value(q, logits)` to get V_π(s).
        """
        q = self.q_values(s_t)
        return q.mean(dim=-1)
