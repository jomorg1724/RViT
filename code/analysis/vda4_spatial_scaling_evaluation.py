"""Evaluate VDA4 behavior and attention across sensory-token discretizations.

The VDA4 task always has four physical stimulus quadrants.  A model may represent
that unchanged 50x50 image with 2x2, 4x4, or 10x10 patch/memory tokens.  This
producer therefore maps each task quadrant to its *full* model-token region before
aggregating attention or applying causal key-logit interventions.

One invocation evaluates one terminal checkpoint and writes an immutable,
hash-bound artifact directory containing psychometrics/RT/SDT, event attention
maps, and regional causal interventions.  Common seeds make outputs pairable
across routing families and token counts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
import time
import types
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VALIDITIES = np.asarray([0.25, 0.50, 0.75, 1.00], dtype=np.float64)
MAGNITUDES = np.asarray([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0], dtype=np.float64)
CONDITIONS = ("valid", "invalid")
INTERVENTION_CONDITIONS = ("valid", "invalid", "nochange")
REGION_ROLES = ("change", "cued", "control")
DOSES = np.asarray([0.0, 0.25, 0.50, 0.75, 1.0], dtype=np.float64)
QUALIFYING_FRAMES = (5, 6)
CUE_INDEX = 0
VALID_CHANGE_INDEX = 0
INVALID_CHANGE_INDEX = 3
CONTROL_INDEX = 1
FOCAL_MAGNITUDE = 30.0
FOCAL_VALIDITY = 1.0
CLAMP_FROM = 5
CLAMP_LOGIT_SCALE = 6.0
PSYCHOMETRIC_SEED = 202707260
ATTENTION_SEED = 202707360
INTERVENTION_SEED = 202707460
SHUFFLE_SEED = 202707560


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def task_region_tokens(grid_rows: int, grid_cols: int, task_location: int) -> tuple[int, ...]:
    """Map one VDA4 2x2 task location to every model token in that quadrant."""
    if grid_rows <= 0 or grid_cols <= 0 or grid_rows % 2 or grid_cols % 2:
        raise ValueError(f"VDA4 region mapping requires positive even grid dimensions; got {grid_rows}x{grid_cols}")
    if task_location not in range(4):
        raise ValueError(f"task_location must be in 0..3; got {task_location}")
    task_row, task_col = divmod(task_location, 2)
    row_start, row_stop = task_row * (grid_rows // 2), (task_row + 1) * (grid_rows // 2)
    col_start, col_stop = task_col * (grid_cols // 2), (task_col + 1) * (grid_cols // 2)
    return tuple(r * grid_cols + c for r in range(row_start, row_stop) for c in range(col_start, col_stop))


def all_task_regions(grid_rows: int, grid_cols: int) -> tuple[tuple[int, ...], ...]:
    regions = tuple(task_region_tokens(grid_rows, grid_cols, location) for location in range(4))
    flat = sorted(token for region in regions for token in region)
    if flat != list(range(grid_rows * grid_cols)):
        raise RuntimeError("task-region mapping is not an exact partition of model tokens")
    return regions


def regional_clamp(feedback: str, n_tokens: int, tokens: tuple[int, ...], alpha: float) -> dict[str, float]:
    """Bias all self keys, or all paired image+memory keys, in one task region."""
    if not 0.0 <= float(alpha) <= 1.0:
        raise ValueError("alpha must be in [0, 1]")
    bias = CLAMP_LOGIT_SCALE * (2.0 * float(alpha) - 1.0)
    keys = list(tokens)
    if feedback == "crossattn1":
        keys += [n_tokens + token for token in tokens]
    elif feedback != "affine_ew":
        raise ValueError(f"unsupported feedback {feedback!r}")
    return {str(key): bias for key in keys}


def spatial_shuffle_permutation(feedback: str, n_tokens: int) -> list[int]:
    """Fixed spatial permutation, preserving image/memory source blocks for cross-attention."""
    rng = np.random.default_rng(SHUFFLE_SEED)
    spatial = rng.permutation(n_tokens).astype(int).tolist()
    if feedback == "crossattn1":
        return spatial + [n_tokens + token for token in spatial]
    return spatial


def install_explicit_attention_interventions(model: Any, feedback: str) -> None:
    """Patch one evaluation model instance with uniform/shuffle/disable modes.

    Training/model source files remain untouched.  Natural and regional additive
    clamps continue through the checkpoint's original attention implementation.
    """
    import torch

    module = model.encoder.attn
    original = module.forward

    if feedback == "crossattn1":
        def patched(this: Any, X: Any, H_prev: Any, return_attn: bool = False, attn_clamp: Any = None):
            mode = attn_clamp.get("__mode__") if isinstance(attn_clamp, dict) else None
            if mode is None:
                return original(X, H_prev, return_attn=return_attn, attn_clamp=attn_clamp)
            Q = this.W_q(X)
            K = torch.cat([this.W_kx(X), this.W_kh(H_prev)], dim=1)
            V = torch.cat([this.W_vx(X), this.W_vh(H_prev)], dim=1)
            scores = torch.matmul(Q, K.transpose(-1, -2)) * this.scale
            natural = torch.softmax(scores, dim=-1)
            if mode == "uniform":
                attention = torch.full_like(natural, 1.0 / natural.shape[-1])
            elif mode == "shuffle":
                permutation = torch.as_tensor(attn_clamp["__permutation__"], device=X.device, dtype=torch.long)
                if permutation.numel() != natural.shape[-1]:
                    raise ValueError("shuffle permutation length does not match cross-attention keys")
                attention = natural.index_select(-1, permutation)
            elif mode == "disable":
                attention = torch.zeros_like(natural)
            else:
                raise ValueError(f"unknown explicit attention mode {mode!r}")
            Z = X + torch.matmul(attention, V)
            return (Z, attention) if return_attn else (Z, None)
    elif feedback == "affine_ew":
        def patched(this: Any, X: Any, H_prev: Any, return_attn: bool = False, attn_clamp: Any = None):
            mode = attn_clamp.get("__mode__") if isinstance(attn_clamp, dict) else None
            if mode is None:
                return original(X, H_prev, return_attn=return_attn, attn_clamp=attn_clamp)
            bottleneck = torch.tanh(this.bottleneck(H_prev))
            Xp = this.gen_scale(bottleneck) * X + this.gen_shift(bottleneck)
            Q, K, V = this.W_XQ(Xp), this.W_XK(Xp), this.W_XV(Xp)
            scores = torch.matmul(Q, K.transpose(-1, -2)) * this.attn_scale
            natural = torch.softmax(scores, dim=-1)
            if mode == "uniform":
                attention = torch.full_like(natural, 1.0 / natural.shape[-1])
            elif mode == "shuffle":
                permutation = torch.as_tensor(attn_clamp["__permutation__"], device=X.device, dtype=torch.long)
                if permutation.numel() != natural.shape[-1]:
                    raise ValueError("shuffle permutation length does not match affine attention keys")
                attention = natural.index_select(-1, permutation)
            elif mode == "disable":
                attention = torch.zeros_like(natural)
            else:
                raise ValueError(f"unknown explicit attention mode {mode!r}")
            Z = X + torch.matmul(attention, V)
            return (Z, attention) if return_attn else (Z, None)
    else:
        raise ValueError(f"unsupported feedback {feedback!r}")

    module.forward = types.MethodType(patched, module)


def first_press_from_logits(logits: np.ndarray) -> np.ndarray:
    actions = np.asarray(logits).argmax(axis=-1)
    press = np.full(actions.shape[0], -1, dtype=np.int64)
    for frame in range(actions.shape[1]):
        new = (actions[:, frame] == 1) & (press < 0)
        press[new] = frame
    return press


def press_histogram(press: np.ndarray) -> np.ndarray:
    values = np.asarray(press, dtype=np.int64)
    return np.asarray([(values == value).sum() for value in (-1, 0, 1, 2, 3, 4, 5, 6)], dtype=np.int64)


def qualifying_stats(press: np.ndarray, *, nochange: bool = False) -> tuple[int, float, np.ndarray]:
    detected = np.asarray(press) >= 0 if nochange else np.isin(press, QUALIFYING_FRAMES)
    count = int(detected.sum())
    mean_rt = float(np.asarray(press)[detected].mean()) if count else float("nan")
    return count, mean_rt, press_histogram(press)


def hautus_sdt(hit_count: int, false_alarm_count: int, n_hit: int, n_fa: int) -> tuple[float, float]:
    from scipy.stats import norm

    hit_rate = (float(hit_count) + 0.5) / (float(n_hit) + 1.0)
    false_alarm_rate = (float(false_alarm_count) + 0.5) / (float(n_fa) + 1.0)
    z_hit, z_fa = float(norm.ppf(hit_rate)), float(norm.ppf(false_alarm_rate))
    return z_hit - z_fa, -0.5 * (z_hit + z_fa)


def rollout_attention(model: Any, videos: Any, core: Any, clamp: dict[str, Any] | None = None) -> tuple[np.ndarray, np.ndarray]:
    import torch

    batch = int(videos.shape[0])
    state = model.init_states(batch, device=core.DEVICE)
    logits, attention = [], []
    for frame in range(core.T):
        active = clamp if (clamp and frame >= CLAMP_FROM) else None
        with torch.no_grad():
            step = model.rl_step(videos[:, frame], state, return_attn=True, attn_clamp=active)
        state = step["new_states"]
        logits.append(step["actor_logits"].detach().cpu().numpy())
        step_attention = step["attn"]
        if step_attention is None:
            raise RuntimeError("model returned no attention under return_attn=True")
        # rl_step wraps the single encoder attention tensor in a one-element
        # list for compatibility with multi-stage attention families.
        while isinstance(step_attention, (list, tuple)) and len(step_attention) == 1:
            step_attention = step_attention[0]
        if isinstance(step_attention, (list, tuple)):
            raise RuntimeError("spatial-scaling evaluation expects one attention tensor")
        attention.append(step_attention.detach().cpu().numpy().astype(np.float32))
    logits_array = np.stack(logits, axis=1)
    return first_press_from_logits(logits_array), np.stack(attention, axis=1)


def location_mass(raw_attention: np.ndarray, n_tokens: int) -> np.ndarray:
    """Trial x time x model-token key mass, averaged over query tokens."""
    raw = np.asarray(raw_attention, dtype=np.float64)
    if raw.ndim != 4 or raw.shape[-2] != n_tokens:
        raise ValueError(f"unexpected attention shape {raw.shape} for {n_tokens} tokens")
    if raw.shape[-1] == 2 * n_tokens:
        combined = raw[..., :n_tokens] + raw[..., n_tokens:]
    elif raw.shape[-1] == n_tokens:
        combined = raw
    else:
        raise ValueError(f"attention key count {raw.shape[-1]} is neither N nor 2N")
    mass = combined.mean(axis=-2)
    if not np.all(np.isfinite(mass)) or not np.allclose(mass.sum(axis=-1), 1.0, atol=2e-5):
        raise RuntimeError("attention mass is not finite and normalized")
    return mass.astype(np.float32)


def region_mass(token_mass: np.ndarray, regions: tuple[tuple[int, ...], ...]) -> np.ndarray:
    return np.stack([token_mass[..., list(tokens)].sum(axis=-1) for tokens in regions], axis=-1).astype(np.float32)


def compute_psychometrics(model: Any, core: Any, trials: int) -> dict[str, np.ndarray]:
    shape = (len(VALIDITIES), len(MAGNITUDES), len(CONDITIONS))
    counts = np.zeros(shape, dtype=np.int64)
    rates = np.zeros(shape, dtype=np.float64)
    mean_rt = np.full(shape, np.nan, dtype=np.float64)
    histograms = np.zeros(shape + (8,), dtype=np.int64)
    false_alarm_count = np.zeros(len(VALIDITIES), dtype=np.int64)
    false_alarm_rate = np.zeros(len(VALIDITIES), dtype=np.float64)
    false_alarm_histogram = np.zeros((len(VALIDITIES), 8), dtype=np.int64)

    for validity_index, validity in enumerate(VALIDITIES):
        nochange_seed = PSYCHOMETRIC_SEED + validity_index * 1000 + 900
        nochange = core.press_times_clamp(
            model, "vda4", CUE_INDEX, float(validity), "red", 0, CUE_INDEX, 0.0,
            B=trials, seed=nochange_seed,
        )
        fa_count, _, fa_hist = qualifying_stats(nochange, nochange=True)
        false_alarm_count[validity_index] = fa_count
        false_alarm_rate[validity_index] = fa_count / float(trials)
        false_alarm_histogram[validity_index] = fa_hist
        for magnitude_index, magnitude in enumerate(MAGNITUDES):
            for condition_index, change_index in enumerate((VALID_CHANGE_INDEX, INVALID_CHANGE_INDEX)):
                seed = PSYCHOMETRIC_SEED + validity_index * 1000 + magnitude_index * 10 + condition_index
                press = core.press_times_clamp(
                    model, "vda4", CUE_INDEX, float(validity), "red", 1, change_index,
                    float(magnitude), B=trials, seed=seed,
                )
                count, rt, histogram = qualifying_stats(press)
                counts[validity_index, magnitude_index, condition_index] = count
                rates[validity_index, magnitude_index, condition_index] = count / float(trials)
                mean_rt[validity_index, magnitude_index, condition_index] = rt
                histograms[validity_index, magnitude_index, condition_index] = histogram
        print(f"[psychometric] validity={validity:.2f} complete", flush=True)

    dprime = np.zeros(shape, dtype=np.float64)
    criterion = np.zeros(shape, dtype=np.float64)
    for validity_index in range(len(VALIDITIES)):
        for magnitude_index in range(len(MAGNITUDES)):
            for condition_index in range(len(CONDITIONS)):
                dprime[validity_index, magnitude_index, condition_index], criterion[
                    validity_index, magnitude_index, condition_index
                ] = hautus_sdt(
                    int(counts[validity_index, magnitude_index, condition_index]),
                    int(false_alarm_count[validity_index]), trials, trials,
                )
    return {
        "response_count": counts,
        "response_rate": rates,
        "mean_rt": mean_rt,
        "press_histogram": histograms,
        "false_alarm_count": false_alarm_count,
        "false_alarm_rate": false_alarm_rate,
        "false_alarm_histogram": false_alarm_histogram,
        "dprime": dprime,
        "criterion": criterion,
    }


def compute_event_attention(model: Any, core: Any, trials: int, n_tokens: int,
                            regions: tuple[tuple[int, ...], ...]) -> dict[str, np.ndarray]:
    presses, token_masses, region_masses, raw_means = [], [], [], []
    for condition_index, change_index in enumerate((VALID_CHANGE_INDEX, INVALID_CHANGE_INDEX)):
        videos = core.make_video_batch(
            "vda4", CUE_INDEX, FOCAL_VALIDITY, "red", 1, change_index, FOCAL_MAGNITUDE,
            B=trials, seed=ATTENTION_SEED + condition_index,
        )
        press, raw = rollout_attention(model, videos, core)
        mass = location_mass(raw, n_tokens)
        presses.append(press)
        token_masses.append(mass)
        region_masses.append(region_mass(mass, regions))
        raw_means.append(raw.mean(axis=0))
        print(f"[attention] {CONDITIONS[condition_index]} complete", flush=True)
    return {
        "press": np.stack(presses, axis=0),
        "token_mass": np.stack(token_masses, axis=0),
        "region_mass": np.stack(region_masses, axis=0),
        "raw_attention_mean": np.stack(raw_means, axis=0),
    }


def compute_interventions(model: Any, core: Any, trials: int, feedback: str, n_tokens: int,
                          regions: tuple[tuple[int, ...], ...]) -> dict[str, np.ndarray]:
    role_location = {"change": INVALID_CHANGE_INDEX, "cued": CUE_INDEX, "control": CONTROL_INDEX}
    response_count = np.zeros((len(REGION_ROLES), len(DOSES), 3), dtype=np.int64)
    response_rate = np.zeros_like(response_count, dtype=np.float64)
    mean_rt = np.full_like(response_rate, np.nan, dtype=np.float64)
    histograms = np.zeros(response_count.shape + (8,), dtype=np.int64)
    achieved_change = np.zeros((len(REGION_ROLES), len(DOSES), core.T), dtype=np.float64)
    achieved_target = np.zeros_like(achieved_change)

    valid_videos = core.make_video_batch(
        "vda4", CUE_INDEX, FOCAL_VALIDITY, "red", 1, VALID_CHANGE_INDEX, FOCAL_MAGNITUDE,
        B=trials, seed=INTERVENTION_SEED,
    )
    invalid_videos = core.make_video_batch(
        "vda4", CUE_INDEX, FOCAL_VALIDITY, "red", 1, INVALID_CHANGE_INDEX, FOCAL_MAGNITUDE,
        B=trials, seed=INTERVENTION_SEED + 1,
    )
    nochange_videos = core.make_video_batch(
        "vda4", CUE_INDEX, FOCAL_VALIDITY, "red", 0, CUE_INDEX, 0.0,
        B=trials, seed=INTERVENTION_SEED + 2,
    )
    videos_by_condition = (valid_videos, invalid_videos, nochange_videos)

    for role_index, role in enumerate(REGION_ROLES):
        target_location = role_location[role]
        for dose_index, dose in enumerate(DOSES):
            clamp = regional_clamp(feedback, n_tokens, regions[target_location], float(dose))
            for condition_index, videos in enumerate(videos_by_condition):
                press = core.press_times_clamp(
                    model, "vda4", CUE_INDEX, FOCAL_VALIDITY, "red",
                    0 if condition_index == 2 else 1,
                    (VALID_CHANGE_INDEX, INVALID_CHANGE_INDEX, CUE_INDEX)[condition_index],
                    0.0 if condition_index == 2 else FOCAL_MAGNITUDE,
                    clamp=clamp, clamp_from=CLAMP_FROM, videos=videos,
                )
                count, rt, histogram = qualifying_stats(press, nochange=condition_index == 2)
                response_count[role_index, dose_index, condition_index] = count
                response_rate[role_index, dose_index, condition_index] = count / float(trials)
                mean_rt[role_index, dose_index, condition_index] = rt
                histograms[role_index, dose_index, condition_index] = histogram
            _, raw = rollout_attention(model, invalid_videos, core, clamp=clamp)
            regional = region_mass(location_mass(raw, n_tokens), regions)
            achieved_change[role_index, dose_index] = regional[..., INVALID_CHANGE_INDEX].mean(axis=0)
            achieved_target[role_index, dose_index] = regional[..., target_location].mean(axis=0)
        print(f"[intervention] regional role={role} complete", flush=True)

    dprime = np.zeros((len(REGION_ROLES), len(DOSES), 2), dtype=np.float64)
    criterion = np.zeros_like(dprime)
    for role_index in range(len(REGION_ROLES)):
        for dose_index in range(len(DOSES)):
            false_alarm = int(response_count[role_index, dose_index, 2])
            for condition_index in range(2):
                dprime[role_index, dose_index, condition_index], criterion[
                    role_index, dose_index, condition_index
                ] = hautus_sdt(
                    int(response_count[role_index, dose_index, condition_index]),
                    false_alarm, trials, trials,
                )

    explicit_modes = ("natural", "uniform", "shuffle", "disable")
    explicit_count = np.zeros((len(explicit_modes), 3), dtype=np.int64)
    explicit_rate = np.zeros_like(explicit_count, dtype=np.float64)
    explicit_rt = np.full_like(explicit_rate, np.nan, dtype=np.float64)
    explicit_hist = np.zeros(explicit_count.shape + (8,), dtype=np.int64)
    permutation = spatial_shuffle_permutation(feedback, n_tokens)
    for mode_index, mode in enumerate(explicit_modes):
        if mode == "natural":
            clamp: dict[str, Any] | None = None
        elif mode == "shuffle":
            clamp = {"__mode__": "shuffle", "__permutation__": permutation}
        else:
            clamp = {"__mode__": mode}
        for condition_index, videos in enumerate(videos_by_condition):
            press, _ = rollout_attention(model, videos, core, clamp=clamp)
            count, rt, histogram = qualifying_stats(press, nochange=condition_index == 2)
            explicit_count[mode_index, condition_index] = count
            explicit_rate[mode_index, condition_index] = count / float(trials)
            explicit_rt[mode_index, condition_index] = rt
            explicit_hist[mode_index, condition_index] = histogram
        print(f"[intervention] explicit mode={mode} complete", flush=True)

    explicit_dprime = np.zeros((len(explicit_modes), 2), dtype=np.float64)
    explicit_criterion = np.zeros_like(explicit_dprime)
    for mode_index in range(len(explicit_modes)):
        for condition_index in range(2):
            explicit_dprime[mode_index, condition_index], explicit_criterion[mode_index, condition_index] = hautus_sdt(
                int(explicit_count[mode_index, condition_index]), int(explicit_count[mode_index, 2]), trials, trials,
            )

    return {
        "response_count": response_count,
        "response_rate": response_rate,
        "mean_rt": mean_rt,
        "press_histogram": histograms,
        "dprime": dprime,
        "criterion": criterion,
        "achieved_change_region_mass": achieved_change,
        "achieved_target_region_mass": achieved_target,
        "explicit_modes": np.asarray(explicit_modes),
        "explicit_response_count": explicit_count,
        "explicit_response_rate": explicit_rate,
        "explicit_mean_rt": explicit_rt,
        "explicit_press_histogram": explicit_hist,
        "explicit_dprime": explicit_dprime,
        "explicit_criterion": explicit_criterion,
        "shuffle_permutation": np.asarray(permutation, dtype=np.int64),
    }


def save_npz(path: Path, payload: dict[str, Any], metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **payload, **{f"meta_{key}": np.asarray(value) for key, value in metadata.items()})


def write_baseline_table(path: Path, psych: dict[str, np.ndarray], label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "model", "displayed_validity", "magnitude", "condition", "response_count",
            "response_rate", "mean_rt", "false_alarm_rate", "dprime", "criterion",
        ])
        writer.writeheader()
        for vi, validity in enumerate(VALIDITIES):
            for mi, magnitude in enumerate(MAGNITUDES):
                for ci, condition in enumerate(CONDITIONS):
                    writer.writerow({
                        "model": label, "displayed_validity": validity, "magnitude": magnitude,
                        "condition": condition, "response_count": int(psych["response_count"][vi, mi, ci]),
                        "response_rate": psych["response_rate"][vi, mi, ci],
                        "mean_rt": psych["mean_rt"][vi, mi, ci],
                        "false_alarm_rate": psych["false_alarm_rate"][vi],
                        "dprime": psych["dprime"][vi, mi, ci], "criterion": psych["criterion"][vi, mi, ci],
                    })


def write_intervention_table(path: Path, payload: dict[str, np.ndarray], label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "model", "role", "dose", "condition", "response_rate", "mean_rt", "dprime", "criterion",
            "achieved_change_mass_t5", "achieved_change_mass_t6",
        ])
        writer.writeheader()
        for ri, role in enumerate(REGION_ROLES):
            for di, dose in enumerate(DOSES):
                for ci, condition in enumerate(INTERVENTION_CONDITIONS):
                    writer.writerow({
                        "model": label, "role": role, "dose": dose, "condition": condition,
                        "response_rate": payload["response_rate"][ri, di, ci],
                        "mean_rt": payload["mean_rt"][ri, di, ci],
                        "dprime": payload["dprime"][ri, di, ci] if ci < 2 else "",
                        "criterion": payload["criterion"][ri, di, ci] if ci < 2 else "",
                        "achieved_change_mass_t5": payload["achieved_change_region_mass"][ri, di, 5],
                        "achieved_change_mass_t6": payload["achieved_change_region_mass"][ri, di, 6],
                    })


def configure_plots() -> Any:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
    return plt


def save_figure(figure: Any, base: Path) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(base.with_suffix(".png"), dpi=240, bbox_inches="tight")
    figure.savefig(base.with_suffix(".pdf"), bbox_inches="tight")


def plot_psychometrics(plt: Any, psych: dict[str, np.ndarray], output: Path, label: str) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11.2, 4.2), constrained_layout=True)
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(VALIDITIES)))
    for vi, validity in enumerate(VALIDITIES):
        for ci, condition in enumerate(CONDITIONS):
            style = "-" if condition == "valid" else "--"
            marker = "o" if condition == "valid" else "s"
            name = f"{int(validity * 100)}% {condition}"
            axes[0].plot(MAGNITUDES, psych["response_rate"][vi, :, ci], style, marker=marker,
                         ms=3, color=colors[vi], label=name)
            axes[1].plot(MAGNITUDES, psych["mean_rt"][vi, :, ci], style, marker=marker,
                         ms=3, color=colors[vi], label=name)
    axes[0].set(title="Response probability", xlabel="orientation change (degrees)", ylabel="P(response at frame 5 or 6)", ylim=(-0.03, 1.03))
    axes[1].set(title="Conditional response time", xlabel="orientation change (degrees)", ylabel="mean response frame", ylim=(4.8, 6.2))
    for axis in axes:
        axis.grid(alpha=0.2)
    axes[0].legend(ncol=2, fontsize=6.5, frameon=False)
    figure.suptitle(f"{label}: VDA4 valid/invalid psychometrics and response timing", fontweight="bold")
    save_figure(figure, output)
    plt.close(figure)


def plot_attention(plt: Any, attention: dict[str, np.ndarray], output: Path, label: str,
                   grid_rows: int, grid_cols: int) -> None:
    maps = attention["token_mass"].mean(axis=1).reshape(2, -1, grid_rows, grid_cols)
    frames = (4, 5, 6)
    vmax = float(maps[:, list(frames)].max())
    figure, axes = plt.subplots(2, 3, figsize=(8.8, 5.4), constrained_layout=True)
    image = None
    for ci, condition in enumerate(CONDITIONS):
        for column, frame in enumerate(frames):
            image = axes[ci, column].imshow(maps[ci, frame], cmap="magma", vmin=0.0, vmax=vmax)
            axes[ci, column].set_title(f"{condition}, frame {frame}")
            axes[ci, column].set_xticks([]); axes[ci, column].set_yticks([])
            axes[ci, column].axvline(grid_cols / 2 - 0.5, color="white", lw=0.7, alpha=0.7)
            axes[ci, column].axhline(grid_rows / 2 - 0.5, color="white", lw=0.7, alpha=0.7)
    if image is not None:
        figure.colorbar(image, ax=axes.ravel().tolist(), fraction=0.025, label="query-averaged spatial key mass")
    figure.suptitle(f"{label}: event attention over {grid_rows}x{grid_cols} tokens (cue TL; invalid change BR)", fontweight="bold")
    save_figure(figure, output)
    plt.close(figure)


def plot_interventions(plt: Any, payload: dict[str, np.ndarray], output: Path, label: str) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(10.4, 7.0), constrained_layout=True)
    colors = {"change": "#0072B2", "cued": "#D55E00", "control": "#777777"}
    for ri, role in enumerate(REGION_ROLES):
        axes[0, 0].plot(DOSES, payload["response_rate"][ri, :, 1], marker="o", label=role, color=colors[role])
        axes[0, 1].plot(DOSES, payload["dprime"][ri, :, 1], marker="o", label=role, color=colors[role])
        axes[1, 0].plot(DOSES, payload["mean_rt"][ri, :, 1], marker="o", label=role, color=colors[role])
        achieved = payload["achieved_change_region_mass"][ri, :, 5:7].mean(axis=-1)
        axes[1, 1].plot(DOSES, achieved, marker="o", label=role, color=colors[role])
    axes[0, 0].set(title="Invalid-trial response", ylabel="P(response at frame 5 or 6)", ylim=(-0.03, 1.03))
    axes[0, 1].set(title="Invalid-trial sensitivity", ylabel="d-prime")
    axes[1, 0].set(title="Invalid conditional timing", ylabel="mean response frame")
    axes[1, 1].set(title="Achieved attention at true change region", ylabel="regional mass at frames 5-6")
    for axis in axes.ravel():
        axis.set_xlabel("regional clamp dose (0=suppress, 0.5=natural, 1=boost)")
        axis.grid(alpha=0.2)
    axes[0, 0].legend(frameon=False)
    figure.suptitle(f"{label}: regional causal attention intervention", fontweight="bold")
    save_figure(figure, output)
    plt.close(figure)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    parser.add_argument("--threads", type=int, default=3)
    parser.add_argument("--psychometric-trials", type=int, default=300)
    parser.add_argument("--attention-trials", type=int, default=128)
    parser.add_argument("--intervention-trials", type=int, default=250)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for name in ("psychometric_trials", "attention_trials", "intervention_trials", "threads"):
        if getattr(args, name) <= 0:
            raise ValueError(f"--{name.replace('_', '-')} must be positive")
    if args.output_root.exists():
        raise FileExistsError(f"refusing to overwrite output root: {args.output_root}")
    args.checkpoint = args.checkpoint.expanduser().resolve()
    actual_sha = sha256_file(args.checkpoint)
    if actual_sha.lower() != args.expected_sha256.lower():
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {actual_sha} != {args.expected_sha256}")

    os.environ["RVIT_DEVICE"] = args.device
    # PyTorch 2.8 / NumPy 2 checkpoints reference numpy._core; provide the
    # compatible alias before torch 1.13 deserializes them on the local rig.
    sys.modules.setdefault("numpy._core", np.core)
    sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
    import torch
    torch.set_num_threads(args.threads)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA evaluation requested but torch.cuda.is_available() is false")
    from vda_sweep import vda_core as core

    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    if not isinstance(checkpoint, dict) or "model_state_dict" not in checkpoint:
        raise ValueError("checkpoint lacks model_state_dict")
    if checkpoint.get("task") != "vda4" or int(checkpoint.get("iter", -1)) != 19999:
        raise ValueError(f"checkpoint is not terminal VDA4 iteration 19999: task={checkpoint.get('task')} iter={checkpoint.get('iter')}")
    model_kwargs = checkpoint.get("model_kwargs")
    if not isinstance(model_kwargs, dict):
        raise ValueError("spatial-scaling evaluation requires embedded model_kwargs")
    feedback = str(model_kwargs.get("feedback"))
    grid_rows, grid_cols = int(model_kwargs.get("grid_rows", -1)), int(model_kwargs.get("grid_cols", -1))
    d_mem, image_size = int(model_kwargs.get("d_mem", -1)), int(model_kwargs.get("image_size", -1))
    if feedback not in ("affine_ew", "crossattn1") or d_mem != 128 or image_size != 50:
        raise ValueError(f"unexpected model contract: feedback={feedback}, d_mem={d_mem}, image_size={image_size}")
    if (grid_rows, grid_cols) not in ((2, 2), (4, 4), (10, 10)):
        raise ValueError(f"unregistered spatial-scaling grid {grid_rows}x{grid_cols}")
    if int(checkpoint.get("checkpoint_schema_version", -1)) < 3:
        raise ValueError("evaluation requires a schema-3 checkpoint")
    producer = checkpoint.get("producer_sha256")
    if not isinstance(producer, dict) or not producer:
        raise ValueError("checkpoint lacks producer SHA-256 provenance")

    model, iteration = core.load(
        "vda4", feedback, d_mem, checkpoint_path=str(args.checkpoint),
        expected_checkpoint_sha256=actual_sha, require_iteration=19999, validate_metadata=False,
    )
    n_tokens = grid_rows * grid_cols
    if int(model.n_tokens) != n_tokens or str(model.encoder.feedback) != feedback:
        raise RuntimeError("loaded model does not match independently validated checkpoint contract")
    install_explicit_attention_interventions(model, feedback)
    regions = all_task_regions(grid_rows, grid_cols)

    args.output_root.mkdir(parents=True)
    started = time.time()
    metadata = {
        "label": args.label, "task": "vda4", "feedback": feedback, "grid_rows": grid_rows,
        "grid_cols": grid_cols, "n_tokens": n_tokens, "checkpoint_iteration": iteration,
        "checkpoint_path": str(args.checkpoint), "checkpoint_sha256": actual_sha,
        "producer_path": str(Path(__file__).resolve()), "producer_sha256": sha256_file(Path(__file__).resolve()),
    }
    config = {
        **metadata, "device": args.device, "threads": args.threads,
        "psychometric_trials": args.psychometric_trials, "attention_trials": args.attention_trials,
        "intervention_trials": args.intervention_trials, "validities": VALIDITIES,
        "magnitudes": MAGNITUDES, "focal_magnitude": FOCAL_MAGNITUDE,
        "focal_validity": FOCAL_VALIDITY, "qualifying_frames": QUALIFYING_FRAMES,
        "region_tokens": regions, "regional_uniform_baseline": 0.25,
        "checkpoint_producer_sha256": producer,
    }
    (args.output_root / "analysis_config.json").write_text(json.dumps(jsonable(config), indent=2) + "\n", encoding="utf-8")

    psych = compute_psychometrics(model, core, args.psychometric_trials)
    attention = compute_event_attention(model, core, args.attention_trials, n_tokens, regions)
    interventions = compute_interventions(model, core, args.intervention_trials, feedback, n_tokens, regions)
    save_npz(args.output_root / "data" / "psychometrics.npz", psych, metadata)
    save_npz(args.output_root / "data" / "event_attention.npz", attention, metadata)
    save_npz(args.output_root / "data" / "interventions.npz", interventions, metadata)
    write_baseline_table(args.output_root / "tables" / "psychometrics.csv", psych, args.label)
    write_intervention_table(args.output_root / "tables" / "regional_interventions.csv", interventions, args.label)

    plt = configure_plots()
    plot_psychometrics(plt, psych, args.output_root / "figures" / "valid_invalid_response_rt", args.label)
    plot_attention(plt, attention, args.output_root / "figures" / "event_attention_maps", args.label, grid_rows, grid_cols)
    plot_interventions(plt, interventions, args.output_root / "figures" / "regional_causal_intervention", args.label)

    natural = interventions["explicit_modes"].tolist().index("natural")
    disabled = interventions["explicit_modes"].tolist().index("disable")
    summary = {
        "schema_version": 1,
        "model": metadata,
        "training_is_not_scientific_validation": True,
        "anchor_100pct_30deg": {
            "valid_response_rate": float(psych["response_rate"][-1, -1, 0]),
            "invalid_response_rate": float(psych["response_rate"][-1, -1, 1]),
            "false_alarm_rate": float(psych["false_alarm_rate"][-1]),
            "valid_dprime": float(psych["dprime"][-1, -1, 0]),
            "invalid_dprime": float(psych["dprime"][-1, -1, 1]),
        },
        "natural_vs_disabled_invalid": {
            "natural_response_rate": float(interventions["explicit_response_rate"][natural, 1]),
            "disabled_response_rate": float(interventions["explicit_response_rate"][disabled, 1]),
            "difference_disabled_minus_natural": float(
                interventions["explicit_response_rate"][disabled, 1] - interventions["explicit_response_rate"][natural, 1]
            ),
        },
        "elapsed_seconds": time.time() - started,
    }
    (args.output_root / "SUMMARY.json").write_text(json.dumps(jsonable(summary), indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "status": "complete",
        "model": metadata,
        "config_path": "analysis_config.json",
        "summary_path": "SUMMARY.json",
        "artifact_hashes": {
            str(path.relative_to(args.output_root)).replace("\\", "/"): sha256_file(path)
            for path in sorted(args.output_root.rglob("*")) if path.is_file()
        },
    }
    (args.output_root / "MANIFEST.json").write_text(json.dumps(jsonable(manifest), indent=2) + "\n", encoding="utf-8")
    print(f"[complete] wrote {args.output_root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
