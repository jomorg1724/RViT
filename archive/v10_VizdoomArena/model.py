"""
V10ArenaModel — multi-layer feedback transformer actor-critic for the ViZDoom
arena (deathmatch).

Pipeline per frame (no convolution anywhere):

    frame x_t (B,3,60,80) float [0,1]
       │  PatchEmbed (reshape + MLP)                  → tokens (B, 48, d_model)
       │  feats f_t (B,25) → StateTokens              → 3 K/V-only state tokens
       │  MultiLayerFeedbackEncoder.forward_step:
       │     layer 1 (perception)     Q=patch, KV=[X ++ H₁..H_L ++ state], res=H₁
       │     layer 2 (consolidation)  Q=H₁,    KV=[H₁..H_L],               res=H₂
       │     readout LSTM (no attn)   H₃ ← LSTM(H₂)
       ├─► ActorDecoder([H₃])   (CLS transformer) → logits (B, A)
       └─► CriticDecoder([H₃])  (CLS transformer) → Q (B, A, n_quantiles)
                                                   → V via derive_V

Trainer-facing API:
  * ``init_states(B)`` — learned initial recurrent state.
  * ``rl_step(x, feats, states, return_attn=, attn_bias=)`` — one online step.
    ``attn_bias`` = {"enc": [per-layer], "actor": [per-layer], "critic": [...]}
    additive pre-softmax biases for causal attention experiments.
  * ``forward_segment(obs, feats, init_states, dones)`` — re-encode a stored
    segment from its STORED initial recurrent state (R2D2 stored-state),
    resetting the state to the learned H₀ after any step with done=1 (episode
    boundary inside the segment).
  * ``states_to_tensors`` / ``tensors_to_states`` — (Hs, Cs) lists ↔
    (B, L, N, d) stack pairs for replay storage.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn

try:
    from .decoder import ActorDecoder, CriticDecoder
    from .encoder import MultiLayerFeedbackEncoder, State
    from .patch_embed import PatchEmbed
except ImportError:  # pragma: no cover
    from decoder import ActorDecoder, CriticDecoder  # type: ignore[no-redef]
    from encoder import MultiLayerFeedbackEncoder, State  # type: ignore[no-redef]
    from patch_embed import PatchEmbed  # type: ignore[no-redef]


class V10ArenaModel(nn.Module):
    """Conv-free patch + hierarchical cross-attention feedback encoder +
    CLS-transformer actor/critic for the ViZDoom arena.

    Args mirror v5 where shared; new: ``feat_dim`` / ``state_groups`` for the
    game-state tokens (pass env.FEAT_GROUPS), image 60×80, patch 10.
    """

    def __init__(
        self,
        in_channels: int = 3,
        image_h: int = 60,
        image_w: int = 80,
        patch_size: int = 10,
        patch_hidden: int = 128,
        d_model: int = 128,
        d_mem: int = 128,
        enc_heads: int = 8,
        enc_layers: int = 2,
        dec_heads: int = 8,
        dec_layers: int = 2,
        head_hidden: Optional[int] = None,
        head_layers: int = 2,
        n_actions: int = 14,
        n_quantiles: int = 51,
        init_action_bias: Optional[list] = None,
        feat_dim: int = 25,
        state_groups: Optional[Dict[str, Tuple[int, int]]] = None,
        drop: float = 0.1,
    ) -> None:
        super().__init__()
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.enc_layers = int(enc_layers)
        self.feat_dim = int(feat_dim)

        self.patch_embed = PatchEmbed(
            in_channels=in_channels, image_h=image_h, image_w=image_w,
            patch_size=patch_size, d_model=d_model, patch_hidden=patch_hidden,
        )
        self.n_tokens = self.patch_embed.n_tokens

        self.encoder = MultiLayerFeedbackEncoder(
            n_tokens=self.n_tokens, d_model=d_model, d_mem=d_mem,
            n_heads=enc_heads, n_layers=enc_layers,
            state_groups=state_groups, drop=drop,
        )

        # Decoders read ONLY the encoder's readout memory H_{L+1}.
        dec_kwargs = dict(
            n_tokens=self.n_tokens, n_states=1,
            state_names=[f"H{enc_layers + 1}"], d_mem=d_mem,
            n_heads=dec_heads, n_layers=dec_layers,
            head_hidden=head_hidden, head_layers=head_layers, drop=drop,
        )
        self.actor_head = ActorDecoder(
            n_actions=n_actions, init_action_bias=init_action_bias, **dec_kwargs,
        )
        self.critic_head = CriticDecoder(
            n_actions=n_actions, n_quantiles=n_quantiles, **dec_kwargs,
        )

    # ── recurrent state ───────────────────────────────────────────────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32) -> State:
        return self.encoder.init_states(batch_size, device=device, dtype=dtype)

    @staticmethod
    def states_to_tensors(states: State) -> Tuple[torch.Tensor, torch.Tensor]:
        """(Hs, Cs) per-layer lists → ((B, L, N, d), (B, L, N, d)) for storage."""
        return torch.stack(states[0], dim=1), torch.stack(states[1], dim=1)

    @staticmethod
    def tensors_to_states(H: torch.Tensor, C: torch.Tensor) -> State:
        """Inverse of states_to_tensors."""
        return list(H.unbind(dim=1)), list(C.unbind(dim=1))

    # ── heads ─────────────────────────────────────────────────────────────────
    def _run_heads(self, rec: List[torch.Tensor]):
        actor_logits = self.actor_head(rec)
        q_dist = self.critic_head(rec)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    # ── one online step ───────────────────────────────────────────────────────
    def rl_step(
        self,
        x_t: torch.Tensor,
        feats_t: torch.Tensor,
        prev_states: State,
        return_attn: bool = False,
        attn_bias: Optional[Dict[str, list]] = None,
    ) -> dict:
        """One frame. x_t (B,3,H,W) float in [0,1]; feats_t (B,F)."""
        bias = attn_bias or {}
        tokens = self.patch_embed(x_t)
        enc_out = self.encoder.forward_step(
            tokens, feats_t, prev_states,
            return_attn=return_attn, attn_bias=bias.get("enc"),
        )
        if return_attn:
            new_states, rec, enc_attn = enc_out
            actor_logits, actor_attn = self.actor_head(
                rec, return_attn=True, attn_bias=bias.get("actor"))
            q_dist, critic_attn = self.critic_head(
                rec, return_attn=True, attn_bias=bias.get("critic"))
        else:
            new_states, rec = enc_out
            actor_logits = self.actor_head(rec, attn_bias=bias.get("actor"))
            q_dist = self.critic_head(rec, attn_bias=bias.get("critic"))
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        out = {
            "new_states": new_states,
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
        }
        if return_attn:
            out["enc_attn"] = enc_attn          # [L] × (B, heads, N, n_keys)
            out["actor_attn"] = actor_attn      # [dec_layers] × (B, heads, S, S)
            out["critic_attn"] = critic_attn
        return out

    # ── re-encode a stored segment (update path) ──────────────────────────────
    def forward_segment(
        self,
        obs: torch.Tensor,
        feats: torch.Tensor,
        init_states: Optional[State] = None,
        dones: Optional[torch.Tensor] = None,
    ) -> dict:
        """Run encoder + heads at every step of a segment, carrying the
        recurrent memory and resetting it to the learned H₀ after done steps.

        obs   : (B, T, 3, H, W) float in [0,1]
        feats : (B, T, F)
        init_states : stored segment-start state (None → learned init).
        dones : (B, T_d) with T_d ≤ T; done at t resets the state entering t+1.
        """
        B, T = obs.shape[:2]
        device, dtype = obs.device, obs.dtype
        states = init_states if init_states is not None else \
            self.init_states(B, device=device, dtype=dtype)
        H0s, C0s = self.init_states(B, device=device, dtype=dtype)

        logits_seq, q_seq, Vd_seq, Vs_seq = [], [], [], []
        for t in range(T):
            tokens = self.patch_embed(obs[:, t].contiguous())
            states, rec = self.encoder.forward_step(tokens, feats[:, t], states)
            actor_logits, q_dist, V_dist, V_scalar = self._run_heads(rec)
            logits_seq.append(actor_logits)
            q_seq.append(q_dist)
            Vd_seq.append(V_dist)
            Vs_seq.append(V_scalar)
            if dones is not None and t < dones.shape[1]:
                d = dones[:, t].view(B, 1, 1).to(dtype)
                states = (
                    [(1.0 - d) * h + d * h0 for h, h0 in zip(states[0], H0s)],
                    [(1.0 - d) * c + d * c0 for c, c0 in zip(states[1], C0s)],
                )
        return {
            "actor_logits_seq": torch.stack(logits_seq, dim=1),   # (B, T, A)
            "q_dist_seq":       torch.stack(q_seq, dim=1),        # (B, T, A, N)
            "V_dist_seq":       torch.stack(Vd_seq, dim=1),       # (B, T, N)
            "V_scalar_seq":     torch.stack(Vs_seq, dim=1),       # (B, T)
            "final_states":     states,
        }
