"""
HRA — Hierarchical Recurrent Attention.

A small recurrent attention model with per-layer recurrent state, spatially
arranged, communicating via the Feedback Transformer. Designed to be both:

    Track A — Interpretable neuro-AI model on cued change-detection
              (Posner task, follow-up to Herman & Morgan 2025 recurrent ViT).
    Track B — Efficient parameter-light video-prediction model
              (MovingMNIST → KTH → UCF101).

See ../MODEL_DESIGN.md for the design document.
"""
from .attention import FeedbackTransformer
from .decoder import FeatureDecoder, PixelDecoder
from .losses import predictive_coding_loss, quantile_huber_loss, slowness_loss
from .memory import GridCellRNNCell
from .model import HRAModel, StepOutput
from .readout import ActorHead, CriticHead, DecisionReadout, DistributionalQHead
from .stem import V1Stem

__all__ = [
    "FeedbackTransformer",
    "FeatureDecoder",
    "PixelDecoder",
    "predictive_coding_loss",
    "quantile_huber_loss",
    "slowness_loss",
    "GridCellRNNCell",
    "HRAModel",
    "StepOutput",
    "ActorHead",
    "CriticHead",
    "DecisionReadout",
    "DistributionalQHead",
    "V1Stem",
]
