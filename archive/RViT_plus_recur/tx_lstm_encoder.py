"""
Encoder for RViT+ v11: PARALLEL dual-stream cross-attention (SALIENCE + TOP-DOWN)
+ two per-token LSTMs, with the actor/critic reading the two TRANSFORMER OUTPUTS
(not the LSTM hidden states).

Two cross-attention streams run in parallel on each frame. BOTH query with the
current patch tokens X (the visual input), but they read different memories and
keep different residuals:

  SALIENCE (bottom-up):        Q = X ,  K = V = H1_prev ,  residual = X
      Z_sal = X + attn(X → H1) + FFN
      The raw image is preserved on the residual — a GROUNDED visual stream — and
      the attention asks "what in my recent sensory memory H1 is relevant to what
      I see now": a salience / change comparison of the current frame against the
      recent past.

  TOP-DOWN (memory-grounded):  Q = X ,  K = V = H2_prev ,  residual = H2_prev
      Z_td = H2_prev + attn(X → H2) + FFN
      The residual is the DEEP memory H2 (the v8-style bottleneck: the current
      image cannot add CONTENT on the residual, it can only RE-GATE the H2
      readout). The attention asks "given my integrated expectation H2, what does
      the current image select."

Memory updates (per-token LSTMCells, hidden carried across frames):
      H1 = LSTM1(X)        # bottom-up sensory trace, written from the RAW image
      H2 = LSTM2(Z_sal)    # deep trace, written from the SALIENCE output

Readout:
      the heads read [Z_sal ++ Z_td] (the two transformer outputs concatenated on
      the FEATURE axis, → 2·d_model channels), NOT H2. (v8/v9 read the top LSTM
      state H2.)

Design intent: the salience stream provides a grounded image pathway (the fallback
the strict v8_part2 lacked) AND a bottom-up change signal, while the top-down
stream is the pure query-gated memory readout validated in v8. Image content
reaches the deep memory H2 only through salience, so the two streams interact via
memory across frames. The recurrent State stays (Hs, Cs) with Hs = [H1, H2], so the
PER trainer's state storage / burn-in / carry are unchanged. d_model must == d_mem.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs), each a per-LSTM list of (B, n_tokens, d_mem).
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
    """Parallel salience + top-down cross-attention streams + two per-token LSTMs.

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : transformer / token width (MUST equal d_mem — memory rows enter the
               attention as keys/values and as residuals).
    d_mem    : LSTM hidden width (= one stream's readout width).
    n_heads  : attention heads per stream (default 8).
    tx_layers: accepted for config parity; v11 is fixed at one block per stream.
    n_lstm   : must be 2 (H1 = salience/sensory memory, H2 = deep memory).
    drop     : dropout.

    forward_step returns (new_state, rec[, attn]) with rec = [Z_sal, Z_td]
    (each (B, N, d_model)); attn = [aw_sal, aw_td] (each (B, heads, N, N)).
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
                f"the attention as keys/values and as residuals."
            )
        if int(n_lstm) != 2:
            raise ValueError(
                "v11 dual-stream needs exactly n_lstm=2 (H1 = salience memory, H2 = deep memory)."
            )
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.stream_dim = 2 * d_model            # width of [Z_sal ++ Z_td] the heads read

        # Two independent cross-attention streams (separate weights).
        self.sal_block = _CrossAttnBlock(d_model, n_heads, drop)   # bottom-up: Q=X, KV=H1, res=X
        self.td_block = _CrossAttnBlock(d_model, n_heads, drop)    # top-down:  Q=X, KV=H2, res=H2
        # Shared positional embedding added to the memory KEYS so an X-query at
        # position i can match the memory key at position i (queries already carry
        # PatchEmbed's positional embedding).
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)

        # Per-token LSTMs: H1 ingests the raw image X; H2 ingests the salience output.
        self.cell1 = nn.LSTMCell(d_model, d_mem)   # H1 ← X
        self.cell2 = nn.LSTMCell(d_model, d_mem)   # H2 ← Z_sal
        # `.cells` alias so generic code (tests / grad checks) can iterate both LSTMs.
        self.cells = nn.ModuleList([self.cell1, self.cell2])
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
        """Consume ONE frame's patch tokens X. Both streams query with X; salience
        reads H1 (residual = X), top-down reads H2 (residual = H2). H1 is then
        updated from X and H2 from the salience output.

        Returns (new_state, rec[, attn]); rec = [Z_sal, Z_td] (the heads' input).
        attn = [aw_sal, aw_td], each (B, heads, N, N).
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H1, H2 = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]
        X = tokens

        # SALIENCE (bottom-up): image queries recent sensory memory H1; raw image residual.
        Z_sal, aw_sal = self.sal_block(X, H1 + self.mem_pos_emb, residual=X, return_attn=return_attn)
        # TOP-DOWN (memory-grounded): image queries deep memory H2; H2 residual (image gates only).
        Z_td, aw_td = self.td_block(X, H2 + self.mem_pos_emb, residual=H2, return_attn=return_attn)

        # Memory updates: H1 from the RAW image, H2 from the SALIENCE output.
        h1, c1 = self.cell1(
            X.reshape(B * N, self.d_model),
            (H1.reshape(B * N, self.d_mem), C1.reshape(B * N, self.d_mem)),
        )
        h2, c2 = self.cell2(
            Z_sal.reshape(B * N, self.d_model),
            (H2.reshape(B * N, self.d_mem), C2.reshape(B * N, self.d_mem)),
        )
        new_Hs = [h1.view(B, N, self.d_mem), h2.view(B, N, self.d_mem)]
        new_Cs = [c1.view(B, N, self.d_mem), c2.view(B, N, self.d_mem)]

        rec = [Z_sal, Z_td]                      # the heads read the transformer outputs
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw_sal, aw_td]
        return (new_Hs, new_Cs), rec
