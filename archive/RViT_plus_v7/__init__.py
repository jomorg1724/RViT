"""RViT+ v7 — conv-free, RL-only recurrent attention model.

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
from .tx_lstm_encoder import TxLSTMEncoder
from .model import RViTPlusV7Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "TxLSTMEncoder",
    "PatchEmbed",
    "RViTPlusV7Model",
]
