"""
Feedback Transformer encoder for RViT+ v4.

This is the heart of the v4 variant. It is a direct adaptation of Jonathan's
``FeedbackTransformer`` / ``RecBlock`` from the PalladioWikiMCP project
(``habit_formation/sequence_models/feedback_model.py``) to the visual
change-detection setting, with the discrete bin-embedding replaced by the
conv-free PatchEmbed (see patch_embed.py).

One ``FeedbackBlock`` (≈ Palladio ``RecBlock``) per layer keeps a recurrent
memory matrix ``(B, n_tokens, d_mem)`` with hidden ``H`` and cell ``C``. Per
environment step (one frame), per layer:

    • project the patch tokens X → Qx, Kx, Vx   (the bottom-up sensory drive)
    • project the memory H       → Qh, Kh, Vh   (the top-down feedback)
    • FiLM-modulate Q = g(Qh)·Qx + b(Qh)  (same for K, V) so the carried memory
      STEERS this frame's attention — this is the "feedback" in feedback
      transformer (multiplicative gain + additive bias, à la Larkum apical
      modulation / Reynolds–Heeger gain)
    • multi-head self-attention over the n_tokens tokens + residual + FFN → Z
    • a SHARED ``LSTMCell`` updates every memory row in parallel: (H,C) ← cell(Z)

Two layers are stacked; layer 2 consumes layer 1's output Z. After a frame,
the encoder exposes the TWO recurrent hidden states H₁, H₂ (each
``(B, n_tokens, d_mem)``) — these are what the actor/critic decoders read
(decoder.py). The memory persists across frames, giving the model its temporal
recurrence over the episode; on the first frame the learned initial memory H0
already modulates attention (top-down prior).

No convolution, no predictive coding, no JEPA — only this recurrent attention
body feeding the RL heads.
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs) where Hs/Cs are per-layer lists of (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


class FeedbackBlock(nn.Module):
    """One feedback-transformer layer with FiLM-modulated recurrent memory.

    Faithful to Palladio ``RecBlock``: sensory projections Qx/Kx/Vx (from the
    token input), memory projections Qh/Kh/Vh (from the carried hidden state),
    FiLM gates fq/fk/fv, an output projection, an FFN, two LayerNorms, and a
    shared LSTMCell that updates every token's memory row.

    Args
    ----
    d_model : token / attention width (Palladio ``dm``).
    d_mem   : memory hidden+cell width (Palladio ``dmem``).
    n_heads : attention heads (must divide d_model).
    drop    : dropout on attention-out and FFN.
    """

    def __init__(self, d_model: int, d_mem: int, n_heads: int, drop: float = 0.1) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads})")
        self.d_model, self.d_mem, self.n_heads = d_model, d_mem, n_heads
        self.d_head = d_model // n_heads

        # Sensory (bottom-up) projections from the patch tokens.
        self.qx = nn.Linear(d_model, d_model)
        self.kx = nn.Linear(d_model, d_model)
        self.vx = nn.Linear(d_model, d_model)
        # Feedback (top-down) projections from the recurrent memory hidden state.
        self.qh = nn.Linear(d_mem, d_model)
        self.kh = nn.Linear(d_mem, d_model)
        self.vh = nn.Linear(d_mem, d_model)
        # FiLM: each produces (gain, bias) of width d_model from the memory proj.
        self.fq = nn.Linear(d_model, 2 * d_model)
        self.fk = nn.Linear(d_model, 2 * d_model)
        self.fv = nn.Linear(d_model, 2 * d_model)

        self.out = nn.Linear(d_model, d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.n1, self.n2 = nn.LayerNorm(d_model), nn.LayerNorm(d_model)
        self.drop = nn.Dropout(drop)
        self.cell = nn.LSTMCell(d_model, d_mem)            # shared across memory rows

    @staticmethod
    def _film(xp: torch.Tensor, hp: torch.Tensor, film: nn.Linear) -> torch.Tensor:
        """FiLM-modulate sensory projection xp by memory projection hp:
        (1 + gain)·xp + bias, with (gain, bias) = film(hp).

        The gain is CENTERED AT 1 (the `+1`). `film` is a near-zero-init Linear,
        so g≈0 at init; without the offset the multiplicative gate starts CLOSED
        (Q≈b, the sensory drive gated out), which makes the attention logits tiny
        and collapses attention to a uniform global average-pool — observed
        empirically (perplexity ≈99.8/100, mean gain≈0) and never recovered in
        training. Centering at 1 means the gate starts OPEN (Q≈proj(X), an
        ordinary self-attention) and memory MODULATES it, so spatial attention
        can emerge. NOT attention supervision — just a sane init for the gate."""
        g, b = film(hp).chunk(2, dim=-1)
        return (1.0 + g) * xp + b

    def _attn(self, Q: torch.Tensor, K: torch.Tensor, V: torch.Tensor, return_attn: bool = False):
        """Standard scaled-dot-product multi-head self-attention. (B, nt, d_model).
        With return_attn, also returns the (B, heads, nt, nt) attention weights."""
        B, nt, _ = Q.shape
        q = Q.view(B, nt, self.n_heads, self.d_head).transpose(1, 2)
        k = K.view(B, nt, self.n_heads, self.d_head).transpose(1, 2)
        v = V.view(B, nt, self.n_heads, self.d_head).transpose(1, 2)
        attn_w = torch.softmax(q @ k.transpose(-1, -2) / math.sqrt(self.d_head), dim=-1)  # (B,heads,nt,nt)
        a = (attn_w @ v).transpose(1, 2).reshape(B, nt, self.d_model)
        return (a, attn_w) if return_attn else a

    def forward(
        self, X: torch.Tensor, Hm: torch.Tensor, Cm: torch.Tensor, return_attn: bool = False
    ):
        """X (B, nt, d_model) sensory tokens; Hm/Cm (B, nt, d_mem) carried memory.
        Returns (Z, H_new, C_new); with return_attn, a 4th element = (B,heads,nt,nt)
        attention weights (analysis only — adds no parameters)."""
        xn = self.n1(X)
        Q = self._film(self.qx(xn), self.qh(Hm), self.fq)
        K = self._film(self.kx(xn), self.kh(Hm), self.fk)
        V = self._film(self.vx(xn), self.vh(Hm), self.fv)
        if return_attn:
            attended, attn_w = self._attn(Q, K, V, return_attn=True)
        else:
            attended = self._attn(Q, K, V)
        Z = X + self.drop(self.out(attended))              # attention + residual
        Z = Z + self.ffn(self.n2(Z))                       # FFN + residual
        B, nt, _ = Z.shape
        h, c = self.cell(
            Z.reshape(B * nt, self.d_model),
            (Hm.reshape(B * nt, self.d_mem), Cm.reshape(B * nt, self.d_mem)),
        )
        Hn, Cn = h.view(B, nt, self.d_mem), c.view(B, nt, self.d_mem)
        return (Z, Hn, Cn, attn_w) if return_attn else (Z, Hn, Cn)


class FeedbackTransformerEncoder(nn.Module):
    """A stack of ``n_layers`` FeedbackBlocks with persistent per-layer memory.

    The model's recurrence lives here: ``init_states`` produces the learned
    initial memory; ``forward_step`` consumes one frame's patch tokens, updates
    every layer's memory, and returns BOTH the new state and the list of
    recurrent hidden states [H₁, …, H_L] that the decoders read.

    Args
    ----
    n_tokens : number of patch tokens (e.g. 100 for a 10×10 grid).
    d_model  : token width (matches PatchEmbed output).
    d_mem    : per-layer recurrent memory width.
    n_heads  : attention heads per block.
    n_layers : number of feedback layers (default 2 — the "2-layer feedback
               transformer" of the v4 spec).
    n_FR     : inner feedback iterations per frame (default 1 = one pass, the
               Palladio behavior). With n_FR>1 the stack re-reads the same
               frame's tokens while the memory settles.
    drop     : dropout inside each block.
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
        self.n_tokens = n_tokens
        self.d_model, self.d_mem = d_model, d_mem
        self.n_layers, self.n_FR = n_layers, max(1, int(n_FR))
        self.blocks = nn.ModuleList(
            [FeedbackBlock(d_model, d_mem, n_heads, drop) for _ in range(n_layers)]
        )
        # Learned initial memory (hidden + cell) per layer, broadcast over batch.
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

    def forward_step(
        self, tokens: torch.Tensor, prev_state: State, return_attn: bool = False
    ):
        """Consume ONE frame's patch tokens; update every layer's memory.

        tokens     : (B, n_tokens, d_model) from PatchEmbed.
        prev_state : (Hs, Cs) from init_states or a previous forward_step.

        Returns (new_state, recurrent_states):
            new_state        : updated (Hs, Cs).
            recurrent_states : [H₁, …, H_L] — the per-layer hidden states the
                               actor/critic decoders consume (each
                               (B, n_tokens, d_mem)).
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        attn_per_layer: List[Optional[torch.Tensor]] = [None] * self.n_layers
        for _ in range(self.n_FR):
            X = tokens
            for li, blk in enumerate(self.blocks):
                if return_attn:
                    Z, Hn, Cn, aw = blk(X, Hs[li], Cs[li], return_attn=True)
                    attn_per_layer[li] = aw                # last inner iteration kept
                else:
                    Z, Hn, Cn = blk(X, Hs[li], Cs[li])
                Hs[li], Cs[li] = Hn, Cn
                X = Z
        rec = [Hs[li] for li in range(self.n_layers)]
        if return_attn:
            return (Hs, Cs), rec, attn_per_layer
        return (Hs, Cs), rec
