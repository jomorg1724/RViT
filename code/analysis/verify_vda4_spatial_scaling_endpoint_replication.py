"""Read-only verifier for the VDA4 cross-attention endpoint replication bundle.

The verifier is intentionally independent of the bundle producer.  It admits
only the four held-out evaluations at the 2x2 and 10x10 endpoints for seeds 0
and 1, verifies every source and bundle hash, recomputes the reported metrics
from the hash-bound NPZ caches, and decodes every declared figure.  It never
creates, edits, replaces, or deletes an artifact.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import numpy as np


VALIDITIES = np.asarray([0.25, 0.50, 0.75, 1.00], dtype=np.float64)
MAGNITUDES = np.asarray(
    [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0],
    dtype=np.float64,
)
GRIDS = ((2, 2), (10, 10))
SEEDS = (0, 1)
EXPLICIT_MODES = ("natural", "uniform", "shuffle", "disable")
ANALYSIS_NAME = "cached-artifact-only VDA4 cross-attention endpoint replication synthesis"
OVERWRITE_PROTECTION = "refuse-existing-output"
HEX64 = re.compile(r"[0-9a-f]{64}")
SOURCE_NAME = re.compile(r"vda4_crossattn1_grid(2x2|10x10)_seed([01])")
SEED0_SYNTHESIS_NAME = re.compile(r"synthesis_seed0(?:_v\d+)?", re.IGNORECASE)

REQUIRED_SOURCE_ARTIFACTS = {
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

METRICS_FILENAME = "vda4_spatial_scaling_endpoint_replication_metrics.csv"
FIGURE_PDF = "vda4_spatial_scaling_endpoint_replication_summary.pdf"
FIGURE_PNG = "vda4_spatial_scaling_endpoint_replication_summary.png"
REQUIRED_OUTPUTS = {"SUMMARY.json", METRICS_FILENAME, FIGURE_PDF, FIGURE_PNG}

METRIC_COLUMNS = (
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


class VerificationError(ValueError):
    """Raised when the bundle cannot be admitted as verified evidence."""


@dataclass
class Audit:
    semantic_checks: int = 0
    hashes_verified: int = 0
    figures_decoded: int = 0

    def require(self, condition: bool, message: str) -> None:
        self.semantic_checks += 1
        if not condition:
            raise VerificationError(message)


@dataclass(frozen=True)
class Source:
    directory: Path
    label: str
    rows: int
    cols: int
    seed: int
    manifest: dict[str, Any]
    manifest_sha256: str
    manifest_bytes: int
    artifacts: dict[str, dict[str, Any]]
    metrics: dict[str, Any]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def read_json(path: Path, audit: Audit) -> dict[str, Any]:
    audit.require(path.is_file() and not path.is_symlink(), f"missing regular JSON file: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                VerificationError(f"non-finite JSON constant {value!r} in {path}")
            ),
        )
    except VerificationError:
        raise
    except Exception as exc:
        raise VerificationError(f"cannot parse JSON {path}: {exc}") from exc
    audit.require(isinstance(value, dict), f"expected a JSON object: {path}")
    return value


def expected_source_labels() -> set[str]:
    return {
        f"vda4_crossattn1_grid{rows}x{cols}_seed{seed}"
        for seed in SEEDS
        for rows, cols in GRIDS
    }


def safe_regular_file(root: Path, key: str, audit: Audit) -> Path:
    audit.require("\\" not in key, f"artifact key is not canonical POSIX: {key!r}")
    relative = PurePosixPath(key)
    audit.require(
        not relative.is_absolute() and ".." not in relative.parts and "." not in relative.parts,
        f"unsafe artifact path: {key!r}",
    )
    path = root.joinpath(*relative.parts)
    resolved_root = root.resolve()
    resolved = path.resolve()
    audit.require(resolved_root in resolved.parents, f"artifact escapes its root: {key!r}")
    audit.require(path.is_file() and not path.is_symlink(), f"missing regular artifact: {path}")
    return path


def verify_hash_and_bytes(
    path: Path,
    evidence: dict[str, Any],
    audit: Audit,
    context: str,
) -> dict[str, Any]:
    audit.require(isinstance(evidence, dict), f"{context}: hash evidence is not an object")
    expected_sha = str(evidence.get("sha256", "")).lower()
    expected_bytes = evidence.get("bytes")
    audit.require(bool(HEX64.fullmatch(expected_sha)), f"{context}: invalid SHA-256")
    audit.require(
        isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) and expected_bytes >= 0,
        f"{context}: invalid byte count",
    )
    actual_bytes = path.stat().st_size
    actual_sha = sha256_file(path)
    audit.require(actual_bytes == expected_bytes, f"{context}: byte mismatch {actual_bytes} != {expected_bytes}")
    audit.require(actual_sha == expected_sha, f"{context}: SHA-256 mismatch {actual_sha} != {expected_sha}")
    audit.hashes_verified += 1
    return {"sha256": actual_sha, "bytes": actual_bytes}


def verify_declared_sha(path: Path, expected_sha: Any, audit: Audit, context: str) -> dict[str, Any]:
    digest = str(expected_sha).lower()
    audit.require(bool(HEX64.fullmatch(digest)), f"{context}: invalid SHA-256")
    actual = sha256_file(path)
    audit.require(actual == digest, f"{context}: SHA-256 mismatch {actual} != {digest}")
    audit.hashes_verified += 1
    return {"sha256": actual, "bytes": path.stat().st_size}


def validate_png(path: Path, audit: Audit, context: str) -> None:
    try:
        from PIL import Image

        with Image.open(path) as image:
            audit.require(image.format == "PNG", f"{context}: file does not decode as PNG")
            width, height = image.size
            audit.require(width >= 600 and height >= 300, f"{context}: implausibly small figure {width}x{height}")
            image.verify()
        with Image.open(path) as image:
            image.load()
            thumbnail = image.convert("L")
            thumbnail.thumbnail((96, 96))
            lo, hi = thumbnail.getextrema()
            audit.require(hi > lo, f"{context}: decoded PNG is visually blank")
    except VerificationError:
        raise
    except Exception as exc:
        raise VerificationError(f"{context}: unreadable PNG: {exc}") from exc
    audit.figures_decoded += 1


def validate_pdf(path: Path, audit: Audit, context: str) -> None:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path), strict=True)
        audit.require(not reader.is_encrypted, f"{context}: encrypted PDF")
        audit.require(len(reader.pages) == 1, f"{context}: expected one-page PDF")
        page = reader.pages[0]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        audit.require(width >= 300.0 and height >= 200.0, f"{context}: implausible PDF media box")
        audit.require(page.get_contents() is not None, f"{context}: PDF page has no content stream")
        text = (page.extract_text() or "").strip()
        audit.require(len(text) >= 20, f"{context}: PDF contains too little readable text")
    except VerificationError:
        raise
    except Exception as exc:
        raise VerificationError(f"{context}: unreadable PDF: {exc}") from exc
    audit.figures_decoded += 1


def validate_figure(path: Path, audit: Audit, context: str) -> None:
    if path.suffix.lower() == ".png":
        validate_png(path, audit, context)
    elif path.suffix.lower() == ".pdf":
        validate_pdf(path, audit, context)
    else:
        raise VerificationError(f"{context}: unsupported figure extension")


def finite_array(value: np.ndarray, audit: Audit, context: str) -> np.ndarray:
    array = np.asarray(value)
    audit.require(np.issubdtype(array.dtype, np.number), f"{context}: not numeric")
    audit.require(bool(np.all(np.isfinite(array))), f"{context}: contains non-finite values")
    return array


def scalar(value: np.ndarray, audit: Audit, context: str) -> Any:
    array = np.asarray(value)
    audit.require(array.ndim == 0, f"{context}: expected scalar")
    return array.item()


def expected_region_tokens(rows: int, cols: int) -> list[list[int]]:
    regions: list[list[int]] = []
    for location in range(4):
        task_row, task_col = divmod(location, 2)
        row_start, row_stop = task_row * (rows // 2), (task_row + 1) * (rows // 2)
        col_start, col_stop = task_col * (cols // 2), (task_col + 1) * (cols // 2)
        regions.append(
            [r * cols + c for r in range(row_start, row_stop) for c in range(col_start, col_stop)]
        )
    return regions


def load_npz(path: Path) -> dict[str, np.ndarray]:
    try:
        with np.load(path, allow_pickle=False) as archive:
            return {key: archive[key] for key in archive.files}
    except Exception as exc:
        raise VerificationError(f"cannot load trusted NPZ {path}: {exc}") from exc


def validate_npz_metadata(
    data: dict[str, np.ndarray],
    label: str,
    rows: int,
    cols: int,
    manifest_model: dict[str, Any],
    cache_name: str,
    audit: Audit,
) -> None:
    expected = {
        "meta_label": label,
        "meta_task": "vda4",
        "meta_feedback": "crossattn1",
        "meta_grid_rows": rows,
        "meta_grid_cols": cols,
        "meta_n_tokens": rows * cols,
        "meta_checkpoint_iteration": 19999,
        "meta_checkpoint_sha256": manifest_model["checkpoint_sha256"],
        "meta_producer_sha256": manifest_model["producer_sha256"],
    }
    for key, expected_value in expected.items():
        audit.require(key in data, f"{label}/{cache_name}: missing {key}")
        actual = scalar(data[key], audit, f"{label}/{cache_name}/{key}")
        audit.require(actual == expected_value, f"{label}/{cache_name}: {key} mismatch")


def monotone_threshold(
    magnitudes: np.ndarray,
    rates: np.ndarray,
    audit: Audit,
    context: str,
    target: float = 0.5,
) -> float:
    x = finite_array(magnitudes, audit, f"{context}/magnitudes").astype(np.float64)
    y = finite_array(rates, audit, f"{context}/rates").astype(np.float64)
    audit.require(x.ndim == y.ndim == 1 and x.size == y.size and x.size >= 2, f"{context}: bad shape")
    audit.require(bool(np.all(np.diff(x) > 0.0)), f"{context}: magnitudes not strictly increasing")
    envelope = np.maximum.accumulate(y)
    crossings = np.flatnonzero(envelope >= target)
    audit.require(crossings.size > 0, f"{context}: response envelope never reaches 0.5")
    index = int(crossings[0])
    if index == 0:
        audit.require(math.isclose(float(envelope[0]), target, abs_tol=1e-12), f"{context}: left-censored threshold")
        return float(x[0])
    lo_y, hi_y = float(envelope[index - 1]), float(envelope[index])
    audit.require(hi_y > lo_y, f"{context}: threshold crossing not identifiable")
    return float(x[index - 1] + (target - lo_y) * (x[index] - x[index - 1]) / (hi_y - lo_y))


def _trapezoid(values: np.ndarray, x: np.ndarray) -> float:
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(values, x=x))
    return float(np.trapz(values, x=x))  # pragma: no cover - NumPy < 2 compatibility


def compute_source_metrics(
    label: str,
    rows: int,
    cols: int,
    seed: int,
    manifest_sha256: str,
    manifest_model: dict[str, Any],
    directory: Path,
    audit: Audit,
) -> dict[str, Any]:
    psych = load_npz(directory / "data" / "psychometrics.npz")
    attention = load_npz(directory / "data" / "event_attention.npz")
    interventions = load_npz(directory / "data" / "interventions.npz")
    for cache_name, cache in (
        ("psychometrics", psych),
        ("event_attention", attention),
        ("interventions", interventions),
    ):
        validate_npz_metadata(cache, label, rows, cols, manifest_model, cache_name, audit)

    psych_trials, attention_trials, intervention_trials = 300, 128, 250
    audit.require(psych.get("response_count", np.empty(0)).shape == (4, 10, 2), f"{label}: response_count shape")
    audit.require(psych.get("response_rate", np.empty(0)).shape == (4, 10, 2), f"{label}: response_rate shape")
    audit.require(psych.get("mean_rt", np.empty(0)).shape == (4, 10, 2), f"{label}: mean_rt shape")
    audit.require(psych.get("press_histogram", np.empty(0)).shape == (4, 10, 2, 8), f"{label}: press histogram shape")
    counts = finite_array(psych["response_count"], audit, f"{label}/response_count")
    rates = finite_array(psych["response_rate"], audit, f"{label}/response_rate")
    audit.require(np.issubdtype(counts.dtype, np.integer), f"{label}: response counts are not integers")
    audit.require(bool(np.all((counts >= 0) & (counts <= psych_trials))), f"{label}: response count range")
    audit.require(bool(np.all((rates >= 0.0) & (rates <= 1.0))), f"{label}: response rate range")
    audit.require(bool(np.allclose(rates, counts / psych_trials, atol=1e-12)), f"{label}: response count/rate mismatch")
    histogram = finite_array(psych["press_histogram"], audit, f"{label}/press_histogram")
    audit.require(np.issubdtype(histogram.dtype, np.integer) and bool(np.all(histogram >= 0)), f"{label}: invalid psychometric histogram counts")
    audit.require(bool(np.all(histogram.sum(axis=-1) == psych_trials)), f"{label}: psychometric histogram totals")
    for name, shape in (
        ("false_alarm_count", (4,)),
        ("false_alarm_rate", (4,)),
        ("false_alarm_histogram", (4, 8)),
        ("dprime", (4, 10, 2)),
        ("criterion", (4, 10, 2)),
    ):
        audit.require(psych.get(name, np.empty(0)).shape == shape, f"{label}: {name} shape")
        finite_array(psych[name], audit, f"{label}/{name}")
    audit.require(np.issubdtype(psych["false_alarm_count"].dtype, np.integer), f"{label}: false-alarm counts are not integers")
    audit.require(np.issubdtype(psych["false_alarm_histogram"].dtype, np.integer), f"{label}: false-alarm histogram is not integer")
    audit.require(
        bool(np.allclose(psych["false_alarm_rate"], psych["false_alarm_count"] / psych_trials, atol=1e-12)),
        f"{label}: false-alarm count/rate mismatch",
    )
    audit.require(
        bool(np.all(psych["false_alarm_histogram"].sum(axis=-1) == psych_trials)),
        f"{label}: false-alarm histogram totals",
    )
    audit.require(bool(np.all(np.isfinite(psych["mean_rt"][:, -1, :]))), f"{label}: non-finite 30-degree RT")

    n_tokens = rows * cols
    audit.require(attention.get("press", np.empty(0)).shape == (2, attention_trials), f"{label}: attention press shape")
    audit.require(
        attention.get("token_mass", np.empty(0)).shape == (2, attention_trials, 7, n_tokens),
        f"{label}: token mass shape",
    )
    audit.require(
        attention.get("region_mass", np.empty(0)).shape == (2, attention_trials, 7, 4),
        f"{label}: region mass shape",
    )
    audit.require(
        attention.get("raw_attention_mean", np.empty(0)).shape == (2, 7, n_tokens, 2 * n_tokens),
        f"{label}: raw attention shape",
    )
    token_mass = finite_array(attention["token_mass"], audit, f"{label}/token_mass")
    region_mass = finite_array(attention["region_mass"], audit, f"{label}/region_mass")
    finite_array(attention["raw_attention_mean"], audit, f"{label}/raw_attention_mean")
    audit.require(bool(np.all(token_mass >= -1e-7)), f"{label}: negative token mass")
    audit.require(bool(np.all(region_mass >= -1e-7)), f"{label}: negative region mass")
    audit.require(bool(np.allclose(token_mass.sum(axis=-1), 1.0, atol=2e-5)), f"{label}: token mass normalization")
    audit.require(bool(np.allclose(region_mass.sum(axis=-1), 1.0, atol=2e-5)), f"{label}: region mass normalization")
    rebuilt_regions = np.stack(
        [token_mass[..., tokens].sum(axis=-1) for tokens in expected_region_tokens(rows, cols)],
        axis=-1,
    )
    audit.require(bool(np.allclose(region_mass, rebuilt_regions, atol=2e-5)), f"{label}: region/token mass mismatch")

    for name, shape in (
        ("response_count", (3, 5, 3)),
        ("response_rate", (3, 5, 3)),
        ("press_histogram", (3, 5, 3, 8)),
        ("explicit_response_count", (4, 3)),
        ("explicit_response_rate", (4, 3)),
        ("explicit_press_histogram", (4, 3, 8)),
    ):
        audit.require(interventions.get(name, np.empty(0)).shape == shape, f"{label}: {name} shape")
    modes = tuple(str(value) for value in interventions["explicit_modes"].tolist())
    audit.require(modes == EXPLICIT_MODES, f"{label}: explicit intervention modes/order")
    regional_counts = finite_array(interventions["response_count"], audit, f"{label}/intervention_count")
    regional_rates = finite_array(interventions["response_rate"], audit, f"{label}/intervention_rate")
    explicit_counts = finite_array(interventions["explicit_response_count"], audit, f"{label}/explicit_count")
    explicit_rates = finite_array(interventions["explicit_response_rate"], audit, f"{label}/explicit_rate")
    audit.require(np.issubdtype(regional_counts.dtype, np.integer), f"{label}: regional intervention counts are not integers")
    audit.require(np.issubdtype(explicit_counts.dtype, np.integer), f"{label}: explicit intervention counts are not integers")
    audit.require(
        np.issubdtype(interventions["press_histogram"].dtype, np.integer)
        and np.issubdtype(interventions["explicit_press_histogram"].dtype, np.integer),
        f"{label}: intervention histograms are not integer",
    )
    audit.require(bool(np.allclose(regional_rates, regional_counts / intervention_trials, atol=1e-12)), f"{label}: regional intervention rate mismatch")
    audit.require(bool(np.allclose(explicit_rates, explicit_counts / intervention_trials, atol=1e-12)), f"{label}: explicit intervention rate mismatch")
    audit.require(bool(np.all(interventions["press_histogram"].sum(axis=-1) == intervention_trials)), f"{label}: intervention histogram totals")
    audit.require(bool(np.all(interventions["explicit_press_histogram"].sum(axis=-1) == intervention_trials)), f"{label}: explicit histogram totals")
    for name in (
        "achieved_change_region_mass",
        "achieved_target_region_mass",
        "explicit_dprime",
        "explicit_criterion",
    ):
        finite_array(interventions[name], audit, f"{label}/{name}")
    permutation = finite_array(interventions["shuffle_permutation"], audit, f"{label}/shuffle_permutation")
    audit.require(permutation.shape == (2 * n_tokens,), f"{label}: shuffle permutation length")
    audit.require(
        sorted(permutation.astype(int).tolist()) == list(range(2 * n_tokens)),
        f"{label}: shuffle is not a permutation",
    )

    validity_index = 3
    response = rates.astype(np.float64)
    mean_rt = psych["mean_rt"].astype(np.float64)
    metric_region_mass = region_mass.astype(np.float64)
    valid_threshold = monotone_threshold(
        MAGNITUDES, response[validity_index, :, 0], audit, f"{label}/valid_threshold"
    )
    invalid_threshold = monotone_threshold(
        MAGNITUDES, response[validity_index, :, 1], audit, f"{label}/invalid_threshold"
    )
    valid_tl = float(metric_region_mass[0, :, 5:7, 0].mean())
    invalid_br = float(metric_region_mass[1, :, 5:7, 3].mean())
    invalid_tl = float(metric_region_mass[1, :, 5:7, 0].mean())
    explicit = explicit_rates.astype(np.float64)
    invalid_explicit = {mode: float(explicit[index, 1]) for index, mode in enumerate(EXPLICIT_MODES)}
    metric = {
        "feedback": "crossattn1",
        "model": "Cross-attention",
        "grid": f"{rows}x{cols}",
        "n_tokens": n_tokens,
        "seed": seed,
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
        "explicit_natural_invalid_response_rate": invalid_explicit["natural"],
        "explicit_uniform_invalid_response_rate": invalid_explicit["uniform"],
        "explicit_shuffle_invalid_response_rate": invalid_explicit["shuffle"],
        "explicit_disable_invalid_response_rate": invalid_explicit["disable"],
        "causal_dependence_natural_minus_disable_pp": 100.0
        * (invalid_explicit["natural"] - invalid_explicit["disable"]),
        "source_manifest_sha256": manifest_sha256,
    }
    audit.require(tuple(metric) == METRIC_COLUMNS, f"{label}: internal metric schema drift")
    audit.require(
        all(math.isfinite(value) for value in metric.values() if isinstance(value, float)),
        f"{label}: computed non-finite metric",
    )
    return metric


def parse_label(label: str, audit: Audit) -> tuple[int, int, int]:
    match = SOURCE_NAME.fullmatch(label)
    audit.require(match is not None, f"unregistered endpoint source label: {label}")
    assert match is not None
    grid, seed_text = match.groups()
    rows, cols = (int(value) for value in grid.split("x"))
    return rows, cols, int(seed_text)


def validate_source(production_root: Path, label: str, audit: Audit) -> Source:
    rows, cols, seed = parse_label(label, audit)
    directory = production_root / label
    audit.require(directory.is_dir() and not directory.is_symlink(), f"missing regular source directory: {directory}")
    manifest_path = directory / "MANIFEST.json"
    manifest = read_json(manifest_path, audit)
    audit.require(manifest.get("schema_version") == 1, f"{label}: unsupported manifest schema")
    audit.require(manifest.get("status") == "complete", f"{label}: source is not complete")
    audit.require(manifest.get("config_path") == "analysis_config.json", f"{label}: config path mismatch")
    audit.require(manifest.get("summary_path") == "SUMMARY.json", f"{label}: summary path mismatch")
    model = manifest.get("model")
    audit.require(isinstance(model, dict), f"{label}: missing model metadata")
    expected_model = {
        "label": label,
        "task": "vda4",
        "feedback": "crossattn1",
        "grid_rows": rows,
        "grid_cols": cols,
        "n_tokens": rows * cols,
        "checkpoint_iteration": 19999,
    }
    for key, expected in expected_model.items():
        audit.require(model.get(key) == expected, f"{label}: model.{key} mismatch")
    for key in ("checkpoint_sha256", "producer_sha256"):
        audit.require(bool(HEX64.fullmatch(str(model.get(key, "")).lower())), f"{label}: invalid model.{key}")
    evaluator_path = Path(str(model.get("producer_path", ""))).expanduser().resolve()
    audit.require(
        evaluator_path.name == "vda4_spatial_scaling_evaluation.py",
        f"{label}: unexpected evaluator producer filename",
    )
    audit.require(evaluator_path.is_file() and not evaluator_path.is_symlink(), f"{label}: evaluator source unavailable")
    verify_declared_sha(evaluator_path, model["producer_sha256"], audit, f"{label}/evaluator producer")

    declared = manifest.get("artifact_hashes")
    audit.require(isinstance(declared, dict), f"{label}: artifact_hashes is not an object")
    declared_keys = set(declared)
    audit.require(
        REQUIRED_SOURCE_ARTIFACTS <= declared_keys,
        f"{label}: missing source artifacts {sorted(REQUIRED_SOURCE_ARTIFACTS - declared_keys)}",
    )
    actual_keys = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    audit.require(
        declared_keys == actual_keys,
        f"{label}: source artifact coverage mismatch; undeclared={sorted(actual_keys-declared_keys)}, missing={sorted(declared_keys-actual_keys)}",
    )
    artifacts: dict[str, dict[str, Any]] = {}
    for key in sorted(declared):
        path = safe_regular_file(directory, key, audit)
        artifacts[key] = verify_declared_sha(path, declared[key], audit, f"{label}/{key}")
        if key.startswith("figures/") and path.suffix.lower() in {".png", ".pdf"}:
            validate_figure(path, audit, f"{label}/{key}")

    config = read_json(directory / "analysis_config.json", audit)
    summary = read_json(directory / "SUMMARY.json", audit)
    for document_name, document_model in (
        ("analysis_config", config),
        ("SUMMARY", summary.get("model")),
    ):
        audit.require(isinstance(document_model, dict), f"{label}: {document_name} model metadata")
        assert isinstance(document_model, dict)
        for key, expected in expected_model.items():
            audit.require(document_model.get(key) == expected, f"{label}: {document_name}.{key} mismatch")
        audit.require(document_model.get("checkpoint_sha256") == model.get("checkpoint_sha256"), f"{label}: {document_name} checkpoint hash mismatch")
        audit.require(document_model.get("producer_path") == model.get("producer_path"), f"{label}: {document_name} producer path mismatch")
        audit.require(document_model.get("producer_sha256") == model.get("producer_sha256"), f"{label}: {document_name} producer hash mismatch")
    audit.require(config.get("psychometric_trials") == 300, f"{label}: psychometric trials")
    audit.require(config.get("attention_trials") == 128, f"{label}: attention trials")
    audit.require(config.get("intervention_trials") == 250, f"{label}: intervention trials")
    audit.require(config.get("validities") == VALIDITIES.tolist(), f"{label}: validity grid")
    audit.require(config.get("magnitudes") == MAGNITUDES.tolist(), f"{label}: magnitude grid")
    audit.require(config.get("focal_validity") == 1.0, f"{label}: focal validity")
    audit.require(config.get("focal_magnitude") == 30.0, f"{label}: focal magnitude")
    audit.require(config.get("qualifying_frames") == [5, 6], f"{label}: qualifying frames")
    audit.require(config.get("region_tokens") == expected_region_tokens(rows, cols), f"{label}: region-token map")
    audit.require(config.get("regional_uniform_baseline") == 0.25, f"{label}: regional baseline")
    producer_map = config.get("checkpoint_producer_sha256")
    audit.require(isinstance(producer_map, dict) and bool(producer_map), f"{label}: checkpoint producer provenance")
    audit.require(
        all(isinstance(value, str) and HEX64.fullmatch(value.lower()) for value in producer_map.values()),
        f"{label}: invalid checkpoint producer provenance hash",
    )
    audit.require(summary.get("schema_version") == 1, f"{label}: SUMMARY schema")
    audit.require(summary.get("training_is_not_scientific_validation") is True, f"{label}: evidence-boundary marker")

    manifest_sha = sha256_file(manifest_path)
    audit.hashes_verified += 1
    metrics = compute_source_metrics(
        label, rows, cols, seed, manifest_sha, model, directory, audit
    )
    return Source(
        directory=directory,
        label=label,
        rows=rows,
        cols=cols,
        seed=seed,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        manifest_bytes=manifest_path.stat().st_size,
        artifacts=artifacts,
        metrics=metrics,
    )


def validate_bundle_location(production_root: Path, bundle_root: Path, audit: Audit) -> None:
    audit.require(production_root.is_dir() and not production_root.is_symlink(), f"invalid production root: {production_root}")
    audit.require(bundle_root.is_dir() and not bundle_root.is_symlink(), f"invalid bundle root: {bundle_root}")
    audit.require(bundle_root != production_root, "bundle root must not overwrite the production root")
    audit.require(bundle_root.parent == production_root, "bundle root must be a direct child of the production root")
    audit.require(SEED0_SYNTHESIS_NAME.fullmatch(bundle_root.name) is None, "refusing to admit a seed-0 synthesis as endpoint replication")
    audit.require("endpoint" in bundle_root.name.lower() and "replication" in bundle_root.name.lower(), "bundle directory is not explicitly endpoint-replication scoped")


def _normalize_source_evidence(entry: dict[str, Any], source: Source, audit: Audit) -> None:
    context = f"bundle source evidence/{source.label}"
    audit.require(entry.get("label") == source.label, f"{context}: label mismatch")
    audit.require(entry.get("seed") == source.seed, f"{context}: seed mismatch")
    audit.require(entry.get("grid") == f"{source.rows}x{source.cols}", f"{context}: grid mismatch")
    audit.require(entry.get("n_tokens") == source.rows * source.cols, f"{context}: token count mismatch")
    audit.require(entry.get("relative_path") == source.label, f"{context}: relative path mismatch")
    audit.require(entry.get("manifest_sha256") == source.manifest_sha256, f"{context}: manifest hash mismatch")
    audit.require(entry.get("manifest_bytes") == source.manifest_bytes, f"{context}: manifest bytes mismatch")
    model = source.manifest["model"]
    audit.require(entry.get("checkpoint_sha256") == model["checkpoint_sha256"], f"{context}: checkpoint hash mismatch")
    audit.require(entry.get("producer_sha256") == model["producer_sha256"], f"{context}: evaluator hash mismatch")
    evidence_artifacts = entry.get("artifacts")
    audit.require(isinstance(evidence_artifacts, dict), f"{context}: artifacts evidence is not an object")
    audit.require(set(evidence_artifacts) == set(source.artifacts), f"{context}: artifact evidence coverage")
    for key, actual in source.artifacts.items():
        audit.require(evidence_artifacts[key] == actual, f"{context}: artifact evidence mismatch for {key}")


def _float(value: Any, audit: Audit, context: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise VerificationError(f"{context}: expected numeric value, got {value!r}") from exc
    audit.require(math.isfinite(result), f"{context}: non-finite number")
    return result


def _integer(value: Any, audit: Audit, context: str) -> int:
    result = _float(value, audit, context)
    audit.require(result.is_integer(), f"{context}: expected integer")
    return int(result)


def numbers_close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=5e-10, abs_tol=5e-10)


def compare_metric_row(
    actual: dict[str, Any],
    expected: dict[str, Any],
    audit: Audit,
    context: str,
) -> None:
    audit.require(set(actual) == set(METRIC_COLUMNS), f"{context}: metric columns/keys mismatch")
    for key in ("feedback", "model", "grid", "source_manifest_sha256"):
        audit.require(actual.get(key) == expected[key], f"{context}: {key} mismatch")
    for key in ("n_tokens", "seed"):
        audit.require(_integer(actual.get(key), audit, f"{context}/{key}") == expected[key], f"{context}: {key} mismatch")
    for key in METRIC_COLUMNS:
        if key in {"feedback", "model", "grid", "n_tokens", "seed", "source_manifest_sha256"}:
            continue
        actual_number = _float(actual.get(key), audit, f"{context}/{key}")
        audit.require(numbers_close(actual_number, float(expected[key])), f"{context}: {key} mismatch {actual_number} != {expected[key]}")


def read_metrics_csv(path: Path, audit: Audit) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            audit.require(reader.fieldnames is not None, "metrics CSV lacks a header")
            assert reader.fieldnames is not None
            audit.require(len(reader.fieldnames) == len(set(reader.fieldnames)), "metrics CSV has duplicate columns")
            audit.require(tuple(reader.fieldnames) == METRIC_COLUMNS, "metrics CSV column order/schema mismatch")
            rows = list(reader)
    except VerificationError:
        raise
    except Exception as exc:
        raise VerificationError(f"cannot read metrics CSV {path}: {exc}") from exc
    audit.require(all(None not in row for row in rows), "metrics CSV contains surplus fields")
    return rows


def expected_deltas(metrics_by_seed_grid: dict[tuple[int, str], dict[str, Any]]) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    for seed in SEEDS:
        low = metrics_by_seed_grid[(seed, "2x2")]
        high = metrics_by_seed_grid[(seed, "10x10")]
        row: dict[str, Any] = {
            "seed": seed,
            "from_grid": "2x2",
            "to_grid": "10x10",
            "from_tokens": 4,
            "to_tokens": 100,
        }
        for metric in DELTA_METRICS:
            row[f"delta_10x10_minus_2x2_{metric}"] = float(high[metric]) - float(low[metric])
        deltas.append(row)
    return deltas


def compare_delta_row(actual: dict[str, Any], expected: dict[str, Any], audit: Audit, context: str) -> None:
    audit.require(set(actual) == set(expected), f"{context}: delta schema mismatch")
    audit.require(_integer(actual.get("seed"), audit, f"{context}/seed") == expected["seed"], f"{context}: seed mismatch")
    for key in ("from_grid", "to_grid"):
        audit.require(actual.get(key) == expected[key], f"{context}: {key} mismatch")
    for key in ("from_tokens", "to_tokens"):
        audit.require(_integer(actual.get(key), audit, f"{context}/{key}") == expected[key], f"{context}: {key} mismatch")
    for key in expected:
        if not key.startswith("delta_"):
            continue
        actual_number = _float(actual.get(key), audit, f"{context}/{key}")
        audit.require(numbers_close(actual_number, float(expected[key])), f"{context}: {key} mismatch")


def delta_direction(value: float, tolerance: float = 1e-12) -> str:
    if value > tolerance:
        return "increase"
    if value < -tolerance:
        return "decrease"
    return "no_change"


def expected_dispersion(delta_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_seed = {int(row["seed"]): row for row in delta_rows}
    result: dict[str, dict[str, Any]] = {}
    for metric in DELTA_METRICS:
        delta_key = f"delta_10x10_minus_2x2_{metric}"
        values = np.asarray([float(by_seed[seed][delta_key]) for seed in SEEDS], dtype=np.float64)
        directions = [delta_direction(float(value)) for value in values]
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


def compare_dispersion(
    actual: dict[str, Any],
    expected: dict[str, dict[str, Any]],
    audit: Audit,
) -> None:
    audit.require(set(actual) == set(DELTA_METRICS), "SUMMARY: descriptive dispersion metric coverage")
    for metric, expected_item in expected.items():
        context = f"SUMMARY/descriptive_replication_summary/{metric}"
        item = actual.get(metric)
        audit.require(isinstance(item, dict), f"{context}: not an object")
        audit.require(set(item) == set(expected_item), f"{context}: schema mismatch")
        for key in (
            "n_training_seeds",
            "direction_by_seed",
            "directional_agreement",
            "shared_direction",
            "evidence_class",
        ):
            audit.require(item.get(key) == expected_item[key], f"{context}: {key} mismatch")
        actual_seedwise = item.get("seedwise_deltas_10x10_minus_2x2")
        audit.require(isinstance(actual_seedwise, dict), f"{context}: seedwise deltas not an object")
        audit.require(set(actual_seedwise) == {"seed0", "seed1"}, f"{context}: seedwise delta coverage")
        for seed_key in ("seed0", "seed1"):
            value = _float(actual_seedwise.get(seed_key), audit, f"{context}/{seed_key}")
            audit.require(numbers_close(value, expected_item["seedwise_deltas_10x10_minus_2x2"][seed_key]), f"{context}: {seed_key} delta mismatch")
        for key in (
            "mean_delta_descriptive_only",
            "minimum_delta",
            "maximum_delta",
            "range_across_two_seed_deltas",
            "sample_standard_deviation_across_two_seed_deltas",
        ):
            value = _float(item.get(key), audit, f"{context}/{key}")
            audit.require(numbers_close(value, expected_item[key]), f"{context}: {key} mismatch")


def validate_summary(
    summary: dict[str, Any],
    sources: list[Source],
    audit: Audit,
) -> None:
    audit.require(summary.get("schema_version") == 1, "SUMMARY: unsupported schema")
    audit.require(summary.get("status") == "complete", "SUMMARY: status is not complete")
    audit.require(summary.get("analysis") == ANALYSIS_NAME, "SUMMARY: analysis identity mismatch")
    audit.require(
        summary.get("scope") == "crossattn1 2x2 versus 10x10 endpoint comparison across training seeds 0 and 1",
        "SUMMARY: scope mismatch",
    )
    audit.require(summary.get("source_evaluation_count") == 4, "SUMMARY: source count must be four")
    audit.require(summary.get("seeds") == [0, 1], "SUMMARY: seeds must be exactly [0, 1]")
    audit.require(summary.get("grids") == ["2x2", "10x10"], "SUMMARY: grids must be endpoint-only")
    audit.require(summary.get("feedbacks") == ["crossattn1"], "SUMMARY: feedback scope mismatch")
    audit.require(summary.get("training_accuracy_used_as_attention_evidence") is False, "SUMMARY: evidence-boundary marker")
    audit.require(summary.get("seed0_synthesis_inputs_consumed_read_only") is True, "SUMMARY: seed-0 read-only marker")
    audit.require(summary.get("statistical_unit") == "independently trained checkpoint seed", "SUMMARY: statistical unit mismatch")
    audit.require(summary.get("n_training_seeds") == 2, "SUMMARY: training-seed count mismatch")
    audit.require(summary.get("all_metrics_path") == METRICS_FILENAME, "SUMMARY: metrics path mismatch")
    for key in ("metric_definitions", "descriptive_replication_summary", "interpretation"):
        audit.require(isinstance(summary.get(key), dict), f"SUMMARY: {key} is not an object")
    evidence_boundary = summary.get("evidence_boundary")
    audit.require(isinstance(evidence_boundary, dict), "SUMMARY: evidence boundary is not an object")
    audit.require(
        evidence_boundary.get("allowed") == "seedwise direction, directional agreement, and descriptive dispersion",
        "SUMMARY: allowed evidence class mismatch",
    )
    not_supported = evidence_boundary.get("not_supported")
    audit.require(isinstance(not_supported, list), "SUMMARY: unsupported-claims list missing")
    for required_limitation in (
        "confidence intervals or p-values",
        "population-level replication or scaling-law claims",
        "causal isolation of token count from parameter count or spatial discretization",
    ):
        audit.require(required_limitation in not_supported, f"SUMMARY: missing evidence boundary {required_limitation!r}")

    source_manifests = summary.get("source_manifests")
    audit.require(isinstance(source_manifests, list) and len(source_manifests) == 4, "SUMMARY: source manifest evidence")
    expected_source_manifest_evidence = {
        source.label: {"label": source.label, "sha256": source.manifest_sha256, "bytes": source.manifest_bytes}
        for source in sources
    }
    actual_source_manifest_evidence: dict[str, dict[str, Any]] = {}
    for entry in source_manifests:
        audit.require(isinstance(entry, dict), "SUMMARY: malformed source manifest entry")
        label = entry.get("label")
        audit.require(label in expected_source_manifest_evidence, f"SUMMARY: unexpected source manifest {label!r}")
        audit.require(label not in actual_source_manifest_evidence, f"SUMMARY: duplicate source manifest {label!r}")
        actual_source_manifest_evidence[str(label)] = entry
    audit.require(actual_source_manifest_evidence == expected_source_manifest_evidence, "SUMMARY: source manifest hashes/bytes mismatch")

    expected_by_identity = {(source.seed, source.metrics["grid"]): source.metrics for source in sources}
    endpoint_metrics = summary.get("endpoint_metrics")
    audit.require(isinstance(endpoint_metrics, list) and len(endpoint_metrics) == 4, "SUMMARY: endpoint metrics must have four rows")
    seen: set[tuple[int, str]] = set()
    for entry in endpoint_metrics:
        audit.require(isinstance(entry, dict), "SUMMARY: malformed endpoint metric row")
        identity = (
            _integer(entry.get("seed"), audit, "SUMMARY/endpoint_metrics/seed"),
            str(entry.get("grid")),
        )
        audit.require(identity in expected_by_identity, f"SUMMARY: unexpected endpoint identity {identity}")
        audit.require(identity not in seen, f"SUMMARY: duplicate endpoint identity {identity}")
        seen.add(identity)
        compare_metric_row(entry, expected_by_identity[identity], audit, f"SUMMARY/endpoint_metrics/{identity}")
    audit.require(seen == set(expected_by_identity), "SUMMARY: endpoint metric coverage mismatch")

    expected_delta_rows = {row["seed"]: row for row in expected_deltas(expected_by_identity)}
    actual_deltas = summary.get("seedwise_endpoint_deltas")
    audit.require(isinstance(actual_deltas, list) and len(actual_deltas) == 2, "SUMMARY: seedwise deltas must have two rows")
    seen_seeds: set[int] = set()
    for entry in actual_deltas:
        audit.require(isinstance(entry, dict), "SUMMARY: malformed delta row")
        seed = _integer(entry.get("seed"), audit, "SUMMARY/seedwise_endpoint_deltas/seed")
        audit.require(seed in expected_delta_rows, f"SUMMARY: unexpected delta seed {seed}")
        audit.require(seed not in seen_seeds, f"SUMMARY: duplicate delta seed {seed}")
        seen_seeds.add(seed)
        compare_delta_row(entry, expected_delta_rows[seed], audit, f"SUMMARY/seedwise_endpoint_deltas/seed{seed}")
    audit.require(seen_seeds == set(SEEDS), "SUMMARY: missing seedwise delta")

    delta_rows_in_seed_order = [expected_delta_rows[seed] for seed in SEEDS]
    compare_dispersion(summary["descriptive_replication_summary"], expected_dispersion(delta_rows_in_seed_order), audit)
    elapsed = _float(summary.get("elapsed_seconds"), audit, "SUMMARY/elapsed_seconds")
    audit.require(elapsed >= 0.0, "SUMMARY: negative elapsed time")

    interpretation = summary["interpretation"]
    findings = interpretation.get("directional_findings")
    limitations = interpretation.get("limitations")
    audit.require(isinstance(findings, list) and len(findings) == len(DELTA_METRICS), "SUMMARY: directional findings coverage")
    audit.require(isinstance(limitations, list) and len(limitations) >= 4, "SUMMARY: limitations are incomplete")
    audit.require(all(isinstance(value, str) and value.strip() for value in findings + limitations), "SUMMARY: empty interpretation text")

    serialized = json.dumps(summary, sort_keys=True).lower()
    audit.require("seed 0 only" not in serialized, "SUMMARY: stale seed-0-only language")
    audit.require("no replication uncertainty" not in serialized, "SUMMARY: stale no-replication language")
    audit.require("affine_ew" not in serialized and "affine ew" not in serialized, "SUMMARY: affine results leaked into cross-attention replication")


def validate_bundle(production_root: Path, bundle_root: Path) -> dict[str, Any]:
    production_root = production_root.expanduser().resolve()
    bundle_root = bundle_root.expanduser().resolve()
    audit = Audit()
    validate_bundle_location(production_root, bundle_root, audit)

    labels = expected_source_labels()
    sources = [validate_source(production_root, label, audit) for label in sorted(labels)]
    audit.require({source.label for source in sources} == labels, "source evaluation coverage mismatch")
    audit.require(len({source.manifest_sha256 for source in sources}) == 4, "source manifests are not distinct")
    audit.require(
        len({source.manifest["model"]["checkpoint_sha256"] for source in sources}) == 4,
        "endpoint evaluations do not reference four distinct checkpoints",
    )
    audit.require(
        len({source.manifest["model"]["producer_sha256"] for source in sources}) == 1,
        "endpoint evaluations were not generated by one evaluator source",
    )

    manifest_path = bundle_root / "MANIFEST.json"
    manifest = read_json(manifest_path, audit)
    audit.require(manifest.get("schema_version") == 1, "bundle manifest schema")
    audit.require(manifest.get("status") == "complete", "bundle manifest is not complete")
    audit.require(manifest.get("analysis") == ANALYSIS_NAME, "bundle analysis identity mismatch")
    audit.require(manifest.get("atomic_promotion") is True, "bundle was not atomically promoted")
    audit.require(manifest.get("overwrite_protection") == OVERWRITE_PROTECTION, "bundle lacks no-overwrite protection")
    audit.require(manifest.get("source_evaluation_count") == 4, "bundle manifest source count")
    audit.require(manifest.get("seeds") == [0, 1], "bundle manifest seed scope")
    audit.require(manifest.get("grids") == ["2x2", "10x10"], "bundle manifest grid scope")
    audit.require(manifest.get("feedbacks") == ["crossattn1"], "bundle manifest feedback scope")
    audit.require(manifest.get("seed0_synthesis_outputs_modified") is False, "bundle modified seed-0 synthesis outputs")
    source_scope_guard = manifest.get("source_scope_guard")
    audit.require(isinstance(source_scope_guard, dict), "bundle source-scope guard missing")
    guarded_labels = source_scope_guard.get("expected_labels")
    audit.require(isinstance(guarded_labels, list), "bundle source-scope expected labels are not a list")
    audit.require(
        set(guarded_labels) == expected_source_labels(),
        "bundle source-scope expected labels mismatch",
    )
    audit.require(source_scope_guard.get("exact_match_required") is True, "bundle source-scope exact-match guard")
    audit.require(source_scope_guard.get("seed0_sources_read_only") is True, "bundle seed-0 source read-only guard")
    recorded_root = Path(str(manifest.get("production_root", ""))).expanduser().resolve()
    audit.require(recorded_root == production_root, "bundle production_root provenance mismatch")

    producer = manifest.get("producer")
    audit.require(isinstance(producer, dict), "bundle producer evidence missing")
    producer_path = Path(str(producer.get("path", ""))).expanduser().resolve()
    audit.require(producer_path.name == "vda4_spatial_scaling_endpoint_replication.py", "unexpected bundle producer filename")
    audit.require(producer_path.is_file() and not producer_path.is_symlink(), "bundle producer source unavailable")
    verify_hash_and_bytes(producer_path, producer, audit, "bundle producer")

    source_evidence = manifest.get("source_evaluations")
    audit.require(isinstance(source_evidence, list) and len(source_evidence) == 4, "bundle must declare four source evaluations")
    evidence_by_label: dict[str, dict[str, Any]] = {}
    for entry in source_evidence:
        audit.require(isinstance(entry, dict), "malformed bundle source evidence")
        label = entry.get("label")
        audit.require(label in labels, f"bundle declares unexpected source {label!r}")
        audit.require(label not in evidence_by_label, f"bundle declares duplicate source {label!r}")
        evidence_by_label[str(label)] = entry
    audit.require(set(evidence_by_label) == labels, "bundle source evidence coverage mismatch")
    for source in sources:
        _normalize_source_evidence(evidence_by_label[source.label], source, audit)

    outputs = manifest.get("outputs")
    audit.require(isinstance(outputs, dict), "bundle outputs evidence is not an object")
    audit.require(set(outputs) == REQUIRED_OUTPUTS, f"bundle outputs must be exactly {sorted(REQUIRED_OUTPUTS)}")
    actual_top_level_files = {
        path.name for path in bundle_root.iterdir() if path.is_file() and path.name != "MANIFEST.json"
    }
    audit.require(actual_top_level_files == REQUIRED_OUTPUTS, "bundle output/file coverage mismatch")
    audit.require(
        all(path.is_file() for path in bundle_root.iterdir()),
        "bundle contains undeclared directories or non-file entries",
    )
    for name in sorted(outputs):
        audit.require("seed0" not in name.lower(), f"seed-0 output reused in replication bundle: {name}")
        path = safe_regular_file(bundle_root, name, audit)
        verify_hash_and_bytes(path, outputs[name], audit, f"bundle output/{name}")
    validate_figure(bundle_root / FIGURE_PNG, audit, f"bundle output/{FIGURE_PNG}")
    validate_figure(bundle_root / FIGURE_PDF, audit, f"bundle output/{FIGURE_PDF}")

    metrics_rows = read_metrics_csv(bundle_root / METRICS_FILENAME, audit)
    audit.require(len(metrics_rows) == 4, "metrics CSV must contain exactly four endpoint rows")
    expected_by_identity = {(source.seed, source.metrics["grid"]): source.metrics for source in sources}
    seen: set[tuple[int, str]] = set()
    for row in metrics_rows:
        identity = (
            _integer(row.get("seed"), audit, "metrics CSV/seed"),
            str(row.get("grid")),
        )
        audit.require(identity in expected_by_identity, f"metrics CSV: unexpected identity {identity}")
        audit.require(identity not in seen, f"metrics CSV: duplicate identity {identity}")
        seen.add(identity)
        compare_metric_row(row, expected_by_identity[identity], audit, f"metrics CSV/{identity}")
    audit.require(seen == set(expected_by_identity), "metrics CSV endpoint coverage mismatch")

    summary = read_json(bundle_root / "SUMMARY.json", audit)
    validate_summary(summary, sources, audit)
    manifest_sha = sha256_file(manifest_path)
    audit.hashes_verified += 1
    return {
        "status": "PASS",
        "analysis": ANALYSIS_NAME,
        "bundle_root": str(bundle_root),
        "bundle_manifest_sha256": manifest_sha,
        "source_evaluations_verified": 4,
        "source_artifacts_verified": sum(len(source.artifacts) for source in sources),
        "bundle_outputs_verified": len(outputs),
        "hashes_verified": audit.hashes_verified,
        "figures_decoded": audit.figures_decoded,
        "semantic_checks": audit.semantic_checks,
        "read_only": True,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-root", type=Path, required=True)
    parser.add_argument("--bundle-root", type=Path, required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        result = validate_bundle(args.production_root, args.bundle_root)
    except VerificationError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
