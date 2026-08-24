"""
Decoders — two roles.

(1) PixelDecoder
    Per-layer pixel-space generative decoder g_ℓ : (B, C_ℓ, H_ℓ, W_ℓ) → (B, 3, 50, 50).
    Used to compute the predictive-coding loss L_PC = ‖x_t − g(C^{(t-1)})‖² at
    each layer. PRISM v1 has a single global decoder; HRA exposes one per layer
    so we can probe what each layer alone can predict (interpretability hook).

(2) FeatureDecoder
    Per-layer feature-space decoder g_ℓ^V : (B, C_ℓ, H_ℓ, W_ℓ) → (B, C_V, 12, 12).
    Predicts the V1 stem features V_t from the layer's recurrent state. Cheaper
    than full pixel reconstruction and useful as an auxiliary supervision signal
    that does not require the model to capture pixel-level texture.

Both decoders are kept deliberately small. They are not the bottleneck; the
GridCell RNN stack is. Zero-init'd output convolutions keep them at the
identity-near-zero attractor at training start so the model is not driven by
random reconstructions during the first few PPO steps.
"""
from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


def _gn_groups_for(channels: int) -> int:
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


class PixelDecoder(nn.Module):
    """
    Decode a layer's recurrent state to RGB pixel space (B, 3, 50, 50).

    Args
    ----
    in_channels : channels of the layer's hidden state C_ℓ
    in_h, in_w  : spatial dims of the hidden state
    out_h, out_w: target pixel-space dims (default 50, 50 — env image size)
    """

    def __init__(
        self,
        in_channels: int,
        in_h: int,
        in_w: int,
        out_h: int = 50,
        out_w: int = 50,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.in_h, self.in_w = in_h, in_w
        self.out_h, self.out_w = out_h, out_w

        mid_ch = max(16, in_channels // 2)
        gn1 = _gn_groups_for(mid_ch)

        # Upsample to ~50×50 in two stages. We use bilinear upsample + conv
        # rather than ConvTranspose2d to avoid checkerboard artifacts in the
        # reconstruction (a known issue for predictive-coding losses).
        self.conv1 = nn.Conv2d(in_channels, mid_ch, kernel_size=3, padding=1)
        self.gn1 = nn.GroupNorm(gn1, mid_ch)
        self.conv2 = nn.Conv2d(mid_ch, mid_ch, kernel_size=3, padding=1)
        self.gn2 = nn.GroupNorm(gn1, mid_ch)
        self.conv_out = nn.Conv2d(mid_ch, 3, kernel_size=1)

        # Zero-init the final 1×1 conv → initial prediction is the zero image,
        # so L_PC is bounded at init regardless of feature scale.
        nn.init.zeros_(self.conv_out.weight)
        nn.init.zeros_(self.conv_out.bias)

    def forward(self, C: torch.Tensor) -> torch.Tensor:
        if C.shape[-2:] != (self.in_h, self.in_w):
            raise ValueError(
                f"PixelDecoder expects spatial dims ({self.in_h},{self.in_w}); "
                f"got {tuple(C.shape[-2:])}"
            )
        x = F.gelu(self.gn1(self.conv1(C)))
        x = F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)
        x = F.gelu(self.gn2(self.conv2(x)))
        x = F.interpolate(x, size=(self.out_h, self.out_w), mode="bilinear", align_corners=False)
        x = self.conv_out(x)  # tanh-free; env range is [-1, 1] so we let the loss enforce.
        return x


class FeatureDecoder(nn.Module):
    """
    Decode a layer's recurrent state to the V1-stem feature volume
    (B, C_V, 12, 12). Used for feature-level predictive-coding loss at layers
    whose spatial resolution doesn't match the V1 grid (i.e., C_2, C_3).
    """

    def __init__(
        self,
        in_channels: int,
        in_h: int,
        in_w: int,
        out_channels: int = 32,
        out_h: int = 12,
        out_w: int = 12,
    ) -> None:
        super().__init__()
        self.in_h, self.in_w = in_h, in_w
        self.out_h, self.out_w = out_h, out_w

        mid_ch = max(16, in_channels)
        gn1 = _gn_groups_for(mid_ch)

        self.conv1 = nn.Conv2d(in_channels, mid_ch, kernel_size=3, padding=1)
        self.gn1 = nn.GroupNorm(gn1, mid_ch)
        self.conv_out = nn.Conv2d(mid_ch, out_channels, kernel_size=1)

        nn.init.zeros_(self.conv_out.weight)
        nn.init.zeros_(self.conv_out.bias)

    def forward(self, C: torch.Tensor) -> torch.Tensor:
        x = F.gelu(self.gn1(self.conv1(C)))
        if (x.shape[-2], x.shape[-1]) != (self.out_h, self.out_w):
            x = F.interpolate(x, size=(self.out_h, self.out_w), mode="bilinear", align_corners=False)
        x = self.conv_out(x)
        return x
