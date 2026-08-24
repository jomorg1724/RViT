"""
Spatial VAE latent sampler for RViT+.

Per the architectural-program commitment (`research_db/threads/the_user_architectural_program.md`
§4 and `concepts/iterative_variational_encoder_decoder.md` §"Multi-patch
distributional latents"): the guide latent is a *matrix*, not a vector —
$\\tilde H_0 \\in \\mathbb{R}^{n_{\\text{patch}} \\times d_{\\text{guide}}}$ —
so the spatial organization of memory is preserved through the VAE
bottleneck.

This implementation samples the latent at the *deepest* encoder level
(C₃, native 6×6 in the reference instantiation). Per-(channel, h, w)
position has its own (μ, log σ²) computed by a 1×1 conv on the encoder's
final C₃ state. KL is the per-position sum against a unit-Gaussian prior.

This replaces the original v1 vector-latent sampler (GAP across spatial
positions → Linear → 128-dim vector) which was the architectural error
identified during run 7: the GAP collapsed the encoder's spatial structure
at the bottleneck, then the decoder broadcast a (B, latent_dim) vector
across space — producing spatially-uniform driving signals at every
decoder step, which the decoder cells could not recover from. The user
flagged this directly: *"You have reduced the visual scene to a single 1D
vector. This was the foundational thing I asked you not to do."*

For the simplest faithful instantiation we keep the latent shape matched
to C₃. A matrix-normal extension with row-covariance over patches (the
full theory of `multi-patch-distributional-latents` in the taxonomy) is
deferred — the per-position diagonal-Gaussian baseline established here
is the simpler first step.
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn


class SpatialVAELatentSampler(nn.Module):
    """Per-position (μ, log σ²) on the encoder's deepest spatial state.

    Args
    ----
    state_channels    : (c1, c2, c3) encoder per-layer channel counts.
                        The latent is sampled off the c3 layer.
    grid_hw           : ((h1,w1),(h2,w2),(h3,w3)) — used only for the
                        deepest level's (h3,w3); shape-checking + return.
    latent_channels   : channel dim of the spatial latent. Default 16 →
                        latent has 16 × 6 × 6 = 576 dims at the standard
                        shape — comparable in size to the prior 128-vector
                        baseline but spatially organized.
    """

    def __init__(
        self,
        state_channels: Tuple[int, int, int] = (64, 96, 128),
        grid_hw: Tuple[Tuple[int, int], ...] = ((12, 12), (6, 6), (3, 3)),
        latent_channels: int = 16,
    ) -> None:
        super().__init__()
        c3 = state_channels[2]
        h3, w3 = grid_hw[2]
        self.c3 = c3
        self.latent_channels = latent_channels
        self.latent_h, self.latent_w = h3, w3

        # Per-position Conv1×1 — no spatial coupling, just channel
        # projection at each (h, w).
        self.conv_mu = nn.Conv2d(c3, latent_channels, kernel_size=1)
        self.conv_logvar = nn.Conv2d(c3, latent_channels, kernel_size=1)

        # σ ≈ exp(-3/2) ≈ 0.22 at init (small but not collapsed).
        nn.init.zeros_(self.conv_logvar.weight)
        nn.init.constant_(self.conv_logvar.bias, -3.0)
        nn.init.xavier_uniform_(self.conv_mu.weight)
        nn.init.zeros_(self.conv_mu.bias)

    def forward(self, layer_states: tuple) -> dict:
        """layer_states: (C₁, C₂, C₃) from the encoder.

        Returns dict with:
            sample      : (B, latent_channels, h3, w3) reparametrized sample
            mu          : (B, latent_channels, h3, w3)
            logvar      : (B, latent_channels, h3, w3)
            kl          : scalar — mean over batch, sum over (c, h, w)
            kl_per_dim  : (B, latent_channels, h3, w3) — for free-bits / diagnostics
        """
        C3 = layer_states[2]  # (B, c3, h3, w3)
        if C3.shape[1] != self.c3:
            raise ValueError(f"C3 channels {C3.shape[1]} != expected {self.c3}")
        if C3.shape[-2:] != (self.latent_h, self.latent_w):
            raise ValueError(
                f"C3 spatial {tuple(C3.shape[-2:])} != expected ({self.latent_h},{self.latent_w})"
            )

        mu = self.conv_mu(C3)       # (B, latent_c, h3, w3)
        logvar = self.conv_logvar(C3)
        std = (0.5 * logvar).exp()
        eps = torch.randn_like(std)
        sample = mu + eps * std     # (B, latent_c, h3, w3)

        # KL(N(μ,σ²) || N(0,1)) per spatial position and channel:
        # ½ (μ² + σ² − log σ² − 1)
        kl_per_dim = 0.5 * (mu.pow(2) + logvar.exp() - logvar - 1.0)
        # Total KL = sum over (latent_c, h3, w3), then batch-mean.
        kl = kl_per_dim.sum(dim=(1, 2, 3)).mean()

        return {
            "sample": sample,
            "mu": mu,
            "logvar": logvar,
            "kl": kl,
            "kl_per_dim": kl_per_dim,
        }


# Back-compat alias so analysis scripts and tests that import the old name
# still resolve to the spatial version. The old VAELatentSampler used a
# (B, latent_dim) vector latent — that signature is intentionally NOT
# preserved because it represented the architectural error of collapsing
# the spatial scene to 1D.
VAELatentSampler = SpatialVAELatentSampler
