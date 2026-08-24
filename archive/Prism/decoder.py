"""
Top-down generative decoder g(M_{t-1}) → V̂_t and the derived prediction-error map.

Architecture writeup: see `../docs/THESIS.md` §3 (Methods).

The conceptual heart of PRISM
------------------------------
The architecture maintains a generative model of the perceptual input:

    p(V_t | M_t) = 𝒩(V_t ; g(M_t), σ² I)        # Gaussian likelihood
    p(M_t | M_{t-1}) = δ(M_t − f(M_{t-1}, V_t))  # deterministic transition (the GRU)

The decoder g is the only learned component of the likelihood. It produces
a top-down prediction V̂_t that, ideally, equals V_t whenever the world is
following memory's expectations.

The prediction-error volume
    E_t  =  V_t  −  V̂_t                ∈ ℝ^(B,C_V,H,W)
is the variational free-energy gradient direction (up to a constant), and
its per-location norm
    S_t(i,j)  =  √( (1/C_V) Σ_c E_{t,c,i,j}² )    ∈ ℝ^(B,1,H,W)
is the architecture's interpretable saliency map. This map has *no learned
parameters of its own*: it is a derived quantity. Reads as "where is the
model's generative prior failing to explain the input right now?"

Why this is principled (Friston 2010; Rao & Ballard 1999)
----------------------------------------------------------
Variational free energy with point-estimate posterior reduces to
    F_t = − log p(V_t | M_t) + const  ∝  ‖V_t − g(M_t)‖²
Minimising F_t with respect to model parameters is exactly the predictive-
coding objective; minimising it with respect to M_t (the inner WM loop in
memory.py) is exactly Friston's iterative variational inference.

Why this is bitter-lesson compliant
------------------------------------
The only inductive bias added is "build a generative model and compare to
bottom-up." That is universal across temporal sensory environments. Nothing
about Gabors, cues, colours, or change detection is encoded.

Initialisation: V̂_t ≈ 0 at random init
---------------------------------------
We initialise the decoder so that its output is near zero. This means
E_t ≈ V_t initially: the network starts maximally surprised by everything,
which is the right initial condition for a system about to learn its
generative model. Achieved by zeroing the *final* conv's weights and
setting its bias to zero (the inner conv keeps default Kaiming init so
gradient flows immediately).

Complexity / params
-------------------
Time:   O(B · H · W · (C_M·C_M·9 + C_M·C_V·9))
Space:  O(B · C_V · H · W)  for V̂_t and E_t.
Params: 16·16·9 + 16·32·9 + 32 = 2,304 + 4,608 + 32 = 6,944 (plus norms).
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class GenerativeDecoder(nn.Module):
    """
    Two-layer conv decoder mapping memory state M to predicted features V̂.

    Architecture:
        M ∈ (B, C_M, H, W)
          → Conv_{3×3}^{C_M → C_M}, GroupNorm, GELU
          → Conv_{3×3}^{C_M → C_V}, (no nonlinearity on output — features can be ±)
          = V̂ ∈ (B, C_V, H, W)

    Args
    ----
    memory_channels  : C_M (default 16)
    feature_channels : C_V (default 32, must match V1Stem.out_channels)
    """

    def __init__(
        self,
        memory_channels: int = 16,
        feature_channels: int = 32,
        gn_groups: int = 8,
    ) -> None:
        super().__init__()
        if memory_channels % gn_groups != 0:
            raise ValueError(
                f"memory_channels ({memory_channels}) must be divisible by "
                f"gn_groups ({gn_groups})"
            )

        # Hidden conv: standard Kaiming-relu init.
        self.conv1 = nn.Conv2d(memory_channels, memory_channels, kernel_size=3, padding=1)
        self.gn1 = nn.GroupNorm(gn_groups, memory_channels)

        # Output conv: zeroed weights + zero bias for V̂ ≈ 0 at init.
        # We do *not* add a final nonlinearity because V_t (the regression target)
        # can take negative values after the GELU+GroupNorm in the V1 stem.
        self.conv2 = nn.Conv2d(memory_channels, feature_channels, kernel_size=3, padding=1)

        # Init scheme:
        # - conv1 keeps default Kaiming (set explicitly below to be deterministic).
        # - conv2 is zero-init so V̂ ≈ 0 initially. This means E ≈ V at step 0,
        #   so L_PC ≈ ‖V‖² and the decoder receives a strong learning signal.
        nn.init.kaiming_uniform_(self.conv1.weight, a=0, mode="fan_in", nonlinearity="relu")
        nn.init.zeros_(self.conv1.bias)
        nn.init.zeros_(self.conv2.weight)
        nn.init.zeros_(self.conv2.bias)

        self.memory_channels = memory_channels
        self.feature_channels = feature_channels

    def forward(self, M: torch.Tensor) -> torch.Tensor:
        """
        M : (B, C_M, H, W)

        Returns
        -------
        V_hat : (B, C_V, H, W)
        """
        if M.shape[1] != self.memory_channels:
            raise ValueError(
                f"GenerativeDecoder expects M with {self.memory_channels} channels; "
                f"got {M.shape[1]}"
            )

        # Hidden representation: Conv → GN → GELU. Same spatial dims throughout.
        h = F.gelu(self.gn1(self.conv1(M)))

        # Output projection: linear (no nonlinearity), so V̂ can be negative.
        v_hat = self.conv2(h)

        return v_hat


class PixelDecoder(nn.Module):
    """
    Top-down decoder mapping memory state M to a *raw-pixel* prediction x̂ of
    the next observation. This is the collapse-proof PC target.

    Why this exists (and why GenerativeDecoder alone is not enough)
    ---------------------------------------------------------------
    L_PC = ‖V − g(M)‖² with both V and g(M) learned admits trivial solutions:
    if the V1 stem outputs a near-constant feature map and the feature decoder
    g matches it, L_PC drops to ~0 with zero useful representation. This is
    the same representation-collapse hazard as in BYOL/SimCLR; GroupNorm
    only forces unit variance per group, not informative content.

    Predicting *raw pixels* x cannot collapse: x is determined by the env,
    not the model, so the only way to reduce ‖x − x̂‖² is for the model to
    encode information about x in M. The stem cannot collapse to constant
    output because then M (= GRU(M_prev, P, ...)) would be constant, and
    PixelDecoder(M) could not match arbitrary x.

    Architecture
    ------------
    M ∈ (B, C_M, 12, 12)
      → Conv_{3×3}^{C_M → 16},  GroupNorm, GELU                   (B, 16, 12, 12)
      → bilinear interp to 50×50                                    (B, 16, 50, 50)
      → Conv_{3×3}^{16 → 16},  GroupNorm, GELU                     (B, 16, 50, 50)
      → Conv_{3×3}^{16 → 3},   linear output                        (B,  3, 50, 50)

    The bilinear upsample is a fixed (parameter-free) interpolation; only the
    convs carry learnable weights. We don't use ConvTranspose because:
      (a) bilinear has no checkerboard artefacts,
      (b) we don't need the extra params,
      (c) the model is already cheap and we want to keep it that way.

    Initialisation
    --------------
    The output conv is zero-init'd so x̂ ≈ 0 at random init. Then E_pix ≈ x
    initially: the network starts maximally surprised — the right initial
    condition for a system about to learn its generative model. Mirrors the
    feature-decoder init strategy for the same reason.

    Params (default sizes)
    ----------------------
    16·C_M·9 + 16  +  16·16·9 + 16  +  16·3·9 + 3   ≈   2.5 K to 5 K depending on C_M.
    """

    def __init__(
        self,
        memory_channels: int = 16,
        out_channels: int = 3,
        out_h: int = 50,
        out_w: int = 50,
        hidden_channels: int = 16,
        gn_groups: int = 8,
    ) -> None:
        super().__init__()
        if hidden_channels % gn_groups != 0:
            raise ValueError(
                f"hidden_channels ({hidden_channels}) must be divisible by gn_groups ({gn_groups})"
            )

        self.memory_channels = memory_channels
        self.out_channels = out_channels
        self.out_h = out_h
        self.out_w = out_w

        # Pre-upsample conv: refine the low-res memory before stretching.
        self.conv_pre = nn.Conv2d(memory_channels, hidden_channels, kernel_size=3, padding=1)
        self.gn_pre = nn.GroupNorm(gn_groups, hidden_channels)

        # Post-upsample conv: smooth out interpolation artefacts at full res.
        self.conv_post = nn.Conv2d(hidden_channels, hidden_channels, kernel_size=3, padding=1)
        self.gn_post = nn.GroupNorm(gn_groups, hidden_channels)

        # Output conv: linear (no nonlinearity) so x̂ can take negative values
        # consistent with the env's observation_space (low=-1, high=1).
        # Zero-init so x̂ ≈ 0 at random init.
        self.conv_out = nn.Conv2d(hidden_channels, out_channels, kernel_size=3, padding=1)

        # Init: Kaiming for the hidden convs, zero for the output.
        for c in (self.conv_pre, self.conv_post):
            nn.init.kaiming_uniform_(c.weight, a=0, mode="fan_in", nonlinearity="relu")
            nn.init.zeros_(c.bias)
        nn.init.zeros_(self.conv_out.weight)
        nn.init.zeros_(self.conv_out.bias)

    def forward(self, M: torch.Tensor) -> torch.Tensor:
        """
        M : (B, C_M, H_in, W_in)   typically (B, C_M, 12, 12)

        Returns
        -------
        x_hat : (B, C_out, out_h, out_w)   typically (B, 3, 50, 50)
        """
        if M.shape[1] != self.memory_channels:
            raise ValueError(
                f"PixelDecoder expects M with {self.memory_channels} channels; "
                f"got {M.shape[1]}"
            )

        # Refine at low res first (cheap).
        h = F.gelu(self.gn_pre(self.conv_pre(M)))  # (B, hidden, 12, 12)

        # Bilinear upsample to the target spatial resolution. align_corners=False
        # is the modern PyTorch default and avoids edge artefacts.
        h = F.interpolate(
            h, size=(self.out_h, self.out_w), mode="bilinear", align_corners=False
        )  # (B, hidden, 50, 50)

        # Smooth out interpolation artefacts.
        h = F.gelu(self.gn_post(self.conv_post(h)))  # (B, hidden, 50, 50)

        # Linear output projection. No clamp/tanh: we rely on PC loss to keep
        # x̂ in roughly the same range as x (env's [-1, 1]).
        return self.conv_out(h)  # (B, 3, 50, 50)


def pixel_saliency_map(
    x: torch.Tensor,
    x_hat: torch.Tensor,
    target_h: int,
    target_w: int,
    eps: float = 1e-6,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Compute pixel-space prediction error and a downsampled feature-grid saliency map.

    Parameters
    ----------
    x        : (B, 3, H_pix, W_pix)   raw observation (e.g. (B, 3, 50, 50))
    x_hat    : (B, 3, H_pix, W_pix)   pixel-space top-down prediction
    target_h : H of the feature grid (e.g. 12)
    target_w : W of the feature grid (e.g. 12)
    eps      : small constant for sqrt stability

    Returns
    -------
    E_pix : (B, 3, H_pix, W_pix)        sign-preserving pixel error
    S_t   : (B, 1, target_h, target_w)  feature-grid saliency = adaptive_avg_pool of
        per-pixel error magnitude, scaled to the feature-grid resolution.

    The downsampled S_t is what drives the GRU's error-gated update and is used
    as the pooling weight in the decision readout. We use adaptive_avg_pool
    (not learnable) so the saliency map remains a *derived* signal — there is
    nothing to overfit and nothing to collapse.
    """
    if x.shape != x_hat.shape:
        raise ValueError(
            f"pixel_saliency_map: shape mismatch x={tuple(x.shape)} "
            f"vs x_hat={tuple(x_hat.shape)}"
        )

    E_pix = x - x_hat  # (B, 3, H_pix, W_pix)
    # RMS across channels: keeps magnitudes invariant to channel count.
    pix_sal = (E_pix.pow(2).mean(dim=1, keepdim=True) + eps).sqrt()  # (B, 1, H_pix, W_pix)
    # Downsample to the feature grid for use by the GRU and readout.
    # adaptive_avg_pool2d and mode="area" both crash on MPS when 50 % 12 != 0.
    # Bilinear uses a different kernel path that works for any size ratio on all backends.
    S_t = F.interpolate(pix_sal, size=(target_h, target_w), mode="bilinear", align_corners=False)
    return E_pix, S_t


def prediction_error_map(
    V_t: torch.Tensor,
    V_hat_t: torch.Tensor,
    eps: float = 1e-6,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Compute the prediction-error volume E_t and the per-location saliency map S_t.

    Parameters
    ----------
    V_t     : (B, C_V, H, W)  bottom-up features from the V1 stem
    V_hat_t : (B, C_V, H, W)  top-down generative prediction
    eps     : small constant for numerical stability of the sqrt

    Returns
    -------
    E_t : (B, C_V, H, W)
        Prediction error per channel and location. Sign-preserving — useful
        for the GRU's candidate computation, where we want to feed in the
        *direction* of the error not just its magnitude.

    S_t : (B, 1, H, W)
        Per-location saliency = root-mean-square of E_t across channels.
        This is the *interpretable readout*. S_t ≥ 0 by construction; equals
        0 only where V_t exactly equals V̂_t.

    Mathematical note
    -----------------
    We use root-MEAN-square (not root-sum-square) so that the magnitude of S_t
    is invariant to C_V — a 32-channel and a 64-channel decoder give comparable
    saliency scales. This makes hyperparameter transfer across model widths
    cleaner.

    Numerical stability
    -------------------
    We add eps inside the sqrt's argument to avoid computing sqrt(0) which has
    infinite gradient at zero. eps=1e-6 is far below typical saliency values
    once the decoder has trained for any non-trivial number of steps.
    """
    if V_t.shape != V_hat_t.shape:
        raise ValueError(
            f"prediction_error_map: shape mismatch V_t={tuple(V_t.shape)} "
            f"vs V_hat_t={tuple(V_hat_t.shape)}"
        )
    if V_t.dim() != 4:
        raise ValueError(
            f"prediction_error_map expects 4D inputs (B,C,H,W); got {V_t.dim()}D"
        )

    # E_t = V_t − V̂_t. Sign-preserving prediction error.
    # Shape: (B, C_V, H, W).
    E_t = V_t - V_hat_t

    # S_t = sqrt( mean_c(E_t²) + eps ).
    # mean over channels (dim=1) keeps spatial dims; keepdim → (B, 1, H, W).
    # The +eps is placed *inside* the sqrt to make the gradient finite at E=0.
    S_t = (E_t.pow(2).mean(dim=1, keepdim=True) + eps).sqrt()

    return E_t, S_t
