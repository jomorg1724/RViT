"""
Fully-CONVOLUTIONAL recurrent ViT — a 2D-spatial version of the recurrent ViT in
which every projection is a conv (no flatten-to-tokens, no FF). Same harness as the
paper build (PAC + QR-DQN + PER + EMA, all RL/buffer settings constant).

Flow (everything lives on a C×10×10 feature grid):
  stem:  image (B,3,50,50) → Conv(k5,s5) → C×10×10              (the big reduction)
  attention (the 2D transformer), per the user's spec:
      Q = Conv_Q([X ‖ H]) ,  K = Conv_K([X ‖ H]) ,  V = Conv_V([X ‖ H])   each (B,C,10,10)
      logits[h,w] = Σ_c Q[c,h,w]·K[c,h,w]      (aligned channel inner product) → (B,10,10)
      α = softmax over the whole 10×10 grid                                    → (B,1,10,10)
      V_filtered = V ⊙ α        (broadcast over channels)
      Z = X + Conv_o(V_filtered)        (residual = X, already C×10×10)
      Z = Z + ConvFFN(Z)                (FFN = conv expand along channels C→4C→C)
  memory: ConvLSTM over the grid:  (H,C_cell) ← ConvLSTM(Z, H, C_cell)        (H is C×10×10)
  heads:  small conv trunks on H → actor logits (2) and QR-DQN critic (A×N quantiles)

The recurrent state is ((H, C_cell), ) — two C×10×10 maps. Heads read the memory map H.
"""
from __future__ import annotations

from typing import Optional, List

import torch
import torch.nn as nn
import torch.nn.functional as F

C_GRID = 64          # channels on the working grid
GRID = 10            # working spatial resolution (10×10)
GN = 8               # GroupNorm groups


def _gn(ch: int) -> nn.GroupNorm:
    return nn.GroupNorm(min(GN, ch), ch)


class ConvStem(nn.Module):
    """image (B,Cin,50,50) → (B,C,10,10) — the big reduction + a same-same conv."""
    def __init__(self, in_ch: int = 3, ch: int = C_GRID) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, ch, kernel_size=5, stride=5),     # 50 → 10
            _gn(ch), nn.GELU(),
            nn.Conv2d(ch, ch, kernel_size=3, padding=1),       # same-same
            _gn(ch), nn.GELU(),
        )

    def forward(self, x):
        return self.net(x)                                     # (B,C,10,10)


class ConvAttention2D(nn.Module):
    """2D conv self-attention with recurrent feedback H (the user's spec)."""
    def __init__(self, ch: int = C_GRID) -> None:
        super().__init__()
        self.norm_in = _gn(2 * ch)
        self.q = nn.Conv2d(2 * ch, ch, kernel_size=3, padding=1)
        self.k = nn.Conv2d(2 * ch, ch, kernel_size=3, padding=1)
        self.v = nn.Conv2d(2 * ch, ch, kernel_size=3, padding=1)
        self.o = nn.Conv2d(ch, ch, kernel_size=1)
        self.norm_ffn = _gn(ch)
        self.ffn = nn.Sequential(
            nn.Conv2d(ch, 4 * ch, kernel_size=3, padding=1), nn.GELU(),
            nn.Conv2d(4 * ch, ch, kernel_size=3, padding=1),
        )
        self.scale = ch ** -0.5

    def forward(self, X, H, return_attn: bool = False):
        inp = self.norm_in(torch.cat([X, H], dim=1))           # (B,2C,10,10)
        Q, K, V = self.q(inp), self.k(inp), self.v(inp)        # each (B,C,10,10)
        B, _, h, w = Q.shape
        logits = (Q * K).sum(dim=1) * self.scale               # (B,10,10) aligned inner product
        attn = torch.softmax(logits.view(B, -1), dim=1).view(B, 1, h, w)   # softmax over grid
        V_filtered = V * attn                                  # broadcast over channels
        Z = X + self.o(V_filtered)                             # residual = X
        Z = Z + self.ffn(self.norm_ffn(Z))                     # conv FFN (expand along channels)
        return (Z, attn) if return_attn else (Z, None)


class ConvLSTMCell(nn.Module):
    """Standard ConvLSTM gate over the grid: (H,C) ← f(Z, H, C)."""
    def __init__(self, ch: int = C_GRID) -> None:
        super().__init__()
        self.gates = nn.Conv2d(2 * ch, 4 * ch, kernel_size=3, padding=1)
        self.ch = ch

    def forward(self, Z, H, Cc):
        i, f, o, g = self.gates(torch.cat([Z, H], dim=1)).chunk(4, dim=1)
        i, f, o = torch.sigmoid(i), torch.sigmoid(f), torch.sigmoid(o)
        g = torch.tanh(g)
        Cc_new = f * Cc + i * g
        H_new = o * torch.tanh(Cc_new)
        return H_new, Cc_new


class ConvActorHead(nn.Module):
    def __init__(self, ch: int = C_GRID, n_actions: int = 2,
                 init_action_bias: Optional[List[float]] = None) -> None:
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Conv2d(ch, ch, 3, stride=2, padding=1), _gn(ch), nn.GELU(),   # 10→5
            nn.Conv2d(ch, ch, 3, stride=2, padding=1), _gn(ch), nn.GELU(),   # 5→3
            nn.AdaptiveAvgPool2d(1),
        )
        self.out = nn.Linear(ch, n_actions)
        if init_action_bias is not None:
            with torch.no_grad():
                self.out.bias.copy_(torch.tensor(init_action_bias, dtype=self.out.bias.dtype))

    def forward(self, H):
        return self.out(self.trunk(H).flatten(1))              # (B, n_actions)


class ConvCriticHead(nn.Module):
    def __init__(self, ch: int = C_GRID, n_actions: int = 2, n_quantiles: int = 5) -> None:
        super().__init__()
        self.n_actions, self.n_quantiles = n_actions, n_quantiles
        self.register_buffer("taus", (torch.arange(n_quantiles, dtype=torch.float32) + 0.5) / n_quantiles)
        self.trunk = nn.Sequential(
            nn.Conv2d(ch, ch, 3, stride=2, padding=1), _gn(ch), nn.GELU(),
            nn.Conv2d(ch, ch, 3, stride=2, padding=1), _gn(ch), nn.GELU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.out = nn.Linear(ch, n_actions * n_quantiles)

    def forward(self, H):
        q = self.out(self.trunk(H).flatten(1))
        return q.view(q.shape[0], self.n_actions, self.n_quantiles)         # (B,A,N)

    def derive_V(self, q_dist, actor_logits):
        pi = torch.softmax(actor_logits, dim=-1).unsqueeze(-1)              # (B,A,1)
        V_dist = (pi * q_dist).sum(dim=-2)                                  # (B,N)
        return V_dist, V_dist.mean(dim=-1)                                  # V_dist, V_scalar


class ConvRViTModel(nn.Module):
    def __init__(self, in_channels: int = 3, ch: int = C_GRID, n_actions: int = 2,
                 n_quantiles: int = 5, init_action_bias: Optional[List[float]] = None,
                 seq_len: int = 7, **_ignore) -> None:
        super().__init__()
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.enc_layers = 1
        self.ch, self.grid = ch, GRID
        self.n_tokens = GRID * GRID

        self.stem = ConvStem(in_channels, ch)
        self.attn = ConvAttention2D(ch)
        self.lstm = ConvLSTMCell(ch)
        self.actor_head = ConvActorHead(ch, n_actions, init_action_bias=init_action_bias)
        self.critic_head = ConvCriticHead(ch, n_actions, n_quantiles)

    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        z = lambda: torch.zeros(batch_size, self.ch, self.grid, self.grid, device=device, dtype=dtype)
        return ((z(), z()),)                                   # ((H, C_cell),)

    @staticmethod
    def _to_bchw(x):
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        return x.contiguous()

    def _run_heads(self, H):
        actor_logits = self.actor_head(H)
        q_dist = self.critic_head(H)
        V_dist, V_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, V_dist, V_scalar

    def _step(self, frame, state, return_attn=False):
        (H, Cc), = state
        X = self.stem(self._to_bchw(frame))
        Z, attn = self.attn(X, H, return_attn=return_attn)
        H_new, Cc_new = self.lstm(Z, H, Cc)
        return ((H_new, Cc_new),), H_new, attn

    def rl_step(self, x_t, prev_states, return_attn: bool = False, **_ignore) -> dict:
        new_state, H_new, attn = self._step(x_t, prev_states, return_attn=return_attn)
        actor_logits, q_dist, V_dist, V_scalar = self._run_heads(H_new)
        return {
            "new_states": new_state, "new_c3_specialists": {},
            "actor_logits": actor_logits, "critic_q_dist": q_dist,
            "V_dist": V_dist, "V_scalar": V_scalar,
            "attn": [attn] if attn is not None else None, "rec": H_new,
        }

    def forward_rl_sequence(self, x_video, return_attn: bool = False, **_ignore) -> dict:
        B, T = x_video.shape[:2]
        state = self.init_states(B, device=x_video.device, dtype=x_video.dtype)
        a_seq, q_seq, vd_seq, vs_seq, attn_seq = [], [], [], [], []
        for t in range(T):
            state, H_new, attn = self._step(x_video[:, t], state, return_attn=return_attn)
            if return_attn and attn is not None:
                attn_seq.append(attn)
            a, q, vd, vs = self._run_heads(H_new)
            a_seq.append(a); q_seq.append(q); vd_seq.append(vd); vs_seq.append(vs)
        out = {
            "actor_logits_seq": torch.stack(a_seq, dim=1),
            "q_dist_seq": torch.stack(q_seq, dim=1),
            "V_dist_seq": torch.stack(vd_seq, dim=1),
            "V_scalar_seq": torch.stack(vs_seq, dim=1),
            "recons": [],
        }
        if return_attn and attn_seq:
            out["attn_seq"] = torch.stack(attn_seq, dim=1)
        return out
