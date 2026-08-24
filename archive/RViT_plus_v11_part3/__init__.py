"""RViT+ v11_part3 — PARALLEL DUAL-STREAM attention with a SPLIT readout, single head
each. v11_part3 is v11_part2 with the readout destinations SWAPPED: TQ TOP-DOWN (Q=X,
K=V=H2, residual=H2 — v8-style gating-only) feeds the ACTOR; Tμ SALIENCE (Q=X,
K=V=[H1‖H2], residual=X) feeds the CRITIC (v11_part2 had Tμ→actor, TQ→critic).
H1=LSTM1(X), H2=LSTM2(Z_sal). Same env + PER/PAC/QR-DQN trainer.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import DualStreamEncoder
from .model import RViTPlusV11Part3Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "DualStreamEncoder",
    "PatchEmbed",
    "RViTPlusV11Part3Model",
]
