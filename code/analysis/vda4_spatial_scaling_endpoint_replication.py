"""Build an immutable two-seed VDA4 cross-attention endpoint synthesis.

The producer is intentionally a cached-artifact consumer: it never loads a
training checkpoint and never executes the model.  It verifies the complete
held-out evaluation bundles for cross-attention 2x2 and 10x10 at seeds 0 and 1,
recomputes the registered endpoint metrics from their hash-bound NPZ caches,
and atomically publishes a comparison bundle.  With only two training seeds,
the output is restricted to seedwise directions and descriptive dispersion;
it does not report confidence intervals, p-values, or population estimates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np


VALIDITIES = np.asarray([0.25, 0.50, 0.75, 1.00], dtype=np.float64)
MAGNITUDES = np.asarray([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0], dtype=np.float64)
GRIDS = ((2, 2), (10, 10))
SEEDS = (0, 1)
EXPLICIT_MODES = ("natural", "uniform", "shuffle", "disable")
REQUIRED_ARTIFACTS = {
    "analysis_config.json",
    "SUMMARY.json",
    "data/psychometrics.npz",
    "data/event_attention.npz",
    "data/interventions.npz",
    "tables/psychometrics.csv",
    "tables/regional_interventions.csv",
    "figures/valid_invalid_response_rt.pdf",
    "figures/valid_invalid_response_rt.png",
    "figures/event_attention_maps.pdf",
    "figures/event_attention_maps.png",
    "figures/regional_causal_intervention.pdf",
    "figures/regional_causal_intervention.png",
}
HEX64 = re.compile(r"[0-9a-f]{64}")
SOURCE_NAME = re.compile(r"vda4_crossattn1_grid(2x2|10x10)_seed([01])")
ANALYSIS_NAME = "cached-artifact-only VDA4 cross-attention endpoint replication synthesis"
METRICS_FILENAME = "vda4_spatial_scaling_endpoint_replication_metrics.csv"
FIGURE_BASENAME = "vda4_spatial_scaling_endpoint_replication_summary"

CSV_FIELDS = (
    "feedback",
    "model",
    "grid",
    "n_tokens",
    "seed",
    "displayed_validity",
    "valid_threshold_deg",
    "invalid_threshold_deg",
    "threshold_cost_invalid_minus_valid_deg",
    "normalized_response_auc_valid_minus_invalid",
    "rt30_invalid_minus_valid_frames",
    "valid_tl_region0_mass_frames5_6",
    "invalid_br_region3_mass_frames5_6",
    "invalid_tl_region0_mass_frames5_6",
    "invalid_reorienting_br_minus_tl_mass_frames5_6",
    "explicit_natural_invalid_response_rate",
    "explicit_uniform_invalid_response_rate",
    "explicit_shuffle_invalid_response_rate",
    "explicit_disable_invalid_response_rate",
    "causal_dependence_natural_minus_disable_pp",
    "source_manifest_sha256",
)

DELTA_METRICS = (
    "threshold_cost_invalid_minus_valid_deg",
    "normalized_response_auc_valid_minus_invalid",
    "rt30_invalid_minus_valid_frames",
    "valid_tl_region0_mass_frames5_6",
    "invalid_br_region3_mass_frames5_6",
    "invalid_tl_region0_mass_frames5_6",
    "causal_dependence_natural_minus_disable_pp",
)


@dataclass(frozen=True)
class Source:
    directory: Path
    label: str
    rows: int
    cols: int
    n_tokens: int
    seed: int
    manifest: dict[str, Any]
    manifest_sha256: str
    manifest_bytes: int
    artifacts: dict[str, dict[str, Any]]
    config: dict[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot parse JSON {path}: {exc}") from exc
    require(isinstance(value, dict), f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(jsonable(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float):
        require(math.isfinite(value), "refusing to serialize a non-finite float")
    return value


def finite_array(value: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(value)
    require(np.issubdtype(array.dtype, np.number), f"{name} is not numeric")
    require(bool(np.all(np.isfinite(array))), f"{name} contains non-finite values")
    return array


def scalar(value: np.ndarray, name: str) -> Any:
    array = np.asarray(value)
    require(array.ndim == 0, f"{name} is not scalar")
    return array.item()


def source_label(rows: int, cols: int, seed: int) -> str:
    return f"vda4_crossattn1_grid{rows}x{cols}_seed{seed}"


def expected_source_labels() -> list[str]:
    return [source_label(rows, cols, seed) for seed in SEEDS for rows, cols in GRIDS]


def expected_region_tokens(rows: int, cols: int) -> list[list[int]]:
    regions: list[list[int]] = []
    for location in range(4):
        task_row, task_col = divmod(location, 2)
        row_start, row_stop = task_row * (rows // 2), (task_row + 1) * (rows // 2)
        col_start, col_stop = task_col * (cols // 2), (task_col + 1) * (cols // 2)
        regions.append([r * cols + c for r in range(row_start, row_stop) for c in range(col_start, col_stop)])
    return regions


def safe_artifact_path(source_dir: Path, key: str) -> Path:
    require("\\" not in key, f"manifest artifact key is not canonical POSIX: {key!r}")
    relative = PurePosixPath(key)
    require(
        not relative.is_absolute() and ".." not in relative.parts and "." not in relative.parts,
        f"unsafe manifest artifact path: {key!r}",
    )
    path = source_dir.joinpath(*relative.parts)
    resolved_root = source_dir.resolve()
    resolved = path.resolve()
    require(resolved_root in resolved.parents, f"artifact escapes source directory: {key!r}")
    require(path.is_file() and not path.is_symlink(), f"artifact is missing or not a regular file: {path}")
    return path


def _expected_model(rows: int, cols: int, seed: int) -> dict[str, Any]:
    return {
        "label": source_label(rows, cols, seed),
        "task": "vda4",
        "feedback": "crossattn1",
        "grid_rows": rows,
        "grid_cols": cols,
        "n_tokens": rows * cols,
        "checkpoint_iteration": 19999,
    }


def validate_source(directory: Path, rows: int, cols: int, seed: int) -> Source:
    label = source_label(rows, cols, seed)
    require(directory.name == label and bool(SOURCE_NAME.fullmatch(directory.name)),
            f"unexpected source directory name: {directory.name}")
    manifest_path = directory / "MANIFEST.json"
    require(manifest_path.is_file() and not manifest_path.is_symlink(), f"missing source manifest: {manifest_path}")
    manifest = read_json(manifest_path)
    require(manifest.get("schema_version") == 1, f"{label}: unsupported manifest schema")
    require(manifest.get("status") == "complete", f"{label}: source manifest is not complete")
    require(manifest.get("config_path") == "analysis_config.json", f"{label}: unexpected config path")
    require(manifest.get("summary_path") == "SUMMARY.json", f"{label}: unexpected summary path")

    model = manifest.get("model")
    require(isinstance(model, dict), f"{label}: missing manifest model metadata")
    expected_model = _expected_model(rows, cols, seed)
    for key, expected in expected_model.items():
        require(model.get(key) == expected, f"{label}: model.{key}={model.get(key)!r}, expected {expected!r}")
    for key in ("checkpoint_sha256", "producer_sha256"):
        value = str(model.get(key, "")).lower()
        require(bool(HEX64.fullmatch(value)), f"{label}: invalid model.{key}")

    declared = manifest.get("artifact_hashes")
    require(isinstance(declared, dict), f"{label}: artifact_hashes is not an object")
    declared_keys = set(declared)
    require(declared_keys == REQUIRED_ARTIFACTS,
            f"{label}: artifact contract mismatch; missing={sorted(REQUIRED_ARTIFACTS-declared_keys)}, extra={sorted(declared_keys-REQUIRED_ARTIFACTS)}")
    actual_keys = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    require(actual_keys == declared_keys,
            f"{label}: manifest/file coverage mismatch; undeclared={sorted(actual_keys-declared_keys)}, missing={sorted(declared_keys-actual_keys)}")

    artifacts: dict[str, dict[str, Any]] = {}
    for key in sorted(declared):
        expected_sha = str(declared[key]).lower()
        require(bool(HEX64.fullmatch(expected_sha)), f"{label}: invalid SHA-256 for {key}")
        path = safe_artifact_path(directory, key)
        actual_sha = sha256_file(path)
        require(actual_sha == expected_sha, f"{label}: SHA-256 mismatch for {key}: {actual_sha} != {expected_sha}")
        artifacts[key] = {"sha256": actual_sha, "bytes": path.stat().st_size}

    config = read_json(directory / "analysis_config.json")
    summary = read_json(directory / "SUMMARY.json")
    for document_name, document in (("analysis_config", config), ("SUMMARY", summary)):
        document_model = document if document_name == "analysis_config" else document.get("model")
        require(isinstance(document_model, dict), f"{label}: {document_name} lacks model metadata")
        for key, expected in expected_model.items():
            require(document_model.get(key) == expected,
                    f"{label}: {document_name}.{key} does not match manifest")
        for key in ("checkpoint_sha256", "producer_sha256"):
            require(document_model.get(key) == model.get(key),
                    f"{label}: {document_name} {key} mismatch")

    require(config.get("psychometric_trials") == 300, f"{label}: expected 300 psychometric trials")
    require(config.get("attention_trials") == 128, f"{label}: expected 128 attention trials")
    require(config.get("intervention_trials") == 250, f"{label}: expected 250 intervention trials")
    require(config.get("validities") == VALIDITIES.tolist(), f"{label}: validity grid mismatch")
    require(config.get("magnitudes") == MAGNITUDES.tolist(), f"{label}: magnitude grid mismatch")
    require(config.get("focal_validity") == 1.0 and config.get("focal_magnitude") == 30.0,
            f"{label}: focal condition mismatch")
    require(config.get("qualifying_frames") == [5, 6], f"{label}: qualifying frames mismatch")
    require(config.get("region_tokens") == expected_region_tokens(rows, cols), f"{label}: region-token map mismatch")
    require(config.get("regional_uniform_baseline") == 0.25, f"{label}: regional baseline mismatch")
    producer_map = config.get("checkpoint_producer_sha256")
    require(isinstance(producer_map, dict) and bool(producer_map), f"{label}: missing checkpoint producer provenance")
    require(all(isinstance(value, str) and HEX64.fullmatch(value.lower()) for value in producer_map.values()),
            f"{label}: invalid checkpoint producer provenance hash")
    require(summary.get("schema_version") == 1, f"{label}: unsupported SUMMARY schema")
    require(summary.get("training_is_not_scientific_validation") is True,
            f"{label}: SUMMARY evidence-boundary marker missing")

    return Source(
        directory=directory,
        label=label,
        rows=rows,
        cols=cols,
        n_tokens=rows * cols,
        seed=seed,
        manifest=manifest,
        manifest_sha256=sha256_file(manifest_path),
        manifest_bytes=manifest_path.stat().st_size,
        artifacts=artifacts,
        config=config,
    )


def validate_sources(production_root: Path) -> list[Source]:
    labels = expected_source_labels()
    missing = [label for label in labels if not (production_root / label).is_dir()]
    require(not missing, f"missing required endpoint evaluation directories: {missing}")
    sources = [
        validate_source(production_root / source_label(rows, cols, seed), rows, cols, seed)
        for seed in SEEDS
        for rows, cols in GRIDS
    ]
    require(len(sources) == 4 and {source.label for source in sources} == set(labels),
            "endpoint source-set guard failed")
    require(len({source.manifest["model"]["checkpoint_sha256"] for source in sources}) == 4,
            "the endpoint evaluations do not reference four distinct checkpoints")
    require(len({source.manifest["model"]["producer_sha256"] for source in sources}) == 1,
            "the endpoint evaluations were not generated by one evaluator source hash")
    return sources


def validate_npz_metadata(data: dict[str, np.ndarray], source: Source, cache_name: str) -> None:
    model = source.manifest["model"]
    expected = {
        "meta_label": source.label,
        "meta_task": "vda4",
        "meta_feedback": "crossattn1",
        "meta_grid_rows": source.rows,
        "meta_grid_cols": source.cols,
        "meta_n_tokens": source.n_tokens,
        "meta_checkpoint_iteration": 19999,
        "meta_checkpoint_sha256": model["checkpoint_sha256"],
        "meta_producer_sha256": model["producer_sha256"],
    }
    for key, expected_value in expected.items():
        require(key in data, f"{source.label}/{cache_name}: missing {key}")
        actual = scalar(data[key], f"{source.label}/{cache_name}/{key}")
        require(actual == expected_value,
                f"{source.label}/{cache_name}: {key}={actual!r}, expected {expected_value!r}")


def load_npz(path: Path) -> dict[str, np.ndarray]:
    # This function is called only after every source artifact hash is verified.
    with np.load(path, allow_pickle=False) as archive:
        return {key: archive[key] for key in archive.files}


def validate_and_load_caches(
    source: Source,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    psych = load_npz(source.directory / "data" / "psychometrics.npz")
    attention = load_npz(source.directory / "data" / "event_attention.npz")
    interventions = load_npz(source.directory / "data" / "interventions.npz")
    for cache_name, data in (("psychometrics", psych), ("event_attention", attention), ("interventions", interventions)):
        validate_npz_metadata(data, source, cache_name)

    trials_psych, trials_attention, trials_intervention = 300, 128, 250
    require(psych["response_count"].shape == (4, 10, 2), f"{source.label}: psychometric count shape")
    require(psych["response_rate"].shape == (4, 10, 2), f"{source.label}: psychometric rate shape")
    require(psych["mean_rt"].shape == (4, 10, 2), f"{source.label}: psychometric RT shape")
    require(psych["press_histogram"].shape == (4, 10, 2, 8), f"{source.label}: psychometric histogram shape")
    counts = finite_array(psych["response_count"], f"{source.label}/response_count")
    rates = finite_array(psych["response_rate"], f"{source.label}/response_rate")
    require(bool(np.all((rates >= 0.0) & (rates <= 1.0))), f"{source.label}: response rate outside [0,1]")
    require(bool(np.allclose(rates, counts / trials_psych, atol=1e-12)),
            f"{source.label}: response count/rate mismatch")
    require(bool(np.all(psych["press_histogram"].sum(axis=-1) == trials_psych)),
            f"{source.label}: psychometric histograms do not sum to trials")
    finite_array(psych["false_alarm_rate"], f"{source.label}/false_alarm_rate")
    finite_array(psych["dprime"], f"{source.label}/dprime")
    finite_array(psych["criterion"], f"{source.label}/criterion")
    require(bool(np.all(np.isfinite(psych["mean_rt"][:, -1, :]))), f"{source.label}: non-finite 30-degree RT")

    require(attention["press"].shape == (2, trials_attention), f"{source.label}: attention press shape")
    require(attention["token_mass"].shape == (2, trials_attention, 7, source.n_tokens),
            f"{source.label}: token-mass shape")
    require(attention["region_mass"].shape == (2, trials_attention, 7, 4),
            f"{source.label}: region-mass shape")
    expected_keys = source.n_tokens * 2
    require(attention["raw_attention_mean"].shape == (2, 7, source.n_tokens, expected_keys),
            f"{source.label}: raw-attention shape")
    token_mass = finite_array(attention["token_mass"], f"{source.label}/token_mass")
    region_mass = finite_array(attention["region_mass"], f"{source.label}/region_mass")
    finite_array(attention["raw_attention_mean"], f"{source.label}/raw_attention_mean")
    require(bool(np.allclose(token_mass.sum(axis=-1), 1.0, atol=2e-5)),
            f"{source.label}: token mass is not normalized")
    require(bool(np.allclose(region_mass.sum(axis=-1), 1.0, atol=2e-5)),
            f"{source.label}: region mass is not normalized")
    rebuilt = np.stack(
        [token_mass[..., tokens].sum(axis=-1) for tokens in expected_region_tokens(source.rows, source.cols)],
        axis=-1,
    )
    require(bool(np.allclose(region_mass, rebuilt, atol=2e-5)),
            f"{source.label}: cached regional mass does not match token mass")

    require(interventions["response_count"].shape == (3, 5, 3), f"{source.label}: intervention count shape")
    require(interventions["response_rate"].shape == (3, 5, 3), f"{source.label}: intervention rate shape")
    require(interventions["explicit_response_count"].shape == (4, 3), f"{source.label}: explicit count shape")
    require(interventions["explicit_response_rate"].shape == (4, 3), f"{source.label}: explicit rate shape")
    modes = tuple(str(value) for value in interventions["explicit_modes"].tolist())
    require(modes == EXPLICIT_MODES, f"{source.label}: explicit intervention modes/order mismatch")
    regional_counts = finite_array(interventions["response_count"], f"{source.label}/intervention_count")
    regional_rates = finite_array(interventions["response_rate"], f"{source.label}/intervention_rate")
    explicit_counts = finite_array(interventions["explicit_response_count"], f"{source.label}/explicit_count")
    explicit_rates = finite_array(interventions["explicit_response_rate"], f"{source.label}/explicit_rate")
    require(bool(np.allclose(regional_rates, regional_counts / trials_intervention, atol=1e-12)),
            f"{source.label}: regional intervention count/rate mismatch")
    require(bool(np.allclose(explicit_rates, explicit_counts / trials_intervention, atol=1e-12)),
            f"{source.label}: explicit intervention count/rate mismatch")
    require(bool(np.all(interventions["press_histogram"].sum(axis=-1) == trials_intervention)),
            f"{source.label}: intervention histograms do not sum to trials")
    require(bool(np.all(interventions["explicit_press_histogram"].sum(axis=-1) == trials_intervention)),
            f"{source.label}: explicit histograms do not sum to trials")
    finite_array(interventions["achieved_change_region_mass"], f"{source.label}/achieved_change_region_mass")
    finite_array(interventions["achieved_target_region_mass"], f"{source.label}/achieved_target_region_mass")
    finite_array(interventions["explicit_dprime"], f"{source.label}/explicit_dprime")
    finite_array(interventions["explicit_criterion"], f"{source.label}/explicit_criterion")
    permutation = finite_array(interventions["shuffle_permutation"], f"{source.label}/shuffle_permutation")
    require(permutation.shape == (source.n_tokens * 2,), f"{source.label}: shuffle permutation length")
    require(sorted(permutation.astype(int).tolist()) == list(range(source.n_tokens * 2)),
            f"{source.label}: shuffle array is not a permutation")
    return psych, attention, interventions


def monotone_threshold(magnitudes: np.ndarray, rates: np.ndarray, target: float = 0.5) -> float:
    x = finite_array(magnitudes, "threshold magnitudes").astype(np.float64)
    y = finite_array(rates, "threshold response rates").astype(np.float64)
    require(x.ndim == y.ndim == 1 and x.size == y.size and x.size >= 2, "invalid threshold inputs")
    require(bool(np.all(np.diff(x) > 0.0)), "threshold magnitudes are not strictly increasing")
    envelope = np.maximum.accumulate(y)
    crossings = np.flatnonzero(envelope >= target)
    require(crossings.size > 0, "monotone response envelope does not reach the 0.5 threshold")
    index = int(crossings[0])
    if index == 0:
        require(math.isclose(float(envelope[0]), target, abs_tol=1e-12), "0.5 threshold is left-censored")
        return float(x[0])
    lo_y, hi_y = float(envelope[index - 1]), float(envelope[index])
    require(hi_y > lo_y, "0.5 threshold crossing is not identifiable")
    return float(x[index - 1] + (target - lo_y) * (x[index] - x[index - 1]) / (hi_y - lo_y))


def _trapezoid(values: np.ndarray, x: np.ndarray) -> float:
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(values, x=x))
    return float(np.trapz(values, x=x))  # pragma: no cover - NumPy < 2 compatibility


def compute_endpoint_rows(sources: list[Source]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in sources:
        psych, attention, interventions = validate_and_load_caches(source)
        response = psych["response_rate"].astype(np.float64)
        mean_rt = psych["mean_rt"].astype(np.float64)
        region_mass = attention["region_mass"].astype(np.float64)
        explicit = interventions["explicit_response_rate"].astype(np.float64)
        validity_index = int(np.flatnonzero(np.isclose(VALIDITIES, 1.0))[0])
        valid_threshold = monotone_threshold(MAGNITUDES, response[validity_index, :, 0])
        invalid_threshold = monotone_threshold(MAGNITUDES, response[validity_index, :, 1])
        valid_tl = float(region_mass[0, :, 5:7, 0].mean())
        invalid_br = float(region_mass[1, :, 5:7, 3].mean())
        invalid_tl = float(region_mass[1, :, 5:7, 0].mean())
        explicit_invalid = {mode: float(explicit[index, 1]) for index, mode in enumerate(EXPLICIT_MODES)}
        row = {
            "feedback": "crossattn1",
            "model": "Cross-attention",
            "grid": f"{source.rows}x{source.cols}",
            "n_tokens": source.n_tokens,
            "seed": source.seed,
            "displayed_validity": 1.0,
            "valid_threshold_deg": valid_threshold,
            "invalid_threshold_deg": invalid_threshold,
            "threshold_cost_invalid_minus_valid_deg": invalid_threshold - valid_threshold,
            "normalized_response_auc_valid_minus_invalid": _trapezoid(
                response[validity_index, :, 0] - response[validity_index, :, 1], MAGNITUDES
            ) / float(MAGNITUDES[-1] - MAGNITUDES[0]),
            "rt30_invalid_minus_valid_frames": float(
                mean_rt[validity_index, -1, 1] - mean_rt[validity_index, -1, 0]
            ),
            "valid_tl_region0_mass_frames5_6": valid_tl,
            "invalid_br_region3_mass_frames5_6": invalid_br,
            "invalid_tl_region0_mass_frames5_6": invalid_tl,
            "invalid_reorienting_br_minus_tl_mass_frames5_6": invalid_br - invalid_tl,
            "explicit_natural_invalid_response_rate": explicit_invalid["natural"],
            "explicit_uniform_invalid_response_rate": explicit_invalid["uniform"],
            "explicit_shuffle_invalid_response_rate": explicit_invalid["shuffle"],
            "explicit_disable_invalid_response_rate": explicit_invalid["disable"],
            "causal_dependence_natural_minus_disable_pp": 100.0 * (
                explicit_invalid["natural"] - explicit_invalid["disable"]
            ),
            "source_manifest_sha256": source.manifest_sha256,
        }
        require(tuple(row) == CSV_FIELDS, f"internal CSV field-order contract failed for {source.label}")
        require(all(math.isfinite(value) for value in row.values() if isinstance(value, float)),
                f"computed non-finite endpoint metric for {source.label}")
        rows.append(row)
    rows.sort(key=lambda row: (int(row["seed"]), int(row["n_tokens"])))
    require(len(rows) == 4, f"expected four endpoint rows, got {len(rows)}")
    return rows


def compute_seedwise_deltas(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    for seed in SEEDS:
        seed_rows = {int(row["n_tokens"]): row for row in rows if int(row["seed"]) == seed}
        require(set(seed_rows) == {4, 100}, f"seed {seed}: expected 4- and 100-token endpoint rows")
        delta: dict[str, Any] = {
            "seed": seed,
            "from_grid": "2x2",
            "to_grid": "10x10",
            "from_tokens": 4,
            "to_tokens": 100,
        }
        for metric in DELTA_METRICS:
            value = float(seed_rows[100][metric]) - float(seed_rows[4][metric])
            require(math.isfinite(value), f"seed {seed}: non-finite delta for {metric}")
            delta[f"delta_10x10_minus_2x2_{metric}"] = value
        deltas.append(delta)
    return deltas


def direction(value: float, tolerance: float = 1e-12) -> str:
    if value > tolerance:
        return "increase"
    if value < -tolerance:
        return "decrease"
    return "no_change"


def summarize_delta_dispersion(deltas: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    require(len(deltas) == 2 and [int(item["seed"]) for item in deltas] == [0, 1],
            "descriptive replication requires exactly seeds 0 and 1")
    result: dict[str, dict[str, Any]] = {}
    for metric in DELTA_METRICS:
        key = f"delta_10x10_minus_2x2_{metric}"
        values = np.asarray([float(item[key]) for item in deltas], dtype=np.float64)
        finite_array(values, f"seedwise deltas/{metric}")
        directions = [direction(float(value)) for value in values]
        agreed = directions[0] == directions[1]
        result[metric] = {
            "n_training_seeds": 2,
            "seedwise_deltas_10x10_minus_2x2": {"seed0": float(values[0]), "seed1": float(values[1])},
            "direction_by_seed": {"seed0": directions[0], "seed1": directions[1]},
            "directional_agreement": agreed,
            "shared_direction": directions[0] if agreed else "discordant",
            "mean_delta_descriptive_only": float(values.mean()),
            "minimum_delta": float(values.min()),
            "maximum_delta": float(values.max()),
            "range_across_two_seed_deltas": float(np.ptp(values)),
            "sample_standard_deviation_across_two_seed_deltas": float(values.std(ddof=1)),
            "evidence_class": "directional_and_dispersion_only_n_equals_2",
        }
    return result


def directional_findings(summary: dict[str, dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    for metric in DELTA_METRICS:
        item = summary[metric]
        if item["directional_agreement"]:
            findings.append(
                f"For {metric}, both observed seeds show {item['shared_direction']} from 2x2 to 10x10; "
                "this is directional replication across two checkpoints, not a population estimate."
            )
        else:
            findings.append(
                f"For {metric}, the two observed seeds have discordant endpoint directions; "
                "the endpoint effect does not directionally replicate in this two-seed sample."
            )
    return findings


def write_metrics(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_FIELDS))
        writer.writeheader()
        for row in rows:
            # Preserve enough significant digits for an exact binary64
            # round-trip.  Twelve digits shifted real float32-derived source
            # values by several e-9, exceeding the independent verifier's
            # registered comparison tolerance.
            writer.writerow({key: format(value, ".17g") if isinstance(value, float) else value for key, value in row.items()})


def configure_plots() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.8,
        "axes.titlesize": 9.5,
        "axes.labelsize": 8.8,
        "xtick.labelsize": 8.2,
        "ytick.labelsize": 8.2,
        "legend.fontsize": 7.6,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.8,
        "lines.markersize": 5.5,
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    return plt


def plot_summary(path_stem: Path, rows: list[dict[str, Any]]) -> None:
    plt = configure_plots()
    figure, axes = plt.subplots(2, 3, figsize=(7.25, 6.1))
    figure.suptitle("VDA4 cross-attention endpoint replication (held-out seeds 0 and 1)",
                    fontsize=11.5, fontweight="bold", y=0.985)
    seed_styles = {
        0: {"label": "seed 0", "color": "#2F6FB0", "marker": "o"},
        1: {"label": "seed 1", "color": "#D06449", "marker": "s"},
    }
    panels = (
        ("threshold_cost_invalid_minus_valid_deg", "A  50% threshold cost", "invalid - valid (deg)"),
        ("normalized_response_auc_valid_minus_invalid", "B  Response AUC gap", "valid - invalid AUC"),
        ("rt30_invalid_minus_valid_frames", "C  RT cost at 30 deg", "invalid - valid (frames)"),
        ("valid_tl_region0_mass_frames5_6", "D  Valid change localization", "TL regional mass"),
        ("invalid_br_region3_mass_frames5_6", "E  Invalid change localization", "regional mass"),
        ("causal_dependence_natural_minus_disable_pp", "F  Invalid-response dependence", "natural - disable (pp)"),
    )
    for axis, (metric, title, ylabel) in zip(axes.flat, panels):
        for seed in SEEDS:
            subset = sorted((row for row in rows if int(row["seed"]) == seed), key=lambda row: int(row["n_tokens"]))
            style = seed_styles[seed]
            axis.plot(
                [row["n_tokens"] for row in subset],
                [row[metric] for row in subset],
                label=style["label"], color=style["color"], marker=style["marker"],
            )
            if metric == "invalid_br_region3_mass_frames5_6":
                axis.plot(
                    [row["n_tokens"] for row in subset],
                    [row["invalid_tl_region0_mass_frames5_6"] for row in subset],
                    color=style["color"], marker=style["marker"], markerfacecolor="white",
                    linestyle="--", linewidth=1.35,
                )
        axis.set_title(title, loc="left", fontweight="bold")
        axis.set_ylabel(ylabel)
        axis.set_xscale("log")
        axis.set_xlim(3.3, 121.0)
        axis.set_xticks((4, 100), labels=("4 (2x2)", "100 (10x10)"))
        axis.set_xlabel("sensory / memory tokens")
        axis.grid(axis="y", color="#D7D7D7", linewidth=0.7)
        axis.spines[["top", "right"]].set_visible(False)
    axes[0, 0].legend(frameon=False, title="Checkpoint", title_fontsize=7.6)
    axes[1, 0].axhline(0.25, color="#666666", linewidth=1.0, linestyle=":", zorder=0)
    axes[1, 1].axhline(0.25, color="#666666", linewidth=1.0, linestyle=":", zorder=0)
    axes[1, 1].text(0.04, 0.04, "solid: BR change\ndashed/open: TL cue", transform=axes[1, 1].transAxes,
                    fontsize=7.0, color="#444444", va="bottom")
    axes[1, 2].axhline(0.0, color="#666666", linewidth=1.0, linestyle=":", zorder=0)
    figure.text(
        0.5, 0.012,
        "Lines are individual training seeds. n=2 supports directional and dispersion descriptions only; no inferential interval or population claim.",
        ha="center", va="bottom", fontsize=7.4, color="#3F4B5A",
    )
    figure.tight_layout(rect=(0.0, 0.045, 1.0, 0.955), h_pad=1.4, w_pad=1.15)
    figure.savefig(path_stem.with_suffix(".pdf"), bbox_inches="tight")
    figure.savefig(path_stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(figure)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-root", type=Path, required=True,
                        help="root containing the four complete endpoint evaluation directories")
    parser.add_argument("--output-root", type=Path,
                        help="final immutable synthesis directory (default: PRODUCTION_ROOT/endpoint_replication_s01)")
    parser.add_argument("--validate-only", action="store_true",
                        help="verify all sources and recompute metrics without creating output")
    return parser


def _guard_output_location(output_root: Path, sources: list[Source]) -> None:
    resolved = output_root.resolve()
    for source in sources:
        source_root = source.directory.resolve()
        require(resolved != source_root and source_root not in resolved.parents,
                f"output root cannot be a source evaluation or its descendant: {output_root}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    production_root = args.production_root.expanduser().resolve()
    require(production_root.is_dir(), f"production root does not exist: {production_root}")
    output_root = (
        args.output_root.expanduser().resolve()
        if args.output_root
        else production_root / "endpoint_replication_s01"
    )
    if not args.validate_only and output_root.exists():
        raise FileExistsError(f"refusing to overwrite output root: {output_root}")

    started = time.time()
    sources = validate_sources(production_root)
    rows = compute_endpoint_rows(sources)
    deltas = compute_seedwise_deltas(rows)
    dispersion = summarize_delta_dispersion(deltas)
    print(
        f"[validated] four manifests, {sum(len(source.artifacts) for source in sources)} source artifact hashes, "
        "and four endpoint metric rows",
        flush=True,
    )
    if args.validate_only:
        print("[validate-only] no output created", flush=True)
        return 0

    _guard_output_location(output_root, sources)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    # Keep staging paths short enough for the legacy Windows MAX_PATH limit.
    # The production root is already deep, and the descriptive output names are
    # long; the previous staging prefix pushed writes just past 260 characters.
    staging = output_root.parent / f".er.{uuid.uuid4().hex[:8]}"
    staging.mkdir()
    print(f"[staging] {staging}", flush=True)

    metrics_path = staging / METRICS_FILENAME
    figure_stem = staging / FIGURE_BASENAME
    write_metrics(metrics_path, rows)
    plot_summary(figure_stem, rows)

    source_evidence = [
        {
            "label": source.label,
            "seed": source.seed,
            "grid": f"{source.rows}x{source.cols}",
            "n_tokens": source.n_tokens,
            "relative_path": source.directory.relative_to(production_root).as_posix(),
            "manifest_sha256": source.manifest_sha256,
            "manifest_bytes": source.manifest_bytes,
            "checkpoint_sha256": source.manifest["model"]["checkpoint_sha256"],
            "producer_sha256": source.manifest["model"]["producer_sha256"],
            "artifacts": source.artifacts,
        }
        for source in sources
    ]
    summary = {
        "schema_version": 1,
        "status": "complete",
        "analysis": ANALYSIS_NAME,
        "scope": "crossattn1 2x2 versus 10x10 endpoint comparison across training seeds 0 and 1",
        "source_evaluation_count": 4,
        "seeds": list(SEEDS),
        "grids": ["2x2", "10x10"],
        "feedbacks": ["crossattn1"],
        "training_accuracy_used_as_attention_evidence": False,
        "seed0_synthesis_inputs_consumed_read_only": True,
        "statistical_unit": "independently trained checkpoint seed",
        "n_training_seeds": 2,
        "evidence_boundary": {
            "allowed": "seedwise direction, directional agreement, and descriptive dispersion",
            "not_supported": [
                "confidence intervals or p-values",
                "population-level replication or scaling-law claims",
                "causal isolation of token count from parameter count or spatial discretization",
            ],
        },
        "metric_definitions": {
            "threshold": "linear crossing of 0.5 on the cumulative-maximum response-rate envelope",
            "threshold_cost": "invalid threshold minus valid threshold at 100% displayed validity, degrees",
            "normalized_response_auc": "trapezoidal integral of valid minus invalid response rate over 0-30 degrees, divided by 30 degrees",
            "rt30_cost": "invalid minus valid mean qualifying response frame at 30 degrees and 100% displayed validity",
            "event_localization": "mean regional attention mass over trials and frames 5-6; valid change uses TL region 0, invalid change uses BR region 3, and invalid cue retention uses TL region 0",
            "causal_dependence": "natural minus disable invalid response rate, percentage points",
            "endpoint_delta": "10x10 value minus matched 2x2 value within one training seed",
        },
        "endpoint_metrics": rows,
        "seedwise_endpoint_deltas": deltas,
        "descriptive_replication_summary": dispersion,
        "interpretation": {
            "directional_findings": directional_findings(dispersion),
            "limitations": [
                "Only two training seeds are available, so dispersion is descriptive and inferential uncertainty is not estimable.",
                "Token count, spatial discretization, and model parameter count co-vary in this endpoint comparison.",
                "The physical VDA4 task retains four regions; this does not establish a general biological or architectural set-size law.",
                "Attention-mass differences are not themselves causal response-dependence evidence; the registered disable contrast is reported separately.",
            ],
        },
        "source_manifests": [
            {"label": source.label, "sha256": source.manifest_sha256, "bytes": source.manifest_bytes}
            for source in sources
        ],
        "all_metrics_path": metrics_path.name,
        "elapsed_seconds": time.time() - started,
    }
    summary_path = staging / "SUMMARY.json"
    write_json(summary_path, summary)

    outputs: dict[str, dict[str, Any]] = {}
    for path in sorted(staging.iterdir()):
        if path.is_file():
            outputs[path.name] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    script_path = Path(__file__).resolve()
    manifest = {
        "schema_version": 1,
        "status": "complete",
        "analysis": ANALYSIS_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "producer": {"path": str(script_path), "sha256": sha256_file(script_path), "bytes": script_path.stat().st_size},
        "production_root": str(production_root),
        "source_evaluation_count": 4,
        "seeds": list(SEEDS),
        "grids": ["2x2", "10x10"],
        "feedbacks": ["crossattn1"],
        "source_scope_guard": {
            "expected_labels": expected_source_labels(),
            "exact_match_required": True,
            "seed0_sources_read_only": True,
        },
        "source_evaluations": source_evidence,
        "outputs": outputs,
        "atomic_promotion": True,
        "overwrite_protection": "refuse-existing-output",
        "seed0_synthesis_outputs_modified": False,
    }
    write_json(staging / "MANIFEST.json", manifest)

    recorded = read_json(staging / "MANIFEST.json")["outputs"]
    actual_output_names = {path.name for path in staging.iterdir() if path.is_file() and path.name != "MANIFEST.json"}
    require(set(recorded) == actual_output_names, "staged output coverage mismatch")
    for name, evidence in recorded.items():
        path = staging / name
        require(path.stat().st_size == evidence["bytes"], f"staged output byte mismatch: {name}")
        require(sha256_file(path) == evidence["sha256"], f"staged output hash mismatch: {name}")
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite output root created during synthesis: {output_root}")
    staging.rename(output_root)
    print(f"[complete] atomically promoted {output_root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
