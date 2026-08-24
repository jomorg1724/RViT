"""
V6 — Multi-Layer Feedback Transformer for the ViZDoom deathmatch arena.

Hierarchical cross-attention feedback encoder (per-layer token memories +
game-state tokens, bias-injectable attention) trained with PAC (MPO+BC) +
distributional QR-DQN + prioritized segment replay + EMA target network.
See V6_DESIGN.md.
"""
from .encoder import MultiLayerFeedbackEncoder, StateTokens, prep_attn_bias
from .decoder import ActorDecoder, CriticDecoder
from .model import V6ArenaModel
from .patch_embed import PatchEmbed
from .trainer import (
    PACConfig, SegmentBatch, SegmentCollector, SegmentReplayBuffer,
    compute_nstep_distributional_targets, ema_update, pac_update, train,
)

__all__ = [
    "MultiLayerFeedbackEncoder", "StateTokens", "prep_attn_bias",
    "ActorDecoder", "CriticDecoder", "V6ArenaModel", "PatchEmbed",
    "PACConfig", "SegmentBatch", "SegmentCollector", "SegmentReplayBuffer",
    "compute_nstep_distributional_targets", "ema_update", "pac_update", "train",
]
