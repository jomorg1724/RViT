"""
Multi-head spatial-softmax attention block for RViT+ V3 (revision 2).

V3 keeps V1/V2's gated Q/K/V fusion (Z↔H concat+conv+sigmoid-gate), GroupNorm,
and conv-FFN block. The attention computation has been revised:

  V1  collapses the spatial axis of Q⋅K into a per-channel scalar, softmax OVER
      CHANNELS within each head. → deterministic channel router (collapsed).
  V2  per channel c, softmax OVER SPATIAL POSITIONS (every channel its own head,
      its own (H,W) saliency). → spatially structured but static, weakly cued.
  V3a 4 heads, per-head channel inner product → SIGMOID gate, broadcast over V.
      → the gate saturated (bright borders / all-on), because a sigmoid has no
      cross-position competition: every location can independently go to 1.
  V3b (this file) MANY heads (default 32), per-head channel inner product →
      SOFTMAX OVER THE GRID, broadcast over V:

          split C channels into n_heads groups:
              Q_i, K_i, V_i ∈ (B, C/n_heads, H, W)
          per-position channel-vector inner product (over the channel axis):
              A_i[b, h, w] = Σ_c Q_i[b, c, h, w] · K_i[b, c, h, w]     → (B, H, W)
          spatial softmax (each head's map sums to 1 over the H·W grid):
              A_i = softmax_{h,w}( A_i / √(C/n_heads) )
          broadcast over the head's channels, add to the residual:
              out_i[b, c, h, w] = A_i[b, h, w] · V_i[b, c, h, w]

Why this revision
-----------------
The V3a sigmoid gate saturated: with no normalization across positions, every
(head, location) could drive to 1 independently, so the maps lit up everywhere
(notably the conv-padding borders). A SOFTMAX over the grid imposes competition
— each head has one unit of attention to spend across the H·W positions, so it
must concentrate rather than saturate. Using MANY heads (32) keeps each head's
channel subspace small (2–4 channels here) while giving 32 independent spatial
maps whose sum is the readout. This is V2's spatial-softmax idea, but pooled
into a modest number of heads instead of one-map-per-channel.

Key mechanics / differences from V3a
------------------------------------
* Gate → distribution: SOFTMAX over the (H·W) grid per head, not a sigmoid.
  Each head's map is a probability distribution over space (sums to 1).
* n_heads default 32 (was 4). n_heads controls ONLY the channel split for the
  attention inner product. d_model must be divisible by n_heads.
* GroupNorm is DECOUPLED from n_heads: norm groups come from `_gn_groups_for`
  (8 for 64/96/128), so raising n_heads to 32 does not turn GroupNorm into
  near-instance-norm.
* `attn` output shape is (B, n_heads, H, W) — the per-head spatial softmax maps.
* `attn_spatial` is the residual contribution A·V, shape (B, C, H, W).
* `1/√(C/n_heads)` score scale is the softmax temperature (kept moderate so the
  distribution is neither uniform nor a hard one-hot at init). `attn_scale=False`
  disables it.

Failure modes to watch for in V3b
---------------------------------
- Softmax going (near-)uniform across the grid (the V2 risk): each head spreads
  its unit of attention evenly → little spatial selectivity. Detectable via the
  mean per-head spatial entropy vs log(H·W); fix by dropping/learning the
  temperature.
- All heads collapsing to the same cell (degenerate). Detectable via cross-head
  argmax variance.
"""
from __future__ import annotations

from typing import List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


def _gn_groups_for(channels: int) -> int:
    """Largest of (8,4,2,1) that divides `channels`. Decouples GroupNorm group
    count from the attention head count."""
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


class FeedbackTransformer(nn.Module):
    """Multi-head spatial-softmax attention block with gated Z↔H fusion.

    Same constructor signature as V1/V2's `FeedbackTransformer` so the cell
    wrapper in `memory.py` stays byte-identical. Only the attention computation
    in `forward()` changes.

    Args
    ----
    d_model    : working channel count. Z input AND module output use this.
    c_feedback : total channel count of `concat(feedback_list)` at forward
                 time. Used to size the Q_H/K_H/V_H projections. If 0, the
                 module runs pure self-attention on Z (no H side).
    n_heads    : number of attention heads (default 32). Channels are split
                 into n_heads contiguous groups; each group's channel vectors
                 are inner-producted per position to form that head's spatial
                 score. `d_model` must be divisible by `n_heads`. (GroupNorm
                 group count is independent — see `_gn_groups_for`.)
    expand     : FFN expansion ratio (default 4).
    n_feedback : legacy arg — used only to derive c_feedback when c_feedback=0:
                 c_feedback = n_feedback · d_model.
    attn_scale : if True (default), divide the pre-softmax score by
                 √(d_model / n_heads) — the softmax temperature.
    """

    def __init__(
        self,
        d_model: int,
        c_feedback: int = 0,
        n_heads: int = 32,
        expand: int = 4,
        n_feedback: int = 0,
        feedback_init_scale: float = 0.0,  # noqa: ARG002 — back-compat
        attn_scale: bool = True,
    ) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(
                f"d_model ({d_model}) must be divisible by n_heads ({n_heads}) "
                f"— each head owns d_model/n_heads channels"
            )
        if c_feedback == 0 and n_feedback > 0:
            c_feedback = n_feedback * d_model

        self.d_model = d_model
        self.n_heads = n_heads
        self.head_channels = d_model // n_heads
        self.expand = expand
        self.c_feedback = c_feedback
        self.n_feedback = n_feedback
        self.attn_scale = bool(attn_scale)

        gn = _gn_groups_for(d_model)   # GroupNorm groups, decoupled from n_heads

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
            self.gate_q = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.fuse_q = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.gate_k = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.fuse_k = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.gate_v = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)
            self.fuse_v = nn.Conv2d(2 * d_model, d_model, kernel_size=K, padding=P, bias=True)

        # ── Pre-attention norms (groups decoupled from n_heads) ─────────
        self.norm_q = nn.GroupNorm(gn, d_model)
        self.norm_k = nn.GroupNorm(gn, d_model)
        self.norm_v = nn.GroupNorm(gn, d_model)

        # ── Post-attention FFN block (pre-norm, residual) ───────────────
        self.norm_mlp     = nn.GroupNorm(gn, d_model)
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

        # ── Multi-head spatial-softmax attention (V3b change) ───────────
        # Split channels into n_heads groups, inner-product the per-head
        # channel vectors at each position into one spatial score, softmax
        # that score over the H·W grid (competition!), broadcast over V.
        #
        #   Q_i, K_i, V_i ∈ (B, Ch, H, W)        with Ch = C / n_heads
        #   A_i[b, h, w]  = Σ_c Q_i[b, c, h, w] · K_i[b, c, h, w]    (B, H, W)
        #   A_i           = softmax_{h,w}( A_i / √Ch )              (B, H, W)
        #   out_i         = A_i · V_i                               (B, Ch, H, W)
        nh, Ch = self.n_heads, self.head_channels
        Qh = Q.reshape(B, nh, Ch, H_z, W_z)
        Kh = K.reshape(B, nh, Ch, H_z, W_z)
        Vh = V.reshape(B, nh, Ch, H_z, W_z)

        scores = (Qh * Kh).sum(dim=2)                  # (B, nh, H, W) channel inner product
        if self.attn_scale:
            scores = scores / float(Ch) ** 0.5
        A = F.softmax(scores.reshape(B, nh, H_z * W_z), dim=-1)
        A = A.reshape(B, nh, H_z, W_z)                 # (B, nh, H, W), each head sums to 1 over grid
        attn_out = A.unsqueeze(2) * Vh                 # (B, nh, Ch, H, W)
        attn_out = attn_out.reshape(B, C, H_z, W_z)    # (B, C, H, W)

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
            "attn":         A,           # (B, n_heads, H, W) — per-head spatial softmax maps
            "attn_spatial": attn_out,    # (B, C, H, W) — A·V, the residual contribution
            "v_post_norm":  V,           # (B, C, H, W) — post-norm V
            "q_gate":       g_q,         # (B, C, H, W) or None
            "k_gate":       g_k,
            "v_gate":       g_v,
        }
