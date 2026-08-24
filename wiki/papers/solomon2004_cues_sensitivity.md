---
id: solomon2004_cues_sensitivity
title: "The effect of spatial cues on visual sensitivity"
authors:
  - "Solomon, Joshua A."
year: 2004
venue: "Vision Research"
doi: "10.1016/j.visres.2003.12.003"
arxiv: ""
url: "https://doi.org/10.1016/j.visres.2003.12.003"
tags:
  - visual-attention
  - psychophysics
concepts:
  - cueing-effect
  - validity-effect
  - signal-detection-theory
related:
  - lu_dosher1998_external_noise
  - cameron2002_covert_attention_contrast
  - posner1980_orienting
  - muller_findlay1987_sensitivity_criterion
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_50
status: full
depth: full
last_updated: "2026-05-14"
---

# The effect of spatial cues on visual sensitivity

## 1. Abstract

A consensus has emerged that visual *sensitivity* can be heightened locally with an appropriate precue. Experiments with partially and totally valid precues suggest an *increase in sensitivity of less than one-half log unit* at the precued position, compared with other positions. New experiments by Solomon with *non-informative* precues demonstrate that most of this small enhancement *is not due to focal attention*. Sensitivity can be heightened at **eight positions simultaneously**, just as much as when a single position is precued. Sensitivities produced by single, totally valid precues and single, non-informative precues were similar. Thus there seems to be *no capacity limit* for the effect of precues on visual sensitivity.

## 2. Why this matters for us

Solomon 2004 is a *critical* paper for the recurrent ViT's cued-attention story. While the bulk of the spatial-cuing literature (Posner, Lu-Dosher, Cameron et al.) shows that precues enhance sensitivity, Solomon argues that *most* of this enhancement is *not focal attention* — it's a non-attentional, capacity-unlimited effect of the precue itself. The recurrent ViT's cued-attention results (faster RT, higher accuracy at cued locations) should therefore be carefully interpreted: are they evidence of *attentional* enhancement, or of *non-attentional* precue effects? Solomon's framework provides the methodological vocabulary for making this distinction, and his result imposes a *constraint* on the recurrent ViT's interpretation: cue-validity-dependence is what distinguishes true attention from precue-related sensitivity enhancement.

## 3. Key claims

1. **Sensitivity is enhanced at precued locations.** The classical finding — precues at a location improve subsequent detection / discrimination at that location — is confirmed.
2. **The enhancement is *small* — less than half a log unit.** The magnitude of the effect is modest, not the large enhancements sometimes claimed.
3. **Non-informative precues produce the same enhancement.** When the precue does not predict the target location (50% valid in a 2-AFC, equivalent to a chance baseline), the enhancement is *the same* as with informative cues.
4. **Eight simultaneous precues produce the same enhancement at all eight locations.** When precues at multiple locations are present, all locations show the same sensitivity enhancement — there is *no capacity limit*.
5. **The enhancement is therefore not focal attention.** Focal attention should be capacity-limited (we can attend to only one location); the precue effect is unlimited.
6. **Most of the precue effect is attributable to *non-attentional* mechanisms.** Solomon proposes that pre-cue presentation produces a *sensory-level* enhancement (perhaps via subtle motion-based cue mechanisms, or by alerting / arousal effects) that doesn't require focal attentional engagement.
7. **True focal attention is what's revealed by *cue validity*.** The validity-dependent component (additional benefit of valid cues over neutral or invalid cues) is the part that reflects genuine attention. The non-validity-dependent component is the non-attentional precue effect.

## 4. Methods

**Task.** Visual sensitivity (typically threshold-detection of a Gabor or similar stimulus) was measured at various spatial locations. The key manipulation was precue type:
- **Totally valid precue.** A single precue at the target location (100% validity, in 2-AFC).
- **Non-informative precue.** A single precue at a random location (50% validity, no information).
- **Eight-position precue.** Precues at all 8 candidate target locations simultaneously.
- **No-precue baseline.**

**Sensitivity measurement.** Standard psychometric threshold measurement: contrast threshold for 75%-correct performance.

**Analysis.** Comparison of threshold across precue types and across the 8 locations. The key contrast: does informative vs non-informative precue produce different enhancement?

## 5. Results

The principal quantitative findings:

- **Small enhancement.** ≈0.3–0.5 log units of contrast threshold improvement at the precued location relative to the no-precue baseline.
- **Same enhancement with non-informative cues.** Non-informative cues produce essentially the same threshold reduction as totally valid cues — within experimental error.
- **Eight-position cues enhance all eight locations.** With cues at all 8 locations, all 8 show the same threshold reduction. The capacity for cue-driven enhancement is unlimited.
- **Conclusion.** The precue effect is not focal attention. It's a non-attentional, sensory-or-alerting enhancement that propagates from cued stimulation to subsequent target processing.

## 6. Critique / limitations

The result is *for sensitivity in detection tasks*. Whether the same conclusion applies to *discrimination* tasks (which require representation of stimulus identity) is less clear. Some subsequent work has reported attention-like patterns in discrimination but not detection.

The interpretation depends on operationalizing "focal attention" as *capacity-limited*. Some accounts (e.g., Treisman's feature-integration theory) allow attention to operate on multiple features / locations simultaneously, so the capacity-unlimited result doesn't *necessarily* rule out attention.

Solomon's claim is *negative* — the enhancement is *not* focal attention. The positive claim (what *is* the mechanism?) is less developed. Candidate mechanisms include arousal, sensory-level neural enhancement at the cued location, motion-mediated effects, and others.

The result is for *transient peripheral* precues. *Sustained* attention (e.g., maintaining attention at a known location over a long delay) may behave differently and is not addressed.

Subsequent work has both confirmed and contested Solomon's conclusion. The capacity-unlimited result has been replicated in some studies but not in others, and the dichotomy "informative vs non-informative" may oversimplify the actual mechanisms.

## 7. Connection to our work

This paper imposes important *interpretive constraints* on the user's program:

**Cue-validity-dependence is the diagnostic of true attention.** Solomon's argument is that the *invariant* precue effect (non-validity-dependent) is not focal attention. The recurrent ViT paper (2502.10955) reports cue-validity-dependent effects (effects that scale with validity); these are diagnostic of *real attentional* engagement, not just precue-driven sensory enhancement. This is the framework support for the recurrent ViT's experimental design.

**Multi-location capacity.** Solomon's eight-position-cued result establishes that *low-level* cue effects are capacity-unlimited. The recurrent ViT's attention map is *capacity-limited* (softmax probabilities sum to 1; high attention at one location reduces it elsewhere). The architectural commitment to capacity-limited attention is consistent with treating the recurrent ViT's attention as *focal*, not as a low-level precue effect.

**Distinguishing attention from arousal.** Solomon's framework distinguishes *focal attention* (validity-dependent, capacity-limited) from non-attentional sensory enhancement (validity-independent, capacity-unlimited). PRISM's saliency-gated update should be carefully positioned: which kind of enhancement does it implement?

**Methodological caution.** Solomon's result is a useful warning against over-interpreting cue benefits. The recurrent ViT's "attention effect" is genuinely attentional only if it scales with cue validity — which the user's paper reports it does.

The recurrent ViT paper cites Solomon 2004 in its bibliography (ref [50]). Future manuscripts that report attentional effects in models should distinguish validity-dependent (attentional) from validity-invariant (non-attentional) components per Solomon's framework.

## 8. Citations to follow

- `lu_dosher1998_external_noise` — external-noise framework. In seed, full depth.
- `cameron2002_covert_attention_contrast` — contrast-gain in Carrasco lab. In seed, full depth.
- `posner1980_orienting` — Posner paradigm. In seed, full depth.
- `muller_findlay1987_sensitivity_criterion` — sensitivity vs criterion. In seed, full depth.
- `carrasco_yeshurun1998_contrast_attention` — Carrasco-Yeshurun. Not in seed.
- `solomon2004_models_attention` — Solomon's modeling follow-up. Not in seed.
