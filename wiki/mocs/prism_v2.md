---
id: prism_v2
type: moc
status: draft
created: 2026-07-11
tags:
  - topic/predictive-coding
  - topic/attention
  - topic/working-memory
  - mechanism/recurrence
scope: "PRISM v2 hierarchical predictive-coding proposal"
summary: "PRISM_V2_PROPOSAL.md is a pre-implementation design for hierarchical predictive coding with fast/slow memory and multi-head saliency. PrismV2/ contains historical implementation attempts, but no validated successful result supports the proposal's predicted scale-up effects."
see_also:
  - slug: attention_program
    rel: informs
    summary: "Locates PRISM v2 as an architectural proposal within the broader attention program."
  - slug: prism_v1
    rel: extends
    summary: "Adds a second perceptual level, dual-timescale memory, and multi-head saliency to v1."
  - slug: hierarchical_predictive_coding
    rel: applies
    summary: "Uses cross-level descending predictions and ascending errors as its organizing mechanism."
  - slug: slow_fast_recurrence
    rel: applies
    summary: "Supplies the dual-timescale recurrent-memory design principle."
  - slug: multi_compartmental_memory
    rel: informs
    summary: "Connects the proposed fast/slow states to the program's broader memory hierarchy."
  - slug: assran2023_ijepa
    rel: informs
    summary: "Provides later latent-prediction context shared with adjacent architecture work, not direct validation of PRISM v2."
---

# PRISM v2

## TL;DR

`PRISM_V2_PROPOSAL.md` is a pre-implementation proposal, whereas `PrismV2/` contains historical implementation attempts. Those attempts did not yield a validated successful result and do not establish the proposal's predicted empirical advantages.

## Plain explanation

The proposal scales PRISM v1 along four axes: a second visual level, separate fast and slow recurrent states, multiple saliency channels, and deeper inner inference. The design is intended to test whether a richer hierarchy better separates cue maintenance, sensory monitoring, and decision evidence. The proposal itself labels the architecture “pre-implementation,” so its numerical parameter budgets and predicted effects are design commitments. The separate `PrismV2/` tree records historical implementation attempts and a reported failure to match v1, not a validated realization of the proposal's predicted benefits.

## Canonical artifacts

- Proposal: `Prism/docs/PRISM_V2_PROPOSAL.md`
- v1 companion: `Prism/docs/THESIS.md`
- Historical implementation tree: `PrismV2/`
- Program context: `research_db/threads/the_user_architectural_program.md`

## Reading order

1. [[prism_v1]] for the simpler predecessor.
2. `Prism/docs/PRISM_V2_PROPOSAL.md` for the proposed architecture and staged roadmap.
3. [[hierarchical_predictive_coding]], [[slow_fast_recurrence]], and [[multi_compartmental_memory]] for mechanism definitions.

## Evidence boundary

The audited briefing reports that PRISM v2 introduced hierarchical predictive coding and slow/fast memory but did not match v1. That historical comparison does not validate the proposal's predicted differential effects, and the proposal should not be treated as the source of RViT+ or normative VDA findings.
