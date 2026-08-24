"""RViT+ v12_part2 — an ADAPTIVE codebook with an energetic maintenance cost.

Develops v12 (a static learnable value codebook read by soft attention) by letting
the agent SPEND ENERGY to deform the codebook toward the current environment, while
the codebook always DECAYS back to the static learned table:

  (1) ENERGY MODULATION — a transformer EDITS the codebook (codebook = residual):
        C_in = C_base + D_{t-1};  Q = C_in;  K = V = [X ‖ H2]
        energy = SAblock(C_in,[X,H2]) − C_in;  D_t = decay·D_{t-1} + energy;  C_t = C_base + D_t
      The maintenance cost mean‖D_t‖² is added to the RL loss (energy_coef), so
      deforming the codebook costs reward.
  (2) READOUT — soft attention over the ADAPTED codebook (the v12 mechanism):
        Q = W_q·X;  K = W_k·H2;  V = C_t;  Z = W_o·(softmax(QKᵀ/√d) @ C_t) + FFN
        H2 ← LSTM(X + Z);  Z → actor AND critic

Trained purely from reward with PAC (MPO+BC) + distributional QR-DQN + PER, plus the
added energetic-cost term — no reconstruction, no predictive coding, no JEPA.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import VQAttnEncoder
from .model import RViTPlusV12Part2Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "VQAttnEncoder",
    "PatchEmbed",
    "RViTPlusV12Part2Model",
]
