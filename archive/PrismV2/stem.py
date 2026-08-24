"""
Two-level perceptual hierarchy: V1 stem + V2 stem.

Spec: §3.1 and §3.2 of ../Prism/docs/PRISM_V2_PROPOSAL.md.

Mathematical formulation
------------------------
The feedforward perceptual hierarchy consists of two convolutional stems
operating in cascade:

    x_t  ─►  V1Stem  ─►  V_1^t  ∈ ℝ^(B, C_V1, 12, 12)        (V1-like)
                                │
                                ▼
                         V2Stem  ─►  V_2^t  ∈ ℝ^(B, C_V2, 6, 6)   (V2/V4-like)

V1 stem (unchanged from PRISM v1):
    V_1^(1) = GELU(GN(Conv_{3→C_V1/2, k=5, s=2, p=2}(x)))      # 50→25
    V_1^(2) = GELU(GN(Conv_{C_V1/2→C_V1, k=3, s=2, p=0}(.)))  # 25→12
    V_1     = GELU(GN(Conv_{C_V1→C_V1, k=3, s=1, p=1}(.)))    # 12→12

V2 stem (new in v2):
    V_2^(1) = GELU(GN(Conv_{C_V1→C_V2, k=3, s=2, p=1}(V_1)))  # 12→6
    V_2     = GELU(GN(Conv_{C_V2→C_V2, k=3, s=1, p=1}(.)))   # 6→6

Spatial-arithmetic check for V2:  ⌊(12 + 2 − 3)/2⌋ + 1 = 6.

Default channel counts:
    C_V1 = 64,  mid_V1 = 32   (one cell per Gabor patch quadrant fits in V_2)
    C_V2 = 128                (channel-doubling mirrors ventral-stream feature
                               expansion; DiCarlo, Zoccolan, & Rust 2012)

Why these dims and strides
--------------------------
The V_2 spatial size of 6×6 is deliberate: with the 4-Gabor scene structure
in `env.py`, each 25×25 Gabor patch maps to exactly one cell at the V_2
resolution (50/25/2 = 1 cell per 25-px region, 6×6 = 4×4 quadrants + context).
This is *not* enforced — the network discovers whether to use the resolution
that way — but the geometry is set up so that quadrant-aligned representations
are easy to learn if useful.

The doubling of channel count from 64 → 128 mirrors the well-documented
expansion in feature-dimension as one ascends the ventral stream
(Felleman & Van Essen 1991; DiCarlo et al. 2012). The expansion gives the
V2 level expressive headroom for binding orientation × color × spatial
configuration into single cells, in analogy to V4's higher-order tuning.

Biological correlates
---------------------
- V1Stem ↔ primary visual cortex V1: orientation-selective simple cells
  with small receptive fields covering local image patches (Hubel & Wiesel 1962;
  De Valois & De Valois 1988).
- V2Stem ↔ extrastriate cortex V2/V4: larger receptive fields with
  orientation, color, contour, and texture tuning (Hegdé & Van Essen 2004;
  Pasupathy & Connor 2002).

Complexity / params (default)
-----------------------------
V1Stem: 3·32·25 + 32·64·9 + 64·64·9 = 2400 + 18432 + 36864 ≈ 57.7K weights.
V2Stem: 64·128·9 + 128·128·9 = 73728 + 147456 ≈ 221.2K weights.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


_GN_GROUPS = 8


# ─────────────────────────────────────────────────────────────────────────────
# V1 stem (unchanged from PRISM v1)
# ─────────────────────────────────────────────────────────────────────────────


class V1Stem(nn.Module):
    """
    V1-like primary visual cortex encoder.

    Maps RGB observations (B, 3, 50, 50) to a feature volume (B, C_V1, 12, 12).

    Args
    ----
    in_channels  : input image channels (default 3 for RGB)
    mid_channels : channels at the intermediate (25×25) stage (default C_V1/2 = 32)
    out_channels : V1 feature channels = C_V1 (default 64)
    """

    def __init__(
        self,
        in_channels: int = 3,
        mid_channels: int = 32,
        out_channels: int = 64,
    ) -> None:
        super().__init__()
        if mid_channels % _GN_GROUPS != 0 or out_channels % _GN_GROUPS != 0:
            raise ValueError(
                f"mid_channels ({mid_channels}) and out_channels ({out_channels}) "
                f"must both be divisible by {_GN_GROUPS} for GroupNorm."
            )

        # Layer 1: aggressive spatial downsampling 50 → 25.
        self.conv1 = nn.Conv2d(in_channels, mid_channels, kernel_size=5, stride=2, padding=2)
        self.gn1 = nn.GroupNorm(_GN_GROUPS, mid_channels)

        # Layer 2: 25 → 12 (pad=0 lands cleanly).
        self.conv2 = nn.Conv2d(mid_channels, out_channels, kernel_size=3, stride=2, padding=0)
        self.gn2 = nn.GroupNorm(_GN_GROUPS, out_channels)

        # Layer 3: same-resolution refinement at 12×12.
        self.conv3 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.gn3 = nn.GroupNorm(_GN_GROUPS, out_channels)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_uniform_(m.weight, a=0, mode="fan_in", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

        self._expected_input_hw = (50, 50)
        self._expected_output_hw = (12, 12)
        self.out_channels = out_channels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x : (B, 3, 50, 50)  →  V_1 : (B, out_channels, 12, 12)"""
        if x.dim() != 4:
            raise ValueError(f"V1Stem expects 4D input; got {tuple(x.shape)}")
        if x.shape[-2:] != self._expected_input_hw:
            raise ValueError(
                f"V1Stem expects spatial dims {self._expected_input_hw}; "
                f"got {tuple(x.shape[-2:])}"
            )

        v1 = F.gelu(self.gn1(self.conv1(x)))
        v2 = F.gelu(self.gn2(self.conv2(v1)))
        v = F.gelu(self.gn3(self.conv3(v2)))

        assert v.shape[-2:] == self._expected_output_hw, (
            f"V1Stem internal arithmetic broken: expected {self._expected_output_hw}, "
            f"got {tuple(v.shape[-2:])}"
        )
        return v


# ─────────────────────────────────────────────────────────────────────────────
# V2 stem (new in v2)
# ─────────────────────────────────────────────────────────────────────────────


class V2Stem(nn.Module):
    """
    V2/V4-like extrastriate encoder.

    Maps V1 features (B, C_V1, 12, 12) to a coarser, higher-channel-count
    feature volume (B, C_V2, 6, 6). Two convolutional layers: a stride-2
    downsampling followed by a same-resolution refinement.

    Args
    ----
    in_channels  : V1 feature channels = C_V1 (default 64, must match V1Stem.out_channels)
    out_channels : V2 feature channels = C_V2 (default 128)
    """

    def __init__(
        self,
        in_channels: int = 64,
        out_channels: int = 128,
    ) -> None:
        super().__init__()
        if in_channels % _GN_GROUPS != 0 or out_channels % _GN_GROUPS != 0:
            raise ValueError(
                f"in_channels ({in_channels}) and out_channels ({out_channels}) "
                f"must both be divisible by {_GN_GROUPS} for GroupNorm."
            )

        # Layer 1: 12 → 6, channel expansion C_V1 → C_V2.
        # Spatial arithmetic: ⌊(12 + 2 − 3)/2⌋ + 1 = 6. ✓
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=2, padding=1)
        self.gn1 = nn.GroupNorm(_GN_GROUPS, out_channels)

        # Layer 2: same-resolution refinement at 6×6.
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.gn2 = nn.GroupNorm(_GN_GROUPS, out_channels)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_uniform_(m.weight, a=0, mode="fan_in", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

        self._expected_input_hw = (12, 12)
        self._expected_output_hw = (6, 6)
        self.in_channels = in_channels
        self.out_channels = out_channels

    def forward(self, v1: torch.Tensor) -> torch.Tensor:
        """v1 : (B, C_V1, 12, 12)  →  V_2 : (B, C_V2, 6, 6)"""
        if v1.dim() != 4:
            raise ValueError(f"V2Stem expects 4D input; got {tuple(v1.shape)}")
        if v1.shape[1] != self.in_channels:
            raise ValueError(
                f"V2Stem expects {self.in_channels} input channels; got {v1.shape[1]}"
            )
        if v1.shape[-2:] != self._expected_input_hw:
            raise ValueError(
                f"V2Stem expects spatial {self._expected_input_hw}; got {tuple(v1.shape[-2:])}"
            )

        h = F.gelu(self.gn1(self.conv1(v1)))
        v2 = F.gelu(self.gn2(self.conv2(h)))

        assert v2.shape[-2:] == self._expected_output_hw, (
            f"V2Stem internal arithmetic broken: expected {self._expected_output_hw}, "
            f"got {tuple(v2.shape[-2:])}"
        )
        return v2
