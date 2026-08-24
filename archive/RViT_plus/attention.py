"""
Conv-recurrent vision-transformer attention block for RViT+.

Replaces the previous flatten-and-linear FeedbackTransformer with a fully
spatial, conv-only module that channel-attends over a token grid AFTER
gating an input Z against a stack of recurrent-state sources H.

Forward path
------------
Inputs (all spatial, 3×3 same-same convs everywhere — NO 1×1 convs):
    Z              : (B, d_model, H, W)  driving input (visual / descended state)
    feedback_list  : list of (B, c_i,    H, W)  recurrent / cross-layer sources.
                     Concatenated along the channel dim into a single H tensor
                     of shape (B, c_feedback, H, W). Caller is responsible for
                     spatially aligning each source to (H, W).

Gated Q/K/V fusion (Q shown; K and V have their own independent conv params):
    Q_Z   = Conv3x3(Z)
    Q_H   = Conv3x3(concat(feedback_list))   # c_feedback → d_model
    g_Q   = sigmoid( Conv3x3( concat([Q_Z, Q_H], dim=channel) ) )    # 2C → C
    Q_ZH  = Conv3x3( concat([Q_Z, Q_H], dim=channel) )               # 2C → C
    Q     = (1 − g_Q) · Q_Z  +  g_Q · Q_ZH

When `feedback_list` is None or empty, Q/K/V come straight from Z.

Channel attention (4 heads ≡ 4 GroupNorm groups):
    Q, K, V get pre-norm GroupNorm(num_groups = n_heads).
    Split channels into n_heads groups: Q_h, K_h, V_h ∈ (B, C/H, H, W).
    score_h = (Q_h ⊙ K_h).sum(over H, W) / sqrt(H · W)   # (B, C/H)
    A_h     = softmax(score_h, dim=channel)              # sums to 1 across channels
    A       = concat over heads → (B, C, 1, 1)
    out     = A · V                                       # broadcast over spatial

Residual + FFN block (pre-norm):
    y     = Z + out                                       # first residual
    m     = Conv3x3(GroupNorm(y), C → 4C) → GELU → Conv3x3(4C → C)
    out_y = y + m                                         # second residual

The 3×3 same-same convolutions give every projection a local spatial
inductive bias and a positional context — no separate positional embedding
needed for channel attention.

Departures from the prior version
---------------------------------
 * Fully spatial — no flatten / reshape to (B, N, D).
 * Channel attention (4 heads from 4 GN groups), not spatial scaled-dot
   self-attention. The "attention map" returned is (B, C, 1, 1).
 * All convolutions are 3×3 with padding=1 (no 1×1 convs anywhere, per spec).
 * Recurrent / cross-layer feedback sources are concatenated along channels
   before a single Q_H/K_H/V_H projection (rather than separate Hadamard
   per-source gates).
 * The microstim `attn_bias` hook from the previous design is retired —
   spatial-attention biasing doesn't map onto channel attention.
"""
from __future__ import annotations

from typing import List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class FeedbackTransformer(nn.Module):
    """Spatial conv attention block with gated Z↔H fusion + channel attention.

    Args
    ----
    d_model    : working channel count. Z input AND module output use this.
    c_feedback : total channel count of `concat(feedback_list)` at forward
                 time. Used to size the Q_H/K_H/V_H projections.
                 If 0, the module has no H side and runs pure self-attention
                 on Z.
    n_heads    : number of channel-attention heads (default 4). Also the
                 number of GroupNorm groups. `d_model` must be divisible.
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
        # Accepted but ignored — retained for constructor back-compat.
        feedback_init_scale: float = 0.0,  # noqa: ARG002 (unused)
    ) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads})")
        if c_feedback == 0 and n_feedback > 0:
            c_feedback = n_feedback * d_model

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.expand = expand
        self.c_feedback = c_feedback
        self.n_feedback = n_feedback

        K = 3  # 3×3 same-same everywhere — no 1×1 convs per spec
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

        # ── Pre-attention norms (4 groups by default = n_heads) ─────────
        self.norm_q = nn.GroupNorm(n_heads, d_model)
        self.norm_k = nn.GroupNorm(n_heads, d_model)
        self.norm_v = nn.GroupNorm(n_heads, d_model)

        # ── Post-attention FFN block (pre-norm, residual) ───────────────
        self.norm_mlp     = nn.GroupNorm(n_heads, d_model)
        self.mlp_expand   = nn.Conv2d(d_model, expand * d_model, kernel_size=K, padding=P, bias=True)
        self.mlp_contract = nn.Conv2d(expand * d_model, d_model, kernel_size=K, padding=P, bias=True)
        self.activation   = nn.GELU()

        # Xavier-init the conv weights, zero biases.
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
            # ── Concatenate feedback sources, then a single Q_H/K_H/V_H. ─
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

            # ── Gated fusion: Q = (1 − g) · Q_Z + g · Q_ZH ───────────────
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

        # ── Pre-attention norms ─────────────────────────────────────────
        Q = self.norm_q(Q)
        K = self.norm_k(K)
        V = self.norm_v(V)

        # ── Channel attention with n_heads groups ───────────────────────
        # Reshape Q, K to (B, n_heads, d_head, H, W).
        Q_h = Q.view(B, self.n_heads, self.d_head, H_z, W_z)
        K_h = K.view(B, self.n_heads, self.d_head, H_z, W_z)
        # score_h = sum over (H, W) of Q_h ⊙ K_h  → (B, n_heads, d_head).
        # Scale by 1/sqrt(H · W) so the score magnitude doesn't depend on
        # the spatial resolution.
        scale = 1.0 / float(H_z * W_z) ** 0.5
        scores = (Q_h * K_h).sum(dim=(-2, -1)) * scale       # (B, n_heads, d_head)
        # Softmax over channels WITHIN each head.
        A = F.softmax(scores, dim=-1)                         # (B, n_heads, d_head)
        # Flatten heads back into a (B, C, 1, 1) attention vector for broadcast.
        A_flat = A.reshape(B, C, 1, 1)
        attn_out = A_flat * V                                  # (B, C, H, W)

        # ── First residual (attention output → Z) ───────────────────────
        y = sensory + attn_out

        # ── Conv FFN block (pre-norm, 3×3 expand-then-contract, residual) ─
        m = self.norm_mlp(y)
        m = self.mlp_expand(m)
        m = self.activation(m)
        m = self.mlp_contract(m)
        out = y + m

        return {
            "out":    out,        # (B, C, H, W) — block output
            "attn":   A_flat,     # (B, C, 1, 1) — channel-attention softmax
            # Spatial attention residual: the (B, C, H, W) tensor that gets
            # ADDED to Z in the first residual. Each channel of V scaled by
            # its softmax weight. This is the signal that empirically looks
            # most "attention-map-like" — it shows WHERE the head attended
            # in pixel space, not just which channels survived the softmax.
            "attn_spatial": attn_out,
            # Post-norm V (before scaling) — useful for separating "what V
            # encoded" from "what A selected".
            "v_post_norm": V,
            "q_gate": g_q,        # (B, C, H, W) or None
            "k_gate": g_k,
            "v_gate": g_v,
        }
