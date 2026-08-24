"""
Encoder for RViT+ v14 — TWO coupled recurrent modules trained CONCURRENTLY by two
objectives, with cross-detachments that firewall the gradients.

  MODULE 1 (self-supervised predictive coding):
        Z1 = T1( Q=W_q·X ,  K=W_k·Z2.detach() ,  V=W_v·H1 ,  skip=X )
        H1 = LSTM1(Z1, H1_prev)
        JEPA loss (LeJEPA/VICReg-style, latent — NO pixels):
            predictor(proj(H1_t)) ≈ proj(H1_{t+k})   + isotropic anti-collapse
            surprise_t = that prediction error
      Trained PURELY by self-supervision. Z2 is detached where it enters T1, so this
      loss never trains Module 2.

  MODULE 2 (RL):
        Z2 = T2( Q=W_q'·H1.detach() ,  K=W_k'·H2 ,  V=W_v'·H2 ,  skip=H1.detach() )
        H2 = LSTM2(Z2, H2_prev)                     # ← actor + critic read H2
      Trained ONLY by the RL objective. H1 is detached where it enters T2, so the RL
      loss never trains Module 1. Z2 (full grad) feeds LSTM2; Z2.detach() feeds T1.

Forward coupling per frame:  Z2 = T2(H1_prev, H2_prev) ;  H2 = LSTM2(Z2) ;
                             Z1 = T1(X, Z2.detach, H1_prev) ;  H1 = LSTM1(Z1).
The modules influence each other's dynamics (the H1→T2→Z2→T1→H1 cycle) but never
share gradients. Concurrent training: one optimizer, L_RL + ss_coef·L_SS.

State note: (Hs, Cs) carries TWO LSTM states — Hs=[H1, H2], Cs=[C1, C2].
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# (Hs, Cs): Hs = [H1, H2], Cs = [C1, C2], each (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _XAttn(nn.Module):
    """Cross-attention + FFN block with an EXTERNAL residual (skip)."""

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
    """Two coupled modules: Module 1 (T1+LSTM1, self-supervised predictive coding) and
    Module 2 (T2+LSTM2, RL), trained concurrently with cross-detached gradients.

    Args
    ----
    n_tokens    : patch tokens (e.g. 100).
    d_model     : transformer / token width (MUST equal d_mem).
    d_mem       : LSTM hidden width.
    n_heads     : attention heads in both transformers (default 1).
    tx_layers, n_lstm : config parity (architecture fixed: T1/T2 + LSTM1/LSTM2).
    drop        : dropout.
    d_latent    : predictive-coding projection width (default d_model).
    pc_horizon  : predict H1 this many steps ahead (default 1).
    temperature : config parity (unused).
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
        pc_horizon: int = 1,
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
        self.pc_horizon = int(pc_horizon)

        self.pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.pos_emb, std=0.02)

        # ── MODULE 1: predictive-coding encoder (self-supervised) ─────────────
        self.T1 = _XAttn(d_model, d_mem, self.n_heads, drop)   # Q=X, K=Z2.detach, V=H1, skip=X
        self.lstm1 = nn.LSTMCell(d_model, d_mem)               # H1 ← LSTM1(Z1)
        # JEPA latent predictive coding on H1: predictor(proj(H1_t)) ≈ proj(H1_{t+k}).
        self.proj = nn.Sequential(nn.Linear(d_mem, d_lat), nn.GELU(), nn.Linear(d_lat, d_lat))
        self.predictor = nn.Sequential(nn.Linear(d_lat, d_lat), nn.GELU(), nn.Linear(d_lat, d_lat))
        self.H0_1 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.C0_1 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))

        # ── MODULE 2: RL module (trained by reward) ───────────────────────────
        self.T2 = _XAttn(d_model, d_mem, self.n_heads, drop)   # Q=H1.detach, K=H2, V=H2, skip=H1.detach
        self.lstm2 = nn.LSTMCell(d_model, d_mem)               # H2 ← LSTM2(Z2)
        self.H0_2 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))
        self.C0_2 = nn.Parameter(torch.zeros(1, n_tokens, d_mem))

        # back-compat aliases for generic grad checks / the decoder.
        self.cells = nn.ModuleList([self.lstm1, self.lstm2])
        self.cell = self.lstm2

        # Diagnostics.
        self.last_H1: Optional[torch.Tensor] = None
        self.last_H2: Optional[torch.Tensor] = None
        self.last_Z2: Optional[torch.Tensor] = None
        self.last_surprise: Optional[torch.Tensor] = None     # (B,T) set by predictive_loss

    def module1_params(self):
        return [self.T1, self.lstm1, self.proj, self.predictor, self.pos_emb, self.H0_1, self.C0_1]

    def module2_params(self):
        return [self.T2, self.lstm2, self.H0_2, self.C0_2]

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        def _z(p):
            return p.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
        return [_z(self.H0_1), _z(self.H0_2)], [_z(self.C0_1), _z(self.C0_2)]

    def _lstm(self, cell, x, h, c):
        B, N, d = h.shape
        nh, nc = cell(x.reshape(B * N, -1), (h.reshape(B * N, -1), c.reshape(B * N, -1)))
        return nh.view(B, N, d), nc.view(B, N, d)

    def forward_step(self, tokens, prev_state, return_attn: bool = False):
        """One frame. Runs BOTH modules with the cross-detachments. rec = [H2]
        (the RL state the heads read). H1 is exposed (the returned state) for the
        self-supervised loss."""
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        H1, H2 = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]
        X = tokens + self.pos_emb

        # ── MODULE 2 (RL): Q=H1.detach, K=H2, V=H2, skip=H1.detach → Z2 → H2 ──
        H1d = H1.detach()                                   # firewall: no RL grad into Module 1
        Z2, _ = self.T2(H1d, H2, H2, H1d)
        new_H2, new_C2 = self._lstm(self.lstm2, Z2, H2, C2)

        # ── MODULE 1 (SS): Q=X, K=Z2.detach, V=H1, skip=X → Z1 → H1 ──────────
        Z1, soft = self.T1(X, Z2.detach(), H1, X)           # firewall: no SS grad into Module 2
        new_H1, new_C1 = self._lstm(self.lstm1, Z1, H1, C1)

        self.last_H1, self.last_H2 = new_H1.detach(), new_H2.detach()
        self.last_Z2 = Z2.detach()

        new_state = ([new_H1, new_H2], [new_C1, new_C2])
        rec = [new_H2]                                      # actor & critic read H2
        if return_attn:
            return new_state, rec, [soft]
        return new_state, rec

    def _vicreg_reg(self, z, mflat):
        zf = z.reshape(-1, self.d_latent)[mflat]
        if zf.shape[0] < 2:
            return z.new_zeros(()), z.new_zeros(())
        std = torch.sqrt(zf.var(dim=0) + 1e-4)
        loss_var = torch.relu(1.0 - std).mean()
        zc = zf - zf.mean(dim=0)
        cov = (zc.T @ zc) / (zf.shape[0] - 1)
        loss_cov = (cov - torch.diag(torch.diag(cov))).pow(2).sum() / self.d_latent
        return loss_var, loss_cov

    def predictive_loss(self, H1_seq, valid_mask, var_coef: float = 1.0, cov_coef: float = 0.04):
        """LeJEPA/VICReg-style latent predictive coding on H1: predictor(proj(H1_t))
        predicts proj(H1_{t+k}) (k=pc_horizon), with isotropic var+cov anti-collapse
        (no EMA/stop-grad). H1_seq: (B,T,N,d); valid_mask: (B,T). surprise = the
        prediction error. Returns (loss, surprise_seq (B,T), parts)."""
        B, T, N, d = H1_seq.shape
        k = self.pc_horizon
        if T <= k:
            z = H1_seq.new_zeros(())
            return z, torch.zeros(B, T, device=H1_seq.device), {"pred": 0.0, "var": 0.0, "cov": 0.0}
        z_pred = self.predictor(self.proj(H1_seq[:, :-k]))         # from H1_t      (B,T-k,N,L)
        z_targ = self.proj(H1_seq[:, k:])                          # to H1_{t+k} (NO stop-grad)
        err = (z_pred - z_targ).pow(2).mean(dim=-1)                # (B,T-k,N)
        surprise = err.mean(dim=-1)                                # (B,T-k)
        m = valid_mask[:, k:]
        denom = m.sum().clamp(min=1.0)
        loss_pred = (surprise * m).sum() / denom
        mflat = m.reshape(B, T - k, 1).expand(-1, -1, N).reshape(-1).bool()
        v1, c1 = self._vicreg_reg(z_pred, mflat)
        v2, c2 = self._vicreg_reg(z_targ, mflat)
        loss = loss_pred + var_coef * (v1 + v2) + cov_coef * (c1 + c2)
        surprise_full = torch.zeros(B, T, device=H1_seq.device)
        surprise_full[:, :-k] = surprise.detach()
        self.last_surprise = surprise_full
        return loss, surprise_full, {"pred": float(loss_pred.detach()),
                                     "var": float((v1 + v2).detach()), "cov": float((c1 + c2).detach())}
