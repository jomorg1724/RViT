"""Reward-table and fidelity tests for the task-battery environments.

These exercise the env reward/target/response logic directly (the network is covered by
test_paper.py). Trials are made deterministic by resetting, overriding the trial variables,
and driving step() with a fixed declare policy.
"""
from __future__ import annotations

import os
import sys

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from envs import make_env                                             # noqa: E402
from envs.tasks import (Validity4Env, VDAEnv, KrauzlisEnv,           # noqa: E402
                        LuoMaunsellEnv, BaruniEnv, MotionZKEnv)


# ── helpers ────────────────────────────────────────────────────────────────
def _force_trial(env, change_true, change_index, cue_index, change_time=5, delta=40.0):
    """Reset, then pin the trial variables so a single trial's outcome is deterministic."""
    env.reset()
    env.change_true = int(change_true)
    env.cue_index = int(cue_index)
    env.change_index = int(change_index) if change_true else -1
    env.change_time = int(change_time)
    env.orientation_change = float(delta)
    env.valid = int(change_true == 1 and env.change_index == cue_index)
    env.t = 0
    env._frame_cache = None


def _run(env, declare_at=None, action_val=1):
    """Step to termination sending `action_val` at logical frame `declare_at` (else wait).
    Returns (terminal_reward, info)."""
    done, r, info = False, 0.0, {}
    while not done:
        L = env.t // env.frame_repeat
        action = action_val if (declare_at is not None and L == declare_at) else 0
        _obs, r, done, info = env.step(action)
    return r, info


# ── plain detection (Validity4) ─────────────────────────────────────────────
def test_validity4_reward_table():
    env = Validity4Env(curriculum=False)
    # hit: change trial, declare on the change frame → reward 1
    _force_trial(env, 1, 0, 0); r, _ = _run(env, declare_at=5); assert r == 1.0
    # premature: declare before change → 0
    _force_trial(env, 1, 0, 0); r, _ = _run(env, declare_at=4); assert r == 0.0
    # miss: change trial, never declare → 0
    _force_trial(env, 1, 0, 0); r, _ = _run(env, declare_at=None); assert r == 0.0
    # correct rejection: no-change trial, wait to end → 1
    _force_trial(env, 0, 0, 0); r, _ = _run(env, declare_at=None); assert r == 1.0
    # false alarm: no-change trial, declare → 0
    _force_trial(env, 0, 0, 0); r, _ = _run(env, declare_at=5); assert r == 0.0


def test_validity4_displayed_validity_equals_true():
    """With exclude_cued_in_uniform, empirical P(change@cued | change) == displayed proportion."""
    env = Validity4Env(curriculum=False, proportions=(0.5,))
    rng = np.random.seed(0)
    cued = total = 0
    for _ in range(4000):
        env.reset()
        if env.change_true == 1:
            total += 1
            cued += int(env.change_index == env.cue_index)
    frac = cued / total
    # true validity 0.5 (NOT 0.5 + 0.5/4 = 0.625 that the old uniform-incl-cued draw gave)
    assert 0.46 <= frac <= 0.54, frac


# ── Krauzlis attend/ignore ──────────────────────────────────────────────────
def test_krauzlis_reward_table():
    env = KrauzlisEnv(curriculum=False)
    cue = 0
    # cued change, declare → hit (1)
    _force_trial(env, 1, cue, cue); r, _ = _run(env, declare_at=5); assert r == 1.0
    # cued change, wait → miss (0)
    _force_trial(env, 1, cue, cue); r, _ = _run(env, declare_at=None); assert r == 0.0
    # FOIL (diametric distractor, cell 3) change, declare → false alarm (0)
    _force_trial(env, 1, 3, cue); r, _ = _run(env, declare_at=5); assert r == 0.0
    # FOIL change, correctly withhold → correct rejection of the distractor (1)
    _force_trial(env, 1, 3, cue); r, _ = _run(env, declare_at=None); assert r == 1.0
    assert env.active_cells == (0, 3)                                   # 2-patch geometry
    # no-change, wait → CR (1)
    _force_trial(env, 0, 0, cue); r, _ = _run(env, declare_at=None); assert r == 1.0
    # no-change, declare → FA (0)
    _force_trial(env, 0, 0, cue); r, _ = _run(env, declare_at=5); assert r == 0.0


# ── Luo & Maunsell criterion session ────────────────────────────────────────
def test_luo_criterion_reward_ratio():
    env = LuoMaunsellEnv(session="criterion", r_hit=2.0, r_cr=1.0, curriculum=False)
    _force_trial(env, 1, 0, 0); r, _ = _run(env, declare_at=5); assert r == 2.0   # hit pays r_hit
    _force_trial(env, 0, 0, 0); r, _ = _run(env, declare_at=None); assert r == 1.0  # CR pays r_cr
    _force_trial(env, 1, 0, 0); r, _ = _run(env, declare_at=None); assert r == 0.0  # miss
    _force_trial(env, 0, 0, 0); r, _ = _run(env, declare_at=5); assert r == 0.0     # FA


# ── Luo & Maunsell sensitivity session (reward-based, pixels identical) ──────
def test_luo_sensitivity_reward_by_location():
    env = LuoMaunsellEnv(session="sensitivity", v_high=5.0, v_low=1.0, curriculum=False)
    env.reset()
    # per-location AVERAGE reward is the sensitivity knob; PIXELS are identical (loc_signal all 1)
    assert env.loc_value[env.cue_index] == 5.0
    assert all(env.loc_value[i] == 1.0 for i in range(env.n_stim) if i != env.cue_index)
    assert all(env.loc_signal[i] == 1.0 for i in range(env.n_stim))     # NO pixel/Δ scaling
    def setval(cue):
        env.loc_value = np.full(env.n_stim, 1.0, np.float32); env.loc_value[cue] = 5.0
    _force_trial(env, 1, 0, 0); setval(0); r, _ = _run(env, declare_at=5); assert r == 5.0   # hit at cued (high value)
    _force_trial(env, 0, 0, 0); setval(0); r, _ = _run(env, declare_at=None); assert r == 5.0  # CR pays the cued value (H:CR ratio = 1)
    _force_trial(env, 1, 3, 0); setval(0); r, _ = _run(env, declare_at=5); assert r == 1.0   # hit at an uncued (low value) location


def test_luo_response_window_expiry_is_clean():
    """A bound response window expires as a miss with base-compatible info, and updates θ."""
    env = LuoMaunsellEnv(session="criterion", response_window=1, curriculum=True,
                         curr_window=1)  # window=1 so expiry can bind at T=7/change@5
    _force_trial(env, 1, 0, 0)
    r, info = _run(env, declare_at=None)
    assert r == 0.0
    assert "correct" in info and info["correct"] == 0.0          # base-compatible info key (was missing)
    assert info.get("expired") is True


# ── registry wiring ─────────────────────────────────────────────────────────
def test_all_battery_tasks_construct():
    for name in ("validity4", "vda4", "luo_maunsell_sensitivity",
                 "luo_maunsell_criterion", "krauzlis"):
        env = make_env(name, curriculum=False)
        obs = env.reset()
        assert obs.shape == (env.S, env.S, 3)
        env.step(0)


# ── Baruni 2-AFC discrimination (post-cued query) ───────────────────────────
def test_baruni_design_two_cells_post_cued():
    env = BaruniEnv(curriculum=False)
    assert env.action_space.n == 3
    env.reset()
    assert set(env.active_cells) == {0, 3} and env.queried in env.active_cells
    for i in env.active_cells:                                          # each cell: class + value + valid orientation
        assert env.cls[i] in (0, 1) and env.val[i] in (env.v_small, env.v_large)
        off = env.orientations[i] - env.BOUNDARY
        assert (off > 0) == (env.cls[i] == 1)
    # the query marker is NOT present before query_frame, and IS present at/after
    env.change_time = 5; env.t = 0; env._frame_cache = None
    for _ in range(4):
        pre, _, _, _ = env.step(0)                                      # t1..t4 (t4 < query_frame 5)
    q = env.cells[env.queried]
    at5, _, _, _ = env.step(0)                                          # t5 = query_frame
    assert at5[q[0], q[2]:q[3]].sum() > pre[q[0], q[2]:q[3]].sum()     # bright border appears on the queried cell


def test_baruni_reward_table():
    env = BaruniEnv(curriculum=False)

    def trial(queried_cls, queried_val, report_action, at):
        env.reset()
        env.queried = 0; env.cls[0] = int(queried_cls); env.val[0] = float(queried_val)
        env.t = 0; env._frame_cache = None
        return _run(env, declare_at=at, action_val=report_action)

    # correct discrimination of the QUERIED cell (query revealed at t5) pays its value
    r, info = trial(1, 5.0, 2, 5); assert r == 5.0 and info["correct"] == 1.0
    r, _ = trial(0, 5.0, 1, 5); assert r == 5.0                          # correct class 0
    r, _ = trial(1, 5.0, 1, 5); assert r == 0.0                          # wrong class
    r, _ = trial(1, 5.0, 2, 4); assert r == 0.0                          # report BEFORE the query (t4<5) → 0
    r, _ = trial(1, 5.0, 2, None); assert r == 0.0                       # no response → 0


def test_baruni_registered():
    env = make_env("baruni", curriculum=False)
    assert env.action_space.n == 3
    obs = env.reset(); assert obs.shape == (env.S, env.S, 3)


# ── Motion (Zénon-Krauzlis motion-direction change-detection) ───────────────
def _force_zk(env, change_true, change_index, cue_index):
    env.reset()
    env.cue_index = cue_index
    env.foil_index = 3 if cue_index == 0 else 0
    env.change_true = int(change_true)
    env.change_index = int(change_index) if change_true else -1
    env.change_time = 5; env.orientation_change = 40.0
    env.loc_signal = np.ones(env.n_stim, np.float32)
    env.dots = {i: env._random_dots_in_aperture(*env._cell_hw(i)) for i in env.active_cells}
    env.t = 0; env._frame_cache = None


def test_motion_zk_go_nogo_reward():
    env = MotionZKEnv(curriculum=False)                        # cue=S1(0), foil=S4(3)
    _force_zk(env, 1, 0, 0); r, _ = _run(env, declare_at=5); assert r == 1.0   # cued change → declare = hit
    _force_zk(env, 1, 0, 0); r, _ = _run(env, declare_at=None); assert r == 0.0  # cued change → wait = miss
    _force_zk(env, 1, 3, 0); r, _ = _run(env, declare_at=5); assert r == 0.0   # FOIL change → declare = false alarm
    _force_zk(env, 1, 3, 0); r, _ = _run(env, declare_at=None); assert r == 1.0  # FOIL change → withhold = CR (ignore foil)
    _force_zk(env, 0, 0, 0); r, _ = _run(env, declare_at=None); assert r == 1.0  # no change → wait = CR
    _force_zk(env, 0, 0, 0); r, _ = _run(env, declare_at=5); assert r == 0.0    # no change → declare = FA


def test_motion_zk_two_active_patches_others_blank():
    env = MotionZKEnv(curriculum=False)
    env.reset()
    for _ in range(3):                                          # step to a stimulus frame (t=3)
        obs, _, _, _ = env.step(0)
    def patch_sum(i):
        r0, r1, c0, c1 = env.cells[i]; return obs[r0:r1, c0:c1, :].sum()
    assert patch_sum(0) > 0 and patch_sum(3) > 0                # diagonal patches have dots
    assert patch_sum(1) == 0 and patch_sum(2) == 0             # the other two cells stay blank


def test_motion_zk_static_dot_cue_marks_one_patch():
    env = MotionZKEnv(curriculum=False)
    env.reset()
    obs, _, _, _ = env.step(0)                                  # t=1 cue frame
    r0, r1, c0, c1 = env.cells[env.cue_index]
    rf0, rf1, cf0, cf1 = env.cells[env.foil_index]
    assert obs[r0:r1, c0:c1, :].sum() > 0                       # cued patch shows the static-dot cue
    assert obs[rf0:rf1, cf0:cf1, :].sum() == 0                 # foil patch is blank at cue time


def test_motion_zk_registered():
    env = make_env("motion_zk", curriculum=False)
    assert isinstance(env, MotionZKEnv) and env.action_space.n == 2
    obs = env.reset(); assert obs.shape == (env.S, env.S, 3)


def test_vda4_pays_cue_colour_value_unchanged():
    """Regression: the already-trained VDA task still pays the cue-colour value on a hit."""
    env = VDAEnv(curriculum=False)
    _force_trial(env, 1, 0, 0)
    env.cue_color = "red"                                        # red=5 by default color_values
    r, _ = _run(env, declare_at=5)
    assert r == 5.0
