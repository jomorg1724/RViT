"""
RViTPlusSetsize9V12Model — conv-free, RL-only recurrent attention model with a VQ-VAE-style
CODEBOOK bottleneck built from attention (develops the v8/exp6 finding).

The image addresses a STATIC learnable codebook and reads it as a soft softmax-weighted
blend (default), instead of injecting content downstream:

    Q = W_q·X ;  K = W_k·H2 ;  V = codebook (a STATIC learnable lookup table)
    weights = softmax(QKᵀ/√d)  over the N codebook slots
    Z = W_o·(weights @ codebook) + FFN               # NO X-residual
    H2 ← LSTM(X + Z) ;  Z → actor AND critic         # only the keys H2 are recurrent

The value codebook is a static nn.Parameter (was the recurrent H1), addressed by the
evolving keys H2. X enters only as queries (which codebook slots to read) and into the
H2 update; it is never a key or a value. Default vq_mode='soft' is plain soft attention;
the hard VQ-VAE-style variants (vq_mode='sample' / 'argmax', straight-through) remain
available behind the knob. See tx_lstm_encoder.py for the rationale and the temperature
knob. Everything else — patch embedding, env, the 1D-conv heads, the PAC + QR-DQN + PER
trainer — is unchanged from v8.

Pipeline:
    frame x_t (B,3,50,50)
       │  PatchEmbed → tokens X (B, N, d_model)
       │  VQAttnEncoder.forward_step: soft STATIC-codebook readout → Z ;
       │     H2 ← LSTM(X+Z)                       → exposes rec = [Z]
       ├─► ActorDecoder([Z])  : Z→(B,d,N)→Conv1d stack→flatten→logits (B, n_actions)
       └─► CriticDecoder([Z]) : Z→(B,d,N)→Conv1d stack→flatten→Q (B, n_actions, n_quantiles)

The external interface (init_states / rl_step / forward_rl_sequence, actor_head /
critic_head, n_actions / n_quantiles / seq_len / split_c3) is unchanged, so the
trainer is reused as-is. The recurrent State is (Hs,Cs) with Hs=[H2] (the value
codebook is a static Parameter, not a recurrent state).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import ActorDecoder, CriticDecoder
    from .tx_lstm_encoder import VQAttnEncoder, State
    from .patch_embed import PatchEmbed
except ImportError:  # pragma: no cover
    from decoder import ActorDecoder, CriticDecoder  # type: ignore[no-redef]
    from tx_lstm_encoder import VQAttnEncoder, State  # type: ignore[no-redef]
    from patch_embed import PatchEmbed  # type: ignore[no-redef]


class RViTPlusSetsize9V12Model(nn.Module):
    """Conv-free patch + VQ-VAE-style sampled codebook encoder + 1D-conv
    actor-critic heads.

    Args
    ----
    in_channels      : image channels (3 RGB).
    image_h, image_w : input size (50×50 for ChangeDetectionEnv).
    patch_size       : square patch edge (default 5 → 10×10 = 100 tokens).
    patch_hidden     : hidden width of the per-patch expansion MLP (default 128).
    d_model          : transformer / token width.
    d_mem            : LSTM hidden width (= recurrent-state width read by the heads).
    tx_heads         : heads in the cross-attention-over-memory block (default 8).
    tx_layers        : number of cross-attention blocks (default 1).
    n_lstm           : number of stacked LSTMs = number of recurrent states (default 2).
    conv_channels    : channels in each decoder Conv1d layer (default 64).
    n_conv_layers    : number of stride-2 Conv1d layers per decoder (default 3).
    conv_kernel      : Conv1d kernel size (default 5).
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
        tx_heads: int = 1,
        tx_layers: int = 1,
        n_lstm: int = 1,
        conv_channels: int = 64,
        n_conv_layers: int = 3,
        conv_kernel: int = 5,
        n_actions: int = 2,
        n_quantiles: int = 51,
        init_action_bias: Optional[list] = None,
        seq_len: int = 29,
        drop: float = 0.1,
        vq_mode: str = "soft",
        vq_temperature: float = 1.0,
    ) -> None:
        super().__init__()
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        # Number of recurrent states the decoders/analysis see (= stacked LSTMs).
        self.enc_layers = int(n_lstm)
        # v3-compat flag read by collect_episodes; this variant has no C₃ specialists.
        self.split_c3 = False

        self.patch_embed = PatchEmbed(
            in_channels=in_channels, image_h=image_h, image_w=image_w,
            patch_size=patch_size, d_model=d_model, patch_hidden=patch_hidden,
        )
        n_tokens = self.patch_embed.n_tokens
        self.n_tokens = n_tokens

        self.encoder = VQAttnEncoder(
            n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
            tx_layers=tx_layers, n_lstm=n_lstm, drop=drop,
            vq_mode=vq_mode, temperature=vq_temperature,
        )

        # 1D-conv heads (SEPARATE weights): BOTH read the transformer output Z (rec=[Z]).
        self.actor_head = ActorDecoder(
            d_mem=d_mem, n_tokens=n_tokens, n_actions=n_actions,
            conv_channels=conv_channels, n_conv_layers=n_conv_layers,
            conv_kernel=conv_kernel, drop=drop, init_action_bias=init_action_bias,
        )
        self.critic_head = CriticDecoder(
            d_mem=d_mem, n_tokens=n_tokens, n_actions=n_actions, n_quantiles=n_quantiles,
            conv_channels=conv_channels, n_conv_layers=n_conv_layers,
            conv_kernel=conv_kernel, drop=drop,
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
        """One frame: patchify → transformer+LSTM encoder step → actor + critic."""
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
        return_decoder: bool = False,                 # accepted for API parity
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
