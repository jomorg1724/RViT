from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import torch

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts import resume_vda16  # noqa: E402


def _checkpoint(path: Path, iteration: int, mtime_ns: int) -> Path:
    path.parent.mkdir(parents=True)
    torch.save({"iter": iteration, "model_state_dict": {"weight": torch.ones(1)}}, path)
    os.utime(path, ns=(mtime_ns, mtime_ns))
    return path


def test_find_latest_checkpoint_selects_newest_vda16_rolling_checkpoint(tmp_path):
    older = _checkpoint(
        tmp_path / "vda16_crossattn1_d256" / "rvit_plus_rl_latest.pt",
        iteration=799,
        mtime_ns=10,
    )
    newest = _checkpoint(
        tmp_path / "vda16_affine_ew_d128" / "rvit_plus_rl_latest.pt",
        iteration=599,
        mtime_ns=20,
    )
    _checkpoint(
        tmp_path / "vda9_affine_ew_d128" / "rvit_plus_rl_latest.pt",
        iteration=999,
        mtime_ns=30,
    )

    selected = resume_vda16.find_latest_checkpoint(tmp_path)

    assert selected == newest
    assert selected != older


def test_build_resume_plan_continues_global_iteration_in_new_run_directory(tmp_path):
    checkpoint = _checkpoint(
        tmp_path / "source" / "vda16_affine_ew_d128" / "rvit_plus_rl_latest.pt",
        iteration=599,
        mtime_ns=20,
    )
    output_root = tmp_path / "resumed"

    plan = resume_vda16.build_resume_plan(
        checkpoint=checkpoint,
        trainer=_ROOT / "train_rl.py",
        output_root=output_root,
        device="mps",
        target_iteration=20_000,
        run_stamp="20260711T120000Z",
    )

    assert plan.checkpoint_iteration == 599
    assert plan.start_iteration == 600
    assert plan.additional_iterations == 19_400
    assert plan.feedback == "affine_ew"
    assert plan.d_mem == 128
    assert plan.output_dir == output_root / "vda16_affine_ew_d128_from_iter0600_20260711T120000Z"
    assert plan.output_dir != checkpoint.parent
    assert plan.command[0] == sys.executable
    assert plan.command[plan.command.index("--checkpoint-path") + 1] == str(checkpoint.resolve())
    assert plan.command[plan.command.index("--checkpoint-dir") + 1] == str(plan.output_dir.resolve())
    assert plan.command[plan.command.index("--start-iteration") + 1] == "600"
    assert plan.command[plan.command.index("--iters") + 1] == "19400"
    assert plan.command[plan.command.index("--device") + 1] == "mps"
    assert plan.command[plan.command.index("--init-mode") + 1] == "warm_start"
    for required_flag in ("--task", "--curriculum", "--conv-frontend", "--jepa-coef"):
        assert required_flag in plan.command


def test_build_resume_plan_refuses_completed_target(tmp_path):
    checkpoint = _checkpoint(
        tmp_path / "vda16_affine_ew_d128" / "rvit_plus_rl_latest.pt",
        iteration=599,
        mtime_ns=20,
    )

    with pytest.raises(ValueError, match="already reached"):
        resume_vda16.build_resume_plan(
            checkpoint=checkpoint,
            trainer=_ROOT / "train_rl.py",
            output_root=tmp_path / "resumed",
            device="mps",
            target_iteration=600,
            run_stamp="20260711T120000Z",
        )


def test_training_iteration_numbers_continue_from_checkpoint_global_iteration():
    from ppo import training_iteration_numbers

    assert list(training_iteration_numbers(start_iteration=600, n_iterations=3)) == [600, 601, 602]


def test_training_cli_accepts_explicit_global_start_iteration():
    from train_rl import build_arg_parser

    args = build_arg_parser().parse_args(["--start-iteration", "600", "--iters", "19400"])

    assert args.start_iteration == 600
    assert args.iters == 19_400


def test_fresh_seed_initializes_python_random_too():
    import random
    from train_rl import seed_training_rngs

    seed_training_rngs(37)
    first = random.random()
    seed_training_rngs(37)

    assert random.random() == first


def test_fresh_vda16_launcher_activates_workspace_venv_and_uses_full_training_flags():
    launcher = _ROOT / "scripts" / "launch_vda16_fresh.sh"
    content = launcher.read_text(encoding="utf-8")

    assert 'cd "$WORKSPACE_ROOT"' in content
    assert 'source .venv/bin/activate' in content
    assert "python3 RViT_plus_paper_jepa_grid9/train_rl.py" in content
    assert "uuid.uuid4().hex" in content
    assert 'mkdir "$CHECKPOINT_DIR"' in content
    assert "replay_excluded" in content
    for expected in (
        "--task vda16",
        "--init-mode fresh",
        "--cell xlstm",
        "--feedback affine_ew",
        "--conv-frontend",
        "--jepa-coef 0.5",
        "--d-mem 128",
        "--curriculum",
        "--iters 20000",
        "--schedule-final-iteration 19999",
        "--episodes-per-iter 8",
        "--save-every 50",
        "--log-every 1",
        "--device mps",
    ):
        assert expected in content
