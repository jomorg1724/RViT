"""
Hierarchical FiLM modulation.

Spec: §3.4 of ../Prism/docs/PRISM_V2_PROPOSAL.md.

Mathematical formulation
------------------------
v2 has two FiLM pathways acting on V_1^t:

    Within-level (fast):  γ^fast = Conv_{1×1}(M^fast_{t-1})  ∈ ℝ^(B, C_V1, 12, 12)
                          β^fast = Conv_{1×1}(M^fast_{t-1})

    Cross-level (slow):   γ^slow = Upsample_{6→12}(Conv_{1×1}(M^slow_{t-1}))
                          β^slow = Upsample_{6→12}(Conv_{1×1}(M^slow_{t-1}))

Composition (fast first, then slow on top):

    P_1^t = γ^slow ⊙ ( γ^fast ⊙ V_1^t + β^fast ) + β^slow

Both modulations initialize to identity (γ-bias=1, β-bias=0, conv weights ~
small Gaussian) so FiLM is a no-op at the start of training. The composition
order — fast modulation first, slow gating it from above — reflects the
cortical observation that within-area recurrence is faster than cross-area
descending feedback (Bastos et al. 2012, Figs. 4–5).

Why 1×1 kernels
---------------
Topographic respect: each location of memory modulates only the corresponding
location of perception. Required so the cued-quadrant top-down expectation is
spatially specific rather than smeared across the visual field.

Slow → V1 upsampling: LEARNED (ConvTranspose2d)
------------------------------------------------
The slow memory operates at 6×6 resolution (paired with V_2). To project it
onto the 12×12 V1 grid we use a learned ConvTranspose2d (kernel=2, stride=2)
rather than fixed bilinear interpolation. The transpose conv is initialized to
match bilinear's behaviour (kernel = 1/4 uniform), then the network can adapt
the upsampling kernel to whatever produces the most useful per-location
top-down modulation. Per-channel (depthwise) so we preserve the per-V1-channel
modulation semantics — γ_slow at output channel c only depends on input
channel c, no cross-channel mixing.

Biological correlates
---------------------
- Within-level fast FiLM ↔ recurrent V1 inhibition / divisive normalization
  shaped by V1's own working-memory-like persistent activity (Reynolds & Heeger
  2009 normalization model of attention).
- Cross-level slow FiLM ↔ descending feedback from prefrontal/parietal cortex
  to V1 (Reynolds & Chelazzi 2004; Maunsell 2015). Anatomically the strongest
  attentional gain modulation in V1 is *exogenous* (driven from higher areas)
  rather than endogenous, which matches the model topology.

Initialization (identity at init)
---------------------------------
γ-bias = 1, β-bias = 0, conv weights ~ 𝒩(0, 1e-4). At random init the
FiLM modulation is the identity transform; the network must earn its
modulation through training.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class HierarchicalFiLM(nn.Module):
    """
    Two-pathway FiLM: within-level (M_fast → V_1) plus cross-level
    (M_slow → V_1, with bilinear upsample).

    Args
    ----
    fast_memory_channels : C_M^fast  (default 32)
    slow_memory_channels : C_M^slow  (default 64)
    feature_channels     : C_V1      (default 64, must match V1Stem.out_channels)
    fast_h, fast_w       : V_1 spatial dims (default 12, 12)
    slow_h, slow_w       : M^slow spatial dims (default 6, 6) — used to size the upsample
    init_weight_std      : init std of γ/β-conv weights (default 1e-4)

    Forward signature: (M_fast, M_slow, V1)  ->  P_1
    """

    def __init__(
        self,
        fast_memory_channels: int = 32,
        slow_memory_channels: int = 64,
        feature_channels: int = 64,
        fast_h: int = 12,
        fast_w: int = 12,
        slow_h: int = 6,
        slow_w: int = 6,
        init_weight_std: float = 1e-4,
    ) -> None:
        super().__init__()
        self.fast_memory_channels = fast_memory_channels
        self.slow_memory_channels = slow_memory_channels
        self.feature_channels = feature_channels
        self.fast_h, self.fast_w = fast_h, fast_w
        self.slow_h, self.slow_w = slow_h, slow_w

        # Within-level fast FiLM (analogous to PRISM v1's FiLM).
        self.gamma_fast = nn.Conv2d(fast_memory_channels, feature_channels, kernel_size=1, bias=True)
        self.beta_fast = nn.Conv2d(fast_memory_channels, feature_channels, kernel_size=1, bias=True)

        # Cross-level slow FiLM. We compute γ, β at the slow resolution (6×6)
        # then LEARNED-upsample to the V1 resolution (12×12) via ConvTranspose2d.
        self.gamma_slow = nn.Conv2d(slow_memory_channels, feature_channels, kernel_size=1, bias=True)
        self.beta_slow = nn.Conv2d(slow_memory_channels, feature_channels, kernel_size=1, bias=True)

        # Learned upsamplers (depthwise, stride-2, kernel-2). Each output channel
        # is a learned reweighting of the corresponding input channel's 2×2
        # neighborhood. Initialized to match bilinear (uniform 1/4 kernel).
        self.upsample_gamma = nn.ConvTranspose2d(
            feature_channels, feature_channels,
            kernel_size=2, stride=2, padding=0,
            groups=feature_channels, bias=False,
        )
        self.upsample_beta = nn.ConvTranspose2d(
            feature_channels, feature_channels,
            kernel_size=2, stride=2, padding=0,
            groups=feature_channels, bias=False,
        )
        # Init: uniform 1/4 kernel = 2× bilinear at initialization.
        with torch.no_grad():
            self.upsample_gamma.weight.fill_(0.25)
            self.upsample_beta.weight.fill_(0.25)

        # Identity-at-init for both modulations.
        for conv in (self.gamma_fast, self.gamma_slow):
            nn.init.normal_(conv.weight, mean=0.0, std=init_weight_std)
            nn.init.constant_(conv.bias, 1.0)
        for conv in (self.beta_fast, self.beta_slow):
            nn.init.normal_(conv.weight, mean=0.0, std=init_weight_std)
            nn.init.constant_(conv.bias, 0.0)

    def forward(
        self,
        M_fast: torch.Tensor,
        M_slow: torch.Tensor,
        V1: torch.Tensor,
    ) -> torch.Tensor:
        """
        M_fast : (B, C_M^fast, 12, 12)
        M_slow : (B, C_M^slow, 6, 6)
        V1     : (B, C_V1, 12, 12)

        Returns
        -------
        P_1 : (B, C_V1, 12, 12)  modulated perceptual code
        """
        # Within-level (fast) modulation.
        gf = self.gamma_fast(M_fast)  # (B, C_V1, 12, 12)
        bf = self.beta_fast(M_fast)
        v_fast_modulated = gf * V1 + bf  # apply fast layer

        # Cross-level (slow) modulation: compute at 6×6, LEARNED-upsample to 12×12.
        gs_low = self.gamma_slow(M_slow)  # (B, C_V1, 6, 6)
        bs_low = self.beta_slow(M_slow)
        gs = self.upsample_gamma(gs_low)  # (B, C_V1, 12, 12) — learned
        bs = self.upsample_beta(bs_low)   # (B, C_V1, 12, 12) — learned

        # Composition: fast first, slow on top.
        P_1 = gs * v_fast_modulated + bs
        return P_1

    @torch.no_grad()
    def gain_magnitudes(self, M_fast: torch.Tensor, M_slow: torch.Tensor) -> dict:
        """Diagnostic: per-location L2 norm of γ_fast and γ_slow across channels.
        Useful as a *secondary* interpretable readout (the primary is the saliency map).
        Returns a dict with keys 'fast' and 'slow', both (B, 1, 12, 12).
        """
        gf = self.gamma_fast(M_fast)
        gs_low = self.gamma_slow(M_slow)
        gs = self.upsample_gamma(gs_low)
        fast_mag = gf.pow(2).mean(dim=1, keepdim=True).sqrt()
        slow_mag = gs.pow(2).mean(dim=1, keepdim=True).sqrt()
        return {"fast": fast_mag, "slow": slow_mag}
