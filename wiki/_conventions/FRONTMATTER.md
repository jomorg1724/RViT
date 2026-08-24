---
type: meta
status: stable
created: 2026-05-30
tags:
  - meta/conventions
---

# Frontmatter schema

> Adapted from the Palladio wiki's `FRONTMATTER.md`. This is the contract the
> forked MCP server validates on every `write_page`. Server-fork adaptations
> from upstream Palladio: **(a)** the `type` enum adds `paper` and `thread`;
> **(b)** the slug regex allows underscores (`^[a-z0-9][a-z0-9_-]*$`) and the
> slugger does **not** dasherize, because this corpus is underscore-native;
> **(c)** `depth` is an accepted optional field; **(d)** the parser is real
> YAML (so structured `see_also` objects parse) — the legacy stdlib parser in
> `tools/audit.py` only reads flat scalars/lists and is superseded for reads.

## Required on every page

```yaml
type:    paper | concept | thread | note | conversation | brief | moc | sop | person | preference | adr | meta
status:  stub | draft | stable | archived
created: YYYY-MM-DD
tags:    [...]            # list, may be empty; namespace below
```

`status` is the **lifecycle** axis (see [`PAGE_TYPES.md`](PAGE_TYPES.md)): new
agent writes default to `draft`; the curator promotes to `stable`; superseded
pages go `archived`; thin/placeholder pages are `stub`. (For `paper` pages the
older `status: stub|summary|full` values are migrated to the lifecycle vocab;
the granular completeness axis lives in `depth` — see below.)

### Tag namespace
Hierarchical with forward slashes: `topic/predictive-coding`,
`topic/attention`, `topic/working-memory`, `topic/rl` for subject matter;
`meta/conventions`, `meta/readme` for wiki infrastructure;
`mechanism/recurrence`, `mechanism/gating` for finer categories. The legacy
flat tags already in the corpus (e.g. `self-attention`, `deep-learning`) are
grandfathered; new tags prefer the namespaced form. Redundant pairs (`attention`
alongside `topic/attention`) are not allowed — pick one.

## Optional on every page

```yaml
modified: YYYY-MM-DD       # maintained by write_page; mirrors legacy last_updated
aliases:  [...]            # synonyms/abbreviations; feeds search_wiki filename mode
see_also: [...]            # structured cross-links; see EDGES.md
summary:  "..."            # the L1 TL;DR in machine-readable form (2-4 sentences),
                           #   surfaced by list_pages / find_pages_by_description
spotcheck_history: [...]   # append-only [{date, agent, grade, notes}] written by the curator only
```

`see_also` is the typed cross-link layer (objects: `{slug, rel, summary?,
notes?}`); inline `[[wikilinks]]` in the body are also detected but `see_also`
is what `link_pages` writes and what the backlink graph is built from. Treat
them as redundant by design: wikilinks for the human reading, `see_also` for
the agent walking.

## Slug rule
The slug is the file basename, lowercased, matching `^[a-z0-9][a-z0-9_-]*$`,
and it equals the page's `id`. Cross-references (`related`, `see_also[].slug`,
`[[wikilinks]]`) use this id. Do not rename files to dasherize them — the
underscore ids are canonical and are wired through 1,777 `related:` edges.

## Per-type extras

### `type: paper`  (external research card — the corpus specialty)
The full bibliographic + relational block, all retained from the existing
schema:
```yaml
id, title, authors, year, venue, doi, arxiv, url
tags:          [...]                 # broad topic flags (TAXONOMY.md)
concepts:      [...]                 # finer mechanisms (TAXONOMY.md)
related:       [...]                 # other paper ids this bears on  -> see_also rel: informs
relevance_to:  [...]                 # recurrent_vit | prism_v1 | prism_v2 | rvit_plus
seed_source:   "..."                 # provenance of the entry
depth:         metadata | abstract | summary | full   # completeness axis (orthogonal to status)
```
`depth` is advisory and orthogonal to `status`: a card can be `status: stable,
depth: full`. The eight-section body (`## 1. Abstract` … `## 8. Citations to
follow`) is the L3; layered disclosure adds a `## TL;DR` above it.

### `type: concept`  (atomic mechanism/term)
```yaml
defines:    "Hierarchical predictive coding"   # canonical term (page title)
papers:     [...]                              # anchor papers  -> see_also rel: grounded-in
concepts:   [...]                              # related concepts -> see_also rel: informs
citations:  [...]                              # optional: paper ids the definition relies on
```

### `type: thread`  (narrative through-line / engineering log — local type)
```yaml
title:            "..."
papers:           [...]    # -> see_also rel: informs
concepts:         [...]    # -> see_also rel: applies
source_documents: [...]    # project code / design docs this log tracks
```

### `type: note`  (a finding about our own work — agent write-target)
Required: the base four. Optional provenance (cheapest way to satisfy the
Reproduction dimension of [`REPRODUCIBLE_FINDINGS.md`](REPRODUCIBLE_FINDINGS.md)):
```yaml
source_project:   "RViT_plus"                  # which project/run produced this
source_code:      "RViT_plus/train.py"         # script/module path
source_commit:    "abc123"                     # commit or branch
source_run_id:    "run-6-..."                  # run label / output dir
see_also:         [...]
```

### `type: conversation`  (dated Q&A / run-log — append-only)
```yaml
session_id:   "2026-05-30-..."
model:        "claude-..."
question:     "..."                            # one-line summary
crystallized: [slug, ...]                      # concepts/notes/briefs this exchange produced
# optional agent-run provenance: agent, run_id, started, ended, code_read, scripts_written
```

### `type: moc`  (project hub — for recurrent_vit / prism_v1 / prism_v2 / rvit_plus)
```yaml
scope: "RViT+ research program"
```

### `type: sop` / `person` / `preference` / `adr` / `meta`
Defined for forward compatibility (operational + wiki-meta layers); see
[`PAGE_TYPES.md`](PAGE_TYPES.md). No extra required fields beyond the base four
except `adr` (`id`, `deciders`, `supersedes`/`superseded_by`).

## Validation rules (enforced by the forked server)
1. Required fields present and well-typed.
2. `type` ∈ the enum above; `status` ∈ the enum above.
3. Slug matches `^[a-z0-9][a-z0-9_-]*$` and equals `id`.
4. Every `see_also[].slug` resolves to a vault page (else surfaced in
   `wiki_stats().dead_links`).
5. The agent surfaces validation failures to the user **before** writing.

## Migration note
`tools/migrate_to_see_also.py` brings the existing 282 content pages onto this
schema additively: it adds `type` (papers), `created`, `modified`, `see_also`,
and remaps `paper.status` to the lifecycle vocab from `depth`. It never deletes
or reorders existing fields and is idempotent. Legacy `last_updated` is kept.
