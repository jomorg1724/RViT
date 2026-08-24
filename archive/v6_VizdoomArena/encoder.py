"""
V6 encoder — hierarchical cross-attention feedback transformer with per-layer
token memories and game-state tokens.

Lineage: combines the two encoder designs that worked in this repo —
RViT_plus_v5's hierarchical per-layer LSTM memories (L1 emerged as a top-down
orienter, L2 as a temporal monitor) and RViT_plus_v5_part2's cross-attention
over memory-as-tokens (the causally decision-moving pathway) — and adds a
third, K/V-only token source: game-state tokens (vitals / weapon / last
action).

Per frame t, per layer ℓ = 1..L:

    K/V_ℓ  =  [ X_ℓ  ++  H₁..H_L (+mem-pos +tag)  ++  state_toks ]    N·(1+L)+S keys
    Z_ℓ    =  CrossAttnBlock_ℓ( Q = X_ℓ, KV = K/V_ℓ )                 N queries → N outputs
    H_ℓ,C_ℓ ← LSTMCell_ℓ( Z_ℓ, (H_ℓ, C_ℓ) )                           per-token memory write
    X_{ℓ+1} = Z_ℓ

Memories of layers < ℓ are already this-frame-updated when layer ℓ attends
(v5's hierarchical update order); layers ≥ ℓ contribute their previous-frame
state — top-down feedback.

Interpretability is built in:
  * ``forward_step(..., return_attn=True)`` returns per-layer attention
    ``(B, heads, N, N(1+L)+S)``; ``key_layout()`` names every key span.
  * Every attention call accepts an additive pre-softmax bias (``attn_bias``),
    routed through ``nn.MultiheadAttention``'s float ``attn_mask`` — the same
    faithful mechanism as the v5 deep-dive's ``dd_core``, but native to the
    model. ``bias=None`` ⇒ bit-identical to the unbiased forward.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import torch
import torch.nn as nn

# A recurrent state: (Hs, Cs) — per-layer lists of (B, n_tokens, d_mem).
State = Tuple[List[torch.Tensor], List[torch.Tensor]]


def prep_attn_bias(
    bias: Optional[torch.Tensor], batch: int, n_heads: int, n_q: int, n_k: int,
) -> Optional[torch.Tensor]:
    """Normalize a user bias to MultiheadAttention's float attn_mask.

    Accepts (n_k,) per-key, (n_q, n_k), (n_heads, n_q, n_k), or
    (B, n_heads, n_q, n_k); returns (B·n_heads, n_q, n_k) float (or a 2-D
    (n_q, n_k) which MHA broadcasts itself), or None.
    """
    if bias is None:
        return None
    if bias.dim() == 1:
        if bias.shape[0] != n_k:
            raise ValueError(f"per-key bias must have length {n_k}; got {tuple(bias.shape)}")
        return bias.view(1, n_k).expand(n_q, n_k)
    if bias.dim() == 2:
        if bias.shape != (n_q, n_k):
            raise ValueError(f"2D bias must be ({n_q},{n_k}); got {tuple(bias.shape)}")
        return bias
    if bias.dim() == 3:
        if bias.shape != (n_heads, n_q, n_k):
            raise ValueError(f"3D bias must be ({n_heads},{n_q},{n_k}); got {tuple(bias.shape)}")
        return bias.unsqueeze(0).expand(batch, -1, -1, -1).reshape(batch * n_heads, n_q, n_k)
    if bias.dim() == 4:
        if bias.shape != (batch, n_heads, n_q, n_k):
            raise ValueError(
                f"4D bias must be ({batch},{n_heads},{n_q},{n_k}); got {tuple(bias.shape)}"
            )
        return bias.reshape(batch * n_heads, n_q, n_k)
    raise ValueError(f"attn bias must be 1-4D; got {bias.dim()}D")


class StateTokens(nn.Module):
    """Game-state feature vector → S semantically fixed K/V tokens.

    Each named group (a contiguous slice of the feature vector) gets its own
    Linear → d_model plus a learned tag embedding, then a shared LayerNorm.
    Attention to these tokens is directly readable ("checks ammo", "monitors
    health") because the grouping is fixed, not learned.
    """

    def __init__(self, groups: Dict[str, Tuple[int, int]], d_model: int) -> None:
        super().__init__()
        self.group_names = list(groups.keys())
        self.slices = [groups[k] for k in self.group_names]
        self.n_tokens = len(self.group_names)
        self.proj = nn.ModuleList(
            [nn.Linear(hi - lo, d_model) for (lo, hi) in self.slices]
        )
        self.tag = nn.Parameter(torch.zeros(self.n_tokens, d_model))
        nn.init.normal_(self.tag, std=0.02)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, feats: torch.Tensor) -> torch.Tensor:
        """feats (B, F) → (B, S, d_model)."""
        toks = [
            proj(feats[:, lo:hi]) for proj, (lo, hi) in zip(self.proj, self.slices)
        ]
        return self.norm(torch.stack(toks, dim=1)) + self.tag


class CrossAttnBlock(nn.Module):
    """Pre-norm transformer block with CROSS-attention: queries = the N patch
    tokens X; keys/values = [X ++ memory/state tokens]. Residual on X.
    Bias-injectable + attention-returning (v5_part2's block, generalized)."""

    def __init__(self, d_model: int, n_heads: int, drop: float) -> None:
        super().__init__()
        self.n_heads = n_heads
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=drop, batch_first=True)
        self.norm_q = nn.LayerNorm(d_model)
        self.norm_kv = nn.LayerNorm(d_model)
        self.norm_ff = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def forward(
        self,
        X: torch.Tensor,
        extra_kv: torch.Tensor,
        return_attn: bool = False,
        attn_bias: Optional[torch.Tensor] = None,
    ):
        kv = self.norm_kv(torch.cat([X, extra_kv], dim=1))      # (B, n_k, d)
        B, n_q, n_k = X.shape[0], X.shape[1], kv.shape[1]
        mask = prep_attn_bias(attn_bias, B, self.n_heads, n_q, n_k)
        a, aw = self.attn(
            self.norm_q(X), kv, kv, attn_mask=mask,
            need_weights=return_attn, average_attn_weights=False,
        )
        Z = X + self.drop(a)
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, aw                                            # aw: (B,H,n_q,n_k) or None


class MultiLayerFeedbackEncoder(nn.Module):
    """L cross-attention feedback layers, each with its own per-token LSTM
    memory, all memories + game-state tokens visible to every layer as K/V.

    Args
    ----
    n_tokens     : patch tokens (48 for the 6×8 grid).
    d_model      : token width. MUST equal d_mem (memory enters the K/V stream).
    d_mem        : per-layer recurrent memory width.
    n_heads      : attention heads.
    n_layers     : feedback layers = recurrent memory states (default 2).
    state_groups : feature-vector slices for the game-state tokens
                   (see env.FEAT_GROUPS).
    drop         : dropout.
    """

    def __init__(
        self,
        n_tokens: int,
        d_model: int = 128,
        d_mem: int = 128,
        n_heads: int = 8,
        n_layers: int = 2,
        state_groups: Optional[Dict[str, Tuple[int, int]]] = None,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        if d_model != d_mem:
            raise ValueError(
                f"requires d_model == d_mem (memory rows enter the d_model K/V "
                f"stream); got d_model={d_model}, d_mem={d_mem}"
            )
        if d_model % n_heads != 0:
            raise ValueError(f"d_model ({d_model}) must be divisible by n_heads ({n_heads})")
        self.n_tokens = n_tokens
        self.d_model = self.d_mem = d_model
        self.n_heads = n_heads
        self.n_layers = max(1, int(n_layers))

        self.state_tokens = StateTokens(state_groups, d_model) if state_groups else None
        self.n_state_tokens = self.state_tokens.n_tokens if self.state_tokens else 0

        self.blocks = nn.ModuleList(
            [CrossAttnBlock(d_model, n_heads, drop) for _ in range(self.n_layers)]
        )
        self.cells = nn.ModuleList(
            [nn.LSTMCell(d_model, d_mem) for _ in range(self.n_layers)]
        )
        # Memory source tags (tell H1 from H2 from patch) + shared memory
        # positional embedding (memory row i ↔ patch position i).
        self.mem_tag = nn.Parameter(torch.zeros(self.n_layers, 1, d_model))
        nn.init.normal_(self.mem_tag, std=0.02)
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)
        # Learned initial memory per layer.
        self.H0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_layers)]
        )
        self.C0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_layers)]
        )

    # ── key layout for analysis ──────────────────────────────────────────────
    def key_layout(self) -> Dict[str, Tuple[int, int]]:
        """Named (start, end) spans of the K/V axis of every layer's attention.
        Layout: [patch (=layer input) | H1..HL | state tokens]."""
        N, L = self.n_tokens, self.n_layers
        layout: Dict[str, Tuple[int, int]] = {"patch": (0, N)}
        for k in range(L):
            layout[f"H{k + 1}"] = ((1 + k) * N, (2 + k) * N)
        if self.state_tokens is not None:
            base = (1 + L) * N
            for i, name in enumerate(self.state_tokens.group_names):
                layout[name] = (base + i, base + i + 1)
        return layout

    @property
    def n_keys(self) -> int:
        return (1 + self.n_layers) * self.n_tokens + self.n_state_tokens

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        Hs = [h.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
              for h in self.H0]
        Cs = [c.to(device=device, dtype=dtype).expand(batch_size, -1, -1).contiguous()
              for c in self.C0]
        return Hs, Cs

    def forward_step(
        self,
        tokens: torch.Tensor,
        feats: Optional[torch.Tensor],
        prev_state: State,
        return_attn: bool = False,
        attn_bias: Optional[Sequence[Optional[torch.Tensor]]] = None,
    ):
        """Consume ONE frame.

        tokens : (B, n_tokens, d_model) from PatchEmbed.
        feats  : (B, F) game-state features (None if no state tokens).
        prev_state : (Hs, Cs).
        attn_bias  : optional per-layer list of pre-softmax biases (see
                     ``prep_attn_bias`` for accepted shapes); None entries skip.

        Returns (new_state, rec[, attn_per_layer]) where rec = [H1..HL] and
        attn_per_layer[ℓ] is (B, heads, N, n_keys) when return_attn.
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens

        state_toks = None
        if self.state_tokens is not None:
            if feats is None:
                raise ValueError("encoder has state tokens but feats is None")
            state_toks = self.state_tokens(feats)            # (B, S, d_model)

        X = tokens
        attn_per_layer: List[Optional[torch.Tensor]] = []
        for li in range(self.n_layers):
            mem = [Hs[k] + self.mem_pos_emb + self.mem_tag[k] for k in range(self.n_layers)]
            extra_kv = torch.cat(mem + ([state_toks] if state_toks is not None else []), dim=1)
            bias = attn_bias[li] if attn_bias is not None else None
            X, aw = self.blocks[li](X, extra_kv, return_attn=return_attn, attn_bias=bias)
            attn_per_layer.append(aw)
            h, c = self.cells[li](
                X.reshape(B * N, self.d_model),
                (Hs[li].reshape(B * N, self.d_mem), Cs[li].reshape(B * N, self.d_mem)),
            )
            Hs[li] = h.view(B, N, self.d_mem)
            Cs[li] = c.view(B, N, self.d_mem)
        rec = [Hs[li] for li in range(self.n_layers)]
        if return_attn:
            return (Hs, Cs), rec, attn_per_layer
        return (Hs, Cs), rec
