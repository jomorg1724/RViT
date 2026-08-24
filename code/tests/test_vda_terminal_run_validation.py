from __future__ import annotations

import csv
from pathlib import Path

import pytest
import torch

from analysis import vda_terminal_run_validation as V


def _write_metrics(path: Path, *, gap_at: int | None = None) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("iter", "loss", "env/theta"))
        writer.writeheader()
        for iteration in range(V.TRAINING_ITERATIONS):
            written = iteration + 1 if gap_at is not None and iteration == gap_at else iteration
            writer.writerow({"iter": written, "loss": 0.25, "env/theta": 8.0})


def _producer_tree(root: Path) -> tuple[dict[str, str], Path, Path]:
    launcher = root / "endpoint_launcher.sh"
    config = root / "endpoint_config.json"
    launcher.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    config.write_text("{}\n", encoding="utf-8")
    producers: dict[str, str] = {}
    for identity in sorted(V.REQUIRED_PRODUCER_IDENTITIES):
        if identity == "experiment_launcher":
            path = launcher
        elif identity == "resolved_config":
            path = config
        else:
            path = root / identity
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"source:{identity}\n", encoding="utf-8")
        producers[identity] = V.sha256_file(path)
    return producers, launcher, config


def _payload(
    task: str,
    seed: int,
    producers: dict[str, str],
    *,
    visual_streams: int | None = None,
    memory_streams: int | None = None,
) -> dict:
    factorial = visual_streams is not None or memory_streams is not None
    if factorial and (visual_streams is None or memory_streams is None):
        raise ValueError("tests must provide both factorial levels")
    grid = 10 if factorial else 4
    image_size = 50 if factorial else 100
    model_state = {"weight": torch.tensor([1.0, 2.0])}
    target_state = {"weight": torch.tensor([1.0, 2.0])}
    if factorial:
        for state in (model_state, target_state):
            for prefix, streams in (
                ("front.projector", visual_streams),
                ("encoder.memory_projector", memory_streams),
            ):
                group_ids, matrix = V._expected_projector_buffers(streams)
                state[f"{prefix}.group_ids"] = torch.from_numpy(group_ids.copy())
                state[f"{prefix}.matrix"] = torch.from_numpy(matrix.copy())
    payload = {
        "checkpoint_schema_version": 3,
        "iter": V.FINAL_ITERATION,
        "task": task,
        "model_kwargs": {
            "feedback": "crossattn1",
            "d_mem": 128,
            "memory_decay": 1.0,
            "conv_frontend": True,
            "grid_rows": grid,
            "grid_cols": grid,
            "image_size": image_size,
            "seq_len": 7,
        },
        "training_args": {
            "task": task,
            "feedback": "crossattn1",
            "d_mem": 128,
            "memory_decay": 1.0,
            "patch_grid_rows": grid,
            "patch_grid_cols": grid,
            "curriculum": True,
            "seed": seed,
            "iters": 20_000,
            "schedule_final_iteration": 19_999,
            "episodes_per_iter": 8,
            "init_mode": "fresh",
        },
        "initialization_contract": {"mode": "fresh"},
        "replay_buffer_persisted": False,
        "resume_fidelity": "replay_excluded_trainer_state",
        "producer_sha256": producers,
        "model_state_dict": model_state,
        "optimizer_state_dict": {"state": {0: {"exp_avg": torch.tensor([0.1])}}},
        "target_model_state_dict": target_state,
        "jepa_teacher_state_dict": {"weight": torch.tensor([1.0, 2.0])},
        "environment_state": {"theta": 8.0},
        "rolling_correct": [0.9, 0.95],
        "rolling_return": [2.0, 2.5],
    }
    if factorial:
        payload["model_factory"] = {
            "kind": "stream_factorial_v1",
            "effective_visual_streams": visual_streams,
            "effective_memory_streams": memory_streams,
            "carrier_grid": [10, 10],
        }
        payload["model_kwargs"].update(
            {
                "memory_noise_std": 0.0,
                "cell": "xlstm",
                "two_lstm": False,
                "jepa_n_heads": 4,
                "jepa_proto_dim": 256,
                "frame_repeat": 1,
            }
        )
        payload["training_args"].update(
            {
                "T": 7,
                "frame_repeat": 1,
                "memory_noise_std": 0.0,
                "cell": "xlstm",
                "two_lstm": False,
                "conv_frontend": True,
                "jepa_coef": 0.5,
                "jepa_heads": 4,
                "jepa_proto_dim": 256,
                "start_iteration": 0,
                "effective_visual_streams": visual_streams,
                "effective_memory_streams": memory_streams,
            }
        )
    return payload


def _write_run(
    tmp_path: Path,
    task: str,
    seed: int,
    *,
    visual_streams: int | None = None,
    memory_streams: int | None = None,
) -> tuple[Path, Path, Path, Path]:
    producers, launcher, config = _producer_tree(tmp_path)
    run = tmp_path / "run"
    run.mkdir()
    payload = _payload(
        task,
        seed,
        producers,
        visual_streams=visual_streams,
        memory_streams=memory_streams,
    )
    torch.save(payload, run / f"rvit_paper_{task}_final.pt")
    torch.save(payload, run / "rvit_plus_rl_latest.pt")
    _write_metrics(run / "metrics.csv")
    log = tmp_path / "train.log"
    log.write_text(
        "[checkpoint] saved replay-excluded trainer state to final\n"
        "[paper] replay-excluded trainer checkpoint saved; iters logged=20000\n",
        encoding="utf-8",
    )
    return run, launcher, config, log


@pytest.mark.parametrize(("task", "seed"), (("vda16", 1), ("vda_fixed9", 0)))
def test_terminal_validator_accepts_exact_new_endpoint_contract(
    tmp_path: Path, task: str, seed: int
) -> None:
    run, launcher, config, log = _write_run(tmp_path, task, seed)
    result = V.validate_terminal_run(
        run,
        task=task,
        expected_seed=seed,
        project_root=tmp_path,
        launcher=launcher,
        config=config,
        log=log,
    )
    assert result["status"] == "validated_terminal_training_artifacts_only"
    assert result["metrics"]["rows"] == 20_000
    assert result["final_latest_semantically_equal"] is True
    assert result["scientific_behavior_evaluated"] is False
    assert len(result["producer_checks"]) == len(V.REQUIRED_PRODUCER_IDENTITIES)


def test_terminal_validator_rejects_latest_state_mismatch(tmp_path: Path) -> None:
    run, launcher, config, log = _write_run(tmp_path, "vda16", 1)
    changed = torch.load(run / "rvit_plus_rl_latest.pt", weights_only=False)
    changed["model_state_dict"]["weight"][0] = 99.0
    torch.save(changed, run / "rvit_plus_rl_latest.pt")
    with pytest.raises(ValueError, match="tensor mismatch"):
        V.validate_terminal_run(
            run,
            task="vda16",
            expected_seed=1,
            project_root=tmp_path,
            launcher=launcher,
            config=config,
            log=log,
        )


def test_metrics_validator_rejects_noncontiguous_iterations(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.csv"
    _write_metrics(metrics, gap_at=12_345)
    with pytest.raises(AssertionError):
        V.load_metrics(metrics)


@pytest.mark.parametrize(
    ("visual_streams", "memory_streams"),
    ((4, 4), (4, 100), (100, 4), (100, 100)),
)
def test_terminal_validator_accepts_exact_stream_factorial_contract(
    tmp_path: Path, visual_streams: int, memory_streams: int
) -> None:
    run, launcher, config, log = _write_run(
        tmp_path,
        "vda4",
        2,
        visual_streams=visual_streams,
        memory_streams=memory_streams,
    )
    result = V.validate_terminal_run(
        run,
        task="vda4",
        expected_seed=2,
        expected_visual_streams=visual_streams,
        expected_memory_streams=memory_streams,
        project_root=tmp_path,
        launcher=launcher,
        config=config,
        log=log,
    )

    assert result["status"] == "validated_terminal_training_artifacts_only"
    assert result["spec"]["grid_rows"] == result["spec"]["grid_cols"] == 10
    assert result["spec"]["image_size"] == 50
    assert result["model_factory"] == {
        "kind": "stream_factorial_v1",
        "effective_visual_streams": visual_streams,
        "effective_memory_streams": memory_streams,
        "carrier_grid": [10, 10],
    }


def test_terminal_validator_requires_explicit_stream_factorial_levels(tmp_path: Path) -> None:
    run, launcher, config, log = _write_run(
        tmp_path, "vda4", 2, visual_streams=4, memory_streams=100
    )
    with pytest.raises(ValueError, match="requires explicit"):
        V.validate_terminal_run(
            run,
            task="vda4",
            expected_seed=2,
            project_root=tmp_path,
            launcher=launcher,
            config=config,
            log=log,
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda payload: payload["model_factory"].update(effective_visual_streams=100),
            "effective_visual_streams",
        ),
        (
            lambda payload: payload["model_state_dict"].pop(
                "front.projector.group_ids"
            ),
            "projector buffers",
        ),
        (
            lambda payload: payload["target_model_state_dict"][
                "encoder.memory_projector.matrix"
            ].zero_(),
            "does not match the registered projector",
        ),
    ],
)
def test_terminal_validator_rejects_factorial_metadata_or_projector_mismatch(
    tmp_path: Path, mutation, message
) -> None:
    run, launcher, config, log = _write_run(
        tmp_path, "vda4", 2, visual_streams=4, memory_streams=100
    )
    for name in ("rvit_paper_vda4_final.pt", "rvit_plus_rl_latest.pt"):
        path = run / name
        payload = torch.load(path, map_location="cpu", weights_only=False)
        mutation(payload)
        torch.save(payload, path)
    with pytest.raises(ValueError, match=message):
        V.validate_terminal_run(
            run,
            task="vda4",
            expected_seed=2,
            expected_visual_streams=4,
            expected_memory_streams=100,
            project_root=tmp_path,
            launcher=launcher,
            config=config,
            log=log,
        )


def test_terminal_validator_rejects_stream_levels_for_nonfactorial_task(tmp_path: Path) -> None:
    run, launcher, config, log = _write_run(tmp_path, "vda16", 1)
    with pytest.raises(ValueError, match="only for task 'vda4'"):
        V.validate_terminal_run(
            run,
            task="vda16",
            expected_seed=1,
            expected_visual_streams=4,
            expected_memory_streams=100,
            project_root=tmp_path,
            launcher=launcher,
            config=config,
            log=log,
        )
