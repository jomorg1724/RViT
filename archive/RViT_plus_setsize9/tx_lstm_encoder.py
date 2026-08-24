"""
Encoder for RViT+ setsize9: PARALLEL dual-stream cross-attention (Tμ SALIENCE +
TQ TOP-DOWN), SINGLE-head each, with a SPLIT readout — the salience output Z_sal
goes to the ACTOR, the top-down output Z_td goes to the CRITIC.

Two single-head cross-attention streams run in parallel each frame, BOTH querying
with the current patch tokens X:

  Tμ — SALIENCE (bottom-up):   Q = X ,  K = V = [H1 ‖ H2] ,  residual = X
      Z_sal = X + attn(X → [H1,H2]) + FFN
      The raw image is preserved on the residual (a GROUNDED visual stream); the
      attention now reads BOTH the fresh sensory memory H1 AND the deep memory H2
      (setsize9's change vs v11: H2 added to the salience K/V, each source tagged).
      → feeds the ACTOR.

  TQ — TOP-DOWN (memory-grounded):  Q = X ,  K = V = H2 ,  residual = H2
      Z_td = H2 + attn(X → H2) + FFN
      The v8-style bottleneck: the image can only RE-GATE the deep-memory readout.
      → feeds the CRITIC.

Memory updates (per-token LSTMCells, hidden carried across frames; unchanged):
      H1 = LSTM1(X)        # bottom-up sensory trace, written from the RAW image
      H2 = LSTM2(Z_sal)    # deep trace, written from the salience output

The recurrent State stays (Hs, Cs) with Hs = [H1, H2], so the PER trainer's state
storage / burn-in / carry are unchanged. d_model must == d_mem. n_heads defaults to
1 (single head per transformer).
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
    """Parallel Tμ-salience + TQ-top-down cross-attention streams + two per-token
    LSTMs. setsize9: Tμ reads K=V=[H1‖H2]; TQ reads K=V=H2; single head each; the
    actor reads Z_sal and the critic reads Z_td (split done in the model).

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : transformer / token width (MUST equal d_mem).
    d_mem    : LSTM hidden width (= one stream's readout width).
    n_heads  : attention heads per stream (default 1).
    tx_layers: accepted for config parity; fixed at one block per stream.
    n_lstm   : must be 2 (H1 = sensory memory, H2 = deep memory).
    drop     : dropout.

    forward_step returns (new_state, rec[, attn]) with rec = [Z_sal, Z_td] (each
    (B, N, d_model)); attn = [aw_sal, aw_td] with aw_sal (B,heads,N,2N), aw_td (B,heads,N,N).
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
                "setsize9 dual-stream needs exactly n_lstm=2 (H1 = sensory memory, H2 = deep memory)."
            )
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_heads = n_heads
        self.n_lstm = 2
        self.stream_dim = d_model                # each head reads ONE stream (d_model)

        # Two independent single-head cross-attention streams (separate weights).
        self.sal_block = _CrossAttnBlock(d_model, n_heads, drop)   # Tμ: Q=X, KV=[H1‖H2], res=X
        self.td_block = _CrossAttnBlock(d_model, n_heads, drop)    # TQ: Q=X, KV=H2,      res=H2
        # Shared positional embedding added to the memory KEYS (queries already carry
        # PatchEmbed's positional embedding).
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)
        # Source tags for the salience K/V bank so attention can tell H1 from H2.
        self.sal_tag = nn.Parameter(torch.zeros(2, 1, d_model))
        nn.init.normal_(self.sal_tag, std=0.02)

        # Per-token LSTMs: H1 ingests the raw image X; H2 ingests the salience output.
        self.cell1 = nn.LSTMCell(d_model, d_mem)   # H1 ← X
        self.cell2 = nn.LSTMCell(d_model, d_mem)   # H2 ← Z_sal
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
        """Consume ONE frame's patch tokens X. Tμ queries [H1‖H2] (residual=X);
        TQ queries H2 (residual=H2). Then H1←X and H2←Z_sal.

        Returns (new_state, rec[, attn]); rec = [Z_sal, Z_td] (Z_sal→actor, Z_td→critic).
        attn = [aw_sal, aw_td] with aw_sal (B,heads,N,2N), aw_td (B,heads,N,N).
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        H1, H2 = Hs[0], Hs[1]
        C1, C2 = Cs[0], Cs[1]
        X = tokens

        # Tμ SALIENCE: image queries BOTH memories [H1 ‖ H2] (each tagged); raw image residual.
        sal_kv = torch.cat(
            [H1 + self.mem_pos_emb + self.sal_tag[0], H2 + self.mem_pos_emb + self.sal_tag[1]], dim=1
        )                                                        # (B, 2N, d_model)
        Z_sal, aw_sal = self.sal_block(X, sal_kv, residual=X, return_attn=return_attn)
        # TQ TOP-DOWN: image queries deep memory H2; H2 residual (image gates only).
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

        rec = [Z_sal, Z_td]                      # Z_sal → actor (Tμ), Z_td → critic (TQ)
        if return_attn:
            return (new_Hs, new_Cs), rec, [aw_sal, aw_td]
        return (new_Hs, new_Cs), rec
