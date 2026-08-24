"""
Single-stream recurrent attention encoder — FiLM-gated queries/keys, memory-sourced
values, concat-residual output.

Per frame (inputs X = current patch tokens, H1 / H2 = the two memories from t-1):

    Q = W_XQ(X) ⊙ (1 + W_HQ(H1))         # queries: FiLM-gated by the feedback state H1
    K = W_XK(X) ⊙ (1 + W_HK(H1))         #   (W_HQ, W_HK ZERO-init ⇒ feedback OFF at init)
    Q, K ← LayerNorm
    V = W_V(H2)                           # values come from the DEEP memory H2
    AV = softmax(QKᵀ/√d) · V              # attention pattern from X·H1, content from H2
    Z = W_reduce( concat[X, AV] )         # X is the residual — CONCAT (not add) then project
    Z = Z + FFN(LN(Z))

    H1 = LSTM1(Z)                         # BOTH LSTMs are updated from Z
    H2 = LSTM2(Z)
    actor, critic  read  Z                # Z drives both memories and both heads

So: H1 is short-term feedback that gain-modulates the query/key matching (FiLM); H2 is the
deep memory that supplies the attended content (values); X enters as the residual via a
learned concat-projection; and the integrated output Z updates both memories and feeds the
policy/value heads. The `readout` knob can instead expose H1 or H2 for ablation.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn

State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class FiLMBlock(nn.Module):
    """FiLM-gated (by H1) query/key attention whose values come from H2; the residual X
    is concatenated with the attention output and reduced by a learned projection."""

    def __init__(self, d_model: int, n_heads: int, d_mem: int, drop: float) -> None:
        super().__init__()
        assert d_model % n_heads == 0, "d_model must divide n_heads"
        self.d_model, self.n_heads, self.dh = d_model, n_heads, d_model // n_heads
        # queries / keys: bottom-up from X, FiLM-gated by the feedback memory H1
        self.W_XQ = nn.Linear(d_model, d_model)
        self.W_XK = nn.Linear(d_model, d_model)
        self.W_HQ = nn.Linear(d_mem, d_model)
        self.W_HK = nn.Linear(d_mem, d_model)
        for m in (self.W_HQ, self.W_HK):                 # zero-init ⇒ feedback off at init
            nn.init.zeros_(m.weight); nn.init.zeros_(m.bias)
        # values: from the deep memory H2
        self.W_V = nn.Linear(d_mem, d_model)
        # output: concat[X, AV] (2·d_model) → d_model
        self.W_reduce = nn.Linear(2 * d_model, d_model)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_k = nn.LayerNorm(d_model)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def _heads(self, x: torch.Tensor) -> torch.Tensor:   # (B,N,d) -> (B,H,N,dh)
        B, N, _ = x.shape
        return x.view(B, N, self.n_heads, self.dh).transpose(1, 2)

    def forward(
        self,
        X: torch.Tensor,
        H1: torch.Tensor,
        H2: torch.Tensor,
        return_attn: bool = False,
        attn_clamp: Optional[Dict[int, float]] = None,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        Q = self.W_XQ(X) * (1.0 + self.W_HQ(H1))         # FiLM gate on queries (by H1)
        K = self.W_XK(X) * (1.0 + self.W_HK(H1))         # FiLM gate on keys   (by H1)
        Q = self.norm_q(Q); K = self.norm_k(K)
        V = self.W_V(H2)                                 # values from the deep memory H2
        qh, kh, vh = self._heads(Q), self._heads(K), self._heads(V)
        scores = torch.matmul(qh, kh.transpose(-2, -1)) / (self.dh ** 0.5)
        aw = torch.softmax(scores, dim=-1)               # (B, n_heads, N, N)
        if attn_clamp:
            aw = aw.clone()
            for j, val in attn_clamp.items():
                aw[..., j] = float(val)
            aw = aw / aw.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        av = torch.matmul(aw, vh).transpose(1, 2).contiguous().view(X.shape)   # AV (B,N,d)
        Z = self.W_reduce(torch.cat([X, av], dim=-1))    # concat residual X + AV → reduce
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, (aw if return_attn else None)


class SingleStreamFiLMEncoder(nn.Module):
    """One FiLM block + two per-token LSTMs (H1 feedback-gates Q/K, H2 supplies values),
    both updated from Z. Same constructor / state / forward_step contract as before so the
    PER + PAC + QR-DQN harness is reused unchanged."""

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 1,
        tx_layers: int = 1,        # accepted for parity; one FiLM block
        n_lstm: int = 2,           # exactly two: H1 (feedback) and H2 (values)
        drop: float = 0.1,
        readout: str = "Z",        # heads read: Z (default) | H1 | H2
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if readout not in ("Z", "H1", "H2"):
            raise ValueError("readout must be 'Z', 'H1', or 'H2'")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.readout = readout
        self.stream_dim = d_model                         # Z (and H*) are all d_model wide

        self.block = FiLMBlock(d_model, n_heads, d_mem=d_mem, drop=drop)
        self.cell1 = nn.LSTMCell(d_model, d_mem)          # H1 ← LSTM1(Z)  (feedback)
        self.cell2 = nn.LSTMCell(d_model, d_mem)          # H2 ← LSTM2(Z)  (values)
        self.cells = nn.ModuleList([self.cell1, self.cell2])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(
        self,
        tokens: torch.Tensor,
        prev_state: State,
        return_attn: bool = False,
        attn_clamp: Optional[Dict[int, float]] = None,
    ):
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        X = tokens
        H1_prev, H2_prev = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]
        # H1 gates Q/K (FiLM); H2 supplies the values; X is the concat-residual.
        Z, aw = self.block(X, H1_prev, H2_prev, return_attn=return_attn, attn_clamp=attn_clamp)

        # both LSTMs are updated from Z
        h1, c1 = self.cell1(Z.reshape(B * N, self.d_model),
                            (H1_prev.reshape(B * N, self.d_mem), C1.reshape(B * N, self.d_mem)))
        h2, c2 = self.cell2(Z.reshape(B * N, self.d_model),
                            (H2_prev.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_Hs = [h1.view(B, N, self.d_mem), h2.view(B, N, self.d_mem)]
        new_Cs = [c1.view(B, N, self.d_mem), c2.view(B, N, self.d_mem)]

        if self.readout == "H1":
            rec = [new_Hs[0]]
        elif self.readout == "H2":
            rec = [new_Hs[1]]
        else:
            rec = [Z]                                     # default: heads read Z
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw]
        return (new_Hs, new_Cs), rec
