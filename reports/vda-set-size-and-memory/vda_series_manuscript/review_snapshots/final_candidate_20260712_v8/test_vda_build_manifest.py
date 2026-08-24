from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILD_MANIFEST_PATH = PROJECT_ROOT / "reports" / "vda_series" / "manuscript" / "build_manifest.py"
SPEC = importlib.util.spec_from_file_location("vda_build_manifest", BUILD_MANIFEST_PATH)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

VERDICTS = {
    "feynman": "PASS",
    "hawking": "PASS",
    "tyson": "PASS",
    "thorne": "PASS",
    "prose": "PASS",
    "artifact": "APPROVE",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configure_review_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    root = tmp_path
    vda_root = root / "reports" / "vda_series"
    qa_root = vda_root / "qa"
    snapshot_root = vda_root / "review_snapshots" / "final_candidate_20260712_v7"
    qa_root.mkdir(parents=True)
    snapshot_root.mkdir(parents=True)
    monkeypatch.setattr(M, "ROOT", root)
    monkeypatch.setattr(M, "VDA_ROOT", vda_root)
    monkeypatch.setattr(M, "QA_ROOT", qa_root)
    monkeypatch.setattr(M, "SNAPSHOT_ROOT", snapshot_root)
    monkeypatch.setattr(M, "SNAPSHOT_MANIFEST", snapshot_root / "SNAPSHOT_MANIFEST.json")
    monkeypatch.setattr(M, "REVIEW_ATTESTATIONS", qa_root / "2026-07-12_final_review_attestations.json")
    M.SNAPSHOT_MANIFEST.write_text(
        json.dumps({"build_manifest_sha256": "builder", "ordered_render_set_sha256": "render"}),
        encoding="utf-8",
    )
    artifact_root = vda_root / "matched_width_20260712_production_v15"
    artifact_root.mkdir()
    (artifact_root / "MANIFEST.json").write_text("{}\n", encoding="utf-8")
    return {
        "snapshot": "final_candidate_20260712_v7",
        "snapshot_manifest_sha256": "snapshot",
        "source_sha256": "source",
        "pdf_sha256": "pdf",
        "build_manifest_sha256": "builder",
        "ordered_render_set_sha256": "render",
        "page_count": 54,
    }


def write_reviews(candidate: dict, mutate=None) -> None:
    records = []
    artifact_manifest = M.VDA_ROOT / "matched_width_20260712_production_v15" / "MANIFEST.json"
    for index, (role, verdict) in enumerate(VERDICTS.items(), start=1):
        review = {
            "schema_version": 1,
            "role": role,
            "verdict": verdict,
            "reviewer_identity": {
                "kind": "independent_subagent",
                "delegation_id": f"delegation-{index}",
                "task_index": index,
                "lens": role,
            },
            "candidate": candidate,
            "artifact_manifest_sha256": digest(artifact_manifest) if role == "artifact" else None,
            "verification": {"snapshot_verifier_verdict": "PASS"},
            "consequential_findings": [],
            "limitations": [],
            "files_modified": [],
            "summary": "Independent approval.",
        }
        if mutate is not None:
            mutate(role, review)
        path = M.QA_ROOT / f"2026-07-12_final_review_{role}.json"
        path.write_text(json.dumps(review), encoding="utf-8")
        records.append({"role": role, "path": M.relative(path), "sha256": digest(path)})
    M.REVIEW_ATTESTATIONS.write_text(
        json.dumps({"schema_version": 1, "candidate": candidate, "records": records}),
        encoding="utf-8",
    )


def test_manifest_assembly_uses_schema_validated_record_roles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = configure_review_fixture(tmp_path, monkeypatch)
    write_reviews(candidate)
    reviews = M.validate_final_reviews("source", "pdf", "snapshot")
    assert M.final_review_roles(reviews) == sorted(VERDICTS)


def test_review_validation_rejects_empty_reviewer_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = configure_review_fixture(tmp_path, monkeypatch)
    write_reviews(
        candidate,
        lambda role, review: review["reviewer_identity"].__setitem__("delegation_id", "")
        if role == "hawking"
        else None,
    )
    with pytest.raises(RuntimeError, match="identity is empty"):
        M.validate_final_reviews("source", "pdf", "snapshot")


def test_review_validation_rejects_unresolved_consequential_findings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = configure_review_fixture(tmp_path, monkeypatch)
    write_reviews(
        candidate,
        lambda role, review: review.__setitem__("consequential_findings", ["unresolved"])
        if role == "thorne"
        else None,
    )
    with pytest.raises(RuntimeError, match="unresolved consequential findings"):
        M.validate_final_reviews("source", "pdf", "snapshot")
