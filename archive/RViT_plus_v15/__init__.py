"""RViT+ v15 — v12's gradient-learned codebook + a VQ-VAE-style ENERGY term that
REDUCES TO v12.

Keeps the v12 mechanism that worked (a gradient-learned codebook C, pulled by softmax
attention from Q=W_q·X / K=W_k·H2) and adds an energy on top:

  energy = T_E(Q=C, K=H2, V=H2, skip=C)        # codebook reads the current memory (zero-init ⇒ ≈0)
  Z      = C + energy                          # the energized codebook
  Z_read = W_o·(softmax(W_q·X·(W_k·H2)ᵀ) @ Z) + FFN ;  H2 ← LSTM(X+Z_read) ;  Z_read → heads

Three-way loss (VQ-VAE): (1) RL task on Z_read; (2) energy_coef·mean‖energy‖²=‖Z−C‖²
(commitment / the energy cost); (3) EMA C ← C + r·mean(energy) (codebook toward Z,
consolidation). When energy→0, Z=C and the readout is byte-for-byte v12 — the floor.
The energy is fast adaptation, the EMA is slow consolidation, the commitment is the cost.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import VQAttnEncoder
from .model import RViTPlusV15Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "VQAttnEncoder",
    "PatchEmbed",
    "RViTPlusV15Model",
]
