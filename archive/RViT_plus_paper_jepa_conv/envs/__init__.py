"""Task registry for the RViT+ FiLM battery.

TASKS[name] -> dict(make=<callable returning a fresh env>, grid=(rows, cols)).
The grid MUST match the model's front-end grid so token i ⇔ stimulus i.
"""
from __future__ import annotations

try:
    from .base import BaseChangeDetectionEnv
    from .tasks import (Validity4Env, VDAEnv, SetSizeEnv, LuoMaunsellEnv, KrauzlisEnv, BaruniEnv, MotionZKEnv)
except ImportError:  # pragma: no cover
    from base import BaseChangeDetectionEnv  # type: ignore
    from tasks import (Validity4Env, VDAEnv, SetSizeEnv, LuoMaunsellEnv, KrauzlisEnv, BaruniEnv, MotionZKEnv)  # type: ignore

TASKS = {
    "validity4":    dict(make=lambda **k: Validity4Env(**k),               grid=(2, 2)),
    "vda4":         dict(make=lambda **k: VDAEnv(**k),                     grid=(2, 2)),
    "setsize2":     dict(make=lambda **k: SetSizeEnv(set_size=2, **k),     grid=(1, 2)),
    "setsize4":     dict(make=lambda **k: SetSizeEnv(set_size=4, **k),     grid=(2, 2)),
    "setsize9":     dict(make=lambda **k: SetSizeEnv(set_size=9, **k),     grid=(3, 3)),
    "luo_maunsell_sensitivity": dict(make=lambda **k: LuoMaunsellEnv(session="sensitivity", **k), grid=(2, 2)),
    "luo_maunsell_criterion":   dict(make=lambda **k: LuoMaunsellEnv(session="criterion", **k),   grid=(2, 2)),
    "krauzlis":     dict(make=lambda **k: KrauzlisEnv(**k),                grid=(2, 2)),
    "baruni":       dict(make=lambda **k: BaruniEnv(**k),                  grid=(2, 2)),   # 2-AFC (n_actions=3)
    "motion_zk":    dict(make=lambda **k: MotionZKEnv(**k),                grid=(2, 2)),   # Zénon-Krauzlis motion change-detection (2 diagonal patches)
}


def make_env(task: str, **kw):
    if task not in TASKS:
        raise ValueError(f"unknown task {task!r}; choices: {sorted(TASKS)}")
    return TASKS[task]["make"](**kw)


def task_grid(task: str):
    return TASKS[task]["grid"]


__all__ = ["TASKS", "make_env", "task_grid", "BaseChangeDetectionEnv", "Validity4Env", "VDAEnv",
           "SetSizeEnv", "LuoMaunsellEnv", "KrauzlisEnv", "BaruniEnv", "MotionZKEnv"]
