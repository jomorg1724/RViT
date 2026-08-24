#!/usr/bin/env python3
"""Apply main-body orphan edges from find_orphan_mentions.py to paper frontmatter.

For each paper that has main-body orphan mentions (i.e., another paper-id is
cited in §1-7 but absent from the frontmatter's `related:` list), append the
orphan ids to `related:` and bump `last_updated` to today.

Run from repo root:
    python3 research_db/tools/apply_orphan_edges.py [--dry-run] [--date YYYY-MM-DD]

Default mode is --apply (changes files). Use --dry-run to preview.
"""

import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
PAPERS_DIR = os.path.join(ROOT, 'papers')


def parse_frontmatter(content):
    if not content.startswith('---'):
        return None, None, None
    end = content.find('\n---', 3)
    if end < 0:
        return None, None, None
    return content[:end + 4], content[4:end], content[end + 4:]


def get_related(fm):
    related = []
    in_list = False
    for line in fm.split('\n'):
        if re.match(r'^[a-z_]+:', line):
            in_list = line.startswith('related:')
            continue
        if in_list:
            m = re.match(r'^\s+-\s+(\S+)\s*$', line)
            if m:
                related.append(m.group(1))
    return related


def main_body_orphans(paper_id, all_ids, body_main, related):
    out = set()
    for cid in all_ids:
        if cid == paper_id or cid in related:
            continue
        if re.search(r'\b' + re.escape(cid) + r'\b', body_main):
            out.add(cid)
    return sorted(out)


def rewrite_related(fm, additions):
    """Append `additions` (list of ids) to the existing `related:` YAML list.

    Returns the new frontmatter. Preserves order of existing items and
    inserts new items at the end of the list, before the next top-level key.
    """
    lines = fm.split('\n')
    out = []
    i = 0
    inserted = False
    while i < len(lines):
        line = lines[i]
        out.append(line)
        if line.startswith('related:') and not inserted:
            i += 1
            # consume the existing list items
            while i < len(lines) and re.match(r'^\s+-\s', lines[i]):
                out.append(lines[i])
                i += 1
            for add in additions:
                out.append(f'  - {add}')
            inserted = True
            continue
        i += 1
    return '\n'.join(out)


def bump_date(fm, date_str):
    return re.sub(
        r'^last_updated:\s*"\d{4}-\d{2}-\d{2}"',
        f'last_updated: "{date_str}"',
        fm,
        count=1,
        flags=re.M,
    )


def sec8_orphans(paper_id, all_ids, body_sec8, related):
    """Return list of (id, line) pairs for §8 orphans."""
    out = []
    for cid in all_ids:
        if cid == paper_id or cid in related:
            continue
        if not re.search(r'\b' + re.escape(cid) + r'\b', body_sec8):
            continue
        for line in body_sec8.splitlines():
            if (re.search(r'\b' + re.escape(cid) + r'\b', line)
                    and line.lstrip().startswith('-')):
                out.append((cid, line))
                break
    return out


def fix_caps_not_in_seed(body):
    """Catch the variant 'NOT in seed' (caps) that fix_stale_status.py
    missed (it only matched [Nn]ot). Rewrite to 'In seed, full depth.'."""
    pat = re.compile(
        r'NOT (?:yet )?in seed[.;]?\s*(?:\*\*should be added\*\*[.;]?)?'
    )
    return pat.subn('In seed, full depth.', body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--date', default='2026-05-16')
    ap.add_argument(
        '--mode',
        choices=['main', 'sec8', 'both'],
        default='main',
        help="main: only §1-7 mentions. "
             "sec8: also §8 'Citations to follow' entries (any annotation; "
             "any §8 entry whose target paper exists is treated as an edge "
             "candidate). 'NOT in seed' annotations are rewritten in place. "
             "both: union.",
    )
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(PAPERS_DIR) if f.endswith('.md'))
    all_ids = {f[:-3] for f in files}
    sec8_re = re.compile(r'^##\s+8\.\s', re.M)

    n_papers = n_edges = n_caps = 0
    for f in files:
        path = os.path.join(PAPERS_DIR, f)
        with open(path) as fh:
            content = fh.read()
        fm_block, fm, body = parse_frontmatter(content)
        if fm is None:
            continue
        related = set(get_related(fm))
        self_id = f[:-3]

        m8 = sec8_re.search(body)
        body_main = body[:m8.start()] if m8 else body
        body_sec8 = body[m8.start():] if m8 else ''

        additions = set()
        if args.mode in ('main', 'both'):
            additions.update(main_body_orphans(self_id, all_ids, body_main, related))

        body_changed = False
        if args.mode in ('sec8', 'both') and body_sec8:
            new_sec8, ncaps = fix_caps_not_in_seed(body_sec8)
            if ncaps:
                body_sec8 = new_sec8
                body_changed = True
                n_caps += ncaps
            for cid, _line in sec8_orphans(self_id, all_ids, body_sec8, related):
                additions.add(cid)

        additions -= related
        if not additions and not body_changed:
            continue

        if additions:
            new_fm = rewrite_related(fm, sorted(additions))
            new_fm = bump_date(new_fm, args.date)
        else:
            new_fm = bump_date(fm, args.date)
        new_body = body_main + body_sec8 if body_changed else body
        new_content = '---\n' + new_fm + '\n---' + new_body

        n_papers += 1
        n_edges += len(additions)
        marker = '*' if body_changed else ''
        print(f"{self_id}{marker}: +{len(additions)} ({', '.join(sorted(additions))})")

        if not args.dry_run:
            with open(path, 'w') as fh:
                fh.write(new_content)

    print(f"\n# {n_papers} papers updated, {n_edges} edges added, "
          f"{n_caps} caps 'NOT in seed' fixes"
          f"{' (dry run)' if args.dry_run else ''}")


if __name__ == '__main__':
    main()
