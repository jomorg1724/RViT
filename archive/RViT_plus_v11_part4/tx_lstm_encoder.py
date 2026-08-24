"""
Encoder for RViT+ v11_part4: TWO PERFECTLY PARALLEL recurrent cross-attention
modules with NO cross-talk. Each module has its OWN memory, updated by its OWN
transformer output. The only tensor the two modules share is the input image X.

  μ — SALIENCE module:   Zμ = X  + attn(Q=X, K=V=Hμ) + FFN ;  Hμ ← LSTM_μ(Zμ)
      residual = X (a GROUNDED image stream). → feeds the ACTOR.

  Q — TOP-DOWN module:   ZQ = HQ + attn(Q=X, K=V=HQ) + FFN ;  HQ ← LSTM_Q(ZQ)
      residual = HQ (the v8-style gating-only bottleneck: the image only re-gates
      the module's own memory; no grounded image content). → feeds the CRITIC.

This CUTS the cross-talk that v11_part2 had: there, both streams read the shared
deep memory H2 (and H2 was written from the salience output Z_sal), so the
top-down stream depended on the salience stream. Here each module is a closed
loop — Zμ depends only on (X, Hμ); ZQ depends only on (X, HQ) — and each memory is
written by its OWN output (Hμ←Zμ, HQ←ZQ), so the two streams never read or write
each other's state. Single head each. Actor reads Zμ; critic reads ZQ (the split
readout from v11_part2). The recurrent State stays (Hs, Cs) with Hs = [Hμ, HQ], so
the PER trainer's state storage / burn-in / carry are unchanged. d_model == d_mem.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs), each a per-module list of (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _CrossAttnBlock(nn.Module):
    """Pre-norm cross-attention block. The QUERY source, the KEY/VALUE bank and the
    residual tensor are all supplied by the caller (the same block used across the
    v8/v9/v11 family). Returns the updated stream + (optionally) attention weights."""

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

    def forward(self, queries: torch.Tensor, kv_seq: torch.Tensor,
                residual: torch.Tensor, return_attn: bool = False):
        kv = self.norm_kv(kv_seq)                               # (B, n_kv, d)
        a, aw = self.attn(self.norm_q(queries), kv, kv,
                          need_weights=return_attn, average_attn_weights=False)
        Z = residual + self.drop(a)
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, aw                                            # aw: (B, heads, N, n_kv) or None


class DualStreamEncoder(nn.Module):
    """Two PERFECTLY PARALLEL recurrent cross-attention modules (no cross-talk).

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : transformer / token width (MUST equal d_mem).
    d_mem    : LSTM hidden width (= one module's readout width).
    n_heads  : attention heads per module (default 1).
    tx_layers: accepted for config parity; fixed at one block per module.
    n_lstm   : must be 2 (one memory per module: Hμ, HQ).
    drop     : dropout.

    forward_step returns (new_state, rec[, attn]) with rec = [Zμ, ZQ] (each
    (B, N, d_model)); attn = [aw_mu, aw_q], each (B, heads, N, N).
    """

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 1,
        tx_layers: int = 1,
        n_lstm: int = 2,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(
                f"d_model ({d_model}) must equal d_mem ({d_mem}): memory rows enter "
                f"the attention as keys/values and as residuals."
            )
        if int(n_lstm) != 2:
            raise ValueError(
                "v11_part4 needs exactly n_lstm=2 (one memory per parallel module: Hμ, HQ)."
            )
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.stream_dim = d_model                # each head reads ONE module's output

        # Two INDEPENDENT single-head cross-attention modules (separate weights).
        self.mu_block = _CrossAttnBlock(d_model, n_heads, drop)   # μ salience:  Q=X, KV=Hμ, res=X
        self.q_block = _CrossAttnBlock(d_model, n_heads, drop)    # Q top-down: Q=X, KV=HQ, res=HQ
        # Separate positional embeddings on each module's memory keys (no shared
        # learnable structure between the modules beyond consuming the same X).
        self.mu_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        self.q_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mu_pos_emb, std=0.02)
        nn.init.normal_(self.q_pos_emb, std=0.02)

        # Per-token LSTMs: each module's memory is written by its OWN output.
        self.cell_mu = nn.LSTMCell(d_model, d_mem)   # Hμ ← Zμ
        self.cell_q = nn.LSTMCell(d_model, d_mem)    # HQ ← ZQ
        self.cells = nn.ModuleList([self.cell_mu, self.cell_q])
        self.H0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)]
        )
        self.C0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(2)]
        )

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        """Consume ONE frame's patch tokens X. The μ module queries its own memory Hμ
        (residual=X) and the Q module queries its own memory HQ (residual=HQ); each
        memory is then updated by its OWN transformer output. The two modules never
        touch each other's state.

        Returns (new_state, rec[, attn]); rec = [Zμ, ZQ] (Zμ→actor, ZQ→critic).
        attn = [aw_mu, aw_q], each (B, heads, N, N).
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        Hmu, Hq = Hs[0], Hs[1]
        Cmu, Cq = Cs[0], Cs[1]
        X = tokens

        # μ SALIENCE module: image queries its OWN memory Hμ; raw image residual.
        Zmu, aw_mu = self.mu_block(X, Hmu + self.mu_pos_emb, residual=X, return_attn=return_attn)
        # Q TOP-DOWN module: image queries its OWN memory HQ; HQ residual (image gates only).
        Zq, aw_q = self.q_block(X, Hq + self.q_pos_emb, residual=Hq, return_attn=return_attn)

        # Each module's memory is written by its OWN output.
        hmu, cmu = self.cell_mu(
            Zmu.reshape(B * N, self.d_model),
            (Hmu.reshape(B * N, self.d_mem), Cmu.reshape(B * N, self.d_mem)),
        )
        hq, cq = self.cell_q(
            Zq.reshape(B * N, self.d_model),
            (Hq.reshape(B * N, self.d_mem), Cq.reshape(B * N, self.d_mem)),
        )
        new_Hs = [hmu.view(B, N, self.d_mem), hq.view(B, N, self.d_mem)]
        new_Cs = [cmu.view(B, N, self.d_mem), cq.view(B, N, self.d_mem)]

        rec = [Zmu, Zq]                          # Zμ → actor, ZQ → critic
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw_mu, aw_q]
        return (new_Hs, new_Cs), rec
