"""
Encoder for RViT+ v13 — a self-supervised PREDICTIVE-CODING recurrent transformer
that is FROZEN, then repurposed for a new task by an ENERGY-MODULATION stream.

TWO PARTS, trained in TWO PHASES.

  PART A — the predictive-coding encoder (Phase 1: self-supervised, then FROZEN):
        X = patches
        T1:  Q = W_q·X ,  K = W_k·H1 ,  V = W_v·(V_src) ,  skip = X   →  Z1
        H1 = LSTM1(Z1) ;  H2 = LSTM2(H1)
        predictive coding (JEPA-style):
            z_pred = predictor(proj2(H2_t)) ;  z_targ = stopgrad(proj1(H1_{t+1}))
            L_pc   = ‖z_pred − z_targ‖²  + anti-collapse (variance/covariance, VICReg/LeJEPA-style)
            surprise_t = ‖z_pred − z_targ‖²        # the quantified surprise
      In Phase 1, V_src = H2 (the plain encoder). The encoder learns a recurrent
      latent dynamics whose H2 predicts the next H1.

  PART B — the energy-modulation stream (Phase 2: trained while PART A is FROZEN):
        H3 = LSTM3(H2)
        T2:  Q = W_q'·H2 ,  K = W_k'·H3 ,  V = W_v'·H3 ,  skip = H2   →  Z_energy
      Then T1's value source is REPLACED: V_src = Z_energy (instead of H2). So the
      energy stream perturbs the frozen encoder's V path; Z1 (now modulated) drives
      the actor/critic. Only LSTM3, T2 (+ the heads) learn — PART A stays frozen.

The test: can a frozen self-supervised recurrent transformer+LSTM, trained by
predictive coding on one task, be repurposed for a DIFFERENT (RL) task purely by
modulating its dynamical system with the energy stream?

State note: (Hs, Cs) carries THREE LSTM states — Hs=[H1, H2, H3], Cs=[C1, C2, C3].
H3 is unused in Phase 1 (no energy).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# (Hs, Cs): Hs = [H1, H2, H3], Cs = [C1, C2, C3], each (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _XAttn(nn.Module):
    """A small cross-attention + FFN block with an EXTERNAL residual (skip)."""

    def __init__(self, d_model: int, d_mem: int, n_heads: int, drop: float):
        super().__init__()
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.scale = self.head_dim ** -0.5
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_mem, d_model)
        self.W_v = nn.Linear(d_mem, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_k = nn.LayerNorm(d_mem)
        self.norm_v = nn.LayerNorm(d_mem)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def _heads(self, x):
        B, L, _ = x.shape
        return x.view(B, L, self.n_heads, self.head_dim).transpose(1, 2)

    def forward(self, q_src, k_src, v_src, skip):
        B, N = q_src.shape[0], q_src.shape[1]
        q = self._heads(self.W_q(self.norm_q(q_src)))
        k = self._heads(self.W_k(self.norm_k(k_src)))
        v = self._heads(self.W_v(self.norm_v(v_src)))
        a = torch.softmax(torch.matmul(q, k.transpose(-2, -1)) * self.scale, dim=-1)
        o = torch.matmul(a, v).transpose(1, 2).reshape(B, N, -1)
        h = skip + self.drop(self.W_o(o))          # external residual = skip
        return h + self.ffn(self.norm_ff(h)), a


class VQAttnEncoder(nn.Module):
    """Predictive-coding encoder (PART A) + energy-modulation stream (PART B).

    Args
    ----
    n_tokens    : patch tokens (e.g. 100).
    d_model     : transformer / token width (MUST equal d_mem).
    d_mem       : LSTM hidden width.
    n_heads     : attention heads in both transformers (default 1).
    tx_layers   : config parity (fixed at one block each).
    n_lstm      : config parity (the architecture is fixed: LSTM1/2 + LSTM3).
    drop        : dropout.
    d_latent    : predictive-coding projection width (default d_model).
    temperature : config parity (unused; readout is in the decoder).
    """

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 1,
        tx_layers: int = 1,
        n_lstm: int = 1,
        drop: float = 0.1,
        d_latent: Optional[int] = None,
        temperature: float = 1.0,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads}).")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = int(n_heads)
        self.n_lstm = 1
        d_lat = d_latent or d_model
        self.d_latent = d_lat

        self.pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.pos_emb, std=0.02)

        # ── PART A: predictive-coding encoder (FROZEN in Phase 2) ─────────────
        self.T1 = _XAttn(d_model, d_mem, self.n_heads, drop)   # Q=X, K=H1, V=H2/Z_energy, skip=X
        self.lstm1 = nn.LSTMCell(d_model, d_mem)               # H1 ← LSTM1(Z1)
        self.lstm2 = nn.LSTMCell(d_mem, d_mem)                 # H2 ← LSTM2(H1)
        # JEPA-style predictive coding: H2_t predicts H1_{t+1} in a latent space.
        self.proj1 = nn.Sequential(nn.Linear(d_mem, d_lat), nn.GELU(), nn.Linear(d_lat, d_lat))   # target (H1)
        self.proj2 = nn.Sequential(nn.Linear(d_mem, d_lat), nn.GELU(), nn.Linear(d_lat, d_lat))   # context (H2)
        self.predictor = nn.Sequential(nn.Linear(d_lat, d_lat), nn.GELU(), nn.Linear(d_lat, d_lat))
        self.H0_1 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.C0_1 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.H0_2 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.C0_2 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))

        # ── PART B: energy-modulation stream (trained in Phase 2) ─────────────
        self.lstm3 = nn.LSTMCell(d_mem, d_mem)                 # H3 ← LSTM3(H2)
        self.T2 = _XAttn(d_model, d_mem, self.n_heads, drop)   # Q=H2, K=H3, V=H3, skip=H2 → Z_energy
        self.H0_3 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.C0_3 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))

        # back-compat aliases for generic grad checks / the decoder.
        self.cells = nn.ModuleList([self.lstm1, self.lstm2, self.lstm3])
        self.cell = self.lstm2

        # Diagnostics.
        self.last_H1: Optional[torch.Tensor] = None
        self.last_H2: Optional[torch.Tensor] = None
        self.last_Zenergy: Optional[torch.Tensor] = None
        self.last_surprise: Optional[torch.Tensor] = None     # (B,T) set by predictive_loss

    # ── parameter groups for the two-phase freeze ──────────────────────────
    def pc_modules(self):
        """PART A — frozen in Phase 2 (the self-supervised encoder + predictor)."""
        return [self.T1, self.lstm1, self.lstm2, self.proj1, self.proj2, self.predictor,
                self.pos_emb, self.H0_1, self.C0_1, self.H0_2, self.C0_2]

    def energy_modules(self):
        """PART B — trained in Phase 2 (the energy-modulation stream)."""
        return [self.lstm3, self.T2, self.H0_3, self.C0_3]

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        def _z(p):
            return p.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
        Hs = [_z(self.H0_1), _z(self.H0_2), _z(self.H0_3)]
        Cs = [_z(self.C0_1), _z(self.C0_2), _z(self.C0_3)]
        return Hs, Cs

    def _lstm(self, cell, x, h, c):
        B, N, d = h.shape
        nh, nc = cell(x.reshape(B * N, -1), (h.reshape(B * N, -1), c.reshape(B * N, -1)))
        return nh.view(B, N, d), nc.view(B, N, d)

    def forward_step(self, tokens, prev_state, use_energy: bool = False, return_attn: bool = False):
        """One frame. use_energy=False → plain predictive-coding encoder (Phase 1);
        use_energy=True → the energy stream modulates T1's V path (Phase 2).
        Returns (new_state, rec=[Z1][, attn])."""
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        H1, H2, H3 = Hs[0], Hs[1], Hs[2]
        C1, C2, C3 = Cs[0], Cs[1], Cs[2]
        X = tokens + self.pos_emb

        new_H3, new_C3 = H3, C3
        Zenergy = None
        if use_energy:
            # PART B — H3 ← LSTM3(H2); T2: Q=H2, K=H3, V=H3, skip=H2 → Z_energy
            new_H3, new_C3 = self._lstm(self.lstm3, H2, H3, C3)
            Zenergy, _ = self.T2(H2, new_H3, new_H3, H2)
            v_src = Zenergy                          # inject energy into T1's V path
        else:
            v_src = H2

        # PART A — T1: Q=X, K=H1, V=v_src, skip=X → Z1
        Z1, soft = self.T1(X, H1, v_src, X)
        new_H1, new_C1 = self._lstm(self.lstm1, Z1, H1, C1)       # H1 ← LSTM1(Z1)
        new_H2, new_C2 = self._lstm(self.lstm2, new_H1, H2, C2)   # H2 ← LSTM2(H1)

        self.last_H1, self.last_H2 = new_H1.detach(), new_H2.detach()
        self.last_Zenergy = None if Zenergy is None else Zenergy.detach()

        new_state = ([new_H1, new_H2, new_H3], [new_C1, new_C2, new_C3])
        rec = [Z1]
        if return_attn:
            return new_state, rec, [soft]
        return new_state, rec

    def _vicreg_reg(self, z, mflat):
        """Variance (hinge → unit std) + covariance (decorrelate dims) on the valid
        embeddings of z (…,L). Prevents representational collapse without EMA/stop-grad."""
        zf = z.reshape(-1, self.d_latent)[mflat]
        if zf.shape[0] < 2:
            return z.new_zeros(()), z.new_zeros(())
        std = torch.sqrt(zf.var(dim=0) + 1e-4)
        loss_var = torch.relu(1.0 - std).mean()
        zc = zf - zf.mean(dim=0)
        cov = (zc.T @ zc) / (zf.shape[0] - 1)
        loss_cov = (cov - torch.diag(torch.diag(cov))).pow(2).sum() / self.d_latent
        return loss_var, loss_cov

    # ── predictive-coding loss over a sequence of (H1, H2) ──────────────────
    def predictive_loss(self, H1_seq, H2_seq, valid_mask, var_coef: float = 1.0,
                        cov_coef: float = 0.04):
        """VICReg-style predictive coding: predictor(proj2(H2_t)) ≈ proj1(H1_{t+1}),
        with variance+covariance anti-collapse on BOTH embeddings (no EMA, no stop-grad
        — so both projectors train, and the latents can't collapse). H1_seq,H2_seq:
        (B,T,N,d); valid_mask: (B,T). surprise = the prediction error. Returns
        (loss, surprise_seq (B,T), parts)."""
        B, T, N, d = H1_seq.shape
        z_pred = self.predictor(self.proj2(H2_seq[:, :-1]))          # from H2_t   (B,T-1,N,L)
        z_targ = self.proj1(H1_seq[:, 1:])                          # to H1_{t+1} (NO stop-grad)
        err = (z_pred - z_targ).pow(2).mean(dim=-1)                 # (B,T-1,N) per-token MSE
        surprise = err.mean(dim=-1)                                 # (B,T-1) per-step surprise
        m = valid_mask[:, 1:]
        denom = m.sum().clamp(min=1.0)
        loss_pred = (surprise * m).sum() / denom                   # invariance term
        mflat = m.reshape(B, T - 1, 1).expand(-1, -1, N).reshape(-1).bool()
        v1, c1 = self._vicreg_reg(z_pred, mflat)
        v2, c2 = self._vicreg_reg(z_targ, mflat)
        loss_var, loss_cov = v1 + v2, c1 + c2
        loss = loss_pred + var_coef * loss_var + cov_coef * loss_cov
        surprise_full = torch.zeros(B, T, device=H1_seq.device)
        surprise_full[:, :-1] = surprise.detach()
        self.last_surprise = surprise_full
        return loss, surprise_full, {"pred": float(loss_pred.detach()),
                                     "var": float(loss_var.detach()), "cov": float(loss_cov.detach())}
