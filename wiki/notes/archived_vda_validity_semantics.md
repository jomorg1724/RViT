---
id: archived_vda_validity_semantics
type: note
status: stable
created: 2026-07-11
tags:
  - topic/value-directed-attention
  - topic/task-semantics
  - topic/reproducibility
source_project: "rvit-plus-paper-jepa-grid9"
source_code: "RViT_plus_paper_jepa_grid9/envs"
summary: "Archived VDA checkpoints do not share one realized cue-validity rule: VDA1 is degenerate, VDA2 is exact, VDA4 and Validity4 realize p+(1-p)/4, and VDA9 realizes p+(1-p)/9. The 2026-07-11 exact-validity repair is prospective and must not be assigned retroactively."
see_also:
  - slug: rvit_plus
    rel: depends-on
    summary: "Constrains empirical comparisons across the archived RViT+ VDA and Validity4 checkpoints."
  - slug: vda_battery_state_and_provenance
    rel: refines
    summary: "Narrows the cross-checkpoint battery interpretation by reconstructing realized rather than displayed validity."
  - slug: corrected_vda_analysis_status
    rel: predecessor
    summary: "Archived semantics are the historical baseline that future corrected analyses must keep separate."
  - slug: fixed_grid_controlled_design_status
    rel: informs
    summary: "The semantic mismatch motivates exact-validity sampling in the controlled fixed-grid family."
  - slug: posner1980_orienting
    rel: grounded-in
    summary: "Defines cue validity as a target-location probability, making displayed-versus-realized differences consequential."
---

# Archived VDA validity semantics

## TL;DR

Archived checkpoints encode several different mappings from displayed cue validity to the probability that a change actually occurs at the cue. VDA1 is necessarily degenerate, VDA2 is exact, VDA4 and Validity4 realize `p + (1-p)/4`, and VDA9 realizes `p + (1-p)/9`; future exact-validity code does not rewrite that history.

## Plain explanation

A displayed validity value `p` is meant to state how often the cue predicts the changed item. In a legacy generator, however, the “invalid” branch sampled uniformly from all locations and could accidentally choose the cue again. That makes realized validity higher than displayed validity. The amount of inflation depends on the number of locations, so comparing checkpoints without reconstructing their generator changes the meaning of the manipulation.

## Research goal

Recover the checkpoint-specific validity rules needed to interpret archived VDA and Validity4 artifacts without assigning corrected 2026-07-11 semantics to older runs.

## Method

The manuscript compliance audit traced each archived checkpoint family to its historical task generator and reconciled that lineage in `reports/upgraded_paper/EVIDENCE_LEDGER.md` and the corrected manuscript Methods. Current exact-validity code and tests were treated only as evidence about future behavior, not as evidence about archived checkpoints.

## Finding

The historical rules are:

- **VDA1:** degenerate singleton. Every realized change is at the only active, cued item; an invalid target does not exist.
- **VDA2:** `VDASetSizeEnv` excludes the cue on invalid trials and realizes displayed `p` exactly.
- **VDA4 and Validity4:** the legacy four-location rule realizes `p + (1-p)/4`.
- **VDA9:** the legacy nine-location rule realizes `p + (1-p)/9`.

Therefore VDA4 and Validity4 share target semantics, so target semantics do not confound that pair. They remain separately trained checkpoints and differ by the value-cue manipulation. Across VDA1/2/4/9, validity semantics remain a comparison confound.

## Evidence

- Reconciled semantics notice: `reports/upgraded_paper/EVIDENCE_LEDGER.md`
- Current manuscript Methods: `reports/upgraded_paper/manuscript/sections/methods.tex`
- Archived VDA4/Validity4 analysis artifacts: `RViT_plus_paper_jepa_grid9/vda_sweep/figs/psych.npz`, `RViT_plus_paper_jepa_grid9/vda_sweep/figs/validity4.npz`
- Archived VDA9 analysis artifact: `RViT_plus_paper_jepa_grid9/vda_sweep/figs/decode.npz`
- Prospective exact-validity implementation: `RViT_plus_paper_jepa_grid9/envs/tasks.py`
- Prospective semantic tests: `RViT_plus_paper_jepa_grid9/tests/test_fixed_grid_setsize.py`

For example, displayed `p=0.25` in the four-location legacy rule realizes `0.4375`, while the nine-location rule realizes `0.25 + 0.75/9`.

## Reproduction

For historical claims, reproduce the lineage audit by reading the checkpoint-family mapping in `reports/upgraded_paper/EVIDENCE_LEDGER.md` beside the archived artifact paths and the manuscript Methods. Do not rerun archived checkpoints with the current `RViT_plus_paper_jepa_grid9/envs/tasks.py` and call the output equivalent: that code now contains prospective exact-validity behavior.

A true numerical reconstruction of archived realized validity requires the historical generator bytes and checkpoint-to-generator mapping. Where those bytes are not preserved independently, the reconciled evidence ledger is the authority and the limitation must remain explicit.

## Caveats

- These formulas describe archived task semantics, not the model's learned subjective belief about validity.
- VDA1 cannot support an invalid-cue comparison because no alternative active target exists.
- Equal displayed proportions do not imply equal realized validity across archived set sizes.
- Validity semantics are only one confound; geometry, tokens, readout dimensions, training support, and separate training also differ.
- Corrected exact-validity applies only to future runs and corrected versioned analyses. No completed corrected derived artifact currently exists.

## Citations

- [[vda_battery_state_and_provenance]] — run identities and phase status.
- [[fixed_grid_controlled_design_status]] — prospective exact-validity controlled design.
- [[posner1980_orienting]] — behavioral definition of cue validity.
