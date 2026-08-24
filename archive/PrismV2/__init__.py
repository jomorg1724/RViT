"""
PRISM v2 — hierarchical predictive coding with slow/fast memory and multi-head saliency.

See ../Prism/docs/PRISM_V2_PROPOSAL.md for the full design doc.

Per-step computation:
    x_t  →  V1Stem → V_1   →  V2Stem → V_2
                                │
                                ▼
    HierarchicalFiLM(M_fast, M_slow) modulates V_1
    PixelDecoder(M_fast)       → x̂  → S_V1_pix    (anchor)
    MultiHeadDecoder_V1(M_fast) → V̂_1 per head    → E_V1, S_V1_per_head
    MultiHeadDecoder_V2(M_slow) → V̂_2 per head    → E_V2, S_V2_per_head
    M_fast = FastConvGRU(M_fast_prev, P_1, E_V1, S_V1)
    M_slow = SlowConvGRU(M_slow_prev, V_2, E_V2, S_V2,
                         pool(E_V1) [cross-level Rao-Ballard error])
    Inner WM loops on each memory.
    Hierarchical readout → actor / critic.

Auxiliary loss (per-level VFE only — bitter-lesson compliant):
    L_PC = α_pix·‖x − x̂(M_fast_prev)‖² + α_auto·‖x − x̂(M_fast)‖²
         + α_V1_feat·L_V1_feat
         + α_V2_feat·L_V2_feat + α_V2_auto·L_V2_feat_auto
"""

from .stem import V1Stem, V2Stem
from .film import HierarchicalFiLM
from .decoder import (
    MultiHeadFeatureDecoder,
    PixelDecoder,
    multi_head_saliency,
    pixel_saliency_map,
)
from .memory import (
    CrossLevelErrorPool,
    FastConvGRU,
    InnerWMLoop,
    SlowConvGRU,
    pool_cross_level_error,
)
from .readout import (
    ActorHead,
    CriticHead,
    HeadCompressionBackbone,
    HierarchicalDecisionReadout,
    SaliencyCoarseGridPerHead,
    saliency_coarse_grid_per_head,
    saliency_weighted_pool_per_head,
)
from .losses import multi_head_pc_loss, predictive_coding_loss, slowness_loss
from .model import EpisodeOutput, PrismV2Model, StepOutput

__all__ = [
    "V1Stem", "V2Stem",
    "HierarchicalFiLM",
    "MultiHeadFeatureDecoder", "PixelDecoder", "multi_head_saliency", "pixel_saliency_map",
    "FastConvGRU", "SlowConvGRU", "InnerWMLoop", "CrossLevelErrorPool", "pool_cross_level_error",
    "HierarchicalDecisionReadout", "ActorHead", "CriticHead", "HeadCompressionBackbone",
    "SaliencyCoarseGridPerHead",
    "saliency_weighted_pool_per_head", "saliency_coarse_grid_per_head",
    "multi_head_pc_loss", "predictive_coding_loss", "slowness_loss",
    "PrismV2Model", "StepOutput", "EpisodeOutput",
]
