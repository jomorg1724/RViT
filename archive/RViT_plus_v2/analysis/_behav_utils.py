"""
Shared harness for V2 behavioral / attention analyses.

Provides:
  * device selection
  * model construction from the JSON config + checkpoint load
  * a ForcedTrialSpec mechanism to pin specific trial conditions while
    letting the marginalized fields randomize per trial
  * batched rollouts (B trials in parallel through one forward pass):
      - `batched_behavior_rollout`: real argmax policy, records hit / RT
      - `batched_attention_rollout`: action forced to 0 (wait), records the
        channel-summed attention heatmap per layer per timestep, averaged
        over trials

Env timing semantics (ChangeDetectionEnv, V2):
  Observation at loop-index t is generated with env.t == t:
      t = 0     → blank
      t = 1     → cue frame
      t = 2     → blank
      t = 3     → gabors appear
      t ≥ Tc    → the changed gabor is shown (Tc = change_time)
  A press (action=1) at loop-index t calls env.step with t_before == t.
      t  <  Tc  → premature press (reward 0, episode ends)  [false alarm]
      t  ≥  Tc  → if change_true==1: HIT (reward = color value), else 0
  So the change is first VISIBLE at t == Tc and a press there is the
  earliest possible hit. We define:
      change_frame = Tc
      reaction time RT = press_index − Tc   (≥ 0, defined on hits only)
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

from RViT_plus_v2.env import ChangeDetectionEnv
from RViT_plus_v2.model import RViTPlusModel

# Quadrant index that each cue points to (env._next_observation layout):
#   change_index 0 = top-left, 1 = bottom-left, 2 = top-right, 3 = bottom-right
#   cue 'left'  → top-left  (index 0);  cue 'right' → bottom-right (index 3)
CUED_QUADRANT = {"left": 0, "right": 3}
ALL_QUADRANTS = [0, 1, 2, 3]
COLOR_VALUE = {"red": 5, "green": 3, "blue": 1}


# ─────────────────────────────────────────────────────────────────────────────
# Device + model
# ─────────────────────────────────────────────────────────────────────────────


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
        path = os.path.join(_PROJECT_ROOT, "RViT_plus_v2", "config", "rvit_plus_config.json")
    with open(path) as f:
        return json.load(f)


def build_model(cfg: dict, device: torch.device) -> RViTPlusModel:
    """Construct the V2 model exactly as train_rl.py does, reading the config."""
    m = cfg["model"]
    rl = m["rl"]
    seq_len = int(cfg["ppo"]["seq_len"])
    model = RViTPlusModel(
        in_channels=int(m["in_channels"]),
        image_h=int(m["image_h"]),
        image_w=int(m["image_w"]),
        stem_out_channels=int(m["stem_out_channels"]),
        state_channels=tuple(m["state_channels"]),
        n_FR=int(m["n_FR"]),
        n_heads=int(m["n_heads"]),
        seq_len=seq_len,
        upsample_out_channels=int(m["upsample_out_channels"]),
        cnn_hidden=int(m["cnn_hidden"]),
        enable_skips=bool(m["enable_skips"]),
        skip_scale=float(m["skip_scale"]),
        enable_actor=True,
        enable_critic=True,
        n_actions=int(rl["n_actions"]),
        n_quantiles=int(rl["n_quantiles"]),
        rl_per_state_channels=int(rl["rl_per_state_channels"]),
        rl_cnn_hidden=int(rl["rl_cnn_hidden"]),
        init_action_bias=list(rl["init_action_bias"]),
        split_c3=bool(rl["split_c3"]),
    ).to(device)
    return model


def load_checkpoint(model: RViTPlusModel, ckpt_path: str, device: torch.device) -> int:
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    missing, unexpected = model.load_state_dict(sd, strict=False)
    if missing:
        print(f"[load] WARNING missing keys ({len(missing)}): {missing[:6]}{'...' if len(missing) > 6 else ''}")
    if unexpected:
        print(f"[load] WARNING unexpected keys ({len(unexpected)}): {unexpected[:6]}{'...' if len(unexpected) > 6 else ''}")
    model.eval()
    return int(ckpt.get("iter", -1))


# ─────────────────────────────────────────────────────────────────────────────
# Forced trial specs
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ForcedTrialSpec:
    """A per-trial condition. Fields left None are randomized by reset().

    change_index_mode:
      'cued'   → the changed gabor is at the cued quadrant (VALID trial)
      'uncued' → the changed gabor is at a random non-cued quadrant (INVALID)
      int      → explicit quadrant index 0..3
      None     → leave whatever reset() sampled
    orientation_mag:
      if not None, |Δθ| is fixed to this magnitude with a random ± sign.
    """
    cue_position: Optional[str] = None       # 'left' / 'right'
    cue_color: Optional[str] = None          # 'red' / 'green' / 'blue'
    proportion: Optional[float] = None       # ring validity 0.25..1.0
    change_true: Optional[int] = None        # 0 / 1
    change_time: Optional[int] = None        # frame the change appears
    change_index_mode: object = None         # 'cued' / 'uncued' / int / None
    orientation_mag: Optional[float] = None  # |Δθ| in degrees


def reset_with_spec(env: ChangeDetectionEnv, spec: ForcedTrialSpec, rng: np.random.Generator) -> np.ndarray:
    """Reset env, then override fields per spec. Returns the t=0 observation.

    Overriding right after reset() is in time: cue_position/color/proportion are
    read at t=1; change_time/index/orientation at t≥change_time. The t=0 frame
    is blank regardless.
    """
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

    # Resolve change_index relative to (possibly overridden) cue_position.
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


# ─────────────────────────────────────────────────────────────────────────────
# Batched rollouts
# ─────────────────────────────────────────────────────────────────────────────


def _obs_to_tensor(obs_list: Sequence[np.ndarray], device: torch.device) -> torch.Tensor:
    """Stack a list of (50,50,3) HWC frames into (B,3,50,50) CHW."""
    arr = np.stack([np.asarray(o, dtype=np.float32) for o in obs_list], axis=0)  # (B,50,50,3)
    x = torch.from_numpy(arr).to(device).permute(0, 3, 1, 2).contiguous()
    return x


def _actor_logits(model: RViTPlusModel, states, c3_spec) -> torch.Tensor:
    if model.split_c3:
        C1, C2, _ = states
        states_for_actor = (C1, C2, c3_spec["actor"])
    else:
        states_for_actor = states
    return model.actor_head(states_for_actor)


@torch.no_grad()
def batched_behavior_rollout(
    model: RViTPlusModel,
    envs: List[ChangeDetectionEnv],
    obs0: List[np.ndarray],
    device: torch.device,
) -> Dict[str, np.ndarray]:
    """Run B trials in parallel under the model's argmax policy.

    `envs[i]` must already be reset+spec'd, with `obs0[i]` its t=0 frame.
    Returns per-trial arrays (length B):
        pressed       bool   — model ever took action=1
        press_index   int    — loop index of the first press (-1 if none)
        change_time   int    — Tc for the trial
        change_true   int
        hit           bool   — pressed at t ≥ Tc on a change_true==1 trial
        premature     bool   — pressed at t <  Tc (false alarm)
        rt            float   — press_index − Tc on hits, else nan
        reward        float
    """
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    c3_spec = model.encoder.init_c3_specialists(B, device=device)

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
        V = model.stem(x)
        enc_out = model.encoder.forward_step(
            V, states, prev_c3_specialists=c3_spec if model.split_c3 else None
        )
        states = enc_out["layer_states_new"]
        c3_spec = enc_out["c3_specialists_new"]
        logits = _actor_logits(model, states, c3_spec)
        actions = logits.argmax(dim=-1).cpu().numpy().astype(np.int64)

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
        "pressed": pressed,
        "press_index": press_index,
        "change_time": change_time,
        "change_true": change_true,
        "hit": hit,
        "premature": premature,
        "rt": rt,
        "reward": reward,
    }


@torch.no_grad()
def batched_attention_rollout(
    model: RViTPlusModel,
    envs: List[ChangeDetectionEnv],
    obs0: List[np.ndarray],
    device: torch.device,
    n_layers: int = 3,
) -> Tuple[List[np.ndarray], np.ndarray]:
    """Run B trials with action forced to 0 (wait) for the full episode.

    At each timestep, for each encoder layer, sum the per-channel spatial
    softmax maps A (B,C,H,W) over channels → (B,H,W), then average over the
    batch → (H,W). Accumulate across timesteps.

    Returns
    -------
    mean_attn : list of length n_layers; mean_attn[L] has shape (T, H_L, W_L)
    obs_example : (T, 50, 50, 3) — the first trial's frames, for reference
    """
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    c3_spec = model.encoder.init_c3_specialists(B, device=device)

    obs = list(obs0)
    T = envs[0].T

    per_layer_frames: List[List[np.ndarray]] = [[] for _ in range(n_layers)]
    obs_example: List[np.ndarray] = []

    t = 0
    done = np.zeros(B, dtype=bool)
    while t <= T and not done.all():
        x = _obs_to_tensor(obs, device)
        obs_example.append(np.asarray(obs[0], dtype=np.float32).copy())
        V = model.stem(x)
        enc_out = model.encoder.forward_step(
            V, states, prev_c3_specialists=c3_spec if model.split_c3 else None
        )
        states = enc_out["layer_states_new"]
        c3_spec = enc_out["c3_specialists_new"]

        attn = enc_out["attn_per_iter"][-1]  # list of (B,C,H,W), last FR iter
        for L in range(n_layers):
            A = attn[L]                       # (B, C, H, W)
            summed = A.sum(dim=1)             # (B, H, W) — sum over channels/heads
            mean_map = summed.mean(dim=0)     # (H, W) — average over trials
            per_layer_frames[L].append(mean_map.detach().cpu().numpy())

        # Force wait. Step all non-done envs with action=0.
        for i in range(B):
            if done[i]:
                continue
            o, r, d, _ = envs[i].step(0)
            obs[i] = o
            if d:
                done[i] = True
        t += 1

    mean_attn = [np.stack(frames, axis=0) for frames in per_layer_frames]  # (T,H,W) each
    return mean_attn, np.stack(obs_example, axis=0)


# ─────────────────────────────────────────────────────────────────────────────
# Batch builder
# ─────────────────────────────────────────────────────────────────────────────


def build_env_batch(
    base_spec: ForcedTrialSpec,
    n_trials: int,
    rng: np.random.Generator,
    *,
    env_kwargs: Optional[dict] = None,
    randomize_cue_position: bool = False,
    randomize_color: bool = False,
) -> Tuple[List[ChangeDetectionEnv], List[np.ndarray]]:
    """Create `n_trials` reset+spec'd envs sharing `base_spec`.

    randomize_cue_position / randomize_color marginalize those fields per trial
    (overriding whatever base_spec set). Useful when the condition of interest
    is e.g. valid-vs-invalid but we want to average over which side was cued.
    """
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
