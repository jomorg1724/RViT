"""Deterministic M2 architecture figure for the VDA manuscript series.

The figure is generated from an explicit model-specification record traced to the
current implementation. It is a specification diagram, not learned-model evidence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ARCHITECTURE_FAMILIES = ("affine_ew", "crossattn1")


@dataclass(frozen=True)
class ArchitectureSpec:
    family: str
    claim_class: str
    is_model_result: bool
    shared_pipeline: tuple[str, ...]
    routing_equations: str
    source_paths: tuple[str, ...]


@dataclass(frozen=True)
class ArchitectureOutputs:
    pdf: Path
    svg: Path
    png: Path
    metadata: Path


_SHARED_PIPELINE = (
    "RGB frame",
    "patch front end",
    "feedback routing",
    "spatial xLSTM",
    "actor and QR critic",
)
_SOURCE_PATHS = ("model.py", "paper_encoder.py", "paper_heads.py")
_SPECS = {
    "affine_ew": ArchitectureSpec(
        family="affine_ew",
        claim_class="model specification",
        is_model_result=False,
        shared_pipeline=_SHARED_PIPELINE,
        routing_equations=(
            "b = tanh(B(H_prev)); gamma = G_scale(b); beta = G_shift(b); "
            "X_prime = gamma * X + beta; Q,K,V = W(X_prime); "
            "A = softmax(Q K^T / sqrt(d)); Z = X + A V"
        ),
        source_paths=_SOURCE_PATHS,
    ),
    "crossattn1": ArchitectureSpec(
        family="crossattn1",
        claim_class="model specification",
        is_model_result=False,
        shared_pipeline=_SHARED_PIPELINE,
        routing_equations=(
            "Q = W_q(X); K = concat(W_kx(X), W_kh(H_prev)); "
            "V = concat(W_vx(X), W_vh(H_prev)); "
            "A = softmax(Q K^T / sqrt(d)); Z = X + A V"
        ),
        source_paths=_SOURCE_PATHS,
    ),
}


def architecture_spec(family: str) -> ArchitectureSpec:
    """Return the admitted source-grounded architecture specification."""
    try:
        return _SPECS[family]
    except KeyError as exc:
        raise ValueError(
            f"unknown architecture family {family!r}; expected one of {ARCHITECTURE_FAMILIES}"
        ) from exc


def _box(
    axis: Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    *,
    face: str = "#E8F1F8",
    edge: str = "#1F4E79",
    fontsize: float = 9.0,
    linewidth: float = 1.2,
) -> None:
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        facecolor=face,
        edgecolor=edge,
        linewidth=linewidth,
    )
    axis.add_patch(patch)
    axis.text(x + width / 2.0, y + height / 2.0, text, ha="center", va="center", fontsize=fontsize)


def _arrow(
    axis: Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = "#46515C",
    style: str = "-|>",
    connectionstyle: str = "arc3",
    linewidth: float = 1.25,
) -> None:
    axis.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=12,
            linewidth=linewidth,
            color=color,
            connectionstyle=connectionstyle,
            shrinkA=2,
            shrinkB=2,
        )
    )


def _setup_panel(axis: Axes, label: str, title: str) -> None:
    axis.set_xlim(0.0, 1.0)
    axis.set_ylim(0.0, 1.0)
    axis.axis("off")
    axis.text(0.0, 1.02, label, fontsize=14, fontweight="bold", va="bottom")
    axis.text(0.055, 1.02, title, fontsize=12, fontweight="bold", va="bottom")


def _draw_shared_pipeline(axis: Axes) -> None:
    _setup_panel(axis, "A", "Shared recurrent VDA agent")
    labels = (
        "RGB frame\nH×W×3",
        "Conv patch front end\nN tokens × d",
        "feedback routing\nXₜ, Hₜ₋₁ → Zₜ",
        "spatial xLSTM\nper-token shared update",
    )
    xs = (0.02, 0.26, 0.52, 0.76)
    widths = (0.17, 0.20, 0.19, 0.20)
    faces = ("#F2F2F2", "#E8F1F8", "#FFF1D6", "#E4F4E8")
    for x, width, label, face in zip(xs, widths, labels, faces):
        _box(axis, x, 0.55, width, 0.20, label, face=face)
    for index in range(3):
        _arrow(axis, (xs[index] + widths[index], 0.65), (xs[index + 1], 0.65))

    _box(axis, 0.76, 0.22, 0.095, 0.14, "Actor\n2 logits", face="#F8E5EC", edge="#8F3B5C", fontsize=8.5)
    _box(axis, 0.865, 0.22, 0.095, 0.14, "QR critic\nA×Q", face="#F8E5EC", edge="#8F3B5C", fontsize=8.5)
    _arrow(axis, (0.86, 0.55), (0.807, 0.36), color="#8F3B5C")
    _arrow(axis, (0.88, 0.55), (0.912, 0.36), color="#8F3B5C")
    axis.text(0.87, 0.43, "flatten Hₜ", ha="center", fontsize=8, color="#8F3B5C")

    _box(axis, 0.52, 0.18, 0.17, 0.14, "JEPA head\ntraining auxiliary", face="#ECE8F7", edge="#5C4A8A", fontsize=8.5)
    _arrow(axis, (0.80, 0.55), (0.69, 0.31), color="#5C4A8A")
    axis.text(0.02, 0.08, "N follows the task geometry (2, 4, 9, or 16); d and memory width are run-resolved.", fontsize=8.5)


def _draw_affine(axis: Axes) -> None:
    _setup_panel(axis, "B", "Element-wise affine feedback (affine_ew)")
    _box(axis, 0.03, 0.63, 0.17, 0.16, "memory\nHₜ₋₁", face="#E4F4E8", edge="#287A45")
    _box(axis, 0.29, 0.63, 0.18, 0.16, "b = tanh(BH)", face="#FFF1D6", edge="#A86400")
    _box(axis, 0.57, 0.68, 0.16, 0.12, "γ = Gγ(b)", face="#FFF1D6", edge="#A86400")
    _box(axis, 0.57, 0.50, 0.16, 0.12, "β = Gβ(b)", face="#FFF1D6", edge="#A86400")
    _arrow(axis, (0.20, 0.71), (0.29, 0.71), color="#287A45")
    _arrow(axis, (0.47, 0.71), (0.57, 0.74), color="#A86400")
    _arrow(axis, (0.47, 0.69), (0.57, 0.56), color="#A86400")

    _box(axis, 0.03, 0.31, 0.17, 0.16, "visual tokens\nXₜ", face="#E8F1F8")
    _box(axis, 0.31, 0.29, 0.22, 0.20, "X′ = γ ⊙ X + β\nelement-wise modulation", face="#FFF1D6", edge="#A86400")
    _arrow(axis, (0.20, 0.39), (0.31, 0.39))
    _arrow(axis, (0.65, 0.50), (0.52, 0.46), color="#A86400")
    _arrow(axis, (0.65, 0.68), (0.48, 0.49), color="#A86400")

    _box(axis, 0.63, 0.27, 0.17, 0.24, "Q,K,V = W(X′)\nA = softmax(QKᵀ/√d)\nZ = X + AV", face="#F3E8F8", edge="#6D3A88", fontsize=8.5)
    _arrow(axis, (0.53, 0.39), (0.63, 0.39), color="#6D3A88")
    _box(axis, 0.85, 0.31, 0.12, 0.16, "Zₜ\nto xLSTM", face="#E4F4E8", edge="#287A45")
    _arrow(axis, (0.80, 0.39), (0.85, 0.39), color="#287A45")
    axis.text(0.03, 0.11, "Initialization: γ = 1 and β = 0, so routing starts as plain self-attention.", fontsize=8.7)


def _draw_memory(axis: Axes) -> None:
    _setup_panel(axis, "C", "Spatial recurrent memory and readouts")
    _box(axis, 0.03, 0.59, 0.16, 0.16, "routed tokens\nZₜ", face="#FFF1D6", edge="#A86400")
    _box(axis, 0.29, 0.50, 0.28, 0.32, "spatial xLSTM\n\nI,F,O,U gates\nC,N,M stabilised state\nHₜ = O ⊙ (C/N)", face="#E4F4E8", edge="#287A45")
    _arrow(axis, (0.19, 0.67), (0.29, 0.67), color="#287A45")
    _box(axis, 0.03, 0.27, 0.16, 0.14, "H,C,N,M\nat t−1", face="#E4F4E8", edge="#287A45", fontsize=8.5)
    _arrow(axis, (0.19, 0.34), (0.33, 0.50), color="#287A45")

    _box(axis, 0.66, 0.59, 0.14, 0.16, "Hₜ\nN×dₕ", face="#E4F4E8", edge="#287A45")
    _arrow(axis, (0.57, 0.67), (0.66, 0.67), color="#287A45")
    _arrow(
        axis,
        (0.70, 0.59),
        (0.56, 0.52),
        color="#287A45",
        connectionstyle="arc3,rad=-0.78",
        linewidth=1.35,
    )
    axis.text(0.66, 0.29, "Hₜ feeds routing\nat t+1", ha="center", fontsize=8.3, color="#287A45")

    _box(axis, 0.84, 0.62, 0.13, 0.13, "flatten\nN·dₕ", face="#F2F2F2", edge="#555555", fontsize=8.5)
    _arrow(axis, (0.80, 0.67), (0.84, 0.67))
    _box(axis, 0.81, 0.37, 0.075, 0.13, "actor", face="#F8E5EC", edge="#8F3B5C", fontsize=8.5)
    _box(axis, 0.90, 0.37, 0.075, 0.13, "critic", face="#F8E5EC", edge="#8F3B5C", fontsize=8.5)
    _arrow(axis, (0.89, 0.62), (0.85, 0.50), color="#8F3B5C")
    _arrow(axis, (0.92, 0.62), (0.94, 0.50), color="#8F3B5C")
    axis.text(0.03, 0.10, "Patch structure is preserved through routing and memory, then removed at the RL readout.", fontsize=8.7)


def _draw_cross(axis: Axes) -> None:
    _setup_panel(axis, "D", "Cross-attention comparator (crossattn1)")
    _box(axis, 0.03, 0.64, 0.16, 0.15, "visual tokens\nXₜ", face="#E8F1F8")
    _box(axis, 0.03, 0.32, 0.16, 0.15, "memory\nHₜ₋₁", face="#E4F4E8", edge="#287A45")
    _box(axis, 0.30, 0.65, 0.15, 0.13, "Q = Wq(X)", face="#E8F1F8")
    _box(axis, 0.30, 0.43, 0.22, 0.14, "K = [Wkx(X) ∥ Wkh(H)]", face="#FFF1D6", edge="#A86400", fontsize=8.5)
    _box(axis, 0.30, 0.22, 0.22, 0.14, "V = [Wvx(X) ∥ Wvh(H)]", face="#FFF1D6", edge="#A86400", fontsize=8.5)
    _arrow(axis, (0.19, 0.72), (0.30, 0.72))
    _arrow(axis, (0.19, 0.69), (0.30, 0.50), color="#A86400")
    _arrow(axis, (0.19, 0.65), (0.30, 0.29), color="#A86400")
    _arrow(axis, (0.19, 0.39), (0.30, 0.48), color="#287A45")
    _arrow(axis, (0.19, 0.37), (0.30, 0.29), color="#287A45")

    _box(axis, 0.61, 0.39, 0.18, 0.25, "A = softmax(QKᵀ/√d)\n\nN queries × 2N keys\n(image + memory)", face="#F3E8F8", edge="#6D3A88", fontsize=8.5)
    _arrow(axis, (0.45, 0.72), (0.63, 0.62), color="#6D3A88")
    _arrow(axis, (0.52, 0.50), (0.61, 0.54), color="#6D3A88")
    _arrow(axis, (0.52, 0.29), (0.64, 0.39), color="#6D3A88")
    _box(axis, 0.85, 0.43, 0.12, 0.17, "Z = X + AV\nto xLSTM", face="#E4F4E8", edge="#287A45", fontsize=8.5)
    _arrow(axis, (0.79, 0.51), (0.85, 0.51), color="#287A45")
    axis.text(0.03, 0.10, "The same recurrent memory and actor/critic heads follow; only the routing operator changes.", fontsize=8.7)


def _source_hashes(project_root: Path) -> dict[str, str]:
    paths = ("model.py", "paper_encoder.py", "paper_heads.py", "conv_frontend.py")
    return {
        path: hashlib.sha256((project_root / path).read_bytes()).hexdigest()
        for path in paths
    }


def build_m2_architecture_figure(output_dir: str | Path) -> ArchitectureOutputs:
    """Build M2 as PDF/SVG/PNG plus a source-hashed metadata record."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = ArchitectureOutputs(
        pdf=output_dir / "m2_architecture.pdf",
        svg=output_dir / "m2_architecture.svg",
        png=output_dir / "m2_architecture.png",
        metadata=output_dir / "m2_architecture.json",
    )

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })
    figure, axes = plt.subplots(2, 2, figsize=(16.0, 10.5), constrained_layout=True)
    _draw_shared_pipeline(axes[0, 0])
    _draw_affine(axes[0, 1])
    _draw_memory(axes[1, 0])
    _draw_cross(axes[1, 1])
    figure.suptitle("M2 · Recurrent VDA architecture and admitted feedback families", fontsize=15, fontweight="bold")
    figure.text(
        0.5,
        0.004,
        "Specification diagram generated from current source; no checkpoint measurements or behavioral outcomes are shown.",
        ha="center",
        fontsize=9,
        color="#4C566A",
    )
    figure.savefig(outputs.pdf, bbox_inches="tight")
    figure.savefig(outputs.svg, bbox_inches="tight")
    figure.savefig(outputs.png, dpi=300, bbox_inches="tight")
    plt.close(figure)

    # The combined source object is retained above, while these full-width
    # panel exports preserve 9 pt or larger text on A4 landscape pages.
    panel_outputs: dict[str, dict[str, str]] = {}
    for panel_id, drawer in (
        ("a", _draw_shared_pipeline),
        ("b", _draw_affine),
        ("c", _draw_memory),
        ("d", _draw_cross),
    ):
        panel_figure, panel_axis = plt.subplots(figsize=(11.4, 6.2), constrained_layout=True)
        drawer(panel_axis)
        panel_figure.text(
            0.5,
            0.012,
            "Model specification from current source; not a checkpoint result.",
            ha="center",
            fontsize=9,
            color="#4C566A",
        )
        panel_paths = {
            "pdf": output_dir / f"m2_architecture_{panel_id}.pdf",
            "svg": output_dir / f"m2_architecture_{panel_id}.svg",
            "png": output_dir / f"m2_architecture_{panel_id}.png",
        }
        panel_figure.savefig(panel_paths["pdf"], bbox_inches="tight")
        panel_figure.savefig(panel_paths["svg"], bbox_inches="tight")
        panel_figure.savefig(panel_paths["png"], dpi=300, bbox_inches="tight")
        plt.close(panel_figure)
        panel_outputs[panel_id] = {kind: path.name for kind, path in panel_paths.items()}

    project_root = Path(__file__).resolve().parents[1]
    metadata = {
        "schema_version": 1,
        "source_object": "M2",
        "claim_class": "model specification",
        "is_model_result": False,
        "families": list(ARCHITECTURE_FAMILIES),
        "panel_map": {
            "M2a": "patching and visual features",
            "M2b": "routing/allocation mechanism",
            "M2c": "recurrent memory update",
            "M2d": "actor and critic readouts",
        },
        "specifications": {family: asdict(architecture_spec(family)) for family in ARCHITECTURE_FAMILIES},
        "source_sha256": _source_hashes(project_root),
        "producer": str(Path(__file__).resolve()),
        "outputs": {
            "pdf": outputs.pdf.name,
            "svg": outputs.svg.name,
            "png": outputs.png.name,
            "manuscript_panels": panel_outputs,
        },
        "claim_boundary": "This figure documents implemented computation and is not evidence of learning, performance, or biological mechanism.",
    }
    outputs.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return outputs
