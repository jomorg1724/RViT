from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest


def _lineage_fields(tmp_path, task, feedback):
    import vda_series.first_wave_figures as first_wave

    checkpoint = tmp_path / f"{task}_{feedback}.pt"
    checkpoint.write_bytes(b"immutable checkpoint fixture")
    dependencies = json.dumps(
        first_wave.producer_dependency_hashes(),
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "task": np.array(task),
        "feedback": np.array(feedback),
        "checkpoint_iteration": np.array(19999),
        "checkpoint_path": np.array(str(checkpoint.resolve())),
        "checkpoint_sha256": np.array(hashlib.sha256(checkpoint.read_bytes()).hexdigest()),
        "producer_path": np.array(str(Path(first_wave.__file__).resolve())),
        "producer_sha256": np.array(hashlib.sha256(Path(first_wave.__file__).read_bytes()).hexdigest()),
        "dependency_hashes_json": np.array(dependencies),
        "runtime_versions_json": np.array(
            json.dumps(
                first_wave.producer_runtime_versions(),
                sort_keys=True,
                separators=(",", ":"),
            )
        ),
        "device": np.array("cpu"),
        "grid": np.array(first_wave.first_wave_spec(task).grid),
    }


def test_first_wave_specs_fix_historical_geometry_and_opposite_corner():
    from vda_series.first_wave_figures import first_wave_spec

    vda4 = first_wave_spec("vda4")
    assert vda4.grid == (2, 2)
    assert vda4.token_count == 4
    assert vda4.active_indices == (0, 1, 2, 3)
    assert vda4.cue_index == 0
    assert vda4.invalid_change_index == 3

    vda9 = first_wave_spec("vda9")
    assert vda9.grid == (3, 3)
    assert vda9.token_count == 9
    assert vda9.active_indices == tuple(range(9))
    assert vda9.cue_index == 0
    assert vda9.invalid_change_index == 8

    with pytest.raises(ValueError, match="first-wave task"):
        first_wave_spec("vda_fixed4")


def test_attention_condition_sweeps_cue_proportion_on_no_change_trials():
    from vda_series.first_wave_figures import attention_condition

    for task in ("vda4", "vda9"):
        condition = attention_condition(task)
        assert condition == {
            "cue_index": 0,
            "change_index": -1,
            "displayed_validities": (0.25, 0.5, 0.75, 1.0),
            "cue_color": "red",
            "change_magnitude_degrees": 0.0,
            "change_present": False,
            "change_frame": 5,
            "timesteps": 7,
        }


def test_real_no_change_stimuli_match_across_cue_proportions_except_cue_frame():
    from vda_sweep import vda_core as core

    for task in ("vda4", "vda9"):
        batches = []
        for cue_proportion in (0.25, 1.0):
            batches.append(
                core.make_video_batch(
                    task,
                    0,
                    cue_proportion,
                    "red",
                    0,
                    -1,
                    0.0,
                    B=2,
                    seed=1701,
                )
            )
        different = batches[0] != batches[1]
        assert not different[:, (0, 2, 3, 4, 5, 6)].any()
        assert different[:, 1].any()


def test_attention_reduction_note_is_feedback_specific_and_self_contained():
    from vda_series.first_wave_figures import attention_reduction_note

    assert "single spatial-key array" in attention_reduction_note("affine_ew")
    cross = attention_reduction_note("crossattn1")
    assert "image and recurrent-memory key arrays" in cross
    assert "shown separately" in cross


def test_dependency_graph_includes_executed_vda_series_package_imports():
    from vda_series.first_wave_figures import PRODUCER_DEPENDENCIES, producer_runtime_versions

    assert {
        "vda_series/__init__.py",
        "vda_series/task_figures.py",
        "vda_series/architecture_figures.py",
        "vda_series/behavior_figures.py",
    }.issubset(PRODUCER_DEPENDENCIES)
    assert {"gymnasium", "scipy", "pillow"}.issubset(producer_runtime_versions())


def test_spatial_attention_maps_preserve_query_rows_and_location_mass():
    from vda_series.first_wave_figures import spatial_attention_maps

    affine = np.arange(7 * 4 * 4, dtype=np.float64).reshape(7, 4, 4) + 1.0
    affine /= affine.sum(axis=-1, keepdims=True)
    collapsed_affine = spatial_attention_maps(affine, feedback="affine_ew")
    assert collapsed_affine.shape == (7, 4, 4)
    np.testing.assert_allclose(collapsed_affine, affine)
    np.testing.assert_allclose(collapsed_affine.sum(axis=-1), 1.0)

    image = np.full((7, 9, 9), 0.25 / 9)
    memory = np.full((7, 9, 9), 0.75 / 9)
    cross = np.concatenate([image, memory], axis=-1)
    collapsed_cross = spatial_attention_maps(cross, feedback="crossattn1")
    assert collapsed_cross.shape == (7, 9, 9)
    np.testing.assert_allclose(collapsed_cross, np.full((7, 9, 9), 1.0 / 9))
    np.testing.assert_allclose(collapsed_cross.sum(axis=-1), 1.0)

    cross_trials = np.stack([cross, cross], axis=0)
    collapsed_trials = spatial_attention_maps(cross_trials, feedback="crossattn1")
    assert collapsed_trials.shape == (2, 7, 9, 9)
    np.testing.assert_allclose(collapsed_trials.sum(axis=-1), 1.0)


def test_attention_source_maps_keep_cross_attention_image_and_memory_arrays_separate():
    from vda_series.first_wave_figures import (
        attention_source_maps,
        query_averaged_attention_maps,
    )

    image = np.full((7, 4, 4), 0.2 / 4)
    memory = np.full((7, 4, 4), 0.8 / 4)
    raw = np.concatenate([image, memory], axis=-1)

    sources = attention_source_maps(raw, feedback="crossattn1")
    assert sources.shape == (7, 4, 2, 4)
    np.testing.assert_allclose(sources[:, :, 0], image)
    np.testing.assert_allclose(sources[:, :, 1], memory)
    np.testing.assert_allclose(sources.sum(axis=(-2, -1)), 1.0)

    plotted = query_averaged_attention_maps(raw, feedback="crossattn1")
    assert plotted.shape == (7, 2, 4)
    np.testing.assert_allclose(plotted[:, 0], np.full((7, 4), 0.2 / 4))
    np.testing.assert_allclose(plotted[:, 1], np.full((7, 4), 0.8 / 4))


def test_spatial_attention_maps_reject_malformed_attention():
    from vda_series.first_wave_figures import spatial_attention_maps

    with pytest.raises(ValueError, match="shape"):
        spatial_attention_maps(np.zeros((7, 4)), feedback="affine_ew")
    with pytest.raises(ValueError, match="requires K=4"):
        spatial_attention_maps(np.zeros((7, 4, 6)), feedback="affine_ew")
    with pytest.raises(ValueError, match="finite"):
        values = np.ones((7, 4, 4)) / 4
        values[0, 0, 0] = np.nan
        spatial_attention_maps(values, feedback="affine_ew")
    with pytest.raises(ValueError, match="nonnegative"):
        values = np.ones((7, 4, 4)) / 4
        values[0, 0, 0] = -1e-9
        spatial_attention_maps(values, feedback="affine_ew")
    with pytest.raises(ValueError, match="sum to one"):
        spatial_attention_maps(np.ones((7, 4, 4)), feedback="affine_ew")
    with pytest.raises(ValueError, match="requires K=4"):
        cross = np.ones((7, 4, 8)) / 8
        spatial_attention_maps(cross, feedback="affine_ew")


def test_cache_validation_fails_closed_on_incomplete_cache(tmp_path):
    from vda_series.first_wave_figures import validate_attention_cache

    cache_path = tmp_path / "incomplete.npz"
    np.savez(cache_path, task=np.array("vda4"), feedback=np.array("affine_ew"))
    with pytest.raises(ValueError, match="missing required fields"):
        validate_attention_cache(cache_path)


def test_attention_compute_binds_no_change_cue_sweep_and_validates_lineage(tmp_path, monkeypatch):
    import torch
    from vda_series.first_wave_figures import compute_attention_cache, validate_attention_cache
    from vda_sweep import vda_core as core

    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"checkpoint selected once")
    load_calls = []
    video_calls = []

    class DummyModel:
        def forward_rl_sequence(self, videos, return_attn=False):
            assert return_attn is True
            batch = videos.shape[0]
            return {"attn_seq": torch.full((batch, 7, 4, 4), 0.25)}

    def fake_load(task, feedback, width, checkpoint_path=None):
        load_calls.append(checkpoint_path)
        return DummyModel(), 19999

    def fake_videos(task, cue_index, validity, cue_color, change, change_loc, magnitude, *, B, seed):
        video_calls.append(
            (task, cue_index, validity, cue_color, change, change_loc, magnitude, B, seed)
        )
        return torch.zeros((B, 7, 3, 50, 50))

    monkeypatch.setattr(core, "ckpt", lambda task, feedback, width: str(checkpoint))
    monkeypatch.setattr(core, "load", fake_load)
    monkeypatch.setattr(core, "make_video_batch", fake_videos)
    cache_path = compute_attention_cache(
        "vda4",
        "affine_ew",
        tmp_path / "attention",
        trials=2,
    )
    assert cache_path == tmp_path / "attention.npz"
    assert load_calls == [str(checkpoint.resolve())]
    metadata = validate_attention_cache(cache_path, expected_trials=2)
    assert metadata["checkpoint_path"] == str(checkpoint.resolve())
    assert [call[2] for call in video_calls] == [0.25, 0.5, 0.75, 1.0]
    assert all(call[4:7] == (0, -1, 0.0) for call in video_calls)
    assert all(call[7:] == (2, 1701) for call in video_calls)
    with np.load(cache_path, allow_pickle=False) as payload:
        assert payload["raw_attention_trials"].shape == (4, 2, 7, 4, 4)
        assert payload["attention_source_trials"].shape == (4, 2, 7, 4, 1, 4)
        assert payload["attention_maps_trials"].shape == (4, 2, 7, 1, 4)
        assert payload["attention_maps"].shape == (4, 7, 1, 4)
        np.testing.assert_allclose(payload["displayed_validities"], [0.25, 0.5, 0.75, 1.0])
        assert not bool(payload["change_present"])
        assert int(payload["change_index"]) == -1

    newly_selected_checkpoint = tmp_path / "newer-checkpoint.pt"
    newly_selected_checkpoint.write_bytes(b"newly selected checkpoint")
    with pytest.raises(ValueError, match="selected checkpoint path"):
        validate_attention_cache(
            cache_path,
            expected_trials=2,
            expected_checkpoint_path=newly_selected_checkpoint,
            expected_checkpoint_sha256=hashlib.sha256(
                newly_selected_checkpoint.read_bytes()
            ).hexdigest(),
        )
    with pytest.raises(ValueError, match="seed"):
        validate_attention_cache(cache_path, expected_seed=1702)
    with pytest.raises(ValueError, match="device"):
        validate_attention_cache(cache_path, expected_device="mps")


def test_attention_compute_rejects_checkpoint_bytes_changed_after_loading(tmp_path, monkeypatch):
    import torch
    from vda_series.first_wave_figures import compute_attention_cache
    from vda_sweep import vda_core as core

    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"checkpoint A")

    class MutatingModel:
        def forward_rl_sequence(self, videos, return_attn=False):
            checkpoint.write_bytes(b"checkpoint B")
            return {"attn_seq": torch.full((videos.shape[0], 7, 4, 4), 0.25)}

    monkeypatch.setattr(core, "ckpt", lambda task, feedback, width: str(checkpoint))
    monkeypatch.setattr(
        core,
        "load",
        lambda task, feedback, width, checkpoint_path=None: (MutatingModel(), 19999),
    )
    monkeypatch.setattr(
        core,
        "make_video_batch",
        lambda *args, B, seed, **kwargs: torch.zeros((B, 7, 3, 50, 50)),
    )
    with pytest.raises(RuntimeError, match="checkpoint changed during attention computation"):
        compute_attention_cache(
            "vda4",
            "affine_ew",
            tmp_path / "attention.npz",
            trials=2,
        )


def test_psychometric_compute_rejects_checkpoint_bytes_changed_during_computation(tmp_path, monkeypatch):
    import torch
    from vda_series.first_wave_figures import compute_psychometric_cache
    from vda_sweep import vda_core as core

    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"checkpoint A")

    def mutating_videos(*args, B, **kwargs):
        checkpoint.write_bytes(b"checkpoint B")
        return torch.zeros((B, 7, 3, 50, 50))

    monkeypatch.setattr(core, "ckpt", lambda task, feedback, width: str(checkpoint))
    monkeypatch.setattr(
        core,
        "load",
        lambda task, feedback, width, checkpoint_path=None: (object(), 19999),
    )
    monkeypatch.setattr(core, "make_video_batch", mutating_videos)
    monkeypatch.setattr(
        core,
        "press_times_clamp",
        lambda *args, videos, **kwargs: np.full(videos.shape[0], -1),
    )
    with pytest.raises(RuntimeError, match="checkpoint changed during psychometric computation"):
        compute_psychometric_cache(
            "vda4",
            "affine_ew",
            tmp_path / "psychometric.npz",
            trials_per_point=1,
        )


def test_psychometric_compute_pairs_seeds_and_counts_only_first_press_at_frame_five_or_later(
    tmp_path, monkeypatch
):
    import torch
    from vda_series.first_wave_figures import compute_psychometric_cache, validate_psychometric_cache
    from vda_sweep import vda_core as core

    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"checkpoint selected once")
    load_calls = []
    video_calls = []

    def fake_load(task, feedback, width, checkpoint_path=None):
        load_calls.append(checkpoint_path)
        return object(), 19999

    def fake_videos(task, cue_index, validity, cue_color, change, change_loc, magnitude, *, B, seed):
        video_calls.append((validity, change_loc, magnitude, seed))
        return torch.zeros((B, 7, 3, 50, 50))

    monkeypatch.setattr(core, "ckpt", lambda task, feedback, width: str(checkpoint))
    monkeypatch.setattr(core, "load", fake_load)
    monkeypatch.setattr(core, "make_video_batch", fake_videos)
    monkeypatch.setattr(
        core,
        "press_times_clamp",
        lambda *args, videos, **kwargs: np.array([4, 5]),
    )
    cache_path = compute_psychometric_cache(
        "vda4",
        "affine_ew",
        tmp_path / "psychometric",
        trials_per_point=2,
        seed=2801,
    )
    assert cache_path == tmp_path / "psychometric.npz"
    assert load_calls == [str(checkpoint.resolve())]
    metadata = validate_psychometric_cache(cache_path, expected_trials_per_point=2)
    assert metadata["seed"] == 2801
    with pytest.raises(ValueError, match="seed"):
        validate_psychometric_cache(cache_path, expected_seed=2802)
    with np.load(cache_path, allow_pickle=False) as payload:
        np.testing.assert_array_equal(payload["response_count_valid"], np.ones((4, 10), dtype=np.int64))
        np.testing.assert_array_equal(payload["response_count_invalid"], np.ones((4, 10), dtype=np.int64))
        assert np.all(payload["point_seeds"] == payload["point_seeds"][0])
    for magnitude in np.unique([call[2] for call in video_calls]):
        matching = [call for call in video_calls if call[2] == magnitude]
        assert len({call[3] for call in matching}) == 1


def test_cross_attention_plot_has_two_cue_proportion_by_timestep_arrays(tmp_path):
    from vda_series.first_wave_figures import (
        DISPLAYED_VALIDITIES,
        attention_source_maps,
        build_attention_figure,
        query_averaged_attention_maps,
    )

    cache_path = tmp_path / "attention_vda9_crossattn1.npz"
    image = np.full((4, 8, 7, 9, 9), 0.2 / 9.0)
    memory = np.full((4, 8, 7, 9, 9), 0.8 / 9.0)
    raw_trials = np.concatenate([image, memory], axis=-1)
    raw_mean = raw_trials.mean(axis=1)
    source_trials = attention_source_maps(raw_trials, feedback="crossattn1")
    source_mean = attention_source_maps(raw_mean, feedback="crossattn1")
    maps_trials = query_averaged_attention_maps(raw_trials, feedback="crossattn1")
    maps = query_averaged_attention_maps(raw_mean, feedback="crossattn1")
    np.savez(
        cache_path,
        attention_maps=maps,
        attention_maps_trials=maps_trials,
        attention_source_mean=source_mean,
        attention_source_trials=source_trials,
        raw_attention_mean=raw_mean,
        raw_attention_trials=raw_trials,
        trials=np.array(8),
        seed=np.array(1701),
        seed_policy=np.array(
            "common random numbers matched across displayed cue proportions on no-change trials"
        ),
        cue_index=np.array(0),
        change_index=np.array(-1),
        displayed_validities=np.asarray(DISPLAYED_VALIDITIES),
        cue_color=np.array("red"),
        change_magnitude_degrees=np.array(0.0),
        change_frame=np.array(5),
        change_present=np.array(False),
        timesteps=np.array(7),
        model_width=np.array(128),
        **_lineage_fields(tmp_path, "vda9", "crossattn1"),
    )
    outputs = build_attention_figure(cache_path, tmp_path / "figures")

    assert outputs.pdf.is_file()
    assert outputs.svg.is_file()
    assert outputs.png.is_file()
    assert outputs.metadata.is_file()
    assert outputs.pdf.stat().st_size > 10_000
    assert outputs.png.stat().st_size > 50_000

    metadata = json.loads(outputs.metadata.read_text())
    assert metadata["task"] == "vda9"
    assert metadata["grid"] == [3, 3]
    assert metadata["figure_rows"] == 4
    assert metadata["figure_columns"] == 7
    assert metadata["attention_arrays"] == ["image keys", "recurrent-memory keys"]
    assert metadata["row_semantics"] == "displayed cue proportion"
    assert metadata["column_semantics"] == "logical timestep"
    assert metadata["displayed_validities"] == [0.25, 0.5, 0.75, 1.0]
    assert metadata["cue_index"] == 0
    assert metadata["change_index"] == -1
    assert metadata["change_present"] is False
    assert metadata["trial_filter"] == "no-change trials only"
    assert set(metadata["source_panel_outputs"]) == {
        "image_keys",
        "recurrent_memory_keys",
    }
    for formats in metadata["source_panel_outputs"].values():
        assert set(formats) == {"pdf", "svg", "png"}
        for filename in formats.values():
            assert (outputs.metadata.parent / filename).is_file()

    with np.load(cache_path, allow_pickle=False) as payload:
        stale_fields = {name: payload[name] for name in payload.files}
    stale_fields["producer_sha256"] = np.array("0" * 64)
    np.savez(cache_path, **stale_fields)
    from vda_series.first_wave_figures import validate_attention_cache
    with pytest.raises(ValueError, match="producer SHA-256"):
        validate_attention_cache(cache_path)


def test_focused_environment_figure_shows_historical_grid_and_forced_locations(tmp_path):
    from vda_series.first_wave_figures import build_environment_figure

    outputs = build_environment_figure("vda9", tmp_path, seed=1701)
    for path in (outputs.pdf, outputs.svg, outputs.png, outputs.metadata):
        assert path.is_file()
    metadata = json.loads(outputs.metadata.read_text())
    assert metadata["task"] == "vda9"
    assert metadata["grid"] == [3, 3]
    assert metadata["active_items"] == 9
    assert metadata["cue_index"] == 0
    assert metadata["valid_change_index"] == 0
    assert metadata["invalid_change_index"] == 8
    assert metadata["panels"] == [
        "red cue at S1",
        "fully occupied array",
        "valid change at S1",
        "invalid change at bottom-right",
    ]


def test_psychometric_conditions_use_s1_and_true_opposite_corner():
    from vda_series.first_wave_figures import psychometric_conditions

    assert psychometric_conditions("vda4") == {
        "cue_index": 0,
        "valid_change_index": 0,
        "invalid_change_index": 3,
        "cue_color": "red",
    }
    assert psychometric_conditions("vda9")["invalid_change_index"] == 8


def test_psychometric_plot_has_three_requested_response_rate_panels(tmp_path):
    from vda_series.first_wave_figures import (
        CHANGE_MAGNITUDES,
        DISPLAYED_VALIDITIES,
        build_psychometric_figure,
    )

    cache_path = tmp_path / "psychometric_vda4_affine_ew.npz"
    shape = (len(DISPLAYED_VALIDITIES), len(CHANGE_MAGNITUDES))
    valid_count = np.arange(np.prod(shape), dtype=np.int64).reshape(shape) + 20
    invalid_count = np.arange(np.prod(shape), dtype=np.int64).reshape(shape) + 10
    valid = valid_count / 300
    invalid = invalid_count / 300
    seed = 2801
    point_seeds = np.tile(
        seed + np.arange(len(CHANGE_MAGNITUDES), dtype=np.int64) * 101,
        (len(DISPLAYED_VALIDITIES), 1),
    )
    np.savez(
        cache_path,
        response_rate_valid=valid,
        response_rate_invalid=invalid,
        response_count_valid=valid_count,
        response_count_invalid=invalid_count,
        change_magnitudes=CHANGE_MAGNITUDES,
        displayed_validities=DISPLAYED_VALIDITIES,
        point_seeds=point_seeds,
        seed=np.array(seed),
        seed_policy=np.array(
            "common random numbers matched across displayed cue proportions and valid/invalid locations at each magnitude"
        ),
        trials_per_point=np.array(300),
        cue_index=np.array(0),
        valid_change_index=np.array(0),
        invalid_change_index=np.array(3),
        cue_color=np.array("red"),
        qualifying_response_frame=np.array(5),
        change_present=np.array(True),
        timesteps=np.array(7),
        model_width=np.array(128),
        **_lineage_fields(tmp_path, "vda4", "affine_ew"),
    )
    outputs = build_psychometric_figure(cache_path, tmp_path / "figures")

    for path in (outputs.pdf, outputs.svg, outputs.png, outputs.metadata):
        assert path.is_file()
    metadata = json.loads(outputs.metadata.read_text())
    assert metadata["panel_count"] == 3
    assert metadata["panels"] == [
        "all cue proportions: valid change at S1",
        "all cue proportions: invalid change at bottom-right",
        "100% displayed validity: forced valid versus forced invalid change",
    ]
    assert metadata["forced_location_intervention"] is True
    assert "not naturally sampled" in metadata["condition_boundary"]
    assert metadata["cue_color"] == "red"
    assert metadata["cue_index"] == 0
    assert metadata["valid_change_index"] == 0
    assert metadata["invalid_change_index"] == 3


def test_frozen_snapshot_is_written_from_startup_bytes_and_digest_checked(tmp_path):
    from scripts.build_first_wave_figures import write_frozen_snapshot

    startup_bytes = b"frozen startup source"
    expected_sha256 = hashlib.sha256(startup_bytes).hexdigest()
    snapshot = tmp_path / "provenance" / "producer.py"
    write_frozen_snapshot(snapshot, startup_bytes, expected_sha256)
    assert snapshot.read_bytes() == startup_bytes
    with pytest.raises(RuntimeError, match="snapshot digest"):
        write_frozen_snapshot(snapshot, startup_bytes, "0" * 64)


def test_recomputation_requires_a_fresh_unique_run_root(tmp_path):
    from scripts.build_first_wave_figures import prepare_fresh_run

    root = tmp_path / "versioned-run"
    manifest, temporary = prepare_fresh_run(root)
    assert root.is_dir()
    assert manifest == root / "MANIFEST.json"
    assert temporary == root / ".MANIFEST.json.tmp"
    with pytest.raises(FileExistsError, match="fresh versioned root"):
        prepare_fresh_run(root)


def test_cache_integer_fields_reject_lossy_float_and_boolean_values():
    from vda_series.first_wave_figures import _npz_integer_scalar

    assert _npz_integer_scalar({"seed": np.array(1701)}, "seed") == 1701
    with pytest.raises(ValueError, match="integer scalar"):
        _npz_integer_scalar({"seed": np.array(1701.5)}, "seed")
    with pytest.raises(ValueError, match="integer scalar"):
        _npz_integer_scalar({"seed": np.array(True)}, "seed")


def test_npz_normalization_matches_numpy_exact_lowercase_suffix_contract(tmp_path):
    from vda_series.first_wave_figures import _normalized_npz_path

    assert _normalized_npz_path(tmp_path / "cache.npz") == tmp_path / "cache.npz"
    assert _normalized_npz_path(tmp_path / "cache") == tmp_path / "cache.npz"
    assert _normalized_npz_path(tmp_path / "cache.NPZ") == tmp_path / "cache.NPZ.npz"


def test_frozen_cache_digest_detects_replacement(tmp_path):
    from vda_series.first_wave_figures import _frozen_cache_bytes

    cache = tmp_path / "cache.npz"
    cache.write_bytes(b"cache A")
    _, digest = _frozen_cache_bytes(cache)
    cache.write_bytes(b"cache B")
    with pytest.raises(RuntimeError, match="immutable digest"):
        _frozen_cache_bytes(cache, digest)


def test_builder_captures_sources_before_loading_scientific_modules():
    import scripts.build_first_wave_figures as builder

    source = Path(builder.__file__).read_text(encoding="utf-8")
    main_body = source[source.index("def main()") :]
    assert main_body.index("capture_executable_sources()") < main_body.index("load_scientific_modules(")
    core_source = (Path(builder.ROOT) / "vda_sweep/vda_core.py").read_text(encoding="utf-8")
    assert "os.makedirs(FIGS" not in core_source


def test_tree_identity_brackets_manifest_and_every_run_file(tmp_path):
    from scripts.build_first_wave_figures import tree_identity

    (tmp_path / "MANIFEST.json").write_text("{}\n", encoding="utf-8")
    before = tree_identity(tmp_path)
    (tmp_path / "artifact.bin").write_bytes(b"changed")
    assert tree_identity(tmp_path) != before


def test_prospective_publication_rejects_unmanifested_macos_icon_file(tmp_path):
    from scripts.build_first_wave_figures import require_exact_file_inventory

    artifact = tmp_path / "data" / "cache.npz"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"cache")
    require_exact_file_inventory(tmp_path, {artifact})

    icon = artifact.parent / "Icon\r"
    icon.write_bytes(b"")
    with pytest.raises(RuntimeError, match="unmanifested"):
        require_exact_file_inventory(tmp_path, {artifact})


def test_prospective_publication_rejects_missing_manifested_file(tmp_path):
    from scripts.build_first_wave_figures import require_exact_file_inventory

    expected = tmp_path / ".MANIFEST.json.tmp"
    with pytest.raises(RuntimeError, match="missing"):
        require_exact_file_inventory(tmp_path, {expected})


@pytest.mark.parametrize("dangling", [False, True])
def test_inventory_rejects_unmanifested_symlink_aliases(tmp_path, dangling):
    from scripts.build_first_wave_figures import require_exact_file_inventory

    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"artifact")
    alias = tmp_path / "alias.bin"
    alias.symlink_to(tmp_path / "missing.bin" if dangling else artifact)
    with pytest.raises(RuntimeError, match="symlink or special entry"):
        require_exact_file_inventory(tmp_path, {artifact})


def test_manifest_publication_does_not_replace_on_precheck_failure(tmp_path):
    from scripts.build_first_wave_figures import publish_manifest_with_inventory

    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"artifact")
    temporary = tmp_path / ".MANIFEST.json.tmp"
    temporary.write_text("{}\n", encoding="utf-8")
    (tmp_path / "alias.bin").symlink_to(artifact)
    manifest = tmp_path / "MANIFEST.json"

    with pytest.raises(RuntimeError, match="symlink or special entry"):
        publish_manifest_with_inventory(tmp_path, temporary, manifest, {artifact})
    assert temporary.is_file()
    assert not manifest.exists()


def test_manifest_publication_rolls_back_on_postcheck_failure(tmp_path, monkeypatch):
    import scripts.build_first_wave_figures as builder

    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"artifact")
    temporary = tmp_path / ".MANIFEST.json.tmp"
    temporary.write_text("{}\n", encoding="utf-8")
    manifest = tmp_path / "MANIFEST.json"
    original = builder.require_exact_file_inventory
    calls = 0

    def fail_second_check(root, expected_files):
        nonlocal calls
        calls += 1
        original(root, expected_files)
        if calls == 2:
            raise RuntimeError("injected post-publication inventory failure")

    monkeypatch.setattr(builder, "require_exact_file_inventory", fail_second_check)
    with pytest.raises(RuntimeError, match="post-publication"):
        builder.publish_manifest_with_inventory(tmp_path, temporary, manifest, {artifact})
    assert calls == 2
    assert not temporary.exists()
    assert not manifest.exists()


@pytest.mark.parametrize("dangling", [False, True])
def test_lexical_output_root_preserves_and_rejects_root_symlink(tmp_path, dangling):
    from scripts.build_first_wave_figures import lexical_output_root, prepare_fresh_run

    target = tmp_path / ("missing-target" if dangling else "target")
    if not dangling:
        target.mkdir()
    link = tmp_path / "output-link"
    link.symlink_to(target, target_is_directory=True)

    lexical = lexical_output_root(link)
    assert lexical == link
    assert lexical.is_symlink()
    with pytest.raises(FileExistsError, match="already exists"):
        prepare_fresh_run(lexical)


def test_inventory_rejects_fifo_special_entry(tmp_path):
    import os

    from scripts.build_first_wave_figures import regular_run_files

    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    with pytest.raises(RuntimeError, match="symlink or special entry"):
        regular_run_files(tmp_path)
