from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return math.nan, math.nan
    p = successes / total
    denom = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denom
    half = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total)) / denom
    return center - half, center + half


def load_two_conditions(csv_path: Path) -> dict[str, list[dict[str, float]]]:
    keep = {"natural", "tested_sample"}
    rows: dict[str, list[dict[str, float]]] = {key: [] for key in keep}
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            condition = raw["intervention"]
            if condition not in keep:
                continue
            rows[condition].append({
                "magnitude": float(raw["magnitude"]),
                "response_rate": float(raw["hit_rate"]),
            })
    for condition in keep:
        rows[condition].sort(key=lambda row: row["magnitude"])
        if not rows[condition]:
            raise ValueError(f"No rows found for {condition}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper-style two-condition response-rate plot.")
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--trials-per-magnitude", type=int, default=64)
    args = parser.parse_args()

    data = load_two_conditions(args.csv)
    normal = data["natural"]
    inhibited = data["tested_sample"]
    x = np.asarray([row["magnitude"] for row in normal], dtype=float)
    y_normal = np.asarray([row["response_rate"] for row in normal], dtype=float)
    y_inhibited = np.asarray([row["response_rate"] for row in inhibited], dtype=float)
    if not np.array_equal(x, np.asarray([row["magnitude"] for row in inhibited], dtype=float)):
        raise ValueError("Normal and inhibited magnitude grids differ")

    def asymmetric_errors(values: np.ndarray) -> np.ndarray:
        lower, upper = [], []
        for value in values:
            successes = int(round(value * args.trials_per_magnitude))
            lo, hi = wilson_interval(successes, args.trials_per_magnitude)
            lower.append(value - lo)
            upper.append(hi - value)
        return np.asarray([lower, upper])

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.linewidth": 0.9,
    })
    fig, ax = plt.subplots(figsize=(7.2, 5.0), constrained_layout=True)

    # One shared uncertainty envelope is sufficient because paired outcomes and
    # therefore Wilson intervals are identical at every tested magnitude.
    errors = asymmetric_errors(y_normal)
    ax.errorbar(
        x, y_normal, yerr=errors, fmt="none", ecolor="#777777",
        elinewidth=1.0, capsize=2.5, capthick=1.0, zorder=1,
    )

    # Morgan–Albanna–Herman Figure 5 grammar: normal in black, manipulation
    # in a saturated color, connected point estimates, no background grid.
    ax.plot(
        x, y_normal, color="black", linewidth=2.2, marker="o", markersize=5.5,
        markerfacecolor="white", markeredgecolor="black", markeredgewidth=1.3,
        label="Normal", zorder=3,
    )
    ax.plot(
        x, y_inhibited, color="#d62728", linewidth=2.2, linestyle=(0, (5, 3)),
        marker="x", markersize=7.0, markeredgewidth=1.7,
        label="Sample-location attention inhibited", zorder=4,
    )

    ax.set_title("Sample-phase attention inhibition")
    ax.set_xlabel(r"Orientation change magnitude $|\Delta|$ (degrees)")
    ax.set_ylabel("Response rate (declare change)")
    ax.set_xlim(-1.0, 36.0)
    ax.set_ylim(0.0, 1.04)
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30, 35])
    ax.set_yticks(np.linspace(0.0, 1.0, 6))
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_color("#8a8a8a")
        spine.set_linewidth(0.9)
    ax.tick_params(direction="out", length=4, width=0.9, color="#555555")
    ax.legend(loc="lower right", frameon=True, fancybox=False, framealpha=1.0,
              edgecolor="#b0b0b0", handlelength=3.0)

    max_difference = float(np.max(np.abs(y_normal - y_inhibited)))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    png = args.output_dir / "normal_vs_attention_inhibited_response_rate.png"
    pdf = args.output_dir / "normal_vs_attention_inhibited_response_rate.pdf"
    fig.savefig(png, dpi=300, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)

    metadata = {
        "reference_style": "Morgan, Albanna & Herman, Figure 5",
        "conditions": ["Normal", "Sample-location attention inhibited"],
        "series_count": 2,
        "trials_per_magnitude_per_condition": args.trials_per_magnitude,
        "magnitudes_degrees": x.tolist(),
        "normal_response_rate": y_normal.tolist(),
        "inhibited_response_rate": y_inhibited.tolist(),
        "maximum_absolute_curve_difference": max_difference,
        "uncertainty": "95% Wilson intervals; shared because paired outcomes are identical",
        "fit": "none; raw point estimates connected because the observed function is non-monotonic",
        "png": str(png.resolve()),
        "pdf": str(pdf.resolve()),
    }
    (args.output_dir / "normal_vs_attention_inhibited_response_rate.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
