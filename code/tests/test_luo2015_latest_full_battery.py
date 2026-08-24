from __future__ import annotations

import numpy as np


def test_exact_magnitude_bank_is_sign_and_location_balanced() -> None:
    from experiments.luo2015_episodic.evaluate_latest_full_battery import exact_magnitude_trial_bank

    bank = exact_magnitude_trial_bank(
        magnitude=20.0, trials_per_sign_per_location=25, seed=123,
        sensory_noise_sd=5.0, second_test_magnitude=65.0,
    )
    assert bank["videos"].shape == (100, 7, 3, 50, 50)
    assert sorted(np.unique(bank["locations"]).tolist()) == [0, 3]
    assert sorted(np.unique(bank["signs"]).tolist()) == [-1, 1]
    for loc in (0, 3):
        for sign in (-1, 1):
            mask = (bank["locations"] == loc) & (bank["signs"] == sign)
            assert int(mask.sum()) == 25
            assert np.allclose(bank["signed_deltas"][mask], sign * 20.0)
    assert np.all((bank["sample_orientations"] >= 0.0) & (bank["sample_orientations"] < 180.0))
    assert np.ptp(bank["sample_orientations"][:, 0]) > 100.0
    assert np.ptp(bank["sample_orientations"][:, 1]) > 100.0


def test_no_change_bank_uses_easy_balanced_second_test() -> None:
    from experiments.luo2015_episodic.evaluate_latest_full_battery import exact_no_change_bank

    bank = exact_no_change_bank(
        trials_per_sign_per_location=20, seed=456,
        sensory_noise_sd=5.0, second_test_magnitude=65.0,
    )
    assert bank["videos"].shape == (80, 7, 3, 50, 50)
    assert np.all(np.abs(bank["second_test_signed_deltas"]) == 65.0)
    for loc in (0, 3):
        for sign in (-1, 1):
            assert int(((bank["locations"] == loc) & (bank["signs"] == sign)).sum()) == 20


def test_counterphased_did_uses_both_reward_locations() -> None:
    from experiments.luo2015_episodic.evaluate_latest_full_battery import counterphased_did

    summaries = [
        {"session": "sensitivity", "condition_loc": 0,
         "locations": {"0": {"dprime": 2.0, "criterion": 0.1}, "3": {"dprime": 1.0, "criterion": 0.0}}},
        {"session": "sensitivity", "condition_loc": 3,
         "locations": {"0": {"dprime": 1.1, "criterion": 0.0}, "3": {"dprime": 2.1, "criterion": 0.1}}},
        {"session": "criterion", "condition_loc": 0,
         "locations": {"0": {"dprime": 1.5, "criterion": -0.7}, "3": {"dprime": 1.5, "criterion": 0.2}}},
        {"session": "criterion", "condition_loc": 3,
         "locations": {"0": {"dprime": 1.4, "criterion": 0.3}, "3": {"dprime": 1.4, "criterion": -0.8}}},
    ]
    assert np.isclose(counterphased_did(summaries, "sensitivity", "dprime"), 1.0)
    assert np.isclose(counterphased_did(summaries, "criterion", "criterion"), -1.0)


def test_primary_and_noise_ablation_preserve_sampled_policy_semantics() -> None:
    from experiments.luo2015_episodic.evaluate_latest_full_battery import evaluation_conditions

    assert evaluation_conditions() == {
        "trained_noise": {"inject_memory_noise": True, "sample_actions": True},
        "zero_mnemonic_noise": {"inject_memory_noise": False, "sample_actions": True},
    }
