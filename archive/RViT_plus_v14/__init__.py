"""RViT+ v14 — TWO coupled recurrent modules trained CONCURRENTLY by two objectives,
with cross-detachments that firewall the gradients.

  MODULE 1 (self-supervised): Z1 = T1(Q=X, K=Z2.detach, V=H1, skip=X) → H1 = LSTM1(Z1);
    JEPA latent predictive coding on H1 (predictor(proj(H1_t)) ≈ proj(H1_{t+k}), VICReg
    anti-collapse, NO pixels) → a quantified surprise. Trains ONLY Module 1.
  MODULE 2 (RL): Z2 = T2(Q=H1.detach, K=H2, V=H2, skip=H1.detach) → H2 = LSTM2(Z2);
    actor + critic read H2. Trains ONLY Module 2 (+ heads).

Z2 detached in T1 → SS loss never trains Module 2; H1 detached in T2 → RL loss never
trains Module 1. They share state forward (the H1→T2→Z2→T1→H1 cycle) but never share
gradients. Concurrent: one optimizer, loss = L_RL + ss_coef·L_SS, on the same batch.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import VQAttnEncoder
from .model import RViTPlusV14Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "VQAttnEncoder",
    "PatchEmbed",
    "RViTPlusV14Model",
]
