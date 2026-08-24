"""RViT+ v5 — conv-free, RL-only, MEMORY-AS-TOKENS recurrent attention model.

Identical to v4 except the encoder. A patch embedding (reshape + MLP, NO
convolution) feeds a 2-layer memory-as-tokens transformer: instead of v4's FiLM
modulation, each layer self-attends over [patch tokens ++ H₁ ++ H₂] = 3·N tokens
(all memory sent in as feedback tokens, tagged by a learned source embedding),
and a per-layer LSTMCell updates that layer's memory from the patch-token
outputs. The two recurrent states are read by 2-layer Transformer actor/critic
decoders with a CLS-token readout. Trained purely from reward with PAC (MPO+BC)
+ distributional QR-DQN + PER — no reconstruction, no predictive coding, no JEPA.

See RVIT_PLUS_V5_DESIGN.md for the architectural rationale.
"""
from .decoder import ActorDecoder, CriticDecoder
from .memtok_encoder import MemTokEncoder
from .model import RViTPlusV5Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "MemTokEncoder",
    "PatchEmbed",
    "RViTPlusV5Model",
]
