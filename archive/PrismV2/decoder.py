"""
Top-down generative decoders + multi-head saliency.

Spec: §3.5 and §3.6 of ../Prism/docs/PRISM_V2_PROPOSAL.md.

Three decoders live in this module:

(1) PixelDecoder — unchanged from PRISM v1. Maps M_fast → x̂ ∈ ℝ^(B,3,50,50).
    The principal collapse-proof PC target. Trained by the dominant pixel-level
    PC loss; provides the saliency signal at the V1 level via the residual
    pixel error.

(2) MultiHeadFeatureDecoder — new in v2. Maps M → multi-head feature predictions
    V̂^(k) ∈ ℝ^(B, K, C/K, H, W). Used at both V1 and V2 levels to produce
    per-head saliency maps. Recipe 1 of the v2 multi-head saliency design:
    each head k predicts a disjoint slice of the target's feature channels,
    so heads specialize via the channel partition without requiring any
    auxiliary specialization loss.

(3) Helpers: pixel_saliency_map() (unchanged from v1), multi_head_saliency() (new).

Mathematical formulation (Recipe 1 multi-head saliency)
-------------------------------------------------------
For a target feature volume V ∈ ℝ^(B, C, H, W) and per-head predictions
V̂^(k) ∈ ℝ^(B, C/K, H, W) for k = 1..K:

    E^(k) = V[:, group(k), :, :] − V̂^(k)              ∈ ℝ^(B, C/K, H, W)
    S^(k)(i,j) = sqrt( (K/C) Σ_{c ∈ group(k)} E^(k)_{c,i,j}² + ε )

stacking gives S ∈ ℝ^(B, K, H, W). Heads specialize because they see disjoint
feature channels of V, and the upstream stem's emergent channel groupings —
which we expect to track distinct visual feature dimensions — are inherited
by the saliency heads.

The mean-over-channels (with the K/C normalization) makes per-head saliency
magnitude comparable across different K choices, so head-count ablations
keep the saliency-amplification scale roughly invariant.

Initialization (V̂ ≈ 0 at random init)
---------------------------------------
The output convs of every decoder are zero-init'd. This ensures the network
starts maximally surprised by everything (E ≈ V, S ≈ ‖V‖), which is the
right initial condition for a generative model under construction.

Biological correlate
--------------------
- PixelDecoder ↔ V1-projecting feedback layers in extrastriate cortex
  (carrying top-down predictions of pixel-level structure).
- MultiHeadFeatureDecoder ↔ multiple feedback subpopulations from higher
  cortex that target distinct V1/V2 functional columns
  (color-selective regions in V4, orientation columns in V1, etc.).

Complexity / params (default sizes K=4)
---------------------------------------
PixelDecoder: ~7K (unchanged from v1).
MultiHeadFeatureDecoder at V1: shared first conv 32·32·9 ≈ 9.2K; K=4
    head convs each 32·16·9 ≈ 4.6K, total head convs 18.4K. Sum ≈ 28K.
MultiHeadFeatureDecoder at V2: shared first conv 64·64·9 ≈ 36.9K; K=4
    head convs each 64·32·9 ≈ 18.4K, total head convs 73.7K. Sum ≈ 110K.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


# ─────────────────────────────────────────────────────────────────────────────
# PixelDecoder (unchanged from PRISM v1)
# ─────────────────────────────────────────────────────────────────────────────


class PixelDecoder(nn.Module):
    """
    Top-down decoder mapping memory state M to a *raw-pixel* prediction x̂.

    See PRISM v1 ../Prism/decoder.py for the full design rationale (BYOL-style
    collapse hazard prevention via pixel-level prediction). Identical here.

    Args
    ----
    memory_channels  : C_M (default 32)
    out_channels     : output pixel channels (default 3 for RGB)
    out_h, out_w     : pixel resolution (default 50, 50)
    hidden_channels  : decoder hidden width (default 16)
    """

    def __init__(
        self,
        memory_channels: int = 32,
        out_channels: int = 3,
        out_h: int = 50,
        out_w: int = 50,
        hidden_channels: int = 16,
        gn_groups: int = 8,
    ) -> None:
        super().__init__()
        if hidden_channels % gn_groups != 0:
            raise ValueError(
                f"hidden_channels ({hidden_channels}) must be divisible by gn_groups ({gn_groups})"
            )

        self.memory_channels = memory_channels
        self.out_channels = out_channels
        self.out_h = out_h
        self.out_w = out_w

        self.conv_pre = nn.Conv2d(memory_channels, hidden_channels, kernel_size=3, padding=1)
        self.gn_pre = nn.GroupNorm(gn_groups, hidden_channels)
        self.conv_post = nn.Conv2d(hidden_channels, hidden_channels, kernel_size=3, padding=1)
        self.gn_post = nn.GroupNorm(gn_groups, hidden_channels)
        self.conv_out = nn.Conv2d(hidden_channels, out_channels, kernel_size=3, padding=1)

        for c in (self.conv_pre, self.conv_post):
            nn.init.kaiming_uniform_(c.weight, a=0, mode="fan_in", nonlinearity="relu")
            nn.init.zeros_(c.bias)
        nn.init.zeros_(self.conv_out.weight)
        nn.init.zeros_(self.conv_out.bias)

        # Second output head: pixel prediction at the memory/V1 grid scale (no upsampling).
        # Taps the same hidden features as conv_out but before the interpolate step.
        # Used to compute pixel saliency at 12×12 without any lossy spatial pooling.
        self.conv_out_grid = nn.Conv2d(hidden_channels, out_channels, kernel_size=3, padding=1)
        nn.init.zeros_(self.conv_out_grid.weight)
        nn.init.zeros_(self.conv_out_grid.bias)

    def forward(self, M: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """M : (B, C_M, H_in, W_in)  →  (x̂_full, x̂_grid)

        x̂_full : (B, C_out, out_h, out_w)  — full-res pixel prediction (50×50)
        x̂_grid : (B, C_out, H_in, W_in)   — grid-scale pixel prediction (12×12)
        """
        if M.shape[1] != self.memory_channels:
            raise ValueError(
                f"PixelDecoder expects {self.memory_channels} channels; got {M.shape[1]}"
            )
        h = F.gelu(self.gn_pre(self.conv_pre(M)))        # (B, C_h, H_in, W_in)
        x_hat_grid = self.conv_out_grid(h)               # (B, C_out, H_in, W_in) — grid scale
        h = F.interpolate(h, size=(self.out_h, self.out_w), mode="bilinear", align_corners=False)
        h = F.gelu(self.gn_post(self.conv_post(h)))
        x_hat = self.conv_out(h)                         # (B, C_out, out_h, out_w)
        return x_hat, x_hat_grid


def pixel_saliency_map(
    x: torch.Tensor,
    x_hat: torch.Tensor,
    eps: float = 1e-6,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Pixel-level prediction error and per-location RMS saliency.

    Both x and x_hat must already be at the same (grid) resolution — call this
    with the 12×12 grid-scale outputs of PixelDecoder so no spatial pooling is
    needed and MPS divisibility constraints are never hit.

    Returns (E_pix, S_t) with shapes
      E_pix : (B, C_x, H, W)
      S_t   : (B, 1,   H, W)
    """
    if x.shape != x_hat.shape:
        raise ValueError(f"pixel_saliency_map shape mismatch {tuple(x.shape)} vs {tuple(x_hat.shape)}")
    E_pix = x - x_hat
    S_t = (E_pix.pow(2).mean(dim=1, keepdim=True) + eps).sqrt()
    return E_pix, S_t


# ─────────────────────────────────────────────────────────────────────────────
# MultiHeadFeatureDecoder (new in v2)
# ─────────────────────────────────────────────────────────────────────────────


class MultiHeadFeatureDecoder(nn.Module):
    """
    K-head decoder mapping memory M to per-head feature predictions.

    Each head k predicts a disjoint slice of the target feature channels:
    head k owns target channels [k·C/K, (k+1)·C/K). The decoder partially
    shares its first conv across heads (for parameter efficiency) but uses
    independent output convs per head (so each head can specialize).

    Args
    ----
    memory_channels : C_M (default 32 for V1-level fast memory)
    feature_channels: C_target — total channels of the target feature volume
                       (must be divisible by n_heads). Default 64 for V1.
    n_heads         : K (default 4)
    spatial_h       : output spatial H (default 12 for V1; 6 for V2)
    spatial_w       : output spatial W
    gn_groups       : GroupNorm groups (default 8)

    Forward signature: M  ->  V̂_per_head ∈ ℝ^(B, K, C/K, H, W)
    """

    def __init__(
        self,
        memory_channels: int = 32,
        feature_channels: int = 64,
        n_heads: int = 4,
        spatial_h: int = 12,
        spatial_w: int = 12,
        gn_groups: int = 8,
    ) -> None:
        super().__init__()
        if feature_channels % n_heads != 0:
            raise ValueError(
                f"feature_channels ({feature_channels}) must be divisible by n_heads ({n_heads})"
            )
        if memory_channels % gn_groups != 0:
            raise ValueError(
                f"memory_channels ({memory_channels}) must be divisible by gn_groups ({gn_groups})"
            )

        self.memory_channels = memory_channels
        self.feature_channels = feature_channels
        self.n_heads = n_heads
        self.channels_per_head = feature_channels // n_heads
        self.spatial_h = spatial_h
        self.spatial_w = spatial_w

        # Shared first conv: takes M → hidden representation. The hidden
        # representation is a richer encoding of memory that all heads can
        # draw from. Sharing this layer makes the model parameter-efficient
        # while still allowing per-head specialization in the output convs.
        self.conv_shared = nn.Conv2d(memory_channels, memory_channels, kernel_size=3, padding=1)
        self.gn_shared = nn.GroupNorm(gn_groups, memory_channels)

        # Per-head output convs. Each head k has its own conv that maps the
        # shared hidden representation to its (C/K)-channel prediction slice.
        # This is what gives heads their independent identity — gradients
        # from each head's saliency only flow through that head's output conv.
        self.head_convs = nn.ModuleList([
            nn.Conv2d(memory_channels, self.channels_per_head, kernel_size=3, padding=1)
            for _ in range(n_heads)
        ])

        # Init: Kaiming on shared conv; zero-init on per-head output convs so
        # V̂^(k) ≈ 0 at random init (network starts maximally surprised).
        nn.init.kaiming_uniform_(self.conv_shared.weight, a=0, mode="fan_in", nonlinearity="relu")
        nn.init.zeros_(self.conv_shared.bias)
        for c in self.head_convs:
            nn.init.zeros_(c.weight)
            nn.init.zeros_(c.bias)

    def forward(self, M: torch.Tensor) -> torch.Tensor:
        """
        M : (B, C_M, H, W)  with H, W matching the configured spatial dims.

        Returns
        -------
        V_hat_per_head : (B, n_heads, channels_per_head, H, W)
        """
        if M.shape[1] != self.memory_channels:
            raise ValueError(
                f"MultiHeadFeatureDecoder expects {self.memory_channels} channels; got {M.shape[1]}"
            )
        if M.shape[-2:] != (self.spatial_h, self.spatial_w):
            raise ValueError(
                f"MultiHeadFeatureDecoder expects spatial {(self.spatial_h, self.spatial_w)}; "
                f"got {tuple(M.shape[-2:])}"
            )

        # Shared hidden representation.
        h = F.gelu(self.gn_shared(self.conv_shared(M)))  # (B, C_M, H, W)

        # Per-head output predictions.
        head_outputs = [conv(h) for conv in self.head_convs]  # K × (B, C/K, H, W)

        # Stack along a new head dimension.
        V_hat_per_head = torch.stack(head_outputs, dim=1)  # (B, K, C/K, H, W)
        return V_hat_per_head


def multi_head_saliency(
    V_target: torch.Tensor,        # (B, C, H, W)
    V_hat_per_head: torch.Tensor,  # (B, K, C/K, H, W)
    eps: float = 1e-6,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Compute per-head prediction error and per-head saliency from a target volume
    and per-head predictions.

    Parameters
    ----------
    V_target       : (B, C, H, W)        full feature volume from the upstream stem
    V_hat_per_head : (B, K, C/K, H, W)   per-head predictions
    eps            : sqrt-stability ε

    Returns
    -------
    E_per_head : (B, K, C/K, H, W)  per-head, sign-preserving prediction error
                                     (head k owns channels [k·C/K, (k+1)·C/K))
    S_per_head : (B, K, H, W)        per-head per-location saliency, normalized
                                     so magnitude is comparable across head counts

    Mathematical formulation
    ------------------------
    Let group(k) = [k·C/K, (k+1)·C/K). Then for each head k:

        E^(k)_{c,i,j} = V_{target, c+k·C/K, i, j} − V̂^(k)_{c, i, j}
        S^(k)(i,j) = sqrt( (1/(C/K)) · Σ_c E^(k)_{c,i,j}² + ε )

    The per-head normalization (1 / channels_per_head, not 1 / C) makes
    per-head saliency magnitude scale-invariant to K.
    """
    if V_target.dim() != 4:
        raise ValueError(f"V_target must be 4D (B,C,H,W); got {V_target.dim()}D")
    if V_hat_per_head.dim() != 5:
        raise ValueError(f"V_hat_per_head must be 5D (B,K,C/K,H,W); got {V_hat_per_head.dim()}D")
    B, K, c_per_head, H, W = V_hat_per_head.shape
    C = V_target.shape[1]
    if C != K * c_per_head:
        raise ValueError(
            f"V_target has {C} channels but V_hat_per_head implies {K * c_per_head} "
            f"(K={K} heads × {c_per_head} channels/head)"
        )
    if V_target.shape[-2:] != V_hat_per_head.shape[-2:]:
        raise ValueError(
            f"Spatial mismatch: V_target {tuple(V_target.shape[-2:])} vs "
            f"V_hat_per_head {tuple(V_hat_per_head.shape[-2:])}"
        )

    # Reshape V_target into per-head slices: (B, K, C/K, H, W).
    # Channel-contiguous: head k gets channels [k*C/K, (k+1)*C/K).
    V_target_per_head = V_target.view(B, K, c_per_head, H, W)

    # Per-head prediction error, sign-preserving.
    E_per_head = V_target_per_head - V_hat_per_head  # (B, K, C/K, H, W)

    # Per-head per-location RMS saliency. Mean over the per-head channel slice
    # (dim=2) gives the right magnitude scaling that's invariant to K.
    S_per_head = (E_per_head.pow(2).mean(dim=2) + eps).sqrt()  # (B, K, H, W)

    return E_per_head, S_per_head
