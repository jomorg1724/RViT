"""
The RViT+ FiLM task battery — thin subclasses of BaseChangeDetectionEnv. Each realises
one paradigm by overriding only the reward / target / response rules.

  Validity4Env   — canonical K=4 cued change detection, UNIFORM reward (reproduces the
                   published main result; validity via ring completeness).
  VDAEnv         — value-directed: coloured value cue (red/green/blue → reward), so the
                   cue carries BOTH validity (ring) and value (colour).
  SetSizeEnv(K)  — set-size manipulation K∈{2,4,9} (grids 1×2 / 2×2 / 3×3), uniform
                   reward; the K-scaling test (Paper-B set-size prediction, deferred but
                   the env is ready).
  LuoMaunsellEnv — reward-STRUCTURE sessions: 'sensitivity' (value concentrated at one
                   location) vs 'criterion' (hit↔correct-reject reward ratio), plus a
                   response window. Engages the Luo & Maunsell d′-vs-criterion result.
  KrauzlisEnv    — attend-here/ignore-here: ONLY a change at the cued location is
                   reportable; uncued changes must be ignored (∂EV/∂HR_uncued = 0).
"""
from __future__ import annotations

import numpy as np
from gymnasium import spaces

try:
    from .base import BaseChangeDetectionEnv, COLOR_RGB
except ImportError:  # pragma: no cover
    from base import BaseChangeDetectionEnv, COLOR_RGB  # type: ignore[no-redef]


class Validity4Env(BaseChangeDetectionEnv):
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        kw.setdefault("cue_positions", [0, 3])      # paper: cue at S1 (top-left) or S4 (bottom-right)
        kw.setdefault("exclude_cued_in_uniform", True)   # displayed ring proportion == true P(change@cued)
        super().__init__(**kw)


class VDAEnv(BaseChangeDetectionEnv):
    """Value-directed attention: coloured value cue + validity ring."""
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", True)
        super().__init__(**kw)


class SetSizeEnv(BaseChangeDetectionEnv):
    """Set-size K via grid: 2→1×2, 4→2×2, 9→3×3 (uniform reward)."""
    _GRIDS = {2: (1, 2), 4: (2, 2), 9: (3, 3), 6: (2, 3), 16: (4, 4)}

    def __init__(self, set_size: int = 4, **kw):
        if set_size not in self._GRIDS:
            raise ValueError(f"set_size must be one of {sorted(self._GRIDS)}")
        gr, gc = self._GRIDS[set_size]
        kw["grid_rows"], kw["grid_cols"] = gr, gc
        kw.setdefault("value_cues", False)
        kw.setdefault("proportions", (0.0, 0.25, 0.5, 0.75, 1.0))   # 0 = uninformative
        self.set_size = set_size
        super().__init__(**kw)


class LuoMaunsellEnv(BaseChangeDetectionEnv):
    """Luo & Maunsell (2015/2018) criterion-vs-sensitivity DISSOCIATION task. The defining feature of
    this paradigm is that the PHYSICAL stimulus is held IDENTICAL across conditions — BOTH SDT
    quantities are moved purely through REWARD, which is exactly what removes the discriminability
    confound of the standard Posner task:

    session='sensitivity': the AVERAGE REWARD per location differs — the cued (attended) location
        pays `v_high`, the others `v_low`, applied equally to hits and correct rejections (so the
        H:CR ratio stays 1 and criterion is NOT moved). Higher expected value at the attended token
        drives the policy to allocate more sensitivity (d') there. Pixels are IDENTICAL everywhere.
    session='criterion': the average reward per location is uniform, but the hit-vs-correct-reject
        reward RATIO (r_hit : r_cr) is asymmetric, shifting the criterion (bias) without changing d'.

    (An earlier version raised d' by enlarging the physical orientation change at the cued cell —
    that is the stimulus-discriminability confound the dissociation task was designed to eliminate,
    so it was replaced by the reward-based mechanism the paper actually uses.)

    response_window: a change must be declared within this many LOGICAL frames of change onset, else
    the trial expires as a miss (event-locked response)."""
    def __init__(self, session: str = "sensitivity",
                 v_high: float = 5.0, v_low: float = 1.0,
                 r_hit: float = 2.0, r_cr: float = 1.0,
                 response_window: int = 2, **kw):
        if session not in ("sensitivity", "criterion"):
            raise ValueError("session must be 'sensitivity' or 'criterion'")
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        kw.setdefault("exclude_cued_in_uniform", True)
        self.session = session
        self.v_high, self.v_low = float(v_high), float(v_low)
        self.r_hit, self.r_cr = float(r_hit), float(r_cr)
        self.response_window = int(response_window)
        super().__init__(**kw)

    def reset(self):
        obs = super().reset()
        # per-location average reward = the sensitivity knob; PIXELS stay identical (loc_signal == 1)
        self.loc_value = np.full(self.n_stim, self.v_low, dtype=np.float32)
        if self.session == "sensitivity":
            self.loc_value[self.cue_index] = self.v_high
        return obs

    def _reward_value(self) -> float:
        if self.session == "criterion":
            return self.r_hit if self.change_true == 1 else self.r_cr
        # sensitivity: pay the RELEVANT location's value (change location on a hit, else the cued
        # location), equally for hit and CR → average reward differs by location, H:CR ratio = 1.
        loc = self.change_index if (self.change_true == 1 and self.change_index >= 0) else self.cue_index
        return float(self.loc_value[loc])

    def step(self, action):
        # response-window expiry → forced miss (event-locked response). Uses LOGICAL frames to
        # match change_time, updates the curriculum (a miss), and returns base-compatible info.
        L = self.t // self.frame_repeat
        if (self.change_true == 1 and L >= self.change_time + self.response_window
                and action == 0):
            self.t += 1
            obs = self._next_observation()
            if self.curriculum:
                self._update_curriculum(False)
            return obs, 0.0, True, {"theta": self.theta, "correct": 0.0, "expired": True}
        return super().step(action)


class KrauzlisEnv(BaseChangeDetectionEnv):
    """Attend-here / ignore-here (Zénon & Krauzlis 2012) — a TWO-stimulus filtering task: the cued
    patch and ONE diametrically-opposed foil (the S1/S4 diagonal), the other two grid cells BLANK.
    Only a change at the CUED patch is reportable; a change at the foil must be IGNORED — declaring
    on it is a false alarm, and correctly WITHHOLDING on it is a correct rejection (paid), not a
    miss. So ∂EV/∂HR_uncued = 0 while a correct withhold is positively reinforced, and the SINGLE
    foil is a clean attn_clamp target (the SC-inactivation analog). (The paper's native feature is
    motion — see MotionZKEnv for the faithful motion version; this keeps the Gabor orientation
    stimulus for token↔stimulus interpretability.)"""
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        kw.setdefault("cue_positions", [0, 3])              # cue at S1 or S4 (the 2 active patches)
        kw.setdefault("exclude_cued_in_uniform", True)
        self.active_cells = (0, 3)
        super().__init__(**kw)

    def reset(self):
        obs = super().reset()
        self.foil_index = (self.active_cells[1] if self.cue_index == self.active_cells[0]
                           else self.active_cells[0])
        return obs

    def _draw_change_index(self) -> int:
        if self.change_true == 0:
            return -1
        foil = self.active_cells[1] if self.cue_index == self.active_cells[0] else self.active_cells[0]
        return self.cue_index if np.random.rand() < self.proportion else foil

    def _is_reportable_change(self) -> bool:
        return self.change_true == 1 and self.change_index == self.cue_index

    def _is_correct_rejection(self) -> bool:
        # No-change trials AND foil-change trials → withholding is correct.
        return self.change_true == 0 or (self.change_true == 1 and self.change_index != self.cue_index)

    def _render_stimuli(self, obs, L):
        for i, (r0, r1, c0, c1) in enumerate(self.cells):
            if i not in self.active_cells:
                continue                                    # only the 2 diagonal patches carry a Gabor
            ori = self._current_feature(i, L) + self.noise_multiplier * np.random.normal()
            g = self._gabor(ori, r1 - r0, c1 - c0)
            obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)
        return obs


class BaruniEnv(BaseChangeDetectionEnv):
    """Baruni, Lau & Salzman (2015) 2-AFC orientation discrimination with RELATIVE value.

    TWO diametrically-opposed stimuli (S1/S4), each an INDEPENDENT discriminandum (orientation =
    45° ± tilt, class = sign of the tilt) carrying its own reward value shown by a coloured cue at
    t1. CRUCIALLY the QUERIED location — which stimulus the agent must report — is revealed only
    LATE (a bright marker at `query_frame`), AFTER the agent has had to attend BOTH streams, exactly
    as in the paper (choice targets appear only after the discriminanda). Because target identity is
    disclosed post-hoc, RELATIVE value (target-vs-distractor) is the only thing the value cues can
    act on — the agent must allocate attention across both by expected value, which is what produces
    the paper's relative-value behaviour (LS>LL~SS>SL). Correct discrimination of the QUERIED
    stimulus pays its value; a balanced LS/SL/LL/SS value design (small=1, large=5) makes the
    relative (LS−SL) and absolute (LL−SS) contrasts estimable. Forced 2-alternative choice, so a
    response bias cannot inflate performance.

    Actions: 0 = wait, 1 = report class 0 (toward horizontal), 2 = report class 1 (toward vertical).
    Train with `--n-actions 3 --init-action-bias 0.0 -1.0 -1.0`.
    """
    BOUNDARY = 45.0                                        # orientation category boundary (deg)

    def __init__(self, tilt_floor: float = 6.0, v_small: float = 1.0, v_large: float = 5.0,
                 query_frame: int = None, wobble: float = 15.0, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        kw.setdefault("cue_positions", [0, 3])
        self.tilt_floor = float(tilt_floor)
        self.v_small, self.v_large = float(v_small), float(v_large)
        self._query_frame_arg = query_frame
        self._wobble = float(wobble)
        self.active_cells = (0, 3)
        super().__init__(**kw)
        self.action_space = spaces.Discrete(3)
        # Baruni OWNS its per-frame orientation wobble (σ, deg) and OVERRIDES the global --noise.
        # train_rl always passes noise_multiplier=args.noise (default 5°, tuned for change-detection),
        # so kw.setdefault CANNOT raise it — a passed value silently wins. We therefore hard-set it
        # AFTER super().__init__. Why high σ: the per-frame decision variable IS the noisy orientation,
        # so a single-frame / pixel reader is hard-capped at Φ(tilt/σ) — at the ~6° tilt floor, σ=15°
        # ⇒ ≤~0.66 from any one frame, and the sign is recoverable ONLY by integrating the stimulus
        # window (temporal integration = attention/memory), defeating the pixel shortcut. Raise σ,
        # do NOT shrink the tilt (below pixel-renderability it is invisible). See
        # [[feedback_pixel_shortcut_vs_attention]].
        self.noise_multiplier = self._wobble
        # Reveal the query LATE but leave ~3 logical frames after it for focused integration. A longer
        # T (more logical frames, since frame_repeat only CACHES a frame — base.py:141) supplies more
        # independent noise draws to average over, so the achievable ceiling rises with T.
        logical_T = self.T // self.frame_repeat
        self.query_frame = int(self._query_frame_arg) if self._query_frame_arg is not None else max(5, logical_T - 3)

    def reset(self):
        obs = super().reset()
        self.change_true = 0; self.change_index = -1      # no change-detection component
        self._val2color = {v: c for c, v in self.color_values.items()}
        # each active cell: independent class + tilt + value; balanced LS/SL/LL/SS value pair
        vpair = [(self.v_large, self.v_small), (self.v_small, self.v_large),
                 (self.v_large, self.v_large), (self.v_small, self.v_small)][int(np.random.randint(4))]
        self.cls = {}; self.val = {}
        for i, v in zip(self.active_cells, vpair):
            c = int(np.random.rand() < 0.5)
            tilt = float(np.random.uniform(self.tilt_floor, max(self.tilt_floor + 1e-3, self.theta)))
            self.orientations[i] = self.BOUNDARY + (tilt if c == 1 else -tilt)
            self.cls[i] = c; self.val[i] = float(v)
        self.queried = int(np.random.choice(self.active_cells))    # revealed only at query_frame
        return obs

    def _disc(self, obs, i, color):
        r0, r1, c0, c1 = self.cells[i]; h, w = r1 - r0, c1 - c0; n = min(h, w)
        yy, xx = np.ogrid[0:h, 0:w]; cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
        d = ((xx - cx) ** 2 + (yy - cy) ** 2 <= (0.32 * n) ** 2).astype(np.float32)
        rgb = COLOR_RGB.get(color, (1.0, 1.0, 1.0))
        for k in range(3): obs[r0:r1, c0:c1, k] = d * rgb[k]

    def _render_cue(self, obs):
        for i in self.active_cells:                        # value cue on BOTH cells; NO query marker yet
            self._disc(obs, i, self._val2color.get(self.val[i], "white"))
        return obs

    def _render_stimuli(self, obs, L):
        for i in self.active_cells:
            r0, r1, c0, c1 = self.cells[i]
            ori = self.orientations[i] + self.noise_multiplier * np.random.normal()
            g = self._gabor(ori, r1 - r0, c1 - c0)
            obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)
            if L >= self.query_frame and i == self.queried:   # query marker (post-hoc): bright border
                obs[r0:r1, c0, :] = 1.0; obs[r0:r1, c1 - 1, :] = 1.0
                obs[r0, c0:c1, :] = 1.0; obs[r1 - 1, c0:c1, :] = 1.0
        return obs

    def step(self, action):
        L_before = self.t // self.frame_repeat
        self.t += 1; obs = self._next_observation()
        reward, done = 0.0, False
        if action in (1, 2):
            done = True
            reported = action - 1                          # 1→class0, 2→class1
            if L_before >= self.query_frame and reported == self.cls[self.queried]:
                reward = float(self.val[self.queried])     # correct discrimination of the queried cell
            # report before the query is revealed, or wrong class → 0
        if self.t >= self.T and not done:
            done = True                                    # no response → 0
        if done and self.curriculum:
            self._update_curriculum(reward > 0)
        return obs, reward, done, {"theta": self.theta, "correct": float(reward > 0),
                                   "queried": self.queried, "target_class": self.cls[self.queried],
                                   "reported": (action - 1) if action in (1, 2) else -1,
                                   "target_value": self.val[self.queried]}


class MotionZKEnv(BaseChangeDetectionEnv):
    """Zénon & Krauzlis (2012, Nature) motion-direction change-detection — a faithful adaptation.

    TWO random-dot patches on the diagonal (S1=top-left, S4=bottom-right), diametrically opposed
    across the image centre (the implicit fixation point); the other two grid cells stay BLANK. A
    peripheral STATIC-dot cue flashes at ONE patch (the cued/target) at t1; the other patch is the
    foil. During the test frames BOTH patches show moving dots. The report is go/no-go (Krauzlis
    attend-here/ignore-here): DECLARE only if the CUED patch's motion direction changes; WITHHOLD if
    the FOIL changes or nothing changes. This is the motion sibling of the colour-change
    Herman-Krauzlis reference task; the paper's SC INACTIVATION maps onto clamping attention AWAY
    from the cued patch (attn_clamp), predicting behaviour collapses while the attention-map gain is
    preserved.

    Faithful to the paper: circular aperture, circular (anti-aliased) dots, motion carried by
    per-dot directional GAUSSIAN NOISE (SD ~16°, `dir_noise_sd`) around a mean heading, a modest
    direction-change signal Δ (the curriculum), a peripheral static-dot spatial cue, 2 diametric
    patches, and a single go/no-go report. Coarsened for our 4-frame stimulus (vs the paper's
    ~continuous 75 Hz display): the 8-frame limited-lifetime algorithm is replaced by per-frame
    directional sampling so the direction change is visible within the 2 post-change frames.
    See [[feedback_pixel_shortcut_vs_attention]] — a single frame carries no direction, so the task
    requires temporal integration and cannot be solved at the pixel level."""
    def __init__(self, n_dots: int = 30, dir_noise_sd: float = 16.0, dot_speed: float = 2.5,
                 dot_radius: float = 1.2, proportion_cued: float = 0.5, reward_scale: float = 10.0, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        kw.setdefault("cue_positions", [0, 3])                 # cue at S1 or S4 — the 2 active patches
        kw.setdefault("proportions", (float(proportion_cued),))  # P(change at cued | change trial)
        self.active_cells = (0, 3)
        self.n_dots = int(n_dots); self.dir_noise_sd = float(dir_noise_sd)
        self.dot_speed = float(dot_speed); self.dot_radius = float(dot_radius)
        self.reward_scale = float(reward_scale)                # reward magnitude multiplier (see _reward_value)
        super().__init__(**kw)

    def _reward_value(self) -> float:
        # ONLY change from the default task: reward magnitude ×10 (applied to BOTH the hit and the
        # correct-rejection reward, so the reward STRUCTURE — relative payoffs, timing, trial mix — is
        # identical; only the scalar magnitude changes).
        return self.reward_scale * super()._reward_value()

    # ── trial setup ──────────────────────────────────────────────────────────
    def reset(self):
        obs = super().reset()
        self.foil_index = (self.active_cells[1] if self.cue_index == self.active_cells[0]
                           else self.active_cells[0])
        self.dots = {i: self._random_dots_in_aperture(*self._cell_hw(i)) for i in self.active_cells}
        return obs

    def _cell_hw(self, i):
        r0, r1, c0, c1 = self.cells[i]
        return r1 - r0, c1 - c0

    def _aperture(self, h, w):
        return (h - 1) / 2.0, (w - 1) / 2.0, min(h, w) / 2.0 - 1.0     # cy, cx, R

    def _random_dots_in_aperture(self, h, w):
        cy, cx, R = self._aperture(h, w)
        u = np.random.rand(self.n_dots); ang = np.random.rand(self.n_dots) * 2 * np.pi
        rr = R * np.sqrt(u)                                            # uniform over the disc
        return np.stack([cy + rr * np.sin(ang), cx + rr * np.cos(ang)], axis=1).astype(np.float32)

    def _draw_change_index(self) -> int:
        # computed from cue_index (set before this call in base.reset) so it does not depend on
        # foil_index, which is assigned later in reset()
        if self.change_true == 0:
            return -1
        foil = self.active_cells[1] if self.cue_index == self.active_cells[0] else self.active_cells[0]
        return self.cue_index if np.random.rand() < self.proportion else foil

    # ── reward: attend cued / ignore foil (go/no-go), as Zénon & Krauzlis ─────
    def _is_reportable_change(self) -> bool:
        return self.change_true == 1 and self.change_index == self.cue_index

    def _is_correct_rejection(self) -> bool:
        return self.change_true == 0 or (self.change_true == 1 and self.change_index != self.cue_index)

    # ── rendering: circular dots in a circular aperture ──────────────────────
    def _paint_dots(self, cell, positions):
        h, w = cell.shape[:2]; r = self.dot_radius
        for cy, cx in positions:
            y0, y1 = max(0, int(cy - r - 1)), min(h, int(cy + r + 2))
            x0, x1 = max(0, int(cx - r - 1)), min(w, int(cx + r + 2))
            if y0 >= y1 or x0 >= x1:
                continue
            yy, xx = np.ogrid[y0:y1, x0:x1]
            dist = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
            cov = np.clip(r + 0.5 - dist, 0.0, 1.0)                    # anti-aliased circular dot
            cell[y0:y1, x0:x1, :] = np.maximum(cell[y0:y1, x0:x1, :], cov[..., None])

    def _render_cue(self, obs):
        # Zénon cue: a peripheral static-dot patch flashed at the CUED location only
        r0, r1, c0, c1 = self.cells[self.cue_index]
        self._paint_dots(obs[r0:r1, c0:c1, :], self._random_dots_in_aperture(r1 - r0, c1 - c0))
        return obs

    def _render_stimuli(self, obs, L):
        for i in self.active_cells:
            r0, r1, c0, c1 = self.cells[i]
            cy, cx, R = self._aperture(r1 - r0, c1 - c0)
            mean_dir = np.deg2rad(self._current_feature(i, L))        # signal heading (+Δ from change) in rad
            ang = mean_dir + np.deg2rad(self.dir_noise_sd) * np.random.randn(self.n_dots)   # directional noise
            d = self.dots[i]
            d[:, 0] += self.dot_speed * np.sin(ang)                   # move y
            d[:, 1] += self.dot_speed * np.cos(ang)                   # move x
            rel = d - np.array([cy, cx], np.float32)
            rad = np.sqrt((rel ** 2).sum(1))
            out = rad > R                                             # wrap dots leaving the circular aperture
            if out.any():
                d[out] = np.array([cy, cx], np.float32) - rel[out] * (R / (rad[out, None] + 1e-6)) * 0.98
            self.dots[i] = d
            self._paint_dots(obs[r0:r1, c0:c1, :], d)
        return obs
