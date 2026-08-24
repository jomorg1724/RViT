---
id: prism_v1
type: moc
status: draft
created: 2026-07-11
tags:
  - topic/predictive-coding
  - topic/attention
  - mechanism/recurrence
scope: "PRISM v1 predictive-coding architecture proposal and historical experiment line"
summary: "PRISM v1 proposes a compact convolutional recurrent model in which prediction error supplies an attention-like signal for cued change detection. Its design manuscript contains pending results, so proposal claims must be separated from historical implementation lessons."
see_also:
  - slug: attention_program
    rel: informs
    summary: "Places PRISM v1 beside, rather than inside, the empirical Recurrent ViT and normative VDA lineages."
  - slug: prism_v2
    rel: predecessor
    summary: "PRISM v1 is the simpler design that the hierarchical slow/fast v2 proposal extends."
  - slug: hierarchical_predictive_coding
    rel: applies
    summary: "PRISM v1 explicitly uses prediction, residual error, and recurrent state updating."
  - slug: posner1980_orienting
    rel: grounded-in
    summary: "Supplies the cued change-detection paradigm targeted by the architecture."
  - slug: the_user_architectural_program
    rel: informs
    summary: "Records the wider architectural program in which PRISM is one specialized instance."
  - slug: rvit_plus_engineering
    rel: informs
    summary: "Preserves later engineering lessons that distinguish PRISM's mechanisms from RViT+ development."
---

# PRISM v1

## TL;DR

PRISM v1 is a predictive-coding architecture proposal with historical implementation evidence, not a submission-complete empirical paper. Its central design replaces a learned spatial pointer with a prediction-error-derived signal, while its draft results section remains explicitly pending.

## Plain explanation

PRISM stands for Predictive Recurrent Inference via Self-Modulation. The v1 design combines a convolutional visual hierarchy, top-down predictions, a recurrent memory state, and reinforcement learning on a Posner-style change-detection task. Because its manuscript labels results as pending, readers should cite the design for architectural commitments and use preserved run artifacts or audited state reports—not proposal prose—for empirical outcomes.

## Canonical artifacts

- Design/manuscript draft: `Prism/docs/THESIS.md`
- Broader program context: `research_db/threads/the_user_architectural_program.md`
- Current audit synthesis of historical outcomes: `reports/research_state/2026-07-11_research_state_briefing.md`

## Reading order

1. `Prism/docs/THESIS.md` for the v1 architecture and intended analyses.
2. [[hierarchical_predictive_coding]] for the mechanism definition and evidential anchors.
3. [[the_user_architectural_program]] for cross-project architectural context.
4. [[prism_v2]] for the distinct hierarchical scale-up proposal.

## Evidence boundary

The audited research-state briefing summarizes PRISM v1 as evidence that prediction-error-driven memory can solve change detection without interpretable softmax attention. That historical assessment does not complete the pending results promised in `Prism/docs/THESIS.md`, and it does not imply that PRISM v2 or RViT+ reproduced every v1 result.
