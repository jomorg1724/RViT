from __future__ import annotations

import hashlib
import json
import re
import stat
import subprocess
from datetime import datetime
from pathlib import Path

MANUSCRIPT = Path(__file__).resolve().parent
ROOT = MANUSCRIPT.parents[2]
MODEL_ROOT = ROOT / "RViT_plus_paper_jepa_grid9"
PYTHON = ROOT / ".venv" / "bin" / "python"
VDA_ROOT = ROOT / "reports" / "vda_series"
QA_ROOT = VDA_ROOT / "qa"
SNAPSHOT_ROOT = VDA_ROOT / "review_snapshots" / "final_candidate_20260712_v10_attention_fix"
SNAPSHOT_MANIFEST = SNAPSHOT_ROOT / "SNAPSHOT_MANIFEST.json"
VISUAL_QA = QA_ROOT / "2026-07-12_attention_fix_v10_integrated_manuscript_visual_audit.md"
REVIEW_PREFIX = "2026-07-12_attention_fix_v10_final_review"
REVIEW_ATTESTATIONS = QA_ROOT / f"{REVIEW_PREFIX}_attestations.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def load_json_strict(path: Path) -> dict:
    def reject_constant(value: str) -> None:
        raise ValueError(f"Non-finite JSON constant {value!r} in {path}")

    def unique_object(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key {key!r} in {path}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=reject_constant,
        object_pairs_hook=unique_object,
    )


def validate_snapshot_inventory(path: Path) -> dict:
    manifest = load_json_strict(path)
    root = path.parent
    records = manifest.get("files")
    if not isinstance(records, list):
        raise RuntimeError("Snapshot manifest files must be a list")
    record_map = {record.get("path"): record for record in records}
    if None in record_map or len(record_map) != len(records):
        raise RuntimeError("Snapshot manifest paths are missing or duplicated")
    for name in record_map:
        item = Path(name)
        if item.is_absolute() or ".." in item.parts:
            raise RuntimeError(f"Snapshot manifest path escapes its root: {name!r}")
    actual: dict[str, Path] = {}
    identities: set[tuple[int, int]] = set()
    immutable_flag = getattr(stat, "UF_IMMUTABLE", 0x00000002)
    for candidate in [root, *root.rglob("*")]:
        item_stat = candidate.lstat()
        mode = item_stat.st_mode
        if stat.S_ISLNK(mode):
            raise RuntimeError(f"Snapshot contains a symbolic link: {candidate}")
        if mode & stat.S_IWUSR:
            raise RuntimeError(f"Snapshot entry is owner-writable: {candidate}")
        if not item_stat.st_flags & immutable_flag:
            raise RuntimeError(f"Snapshot entry lacks the immutable flag: {candidate}")
        if stat.S_ISREG(mode):
            if item_stat.st_nlink != 1:
                raise RuntimeError(
                    f"Snapshot file has {item_stat.st_nlink} hard links instead of one: {candidate}"
                )
            identity = (item_stat.st_dev, item_stat.st_ino)
            if identity in identities:
                raise RuntimeError(f"Snapshot reuses a file identity: {candidate}")
            identities.add(identity)
            if candidate != path:
                actual[str(candidate.relative_to(root))] = candidate
    if set(record_map) != set(actual):
        missing = sorted(set(record_map) - set(actual))
        extra = sorted(set(actual) - set(record_map))
        raise RuntimeError(f"Snapshot inventory mismatch: missing={missing}, extra={extra}")
    if manifest.get("file_count_excluding_manifest") != len(actual):
        raise RuntimeError("Snapshot file count does not match exact inventory")
    for name, candidate in actual.items():
        record = record_map[name]
        if record.get("bytes") != candidate.stat().st_size or record.get("sha256") != sha256(candidate):
            raise RuntimeError(f"Snapshot record mismatch: {name}")
    return manifest


def render_set_digest(pages: list[Path]) -> str:
    digest = hashlib.sha256()
    for page in pages:
        digest.update(f"{sha256(page)}  rendered/{page.name}\n".encode("utf-8"))
    return digest.hexdigest()


def validate_visual_qa(source_sha: str, pdf_sha: str, page_count: int, render_digest: str) -> None:
    text = VISUAL_QA.read_text(encoding="utf-8")
    required = [
        "Verdict: **PASS**",
        f"Source SHA-256: `{source_sha}`",
        f"PDF SHA-256: `{pdf_sha}`",
        f"Page count: {page_count}",
        f"ordered `sha256sum rendered/page-*.png` output): `{render_digest}`",
        f"All {page_count} pages of the exact hash-bound PDF passed rendered-page QA.",
    ]
    absent = [marker for marker in required if marker not in text]
    if absent:
        raise RuntimeError(f"Visual-QA record is stale or non-approving: {absent}")


def validate_final_reviews(source_sha: str, pdf_sha: str, snapshot_sha: str) -> dict:
    attestations = load_json_strict(REVIEW_ATTESTATIONS)
    snapshot = load_json_strict(SNAPSHOT_MANIFEST)
    expected_candidate = {
        "snapshot": SNAPSHOT_ROOT.name,
        "snapshot_manifest_sha256": snapshot_sha,
        "source_sha256": source_sha,
        "pdf_sha256": pdf_sha,
        "build_manifest_sha256": snapshot.get("build_manifest_sha256"),
        "ordered_render_set_sha256": snapshot.get("ordered_render_set_sha256"),
        "page_count": snapshot.get("pdf_pages"),
    }
    if set(attestations) != {"schema_version", "candidate", "records"}:
        raise RuntimeError("Final review attestation has an invalid top-level schema")
    if attestations.get("schema_version") != 1 or attestations.get("candidate") != expected_candidate:
        raise RuntimeError("Final review attestation candidate identity is stale or malformed")
    required_verdicts = {
        "feynman": "PASS",
        "hawking": "PASS",
        "tyson": "PASS",
        "thorne": "PASS",
        "prose": "PASS",
        "artifact": "APPROVE",
    }
    records = attestations.get("records")
    if not isinstance(records, list):
        raise RuntimeError("Final review attestations must contain a record list")
    by_role = {record.get("role"): record for record in records}
    if set(by_role) != set(required_verdicts) or len(by_role) != len(records):
        raise RuntimeError("Final review record roles are missing, duplicated, or unexpected")
    required_record_keys = {
        "schema_version",
        "role",
        "verdict",
        "reviewer_identity",
        "candidate",
        "artifact_manifest_sha256",
        "verification",
        "consequential_findings",
        "limitations",
        "files_modified",
        "summary",
    }
    required_identity_keys = {"kind", "delegation_id", "task_index", "lens"}
    identities: set[tuple[str, int]] = set()
    reviewed_artifact_manifest = VDA_ROOT / "figures" / "first_wave" / "PRODUCTION_MANIFEST.json"
    for role, verdict in required_verdicts.items():
        attestation = by_role[role]
        expected_path = relative(QA_ROOT / f"{REVIEW_PREFIX}_{role}.json")
        if set(attestation) != {"role", "path", "sha256"} or attestation != {
            "role": role,
            "path": expected_path,
            "sha256": attestation.get("sha256"),
        }:
            raise RuntimeError(f"{role} attestation record is malformed")
        record_path = ROOT / expected_path
        if not record_path.is_file() or attestation["sha256"] != sha256(record_path):
            raise RuntimeError(f"{role} structured review is missing or hash-mismatched")
        review = load_json_strict(record_path)
        if set(review) != required_record_keys or review.get("schema_version") != 1:
            raise RuntimeError(f"{role} structured review has an invalid schema")
        if review.get("role") != role or review.get("verdict") != verdict:
            raise RuntimeError(f"{role} structured review is non-approving or mislabeled")
        if review.get("candidate") != expected_candidate:
            raise RuntimeError(f"{role} structured review binds a stale candidate")
        identity = review.get("reviewer_identity")
        if not isinstance(identity, dict) or set(identity) != required_identity_keys:
            raise RuntimeError(f"{role} reviewer identity is not strictly typed")
        if identity.get("kind") != "independent_subagent" or identity.get("lens") != role:
            raise RuntimeError(f"{role} reviewer identity has the wrong kind or lens")
        delegation_id = identity.get("delegation_id")
        task_index = identity.get("task_index")
        if not isinstance(delegation_id, str) or not delegation_id.strip():
            raise RuntimeError(f"{role} reviewer delegation identity is empty")
        if not isinstance(task_index, int) or isinstance(task_index, bool) or task_index < 1:
            raise RuntimeError(f"{role} reviewer task index is invalid")
        identity_key = (delegation_id, task_index)
        if identity_key in identities:
            raise RuntimeError(f"{role} reviewer identity is not distinct")
        identities.add(identity_key)
        if review.get("verification") != {"snapshot_verifier_verdict": "PASS"}:
            raise RuntimeError(f"{role} review lacks successful candidate verification")
        if review.get("consequential_findings") != []:
            raise RuntimeError(f"{role} review has unresolved consequential findings")
        if review.get("limitations") != []:
            raise RuntimeError(f"{role} review has unresolved limitations")
        if review.get("files_modified") != []:
            raise RuntimeError(f"{role} reviewer modified files")
        if not isinstance(review.get("summary"), str) or not review["summary"].strip():
            raise RuntimeError(f"{role} structured review summary is empty")
        expected_artifact_sha = sha256(reviewed_artifact_manifest) if role == "artifact" else None
        if review.get("artifact_manifest_sha256") != expected_artifact_sha:
            raise RuntimeError(f"{role} artifact binding is stale or unexpected")
    return attestations


def final_review_roles(attestations: dict) -> list[str]:
    return sorted(record["role"] for record in attestations["records"])


def pdf_metadata(path: Path) -> dict[str, str | int]:
    output = subprocess.run(
        ["pdfinfo", str(path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    fields: dict[str, str | int] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower().replace(" ", "_")] = value.strip()
    fields["pages"] = int(fields["pages"])
    return fields


def main() -> None:
    pdf = MANUSCRIPT / "main.pdf"
    log = (MANUSCRIPT / "main.log").read_text(encoding="utf-8", errors="replace")
    diagnostics = {
        "latex_errors": len(re.findall(r"^!", log, re.MULTILINE)),
        "overfull_hboxes": len(re.findall(r"Overfull \\hbox", log)),
        "overfull_vboxes": len(re.findall(r"Overfull \\vbox", log)),
        "undefined_references_or_citations": len(
            re.findall(
                r"undefined references?|Reference .* undefined|Citation .* undefined",
                log,
                re.IGNORECASE,
            )
        ),
        "missing_glyphs": len(re.findall(r"Missing character", log, re.IGNORECASE)),
    }
    if any(diagnostics.values()):
        raise RuntimeError(f"LaTeX diagnostics are not clean: {diagnostics}")

    source_sha = sha256(MANUSCRIPT / "main.tex")
    pdf_sha = sha256(pdf)
    snapshot = validate_snapshot_inventory(SNAPSHOT_MANIFEST)
    if snapshot.get("source_sha256") != source_sha or snapshot.get("pdf_sha256") != pdf_sha:
        raise RuntimeError("Live source/PDF do not match the immutable review snapshot")
    snapshot_sha = sha256(SNAPSHOT_MANIFEST)

    artifacts = [
        MANUSCRIPT / "main.tex",
        MANUSCRIPT / "main.pdf",
        MANUSCRIPT / "build_manifest.py",
        MANUSCRIPT / "verify_review_snapshot.py",
        MANUSCRIPT / "build_tables.py",
        MANUSCRIPT / "build_constituent_tables.py",
        MANUSCRIPT / "generated" / "status_summary.tex",
        MANUSCRIPT / "generated" / "object_status_counts.tex",
        MANUSCRIPT / "generated" / "panel_coverage_table.tex",
        MANUSCRIPT / "generated" / "matched_width_absolute_behavior.tex",
        MANUSCRIPT / "generated" / "matched_width_clamp_constituents.tex",
        MANUSCRIPT / "generated" / "matched_width_constituents.json",
        VDA_ROOT / "PANEL_COVERAGE.csv",
        VDA_ROOT / "MAH_SOURCE_PANEL_INVENTORY.md",
        VDA_ROOT / "FIGURE_COVERAGE_MATRIX.md",
        VISUAL_QA,
        QA_ROOT / "2026-07-12_attention_fix_v10_265_test_gate.txt",
        QA_ROOT / "2026-07-12_attention_fix_production_audit.md",
        QA_ROOT / "2026-07-12_attention_fix_v10_prose_trigger_lint.txt",
        QA_ROOT / "2026-07-12_attention_fix_v10_prose_trigger_disposition.md",
        QA_ROOT / "2026-07-12_matched_width_v15_exact_inventory_audit.md",
        QA_ROOT / "2026-07-12_final_161_test_gate.txt",
        QA_ROOT / "2026-07-12_final_matched_width_read_only_audits.txt",
        QA_ROOT / "2026-07-12_matched_width_upstream_independent_review.txt",
        QA_ROOT / "2026-07-12_matched_width_v15_independent_review.txt",
        QA_ROOT / "2026-07-12_matched_width_checkpoint_execution_audit.md",
        QA_ROOT / "2026-07-12_matched_width_integrated_four_lens_review.md",
        QA_ROOT / "2026-07-12_matched_width_integrated_prose_review.txt",
        REVIEW_ATTESTATIONS,
        QA_ROOT / f"{REVIEW_PREFIX}_feynman.json",
        QA_ROOT / f"{REVIEW_PREFIX}_hawking.json",
        QA_ROOT / f"{REVIEW_PREFIX}_tyson.json",
        QA_ROOT / f"{REVIEW_PREFIX}_thorne.json",
        QA_ROOT / f"{REVIEW_PREFIX}_prose.json",
        QA_ROOT / f"{REVIEW_PREFIX}_artifact.json",
        SNAPSHOT_MANIFEST,
        MODEL_ROOT / "vda_sweep" / "figs" / "psych.npz",
        MODEL_ROOT / "vda_series" / "task_figures.py",
        MODEL_ROOT / "vda_series" / "architecture_figures.py",
        MODEL_ROOT / "vda_series" / "behavior_figures.py",
        MODEL_ROOT / "vda_series" / "first_wave_figures.py",
        MODEL_ROOT / "scripts" / "build_first_wave_figures.py",
        MODEL_ROOT / "scripts" / "build_matched_width_summary.py",
        MODEL_ROOT / "tests" / "test_vda_first_wave_figures.py",
        MODEL_ROOT / "tests" / "test_matched_width_summary.py",
        MODEL_ROOT / "tests" / "test_vda_build_manifest.py",
        MODEL_ROOT / "vda_sweep" / "vda_core.py",
        MODEL_ROOT / "model.py",
        MODEL_ROOT / "paper_encoder.py",
        MODEL_ROOT / "paper_heads.py",
        MODEL_ROOT / "conv_frontend.py",
        MODEL_ROOT / "reports" / "vda_series" / "first_wave_20260711_production_QA.md",
        VDA_ROOT / "matched_width_20260712_production_v15" / "MANIFEST.json",
        VDA_ROOT / "matched_width_20260712_production_v15" / "provenance" / "UPSTREAM_MANIFEST.json",
        VDA_ROOT / "matched_width_20260712_production_v15" / "provenance" / "VALIDATION_RESULT.json",
    ]
    task_metadata = sorted((VDA_ROOT / "figures" / "task").glob("*.json"))
    architecture_sidecars = sorted((VDA_ROOT / "figures" / "architecture").glob("*.json"))
    if len(task_metadata) != 14 or len(architecture_sidecars) != 1:
        raise RuntimeError(
            f"Expected 14 M1 metadata files and one M2 sidecar; got {len(task_metadata)} and {len(architecture_sidecars)}"
        )
    artifacts.extend(sorted((VDA_ROOT / "figures" / "task").glob("*.pdf")))
    artifacts.extend(task_metadata)
    artifacts.extend(sorted((VDA_ROOT / "figures" / "architecture").glob("*.pdf")))
    artifacts.extend(architecture_sidecars)
    artifacts.extend(sorted((VDA_ROOT / "figures" / "behavior").glob("*.pdf")))
    artifacts.extend(sorted((VDA_ROOT / "figures" / "behavior").glob("*.json")))
    artifacts.extend(sorted((VDA_ROOT / "figures" / "first_wave").glob("*.pdf")))
    artifacts.extend(sorted((VDA_ROOT / "figures" / "first_wave").glob("*.json")))
    artifacts.extend(sorted((VDA_ROOT / "figures" / "matched_width").glob("*")))
    missing = [str(path) for path in artifacts if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Manifest inputs missing: {missing}")

    metadata = pdf_metadata(pdf)
    pages = sorted((MANUSCRIPT / "rendered").glob("page-*.png"))
    expected_names = [f"page-{index:02d}.png" for index in range(1, metadata["pages"] + 1)]
    if [page.name for page in pages] != expected_names:
        raise RuntimeError("Rendered page names are incomplete, duplicated, or non-canonical")
    rendered_pages = len(pages)
    digest = render_set_digest(pages)
    validate_visual_qa(source_sha, pdf_sha, metadata["pages"], digest)
    reviews = validate_final_reviews(source_sha, pdf_sha, snapshot_sha)

    test_command = [
        str(PYTHON),
        "-m",
        "pytest",
        "-q",
        "tests/test_vda_correctness.py",
        "tests/test_vda_first_wave_figures.py",
        "tests/test_vda_series_task_figures.py",
        "tests/test_vda_series_architecture_figures.py",
        "tests/test_vda_series_behavior_figures.py",
        "tests/test_matched_width_summary.py",
        "tests/test_vda_build_manifest.py",
    ]
    test_run = subprocess.run(
        test_command,
        cwd=MODEL_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    test_summary = test_run.stdout.strip().splitlines()[-1]

    manifest = {
        "schema_version": 1,
        "artifact_class": "newly authored VDA-series manuscript",
        "not_a_rebuild_of": "reports/upgraded_paper/manuscript/main.pdf",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "pdf": {
            "path": relative(pdf),
            "sha256": pdf_sha,
            "bytes": pdf.stat().st_size,
            "pages": metadata["pages"],
            "page_size": metadata.get("page_size"),
            "creation_date": metadata.get("creationdate"),
        },
        "evidence_accounting": {
            "source_objects": 22,
            "panel_groups": 68,
            "environments": 14,
            "panel_environment_cells": 952,
            "m1_metadata_records": len(task_metadata),
            "m2_architecture_sidecars": len(architecture_sidecars),
        },
        "verification": {
            "xelatex_passes": 3,
            "latex_diagnostics": diagnostics,
            "rendered_pages_inspected": rendered_pages,
            "ordered_render_set_sha256": digest,
            "figure_regression_tests": test_summary,
            "visual_qa_record": relative(VISUAL_QA),
            "review_snapshot_manifest": relative(SNAPSHOT_MANIFEST),
            "review_snapshot_manifest_sha256": snapshot_sha,
            "final_review_attestations": relative(REVIEW_ATTESTATIONS),
            "final_review_roles": final_review_roles(reviews),
        },
        "artifact_sha256": {relative(path): sha256(path) for path in sorted(set(artifacts))},
    }
    target = MANUSCRIPT / "BUILD_MANIFEST.json"
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {target}")
    print(f"pdf sha256={manifest['pdf']['sha256']}")
    print(f"tests={test_summary}")


if __name__ == "__main__":
    main()
