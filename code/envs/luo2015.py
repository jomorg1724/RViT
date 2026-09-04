"""Compact Luo & Maunsell (2015) reward-dissociation task analogue.

The primary protocol source is Luo & Maunsell (2015, Neuron 86:1182--1188), with
the related 2018 LPFC experiment as an extension. There is no visual value cue. Two
simultaneous sample Gabors occupy opposite locations; each sample orientation is drawn
independently and uniformly over the axial Gabor domain [0°, 180°). After a delay, one location is
tested with the same orientation or with a signed change drawn from the current curriculum range. A declaration to
the first test is a hit or false alarm. On no-change trials, withholding is verified by
a required declaration to a guaranteed changed second test; failure to answer that test
is excluded from SDT, as in the paper.

The published reward structure is spatially counterphased between conditions:
  * sensitivity: mean reward 5 versus 1, with H:CR ratios 0.7 and 1.1;
  * criterion: low-c H:CR ratio 1.5 at 90% of the high-c mean reward, versus
    high-c H:CR ratio 0.5.

The published sensitivity ratios are the *averaged outputs* of a per-location titration
L&M ran until each animal's criterion was unbiased, not settings they started from. They
are therefore the defaults of `high_hit_cr_ratio` / `low_hit_cr_ratio` rather than
constants: holding them fixed forces a nonzero reward-optimal criterion difference
(beta* = R_CR/R_hit, c* = ln beta* / d'), while ratio 1 at both locations makes
ln beta* = 0 and the reward-optimal criterion zero at both locations for any pair of d'
values. Overriding them leaves the mean reward, and hence the 5:1 value manipulation,
untouched.

This is a scaled seven-frame computational analogue, not a millisecond-exact monkey
apparatus: sample frames 0--1, delay 2, first-test response window 3--4, inter-test gap
5, and second test 6. Locations are top-left (0) and bottom-right (3) in the existing
2x2 model grid; action 1 stands in for the test-directed saccade. Pixel/orientation
noise is an explicit model-side approximation to sensory variability.
"""
from __future__ import annotations
import numpy as np

try:
    from .base import BaseChangeDetectionEnv, cell_bounds
except ImportError:  # pragma: no cover
    from base import BaseChangeDetectionEnv, cell_bounds  # type: ignore


class LuoMaunsell2015Env(BaseChangeDetectionEnv):
    LOC = [0, 3]                 # two diametrically-opposed locations on the 2x2 grid
    SAMPLE_FRAMES = (0, 1)       # both samples shown
    DELAY_FRAME = 2              # blank
    FIRST_TEST_ONSET = 3
    FIRST_TEST_END = 4
    INTERTEST_FRAME = 5
    SECOND_TEST_ONSET = 6
    TEST_ONSET = FIRST_TEST_ONSET  # backward-compatible alias used by analysis code

    def __init__(self, session: str = "sensitivity",
                 high_reward: float = 5.0, low_reward: float = 1.0,
                 high_hit_cr_ratio: float = 0.7, low_hit_cr_ratio: float = 1.1,
                 r_hit: float | None = None, r_cr: float | None = None,
                 high_loc: int = 0, condition_loc: int | None = None,
                 spatial_grid_size: int = 2, **kw):
        if session not in ("sensitivity", "criterion"):
            raise ValueError("session must be 'sensitivity' or 'criterion'")
        logical_rows = int(kw.setdefault("grid_rows", 2))
        logical_cols = int(kw.setdefault("grid_cols", 2))
        if (logical_rows, logical_cols) != (2, 2):
            raise ValueError("Luo logical stimulus locations must remain on the 2x2 task grid")
        self.spatial_grid_size = int(spatial_grid_size)
        if self.spatial_grid_size not in (2, 4):
            raise ValueError("spatial_grid_size must be 2 or 4")
        expected_image_size = 25 * self.spatial_grid_size
        requested_image_size = int(kw.get("image_size", expected_image_size))
        if requested_image_size != expected_image_size:
            raise ValueError(
                f"spatial_grid_size={self.spatial_grid_size} requires "
                f"image_size={expected_image_size}"
            )
        kw["image_size"] = expected_image_size

        # The 4x4 layout center-pads the exact legacy 50x50 scene. Logical location
        # IDs stay {0, 3}, while the two unchanged 25x25 stimulus cells occupy the
        # central diagonal patches {5, 10}; the other 12 patches remain blank.
        offset = (self.spatial_grid_size - 2) // 2
        patch_rc = {0: (offset, offset), 3: (offset + 1, offset + 1)}
        rb = cell_bounds(expected_image_size, self.spatial_grid_size)
        cb = cell_bounds(expected_image_size, self.spatial_grid_size)
        self.stimulus_patch_indices = {
            loc: row * self.spatial_grid_size + col
            for loc, (row, col) in patch_rc.items()
        }
        self.stimulus_cells = {
            loc: (rb[row][0], rb[row][1], cb[col][0], cb[col][1])
            for loc, (row, col) in patch_rc.items()
        }
        kw.setdefault("value_cues", False)
        kw.setdefault("curriculum", False)
        kw.setdefault("min_change_time", 5); kw.setdefault("max_change_time", 5)  # unused; keeps base happy
        self.session = session
        self.high_reward, self.low_reward = float(high_reward), float(low_reward)
        # Titratable per-location H:CR ratios; defaults reproduce the published averages.
        # _hit_cr_pair divides by (1 + ratio) and scales the hit by it, so a ratio at or
        # below zero is degenerate (unrewarded hits) or singular.
        for _name, _value in (("high_hit_cr_ratio", high_hit_cr_ratio),
                              ("low_hit_cr_ratio", low_hit_cr_ratio)):
            if not float(_value) > 0.0:
                raise ValueError(f"{_name} must be positive, got {_value!r}")
        self.high_hit_cr_ratio = float(high_hit_cr_ratio)
        self.low_hit_cr_ratio = float(low_hit_cr_ratio)
        if (r_hit is None) != (r_cr is None):
            raise ValueError("r_hit and r_cr must be provided together")
        self.r_hit = None if r_hit is None else float(r_hit)
        self.r_cr = None if r_cr is None else float(r_cr)
        self.high_loc = int(high_loc if condition_loc is None else condition_loc)
        self.reward_table: dict[int, tuple[float, float]] = {}
        self.set_condition(self.high_loc)
        # attrs referenced by _next_observation must exist before base __init__ calls reset()
        self.samp = {i: 0.0 for i in self.LOC}
        self.test_loc = self.LOC[0]
        self.test_ori = 0.0
        self.second_test_ori = 0.0
        self.change_true = 0
        super().__init__(**kw)
        if self.n_logical < self.SECOND_TEST_ONSET + 1:
            raise ValueError("Luo task requires at least 7 logical frames")

    @staticmethod
    def _hit_cr_pair(mean_reward: float, hit_cr_ratio: float) -> tuple[float, float]:
        correct_rejection = 2.0 * mean_reward / (1.0 + hit_cr_ratio)
        return hit_cr_ratio * correct_rejection, correct_rejection

    def set_condition(self, condition_loc: int) -> None:
        """Counterphase the published reward schedule between the two locations."""
        condition_loc = int(condition_loc)
        if condition_loc not in self.LOC:
            raise ValueError(f"condition_loc must be one of {self.LOC}")
        other_loc = self.LOC[1] if condition_loc == self.LOC[0] else self.LOC[0]
        self.high_loc = condition_loc
        self.high_value_index = condition_loc
        if self.session == "sensitivity":
            self.reward_table = {
                condition_loc: self._hit_cr_pair(self.high_reward, self.high_hit_cr_ratio),
                other_loc: self._hit_cr_pair(self.low_reward, self.low_hit_cr_ratio),
            }
        elif self.r_hit is not None and self.r_cr is not None:
            self.reward_table = {
                condition_loc: (self.r_hit, self.r_cr),
                other_loc: (self.r_cr, self.r_hit),
            }
        else:
            self.reward_table = {
                condition_loc: self._hit_cr_pair(0.9, 1.5),
                other_loc: self._hit_cr_pair(1.0, 0.5),
            }

    # ── trial setup: NO cue anywhere ──────────────────────────────────────────
    def reset(self):
        self.t = 0
        self._frame_cache = None
        theta = float(self.theta)                    # current max |change| (curriculum)
        # Axial Gabor orientations are 180° periodic. Both samples are fresh,
        # independent Uniform[0°, 180°) draws on every trial; theta must not affect them.
        self.samp = {
            location: float(np.random.uniform(0.0, 180.0))
            for location in self.LOC
        }
        self.test_loc = int(np.random.choice(self.LOC))
        self.change_true = int(np.random.rand() < 0.5)
        # Match the logged curriculum contract: theta is a bound, not a fixed
        # separation. One signed offset is sampled per trial and reused for the
        # changed first test or the guaranteed-changed second test.
        self.orientation_change = float(np.random.uniform(-theta, theta))
        if self.change_true:
            self.test_ori = self.samp[self.test_loc] + self.orientation_change
        else:
            self.test_ori = self.samp[self.test_loc]
        self.second_test_ori = self.samp[self.test_loc] + self.orientation_change
        self.high_value_index = self.high_loc
        return self._next_observation()

    def _draw_gabor(self, obs, cell_idx, orientation):
        r0, r1, c0, c1 = self.stimulus_cells[cell_idx]
        ori = orientation + self.noise_multiplier * np.random.normal()
        g = self._gabor(ori, r1 - r0, c1 - c0)
        obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)

    def _draw_fixation(self, obs):
        center = self.S // 2
        obs[center - 1:center + 1, center - 1:center + 1, :] = 1.0

    def _next_observation(self):
        L = self.t // self.frame_repeat
        if self.frame_repeat > 1 and self.t % self.frame_repeat != 0 and self._frame_cache is not None:
            return self._frame_cache
        obs = np.zeros((self.S, self.S, 3), dtype=np.float32)
        if L in self.SAMPLE_FRAMES:                   # BOTH samples, no cue
            for i in self.LOC:
                self._draw_gabor(obs, i, self.samp[i])
        elif self.FIRST_TEST_ONSET <= L <= self.FIRST_TEST_END:
            self._draw_gabor(obs, self.test_loc, self.test_ori)
        elif L >= self.SECOND_TEST_ONSET and self.change_true == 0:
            self._draw_gabor(obs, self.test_loc, self.second_test_ori)
        self._draw_fixation(obs)
        self._frame_cache = obs
        return obs

    def render_trial(self) -> np.ndarray:
        """Render the complete physical-frame sequence without applying actions."""
        saved_t, saved_cache = self.t, self._frame_cache
        self._frame_cache = None
        frames = []
        try:
            for physical_t in range(self.T):
                self.t = physical_t
                frames.append(self._next_observation().copy())
        finally:
            self.t, self._frame_cache = saved_t, saved_cache
        return np.stack(frames)

    def training_state_dict(self) -> dict:
        state = super().training_state_dict()
        state["environment_config"].update({
            "session": self.session,
            "condition_loc": self.high_loc,
            "reward_table": dict(self.reward_table),
            "high_hit_cr_ratio": self.high_hit_cr_ratio,
            "low_hit_cr_ratio": self.low_hit_cr_ratio,
            "orientation_sampling": "independent_uniform_axial_0_180",
            "orientation_period_degrees": 180.0,
            "spatial_grid_size": self.spatial_grid_size,
            "stimulus_patch_indices": dict(self.stimulus_patch_indices),
            "stimulus_cells": dict(self.stimulus_cells),
            "first_test_onset": self.FIRST_TEST_ONSET,
            "first_test_end": self.FIRST_TEST_END,
            "second_test_onset": self.SECOND_TEST_ONSET,
        })
        return state

    # ── SDT reward: H/M/FA/CR, session-dependent magnitude ────────────────────
    def _correct_reward(self) -> float:
        hit_reward, correct_rejection_reward = self.reward_table[self.test_loc]
        reward = hit_reward if self.change_true == 1 else correct_rejection_reward
        return self.reward_scale * reward

    def step(self, action):
        L_before = self.t // self.frame_repeat
        self.t += 1
        reward, done = 0.0, False
        outcome = "in_progress"
        valid_sdt = False
        obs = self._next_observation()
        if action == 1 and self.FIRST_TEST_ONSET <= L_before <= self.FIRST_TEST_END:
            done = True
            valid_sdt = True
            if self.change_true == 1:
                outcome = "hit"
                reward = self._correct_reward()
            else:
                outcome = "false_alarm"
        elif action == 1 and L_before >= self.SECOND_TEST_ONSET and self.change_true == 0:
            done = True
            valid_sdt = True
            outcome = "correct_rejection"
            reward = self._correct_reward()
        elif action == 1:
            done = True
            outcome = "fixation_break"

        leaving_first_test = (
            L_before == self.FIRST_TEST_END and self.t % self.frame_repeat == 0
        )
        if not done and leaving_first_test and self.change_true == 1:
            done = True
            valid_sdt = True
            outcome = "miss"
        elif not done and self.t >= self.T:
            done = True
            outcome = "second_test_miss" if self.change_true == 0 else "miss"
            valid_sdt = self.change_true == 1

        if done and self.curriculum and valid_sdt:
            self._update_curriculum(reward > 0)
        return obs, reward, done, {
            "theta": self.theta,
            "correct": float(outcome in ("hit", "correct_rejection")),
            "test_loc": self.test_loc,
            "change": self.change_true,
            "high_value_index": self.high_value_index,
            "outcome": outcome,
            "valid_sdt": valid_sdt,
        }


class LuoMaunsell2015Sensitivity(LuoMaunsell2015Env):
    def __init__(self, **kw):
        kw.setdefault("session", "sensitivity"); super().__init__(**kw)


class LuoMaunsell2015Criterion(LuoMaunsell2015Env):
    def __init__(self, **kw):
        kw.setdefault("session", "criterion"); super().__init__(**kw)
