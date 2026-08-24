#!/usr/bin/env python3
"""Find paper-id mentions in a paper's body that are missing from its `related:`.

Outputs: paper_id <TAB> count <TAB> orphan1,orphan2,...
Sorted by count descending.

Only flags mentions where:
  - the cited id exists in papers/
  - it is not the paper's own id
  - it is not already in the paper's `related:` frontmatter list
"""

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
PAPERS_DIR = os.path.join(ROOT, 'papers')


def parse_frontmatter(content):
    """Return (frontmatter_str, body_str)."""
    if not content.startswith('---'):
        return '', content
    end = content.find('\n---', 3)
    if end < 0:
        return '', content
    return content[4:end], content[end + 4:]


def get_related(fm):
    """Parse the `related:` list out of YAML-ish frontmatter."""
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
    return set(related)


def main():
    files = sorted(f for f in os.listdir(PAPERS_DIR) if f.endswith('.md'))
    all_ids = {f[:-3] for f in files}

    # Split body at "## 8." (Citations to follow). Mentions in §1-7 are
    # almost always real edges; mentions only in §8 are author-curated
    # discovery candidates and only become real edges when the cited
    # paper actually enters the database.
    sec8_re = re.compile(r'^##\s+8\.\s', re.M)

    results = []
    for f in files:
        with open(os.path.join(PAPERS_DIR, f)) as fh:
            content = fh.read()
        fm, body = parse_frontmatter(content)
        related = get_related(fm)
        self_id = f[:-3]

        sec8_match = sec8_re.search(body)
        if sec8_match:
            body_main = body[:sec8_match.start()]
            body_sec8 = body[sec8_match.start():]
        else:
            body_main = body
            body_sec8 = ''

        mentioned_main = set()
        mentioned_sec8 = set()
        for cid in all_ids:
            if cid == self_id:
                continue
            pat = r'\b' + re.escape(cid) + r'\b'
            if re.search(pat, body_main):
                mentioned_main.add(cid)
            if body_sec8 and re.search(pat, body_sec8):
                mentioned_sec8.add(cid)

        orphans_main = mentioned_main - related
        orphans_sec8_only = (mentioned_sec8 - mentioned_main) - related
        if orphans_main or orphans_sec8_only:
            results.append((self_id, sorted(orphans_main), sorted(orphans_sec8_only)))

    results.sort(key=lambda x: -(len(x[1]) + len(x[2])))
    total_main = total_sec8 = 0
    for sid, om, os8 in results:
        total_main += len(om)
        total_sec8 += len(os8)
        print(f"{sid}\tmain={len(om)}\tsec8only={len(os8)}\tmain:{','.join(om)}\tsec8only:{','.join(os8)}")
    print(
        f"\n# {len(results)} papers with orphans; "
        f"{total_main} main-body orphans (high-confidence edges); "
        f"{total_sec8} §8-only orphans (review individually)",
        file=sys.stderr,
    )


if __name__ == '__main__':
    main()
