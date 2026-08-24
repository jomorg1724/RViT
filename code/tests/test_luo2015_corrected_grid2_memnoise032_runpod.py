from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "experiments" / "luo2015_episodic" / "corrected_orientation_grid_compare_runpod"
NEW = ROOT / "experiments" / "luo2015_episodic" / "corrected_grid2_memnoise032_runpod"


def bash_exe() -> str:
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(git_bash) if git_bash.exists() else (shutil.which("bash") or "bash")


def dry(script: Path, *, grid: int | None, run_root: str) -> str:
    env = os.environ.copy()
    env.update({"DRY_RUN": "1", "RUN_ROOT": run_root})
    if grid is not None:
        env["GRID"] = str(grid)
    p = subprocess.run([bash_exe(), str(script)], cwd=ROOT, env=env, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.strip()


def test_memnoise032_manifest_is_single_variable_followup() -> None:
    m = json.loads((NEW / "experiment_manifest.json").read_text(encoding="utf-8"))
    assert m["task_contract"]["orientation_sampling"] == "independent_uniform_axial_0_180"
    assert m["task_contract"]["signed_change_sampling"] == "uniform(-theta,+theta)"
    assert m["patch_grid"] == [2, 2]
    assert m["memory_noise_sd"] == 0.32
    assert m["parent_run"]["memory_noise_sd"] == 0.64
    assert m["changed_variable"] == "memory_noise_sd"
    assert m["initialization"] == "fresh"


def test_memnoise032_command_differs_only_in_noise_and_root() -> None:
    old = dry(OLD / "launch_neutral.sh", grid=2, run_root="/tmp/old_grid2_noise064")
    new = dry(NEW / "launch_neutral.sh", grid=None, run_root="/tmp/new_grid2_noise032")
    old_normalized = old.replace("--memory-noise-std 0.64", "--memory-noise-std NOISE").replace(
        "/tmp/old_grid2_noise064", "RUN_ROOT"
    )
    new_normalized = new.replace("--memory-noise-std 0.32", "--memory-noise-std NOISE").replace(
        "/tmp/new_grid2_noise032", "RUN_ROOT"
    )
    assert old_normalized == new_normalized


def test_memnoise032_scripts_are_valid_shell() -> None:
    for name in ("launch_neutral.sh", "bootstrap_runpod.sh"):
        p = subprocess.run([bash_exe(), "-n", str(NEW / name)], cwd=ROOT, capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
