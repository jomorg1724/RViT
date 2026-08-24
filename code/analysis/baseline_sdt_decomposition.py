"""Systematic sensitivity/criterion (d'/c) decomposition for the *base* cueing effect.

Every clamp/rescue analysis in this paper already reports d' and criterion (they need a
false-alarm rate to compute either, and the clamp scripts always ran a paired no-change
condition). The plain psychometric curves in Section 3 never did -- they report response
probability only, so a reader cannot tell whether the cueing benefit reported there is a
sensitivity effect or a criterion effect (Luo and Maunsell's warning). This script closes
that gap for every checkpoint where a real .pt file is available in this environment: it
reuses the existing cached hit-count arrays from the psychometric NPZ producers (no new
inference for the change-trial arm) and adds one new no-change-trial batch per displayed
validity (the only thing genuinely missing), then combines them with the same
``matched_width._sdt_from_counts`` helper used everywhere else in this project.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vda_sweep import matched_width as MW
from vda_sweep import vda_core as core

TRIALS_PER_POINT = 300
NOCHANGE_SEED_BASE = 20270726
QUALIFYING_FRAMES = (5, 6)


@dataclass(frozen=True)
class CheckpointSpec:
    label: str
    env: str
    feedback: str
    cue_index: int
    psychometric_npz: Path
    checkpoint_path: Path
    checkpoint_sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


SPECS: list[CheckpointSpec] = [
    CheckpointSpec(
        label="VDA16 cross-attention",
        env="vda16",
        feedback="crossattn1",
        cue_index=0,
        psychometric_npz=ROOT
        / "reports/vda_series/vda16_crossattn_nodecay_20260719_production/data/psychometric_vda16_crossattn1.npz",
        checkpoint_path=ROOT
        / "reports/vda_series/vda16_crossattn_nodecay_20260719_production/provenance/checkpoints/rvit_paper_vda16_final.pt",
        checkpoint_sha256="b40d9aa49ec28c352d7a790de84f5902e1a307f7b2abe5fe68dc9e6aabb4f84d",
    ),
    CheckpointSpec(
        label="VDA16 affine",
        env="vda16",
        feedback="affine_ew",
        cue_index=0,
        psychometric_npz=ROOT
        / "reports/vda_series/vda16_affine_nodecay_20260720_production/data/psychometric_vda16_affine_ew.npz",
        checkpoint_path=ROOT
        / "reports/vda_series/vda16_affine_nodecay_20260720_production/provenance/checkpoints/rvit_paper_vda16_final.pt",
        checkpoint_sha256="52141da629e2c7f8f902826196067efbadb924608eecde7560559fdc0f813233",
    ),
]


def compute_for_spec(spec: CheckpointSpec, out_dir: Path) -> dict[str, Any]:
    if not spec.checkpoint_path.is_file():
        print(f"[{spec.label}] BLOCKED: checkpoint not found at {spec.checkpoint_path}")
        return {"label": spec.label, "status": "blocked", "expected_path": str(spec.checkpoint_path)}
    if not spec.psychometric_npz.is_file():
        print(f"[{spec.label}] BLOCKED: psychometric cache not found at {spec.psychometric_npz}")
        return {"label": spec.label, "status": "blocked", "expected_path": str(spec.psychometric_npz)}

    actual_sha = sha256_file(spec.checkpoint_path)
    if actual_sha != spec.checkpoint_sha256:
        raise RuntimeError(f"{spec.label}: checkpoint SHA-256 mismatch ({actual_sha} != {spec.checkpoint_sha256})")

    cache = np.load(spec.psychometric_npz, allow_pickle=True)
    validities = np.asarray(cache["displayed_validities"], dtype=float)
    magnitudes = np.asarray(cache["change_magnitudes"], dtype=float)
    count_valid = np.asarray(cache["response_count_valid"], dtype=int)  # (validity, magnitude)
    count_invalid = np.asarray(cache["response_count_invalid"], dtype=int)
    trials_per_point = int(cache["trials_per_point"])
    cache_sha = sha256_file(spec.psychometric_npz)

    print(f"[{spec.label}] loading checkpoint")
    model, iteration = core.load(spec.env, spec.feedback, 128, checkpoint_path=str(spec.checkpoint_path))
    print(f"[{spec.label}] loaded at iteration {iteration}; running {len(validities)} no-change batches")

    false_alarm_count = np.zeros(len(validities), dtype=int)
    for vi, validity in enumerate(validities):
        press = core.press_times_clamp(
            model, spec.env, spec.cue_index, float(validity), "red", 0, -1, 0.0,
            clamp=None, clamp_from=5, B=TRIALS_PER_POINT, seed=NOCHANGE_SEED_BASE + vi,
        )
        false_alarm_count[vi] = int((press >= 0).sum())
        print(f"[{spec.label}]   validity={validity:.2f}  false_alarm_count={false_alarm_count[vi]}/{TRIALS_PER_POINT}")

    dprime_valid = np.zeros_like(count_valid, dtype=float)
    criterion_valid = np.zeros_like(count_valid, dtype=float)
    dprime_invalid = np.zeros_like(count_invalid, dtype=float)
    criterion_invalid = np.zeros_like(count_invalid, dtype=float)
    for vi in range(len(validities)):
        for mi in range(len(magnitudes)):
            dprime_valid[vi, mi], criterion_valid[vi, mi] = MW._sdt_from_counts(
                np.asarray(count_valid[vi, mi]), np.asarray(false_alarm_count[vi]), trials_per_point
            )
            dprime_invalid[vi, mi], criterion_invalid[vi, mi] = MW._sdt_from_counts(
                np.asarray(count_invalid[vi, mi]), np.asarray(false_alarm_count[vi]), trials_per_point
            )

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / f"baseline_sdt_{spec.env}_{spec.feedback}"
    np.savez_compressed(
        stem.with_suffix(".npz"),
        validities=validities,
        magnitudes=magnitudes,
        false_alarm_count=false_alarm_count,
        dprime_valid=dprime_valid,
        criterion_valid=criterion_valid,
        dprime_invalid=dprime_invalid,
        criterion_invalid=criterion_invalid,
    )

    summary = {
        "label": spec.label,
        "status": "ok",
        "env": spec.env,
        "feedback": spec.feedback,
        "checkpoint_path": str(spec.checkpoint_path),
        "checkpoint_sha256": actual_sha,
        "checkpoint_iteration": iteration,
        "psychometric_cache_path": str(spec.psychometric_npz),
        "psychometric_cache_sha256": cache_sha,
        "trials_per_point": trials_per_point,
        "nochange_trials_per_validity": TRIALS_PER_POINT,
        "validities": validities.tolist(),
        "magnitudes": magnitudes.tolist(),
        "false_alarm_count": false_alarm_count.tolist(),
        "false_alarm_rate": (false_alarm_count / TRIALS_PER_POINT).tolist(),
        "dprime_valid": dprime_valid.tolist(),
        "criterion_valid": criterion_valid.tolist(),
        "dprime_invalid": dprime_invalid.tolist(),
        "criterion_invalid": criterion_invalid.tolist(),
        "cache_npz": str(stem.with_suffix(".npz").resolve()),
    }
    (out_dir / f"baseline_sdt_{spec.env}_{spec.feedback}.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[{spec.label}] wrote {stem.with_suffix('.npz')}")
    return summary


def render_figure(results: list[dict[str, Any]], out_dir: Path) -> None:
    ok = [r for r in results if r["status"] == "ok"]
    if not ok:
        return
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.titlesize": 12, "pdf.fonttype": 42})
    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), constrained_layout=True)
    colors = plt.cm.tab10.colors
    for i, r in enumerate(ok):
        validities = np.asarray(r["validities"])
        magnitudes = np.asarray(r["magnitudes"])
        focal_idx = int(np.argmin(np.abs(magnitudes - 18.0)))
        d_valid = np.asarray(r["dprime_valid"])[:, focal_idx]
        d_invalid = np.asarray(r["dprime_invalid"])[:, focal_idx]
        c_valid = np.asarray(r["criterion_valid"])[:, focal_idx]
        c_invalid = np.asarray(r["criterion_invalid"])[:, focal_idx]
        color = colors[i % len(colors)]
        axes[0].plot(validities, d_valid, color=color, marker="o", ms=5, lw=1.8, label=f"{r['label']} (valid)")
        axes[0].plot(validities, d_invalid, color=color, marker="s", ms=5, lw=1.4, ls="--", label=f"{r['label']} (invalid)")
        axes[1].plot(validities, c_valid, color=color, marker="o", ms=5, lw=1.8, label=f"{r['label']} (valid)")
        axes[1].plot(validities, c_invalid, color=color, marker="s", ms=5, lw=1.4, ls="--", label=f"{r['label']} (invalid)")
    axes[0].set(title="A  Sensitivity $d'$ near 18°", xlabel="displayed validity", ylabel="$d'$")
    axes[1].set(title="B  Criterion $c$ near 18°", xlabel="displayed validity", ylabel="$c$")
    for axis in axes:
        axis.grid(alpha=0.2)
    axes[0].legend(frameon=False, fontsize=7.5, loc="upper left")
    figure.suptitle(
        "Sensitivity/criterion decomposition of the base cueing effect (not the clamp)",
        fontsize=12, fontweight="bold",
    )
    stem = out_dir / "baseline_sdt_decomposition"
    figure.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    figure.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(figure)
    print(f"wrote {stem.with_suffix('.pdf')}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "reports/vda_series/baseline_sdt_decomposition_20260726")
    args = parser.parse_args()
    results = [compute_for_spec(spec, args.output_root) for spec in SPECS]
    render_figure(results, args.output_root)
    (args.output_root / "MANIFEST.json").write_text(
        json.dumps({"schema_version": 1, "results": results}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {args.output_root / 'MANIFEST.json'}")


if __name__ == "__main__":
    main()
