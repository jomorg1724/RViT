"""RViT+ v8 — v5_part2 with the H1-RESIDUAL encoder (visual info flows ONLY through attention values; the cross-attn skip path carries prev-frame H1 memory, not X).

A re-architecture of v5 along two axes (everything else unchanged):
  1. ENCODER — a SINGLE plain transformer encoder layer (8 heads) over the patch
     tokens, followed by TWO stacked per-token LSTMs that hold all temporal
     memory (H1 = LSTM1 hidden, H2 = LSTM2 hidden). Attention is now purely
     feedforward/spatial; recurrence lives entirely in the LSTMs.
  2. DECODERS — radically reduced: tiny 3-layer FF heads that mean-pool the top
     recurrent state H2 over the N tokens and decode that (B, d_mem) vector
     (no CLS, no action-as-input encoding).

Trained purely from reward with PAC (MPO+BC) + distributional QR-DQN + PER —
no reconstruction, no predictive coding, no JEPA.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import VQAttnEncoder
from .model import RViTPlusV12Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "VQAttnEncoder",
    "PatchEmbed",
    "RViTPlusV12Model",
]
