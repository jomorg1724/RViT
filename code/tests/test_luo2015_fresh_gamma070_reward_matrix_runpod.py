from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "luo2015_episodic" / "fresh_grid2_memnoise032_gamma070_reward_matrix_runpod"
CELLS = {
    "sensitivity_loc0": ("luo2015_sensitivity", "0", str(1.0 / 3.0)),
    "sensitivity_loc3": ("luo2015_sensitivity", "3", str(1.0 / 3.0)),
    "criterion_loc0": ("luo2015_criterion", "0", str(1.0 / 0.95)),
    "criterion_loc3": ("luo2015_criterion", "3", str(1.0 / 0.95)),
}


def bash_exe() -> str:
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(git_bash) if git_bash.exists() else (shutil.which("bash") or "bash")


def dry(cell: str) -> list[str]:
    env = os.environ.copy()
    env.update({"DRY_RUN": "1", "CELL": cell, "RUN_ROOT": f"/tmp/{cell}"})
    p = subprocess.run([bash_exe(), str(EXP / "launch_cell.sh")], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    # %q output is shell-safe; these commands contain no spaces in individual values.
    return p.stdout.strip().split()


def value(command: list[str], flag: str) -> str:
    return command[command.index(flag) + 1]


def test_manifest_registers_exact_fresh_four_cell_design() -> None:
    m = json.loads((EXP / "experiment_manifest.json").read_text(encoding="utf-8"))
    assert m["design"] == "fresh_counterphased_reward_objectives"
    assert m["initialization"] == "fresh_identical_seed_per_cell"
    assert m["discount_factor"] == 0.7
    assert m["patch_grid"] == [2, 2]
    assert m["memory_noise_sd"] == 0.32
    assert m["theta"] == 65.0
    assert m["curriculum"] is False
    assert set(m["cells"]) == set(CELLS)
    assert m["task_contract"]["orientation_sampling"] == "independent_uniform_axial_0_180"


def test_each_cell_is_fresh_gamma070_and_has_exact_reward_assignment() -> None:
    for cell, (task, loc, scale) in CELLS.items():
        command = dry(cell)
        assert value(command, "--task") == task
        assert value(command, "--high-loc") == loc
        assert float(value(command, "--reward-scale")) == float(scale)
        assert value(command, "--init-mode") == "fresh"
        assert "--checkpoint-path" not in command
        assert "--expected-parent-sha256" not in command
        assert value(command, "--gamma") == "0.7"
        assert value(command, "--theta-start") == "65.0"
        assert "--curriculum" not in command
        assert value(command, "--patch-grid-rows") == "2"
        assert value(command, "--patch-grid-cols") == "2"
        assert value(command, "--memory-noise-std") == "0.32"
        assert value(command, "--d-mem") == "32"
        assert value(command, "--seed") == "0"
        assert value(command, "--iters") == "20000"


def test_commands_differ_only_in_registered_condition_fields_and_output_root() -> None:
    normalized = []
    for cell in CELLS:
        command = dry(cell)
        for flag in ("--task", "--high-loc", "--reward-scale", "--checkpoint-dir"):
            command[command.index(flag) + 1] = flag.upper()
        normalized.append(command)
    assert all(command == normalized[0] for command in normalized[1:])


def test_scripts_have_valid_shell_syntax() -> None:
    for name in ("launch_cell.sh", "bootstrap_runpod.sh"):
        p = subprocess.run([bash_exe(), "-n", str(EXP / name)], cwd=ROOT,
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
