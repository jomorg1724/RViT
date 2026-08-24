---
id: posner1980_orienting
title: "Orienting of attention"
authors:
  - "Posner, Michael I."
  - "Snyder, Charles R."
  - "Davidson, Brian J."
year: 1980
venue: "Quarterly Journal of Experimental Psychology / Journal of Experimental Psychology: General"
doi: ""
arxiv: ""
url: ""
tags:
  - visual-attention
  - posner-cuing
  - psychophysics
  - reaction-time
concepts:
  - attentional-spotlight
  - cueing-effect
  - validity-effect
  - signal-detection-theory
related:
  - itti_koch2001_saliency_review
  - reynolds_heeger2009_normalization
  - desimone_duncan1995_biased_competition
  - carrasco2011_visual_attention_25y
  - bisley_goldberg2010_parietal_priority
  - hawkins1990_attention_detectability
  - lu_dosher1998_external_noise
  - treisman_gelade1980_feature_integration
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_11
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Orienting of attention

## 1. Abstract

The 1980 paper introduces what is now called the Posner cueing paradigm. A central or peripheral cue precedes a target stimulus. The cue probabilistically predicts where the target will appear (valid trials), where it will not (invalid trials), or carries no spatial information (neutral trials). Subjects respond faster and more accurately to validly cued targets than to invalidly cued targets — the "validity effect" — and the magnitude of this effect varies with the cue's validity. Two attentional systems are dissociated: an exogenous, peripheral-cue-driven, fast and stimulus-bound capture; and an endogenous, central-cue-driven, slower and voluntarily controlled orienting. The paper argues that the validity effect is the behavioral signature of covert spatial attention — attention that shifts independently of the eyes.

## 2. Why this matters for us

This is the foundational paradigm both the Recurrent ViT (2502.10955) and PRISM are built around. Every cued change-detection trial in our task is a Posner cue. The validity-effect prediction — that performance and reaction time should improve at cued locations and degrade at uncued locations — is the empirical target our models are evaluated against (`Prism/docs/THESIS.md` §3.2; PROJECT_PLAN P2.2). Without the Posner framework, the term "cue validity" in our 25%/50%/75%/100% conditions is meaningless.

## 3. Key claims

1. Covert spatial attention can be shifted independently of eye position and produces measurable RT and accuracy benefits at attended locations.
2. The benefit of attention at cued locations is matched by a cost at uncued locations, relative to a neutral baseline — the so-called cost–benefit dissociation.
3. There are two distinct attentional systems: exogenous (reflexive, peripheral-cue-driven, time-course peaks ~100ms) and endogenous (voluntary, central-symbol-driven, time-course peaks ~300ms).
4. Cue validity (the conditional probability that the target appears at the cued location) parametrically modulates the cueing effect: higher validity → larger benefit/cost.
5. The cueing effect reflects an internal attentional shift, not a sensory or motor adjustment — established by the delay between cue and target, during which the relevant computation must be internal.

## 4. Methods

Reaction-time paradigm with a centrally fixated subject. On each trial, a cue (arrow, peripheral flash, or neutral marker) is presented, followed by a target at one of two or four possible locations, after a variable cue–target onset asynchrony (typically 50–800 ms). Subjects make a speeded detection or simple discrimination response. The proportion of trials on which the cue correctly predicts the target location (the cue validity) is manipulated between blocks. Eye position is monitored to confirm that effects are covert. The key dependent variables are mean RT and percent correct, stratified by (cue type × validity × SOA).

## 5. Results

The canonical observation, replicated in essentially every cueing experiment since:

- Valid trials: shortest RT, highest accuracy.
- Invalid trials: longest RT, lowest accuracy.
- Neutral trials: intermediate.

The benefit (RT_neutral − RT_valid) and the cost (RT_invalid − RT_neutral) are both significant and approximately additive — i.e., the cue produces both a facilitation at the cued location and a deficit at uncued locations relative to baseline.

The validity effect (RT_invalid − RT_valid) scales with cue validity: a 100% valid cue produces ~50 ms validity effect in humans; a 50% valid cue produces a smaller but nonzero effect; a 25% valid cue (chance baseline given four locations) produces effectively no effect.

The two attentional systems have distinct time courses: exogenous attention peaks around 100 ms after cue onset and decays by ~300 ms; endogenous attention rises more slowly, peaks around 300–500 ms, and is sustained as long as the cue remains relevant.

## 6. Critique / limitations

The original framing posits a unified "attentional spotlight" — a single beam directed at one location at a time. Subsequent work (Carrasco 2011; Reynolds & Heeger 2009) has substantially undermined this metaphor, showing that covert attention is better characterized as a graded multiplicative gain modulation distributed across the visual field, not a winner-take-all gate. This is the conceptual move that motivates PRISM's explicit rejection of softmax-over-locations primitives.

The behavioral effects are robust but small in absolute terms (~30–50 ms in RT, a few percent in accuracy). Whether the underlying mechanism is best characterized as a sensitivity change (improved signal-to-noise at the cued location) or a criterion shift (more willing to respond at the cued location) was not resolved by the original paper; signal-detection-theoretic work since has shown both effects are present (Hawkins et al., 1990; Lu & Dosher, 1998).

The cue–target asynchrony is short enough that the validity effect is plausibly due to either active attention deployment or to lingering sensory traces of the cue itself; this confound is partly addressed in later studies using longer SOAs and central symbolic cues, but is not eliminated.

## 7. Connection to our work

The Recurrent ViT and PRISM both operationalize the Posner paradigm computationally. Specifically:

- The cue at $t = 1$ in our environments is the Posner cue.
- The cue validity proportions (25%/50%/75%/100%) we use are the parametric manipulation of P(target at cued location).
- The validity effect we measure (improved hit rate and shorter RT at cued versus uncued locations) is the direct analog of Posner's RT validity effect.
- Our experimental design exploits the fact that cue–target SOA is long enough (at least 10 steps in PRISM, 4 steps in the Recurrent ViT) that any effect must be due to internal attentional dynamics, not lingering cue traces — exactly the rationale Posner offered.

The validity effect is the headline behavioral signature both our papers report. Specifically: in the Recurrent ViT paper, Figure 3C/F shows the cueing effect at 100% validity (the canonical Posner result). In PRISM, this is the target of `PROJECT_PLAN.md` P2.2 (psychometric validity figure).

A critical distinction we draw is that Posner's spotlight metaphor is *not* the framework we adopt. PRISM specifically argues that the model should not contain a softmax-over-locations primitive (the architectural translation of "spotlight"). Instead, attention emerges as the prediction-error magnitude of the model's own generative model. This is a substantive departure from Posner's original framing, but it preserves the validity-effect prediction — and this is exactly the kind of architectural-versus-behavioral dissociation our work is built to test.

## 8. Citations to follow

- `treisman_gelade1980_feature_integration` — Treisman & Gelade 1980 feature-integration theory, the direct theoretical descendant of the spotlight metaphor. Both papers from the same year.
- `carrasco2011_visual_attention_25y` — the 25-year retrospective; documents how the spotlight metaphor has been progressively undermined and replaced by graded-gain accounts.
- `hawkins1990_attention_detectability` — signal-detection-theoretic deconstruction of the cueing effect.
- `lu_dosher1998_external_noise` — external-noise paradigm that dissociates sensitivity from criterion explanations of the cueing effect.
- `bisley_goldberg2010_parietal_priority` — modern neural substrate of the priority map (LIP) that the Posner cue is presumed to modulate.
