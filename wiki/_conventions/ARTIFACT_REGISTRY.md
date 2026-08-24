---
type: meta
status: stable
created: 2026-07-11
tags:
  - meta/conventions
  - meta/reproducibility
  - topic/run-registry
---

# Artifact registry convention

## Purpose

The run registry is the machine-readable provenance ledger for metrics-backed training runs in this workspace. It records what can be established from existing artifacts without executing training code or deserializing model tensors. The canonical files are under [`../registry/`](../registry/).

A registry entry is evidence about an artifact set, not a claim that a model converged, learned the intended behavior, or supports a manuscript finding.

## Discovery boundary

`tools/build_run_registry.py` discovers candidates only from `metrics.csv` files below these roots:

1. `RViT_plus_paper_jepa_conv/battery_sweep_results/`
2. `battery_sweep_results/`

The expected current inventory is 44 candidates: 43 under the central battery root and one under the convolutional project root. Other metrics files in the workspace are outside this registry's approved scope.

Discovery and ordering are deterministic. A `run_id` is derived from the workspace-relative run directory, so moving a run changes its identity. Duplicate IDs are audit errors.

## Read-only evidence policy

The builder may read:

- `metrics.csv` rows, to establish row count, iteration maxima, and counter resets;
- run-directory filenames and approved analysis artifacts;
- text logs, when available, for explicit device evidence;
- producer source trees, as raw bytes, to compute a source-tree SHA-256;
- checkpoint files as raw byte streams **only** when `--hash-checkpoints` is requested.

The builder must never import training modules, invoke training or analysis programs, call `torch.load`, unpickle checkpoints, or otherwise deserialize tensors. It writes only `research_db/registry/projects.json` and `research_db/registry/artifacts.jsonl` (or an explicitly supplied registry directory).

## Manifest semantics

Each JSONL object conforms to `run_manifest.schema.json` and includes:

- identity: `run_id`, `experiment_id`, `task`, `producer_path`;
- source provenance: `source_tree_sha256`, `command`, `config`;
- parsed configuration: `feedback`, `d_mem`, `reward_scale`, `seed`, `device`;
- timing and progress: `start_time`, `end_time`, `planned_iterations`, `max_logged_iteration`;
- interpretation: `completion_reason`, `status`, `caveats`;
- artifact references: `metrics_path`, `checkpoint_paths`, `checkpoint_sha256`, `analysis_paths`;
- lineage: `parent_run_id`.

Path-derived values are marked by `config.path_inferred: true`. Unknown values remain explicit as `null`, `"unknown"`, or a caveat; they must not be guessed.

### Completion language

`status: logged_phase_complete` means the metrics artifact contains at least the planned number of valid iteration rows. It does **not** establish convergence or scientific success. Partial logs use `status: partial` and `completion_reason: unknown` unless an artifact directly establishes another controlled completion reason.

Allowed completion reasons are:

- `budget_complete`
- `early_success`
- `interrupted_infrastructure`
- `interrupted_manual`
- `numerical_failure`
- `policy_collapse`
- `unknown`

## Hashes

Source hashes are enabled by default and use a deterministic producer-source allowlist: the root training/model modules named in `PRODUCER_ROOT_SOURCE_FILES`, root launch scripts (`*.sh`), and source/config files under the producer's `config/` and `envs/` packages. Symlinks and paths resolving outside the producer root are rejected. Each included file is hashed separately; the tree digest covers a length-framed sequence of normalized workspace-relative paths and per-file SHA-256 digests. Tests and test caches, analysis/derived/figure outputs, metrics and result trees, checkpoints, logs, PDFs, bytecode, Git/cache directories, and Finder metadata are outside the hash scope. The hash identifies the approved producer source bytes available at registry-build time; it is not a Git commit identifier.

Checkpoint paths are always recorded. Checkpoint hashes may initially be `null` because hashing large checkpoints is costly. To populate them without tensor deserialization, rebuild with:

```bash
cd research_db
../.venv/bin/python tools/build_run_registry.py --hash-checkpoints
```

The implementation streams raw checkpoint bytes through SHA-256 and rejects symlinks or paths outside the run directory. A normal rebuild preserves existing non-null hashes for an exact `(run_id, checkpoint_path)` pair. Use `--hash-checkpoints` to recompute all hashes or `--drop-checkpoint-hashes` to set all values to `null`; these modes are mutually exclusive.

## Validation workflow

From `research_db/`:

```bash
# Deterministically rebuild; abort unless exactly 44 candidates are present.
../.venv/bin/python tools/build_run_registry.py

# Validate schema, duplicate IDs, artifact paths, and provenance.
../.venv/bin/python tools/audit_runs.py

# Apply stronger provenance rules to any status=active records.
../.venv/bin/python tools/audit_runs.py --strict-active
```

Both audit modes emit JSON with record, error, and warning counts. Any schema violation, duplicate ID, unsafe/missing path, or strict-active provenance failure is an error. Unknown provenance for non-active historical runs is a warning.

The builder validates staged records before replacing canonical files. Each replacement is atomic on the registry filesystem, and rollback restores both prior files if either replacement fails.

## Change control

- Do not edit `artifacts.jsonl` by hand; change the builder or source artifacts and rebuild.
- Do not rename or relocate metrics/checkpoint directories as part of registry maintenance.
- Do not infer a completion cause from the last iteration alone.
- Do not replace unknown provenance with a plausible value.
- Run focused registry tests before rebuilding and audit the generated registry afterward.
