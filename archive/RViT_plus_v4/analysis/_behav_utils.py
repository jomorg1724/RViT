"""
Shared harness for RViT+ v4 behavioral / attention analyses (the "first-look" SOP).

Ported from RViT_plus_v3/analysis/_behav_utils.py. The env (ChangeDetectionEnv)
and the forced-trial mechanism are IDENTICAL; only the model-specific pieces
change for v4:
  * build_model     → constructs RViTPlusV4Model from the v4 config
  * rollouts        → drive the model via `model.rl_step` (patchify + feedback
                      transformer + actor/critic); no conv stem, no C₃ specialists
  * attention       → v4 attention is token×token over the patch grid, not a
                      spatial conv softmax. We extract per-layer attention via
                      encoder.forward_step(..., return_attn=True), reduce to a
                      per-key saliency map (mean over heads & query patches), and
                      reshape to the (grid_h, grid_w) patch grid. For the default
                      50×50 / patch 5 that is 10×10, and the H/2×W/2 quadrant
                      split lands exactly on the 4 Gabor quadrants.

Env timing semantics (unchanged from v2/v3):
    t=0 blank · t=1 cue · t=2 blank · t=3 gabors · t≥Tc changed gabor.
    press at t<Tc → premature (false alarm); press at t≥Tc on a change trial → HIT.
    RT = press_index − change_time, defined on hits.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v4.env import ChangeDetectionEnv
from RViT_plus_v4.model import RViTPlusV4Model

# Quadrant index each cue points to (env._next_observation layout):
#   0 = top-left, 1 = bottom-left, 2 = top-right, 3 = bottom-right
#   cue 'left' → top-left (0);  cue 'right' → bottom-right (3)
CUED_QUADRANT = {"left": 0, "right": 3}
ALL_QUADRANTS = [0, 1, 2, 3]
COLOR_VALUE = {"red": 5, "green": 3, "blue": 1}


# ── device + model ──────────────────────────────────────────────────────────


def select_device(arg: str = "") -> torch.device:
    if arg:
        return torch.device(arg)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_config(path: Optional[str] = None) -> dict:
    if path is None:
        path = os.path.join(_PROJECT_ROOT, "RViT_plus_v4", "config", "rvit_plus_config.json")
    with open(path) as f:
        return json.load(f)


def build_model(cfg: dict, device: torch.device) -> RViTPlusV4Model:
    """Construct the v4 model exactly as train_rl.py does, from the config."""
    m = cfg["model"]
    rl = m["rl"]
    model = RViTPlusV4Model(
        in_channels=3, image_h=50, image_w=50,
        patch_size=int(m["patch_size"]),
        patch_hidden=int(m.get("patch_hidden", m["d_model"])),
        d_model=int(m["d_model"]),
        d_mem=int(m["d_mem"]),
        enc_heads=int(m["enc_heads"]),
        enc_layers=int(m["enc_layers"]),
        n_FR=int(m["n_FR"]),
        dec_heads=int(m["dec_heads"]),
        dec_layers=int(m["dec_layers"]),
        n_actions=int(rl["n_actions"]),
        n_quantiles=int(rl["n_quantiles"]),
        init_action_bias=list(rl["init_action_bias"]),
        seq_len=int(cfg["ppo"]["seq_len"]),
        head_hidden=int(m.get("head_hidden", m["d_model"])),
        head_layers=int(m.get("head_layers", 2)),
    ).to(device)
    return model


def load_checkpoint(model: RViTPlusV4Model, ckpt_path: str, device: torch.device) -> int:
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    missing, unexpected = model.load_state_dict(sd, strict=False)
    if missing:
        print(f"[load] WARNING missing keys ({len(missing)}): {missing[:6]}{'...' if len(missing) > 6 else ''}")
    if unexpected:
        print(f"[load] WARNING unexpected keys ({len(unexpected)}): {unexpected[:6]}{'...' if len(unexpected) > 6 else ''}")
    model.eval()
    return int(ckpt.get("iter", -1))


# ── forced trial specs (identical to v3) ────────────────────────────────────


@dataclass
class ForcedTrialSpec:
    """A per-trial condition. Fields left None are randomized by reset()."""
    cue_position: Optional[str] = None       # 'left' / 'right'
    cue_color: Optional[str] = None          # 'red' / 'green' / 'blue'
    proportion: Optional[float] = None       # ring validity 0.25..1.0
    change_true: Optional[int] = None        # 0 / 1
    change_time: Optional[int] = None        # frame the change appears
    change_index_mode: object = None         # 'cued' / 'uncued' / int / None
    orientation_mag: Optional[float] = None  # |Δθ| in degrees


def reset_with_spec(env: ChangeDetectionEnv, spec: ForcedTrialSpec, rng: np.random.Generator) -> np.ndarray:
    """Reset env, then override fields per spec. Returns the t=0 observation."""
    env.reset()
    if spec.cue_position is not None:
        env.cue_position = spec.cue_position
    if spec.cue_color is not None:
        env.cue_color = spec.cue_color
    if spec.proportion is not None:
        env.proportion = float(spec.proportion)
    if spec.change_true is not None:
        env.change_true = int(spec.change_true)
    if spec.change_time is not None:
        env.change_time = int(spec.change_time)
    if spec.orientation_mag is not None:
        sign = 1.0 if rng.random() < 0.5 else -1.0
        env.orientation_change = float(sign * spec.orientation_mag)
    mode = spec.change_index_mode
    if mode is not None and int(env.change_true) == 1:
        if mode == "cued":
            env.change_index = CUED_QUADRANT[env.cue_position]
        elif mode == "uncued":
            cued = CUED_QUADRANT[env.cue_position]
            choices = [q for q in ALL_QUADRANTS if q != cued]
            env.change_index = int(rng.choice(choices))
        elif isinstance(mode, int):
            env.change_index = int(mode)
        else:
            raise ValueError(f"bad change_index_mode: {mode!r}")
    env.t = 0
    return env._next_observation()


def build_env_batch(
    base_spec: ForcedTrialSpec,
    n_trials: int,
    rng: np.random.Generator,
    *,
    env_kwargs: Optional[dict] = None,
    randomize_cue_position: bool = False,
    randomize_color: bool = False,
) -> Tuple[List[ChangeDetectionEnv], List[np.ndarray]]:
    """Create `n_trials` reset+spec'd envs sharing `base_spec`."""
    env_kwargs = env_kwargs or {}
    envs: List[ChangeDetectionEnv] = []
    obs0: List[np.ndarray] = []
    for _ in range(n_trials):
        spec = ForcedTrialSpec(**base_spec.__dict__)
        if randomize_cue_position:
            spec.cue_position = "left" if rng.random() < 0.5 else "right"
        if randomize_color:
            spec.cue_color = str(rng.choice(["red", "green", "blue"]))
        env = ChangeDetectionEnv(**env_kwargs)
        o = reset_with_spec(env, spec, rng)
        envs.append(env)
        obs0.append(o)
    return envs, obs0


# ── batched rollouts (v4: driven by rl_step) ────────────────────────────────


def _obs_to_tensor(obs_list: Sequence[np.ndarray], device: torch.device) -> torch.Tensor:
    """Stack a list of (50,50,3) HWC frames into (B,3,50,50) CHW."""
    arr = np.stack([np.asarray(o, dtype=np.float32) for o in obs_list], axis=0)  # (B,50,50,3)
    return torch.from_numpy(arr).to(device).permute(0, 3, 1, 2).contiguous()


@torch.no_grad()
def batched_behavior_rollout(
    model: RViTPlusV4Model,
    envs: List[ChangeDetectionEnv],
    obs0: List[np.ndarray],
    device: torch.device,
) -> Dict[str, np.ndarray]:
    """Run B trials in parallel under the model's argmax policy (via rl_step).
    Returns per-trial arrays: pressed / press_index / change_time / change_true /
    hit / premature / rt / reward."""
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)

    obs = list(obs0)
    done = np.zeros(B, dtype=bool)
    press_index = np.full(B, -1, dtype=np.int64)
    reward = np.zeros(B, dtype=np.float32)
    change_time = np.array([int(e.change_time) for e in envs], dtype=np.int64)
    change_true = np.array([int(e.change_true) for e in envs], dtype=np.int64)

    T = envs[0].T
    t = 0
    while (not done.all()) and t <= T:
        x = _obs_to_tensor(obs, device)
        step = model.rl_step(x, states)
        states = step["new_states"]
        actions = step["actor_logits"].argmax(dim=-1).cpu().numpy().astype(np.int64)
        for i in range(B):
            if done[i]:
                continue
            a = int(actions[i])
            o, r, d, _ = envs[i].step(a)
            obs[i] = o
            if a == 1 and press_index[i] < 0:
                press_index[i] = t
            reward[i] = float(r)
            if d:
                done[i] = True
        t += 1

    pressed = press_index >= 0
    premature = pressed & (press_index < change_time)
    hit = pressed & (press_index >= change_time) & (change_true == 1)
    rt = np.where(hit, press_index - change_time, np.nan).astype(np.float32)
    return {
        "pressed": pressed, "press_index": press_index, "change_time": change_time,
        "change_true": change_true, "hit": hit, "premature": premature,
        "rt": rt, "reward": reward,
    }


@torch.no_grad()
def batched_attention_rollout(
    model: RViTPlusV4Model,
    envs: List[ChangeDetectionEnv],
    obs0: List[np.ndarray],
    device: torch.device,
    n_layers: int = 2,
) -> Tuple[List[np.ndarray], np.ndarray]:
    """Run B trials with action forced to 0 (wait) for the full episode.

    At each timestep, for each feedback layer, take the token-attention weights
    (B, heads, n_tokens, n_tokens) and reduce to a PER-HEAD per-key saliency —
    mean over QUERY tokens only, NOT over heads (heads can attend to opposite
    locations, so head-averaging cancels real structure), reshaped to the
    (grid_h, grid_w) patch grid and averaged over the batch.

    Returns
    -------
    mean_attn  : list of length n_layers; mean_attn[L] has shape (T, n_heads, grid_h, grid_w)
    obs_example: (T, 50, 50, 3) — the first trial's frames, for reference
    """
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    gh, gw = model.patch_embed.grid_h, model.patch_embed.grid_w

    obs = list(obs0)
    T = envs[0].T
    per_layer_frames: List[List[np.ndarray]] = [[] for _ in range(n_layers)]
    obs_example: List[np.ndarray] = []

    t = 0
    done = np.zeros(B, dtype=bool)
    while t <= T and not done.all():
        x = _obs_to_tensor(obs, device)
        obs_example.append(np.asarray(obs[0], dtype=np.float32).copy())
        tokens = model.patch_embed(x)
        states, _rec, attn = model.encoder.forward_step(tokens, states, return_attn=True)
        for L in range(n_layers):
            aw = attn[L]                                  # (B, heads, N_q, N_k)
            sal = aw.mean(dim=2)                          # mean over QUERIES only → (B, heads, N_k)
            grid = sal.view(B, sal.shape[1], gh, gw)      # (B, heads, grid_h, grid_w) row-major
            per_layer_frames[L].append(grid.mean(dim=0).detach().cpu().numpy())  # (heads, gh, gw)
        for i in range(B):
            if done[i]:
                continue
            o, r, d, _ = envs[i].step(0)                  # force wait
            obs[i] = o
            if d:
                done[i] = True
        t += 1

    mean_attn = [np.stack(frames, axis=0) for frames in per_layer_frames]  # (T,gh,gw) each
    return mean_attn, np.stack(obs_example, axis=0)
