"""RViT+ — Recurrent ViT plus.

A multi-layer recurrent attention model designed for video reconstruction
pretraining followed by RL fine-tuning on change-detection. See
../RVIT_PLUS_DESIGN.md for the full architectural rationale.
"""
from .attention import FeedbackTransformer
from .decoder import IterativeReconstructionDecoder
from .encoder import RViTPlusEncoder
from .latent import VAELatentSampler
from .losses import (
    attention_supervision_loss,
    jepa_latent_loss,
    kl_to_unit_gaussian,
    pixel_recon_loss,
    slowness_loss,
)
from .memory import GridCellRNN_LSTM
from .model import RViTPlusModel, StepOutput
from .stem import V1Stem

__all__ = [
    "FeedbackTransformer",
    "GridCellRNN_LSTM",
    "IterativeReconstructionDecoder",
    "RViTPlusEncoder",
    "RViTPlusModel",
    "StepOutput",
    "V1Stem",
    "VAELatentSampler",
    "attention_supervision_loss",
    "jepa_latent_loss",
    "kl_to_unit_gaussian",
    "pixel_recon_loss",
    "slowness_loss",
]
