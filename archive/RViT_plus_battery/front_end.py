"""
Patch front-end for the RViT+ FiLM reproduction.

DEFAULT = PIXEL: raw pixels → linear projection → transformer (standard ViT patch
embedding, NO convolution). The conv front-end (below) pooled each patch 24→12→2×2 with
RL-only training and no reconstruction pressure, which discarded the subtle orientation-
change signal and the model could not learn change-timing. Going straight from pixels to a
linear patch embedding keeps the full signal; the linear map can realise an oriented-
filter bank and the transformer + LSTM do the rest. `kind="conv"` / `"mlp"` / `"vae_frozen"`
remain available as alternatives but are not the default.

LEGACY NOTE (conv front-end, kept as a non-default option):
    The published model used a *frozen, separately-pretrained VAE* whose second
    flattened encoder layer fed the ViT. Every working model in the v5–v15 line
    instead trains a per-patch front-end END-TO-END (the PatchEmbed MLP) and still
    shows the full cueing effect, so the early "end-to-end perception weakens the
    cue" worry does not hold for the mature harness. We therefore default to a small
    per-patch CONVOLUTIONAL encoder trained jointly with the network:
      • no brittle separate VAE-pretraining step, and no per-geometry VAE to retrain;
      • one front-end works across the whole battery (K = 2 / 4 / 9, Luo–Maunsell,
        Krauzlis) because every stimulus patch is the same Gabor primitive;
      • a conv (vs flat MLP) gives each patch a local spatial inductive bias.
    `kind="mlp"` recovers the reshape+MLP PatchEmbed; `kind="vae_frozen"` is a stub
    hook for exact paper reproduction (load + freeze a pretrained per-patch VAE).

ONE TOKEN PER STIMULUS:
    The image is split into a grid_rows × grid_cols grid of cells (one stimulus per
    cell), each cell encoded to a single token. This keeps the attention map a clean
    K-token (e.g. 2×2, 3×3) array that is directly interpretable AND directly
    manipulable for causal-perturbation experiments — exactly what James asked for
    (vs the 100-token 10×10 grid, which he flagged as un-manipulable). Token order is
    row-major; token i ⇔ stimulus i (all battery envs index stimuli row-major).
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def _cell_bounds(extent: int, n: int) -> list:
    """Integer cell boundaries splitting [0, extent) into n contiguous bands."""
    edges = np.linspace(0, extent, n + 1).round().astype(int).tolist()
    return [(edges[i], edges[i + 1]) for i in range(n)]


class ConvPatchFrontEnd(nn.Module):
    """Per-patch conv encoder (default). Crops the image into a grid of one-stimulus
    cells, encodes each with a shared small CNN, projects to d_model, adds a learned
    positional embedding. Trained end-to-end with the rest of the network.

    forward: x (B, in_channels, H, W) -> tokens (B, n_tokens, d_model)
    """

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        grid_rows: int = 2,
        grid_cols: int = 2,
        d_model: int = 128,
        conv_hidden: int = 32,
        pool: int = 2,
        cell_size: int = 24,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.image_h, self.image_w = image_h, image_w
        self.grid_rows, self.grid_cols = grid_rows, grid_cols
        self.n_tokens = grid_rows * grid_cols
        self.d_model = d_model
        self.pool = pool
        # Each cropped cell is resized to a fixed cell_size×cell_size before the CNN so
        # (a) the conv output is a fixed, MPS-divisible spatial size for the adaptive
        # pool, and (b) the shared front-end sees a consistent patch scale across all
        # grid geometries (2×2 25px, 3×3 17px, 1×2 50×25px → one canonical patch).
        self.cell_size = int(cell_size)
        # precompute cell crop boxes (row-major)
        rb = _cell_bounds(image_h, grid_rows)
        cb = _cell_bounds(image_w, grid_cols)
        self.cells = [(r0, r1, c0, c1) for (r0, r1) in rb for (c0, c1) in cb]

        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels, conv_hidden // 2, 3, stride=1, padding=1), nn.GELU(),
            nn.Conv2d(conv_hidden // 2, conv_hidden, 3, stride=2, padding=1), nn.GELU(),
            nn.AdaptiveAvgPool2d((pool, pool)),
        )
        self.proj = nn.Linear(conv_hidden * pool * pool, d_model)
        self.pos = nn.Parameter(torch.zeros(1, self.n_tokens, d_model))
        nn.init.normal_(self.pos, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 4 or x.shape[1] != self.in_channels:
            raise ValueError(f"expected (B,{self.in_channels},H,W); got {tuple(x.shape)}")
        B, C = x.shape[0], self.in_channels
        cs = self.cell_size
        crops = [F.interpolate(x[:, :, r0:r1, c0:c1], size=(cs, cs),
                               mode="bilinear", align_corners=False)
                 for (r0, r1, c0, c1) in self.cells]          # each (B, C, cs, cs)
        stacked = torch.stack(crops, dim=1).reshape(B * self.n_tokens, C, cs, cs)
        f = self.cnn(stacked).reshape(B * self.n_tokens, -1)  # (B*N, conv_hidden*pool*pool)
        tokens = self.proj(f).reshape(B, self.n_tokens, self.d_model)
        return tokens + self.pos


class PixelPatchFrontEnd(nn.Module):
    """Straight pixels → linear → transformer (standard ViT patch embedding, NO conv).

    Crops the image into one-stimulus cells, resizes each to a canonical square (so the
    flattened dim is fixed across grid geometries), flattens the RAW pixels, and linearly
    projects to d_model. + learned positional embedding. No convolution, no pooling — the
    full orientation signal reaches the transformer; the linear map can realise an
    oriented-filter bank and the transformer/LSTM do the rest.

    forward: x (B, in_channels, H, W) -> tokens (B, n_tokens, d_model)
    """

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        grid_rows: int = 2,
        grid_cols: int = 2,
        d_model: int = 128,
        cell_size: int = 25,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.image_h, self.image_w = image_h, image_w
        self.grid_rows, self.grid_cols = grid_rows, grid_cols
        self.n_tokens = grid_rows * grid_cols
        self.d_model = d_model
        self.cell_size = int(cell_size)
        rb = _cell_bounds(image_h, grid_rows)
        cb = _cell_bounds(image_w, grid_cols)
        self.cells = [(r0, r1, c0, c1) for (r0, r1) in rb for (c0, c1) in cb]
        patch_dim = in_channels * self.cell_size * self.cell_size
        self.proj = nn.Linear(patch_dim, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.pos = nn.Parameter(torch.zeros(1, self.n_tokens, d_model))
        nn.init.normal_(self.pos, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 4 or x.shape[1] != self.in_channels:
            raise ValueError(f"expected (B,{self.in_channels},H,W); got {tuple(x.shape)}")
        B, C = x.shape[0], self.in_channels
        cs = self.cell_size
        crops = [F.interpolate(x[:, :, r0:r1, c0:c1], size=(cs, cs),
                               mode="bilinear", align_corners=False)
                 for (r0, r1, c0, c1) in self.cells]          # each (B, C, cs, cs)
        stacked = torch.stack(crops, dim=1).reshape(B, self.n_tokens, C * cs * cs)  # raw pixels
        tokens = self.norm(self.proj(stacked))
        return tokens + self.pos


class MLPPatchFrontEnd(nn.Module):
    """Reshape + per-patch MLP (= the original PatchEmbed), kept for parity. Requires
    image dims divisible by the (square) patch size and produces grid_rows*grid_cols
    tokens of patch_size×patch_size pixels."""

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        grid_rows: int = 2,
        grid_cols: int = 2,
        d_model: int = 128,
        patch_hidden: int = 128,
    ) -> None:
        super().__init__()
        if image_h % grid_rows or image_w % grid_cols:
            raise ValueError("MLP front-end needs image dims divisible by the grid")
        self.in_channels = in_channels
        self.image_h, self.image_w = image_h, image_w
        self.grid_rows, self.grid_cols = grid_rows, grid_cols
        self.ph, self.pw = image_h // grid_rows, image_w // grid_cols
        self.n_tokens = grid_rows * grid_cols
        self.d_model = d_model
        patch_dim = in_channels * self.ph * self.pw
        self.mlp = nn.Sequential(
            nn.Linear(patch_dim, patch_hidden), nn.GELU(),
            nn.Linear(patch_hidden, d_model), nn.LayerNorm(d_model),
        )
        self.pos = nn.Parameter(torch.zeros(1, self.n_tokens, d_model))
        nn.init.normal_(self.pos, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, C, H, W = x.shape
        gh, gw, ph, pw = self.grid_rows, self.grid_cols, self.ph, self.pw
        x = x.reshape(B, C, gh, ph, gw, pw).permute(0, 2, 4, 1, 3, 5)
        x = x.reshape(B, gh * gw, C * ph * pw)           # (B, N, patch_dim) row-major
        return self.mlp(x) + self.pos


class VAEFrontEnd(nn.Module):
    """Paper's VAE-encoder front-end: per cell, grayscale 25×25 → Conv16 → Conv32 → FC128
    (o_flat,2) → token, + learnable positional embedding. d_model must be 128. Loads a
    pretrained PatchVAE encoder (conv1/conv2/fc1) and (optionally) freezes it — the
    perception the task can't learn from reward. Same conv/fc layer names as `vae.PatchVAE`.

    forward: x (B,3,H,W) or (B,H,W,3) -> tokens (B, n_tokens, 128).
    """

    def __init__(self, in_channels: int = 3, image_h: int = 50, image_w: int = 50,
                 grid_rows: int = 2, grid_cols: int = 2, d_model: int = 128, **_kw) -> None:
        super().__init__()
        if d_model != 128:
            raise ValueError(f"VAE front-end requires d_model=128 (o_flat,2 width), got {d_model}")
        self.in_channels = in_channels
        self.n_tokens = grid_rows * grid_cols
        self.d_model = 128
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1)
        self.fc1 = nn.Linear(7 * 7 * 32, 128)
        self._rb = _cell_bounds(image_h, grid_rows)
        self._cb = _cell_bounds(image_w, grid_cols)
        self.pos = nn.Parameter(torch.zeros(1, self.n_tokens, 128))
        nn.init.normal_(self.pos, std=0.02)
        self.frozen = False

    def load_pretrained(self, encoder_state: dict, freeze: bool = True):
        res = self.load_state_dict(encoder_state, strict=False)
        if freeze:
            for m in (self.conv1, self.conv2, self.fc1):
                for p in m.parameters():
                    p.requires_grad_(False)
            self.frozen = True
        return res

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        g = x.contiguous().mean(dim=1, keepdim=True)               # grayscale (B,1,H,W)
        toks = []
        for (r0, r1) in self._rb:                                   # rows outer, cols inner → [TL,TR,BL,BR]
            for (c0, c1) in self._cb:
                cell = g[:, :, r0:r1, c0:c1]
                if cell.shape[-1] != 25 or cell.shape[-2] != 25:
                    cell = F.interpolate(cell, size=(25, 25), mode="bilinear", align_corners=False)
                z = torch.relu(self.conv1(cell))
                z = torch.relu(self.conv2(z))
                toks.append(torch.relu(self.fc1(z.flatten(1))))    # o_flat,2 (B,128)
        return torch.stack(toks, dim=1) + self.pos                 # (B, n_tokens, 128)


def build_front_end(kind: str = "pixel", **kw) -> nn.Module:
    """Factory. kind ∈ {pixel (default — raw pixels → linear, no conv), patches, conv, mlp,
    vae_frozen}. `patches` = the ORIGINAL ViT patchification: a (H//patch_size)² grid of
    patch_size×patch_size tokens + per-patch MLP (patch_size=5 → 100 tokens, the v11_part2
    resolution) — grid-agnostic, NOT one-token-per-stimulus."""
    if kind == "patches":
        try:
            from .patch_embed import PatchEmbed
        except ImportError:  # pragma: no cover
            from patch_embed import PatchEmbed  # type: ignore[no-redef]
        return PatchEmbed(**{k: v for k, v in kw.items()
                             if k in PatchEmbed.__init__.__code__.co_varnames})
    if kind == "pixel":
        return PixelPatchFrontEnd(**{k: v for k, v in kw.items()
                                     if k in PixelPatchFrontEnd.__init__.__code__.co_varnames})
    if kind == "conv":
        return ConvPatchFrontEnd(**{k: v for k, v in kw.items()
                                    if k in ConvPatchFrontEnd.__init__.__code__.co_varnames})
    if kind == "mlp":
        return MLPPatchFrontEnd(**{k: v for k, v in kw.items()
                                   if k in MLPPatchFrontEnd.__init__.__code__.co_varnames})
    if kind in ("vae", "vae_frozen"):
        return VAEFrontEnd(**{k: v for k, v in kw.items()
                              if k in VAEFrontEnd.__init__.__code__.co_varnames})
    raise ValueError(f"unknown front-end kind: {kind!r}")
