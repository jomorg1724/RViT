"""
RViTPlusV15Model — v12's gradient-learned-codebook readout + a VQ-VAE-style ENERGY
term (reduces to v12 when energy → 0). See tx_lstm_encoder.py.

Per frame: Z = C + energy(C, H2) ; readout (v12) over Z → Z_read ; H2 ← LSTM(X+Z_read);
Z_read → actor + critic. The trainer adds energy_coef·mean‖energy‖² (commitment cost)
and EMAs C toward Z. forward_rl_sequence returns energy_cost_seq (B,T, for the penalty)
and energy_seq (B,T,N,d detached, for the EMA). The recurrent State is (Hs,Cs) with
Hs=[H2]; the codebook C is a gradient + EMA parameter, not a recurrent state.
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


class RViTPlusV15Model(nn.Module):
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
            tx_layers=tx_layers, n_lstm=n_lstm, drop=drop, temperature=temperature,
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
        al, qd, vd, vs, states_seq, ecost, eseq = [], [], [], [], [], [], []
        for t in range(T):
            tokens = self.patch_embed(x_video[:, t].contiguous())
            states, rec = self.encoder.forward_step(tokens, states)
            states_seq.append(states)
            ecost.append(self.encoder.last_energy_cost)        # (B,) differentiable mean‖energy‖²
            eseq.append(self.encoder.last_energy)              # (B,N,d) DETACHED energy (EMA signal)
            a, q, V, Vs = self._run_heads(rec)
            al.append(a); qd.append(q); vd.append(V); vs.append(Vs)
        # The per-step differentiable energy cost is already captured in `ecost`; detach
        # the lingering encoder attribute so the model stays deepcopy-safe (PAC target net).
        if self.encoder.last_energy_cost is not None:
            self.encoder.last_energy_cost = self.encoder.last_energy_cost.detach()
        return {
            "actor_logits_seq": torch.stack(al, dim=1),
            "q_dist_seq":       torch.stack(qd, dim=1),
            "V_dist_seq":       torch.stack(vd, dim=1),
            "V_scalar_seq":     torch.stack(vs, dim=1),
            "energy_cost_seq":  torch.stack(ecost, dim=1),     # (B,T) commitment / energy cost
            "energy_seq":       torch.stack(eseq, dim=1),      # (B,T,N,d) DETACHED — EMA signal
            "states_seq":       states_seq,
            "final_states":     states,
            "recons":           [],
        }
