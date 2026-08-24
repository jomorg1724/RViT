"""Task registry for the RViT+ FiLM battery.

TASKS[name] -> dict(make=<callable returning a fresh env>, grid=(rows, cols)).
The grid MUST match the model's front-end grid so token i ⇔ stimulus i.
"""
from __future__ import annotations

try:
    from .base import BaseChangeDetectionEnv
    from .tasks import (Validity4Env, VDAEnv, VDA9Env, SetSizeEnv, LuoMaunsellEnv, KrauzlisEnv, VDAExclusionEnv, VDASetSizeEnv, FixedGridVDASetSizeEnv, DelayProbeEnv)
    from .luo2015 import LuoMaunsell2015Sensitivity, LuoMaunsell2015Criterion
except ImportError:  # pragma: no cover
    from base import BaseChangeDetectionEnv  # type: ignore
    from tasks import (Validity4Env, VDAEnv, VDA9Env, SetSizeEnv, LuoMaunsellEnv, KrauzlisEnv, VDAExclusionEnv, VDASetSizeEnv, FixedGridVDASetSizeEnv, DelayProbeEnv)  # type: ignore
    from luo2015 import LuoMaunsell2015Sensitivity, LuoMaunsell2015Criterion  # type: ignore

TASKS = {
    "validity4":    dict(make=lambda **k: Validity4Env(**k),               grid=(2, 2)),
    "vda4":         dict(make=lambda **k: VDAEnv(**k),                     grid=(2, 2)),
    "vda9":         dict(make=lambda **k: VDA9Env(**k),                    grid=(3, 3)),
    "vda1":         dict(make=lambda **k: VDASetSizeEnv(set_size=1, **k),                         grid=(2, 2)),   # value-directed set-size 1 on the 2x2 grid (target alone)
    "vda2":         dict(make=lambda **k: VDASetSizeEnv(set_size=2, **k),                         grid=(2, 2)),   # value-directed set-size 2 on the 2x2 grid
    "vda_excl":     dict(make=lambda **k: VDAExclusionEnv(**k),                                   grid=(1, 2)),   # distractor-exclusion (1-vs-2 interleaved)
    "vda16":        dict(make=lambda **k: VDAEnv(grid_rows=4, grid_cols=4, image_size=100, **k),  grid=(4, 4)),   # value-directed, set-size 16
    "vda_fixed1":   dict(make=lambda **k: FixedGridVDASetSizeEnv(set_size=1, **k),  grid=(4, 4)),
    "vda_fixed2":   dict(make=lambda **k: FixedGridVDASetSizeEnv(set_size=2, **k),  grid=(4, 4)),
    "vda_fixed4":   dict(make=lambda **k: FixedGridVDASetSizeEnv(set_size=4, **k),  grid=(4, 4)),
    "vda_fixed9":   dict(make=lambda **k: FixedGridVDASetSizeEnv(set_size=9, **k),  grid=(4, 4)),
    "vda_fixed16":  dict(make=lambda **k: FixedGridVDASetSizeEnv(set_size=16, **k), grid=(4, 4)),
    "setsize2":     dict(make=lambda **k: SetSizeEnv(set_size=2, **k),     grid=(1, 2)),
    "setsize4":     dict(make=lambda **k: SetSizeEnv(set_size=4, **k),     grid=(2, 2)),
    "setsize9":     dict(make=lambda **k: SetSizeEnv(set_size=9, **k),     grid=(3, 3)),
    "luo_maunsell_sensitivity": dict(make=lambda **k: LuoMaunsellEnv(session="sensitivity", **k), grid=(2, 2)),
    "luo_maunsell_criterion":   dict(make=lambda **k: LuoMaunsellEnv(session="criterion", **k),   grid=(2, 2)),
    "luo2015_sensitivity": dict(make=lambda **k: LuoMaunsell2015Sensitivity(**k), grid=(2, 2)),   # FAITHFUL: no cue, sample->delay->test
    "luo2015_criterion":   dict(make=lambda **k: LuoMaunsell2015Criterion(**k),   grid=(2, 2)),   # FAITHFUL: no cue, sample->delay->test
    "krauzlis":     dict(make=lambda **k: KrauzlisEnv(**k),                grid=(2, 2)),
    "vda_probe_cued":   dict(make=lambda **k: DelayProbeEnv(probe_loc="cued", **k),   grid=(2, 2)),   # Awh-1998 delay-probe at the MEMORIZED (cued) location
    "vda_probe_uncued": dict(make=lambda **k: DelayProbeEnv(probe_loc="uncued", **k), grid=(2, 2)),   # delay-probe at an UNCUED location (control)
}


def make_env(task: str, **kw):
    if task not in TASKS:
        raise ValueError(f"unknown task {task!r}; choices: {sorted(TASKS)}")
    return TASKS[task]["make"](**kw)


def task_grid(task: str):
    return TASKS[task]["grid"]


__all__ = ["TASKS", "make_env", "task_grid", "BaseChangeDetectionEnv",
           "Validity4Env", "VDAEnv", "VDA9Env", "SetSizeEnv", "LuoMaunsellEnv", "KrauzlisEnv",
           "VDAExclusionEnv", "VDASetSizeEnv", "FixedGridVDASetSizeEnv", "DelayProbeEnv"]
