from __future__ import annotations

from analysis.vda4_spatial_scaling_evaluation import (
    all_task_regions,
    regional_clamp,
    spatial_shuffle_permutation,
    task_region_tokens,
)
from analysis.vda_endpoint_evaluation import (
    build_parser,
    compute_psychometrics,
    evaluation_protocol,
)
from vda_sweep.vda_core import conditioned_active_locations


def test_task_quadrants_partition_every_registered_grid() -> None:
    for size, expected_region_size in ((2, 1), (4, 4), (10, 25)):
        regions = all_task_regions(size, size)
        assert len(regions) == 4
        assert all(len(region) == expected_region_size for region in regions)
        assert sorted(token for region in regions for token in region) == list(range(size * size))


def test_top_left_and_bottom_right_region_indices() -> None:
    assert task_region_tokens(2, 2, 0) == (0,)
    assert task_region_tokens(2, 2, 3) == (3,)
    assert task_region_tokens(4, 4, 0) == (0, 1, 4, 5)
    assert task_region_tokens(4, 4, 3) == (10, 11, 14, 15)
    assert task_region_tokens(10, 10, 0) == tuple(r * 10 + c for r in range(5) for c in range(5))
    assert task_region_tokens(10, 10, 3) == tuple(r * 10 + c for r in range(5, 10) for c in range(5, 10))


def test_regional_clamp_covers_self_or_paired_image_memory_keys() -> None:
    tokens = task_region_tokens(4, 4, 0)
    affine = regional_clamp("affine_ew", 16, tokens, 1.0)
    cross = regional_clamp("crossattn1", 16, tokens, 1.0)
    assert set(map(int, affine)) == set(tokens)
    assert set(map(int, cross)) == set(tokens) | {16 + token for token in tokens}
    assert set(affine.values()) == {6.0}
    assert set(cross.values()) == {6.0}


def test_cross_attention_shuffle_preserves_source_blocks() -> None:
    permutation = spatial_shuffle_permutation("crossattn1", 100)
    assert sorted(permutation[:100]) == list(range(100))
    assert sorted(permutation[100:]) == list(range(100, 200))
    assert [value - 100 for value in permutation[100:]] == permutation[:100]


def test_registered_vda16_and_fixed9_use_singleton_carrier_regions() -> None:
    for task, active_count in (("vda16", 16), ("vda_fixed9", 9)):
        protocol, regions = evaluation_protocol(task, 4, 4)
        assert protocol.active_count == active_count
        assert protocol.invalid_change_index == 15
        assert protocol.control_index == 3
        assert regions == tuple((index,) for index in range(16))


def test_fixed9_conditioned_active_set_is_reproducible_and_keeps_targets_visible() -> None:
    first = conditioned_active_locations(
        "vda_fixed9", 0, 1, 15, required_active_locations=(15, 3), seed=90210
    )
    second = conditioned_active_locations(
        "vda_fixed9", 0, 1, 15, required_active_locations=(15, 3), seed=90210
    )
    assert first == second
    assert len(first) == 9
    assert len(set(first)) == 9
    assert {0, 3, 15}.issubset(first)


def test_endpoint_parser_requires_seed_bound_registered_task() -> None:
    parser = build_parser()
    endpoint = parser.parse_args([
        "--label", "fixed9", "--task", "vda_fixed9", "--expected-seed", "0",
        "--checkpoint", "final.pt", "--expected-sha256", "b" * 64, "--output-root", "out",
    ])
    assert endpoint.task == "vda_fixed9"
    assert endpoint.expected_seed == 0


def test_fixed9_psychometrics_routes_every_batch_through_conditioned_task_protocol() -> None:
    protocol, _ = evaluation_protocol("vda_fixed9", 4, 4)

    class Core:
        def __init__(self) -> None:
            self.calls = []

        def make_video_batch(self, task, cue, validity, color, change_true, change_index,
                             magnitude, *, B, seed, required_active_locations):
            self.calls.append((task, cue, change_true, change_index, B, required_active_locations))
            return {"batch": B}

        @staticmethod
        def press_times_clamp(model, task, cue, validity, color, change_true, change_index,
                              magnitude, *, videos):
            return [-1] * videos["batch"]

    core = Core()
    payload = compute_psychometrics(object(), core, 2, protocol)
    assert payload["response_rate"].shape == (4, 10, 2)
    assert len(core.calls) == 84
    assert all(call[0] == "vda_fixed9" for call in core.calls)
    assert all(call[-1] == (15, 3) for call in core.calls)
    assert {call[3] for call in core.calls} == {0, 15}
