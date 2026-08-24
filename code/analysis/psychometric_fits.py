#!/usr/bin/env python3
"""Four-parameter logistic psychometric-function fits over cached behavioral data.

This is a light re-analysis layer: every input is an already-produced, already-QA'd
NPZ cache from the first-wave and VDA16 psychometric producers (checkpoint-recomputed,
Wilson-interval-eligible response-rate arrays). No checkpoint is loaded and no model
inference is performed here -- this script has no Torch dependency, matching the
project's separation between the compute layer (writes versioned data) and the plotting
layer (reads only cached data).

For each (environment, routing family) source file it fits, independently at every
displayed validity, a four-parameter logistic

    p(x) = gamma + (1 - gamma - lambda) / (1 + exp(-(x - alpha) / beta))

separately for the change-at-cued-location ("valid") and change-at-opposite-location
("invalid") conditions, where alpha is the fitted threshold (degrees), beta the slope
scale, gamma the lower asymptote (guess rate), and lambda the lapse rate. It then
renders:

  - one two-panel figure per (environment, routing family): the fitted psychometric
    function at displayed validity 0.75 (matching the headline numbers already quoted
    elsewhere in the manuscript), and fitted threshold versus displayed validity, both
    split by location condition;
  - one cross-environment summary figure of the valid-minus-invalid qualifying-response-
    probability gap at the change magnitude nearest 18 degrees, at displayed validity
    0.75, one point per (environment, routing family), following the manuscript's
    established convention of plotting VDA16 as an open, unconnected point rather than
    implying a fitted set-size trend across non-interchangeable lineages.

Every fitted parameter is written to a JSON and CSV summary alongside the figures, with
the source NPZ path and SHA-256 recorded per fit so every plotted curve traces to a
cached data field, per the project's own reproducibility standard.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import curve_fit

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]

SOURCES: list[dict[str, Any]] = [
    {
        "env": "vda4",
        "routing": "affine_ew",
        "active_items": 4,
        "path": ROOT / "reports/vda_series/first_wave/data/psychometric_vda4_affine_ew.npz",
    },
    {
        "env": "vda4",
        "routing": "crossattn1",
        "active_items": 4,
        "path": ROOT / "reports/vda_series/first_wave/data/psychometric_vda4_crossattn1.npz",
    },
    {
        "env": "vda4_grid4x4",
        "routing": "crossattn1",
        "active_items": 4,
        "path": ROOT / "reports/vda_series/first_wave/data/psychometric_vda4_grid4x4_crossattn1.npz",
    },
    {
        "env": "vda9",
        "routing": "affine_ew",
        "active_items": 9,
        "path": ROOT
        / "RViT_plus_paper_jepa_grid9/reports/vda_series/first_wave_20260711_production/data/psychometric_vda9_affine_ew.npz",
    },
    {
        "env": "vda9",
        "routing": "crossattn1",
        "active_items": 9,
        "path": ROOT
        / "RViT_plus_paper_jepa_grid9/reports/vda_series/first_wave_20260711_production/data/psychometric_vda9_crossattn1.npz",
    },
    {
        "env": "vda16",
        "routing": "crossattn1",
        "active_items": 16,
        "path": ROOT
        / "RViT_plus_paper_jepa_grid9/reports/vda_series/vda16_crossattn_nodecay_20260719_production/data/psychometric_vda16_crossattn1.npz",
    },
    {
        "env": "vda16",
        "routing": "affine_ew",
        "active_items": 16,
        "path": ROOT
        / "RViT_plus_paper_jepa_grid9/reports/vda_series/vda16_affine_nodecay_20260720_production/data/psychometric_vda16_affine_ew.npz",
    },
]

FOCAL_VALIDITY = 0.75
FOCAL_MAGNITUDE = 18.0
CONDITION_LABELS = {"valid": "change at cued location", "invalid": "change at opposite location"}
CONDITION_COLORS = {"valid": "#0072B2", "invalid": "#D55E00"}
ROUTING_STYLE = {"affine_ew": "-", "crossattn1": "--"}
ENV_MARKER = {"vda4": "o", "vda4_grid4x4": "^", "vda9": "s", "vda16": "D"}
OUT_DIR = ROOT / "reports/vda_series/figures/psychometric_fits"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def logistic(x: np.ndarray, alpha: float, beta: float, gamma: float, lam: float) -> np.ndarray:
    return gamma + (1.0 - gamma - lam) / (1.0 + np.exp(-(x - alpha) / beta))


@dataclass
class FitResult:
    env: str
    routing: str
    condition: str
    displayed_validity: float
    alpha: float
    beta: float
    gamma: float
    lam: float
    converged: bool
    n_trials_per_point: int


def wilson_interval(count: np.ndarray, n: int, z: float = 1.96) -> tuple[np.ndarray, np.ndarray]:
    count = np.asarray(count, dtype=np.float64)
    p = count / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return center - half, center + half


def fit_logistic(x: np.ndarray, y: np.ndarray, n: int) -> tuple[np.ndarray, bool]:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    y_clipped = np.clip(y, 1.0 / (2 * n), 1.0 - 1.0 / (2 * n))
    sigma = np.sqrt(y_clipped * (1 - y_clipped) / n)
    alpha0 = float(np.clip(x[np.argmin(np.abs(y - 0.5))], x.min(), x.max()))
    beta0 = max((x.max() - x.min()) / 6.0, 1e-3)
    gamma0 = float(np.clip(y.min(), 0.0, 0.45))
    lam0 = float(np.clip(1.0 - y.max(), 0.0, 0.45))
    bounds = (
        [x.min() - 5.0, 1e-2, 0.0, 0.0],
        [x.max() + 5.0, (x.max() - x.min()) * 3.0 + 1.0, 0.5, 0.5],
    )
    try:
        params, _ = curve_fit(
            logistic,
            x,
            y,
            p0=[alpha0, beta0, gamma0, lam0],
            sigma=sigma,
            absolute_sigma=False,
            bounds=bounds,
            maxfev=20000,
        )
        return params, True
    except (RuntimeError, ValueError):
        return np.array([np.nan, np.nan, gamma0, lam0]), False


def load_source(spec: dict[str, Any]) -> dict[str, Any]:
    path: Path = spec["path"]
    if not path.exists():
        raise FileNotFoundError(f"missing cached source for {spec['env']}/{spec['routing']}: {path}")
    payload = np.load(path, allow_pickle=False)
    return {
        "magnitudes": np.asarray(payload["change_magnitudes"], dtype=np.float64),
        "validities": np.asarray(payload["displayed_validities"], dtype=np.float64),
        "rate_valid": np.asarray(payload["response_rate_valid"], dtype=np.float64),
        "rate_invalid": np.asarray(payload["response_rate_invalid"], dtype=np.float64),
        "count_valid": np.asarray(payload["response_count_valid"], dtype=np.int64),
        "count_invalid": np.asarray(payload["response_count_invalid"], dtype=np.int64),
        "trials_per_point": int(payload["trials_per_point"]),
        "checkpoint_sha256": str(payload["checkpoint_sha256"]),
        "sha256": sha256_file(path),
        "path": str(path.relative_to(ROOT)),
    }


def fit_all(spec: dict[str, Any], data: dict[str, Any]) -> list[FitResult]:
    results: list[FitResult] = []
    n = data["trials_per_point"]
    for vidx, validity in enumerate(data["validities"]):
        for condition, rates in (("valid", data["rate_valid"]), ("invalid", data["rate_invalid"])):
            params, converged = fit_logistic(data["magnitudes"], rates[vidx], n)
            alpha, beta, gamma, lam = (float(v) for v in params)
            results.append(
                FitResult(
                    env=spec["env"],
                    routing=spec["routing"],
                    condition=condition,
                    displayed_validity=float(validity),
                    alpha=alpha,
                    beta=beta,
                    gamma=gamma,
                    lam=lam,
                    converged=converged,
                    n_trials_per_point=n,
                )
            )
    return results


def nearest_index(values: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(values - target)))


def save_figure(figure: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(stem.with_suffix(".pdf"), bbox_inches="tight")
    figure.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(figure)


def render_environment_figure(
    spec: dict[str, Any], data: dict[str, Any], results: list[FitResult], out_dir: Path
) -> Path:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 12,
            "axes.titlesize": 13,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    figure, axes = plt.subplots(1, 2, figsize=(9.6, 4.0), constrained_layout=True)
    focal_v = nearest_index(data["validities"], FOCAL_VALIDITY)
    magnitudes = data["magnitudes"]
    x_smooth = np.linspace(magnitudes.min(), magnitudes.max(), 200)

    for condition, rates, counts in (
        ("valid", data["rate_valid"], data["count_valid"]),
        ("invalid", data["rate_invalid"], data["count_invalid"]),
    ):
        color = CONDITION_COLORS[condition]
        y = rates[focal_v]
        lo, hi = wilson_interval(counts[focal_v], data["trials_per_point"])
        axes[0].errorbar(
            magnitudes,
            y,
            yerr=[y - lo, hi - y],
            fmt="o",
            color=color,
            ms=4,
            lw=0,
            elinewidth=1.1,
            capsize=2,
        )
        fit = next(
            r
            for r in results
            if r.condition == condition and np.isclose(r.displayed_validity, data["validities"][focal_v])
        )
        if fit.converged:
            axes[0].plot(
                x_smooth,
                logistic(x_smooth, fit.alpha, fit.beta, fit.gamma, fit.lam),
                color=color,
                lw=1.8,
                label=f"{CONDITION_LABELS[condition]} ({fit.alpha:.1f}\N{DEGREE SIGN})",
            )
            axes[0].axvline(fit.alpha, color=color, lw=0.8, ls=":", alpha=0.6)

    axes[0].set(
        title=f"A  Psychometric function at displayed validity {data['validities'][focal_v]:g}",
        xlabel="orientation change (degrees)",
        ylabel="qualifying change-response probability",
        ylim=(-0.02, 1.02),
    )
    axes[0].legend(frameon=False, fontsize=9.5, loc="upper left")
    axes[0].grid(alpha=0.2)

    for condition in ("valid", "invalid"):
        color = CONDITION_COLORS[condition]
        alphas = [
            r.alpha if r.converged else np.nan
            for r in sorted(
                (r for r in results if r.condition == condition), key=lambda r: r.displayed_validity
            )
        ]
        validities_sorted = sorted(data["validities"])
        axes[1].plot(
            validities_sorted,
            alphas,
            color=color,
            marker="o",
            ms=4,
            lw=1.8,
            label=CONDITION_LABELS[condition],
        )
    axes[1].set(
        title="B  Fitted threshold vs. displayed cue validity",
        xlabel="displayed validity",
        ylabel="fitted threshold (degrees)",
    )
    axes[1].legend(frameon=False, fontsize=9.5)
    axes[1].grid(alpha=0.2)

    figure.suptitle(
        f"{spec['env'].upper()} · {spec['routing']} · {spec['active_items']} active items",
        fontsize=13,
        fontweight="bold",
    )
    figure.text(
        0.5,
        -0.03,
        f"{data['trials_per_point']} eval. trials/point, one frozen checkpoint (SHA-256 {data['sha256'][:10]}...); "
        "bands/curves show finite-trial fit uncertainty, not training-seed uncertainty.",
        ha="center",
        fontsize=8.5,
        color="#4C566A",
    )
    stem = out_dir / f"psychometric_fit_{spec['env']}_{spec['routing']}"
    save_figure(figure, stem)
    return stem.with_suffix(".pdf")


def render_summary_figure(all_results: dict[str, list[FitResult]], sources: dict[str, dict[str, Any]], out_dir: Path) -> Path:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    figure, axis = plt.subplots(1, 1, figsize=(5.6, 4.4), constrained_layout=True)
    routing_seen = set()
    for key, spec in sources.items():
        data = spec["data"]
        results = all_results[key]
        focal_v = nearest_index(data["validities"], FOCAL_VALIDITY)
        focal_m = nearest_index(data["magnitudes"], FOCAL_MAGNITUDE)
        gap = float(
            data["rate_valid"][focal_v, focal_m] - data["rate_invalid"][focal_v, focal_m]
        )
        marker = ENV_MARKER[spec["env"]]
        hollow = spec["env"] in ("vda16", "vda4_grid4x4")
        axis.scatter(
            [spec["active_items"]],
            [gap],
            marker=marker,
            s=70,
            facecolors="none" if hollow else ("#0072B2" if spec["routing"] == "crossattn1" else "#009E73"),
            edgecolors="#0072B2" if spec["routing"] == "crossattn1" else "#009E73",
            linewidths=1.8,
            label=(
                spec["routing"] if spec["routing"] not in routing_seen else None
            ),
        )
        routing_seen.add(spec["routing"])
        label_offset = (6, -16) if spec["env"] == "vda4_grid4x4" else (6, 6)
        axis.annotate(
            "VDA4 4x4-grid" if spec["env"] == "vda4_grid4x4" else spec["env"].upper(),
            (spec["active_items"], gap),
            textcoords="offset points",
            xytext=label_offset,
            fontsize=7.5,
        )

    for routing, color in (("affine_ew", "#009E73"), ("crossattn1", "#0072B2")):
        pts = sorted(
            (
                (spec["active_items"], data["rate_valid"][nearest_index(data["validities"], FOCAL_VALIDITY), nearest_index(data["magnitudes"], FOCAL_MAGNITUDE)]
                 - data["rate_invalid"][nearest_index(data["validities"], FOCAL_VALIDITY), nearest_index(data["magnitudes"], FOCAL_MAGNITUDE)])
                for spec in sources.values() for data in [spec["data"]]
                if spec["routing"] == routing and spec["env"] not in ("vda16", "vda4_grid4x4")
            )
        )
        if len(pts) >= 2:
            xs, ys = zip(*pts)
            axis.plot(xs, ys, color=color, lw=1.0, ls="-", zorder=0, alpha=0.7)

    axis.set(
        title=(
            "Valid-minus-invalid response-probability gap\n"
            f"near {FOCAL_MAGNITUDE:g}\N{DEGREE SIGN} change, displayed validity {FOCAL_VALIDITY:g}"
        ),
        xlabel="active items (set size)",
        ylabel="P(qualifying response | valid) - P(qualifying response | invalid)",
        xticks=[4, 9, 16],
        ylim=(-0.05, 1.0),
    )
    axis.grid(alpha=0.2)
    axis.legend(frameon=False, fontsize=8, loc="upper left")
    figure.text(
        0.5,
        -0.07,
        "Filled markers connected within a lineage are historical VDA4/VDA9.\n"
        "The open VDA16 diamond is a competence-gated, unconnected single checkpoint,\n"
        "not a fitted set-size trend.",
        ha="center",
        va="top",
        fontsize=7.2,
        color="#4C566A",
    )
    stem = out_dir / "psychometric_fit_setsize_summary"
    save_figure(figure, stem)
    return stem.with_suffix(".pdf")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    all_results: dict[str, list[FitResult]] = {}
    sources: dict[str, dict[str, Any]] = {}
    for spec in SOURCES:
        key = f"{spec['env']}_{spec['routing']}"
        data = load_source(spec)
        results = fit_all(spec, data)
        all_results[key] = results
        sources[key] = {**spec, "data": data}
        render_environment_figure(spec, data, results, args.out_dir)
        print(f"fitted {key}: {sum(r.converged for r in results)}/{len(results)} logistic fits converged")

    render_summary_figure(all_results, sources, args.out_dir)

    records = []
    for key, results in all_results.items():
        spec = sources[key]
        for r in results:
            row = asdict(r)
            row["active_items"] = spec["active_items"]
            row["source_path"] = spec["data"]["path"]
            row["source_sha256"] = spec["data"]["sha256"]
            row["checkpoint_sha256"] = spec["data"]["checkpoint_sha256"]
            records.append(row)

    json_path = args.out_dir / "psychometric_fits_summary.json"
    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    csv_path = args.out_dir / "psychometric_fits_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print(f"wrote {len(records)} fit records to {json_path} and {csv_path}")
    print(f"figures written under {args.out_dir}")


if __name__ == "__main__":
    main()
