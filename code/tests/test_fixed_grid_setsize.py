"""Controlled fixed-geometry VDA set-size environment tests."""
from __future__ import annotations

import os
import sys

import numpy as np
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from conv_frontend import ConvPatchFrontEnd  # noqa: E402
from envs import TASKS, make_env, task_grid  # noqa: E402
from train_rl import build_arg_parser, seed_training_rngs  # noqa: E402


FIXED_TASKS = {
    "vda_fixed1": 1,
    "vda_fixed2": 2,
    "vda_fixed4": 4,
    "vda_fixed9": 9,
    "vda_fixed16": 16,
}


@pytest.mark.parametrize(("task", "set_size"), FIXED_TASKS.items())
def test_fixed_vda_tasks_are_registered_constructible_and_cli_selectable(task, set_size):
    assert task in TASKS
    assert task_grid(task) == (4, 4)
    env = make_env(task, curriculum=False)
    assert env.set_size == set_size
    assert build_arg_parser().parse_args(["--task", task]).task == task


def test_fixed_vda_family_holds_geometry_timing_reward_and_model_dimensions_constant():
    envs = [make_env(task, curriculum=False) for task in FIXED_TASKS]
    signatures = []
    for env, set_size in zip(envs, FIXED_TASKS.values()):
        obs = env.reset()
        signatures.append(
            (
                env.grid_rows,
                env.grid_cols,
                env.n_stim,
                env.S,
                env.observation_space.shape,
                env.n_logical,
                env.T,
                env.frame_repeat,
                env.min_change_time,
                env.max_change_time,
                env.noise_multiplier,
                env.reward_scale,
                tuple(env.proportions),
                env.value_cues,
                tuple(sorted(env.color_values.items())),
            )
        )
        assert obs.shape == (100, 100, 3)
        assert obs.dtype == np.float32
        assert len(env.active) == set_size
        assert len(set(env.active)) == set_size

    assert len(set(signatures)) == 1
    assert signatures[0][:5] == (4, 4, 16, 100, (100, 100, 3))

    model_front = ConvPatchFrontEnd(grid_rows=4, grid_cols=4, image_size=100)
    assert model_front.n_tokens == 16
    assert model_front.token_dim == 128 + 16 + 8


@pytest.mark.parametrize("task", ["vda_fixed2", "vda_fixed4", "vda_fixed9", "vda_fixed16"])
@pytest.mark.parametrize(("displayed", "expected_realized"), [(0.0, False), (1.0, True)])
def test_fixed_vda_exact_validity_keeps_cue_and_target_active(task, displayed, expected_realized):
    np.random.seed(1701)
    env = make_env(task, proportions=(displayed,), curriculum=False)
    changed_trials = 0
    for _ in range(200):
        env.reset()
        assert len(env.active) == env.set_size
        assert env.cue_index in env.active
        if not env.change_true:
            continue
        changed_trials += 1
        meta = env.trial_metadata()
        assert env.change_index in env.active
        assert meta["displayed_validity"] == displayed
        assert meta["realized_validity"] is expected_realized
        assert meta["validity_mode"] == "exact_bernoulli"
        assert meta["invalid_target_available"] is True
        if displayed == 0.0:
            assert env.change_index != env.cue_index
    assert changed_trials > 50


@pytest.mark.parametrize("task", ["vda_fixed2", "vda_fixed4", "vda_fixed9", "vda_fixed16"])
def test_fixed_vda_displayed_validity_matches_realized_rate(task):
    np.random.seed(1701)
    env = make_env(task, proportions=(0.25,), curriculum=False)
    realized = []
    for _ in range(10000):
        env.reset()
        if env.change_true:
            realized.append(env.change_index == env.cue_index)
    assert len(realized) > 4800
    assert np.mean(realized) == pytest.approx(0.25, abs=0.03)


def test_fixed_vda_singleton_reports_forced_validity_degeneracy_truthfully():
    np.random.seed(2718)
    env = make_env("vda_fixed1", proportions=(0.0,), curriculum=False)
    changed_trials = 0
    for _ in range(100):
        env.reset()
        assert len(env.active) == 1
        assert env.cue_index == env.active[0]
        if not env.change_true:
            continue
        changed_trials += 1
        meta = env.trial_metadata()
        assert env.change_index == env.cue_index
        assert meta["displayed_validity"] == 0.0
        assert meta["realized_validity"] is True
        assert meta["effective_validity"] == 1.0
        assert meta["validity_mode"] == "degenerate_singleton"
        assert meta["invalid_target_available"] is False
        assert "cannot realize an uncued invalid target" in meta["validity_caveat"]
    assert changed_trials > 25


@pytest.mark.parametrize(("task", "set_size"), FIXED_TASKS.items())
def test_fixed_vda_renders_only_active_cells_on_stimulus_frames(task, set_size):
    np.random.seed(31415)
    env = make_env(task, curriculum=False)
    env.reset()
    frame = env._render_stimuli(np.zeros((env.S, env.S, 3), dtype=np.float32), L=3)

    active = set(env.active)
    assert len(active) == set_size
    for index, (r0, r1, c0, c1) in enumerate(env.cells):
        cell = frame[r0:r1, c0:c1]
        if index in active:
            assert np.any(cell != 0.0)
        else:
            assert np.all(cell == 0.0)


def _seeded_trial_replay(task, seed):
    np.random.seed(seed)
    env = make_env(task, curriculum=False)
    observations = [env.reset()]
    infos = []
    for _ in range(3):
        obs, _, _, info = env.step(0)
        observations.append(obs.copy())
        infos.append(info)
    state = {
        "active": tuple(env.active),
        "cue_index": env.cue_index,
        "change_true": env.change_true,
        "change_index": env.change_index,
        "change_time": env.change_time,
        "proportion": env.proportion,
        "cue_color": env.cue_color,
        "orientation_change": env.orientation_change,
        "orientations": tuple(env.orientations),
    }
    return np.stack(observations), infos, state


@pytest.mark.parametrize("task", FIXED_TASKS)
def test_fixed_vda_trials_replay_exactly_with_numpy_seed(task):
    first = _seeded_trial_replay(task, 4242)
    second = _seeded_trial_replay(task, 4242)
    assert np.array_equal(first[0], second[0])
    assert first[1] == second[1]
    assert first[2] == second[2]


def test_training_cli_seed_initializes_numpy_before_environment_construction():
    def trial_state():
        args = build_arg_parser().parse_args(["--task", "vda_fixed4", "--seed", "4242"])
        seed_training_rngs(args.seed)
        env = make_env(args.task, curriculum=False)
        env.reset()
        return (
            tuple(env.active),
            env.cue_index,
            env.change_index,
            env.change_time,
            env.proportion,
            tuple(env.orientations),
        )

    assert trial_state() == trial_state()
