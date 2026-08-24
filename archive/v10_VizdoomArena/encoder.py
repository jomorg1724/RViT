"""
V10 encoder — V6's hierarchical cross-attention feedback transformer rewired
so that EVERY layer's residual is its own carried memory (the RViT_plus_v8
H1-RESIDUAL, applied per layer).

V6's blocks put their residual on the layer input:

    Z₁ = X  + attn( Q=norm(X),  KV=[X ++ H₁..H_L ++ state] )    # V6 layer 1
    Z₂ = Z₁ + attn( Q=norm(Z₁), KV=[Z₁ ++ H₁..H_L ++ state] )   # V6 layer 2

Layer 1's X-residual is a bypass: current-frame visual content reaches the
LSTMs even when the attention ignores the patch keys entirely. V10 closes it
and makes the two layers structurally symmetric — each block's skip path is
the PREVIOUS state of the very memory its LSTM writes:

    Z₁ = H₁_prev + attn( Q=norm(X),       KV=[X ++ H₁..H_L ++ state] )  # perception
    Z₂ = H₂_prev + attn( Q=norm(H₁_new),  KV=[H₁ ++ H₂ (+pos+tag)]   )  # consolidation

(residuals are the raw carried memories — no tag/pos-emb). Layer 1 is the
PERCEPTION layer: the only routes by which frame-t input (visual patches AND
the K/V-only game-state tokens) can move downstream are its attention's value
stream and the query-driven re-gating of the softmax — to perceive, the model
must attend. Layer 2 is a MEMORY-CONSOLIDATION layer: H₁ (which has already
absorbed the frame through layer 1 + LSTM₁) queries over the memory bank
[H₁ ++ H₂]; it sees no raw input at all — no X, no state tokens. For L > 2 the
pattern continues: layer ℓ queries H_{ℓ-1} (this-frame), reads K/V=[H₁..H_L],
and its residual is H_ℓ_prev. The change is parameter-free — V10 has exactly
V6's weights.

The v8 deep-dive (exp6, RViT_plus_v8/analysis/deepdive) found that under the
H1-residual the trained model carried perception mostly through the
QUERY-GATING sub-channel (the frame re-aims the softmax over memory keys)
rather than the patch value content — the motivating reason to test the
wiring at arena scale.

On top of the L attention layers sits a READOUT stage: a per-token LSTM with
no attention block of its own that ingests the freshly written top memory
(H_L, this frame) and carries H_{L+1} — the ONLY representation the actor and
critic decoders read. H_{L+1} is not in any attention K/V bank; it is a pure
decision-side accumulator downstream of the whole attention stack.

Per frame t (hierarchical update order — layer ℓ sees layers < ℓ already
this-frame-updated, layers ≥ ℓ at their previous-frame state):

    layer 1:  Z₁ = H₁_prev + attn(Q=X,      KV=[X ++ H₁..H_L ++ state])   N·(1+L)+S keys
              H₁,C₁ ← LSTMCell₁(Z₁, (H₁,C₁))
    layer ℓ>1: Z_ℓ = H_ℓ_prev + attn(Q=H_{ℓ-1}, KV=[H₁..H_L])             N·L keys
              H_ℓ,C_ℓ ← LSTMCell_ℓ(Z_ℓ, (H_ℓ,C_ℓ))
    readout:  H_{L+1},C_{L+1} ← LSTMCell_readout(H_L, (H_{L+1},C_{L+1}))  → decoders

Interpretability is built in:
  * ``forward_step(..., return_attn=True)`` returns per-layer attention
    ``(B, heads, N, n_keys_for(ℓ))``; ``key_layout(ℓ)`` names every key span
    of layer ℓ (the key axis DIFFERS between layer 1 and later layers).
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
    """Pre-norm transformer block with CROSS-attention. The CALLER supplies all
    three streams: queries, the full K/V token set, and the residual tensor
    (v10: residual = the prev-frame memory the layer's LSTM carries, so the
    query content reaches the output only through the attention).
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
        query: torch.Tensor,
        kv_tokens: torch.Tensor,
        residual: torch.Tensor,
        return_attn: bool = False,
        attn_bias: Optional[torch.Tensor] = None,
    ):
        kv = self.norm_kv(kv_tokens)                            # (B, n_k, d)
        B, n_q, n_k = query.shape[0], query.shape[1], kv.shape[1]
        mask = prep_attn_bias(attn_bias, B, self.n_heads, n_q, n_k)
        a, aw = self.attn(
            self.norm_q(query), kv, kv, attn_mask=mask,
            need_weights=return_attn, average_attn_weights=False,
        )
        # v10 memory-residual: the skip path is the carried memory, NOT the
        # query input — query content can only enter via the attention.
        Z = residual + self.drop(a)
        Z = Z + self.ffn(self.norm_ff(Z))
        return Z, aw                                            # aw: (B,H,n_q,n_k) or None


class MultiLayerFeedbackEncoder(nn.Module):
    """L cross-attention feedback layers, each with its own per-token LSTM
    memory, plus a per-token READOUT LSTM (no attention) fed by the top
    memory H_L; its state H_{L+1} is what the decoders read. v10: every
    attention layer's residual is its own carried memory (the v8 H1-residual,
    per layer). Layer 1 (queries = patch tokens, K/V = [X ++ H₁..H_L ++ state])
    is the only layer that sees raw frame/state content; layers > 1 are
    memory-consolidation layers (queries = H_{ℓ-1} this-frame, K/V =
    [H₁..H_L]) — see the module docstring.

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
        # Readout stage: per-token LSTM fed by the freshly written H_L;
        # H_{L+1} is the decoders' input and is NOT part of any K/V bank.
        self.readout_cell = nn.LSTMCell(d_mem, d_mem)
        # Memory source tags (tell H1 from H2 from patch) + shared memory
        # positional embedding (memory row i ↔ patch position i).
        self.mem_tag = nn.Parameter(torch.zeros(self.n_layers, 1, d_model))
        nn.init.normal_(self.mem_tag, std=0.02)
        self.mem_pos_emb = nn.Parameter(torch.zeros(1, n_tokens, d_model))
        nn.init.normal_(self.mem_pos_emb, std=0.02)
        # Learned initial memory per layer (+1 for the readout state).
        self.n_states = self.n_layers + 1
        self.H0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_states)]
        )
        self.C0 = nn.ParameterList(
            [nn.Parameter(torch.zeros(1, n_tokens, d_mem)) for _ in range(self.n_states)]
        )

    # ── key layout for analysis ──────────────────────────────────────────────
    def key_layout(self, layer: int = 0) -> Dict[str, Tuple[int, int]]:
        """Named (start, end) spans of the K/V axis of one layer's attention.

        Layer 0:  [patch | H1..HL | state tokens]   ((1+L)·N + S keys)
        Layer ≥1: [H1..HL]                          (L·N keys)
        """
        N, L = self.n_tokens, self.n_layers
        if layer == 0:
            layout: Dict[str, Tuple[int, int]] = {"patch": (0, N)}
            for k in range(L):
                layout[f"H{k + 1}"] = ((1 + k) * N, (2 + k) * N)
            if self.state_tokens is not None:
                base = (1 + L) * N
                for i, name in enumerate(self.state_tokens.group_names):
                    layout[name] = (base + i, base + i + 1)
            return layout
        return {f"H{k + 1}": (k * N, (k + 1) * N) for k in range(L)}

    def n_keys_for(self, layer: int) -> int:
        if layer == 0:
            return (1 + self.n_layers) * self.n_tokens + self.n_state_tokens
        return self.n_layers * self.n_tokens

    @property
    def n_keys(self) -> int:
        """Layer-0 key count (the perception layer)."""
        return self.n_keys_for(0)

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

        Returns (new_state, rec[, attn_per_layer]) where rec = [H_{L+1}] (the
        readout memory — the decoders' sole input) and attn_per_layer[ℓ] is
        (B, heads, N, n_keys_for(ℓ)) when return_attn — layer 0 has
        (1+L)·N+S keys, later layers L·N keys.
        """
        Hs, Cs = list(prev_state[0]), list(prev_state[1])
        B, N = tokens.shape[0], self.n_tokens

        state_toks = None
        if self.state_tokens is not None:
            if feats is None:
                raise ValueError("encoder has state tokens but feats is None")
            state_toks = self.state_tokens(feats)            # (B, S, d_model)

        attn_per_layer: List[Optional[torch.Tensor]] = []
        for li in range(self.n_layers):
            mem = [Hs[k] + self.mem_pos_emb + self.mem_tag[k] for k in range(self.n_layers)]
            bias = attn_bias[li] if attn_bias is not None else None
            if li == 0:
                # PERCEPTION layer: frame queries over [X ++ memories ++ state];
                # residual = raw prev-frame H1 (Hs[0] not yet updated), so raw
                # frame/state content enters only through the attention.
                q = tokens
                kv = torch.cat([tokens] + mem
                               + ([state_toks] if state_toks is not None else []), dim=1)
            else:
                # CONSOLIDATION layer: H_{li-1} (already this-frame-updated by
                # cell li-1) queries over the memory bank only — no raw input,
                # no state tokens. Residual = raw prev-frame H_li.
                q = Hs[li - 1]
                kv = torch.cat(mem, dim=1)
            Z, aw = self.blocks[li](q, kv, residual=Hs[li],
                                    return_attn=return_attn, attn_bias=bias)
            attn_per_layer.append(aw)
            h, c = self.cells[li](
                Z.reshape(B * N, self.d_model),
                (Hs[li].reshape(B * N, self.d_mem), Cs[li].reshape(B * N, self.d_mem)),
            )
            Hs[li] = h.view(B, N, self.d_mem)
            Cs[li] = c.view(B, N, self.d_mem)
        # READOUT stage: per-token LSTM (no attention) on the freshly written
        # top memory; H_{L+1} is the only representation the decoders see.
        ri = self.n_layers
        h, c = self.readout_cell(
            Hs[ri - 1].reshape(B * N, self.d_mem),
            (Hs[ri].reshape(B * N, self.d_mem), Cs[ri].reshape(B * N, self.d_mem)),
        )
        Hs[ri] = h.view(B, N, self.d_mem)
        Cs[ri] = c.view(B, N, self.d_mem)
        rec = [Hs[ri]]
        if return_attn:
            return (Hs, Cs), rec, attn_per_layer
        return (Hs, Cs), rec
