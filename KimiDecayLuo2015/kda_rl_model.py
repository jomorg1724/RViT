"""KDA conv-memory backbone + PAC/QR actor–critic heads for Luo–Maunsell RL.

The sensory/memory stack is the same `KDAConvMemoryModel` used on VDA16/motion
(stem → KDA accumulator → vision conv-attn → H1/H2 memory → R = [H1‖H2‖Z‖att_vis]).
This wrapper adds the PPO harness interface (`init_states` / `rl_step` /
`forward_rl_sequence`) and mean-pools R into the paper FFActor / QRCritic.

JEPA stays per-pixel on R, reshaped to the harness's structured layout
`(B, T, P, 1, proto)` so `structured_jepa_loss` can consume it unchanged.
"""
from __future__ import annotations

from typing import List, Optional

import torch
import torch.nn as nn

from kda_conv_memory_model import KDAConvMemoryModel
from paper_heads import FFActor, QRCritic


class KDALuoRLModel(nn.Module):
    def __init__(
        self,
        n_actions: int = 2,
        n_quantiles: int = 5,
        seq_len: int = 7,
        init_action_bias: Optional[List[float]] = None,
        n_channels: int = 64,
        map_size: int = 16,
        proto_dim: int = 256,
        memory_noise_std: float = 0.05,
        mem_every: int = 1,
        accum_mode: str = "kda",
        accum_decay: float = 0.5,
        kda_heads: int = 4,
        kda_head_dim: int = 16,
        frame_window: int = 1,
        frame_stride: int = 1,
    ) -> None:
        super().__init__()
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.n_channels = int(n_channels)
        self.map_size = int(map_size)
        self.proto_dim = int(proto_dim)
        self.n_tokens = self.map_size * self.map_size
        self.enc_layers = 1

        self.backbone = KDAConvMemoryModel(
            n_channels=n_channels,
            proto_dim=proto_dim,
            map_size=map_size,
            memory_noise_std=memory_noise_std,
            frame_window=frame_window,
            frame_stride=frame_stride,
            mem_every=mem_every,
            accum_mode=accum_mode,
            accum_decay=accum_decay,
            kda_heads=kda_heads,
            kda_head_dim=kda_head_dim,
        )
        # ppo_update records encoder grad-max; the whole backbone is the encoder.
        self.encoder = self.backbone

        readout_dim = 4 * n_channels
        self.actor_head = FFActor(readout_dim, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(readout_dim, n_actions, n_quantiles)

        # Structured JEPA centre: (P, 1, proto) matches logits (B,T,P,1,proto).
        self.register_buffer(
            "jepa_center",
            torch.zeros(self.n_tokens, 1, proto_dim),
        )

    def _to_bchw(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        return x.contiguous()

    def _run_heads(self, h_flat: torch.Tensor):
        actor_logits = self.actor_head(h_flat)
        q_dist = self.critic_head(h_flat)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        if device is None:
            device = next(self.parameters()).device
        h1, h2, acc = self.backbone.init_state(batch_size, device, dtype)
        return (h1, h2, acc, 0)

    def _step_frame(self, x_bchw: torch.Tensor, state, inject_memory_noise: bool):
        h1, h2, acc, t = state
        mem = self.backbone.memory
        old_noise = mem.memory_noise_std
        if not inject_memory_noise:
            mem.memory_noise_std = 0.0
        try:
            X_t = self.backbone.stem(x_bchw)
            R, (h1, h2, acc) = self.backbone.step(
                X_t, (h1, h2, acc),
                update_memory=((t + 1) % self.backbone.mem_every == 0),
            )
        finally:
            mem.memory_noise_std = old_noise
        return R, (h1, h2, acc, t + 1)

    def rl_step(self, x_t: torch.Tensor, prev_states, inject_memory_noise: bool = True, **_ignore) -> dict:
        R, new_states = self._step_frame(self._to_bchw(x_t), prev_states, inject_memory_noise)
        h_flat = R.mean(dim=(2, 3))
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(h_flat)
        return {
            "new_states": new_states,
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
            "attn": None,
            "rec": h_flat,
        }

    def forward_rl_sequence(
        self,
        x_video: torch.Tensor,
        return_cell: bool = False,
        inject_memory_noise: bool = True,
        **_ignore,
    ) -> dict:
        B, T = x_video.shape[:2]
        state = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        a_seq, q_seq, vd_seq, vs_seq, cell_seq = [], [], [], [], []
        for _t in range(T):
            R, state = self._step_frame(
                self._to_bchw(x_video[:, _t]), state, inject_memory_noise,
            )
            h_flat = R.mean(dim=(2, 3))
            a, q, vd, vs = self._run_heads(h_flat)
            a_seq.append(a)
            q_seq.append(q)
            vd_seq.append(vd)
            vs_seq.append(vs)
            if return_cell:
                cell_seq.append(R)
        out = {
            "actor_logits_seq": torch.stack(a_seq, dim=1),
            "q_dist_seq": torch.stack(q_seq, dim=1),
            "V_dist_seq": torch.stack(vd_seq, dim=1),
            "V_scalar_seq": torch.stack(vs_seq, dim=1),
            "recons": [],
        }
        if return_cell:
            out["cell_seq"] = torch.stack(cell_seq, dim=1)  # (B,T,4C,map,map)
        return out

    def jepa_logits(self, cell_seq: torch.Tensor) -> torch.Tensor:
        """R_seq (B,T,4C,H,W) → structured logits (B,T,P,1,proto)."""
        pix = self.backbone.jepa_logits(cell_seq)          # (B,T,H,W,proto)
        return pix.flatten(2, 3).unsqueeze(-2)             # (B,T,P,1,proto)

    def jepa_features(self, cell_seq: torch.Tensor) -> torch.Tensor:
        """R_seq → (B,T,P,2C) for VICReg anti-collapse."""
        return self.backbone.jepa_features(cell_seq)

    def heads_from_memory_sequence(self, h2: torch.Tensor) -> dict:
        raise RuntimeError(
            "teacher→actor/critic STE is not wired for the KDA Luo agent "
            "(cell_seq is the 4C spatial R map, not an H1/H2 token axis)"
        )
