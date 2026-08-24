"""
Working memory: error-gated ConvGRU + inner WM variational-inference loop.

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

Two components, both small, both pure-conv.

(1) ErrorGatedConvGRU  (§4.4)
-----------------------------
Standard convolutional GRU (Ballas et al., 2016) with one twist: the update
gate is amplified by per-location prediction-error magnitude, so memory writes
more strongly where the model was wrong.

    cat_t  = [M_{t-1}, P_t]                      (B, C_M+C_V, H, W)
    cat_e  = [M_{t-1}, P_t, E_t]                 (B, C_M+2C_V, H, W)

    r_t        = σ( W_r * cat_t )                (B, C_M, H, W)
    C̃_t        = tanh( W_c * [r_t⊙M_{t-1}, P_t, E_t] )
    u_t^base   = σ( W_u * cat_t )

    Ŝ_t = batch-normalised S_t / max_{HW}(S_t)   (B, 1, H, W)  ∈ [0, 1]
    u_t = clamp( u_t^base · (1 + softplus(λ̃)·Ŝ_t),  max=1 )

    M_t = (1 − u_t) ⊙ M_{t-1}  +  u_t ⊙ C̃_t

The "softplus(λ̃)" parameterisation keeps λ ≥ 0 with a single learned scalar
(λ̃ ∈ ℝ); init λ̃ such that softplus(λ̃) ≈ 1.

(2) InnerWMLoop  (§4.5)
-----------------------
K-step iterative variational inference: at each iteration we re-decode M, take
the new prediction error, and use it (together with M itself) to drive an
update direction. This is one Friston-style gradient step on the variational
free energy F per iteration, with K iterations buying K gradient steps.

    for k = 0..K-1:
        V̂^(k) = g( M^(k) )
        E^(k) = V_t − V̂^(k)
        M^(k+1) = M^(k) + ε · ErrBlock( [E^(k), M^(k)] )

The K iterations realise the working-memory compute-depth hypothesis: a
single recurrent state can support K refinement steps within one environment
step, decoupling the depth of working-memory computation from the depth of
sensory feedforward processing. The reinterpretation as variational inference
gives the iterative loop a precise mathematical meaning: each step descends F.

Numerical stability of the inner loop
--------------------------------------
ε = 0.1 by default keeps each step perturbative. If the inner block diverges
in practice (residual norm grows in k rather than shrinking), wrap ErrBlock's
output in tanh — then each update has bounded magnitude and divergence is
impossible. We do NOT do this by default because tanh squashes gradient when
errors are large, slowing learning when learning is most informative.
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class ErrorGatedConvGRU(nn.Module):
    """
    Convolutional GRU whose update gate is amplified by per-location
    prediction-error magnitude.

    Args
    ----
    memory_channels  : C_M (default 16)
    feature_channels : C_V (default 32)
    kernel_size      : conv kernel (default 3)
    update_gate_bias : bias added to the update-gate logits before σ.
                       Default −1.0 → σ(−1) ≈ 0.27, conservative writing.
                       This is the chrono-init / slow-cell trick of Tallec &
                       Ollivier (2018) — biasing the update gate toward zero
                       sets the cell's effective time constant to multiple
                       environmental steps regardless of input magnitude.

    Forward signature: (M_prev, P_t, E_t)  ->  (M_t, u_t)
    """

    def __init__(
        self,
        memory_channels: int = 16,
        feature_channels: int = 32,
        kernel_size: int = 3,
        update_gate_bias: float = -1.0,
        init_lambda: float = 1.0,
    ) -> None:
        super().__init__()
        self.memory_channels = memory_channels
        self.feature_channels = feature_channels
        pad = kernel_size // 2  # SAME padding for odd kernels.

        # Reset gate r_t: takes [M, P], outputs C_M-channel σ in [0, 1].
        # Used to mask out parts of memory before forming the candidate.
        c_in_rt = memory_channels + feature_channels
        self.r_conv = nn.Conv2d(c_in_rt, memory_channels, kernel_size=kernel_size, padding=pad)

        # Candidate C̃_t: takes [r⊙M, P, E], outputs C_M-channel tanh.
        # Note: error E is fed in here so the *content* the GRU is considering
        # writing is informed by where predictions failed. This is the dense
        # learning signal that ties memory directly to the PC error.
        c_in_ct = memory_channels + feature_channels + feature_channels
        self.c_conv = nn.Conv2d(c_in_ct, memory_channels, kernel_size=kernel_size, padding=pad)

        # Update gate u_t^base: takes [M, P], outputs C_M-channel σ in [0, 1].
        # Pre-σ bias initialised negative for conservative writing.
        c_in_ut = memory_channels + feature_channels
        self.u_conv = nn.Conv2d(c_in_ut, memory_channels, kernel_size=kernel_size, padding=pad)

        # Initialisations.
        for conv in (self.r_conv, self.c_conv, self.u_conv):
            nn.init.kaiming_uniform_(conv.weight, a=0, mode="fan_in", nonlinearity="relu")
            if conv.bias is not None:
                nn.init.zeros_(conv.bias)
        # Override the update-gate bias to the conservative-writing value.
        with torch.no_grad():
            self.u_conv.bias.fill_(update_gate_bias)

        # λ as softplus(λ̃) ≥ 0. We pick λ̃ such that softplus(λ̃) ≈ init_lambda.
        # softplus⁻¹(y) = log(exp(y) − 1).
        # Default init_lambda=1.0 → λ̃ ≈ log(e − 1) ≈ 0.5413.
        lam_tilde_init = float(torch.log(torch.expm1(torch.tensor(init_lambda))).item())
        self.lambda_tilde = nn.Parameter(torch.tensor(lam_tilde_init))

    def forward(
        self,
        M_prev: torch.Tensor,
        P_t: torch.Tensor,
        E_t: torch.Tensor,
        S_t: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        M_prev : (B, C_M, H, W)  previous memory
        P_t    : (B, C_V, H, W)  FiLM-modulated bottom-up features
        E_t    : (B, C_V, H, W)  prediction-error volume (sign-preserving)
        S_t    : (B, 1, H, W)    per-location saliency map ≥ 0 (from prediction_error_map)

        Returns
        -------
        M_t : (B, C_M, H, W)  updated memory
        u_t : (B, C_M, H, W)  effective update gate (post error-amplification, post-clamp)
        """
        # ── Reset gate r_t ───────────────────────────────────────────────────
        # σ(W_r * [M_prev, P_t]). Modulates which channels of memory enter the
        # candidate. Range [0, 1] elementwise.
        cat_t = torch.cat([M_prev, P_t], dim=1)  # (B, C_M+C_V, H, W)
        r_t = torch.sigmoid(self.r_conv(cat_t))  # (B, C_M, H, W)

        # ── Candidate C̃_t ────────────────────────────────────────────────────
        # tanh ensures candidate values are bounded in [-1, 1], which is what
        # we want for a "proposal" that will be linearly blended with M_prev.
        # Including E_t here is the key channel of dense learning signal —
        # gradients from the PC loss flow through both the decoder (which
        # produced V̂ in E_t = V − V̂) AND through this convolution.
        cand_in = torch.cat([r_t * M_prev, P_t, E_t], dim=1)  # (B, C_M+2C_V, H, W)
        C_tilde = torch.tanh(self.c_conv(cand_in))  # (B, C_M, H, W)

        # ── Base update gate u_t^base ───────────────────────────────────────
        # σ(W_u * [M_prev, P_t]) + conservative-writing bias.
        u_base = torch.sigmoid(self.u_conv(cat_t))  # (B, C_M, H, W)

        # ── Per-batch normalisation of saliency S_t to [0, 1] ───────────────
        # We normalise per-batch-element so the amplification is RELATIVE to
        # each trial's current peak surprise — early in a trial when nothing
        # is surprising at all, even tiny errors get amplified to write what
        # signal they have. Late in a trial when one Gabor changed, the change
        # location dominates.
        # Numerical guard: divide by (max + eps) to avoid 0/0.
        # detach the max to keep this a pure normalisation; we still backprop
        # through the un-normalised S_t = sqrt(mean E²) elsewhere.
        S_max = S_t.amax(dim=(-1, -2), keepdim=True).detach() + 1e-6  # (B, 1, 1, 1)
        S_bar = S_t / S_max  # (B, 1, H, W),  ∈ [0, 1]

        # ── Error-amplified update gate ─────────────────────────────────────
        # u_t = u_base · (1 + λ · S̄_t). λ ≥ 0 via softplus.
        # The (1 + …) form means error amplifies but never *zeroes* the gate,
        # so memory always has the option to update everywhere (just less so).
        # Clamp at 1 so u_t remains a valid mixing weight.
        lam = F.softplus(self.lambda_tilde)  # scalar ≥ 0
        u_t = (u_base * (1.0 + lam * S_bar)).clamp(max=1.0)  # (B, C_M, H, W)

        # ── Memory update: convex combination ───────────────────────────────
        # Standard GRU update: M_t = (1 − u_t)·M_{t-1} + u_t·C̃_t.
        # Both terms have the same shape (B, C_M, H, W).
        M_t = (1.0 - u_t) * M_prev + u_t * C_tilde

        return M_t, u_t


class InnerWMLoop(nn.Module):
    """
    K-step variational inference on M: free-energy gradient descent.

    For k=0..K-1:
        V̂^(k) = decoder( M^(k) )
        E^(k) = V_t − V̂^(k)
        M^(k+1) = M^(k) + ε · ErrBlock( [E^(k), M^(k)] )

    `decoder` is shared with the outer step (passed in at forward time, not
    owned by this module) so that gradient flows through the same parameters
    K+1 times per env step.

    Args
    ----
    memory_channels  : C_M (default 16)
    feature_channels : C_V (default 32)
    K                : number of inner iterations (default 2; one Friston-style
                       gradient step on the variational free energy F per iter,
                       so K iterations buy K refinement steps within one env step)
    epsilon          : step size for the inner update (default 0.1)
    """

    def __init__(
        self,
        memory_channels: int = 16,
        feature_channels: int = 32,
        K: int = 2,
        epsilon: float = 0.1,
        gn_groups: int = 8,
    ) -> None:
        super().__init__()
        if memory_channels % gn_groups != 0:
            raise ValueError(
                f"memory_channels ({memory_channels}) must be divisible by "
                f"gn_groups ({gn_groups})"
            )

        self.K = int(K)
        self.epsilon = float(epsilon)
        self.memory_channels = memory_channels
        self.feature_channels = feature_channels

        # ErrBlock: takes [E, M], outputs an update direction in M-space.
        # First conv: maps (C_V + C_M) → C_M; GN + GELU; second conv refines.
        c_in = feature_channels + memory_channels
        self.conv1 = nn.Conv2d(c_in, memory_channels, kernel_size=3, padding=1)
        self.gn1 = nn.GroupNorm(gn_groups, memory_channels)
        self.conv2 = nn.Conv2d(memory_channels, memory_channels, kernel_size=3, padding=1)

        # Init: Kaiming for the first conv; zero-init the second conv so that
        # at random init the inner loop is the *identity* (no update). This way,
        # untrained inner iterations don't blow up the memory state.
        nn.init.kaiming_uniform_(self.conv1.weight, a=0, mode="fan_in", nonlinearity="relu")
        nn.init.zeros_(self.conv1.bias)
        nn.init.zeros_(self.conv2.weight)
        nn.init.zeros_(self.conv2.bias)

    def forward(
        self,
        M_t: torch.Tensor,
        V_t: torch.Tensor,
        decoder: nn.Module,
    ) -> torch.Tensor:
        """
        M_t     : (B, C_M, H, W)  memory after the GRU update at step t (== M_t^(0))
        V_t     : (B, C_V, H, W)  bottom-up features (held fixed across iterations)
        decoder : the GenerativeDecoder used for V̂ — passed in to share params

        Returns
        -------
        M_t^(K) : (B, C_M, H, W)  memory after K inner-loop iterations
        """
        if self.K == 0:
            return M_t

        for _k in range(self.K):
            # Top-down prediction at the current iterate.
            V_hat_k = decoder(M_t)  # (B, C_V, H, W)

            # Prediction error at the current iterate.
            E_k = V_t - V_hat_k  # (B, C_V, H, W)

            # ErrBlock( [E^(k), M^(k)] ): update direction in M-space.
            # We feed both E (the gradient direction, up to Jacobian) and M
            # (the current iterate) so the block can learn a state-dependent
            # step direction rather than a pure error-following update.
            cat_in = torch.cat([E_k, M_t], dim=1)  # (B, C_V+C_M, H, W)
            update = self.conv2(F.gelu(self.gn1(self.conv1(cat_in))))  # (B, C_M, H, W)

            # Perturbative step: M ← M + ε·update. Equivalent to
            # M ← M − ε·∇_M F under the variational interpretation.
            M_t = M_t + self.epsilon * update

        return M_t

    @torch.no_grad()
    def diagnose_contraction(
        self,
        M_t: torch.Tensor,
        V_t: torch.Tensor,
        decoder: nn.Module,
    ) -> torch.Tensor:
        """
        Diagnostic: report ‖M^(k+1) − M^(k)‖_F for k=0..K-1 on a single batch.

        Useful for verifying the Banach-contraction property: under the
        variational-inference reading of the inner loop, the per-iteration
        residual should decay geometrically (each step reduces F by a
        constant factor when ε is small enough). See `tests/test_inner_wm.py`.

        Returns
        -------
        residuals : (K,)  per-iteration L2 norm of the update step.
        """
        residuals = torch.zeros(self.K, device=M_t.device)
        for k in range(self.K):
            V_hat_k = decoder(M_t)
            E_k = V_t - V_hat_k
            cat_in = torch.cat([E_k, M_t], dim=1)
            update = self.conv2(F.gelu(self.gn1(self.conv1(cat_in))))
            step = self.epsilon * update
            residuals[k] = step.norm()
            M_t = M_t + step
        return residuals
