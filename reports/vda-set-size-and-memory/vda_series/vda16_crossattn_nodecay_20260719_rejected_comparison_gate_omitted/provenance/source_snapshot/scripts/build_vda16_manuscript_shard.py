#!/usr/bin/env python3
"""Build a provenance-closed VDA16 cross-attention manuscript evidence shard."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
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
        required=True,
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
    return parser.parse_args(argv)


def _hash_sources(integration: Any) -> dict[str, str]:
    records: dict[str, str] = {}
    for relative in SOURCE_DEPENDENCIES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        records[relative] = integration.sha256_file(path)
    return records


def _freeze_sources(
    source_hashes: dict[str, str], destination: Path, integration: Any
) -> list[dict[str, Any]]:
    records = []
    for relative, expected in source_hashes.items():
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
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
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("shards")
    if not isinstance(records, list) or len(records) != 12:
        raise ValueError("historical matched-width manifest does not contain 12 shards")
    selected = {
        f"{task}_{feedback}_d128.npz"
        for task in ("vda1", "vda4", "vda9")
        for feedback in ("affine_ew", "crossattn1")
    }
    verified = []
    for record in records:
        relative = Path(str(record["path"]))
        if relative.name not in selected:
            continue
        path = upstream_root / relative
        digest = integration.sha256_file(path)
        if path.stat().st_size != int(record["bytes"]) or digest != str(record["sha256"]):
            raise RuntimeError(f"historical matched-width shard identity mismatch: {path}")
        verified.append(
            {
                "path": str(path.resolve()),
                "sha256": digest,
                "bytes": path.stat().st_size,
            }
        )
    if {Path(record["path"]).name for record in verified} != selected:
        raise RuntimeError("historical d128 routing-family shard scope is incomplete")
    snapshot = provenance_dir / "HISTORICAL_MATCHED_WIDTH_MANIFEST.json"
    shutil.copy2(manifest_path, snapshot)
    return {
        "manifest_path": str(manifest_path.resolve()),
        "manifest_sha256": integration.sha256_file(manifest_path),
        "snapshot": str(snapshot.resolve()),
        "selected_shards": verified,
        "lineage_boundary": (
            "historical shards are hash-bound aggregate evidence; this build does not "
            "recompute their checkpoints"
        ),
    }


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
into an absent global source tree.

## Required caveats

This is a single seed and a single cross-attention/d128/no-decay checkpoint.
VDA16 affine, d256, decay contrasts, and seed-level uncertainty are unavailable.
The historical VDA1/VDA4/VDA9 comparison is descriptive because task geometry and
token count change together. The clamp dose is an additive logit bias, not achieved
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


def build(args: argparse.Namespace) -> Path:
    run_dir = args.run_dir.resolve()
    output_root = args.output_root.resolve()
    if output_root.exists() or output_root.is_symlink():
        raise FileExistsError(f"fresh output root required: {output_root}")
    if args.attention_trials != 96 or args.psychometric_trials != 300:
        raise ValueError("publication build requires attention n=96 and psychometric n=300")
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
    for source, name in (
        (launch_manifest, "launch_manifest.json"),
        (metrics_path, "metrics.csv"),
        (train_log, "train.log"),
    ):
        shutil.copy2(source, provenance_dir / name)
    admission["original_checkpoint_path"] = admission["checkpoint_path"]
    admission["checkpoint_path"] = str(frozen_checkpoint.resolve())
    admission["frozen_checkpoint_sha256"] = integration.sha256_file(frozen_checkpoint)

    source_hashes = _hash_sources(integration)
    source_snapshots = _freeze_sources(
        source_hashes, provenance_dir / "source_snapshot", integration
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
    first_wave.build_attention_figure(
        attention_cache,
        attention_dir,
        expected_cache_sha256=str(attention_meta["cache_sha256"]),
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
    first_wave.build_psychometric_figure(
        psychometric_cache,
        psychometric_dir,
        expected_cache_sha256=str(psychometric_meta["cache_sha256"]),
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
    )
    integration.build_achieved_clamp_attention_figure(
        achieved_attention_cache,
        figures_dir / "clamp" / "vda16_clamp_achieved_attention",
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
    )
    integration.build_manuscript_summary_figure(
        shard_path,
        manuscript_dir / "vda16_manuscript_summary",
        competence_status=admission["training"]["status"],
    )
    integration.build_method_comparison_figure(
        shard_path,
        HISTORICAL_MATCHED_WIDTH,
        manuscript_dir / "vda_method_comparison_with_vda16",
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
    if integration.sha256_file(checkpoint) != admission["checkpoint_sha256"]:
        raise RuntimeError("original final checkpoint changed during analysis")
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
    )
    integration.validate_achieved_clamp_attention(
        achieved_attention_cache,
        expected_checkpoint_sha256=admission["checkpoint_sha256"],
        expected_device=args.device,
    )

    validation_path = provenance_dir / "VALIDATION_RESULT.json"
    validation_path.write_text(
        json.dumps(
            {
                "result": "pass",
                "validated_at_utc": datetime.now(timezone.utc).isoformat(),
                "checkpoint_admission": "pass",
                "metrics_contiguous_0_through_19999": True,
                "matched_protocol_shard": "pass",
                "first_wave_attention_cache": "pass",
                "first_wave_psychometric_cache": "pass",
                "achieved_clamp_attention_cache": "pass",
                "source_graph_unchanged": True,
                "original_checkpoint_unchanged": True,
                "competence_status": admission["training"]["status"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    regular_files = sorted(path for path in output_root.rglob("*") if path.is_file())
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
            "descriptive historical routing-family comparison",
        ],
        "protocol": matched.protocol_for(spec),
        "checkpoint_admission": admission,
        "runtime": _runtime(args.device),
        "source_hashes": source_hashes,
        "source_snapshots": source_snapshots,
        "historical_evidence": historical,
        "competence_gate": admission["training"],
        "claim_boundary": admission["claim_boundary"],
        "artifacts": [
            integration.artifact_record(path, output_root) for path in regular_files
        ],
    }
    manifest_path = output_root / "MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    expected = {
        output_root / record["path"].replace("/", os.sep)
        for record in manifest["artifacts"]
    } | {manifest_path}
    actual = {path for path in output_root.rglob("*") if path.is_file()}
    if actual != expected:
        raise RuntimeError("published output inventory differs from the manifest")
    for record in manifest["artifacts"]:
        path = output_root / record["path"].replace("/", os.sep)
        if (
            path.stat().st_size != int(record["bytes"])
            or integration.sha256_file(path) != str(record["sha256"])
        ):
            raise RuntimeError(f"published artifact identity mismatch: {path}")
    print(f"[complete] {manifest_path}", flush=True)
    return manifest_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
