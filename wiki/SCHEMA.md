# Schema and compatibility contract

`research_db` currently carries two overlapping compatibility lanes. Agents must preserve their boundary rather than forcing a bulk migration:

1. **Grandfathered legacy schema** — the 265 cards in `papers/` plus legacy-form concept and thread pages explicitly recognized by `tools/audit.py`. These pages remain accepted in place and retain their historical fields.
2. **Wiki-native schema** — the page and edge contract under `_conventions/`, required for every newly wiki-native page in a supported directory and for any legacy page deliberately migrated to the current contract.

The audit and graph builder discover every supported page directory. Untyped legacy paper cards remain valid under the paper contract, and legacy concept/thread pages that match the untouched historical frontmatter signatures remain valid without retrofitted current base fields. Grandfathering is not a general exemption from the current contract: a new concept, thread, MOC, note, brief, conversation, SOP, person, preference, ADR, or typed paper must satisfy the current base fields for its page type. At the 2026-07-11 verification, this dual-schema policy produced a zero-issue audit.

## Governing documents

For wiki-native writes, authority is:

1. [`_conventions/PAGE_TYPES.md`](_conventions/PAGE_TYPES.md)
2. [`_conventions/FRONTMATTER.md`](_conventions/FRONTMATTER.md)
3. [`_conventions/EDGES.md`](_conventions/EDGES.md)
4. [`_conventions/LAYERED_DISCLOSURE.md`](_conventions/LAYERED_DISCLOSURE.md)
5. [`_conventions/REPRODUCIBLE_FINDINGS.md`](_conventions/REPRODUCIBLE_FINDINGS.md)
6. [`_conventions/ARTIFACT_REGISTRY.md`](_conventions/ARTIFACT_REGISTRY.md) for run/artifact identity

This file is the operator bridge. If it conflicts with a convention, follow the convention unless doing so would break the live legacy audit; in that case stop, report the incompatibility, and migrate the validator and content together in a separately authorized change.

## Stable identity rules

- The canonical page slug is the lowercase filename stem and uses `^[a-z0-9][a-z0-9_-]*$`.
- Legacy underscore IDs are permanent. Do not rename files to replace underscores with hyphens.
- Cross-references use slugs/IDs, not filesystem paths.
- Do not delete or rename existing pages. A necessary identity change requires an explicit migration and a redirect/compatibility plan.
- `INDEX.md` is an append-only bibliographic ledger. Never renumber existing paper rows.

## 1. Legacy paper cards

### File naming

```text
papers/{firstauthorlast}{year}_{keyword}.md
```

Use lowercase ASCII. A short keyword identifies the work; established two-author forms may retain both names, such as `rao_ballard1999_predictive_coding.md`.

### Live frontmatter contract

`tools/audit.py` currently requires these fields and vocabularies:

```yaml
---
id: vaswani2017_attention       # required; equals filename stem
title: "Attention Is All You Need"
authors:
  - "Vaswani, Ashish"
  - "Shazeer, Noam"
year: 2017
venue: "NeurIPS"
doi: ""
arxiv: "1706.03762"
url: "https://arxiv.org/abs/1706.03762"
tags:                           # each term declared in TAXONOMY.md
  - transformers
  - deep-learning
concepts:                       # each term declared in TAXONOMY.md
  - scaled-dot-product-attention
related:                        # existing paper ids only
  - bahdanau2014_neural_translation
relevance_to:                   # allowed values below
  - recurrent_vit
  - rvit_plus
seed_source:                    # provenance; preserve existing values exactly
  - vit_paper_ref_23
status: full                    # legacy validator: stub | summary | full
depth: full                     # metadata | abstract | summary | full
last_updated: "2026-07-11"
---
```

Allowed `relevance_to` values in the live audit are:

- `recurrent_vit`
- `prism_v1`
- `prism_v2`
- `rvit_plus`

`seed_source` is historical provenance, not a small closed enum in the live corpus. Preserve existing values; for a new entry, use a truthful, specific source label and record its ledger section. Never retrofit provenance from memory.

### Legacy `status` versus wiki lifecycle `status`

This is the main compatibility hazard:

- `tools/audit.py` accepts paper `status: stub|summary|full`.
- `_conventions/FRONTMATTER.md` defines lifecycle `status: stub|draft|stable|archived` and moves completeness to `depth`.

The corpus still passes the legacy validator, so do **not** bulk-change paper statuses or add a second `status` key. Until a coordinated migration updates both validator and content, existing paper cards retain legacy `status` plus `depth`. Wiki-native non-paper pages use lifecycle status. Treat any paper migration as code-and-content work outside routine editing.

### Paper body and depth

A full card uses the existing eight-section technical body:

1. `## 1. Abstract`
2. `## 2. Why this matters for us`
3. `## 3. Key claims`
4. `## 4. Methods`
5. `## 5. Results`
6. `## 6. Critique / limitations`
7. `## 7. Connection to our work`
8. `## 8. Citations to follow`

Completeness is recorded by `depth`:

- `metadata` — frontmatter and title only;
- `abstract` — adds the abstract;
- `summary` — adds the short research-program connection;
- `full` — includes the complete structured body.

The wiki layered-disclosure convention additionally calls for a plain-language `## TL;DR` above the numbered sections and a machine-readable `summary`. Existing cards are not all migrated; backfill must be additive and evidence-preserving, not a pretext to rewrite bibliographic content.

## 2. Wiki-native pages

Every new wiki-native page uses the base contract:

```yaml
---
type: concept                 # paper | concept | thread | note | conversation |
                              # brief | moc | sop | person | preference | adr | meta
status: draft                 # stub | draft | stable | archived
created: 2026-07-11
tags:
  - topic/attention
summary: "Two to four plain-language sentences when substantive."
see_also:
  - slug: recurrent_vit
    rel: informs
    summary: "States the specific relationship rather than repeating the slug."
---
```

Optional common fields include `modified`, `aliases`, and curator-managed `spotcheck_history`. Substantive pages open with `## TL;DR`, then a plain explanation, then technical detail.

### Grandfathered concepts and threads

The concept and thread pages that predate the wiki-native base contract are accepted through explicit untouched-frontmatter signatures in `tools/audit.py`: legacy concepts carry `id`, `type`, and `papers`; legacy threads carry `id`, `type`, `title`, `papers`, `concepts`, and `last_updated`; neither form carries any of `created`, lifecycle `status`, or `tags`. This preserves historical frontmatter without exempting partially written current pages. Do not copy an old page as a template for a new one: newly created concepts and threads require `type`, lifecycle `status`, `created`, and `tags`. A deliberate conversion of a grandfathered page should add the current fields coherently and keep its slug, evidence links, and legacy relationship fields unless an authorized migration says otherwise.

### Page-type locations

| Type | Location | Function |
|---|---|---|
| `paper` | `papers/` | External research card; original paper is quotation authority. |
| `concept` | `concepts/` | One atomic mechanism or term with paper anchors. |
| `thread` | `threads/` | Chronological narrative or engineering history. |
| `moc` | `mocs/` when present | Curated project/lineage hub. |
| `note` | `notes/` when present | Finding or bounded working-memory record. |
| `brief` | `briefs/` when present | Synthesis across multiple concepts or findings. |
| `conversation` | `conversations/` when present | Append-only exchange or agent-run record. |
| `sop` | `sops/` when introduced | Repeatable operational procedure. |
| `adr` | `_adr/` when introduced | Immutable wiki architecture decision. |
| `meta` | `_conventions/` and operator docs | Governance and navigation. |

Do not create an empty directory merely to make the layout look complete. Create a layer when an authorized substantive page needs it.

### Typed edges

Wiki-native relations use structured `see_also` entries from `_conventions/EDGES.md`. The controlled relations currently include `applies`, `grounded-in`, `informs`, `depends-on`, `extends`, `refines`, `refutes`, `corroborates`, `replicates`, `predecessor`, `defines`, `instantiates`, `explains`, `audits`, `motivates`, `benchmarks`, and `ablates`.

Legacy `related`, `concepts`, `relevance_to`, and `papers` lists remain in place under the compatibility policy. Do not delete them merely because a `see_also` edge exists. Hand-authored edges should carry a specific summary; never fabricate relationship text for bulk migration.

### Finding pages

Any page asserting a result about this research program must include:

1. Research goal
2. Method
3. Finding
4. Evidence
5. Reproduction
6. Caveats

Resolve run IDs through the canonical registry and link the exact producer/artifact path. Because the workspace root is non-Git, do not invent `source_commit`; use a verified source-tree hash or explicitly mark the commit unknown. A result with missing evidence remains `status: stub` and labels the claim as a hypothesis.

## 3. Registry schema boundary

The canonical run index is:

- `registry/artifacts.jsonl` — one deterministic run record per line;
- `registry/projects.json` — producer catalog;
- `registry/run_manifest.schema.json` — JSON Schema.

Registry records describe artifact identity, source hashes, configuration, progress, status, artifact paths, and lineage. They do not prove convergence or manuscript support. `logged_phase_complete` means the planned metrics-row phase is present; it is not a convergence label. Unknown commands, seeds, devices, timestamps, and completion causes remain unknown.

Do not hand-edit generated registry JSON/JSONL. Use `tools/build_run_registry.py`, then audit both modes.

## 4. Derived graph boundary

`tools/build_graph.py` discovers `papers/`, `concepts/`, `threads/`, `briefs/`, `notes/`, `mocs/`, `conversations/`, `sops/`, `people/`, `preferences/`, and `_adr/` when those directories are present. It preserves legacy field-derived edges, adds typed `see_also` edges, and uses synthetic historical work nodes only when no real page owns that ID. Registry records remain outside this page graph.

Therefore:

- `graph/graph.json`, `graph/graph.graphml`, and `graph/graph_summary.md` are derived and rebuildable;
- graph counts are not corpus authority;
- a stale generated export does not prove a source page or run is absent;
- the registry, not the graph, is the canonical run index.

At the 2026-07-11 verification, the generated JSON, GraphML, and Markdown summary had been rebuilt from the current source pages and all reported 388 nodes and 3,859 edges. The total includes 89 synthetic `taxonomy-concept` nodes for controlled legacy concept terms that are referenced but do not yet have standalone concept pages; these nodes prevent the graph from silently dropping valid taxonomy relationships.

## Validation commands

Run from `/Users/jonathanmorgan/AttentionManuscript`:

```bash
.venv/bin/python research_db/tools/audit.py
.venv/bin/python research_db/tools/build_graph.py
.venv/bin/python research_db/tools/build_run_registry.py
.venv/bin/python research_db/tools/audit_runs.py
.venv/bin/python research_db/tools/audit_runs.py --strict-active
.venv/bin/python -m pytest research_db/tests -q
```

The two build commands write generated state. Run them only when their source inputs changed and the change is within your assigned scope. Always audit after rebuilding.
