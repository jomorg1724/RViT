"""Matched-width VDA battery with explicit geometry and checkpoint identity."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_ROOT = PROJECT_ROOT.parent / "battery_sweep_results/pod2/ckpt2"
TASKS = ("vda1", "vda4", "vda9")
FEEDBACKS = ("affine_ew", "crossattn1")
WIDTHS = (128, 256)
DECODED_VARIABLES = ("colour", "validity", "change", "change_location", "cued_change")
SAMPLE_LABELS = DECODED_VARIABLES
DISPLAYED_VALIDITIES = (0.25, 0.5, 0.75, 1.0)
CHANGE_MAGNITUDES = tuple(float(value) for value in range(2, 40, 4))
CLAMP_DOSE_PARAMETERS = (0.0, 0.25, 0.5, 0.75, 1.0)
CLAMP_LOGIT_SCALE = 6.0
CLAMP_KEY_LOGIT_BIASES = tuple(
    CLAMP_LOGIT_SCALE * (2.0 * dose - 1.0) for dose in CLAMP_DOSE_PARAMETERS
)
PSYCHOMETRIC_TRIALS_PER_POINT = 300
DECODER_N = 900
CLAMP_TRIALS = 250
PSYCHOMETRIC_SEED = 20260711
DECODER_SEED = 20260711
CLAMP_SEED = 20270711
BLOCKED_TASKS = {
    "vda2": {
        "status": "blocked",
        "reason": "no canonical d_mem=256 2x2 checkpoint; available d256 checkpoint has two tokens",
        "canonical_d128_tokens": 4,
        "available_d256_tokens": 2,
    }
}
COMPETENCE_FLAGS = [
    {
        "task": "vda9",
        "feedback": "crossattn1",
        "width": 256,
        "status": "competence_gated",
        "last_correct": 0.48,
        "late50_mean_correct": 0.45935,
        "best_correct": 0.5825,
        "last_theta": 65.0,
        "interpretation": (
            "retain in declared scope, but interpret mechanistic estimates as possible "
            "floor-policy diagnostics rather than controlled-attention evidence"
        ),
        "evidence_identity": "__metrics_inventory__",
        "evidence_row": 41,
    }
]


@dataclass(frozen=True)
class CheckpointSpec:
    task: str
    feedback: str
    width: int
    relative_path: str
    sha256: str
    grid: tuple[int, int]
    image_size: int
    active_locations: tuple[int, ...]

    @property
    def path(self) -> Path:
        return CHECKPOINT_ROOT / self.relative_path


_HASHES = {
    ("vda1", "affine_ew", 128): "1869701f8ff7d18c7caaeaabb0e9440b005af8d009a4e0eb5e7950191806d0f0",
    ("vda1", "affine_ew", 256): "bc8b2792dd3c18b02010bb2fcd74c3048f4943baa6a86c435c582efa23bc017c",
    ("vda1", "crossattn1", 128): "7e62d83a2241ec4b0aee7a05755d9b8053689910e06f35a10d0db02ad7abc492",
    ("vda1", "crossattn1", 256): "b6699c3ea52aa91b25546004a6352aa14b41a8d4631a4b7c72fb073a95c8b55f",
    ("vda4", "affine_ew", 128): "2341026363e6e1d2115a34a8ad9a91a73e385aab4a223aace763529e4047e085",
    ("vda4", "affine_ew", 256): "a991273cffb0ea54e0546a44d065c756333e089774627adada66aeda00a3b38d",
    ("vda4", "crossattn1", 128): "1a2fa8ae2a57982b6c91dc75079d8293781ce843271b92fe3cfbe5fc16137155",
    ("vda4", "crossattn1", 256): "e211fef85616e9d5e0bcc2991a9e4ca294d04c475246f44f3c693045d5b1cb17",
    ("vda9", "affine_ew", 128): "22f028f6232d9c3ea040019aff357645ddcaa69e4a09c2f8ceff224ea568d8d7",
    ("vda9", "affine_ew", 256): "cf594ad8d65deb5a227a52b2181249a94a49ea73eb1fddf3a917fd9c8b955612",
    ("vda9", "crossattn1", 128): "6c0587201cd2bf99b43e02278d4c65b03ab79d9b1f811406fc4962d962714946",
    ("vda9", "crossattn1", 256): "c26b2ad3202c69aedfa2ecbc4add9c81ba5b5fae73b32a41624a92f1629d751c",
}


def _task_geometry(task: str) -> tuple[tuple[int, int], int, tuple[int, ...]]:
    if task in ("vda1", "vda4"):
        return (2, 2), 50, ((0,) if task == "vda1" else tuple(range(4)))
    if task == "vda9":
        return (3, 3), 75, tuple(range(9))
    raise ValueError(f"task is not admitted to matched-width analysis: {task}")


def admissible_specs() -> tuple[CheckpointSpec, ...]:
    specs = []
    for task in TASKS:
        grid, image_size, active = _task_geometry(task)
        for feedback in FEEDBACKS:
            for width in WIDTHS:
                directory = f"{task}_{feedback}_d{width}"
                specs.append(
                    CheckpointSpec(
                        task=task,
                        feedback=feedback,
                        width=width,
                        relative_path=f"{directory}/rvit_plus_rl_latest.pt",
                        sha256=_HASHES[(task, feedback, width)],
                        grid=grid,
                        image_size=image_size,
                        active_locations=active,
                    )
                )
    return tuple(specs)


def blocked_cells() -> list[dict[str, object]]:
    return [
        {
            "task": task,
            "widths": list(WIDTHS),
            "feedbacks": list(FEEDBACKS),
            **record,
        }
        for task, record in BLOCKED_TASKS.items()
    ]


def protocol_for(spec: CheckpointSpec) -> dict[str, object]:
    """Return the task-level protocol shared exactly across width and routing."""
    invalid_index = -1 if len(spec.active_locations) == 1 else spec.active_locations[-1]
    return {
        "task": spec.task,
        "cue_index": spec.active_locations[0],
        "invalid_change_index": invalid_index,
        "invalid_defined": invalid_index >= 0,
        "displayed_validities": DISPLAYED_VALIDITIES,
        "change_magnitudes": CHANGE_MAGNITUDES,
        "psychometric_trials_per_point": PSYCHOMETRIC_TRIALS_PER_POINT,
        "psychometric_seed": PSYCHOMETRIC_SEED,
        "psychometric_invalid_at_displayed_validity_1": "forced out-of-policy stress test",
        "press_histogram_bins": ("no_response", 0, 1, 2, 3, 4, 5, 6),
        "qualifying_response_frames": (5, 6),
        "decoder_n": DECODER_N,
        "decoder_seed": DECODER_SEED,
        "decoder_location_condition": "change-present trials only",
        "decoder_spaces": ("architecture_native", "foldwise_pca_128"),
        "clamp_trials": CLAMP_TRIALS,
        "clamp_seed": CLAMP_SEED,
        "clamp_dose_parameters": CLAMP_DOSE_PARAMETERS,
        "clamp_logit_scale": CLAMP_LOGIT_SCALE,
        "clamp_key_logit_biases": CLAMP_KEY_LOGIT_BIASES,
        "clamp_intervention_semantics": (
            "additive bias to the cued location's attention-key logits; not achieved attention mass"
        ),
        "clamp_target_keys_by_routing": {
            "affine_ew": "cued image/self key",
            "crossattn1": "cued image key and corresponding memory key",
        },
        "clamp_displayed_validity": 0.75,
        "clamp_from_frame": 5,
        "clamp_hit_definition": "declaration at frame 5 or 6 on a reportable-change trial",
        "clamp_false_alarm_definition": "any declaration frame 0-6 on a no-change trial",
        "common_random_numbers_across_width_and_routing": True,
    }


def expected_shard_keys() -> set[str]:
    return {
        "metadata_json",
        "displayed_validities",
        "change_magnitudes",
        "psychometric_response_count_valid",
        "psychometric_response_count_invalid",
        "psychometric_response_rate_valid",
        "psychometric_response_rate_invalid",
        "psychometric_press_histogram_valid",
        "psychometric_press_histogram_invalid",
        "psychometric_nochange_response_count",
        "psychometric_nochange_response_rate",
        "psychometric_nochange_press_histogram",
        "decoder_sample_change_index",
        "clamp_dose_parameters",
        "clamp_key_logit_biases",
        "clamp_press_histogram_valid",
        "clamp_press_histogram_invalid",
        "clamp_press_histogram_nochange",
        "clamp_hit_count_valid",
        "clamp_hit_count_invalid",
        "clamp_false_alarm_count",
        "clamp_hit_rate_valid",
        "clamp_hit_rate_invalid",
        "clamp_false_alarm_rate",
        "clamp_dprime_valid",
        "clamp_dprime_invalid",
        "clamp_criterion_valid",
        "clamp_criterion_invalid",
    } | {
        f"decoder_{space}_{name}"
        for space in ("native", "matched128")
        for name in DECODED_VARIABLES
    } | {
        f"decoder_sample_label_{name}" for name in SAMPLE_LABELS
    } | {
        f"decoder_fold_id_{name}" for name in DECODED_VARIABLES
    }


def _sdt_from_counts(
    hit_count: np.ndarray, false_alarm_count: np.ndarray, n: int
) -> tuple[np.ndarray, np.ndarray]:
    from scipy.stats import norm

    lower, upper = 1.0 / (2 * n), 1.0 - 1.0 / (2 * n)
    hit = np.clip(np.asarray(hit_count, dtype=float) / n, lower, upper)
    false_alarm = np.clip(np.asarray(false_alarm_count, dtype=float) / n, lower, upper)
    z_hit, z_false_alarm = norm.ppf(hit), norm.ppf(false_alarm)
    return z_hit - z_false_alarm, -0.5 * (z_hit + z_false_alarm)


def _assert_count_rate(count: np.ndarray, rate: np.ndarray, n: int) -> None:
    if not np.issubdtype(count.dtype, np.integer):
        raise ValueError("response counts must be integer arrays")
    if np.any((count < 0) | (count > n)):
        raise ValueError("response counts are outside the trial range")
    np.testing.assert_allclose(rate, count / n, rtol=0.0, atol=1e-12)


def validate_shard_payload(payload: object, spec: CheckpointSpec) -> dict[str, object]:
    """Fail closed unless one matched-width result shard satisfies the full contract."""
    keys = set(payload.files) if hasattr(payload, "files") else set(payload)  # type: ignore[arg-type]
    expected_keys = expected_shard_keys()
    if keys != expected_keys:
        raise ValueError(
            f"matched-width shard key inventory mismatch; missing={sorted(expected_keys - keys)}, "
            f"unmanifested={sorted(keys - expected_keys)}"
        )

    metadata = json.loads(str(np.asarray(payload["metadata_json"]).item()))  # type: ignore[index]
    expected_metadata = {
        "task": spec.task,
        "feedback": spec.feedback,
        "width": spec.width,
        "checkpoint_path": str(spec.path.resolve()),
        "checkpoint_sha256": spec.sha256,
        "checkpoint_iteration": 19999,
        "protocol": json.loads(json.dumps(protocol_for(spec))),
    }
    for field, expected in expected_metadata.items():
        if metadata.get(field) != expected:
            raise ValueError(f"matched-width shard metadata {field} mismatch")
    source_hashes = metadata.get("source_hashes")
    if not isinstance(source_hashes, dict) or not source_hashes:
        raise ValueError("matched-width shard must bind non-empty source hashes")
    if any(not isinstance(value, str) or len(value) != 64 for value in source_hashes.values()):
        raise ValueError("matched-width shard source hashes must be SHA-256 strings")
    runtime = metadata.get("runtime")
    runtime_fields = {"python", "numpy", "torch", "scipy", "sklearn", "device"}
    if (
        not isinstance(runtime, dict)
        or set(runtime) != runtime_fields
        or any(not isinstance(value, str) or not value for value in runtime.values())
    ):
        raise ValueError("matched-width shard runtime metadata violates the contract")

    np.testing.assert_allclose(payload["displayed_validities"], DISPLAYED_VALIDITIES)  # type: ignore[index]
    np.testing.assert_allclose(payload["change_magnitudes"], CHANGE_MAGNITUDES)  # type: ignore[index]
    np.testing.assert_allclose(payload["clamp_dose_parameters"], CLAMP_DOSE_PARAMETERS)  # type: ignore[index]
    np.testing.assert_allclose(payload["clamp_key_logit_biases"], CLAMP_KEY_LOGIT_BIASES)  # type: ignore[index]
    invalid_defined = bool(protocol_for(spec)["invalid_defined"])
    psych_shape = (len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES))
    trials = PSYCHOMETRIC_TRIALS_PER_POINT

    valid_count = np.asarray(payload["psychometric_response_count_valid"])  # type: ignore[index]
    valid_rate = np.asarray(payload["psychometric_response_rate_valid"], dtype=float)  # type: ignore[index]
    valid_hist = np.asarray(payload["psychometric_press_histogram_valid"])  # type: ignore[index]
    if valid_count.shape != psych_shape or valid_hist.shape != psych_shape + (8,):
        raise ValueError("valid psychometric array shape mismatch")
    if np.any(valid_hist < 0) or np.any(valid_hist.sum(axis=-1) != trials):
        raise ValueError("valid psychometric histograms must contain exactly all trials")
    np.testing.assert_array_equal(valid_count, valid_hist[..., 6:].sum(axis=-1))
    _assert_count_rate(valid_count, valid_rate, trials)

    invalid_count = np.asarray(payload["psychometric_response_count_invalid"])  # type: ignore[index]
    invalid_rate = np.asarray(payload["psychometric_response_rate_invalid"], dtype=float)  # type: ignore[index]
    invalid_hist = np.asarray(payload["psychometric_press_histogram_invalid"])  # type: ignore[index]
    if invalid_count.shape != psych_shape or invalid_hist.shape != psych_shape + (8,):
        raise ValueError("invalid psychometric array shape mismatch")
    if invalid_defined:
        if np.any(invalid_hist < 0) or np.any(invalid_hist.sum(axis=-1) != trials):
            raise ValueError("invalid psychometric histograms must contain exactly all trials")
        np.testing.assert_array_equal(invalid_count, invalid_hist[..., 6:].sum(axis=-1))
        _assert_count_rate(invalid_count, invalid_rate, trials)
    elif not (
        np.all(invalid_count == -1)
        and np.isnan(invalid_rate).all()
        and np.all(invalid_hist == -1)
    ):
        raise ValueError("singleton-task invalid psychometric fields must be explicitly undefined")

    nochange_count = np.asarray(payload["psychometric_nochange_response_count"])  # type: ignore[index]
    nochange_rate = np.asarray(payload["psychometric_nochange_response_rate"], dtype=float)  # type: ignore[index]
    nochange_hist = np.asarray(payload["psychometric_nochange_press_histogram"])  # type: ignore[index]
    nochange_shape = (len(DISPLAYED_VALIDITIES),)
    if nochange_count.shape != nochange_shape or nochange_hist.shape != nochange_shape + (8,):
        raise ValueError("no-change psychometric array shape mismatch")
    if np.any(nochange_hist < 0) or np.any(nochange_hist.sum(axis=-1) != trials):
        raise ValueError("no-change histograms must contain exactly all trials")
    np.testing.assert_array_equal(nochange_count, nochange_hist[..., 6:].sum(axis=-1))
    _assert_count_rate(nochange_count, nochange_rate, trials)

    change_index = np.asarray(payload["decoder_sample_change_index"])  # type: ignore[index]
    if change_index.shape != (DECODER_N,) or not np.issubdtype(change_index.dtype, np.integer):
        raise ValueError("decoder sample change-index contract mismatch")
    for name in SAMPLE_LABELS:
        labels = np.asarray(payload[f"decoder_sample_label_{name}"])  # type: ignore[index]
        if labels.shape != (DECODER_N,) or not np.issubdtype(labels.dtype, np.integer):
            raise ValueError(f"decoder sample labels for {name} violate the contract")
    for name in DECODED_VARIABLES:
        defined = name not in ("change_location", "cued_change") or invalid_defined
        fold_ids = np.asarray(payload[f"decoder_fold_id_{name}"])  # type: ignore[index]
        if fold_ids.shape != (DECODER_N,) or not np.issubdtype(fold_ids.dtype, np.integer):
            raise ValueError(f"decoder fold IDs for {name} violate the contract")
        if np.any((fold_ids < -1) | (fold_ids >= 4)):
            raise ValueError(f"decoder fold IDs for {name} are outside [-1, 3]")
        for space in ("native", "matched128"):
            scores = np.asarray(payload[f"decoder_{space}_{name}"], dtype=float)  # type: ignore[index]
            if scores.shape != (7,):
                raise ValueError(f"decoder {space}/{name} shape mismatch")
            if defined:
                if not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
                    raise ValueError(f"decoder {space}/{name} scores must be finite probabilities")
            elif not np.isnan(scores).all() or not np.all(fold_ids == -1):
                raise ValueError(f"decoder {space}/{name} must be explicitly undefined")

    clamp_n = CLAMP_TRIALS
    clamp_shape = (len(CLAMP_DOSE_PARAMETERS),)
    histogram_shape = clamp_shape + (8,)
    valid_histogram = np.asarray(payload["clamp_press_histogram_valid"])  # type: ignore[index]
    invalid_histogram = np.asarray(payload["clamp_press_histogram_invalid"])  # type: ignore[index]
    nochange_histogram = np.asarray(payload["clamp_press_histogram_nochange"])  # type: ignore[index]
    if valid_histogram.shape != histogram_shape or nochange_histogram.shape != histogram_shape:
        raise ValueError("clamp press-histogram shape mismatch")
    if (
        not np.issubdtype(valid_histogram.dtype, np.integer)
        or not np.issubdtype(nochange_histogram.dtype, np.integer)
        or np.any(valid_histogram < 0)
        or np.any(nochange_histogram < 0)
        or np.any(valid_histogram.sum(axis=-1) != clamp_n)
        or np.any(nochange_histogram.sum(axis=-1) != clamp_n)
    ):
        raise ValueError("defined clamp histograms must preserve exactly all trials")
    false_alarm_count = np.asarray(payload["clamp_false_alarm_count"])  # type: ignore[index]
    false_alarm_rate = np.asarray(payload["clamp_false_alarm_rate"], dtype=float)  # type: ignore[index]
    if false_alarm_count.shape != clamp_shape:
        raise ValueError("clamp false-alarm shape mismatch")
    np.testing.assert_array_equal(false_alarm_count, nochange_histogram[:, 1:].sum(axis=-1))
    _assert_count_rate(false_alarm_count, false_alarm_rate, clamp_n)
    for condition in ("valid", "invalid"):
        hit_count = np.asarray(payload[f"clamp_hit_count_{condition}"])  # type: ignore[index]
        hit_rate = np.asarray(payload[f"clamp_hit_rate_{condition}"], dtype=float)  # type: ignore[index]
        dprime = np.asarray(payload[f"clamp_dprime_{condition}"], dtype=float)  # type: ignore[index]
        criterion = np.asarray(payload[f"clamp_criterion_{condition}"], dtype=float)  # type: ignore[index]
        if hit_count.shape != clamp_shape or dprime.shape != clamp_shape or criterion.shape != clamp_shape:
            raise ValueError(f"clamp {condition} array shape mismatch")
        if condition == "invalid" and not invalid_defined:
            if not (
                np.all(hit_count == -1)
                and invalid_histogram.shape == histogram_shape
                and np.issubdtype(invalid_histogram.dtype, np.integer)
                and np.all(invalid_histogram == -1)
                and np.isnan(hit_rate).all()
                and np.isnan(dprime).all()
                and np.isnan(criterion).all()
            ):
                raise ValueError("singleton-task invalid clamp fields must be explicitly undefined")
            continue
        histogram = valid_histogram if condition == "valid" else invalid_histogram
        if (
            histogram.shape != histogram_shape
            or not np.issubdtype(histogram.dtype, np.integer)
            or np.any(histogram < 0)
            or np.any(histogram.sum(axis=-1) != clamp_n)
        ):
            raise ValueError(f"clamp {condition} histogram must preserve exactly all trials")
        np.testing.assert_array_equal(hit_count, histogram[:, 6:].sum(axis=-1))
        _assert_count_rate(hit_count, hit_rate, clamp_n)
        expected_dprime, expected_criterion = _sdt_from_counts(
            hit_count, false_alarm_count, clamp_n
        )
        np.testing.assert_allclose(dprime, expected_dprime, rtol=0.0, atol=1e-12)
        np.testing.assert_allclose(criterion, expected_criterion, rtol=0.0, atol=1e-12)
    return metadata


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_checkpoint_registry() -> list[dict[str, object]]:
    import torch

    records: list[dict[str, object]] = []
    identities: set[tuple[int, int]] = set()
    for spec in admissible_specs():
        path = spec.path.resolve()
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"registered checkpoint is not a regular file: {path}")
        metadata = path.stat()
        identity = (metadata.st_dev, metadata.st_ino)
        if identity in identities:
            raise RuntimeError(f"registered checkpoints alias one inode: {path}")
        identities.add(identity)
        digest = sha256_file(path)
        if digest != spec.sha256:
            raise RuntimeError(f"registered checkpoint SHA-256 mismatch: {path}")
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        iteration = int(checkpoint.get("iter", -1))
        if iteration != 19999:
            raise RuntimeError(f"registered checkpoint iteration is {iteration}, expected 19999: {path}")
        records.append(
            {
                "task": spec.task,
                "feedback": spec.feedback,
                "width": spec.width,
                "path": str(path),
                "sha256": digest,
                "bytes": metadata.st_size,
                "device": metadata.st_dev,
                "inode": metadata.st_ino,
                "nlink": metadata.st_nlink,
                "iteration": iteration,
                "grid": list(spec.grid),
                "image_size": spec.image_size,
                "active_locations": list(spec.active_locations),
            }
        )
    return records
