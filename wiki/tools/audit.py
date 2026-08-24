"""Schema audit for legacy paper cards and current research-wiki pages."""
from __future__ import annotations

import datetime as dt
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
DB_ROOT = SCRIPT_DIR.parent
TAXONOMY_PATH = DB_ROOT / "TAXONOMY.md"

PAGE_DIRECTORIES = {
    "papers": "paper",
    "concepts": "concept",
    "threads": "thread",
    "briefs": "brief",
    "notes": "note",
    "mocs": "moc",
    "conversations": "conversation",
    "sops": "sop",
    "people": "person",
    "preferences": "preference",
    "_adr": "adr",
}

LEGACY_PAPER_REQUIRED_FIELDS = {
    "id", "title", "authors", "year", "venue", "tags", "concepts",
    "relevance_to", "seed_source", "status", "depth", "last_updated",
}
CURRENT_REQUIRED_FIELDS = {"type", "status", "created", "tags"}
LEGACY_NON_PAPER_SIGNATURES = {
    "concept": {"id", "type", "papers"},
    "thread": {"id", "type", "title", "papers", "concepts", "last_updated"},
}
ALLOWED_RELEVANCE = {"recurrent_vit", "prism_v1", "prism_v2", "rvit_plus"}
ALLOWED_DEPTH = {"metadata", "abstract", "summary", "full"}
ALLOWED_LEGACY_PAPER_STATUS = {"stub", "summary", "full"}
ALLOWED_CURRENT_STATUS = {"stub", "draft", "stable", "archived"}
ALLOWED_RELS = {
    "applies", "grounded-in", "informs", "depends-on", "extends",
    "refines", "refutes", "corroborates", "replicates", "predecessor",
    "defines", "instantiates", "explains", "audits", "motivates",
    "benchmarks", "ablates",
}


def load_taxonomy_terms(path: Path) -> set[str]:
    """Extract every backtick-quoted taxonomy term."""
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"`([a-zA-Z][a-zA-Z0-9_\-/]+)`", text))


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Parse a Markdown YAML frontmatter mapping with PyYAML."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.DOTALL)
    if match is None:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _values(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _is_legacy_non_paper(fm: dict[str, Any], expected_type: str) -> bool:
    """Recognize untouched legacy concept/thread frontmatter, not partial wiki pages."""
    signature = LEGACY_NON_PAPER_SIGNATURES.get(expected_type)
    return bool(
        signature
        and signature <= set(fm)
        and fm.get("type") == expected_type
        and not ({"created", "status", "tags"} & set(fm))
    )


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_iso_date(value: Any) -> bool:
    if isinstance(value, dt.datetime):
        return False
    if isinstance(value, dt.date):
        return True
    if not isinstance(value, str):
        return False
    try:
        return dt.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def discover_pages(db_root: Path) -> list[tuple[Path, str]]:
    """Return Markdown pages from every supported substantive directory present."""
    pages: list[tuple[Path, str]] = []
    for directory, page_type in PAGE_DIRECTORIES.items():
        page_dir = db_root / directory
        if page_dir.exists():
            pages.extend((path, page_type) for path in sorted(page_dir.glob("*.md")))
    return pages


def audit_database(db_root: Path = DB_ROOT) -> dict[str, Any]:
    """Audit a database root and return issues plus dynamic summary counts."""
    db_root = Path(db_root)
    pages = discover_pages(db_root)
    taxonomy = load_taxonomy_terms(db_root / "TAXONOMY.md")
    issues: list[str] = []
    records: list[tuple[Path, str, dict[str, Any] | None]] = []
    counts: Counter[str] = Counter()
    slugs: dict[str, list[Path]] = {}
    depth_counts: Counter[str] = Counter()
    seed_counts: Counter[str] = Counter()
    relevance_counts: Counter[str] = Counter()

    for path, expected_type in pages:
        counts[expected_type] += 1
        slugs.setdefault(path.stem, []).append(path)
        fm = parse_frontmatter(path)
        records.append((path, expected_type, fm))
        if fm is None:
            issues.append(f"[{path.name}] frontmatter missing or malformed")

    for slug, slug_paths in sorted(slugs.items()):
        if len(slug_paths) > 1:
            locations = ", ".join(path.relative_to(db_root).as_posix() for path in slug_paths)
            issues.append(f"duplicate slug '{slug}' across directories: {locations}")

    all_slugs = set(slugs)
    paper_slugs = {path.stem for path, expected_type in pages if expected_type == "paper"}
    concept_slugs = {path.stem for path, expected_type in pages if expected_type == "concept"}

    for path, expected_type, fm in records:
        if fm is None:
            continue
        label = f"[{path.name}]"
        is_legacy_paper = expected_type == "paper" and "type" not in fm
        is_legacy_non_paper = _is_legacy_non_paper(fm, expected_type)

        if is_legacy_paper:
            missing_paper = LEGACY_PAPER_REQUIRED_FIELDS - set(fm)
            if missing_paper:
                issues.append(f"{label} missing fields: {sorted(missing_paper)}")

            depth = fm.get("depth")
            if depth not in ALLOWED_DEPTH:
                issues.append(f"{label} depth '{depth}' not in {ALLOWED_DEPTH}")
            else:
                depth_counts[str(depth)] += 1

            relationship_values: dict[str, list[str]] = {}
            for field in ("concepts", "related", "relevance_to"):
                value = fm.get(field, [])
                if not _is_string_list(value):
                    issues.append(f"{label} {field} must be a list of strings")
                    relationship_values[field] = []
                else:
                    relationship_values[field] = value

            for relevance in relationship_values["relevance_to"]:
                if relevance not in ALLOWED_RELEVANCE:
                    issues.append(f"{label} relevance_to '{relevance}' not in {ALLOWED_RELEVANCE}")
                else:
                    relevance_counts[str(relevance)] += 1
            for source in _values(fm.get("seed_source")):
                seed_counts[str(source)] += 1

            for tag in _values(fm.get("tags")):
                if taxonomy and tag not in taxonomy:
                    issues.append(f"{label} tag '{tag}' not in TAXONOMY.md")
            for concept in relationship_values["concepts"]:
                if taxonomy and concept not in taxonomy:
                    issues.append(f"{label} concept '{concept}' not in TAXONOMY.md")
            for related in relationship_values["related"]:
                if related not in paper_slugs:
                    issues.append(f"{label} related id '{related}' does not resolve to a paper file")

        if is_legacy_paper:
            status = fm.get("status")
            if status not in ALLOWED_LEGACY_PAPER_STATUS:
                issues.append(f"{label} status '{status}' not in {ALLOWED_LEGACY_PAPER_STATUS}")
        elif not is_legacy_non_paper:
            missing_current = CURRENT_REQUIRED_FIELDS - set(fm)
            if missing_current:
                issues.append(f"{label} missing fields: {sorted(missing_current)}")
            actual_type = fm.get("type")
            if not isinstance(actual_type, str) or actual_type != expected_type:
                issues.append(
                    f"{label} type '{actual_type}' does not match directory type '{expected_type}'"
                )
            status = fm.get("status")
            if not isinstance(status, str) or status not in ALLOWED_CURRENT_STATUS:
                issues.append(f"{label} status '{status}' not in {ALLOWED_CURRENT_STATUS}")
            if "created" in fm and not _is_iso_date(fm.get("created")):
                issues.append(f"{label} created must be a YYYY-MM-DD date")
            if "tags" in fm and not _is_string_list(fm.get("tags")):
                issues.append(f"{label} tags must be a list of strings")

        if expected_type in {"concept", "thread"}:
            for field, targets, target_kind in (
                ("papers", paper_slugs, "paper"),
                ("concepts", concept_slugs, "concept"),
            ):
                value = fm.get(field, [])
                if not _is_string_list(value):
                    issues.append(f"{label} {field} must be a list of strings")
                    continue
                for target in value:
                    normalized = target.replace("-", "_") if target_kind == "concept" else target
                    resolves = normalized in targets
                    if target_kind == "concept":
                        resolves = resolves or target in taxonomy or normalized in taxonomy
                    if not resolves:
                        target_description = (
                            "concept page or taxonomy term" if target_kind == "concept" else "paper file"
                        )
                        issues.append(
                            f"{label} {field} id '{target}' does not resolve to a {target_description}"
                        )

        if fm.get("id") is not None and fm.get("id") != path.stem:
            issues.append(f"{label} id '{fm.get('id')}' != filename stem '{path.stem}'")

        see_also = fm.get("see_also", [])
        if see_also is None:
            see_also = []
        if not isinstance(see_also, list):
            issues.append(f"{label} see_also must be a list")
            continue
        for entry in see_also:
            if isinstance(entry, str):
                slug = entry
                if not slug or slug not in all_slugs:
                    issues.append(f"{label} see_also slug '{slug}' does not resolve")
                continue
            if not isinstance(entry, dict):
                issues.append(f"{label} see_also entry must be a string or object")
                continue
            slug = entry.get("slug")
            if not isinstance(slug, str) or not slug:
                issues.append(f"{label} see_also object missing string slug")
            elif slug not in all_slugs:
                issues.append(f"{label} see_also slug '{slug}' does not resolve")
            rel = entry.get("rel")
            if not isinstance(rel, str) or rel not in ALLOWED_RELS:
                issues.append(f"{label} see_also rel '{rel}' not in {ALLOWED_RELS}")

    return {
        "issues": issues,
        "counts": dict(counts),
        "depth_counts": dict(depth_counts),
        "seed_counts": seed_counts,
        "relevance_counts": dict(relevance_counts),
    }


def main() -> int:
    if not (DB_ROOT / "papers").exists():
        print(f"FATAL: papers dir not found: {DB_ROOT / 'papers'}")
        return 1

    report = audit_database(DB_ROOT)
    if not load_taxonomy_terms(TAXONOMY_PATH):
        print(f"WARNING: no taxonomy terms loaded from {TAXONOMY_PATH}")

    print("=== Audit summary ===")
    for directory, page_type in PAGE_DIRECTORIES.items():
        if (DB_ROOT / directory).exists():
            print(f"{directory + '/':<15}: {report['counts'].get(page_type, 0)} files")
    print(f"depth counts   : {report['depth_counts']}")
    print(f"relevance dist : {report['relevance_counts']}")
    print("top seed sources:")
    for source, count in report["seed_counts"].most_common(10):
        print(f"  {source}: {count}")
    print()
    issues = report["issues"]
    print(f"Issues found   : {len(issues)}")
    for issue in issues[:40]:
        print(f"  - {issue}")
    if len(issues) > 40:
        print(f"  ... and {len(issues) - 40} more")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
