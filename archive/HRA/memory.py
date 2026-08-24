"""
GridCell RNN — per-layer recurrent cell that combines a convolutional GRU with
the Feedback Transformer for cross-grid attention and cross-layer integration.

Per the architectural-program thread §2:

    Stage one — spatially-independent processing (SIP). Each grid cell is
    processed independently to produce an update proposal using only the
    previous grid state and the current input at that cell. Analog of the
    LSTM candidate cell.

    Stage two — inter-cell and inter-grid integration. The Feedback
    Transformer takes the proposal as input, treats each grid cell as a
    token, and integrates feedback from an arbitrary set of other GridCell
    RNN states (parallel, deeper, shallower). The final update is a gated
    sum of the SIP proposal and the FT output.

The clean separation between SIP and FT integration is the architectural
reason the system can scale to many memory layers without combinatorial
blowup. SIP handles within-state computation in parallel; FT handles
between-state communication.

Notes on the ConvGRU base
-------------------------
Ballas et al. 2016 ConvGRU. Reset and update gates are 3×3 convs (preserves
spatial topography). Update-gate bias init = -1.0 (chrono-init trick of
Tallec & Ollivier 2018) so the cell's effective time constant is multiple
environment steps regardless of input magnitude.

Forward state shape: (B, C, H, W) for all internal tensors. The FT operates
on the flattened token sequence (B, H*W, C); the cell reshapes around the FT
call internally so the caller never needs to think about the layout.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .attention import FeedbackTransformer


def _gn_groups_for(channels: int) -> int:
    """Pick a GroupNorm group count that divides `channels` and is ≤ 8."""
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


class GridCellRNNCell(nn.Module):
    """
    One layer of HRA's hierarchical recurrent stack.

    Maintains a spatially-arranged hidden state C^{(t)} ∈ ℝ^{B × n_C × H × W}.
    Each forward step performs:

        1. SIP — pure-conv ConvGRU update proposal from (input_t, C^{(t-1)}).
        2. FT  — Feedback Transformer over flattened grid cells, with feedback
                 from this layer's previous state plus any cross-layer
                 feedback projections supplied by the caller.
        3. Gated mix — final C^{(t)} = (1-u) ⊙ C^{(t-1)} + u ⊙ (sip_proposal + ft_residual).

    Args
    ----
    in_channels       : channels of the bottom-up input z_t at this layer
    state_channels    : channels of the hidden state C_t (n_C for this layer)
    grid_h, grid_w    : spatial dims of the grid
    n_heads           : attention heads in the FT (default 4)
    n_feedback        : how many *external* feedback sources to expect at
                        forward() time. Self-recurrent feedback (C^{(t-1)})
                        is always present in addition.
    update_gate_bias  : chrono-init bias on the update gate (default 0.0,
                        σ(0)=0.5 update rate). The PRISM-v1 default of -1.0
                        is too sticky for our multi-layer task: signal that
                        does reach a cell gets damped by σ(-1)≈0.27 per
                        step, and over 3 stacked cells with n_FR=5 inner
                        iterations the cell freezes at its fixed point.
                        See `HRA/analysis/deep_dive.py` post-mortem.
    error_gated_update : if True (default), use PRISM v1's surprise-amplified
                        update gate: u_eff = clamp(u_base · (1 + λ · Ŝ_t),
                        max=1) where Ŝ_t = |C̃_t − C_prev| normalised to
                        [0,1] per cell. Amplifies updates exactly when the
                        candidate differs from prior state — the cell can't
                        sit at a fixed point through a stimulus change.
    """

    def __init__(
        self,
        in_channels: int,
        state_channels: int,
        grid_h: int,
        grid_w: int,
        n_heads: int = 4,
        n_feedback: int = 0,
        update_gate_bias: float = 0.0,
        error_gated_update: bool = True,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.state_channels = state_channels
        self.grid_h = grid_h
        self.grid_w = grid_w
        self.n_feedback = n_feedback
        self.n_heads = n_heads

        cat_ch = in_channels + state_channels  # conv input for gates

        # ConvGRU gates (Ballas et al. 2016).
        self.conv_reset = nn.Conv2d(cat_ch, state_channels, kernel_size=3, padding=1, bias=True)
        self.conv_update = nn.Conv2d(cat_ch, state_channels, kernel_size=3, padding=1, bias=True)
        self.conv_candidate = nn.Conv2d(cat_ch, state_channels, kernel_size=3, padding=1, bias=True)

        # Chrono-init: bias update gate to ~σ(-1) ≈ 0.27 at init.
        nn.init.constant_(self.conv_update.bias, update_gate_bias)

        # Per-layer GroupNorm before the FT helps it cope with the conv proposal
        # output scale during early training.
        gn_groups = _gn_groups_for(state_channels)
        self.gn_pre_ft = nn.GroupNorm(gn_groups, state_channels)

        # Self-recurrent feedback is always present, so +1 to the FT's source count.
        self.ft = FeedbackTransformer(
            d_model=state_channels,
            n_heads=n_heads,
            n_feedback=1 + n_feedback,
        )

        # A small residual scale lets the FT output start near identity
        # (gated mix → conv proposal dominates initially).
        self.ft_residual_scale = nn.Parameter(torch.zeros(1))

        # Error-gated update parameter. softplus(λ̃) ≥ 0 keeps the gate-boost
        # non-negative. Initialise λ̃ such that softplus(λ̃) ≈ 1, so at
        # surprise = 1.0 (max), the update gate is boosted by 2x and clamped
        # to 1. At surprise = 0 (steady state), the update gate is unchanged.
        # Matches PRISM v1's `ErrorGatedConvGRU` (Prism/memory.py §1).
        self.error_gated_update = error_gated_update
        if error_gated_update:
            self.error_lambda_tilde = nn.Parameter(torch.tensor(0.5413))  # softplus(0.54) ≈ 1.0

    def forward(
        self,
        z_t: torch.Tensor,
        C_prev: torch.Tensor,
        feedback_list: Optional[List[torch.Tensor]] = None,
    ) -> dict:
        """
        z_t           : (B, in_channels, H, W) — bottom-up input at this layer
        C_prev        : (B, state_channels, H, W) — previous hidden state
        feedback_list : optional list of (B, state_channels, H, W) feedback
                        tensors from OTHER layers, already spatially aligned to
                        this layer's grid (H, W). Length must equal n_feedback.

        Returns dict with:
            C_new   : (B, state_channels, H, W) — new hidden state
            attn    : (B, n_heads, N, N) — FT attention map (N = H*W)
            u_gate  : (B, state_channels, H, W) — update gate (interpretability)
            r_gate  : (B, state_channels, H, W) — reset gate (interpretability)
            sip     : (B, state_channels, H, W) — SIP candidate (interpretability)
        """
        if z_t.dim() != 4 or C_prev.dim() != 4:
            raise ValueError("z_t and C_prev must be 4D (B,C,H,W)")
        if z_t.shape[-2:] != (self.grid_h, self.grid_w):
            raise ValueError(
                f"z_t spatial dims {tuple(z_t.shape[-2:])} != expected ({self.grid_h},{self.grid_w})"
            )
        if C_prev.shape[1] != self.state_channels:
            raise ValueError(
                f"C_prev channels {C_prev.shape[1]} != state_channels {self.state_channels}"
            )

        # --- Stage 1: ConvGRU SIP ---
        cat = torch.cat([z_t, C_prev], dim=1)  # (B, in_C + state_C, H, W)
        r = torch.sigmoid(self.conv_reset(cat))
        u_base = torch.sigmoid(self.conv_update(cat))
        cand_input = torch.cat([z_t, r * C_prev], dim=1)
        c_tilde = torch.tanh(self.conv_candidate(cand_input))  # SIP candidate

        # Error-gated update: amplify update gate where the candidate
        # disagrees with the current state. PRISM v1 used prediction error
        # against a top-down decoder; we use the cell's own innovation as a
        # cell-local approximation. Normalised per-cell so the boost factor
        # lives in [0, 1+softplus(λ̃)].
        if self.error_gated_update:
            innovation = (c_tilde - C_prev).abs()                          # (B, state_C, H, W)
            denom = innovation.amax(dim=(-2, -1), keepdim=True).clamp(min=1e-6)
            saliency = innovation / denom                                  # per-(batch, channel) ∈ [0,1]
            boost = 1.0 + F.softplus(self.error_lambda_tilde) * saliency
            u = (u_base * boost).clamp(max=1.0)
        else:
            u = u_base

        # --- Stage 2: Feedback Transformer over flattened grid cells ---
        # Use the SIP candidate as the "sensory" input to the FT; this lets
        # the FT decide how to spatially redistribute the SIP proposal in light
        # of feedback.
        B, C, H, W = c_tilde.shape
        N = H * W

        # Normalise and reshape to tokens.
        sensory_tokens = self.gn_pre_ft(c_tilde).permute(0, 2, 3, 1).reshape(B, N, C)

        # Always include self-recurrent feedback (the previous hidden state).
        all_feedback = [C_prev.permute(0, 2, 3, 1).reshape(B, N, C)]
        if feedback_list is not None:
            for fb in feedback_list:
                if fb.shape != C_prev.shape:
                    raise ValueError(
                        f"Cross-layer feedback shape {tuple(fb.shape)} must match "
                        f"this layer's state shape {tuple(C_prev.shape)}; align before passing in."
                    )
                all_feedback.append(fb.permute(0, 2, 3, 1).reshape(B, N, C))

        ft_out = self.ft(sensory_tokens, feedback_list=all_feedback)
        ft_tokens = ft_out["out"]  # (B, N, C)
        ft_residual = ft_tokens.reshape(B, H, W, C).permute(0, 3, 1, 2).contiguous()

        # Apply the FT as a learnable residual on top of the SIP candidate.
        # ft_residual_scale starts at zero, so initial behaviour reduces to
        # plain ConvGRU. The model learns to lift this scale as the FT starts
        # contributing useful information.
        c_combined = c_tilde + self.ft_residual_scale * ft_residual

        # --- Stage 3: Gated mix ---
        C_new = (1.0 - u) * C_prev + u * c_combined

        return {
            "C_new": C_new,
            "attn": ft_out["attn"],   # (B, n_heads, N, N) — exposed for analysis
            "u_gate": u,              # (B, state_C, H, W)
            "r_gate": r,              # (B, state_C, H, W)
            "sip": c_tilde,           # (B, state_C, H, W) — pre-FT candidate
            "ft_residual": ft_residual,
        }
