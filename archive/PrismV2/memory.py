"""
Slow / fast recurrent memory + per-level inner variational-inference loops.

Spec: §3.3, §3.7, §3.8, §3.10 of ../Prism/docs/PRISM_V2_PROPOSAL.md.

Mathematical formulation
------------------------
Two memory states with structurally different gating biases.

Fast memory M^fast ∈ ℝ^(B, C_M^fast, 12, 12) is paired with the V1 level.
Its ConvGRU is the v1 architecture with bias_u = -1 (moderate writing).

Slow memory M^slow ∈ ℝ^(B, C_M^slow, 6, 6) is paired with the V2 level.
Its ConvGRU has bias_u = -3 (conservative writing, σ(-3) ≈ 0.05) and
takes an additional cross-level input: the spatially pooled V1-level error.
This implements the bottom-up-error component of Rao-Ballard hierarchical PC:

    M_slow_t = ConvGRU_slow( M_slow_{t-1}, V_2^t, E_V2^t, Pool_{12→6}(E_V1^t) )

Multi-head saliency amplification
---------------------------------
Both GRUs amplify their update gates per memory subspace, with each
saliency head k amplifying the corresponding memory channel group:

    u_t,k,c,i,j = u^base_t,k,c,i,j · (1 + λ · S̄^(k)_t(i,j)),  c ∈ group(k)

where the memory channels are partitioned C_M = K · (C_M / K) and S̄ is
the per-batch-normalized saliency map. This is the direct analogue of
multi-head attention's per-head value projection in transformers.

Inner variational-inference loop
--------------------------------
Per-level. At each iteration, re-decode M, recompute prediction error,
take a gradient step on the variational free-energy functional w.r.t. M:

    V̂^(k)_t = decoder( M^(k)_t )       # multi-head decoder
    E^(k)_t = V_t - V̂^(k)_t            # per-head error volume
    M^(k+1)_t = M^(k)_t + ε · ErrBlock( flatten(E^(k)_t), M^(k)_t )

Banach contraction theorem gives geometric convergence to the variational
fixed point under standard smoothness assumptions on `decoder` and `ErrBlock`.

Biological correlates
---------------------
- FastConvGRU ↔ V1 recurrent dynamics (gamma-band rapid integration; Buzsáki
  & Wang 2012).
- SlowConvGRU ↔ dorsolateral prefrontal cortex working-memory delay activity
  (Funahashi et al. 1989; Goldman-Rakic 1995; Constantinidis et al. 2018).
  The conservative gate biases instantiate the chrono-initialization argument
  (Tallec & Ollivier 2018) for setting time constants of multiple env steps.
- Cross-level error pooling ↔ ascending error projections from V1/V2 to
  parietal/prefrontal cortex (Bastos et al. 2012 canonical microcircuit).
- Inner loop ↔ persistent recurrent activity reinterpreted as iterative
  variational inference (Friston 2010; Bastos et al. 2012).
"""
from __future__ import annotations

from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


# ─────────────────────────────────────────────────────────────────────────────
# Multi-head amplification helper (used by both FastConvGRU and SlowConvGRU)
# ─────────────────────────────────────────────────────────────────────────────


def _per_head_amplify(
    u_base: torch.Tensor,      # (B, C_M, H, W)
    S_per_head: torch.Tensor,  # (B, K, H, W)
    lam: torch.Tensor,         # PER-CHANNEL learned vector, shape (C_M,) (softplus'd)
) -> torch.Tensor:
    """Amplify the update gate per memory subspace using per-head saliency.

    Memory channels are split into K contiguous groups; head k amplifies
    the gate values in group k. λ is now a PER-MEMORY-CHANNEL learned vector
    (shape (C_M,)), not a single scalar — so each memory channel has its own
    saliency-amplification rate. This lets channels that carry different content
    (cue identity vs. baseline orientation vs. decision evidence) learn
    different per-step update sensitivities to error-driven amplification.

    Forward formula (with C_M = K · G):

        u_{b, k·G + c, i, j} = u_base_{b, k·G + c, i, j}
                                · (1 + λ_{k·G + c} · S̄^(k)_{b, i, j})

    where S̄ is the per-batch-normalized saliency in [0,1].

    Returns
    -------
    u_t : (B, C_M, H, W)  amplified update gate, clamped to ≤ 1.
    """
    B, C_M, H, W = u_base.shape
    K = S_per_head.shape[1]
    if C_M % K != 0:
        raise ValueError(f"C_M ({C_M}) must be divisible by K ({K}) for per-head amplification.")
    if lam.dim() != 1 or lam.shape[0] != C_M:
        raise ValueError(
            f"lam must be a per-channel vector of shape ({C_M},); got {tuple(lam.shape)}"
        )
    cell_per_head = C_M // K

    # Reshape u_base into (B, K, G, H, W).
    u_reshaped = u_base.view(B, K, cell_per_head, H, W)

    # Reshape lam into (1, K, G, 1, 1) so it broadcasts per memory channel.
    lam_reshaped = lam.view(1, K, cell_per_head, 1, 1)

    # Per-batch-element, per-head normalization of saliency to [0, 1].
    S_expand = S_per_head.unsqueeze(2)  # (B, K, 1, H, W)
    S_max = S_expand.amax(dim=(-1, -2), keepdim=True).detach() + 1e-6
    S_bar = S_expand / S_max  # (B, K, 1, H, W) ∈ [0, 1]

    # Amplify each memory channel by its own learned λ, weighted by its head's saliency.
    u_amplified = u_reshaped * (1.0 + lam_reshaped * S_bar)
    u_amplified = u_amplified.clamp(max=1.0)

    return u_amplified.view(B, C_M, H, W)


# ─────────────────────────────────────────────────────────────────────────────
# Fast memory ConvGRU (V1 level, multi-head saliency amplification)
# ─────────────────────────────────────────────────────────────────────────────


class FastConvGRU(nn.Module):
    """
    V1-level ConvGRU with multi-head saliency-amplified update gate.

    Update equations (with K_fast multi-head saliency):
        cat_t  = [M_prev, P_t]                             (B, C_M+C_V1, H, W)
        cat_e  = [r_t·M_prev, P_t, E_flat_t]               (B, C_M+2·C_V1, H, W)

        r_t        = σ( Conv_{3×3}(cat_t) )                 reset gate
        C̃_t        = tanh( Conv_{3×3}(cat_e) )              candidate
        u_base_t   = σ( Conv_{3×3}(cat_t) + bias_u )        base update gate
        u_t        = per_head_amplify(u_base_t, S_per_head_t, λ)
        M_t        = (1 − u_t)·M_prev + u_t·C̃_t             convex combination

    Args
    ----
    memory_channels  : C_M^fast (default 32)
    feature_channels : C_V1     (default 64; must be divisible by n_heads)
    n_heads          : K_fast   (default 4; must divide both C_M and C_V1)
    update_gate_bias : default -1.0 (σ(-1) ≈ 0.27 — moderate writing)
    init_lambda      : initial value for the softplus-parameterized
                        amplification scalar λ (default 1.0)
    """

    def __init__(
        self,
        memory_channels: int = 32,
        feature_channels: int = 64,
        pixel_channels: int = 3,
        n_heads: int = 4,
        update_gate_bias: float = -1.0,
        init_lambda: float = 1.0,
        kernel_size: int = 3,
    ) -> None:
        super().__init__()
        if memory_channels % n_heads != 0:
            raise ValueError(
                f"memory_channels ({memory_channels}) must be divisible by n_heads ({n_heads})"
            )
        if feature_channels % n_heads != 0:
            raise ValueError(
                f"feature_channels ({feature_channels}) must be divisible by n_heads ({n_heads})"
            )
        self.memory_channels = memory_channels
        self.feature_channels = feature_channels
        self.pixel_channels = pixel_channels
        self.n_heads = n_heads

        pad = kernel_size // 2

        # Reset gate: takes [M, P], outputs C_M-channel σ.
        self.r_conv = nn.Conv2d(
            memory_channels + feature_channels, memory_channels,
            kernel_size=kernel_size, padding=pad,
        )
        # Candidate: takes [r·M, P, E_flat, E_pix_scaled], outputs C_M-channel tanh.
        # E_flat is the multi-head feature error (C channels); E_pix_scaled is the
        # pixel-domain error at the V1 grid scale (pixel_channels channels).
        self.c_conv = nn.Conv2d(
            memory_channels + 2 * feature_channels + pixel_channels, memory_channels,
            kernel_size=kernel_size, padding=pad,
        )
        # Base update gate: takes [M, P], outputs C_M-channel σ.
        self.u_conv = nn.Conv2d(
            memory_channels + feature_channels, memory_channels,
            kernel_size=kernel_size, padding=pad,
        )

        for conv in (self.r_conv, self.c_conv, self.u_conv):
            nn.init.kaiming_uniform_(conv.weight, a=0, mode="fan_in", nonlinearity="relu")
            if conv.bias is not None:
                nn.init.zeros_(conv.bias)
        with torch.no_grad():
            self.u_conv.bias.fill_(update_gate_bias)

        # PER-MEMORY-CHANNEL learned amplification λ. Each of the C_M memory
        # channels gets its own softplus-parameterized amplification rate.
        # Initialized so softplus(λ̃) ≈ init_lambda for every channel.
        # Rationale: the multi-head structure already partitions memory into K
        # subspaces; per-channel λ further lets each channel within a subspace
        # learn its own write sensitivity to error-driven amplification.
        lam_tilde_init = float(torch.log(torch.expm1(torch.tensor(init_lambda))).item())
        self.lambda_tilde = nn.Parameter(torch.full((memory_channels,), lam_tilde_init))

        # PER-PIXEL-CHANNEL learned scale for the pixel-domain error input.
        # Each of the C_pix=3 RGB channels gets its own scaling, initialized at 0.5.
        # Per-channel because R/G/B carry different signal magnitudes (the cue colors
        # differentially load these channels) so it's reasonable to have per-channel
        # scaling rather than one shared scalar.
        pixel_tilde_init = float(torch.log(torch.expm1(torch.tensor(0.5))).item())
        self.pixel_scale_tilde = nn.Parameter(torch.full((pixel_channels,), pixel_tilde_init))

    def forward(
        self,
        M_prev: torch.Tensor,        # (B, C_M^fast, 12, 12)
        P_t: torch.Tensor,           # (B, C_V1, 12, 12)         FiLM-modulated V1 features
        E_per_head: torch.Tensor,    # (B, K, C_V1/K, 12, 12)   per-head V1 feature error
        S_per_head: torch.Tensor,    # (B, K, 12, 12)            per-head V1 saliency
        E_pix: torch.Tensor,         # (B, C_pix, 12, 12)        pixel-domain error at grid scale
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns (M_t, u_t)."""
        B = M_prev.shape[0]

        # Flatten the multi-head feature error along (K, C/K) → C channels.
        E_flat = E_per_head.view(B, self.feature_channels, *E_per_head.shape[-2:])

        # Scale the pixel-domain error PER PIXEL CHANNEL.
        pixel_scale = F.softplus(self.pixel_scale_tilde)              # (C_pix,)
        E_pix_scaled = pixel_scale.view(1, -1, 1, 1) * E_pix          # broadcast over B,H,W

        # Reset gate.
        cat_t = torch.cat([M_prev, P_t], dim=1)
        r_t = torch.sigmoid(self.r_conv(cat_t))

        # Candidate: feature error + pixel error both inform what to write.
        cand_in = torch.cat([r_t * M_prev, P_t, E_flat, E_pix_scaled], dim=1)
        C_tilde = torch.tanh(self.c_conv(cand_in))

        # Base update gate.
        u_base = torch.sigmoid(self.u_conv(cat_t))

        # Per-CHANNEL amplification of update gate (feature saliency).
        lam = F.softplus(self.lambda_tilde)                           # (C_M,)
        u_t = _per_head_amplify(u_base, S_per_head, lam)

        # Memory update.
        M_t = (1.0 - u_t) * M_prev + u_t * C_tilde
        return M_t, u_t


# ─────────────────────────────────────────────────────────────────────────────
# Slow memory ConvGRU (V2 level, conservative biases, cross-level error input)
# ─────────────────────────────────────────────────────────────────────────────


class SlowConvGRU(nn.Module):
    """
    V2-level ConvGRU with conservative gate biases and cross-level error input.

    Same gate-and-candidate structure as FastConvGRU, but:
      - update_gate_bias defaults to -3 (σ(-3) ≈ 0.05 — strongly conservative)
      - the candidate accepts an additional input: the spatially pooled V1-level
        error E_V1 (down-pooled from 12×12 to 6×6). This is the bottom-up
        component of Rao-Ballard hierarchical PC.

    Args
    ----
    memory_channels    : C_M^slow            (default 64)
    feature_channels   : C_V2                (default 128; must be divisible by n_heads)
    cross_in_channels  : C_V1                (channels of the V1-level error after pooling)
    n_heads            : K_slow              (default 4; must divide C_M and C_V2)
    update_gate_bias   : default -3.0
    init_lambda        : default 1.0
    """

    def __init__(
        self,
        memory_channels: int = 64,
        feature_channels: int = 128,
        cross_in_channels: int = 64,
        n_heads: int = 4,
        update_gate_bias: float = -3.0,
        init_lambda: float = 1.0,
        kernel_size: int = 3,
    ) -> None:
        super().__init__()
        if memory_channels % n_heads != 0:
            raise ValueError(
                f"memory_channels ({memory_channels}) must be divisible by n_heads ({n_heads})"
            )
        if feature_channels % n_heads != 0:
            raise ValueError(
                f"feature_channels ({feature_channels}) must be divisible by n_heads ({n_heads})"
            )
        self.memory_channels = memory_channels
        self.feature_channels = feature_channels
        self.cross_in_channels = cross_in_channels
        self.n_heads = n_heads

        pad = kernel_size // 2

        # Reset and update gates: [M_prev, V_2_t]. They do NOT see the cross-level
        # error or the V2 error directly — those affect candidate content only.
        # This keeps the gate decisions about "should I write" separate from
        # the content decisions about "what do I write."
        c_in_gate = memory_channels + feature_channels
        self.r_conv = nn.Conv2d(c_in_gate, memory_channels, kernel_size=kernel_size, padding=pad)
        self.u_conv = nn.Conv2d(c_in_gate, memory_channels, kernel_size=kernel_size, padding=pad)

        # Candidate: [r·M_prev, V_2_t, E_V2_flat, pooled_E_V1]. This is where
        # both same-level and cross-level error information enter.
        c_in_cand = memory_channels + 2 * feature_channels + cross_in_channels
        self.c_conv = nn.Conv2d(c_in_cand, memory_channels, kernel_size=kernel_size, padding=pad)

        for conv in (self.r_conv, self.c_conv, self.u_conv):
            nn.init.kaiming_uniform_(conv.weight, a=0, mode="fan_in", nonlinearity="relu")
            if conv.bias is not None:
                nn.init.zeros_(conv.bias)
        with torch.no_grad():
            self.u_conv.bias.fill_(update_gate_bias)

        # PER-MEMORY-CHANNEL amplification λ. Same rationale as FastConvGRU.
        lam_tilde_init = float(torch.log(torch.expm1(torch.tensor(init_lambda))).item())
        self.lambda_tilde = nn.Parameter(torch.full((memory_channels,), lam_tilde_init))

        # PER-CROSS-CHANNEL learned scale for the V1-level error input.
        # Each of the C_V1 cross-input channels gets its own scaling (was a single
        # scalar). Initialized at 0.5 per channel to start at half-strength
        # relative to within-level error, protecting M_slow from being dominated
        # by V1 noise during early training.
        cross_tilde_init = float(torch.log(torch.expm1(torch.tensor(0.5))).item())
        self.cross_scale_tilde = nn.Parameter(torch.full((cross_in_channels,), cross_tilde_init))

    def forward(
        self,
        M_prev: torch.Tensor,        # (B, C_M^slow, 6, 6)
        V_2: torch.Tensor,           # (B, C_V2, 6, 6)        bottom-up V2 features
        E_V2_per_head: torch.Tensor, # (B, K_slow, C_V2/K_slow, 6, 6)
        S_V2_per_head: torch.Tensor, # (B, K_slow, 6, 6)
        E_V1_pooled: torch.Tensor,   # (B, C_V1, 6, 6)        cross-level pooled error
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns (M_t, u_t)."""
        B = M_prev.shape[0]

        E_V2_flat = E_V2_per_head.view(B, self.feature_channels, *E_V2_per_head.shape[-2:])

        # PER-CHANNEL cross-level error scaling.
        cross_scale = F.softplus(self.cross_scale_tilde)              # (C_V1,)
        E_V1_scaled = cross_scale.view(1, -1, 1, 1) * E_V1_pooled     # broadcast over B,H,W

        # Reset gate.
        cat_gate = torch.cat([M_prev, V_2], dim=1)
        r_t = torch.sigmoid(self.r_conv(cat_gate))

        # Candidate.
        cand_in = torch.cat([r_t * M_prev, V_2, E_V2_flat, E_V1_scaled], dim=1)
        C_tilde = torch.tanh(self.c_conv(cand_in))

        # Base update gate (with conservative -3 bias).
        u_base = torch.sigmoid(self.u_conv(cat_gate))

        # Per-CHANNEL amplification of update gate (V2 saliency).
        lam = F.softplus(self.lambda_tilde)                           # (C_M,)
        u_t = _per_head_amplify(u_base, S_V2_per_head, lam)

        # Memory update.
        M_t = (1.0 - u_t) * M_prev + u_t * C_tilde
        return M_t, u_t


# ─────────────────────────────────────────────────────────────────────────────
# Inner WM loop (variational inference; works with multi-head decoders)
# ─────────────────────────────────────────────────────────────────────────────


class InnerWMLoop(nn.Module):
    """
    K-step inner variational-inference loop.

    For k = 0..K-1:
        V̂^(k)_t = decoder( M^(k)_t )                  # multi-head decoder
        E^(k)_t = V_t (per-head reshape) − V̂^(k)_t    # per-head error
        M^(k+1)_t = M^(k)_t + ε · ErrBlock( flatten(E^(k)_t), M^(k)_t )

    `decoder` is shared with the outer step (passed in at forward time so the
    inner loop's gradient flows through the same decoder weights K+1 times).

    The ErrBlock is a small 2-layer conv block whose output is added to M
    in residual form; the second conv is zero-init'd so the inner loop is
    the identity at random init (no destabilizing effect on untrained M).

    Args
    ----
    memory_channels  : C_M (channels of the memory we're refining)
    feature_channels : C_V (channels of the target features the decoder predicts)
    n_heads          : K (must match the multi-head decoder's head count)
    K                : number of inner iterations (default 2)
    epsilon          : step size of the perturbative update (default 0.1)
    """

    def __init__(
        self,
        memory_channels: int,
        feature_channels: int,
        n_heads: int,
        K: int = 2,
        epsilon: float = 0.1,
        gn_groups: int = 8,
    ) -> None:
        super().__init__()
        if memory_channels % gn_groups != 0:
            raise ValueError(
                f"memory_channels ({memory_channels}) must be divisible by gn_groups ({gn_groups})"
            )
        self.memory_channels = memory_channels
        self.feature_channels = feature_channels
        self.n_heads = n_heads
        self.K = int(K)

        # PER-MEMORY-CHANNEL learned variational-inference step size.
        # Was a hardcoded scalar (0.1); now a learned vector of shape (C_M,)
        # initialized so softplus(ε̃) ≈ epsilon. Each memory channel learns its
        # own step size on the free-energy gradient — channels carrying slowly-
        # varying content (cue identity) can use small steps while channels
        # tracking fast-changing content (per-frame Gabor orientation) can use
        # larger ones, without trading off via a single global rate.
        eps_tilde_init = float(torch.log(torch.expm1(torch.tensor(epsilon))).item())
        self.epsilon_tilde = nn.Parameter(torch.full((memory_channels,), eps_tilde_init))

        c_in = feature_channels + memory_channels  # E_flat (C_V) + M (C_M)
        self.conv1 = nn.Conv2d(c_in, memory_channels, kernel_size=3, padding=1)
        self.gn1 = nn.GroupNorm(gn_groups, memory_channels)
        self.conv2 = nn.Conv2d(memory_channels, memory_channels, kernel_size=3, padding=1)

        nn.init.kaiming_uniform_(self.conv1.weight, a=0, mode="fan_in", nonlinearity="relu")
        nn.init.zeros_(self.conv1.bias)
        nn.init.zeros_(self.conv2.weight)
        nn.init.zeros_(self.conv2.bias)

    def forward(
        self,
        M_t: torch.Tensor,         # (B, C_M, H, W)
        V_target: torch.Tensor,    # (B, C_V, H, W)        full feature volume
        decoder: nn.Module,        # MultiHeadFeatureDecoder
    ) -> torch.Tensor:
        """Returns the K-step refined M_t."""
        if self.K == 0:
            return M_t

        # Per-channel step size, broadcast to (1, C_M, 1, 1) for the residual update.
        eps_per_channel = F.softplus(self.epsilon_tilde).view(1, -1, 1, 1)

        for _k in range(self.K):
            V_hat_per_head = decoder(M_t)  # (B, K, C/K, H, W)
            B = V_hat_per_head.shape[0]
            V_target_per_head = V_target.view(
                B, self.n_heads, self.feature_channels // self.n_heads, *V_target.shape[-2:]
            )
            E_per_head = V_target_per_head - V_hat_per_head  # (B, K, C/K, H, W)
            E_flat = E_per_head.view(B, self.feature_channels, *E_per_head.shape[-2:])
            cat_in = torch.cat([E_flat, M_t], dim=1)
            update = self.conv2(F.gelu(self.gn1(self.conv1(cat_in))))
            M_t = M_t + eps_per_channel * update

        return M_t


# ─────────────────────────────────────────────────────────────────────────────
# Cross-level error pooling helper
# ─────────────────────────────────────────────────────────────────────────────


class CrossLevelErrorPool(nn.Module):
    """LEARNED cross-level error pooling (12 → 6).

    Replaces the previous unweighted `F.adaptive_avg_pool2d`-based helper with
    a learned stride-2 conv. Each output element at the V2 grid is now a
    learned linear combination of its 2×2 V1-grid receptive field, rather than
    a uniform spatial mean. Per-channel input/output is preserved (no channel
    mixing), so the V2-level GRU still receives one channel per V1-feature
    channel — the same downstream interface, but the spatial reduction is
    now learned.

    Implementation: a depthwise stride-2 conv with kernel_size=2. Output spatial
    is exactly half the input (12 → 6), no padding.

    Args
    ----
    cross_in_channels : C_V1, the channel count flowing through (default 64)

    Forward signature: (E_V1_per_head)  →  (B, C_V1, target_h, target_w)
    """

    def __init__(self, cross_in_channels: int = 64) -> None:
        super().__init__()
        self.cross_in_channels = cross_in_channels
        # Depthwise conv (groups=C) so each input channel maps to one output channel.
        # No channel mixing — the V2 GRU sees one channel per V1 feature channel.
        self.pool_conv = nn.Conv2d(
            cross_in_channels, cross_in_channels,
            kernel_size=2, stride=2, padding=0,
            groups=cross_in_channels, bias=True,
        )
        # Init to mean-equivalent: kernel = 1/4 everywhere, bias = 0. Equivalent to
        # the average pool at init, then the conv learns to reweight.
        with torch.no_grad():
            self.pool_conv.weight.fill_(0.25)
            nn.init.zeros_(self.pool_conv.bias)

    def forward(self, E_V1_per_head: torch.Tensor) -> torch.Tensor:
        """E_V1_per_head : (B, K, C_V1/K, H_in, W_in) → (B, C_V1, H_out, W_out)"""
        B, K, c_per_head, H, W = E_V1_per_head.shape
        C = K * c_per_head
        if C != self.cross_in_channels:
            raise ValueError(
                f"CrossLevelErrorPool expects K·C/K = {self.cross_in_channels}; "
                f"got K={K}, C/K={c_per_head}"
            )
        E_flat = E_V1_per_head.reshape(B, C, H, W).contiguous()
        return self.pool_conv(E_flat)


# Keep the old function name as a thin wrapper for backward compatibility with
# any code that imports it directly. Internally just calls a fresh pool with
# the same channel count — this path is NOT used by PrismV2Model (which holds
# a CrossLevelErrorPool instance), so no learned weights are lost.
def pool_cross_level_error(
    E_V1_per_head: torch.Tensor,
    target_h: int = 6,
    target_w: int = 6,
) -> torch.Tensor:
    """Legacy unweighted-pool wrapper. Prefer instantiating CrossLevelErrorPool
    inside the model so the weights are part of the model's state dict.
    """
    B, K, c_per_head, H, W = E_V1_per_head.shape
    C = K * c_per_head
    E_flat = E_V1_per_head.reshape(B, C, H, W).contiguous()
    return F.adaptive_avg_pool2d(E_flat, (target_h, target_w))
