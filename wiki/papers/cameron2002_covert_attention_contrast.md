---
id: cameron2002_covert_attention_contrast
title: "Covert attention affects the psychometric function of contrast sensitivity"
authors:
  - "Cameron, E. Leslie"
  - "Tai, Joanna C."
  - "Carrasco, Marisa"
year: 2002
venue: "Vision Research"
doi: "10.1016/s0042-6989(02)00039-1"
arxiv: ""
url: "https://doi.org/10.1016/s0042-6989(02)00039-1"
tags:
  - visual-attention
  - psychophysics
concepts:
  - psychometric-function
  - gain-modulation
  - cueing-effect
related:
  - lu_dosher1998_external_noise
  - solomon2004_cues_sensitivity
  - posner1980_orienting
  - reynolds_heeger2009_normalization
  - feldman_friston2010_attention_free_energy
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_51
status: full
depth: full
last_updated: "2026-05-14"
---

# Covert attention affects the psychometric function of contrast sensitivity

## 1. Abstract

Cameron, Tai & Carrasco examine the effect of *transient covert attention* on the psychometric function for contrast sensitivity in an orientation-discrimination task when the target is presented *alone* — without distractors and without visual masks. Transient covert attention *decreases the threshold* (consistent with a *contrast gain* mechanism) and, less consistently, also *decreases the slope* of the psychometric function. The authors assessed performance at 8 equidistant locations (4.5° eccentricity) and found that threshold and slope depended on target location — both were higher on the vertical meridian than the horizontal meridian, particularly directly above fixation. All effects were robust across a range of spatial frequencies, and the visual-field asymmetries increased with spatial frequency. Despite the dependence of the psychometric function on target location, *attention improved performance to a similar extent across the visual field*. Because the experiment excluded all sources of external noise and the authors experimentally ruled out spatial uncertainty as an explanation, they conclude that the observed attentional benefit is *consistent with signal enhancement*.

## 2. Why this matters for us

Cameron, Tai & Carrasco 2002 is the foundational *contrast-gain* paper for covert attention. The result that covert attention *shifts* the contrast psychometric function (rather than *scaling* it) identifies the mechanism as *contrast gain* — multiplicative gain on the input signal — rather than *response gain*. For the user's program, this paper supplies the architectural support for the recurrent ViT's *multiplicative* attention modulation: real attention is contrast gain, exactly what the Feedback Transformer's Hadamard-product structure implements.

## 3. Key claims

1. **Transient covert attention shifts the contrast psychometric function.** The function (proportion-correct as a function of contrast) shifts leftward with attention — lower contrast is needed to reach the same accuracy.
2. **The shift is *contrast gain*, not response gain.** Contrast gain shifts the whole function leftward; response gain would scale the function vertically. Cameron et al. find a leftward shift, consistent with contrast gain.
3. **The slope decreases slightly (less consistent finding).** In addition to the threshold shift, the slope of the function sometimes decreases — but this effect is less robust than the threshold shift.
4. **The threshold and slope depend on visual-field location.** Vertical meridian (especially above fixation) gives higher thresholds and steeper slopes than horizontal meridian. The lower visual field shows the smallest thresholds.
5. **Attention's effect is uniform across the visual field.** Despite the location-dependence of the *baseline* psychometric function, attention's *benefit* is approximately constant across locations.
6. **Signal enhancement is the underlying mechanism.** Since external noise is excluded and spatial uncertainty is ruled out, the attentional benefit must be due to signal enhancement (multiplicative gain on the input signal). This is consistent with Lu & Dosher 1998 ([lu_dosher1998_external_noise](research_db/papers/lu_dosher1998_external_noise.md)).
7. **The contrast-gain finding constrains computational models.** Reynolds & Heeger 2009 normalization model of attention ([reynolds_heeger2009_normalization](research_db/papers/reynolds_heeger2009_normalization.md)) accounts for the contrast-gain pattern; other models must too.

## 4. Methods

**Task.** Orientation-discrimination (clockwise vs counterclockwise tilt) of a Gabor patch presented at one of eight locations around fixation (4.5° eccentricity). The target was presented alone — no distractors, no mask, no external noise.

**Attention manipulation.** A *transient peripheral cue* appeared just before the target. On valid trials, the cue marked the target's location; on neutral trials, the cue was non-spatial. The cue-stimulus onset asynchrony (CSOA) was short enough to capture *transient* (exogenous) attention.

**Contrast manipulation.** Eight contrast levels per location were tested to estimate the full psychometric function — proportion-correct as a function of stimulus contrast.

**Analysis.** Psychometric functions (Weibull) were fit separately for cued and neutral conditions. Threshold (75%-correct contrast) and slope parameters were extracted. The fit parameters were compared across cued/neutral and across the 8 locations.

## 5. Results

The principal quantitative findings:

- **Threshold shift.** Cued thresholds were significantly lower than neutral thresholds. The magnitude of the shift was ≈10–20% in contrast — a robust effect across subjects.
- **Slope effect.** A small decrease in psychometric-function slope was observed with attention, but this effect was less consistent across subjects.
- **Visual-field asymmetry.** Thresholds on the vertical meridian (especially upper) were higher than on the horizontal meridian; this asymmetry increased with spatial frequency.
- **Uniform attention benefit.** The attentional benefit was approximately constant across the 8 locations — the *baseline* differences in performance didn't change the *relative* benefit of attention.
- **External-noise control.** No external noise was added; observed effects are due to internal noise + signal modulation.
- **Spatial-uncertainty control.** The authors experimentally ruled out spatial uncertainty as an explanation by showing the same pattern with reduced uncertainty.

## 6. Critique / limitations

The "contrast gain" vs "response gain" distinction is a *parametric* distinction. Real neurons may show a mixture; the empirical pattern is sufficient to favor contrast gain as the *dominant* mechanism but doesn't rule out smaller contributions from response gain.

The task uses *transient* (exogenous) attention — peripheral cues. *Sustained* (endogenous) attention may behave differently. The authors' subsequent work has addressed both regimes; the 2002 paper is specifically about transient attention.

The visual-field asymmetries are interesting but are a *side finding* — they're characterized but their mechanism (e.g., asymmetric cortical magnification) is not addressed.

The framework doesn't distinguish *attention-as-gain* from *attention-as-precision*. Reynolds & Heeger 2009 frames it as gain modulation; Feldman & Friston 2010 frames it as precision-weighting. The Cameron-Tai-Carrasco data support gain modulation; whether this is the underlying mechanism or just a phenomenological description is an open question.

The result is for *covert* attention. Overt attention (with eye movements) involves additional processes (saccade preparation, pre-saccadic attention) not captured by this paradigm.

## 7. Connection to our work

This paper supports the user's commitment to *multiplicative gain* as the architectural form of attention:

**Contrast gain ↔ Feedback Transformer Hadamard product.** Cameron et al.'s "contrast gain" mechanism — multiplicative scaling of the input signal — is the *exact* architectural form the Feedback Transformer's Hadamard-product implements. The architectural choice is empirically warranted by Cameron et al.'s human-psychophysics result.

**Cued attention shifts the psychometric function.** The recurrent ViT's cued-attention results (faster RT, higher accuracy at cued locations) are the AI analog of Cameron et al.'s contrast-threshold shift. Future experiments could measure the recurrent ViT's *full psychometric function* at cued and uncued locations to verify the architectural homology — does the model also show a *leftward shift* (contrast gain) rather than a *vertical scaling* (response gain)?

**Visual-field uniformity of attention.** Cameron et al.'s finding that attention's benefit is uniform across the visual field is a useful invariance property. The recurrent ViT's attention map should similarly produce uniform benefits across the 12×12 patch grid; checking this empirically would validate the architectural fidelity.

**External-noise-free regime.** Cameron et al.'s exclusion of external noise puts them in the *signal-enhancement-dominant* regime of Lu & Dosher 1998. PRISM and the recurrent ViT are typically tested on clean (noise-free) stimuli — the regime where signal enhancement should dominate. The Cameron-Tai-Carrasco methodology applies directly.

The recurrent ViT paper cites Cameron et al. 2002 in its bibliography (ref [51]). Future manuscripts that argue for multiplicative attention should cite this paper as the empirical foundation.

## 8. Citations to follow

- `lu_dosher1998_external_noise` — companion external-noise paper. In seed, full depth.
- `solomon2004_cues_sensitivity` — companion cue-effect paper. In seed, full depth.
- `reynolds_heeger2009_normalization` — normalization model. In seed, full depth.
- `carrasco_yeshurun1998_contrast_attention` — Carrasco & Yeshurun foundational work. Not in seed.
- `pestilli_carrasco2005_attention_gain` — Pestilli & Carrasco follow-up. Not in seed.
- `feldman_friston2010_attention_free_energy` — precision-weighting reframing. In seed, full depth.
- `posner1980_orienting` — Posner paradigm. In seed, full depth.
