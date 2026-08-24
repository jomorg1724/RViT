"""
Auxiliary losses for HRA.

(1) predictive_coding_loss  — variational free-energy / next-frame MSE.
(2) slowness_loss           — optional temporal regulariser on the recurrent state.
(3) quantile_huber_loss     — QR-DQN distributional-critic loss (Dabney 2018).

All three are bitter-lesson compliant — environment-agnostic, no reference to
the cue / change-detection structure / reward palette / Posner timeline. The
same losses apply unchanged to MovingMNIST, KTH, UCF101, Atari, etc.

Architecture writeups:
    L_PC, L_slow         : see ../MODEL_DESIGN.md §3 (architecture)
    quantile_huber_loss  : see ../Prism/docs/PRISM_V2/Q_CRITIC.md (precedent
                           design) and Dabney et al. 2018 (the original loss).
"""
from __future__ import annotations

import torch


def predictive_coding_loss(
    V_t: torch.Tensor,
    V_hat_t: torch.Tensor,
    valid_mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """
    Variational free-energy *accuracy* term, under a Gaussian likelihood
    p(V_t | M_{t-1}) = 𝒩(V_t; g(M_{t-1}), σ² I).

    Up to the irrelevant constant 1/(2σ²) and an additive log(σ) term, this
    reduces to mean squared error between the bottom-up features V_t and the
    top-down generative prediction V̂_t = g(M_{t-1}):

        L_PC  =  (1 / (C·H·W)) · Σ_{c,i,j} ( V_{t,c,i,j} − V̂_{t,c,i,j} )²

    Parameters
    ----------
    V_t        : (B, C, H, W)  bottom-up features (target)
    V_hat_t    : (B, C, H, W)  top-down prediction (candidate)
    valid_mask : (B,) or None
        Optional per-batch-element mask. If provided, only batch elements with
        valid_mask[b] == 1 contribute to the loss (useful for padded sequences
        where some elements are post-episode garbage).

    Returns
    -------
    loss : scalar tensor (mean across batch and spatial dims)

    Why mean (not sum)?
    -------------------
    Mean-reduction makes the loss scale invariant to (C, H, W) and to batch
    size, so the same coefficient λ_PC = 1.0 transfers between model widths
    and batch sizes. Sum-reduction is sometimes preferred for theoretical
    reasons (it's what falls out of variational inference up to constants),
    but is brittle in practice — a 2× wider model would need a 2× smaller λ.

    Numerical stability
    -------------------
    Plain MSE is numerically well-behaved if V_t and V̂_t are O(1), which we
    arrange by GroupNorming the V1 stem output (see stem.py) and zero-init'ing
    the decoder output (see decoder.py).

    Gradient flow
    -------------
    Gradient flows from this scalar to:
      - the decoder g (via V̂_t)
      - the V1 stem (via V_t — V_t is the *target* but it is differentiable;
        the stem learns to produce features the decoder can predict)
      - the FiLM γ, β only indirectly: P_t feeds the GRU which feeds the next
        M, so the FiLM affects future V̂'s.
      - the GRU only via future steps (this loss does not directly touch M_t).
    """
    if V_t.shape != V_hat_t.shape:
        raise ValueError(
            f"predictive_coding_loss: shape mismatch V_t={tuple(V_t.shape)} "
            f"vs V_hat_t={tuple(V_hat_t.shape)}"
        )

    # Per-batch-element MSE: (B, C, H, W) → (B,) by mean over (1, 2, 3).
    sq_err = (V_t - V_hat_t).pow(2)
    per_b_loss = sq_err.mean(dim=(1, 2, 3))  # (B,)

    if valid_mask is not None:
        if valid_mask.shape != per_b_loss.shape:
            raise ValueError(
                f"valid_mask shape {tuple(valid_mask.shape)} does not match "
                f"per-batch loss shape {tuple(per_b_loss.shape)}"
            )
        # Masked mean. Add small eps to avoid div-by-zero on all-invalid batches.
        denom = valid_mask.sum().clamp(min=1.0)
        return (per_b_loss * valid_mask).sum() / denom

    return per_b_loss.mean()


def slowness_loss(
    M_t: torch.Tensor,
    M_prev: torch.Tensor,
    valid_mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """
    Slowness prior (Berkes & Wiskott, 2005):

        L_slow  =  (1 / (C·H·W)) · ‖ M_t − M_{t-1} ‖_F²

    A small weight on this loss encourages temporally stable representations,
    which is universally useful for any temporal sensory environment — it
    does not encode task-specific knowledge.

    Off by default (λ_slow = 0). Turn on if memory representations look
    over-volatile in diagnostics.

    Parameters
    ----------
    M_t        : (B, C, H, W)  current memory
    M_prev     : (B, C, H, W)  previous memory
    valid_mask : (B,) or None  optional masking (see predictive_coding_loss)

    Returns
    -------
    loss : scalar tensor
    """
    if M_t.shape != M_prev.shape:
        raise ValueError(
            f"slowness_loss: shape mismatch M_t={tuple(M_t.shape)} vs "
            f"M_prev={tuple(M_prev.shape)}"
        )

    sq = (M_t - M_prev).pow(2)
    per_b = sq.mean(dim=(1, 2, 3))  # (B,)

    if valid_mask is not None:
        denom = valid_mask.sum().clamp(min=1.0)
        return (per_b * valid_mask).sum() / denom

    return per_b.mean()


def quantile_huber_loss(
    predicted_quantiles: torch.Tensor,
    targets: torch.Tensor,
    valid_mask: torch.Tensor | None = None,
    kappa: float = 1.0,
) -> torch.Tensor:
    """
    Quantile-Huber regression loss for distributional RL (Dabney et al. 2018,
    "Distributional Reinforcement Learning with Quantile Regression", §3).

    Shape-agnostic over leading batch dimensions. The last dim of
    ``predicted_quantiles`` is the quantile axis; ``targets`` and
    ``valid_mask`` share the leading dims (without the quantile axis).

    Given N predicted quantile estimates Z_τ_1, ..., Z_τ_N at midpoint quantile
    levels τ_i = (2i − 1)/(2N), and a scalar return target G, the loss is

        L  =  (1/N) Σ_i  |τ_i − 𝟙[G − Z_τ_i < 0]| · L_κ(G − Z_τ_i)

    where L_κ is the Huber loss with transition point κ:

        L_κ(δ)  =  ½ δ²                     if |δ| ≤ κ
                =  κ (|δ| − ½ κ)             otherwise

    The asymmetric multiplier |τ − 𝟙[·]| makes this a *quantile* regression:
    above-target residuals are penalised at weight (1 − τ_i), below-target at
    weight τ_i. With τ_i evenly spaced over (0, 1) this fits the full
    empirical CDF of returns at the N midpoint levels.

    1/N reduction over quantiles matches Q_CRITIC.md §2.3.

    Parameters
    ----------
    predicted_quantiles : (..., N)   last dim is the quantile axis
    targets             : (...,)     same leading shape as predictions
    valid_mask          : (...,) | None   optional same-shape mask; if given,
                           the loss is the masked-mean over per-element terms.
    kappa               : Huber transition (default 1.0, per Dabney 2018)

    Returns
    -------
    loss : scalar tensor

    Caller contract
    ---------------
    For action-conditional distributional critics, gather the executed-
    action's quantile slice *before* calling this function — pass
    Q_φ(s_t, a_t; ·), not the full Q_φ(s_t, ·; ·) tensor. Otherwise
    broadcasting silently trains every action's Q toward the same target
    (the bug Q_CRITIC.md §4.3 flags).
    """
    if predicted_quantiles.dim() < 2:
        raise ValueError(
            f"predicted_quantiles must have ≥2 dims with quantile axis last; "
            f"got shape {tuple(predicted_quantiles.shape)}"
        )
    N = predicted_quantiles.shape[-1]
    leading = predicted_quantiles.shape[:-1]
    if targets.shape != leading:
        raise ValueError(
            f"targets shape {tuple(targets.shape)} must match predicted_quantiles "
            f"leading dims {tuple(leading)}"
        )
    if valid_mask is not None and valid_mask.shape != leading:
        raise ValueError(
            f"valid_mask shape {tuple(valid_mask.shape)} must match leading dims {tuple(leading)}"
        )

    targets_b = targets.unsqueeze(-1)  # (..., 1)
    delta = targets_b - predicted_quantiles  # (..., N)

    # Quantile midpoints τ_i = (2i − 1)/(2N), broadcast to (..., N).
    tau = (torch.arange(N, device=delta.device, dtype=delta.dtype) * 2.0 + 1.0) / (2.0 * N)
    tau = tau.view(*((1,) * len(leading)), N)

    abs_d = delta.abs()
    huber = torch.where(
        abs_d <= kappa,
        0.5 * delta.pow(2),
        kappa * (abs_d - 0.5 * kappa),
    )
    weight = (tau - (delta < 0).float()).abs()

    per_elt = (weight * huber).mean(dim=-1)  # (...,)

    if valid_mask is not None:
        denom = valid_mask.sum().clamp(min=1.0)
        return (per_elt * valid_mask).sum() / denom

    return per_elt.mean()
