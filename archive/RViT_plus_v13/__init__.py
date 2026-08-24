"""RViT+ v13 — a FROZEN self-supervised predictive-coding encoder repurposed for RL
by an energy-modulation stream. Two phases:

  PHASE 1 (pretrain_pc.py): self-supervised predictive coding. T1 (Q=X, K=H1, V=H2,
    skip=X) → Z1 → LSTM1 → H1 → LSTM2 → H2; JEPA loss trains H2_t to predict H1_{t+1}
    (VICReg anti-collapse) → a quantified surprise. Then PART A is frozen.
  PHASE 2 (train_rl.py --pc-checkpoint): freeze PART A; add LSTM3 (H3←LSTM3(H2)) + T2
    (Q=H2, K=H3, V=H3, skip=H2) → Z_energy, injected as T1's V source; the modulated
    Z1 drives actor+critic. Only the energy stream (PART B) + heads train (PAC+QR-DQN+PER).

The test: can a frozen self-supervised recurrent transformer+LSTM be repurposed for a
different (RL) task purely by energy-modulating its dynamical system?
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import VQAttnEncoder
from .model import RViTPlusV13Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "VQAttnEncoder",
    "PatchEmbed",
    "RViTPlusV13Model",
]
