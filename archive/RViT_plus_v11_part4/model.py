"""
RViTPlusV11Part4Model — conv-free, RL-only recurrent attention model with TWO
PERFECTLY PARALLEL recurrent cross-attention modules (NO cross-talk) and a SPLIT
readout: the μ SALIENCE module feeds the ACTOR and the Q TOP-DOWN module feeds the
CRITIC (see tx_lstm_encoder.py).

A variant of v11_part2 (everything else — patch embedding, env, PAC + QR-DQN + PER
trainer, hyperparameters — unchanged). v11_part4 CUTS the cross-talk v11_part2 had
(both streams shared the deep memory H2, written from the salience output): now each
module is a closed loop with its OWN memory, updated by its OWN transformer output.

  ENCODER (DualStreamEncoder), SINGLE head each, fully INDEPENDENT modules:
       • μ SALIENCE:  Zμ = X  + attn(Q=X, K=V=Hμ) + FFN ;  Hμ ← LSTM_μ(Zμ)   (residual=X,
         a grounded image stream). → ACTOR.
       • Q TOP-DOWN:  ZQ = HQ + attn(Q=X, K=V=HQ) + FFN ;  HQ ← LSTM_Q(ZQ)   (residual=HQ,
         v8-style gating-only; no grounded image content). → CRITIC.
     The two modules share ONLY the input X — neither reads or writes the other's
     memory; each memory is written by its own output (Hμ←Zμ, HQ←ZQ).

  DECODERS (SPLIT): the actor's 1D-CONV head reads ONLY Zμ; the critic's reads ONLY
     ZQ. Each ingests a single stream (d_model channels), arranged (B,d,N) and run
     through strided Conv1d over the TOKEN axis → flatten + Linear.

Pipeline (no convolution stem, no PC/JEPA, no decoder/VAE):

    frame x_t (B,3,50,50)
       │  PatchEmbed (reshape + MLP)        → tokens X (B, N, d_model)
       │  DualStreamEncoder.forward_step:
       │     μ SALIENCE  Zμ = X  + attn(Q=X, KV=Hμ) + FFN ;  Hμ ← LSTM_μ(Zμ)
       │     Q TOP-DOWN  ZQ = HQ + attn(Q=X, KV=HQ) + FFN ;  HQ ← LSTM_Q(ZQ)
       │                                    → exposes rec = [Zμ, ZQ] (B,N,d)
       ├─► ActorDecoder([Zμ])   : (B,d,N)→Conv1d stack→flatten→logits (B, n_actions)
       └─► CriticDecoder([ZQ])  : (B,d,N)→Conv1d stack→flatten→Q (B, n_actions, n_quantiles)
                                                          → V via derive_V

The external interface (init_states / rl_step / forward_rl_sequence,
actor_head / critic_head, n_actions / n_quantiles / seq_len / split_c3) is
unchanged, so the PER + PAC + QR-DQN trainer is reused as-is. The recurrent State
stays (Hs, Cs) with Hs=[Hμ,HQ], so state storage / burn-in / carry are untouched.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import ActorDecoder, CriticDecoder
    from .tx_lstm_encoder import DualStreamEncoder, State
    from .patch_embed import PatchEmbed
except ImportError:  # pragma: no cover
    from decoder import ActorDecoder, CriticDecoder  # type: ignore[no-redef]
    from tx_lstm_encoder import DualStreamEncoder, State  # type: ignore[no-redef]
    from patch_embed import PatchEmbed  # type: ignore[no-redef]


class RViTPlusV11Part4Model(nn.Module):
    """Conv-free patch + parallel dual-stream (salience + top-down) cross-attention
    encoder + 1D-conv actor-critic heads reading the two transformer outputs.

    Args
    ----
    in_channels      : image channels (3 RGB).
    image_h, image_w : input size (50×50 for ChangeDetectionEnv).
    patch_size       : square patch edge (default 5 → 10×10 = 100 tokens).
    patch_hidden     : hidden width of the per-patch expansion MLP (default 128).
    d_model          : transformer / token width.
    d_mem            : LSTM hidden width (= recurrent-state width read by the heads).
    tx_heads         : attention heads per stream (default 1; single head).
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

        self.encoder = DualStreamEncoder(
            n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
            tx_layers=tx_layers, n_lstm=n_lstm, drop=drop,
        )

        # 1D-conv heads (SEPARATE weights), SPLIT readout: the actor reads ONLY the
        # Tμ salience output Z_sal; the critic reads ONLY the TQ top-down output Z_td.
        # Each head therefore ingests a SINGLE stream (dec_in = d_model channels).
        dec_in = self.encoder.stream_dim         # = d_model (one stream)
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
        # SPLIT readout: rec = [Zμ, ZQ]. μ salience → ACTOR; Q top-down → CRITIC.
        z_mu, z_q = recurrent_states[0], recurrent_states[1]
        actor_logits = self.actor_head([z_mu])
        q_dist = self.critic_head([z_q])
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
