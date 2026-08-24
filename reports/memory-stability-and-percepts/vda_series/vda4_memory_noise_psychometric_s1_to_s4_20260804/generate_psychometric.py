"""Generate the frozen S1-cued, forced-S4 VDA4 psychometric diagnostic."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
import uuid
from pathlib import Path
from typing import Any

os.environ["RVIT_DEVICE"] = "cuda"

import numpy as np

sys.modules.setdefault("numpy._core", np.core)
sys.modules.setdefault("numpy._core.multiarray", np.core.multiarray)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vda_sweep import vda_core as core
from experiments.vda4_memory_noise.grid2x2_crossattn1_pilot_v1 import (
    evaluate_paired_v1 as evalmod,
)


OUTPUT_ROOT = HERE / "results_v1"
PROTOCOL = HERE / "PROTOCOL_AMENDMENT.md"
TRIALS = 300
T = 7
MAGNITUDES = np.asarray([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0])
CONDITIONS = ("historical_clean", "interrupted_noisy")
CONDITION_LABELS = (
    "No injection · train σ=0 · eval σ=0",
    "Noise injection · train σ=0.5 · eval σ=0.5",
)
SENSORY_SEED = 2608044101
POLICY_SEED = 2608044102
MEMORY_SEED = 2608044103
NOCHANGE_SENSORY_SEED = 2608044201
NOCHANGE_POLICY_SEED = 2608044202
NOCHANGE_MEMORY_SEED = 2608044203

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
    "Exploratory OOD invalid probe: historical terminal clean reference versus "
    "interrupted noise-trained checkpoint; training duration, provenance, and "
    "acute evaluation noise are not matched."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
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


def validate_model(model: Any, expected_noise: float) -> dict[str, Any]:
    encoder = model.encoder
    observed = {
        "feedback": str(encoder.feedback),
        "cell": str(encoder.cell),
        "two_lstm": bool(encoder.two_lstm),
        "d_mem": int(encoder.d_mem),
        "n_tokens": int(model.n_tokens),
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
        "memory_decay": 1.0,
        "memory_noise_std": float(expected_noise),
        "seq_len": 7,
    }
    for key, value in expected.items():
        if observed[key] != value:
            raise RuntimeError(f"model contract mismatch for {key}: {observed[key]!r} != {value!r}")
    return observed


def load_models() -> tuple[dict[str, Any], dict[str, Any]]:
    if not str(core.DEVICE).startswith("cuda"):
        raise RuntimeError(f"frozen producer requires local CUDA, got {core.DEVICE!r}")
    if sha256_file(CLEAN_CHECKPOINT) != CLEAN_SHA256:
        raise RuntimeError("historical clean checkpoint hash mismatch")
    if sha256_file(NOISY_CHECKPOINT) != NOISY_SHA256:
        raise RuntimeError("interrupted noisy checkpoint hash mismatch")
    clean, clean_iteration = core.load(
        "vda4", "crossattn1", 128,
        checkpoint_path=CLEAN_CHECKPOINT,
        expected_checkpoint_sha256=CLEAN_SHA256,
        require_iteration=CLEAN_ITERATION,
        validate_metadata=True,
    )
    noisy, noisy_iteration = core.load(
        "vda4", "crossattn1", 128,
        checkpoint_path=NOISY_CHECKPOINT,
        expected_checkpoint_sha256=NOISY_SHA256,
        require_iteration=NOISY_ITERATION,
        validate_metadata=True,
    )
    contracts = {
        CONDITIONS[0]: validate_model(clean, 0.0),
        CONDITIONS[1]: validate_model(noisy, 0.5),
    }
    clean_shapes = {key: tuple(value.shape) for key, value in clean.state_dict().items()}
    noisy_shapes = {key: tuple(value.shape) for key, value in noisy.state_dict().items()}
    if clean_shapes != noisy_shapes:
        raise RuntimeError("checkpoint model keys or tensor shapes do not match")
    identities = {
        CONDITIONS[0]: {
            "path": str(CLEAN_CHECKPOINT.resolve()),
            "sha256": CLEAN_SHA256,
            "iteration": int(clean_iteration),
            "training_memory_noise_std": 0.0,
            "evaluation_memory_noise_std": 0.0,
            "contract": contracts[CONDITIONS[0]],
        },
        CONDITIONS[1]: {
            "path": str(NOISY_CHECKPOINT.resolve()),
            "sha256": NOISY_SHA256,
            "iteration": int(noisy_iteration),
            "training_memory_noise_std": 0.5,
            "evaluation_memory_noise_std": 0.5,
            "contract": contracts[CONDITIONS[1]],
        },
        "architecture_state_shape_sha256": sha256_bytes(
            json.dumps(clean_shapes, sort_keys=True).encode("utf-8")
        ),
    }
    return {CONDITIONS[0]: clean, CONDITIONS[1]: noisy}, identities


def make_bank(
    *,
    bank_id: str,
    changed: int,
    change_index: int,
    magnitude: float,
    sensory_seed: int,
    policy_uniforms: np.ndarray,
    policy_seed: int,
    memory_seed: int,
) -> tuple[evalmod.TrialBank, dict[str, Any]]:
    videos = core.make_video_batch(
        "vda4", 0, 1.0, "red", int(changed), int(change_index), float(magnitude),
        B=TRIALS, seed=int(sensory_seed),
    )
    video_cpu = videos.detach().cpu().numpy()
    record = {
        "bank_id": bank_id,
        "task": "vda4",
        "trials": TRIALS,
        "cue_index": 0,
        "displayed_validity": 1.0,
        "validity_scope": "ood_forced_invalid_probe" if changed else "nochange_control",
        "changed": int(changed),
        "change_index": int(change_index),
        "magnitude_degrees": float(magnitude),
        "sensory_seed": int(sensory_seed),
        "policy_uniform_seed": int(policy_seed),
        "memory_noise_seed": int(memory_seed),
        "video_shape": list(video_cpu.shape),
        "video_sha256": sha256_bytes(video_cpu.tobytes(order="C")),
        "policy_uniform_shape": list(policy_uniforms.shape),
        "policy_uniform_sha256": sha256_bytes(policy_uniforms.tobytes(order="C")),
    }
    return (
        evalmod.TrialBank(bank_id, videos, policy_uniforms, int(memory_seed), record),
        record,
    )


def run_pair(models: dict[str, Any], bank: evalmod.TrialBank) -> dict[str, dict[str, Any]]:
    return {
        CONDITIONS[0]: evalmod.rollout_sampled(
            models[CONDITIONS[0]], bank, eval_noise_std=0.0
        ),
        CONDITIONS[1]: evalmod.rollout_sampled(
            models[CONDITIONS[1]], bank, eval_noise_std=0.5
        ),
    }


def qualifying_mask(press: np.ndarray) -> np.ndarray:
    return np.isin(np.asarray(press), (5, 6))


def wilson_interval(count: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = float(count) / float(n)
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / denom
    return center - half, center + half


def save_curve_figure(root: Path, rates: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> None:
    figure_dir = root / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    styles = (
        {"color": "#1f77b4", "marker": "o", "linestyle": "-"},
        {"color": "#d62728", "marker": "s", "linestyle": "--"},
    )
    for condition_index, label in enumerate(CONDITION_LABELS):
        errors = np.vstack(
            (rates[condition_index] - lower[condition_index], upper[condition_index] - rates[condition_index])
        )
        ax.errorbar(
            MAGNITUDES,
            rates[condition_index],
            yerr=errors,
            label=label,
            linewidth=2.0,
            markersize=5.0,
            capsize=3.0,
            **styles[condition_index],
        )
    ax.set_xlim(-0.8, 30.8)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xticks(MAGNITUDES)
    ax.set_yticks(np.linspace(0.0, 1.0, 6))
    ax.set_xlabel("S4 orientation-change magnitude (degrees)")
    ax.set_ylabel("P(first change report at t5 or t6)")
    ax.grid(True, alpha=0.22, linewidth=0.7)
    ax.legend(frameon=False, loc="best")
    ax.set_title("Fully expressed S1 cue → forced invalid S4 change")
    fig.text(
        0.5, 0.01,
        "300 matched held-out sampled-policy trials per point; Wilson 95% intervals. "
        "Validity=1.0 forced-invalid probe is out of distribution.",
        ha="center", fontsize=8,
    )
    fig.tight_layout(rect=(0.0, 0.055, 1.0, 1.0))
    fig.savefig(figure_dir / "psychometric.png", dpi=220, bbox_inches="tight")
    fig.savefig(figure_dir / "psychometric.pdf", bbox_inches="tight")
    plt.close(fig)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = (
        "condition", "label", "magnitude_degrees", "trials", "response_count",
        "response_probability", "wilson95_lower", "wilson95_upper",
        "early_response_count", "no_response_count", "mean_qualifying_rt_frame",
        "false_alarm_count", "false_alarm_trials", "false_alarm_rate",
        "dprime", "criterion",
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate(stage: Path) -> None:
    if not PROTOCOL.is_file():
        raise FileNotFoundError(PROTOCOL)
    models, identities = load_models()
    protocol_sha = sha256_file(PROTOCOL)
    producer_sha = sha256_file(Path(__file__).resolve())

    policy_uniforms = np.random.default_rng(POLICY_SEED).random((TRIALS, T)).astype(np.float32)
    nochange_uniforms = np.random.default_rng(NOCHANGE_POLICY_SEED).random((TRIALS, T)).astype(np.float32)

    trial_registry: dict[str, Any] = {}
    runtime_registry: dict[str, Any] = {condition: {} for condition in CONDITIONS}
    presses = np.empty((2, len(MAGNITUDES), TRIALS), dtype=np.int64)
    action1_probability = np.empty((2, len(MAGNITUDES), TRIALS, T), dtype=np.float32)
    response_count = np.zeros((2, len(MAGNITUDES)), dtype=np.int64)
    response_rate = np.zeros((2, len(MAGNITUDES)), dtype=np.float64)
    ci_lower = np.zeros_like(response_rate)
    ci_upper = np.zeros_like(response_rate)
    early_count = np.zeros_like(response_count)
    no_response_count = np.zeros_like(response_count)
    mean_rt = np.full_like(response_rate, np.nan)

    for magnitude_index, magnitude in enumerate(MAGNITUDES):
        bank_id = f"s1_full_forced_s4_mag{magnitude:g}"
        bank, record = make_bank(
            bank_id=bank_id,
            changed=1,
            change_index=3,
            magnitude=float(magnitude),
            sensory_seed=SENSORY_SEED,
            policy_uniforms=policy_uniforms,
            policy_seed=POLICY_SEED,
            memory_seed=MEMORY_SEED,
        )
        trial_registry[bank_id] = record
        rollouts = run_pair(models, bank)
        for condition_index, condition in enumerate(CONDITIONS):
            rollout = rollouts[condition]
            condition_press = np.asarray(rollout["press"], dtype=np.int64)
            detected = qualifying_mask(condition_press)
            presses[condition_index, magnitude_index] = condition_press
            action1_probability[condition_index, magnitude_index] = rollout[
                "action1_probability"
            ]
            count = int(detected.sum())
            response_count[condition_index, magnitude_index] = count
            response_rate[condition_index, magnitude_index] = count / float(TRIALS)
            ci_lower[condition_index, magnitude_index], ci_upper[
                condition_index, magnitude_index
            ] = wilson_interval(count, TRIALS)
            early_count[condition_index, magnitude_index] = int(
                np.isin(condition_press, (0, 1, 2, 3, 4)).sum()
            )
            no_response_count[condition_index, magnitude_index] = int(
                (condition_press < 0).sum()
            )
            if count:
                mean_rt[condition_index, magnitude_index] = float(condition_press[detected].mean())
            runtime_registry[condition][bank_id] = {
                "runtime_noise_contract": rollout["runtime_noise_contract"],
                "memory_noise_seed": int(rollout["memory_noise_seed"]),
                "memory_noise_draw_calls": int(rollout["memory_noise_draw_calls"]),
                "memory_noise_schedule_sha256": rollout["memory_noise_schedule_sha256"],
            }

    noisy_schedule_hashes = {
        runtime_registry[CONDITIONS[1]][f"s1_full_forced_s4_mag{magnitude:g}"][
            "memory_noise_schedule_sha256"
        ]
        for magnitude in MAGNITUDES
    }
    if len(noisy_schedule_hashes) != 1:
        raise RuntimeError("noisy condition did not reuse one mnemonic CRN schedule across magnitudes")

    nochange_bank, nochange_record = make_bank(
        bank_id="s1_full_nochange_control",
        changed=0,
        change_index=0,
        magnitude=0.0,
        sensory_seed=NOCHANGE_SENSORY_SEED,
        policy_uniforms=nochange_uniforms,
        policy_seed=NOCHANGE_POLICY_SEED,
        memory_seed=NOCHANGE_MEMORY_SEED,
    )
    trial_registry[nochange_bank.bank_id] = nochange_record
    nochange_rollouts = run_pair(models, nochange_bank)
    nochange_press = np.empty((2, TRIALS), dtype=np.int64)
    false_alarm_count = np.zeros(2, dtype=np.int64)
    false_alarm_rate = np.zeros(2, dtype=np.float64)
    late_nochange_count = np.zeros(2, dtype=np.int64)
    for condition_index, condition in enumerate(CONDITIONS):
        rollout = nochange_rollouts[condition]
        values = np.asarray(rollout["press"], dtype=np.int64)
        nochange_press[condition_index] = values
        false_alarm_count[condition_index] = int((values >= 0).sum())
        false_alarm_rate[condition_index] = false_alarm_count[condition_index] / float(TRIALS)
        late_nochange_count[condition_index] = int(qualifying_mask(values).sum())
        runtime_registry[condition][nochange_bank.bank_id] = {
            "runtime_noise_contract": rollout["runtime_noise_contract"],
            "memory_noise_seed": int(rollout["memory_noise_seed"]),
            "memory_noise_draw_calls": int(rollout["memory_noise_draw_calls"]),
            "memory_noise_schedule_sha256": rollout["memory_noise_schedule_sha256"],
        }

    dprime = np.zeros_like(response_rate)
    criterion = np.zeros_like(response_rate)
    rows: list[dict[str, Any]] = []
    for condition_index, condition in enumerate(CONDITIONS):
        for magnitude_index, magnitude in enumerate(MAGNITUDES):
            dprime[condition_index, magnitude_index], criterion[
                condition_index, magnitude_index
            ] = evalmod.hautus_sdt(
                int(response_count[condition_index, magnitude_index]),
                int(false_alarm_count[condition_index]),
                TRIALS,
                TRIALS,
            )
            rows.append(
                {
                    "condition": condition,
                    "label": CONDITION_LABELS[condition_index],
                    "magnitude_degrees": float(magnitude),
                    "trials": TRIALS,
                    "response_count": int(response_count[condition_index, magnitude_index]),
                    "response_probability": float(response_rate[condition_index, magnitude_index]),
                    "wilson95_lower": float(ci_lower[condition_index, magnitude_index]),
                    "wilson95_upper": float(ci_upper[condition_index, magnitude_index]),
                    "early_response_count": int(early_count[condition_index, magnitude_index]),
                    "no_response_count": int(no_response_count[condition_index, magnitude_index]),
                    "mean_qualifying_rt_frame": float(mean_rt[condition_index, magnitude_index]),
                    "false_alarm_count": int(false_alarm_count[condition_index]),
                    "false_alarm_trials": TRIALS,
                    "false_alarm_rate": float(false_alarm_rate[condition_index]),
                    "dprime": float(dprime[condition_index, magnitude_index]),
                    "criterion": float(criterion[condition_index, magnitude_index]),
                }
            )

    thresholds = np.asarray(
        [evalmod.threshold50(MAGNITUDES, response_rate[index]) for index in range(2)],
        dtype=np.float64,
    )

    data_dir = stage / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        data_dir / "psychometric_trials.npz",
        conditions=np.asarray(CONDITIONS),
        condition_labels=np.asarray(CONDITION_LABELS),
        magnitudes_degrees=MAGNITUDES,
        press=presses,
        action1_probability=action1_probability,
        response_count=response_count,
        response_rate=response_rate,
        wilson95_lower=ci_lower,
        wilson95_upper=ci_upper,
        early_response_count=early_count,
        no_response_count=no_response_count,
        mean_qualifying_rt_frame=mean_rt,
        nochange_press=nochange_press,
        false_alarm_count=false_alarm_count,
        false_alarm_rate=false_alarm_rate,
        late_nochange_count=late_nochange_count,
        dprime=dprime,
        criterion=criterion,
        threshold50_degrees=thresholds,
    )
    write_csv(data_dir / "psychometric.csv", rows)

    display = {
        "schema_version": 1,
        "question": "Fully expressed S1 cue followed by forced invalid S4 change",
        "validity_scope": "ood_forced_invalid_probe",
        "conditions": CONDITIONS,
        "condition_labels": CONDITION_LABELS,
        "magnitudes_degrees": MAGNITUDES,
        "trials_per_point": TRIALS,
        "response_definition": "first sampled change report at t5 or t6",
        "response_count": response_count,
        "response_probability": response_rate,
        "wilson95_lower": ci_lower,
        "wilson95_upper": ci_upper,
        "early_response_count": early_count,
        "no_response_count": no_response_count,
        "mean_qualifying_rt_frame": mean_rt,
        "false_alarm_count": false_alarm_count,
        "false_alarm_rate": false_alarm_rate,
        "late_nochange_count": late_nochange_count,
        "threshold50_degrees": thresholds,
        "dprime": dprime,
        "criterion": criterion,
        "evidence_label": EVIDENCE_LABEL,
    }
    write_json(stage / "DISPLAY_DATA.json", display)
    write_json(stage / "TRIAL_BANK_REGISTRY.json", trial_registry)
    write_json(stage / "RUNTIME_NOISE_REGISTRY.json", runtime_registry)
    write_json(
        stage / "COMPARISON_IDENTITY.json",
        {
            "schema_version": 1,
            "registered_terminal_pair": False,
            "validity_scope": "ood_forced_invalid_probe",
            "evidence_boundary": EVIDENCE_LABEL,
            "checkpoint_identities": identities,
            "device": str(core.DEVICE),
            "gpu_name": __import__("torch").cuda.get_device_name(0),
            "producer_path": str(Path(__file__).resolve()),
            "producer_sha256": producer_sha,
            "protocol_path": str(PROTOCOL.resolve()),
            "protocol_sha256": protocol_sha,
            "frozen_seeds": {
                "sensory": SENSORY_SEED,
                "policy_uniform": POLICY_SEED,
                "mnemonic_standard_normal": MEMORY_SEED,
                "nochange_sensory": NOCHANGE_SENSORY_SEED,
                "nochange_policy_uniform": NOCHANGE_POLICY_SEED,
                "nochange_mnemonic_standard_normal": NOCHANGE_MEMORY_SEED,
            },
        },
    )
    save_curve_figure(stage, response_rate, ci_lower, ci_upper)

    files = []
    for path in sorted(item for item in stage.rglob("*") if item.is_file()):
        files.append(
            {
                "path": path.relative_to(stage).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    write_json(
        stage / "MANIFEST.json",
        {"schema_version": 1, "evidence_boundary": EVIDENCE_LABEL, "files": files},
    )


def main() -> None:
    if OUTPUT_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {OUTPUT_ROOT}")
    stage = HERE / f".p.{uuid.uuid4().hex[:6]}"
    if stage.exists():
        raise FileExistsError(stage)
    stage.mkdir(parents=True)
    generate(stage)
    os.replace(stage, OUTPUT_ROOT)
    print(OUTPUT_ROOT)


if __name__ == "__main__":
    main()
