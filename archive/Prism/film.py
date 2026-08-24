"""
FiLM (Feature-wise Linear Modulation) — top-down gain pathway from memory.

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

Mathematical formulation
------------------------
Given previous memory state M_{t-1} ∈ ℝ^(B,C_M,H,W) and bottom-up perceptual
feature volume V_t ∈ ℝ^(B,C_V,H,W), produce a top-down-modulated code:

    γ_t = Conv_{1×1}^{C_M → C_V}(M_{t-1})         ∈ ℝ^(B,C_V,H,W)
    β_t = Conv_{1×1}^{C_M → C_V}(M_{t-1})         ∈ ℝ^(B,C_V,H,W)

    P_t = γ_t ⊙ V_t  +  β_t                       ∈ ℝ^(B,C_V,H,W)

This implements the multiplicative-gain-plus-additive-shift form of FiLM
(Perez et al., 2018), which matches the canonical "normalisation model of
attention" (Reynolds & Heeger, 2009) — distributed, per-channel, per-location
multiplicative gain plus a baseline shift.

Why 1×1 convs (and not 3×3)?
----------------------------
Topographic respect: location (i, j) in memory modulates location (i, j) in
perception, with no spatial bleed across receptive fields. This preserves
the invariant that memory at location (i, j) is "about" location (i, j),
which is what makes spatial binding through memory possible.

Initialisation: identity at init
--------------------------------
We require γ ≈ 1 and β ≈ 0 at random init so FiLM is the identity transform
initially. This gives the rest of the network a clean training start: the
generative decoder must *earn* its modulation, rather than starting from a
random affine perturbation that the stem then has to undo.

We achieve this by:
    γ-conv: weights ∼ 𝒩(0, 1e-4),  bias = 1.0   ⇒  γ ≈ 1 + ε
    β-conv: weights ∼ 𝒩(0, 1e-4),  bias = 0.0   ⇒  β ≈ 0 + ε

A common alternative is *zero-init* (Goyal et al., 2017) for the conv
weights and bias, then learning a residual; we use small-Gaussian-weight +
identity-bias because it gives nonzero gradient to the conv weights from the
first step.

Complexity / params
-------------------
Time:   O(B · C_M · C_V · H · W)
Space:  O(B · C_V · H · W) for γ, β, and P_t (computed in place where possible).
Params: 2 · (C_M · C_V + C_V) = 2·(16·32 + 32) = 1,088 for the default sizes.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class FiLM(nn.Module):
    """
    Feature-wise Linear Modulation: P_t = γ(M_{t-1}) ⊙ V_t + β(M_{t-1}).

    Args
    ----
    memory_channels : C_M, channels in M_{t-1} (default 16)
    feature_channels: C_V, channels in V_t      (default 32)
    init_weight_std : std of γ/β-conv weights at init (default 1e-4)

    Returns (forward)
    -----------------
    P_t : torch.Tensor  shape (B, C_V, H, W)
    """

    def __init__(
        self,
        memory_channels: int = 16,
        feature_channels: int = 32,
        init_weight_std: float = 1e-4,
    ) -> None:
        super().__init__()
        self.memory_channels = memory_channels
        self.feature_channels = feature_channels

        # 1×1 convs: per-location, per-channel modulation. No spatial mixing.
        # bias=True so we can set biases to (1, 0) for identity-at-init.
        self.gamma_conv = nn.Conv2d(memory_channels, feature_channels, kernel_size=1, bias=True)
        self.beta_conv = nn.Conv2d(memory_channels, feature_channels, kernel_size=1, bias=True)

        # Identity-at-init: small-Gaussian weights, biases at (1, 0).
        # Why small-Gaussian and not zero?
        # Zero-init weights leave the conv with no gradient signal until the
        # bias accumulates a nonzero modulation (which would never happen
        # without input). Small-Gaussian gives the conv weights a tiny,
        # nonzero gradient from step 1 while the modulation is still ≈ identity.
        with torch.no_grad():
            nn.init.normal_(self.gamma_conv.weight, mean=0.0, std=init_weight_std)
            nn.init.normal_(self.beta_conv.weight, mean=0.0, std=init_weight_std)
            nn.init.constant_(self.gamma_conv.bias, 1.0)  # γ ≈ 1
            nn.init.constant_(self.beta_conv.bias, 0.0)  # β ≈ 0

    def forward(self, M_prev: torch.Tensor, V_t: torch.Tensor) -> torch.Tensor:
        """
        M_prev : (B, C_M, H, W)
        V_t    : (B, C_V, H, W)

        Returns
        -------
        P_t    : (B, C_V, H, W)
        """
        if M_prev.shape[1] != self.memory_channels:
            raise ValueError(
                f"FiLM expects M_prev with {self.memory_channels} channels; "
                f"got {M_prev.shape[1]}"
            )
        if V_t.shape[1] != self.feature_channels:
            raise ValueError(
                f"FiLM expects V_t with {self.feature_channels} channels; "
                f"got {V_t.shape[1]}"
            )
        if M_prev.shape[-2:] != V_t.shape[-2:]:
            raise ValueError(
                f"FiLM expects matching spatial dims; "
                f"got M={tuple(M_prev.shape[-2:])} vs V={tuple(V_t.shape[-2:])}"
            )

        # γ(M_{t-1}) : (B, C_V, H, W)
        gamma = self.gamma_conv(M_prev)

        # β(M_{t-1}) : (B, C_V, H, W)
        beta = self.beta_conv(M_prev)

        # P_t = γ ⊙ V + β. Broadcasted multiply + add: linear-cost element-wise.
        # Note: this is equivalent to learning a per-location, per-channel affine
        # transform of V_t whose parameters are predicted from M_{t-1}. It is the
        # discrete analogue of multiplicative gain modulation in cortex.
        return gamma * V_t + beta

    @torch.no_grad()
    def gain_magnitude(self, M_prev: torch.Tensor) -> torch.Tensor:
        """
        Diagnostic: per-location L2 norm of the gain γ(M_{t-1}) across channels.

        High values indicate locations where the top-down pathway is
        contributing strong amplification or suppression. Useful as a *secondary*
        interpretable readout (the primary one is the prediction-error map).

        Returns
        -------
        (B, 1, H, W)
        """
        gamma = self.gamma_conv(M_prev)
        # ‖γ_loc‖₂ across channels, with /sqrt(C) to keep the magnitude scale invariant.
        return gamma.pow(2).mean(dim=1, keepdim=True).sqrt()
