---
id: upgraded_empirical_manuscript_evidence_status
type: note
status: draft
created: 2026-07-11
tags:
  - topic/attention
  - topic/manuscript
  - topic/evidence-audit
source_project: "rvit-plus-paper-jepa-grid9"
source_code: "RViT_plus_paper_jepa_grid9"
summary: "The upgraded empirical manuscript now builds and has an audited affine-feedback evidence ledger, but it is not submission-final. Its supported claims remain checkpoint-specific, archived validity semantics remain historical, and frozen invalid decoder/clamp fields await versioned corrected artifacts."
see_also:
  - slug: rvit_plus
    rel: depends-on
    summary: "Defines the empirical project and producer to which the manuscript belongs."
  - slug: vda_battery_state_and_provenance
    rel: depends-on
    summary: "Supplies run identities and prohibits convergence or replication inflation."
  - slug: archived_vda_validity_semantics
    rel: depends-on
    summary: "Governs displayed-versus-realized validity claims in every archived checkpoint comparison."
  - slug: corrected_vda_analysis_status
    rel: depends-on
    summary: "Keeps frozen invalid fields excluded until corrected versioned derivatives exist."
  - slug: attention_program_lineage_boundaries
    rel: depends-on
    summary: "Prevents the upgraded empirical paper from being mistaken for the normative VDA reconstruction."
  - slug: carrasco2011_visual_attention_25y
    rel: grounded-in
    summary: "Provides the sensitivity, criterion, and external-noise framing used with explicit measurement limits."
---

# Upgraded empirical manuscript evidence status

## TL;DR

The upgraded empirical manuscript is a current, audited affine-feedback draft, not a submission-final paper and not the normative VDA reconstruction. It supports checkpoint-specific sensitivity, criterion, spatial-gating, decoding, and cross-checkpoint results while preserving explicit exclusions for invalid legacy fields, unmeasured rehearsal, and unexecuted corrected analyses.

## Plain explanation

The manuscript upgrades the empirical Recurrent ViT story using the current RViT+ battery. Its evidence ledger ties prose to named checkpoints and derived artifacts, and a 2026-07-11 pass reconciled the most important semantic errors. The remaining limitation is not simply writing quality: most scaling evidence is single-checkpoint, archived task semantics differ, and some promised corrected or controlled experiments do not yet have results.

## Research goal

Determine which claims the current upgraded empirical manuscript can support and which claims must remain historical, provisional, or pending.

## Method

The manuscript audit reconciled `reports/upgraded_paper/EVIDENCE_LEDGER.md` against the producer, registry, archived NPZ bundles, manuscript section files, and the research-state briefing. The implementation log additionally records a clean build and visual QA of `reports/upgraded_paper/manuscript/main.pdf`.

## Finding

The manuscript is now explicitly affine-feedback only and states that all reported checkpoints were optimized by reinforcement learning plus a temporal JEPA auxiliary loss with weight 0.5. Its canonical VDA4 evidence supports directly measured changes in sensitivity and criterion, location-gated attention injection, value decoding, validity decoding with the corrected checkpoint attribution, and event-time change-location decoding. The VDA1/2/4/9 threshold series is reported as a qualified cross-checkpoint association rather than a pure capacity law. Rehearsal, faithful shared-base Luo–Maunsell dissociation, width-as-capacity, corrected VDA2/VDA9 decoding, and fixed-grid scaling remain incomplete.

## Evidence

- Current PDF: `reports/upgraded_paper/manuscript/main.pdf`
- Manuscript source: `reports/upgraded_paper/manuscript/main.tex` and `reports/upgraded_paper/manuscript/sections/`
- Claim ledger and frozen-artifact notice: `reports/upgraded_paper/EVIDENCE_LEDGER.md`
- Current research-state audit: `reports/research_state/2026-07-11_research_state_briefing.md`
- Build/QA status: `reports/research_state/2026-07-11_implementation_log.md`
- Canonical archived analysis bundles: `RViT_plus_paper_jepa_grid9/vda_sweep/figs/psych.npz`, `sdt.npz`, `decode.npz`, `microstim.npz`, `validity4.npz`, `attn.npz`, and `entropy.npz`. `vda_fig_attn.py` produces task/model/color/validity `*_map` arrays and location-reduced `*_alpha` time courses. `vda_fig_entropy.py` produces the `affine_ew` and `crossattn1` condition-by-measure arrays used for decision entropy, spread, and declaration analyses.

The implementation log reports a clean 46-page A4 PDF with no LaTeX warning, undefined-reference, or box-error patterns and completed rendered-page visual QA. The evidence ledger's current boundaries include: canonical VDA4 validity balanced accuracy 0.773 at t1, 0.296 at t2, and mean 0.309 over t2–t6; change presence/location 0.81/0.50 at t5; criterion moving from 1.42 to -0.60 across the canonical clamp sweep; and no fitted cue-location decoder across the delay.

## Reproduction

Reproduce the manuscript evidence audit by tracing each load-bearing statement in `reports/upgraded_paper/EVIDENCE_LEDGER.md` to its named checkpoint/run in `research_db/registry/artifacts.jsonl`, then to the named NPZ field and manuscript section. Use [[archived_vda_validity_semantics]] before comparing validity conditions and [[corrected_vda_analysis_status]] before using any frozen decoder or high-token cross-attention clamp field.

The reviewed sources do not preserve one exact end-to-end manuscript build command in the evidence ledger or implementation log. Build instructions and dependencies should therefore be recovered from the manuscript tree before a future release, and the exact release command plus PDF checksum should be archived with that release.

## Caveats

- The manuscript is current but not submission-final; `status: draft` reflects that lifecycle.
- A clean PDF build validates presentation, not scientific truth.
- Most headline scaling conditions use one trained checkpoint; fixed-checkpoint evaluation batches are not training replications.
- Archived validity semantics remain checkpoint-specific and are not retroactively corrected.
- VDA16 is partial/incomplete with an unknown stop reason; task correctness remained near chance at checkpoint 599, so it is not a completed negative result.
- Frozen VDA2/VDA9 change-location and VDA9 `crossattn1` high-token clamp fields remain invalid for those claims.
- No dedicated external-noise experiment, quantitative three-way Carrasco decomposition, cue-location delay decoder, trained delay-probe result, or causal rehearsal result exists.

## Citations

- [[vda_battery_state_and_provenance]] — run-level battery evidence and VDA16 status.
- [[archived_vda_validity_semantics]] — historical task semantics.
- [[corrected_vda_analysis_status]] — code-complete/result-pending correction boundary.
- [[carrasco2011_visual_attention_25y]] — mechanism framing and external-noise boundary.
- [[assran2023_ijepa]] — latent-prediction background; not evidence that the current auxiliary is identical to I-JEPA training.
