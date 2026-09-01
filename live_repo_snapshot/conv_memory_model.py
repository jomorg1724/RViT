"""
Convolutional recurrent-transformer memory — DUAL-STATE variant (the working one).

Restored from the v3 run (the variant that learned the change). Two recurrent states:
  * H1 = the persistent, transformed memory state  (SE-projected concat residual)
  * H2 = the raw, ephemeral attended read          (the FFN'd gated blend, NO normalization)
H2 survives exactly one step: it is fully regenerated each iteration and only feeds the
next vision block's values (V_H <- H2) plus the representation R.

Per specification, a Gaussian noise term N(0, memory_noise_std) is added to the H1
OUTPUT every iteration (the persistent memory is corrupted as it is written; H2 stays
clean). There is NO channel softmax on the memory in this variant.

Per-step pipeline:
  stem:       o_t -> X_t                      (50x50x3 -> 16x16xC)
  vision:     Q<-X, K<-[X,H1], V<-[X,H2]  ->  Z, att_vis   (2-way per-pixel gate, concat resid + SE)
  memory:     Q<-H1, K/V<-[Z,H1]          ->  H1' = SE-proj([H1 || att]) + noise ;  H2' = att
  R = [H1' || H2' || Z || att_vis]  (4C channels)
  JEPA head:  one per-pixel head (LayerNorm -> 1x1 4C->2C -> 1x1 2C->P), 16x16 CE targets
  classifier: mean-pool R@last -> 2 logits, full BPTT
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class SEBlock(nn.Module):
    """Lightweight Squeeze-and-Excitation channel recalibration."""

    def __init__(self, channels: int, reduction: int = 4):
        super().__init__()
        self.fc = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(channels, max(channels // reduction, 1), 1),
            nn.GELU(),
            nn.Conv2d(max(channels // reduction, 1), channels, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.fc(x)


class SEResStage(nn.Module):
    """Small SE-ResNet stage (similar structure to the previous frontend)."""

    def __init__(self, cin: int, cout: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(cin, cout, 3, stride, 1, bias=False)
        self.conv2 = nn.Conv2d(cout, cout, 3, 1, 1, bias=False)
        self.se = SEBlock(cout)
        self.short = (nn.Conv2d(cin, cout, 1, stride, bias=False)
                      if (cin != cout or stride != 1) else nn.Identity())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = F.gelu(self.conv1(x))
        h = self.conv2(h)
        h = self.se(h)
        return F.gelu(h + self.short(x))


class ConvStem(nn.Module):
    """Full-image conv processing: 50x50x(3*frame_window) -> [C, 16, 16] (downsample + interpolate)."""

    def __init__(self, channels: int = 128, map_size: int = 16, in_channels: int = 3):
        super().__init__()
        self.map_size = map_size
        c1 = max(channels // 4, 8)
        c2 = max(channels // 2, 8)
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, c1, 7, stride=2, padding=3, bias=False), nn.GELU(),  # 25x25
            SEResStage(c1, c2, stride=1),                                     # 25x25
            SEResStage(c2, channels, stride=2),                               # 13x13
        )

    def forward(self, frame: torch.Tensor) -> torch.Tensor:  # frame: (B,3,50,50)
        h = self.net(frame)
        return F.interpolate(h, size=(self.map_size, self.map_size),
                             mode="bilinear", align_corners=False)            # (B,C,16,16)


class ConvAttentionBlock(nn.Module):
    """Recurrent conv-transformer vision block: Q<-X, K<-[X,H1], V<-[X,H2].

    Per-pixel channel-inner-product attention with a 2-way softmax gate,
    FFN, CONCATENATED residual, and an SE block.
    `in_c` allows a wider visual input (e.g. X concatenated with a visual
    accumulator); H-sides and the output stay at width c.
    """

    def __init__(self, c: int = 128, in_c: int | None = None):
        super().__init__()
        cin = int(in_c) if in_c else c
        self.W_q = nn.Conv2d(cin, c, 1, bias=False)
        self.W_kx = nn.Conv2d(cin, c, 1, bias=False)
        self.W_kh = nn.Conv2d(c, c, 1, bias=False)
        self.W_vx = nn.Conv2d(cin, c, 1, bias=False)
        self.W_vh = nn.Conv2d(c, c, 1, bias=False)
        self.ffn = nn.Sequential(nn.Conv2d(c, 2 * c, 1), nn.GELU(), nn.Conv2d(2 * c, c, 1))
        self.se = SEBlock(cin + c)
        self.proj = nn.Conv2d(cin + c, c, 1)
        self.scale = c ** -0.5

    def forward(self, X: torch.Tensor, H1: torch.Tensor, H2: torch.Tensor,
                return_attn: bool = False):
        Q = self.W_q(X)
        Kx, Kh = self.W_kx(X), self.W_kh(H1)
        Vx, Vh = self.W_vx(X), self.W_vh(H2)
        Sx = (Q * Kx).sum(dim=1, keepdim=True) * self.scale   # (B,1,16,16)
        Sh = (Q * Kh).sum(dim=1, keepdim=True) * self.scale
        A = torch.softmax(torch.cat([Sx, Sh], dim=1), dim=1)   # (B,2,16,16) per-pixel gate
        att = A[:, 0:1] * Vx + A[:, 1:2] * Vh                  # (B,C,16,16)
        att = self.ffn(att)
        res = torch.cat([X, att], dim=1)                       # CONCAT residual (B,2C,16,16)
        Z = self.proj(self.se(res))                            # (B,C,16,16)
        if return_attn:
            return Z, att, A
        return Z, att


class ConvMemoryBlock(nn.Module):
    """One memory structure: Q<-H1, K/V<-[Z,H1]; same attention formula.

    H1' = SE-proj([H1 || att])  (+ N(0, noise) on the OUTPUT, if set)  — the persistent state
    H2' = att                                                          — the raw ephemeral read
    No channel softmax here (the softmax-normalized variant lost the change signal).
    """

    def __init__(self, c: int = 128, memory_noise_std: float = 0.0):
        super().__init__()
        self.memory_noise_std = float(memory_noise_std)
        self.W_q = nn.Conv2d(c, c, 1, bias=False)
        self.W_kz = nn.Conv2d(c, c, 1, bias=False)
        self.W_kh = nn.Conv2d(c, c, 1, bias=False)
        self.W_vz = nn.Conv2d(c, c, 1, bias=False)
        self.W_vh = nn.Conv2d(c, c, 1, bias=False)
        self.ffn = nn.Sequential(nn.Conv2d(c, 2 * c, 1), nn.GELU(), nn.Conv2d(2 * c, c, 1))
        self.se = SEBlock(2 * c)
        self.proj = nn.Conv2d(2 * c, c, 1)
        self.scale = c ** -0.5

    def forward(self, Z: torch.Tensor, H1: torch.Tensor):
        Q = self.W_q(H1)
        Kz, Kh = self.W_kz(Z), self.W_kh(H1)
        Vz, Vh = self.W_vz(Z), self.W_vh(H1)
        Sz = (Q * Kz).sum(dim=1, keepdim=True) * self.scale
        Sh = (Q * Kh).sum(dim=1, keepdim=True) * self.scale
        A = torch.softmax(torch.cat([Sz, Sh], dim=1), dim=1)
        att = A[:, 0:1] * Vz + A[:, 1:2] * Vh
        att = self.ffn(att)
        res = torch.cat([H1, att], dim=1)
        H1_new = self.proj(self.se(res))                        # (B,C,16,16)
        if self.memory_noise_std > 0.0:
            H1_new = H1_new + self.memory_noise_std * torch.randn_like(H1_new)
        H2_new = att                                            # raw read, no normalization
        return H1_new, H2_new


class ConvMemoryModel(nn.Module):
    """Full recurrent model: stem -> vision conv-attn -> memory conv-attn -> JEPA head
    (+ classifier). The recurrent state is the pair (H1, H2)."""

    def __init__(self, n_channels: int = 128, proto_dim: int = 256, map_size: int = 16,
                 memory_noise_std: float = 0.0,
                 frame_window: int = 1, frame_stride: int = 1, mem_every: int = 1,
                 visual_accum: bool = False, accum_decay: float = 0.5):
        super().__init__()
        self.n_channels = n_channels
        self.map_size = map_size
        self.proto_dim = proto_dim
        self.memory_noise_std = float(memory_noise_std)
        # Temporal hierarchy: each agent step consumes `frame_window` frames as input
        # channels; steps advance `frame_stride` frames; the memory block (H1/H2 update)
        # runs only every `mem_every`-th step. Defaults reproduce the original model.
        self.frame_window = int(frame_window)
        self.frame_stride = int(frame_stride)
        self.mem_every = int(mem_every)
        # Visual accumulator: H_VA^t = d*H_VA^{t-1} + (1-d)*X_t, a per-channel learnable
        # EMA of the stem output (sigmoid-parametrized decay, init `accum_decay`).
        # Concatenated with X_t as the vision block's input (X-side convs widen to 2C).
        self.visual_accum = bool(visual_accum)
        if self.visual_accum:
            init = float(accum_decay)
            init = min(max(init, 1e-3), 1.0 - 1e-3)
            self.accum_logit = nn.Parameter(
                torch.full((n_channels,), float(np.log(init / (1.0 - init)))))
        self.stem = ConvStem(channels=n_channels, map_size=map_size,
                             in_channels=3 * self.frame_window)
        self.vision = ConvAttentionBlock(n_channels,
                                         in_c=2 * n_channels if self.visual_accum else None)
        self.memory = ConvMemoryBlock(n_channels, memory_noise_std=memory_noise_std)
        # JEPA head: ONE per-pixel head. R = 4 x n_channels (H1' || H2' || Z || att_vis).
        self.jepa_norm = nn.LayerNorm(4 * n_channels)
        self.jepa_feat = nn.Sequential(nn.Conv2d(4 * n_channels, 2 * n_channels, 1), nn.GELU())
        self.jepa_out = nn.Conv2d(2 * n_channels, proto_dim, 1)
        self.classifier = nn.Linear(4 * n_channels, 2)
        self.register_buffer("jepa_center", torch.zeros(map_size, map_size, proto_dim))

    def init_state(self, B: int, device, dtype):
        z = torch.zeros(B, self.n_channels, self.map_size, self.map_size,
                        device=device, dtype=dtype)
        if self.visual_accum:
            return (z.clone(), z.clone(), z)   # (H1, H2, H_VA)
        return (z, z)

    def step(self, X_t: torch.Tensor, state, update_memory: bool = True):
        if self.visual_accum:
            H1, H2, HVA = state
            d = torch.sigmoid(self.accum_logit).view(1, -1, 1, 1)
            HVA = d * HVA + (1.0 - d) * X_t                        # decayed visual sum (EMA)
            Xin = torch.cat([X_t, HVA], dim=1)                     # (B,2C,16,16)
        else:
            H1, H2 = state
            HVA = None
            Xin = X_t
        Z, att_vis = self.vision(Xin, H1, H2)
        if update_memory:
            H1, H2 = self.memory(Z, H1)
        R = torch.cat([H1, H2, Z, att_vis], dim=1)      # (B, 4C, 16, 16)
        if self.visual_accum:
            return R, (H1, H2, HVA)
        return R, (H1, H2)

    def forward_seq(self, obs: torch.Tensor) -> torch.Tensor:
        """obs: (B, T, 50, 50, 3) -> R_seq (B, n_steps, 4C, 16, 16).

        Agent steps: windows of `frame_window` frames ending at
        frame_window-1, +frame_stride, ..., T-1 (last window always ends at T-1).
        The memory block updates only every `mem_every`-th step.
        """
        B, T = obs.shape[:2]
        W, S = self.frame_window, self.frame_stride
        ends = list(range(W - 1, T, S))
        if ends[-1] != T - 1:
            ends.append(T - 1)
        state = self.init_state(B, obs.device, obs.dtype)
        Rs = []
        for k, e in enumerate(ends):
            win = obs[:, e - W + 1: e + 1]                                # (B,W,50,50,3)
            x = win.permute(0, 1, 4, 2, 3).flatten(1, 2).contiguous()     # (B,3W,50,50)
            X_t = self.stem(x)
            R, state = self.step(X_t, state,
                                 update_memory=((k + 1) % self.mem_every == 0))
            Rs.append(R)
        return torch.stack(Rs, dim=1)

    def _head_input(self, R_seq: torch.Tensor) -> torch.Tensor:
        """Per-pixel channel LayerNorm: (B,T,C,H,W) -> (B,T,H,W,C) -> LN over C -> back."""
        x = R_seq.permute(0, 1, 3, 4, 2).contiguous()   # (B,T,H,W,C)
        x = self.jepa_norm(x)
        return x.permute(0, 1, 4, 2, 3).contiguous()    # (B,T,C,H,W)

    def jepa_logits(self, R_seq: torch.Tensor) -> torch.Tensor:
        """Per-pixel prototype logits: (B, T, 16, 16, P)."""
        B, T = R_seq.shape[:2]
        feat = self.jepa_feat(self._head_input(R_seq).flatten(0, 1))
        logits = self.jepa_out(feat)                            # (B*T, P, 16, 16)
        logits = logits.unflatten(0, (B, T)).permute(0, 1, 3, 4, 2)  # (B,T,16,16,P)
        return logits

    def jepa_features(self, R_seq: torch.Tensor) -> torch.Tensor:
        """Pre-prototype features for variance/covariance anti-collapse: (B, T, H*W, 2C)."""
        B, T = R_seq.shape[:2]
        feat = self.jepa_feat(self._head_input(R_seq).flatten(0, 1))
        feat = feat.unflatten(0, (B, T))                        # (B,T,2C,16,16)
        return feat.flatten(2, 3)                               # (B,T,256 pixels,2C feat)

    def classify(self, R_last: torch.Tensor) -> torch.Tensor:
        """R_last: (B, 4C, 16, 16) -> (B, 2)."""
        return self.classifier(R_last.mean(dim=(2, 3)))
