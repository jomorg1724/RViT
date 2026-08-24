# Research database and evidence wiki

`research_db/` is the navigation and provenance layer for the AttentionManuscript research program. It contains the external-paper corpus, concept and engineering syntheses, wiki conventions, a canonical run registry, and a rebuildable graph export. It is not itself the scientific source of truth: agents must resolve claims to the owning manuscript, producer code, run artifacts, or original paper.

## Read this first

The workspace root `/Users/jonathanmorgan/AttentionManuscript` is **not a Git repository**. There is no root commit, branch, or Git rollback. Do not move, rename, overwrite, or delete source trees, checkpoints, metrics, logs, NPZ bundles, manuscript sources, or stable wiki IDs as routine cleanup. Use additive changes, preserve unknown provenance as unknown, and obtain explicit approval before physical reorganization.

For current workspace status and implementation history, read:

- [`../reports/research_state/2026-07-11_research_state_briefing.md`](../reports/research_state/2026-07-11_research_state_briefing.md)
- [`../reports/research_state/2026-07-11_implementation_log.md`](../reports/research_state/2026-07-11_implementation_log.md)
- [`HANDOFF.md`](HANDOFF.md) for the operator runbook
- [`SCHEMA.md`](SCHEMA.md) for the dual-schema compatibility contract
- [`INDEX.md`](INDEX.md) for the append-only bibliographic ledger

## Authority order

Use the narrowest applicable authority, in this order:

1. **Canonical source and owning evidence:** the original external paper; the canonical manuscript and trace; producer code; run metrics, checkpoints, analyses, and other primary artifacts.
2. **Canonical run index:** [`registry/artifacts.jsonl`](registry/artifacts.jsonl), [`registry/projects.json`](registry/projects.json), and the governing [`_conventions/ARTIFACT_REGISTRY.md`](_conventions/ARTIFACT_REGISTRY.md). The registry establishes run identity and recorded provenance, not convergence or scientific truth.
3. **Dated workspace synthesis:** the research-state briefing and implementation log linked above. These summarize a verified date; newer primary artifacts can supersede them.
4. **Wiki governance:** files under [`_conventions/`](_conventions/) for page types, frontmatter, edges, layered disclosure, and reproducible findings. [`SCHEMA.md`](SCHEMA.md) explains the live compatibility boundary with the older paper corpus.
5. **Curated navigation and synthesis:** the top-level [`mocs/attention_program.md`](mocs/attention_program.md), project MOCs, evidence-backed notes/briefs, concepts, and threads. These route readers to evidence; they do not override it.
6. **External-paper cards and bibliography:** `papers/`, [`INDEX.md`](INDEX.md), and [`BIBLIOGRAPHY.bib`](BIBLIOGRAPHY.bib).
7. **Derived graph export:** `graph/`. It is a disposable query artifact and may be rebuilt from supported source pages.

If two layers disagree, preserve and report the conflict. Never use graph degree, a search hit, a MOC, or stale prose to override a newer canonical artifact.

## Lineage boundaries

Do not collapse these families:

- **2025 empirical MAH baseline:** Morgan, Albanna, and Herman, *A recurrent vision transformer shows signatures of primate visual attention* (arXiv:2502.10955v1). This is the empirical Recurrent ViT baseline.
- **RViT+ and upgraded empirical paper:** `RVIT_PLUS_DESIGN.md`, the RViT+ producer trees, `RViT_plus_paper_jepa_grid9/`, and `reports/upgraded_paper/` extend or reproduce the empirical line. They are not corrected editions of the normative paper.
- **2026 normative paper:** `Critique/source/main.pdf`, *When Does Value-Directed Attention Matter?*, is a separate stationary signal-detection model. It has no transformer, recurrent memory, or actor–critic network.
- **Normative audit and repair:** `Critique/` audits the normative source; `Rebuild/` is the deepest technical/provenance repair record; `Reconstruction/manuscript/` is the current corrected public-facing normative manuscript. None is a correction of arXiv:2502.10955.
- **PRISM/PrismV2/HRA history:** `Prism/`, `PrismV2/`, and `HRA/` preserve architecture and failure-history lines. They inform RViT+ but are not interchangeable with the current executable empirical producer.

## Layout

```text
research_db/
├── README.md, HANDOFF.md, SCHEMA.md       # operator contract
├── INDEX.md, TAXONOMY.md, BIBLIOGRAPHY.bib
├── _conventions/                          # wiki governance
├── papers/                                # external-paper cards; stable legacy ids
├── concepts/                              # atomic mechanisms and terms
├── threads/                               # narrative and engineering histories
├── mocs/                                  # project hubs when present
├── notes/                                 # evidence-backed findings when present
├── briefs/                                # cross-concept syntheses when present
├── conversations/                         # append-only exchanges when present
├── registry/                              # canonical run index + schema
├── graph/                                 # generated JSON/GraphML/summary
├── tools/                                 # audits, builders, query and migrations
└── tests/                                 # research_db tool tests
```

The page-type convention also reserves `_adr/`, `sops/`, `people/`, and `preferences/` if those layers are introduced. At the 2026-07-11 operator verification, the expansion had added six MOCs, five evidence notes, and one lineage brief; `conversations/` was not present. Re-check the filesystem before relying on those dated counts.

Current MOC routes are:

- [`mocs/attention_program.md`](mocs/attention_program.md) — top-level program map;
- [`mocs/recurrent_vit.md`](mocs/recurrent_vit.md) — 2025 empirical MAH baseline;
- [`mocs/rvit_plus.md`](mocs/rvit_plus.md) — current empirical extension and upgraded manuscript;
- [`mocs/prism_v1.md`](mocs/prism_v1.md) and [`mocs/prism_v2.md`](mocs/prism_v2.md) — architecture-proposal line;
- [`mocs/vda_normative_repair.md`](mocs/vda_normative_repair.md) — separate 2026 normative source and repair chain.

## Verified state (2026-07-11)

Live commands and source inspection reported:

- expanded wiki audit: 0 issues across 265 papers, 16 concepts, 6 threads, 6 MOCs, 5 notes, and 1 brief; paper depth is 261 full and 4 abstract;
- dual-schema boundary: grandfathered legacy paper, concept, and thread pages remain accepted in place, while every newly wiki-native page must carry the current base fields for its page type;
- rebuilt graph artifacts: 388 nodes and 3,859 edges, including 89 referenced taxonomy-concept nodes, 6 MOCs, 5 notes, and 1 brief;
- canonical run registry: 44 unique records, 0 normal-audit errors, 217 explicit unknown-provenance warnings;
- strict-active registry audit: 0 errors (historical unknowns remain warnings);
- `research_db/tests`: 58 passed.

These are dated observations, not constants. Re-run the commands below before citing current counts.

## Standard commands

Run from `/Users/jonathanmorgan/AttentionManuscript`:

```bash
# Validate legacy paper cards and every supported wiki page directory.
.venv/bin/python research_db/tools/audit.py

# Rebuild the derived graph after edits in any supported page directory.
.venv/bin/python research_db/tools/build_graph.py

# Rebuild the canonical run registry from approved metrics roots.
.venv/bin/python research_db/tools/build_run_registry.py

# Audit registry structure and provenance.
.venv/bin/python research_db/tools/audit_runs.py
.venv/bin/python research_db/tools/audit_runs.py --strict-active

# Test research_db tooling.
.venv/bin/python -m pytest research_db/tests -q
```

`build_graph.py` rewrites `graph/graph.json`, `graph/graph.graphml`, and `graph/graph_summary.md`; these artifacts are derived and may be rebuilt. The expanded builder discovers every supported page directory and includes typed `see_also` edges. `build_run_registry.py` rewrites the canonical registry only after staged validation; do not hand-edit its JSON/JSONL outputs. It intentionally refuses unexpected discovery changes under the current 44-candidate contract. See [`registry/README.md`](registry/README.md) before hashing checkpoints or changing registry state.

## Operating rules

- Preserve every paper filename and `id`; cross-references depend on stable underscore-style slugs.
- Keep the bibliographic rows in [`INDEX.md`](INDEX.md) append-only. Add in the appropriate provenance section; never renumber existing rows.
- Follow [`SCHEMA.md`](SCHEMA.md) before editing a legacy paper or adding a wiki-native page. The two lanes are governed by an explicit compatibility policy.
- Add or change taxonomy terms through [`TAXONOMY.md`](TAXONOMY.md) before using them in legacy paper fields.
- New empirical findings must satisfy [`_conventions/REPRODUCIBLE_FINDINGS.md`](_conventions/REPRODUCIBLE_FINDINGS.md): goal, method, finding, evidence, reproduction, and caveats. Missing evidence stays an explicit stub.
- Use typed `see_also` relationships from [`_conventions/EDGES.md`](_conventions/EDGES.md) on wiki-native pages. Do not fabricate edge summaries.
- A `logged_phase_complete` registry status means the planned metrics-row phase is present; it does not mean convergence, replication, or scientific success.
- Never fill an unknown command, seed, device, timestamp, completion cause, or lineage parent with a plausible guess.
