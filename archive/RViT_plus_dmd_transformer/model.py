"""
DMD-feature transformer.

This experiment removes learned visual convolution entirely. Each frame is split
into four 25x25 quadrants. For each quadrant, exact DMD is computed over the
available history in the current episode prefix; the top 10 eigenvalues are
represented as (real, imag) pairs and fed as four tokens into a standard
TransformerEncoder. The transformer output is flattened for actor and critic.

DMD is a fixed, non-learned feature extractor. The eigensolve runs on CPU because
MPS support for small complex eigensystems is uneven; the resulting features are
moved back to the model device before the transformer.
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

from paper_heads import FFActor, QRCritic  # noqa: E402


N_PATCHES = 4
PATCH = 25
TOP_K = 20
FEATURE_DIM = TOP_K * 2
D_MODEL = 256


def _to_bchw(x: torch.Tensor) -> torch.Tensor:
    if x.dim() == 4 and x.shape[-1] == 3 and x.shape[1] != 3:
        x = x.permute(0, 3, 1, 2)
    return x.contiguous()


def _quadrants_gray(x_bchw: torch.Tensor) -> torch.Tensor:
    """Return flattened grayscale quadrants: (B, 4, 625)."""
    gray = x_bchw.mean(dim=1)
    patches = [
        gray[:, :PATCH, :PATCH],
        gray[:, :PATCH, PATCH:],
        gray[:, PATCH:, :PATCH],
        gray[:, PATCH:, PATCH:],
    ]
    return torch.stack([p.flatten(1) for p in patches], dim=1)


def _top_dmd_eigs(snapshots: torch.Tensor, top_k: int = TOP_K) -> torch.Tensor:
    """Exact DMD eigenvalues for snapshots shaped (n_features, n_times)."""
    out = torch.zeros(top_k, 2, dtype=torch.float32)
    if snapshots.shape[1] < 2:
        return out.flatten()
    X1 = snapshots[:, :-1]
    X2 = snapshots[:, 1:]
    # DMD is scale-sensitive; centering each pixel time series removes DC offset.
    X1 = X1 - X1.mean(dim=1, keepdim=True)
    X2 = X2 - X2.mean(dim=1, keepdim=True)
    try:
        U, S, Vh = torch.linalg.svd(X1, full_matrices=False)
        r = int(min(top_k, (S > 1e-6).sum().item(), U.shape[1]))
        if r <= 0:
            return out.flatten()
        U_r = U[:, :r]
        S_r = S[:r]
        V_r = Vh[:r].T
        A_tilde = U_r.T @ X2 @ V_r @ torch.diag(1.0 / S_r)
        eigvals = torch.linalg.eigvals(A_tilde)
        order = torch.argsort(eigvals.abs(), descending=True)[:r]
        eigvals = eigvals[order]
        out[:r, 0] = eigvals.real.float()
        out[:r, 1] = eigvals.imag.float()
    except RuntimeError:
        return out.flatten()
    return out.flatten()


class DMDFrontEnd(nn.Module):
    """Episode-prefix DMD features -> four transformer tokens."""

    def __init__(self, d_model: int = D_MODEL, seq_len: int = 7) -> None:
        super().__init__()
        self.seq_len = int(seq_len)
        self.proj = nn.Sequential(
            nn.LayerNorm(FEATURE_DIM),
            nn.Linear(FEATURE_DIM, d_model),
            nn.GELU(),
            nn.LayerNorm(d_model),
        )
        self.pos = nn.Parameter(torch.randn(1, N_PATCHES, d_model) * 0.02)
        self.time = nn.Parameter(torch.randn(1, max(seq_len, 16), d_model) * 0.02)

    @torch.no_grad()
    def dmd_features_from_history(self, history_btc: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        """history_btc: (B, T, 3, 50, 50), lengths: (B,), returns (B, 4, 40)."""
        hist = history_btc.detach().float().cpu()
        lengths_cpu = lengths.detach().cpu().long()
        B = hist.shape[0]
        feats = torch.zeros(B, N_PATCHES, FEATURE_DIM, dtype=torch.float32)
        for b in range(B):
            L = int(lengths_cpu[b].item())
            if L <= 0:
                continue
            frames = hist[b, :L]
            patch_series = _quadrants_gray(frames)  # (L, 4, 625)
            for p in range(N_PATCHES):
                snapshots = patch_series[:, p].T.contiguous()  # (625, L)
                feats[b, p] = _top_dmd_eigs(snapshots)
        return feats.to(device=history_btc.device, dtype=history_btc.dtype)

    def forward_from_history(self, history_btc: torch.Tensor, lengths: torch.Tensor, t: int) -> torch.Tensor:
        feats = self.dmd_features_from_history(history_btc, lengths)
        tokens = self.proj(feats)
        t_idx = min(int(t), self.time.shape[1] - 1)
        return tokens + self.pos + self.time[:, t_idx:t_idx + 1]


class DMDTransformerModel(nn.Module):
    def __init__(
        self,
        n_actions: int = 2,
        n_quantiles: int = 5,
        init_action_bias: Optional[List[float]] = None,
        seq_len: int = 7,
        d_model: int = D_MODEL,
        n_heads: int = 1,
        n_layers: int = 2,
        **_ignore,
    ) -> None:
        super().__init__()
        if init_action_bias is None:
            init_action_bias = [0.0, -1.5]
        self.n_actions = int(n_actions)
        self.n_quantiles = int(n_quantiles)
        self.seq_len = int(seq_len)
        self.n_tokens = N_PATCHES + 1
        self.enc_layers = int(n_layers)

        self.front = DMDFrontEnd(d_model=d_model, seq_len=seq_len)
        self.cls = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=4 * d_model,
            dropout=0.0, activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=n_layers)
        readout_dim = d_model
        self.actor_head = FFActor(readout_dim, n_actions, init_action_bias=init_action_bias)
        self.critic_head = QRCritic(readout_dim, n_actions, n_quantiles)

    def init_states(self, batch_size: int, device=None, dtype=torch.float32):
        history = torch.zeros(batch_size, self.seq_len, 3, 50, 50, device=device, dtype=dtype)
        lengths = torch.zeros(batch_size, device=device, dtype=torch.long)
        return history, lengths

    def _run_heads(self, h_flat: torch.Tensor):
        actor_logits = self.actor_head(h_flat)
        q_dist = self.critic_head(h_flat)
        v_dist, v_scalar = self.critic_head.derive_V(q_dist, actor_logits)
        return actor_logits, q_dist, v_dist, v_scalar

    def _encode_from_history(self, history: torch.Tensor, lengths: torch.Tensor, t: int) -> torch.Tensor:
        tokens = self.front.forward_from_history(history, lengths, t)
        cls = self.cls.expand(tokens.shape[0], -1, -1)
        tokens = torch.cat([cls, tokens], dim=1)
        return self.encoder(tokens)

    def rl_step(self, x_t: torch.Tensor, prev_states, return_attn: bool = False,
                attn_clamp=None, **_ignore) -> dict:
        history, lengths = prev_states
        t = int(lengths.max().item())
        x = _to_bchw(x_t)
        idx = min(t, self.seq_len - 1)
        history = history.clone()
        history[:, idx] = x
        lengths = (lengths + 1).clamp(max=self.seq_len)
        enc = self._encode_from_history(history, lengths, idx)
        cls = enc[:, 0]
        actor_logits, q_dist, v_dist, v_scalar = self._run_heads(cls)
        return {
            "new_states": (history, lengths),
            "new_c3_specialists": {},
            "actor_logits": actor_logits,
            "critic_q_dist": q_dist,
            "V_dist": v_dist,
            "V_scalar": v_scalar,
            "attn": None,
            "rec": cls,
            "dmd_tokens": enc,
        }

    def forward_rl_sequence(self, x_video: torch.Tensor, return_attn: bool = False,
                            **_ignore) -> dict:
        B, T = x_video.shape[:2]
        history = torch.zeros(B, self.seq_len, 3, 50, 50, device=x_video.device, dtype=x_video.dtype)
        lengths = torch.zeros(B, device=x_video.device, dtype=torch.long)
        a_seq, q_seq, vd_seq, vs_seq, tok_seq = [], [], [], [], []
        for t in range(T):
            x = _to_bchw(x_video[:, t])
            idx = min(t, self.seq_len - 1)
            history[:, idx] = x
            lengths = (lengths + 1).clamp(max=self.seq_len)
            enc = self._encode_from_history(history, lengths, idx)
            cls = enc[:, 0]
            a, q, vd, vs = self._run_heads(cls)
            a_seq.append(a); q_seq.append(q); vd_seq.append(vd); vs_seq.append(vs); tok_seq.append(enc)
        return {
            "actor_logits_seq": torch.stack(a_seq, dim=1),
            "q_dist_seq": torch.stack(q_seq, dim=1),
            "V_dist_seq": torch.stack(vd_seq, dim=1),
            "V_scalar_seq": torch.stack(vs_seq, dim=1),
            "dmd_token_seq": torch.stack(tok_seq, dim=1),
            "recons": [],
        }
