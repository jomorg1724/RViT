"""RViT+ v11_part4 — TWO PERFECTLY PARALLEL recurrent cross-attention modules (no
cross-talk) with a SPLIT readout, single head each. μ SALIENCE (Q=X, K=V=Hμ,
residual=X; Hμ←LSTM_μ(Zμ)) feeds the ACTOR; Q TOP-DOWN (Q=X, K=V=HQ, residual=HQ;
HQ←LSTM_Q(ZQ)) feeds the CRITIC. v11_part4 = v11_part2 with the cross-talk cut: each
module reads/writes ONLY its own memory, updated by its own output; the modules
share only the input X. Same env + PER/PAC/QR-DQN trainer.
"""
from .decoder import ActorDecoder, CriticDecoder
from .tx_lstm_encoder import DualStreamEncoder
from .model import RViTPlusV11Part4Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "DualStreamEncoder",
    "PatchEmbed",
    "RViTPlusV11Part4Model",
]
