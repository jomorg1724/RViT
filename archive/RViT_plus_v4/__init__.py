"""RViT+ v4 — conv-free, RL-only recurrent attention model.

A patch embedding (reshape + Linear, NO convolution) feeds a 2-layer Feedback
Transformer (Palladio RecBlock: FiLM-modulated recurrent attention with a
shared LSTMCell memory). The two per-layer recurrent states are concatenated
and read by 2-layer Transformer actor/critic decoders with a CLS-token readout.
Trained purely from reward with PAC (MPO+BC) + distributional QR-DQN + PER —
no reconstruction, no predictive coding, no JEPA.

See RVIT_PLUS_V4_DESIGN.md for the architectural rationale.
"""
from .decoder import ActorDecoder, CriticDecoder
from .feedback_transformer import FeedbackBlock, FeedbackTransformerEncoder
from .model import RViTPlusV4Model
from .patch_embed import PatchEmbed

__all__ = [
    "ActorDecoder",
    "CriticDecoder",
    "FeedbackBlock",
    "FeedbackTransformerEncoder",
    "PatchEmbed",
    "RViTPlusV4Model",
]
