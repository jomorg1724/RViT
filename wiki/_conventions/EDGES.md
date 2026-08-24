---
type: meta
status: stable
created: 2026-05-30
tags:
  - meta/conventions
  - meta/methodology
---

# Edges — layered cross-link discipline

> Adapted from the Palladio wiki's `EDGES.md`. Two local divergences are
> load-bearing: **(1) slugs are underscore-style file ids** (e.g.
> `rao_ballard1999_predictive_coding`, `hierarchical_predictive_coding`), not
> Palladio's dasherized form — the forked server's slugger preserves
> underscores and the slug regex is `^[a-z0-9][a-z0-9_-]*$`. **(2)** the
> controlled vocabulary drops Palladio's product-analytics rels and adds
> neuro-AI ones.

## TL;DR

An edge here is not "page A mentions page B." Every frontmatter `see_also`
entry carries (1) a target `slug`, (2) a `rel` tag from the controlled
vocabulary below, and (3) — for hand-authored or upgraded edges — a
one-sentence `summary` of *what* the relationship is. This makes the graph
queryable and makes relationships legible without re-reading both pages.

## Scope

Applies to **frontmatter `see_also` entries** only. Inline `[[wikilinks]]` in
body prose are not in scope (the surrounding sentence is their context) and
`crystallized:` entries on conversation pages stay bare (the relationship is
uniform). `see_also` is what `link_pages` writes and what the graph walk
(`read_neighborhood`) traverses.

## The layers of an edge

| Layer | YAML key | Content | Length |
|---|---|---|---|
| **L1** | `slug` | Target page's file-id slug. | one slug |
| **L2** | `rel`  | A tag from the vocabulary below. | 1–2 hyphenated words |
| **L3** | `summary` | One-sentence, *specific* description of the relationship. | 5–25 words |
| **L4** | `notes` | Optional multi-paragraph block, only when the edge is itself a finding (e.g. "A refutes B"). | as needed |

```yaml
see_also:
  - slug: hierarchical_predictive_coding
    rel: extends
    summary: "Adds the fast/slow recurrence split to the canonical HPC microcircuit this page defines."
  - slug: rao_ballard1999_predictive_coding
    rel: grounded-in
```

The **bare slug-only** form and the **slug+rel** form are both accepted
(grounded-in graph walks); a hand-authored edge **should** add `summary`. The
linter warns on `rel`-less and `summary`-less edges so they surface as backfill
candidates — it does not reject them.

## Controlled vocabulary for `rel`

Directed from the source page (where the `see_also` lives) to the target.

| `rel` | Meaning |
|---|---|
| `applies` | Source applies the target's method, mechanism, or definition (paper → concept it uses; thread → concept it builds on). |
| `grounded-in` | Source's claim/definition is evidenced by the target paper or source. (concept/finding → paper). |
| `informs` | Source draws background or context from the target; looser than `depends-on`. (the default for `related:` paper↔paper and `relevance_to:` paper→project). |
| `depends-on` | Source's analysis requires the target's result as a direct input. |
| `extends` | Source builds on the target's claim/method without contradicting it. |
| `refines` | Source tightens, corrects, or narrows the target. |
| `refutes` | Source contradicts a load-bearing claim of the target. |
| `corroborates` | Independent evidence agreeing with the target via a different method. |
| `replicates` | Source reproduces the target's result/analysis. |
| `predecessor` | Source was superseded by the target (newer version of the same work). |
| `defines` | Source introduces/defines a term the target uses. |
| `instantiates` | Source is a concrete instance/example of a general concept the target defines. |
| `explains` | Source describes the mechanism underlying the target's observed phenomenon (concept → finding/metric). |
| `audits` | Source is a quality-check / spot-check of the target. |
| `motivates` | Source (a paper or finding) motivates a design choice recorded in the target. |
| `benchmarks` | Source benchmarks against the target's result, dataset, or task. |
| `ablates` | Source ablates a component the target defines or uses. |

### Adding a new `rel`
The vocabulary is intentionally small. When a relationship fits none, pick the
closest tag, add the entry, and **surface the gap to the user** ("I tagged this
`extends`; it's closer to `corroborates` — add `corroborates`?"). Add a new tag
only once a gap has been hit more than once. New tags are appended to the table
above with a dated note in the audit trail below.

### Audit trail — added rels
- Base set seeded 2026-05-30 from the adapted Palladio vocabulary, minus
  `companion-segment` / `companion-window` / `denominator-shares` (product-
  analytics specific), plus `grounded-in` / `motivates` / `benchmarks` /
  `ablates` for this research domain.

## Migration mapping (legacy frontmatter lists → `see_also`)

`tools/migrate_to_see_also.py` performs the initial, additive conversion. It is
intentionally conservative: it emits `slug` + `rel` (no fabricated `summary` —
a generic summary is the anti-pattern this SOP exists to prevent), and only for
targets that resolve to a real page.

| Existing field (owner) | → `rel` | Notes |
|---|---|---|
| `concepts:` on a paper (→ concept file) | `applies` | Ref normalized (`-`↔`_`) to the canonical concept file-id. Refs with no concept page are **not** emitted — they are reported as a "concept pages to create" backlog. |
| `related:` on a paper (→ paper file) | `informs` | All 1,777 resolve today. |
| `relevance_to:` on a paper (→ project) | `informs` | Targets are the `moc` hubs `recurrent_vit` / `prism_v1` / `prism_v2` / `rvit_plus`. |
| `papers:` on a concept (→ paper) | `grounded-in` | The concept's evidential anchors. |
| `concepts:` on a concept (→ concept) | `informs` | |
| `papers:` on a thread (→ paper) | `informs` | |
| `concepts:` on a thread (→ concept) | `applies` | |

The legacy fields (`related`, `concepts`, `relevance_to`, `papers`) are
**preserved** by the migration, not deleted — `see_also` is added alongside.
Deprecating the legacy fields is a later, separate decision once the server
reads `see_also` as the source of truth.

## Self-check before writing an edge
1. Structured form with a valid `slug`?
2. `rel` from the vocabulary above?
3. `summary` (when hand-authoring) one specific sentence, not a generic
   restatement of the slug?
4. Does `slug` resolve to a real page (else flagged in `wiki_stats().dead_links`)?
