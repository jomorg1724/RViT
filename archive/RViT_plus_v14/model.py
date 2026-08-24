"""
RViTPlusV14Model — conv-free model with TWO coupled recurrent modules trained
CONCURRENTLY: Module 1 (T1+LSTM1) by self-supervised predictive coding, Module 2
(T2+LSTM2) by RL. Cross-detachments firewall the gradients (see tx_lstm_encoder.py).

Per frame:  Z2 = T2(H1.detach, H2) ; H2 = LSTM2(Z2) ;  Z1 = T1(X, Z2.detach, H1) ;
            H1 = LSTM1(Z1).  Actor/critic read H2; the SS loss runs on the H1 sequence.

The trainer adds ss_coef·L_SS to the RL loss; the detaches route L_SS only into
Module 1 and L_RL only into Module 2 (+ the heads). One optimizer, concurrent.
forward_rl_sequence returns the usual *_seq plus H1_seq (for the SS loss).
"""
from __future__ import annotations

from typing import List, Optional

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


class RViTPlusV14Model(nn.Module):
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
        d_latent: Optional[int] = None,
        pc_horizon: int = 1,
        temperature: float = 1.0,
    ) -> None:
        super().__init__()
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.enc_layers = 1
        self.split_c3 = False

        self.patch_embed = PatchEmbed(
            in_channels=in_channels, image_h=image_h, image_w=image_w,
            patch_size=patch_size, d_model=d_model, patch_hidden=patch_hidden,
        )
        n_tokens = self.patch_embed.n_tokens
        self.n_tokens = n_tokens

        self.encoder = VQAttnEncoder(
            n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
            tx_layers=tx_layers, n_lstm=n_lstm, drop=drop, d_latent=d_latent,
            pc_horizon=pc_horizon,
        )
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

    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        return self.encoder.init_states(batch_size, device=device, dtype=dtype)

    def _run_heads(self, recurrent_states):
        actor_logits = self.actor_head(recurrent_states)
        q_dist = self.critic_head(recurrent_states)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    def rl_step(self, x_t, prev_states, attn_biases=None, prev_c3_specialists=None) -> dict:
        tokens = self.patch_embed(x_t)
        new_states, rec = self.encoder.forward_step(tokens, prev_states)
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(rec)
        return {"new_states": new_states, "new_c3_specialists": {},
                "actor_logits": actor_logits, "critic_q_dist": q_dist,
                "V_dist": V_dist, "V_scalar": V_scalar}

    def forward_rl_sequence(self, x_video, return_decoder=False, attn_biases_per_frame=None) -> dict:
        B, T = x_video.shape[:2]
        states = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        al, qd, vd, vs, states_seq, H1_seq = [], [], [], [], [], []
        for t in range(T):
            tokens = self.patch_embed(x_video[:, t].contiguous())
            states, rec = self.encoder.forward_step(tokens, states)
            states_seq.append(states)
            H1_seq.append(states[0][0])                    # H1 (Module 1) for the SS loss
            a, q, V, Vs = self._run_heads(rec)
            al.append(a); qd.append(q); vd.append(V); vs.append(Vs)
        return {
            "actor_logits_seq": torch.stack(al, dim=1),
            "q_dist_seq":       torch.stack(qd, dim=1),
            "V_dist_seq":       torch.stack(vd, dim=1),
            "V_scalar_seq":     torch.stack(vs, dim=1),
            "H1_seq":           torch.stack(H1_seq, dim=1),   # (B,T,N,d) — SS predictive target
            "states_seq":       states_seq,
            "final_states":     states,
            "recons":           [],
        }
