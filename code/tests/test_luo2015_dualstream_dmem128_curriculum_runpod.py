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
    / "fresh_dualstream_dmem128_grid2_memnoise0075_gamma100_bc000_curriculum_sensitivity_runpod"
)


def test_manifest_binds_dmem128_single_variable_followup() -> None:
    manifest = json.loads((EXPERIMENT / "experiment_manifest.json").read_text(encoding="utf-8"))
    assert manifest["design"] == "fresh_dualstream_dmem128_curriculum_sensitivity_counterphase"
    assert manifest["changed_variable"] == {
        "name": "d_mem_per_branch",
        "parent": 64,
        "followup": 128,
    }
    assert set(manifest["cells"]) == {"sensitivity_loc0", "sensitivity_loc3"}
    assert manifest["memory_dim_per_branch"] == 128
    assert manifest["hidden_memory_scalars_per_branch"] == 512
    assert manifest["full_xlstm_state_scalars_per_branch"] == 2048
    assert manifest["full_xlstm_state_scalars_two_streams"] == 4096
    assert manifest["dual_actor_critic_streams"] is True
    assert manifest["jepa_coef_per_branch"] == 0.5
    assert manifest["jepa_teacher_ema"] == 0.996
    assert manifest["memory_noise_sd"] == 0.075
    assert manifest["sensory_orientation_noise_sd"] == 5.0
    assert manifest["bc_alpha"] == 0.0
    assert manifest["gamma"] == 1.0
    assert manifest["curriculum"] == {
        "enabled": True,
        "theta_start": 65.0,
        "window_valid_sdt_trials": 1000,
        "threshold": 0.85,
        "step_degrees": 3.0,
        "floor_degrees": 8.0,
    }
    assert manifest["initialization"] == "fresh_seed_0"
    assert manifest["iterations"] == 20_000


def _bash_exe() -> str:
    candidate = Path(r"C:\Program Files\Git\bin\bash.exe")
    return str(candidate) if candidate.exists() else (shutil.which("bash") or "bash")


def _dry_command(experiment: Path, cell: str, run_root: str) -> list[str]:
    env = os.environ.copy()
    env.update(
        {
            "DRY_RUN": "1",
            "CELL": cell,
            "RUN_ROOT": run_root,
            "ITERS": "20000",
            "START_ITERATION": "0",
            "SAVE_EVERY": "50",
            "DEVICE": "cuda",
        }
    )
    result = subprocess.run(
        [_bash_exe(), str(experiment / "launch_cell.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip().split()


def _value(command: list[str], flag: str) -> str:
    return command[command.index(flag) + 1]


def test_launches_bind_dmem128_and_match_parent_except_width_and_root() -> None:
    parent = (
        ROOT
        / "experiments"
        / "luo2015_episodic"
        / "fresh_dualstream_dmem64_grid2_memnoise0075_gamma100_bc000_curriculum_sensitivity_runpod"
    )
    for cell, location in {"sensitivity_loc0": "0", "sensitivity_loc3": "3"}.items():
        command = _dry_command(EXPERIMENT, cell, f"/tmp/dmem128/{cell}")
        parent_command = _dry_command(parent, cell, f"/tmp/dmem64/{cell}")
        assert _value(command, "--d-mem") == "128"
        assert _value(command, "--high-loc") == location
        assert "--dual-actor-critic-streams" in command
        assert "--curriculum" in command
        assert _value(command, "--theta-start") == "65.0"
        assert _value(command, "--curr-window") == "1000"
        assert _value(command, "--curr-threshold") == "0.85"
        assert _value(command, "--curr-step") == "3.0"
        assert _value(command, "--curr-floor") == "8.0"
        assert _value(command, "--memory-noise-std") == "0.075"
        assert _value(command, "--noise") == "5.0"
        assert _value(command, "--gamma") == "1.0"
        assert _value(command, "--bc-alpha") == "0.0"
        assert _value(command, "--jepa-coef") == "0.5"
        assert _value(command, "--init-mode") == "fresh"
        normalized = list(command)
        normalized[normalized.index("--d-mem") + 1] = "64"
        normalized[normalized.index("--checkpoint-dir") + 1] = _value(
            parent_command, "--checkpoint-dir"
        )
        normalized[normalized.index("--experiment-launcher") + 1] = _value(
            parent_command, "--experiment-launcher"
        )
        assert normalized == parent_command


def test_package_rejects_criterion_and_bootstrap_binds_dmem128() -> None:
    env = os.environ.copy()
    env.update(
        {
            "DRY_RUN": "1",
            "CELL": "criterion_loc0",
            "RUN_ROOT": "/tmp/dmem128/criterion",
            "ITERS": "20000",
            "START_ITERATION": "0",
            "SAVE_EVERY": "50",
            "DEVICE": "cuda",
        }
    )
    rejected = subprocess.run(
        [_bash_exe(), str(EXPERIMENT / "launch_cell.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert "invalid CELL" in rejected.stderr
    bootstrap = (EXPERIMENT / "bootstrap_runpod.sh").read_text(encoding="utf-8")
    assert "tests/test_luo2015_dualstream_dmem128_curriculum_runpod.py" in bootstrap
    assert "assert int(a['d_mem'])==128" in bootstrap
    assert "assert int(c['model_kwargs']['d_mem'])==128" in bootstrap
    assert '"d_mem_per_branch":128' in bootstrap
    for name in ("launch_cell.sh", "bootstrap_runpod.sh"):
        path = EXPERIMENT / name
        assert b"\r" not in path.read_bytes()
        syntax = subprocess.run(
            [_bash_exe(), "-n", str(path)], cwd=ROOT, capture_output=True, text=True
        )
        assert syntax.returncode == 0, syntax.stderr
