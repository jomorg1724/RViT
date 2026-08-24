"""Plot eight-curve valid/invalid overlays for both terminal VDA16 models."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
SOURCES = {
    "Affine element-wise": REPO_ROOT
    / "reports/vda_series/vda16_affine_nodecay_20260720_production/data/"
    / "vda16_affine_ew_d128_nodecay_seed0.npz",
    "Cross-attention": REPO_ROOT
    / "reports/vda_series/vda16_crossattn_nodecay_20260719_production/data/"
    / "vda16_crossattn1_d128_nodecay_seed0.npz",
}
OUTPUT_STEM = (
    WORKSPACE_ROOT
    / "reports/vda_series/figures/vda16/vda16_valid_invalid_eight_curve_overlay"
)


def qualifying_mean_response_frame(histogram: np.ndarray) -> np.ndarray:
    """Conditional mean over qualifying response frames 5 and 6."""
    histogram = np.asarray(histogram)
    if histogram.shape[-1] != 8:
        raise ValueError("press histogram must use bins (-1, 0, ..., 6)")
    counts = histogram[..., 6:8].sum(axis=-1)
    weighted = histogram[..., 6] * 5.0 + histogram[..., 7] * 6.0
    return np.divide(
        weighted,
        counts,
        out=np.full(counts.shape, np.nan, dtype=float),
        where=counts > 0,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_source(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        return {key: np.asarray(archive[key]) for key in archive.files}


def main() -> int:
    data = {name: load_source(path) for name, path in SOURCES.items()}
    reference = next(iter(data.values()))
    magnitudes = reference["change_magnitudes"]
    validities = reference["displayed_validities"]
    for name, payload in data.items():
        if not np.array_equal(payload["change_magnitudes"], magnitudes):
            raise ValueError(f"change grid mismatch for {name}")
        if not np.array_equal(payload["displayed_validities"], validities):
            raise ValueError(f"displayed-validity grid mismatch for {name}")

    colors = ("#0072B2", "#009E73", "#E69F00", "#CC79A7")
    figure, axes = plt.subplots(
        2,
        2,
        figsize=(13.0, 7.8),
        sharex=True,
        sharey="row",
        constrained_layout=False,
    )

    for column, (name, payload) in enumerate(data.items()):
        valid_rate = payload["psychometric_response_rate_valid"]
        invalid_rate = payload["psychometric_response_rate_invalid"]
        valid_rt = qualifying_mean_response_frame(
            payload["psychometric_press_histogram_valid"]
        )
        invalid_rt = qualifying_mean_response_frame(
            payload["psychometric_press_histogram_invalid"]
        )
        for index, _validity in enumerate(validities):
            common = {"color": colors[index], "lw": 1.8, "ms": 4}
            axes[0, column].plot(
                magnitudes, valid_rate[index], marker="o", ls="-", **common
            )
            axes[0, column].plot(
                magnitudes,
                invalid_rate[index],
                marker="s",
                markerfacecolor="white",
                ls="--",
                **common,
            )
            axes[1, column].plot(
                magnitudes, valid_rt[index], marker="o", ls="-", **common
            )
            axes[1, column].plot(
                magnitudes,
                invalid_rt[index],
                marker="s",
                markerfacecolor="white",
                ls="--",
                **common,
            )

        axes[0, column].set_title(name, fontweight="bold", pad=8)
        axes[0, column].set_ylim(-0.02, 1.03)
        axes[1, column].set_ylim(4.95, 6.02)
        for row in range(2):
            axes[row, column].grid(alpha=0.2)
            axes[row, column].set_xlabel("orientation change (degrees)")

    axes[0, 0].set_ylabel("P(response at frame 5 or 6)")
    axes[1, 0].set_ylabel("mean response frame | response")
    axes[0, 0].text(
        0.01,
        0.97,
        "A  Qualifying-response probability",
        transform=axes[0, 0].transAxes,
        va="top",
        fontweight="bold",
    )
    axes[0, 1].text(
        0.01,
        0.97,
        "B  Qualifying-response probability",
        transform=axes[0, 1].transAxes,
        va="top",
        fontweight="bold",
    )
    axes[1, 0].text(
        0.01,
        0.97,
        "C  Conditional response timing",
        transform=axes[1, 0].transAxes,
        va="top",
        fontweight="bold",
    )
    axes[1, 1].text(
        0.01,
        0.97,
        "D  Conditional response timing",
        transform=axes[1, 1].transAxes,
        va="top",
        fontweight="bold",
    )

    validity_handles = [
        Line2D(
            [0],
            [0],
            color=color,
            marker="o",
            lw=1.8,
            label=f"{int(round(100 * validity))}% displayed",
        )
        for color, validity in zip(colors, validities, strict=True)
    ]
    condition_handles = [
        Line2D([0], [0], color="#444444", marker="o", lw=1.8, label="valid change"),
        Line2D(
            [0],
            [0],
            color="#444444",
            marker="s",
            markerfacecolor="white",
            lw=1.8,
            ls="--",
            label="forced-invalid change",
        ),
    ]
    figure.legend(
        handles=validity_handles + condition_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.885),
        ncol=6,
        frameon=False,
        fontsize=9,
    )
    figure.suptitle(
        "VDA16 valid-versus-invalid overlays: eight curves per panel\n"
        "Color encodes displayed cue proportion; line style encodes change location",
        fontweight="bold",
        y=0.985,
    )
    figure.text(
        0.5,
        -0.012,
        "The 100% displayed-validity invalid condition is a forced, out-of-policy stress test. "
        "Timing is conditional on a qualifying response.",
        ha="center",
        color="#555555",
        fontsize=9,
    )
    figure.subplots_adjust(
        left=0.075, right=0.995, bottom=0.105, top=0.79, hspace=0.12, wspace=0.08
    )

    OUTPUT_STEM.parent.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for suffix in ("pdf", "svg", "png"):
        output = OUTPUT_STEM.with_suffix(f".{suffix}")
        figure.savefig(output, dpi=300 if suffix == "png" else None, bbox_inches="tight")
        outputs[suffix] = output
    plt.close(figure)

    sidecar = {
        "figure": "VDA16 valid-versus-invalid eight-curve overlay",
        "panels": [
            "affine response probability",
            "cross-attention response probability",
            "affine conditional mean response frame",
            "cross-attention conditional mean response frame",
        ],
        "displayed_validities": validities.tolist(),
        "change_magnitudes_degrees": magnitudes.tolist(),
        "condition_encoding": {
            "valid": "solid line with filled circle",
            "forced_invalid": "dashed line with open square",
        },
        "condition_boundary": (
            "At displayed validity 1.0, invalid changes are forced out-of-policy "
            "stress tests rather than naturally sampled trials."
        ),
        "timing_definition": (
            "Conditional mean response frame over qualifying response frames 5 and 6."
        ),
        "sources": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in SOURCES.items()
        },
        "outputs": {suffix: str(path) for suffix, path in outputs.items()},
    }
    OUTPUT_STEM.with_suffix(".json").write_text(
        json.dumps(sidecar, indent=2) + "\n", encoding="utf-8"
    )
    for output in outputs.values():
        print(output)
    print(OUTPUT_STEM.with_suffix(".json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
