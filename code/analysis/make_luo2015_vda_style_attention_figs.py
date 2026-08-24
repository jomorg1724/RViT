#!/usr/bin/env python3
"""Render the archived Luo/Maunsell attention arrays in the VDA common-quadrant style.

This is a pure re-plotting producer. It reruns no checkpoint and retrains nothing; it
reads the frozen ``fixed_condition_attention.npz`` cache from the 2026-08-03 scientific
assay and projects it onto the same physical 2x2 partition used for the VDA series
figures, resolved by frame (time) and by environment condition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.luo2015_attention_allocation import quadrant_indices  # noqa: E402

FRAME_LABELS = (
    ("t0", "sample 1"),
    ("t1", "sample 2"),
    ("t2", "delay"),
    ("t3", "test 1 onset"),
    ("t4", "test 1 repeat"),
    ("t5", "gap"),
    ("t6", "test 2"),
)
# Frames the policy can still be running in. Changed trials terminate at the end of the
# first-test window (hit, false-alarm-free declaration, or miss), so t5-t6 are open-loop
# continuations that no changed trial ever experiences under its own policy.
EXPERIENCED = {
    "changed": (0, 1, 2, 3, 4),
    "unchanged": (0, 1, 2, 3, 4, 5, 6),
}
GRID = 20
UNIFORM_QUADRANT = 0.25


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_conditions(npz_path: Path) -> list[dict]:
    data = np.load(npz_path, allow_pickle=True)
    conditions = []
    index = 0
    while f"condition_{index}_name" in data.files:
        raw_name = str(data[f"condition_{index}_name"])
        source_mass = np.asarray(data[f"condition_{index}_source_mass"], dtype=np.float64)
        routing = np.asarray(data[f"condition_{index}_routing"], dtype=np.float64)
        if source_mass.shape[1:] != (7, 2, GRID * GRID):
            raise ValueError(f"unexpected source mass shape {source_mass.shape}")
        if routing.shape[1:] != (7, 4, 2, 4):
            raise ValueError(f"unexpected routing shape {routing.shape}")
        if not np.allclose(source_mass.sum(axis=(2, 3)), 1.0, atol=1e-5):
            raise ValueError("source mass rows are not normalized")
        status = "changed" if raw_name.startswith("changed") else "unchanged"
        tested = 0 if "test L0" in raw_name else 3
        conditions.append(
            {
                "raw_name": raw_name,
                "status": status,
                "tested": tested,
                "other": 3 - tested,
                "label": f"{status}\ntest L{tested}",
                "source_mass": source_mass,
                "routing": routing,
                "outcomes": np.asarray(data[f"condition_{index}_outcomes"]),
                "correct": np.asarray(data[f"condition_{index}_correct"], dtype=bool),
                "press": np.asarray(data[f"condition_{index}_press"], dtype=np.int64),
            }
        )
        index += 1
    if len(conditions) != 4:
        raise ValueError(f"expected four environment conditions, found {len(conditions)}")
    return conditions


def quadrant_scores(source_mass: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (source share, source-conditional quadrant totals).

    Shares have shape (trials, 7, 2); quadrant totals have shape (trials, 7, 2, 4) and
    sum to one within each source block, so the uniform baseline is 0.25 per quadrant.
    """
    regions = quadrant_indices(GRID, GRID)
    totals = np.stack([source_mass[..., list(region)].sum(axis=-1) for region in regions], axis=-1)
    share = source_mass.sum(axis=-1)
    conditional = totals / np.maximum(share[..., None], 1e-12)
    return share, conditional


def draw_map_panel(ax, values, tested, other, plt, Rectangle, vmax):
    grid = np.asarray(values, dtype=np.float64).reshape(2, 2)
    image = ax.imshow(grid, cmap="viridis", vmin=0.0, vmax=vmax, interpolation="nearest")
    for quadrant in range(4):
        row, col = divmod(quadrant, 2)
        value = grid[row, col]
        ax.text(
            col,
            row,
            f"{value:.2f}",
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="white" if value < 0.55 * vmax else "black",
        )
    for quadrant, edge, style, width in (
        (tested, "#E8590C", "solid", 2.4),
        (other, "white", "dashed", 1.8),
    ):
        row, col = divmod(quadrant, 2)
        ax.add_patch(
            Rectangle(
                (col - 0.5, row - 0.5),
                1.0,
                1.0,
                fill=False,
                edgecolor=edge,
                linestyle=style,
                linewidth=width,
            )
        )
    ax.set_xticks([])
    ax.set_yticks([])
    return image


def plot_source_maps(conditions, source_index, source_name, output, vmax):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    fig, axes = plt.subplots(len(conditions), 7, figsize=(13.6, 8.4), constrained_layout=True)
    image = None
    for r, condition in enumerate(conditions):
        share, conditional = quadrant_scores(condition["source_mass"])
        experienced = EXPERIENCED[condition["status"]]
        for frame in range(7):
            ax = axes[r, frame]
            if frame not in experienced:
                ax.set_facecolor("#E6E6E6")
                ax.text(
                    0.5,
                    0.5,
                    "not experienced\n(post-decision)",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="#555555",
                    transform=ax.transAxes,
                )
                ax.set_xticks([])
                ax.set_yticks([])
            else:
                image = draw_map_panel(
                    ax,
                    conditional[:, frame, source_index, :].mean(axis=0),
                    condition["tested"],
                    condition["other"],
                    plt,
                    Rectangle,
                    vmax,
                )
                ax.set_xlabel(
                    f"$w$={share[:, frame, source_index].mean():.2f}",
                    fontsize=7,
                    labelpad=1.5,
                )
            if r == 0:
                tag, name = FRAME_LABELS[frame]
                ax.set_title(f"{tag}\n{name}", fontsize=9, fontweight="bold")
            if frame == 0:
                ax.set_ylabel(condition["label"], fontsize=9, fontweight="bold")
    colorbar = fig.colorbar(image, ax=axes.ravel().tolist(), shrink=0.55, pad=0.01)
    colorbar.set_label("quadrant mass conditional on source", fontsize=9)
    colorbar.ax.axhline(UNIFORM_QUADRANT, color="white", linewidth=1.4)
    fig.suptitle(
        f"Attention over time by environment condition: {source_name}",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.01,
        -0.012,
        "Common physical 2x2 partition of the 20x20 key grid. Orange solid outline = tested location; "
        "dashed white outline = the other sample location. Each panel sums to one within its key source; "
        "the white colorbar tick marks the 0.25 uniform-quadrant baseline. $w$ = that source's share of the "
        "joint softmax at that frame. Values are means over 64 noise repetitions of one fixed latent condition.",
        fontsize=7.4,
        ha="left",
    )
    fig.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_timecourses(conditions, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x = np.arange(7)
    ticks = [f"{tag}: {name}" for tag, name in FRAME_LABELS]
    fig, axes = plt.subplots(3, len(conditions), figsize=(14.0, 9.0), constrained_layout=True, sharex=True)
    for c, condition in enumerate(conditions):
        share, conditional = quadrant_scores(condition["source_mass"])
        combined = (conditional * share[..., None]).sum(axis=2)  # trials x 7 x 4, sums to 1
        experienced = np.asarray(EXPERIENCED[condition["status"]])
        tested, other = condition["tested"], condition["other"]
        blank = [q for q in range(4) if q not in (tested, other)]

        ax = axes[0, c]
        for values, label, color in (
            (combined[:, :, tested], "tested location", "#0072B2"),
            (combined[:, :, other], "other sample location", "#D55E00"),
            (combined[:, :, blank].mean(axis=-1), "mean blank quadrant", "#777777"),
        ):
            mean = values.mean(axis=0)
            sem = values.std(axis=0, ddof=1) / np.sqrt(values.shape[0])
            ax.plot(x[experienced], mean[experienced], marker="o", color=color, label=label)
            ax.fill_between(
                x[experienced],
                (mean - 1.96 * sem)[experienced],
                (mean + 1.96 * sem)[experienced],
                color=color,
                alpha=0.15,
            )
        ax.axhline(UNIFORM_QUADRANT, color="black", linestyle=":", linewidth=0.8)
        ax.set_title(condition["label"].replace("\n", ", "), fontsize=10, fontweight="bold")
        if c == 0:
            ax.set_ylabel("total incoming quadrant mass\n(visual + memory keys)", fontsize=9)
            ax.legend(frameon=False, fontsize=7.5)
        ax.grid(alpha=0.2)

        ax = axes[1, c]
        for source_index, label, color in ((0, "visual keys", "#56B4E9"), (1, "memory keys", "#E69F00")):
            values = share[:, :, source_index]
            mean = values.mean(axis=0)
            sem = values.std(axis=0, ddof=1) / np.sqrt(values.shape[0])
            ax.plot(x[experienced], mean[experienced], marker="s", color=color, label=label)
            ax.fill_between(
                x[experienced],
                (mean - 1.96 * sem)[experienced],
                (mean + 1.96 * sem)[experienced],
                color=color,
                alpha=0.15,
            )
        ax.axhline(0.5, color="black", linestyle=":", linewidth=0.8)
        ax.set_ylim(-0.02, 1.02)
        if c == 0:
            ax.set_ylabel("key-source share $w_s$", fontsize=9)
            ax.legend(frameon=False, fontsize=7.5)
        ax.grid(alpha=0.2)

        ax = axes[2, c]
        routing = condition["routing"]
        for source_index, label, color in ((0, "visual keys", "#009E73"), (1, "memory keys", "#CC79A7")):
            values = (
                routing[:, :, tested, source_index, tested]
                - routing[:, :, tested, source_index, other]
            )
            mean = values.mean(axis=0)
            sem = values.std(axis=0, ddof=1) / np.sqrt(values.shape[0])
            ax.plot(x[experienced], mean[experienced], marker="^", color=color, label=label)
            ax.fill_between(
                x[experienced],
                (mean - 1.96 * sem)[experienced],
                (mean + 1.96 * sem)[experienced],
                color=color,
                alpha=0.15,
            )
        ax.axhline(0.0, color="black", linestyle=":", linewidth=0.8)
        ax.set_xticks(x, ticks, fontsize=7, rotation=45, ha="right")
        if c == 0:
            ax.set_ylabel("tested-query routing\n(same $-$ other location)", fontsize=9)
            ax.legend(frameon=False, fontsize=7.5)
        ax.grid(alpha=0.2)

    fig.suptitle(
        "Phase-resolved attention allocation across the four environment conditions",
        fontsize=13,
        fontweight="bold",
    )
    fig.text(
        0.01,
        -0.02,
        "Bands are 1.96 SEM over 64 noise repetitions of one fixed latent condition. Dotted lines mark the "
        "uniform baselines (0.25 quadrant mass, 0.5 source share, 0 routing difference). Changed conditions "
        "stop at t4 because the episode terminates in the first-test window.",
        fontsize=7.4,
        ha="left",
    )
    fig.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_behavior(psychometric_csv: Path, output):
    import csv

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = []
    with psychometric_csv.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["intervention"] != "natural":
                continue
            rows.append(row)
    magnitude = np.asarray([float(row["magnitude"]) for row in rows])
    order = np.argsort(magnitude)
    magnitude = magnitude[order]
    hit = np.asarray([float(row["hit_rate"]) for row in rows])[order]
    dprime = np.asarray([float(row["dprime"]) for row in rows])[order]
    criterion = np.asarray([float(row["criterion"]) for row in rows])[order]
    frame = np.asarray([float(row["mean_hit_frame"]) for row in rows])[order]

    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.4), constrained_layout=True)
    axes[0].plot(magnitude, hit, marker="o", color="#0072B2")
    axes[0].set_ylabel("hit rate")
    axes[0].set_title("Psychometric", fontsize=10, fontweight="bold")
    axes[1].plot(magnitude, dprime, marker="o", color="#009E73", label="$d'$")
    axes[1].plot(magnitude, criterion, marker="s", color="#CC79A7", label="criterion $c$")
    axes[1].set_title("Signal detection", fontsize=10, fontweight="bold")
    axes[1].legend(frameon=False, fontsize=8)
    axes[2].plot(magnitude, frame, marker="o", color="#D55E00")
    axes[2].set_ylabel("mean hit frame")
    axes[2].set_title("Chronometric", fontsize=10, fontweight="bold")
    for ax in axes:
        ax.set_xlabel("first-test orientation change (deg)")
        ax.grid(alpha=0.2)
    fig.suptitle(
        "Behaviour of the frozen checkpoint on controlled fixed-magnitude slices",
        fontsize=12,
        fontweight="bold",
    )
    fig.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def condition_statistics(conditions) -> dict:
    stats = {}
    for condition in conditions:
        share, conditional = quadrant_scores(condition["source_mass"])
        combined = (conditional * share[..., None]).sum(axis=2)
        tested, other = condition["tested"], condition["other"]
        blank = [q for q in range(4) if q not in (tested, other)]
        routing = condition["routing"]
        entry = {
            "n_trials": int(condition["source_mass"].shape[0]),
            "accuracy": float(condition["correct"].mean()),
            "outcomes": {
                str(name): int(count)
                for name, count in zip(*np.unique(condition["outcomes"], return_counts=True))
            },
            "experienced_frames": list(EXPERIENCED[condition["status"]]),
            "per_frame": {},
        }
        for frame in EXPERIENCED[condition["status"]]:
            entry["per_frame"][f"t{frame}"] = {
                "visual_share": float(share[:, frame, 0].mean()),
                "memory_share": float(share[:, frame, 1].mean()),
                "combined_tested": float(combined[:, frame, tested].mean()),
                "combined_other": float(combined[:, frame, other].mean()),
                "combined_blank_mean": float(combined[:, frame, blank].mean()),
                "visual_conditional_tested": float(conditional[:, frame, 0, tested].mean()),
                "memory_conditional_tested": float(conditional[:, frame, 1, tested].mean()),
                "visual_conditional_other": float(conditional[:, frame, 0, other].mean()),
                "memory_conditional_other": float(conditional[:, frame, 1, other].mean()),
                "tested_query_visual_same_minus_other": float(
                    (routing[:, frame, tested, 0, tested] - routing[:, frame, tested, 0, other]).mean()
                ),
                "tested_query_memory_same_minus_other": float(
                    (routing[:, frame, tested, 1, tested] - routing[:, frame, tested, 1, other]).mean()
                ),
            }
        stats[condition["raw_name"]] = entry
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--assay-root",
        type=Path,
        default=ROOT / "reports" / "luo2015_scientific_assay_20260803_production",
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--vmax", type=float, default=1.0)
    args = parser.parse_args()

    npz_path = args.assay_root / "data" / "fixed_condition_attention.npz"
    psychometric_csv = args.assay_root / "data" / "psychometric_chronometric.csv"
    for path in (npz_path, psychometric_csv):
        if not path.is_file():
            raise FileNotFoundError(path)

    figures = args.output_root / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    conditions = load_conditions(npz_path)

    plot_source_maps(conditions, 0, "visual keys", figures / "attention_time_condition_visual", args.vmax)
    plot_source_maps(conditions, 1, "recurrent-memory keys", figures / "attention_time_condition_memory", args.vmax)
    plot_timecourses(conditions, figures / "attention_timecourse_conditions")
    plot_behavior(psychometric_csv, figures / "behaviour_curves")

    stats = {
        "schema_version": 1,
        "source_npz": str(npz_path.resolve()),
        "source_npz_sha256": sha256_file(npz_path),
        "grid": [GRID, GRID],
        "uniform_quadrant_baseline": UNIFORM_QUADRANT,
        "conditions": condition_statistics(conditions),
    }
    (args.output_root / "figure_statistics.json").write_text(
        json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"[complete] {args.output_root.resolve()}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
