#!/usr/bin/env python3
"""Controlled Luo-2015 attention maps, psychometrics, chronometrics, and sample lesions.

The producer consumes an immutable checkpoint. It never reads the mutable live-training
checkpoint. Map cells repeat exactly fixed latent trials while sensory, mnemonic, and policy
sampling noise vary. The causal assay suppresses visual+memory attention keys in the future
first-test location during the two sample frames only, with equal-area active-sample and blank
spatial controls. Controlled fixed-magnitude psychometrics are measurement slices within the
training support, not a replacement for the same-distribution competence probe.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.luo2015_attention_allocation import (  # noqa: E402
    quadrant_indices,
    query_averaged_source_mass,
    query_quadrant_routing,
)
from luo2015_analysis.luo2015_core import classify_trial  # noqa: E402

PHASE_LABELS = ("sample 1", "sample 2", "delay", "test 1 onset", "test 1 repeat", "gap", "test 2")
MAGNITUDES = np.asarray([0.0, 3.0, 6.0, 9.0, 12.0, 18.0, 24.0, 30.0, 35.0])
INTERVENTIONS = ("natural", "tested_sample", "other_sample", "blank_control")
INTERVENTION_LABELS = {
    "natural": "natural attention",
    "tested_sample": "inhibit future-tested sample",
    "other_sample": "inhibit other active sample",
    "blank_control": "inhibit equal-area blank region",
}
COLORS = {
    "natural": "#111111",
    "tested_sample": "#D55E00",
    "other_sample": "#0072B2",
    "blank_control": "#7A7A7A",
}


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


def build_regional_clamp(rows: int, cols: int, location: int, bias: float = -6.0,
                         source: str = "both") -> dict[str, float]:
    regions = quadrant_indices(rows, cols)
    if int(location) not in range(4):
        raise ValueError("location must be in 0..3")
    n = rows * cols
    tokens = list(regions[int(location)])
    if source == "visual":
        keys = tokens
    elif source == "memory":
        keys = [n + token for token in tokens]
    elif source == "both":
        keys = tokens + [n + token for token in tokens]
    else:
        raise ValueError("source must be visual, memory, or both")
    return {str(key): float(bias) for key in keys}


def intervention_location(test_location: int, role: str) -> int:
    test_location = int(test_location)
    if test_location not in (0, 3):
        raise ValueError("Luo test location must be 0 or 3")
    mapping = {
        "tested_sample": test_location,
        "other_sample": 3 - test_location,
        "blank_control": 1 if test_location == 0 else 2,
    }
    if role not in mapping:
        raise ValueError(f"unknown intervention role {role!r}")
    return mapping[role]


def sample_phase_clamp(frame: int, clamp: dict[str, float] | None) -> dict[str, float] | None:
    return clamp if clamp and int(frame) in (0, 1) else None


def regional_source_mass(source_mass: np.ndarray, rows: int, cols: int,
                         locations: np.ndarray, frames: tuple[int, ...] = (0, 1)) -> np.ndarray:
    """Combined visual+memory mass in each trial's selected task quadrant."""
    source = np.asarray(source_mass)
    locations = np.asarray(locations, dtype=np.int64)
    if source.ndim != 4 or source.shape[0] != locations.size or source.shape[2:] != (2, rows * cols):
        raise ValueError("source mass must be trial x time x 2 x N and match locations")
    regions = quadrant_indices(rows, cols)
    result = np.zeros(locations.size, dtype=np.float64)
    for trial_index, location in enumerate(locations):
        selected = source[trial_index, list(frames)][:, :, list(regions[int(location)])]
        result[trial_index] = float(selected.sum(axis=(-2, -1)).mean())
    return result


def first_press(actions: np.ndarray) -> np.ndarray:
    values = np.asarray(actions)
    press = np.full(values.shape[0], -1, dtype=np.int64)
    for frame in range(values.shape[1]):
        mask = (values[:, frame] == 1) & (press < 0)
        press[mask] = frame
    return press


def wilson_interval(count: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return float("nan"), float("nan")
    p = float(count) / float(n)
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, center - half), min(1.0, center + half)


def paired_bootstrap_difference(natural: np.ndarray, inhibited: np.ndarray, *, draws: int = 5000,
                                seed: int = 0) -> dict[str, float | int | None]:
    baseline = np.asarray(natural, dtype=np.float64)
    lesion = np.asarray(inhibited, dtype=np.float64)
    if baseline.shape != lesion.shape or baseline.ndim != 1 or baseline.size == 0:
        raise ValueError("paired vectors must be non-empty and shape matched")
    delta = lesion - baseline
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, delta.size, size=(int(draws), delta.size))
    draws_value = delta[indices].mean(axis=1)
    low, high = np.quantile(draws_value, [0.025, 0.975])
    discordant = int(np.count_nonzero(delta))
    return {
        "n": int(delta.size),
        "mean_inhibited_minus_natural": float(delta.mean()),
        "ci95_low": float(low),
        "ci95_high": float(high),
        "discordant_pairs": discordant,
        # If no paired outcomes differ, ordinary resampling is degenerate. This
        # exact binomial upper bound is a conservative two-sided bound on the
        # absolute mean difference under IID trial-pair sampling.
        "no_discordance_abs_bound_95": (
            float(1.0 - 0.025 ** (1.0 / delta.size)) if discordant == 0 else None
        ),
    }


def render_fixed_trial(env: Any, *, samples: dict[int, float], test_location: int,
                       changed: int, signed_change: float, seed: int) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Render one exactly specified latent trial while recording realized sensory jitter."""
    rng = np.random.RandomState(int(seed))
    test_location = int(test_location)
    changed = int(changed)
    test_orientation = samples[test_location] + (float(signed_change) if changed else 0.0)
    second_orientation = samples[test_location] + float(signed_change)
    frames: list[np.ndarray] = []
    records: list[dict[str, Any]] = []
    for frame in range(7):
        image = np.zeros((env.S, env.S, 3), dtype=np.float32)
        active: list[tuple[int, float]] = []
        if frame in (0, 1):
            active = [(0, samples[0]), (3, samples[3])]
        elif frame in (3, 4):
            active = [(test_location, test_orientation)]
        elif frame == 6 and not changed:
            active = [(test_location, second_orientation)]
        realized: list[dict[str, float | int]] = []
        for location, intended in active:
            actual = float(intended + env.noise_multiplier * rng.normal())
            r0, r1, c0, c1 = env.stimulus_cells[location]
            gabor = env._gabor(actual, r1 - r0, c1 - c0)
            image[r0:r1, c0:c1, :] = np.stack([gabor, gabor, gabor], axis=-1)
            realized.append({"location": int(location), "intended_degrees": float(intended),
                             "realized_degrees": actual})
        env._draw_fixation(image)
        frames.append(image)
        records.append({"frame": frame, "phase": PHASE_LABELS[frame], "stimuli": realized})
    return np.stack(frames), records


def make_trials(env: Any, theta: float, *, changed: int,
                count: int, magnitude: float | None, seed: int,
                fixed_location: int | None = None, fixed_samples: dict[int, float] | None = None,
                fixed_sign: int | None = None) -> tuple[np.ndarray, dict[str, np.ndarray], list[list[dict[str, Any]]]]:
    videos, frame_records = [], []
    fields: dict[str, list[Any]] = {name: [] for name in
        ("test_location", "changed", "signed_change", "magnitude", "sample_orientation0", "sample_orientation3", "video_seed")}
    rng = np.random.default_rng(seed)
    for index in range(int(count)):
        location = int(fixed_location if fixed_location is not None else (0 if index % 2 == 0 else 3))
        if fixed_samples is None:
            samples = {
                0: float(rng.uniform(0.0, 180.0)),
                3: float(rng.uniform(0.0, 180.0)),
            }
        else:
            if set(fixed_samples) != {0, 3}:
                raise ValueError("fixed_samples must have exactly locations {0, 3}")
            samples = {location_id: float(fixed_samples[location_id]) for location_id in (0, 3)}
        if magnitude is None:
            signed = float(rng.uniform(-theta, theta))
        else:
            sign = int(fixed_sign if fixed_sign is not None else (1 if (index // 8) % 2 == 0 else -1))
            signed = sign * float(magnitude)
        # NumPy's legacy MT19937 renderer accepts unsigned 32-bit seeds only.
        video_seed = int((seed * 100000 + index + 17) % (2**32 - 1))
        video, records = render_fixed_trial(
            env, samples=samples, test_location=location, changed=changed,
            signed_change=signed, seed=video_seed,
        )
        videos.append(video)
        frame_records.append(records)
        for name, value in (
            ("test_location", location), ("changed", int(changed)), ("signed_change", signed),
            ("magnitude", abs(signed)), ("sample_orientation0", samples[0]),
            ("sample_orientation3", samples[3]),
            ("video_seed", video_seed),
        ):
            fields[name].append(value)
    array = np.stack(videos).astype(np.float32).transpose(0, 1, 4, 2, 3)
    metadata = {name: np.asarray(value) for name, value in fields.items()}
    return array, metadata, frame_records


def _unwrap_attention(value: Any) -> Any:
    while isinstance(value, (list, tuple)) and len(value) == 1:
        value = value[0]
    if isinstance(value, (list, tuple)):
        raise RuntimeError("expected exactly one attention tensor")
    return value


def rollout(model: Any, videos: np.ndarray, locations: np.ndarray, *, role: str, bias: float,
            rows: int, cols: int, seed: int, batch_size: int, torch: Any,
            capture_attention: bool = False) -> dict[str, np.ndarray]:
    """Online stochastic rollout with phase-specific sample attention intervention."""
    total = len(videos)
    actions_all = np.zeros((total, 7), dtype=np.int64)
    probabilities_all = np.zeros((total, 7), dtype=np.float32)
    source_all = np.zeros((total, 7, 2, rows * cols), dtype=np.float32) if capture_attention else None
    routing_all = np.zeros((total, 7, 4, 2, 4), dtype=np.float32) if capture_attention else None
    for location in (0, 3):
        group = np.flatnonzero(np.asarray(locations) == location)
        if not group.size:
            continue
        clamp = None
        if role != "natural":
            target = intervention_location(location, role)
            clamp = build_regional_clamp(rows, cols, target, bias=bias, source="both")
        torch.manual_seed(int(seed + location))
        for begin in range(0, len(group), int(batch_size)):
            chosen = group[begin:begin + int(batch_size)]
            tensor = torch.from_numpy(videos[chosen]).to(dtype=torch.float32)
            state = model.init_states(len(chosen), device="cpu")
            for frame in range(7):
                with torch.no_grad():
                    step = model.rl_step(
                        tensor[:, frame], state, return_attn=capture_attention,
                        attn_clamp=sample_phase_clamp(frame, clamp), inject_memory_noise=True,
                    )
                    distribution = torch.distributions.Categorical(logits=step["actor_logits"])
                    action = distribution.sample()
                    probability = torch.softmax(step["actor_logits"], dim=-1)[:, 1]
                state = step["new_states"]
                actions_all[chosen, frame] = action.cpu().numpy()
                probabilities_all[chosen, frame] = probability.cpu().numpy()
                if capture_attention:
                    raw = _unwrap_attention(step["attn"]).detach().cpu().numpy().astype(np.float32)
                    source_all[chosen, frame] = query_averaged_source_mass(raw, rows * cols)
                    routing_all[chosen, frame] = query_quadrant_routing(raw, rows, cols)
    result = {
        "actions": actions_all,
        "press": first_press(actions_all),
        "declare_probability": probabilities_all,
    }
    if capture_attention:
        result["source_mass"] = source_all
        result["routing"] = routing_all
    return result


def outcome_arrays(changed: np.ndarray, press: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    outcomes = np.asarray([classify_trial(int(c), int(p)) for c, p in zip(changed, press)])
    correct = np.isin(outcomes, ("hit", "correct_rejection"))
    return outcomes, correct


def sdt_metrics(change_press: np.ndarray, nochange_press: np.ndarray) -> dict[str, float | int]:
    from statistics import NormalDist
    change_outcomes, _ = outcome_arrays(np.ones(len(change_press)), change_press)
    nochange_outcomes, _ = outcome_arrays(np.zeros(len(nochange_press)), nochange_press)
    valid_change = np.isin(change_outcomes, ("hit", "miss"))
    valid_nochange = np.isin(nochange_outcomes, ("false_alarm", "correct_rejection"))
    hits = int((change_outcomes == "hit").sum())
    false_alarms = int((nochange_outcomes == "false_alarm").sum())
    nh, nf = int(valid_change.sum()), int(valid_nochange.sum())
    if not nh or not nf:
        return {"n_change": nh, "n_nochange": nf, "hit_rate": float("nan"),
                "false_alarm_rate": float("nan"), "dprime": float("nan"), "criterion": float("nan")}
    hr = (hits + 0.5) / (nh + 1.0)
    fa = (false_alarms + 0.5) / (nf + 1.0)
    normal = NormalDist()
    zh, zf = normal.inv_cdf(hr), normal.inv_cdf(fa)
    return {
        "n_change": nh, "n_nochange": nf, "hits": hits, "false_alarms": false_alarms,
        "hit_rate": hits / nh, "false_alarm_rate": false_alarms / nf,
        "dprime": zh - zf, "criterion": -0.5 * (zh + zf),
        "excluded_change": int(len(change_press) - nh), "excluded_nochange": int(len(nochange_press) - nf),
    }


def _survivor_mask(changed: int, press: np.ndarray, frame: int) -> np.ndarray:
    press = np.asarray(press)
    seen = (press < 0) | (press >= frame)
    if changed and frame > 4:
        seen &= False
    return seen


def configure_plots() -> Any:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.spines.top": False, "axes.spines.right": False,
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    return plt


def save_figure(fig: Any, stem: Path, plt: Any) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_condition_maps(map_payload: dict[str, dict[str, Any]], rows: int, cols: int,
                        figures: Path, plt: Any) -> None:
    condition_names = list(map_payload)
    for source_index, source_label in ((0, "visual keys"), (1, "recurrent-memory keys"), (2, "combined keys")):
        prepared: list[list[np.ndarray | None]] = []
        maxima = []
        for name in condition_names:
            item = map_payload[name]
            maps = []
            for frame in range(7):
                mask = _survivor_mask(item["changed"], item["press"], frame)
                if not mask.any():
                    maps.append(None)
                    continue
                source = item["source_mass"][mask, frame]
                token = source[:, source_index].mean(axis=0) if source_index < 2 else source.sum(axis=1).mean(axis=0)
                baseline = 1.0 / (2 * rows * cols) if source_index < 2 else 1.0 / (rows * cols)
                value = np.log2(np.maximum(token / baseline, 1e-6)).reshape(rows, cols)
                maps.append(value)
                maxima.append(float(np.abs(value).max()))
            prepared.append(maps)
        limit = 6.0  # fixed interpretable range; extreme near-zero keys are saturated.
        fig, axes = plt.subplots(len(condition_names), 7, figsize=(15.5, 2.55 * len(condition_names)), constrained_layout=True)
        image = None
        for r, name in enumerate(condition_names):
            display_name = f"{'changed' if map_payload[name]['changed'] else 'unchanged'} · test L{map_payload[name]['location']}"
            for frame in range(7):
                ax = axes[r, frame]
                value = prepared[r][frame]
                if value is None:
                    ax.set_facecolor("#E6E6E6")
                    ax.text(0.5, 0.5, "not experienced", ha="center", va="center", transform=ax.transAxes, fontsize=7)
                else:
                    image = ax.imshow(value, cmap="coolwarm", vmin=-limit, vmax=limit, interpolation="nearest")
                    ax.axvline(cols / 2 - 0.5, color="black", lw=0.5)
                    ax.axhline(rows / 2 - 0.5, color="black", lw=0.5)
                if r == 0:
                    ax.set_title(f"t{frame}\n{PHASE_LABELS[frame]}", fontsize=8)
                if frame == 0:
                    ax.set_ylabel(display_name, fontweight="bold", fontsize=9)
                ax.set_xticks([]); ax.set_yticks([])
        if image is not None:
            fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.6, label="log2(attention / uniform key baseline)")
        fig.suptitle(f"Noise-averaged incoming attention: {source_label} (survivor controlled)", fontweight="bold")
        save_figure(fig, figures / f"attention_maps_{source_label.replace(' ', '_').replace('-', '_')}", plt)

    routing_vmax = 0.4
    for name in condition_names:
        item = map_payload[name]
        for frame in range(7):
            mask = _survivor_mask(item["changed"], item["press"], frame)
            if mask.any():
                routing_vmax = max(routing_vmax, float(item["routing"][mask, frame].sum(axis=2).mean(axis=0).max()))
    fig, axes = plt.subplots(len(condition_names), 7, figsize=(15.2, 2.35 * len(condition_names)), constrained_layout=True)
    image = None
    for r, name in enumerate(condition_names):
        item = map_payload[name]
        display_name = f"{'changed' if item['changed'] else 'unchanged'} · test L{item['location']}"
        for frame in range(7):
            ax = axes[r, frame]
            mask = _survivor_mask(item["changed"], item["press"], frame)
            if mask.any():
                matrix = item["routing"][mask, frame].sum(axis=2).mean(axis=0)
                image = ax.imshow(matrix, cmap="magma", vmin=0.0, vmax=routing_vmax)
                ax.set_xticks(range(4)); ax.set_yticks(range(4))
            else:
                ax.set_facecolor("#E6E6E6"); ax.set_xticks([]); ax.set_yticks([])
            if r == 0: ax.set_title(f"t{frame}")
            if frame == 0: ax.set_ylabel(display_name, fontsize=9)
    if image is not None:
        fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.6, label="joint-softmax mass")
    fig.supxlabel("key quadrant"); fig.supylabel("query quadrant")
    fig.suptitle("Query-conditioned spatial routing (visual + memory; survivor controlled)", fontweight="bold")
    save_figure(fig, figures / "attention_query_to_key_routing", plt)


def plot_psychometric(curves: dict[str, Any], figures: Path, plt: Any) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.2), constrained_layout=True)
    for role in INTERVENTIONS:
        payload = curves[role]
        axes[0, 0].plot(MAGNITUDES, payload["hit_rate"], marker="o", color=COLORS[role], label=INTERVENTION_LABELS[role])
        axes[0, 1].plot(MAGNITUDES, payload["dprime"], marker="o", color=COLORS[role])
        axes[1, 0].plot(MAGNITUDES, payload["mean_hit_frame"], marker="o", color=COLORS[role])
        axes[1, 1].plot(MAGNITUDES, payload["early_hit_fraction"], marker="o", color=COLORS[role])
    axes[0, 0].set(title="A  Psychometric function", ylabel="hit rate", ylim=(-0.03, 1.03))
    axes[0, 1].set(title="B  Sensitivity", ylabel="$d'$",)
    axes[1, 0].set(title="C  Chronometric function", ylabel="mean response frame | hit", ylim=(2.9, 4.1))
    axes[1, 1].set(title="D  Early-hit probability", ylabel="P(response at t3 | hit)", ylim=(-0.03, 1.03))
    for ax in axes.flat:
        ax.set_xlabel("fixed absolute orientation change (degrees)"); ax.grid(alpha=0.2)
    axes[0, 0].legend(frameon=False, fontsize=7)

    fig.suptitle("Controlled psychometric and chronometric slices under sample-phase attention inhibition", fontweight="bold")
    save_figure(fig, figures / "psychometric_chronometric_curves", plt)


def plot_intervention_summary(summary: dict[str, Any], figures: Path, plt: Any) -> None:
    roles = list(INTERVENTIONS)
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 3.8), constrained_layout=True)
    colors = [COLORS[r] for r in roles]
    accuracy = [summary["intervention_overall"][r]["all_trial_accuracy"] for r in roles]
    sample_mass = [summary["intervention_overall"][r]["target_region_sample_mass"] for r in roles]
    delta = [summary["paired_accuracy_effects"].get(r, {}).get("mean_inhibited_minus_natural", 0.0) for r in roles]
    axes[0].bar(range(4), accuracy, color=colors)
    axes[0].set(title="A  Overall task accuracy", ylabel="accuracy", ylim=(0, 1))
    axes[1].bar(range(4), sample_mass, color=colors)
    axes[1].set(title="B  Attention at corresponding region", ylabel="mean sample-frame mass")
    axes[2].bar(range(4), delta, color=colors)
    axes[2].axhline(0, color="black", lw=0.8)
    axes[2].set(title="C  Paired accuracy effect", ylabel="intervention − natural")

    for index, value in enumerate(sample_mass):
        axes[1].text(index, value + 0.004, f"{value:.4f}", ha="center", va="bottom", fontsize=8)
    for ax in axes:
        ax.set_xticks(range(4), ["natural", "tested", "other", "blank"], rotation=25, ha="right"); ax.grid(axis="y", alpha=0.2)
    fig.suptitle("Sample-phase regional attention inhibition and equal-area controls", fontweight="bold")
    save_figure(fig, figures / "sample_attention_inhibition_summary", plt)


def create_trial_artifacts(model: Any, env: Any, theta: float, rows: int, cols: int,
                           output: Path, torch: Any, plt: Any, seed: int) -> dict[str, Any]:
    from PIL import Image
    output.mkdir(parents=True, exist_ok=True)
    # Preselect the canonical replicate independently of behavior. Never search for a
    # correct or visually attractive example after inspecting outcomes.
    offset = 0
    videos, metadata, records = make_trials(
        env, theta, changed=0, count=1, magnitude=18.0, seed=seed,
        fixed_location=0, fixed_samples={0: 45.0, 3: 135.0}, fixed_sign=1,
    )
    result = rollout(model, videos, metadata["test_location"], role="natural", bias=-6.0,
                     rows=rows, cols=cols, seed=seed + 1000, batch_size=1,
                     torch=torch, capture_attention=True)
    outcome = classify_trial(0, int(result["press"][0]))
    records = records[0]
    panels = []
    frame_paths = []
    for frame in range(7):
        image = videos[0, frame].transpose(1, 2, 0)
        attention = result["source_mass"][0, frame].sum(axis=0).reshape(rows, cols)
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3), constrained_layout=True)
        axes[0].imshow(image.mean(axis=-1), cmap="gray", vmin=-1.0, vmax=1.0)
        axes[0].set_title(f"Input image — t{frame}: {PHASE_LABELS[frame]}")
        axes[1].imshow(np.log2(np.maximum(attention * rows * cols, 1e-6)), cmap="coolwarm", vmin=-6, vmax=6)
        axes[1].set_title("Incoming attention\nlog2(relative to uniform)")
        for ax in axes: ax.set_xticks([]); ax.set_yticks([])
        action = int(result["actions"][0, frame])
        probability = float(result["declare_probability"][0, frame])
        stimulus_text = "; ".join(
            f"L{s['location']}: {s['realized_degrees']:.1f}°" for s in records[frame]["stimuli"]
        ) or "blank"
        fig.suptitle(f"{stimulus_text} | P(declare)={probability:.3f} | sampled action={'DECLARE' if action else 'WAIT'}", fontsize=10)
        canvas = fig.canvas
        canvas.draw()
        width, height = canvas.get_width_height()
        panel = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8).reshape(height, width, 4)[..., :3]
        panels.append(Image.fromarray(panel))
        frame_path = output / f"trial_frame_t{frame}.png"
        fig.savefig(frame_path, dpi=180, bbox_inches="tight")
        frame_paths.append(str(frame_path))
        plt.close(fig)
    gif_path = output / "specific_trial_all_frames.gif"
    panels[0].save(gif_path, save_all=True, append_images=panels[1:], duration=1100, loop=0, optimize=False)
    montage_fig, montage_axes = plt.subplots(2, 4, figsize=(12.5, 6.0), constrained_layout=True)
    for frame, ax in enumerate(montage_axes.flat):
        if frame < 7:
            ax.imshow(videos[0, frame].mean(axis=0), cmap="gray", vmin=-1.0, vmax=1.0); ax.set_title(f"t{frame}: {PHASE_LABELS[frame]}")
        else:
            ax.axis("off")
        ax.set_xticks([]); ax.set_yticks([])
    montage_fig.suptitle(
        f"Canonical complete trial (replicate 0): unchanged first test, guaranteed changed second test, {outcome.replace('_', ' ')}",
        fontweight="bold",
    )
    save_figure(montage_fig, output / "specific_trial_montage", plt)
    trial_record = {
        "latent_condition": {
            "sample_orientations": {"0": float(base[0]), "3": float(base[3])},
            "test_location": 0, "first_test_changed": False,
            "guaranteed_second_test_change_degrees": 18.0,
        },
        "sensory_frames": records,
        "declare_probabilities": result["declare_probability"][0].tolist(),
        "sampled_actions": result["actions"][0].tolist(),
        "first_press": int(result["press"][0]),
        "outcome": outcome,
        "selection_rule": "canonical fixed replicate 0, preselected independently of behavior",
        "candidate_offset": offset,
        "gif": str(gif_path), "individual_frames": frame_paths,
    }
    (output / "specific_trial.json").write_text(json.dumps(trial_record, indent=2) + "\n", encoding="utf-8")
    return trial_record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--map-repeats", type=int, default=64)
    parser.add_argument("--curve-trials", type=int, default=64)
    parser.add_argument("--nochange-trials", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--bias", type=float, default=-6.0)
    parser.add_argument("--seed", type=int, default=20260803)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.output_root.exists():
        raise FileExistsError(f"refusing to overwrite {args.output_root}")
    actual_hash = sha256_file(args.checkpoint)
    if actual_hash.lower() != args.expected_sha256.lower():
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {actual_hash}")
    args.output_root.mkdir(parents=True)
    data_dir = args.output_root / "data"; data_dir.mkdir()
    figures_dir = args.output_root / "figures"; figures_dir.mkdir()
    trial_dir = args.output_root / "trial"; trial_dir.mkdir()
    os.environ["RVIT_DEVICE"] = "cpu"
    os.environ["MPLBACKEND"] = "Agg"
    import torch
    torch.set_num_threads(args.threads)
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    kwargs = checkpoint["model_kwargs"]
    rows, cols = int(kwargs["grid_rows"]), int(kwargs["grid_cols"])
    if (rows, cols) != (20, 20) or kwargs["feedback"] != "crossattn1":
        raise RuntimeError("assay is registered for the 20x20 crossattn1 Luo checkpoint")
    env_state = checkpoint["environment_state"]
    config = env_state["environment_config"]
    theta = float(env_state["theta"])
    orientation_sampling = str(config.get("orientation_sampling", ""))
    if orientation_sampling != "independent_uniform_axial_0_180":
        raise RuntimeError(
            "checkpoint uses the invalid pre-fix sample-orientation contract; retrain before analysis"
        )
    noise = float(config["noise_multiplier"])
    task = str(checkpoint["task"])
    from luo2015_analysis.luo2015_core import _env, load_model
    model, iteration = load_model(str(args.checkpoint))
    model.to("cpu"); model.eval()
    env = _env(task, theta, spatial_grid_size=int(config["spatial_grid_size"]),
               noise_multiplier=noise)
    started = time.time()

    # Exact-latent repeated map cells; only sensory, mnemonic, and policy sampling noise vary.
    map_payload: dict[str, dict[str, Any]] = {}
    for changed, status_label in ((1, "changed"), (0, "unchanged")):
        for location in (0, 3):
            name = f"{status_label}, test L{location}, +18°, samples 45°/135°"
            videos, metadata, _ = make_trials(
                env, theta, changed=changed, count=args.map_repeats, magnitude=18.0,
                seed=args.seed + changed * 100 + location, fixed_location=location,
                fixed_samples={0: 45.0, 3: 135.0}, fixed_sign=1,
            )
            result = rollout(model, videos, metadata["test_location"], role="natural", bias=args.bias,
                             rows=rows, cols=cols, seed=args.seed + 10000 + changed * 100 + location,
                             batch_size=args.batch_size, torch=torch, capture_attention=True)
            outcomes, correct = outcome_arrays(metadata["changed"], result["press"])
            map_payload[name] = {
                "changed": changed, "location": location, "source_mass": result["source_mass"],
                "routing": result["routing"], "press": result["press"], "outcomes": outcomes,
                "correct": correct,
            }
            print(f"[maps] {name}: {Counter(outcomes.tolist())}", flush=True)

    # Shared no-change trial bank; its guaranteed second-test change remains sampled from the
    # trained uniform support so engagement/exclusion behavior is not fixed by psychometric bin.
    no_videos, no_meta, _ = make_trials(env, theta, changed=0, count=args.nochange_trials,
                                        magnitude=None, seed=args.seed + 20000)
    no_results: dict[str, dict[str, np.ndarray]] = {}
    for role in INTERVENTIONS:
        no_results[role] = rollout(
            model, no_videos, no_meta["test_location"], role=role, bias=args.bias, rows=rows, cols=cols,
            seed=args.seed + 30000, batch_size=args.batch_size, torch=torch, capture_attention=True,
        )
        print(f"[nochange] {role} complete", flush=True)

    curves: dict[str, dict[str, Any]] = {
        role: {key: [] for key in ("hit_rate", "dprime", "criterion", "mean_hit_frame", "early_hit_fraction",
                                   "false_alarm_rate", "change_press", "change_correct")}
        for role in INTERVENTIONS
    }
    changed_by_mag: dict[float, tuple[np.ndarray, dict[str, np.ndarray]]] = {}
    for magnitude_index, magnitude in enumerate(MAGNITUDES):
        videos, metadata, _ = make_trials(
            env, theta, changed=1, count=args.curve_trials, magnitude=float(magnitude),
            seed=args.seed + 40000 + magnitude_index,
        )
        changed_by_mag[float(magnitude)] = (videos, metadata)
        for role in INTERVENTIONS:
            result = rollout(
                model, videos, metadata["test_location"], role=role, bias=args.bias, rows=rows, cols=cols,
                seed=args.seed + 50000 + magnitude_index, batch_size=args.batch_size, torch=torch,
                capture_attention=False,
            )
            metrics = sdt_metrics(result["press"], no_results[role]["press"])
            hit_mask = np.asarray([classify_trial(1, int(p)) == "hit" for p in result["press"]])
            curves[role]["hit_rate"].append(metrics["hit_rate"])
            curves[role]["dprime"].append(metrics["dprime"])
            curves[role]["criterion"].append(metrics["criterion"])
            curves[role]["false_alarm_rate"].append(metrics["false_alarm_rate"])
            curves[role]["mean_hit_frame"].append(float(result["press"][hit_mask].mean()) if hit_mask.any() else float("nan"))
            curves[role]["early_hit_fraction"].append(float((result["press"][hit_mask] == 3).mean()) if hit_mask.any() else float("nan"))
            curves[role]["change_press"].append(result["press"])
            _, correct = outcome_arrays(metadata["changed"], result["press"])
            curves[role]["change_correct"].append(correct)
        print(f"[curves] magnitude {magnitude:g} complete", flush=True)

    intervention_overall: dict[str, Any] = {}
    all_correct: dict[str, np.ndarray] = {}
    for role in INTERVENTIONS:
        change_correct = np.concatenate(curves[role]["change_correct"])
        _, no_correct = outcome_arrays(no_meta["changed"], no_results[role]["press"])
        combined = np.concatenate((change_correct, no_correct)).astype(np.float64)
        all_correct[role] = combined
        source = no_results[role]["source_mass"]
        if role in ("natural", "tested_sample"):
            measured_locations = no_meta["test_location"]
        else:
            measured_locations = np.asarray([
                intervention_location(int(location), role) for location in no_meta["test_location"]
            ])
        target_mass_values = regional_source_mass(source, rows, cols, measured_locations, frames=(0, 1))
        intervention_overall[role] = {
            "all_trial_accuracy": float(combined.mean()),
            "correct_count": int(combined.sum()), "total_trials": int(combined.size),
            "target_region_sample_mass": float(np.mean(target_mass_values)),
            "nochange_outcomes": dict(Counter(outcome_arrays(no_meta["changed"], no_results[role]["press"])[0].tolist())),
        }
    paired_effects = {
        role: paired_bootstrap_difference(all_correct["natural"], all_correct[role], draws=5000,
                                          seed=args.seed + index)
        for index, role in enumerate(INTERVENTIONS) if role != "natural"
    }

    plt = configure_plots()
    plot_condition_maps(map_payload, rows, cols, figures_dir, plt)
    plot_psychometric(curves, figures_dir, plt)
    summary = {
        "schema_version": 1,
        "checkpoint": {"path": str(args.checkpoint.resolve()), "sha256": actual_hash, "iteration": int(iteration)},
        "contract": {
            "task": task, "theta_uniform_training_bound_degrees": theta,
            "initial_orientation_sampling": orientation_sampling,
            "orientation_period_degrees": 180.0, "sensory_noise_std_degrees": noise,
            "mnemonic_noise_std": float(kwargs["memory_noise_std"]), "memory_noise_enabled": True,
            "sampled_actions": True, "model_grid": [rows, cols], "sample_inhibition_frames": [0, 1],
            "sample_inhibition_key_sources": ["visual", "recurrent_memory"],
            "sample_inhibition_logit_bias": args.bias,
            "map_repeats_per_exact_latent_cell": args.map_repeats,
            "curve_changed_trials_per_magnitude": args.curve_trials,
            "common_nochange_trials": args.nochange_trials,
            "fixed_psychometric_magnitudes_degrees": MAGNITUDES,
        },
        "map_conditions": {
            name: {"outcomes": dict(Counter(item["outcomes"].tolist())), "accuracy": float(item["correct"].mean())}
            for name, item in map_payload.items()
        },
        "curves": {role: {key: value for key, value in payload.items() if key not in ("change_press", "change_correct")}
                   for role, payload in curves.items()},
        "intervention_overall": intervention_overall,
        "paired_accuracy_effects": paired_effects,
        "interpretation_boundaries": [
            "Attention maps are descriptive routing weights, not content decoding.",
            "The tested-sample lesion is oracle-targeted to the future first-test location, which is not cued to the model.",
            "Fixed-magnitude curves are controlled measurement slices within the training support; the trained changed-trial sampler is uniform.",
            "Intervals quantify evaluation-trial sampling for one frozen checkpoint, not training-seed uncertainty.",
        ],
        "elapsed_seconds": time.time() - started,
    }
    plot_intervention_summary(summary, figures_dir, plt)
    trial_record = create_trial_artifacts(model, env, theta, rows, cols, trial_dir, torch, plt, args.seed + 70000)
    summary["specific_trial"] = trial_record

    # Store compact scientific data; reduced maps retain source and query-quadrant semantics.
    map_npz: dict[str, Any] = {}
    for index, (name, item) in enumerate(map_payload.items()):
        map_npz[f"condition_{index}_name"] = np.asarray(name)
        for key in ("source_mass", "routing", "press", "outcomes", "correct"):
            map_npz[f"condition_{index}_{key}"] = item[key]
    np.savez_compressed(data_dir / "fixed_condition_attention.npz", **map_npz)
    np.savez_compressed(
        data_dir / "behavioral_curves.npz", magnitudes=MAGNITUDES,
        **{f"{role}_{key}": np.asarray(value) for role, payload in curves.items()
           for key, value in payload.items() if key not in ("change_press", "change_correct")},
    )
    with (data_dir / "psychometric_chronometric.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["intervention", "magnitude", "hit_rate", "false_alarm_rate", "dprime", "criterion",
                         "mean_hit_frame", "early_hit_fraction"])
        for role in INTERVENTIONS:
            for index, magnitude in enumerate(MAGNITUDES):
                writer.writerow([role, magnitude, *[curves[role][key][index] for key in
                    ("hit_rate", "false_alarm_rate", "dprime", "criterion", "mean_hit_frame", "early_hit_fraction")]])
    (data_dir / "summary.json").write_text(json.dumps(jsonable(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_root / "analysis_config.json").write_text(json.dumps(jsonable(vars(args)), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    artifacts = {}
    for path in sorted(args.output_root.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.json":
            artifacts[path.relative_to(args.output_root).as_posix()] = sha256_file(path)
    manifest = {
        "status": "complete", "producer": str(Path(__file__).resolve()),
        "producer_sha256": sha256_file(Path(__file__).resolve()),
        "checkpoint_sha256": actual_hash, "artifact_hashes": artifacts,
    }
    (args.output_root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(jsonable({"intervention_overall": intervention_overall, "paired_effects": paired_effects}), indent=2), flush=True)
    print(f"[complete] {args.output_root.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
