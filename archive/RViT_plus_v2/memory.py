"""
GridCell RNN cell — conv-spatial attention block + LSTM-style update gate.

After the conv-recurrent attention redesign (see `attention.py`), the cell
is much thinner:

    Stage 1 — Conv-attention candidate. The new `FeedbackTransformer` takes
    Z = z_t and a list of recurrent / cross-layer sources via feedback_list.
    Internally it gates Z against the concatenation of those sources (per
    Q/K/V), runs 4-head channel attention, and emits a refined spatial
    tensor `tilde_C` of the same shape as Z. Z↔H fusion happens inside the
    attention block; no separate SIP candidate stage is needed any more.

    Stage 2 — LSTM-style update-gate mix.
        C_new = (1 − u) ⊙ C_{t-1} + u ⊙ tilde_C
        u     = σ( Conv3x3( cat(z_t, C_{t-1}) ) )
    The attention block is in the gradient path of C_new through u · tilde_C
    so there's no zero-multiplied residual side-channel.

All convolutions in this module are 3×3 with padding=1 — no 1×1 convs.

Departures from the prior (FT + SIP candidate) version
------------------------------------------------------
 * SIP candidate (1×1 conv on cat(z, C_prev) → tanh) removed: the new
   attention module handles Z↔H fusion via gated 3×3 Q/K/V conv projections.
 * Pre-attention GroupNorm removed: the new attention module has internal
   GroupNorms on Q, K, V.
 * Learned positional embedding removed: channel attention is not
   permutation-equivariant across grid cells once 3×3 convs are involved,
   so the explicit pos_emb is no longer needed.
 * Update-gate conv switched from 1×1 to 3×3 (no 1×1 convs anywhere, per
   the redesign spec).
 * `attn_bias` (microstim hook) is accepted but a no-op — channel attention
   doesn't have a spatial attention map to bias.
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
    """Conv-attention recurrent cell with spatial grid state.

    Args
    ----
    in_channels       : channels of the bottom-up input z_t.
                        Must equal `state_channels` (the attention block's
                        Z input AND output use the same channel count).
    state_channels    : channels of the hidden state C_t. Also = d_model
                        of the internal attention block.
    grid_h, grid_w    : spatial dims of the recurrent state grid.
    n_heads           : channel-attention head count (default 4). Also the
                        GroupNorm group count inside the attention block.
    n_feedback        : number of EXTERNAL (cross-layer) feedback sources
                        expected at forward() time. The cell's own C_prev
                        is always added as one additional internal source,
                        so the attention block's `c_feedback` is sized to
                        (1 + n_feedback) · state_channels.
    forget_gate_bias  : LSTM-style update-gate bias (default 0.0 → σ(0)=0.5
                        balanced baseline).
    """

    def __init__(
        self,
        in_channels: int,
        state_channels: int,
        grid_h: int,
        grid_w: int,
        n_heads: int = 4,
        n_feedback: int = 0,
        forget_gate_bias: float = 0.0,
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

        # ── Update gate: σ(Conv3x3(cat(z, C_prev))) ─────────────────────
        # Per-cell mixing weight in [0, 1]. 3×3 same-same (per spec).
        # Output channels = state_channels so we can do element-wise gating
        # against C_prev and tilde_C.
        cat_ch = in_channels + state_channels
        self.conv_update = nn.Conv2d(cat_ch, state_channels, kernel_size=3, padding=1, bias=True)
        with torch.no_grad():
            self.conv_update.bias.fill_(forget_gate_bias)

        # ── Conv-attention block ────────────────────────────────────────
        # Z = z_t (B, state_channels, H, W).
        # H = concat([C_prev, *external_feedback]) along channels.
        # All sources are assumed to be at state_channels (the encoder
        # ensures this via the ascend/descend projections).
        c_feedback = (1 + n_feedback) * state_channels
        self.ft = FeedbackTransformer(
            d_model=state_channels,
            c_feedback=c_feedback,
            n_heads=n_heads,
            n_feedback=1 + n_feedback,   # legacy arg, informational only
        )

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
        attn_bias     : legacy microstim hook — accepted but not used by the
                        channel-attention block.

        Returns dict:
            C_new   : (B, state_channels, H, W) new hidden state
            attn    : (B, state_channels, 1, 1) channel-attention weights
            tilde_C : (B, state_channels, H, W) raw conv-attention output
            u_gate  : (B, state_channels, H, W) per-cell update-gate values
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
        # The new attention block expects the feedback list to be concat'd
        # along channels internally, with a FIXED total channel count of
        # (1 + n_feedback) · state_channels. We always pass C_prev first,
        # then any external feedback. If fewer external feedback sources
        # are provided than n_feedback, pad with zero tensors so the
        # attention block's c_feedback expectation is satisfied.
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

        # ── Stage 1: conv attention → tilde_C ───────────────────────────
        ft_out = self.ft(z_t, feedback_list=all_feedback, attn_bias=attn_bias)
        tilde_C = ft_out["out"]                                # (B, C, H, W)

        # ── Stage 2: LSTM-style update-gate mix ────────────────────────
        # C_new = (1 − u) ⊙ C_{t-1} + u ⊙ tilde_C
        # u = σ(Conv3x3(cat(z_t, C_{t-1}))) — 3×3 same-same per redesign spec.
        u = torch.sigmoid(self.conv_update(torch.cat([z_t, C_prev], dim=1)))
        C_new = (1.0 - u) * C_prev + u * tilde_C

        return {
            "C_new":   C_new,
            "attn":    ft_out["attn"],                # (B, C, 1, 1) channel softmax
            "attn_spatial": ft_out["attn_spatial"],   # (B, C, H, W) spatial residual
            "v_post_norm":  ft_out["v_post_norm"],    # (B, C, H, W) post-norm V
            "tilde_C": tilde_C,
            "u_gate":  u,
            "q_gate":  ft_out["q_gate"],
            "k_gate":  ft_out["k_gate"],
            "v_gate":  ft_out["v_gate"],
            # Back-compat aliases for downstream code that previously read
            # sip_candidate / ft_out.
            "sip_candidate": tilde_C,           # no separate SIP stage now
            "ft_out": tilde_C,
        }
