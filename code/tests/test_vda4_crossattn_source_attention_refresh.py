from __future__ import annotations

import numpy as np
import pytest

from analysis.vda4_crossattn_source_attention_refresh import (
    combined_location_mass,
    query_averaged_source_mass,
    source_quadrant_statistics,
)


@pytest.mark.parametrize("n_tokens", [4, 16, 100])
def test_uniform_cross_attention_preserves_global_source_mass_and_shapes(
    n_tokens: int,
) -> None:
    raw = np.full((3, 7, n_tokens, 2 * n_tokens), 1.0 / (2 * n_tokens))
    source = query_averaged_source_mass(raw, n_tokens)
    assert source.shape == (3, 7, 2, n_tokens)
    np.testing.assert_allclose(source, 1.0 / (2 * n_tokens))
    np.testing.assert_allclose(source.sum(axis=-1), 0.5)
    combined = combined_location_mass(source)
    assert combined.shape == (3, 7, n_tokens)
    np.testing.assert_allclose(combined, 1.0 / n_tokens)

    side = int(round(np.sqrt(n_tokens)))
    total, peak = source_quadrant_statistics(source, side, side)
    assert total.shape == (3, 7, 2, 4)
    assert peak.shape == (3, 7, 2, 4)
    np.testing.assert_allclose(total, 0.125)
    np.testing.assert_allclose(peak, 1.0 / (2 * n_tokens))


@pytest.mark.parametrize("n_tokens", [4, 16, 100])
def test_source_sum_reconstructs_direct_paired_location_mass(n_tokens: int) -> None:
    rng = np.random.default_rng(1000 + n_tokens)
    logits = rng.normal(size=(5, 7, n_tokens, 2 * n_tokens))
    logits -= logits.max(axis=-1, keepdims=True)
    raw = np.exp(logits)
    raw /= raw.sum(axis=-1, keepdims=True)
    source = query_averaged_source_mass(raw, n_tokens)
    rebuilt = combined_location_mass(source)
    direct = (raw[..., :n_tokens] + raw[..., n_tokens:]).mean(axis=-2)
    np.testing.assert_allclose(rebuilt, direct, rtol=1e-12, atol=1e-12)


def test_source_maxima_are_not_replaced_by_maximum_after_source_sum() -> None:
    # Every query has the same joint-softmax row. Visual peaks at patch 0,
    # memory peaks at patch 1, and only their sum peaks at patch 2.
    visual = np.asarray([0.25, 0.00, 0.18, 0.00])
    memory = np.asarray([0.00, 0.24, 0.18, 0.15])
    row = np.concatenate([visual, memory])
    np.testing.assert_allclose(row.sum(), 1.0)
    raw = np.repeat(row[None, :], 4, axis=0)
    source = query_averaged_source_mass(raw, n_tokens=4)
    combined = combined_location_mass(source)
    assert int(np.argmax(source[0])) == 0
    assert int(np.argmax(source[1])) == 1
    assert int(np.argmax(combined)) == 2
    assert float(np.max(combined)) != float(np.max(source[0]))
    assert float(np.max(combined)) != float(np.max(source[1]))


@pytest.mark.parametrize(
    ("n_tokens", "expected_source", "expected_quadrant"),
    [
        (4, (2, 128, 7, 2, 4), (2, 128, 7, 2, 4)),
        (16, (2, 128, 7, 2, 16), (2, 128, 7, 2, 4)),
        (100, (2, 128, 7, 2, 100), (2, 128, 7, 2, 4)),
    ],
)
def test_full_refresh_array_contracts(
    n_tokens: int,
    expected_source: tuple[int, ...],
    expected_quadrant: tuple[int, ...],
) -> None:
    raw = np.full(
        (2, 128, 7, n_tokens, 2 * n_tokens),
        1.0 / (2 * n_tokens),
        dtype=np.float32,
    )
    source = query_averaged_source_mass(raw, n_tokens)
    assert source.shape == expected_source
    side = int(round(np.sqrt(n_tokens)))
    total, peak = source_quadrant_statistics(source, side, side)
    assert total.shape == expected_quadrant
    assert peak.shape == expected_quadrant
