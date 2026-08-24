"""
Encoder for RViT+ v9: MEMORY-QUERY cross-attention + stacked per-token LSTMs.

v8 kept the queries on the visual tokens (Q = W_q·X) and put H1 in both the
key/value bank AND the residual. v9 inverts the direction of interrogation —
the user's design: **memory asks questions of the world**.

    Q = W_q · (H1_prev + pos)         # N queries from the carried MEMORY
    K = W_k · [X ++ H2_prev]          # 2N keys   : current image + deep memory
    V = W_v · [X ++ H2_prev]          # 2N values
    Z = H1_prev + softmax(QKᵀ/√d)·V   # skip path = H1 (unchanged from v8)
    Z = Z + FFN(Z)
    H1 = LSTM1(Z) ; H2 = LSTM2(H1)    # per-token, carried across frames

Each H1 memory slot (one per patch position) probes the current image and the
deeper memory H2 for what is relevant to it, and the retrieved content updates
the memory stream through the H1 residual. Top-down: the internal state drives
the queries; the image supplies evidence only as attended VALUES. Visual
information now has exactly ONE route into the network — it no longer even
shapes the queries (in v8, X formed the queries). H1 is no longer a key bank
(it was redundant there: query source, residual, and key all at once).

Attention weights are (B, heads, N, 2N) with keys ordered [X(0:N) ++ H2(N:2N)].
For tx_layers > 1 only the FIRST block uses memory queries + the H1 residual;
later blocks run standard stream-query attention over [stream ++ H2] (their
input is already attention-derived, so no raw-visual bypass re-opens).

Everything else matches v8/v5_part2: per-token LSTMs with learned initial
state, the State/forward_step contract, d_model == d_mem.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs) with Hs/Cs per-LSTM lists of (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class _CrossAttnBlock(nn.Module):
    """Pre-norm cross-attention block. The QUERY source, the KEY/VALUE bank and
    the residual tensor are all supplied by the caller — block 0 in v9 uses
    queries = carried H1 memory, keys/values = [X ++ H2], residual = H1."""

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


class TxLSTMEncoder(nn.Module):
    """Memory-query cross-attention block(s) + a stack of per-token LSTMs.

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : transformer / token width (MUST equal d_mem — memory rows enter
               the attention as queries and keys/values).
    d_mem    : LSTM hidden width (= recurrent-state width read by the decoders).
    n_heads  : attention heads (default 8).
    tx_layers: number of attention blocks (default 1 — a single encoder).
    n_lstm   : number of stacked LSTMs = number of recurrent states (default 2).
               H1 (first LSTM) supplies the queries + residual; the LATER
               memories (H2, …) join X in the key/value bank.
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
                f"d_model ({d_model}) must equal d_mem ({d_mem}): memory rows enter "
                f"the attention as queries and keys/values."
            )
        if n_lstm < 2:
            raise ValueError("v9 needs n_lstm >= 2 (H1 queries; H2+ join the key/value bank)")
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads, self.tx_layers, self.n_lstm = n_heads, max(1, int(tx_layers)), int(n_lstm)
        # keys/values per block-0 attention: X plus every memory AFTER H1.
        self.n_kv = (1 + (self.n_lstm - 1)) * n_tokens          # = 2N for n_lstm=2

        self.blocks = nn.ModuleList(
            [_CrossAttnBlock(d_model, n_heads, drop) for _ in range(self.tx_layers)]
        )
        # Source tags for the key/value memories (H2, …) + a shared positional
        # embedding (row i ↔ patch position i) used on memory queries AND keys.
        self.mem_tag = nn.Parameter(torch.zeros(self.n_lstm - 1, 1, d_model))
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

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous() for c in self.C0]
        return Hs, Cs

    def forward_step(self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False):
        """Consume ONE frame's patch tokens: the carried H1 memory queries
        [X ++ H2], the result (on the H1 residual stream) drives the LSTMs.

        Returns (new_state, rec[, attn_per_layer]); rec = [H1, …, H_{n_lstm}]
        (decoders read the LAST, H2). attn_per_layer[0]: (B, heads, N, 2N),
        keys ordered [X(0:N) ++ H2(N:2N)].
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens

        # Key/value bank: current image + the LATER memories (H2, …), tagged.
        kv_mems = [Hs[k] + self.mem_pos_emb + self.mem_tag[k - 1]
                   for k in range(1, self.n_lstm)]
        kv_seq = torch.cat([tokens] + kv_mems, dim=1)           # (B, 2N, d_model)

        # Queries: the carried H1 memory, position-tagged. Residual: raw H1.
        q = Hs[0] + self.mem_pos_emb

        attn_per_layer: List[Optional[torch.Tensor]] = []
        stream = None
        for bi, blk in enumerate(self.blocks):
            if bi == 0:
                stream, aw = blk(q, kv_seq, residual=Hs[0], return_attn=return_attn)
            else:
                # later blocks: standard stream-query attention over [stream ++ H2…];
                # the stream is already attention-derived (no raw-visual bypass).
                kv2 = torch.cat([stream] + kv_mems, dim=1)
                stream, aw = blk(stream, kv2, residual=stream, return_attn=return_attn)
            attn_per_layer.append(aw)
        Z = stream                                              # (B, N, d_model)

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
