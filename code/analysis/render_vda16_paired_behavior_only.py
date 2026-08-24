"""Render the valid behavior-only portion of the frozen VDA16 paired evaluation.

The legacy cache also contains a fused current-image-key plus previous-hidden-
state-key location total.  That statistic is deliberately not loaded here: it
cannot support source-separated attention maps or source-specific conclusions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


EXPECTED_CACHE_SHA256 = "d3359287ced22900b018dc136f15177d3f370c405152368e796121b4bc126c7e"
CONDITION_LABELS = (
    "valid: change at cued S1 (top-left)",
    "forced-invalid: change at S16 (bottom-right)",
)
CONDITION_COLORS = ("#0072B2", "#D55E00")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wilson_interval(successes: np.ndarray, trials: int) -> tuple[np.ndarray, np.ndarray]:
    z = 1.959963984540054
    proportion = successes / trials
    denominator = 1.0 + z * z / trials
    center = (proportion + z * z / (2.0 * trials)) / denominator
    half_width = (
        z
        * np.sqrt(proportion * (1.0 - proportion) / trials + z * z / (4.0 * trials * trials))
        / denominator
    )
    return center - half_width, center + half_width


def conditional_mean_sem(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    counts = np.sum(np.isfinite(values), axis=-1)
    means = np.nanmean(values, axis=-1)
    std = np.nanstd(values, axis=-1, ddof=1)
    sem = np.divide(std, np.sqrt(counts), out=np.full_like(std, np.nan), where=counts > 1)
    return means, sem


def render(cache_path: Path, output_stem: Path) -> dict[str, object]:
    cache_path = cache_path.resolve()
    output_stem = output_stem.resolve()
    cache_hash = sha256_file(cache_path)
    if cache_hash != EXPECTED_CACHE_SHA256:
        raise RuntimeError(f"unexpected cache SHA-256: {cache_hash}")

    # Load only behavioral arrays.  The fused attention arrays are intentionally excluded.
    with np.load(cache_path, allow_pickle=False) as payload:
        press = np.asarray(payload["press_times"], dtype=np.int64)
        magnitudes = np.asarray(payload["change_magnitudes"], dtype=np.float64)
        condition_names = np.asarray(payload["condition_names"]).astype(str)

    if press.shape != (2, 10, 300):
        raise RuntimeError(f"unexpected press_times shape: {press.shape}")
    if magnitudes.shape != (10,):
        raise RuntimeError(f"unexpected change_magnitudes shape: {magnitudes.shape}")
    if condition_names.tolist() != ["cued_top_left", "forced_bottom_right"]:
        raise RuntimeError(f"unexpected conditions: {condition_names.tolist()}")

    qualifying = press >= 5
    response_count = qualifying.sum(axis=-1)
    response_rate = response_count / press.shape[-1]
    response_frames = np.where(qualifying, press, np.nan)
    frame_mean, frame_sem = conditional_mean_sem(response_frames)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    figure, axes = plt.subplots(1, 2, figsize=(12.8, 4.45), constrained_layout=True)
    markers = ("o", "s")
    for condition in range(2):
        color = CONDITION_COLORS[condition]
        low, high = wilson_interval(response_count[condition], press.shape[-1])
        axes[0].plot(
            magnitudes,
            response_rate[condition],
            color=color,
            marker=markers[condition],
            ms=4,
            lw=2,
            label=CONDITION_LABELS[condition],
        )
        axes[0].fill_between(magnitudes, low, high, color=color, alpha=0.14)
        axes[1].plot(
            magnitudes,
            frame_mean[condition],
            color=color,
            marker=markers[condition],
            ms=4,
            lw=2,
            label=CONDITION_LABELS[condition],
        )
        axes[1].fill_between(
            magnitudes,
            frame_mean[condition] - 1.96 * frame_sem[condition],
            frame_mean[condition] + 1.96 * frame_sem[condition],
            color=color,
            alpha=0.14,
        )

    axes[0].set(
        title="A  Change-report probability",
        xlabel="orientation change (degrees)",
        ylabel="P(response at t5 or t6)",
        ylim=(-0.02, 1.02),
    )
    axes[1].set(
        title="B  Discrete response frame among qualifying responses",
        xlabel="orientation change (degrees)",
        ylabel="mean response frame | response at t5 or t6",
        ylim=(4.95, 6.05),
    )
    for axis in axes:
        axis.grid(alpha=0.2)
    axes[0].legend(frameon=False, fontsize=8, loc="best")
    axes[1].text(
        0.99,
        0.03,
        "frames are model timesteps, not human reaction time",
        transform=axes[1].transAxes,
        ha="right",
        va="bottom",
        fontsize=7.5,
        color="#4C566A",
    )
    figure.suptitle(
        "VDA16 crossattn1: held-out paired behavior only\n"
        "cue fixed at S1; physical change at cued S1 or forced-invalid S16; 300 CRN trials per point",
        fontweight="bold",
    )
    figure.text(
        0.5,
        -0.015,
        "Bands are 95% evaluation-trial intervals from one checkpoint; they are not training-seed uncertainty. "
        "No attention sources are summed or displayed.",
        ha="center",
        fontsize=8,
        color="#4C566A",
    )

    output_stem.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = output_stem.with_suffix(".pdf")
    png_path = output_stem.with_suffix(".png")
    figure.savefig(
        pdf_path,
        bbox_inches="tight",
        metadata={"Title": "VDA16 paired held-out behavior only", "CreationDate": None},
    )
    figure.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(figure)

    metadata = {
        "schema_version": 1,
        "artifact": "VDA16 paired held-out behavior only",
        "cache_path": str(cache_path),
        "cache_sha256": cache_hash,
        "renderer_path": str(Path(__file__).resolve()),
        "renderer_sha256": sha256_file(Path(__file__).resolve()),
        "conditions": condition_names.tolist(),
        "change_magnitudes_degrees": magnitudes.tolist(),
        "trials_per_point": int(press.shape[-1]),
        "qualifying_response_frames": [5, 6],
        "attention_data_used": False,
        "exclusion_reason": (
            "legacy cache retained only a fused current-image-key plus previous-hidden-state-key "
            "location total; source-separated branch maps require checkpoint reevaluation"
        ),
        "outputs": {
            "pdf": {"path": str(pdf_path), "sha256": sha256_file(pdf_path)},
            "png": {"path": str(png_path), "sha256": sha256_file(png_path)},
        },
        "runtime_versions": {"numpy": np.__version__, "matplotlib": matplotlib.__version__},
    }
    json_path = output_stem.with_suffix(".json")
    json_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--output-stem", required=True, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(json.dumps(render(args.cache, args.output_stem), indent=2))
