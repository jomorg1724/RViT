#!/usr/bin/env python3
"""Build a provenance-closed VDA16 cross-attention manuscript evidence shard."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "vda_series" / "vda16_crossattn_nodecay_20260719_production"
HISTORICAL_MATCHED_WIDTH = (
    ROOT / "vda_sweep" / "derived" / "2026-07-11_matched_width" / "shards"
)
SOURCE_DEPENDENCIES = (
    "scripts/build_vda16_manuscript_shard.py",
    "vda_series/vda16_integration.py",
    "vda_series/first_wave_figures.py",
    "vda_series/task_figures.py",
    "vda_sweep/vda_core.py",
    "vda_sweep/vda_fig_decode.py",
    "vda_sweep/matched_width.py",
    "vda_sweep/matched_width_compute.py",
    "vda_sweep/matched_width_producer.py",
    "model.py",
    "conv_frontend.py",
    "vae_frontend.py",
    "paper_encoder.py",
    "paper_heads.py",
    "envs/__init__.py",
    "envs/base.py",
    "envs/tasks.py",
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="completed VDA16 training directory",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--device",
        choices=("cpu", "cuda"),
        default="cuda",
        help="inference device; analysis never updates model weights",
    )
    parser.add_argument("--attention-trials", type=int, default=96)
    parser.add_argument("--psychometric-trials", type=int, default=300)
    parser.add_argument(
        "--audit",
        action="store_true",
        help="read-only validation of an existing completed output tree",
    )
    return parser.parse_args(argv)


def lexical_path(path: str | Path) -> Path:
    """Normalize path syntax without dereferencing its final component."""
    return Path(os.path.abspath(path))


def regular_files(root: str | Path) -> set[Path]:
    """Inventory regular files while rejecting symlinks and special entries."""
    root = lexical_path(root)
    if root.is_symlink() or not root.is_dir():
        raise FileNotFoundError(f"not a regular output directory: {root}")
    files: set[Path] = set()
    for path in root.rglob("*"):
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise RuntimeError(f"symlink or special output entry rejected: {path}")
        files.add(lexical_path(path))
    return files


def require_exact_inventory(root: Path, expected: set[Path]) -> None:
    root = lexical_path(root)
    normalized = {lexical_path(path) for path in expected}
    if any(root not in path.parents for path in normalized):
        raise RuntimeError("expected output path escapes the output root")
    actual = regular_files(root)
    if actual != normalized:
        raise RuntimeError(
            "output inventory mismatch; "
            f"missing={sorted(map(str, normalized - actual))}, "
            f"unmanifested={sorted(map(str, actual - normalized))}"
        )


def _hash_sources(integration: Any) -> dict[str, str]:
    records: dict[str, str] = {}
    for relative in SOURCE_DEPENDENCIES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        records[relative] = integration.sha256_file(path)
    return records


def _capture_source_bytes() -> dict[str, bytes]:
    captured: dict[str, bytes] = {}
    for relative in SOURCE_DEPENDENCIES:
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"analysis source is not a regular file: {path}")
        captured[relative] = path.read_bytes()
    return captured


def _hash_captured_sources(captured: dict[str, bytes]) -> dict[str, str]:
    return {
        relative: hashlib.sha256(content).hexdigest()
        for relative, content in captured.items()
    }


def _freeze_sources(
    source_bytes: dict[str, bytes],
    source_hashes: dict[str, str],
    destination: Path,
    integration: Any,
) -> list[dict[str, Any]]:
    records = []
    for relative, expected in source_hashes.items():
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source_bytes[relative])
        actual = integration.sha256_file(target)
        if actual != expected:
            raise RuntimeError(f"source snapshot digest mismatch: {target}")
        records.append(
            {
                "source": str(source.resolve()),
                "path": str(target.resolve()),
                "sha256": actual,
            }
        )
    return records


def _audit_historical_shards(
    shard_root: Path, provenance_dir: Path, integration: Any
) -> dict[str, Any]:
    upstream_root = shard_root.parent
    manifest_path = upstream_root / "MANIFEST.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    records = manifest.get("shards")
    if not isinstance(records, list) or len(records) != 12:
        raise ValueError("historical matched-width manifest does not contain 12 shards")
    selected = {
        f"{task}_{feedback}_d128.npz"
        for task in ("vda1", "vda4", "vda9")
        for feedback in ("affine_ew", "crossattn1")
    }
    frozen_root = provenance_dir / "historical_shards"
    frozen_root.mkdir(parents=True, exist_ok=False)
    verified = []
    for record in records:
        relative = Path(str(record["path"]))
        if relative.name not in selected:
            continue
        path = upstream_root / relative
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"historical shard is not a regular file: {path}")
        digest = integration.sha256_file(path)
        if path.stat().st_size != int(record["bytes"]) or digest != str(record["sha256"]):
            raise RuntimeError(f"historical matched-width shard identity mismatch: {path}")
        frozen = frozen_root / relative.name
        shutil.copy2(path, frozen)
        if (
            frozen.stat().st_size != path.stat().st_size
            or integration.sha256_file(frozen) != digest
        ):
            raise RuntimeError(f"frozen historical shard identity mismatch: {frozen}")
        verified.append(
            {
                "original_path": str(path.resolve()),
                "frozen_path": str(frozen.resolve()),
                "sha256": digest,
                "bytes": path.stat().st_size,
            }
        )
    if {Path(record["frozen_path"]).name for record in verified} != selected:
        raise RuntimeError("historical d128 routing-family shard scope is incomplete")
    snapshot = provenance_dir / "HISTORICAL_MATCHED_WIDTH_MANIFEST.json"
    snapshot.write_bytes(manifest_bytes)
    if integration.sha256_file(snapshot) != manifest_sha256:
        raise RuntimeError("historical manifest snapshot digest mismatch")
    return {
        "manifest_path": str(manifest_path.resolve()),
        "manifest_sha256": manifest_sha256,
        "snapshot": str(snapshot.resolve()),
        "frozen_shard_root": str(frozen_root.resolve()),
        "selected_shards": verified,
        "lineage_boundary": (
            "historical shards are hash-bound aggregate evidence; this build does not "
            "recompute their checkpoints"
        ),
    }


def _revalidate_historical_evidence(
    historical: dict[str, Any], integration: Any
) -> None:
    manifest_hash = str(historical["manifest_sha256"])
    for path in (
        Path(str(historical["manifest_path"])),
        Path(str(historical["snapshot"])),
    ):
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(path)
        if integration.sha256_file(path) != manifest_hash:
            raise RuntimeError(f"historical manifest identity changed: {path}")
    for record in historical["selected_shards"]:
        for field in ("original_path", "frozen_path"):
            path = Path(str(record[field]))
            if path.is_symlink() or not path.is_file():
                raise FileNotFoundError(path)
            if (
                path.stat().st_size != int(record["bytes"])
                or integration.sha256_file(path) != str(record["sha256"])
            ):
                raise RuntimeError(f"historical shard identity changed: {path}")


def _summary_from_shard(shard_path: Path, admission: dict[str, Any]) -> dict[str, Any]:
    with np.load(shard_path, allow_pickle=False) as payload:
        validities = np.asarray(payload["displayed_validities"], dtype=float)
        magnitudes = np.asarray(payload["change_magnitudes"], dtype=float)
        validity_index = int(np.flatnonzero(np.isclose(validities, 0.75))[0])
        magnitude_index = int(np.argmin(np.abs(magnitudes - 18.0)))
        valid = float(payload["psychometric_response_rate_valid"][validity_index, magnitude_index])
        invalid = float(payload["psychometric_response_rate_invalid"][validity_index, magnitude_index])
        decoder = {
            variable: {
                "native_t6": float(payload[f"decoder_native_{variable}"][-1]),
                "pca128_t6": float(payload[f"decoder_matched128_{variable}"][-1]),
            }
            for variable in (
                "colour",
                "validity",
                "change",
                "change_location",
                "cued_change",
            )
        }
        clamp = {
            "key_logit_biases": np.asarray(payload["clamp_key_logit_biases"], dtype=float).tolist(),
            "valid_dprime": np.asarray(payload["clamp_dprime_valid"], dtype=float).tolist(),
            "invalid_dprime": np.asarray(payload["clamp_dprime_invalid"], dtype=float).tolist(),
            "valid_criterion": np.asarray(payload["clamp_criterion_valid"], dtype=float).tolist(),
            "invalid_criterion": np.asarray(payload["clamp_criterion_invalid"], dtype=float).tolist(),
        }
    return {
        "task": "vda16",
        "feedback": "crossattn1",
        "width": 128,
        "memory_decay": 1.0,
        "checkpoint_iteration": 19999,
        "training": admission["training"],
        "psychometric_probe": {
            "displayed_validity": float(validities[validity_index]),
            "orientation_change_degrees": float(magnitudes[magnitude_index]),
            "valid_response_rate": valid,
            "forced_invalid_response_rate": invalid,
            "valid_minus_invalid": valid - invalid,
        },
        "decoder": decoder,
        "clamp": clamp,
        "claim_boundary": admission["claim_boundary"],
    }


def _write_summary_csv(path: Path, summary: dict[str, Any]) -> None:
    rows = [
        ("training", "status", summary["training"]["status"]),
        ("training", "final_theta_degrees", summary["training"]["final_theta_degrees"]),
        (
            "training",
            "late50_mean_rolling_correct",
            summary["training"]["late50_mean_rolling_correct"],
        ),
        (
            "psychometric",
            "valid_minus_invalid_p075_nearest_d18",
            summary["psychometric_probe"]["valid_minus_invalid"],
        ),
    ]
    for variable, record in summary["decoder"].items():
        rows.append(("decoder_native_t6", variable, record["native_t6"]))
        rows.append(("decoder_pca128_t6", variable, record["pca128_t6"]))
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write("family,metric,value\n")
        for family, metric, value in rows:
            stream.write(f"{family},{metric},{value}\n")


def _write_manuscript_fragments(
    output_root: Path, summary: dict[str, Any], admission: dict[str, Any]
) -> tuple[Path, Path]:
    markdown_path = output_root / "MANUSCRIPT_INTEGRATION.md"
    tex_path = output_root / "manuscript" / "vda16_results_fragment.tex"
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    probe = summary["psychometric_probe"]
    training = summary["training"]
    markdown = f"""# VDA16 cross-attention manuscript integration

This bundle adds one descriptive VDA16 cell to the VDA evidence series using the
same matched trial-bank psychometrics, native/PCA-128 decoders, graded key-logit
clamps, and source-resolved attention analysis used by the current VDA pipelines.

## Result boundary

- Checkpoint: iteration 19,999, SHA-256 `{admission['checkpoint_sha256']}`
- Architecture: cross-attention, d_mem=128, memory decay=1.0, 4×4/16 tokens
- Training status: **{training['status']}**
- Final theta: {training['final_theta_degrees']:.1f} degrees
- Late-50 rolling correctness: {training['late50_mean_rolling_correct']:.3f}
- At displayed validity .75 and the nearest sampled change to 18 degrees:
  valid={probe['valid_response_rate']:.3f}, forced-invalid={probe['forced_invalid_response_rate']:.3f},
  difference={probe['valid_minus_invalid']:+.3f}

The current repository extract does not contain the global VDA manuscript source
expected by `tests/test_vda_build_manifest.py`. The LaTeX fragment and PDF/SVG/PNG
figures in this bundle are therefore manuscript-ready, but have not been inserted
into an absent global source tree. The canonical M3 registry consequently remains
blocked for VDA16, and the descriptive task-sequence panel omits VDA2 because no
compatible modern matched-width VDA2 shard exists.

## Required caveats

This is a single seed and a single cross-attention/d128/no-decay checkpoint.
VDA16 affine, d256, decay contrasts, and seed-level uncertainty are unavailable.
The historical VDA1/VDA4/VDA9 comparison is descriptive because task geometry and
token count change together. Historical and VDA16 cells also come from separately
frozen executable/runtime lineages. Cross-method intervention effects are not
compared at nominal clamp dose; equal logit biases do not imply equal achieved
attention mass. Because training remained at theta={training['final_theta_degrees']:.1f}
degrees, mechanistic outputs are competence-gated and should be described as an
easiest-condition diagnostic.
"""
    markdown_path.write_text(markdown, encoding="utf-8")
    tex = rf"""\subsection{{VDA16 cross-attention checkpoint}}
\label{{sec:vda16_crossattn}}

We evaluated one VDA16 cross-attention checkpoint ($d_\mathrm{{mem}}=128$,
memory decay $=1.0$, seed 0) at terminal iteration 19,999 using the same
deterministic psychometric, recurrent-decoder, and attention-key clamp protocols
as the VDA analysis series (Fig.~\ref{{fig:vda16_summary}}). At displayed
validity 0.75 and the sampled orientation change nearest $18^\circ$, the
qualifying response rates were {probe['valid_response_rate']:.3f} for valid and
{probe['forced_invalid_response_rate']:.3f} for forced-invalid changes
($\Delta={probe['valid_minus_invalid']:+.3f}$). These are finite-trial estimates
from one checkpoint, not training-seed estimates.

\begin{{figure*}}[t]
  \centering
  \includegraphics[width=\textwidth]{{figures/manuscript/vda16_manuscript_summary.pdf}}
  \caption{{VDA16 cross-attention analysis. (A) Matched-bank response rates.
  (B) Foldwise train-only PCA-128 decoding from recurrent state.
  (C--D) Sensitivity and criterion under additive cued-location attention-key
  logit clamps. The checkpoint is competence-gated because its curriculum
  remained at $\theta={training['final_theta_degrees']:.1f}^\circ$. VDA16
  affine, d256, decay, and replicated-seed cells are unavailable.}}
  \label{{fig:vda16_summary}}
\end{{figure*}}

\begin{{figure*}}[t]
  \centering
  \includegraphics[width=\textwidth]{{figures/manuscript/vda_method_comparison_with_vda16.pdf}}
  \caption{{Descriptive d128 routing-family matrix. The open, unconnected
  VDA16 point is competence-gated and is not part of a fitted or implied
  set-size trend. VDA2 is absent because no compatible modern matched-width
  shard exists. Historical and VDA16 cells use separately frozen
  executable/runtime lineages.}}
  \label{{fig:vda16_method_context}}
\end{{figure*}}

\begin{{figure*}}[t]
  \centering
  \includegraphics[width=\textwidth]{{figures/clamp/vda16_clamp_achieved_attention.pdf}}
  \caption{{Achieved cued-location attention mass under the VDA16 logit-clamp
  series. Image-key and corresponding recurrent-memory-key mass are summed and
  averaged over query tokens. Trial-level error bars describe evaluation trials
  from one checkpoint, not training-seed uncertainty.}}
  \label{{fig:vda16_achieved_attention}}
\end{{figure*}}
"""
    tex_path.write_text(tex, encoding="utf-8")
    return markdown_path, tex_path


def _runtime(device: str) -> dict[str, str]:
    import matplotlib
    import scipy
    import sklearn
    import torch

    return {
        "python": platform.python_version(),
        "python_executable": str(Path(sys.executable).resolve()),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "torch": torch.__version__,
        "device": device,
    }


def audit_completed_output(output_root: str | Path) -> Path:
    """Read-only byte/inventory audit of a published VDA16 bundle."""
    output_root = lexical_path(output_root)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from vda_series import vda16_integration as integration

    files = regular_files(output_root)
    manifest_path = output_root / "MANIFEST.json"
    if manifest_path not in files:
        raise FileNotFoundError(f"completed manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported VDA16 bundle manifest schema")
    records = manifest.get("artifacts")
    if not isinstance(records, list) or not records:
        raise ValueError("VDA16 bundle has no manifested artifacts")
    expected: set[Path] = {manifest_path}
    seen: set[str] = set()
    for record in records:
        relative = str(record["path"])
        if relative in seen:
            raise ValueError(f"duplicate manifested artifact: {relative}")
        seen.add(relative)
        path = lexical_path(output_root / relative.replace("/", os.sep))
        if output_root not in path.parents:
            raise ValueError(f"manifested artifact escapes output root: {relative}")
        expected.add(path)
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or integration.sha256_file(path) != str(record["sha256"])
        ):
            raise RuntimeError(f"manifested artifact identity mismatch: {path}")
    if files != expected:
        raise RuntimeError("completed VDA16 bundle inventory differs from its manifest")
    validation = json.loads(
        (output_root / "provenance" / "VALIDATION_RESULT.json").read_text(
            encoding="utf-8"
        )
    )
    if validation.get("result") != "pass":
        raise RuntimeError("VDA16 validation gate did not pass")
    return manifest_path


def build(args: argparse.Namespace) -> Path:
    if args.run_dir is None:
        raise ValueError("--run-dir is required unless --audit is used")
    run_dir = args.run_dir.resolve()
    output_root = lexical_path(args.output_root)
    if os.path.lexists(output_root):
        raise FileExistsError(f"fresh output root required: {output_root}")
    if args.attention_trials != 96 or args.psychometric_trials != 300:
        raise ValueError("publication build requires attention n=96 and psychometric n=300")
    source_bytes = _capture_source_bytes()
    source_hashes = _hash_captured_sources(source_bytes)
    os.environ["RVIT_DEVICE"] = args.device
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from vda_series import first_wave_figures as first_wave
    from vda_series import vda16_integration as integration
    from vda_sweep import matched_width as matched
    from vda_sweep import matched_width_producer as producer
    from vda_sweep import vda_core as core

    core.DEVICE = args.device
    checkpoint = run_dir / "rvit_paper_vda16_final.pt"
    launch_manifest = run_dir / "launch_manifest.json"
    metrics_path = run_dir / "metrics.csv"
    train_log = run_dir / "train.log"
    for path in (checkpoint, launch_manifest, metrics_path, train_log):
        if path.is_symlink() or not path.is_file():
            raise FileNotFoundError(f"training input is not a regular file: {path}")
    admission = integration.validate_checkpoint_admission(
        checkpoint,
        launch_manifest,
        metrics_path,
        project_root=ROOT,
    )
    output_root.mkdir(parents=True)
    data_dir = output_root / "data"
    figures_dir = output_root / "figures"
    provenance_dir = output_root / "provenance"
    for directory in (data_dir, figures_dir, provenance_dir):
        directory.mkdir(parents=True)

    frozen_checkpoint = provenance_dir / "checkpoints" / checkpoint.name
    frozen_checkpoint.parent.mkdir(parents=True)
    shutil.copy2(checkpoint, frozen_checkpoint)
    if integration.sha256_file(frozen_checkpoint) != admission["checkpoint_sha256"]:
        raise RuntimeError("frozen final checkpoint differs from admitted checkpoint")
    original_input_hashes = {
        "checkpoint": admission["checkpoint_sha256"],
        "launch_manifest": admission["launch_manifest_sha256"],
        "metrics": admission["metrics_sha256"],
        "train_log": integration.sha256_file(train_log),
    }
    for source, name, expected_hash in (
        (launch_manifest, "launch_manifest.json", original_input_hashes["launch_manifest"]),
        (metrics_path, "metrics.csv", original_input_hashes["metrics"]),
        (train_log, "train.log", original_input_hashes["train_log"]),
    ):
        frozen_input = provenance_dir / name
        shutil.copy2(source, frozen_input)
        if integration.sha256_file(frozen_input) != expected_hash:
            raise RuntimeError(f"frozen training input differs from admitted input: {source}")
    frozen_admission = integration.validate_checkpoint_admission(
        frozen_checkpoint,
        provenance_dir / "launch_manifest.json",
        provenance_dir / "metrics.csv",
        project_root=ROOT,
    )
    for field in (
        "checkpoint_sha256",
        "checkpoint_iteration",
        "task",
        "feedback",
        "width",
        "memory_decay",
        "seed",
        "training",
        "launch_manifest_sha256",
        "metrics_sha256",
    ):
        if frozen_admission[field] != admission[field]:
            raise RuntimeError(f"frozen checkpoint admission drifted in field {field}")
    admission["original_checkpoint_path"] = admission["checkpoint_path"]
    admission["checkpoint_path"] = str(frozen_checkpoint.resolve())
    admission["frozen_checkpoint_sha256"] = integration.sha256_file(frozen_checkpoint)

    source_snapshots = _freeze_sources(
        source_bytes,
        source_hashes,
        provenance_dir / "source_snapshot",
        integration,
    )
    historical = _audit_historical_shards(
        HISTORICAL_MATCHED_WIDTH, provenance_dir, integration
    )

    matched.CHECKPOINT_ROOT = frozen_checkpoint.parent
    spec = matched.CheckpointSpec(
        task="vda16",
        feedback="crossattn1",
        width=128,
        relative_path=frozen_checkpoint.name,
        sha256=admission["checkpoint_sha256"],
        grid=(4, 4),
        image_size=100,
        active_locations=tuple(range(16)),
    )
    shard_path = data_dir / "vda16_crossattn1_d128_nodecay_seed0.npz"
    print("[matched protocol] psychometrics + decoders + clamps", flush=True)
    producer.write_shard(spec, shard_path, source_hashes=source_hashes)
    with np.load(shard_path, allow_pickle=False) as payload:
        matched.validate_shard_payload(payload, spec)
    shard_sha256 = integration.sha256_file(shard_path)

    environment_dir = figures_dir / "environment"
    attention_dir = figures_dir / "attention"
    psychometric_dir = figures_dir / "psychometrics"
    manuscript_dir = figures_dir / "manuscript"
    print("[first wave] environment", flush=True)
    first_wave.build_environment_figure("vda16", environment_dir, seed=1701)
    attention_cache = data_dir / "attention_vda16_crossattn1.npz"
    print("[first wave] source-resolved attention", flush=True)
    first_wave.compute_attention_cache(
        "vda16",
        "crossattn1",
        attention_cache,
        trials=args.attention_trials,
        seed=1701,
        checkpoint_path=frozen_checkpoint,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
    )
    attention_meta = first_wave.validate_attention_cache(
        attention_cache,
        expected_task="vda16",
        expected_feedback="crossattn1",
        expected_trials=args.attention_trials,
        expected_seed=1701,
        expected_device=args.device,
        expected_checkpoint_path=frozen_checkpoint,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
    )
    attention_cache_sha256 = str(attention_meta["cache_sha256"])
    first_wave.build_attention_figure(
        attention_cache,
        attention_dir,
        expected_cache_sha256=attention_cache_sha256,
    )
    psychometric_cache = data_dir / "psychometric_vda16_crossattn1.npz"
    print("[first wave] focused psychometrics", flush=True)
    first_wave.compute_psychometric_cache(
        "vda16",
        "crossattn1",
        psychometric_cache,
        trials_per_point=args.psychometric_trials,
        seed=2801,
        checkpoint_path=frozen_checkpoint,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
    )
    psychometric_meta = first_wave.validate_psychometric_cache(
        psychometric_cache,
        expected_task="vda16",
        expected_feedback="crossattn1",
        expected_trials_per_point=args.psychometric_trials,
        expected_seed=2801,
        expected_device=args.device,
        expected_checkpoint_path=frozen_checkpoint,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
    )
    psychometric_cache_sha256 = str(psychometric_meta["cache_sha256"])
    first_wave.build_psychometric_figure(
        psychometric_cache,
        psychometric_dir,
        expected_cache_sha256=psychometric_cache_sha256,
    )

    metrics = integration.load_metrics(provenance_dir / "metrics.csv")
    print("[figures] training, behavior/RT, decoder, clamp, manuscript summaries", flush=True)
    integration.build_training_figure(metrics, figures_dir / "training" / "vda16_training")
    integration.build_behavior_timing_figure(
        shard_path, figures_dir / "behavior" / "vda16_behavior_timing"
    )
    integration.build_decoder_figure(
        shard_path, figures_dir / "decoder" / "vda16_decoder"
    )
    integration.build_clamp_figure(
        shard_path, figures_dir / "clamp" / "vda16_attention_clamp"
    )
    achieved_attention_cache = data_dir / "vda16_clamp_achieved_attention.npz"
    print("[clamp] achieved attention mass", flush=True)
    integration.compute_achieved_clamp_attention(
        frozen_checkpoint,
        achieved_attention_cache,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
        device=args.device,
        source_hashes=source_hashes,
    )
    achieved_attention_cache_sha256 = integration.sha256_file(achieved_attention_cache)
    integration.build_achieved_clamp_attention_figure(
        achieved_attention_cache,
        figures_dir / "clamp" / "vda16_clamp_achieved_attention",
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
        expected_cache_sha256=achieved_attention_cache_sha256,
        expected_device=args.device,
        expected_source_hashes=source_hashes,
    )
    integration.build_manuscript_summary_figure(
        shard_path,
        manuscript_dir / "vda16_manuscript_summary",
        competence_status=admission["training"]["status"],
    )
    integration.build_method_comparison_figure(
        shard_path,
        Path(str(historical["frozen_shard_root"])),
        manuscript_dir / "vda_method_comparison_with_vda16",
        vda16_competence_status=admission["training"]["status"],
        vda16_final_theta=admission["training"]["final_theta_degrees"],
    )

    summary = _summary_from_shard(shard_path, admission)
    summary_path = data_dir / "vda16_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    _write_summary_csv(data_dir / "vda16_summary.csv", summary)
    _write_manuscript_fragments(output_root, summary, admission)
    admission_path = provenance_dir / "CHECKPOINT_ADMISSION.json"
    admission_path.write_text(
        json.dumps(admission, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    historical_path = provenance_dir / "HISTORICAL_SHARD_AUDIT.json"
    historical_path.write_text(
        json.dumps(historical, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )

    if _hash_sources(integration) != source_hashes:
        raise RuntimeError("analysis source changed while the build was running")
    for name, path, frozen_path in (
        ("checkpoint", checkpoint, frozen_checkpoint),
        ("launch_manifest", launch_manifest, provenance_dir / "launch_manifest.json"),
        ("metrics", metrics_path, provenance_dir / "metrics.csv"),
        ("train_log", train_log, provenance_dir / "train.log"),
    ):
        expected_hash = original_input_hashes[name]
        for candidate in (path, frozen_path):
            if integration.sha256_file(candidate) != expected_hash:
                raise RuntimeError(f"{name} changed during analysis: {candidate}")
    if integration.sha256_file(shard_path) != shard_sha256:
        raise RuntimeError("matched-protocol shard changed after rendering")
    with np.load(shard_path, allow_pickle=False) as payload:
        matched.validate_shard_payload(payload, spec)
    first_wave.validate_attention_cache(
        attention_cache,
        expected_task="vda16",
        expected_feedback="crossattn1",
        expected_trials=args.attention_trials,
        expected_seed=1701,
        expected_device=args.device,
        expected_checkpoint_path=frozen_checkpoint,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
        expected_cache_sha256=attention_cache_sha256,
    )
    first_wave.validate_psychometric_cache(
        psychometric_cache,
        expected_task="vda16",
        expected_feedback="crossattn1",
        expected_trials_per_point=args.psychometric_trials,
        expected_seed=2801,
        expected_device=args.device,
        expected_checkpoint_path=frozen_checkpoint,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
        expected_cache_sha256=psychometric_cache_sha256,
    )
    integration.validate_achieved_clamp_attention(
        achieved_attention_cache,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
        expected_device=args.device,
        expected_cache_sha256=achieved_attention_cache_sha256,
        expected_source_hashes=source_hashes,
    )
    _revalidate_historical_evidence(historical, integration)

    validation_path = provenance_dir / "VALIDATION_RESULT.json"
    validation_temporary = provenance_dir / ".VALIDATION_RESULT.json.tmp"
    validation_temporary.write_text(
        json.dumps(
            {
                "result": "pass",
                "validated_at_utc": datetime.now(timezone.utc).isoformat(),
                "checkpoint_admission": "pass",
                "metrics_contiguous_0_through_19999": True,
                "matched_protocol_shard": "pass",
                "matched_protocol_shard_sha256": shard_sha256,
                "first_wave_attention_cache": "pass",
                "first_wave_attention_cache_sha256": attention_cache_sha256,
                "first_wave_psychometric_cache": "pass",
                "first_wave_psychometric_cache_sha256": psychometric_cache_sha256,
                "achieved_clamp_attention_cache": "pass",
                "achieved_clamp_attention_cache_sha256": achieved_attention_cache_sha256,
                "source_graph_unchanged": True,
                "training_inputs_unchanged": True,
                "historical_evidence_unchanged": True,
                "competence_status": admission["training"]["status"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    premanifest_files = regular_files(output_root)
    if validation_path in premanifest_files:
        raise RuntimeError("final validation sentinel exists before publication")
    artifact_records = []
    for path in sorted(premanifest_files):
        published_path = validation_path if path == validation_temporary else path
        artifact_records.append(
            {
                "path": str(published_path.relative_to(output_root)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": integration.sha256_file(path),
            }
        )
    manifest = {
        "schema_version": 1,
        "artifact_class": "VDA16 single-checkpoint manuscript evidence shard",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "task": "vda16",
            "feedback": "crossattn1",
            "width": 128,
            "memory_decay": 1.0,
            "seed": 0,
            "checkpoint_iteration": 19999,
        },
        "analysis_families": [
            "training competence",
            "first-wave environment schematic",
            "first-wave source-resolved attention",
            "first-wave psychometrics",
            "matched-bank psychometrics and response timing",
            "five-variable native and foldwise PCA-128 recurrent decoding",
            "graded attention-key clamp with response rates, d-prime, criterion, and timing",
            "achieved attention mass for every clamp dose and condition",
            "visually competence-gated descriptive historical routing-family comparison",
        ],
        "protocol": matched.protocol_for(spec),
        "checkpoint_admission": admission,
        "runtime": _runtime(args.device),
        "source_hashes": source_hashes,
        "source_snapshots": source_snapshots,
        "historical_evidence": historical,
        "competence_gate": admission["training"],
        "claim_boundary": admission["claim_boundary"],
        "validation_gate": {
            "result": "pass",
            "path": "provenance/VALIDATION_RESULT.json",
            "sha256": integration.sha256_file(validation_temporary),
        },
        "artifacts": artifact_records,
    }
    manifest_path = output_root / "MANIFEST.json"
    manifest_temporary = output_root / ".MANIFEST.json.tmp"
    manifest_temporary.write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )

    # Final prepublication gate over the exact temporary tree.
    require_exact_inventory(
        output_root,
        premanifest_files | {manifest_temporary},
    )
    if _hash_sources(integration) != source_hashes:
        raise RuntimeError("analysis source changed before manifest publication")
    for name, path, frozen_path in (
        ("checkpoint", checkpoint, frozen_checkpoint),
        ("launch_manifest", launch_manifest, provenance_dir / "launch_manifest.json"),
        ("metrics", metrics_path, provenance_dir / "metrics.csv"),
        ("train_log", train_log, provenance_dir / "train.log"),
    ):
        for candidate in (path, frozen_path):
            if integration.sha256_file(candidate) != original_input_hashes[name]:
                raise RuntimeError(f"{name} changed before manifest publication")
    if integration.sha256_file(shard_path) != shard_sha256:
        raise RuntimeError("matched-protocol shard changed before publication")
    if integration.sha256_file(attention_cache) != attention_cache_sha256:
        raise RuntimeError("attention cache changed before publication")
    if integration.sha256_file(psychometric_cache) != psychometric_cache_sha256:
        raise RuntimeError("psychometric cache changed before publication")
    if (
        integration.sha256_file(achieved_attention_cache)
        != achieved_attention_cache_sha256
    ):
        raise RuntimeError("achieved-attention cache changed before publication")
    _revalidate_historical_evidence(historical, integration)

    validation_temporary.replace(validation_path)
    transitional_files = (
        premanifest_files - {validation_temporary}
    ) | {validation_path, manifest_temporary}
    require_exact_inventory(output_root, transitional_files)
    manifest_temporary.replace(manifest_path)
    expected = {
        output_root / record["path"].replace("/", os.sep)
        for record in manifest["artifacts"]
    } | {manifest_path}
    try:
        require_exact_inventory(output_root, expected)
        for record in manifest["artifacts"]:
            path = output_root / record["path"].replace("/", os.sep)
            if (
                path.stat().st_size != int(record["bytes"])
                or integration.sha256_file(path) != str(record["sha256"])
            ):
                raise RuntimeError(f"published artifact identity mismatch: {path}")
        audit_completed_output(output_root)
    except BaseException:
        # Never leave a completed MANIFEST next to a failed final audit.
        manifest_path.unlink(missing_ok=True)
        raise
    print(f"[complete] {manifest_path}", flush=True)
    return manifest_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.audit:
        path = audit_completed_output(args.output_root)
        print(f"[validated] {path}", flush=True)
        return 0
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
