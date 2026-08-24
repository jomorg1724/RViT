from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "luo2015_episodic" / "fresh_dualstream_dmem64_grid2_memnoise0075_gamma100_bc000_curriculum_sensitivity_runpod"
CELLS = {"sensitivity_loc0": "0", "sensitivity_loc3": "3"}


def bash_exe() -> str:
    candidate = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(candidate) if candidate.exists() else (shutil.which("bash") or "bash")


def run_launcher(cell: str, root: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({"DRY_RUN":"1","CELL":cell,"RUN_ROOT":root,"ITERS":"20000",
                "START_ITERATION":"0","SAVE_EVERY":"50","DEVICE":"cuda"})
    return subprocess.run([bash_exe(), str(EXPERIMENT / "launch_cell.sh")], cwd=ROOT,
                          env=env, capture_output=True, text=True)


def command(cell: str) -> list[str]:
    result = run_launcher(cell, f"/tmp/dmem64/{cell}")
    assert result.returncode == 0, result.stderr
    return result.stdout.strip().split()


def value(cmd: list[str], flag: str) -> str:
    return cmd[cmd.index(flag)+1]


def test_manifest_binds_dmem64_curriculum_sensitivity_contract() -> None:
    manifest=json.loads((EXPERIMENT/"experiment_manifest.json").read_text(encoding="utf-8"))
    assert manifest["design"] == "fresh_dualstream_dmem64_curriculum_sensitivity_counterphase"
    assert set(manifest["cells"]) == set(CELLS)
    assert manifest["task_family"] == "luo2015_sensitivity"
    assert manifest["changed_variable"] == {"name":"d_mem_per_branch","parent":32,"followup":64}
    assert manifest["dual_actor_critic_streams"] is True
    assert manifest["memory_dim_per_branch"] == 64
    assert manifest["bc_alpha"] == 0.0
    assert manifest["gamma"] == 1.0
    assert manifest["memory_noise_sd"] == 0.075
    assert manifest["curriculum"] == {"enabled":True,"theta_start":65.0,"window_valid_sdt_trials":1000,
                                      "threshold":0.85,"step_degrees":3.0,"floor_degrees":8.0}
    assert manifest["initialization"] == "fresh_seed_0"
    assert manifest["iterations"] == 20_000


def test_launches_bind_exact_memory_and_curriculum_contract() -> None:
    for cell, location in CELLS.items():
        cmd=command(cell)
        assert value(cmd,"--task") == "luo2015_sensitivity"
        assert value(cmd,"--high-loc") == location
        assert value(cmd,"--d-mem") == "64"
        assert "--dual-actor-critic-streams" in cmd
        assert value(cmd,"--bc-alpha") == "0.0"
        assert value(cmd,"--jepa-coef") == "0.5"
        assert value(cmd,"--memory-noise-std") == "0.075"
        assert value(cmd,"--noise") == "5.0"
        assert value(cmd,"--gamma") == "1.0"
        assert value(cmd,"--reward-scale") == "0.3333333333333333"
        assert value(cmd,"--seed") == "0"
        assert value(cmd,"--init-mode") == "fresh"
        assert value(cmd,"--iters") == "20000"
        assert "--curriculum" in cmd
        assert value(cmd,"--theta-start") == "65.0"
        assert value(cmd,"--curr-window") == "1000"
        assert value(cmd,"--curr-threshold") == "0.85"
        assert value(cmd,"--curr-step") == "3.0"
        assert value(cmd,"--curr-floor") == "8.0"


def test_launcher_rejects_criterion_and_scripts_are_portable() -> None:
    bad=run_launcher("criterion_loc0","/tmp/dmem64/criterion")
    assert bad.returncode != 0 and "invalid CELL" in bad.stderr
    for name in ("launch_cell.sh","bootstrap_runpod.sh"):
        path=EXPERIMENT/name
        assert b"\r" not in path.read_bytes()
        syntax=subprocess.run([bash_exe(),"-n",str(path)],cwd=ROOT,capture_output=True,text=True)
        assert syntax.returncode == 0, syntax.stderr
