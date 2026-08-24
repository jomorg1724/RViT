"""
Encoder for RViT+ v8_part2: v8's CROSS-ATTENTION-over-memory block + stacked
per-token LSTMs, with TWO deliberate changes on top of v5_part2:

  1. **H1-residual** (from v8): the attention skip path carries the previous
     frame's H1 memory, not the visual input X.
  2. **Memory-only K/V** (new): patch tokens are QUERIES ONLY — they never
     appear in the keys/values. Visual information can reach the recurrent
     state ONLY through query-side gating (re-aiming the softmax over the
     mnemonic codebook), not through a visual value stream.

    Q = W_q · X                       # N queries  (the patch tokens)
    K = W_k · [H1 ++ H2]              # n_lstm·N keys   (NO patch keys)
    V = W_v · [H1 ++ H2]              # n_lstm·N values (NO patch values)
    Z = softmax(QKᵀ/√d)·V  + H1_prev  + FFN

With the residual carried by the PREVIOUS frame's H1 (raw — no tag/pos-emb),
the only route by which current-frame visual information can move downstream
is the query-driven re-weighting of the memory keys: to see, the model must
attend — and what it "reads" is always mnemonic content, never raw pixels.
(exp6 on v8 showed this gating channel was already the dominant percept.)

For tx_layers > 1 only the FIRST block uses the H1-residual; later blocks'
inputs are already attention-derived, so a standard residual on them
re-introduces no raw-visual bypass.

Everything else is v5_part2 verbatim: memory K/V tokens tagged by a learned
source embedding + shared memory positional embedding (row i ↔ patch position
i); Z drives the 2 stacked per-token LSTMs; the State/forward_step contract is
unchanged, so model.py / ppo.py are untouched. Requires d_model == d_mem.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs) with Hs/Cs per-LSTM lists of (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _CrossAttnBlock(nn.Module):
    """Pre-norm transformer block whose attention is CROSS-attention: queries are
    the patch tokens X; keys/values are MEMORY ONLY (no patch in K/V). The
    residual tensor is supplied by the CALLER (v8_part2: prev-frame H1 for the
    first block) — there is no unconditional residual on X, and no visual
    content in the value stream at all."""

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

    def forward(self, X: torch.Tensor, mem_kv: torch.Tensor,
                residual: torch.Tensor, return_attn: bool = False):
        # K/V source = MEMORY TOKENS ONLY — no patch keys/values.
        kv = self.norm_kv(mem_kv)                               # (B, n_lstm·N, d)
        a, aw = self.attn(self.norm_q(X), kv, kv,
                          need_weights=return_attn, average_attn_weights=False)
        # H1-residual: skip path carries MEMORY; visual content enters only via
        # query-side gating of the softmax over mnemonic keys.
        Z = residual + self.drop(a)
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, aw                                            # aw: (B, heads, N, n_lstm·N) or None


class TxLSTMEncoder(nn.Module):
    """Cross-attention-over-memory block(s) + a stack of per-token LSTMs.

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : transformer / token width (MUST equal d_mem — memory is concatenated
               into the token stream as keys/values).
    d_mem    : LSTM hidden width (= recurrent-state width read by the decoders).
    n_heads  : attention heads (the spec's 8 heads).
    tx_layers: number of cross-attention blocks (default 1 — a single encoder).
    n_lstm   : number of stacked LSTMs = number of recurrent states (default 2).
    drop     : dropout.
    """

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 8,
        tx_layers: int = 1,
        n_lstm: int = 2,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(
                f"d_model ({d_model}) must equal d_mem ({d_mem}): memory is concatenated "
                f"into the d_model token stream as keys/values."
            )
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads, self.tx_layers, self.n_lstm = n_heads, max(1, int(tx_layers)), max(1, int(n_lstm))

        self.blocks = nn.ModuleList(
            [_CrossAttnBlock(d_model, n_heads, drop) for _ in range(self.tx_layers)]
        )
        # One learned source tag per memory (lets attention tell H1 from H2) +
        # a shared memory positional embedding (row i ↔ patch position i).
        self.mem_tag = nn.Parameter(torch.zeros(self.n_lstm, 1, d_model))
        nn.init.normal_(self.mem_tag, std=0.02)
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)

        # Stacked per-token LSTMs: cell0 ingests the attention output (d_model);
        # later cells ingest the previous LSTM's hidden state (d_mem).
        self.cells = nn.ModuleList(
            [nn.LSTMCell(d_model if i == 0 else d_mem, d_mem) for i in range(self.n_lstm)]
        )
        self.H0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_lstm)]
        )
        self.C0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_lstm)]
        )

    @property
    def n_keys(self) -> int:
        """Keys per cross-attention block = memory tokens only."""
        return self.n_lstm * self.n_tokens

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        """Consume ONE frame's patch tokens; cross-attend Q=X over MEMORY K/V only,
        then advance every LSTM's per-token memory.

        Returns (new_state, rec[, attn_per_layer]); rec = [H1, …, H_{n_lstm}]
        (decoders read the LAST, H2). attn_per_layer[i]: (B, heads, N, n_lstm·N).
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens

        # Memory tokens = PREVIOUS-frame LSTM states, tagged by source + position.
        mem_kv = torch.cat(
            [Hs[k] + self.mem_pos_emb + self.mem_tag[k] for k in range(self.n_lstm)], dim=1
        )                                                       # (B, n_lstm·N, d_model)

        X = tokens
        attn_per_layer: List[Optional[torch.Tensor]] = []
        for bi, blk in enumerate(self.blocks):
            # H1-residual on block 0; later blocks keep standard residual on
            # attention-derived input (no raw-visual bypass).
            res = Hs[0] if bi == 0 else X
            X, aw = blk(X, mem_kv, residual=res, return_attn=return_attn)
            attn_per_layer.append(aw)
        Z = X                                                   # (B, N, d_model)

        inp = Z
        for li, cell in enumerate(self.cells):
            h, c = cell(
                inp.reshape(B * N, inp.shape[-1]),
                (Hs[li].reshape(B * N, self.d_mem), Cs[li].reshape(B * N, self.d_mem)),
            )
            Hs[li] = h.view(B, N, self.d_mem)
            Cs[li] = c.view(B, N, self.d_mem)
            inp = Hs[li]
        rec = [Hs[li] for li in range(self.n_lstm)]
        if return_attn:
            return (Hs, Cs), rec, attn_per_layer
        return (Hs, Cs), rec
