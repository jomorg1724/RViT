"""Constant-shape visual-versus-memory stream experiment scaffolding."""

from .stream_model import (
    GroupedMeanProjector,
    ProjectedMemoryEncoder,
    StreamFactorialModel,
    build_stream_factorial_model,
)

__all__ = [
    "GroupedMeanProjector",
    "ProjectedMemoryEncoder",
    "StreamFactorialModel",
    "build_stream_factorial_model",
]
