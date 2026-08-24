---
id: corrected_vda_analysis_status
type: note
status: stub
created: 2026-07-11
tags:
  - topic/value-directed-attention
  - topic/decoding
  - topic/reproducibility
source_project: "rvit-plus-paper-jepa-grid9"
source_code: "RViT_plus_paper_jepa_grid9/vda_sweep/vda_fig_decode.py"
summary: "Corrected deterministic decoding and clamp-analysis safeguards are implemented and tested, but no completed corrected derived artifact exists. Legacy invalid fields remain frozen and must not be cited as repaired results."
see_also:
  - slug: rvit_plus
    rel: informs
    summary: "Records which parts of the current empirical analysis are code-complete versus result-complete."
  - slug: archived_vda_validity_semantics
    rel: depends-on
    summary: "Requires archived semantics to remain historical while corrected sampling is versioned prospectively."
  - slug: vda_battery_state_and_provenance
    rel: refines
    summary: "Prevents frozen VDA2/VDA9 decoder and high-token cross-attention clamp fields from entering battery claims."
  - slug: upgraded_empirical_manuscript_evidence_status
    rel: informs
    summary: "Explains why the manuscript preserves invalid-artifact notices despite code repairs."
---

# Corrected VDA analysis status

## TL;DR

*Unexecuted corrected analysis.* The decoder and analysis safeguards now support deterministic balanced sampling, explicit checkpoint provenance, safe versioned outputs, and corrected high-token indexing, but no completed corrected numerical artifact has been produced. The frozen legacy VDA2/VDA9 change-location and high-token cross-attention clamp fields remain invalid for those claims.

## Plain explanation

Correcting an analysis program does not retroactively correct numbers already saved by an older program. The current code can generate a new, versioned decoding artifact with replay metadata and checkpoint hashes, while refusing to overwrite the legacy file. Until that generation finishes and the output is audited, the project has a tested analysis implementation but no replacement result.

## Research goal

Determine whether the 2026-07-11 correctness repairs have produced an evidence-bearing replacement for the frozen decoder and clamp fields.

## Method

The implementation audit inspected `RViT_plus_paper_jepa_grid9/vda_sweep/vda_fig_decode.py`, `RViT_plus_paper_jepa_grid9/vda_sweep/vda_core.py`, and `RViT_plus_paper_jepa_grid9/tests/test_vda_correctness.py`, then checked the expected versioned output tree. The code's default target is `RViT_plus_paper_jepa_grid9/vda_sweep/derived/2026-07-11_corrected/decode.npz`; that completed artifact is not present in the audited workspace.

## Finding

*Implementation finding, numerical result pending.* Corrected code now balances changed trials across cued and uncued locations for VDA2/4/9, marks VDA1 change-location decoding undefined, records replay configuration and checkpoint SHA-256, uses deterministic private random-number streams, and defaults to a versioned non-legacy output. The test suite also covers runtime clamp indexing and immutable output behavior. No corrected decoder values or corrected cross-attention high-token clamp curves may be claimed yet.

## Evidence

- Corrected decoder implementation: `RViT_plus_paper_jepa_grid9/vda_sweep/vda_fig_decode.py`
- Corrected analysis core: `RViT_plus_paper_jepa_grid9/vda_sweep/vda_core.py`
- Correctness tests: `RViT_plus_paper_jepa_grid9/tests/test_vda_correctness.py`
- Implementation audit: `reports/research_state/2026-07-11_implementation_log.md`
- Frozen-artifact notice: `reports/upgraded_paper/EVIDENCE_LEDGER.md`
- Preserved legacy artifact: `RViT_plus_paper_jepa_grid9/vda_sweep/figs/decode.npz`
- Expected but absent completed replacement: `RViT_plus_paper_jepa_grid9/vda_sweep/derived/2026-07-11_corrected/decode.npz`

The implementation log reports 87 VDA correctness tests passing and records the preserved legacy decoder SHA-256 as `1d8c7fe221d7b67d12dfc7dca05126550228a4825cfaf5d3e0ba6edd696b3a4e`.

## Reproduction

*Not yet completed as a finding artifact.* The corrected script exposes `--out`, `--seed`, `--n`, and explicit overwrite controls, but the reviewed evidence does not archive the exact completed invocation for a corrected run because no such run has completed. A future run must preserve its exact command, selected checkpoints, checkpoint hashes, seed, sample count, replay configuration, software environment, and versioned output path, then audit the output before this note can be promoted.

## Caveats

- Passing tests establish implementation behavior, not scientific results.
- The default corrected path is an intended destination, not evidence that a file exists.
- Legacy fields remain frozen even after code repair; never silently replace their semantics in prose.
- The corrected decoder still evaluates fixed checkpoints. Repeated trials do not estimate between-training-seed uncertainty.
- This page is a `stub` until a versioned corrected artifact and its audit exist.

## Citations

- [[archived_vda_validity_semantics]] — historical semantics that corrected code must not rewrite.
- [[vda_battery_state_and_provenance]] — checkpoints and archived battery boundaries.
- [[upgraded_empirical_manuscript_evidence_status]] — manuscript treatment of frozen invalid fields.
