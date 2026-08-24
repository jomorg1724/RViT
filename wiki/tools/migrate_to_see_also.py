#!/usr/bin/env python3
"""
migrate_to_see_also.py — bring research_db onto the adapted Palladio
conventions (see _conventions/). Additive, idempotent, stdlib-only.

DRY-RUN BY DEFAULT: prints a per-file preview of the frontmatter it WOULD add
or change and writes nothing. Pass --apply to write the changes.

What it does (only to papers/, concepts/, threads/ — never root docs, tools/,
graph/, _conventions/):
  * papers: add `type: paper`; add `created`/`modified`; remap legacy
    `status: stub|summary|full` to the lifecycle vocab `stub|draft|stable`
    using `depth` (full->stable, summary/abstract->draft, metadata->stub).
  * concepts/threads: add `status: stable` (human-authored canon); add
    `created`/`modified`.
  * all three: add a `see_also:` block built from the existing edge-bearing
    frontmatter lists (see EDGES.md migration mapping), emitting only targets
    that resolve to a real page. Unresolved concept refs (tags with no page)
    are reported as a backlog, not emitted.

Idempotent: any field already present is left untouched; a file that already
has see_also/created (and, for papers, type + a lifecycle status) is reported
"up to date". Existing fields are never deleted or reordered; new keys are
inserted just before the closing `---`. Legacy `last_updated`/`related`/
`concepts`/`relevance_to`/`papers` are preserved.

Usage:
    python3 research_db/tools/migrate_to_see_also.py            # dry run
    python3 research_db/tools/migrate_to_see_also.py --verbose  # show every changed file
    python3 research_db/tools/migrate_to_see_also.py --apply     # write changes
    python3 research_db/tools/migrate_to_see_also.py --apply --no-moc  # don't scaffold moc stubs
"""
from __future__ import annotations
import argparse
import datetime as _dt
import os
import re
import sys
import tempfile
from collections import Counter, OrderedDict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DB_ROOT = SCRIPT_DIR.parent
TODAY = _dt.date.today().isoformat()

WORK_IDS = ["recurrent_vit", "prism_v1", "prism_v2", "rvit_plus"]
PAPER_DEPTH_TO_STATUS = {
    "full": "stable", "summary": "draft", "abstract": "draft", "metadata": "stub",
}
PAPER_LEGACY_STATUS_TO_STATUS = {"full": "stable", "summary": "draft", "stub": "stub"}
LIFECYCLE = {"stub", "draft", "stable", "archived"}
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


# --------------------------------------------------------------------------- #
# Frontmatter parsing (read) — handles scalars, block lists, and inline lists #
# --------------------------------------------------------------------------- #
def split_doc(text: str):
    """Return (head_line, fm_lines, close_idx, lines) or None if no frontmatter."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[0], lines[1:i], i, lines
    return None


def parse_fm(fm_lines: list[str]) -> dict:
    data: dict = {}
    cur_key = None
    cur_list = None
    for raw in fm_lines:
        if not raw.strip():
            continue
        stripped = raw.lstrip()
        if stripped.startswith("- "):
            if cur_list is None:
                continue
            cur_list.append(_unquote(stripped[2:].strip()))
            continue
        m = re.match(r"^([A-Za-z0-9_]+):(.*)$", raw)
        if not m:
            continue
        key, rest = m.group(1), m.group(2).strip()
        cur_key = key
        if rest == "" or rest == "[]":
            data[key] = []
            cur_list = data[key]
        elif rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            data[key] = [_unquote(x.strip()) for x in inner.split(",") if x.strip()]
            cur_list = None
        else:
            data[key] = _coerce(_unquote(rest))
            cur_list = None
    return data


def _unquote(v: str) -> str:
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        return v[1:-1]
    return v


def _coerce(v: str):
    try:
        return int(v)
    except ValueError:
        return v


def lead_date(v) -> str | None:
    if not v:
        return None
    m = DATE_RE.search(str(v))
    return m.group(1) if m else None


# --------------------------------------------------------------------------- #
# Index of resolvable slugs                                                    #
# --------------------------------------------------------------------------- #
def stems(d: Path) -> set[str]:
    return {p.stem for p in d.glob("*.md")}


def build_index():
    paper_ids = stems(DB_ROOT / "papers")
    concept_ids = stems(DB_ROOT / "concepts")
    thread_ids = stems(DB_ROOT / "threads")
    # map normalized (hyphen<->underscore folded) concept ref -> canonical file id
    concept_norm = {}
    for cid in concept_ids:
        concept_norm[cid.replace("-", "_")] = cid
    return paper_ids, concept_ids, thread_ids, concept_norm


def norm(s: str) -> str:
    return s.replace("-", "_")


# --------------------------------------------------------------------------- #
# Per-file change computation                                                  #
# --------------------------------------------------------------------------- #
class Change:
    def __init__(self, path: Path, kind: str):
        self.path = path
        self.kind = kind
        self.add_keys: "OrderedDict[str, object]" = OrderedDict()  # key -> value (str or list[edge])
        self.status_remap: tuple[str, str] | None = None           # (old, new) for papers
        self.unresolved_concepts: Counter = Counter()
        self.unresolved_other: list[str] = []

    @property
    def touched(self) -> bool:
        return bool(self.add_keys) or self.status_remap is not None


def edges_for(kind: str, fm: dict, self_id: str, idx) -> tuple[list[dict], Counter, list[str]]:
    paper_ids, concept_ids, thread_ids, concept_norm = idx
    edges: "OrderedDict[tuple, dict]" = OrderedDict()
    unresolved_concepts: Counter = Counter()
    unresolved_other: list[str] = []

    def add(slug, rel):
        if slug == self_id:
            return
        edges.setdefault((slug, rel), {"slug": slug, "rel": rel})

    def resolve_concept(ref):
        return concept_norm.get(norm(ref))

    if kind == "paper":
        for c in fm.get("concepts", []) or []:
            canon = resolve_concept(c)
            if canon:
                add(canon, "applies")
            else:
                unresolved_concepts[c] += 1
        for r in fm.get("related", []) or []:
            if r in paper_ids:
                add(r, "informs")
            else:
                unresolved_other.append(f"related:{r}")
        for w in fm.get("relevance_to", []) or []:
            add(w, "informs")  # target is a moc hub (may not exist yet)
    elif kind == "concept":
        for p in fm.get("papers", []) or []:
            if p in paper_ids:
                add(p, "grounded-in")
            else:
                unresolved_other.append(f"papers:{p}")
        for c in fm.get("concepts", []) or []:
            canon = resolve_concept(c)
            if canon:
                add(canon, "informs")
            else:
                unresolved_concepts[c] += 1
    elif kind == "thread":
        for p in fm.get("papers", []) or []:
            if p in paper_ids:
                add(p, "informs")
            else:
                unresolved_other.append(f"papers:{p}")
        for c in fm.get("concepts", []) or []:
            canon = resolve_concept(c)
            if canon:
                add(canon, "applies")
            else:
                unresolved_concepts[c] += 1
    return list(edges.values()), unresolved_concepts, unresolved_other


def compute(path: Path, kind: str, idx) -> Change | None:
    text = path.read_text(encoding="utf-8")
    doc = split_doc(text)
    if doc is None:
        ch = Change(path, kind)
        ch.unresolved_other.append("NO_FRONTMATTER")
        return ch
    _, fm_lines, _, _ = doc
    fm = parse_fm(fm_lines)
    self_id = fm.get("id", path.stem)
    ch = Change(path, kind)

    # type (papers only)
    if kind == "paper" and "type" not in fm:
        ch.add_keys["type"] = "paper"

    # status
    if kind == "paper":
        cur = fm.get("status")
        if cur not in LIFECYCLE:  # legacy stub|summary|full -> remap
            depth = fm.get("depth")
            new = PAPER_DEPTH_TO_STATUS.get(depth) or \
                PAPER_LEGACY_STATUS_TO_STATUS.get(cur, "draft")
            if cur is None:
                ch.add_keys["status"] = new
            else:
                ch.status_remap = (cur, new)
    else:  # concept / thread
        if "status" not in fm:
            ch.add_keys["status"] = "stable"

    # created / modified
    lu = lead_date(fm.get("last_updated"))
    if "created" not in fm:
        ch.add_keys["created"] = lu or TODAY
    if "modified" not in fm and lu:
        ch.add_keys["modified"] = lu

    # see_also
    if "see_also" not in fm:
        edges, unresolved_concepts, unresolved_other = edges_for(kind, fm, self_id, idx)
        ch.unresolved_concepts = unresolved_concepts
        ch.unresolved_other = unresolved_other
        if edges:
            ch.add_keys["see_also"] = edges
    return ch


# --------------------------------------------------------------------------- #
# Rendering / writing                                                          #
# --------------------------------------------------------------------------- #
def render_added_lines(add_keys: "OrderedDict[str, object]") -> list[str]:
    out: list[str] = []
    for k, v in add_keys.items():
        if k == "see_also":
            out.append("see_also:")
            for e in v:  # list of {slug, rel}
                out.append(f"  - slug: {e['slug']}")
                out.append(f"    rel: {e['rel']}")
        else:
            out.append(f"{k}: {v}")
    return out


def apply_change(ch: Change) -> None:
    text = ch.path.read_text(encoding="utf-8")
    doc = split_doc(text)
    if doc is None:
        return
    head, fm_lines, close_idx, lines = doc
    new_fm = list(fm_lines)
    if ch.status_remap is not None:
        old, new = ch.status_remap
        for i, ln in enumerate(new_fm):
            if re.match(r"^status:\s*", ln):
                new_fm[i] = f"status: {new}"
                break
    new_fm.extend(render_added_lines(ch.add_keys))
    body = lines[close_idx + 1:]
    rebuilt = "\n".join([head] + new_fm + ["---"] + body)
    fd, tmp = tempfile.mkstemp(dir=str(ch.path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(rebuilt)
        os.replace(tmp, ch.path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def preview(ch: Change) -> str:
    rel = ch.path.relative_to(DB_ROOT)
    out = [f"  {rel}"]
    if ch.status_remap is not None:
        out.append(f"      ~ status: {ch.status_remap[0]} -> {ch.status_remap[1]}")
    for ln in render_added_lines(ch.add_keys):
        out.append(f"      + {ln}")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--verbose", action="store_true", help="preview every changed file, not just a sample")
    ap.add_argument("--no-moc", action="store_true", help="with --apply, do not scaffold moc stubs")
    args = ap.parse_args()

    idx = build_index()
    paper_ids, concept_ids, thread_ids, _ = idx

    groups = [("paper", DB_ROOT / "papers"),
              ("concept", DB_ROOT / "concepts"),
              ("thread", DB_ROOT / "threads")]

    changes: list[Change] = []
    for kind, d in groups:
        for p in sorted(d.glob("*.md")):
            ch = compute(p, kind, idx)
            if ch is not None:
                changes.append(ch)

    touched = [c for c in changes if c.touched]
    malformed = [c for c in changes if "NO_FRONTMATTER" in c.unresolved_other]

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"=== migrate_to_see_also.py [{mode}] ===")
    print(f"scanned: {len(changes)} pages ({len(paper_ids)} papers, "
          f"{len(concept_ids)} concepts, {len(thread_ids)} threads)")
    print(f"would change: {len(touched)} pages; already up to date: "
          f"{len(changes) - len(touched) - len(malformed)}; malformed: {len(malformed)}")

    # aggregate stats
    edge_rels: Counter = Counter()
    work_edges = 0
    unresolved_concepts: Counter = Counter()
    unresolved_other: list[str] = []
    for c in changes:
        for e in c.add_keys.get("see_also", []) or []:
            edge_rels[e["rel"]] += 1
            if e["slug"] in WORK_IDS:
                work_edges += 1
        unresolved_concepts.update(c.unresolved_concepts)
        unresolved_other.extend(c.unresolved_other)

    print(f"\nsee_also edges to add: {sum(edge_rels.values())}  by rel: {dict(edge_rels)}")
    print(f"  (of which paper->project 'informs' edges to moc hubs: {work_edges})")

    # sample previews
    sample = touched if args.verbose else touched[:8]
    if sample:
        print(f"\n--- {'all' if args.verbose else 'sample'} changed pages "
              f"({len(sample)} of {len(touched)}) ---")
        for c in sample:
            print(preview(c))

    # backlog: concept tags referenced but with no page
    if unresolved_concepts:
        print(f"\n--- BACKLOG: concept pages to create "
              f"({len(unresolved_concepts)} distinct tags, "
              f"{sum(unresolved_concepts.values())} refs) — top 25 ---")
        for tag, n in unresolved_concepts.most_common(25):
            print(f"  {n:4d}  {tag}")

    # moc hubs to create
    missing_mocs = [w for w in WORK_IDS if w not in paper_ids | concept_ids | thread_ids
                    and not (DB_ROOT / "mocs" / f"{w}.md").exists()]
    if missing_mocs:
        print(f"\n--- moc hubs to create (targets of relevance_to edges): {missing_mocs} ---")
        if args.apply and not args.no_moc:
            print("  scaffolding stubs under mocs/ ...")

    other = [o for o in unresolved_other if o != "NO_FRONTMATTER"]
    if other:
        print(f"\n--- unresolved non-concept refs ({len(other)}) — sample ---")
        for o in other[:15]:
            print(f"  {o}")
    if malformed:
        print(f"\n--- MALFORMED (no frontmatter) ---")
        for c in malformed:
            print(f"  {c.path.relative_to(DB_ROOT)}")

    if args.apply:
        for c in touched:
            apply_change(c)
        if missing_mocs and not args.no_moc:
            scaffold_mocs(missing_mocs)
        print(f"\nAPPLIED to {len(touched)} pages"
              + (f" + {len(missing_mocs)} moc stubs" if (missing_mocs and not args.no_moc) else ""))
        print("Next: run `python3 tools/audit.py` to confirm nothing broke.")
    else:
        print(f"\nDRY RUN — nothing written. Re-run with --apply to write, "
              f"--verbose to see all {len(touched)} changed pages.")
    return 0


def scaffold_mocs(work_ids: list[str]) -> None:
    moc_dir = DB_ROOT / "mocs"
    moc_dir.mkdir(exist_ok=True)
    titles = {
        "recurrent_vit": "Recurrent ViT (arXiv:2502.10955)",
        "prism_v1": "PRISM v1",
        "prism_v2": "PRISM v2",
        "rvit_plus": "RViT+",
    }
    for w in work_ids:
        p = moc_dir / f"{w}.md"
        if p.exists():
            continue
        p.write_text(
            f"---\n"
            f"type: moc\n"
            f"status: stub\n"
            f"created: {TODAY}\n"
            f"scope: \"{titles.get(w, w)} research program\"\n"
            f"tags:\n  - meta/moc\n"
            f"---\n\n"
            f"# {titles.get(w, w)}\n\n"
            f"## TL;DR\n"
            f"Project hub for {titles.get(w, w)}. Stub — to be filled with a curated "
            f"reading path through the papers, concepts, threads, and findings that "
            f"bear on this program.\n\n"
            f"## Plain explanation\n"
            f"_TODO (curator): one paragraph orienting a newcomer to this project and "
            f"linking the entry-point pages in reading order._\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    sys.exit(main())
