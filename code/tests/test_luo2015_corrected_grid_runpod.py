from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "luo2015_episodic" / "corrected_orientation_grid_compare_runpod"


def _bash() -> str:
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if git_bash.exists():
        return str(git_bash)
    resolved = shutil.which("bash")
    assert resolved is not None, "bash is required"
    return resolved


def _dry_command(grid: int, tmp_path: Path) -> str:
    env = os.environ.copy()
    env.update(
        {
            "DRY_RUN": "1",
            "GRID": str(grid),
            "RUN_ROOT": f"/tmp/luo_test_grid{grid}",
        }
    )
    proc = subprocess.run(
        [_bash(), str(EXP / "launch_neutral.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def test_manifest_changes_only_model_visual_grid() -> None:
    manifest = json.loads((EXP / "experiment_manifest.json").read_text(encoding="utf-8"))
    assert manifest["task_contract"]["orientation_sampling"] == "independent_uniform_axial_0_180"
    assert manifest["task_contract"]["signed_change_sampling"] == "uniform(-theta,+theta)"
    assert manifest["task_contract"]["curriculum_changes_only"] == "theta"
    assert manifest["initialization"] == "fresh"
    assert manifest["automatic_children"] is False
    assert manifest["comparison"]["changed_variable"] == "model_patch_grid"
    assert manifest["comparison"]["conditions"] == [
        {"name": "dense_grid20", "patch_grid": [20, 20], "visual_tokens": 400},
        {"name": "coarse_grid2", "patch_grid": [2, 2], "visual_tokens": 4},
    ]


def test_two_launches_hold_training_contract_fixed(tmp_path: Path) -> None:
    grid20 = _dry_command(20, tmp_path)
    grid2 = _dry_command(2, tmp_path)

    normalized20 = grid20.replace("--patch-grid-rows 20", "--patch-grid-rows GRID").replace(
        "--patch-grid-cols 20", "--patch-grid-cols GRID"
    ).replace("/tmp/luo_test_grid20", "RUN_ROOT")
    normalized2 = grid2.replace("--patch-grid-rows 2", "--patch-grid-rows GRID").replace(
        "--patch-grid-cols 2", "--patch-grid-cols GRID"
    ).replace("/tmp/luo_test_grid2", "RUN_ROOT")
    assert normalized20 == normalized2

    required = {
        "--cell xlstm",
        "--feedback crossattn1",
        "--memory-decay 1.0",
        "--memory-noise-std 0.64",
        "--noise 5.0",
        "--jepa-coef 0.5",
        "--d-mem 32",
        "--episodes-per-iter 8",
        "--seed 0",
        "--iters 20000",
        "--init-mode fresh",
        "--r-hit 1.0",
        "--r-cr 1.0",
        "--theta-start 65.0",
        "--curr-floor 18.0",
    }
    for fragment in required:
        assert fragment in grid20
        assert fragment in grid2


def test_launch_and_bootstrap_scripts_are_valid_shell() -> None:
    for name in ("launch_neutral.sh", "bootstrap_runpod.sh"):
        proc = subprocess.run(
            [_bash(), "-n", str(EXP / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
