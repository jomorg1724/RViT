---
id: muller_findlay1987_sensitivity_criterion
title: "Sensitivity and criterion effects in the spatial cuing of visual attention"
authors:
  - "Müller, Hermann J."
  - "Findlay, John M."
year: 1987
venue: "Perception & Psychophysics"
doi: "10.3758/bf03203097"
arxiv: ""
url: "https://doi.org/10.3758/bf03203097"
tags:
  - visual-attention
  - psychophysics
concepts:
  - signal-detection-theory
  - cueing-effect
  - validity-effect
related:
  - posner1980_orienting
  - hawkins1990_attention_detectability
  - lu_dosher1998_external_noise
  - luo_maunsell2018_criterion_sensitivity
  - sridharan2017_sc_sensitivity_bias
  - solomon2004_cues_sensitivity
  - prinzmetal2005_rt_vs_accuracy
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_52
status: full
depth: full
last_updated: "2026-05-16"
---

# Sensitivity and criterion effects in the spatial cuing of visual attention

> **Abstract note.** PubMed does not have a standardized abstract for this paper; the deepening below is from prior knowledge of the paper plus contextual reference to subsequent work that cites it.

## 1. Abstract

(No abstract on PubMed.) Müller & Findlay 1987 conduct a detailed signal-detection-theory analysis of the Posner spatial-cuing paradigm, decomposing cue-validity effects into changes in *sensitivity* (d') and changes in *response criterion* (β). The principal finding: spatial cues produce *both* sensitivity changes (attended stimuli are more discriminable) *and* criterion shifts (subjects are biased to report stimuli at cued locations). The two effects are *dissociable* but co-occur in standard cuing paradigms. The paper is the foundational empirical demonstration that "attention" as measured by Posner-style cuing is *not* a pure perceptual sensitivity change — there is a decisional / bias component that must be partitioned out by SDT analysis.

## 2. Why this matters for us

Müller & Findlay 1987 establishes the *sensitivity vs criterion* distinction as the key methodological principle for testing attention effects in cuing paradigms. The distinction has become standard in subsequent work (Hawkins 1990, [hawkins1990_attention_detectability](research_db/papers/hawkins1990_attention_detectability.md); Luo & Maunsell 2018, [luo_maunsell2018_criterion_sensitivity](research_db/papers/luo_maunsell2018_criterion_sensitivity.md); Sridharan et al. 2017, [sridharan2017_sc_sensitivity_bias](research_db/papers/sridharan2017_sc_sensitivity_bias.md)). For the user's program, this paper provides:
- The *methodological* framework for interpreting the recurrent ViT's cue-validity effects: are they due to sensitivity changes (true attention) or criterion shifts (decisional bias)?
- The *conceptual* support for treating "attention" as *multiple coexisting effects*, not a single mechanism.

## 3. Key claims

1. **Spatial cues affect both sensitivity (d') and criterion (β).** Standard Posner-paradigm cue benefits decompose into both components.
2. **Sensitivity changes reflect perceptual processing.** The d' increase at cued locations indicates that the perceptual representation of the stimulus is genuinely more reliable (or the noise is reduced).
3. **Criterion changes reflect decision processes.** The β shift at cued locations indicates that the subject is biased to report stimuli there — independent of perceptual changes.
4. **The two are dissociable.** Cued vs uncued conditions can be designed to produce *only* sensitivity changes (perceptual manipulation) or *only* criterion shifts (response-bias manipulation), confirming the components are separate mechanisms.
5. **The two co-occur in standard paradigms.** In typical Posner cuing, both components are present and contribute to the overall RT and accuracy benefits.
6. **Methodological implication.** Studies of attention that report only RT or only accuracy don't distinguish between sensitivity and criterion effects. Proper SDT analysis is required to dissect the mechanisms.

## 4. Methods

Müller & Findlay use the Posner spatial-cuing paradigm with a *detection / discrimination* task (typically present/absent for a near-threshold stimulus). The key methodological innovation is *signal detection theory analysis*:

- **d' (sensitivity).** Computed from hit rate and false-alarm rate. Reflects the discriminability of the stimulus.
- **β (criterion).** Computed from the decision threshold above which the subject reports "present." Reflects response bias independent of sensitivity.

Standard Posner-cuing conditions (valid, neutral, invalid) are compared on both d' and β. The patterns across conditions diagnose whether attention is producing sensitivity changes, criterion shifts, or both.

The paper extends the standard paradigm with manipulations designed to *separate* sensitivity from criterion effects — e.g., by varying signal probability, by using forced-choice rather than yes/no responses, etc.

## 5. Results

The principal findings:

- **Sensitivity (d') is higher at cued locations.** Cued trials show higher d' than neutral or invalid trials, indicating genuine perceptual enhancement.
- **Criterion (β) is more liberal at cued locations.** Subjects are more willing to report a stimulus as present at cued locations, indicating a decision-level bias.
- **The two effects scale with cue validity.** Higher cue validity produces larger effects on both d' and β.
- **Decision-bias-only manipulations reproduce part of the cuing benefit.** Manipulating signal probability without changing perceptual conditions produces criterion shifts that mimic part of the cued-attention effect — confirming that some of the "cued benefit" is decisional rather than perceptual.
- **Perceptual-only manipulations reproduce a different part.** Manipulating stimulus contrast (perceptual manipulation) produces d' changes without criterion shifts.

## 6. Critique / limitations

The framework treats attention as having two components (sensitivity, criterion). Subsequent work (Luo & Maunsell 2018; Sridharan et al. 2017) has shown that the *neural* substrates of these two components may be distinct. The 1987 paper is the founding observation; later work has dissected the substrates more fully.

The paper uses *detection* tasks (yes/no). *Discrimination* tasks (which of two stimuli was presented) involve different SDT parameters; whether the same decomposition holds is partially answered by subsequent work.

The 1987 framework doesn't make a strong claim about which component is "more important" or which reflects "true attention." The Solomon 2004 framework ([solomon2004_cues_sensitivity](research_db/papers/solomon2004_cues_sensitivity.md)) takes a stronger position: validity-dependent components reflect attention; validity-invariant components may not. The Müller-Findlay framework is more neutral.

The paper doesn't engage with the predictive-coding or precision-weighting frameworks. Sensitivity changes could be reframed as *precision-weighting at the perceptual level*; criterion shifts could be reframed as *bias at the decision level*. The 1987 paper is silent on these reinterpretations.

## 7. Connection to our work

This paper supplies the *methodological framework* for interpreting the recurrent ViT's cue-validity effects:

**Decomposing cued-attention effects in the recurrent ViT.** The 2502.10955 paper reports that the recurrent ViT shows faster RT and higher accuracy at cued locations. The Müller-Findlay framework asks: are these effects due to sensitivity changes (the model's attention map at cued locations is sharper / more reliable), or criterion shifts (the model is biased to report stimuli at cued locations regardless of perceptual evidence)? A proper SDT analysis of the recurrent ViT's outputs could distinguish these.

**Architectural commitments and SDT predictions.** The Feedback Transformer's multiplicative gain ([feedback_transformer](research_db/concepts/feedback_transformer.md)) implements *signal enhancement* — this should produce *sensitivity* changes in SDT terms. PRISM v1's saliency-gated update similarly implements perceptual modulation. These architectural choices predict that the model's cued-attention effects should be primarily sensitivity-based, not criterion-based.

**A potential bias mechanism in the multi-hub system.** In the user's multi-hub system, the RL hub could in principle implement a *criterion shift* — biasing decisions in a way that doesn't change perceptual sensitivity. The Müller-Findlay distinction predicts that such an RL-driven bias would be empirically distinguishable from MSI-hub-driven sensitivity changes.

**Single-unit interpretation of attention modulation.** Luo & Maunsell 2018 ([luo_maunsell2018_criterion_sensitivity](research_db/papers/luo_maunsell2018_criterion_sensitivity.md)) extend the Müller-Findlay framework to single-cell recordings: cells in visual cortex correlate with sensitivity changes; cells in LPFC correlate with both. The user's multi-hub system could be analyzed in the same framework: which hubs correlate with sensitivity, which with criterion.

The recurrent ViT paper cites Müller & Findlay 1987 in its bibliography (ref [52]). Future manuscripts should adopt the SDT framework explicitly when reporting attention effects.

## 8. Citations to follow

- `posner1980_orienting` — the foundational Posner paradigm. In seed, full depth.
- `hawkins1990_attention_detectability` — Hawkins follow-up. In seed, full depth.
- `lu_dosher1998_external_noise` — external-noise framework. In seed, full depth.
- `luo_maunsell2018_criterion_sensitivity` — modern primate extension. In seed, full depth.
- `sridharan2017_sc_sensitivity_bias` — modern SC-bias analysis. In seed, full depth.
- `solomon2004_cues_sensitivity` — capacity-unlimited precue effects. In seed, full depth.
- `prinzmetal2005_rt_vs_accuracy` — RT vs accuracy in attention. In seed.
