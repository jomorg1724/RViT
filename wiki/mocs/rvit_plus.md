---
id: rvit_plus
type: moc
status: draft
created: 2026-07-11
tags:
  - topic/attention
  - topic/recurrent-vision
  - topic/value-directed-attention
  - mechanism/recurrence
scope: "RViT+ design, executable empirical producer, battery, and upgraded manuscript"
summary: "RViT+ extends the 2025 empirical Recurrent ViT line and now includes a current executable producer, a registered battery, and an upgraded affine-feedback manuscript. Its strongest current set-size result is cross-checkpoint and single-seed; it is not a convergence or pure-capacity result."
see_also:
  - slug: attention_program
    rel: informs
    summary: "Places RViT+ in the empirical branch of the broader attention program."
  - slug: recurrent_vit
    rel: extends
    summary: "Extends the 2025 empirical baseline with new task batteries, interventions, and manuscript analyses."
  - slug: rvit_plus_engineering
    rel: informs
    summary: "Preserves the historical architecture failures and fixes that preceded the current producer."
  - slug: vda_battery_state_and_provenance
    rel: depends-on
    summary: "Supplies the audited run identities, phase-completion language, and VDA16 interruption status."
  - slug: archived_vda_validity_semantics
    rel: depends-on
    summary: "Constrains every comparison involving displayed versus realized validity in archived checkpoints."
  - slug: corrected_vda_analysis_status
    rel: informs
    summary: "Separates corrected analysis code from corrected numerical artifacts that have not yet been produced."
  - slug: fixed_grid_controlled_design_status
    rel: informs
    summary: "Records the implemented controlled set-size design and the absence of training results."
  - slug: upgraded_empirical_manuscript_evidence_status
    rel: depends-on
    summary: "Audits the current manuscript's supported claims, invalid fields, and submission boundary."
  - slug: assran2023_ijepa
    rel: grounded-in
    summary: "Supplies latent-prediction background for the temporal JEPA auxiliary objective."
---

# RViT+

## TL;DR

RViT+ is the current empirical extension of the 2025 Recurrent ViT line. The present paper-oriented producer and manuscript support a qualified affine-feedback attention battery, but current scaling evidence uses one checkpoint per condition and does not establish convergence, training replication, or a pure set-size law.

## Plain explanation

The name RViT+ covers two layers that should be kept distinct. `RVIT_PLUS_DESIGN.md` is a broad May 2026 architecture proposal shaped by earlier failure analyses. The current paper line, produced under `RViT_plus_paper_jepa_grid9/`, is a smaller executable recurrent detector with `affine_ew` and `crossattn1` routing variants; the upgraded manuscript reports the affine-feedback model rather than an architecture comparison.

The battery includes value-directed attention, validity-only, Baruni, Luo–Maunsell, Krauzlis, motion, width, reward-scale, and memory-noise conditions. The run registry is the authority for artifact identity and logging status; derived NPZ files and the evidence ledger govern numerical manuscript claims.

## Canonical artifacts

- Broad design proposal: `RVIT_PLUS_DESIGN.md`
- Historical engineering record: `research_db/threads/rvit_plus_engineering.md`
- Current producer: `RViT_plus_paper_jepa_grid9/`
- Secondary convolutional/memory-noise producer: `RViT_plus_paper_jepa_conv/`
- Run registry: `research_db/registry/projects.json` and `research_db/registry/artifacts.jsonl`
- Current empirical manuscript: `reports/upgraded_paper/manuscript/main.pdf`
- Claim ledger: `reports/upgraded_paper/EVIDENCE_LEDGER.md`

## Reading order

1. [[attention_program_lineage_boundaries]] for lineage and evidence authority.
2. [[rvit_plus_engineering]] for historical mechanism-discovery lessons.
3. [[vda_battery_state_and_provenance]] and [[archived_vda_validity_semantics]] for current run interpretation.
4. [[upgraded_empirical_manuscript_evidence_status]] for the manuscript claim surface.
5. [[corrected_vda_analysis_status]] and [[fixed_grid_controlled_design_status]] for future corrected work.

## Current claim boundary

The affine `d_mem=128` VDA1/2/4/9 checkpoints each have a 20,000-row logged phase. Their displayed-validity threshold changes form an ordered cross-checkpoint association, while clamp sensitivity, criterion, sustained attention, geometry, training support, and validity semantics do not form one controlled monotone ladder. VDA16 remains partial/incomplete, with an unknown stop reason, and cannot serve as a terminal capacity point.
