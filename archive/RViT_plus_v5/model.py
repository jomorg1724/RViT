"""
RViTPlusV5Model — conv-free, RL-only, memory-as-tokens recurrent attention model.

Identical to v4 except the encoder: v5 replaces v4's FiLM-modulated
`FeedbackTransformerEncoder` with a `MemTokEncoder` (memtok_encoder.py) in which
the recurrent memory is treated AS TOKENS — each layer self-attends over
[patch tokens ++ H₁ ++ H₂] = 3·N tokens (no FiLM), and a per-layer LSTMCell
updates that layer's memory from the patch-token outputs.

Pipeline (no convolution, no predictive coding, no JEPA, no decoder/VAE):

    frame x_t (B,3,50,50)
       │  PatchEmbed (reshape + MLP)               → tokens (B, N, d_model)
       │  MemTokEncoder.forward_step               → updates 2 token-memories,
       │     each layer attends over [patch ++ H₁ ++ H₂] = 3·N tokens
       │                                            → exposes [H₁, H₂] (each B,N,d_mem)
       ├─► ActorDecoder([H₁,H₂])  (2-layer Transformer, CLS) → logits (B, n_actions)
       └─► CriticDecoder([H₁,H₂]) (2-layer Transformer, CLS) → Q (B, n_actions, n_quantiles)
                                                              → V via derive_V

The external interface (init_states / rl_step / forward_rl_sequence,
actor_head / critic_head, n_actions / n_quantiles / seq_len / split_c3) is
unchanged from v4, so the PER + PAC + QR-DQN trainer is reused as-is.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import ActorDecoder, CriticDecoder
    from .memtok_encoder import MemTokEncoder, State
    from .patch_embed import PatchEmbed
except ImportError:  # pragma: no cover
    from decoder import ActorDecoder, CriticDecoder  # type: ignore[no-redef]
    from memtok_encoder import MemTokEncoder, State  # type: ignore[no-redef]
    from patch_embed import PatchEmbed  # type: ignore[no-redef]


class RViTPlusV5Model(nn.Module):
    """Conv-free patch + memory-as-tokens transformer + transformer-decoder
    actor-critic.

    Args
    ----
    in_channels      : image channels (3 RGB).
    image_h, image_w : input size (50×50 for ChangeDetectionEnv).
    patch_size       : square patch edge (default 5 → 10×10 = 100 tokens).
    patch_hidden     : hidden width of the per-patch expansion MLP (default 128)
                       that blows the small raw patch (≈75 dims) up to d_model.
    d_model          : token / attention width. MUST equal d_mem (memtok concatenates
                       memory rows into the d_model token stream).
    d_mem            : recurrent-memory width (= d_model).
    enc_heads        : attention heads in each memtok transformer layer.
    enc_layers       : recurrent layers / memory states (default 2). Each layer
                       attends over patch + ALL memories → (1+enc_layers)·N tokens.
    n_FR             : inner iterations per frame (default 1).
    dec_heads        : attention heads in each decoder transformer.
    dec_layers       : decoder transformer depth (default 2).
    head_hidden      : hidden width of each decoder's MLP readout head
                       (default = d_mem).
    head_layers      : number of Linear layers in the MLP readout head
                       (default 2 — at least two FF layers decode the CLS).
    n_actions        : discrete action count (2 — wait/press).
    n_quantiles      : QR-DQN quantiles per (s, a) (default 51).
    init_action_bias : actor's per-action initial logit bias.
    seq_len          : max episode length the trainer pads to (env.T = 29).
    drop             : dropout used throughout.
    """

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 50,
        image_w: int = 50,
        patch_size: int = 5,
        patch_hidden: int = 128,
        d_model: int = 128,
        d_mem: int = 128,
        enc_heads: int = 4,
        enc_layers: int = 2,
        n_FR: int = 1,
        dec_heads: int = 4,
        dec_layers: int = 2,
        head_hidden: Optional[int] = None,
        head_layers: int = 2,
        n_actions: int = 2,
        n_quantiles: int = 51,
        init_action_bias: Optional[list] = None,
        seq_len: int = 29,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.enc_layers = int(enc_layers)
        # v3-compat flag read by collect_episodes; v5 has no C₃ specialists.
        self.split_c3 = False

        self.patch_embed = PatchEmbed(
            in_channels=in_channels, image_h=image_h, image_w=image_w,
            patch_size=patch_size, d_model=d_model, patch_hidden=patch_hidden,
        )
        n_tokens = self.patch_embed.n_tokens
        self.n_tokens = n_tokens

        self.encoder = MemTokEncoder(
            n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=enc_heads,
            n_layers=enc_layers, n_FR=n_FR, drop=drop,
        )

        dec_kwargs = dict(
            n_tokens=n_tokens, n_states=enc_layers, d_mem=d_mem,
            n_heads=dec_heads, n_layers=dec_layers,
            head_hidden=head_hidden, head_layers=head_layers, drop=drop,
        )
        # SEPARATE-weight, same-shape decoders ("the same decoder for the actor").
        self.actor_head = ActorDecoder(
            n_actions=n_actions, init_action_bias=init_action_bias, **dec_kwargs,
        )
        self.critic_head = CriticDecoder(
            n_actions=n_actions, n_quantiles=n_quantiles, **dec_kwargs,
        )

    # ── recurrent state ────────────────────────────────────────────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        return self.encoder.init_states(batch_size, device=device, dtype=dtype)

    # ── one-frame head evaluation ───────────────────────────────────────────
    def _run_heads(
        self, recurrent_states: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        actor_logits = self.actor_head(recurrent_states)
        q_dist = self.critic_head(recurrent_states)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    # ── online RL inference (single step, recurrent state in/out) ───────────
    def rl_step(
        self,
        x_t: torch.Tensor,
        prev_states: State,
        attn_biases: Optional[dict] = None,           # accepted for API parity; unused
        prev_c3_specialists: Optional[dict] = None,   # accepted for API parity; unused
    ) -> dict:
        """One frame: patchify → memtok encoder step → actor + critic."""
        tokens = self.patch_embed(x_t)
        new_states, rec_states = self.encoder.forward_step(tokens, prev_states)
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(rec_states)
        return {
            "new_states": new_states,
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
        }

    # ── re-encode a whole trajectory (PPO/PAC update path) ──────────────────
    def forward_rl_sequence(
        self,
        x_video: torch.Tensor,
        return_decoder: bool = False,                 # accepted for API parity; v5 has no decoder
        attn_biases_per_frame: Optional[list] = None,
    ) -> dict:
        """Run encoder + actor + critic at EVERY timestep, carrying the recurrent
        memory across frames. Returns the *_seq stacks the trainer consumes."""
        B, T = x_video.shape[:2]
        states = self.init_states(B, device=x_video.device, dtype=x_video.dtype)

        actor_logits_seq, q_dist_seq, V_dist_seq, V_scalar_seq = [], [], [], []
        states_seq: List[State] = []
        for t in range(T):
            tokens = self.patch_embed(x_video[:, t].contiguous())
            states, rec_states = self.encoder.forward_step(tokens, states)
            states_seq.append(states)
            actor_logits, q_dist, V_dist, V_scalar = self._run_heads(rec_states)
            actor_logits_seq.append(actor_logits)
            q_dist_seq.append(q_dist)
            V_dist_seq.append(V_dist)
            V_scalar_seq.append(V_scalar)

        return {
            "actor_logits_seq": torch.stack(actor_logits_seq, dim=1),   # (B, T, A)
            "q_dist_seq":       torch.stack(q_dist_seq, dim=1),         # (B, T, A, N)
            "V_dist_seq":       torch.stack(V_dist_seq, dim=1),         # (B, T, N)
            "V_scalar_seq":     torch.stack(V_scalar_seq, dim=1),       # (B, T)
            "states_seq":       states_seq,
            "final_states":     states,
            "recons":           [],
        }
