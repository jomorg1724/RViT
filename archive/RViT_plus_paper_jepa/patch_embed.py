"""
Conv-free patch embedding for RViT+ v4.

v4 deliberately removes the convolutional V1 stem of v1–v3. The image is cut
into a regular grid of non-overlapping square patches; each patch is flattened
and expanded to ``d_model`` by a small per-patch MLP. This is the standard ViT
patchify step (Dosovitskiy et al. 2020), but implemented with a pure reshape +
``nn.Linear`` rather than a strided ``Conv2d``, so there is genuinely NO
convolution anywhere in the model.

The raw flattened patch is small: ``patch_dim = C·p·p = 3·5·5 = 75``, and only
~25 of those values are unique because ChangeDetectionEnv replicates each Gabor
across the 3 RGB channels (the colored cue frame is the exception). A single
linear map would under-use ``d_model``, so the projection is a 2-layer MLP
(Linear → GELU → Linear) with a final LayerNorm — a richer "preprocessing layer"
that blows the tiny patch up to the recurrent/transformer width and the
conv-free analog of v3's normed V1 stem. It is applied identically to every
patch (shared weights, broadcast over the token axis).

For the ChangeDetectionEnv (50×50 RGB), the default ``patch_size=5`` yields a
10×10 grid = 100 tokens. 50 is not divisible by 16, so a literal 16×16 grid
does not tile the image; 5 is the cleanest fine-grid divisor and aligns with
the env's 2×2 arrangement of 25×25 Gabor quadrants (each quadrant = a 5×5 block
of patches).

Output token layout is row-major over the grid: token index ``i*gw + j``
corresponds to grid cell ``(i, j)`` (row i, col j), which downstream attention
and analysis code can map back to image space.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class PatchEmbed(nn.Module):
    """Cut an image into patches and linearly embed each one (no convolution).

    Args
    ----
    in_channels : input image channels (default 3 RGB).
    image_h, image_w : input spatial size (default 50×50). Must be divisible
        by ``patch_size``.
    patch_size  : square patch edge in pixels (default 5 → 10×10 = 100 tokens).
    d_model     : embedding dimension each patch is expanded to.
    patch_hidden : hidden width of the per-patch expansion MLP (default 128).
        The MLP is ``Linear(patch_dim, patch_hidden) → GELU → Linear(patch_hidden,
        d_model)``; with the defaults this is 75 → 128 → 128.

    Forward
    -------
    x : (B, in_channels, image_h, image_w)
    → tokens : (B, n_tokens, d_model)  with a learned positional embedding added.
    """

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        patch_size: int = 5,
        d_model: int = 128,
        patch_hidden: int = 128,
    ) -> None:
        super().__init__()
        if image_h % patch_size != 0 or image_w % patch_size != 0:
            raise ValueError(
                f"image ({image_h}×{image_w}) must be divisible by patch_size "
                f"({patch_size}); 50 supports patch_size ∈ {{1,2,5,10,25,50}}."
            )
        self.in_channels = in_channels
        self.image_h, self.image_w = image_h, image_w
        self.patch_size = patch_size
        self.grid_h = image_h // patch_size
        self.grid_w = image_w // patch_size
        self.n_tokens = self.grid_h * self.grid_w
        self.patch_dim = in_channels * patch_size * patch_size
        self.d_model = d_model
        self.patch_hidden = patch_hidden

        # Per-patch preprocessing MLP: expand the small raw patch (patch_dim ≈ 75,
        # ~25 unique) up to d_model with a nonlinearity, then LayerNorm so the
        # token scale entering the recurrent residual stream is well-behaved.
        # Shared across patches (broadcast over the token axis).
        self.proj = nn.Sequential(
            nn.Linear(self.patch_dim, patch_hidden),
            nn.GELU(),
            nn.Linear(patch_hidden, d_model),
        )
        self.norm = nn.LayerNorm(d_model)
        # Learned absolute positional embedding over the token grid.
        self.pos_emb = nn.Parameter(torch.zeros(1, self.n_tokens, d_model))
        nn.init.normal_(self.pos_emb, std=0.02)
        self._expected_input_hw = (image_h, image_w)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 4:
            raise ValueError(f"PatchEmbed expects 4D (B,C,H,W); got {tuple(x.shape)}")
        if x.shape[-2:] != self._expected_input_hw:
            raise ValueError(
                f"PatchEmbed expects input HW={self._expected_input_hw}; "
                f"got {tuple(x.shape[-2:])}"
            )
        B, C, H, W = x.shape
        p, gh, gw = self.patch_size, self.grid_h, self.grid_w
        # (B,C,H,W) → (B,C,gh,p,gw,p) → (B,gh,gw,C,p,p) → (B, gh*gw, C*p*p)
        x = x.reshape(B, C, gh, p, gw, p)
        x = x.permute(0, 2, 4, 1, 3, 5).contiguous()
        patches = x.reshape(B, gh * gw, C * p * p)          # (B, n_tokens, patch_dim)
        tokens = self.norm(self.proj(patches)) + self.pos_emb   # (B, n_tokens, d_model)
        return tokens
