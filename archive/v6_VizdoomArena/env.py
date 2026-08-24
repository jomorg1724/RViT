"""
ViZDoom "arena" environment wrapper for V6 — the `deathmatch` scenario.

The scenario: a large arena, monsters spawn continuously, weapons / ammo /
medkits are scattered around the perimeter. +1 KILLCOUNT per monster killed,
episode ends on death or after 4200 tics (1050 agent steps at frame-skip 4).

The wrapper exposes:

  • obs   : (3, 60, 80) uint8 CHW RGB — RES_160X120 CRCGCB screen, 2×2
            average-pooled. uint8 so the replay buffer stays small; the model
            normalizes to [0,1] on-device.
  • feats : (25,) float32 — the game-state vector that becomes the encoder's
            K/V-only state tokens. Layout (see FEAT_GROUPS):
                [0:3)   vitals      health/100, armor/100, min(ammo,200)/200
                [3:11)  weapon      one-hot of SELECTED_WEAPON (0..7)
                [11:25) last_action one-hot of the previous wrapper action
  • 13 discrete actions (button combos, ACTION_NAMES below).
  • shaped reward from game-variable deltas — REVISED after the run-1
    postmortem (2026-06-10). KILLCOUNT was verified to be the GLOBAL map kill
    tally (a noop policy "earns" ~1 kill/episode from monster infighting), so
    the reward is now built from PLAYER-ATTRIBUTED signals only; the kill
    bonus is gated on same-step attribution evidence:
        + w_kill   · ΔKILLCOUNT   ONLY when ΔDAMAGECOUNT>0 or ΔHITCOUNT>0
        + w_damage · ΔDAMAGECOUNT          (player damage dealt; 0 vs walls)
        + w_hit    · ΔHITCOUNT             (player shots landed)
        − w_taken  · ΔDAMAGE_TAKEN
        − w_ammo_spent · rounds fired      (same-weapon ammo decrease — makes
                                            wall-shooting strictly negative)
        + w_health_gain · HP gained        (medkit pickups)
        − w_death  · [died this step]
    KILLCOUNT stays the headline METRIC (it is the scenario score) and rides
    on `info`, alongside player-attributed damage/hits.
  • AUTO-RESET: when the episode finishes, `step` returns done=True together
    with the FIRST obs/feats of the next episode (the recurrent state must be
    reset by the caller — the trainer does this on `done`), and
    `info["episode"]` carries {"return", "kills", "length"} of the episode
    that just ended.
  • labels (optional, `enable_labels=True`): per-object screen bounding boxes
    from ViZDoom's labels buffer, already scaled to the 60×80 obs — used by
    the analysis tools for the attention-on-enemies metric. Off during
    training (tiny speedup, smaller states).
"""
from __future__ import annotations

import os
from typing import Optional

import numpy as np

try:
    import vizdoom as vzd
except ImportError as _e:  # pragma: no cover — surfaced lazily in __init__
    vzd = None
    _VIZDOOM_IMPORT_ERROR = _e


# ─────────────────────────────────────────────────────────────────────────────
# Discrete action set (button combos)
# ─────────────────────────────────────────────────────────────────────────────

# Buttons in deathmatch.cfg order (indices into the 20-button action vector).
_B_ATTACK, _B_SPEED, _B_STRAFE = 0, 1, 2
_B_MOVE_RIGHT, _B_MOVE_LEFT, _B_MOVE_BACKWARD, _B_MOVE_FORWARD = 3, 4, 5, 6
_B_TURN_RIGHT, _B_TURN_LEFT = 7, 8
_B_SELECT_NEXT_WEAPON = 15

# NOTE (run-1 postmortem, 2026-06-10): "next_weapon" was REMOVED from the
# action set. With only fist+pistol owned at spawn, one SELECT_NEXT_WEAPON
# press switches to the 0-ammo fist and STICKS there (verified) — an
# irreversible self-disarm trap. Weapon upgrades still happen via the engine's
# auto-switch-on-pickup.
ACTION_NAMES = [
    "noop", "attack", "forward", "forward_attack",
    "turn_left", "turn_right", "forward_turn_left", "forward_turn_right",
    "strafe_left", "strafe_right", "backward",
    "attack_turn_left", "attack_turn_right",
]
_ACTION_BUTTONS = [
    [], [_B_ATTACK], [_B_MOVE_FORWARD], [_B_MOVE_FORWARD, _B_ATTACK],
    [_B_TURN_LEFT], [_B_TURN_RIGHT],
    [_B_MOVE_FORWARD, _B_TURN_LEFT], [_B_MOVE_FORWARD, _B_TURN_RIGHT],
    [_B_MOVE_LEFT], [_B_MOVE_RIGHT], [_B_MOVE_BACKWARD],
    [_B_ATTACK, _B_TURN_LEFT], [_B_ATTACK, _B_TURN_RIGHT],
]
N_ACTIONS = len(ACTION_NAMES)

# Feature-vector layout consumed by the model's state tokens.
N_WEAPON_SLOTS = 8                       # SELECTED_WEAPON ∈ 1..7; clamp to 0..7
FEAT_GROUPS = {
    "vitals":      (0, 3),
    "weapon":      (3, 3 + N_WEAPON_SLOTS),
    "last_action": (3 + N_WEAPON_SLOTS, 3 + N_WEAPON_SLOTS + N_ACTIONS),
}
FEAT_DIM = 3 + N_WEAPON_SLOTS + N_ACTIONS          # 25

# Monsters that spawn in the deathmatch arena (labels-buffer object names).
MONSTER_NAMES = frozenset({
    "Zombieman", "ShotgunGuy", "ChaingunGuy", "DoomImp", "Demon", "Spectre",
    "LostSoul", "Cacodemon", "HellKnight", "BaronOfHell", "Arachnotron",
    "PainElemental", "Revenant", "Mancubus", "Fatso", "Archvile",
})

OBS_H, OBS_W = 60, 80


def _avg_pool2(img_chw_u8: np.ndarray) -> np.ndarray:
    """(C, 2H, 2W) uint8 → (C, H, W) uint8, 2×2 average (cheap anti-alias)."""
    x = img_chw_u8.astype(np.uint16)
    x = x[:, 0::2, 0::2] + x[:, 1::2, 0::2] + x[:, 0::2, 1::2] + x[:, 1::2, 1::2]
    return (x // 4).astype(np.uint8)


class VizdoomArenaEnv:
    """The deathmatch arena with discrete combo actions and shaped rewards.

    Args
    ----
    frame_skip    : tics per agent action (default 4).
    reward_kill   : per ATTRIBUTED ΔKILLCOUNT — paid only when the same step
                    also has ΔDAMAGECOUNT>0 or ΔHITCOUNT>0 (default 1.0).
    reward_damage : per point of player damage dealt (default 0.02).
    reward_hit    : per player shot landed, ΔHITCOUNT (default 0.5).
    reward_taken  : per point of damage taken, applied NEGATIVE (default 0.005).
    reward_ammo_spent  : per round fired (same-weapon ammo decrease), applied
                    NEGATIVE (default 0.01) — prices wall-shooting.
    reward_health_gain : per HP gained from pickups (default 0.01).
    reward_death  : applied NEGATIVE when the agent dies (default 1.0).
    reward_clip   : per-step |shaped reward| clip (default 5.0).
    enable_labels : turn on the labels buffer (analysis only).
    seed          : engine seed (None → nondeterministic).
    visible       : show the game window (analysis/demos only).
    """

    def __init__(
        self,
        frame_skip: int = 4,
        reward_kill: float = 1.0,
        reward_damage: float = 0.02,
        reward_hit: float = 0.5,
        reward_taken: float = 0.005,
        reward_ammo_spent: float = 0.01,
        reward_health_gain: float = 0.01,
        reward_death: float = 1.0,
        reward_clip: float = 5.0,
        enable_labels: bool = False,
        seed: Optional[int] = None,
        visible: bool = False,
    ) -> None:
        if vzd is None:  # pragma: no cover
            raise ImportError(
                f"vizdoom is required for VizdoomArenaEnv: {_VIZDOOM_IMPORT_ERROR}"
            )
        self.frame_skip = int(frame_skip)
        self.w_kill, self.w_damage = float(reward_kill), float(reward_damage)
        self.w_hit = float(reward_hit)
        self.w_taken, self.w_death = float(reward_taken), float(reward_death)
        self.w_ammo_spent = float(reward_ammo_spent)
        self.w_health_gain = float(reward_health_gain)
        self.reward_clip = float(reward_clip)
        self.enable_labels = bool(enable_labels)
        self.n_actions = N_ACTIONS
        self.feat_dim = FEAT_DIM
        self.obs_shape = (3, OBS_H, OBS_W)

        g = vzd.DoomGame()
        g.load_config(os.path.join(vzd.scenarios_path, "deathmatch.cfg"))
        g.set_window_visible(visible)
        g.set_sound_enabled(False)
        g.set_screen_resolution(vzd.ScreenResolution.RES_160X120)
        g.set_screen_format(vzd.ScreenFormat.CRCGCB)        # (3,120,160) uint8 CHW
        if self.enable_labels:
            g.set_labels_buffer_enabled(True)
        # Shaping variables appended AFTER the cfg's 5:
        #   cfg: [0]=KILLCOUNT [1]=HEALTH [2]=ARMOR [3]=SELECTED_WEAPON
        #        [4]=SELECTED_WEAPON_AMMO
        #   extra: [5]=DAMAGECOUNT [6]=DAMAGE_TAKEN [7]=HITCOUNT [8]=DEAD
        for v in (vzd.GameVariable.DAMAGECOUNT, vzd.GameVariable.DAMAGE_TAKEN,
                  vzd.GameVariable.HITCOUNT, vzd.GameVariable.DEAD):
            g.add_available_game_variable(v)
        if seed is not None:
            g.set_seed(int(seed))
        g.init()
        self.game = g
        self._n_buttons = g.get_available_buttons_size()
        self._action_vectors = []
        for combo in _ACTION_BUTTONS:
            vec = [0] * self._n_buttons
            for b in combo:
                vec[b] = 1
            self._action_vectors.append(vec)

        # Per-episode bookkeeping (deltas + stats).
        self._last_action = 0
        self._prev_kills = 0.0
        self._prev_damage = 0.0
        self._prev_taken = 0.0
        self._prev_hits = 0.0
        self._prev_health = 100.0
        self._prev_ammo = 0.0
        self._prev_weapon = 0
        self._ep_return = 0.0
        self._ep_len = 0
        self._last_labels: list = []

    # ── observation / feature extraction ────────────────────────────────────

    def _grab(self) -> tuple[np.ndarray, np.ndarray]:
        """Current (obs, feats) from the live game state. Episode must be live."""
        state = self.game.get_state()
        obs = _avg_pool2(state.screen_buffer)               # (3,60,80) uint8
        gv = state.game_variables
        health, armor = float(gv[1]), float(gv[2])
        weapon, ammo = int(gv[3]), float(gv[4])
        # Stash for the reward deltas (health gain / ammo spent / weapon switch).
        self._cur_health, self._cur_ammo, self._cur_weapon = health, ammo, weapon
        feats = np.zeros(FEAT_DIM, dtype=np.float32)
        feats[0] = max(health, 0.0) / 100.0
        feats[1] = max(armor, 0.0) / 100.0
        feats[2] = min(max(ammo, 0.0), 200.0) / 200.0
        feats[3 + min(max(weapon, 0), N_WEAPON_SLOTS - 1)] = 1.0
        feats[3 + N_WEAPON_SLOTS + self._last_action] = 1.0
        if self.enable_labels:
            self._last_labels = self._scale_labels(state.labels)
        return obs, feats

    def _scale_labels(self, labels) -> list:
        """Labels-buffer bboxes scaled from 160×120 to the 80×60 obs grid."""
        out = []
        for l in labels or []:
            out.append({
                "name": l.object_name,
                "is_monster": l.object_name in MONSTER_NAMES,
                "x": l.x / 2.0, "y": l.y / 2.0,
                "w": l.width / 2.0, "h": l.height / 2.0,
            })
        return out

    @property
    def labels(self) -> list:
        """Most recent scaled labels (requires enable_labels=True)."""
        return self._last_labels

    # ── env API ──────────────────────────────────────────────────────────────

    def reset(self) -> tuple[np.ndarray, np.ndarray]:
        self.game.new_episode()
        self._last_action = 0
        self._prev_kills = self._prev_damage = self._prev_taken = self._prev_hits = 0.0
        self._ep_return, self._ep_len = 0.0, 0
        out = self._grab()
        self._prev_health = self._cur_health
        self._prev_ammo = self._cur_ammo
        self._prev_weapon = self._cur_weapon
        return out

    def step(self, action: int) -> tuple[np.ndarray, np.ndarray, float, bool, dict]:
        """Returns (obs, feats, shaped_reward, done, info). AUTO-RESETS on done:
        the returned obs/feats are the next episode's first frame."""
        a = int(action)
        self.game.make_action(self._action_vectors[a], self.frame_skip)
        done = self.game.is_episode_finished()
        died = self.game.is_player_dead()

        if done:
            # Terminal: no live state; deltas come from the persistent totals.
            # Health/ammo terms are skipped on the terminal step (negligible).
            kills = float(self.game.get_game_variable(vzd.GameVariable.KILLCOUNT))
            damage = float(self.game.get_game_variable(vzd.GameVariable.DAMAGECOUNT))
            taken = float(self.game.get_game_variable(vzd.GameVariable.DAMAGE_TAKEN))
            hits = float(self.game.get_game_variable(vzd.GameVariable.HITCOUNT))
            health, ammo, weapon = self._prev_health, self._prev_ammo, self._prev_weapon
        else:
            gv = self.game.get_state().game_variables
            kills, damage, taken = float(gv[0]), float(gv[5]), float(gv[6])
            hits = float(gv[7])
            health, ammo, weapon = float(gv[1]), float(gv[4]), int(gv[3])

        d_kills = kills - self._prev_kills
        d_damage = damage - self._prev_damage
        d_hits = hits - self._prev_hits
        # Kill credit GATED on attribution: KILLCOUNT is the global map tally
        # (monster infighting included), so a kill only pays when this step
        # also shows player damage/hits (verified: infight rises have neither).
        attributed_kills = d_kills if (d_damage > 0 or d_hits > 0) else 0.0
        # Rounds fired = same-weapon ammo decrease (weapon switches change the
        # SELECTED_WEAPON_AMMO pool and must not be charged).
        ammo_spent = max(self._prev_ammo - ammo, 0.0) if weapon == self._prev_weapon else 0.0

        r = (self.w_kill * attributed_kills
             + self.w_damage * d_damage
             + self.w_hit * d_hits
             - self.w_taken * (taken - self._prev_taken)
             - self.w_ammo_spent * ammo_spent
             + self.w_health_gain * max(health - self._prev_health, 0.0)
             - (self.w_death if (done and died) else 0.0))
        r = float(np.clip(r, -self.reward_clip, self.reward_clip))
        self._prev_kills, self._prev_damage, self._prev_taken = kills, damage, taken
        self._prev_hits = hits
        self._prev_health, self._prev_ammo, self._prev_weapon = health, ammo, weapon
        self._last_action = a
        self._ep_return += r
        self._ep_len += 1

        info: dict = {"kills": kills, "died": bool(died)}
        if done:
            info["episode"] = {
                "return": self._ep_return, "kills": kills, "length": self._ep_len,
                "damage": damage, "hits": hits,
            }
            obs, feats = self.reset()                      # auto-reset
        else:
            obs, feats = self._grab()
        return obs, feats, r, done, info

    def close(self) -> None:
        self.game.close()
