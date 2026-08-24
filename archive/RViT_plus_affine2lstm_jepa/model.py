"""
Affine + dual-xLSTM recurrent ViT without the VAE front-end.

This variant keeps the cue-orienting affine feedback mechanism:

    X' = Gamma(H1) * X + beta(H1)
    Z  = X + SA(X')
    H1 = LSTM1(Z)
    H2 = LSTM2(H1)

but replaces the VAE patch front-end with a moderate conv patchifier that emits a
4x4 token grid. It also exposes a sequential JEPA objective: the online/student
projects H2_t, predicts the next latent, and matches an EMA teacher projection of
H2_{t+1}. RL and JEPA are trained together from scratch.
"""
from __future__ import annotations

import os
import sys
from typing import List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

_PAPER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "RViT_plus_paper")
if _PAPER not in sys.path:
    sys.path.insert(0, _PAPER)

from paper_encoder import RecurrentViTxLSTM  # noqa: E402
from paper_heads import FFActor, QRCritic    # noqa: E402


D_MODEL = 140
D_MEM = 1024
GRID = 4
N_TOKENS = GRID * GRID


class ConvPatchFrontEnd(nn.Module):
    """50x50 RGB frame -> 4x4 tokens with d_model channels."""

    def __init__(self, d_model: int = D_MODEL, seq_len: int = 7) -> None:
        super().__init__()
        self.d_model = int(d_model)
        self.seq_len = int(seq_len)
        self.net = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=5, stride=2, padding=2), nn.GroupNorm(8, 32), nn.GELU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1), nn.GroupNorm(8, 64), nn.GELU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1), nn.GroupNorm(8, 128), nn.GELU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=2, padding=1), nn.GroupNorm(8, 128), nn.GELU(),
            nn.Conv2d(128, d_model, kernel_size=3, padding=1), nn.GroupNorm(10, d_model), nn.GELU(),
        )
        self.pos = nn.Parameter(torch.randn(1, N_TOKENS, d_model) * 0.02)
        self.time = nn.Parameter(torch.randn(1, max(seq_len, 16), d_model) * 0.02)
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor, t: int) -> torch.Tensor:
        y = self.net(x)
        tokens = y.flatten(2).transpose(1, 2).contiguous()  # (B, 16, d_model)
        t_idx = min(int(t), self.time.shape[1] - 1)
        tokens = tokens + self.pos + self.time[:, t_idx:t_idx + 1]
        return self.norm(tokens)


class JEPAHead(nn.Module):
    """Project H2 tokens into the JEPA latent space and predict the next latent."""

    def __init__(self, d_mem: int = D_MEM, latent_dim: int = 256, hidden: int = 512) -> None:
        super().__init__()
        self.projector = nn.Sequential(
            nn.LayerNorm(d_mem),
            nn.Linear(d_mem, hidden), nn.GELU(),
            nn.Linear(hidden, latent_dim),
        )
        self.predictor = nn.Sequential(
            nn.LayerNorm(latent_dim),
            nn.Linear(latent_dim, hidden), nn.GELU(),
            nn.Linear(hidden, latent_dim),
        )

    def project(self, h: torch.Tensor) -> torch.Tensor:
        return self.projector(h)

    def predict(self, z: torch.Tensor) -> torch.Tensor:
        return self.predictor(z)


class Affine2LSTMJEPAModel(nn.Module):
    def __init__(
        self,
        n_actions: int = 2,
        n_quantiles: int = 5,
        init_action_bias: Optional[List[float]] = None,
        seq_len: int = 7,
        jepa_latent_dim: int = 256,
        **_ignore,
    ) -> None:
        super().__init__()
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.feedback = "affine"
        self.two_lstm = True
        self.enc_layers = 2

        self.front = ConvPatchFrontEnd(d_model=D_MODEL, seq_len=seq_len)
        self.encoder = RecurrentViTxLSTM(
            d_token=D_MODEL, d_mem=D_MEM, n_patch=N_TOKENS,
            feedback="affine", two_lstm=True,
        )
        self.n_tokens = self.encoder.n_patch
        readout_dim = self.n_tokens * D_MEM
        self.actor_head = FFActor(readout_dim, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(readout_dim, n_actions, n_quantiles)
        self.jepa = JEPAHead(d_mem=D_MEM, latent_dim=jepa_latent_dim)

    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        return (self.encoder.init_states(batch_size, device=device, dtype=dtype), 0)

    @staticmethod
    def _to_bchw(x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
            x = x.permute(0, 3, 1, 2)
        return x.contiguous()

    def _run_heads(self, h_flat: torch.Tensor):
        actor_logits = self.actor_head(h_flat)
        q_dist = self.critic_head(h_flat)
        v_dist, v_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, v_dist, v_scalar

    def rl_step(self, x_t: torch.Tensor, prev_states, return_attn: bool = False,
                attn_clamp=None, **_ignore) -> dict:
        enc_state, t = prev_states
        X = self.front(self._to_bchw(x_t), t)
        new_enc, h2, attn = self.encoder.forward_step(
            X, enc_state, return_attn=return_attn, attn_clamp=attn_clamp,
        )
        h_flat = h2.flatten(1)
        actor_logits, q_dist, v_dist, v_scalar = self._run_heads(h_flat)
        return {
            "new_states": (new_enc, t + 1),
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": v_dist,
            "V_scalar": v_scalar,
            "attn": [attn] if attn is not None else None,
            "rec": h_flat,
            "h2": h2,
        }

    def forward_rl_sequence(self, x_video: torch.Tensor, return_attn: bool = False,
                            **_ignore) -> dict:
        B, T = x_video.shape[:2]
        enc_state = self.encoder.init_states(B, device=x_video.device, dtype=x_video.dtype)
        a_seq, q_seq, vd_seq, vs_seq, h2_seq, attn_seq = [], [], [], [], [], []
        for t in range(T):
            X = self.front(self._to_bchw(x_video[:, t]), t)
            enc_state, h2, attn = self.encoder.forward_step(X, enc_state, return_attn=return_attn)
            if return_attn and attn is not None:
                attn_seq.append(attn)
            h_flat = h2.flatten(1)
            a, q, vd, vs = self._run_heads(h_flat)
            a_seq.append(a); q_seq.append(q); vd_seq.append(vd); vs_seq.append(vs); h2_seq.append(h2)
        out = {
            "actor_logits_seq": torch.stack(a_seq, dim=1),
            "q_dist_seq": torch.stack(q_seq, dim=1),
            "V_dist_seq": torch.stack(vd_seq, dim=1),
            "V_scalar_seq": torch.stack(vs_seq, dim=1),
            "h2_seq": torch.stack(h2_seq, dim=1),  # (B, T, 16, 1024)
            "recons": [],
        }
        if return_attn and attn_seq:
            out["attn_seq"] = torch.stack(attn_seq, dim=1)
        return out

    def jepa_student_prediction(self, h2_t: torch.Tensor) -> torch.Tensor:
        z = self.jepa.project(h2_t)
        return self.jepa.predict(z)

    def jepa_teacher_latent(self, h2_t1: torch.Tensor) -> torch.Tensor:
        return self.jepa.project(h2_t1)


def sequential_jepa_loss(
    student: Affine2LSTMJEPAModel,
    teacher: Affine2LSTMJEPAModel,
    student_out: dict,
    teacher_out: dict,
    valid_mask: torch.Tensor,
) -> torch.Tensor:
    """Predict EMA-teacher H2_{t+1} latents from online H2_t latents."""
    h_now = student_out["h2_seq"][:, :-1]      # (B, T-1, N, D)
    h_next = teacher_out["h2_seq"][:, 1:]
    pair_mask = (valid_mask[:, :-1] * valid_mask[:, 1:]).unsqueeze(-1).unsqueeze(-1)
    pred = student.jepa_student_prediction(h_now)
    with torch.no_grad():
        target = teacher.jepa_teacher_latent(h_next)
        target = F.layer_norm(target, target.shape[-1:])
    pred = F.layer_norm(pred, pred.shape[-1:])
    per = F.smooth_l1_loss(pred, target.detach(), reduction="none").mean(dim=(-1, -2))
    denom = pair_mask.squeeze(-1).squeeze(-1).sum().clamp(min=1.0)
    return (per * pair_mask.squeeze(-1).squeeze(-1)).sum() / denom
