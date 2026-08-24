from __future__ import annotations

import json

import pytest

from scripts import build_vda16_manuscript_shard as builder
from vda_series import first_wave_figures
from vda_series import vda16_integration as integration


def test_audit_completed_output_is_read_only_and_hash_closed(tmp_path):
    provenance = tmp_path / "provenance"
    provenance.mkdir()
    validation = provenance / "VALIDATION_RESULT.json"
    validation.write_text('{"result": "pass"}\n', encoding="utf-8")
    evidence = tmp_path / "evidence.bin"
    evidence.write_bytes(b"evidence")
    artifacts = []
    for path in (validation, evidence):
        artifacts.append(integration.artifact_record(path, tmp_path))
    manifest = tmp_path / "MANIFEST.json"
    manifest.write_text(
        json.dumps({"schema_version": 1, "artifacts": artifacts}) + "\n",
        encoding="utf-8",
    )
    identity_before = {
        path.relative_to(tmp_path): (path.stat().st_size, integration.sha256_file(path))
        for path in builder.regular_files(tmp_path)
    }

    assert builder.audit_completed_output(tmp_path) == manifest
    identity_after = {
        path.relative_to(tmp_path): (path.stat().st_size, integration.sha256_file(path))
        for path in builder.regular_files(tmp_path)
    }
    assert identity_after == identity_before

    evidence.write_bytes(b"changed")
    with pytest.raises(RuntimeError, match="identity mismatch"):
        builder.audit_completed_output(tmp_path)


def test_audit_cli_does_not_require_training_run_directory():
    args = builder.parse_args(["--audit", "--output-root", "bundle"])
    assert args.audit is True
    assert args.run_dir is None


def test_builder_snapshots_every_first_wave_dependency():
    assert set(first_wave_figures.PRODUCER_DEPENDENCIES) <= set(
        builder.SOURCE_DEPENDENCIES
    )
