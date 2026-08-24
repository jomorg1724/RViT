"""Produce the VDA16 affine three-location causal-rescue evaluation.

This is the affine_ew counterpart of ``change_location_intervention.py``'s
VDA16 crossattn1 experiment.  It deliberately keeps that experiment's trial
generator, common-random-number policy, clamp doses, hit definition, no-change
SDT control, and figures unchanged while binding the admitted terminal affine
checkpoint.  The output directory is immutable: an existing path is rejected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis import change_location_intervention as intervention


CHECKPOINT = (
    ROOT
    / "reports/vda_series/vda16_affine_nodecay_20260720_production"
    / "provenance/checkpoints/rvit_paper_vda16_final.pt"
)
CHECKPOINT_ADMISSION = (
    ROOT
    / "reports/vda_series/vda16_affine_nodecay_20260720_production"
    / "provenance/CHECKPOINT_ADMISSION.json"
)
EXPECTED_CHECKPOINT_SHA256 = "52141da629e2c7f8f902826196067efbadb924608eecde7560559fdc0f813233"
EXPECTED_ADMISSION_SHA256 = "724cf10b92ead6f34772c28ff236169e54d39b500154cbc3305fb35bc1689239"
DEFAULT_OUTPUT = ROOT / "reports/vda_series/vda16_affine_change_location_intervention_20260729_v2"
SOURCE_FILES = (
    ROOT / "analysis/vda16_affine_change_location_intervention.py",
    ROOT / "analysis/change_location_intervention.py",
    ROOT / "vda_sweep/vda_core.py",
    ROOT / "vda_sweep/matched_width.py",
    ROOT / "model.py",
    ROOT / "paper_encoder.py",
    ROOT / "paper_heads.py",
    ROOT / "conv_frontend.py",
    ROOT / "envs/tasks.py",
    ROOT / "envs/base.py",
    ROOT / "envs/__init__.py",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): strict_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [strict_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return strict_jsonable(value.tolist())
    if isinstance(value, np.generic):
        return strict_jsonable(value.item())
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(strict_jsonable(payload), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def validate_checkpoint_contract() -> dict[str, Any]:
    if not CHECKPOINT.is_file() or not CHECKPOINT_ADMISSION.is_file():
        raise FileNotFoundError("the admitted VDA16 affine checkpoint bundle is incomplete")
    checkpoint_sha = sha256_file(CHECKPOINT)
    admission_sha = sha256_file(CHECKPOINT_ADMISSION)
    if checkpoint_sha != EXPECTED_CHECKPOINT_SHA256:
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {checkpoint_sha}")
    if admission_sha != EXPECTED_ADMISSION_SHA256:
        raise RuntimeError(f"checkpoint-admission SHA-256 mismatch: {admission_sha}")

    admission = json.loads(CHECKPOINT_ADMISSION.read_text(encoding="utf-8"))
    expected = {
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        "checkpoint_schema_version": 3,
        "checkpoint_iteration": 19999,
        "task": "vda16",
        "feedback": "affine_ew",
        "width": 128,
        "memory_decay": 1.0,
        "grid": [4, 4],
        "image_size": 100,
        "seed": 0,
        "initialization": "fresh",
    }
    for key, value in expected.items():
        if admission.get(key) != value:
            raise ValueError(f"admission field {key!r} is {admission.get(key)!r}, expected {value!r}")
    if CHECKPOINT.stat().st_size != int(admission.get("checkpoint_bytes", -1)):
        raise ValueError("checkpoint byte count differs from its admission record")

    import torch

    checkpoint = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    if not isinstance(checkpoint, dict) or int(checkpoint.get("iter", -1)) != 19999:
        raise ValueError("checkpoint is not a terminal iteration-19999 dictionary")
    if int(checkpoint.get("checkpoint_schema_version", -1)) < 3:
        raise ValueError("checkpoint schema is older than 3")
    if checkpoint.get("task") != "vda16":
        raise ValueError("checkpoint task is not vda16")
    model_kwargs = checkpoint.get("model_kwargs")
    required_kwargs = {
        "feedback": "affine_ew",
        "d_mem": 128,
        "memory_decay": 1.0,
        "grid_rows": 4,
        "grid_cols": 4,
        "image_size": 100,
        "cell": "xlstm",
    }
    if not isinstance(model_kwargs, dict):
        raise ValueError("checkpoint lacks embedded model_kwargs")
    for key, value in required_kwargs.items():
        if model_kwargs.get(key) != value:
            raise ValueError(f"checkpoint model_kwargs[{key!r}] violates the evaluation contract")
    producer_hashes = checkpoint.get("producer_sha256")
    if not isinstance(producer_hashes, dict) or not producer_hashes:
        raise ValueError("checkpoint lacks producer hashes")
    state = checkpoint.get("model_state_dict")
    if not isinstance(state, dict) or not state:
        raise ValueError("checkpoint lacks model_state_dict")
    nonfinite = [name for name, tensor in state.items() if torch.is_tensor(tensor) and not torch.isfinite(tensor).all()]
    if nonfinite:
        raise ValueError(f"non-finite model tensors: {nonfinite[:5]}")

    return {
        "admission": admission,
        "admission_path": str(CHECKPOINT_ADMISSION.resolve()),
        "admission_sha256": admission_sha,
        "checkpoint_path": str(CHECKPOINT.resolve()),
        "checkpoint_sha256": checkpoint_sha,
        "checkpoint_bytes": CHECKPOINT.stat().st_size,
        "checkpoint_producer_sha256": producer_hashes,
        "checkpoint_tensor_count": len(state),
        "checkpoint_all_tensors_finite": True,
    }


def freeze_provenance(output_root: Path, checkpoint_contract: dict[str, Any]) -> dict[str, Any]:
    provenance = output_root / "provenance"
    source_snapshot = provenance / "source_snapshot"
    source_hashes: dict[str, str] = {}
    archived_sources: dict[str, dict[str, str]] = {}
    for source_index, source in enumerate(SOURCE_FILES):
        if not source.is_file():
            raise FileNotFoundError(source)
        relative = source.relative_to(ROOT)
        # The workspace root is already long on Windows.  Use compact archive
        # names and retain the source mapping explicitly in PROVENANCE.json.
        target = source_snapshot / f"{source_index:02d}{source.suffix}"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        source_hashes[str(relative).replace("\\", "/")] = sha256_file(target)
        archived_sources[str(relative).replace("\\", "/")] = {
            "archived_path": str(target.relative_to(output_root)).replace("\\", "/"),
            "sha256": sha256_file(target),
        }
    shutil.copy2(CHECKPOINT_ADMISSION, provenance / "CHECKPOINT_ADMISSION.json")
    record = {
        "schema_version": 1,
        "checkpoint": {key: value for key, value in checkpoint_contract.items() if key != "admission"},
        "source_snapshot_sha256": source_hashes,
        "archived_sources": archived_sources,
        "compatibility_audit": {
            "result": "pass_for_vda16_affine_ew_xlstm_4x4_path",
            "basis": (
                "The current generalized model differs from the frozen July 20 analysis snapshot "
                "only through an added recurrent-cell option, generalized state dispatch, comments, "
                "and unequal-grid frontend batching. The selected xlstm, affine_ew, equal 4x4 path "
                "retains the same operations and loads the checkpoint strictly."
            ),
            "claim_boundary": (
                "This is an analysis-code compatibility statement, not a claim that current source "
                "matches every original training producer hash."
            ),
        },
    }
    write_json(provenance / "PROVENANCE.json", record)
    return record


def build_effect_summary(environment: dict[str, Any], elapsed_seconds: float) -> dict[str, Any]:
    doses = [float(value) for value in environment["doses"]]
    suppress_index, natural_index, boost_index = doses.index(0.0), doses.index(0.5), doses.index(1.0)
    effects: dict[str, Any] = {}
    for role in intervention.LOCATION_ROLES:
        metrics = environment["metrics"][role]
        effects[role] = {
            "target_location": int(environment["role_target_location"][role]),
            "response_rate_suppress": float(metrics["response_rate"][suppress_index]),
            "response_rate_natural": float(metrics["response_rate"][natural_index]),
            "response_rate_boost": float(metrics["response_rate"][boost_index]),
            "response_rate_boost_minus_suppress": float(
                metrics["response_rate"][boost_index] - metrics["response_rate"][suppress_index]
            ),
            "dprime_boost_minus_suppress": float(
                metrics["dprime"][boost_index] - metrics["dprime"][suppress_index]
            ),
            "false_alarm_rate_suppress": float(metrics["false_alarm_rate"][suppress_index]),
            "false_alarm_rate_boost": float(metrics["false_alarm_rate"][boost_index]),
            "achieved_target_mass_suppress": float(
                metrics[
                    {"change": "achieved_change_mass_t6", "cued": "achieved_cued_mass_t6", "control": "achieved_control_mass_t6"}[role]
                ][suppress_index]
            ),
            "achieved_target_mass_natural": float(
                metrics[
                    {"change": "achieved_change_mass_t6", "cued": "achieved_cued_mass_t6", "control": "achieved_control_mass_t6"}[role]
                ][natural_index]
            ),
            "achieved_target_mass_boost": float(
                metrics[
                    {"change": "achieved_change_mass_t6", "cued": "achieved_cued_mass_t6", "control": "achieved_control_mass_t6"}[role]
                ][boost_index]
            ),
        }
    return {
        "schema_version": 1,
        "status": "complete_pending_independent_verification",
        "model": {
            "task": "vda16",
            "feedback": "affine_ew",
            "width": 128,
            "seed": 0,
            "checkpoint_iteration": 19999,
            "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        },
        "protocol": {
            "cue_location": 0,
            "true_change_location": 15,
            "neutral_control_location": 5,
            "focal_change_degrees": 30.0,
            "displayed_validity": 1.0,
            "invalid_trial_interpretation": "forced out-of-policy stress test",
            "trials_per_condition": intervention.TRIALS_PER_CONDITION,
            "common_random_numbers": True,
            "nochange_sdt_control": True,
            "clamp_from_frame": intervention.CLAMP_FROM,
            "qualifying_frames": list(intervention.QUALIFYING_FRAMES),
            "dose_parameters": doses,
            "key_logit_scale": intervention.CLAMP_LOGIT_SCALE,
        },
        "effects": effects,
        "elapsed_seconds": elapsed_seconds,
        "evidence_boundary": (
            "Single admitted seed-0 checkpoint; curriculum stopped at 47 degrees and is competence-gated. "
            "The experiment estimates within-checkpoint routing dependence at a 30-degree forced-invalid "
            "stress-test condition, not population uncertainty or full VDA16 competence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args()
    output_root = args.output_root.expanduser().resolve()
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {output_root}")

    # vda_core reads RVIT_DEVICE at import time.  The common producer has already
    # imported it, so require the caller's environment to agree with this flag.
    actual_device = str(intervention.core.DEVICE)
    if actual_device != args.device:
        raise RuntimeError(
            f"--device={args.device} but RVIT_DEVICE resolved to {actual_device!r}; "
            "set RVIT_DEVICE before launching"
        )

    checkpoint_contract = validate_checkpoint_contract()
    output_root.mkdir(parents=True)
    provenance = freeze_provenance(output_root, checkpoint_contract)
    config = {
        "schema_version": 1,
        "producer_path": str(Path(__file__).resolve()),
        "producer_sha256": sha256_file(Path(__file__).resolve()),
        "common_producer_path": str(Path(intervention.__file__).resolve()),
        "common_producer_sha256": sha256_file(Path(intervention.__file__).resolve()),
        "device": actual_device,
        "threads": 3,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "checkpoint": {key: value for key, value in checkpoint_contract.items() if key != "admission"},
        "protocol": {
            "trials_per_condition": intervention.TRIALS_PER_CONDITION,
            "invalid_trials_seed": intervention.INVALID_TRIALS_SEED,
            "nochange_trials_seed": intervention.NOCHANGE_TRIALS_SEED,
            "location_roles": list(intervention.LOCATION_ROLES),
            "dose_parameters": list(intervention.CLAMP_DOSE_PARAMETERS),
            "natural_dose": intervention.NATURAL_DOSE,
            "clamp_logit_scale": intervention.CLAMP_LOGIT_SCALE,
            "clamp_from_frame": intervention.CLAMP_FROM,
            "qualifying_frames": list(intervention.QUALIFYING_FRAMES),
        },
        "provenance_path": "provenance/PROVENANCE.json",
        "source_snapshot_sha256": provenance["source_snapshot_sha256"],
    }
    write_json(output_root / "analysis_config.json", config)

    spec = intervention.EnvSpec(
        env="vda16",
        feedback="affine_ew",
        width=128,
        grid=(4, 4),
        n_locations=16,
        cue_index=0,
        change_index=15,
        control_index=5,
        focal_magnitude=30.0,
        displayed_validity=1.0,
        checkpoint_path=CHECKPOINT,
        checkpoint_sha256=EXPECTED_CHECKPOINT_SHA256,
    )
    started = time.time()
    environment = intervention.run_environment(spec, output_root)
    if environment.get("status") != "ok" or int(environment.get("checkpoint_iteration", -1)) != 19999:
        raise RuntimeError("the common intervention producer did not return a terminal successful result")

    # Replace the historical permissive JSON serialization with strict JSON.
    write_json(output_root / "vda16/data/summary.json", environment)
    summary = build_effect_summary(environment, time.time() - started)
    write_json(output_root / "SUMMARY.json", summary)

    artifact_hashes = {
        str(path.relative_to(output_root)).replace("\\", "/"): sha256_file(path)
        for path in sorted(output_root.rglob("*"))
        if path.is_file()
    }
    manifest = {
        "schema_version": 1,
        "artifact_class": "VDA16 affine_ew three-location causal-rescue evaluation",
        "status": "complete_pending_independent_verification",
        "config_path": "analysis_config.json",
        "summary_path": "SUMMARY.json",
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        "checkpoint_admission_sha256": EXPECTED_ADMISSION_SHA256,
        "artifact_hashes": artifact_hashes,
    }
    write_json(output_root / "MANIFEST.json", manifest)
    print(f"[complete] wrote {output_root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
