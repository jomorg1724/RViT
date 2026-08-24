---
id: vda_battery_state_and_provenance
type: note
status: stable
created: 2026-07-11
tags:
  - topic/value-directed-attention
  - topic/run-registry
  - topic/reproducibility
source_project: "rvit-plus-paper-jepa-grid9"
source_code: "RViT_plus_paper_jepa_grid9"
summary: "The canonical affine d_mem=128 VDA1/2/4/9 runs each contain one 20,000-row logged phase and final checkpoints; this is phase completion, not convergence. VDA16 is partial/incomplete with an unknown stop reason and near-chance checkpoint-599 task correctness; fixed-checkpoint evaluation batches do not provide training-run replication."
see_also:
  - slug: rvit_plus
    rel: depends-on
    summary: "Supplies the run-level evidence boundary for the current empirical RViT+ program."
  - slug: archived_vda_validity_semantics
    rel: depends-on
    summary: "Explains why displayed validity is not comparable without checkpoint-specific realized-validity semantics."
  - slug: corrected_vda_analysis_status
    rel: informs
    summary: "Separates archived battery findings from corrected analyses that remain unexecuted."
  - slug: fixed_grid_controlled_design_status
    rel: informs
    summary: "The ladder's geometry and training confounds motivate the controlled fixed-grid design."
  - slug: carrasco2011_visual_attention_25y
    rel: grounded-in
    summary: "Provides the sensitivity, criterion, and noise-limited attention framing used to interpret the battery."
---

# Current VDA battery state and provenance

## TL;DR

The completed affine-feedback VDA1/2/4/9 artifacts are four separately trained, single-checkpoint conditions with one 20,000-row logged phase each. They support a qualified cross-checkpoint attention result, not convergence, training replication, or a pure capacity law; VDA16 is partial/incomplete, its stop reason is unknown, and it cannot be treated as a completed endpoint.

## Plain explanation

The value-directed-attention (VDA) battery varies the number of active stimuli and asks whether cue value and reliability alter behavior and internal attention. The registry can establish which metrics and checkpoints exist and how far each logged phase ran. It cannot recover unknown seeds, commands, cumulative lifetime updates, or a formal convergence criterion, and it cannot turn repeated evaluation trials from one checkpoint into independently trained model replications.

## Research goal

Establish the current evidential status and exact provenance of the archived VDA1/2/4/9/16 battery before using it in the upgraded empirical manuscript or designing corrected runs.

## Method

The 2026-07-11 audit combined the deterministic run registry (`research_db/registry/artifacts.jsonl`), the metrics inventory (`reports/research_state/2026-07-11_battery_metrics_inventory.csv`), the research-state briefing, the upgraded-paper evidence ledger, and the saved VDA analysis bundles under `RViT_plus_paper_jepa_grid9/vda_sweep/figs/`. The canonical manuscript ladder selects affine feedback, `d_mem=128`, and the `_2x2` VDA2 checkpoint.

## Finding

VDA1, VDA2 `_2x2`, VDA4, and VDA9 each have a logged phase ending at iteration 19,999 with final checkpoints. In the saved cross-checkpoint analysis, low-to-high displayed-validity cued-threshold changes are 0.148°, 0.193°, 0.979°, and 2.207° respectively. Other signatures do not form the same monotone ladder: clamp-induced sensitivity ranges are 1.982, 1.647, 1.131, and 0.367, while criterion ranges are 1.020, 1.381, 1.622, and 1.048. VDA16 has four partial registered runs ending at logged iterations 622, 682, 686, and 690; the audited newest checkpoints are at iteration 599 and remain near chance.

## Evidence

Canonical affine `d_mem=128` run identities and metrics:

- VDA1: `run-battery-sweep-results--pod2--ckpt2--vda1-affine-ew-d128`; `battery_sweep_results/pod2/ckpt2/vda1_affine_ew_d128/metrics.csv`
- VDA2 matched-grid: `run-battery-sweep-results--pod2--ckpt2--vda2-affine-ew-d128-2x2`; `battery_sweep_results/pod2/ckpt2/vda2_affine_ew_d128_2x2/metrics.csv`
- VDA4: `run-battery-sweep-results--pod2--ckpt2--vda4-affine-ew-d128`; `battery_sweep_results/pod2/ckpt2/vda4_affine_ew_d128/metrics.csv`
- VDA9: `run-battery-sweep-results--pod2--ckpt2--vda9-affine-ew-d128`; `battery_sweep_results/pod2/ckpt2/vda9_affine_ew_d128/metrics.csv`
- Archived derived bundles: `RViT_plus_paper_jepa_grid9/vda_sweep/figs/psych.npz`, `RViT_plus_paper_jepa_grid9/vda_sweep/figs/sdt.npz`, `RViT_plus_paper_jepa_grid9/vda_sweep/figs/decode.npz`, and `RViT_plus_paper_jepa_grid9/vda_sweep/figs/attn.npz`
- VDA16 partial metrics: `battery_sweep_results/pod2/ckpt2/vda16_affine_ew_d128/metrics.csv`, `battery_sweep_results/pod2/ckpt2/vda16_affine_ew_d256/metrics.csv`, `battery_sweep_results/pod2/ckpt2/vda16_crossattn1_d128/metrics.csv`, and `battery_sweep_results/pod2/ckpt2/vda16_crossattn1_d256/metrics.csv`

## Reproduction

Rebuild and audit run identity from `research_db/` using the commands documented in `research_db/registry/README.md`:

```bash
../.venv/bin/python tools/build_run_registry.py
../.venv/bin/python tools/audit_runs.py
../.venv/bin/python tools/audit_runs.py --strict-active
```

These commands reproduce the registry, not the behavioral numbers in the archived NPZ bundles. The exact original command, seed, and saved trial-level data for those bundles are not preserved in the reviewed evidence, so a numerical rerun must be versioned as a new corrected artifact rather than represented as byte-for-byte reproduction.

## Caveats

- “20,000-row logged phase” does not mean converged, successful, or 20,000 cumulative lifetime updates; resume counters can reset and metrics can be overwritten.
- Each condition contributes one checkpoint. Fixed-checkpoint batches estimate within-model evaluation variation, not between-training-run uncertainty.
- Seeds and original launch commands are `null` in the registry. Single-seed/incomplete evidence remains provisional for scaling claims.
- VDA1/2/4/9 differ in validity semantics; VDA9 also changes grid, token count, readout dimensions, image size, and training support.
- Cross-attention high-token clamp fields are frozen as invalid. The manuscript's current causal figures are affine-only.
- VDA16 is partial/incomplete and its stop reason is unknown; the preserved state establishes only that task correctness remained near chance at checkpoint 599.

## Citations

- [[archived_vda_validity_semantics]] — checkpoint-specific realized-validity rules.
- [[fixed_grid_controlled_design_status]] — prospective design that removes major ladder confounds.
- [[carrasco2011_visual_attention_25y]] — mechanism and noise-limited attention framing.
- [[posner1980_orienting]] — cue-validity paradigm.
