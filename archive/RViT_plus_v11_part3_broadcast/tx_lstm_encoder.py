"""
Encoder for RViT+ v11_part3_broadcast: the v11_part2 split dual-stream structure
(priority → actor, value → critic, two per-token LSTMs) with the cross-attention
blocks replaced by the Herman/Morgan multiplicative self-attention in the **FiLM**
form (paper §4.7.3, Eq 9-10 / §5.2, Eq 13-17, with an identity-init feedback gate):

    Q = Q_X(X) ⊙ (1 + Q_H(H)) ,  K = K_X(X) ⊙ (1 + K_H(H)) ,  V = V_X(X) ⊙ (1 + V_H(H))
    Z = X + softmax(QKᵀ/√d) · V + FFN                         (residual = X)

i.e. a self-attention over the patch tokens X in which the top-down memory H FiLM-gates
each of the bottom-up Q/K/V projections — the (1 + ·) wrapping with a ZERO-init top-down
projection means feedback is OFF at init, so the block starts as plain self-attention
over X (a clean baseline, no explosion) and engages as the top-down weights train. We
LayerNorm Q,K after the gate and before the softmax to keep the logits bounded.

Two streams, two recurrent states (the only change from the paper's single-stream /
single-memory form). For BOTH streams the bottom-up input is the current image X, the
top-down input is the concatenation of both memories H = [H1 ‖ H2], and the residual is
X. The two streams are parallel with separate weights; the split read-out (priority →
actor, value → critic) is unchanged. Memory updates: H1 = LSTM1(X), H2 = LSTM2(Z_priority).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _MultFeedbackBlock(nn.Module):
    """Multiplicative-feedback self-attention. Q/K/V are each the Hadamard product of a
    bottom-up projection of the image X and a top-down projection of the memory H; the
    attention is a standard softmax self-attention over the N patch tokens; the residual
    is supplied by the caller (X). LayerNorm on Q,K before the softmax."""

    def __init__(self, d_model: int, n_heads: int, d_mem_in: int, drop: float) -> None:
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model, self.n_heads, self.dh = d_model, n_heads, d_model // n_heads
        # bottom-up projections (from the image X)
        self.W_XQ = nn.Linear(d_model, d_model)
        self.W_XK = nn.Linear(d_model, d_model)
        self.W_XV = nn.Linear(d_model, d_model)
        # top-down FiLM projections (from the memory H, width d_mem_in); ZERO-init so the
        # gate (1 + W_H·H) starts at 1 ⇒ feedback off ⇒ plain self-attention over X at init.
        self.W_HQ = nn.Linear(d_mem_in, d_model)
        self.W_HK = nn.Linear(d_mem_in, d_model)
        self.W_HV = nn.Linear(d_mem_in, d_model)
        for m in (self.W_HQ, self.W_HK, self.W_HV):
            nn.init.zeros_(m.weight); nn.init.zeros_(m.bias)
        self.W_o = nn.Linear(d_model, d_model)
        self.norm_q = nn.LayerNorm(d_model)        # normalize Q,K after the Hadamard,
        self.norm_k = nn.LayerNorm(d_model)        # before the softmax broadcast
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def _heads(self, x):                            # (B,N,d) -> (B,H,N,dh)
        B, N, _ = x.shape
        return x.view(B, N, self.n_heads, self.dh).transpose(1, 2)

    def forward(self, X: torch.Tensor, H: torch.Tensor, residual: torch.Tensor,
                return_attn: bool = False):
        Q = self.W_XQ(X) * (1.0 + self.W_HQ(H))     # Q_X ⊙ (1 + Q_H)  — FiLM feedback gate
        K = self.W_XK(X) * (1.0 + self.W_HK(H))     # K_X ⊙ (1 + K_H)
        V = self.W_XV(X) * (1.0 + self.W_HV(H))     # V_X ⊙ (1 + V_H)
        Q = self.norm_q(Q); K = self.norm_k(K)      # normalize before the broadcast
        qh, kh, vh = self._heads(Q), self._heads(K), self._heads(V)
        scores = torch.matmul(qh, kh.transpose(-2, -1)) / (self.dh ** 0.5)
        aw = torch.softmax(scores, dim=-1)
        out = torch.matmul(aw, vh).transpose(1, 2).contiguous().view(X.shape)
        Z = residual + self.drop(self.W_o(out))
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, (aw if return_attn else None)


class DualStreamEncoder(nn.Module):
    """v11_part2 split structure with multiplicative-feedback self-attention. Same
    constructor / state / forward_step return as the cross-attention encoder."""

    def __init__(self, n_tokens: int, d_model: int = 128, d_mem: int = 128,
                 n_heads: int = 1, tx_layers: int = 1, n_lstm: int = 2, drop: float = 0.1) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if int(n_lstm) != 2:
            raise ValueError("dual-stream needs exactly n_lstm=2 (H1 sensory, H2 deep).")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.stream_dim = d_model                   # split readout: each head reads ONE stream

        d_mem_in = 2 * d_mem                         # top-down reads H = [H1 ‖ H2]
        # both streams: bottom-up = X, top-down = [H1‖H2], residual = X (separate weights)
        self.priority_block = _MultFeedbackBlock(d_model, n_heads, d_mem_in, drop)
        self.value_block = _MultFeedbackBlock(d_model, n_heads, d_mem_in, drop)
        self.sal_block = self.priority_block         # back-compat aliases
        self.td_block = self.value_block

        self.cell1 = nn.LSTMCell(d_model, d_mem)     # H1 ← X
        self.cell2 = nn.LSTMCell(d_model, d_mem)     # H2 ← Z_priority
        self.cells = nn.ModuleList([self.cell1, self.cell2])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H1, H2 = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]
        X = tokens
        Hcat = torch.cat([H1, H2], dim=-1)           # (B, N, 2·d_mem) — top-down memory

        # both streams: multiplicative self-attention over X gated by [H1‖H2], residual X
        Z_priority, aw_p = self.priority_block(X, Hcat, residual=X, return_attn=return_attn)
        Z_value, aw_v = self.value_block(X, Hcat, residual=X, return_attn=return_attn)

        h1, c1 = self.cell1(X.reshape(B * N, self.d_model),
                            (H1.reshape(B * N, self.d_mem), C1.reshape(B * N, self.d_mem)))
        h2, c2 = self.cell2(Z_priority.reshape(B * N, self.d_model),
                            (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_Hs = [h1.view(B, N, self.d_mem), h2.view(B, N, self.d_mem)]
        new_Cs = [c1.view(B, N, self.d_mem), c2.view(B, N, self.d_mem)]

        rec = [Z_priority, Z_value]                  # Z_priority → actor, Z_value → critic
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw_p, aw_v]
        return (new_Hs, new_Cs), rec
