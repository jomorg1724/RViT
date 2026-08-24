"""
Recurrent ViT — the EXACT paper network (Morgan, Albanna, Herman), assembled:

    frame → VAEPatchFrontEnd (4 patches → 140-d tokens)
          → RecurrentViTxLSTM (multiplicative self-attention + spatial xLSTM)
          → flattened memory readout H' ∈ ℝ^{4096}
          → FFActor (policy)  +  QRCritic (distributional value)

The model exposes the interface our PAC/QR-DQN/PER harness (ppo.py) expects:
init_states / rl_step / forward_rl_sequence, and the attributes n_actions,
n_quantiles, seq_len. The recurrent state is ((H,C,N,M), t) — the xLSTM memory plus
an integer timestep used for the token's temporal one-hot. State is fully internal:
the harness only carries it opaquely (and re-encodes whole sequences from frames).
"""
from __future__ import annotations

from typing import Optional, List

import torch
import torch.nn as nn

try:
    from .vae_frontend import VAEPatchFrontEnd
    from .paper_encoder import RecurrentViTxLSTM
    from .paper_heads import FFActor, QRCritic
except ImportError:  # script / flat import
    from vae_frontend import VAEPatchFrontEnd        # type: ignore[no-redef]
    from paper_encoder import RecurrentViTxLSTM       # type: ignore[no-redef]
    from paper_heads import FFActor, QRCritic         # type: ignore[no-redef]


class RViTPaperModel(nn.Module):
    def __init__(self, n_actions: int = 2, n_quantiles: int = 5,
                 init_action_bias: Optional[List[float]] = None, seq_len: int = 7,
                 feedback: str = "multiplicative", two_lstm: bool = False, **_ignore) -> None:
        super().__init__()
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.feedback = feedback
        self.two_lstm = two_lstm
        self.enc_layers = 2 if two_lstm else 1                    # parity field for the harness

        self.front = VAEPatchFrontEnd()
        self.encoder = RecurrentViTxLSTM(feedback=feedback, two_lstm=two_lstm)
        self.n_tokens = self.encoder.n_patch
        rd = self.encoder.readout_dim                            # 4096
        self.actor_head = FFActor(rd, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(rd, n_actions, n_quantiles)

    # ── recurrent state: (xLSTM (H,C,N,M), timestep) ─────────────────────────
    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        return (self.encoder.init_states(batch_size, device=device, dtype=dtype), 0)

    @staticmethod
    def _to_bchw(x: torch.Tensor) -> torch.Tensor:
        """Accept (B,3,50,50) or (B,50,50,3); return (B,3,50,50)."""
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        return x.contiguous()

    def _run_heads(self, H_flat: torch.Tensor):
        actor_logits = self.actor_head(H_flat)
        q_dist = self.critic_head(H_flat)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    def _decode_readout(self, H_new):
        """H_new is either a single (B,4,1024) readout (both heads read it) or a tuple
        (actor_H, critic_H) for split-readout variants (e.g. affine_cascade: actor←H2,
        critic←H1). Returns (actor_logits, q_dist, V_dist, V_scalar, rec_flat)."""
        if isinstance(H_new, (tuple, list)):
            a_flat, c_flat = H_new[0].flatten(1), H_new[1].flatten(1)
            actor_logits = self.actor_head(a_flat)
            q_dist = self.critic_head(c_flat)
            V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
            return actor_logits, q_dist, V_dist, V_scalar, a_flat
        H_flat = H_new.flatten(1)
        a, q, vd, vs = self._run_heads(H_flat)
        return a, q, vd, vs, H_flat

    # ── one online step ──────────────────────────────────────────────────────
    def rl_step(self, x_t: torch.Tensor, prev_states, return_attn: bool = False,
                attn_clamp=None, **_ignore) -> dict:
        enc_state, t = prev_states
        X = self.front(self._to_bchw(x_t), t)
        new_enc, H_new, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn,
                                                         attn_clamp=attn_clamp)
        actor_logits, q_dist, V_dist, V_scalar, H_flat = self._decode_readout(H_new)
        return {
            "new_states": (new_enc, t + 1),
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
            "attn": [attn] if attn is not None else None,
            "rec": H_flat,
        }

    # ── re-encode a whole trajectory (PAC update / analysis) ──────────────────
    def forward_rl_sequence(self, x_video: torch.Tensor, return_attn: bool = False,
                            **_ignore) -> dict:
        B, T = x_video.shape[:2]
        enc_state = self.encoder.init_states(B, device=x_video.device, dtype=x_video.dtype)
        a_seq, q_seq, vd_seq, vs_seq, attn_seq = [], [], [], [], []
        for t in range(T):
            X = self.front(self._to_bchw(x_video[:, t]), t)
            enc_state, H_new, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn)
            if return_attn and attn is not None:
                attn_seq.append(attn)
            a, q, vd, vs, _ = self._decode_readout(H_new)
            a_seq.append(a); q_seq.append(q); vd_seq.append(vd); vs_seq.append(vs)
        out = {
            "actor_logits_seq": torch.stack(a_seq, dim=1),       # (B,T,A)
            "q_dist_seq": torch.stack(q_seq, dim=1),             # (B,T,A,N)
            "V_dist_seq": torch.stack(vd_seq, dim=1),            # (B,T,N)
            "V_scalar_seq": torch.stack(vs_seq, dim=1),          # (B,T)
            "recons": [],
        }
        if return_attn and attn_seq:
            out["attn_seq"] = torch.stack(attn_seq, dim=1)       # (B,T,4,4)
        return out
