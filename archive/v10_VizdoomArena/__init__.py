"""
V10 — Multi-Layer Feedback Transformer for the ViZDoom deathmatch arena,
with the v8 H1-RESIDUAL encoder (vision reaches memory only through attention).

Hierarchical cross-attention feedback encoder (per-layer token memories +
game-state tokens, bias-injectable attention) trained with PAC (MPO+BC) +
distributional QR-DQN + prioritized segment replay + EMA target network.
See V10_DESIGN.md.
"""
from .encoder import MultiLayerFeedbackEncoder, StateTokens, prep_attn_bias
from .decoder import ActorDecoder, CriticDecoder
from .model import V10ArenaModel
from .patch_embed import PatchEmbed
from .trainer import (
    PACConfig, SegmentBatch, SegmentCollector, SegmentReplayBuffer,
    compute_nstep_distributional_targets, ema_update, pac_update, train,
)

__all__ = [
    "MultiLayerFeedbackEncoder", "StateTokens", "prep_attn_bias",
    "ActorDecoder", "CriticDecoder", "V10ArenaModel", "PatchEmbed",
    "PACConfig", "SegmentBatch", "SegmentCollector", "SegmentReplayBuffer",
    "compute_nstep_distributional_targets", "ema_update", "pac_update", "train",
]
