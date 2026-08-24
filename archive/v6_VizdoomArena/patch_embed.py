"""
Conv-free patch embedding for V6 (lineage: RViT_plus_v4/v5 PatchEmbed).

The frame is cut into a regular grid of non-overlapping square patches; each
patch is flattened and expanded to ``d_model`` by a small per-patch MLP
(Linear → GELU → Linear → LayerNorm) — the standard ViT patchify implemented
with a pure reshape + Linear so there is genuinely no convolution anywhere.

For the V6 arena observation (3, 60, 80) the default ``patch_size=10`` yields
a 6×8 grid = 48 tokens (each token covers 10×10 obs pixels = 20×20 native
RES_160X120 pixels). Token layout is row-major: token ``i*grid_w + j`` is grid
cell (row i, col j), which the attention overlays map straight back to pixels.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class PatchEmbed(nn.Module):
    """Cut an image into patches and embed each with a shared MLP (no conv).

    Args
    ----
    in_channels : image channels (3).
    image_h, image_w : input size (60×80); must be divisible by patch_size.
    patch_size  : square patch edge in pixels (10 → 6×8 = 48 tokens).
    d_model     : embedding width.
    patch_hidden: hidden width of the per-patch expansion MLP.

    Forward: (B, C, H, W) float → (B, n_tokens, d_model), learned pos-emb added.
    """

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 60,
        image_w: int = 80,
        patch_size: int = 10,
        d_model: int = 128,
        patch_hidden: int = 128,
    ) -> None:
        super().__init__()
        if image_h % patch_size != 0 or image_w % patch_size != 0:
            raise ValueError(
                f"image ({image_h}×{image_w}) must be divisible by patch_size ({patch_size})"
            )
        self.in_channels = in_channels
        self.image_h, self.image_w = image_h, image_w
        self.patch_size = patch_size
        self.grid_h = image_h // patch_size
        self.grid_w = image_w // patch_size
        self.n_tokens = self.grid_h * self.grid_w
        self.patch_dim = in_channels * patch_size * patch_size
        self.d_model = d_model

        self.proj = nn.Sequential(
            nn.Linear(self.patch_dim, patch_hidden),
            nn.GELU(),
            nn.Linear(patch_hidden, d_model),
        )
        self.norm = nn.LayerNorm(d_model)
        self.pos_emb = nn.Parameter(torch.zeros(1, self.n_tokens, d_model))
        nn.init.normal_(self.pos_emb, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 4:
            raise ValueError(f"PatchEmbed expects 4D (B,C,H,W); got {tuple(x.shape)}")
        if x.shape[-2:] != (self.image_h, self.image_w):
            raise ValueError(
                f"PatchEmbed expects HW=({self.image_h},{self.image_w}); got {tuple(x.shape[-2:])}"
            )
        B, C, H, W = x.shape
        p, gh, gw = self.patch_size, self.grid_h, self.grid_w
        x = x.reshape(B, C, gh, p, gw, p)
        x = x.permute(0, 2, 4, 1, 3, 5).contiguous()
        patches = x.reshape(B, gh * gw, C * p * p)               # (B, N, patch_dim)
        return self.norm(self.proj(patches)) + self.pos_emb     # (B, N, d_model)
