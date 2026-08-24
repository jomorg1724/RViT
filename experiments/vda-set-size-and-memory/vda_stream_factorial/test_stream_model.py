from __future__ import annotations

import pytest
import torch

from experiments.vda_stream_factorial.design_matrix import EXPECTED_PARAMETERS, build_matrix
from experiments.vda_stream_factorial.stream_model import (
    GroupedMeanProjector,
    build_stream_factorial_model,
)


@pytest.mark.parametrize("streams,effective_grid", [(4, (2, 2)), (100, (10, 10))])
def test_projector_is_idempotent_and_has_registered_rank(streams, effective_grid):
    projector = GroupedMeanProjector(10, 10, *effective_grid)
    assert torch.allclose(projector.matrix @ projector.matrix, projector.matrix, atol=1e-7)
    assert int(torch.linalg.matrix_rank(projector.matrix).item()) == streams
    values = torch.randn(2, 100, 7, requires_grad=True)
    projected = projector(values)
    assert projected.shape == values.shape
    projected.square().mean().backward()
    assert values.grad is not None and torch.isfinite(values.grad).all()


def test_four_stream_projector_makes_each_quadrant_identical():
    projector = GroupedMeanProjector(10, 10, 2, 2)
    values = torch.arange(100, dtype=torch.float32).reshape(1, 100, 1)
    projected = projector(values).reshape(10, 10)
    for rows in (slice(0, 5), slice(5, 10)):
        for cols in (slice(0, 5), slice(5, 10)):
            block = projected[rows, cols]
            assert torch.allclose(block, torch.full_like(block, block[0, 0]))


@pytest.mark.parametrize("feedback", ["crossattn1", "affine_ew"])
def test_parameter_count_and_readout_are_constant_across_factorial(feedback):
    observed = set()
    for visual in (4, 100):
        for memory in (4, 100):
            model = build_stream_factorial_model(visual, memory, feedback)
            observed.add(
                (
                    sum(parameter.numel() for parameter in model.parameters()),
                    model.encoder.readout_dim,
                    model.front.token_dim,
                    model.n_tokens,
                )
            )
    assert observed == {(EXPECTED_PARAMETERS[feedback], 12_800, 236, 100)}


def test_memory_rank_four_is_enforced_after_one_recurrent_step():
    torch.manual_seed(7)
    model = build_stream_factorial_model(100, 4, "crossattn1").eval()
    state = model.init_states(batch_size=1, device="cpu")
    frame = torch.randn(1, 3, 50, 50)
    with torch.no_grad():
        result = model.rl_step(frame, state)
    recurrent_state = result["new_states"][0]
    for component in recurrent_state:
        grouped = component.reshape(1, 10, 10, -1)
        for rows in (slice(0, 5), slice(5, 10)):
            for cols in (slice(0, 5), slice(5, 10)):
                block = grouped[:, rows, cols]
                assert torch.allclose(block, block[:, :1, :1].expand_as(block), atol=1e-6)


def test_paired_seed_starts_all_factor_cells_from_identical_trainable_tensors():
    snapshots = []
    for visual, memory in ((4, 4), (4, 100), (100, 4), (100, 100)):
        torch.manual_seed(19)
        model = build_stream_factorial_model(visual, memory, "crossattn1")
        snapshots.append({name: value.detach().clone() for name, value in model.named_parameters()})
    assert all(snapshot.keys() == snapshots[0].keys() for snapshot in snapshots[1:])
    for name, reference in snapshots[0].items():
        assert all(torch.equal(snapshot[name], reference) for snapshot in snapshots[1:])


def test_registered_matrix_contains_all_cells_and_no_training_claim():
    payload = build_matrix(seeds=(0, 1, 2))
    assert payload["status"] == "design_only_not_launched"
    for feedback in ("crossattn1", "affine_ew"):
        cells = payload["families"][feedback]
        assert {(cell["visual_streams"], cell["memory_streams"]) for cell in cells} == {
            (4, 4), (4, 100), (100, 4), (100, 100)
        }
        assert {cell["parameters"] for cell in cells} == {EXPECTED_PARAMETERS[feedback]}
