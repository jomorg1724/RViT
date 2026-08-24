from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def load_builder():
    module_path = Path(__file__).parents[1] / "tools" / "build_run_registry.py"
    spec = importlib.util.spec_from_file_location("build_run_registry", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_metrics(path: Path, iterations: list[int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "iter,rolling/correct_rate\n"
        + "".join(f"{iteration},0.5\n" for iteration in iterations),
        encoding="utf-8",
    )


def test_discover_run_candidates_uses_only_the_two_metrics_roots(tmp_path: Path) -> None:
    primary = tmp_path / "battery_sweep_results" / "a" / "metrics.csv"
    secondary = (
        tmp_path
        / "RViT_plus_paper_jepa_conv"
        / "battery_sweep_results"
        / "b"
        / "metrics.csv"
    )
    unrelated = tmp_path / "elsewhere" / "metrics.csv"
    for path in (secondary, unrelated, primary):
        write_metrics(path, [0])

    builder = load_builder()

    assert [path.relative_to(tmp_path).as_posix() for path in builder.discover_metrics(tmp_path)] == [
        "RViT_plus_paper_jepa_conv/battery_sweep_results/b/metrics.csv",
        "battery_sweep_results/a/metrics.csv",
    ]


def test_discovery_rejects_symlink_root_and_metrics_candidate(tmp_path: Path) -> None:
    builder = load_builder()
    outside = tmp_path / "outside"
    write_metrics(outside / "run" / "metrics.csv", [0])
    discovery_root = tmp_path / "battery_sweep_results"
    discovery_root.symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="discovery root.*symlink"):
        builder.discover_metrics(tmp_path)

    discovery_root.unlink()
    run_dir = discovery_root / "run"
    run_dir.mkdir(parents=True)
    (run_dir / "metrics.csv").symlink_to(outside / "run" / "metrics.csv")

    with pytest.raises(ValueError, match="metrics candidate.*symlink"):
        builder.discover_metrics(tmp_path)


def test_build_run_extracts_identity_config_and_logged_phase_status(tmp_path: Path) -> None:
    metrics = (
        tmp_path
        / "battery_sweep_results"
        / "pod2"
        / "ckpt2"
        / "vda9_crossattn1_d256_rew10"
        / "metrics.csv"
    )
    write_metrics(metrics, list(range(20_000)))
    (metrics.parent / "rvit_plus_rl_latest.pt").write_bytes(b"checkpoint bytes")

    builder = load_builder()
    run = builder.build_run(tmp_path, metrics, hash_checkpoints=False, hash_source=False)

    assert run["run_id"] == "run-battery-sweep-results--pod2--ckpt2--vda9-crossattn1-d256-rew10"
    assert run["experiment_id"] == "rvit-plus-paper-jepa-grid9:vda9"
    assert run["task"] == "vda9"
    assert run["producer_path"] == "RViT_plus_paper_jepa_grid9"
    assert run["feedback"] == "crossattn1"
    assert run["d_mem"] == 256
    assert run["reward_scale"] == 10.0
    assert run["config"]["memory_noise"] == 0.0
    assert run["planned_iterations"] == 20_000
    assert run["max_logged_iteration"] == 19_999
    assert run["status"] == "logged_phase_complete"
    assert run["completion_reason"] == "budget_complete"
    assert run["checkpoint_paths"] == [
        "battery_sweep_results/pod2/ckpt2/vda9_crossattn1_d256_rew10/rvit_plus_rl_latest.pt"
    ]
    assert run["checkpoint_sha256"] == {
        run["checkpoint_paths"][0]: None,
    }
    assert any("not convergence" in caveat for caveat in run["caveats"])


def test_unknown_launch_convention_never_guesses_budget_completion(tmp_path: Path) -> None:
    metrics = tmp_path / "battery_sweep_results" / "synthetic_unknown" / "metrics.csv"
    write_metrics(metrics, list(range(20_000)))
    builder = load_builder()

    run = builder.build_run(tmp_path, metrics, hash_source=False)

    assert run["task"] == "unknown"
    assert run["planned_iterations"] is None
    assert run["config"]["planned_iterations_inference"] is None
    assert run["status"] == "partial"
    assert run["completion_reason"] == "unknown"
    assert any("No recognized launch convention" in caveat for caveat in run["caveats"])


@pytest.mark.parametrize(
    "run_name",
    [
        "vda10_affine_ew_d128",
        "vda1_synthetic_known_task_name",
    ],
)
def test_near_miss_and_synthetic_known_task_names_remain_unknown(
    tmp_path: Path, run_name: str
) -> None:
    metrics = tmp_path / "battery_sweep_results" / run_name / "metrics.csv"
    write_metrics(metrics, list(range(20_000)))
    builder = load_builder()

    run = builder.build_run(tmp_path, metrics, hash_source=False)

    assert run["task"] == "unknown"
    assert run["planned_iterations"] is None
    assert run["config"]["planned_iterations_inference"] is None
    assert run["status"] == "partial"
    assert run["completion_reason"] == "unknown"


def test_completion_caveat_uses_actual_36k_planned_budget(tmp_path: Path) -> None:
    metrics = (
        tmp_path
        / "battery_sweep_results"
        / "motion_affine_ew_twolstm_mps"
        / "metrics.csv"
    )
    write_metrics(metrics, list(range(36_000)))
    builder = load_builder()

    run = builder.build_run(tmp_path, metrics, hash_source=False)

    assert run["planned_iterations"] == 36_000
    assert run["status"] == "logged_phase_complete"
    assert any("36,000 metrics rows" in caveat for caveat in run["caveats"])
    assert not any("20,000 metrics rows" in caveat for caveat in run["caveats"])


def test_build_run_stream_hashes_raw_checkpoints_and_preserves_unknowns(tmp_path: Path) -> None:
    metrics = (
        tmp_path
        / "battery_sweep_results"
        / "baruni_memnoise"
        / "baruni_crossattn1_mn05"
        / "metrics.csv"
    )
    write_metrics(metrics, [0, 1, 0])
    checkpoint = metrics.parent / "rvit_plus_rl_latest.pt"
    checkpoint.write_bytes(b"not a model tensor payload")
    source = tmp_path / "RViT_plus_paper_jepa_conv" / "train_rl.py"
    source.parent.mkdir(parents=True)
    source.write_text("print('producer')\n", encoding="utf-8")

    builder = load_builder()
    run = builder.build_run(tmp_path, metrics, hash_checkpoints=True, hash_source=True)

    checkpoint_key = checkpoint.relative_to(tmp_path).as_posix()
    assert run["checkpoint_sha256"][checkpoint_key] == hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    assert run["source_tree_sha256"] is not None
    assert len(run["source_tree_sha256"]) == 64
    assert run["task"] == "baruni"
    assert run["config"]["memory_noise"] == 0.5
    assert run["max_logged_iteration"] == 1
    assert run["status"] == "partial"
    assert run["completion_reason"] == "unknown"
    assert run["command"] is None
    assert run["seed"] is None
    assert run["start_time"] is None
    assert run["end_time"] is None
    assert any("reset" in caveat for caveat in run["caveats"])


def test_write_registry_is_deterministic_and_emits_one_json_line_per_run(tmp_path: Path) -> None:
    write_metrics(tmp_path / "battery_sweep_results" / "pod2" / "ckpt2" / "vda4_affine_ew_d128" / "metrics.csv", [0])
    write_metrics(
        tmp_path
        / "RViT_plus_paper_jepa_conv"
        / "battery_sweep_results"
        / "motion_convrec_affine_ew_twolstm_mps"
        / "metrics.csv",
        [0],
    )
    output = tmp_path / "research_db" / "registry"
    builder = load_builder()

    runs = builder.write_registry(tmp_path, output, hash_checkpoints=False, hash_source=False)
    first_bytes = (output / "artifacts.jsonl").read_bytes()
    builder.write_registry(tmp_path, output, hash_checkpoints=False, hash_source=False)

    lines = (output / "artifacts.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(runs) == len(lines) == 2
    assert first_bytes == (output / "artifacts.jsonl").read_bytes()
    assert [run["run_id"] for run in runs] == sorted(run["run_id"] for run in runs)
    motion_run = next(run for run in runs if run["task"] == "motion_zk")
    assert motion_run["reward_scale"] == 1.0
    projects = __import__("json").loads((output / "projects.json").read_text(encoding="utf-8"))
    assert [project["project_id"] for project in projects["projects"]] == [
        "rvit-plus-paper-jepa-conv",
        "rvit-plus-paper-jepa-grid9",
    ]


def test_normalized_run_id_collision_fails_before_any_output_write(tmp_path: Path) -> None:
    write_metrics(tmp_path / "battery_sweep_results" / "same name" / "metrics.csv", [0])
    write_metrics(tmp_path / "battery_sweep_results" / "same-name" / "metrics.csv", [0])
    output = tmp_path / "registry"
    output.mkdir()
    artifacts = output / "artifacts.jsonl"
    projects = output / "projects.json"
    artifacts.write_bytes(b"original artifacts\n")
    projects.write_bytes(b"original projects\n")
    builder = load_builder()

    with pytest.raises(ValueError, match="run_id collision"):
        builder.write_registry(tmp_path, output, hash_source=False)

    assert artifacts.read_bytes() == b"original artifacts\n"
    assert projects.read_bytes() == b"original projects\n"


def test_collision_preflight_occurs_before_evidence_registry_or_staging_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_metrics(tmp_path / "battery_sweep_results" / "same name" / "metrics.csv", [0])
    write_metrics(tmp_path / "battery_sweep_results" / "same-name" / "metrics.csv", [0])
    output = tmp_path / "registry"
    builder = load_builder()

    def sentinel(*args, **kwargs):
        raise AssertionError("sentinel read or write occurred before collision rejection")

    monkeypatch.setattr(builder, "_open_safe_file", sentinel)
    monkeypatch.setattr(builder, "_existing_checkpoint_hashes", sentinel)
    monkeypatch.setattr(builder, "_stage_bytes", sentinel)

    with pytest.raises(ValueError, match="run_id collision"):
        builder.write_registry(tmp_path, output, hash_source=True)

    assert not output.exists()


def test_generated_registry_validation_failure_leaves_prior_outputs_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    metrics = tmp_path / "battery_sweep_results" / "vda1_affine_ew_d128" / "metrics.csv"
    write_metrics(metrics, [0])
    output = tmp_path / "registry"
    builder = load_builder()
    builder.write_registry(tmp_path, output, hash_source=False)
    artifacts = output / "artifacts.jsonl"
    projects = output / "projects.json"
    prior_artifacts = artifacts.read_bytes()
    prior_projects = projects.read_bytes()
    real_build_run = builder.build_run

    def build_invalid_run(*args, **kwargs):
        run = real_build_run(*args, **kwargs)
        run["metrics_path"] = "missing/metrics.csv"
        return run

    monkeypatch.setattr(builder, "build_run", build_invalid_run)

    with pytest.raises(ValueError, match="generated registry validation failed"):
        builder.write_registry(tmp_path, output, hash_source=False)

    assert artifacts.read_bytes() == prior_artifacts
    assert projects.read_bytes() == prior_projects


def test_structurally_invalid_staged_projects_leave_prior_outputs_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    metrics = tmp_path / "battery_sweep_results" / "vda1_affine_ew_d128" / "metrics.csv"
    write_metrics(metrics, [0])
    output = tmp_path / "registry"
    builder = load_builder()
    builder.write_registry(tmp_path, output, hash_source=False)
    artifacts = output / "artifacts.jsonl"
    projects = output / "projects.json"
    prior_artifacts = artifacts.read_bytes()
    prior_projects = projects.read_bytes()
    real_stage_bytes = builder._stage_bytes

    def stage_invalid_projects(output_dir, name, content):
        staged = real_stage_bytes(output_dir, name, content)
        if name == "projects.json":
            staged.write_text(
                '{"schema_version":1,"projects":"not-a-list"}\n',
                encoding="utf-8",
            )
        return staged

    monkeypatch.setattr(builder, "_stage_bytes", stage_invalid_projects)

    with pytest.raises(ValueError, match="generated projects validation failed"):
        builder.write_registry(tmp_path, output, hash_source=False)

    assert artifacts.read_bytes() == prior_artifacts
    assert projects.read_bytes() == prior_projects


def test_atomic_replacement_failure_rolls_back_all_prior_output_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    metrics = tmp_path / "battery_sweep_results" / "vda1_affine_ew_d128" / "metrics.csv"
    write_metrics(metrics, [0])
    output = tmp_path / "registry"
    builder = load_builder()
    builder.write_registry(tmp_path, output, hash_source=False)
    artifacts = output / "artifacts.jsonl"
    projects = output / "projects.json"
    prior_artifacts = artifacts.read_bytes()
    projects.write_bytes(b'{"prior":true}\n')
    prior_projects = projects.read_bytes()
    real_replace = builder.os.replace
    replace_calls = 0

    def fail_second_replace(source, target):
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 2:
            raise OSError("simulated replacement failure")
        return real_replace(source, target)

    monkeypatch.setattr(builder.os, "replace", fail_second_replace)

    with pytest.raises(OSError, match="simulated replacement failure"):
        builder.write_registry(tmp_path, output, hash_source=False)

    assert artifacts.read_bytes() == prior_artifacts
    assert projects.read_bytes() == prior_projects


def test_rebuild_preserves_checkpoint_hashes_unless_drop_or_recompute_is_explicit(tmp_path: Path) -> None:
    metrics = tmp_path / "battery_sweep_results" / "vda1_affine_ew_d128" / "metrics.csv"
    write_metrics(metrics, [0])
    checkpoint = metrics.parent / "latest.pt"
    checkpoint.write_bytes(b"synthetic checkpoint")
    output = tmp_path / "registry"
    builder = load_builder()
    original = builder.write_registry(tmp_path, output, hash_source=False)
    checkpoint_path = original[0]["checkpoint_paths"][0]
    preserved_digest = "a" * 64
    original[0]["checkpoint_sha256"][checkpoint_path] = preserved_digest
    (output / "artifacts.jsonl").write_text(json.dumps(original[0]) + "\n", encoding="utf-8")

    preserved = builder.write_registry(tmp_path, output, hash_source=False)
    assert preserved[0]["checkpoint_sha256"][checkpoint_path] == preserved_digest

    dropped = builder.write_registry(
        tmp_path,
        output,
        hash_source=False,
        drop_checkpoint_hashes=True,
    )
    assert dropped[0]["checkpoint_sha256"][checkpoint_path] is None

    with pytest.raises(ValueError, match="mutually exclusive"):
        builder.write_registry(
            tmp_path,
            output,
            hash_source=False,
            hash_checkpoints=True,
            drop_checkpoint_hashes=True,
        )


def test_source_hash_ignores_generated_and_volatile_files_but_tracks_producer_source(tmp_path: Path) -> None:
    producer = tmp_path / "producer"
    source = producer / "train_rl.py"
    source.parent.mkdir()
    source.write_text("LEARNING_RATE = 1e-3\n", encoding="utf-8")
    (producer / "config").mkdir()
    (producer / "config" / "default.json").write_text('{"seed": 1}\n', encoding="utf-8")

    builder = load_builder()
    baseline = builder.sha256_source_tree(producer)

    volatile_files = {
        ".pytest_cache/v/cache/nodeids": "cache",
        "tests/.pytest_cache/v/cache/nodeids": "test cache",
        "analysis/derived/results.json": "derived",
        "repro/figs/figure.json": "figure metadata",
        "battery_sweep_results/run/metrics.csv": "iter,loss\n0,1\n",
        "battery_sweep_results/run/checkpoint.pt": "checkpoint",
        "logs/training.log": "log",
        "paper.pdf": "pdf",
        "__pycache__/train_rl.cpython-312.pyc": "bytecode",
        ".DS_Store": "finder metadata",
        "Icon\r": "finder icon metadata",
    }
    for relative, content in volatile_files.items():
        path = producer / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    assert builder.sha256_source_tree(producer) == baseline

    source.write_text("LEARNING_RATE = 2e-3\n", encoding="utf-8")
    assert builder.sha256_source_tree(producer) != baseline


def test_source_and_checkpoint_hashing_reject_symlink_escape(tmp_path: Path) -> None:
    builder = load_builder()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "payload.py").write_bytes(b"outside bytes")

    producer = tmp_path / "producer"
    producer.mkdir()
    (producer / "train_rl.py").symlink_to(outside / "payload.py")
    with pytest.raises(ValueError, match="symlink"):
        builder.sha256_source_tree(producer)

    checkpoint_root = tmp_path / "checkpoints"
    checkpoint_root.mkdir()
    checkpoint = checkpoint_root / "latest.pt"
    checkpoint.symlink_to(outside / "payload.py")
    with pytest.raises(ValueError, match="symlink"):
        builder.sha256_file(checkpoint, allowed_root=checkpoint_root)


def test_source_hash_rejects_symlink_producer_root_and_allowed_subtree(tmp_path: Path) -> None:
    builder = load_builder()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "train_rl.py").write_text("EXTERNAL = True\n", encoding="utf-8")

    producer_link = tmp_path / "producer-link"
    producer_link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="producer root.*symlink"):
        builder.sha256_source_tree(producer_link)

    producer = tmp_path / "producer"
    producer.mkdir()
    (producer / "train_rl.py").write_text("LOCAL = True\n", encoding="utf-8")
    (producer / "config").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="source subtree.*symlink"):
        builder.sha256_source_tree(producer)


def test_build_run_rejects_symlink_metrics_and_logs_without_reading_external_evidence(
    tmp_path: Path,
) -> None:
    builder = load_builder()
    outside = tmp_path / "outside"
    external_metrics = outside / "metrics.csv"
    write_metrics(external_metrics, list(range(20_000)))
    external_log = outside / "training.log"
    external_log.write_text("device=cuda\n", encoding="utf-8")

    run_dir = tmp_path / "battery_sweep_results" / "motion_affine_ew_twolstm_mps"
    run_dir.mkdir(parents=True)
    metrics_link = run_dir / "metrics.csv"
    metrics_link.symlink_to(external_metrics)
    with pytest.raises(ValueError, match="metrics candidate.*symlink"):
        builder.build_run(tmp_path, metrics_link, hash_source=False)

    metrics_link.unlink()
    write_metrics(metrics_link, [0])
    (run_dir / "training.log").symlink_to(external_log)
    with pytest.raises(ValueError, match="log.*symlink"):
        builder.build_run(tmp_path, metrics_link, hash_source=False)


def test_source_tree_hash_frames_per_file_digests_against_boundary_collisions(tmp_path: Path) -> None:
    builder = load_builder()
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    second_frame = len(b"train_rl.py").to_bytes(8, "big") + b"train_rl.py"

    (left / "model.py").write_bytes(b"prefix" + second_frame)
    (left / "train_rl.py").write_bytes(b"suffix")
    (right / "model.py").write_bytes(b"prefix")
    (right / "train_rl.py").write_bytes(second_frame + b"suffix")

    def old_unframed_stream(root: Path) -> bytes:
        return b"".join(
            len(path.name.encode()).to_bytes(8, "big") + path.name.encode() + path.read_bytes()
            for path in sorted(root.iterdir(), key=lambda item: item.name)
        )

    assert old_unframed_stream(left) == old_unframed_stream(right)
    assert builder.sha256_source_tree(left) != builder.sha256_source_tree(right)


def test_write_registry_hashes_each_producer_tree_once(tmp_path: Path) -> None:
    write_metrics(tmp_path / "battery_sweep_results" / "pod2" / "ckpt2" / "vda1_affine_ew_d128" / "metrics.csv", [0])
    write_metrics(tmp_path / "battery_sweep_results" / "pod2" / "ckpt2" / "vda2_affine_ew_d128" / "metrics.csv", [0])
    output = tmp_path / "registry"
    builder = load_builder()
    calls: list[Path] = []

    def record_hash(path: Path) -> str:
        calls.append(path)
        return "a" * 64

    builder.sha256_source_tree = record_hash
    runs = builder.write_registry(tmp_path, output, hash_source=True)

    assert len(runs) == 2
    assert calls == [tmp_path / "RViT_plus_paper_jepa_grid9"]
    assert {run["source_tree_sha256"] for run in runs} == {"a" * 64}


def test_schema_requires_full_manifest_and_controlled_enums() -> None:
    schema_path = Path(__file__).parents[1] / "registry" / "run_manifest.schema.json"
    schema = __import__("json").loads(schema_path.read_text(encoding="utf-8"))
    required = {
        "run_id",
        "experiment_id",
        "task",
        "producer_path",
        "source_tree_sha256",
        "command",
        "config",
        "feedback",
        "d_mem",
        "reward_scale",
        "seed",
        "device",
        "start_time",
        "end_time",
        "planned_iterations",
        "max_logged_iteration",
        "completion_reason",
        "status",
        "metrics_path",
        "checkpoint_paths",
        "checkpoint_sha256",
        "analysis_paths",
        "parent_run_id",
        "caveats",
    }
    assert set(schema["required"]) == required
    assert set(schema["properties"]["completion_reason"]["enum"]) == {
        "budget_complete",
        "early_success",
        "interrupted_infrastructure",
        "interrupted_manual",
        "numerical_failure",
        "policy_collapse",
        "unknown",
    }
    assert set(schema["properties"]["status"]["enum"]) == {
        "active",
        "partial",
        "logged_phase_complete",
    }
    assert schema["properties"]["source_tree_sha256"]["type"] == ["string", "null"]


def test_canonical_registry_matches_fresh_normalized_44_run_build(tmp_path: Path) -> None:
    workspace = Path(__file__).parents[2]
    builder = load_builder()
    candidates = builder.discover_metrics(workspace)
    relative_candidates = [path.relative_to(workspace).as_posix() for path in candidates]

    assert len(candidates) == 44
    assert sum(path.startswith("battery_sweep_results/") for path in relative_candidates) == 43
    assert sum(
        path.startswith("RViT_plus_paper_jepa_conv/battery_sweep_results/")
        for path in relative_candidates
    ) == 1

    fresh_dir = tmp_path / "registry"
    fresh_runs = builder.write_registry(
        workspace,
        fresh_dir,
        hash_checkpoints=False,
        hash_source=True,
    )
    assert len(fresh_runs) == 44
    assert all(
        value is None
        for run in fresh_runs
        for value in run["checkpoint_sha256"].values()
    )

    canonical_path = workspace / "research_db" / "registry" / "artifacts.jsonl"
    assert canonical_path.read_bytes() == (fresh_dir / "artifacts.jsonl").read_bytes()


def test_cli_checks_expected_count_and_writes_registry(tmp_path: Path) -> None:
    write_metrics(tmp_path / "battery_sweep_results" / "one" / "metrics.csv", [0])
    output = tmp_path / "registry"
    script = Path(__file__).parents[1] / "tools" / "build_run_registry.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace",
            str(tmp_path),
            "--registry-dir",
            str(output),
            "--expected-count",
            "1",
            "--no-hash-source",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Wrote 1 runs" in result.stdout
    assert (output / "artifacts.jsonl").is_file()

    mismatch = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace",
            str(tmp_path),
            "--registry-dir",
            str(output),
            "--expected-count",
            "2",
            "--no-hash-source",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert mismatch.returncode == 1
    assert "expected 2" in mismatch.stderr


def test_builder_cli_reports_malformed_existing_jsonl_without_overwriting_it(tmp_path: Path) -> None:
    write_metrics(tmp_path / "battery_sweep_results" / "one" / "metrics.csv", [0])
    output = tmp_path / "registry"
    output.mkdir()
    artifacts = output / "artifacts.jsonl"
    malformed_bytes = b'{}\n{"broken":\n'
    artifacts.write_bytes(malformed_bytes)
    (output / "projects.json").write_bytes(b'{"prior":true}\n')
    script = Path(__file__).parents[1] / "tools" / "build_run_registry.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace",
            str(tmp_path),
            "--registry-dir",
            str(output),
            "--expected-count",
            "1",
            "--no-hash-source",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert f"{artifacts}:2:" in result.stderr
    assert "malformed JSON" in result.stderr
    assert "Traceback" not in result.stderr
    assert artifacts.read_bytes() == malformed_bytes


@pytest.mark.parametrize("iteration", ["NaN", "1e309"])
def test_builder_cli_reports_nonfinite_metric_iteration_with_context(
    tmp_path: Path, iteration: str
) -> None:
    metrics = tmp_path / "battery_sweep_results" / "one" / "metrics.csv"
    metrics.parent.mkdir(parents=True)
    metrics.write_text(f"iter,score\n{iteration},0.5\n", encoding="utf-8")
    output = tmp_path / "registry"
    script = Path(__file__).parents[1] / "tools" / "build_run_registry.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace",
            str(tmp_path),
            "--registry-dir",
            str(output),
            "--expected-count",
            "1",
            "--no-hash-source",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert f"{metrics}:2:" in result.stderr
    assert "non-finite iter metric" in result.stderr
    assert iteration in result.stderr
    assert "Traceback" not in result.stderr
    assert not (output / "artifacts.jsonl").exists()
