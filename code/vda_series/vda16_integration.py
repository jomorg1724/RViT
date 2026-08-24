"""VDA16 single-checkpoint analysis and manuscript-integration helpers.

Each build admits exactly one routing-family/d128/no-decay checkpoint.  A
second admitted VDA16 shard may be supplied only for a descriptive paired
routing-family figure; this still does not create a replicated factorial
battery.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch


TASK = "vda16"
FEEDBACK = "crossattn1"
WIDTH = 128
MEMORY_DECAY = 1.0
GRID = (4, 4)
IMAGE_SIZE = 100
FINAL_ITERATION = 19999
TRAINING_ITERATIONS = 20000
DISPLAY_NAME = "VDA16 · cross-attention · d128 · no decay · seed 0"
DECODER_LABELS = {
    "colour": "cue value/colour",
    "validity": "displayed validity",
    "change": "change occurrence",
    "change_location": "change location",
    "cued_change": "cued vs uncued change",
}
ROUTING_COLORS = {"affine_ew": "#0072B2", "crossattn1": "#D55E00"}
TASK_COLORS = {"vda1": "#0072B2", "vda4": "#009E73", "vda9": "#CC79A7", "vda16": "#D55E00"}


def configure_feedback(feedback: str) -> None:
    """Select the admitted VDA16 routing family for one isolated build."""
    if feedback not in ROUTING_COLORS:
        raise ValueError(f"unsupported VDA16 routing family: {feedback!r}")
    global FEEDBACK, DISPLAY_NAME
    FEEDBACK = feedback
    routing = "affine element-wise" if feedback == "affine_ew" else "cross-attention"
    DISPLAY_NAME = f"VDA16 · {routing} · d128 · no decay · seed 0"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_metrics(path: str | Path) -> dict[str, np.ndarray]:
    """Read and strictly validate a completed per-iteration training trace."""
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != TRAINING_ITERATIONS:
        raise ValueError(
            f"metrics contain {len(rows)} rows; expected {TRAINING_ITERATIONS}"
        )
    required = {
        "iter",
        "rolling/correct_rate",
        "rolling/mean_return",
        "rollout/correct_rate",
        "env/theta",
        "loss_policy",
        "loss_value",
        "loss_jepa",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"metrics are missing columns: {sorted(missing)}")
    iterations = np.asarray([int(row["iter"]) for row in rows], dtype=np.int64)
    np.testing.assert_array_equal(iterations, np.arange(TRAINING_ITERATIONS))
    columns: dict[str, np.ndarray] = {"iter": iterations}
    for name in rows[0]:
        if name == "iter":
            continue
        values = np.asarray([float(row[name]) for row in rows], dtype=np.float64)
        if not np.isfinite(values).all():
            raise ValueError(f"metrics column {name!r} contains non-finite values")
        columns[name] = values
    return columns


def training_summary(metrics: dict[str, np.ndarray]) -> dict[str, Any]:
    rolling = np.asarray(metrics["rolling/correct_rate"], dtype=float)
    theta = np.asarray(metrics["env/theta"], dtype=float)
    completed_curriculum = bool(theta[-1] <= 8.0 + 1e-9)
    late50 = float(rolling[-50:].mean())
    competence_gated = not completed_curriculum
    return {
        "final_iteration": int(metrics["iter"][-1]),
        "final_rolling_correct": float(rolling[-1]),
        "late50_mean_rolling_correct": late50,
        "best_rolling_correct": float(rolling.max()),
        "initial_theta_degrees": float(theta[0]),
        "final_theta_degrees": float(theta[-1]),
        "minimum_theta_degrees": float(theta.min()),
        "curriculum_floor_degrees": 8.0,
        "curriculum_completed": completed_curriculum,
        "status": "competence_gated" if competence_gated else "admitted",
        "interpretation": (
            "easiest-condition diagnostic; the curriculum never reached its declared floor"
            if competence_gated
            else "terminal checkpoint completed the declared curriculum"
        ),
    }


def _require_mapping_value(mapping: dict[str, Any], key: str, expected: Any, label: str) -> None:
    actual = mapping.get(key)
    if isinstance(expected, float):
        matched = np.isclose(float(actual), expected)
    else:
        matched = actual == expected
    if not matched:
        raise ValueError(f"{label} {key}={actual!r}, expected {expected!r}")


def validate_checkpoint_admission(
    checkpoint_path: str | Path,
    launch_manifest_path: str | Path,
    metrics_path: str | Path,
    *,
    project_root: str | Path,
) -> dict[str, Any]:
    """Fail closed unless the final VDA16 checkpoint matches its training ledger."""
    checkpoint_path = Path(checkpoint_path).resolve()
    launch_manifest_path = Path(launch_manifest_path).resolve()
    metrics_path = Path(metrics_path).resolve()
    project_root = Path(project_root).resolve()
    if checkpoint_path.name != "rvit_paper_vda16_final.pt":
        raise ValueError("only the immutable-named VDA16 final checkpoint is admissible")
    if not checkpoint_path.is_file():
        raise FileNotFoundError(checkpoint_path)
    launch = json.loads(launch_manifest_path.read_text(encoding="utf-8-sig"))
    metrics = load_metrics(metrics_path)
    summary = training_summary(metrics)
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    if not isinstance(payload, dict):
        raise ValueError("checkpoint payload must be a mapping")
    if int(payload.get("checkpoint_schema_version", -1)) < 3:
        raise ValueError("VDA16 final checkpoint must use schema version 3 or later")
    if int(payload.get("iter", -1)) != FINAL_ITERATION:
        raise ValueError(
            f"checkpoint iteration is {payload.get('iter')}, expected {FINAL_ITERATION}"
        )
    _require_mapping_value(payload, "task", TASK, "checkpoint")
    model_kwargs = payload.get("model_kwargs")
    training_args = payload.get("training_args")
    if not isinstance(model_kwargs, dict) or not isinstance(training_args, dict):
        raise ValueError("checkpoint lacks embedded model_kwargs/training_args")
    expected_model = {
        "feedback": FEEDBACK,
        "d_mem": WIDTH,
        "memory_decay": MEMORY_DECAY,
        "conv_frontend": True,
        "grid_rows": GRID[0],
        "grid_cols": GRID[1],
        "image_size": IMAGE_SIZE,
        "seq_len": 7,
    }
    for key, value in expected_model.items():
        _require_mapping_value(model_kwargs, key, value, "checkpoint model_kwargs")
    expected_training = {
        "task": TASK,
        "feedback": FEEDBACK,
        "d_mem": WIDTH,
        "memory_decay": MEMORY_DECAY,
        "patch_grid_rows": GRID[0],
        "patch_grid_cols": GRID[1],
        "curriculum": True,
        "seed": 0,
        "schedule_final_iteration": FINAL_ITERATION,
    }
    for key, value in expected_training.items():
        _require_mapping_value(training_args, key, value, "checkpoint training_args")
    initialization_contract = payload.get("initialization_contract")
    if not isinstance(initialization_contract, dict):
        if training_args.get("init_mode") == "fresh":
            initialization_contract = {"mode": "fresh"}
        else:
            raise ValueError("resumed checkpoint lacks an initialization contract")
    _require_mapping_value(
        initialization_contract, "mode", "fresh", "checkpoint initialization contract"
    )
    if training_args.get("init_mode") not in {"fresh", "resume"}:
        raise ValueError(
            "terminal checkpoint must be fresh or a stateful descendant of a fresh run"
        )
    if training_args.get("init_mode") == "fresh":
        _require_mapping_value(
            training_args, "iters", TRAINING_ITERATIONS, "checkpoint training_args"
        )
    else:
        resume_contract = payload.get("resume_contract")
        if not isinstance(resume_contract, dict):
            raise ValueError("resumed checkpoint lacks a resume contract")
        _require_mapping_value(
            resume_contract,
            "schedule_final_iteration",
            FINAL_ITERATION,
            "checkpoint resume contract",
        )
        if not payload.get("parent_checkpoint_sha256"):
            raise ValueError("resumed checkpoint lacks parent checkpoint identity")
    expected_launch = {
        "task": TASK,
        "feedback": FEEDBACK,
        "memory_decay": MEMORY_DECAY,
        "d_mem": WIDTH,
        "patch_grid_rows": GRID[0],
        "patch_grid_cols": GRID[1],
        "initialization": initialization_contract.get("mode"),
        "curriculum": True,
        "seed": 0,
        "iterations": TRAINING_ITERATIONS,
        "schedule_final_iteration": FINAL_ITERATION,
    }
    for key, value in expected_launch.items():
        _require_mapping_value(launch, key, value, "launch manifest")
    producer = payload.get("producer_sha256")
    if not isinstance(producer, dict) or not producer:
        raise ValueError("checkpoint lacks training-producer hashes")
    producer_checks: list[dict[str, Any]] = []
    for relative, expected_hash in producer.items():
        candidate: Path | None = None
        if relative == "experiment_launcher":
            candidate = Path(str(launch["launcher"]))
        elif relative == "resolved_config":
            candidate = None
        else:
            proposed = project_root / relative
            if proposed.is_file():
                candidate = proposed
        record: dict[str, Any] = {
            "identity": relative,
            "checkpoint_sha256": str(expected_hash),
            "path": str(candidate.resolve()) if candidate is not None else None,
            "status": "not_reconstructable" if candidate is None else "pending",
        }
        if candidate is not None:
            actual = sha256_file(candidate)
            record["current_sha256"] = actual
            record["status"] = "match" if actual == str(expected_hash) else "mismatch"
            if actual != str(expected_hash):
                raise RuntimeError(f"training producer changed since checkpoint: {candidate}")
        producer_checks.append(record)
    checkpoint_hash = sha256_file(checkpoint_path)
    return {
        "schema_version": 1,
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_hash,
        "checkpoint_bytes": checkpoint_path.stat().st_size,
        "checkpoint_schema_version": int(payload["checkpoint_schema_version"]),
        "checkpoint_iteration": int(payload["iter"]),
        "task": TASK,
        "feedback": FEEDBACK,
        "width": WIDTH,
        "memory_decay": MEMORY_DECAY,
        "grid": list(GRID),
        "image_size": IMAGE_SIZE,
        "seed": 0,
        "initialization": "fresh",
        "launch_manifest_path": str(launch_manifest_path),
        "launch_manifest_sha256": sha256_file(launch_manifest_path),
        "metrics_path": str(metrics_path),
        "metrics_sha256": sha256_file(metrics_path),
        "training": summary,
        "terminal_phase": {
            "init_mode": training_args.get("init_mode"),
            "phase_iterations": int(training_args.get("iters", TRAINING_ITERATIONS)),
            "parent_checkpoint_path": payload.get("parent_checkpoint_path"),
            "parent_checkpoint_sha256": payload.get("parent_checkpoint_sha256"),
            "launch_argv": payload.get("launch_argv"),
        },
        "training_runtime": payload.get("runtime_versions"),
        "resume_fidelity": payload.get("resume_fidelity"),
        "replay_buffer_persisted": payload.get("replay_buffer_persisted"),
        "producer_checks": producer_checks,
        "claim_boundary": (
            f"single seed and one {FEEDBACK}/d128/no-decay checkpoint; no width, "
            "decay, seed-population, or causal set-size contrast"
        ),
    }


def qualifying_mean_rt(histogram: np.ndarray) -> np.ndarray:
    """Return conditional mean response frame over qualifying frames 5 and 6."""
    histogram = np.asarray(histogram)
    if histogram.shape[-1] != 8:
        raise ValueError("press histogram must use bins (-1, 0, ..., 6)")
    counts = histogram[..., 6:8].sum(axis=-1)
    weighted = histogram[..., 6] * 5.0 + histogram[..., 7] * 6.0
    return np.divide(
        weighted,
        counts,
        out=np.full(counts.shape, np.nan, dtype=float),
        where=counts > 0,
    )


def _save_figure(figure: plt.Figure, stem: Path) -> dict[str, Path]:
    stem.parent.mkdir(parents=True, exist_ok=True)
    outputs = {suffix: stem.with_suffix(f".{suffix}") for suffix in ("pdf", "svg", "png")}
    figure.savefig(outputs["pdf"], bbox_inches="tight")
    figure.savefig(outputs["svg"], bbox_inches="tight")
    figure.savefig(outputs["png"], dpi=300, bbox_inches="tight")
    plt.close(figure)
    return outputs


def _load_npz(path: str | Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as payload:
        return {name: np.array(payload[name]) for name in payload.files}


def build_training_figure(
    metrics: dict[str, np.ndarray], output_stem: str | Path
) -> dict[str, Path]:
    summary = training_summary(metrics)
    status_label = str(summary["status"]).replace("_", "-")
    iteration = metrics["iter"]
    figure, axes = plt.subplots(2, 2, figsize=(12.5, 7.7), constrained_layout=True)
    axes[0, 0].plot(iteration, metrics["rolling/correct_rate"], color="#0072B2", lw=1.2)
    axes[0, 0].axhline(0.85, color="#D55E00", ls="--", lw=1, label="curriculum threshold")
    axes[0, 0].set(title="A  Rolling correctness", ylabel="P(correct)")
    axes[0, 0].legend(frameon=False)
    axes[0, 1].plot(iteration, metrics["rolling/mean_return"], color="#009E73", lw=1.2)
    axes[0, 1].set(title="B  Rolling return", ylabel="mean return")
    axes[1, 0].plot(iteration, metrics["env/theta"], color="#CC79A7", lw=1.2)
    axes[1, 0].axhline(8.0, color="#555555", ls=":", lw=1, label="declared floor")
    axes[1, 0].set(title="C  Curriculum difficulty", ylabel="maximum change θ (degrees)")
    axes[1, 0].legend(frameon=False)
    axes[1, 1].plot(iteration, metrics["loss_value"], label="value", lw=0.8)
    axes[1, 1].plot(iteration, metrics["loss_jepa"], label="JEPA", lw=0.8)
    axes[1, 1].set(title="D  Training losses", ylabel="loss")
    axes[1, 1].legend(frameon=False)
    for axis in axes.flat:
        axis.set_xlabel("training iteration")
        axis.grid(alpha=0.2)
    figure.suptitle(
        f"{DISPLAY_NAME}\n"
        f"status: {status_label} · final θ={summary['final_theta_degrees']:.1f}° · "
        f"late-50 rolling correctness={summary['late50_mean_rolling_correct']:.3f}",
        fontweight="bold",
    )
    return _save_figure(figure, Path(output_stem))


def build_behavior_timing_figure(
    shard_path: str | Path, output_stem: str | Path
) -> dict[str, Path]:
    data = _load_npz(shard_path)
    magnitudes = data["change_magnitudes"]
    validities = data["displayed_validities"]
    valid_rate = data["psychometric_response_rate_valid"]
    invalid_rate = data["psychometric_response_rate_invalid"]
    valid_rt = qualifying_mean_rt(data["psychometric_press_histogram_valid"])
    invalid_rt = qualifying_mean_rt(data["psychometric_press_histogram_invalid"])
    nochange = data["psychometric_nochange_response_rate"]
    colors = ("#0072B2", "#009E73", "#E69F00", "#CC79A7")
    figure, axes = plt.subplots(2, 2, figsize=(13.0, 8.2), constrained_layout=True, sharex=True)
    for index, validity in enumerate(validities):
        label = f"{int(round(100 * validity))}% displayed"
        axes[0, 0].plot(magnitudes, valid_rate[index], marker="o", ms=3, color=colors[index], label=label)
        axes[0, 1].plot(magnitudes, invalid_rate[index], marker="o", ms=3, color=colors[index], label=label)
        axes[0, 0].axhline(nochange[index], color=colors[index], lw=0.7, ls=":", alpha=0.65)
        axes[0, 1].axhline(nochange[index], color=colors[index], lw=0.7, ls=":", alpha=0.65)
        axes[1, 0].plot(magnitudes, valid_rt[index], marker="o", ms=3, color=colors[index])
        axes[1, 1].plot(magnitudes, invalid_rt[index], marker="o", ms=3, color=colors[index])
    titles = (
        "A  Valid change at S1",
        "B  Forced invalid change at S16",
        "C  Valid-change qualifying RT",
        "D  Forced-invalid qualifying RT",
    )
    for axis, title in zip(axes.flat, titles, strict=True):
        axis.set_title(title, loc="left", fontweight="bold")
        axis.grid(alpha=0.2)
        axis.set_xlabel("orientation change (degrees)")
    axes[0, 0].set_ylabel("P(response at frame 5 or 6)")
    axes[0, 1].set_ylabel("P(response at frame 5 or 6)")
    axes[1, 0].set_ylabel("mean response frame | response")
    axes[1, 1].set_ylabel("mean response frame | response")
    axes[0, 0].legend(frameon=False, fontsize=8)
    figure.suptitle(
        f"{DISPLAY_NAME}\n"
        "Matched trial banks; dotted lines are no-change qualifying-response rates",
        fontweight="bold",
    )
    return _save_figure(figure, Path(output_stem))


def _decoder_chance(data: dict[str, np.ndarray], variable: str) -> float:
    labels = data[f"decoder_sample_label_{variable}"]
    folds = data[f"decoder_fold_id_{variable}"]
    classes = np.unique(labels[folds >= 0])
    return 1.0 / len(classes)


def build_decoder_figure(
    shard_path: str | Path, output_stem: str | Path
) -> dict[str, Path]:
    data = _load_npz(shard_path)
    timesteps = np.arange(7)
    colors = ("#0072B2", "#009E73", "#E69F00", "#CC79A7", "#D55E00")
    figure, axes = plt.subplots(1, 2, figsize=(14.0, 5.4), constrained_layout=True, sharey=True)
    for axis, space, title in (
        (axes[0], "native", "A  Architecture-native recurrent state"),
        (axes[1], "matched128", "B  Foldwise train-only PCA-128"),
    ):
        for color, variable in zip(colors, DECODER_LABELS, strict=True):
            axis.plot(
                timesteps,
                data[f"decoder_{space}_{variable}"],
                marker="o",
                ms=4,
                color=color,
                label=f"{DECODER_LABELS[variable]} (chance {_decoder_chance(data, variable):.3f})",
            )
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xlabel("logical timestep")
        axis.set_xticks(timesteps)
        axis.set_ylim(0.0, 1.02)
        axis.grid(alpha=0.2)
    axes[0].set_ylabel("four-fold balanced accuracy")
    axes[1].legend(
        frameon=True,
        framealpha=0.95,
        facecolor="white",
        edgecolor="none",
        fontsize=8,
        loc="lower right",
    )
    figure.suptitle(
        f"{DISPLAY_NAME}\nN=900 deterministic balanced trials; point estimates from one checkpoint",
        fontweight="bold",
    )
    return _save_figure(figure, Path(output_stem))


def build_clamp_figure(
    shard_path: str | Path, output_stem: str | Path
) -> dict[str, Path]:
    data = _load_npz(shard_path)
    bias = data["clamp_key_logit_biases"]
    valid_rt = qualifying_mean_rt(data["clamp_press_histogram_valid"])
    invalid_rt = qualifying_mean_rt(data["clamp_press_histogram_invalid"])
    figure, axes = plt.subplots(2, 2, figsize=(12.5, 8.0), constrained_layout=True)
    axes[0, 0].plot(bias, data["clamp_hit_rate_valid"], marker="o", label="valid hit rate")
    axes[0, 0].plot(bias, data["clamp_hit_rate_invalid"], marker="s", label="invalid hit rate")
    axes[0, 0].plot(bias, data["clamp_false_alarm_rate"], marker="^", label="false-alarm rate")
    axes[0, 1].plot(bias, data["clamp_dprime_valid"], marker="o", label="valid")
    axes[0, 1].plot(bias, data["clamp_dprime_invalid"], marker="s", label="invalid")
    axes[1, 0].plot(bias, data["clamp_criterion_valid"], marker="o", label="valid")
    axes[1, 0].plot(bias, data["clamp_criterion_invalid"], marker="s", label="invalid")
    axes[1, 1].plot(bias, valid_rt, marker="o", label="valid")
    axes[1, 1].plot(bias, invalid_rt, marker="s", label="invalid")
    titles = (
        "A  Response rates",
        "B  Sensitivity d′",
        "C  Criterion c",
        "D  Qualifying response time",
    )
    ylabels = ("probability", "d′", "c", "mean response frame")
    for axis, title, ylabel in zip(axes.flat, titles, ylabels, strict=True):
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xlabel("additive cued-key logit bias")
        axis.set_ylabel(ylabel)
        axis.axvline(0.0, color="#555555", lw=0.8, ls=":")
        axis.grid(alpha=0.2)
        axis.legend(frameon=False)
    figure.suptitle(
        f"{DISPLAY_NAME}\n"
        "Clamp begins at frame 5; image and corresponding memory keys receive the same logit bias",
        fontweight="bold",
    )
    return _save_figure(figure, Path(output_stem))


def compute_achieved_clamp_attention(
    checkpoint_path: str | Path,
    output_path: str | Path,
    *,
    expected_checkpoint_sha256: str,
    device: str,
    source_hashes: dict[str, str],
) -> Path:
    """Measure achieved cued-key mass for every registered clamp dose.

    The matched-width intervention defines dose in logit space.  This companion
    cache records the attention allocation actually achieved at every timestep,
    condition, and trial so equal nominal doses are not mistaken for equal
    attention mass.
    """
    from vda_sweep import matched_width as matched
    from vda_sweep import vda_core as core

    checkpoint_path = Path(checkpoint_path).resolve()
    output_path = Path(output_path)
    checkpoint_hash = sha256_file(checkpoint_path)
    if checkpoint_hash != expected_checkpoint_sha256:
        raise RuntimeError("checkpoint changed before achieved-attention computation")
    core.DEVICE = device
    model, iteration = core.load(
        TASK,
        FEEDBACK,
        WIDTH,
        checkpoint_path=checkpoint_path,
        expected_checkpoint_sha256=expected_checkpoint_sha256,
        require_iteration=FINAL_ITERATION,
    )
    cue, invalid = 0, 15
    validity, magnitude = 0.75, 18.0
    videos = {
        "valid": core.make_video_batch(
            TASK,
            cue,
            validity,
            "red",
            1,
            cue,
            magnitude,
            B=matched.CLAMP_TRIALS,
            seed=matched.CLAMP_SEED,
        ),
        "invalid": core.make_video_batch(
            TASK,
            cue,
            validity,
            "red",
            1,
            invalid,
            magnitude,
            B=matched.CLAMP_TRIALS,
            seed=matched.CLAMP_SEED,
        ),
        "nochange": core.make_video_batch(
            TASK,
            cue,
            validity,
            "red",
            0,
            -1,
            magnitude,
            B=matched.CLAMP_TRIALS,
            seed=matched.CLAMP_SEED + 1,
        ),
    }
    condition_names = tuple(videos)
    trial_mass = np.zeros(
        (
            len(condition_names),
            len(matched.CLAMP_DOSE_PARAMETERS),
            7,
            matched.CLAMP_TRIALS,
        ),
        dtype=np.float32,
    )
    keys = model.n_tokens if FEEDBACK == "affine_ew" else 2 * model.n_tokens
    cued_keys = [cue] if FEEDBACK == "affine_ew" else [cue, model.n_tokens + cue]
    for condition_index, condition in enumerate(condition_names):
        batch = videos[condition]
        for dose_index, dose in enumerate(matched.CLAMP_DOSE_PARAMETERS):
            clamp = core.clamp_alpha(
                keys,
                model.n_tokens,
                cue,
                dose,
                scale=matched.CLAMP_LOGIT_SCALE,
            )
            states = model.init_states(matched.CLAMP_TRIALS, device=device)
            for timestep in range(7):
                active_clamp = clamp if timestep >= 5 else None
                with torch.no_grad():
                    step = model.rl_step(
                        batch[:, timestep],
                        states,
                        return_attn=True,
                        attn_clamp=active_clamp,
                    )
                states = step["new_states"]
                raw = step["attn"][0].detach()
                mass = raw[:, :, cued_keys].sum(dim=-1).mean(dim=-1)
                trial_mass[condition_index, dose_index, timestep] = (
                    mass.cpu().numpy().astype(np.float32)
                )
    if sha256_file(checkpoint_path) != checkpoint_hash:
        raise RuntimeError("checkpoint changed during achieved-attention computation")
    metadata = {
        "schema_version": 1,
        "task": TASK,
        "feedback": FEEDBACK,
        "width": WIDTH,
        "memory_decay": MEMORY_DECAY,
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_hash,
        "checkpoint_iteration": iteration,
        "device": device,
        "runtime": {
            "python": platform.python_version(),
            "python_executable": str(Path(sys.executable).resolve()),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "platform": platform.platform(),
        },
        "source_hashes": dict(source_hashes),
        "conditions": list(condition_names),
        "displayed_validity": validity,
        "change_magnitude_degrees": magnitude,
        "cue_index": cue,
        "invalid_change_index": invalid,
        "trials_per_condition_and_dose": matched.CLAMP_TRIALS,
        "clamp_from_frame": 5,
        "attention_mass_definition": (
            "S1 self-key mass averaged over query tokens"
            if FEEDBACK == "affine_ew"
            else "sum of image-key and corresponding recurrent-memory-key mass for S1, "
            "averaged over query tokens"
        ),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
        conditions=np.asarray(condition_names),
        clamp_dose_parameters=np.asarray(matched.CLAMP_DOSE_PARAMETERS, dtype=float),
        clamp_key_logit_biases=np.asarray(matched.CLAMP_KEY_LOGIT_BIASES, dtype=float),
        achieved_cued_attention_mass_trials=trial_mass,
        achieved_cued_attention_mass_mean=trial_mass.mean(axis=-1),
        achieved_cued_attention_mass_sem=trial_mass.std(axis=-1, ddof=1)
        / np.sqrt(matched.CLAMP_TRIALS),
    )
    validate_achieved_clamp_attention(
        output_path,
        expected_checkpoint_sha256=expected_checkpoint_sha256,
        expected_device=device,
        expected_source_hashes=source_hashes,
    )
    return output_path


def validate_achieved_clamp_attention(
    path: str | Path,
    *,
    expected_checkpoint_sha256: str,
    expected_device: str | None = None,
    expected_cache_sha256: str | None = None,
    expected_source_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    cache_hash = sha256_file(path)
    if expected_cache_sha256 is not None and cache_hash != expected_cache_sha256:
        raise ValueError("achieved-attention cache SHA-256 mismatch")
    with np.load(path, allow_pickle=False) as payload:
        expected_keys = {
            "metadata_json",
            "conditions",
            "clamp_dose_parameters",
            "clamp_key_logit_biases",
            "achieved_cued_attention_mass_trials",
            "achieved_cued_attention_mass_mean",
            "achieved_cued_attention_mass_sem",
        }
        if set(payload.files) != expected_keys:
            raise ValueError("achieved-attention cache key inventory mismatch")
        metadata = json.loads(str(payload["metadata_json"].item()))
        if metadata.get("checkpoint_sha256") != expected_checkpoint_sha256:
            raise ValueError("achieved-attention cache checkpoint hash mismatch")
        if int(metadata.get("checkpoint_iteration", -1)) != FINAL_ITERATION:
            raise ValueError("achieved-attention cache is not terminal")
        expected_identity = {
            "task": TASK,
            "feedback": FEEDBACK,
            "width": WIDTH,
            "memory_decay": MEMORY_DECAY,
        }
        for field, expected in expected_identity.items():
            if metadata.get(field) != expected:
                raise ValueError(
                    f"achieved-attention metadata {field} mismatch"
                )
        if expected_device is not None and metadata.get("device") != expected_device:
            raise ValueError("achieved-attention cache device mismatch")
        runtime = metadata.get("runtime")
        if not isinstance(runtime, dict) or not {
            "python",
            "python_executable",
            "numpy",
            "torch",
            "platform",
        }.issubset(runtime):
            raise ValueError("achieved-attention cache runtime metadata is incomplete")
        if (
            expected_source_hashes is not None
            and metadata.get("source_hashes") != expected_source_hashes
        ):
            raise ValueError("achieved-attention cache source hashes mismatch")
        conditions = np.asarray(payload["conditions"])
        if conditions.tolist() != ["valid", "invalid", "nochange"]:
            raise ValueError("achieved-attention condition order mismatch")
        trials = np.asarray(payload["achieved_cued_attention_mass_trials"], dtype=float)
        means = np.asarray(payload["achieved_cued_attention_mass_mean"], dtype=float)
        sem = np.asarray(payload["achieved_cued_attention_mass_sem"], dtype=float)
        expected_shape = (3, 5, 7, 250)
        if trials.shape != expected_shape or means.shape != expected_shape[:-1]:
            raise ValueError("achieved-attention array shape mismatch")
        if sem.shape != expected_shape[:-1]:
            raise ValueError("achieved-attention SEM shape mismatch")
        if (
            not np.isfinite(trials).all()
            or not np.isfinite(means).all()
            or not np.isfinite(sem).all()
            or np.any((trials < 0.0) | (trials > 1.0))
        ):
            raise ValueError("achieved-attention values are invalid")
        np.testing.assert_allclose(means, trials.mean(axis=-1), atol=1e-7, rtol=0.0)
        expected_sem = trials.std(axis=-1, ddof=1) / np.sqrt(250)
        np.testing.assert_allclose(sem, expected_sem, atol=1e-7, rtol=0.0)
        dose = np.asarray(payload["clamp_dose_parameters"], dtype=float)
        bias = np.asarray(payload["clamp_key_logit_biases"], dtype=float)
        if dose.shape != (5,) or bias.shape != (5,):
            raise ValueError("achieved-attention clamp-axis shape mismatch")
        np.testing.assert_allclose(dose, (0.0, 0.25, 0.5, 0.75, 1.0))
        np.testing.assert_allclose(bias, (-6.0, -3.0, 0.0, 3.0, 6.0))
    return metadata


def build_achieved_clamp_attention_figure(
    cache_path: str | Path,
    output_stem: str | Path,
    *,
    expected_checkpoint_sha256: str,
    expected_cache_sha256: str,
    expected_device: str,
    expected_source_hashes: dict[str, str],
) -> dict[str, Path]:
    validate_achieved_clamp_attention(
        cache_path,
        expected_checkpoint_sha256=expected_checkpoint_sha256,
        expected_cache_sha256=expected_cache_sha256,
        expected_device=expected_device,
        expected_source_hashes=expected_source_hashes,
    )
    with np.load(cache_path, allow_pickle=False) as payload:
        biases = np.asarray(payload["clamp_key_logit_biases"], dtype=float)
        means = np.asarray(payload["achieved_cued_attention_mass_mean"], dtype=float)
        sem = np.asarray(payload["achieved_cued_attention_mass_sem"], dtype=float)
        conditions = [str(value) for value in payload["conditions"]]
    figure, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), constrained_layout=True, sharey=True)
    colors = {"valid": "#0072B2", "invalid": "#D55E00", "nochange": "#009E73"}
    for axis, timestep in zip(axes, (5, 6), strict=True):
        for condition_index, condition in enumerate(conditions):
            axis.errorbar(
                biases,
                means[condition_index, :, timestep],
                yerr=sem[condition_index, :, timestep],
                marker="o",
                capsize=2,
                color=colors[condition],
                label=condition,
            )
        axis.set_title(f"{'A' if timestep == 5 else 'B'}  Logical frame {timestep}", loc="left", fontweight="bold")
        axis.set_xlabel("additive cued-key logit bias")
        axis.set_ylim(-0.02, 1.02)
        axis.axvline(0.0, color="#555555", lw=0.8, ls=":")
        axis.grid(alpha=0.2)
    axes[0].set_ylabel("achieved cued-location attention mass")
    axes[1].legend(frameon=False)
    figure.suptitle(
        f"{DISPLAY_NAME}\nAchieved cued-key mass (mean ± trial-level SEM)",
        fontweight="bold",
    )
    outputs = _save_figure(figure, Path(output_stem))
    if sha256_file(cache_path) != expected_cache_sha256:
        raise RuntimeError("achieved-attention cache changed while rendering")
    return outputs


def build_manuscript_summary_figure(
    shard_path: str | Path,
    output_stem: str | Path,
    *,
    competence_status: str,
) -> dict[str, Path]:
    data = _load_npz(shard_path)
    competence_label = competence_status.replace("_", "-")
    validity_index = int(np.flatnonzero(np.isclose(data["displayed_validities"], 0.75))[0])
    figure, axes = plt.subplots(2, 2, figsize=(13.0, 8.5), constrained_layout=True)
    axes[0, 0].plot(
        data["change_magnitudes"],
        data["psychometric_response_rate_valid"][validity_index],
        marker="o",
        label="valid S1",
    )
    axes[0, 0].plot(
        data["change_magnitudes"],
        data["psychometric_response_rate_invalid"][validity_index],
        marker="s",
        label="forced invalid S16",
    )
    axes[0, 0].axhline(
        data["psychometric_nochange_response_rate"][validity_index],
        color="#555555",
        ls=":",
        label="no-change",
    )
    for variable, color in zip(
        ("change", "change_location", "cued_change"),
        ("#0072B2", "#009E73", "#D55E00"),
        strict=True,
    ):
        axes[0, 1].plot(
            np.arange(7),
            data[f"decoder_matched128_{variable}"],
            marker="o",
            color=color,
            label=DECODER_LABELS[variable],
        )
    axes[1, 0].plot(data["clamp_key_logit_biases"], data["clamp_dprime_valid"], marker="o", label="valid")
    axes[1, 0].plot(data["clamp_key_logit_biases"], data["clamp_dprime_invalid"], marker="s", label="invalid")
    axes[1, 1].plot(data["clamp_key_logit_biases"], data["clamp_criterion_valid"], marker="o", label="valid")
    axes[1, 1].plot(data["clamp_key_logit_biases"], data["clamp_criterion_invalid"], marker="s", label="invalid")
    titles = (
        "A  Behavior at displayed validity 0.75",
        "B  PCA-128 memory decoding",
        "C  Cued-key clamp: sensitivity",
        "D  Cued-key clamp: criterion",
    )
    xlabels = (
        "orientation change (degrees)",
        "logical timestep",
        "additive cued-key logit bias",
        "additive cued-key logit bias",
    )
    ylabels = ("response probability", "balanced accuracy", "d′", "c")
    for axis, title, xlabel, ylabel in zip(axes.flat, titles, xlabels, ylabels, strict=True):
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.2)
        axis.legend(frameon=False, fontsize=8)
    figure.suptitle(
        f"{DISPLAY_NAME}\nstatus: {competence_label} · single-checkpoint descriptive evidence",
        fontweight="bold",
    )
    figure.text(
        0.5,
        -0.01,
        "No d256 VDA16, decay contrast, or training-seed uncertainty is available.",
        ha="center",
        fontsize=9,
        color="#7A1F1F",
    )
    return _save_figure(figure, Path(output_stem))


def _historical_shard(
    historical_root: Path, task: str, feedback: str
) -> dict[str, np.ndarray]:
    path = historical_root / f"{task}_{feedback}_d128.npz"
    if not path.is_file():
        raise FileNotFoundError(path)
    return _load_npz(path)


def build_method_comparison_figure(
    vda16_shard_path: str | Path,
    historical_root: str | Path,
    output_stem: str | Path,
    *,
    vda16_competence_status: str,
    vda16_final_theta: float,
    vda16_feedback: str = "crossattn1",
    companion_vda16_shard_path: str | Path | None = None,
    companion_vda16_feedback: str | None = None,
    companion_competence_status: str | None = None,
    companion_final_theta: float | None = None,
) -> dict[str, Path]:
    """Add a visually gated VDA16 point to the descriptive d128 method matrix."""
    competence_label = vda16_competence_status.replace("_", "-")
    historical_root = Path(historical_root)
    cells: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    for task in ("vda1", "vda4", "vda9"):
        for feedback in ("affine_ew", "crossattn1"):
            cells[(task, feedback)] = _historical_shard(historical_root, task, feedback)
    cells[("vda16", vda16_feedback)] = _load_npz(vda16_shard_path)
    vda16_annotations = {
        vda16_feedback: (vda16_competence_status, float(vda16_final_theta))
    }
    if companion_vda16_shard_path is not None:
        if companion_vda16_feedback not in ROUTING_COLORS:
            raise ValueError("companion VDA16 feedback is missing or unsupported")
        cells[("vda16", companion_vda16_feedback)] = _load_npz(
            companion_vda16_shard_path
        )
        vda16_annotations[companion_vda16_feedback] = (
            companion_competence_status or "competence_gated",
            float(companion_final_theta) if companion_final_theta is not None else np.nan,
        )
    tasks = ("vda1", "vda4", "vda9", "vda16")
    set_sizes = np.asarray([1, 4, 9, 16], dtype=float)
    figure, axes = plt.subplots(2, 2, figsize=(12.8, 8.2))
    for feedback in ("affine_ew", "crossattn1"):
        values: dict[str, list[float]] = {
            "cue_benefit": [],
            "change_decode": [],
            "cued_decode": [],
            "false_alarm": [],
        }
        for task in tasks:
            data = cells.get((task, feedback))
            if data is None:
                for series in values.values():
                    series.append(np.nan)
                continue
            validities = data["displayed_validities"]
            magnitudes = data["change_magnitudes"]
            vi = int(np.flatnonzero(np.isclose(validities, 0.75))[0])
            mi = int(np.argmin(np.abs(magnitudes - 18.0)))
            invalid = float(data["psychometric_response_rate_invalid"][vi, mi])
            valid = float(data["psychometric_response_rate_valid"][vi, mi])
            values["cue_benefit"].append(valid - invalid if np.isfinite(invalid) else np.nan)
            values["change_decode"].append(float(data["decoder_matched128_change"][-1]))
            values["cued_decode"].append(float(data["decoder_matched128_cued_change"][-1]))
            values["false_alarm"].append(
                float(data["psychometric_nochange_response_rate"][vi])
            )
        label = "affine" if feedback == "affine_ew" else "cross-attention"
        style = {
            "color": ROUTING_COLORS[feedback],
            "marker": "o" if feedback == "affine_ew" else "s",
            "lw": 1.8,
            "label": label,
        }
        for axis, key in zip(
            axes.flat,
            ("cue_benefit", "change_decode", "cued_decode", "false_alarm"),
            strict=True,
        ):
            # Only the historical VDA1/4/9 cells form a connected sequence.
            # VDA16 remains unconnected because it did not leave theta=65.
            axis.plot(set_sizes[:3], values[key][:3], **style)
            if np.isfinite(values[key][3]):
                status, _theta = vda16_annotations[feedback]
                marker = "o" if feedback == "affine_ew" else "s"
                axis.scatter(
                    [set_sizes[3]],
                    [values[key][3]],
                    s=72,
                    marker=marker,
                    facecolors="none",
                    edgecolors=ROUTING_COLORS[feedback],
                    linewidths=1.8,
                    label=f"VDA16 {label} ({status.replace('_', '-')})",
                    zorder=5,
                )
    titles = (
        "A  Valid − invalid response rate\n(V=.75, nearest Δ=18°)",
        "B  Final-timestep change decoder",
        "C  Final-timestep cued-change decoder",
        "D  No-change qualifying-response rate\n(V=.75; no intervention)",
    )
    ylabels = (
        "Δ response probability",
        "balanced accuracy",
        "balanced accuracy",
        "false-alarm probability",
    )
    for axis, title, ylabel in zip(axes.flat, titles, ylabels, strict=True):
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_xlabel("active locations (task/display geometry also changes)")
        axis.set_ylabel(ylabel)
        axis.set_xticks(set_sizes, [1, 4, 9, 16])
        axis.grid(alpha=0.2)
        axis.legend(frameon=False)
    for axis in (axes[0, 0], axes[1, 0]):
        axis.text(
            1,
            0.02,
            "undefined",
            rotation=90,
            va="bottom",
            fontsize=8,
            transform=axis.get_xaxis_transform(),
        )
    missing = [feedback for feedback in ROUTING_COLORS if feedback not in vda16_annotations]
    if missing:
        missing_label = "affine" if missing[0] == "affine_ew" else "cross-attention"
        for axis in axes.flat:
            axis.annotate(
                f"VDA16 {missing_label} unavailable",
                xy=(16, 0),
                xycoords=("data", "axes fraction"),
                xytext=(-5, 6),
                textcoords="offset points",
                ha="right",
                fontsize=8,
                color=ROUTING_COLORS[missing[0]],
            )
    theta_summary = ", ".join(
        f"{'affine' if feedback == 'affine_ew' else 'cross-attention'} θ={theta:.1f}°"
        for feedback, (_status, theta) in vda16_annotations.items()
    )
    figure.suptitle(
        "Descriptive d128 VDA task sequence with admitted VDA16 routing checkpoints\n"
        f"Open VDA16 markers are unconnected and competence-gated ({theta_summary})",
        fontweight="bold",
    )
    figure.text(
        0.5,
        -0.02,
        "Historical and VDA16 cells use separately frozen executable/runtime lineages; "
        "VDA2 lacks a compatible modern shard; one checkpoint per cell; "
        "not a controlled, replicated, or causal set-size effect.",
        ha="center",
        fontsize=8.5,
        color="#4C566A",
    )
    figure.subplots_adjust(
        left=0.08,
        right=0.97,
        bottom=0.16,
        top=0.82,
        wspace=0.28,
        hspace=0.42,
    )
    return _save_figure(figure, Path(output_stem))


def artifact_record(path: str | Path, root: str | Path) -> dict[str, Any]:
    path, root = Path(path).resolve(), Path(root).resolve()
    return {
        "path": str(path.relative_to(root)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
