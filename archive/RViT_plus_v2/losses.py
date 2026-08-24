"""
Loss helpers for RViT+.

Five auxiliary objectives (per design doc §3.5):
    1. pixel_recon_loss           — exponentially-weighted MSE across n_BR reconstructions
    2. kl_to_unit_gaussian        — VAE KL against N(0, I) (computed in latent.py; this
                                    file just provides a wrapper for convenience)
    3. slowness_loss              — temporal stability on each layer's hidden state
    4. jepa_latent_loss           — V-JEPA-style next-frame latent prediction
    5. attention_supervision_loss — optional KL against a cue-derived attention prior
                                    (off by default; turned on if Stage-4 RL stalls)
"""
from __future__ import annotations

from typing import List, Optional, Sequence

import torch
import torch.nn.functional as F


def pixel_recon_loss(
    recons: Sequence[torch.Tensor],
    target: torch.Tensor,
    n_BR: Optional[int] = None,
) -> torch.Tensor:
    """Exponentially-weighted MSE across n_BR iterative reconstructions.

    Per `concepts/iterative_variational_encoder_decoder.md` §"Phase 2":
        L_recon = Σ_i γ_i · MSE(recon_i, target),  γ_i = e^{i − n_BR}

    The exponential schedule weights later proposals more heavily — the
    architecture is encouraged to *converge*, not just to produce a good
    first guess.

    Parameters
    ----------
    recons : list/tuple of (B, C, H, W) tensors, length n_BR (or `n_BR` if given)
    target : (B, C, H, W)
    n_BR   : int | None — defaults to len(recons)

    Returns
    -------
    loss : scalar
    """
    if n_BR is None:
        n_BR = len(recons)
    total = 0.0
    total_w = 0.0
    for i, recon in enumerate(recons):
        if recon.shape != target.shape:
            raise ValueError(
                f"recon[{i}] shape {tuple(recon.shape)} != target {tuple(target.shape)}"
            )
        gamma = float(torch.exp(torch.tensor(float(i - n_BR + 1))).item())
        # i+1−n_BR so the LAST proposal gets weight e^0 = 1, earlier are smaller.
        mse = F.mse_loss(recon, target, reduction="mean")
        total = total + gamma * mse
        total_w += gamma
    return total / max(total_w, 1e-12)


def kl_to_unit_gaussian(mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
    """KL(N(μ, σ²) || N(0, I)) = ½ Σ (μ² + σ² − log σ² − 1)."""
    kl_per_dim = 0.5 * (mu.pow(2) + logvar.exp() - logvar - 1.0)
    return kl_per_dim.sum(dim=-1).mean()


def slowness_loss(
    states_t: torch.Tensor,
    states_t_minus_1: torch.Tensor,
) -> torch.Tensor:
    """L = mean ‖C_t − C_{t-1}‖². Per Berkes-Wiskott 2005."""
    if states_t.shape != states_t_minus_1.shape:
        raise ValueError(
            f"slowness shape mismatch: {tuple(states_t.shape)} vs {tuple(states_t_minus_1.shape)}"
        )
    return F.mse_loss(states_t, states_t_minus_1, reduction="mean")


def jepa_latent_loss(
    predicted_next_latent: torch.Tensor,
    target_next_latent: torch.Tensor,
) -> torch.Tensor:
    """V-JEPA-style latent prediction loss.

    The "target" latent is computed by the *target encoder* (EMA copy of the
    main encoder), and its gradient is NOT propagated — this is the standard
    JEPA stop-gradient trick to prevent representation collapse. The caller
    is responsible for applying .detach() before passing target_next_latent.

    L = mean ‖predicted − sg[target]‖² (cosine option deferred).
    """
    return F.mse_loss(predicted_next_latent, target_next_latent, reduction="mean")


def attention_supervision_loss(
    attn_logits: torch.Tensor,
    prior: torch.Tensor,
    valid_mask: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """KL between the model's attention distribution and a target prior.

    For escaping the FT-collapse-to-uniform trap (see
    `concepts/feedback_transformer.md` open question 4): a small KL penalty
    that pulls attention toward a cue-derived location prior during cue/change
    windows. OFF by default in the loss bundle; enable with a small coef
    (e.g. 0.05) if Stage-4 RL convergence stalls.

    attn_logits : (B, n_heads, N, N) — pre-softmax FT scores.
    prior       : (B, N) | (N,) — target distribution over key positions, summing to 1.
    valid_mask  : (B,) or (B, n_heads) — only count loss where mask=1.

    Loss is KL(softmax(attn_logits[query=avg]) || prior).
    """
    # Average over query positions, take mean over heads → (B, N) distribution over keys.
    attn_mean = attn_logits.mean(dim=(1, 2))  # (B, N)
    attn_dist = F.log_softmax(attn_mean, dim=-1)
    if prior.dim() == 1:
        prior = prior.unsqueeze(0).expand(attn_dist.shape[0], -1)
    # KL(model || prior) = Σ model · (log model − log prior)
    # Equivalent: cross-entropy(prior, model) − entropy(prior). Use the
    # asymmetric form pulling model toward prior:
    log_prior = (prior + 1e-9).log()
    kl_per_b = (attn_dist.exp() * (attn_dist - log_prior)).sum(dim=-1)
    if valid_mask is not None:
        kl_per_b = kl_per_b * valid_mask.view(-1)
        denom = valid_mask.sum().clamp(min=1.0)
        return kl_per_b.sum() / denom
    return kl_per_b.mean()
