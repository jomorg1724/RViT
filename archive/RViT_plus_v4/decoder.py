"""
Actor and critic decoders for RViT+ v4 (decoder is shared with v4).

Each head is a TWO-LAYER Transformer that reads BOTH recurrent states produced
by the encoder. The two states (H₁, H₂), each ``(B, n_tokens, d_mem)``, are
concatenated along the token axis into a ``(B, 2·n_tokens, d_mem)`` sequence; a
learned **CLS token** is prepended, the transformer runs, and the CLS embedding
is decoded by a small multi-layer feed-forward head (``head_layers`` ≥ 2 Linear
layers — NOT a single linear projection):

    seq = [CLS] ++ [H₁ tokens (n_tokens)] ++ [H₂ tokens (n_tokens)]   # 1 + 2·n_tokens
    z   = norm( TransformerEncoder(seq + pos_emb) )[:, 0]              # CLS readout
    out = ff_head(z)   # Linear→GELU→Dropout→…→Linear  (>= 2 FF layers)

This mirrors Palladio's ``FBT_AC`` (``ac_models.py``), where ``actor_tx`` and
``critic_tx`` are constructed by the SAME factory but are SEPARATE modules with
their own weights ("the same decoder for the actor"). Here both are 2-layer
``nn.TransformerEncoder`` stacks of identical shape, instantiated twice, each
with its own MLP readout head.

  • ActorDecoder  → logits (B, n_actions)
  • CriticDecoder → action-conditional quantile distribution
                    (B, n_actions, n_quantiles). The action is injected as a
                    learned positional-style encoding on the INPUT tokens and the
                    decoder is run once per action; V is derived from Q and π via
                    expected SARSA with stop-grad on π (``derive_V``), so ppo.py
                    is unchanged.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn


def _make_ff_head(
    d_in: int, d_out: int, hidden: int, n_layers: int, drop: float,
    final_init_std: float = 0.02,
) -> nn.Sequential:
    """Build an MLP readout head with at least two feed-forward (Linear) layers.

    n_layers counts Linear layers: 2 → ``Linear→GELU→Dropout→Linear`` (one
    hidden layer); 3 adds another ``Linear→GELU→Dropout`` block; etc. The FINAL
    Linear is small-Gaussian-init'd so initial outputs are ~0 (≈uniform policy /
    ≈0 value); hidden layers keep PyTorch's default init. The actor's
    ``init_action_bias`` is applied to ``head[-1].bias``.
    """
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


class _TwoLayerTransformerDecoder(nn.Module):
    """Shared backbone: concat recurrent states, prepend CLS, run a 2-layer
    Transformer encoder, return the CLS embedding.

    Args
    ----
    n_tokens   : tokens per recurrent state (e.g. 100).
    n_states   : how many recurrent states are concatenated (2 for a 2-layer
                 encoder).
    d_mem      : width of the recurrent-state tokens (= encoder d_mem).
    n_heads    : attention heads (must divide d_mem).
    n_layers   : transformer depth (default 2 — "two layer transformer").
    drop       : dropout.
    """

    def __init__(
        self,
        n_tokens: int,
        n_states: int = 2,
        d_mem: int = 128,
        n_heads: int = 4,
        n_layers: int = 2,
        head_hidden: Optional[int] = None,
        head_layers: int = 2,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        if d_mem % n_heads != 0:
            raise ValueError(f"d_mem ({d_mem}) must be divisible by n_heads ({n_heads})")
        self.n_tokens, self.n_states, self.d_mem = n_tokens, n_states, d_mem
        self.n_input = n_states * n_tokens                  # 2·n_tokens content tokens
        # MLP readout-head config (>= 2 feed-forward layers decode the CLS vector).
        self.head_hidden = int(head_hidden) if head_hidden is not None else d_mem
        self.head_layers = max(2, int(head_layers))
        self.drop_p = drop

        self.cls = nn.Parameter(torch.zeros(1, 1, d_mem))
        nn.init.normal_(self.cls, std=0.02)
        # Positional embedding over the concatenated state tokens. Position
        # alone distinguishes both the source layer (first n_tokens = H₁, next
        # n_tokens = H₂) and the patch index within it.
        self.pos_emb = nn.Parameter(torch.zeros(1, self.n_input, d_mem))
        nn.init.normal_(self.pos_emb, std=0.02)

        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_mem, nhead=n_heads, dim_feedforward=4 * d_mem,
            dropout=drop, batch_first=True, activation="gelu",
        )
        self.tx = nn.TransformerEncoder(enc_layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(d_mem)
        self.dp = nn.Dropout(drop)

    def encode(self, recurrent_states: List[torch.Tensor]) -> torch.Tensor:
        """recurrent_states: list of ``n_states`` tensors (B, n_tokens, d_mem).
        Returns the CLS embedding (B, d_mem)."""
        if len(recurrent_states) != self.n_states:
            raise ValueError(
                f"expected {self.n_states} recurrent states; got {len(recurrent_states)}"
            )
        M = torch.cat(recurrent_states, dim=1)              # (B, n_input, d_mem)
        if M.shape[1] != self.n_input:
            raise ValueError(
                f"concatenated states have {M.shape[1]} tokens; expected {self.n_input}"
            )
        B = M.shape[0]
        M = M + self.pos_emb
        seq = torch.cat([self.cls.expand(B, -1, -1), M], dim=1)   # (B, 1+n_input, d_mem)
        out = self.tx(seq)
        return self.dp(self.norm(out[:, 0]))                # CLS readout (B, d_mem)


class ActorDecoder(_TwoLayerTransformerDecoder):
    """Discrete-action policy head. CLS embedding → (B, n_actions) logits.

    Args
    ----
    n_actions        : action-space size (default 2 — Posner wait/press).
    init_action_bias : optional per-action initial logit bias. For
                       ChangeDetectionEnv, [0.0, -1.5] makes the initial policy
                       mostly-wait (press prob ≈ 0.18) so episodes run long
                       enough to generate a learning signal.
    Other args forwarded to ``_TwoLayerTransformerDecoder``.
    """

    def __init__(
        self,
        n_actions: int = 2,
        init_action_bias: Optional[list] = None,
        final_init_std: float = 0.02,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.n_actions = n_actions
        # >= 2-layer feed-forward MLP decoding the CLS vector → action logits.
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

    def forward(self, recurrent_states: List[torch.Tensor]) -> torch.Tensor:
        return self.head(self.encode(recurrent_states))     # (B, n_actions)


class CriticDecoder(_TwoLayerTransformerDecoder):
    """Action-conditional distributional value head — QR-DQN style, with the
    action injected as a learned **positional-style encoding** at the INPUT.

    Unlike the actor (one decode → all action logits), the critic conditions on
    the action BEFORE the transformer: a learned ``action_emb`` of shape
    ``(n_actions, n_tokens, d_mem)`` is added — like a positional encoding — to
    the memory tokens (tiled across the ``n_states`` recurrent-state blocks), one
    additive code per action. The decoder is then run once per action (batched
    over B·n_actions) and the CLS readout of action a's pass IS ``Q(s, a, ·)``.
    So the action modulates the whole attention computation, not just a final
    projection, and the head emits a single per-action quantile vector.

    Output: ``(B, n_actions, n_quantiles)``. V(s) is derived from Q(s,a) and π
    via expected SARSA with stop-grad on π (``derive_V``), so the PPO/PER
    machinery is unchanged.

    Args
    ----
    n_actions   : number of discrete actions (must match the actor).
    n_quantiles : N quantiles per (s, a). Default 51 (QR-DQN).
    Other args forwarded to ``_TwoLayerTransformerDecoder``.
    """

    def __init__(
        self,
        n_actions: int = 2,
        n_quantiles: int = 51,
        final_init_std: float = 0.02,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.n_actions = n_actions
        self.n_quantiles = n_quantiles
        # Learned per-action additive encoding injected into the input tokens
        # BEFORE the transformer (positional-style). (n_actions, n_tokens, d_mem);
        # tiled across the n_states memory blocks at forward.
        self.action_emb = nn.Parameter(torch.zeros(n_actions, self.n_tokens, self.d_mem))
        nn.init.normal_(self.action_emb, std=0.02)
        # The action is encoded at the INPUT, so the head emits ONE action's
        # quantile vector (n_quantiles); the decode is run per action.
        self.head = _make_ff_head(self.d_mem, n_quantiles, self.head_hidden,
                                  self.head_layers, self.drop_p, final_init_std)
        # Quantile midpoints τ_i = (i + 0.5) / N for the quantile-Huber loss.
        taus = (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles
        self.register_buffer("taus", taus)

    def forward(self, recurrent_states: List[torch.Tensor]) -> torch.Tensor:
        """Run the decoder once per action with that action's input encoding
        added; return Q(s,a,·) as (B, n_actions, n_quantiles)."""
        if len(recurrent_states) != self.n_states:
            raise ValueError(
                f"expected {self.n_states} recurrent states; got {len(recurrent_states)}"
            )
        M = torch.cat(recurrent_states, dim=1)              # (B, n_input, d_mem)
        if M.shape[1] != self.n_input:
            raise ValueError(
                f"concatenated states have {M.shape[1]} tokens; expected {self.n_input}"
            )
        B, A = M.shape[0], self.n_actions
        M = M + self.pos_emb                                # base positional encoding
        # Per-action additive code, tiled across the n_states blocks so action a's
        # code at patch i hits every state's token i → (A, n_input, d_mem).
        a_enc = self.action_emb.repeat(1, self.n_states, 1)
        Ma = (M.unsqueeze(1) + a_enc.unsqueeze(0)).reshape(B * A, self.n_input, self.d_mem)
        seq = torch.cat([self.cls.expand(B * A, -1, -1), Ma], dim=1)   # (B*A, 1+n_input, d_mem)
        z = self.dp(self.norm(self.tx(seq)[:, 0]))          # (B*A, d_mem) CLS readout per (s,a)
        q = self.head(z)                                    # (B*A, n_quantiles)
        return q.view(B, A, self.n_quantiles)               # (B, n_actions, n_quantiles)

    def derive_V(
        self, q_dist: torch.Tensor, actor_logits: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Expected-SARSA V from Q and π, stop-grad on π (Q_CRITIC.md §2.4).

            V_dist(s)   = Σ_a sg[π(a|s)] · Q(s, a, :)   → (B, n_quantiles)
            V_scalar(s) = mean over quantiles of V_dist → (B,)
        """
        if q_dist.dim() != 3:
            raise ValueError(f"q_dist must be (B, n_actions, n_quantiles); got {tuple(q_dist.shape)}")
        if actor_logits.dim() != 2:
            raise ValueError(f"actor_logits must be (B, n_actions); got {tuple(actor_logits.shape)}")
        pi = torch.softmax(actor_logits, dim=-1)
        pi_sg = pi.detach()                                  # stop-grad on the policy
        V_dist = (pi_sg.unsqueeze(-1) * q_dist).sum(dim=1)   # (B, n_quantiles)
        V_scalar = V_dist.mean(dim=-1)                       # (B,)
        return V_dist, V_scalar
