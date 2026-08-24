"""Set-size-9 cued change-detection environment (distractor-free, uniform reward).

Nine Gabor patches are shown in a 3x3 grid. On half of trials, exactly one of them
(the TARGET) steps its orientation at a random change time; every change is task-
relevant (there is no distractor). A cue marks one of the nine locations and, through
the completeness of a ring, displays its RELIABILITY (proportion). On a change trial
the target is at the cued location with probability `proportion`, otherwise uniformly
over all nine — so proportion 0 is an uninformative cue (uniform over all stimuli) and
proportion 1 is a perfectly valid cue. Reward is uniform: a correct detection (or a
correct rejection on a no-change trial) yields 1, regardless of cue/location.

This is the set-size manipulation: relative to the 4-stimulus task, knowing where to
look should be worth more, so the validity benefit is predicted to grow.

Grid indexing (row-major): 0,1,2 = top row; 3,4,5 = middle; 6,7,8 = bottom.
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces

N_STIMULI = 9
GRID = 3
CELL_CENTERS = [8, 25, 42]                       # 50*(2k+1)/6 rounded, for k=0,1,2
STIM_CENTERS = [(CELL_CENTERS[i // GRID], CELL_CENTERS[i % GRID]) for i in range(N_STIMULI)]
PATCH = 15                                       # Gabor / cue patch size (radius ~7, no overlap)


class ChangeDetectionEnv(gym.Env):
    def __init__(self, theta=64, noise_multiplier=5.0, min_change_time=11, max_change_time=25):
        super().__init__()
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(50, 50, 3), dtype=np.float32)
        self.min_change_time = int(min_change_time)
        self.max_change_time = int(max_change_time)
        if self.max_change_time < self.min_change_time:
            raise ValueError("max_change_time must be >= min_change_time")
        if self.min_change_time < 3:
            raise ValueError("min_change_time must be >= 3 (Gabors start at t=3)")
        self.T = 29
        self.theta = float(theta)
        self.noise_multiplier = float(noise_multiplier)
        self.proportions = [0.0, 0.25, 0.5, 0.75, 1.0]   # FIVE levels incl. the uninformative 0
        self.n_stimuli = N_STIMULI
        self.t = 0
        self.change_time = self.min_change_time
        self.orientations = [np.random.uniform(0, 360) for _ in range(N_STIMULI)]
        self.cue_index = 0

    def reset(self):
        self.t = 0
        self.change_time = np.random.randint(self.min_change_time, self.max_change_time + 1)
        self.orientations = [np.random.uniform(0, 360) for _ in range(N_STIMULI)]
        self.change_true = 0 if np.random.rand() < 0.5 else 1
        self.orientation_change = np.random.uniform(-self.theta, self.theta)

        self.cue_index = int(np.random.randint(N_STIMULI))      # cue marks one of nine locations
        self.proportion = float(np.random.choice(self.proportions))

        # target location: cued with prob `proportion`, else uniform over ALL nine
        # (so proportion 0 -> uniform over the whole array).
        if self.change_true == 1:
            if np.random.rand() < self.proportion:
                self.change_index = self.cue_index
            else:
                self.change_index = int(np.random.randint(N_STIMULI))
        else:
            self.change_index = -1
        self.valid = int(self.change_true == 1 and self.change_index == self.cue_index)
        return self._next_observation()

    def _place(self, obs, patch, cy, cx):
        h = PATCH // 2
        obs[cy - h:cy + h + 1, cx - h:cx + h + 1, :] += patch

    def _next_observation(self):
        if self.t in (0, 2):
            return np.zeros((50, 50, 3))
        if self.t == 1:
            return self._generate_cue()
        obs = np.zeros((50, 50, 3))
        for i in range(N_STIMULI):
            ori = self.orientations[i] + self.noise_multiplier * np.random.normal()
            if self.t >= self.change_time and self.change_true == 1 and self.change_index == i:
                ori += self.orientation_change
            g = self._generate_gabor(ori)
            cy, cx = STIM_CENTERS[i]
            self._place(obs, np.stack([g, g, g], axis=-1), cy, cx)
        return obs

    def _generate_cue(self):
        obs = np.zeros((50, 50, 3))
        n = PATCH
        cy0, cx0 = np.ogrid[-(n // 2):(n // 2) + 1, -(n // 2):(n // 2) + 1]
        r2 = cx0 ** 2 + cy0 ** 2
        cue = np.zeros((n, n))
        cue[r2 <= 4 ** 2] = 1.0                                  # filled disc = location marker
        ring = (r2 <= 7 ** 2) & (r2 >= 5 ** 2)                   # ring arc = reliability
        ang = np.arctan2(cy0 * np.ones_like(cx0), cx0 * np.ones_like(cy0)) + np.pi
        ring &= ~(ang < 2 * np.pi * (1 - self.proportion))      # completeness = proportion
        cue[ring] = 1.0
        cy, cx = STIM_CENTERS[self.cue_index]
        self._place(obs, np.stack([cue, cue, cue], axis=-1), cy, cx)   # white cue (uniform reward)
        return obs

    def _generate_gabor(self, orientation):
        x, y = np.meshgrid(np.linspace(-1, 1, PATCH), np.linspace(-1, 1, PATCH))
        d = np.sqrt(x * x + y * y)
        sigma, theta, Lambda, psi, gamma = 0.5, np.deg2rad(orientation), 0.3, 0, 1
        xt = x * np.cos(theta) + y * np.sin(theta)
        yt = -x * np.sin(theta) + y * np.cos(theta)
        gabor = np.exp(-0.5 * (xt ** 2 + yt ** 2 / gamma ** 2) / sigma ** 2) * np.cos(2 * np.pi * xt / Lambda + psi)
        noise = np.random.uniform(-0.11, 0.11, size=gabor.shape)
        gabor[d > 0.5] = 0
        noise[d > 0.5] = 0
        return gabor + noise

    def step(self, action):
        t_before = int(self.t)
        self.t += 1
        reward = 0.0
        done = False
        observation = self._next_observation()
        if action == 1 and t_before < self.change_time:
            reward = 0.0; done = True                            # false alarm
        elif action == 1 and t_before >= self.change_time:
            reward = 1.0 if self.change_true == 1 else 0.0       # uniform hit reward / FA on no-change
            done = True
        if self.t >= self.T:
            done = True
            if action == 0 and self.change_true == 0:
                reward = 1.0                                      # correct rejection
        return observation, reward, done, {}

    def render(self):
        return None

    def close(self):
        pass
