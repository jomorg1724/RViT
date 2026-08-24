"""
V1 stem — bottom-up perceptual feature extractor.

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

Mathematical formulation
------------------------
Given an RGB observation x ∈ ℝ^(B,3,50,50), produce a feature volume
V ∈ ℝ^(B,32,12,12) via three convolutional layers:

    V^(1) = GELU(GN_8(Conv_{3→16, k=5, s=2, p=2}(x)))     # → (B,16,25,25)
    V^(2) = GELU(GN_8(Conv_{16→32, k=3, s=2, p=0}(V^(1))))# → (B,32,12,12)
    V     = GELU(GN_8(Conv_{32→32, k=3, s=1, p=1}(V^(2))))# → (B,32,12,12)

Spatial-arithmetic check (PyTorch's floor formula
    H_out = ⌊(H_in + 2p − k)/s⌋ + 1):
    50 → ⌊(50+4−5)/2⌋+1 = 25
    25 → ⌊(25+0−3)/2⌋+1 = 12
    12 → ⌊(12+2−3)/1⌋+1 = 12

Why these dims
--------------
The four 25×25 Gabor patches in `ChangeDetectionEnv` map to 6×6 sub-regions
of the 12×12 grid. We do *not* explicitly patchify; the network discovers
patch structure from data if needed. The 5×5 first-layer kernel gives a
receptive field large enough to capture a Gabor's spatial period at the
input resolution.

Why GroupNorm (not BatchNorm)
-----------------------------
Recurrent rollouts process B episodes in lockstep with very small effective
batches per timestep; BatchNorm statistics become unreliable. GroupNorm
(Wu & He, 2018) normalises within each sample, batch-size invariant, which
is why every recurrent-vision codebase converged on it.

Complexity
----------
Time:   O(B · H · W · (3·16·25 + 16·32·9 + 32·32·9))  per step.
Space:  O(B · 32 · 12 · 12)  for V_t.

Params: 3·16·5² + 16·32·9 + 32·32·9 = 1,200 + 4,608 + 9,216 = 15,024  weights,
plus ~96 GroupNorm scales/biases.
"""
from __future__ import annotations

import torch
import torch.nn as nn

# Number of GroupNorm groups for the stem. Must divide each layer's channel
# count. 8 divides 16 and 32; do not change without re-checking.
_GN_GROUPS = 8


class V1Stem(nn.Module):
    """
    Bottom-up convolutional encoder (V1-like).

    Maps RGB observations to a feature volume of shape (B, out_channels, 12, 12).

    Args
    ----
    in_channels  : number of input image channels (default 3 for RGB)
    mid_channels : channels at the intermediate (25×25) stage (default 16)
    out_channels : channels at the output (12×12) stage  (default 32)

    Returns (forward)
    -----------------
    V : torch.Tensor  shape (B, out_channels, 12, 12)
    """

    def __init__(
        self,
        in_channels: int = 3,
        mid_channels: int = 16,
        out_channels: int = 32,
    ) -> None:
        super().__init__()
        if mid_channels % _GN_GROUPS != 0 or out_channels % _GN_GROUPS != 0:
            raise ValueError(
                f"mid_channels ({mid_channels}) and out_channels ({out_channels}) "
                f"must both be divisible by {_GN_GROUPS} for GroupNorm."
            )

        # Layer 1: aggressive spatial downsampling (50 → 25). 5×5 kernel ≈ Gabor period.
        self.conv1 = nn.Conv2d(in_channels, mid_channels, kernel_size=5, stride=2, padding=2)
        self.gn1 = nn.GroupNorm(_GN_GROUPS, mid_channels)

        # Layer 2: further downsample (25 → 12). pad=0 so we land exactly on 12.
        self.conv2 = nn.Conv2d(mid_channels, out_channels, kernel_size=3, stride=2, padding=0)
        self.gn2 = nn.GroupNorm(_GN_GROUPS, out_channels)

        # Layer 3: same-resolution refinement (12 → 12). No skip connection on purpose:
        # we want the stem to be a feedforward feature pyramid, not a residual block.
        # Adding a residual here is a one-line ablation.
        self.conv3 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.gn3 = nn.GroupNorm(_GN_GROUPS, out_channels)

        # Use Kaiming init with nonlinearity='relu' as a reasonable proxy for GELU.
        # GELU and ReLU have similar effective-gain factors near the origin
        # (≈ √2), so Kaiming-relu is an order-1 correct initialisation.
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_uniform_(m.weight, a=0, mode="fan_in", nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

        # Cache expected output spatial size for cheap shape-checking.
        self._expected_input_hw = (50, 50)
        self._expected_output_hw = (12, 12)
        self.out_channels = out_channels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x : (B, 3, 50, 50)  observation in [-1, 1] (env's box space)
        """
        if x.dim() != 4:
            raise ValueError(f"V1Stem expects 4D input (B,C,H,W); got shape {tuple(x.shape)}")
        if x.shape[-2:] != self._expected_input_hw:
            raise ValueError(
                f"V1Stem expects spatial dims {self._expected_input_hw}; "
                f"got {tuple(x.shape[-2:])}"
            )

        # Layer 1: x ∈ (B, 3, 50, 50) → V1 ∈ (B, 16, 25, 25)
        # GELU is preferred over ReLU here for two reasons:
        # (1) smoother gradient, important for the long BPTT-truncation windows;
        # (2) it does not zero negative activations, so prediction errors that
        #     are negative on a feature can still flow upstream during backward.
        v1 = torch.nn.functional.gelu(self.gn1(self.conv1(x)))

        # Layer 2: V1 → V2 ∈ (B, 32, 12, 12)
        v2 = torch.nn.functional.gelu(self.gn2(self.conv2(v1)))

        # Layer 3: V2 → V ∈ (B, 32, 12, 12)
        v = torch.nn.functional.gelu(self.gn3(self.conv3(v2)))

        # Cheap output-shape sanity check (dropped by torch.compile / can be removed).
        assert v.shape[-2:] == self._expected_output_hw, (
            f"V1Stem internal arithmetic broken: expected {self._expected_output_hw}, "
            f"got {tuple(v.shape[-2:])}"
        )
        return v
