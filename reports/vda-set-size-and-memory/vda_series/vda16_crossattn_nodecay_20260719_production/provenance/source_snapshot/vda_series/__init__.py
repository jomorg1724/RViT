"""High-quality, source-mapped figure builders for the VDA manuscript series."""

from .task_figures import VDA_TASK_ORDER, build_m1_task_figure, task_spec
from .architecture_figures import ARCHITECTURE_FAMILIES, build_m2_architecture_figure
from .behavior_figures import BEHAVIOR_TASKS, build_m3_behavior_figure

__all__ = [
    "ARCHITECTURE_FAMILIES",
    "BEHAVIOR_TASKS",
    "VDA_TASK_ORDER",
    "build_m1_task_figure",
    "build_m2_architecture_figure",
    "build_m3_behavior_figure",
    "task_spec",
]
