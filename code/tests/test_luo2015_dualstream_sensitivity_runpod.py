from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "luo2015_episodic"
    / "fresh_dualstream_grid2_memnoise0075_gamma100_bc000_sensitivity_runpod"
)
CELLS = {
    "sensitivity_loc0": ("luo2015_sensitivity", "0"),
    "sensitivity_loc3": ("luo2015_sensitivity", "3"),
}


def bash_exe() -> str:
    candidate = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(candidate) if candidate.exists() else (shutil.which("bash") or "bash")


def run_launcher(cell: str, root: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({
        "DRY_RUN": "1",
        "CELL": cell,
        "RUN_ROOT": root,
        "ITERS": "20000",
        "START_ITERATION": "0",
        "SAVE_EVERY": "50",
        "DEVICE": "cuda",
    })
    return subprocess.run(
        [bash_exe(), str(EXPERIMENT / "launch_cell.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def command(cell: str) -> list[str]:
    result = run_launcher(cell, f"/tmp/dual/{cell}")
    assert result.returncode == 0, result.stderr
    return result.stdout.strip().split()


def value(cmd: list[str], flag: str) -> str:
    return cmd[cmd.index(flag) + 1]


def test_manifest_binds_dualstream_sensitivity_only_contract() -> None:
    manifest = json.loads(
        (EXPERIMENT / "experiment_manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["design"] == "fresh_dual_actor_critic_sensitivity_counterphase"
    assert set(manifest["cells"]) == set(CELLS)
    assert manifest["task_family"] == "luo2015_sensitivity"
    assert manifest["dual_actor_critic_streams"] is True
    assert manifest["actor_critic_parameter_sharing"] == "none"
    assert manifest["independent_jepa_branches"] == ["actor", "critic"]
    assert manifest["jepa_coef_per_branch"] == 0.5
    assert manifest["bc_alpha"] == 0.0
    assert manifest["gamma"] == 1.0
    assert manifest["memory_noise_sd"] == 0.075
    assert manifest["sensory_orientation_noise_sd"] == 5.0
    assert manifest["theta"] == 65.0
    assert manifest["curriculum"] is False
    assert manifest["iterations"] == 20_000
    assert manifest["initialization"] == "fresh_seed_0"


def test_both_launches_bind_exact_dualstream_bc000_contract() -> None:
    for cell, (task, location) in CELLS.items():
        cmd = command(cell)
        assert value(cmd, "--task") == task
        assert value(cmd, "--high-loc") == location
        assert value(cmd, "--reward-scale") == "0.3333333333333333"
        assert "--dual-actor-critic-streams" in cmd
        assert value(cmd, "--bc-alpha") == "0.0"
        assert value(cmd, "--jepa-coef") == "0.5"
        assert value(cmd, "--memory-noise-std") == "0.075"
        assert value(cmd, "--noise") == "5.0"
        assert value(cmd, "--gamma") == "1.0"
        assert value(cmd, "--cell") == "xlstm"
        assert value(cmd, "--feedback") == "crossattn1"
        assert value(cmd, "--d-mem") == "32"
        assert value(cmd, "--init-mode") == "fresh"
        assert value(cmd, "--iters") == "20000"
        assert value(cmd, "--seed") == "0"
        assert value(cmd, "--theta-start") == "65.0"
        assert "--curriculum" not in cmd


def test_launcher_rejects_criterion_cells() -> None:
    result = run_launcher("criterion_loc0", "/tmp/dual/criterion_loc0")

    assert result.returncode != 0
    assert "invalid CELL" in result.stderr


def test_scripts_have_valid_shell_syntax_and_lf_endings() -> None:
    for name in ("launch_cell.sh", "bootstrap_runpod.sh"):
        path = EXPERIMENT / name
        assert b"\r" not in path.read_bytes()
        result = subprocess.run(
            [bash_exe(), "-n", str(path)], cwd=ROOT, capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr
