from __future__ import annotations

import numpy as np
import pytest

from analysis.luo2015_scientific_assay import (
    build_regional_clamp,
    first_press,
    intervention_location,
    make_trials,
    paired_bootstrap_difference,
    regional_source_mass,
    sample_phase_clamp,
    wilson_interval,
)


def test_regional_clamp_covers_visual_and_memory_keys_for_dense_quadrant() -> None:
    clamp = build_regional_clamp(20, 20, location=0, bias=-6.0, source="both")
    keys = set(map(int, clamp))
    assert len(keys) == 200
    assert 0 in keys and 189 in keys
    assert 400 in keys and 589 in keys
    assert 210 not in keys and 610 not in keys
    assert set(clamp.values()) == {-6.0}


def test_regional_clamp_can_target_visual_or_memory_source_only() -> None:
    visual = build_regional_clamp(2, 2, location=3, bias=-4.0, source="visual")
    memory = build_regional_clamp(2, 2, location=3, bias=-4.0, source="memory")
    assert visual == {"3": -4.0}
    assert memory == {"7": -4.0}


def test_intervention_locations_are_equal_area_spatial_controls() -> None:
    assert intervention_location(0, "tested_sample") == 0
    assert intervention_location(0, "other_sample") == 3
    assert intervention_location(0, "blank_control") == 1
    assert intervention_location(3, "tested_sample") == 3
    assert intervention_location(3, "other_sample") == 0
    assert intervention_location(3, "blank_control") == 2
    with pytest.raises(ValueError, match="unknown intervention role"):
        intervention_location(0, "bad")


def test_assay_trial_bank_samples_full_domain_independent_of_theta() -> None:
    from envs.luo2015 import LuoMaunsell2015Env

    env = LuoMaunsell2015Env(theta=35.0, noise_multiplier=0.0)
    _, low_meta, _ = make_trials(
        env, theta=10.0, changed=1, count=128, magnitude=None, seed=817,
    )
    _, high_meta, _ = make_trials(
        env, theta=40.0, changed=1, count=128, magnitude=None, seed=817,
    )

    for name in ("sample_orientation0", "sample_orientation3"):
        assert np.all((0.0 <= low_meta[name]) & (low_meta[name] < 180.0))
        np.testing.assert_array_equal(low_meta[name], high_meta[name])
        assert np.unique(low_meta[name]).size == 128
    np.testing.assert_allclose(high_meta["signed_change"], 4.0 * low_meta["signed_change"])


def test_sample_phase_clamp_is_gated_to_both_sample_frames_only() -> None:
    clamp = {"0": -6.0}
    assert sample_phase_clamp(0, clamp) is clamp
    assert sample_phase_clamp(1, clamp) is clamp
    for frame in range(2, 7):
        assert sample_phase_clamp(frame, clamp) is None


def test_regional_source_mass_sums_sources_and_every_token_in_quadrant() -> None:
    source = np.full((2, 7, 2, 4), 1.0 / 8.0)
    locations = np.asarray([0, 3])
    mass = regional_source_mass(source, 2, 2, locations, frames=(0, 1))
    np.testing.assert_allclose(mass, np.asarray([0.25, 0.25]))


def test_first_press_uses_first_declare_action() -> None:
    actions = np.asarray([[0, 0, 1, 1], [0, 0, 0, 0], [1, 0, 1, 0]])
    np.testing.assert_array_equal(first_press(actions), np.asarray([2, -1, 0]))


def test_wilson_interval_is_bounded_and_contains_observed_rate() -> None:
    low, high = wilson_interval(8, 10)
    assert 0.0 <= low < 0.8 < high <= 1.0


def test_paired_bootstrap_difference_is_deterministic_and_directional() -> None:
    natural = np.asarray([0.0, 1.0, 1.0, 1.0])
    inhibited = np.asarray([0.0, 0.0, 1.0, 0.0])
    first = paired_bootstrap_difference(natural, inhibited, draws=2000, seed=9)
    second = paired_bootstrap_difference(natural, inhibited, draws=2000, seed=9)
    assert first == second
    assert first["mean_inhibited_minus_natural"] == pytest.approx(-0.5)
    assert first["ci95_high"] <= 0.0
    assert first["discordant_pairs"] == 2


def test_paired_no_discordance_reports_nonzero_exact_uncertainty_bound() -> None:
    values = np.asarray([0.0, 1.0] * 352)
    result = paired_bootstrap_difference(values, values, draws=100, seed=1)
    assert result["ci95_low"] == 0.0
    assert result["ci95_high"] == 0.0
    assert result["discordant_pairs"] == 0
    assert result["no_discordance_abs_bound_95"] == pytest.approx(0.005226181334430091)
