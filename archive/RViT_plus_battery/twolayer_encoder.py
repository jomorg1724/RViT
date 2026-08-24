"""
Two-transformer codebook encoder — adds a cross-slot SPREADING layer (T1) before the
codebook readout (T2), so the cue (shown at one spatial slot) can propagate to all memory
slots before the response is read out.

Per frame (X = patch tokens; H1, H2 = the two recurrent states; codebook = static):

  T1  (spread — 1 head, residual = X):
        Q  = W_q(X)
        K  = W_kX(X) + W_kH(H1)          # keys/values combine the image with memory H1
        V  = W_vX(X) + W_vH(H1)          #   (additive projections)
        Z1 = X + W_o(softmax(QKᵀ/√d)·V) + FFN
        H1 = LSTM1(Z1)
  T2  (codebook readout — 2 heads, NO residual; = the v12 codebook block fed by Z1/H2):
        Q  = W_q(Z1) ;  K = W_k(H2) ;  V = codebook
        Z2 = W_o(softmax(QKᵀ/√d)·codebook) + FFN
        H2 = LSTM2(Z1 + H1)             # H1 here is the freshly-updated H1
  actor, critic read Z2 (the codebook selection)

T1 mixes across spatial tokens (every query can attend to the cue's slot), so the cue
spreads into Z1 → H1 at all slots; T2 then reads the codebook (the SC-like response
signal) using the spread representation. Heads: T1 single, T2 two.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .codebook_encoder import CodebookV12Block
except ImportError:  # pragma: no cover
    from codebook_encoder import CodebookV12Block  # type: ignore[no-redef]

State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class T1SpreadBlock(nn.Module):
    """Self-attention over the patch tokens with K/V combining X and the memory H1
    (additive), residual = X. Mixes information across spatial slots."""

    def __init__(self, d_model: int, d_mem: int, n_heads: int, drop: float) -> None:
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model, self.n_heads, self.dh = d_model, n_heads, d_model // n_heads
        self.scale = self.dh ** -0.5
        self.W_q = nn.Linear(d_model, d_model)
        self.W_kX = nn.Linear(d_model, d_model); self.W_kH = nn.Linear(d_mem, d_model)
        self.W_vX = nn.Linear(d_model, d_model); self.W_vH = nn.Linear(d_mem, d_model)
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

    def forward(self, X, H1, return_attn=False, attn_clamp=None):
        Q = self.W_q(X)
        K = self.W_kX(X) + self.W_kH(H1)
        V = self.W_vX(X) + self.W_vH(H1)
        Q = self.norm_q(Q); K = self.norm_k(K)
        qh, kh, vh = self._heads(Q), self._heads(K), self._heads(V)
        aw = torch.softmax(torch.matmul(qh, kh.transpose(-2, -1)) * self.scale, dim=-1)
        if attn_clamp:
            aw = aw.clone()
            for j, val in attn_clamp.items():
                aw[..., j] = float(val)
            aw = aw / aw.sum(dim=-1, keepdim=True).clamp_min(1e-8)
        out = torch.matmul(aw, vh).transpose(1, 2).contiguous().view(X.shape)
        Z1 = X + self.drop(self.W_o(out))                 # skip = X
        Z1 = Z1 + self.ffn(self.norm_ff(Z1))
        return Z1, (aw if return_attn else None)


class TwoLayerCodebookEncoder(nn.Module):
    """T1 (spread) → LSTM1 → T2 (codebook readout) → LSTM2. Two recurrent states + a
    static codebook. Same forward_step contract as the other encoders."""

    def __init__(self, n_tokens, d_model=128, d_mem=128, t1_heads=1, t2_heads=2,
                 tx_layers=1, n_lstm=2, drop=0.1, readout="Z2") -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        if readout not in ("Z2", "Z1", "H1", "H2"):
            raise ValueError("readout must be Z2 (default), Z1, H1, or H2")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_lstm = 2
        self.n_heads = t2_heads          # reported head count = the codebook layer's
        self.readout = readout
        self.stream_dim = d_model

        self.t1 = T1SpreadBlock(d_model, d_mem, n_heads=t1_heads, drop=drop)
        # T2 = the v12 codebook block, fed by Z1 (queries) and H2 (keys):
        self.t2 = CodebookV12Block(d_model, t2_heads, d_mem=d_mem, n_tokens=n_tokens, drop=drop)
        self.cell1 = nn.LSTMCell(d_model, d_mem)          # H1 ← LSTM1(Z1)
        self.cell2 = nn.LSTMCell(d_model, d_mem)          # H2 ← LSTM2(Z1 + H1)
        self.cells = nn.ModuleList([self.cell1, self.cell2])
        self.H0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])
        self.C0 = nn.ParameterList([nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)])

    def init_states(self, batch_size, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens, prev_state, return_attn=False, attn_clamp=None):
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        X = tokens
        H1p, H2p = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]

        # T1: spread across slots (cue propagation), residual X
        Z1, aw1 = self.t1(X, H1p, return_attn=return_attn)
        h1, c1 = self.cell1(Z1.reshape(B * N, self.d_model),
                            (H1p.reshape(B * N, self.d_mem), C1.reshape(B * N, self.d_mem)))
        h1 = h1.view(B, N, self.d_mem); c1 = c1.view(B, N, self.d_mem)

        # T2: codebook readout, queries from Z1, keys from H2 (prev), values = codebook.
        # attn_clamp targets the codebook selection (the SC-like response signal).
        Z2, aw2 = self.t2(Z1, H2p, return_attn=return_attn, attn_clamp=attn_clamp)
        # update H2 from Z1 + the freshly-computed H1
        h2, c2 = self.cell2((Z1 + h1).reshape(B * N, self.d_model),
                            (H2p.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        h2 = h2.view(B, N, self.d_mem); c2 = c2.view(B, N, self.d_mem)

        new_Hs, new_Cs = [h1, h2], [c1, c2]
        if self.readout == "Z1":
            rec = [Z1]
        elif self.readout == "H1":
            rec = [h1]
        elif self.readout == "H2":
            rec = [h2]
        else:
            rec = [Z2]                                    # default: codebook selection
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw2, aw1]      # [codebook attn, spread attn]
        return (new_Hs, new_Cs), rec
