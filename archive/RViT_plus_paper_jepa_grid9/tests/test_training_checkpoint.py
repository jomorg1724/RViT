from __future__ import annotations

import copy
import csv
import random
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from envs.base import BaseChangeDetectionEnv  # noqa: E402
from ppo import (  # noqa: E402
    _capture_rng_state,
    _restore_rng_state,
    build_training_checkpoint,
    reconcile_metrics_for_resume,
    restore_training_checkpoint,
    validate_resume_contract,
)


def _trained_linear() -> tuple[torch.nn.Linear, torch.optim.Adam]:
    model = torch.nn.Linear(2, 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss = model(torch.ones(1, 2)).sum()
    loss.backward()
    optimizer.step()
    return model, optimizer


def test_environment_training_state_round_trips_theta_and_curriculum_window():
    env = BaseChangeDetectionEnv(curriculum=True)
    env.theta = 47.0
    env._recent_correct = [True, False, True]

    state = env.training_state_dict()
    env.theta = 8.0
    env._recent_correct = []
    env.load_training_state_dict(state)

    assert env.theta == 47.0
    assert env._recent_correct == [True, False, True]


def test_environment_training_state_rejects_nonfinite_theta_and_timeline_mismatch():
    env = BaseChangeDetectionEnv(curriculum=True)
    state = env.training_state_dict()
    state["theta"] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        env.load_training_state_dict(state)

    state = env.training_state_dict()
    state["environment_config"]["T"] += 1
    with pytest.raises(ValueError, match="environment configuration mismatch"):
        env.load_training_state_dict(state)


def test_full_checkpoint_contains_teacher_target_optimizer_theta_and_no_replay_buffer():
    model, optimizer = _trained_linear()
    target = torch.nn.Linear(2, 1)
    teacher = torch.nn.Linear(2, 1)
    env = BaseChangeDetectionEnv(curriculum=True)
    env.theta = 53.0
    env._recent_correct = [True, False]

    checkpoint = build_training_checkpoint(
        iteration=17,
        model=model,
        optimizer=optimizer,
        target_model=target,
        target_step=3,
        jepa_teacher=teacher,
        env=env,
        rolling_correct=[0.25, 0.5],
        rolling_return=[1.0, 2.0],
        metadata={"task": "vda16"},
    )

    assert checkpoint["checkpoint_schema_version"] == 3
    assert checkpoint["iter"] == 17
    assert checkpoint["optimizer_state_dict"]["state"]
    assert checkpoint["target_model_state_dict"]
    assert checkpoint["target_step"] == 3
    assert checkpoint["jepa_teacher_state_dict"]
    assert checkpoint["environment_state"]["theta"] == 53.0
    assert checkpoint["environment_state"]["recent_correct"] == [True, False]
    assert checkpoint["rolling_correct"] == [0.25, 0.5]
    assert checkpoint["rolling_return"] == [1.0, 2.0]
    assert "rng_state" in checkpoint
    assert "replay_buffer" not in checkpoint
    assert checkpoint["task"] == "vda16"


def test_full_checkpoint_restore_recovers_training_state_and_rng_streams():
    random.seed(12)
    np.random.seed(13)
    torch.manual_seed(14)
    model, optimizer = _trained_linear()
    target = torch.nn.Linear(2, 1)
    teacher = torch.nn.Linear(2, 1)
    with torch.no_grad():
        target.weight.fill_(2.0)
        teacher.weight.fill_(3.0)
    env = BaseChangeDetectionEnv(curriculum=True)
    env.theta = 41.0
    env._recent_correct = [True, True, False]

    checkpoint = build_training_checkpoint(
        iteration=29,
        model=model,
        optimizer=optimizer,
        target_model=target,
        target_step=7,
        jepa_teacher=teacher,
        env=env,
        rolling_correct=[0.4, 0.6],
        rolling_return=[1.5, 2.5],
        metadata={},
    )
    expected_random = random.random()
    expected_numpy = float(np.random.rand())
    expected_torch = float(torch.rand(()))

    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
        target.weight.zero_()
        teacher.weight.zero_()
    optimizer.state.clear()
    env.theta = 8.0
    env._recent_correct = []
    random.random()
    np.random.rand()
    torch.rand(())

    restored = restore_training_checkpoint(
        checkpoint,
        model=model,
        optimizer=optimizer,
        target_model=target,
        jepa_teacher=teacher,
        env=env,
    )

    assert optimizer.state
    assert torch.all(target.weight == 2.0)
    assert torch.all(teacher.weight == 3.0)
    assert env.theta == 41.0
    assert env._recent_correct == [True, True, False]
    assert restored == {
        "target_step": 7,
        "rolling_correct": [0.4, 0.6],
        "rolling_return": [1.5, 2.5],
    }
    assert random.random() == expected_random
    assert float(np.random.rand()) == expected_numpy
    assert float(torch.rand(())) == expected_torch


def test_metrics_resume_discards_rows_newer_than_checkpoint_before_append(tmp_path):
    metrics = tmp_path / "metrics.csv"
    with metrics.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["iter", "env/theta"])
        writer.writeheader()
        writer.writerows([
            {"iter": 0, "env/theta": 65.0},
            {"iter": 1, "env/theta": 65.0},
            {"iter": 2, "env/theta": 62.0},
        ])

    fieldnames = reconcile_metrics_for_resume(metrics, checkpoint_iteration=1)

    with metrics.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert fieldnames == ["iter", "env/theta"]
    assert [int(row["iter"]) for row in rows] == [0, 1]


def test_metrics_resume_rejects_duplicate_iterations(tmp_path):
    metrics = tmp_path / "metrics.csv"
    metrics.write_text("iter,env/theta\n0,65\n1,65\n1,62\n", encoding="utf-8")
    with pytest.raises(ValueError, match="strictly increasing"):
        reconcile_metrics_for_resume(metrics, checkpoint_iteration=1)


def test_checkpoint_metadata_cannot_overwrite_reserved_state():
    model, optimizer = _trained_linear()
    env = BaseChangeDetectionEnv(curriculum=True)
    with pytest.raises(ValueError, match="reserved"):
        build_training_checkpoint(
            iteration=1, model=model, optimizer=optimizer, target_model=None,
            target_step=0, jepa_teacher=None, env=env,
            rolling_correct=[], rolling_return=[], metadata={"iter": 999},
        )


def test_resume_contract_rejects_config_or_backend_changes():
    contract = {
        "task": "vda16", "model_kwargs": {"d_mem": 128},
        "ppo_config": {"gamma": 0.95}, "episodes_per_iter": 8,
        "schedule_final_iteration": 19999,
        "training_backend": "mps", "runtime_versions": {"torch": "2.12.0"},
        "producer_sha256": {"ppo.py": "abc"},
    }
    checkpoint = {"resume_contract": copy.deepcopy(contract)}
    validate_resume_contract(checkpoint, current_contract=contract, active_backend="mps")
    changed = copy.deepcopy(contract)
    changed["ppo_config"]["gamma"] = 0.99
    with pytest.raises(ValueError, match="ppo_config"):
        validate_resume_contract(checkpoint, current_contract=changed, active_backend="mps")
    with pytest.raises(ValueError, match="backend"):
        validate_resume_contract(checkpoint, current_contract=contract, active_backend="cuda")
    changed = copy.deepcopy(contract)
    changed["schedule_final_iteration"] = 699
    with pytest.raises(ValueError, match="schedule_final_iteration"):
        validate_resume_contract(checkpoint, current_contract=changed, active_backend="mps")


def test_resume_contract_allows_only_explicit_producer_transition():
    saved = {
        "task": "vda4", "model_kwargs": {"feedback": "crossattn1"},
        "ppo_config": {"gamma": 0.95}, "episodes_per_iter": 8,
        "schedule_final_iteration": 19999,
        "training_backend": "mps", "runtime_versions": {"torch": "2.12.0"},
        "producer_sha256": {
            "train_rl.py": "old-train", "ppo.py": "old-ppo", "model.py": "same-model",
        },
    }
    checkpoint = {"resume_contract": copy.deepcopy(saved)}
    current = copy.deepcopy(saved)
    current["producer_sha256"].update({"train_rl.py": "new-train", "ppo.py": "new-ppo"})

    validate_resume_contract(
        checkpoint,
        current_contract=current,
        active_backend="mps",
        allowed_producer_changes={"train_rl.py", "ppo.py"},
    )

    current["producer_sha256"]["model.py"] = "changed-model"
    with pytest.raises(ValueError, match="producer_sha256"):
        validate_resume_contract(
            checkpoint,
            current_contract=current,
            active_backend="mps",
            allowed_producer_changes={"train_rl.py", "ppo.py"},
        )


def test_schedule_overrun_requires_explicit_compatibility_transition():
    from ppo import validate_training_schedule_bounds

    with pytest.raises(ValueError, match="cannot precede"):
        validate_training_schedule_bounds(
            phase_final_iteration=22799,
            schedule_final_iteration=19999,
            allow_schedule_overrun=False,
        )

    validate_training_schedule_bounds(
        phase_final_iteration=22799,
        schedule_final_iteration=19999,
        allow_schedule_overrun=True,
    )


def test_cli_schedule_overrun_compatibility_is_resume_only():
    from train_rl import resolve_schedule_overrun_compatibility

    with pytest.raises(ValueError, match="allow-schedule-overrun-resume"):
        resolve_schedule_overrun_compatibility(
            init_mode="resume",
            phase_final_iteration=22799,
            schedule_final_iteration=19999,
            explicitly_allowed=False,
        )
    with pytest.raises(ValueError, match="requires --init-mode resume"):
        resolve_schedule_overrun_compatibility(
            init_mode="warm_start",
            phase_final_iteration=22799,
            schedule_final_iteration=19999,
            explicitly_allowed=True,
        )

    assert resolve_schedule_overrun_compatibility(
        init_mode="resume",
        phase_final_iteration=22799,
        schedule_final_iteration=19999,
        explicitly_allowed=True,
    ) == {"train_rl.py", "ppo.py"}

    from train_rl import build_arg_parser

    args = build_arg_parser().parse_args(["--allow-schedule-overrun-resume"])
    assert args.allow_schedule_overrun_resume is True


@torch.no_grad()
def test_rng_restore_accepts_checkpoint_loaded_onto_mps(tmp_path):
    if not torch.backends.mps.is_available():
        return
    path = tmp_path / "rng.pt"
    torch.save({"rng_state": _capture_rng_state()}, path)
    loaded = torch.load(path, map_location="mps", weights_only=False)

    _restore_rng_state(loaded["rng_state"], required_backend="mps")
    expected = torch.rand((), device="mps").cpu()
    _restore_rng_state(loaded["rng_state"], required_backend="mps")
    actual = torch.rand((), device="mps").cpu()
    assert torch.equal(actual, expected)


def test_training_loop_writes_complete_rolling_and_final_checkpoints(tmp_path, monkeypatch):
    import ppo

    class TinyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = torch.nn.Parameter(torch.tensor([1.0]))
            self.n_actions = 2
            self.n_quantiles = 5
            self.n_tokens = 1
            self.enc_layers = 1

    batch = ppo.RolloutBatch(
        observations=torch.zeros((1, 1, 1)),
        actions=torch.zeros((1, 1), dtype=torch.long),
        rewards=torch.ones((1, 1)),
        dones=torch.ones((1, 1)),
        valid_mask=torch.ones((1, 1)),
        old_log_probs=torch.zeros((1, 1)),
        old_V_scalar=torch.zeros((1, 1)),
        old_V_dist=torch.zeros((1, 1, 5)),
        last_V_dist=torch.zeros((1, 5)),
        lengths=torch.ones((1,), dtype=torch.long),
    )

    monkeypatch.setattr(
        ppo,
        "collect_episodes",
        lambda **kwargs: (
            batch,
            {
                "rollout/mean_return": 1.0,
                "rollout/mean_length": 1.0,
                "rollout/correct_rate": 1.0,
                "rollout/n_episodes": 1.0,
            },
        ),
    )

    def fake_update(model, optimizer, combined_batch, cfg, **kwargs):
        del combined_batch, cfg, kwargs
        optimizer.zero_grad(set_to_none=True)
        model.weight.square().sum().backward()
        optimizer.step()
        return {
            "loss_policy": 0.1,
            "loss_value": 0.2,
            "loss_entropy": -0.3,
            "loss_contrastive": 0.0,
            "loss_jepa": 0.4,
            "loss_total": 0.5,
            "approx_kl": 0.01,
            "n_updates": 1.0,
            "n_loss_evals": 1.0,
            "n_skipped": 0.0,
            "max_grad_elem": 2.0,
            "per_episode_priority": torch.ones(1),
        }

    monkeypatch.setattr(ppo, "ppo_update", fake_update)
    env = BaseChangeDetectionEnv(curriculum=True)
    cfg = ppo.PPOConfig(
        n_epochs=1,
        per_n_replay=0,
        ema_decay=0.9,
        target_update_period=0,
        jepa_coef=0.5,
    )

    ppo.train(
        TinyModel(),
        env,
        n_iterations=1,
        episodes_per_iter=1,
        cfg=cfg,
        device=torch.device("cpu"),
        log_every=10,
        checkpoint_dir=str(tmp_path),
        save_every=1,
        start_iteration=2,
        schedule_final_iteration=1,
        allow_schedule_overrun=True,
        checkpoint_metadata={"task": "vda16"},
    )

    for path in (
        tmp_path / "rvit_plus_rl_latest.pt",
        tmp_path / "rvit_paper_vda16_final.pt",
    ):
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        assert checkpoint["checkpoint_schema_version"] == 3
        assert checkpoint["optimizer_state_dict"]["state"]
        assert checkpoint["target_model_state_dict"]
        assert checkpoint["jepa_teacher_state_dict"]
        assert checkpoint["environment_state"]["theta"] == 65.0
        assert "replay_buffer" not in checkpoint
