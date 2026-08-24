"""
RViTPlusV13Model — conv-free, two-phase model: a self-supervised PREDICTIVE-CODING
recurrent transformer that is FROZEN, then repurposed for an RL task by an
ENERGY-MODULATION stream.

  Phase 1 (self-supervised):  predictive_forward(x_video) trains the encoder
    (PART A: T1 + LSTM1 + LSTM2 + the JEPA predictor) so H2_t predicts H1_{t+1}.
    Then call freeze_pc() to freeze PART A (+ patch_embed) and switch use_energy on.

  Phase 2 (RL):  rl_step / forward_rl_sequence run with use_energy=True — the
    energy stream (PART B: LSTM3 + T2) perturbs the frozen encoder's V path; the
    modulated Z1 drives the actor + critic. Only PART B + the heads train.

See tx_lstm_encoder.py for the architecture and the math. The external interface
(init_states / rl_step / forward_rl_sequence, actor_head / critic_head, n_actions /
n_quantiles / seq_len / split_c3) matches the trainer; the recurrent State is
(Hs,Cs) with Hs=[H1,H2,H3].
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


class RViTPlusV13Model(nn.Module):
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
        temperature: float = 1.0,
    ) -> None:
        super().__init__()
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.enc_layers = 1
        self.split_c3 = False
        self.use_energy = False          # Phase 1 by default; flipped on by freeze_pc()

        self.patch_embed = PatchEmbed(
            in_channels=in_channels, image_h=image_h, image_w=image_w,
            patch_size=patch_size, d_model=d_model, patch_hidden=patch_hidden,
        )
        n_tokens = self.patch_embed.n_tokens
        self.n_tokens = n_tokens

        self.encoder = VQAttnEncoder(
            n_tokens=n_tokens, d_model=d_model, d_mem=d_mem, n_heads=tx_heads,
            tx_layers=tx_layers, n_lstm=n_lstm, drop=drop, d_latent=d_latent,
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

    # ── two-phase control ───────────────────────────────────────────────────
    def freeze_pc(self) -> int:
        """Phase 1 → 2: freeze the predictive-coding encoder (PART A) + patch_embed,
        and switch the energy modulation ON. Only PART B + the heads remain trainable.
        Returns the number of frozen parameters."""
        n = 0
        for mod in [self.patch_embed, *self.encoder.pc_modules()]:
            params = [mod] if isinstance(mod, nn.Parameter) else list(mod.parameters())
            for p in params:
                p.requires_grad_(False)
                n += p.numel()
        self.encoder.T1.eval(); self.encoder.lstm1.eval(); self.encoder.lstm2.eval()
        self.patch_embed.eval()
        self.use_energy = True
        return n

    # ── recurrent state ─────────────────────────────────────────────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        return self.encoder.init_states(batch_size, device=device, dtype=dtype)

    def _run_heads(self, recurrent_states):
        actor_logits = self.actor_head(recurrent_states)
        q_dist = self.critic_head(recurrent_states)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    # ── Phase 1: self-supervised predictive coding ──────────────────────────
    def predictive_forward(self, x_video: torch.Tensor) -> dict:
        """Run the encoder (no energy), collect (H1,H2) sequences, and compute the
        JEPA predictive-coding loss (H2_t → H1_{t+1}). Trains PART A."""
        B, T = x_video.shape[:2]
        states = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        H1_seq, H2_seq = [], []
        for t in range(T):
            tokens = self.patch_embed(x_video[:, t].contiguous())
            states, _rec = self.encoder.forward_step(tokens, states, use_energy=False)
            H1_seq.append(states[0][0]); H2_seq.append(states[0][1])
        H1_seq = torch.stack(H1_seq, dim=1)        # (B,T,N,d)
        H2_seq = torch.stack(H2_seq, dim=1)
        valid = torch.ones(B, T, device=x_video.device)
        loss, surprise, parts = self.encoder.predictive_loss(H1_seq, H2_seq, valid)
        return {"loss": loss, "surprise_seq": surprise, "parts": parts}

    # ── Phase 2: RL inference (single step) ─────────────────────────────────
    def rl_step(self, x_t, prev_states, attn_biases=None, prev_c3_specialists=None) -> dict:
        tokens = self.patch_embed(x_t)
        new_states, rec = self.encoder.forward_step(tokens, prev_states, use_energy=self.use_energy)
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(rec)
        return {"new_states": new_states, "new_c3_specialists": {},
                "actor_logits": actor_logits, "critic_q_dist": q_dist,
                "V_dist": V_dist, "V_scalar": V_scalar}

    # ── Phase 2: re-encode a whole trajectory (PAC update path) ─────────────
    def forward_rl_sequence(self, x_video, return_decoder=False, attn_biases_per_frame=None) -> dict:
        B, T = x_video.shape[:2]
        states = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        al, qd, vd, vs, states_seq = [], [], [], [], []
        for t in range(T):
            tokens = self.patch_embed(x_video[:, t].contiguous())
            states, rec = self.encoder.forward_step(tokens, states, use_energy=self.use_energy)
            states_seq.append(states)
            a, q, V, Vs = self._run_heads(rec)
            al.append(a); qd.append(q); vd.append(V); vs.append(Vs)
        return {
            "actor_logits_seq": torch.stack(al, dim=1),
            "q_dist_seq":       torch.stack(qd, dim=1),
            "V_dist_seq":       torch.stack(vd, dim=1),
            "V_scalar_seq":     torch.stack(vs, dim=1),
            "states_seq":       states_seq,
            "final_states":     states,
            "recons":           [],
        }
