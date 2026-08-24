"""
v7 ChangeDetectionEnv — cued-SIDE change detection with DISTRACTOR changes.

The cue's meaning is upgraded from v5_part2's "where the change will probably
be" to "which SIDE is response-relevant":

  * Cue at S1 (top-left, cue_position='left')  → respond ONLY to LEFT-side
    changes (S1 top / S2 bottom). The ring proportion is the probability that
    the target change (if this is a change trial) occurs at S1; otherwise it
    occurs at S2 — i.e. the proportion now distributes the target WITHIN the
    cued side.
  * Cue at S4 (bottom-right, cue_position='right') → mirrored: respond only to
    RIGHT-side changes; target at S4 with p=proportion, else S3.

  * DISTRACTOR: independently of the target, the UNCUED side may also change.
    With probability ``distractor_prob`` (default 0.5) one of the two uncued-
    side quadrants (chosen uniformly) steps in orientation by an independently
    sampled magnitude U(−θ, θ) at an independently sampled change time from the
    same window. The distractor is rendered identically to a target change but
    must be IGNORED.

Reward is keyed to the TARGET change only (logic unchanged from v5_part2):
  * press while t < target change time            → 0, episode ends
      (this includes pressing in response to an earlier distractor change —
       the false-alarm trap the task is designed to create)
  * press at/after target change time, change trial → color reward, ends
  * press at/after that time on a no-target trial → 0, ends
  * timeout with no press and no target change    → color reward
      (correct rejection — granted even if a distractor changed and was
       correctly ignored)

Quadrant indices (unchanged): 0=S1 top-left, 1=S2 bottom-left,
2=S3 top-right, 3=S4 bottom-right. Left side = {0,1}, right side = {2,3}.
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces

# (primary, secondary) target quadrants per cue side, and the uncued side's pair.
SIDE_QUADRANTS = {
    'left':  {'primary': 0, 'secondary': 1, 'distractor': (2, 3)},
    'right': {'primary': 3, 'secondary': 2, 'distractor': (0, 1)},
}


class ChangeDetectionEnv(gym.Env):
    def __init__(
        self,
        theta=64,
        noise_multiplier=5.0,
        min_change_time: int = 11,
        max_change_time: int = 25,
        distractor_prob: float = 0.5,
    ):
        super().__init__()

        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(50, 50, 3), dtype=np.float32)

        self.min_change_time = int(min_change_time)
        self.max_change_time = int(max_change_time)
        if self.max_change_time < self.min_change_time:
            raise ValueError("max_change_time must be >= min_change_time")
        if self.min_change_time < 3:
            raise ValueError("min_change_time must be >= 3 (Gabor display starts at t=3)")
        if not 0.0 <= float(distractor_prob) <= 1.0:
            raise ValueError("distractor_prob must be in [0, 1]")
        self.distractor_prob = float(distractor_prob)

        self.T = 29
        self.change_time = self.min_change_time
        self.t = 0
        self.orientations = [
            np.random.uniform(0, 360),
            np.random.uniform(0, 360),
            np.random.uniform(0, 360),
            np.random.uniform(0, 360),
        ]

        self.cue_position = None
        self.cue_color = None
        self.theta = float(theta)
        self.noise_multiplier = float(noise_multiplier)
        self.color_rewards = {'red': 5, 'green': 3, 'blue': 1}

        # distractor state (populated by reset)
        self.distractor_true = 0
        self.distractor_time = self.min_change_time
        self.distractor_index = 2
        self.distractor_change = 0.0

    def reset(self):
        self.t = 0
        self.change_time = np.random.randint(
            self.min_change_time, self.max_change_time + 1
        )
        self.orientations = [
            np.random.uniform(0, 360),
            np.random.uniform(0, 360),
            np.random.uniform(0, 360),
            np.random.uniform(0, 360),
        ]
        self.change_true = 0 if np.random.rand() < 0.5 else 1
        self.orientation_change = np.random.uniform(-self.theta, self.theta)

        self.cue_position = 'left' if np.random.rand() < 0.5 else 'right'
        self.cue_color = np.random.choice(['red', 'green', 'blue'])
        self.proportions = [1.0, 0.75, 0.5, 0.25]
        self.proportion = np.random.choice(self.proportions)

        side = SIDE_QUADRANTS[self.cue_position]

        # Target change: ON THE CUED SIDE; at the cued quadrant with
        # p = proportion, otherwise at the other quadrant of the same side.
        if self.change_true == 1:
            if np.random.rand() < self.proportion:
                self.change_index = side['primary']
            else:
                self.change_index = side['secondary']

        # Distractor change: independent of the target, on the UNCUED side;
        # uniform over that side's two quadrants, independent magnitude and time.
        self.distractor_true = 1 if np.random.rand() < self.distractor_prob else 0
        self.distractor_time = np.random.randint(
            self.min_change_time, self.max_change_time + 1
        )
        self.distractor_change = np.random.uniform(-self.theta, self.theta)
        self.distractor_index = int(np.random.choice(side['distractor']))

        return self._next_observation()

    def _next_observation(self):
        observation = np.zeros((50, 50, 3))

        if self.t in [0, 2]:
            return np.zeros((50, 50, 3))

        if self.t == 1:
            return self._generate_cue()

        # Per-quadrant orientation offsets active at this frame.
        offsets = [0.0, 0.0, 0.0, 0.0]
        if self.t >= self.change_time and self.change_true == 1:
            offsets[self.change_index] += self.orientation_change
        if self.t >= self.distractor_time and self.distractor_true == 1:
            offsets[self.distractor_index] += self.distractor_change

        gabors = [
            self._generate_gabor(
                self.orientations[i] + offsets[i]
                + self.noise_multiplier * np.random.normal()
            )
            for i in range(4)
        ]

        observation[0:25, 0:25, :] = np.stack([gabors[0]] * 3, axis=-1)
        observation[0:25, 25:50, :] = np.stack([gabors[2]] * 3, axis=-1)
        observation[25:50, 0:25, :] = np.stack([gabors[1]] * 3, axis=-1)
        observation[25:50, 25:50, :] = np.stack([gabors[3]] * 3, axis=-1)

        return observation

    def _generate_cue(self):
        observation = np.zeros((50, 50, 3))
        cue = np.zeros((25, 25))

        cy, cx = np.ogrid[-12.5:12.5, -12.5:12.5]
        disc_radius = 8
        disc_mask = cx ** 2 + cy ** 2 <= disc_radius ** 2
        cue[disc_mask] = 1

        ring_outer_radius = 12
        ring_inner_radius = 10
        ring_mask = (
            (cx ** 2 + cy ** 2 <= ring_outer_radius ** 2)
            & (cx ** 2 + cy ** 2 >= ring_inner_radius ** 2)
        )

        angle_to_remove = 2 * np.pi * (1 - self.proportion)
        theta = np.arctan2(cy, cx) + np.pi
        ring_mask &= ~(theta < angle_to_remove)
        cue[ring_mask] = 1

        if self.cue_color == 'red':
            color_channels = [1.0, 0.0, 0.0]
        elif self.cue_color == 'green':
            color_channels = [0.0, 1.0, 0.0]
        elif self.cue_color == 'blue':
            color_channels = [0.0, 0.0, 1.0]
        else:
            color_channels = [1.0, 1.0, 1.0]

        cue_rgb = np.zeros((25, 25, 3))
        for i in range(3):
            cue_rgb[:, :, i] = cue * color_channels[i]

        if self.cue_position == 'left':
            observation[0:25, 0:25, :] = cue_rgb
        else:
            observation[25:50, 25:50, :] = cue_rgb

        return observation

    def _generate_gabor(self, orientation):
        x, y = np.meshgrid(np.linspace(-1, 1, 25), np.linspace(-1, 1, 25))
        d = np.sqrt(x * x + y * y)
        sigma, theta, Lambda, psi, gamma = 0.5, np.deg2rad(orientation), 0.3, 0, 1
        x_theta = x * np.cos(theta) + y * np.sin(theta)
        y_theta = -x * np.sin(theta) + y * np.cos(theta)
        gabor = np.exp(
            -0.5 * (x_theta ** 2 + y_theta ** 2 / gamma ** 2) / sigma ** 2
        ) * np.cos(2 * np.pi * x_theta / Lambda + psi)

        noise = np.random.uniform(-0.11, 0.11, size=gabor.shape)
        gabor[d > 0.5] = 0
        noise[d > 0.5] = 0
        return gabor + noise

    def step(self, action):
        # Reward is keyed to the TARGET change only. A press triggered by an
        # earlier DISTRACTOR change lands in the t_before < change_time branch
        # (false alarm: 0, episode ends) — the discrimination the task trains.
        t_before = int(self.t)
        self.t += 1

        reward = 0
        done = False

        observation = self._next_observation()

        if action == 1 and t_before < self.change_time:
            reward = 0
            done = True
        elif action == 1 and t_before >= self.change_time:
            if self.change_true == 1:
                reward = self.color_rewards.get(self.cue_color, 1)
            else:
                reward = 0
            done = True

        if self.t >= self.T:
            done = True
            if action == 0 and self.change_true == 0:
                reward = self.color_rewards.get(self.cue_color, 1)

        return observation, reward, done, {}

    def render(self):
        return None

    def close(self):
        pass
