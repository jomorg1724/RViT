"""RViT+ v11_part5 — PARALLEL DUAL-STREAM attention with a SPLIT readout, single head
each. Tμ SALIENCE (Q=X, K=V=[H1‖H2], residual=X) feeds the ACTOR; TQ TOP-DOWN (Q=X,
K=V=H2, residual=H2 — v8-style gating-only) feeds the CRITIC. H1=LSTM1(X),
H2=LSTM2(Z_sal). v11_part5 changes vs v11: H2 added to the salience K/V, split
actor/critic readout, single attention head. Same env + PER/PAC/QR-DQN trainer.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import DualStreamEncoder
from .model import RViTPlusV11Part5Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "DualStreamEncoder",
    "PatchEmbed",
    "RViTPlusV11Part5Model",
]
