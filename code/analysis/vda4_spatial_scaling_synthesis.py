"""Synthesize the six cached VDA4 seed-0 spatial-scaling evaluations.

This consumer never loads a checkpoint or executes the model.  It first verifies
each complete source manifest and every hash-bound artifact, then reads the three
NPZ caches and writes a compact, immutable comparison bundle through a unique
staging directory and an atomic directory rename.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np


VALIDITIES = np.asarray([0.25, 0.50, 0.75, 1.00], dtype=np.float64)
MAGNITUDES = np.asarray([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0], dtype=np.float64)
TOKEN_COUNTS = (4, 16, 100)
GRIDS = ((2, 2), (4, 4), (10, 10))
FEEDBACKS = ("crossattn1", "affine_ew")
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
SOURCE_NAME = re.compile(r"vda4_(crossattn1|affine_ew)_grid(2x2|4x4|10x10)_seed0")


@dataclass(frozen=True)
class Source:
    directory: Path
    label: str
    feedback: str
    rows: int
    cols: int
    n_tokens: int
    manifest: dict[str, Any]
    manifest_sha256: str
    manifest_bytes: int
    artifacts: dict[str, dict[str, Any]]
    config: dict[str, Any]


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
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite_array(value: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(value)
    require(np.issubdtype(array.dtype, np.number), f"{name} is not numeric")
    require(bool(np.all(np.isfinite(array))), f"{name} contains non-finite values")
    return array


def scalar(value: np.ndarray, name: str) -> Any:
    array = np.asarray(value)
    require(array.ndim == 0, f"{name} is not scalar")
    return array.item()


def source_label(feedback: str, rows: int, cols: int) -> str:
    return f"vda4_{feedback}_grid{rows}x{cols}_seed0"


def safe_artifact_path(source_dir: Path, key: str) -> Path:
    require("\\" not in key, f"manifest artifact key is not canonical POSIX: {key!r}")
    relative = PurePosixPath(key)
    require(not relative.is_absolute() and ".." not in relative.parts and "." not in relative.parts,
            f"unsafe manifest artifact path: {key!r}")
    path = source_dir.joinpath(*relative.parts)
    resolved_root = source_dir.resolve()
    resolved = path.resolve()
    require(resolved_root in resolved.parents, f"artifact escapes source directory: {key!r}")
    require(path.is_file() and not path.is_symlink(), f"artifact is missing or not a regular file: {path}")
    return path


def expected_region_tokens(rows: int, cols: int) -> list[list[int]]:
    regions: list[list[int]] = []
    for location in range(4):
        task_row, task_col = divmod(location, 2)
        row_start, row_stop = task_row * (rows // 2), (task_row + 1) * (rows // 2)
        col_start, col_stop = task_col * (cols // 2), (task_col + 1) * (cols // 2)
        regions.append([r * cols + c for r in range(row_start, row_stop) for c in range(col_start, col_stop)])
    return regions


def validate_source(directory: Path, feedback: str, rows: int, cols: int) -> Source:
    label = source_label(feedback, rows, cols)
    require(directory.name == label, f"unexpected source directory name: {directory.name}")
    manifest_path = directory / "MANIFEST.json"
    require(manifest_path.is_file() and not manifest_path.is_symlink(), f"missing source manifest: {manifest_path}")
    manifest = read_json(manifest_path)
    require(manifest.get("schema_version") == 1, f"{label}: unsupported manifest schema")
    require(manifest.get("status") == "complete", f"{label}: source manifest is not complete")
    require(manifest.get("config_path") == "analysis_config.json", f"{label}: unexpected config path")
    require(manifest.get("summary_path") == "SUMMARY.json", f"{label}: unexpected summary path")

    model = manifest.get("model")
    require(isinstance(model, dict), f"{label}: missing manifest model metadata")
    expected_model = {
        "label": label,
        "task": "vda4",
        "feedback": feedback,
        "grid_rows": rows,
        "grid_cols": cols,
        "n_tokens": rows * cols,
        "checkpoint_iteration": 19999,
    }
    for key, expected in expected_model.items():
        require(model.get(key) == expected, f"{label}: model.{key}={model.get(key)!r}, expected {expected!r}")
    for key in ("checkpoint_sha256", "producer_sha256"):
        value = str(model.get(key, "")).lower()
        require(bool(HEX64.fullmatch(value)), f"{label}: invalid model.{key}")

    declared = manifest.get("artifact_hashes")
    require(isinstance(declared, dict), f"{label}: artifact_hashes is not an object")
    declared_keys = set(declared)
    require(REQUIRED_ARTIFACTS <= declared_keys,
            f"{label}: missing required artifacts {sorted(REQUIRED_ARTIFACTS - declared_keys)}")
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

    # JSON source artifacts are read only after their hashes have been verified.
    config = read_json(directory / "analysis_config.json")
    summary = read_json(directory / "SUMMARY.json")
    for document_name, document in (("analysis_config", config), ("SUMMARY", summary)):
        document_model = document if document_name == "analysis_config" else document.get("model")
        require(isinstance(document_model, dict), f"{label}: {document_name} lacks model metadata")
        for key, expected in expected_model.items():
            require(document_model.get(key) == expected,
                    f"{label}: {document_name}.{key} does not match manifest")
        require(document_model.get("checkpoint_sha256") == model.get("checkpoint_sha256"),
                f"{label}: {document_name} checkpoint hash mismatch")
        require(document_model.get("producer_sha256") == model.get("producer_sha256"),
                f"{label}: {document_name} producer hash mismatch")
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
        feedback=feedback,
        rows=rows,
        cols=cols,
        n_tokens=rows * cols,
        manifest=manifest,
        manifest_sha256=sha256_file(manifest_path),
        manifest_bytes=manifest_path.stat().st_size,
        artifacts=artifacts,
        config=config,
    )


def validate_sources(production_root: Path) -> list[Source]:
    expected = {source_label(feedback, rows, cols) for feedback in FEEDBACKS for rows, cols in GRIDS}
    seed0_dirs = {
        path.name
        for path in production_root.iterdir()
        if path.is_dir() and path.name.startswith("vda4_") and path.name.endswith("_seed0")
    }
    require(seed0_dirs == expected,
            f"production root must contain exactly the six registered seed-0 evaluations; missing={sorted(expected-seed0_dirs)}, extra={sorted(seed0_dirs-expected)}")
    require(all(SOURCE_NAME.fullmatch(name) for name in seed0_dirs), "unregistered seed-0 source directory")
    sources = [
        validate_source(production_root / source_label(feedback, rows, cols), feedback, rows, cols)
        for feedback in FEEDBACKS
        for rows, cols in GRIDS
    ]
    require(len({source.manifest["model"]["checkpoint_sha256"] for source in sources}) == 6,
            "the six evaluations do not reference six distinct checkpoints")
    require(len({source.manifest["model"]["producer_sha256"] for source in sources}) == 1,
            "the six evaluations were not generated by one evaluator source hash")
    return sources


def validate_npz_metadata(data: dict[str, np.ndarray], source: Source, cache_name: str) -> None:
    model = source.manifest["model"]
    expected = {
        "meta_label": source.label,
        "meta_task": "vda4",
        "meta_feedback": source.feedback,
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
    # Called only after validate_sources has verified every artifact in every source.
    with np.load(path, allow_pickle=False) as archive:
        return {key: archive[key] for key in archive.files}


def validate_and_load_caches(source: Source) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    psych = load_npz(source.directory / "data" / "psychometrics.npz")
    attention = load_npz(source.directory / "data" / "event_attention.npz")
    interventions = load_npz(source.directory / "data" / "interventions.npz")
    for name, data in (("psychometrics", psych), ("event_attention", attention), ("interventions", interventions)):
        validate_npz_metadata(data, source, name)

    trials_psych, trials_attention, trials_intervention = 300, 128, 250
    require(psych["response_count"].shape == (4, 10, 2), f"{source.label}: psychometric count shape")
    require(psych["response_rate"].shape == (4, 10, 2), f"{source.label}: psychometric rate shape")
    require(psych["mean_rt"].shape == (4, 10, 2), f"{source.label}: psychometric RT shape")
    require(psych["press_histogram"].shape == (4, 10, 2, 8), f"{source.label}: psychometric histogram shape")
    counts = finite_array(psych["response_count"], f"{source.label}/response_count")
    rates = finite_array(psych["response_rate"], f"{source.label}/response_rate")
    require(bool(np.all((rates >= 0.0) & (rates <= 1.0))), f"{source.label}: response rate outside [0,1]")
    require(bool(np.allclose(rates, counts / trials_psych, atol=1e-12)), f"{source.label}: response count/rate mismatch")
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
    expected_keys = source.n_tokens * (2 if source.feedback == "crossattn1" else 1)
    require(attention["raw_attention_mean"].shape == (2, 7, source.n_tokens, expected_keys),
            f"{source.label}: raw-attention shape")
    token_mass = finite_array(attention["token_mass"], f"{source.label}/token_mass")
    region_mass = finite_array(attention["region_mass"], f"{source.label}/region_mass")
    finite_array(attention["raw_attention_mean"], f"{source.label}/raw_attention_mean")
    require(bool(np.allclose(token_mass.sum(axis=-1), 1.0, atol=2e-5)), f"{source.label}: token mass is not normalized")
    require(bool(np.allclose(region_mass.sum(axis=-1), 1.0, atol=2e-5)), f"{source.label}: region mass is not normalized")
    rebuilt = np.stack(
        [token_mass[..., tokens].sum(axis=-1) for tokens in expected_region_tokens(source.rows, source.cols)],
        axis=-1,
    )
    require(bool(np.allclose(region_mass, rebuilt, atol=2e-5)), f"{source.label}: cached regional mass does not match token mass")

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
    expected_permutation = source.n_tokens * (2 if source.feedback == "crossattn1" else 1)
    permutation = finite_array(interventions["shuffle_permutation"], f"{source.label}/shuffle_permutation")
    require(permutation.shape == (expected_permutation,), f"{source.label}: shuffle permutation length")
    require(sorted(permutation.astype(int).tolist()) == list(range(expected_permutation)),
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


def compute_rows(sources: list[Source]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in sources:
        psych, attention, interventions = validate_and_load_caches(source)
        response = psych["response_rate"].astype(np.float64)
        mean_rt = psych["mean_rt"].astype(np.float64)
        region_mass = attention["region_mass"].astype(np.float64)
        explicit = interventions["explicit_response_rate"].astype(np.float64)
        valid_localized = float(region_mass[0, :, 5:7, 0].mean())
        invalid_localized = float(region_mass[1, :, 5:7, 3].mean())
        invalid_explicit = {mode: float(explicit[index, 1]) for index, mode in enumerate(EXPLICIT_MODES)}
        dependence_pp = 100.0 * (invalid_explicit["natural"] - invalid_explicit["disable"])
        for validity_index, validity in enumerate(VALIDITIES):
            valid_threshold = monotone_threshold(MAGNITUDES, response[validity_index, :, 0])
            invalid_threshold = monotone_threshold(MAGNITUDES, response[validity_index, :, 1])
            normalized_auc = float(
                np.trapz(response[validity_index, :, 0] - response[validity_index, :, 1], x=MAGNITUDES)
                / (MAGNITUDES[-1] - MAGNITUDES[0])
            )
            row = {
                "feedback": source.feedback,
                "model": "Cross-attention" if source.feedback == "crossattn1" else "Affine EW",
                "grid": f"{source.rows}x{source.cols}",
                "n_tokens": source.n_tokens,
                "seed": 0,
                "displayed_validity": float(validity),
                "valid_threshold_deg": valid_threshold,
                "invalid_threshold_deg": invalid_threshold,
                "threshold_cost_invalid_minus_valid_deg": invalid_threshold - valid_threshold,
                "normalized_response_auc_valid_minus_invalid": normalized_auc,
                "rt30_invalid_minus_valid_frames": float(
                    mean_rt[validity_index, -1, 1] - mean_rt[validity_index, -1, 0]
                ),
                "valid_tl_region0_mass_frames5_6": valid_localized,
                "invalid_br_region3_mass_frames5_6": invalid_localized,
                "explicit_natural_invalid_response_rate": invalid_explicit["natural"],
                "explicit_uniform_invalid_response_rate": invalid_explicit["uniform"],
                "explicit_shuffle_invalid_response_rate": invalid_explicit["shuffle"],
                "explicit_disable_invalid_response_rate": invalid_explicit["disable"],
                "causal_dependence_natural_minus_disable_pp": dependence_pp,
                "source_manifest_sha256": source.manifest_sha256,
            }
            require(all(math.isfinite(value) for value in row.values() if isinstance(value, float)),
                    f"computed non-finite metric for {source.label} validity={validity}")
            rows.append(row)
    return rows


def write_metrics(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format(value, ".12g") if isinstance(value, float) else value for key, value in row.items()})


def configure_plots() -> Any:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9.2,
        "axes.titlesize": 10.0,
        "axes.labelsize": 9.2,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.0,
        "axes.linewidth": 0.8,
        "lines.linewidth": 2.0,
        "lines.markersize": 5.5,
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    return plt


def plot_summary(path_stem: Path, rows: list[dict[str, Any]]) -> None:
    plt = configure_plots()
    figure, axes = plt.subplots(2, 2, figsize=(7.25, 5.65), constrained_layout=True)
    figure.suptitle("VDA4 spatial discretization: held-out seed-0 synthesis", fontsize=12.0, fontweight="bold")
    styles = {
        "crossattn1": {"label": "Cross-attention", "color": "#2F6FB0", "marker": "o", "linestyle": "-"},
        "affine_ew": {"label": "Affine EW", "color": "#7B4FA3", "marker": "s", "linestyle": "--"},
    }
    hundred = [row for row in rows if math.isclose(row["displayed_validity"], 1.0)]
    for feedback in FEEDBACKS:
        subset = sorted((row for row in hundred if row["feedback"] == feedback), key=lambda row: row["n_tokens"])
        x = [row["n_tokens"] for row in subset]
        style = styles[feedback]
        axes[0, 0].plot(x, [row["threshold_cost_invalid_minus_valid_deg"] for row in subset],
                        label=style["label"], color=style["color"], marker=style["marker"],
                        linestyle=style["linestyle"])
        axes[0, 1].plot(x, [row["normalized_response_auc_valid_minus_invalid"] for row in subset],
                        color=style["color"], marker=style["marker"], linestyle=style["linestyle"])
        axes[1, 0].plot(x, [row["valid_tl_region0_mass_frames5_6"] for row in subset],
                        label=f"{style['label']} - valid TL", color=style["color"], marker=style["marker"],
                        markerfacecolor=style["color"], linestyle="-")
        axes[1, 0].plot(x, [row["invalid_br_region3_mass_frames5_6"] for row in subset],
                        label=f"{style['label']} - invalid BR", color=style["color"], marker=style["marker"],
                        markerfacecolor="white", markeredgewidth=1.4, linestyle="--")
        axes[1, 1].plot(x, [row["causal_dependence_natural_minus_disable_pp"] for row in subset],
                        color=style["color"], marker=style["marker"], linestyle=style["linestyle"])

    axes[0, 0].set_title("A  50% threshold cost at 100% validity", loc="left", fontweight="bold")
    axes[0, 0].set_ylabel("invalid - valid threshold (deg)")
    axes[0, 0].legend(frameon=False, title="Routing family", title_fontsize=8.0)
    axes[0, 1].set_title("B  Response AUC gap at 100% validity", loc="left", fontweight="bold")
    axes[0, 1].set_ylabel("valid - invalid normalized AUC")
    axes[1, 0].set_title("C  Event-localized regional mass (frames 5-6)", loc="left", fontweight="bold")
    axes[1, 0].set_ylabel("absolute regional mass")
    axes[1, 0].set_ylim(0.23, 1.10)
    axes[1, 0].axhline(0.25, color="#666666", linewidth=1.0, linestyle=":", zorder=0)
    axes[1, 0].text(4.15, 0.263, "uniform region mass", color="#555555", fontsize=7.2)
    axes[1, 0].legend(
        frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=2,
        columnspacing=0.8, handlelength=1.9, fontsize=7.3,
    )
    axes[1, 1].set_title("D  Invalid-response causal dependence", loc="left", fontweight="bold")
    axes[1, 1].set_ylabel("natural - disable (pp)")
    axes[1, 1].axhline(0.0, color="#666666", linewidth=1.0, linestyle=":", zorder=0)

    for axis in axes.flat:
        axis.set_xscale("log")
        axis.set_xlim(3.3, 121.0)
        axis.set_xticks(TOKEN_COUNTS, labels=("4", "16", "100"))
        axis.set_xlabel("sensory / memory tokens")
        axis.grid(axis="y", color="#D7D7D7", linewidth=0.7)
        axis.spines[["top", "right"]].set_visible(False)
    figure.savefig(path_stem.with_suffix(".pdf"), bbox_inches="tight")
    figure.savefig(path_stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(figure)


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


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(jsonable(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-root", type=Path, required=True,
                        help="root containing exactly six complete seed-0 evaluation directories")
    parser.add_argument("--output-root", type=Path,
                        help="final synthesis directory (default: PRODUCTION_ROOT/synthesis_seed0)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    production_root = args.production_root.expanduser().resolve()
    require(production_root.is_dir(), f"production root does not exist: {production_root}")
    output_root = (args.output_root.expanduser().resolve() if args.output_root
                   else production_root / "synthesis_seed0")
    if output_root.exists():
        raise FileExistsError(f"refusing to overwrite output root: {output_root}")

    started = time.time()
    sources = validate_sources(production_root)
    print(f"[validated] six manifests and {sum(len(source.artifacts) for source in sources)} source artifact hashes", flush=True)
    rows = compute_rows(sources)
    require(len(rows) == 24, f"expected 24 model/grid/validity metric rows, got {len(rows)}")

    output_root.parent.mkdir(parents=True, exist_ok=True)
    # Keep the unique staging basename short enough for conservative Windows
    # MAX_PATH configurations; the production root itself is already long.
    staging = output_root.parent / f".s0.partial.{uuid.uuid4().hex[:10]}"
    staging.mkdir()
    print(f"[staging] {staging}", flush=True)
    metrics_path = staging / "vda4_spatial_scaling_seed0_metrics.csv"
    figure_stem = staging / "vda4_spatial_scaling_seed0_summary"
    write_metrics(metrics_path, rows)
    plot_summary(figure_stem, rows)

    source_evidence = [
        {
            "label": source.label,
            "relative_path": source.directory.relative_to(production_root).as_posix(),
            "manifest_sha256": source.manifest_sha256,
            "manifest_bytes": source.manifest_bytes,
            "checkpoint_sha256": source.manifest["model"]["checkpoint_sha256"],
            "producer_sha256": source.manifest["model"]["producer_sha256"],
            "artifacts": source.artifacts,
        }
        for source in sources
    ]
    hundred = [row for row in rows if math.isclose(row["displayed_validity"], 1.0)]
    summary = {
        "schema_version": 1,
        "status": "complete",
        "analysis": "cached-artifact-only VDA4 spatial-scaling synthesis",
        "training_accuracy_used_as_attention_evidence": False,
        "source_evaluation_count": 6,
        "metric_definitions": {
            "threshold": "linear crossing of 0.5 on the cumulative-maximum response-rate envelope",
            "threshold_cost": "invalid threshold minus valid threshold, degrees",
            "normalized_response_auc": "trapezoidal integral of valid minus invalid response rate over 0-30 degrees, divided by 30 degrees",
            "rt30_cost": "invalid minus valid mean qualifying response frame at 30 degrees",
            "event_localization": "mean regional attention mass over trials and frames 5-6; valid uses TL region 0, invalid uses BR region 3",
            "causal_dependence": "natural minus disable invalid response rate, percentage points",
        },
        "metrics_at_100pct_validity": hundred,
        "all_metrics_path": metrics_path.name,
        "interpretation": {
            "finding_1": "No monotonic architecture-independent scaling law is supported: threshold cost and normalized response AUC do not change monotonically in a shared way across both routing families.",
            "finding_2": "The increase in natural-minus-disable invalid-response dependence is affine-specific in these caches (38.4, 98.0, and 99.2 percentage points at 4, 16, and 100 tokens); cross-attention instead measures 12.4, 8.0, and 1.2 percentage points.",
            "finding_3": "Event-localized regional attention concentration does not increase with token count in either routing family.",
            "limitations": [
                "All six cells use seed 0 only; there is no replication uncertainty estimate.",
                "Token count and model parameter count co-vary, so these comparisons do not isolate a token-count causal effect.",
                "The physical VDA4 task has four regions throughout; this is a spatial-discretization comparison, not evidence for a general set-size mechanism.",
            ],
        },
        "source_manifests": [
            {"label": source.label, "sha256": source.manifest_sha256, "bytes": source.manifest_bytes}
            for source in sources
        ],
        "elapsed_seconds": time.time() - started,
    }
    summary_path = staging / "SUMMARY.json"
    write_json(summary_path, summary)

    outputs = {}
    for path in sorted(staging.iterdir()):
        if path.is_file():
            outputs[path.name] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    script_path = Path(__file__).resolve()
    manifest = {
        "schema_version": 1,
        "status": "complete",
        "analysis": "cached-artifact-only VDA4 spatial-scaling synthesis",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "producer": {"path": str(script_path), "sha256": sha256_file(script_path), "bytes": script_path.stat().st_size},
        "production_root": str(production_root),
        "source_evaluations": source_evidence,
        "outputs": outputs,
        "atomic_promotion": True,
    }
    write_json(staging / "MANIFEST.json", manifest)

    # Verify the just-written bundle independently before the no-clobber rename.
    recorded = read_json(staging / "MANIFEST.json")["outputs"]
    require(set(recorded) == {path.name for path in staging.iterdir() if path.is_file() and path.name != "MANIFEST.json"},
            "staged output coverage mismatch")
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
