from __future__ import annotations

from pathlib import Path

import numpy as np

from analysis.vda4_spatial_attention_measures import (
    common_quadrant_metrics,
    discover_sources,
    load_source,
    patch_column_scores,
    quadrant_indices,
    source_patch_column_scores,
    source_quadrant_metrics,
    source_mean_rows_for_source,
    summarize_paired_grid_contrasts,
    trial_rows_for_source,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = (
    ROOT
    / "reports"
    / "vda_series"
    / "spatial_scaling_evaluation_production_20260727"
)


def test_quadrants_partition_every_supported_native_grid() -> None:
    for side in (2, 4, 10):
        regions = quadrant_indices(side, side)
        assert len(regions) == 4
        assert {len(region) for region in regions} == {side * side // 4}
        assert sorted(token for region in regions for token in region) == list(range(side * side))


def test_patch_score_is_column_mean_and_pairs_cross_attention_sources() -> None:
    # Two queries, two spatial positions, with visual columns followed by memory columns.
    raw = np.asarray(
        [
            [0.10, 0.20, 0.30, 0.40],
            [0.20, 0.10, 0.40, 0.30],
        ],
        dtype=np.float64,
    )
    scores = patch_column_scores(raw, n_tokens=2)
    # Position 0 receives mean([.1+.3, .2+.4])=.5; position 1 likewise.
    np.testing.assert_allclose(scores, [0.5, 0.5])


def test_cross_attention_sources_are_split_before_spatial_reduction() -> None:
    # Visual and memory peaks are intentionally placed at different positions.
    raw = np.asarray(
        [
            [0.35, 0.05, 0.10, 0.50],
            [0.25, 0.05, 0.20, 0.50],
        ],
        dtype=np.float64,
    )
    scores = source_patch_column_scores(raw, n_tokens=2)
    np.testing.assert_allclose(scores["visual"], [0.30, 0.05])
    np.testing.assert_allclose(scores["memory"], [0.15, 0.50])
    assert np.isclose(scores["visual"].sum(), 0.35)
    assert np.isclose(scores["memory"].sum(), 0.65)
    # Verify reconstruction without changing the distinct source peak locations.
    normalized = raw / raw.sum(axis=-1, keepdims=True)
    split = source_patch_column_scores(normalized, n_tokens=2)
    combined = patch_column_scores(normalized, n_tokens=2)
    np.testing.assert_allclose(split["visual"] + split["memory"], combined)
    assert int(np.argmax(split["visual"])) == 0
    assert int(np.argmax(split["memory"])) == 1


def test_uniform_cross_attention_preserves_half_mass_per_source() -> None:
    for n_tokens in (4, 16, 100):
        raw = np.full((3, n_tokens, 2 * n_tokens), 1.0 / (2 * n_tokens))
        split = source_patch_column_scores(raw, n_tokens)
        for score in split.values():
            np.testing.assert_allclose(score, 1.0 / (2 * n_tokens))
            np.testing.assert_allclose(score.sum(axis=-1), 0.5)
        combined = split["visual"] + split["memory"]
        np.testing.assert_allclose(combined, 1.0 / n_tokens)


def test_source_quadrant_metrics_keep_raw_share_and_source_peak_baseline() -> None:
    regions = quadrant_indices(4, 4)
    uniform_source = np.full((2, 16), 1.0 / 32.0)
    metrics = source_quadrant_metrics(uniform_source, regions)
    np.testing.assert_allclose(metrics["source_total_share"], 0.5)
    np.testing.assert_allclose(metrics["raw_total_quadrant_mass"], 0.125)
    np.testing.assert_allclose(metrics["raw_peak_patch"], 1.0 / 32.0)
    np.testing.assert_allclose(metrics["raw_peak_patch_uniform_ratio"], 1.0)
    np.testing.assert_allclose(metrics["conditional_total_quadrant_mass"], 0.25)


def test_common_quadrant_metrics_have_named_uniform_baselines() -> None:
    regions = quadrant_indices(4, 4)
    uniform = np.full((3, 16), 1.0 / 16.0)
    metrics = common_quadrant_metrics(uniform, regions)
    np.testing.assert_allclose(metrics["total_quadrant_mass"], 0.25)
    np.testing.assert_allclose(metrics["peak_patch_raw"], 1.0 / 16.0)
    np.testing.assert_allclose(metrics["peak_patch_uniform_ratio"], 1.0)
    np.testing.assert_allclose(metrics["peak_patch_quadrant_share"], 0.25)
    np.testing.assert_allclose(metrics["within_quadrant_peak_ratio"], 1.0)


def test_peak_patch_measure_is_not_total_quadrant_mass() -> None:
    regions = quadrant_indices(4, 4)
    scores = np.full((16,), 0.01)
    scores[list(regions[0])] = [0.50, 0.10, 0.05, 0.05]
    scores[list(regions[1])] = [0.05, 0.05, 0.02, 0.02]
    scores[list(regions[2])] = [0.03, 0.03, 0.02, 0.02]
    scores[list(regions[3])] = [0.03, 0.01, 0.01, 0.01]
    scores /= scores.sum()
    metrics = common_quadrant_metrics(scores, regions)
    assert metrics["total_quadrant_mass"][0] != metrics["peak_patch_raw"][0]
    assert metrics["peak_patch_quadrant_share"][0] > metrics["total_quadrant_mass"][0]
    assert metrics["within_quadrant_peak_ratio"][0] > 1.0


def test_admitted_caches_reconstruct_and_retain_framewise_sign_change() -> None:
    sources = discover_sources(SOURCE_ROOT)
    assert len(sources) == 8
    source = next(source for source in sources if source.label == "vda4_crossattn1_grid2x2_seed0")
    payload = load_source(source)
    metrics = common_quadrant_metrics(payload["token_mass"], quadrant_indices(2, 2))
    invalid_total = metrics["total_quadrant_mass"][1]
    frame5 = float((invalid_total[:, 5, 3] - invalid_total[:, 5, 0]).mean())
    frame6 = float((invalid_total[:, 6, 3] - invalid_total[:, 6, 0]).mean())
    assert frame5 < 0.0
    assert frame6 > 0.0


def test_source_decomposition_separates_share_from_conditional_localization() -> None:
    sources = discover_sources(SOURCE_ROOT)
    source = next(source for source in sources if source.label == "vda4_crossattn1_grid10x10_seed0")
    rows = source_mean_rows_for_source(source, load_source(source))
    frame5_valid = [
        row for row in rows if row["condition"] == "valid" and row["window"] == "frame5"
    ]
    assert {row["source"] for row in frame5_valid} == {"visual", "memory"}
    assert np.isclose(sum(float(row["source_total_share"]) for row in frame5_valid), 1.0, atol=2e-5)
    for row in frame5_valid:
        assert 0.0 <= float(row["target_conditional_total_mass"]) <= 1.0
        assert row["estimation_unit"] == "trial-averaged raw attention; descriptive mean only"


def test_paired_grid_contrasts_use_all_common_trial_ids() -> None:
    sources = discover_sources(SOURCE_ROOT)
    selected = [
        source
        for source in sources
        if source.feedback == "crossattn1" and source.seed == 0 and source.n_tokens in (4, 100)
    ]
    trial_rows = []
    for source in selected:
        rows, _ = trial_rows_for_source(source, load_source(source))
        trial_rows.extend(rows)
    contrasts = summarize_paired_grid_contrasts(trial_rows)
    match = next(
        row
        for row in contrasts
        if row["condition"] == "invalid"
        and row["window"] == "frame5"
        and row["from_n_tokens"] == 4
        and row["to_n_tokens"] == 100
        and row["metric"] == "target_minus_cue_total_mass"
    )
    assert match["n_paired_trials"] == 128
    assert np.isfinite(float(match["mean_difference"]))
