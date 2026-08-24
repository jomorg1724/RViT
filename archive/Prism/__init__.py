"""
PRISM — Predictive Recurrent Inference via Self-Modulation.

A small (~60 K parameter) all-convolutional, recurrent visual-attention
architecture for cued change-detection (and any other temporal sensory env).

Architecture (full writeup in `docs/THESIS.md` §3 Methods):

    x_t  ─►  V1 stem  ─►  V_t
                          │
            M_{t-1}  ─►  FiLM(γ,β)  ─►  P_t   (top-down gain)
                  │
                  └────►  decoder g  ─►  V̂_t  (top-down generative prediction)

            E_t = V_t − V̂_t          (prediction error volume)
            S_t = ‖E_t‖_c            (interpretable saliency map, derived)

            error-gated ConvGRU:    M_t = (1−u_t)·M_{t-1} + u_t·C̃_t
                                     u_t ∝ σ(...) · (1 + λ·S̄_t)

            inner WM (K iterations of free-energy gradient descent):
                  for k=1..K:  M_t  ←  M_t + ε · ErrBlock(V_t − g(M_t), M_t)

            decision readout:  s_t = [GAP(d_t), errPool(d_t, S_t)]   ∈ ℝ⁸
            heads:             π(a|s) = softmax(MLP(s_t)),  V(s) = MLP(s_t)

The only auxiliary loss is

    L_PC = ‖V_t − g(M_{t-1})‖²

i.e. the variational free-energy accuracy term. Bitter-lesson compliant.

References (full bibliography in `docs/THESIS.md`):
    - Friston, K. (2010). The free-energy principle: a unified brain theory?
    - Rao, R. P. N., & Ballard, D. H. (1999). Predictive coding in the visual cortex.
    - Schulman et al. (2017). Proximal Policy Optimization Algorithms.
    - Ballas, N. et al. (2016). Convolutional GRU.
"""

from .stem import V1Stem
from .film import FiLM
from .decoder import GenerativeDecoder, prediction_error_map
from .memory import ErrorGatedConvGRU, InnerWMLoop
from .readout import DecisionReadout, ActorHead, CriticHead
from .losses import predictive_coding_loss, slowness_loss
from .model import PrismModel

__all__ = [
    "V1Stem",
    "FiLM",
    "GenerativeDecoder",
    "prediction_error_map",
    "ErrorGatedConvGRU",
    "InnerWMLoop",
    "DecisionReadout",
    "ActorHead",
    "CriticHead",
    "predictive_coding_loss",
    "slowness_loss",
    "PrismModel",
]
