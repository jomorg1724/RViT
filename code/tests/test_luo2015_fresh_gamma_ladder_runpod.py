from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "luo2015_episodic" / "fresh_grid2_memnoise032_gamma_ladder_runpod"
GAMMAS = [0.8, 0.9, 1.0]
CELLS = {
    "sensitivity_loc0": ("luo2015_sensitivity", "0", 1.0 / 3.0),
    "sensitivity_loc3": ("luo2015_sensitivity", "3", 1.0 / 3.0),
    "criterion_loc0": ("luo2015_criterion", "0", 1.0 / 0.95),
    "criterion_loc3": ("luo2015_criterion", "3", 1.0 / 0.95),
}


def bash_exe() -> str:
    candidate = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(candidate) if candidate.exists() else (shutil.which("bash") or "bash")


def dry(cell: str, gamma: float) -> list[str]:
    env = os.environ.copy()
    env.update({"DRY_RUN": "1", "CELL": cell, "GAMMA": str(gamma),
                "RUN_ROOT": f"/tmp/{cell}/gamma{gamma}"})
    p = subprocess.run([bash_exe(), str(EXP / "launch_cell.sh")], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip().split()


def value(command: list[str], flag: str) -> str:
    return command[command.index(flag) + 1]


def test_manifest_registers_fresh_sequential_ladder() -> None:
    manifest = json.loads((EXP / "experiment_manifest.json").read_text(encoding="utf-8"))
    assert manifest["gammas"] == GAMMAS
    assert manifest["stage_transition"] == "automatic_per_cell_after_verified_completion"
    assert manifest["initialization_each_stage"] == "fresh_seed_0"
    assert manifest["weights_carried_between_gammas"] is False
    assert manifest["iterations_per_gamma"] == 20_000
    assert manifest["theta"] == 65.0
    assert manifest["curriculum"] is False
    assert set(manifest["cells"]) == set(CELLS)


def test_every_cell_and_gamma_launches_fresh_exact_contract() -> None:
    for cell, (task, location, scale) in CELLS.items():
        for gamma in GAMMAS:
            command = dry(cell, gamma)
            assert value(command, "--task") == task
            assert value(command, "--high-loc") == location
            assert float(value(command, "--reward-scale")) == scale
            assert float(value(command, "--gamma")) == gamma
            assert value(command, "--init-mode") == "fresh"
            assert "--checkpoint-path" not in command
            assert "--expected-parent-sha256" not in command
            assert value(command, "--seed") == "0"
            assert value(command, "--iters") == "20000"
            assert value(command, "--theta-start") == "65.0"
            assert "--curriculum" not in command
            assert value(command, "--patch-grid-rows") == "2"
            assert value(command, "--patch-grid-cols") == "2"
            assert value(command, "--memory-noise-std") == "0.32"


def test_ladder_dry_run_emits_three_ordered_fresh_commands() -> None:
    env = os.environ.copy()
    env.update({"DRY_RUN": "1", "CELL": "criterion_loc0",
                "LADDER_ROOT": "/tmp/ladder"})
    p = subprocess.run([bash_exe(), str(EXP / "run_ladder.sh")], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    lines = [line for line in p.stdout.splitlines() if "train_rl.py" in line]
    assert len(lines) == 3
    assert [float(value(line.split(), "--gamma")) for line in lines] == GAMMAS
    assert all(value(line.split(), "--init-mode") == "fresh" for line in lines)


def test_scripts_have_valid_shell_syntax() -> None:
    for name in ("launch_cell.sh", "run_ladder.sh", "bootstrap_runpod.sh"):
        p = subprocess.run([bash_exe(), "-n", str(EXP / name)], cwd=ROOT,
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
