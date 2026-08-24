#!/usr/bin/env python3
"""Freeze a live Luo checkpoint and produce source-resolved spatial attention maps.

This is a one-shot analysis producer. It never modifies or pauses the live trainer.
The matched rollout preserves the checkpoint's task, session base orientations,
sensory noise, theta, seven-frame state machine, mnemonic noise, and sampled actions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.luo2015_attention_allocation import (  # noqa: E402
    phase_contrasts,
    quadrant_indices,
    query_averaged_source_mass,
    query_quadrant_routing,
    summarize_contrasts,
)
from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank  # noqa: E402
from luo2015_analysis.luo2015_core import classify_trial, load_model  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_press_sampled(logits, torch):
    actions = torch.distributions.Categorical(logits=logits).sample().cpu().numpy()
    press = np.full(actions.shape[0], -1, dtype=np.int64)
    for frame in range(actions.shape[1]):
        mask = (actions[:, frame] == 1) & (press < 0)
        press[mask] = frame
    return press


def source_quadrant_mass(source_mass: np.ndarray, rows: int, cols: int) -> np.ndarray:
    return np.stack(
        [source_mass[..., list(region)].sum(axis=-1) for region in quadrant_indices(rows, cols)],
        axis=-1,
    )


def plot_phase_maps(source_mass, locations, status, rows, cols, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    selections = [
        ("Initial samples, t0–t1", np.ones(len(locations), dtype=bool), (0, 1), (0, 3)),
        ("First test at location 0, t3–t4", locations == 0, (3, 4), (0,)),
        ("First test at location 3, t3–t4", locations == 3, (3, 4), (3,)),
        ("Second changed test at location 0, t6", (locations == 0) & (status == 0), (6,), (0,)),
        ("Second changed test at location 3, t6", (locations == 3) & (status == 0), (6,), (3,)),
    ]
    maps = []
    for _label, mask, frames, _outline in selections:
        selected = source_mass[mask][:, list(frames)].mean(axis=(0, 1))
        maps.append(
            (
                np.log2(np.maximum(2 * rows * cols * selected[0], 1e-6)),
                np.log2(np.maximum(2 * rows * cols * selected[1], 1e-6)),
                np.log2(np.maximum(rows * cols * selected.sum(axis=0), 1e-6)),
            )
        )
    limit = max(2.0, float(np.ceil(max(np.abs(item).max() for row in maps for item in row))))
    fig, axes = plt.subplots(len(selections), 3, figsize=(11.0, 15.0), constrained_layout=True)
    image = None
    for r, ((label, _mask, _frames, outlines), row_maps) in enumerate(zip(selections, maps)):
        for c, data in enumerate(row_maps):
            ax = axes[r, c]
            image = ax.imshow(data.reshape(rows, cols), cmap="coolwarm", vmin=-limit, vmax=limit, interpolation="nearest")
            ax.axvline(cols / 2 - 0.5, color="black", linewidth=0.8)
            ax.axhline(rows / 2 - 0.5, color="black", linewidth=0.8)
            for quadrant in outlines:
                qr, qc = divmod(quadrant, 2)
                ax.add_patch(Rectangle((qc * cols / 2 - 0.5, qr * rows / 2 - 0.5), cols / 2, rows / 2,
                                       fill=False, edgecolor="#00D084", linewidth=2.0))
            ax.set_xticks([])
            ax.set_yticks([])
            if r == 0:
                ax.set_title(("Visual keys", "Recurrent-memory keys", "Co-located visual + memory")[c], fontweight="bold")
            if c == 0:
                ax.set_ylabel(label, fontweight="bold")
    fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.65, label="log2(attention / uniform key baseline)")
    fig.suptitle("Luo neutral parent: source-resolved cross-attention allocation", fontweight="bold")
    fig.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_timecourses(source_mass, routing, locations, status, rows, cols, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    source_q = source_quadrant_mass(source_mass, rows, cols)
    combined = source_q.sum(axis=-2)
    trial = np.arange(len(locations))
    target = locations
    other = 3 - locations
    target_mass = combined[trial[:, None], np.arange(7)[None, :], target[:, None]]
    other_mass = combined[trial[:, None], np.arange(7)[None, :], other[:, None]]
    blank_mass = combined[:, :, [1, 2]].mean(axis=-1)
    same_memory = routing[trial[:, None], np.arange(7)[None, :], target[:, None], 1, target[:, None]]
    other_memory = routing[trial[:, None], np.arange(7)[None, :], target[:, None], 1, other[:, None]]
    source_share = source_mass.sum(axis=-1)

    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.0), constrained_layout=True)
    frame_labels = ("sample 1", "sample 2", "delay", "test 1", "test 1", "gap", "test 2")
    x = np.arange(7)
    for ax, condition, title in ((axes[0, 0], 1, "Changed first test"), (axes[0, 1], 0, "No-change first test → second changed test")):
        mask = status == condition
        for values, label, color in (
            (target_mass, "tested location", "#0072B2"),
            (other_mass, "other sample location", "#D55E00"),
            (blank_mass, "mean blank quadrant", "#777777"),
        ):
            mean = values[mask].mean(axis=0)
            sem = values[mask].std(axis=0, ddof=1) / np.sqrt(mask.sum())
            ax.plot(x, mean, marker="o", label=label, color=color)
            ax.fill_between(x, mean - 1.96 * sem, mean + 1.96 * sem, color=color, alpha=0.12)
        ax.axhline(0.25, color="black", linestyle=":", linewidth=0.8)
        ax.set_title(title, fontweight="bold")
        ax.set_xticks(x, frame_labels, rotation=30, ha="right")
        ax.set_ylabel("co-located visual + memory key mass")
        ax.grid(alpha=0.2)
        ax.legend(frameon=False, fontsize=8)

    mask = status == 0
    for values, label, color in (
        (same_memory, "same-location memory key quadrant", "#009E73"),
        (other_memory, "other-sample memory key quadrant", "#CC79A7"),
    ):
        mean = values[mask].mean(axis=0)
        sem = values[mask].std(axis=0, ddof=1) / np.sqrt(mask.sum())
        axes[1, 0].plot(x, mean, marker="o", label=label, color=color)
        axes[1, 0].fill_between(x, mean - 1.96 * sem, mean + 1.96 * sem, color=color, alpha=0.12)
    axes[1, 0].set_title("No-change trials: tested-query routing", fontweight="bold")
    axes[1, 0].set_xticks(x, frame_labels, rotation=30, ha="right")
    axes[1, 0].set_ylabel("raw joint-softmax mass")
    axes[1, 0].grid(alpha=0.2)
    axes[1, 0].legend(frameon=False, fontsize=8)

    for source_index, label, color in ((0, "visual keys", "#56B4E9"), (1, "memory keys", "#E69F00")):
        mean = source_share[:, :, source_index].mean(axis=0)
        sem = source_share[:, :, source_index].std(axis=0, ddof=1) / np.sqrt(len(source_share))
        axes[1, 1].plot(x, mean, marker="o", label=label, color=color)
        axes[1, 1].fill_between(x, mean - 1.96 * sem, mean + 1.96 * sem, color=color, alpha=0.12)
    axes[1, 1].axhline(0.5, color="black", linestyle=":", linewidth=0.8)
    axes[1, 1].set_title("Global visual-versus-memory source share", fontweight="bold")
    axes[1, 1].set_xticks(x, frame_labels, rotation=30, ha="right")
    axes[1, 1].set_ylabel("attention mass")
    axes[1, 1].grid(alpha=0.2)
    axes[1, 1].legend(frameon=False, fontsize=8)
    fig.suptitle("Luo neutral parent: attention time course", fontweight="bold")
    fig.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--trials-per-cell", type=int, default=24)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if args.output_root.exists():
        raise RuntimeError(f"refusing to overwrite output root: {args.output_root}")
    if args.trials_per_cell < 2 or args.batch_size < 1 or args.threads < 1:
        raise ValueError("invalid positive trial/batch/thread setting")

    args.output_root.mkdir(parents=True)
    data_dir = args.output_root / "data"
    figures_dir = args.output_root / "figures"
    data_dir.mkdir()
    figures_dir.mkdir()
    snapshot = args.output_root / "checkpoint_snapshot.pt"
    before_hash = sha256_file(args.checkpoint)
    shutil.copy2(args.checkpoint, snapshot)
    after_hash = sha256_file(args.checkpoint)
    snapshot_hash = sha256_file(snapshot)
    if not (before_hash == after_hash == snapshot_hash):
        raise RuntimeError("live checkpoint changed while being copied; rerun with a fresh output root")

    os.environ.setdefault("MPLBACKEND", "Agg")
    import torch

    torch.set_num_threads(args.threads)
    checkpoint = torch.load(snapshot, map_location="cpu", weights_only=False)
    model_kwargs = checkpoint.get("model_kwargs", {})
    rows = int(model_kwargs.get("grid_rows", 0))
    cols = int(model_kwargs.get("grid_cols", 0))
    if (rows, cols) != (20, 20):
        raise RuntimeError(f"expected active 20x20 model, found {rows}x{cols}")
    if model_kwargs.get("feedback") != "crossattn1":
        raise RuntimeError("attention producer requires crossattn1")
    env_state = checkpoint.get("environment_state", {})
    env_config = env_state.get("environment_config", {})
    theta = float(env_state["theta"])
    task = str(checkpoint["task"])
    orientation_sampling = str(env_config.get("orientation_sampling", ""))
    if orientation_sampling != "independent_uniform_axial_0_180":
        raise RuntimeError(
            "checkpoint uses the invalid pre-fix sample-orientation contract; retrain before analysis"
        )
    noise_multiplier = float(env_config["noise_multiplier"])
    spatial_grid_size = int(env_config["spatial_grid_size"])

    model, iteration = load_model(str(snapshot))
    change_videos, nochange_videos, change_locs, nochange_locs = balanced_trial_bank(
        magnitude=theta,
        trials_per_location=args.trials_per_cell,
        seed=args.seed,
        task=task,
        noise_multiplier=noise_multiplier,
        spatial_grid_size=spatial_grid_size,
    )
    videos = torch.cat((change_videos, nochange_videos), dim=0)
    locations = np.concatenate((change_locs, nochange_locs))
    status = np.concatenate((np.ones(len(change_locs), dtype=np.int64), np.zeros(len(nochange_locs), dtype=np.int64)))

    torch.manual_seed(args.seed)
    source_parts = []
    routing_parts = []
    press_parts = []
    for start in range(0, len(videos), args.batch_size):
        stop = min(start + args.batch_size, len(videos))
        print(f"[attention] trials {start}:{stop}/{len(videos)}", flush=True)
        with torch.no_grad():
            result = model.forward_rl_sequence(
                videos[start:stop], return_attn=True, inject_memory_noise=True
            )
        raw = result["attn_seq"].detach().cpu().numpy().astype(np.float32)
        source_parts.append(query_averaged_source_mass(raw, rows * cols).astype(np.float32))
        routing_parts.append(query_quadrant_routing(raw, rows, cols).astype(np.float32))
        press_parts.append(first_press_sampled(result["actor_logits_seq"], torch))
        del result, raw
    source_mass = np.concatenate(source_parts, axis=0)
    routing = np.concatenate(routing_parts, axis=0)
    press = np.concatenate(press_parts)
    outcomes = np.asarray([classify_trial(int(changed), int(value)) for changed, value in zip(status, press)])

    contrasts = phase_contrasts(
        source_mass,
        routing,
        test_locations=locations,
        change_status=status,
        grid_rows=rows,
        grid_cols=cols,
    )
    estimates = summarize_contrasts(contrasts, bootstrap_draws=5000, seed=args.seed)
    initial_query_yes = (
        estimates["sample_query_stimulus_minus_blank_combined"]["direction"] == "positive"
    )
    initial_incoming_yes = (
        estimates["sample_stimulus_minus_blank_combined"]["direction"] == "positive"
    )
    first_t3_memory_yes = (
        estimates["first_test_t3_query_same_minus_other_memory"]["direction"] == "positive"
    )
    first_t4_memory_yes = (
        estimates["first_test_t4_query_same_minus_other_memory"]["direction"] == "positive"
    )
    second_query_yes = (
        estimates["second_test_query_same_minus_other_combined"]["direction"] == "positive"
    )

    np.savez_compressed(
        data_dir / "attention_trials.npz",
        source_token_mass=source_mass,
        query_quadrant_routing=routing,
        test_locations=locations,
        change_status=status,
        press_times=press,
        outcomes=outcomes,
        checkpoint_iteration=np.asarray(iteration),
        checkpoint_sha256=np.asarray(snapshot_hash),
        theta=np.asarray(theta),
    )
    with (data_dir / "contrast_trials.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["trial", "change_status", "test_location", *contrasts])
        for index in range(len(locations)):
            writer.writerow([index, int(status[index]), int(locations[index]), *[float(contrasts[name][index]) for name in contrasts]])

    plot_phase_maps(source_mass, locations, status, rows, cols, figures_dir / "attention_phase_maps")
    plot_timecourses(source_mass, routing, locations, status, rows, cols, figures_dir / "attention_timecourses")

    summary = {
        "schema_version": 1,
        "checkpoint": {
            "source_path": str(args.checkpoint.resolve()),
            "snapshot_path": str(snapshot.resolve()),
            "sha256": snapshot_hash,
            "iteration": int(iteration),
        },
        "contract": {
            "task": task,
            "theta_uniform_bound_degrees": theta,
            "initial_orientation_sampling": orientation_sampling,
            "orientation_period_degrees": 180.0,
            "sensory_orientation_noise_std_degrees": noise_multiplier,
            "memory_noise_enabled": True,
            "sample_actions": True,
            "trials_per_change_status_per_location": args.trials_per_cell,
            "total_trials": int(len(locations)),
            "evaluation_seed": args.seed,
            "model_patch_grid": [rows, cols],
            "task_logical_grid": [2, 2],
        },
        "outcomes": dict(Counter(outcomes.tolist())),
        "estimates": estimates,
        "answers": {
            "cue_exists": False,
            "cue_note": "The Luo task has no explicit cue; both sample Gabors are simultaneously task-relevant at t0-t1.",
            "sample_queries_route_more_mass_to_sample_than_blank_regions": bool(initial_query_yes),
            "sample_regions_receive_more_global_incoming_mass_than_blank_regions": bool(initial_incoming_yes),
            "first_test_onset_t3_query_selects_same_location_memory": bool(first_t3_memory_yes),
            "first_test_repeat_t4_query_selects_same_location_memory": bool(first_t4_memory_yes),
            "guaranteed_second_test_t6_query_reselects_same_location": bool(second_query_yes),
            "timing_note": "t3 is first-test onset; t4 repeats that test. On no-change trials, t6 is a later guaranteed changed test at the same location.",
        },
        "interpretation_boundary": (
            "Weights are descriptive routing evidence for one mid-training checkpoint. "
            "They do not by themselves establish causal use; attention clamping/ablation is required."
        ),
    }
    summary_path = data_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifacts = {}
    for path in sorted(args.output_root.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.json":
            artifacts[path.relative_to(args.output_root).as_posix()] = sha256_file(path)
    manifest = {
        "status": "complete",
        "producer": str(Path(__file__).resolve()),
        "producer_sha256": sha256_file(Path(__file__).resolve()),
        "checkpoint_sha256": snapshot_hash,
        "artifact_hashes": artifacts,
    }
    (args.output_root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary["answers"], indent=2), flush=True)
    print(json.dumps(estimates, indent=2), flush=True)
    print(f"[complete] {args.output_root.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
