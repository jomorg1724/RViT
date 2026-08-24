"""
Auxiliary losses — the *only* aux is the variational free-energy / predictive
coding error. One optional regulariser (slowness).

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

Bitter-lesson audit
-------------------
Both functions in this module are entirely environment-agnostic:
    - L_PC depends only on (V_t, V̂_t)
    - L_slow depends only on (M_t, M_{t-1})
Neither references the cue, the change-detection structure, the reward palette,
the trial timeline, or any other ChangeDetectionEnv-specific quantity.
The same losses apply unchanged to moving MNIST, Atari, MetaWorld, etc.
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
