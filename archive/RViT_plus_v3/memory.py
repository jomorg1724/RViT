"""
GridCell RNN cell — conv attention candidate + attractor-settling memory compute.

Per timestep the cell runs three stages:

    Stage 1 — Conv-attention candidate. The `FeedbackTransformer` (see
    `attention.py`) takes Z = z_t and a list of recurrent / cross-layer
    sources via feedback_list, gates Z against them (per Q/K/V), runs the
    V3 multi-head co-located gated attention, and emits a refined spatial
    tensor `tilde_C` of the same shape as Z.

    Stage 2 — Gated evidence write (LSTM-style).
        C_0 = (1 − u) ⊙ C_{t-1} + u ⊙ tilde_C
        u   = σ( Conv3x3( cat(z_t, C_{t-1}) ) )
    This writes the new evidence into the maintained state, seeding the
    recurrent dynamics below.

    Stage 3 — Attractor-settling memory compute (the V3 memory change).
    The maintained state is no longer a passive register: it is transformed
    by K micro-steps of a leaky recurrent relaxation toward a learned
    attractor, with GroupNorm normalization after every step.
        for k in 1..K:
            C ← C + η ⊙ ( −C + R(C) )          # leaky relaxation
            C ← GroupNorm(C)                    # normalize the sum each step
        C_new = C
    where R(C) = Conv3x3 → GELU → Conv3x3 is a recurrent map SHARED across the
    K micro-steps (so this is genuine recurrent dynamics, not K independent
    layers), and η ∈ (0,1)^C is a per-channel learnable step size.

Why Stage 3 (neuroscience)
--------------------------
Working memory is active manipulation, not storage (`miller_cohen2001_pfc_function`,
`goldman_rakic1995_cellular_wm`, `desposito_postle2015_wm_neuroscience`,
`stokes2015_activity_silent_wm`). The computation is carried by recurrent
attractor dynamics: context-dependent selection + integration in PFC
(`mante2013_context_dependent_pfc`), bump/line attractors (Compte et al. 2000),
and — fittingly for a "GridCell" RNN — the continuous-attractor model of grid
cells (Burak & Fiete 2009), where the recurrent connectivity literally computes
path integration. Stage 3 gives each maintained state K steps of such dynamics
to denoise / pattern-complete / transform the held evidence. The per-step
GroupNorm (`reynolds_heeger2009_normalization`, divisive normalization as a
canonical cortical computation) keeps the settling bounded so gradients stay
controlled across the 29-step episode.

This combines options B (gated evidence write), C (attractor settling, K≈2),
and D (normalization) from the V3 memory-design discussion. The state shape is
unchanged: (B, state_channels, H, W).

All convolutions in this module are 3×3 with padding=1 — no 1×1 convs.
"""
from __future__ import annotations

from typing import List, Optional

import torch
import torch.nn as nn

try:
    from .attention import FeedbackTransformer
except ImportError:  # pragma: no cover
    from attention import FeedbackTransformer  # type: ignore[no-redef]


def _gn_groups_for(channels: int) -> int:
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


class GridCellRNN_LSTM(nn.Module):
    """Conv-attention recurrent cell with an attractor-settling memory compute.

    Args
    ----
    in_channels       : channels of the bottom-up input z_t.
                        Must equal `state_channels` (the attention block's
                        Z input AND output use the same channel count).
    state_channels    : channels of the hidden state C_t. Also = d_model
                        of the internal attention block.
    grid_h, grid_w    : spatial dims of the recurrent state grid.
    n_heads           : attention head count (default 32). The attention block's
                        GroupNorm group count is decoupled from this.
    n_feedback        : number of EXTERNAL (cross-layer) feedback sources
                        expected at forward() time. The cell's own C_prev
                        is always added as one additional internal source,
                        so the attention block's `c_feedback` is sized to
                        (1 + n_feedback) · state_channels.
    forget_gate_bias  : update-gate bias (default 0.0 → σ(0)=0.5 baseline).
    mem_compute_steps : K — number of attractor-settling micro-steps in
                        Stage 3 (default 2). Set 0 to disable Stage 3 (the
                        cell then reduces to the gated-register update).
    """

    def __init__(
        self,
        in_channels: int,
        state_channels: int,
        grid_h: int,
        grid_w: int,
        n_heads: int = 32,
        n_feedback: int = 0,
        forget_gate_bias: float = 0.0,
        mem_compute_steps: int = 2,
    ) -> None:
        super().__init__()
        if in_channels != state_channels:
            raise ValueError(
                f"in_channels ({in_channels}) must equal state_channels "
                f"({state_channels}) — the conv-attention block uses a "
                "single d_model for Z input and output."
            )
        self.in_channels = in_channels
        self.state_channels = state_channels
        self.grid_h = grid_h
        self.grid_w = grid_w
        self.n_heads = n_heads
        self.n_feedback = n_feedback
        self.mem_compute_steps = int(mem_compute_steps)

        # ── Update gate: σ(Conv3x3(cat(z, C_prev))) ─────────────────────
        cat_ch = in_channels + state_channels
        self.conv_update = nn.Conv2d(cat_ch, state_channels, kernel_size=3, padding=1, bias=True)
        with torch.no_grad():
            self.conv_update.bias.fill_(forget_gate_bias)

        # ── Conv-attention block ────────────────────────────────────────
        c_feedback = (1 + n_feedback) * state_channels
        self.ft = FeedbackTransformer(
            d_model=state_channels,
            c_feedback=c_feedback,
            n_heads=n_heads,
            n_feedback=1 + n_feedback,   # legacy arg, informational only
        )

        # ── Stage 3: attractor-settling memory compute (B + C + D) ──────
        # Recurrent map R(C) = Conv3x3 → GELU → Conv3x3, SHARED across the K
        # micro-steps (genuine recurrent dynamics). GroupNorm normalizes the
        # state after every relaxation step. η is a per-channel learnable step
        # size in (0,1) via sigmoid(raw); raw=0 → η=0.5.
        if self.mem_compute_steps > 0:
            self.mem_rec1 = nn.Conv2d(state_channels, state_channels, kernel_size=3, padding=1, bias=True)
            self.mem_rec2 = nn.Conv2d(state_channels, state_channels, kernel_size=3, padding=1, bias=True)
            self.mem_act = nn.GELU()
            self.mem_norm = nn.GroupNorm(_gn_groups_for(state_channels), state_channels)
            self.mem_eta_raw = nn.Parameter(torch.zeros(1, state_channels, 1, 1))
            # Init the recurrent map small so settling is ~identity-up-to-norm
            # at the start of training (won't destroy the gated state at init).
            for conv in (self.mem_rec1, self.mem_rec2):
                nn.init.xavier_uniform_(conv.weight, gain=0.5)
                nn.init.zeros_(conv.bias)

    def _settle(self, C: torch.Tensor) -> torch.Tensor:
        """K micro-steps of leaky attractor relaxation + per-step GroupNorm."""
        eta = torch.sigmoid(self.mem_eta_raw)          # (1, C, 1, 1) ∈ (0,1)
        for _ in range(self.mem_compute_steps):
            R = self.mem_rec2(self.mem_act(self.mem_rec1(C)))   # recurrent map R(C)
            C = C + eta * (-C + R)                              # relaxation toward attractor
            C = self.mem_norm(C)                                # normalize the sum (D)
        return C

    def forward(
        self,
        z_t: torch.Tensor,
        C_prev: torch.Tensor,
        feedback_list: Optional[List[torch.Tensor]] = None,
        attn_bias: Optional[torch.Tensor] = None,
    ) -> dict:
        """
        z_t           : (B, in_channels, H, W)   bottom-up input (= state_channels)
        C_prev        : (B, state_channels, H, W) previous hidden state
        feedback_list : list of (B, state_channels, H, W) from OTHER layers,
                        already spatially aligned to this layer's grid.
                        Length must equal n_feedback.
        attn_bias     : legacy microstim hook — accepted but not used.

        Returns dict:
            C_new   : (B, state_channels, H, W) new hidden state (post-settling)
            attn    : (B, n_heads, H, W) per-head sigmoid gate maps
            tilde_C : (B, state_channels, H, W) raw conv-attention candidate
            C_write : (B, state_channels, H, W) gated evidence write (pre-settling)
            u_gate  : (B, state_channels, H, W) per-cell update-gate values
            eta     : (1, state_channels, 1, 1) settling step size (or None)
            q_gate, k_gate, v_gate : Z↔H fusion gates from the attention block
        """
        if z_t.dim() != 4 or C_prev.dim() != 4:
            raise ValueError("z_t and C_prev must be 4D (B, C, H, W)")
        if z_t.shape[-2:] != (self.grid_h, self.grid_w):
            raise ValueError(
                f"z_t HW {tuple(z_t.shape[-2:])} != expected ({self.grid_h}, {self.grid_w})"
            )
        if C_prev.shape[1] != self.state_channels:
            raise ValueError(
                f"C_prev channels {C_prev.shape[1]} != state_channels {self.state_channels}"
            )

        # ── All recurrent / cross-layer sources concatenated downstream ──
        all_feedback: List[torch.Tensor] = [C_prev]
        if feedback_list is not None:
            for fb in feedback_list:
                if fb.shape != C_prev.shape:
                    raise ValueError(
                        f"feedback shape {tuple(fb.shape)} must match this "
                        f"layer's state shape {tuple(C_prev.shape)}"
                    )
                all_feedback.append(fb)
        # Pad missing slots with zeros to keep the concat shape stable.
        while len(all_feedback) < 1 + self.n_feedback:
            all_feedback.append(torch.zeros_like(C_prev))

        # ── Stage 1: conv attention → candidate tilde_C ─────────────────
        ft_out = self.ft(z_t, feedback_list=all_feedback, attn_bias=attn_bias)
        tilde_C = ft_out["out"]                                # (B, C, H, W)

        # ── Stage 2: gated evidence write (B) ───────────────────────────
        # C_write = (1 − u) ⊙ C_{t-1} + u ⊙ tilde_C
        u = torch.sigmoid(self.conv_update(torch.cat([z_t, C_prev], dim=1)))
        C_write = (1.0 - u) * C_prev + u * tilde_C

        # ── Stage 3: attractor-settling memory compute (C + D) ──────────
        if self.mem_compute_steps > 0:
            C_new = self._settle(C_write)
            eta = torch.sigmoid(self.mem_eta_raw)
        else:
            C_new = C_write
            eta = None

        return {
            "C_new":   C_new,
            "attn":    ft_out["attn"],                # (B, n_heads, H, W) per-head gate
            "attn_spatial": ft_out["attn_spatial"],   # (B, C, H, W) σ(A)·V residual
            "v_post_norm":  ft_out["v_post_norm"],    # (B, C, H, W) post-norm V
            "tilde_C": tilde_C,
            "C_write": C_write,
            "u_gate":  u,
            "eta":     eta,
            "q_gate":  ft_out["q_gate"],
            "k_gate":  ft_out["k_gate"],
            "v_gate":  ft_out["v_gate"],
            # Back-compat aliases for downstream code that previously read
            # sip_candidate / ft_out.
            "sip_candidate": tilde_C,           # no separate SIP stage now
            "ft_out": tilde_C,
        }
