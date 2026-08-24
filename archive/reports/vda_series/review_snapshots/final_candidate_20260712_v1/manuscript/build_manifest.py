from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

MANUSCRIPT = Path(__file__).resolve().parent
ROOT = MANUSCRIPT.parents[2]
MODEL_ROOT = ROOT / "RViT_plus_paper_jepa_grid9"
PYTHON = ROOT / ".venv" / "bin" / "python"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


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
    ]
    test_run = subprocess.run(
        test_command,
        cwd=MODEL_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    test_summary = test_run.stdout.strip().splitlines()[-1]

    artifacts = [
        MANUSCRIPT / "main.tex",
        MANUSCRIPT / "main.pdf",
        MANUSCRIPT / "build_manifest.py",
        MANUSCRIPT / "build_tables.py",
        MANUSCRIPT / "build_constituent_tables.py",
        MANUSCRIPT / "generated" / "status_summary.tex",
        MANUSCRIPT / "generated" / "object_status_counts.tex",
        MANUSCRIPT / "generated" / "panel_coverage_table.tex",
        MANUSCRIPT / "generated" / "matched_width_absolute_behavior.tex",
        MANUSCRIPT / "generated" / "matched_width_clamp_constituents.tex",
        MANUSCRIPT / "generated" / "matched_width_constituents.json",
        ROOT / "reports" / "vda_series" / "PANEL_COVERAGE.csv",
        ROOT / "reports" / "vda_series" / "MAH_SOURCE_PANEL_INVENTORY.md",
        ROOT / "reports" / "vda_series" / "FIGURE_COVERAGE_MATRIX.md",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_integrated_manuscript_visual_audit.md",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_final_prose_lint.txt",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_final_prose_lint_disposition.md",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_v15_exact_inventory_audit.md",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_final_161_test_gate.txt",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_final_matched_width_read_only_audits.txt",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_upstream_independent_review.txt",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_v15_independent_review.txt",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_checkpoint_execution_audit.md",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_integrated_four_lens_review.md",
        ROOT / "reports" / "vda_series" / "qa" / "2026-07-12_matched_width_integrated_prose_review.txt",
        MODEL_ROOT / "vda_sweep" / "figs" / "psych.npz",
        MODEL_ROOT / "vda_series" / "task_figures.py",
        MODEL_ROOT / "vda_series" / "architecture_figures.py",
        MODEL_ROOT / "vda_series" / "behavior_figures.py",
        MODEL_ROOT / "vda_series" / "first_wave_figures.py",
        MODEL_ROOT / "scripts" / "build_first_wave_figures.py",
        MODEL_ROOT / "scripts" / "build_matched_width_summary.py",
        MODEL_ROOT / "tests" / "test_vda_first_wave_figures.py",
        MODEL_ROOT / "tests" / "test_matched_width_summary.py",
        MODEL_ROOT / "vda_sweep" / "vda_core.py",
        MODEL_ROOT / "reports" / "vda_series" / "first_wave_20260711_production_QA.md",
        ROOT / "reports" / "vda_series" / "matched_width_20260712_production_v15" / "MANIFEST.json",
        ROOT / "reports" / "vda_series" / "matched_width_20260712_production_v15" / "provenance" / "UPSTREAM_MANIFEST.json",
        ROOT / "reports" / "vda_series" / "matched_width_20260712_production_v15" / "provenance" / "VALIDATION_RESULT.json",
    ]
    artifacts.extend(sorted((ROOT / "reports" / "vda_series" / "figures" / "task").glob("*.pdf")))
    artifacts.extend(sorted((ROOT / "reports" / "vda_series" / "figures" / "architecture").glob("*.pdf")))
    artifacts.extend(sorted((ROOT / "reports" / "vda_series" / "figures" / "behavior").glob("*.pdf")))
    artifacts.extend(sorted((ROOT / "reports" / "vda_series" / "figures" / "behavior").glob("*.json")))
    artifacts.extend(sorted((ROOT / "reports" / "vda_series" / "figures" / "first_wave").glob("*.pdf")))
    artifacts.extend(sorted((ROOT / "reports" / "vda_series" / "figures" / "first_wave").glob("*.json")))
    artifacts.extend(sorted((ROOT / "reports" / "vda_series" / "figures" / "matched_width").glob("*")))
    missing = [str(path) for path in artifacts if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Manifest inputs missing: {missing}")

    metadata = pdf_metadata(pdf)
    rendered_pages = len(list((MANUSCRIPT / "rendered").glob("page-*.png")))
    if rendered_pages != metadata["pages"]:
        raise RuntimeError(
            f"Rendered page count {rendered_pages} does not match PDF page count {metadata['pages']}"
        )

    manifest = {
        "schema_version": 1,
        "artifact_class": "newly authored VDA-series manuscript",
        "not_a_rebuild_of": "reports/upgraded_paper/manuscript/main.pdf",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "pdf": {
            "path": relative(pdf),
            "sha256": sha256(pdf),
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
        },
        "verification": {
            "xelatex_passes": 3,
            "latex_diagnostics": diagnostics,
            "rendered_pages_inspected": rendered_pages,
            "figure_regression_tests": test_summary,
            "visual_qa_record": "reports/vda_series/qa/2026-07-12_matched_width_integrated_manuscript_visual_audit.md",
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
