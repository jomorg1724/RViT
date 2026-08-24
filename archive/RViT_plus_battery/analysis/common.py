"""
Shared analysis helpers for the FiLM battery (E5/E6).

COMPUTE NOTE: these load a model and run rollouts. They hard-cap threads and default
to CPU so they are safe to run alongside nothing — but DO NOT run them while the live
MPS training jobs are going (laptop CPU must not be over-subscribed). Run them after
training is stopped, or on a machine that's idle.
"""
from __future__ import annotations

import os
# hard thread caps BEFORE importing torch (laptop-CPU safety)
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import sys
from typing import Dict, List, Optional

import numpy as np
import torch

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

torch.set_num_threads(2)

from envs import make_env, task_grid                 # noqa: E402
from model import RViTPlusModel                   # noqa: E402


def load_model(checkpoint_path: str, task: Optional[str] = None,
               device: str = "cpu") -> RViTPlusModel:
    """Rebuild a model from a checkpoint. Prefers saved model_kwargs; falls back to
    the task grid + defaults if only a state_dict is present."""
    ckpt = torch.load(checkpoint_path, map_location=device)
    mk = ckpt.get("model_kwargs")
    if mk is None:
        if task is None:
            raise ValueError("checkpoint has no model_kwargs; pass --task to rebuild")
        gr, gc = task_grid(task)
        mk = dict(in_channels=3, image_h=50, image_w=50, grid_rows=gr, grid_cols=gc,
                  front_end="pixel", d_model=128, d_mem=128, tx_heads=1, n_lstm=2,
                  conv_channels=64, n_conv_layers=2, conv_kernel=3,
                  n_actions=2, n_quantiles=51, init_action_bias=[0.0, -1.5], seq_len=29)
    model = RViTPlusModel(**mk).to(device)
    sd = ckpt.get("model_state_dict", ckpt)
    model.load_state_dict(sd, strict=False)
    model.eval()
    return model


@torch.no_grad()
def rollout(model: RViTPlusModel, env, n_trials: int = 2000, device: str = "cpu",
            greedy: bool = True, collect_attn: bool = False) -> Dict[str, np.ndarray]:
    """Run n_trials episodes; return per-trial records. If collect_attn, also returns
    the per-stimulus attention TO each token over time (properly normalised, one value
    per stimulus per frame) — the FIXED visualization (no quadrant averaging)."""
    recs: List[dict] = []
    attn_by_t: Dict[int, list] = {}
    N = model.n_tokens
    for _ in range(n_trials):
        obs = env.reset()
        states = model.init_states(1, device=device)
        declared_t = -1
        for t in range(env.T):
            x = torch.from_numpy(np.transpose(obs, (2, 0, 1))).float().unsqueeze(0).to(device)
            out = model.rl_step(x, states, return_attn=collect_attn)
            states = out["new_states"]
            if collect_attn and out["attn"] is not None:
                aw = out["attn"][0]                       # (1, n_heads, N, N)
                # attention PAID TO each stimulus token = mean over heads & queries
                per_stim = aw.mean(dim=(0, 1, 2)).cpu().numpy()   # (N,)
                attn_by_t.setdefault(t, []).append((env.cue_index, env.proportion, per_stim))
            logits = out["actor_logits"][0]
            act = int(torch.argmax(logits)) if greedy else int(torch.distributions.Categorical(
                logits=logits).sample())
            obs, reward, done, info = env.step(act)
            if act == 1 and declared_t < 0:
                declared_t = t
            if done:
                break
        change = int(env.change_true)
        ct = int(env.change_time)
        hit = int(change == 1 and declared_t >= ct)
        fa = int(change == 0 and declared_t >= 0)
        rt = (declared_t - ct) if hit else np.nan
        recs.append(dict(change=change, change_time=ct, cue_index=int(env.cue_index),
                         change_index=int(env.change_index), proportion=float(env.proportion),
                         valid=int(env.valid), cue_color=getattr(env, "cue_color", "white"),
                         delta=float(env.orientation_change), declared_t=declared_t,
                         hit=hit, fa=fa, rt=rt))
    out = {k: np.array([r[k] for r in recs]) for k in recs[0]}
    if collect_attn:
        out["_attn_by_t"] = attn_by_t                     # dict t -> list[(cue,prop,(N,))]
    return out


def sdt(hit_rate: float, fa_rate: float):
    """d' and criterion with a (0,1) clamp."""
    from math import erf, sqrt
    def z(p):
        p = min(max(p, 1e-3), 1 - 1e-3)
        # inverse normal CDF via bisection on erf
        lo, hi = -6.0, 6.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if 0.5 * (1 + erf(mid / sqrt(2))) < p:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)
    zh, zf = z(hit_rate), z(fa_rate)
    return dict(dprime=zh - zf, criterion=-0.5 * (zh + zf))
