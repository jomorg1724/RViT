"""
V1 stem — bottom-up perceptual feature extractor.

Maps RGB observations from ChangeDetectionEnv (50×50) to a feature volume of
shape (B, C_V, 12, 12). Same arithmetic as PRISM v1; reused as the input
projection for HRA layer C_1.

Architecture writeup: see ../MODEL_DESIGN.md §3.

Spatial-arithmetic check (PyTorch's floor formula H_out = ⌊(H+2p−k)/s⌋ + 1):
    50 → ⌊(50+4−5)/2⌋+1 = 25
    25 → ⌊(25+0−3)/2⌋+1 = 12
    12 → ⌊(12+2−3)/1⌋+1 = 12

GroupNorm rather than BatchNorm — recurrent rollouts have small effective per-
timestep batches; BatchNorm stats become unreliable (Wu & He 2018).
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

# Must divide every channel count below.
_GN_GROUPS = 8


class V1Stem(nn.Module):
    """
    Bottom-up convolutional encoder (V1-like).

    Args
    ----
    in_channels  : input image channels (default 3 for RGB)
    mid_channels : channels at the 25×25 stage (default 16)
    out_channels : channels at the 12×12 output stage (default 32). This sets
                   C_V — the channel count of the V1-level feature volume
                   that feeds the first GridCell RNN layer C_1.

    Forward
    -------
    V : (B, out_channels, 12, 12)
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

        self.conv1 = nn.Conv2d(in_channels, mid_channels, kernel_size=5, stride=2, padding=2)
        self.gn1 = nn.GroupNorm(_GN_GROUPS, mid_channels)

        self.conv2 = nn.Conv2d(mid_channels, out_channels, kernel_size=3, stride=2, padding=0)
        self.gn2 = nn.GroupNorm(_GN_GROUPS, out_channels)

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
        if x.dim() != 4:
            raise ValueError(f"V1Stem expects 4D (B,C,H,W); got {tuple(x.shape)}")
        if x.shape[-2:] != self._expected_input_hw:
            raise ValueError(
                f"V1Stem expects input HW={self._expected_input_hw}; got {tuple(x.shape[-2:])}"
            )

        v1 = F.gelu(self.gn1(self.conv1(x)))
        v2 = F.gelu(self.gn2(self.conv2(v1)))
        v = F.gelu(self.gn3(self.conv3(v2)))

        assert v.shape[-2:] == self._expected_output_hw
        return v
