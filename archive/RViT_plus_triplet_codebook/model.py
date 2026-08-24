"""
Triplet-codebook recurrent ViT.

Flow:
    frame -> conv 4x4 patchifier -> X
    Q = Q(X)
    K = concat(K1(f1(H1)), K2(f2(H1)), K3(f3(H1)))
    V = concat(V1(H_CB1), V2(H_CB2), V3(H_CB3))
    Z = softmax(QK^T / sqrt(d)) V            # no residual; selected codebook values only
    H1 = xLSTM(X + Z, H1)                    # memory integrates vision + selected code
    actor/critic read flatten(Z)

The codebooks are learned embeddings. This is a continuous codebook lookup: H1
constructs the key-space, X asks the query, and the selected values become the
agent-facing representation.
"""
from __future__ import annotations

import os
import sys
from typing import List, Optional

import torch
import torch.nn as nn

_PAPER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RViT_plus_paper")
if _PAPER not in sys.path:
    sys.path.insert(0, _PAPER)

from paper_encoder import SpatialXLSTM  # noqa: E402
from paper_heads import FFActor, QRCritic  # noqa: E402


D_MODEL = 140
D_MEM = 1024
GRID = 4
N_TOKENS = GRID * GRID
N_CODEBOOKS = 3


class ConvPatchFrontEnd(nn.Module):
    """50x50 RGB frame -> 4x4 tokens."""

    def __init__(self, d_model: int = D_MODEL, seq_len: int = 7) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5, stride=2, padding=2), nn.GroupNorm(8, 32), nn.GELU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1), nn.GroupNorm(8, 64), nn.GELU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1), nn.GroupNorm(8, 128), nn.GELU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=2, padding=1), nn.GroupNorm(8, 128), nn.GELU(),
            nn.Conv2d(128, d_model, kernel_size=3, padding=1), nn.GroupNorm(10, d_model), nn.GELU(),
        )
        self.pos = nn.Parameter(torch.randn(1, N_TOKENS, d_model) * 0.02)
        self.time = nn.Parameter(torch.randn(1, max(int(seq_len), 16), d_model) * 0.02)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor, t: int) -> torch.Tensor:
        y = self.net(x)
        tokens = y.flatten(2).transpose(1, 2).contiguous()
        t_idx = min(int(t), self.time.shape[1] - 1)
        return self.norm(tokens + self.pos + self.time[:, t_idx:t_idx + 1])


class TripletCodebookAttention(nn.Module):
    """Continuous lookup over three learned codebooks."""

    def __init__(
        self,
        d_token: int = D_MODEL,
        d_mem: int = D_MEM,
        n_tokens: int = N_TOKENS,
        n_codebooks: int = N_CODEBOOKS,
    ) -> None:
        super().__init__()
        self.d_token = d_token
        self.n_tokens = n_tokens
        self.n_codebooks = n_codebooks
        self.W_q = nn.Linear(d_token, d_token, bias=False)
        self.mem_features = nn.ModuleList([
            nn.Sequential(nn.LayerNorm(d_mem), nn.Linear(d_mem, d_token), nn.GELU())
            for _ in range(n_codebooks)
        ])
        self.W_k = nn.ModuleList([nn.Linear(d_token, d_token, bias=False) for _ in range(n_codebooks)])
        self.codebooks = nn.Parameter(torch.randn(n_codebooks, n_tokens, d_token) * 0.02)
        self.scale = d_token ** -0.5

    def forward(self, X: torch.Tensor, H_prev: torch.Tensor, return_attn: bool = False):
        B = X.shape[0]
        Q = self.W_q(X)
        keys = []
        vals = []
        for i in range(self.n_codebooks):
            keys.append(self.W_k[i](self.mem_features[i](H_prev)))
            cb = self.codebooks[i].unsqueeze(0).expand(B, -1, -1)
            vals.append(cb)
        K = torch.cat(keys, dim=1)  # (B, 3N, d)
        V = torch.cat(vals, dim=1)  # (B, 3N, d)
        attn = torch.softmax(torch.matmul(Q, K.transpose(-1, -2)) * self.scale, dim=-1)
        Z = torch.matmul(attn, V)
        return (Z, attn) if return_attn else (Z, None)


class TripletCodebookEncoder(nn.Module):
    def __init__(self, d_token: int = D_MODEL, d_mem: int = D_MEM, n_tokens: int = N_TOKENS) -> None:
        super().__init__()
        self.n_patch = n_tokens
        self.d_token = d_token
        self.d_mem = d_mem
        self.attn = TripletCodebookAttention(d_token=d_token, d_mem=d_mem, n_tokens=n_tokens)
        self.lstm = SpatialXLSTM(d_token, d_mem)
        self.readout_dim = n_tokens * d_token

    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        z = torch.zeros(batch_size, self.n_patch, self.d_mem, device=device, dtype=dtype)
        return z, z.clone(), z.clone(), z.clone()

    def forward_step(self, X: torch.Tensor, state, return_attn: bool = False, attn_clamp=None):
        H_prev, C_prev, N_prev, M_prev = state
        Z, attn = self.attn(X, H_prev, return_attn=return_attn)
        H, C, N, M = self.lstm(X + Z, H_prev, C_prev, N_prev, M_prev)
        return (H, C, N, M), Z, attn


class TripletCodebookModel(nn.Module):
    def __init__(
        self,
        n_actions: int = 2,
        n_quantiles: int = 5,
        init_action_bias: Optional[List[float]] = None,
        seq_len: int = 7,
        **_ignore,
    ) -> None:
        super().__init__()
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.feedback = "triplet_codebook"
        self.two_lstm = False
        self.enc_layers = 1

        self.front = ConvPatchFrontEnd(d_model=D_MODEL, seq_len=seq_len)
        self.encoder = TripletCodebookEncoder(d_token=D_MODEL, d_mem=D_MEM, n_tokens=N_TOKENS)
        self.n_tokens = self.encoder.n_patch
        readout_dim = self.encoder.readout_dim
        self.actor_head = FFActor(readout_dim, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(readout_dim, n_actions, n_quantiles)

    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        return self.encoder.init_states(batch_size, device=device, dtype=dtype), 0

    @staticmethod
    def _to_bchw(x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        return x.contiguous()

    def _run_heads(self, z_flat: torch.Tensor):
        actor_logits = self.actor_head(z_flat)
        q_dist = self.critic_head(z_flat)
        v_dist, v_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, v_dist, v_scalar

    def rl_step(self, x_t: torch.Tensor, prev_states, return_attn: bool = False,
                attn_clamp=None, **_ignore) -> dict:
        enc_state, t = prev_states
        X = self.front(self._to_bchw(x_t), t)
        new_enc, Z, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn)
        z_flat = Z.flatten(1)
        actor_logits, q_dist, v_dist, v_scalar = self._run_heads(z_flat)
        return {
            "new_states": (new_enc, t + 1),
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": v_dist,
            "V_scalar": v_scalar,
            "attn": [attn] if attn is not None else None,
            "rec": z_flat,
            "codebook_z": Z,
        }

    def forward_rl_sequence(self, x_video: torch.Tensor, return_attn: bool = False,
                            **_ignore) -> dict:
        B, T = x_video.shape[:2]
        enc_state = self.encoder.init_states(B, device=x_video.device, dtype=x_video.dtype)
        a_seq, q_seq, vd_seq, vs_seq, z_seq, attn_seq = [], [], [], [], [], []
        for t in range(T):
            X = self.front(self._to_bchw(x_video[:, t]), t)
            enc_state, Z, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn)
            if return_attn and attn is not None:
                attn_seq.append(attn)
            z_flat = Z.flatten(1)
            a, q, vd, vs = self._run_heads(z_flat)
            a_seq.append(a); q_seq.append(q); vd_seq.append(vd); vs_seq.append(vs); z_seq.append(Z)
        out = {
            "actor_logits_seq": torch.stack(a_seq, dim=1),
            "q_dist_seq": torch.stack(q_seq, dim=1),
            "V_dist_seq": torch.stack(vd_seq, dim=1),
            "V_scalar_seq": torch.stack(vs_seq, dim=1),
            "codebook_z_seq": torch.stack(z_seq, dim=1),
            "recons": [],
        }
        if return_attn and attn_seq:
            out["attn_seq"] = torch.stack(attn_seq, dim=1)
        return out
