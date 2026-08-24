"""RViT+ v8_part3 — v8's H1-residual cross-attention encoder + a PREDICTIVE-COMPARATOR
write gate that makes the per-frame-rewritten memory store explicit.

Built on v8 (everything kept verbatim except):
  1. COMPARATOR WRITE GATE — a tiny forward model predicts the attention output Z
     from the carried deep memory H2; the detached prediction-error 'surprise'
     drives a learnable gate g that scales the LSTM2 input by (1+g), so the evolving
     codebook H2 is rewritten harder exactly where the current frame surprises the
     stored prediction. Self-supervised (reward-independent) predictor loss;
     g≈0 at init ⇒ exactly v8. The evolving store is leveraged, never frozen.
  2. LEARNABLE-GAIN H1 RESIDUAL — the block-0 skip amplitude becomes tunable.
  3. READOUT — the 1D-conv heads read H1 ‖ H2 (both LSTM states), not just H2.

Trained purely from reward with PAC (MPO+BC) + distributional QR-DQN + PER, plus the
comparator's self-supervised next-Z loss and a small always-wait-harbor penalty.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import ComparatorEncoder
from .model import RViTPlusV8Part3Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "ComparatorEncoder",
    "PatchEmbed",
    "RViTPlusV8Part3Model",
]
