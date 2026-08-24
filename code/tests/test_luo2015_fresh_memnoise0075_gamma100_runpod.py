from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "experiments" / "luo2015_episodic" / "fresh_grid2_memnoise0106667_gamma100_reward_matrix_runpod"
NEW = ROOT / "experiments" / "luo2015_episodic" / "fresh_grid2_memnoise0075_gamma100_reward_matrix_runpod"
PARENT_NOISE = 0.10666666666666666
NOISE = 0.075
CELLS = {
    "sensitivity_loc0": ("luo2015_sensitivity", "0", 1.0 / 3.0),
    "sensitivity_loc3": ("luo2015_sensitivity", "3", 1.0 / 3.0),
    "criterion_loc0": ("luo2015_criterion", "0", 1.0 / 0.95),
    "criterion_loc3": ("luo2015_criterion", "3", 1.0 / 0.95),
}


def bash_exe() -> str:
    candidate = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(candidate) if candidate.exists() else (shutil.which("bash") or "bash")


def command(script: Path, cell: str, root: str) -> list[str]:
    env = os.environ.copy()
    env.update({"DRY_RUN": "1", "CELL": cell, "RUN_ROOT": root})
    p = subprocess.run([bash_exe(), str(script)], cwd=ROOT, env=env,
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip().split()


def value(cmd: list[str], flag: str) -> str:
    return cmd[cmd.index(flag) + 1]


def normalize(cmd: list[str]) -> list[str]:
    out = list(cmd)
    for flag, sentinel in (("--memory-noise-std", "<MEMORY_NOISE>"),
                           ("--checkpoint-dir", "<RUN_ROOT>"),
                           ("--experiment-launcher", "<LAUNCHER>")):
        out[out.index(flag) + 1] = sentinel
    return out


def test_manifest_declares_memory_noise_only_followup() -> None:
    m = json.loads((NEW / "experiment_manifest.json").read_text(encoding="utf-8"))
    assert m["gamma"] == 1.0
    assert m["parent_memory_noise_sd"] == PARENT_NOISE
    assert m["memory_noise_sd"] == NOISE
    assert m["changed_variable"] == "memory_noise_sd"
    assert m["initialization"] == "fresh_seed_0"
    assert m["iterations"] == 20_000
    assert m["theta"] == 65.0 and m["curriculum"] is False
    assert m["sensory_orientation_noise_sd"] == 5.0
    assert set(m["cells"]) == set(CELLS)


def test_all_cells_have_exact_noise0075_contract() -> None:
    for cell, (task, location, scale) in CELLS.items():
        cmd = command(NEW / "launch_cell.sh", cell, f"/tmp/new/{cell}")
        assert value(cmd, "--task") == task
        assert value(cmd, "--high-loc") == location
        assert float(value(cmd, "--reward-scale")) == scale
        assert value(cmd, "--init-mode") == "fresh"
        assert float(value(cmd, "--gamma")) == 1.0
        assert float(value(cmd, "--memory-noise-std")) == NOISE
        assert float(value(cmd, "--noise")) == 5.0
        assert value(cmd, "--seed") == "0"
        assert value(cmd, "--iters") == "20000"
        assert value(cmd, "--theta-start") == "65.0"
        assert "--curriculum" not in cmd
        assert "--checkpoint-path" not in cmd


def test_parent_and_noise0075_differ_only_in_memory_noise_and_provenance_paths() -> None:
    for cell in CELLS:
        old = command(PARENT / "launch_cell.sh", cell, f"/tmp/old/{cell}")
        new = command(NEW / "launch_cell.sh", cell, f"/tmp/new/{cell}")
        assert float(value(old, "--memory-noise-std")) == PARENT_NOISE
        assert float(value(new, "--memory-noise-std")) == NOISE
        assert normalize(old) == normalize(new)


def test_scripts_have_valid_shell_syntax() -> None:
    for name in ("launch_cell.sh", "bootstrap_runpod.sh"):
        p = subprocess.run([bash_exe(), "-n", str(NEW / name)], cwd=ROOT,
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
