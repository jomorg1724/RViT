"""
Feedback Transformer — self-attention over a spatial grid with arbitrary
recurrent feedback sources integrated at the Q/K/V level.

This is the core architectural primitive of HRA. Per the architectural-program
thread §1, a standard transformer self-attention layer is augmented to
integrate, at the level of the Q / K / V projections, an arbitrary number of
recurrent internal states drawn from elsewhere in the architecture.

For each recurrent feedback state $C_i$ (already aligned to the target grid's
spatial resolution by the caller), this module projects $C_i$ into per-state
queries, keys, and values, and combines them with the bottom-up sensory
projections $Q_S, K_S, V_S$ via element-wise (Hadamard) product *prior* to the
softmax. Concretely, the attention score for position i becomes

    α_{ij} ∝ ⟨ s_{q,i} ⊙ (1 + Σ_k c^{(k)}_{q,i}),  s_{k,j} ⊙ (1 + Σ_k c^{(k)}_{k,j}) ⟩

The "+1" trick keeps the multiplicative integration identity-initialised: when
feedback projections output zero, the attention reduces to a vanilla self-
attention over the sensory tokens, so the model starts from a sensible
baseline and learns to *modulate* rather than replace.

This formulation is the strict generalisation of FiLM (Perez 2018) to a
multi-source, intra-attention, hierarchical setting. PRISM v1's FiLM is a
special case (one feedback source, modulation only at the input to the
feature stack, not at the attention level).

Interpretability hooks
----------------------
Every forward() call returns the post-softmax attention map per head so the
analysis pipeline can inspect attention dynamics over iterations and layers
exactly the way Herman & Morgan 2025 analysed the recurrent ViT.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class FeedbackTransformer(nn.Module):
    """
    Multi-head self-attention over a spatial grid with feedback integration.

    The sensory input and every feedback source are flat token sequences of
    shape (B, N, D) where N = H × W. Spatial alignment of feedback sources to
    the target grid is the caller's responsibility (see memory.GridCellRNNCell
    for the conv-up/conv-down projections that do this).

    Args
    ----
    d_model        : token feature dim D
    n_heads        : number of attention heads (default 4); D must be divisible
    n_feedback     : number of feedback sources to expect. Pre-declared so all
                     per-source projections live in this module. If a forward
                     call passes fewer feedback states, the missing slots are
                     skipped (used for ablations).
    feedback_init_scale : multiplier on the initial weights of feedback Q/K/V
                     projections. Default 0.0 → feedback contributes nothing
                     at init (the "(1 + 0) = 1" identity start). Stage 1
                     should keep this at 0.0; later stages can warm-start
                     non-zero if needed.

    Forward (see __call__)
    ----------------------
    Inputs:
        sensory       : (B, N, D)
        feedback_list : list of (B, N, D), length ≤ n_feedback. If empty or
                        None, behaves as plain self-attention.
    Outputs (named-tuple style dict for interpretability):
        out      : (B, N, D)               — post-attention token features
        attn     : (B, n_heads, N, N)      — post-softmax attention weights
                                             EXPOSED for analysis; do not strip
        q_gate   : (B, N, D)               — multiplicative Q gate (1+Σc_q)
        k_gate   : (B, N, D)               — multiplicative K gate (1+Σc_k)
        v_gate   : (B, N, D)               — multiplicative V gate (1+Σc_v)
    """

    def __init__(
        self,
        d_model: int,
        n_heads: int = 4,
        n_feedback: int = 0,
        feedback_init_scale: float = 0.0,
    ) -> None:
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads})")

        self.d_model = d_model
        self.n_heads = n_heads
        self.d_head = d_model // n_heads
        self.n_feedback = n_feedback

        # Sensory Q, K, V — one big projection split into three.
        self.qkv_sensory = nn.Linear(d_model, 3 * d_model, bias=True)

        # Per-feedback-source Q, K, V projections. Pre-allocated as a single
        # ModuleList so the architecture is static and JIT-friendly.
        self.qkv_feedback = nn.ModuleList(
            [nn.Linear(d_model, 3 * d_model, bias=True) for _ in range(n_feedback)]
        )

        # Output projection (standard transformer pattern).
        self.proj_out = nn.Linear(d_model, d_model, bias=True)

        # Initialisation.
        nn.init.xavier_uniform_(self.qkv_sensory.weight)
        nn.init.zeros_(self.qkv_sensory.bias)
        for proj in self.qkv_feedback:
            nn.init.xavier_uniform_(proj.weight)
            proj.weight.data.mul_(feedback_init_scale)
            nn.init.zeros_(proj.bias)
        nn.init.xavier_uniform_(self.proj_out.weight)
        nn.init.zeros_(self.proj_out.bias)

        self._scale = self.d_head ** -0.5

    def forward(
        self,
        sensory: torch.Tensor,
        feedback_list: Optional[List[torch.Tensor]] = None,
    ) -> dict:
        if sensory.dim() != 3:
            raise ValueError(f"FeedbackTransformer.sensory must be (B,N,D); got {tuple(sensory.shape)}")
        B, N, D = sensory.shape
        if D != self.d_model:
            raise ValueError(f"D mismatch: sensory has {D}, expected {self.d_model}")

        # Sensory Q/K/V.
        s_q, s_k, s_v = self.qkv_sensory(sensory).chunk(3, dim=-1)  # each (B, N, D)

        # Accumulate feedback contributions. Default to zeros (identity at init).
        fb_q_sum = torch.zeros_like(s_q)
        fb_k_sum = torch.zeros_like(s_k)
        fb_v_sum = torch.zeros_like(s_v)

        if feedback_list is not None:
            for i, fb in enumerate(feedback_list):
                if i >= self.n_feedback:
                    raise ValueError(
                        f"feedback_list has {len(feedback_list)} entries but n_feedback={self.n_feedback}"
                    )
                if fb.shape != sensory.shape:
                    raise ValueError(
                        f"feedback[{i}] shape {tuple(fb.shape)} must match sensory {tuple(sensory.shape)}"
                    )
                f_q, f_k, f_v = self.qkv_feedback[i](fb).chunk(3, dim=-1)
                fb_q_sum = fb_q_sum + f_q
                fb_k_sum = fb_k_sum + f_k
                fb_v_sum = fb_v_sum + f_v

        # The "+1" identity-initialised multiplicative integration.
        q_gate = 1.0 + fb_q_sum
        k_gate = 1.0 + fb_k_sum
        v_gate = 1.0 + fb_v_sum

        q = s_q * q_gate
        k = s_k * k_gate
        v = s_v * v_gate

        # Reshape to (B, n_heads, N, d_head) for multi-head attention.
        q = q.view(B, N, self.n_heads, self.d_head).transpose(1, 2)
        k = k.view(B, N, self.n_heads, self.d_head).transpose(1, 2)
        v = v.view(B, N, self.n_heads, self.d_head).transpose(1, 2)

        # Scaled dot-product attention. Use the explicit form so we can return
        # the attention map; PyTorch's F.scaled_dot_product_attention is faster
        # but doesn't expose the post-softmax weights.
        scores = (q @ k.transpose(-2, -1)) * self._scale  # (B, H, N, N)
        attn = F.softmax(scores, dim=-1)
        out = attn @ v  # (B, H, N, d_head)

        # Re-merge heads.
        out = out.transpose(1, 2).contiguous().view(B, N, D)
        out = self.proj_out(out)

        return {
            "out": out,
            "attn": attn,        # (B, n_heads, N, N) — interpretability hook
            "q_gate": q_gate,    # (B, N, D)         — feedback Q modulation
            "k_gate": k_gate,    # (B, N, D)
            "v_gate": v_gate,    # (B, N, D)
        }
