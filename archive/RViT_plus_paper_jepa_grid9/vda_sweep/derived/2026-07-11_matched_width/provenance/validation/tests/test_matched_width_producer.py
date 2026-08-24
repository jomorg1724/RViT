from __future__ import annotations

import numpy as np

from vda_sweep import matched_width as M
from vda_sweep import matched_width_producer as P


def _spec(task: str = "vda4", feedback: str = "crossattn1", width: int = 128):
    return next(
        spec for spec in M.admissible_specs()
        if (spec.task, spec.feedback, spec.width) == (task, feedback, width)
    )


def test_psychometric_payload_uses_common_seeds_and_complete_histograms(monkeypatch):
    calls = []

    def fake_press(model, spec, *, validity, change, change_index, magnitude, seed, trials):
        calls.append((validity, change, change_index, magnitude, seed, trials))
        press = np.full(trials, -1, dtype=np.int64)
        press[: trials // 2] = 5
        return press

    monkeypatch.setattr(P, "_press", fake_press)
    spec = _spec()
    result = P.psychometric_payload(object(), spec)

    assert result["psychometric_press_histogram_valid"].shape == (4, 10, 8)
    assert np.all(result["psychometric_press_histogram_valid"].sum(axis=-1) == 300)
    assert np.all(result["psychometric_press_histogram_invalid"].sum(axis=-1) == 300)
    assert np.all(result["psychometric_nochange_press_histogram"].sum(axis=-1) == 300)
    assert np.all(result["psychometric_response_count_valid"] == 150)
    assert np.all(result["psychometric_response_count_invalid"] == 150)

    changed = [call for call in calls if call[1] == 1]
    for validity in M.DISPLAYED_VALIDITIES:
        at_validity = [call for call in changed if call[0] == validity]
        for magnitude in M.CHANGE_MAGNITUDES:
            pair = [call for call in at_validity if call[3] == magnitude]
            assert len(pair) == 2
            assert pair[0][4] == pair[1][4]


def test_clamp_payload_reuses_three_batches_and_runtime_token_count(monkeypatch):
    batches = []
    used = []
    clamps = []

    def fake_batch(*args, **kwargs):
        marker = object()
        batches.append(marker)
        return marker

    def fake_clamp(keys, tokens, cue, dose, *, scale):
        clamps.append((keys, tokens, cue, dose, scale))
        return {"dose": dose}

    def fake_press(*args, videos, clamp, **kwargs):
        used.append((videos, clamp["dose"]))
        press = np.full(M.CLAMP_TRIALS, -1, dtype=np.int64)
        press[:125] = 5
        press[125:175] = 1
        return press

    monkeypatch.setattr(P.core, "make_video_batch", fake_batch)
    monkeypatch.setattr(P.core, "clamp_alpha", fake_clamp)
    monkeypatch.setattr(P.core, "press_times_clamp", fake_press)
    model = type("FakeModel", (), {"n_tokens": 4})()
    result = P.clamp_payload(model, _spec())

    assert len(batches) == 3
    assert len(clamps) == len(M.CLAMP_DOSE_PARAMETERS)
    assert all(
        (keys, tokens, cue, scale) == (8, 4, 0, M.CLAMP_LOGIT_SCALE)
        for keys, tokens, cue, _, scale in clamps
    )
    assert used == [
        item
        for dose in M.CLAMP_DOSE_PARAMETERS
        for item in ((batches[0], dose), (batches[1], dose), (batches[2], dose))
    ]
    assert np.all(result["clamp_hit_count_valid"] == 125)
    assert np.all(result["clamp_hit_count_invalid"] == 125)
    assert np.all(result["clamp_false_alarm_count"] == 175)
    assert np.all(result["clamp_press_histogram_valid"].sum(axis=-1) == M.CLAMP_TRIALS)
    assert np.all(result["clamp_press_histogram_invalid"].sum(axis=-1) == M.CLAMP_TRIALS)
    assert np.all(result["clamp_press_histogram_nochange"].sum(axis=-1) == M.CLAMP_TRIALS)
    np.testing.assert_array_equal(
        result["clamp_false_alarm_count"],
        result["clamp_press_histogram_nochange"][:, 1:].sum(axis=-1),
    )
    expected_dprime, expected_criterion = M._sdt_from_counts(
        np.full(len(M.CLAMP_DOSE_PARAMETERS), 125),
        np.full(len(M.CLAMP_DOSE_PARAMETERS), 175),
        M.CLAMP_TRIALS,
    )
    np.testing.assert_allclose(result["clamp_dprime_valid"], expected_dprime)
    np.testing.assert_allclose(result["clamp_criterion_invalid"], expected_criterion)
