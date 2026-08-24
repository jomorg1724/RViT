"""Deterministic, source-mapped task figures for the VDA manuscript series.

This module deliberately derives task schematics from explicit historical or
prospective task specifications rather than from archived learned checkpoints.
It therefore visualizes task mechanics only; it does not constitute model-result
evidence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


VDA_TASK_ORDER = (
    "validity4",
    "vda1",
    "vda2",
    "vda4",
    "vda9",
    "vda16",
    "vda_excl",
    "vda_fixed1",
    "vda_fixed2",
    "vda_fixed4",
    "vda_fixed9",
    "vda_fixed16",
    "vda_probe_cued",
    "vda_probe_uncued",
)


@dataclass(frozen=True)
class TaskSpec:
    name: str
    grid: tuple[int, int]
    image_size: int
    token_count: int
    active_count: int
    validity_mode: str
    lineage: str
    value_cues: bool = True
    probe_location: str | None = None


@dataclass(frozen=True)
class FigureOutputs:
    pdf: Path
    png: Path
    metadata: Path


_TASK_SPECS = {
    "validity4": TaskSpec(
        "validity4", (2, 2), 50, 4, 4, "archived_including_cue", "historical-comparator", False
    ),
    "vda1": TaskSpec("vda1", (2, 2), 50, 4, 1, "degenerate_singleton", "historical"),
    "vda2": TaskSpec("vda2", (2, 2), 50, 4, 2, "exact_excluding_cue", "historical"),
    "vda4": TaskSpec("vda4", (2, 2), 50, 4, 4, "archived_including_cue", "historical"),
    "vda9": TaskSpec("vda9", (3, 3), 75, 9, 9, "archived_including_cue", "historical"),
    # The current VDA16 run was trained after VDAEnv adopted the exact
    # Bernoulli sampler: the invalid branch excludes the cue. Keep the archived
    # including-cue rule for the historical VDA4/VDA9 artifacts above.
    "vda16": TaskSpec("vda16", (4, 4), 100, 16, 16, "exact_excluding_cue", "current"),
    "vda_excl": TaskSpec("vda_excl", (1, 2), 50, 2, 2, "exclusion_target_only", "historical"),
    "vda_fixed1": TaskSpec("vda_fixed1", (4, 4), 100, 16, 1, "degenerate_singleton", "controlled"),
    "vda_fixed2": TaskSpec("vda_fixed2", (4, 4), 100, 16, 2, "exact_excluding_cue", "controlled"),
    "vda_fixed4": TaskSpec("vda_fixed4", (4, 4), 100, 16, 4, "exact_excluding_cue", "controlled"),
    "vda_fixed9": TaskSpec("vda_fixed9", (4, 4), 100, 16, 9, "exact_excluding_cue", "controlled"),
    "vda_fixed16": TaskSpec("vda_fixed16", (4, 4), 100, 16, 16, "exact_excluding_cue", "controlled"),
    "vda_probe_cued": TaskSpec(
        "vda_probe_cued", (2, 2), 50, 4, 4, "archived_including_cue", "historical-probe", True, "cued"
    ),
    "vda_probe_uncued": TaskSpec(
        "vda_probe_uncued", (2, 2), 50, 4, 4, "archived_including_cue", "historical-probe", True, "uncued"
    ),
}


def task_spec(task: str) -> TaskSpec:
    """Return the immutable task mechanics used by source-mapped schematics."""
    try:
        return _TASK_SPECS[task]
    except KeyError as exc:
        raise ValueError(f"unknown VDA task {task!r}; expected one of {VDA_TASK_ORDER}") from exc


def _validated_active_indices(spec: TaskSpec, active_indices: Iterable[int]) -> tuple[int, ...]:
    active = tuple(int(index) for index in active_indices)
    if len(active) != spec.active_count or len(active) != len(set(active)):
        raise ValueError(
            f"active_indices must contain exactly {spec.active_count} unique indices for {spec.name}"
        )
    if any(index < 0 or index >= spec.token_count for index in active):
        raise ValueError(f"active_indices must lie in [0, {spec.token_count})")
    return active


def realized_target_distribution(
    spec: TaskSpec,
    cue_index: int,
    displayed_validity: float,
    active_indices: Iterable[int],
) -> np.ndarray:
    """Return the task's realized target distribution over all model tokens.

    Historical ``archived_including_cue`` tasks use the preserved rule in which
    an invalid-branch draw is uniform over every active item, including the cue.
    The current VDA16 run and controlled fixed-grid tasks draw the invalid branch
    only from non-cued active items, making displayed and realized validity equal.
    """
    active = _validated_active_indices(spec, active_indices)
    cue_index = int(cue_index)
    if cue_index not in active:
        raise ValueError("cue_index must be active")
    validity = float(displayed_validity)
    if not np.isfinite(validity) or not 0.0 <= validity <= 1.0:
        raise ValueError("displayed_validity must lie in [0, 1]")

    distribution = np.zeros(spec.token_count, dtype=np.float64)
    if spec.validity_mode in {"degenerate_singleton", "exclusion_target_only"}:
        distribution[cue_index] = 1.0
    elif spec.validity_mode == "archived_including_cue":
        distribution[list(active)] = (1.0 - validity) / len(active)
        distribution[cue_index] += validity
    elif spec.validity_mode == "exact_excluding_cue":
        if len(active) < 2:
            raise ValueError("exact_excluding_cue requires at least two active indices")
        distribution[cue_index] = validity
        uncued = [index for index in active if index != cue_index]
        distribution[uncued] = (1.0 - validity) / len(uncued)
    else:  # defensive: TaskSpec is public and may be constructed externally
        raise ValueError(f"unsupported validity_mode {spec.validity_mode!r}")
    return distribution


def realized_cue_probability_curve(
    spec: TaskSpec,
    cue_index: int,
    active_indices: Iterable[int],
) -> tuple[np.ndarray, np.ndarray]:
    """Return the displayed and realized cue probabilities shown in M1."""
    displayed = (
        np.array([1.0], dtype=np.float64)
        if spec.validity_mode == "exclusion_target_only"
        else np.array([0.25, 0.5, 0.75, 1.0], dtype=np.float64)
    )
    realized = np.array([
        realized_target_distribution(spec, cue_index, value, active_indices)[cue_index]
        for value in displayed
    ])
    return displayed, realized


def _active_indices(spec: TaskSpec) -> tuple[int, ...]:
    """Choose a deterministic, spatially spread active set for task schematics."""
    if spec.active_count == spec.token_count:
        return tuple(range(spec.token_count))
    if spec.active_count == 1:
        return (0,)
    candidates = np.linspace(0, spec.token_count - 1, spec.active_count)
    active = tuple(dict.fromkeys(int(round(value)) for value in candidates))
    if len(active) != spec.active_count:
        active = tuple(range(spec.active_count))
    return active


def _cell_bounds(spec: TaskSpec, index: int) -> tuple[int, int, int, int]:
    rows, cols = spec.grid
    row, col = divmod(index, cols)
    row_edges = np.linspace(0, spec.image_size, rows + 1, dtype=int)
    col_edges = np.linspace(0, spec.image_size, cols + 1, dtype=int)
    return row_edges[row], row_edges[row + 1], col_edges[col], col_edges[col + 1]


def _gabor(height: int, width: int, orientation_deg: float) -> np.ndarray:
    y, x = np.mgrid[-1.0:1.0:complex(height), -1.0:1.0:complex(width)]
    angle = np.deg2rad(orientation_deg)
    carrier = x * np.cos(angle) + y * np.sin(angle)
    envelope = np.exp(-3.5 * (x * x + y * y))
    return (0.5 + 0.5 * np.cos(5.0 * np.pi * carrier) * envelope).astype(np.float32)


def _render_stimuli(
    spec: TaskSpec,
    active: tuple[int, ...],
    orientations: dict[int, float],
) -> np.ndarray:
    frame = np.zeros((spec.image_size, spec.image_size, 3), dtype=np.float32)
    for index in active:
        r0, r1, c0, c1 = _cell_bounds(spec, index)
        margin = max(1, int(round(min(r1 - r0, c1 - c0) * 0.10)))
        patch = _gabor(r1 - r0 - 2 * margin, c1 - c0 - 2 * margin, orientations[index])
        frame[r0 + margin:r1 - margin, c0 + margin:c1 - margin, :] = patch[..., None]
    return frame


def render_cue_frame(spec: TaskSpec, cue_index: int, displayed_validity: float) -> np.ndarray:
    """Render the source cue: validity arc around a central value disk."""
    validity = float(displayed_validity)
    if not np.isfinite(validity) or not 0.0 <= validity <= 1.0:
        raise ValueError("displayed_validity must lie in [0, 1]")

    frame = np.zeros((spec.image_size, spec.image_size, 3), dtype=np.float32)
    r0, r1, c0, c1 = _cell_bounds(spec, cue_index)
    height, width = r1 - r0, c1 - c0
    yy, xx = np.mgrid[0:height, 0:width]
    cy, cx = (height - 1) / 2.0, (width - 1) / 2.0
    radius = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    scale = float(min(height, width))
    cell = frame[r0:r1, c0:c1]

    disk = radius <= 0.11 * scale
    disk_color = (
        np.array([0.90, 0.25, 0.10], dtype=np.float32)
        if spec.value_cues
        else np.array([0.55, 0.55, 0.55], dtype=np.float32)
    )
    cell[disk] = disk_color

    theta = (np.arctan2(yy - cy, xx - cx) + np.pi / 2.0) % (2.0 * np.pi)
    ring = (radius >= 0.23 * scale) & (radius <= 0.31 * scale)
    arc = ring & (theta <= validity * 2.0 * np.pi + 1e-12)
    cell[arc] = 1.0
    return frame


def render_timeline_frames(spec: TaskSpec, seed: int = 0, change: bool = True) -> tuple[np.ndarray, ...]:
    """Render the seven VDA task frames without invoking a learned model."""
    rng = np.random.default_rng(seed)
    active = _active_indices(spec)
    cue_index = active[0]
    baseline = {index: float(rng.uniform(0.0, 180.0)) for index in active}
    changed = dict(baseline)
    if change:
        distribution = realized_target_distribution(spec, cue_index, 0.75, active)
        target = int(rng.choice(spec.token_count, p=distribution))
        changed[target] = (changed[target] + 56.0) % 180.0

    blank = np.zeros((spec.image_size, spec.image_size, 3), dtype=np.float32)
    cue_validity = 1.0 if spec.validity_mode == "exclusion_target_only" else 0.75
    cue = render_cue_frame(spec, cue_index, cue_validity)
    delay = blank.copy()
    if spec.probe_location is not None:
        probe_index = cue_index
        if spec.probe_location == "uncued":
            probe_index = next(index for index in active if index != cue_index)
        probe_orientation = {probe_index: float(rng.uniform(0.0, 180.0))}
        delay = _render_stimuli(spec, (probe_index,), probe_orientation)
    before = _render_stimuli(spec, active, baseline)
    after = _render_stimuli(spec, active, changed)
    return (blank.copy(), cue, delay, before.copy(), before.copy(), after.copy(), after.copy())


def _distribution_grid(spec: TaskSpec, distribution: np.ndarray) -> np.ndarray:
    rows, cols = spec.grid
    return distribution.reshape(rows, cols) * 100.0


def build_m1_task_figure(task: str, output_dir: str | Path, seed: int = 0) -> FigureOutputs:
    """Build the source-mapped M1 task figure as PDF, PNG, and JSON metadata."""
    spec = task_spec(task)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"m1_task_{task}"
    outputs = FigureOutputs(
        pdf=output_dir / f"{stem}.pdf",
        png=output_dir / f"{stem}.png",
        metadata=output_dir / f"{stem}.json",
    )

    frames = render_timeline_frames(spec, seed=seed, change=True)
    active = _active_indices(spec)
    cue_index = active[0]
    displayed_validity = 1.0 if spec.validity_mode == "exclusion_target_only" else 0.25
    distribution = realized_target_distribution(spec, cue_index, displayed_validity, active)

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 10,
        "axes.labelsize": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    figure = plt.figure(figsize=(15.0, 8.8), constrained_layout=True)
    grid = figure.add_gridspec(3, 7, height_ratios=(1.0, 0.92, 1.05))
    frame_titles = (
        "t0 · blank",
        "t1 · value/validity cue" if spec.value_cues else "t1 · validity cue",
        "t2 · delay probe" if spec.probe_location else "t2 · delay",
        "t3 · array onset",
        "t4 · maintenance",
        "t5 · possible change",
        "t6 · response",
    )
    for index, (frame, title) in enumerate(zip(frames, frame_titles)):
        axis = figure.add_subplot(grid[0, index])
        axis.imshow(np.clip(frame, 0.0, 1.0), interpolation="nearest")
        axis.set_title(title, pad=7)
        axis.set_xticks([])
        axis.set_yticks([])
        for spine in axis.spines.values():
            spine.set_color("#4C566A")
            spine.set_linewidth(0.8)

    cue_validities = (
        (1.0,) if spec.validity_mode == "exclusion_target_only" else (0.25, 0.5, 0.75, 1.0)
    )
    cue_grid = grid[1, 0:4].subgridspec(1, 4)
    for index, validity in enumerate(cue_validities):
        cue_axis = figure.add_subplot(cue_grid[0, index])
        cue_axis.imshow(render_cue_frame(spec, cue_index, validity), interpolation="nearest")
        cue_axis.set_title(f"displayed validity {validity:.0%}", pad=6)
        cue_axis.set_xticks([])
        cue_axis.set_yticks([])
    if len(cue_validities) == 1:
        note_axis = figure.add_subplot(cue_grid[0, 1:4])
        note_axis.axis("off")
        note_axis.text(
            0.5,
            0.5,
            "25–75% cue configurations are inapplicable:\n"
            "the exclusion task is target-valid by construction.",
            ha="center",
            va="center",
            transform=note_axis.transAxes,
        )

    curve_axis = figure.add_subplot(grid[1, 4:7])
    displayed_curve, realized_curve = realized_cue_probability_curve(spec, cue_index, active)
    curve_axis.plot(
        displayed_curve,
        realized_curve,
        color="#0072B2",
        marker="o",
        linewidth=2.0,
        label="realized cue probability",
    )
    curve_axis.plot([0.25, 1.0], [0.25, 1.0], color="#666666", linestyle="--", label="displayed = realized")
    curve_axis.set_xlim(0.22, 1.03)
    curve_axis.set_ylim(0.22, 1.03)
    curve_axis.set_xticks((0.25, 0.5, 0.75, 1.0))
    curve_axis.set_yticks((0.25, 0.5, 0.75, 1.0))
    curve_axis.set_xlabel("displayed validity")
    curve_axis.set_ylabel("realized P(target = cue)")
    curve_axis.set_title("Displayed and realized validity")
    curve_axis.grid(alpha=0.2)
    curve_axis.legend(frameon=False, fontsize=8, loc="lower right")

    heat_axis = figure.add_subplot(grid[2, 0:3])
    location_grid = _distribution_grid(spec, distribution)
    image = heat_axis.imshow(location_grid, cmap="viridis", vmin=0.0, vmax=100.0)
    for (row, col), value in np.ndenumerate(location_grid):
        color = "white" if value < 45.0 else "black"
        heat_axis.text(col, row, f"{value:.1f}%", ha="center", va="center", color=color, fontsize=9)
    heat_axis.set_title(f"Realized target-location distribution at displayed validity {displayed_validity:.2f}")
    heat_axis.set_xticks(range(spec.grid[1]))
    heat_axis.set_yticks(range(spec.grid[0]))
    heat_axis.set_xlabel("grid column")
    heat_axis.set_ylabel("grid row")
    figure.colorbar(image, ax=heat_axis, label="target probability (%)", fraction=0.05, pad=0.04)

    semantics_axis = figure.add_subplot(grid[2, 3:5])
    semantics_axis.axis("off")
    realized_at_cue = float(distribution[cue_index])
    semantics_axis.text(
        0.0,
        1.0,
        "Task semantics",
        transform=semantics_axis.transAxes,
        va="top",
        fontsize=12,
        fontweight="bold",
    )
    semantics_lines = [
        f"Environment: {spec.name}",
        f"Lineage: {spec.lineage}",
        f"Geometry: {spec.grid[0]}×{spec.grid[1]} grid; {spec.image_size}×{spec.image_size} RGB",
        f"Model tokens: {spec.token_count}",
        f"Active items: {spec.active_count}",
        f"Validity rule: {spec.validity_mode}",
        f"Realized P(target = cue): {realized_at_cue:.3f}",
    ]
    if spec.name == "vda_excl":
        semantics_lines.extend((
            "Shown branch: distractor present",
            "Paired branch: target alone (distractor blank)",
        ))
    if spec.probe_location is not None:
        semantics_lines.extend((
            f"Delay probe: {spec.probe_location} location",
            "Probe is passive; no dedicated trained checkpoint",
        ))
    semantics_axis.text(
        0.0,
        0.86,
        "\n".join(semantics_lines),
        transform=semantics_axis.transAxes,
        va="top",
        linespacing=1.45,
    )

    boundary_axis = figure.add_subplot(grid[2, 5:7])
    boundary_axis.axis("off")
    boundary_axis.text(
        0.0,
        1.0,
        "Evidence boundary",
        transform=boundary_axis.transAxes,
        va="top",
        fontsize=12,
        fontweight="bold",
    )
    boundary_axis.text(
        0.0,
        0.86,
        "Deterministic task-derived schematic.\n\n"
        "It documents geometry, timing, active-item count, and target-sampling semantics. "
        "It contains no learned-model measurement and does not establish performance, "
        "convergence, neural equivalence, or a capacity limit.",
        transform=boundary_axis.transAxes,
        va="top",
        wrap=True,
        linespacing=1.45,
    )

    task_family = "Cued change-detection comparator" if spec.name == "validity4" else "Value-directed change-detection task"
    figure.suptitle(
        f"M1 · {task_family} — {spec.name}",
        fontsize=15,
        fontweight="bold",
    )
    figure.savefig(outputs.pdf, bbox_inches="tight")
    figure.savefig(outputs.png, dpi=300, bbox_inches="tight")
    plt.close(figure)

    metadata = {
        "schema_version": 2,
        "figure_id": "M1",
        "task": asdict(spec),
        "seed": int(seed),
        "evidence_class": "task-derived schematic",
        "active_indices": list(active),
        "cue_index": cue_index,
        "displayed_validity": displayed_validity,
        "realized_target_distribution": distribution.tolist(),
        "cue_configurations": list(cue_validities),
        "displayed_validity_curve": displayed_curve.tolist(),
        "realized_cue_probability_curve": realized_curve.tolist(),
        "timeline_frames": 7,
        "outputs": {"pdf": outputs.pdf.name, "png": outputs.png.name},
    }
    outputs.metadata.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return outputs
