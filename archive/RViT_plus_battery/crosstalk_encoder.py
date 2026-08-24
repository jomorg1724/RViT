"""
Cross-talk dual-stream encoder (the v11_part2 architecture that worked on the T=29
value-cue task), ported to the FiLM directory and matched to the other 7-step models
(4 patches, pixel front-end, shared harness). Cross-ATTENTION (not FiLM), SPLIT readout,
with the coupling that was shown to be necessary for learning.

Two single-head cross-attention streams per frame, both querying with the patch tokens X:

  μ pathway (→ ACTOR, image-grounded):   Q = X ,  K = V = [H1 ‖ H2] ,  residual = X
        Z_μ = X + attn(X → [H1, H2]) + FFN
  q pathway (→ CRITIC, memory-grounded): Q = X ,  K = V = H2 ,         residual = H2
        Z_q = H2 + attn(X → H2) + FFN

Memory (two per-token LSTMs):  H1 = LSTM1(X)  (sensory) ;  H2 = LSTM2(Z_μ)  (deep).

The CROSS-TALK lives in H2: the μ (actor) pathway WRITES it (via Z_μ) and READS it back
(inside [H1‖H2]); the q (critic) pathway READS the same H2. Split readout: actor reads Z_μ,
critic reads Z_q. (Naming: μ = policy/actor stream, q = value/critic stream — NOT
"salience/top-down".) Prior results: coupling is required (private memories → never learns)
and the image-grounded μ stream must drive the policy (swap → never learns).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _CrossAttnBlock(nn.Module):
    """Pre-norm cross-attention block; query source, key/value bank, and residual are all
    supplied by the caller."""

    def __init__(self, d_model: int, n_heads: int, drop: float) -> None:
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=drop, batch_first=True)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_kv = nn.LayerNorm(d_model)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def forward(self, queries, kv_seq, residual, return_attn=False):
        kv = self.norm_kv(kv_seq)
        a, aw = self.attn(self.norm_q(queries), kv, kv,
                          need_weights=return_attn, average_attn_weights=False)
        Z = residual + self.drop(a)
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, aw


class CrossTalkEncoder(nn.Module):
    """Parallel μ + q cross-attention streams + two per-token LSTMs, split readout,
    coupled through the shared deep memory H2. Same forward_step contract as the other
    encoders, except rec has TWO entries [Z_μ, Z_q] (the model routes Z_μ→actor, Z_q→critic)."""

    def __init__(self, n_tokens, d_model=128, d_mem=128, n_heads=1, tx_layers=1,
                 n_lstm=2, drop=0.1, readout="split") -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(f"d_model ({d_model}) must equal d_mem ({d_mem}).")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.readout = "split"
        self.stream_dim = d_model                 # each head reads ONE stream

        self.mu_block = _CrossAttnBlock(d_model, n_heads, drop)   # μ: Q=X, KV=[H1‖H2], res=X → actor
        self.q_block = _CrossAttnBlock(d_model, n_heads, drop)    # q: Q=X, KV=H2,      res=H2 → critic
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)
        self.mu_tag = nn.Parameter(torch.zeros(2, 1, d_model))   # tag H1 vs H2 in the μ K/V bank
        nn.init.normal_(self.mu_tag, std=0.02)

        self.cell1 = nn.LSTMCell(d_model, d_mem)   # H1 ← X
        self.cell2 = nn.LSTMCell(d_model, d_mem)   # H2 ← Z_μ
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
        H1, H2 = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]
        X = tokens

        # μ (actor): image queries BOTH memories [H1‖H2] (tagged + positional); raw-image residual.
        mu_kv = torch.cat(
            [H1 + self.mem_pos_emb + self.mu_tag[0], H2 + self.mem_pos_emb + self.mu_tag[1]], dim=1
        )
        Z_mu, aw_mu = self.mu_block(X, mu_kv, residual=X, return_attn=return_attn)
        # q (critic): image queries deep memory H2; H2 residual (image only re-gates the readout).
        Z_q, aw_q = self.q_block(X, H2 + self.mem_pos_emb, residual=H2, return_attn=return_attn)

        # memory updates: H1 from the raw image; H2 from the μ (actor) output  ← the cross-talk
        h1, c1 = self.cell1(X.reshape(B * N, self.d_model),
                            (H1.reshape(B * N, self.d_mem), C1.reshape(B * N, self.d_mem)))
        h2, c2 = self.cell2(Z_mu.reshape(B * N, self.d_model),
                            (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)))
        new_Hs = [h1.view(B, N, self.d_mem), h2.view(B, N, self.d_mem)]
        new_Cs = [c1.view(B, N, self.d_mem), c2.view(B, N, self.d_mem)]

        rec = [Z_mu, Z_q]                          # Z_μ → actor, Z_q → critic (split)
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw_mu, aw_q]
        return (new_Hs, new_Cs), rec
