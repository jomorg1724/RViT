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
  FixedGridVDASetSizeEnv(K) — controlled VDA K∈{1,2,4,9,16} on one 4×4/100px,
                   16-token geometry; inactive cells are blank.
  LuoMaunsellEnv — reward-STRUCTURE sessions: 'sensitivity' (value concentrated at one
                   location) vs 'criterion' (hit↔correct-reject reward ratio), plus a
                   response window. Engages the Luo & Maunsell d′-vs-criterion result.
  KrauzlisEnv    — attend-here/ignore-here: ONLY a change at the cued location is
                   reportable; uncued changes must be ignored (∂EV/∂HR_uncued = 0).
"""
from __future__ import annotations

import numpy as np

try:
    from .base import BaseChangeDetectionEnv
except ImportError:  # pragma: no cover
    from base import BaseChangeDetectionEnv  # type: ignore[no-redef]


class _VDATrialMetadataMixin:
    """Expose the cue's displayed target claim and the trial's realized target."""

    def trial_metadata(self):
        changed = bool(self.change_true)
        active = tuple(int(i) for i in getattr(self, "active", range(self.n_stim)))
        return {
            "displayed_validity": float(self.proportion),
            "realized_validity": bool(self.change_index == self.cue_index) if changed else None,
            "displayed_target_index": int(self.cue_index),
            "realized_target_index": int(self.change_index) if changed else None,
            "active_locations": active,
        }

    def step(self, action):
        obs, reward, done, info = super().step(action)
        info = dict(info)
        info.update(self.trial_metadata())
        return obs, reward, done, info


class Validity4Env(BaseChangeDetectionEnv):
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        kw.setdefault("cue_positions", [0, 3])      # paper: cue at S1 (top-left) or S4 (bottom-right)
        super().__init__(**kw)


class VDAEnv(_VDATrialMetadataMixin, BaseChangeDetectionEnv):
    """Value-directed attention: coloured value cue + validity ring."""
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", True)
        super().__init__(**kw)

    def _draw_change_index(self) -> int:
        return self._draw_validity_target()


class DelayProbeEnv(VDAEnv):
    """Awh, Jonides & Reuter-Lorenz (1998) delay-probe (ledger E4/E6). During the post-cue DELAY
    frame (logical L=2, normally blank) a transient probe Gabor appears at either the CUED
    (memorized) location (``probe_loc='cued'``) or a random UNCUED location (``probe_loc='uncued'``).
    The value/validity cued task is otherwise unchanged.

    ZERO-SHOT USE (no retraining): run an ALREADY-TRAINED model and read its actor 'declare' logit
    on the delay frame — compare cued vs uncued probe trials. A larger declare-response to a
    cued-location probe = visual processing enhanced at the memorized location = attention-based
    rehearsal. The probe carries NO reward (passive transient); the main change task/reward is intact.
    """
    def __init__(self, probe_loc: str = "cued", probe_prob: float = 1.0,
                 probe_contrast: float = 1.0, **kw):
        self.probe_loc = str(probe_loc)              # "cued" | "uncued"
        self.probe_prob = float(probe_prob)          # P(a probe appears on a trial)
        self.probe_contrast = float(probe_contrast)  # probe Gabor amplitude (1.0 = full)
        self.probe_present = False                   # must exist before super() renders L=0
        self.probe_index = -1
        self.probe_orientation = 0.0
        super().__init__(**kw)

    def reset(self):
        self.probe_present = False                   # keep attr valid for the L=0 render inside super()
        obs = super().reset()                        # sets cue_index / trial vars, renders blank L=0
        if self.n_stim > 1 and np.random.rand() < self.probe_prob:
            self.probe_present = True
            if self.probe_loc == "cued":
                self.probe_index = int(self.cue_index)
            else:                                    # a random NON-cued cell
                others = [i for i in range(self.n_stim) if i != self.cue_index]
                self.probe_index = int(np.random.choice(others))
            self.probe_orientation = float(np.random.uniform(0, 360))
        else:
            self.probe_present = False
            self.probe_index = -1
        return obs

    def _render_probe(self, obs):
        r0, r1, c0, c1 = self.cells[self.probe_index]
        ori = self.probe_orientation + self.noise_multiplier * np.random.normal()
        g = self._gabor(ori, r1 - r0, c1 - c0) * self.probe_contrast
        obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)
        return obs

    def _next_observation(self):
        L = self.t // self.frame_repeat
        if self.frame_repeat > 1 and self.t % self.frame_repeat != 0 and self._frame_cache is not None:
            return self._frame_cache
        obs = np.zeros((self.S, self.S, 3), dtype=np.float32)
        if L == 1:
            out = self._render_cue(obs)
        elif L == 2 and self.probe_present:
            out = self._render_probe(obs)           # probe replaces the blank delay frame
        elif L in (0, 2):
            out = obs
        else:
            out = self._render_stimuli(obs, L)
        self._frame_cache = out
        return out

    def step(self, action):
        obs, reward, done, info = super().step(action)
        info = dict(info)
        info["probe_present"] = bool(self.probe_present)
        info["probe_index"] = int(self.probe_index)
        info["probe_is_cued"] = bool(self.probe_present and self.probe_index == self.cue_index)
        return obs, reward, done, info


class VDA9Env(VDAEnv):
    """VDA on a 3x3 grid (9 stimuli, 75x75 image). Same rules as VDAEnv, more stimuli: coloured value
    cue (red5/green3/blue1) + validity ring at the TWO corners (TL=0, BR=8), plus one extra proportion
    0.0 = NO ring = changes always target one of the eight uncued stimuli."""
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 3); kw.setdefault("grid_cols", 3)
        kw.setdefault("image_size", 75)                              # 3 x 25px patches
        kw.setdefault("value_cues", True)
        kw.setdefault("cue_positions", [0, 8])                       # TL and BR of the 3x3 (as before)
        kw.setdefault("proportions", (0.0, 0.25, 0.5, 0.75, 1.0))    # 0 = uninformative (no ring)
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
    """Reward-structure sessions + response window.

    session='sensitivity': correct detection at the HIGH-VALUE location pays
        `high_reward`, elsewhere `low_reward` (value concentrated at a location →
        modulates where it pays to be sensitive).
    session='criterion':   hits pay `r_hit`, correct rejections pay `r_cr` (same across
        locations); their ratio shifts the optimal criterion without touching where
        sensitivity should go.
    response_window: a change must be declared within this many steps or it expires
        (miss), preventing a wait-to-the-end strategy.
    """
    def __init__(self, session: str = "sensitivity", high_reward: float = 5.0,
                 low_reward: float = 1.0, r_hit: float = 1.0, r_cr: float = 1.0,
                 response_window: int = 3, **kw):
        if session not in ("sensitivity", "criterion"):
            raise ValueError("session must be 'sensitivity' or 'criterion'")
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        self.session = session
        self.high_reward, self.low_reward = float(high_reward), float(low_reward)
        self.r_hit, self.r_cr = float(r_hit), float(r_cr)
        self.response_window = int(response_window)
        super().__init__(**kw)

    def reset(self):
        obs = super().reset()
        # high-value location = the cued one (a per-trial reward-context manipulation)
        self.high_value_index = self.cue_index
        return obs

    def _reward_value(self) -> float:
        if self.session == "sensitivity":
            if self.change_true == 1:
                return self.high_reward if self.change_index == self.high_value_index else self.low_reward
            return self.low_reward                      # correct rejection
        # criterion session
        return self.r_hit if self.change_true == 1 else self.r_cr

    def step(self, action):
        # response-window expiry → forced miss (trial ends, no reward) if not declared
        if (self.change_true == 1 and self.t >= self.change_time + self.response_window
                and action == 0):
            self.t += 1
            return self._next_observation(), 0.0, True, {"expired": True}
        return super().step(action)


class KrauzlisEnv(BaseChangeDetectionEnv):
    """Attend-here / ignore-here: only a change at the CUED location is reportable;
    a change elsewhere is a distractor that must be ignored (declaring on it = 0)."""
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
        super().__init__(**kw)

    def _is_reportable_change(self) -> bool:
        return self.change_true == 1 and self.change_index == self.cue_index


class VDAExclusionEnv(BaseChangeDetectionEnv):
    """Distractor-EXCLUSION test (value-directed), within-subject. Two locations (1x2); the cue is
    100% VALID and always marks the TARGET, and the change to detect is always at the target. The
    OTHER location holds a task-IRRELEVANT distractor that is PRESENT on a random fraction
    (`p_distractor`) of trials and ABSENT (blank) on the rest. Interleaving target-alone vs
    target+distractor trials in one session isolates the distractor-exclusion prediction of the
    external-noise-reduction account: the cueing/attention benefit — and the effect of clamping
    attention onto the target — should appear on distractor-PRESENT trials and vanish when the target
    is alone (attention helps by suppressing the distractor; no distractor → nothing to suppress).
    `info['distractor_present']` labels each trial for the split."""
    def __init__(self, p_distractor: float = 0.5, **kw):
        kw.setdefault("grid_rows", 1); kw.setdefault("grid_cols", 2)
        kw.setdefault("image_size", 50)
        kw.setdefault("value_cues", True)
        kw.setdefault("proportions", (1.0,))            # 100% valid cue: change always at the target
        self.p_distractor = float(p_distractor)
        super().__init__(**kw)

    def reset(self):
        obs = super().reset()
        self.target_index = self.cue_index
        self.distractor_index = 1 - self.cue_index      # the other of the two cells
        self.distractor_present = int(np.random.rand() < self.p_distractor)
        return obs

    def _render_stimuli(self, obs, L):
        present = getattr(self, "distractor_present", 1)
        dis = getattr(self, "distractor_index", -1)
        for i, (r0, r1, c0, c1) in enumerate(self.cells):
            if i == dis and not present:
                continue                                 # target-alone trial: distractor cell stays blank
            ori = self._current_feature(i, L) + self.noise_multiplier * np.random.normal()
            g = self._gabor(ori, r1 - r0, c1 - c0)
            obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)
        return obs

    def step(self, action):
        obs, r, done, info = super().step(action)
        info["distractor_present"] = getattr(self, "distractor_present", 1)
        return obs, r, done, info


class VDASetSizeEnv(_VDATrialMetadataMixin, BaseChangeDetectionEnv):
    """Value-directed change-detection at a reduced set size on a FIXED grid (default 2x2). Each trial
    `set_size` of the grid's cells hold a Gabor (chosen at random); the rest stay blank. The cue
    (colour = value) marks one active cell (the TARGET); the change is at the target (w.p.
    `proportion`) or, for set_size>1, another active cell. Keeping the 2x2 layout (4 tokens, 25x25
    cells) makes VDA1/VDA2 directly comparable to VDA4 — only the NUMBER of stimuli changes, not the
    display geometry. `info['set_size']`/`active` label each trial."""
    def __init__(self, set_size: int = 2, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("image_size", 50)
        kw.setdefault("value_cues", True)
        self.set_size = int(set_size)
        super().__init__(**kw)

    def reset(self):
        obs = super().reset()
        k = min(self.set_size, self.n_stim)
        self.active = sorted(int(c) for c in np.random.choice(self.n_stim, size=k, replace=False))
        self.cue_index = int(np.random.choice(self.active))                 # target = a random active cell
        self.change_index = self._draw_validity_target(self.active)
        self.valid = int(self.change_true == 1 and self.change_index == self.cue_index)
        return obs

    def _render_stimuli(self, obs, L):
        active = getattr(self, "active", list(range(self.n_stim)))
        for i, (r0, r1, c0, c1) in enumerate(self.cells):
            if i not in active:
                continue                                                    # inactive cell stays blank
            ori = self._current_feature(i, L) + self.noise_multiplier * np.random.normal()
            g = self._gabor(ori, r1 - r0, c1 - c0)
            obs[r0:r1, c0:c1, :] = np.stack([g, g, g], axis=-1)
        return obs

    def step(self, action):
        obs, r, done, info = super().step(action)
        info["set_size"] = self.set_size
        return obs, r, done, info


class FixedGridVDASetSizeEnv(VDASetSizeEnv):
    """Controlled VDA set size on an invariant 4x4, 100px, 16-token canvas.

    Only ``set_size`` changes across this family. Active cells are sampled with the
    existing NumPy RNG convention and inactive cells remain blank. K>=2 uses the exact
    validity sampler (invalid targets exclude the cue). K=1 necessarily forces every
    realized change to the sole cued item, which is reported explicitly in metadata.
    """
    SET_SIZES = (1, 2, 4, 9, 16)

    def __init__(self, set_size: int, **kw):
        if int(set_size) not in self.SET_SIZES:
            raise ValueError(f"set_size must be one of {self.SET_SIZES}")
        kw["grid_rows"] = 4
        kw["grid_cols"] = 4
        kw["image_size"] = 100
        super().__init__(set_size=int(set_size), **kw)

    def trial_metadata(self):
        metadata = super().trial_metadata()
        metadata.update({
            "validity_mode": "exact_bernoulli" if self.set_size >= 2 else "degenerate_singleton",
            "invalid_target_available": self.set_size >= 2,
            "effective_validity": float(self.proportion) if self.set_size >= 2 else 1.0,
            "validity_caveat": (
                None if self.set_size >= 2 else
                "K=1 cannot realize an uncued invalid target; every realized change is cued."
            ),
        })
        return metadata
