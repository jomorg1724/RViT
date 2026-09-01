"""
KDA visual-accumulator convolutional recurrent transformer — VDA16 variant.

Lineage: the dual-state conv-memory model (conv_memory_model.py, the v3/dual-state
variant that learned the change) with the static-EMA visual accumulator H_VA
replaced by a *learned* accumulator family, selectable by `accum_mode`:

  "ema"   — the current in-flight variant: H_VA <- d ⊙ H_VA + (1-d) ⊙ X_t,
            d = sigmoid(accum_logit): C static per-channel time constants.
  "gated" — dynamic decay field + decoupled write (GLA-flavoured, vector state):
            a_t = sigmoid(W_a[X_t‖H1] + b_a)      (B,C,16,16) per-pixel, per-channel
            b_t = sigmoid(W_b[X_t‖H1] + b_b)      write strength decoupled from decay
            H_VA <- a_t ⊙ H_VA + b_t ⊙ X_t
            Biases initialised so a_t≈accum_decay, b_t≈1-accum_decay at start
            (=> identical to "ema" at initialisation).
  "kda"   — gated delta rule (Kimi Delta Attention style) per pixel:
            state S_p ∈ R^{h x d_k x d_v} per pixel p (matrix associative memory)
            k,q = L2norm(W_k/W_q[X_t‖H1]);  v = W_v[X_t‖H1]
            a_t = sigmoid(W_a[X_t‖H1] + b_a)      per-head-channel decay (0,1)
            b_t = sigmoid(W_b[X_t‖H1])            per-head write strength
            S  <- (a_t ⊙ S) + b_t · k (v - (a_t ⊙ S)^T k)^T     error-corrected write
            o  = RMSNorm_head(S^T q) ⊙ sigmoid(W_g[X_t‖H1])     gated readout
            Reference: Kimi Linear (arXiv:2510.26692), KDA Eqs. 1-10. Sequences here
            are T<=20 steps, so the plain per-step recurrence is used (no chunkwise
            kernels — those exist for million-token LM training and add nothing here).

The delta rule makes the write proportional to the *prediction error against the
stored content*: static displays stop being re-integrated (error -> 0), and a
change event produces an immediate, localised write — ||v - S^T k|| per pixel is a
built-in surprise/change signal (exposed via `accum_stats` for analysis).

Everything downstream of the accumulator readout is UNCHANGED from the dual-state
model: vision block (X-side convs widened to 2C), H1/H2 memory block with output
noise on H1, R = [H1‖H2‖Z‖att_vis] (4C), per-pixel JEPA head, mean-pool classifier.

Default geometry is sized for VDA16 (4x4 grid, 100x100 px frames): map_size=16
gives a 4x4-pixel patch per stimulus cell; n_channels=64; heads x d_v = C.
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
    """Full-image conv processing: SxSx(3*frame_window) -> [C, map, map].

    Works for any input size (final bilinear interpolate); for VDA16 the input is
    100x100 and map_size=16 gives a 4x4-pixel patch per 25px stimulus cell.
    """

    def __init__(self, channels: int = 128, map_size: int = 16, in_channels: int = 3):
        super().__init__()
        self.map_size = map_size
        c1 = max(channels // 4, 8)
        c2 = max(channels // 2, 8)
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, c1, 7, stride=2, padding=3, bias=False), nn.GELU(),
            SEResStage(c1, c2, stride=1),
            SEResStage(c2, channels, stride=2),
        )

    def forward(self, frame: torch.Tensor) -> torch.Tensor:  # frame: (B,3W,S,S)
        h = self.net(frame)
        return F.interpolate(h, size=(self.map_size, self.map_size),
                             mode="bilinear", align_corners=False)            # (B,C,map,map)


class ConvAttentionBlock(nn.Module):
    """Recurrent conv-transformer vision block: Q<-X, K<-[X,H1], V<-[X,H2].

    Per-pixel channel-inner-product attention with a 2-way softmax gate,
    FFN, CONCATENATED residual, and an SE block.
    `in_c` allows a wider visual input (X concatenated with the accumulator
    readout); H-sides and the output stay at width c.
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
        Sx = (Q * Kx).sum(dim=1, keepdim=True) * self.scale   # (B,1,map,map)
        Sh = (Q * Kh).sum(dim=1, keepdim=True) * self.scale
        A = torch.softmax(torch.cat([Sx, Sh], dim=1), dim=1)   # (B,2,map,map) per-pixel gate
        att = A[:, 0:1] * Vx + A[:, 1:2] * Vh                  # (B,C,map,map)
        att = self.ffn(att)
        res = torch.cat([X, att], dim=1)                       # CONCAT residual
        Z = self.proj(self.se(res))                            # (B,C,map,map)
        if return_attn:
            return Z, att, A
        return Z, att


class ConvMemoryBlock(nn.Module):
    """One memory structure: Q<-H1, K/V<-[Z,H1]; same attention formula.

    H1' = SE-proj([H1 || att])  (+ N(0, noise) on the OUTPUT, if set)  — the persistent state
    H2' = att                                                          — the raw ephemeral read
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
        H1_new = self.proj(self.se(res))                        # (B,C,map,map)
        if self.memory_noise_std > 0.0:
            H1_new = H1_new + self.memory_noise_std * torch.randn_like(H1_new)
        H2_new = att                                            # raw read, no normalization
        return H1_new, H2_new


def _logit(p: float) -> float:
    p = min(max(float(p), 1e-3), 1.0 - 1e-3)
    return float(np.log(p / (1.0 - p)))


class GatedVisualAccumulator(nn.Module):
    """Dynamic-decay, decoupled-write VECTOR accumulator ("gated" mode).

        a_t = sigmoid(W_a[X_t‖H1] + b_a)      per-pixel, per-channel decay field
        b_t = sigmoid(W_b[X_t‖H1] + b_b)      write strength, decoupled from a_t
        H_VA <- a_t ⊙ H_VA + b_t ⊙ X_t

    Bias-init: a_t ≈ accum_decay, b_t ≈ 1-accum_decay at start (== the static EMA).
    """

    def __init__(self, c: int = 128, accum_decay: float = 0.5):
        super().__init__()
        self.W_a = nn.Conv2d(2 * c, c, 1, bias=True)
        self.W_b = nn.Conv2d(2 * c, c, 1, bias=True)
        nn.init.zeros_(self.W_a.weight); nn.init.zeros_(self.W_b.weight)
        nn.init.constant_(self.W_a.bias, _logit(accum_decay))
        nn.init.constant_(self.W_b.bias, _logit(1.0 - accum_decay))

    def init_state(self, B: int, map_size: int, device, dtype) -> torch.Tensor:
        return torch.zeros(B, self.W_a.out_channels, map_size, map_size,
                           device=device, dtype=dtype)

    def forward(self, X: torch.Tensor, H1: torch.Tensor, HVA: torch.Tensor):
        inp = torch.cat([X, H1], dim=1)
        a = torch.sigmoid(self.W_a(inp))
        b = torch.sigmoid(self.W_b(inp))
        HVA = a * HVA + b * X
        stats = {"alpha_mean": a.detach().mean(), "beta_mean": b.detach().mean()}
        return HVA, HVA, stats                    # (new state, readout, diagnostics)


class KDAVisualAccumulator(nn.Module):
    """Gated delta-rule (KDA-style) visual accumulator, one matrix state per pixel.

    State S: (B, h, d_k, d_v, P) with P = map*map pixels. Per step:

        k,q = L2norm(W_k/W_q(inp)),  v = W_v(inp),   inp = [X_t ‖ H1]
        a_t = sigmoid(W_a(inp) + b_a)        per-head-channel decay, bias-init accum_decay
        b_t = sigmoid(W_b(inp))              per-head write strength
        S   <- (a_t ⊙ S) + b_t · k (v - (a_t ⊙ S)^T k)^T      delta-rule write
        o    = RMSNorm_dv(S^T q) ⊙ sigmoid(W_g(inp))          gated readout (B,C,map,map)

    k,q are L2-normalised so (I - b·k·kᵀ)Diag(a) has eigenvalues in [0,1]; the state
    update is computed in fp32 regardless of autocast (the accumulator is the
    precision-sensitive part of the recurrence).
    """

    def __init__(self, c: int = 64, heads: int = 4, head_dim: int = 16,
                 accum_decay: float = 0.5):
        super().__init__()
        if heads * head_dim != c:
            raise ValueError(f"heads*head_dim must equal n_channels ({c}), "
                             f"got {heads}x{head_dim}")
        self.c, self.h, self.dk, self.dv = c, heads, head_dim, head_dim
        inp_c = 2 * c
        self.W_k = nn.Conv2d(inp_c, heads * self.dk, 1, bias=False)
        self.W_v = nn.Conv2d(inp_c, heads * self.dv, 1, bias=False)
        self.W_q = nn.Conv2d(inp_c, heads * self.dk, 1, bias=False)
        self.W_a = nn.Conv2d(inp_c, heads * self.dk, 1, bias=True)
        self.W_b = nn.Conv2d(inp_c, heads, 1, bias=True)
        self.W_g = nn.Conv2d(inp_c, heads * self.dv, 1, bias=True)
        nn.init.zeros_(self.W_a.weight)
        nn.init.constant_(self.W_a.bias, _logit(accum_decay))
        nn.init.zeros_(self.W_b.weight)
        nn.init.constant_(self.W_b.bias, _logit(1.0 - accum_decay))
        self.rms_gain = nn.Parameter(torch.ones(heads * self.dv))
        self.eps = 1e-6

    def init_state(self, B: int, map_size: int, device, dtype) -> torch.Tensor:
        P = map_size * map_size
        return torch.zeros(B, self.h, self.dk, self.dv, P, device=device, dtype=dtype)

    def forward(self, X: torch.Tensor, H1: torch.Tensor, S: torch.Tensor):
        B, _, H, W = X.shape
        inp = torch.cat([X, H1], dim=1)
        h, dk, dv, P = self.h, self.dk, self.dv, H * W

        def shp(t):  # (B, h*d, H, W) -> (B, h, d, P)
            return t.view(B, h, -1, P)

        k = shp(self.W_k(inp)); q = shp(self.W_q(inp)); v = shp(self.W_v(inp))
        k = F.normalize(k.float(), dim=2)                 # L2 over d_k
        q = F.normalize(q.float(), dim=2)
        v = v.float()
        a = torch.sigmoid(self.W_a(inp)).view(B, h, dk, 1, P).float()
        b = torch.sigmoid(self.W_b(inp)).view(B, h, 1, 1, P).float()

        S = S.float()
        S_dec = a * S                                              # decayed state
        v_hat = torch.einsum("bhikp,bhip->bhkp", S_dec, k)         # current prediction
        err = v - v_hat                                            # prediction error
        S = S_dec + b * torch.einsum("bhip,bhkp->bhikp", k, err)   # delta-rule write

        o = torch.einsum("bhikp,bhip->bhkp", S, q)                 # readout (B,h,dv,P)
        o = o * torch.rsqrt(o.pow(2).mean(dim=2, keepdim=True) + self.eps)
        o = o * self.rms_gain.view(1, h, dv, 1)
        g = torch.sigmoid(self.W_g(inp)).view(B, h, dv, P).float()
        o = (o * g).reshape(B, self.c, H, W)

        stats = {"alpha_mean": a.detach().mean(), "beta_mean": b.detach().mean(),
                 "err_norm": err.detach().norm(dim=2).mean()}      # per-head err ||.||, meaned
        return S.to(X.dtype), o.to(X.dtype), stats


class KDAConvMemoryModel(nn.Module):
    """Full recurrent model: stem -> [accumulator] -> vision conv-attn -> memory
    conv-attn -> JEPA head (+ classifier).

    Recurrent state: (H1, H2, ACC). ACC is a (B,C,map,map) tensor for
    accum_mode in {"ema","gated"} and a (B,h,d_k,d_v,P) tensor for "kda".
    """

    def __init__(self, n_channels: int = 64, proto_dim: int = 256, map_size: int = 16,
                 memory_noise_std: float = 0.0,
                 frame_window: int = 1, frame_stride: int = 1, mem_every: int = 1,
                 accum_mode: str = "kda", accum_decay: float = 0.5,
                 kda_heads: int = 4, kda_head_dim: int = 16):
        super().__init__()
        if accum_mode not in ("ema", "gated", "kda"):
            raise ValueError(f"accum_mode must be ema|gated|kda, got {accum_mode!r}")
        self.n_channels = n_channels
        self.map_size = map_size
        self.proto_dim = proto_dim
        self.memory_noise_std = float(memory_noise_std)
        self.frame_window = int(frame_window)
        self.frame_stride = int(frame_stride)
        self.mem_every = int(mem_every)
        self.accum_mode = accum_mode
        self.kda_heads = int(kda_heads)
        self.kda_head_dim = int(kda_head_dim)

        if accum_mode == "ema":
            init = _logit(accum_decay)
            self.accum_logit = nn.Parameter(torch.full((n_channels,), init))
            self.accumulator = None
        elif accum_mode == "gated":
            self.accumulator = GatedVisualAccumulator(n_channels, accum_decay)
        else:
            self.accumulator = KDAVisualAccumulator(n_channels, self.kda_heads,
                                                    self.kda_head_dim, accum_decay)

        self.stem = ConvStem(channels=n_channels, map_size=map_size,
                             in_channels=3 * self.frame_window)
        # The accumulator readout is always concatenated with X_t (X-side widens to 2C).
        self.vision = ConvAttentionBlock(n_channels, in_c=2 * n_channels)
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
        acc = self.accumulator.init_state(B, self.map_size, device, dtype) \
            if self.accumulator is not None else z.clone()
        return (z, z.clone(), acc)                              # (H1, H2, ACC)

    def _accumulate(self, X_t: torch.Tensor, H1: torch.Tensor, ACC: torch.Tensor):
        """One accumulator update; returns (ACC_new, readout, stats)."""
        if self.accum_mode == "ema":
            d = torch.sigmoid(self.accum_logit).view(1, -1, 1, 1)
            ACC = d * ACC + (1.0 - d) * X_t
            return ACC, ACC, {"alpha_mean": d.detach().mean(),
                              "beta_mean": (1.0 - d).detach().mean()}
        return self.accumulator(X_t, H1, ACC)

    def step(self, X_t: torch.Tensor, state, update_memory: bool = True,
             return_stats: bool = False):
        H1, H2, ACC = state
        ACC, acc_read, stats = self._accumulate(X_t, H1, ACC)
        Xin = torch.cat([X_t, acc_read], dim=1)                 # (B,2C,map,map)
        Z, att_vis = self.vision(Xin, H1, H2)
        if update_memory:
            H1, H2 = self.memory(Z, H1)
        R = torch.cat([H1, H2, Z, att_vis], dim=1)              # (B,4C,map,map)
        if return_stats:
            return R, (H1, H2, ACC), stats
        return R, (H1, H2, ACC)

    def forward_seq(self, obs: torch.Tensor, return_stats: bool = False):
        """obs: (B, T, S, S, 3) -> R_seq (B, n_steps, 4C, map, map).

        Agent steps: windows of `frame_window` frames ending at
        frame_window-1, +frame_stride, ..., T-1 (last window always ends at T-1).
        The memory block updates only every `mem_every`-th step; the visual
        accumulator updates EVERY step (it is the fast sensory integrator).
        """
        B, T = obs.shape[:2]
        W, S = self.frame_window, self.frame_stride
        ends = list(range(W - 1, T, S))
        if ends[-1] != T - 1:
            ends.append(T - 1)
        state = self.init_state(B, obs.device, obs.dtype)
        Rs, stats_seq = [], []
        for k, e in enumerate(ends):
            win = obs[:, e - W + 1: e + 1]                                # (B,W,S,S,3)
            x = win.permute(0, 1, 4, 2, 3).flatten(1, 2).contiguous()     # (B,3W,S,S)
            X_t = self.stem(x)
            if return_stats:
                R, state, stats = self.step(X_t, state,
                                            update_memory=((k + 1) % self.mem_every == 0),
                                            return_stats=True)
                stats_seq.append(stats)
            else:
                R, state = self.step(X_t, state,
                                     update_memory=((k + 1) % self.mem_every == 0))
            Rs.append(R)
        R_seq = torch.stack(Rs, dim=1)
        if return_stats:
            return R_seq, stats_seq
        return R_seq

    def _head_input(self, R_seq: torch.Tensor) -> torch.Tensor:
        """Per-pixel channel LayerNorm: (B,T,C,H,W) -> (B,T,H,W,C) -> LN over C -> back."""
        x = R_seq.permute(0, 1, 3, 4, 2).contiguous()   # (B,T,H,W,C)
        x = self.jepa_norm(x)
        return x.permute(0, 1, 4, 2, 3).contiguous()    # (B,T,C,H,W)

    def jepa_logits(self, R_seq: torch.Tensor) -> torch.Tensor:
        """Per-pixel prototype logits: (B, T, map, map, P)."""
        B, T = R_seq.shape[:2]
        feat = self.jepa_feat(self._head_input(R_seq).flatten(0, 1))
        logits = self.jepa_out(feat)                            # (B*T, P, map, map)
        return logits.unflatten(0, (B, T)).permute(0, 1, 3, 4, 2)  # (B,T,map,map,P)

    def jepa_features(self, R_seq: torch.Tensor) -> torch.Tensor:
        """Pre-prototype features for variance/covariance anti-collapse: (B, T, P_pix, 2C)."""
        B, T = R_seq.shape[:2]
        feat = self.jepa_feat(self._head_input(R_seq).flatten(0, 1))
        feat = feat.unflatten(0, (B, T))                        # (B,T,2C,map,map)
        return feat.flatten(2, 3)                               # (B,T,map*map,2C)

    def classify(self, R_last: torch.Tensor) -> torch.Tensor:
        """R_last: (B, 4C, map, map) -> (B, 2)."""
        return self.classifier(R_last.mean(dim=(2, 3)))
