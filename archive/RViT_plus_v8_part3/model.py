"""
RViTPlusV8Part3Model — conv-free, RL-only recurrent attention model. Keeps v8's
H1-residual cross-attention encoder verbatim and adds a PREDICTIVE-COMPARATOR write
gate on the deep memory (change = a surprise-driven, localized rewrite of the
evolving codebook), a learnable-gain H1 residual, and a readout that reads H1 ‖ H2
(both LSTM states), not just H2. The comparator is a self-supervised side-car
(predictor trained reward-independently; gate sensitivity trained by RL), and at
init it reduces to exactly v8. See tx_lstm_encoder.py.

A re-architecture of v5 along two axes (everything else — patch embedding, env,
PAC + QR-DQN + PER trainer, all hyperparameters — is unchanged):

  1. ENCODER: a CROSS-ATTENTION-over-memory block (tx_heads=8) followed by TWO
     stacked per-token LSTMs (tx_lstm_encoder.py). The patch tokens X are the
     QUERIES; the keys/values are [X ++ H1 ++ H2] (patch + both carried LSTM
     memories, AS TOKENS). So memory is fed as tokens, but with only N queries the
     output Z is (B,N,d_model) — no slice-from-3N needed (contrast v5 memtok). The
     LSTMs keep per-token (B,N,d_mem) state carried across frames; H1 = LSTM1
     hidden, H2 = LSTM2 hidden, fed back as the memory tokens next frame.

  2. DECODERS: v5's 2-layer Transformer decoders are replaced by 1D-CONV heads
     (decoder.py). Each arranges the top recurrent state H2 as (B, d_mem channels,
     N tokens) and runs a stack of strided Conv1d layers over the TOKEN axis, then
     flattens + Linear to the outputs — preserving the spatial token layout (an
     earlier mean-pool variant that discarded it did not learn). No CLS, no
     action-as-input encoding.

Pipeline (no convolution stem, no PC/JEPA, no decoder/VAE):

    frame x_t (B,3,50,50)
       │  PatchEmbed (reshape + MLP)        → tokens (B, N, d_model)
       │  ComparatorEncoder.forward_step:
       │     cross-attn: Q=X, K=V=[X ++ H1 ++ H2] (memory-as-tokens) → Z (B,N,d)
       │     Z → LSTM1 → H1 ;  H1 → LSTM2 → H2   (per-token, carried across frames)
       │                                    → exposes [H1, H2] (each B,N,d_mem)
       ├─► ActorDecoder([H1,H2])  : H2→(B,d_mem,N)→Conv1d stack→flatten→logits (B, n_actions)
       └─► CriticDecoder([H1,H2]) : H2→(B,d_mem,N)→Conv1d stack→flatten→Q (B, n_actions, n_quantiles)
                                                          → V via derive_V

The external interface (init_states / rl_step / forward_rl_sequence,
actor_head / critic_head, n_actions / n_quantiles / seq_len / split_c3) is
unchanged from v5, so the PER + PAC + QR-DQN trainer is reused as-is.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import ActorDecoder, CriticDecoder
    from .tx_lstm_encoder import ComparatorEncoder, State
    from .patch_embed import PatchEmbed
except ImportError:  # pragma: no cover
    from decoder import ActorDecoder, CriticDecoder  # type: ignore[no-redef]
    from tx_lstm_encoder import ComparatorEncoder, State  # type: ignore[no-redef]
    from patch_embed import PatchEmbed  # type: ignore[no-redef]


class RViTPlusV8Part3Model(nn.Module):
    """Conv-free patch + v8 cross-attention encoder with a predictive-comparator
    write gate + 2 stacked LSTMs + 1D-conv actor-critic heads reading H1 ‖ H2.

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
        tx_heads: int = 8,
        tx_layers: int = 1,
        n_lstm: int = 2,
        conv_channels: int = 64,
        n_conv_layers: int = 3,
        conv_kernel: int = 5,
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

        self.encoder = ComparatorEncoder(
            n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
            tx_layers=tx_layers, n_lstm=n_lstm, drop=drop,
        )

        # 1D-conv heads (SEPARATE weights) over the token axis of [H1 ‖ H2] →
        # dec_in = n_lstm · d_mem channels (v8_part3 reads BOTH recurrent states).
        dec_in = self.enc_layers * d_mem
        self.actor_head = ActorDecoder(
            d_mem=dec_in, n_tokens=n_tokens, n_actions=n_actions,
            conv_channels=conv_channels, n_conv_layers=n_conv_layers,
            conv_kernel=conv_kernel, drop=drop, init_action_bias=init_action_bias,
        )
        self.critic_head = CriticDecoder(
            d_mem=dec_in, n_tokens=n_tokens, n_actions=n_actions, n_quantiles=n_quantiles,
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
        aux_pred_seq: List[torch.Tensor] = []
        states_seq: List[State] = []
        for t in range(T):
            tokens = self.patch_embed(x_video[:, t].contiguous())
            states, rec_states = self.encoder.forward_step(tokens, states)
            states_seq.append(states)
            aux_pred_seq.append(self.encoder.last_aux)                   # (B,) self-supervised predictor MSE
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
            "aux_pred_seq":     torch.stack(aux_pred_seq, dim=1),       # (B, T) comparator predictor loss
            "states_seq":       states_seq,
            "final_states":     states,
            "recons":           [],
        }
