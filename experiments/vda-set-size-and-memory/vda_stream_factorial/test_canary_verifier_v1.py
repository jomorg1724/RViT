from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
import torch

from analysis.vda_terminal_run_validation import _expected_projector_buffers
from experiments.vda_stream_factorial import verify_canary_block_v1 as C


ROOT = Path(__file__).resolve().parents[2]


def _producer_hashes() -> dict[str, str]:
    values = {}
    for identity in sorted(C.REQUIRED_PRODUCER_IDENTITIES):
        if identity == "resolved_config":
            path = ROOT / C.CONFIG_RELATIVE
        elif identity == "experiment_launcher":
            path = ROOT / C.LAUNCHER_RELATIVE
        else:
            path = ROOT / identity
        values[identity] = C.sha256_file(path)
    return values


def _state(visual: int, memory: int, marker: float) -> dict[str, torch.Tensor]:
    state = {"weight": torch.tensor([marker, marker + 1.0])}
    for prefix, streams in (
        ("front.projector", visual),
        ("encoder.memory_projector", memory),
    ):
        group_ids, matrix = _expected_projector_buffers(streams)
        state[f"{prefix}.group_ids"] = torch.from_numpy(group_ids.copy())
        state[f"{prefix}.matrix"] = torch.from_numpy(matrix.copy())
    return state


def _payload(
    visual: int, memory: int, producer: dict[str, str], marker: float
) -> dict:
    factory = C._factory_for_cell(visual, memory)
    model_kwargs = {
        "feedback": "crossattn1",
        "cell": "xlstm",
        "two_lstm": False,
        "d_mem": 128,
        "memory_decay": 1.0,
        "memory_noise_std": 0.0,
        "conv_frontend": True,
        "grid_rows": 10,
        "grid_cols": 10,
        "image_size": 50,
        "seq_len": 7,
    }
    return {
        "checkpoint_schema_version": 3,
        "iter": C.CANARY_FINAL_ITERATION,
        "task": "vda4",
        "model_factory": factory,
        "model_kwargs": model_kwargs,
        "training_args": {
            "task": "vda4",
            "feedback": "crossattn1",
            "cell": "xlstm",
            "two_lstm": False,
            "d_mem": 128,
            "memory_decay": 1.0,
            "memory_noise_std": 0.0,
            "patch_grid_rows": 10,
            "patch_grid_cols": 10,
            "curriculum": True,
            "seed": 0,
            "start_iteration": 0,
            "iters": 50,
            "schedule_final_iteration": 19_999,
            "episodes_per_iter": 8,
            "init_mode": "fresh",
        },
        "initialization_contract": {"mode": "fresh"},
        "replay_buffer_persisted": False,
        "resume_fidelity": "replay_excluded_trainer_state",
        "producer_sha256": producer,
        "resume_contract": {
            "task": "vda4",
            "model_kwargs": model_kwargs,
            "episodes_per_iter": 8,
            "schedule_final_iteration": 19_999,
            "model_factory": factory,
            "producer_sha256": producer,
        },
        "model_state_dict": _state(visual, memory, marker),
        "optimizer_state_dict": {
            "state": {0: {"exp_avg": torch.tensor([0.1, 0.2])}}
        },
        "target_model_state_dict": _state(visual, memory, marker),
        "jepa_teacher_state_dict": {"weight": torch.tensor([1.0, 2.0])},
        "environment_state": {"theta": 65.0},
        "rolling_correct": [0.25, 0.5],
        "rolling_return": [1.0, 1.5],
    }


def _write_metrics(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("iter", "loss", "env/theta"))
        writer.writeheader()
        for iteration in range(50):
            writer.writerow({"iter": iteration, "loss": 0.25, "env/theta": 65.0})


def _common_hashes() -> tuple[str, str, dict[str, str]]:
    design = json.loads((ROOT / C.DESIGN_RELATIVE).read_text(encoding="utf-8"))
    trace = design["environment_rng_trace"]["expected_sha256_by_seed"]["0"]
    return "a" * 64, trace, _producer_hashes()


def _launch_contract(
    visual: int,
    memory: int,
    producer: dict[str, str],
    init_hash: str,
    trace_hash: str,
) -> dict:
    paired = {cell_id: init_hash for cell_id in C.CELL_IDS.values()}
    return {
        "schema_version": 1,
        "status": "preflight_passed",
        "evidence_class": "engineering_only_not_scientific_evidence",
        "request": {
            "visual_streams": visual,
            "memory_streams": memory,
            "seed": 0,
            "run_kind": "canary",
            "iterations": 50,
            "terminal_iteration": 49,
        },
        "sha256": {
            "config": C.sha256_file(ROOT / C.CONFIG_RELATIVE),
            "design": C.sha256_file(ROOT / C.DESIGN_RELATIVE),
            "preflight": C.sha256_file(ROOT / C.PREFLIGHT_RELATIVE),
            "launcher": C.sha256_file(ROOT / C.LAUNCHER_RELATIVE),
            "trainable_initialization": init_hash,
            "environment_rng_trace": trace_hash,
        },
        "paired_trainable_initialization_sha256_by_cell": paired,
        "model_factory": C._factory_for_cell(visual, memory),
        "producer_sha256": producer,
    }


def _write_block(tmp_path: Path) -> tuple[list[Path], list[Path]]:
    init_hash, trace_hash, producer = _common_hashes()
    runs, logs = [], []
    for index, (visual, memory) in enumerate(sorted(C.EXPECTED_CELLS)):
        run = tmp_path / C.CELL_IDS[(visual, memory)]
        run.mkdir()
        payload = _payload(visual, memory, producer, float(index + 1))
        torch.save(payload, run / "rvit_paper_vda4_final.pt")
        torch.save(payload, run / "rvit_plus_rl_latest.pt")
        _write_metrics(run / "metrics.csv")
        (run / "launch_contract.json").write_text(
            json.dumps(
                _launch_contract(
                    visual, memory, producer, init_hash, trace_hash
                ),
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        log = run / "train.log"
        log.write_text(
            "[checkpoint] saved replay-excluded trainer state to "
            f"{run / 'rvit_paper_vda4_final.pt'}\n"
            "[paper] replay-excluded trainer checkpoint saved; iters logged=50\n",
            encoding="utf-8",
        )
        runs.append(run)
        logs.append(log)
    return runs, logs


def _mutate_both_checkpoints(run: Path, mutation) -> None:
    for name in ("rvit_paper_vda4_final.pt", "rvit_plus_rl_latest.pt"):
        path = run / name
        payload = torch.load(path, map_location="cpu", weights_only=False)
        mutation(payload)
        torch.save(payload, path)


def test_verifier_accepts_exact_four_cell_engineering_block(tmp_path: Path) -> None:
    runs, logs = _write_block(tmp_path)
    result = C.verify_canary_block(runs, logs, project_root=ROOT)

    assert result["status"] == "complete_verified_engineering_canary_block"
    assert result["scientific_evidence"] is False
    assert result["scientific_behavior_evaluated"] is False
    assert set(result["cells"]) == set(C.CELL_IDS.values())
    assert {cell["metrics"]["rows"] for cell in result["cells"].values()} == {50}
    assert all(
        cell["final_latest_semantically_equal"]
        for cell in result["cells"].values()
    )
    assert result["common_trainable_initialization_sha256"] == "a" * 64


def test_verifier_rejects_incomplete_block(tmp_path: Path) -> None:
    runs, logs = _write_block(tmp_path)
    with pytest.raises(ValueError, match="exactly four"):
        C.verify_canary_block(runs[:3], logs[:3], project_root=ROOT)


@pytest.mark.parametrize("kind", ("gap", "nonfinite"))
def test_verifier_rejects_invalid_metrics(tmp_path: Path, kind: str) -> None:
    runs, logs = _write_block(tmp_path)
    rows = list(csv.DictReader((runs[0] / "metrics.csv").open(encoding="utf-8")))
    if kind == "gap":
        rows[12]["iter"] = "13"
    else:
        rows[12]["loss"] = "nan"
    with (runs[0] / "metrics.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    match = "contiguous" if kind == "gap" else "non-finite"
    with pytest.raises(ValueError, match=match):
        C.verify_canary_block(runs, logs, project_root=ROOT)


def test_verifier_rejects_final_latest_mismatch(tmp_path: Path) -> None:
    runs, logs = _write_block(tmp_path)
    latest = torch.load(
        runs[0] / "rvit_plus_rl_latest.pt", map_location="cpu", weights_only=False
    )
    latest["model_state_dict"]["weight"][0] = 99.0
    torch.save(latest, runs[0] / "rvit_plus_rl_latest.pt")
    with pytest.raises(ValueError, match="tensor mismatch"):
        C.verify_canary_block(runs, logs, project_root=ROOT)


@pytest.mark.parametrize("kind", ("factory", "projector", "nonfinite"))
def test_verifier_rejects_checkpoint_contract_corruption(
    tmp_path: Path, kind: str
) -> None:
    runs, logs = _write_block(tmp_path)
    if kind == "factory":
        mutation = lambda payload: payload["model_factory"].update(
            effective_visual_streams=100
        )
        match = "model_factory"
    elif kind == "projector":
        mutation = lambda payload: payload["model_state_dict"].pop(
            "front.projector.matrix"
        )
        match = "projector buffers"
    else:
        mutation = lambda payload: payload["optimizer_state_dict"]["state"][0][
            "exp_avg"
        ].fill_(float("nan"))
        match = "non-finite"
    _mutate_both_checkpoints(runs[0], mutation)
    with pytest.raises(ValueError, match=match):
        C.verify_canary_block(runs, logs, project_root=ROOT)


@pytest.mark.parametrize("kind", ("initialization", "rng"))
def test_verifier_rejects_unpaired_launch_contracts(tmp_path: Path, kind: str) -> None:
    runs, logs = _write_block(tmp_path)
    path = runs[0] / "launch_contract.json"
    contract = json.loads(path.read_text(encoding="utf-8"))
    if kind == "initialization":
        contract["sha256"]["trainable_initialization"] = "b" * 64
        contract["paired_trainable_initialization_sha256_by_cell"] = {
            key: "b" * 64
            for key in contract["paired_trainable_initialization_sha256_by_cell"]
        }
        match = "trainable-initialization"
    else:
        contract["sha256"]["environment_rng_trace"] = "b" * 64
        match = "environment RNG trace"
    path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        C.verify_canary_block(runs, logs, project_root=ROOT)


def test_verifier_rejects_dirty_terminal_log(tmp_path: Path) -> None:
    runs, logs = _write_block(tmp_path)
    logs[0].write_text("Traceback\n", encoding="utf-8")
    with pytest.raises(ValueError, match="failure marker"):
        C.verify_canary_block(runs, logs, project_root=ROOT)


def test_verifier_rejects_provenance_hash_mismatch(tmp_path: Path) -> None:
    runs, logs = _write_block(tmp_path)
    path = runs[0] / "launch_contract.json"
    contract = json.loads(path.read_text(encoding="utf-8"))
    contract["sha256"]["preflight"] = "0" * 64
    path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="preflight SHA-256 mismatch"):
        C.verify_canary_block(runs, logs, project_root=ROOT)
