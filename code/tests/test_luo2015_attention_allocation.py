from __future__ import annotations

import numpy as np
import pytest

from analysis.luo2015_attention_allocation import (
    phase_contrasts,
    quadrant_indices,
    query_averaged_source_mass,
    query_quadrant_routing,
    summarize_contrasts,
)


def test_quadrant_indices_partition_dense_grid_in_row_major_order():
    regions = quadrant_indices(20, 20)
    assert len(regions) == 4
    assert all(len(region) == 100 for region in regions)
    assert regions[0][0] == 0
    assert regions[0][-1] == 189
    assert regions[3][0] == 210
    assert regions[3][-1] == 399
    assert sorted(index for region in regions for index in region) == list(range(400))


def test_query_averaged_source_mass_preserves_joint_softmax_mass():
    n = 4
    raw = np.full((2, 7, n, 2 * n), 1.0 / (2 * n), dtype=np.float64)
    source = query_averaged_source_mass(raw, n)
    assert source.shape == (2, 7, 2, n)
    np.testing.assert_allclose(source.sum(axis=(-2, -1)), 1.0)
    np.testing.assert_allclose(source[..., 0, :], 1.0 / (2 * n))
    np.testing.assert_allclose(source[..., 1, :], 1.0 / (2 * n))


def test_query_averaged_source_mass_rejects_wrong_key_count():
    with pytest.raises(ValueError, match="expected 8 keys"):
        query_averaged_source_mass(np.ones((1, 4, 7)), 4)


def test_query_quadrant_routing_tracks_same_location_visual_and_memory_keys():
    n = 4
    raw = np.zeros((1, n, 2 * n), dtype=np.float64)
    # Query 0 routes 25% to its visual key and 75% to its memory key.
    raw[0, 0, 0] = 0.25
    raw[0, 0, n + 0] = 0.75
    # Remaining query rows route uniformly so every row is normalized.
    raw[0, 1:, :] = 1.0 / (2 * n)
    routing = query_quadrant_routing(raw, 2, 2)
    assert routing.shape == (1, 4, 2, 4)
    assert routing[0, 0, 0, 0] == pytest.approx(0.25)
    assert routing[0, 0, 1, 0] == pytest.approx(0.75)
    np.testing.assert_allclose(routing.sum(axis=(-2, -1)), 1.0)


def test_phase_contrasts_identify_sample_test_and_second_test_allocation():
    # One no-change trial, 2x2 native grid. Visual and memory are already paired
    # in combined mass; make the attended spatial location explicit by phase.
    source = np.full((1, 7, 2, 4), 1.0 / 8.0, dtype=np.float64)
    # Sample frames favor both stimulus quadrants (0 and 3) over blanks (1 and 2).
    source[:, 0:2, :, :] = 0.0
    source[:, 0:2, :, 0] = 0.25
    source[:, 0:2, :, 3] = 0.25
    # First test at quadrant 3 and second test at the same quadrant.
    source[:, 3:5, :, :] = 0.0
    source[:, 3:5, :, 3] = 0.5
    source[:, 5, :, :] = 1.0 / 8.0
    source[:, 6, :, :] = 0.0
    source[:, 6, :, 3] = 0.5

    routing = np.full((1, 7, 4, 2, 4), 1.0 / 8.0, dtype=np.float64)
    routing[:, 3:5, 3, 1, :] = 0.0
    routing[:, 3:5, 3, 1, 3] = 0.5
    routing[:, 3:5, 3, 0, :] = 0.0
    routing[:, 3:5, 3, 0, 3] = 0.5
    routing[:, 6, 3, 1, :] = 0.0
    routing[:, 6, 3, 1, 3] = 0.5
    routing[:, 6, 3, 0, :] = 0.0
    routing[:, 6, 3, 0, 3] = 0.5

    result = phase_contrasts(
        source,
        routing,
        test_locations=np.asarray([3]),
        change_status=np.asarray([0]),
        grid_rows=2,
        grid_cols=2,
    )
    assert result["sample_stimulus_minus_blank_combined"][0] == pytest.approx(0.5)
    assert result["first_test_target_minus_other_combined"][0] == pytest.approx(1.0)
    assert result["second_test_target_minus_other_combined"][0] == pytest.approx(1.0)
    assert result["second_test_return_from_gap_combined"][0] == pytest.approx(0.75)
    assert result["first_test_query_same_minus_other_memory"][0] == pytest.approx(0.5)
    assert result["first_test_t3_query_same_minus_other_combined"][0] == pytest.approx(1.0)
    assert result["first_test_t4_query_same_minus_other_combined"][0] == pytest.approx(1.0)
    assert result["second_test_query_same_minus_other_memory"][0] == pytest.approx(0.5)
    assert result["second_test_query_same_minus_other_combined"][0] == pytest.approx(1.0)


def test_summarize_contrasts_ignores_nan_and_is_deterministic():
    contrasts = {
        "positive": np.asarray([0.1, 0.2, 0.3, np.nan]),
        "negative": np.asarray([-0.3, -0.2, -0.1, np.nan]),
    }
    first = summarize_contrasts(contrasts, bootstrap_draws=1000, seed=17)
    second = summarize_contrasts(contrasts, bootstrap_draws=1000, seed=17)
    assert first == second
    assert first["positive"]["n"] == 3
    assert first["positive"]["mean"] == pytest.approx(0.2)
    assert first["positive"]["ci95_low"] > 0.0
    assert first["positive"]["direction"] == "positive"
    assert first["negative"]["ci95_high"] < 0.0
    assert first["negative"]["direction"] == "negative"
