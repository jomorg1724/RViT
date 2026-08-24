"""
V1 stem for RViT+ — bottom-up perceptual feature extractor.

Maps RGB observations from ChangeDetectionEnv (50×50) to a feature volume of
shape (B, stem_out_ch, 12, 12). Channel count defaults to 64 (vs HRA's 32) to
give the LSTM SIP a richer per-patch feature vector to operate on.

Architecture writeup: see ../RVIT_PLUS_DESIGN.md §3.1.

Spatial arithmetic (PyTorch floor formula H_out = ⌊(H+2p−k)/s⌋ + 1):
    50 → ⌊(50+4−5)/2⌋+1 = 25
    25 → ⌊(25+0−3)/2⌋+1 = 12
    12 → ⌊(12+2−3)/1⌋+1 = 12

GroupNorm rather than BatchNorm — recurrent rollouts have small effective
per-timestep batches; BatchNorm stats become unreliable (Wu & He 2018).
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

_GN_GROUPS = 8  # must divide every channel count


class V1Stem(nn.Module):
    """Bottom-up convolutional encoder (V1-analog).

    Args
    ----
    in_channels  : input image channels (default 3 RGB)
    mid_channels : channels at the 25×25 intermediate stage (default 32)
    out_channels : channels at the 12×12 output stage (default 64)

    Forward
    -------
    V : (B, out_channels, 12, 12)
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
                f"must both be divisible by {_GN_GROUPS}."
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

        self.out_channels = out_channels
        self._expected_input_hw = (50, 50)
        self._expected_output_hw = (12, 12)

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
