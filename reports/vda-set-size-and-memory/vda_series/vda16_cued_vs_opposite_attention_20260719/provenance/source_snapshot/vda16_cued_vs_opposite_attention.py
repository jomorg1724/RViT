"""Paired VDA16 cue-location versus opposite-corner attention experiment.

The cue is fixed at S1 (top-left) with displayed validity 100%. Matched latent
trial streams are evaluated with the physical change forced either at S1 or at
S16 (bottom-right). The analysis records behavior and achieved spatial
attention mass, defined for cross-attention as the sum of the image key and
corresponding recurrent-memory key, averaged over query tokens.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path
import sys
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vda_sweep import matched_width as protocol
from vda_sweep import vda_core as core


TASK = "vda16"
FEEDBACK = "crossattn1"
WIDTH = 128
CUE_INDEX = 0
OPPOSITE_INDEX = 15
DISPLAYED_VALIDITY = 1.0
CUE_COLOR = "red"
TRIALS_PER_POINT = 300
SEED = protocol.PSYCHOMETRIC_SEED
CHANGE_MAGNITUDES = np.asarray(protocol.CHANGE_MAGNITUDES, dtype=np.float64)
FOCAL_MAGNITUDE = 30.0
EXPECTED_CHECKPOINT_SHA256 = (
    "b40d9aa49ec28c352d7a790de84f5902e1a307f7b2abe5fe68dc9e6aabb4f84d"
)
CONDITION_NAMES = ("cued_top_left", "forced_bottom_right")
CONDITION_LABELS = ("change at cued S1 (top-left)", "change at S16 (bottom-right)")
CONDITION_COLORS = ("#0072B2", "#D55E00")
TIMESTEP_LABELS = ("t0", "t1 cue", "t2", "t3 array", "t4 pre-change", "t5 change", "t6")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_press(actor_logits: np.ndarray) -> np.ndarray:
    actions = np.asarray(actor_logits).argmax(axis=-1)
    press = np.full(actions.shape[0], -1, dtype=np.int64)
    for timestep in range(actions.shape[1]):
        newly_pressed = (actions[:, timestep] == 1) & (press < 0)
        press[newly_pressed] = timestep
    return press


def achieved_location_mass(raw_attention: np.ndarray) -> np.ndarray:
    """Return trial x time x location mass after summing image and memory keys."""
    raw = np.asarray(raw_attention, dtype=np.float64)
    if raw.ndim != 4:
        raise ValueError(f"attention must be B x T x N x K; got {raw.shape}")
    _, _, queries, keys = raw.shape
    if queries != 16 or keys != 32:
        raise ValueError(f"expected VDA16 cross-attention N=16, K=32; got {raw.shape}")
    image = raw[..., :queries]
    memory = raw[..., queries:]
    mass = (image + memory).mean(axis=2)
    np.testing.assert_allclose(
        mass.sum(axis=-1),
        np.ones(mass.shape[:2]),
        rtol=1e-5,
        atol=1e-6,
        err_msg="aggregated spatial attention mass does not sum to one",
    )
    return mass


def mean_sem(values: np.ndarray, axis: int = 0) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(values, dtype=np.float64)
    mean = np.nanmean(values, axis=axis)
    count = np.sum(np.isfinite(values), axis=axis)
    sd = np.nanstd(values, axis=axis, ddof=1)
    sem = np.divide(
        sd,
        np.sqrt(count),
        out=np.full_like(mean, np.nan, dtype=np.float64),
        where=count > 1,
    )
    return mean, sem


def wilson_interval(count: np.ndarray, trials: int, z: float = 1.96) -> tuple[np.ndarray, np.ndarray]:
    count = np.asarray(count, dtype=np.float64)
    proportion = count / trials
    denominator = 1.0 + z * z / trials
    center = (proportion + z * z / (2.0 * trials)) / denominator
    half = z * np.sqrt(
        proportion * (1.0 - proportion) / trials + z * z / (4.0 * trials * trials)
    ) / denominator
    return center - half, center + half


def paired_interval(difference: np.ndarray) -> dict[str, float]:
    difference = np.asarray(difference, dtype=np.float64)
    mean = float(difference.mean())
    sem = float(difference.std(ddof=1) / np.sqrt(difference.size))
    return {
        "mean": mean,
        "sem": sem,
        "ci95_low": mean - 1.96 * sem,
        "ci95_high": mean + 1.96 * sem,
        "trials": int(difference.size),
    }


def save_figure(figure: plt.Figure, stem: Path) -> dict[str, Path]:
    stem.parent.mkdir(parents=True, exist_ok=True)
    outputs = {suffix: stem.with_suffix(f".{suffix}") for suffix in ("pdf", "svg", "png")}
    figure.savefig(outputs["pdf"], bbox_inches="tight")
    figure.savefig(outputs["svg"], bbox_inches="tight")
    figure.savefig(outputs["png"], dpi=300, bbox_inches="tight")
    plt.close(figure)
    return outputs


def build_summary_figure(
    press: np.ndarray,
    spatial_mass: np.ndarray,
    focal_index: int,
    output_stem: Path,
) -> dict[str, Path]:
    qualifying = press >= 5
    response_count = qualifying.sum(axis=-1)
    response_rate = response_count / press.shape[-1]
    response_frames = np.where(qualifying, press, np.nan)
    rt_mean, rt_sem = mean_sem(response_frames, axis=-1)

    target_mass = np.stack(
        (spatial_mass[0, ..., CUE_INDEX], spatial_mass[1, ..., OPPOSITE_INDEX]),
        axis=0,
    )
    target_mean, target_sem = mean_sem(target_mass, axis=2)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    figure, axes = plt.subplots(2, 2, figsize=(13.2, 8.3), constrained_layout=True)
    for condition in range(2):
        color = CONDITION_COLORS[condition]
        label = CONDITION_LABELS[condition]
        low, high = wilson_interval(response_count[condition], press.shape[-1])
        axes[0, 0].plot(
            CHANGE_MAGNITUDES,
            response_rate[condition],
            color=color,
            marker="o" if condition == 0 else "s",
            ms=4,
            lw=2,
            label=label,
        )
        axes[0, 0].fill_between(CHANGE_MAGNITUDES, low, high, color=color, alpha=0.13)
        axes[0, 1].plot(
            CHANGE_MAGNITUDES,
            rt_mean[condition],
            color=color,
            marker="o" if condition == 0 else "s",
            ms=4,
            lw=2,
            label=label,
        )
        axes[0, 1].fill_between(
            CHANGE_MAGNITUDES,
            rt_mean[condition] - 1.96 * rt_sem[condition],
            rt_mean[condition] + 1.96 * rt_sem[condition],
            color=color,
            alpha=0.13,
        )
        axes[1, 0].plot(
            CHANGE_MAGNITUDES,
            target_mean[condition, :, 5],
            color=color,
            marker="o" if condition == 0 else "s",
            ms=4,
            lw=2,
            label=label,
        )
        axes[1, 0].fill_between(
            CHANGE_MAGNITUDES,
            target_mean[condition, :, 5] - 1.96 * target_sem[condition, :, 5],
            target_mean[condition, :, 5] + 1.96 * target_sem[condition, :, 5],
            color=color,
            alpha=0.13,
        )
        axes[1, 1].plot(
            np.arange(7),
            target_mean[condition, focal_index],
            color=color,
            marker="o" if condition == 0 else "s",
            ms=4,
            lw=2,
            label=label,
        )
        axes[1, 1].fill_between(
            np.arange(7),
            target_mean[condition, focal_index] - 1.96 * target_sem[condition, focal_index],
            target_mean[condition, focal_index] + 1.96 * target_sem[condition, focal_index],
            color=color,
            alpha=0.13,
        )

    axes[0, 0].set(
        title="A  Change-report probability",
        xlabel="orientation change (degrees)",
        ylabel="P(response at t5 or t6)",
        ylim=(-0.02, 1.02),
    )
    axes[0, 1].set(
        title="B  Response timing",
        xlabel="orientation change (degrees)",
        ylabel="mean response frame | qualifying response",
        ylim=(4.95, 6.05),
    )
    axes[1, 0].set(
        title="C  Achieved attention at changed location on t5",
        xlabel="orientation change (degrees)",
        ylabel="image-key + memory-key attention mass",
    )
    axes[1, 1].set(
        title=f"D  Changed-location attention trajectory at {FOCAL_MAGNITUDE:.0f} degrees",
        xlabel="logical timestep",
        ylabel="image-key + memory-key attention mass",
        xticks=np.arange(7),
        xticklabels=TIMESTEP_LABELS,
    )
    for axis in axes.flat:
        axis.grid(alpha=0.2)
        axis.axhline(1.0 / 16.0, color="#555555", lw=0.9, ls=":", label="uniform location mass")
    axes[0, 0].legend(frameon=False, fontsize=8)
    axes[1, 0].legend(frameon=False, fontsize=8)
    axes[1, 1].axvline(4, color="#777777", lw=0.8, ls="--")
    axes[1, 1].axvline(5, color="#777777", lw=0.8, ls="--")
    figure.suptitle(
        "VDA16 4x4 - crossattn1 - cue S1 top-left - 100% displayed validity\n"
        "Paired checkpoint rerun: change at S1 versus forced change at S16; "
        "bands are 95% evaluation-trial intervals",
        fontweight="bold",
    )
    figure.text(
        0.5,
        -0.01,
        "Attention is summed over the changed location's image and recurrent-memory keys, "
        "then averaged over query tokens. Intervals describe finite trials from one checkpoint, "
        "not training-seed uncertainty.",
        ha="center",
        fontsize=8,
        color="#4C566A",
    )
    return save_figure(figure, output_stem)


def add_location_outlines(axis: plt.Axes, change_index: int) -> None:
    cue_row, cue_col = divmod(CUE_INDEX, 4)
    change_row, change_col = divmod(change_index, 4)
    axis.add_patch(
        Rectangle(
            (cue_col - 0.5, cue_row - 0.5),
            1,
            1,
            fill=False,
            edgecolor="#E31A1C",
            linewidth=2.2,
        )
    )
    axis.add_patch(
        Rectangle(
            (change_col - 0.42, change_row - 0.42),
            0.84,
            0.84,
            fill=False,
            edgecolor="#33A02C",
            linewidth=2.2,
            linestyle="--",
        )
    )


def build_spatial_figure(
    spatial_mass: np.ndarray,
    focal_index: int,
    output_stem: Path,
) -> dict[str, Path]:
    maps = spatial_mass[:, focal_index].mean(axis=1)
    selected = maps[:, (4, 5)]
    vmax = float(selected.max())
    figure, axes = plt.subplots(2, 2, figsize=(9.2, 8.0), constrained_layout=True)
    image = None
    for condition in range(2):
        change_index = CUE_INDEX if condition == 0 else OPPOSITE_INDEX
        for column, timestep in enumerate((4, 5)):
            axis = axes[condition, column]
            image = axis.imshow(
                maps[condition, timestep].reshape(4, 4),
                cmap="cividis",
                vmin=0.0,
                vmax=vmax,
                interpolation="nearest",
            )
            add_location_outlines(axis, change_index)
            axis.set_xticks([])
            axis.set_yticks([])
            if condition == 0:
                axis.set_title("t4 pre-change" if timestep == 4 else "t5 change frame", fontweight="bold")
            if column == 0:
                axis.set_ylabel(CONDITION_LABELS[condition], fontweight="bold")
    assert image is not None
    colorbar = figure.colorbar(image, ax=axes, shrink=0.76)
    colorbar.set_label("achieved spatial attention mass")
    figure.suptitle(
        f"VDA16 changed-location attention maps at {FOCAL_MAGNITUDE:.0f} degrees\n"
        "red solid = cue S1; green dashed = physical change location",
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.01,
        "Each cell sums image and recurrent-memory key mass and averages over all query tokens "
        f"and {TRIALS_PER_POINT} matched trials. Shared zero-to-observed-maximum color scale.",
        ha="center",
        fontsize=8,
        color="#4C566A",
    )
    return save_figure(figure, output_stem)


def run(checkpoint: Path, output_root: Path) -> dict[str, Any]:
    import scipy
    import torch

    checkpoint = checkpoint.resolve()
    checkpoint_sha256 = sha256_file(checkpoint)
    if checkpoint_sha256 != EXPECTED_CHECKPOINT_SHA256:
        raise RuntimeError(
            f"checkpoint SHA-256 {checkpoint_sha256} does not match admitted "
            f"{EXPECTED_CHECKPOINT_SHA256}"
        )
    model, iteration = core.load(TASK, FEEDBACK, WIDTH, checkpoint_path=str(checkpoint))
    if iteration != 19999:
        raise RuntimeError(f"expected terminal iteration 19999, got {iteration}")

    conditions = ((CUE_INDEX, CONDITION_NAMES[0]), (OPPOSITE_INDEX, CONDITION_NAMES[1]))
    press = np.full((2, len(CHANGE_MAGNITUDES), TRIALS_PER_POINT), -1, dtype=np.int64)
    spatial_mass = np.zeros(
        (2, len(CHANGE_MAGNITUDES), TRIALS_PER_POINT, 7, 16), dtype=np.float32
    )
    point_seeds = np.zeros(len(CHANGE_MAGNITUDES), dtype=np.int64)

    for magnitude_index, magnitude in enumerate(CHANGE_MAGNITUDES):
        point_seed = SEED + magnitude_index * 101
        point_seeds[magnitude_index] = point_seed
        for condition_index, (change_index, condition_name) in enumerate(conditions):
            print(
                f"[{magnitude_index + 1}/{len(CHANGE_MAGNITUDES)}] "
                f"{condition_name} magnitude={magnitude:g} seed={point_seed}",
                flush=True,
            )
            videos = core.make_video_batch(
                TASK,
                CUE_INDEX,
                DISPLAYED_VALIDITY,
                CUE_COLOR,
                1,
                change_index,
                float(magnitude),
                B=TRIALS_PER_POINT,
                seed=int(point_seed),
            )
            with torch.no_grad():
                result = model.forward_rl_sequence(videos, return_attn=True)
            logits = result["actor_logits_seq"].detach().cpu().numpy()
            raw_attention = result["attn_seq"].detach().cpu().numpy()
            press[condition_index, magnitude_index] = first_press(logits)
            spatial_mass[condition_index, magnitude_index] = achieved_location_mass(raw_attention)
            del videos, result, logits, raw_attention

    if sha256_file(checkpoint) != checkpoint_sha256:
        raise RuntimeError("checkpoint changed during analysis")

    focal_matches = np.flatnonzero(np.isclose(CHANGE_MAGNITUDES, FOCAL_MAGNITUDE))
    if focal_matches.size != 1:
        raise RuntimeError(f"focal magnitude {FOCAL_MAGNITUDE} is not uniquely present")
    focal_index = int(focal_matches[0])
    target_mass = np.stack(
        (spatial_mass[0, ..., CUE_INDEX], spatial_mass[1, ..., OPPOSITE_INDEX]),
        axis=0,
    )
    t4_difference = paired_interval(
        target_mass[0, focal_index, :, 4] - target_mass[1, focal_index, :, 4]
    )
    t5_difference = paired_interval(
        target_mass[0, focal_index, :, 5] - target_mass[1, focal_index, :, 5]
    )
    qualifying = press >= 5
    response_rate = qualifying.mean(axis=-1)
    response_frames = np.where(qualifying, press, np.nan)
    rt_mean, _ = mean_sem(response_frames, axis=-1)
    target_mean, target_sem = mean_sem(target_mass, axis=2)

    output_root.mkdir(parents=True, exist_ok=True)
    data_dir = output_root / "data"
    figures_dir = output_root / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    cache_path = data_dir / "vda16_cued_vs_opposite_attention.npz"
    metadata = {
        "schema_version": 1,
        "artifact": "paired VDA16 cued-location versus opposite-corner behavior and attention",
        "task": TASK,
        "feedback": FEEDBACK,
        "width": WIDTH,
        "grid": [4, 4],
        "checkpoint_iteration": iteration,
        "checkpoint_path": str(checkpoint),
        "checkpoint_sha256": checkpoint_sha256,
        "competence_status": "competence-gated",
        "displayed_validity": DISPLAYED_VALIDITY,
        "cue_index": CUE_INDEX,
        "cue_location": "top-left",
        "change_indices": [CUE_INDEX, OPPOSITE_INDEX],
        "change_locations": ["top-left", "bottom-right"],
        "change_magnitudes_degrees": CHANGE_MAGNITUDES.tolist(),
        "focal_magnitude_degrees": FOCAL_MAGNITUDE,
        "trials_per_point": TRIALS_PER_POINT,
        "seed": SEED,
        "seed_policy": (
            "common random numbers matched across forced change locations at each magnitude"
        ),
        "qualifying_response_frames": [5, 6],
        "attention_reduction": (
            "sum image and corresponding recurrent-memory key for each spatial location; "
            "arithmetic mean over all 16 query tokens"
        ),
        "uniform_spatial_location_mass": 1.0 / 16.0,
        "t4_interpretation": (
            "pre-change matched-frame contrast; isolates cue-established spatial routing"
        ),
        "t5_interpretation": (
            "change-frame contrast; combines cue-established and change-evoked routing"
        ),
        "focal_paired_attention_difference_top_left_minus_bottom_right": {
            "t4": t4_difference,
            "t5": t5_difference,
        },
        "focal_response_rate": {
            CONDITION_NAMES[0]: float(response_rate[0, focal_index]),
            CONDITION_NAMES[1]: float(response_rate[1, focal_index]),
        },
        "focal_mean_response_frame_conditional": {
            CONDITION_NAMES[0]: float(rt_mean[0, focal_index]),
            CONDITION_NAMES[1]: float(rt_mean[1, focal_index]),
        },
        "runtime_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
            "device": str(core.DEVICE),
        },
        "producer_path": str(Path(__file__).resolve()),
        "producer_sha256": sha256_file(Path(__file__).resolve()),
        "inference_boundary": (
            "single competence-gated checkpoint and finite matched evaluation trials; "
            "not training-seed uncertainty, curriculum completion, or a causal set-size result"
        ),
    }
    np.savez_compressed(
        cache_path,
        press_times=press,
        qualifying_response=qualifying,
        response_rate=response_rate,
        conditional_mean_response_frame=rt_mean,
        spatial_attention_mass_trials=spatial_mass,
        target_attention_mass_trials=target_mass,
        target_attention_mean=target_mean,
        target_attention_sem=target_sem,
        change_magnitudes=CHANGE_MAGNITUDES,
        point_seeds=point_seeds,
        condition_names=np.asarray(CONDITION_NAMES),
        condition_change_indices=np.asarray((CUE_INDEX, OPPOSITE_INDEX), dtype=np.int64),
        focal_magnitude=np.asarray(FOCAL_MAGNITUDE),
        metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
    )
    summary_outputs = build_summary_figure(
        press, spatial_mass, focal_index, figures_dir / "vda16_cued_vs_opposite_summary"
    )
    spatial_outputs = build_spatial_figure(
        spatial_mass, focal_index, figures_dir / "vda16_cued_vs_opposite_spatial_maps"
    )

    summary_path = data_dir / "summary.json"
    metadata["cache_path"] = str(cache_path.resolve())
    metadata["cache_sha256"] = sha256_file(cache_path)
    metadata["figure_outputs"] = {
        "summary": {suffix: str(path.resolve()) for suffix, path in summary_outputs.items()},
        "spatial_maps": {suffix: str(path.resolve()) for suffix, path in spatial_outputs.items()},
    }
    summary_path.write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    csv_path = data_dir / "curves.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "condition",
                "change_index",
                "magnitude_degrees",
                "response_rate",
                "conditional_mean_response_frame",
                "target_attention_t4_mean",
                "target_attention_t4_sem",
                "target_attention_t5_mean",
                "target_attention_t5_sem",
            ]
        )
        for condition_index, condition_name in enumerate(CONDITION_NAMES):
            for magnitude_index, magnitude in enumerate(CHANGE_MAGNITUDES):
                writer.writerow(
                    [
                        condition_name,
                        CUE_INDEX if condition_index == 0 else OPPOSITE_INDEX,
                        float(magnitude),
                        float(response_rate[condition_index, magnitude_index]),
                        float(rt_mean[condition_index, magnitude_index]),
                        float(target_mean[condition_index, magnitude_index, 4]),
                        float(target_sem[condition_index, magnitude_index, 4]),
                        float(target_mean[condition_index, magnitude_index, 5]),
                        float(target_sem[condition_index, magnitude_index, 5]),
                    ]
                )

    readme_path = output_root / "README.md"
    readme_path.write_text(
        "# VDA16 cued versus opposite-corner attention\n\n"
        "Cue S1 is fixed at the top-left with 100% displayed validity. The physical "
        "change is forced either at S1 or at S16 (bottom-right) on matched latent trial "
        "streams. Achieved spatial attention sums the image key and corresponding "
        "recurrent-memory key and averages over query tokens.\n\n"
        f"The focal comparison uses {FOCAL_MAGNITUDE:.0f} degrees. See `data/summary.json` "
        "for paired t4 and t5 attention differences and the figures for behavior and "
        "spatial maps. This is one competence-gated checkpoint; evaluation-trial "
        "intervals are not training-seed uncertainty.\n",
        encoding="utf-8",
    )
    artifact_paths = [
        cache_path,
        summary_path,
        csv_path,
        readme_path,
        *summary_outputs.values(),
        *spatial_outputs.values(),
        Path(__file__).resolve(),
        checkpoint,
    ]
    manifest = {
        "schema_version": 1,
        "created_by": str(Path(__file__).resolve()),
        "artifacts": [
            {
                "path": str(path.resolve()),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in artifact_paths
        ],
    }
    manifest_path = output_root / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata["focal_paired_attention_difference_top_left_minus_bottom_right"], indent=2))
    print(f"wrote {output_root.resolve()}")
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run(arguments.checkpoint, arguments.output_root)
