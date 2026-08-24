"""
Encoder for RViT+ v11_part4_BROADCAST: two INDEPENDENT modules (no cross-talk), with
the Herman/Morgan **FiLM multiplicative self-attention** in each (paper Eq 9-10, identity-init gate):

    Q = Q_X(X) ⊙ (1 + Q_H(H)) ,  K = K_X(X) ⊙ (1+K_H) ,  V = V_X(X) ⊙ (1+V_H)
    Z = X + softmax(QKᵀ/√d) · V + FFN                        (residual = X)

Unlike the cross-talk variants, each module's top-down H is its OWN memory only (no
concatenation) — that is what keeps the two modules independent:

  μ module (→ actor):  self-attn over X, top-down = Hμ, residual = X  → Zμ ; Hμ = LSTM(Zμ)
  Q module (→ critic): self-attn over X, top-down = HQ, residual = X  → ZQ ; HQ = LSTM(ZQ)
Each memory is updated by its own module's output; the modules never touch each other's state.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _MultFeedbackBlock(nn.Module):
    """Multiplicative-feedback self-attention. Q/K/V are each the Hadamard product of a
    bottom-up projection of the image X and a top-down projection of the memory H;
    standard softmax self-attention over the N patch tokens; residual supplied by the
    caller (X). LayerNorm on Q,K before the softmax."""

    def __init__(self, d_model: int, n_heads: int, d_mem_in: int, drop: float) -> None:
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model, self.n_heads, self.dh = d_model, n_heads, d_model // n_heads
        self.W_XQ = nn.Linear(d_model, d_model)
        self.W_XK = nn.Linear(d_model, d_model)
        self.W_XV = nn.Linear(d_model, d_model)
        self.W_HQ = nn.Linear(d_mem_in, d_model)
        self.W_HK = nn.Linear(d_mem_in, d_model)
        self.W_HV = nn.Linear(d_mem_in, d_model)
        for m in (self.W_HQ, self.W_HK, self.W_HV):
            nn.init.zeros_(m.weight); nn.init.zeros_(m.bias)
        self.W_o = nn.Linear(d_model, d_model)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_k = nn.LayerNorm(d_model)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def _heads(self, x):
        B, N, _ = x.shape
        return x.view(B, N, self.n_heads, self.dh).transpose(1, 2)

    def forward(self, X, H, residual, return_attn=False):
        Q = self.W_XQ(X) * (1.0 + self.W_HQ(H))   # FiLM feedback gate
        K = self.W_XK(X) * (1.0 + self.W_HK(H))
        V = self.W_XV(X) * (1.0 + self.W_HV(H))
        Q = self.norm_q(Q); K = self.norm_k(K)
        qh, kh, vh = self._heads(Q), self._heads(K), self._heads(V)
        scores = torch.matmul(qh, kh.transpose(-2, -1)) / (self.dh ** 0.5)
        aw = torch.softmax(scores, dim=-1)
        out = torch.matmul(aw, vh).transpose(1, 2).contiguous().view(X.shape)
        Z = residual + self.drop(self.W_o(out))
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, (aw if return_attn else None)


class DualStreamEncoder(nn.Module):
    """Two INDEPENDENT multiplicative-feedback modules (no cross-talk). Same
    constructor / state / forward_step interface as the cross-attention encoder."""

    def __init__(self, n_tokens: int, d_model: int = 128, d_mem: int = 128,
                 n_heads: int = 1, tx_layers: int = 1, n_lstm: int = 2, drop: float = 0.1) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if int(n_lstm) != 2:
            raise ValueError("dual-stream needs exactly n_lstm=2 (Hμ, HQ).")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.stream_dim = d_model                    # split readout (each head reads ONE stream)

        # each module's top-down reads its OWN single memory (d_mem_in = d_mem) — no cross-talk
        self.mu_block = _MultFeedbackBlock(d_model, n_heads, d_mem, drop)
        self.q_block = _MultFeedbackBlock(d_model, n_heads, d_mem, drop)
        self.sal_block = self.mu_block               # back-compat aliases
        self.td_block = self.q_block

        self.cell_mu = nn.LSTMCell(d_model, d_mem)   # Hμ ← Zμ
        self.cell_q = nn.LSTMCell(d_model, d_mem)    # HQ ← ZQ
        self.cells = nn.ModuleList([self.cell_mu, self.cell_q])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        Hmu, Hq = Hs[0], Hs[1]
        Cmu, Cq = Cs[0], Cs[1]
        X = tokens

        # independent: each module self-attends over X gated by its OWN memory, residual X
        Zmu, aw_mu = self.mu_block(X, Hmu, residual=X, return_attn=return_attn)
        Zq, aw_q = self.q_block(X, Hq, residual=X, return_attn=return_attn)

        hmu, cmu = self.cell_mu(Zmu.reshape(B * N, self.d_model),
                                (Hmu.reshape(B * N, self.d_mem), Cmu.reshape(B * N, self.d_mem)))
        hq, cq = self.cell_q(Zq.reshape(B * N, self.d_model),
                             (Hq.reshape(B * N, self.d_mem), Cq.reshape(B * N, self.d_mem)))
        new_Hs = [hmu.view(B, N, self.d_mem), hq.view(B, N, self.d_mem)]
        new_Cs = [cmu.view(B, N, self.d_mem), cq.view(B, N, self.d_mem)]

        rec = [Zmu, Zq]                              # Zμ → actor, ZQ → critic
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw_mu, aw_q]
        return (new_Hs, new_Cs), rec
