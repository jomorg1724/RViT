"""
Shared base for the RViT+ FiLM task battery.

BaseChangeDetectionEnv generalises the published cued orientation-change-detection
task to an arbitrary grid_rows × grid_cols stimulus array (one Gabor per cell, indexed
ROW-MAJOR so token i ⇔ stimulus i in the conv front-end), with a cue that marks one
cell and shows its reliability (ring completeness = proportion = validity) and,
optionally, its value (colour). Subclasses override only the reward / target / response
rules to realise the specific battery tasks.

Trial timeline (T steps): t=0,2 blank · t=1 cue · t≥3 Gabors (orientation noise every
frame) · at change_time∈[min,max] one stimulus steps by Δ (50% of trials are change
trials). Actions: 0=wait, 1=declare change.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import gymnasium as gym
from gymnasium import spaces

COLOR_RGB = {"red": (1.0, 0.0, 0.0), "green": (0.0, 1.0, 0.0),
             "blue": (0.0, 0.0, 1.0), "white": (1.0, 1.0, 1.0)}


def cell_bounds(extent: int, n: int):
    edges = np.linspace(0, extent, n + 1).round().astype(int)
    return [(int(edges[i]), int(edges[i + 1])) for i in range(n)]


class BaseChangeDetectionEnv(gym.Env):
    def __init__(
        self,
        grid_rows: int = 2,
        grid_cols: int = 2,
        theta: float = 65.0,                  # paper: Δ ~ U(−k,k), k starts at 65
        noise_multiplier: float = 5.0,
        cue_positions=None,                   # restrict the cue to these stim indices (paper: S1/S4)
        # Paper timeline: 7 steps (t=0 black, t=1 cue, t=2 black, t=3-6 stimuli) with the
        # change FIXED at t=5. (Set min<max and a larger T for the longer random-onset
        # variant.)
        min_change_time: int = 5,
        max_change_time: int = 5,
        T: int = 7,
        proportions=(0.25, 0.5, 0.75, 1.0),
        value_cues: bool = False,
        color_values=None,
        image_size: int = 50,
        # Curriculum on the orientation-change magnitude (paper: start large/easy and
        # SHRINK Δ as performance improves, to make detection progressively harder).
        # `self.theta` is the current max |Δ| — the harness logs it each iteration.
        curriculum: bool = True,
        curr_window: int = 200,
        curr_threshold: float = 0.85,
        curr_decay: float = 0.9,
        theta_floor: float = 8.0,
    ) -> None:
        super().__init__()
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(image_size, image_size, 3),
                                            dtype=np.float32)
        self.grid_rows, self.grid_cols = int(grid_rows), int(grid_cols)
        self.n_stim = self.grid_rows * self.grid_cols
        self.cue_positions = list(cue_positions) if cue_positions else list(range(self.n_stim))
        self.theta = float(theta)
        self.noise_multiplier = float(noise_multiplier)
        self.min_change_time, self.max_change_time = int(min_change_time), int(max_change_time)
        if self.min_change_time < 3:
            raise ValueError("min_change_time must be >= 3 (Gabors start at t=3)")
        self.T = int(T)
        self.S = int(image_size)
        self.proportions = list(proportions)
        self.value_cues = bool(value_cues)
        self.color_values = dict(color_values) if color_values else {"red": 5, "green": 3, "blue": 1}
        self.curriculum = bool(curriculum)
        self.theta_start = float(theta)
        self.theta_floor = float(theta_floor)
        self.curr_window = int(curr_window)
        self.curr_threshold = float(curr_threshold)
        self.curr_decay = float(curr_decay)
        self._recent_correct: list = []
        self._rb = cell_bounds(self.S, self.grid_rows)
        self._cb = cell_bounds(self.S, self.grid_cols)
        self.cells = [(r0, r1, c0, c1) for (r0, r1) in self._rb for (c0, c1) in self._cb]
        self.t = 0
        self.reset()

    # ── trial setup ─────────────────────────────────────────────────────────
    def reset(self):
        self.t = 0
        self.change_time = np.random.randint(self.min_change_time, self.max_change_time + 1)
        self.orientations = [np.random.uniform(0, 360) for _ in range(self.n_stim)]
        self.change_true = int(np.random.rand() >= 0.5)
        self.orientation_change = np.random.uniform(-self.theta, self.theta)
        self.cue_index = int(np.random.choice(self.cue_positions))
        self.proportion = float(np.random.choice(self.proportions))
        if self.value_cues:
            self.cue_color = str(np.random.choice(list(self.color_values.keys())))
        else:
            self.cue_color = "white"
        self.change_index = self._draw_change_index()
        self.valid = int(self.change_true == 1 and self.change_index == self.cue_index)
        return self._next_observation()

    def _draw_change_index(self) -> int:
        """Where the change occurs on a change trial (cued w.p. proportion else uniform)."""
        if self.change_true == 0:
            return -1
        if np.random.rand() < self.proportion:
            return self.cue_index
        return int(np.random.randint(self.n_stim))

    # ── rendering ─────────────────────────────────────────────────────────────
    def _next_observation(self):
        obs = np.zeros((self.S, self.S, 3), dtype=np.float32)
        if self.t in (0, 2):
            return obs
        if self.t == 1:
            return self._render_cue(obs)
        for i, (r0, r1, c0, c1) in enumerate(self.cells):
            ori = self.orientations[i] + self.noise_multiplier * np.random.normal()
            if self.t >= self.change_time and self.change_true == 1 and self.change_index == i:
                ori += self.orientation_change
            g = self._gabor(ori, r1 - r0, c1 - c0)
            obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)
        return obs

    def _render_cue(self, obs):
        r0, r1, c0, c1 = self.cells[self.cue_index]
        h, w = r1 - r0, c1 - c0
        n = min(h, w)
        yy, xx = np.ogrid[0:h, 0:w]                      # match the actual (h, w) cell
        cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
        rr = (xx - cx) ** 2 + (yy - cy) ** 2
        disc_r = 0.32 * n
        ring_in, ring_out = 0.40 * n, 0.48 * n
        cue = np.zeros((h, w), dtype=np.float32)
        cue[rr <= disc_r ** 2] = 1.0
        ring = (rr <= ring_out ** 2) & (rr >= ring_in ** 2)
        ang = np.arctan2(yy - cy, xx - cx) + np.pi
        ring &= ~(ang < 2 * np.pi * (1 - self.proportion))
        cue[ring] = 1.0
        rgb = COLOR_RGB.get(self.cue_color, (1.0, 1.0, 1.0))
        for k in range(3):
            obs[r0:r1, c0:c1, k] = cue * rgb[k]
        return obs

    def _gabor(self, orientation, h, w):
        x, y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
        d = np.sqrt(x * x + y * y)
        sigma, th, Lambda, psi, gamma = 0.5, np.deg2rad(orientation), 0.3, 0, 1
        xt = x * np.cos(th) + y * np.sin(th)
        yt = -x * np.sin(th) + y * np.cos(th)
        g = np.exp(-0.5 * (xt ** 2 + yt ** 2 / gamma ** 2) / sigma ** 2) * np.cos(2 * np.pi * xt / Lambda + psi)
        noise = np.random.uniform(-0.11, 0.11, size=g.shape)
        g[d > 0.5] = 0.0; noise[d > 0.5] = 0.0
        return (g + noise).astype(np.float32)

    # ── reward (overridable hooks) ────────────────────────────────────────────
    def _reward_value(self) -> float:
        """Reward for a correct response on this trial."""
        if self.value_cues:
            return float(self.color_values.get(self.cue_color, 1))
        return 1.0

    def _is_reportable_change(self) -> bool:
        """Whether the change on this trial should be reported (True for plain
        detection; subclasses restrict it, e.g. Krauzlis = cued only)."""
        return self.change_true == 1

    def step(self, action):
        t_before = int(self.t)
        self.t += 1
        reward, done = 0.0, False
        obs = self._next_observation()
        if action == 1:
            done = True
            if t_before >= self.change_time and self._is_reportable_change():
                reward = self._reward_value()
            else:
                reward = 0.0                                # premature / false alarm
        if self.t >= self.T and not done:
            done = True
            if self.change_true == 0:                       # correct rejection
                reward = self._reward_value()
        if done and self.curriculum:
            self._update_curriculum(reward > 0)
        return obs, reward, done, {"theta": self.theta, "correct": float(reward > 0)}

    def _update_curriculum(self, correct: bool) -> None:
        """Shrink the max orientation change once a window of trials clears threshold."""
        self._recent_correct.append(bool(correct))
        if len(self._recent_correct) >= self.curr_window:
            acc = sum(self._recent_correct) / len(self._recent_correct)
            if acc >= self.curr_threshold:
                self.theta = max(self.theta_floor, self.theta * self.curr_decay)
            self._recent_correct = []

    def render(self):
        return None

    def close(self):
        pass
