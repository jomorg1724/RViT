"""
Encoder for RViT+ v15 — v12's gradient-learned codebook + a VQ-VAE-style ENERGY term.

This KEEPS the v12 mechanism that worked (a gradient-learned codebook C, pulled by
softmax attention from queries=X / keys=H2) and ADDS an energy term on top, mapped
onto VQ-VAE's three-way loss. It REDUCES TO v12 when the energy is zero.

  (E) ENERGY — a transformer energizes the codebook from the current memory:
        energy = W_o^E · softmax(W_q^E·C · (W_k^E·H2)ᵀ) · (W_v^E·H2) + FFN^E   # codebook reads H2
        Z      = C + energy                                                    # C is the residual

  (R) READOUT — v12, but the VALUES are the energized codebook Z (instead of C):
        Z_read = W_o·( softmax(W_q·X · (W_k·H2)ᵀ) @ Z ) + FFN
        H2 ← LSTM(X + Z_read) ;  Z_read → actor & critic

  Three-way loss (the trainer wires the last two; this encoder exposes them):
    1. RL task on Z_read                                      (↔ reconstruction)
    2. energy_coef · mean‖energy‖²  = mean‖Z − C‖²            (↔ commitment / the energy cost)
    3. EMA:  C ← C + r·mean(energy)  = EMA C toward Z         (↔ codebook update / consolidation)

C is a gradient-learned nn.Parameter (the v12 core — the safety net + the reduce-to-v12
property) AND additionally nudged by the slow EMA (the consolidation). When energy → 0,
Z = C and the readout is byte-for-byte v12. Only ONE recurrent state: the key-memory H2.

State note: (Hs, Cs) carries ONE LSTM state — Hs=[H2], Cs=[C2].
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# (Hs, Cs): Hs = [H2 (B,N,d_mem)], Cs = [C2 (B,N,d_mem)].
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

    def forward(self, q_src, k_src, v_src, skip, return_attn=False):
        B, N = q_src.shape[0], q_src.shape[1]
        q = self._heads(self.W_q(self.norm_q(q_src)))
        k = self._heads(self.W_k(self.norm_k(k_src)))
        v = self._heads(self.W_v(self.norm_v(v_src)))
        a = torch.softmax(torch.matmul(q, k.transpose(-2, -1)) * self.scale, dim=-1)
        o = torch.matmul(a, v).transpose(1, 2).reshape(B, N, -1)
        h = skip + self.drop(self.W_o(o))
        out = h + self.ffn(self.norm_ff(h))
        return (out, a) if return_attn else out


class VQAttnEncoder(nn.Module):
    """v12 gradient-codebook readout + a VQ-VAE-style energy term (reduces to v12).

    Args
    ----
    n_tokens    : patch tokens AND codebook slots (e.g. 100).
    d_model     : transformer / token width (MUST equal d_mem).
    d_mem       : LSTM hidden / codebook width.
    n_heads     : attention heads (default 1).
    tx_layers, n_lstm : config parity (architecture fixed: 1 readout LSTM + the energy T).
    drop        : dropout.
    temperature : softmax temperature τ for the readout attention.
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
        self.head_dim = d_model // self.n_heads
        self.scale = self.head_dim ** -0.5
        self.n_lstm = 1
        self.temperature = float(temperature)

        # The codebook: a GRADIENT-LEARNED parameter (the v12 core), also nudged by the
        # slow EMA. Init randn (v12). When energy→0 the readout reads this directly = v12.
        self.codebook = nn.Parameter(torch.randn(1, n_tokens, d_mem))
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)

        # ── ENERGY transformer: Q=C, K=H2, V=H2, skip=C → Z = C + energy ──────
        self.T_E = _XAttn(d_model, d_mem, self.n_heads, drop)
        # Zero-init the energy output so energy ≈ 0 at init ⇒ the model STARTS as v12
        # and grows the energy only if the task earns it against the commitment penalty.
        with torch.no_grad():
            self.T_E.W_o.weight.mul_(1e-2); self.T_E.W_o.bias.zero_()
            self.T_E.ffn[-1].weight.mul_(1e-2); self.T_E.ffn[-1].bias.zero_()

        # ── READOUT (v12): Q=W_q·X, K=W_k·H2, V=Z; Z_read=W_o(softmax@Z)+FFN ──
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_mem, d_model)
        self.W_o = nn.Linear(d_mem, d_model)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_k = nn.LayerNorm(d_mem)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)
        self.cell = nn.LSTMCell(d_model, d_mem)              # H2 ← LSTM(X + Z_read)
        self.cells = nn.ModuleList([self.cell])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem))])

        # Diagnostics.
        self.last_soft: Optional[torch.Tensor] = None          # readout attention (B,H,N,N)
        self.last_energy: Optional[torch.Tensor] = None        # energy = Z−C (B,N,d) DETACHED — EMA signal
        self.last_energy_cost: Optional[torch.Tensor] = None   # mean‖energy‖² per item (B,) DIFFERENTIABLE

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    @torch.no_grad()
    def ema_update_codebook(self, mean_energy: torch.Tensor, rate: float) -> torch.Tensor:
        """EMA the codebook TOWARD the energized codebook Z = C + energy:
            C ← (1−r)·C + r·mean(Z) = C + r·mean(energy)
        (mean over valid batch/time, provided by the trainer). Returns the increment.
        No gradient — this is the slow consolidation on top of the gradient learning."""
        if rate <= 0.0:
            return torch.zeros_like(self.codebook)
        me = mean_energy
        if me.dim() == 2:
            me = me.unsqueeze(0)
        increment = rate * me.to(self.codebook.dtype)
        self.codebook.add_(increment)                        # = (1-r)·C + r·mean(C+energy)
        return increment

    def _heads(self, x):
        B, L, _ = x.shape
        return x.view(B, L, self.n_heads, self.head_dim).transpose(1, 2)

    def forward_step(self, tokens, prev_state, return_attn: bool = False):
        """One frame: energize the codebook (Z = C + energy(C,H2)), then the v12 soft
        readout over Z → Z_read; H2 ← LSTM(X + Z_read). Returns (new_state, rec=[Z_read])."""
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H2, C2 = Hs[0], Cs[0]
        X = tokens
        Hh, dh = self.n_heads, self.head_dim
        C = self.codebook.expand(B, -1, -1)                  # (B,N,d) gradient-learned codebook

        # ── ENERGY: Z = C + T_E(Q=C, K=H2, V=H2, skip=C) ─────────────────────
        Z = self.T_E(C + self.mem_pos_emb, H2, H2, C)        # energized codebook (skip = C)
        energy = Z - C                                       # the energy = Z − C (the deviation)

        # ── READOUT (v12): Q=X, K=H2, V=Z ───────────────────────────────────
        q = self.W_q(self.norm_q(X)) + self.mem_pos_emb
        k = self.W_k(self.norm_k(H2)) + self.mem_pos_emb
        q, k = self._heads(q), self._heads(k)
        v = Z.view(B, N, Hh, dh).transpose(1, 2)             # (B,H,N,dh) — the energized codebook values
        logits = torch.matmul(q, k.transpose(-2, -1)) * self.scale / max(self.temperature, 1e-6)
        soft = torch.softmax(logits, dim=-1)                 # (B,H,N,N)
        attn_out = torch.matmul(soft, v).transpose(1, 2).reshape(B, N, self.d_mem)
        a = self.drop(self.W_o(attn_out))                    # NO X residual (v12)
        Z_read = a + self.ffn(self.norm_ff(a))

        h2, c2 = self.cell((X + Z_read).reshape(B * N, self.d_model),
                           (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_H2 = h2.view(B, N, self.d_mem)
        new_C2 = c2.view(B, N, self.d_mem)

        self.last_soft = soft.detach()
        self.last_energy = energy.detach()                   # (B,N,d) — EMA signal (mean over valid = Δcodebook)
        self.last_energy_cost = energy.pow(2).mean(dim=(1, 2))   # (B,) — commitment / energy penalty

        rec = [Z_read]                                       # actor & critic read Z_read
        if return_attn:
            return ([new_H2], [new_C2]), rec, [soft]
        return ([new_H2], [new_C2]), rec
