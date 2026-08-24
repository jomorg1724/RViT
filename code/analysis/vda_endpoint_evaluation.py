"""Held-out evaluation for registered 4x4 VDA16 and fixed-nine endpoints.

This producer reuses the frozen spatial-scaling evaluator's tested attention,
SDT, plotting, and artifact primitives without changing that hash-bound source.
VDA16 and controlled fixed-nine use one carrier token per task location.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis import vda4_spatial_scaling_evaluation as base


@dataclass(frozen=True)
class EvaluationProtocol:
    task: str
    cue_index: int
    valid_change_index: int
    invalid_change_index: int
    control_index: int
    active_count: int
    required_active_locations: tuple[int, ...]


PROTOCOLS = {
    "vda16": EvaluationProtocol("vda16", 0, 0, 15, 3, 16, ()),
    # Condition random 9-of-16 layouts on all three probed locations being
    # visible. The other six active items remain a reproducible random nuisance.
    "vda_fixed9": EvaluationProtocol("vda_fixed9", 0, 0, 15, 3, 9, (15, 3)),
}


def evaluation_protocol(task: str, grid_rows: int, grid_cols: int) -> tuple[EvaluationProtocol, tuple[tuple[int, ...], ...]]:
    try:
        protocol = PROTOCOLS[task]
    except KeyError as exc:
        raise ValueError(f"unsupported endpoint task {task!r}; expected {sorted(PROTOCOLS)}") from exc
    if (grid_rows, grid_cols) != (4, 4):
        raise ValueError(f"{task} endpoint evaluation requires a 4x4 grid, got {grid_rows}x{grid_cols}")
    return protocol, tuple((index,) for index in range(16))


def compute_psychometrics(
    model: Any, core: Any, trials: int, protocol: EvaluationProtocol
) -> dict[str, np.ndarray]:
    shape = (len(base.VALIDITIES), len(base.MAGNITUDES), len(base.CONDITIONS))
    counts = np.zeros(shape, dtype=np.int64)
    rates = np.zeros(shape, dtype=np.float64)
    mean_rt = np.full(shape, np.nan, dtype=np.float64)
    histograms = np.zeros(shape + (8,), dtype=np.int64)
    false_alarm_count = np.zeros(len(base.VALIDITIES), dtype=np.int64)
    false_alarm_rate = np.zeros(len(base.VALIDITIES), dtype=np.float64)
    false_alarm_histogram = np.zeros((len(base.VALIDITIES), 8), dtype=np.int64)

    for validity_index, validity in enumerate(base.VALIDITIES):
        nochange_seed = base.PSYCHOMETRIC_SEED + validity_index * 1000 + 900
        nochange_videos = core.make_video_batch(
            protocol.task, protocol.cue_index, float(validity), "red", 0,
            protocol.cue_index, 0.0, B=trials, seed=nochange_seed,
            required_active_locations=protocol.required_active_locations,
        )
        nochange = core.press_times_clamp(
            model, protocol.task, protocol.cue_index, float(validity), "red", 0,
            protocol.cue_index, 0.0, videos=nochange_videos,
        )
        fa_count, _, fa_hist = base.qualifying_stats(nochange, nochange=True)
        false_alarm_count[validity_index] = fa_count
        false_alarm_rate[validity_index] = fa_count / float(trials)
        false_alarm_histogram[validity_index] = fa_hist
        for magnitude_index, magnitude in enumerate(base.MAGNITUDES):
            for condition_index, change_index in enumerate(
                (protocol.valid_change_index, protocol.invalid_change_index)
            ):
                seed = base.PSYCHOMETRIC_SEED + validity_index * 1000 + magnitude_index * 10 + condition_index
                videos = core.make_video_batch(
                    protocol.task, protocol.cue_index, float(validity), "red", 1,
                    change_index, float(magnitude), B=trials, seed=seed,
                    required_active_locations=protocol.required_active_locations,
                )
                press = core.press_times_clamp(
                    model, protocol.task, protocol.cue_index, float(validity), "red", 1,
                    change_index, float(magnitude), videos=videos,
                )
                count, rt, histogram = base.qualifying_stats(press)
                counts[validity_index, magnitude_index, condition_index] = count
                rates[validity_index, magnitude_index, condition_index] = count / float(trials)
                mean_rt[validity_index, magnitude_index, condition_index] = rt
                histograms[validity_index, magnitude_index, condition_index] = histogram
        print(f"[psychometric] validity={validity:.2f} complete", flush=True)

    dprime = np.zeros(shape, dtype=np.float64)
    criterion = np.zeros(shape, dtype=np.float64)
    for validity_index in range(len(base.VALIDITIES)):
        for magnitude_index in range(len(base.MAGNITUDES)):
            for condition_index in range(len(base.CONDITIONS)):
                dprime[validity_index, magnitude_index, condition_index], criterion[
                    validity_index, magnitude_index, condition_index
                ] = base.hautus_sdt(
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


def compute_event_attention(
    model: Any,
    core: Any,
    trials: int,
    n_tokens: int,
    regions: tuple[tuple[int, ...], ...],
    protocol: EvaluationProtocol,
) -> dict[str, np.ndarray]:
    presses, token_masses, region_masses, raw_means = [], [], [], []
    for condition_index, change_index in enumerate(
        (protocol.valid_change_index, protocol.invalid_change_index)
    ):
        videos = core.make_video_batch(
            protocol.task, protocol.cue_index, base.FOCAL_VALIDITY, "red", 1,
            change_index, base.FOCAL_MAGNITUDE, B=trials,
            seed=base.ATTENTION_SEED + condition_index,
            required_active_locations=protocol.required_active_locations,
        )
        press, raw = base.rollout_attention(model, videos, core)
        mass = base.location_mass(raw, n_tokens)
        presses.append(press)
        token_masses.append(mass)
        region_masses.append(base.region_mass(mass, regions))
        raw_means.append(raw.mean(axis=0))
        print(f"[attention] {base.CONDITIONS[condition_index]} complete", flush=True)
    return {
        "press": np.stack(presses, axis=0),
        "token_mass": np.stack(token_masses, axis=0),
        "region_mass": np.stack(region_masses, axis=0),
        "raw_attention_mean": np.stack(raw_means, axis=0),
    }


def compute_interventions(
    model: Any,
    core: Any,
    trials: int,
    feedback: str,
    n_tokens: int,
    regions: tuple[tuple[int, ...], ...],
    protocol: EvaluationProtocol,
) -> dict[str, np.ndarray]:
    role_location = {
        "change": protocol.invalid_change_index,
        "cued": protocol.cue_index,
        "control": protocol.control_index,
    }
    response_count = np.zeros((len(base.REGION_ROLES), len(base.DOSES), 3), dtype=np.int64)
    response_rate = np.zeros_like(response_count, dtype=np.float64)
    mean_rt = np.full_like(response_rate, np.nan, dtype=np.float64)
    histograms = np.zeros(response_count.shape + (8,), dtype=np.int64)
    achieved_change = np.zeros((len(base.REGION_ROLES), len(base.DOSES), core.T), dtype=np.float64)
    achieved_target = np.zeros_like(achieved_change)

    conditions = (
        (1, protocol.valid_change_index, base.FOCAL_MAGNITUDE, base.INTERVENTION_SEED),
        (1, protocol.invalid_change_index, base.FOCAL_MAGNITUDE, base.INTERVENTION_SEED + 1),
        (0, protocol.cue_index, 0.0, base.INTERVENTION_SEED + 2),
    )
    videos_by_condition = tuple(
        core.make_video_batch(
            protocol.task, protocol.cue_index, base.FOCAL_VALIDITY, "red",
            changed, change_index, magnitude, B=trials, seed=seed,
            required_active_locations=protocol.required_active_locations,
        )
        for changed, change_index, magnitude, seed in conditions
    )

    for role_index, role in enumerate(base.REGION_ROLES):
        target_location = role_location[role]
        for dose_index, dose in enumerate(base.DOSES):
            clamp = base.regional_clamp(feedback, n_tokens, regions[target_location], float(dose))
            for condition_index, videos in enumerate(videos_by_condition):
                changed, change_index, magnitude, _ = conditions[condition_index]
                press = core.press_times_clamp(
                    model, protocol.task, protocol.cue_index, base.FOCAL_VALIDITY, "red",
                    changed, change_index, magnitude,
                    clamp=clamp, clamp_from=base.CLAMP_FROM, videos=videos,
                )
                count, rt, histogram = base.qualifying_stats(press, nochange=condition_index == 2)
                response_count[role_index, dose_index, condition_index] = count
                response_rate[role_index, dose_index, condition_index] = count / float(trials)
                mean_rt[role_index, dose_index, condition_index] = rt
                histograms[role_index, dose_index, condition_index] = histogram
            _, raw = base.rollout_attention(model, videos_by_condition[1], core, clamp=clamp)
            regional = base.region_mass(base.location_mass(raw, n_tokens), regions)
            achieved_change[role_index, dose_index] = regional[..., protocol.invalid_change_index].mean(axis=0)
            achieved_target[role_index, dose_index] = regional[..., target_location].mean(axis=0)
        print(f"[intervention] regional role={role} complete", flush=True)

    dprime = np.zeros((len(base.REGION_ROLES), len(base.DOSES), 2), dtype=np.float64)
    criterion = np.zeros_like(dprime)
    for role_index in range(len(base.REGION_ROLES)):
        for dose_index in range(len(base.DOSES)):
            false_alarm = int(response_count[role_index, dose_index, 2])
            for condition_index in range(2):
                dprime[role_index, dose_index, condition_index], criterion[
                    role_index, dose_index, condition_index
                ] = base.hautus_sdt(
                    int(response_count[role_index, dose_index, condition_index]),
                    false_alarm, trials, trials,
                )

    explicit_modes = ("natural", "uniform", "shuffle", "disable")
    explicit_count = np.zeros((len(explicit_modes), 3), dtype=np.int64)
    explicit_rate = np.zeros_like(explicit_count, dtype=np.float64)
    explicit_rt = np.full_like(explicit_rate, np.nan, dtype=np.float64)
    explicit_hist = np.zeros(explicit_count.shape + (8,), dtype=np.int64)
    permutation = base.spatial_shuffle_permutation(feedback, n_tokens)
    for mode_index, mode in enumerate(explicit_modes):
        if mode == "natural":
            clamp: dict[str, Any] | None = None
        elif mode == "shuffle":
            clamp = {"__mode__": "shuffle", "__permutation__": permutation}
        else:
            clamp = {"__mode__": mode}
        for condition_index, videos in enumerate(videos_by_condition):
            press, _ = base.rollout_attention(model, videos, core, clamp=clamp)
            count, rt, histogram = base.qualifying_stats(press, nochange=condition_index == 2)
            explicit_count[mode_index, condition_index] = count
            explicit_rate[mode_index, condition_index] = count / float(trials)
            explicit_rt[mode_index, condition_index] = rt
            explicit_hist[mode_index, condition_index] = histogram
        print(f"[intervention] explicit mode={mode} complete", flush=True)

    explicit_dprime = np.zeros((len(explicit_modes), 2), dtype=np.float64)
    explicit_criterion = np.zeros_like(explicit_dprime)
    for mode_index in range(len(explicit_modes)):
        for condition_index in range(2):
            explicit_dprime[mode_index, condition_index], explicit_criterion[
                mode_index, condition_index
            ] = base.hautus_sdt(
                int(explicit_count[mode_index, condition_index]),
                int(explicit_count[mode_index, 2]), trials, trials,
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


def plot_psychometrics(
    plt: Any, psych: dict[str, np.ndarray], output: Path, label: str, task: str
) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11.2, 4.2), constrained_layout=True)
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(base.VALIDITIES)))
    for validity_index, validity in enumerate(base.VALIDITIES):
        for condition_index, condition in enumerate(base.CONDITIONS):
            style = "-" if condition == "valid" else "--"
            marker = "o" if condition == "valid" else "s"
            axes[0].plot(
                base.MAGNITUDES, psych["response_rate"][validity_index, :, condition_index],
                style, marker=marker, ms=3, color=colors[validity_index],
                label=f"{int(validity * 100)}% {condition}",
            )
            axes[1].plot(
                base.MAGNITUDES, psych["mean_rt"][validity_index, :, condition_index],
                style, marker=marker, ms=3, color=colors[validity_index],
            )
    axes[0].set(title="Response probability", xlabel="orientation change (degrees)",
                ylabel="P(response at frame 5 or 6)", ylim=(-0.03, 1.03))
    axes[1].set(title="Conditional response time", xlabel="orientation change (degrees)",
                ylabel="mean response frame", ylim=(4.8, 6.2))
    for axis in axes:
        axis.grid(alpha=0.2)
    axes[0].legend(ncol=2, fontsize=6.5, frameon=False)
    figure.suptitle(f"{label}: {task} valid/invalid psychometrics and response timing", fontweight="bold")
    base.save_figure(figure, output)
    plt.close(figure)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--task", choices=tuple(PROTOCOLS), required=True)
    parser.add_argument("--expected-seed", type=int, required=True)
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
    actual_sha = base.sha256_file(args.checkpoint)
    if actual_sha.lower() != args.expected_sha256.lower():
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {actual_sha} != {args.expected_sha256}")

    os.environ["RVIT_DEVICE"] = args.device
    sys.modules.setdefault("numpy._core", np.core)
    sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)
    import torch
    torch.set_num_threads(args.threads)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA evaluation requested but torch.cuda.is_available() is false")
    from vda_sweep import vda_core as core

    dependency_paths = (
        Path(__file__).resolve(),
        Path(base.__file__).resolve(),
        Path(core.__file__).resolve(),
        ROOT / "envs" / "__init__.py",
        ROOT / "envs" / "tasks.py",
    )
    dependency_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): base.sha256_file(path)
        for path in dependency_paths
    }
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    if not isinstance(checkpoint, dict) or "model_state_dict" not in checkpoint:
        raise ValueError("checkpoint lacks model_state_dict")
    if checkpoint.get("task") != args.task or int(checkpoint.get("iter", -1)) != 19999:
        raise ValueError(
            f"checkpoint is not terminal {args.task} iteration 19999: "
            f"task={checkpoint.get('task')} iter={checkpoint.get('iter')}"
        )
    model_kwargs = checkpoint.get("model_kwargs")
    training_args = checkpoint.get("training_args")
    if not isinstance(model_kwargs, dict) or not isinstance(training_args, dict):
        raise ValueError("endpoint evaluation requires embedded model_kwargs/training_args")
    feedback = str(model_kwargs.get("feedback"))
    grid_rows = int(model_kwargs.get("grid_rows", -1))
    grid_cols = int(model_kwargs.get("grid_cols", -1))
    protocol, regions = evaluation_protocol(args.task, grid_rows, grid_cols)
    if (
        feedback != "crossattn1"
        or int(model_kwargs.get("d_mem", -1)) != 128
        or int(model_kwargs.get("image_size", -1)) != 100
        or not np.isclose(float(model_kwargs.get("memory_decay", np.nan)), 1.0)
    ):
        raise ValueError("checkpoint is not the registered crossattn1/d128/no-decay 4x4 endpoint")
    if int(training_args.get("seed", -1)) != args.expected_seed:
        raise ValueError("checkpoint seed does not match --expected-seed")
    if int(checkpoint.get("checkpoint_schema_version", -1)) < 3:
        raise ValueError("evaluation requires a schema-3 checkpoint")
    producer = checkpoint.get("producer_sha256")
    if not isinstance(producer, dict) or not producer:
        raise ValueError("checkpoint lacks producer SHA-256 provenance")

    model, iteration = core.load(
        args.task, feedback, 128, checkpoint_path=str(args.checkpoint),
        expected_checkpoint_sha256=actual_sha, require_iteration=19999,
        validate_metadata=False,
    )
    if int(model.n_tokens) != 16 or str(model.encoder.feedback) != feedback:
        raise RuntimeError("loaded model does not match independently validated checkpoint contract")
    base.install_explicit_attention_interventions(model, feedback)

    args.output_root.mkdir(parents=True)
    started = time.time()
    metadata = {
        "label": args.label,
        "task": args.task,
        "feedback": feedback,
        "grid_rows": 4,
        "grid_cols": 4,
        "n_tokens": 16,
        "checkpoint_iteration": iteration,
        "checkpoint_path": str(args.checkpoint),
        "checkpoint_sha256": actual_sha,
        "checkpoint_seed": args.expected_seed,
        "producer_path": str(Path(__file__).resolve()),
        "producer_sha256": base.sha256_file(Path(__file__).resolve()),
    }
    config = {
        **metadata,
        "device": args.device,
        "threads": args.threads,
        "psychometric_trials": args.psychometric_trials,
        "attention_trials": args.attention_trials,
        "intervention_trials": args.intervention_trials,
        "validities": base.VALIDITIES,
        "magnitudes": base.MAGNITUDES,
        "focal_magnitude": base.FOCAL_MAGNITUDE,
        "focal_validity": base.FOCAL_VALIDITY,
        "qualifying_frames": base.QUALIFYING_FRAMES,
        "cue_index": protocol.cue_index,
        "valid_change_index": protocol.valid_change_index,
        "invalid_change_index": protocol.invalid_change_index,
        "control_index": protocol.control_index,
        "active_count": protocol.active_count,
        "required_active_locations": protocol.required_active_locations,
        "active_set_sampling": (
            "random_without_replacement_conditioned_on_cue_invalid_and_control"
            if args.task == "vda_fixed9" else "all_16_active"
        ),
        "region_semantics": "one_carrier_token_per_location",
        "region_tokens": regions,
        "regional_uniform_baseline": 1.0 / 16.0,
        "checkpoint_producer_sha256": producer,
        "evaluation_dependency_sha256": dependency_hashes,
    }
    (args.output_root / "analysis_config.json").write_text(
        json.dumps(base.jsonable(config), indent=2) + "\n", encoding="utf-8"
    )

    psych = compute_psychometrics(model, core, args.psychometric_trials, protocol)
    attention = compute_event_attention(model, core, args.attention_trials, 16, regions, protocol)
    interventions = compute_interventions(
        model, core, args.intervention_trials, feedback, 16, regions, protocol
    )
    base.save_npz(args.output_root / "data" / "psychometrics.npz", psych, metadata)
    base.save_npz(args.output_root / "data" / "event_attention.npz", attention, metadata)
    base.save_npz(args.output_root / "data" / "interventions.npz", interventions, metadata)
    base.write_baseline_table(args.output_root / "tables" / "psychometrics.csv", psych, args.label)
    base.write_intervention_table(
        args.output_root / "tables" / "regional_interventions.csv", interventions, args.label
    )

    plt = base.configure_plots()
    plot_psychometrics(
        plt, psych, args.output_root / "figures" / "valid_invalid_response_rt", args.label, args.task
    )
    base.plot_attention(
        plt, attention, args.output_root / "figures" / "event_attention_maps", args.label, 4, 4
    )
    base.plot_interventions(
        plt, interventions, args.output_root / "figures" / "regional_causal_intervention", args.label
    )

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
                interventions["explicit_response_rate"][disabled, 1]
                - interventions["explicit_response_rate"][natural, 1]
            ),
        },
        "elapsed_seconds": time.time() - started,
    }
    for path in dependency_paths:
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        if base.sha256_file(path) != dependency_hashes[relative]:
            raise RuntimeError(f"evaluation dependency changed during execution: {path}")
    (args.output_root / "SUMMARY.json").write_text(
        json.dumps(base.jsonable(summary), indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "schema_version": 1,
        "status": "complete",
        "model": metadata,
        "config_path": "analysis_config.json",
        "summary_path": "SUMMARY.json",
        "artifact_hashes": {
            str(path.relative_to(args.output_root)).replace("\\", "/"): base.sha256_file(path)
            for path in sorted(args.output_root.rglob("*")) if path.is_file()
        },
    }
    (args.output_root / "MANIFEST.json").write_text(
        json.dumps(base.jsonable(manifest), indent=2) + "\n", encoding="utf-8"
    )
    print(f"[complete] wrote {args.output_root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
