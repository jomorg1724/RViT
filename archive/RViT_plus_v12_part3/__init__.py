"""RViT+ v12_part3 — an EMA codebook written by a GATED IMAGE-CONTENT STREAM.

The codebook C_base is a buffer (no gradient) consolidated by a slow VQ-VAE EMA; what
is written into it comes from a dedicated transformer + LSTM ("stream 3") whose VALUES
are the image, gated so the write shuts off when no longer needed:

  (1) WRITE STREAM — image content → gated codebook write:
        Q3 = W_q3·C_base;  K3 = W_k3·H3;  V3 = W_v3·X
        Z3 = W_o3·softmax(Q3 K3ᵀ/√d) V3 + FFN3;  H3 ← LSTM3(Z3)
        gate = σ(W_g·H3);  write = gate ⊙ H3;  C_t = C_base + write
  (2) READOUT — soft attention over the written codebook C_t (the v12 mechanism):
        Q = W_q·X;  K = W_k·H2;  V = C_t;  Z = W_o·(softmax(QKᵀ/√d) @ C_t) + FFN
        H2 ← LSTM2(X + Z);  Z → actor AND critic
  (3) CONSOLIDATION — EMA toward C_t: C_base ← (1−r)·C_base + r·mean(C_t) = C_base + r·mean(gate⊙H3).
      Target is C_t (not the write alone), so C_base keeps its scale and accumulates the
      gated write. The gate is the throttle (closing it → C_t→C_base); a small warmed-in
      penalty on mean(gate) is the energy cost. C_base inits at ZERO. Perception is
      gradient-grounded through the write (Z→C_t→write→H3→LSTM3→W_v3·X) — what avoids the
      always-WAIT collapse.

Trained from reward with PAC (MPO+BC) + distributional QR-DQN + PER + the gate cost + the
codebook EMA — no reconstruction, no predictive coding.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import VQAttnEncoder
from .model import RViTPlusV12Part3Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "VQAttnEncoder",
    "PatchEmbed",
    "RViTPlusV12Part3Model",
]
