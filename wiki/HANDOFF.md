# Operator handoff

This is the restart-safe runbook for `research_db/`. It replaces the old one-session handoff and obsolete private-mount instructions. Read [`README.md`](README.md), this file, [`SCHEMA.md`](SCHEMA.md), and the governing conventions before editing.

## Mission

Maintain a research wiki that can route an agent from a question to the correct lineage, run identity, primary artifact, and caveat. The database has three distinct jobs:

1. curate external literature (`papers/`, `concepts/`, `threads/`, `INDEX.md`);
2. route project knowledge through MOCs and evidence-backed notes/briefs as those layers appear;
3. maintain the canonical run index (`registry/`) and a disposable query export (`graph/`).

Do not treat the wiki, registry, and graph as interchangeable. The registry is the canonical index of approved metrics-backed runs. The graph is derived. Neither replaces primary evidence.

## Safety gate

The workspace root `/Users/jonathanmorgan/AttentionManuscript` is **not under Git**. Before any write:

- confirm your writer lane and exact paths;
- inspect current bytes instead of trusting this dated handoff;
- avoid physical moves, renames, deletion, or overwrite of experiments and evidence;
- preserve stable page IDs and registry run IDs;
- keep unknown provenance explicit;
- use a new run directory plus a parent link for resumed or repeated runs;
- obtain explicit approval before reorganizing source/evidence trees.

A root-level `git status`, commit, or reset cannot protect or restore this workspace.

## Scientific lineage map

| Line | Canonical routing | Boundary |
|---|---|---|
| 2025 empirical MAH/Recurrent ViT | arXiv:2502.10955v1 and bundled supplement | Empirical recurrent neural model; baseline for RViT+ and the upgraded empirical paper. |
| RViT+ empirical extension | `RVIT_PLUS_DESIGN.md`, RViT+ producer trees, current `RViT_plus_paper_jepa_grid9/`, `reports/upgraded_paper/` | Extension/reproduction line, not a correction of the normative paper. |
| 2026 normative source | `Critique/source/main.pdf` | Separate stationary signal-detection model; no transformer, recurrent memory, or actor–critic network. |
| Normative audit/repair | `Critique/`, `Rebuild/manuscript/`, `Reconstruction/manuscript/` | Critique audits; Rebuild is deepest technical repair record; Reconstruction is current corrected normative manuscript. None corrects the 2025 empirical paper. |
| PRISM/PrismV2/HRA | `Prism/`, `PrismV2/`, `HRA/`, historical wiki threads | Architecture and failure-history lineage; informative but not identical to the current executable empirical line. |

For the dated evidence map and current scientific caveats, use [`../reports/research_state/2026-07-11_research_state_briefing.md`](../reports/research_state/2026-07-11_research_state_briefing.md). For implementation state and safety invariants, use [`../reports/research_state/2026-07-11_implementation_log.md`](../reports/research_state/2026-07-11_implementation_log.md).

## Authority and navigation order

1. Resolve which lineage owns the question.
2. Read the canonical source/manuscript, producer code, and primary artifacts.
3. Resolve run identity through [`registry/`](registry/README.md); do not infer it from a convenient path name alone.
4. Use dated research-state reports for cross-tree synthesis and known contradictions.
5. Apply `_conventions/` and [`SCHEMA.md`](SCHEMA.md) before a wiki write.
6. Start at [`mocs/attention_program.md`](mocs/attention_program.md), then follow the verified project MOC for Recurrent ViT, RViT+, PRISM v1/v2, or normative repair.
7. Use the generated graph only for discovery, then verify load-bearing claims against the owning evidence.

## Live layout and compatibility state

The live layers are `papers/`, `concepts/`, `threads/`, `mocs/`, `notes/`, `briefs/`, `_conventions/`, `registry/`, `graph/`, `tools/`, and `tests/`; `conversations/` remains reserved but absent at the 2026-07-11 verification. The six current MOCs are [`attention_program`](mocs/attention_program.md), [`recurrent_vit`](mocs/recurrent_vit.md), [`rvit_plus`](mocs/rvit_plus.md), [`prism_v1`](mocs/prism_v1.md), [`prism_v2`](mocs/prism_v2.md), and [`vda_normative_repair`](mocs/vda_normative_repair.md).

The 265 paper cards retain the legacy paper status/depth contract. Pre-existing concept and thread pages that match the untouched historical frontmatter signatures are explicitly grandfathered. Newly wiki-native pages—including new concepts and threads—must use current lifecycle status and the other current base fields, plus structured `see_also` when relationships are added. [`SCHEMA.md`](SCHEMA.md) describes the exact boundary. Do not bulk-migrate legacy frontmatter unless validator, graph consumer, tests, and content are all in an explicitly assigned scope.

## Verified operator baseline (2026-07-11)

The following came from live tool output:

| Check | Result |
|---|---|
| Expanded wiki audit | 0 issues; 265 papers; 16 concepts; 6 threads; 6 MOCs; 5 notes; 1 brief; 261 full, 4 abstract |
| Dual-schema compatibility | Legacy paper/concept/thread pages grandfathered; newly wiki-native pages require current base fields |
| Rebuilt graph artifacts | 388 nodes and 3,859 edges in JSON, GraphML, and Markdown summary, including 89 referenced taxonomy-concept nodes |
| Registry normal audit | 44 records; 0 errors; 217 warnings |
| Registry strict-active audit | 0 errors; historical unknown-provenance warnings remain |
| Tool tests | 58 passed |
| Workspace Git check | not a Git repository |

Counts drift. Re-run checks before quoting them.

## Standard workflow

Run every command from `/Users/jonathanmorgan/AttentionManuscript`.

### A. Documentation or wiki-source edit

1. Read the target and its governing convention.
2. Verify lineage and primary evidence.
3. Preserve IDs, source fields, caveats, and existing legacy fields.
4. Make only path-scoped edits.
5. Validate the legacy paper cards and all supported wiki page directories:

```bash
.venv/bin/python research_db/tools/audit.py
```

6. If pages in any supported graph-source directory changed and graph outputs are in scope, rebuild the derived graph. Supported directories are `papers/`, `concepts/`, `threads/`, `briefs/`, `notes/`, `mocs/`, `conversations/`, `sops/`, `people/`, `preferences/`, and `_adr/` when present:

```bash
.venv/bin/python research_db/tools/build_graph.py
```

The build rewrites all three files under `research_db/graph/`. The expanded builder includes supported MOCs, notes, briefs, conversations, and typed `see_also` relationships. Registry records are deliberately separate.

### B. Registry maintenance

Read [`registry/README.md`](registry/README.md) and [`_conventions/ARTIFACT_REGISTRY.md`](_conventions/ARTIFACT_REGISTRY.md), then run:

```bash
# Focused tests before generated-state replacement.
.venv/bin/python -m pytest research_db/tests -q

# Deterministic staged rebuild from approved metrics roots.
.venv/bin/python research_db/tools/build_run_registry.py

# Required audits after rebuild.
.venv/bin/python research_db/tools/audit_runs.py
.venv/bin/python research_db/tools/audit_runs.py --strict-active
```

The current builder intentionally aborts unless discovery matches the approved 44-candidate contract. Do not weaken the guard or edit `artifacts.jsonl`/`projects.json` by hand to force a pass. Checkpoint hashing is optional and expensive; use only when explicitly required:

```bash
.venv/bin/python research_db/tools/build_run_registry.py --hash-checkpoints
```

A normal rebuild preserves existing non-null hashes for exact run/path pairs. `--drop-checkpoint-hashes` explicitly discards them and must not be used casually.

### C. Querying

After a graph build:

```bash
.venv/bin/python research_db/tools/query.py stats
.venv/bin/python research_db/tools/query.py search <terms>
.venv/bin/python research_db/tools/query.py neighbors <slug> --depth 1
```

Treat query output as navigation, not claim verification.

## Preservation and acceptance rules

- **Evidence:** never modify source metrics, checkpoints, logs, NPZ bundles, analysis outputs, or manuscript sources as registry maintenance.
- **Runs:** never resume into a legacy run directory. Create a new identity and record `parent_run_id` when supported by evidence.
- **Provenance:** do not infer command, seed, device, timestamps, completion cause, convergence, or success from the last row or directory name. Keep null/unknown plus caveats.
- **Registry:** canonical run index; generated via the builder; no hand edits.
- **Graph:** derived export; safe to rebuild from supported sources; never cite it as the only evidence for a scientific claim.
- **Bibliography:** preserve every paper ID and every existing ledger row. Add entries to the correct provenance section; do not renumber.
- **Taxonomy:** define a new legacy tag/concept in `TAXONOMY.md` before using it.
- **Findings:** satisfy goal, method, finding, evidence, reproduction, and caveats. A missing-evidence claim remains a clearly marked stub.
- **Lineage:** keep empirical MAH, RViT+, normative source, normative repair, and PRISM/PrismV2/HRA identities separate.
- **Concurrent work:** immediately re-read any file just before patching it. Do not overwrite a parallel worker's new MOC or content page.

## Completion gate

A maintenance batch is complete only when:

1. every modified path was in the assigned writer lane;
2. primary evidence and lineage were checked;
3. no stable IDs or raw artifacts were lost;
4. `tools/audit.py` exits 0 with 0 issues under the dual-schema compatibility policy;
5. registry audits exit 0 if registry state changed;
6. `research_db/tests` pass if tooling or generated registry state changed;
7. generated graph/registry changes are identified as derived, not hand-authored canon;
8. the handoff reports exact modified files, live command results, and any remaining warnings.
