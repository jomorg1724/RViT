"""
Memory-as-tokens encoder for RViT+ v5.

This is the one place v5 departs from v4. Where v4's `FeedbackBlock` lets the
recurrent memory steer attention via FiLM modulation (memory → gain/bias on
Q/K/V) over the N patch tokens only, v5 instead treats the memory **as tokens**:
each layer is a plain `nn.TransformerEncoderLayer` that self-attends over the
concatenation

    [ patch tokens (N) ++ H₁ rows (N) ++ H₂ rows (N) ]   =  3·N tokens

(no FiLM). Every memory token from BOTH recurrent states is sent in as feedback,
so for n_layers=2 the encoder transformer sees (1 + 2)·N = 3·N tokens — the
"N_tokens × 3" of the v5 spec. Each token group is tagged by a learned source
embedding {patch, H₁, H₂}; memory rows additionally get a positional embedding
so row i aligns with patch position i.

After attention, the **patch-token outputs** (the first N positions) drive a
per-layer shared `LSTMCell` that updates that layer's memory. Layer 2 consumes
layer 1's patch-token output AND the just-updated H₁, so the recurrence is
hierarchical exactly as in v4. Two layers → two recurrent states H₁, H₂, each
(B, N, d_mem), which the actor/critic decoders read unchanged.

Direct adaptation of Jonathan's `FBT_MemTok` from PalladioWikiMCP
(`habit_formation/sequence_models/mt_models.py`). Requires d_model == d_mem
(memory rows are concatenated into the same d_model token stream).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs) where Hs/Cs are per-layer lists of (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class MemTokEncoder(nn.Module):
    """Stack of ``n_layers`` memory-as-tokens transformer layers with persistent
    per-layer LSTM memory.

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : token width (matches PatchEmbed output). MUST equal d_mem.
    d_mem    : per-layer recurrent memory width (= d_model).
    n_heads  : attention heads per transformer layer (must divide d_model).
    n_layers : number of recurrent layers / memory states (default 2 — the
               "two memory states" of the v5 spec). Each layer attends over
               patch tokens + ALL n_layers memories → (1 + n_layers)·N tokens.
    n_FR     : inner iterations per frame (default 1). >1 re-reads the patch
               tokens while the memories settle.
    drop     : dropout inside the transformer layers.
    """

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 4,
        n_layers: int = 2,
        n_FR: int = 1,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(
                f"MemTokEncoder requires d_model == d_mem (memory rows are "
                f"concatenated into the d_model token stream); got "
                f"d_model={d_model}, d_mem={d_mem}."
            )
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads})")
        self.n_tokens = n_tokens
        self.d_model = self.d_mem = d_model
        self.n_layers = n_layers
        self.n_FR = max(1, int(n_FR))

        # One pre-norm transformer encoder layer per recurrent layer.
        self.enc = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=d_model, nhead=n_heads, dim_feedforward=4 * d_model,
                dropout=drop, batch_first=True, activation="gelu", norm_first=True,
            )
            for _ in range(n_layers)
        ])
        # Per-layer shared LSTMCell: input = patch-token output Z (d_model),
        # hidden/cell = that layer's memory row (d_mem).
        self.cells = nn.ModuleList([nn.LSTMCell(d_model, d_mem) for _ in range(n_layers)])

        # Source tags: index 0 = patch token, index k+1 = memory state k.
        self.src_emb = nn.Embedding(1 + n_layers, d_model)
        nn.init.normal_(self.src_emb.weight, std=0.02)
        # Positional embedding for memory rows (row i ↔ patch position i), shared
        # across the two memory states. Patch tokens carry their own pos-emb from
        # PatchEmbed.
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)

        # Learned initial memory (hidden + cell) per layer.
        self.H0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(n_layers)]
        )
        self.C0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(n_layers)]
        )

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        """Learned initial recurrent state, expanded to the batch."""
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
              for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
              for c in self.C0]
        return Hs, Cs

    @staticmethod
    def _layer_with_attn(layer: nn.TransformerEncoderLayer, seq: torch.Tensor):
        """Replicate a pre-norm (norm_first=True) TransformerEncoderLayer forward
        while capturing the self-attention weights (B, n_heads, S, S). Analysis
        only — uses the layer's own submodules so it exactly matches the trained
        forward (in eval mode the dropouts are identity)."""
        normed = layer.norm1(seq)
        attn_out, attn_w = layer.self_attn(
            normed, normed, normed, need_weights=True, average_attn_weights=False,
        )
        x = seq + layer.dropout1(attn_out)
        ff = layer.linear2(layer.dropout(layer.activation(layer.linear1(layer.norm2(x)))))
        x = x + layer.dropout2(ff)
        return x, attn_w

    def forward_step(
        self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False
    ):
        """Consume ONE frame's patch tokens; update every layer's memory by
        treating all memory as tokens in the attention.

        tokens     : (B, n_tokens, d_model) from PatchEmbed (carries patch pos-emb).
        prev_state : (Hs, Cs) from init_states or a previous forward_step.

        Returns (new_state, recurrent_states):
            new_state        : updated (Hs, Cs).
            recurrent_states : [H₁, …, H_L] — the per-layer hidden states the
                               actor/critic decoders consume (each (B, N, d_mem)).
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens
        sf = self.src_emb.weight[0]                                  # patch source tag (d_model,)
        mtag = [self.src_emb.weight[k + 1] for k in range(self.n_layers)]  # memory tags
        mpe = self.mem_pos_emb                                       # (1, N, d_model)

        attn_per_layer: List[Optional[torch.Tensor]] = [None] * self.n_layers
        for _ in range(self.n_FR):
            X = tokens
            for li in range(self.n_layers):
                # ALL memories as feedback tokens; earlier layers' memories are
                # already this-frame-updated, later layers' are previous-frame.
                mem_toks = [Hs[k] + mpe + mtag[k] for k in range(self.n_layers)]
                seq = torch.cat([X + sf] + mem_toks, dim=1)         # (B, (1+L)·N, d_model)
                if return_attn:
                    out, attn_per_layer[li] = self._layer_with_attn(self.enc[li], seq)
                else:
                    out = self.enc[li](seq)
                Z = out[:, :N]                                       # patch-token outputs
                h, c = self.cells[li](
                    Z.reshape(B * N, self.d_model),
                    (Hs[li].reshape(B * N, self.d_mem), Cs[li].reshape(B * N, self.d_mem)),
                )
                Hs[li] = h.view(B, N, self.d_mem)
                Cs[li] = c.view(B, N, self.d_mem)
                X = Z                                                # next layer consumes this layer's output
        rec = [Hs[li] for li in range(self.n_layers)]
        if return_attn:
            return (Hs, Cs), rec, attn_per_layer                    # attn[li]: (B, heads, 3N, 3N)
        return (Hs, Cs), rec
