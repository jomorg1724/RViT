from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
import torch

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _arg(command: tuple[str, ...], flag: str) -> str:
    return command[command.index(flag) + 1]


def test_matrix_forks_four_fixed_condition_agents_from_one_neutral_parent(tmp_path):
    from experiments.luo2015_episodic.run_matrix import build_cells

    cells = build_cells(
        project_root=_ROOT,
        run_root=tmp_path / "run",
        python_executable=Path(sys.executable),
        seeds=(7,),
        parent_iterations=100,
        child_iterations=200,
        device="cpu",
        theta=18.0,
    )

    assert len(cells) == 5
    parent, *children = cells
    assert parent.role == "neutral_parent"
    assert _arg(parent.command, "--gamma") == "1.0"
    assert "--curriculum" in parent.command
    assert _arg(parent.command, "--r-hit") == "1.0"
    assert _arg(parent.command, "--r-cr") == "1.0"
    assert _arg(parent.command, "--curr-floor") == "18.0"

    assert {(cell.task, cell.condition_loc) for cell in children} == {
        ("luo2015_sensitivity", 0),
        ("luo2015_sensitivity", 3),
        ("luo2015_criterion", 0),
        ("luo2015_criterion", 3),
    }
    parent_checkpoint = parent.output_dir / "rvit_paper_luo2015_criterion_final.pt"
    for cell in children:
        assert cell.parent_checkpoint == parent_checkpoint
        assert "--curriculum" not in cell.command
        assert _arg(cell.command, "--init-mode") == "warm_start"
        assert Path(_arg(cell.command, "--checkpoint-path")) == parent_checkpoint
        assert _arg(cell.command, "--theta-start") == "18.0"
        assert _arg(cell.command, "--seed") == "7"
        assert _arg(cell.command, "--cell") == "xlstm"
        assert _arg(cell.command, "--feedback") == "affine_ew"
        assert "--conv-frontend" in cell.command
        assert _arg(cell.command, "--jepa-coef") == "0.5"
        assert _arg(cell.command, "--d-mem") == "128"
        assert _arg(cell.command, "--gamma") == "1.0"

    sensitivity_scales = {
        float(_arg(cell.command, "--reward-scale"))
        for cell in children
        if cell.task == "luo2015_sensitivity"
    }
    criterion_scales = {
        float(_arg(cell.command, "--reward-scale"))
        for cell in children
        if cell.task == "luo2015_criterion"
    }
    assert sensitivity_scales == {1.0 / 3.0}
    assert criterion_scales == {1.0 / 0.95}


@pytest.mark.parametrize("feedback", ["affine_ew", "crossattn1"])
def test_matrix_configures_decay_architecture_and_small_stimulus_noise(tmp_path, feedback):
    from experiments.luo2015_episodic.run_matrix import build_cells

    cells = build_cells(
        project_root=_ROOT,
        run_root=tmp_path / feedback,
        python_executable=Path(sys.executable),
        seeds=(3,),
        parent_iterations=10,
        child_iterations=20,
        device="cpu",
        theta=18.0,
        feedback=feedback,
        memory_decay=0.5,
        d_mem=16,
        noise=0.5,
    )

    assert len(cells) == 5
    for cell in cells:
        assert _arg(cell.command, "--feedback") == feedback
        assert _arg(cell.command, "--memory-decay") == "0.5"
        assert _arg(cell.command, "--d-mem") == "16"
        assert _arg(cell.command, "--noise") == "0.5"


def test_matrix_configures_dense_grid_independent_memory_noise_without_changing_task(tmp_path):
    from experiments.luo2015_episodic.run_matrix import build_cells

    cells = build_cells(
        project_root=_ROOT,
        run_root=tmp_path / "dense_memory_noise",
        python_executable=Path(sys.executable),
        seeds=(11,),
        parent_iterations=10,
        child_iterations=20,
        device="cpu",
        theta=18.0,
        feedback="crossattn1",
        memory_decay=1.0,
        d_mem=32,
        noise=5.0,
        patch_grid_rows=20,
        patch_grid_cols=20,
        memory_noise_std=0.01,
    )

    assert len(cells) == 5
    for cell in cells:
        assert _arg(cell.command, "--patch-grid-rows") == "20"
        assert _arg(cell.command, "--patch-grid-cols") == "20"
        assert _arg(cell.command, "--d-mem") == "32"
        assert _arg(cell.command, "--memory-decay") == "1.0"
        assert _arg(cell.command, "--memory-noise-std") == "0.01"
        assert _arg(cell.command, "--noise") == "5.0"
        assert _arg(cell.command, "--T") == "7"
        assert _arg(cell.command, "--jepa-coef") == "0.5"
        assert "--luo-spatial-grid-size" not in cell.command


def test_matrix_preserves_virtualenv_python_symlink(tmp_path):
    from experiments.luo2015_episodic.run_matrix import build_cells

    base_python = tmp_path / "base-python"
    base_python.write_text("#!/bin/sh\n")
    base_python.chmod(0o755)
    venv_python = tmp_path / "venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    try:
        venv_python.symlink_to(base_python)
    except OSError as exc:
        if sys.platform == "win32" and getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows symlink creation requires Developer Mode or elevation")
        raise

    cells = build_cells(
        project_root=_ROOT,
        run_root=tmp_path / "run",
        python_executable=venv_python,
        seeds=(0,),
        parent_iterations=1,
        child_iterations=1,
        device="cpu",
        theta=18.0,
    )

    assert all(cell.command[0] == str(venv_python.absolute()) for cell in cells)


def test_grid20_dmem32_memory_noise_experiment_is_isolated_and_fully_specified():
    experiment_dir = (
        _ROOT
        / "experiments"
        / "luo2015_episodic"
        / "grid20x20_dmem32_memnoise001_nodecay"
    )
    launcher = experiment_dir / "launch_20k.sh"
    readme = experiment_dir / "README.md"

    assert launcher.is_file()
    assert readme.is_file()
    content = launcher.read_text(encoding="utf-8")
    for expected in (
        "experiments/luo2015_episodic/run_matrix.py",
        "--patch-grid-rows 20",
        "--patch-grid-cols 20",
        "--feedback crossattn1",
        "--memory-decay 1.0",
        "--memory-noise-std 0.01",
        "--d-mem 32",
        "--noise 5.0",
        "--parent-iters 20000",
        "--child-iters 20000",
        "--theta 18.0",
        "--seeds 0 1 2",
        "--execute",
    ):
        assert expected in content


def test_grid20_dmem32_memory_noise008_matched_evaluation_experiment_is_specified():
    experiment_dir = (
        _ROOT
        / "experiments"
        / "luo2015_episodic"
        / "grid20x20_dmem32_memnoise008_nodecay_matched_eval"
    )
    launcher = experiment_dir / "launch_local_20k.sh"
    readme = experiment_dir / "README.md"

    assert launcher.is_file()
    assert readme.is_file()
    content = launcher.read_text(encoding="utf-8")
    for expected in (
        "experiments/luo2015_episodic/run_matrix.py",
        "--patch-grid-rows 20",
        "--patch-grid-cols 20",
        "--feedback crossattn1",
        "--memory-decay 1.0",
        "--memory-noise-std 0.08",
        "--d-mem 32",
        "--noise 5.0",
        "--parent-iters 20000",
        "--child-iters 20000",
        "--theta 18.0",
        "--seeds 0 1 2",
        "--device cuda",
        "--execute",
    ):
        assert expected in content

    documentation = readme.read_text(encoding="utf-8")
    for expected in (
        "0.08",
        "same task",
        "independent Uniform[0°, 180°) initial-orientation distribution",
        "mnemonic noise enabled",
        "sampled policy actions",
    ):
        assert expected in documentation


def test_dry_run_prints_complete_matrix_without_creating_run_directory(tmp_path, capsys):
    from experiments.luo2015_episodic.run_matrix import main

    run_root = tmp_path / "would_run_here"
    status = main([
        "--run-root", str(run_root),
        "--seeds", "2",
        "--parent-iters", "1",
        "--child-iters", "1",
        "--device", "cpu",
    ])

    captured = capsys.readouterr().out
    assert status == 0
    assert not run_root.exists()
    assert "paired episodic fixed-condition optimization" in captured
    assert captured.count("[dry-run]") == 5
    assert "neutral_parent" in captured
    assert "sensitivity_loc0" in captured
    assert "sensitivity_loc3" in captured
    assert "criterion_loc0" in captured
    assert "criterion_loc3" in captured


def test_execute_preflight_fails_before_creating_a_manifest_without_torch(
    tmp_path, monkeypatch,
):
    import experiments.luo2015_episodic.run_matrix as run_matrix

    run_root = tmp_path / "missing_torch"

    def missing_torch():
        raise RuntimeError("training requires Torch")

    monkeypatch.setattr(run_matrix, "_validate_torch_runtime", missing_torch)
    with pytest.raises(RuntimeError, match="requires Torch"):
        run_matrix.main([
            "--run-root", str(run_root),
            "--seeds", "0",
            "--parent-iters", "1",
            "--child-iters", "1",
            "--device", "cpu",
            "--execute",
        ])

    assert not run_root.exists()


@pytest.mark.parametrize("extra", [
    ["--theta", "nan"],
    ["--parent-min-accuracy", "nan"],
    ["--parent-min-valid-fraction", "1.1"],
    ["--parent-gate-trials", "0"],
])
def test_launcher_rejects_invalid_gate_configuration_before_training(tmp_path, extra):
    from experiments.luo2015_episodic.run_matrix import main

    with pytest.raises(ValueError):
        main(["--run-root", str(tmp_path / "invalid"), *extra])


def test_execute_writes_restart_manifest_and_completes_parent_before_children(tmp_path):
    from experiments.luo2015_episodic.run_matrix import main

    run_root = tmp_path / "executed"
    calls: list[tuple[str, ...]] = []

    def fake_runner(command, *, cwd, check):
        from envs import make_env
        from train_rl import _producer_hashes

        command = tuple(command)
        calls.append(command)
        output_dir = Path(_arg(command, "--checkpoint-dir"))
        output_dir.mkdir(parents=True, exist_ok=True)
        task = _arg(command, "--task")
        parent_hash = None
        initialization_contract = {"mode": "fresh"}
        if _arg(command, "--init-mode") == "warm_start":
            parent_path = Path(_arg(command, "--checkpoint-path"))
            assert parent_path.is_file()
            parent_hash = hashlib.sha256(parent_path.read_bytes()).hexdigest()
            assert _arg(command, "--expected-parent-sha256") == parent_hash
            initialization_contract = {
                "mode": "warm_start", "checkpoint_sha256": parent_hash,
                "strict": True,
            }
        reward_scale = float(_arg(command, "--reward-scale"))
        theta = float(_arg(command, "--theta-start"))
        high_loc = int(_arg(command, "--high-loc"))
        torch.save(
            {
                "iter": int(_arg(command, "--iters")) - 1,
                "task": task,
                "training_args": {
                    "seed": int(_arg(command, "--seed")),
                    "high_loc": high_loc,
                    "reward_scale": reward_scale,
                    "theta_start": theta,
                    "curriculum": "--curriculum" in command,
                    "T": 7,
                    "curr_floor": float(_arg(command, "--curr-floor")) if "--curr-floor" in command else 18.0,
                    "r_hit": float(_arg(command, "--r-hit")) if "--r-hit" in command else None,
                    "r_cr": float(_arg(command, "--r-cr")) if "--r-cr" in command else None,
                    "expected_parent_sha256": parent_hash,
                },
                "initialization_contract": initialization_contract,
                "ppo_config": {"gamma": float(_arg(command, "--gamma"))},
                "producer_hashes": _producer_hashes(
                    experiment_launcher=_arg(command, "--experiment-launcher")
                ),
                "environment_state": make_env(
                    task, T=7, min_change_time=5, max_change_time=5,
                    noise_multiplier=5.0, reward_scale=reward_scale,
                    curriculum="--curriculum" in command, theta=theta,
                    high_loc=high_loc,
                    theta_floor=float(_arg(command, "--curr-floor")) if "--curr-floor" in command else 5.0,
                    r_hit=float(_arg(command, "--r-hit")) if "--r-hit" in command else None,
                    r_cr=float(_arg(command, "--r-cr")) if "--r-cr" in command else None,
                ).training_state_dict(),
            },
            output_dir / f"rvit_paper_{task}_final.pt",
        )

    status = main([
        "--run-root", str(run_root),
        "--seeds", "4",
        "--parent-iters", "1",
        "--child-iters", "1",
        "--device", "cpu",
        "--canary",
        "--execute",
    ], runner=fake_runner)

    assert status == 0
    assert len(calls) == 5
    manifest = json.loads((run_root / "experiment_manifest.json").read_text())
    assert manifest["design"] == "paired_episodic_fixed_condition_optimization"
    assert manifest["claim_scope"] == "condition_specific_policy_optima_not_online_block_adaptation"
    assert {cell["status"] for cell in manifest["cells"]} == {"complete"}
    parent = manifest["cells"][0]
    assert parent["role"] == "neutral_parent"
    assert len(parent["final_checkpoint_sha256"]) == 64
    for child in manifest["cells"][1:]:
        assert child["parent_checkpoint_sha256"] == parent["final_checkpoint_sha256"]


def test_restart_rejects_stale_children_after_parent_checkpoint_replacement(tmp_path):
    from experiments.luo2015_episodic.run_matrix import main

    run_root = tmp_path / "immutable_lineage"

    def fake_runner(command, *, cwd, check):
        from envs import make_env
        from train_rl import _producer_hashes

        command = tuple(command)
        output_dir = Path(_arg(command, "--checkpoint-dir"))
        output_dir.mkdir(parents=True, exist_ok=True)
        task = _arg(command, "--task")
        parent_hash = None
        if _arg(command, "--init-mode") == "warm_start":
            parent_hash = hashlib.sha256(
                Path(_arg(command, "--checkpoint-path")).read_bytes()
            ).hexdigest()
            assert _arg(command, "--expected-parent-sha256") == parent_hash
        reward_scale = float(_arg(command, "--reward-scale"))
        theta = float(_arg(command, "--theta-start"))
        high_loc = int(_arg(command, "--high-loc"))
        torch.save({
            "iter": int(_arg(command, "--iters")) - 1,
            "task": task,
            "training_args": {
                "seed": int(_arg(command, "--seed")),
                "high_loc": high_loc,
                "reward_scale": reward_scale,
                "theta_start": theta,
                "curriculum": "--curriculum" in command,
                "T": 7,
                "curr_floor": float(_arg(command, "--curr-floor")) if "--curr-floor" in command else 18.0,
                "r_hit": float(_arg(command, "--r-hit")) if "--r-hit" in command else None,
                "r_cr": float(_arg(command, "--r-cr")) if "--r-cr" in command else None,
                "expected_parent_sha256": parent_hash,
            },
            "initialization_contract": (
                {"mode": "warm_start", "checkpoint_sha256": parent_hash, "strict": True}
                if parent_hash else {"mode": "fresh"}
            ),
            "ppo_config": {"gamma": float(_arg(command, "--gamma"))},
            "producer_hashes": _producer_hashes(
                experiment_launcher=_arg(command, "--experiment-launcher")
            ),
            "environment_state": make_env(
                task, T=7, min_change_time=5, max_change_time=5,
                noise_multiplier=5.0, reward_scale=reward_scale,
                curriculum="--curriculum" in command, theta=theta,
                high_loc=high_loc,
                theta_floor=float(_arg(command, "--curr-floor")) if "--curr-floor" in command else 5.0,
                r_hit=float(_arg(command, "--r-hit")) if "--r-hit" in command else None,
                r_cr=float(_arg(command, "--r-cr")) if "--r-cr" in command else None,
            ).training_state_dict(),
        }, output_dir / f"rvit_paper_{task}_final.pt")

    argv = [
        "--run-root", str(run_root), "--seeds", "4",
        "--parent-iters", "1", "--child-iters", "1",
        "--device", "cpu", "--canary", "--execute",
    ]
    assert main(argv, runner=fake_runner) == 0
    manifest_path = run_root / "experiment_manifest.json"
    original = json.loads(manifest_path.read_text())
    original_child_lineage = original["cells"][1]["parent_checkpoint_sha256"]

    parent_path = Path(original["cells"][0]["final_checkpoint"])
    replacement = torch.load(parent_path, map_location="cpu", weights_only=False)
    replacement["replacement_nonce"] = "different but protocol-valid parent"
    torch.save(replacement, parent_path)
    with pytest.raises(RuntimeError, match="parent checkpoint lineage"):
        main(argv, runner=fake_runner)

    unchanged = json.loads(manifest_path.read_text())
    assert unchanged["cells"][1]["parent_checkpoint_sha256"] == original_child_lineage


def test_warm_start_parent_loading_is_hash_bound_and_strict(tmp_path):
    from train_rl import load_warm_start_parent

    source = torch.nn.Linear(3, 2)
    parent_path = tmp_path / "parent.pt"
    torch.save({
        "iter": 17,
        "task": "luo2015_criterion",
        "model_state_dict": source.state_dict(),
    }, parent_path)
    parent_hash = hashlib.sha256(parent_path.read_bytes()).hexdigest()
    child = torch.nn.Linear(3, 2)

    info, contract = load_warm_start_parent(
        child, str(parent_path), expected_sha256=parent_hash, device=torch.device("cpu")
    )
    assert info["strict"] is True
    assert contract == {
        "mode": "warm_start",
        "checkpoint_path": str(parent_path.resolve()),
        "checkpoint_sha256": parent_hash,
        "checkpoint_iteration": 17,
        "checkpoint_task": "luo2015_criterion",
        "strict": True,
    }
    assert all(torch.equal(left, right) for left, right in zip(child.parameters(), source.parameters()))

    with pytest.raises(ValueError, match="hash mismatch"):
        load_warm_start_parent(
            child, str(parent_path), expected_sha256="0" * 64, device=torch.device("cpu")
        )

    torch.save({"model_state_dict": {"weight": source.weight}}, parent_path)
    incomplete_hash = hashlib.sha256(parent_path.read_bytes()).hexdigest()
    with pytest.raises(RuntimeError):
        load_warm_start_parent(
            child, str(parent_path), expected_sha256=incomplete_hash, device=torch.device("cpu")
        )


def test_resume_preserves_original_warm_start_parent_contract():
    from train_rl import resume_initialization_contract

    parent_hash = "a" * 64
    original = {
        "mode": "warm_start", "checkpoint_sha256": parent_hash,
        "checkpoint_iteration": 19, "strict": True,
    }
    resumed = resume_initialization_contract(
        {"initialization_contract": original},
        expected_parent_sha256=parent_hash,
        resume_checkpoint_path="/tmp/child_latest.pt",
        resume_checkpoint_sha256="b" * 64,
    )
    assert resumed == original
    assert resumed is not original

    with pytest.raises(ValueError, match="initialization parent hash mismatch"):
        resume_initialization_contract(
            {"initialization_contract": original},
            expected_parent_sha256="c" * 64,
            resume_checkpoint_path="/tmp/child_latest.pt",
            resume_checkpoint_sha256="b" * 64,
        )


@pytest.mark.parametrize("mutation, match", [
    (("ppo_config", "gamma", 0.95), "gamma"),
    (("training_args", "reward_scale", 1.0), "reward scale"),
    (("initialization_contract", "strict", False), "strict warm-start"),
    (("training_args", "curriculum", True), "curriculum"),
])
def test_child_checkpoint_contract_rejects_protocol_drift(tmp_path, mutation, match):
    from envs import make_env
    from train_rl import _producer_hashes
    from experiments.luo2015_episodic.run_matrix import (
        build_cells,
        validate_child_checkpoint_contract,
    )

    cell = build_cells(
        project_root=_ROOT, run_root=tmp_path / "run",
        python_executable=Path(sys.executable), seeds=(8,),
        parent_iterations=2, child_iterations=3, device="cpu", theta=18.0,
    )[1]
    parent = tmp_path / "parent.pt"
    parent.write_bytes(b"immutable-parent")
    parent_hash = hashlib.sha256(parent.read_bytes()).hexdigest()
    reward_scale = float(_arg(cell.command, "--reward-scale"))
    expected_env = make_env(
        cell.task, T=7, min_change_time=5, max_change_time=5,
        noise_multiplier=5.0, reward_scale=reward_scale,
        curriculum=False, theta=18.0, high_loc=cell.condition_loc,
    )
    blob = {
        "iter": 2,
        "task": cell.task,
        "initialization_contract": {
            "mode": "warm_start", "checkpoint_sha256": parent_hash, "strict": True,
        },
        "ppo_config": {"gamma": 1.0},
        "producer_hashes": _producer_hashes(
            experiment_launcher=_arg(cell.command, "--experiment-launcher")
        ),
        "training_args": {
            "seed": cell.seed, "high_loc": cell.condition_loc,
            "reward_scale": reward_scale, "theta_start": 18.0,
            "curriculum": False, "T": 7,
            "expected_parent_sha256": parent_hash,
        },
        "environment_state": expected_env.training_state_dict(),
    }
    checkpoint = tmp_path / "child.pt"
    torch.save(blob, checkpoint)
    validate_child_checkpoint_contract(checkpoint, cell, parent_hash)

    section, field, value = mutation
    blob[section][field] = value
    torch.save(blob, checkpoint)
    with pytest.raises(RuntimeError, match=match):
        validate_child_checkpoint_contract(checkpoint, cell, parent_hash)


def test_neutral_parent_checkpoint_contract_rejects_biased_objective(tmp_path):
    from envs import make_env
    from train_rl import _producer_hashes
    from experiments.luo2015_episodic.run_matrix import (
        build_cells,
        validate_parent_checkpoint_contract,
    )

    parent = build_cells(
        project_root=_ROOT, run_root=tmp_path / "run",
        python_executable=Path(sys.executable), seeds=(8,),
        parent_iterations=2, child_iterations=3, device="cpu", theta=18.0,
    )[0]
    expected_env = make_env(
        parent.task, T=7, min_change_time=5, max_change_time=5,
        noise_multiplier=5.0, reward_scale=1.0, curriculum=True,
        theta=65.0, theta_floor=18.0, high_loc=0, r_hit=1.0, r_cr=1.0,
    )
    blob = {
        "iter": 1, "task": parent.task,
        "initialization_contract": {"mode": "fresh"},
        "ppo_config": {"gamma": 1.0},
        "producer_hashes": _producer_hashes(
            experiment_launcher=_arg(parent.command, "--experiment-launcher")
        ),
        "training_args": {
            "seed": 8, "high_loc": 0, "reward_scale": 1.0,
            "theta_start": 65.0, "curr_floor": 18.0,
            "curriculum": True, "T": 7, "r_hit": 1.0, "r_cr": 1.0,
        },
        "environment_state": expected_env.training_state_dict(),
    }
    checkpoint = tmp_path / "neutral.pt"
    torch.save(blob, checkpoint)
    validate_parent_checkpoint_contract(checkpoint, parent)
    from experiments.luo2015_episodic.analyze_matrix import _validate_parent_checkpoint_record
    _validate_parent_checkpoint_record({
        "role": parent.role, "seed": parent.seed, "task": parent.task,
        "condition_loc": None, "output_dir": str(parent.output_dir),
        "command": list(parent.command), "final_checkpoint": str(checkpoint),
    })

    blob["training_args"]["r_hit"] = 2.0
    torch.save(blob, checkpoint)
    with pytest.raises(RuntimeError, match="neutral reward objective"):
        validate_parent_checkpoint_contract(checkpoint, parent)


def test_counterphased_difference_in_differences_recovers_paper_predictions():
    from experiments.luo2015_episodic.analyze_matrix import counterphased_effects

    records = [
        {"seed": 9, "session": "sensitivity", "condition_loc": 0,
         "metrics": {"0": {"dprime": 2.0, "criterion": 0.1},
                     "3": {"dprime": 1.0, "criterion": 0.1}}},
        {"seed": 9, "session": "sensitivity", "condition_loc": 3,
         "metrics": {"0": {"dprime": 1.0, "criterion": 0.1},
                     "3": {"dprime": 2.0, "criterion": 0.1}}},
        {"seed": 9, "session": "criterion", "condition_loc": 0,
         "metrics": {"0": {"dprime": 1.5, "criterion": -0.4},
                     "3": {"dprime": 1.5, "criterion": 0.4}}},
        {"seed": 9, "session": "criterion", "condition_loc": 3,
         "metrics": {"0": {"dprime": 1.5, "criterion": 0.4},
                     "3": {"dprime": 1.5, "criterion": -0.4}}},
    ]

    effects = counterphased_effects(records)
    assert effects == [{
        "seed": 9,
        "sensitivity_dprime_did": 1.0,
        "sensitivity_criterion_did": 0.0,
        "criterion_dprime_did": 0.0,
        "criterion_criterion_did": -0.8,
    }]


def test_balanced_evaluation_bank_is_reproducible_and_location_matched():
    import numpy as np
    import torch
    from experiments.luo2015_episodic.analyze_matrix import balanced_trial_bank

    np.random.seed(123)
    state_before = np.random.get_state()
    first = balanced_trial_bank(magnitude=18.0, trials_per_location=2, seed=77)
    state_after = np.random.get_state()
    second = balanced_trial_bank(magnitude=18.0, trials_per_location=2, seed=77)

    assert all(np.array_equal(a, b) for a, b in zip(state_before, state_after))
    for left, right in zip(first, second):
        if torch.is_tensor(left):
            assert torch.equal(left, right)
        else:
            assert np.array_equal(left, right)
    change_videos, no_change_videos, change_locs, no_change_locs = first
    assert change_videos.shape == no_change_videos.shape == (4, 7, 3, 50, 50)
    assert np.bincount(change_locs, minlength=4).tolist() == [2, 0, 0, 2]
    assert np.bincount(no_change_locs, minlength=4).tolist() == [2, 0, 0, 2]


def test_full_run_parent_gate_requires_balanced_target_theta_competence(tmp_path):
    from experiments.luo2015_episodic.run_matrix import validate_parent_gate

    checkpoint = tmp_path / "parent.pt"
    torch.save({"environment_state": {"theta": 24.0}}, checkpoint)
    with pytest.raises(RuntimeError, match="target theta"):
        validate_parent_gate(
            checkpoint, target_theta=18.0, min_accuracy=0.75,
            min_valid_fraction=0.9, gate_metrics={},
        )

    torch.save({"environment_state": {"theta": 18.0}}, checkpoint)
    passing = {
        "theta": 18.0, "trials_per_status_per_location": 100,
        "locations": {
            "0": {"change_accuracy": 0.9, "no_change_accuracy": 0.86,
                  "change_valid_fraction": 0.98, "no_change_valid_fraction": 0.97},
            "3": {"change_accuracy": 0.88, "no_change_accuracy": 0.84,
                  "change_valid_fraction": 0.96, "no_change_valid_fraction": 0.95},
        },
    }
    asymmetric = json.loads(json.dumps(passing))
    asymmetric["locations"]["3"]["change_accuracy"] = 0.5
    with pytest.raises(RuntimeError, match="location 3 change accuracy"):
        validate_parent_gate(
            checkpoint, target_theta=18.0, min_accuracy=0.75,
            min_valid_fraction=0.9, gate_metrics=asymmetric,
        )

    disengaged = json.loads(json.dumps(passing))
    disengaged["locations"]["0"]["no_change_valid_fraction"] = 0.5
    with pytest.raises(RuntimeError, match="location 0 no-change valid fraction"):
        validate_parent_gate(
            checkpoint, target_theta=18.0, min_accuracy=0.75,
            min_valid_fraction=0.9, gate_metrics=disengaged,
        )

    assert validate_parent_gate(
        checkpoint, target_theta=18.0, min_accuracy=0.75,
        min_valid_fraction=0.9, gate_metrics=passing,
    ) == passing

    with pytest.raises(ValueError, match="finite"):
        validate_parent_gate(
            checkpoint, target_theta=float("nan"), min_accuracy=0.75,
            min_valid_fraction=0.9, gate_metrics=passing,
        )
    with pytest.raises(ValueError, match="between 0 and 1"):
        validate_parent_gate(
            checkpoint, target_theta=18.0, min_accuracy=float("nan"),
            min_valid_fraction=0.9, gate_metrics=passing,
        )


def test_parent_gate_evaluation_matches_checkpoint_environment_and_policy_dynamics(
    tmp_path, monkeypatch,
):
    import numpy as np
    from experiments.luo2015_episodic import analyze_matrix
    from experiments.luo2015_episodic.run_matrix import evaluate_parent_gate_metrics
    from luo2015_analysis import luo2015_core

    checkpoint = tmp_path / "parent.pt"
    torch.save({
        "task": "luo2015_criterion",
        "environment_state": {
            "environment_config": {
                "orientation_sampling": "independent_uniform_axial_0_180",
                "noise_multiplier": 5.0,
                "spatial_grid_size": 2,
            },
        },
    }, checkpoint)

    model = object()
    monkeypatch.setattr(luo2015_core, "load_model", lambda _path: (model, 19999))
    bank_call = {}

    def fake_bank(**kwargs):
        bank_call.update(kwargs)
        videos = torch.zeros(2, 7, 3, 50, 50)
        locations = np.asarray([0, 3], dtype=np.int64)
        return videos, videos.clone(), locations, locations.copy()

    press_calls = []

    def fake_press(_model, videos, batch_size, **kwargs):
        press_calls.append({"model": _model, "batch_size": batch_size, **kwargs})
        return np.asarray([3, 3] if len(press_calls) == 1 else [6, 6])

    monkeypatch.setattr(analyze_matrix, "balanced_trial_bank", fake_bank)
    monkeypatch.setattr(analyze_matrix, "_press_times_batched", fake_press)

    result = evaluate_parent_gate_metrics(
        checkpoint,
        target_theta=18.0,
        trials_per_status_per_location=1,
        eval_seed=77,
        batch_size=64,
    )

    assert bank_call == {
        "magnitude": 18.0,
        "trials_per_location": 1,
        "seed": 77,
        "task": "luo2015_criterion",
        "noise_multiplier": 5.0,
        "spatial_grid_size": 2,
    }
    assert len(press_calls) == 2
    assert all(call["model"] is model for call in press_calls)
    assert all(call["batch_size"] == 64 for call in press_calls)
    assert all(call["inject_memory_noise"] is True for call in press_calls)
    assert all(call["sample_actions"] is True for call in press_calls)
    assert result["evaluation_contract"] == {
        "same_task": True,
        "same_initial_orientation_distribution": True,
        "same_sensory_noise": True,
        "memory_noise_enabled": True,
        "sample_actions": True,
    }


def test_press_times_supports_same_noisy_sampled_policy_used_during_training(monkeypatch):
    import torch
    from luo2015_analysis.luo2015_core import press_times

    calls = []

    class FakeModel:
        def forward_rl_sequence(self, videos, **kwargs):
            calls.append(kwargs)
            return {"actor_logits_seq": torch.zeros(videos.shape[0], videos.shape[1], 2)}

    monkeypatch.setattr(
        torch.distributions.Categorical,
        "sample",
        lambda self: torch.ones(self.batch_shape, dtype=torch.long),
    )
    videos = torch.zeros(3, 7, 3, 50, 50)
    observed = press_times(
        FakeModel(), videos, inject_memory_noise=True, sample_actions=True
    )

    assert calls == [{"inject_memory_noise": True}]
    assert observed.tolist() == [0, 0, 0]


def test_analyzer_rejects_canary_or_incomplete_manifests_before_sdt():
    from experiments.luo2015_episodic.analyze_matrix import validate_analysis_manifest

    with pytest.raises(RuntimeError, match="canary"):
        validate_analysis_manifest({"run_mode": "canary", "cells": []})
    with pytest.raises(RuntimeError, match="incomplete"):
        validate_analysis_manifest({
            "run_mode": "full",
            "cells": [{"role": "fixed_condition", "status": "running"}],
        })


def test_analyzer_requires_passed_parent_gate_and_exact_child_lineage(tmp_path):
    from experiments.luo2015_episodic.analyze_matrix import validate_analysis_manifest

    parent_checkpoint = tmp_path / "parent.pt"
    parent_checkpoint.write_bytes(b"checkpointed parent weights")
    parent_hash = hashlib.sha256(parent_checkpoint.read_bytes()).hexdigest()
    parent = {
        "id": "seed0/neutral_parent", "role": "neutral_parent", "seed": 0,
        "status": "complete", "final_checkpoint": str(parent_checkpoint),
        "final_checkpoint_sha256": parent_hash,
        "parent_gate": {"status": "passed"},
    }
    children = [
        {
            "id": f"seed0/{task}_loc{loc}", "role": "fixed_condition",
            "seed": 0, "status": "complete", "task": f"luo2015_{task}",
            "condition_loc": loc, "parent_checkpoint_sha256": parent_hash,
        }
        for task in ("sensitivity", "criterion")
        for loc in (0, 3)
    ]
    manifest = {"run_mode": "full", "cells": [parent, *children]}
    validate_analysis_manifest(manifest)

    manifest["cells"][1]["parent_checkpoint_sha256"] = "wrong-parent"
    with pytest.raises(RuntimeError, match="lineage"):
        validate_analysis_manifest(manifest)

    manifest["cells"][1]["parent_checkpoint_sha256"] = parent_hash
    manifest["cells"][0]["parent_gate"] = {"status": "failed"}
    with pytest.raises(RuntimeError, match="parent gate"):
        validate_analysis_manifest(manifest)

    manifest["cells"][0]["parent_gate"] = {"status": "passed"}
    parent_checkpoint.write_bytes(b"tampered")
    with pytest.raises(RuntimeError, match="parent checkpoint hash"):
        validate_analysis_manifest(manifest)
