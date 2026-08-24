"""
Conv patch front-end — a CAPABLE-but-small SE-ResNet replacing the paper VAE encoder.

Each 50×50 RGB frame is split into FOUR 25×25 patches in the env's cell order
[TL, TR, BL, BR] (so patch index == cue_index/change_index; S1=TL=0 … S4=BR=3).
A SHARED small CNN encodes each patch to a 128-d embedding ô_i; the token is then
x_i = [ô_i ‖ ρ_i(4) ‖ τ(8)] = 140-d, X = (x_1..x_4) ∈ ℝ^{4×140} — IDENTICAL token
layout to VAEPatchFrontEnd, so it is a drop-in front-end.

CNN (standard small-visual-encoder best practice; NOT a naive conv stack):
  stem 3×3 conv → 3 SE-residual stages (progressive downsample + channel growth)
  → global average pool → RMSNorm (scale-match, colour-DC-preserving) → 128-d. Each stage:
  Conv3×3-GN-SiLU → Conv3×3-GN → Squeeze-Excite (channel attention) → +residual → SiLU.

CHOICES (flagged):
  • 3-channel COLOUR input — the value cue (red/green/blue) must be visible.
  • GroupNorm, NOT BatchNorm: the front-end runs at batch=1 during the recurrent online
    rollout (rl_step), where BN running-stats are fragile; GroupNorm is batch-independent
    and train/eval-identical.
  • Squeeze-Excitation + residual on every stage (per the user's spec).
  • Trained END-TO-END with RL+JEPA (no pretrain, no reconstruction). It replaces the
    from-scratch VAE-shaped encoder that was the perception bottleneck.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

N_PATCH = 4
O_FLAT2 = 128                 # per-patch embedding width (matches the paper's o_flat,2)
POS_DIM = 4                   # one-hot over the 4 patch positions
TEMP_DIM = 8                  # one-hot over timestep (T=7 task; 8 slots, t clamped)
TOKEN_DIM = O_FLAT2 + POS_DIM + TEMP_DIM   # = 140 (matches VAEPatchFrontEnd / the paper 4×140)


def _gn(c: int, max_groups: int = 8) -> nn.GroupNorm:
    for cand in (max_groups, 4, 2, 1):
        if c % cand == 0:
            return nn.GroupNorm(cand, c)
    return nn.GroupNorm(1, c)


class RMSNorm(nn.Module):
    """Scale-normalise the embedding WITHOUT mean-subtraction. Used on the pooled patch vector to
    match its scale to the pos/temporal one-hots feeding the ViT, while preserving any constant
    (DC) component — important because the value cue is COLOUR; a mean-subtracting LayerNorm here
    could attenuate a uniform colour offset."""
    def __init__(self, d: int, eps: float = 1e-6) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight


class SqueezeExcite(nn.Module):
    """Channel attention: global-avg-pool (squeeze) → FC↓ → SiLU → FC↑ → sigmoid (excite) → rescale."""
    def __init__(self, c: int, reduction: int = 8) -> None:
        super().__init__()
        h = max(4, c // reduction)
        self.fc1 = nn.Conv2d(c, h, 1)
        self.fc2 = nn.Conv2d(h, c, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        s = x.mean(dim=(2, 3), keepdim=True)          # squeeze
        s = F.silu(self.fc1(s))
        s = torch.sigmoid(self.fc2(s))
        return x * s                                  # excite


class SEResBlock(nn.Module):
    """Conv3×3-GN-SiLU → Conv3×3-GN → SE → + (projected) residual → SiLU."""
    def __init__(self, in_c: int, out_c: int, stride: int = 1, reduction: int = 8) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_c, out_c, 3, stride=stride, padding=1, bias=False)
        self.gn1 = _gn(out_c)
        self.conv2 = nn.Conv2d(out_c, out_c, 3, stride=1, padding=1, bias=False)
        self.gn2 = _gn(out_c)
        self.se = SqueezeExcite(out_c, reduction)
        if stride != 1 or in_c != out_c:
            self.short = nn.Sequential(nn.Conv2d(in_c, out_c, 1, stride=stride, bias=False), _gn(out_c))
        else:
            self.short = nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = F.silu(self.gn1(self.conv1(x)))
        h = self.gn2(self.conv2(h))
        h = self.se(h)
        return F.silu(h + self.short(x))


class ConvPatchFrontEnd(nn.Module):
    def __init__(self, in_channels: int = 3, grid_rows: int = 2, grid_cols: int = 2,
                 image_size: int = 50) -> None:
        super().__init__()
        self.in_channels = int(in_channels)
        self.grid_rows, self.grid_cols = int(grid_rows), int(grid_cols)
        self.image_size = int(image_size)
        self.n_patch = self.grid_rows * self.grid_cols                 # 4 (2x2) or 9 (3x3)
        self.pos_dim = self.n_patch                                    # one-hot over patch positions
        self.token_dim = O_FLAT2 + self.pos_dim + TEMP_DIM             # 128 + n_patch + 8
        # row-major patch boundaries (must match the env's cell order so token i ⇔ stimulus i)
        rb = [round(image_size*i/self.grid_rows) for i in range(self.grid_rows+1)]
        cb = [round(image_size*j/self.grid_cols) for j in range(self.grid_cols+1)]
        self._bounds = [(rb[r], rb[r+1], cb[c], cb[c+1]) for r in range(self.grid_rows) for c in range(self.grid_cols)]
        c0, c1, c2, c3 = 32, 64, 128, 128
        self.stem = nn.Sequential(
            nn.Conv2d(self.in_channels, c0, 3, stride=1, padding=1, bias=False), _gn(c0), nn.SiLU())
        self.stage1 = SEResBlock(c0, c1, stride=2)    # 25→13
        self.stage2 = SEResBlock(c1, c2, stride=2)    # 13→7
        self.stage3 = SEResBlock(c2, c3, stride=1)    # 7→7 (extra depth, no further downsample)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.out_norm = RMSNorm(O_FLAT2)              # scale-match into the ViT; PRESERVES colour DC (no mean-subtract)
        assert c3 == O_FLAT2
        self.n_tokens = self.n_patch
        self.frozen = False

    def _encode_patch(self, o: torch.Tensor) -> torch.Tensor:
        """o: (B,C,25,25) → ô (B,128)."""
        z = self.stem(o)
        z = self.stage1(z); z = self.stage2(z); z = self.stage3(z)
        z = self.pool(z).flatten(1)                   # (B,128)
        return self.out_norm(z)

    def forward(self, x: torch.Tensor, t: int) -> torch.Tensor:
        """x: (B,3,S,S) RGB frame, t: integer timestep. Returns X: (B, n_patch, 128+n_patch+8)."""
        B = x.shape[0]
        g = x if self.in_channels == 3 else x.mean(dim=1, keepdim=True)
        patches = [g[:, :, r0:r1, c0:c1] for (r0, r1, c0, c1) in self._bounds]   # row-major grid order
        emb = torch.stack([self._encode_patch(p) for p in patches], dim=1)       # (B, n_patch, 128)
        pos = torch.eye(self.pos_dim, device=x.device, dtype=x.dtype).unsqueeze(0).expand(B, -1, -1)
        ti = max(0, min(int(t), TEMP_DIM - 1))
        tau = torch.zeros(B, self.n_patch, TEMP_DIM, device=x.device, dtype=x.dtype)
        tau[:, :, ti] = 1.0
        return torch.cat([emb, pos, tau], dim=-1)                                # (B, n_patch, token_dim)
