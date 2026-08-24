"""RViT+ v11 — PARALLEL DUAL-STREAM attention. A SALIENCE stream (Q=X, K=V=H1,
residual=X — grounded image + bottom-up change signal) and a TOP-DOWN stream (Q=X,
K=V=H2, residual=H2 — v8-style gating-only bottleneck) run in parallel; H1=LSTM1(X),
H2=LSTM2(Z_sal); the actor/critic read the two TRANSFORMER OUTPUTS [Z_sal ++ Z_td]
(not the LSTM states). Same change-detection env + PER/PAC/QR-DQN trainer as v8.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import DualStreamEncoder
from .model import RViTPlusV11BroadcastModel
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "DualStreamEncoder",
    "PatchEmbed",
    "RViTPlusV11BroadcastModel",
]
