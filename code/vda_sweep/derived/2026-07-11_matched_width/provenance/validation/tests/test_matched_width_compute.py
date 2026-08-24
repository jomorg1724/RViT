from __future__ import annotations

import numpy as np
import pytest

from vda_sweep import matched_width as M
from vda_sweep import matched_width_compute as C


def test_press_histogram_preserves_no_response_and_every_frame():
    press = np.asarray([-1, 0, 1, 2, 3, 4, 5, 6, 5])
    np.testing.assert_array_equal(C.press_histogram(press), [1, 1, 1, 1, 1, 1, 2, 1])
    with pytest.raises(ValueError, match="press times"):
        C.press_histogram(np.asarray([-2, 5]))


def test_decoder_design_is_replayable_and_conditions_location_on_change():
    first = C.decoder_design("vda4")
    second = C.decoder_design("vda4")
    for name in M.SAMPLE_LABELS:
        np.testing.assert_array_equal(first["labels"][name], second["labels"][name])
        np.testing.assert_array_equal(first["fold_ids"][name], second["fold_ids"][name])
    changed = first["labels"]["change"] == 1
    assert np.all(first["fold_ids"]["change_location"][~changed] == -1)
    assert np.all(first["fold_ids"]["cued_change"][~changed] == -1)
    assert set(first["fold_ids"]["change_location"][changed]) == {0, 1, 2, 3}

    singleton = C.decoder_design("vda1")
    assert np.all(singleton["fold_ids"]["change_location"] == -1)
    assert np.all(singleton["fold_ids"]["cued_change"] == -1)


def test_decode_timecourses_supports_native_and_fixed_128d_sensitivity():
    rng = np.random.default_rng(41)
    n, timesteps, tokens, width = 240, 7, 2, 128
    labels = np.resize(np.arange(2), n)
    rng.shuffle(labels)
    cells = rng.normal(size=(n, timesteps, tokens, width))
    cells[:, :, 0, 0] += labels[:, None] * 6.0
    fold_ids = C.stratified_fold_ids(labels, np.ones(n, dtype=bool), seed=17)

    native = C.decode_timecourses(cells, labels, fold_ids, matched_dimensions=None)
    matched = C.decode_timecourses(cells, labels, fold_ids, matched_dimensions=128)
    assert native.shape == matched.shape == (7,)
    assert np.isfinite(native).all() and np.isfinite(matched).all()
    assert np.all((0 <= native) & (native <= 1))
    assert np.all((0 <= matched) & (matched <= 1))
    assert native[-1] > 0.75
    assert matched[-1] > 0.75
