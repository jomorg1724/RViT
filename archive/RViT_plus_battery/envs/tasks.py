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

try:
    from .base import BaseChangeDetectionEnv
except ImportError:  # pragma: no cover
    from base import BaseChangeDetectionEnv  # type: ignore[no-redef]


class Validity4Env(BaseChangeDetectionEnv):
    def __init__(self, **kw):
        kw.setdefault("grid_rows", 2); kw.setdefault("grid_cols", 2)
        kw.setdefault("value_cues", False)
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
