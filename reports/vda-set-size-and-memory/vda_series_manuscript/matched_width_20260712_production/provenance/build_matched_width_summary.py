#!/usr/bin/env python3
"""Build and audit a provenance-closed summary of the matched-width VDA battery."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

MODEL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODEL_ROOT.parent
DEFAULT_INPUT = MODEL_ROOT / "vda_sweep" / "derived" / "2026-07-11_matched_width"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "vda_series" / "matched_width_20260712_production"
TASKS = ("vda1", "vda4", "vda9")
FEEDBACKS = ("affine_ew", "crossattn1")
WIDTHS = (128, 256)
VARIABLES = ("change", "change_location", "cued_change")
COLORS = {"vda1": "#0072B2", "vda4": "#009E73", "vda9": "#D55E00"}
MARKERS = {"affine_ew": "o", "crossattn1": "s"}
LINESTYLES = {"affine_ew": "-", "crossattn1": "--"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def width_difference(d128: np.ndarray, d256: np.ndarray) -> np.ndarray:
    """Return the declared architectural contrast, d256 minus d128."""
    return np.asarray(d256, dtype=float) - np.asarray(d128, dtype=float)


def clamp_width_difference_in_differences(
    d128: np.ndarray, d256: np.ndarray, *, baseline_index: int
) -> np.ndarray:
    """Contrast width-associated clamp effects after subtracting each width's zero-bias value."""
    raw = width_difference(d128, d256)
    return raw - raw[baseline_index]


def width_pair_is_admissible(
    competence_flags: list[dict[str, Any]], task: str, feedback: str
) -> bool:
    """Exclude a width pair when either member has a registered competence gate."""
    return not any(
        flag.get("task") == task
        and flag.get("feedback") == feedback
        and flag.get("status") == "competence_gated"
        for flag in competence_flags
    )


def regular_files(root: Path) -> set[Path]:
    root = Path(os.path.abspath(root))
    if root.is_symlink() or not root.is_dir():
        raise FileNotFoundError(f"not a regular directory: {root}")
    files: set[Path] = set()
    for path in root.rglob("*"):
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise RuntimeError(f"symlink or special file rejected: {path}")
        files.add(path)
    return files


def audit_upstream(root: Path) -> dict[str, Any]:
    subprocess.run(
        [sys.executable, str(MODEL_ROOT / "scripts" / "run_matched_width.py"), "--audit"],
        cwd=MODEL_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    manifest_path = root / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported upstream manifest schema")
    if len(manifest.get("shards", [])) != 12:
        raise ValueError("upstream manifest must admit exactly 12 shards")
    expected = {root / str(record["path"]) for record in manifest["shards"]}
    for record in manifest["shards"]:
        path = root / str(record["path"])
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(path)
        if path.stat().st_size != int(record["bytes"]) or sha256(path) != record["sha256"]:
            raise RuntimeError(f"upstream shard identity mismatch: {path}")
    if expected != {path for path in regular_files(root) if path.parent == root / "shards"}:
        raise RuntimeError("upstream shard inventory mismatch")
    return manifest


def load_shards(root: Path, manifest: dict[str, Any]) -> dict[tuple[str, str, int], dict[str, np.ndarray]]:
    shards: dict[tuple[str, str, int], dict[str, np.ndarray]] = {}
    for record in manifest["shards"]:
        path = root / str(record["path"])
        with np.load(path, allow_pickle=False) as handle:
            payload = {name: np.array(handle[name]) for name in handle.files}
        metadata = json.loads(str(payload["metadata_json"].item()))
        key = (str(metadata["task"]), str(metadata["feedback"]), int(metadata["width"]))
        if key in shards:
            raise RuntimeError(f"duplicate shard key: {key}")
        shards[key] = payload
    expected = {(task, feedback, width) for task in TASKS for feedback in FEEDBACKS for width in WIDTHS}
    if set(shards) != expected:
        raise RuntimeError(f"unexpected shard scope: {sorted(shards)}")
    return shards


def compute_summary(
    shards: dict[tuple[str, str, int], dict[str, np.ndarray]],
    competence_flags: list[dict[str, Any]],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for task in TASKS:
        for feedback in FEEDBACKS:
            if not width_pair_is_admissible(competence_flags, task, feedback):
                exclusions.append(
                    {
                        "task": task,
                        "feedback": feedback,
                        "reason": "d256 checkpoint is competence_gated; no width contrast is estimated",
                    }
                )
                continue
            a = shards[(task, feedback, 128)]
            b = shards[(task, feedback, 256)]
            if not np.array_equal(a["change_magnitudes"], b["change_magnitudes"]):
                raise RuntimeError(f"change-magnitude axes disagree for {task}/{feedback}")
            if not np.array_equal(a["displayed_validities"], b["displayed_validities"]):
                raise RuntimeError(f"validity axes disagree for {task}/{feedback}")
            if not np.array_equal(a["clamp_key_logit_biases"], b["clamp_key_logit_biases"]):
                raise RuntimeError(f"clamp axes disagree for {task}/{feedback}")
            validity_index = int(np.flatnonzero(a["displayed_validities"] == 0.75)[0])
            biases = a["clamp_key_logit_biases"].astype(float)
            baseline_index = int(np.flatnonzero(biases == 0.0)[0])
            decoder: dict[str, list[float] | None] = {}
            for variable in VARIABLES:
                key = f"decoder_matched128_{variable}"
                if key in a and key in b:
                    decoder[variable] = width_difference(a[key], b[key])[-1:].tolist()
                else:
                    decoder[variable] = None
            records.append(
                {
                    "task": task,
                    "feedback": feedback,
                    "change_magnitudes": a["change_magnitudes"].astype(float).tolist(),
                    "psychometric_valid_p075_d256_minus_d128": width_difference(
                        a["psychometric_response_rate_valid"][validity_index],
                        b["psychometric_response_rate_valid"][validity_index],
                    ).tolist(),
                    "decoder_matched128_t6_d256_minus_d128": decoder,
                    "clamp_key_logit_biases": biases.tolist(),
                    "clamp_valid_dprime_width_effect_did": clamp_width_difference_in_differences(
                        a["clamp_dprime_valid"], b["clamp_dprime_valid"], baseline_index=baseline_index
                    ).tolist(),
                    "clamp_invalid_dprime_width_effect_did": (
                        clamp_width_difference_in_differences(
                            a["clamp_dprime_invalid"],
                            b["clamp_dprime_invalid"],
                            baseline_index=baseline_index,
                        ).tolist()
                        if task != "vda1"
                        else None
                    ),
                }
            )
    return {"records": records, "exclusions": exclusions}


def label(task: str, feedback: str) -> str:
    routing = "affine" if feedback == "affine_ew" else "cross-attention"
    return f"{task.upper()} · {routing}"


def build_figure(summary: dict[str, Any], output_stem: Path) -> None:
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9})
    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.2), constrained_layout=True)
    ax_a, ax_b, ax_c, ax_d = axes.flat
    for ax in axes.flat:
        ax.axhline(0.0, color="#4C566A", linewidth=0.8, zorder=0)
        ax.grid(axis="y", color="#D8DEE9", linewidth=0.55, alpha=0.8)
    for record in summary["records"]:
        task = record["task"]
        feedback = record["feedback"]
        style = dict(
            color=COLORS[task], marker=MARKERS[feedback], linestyle=LINESTYLES[feedback],
            linewidth=1.5, markersize=4.5, label=label(task, feedback),
        )
        ax_a.plot(
            record["change_magnitudes"],
            record["psychometric_valid_p075_d256_minus_d128"],
            **style,
        )
        ax_c.plot(record["clamp_key_logit_biases"], record["clamp_valid_dprime_width_effect_did"], **style)
        invalid = record["clamp_invalid_dprime_width_effect_did"]
        if invalid is not None:
            ax_d.plot(record["clamp_key_logit_biases"], invalid, **style)
    positions = np.arange(len(VARIABLES), dtype=float)
    offsets = np.linspace(-0.24, 0.24, len(summary["records"]))
    for offset, record in zip(offsets, summary["records"], strict=True):
        values = [record["decoder_matched128_t6_d256_minus_d128"][name] for name in VARIABLES]
        for x, value in zip(positions, values, strict=True):
            if value is not None:
                ax_b.plot(
                    x + offset, value[0], color=COLORS[record["task"]],
                    marker=MARKERS[record["feedback"]], markersize=6,
                    markerfacecolor="white" if record["feedback"] == "crossattn1" else COLORS[record["task"]],
                    linestyle="none",
                )
    ax_a.set_title("A  Valid change-response rate at displayed validity 0.75")
    ax_a.set_xlabel("Orientation change (degrees)")
    ax_a.set_ylabel("d256 − d128 response probability")
    ax_b.set_title("B  Foldwise PCA-128 decoder at final timestep t6")
    ax_b.set_xticks(positions, ["change", "change\nlocation", "cued\nchange"])
    ax_b.set_ylabel("d256 − d128 balanced accuracy")
    ax_c.set_title("C  Valid-change clamp effect relative to zero bias")
    ax_c.set_xlabel("Additive cued-key logit bias")
    ax_c.set_ylabel("Width difference-in-differences in d′")
    ax_d.set_title("D  Invalid-change clamp effect relative to zero bias")
    ax_d.set_xlabel("Additive cued-key logit bias")
    ax_d.set_ylabel("Width difference-in-differences in d′")
    note = "VDA9 · cross-attention omitted: d256 checkpoint competence-gated (floor-policy diagnostic)."
    fig.text(0.5, 0.005, note, ha="center", va="bottom", fontsize=9, color="#7A1F1F")
    handles, labels = ax_a.get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.03))
    for suffix in ("pdf", "svg", "png"):
        kwargs = {"dpi": 300} if suffix == "png" else {}
        fig.savefig(output_stem.with_suffix(f".{suffix}"), bbox_inches="tight", **kwargs)
    plt.close(fig)


def manifest_records(root: Path, paths: set[Path]) -> list[dict[str, Any]]:
    return [
        {"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(paths)
    ]


def build(input_root: Path, output_root: Path) -> Path:
    if os.path.lexists(output_root):
        raise FileExistsError(f"fresh output root required: {output_root}")
    startup_bytes = Path(__file__).read_bytes()
    upstream = audit_upstream(input_root)
    shards = load_shards(input_root, upstream)
    summary = compute_summary(shards, list(upstream.get("competence_flags", [])))
    output_root.mkdir(parents=True)
    figures = output_root / "figures"
    provenance = output_root / "provenance"
    figures.mkdir()
    provenance.mkdir()
    stem = figures / "matched_width_summary"
    build_figure(summary, stem)
    upstream_snapshot = provenance / "UPSTREAM_MANIFEST.json"
    upstream_snapshot.write_bytes((input_root / "MANIFEST.json").read_bytes())
    source_snapshot = provenance / "build_matched_width_summary.py"
    source_snapshot.write_bytes(startup_bytes)
    sidecar = {
        "schema_version": 1,
        "artifact_class": "descriptive matched-width summary",
        "evidence_class": "checkpoint-recomputed, single checkpoint per task × routing × width cell",
        "upstream_manifest_sha256": sha256(input_root / "MANIFEST.json"),
        "contrast_direction": "d256 minus d128",
        "psychometric_reference_condition": {"location": "valid", "displayed_validity": 0.75, "trials_per_point": 300},
        "decoder": {"space": "foldwise train-only PCA-128", "timestep": 6, "metric": "balanced accuracy"},
        "clamp": {"intervention": "additive bias on cued routing-key logits at change time", "baseline_key_logit_bias": 0.0, "trials_per_cell": 512},
        "claim_boundary": upstream["claim_boundary"],
        "limits": [
            "Width pairs are separately trained checkpoints, not within-checkpoint causal interventions or independent-seed populations.",
            "Finite-trial aggregate counts do not retain trial pairing, so the plotted contrasts have no paired confidence intervals.",
            "Native-space decoder values are not plotted; panel B uses only foldwise train-only PCA-128 scores.",
            "Timestep t0 is omitted from the decoder summary because pre-stimulus recurrent states are zero-variance and chance-level.",
            "The intervention manipulates key logits, not an observed or clamped achieved allocation value.",
        ],
        **summary,
    }
    sidecar_path = stem.with_suffix(".json")
    sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    expected = regular_files(output_root)
    manifest = {
        "schema_version": 1,
        "artifact_class": "completed matched-width manuscript summary",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_root": str(input_root.resolve()),
        "upstream_manifest_sha256": sha256(input_root / "MANIFEST.json"),
        "source_sha256": hashlib.sha256(startup_bytes).hexdigest(),
        "artifacts": manifest_records(output_root, expected),
    }
    temporary = output_root / ".MANIFEST.json.tmp"
    final = output_root / "MANIFEST.json"
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if regular_files(output_root) != expected | {temporary}:
        raise RuntimeError("prepublication output inventory changed")
    temporary.replace(final)
    audit(output_root)
    return final


def audit(output_root: Path) -> Path:
    manifest_path = output_root / "MANIFEST.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise FileNotFoundError(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported summary manifest schema")
    input_root = Path(str(manifest["input_root"]))
    upstream = audit_upstream(input_root)
    if sha256(input_root / "MANIFEST.json") != manifest["upstream_manifest_sha256"]:
        raise RuntimeError("live upstream manifest identity changed")
    if sha256(output_root / "provenance" / "UPSTREAM_MANIFEST.json") != manifest["upstream_manifest_sha256"]:
        raise RuntimeError("retained upstream manifest identity mismatch")
    if sha256(output_root / "provenance" / "build_matched_width_summary.py") != manifest["source_sha256"]:
        raise RuntimeError("retained builder source identity mismatch")
    expected = {output_root / record["path"] for record in manifest["artifacts"]} | {manifest_path}
    if regular_files(output_root) != expected:
        raise RuntimeError("completed summary inventory mismatch")
    for record in manifest["artifacts"]:
        path = output_root / record["path"]
        if path.stat().st_size != int(record["bytes"]) or sha256(path) != record["sha256"]:
            raise RuntimeError(f"summary artifact identity mismatch: {path}")
    shards = load_shards(input_root, upstream)
    expected_summary = compute_summary(shards, list(upstream.get("competence_flags", [])))
    sidecar = json.loads((output_root / "figures" / "matched_width_summary.json").read_text(encoding="utf-8"))
    if sidecar["records"] != expected_summary["records"] or sidecar["exclusions"] != expected_summary["exclusions"]:
        raise RuntimeError("summary values do not reconstruct from admitted shards")
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--audit", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = audit(args.output_root) if args.audit else build(args.input_root, args.output_root)
    print(path)


if __name__ == "__main__":
    main()
