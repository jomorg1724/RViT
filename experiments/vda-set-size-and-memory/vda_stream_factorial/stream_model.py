"""Experimental constant-shape stream controls for RViT.

This module intentionally lives outside the production model.  It fixes a 10x10
carrier tensor (100 visual positions, 100 recurrent positions, 100*128 flattened
readout) and changes only the rank of two fixed, non-parametric projections:

* visual projection: group-average frontend tokens before routing;
* memory projection: group-average routed writes before the spatial xLSTM.

The four-item VDA display, trainable parameter shapes, actor/critic readout, and
training budget can therefore remain identical while effective visual and memory
stream counts are crossed independently at 4 versus 100.

Only the single-xLSTM ``crossattn1`` and ``affine_ew`` families are admitted by
this scaffold.  It is not wired into ``train_rl.py`` yet and must not be used as
production evidence without a dedicated launcher, provenance fields, and tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import torch
import torch.nn as nn

from model import RViTPaperModel
from paper_encoder import RecurrentViTxLSTM


class GroupedMeanProjector(nn.Module):
    """Fixed mean-and-broadcast projection over the token axis.

    ``input`` must end in ``(..., carrier_tokens, feature_dim)``.  A rectangular
    effective grid partitions the carrier grid into equal contiguous blocks.
    Every output position receives its block mean.  The projection is idempotent
    and its matrix rank equals ``effective_rows * effective_cols``.
    """

    def __init__(
        self,
        carrier_rows: int,
        carrier_cols: int,
        effective_rows: int,
        effective_cols: int,
    ) -> None:
        super().__init__()
        values = (carrier_rows, carrier_cols, effective_rows, effective_cols)
        if any(int(value) <= 0 for value in values):
            raise ValueError("carrier and effective grid dimensions must be positive")
        if carrier_rows % effective_rows or carrier_cols % effective_cols:
            raise ValueError("effective grid must divide the carrier grid exactly")

        self.carrier_rows = int(carrier_rows)
        self.carrier_cols = int(carrier_cols)
        self.effective_rows = int(effective_rows)
        self.effective_cols = int(effective_cols)
        self.carrier_tokens = self.carrier_rows * self.carrier_cols
        self.effective_streams = self.effective_rows * self.effective_cols

        row_group = torch.arange(self.carrier_rows) // (self.carrier_rows // self.effective_rows)
        col_group = torch.arange(self.carrier_cols) // (self.carrier_cols // self.effective_cols)
        group_ids = (
            row_group[:, None] * self.effective_cols + col_group[None, :]
        ).reshape(-1)
        matrix = torch.zeros(self.carrier_tokens, self.carrier_tokens, dtype=torch.float32)
        for group in range(self.effective_streams):
            members = torch.nonzero(group_ids == group, as_tuple=False).flatten()
            matrix[members[:, None], members[None, :]] = 1.0 / float(members.numel())
        self.register_buffer("group_ids", group_ids, persistent=True)
        self.register_buffer("matrix", matrix, persistent=True)

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        if values.ndim < 2 or values.shape[-2] != self.carrier_tokens:
            raise ValueError(
                f"expected token axis {-2} to have length {self.carrier_tokens}; "
                f"got shape {tuple(values.shape)}"
            )
        matrix = self.matrix.to(device=values.device, dtype=values.dtype)
        return torch.einsum("ij,...jd->...id", matrix, values)


class ProjectedMemoryEncoder(RecurrentViTxLSTM):
    """Single-xLSTM encoder with a fixed-rank recurrent write bottleneck."""

    _ALLOWED_FEEDBACK = frozenset(("crossattn1", "affine_ew"))

    def __init__(self, *args, memory_projector: GroupedMeanProjector, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.feedback not in self._ALLOWED_FEEDBACK:
            raise ValueError(
                "stream factorial admits only crossattn1 and affine_ew; "
                f"got {self.feedback!r}"
            )
        if self.cell != "xlstm" or self.two_lstm:
            raise ValueError("stream factorial requires one standard xlstm recurrent cell")
        if memory_projector.carrier_tokens != self.n_patch:
            raise ValueError("memory projector carrier size does not match encoder patches")
        self.memory_projector = memory_projector

    def _project_state(self, state):
        return tuple(self.memory_projector(component) for component in state)

    def forward_step(
        self,
        X: torch.Tensor,
        state,
        return_attn: bool = False,
        attn_clamp=None,
        inject_memory_noise: bool = False,
    ):
        # Projecting the routed write before the shared recurrent update makes all
        # positions in a memory group receive the same input and carry the same
        # H/C/N/M state.  Thus the token-axis state rank is the registered M level.
        state = self._project_state(state)
        H_prev = state[0]
        Z, attn = self.attn(
            X,
            H_prev,
            return_attn=return_attn,
            attn_clamp=attn_clamp,
        )
        Z_write = self.memory_projector(Z)
        next_state, _ = self._run_recurrent_cell(
            self.lstm,
            Z_write,
            state,
            inject_memory_noise=inject_memory_noise,
        )
        next_state = self._project_state(next_state)
        return next_state, next_state[0], attn


class ProjectedFrontEnd(nn.Module):
    """Parameter-preserving wrapper that projects frontend tokens."""

    def __init__(self, base: nn.Module, projector: GroupedMeanProjector) -> None:
        super().__init__()
        if int(base.n_tokens) != projector.carrier_tokens:
            raise ValueError("visual projector carrier size does not match frontend tokens")
        self.base = base
        self.projector = projector
        # Preserve the public fields consumed by train_rl.py and analysis code.
        self.n_tokens = int(base.n_tokens)
        self.token_dim = int(base.token_dim)
        self.patch_height = base.patch_height
        self.patch_width = base.patch_width
        self.frozen = bool(base.frozen)

    def forward(self, x: torch.Tensor, t: int) -> torch.Tensor:
        return self.projector(self.base(x, t))


@dataclass(frozen=True)
class StreamFactorialCondition:
    visual_streams: int
    memory_streams: int

    @property
    def label(self) -> str:
        return f"visual{self.visual_streams}_memory{self.memory_streams}"


class StreamFactorialModel(RViTPaperModel):
    """RViT with fixed 100-slot carrier and independent V/M rank controls."""

    CARRIER_ROWS = 10
    CARRIER_COLS = 10
    EFFECTIVE_GRIDS = {4: (2, 2), 100: (10, 10)}

    def __init__(
        self,
        *,
        effective_visual_streams: int,
        effective_memory_streams: int,
        feedback: str,
        d_mem: int = 128,
        image_size: int = 50,
        **kwargs,
    ) -> None:
        if effective_visual_streams not in self.EFFECTIVE_GRIDS:
            raise ValueError("effective_visual_streams must be 4 or 100")
        if effective_memory_streams not in self.EFFECTIVE_GRIDS:
            raise ValueError("effective_memory_streams must be 4 or 100")
        if feedback not in ProjectedMemoryEncoder._ALLOWED_FEEDBACK:
            raise ValueError("feedback must be crossattn1 or affine_ew")
        if kwargs.get("two_lstm", False):
            raise ValueError("two_lstm is outside the registered stream-factorial design")
        if kwargs.get("cell", "xlstm") != "xlstm":
            raise ValueError("cell must be xlstm in the registered stream-factorial design")

        kwargs.update(
            feedback=feedback,
            d_mem=int(d_mem),
            conv_frontend=True,
            grid_rows=self.CARRIER_ROWS,
            grid_cols=self.CARRIER_COLS,
            image_size=int(image_size),
            cell="xlstm",
            two_lstm=False,
        )
        super().__init__(**kwargs)

        visual_grid = self.EFFECTIVE_GRIDS[effective_visual_streams]
        memory_grid = self.EFFECTIVE_GRIDS[effective_memory_streams]
        visual_projector = GroupedMeanProjector(
            self.CARRIER_ROWS, self.CARRIER_COLS, *visual_grid
        )
        memory_projector = GroupedMeanProjector(
            self.CARRIER_ROWS, self.CARRIER_COLS, *memory_grid
        )
        self.front = ProjectedFrontEnd(self.front, visual_projector)
        self.encoder = ProjectedMemoryEncoder(
            d_token=int(self.front.token_dim),
            d_mem=int(d_mem),
            n_patch=self.CARRIER_ROWS * self.CARRIER_COLS,
            feedback=feedback,
            two_lstm=False,
            cell="xlstm",
            memory_decay=float(kwargs.get("memory_decay", 1.0)),
            memory_noise_std=float(kwargs.get("memory_noise_std", 0.0)),
            memory_projector=memory_projector,
        )
        self.n_tokens = int(self.encoder.n_patch)
        self.effective_visual_streams = int(effective_visual_streams)
        self.effective_memory_streams = int(effective_memory_streams)
        self.stream_condition = StreamFactorialCondition(
            self.effective_visual_streams, self.effective_memory_streams
        )


def build_stream_factorial_model(
    visual_streams: int,
    memory_streams: int,
    feedback: str,
    **kwargs,
) -> StreamFactorialModel:
    """Factory kept explicit so a future launcher can provenance-hash one entrypoint."""

    defaults = dict(
        n_actions=2,
        n_quantiles=5,
        init_action_bias=[0.0, -1.5],
        seq_len=7,
        jepa_n_heads=4,
        jepa_proto_dim=256,
        frame_repeat=1,
        memory_decay=1.0,
        memory_noise_std=0.0,
    )
    defaults.update(kwargs)
    return StreamFactorialModel(
        effective_visual_streams=visual_streams,
        effective_memory_streams=memory_streams,
        feedback=feedback,
        **defaults,
    )
