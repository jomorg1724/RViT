import numpy as np
import gymnasium as gym
from gymnasium import spaces


class ChangeDetectionEnv(gym.Env):
    def __init__(
        self,
        theta=64,
        noise_multiplier=5.0,
        min_change_time: int = 11,
        max_change_time: int = 25,
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

        rand = np.random.rand()
        if self.change_true == 1:
            if self.cue_position == 'left':
                if rand < self.proportion:
                    self.change_index = 0
                else:
                    self.change_index = np.random.randint(3) + 1
            else:
                if rand < self.proportion:
                    self.change_index = 3
                else:
                    self.change_index = np.random.randint(3)

        return self._next_observation()

    def _next_observation(self):
        observation = np.zeros((50, 50, 3))

        if self.t in [0, 2]:
            return np.zeros((50, 50, 3))

        if self.t == 1:
            return self._generate_cue()

        gabor1 = self._generate_gabor(
            self.orientations[0] + self.noise_multiplier * np.random.normal()
        )
        gabor2 = self._generate_gabor(
            self.orientations[1] + self.noise_multiplier * np.random.normal()
        )
        gabor3 = self._generate_gabor(
            self.orientations[2] + self.noise_multiplier * np.random.normal()
        )
        gabor4 = self._generate_gabor(
            self.orientations[3] + self.noise_multiplier * np.random.normal()
        )

        if self.t >= self.change_time and self.change_true == 1:
            if self.change_index == 0:
                gabor1 = self._generate_gabor(
                    self.orientations[0] + self.orientation_change
                    + self.noise_multiplier * np.random.normal()
                )
            elif self.change_index == 1:
                gabor2 = self._generate_gabor(
                    self.orientations[1] + self.orientation_change
                    + self.noise_multiplier * np.random.normal()
                )
            elif self.change_index == 2:
                gabor3 = self._generate_gabor(
                    self.orientations[2] + self.orientation_change
                    + self.noise_multiplier * np.random.normal()
                )
            elif self.change_index == 3:
                gabor4 = self._generate_gabor(
                    self.orientations[3] + self.orientation_change
                    + self.noise_multiplier * np.random.normal()
                )

        observation[0:25, 0:25, :] = np.stack([gabor1, gabor1, gabor1], axis=-1)
        observation[0:25, 25:50, :] = np.stack([gabor3, gabor3, gabor3], axis=-1)
        observation[25:50, 0:25, :] = np.stack([gabor2, gabor2, gabor2], axis=-1)
        observation[25:50, 25:50, :] = np.stack([gabor4, gabor4, gabor4], axis=-1)

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
