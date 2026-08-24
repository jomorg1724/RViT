"""Source-mapped M3 behavior figures regenerated from the preserved psych.npz cache.

This module never reruns a model. It validates and plots archived aggregate arrays,
records their checksum, and makes undefined/blocked distinctions explicit.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


M3_PANELS = ("M3A", "M3B", "M3C", "M3D", "M3E", "M3F")
BEHAVIOR_TASKS = ("vda1", "vda2", "vda4", "vda9")
FEEDBACK_FAMILIES = ("affine_ew", "crossattn1")


@dataclass(frozen=True)
class BehaviorOutputs:
    pdf: Path
    svg: Path
    png: Path
    metadata: Path


@dataclass
class ArchivedPsychology:
    path: Path
    source_sha256: str
    change_magnitudes: np.ndarray
    validities: np.ndarray
    arrays: dict[str, np.ndarray]

    def iteration(self, task: str, feedback: str) -> int:
        return int(self.arrays[f"{task}_{feedback}_iter"])

    def curve(self, task: str, feedback: str, validity: float, location: str, metric: str) -> np.ndarray:
        suffix = "" if metric == "response_rate" else "_rt"
        key = f"{task}_{feedback}_p{validity}_{location}{suffix}"
        try:
            values = np.asarray(self.arrays[key], dtype=np.float64)
        except KeyError as exc:
            raise ValueError(f"archive is missing required M3 array {key!r}") from exc
        if values.shape != self.change_magnitudes.shape:
            raise ValueError(f"archive array {key!r} has shape {values.shape}, expected {self.change_magnitudes.shape}")
        return values


_DEFAULT_CACHE = Path(__file__).resolve().parents[1] / "vda_sweep" / "figs" / "psych.npz"


def load_archived_psychology(path: str | Path = _DEFAULT_CACHE) -> ArchivedPsychology:
    """Load and validate the preserved aggregate cache without model execution."""
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with np.load(path, allow_pickle=False) as payload:
        arrays = {key: np.array(payload[key], copy=True) for key in payload.files}
    change_magnitudes = np.asarray(arrays.get("DE"), dtype=np.float64)
    validities = np.asarray(arrays.get("PROPS"), dtype=np.float64)
    if change_magnitudes.shape != (10,) or not np.array_equal(
        change_magnitudes, np.array([0, 3, 6, 9, 12, 15, 18, 22, 26, 30], dtype=np.float64)
    ):
        raise ValueError("psychology archive has an unexpected change-magnitude axis")
    if validities.shape != (4,) or not np.array_equal(validities, np.array([0.25, 0.5, 0.75, 1.0])):
        raise ValueError("psychology archive has an unexpected validity axis")
    cache = ArchivedPsychology(path, digest, change_magnitudes, validities, arrays)
    for task in BEHAVIOR_TASKS:
        for feedback in FEEDBACK_FAMILIES:
            cache.iteration(task, feedback)
            for validity in validities:
                for metric in ("response_rate", "response_time"):
                    values = cache.curve(task, feedback, float(validity), "cued", metric)
                    if not np.isfinite(values).all():
                        raise ValueError(f"non-finite admitted M3 values for {task}/{feedback}/{validity}/{metric}")
                    if task != "vda1":
                        uncued = cache.curve(task, feedback, float(validity), "uncued", metric)
                        if not np.isfinite(uncued).all():
                            raise ValueError(
                                f"non-finite admitted uncued-location values for {task}/{feedback}/{validity}/{metric}"
                            )
    return cache


def m3_panel_status(task: str, panel: str) -> str:
    """Return the scientific disposition for one M3 panel and environment."""
    if panel not in M3_PANELS:
        raise ValueError(f"unknown M3 panel {panel!r}; expected one of {M3_PANELS}")
    if task in BEHAVIOR_TASKS:
        if task == "vda1" and panel in {"M3B", "M3C", "M3E", "M3F"}:
            return "undefined"
        return "available"
    if task == "vda16":
        return "blocked"
    if task == "vda_fixed16":
        return "training"
    if task == "vda_fixed1":
        return "undefined" if panel in {"M3B", "M3C", "M3E", "M3F"} else "blocked"
    if task in {"vda_fixed2", "vda_fixed4", "vda_fixed9"}:
        return "blocked"
    if task in {"validity4", "vda_excl", "vda_probe_cued", "vda_probe_uncued"}:
        return "inapplicable"
    raise ValueError(f"unknown VDA environment {task!r}")


def _panel_label(axis, label: str) -> None:
    axis.text(-0.16, 1.06, label[-1], transform=axis.transAxes, fontsize=13, fontweight="bold", va="top")


def _undefined_panel(axis, label: str, metric: str) -> None:
    _panel_label(axis, label)
    axis.set_facecolor("#F4F4F4")
    axis.text(
        0.5,
        0.56,
        "Undefined",
        transform=axis.transAxes,
        ha="center",
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#555555",
    )
    axis.text(
        0.5,
        0.38,
        "VDA1 has one active item;\nno uncued active change location exists.",
        transform=axis.transAxes,
        ha="center",
        va="center",
        fontsize=9,
        color="#555555",
    )
    axis.set_title(metric)
    axis.set_xticks([])
    axis.set_yticks([])
    for spine in axis.spines.values():
        spine.set_color("#999999")
        spine.set_linestyle("--")


def _style_axis(axis, *, response_time: bool) -> None:
    axis.set_xlim(-0.5, 30.5)
    axis.set_xticks((0, 6, 12, 18, 24, 30))
    axis.grid(alpha=0.18, linewidth=0.7)
    axis.spines[["top", "right"]].set_visible(False)
    if response_time:
        axis.set_ylabel("mean response frame\nconditional on scored response")
        axis.set_ylim(4.95, 6.05)
    else:
        axis.set_ylabel("P(change response)")
        axis.set_ylim(-0.02, 1.02)
    axis.set_xlabel("orientation change Δ (degrees)")


def _plot_validity_family(axis, cache, task, feedback, metric, panel, colors, markers) -> None:
    response_time = metric == "response_time"
    for validity, color, marker in zip(cache.validities, colors, markers):
        axis.plot(
            cache.change_magnitudes,
            cache.curve(task, feedback, float(validity), "cued", metric),
            color=color,
            marker=marker,
            markevery=(1 if response_time else 2),
            markersize=4.0,
            linewidth=1.7,
            label=f"{validity:.0%}",
        )
    _panel_label(axis, panel)
    axis.set_title("Cued-location change by displayed validity")
    _style_axis(axis, response_time=response_time)
    axis.legend(title="displayed validity", frameon=False, fontsize=8, title_fontsize=8, ncol=2)


def _plot_location_pair(axis, cache, task, feedback, validity, metric, panel) -> None:
    response_time = metric == "response_time"
    styles = (
        ("cued", "#0072B2", "o", "cued location"),
        ("uncued", "#D55E00", "s", "archived uncued location"),
    )
    for location, color, marker, label in styles:
        axis.plot(
            cache.change_magnitudes,
            cache.curve(task, feedback, validity, location, metric),
            color=color,
            marker=marker,
            markevery=(1 if response_time else 2),
            markersize=4.0,
            linewidth=1.8,
            label=label,
        )
    _panel_label(axis, panel)
    axis.set_title(f"Cued / archived uncued\nvalidity {validity:.0%}", fontsize=9.5, pad=4)
    _style_axis(axis, response_time=response_time)
    axis.legend(frameon=False, fontsize=8)


def build_m3_behavior_figure(
    task: str,
    feedback: str,
    output_dir: str | Path,
    *,
    archive_path: str | Path = _DEFAULT_CACHE,
) -> BehaviorOutputs:
    """Regenerate the six M3 panels for one admitted historical task/family."""
    status = m3_panel_status(task, "M3A")
    if status != "available":
        raise ValueError(f"M3 behavior result for {task!r} is {status}; no empirical figure will be generated")
    if feedback not in FEEDBACK_FAMILIES:
        raise ValueError(f"unknown feedback family {feedback!r}; expected one of {FEEDBACK_FAMILIES}")
    cache = load_archived_psychology(archive_path)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"m3_behavior_{task}_{feedback}"
    outputs = BehaviorOutputs(
        pdf=output_dir / f"{stem}.pdf",
        svg=output_dir / f"{stem}.svg",
        png=output_dir / f"{stem}.png",
        metadata=output_dir / f"{stem}.json",
    )

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })
    # Sized for near-native placement on an A4 landscape manuscript page.
    figure, axes = plt.subplots(2, 3, figsize=(11.4, 6.7), constrained_layout=True)
    layout_engine = figure.get_layout_engine()
    if layout_engine is not None:
        layout_engine.set(rect=(0.02, 0.075, 0.96, 0.86))
    colors = ("#0072B2", "#009E73", "#E69F00", "#CC79A7")
    markers = ("o", "s", "^", "D")
    _plot_validity_family(axes[0, 0], cache, task, feedback, "response_rate", "M3A", colors, markers)
    _plot_validity_family(axes[1, 0], cache, task, feedback, "response_time", "M3D", colors, markers)
    if task == "vda1":
        for axis, panel, title in (
            (axes[0, 1], "M3B", "Response rate · displayed validity 25%"),
            (axes[0, 2], "M3C", "Response rate · displayed validity 100%"),
            (axes[1, 1], "M3E", "Conditional response frame · validity 25%"),
            (axes[1, 2], "M3F", "Conditional response frame · validity 100%"),
        ):
            _undefined_panel(axis, panel, title)
    else:
        _plot_location_pair(axes[0, 1], cache, task, feedback, 0.25, "response_rate", "M3B")
        _plot_location_pair(axes[0, 2], cache, task, feedback, 1.0, "response_rate", "M3C")
        _plot_location_pair(axes[1, 1], cache, task, feedback, 0.25, "response_time", "M3E")
        _plot_location_pair(axes[1, 2], cache, task, feedback, 1.0, "response_time", "M3F")

    iteration = cache.iteration(task, feedback)
    figure.suptitle(
        f"M3 · {task} · {feedback} · archived aggregate at iteration {iteration}",
        fontsize=14,
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.018,
        "Regenerated from preserved psych.npz aggregates; no checkpoint rerun and no uncertainty estimates are available.",
        ha="center",
        fontsize=8.5,
        color="#4C566A",
    )
    figure.savefig(outputs.pdf, bbox_inches="tight")
    figure.savefig(outputs.svg, bbox_inches="tight")
    figure.savefig(outputs.png, dpi=300, bbox_inches="tight")
    plt.close(figure)

    project_root = Path(__file__).resolve().parents[1]
    producer_script = project_root / "vda_sweep" / "vda_fig_psych.py"
    publication_status = {
        panel: ("undefined" if m3_panel_status(task, panel) == "undefined" else "complete")
        for panel in M3_PANELS
    }
    epistemic_status = {
        panel: ("undefined" if status == "undefined" else "cache-attributed-aggregate")
        for panel, status in publication_status.items()
    }
    metadata = {
        "schema_version": 1,
        "source_object": "M3",
        "task": task,
        "feedback": feedback,
        "checkpoint_iteration_reported_in_cache": iteration,
        "evidence_class": "regenerated from archived NPZ",
        "recomputed_from_checkpoint": False,
        "source_npz": str(cache.path.resolve()),
        "source_npz_sha256": cache.source_sha256,
        "panel_status_axis": "publication_coverage",
        "panel_status": publication_status,
        "epistemic_status_axis": "claim_support",
        "epistemic_status": epistemic_status,
        "panel_map": {
            "M3A": "response rate by displayed validity for cued-location changes",
            "M3B": "response rate: cued versus archived uncued change at 25% displayed validity",
            "M3C": "response rate: cued versus archived uncued change at 100% displayed validity",
            "M3D": "conditional response frame by displayed validity for cued-location changes",
            "M3E": "conditional response frame: cued versus archived uncued change at 25% displayed validity",
            "M3F": "conditional response frame: cued versus archived uncued change at 100% displayed validity",
        },
        "change_magnitudes_degrees": cache.change_magnitudes.tolist(),
        "displayed_validities": cache.validities.tolist(),
        "producer_source_reported_trials_per_point": 300,
        "producer_source_current_sha256": hashlib.sha256(producer_script.read_bytes()).hexdigest(),
        "producer_source_hash_boundary": "The NPZ does not embed its producer hash; this is the current script hash, not proof of the historical execution source.",
        "producer_semantics_boundary": "The inspected current producer evaluates change-conditioned trials at forced cued or uncued locations. The NPZ does not prove that this exact producer generated the historical cache.",
        "uncued_location_boundary": "The NPZ labels these arrays 'uncued' but does not embed the evaluated spatial index. The figures therefore do not rename them as geometrically opposing locations.",
        "outputs": {"pdf": outputs.pdf.name, "svg": outputs.svg.name, "png": outputs.png.name},
        "claim_boundary": "Publication coverage marked complete means the admitted cache-derived product, sidecar, manuscript placement, and QA are complete. Epistemically, the values remain cache-attributed aggregate point estimates and do not establish historical producer identity, sampling uncertainty, seed reliability, convergence, or mechanism.",
    }
    outputs.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return outputs
