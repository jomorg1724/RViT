from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from scripts import run_matched_width as R
from tests.test_matched_width import _valid_shard_payload


def test_runner_freezes_full_matched_width_execution_and_validation_graph():
    sources = R.capture_executable_sources()
    assert set(sources) == {
        "__runner__",
        "__metrics_inventory__",
        "vda_sweep/matched_width.py",
        "vda_sweep/matched_width_compute.py",
        "vda_sweep/matched_width_producer.py",
        *R.PRODUCER_DEPENDENCIES,
        *R.VALIDATION_SOURCES,
    }
    R.assert_executable_sources_unchanged(sources)


def test_runner_defaults_to_registered_versioned_scope():
    args = R.parse_args([])
    assert args.output_root == R.ROOT / "vda_sweep/derived/2026-07-11_matched_width"
    assert args.audit is False
    assert args.no_finalize is False
    assert args.cell is None


def test_registered_shard_names_are_exact_and_vda2_is_absent():
    matched, _ = R._load_modules(R.capture_executable_sources())
    names = R.expected_shard_names(matched)
    checkpoints = R._checkpoint_records(matched)
    assert len(names) == 12
    assert len(checkpoints) == 12
    assert all("nlink" not in record for record in checkpoints)
    assert "vda1_affine_ew_d128.npz" in names
    assert "vda9_crossattn1_d256.npz" in names
    assert not any("vda2" in name for name in names)


def test_regular_files_rejects_unmanifested_and_linked_entries(tmp_path: Path):
    root = tmp_path / "run"
    root.mkdir()
    admitted = root / "RUN_SPEC.json"
    admitted.write_text("{}")
    R.require_exact_inventory(root, {admitted})

    extra = root / "extra.txt"
    extra.write_text("no")
    with pytest.raises(RuntimeError, match="inventory mismatch"):
        R.require_exact_inventory(root, {admitted})
    extra.unlink()

    alias = root / "alias.json"
    alias.symlink_to(admitted)
    with pytest.raises(RuntimeError, match="symlink or special"):
        R.regular_run_files(root)


def test_inventory_gate_removes_recreated_empty_finder_sidecars(tmp_path: Path):
    root = tmp_path / "run"
    nested = root / "provenance" / "execution"
    nested.mkdir(parents=True)
    admitted = root / "RUN_SPEC.json"
    admitted.write_text("{}")
    sidecars = [root / "Icon\r", nested / "Icon\r"]
    for sidecar in sidecars:
        sidecar.write_bytes(b"")

    R.require_clean_exact_inventory(root, {admitted})

    assert not any(sidecar.exists() for sidecar in sidecars)
    assert R.regular_run_files(root) == {admitted}


def test_finder_cleanup_refuses_and_preserves_hardlinked_sidecar(tmp_path: Path):
    root = tmp_path / "run"
    root.mkdir()
    external = tmp_path / "external"
    external.write_bytes(b"")
    sidecar = root / "Icon\r"
    sidecar.hardlink_to(external)

    with pytest.raises(RuntimeError, match="linked Finder sidecar"):
        R.remove_known_finder_metadata(root)

    assert sidecar.exists()
    assert external.exists()
    assert sidecar.stat().st_nlink == 2


def test_finder_cleanup_refuses_and_preserves_nonempty_sidecar(tmp_path: Path):
    root = tmp_path / "run"
    root.mkdir()
    sidecar = root / "Icon\r"
    sidecar.write_bytes(b"not Finder metadata")

    with pytest.raises(RuntimeError, match="non-empty or linked Finder sidecar"):
        R.remove_known_finder_metadata(root)

    assert sidecar.read_bytes() == b"not Finder metadata"


def test_competence_evidence_is_semantically_bound():
    sources = R.capture_executable_sources()
    matched, _ = R._load_modules(sources)
    R.validate_competence_evidence(sources, matched)
    tampered = dict(sources)
    tampered["__metrics_inventory__"] = tampered["__metrics_inventory__"].replace(
        b",0.480000,0.459350,0.582500,65.000000,",
        b",0.480000,0.459351,0.582500,65.000000,",
        1,
    )
    with pytest.raises(RuntimeError, match="competence evidence mismatch"):
        R.validate_competence_evidence(tampered, matched)


def test_initialize_resume_roundtrip_rejects_protocol_tampering(tmp_path: Path):
    sources = R.capture_executable_sources()
    matched, producer = R._load_modules(sources)
    runtime = producer.numerical_runtime()
    root = tmp_path / "run"
    run_spec, admitted = R.initialize_run(root, sources, matched, runtime)
    loaded, resumed_admitted = R.validate_run_spec(root, sources, matched, runtime)
    assert loaded == run_spec
    assert resumed_admitted == admitted
    R.require_exact_inventory(root, admitted)

    run_spec_path = root / "RUN_SPEC.json"
    tampered = json.loads(run_spec_path.read_text())
    first_protocol = next(iter(tampered["protocols"].values()))
    first_protocol["decoder_n"] = 899
    run_spec_path.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n")
    with pytest.raises(RuntimeError, match="staged protocols differ"):
        R.validate_run_spec(root, sources, matched, runtime)


def test_resume_rejects_numerical_runtime_tampering(tmp_path: Path):
    sources = R.capture_executable_sources()
    matched, producer = R._load_modules(sources)
    runtime = producer.numerical_runtime()
    root = tmp_path / "run"
    R.initialize_run(root, sources, matched, runtime)
    tampered_runtime = {**runtime, "device": "mps"}
    with pytest.raises(RuntimeError, match="live numerical runtime differs"):
        R.validate_run_spec(root, sources, matched, tampered_runtime)


def test_existing_shard_rejects_mixed_runtime(tmp_path: Path):
    sources = R.capture_executable_sources()
    matched, producer = R._load_modules(sources)
    runtime = producer.numerical_runtime()
    expected_hashes = R.source_hashes(sources)
    spec = matched.admissible_specs()[0]
    root = tmp_path / "run"
    (root / "shards").mkdir(parents=True)
    payload = _valid_shard_payload(
        spec, source_hashes=expected_hashes, runtime=runtime
    )
    metadata = json.loads(str(payload["metadata_json"]))
    metadata["runtime"] = {**runtime, "device": "mps"}
    payload["metadata_json"] = np.asarray(json.dumps(metadata, sort_keys=True))
    np.savez_compressed(root / "shards" / R.shard_name(spec), **payload)
    with pytest.raises(RuntimeError, match="shard numerical runtime mismatch"):
        R.validate_existing_shards(root, matched, expected_hashes, runtime)


def test_finalize_audit_is_read_only_and_rejects_snapshot_tampering(tmp_path: Path):
    sources = R.capture_executable_sources()
    matched, producer = R._load_modules(sources)
    runtime = producer.numerical_runtime()
    expected_hashes = R.source_hashes(sources)
    root = tmp_path / "run"
    run_spec, admitted = R.initialize_run(root, sources, matched, runtime)
    for spec in matched.admissible_specs():
        payload = _valid_shard_payload(
            spec, source_hashes=expected_hashes, runtime=runtime
        )
        np.savez_compressed(root / "shards" / R.shard_name(spec), **payload)
    manifest = R.finalize_run(
        root, run_spec, admitted, matched, sources, runtime
    )
    before = tuple(
        sorted((path.relative_to(root), R.sha256(path)) for path in R.regular_run_files(root))
    )
    assert R.audit_existing_run(
        root, startup_sources=sources, matched=matched, runtime=runtime
    ) == manifest
    after = tuple(
        sorted((path.relative_to(root), R.sha256(path)) for path in R.regular_run_files(root))
    )
    assert after == before

    run_spec_path = root / "RUN_SPEC.json"
    run_spec_bytes = run_spec_path.read_bytes()
    run_spec_path.write_bytes(run_spec_bytes + b" \n")
    with pytest.raises(RuntimeError, match="RUN_SPEC.json byte identity changed"):
        R.audit_existing_run(
            root, startup_sources=sources, matched=matched, runtime=runtime
        )
    run_spec_path.write_bytes(run_spec_bytes)

    manifest_bytes = manifest.read_bytes()
    manifest_document = json.loads(manifest_bytes)
    manifest_document["validation_gate"]["command"] = "not the registered gate"
    manifest.write_text(json.dumps(manifest_document, indent=2, sort_keys=True) + "\n")
    with pytest.raises(RuntimeError, match="validation-gate record"):
        R.audit_existing_run(
            root, startup_sources=sources, matched=matched, runtime=runtime
        )
    manifest.write_bytes(manifest_bytes)
    assert R.audit_existing_run(
        root, startup_sources=sources, matched=matched, runtime=runtime
    ) == manifest

    manifest_document = json.loads(manifest_bytes)
    manifest_document["shards"].append(dict(manifest_document["shards"][0]))
    manifest.write_text(json.dumps(manifest_document, indent=2, sort_keys=True) + "\n")
    with pytest.raises(RuntimeError, match="canonical ordered identities"):
        R.audit_existing_run(
            root, startup_sources=sources, matched=matched, runtime=runtime
        )
    manifest.write_bytes(manifest_bytes)

    manifest_document = json.loads(manifest_bytes)
    manifest_document["shards"] = list(reversed(manifest_document["shards"]))
    manifest.write_text(json.dumps(manifest_document, indent=2, sort_keys=True) + "\n")
    with pytest.raises(RuntimeError, match="canonical ordered identities"):
        R.audit_existing_run(
            root, startup_sources=sources, matched=matched, runtime=runtime
        )
    manifest.write_bytes(manifest_bytes)
    assert R.audit_existing_run(
        root, startup_sources=sources, matched=matched, runtime=runtime
    ) == manifest

    snapshot = root / run_spec["sources"][0]["snapshot_path"]
    snapshot.write_bytes(snapshot.read_bytes() + b"\n# tampered\n")
    with pytest.raises(RuntimeError, match="source snapshot identity changed"):
        R.audit_existing_run(
            root, startup_sources=sources, matched=matched, runtime=runtime
        )


def test_finalize_rolls_back_manifest_when_postpublication_audit_fails(
    tmp_path: Path, monkeypatch
):
    sources = R.capture_executable_sources()
    matched, producer = R._load_modules(sources)
    runtime = producer.numerical_runtime()
    root = tmp_path / "run"
    run_spec, admitted = R.initialize_run(root, sources, matched, runtime)
    shard_paths = {
        root / "shards" / name for name in R.expected_shard_names(matched)
    }
    for path in shard_paths:
        np.savez_compressed(path, placeholder=np.asarray(1))

    monkeypatch.setattr(
        R,
        "validate_existing_shards",
        lambda *args, **kwargs: shard_paths,
    )
    monkeypatch.setattr(R, "validate_cross_shard_replay", lambda *args, **kwargs: None)

    def reject_audit(*args, **kwargs):
        raise RuntimeError("forced postpublication audit failure")

    monkeypatch.setattr(R, "audit_existing_run", reject_audit)
    with pytest.raises(RuntimeError, match="forced postpublication audit failure"):
        R.finalize_run(root, run_spec, admitted, matched, sources, runtime)
    assert not (root / "MANIFEST.json").exists()
    R.require_exact_inventory(root, admitted | shard_paths)
