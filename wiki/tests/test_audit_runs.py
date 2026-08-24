from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def load_auditor():
    module_path = Path(__file__).parents[1] / "tools" / "audit_runs.py"
    spec = importlib.util.spec_from_file_location("audit_runs", module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(metrics_path: str, *, status: str = "partial") -> dict:
    return {
        "run_id": "run-example",
        "experiment_id": "project:task",
        "task": "task",
        "producer_path": "producer",
        "source_tree_sha256": None,
        "command": None,
        "config": {},
        "feedback": "affine_ew",
        "d_mem": 128,
        "reward_scale": 1.0,
        "seed": None,
        "device": None,
        "start_time": None,
        "end_time": None,
        "planned_iterations": 20_000,
        "max_logged_iteration": 100,
        "completion_reason": "unknown",
        "status": status,
        "metrics_path": metrics_path,
        "checkpoint_paths": [],
        "checkpoint_sha256": {},
        "analysis_paths": [],
        "parent_run_id": None,
        "caveats": ["partial evidence"],
    }


def test_audit_reports_missing_provenance_as_warnings_for_inactive_run(tmp_path: Path) -> None:
    metrics = tmp_path / "run" / "metrics.csv"
    metrics.parent.mkdir()
    metrics.write_text("iter\n0\n", encoding="utf-8")
    auditor = load_auditor()

    report = auditor.audit_records(
        [manifest(metrics.relative_to(tmp_path).as_posix())],
        tmp_path,
        strict_active=True,
    )

    assert report["errors"] == []
    warning_fields = {issue["field"] for issue in report["warnings"]}
    assert {"source_tree_sha256", "command", "seed", "device", "start_time", "end_time"} <= warning_fields


def test_strict_active_promotes_missing_provenance_to_errors(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.csv"
    metrics.write_text("iter\n0\n", encoding="utf-8")
    auditor = load_auditor()

    report = auditor.audit_records(
        [manifest("metrics.csv", status="active")],
        tmp_path,
        strict_active=True,
    )

    error_fields = {issue["field"] for issue in report["errors"]}
    assert {"source_tree_sha256", "command", "seed", "device", "start_time", "end_time"} <= error_fields
    assert not ({"source_tree_sha256", "command"} & {issue["field"] for issue in report["warnings"]})


def test_audit_reports_schema_path_and_duplicate_id_errors(tmp_path: Path) -> None:
    first = manifest("missing/metrics.csv")
    first.pop("task")
    second = manifest("also-missing/metrics.csv")
    auditor = load_auditor()

    report = auditor.audit_records([first, second], tmp_path)

    error_fields = [issue["field"] for issue in report["errors"]]
    assert "task" in error_fields
    assert error_fields.count("metrics_path") == 2
    assert "run_id" in error_fields


def test_audit_rejects_absolute_and_traversal_paths(tmp_path: Path) -> None:
    auditor = load_auditor()
    absolute = manifest(str(tmp_path / "metrics.csv"))
    absolute["run_id"] = "run-absolute"
    traversal = manifest("nested/../metrics.csv")
    traversal["run_id"] = "run-traversal"

    report = auditor.audit_records([absolute, traversal], tmp_path)

    unsafe = {
        issue["run_id"]
        for issue in report["errors"]
        if issue["field"] == "metrics_path" and "workspace-relative" in issue["message"]
    }
    assert unsafe == {"run-absolute", "run-traversal"}


def test_audit_rejects_workspace_relative_symlink_escape(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside-metrics.csv"
    outside.write_text("iter\n0\n", encoding="utf-8")
    (workspace / "metrics-link.csv").symlink_to(outside)
    auditor = load_auditor()

    report = auditor.audit_records([manifest("metrics-link.csv")], workspace)

    assert any(
        issue["field"] == "metrics_path" and "escapes workspace" in issue["message"]
        for issue in report["errors"]
    )


def test_audit_validates_schema_types_and_enums(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.csv"
    metrics.write_text("iter\n0\n", encoding="utf-8")
    record = manifest("metrics.csv")
    record["d_mem"] = "128"
    record["completion_reason"] = "finished"
    auditor = load_auditor()

    report = auditor.audit_records([record], tmp_path)

    messages = {(issue["field"], issue["message"]) for issue in report["errors"]}
    assert any(field == "d_mem" and "type" in message for field, message in messages)
    assert any(field == "completion_reason" and "allowed" in message for field, message in messages)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_audit_rejects_nonfinite_numeric_api_values(tmp_path: Path, value: float) -> None:
    (tmp_path / "metrics.csv").write_text("iter\n0\n", encoding="utf-8")
    record = manifest("metrics.csv")
    record["reward_scale"] = value
    auditor = load_auditor()

    report = auditor.audit_records([record], tmp_path)

    assert any(
        issue["field"] == "reward_scale" and "finite" in issue["message"]
        for issue in report["errors"]
    )


def test_audit_requires_checkpoint_hash_keys_to_exactly_match_paths_and_valid_digests(tmp_path: Path) -> None:
    (tmp_path / "metrics.csv").write_text("iter\n0\n", encoding="utf-8")
    (tmp_path / "first.pt").write_bytes(b"first")
    (tmp_path / "second.pt").write_bytes(b"second")
    record = manifest("metrics.csv")
    record["checkpoint_paths"] = ["first.pt", "second.pt"]
    record["checkpoint_sha256"] = {"first.pt": "not-a-digest", "extra.pt": None}
    auditor = load_auditor()

    report = auditor.audit_records([record], tmp_path)

    checkpoint_errors = [
        issue["message"] for issue in report["errors"] if issue["field"] == "checkpoint_sha256"
    ]
    assert any("exactly match" in message and "second.pt" in message and "extra.pt" in message for message in checkpoint_errors)
    assert any("64 lowercase hexadecimal" in message and "first.pt" in message for message in checkpoint_errors)


def test_audit_accepts_valid_rfc3339_timestamps(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.csv"
    metrics.write_text("iter\n0\n", encoding="utf-8")
    record = manifest("metrics.csv")
    record["start_time"] = "2026-07-11T12:34:56Z"
    record["end_time"] = "2026-07-11T12:35:56.123+00:00"
    auditor = load_auditor()

    report = auditor.audit_records([record], tmp_path)

    assert report["errors"] == []


def test_audit_rejects_end_time_before_start_time(tmp_path: Path) -> None:
    (tmp_path / "metrics.csv").write_text("iter\n0\n", encoding="utf-8")
    record = manifest("metrics.csv")
    record["start_time"] = "2026-07-11T12:35:56+00:00"
    record["end_time"] = "2026-07-11T12:34:56Z"
    auditor = load_auditor()

    report = auditor.audit_records([record], tmp_path)

    assert any(
        issue["field"] == "end_time" and "not precede start_time" in issue["message"]
        for issue in report["errors"]
    )


def test_audit_enforces_controlled_status_completion_reason_pairs(tmp_path: Path) -> None:
    (tmp_path / "metrics.csv").write_text("iter\n0\n", encoding="utf-8")
    invalid_pairs = [
        ("run-active", "active", "early_success"),
        ("run-partial", "partial", "budget_complete"),
        ("run-complete", "logged_phase_complete", "unknown"),
    ]
    records = []
    for run_id, status, reason in invalid_pairs:
        record = manifest("metrics.csv", status=status)
        record["run_id"] = run_id
        record["completion_reason"] = reason
        records.append(record)
    auditor = load_auditor()

    report = auditor.audit_records(records, tmp_path)

    semantic_errors = {
        issue["run_id"]
        for issue in report["errors"]
        if issue["field"] == "completion_reason" and "inconsistent with status" in issue["message"]
    }
    assert semantic_errors == {run_id for run_id, _, _ in invalid_pairs}


def test_audit_rejects_invalid_date_time_fields(tmp_path: Path) -> None:
    metrics = tmp_path / "metrics.csv"
    metrics.write_text("iter\n0\n", encoding="utf-8")
    record = manifest("metrics.csv")
    record["start_time"] = "2026-07-11 12:34:56"
    record["end_time"] = "2026-02-30T12:35:56Z"
    auditor = load_auditor()

    report = auditor.audit_records([record], tmp_path)

    format_errors = {
        issue["field"]
        for issue in report["errors"]
        if "date-time" in issue["message"]
    }
    assert format_errors == {"start_time", "end_time"}


def test_cli_audits_jsonl_in_normal_and_strict_active_modes(tmp_path: Path) -> None:
    (tmp_path / "metrics.csv").write_text("iter\n0\n", encoding="utf-8")
    registry = tmp_path / "artifacts.jsonl"
    registry.write_text(json.dumps(manifest("metrics.csv", status="active")) + "\n", encoding="utf-8")
    script = Path(__file__).parents[1] / "tools" / "audit_runs.py"
    base_command = [
        sys.executable,
        str(script),
        "--workspace",
        str(tmp_path),
        "--registry",
        str(registry),
    ]

    normal = subprocess.run(base_command, text=True, capture_output=True, check=False)
    strict = subprocess.run(base_command + ["--strict-active"], text=True, capture_output=True, check=False)

    assert normal.returncode == 0, normal.stderr
    assert json.loads(normal.stdout)["counts"] == {"records": 1, "errors": 0, "warnings": 6}
    assert strict.returncode == 1
    assert json.loads(strict.stdout)["counts"] == {"records": 1, "errors": 6, "warnings": 0}


def test_cli_reports_malformed_jsonl_with_registry_line_and_no_traceback(tmp_path: Path) -> None:
    registry = tmp_path / "artifacts.jsonl"
    registry.write_text('{}\n{"broken":\n', encoding="utf-8")
    script = Path(__file__).parents[1] / "tools" / "audit_runs.py"

    result = subprocess.run(
        [sys.executable, str(script), "--workspace", str(tmp_path), "--registry", str(registry)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert f"{registry}:2:" in result.stderr
    assert "malformed JSON" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


@pytest.mark.parametrize("numeric", ["NaN", "Infinity", "1e10000"])
def test_cli_rejects_nonfinite_or_overflowing_json_numbers_with_line_context(
    tmp_path: Path, numeric: str
) -> None:
    registry = tmp_path / "artifacts.jsonl"
    registry.write_text(f'{{"reward_scale":{numeric}}}\n', encoding="utf-8")
    script = Path(__file__).parents[1] / "tools" / "audit_runs.py"

    result = subprocess.run(
        [sys.executable, str(script), "--workspace", str(tmp_path), "--registry", str(registry)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert f"{registry}:1:" in result.stderr
    assert "non-finite JSON number" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""
