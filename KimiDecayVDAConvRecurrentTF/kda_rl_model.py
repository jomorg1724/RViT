"""KDA conv-memory backbone + PAC/QR actor–critic heads for VDA16 RL.

Same wrapper contract as the Luo KDA RL agent: init_states / rl_step /
forward_rl_sequence, mean-pool R into FFActor / QRCritic, per-pixel JEPA
reshaped to (B, T, P, 1, proto). Width is VDA's C=128 (KDA 4×32), not Luo C=64.
"""
from __future__ import annotations

from typing import List, Optional

import torch
import torch.nn as nn

from kda_conv_memory_model import KDAConvMemoryModel
from paper_heads import FFActor, QRCritic


class SpatialConvReadout(nn.Module):
    """Decode R (B, 4C, H, W) with strided convs. No global mean-pool."""

    def __init__(self, in_ch: int, map_size: int = 16) -> None:
        super().__init__()
        hid = max(in_ch // 4, 32)
        mid = max(hid // 2, 16)
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, hid, 3, stride=2, padding=1),
            nn.GELU(),
            nn.Conv2d(hid, mid, 3, stride=2, padding=1),
            nn.GELU(),
        )
        spatial = (map_size // 4) * (map_size // 4)
        self.out_dim = mid * spatial

    def forward(self, R: torch.Tensor) -> torch.Tensor:
        return self.net(R).flatten(1)


class TinyHead(nn.Module):
    """One small FFN on the conv readout."""

    def __init__(self, in_dim: int, out_dim: int, hidden: int = 64,
                 out_bias: Optional[List[float]] = None) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.ELU(),
            nn.Linear(hidden, out_dim),
        )
        if out_bias is not None:
            with torch.no_grad():
                self.net[-1].bias.copy_(torch.tensor(out_bias, dtype=self.net[-1].bias.dtype))

    def forward(self, h: torch.Tensor) -> torch.Tensor:
        return self.net(h)


class KDARLModel(nn.Module):
    def __init__(
        self,
        n_actions: int = 2,
        n_quantiles: int = 5,
        seq_len: int = 7,
        init_action_bias: Optional[List[float]] = None,
        n_channels: int = 128,
        map_size: int = 16,
        proto_dim: int = 256,
        memory_noise_std: float = 0.05,
        mem_every: int = 1,
        accum_mode: str = "kda",
        accum_decay: float = 0.5,
        kda_heads: int = 4,
        kda_head_dim: int = 32,
        frame_window: int = 1,
        frame_stride: int = 1,
        attn_mode: str = "pixel_gate",
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
            attn_mode=attn_mode,
        )
        self.encoder = self.backbone

        readout_dim = 4 * n_channels
        self.readout = SpatialConvReadout(readout_dim, map_size)
        self.actor_head = TinyHead(
            self.readout.out_dim, n_actions, hidden=64, out_bias=init_action_bias,
        )
        self.critic_ff = TinyHead(
            self.readout.out_dim, n_actions * n_quantiles, hidden=64,
        )
        self.critic_ff.register_buffer(
            "taus",
            (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles,
        )
        self.critic_head = self.critic_ff
        self.register_buffer(
            "jepa_center",
            torch.zeros(self.n_tokens, 1, proto_dim),
        )

    def _to_bchw(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        return x.contiguous()

    def _run_heads(self, R: torch.Tensor):
        h = self.readout(R)
        actor_logits = self.actor_head(h)
        q_dist = self.critic_ff(h).view(h.shape[0], self.n_actions, self.n_quantiles)
        pi = torch.softmax(actor_logits, dim=-1).unsqueeze(-1)
        V_dist = (pi * q_dist).sum(dim=-2)
        V_scalar = V_dist.mean(dim=-1)
        return actor_logits, q_dist, V_dist, V_scalar, h

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
        actor_logits, q_dist, V_dist, V_scalar, h = self._run_heads(R)
        return {
            "new_states": new_states,
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": V_dist,
            "V_scalar": V_scalar,
            "attn": None,
            "rec": h,
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
            a, q, vd, vs, _ = self._run_heads(R)
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
            out["cell_seq"] = torch.stack(cell_seq, dim=1)
        return out

    def jepa_logits(self, cell_seq: torch.Tensor) -> torch.Tensor:
        pix = self.backbone.jepa_logits(cell_seq)
        return pix.flatten(2, 3).unsqueeze(-2)

    def jepa_features(self, cell_seq: torch.Tensor) -> torch.Tensor:
        return self.backbone.jepa_features(cell_seq)

    def heads_from_memory_sequence(self, h2: torch.Tensor) -> dict:
        raise RuntimeError(
            "teacher→actor/critic STE is not wired for the KDA VDA RL agent"
        )
