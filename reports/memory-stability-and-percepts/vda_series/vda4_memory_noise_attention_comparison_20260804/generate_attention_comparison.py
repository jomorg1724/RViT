"""Generate a source-separated VDA4 clean-versus-memory-noise map comparison.

This producer implements PROTOCOL_AMENDMENT.md.  It is intentionally separate
from the frozen terminal-pair evaluator because the noisy checkpoint was
interrupted at iteration 15,999 and the clean checkpoint is historical.  Its
outputs are descriptive checkpoint diagnostics, not the registered paired
experiment and not causal mechanism evidence.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any

os.environ["RVIT_DEVICE"] = "cpu"

import numpy as np

# Checkpoints produced under newer NumPy versions may reference numpy._core.
# NumPy 1.23 exposes the same objects through numpy.core.
sys.modules.setdefault("numpy._core", np.core)
sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vda_sweep import vda_core as core
from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
    evaluate_paired_v1 as evalmod,
)


OUTPUT_ROOT = HERE / "maps_v2"
PROTOCOL = HERE / "PROTOCOL_AMENDMENT.md"
TRIALS = 96
T = 7
VALIDITIES = np.asarray([0.25, 0.50, 0.75, 1.00], dtype=np.float64)
CONDITIONS = ("historical_clean", "interrupted_noisy")
SOURCES = ("current_image_keys", "previous_hidden_state_keys")
SOURCE_SHORT = ("visual", "memory")

CLEAN_CHECKPOINT = Path(
    r"C:\Users\jomor\Documents\RViT_runs\vda4_crossattn1_d128_nodecay_seed0_pod\rvit_paper_vda4_final.pt"
)
NOISY_CHECKPOINT = Path(
    r"C:\Users\jomor\Documents\RViT_runs\vda4_memory_noise_noise0p5_interrupted_snapshot_20260804T055300Z\run\rvit_plus_rl_latest.pt"
)
CLEAN_SHA256 = "ea671f9758551e06b39ef19c06e85e888ce3ee74dda8a534c1532251a69ee4ca"
NOISY_SHA256 = "be5e67f907e6603229c48ee54cc41e7075d62a4514f61f0f9da0d2e56d1de967"
CLEAN_ITERATION = 19999
NOISY_ITERATION = 15999

EVIDENCE_LABEL = (
    "Exploratory held-out routing comparison: historical terminal clean reference "
    "versus interrupted noise-trained checkpoint. Training duration, provenance, "
    "and initialization pairing are not matched."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def stable_seed(*parts: Any, bits: int = 63) -> int:
    material = "|".join(str(part) for part in parts).encode("utf-8")
    value = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return value & ((1 << bits) - 1)


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_model(model: Any, *, expected_train_noise: float) -> dict[str, Any]:
    encoder = model.encoder
    contract = {
        "task": "vda4",
        "feedback": str(encoder.feedback),
        "cell": str(encoder.cell),
        "two_lstm": bool(encoder.two_lstm),
        "d_mem": int(encoder.d_mem),
        "n_tokens": int(model.n_tokens),
        "grid_rows": 2,
        "grid_cols": 2,
        "memory_decay": float(encoder.lstm.memory_decay),
        "memory_noise_std": float(encoder.lstm.memory_noise_std),
        "seq_len": int(model.seq_len),
    }
    expected = {
        "feedback": "crossattn1",
        "cell": "xlstm",
        "two_lstm": False,
        "d_mem": 128,
        "n_tokens": 4,
        "grid_rows": 2,
        "grid_cols": 2,
        "memory_decay": 1.0,
        "memory_noise_std": float(expected_train_noise),
        "seq_len": 7,
    }
    for key, value in expected.items():
        if contract[key] != value:
            raise RuntimeError(f"model contract mismatch for {key}: {contract[key]!r} != {value!r}")
    return contract


def load_models() -> tuple[dict[str, Any], dict[str, Any]]:
    if sha256_file(CLEAN_CHECKPOINT) != CLEAN_SHA256:
        raise RuntimeError("historical clean checkpoint hash mismatch")
    if sha256_file(NOISY_CHECKPOINT) != NOISY_SHA256:
        raise RuntimeError("interrupted noisy checkpoint hash mismatch")
    clean, clean_iter = core.load(
        "vda4",
        "crossattn1",
        128,
        checkpoint_path=CLEAN_CHECKPOINT,
        expected_checkpoint_sha256=CLEAN_SHA256,
        require_iteration=CLEAN_ITERATION,
        validate_metadata=True,
    )
    noisy, noisy_iter = core.load(
        "vda4",
        "crossattn1",
        128,
        checkpoint_path=NOISY_CHECKPOINT,
        expected_checkpoint_sha256=NOISY_SHA256,
        require_iteration=NOISY_ITERATION,
        validate_metadata=True,
    )
    contracts = {
        "historical_clean": validate_model(clean, expected_train_noise=0.0),
        "interrupted_noisy": validate_model(noisy, expected_train_noise=0.5),
    }
    clean_shapes = {k: tuple(v.shape) for k, v in clean.state_dict().items()}
    noisy_shapes = {k: tuple(v.shape) for k, v in noisy.state_dict().items()}
    if clean_shapes != noisy_shapes:
        raise RuntimeError("clean/noisy model state keys or tensor shapes differ")
    identities = {
        "historical_clean": {
            "path": str(CLEAN_CHECKPOINT.resolve()),
            "sha256": CLEAN_SHA256,
            "iteration": int(clean_iter),
            "training_memory_noise_std": 0.0,
            "evaluation_memory_noise_std": 0.0,
            "contract": contracts["historical_clean"],
        },
        "interrupted_noisy": {
            "path": str(NOISY_CHECKPOINT.resolve()),
            "sha256": NOISY_SHA256,
            "iteration": int(noisy_iter),
            "training_memory_noise_std": 0.5,
            "evaluation_memory_noise_std": 0.5,
            "contract": contracts["interrupted_noisy"],
        },
        "architecture_state_shape_sha256": sha256_bytes(
            json.dumps(clean_shapes, sort_keys=True).encode("utf-8")
        ),
    }
    return {"historical_clean": clean, "interrupted_noisy": noisy}, identities


def make_bank(
    *,
    bank_id: str,
    displayed_validity: float,
    changed: int,
    change_index: int,
    magnitude: float,
    sensory_seed: int,
    policy_uniforms: np.ndarray,
    memory_noise_seed: int,
) -> tuple[evalmod.TrialBank, dict[str, Any]]:
    videos = core.make_video_batch(
        "vda4",
        0,
        float(displayed_validity),
        "red",
        int(changed),
        int(change_index),
        float(magnitude),
        B=TRIALS,
        seed=int(sensory_seed),
    )
    video_cpu = videos.detach().cpu().numpy()
    record = {
        "bank_id": bank_id,
        "trials": TRIALS,
        "cue_index": 0,
        "displayed_validity": float(displayed_validity),
        "changed": int(changed),
        "change_index": int(change_index),
        "magnitude_degrees": float(magnitude),
        "sensory_seed": int(sensory_seed),
        "policy_uniform_seeded_externally": True,
        "memory_noise_seed": int(memory_noise_seed),
        "video_shape": list(video_cpu.shape),
        "video_sha256": sha256_bytes(video_cpu.tobytes(order="C")),
        "policy_uniform_shape": list(policy_uniforms.shape),
        "policy_uniform_sha256": sha256_bytes(policy_uniforms.tobytes(order="C")),
    }
    return (
        evalmod.TrialBank(
            bank_id=bank_id,
            videos=videos,
            policy_uniforms=policy_uniforms,
            memory_noise_seed=int(memory_noise_seed),
            registry=record,
        ),
        record,
    )


def run_pair(models: dict[str, Any], bank: evalmod.TrialBank) -> tuple[dict[str, Any], dict[str, Any]]:
    clean = evalmod.rollout_sampled(
        models["historical_clean"],
        bank,
        eval_noise_std=0.0,
        return_attention=True,
    )
    noisy = evalmod.rollout_sampled(
        models["interrupted_noisy"],
        bank,
        eval_noise_std=0.5,
        return_attention=True,
    )
    if noisy["memory_noise_draw_calls"] != T:
        raise RuntimeError("noisy rollout did not inject memory noise at every recurrent update")
    return clean, noisy


def split_and_score(raw: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    visual, memory = evalmod.split_source_attention(raw)
    visual_scores = evalmod.column_averaged_patch_scores(visual)
    memory_scores = evalmod.column_averaged_patch_scores(memory)
    if not np.allclose(visual_scores.sum(-1) + memory_scores.sum(-1), 1.0, atol=2e-5):
        raise RuntimeError("source-separated column scores do not preserve joint-softmax mass")
    return visual, memory, visual_scores, memory_scores


def metric_bundle(scores: np.ndarray, *, cue_index: int, target_index: int) -> dict[str, np.ndarray]:
    scores = np.asarray(scores, dtype=np.float64)
    share = scores.sum(axis=-1)
    if np.any(share <= 0.0):
        raise RuntimeError("non-positive source share")
    conditional = scores / share[..., None]
    entropy = -(conditional * np.log(np.clip(conditional, 1e-12, 1.0))).sum(axis=-1)
    distractors = [i for i in range(4) if i != target_index]
    return {
        "source_share": share,
        "cue_raw": scores[..., cue_index],
        "cue_conditional": conditional[..., cue_index],
        "target_raw": scores[..., target_index],
        "target_conditional": conditional[..., target_index],
        "target_selectivity": conditional[..., target_index]
        - conditional[..., distractors].mean(axis=-1),
        "max_raw_patch": scores.max(axis=-1),
        "max_conditional_patch": conditional.max(axis=-1),
        "normalized_entropy": entropy / math.log(4.0),
        "effective_locations": np.exp(entropy),
    }


def mean_sem(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=np.float64)
    return values.mean(axis=0), values.std(axis=0, ddof=1) / math.sqrt(values.shape[0])


def save_figure(fig: Any, root: Path, stem: str) -> None:
    figure_dir = root / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_dir / f"{stem}.png", dpi=200, bbox_inches="tight")
    fig.savefig(figure_dir / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def outline_locations(ax: Any, *, target: bool) -> None:
    ax.add_patch(Rectangle((-0.48, -0.48), 0.96, 0.96, fill=False, lw=1.4, ec="#d62728"))
    if target:
        ax.add_patch(Rectangle((0.52, 0.52), 0.96, 0.96, fill=False, lw=1.4, ec="#00a6c8"))


def heatmap(ax: Any, values: np.ndarray, *, cmap: str, vmin: float, vmax: float, target: bool) -> Any:
    image = ax.imshow(np.asarray(values).reshape(2, 2), cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
    outline_locations(ax, target=target)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_linewidth(0.35)
        spine.set_color("#777777")
    return image


def plot_cue_plate(cue_mean: np.ndarray, root: Path, vmax: float) -> None:
    # cue_mean: condition, validity, source, time, patch
    fig, axes = plt.subplots(8, 14, figsize=(21.0, 11.5), constrained_layout=False)
    last = None
    for ci, condition in enumerate(CONDITIONS):
        for si, source in enumerate(SOURCES):
            for vi, validity in enumerate(VALIDITIES):
                for ti in range(T):
                    row = ci * 4 + vi
                    col = si * 7 + ti
                    ax = axes[row, col]
                    last = heatmap(
                        ax,
                        cue_mean[ci, vi, si, ti],
                        cmap="viridis",
                        vmin=0.0,
                        vmax=vmax,
                        target=False,
                    )
                    if vi == 0 and ci in (0, 1):
                        ax.set_title(f"t{ti}", fontsize=8)
                    if ti == 0 and si == 0:
                        prefix = "Clean" if ci == 0 else "Noisy"
                        ax.set_ylabel(f"{prefix} · {int(validity * 100)}%", fontsize=8)
    fig.subplots_adjust(left=0.075, right=0.935, top=0.88, bottom=0.075, wspace=0.08, hspace=0.18)
    fig.text(0.285, 0.915, "Current-image-key routing", ha="center", fontsize=11)
    fig.text(0.725, 0.915, "Previous-hidden-state-key routing", ha="center", fontsize=11)
    fig.text(0.02, 0.68, "Historical clean final", rotation=90, va="center", fontsize=10)
    fig.text(0.02, 0.29, "Interrupted noisy checkpoint", rotation=90, va="center", fontsize=10)
    if last is not None:
        color_ax = fig.add_axes([0.952, 0.19, 0.012, 0.59])
        fig.colorbar(last, cax=color_ax, label="Raw mean attention per key")
    fig.suptitle("No-change cue-proportion routing maps · red outline = S1 cue", fontsize=13, y=0.97)
    fig.text(0.5, 0.018, EVIDENCE_LABEL, ha="center", va="bottom", fontsize=8)
    save_figure(fig, root, "cue_maps")


def plot_cue_difference(cue_mean: np.ndarray, root: Path, diff_abs: float) -> None:
    difference = cue_mean[1] - cue_mean[0]  # validity, source, time, patch
    fig, axes = plt.subplots(4, 14, figsize=(21.0, 6.2), constrained_layout=False)
    last = None
    for si, source in enumerate(SOURCES):
        for vi, validity in enumerate(VALIDITIES):
            for ti in range(T):
                ax = axes[vi, si * 7 + ti]
                last = heatmap(
                    ax,
                    difference[vi, si, ti],
                    cmap="coolwarm",
                    vmin=-diff_abs,
                    vmax=diff_abs,
                    target=False,
                )
                if vi == 0:
                    ax.set_title(f"t{ti}", fontsize=8)
                if ti == 0 and si == 0:
                    ax.set_ylabel(f"{int(validity * 100)}%", fontsize=8)
    fig.subplots_adjust(left=0.055, right=0.935, top=0.82, bottom=0.12, wspace=0.08, hspace=0.18)
    fig.text(0.28, 0.87, "Noisy − clean · current-image keys", ha="center", fontsize=11)
    fig.text(0.72, 0.87, "Noisy − clean · previous-hidden-state keys", ha="center", fontsize=11)
    if last is not None:
        color_ax = fig.add_axes([0.952, 0.2, 0.012, 0.52])
        fig.colorbar(last, cax=color_ax, label="Difference in raw mean attention")
    fig.suptitle("Cue-proportion difference maps (sources never fused)", fontsize=13, y=0.97)
    fig.text(0.5, 0.025, EVIDENCE_LABEL, ha="center", va="bottom", fontsize=8)
    save_figure(fig, root, "cue_diff")


def plot_invalid_plate(invalid_mean: np.ndarray, root: Path, vmax: float) -> None:
    # invalid_mean: condition, source, time, patch
    fig = plt.figure(figsize=(16.5, 8.8), constrained_layout=True)
    grid = fig.add_gridspec(4, 7, wspace=0.06, hspace=0.14)
    last = None
    row_labels = (
        "Clean · current-image keys",
        "Clean · previous-hidden-state keys",
        "Noisy · current-image keys",
        "Noisy · previous-hidden-state keys",
    )
    row_data = (
        invalid_mean[0, 0],
        invalid_mean[0, 1],
        invalid_mean[1, 0],
        invalid_mean[1, 1],
    )
    for ri, values in enumerate(row_data):
        for ti in range(T):
            ax = fig.add_subplot(grid[ri, ti])
            last = heatmap(ax, values[ti], cmap="viridis", vmin=0.0, vmax=vmax, target=True)
            if ri == 0:
                ax.set_title(f"t{ti}", fontsize=9)
            if ti == 0:
                ax.set_ylabel(row_labels[ri], fontsize=9)
    if last is not None:
        fig.colorbar(last, ax=fig.axes, shrink=0.62, pad=0.01, label="Raw mean attention per key")
    fig.suptitle(
        "Invalid-change exemplar · red = S1 cue · cyan = S4 changed target · 18° at t5",
        fontsize=13,
    )
    fig.text(0.5, -0.004, EVIDENCE_LABEL, ha="center", va="bottom", fontsize=8)
    save_figure(fig, root, "invalid_maps")


def plot_invalid_difference(invalid_mean: np.ndarray, root: Path, diff_abs: float) -> None:
    difference = invalid_mean[1] - invalid_mean[0]
    fig = plt.figure(figsize=(16.5, 4.7), constrained_layout=True)
    grid = fig.add_gridspec(2, 7, wspace=0.06, hspace=0.14)
    last = None
    for si, label in enumerate(("Current-image keys", "Previous-hidden-state keys")):
        for ti in range(T):
            ax = fig.add_subplot(grid[si, ti])
            last = heatmap(
                ax,
                difference[si, ti],
                cmap="coolwarm",
                vmin=-diff_abs,
                vmax=diff_abs,
                target=True,
            )
            if si == 0:
                ax.set_title(f"t{ti}", fontsize=9)
            if ti == 0:
                ax.set_ylabel(label, fontsize=9)
    if last is not None:
        fig.colorbar(last, ax=fig.axes, shrink=0.62, pad=0.01, label="Noisy − clean raw attention")
    fig.suptitle("Invalid exemplar difference maps (sources never fused)", fontsize=13)
    fig.text(0.5, -0.007, EVIDENCE_LABEL, ha="center", va="bottom", fontsize=8)
    save_figure(fig, root, "invalid_diff")


def append_metric_rows(
    rows: list[dict[str, Any]],
    *,
    assay: str,
    condition: str,
    source: str,
    validity: float,
    metrics: dict[str, np.ndarray],
) -> None:
    for metric, values in metrics.items():
        mean, sem = mean_sem(values)
        for frame in range(T):
            rows.append(
                {
                    "assay": assay,
                    "condition": condition,
                    "source": source,
                    "displayed_validity": float(validity),
                    "frame": frame,
                    "metric": metric,
                    "mean": float(mean[frame]),
                    "sem": float(sem[frame]),
                    "trials": int(values.shape[0]),
                }
            )


def write_metrics_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = (
        "assay",
        "condition",
        "source",
        "displayed_validity",
        "frame",
        "metric",
        "mean",
        "sem",
        "trials",
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate(stage: Path) -> None:
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    models, identities = load_models()
    producer_hash = sha256_file(Path(__file__).resolve())
    protocol_hash = sha256_file(PROTOCOL)

    policy_seed_a = stable_seed("vda4_memory_noise_attention_diagnostic_v1", "assay_a", "policy")
    memory_seed_a = stable_seed("vda4_memory_noise_attention_diagnostic_v1", "assay_a", "mnemonic")
    policy_a = np.random.default_rng(policy_seed_a).random((TRIALS, T)).astype(np.float32)

    cue_visual = np.empty((2, len(VALIDITIES), TRIALS, T, 4, 4), dtype=np.float32)
    cue_memory = np.empty_like(cue_visual)
    cue_visual_scores = np.empty((2, len(VALIDITIES), TRIALS, T, 4), dtype=np.float32)
    cue_memory_scores = np.empty_like(cue_visual_scores)
    trial_registry: dict[str, Any] = {}
    runtime_registry: dict[str, Any] = {condition: {} for condition in CONDITIONS}
    metric_rows: list[dict[str, Any]] = []

    for vi, validity in enumerate(VALIDITIES):
        bank, record = make_bank(
            bank_id=f"assay_a_nochange_v{validity:g}",
            displayed_validity=float(validity),
            changed=0,
            change_index=0,
            magnitude=0.0,
            sensory_seed=1701,
            policy_uniforms=policy_a,
            memory_noise_seed=memory_seed_a,
        )
        record["policy_uniform_seed"] = int(policy_seed_a)
        trial_registry[bank.bank_id] = record
        clean, noisy = run_pair(models, bank)
        for ci, (condition, rollout) in enumerate(zip(CONDITIONS, (clean, noisy))):
            visual, memory, visual_scores, memory_scores = split_and_score(rollout["attention"])
            cue_visual[ci, vi] = visual
            cue_memory[ci, vi] = memory
            cue_visual_scores[ci, vi] = visual_scores
            cue_memory_scores[ci, vi] = memory_scores
            runtime_registry[condition][bank.bank_id] = {
                "runtime_noise_contract": rollout["runtime_noise_contract"],
                "memory_noise_seed": rollout["memory_noise_seed"],
                "memory_noise_draw_calls": rollout["memory_noise_draw_calls"],
                "memory_noise_schedule_sha256": rollout["memory_noise_schedule_sha256"],
            }
            append_metric_rows(
                metric_rows,
                assay="cue_proportion_nochange",
                condition=condition,
                source=SOURCES[0],
                validity=float(validity),
                metrics=metric_bundle(visual_scores, cue_index=0, target_index=0),
            )
            append_metric_rows(
                metric_rows,
                assay="cue_proportion_nochange",
                condition=condition,
                source=SOURCES[1],
                validity=float(validity),
                metrics=metric_bundle(memory_scores, cue_index=0, target_index=0),
            )

    noisy_schedule_hashes = {
        runtime_registry["interrupted_noisy"][f"assay_a_nochange_v{v:g}"][
            "memory_noise_schedule_sha256"
        ]
        for v in VALIDITIES
    }
    if len(noisy_schedule_hashes) != 1:
        raise RuntimeError("Assay A did not reuse one mnemonic CRN schedule across cue proportions")

    policy_seed_b = stable_seed("vda4_memory_noise_attention_diagnostic_v1", "assay_b", "policy")
    memory_seed_b = stable_seed("vda4_memory_noise_attention_diagnostic_v1", "assay_b", "mnemonic")
    sensory_seed_b = stable_seed(
        "vda4_memory_noise_attention_diagnostic_v1", "assay_b", "sensory", bits=32
    )
    policy_b = np.random.default_rng(policy_seed_b).random((TRIALS, T)).astype(np.float32)
    invalid_bank, invalid_record = make_bank(
        bank_id="assay_b_invalid_cue0_target3_v0.75_mag18",
        displayed_validity=0.75,
        changed=1,
        change_index=3,
        magnitude=18.0,
        sensory_seed=sensory_seed_b,
        policy_uniforms=policy_b,
        memory_noise_seed=memory_seed_b,
    )
    invalid_record["policy_uniform_seed"] = int(policy_seed_b)
    trial_registry[invalid_bank.bank_id] = invalid_record
    clean_invalid, noisy_invalid = run_pair(models, invalid_bank)

    invalid_visual = np.empty((2, TRIALS, T, 4, 4), dtype=np.float32)
    invalid_memory = np.empty_like(invalid_visual)
    invalid_visual_scores = np.empty((2, TRIALS, T, 4), dtype=np.float32)
    invalid_memory_scores = np.empty_like(invalid_visual_scores)
    for ci, (condition, rollout) in enumerate(zip(CONDITIONS, (clean_invalid, noisy_invalid))):
        visual, memory, visual_scores, memory_scores = split_and_score(rollout["attention"])
        invalid_visual[ci] = visual
        invalid_memory[ci] = memory
        invalid_visual_scores[ci] = visual_scores
        invalid_memory_scores[ci] = memory_scores
        runtime_registry[condition][invalid_bank.bank_id] = {
            "runtime_noise_contract": rollout["runtime_noise_contract"],
            "memory_noise_seed": rollout["memory_noise_seed"],
            "memory_noise_draw_calls": rollout["memory_noise_draw_calls"],
            "memory_noise_schedule_sha256": rollout["memory_noise_schedule_sha256"],
        }
        append_metric_rows(
            metric_rows,
            assay="invalid_exemplar",
            condition=condition,
            source=SOURCES[0],
            validity=0.75,
            metrics=metric_bundle(visual_scores, cue_index=0, target_index=3),
        )
        append_metric_rows(
            metric_rows,
            assay="invalid_exemplar",
            condition=condition,
            source=SOURCES[1],
            validity=0.75,
            metrics=metric_bundle(memory_scores, cue_index=0, target_index=3),
        )

    arrays_dir = stage / "data"
    arrays_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        arrays_dir / "attention_diagnostic_trials.npz",
        cue_visual_full_4x4=cue_visual,
        cue_memory_full_4x4=cue_memory,
        cue_visual_column_scores=cue_visual_scores,
        cue_memory_column_scores=cue_memory_scores,
        invalid_visual_full_4x4=invalid_visual,
        invalid_memory_full_4x4=invalid_memory,
        invalid_visual_column_scores=invalid_visual_scores,
        invalid_memory_column_scores=invalid_memory_scores,
        conditions=np.asarray(CONDITIONS),
        sources=np.asarray(SOURCES),
        displayed_validities=VALIDITIES,
        frames=np.arange(T, dtype=np.int64),
        cue_index=np.asarray(0, dtype=np.int64),
        invalid_target_index=np.asarray(3, dtype=np.int64),
    )
    write_metrics_csv(arrays_dir / "attention_metrics.csv", metric_rows)

    cue_mean = np.stack(
        (cue_visual_scores.mean(axis=2), cue_memory_scores.mean(axis=2)), axis=2
    )
    invalid_mean = np.stack(
        (invalid_visual_scores.mean(axis=1), invalid_memory_scores.mean(axis=1)), axis=1
    )
    raw_vmax = float(max(cue_mean.max(), invalid_mean.max()))
    cue_diff_abs = float(np.max(np.abs(cue_mean[1] - cue_mean[0])))
    invalid_diff_abs = float(np.max(np.abs(invalid_mean[1] - invalid_mean[0])))
    if raw_vmax <= 0.0 or cue_diff_abs <= 0.0 or invalid_diff_abs <= 0.0:
        raise RuntimeError("unexpected zero attention scale")

    display = {
        "schema_version": 1,
        "evidence_label": EVIDENCE_LABEL,
        "conditions": CONDITIONS,
        "condition_labels": (
            "Historical clean final · train σ=0 · eval σ=0 · iter 19,999",
            "Interrupted noisy · train σ=0.5 · eval σ=0.5 · iter 15,999",
        ),
        "sources": SOURCES,
        "source_labels": (
            "Current-image-key routing",
            "Previous-hidden-state-key routing",
        ),
        "displayed_validities": VALIDITIES,
        "frames": list(range(T)),
        "patch_order": ["top_left", "top_right", "bottom_left", "bottom_right"],
        "cue_index": 0,
        "invalid_target_index": 3,
        "raw_shared_vmax": raw_vmax,
        "cue_difference_absmax": cue_diff_abs,
        "invalid_difference_absmax": invalid_diff_abs,
        "cue_mean_column_scores": cue_mean,
        "invalid_mean_column_scores": invalid_mean,
        "attention_definition": {
            "raw_shape": [4, 8],
            "query_rows": "four current-image patches",
            "current_image_key_columns": [0, 1, 2, 3],
            "previous_hidden_state_key_columns": [4, 5, 6, 7],
            "column_score": "mean down four query rows, sources split first",
            "normalization": "joint eight-key softmax; raw source mass retained",
            "fusion": "never",
        },
    }
    write_json(stage / "DISPLAY_DATA.json", display)
    write_json(stage / "TRIAL_BANK_REGISTRY.json", trial_registry)
    write_json(stage / "RUNTIME_NOISE_REGISTRY.json", runtime_registry)
    write_json(
        stage / "COMPARISON_IDENTITY.json",
        {
            "schema_version": 1,
            "evidence_boundary": EVIDENCE_LABEL,
            "registered_terminal_pair": False,
            "checkpoint_identities": identities,
            "producer_path": str(Path(__file__).resolve()),
            "producer_sha256": producer_hash,
            "protocol_path": str(PROTOCOL.resolve()),
            "protocol_sha256": protocol_hash,
            "device": str(core.DEVICE),
            "trials_per_display_cell": TRIALS,
            "assays": {
                "cue_proportion_nochange": {
                    "cue_index": 0,
                    "validities": VALIDITIES,
                    "sensory_seed": 1701,
                    "policy_uniform_seed": int(policy_seed_a),
                    "memory_noise_seed": int(memory_seed_a),
                },
                "invalid_exemplar": {
                    "cue_index": 0,
                    "target_index": 3,
                    "validity": 0.75,
                    "magnitude_degrees": 18.0,
                    "sensory_seed": int(sensory_seed_b),
                    "policy_uniform_seed": int(policy_seed_b),
                    "memory_noise_seed": int(memory_seed_b),
                },
            },
        },
    )

    plot_cue_plate(cue_mean, stage, raw_vmax)
    plot_cue_difference(cue_mean, stage, cue_diff_abs)
    plot_invalid_plate(invalid_mean, stage, raw_vmax)
    plot_invalid_difference(invalid_mean, stage, invalid_diff_abs)

    manifest_entries = []
    for path in sorted(p for p in stage.rglob("*") if p.is_file()):
        manifest_entries.append(
            {
                "path": path.relative_to(stage).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    write_json(
        stage / "MANIFEST.json",
        {
            "schema_version": 1,
            "evidence_boundary": EVIDENCE_LABEL,
            "files": manifest_entries,
        },
    )


def main() -> None:
    if OUTPUT_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {OUTPUT_ROOT}")
    stage = HERE / f".m.{uuid.uuid4().hex[:6]}"
    if stage.exists():
        raise FileExistsError(stage)
    stage.mkdir(parents=True)
    try:
        generate(stage)
        os.replace(stage, OUTPUT_ROOT)
    except Exception:
        # Preserve the unique partial directory for diagnosis; never overwrite it.
        raise
    print(OUTPUT_ROOT)


if __name__ == "__main__":
    main()
