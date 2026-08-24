"""
Shared harness for RViT+ v5 behavioral / attention analyses (the "first-look" SOP).

Ported from RViT_plus_v4/analysis/_behav_utils.py. The env (ChangeDetectionEnv)
and the forced-trial mechanism are IDENTICAL; the v5-specific pieces are:
  * build_model     → constructs RViTPlusV9Model from the v5 config
  * attention       → v5's encoder is memory-as-tokens: each layer attends over
                      [patch ++ H₁ ++ H₂] = 3·N tokens. We pull the per-layer
                      attention via encoder.forward_step(..., return_attn=True),
                      take the columns over the N image-PATCH keys (the spatial
                      ones), reduce to a per-patch saliency (mean over heads and
                      all queries), and reshape to the (grid_h, grid_w) patch grid
                      (10×10 for 50×50/patch-5 — the H/2×W/2 quadrant split lands
                      exactly on the 4 Gabor quadrants).

Env timing semantics (unchanged): t=0 blank · t=1 cue · t=2 blank · t=3 gabors ·
t≥Tc changed gabor. press at t<Tc → premature; press at t≥Tc on a change trial →
HIT. RT = press_index − change_time, defined on hits.
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

from RViT_plus_jump_softmax.env import ChangeDetectionEnv
from RViT_plus_jump_softmax.model import RViTPlusJumpModel

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
        path = os.path.join(_PROJECT_ROOT, "RViT_plus_jump_softmax", "config", "rvit_plus_config.json")
    with open(path) as f:
        return json.load(f)


def build_model(cfg: dict, device: torch.device) -> RViTPlusJumpModel:
    """Construct the v11 dual-stream model exactly as train_rl.py does, from config."""
    m = cfg["model"]
    rl = m["rl"]
    model = RViTPlusJumpModel(
        in_channels=3, image_h=50, image_w=50,
        patch_size=int(m["patch_size"]),
        patch_hidden=int(m.get("patch_hidden", m["d_model"])),
        d_model=int(m["d_model"]),
        d_mem=int(m["d_mem"]),
        tx_heads=int(m.get("tx_heads", 8)),
        tx_layers=int(m.get("tx_layers", 1)),
        n_lstm=int(m.get("n_lstm", 2)),
        conv_channels=int(m.get("conv_channels", 64)),
        n_conv_layers=int(m.get("n_conv_layers", 3)),
        conv_kernel=int(m.get("conv_kernel", 5)),
        n_actions=int(rl["n_actions"]),
        n_quantiles=int(rl["n_quantiles"]),
        init_action_bias=list(rl["init_action_bias"]),
        seq_len=int(cfg["ppo"]["seq_len"]),
    ).to(device)
    return model


def load_checkpoint(model: RViTPlusJumpModel, ckpt_path: str, device: torch.device) -> int:
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    missing, unexpected = model.load_state_dict(sd, strict=False)
    if missing:
        print(f"[load] WARNING missing keys ({len(missing)}): {missing[:6]}{'...' if len(missing) > 6 else ''}")
    if unexpected:
        print(f"[load] WARNING unexpected keys ({len(unexpected)}): {unexpected[:6]}{'...' if len(unexpected) > 6 else ''}")
    model.eval()
    return int(ckpt.get("iter", -1))


# ── forced trial specs (identical to v3/v4) ─────────────────────────────────


@dataclass
class ForcedTrialSpec:
    """A per-trial condition. Fields left None are randomized by reset()."""
    cue_position: Optional[str] = None
    cue_color: Optional[str] = None
    proportion: Optional[float] = None
    change_true: Optional[int] = None
    change_time: Optional[int] = None
    change_index_mode: object = None
    orientation_mag: Optional[float] = None


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


# ── batched rollouts ────────────────────────────────────────────────────────


def _obs_to_tensor(obs_list: Sequence[np.ndarray], device: torch.device) -> torch.Tensor:
    arr = np.stack([np.asarray(o, dtype=np.float32) for o in obs_list], axis=0)  # (B,50,50,3)
    return torch.from_numpy(arr).to(device).permute(0, 3, 1, 2).contiguous()


@torch.no_grad()
def batched_behavior_rollout(
    model: RViTPlusJumpModel,
    envs: List[ChangeDetectionEnv],
    obs0: List[np.ndarray],
    device: torch.device,
) -> Dict[str, np.ndarray]:
    """Run B trials in parallel under the model's argmax policy (via rl_step)."""
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


STREAM_NAMES = ["salience", "topdown"]   # attn[0] = salience (KV=H1), attn[1] = top-down (KV=H2)


@torch.no_grad()
def batched_attention_rollout(
    model: RViTPlusJumpModel,
    envs: List[ChangeDetectionEnv],
    obs0: List[np.ndarray],
    device: torch.device,
    n_layers: int = 2,
) -> Tuple[List[np.ndarray], np.ndarray]:
    """Run B trials forced to wait and pull v11's TWO dual-stream attentions.

    v11 has no patch keys: each stream is the image queries X attending OVER a
    memory bank — salience over H1, top-down over H2 — so each attention is
    (B, heads, N_query, N_key) with N_key memory rows (memory row i ↔ patch
    position i). The spatially-meaningful per-head saliency is the attention each
    MEMORY KEY *receives*, i.e. mean over the N image queries → (B, heads, N_key),
    reshaped to the (grid_h, grid_w) grid and averaged over trials. Heads are kept
    separate (they specialize). The two "layers" returned are the two STREAMS:
    index 0 = salience (reading H1), index 1 = top-down (reading H2).

    Returns (mean_attn[s] : (T, n_heads, gh, gw), obs_example : (T,50,50,3)) for
    s in {salience, top-down}.
    """
    B = len(envs)
    model.eval()
    states = model.init_states(B, device=device)
    gh, gw, N = model.patch_embed.grid_h, model.patch_embed.grid_w, model.n_tokens
    n_streams = 2
    obs = list(obs0)
    T = envs[0].T
    per_stream_frames: List[List[np.ndarray]] = [[] for _ in range(n_streams)]
    obs_example: List[np.ndarray] = []
    t = 0
    done = np.zeros(B, dtype=bool)
    while t <= T and not done.all():
        x = _obs_to_tensor(obs, device)
        obs_example.append(np.asarray(obs[0], dtype=np.float32).copy())
        tokens = model.patch_embed(x)
        states, _rec, attn = model.encoder.forward_step(tokens, states, return_attn=True)
        for s in range(n_streams):
            aw = attn[s]                                  # (B, heads, N_query, N_key)
            sal = aw.mean(dim=2)                          # mean over image QUERIES → (B, heads, N_key)
            grid = sal.view(B, sal.shape[1], gh, gw)      # (B, heads, grid_h, grid_w) row-major
            per_stream_frames[s].append(grid.mean(dim=0).detach().cpu().numpy())  # (heads, gh, gw)
        for i in range(B):
            if done[i]:
                continue
            o, r, d, _ = envs[i].step(0)                  # force wait
            obs[i] = o
            if d:
                done[i] = True
        t += 1
    mean_attn = [np.stack(frames, axis=0) for frames in per_stream_frames]
    return mean_attn, np.stack(obs_example, axis=0)
