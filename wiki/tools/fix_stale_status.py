#!/usr/bin/env python3
"""Fix stale 'seed status' annotations in §8 (Citations to follow) sections
and in concept/thread bodies.

Three classes of stale phrase:

1. "In seed; being deepened" / "In seed, being deepened" — all entries are
   now at depth:full per the audit, so the phrase is universally outdated.
   Replace with "In seed, full depth".

2. "in cite-trail" — predates the database's seed expansion. Check whether
   the referenced paper now exists in papers/; if so, update to
   "in seed, full depth".

3. "not in seed" / "not yet in seed" / "Not in seed" — paper-id-anchored
   §8 lines that claim the paper isn't in the database. For each such line,
   parse out the leading backticked id and check papers/. If the paper
   exists, update annotation to "In seed, full depth".

Run from repo root:
    python3 research_db/tools/fix_stale_status.py [--dry-run]
"""
import argparse
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
PAPERS_DIR = os.path.join(ROOT, 'papers')
SEARCH_DIRS = [
    os.path.join(ROOT, 'papers'),
    os.path.join(ROOT, 'concepts'),
    os.path.join(ROOT, 'threads'),
]


def all_paper_ids():
    return {f[:-3] for f in os.listdir(PAPERS_DIR) if f.endswith('.md')}


def iter_md_files():
    for d in SEARCH_DIRS:
        for f in sorted(os.listdir(d)):
            if f.endswith('.md'):
                yield os.path.join(d, f)


# ----- pass 1: "In seed; being deepened" → "In seed, full depth"
RE_BEING_DEEPENED = re.compile(r'\b[Ii]n seed[;,]\s+being deepened', re.M)


# ----- pass 2 & 3: id-anchored stale annotations
# Match lines that look like §8 entries:
#   - `paper_id` — annotation text. Suffix.
# Or:
#   - paper_id — annotation text.
# Capture the id and the trailing annotation.
RE_LIST_LINE = re.compile(
    r'^(?P<prefix>-\s+`?)'
    r'(?P<id>[a-z][a-z0-9_]*)'
    r'(?P<mid>`?\s+[—–-]\s+.*?)'
    r'(?P<tail>'
    r'(?:[Nn]ot (?:yet )?in seed)'
    r'|(?:[Ii]n cite-trail)'
    r')'
    r'(?P<suffix>[.;,]?.*)$',
    re.M,
)


def fix_being_deepened(text):
    return RE_BEING_DEEPENED.subn('In seed, full depth', text)


def fix_stale_id_annotations(text, all_ids):
    changes = []

    def repl(m):
        pid = m.group('id')
        if pid in all_ids:
            changes.append(pid)
            return (
                m.group('prefix')
                + pid
                + m.group('mid')
                + 'In seed, full depth'
                + m.group('suffix')
            )
        return m.group(0)

    new = RE_LIST_LINE.sub(repl, text)
    return new, changes


# Also handle the bare "in cite-trail" phrase that appears outside §8 lists
# (e.g., concept-file body prose). Replace with "in seed, full depth" only
# when the surrounding context clearly references a paper that now exists.
RE_CITETRAIL_PROSE = re.compile(r'\bin cite-trail\b')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    ids = all_paper_ids()
    summary = {
        'being_deepened': 0,
        'id_anchored': 0,
        'citetrail_prose': 0,
        'files_changed': 0,
    }
    per_file_details = []

    for path in iter_md_files():
        with open(path) as fh:
            content = fh.read()
        orig = content

        # Pass 1
        content, n1 = fix_being_deepened(content)

        # Pass 2/3
        content, ids_touched = fix_stale_id_annotations(content, ids)
        n2 = len(ids_touched)

        # Pass 4: bare "in cite-trail" — only update if the same paragraph
        # references at least one valid paper id (otherwise the phrase may
        # be deliberately metaphorical).
        n3 = 0
        if 'in cite-trail' in content:
            new = RE_CITETRAIL_PROSE.sub('in seed, full depth', content)
            if new != content:
                content = new
                n3 = orig.count('in cite-trail') - content.count('in cite-trail')

        if content != orig:
            summary['being_deepened'] += n1
            summary['id_anchored'] += n2
            summary['citetrail_prose'] += n3
            summary['files_changed'] += 1
            per_file_details.append((path, n1, n2, n3, ids_touched))
            if not args.dry_run:
                with open(path, 'w') as fh:
                    fh.write(content)

    print(f"Files changed:           {summary['files_changed']}")
    print(f"'being deepened' fixes:  {summary['being_deepened']}")
    print(f"id-anchored 'not in seed'/'in cite-trail' fixes: {summary['id_anchored']}")
    print(f"prose 'in cite-trail' fixes: {summary['citetrail_prose']}")
    if args.dry_run:
        print("\n(dry run — no files written)")
        print("\nSample fixes:")
        for path, n1, n2, n3, ids_touched in per_file_details[:10]:
            rel = os.path.relpath(path, ROOT)
            print(f"  {rel}: bd={n1} id={n2} prose={n3} ids={ids_touched[:3]}")


if __name__ == '__main__':
    main()
