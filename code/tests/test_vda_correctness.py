"""Focused correctness tests for VDA analysis and task generation."""
from __future__ import annotations

import hashlib
import json
import os
import sys

import numpy as np
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_VDA = os.path.join(_ROOT, "vda_sweep")
if _VDA not in sys.path:
    sys.path.insert(0, _VDA)

from envs import make_env  # noqa: E402
from vda_sweep import krauzlis_repro as K  # noqa: E402
from vda_sweep import vda_core as C  # noqa: E402
from vda_sweep import vda_fig_decode as D  # noqa: E402
from vda_sweep import vda_fig_entropy as E  # noqa: E402
from vda_sweep import vda_fig_microstim as M  # noqa: E402
from vda_sweep import vda_fig_sdt as S  # noqa: E402


def _assert_numpy_random_state_equal(left, right):
    assert left[0] == right[0]
    assert np.array_equal(left[1], right[1])
    assert left[2:] == right[2:]


def test_make_video_seed_replays_without_mutating_global_numpy_rng():
    np.random.seed(808)
    before = np.random.get_state()

    first = C.make_video("vda4", C.TL, 0.5, "red", 1, C.BR, seed=91)
    after_first = np.random.get_state()
    second = C.make_video("vda4", C.TL, 0.5, "red", 1, C.BR, seed=91)
    after_second = np.random.get_state()

    assert np.array_equal(first, second)
    _assert_numpy_random_state_equal(before, after_first)
    _assert_numpy_random_state_equal(before, after_second)


def test_collect_replays_complete_outputs_without_mutating_global_numpy_rng():
    class ReplayModel:
        def forward_rl_sequence(self, videos, return_cell=False):
            assert return_cell is True
            return {"cell_seq": videos[:, :, :1, :2, :2]}

    np.random.seed(707)
    before = np.random.get_state()
    first = D.collect(ReplayModel(), "vda1", n=16, seed=1234)
    after_first = np.random.get_state()
    second = D.collect(ReplayModel(), "vda1", n=16, seed=1234)
    after_second = np.random.get_state()

    _assert_numpy_random_state_equal(before, after_first)
    _assert_numpy_random_state_equal(before, after_second)
    assert np.array_equal(first[0], second[0])
    for left, right in zip(first[1:3], second[1:3]):
        assert left.keys() == right.keys()
        assert all(np.array_equal(left[key], right[key]) for key in left)
    assert first[3] == second[3]


def test_make_video_batch_replays_distinct_trials_without_global_rng_leak():
    np.random.seed(606)
    before = np.random.get_state()
    first = C.make_video_batch(
        "vda4", C.TL, 1.0, "red", 0, -1, 18.0, B=3, seed=77
    )
    after = np.random.get_state()
    second = C.make_video_batch(
        "vda4", C.TL, 1.0, "red", 0, -1, 18.0, B=3, seed=77
    )

    _assert_numpy_random_state_equal(before, after)
    assert np.array_equal(first.cpu().numpy(), second.cpu().numpy())
    assert not np.array_equal(first[0].cpu().numpy(), first[1].cpu().numpy())


def test_press_times_clamp_uses_supplied_batch_and_infers_its_size(monkeypatch):
    videos = C.torch.arange(2 * C.T * 3 * 2 * 2, dtype=C.torch.float32).reshape(
        2, C.T, 3, 2, 2
    )
    seen = []

    class FakeModel:
        def init_states(self, batch_size, device=None):
            assert batch_size == 2
            return None

        def rl_step(self, frame, state, attn_clamp=None):
            del state, attn_clamp
            seen.append(frame.clone())
            return {
                "actor_logits": C.torch.zeros((2, 2)),
                "new_states": None,
            }

    monkeypatch.setattr(
        C,
        "make_video_batch",
        lambda *args, **kwargs: pytest.fail("supplied videos must be reused"),
    )
    press = C.press_times_clamp(
        FakeModel(), "vda4", C.TL, 1.0, "red", 0, -1, 18.0,
        videos=videos,
    )

    assert press.shape == (2,)
    assert len(seen) == C.T
    assert all(C.torch.equal(seen[t], videos[:, t]) for t in range(C.T))


def test_rollout_uses_supplied_batch_instead_of_regenerating(monkeypatch):
    videos = C.torch.zeros((2, C.T, 3, 2, 2))

    class FakeModel:
        def init_states(self, batch_size, device=None):
            assert batch_size == 2
            return None

        def rl_step(self, frame, state, attn_clamp=None):
            del frame, state, attn_clamp
            return {
                "actor_logits": C.torch.zeros((2, 2)),
                "V_scalar": C.torch.zeros(2),
                "V_dist": C.torch.zeros((2, 5)),
                "rec": C.torch.zeros((2, 1)),
                "new_states": None,
            }

    monkeypatch.setattr(
        C,
        "make_video_batch",
        lambda *args, **kwargs: pytest.fail("supplied videos must be reused"),
    )
    result = C.rollout(
        FakeModel(), "vda4", C.TL, 1.0, "red", 0, -1, 18.0,
        videos=videos,
    )

    assert all(array.shape[0] == 2 for array in result)


def test_sdt_sweep_builds_each_condition_once_and_reuses_it_for_all_alphas(monkeypatch):
    class FakeModel:
        n_tokens = 4

    batches = []
    used = []

    def fake_batch(*args, **kwargs):
        token = object()
        batches.append((args, kwargs, token))
        return token

    def fake_press(*args, videos=None, **kwargs):
        used.append(videos)
        return np.asarray([5, -1, 5, -1])

    monkeypatch.setattr(S.C, "make_video_batch", fake_batch)
    monkeypatch.setattr(S.C, "press_times_clamp", fake_press)

    ds, cs = S.run_sweep(FakeModel(), "vda4", K=4, seed=321, B=4)

    assert len(batches) == 2
    assert len(used) == 2 * len(S.ALPHAS)
    assert all(used.count(batch[2]) == len(S.ALPHAS) for batch in batches)
    assert len(ds) == len(cs) == len(S.ALPHAS)


def test_microstim_sweep_reuses_one_no_change_batch_across_sites_and_alphas(monkeypatch):
    class FakeModel:
        n_tokens = 4

    batch = object()
    used = []
    monkeypatch.setattr(M.C, "make_video_batch", lambda *args, **kwargs: batch)

    def fake_press(*args, videos=None, **kwargs):
        used.append(videos)
        return np.asarray([5, -1, 5, -1])

    monkeypatch.setattr(M.C, "press_times_clamp", fake_press)

    fa_tl, fa_br = M.run_sweep(FakeModel(), "vda4", K=4, seed=19, B=4)

    assert used == [batch] * (2 * len(M.ALPHAS))
    assert len(fa_tl) == len(fa_br) == len(M.ALPHAS)


def test_entropy_conditions_share_real_change_batch_and_separate_no_change_batch(monkeypatch):
    class FakeModel:
        n_tokens = 4

    batches = [object(), object()]
    made = []

    def fake_batch(*args, **kwargs):
        batch = batches[len(made)]
        made.append((args, kwargs, batch))
        return batch

    seen = []

    def fake_measure(*args, videos=None, **kwargs):
        seen.append(videos)
        return (0.1, 0.2, 0.3)

    monkeypatch.setattr(E.C, "make_video_batch", fake_batch)
    monkeypatch.setattr(E, "measure", fake_measure)

    result = E.run_conditions(FakeModel(), "vda4", K=4, seed=29, B=4)

    assert len(made) == 2
    assert seen == [batches[0], batches[0], batches[0], batches[1]]
    assert np.asarray(result).shape == (4, 3)


def test_krauzlis_baseline_and_suppression_reuse_matched_condition_batches(monkeypatch):
    class FakeModel:
        n_tokens = 4

    made = []
    used = []

    def fake_batch(*args, **kwargs):
        token = object()
        made.append((args, kwargs, token))
        return token

    def fake_press(*args, clamp=None, videos=None, **kwargs):
        used.append((videos, clamp))
        return np.asarray([5, -1, 5, -1])

    monkeypatch.setattr(K.C, "make_video_batch", fake_batch)
    monkeypatch.setattr(K.C, "press_times_clamp", fake_press)

    result = K.run_conditions(FakeModel(), K=8, seed=41, B=4)

    assert len(made) == 2 * len(K.MAGS) + 1
    for _, _, batch in made[:-1]:
        calls = [call for call in used if call[0] is batch]
        assert len(calls) == 2
        assert sum(clamp is None for _, clamp in calls) == 1
        assert sum(clamp is not None for _, clamp in calls) == 1
    assert [call[0] for call in used].count(made[-1][2]) == 1
    assert all(len(values) == len(K.MAGS) for values in (result[0], result[1], result[3], result[4]))


def test_krauzlis_output_records_seed_n_and_loaded_iterations(tmp_path, monkeypatch):
    class FakeModel:
        n_tokens = 4

    monkeypatch.setattr(K.C, "FIGS", str(tmp_path))
    monkeypatch.setattr(K, "load_k", lambda task, feedback: (FakeModel(), 77))
    monkeypatch.setattr(
        K,
        "run_conditions",
        lambda model, key_count, seed=K.SEED, B=K.B: (
            [0.1] * 3, [0.2] * 3, 0.3, [0.4] * 3, [0.5] * 3
        ),
    )

    saved = K.main()

    assert saved == (tmp_path / "krauzlis.npz").resolve()
    with np.load(saved) as result:
        assert int(result["seed"]) == K.SEED
        assert int(result["n"]) == K.B
        assert int(result["crossattn1_iter"]) == 77
        assert int(result["affine_ew_iter"]) == 77


@pytest.mark.parametrize(
    ("K", "N", "i", "expected"),
    [
        (8, 4, 2, [2, 6]),
        (18, 9, 5, [5, 14]),
        (32, 16, 11, [11, 27]),
        (9, 9, 5, [5]),
    ],
)
def test_location_clamp_keys_use_runtime_patch_count(K, N, i, expected):
    assert C._loc_keys(K, N, i) == expected


@pytest.mark.parametrize(("K", "N"), [(8, 9), (17, 9), (0, 0), (8, 0)])
def test_location_clamp_keys_reject_incompatible_key_and_patch_counts(K, N):
    with pytest.raises(ValueError, match="K.*N"):
        C._loc_keys(K, N, 0)


@pytest.mark.parametrize(
    ("K", "N", "i"),
    [
        (8.9, 4, 0),
        (8, 4.9, 0),
        (8, 4, 0.9),
        ("8", 4, 0),
        (8, None, 0),
        (8, 4, 0j),
        (True, 1, 0),
        (2, np.bool_(True), 0),
        (2, 1, False),
    ],
)
def test_location_clamp_keys_reject_non_integer_inputs(K, N, i):
    with pytest.raises(TypeError, match="integers"):
        C._loc_keys(K, N, i)


@pytest.mark.parametrize(
    ("K", "N", "i", "expected"),
    [
        (np.int64(8), np.int32(4), np.int16(2), [2, 6]),
        (np.int64(9), np.int64(9), np.int64(5), [5]),
    ],
)
def test_location_clamp_keys_accept_numpy_integer_inputs(K, N, i, expected):
    assert C._loc_keys(K, N, i) == expected


@pytest.mark.parametrize(
    ("alpha", "error"),
    [
        (True, TypeError),
        (np.bool_(False), TypeError),
        ("0.5", TypeError),
        (None, TypeError),
        (np.nan, ValueError),
        (np.inf, ValueError),
        (-0.01, ValueError),
        (1.01, ValueError),
    ],
)
def test_clamp_alpha_rejects_nonfinite_nonnumeric_or_out_of_range_alpha(alpha, error):
    with pytest.raises(error, match="alpha"):
        C.clamp_alpha(8, 4, 0, alpha)


@pytest.mark.parametrize(
    ("scale", "error"),
    [
        (True, TypeError),
        ("6", TypeError),
        (None, TypeError),
        (np.nan, ValueError),
        (-np.inf, ValueError),
    ],
)
def test_clamp_alpha_rejects_nonfinite_or_nonnumeric_scale(scale, error):
    with pytest.raises(error, match="scale"):
        C.clamp_alpha(8, 4, 0, 0.5, scale=scale)


def test_clamp_alpha_accepts_finite_numpy_numbers_at_closed_interval_bounds():
    assert C.clamp_alpha(8, 4, 0, np.float32(0), scale=np.int64(2)) == {
        "0": -2.0,
        "4": -2.0,
    }
    assert C.clamp_alpha(8, 4, 0, np.float64(1), scale=np.float32(2)) == {
        "0": 2.0,
        "4": 2.0,
    }


@pytest.mark.parametrize(("K", "N", "i"), [(8, 4, -1), (8, 4, 4), (8, 4, 9)])
def test_location_clamp_keys_reject_negative_or_out_of_range_locations(K, N, i):
    with pytest.raises(ValueError, match="0 <= i < N"):
        C._loc_keys(K, N, i)


@pytest.mark.parametrize("task", ["vda2", "vda4", "vda9", "vda16"])
def test_vda_displayed_validity_matches_realized_cued_change_rate(task):
    np.random.seed(1701)
    env = make_env(task, proportions=(0.25,), curriculum=False)
    realized = []
    for _ in range(4000):
        env.reset()
        if not env.change_true:
            continue
        is_cued = env.change_index == env.cue_index
        realized.append(is_cued)
        if not is_cued:
            assert env.change_index != env.cue_index

    rate = float(np.mean(realized))
    assert len(realized) > 1900
    assert rate == pytest.approx(0.25, abs=0.03)


@pytest.mark.parametrize("task", ["vda2", "vda4", "vda9", "vda16"])
def test_vda_exposes_displayed_and_realized_target_metadata(task):
    np.random.seed(29)
    env = make_env(task, proportions=(0.25,), curriculum=False)
    env.reset()
    meta = env.trial_metadata()

    assert meta["displayed_validity"] == 0.25
    assert meta["displayed_target_index"] == env.cue_index
    assert meta["realized_target_index"] == (env.change_index if env.change_true else None)
    assert meta["realized_validity"] == (
        (env.change_index == env.cue_index) if env.change_true else None
    )
    assert env.cue_index in meta["active_locations"]
    if env.change_true:
        assert env.change_index in meta["active_locations"]

    _, _, _, info = env.step(0)
    for key, value in meta.items():
        assert info[key] == value


@pytest.mark.parametrize(
    ("task", "active"),
    [
        ("vda1", (0,)),
        ("vda2", (0, 3)),
        ("vda4", (0, 1, 2, 3)),
        ("vda9", tuple(range(9))),
        ("vda16", tuple(range(16))),
    ],
)
def test_decode_sampling_uses_task_active_locations_and_balances_changes(task, active):
    conditions, labels, config = D.sample_conditions(task, n=288, seed=73)

    assert config["active_locations"] == active
    assert set(np.unique(conditions["change_index"])) <= {-1, *active}
    assert int(labels["change"].sum()) == 144
    assert set(np.unique(labels["colour"])) == {0, 1, 2}
    assert set(np.unique(labels["validity"])) == {0, 1, 2, 3}

    changed = labels["change"].astype(bool)
    cued = conditions["change_index"] == config["cue_index"]
    if task == "vda1":
        assert np.all(cued[changed])
        assert config["location_decode_defined"] is False
    else:
        assert int(np.sum(changed & cued)) == int(np.sum(changed & ~cued)) == 72
        assert set(np.unique(conditions["change_index"][changed])) == set(active)
        assert config["location_decode_defined"] is True


@pytest.mark.parametrize(
    ("task", "n"),
    [
        ("vda1", 144),
        ("vda2", 144),
        ("vda4", 144),
        ("vda9", 144),
        ("vda16", 288),
    ],
)
def test_decode_sampling_replays_exactly_from_seed_and_config(task, n):
    first = D.sample_conditions(task, n=n, seed=991)
    replay = D.sample_conditions(task, n=first[2]["n"], seed=first[2]["seed"])
    assert first[2] == replay[2]
    for left, right in zip(first[:2], replay[:2]):
        assert left.keys() == right.keys()
        assert all(np.array_equal(left[key], right[key]) for key in left)


def test_vda1_location_decode_timecourse_is_undefined():
    _, labels, config = D.sample_conditions("vda1", n=24, seed=5)
    cell = np.zeros((24, 7, 2, 3), dtype=np.float32)
    result = D.decode_timecourse(
        cell,
        labels["chg_loc"],
        defined=config["location_decode_defined"],
    )
    assert result.shape == (7,)
    assert np.isnan(result).all()


@pytest.mark.parametrize(
    ("task", "minimum"),
    [("vda1", 16), ("vda2", 16), ("vda4", 48), ("vda9", 128), ("vda16", 256)],
)
def test_decode_sampling_accepts_documented_conservative_cv4_minimum(task, minimum):
    conditions, labels, config = D.sample_conditions(task, n=minimum, seed=5)

    assert len(conditions["change_true"]) == minimum
    assert len(labels["chg_loc"]) == minimum
    assert config["cv_folds"] == 4
    assert config["minimum_n"] == minimum


def test_vda16_decoder_minimum_supports_every_location_in_each_cv4_split():
    conditions, labels, config = D.sample_conditions("vda16", n=256, seed=5)

    changed = labels["change"].astype(bool)
    realized_locations, counts = np.unique(
        conditions["change_index"][changed], return_counts=True
    )
    assert config["active_locations"] == tuple(range(16))
    np.testing.assert_array_equal(realized_locations, np.arange(16))
    assert counts.min() >= D.CV_FOLDS


@pytest.mark.parametrize(
    ("task", "minimum"),
    [("vda1", 16), ("vda2", 16), ("vda4", 48), ("vda9", 128), ("vda16", 256)],
)
def test_decode_sampling_rejects_one_below_task_cv4_minimum(task, minimum):
    with pytest.raises(ValueError, match=rf"{task}.*n.*{minimum}"):
        D.sample_conditions(task, n=minimum - 1, seed=5)


def test_decode_main_rejects_n_invalid_for_any_task_before_loading_models(monkeypatch):
    monkeypatch.setattr(
        C,
        "load",
        lambda *args, **kwargs: pytest.fail("sample preflight must precede model loading"),
    )

    with pytest.raises(ValueError, match=r"vda9.*n.*128"):
        D.main(["--n", "127"])

    with pytest.raises(ValueError, match=r"vda16.*n.*256"):
        D.main(["--n", "255"])


def test_decode_cli_defaults_to_versioned_nonlegacy_output_and_accepts_run_config():
    defaults = D.parse_args([])
    configured = D.parse_args(["--out", "custom/decode.npz", "--seed", "17", "--n", "128"])

    assert D.resolve_output_path(defaults.out) == D.DEFAULT_OUTPUT
    assert D.DEFAULT_OUTPUT.parent.name == "2026-07-11_corrected"
    assert D.DEFAULT_OUTPUT.parent.parent.name == "derived"
    assert D.DEFAULT_OUTPUT != D.LEGACY_OUTPUT
    assert defaults.seed == D.SEED
    assert defaults.n == D.N
    assert defaults.overwrite is False
    assert defaults.dangerously_overwrite_legacy is False
    assert configured.out == "custom/decode.npz"
    assert configured.seed == 17
    assert configured.n == 128


def test_decode_output_normalizes_npz_suffix_before_safety_checks(tmp_path):
    suffixless = tmp_path / "corrected" / "decode"
    other_suffix = tmp_path / "corrected" / "decode.data"

    assert D.resolve_output_path(suffixless) == suffixless.with_name("decode.npz").resolve()
    assert D.resolve_output_path(other_suffix) == other_suffix.with_name("decode.data.npz").resolve()


def test_decode_refuses_existing_corrected_output_without_overwrite(tmp_path):
    output = tmp_path / "decode.npz"
    output.write_bytes(b"preserve me")

    with pytest.raises(FileExistsError, match="--overwrite"):
        D.resolve_output_path(output)

    assert D.resolve_output_path(output, overwrite=True) == output.resolve()
    assert output.read_bytes() == b"preserve me"


def test_decode_legacy_permissions_are_separate_and_both_required():
    with pytest.raises(ValueError, match="legacy"):
        D.resolve_output_path(D.LEGACY_OUTPUT, overwrite=True)
    with pytest.raises(FileExistsError, match="--overwrite"):
        D.resolve_output_path(D.LEGACY_OUTPUT, allow_legacy=True)


def test_decode_main_refuses_existing_corrected_output_before_loading_models(
    tmp_path, monkeypatch
):
    output = tmp_path / "decode.npz"
    output.write_bytes(b"preserve me")
    monkeypatch.setattr(
        C,
        "load",
        lambda *args, **kwargs: pytest.fail("overwrite preflight must precede model loading"),
    )

    with pytest.raises(FileExistsError, match="--overwrite"):
        D.main(["--out", str(output), "--n", "256"])

    assert output.read_bytes() == b"preserve me"


def test_decode_main_writes_small_configured_result_without_changing_legacy_bytes(
    tmp_path, monkeypatch
):
    legacy_before = D.LEGACY_OUTPUT.read_bytes()
    requested_output = tmp_path / "derived" / "controlled" / "decode"
    output = requested_output.with_name("decode.npz")
    collect_calls = []
    load_calls = []
    checkpoints = {}
    for task in D.DECODER_TASKS:
        for feedback in ("crossattn1", "affine_ew"):
            checkpoint = tmp_path / "checkpoints" / task / feedback / "latest.pt"
            checkpoint.parent.mkdir(parents=True, exist_ok=True)
            checkpoint.write_bytes(f"{task}:{feedback}:checkpoint".encode())
            checkpoints[(task, feedback)] = checkpoint

    monkeypatch.setattr(
        C,
        "ckpt",
        lambda task, feedback, dm: str(checkpoints[(task, feedback)]),
    )

    def controlled_load(task, feedback, dm, checkpoint_path=None):
        load_calls.append((task, feedback, dm, checkpoint_path))
        assert checkpoint_path == str(checkpoints[(task, feedback)].resolve())
        return object(), 123

    monkeypatch.setattr(C, "load", controlled_load)

    def controlled_collect(model, task, n, seed):
        del model
        collect_calls.append((task, n, seed))
        labels = {
            "colour": np.arange(n, dtype=np.int64) % 3,
            "validity": np.arange(n, dtype=np.int64) % 4,
            "change": np.arange(n, dtype=np.int64) % 2,
            "chg_loc": np.arange(n, dtype=np.int64) % 2,
            "cued_change": np.arange(n, dtype=np.int64) % 2,
        }
        conditions = {"change_index": np.arange(n, dtype=np.int64) % 2}
        config = {
            "task": task,
            "n": n,
            "seed": seed,
            "location_decode_defined": task != "vda1",
        }
        return np.zeros((n, 1, 1, 1), dtype=np.float32), labels, conditions, config

    monkeypatch.setattr(D, "collect", controlled_collect)
    monkeypatch.setattr(
        D,
        "decode_timecourse",
        lambda cell, labels, defined=True: np.asarray([0.5 if defined else np.nan]),
    )

    saved = D.main(["--out", str(requested_output), "--seed", "17", "--n", "256"])

    assert saved == output.resolve()
    assert output.is_file()
    assert len(load_calls) == len(D.DECODER_TASKS) * len(D.FEEDBACKS)
    assert len(collect_calls) == len(D.DECODER_TASKS) * len(D.FEEDBACKS)
    assert all(n == 256 and seed == 17 for _, n, seed in collect_calls)
    with np.load(output) as result:
        config = json.loads(str(result["vda2_sample_config_json"]))
        assert config["seed"] == 17
        assert config["n"] == 256
        for task in D.DECODER_TASKS:
            for feedback in ("crossattn1", "affine_ew"):
                key = f"{task}_{feedback}_provenance_json"
                provenance = json.loads(str(result[key]))
                checkpoint = checkpoints[(task, feedback)].resolve()
                assert provenance == {
                    "checkpoint_path_absolute": str(checkpoint),
                    "checkpoint_path_relative": os.path.relpath(checkpoint, D.PROJECT_ROOT),
                    "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                    "d_mem": 128,
                    "feedback": feedback,
                    "loaded_iteration": 123,
                    "model_identity": f"{task}:{feedback}:d_mem=128",
                    "n": 256,
                    "replay_config": json.loads(
                        str(result[f"{task}_sample_config_json"])
                    ),
                    "seed": 17,
                    "task": task,
                }
    assert D.LEGACY_OUTPUT.read_bytes() == legacy_before


def test_decode_main_rejects_paths_resolving_to_legacy_before_loading_models(
    tmp_path, monkeypatch
):
    legacy_before = D.LEGACY_OUTPUT.read_bytes()
    legacy_alias = tmp_path / "legacy-alias.npz"
    legacy_alias.symlink_to(D.LEGACY_OUTPUT)
    monkeypatch.setattr(
        C,
        "load",
        lambda *args, **kwargs: pytest.fail("unsafe output must fail before decoder work"),
    )

    with pytest.raises(ValueError, match="legacy"):
        D.main(["--out", str(legacy_alias), "--n", "256"])

    assert D.LEGACY_OUTPUT.read_bytes() == legacy_before


def test_decode_main_rejects_hard_link_to_legacy_before_loading_models(
    tmp_path, monkeypatch
):
    legacy_before = D.LEGACY_OUTPUT.read_bytes()
    legacy_hard_link = tmp_path / "legacy-hard-link.npz"
    os.link(D.LEGACY_OUTPUT, legacy_hard_link)
    assert os.path.samefile(D.LEGACY_OUTPUT, legacy_hard_link)
    monkeypatch.setattr(
        C,
        "load",
        lambda *args, **kwargs: pytest.fail("unsafe output must fail before decoder work"),
    )

    with pytest.raises(ValueError, match="legacy"):
        D.main(["--out", str(legacy_hard_link), "--n", "256"])

    assert D.LEGACY_OUTPUT.read_bytes() == legacy_before
