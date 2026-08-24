"""
Per-channel spatial-attention block for RViT+ V2.

V2 keeps V1's gated Q/K/V fusion (Z↔H concat+conv+sigmoid-gate), GroupNorm,
and conv-FFN block. The change is in the attention computation itself:

  V1 collapses the spatial axis of Q⋅K into a per-channel scalar score, then
  takes a softmax OVER CHANNELS within each head. Each head's "selected"
  channel of V is what gets added to Z. Channel attention.

  V2 does the opposite: per channel c, the attention computation is independent
  of every other channel, and the softmax is OVER SPATIAL POSITIONS within
  that channel:

      scores[b, c, h, w]   =  Q[b, c, h, w] * K[b, c, h, w]
      A[b, c, :, :]        =  softmax_{h, w}( scores[b, c, :, :] )
      attn_out[b, c, h, w] =  A[b, c, h, w] * V[b, c, h, w]

  In other words: every channel is its own attention head, and each channel
  learns its own (H, W) saliency map that picks the spatial position(s) at
  which its V projection gets to contribute. C channels → C separate
  spatial softmaxes.

Why this design
---------------
V1 trained itself into a deterministic channel router — per head, the
softmax-over-channels picked one channel and stuck with it. Useful but no
longer "attention" in any context-dependent sense (see
`research_db/threads/rvit_plus_engineering.md` § "Channel-softmax collapse").
V2 moves the softmax to a different axis, so the failure mode shifts: a
collapsed V2 channel would pick a single spatial cell, which still encodes
where the channel attends. The mechanism cannot become "fully static" the
way V1's channel softmax did, because every (b, t) state produces a fresh
spatial map per channel.

Failure modes to watch for in V2
--------------------------------
- Per-channel softmaxes all collapsing to the SAME spatial cell (degenerate
  attention map — every channel routes to the same pixel). Empirically
  detectable via the cross-channel variance of A's argmax.
- Per-channel softmaxes saturating (peak ≈ 1 on one cell, ≈ 0 elsewhere)
  uniformly across channels. Detectable via the mean per-channel softmax
  entropy compared against log(H·W).

Departures from V1's attention.py
---------------------------------
* New score axis: per-spatial-position element-wise Q*K instead of
  per-head global sum.
* New softmax axis: spatial (H·W) per channel, instead of channel-within-head.
* `attn` output shape changed from (B, C, 1, 1) to (B, C, H, W) — A IS the
  spatial map now.
* `attn_spatial` retained for back-compatibility with the diagnostic scripts,
  and is literally `A · V` (same as V1's semantic).
* Gated Z↔H fusion (`q_gate`, `k_gate`, `v_gate`) preserved as-is.
* FFN block (3×3 expand → GELU → 3×3 contract, with pre-norm + residual)
  preserved as-is.
* `n_heads` is retained as a parameter only for GroupNorm group count;
  attention itself no longer uses head grouping.
"""
from __future__ import annotations

from typing import List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class FeedbackTransformer(nn.Module):
    """Per-channel spatial attention block with gated Z↔H fusion.

    Same constructor signature as V1's `FeedbackTransformer` so the cell
    wrapper in `memory.py` can stay byte-identical. Only the attention
    computation in `forward()` changes.

    Args
    ----
    d_model    : working channel count. Z input AND module output use this.
    c_feedback : total channel count of `concat(feedback_list)` at forward
                 time. Used to size the Q_H/K_H/V_H projections.
                 If 0, the module has no H side and runs pure self-attention
                 on Z.
    n_heads    : GroupNorm group count. The attention computation itself is
                 per-channel; this only controls how GroupNorm splits Q, K, V.
                 `d_model` must be divisible by `n_heads`.
    expand     : FFN expansion ratio (default 4) — Conv3x3(C → expand·C) →
                 GELU → Conv3x3(expand·C → C).
    n_feedback : legacy arg — number of feedback sources expected. Used only
                 as a convenience to derive c_feedback when c_feedback=0:
                 c_feedback = n_feedback · d_model.
    """

    def __init__(
        self,
        d_model: int,
        c_feedback: int = 0,
        n_heads: int = 4,
        expand: int = 4,
        n_feedback: int = 0,
        feedback_init_scale: float = 0.0,  # noqa: ARG002 — back-compat
    ) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(
                f"d_model ({d_model}) must be divisible by n_heads ({n_heads}) "
                f"for GroupNorm to partition channels evenly"
            )
        if c_feedback == 0 and n_feedback > 0:
            c_feedback = n_feedback * d_model

        self.d_model = d_model
        self.n_heads = n_heads      # GroupNorm groups only — not "heads" in V1 sense
        self.expand = expand
        self.c_feedback = c_feedback
        self.n_feedback = n_feedback

        K = 3   # 3×3 same-same everywhere
        P = 1

        # ── Q/K/V from Z (driving input) ─────────────────────────────────
        self.q_proj_z = nn.Conv2d(d_model, d_model, kernel_size=K, padding=P, bias=True)
        self.k_proj_z = nn.Conv2d(d_model, d_model, kernel_size=K, padding=P, bias=True)
        self.v_proj_z = nn.Conv2d(d_model, d_model, kernel_size=K, padding=P, bias=True)

        # ── Q/K/V from H (concatenated feedback / recurrent state) ──────
        if c_feedback > 0:
            self.q_proj_h = nn.Conv2d(c_feedback, d_model, kernel_size=K, padding=P, bias=True)
            self.k_proj_h = nn.Conv2d(c_feedback, d_model, kernel_size=K, padding=P, bias=True)
            self.v_proj_h = nn.Conv2d(c_feedback, d_model, kernel_size=K, padding=P, bias=True)

            # Gated fusion: gate ∈ [0, 1], "fuse" path = raw Conv3x3 (2C → C).
            # Three independent gate/fuse pairs — Q, K, V each get their own.
            self.gate_q = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.fuse_q = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.gate_k = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.fuse_k = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.gate_v = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.fuse_v = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)

        # ── Pre-attention norms ─────────────────────────────────────────
        self.norm_q = nn.GroupNorm(n_heads, d_model)
        self.norm_k = nn.GroupNorm(n_heads, d_model)
        self.norm_v = nn.GroupNorm(n_heads, d_model)

        # ── Post-attention FFN block (pre-norm, residual) ───────────────
        self.norm_mlp     = nn.GroupNorm(n_heads, d_model)
        self.mlp_expand   = nn.Conv2d(d_model, expand * d_model, kernel_size=K, padding=P, bias=True)
        self.mlp_contract = nn.Conv2d(expand * d_model, d_model, kernel_size=K, padding=P, bias=True)
        self.activation   = nn.GELU()

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(
        self,
        sensory: torch.Tensor,
        feedback_list: Optional[List[torch.Tensor]] = None,
        attn_bias: Optional[torch.Tensor] = None,  # noqa: ARG002 (legacy, ignored)
    ) -> dict:
        if sensory.dim() != 4:
            raise ValueError(f"sensory must be (B, C, H, W); got {tuple(sensory.shape)}")
        B, C, H_z, W_z = sensory.shape
        if C != self.d_model:
            raise ValueError(f"sensory channels {C} != d_model {self.d_model}")

        # ── Z-side Q, K, V ───────────────────────────────────────────────
        Q_z = self.q_proj_z(sensory)
        K_z = self.k_proj_z(sensory)
        V_z = self.v_proj_z(sensory)

        have_h = (
            self.c_feedback > 0
            and feedback_list is not None
            and len(feedback_list) > 0
        )
        if have_h:
            H_cat = torch.cat(feedback_list, dim=1)
            if H_cat.shape[1] != self.c_feedback:
                raise ValueError(
                    f"concat(feedback_list) channels {H_cat.shape[1]} != "
                    f"c_feedback {self.c_feedback}"
                )
            if H_cat.shape[-2:] != (H_z, W_z):
                raise ValueError(
                    f"feedback spatial {tuple(H_cat.shape[-2:])} must match Z "
                    f"spatial {(H_z, W_z)} — resize before passing"
                )
            Q_h_proj = self.q_proj_h(H_cat)
            K_h_proj = self.k_proj_h(H_cat)
            V_h_proj = self.v_proj_h(H_cat)

            cat_q = torch.cat([Q_z, Q_h_proj], dim=1)
            cat_k = torch.cat([K_z, K_h_proj], dim=1)
            cat_v = torch.cat([V_z, V_h_proj], dim=1)
            g_q = torch.sigmoid(self.gate_q(cat_q))
            g_k = torch.sigmoid(self.gate_k(cat_k))
            g_v = torch.sigmoid(self.gate_v(cat_v))
            Q_zh = self.fuse_q(cat_q)
            K_zh = self.fuse_k(cat_k)
            V_zh = self.fuse_v(cat_v)
            Q = (1.0 - g_q) * Q_z + g_q * Q_zh
            K = (1.0 - g_k) * K_z + g_k * K_zh
            V = (1.0 - g_v) * V_z + g_v * V_zh
        else:
            Q, K, V = Q_z, K_z, V_z
            g_q = g_k = g_v = None

        Q = self.norm_q(Q)
        K = self.norm_k(K)
        V = self.norm_v(V)

        # ── Per-channel spatial attention (V2 change) ───────────────────
        # Each channel computes its own saliency over the (H, W) grid.
        #
        #   scores[b, c, h, w]   =  Q[b, c, h, w] * K[b, c, h, w]
        #   A[b, c, :, :]        =  softmax over (H·W) of scores[b, c, :, :]
        #   attn_out[b, c, h, w] =  A[b, c, h, w] * V[b, c, h, w]
        #
        # Note: the softmax denominator depends on the SAME channel's other
        # spatial positions. Channels are otherwise fully independent.
        # We multiply by 1/sqrt(H*W) for numerical stability of the
        # exponentials (kept small initially so softmax doesn't saturate
        # immediately at the start of training).
        scale = 1.0 / float(H_z * W_z) ** 0.5
        scores = (Q * K) * scale                                # (B, C, H, W)
        N = H_z * W_z
        scores_flat = scores.reshape(B, C, N)
        A_flat = F.softmax(scores_flat, dim=-1)                  # softmax over spatial axis
        A = A_flat.reshape(B, C, H_z, W_z)                       # (B, C, H, W)
        attn_out = A * V                                         # (B, C, H, W)

        # ── First residual ──────────────────────────────────────────────
        y = sensory + attn_out

        # ── Conv FFN block (pre-norm, 3×3 expand-then-contract, residual) ─
        m = self.norm_mlp(y)
        m = self.mlp_expand(m)
        m = self.activation(m)
        m = self.mlp_contract(m)
        out = y + m

        return {
            "out":          out,         # (B, C, H, W) — block output
            "attn":         A,           # (B, C, H, W) — V2: per-channel spatial softmax
            "attn_spatial": attn_out,    # (B, C, H, W) — A · V, the residual contribution
            "v_post_norm":  V,           # (B, C, H, W) — post-norm V
            "q_gate":       g_q,         # (B, C, H, W) or None
            "k_gate":       g_k,
            "v_gate":       g_v,
        }
