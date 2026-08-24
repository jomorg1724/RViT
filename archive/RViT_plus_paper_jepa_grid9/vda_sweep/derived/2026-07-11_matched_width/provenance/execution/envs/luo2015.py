"""
Faithful Luo & Maunsell (2015 task / 2018 paper) sample--delay--test change-detection
environment. NO CUE — attention is driven purely by the reward structure, learned over
training, exactly as in the monkey task.

Task (STAR Methods, Luo & Maunsell 2018, Neuron 97:1382):
  - Two sample Gabors appear SIMULTANEOUSLY at two diametrically-opposed locations.
  - A delay (blank).
  - A single test Gabor appears at ONE randomly chosen location; it is the SAME (p=0.5)
    or CHANGED (p=0.5) in orientation relative to the sample that was at that location.
  - Report a change by declaring (saccade). SDT categories, per location:
      H  = declare on a changed test              (hit)
      M  = fail to declare on a changed test       (miss)
      FA = declare on an unchanged test            (false alarm)
      CR = withhold on an unchanged test           (correct rejection)
  - Each sample independently takes one of TWO orientations, randomized per trial, so
    both samples must be inspected and held in working memory (the tested location is
    not known in advance).
  - There is NO cue and NO validity ring. The physical display is symmetric.
  - Reward structure sets the attended location (learned, not cued):
      session='sensitivity': correct responses (H or CR) at the HIGH-VALUE location pay
        `high_reward`, elsewhere `low_reward` (higher AVERAGE reward -> higher d' there).
      session='criterion':   H pays `r_hit`, CR pays `r_cr` (same across locations);
        the H:CR ratio shifts the criterion c without moving d'.

DESIGN CHOICES (flagged): two locations are the top-left (0) and bottom-right (3) cells
of the 2x2 grid (diametrically opposed across centre; the other two cells stay blank,
so the conv front-end and 4-token model are reused unchanged). Timeline on the paper's
7 logical frames: samples at t=0,1 (both locations); blank delay at t=2; test at
t>=3 (one location), giving a response window. The change magnitude is `theta`
(curriculum-shrinkable), and the two orientations are {base, base+theta} with base
randomized per trial.
"""
from __future__ import annotations
import numpy as np

try:
    from .base import BaseChangeDetectionEnv
except ImportError:  # pragma: no cover
    from base import BaseChangeDetectionEnv  # type: ignore


class LuoMaunsell2015Env(BaseChangeDetectionEnv):
    LOC = [0, 3]                 # two diametrically-opposed locations on the 2x2 grid
    SAMPLE_FRAMES = (0, 1)       # both samples shown
    DELAY_FRAME = 2              # blank
    TEST_ONSET = 3               # test appears at t>=3 at ONE location (response window t3..T-1)

    def __init__(self, session: str = "sensitivity",
                 high_reward: float = 5.0, low_reward: float = 1.0,
                 r_hit: float = 1.0, r_cr: float = 1.0, high_loc: int = 0, **kw):
        if session not in ("sensitivity", "criterion"):
            raise ValueError("session must be 'sensitivity' or 'criterion'")
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        kw.setdefault("min_change_time", 5); kw.setdefault("max_change_time", 5)  # unused; keeps base happy
        self.session = session
        self.high_reward, self.low_reward = float(high_reward), float(low_reward)
        self.r_hit, self.r_cr = float(r_hit), float(r_cr)
        self.high_loc = int(high_loc)               # the high-value location (fixed; learned, NOT cued)
        # attrs referenced by _next_observation must exist before base __init__ calls reset()
        self.samp = {i: 0.0 for i in self.LOC}
        self.test_loc = self.LOC[0]; self.test_ori = 0.0; self.change_true = 0
        super().__init__(**kw)

    # ── trial setup: NO cue anywhere ──────────────────────────────────────────
    def reset(self):
        self.t = 0
        self._frame_cache = None
        theta = float(self.theta)                    # current change magnitude (curriculum)
        # each location has TWO orientations {base_i, base_i+theta}; the sample takes one,
        # base_i randomized per trial so the sample must be inspected (cannot use absolute angle).
        self.samp, base, hi = {}, {}, {}
        for i in self.LOC:
            base[i] = float(np.random.uniform(0, 360))
            hi[i] = bool(np.random.rand() < 0.5)
            self.samp[i] = base[i] + (theta if hi[i] else 0.0)
        self.test_loc = int(np.random.choice(self.LOC))
        self.change_true = int(np.random.rand() < 0.5)
        if self.change_true:                          # test = the OTHER orientation (differs by theta)
            self.test_ori = base[self.test_loc] + (0.0 if hi[self.test_loc] else theta)
        else:                                         # test = same as the sample at that location
            self.test_ori = self.samp[self.test_loc]
        self.high_value_index = self.high_loc
        return self._next_observation()

    def _draw_gabor(self, obs, cell_idx, orientation):
        r0, r1, c0, c1 = self.cells[cell_idx]
        ori = orientation + self.noise_multiplier * np.random.normal()
        g = self._gabor(ori, r1 - r0, c1 - c0)
        obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)

    def _next_observation(self):
        L = self.t // self.frame_repeat
        if self.frame_repeat > 1 and self.t % self.frame_repeat != 0 and self._frame_cache is not None:
            return self._frame_cache
        obs = np.zeros((self.S, self.S, 3), dtype=np.float32)
        if L in self.SAMPLE_FRAMES:                   # BOTH samples, no cue
            for i in self.LOC:
                self._draw_gabor(obs, i, self.samp[i])
        elif L >= self.TEST_ONSET:                    # test at ONE location only
            self._draw_gabor(obs, self.test_loc, self.test_ori)
        # else (delay) -> blank
        self._frame_cache = obs
        return obs

    # ── SDT reward: H/M/FA/CR, session-dependent magnitude ────────────────────
    def _correct_reward(self) -> float:
        """Reward for a CORRECT response (a hit or a correct rejection)."""
        if self.session == "sensitivity":
            return self.high_reward if self.test_loc == self.high_value_index else self.low_reward
        return self.r_hit if self.change_true == 1 else self.r_cr   # criterion: H vs CR ratio

    def step(self, action):
        L_before = self.t // self.frame_repeat
        self.t += 1
        reward, done = 0.0, False
        obs = self._next_observation()
        if action == 1:                               # declare ("saccade to the test")
            done = True
            if L_before >= self.TEST_ONSET and self.change_true == 1:
                reward = self._correct_reward()        # HIT
            else:
                reward = 0.0                           # FALSE ALARM (or premature)
        if self.t >= self.T and not done:
            done = True
            if self.change_true == 0:
                reward = self._correct_reward()        # CORRECT REJECTION
            else:
                reward = 0.0                           # MISS
        if done and self.curriculum:
            self._update_curriculum(reward > 0)
        return obs, reward, done, {"theta": self.theta, "correct": float(reward > 0),
                                   "test_loc": self.test_loc, "change": self.change_true,
                                   "high_value_index": self.high_value_index}


class LuoMaunsell2015Sensitivity(LuoMaunsell2015Env):
    def __init__(self, **kw):
        kw.setdefault("session", "sensitivity"); super().__init__(**kw)


class LuoMaunsell2015Criterion(LuoMaunsell2015Env):
    def __init__(self, **kw):
        kw.setdefault("session", "criterion"); super().__init__(**kw)
