from __future__ import annotations

import numpy as np
import pytest


def test_vda_source_task_inventory_is_complete_and_unique():
    from vda_series.task_figures import VDA_TASK_ORDER

    assert VDA_TASK_ORDER == (
        "validity4",
        "vda1",
        "vda2",
        "vda4",
        "vda9",
        "vda16",
        "vda_excl",
        "vda_fixed1",
        "vda_fixed2",
        "vda_fixed4",
        "vda_fixed9",
        "vda_fixed16",
        "vda_probe_cued",
        "vda_probe_uncued",
    )
    assert len(VDA_TASK_ORDER) == len(set(VDA_TASK_ORDER))


@pytest.mark.parametrize(
    ("task", "grid", "tokens", "active", "mode"),
    [
        ("validity4", (2, 2), 4, 4, "archived_including_cue"),
        ("vda1", (2, 2), 4, 1, "degenerate_singleton"),
        ("vda2", (2, 2), 4, 2, "exact_excluding_cue"),
        ("vda4", (2, 2), 4, 4, "archived_including_cue"),
        ("vda9", (3, 3), 9, 9, "archived_including_cue"),
        ("vda16", (4, 4), 16, 16, "exact_excluding_cue"),
        ("vda_excl", (1, 2), 2, 2, "exclusion_target_only"),
        ("vda_fixed1", (4, 4), 16, 1, "degenerate_singleton"),
        ("vda_fixed2", (4, 4), 16, 2, "exact_excluding_cue"),
        ("vda_fixed4", (4, 4), 16, 4, "exact_excluding_cue"),
        ("vda_fixed9", (4, 4), 16, 9, "exact_excluding_cue"),
        ("vda_fixed16", (4, 4), 16, 16, "exact_excluding_cue"),
        ("vda_probe_cued", (2, 2), 4, 4, "archived_including_cue"),
        ("vda_probe_uncued", (2, 2), 4, 4, "archived_including_cue"),
    ],
)
def test_task_specs_preserve_historical_and_controlled_semantics(task, grid, tokens, active, mode):
    from vda_series.task_figures import task_spec

    spec = task_spec(task)
    assert spec.grid == grid
    assert spec.token_count == tokens
    assert spec.active_count == active
    assert spec.validity_mode == mode


def test_archived_vda4_distribution_preserves_including_cue_semantics():
    from vda_series.task_figures import realized_target_distribution, task_spec

    distribution = realized_target_distribution(
        task_spec("vda4"), cue_index=0, displayed_validity=0.25, active_indices=(0, 1, 2, 3)
    )
    np.testing.assert_allclose(distribution, [0.4375, 0.1875, 0.1875, 0.1875])


def test_archived_vda9_distribution_preserves_including_cue_semantics():
    from vda_series.task_figures import realized_target_distribution, task_spec

    distribution = realized_target_distribution(
        task_spec("vda9"), cue_index=0, displayed_validity=0.25, active_indices=tuple(range(9))
    )
    expected = np.full(9, 0.75 / 9)
    expected[0] += 0.25
    np.testing.assert_allclose(distribution, expected)


def test_current_vda16_distribution_uses_exact_excluding_cue_semantics():
    from vda_series.task_figures import realized_target_distribution, task_spec

    spec = task_spec("vda16")
    distribution = realized_target_distribution(
        spec, cue_index=0, displayed_validity=0.25, active_indices=tuple(range(16))
    )
    expected = np.full(16, 0.75 / 15)
    expected[0] = 0.25
    np.testing.assert_allclose(distribution, expected)
    assert spec.lineage == "current"


def test_controlled_fixed16_distribution_is_exact():
    from vda_series.task_figures import realized_target_distribution, task_spec

    distribution = realized_target_distribution(
        task_spec("vda_fixed16"), cue_index=0, displayed_validity=0.25, active_indices=tuple(range(16))
    )
    expected = np.full(16, 0.75 / 15)
    expected[0] = 0.25
    np.testing.assert_allclose(distribution, expected)


def test_singleton_distribution_is_declared_degenerate():
    from vda_series.task_figures import realized_target_distribution, task_spec

    for task in ("vda1", "vda_fixed1"):
        distribution = realized_target_distribution(
            task_spec(task), cue_index=0, displayed_validity=0.25, active_indices=(0,)
        )
        np.testing.assert_allclose(distribution, [1.0, 0.0, 0.0, 0.0] if task == "vda1" else [1.0] + [0.0] * 15)


def test_distribution_rejects_invalid_active_or_cue_configuration():
    from vda_series.task_figures import realized_target_distribution, task_spec

    with pytest.raises(ValueError, match="cue_index must be active"):
        realized_target_distribution(task_spec("vda_fixed4"), 0, 0.5, (1, 2, 3, 4))
    with pytest.raises(ValueError, match="active_indices"):
        realized_target_distribution(task_spec("vda_fixed4"), 0, 0.5, (0, 1, 2))
    with pytest.raises(ValueError, match="displayed_validity"):
        realized_target_distribution(task_spec("vda_fixed4"), 0, 1.1, (0, 1, 2, 3))


def test_rendered_timeline_has_seven_frames_and_fixed16_geometry():
    from vda_series.task_figures import render_timeline_frames, task_spec

    frames = render_timeline_frames(task_spec("vda_fixed16"), seed=7, change=True)
    assert len(frames) == 7
    assert all(frame.shape == (100, 100, 3) for frame in frames)
    assert all(np.isfinite(frame).all() for frame in frames)
    assert np.count_nonzero(frames[0]) == 0
    assert np.count_nonzero(frames[1]) > 0
    assert np.count_nonzero(frames[3]) > 0


def test_cue_configurations_encode_all_four_source_validities():
    from vda_series.task_figures import render_cue_frame, task_spec

    spec = task_spec("vda4")
    frames = [
        render_cue_frame(spec, cue_index=0, displayed_validity=value)
        for value in (0.25, 0.5, 0.75, 1.0)
    ]
    assert all(frame.shape == (50, 50, 3) for frame in frames)
    assert len({frame.tobytes() for frame in frames}) == 4
    nonzero = [np.count_nonzero(frame) for frame in frames]
    assert nonzero == sorted(nonzero)


def test_realized_cue_probability_curve_exposes_archived_semantics():
    from vda_series.task_figures import realized_cue_probability_curve, task_spec

    displayed, realized = realized_cue_probability_curve(
        task_spec("vda4"), cue_index=0, active_indices=(0, 1, 2, 3)
    )
    np.testing.assert_allclose(displayed, [0.25, 0.5, 0.75, 1.0])
    np.testing.assert_allclose(realized, [0.4375, 0.625, 0.8125, 1.0])


def test_probe_schematics_place_the_probe_in_the_delay_frame():
    from vda_series.task_figures import render_timeline_frames, task_spec

    ordinary = render_timeline_frames(task_spec("vda4"), seed=7, change=True)
    cued = render_timeline_frames(task_spec("vda_probe_cued"), seed=7, change=True)
    uncued = render_timeline_frames(task_spec("vda_probe_uncued"), seed=7, change=True)
    assert np.count_nonzero(ordinary[2]) == 0
    assert np.count_nonzero(cued[2]) > 0
    assert np.count_nonzero(uncued[2]) > 0
    assert not np.array_equal(cued[2], uncued[2])


def test_figure_builder_exports_vector_raster_and_metadata(tmp_path):
    from vda_series.task_figures import build_m1_task_figure

    outputs = build_m1_task_figure("vda_fixed4", tmp_path, seed=11)
    assert outputs.pdf.is_file()
    assert outputs.png.is_file()
    assert outputs.metadata.is_file()
    assert outputs.pdf.stat().st_size > 10_000
    assert outputs.png.stat().st_size > 50_000
