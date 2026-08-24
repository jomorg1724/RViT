"""
Actor and critic decoders for V6.

Each head reads the concatenation of ALL encoder memories
[CLS ++ H₁ ++ … ++ H_L] (1 + L·N tokens) through a small pre-norm transformer
whose attention is exposed and bias-injectable (same mechanism as the
encoder), then decodes the CLS embedding with a ≥2-layer MLP head
(small-init final Linear — v5's proven readout).

  • ActorDecoder  → logits (B, n_actions); single pass.
  • CriticDecoder → Q-quantiles (B, n_actions, n_quantiles) in a SINGLE pass
    (the CLS maps to n_actions·n_quantiles outputs). v5's per-action
    input-encoding critic re-ran the decoder once per action — fine at A=2,
    a 14× cost at the arena's A=14, so v6 trades it for the standard QR-DQN
    multi-action head. The PAC math only needs Q̄(s,·) per action.
  • derive_V: expected-SARSA V_dist = Σ_a sg[π(a|s)]·Q(s,a,:) — unchanged
    from v5, so the trainer's distributional TD machinery carries over.

The CLS row of the final layer's attention is "what the decision reads" —
analysis slices it via ``Decoder.token_layout()``.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import torch
import torch.nn as nn

try:
    from .encoder import prep_attn_bias
except ImportError:  # pragma: no cover
    from encoder import prep_attn_bias  # type: ignore[no-redef]


def _make_ff_head(
    d_in: int, d_out: int, hidden: int, n_layers: int, drop: float,
    final_init_std: float = 0.02,
) -> nn.Sequential:
    """MLP readout: n_layers Linear layers (min 2), final Linear small-init'd
    so initial outputs are ~0 (≈uniform policy / ≈0 value)."""
    n_layers = max(2, int(n_layers))
    mods: list[nn.Module] = []
    d = d_in
    for _ in range(n_layers - 1):
        mods += [nn.Linear(d, hidden), nn.GELU(), nn.Dropout(drop)]
        d = hidden
    final = nn.Linear(d, d_out)
    nn.init.normal_(final.weight, std=final_init_std)
    nn.init.zeros_(final.bias)
    mods.append(final)
    return nn.Sequential(*mods)


class SelfAttnBlock(nn.Module):
    """Pre-norm transformer encoder block, attention-returning and
    bias-injectable (the decoder twin of encoder.CrossAttnBlock)."""

    def __init__(self, d_model: int, n_heads: int, drop: float) -> None:
        super().__init__()
        self.n_heads = n_heads
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=drop, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model), nn.GELU(), nn.Dropout(drop),
            nn.Linear(4 * d_model, d_model),
        )
        self.drop = nn.Dropout(drop)

    def forward(
        self,
        x: torch.Tensor,
        return_attn: bool = False,
        attn_bias: Optional[torch.Tensor] = None,
    ):
        h = self.norm1(x)
        B, S = x.shape[0], x.shape[1]
        mask = prep_attn_bias(attn_bias, B, self.n_heads, S, S)
        a, aw = self.attn(h, h, h, attn_mask=mask,
                          need_weights=return_attn, average_attn_weights=False)
        x = x + self.drop(a)
        x = x + self.ffn(self.norm2(x))
        return x, aw


class _CLSTransformerDecoder(nn.Module):
    """Shared backbone: concat memories, prepend CLS, run n_layers pre-norm
    blocks, return the normed CLS embedding (and attention if asked)."""

    def __init__(
        self,
        n_tokens: int,
        n_states: int = 2,
        d_mem: int = 128,
        n_heads: int = 8,
        n_layers: int = 2,
        head_hidden: Optional[int] = None,
        head_layers: int = 2,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        if d_mem % n_heads != 0:
            raise ValueError(f"d_mem ({d_mem}) must be divisible by n_heads ({n_heads})")
        self.n_tokens, self.n_states, self.d_mem = n_tokens, n_states, d_mem
        self.n_input = n_states * n_tokens
        self.head_hidden = int(head_hidden) if head_hidden is not None else d_mem
        self.head_layers = max(2, int(head_layers))
        self.drop_p = drop

        self.cls = nn.Parameter(torch.zeros(1, 1, d_mem))
        nn.init.normal_(self.cls, std=0.02)
        # Position alone distinguishes source state (block k) AND patch index.
        self.pos_emb = nn.Parameter(torch.zeros(1, self.n_input, d_mem))
        nn.init.normal_(self.pos_emb, std=0.02)

        self.blocks = nn.ModuleList(
            [SelfAttnBlock(d_mem, n_heads, drop) for _ in range(max(1, int(n_layers)))]
        )
        self.norm = nn.LayerNorm(d_mem)
        self.dp = nn.Dropout(drop)

    def token_layout(self) -> Dict[str, Tuple[int, int]]:
        """Named spans of the decoder sequence: [CLS | H1 | … | HL]."""
        layout = {"cls": (0, 1)}
        for k in range(self.n_states):
            layout[f"H{k + 1}"] = (1 + k * self.n_tokens, 1 + (k + 1) * self.n_tokens)
        return layout

    def encode(
        self,
        recurrent_states: List[torch.Tensor],
        return_attn: bool = False,
        attn_bias: Optional[Sequence[Optional[torch.Tensor]]] = None,
    ):
        if len(recurrent_states) != self.n_states:
            raise ValueError(
                f"expected {self.n_states} recurrent states; got {len(recurrent_states)}"
            )
        M = torch.cat(recurrent_states, dim=1)                  # (B, n_input, d_mem)
        if M.shape[1] != self.n_input:
            raise ValueError(
                f"concatenated states have {M.shape[1]} tokens; expected {self.n_input}"
            )
        B = M.shape[0]
        seq = torch.cat([self.cls.expand(B, -1, -1), M + self.pos_emb], dim=1)
        attns: List[Optional[torch.Tensor]] = []
        for li, blk in enumerate(self.blocks):
            bias = attn_bias[li] if attn_bias is not None else None
            seq, aw = blk(seq, return_attn=return_attn, attn_bias=bias)
            attns.append(aw)
        z = self.dp(self.norm(seq[:, 0]))                       # CLS readout (B, d_mem)
        if return_attn:
            return z, attns
        return z


class ActorDecoder(_CLSTransformerDecoder):
    """Policy head: CLS embedding → (B, n_actions) logits."""

    def __init__(
        self,
        n_actions: int = 14,
        init_action_bias: Optional[list] = None,
        final_init_std: float = 0.02,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.n_actions = n_actions
        self.head = _make_ff_head(self.d_mem, n_actions, self.head_hidden,
                                  self.head_layers, self.drop_p, final_init_std)
        if init_action_bias is not None:
            if len(init_action_bias) != n_actions:
                raise ValueError(
                    f"init_action_bias has length {len(init_action_bias)} but "
                    f"n_actions = {n_actions}"
                )
            with torch.no_grad():
                self.head[-1].bias.copy_(torch.tensor(init_action_bias, dtype=torch.float32))

    def forward(self, recurrent_states, return_attn: bool = False, attn_bias=None):
        out = self.encode(recurrent_states, return_attn=return_attn, attn_bias=attn_bias)
        if return_attn:
            z, attns = out
            return self.head(z), attns
        return self.head(out)                                   # (B, n_actions)


class CriticDecoder(_CLSTransformerDecoder):
    """Distributional QR-DQN head: CLS embedding → (B, n_actions, n_quantiles)
    in one pass."""

    def __init__(
        self,
        n_actions: int = 14,
        n_quantiles: int = 51,
        final_init_std: float = 0.02,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.n_actions = n_actions
        self.n_quantiles = n_quantiles
        self.head = _make_ff_head(self.d_mem, n_actions * n_quantiles, self.head_hidden,
                                  self.head_layers, self.drop_p, final_init_std)
        taus = (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles
        self.register_buffer("taus", taus)

    def forward(self, recurrent_states, return_attn: bool = False, attn_bias=None):
        out = self.encode(recurrent_states, return_attn=return_attn, attn_bias=attn_bias)
        if return_attn:
            z, attns = out
            return self.head(z).view(-1, self.n_actions, self.n_quantiles), attns
        return self.head(out).view(-1, self.n_actions, self.n_quantiles)

    def derive_V(
        self, q_dist: torch.Tensor, actor_logits: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Expected-SARSA V from Q and π, stop-grad on π (v5's derive_V):
            V_dist(s)   = Σ_a sg[π(a|s)] · Q(s, a, :)   → (B, n_quantiles)
            V_scalar(s) = mean over quantiles            → (B,)
        """
        if q_dist.dim() != 3:
            raise ValueError(f"q_dist must be (B, A, N); got {tuple(q_dist.shape)}")
        if actor_logits.dim() != 2:
            raise ValueError(f"actor_logits must be (B, A); got {tuple(actor_logits.shape)}")
        pi_sg = torch.softmax(actor_logits, dim=-1).detach()
        V_dist = (pi_sg.unsqueeze(-1) * q_dist).sum(dim=1)
        return V_dist, V_dist.mean(dim=-1)
