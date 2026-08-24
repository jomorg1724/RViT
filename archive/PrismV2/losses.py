"""
Auxiliary losses — variational free energy / predictive coding, per level.

Spec: §4 + §5 of ../Prism/docs/PRISM_V2_PROPOSAL.md.

The single auxiliary objective family is the variational-free-energy accuracy
term, instantiated at two cortical levels (V1 and V2). All loss components in
this module depend only on (x_t, V_1^t, V_2^t, M_fast, M_slow) and the model's
own predictions — they reference no environment-specific quantities and
preserve the bitter-lesson framing of v1.

Loss components used by the v2 trainer:

  L_pix^fwd      = ‖x_t − x̂(M_fast_{t-1})‖²              [V1 pixel forward]
  L_pix^auto     = ‖x_t − x̂(M_fast_t)‖²                  [V1 pixel autoencoding]
  L_V1^feat      = ‖V_1^t − ḡ_V1(M_fast_{t-1})‖²          [V1 feature]
  L_V2^feat      = ‖V_2^t − ḡ_V2(M_slow_{t-1})‖²          [V2 feature]
  L_V2^feat_auto = ‖V_2^t − ḡ_V2(M_slow_t)‖²              [V2 feature autoencoding]

where ḡ denotes the multi-head decoder's full prediction (per-head predictions
flattened back to a single feature volume for the loss).
"""
from __future__ import annotations

import torch


def predictive_coding_loss(
    target: torch.Tensor,
    prediction: torch.Tensor,
    valid_mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """Mean squared error between target and prediction.

    Generic; used for all PC components (pixel and feature, forward and autoenc).
    """
    if target.shape != prediction.shape:
        raise ValueError(
            f"predictive_coding_loss shape mismatch: {tuple(target.shape)} vs {tuple(prediction.shape)}"
        )
    sq_err = (target - prediction).pow(2)
    # Mean over all dims except batch.
    per_b = sq_err.mean(dim=tuple(range(1, sq_err.dim())))
    if valid_mask is not None:
        denom = valid_mask.sum().clamp(min=1.0)
        return (per_b * valid_mask).sum() / denom
    return per_b.mean()


def multi_head_pc_loss(
    V_target: torch.Tensor,        # (B, C, H, W)
    V_hat_per_head: torch.Tensor,  # (B, K, C/K, H, W)
) -> torch.Tensor:
    """Per-head feature-PC loss = mean MSE between V_target's per-head slices and V_hat_per_head.

    Equivalent to flattening V_hat_per_head back to (B, C, H, W) and computing MSE,
    but explicit so the per-head structure is documented.
    """
    B, K, c_per_head, H, W = V_hat_per_head.shape
    V_target_per_head = V_target.view(B, K, c_per_head, H, W)
    return (V_target_per_head - V_hat_per_head).pow(2).mean()


def quantile_huber_loss(
    quantiles: torch.Tensor,
    targets: torch.Tensor,
    valid_mask: torch.Tensor,
    kappa: float = 1.0,
) -> torch.Tensor:
    """Quantile regression (QR-DQN) loss for a distributional value head.

    Each timestep has N quantile predictions θ_1..θ_N, estimated at fixed
    quantile levels τ_i = (2i − 1) / (2N). The loss is the asymmetric Huber:

        L = (1/N) Σ_i |τ_i − 1(δ_i < 0)| · L_huber_κ(δ_i)
        where δ_i = target − θ_i

    Using a single scalar return target per timestep (standard for PPO with
    GAE; the distribution is learned by fitting different quantiles to the
    same scalar target at different asymmetric penalties).

    Args
    ----
    quantiles  : (B, T, N)  predicted quantile values
    targets    : (B, T)     scalar GAE return targets
    valid_mask : (B, T)     1 at valid steps, 0 at padding
    kappa      : Huber transition point (1.0 is standard)
    """
    N = quantiles.shape[-1]
    tau = (torch.arange(N, device=quantiles.device, dtype=quantiles.dtype) + 0.5) / N

    delta = targets.unsqueeze(-1) - quantiles           # (B, T, N)
    abs_delta = delta.abs()
    huber = torch.where(
        abs_delta <= kappa,
        0.5 * delta.pow(2),
        kappa * (abs_delta - 0.5 * kappa),
    )
    weight = (tau - (delta.detach() < 0).float()).abs() # (B, T, N)
    loss_per_step = (weight * huber).mean(dim=-1)        # (B, T)
    denom = valid_mask.sum().clamp(min=1.0)
    return (loss_per_step * valid_mask).sum() / denom


def slowness_loss(
    M_t: torch.Tensor,
    M_prev: torch.Tensor,
    valid_mask: torch.Tensor | None = None,
) -> torch.Tensor:
    """Slowness prior: L_slow = ‖M_t − M_{t-1}‖_F² (mean per element)."""
    if M_t.shape != M_prev.shape:
        raise ValueError(
            f"slowness_loss shape mismatch: {tuple(M_t.shape)} vs {tuple(M_prev.shape)}"
        )
    per_b = (M_t - M_prev).pow(2).mean(dim=tuple(range(1, M_t.dim())))
    if valid_mask is not None:
        denom = valid_mask.sum().clamp(min=1.0)
        return (per_b * valid_mask).sum() / denom
    return per_b.mean()
