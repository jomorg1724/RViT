---
id: lu_dosher1998_external_noise
title: "External noise distinguishes attention mechanisms"
authors:
  - "Lu, Zhong-Lin"
  - "Dosher, Barbara A."
year: 1998
venue: "Vision Research"
doi: "10.1016/s0042-6989(97)00273-3"
arxiv: ""
url: "https://doi.org/10.1016/s0042-6989(97)00273-3"
tags:
  - visual-attention
  - psychophysics
  - methodology
concepts:
  - signal-detection-theory
  - gain-modulation
  - precision-weighting
  - psychometric-function
related:
  - cameron2002_covert_attention_contrast
  - solomon2004_cues_sensitivity
  - reynolds_heeger2009_normalization
  - feldman_friston2010_attention_free_energy
  - posner1980_orienting
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_49
status: full
depth: full
last_updated: "2026-05-14"
---

# External noise distinguishes attention mechanisms

## 1. Abstract

Lu & Dosher develop and test a powerful method — the *perceptual template model* (PTM) with *external noise* — for identifying which of three attention mechanisms is at work: *signal enhancement*, *distractor exclusion*, or *internal noise suppression*. Based on a noisy PTM of a human observer, the method adds increasing amounts of external Gaussian noise to the visual stimulus and observes the effect on attended vs unattended performance. The three mechanisms yield three "signature" patterns: signal enhancement gives an attentional benefit at *low* external noise that disappears at high noise; distractor exclusion gives a benefit at *high* external noise; internal noise suppression gives an overall additive shift. The authors apply the framework to a concurrent location-cued orientation discrimination task. They find that contrast thresholds are *systematically lower* for attended than for unattended stimuli at low external noise (consistent across three subjects, ≈17% threshold elevation for unattended), but the difference *disappears* at high external noise. This pattern is the signature of *signal enhancement* (equivalently, internal additive noise reduction).

## 2. Why this matters for us

Lu & Dosher 1998 is the canonical methodological paper for *dissecting attention mechanisms* using external noise manipulation. The framework — signal enhancement vs distractor exclusion vs noise suppression — is the standard taxonomy for what attention *does* computationally. For the user's program, this paper provides:
- A *methodology* for empirically testing what the recurrent ViT's attention map does (signal enhancement vs distractor exclusion vs noise suppression).
- The empirical evidence that human covert attention works primarily through *signal enhancement* — the architectural commitment of the user's Feedback Transformer's multiplicative gain.

## 3. Key claims

1. **Three attention mechanisms can be distinguished.** The Perceptual Template Model framework formalizes attention as a combination of three mechanisms: signal enhancement (boosting the attended signal), distractor exclusion (suppressing other signals), and internal noise suppression (reducing the effect of internal noise on attended signals).
2. **Each mechanism has a *signature* in the external-noise function.** The PTM predicts qualitatively different patterns of attended-vs-unattended performance as a function of added external noise. The mechanism can be identified from the empirical pattern.
3. **Signal enhancement: benefit at low noise, no benefit at high noise.** At low external noise, internal noise dominates; signal enhancement helps. At high external noise, external noise dominates; signal enhancement is ineffective.
4. **Distractor exclusion: benefit at high external noise.** Distractor exclusion gates out noise sources; the benefit grows with external noise.
5. **Internal noise suppression: shifts the whole curve.** Internal noise suppression provides an additive benefit across all noise levels.
6. **Empirical result: covert spatial attention is signal enhancement.** In Lu & Dosher's location-cued orientation task, the attentional benefit (≈17% threshold reduction) is present at low external noise and absent at high external noise — the signature of signal enhancement.
7. **The framework is robust.** The result holds across three subjects and across eight external-noise levels, providing strong empirical support.

## 4. Methods

**Task.** Concurrent location-cued orientation discrimination. Two Gabor patches appeared on either side of fixation; subjects judged the orientation of *both* (tilted slightly right or left). A central cue indicated which side to attend ("attended"), which to ignore ("unattended"), or "equal attention" baseline.

**External noise manipulation.** White Gaussian random noise was added to the visual stimulus at eight levels, ranging from 0% to high contrast. The subject's contrast threshold (for accurate orientation discrimination) was measured at each noise level.

**Conditions.**
- Attended: report orientation at the cued location.
- Unattended: report orientation at the uncued location.
- Equal: both locations equally attended.

**Analysis.** Threshold-vs-external-noise functions (the "threshold-versus-contrast" or TVC curves) were fit with PTM model parameters that specify the three attention mechanisms. The relative magnitudes of the parameters identify which mechanism is dominant.

## 5. Results

The principal quantitative findings:

- **17% threshold elevation for unattended.** Across three subjects, contrast thresholds for unattended stimuli were systematically 17% higher than for attended stimuli at low external noise (below ≈10% RMS contrast).
- **No attentional effect at high external noise.** Above the ≈10% noise level, attended and unattended threshold contrasts were *not* different.
- **The equal-attention condition is intermediate.** At low noise, equal-attention thresholds fell between attended and unattended, as expected for resource division.
- **The signature is clean.** The shape of the external-noise function (low-noise benefit, high-noise null) is the *signal enhancement* signature; the other two mechanisms (distractor exclusion, internal noise suppression) would have produced different patterns and are *not* observed.
- **Conclusion: covert attention enhances the signal, not gates distractors.** The architectural-level interpretation is that attention multiplies the signal (or equivalently, suppresses internal additive noise on the attended channel).

## 6. Critique / limitations

The PTM is a *linear model* of observer behavior. Real perception involves nonlinear stages (e.g., divisive normalization), which the framework partially abstracts away. Subsequent work (Reynolds & Heeger 2009 normalization model, [reynolds_heeger2009_normalization](research_db/papers/reynolds_heeger2009_normalization.md)) provides a more biologically detailed framework that subsumes the Lu-Dosher analysis.

The task uses *Gabor patches* — simple, low-level stimuli. Whether the same attention mechanism (signal enhancement) operates for richer, more complex stimuli is partially demonstrated by subsequent work but is not directly tested in this paper.

The framework treats attention as having three *separable* mechanisms. In reality, the mechanisms may co-occur or interact; a single empirical pattern might be produced by combinations. The PTM identifies the *dominant* mechanism but doesn't rule out smaller contributions of the others.

The external-noise manipulation is *external* — the experimenter controls the noise level. Whether the model captures the brain's response to *internal* perceptual noise (natural fluctuations in cortical activity) is more questionable.

The framework doesn't directly engage with the predictive-coding tradition. Signal enhancement can be reframed as precision-weighting in the FEP framework (Feldman & Friston 2010), but the 1998 paper doesn't make the connection.

## 7. Connection to our work

This paper supplies both methodology and substantive support for the user's program:

**Methodological framework for testing the recurrent ViT.** The Lu-Dosher external-noise method is directly applicable to the recurrent ViT: present stimuli with added external noise; measure detection performance; check whether the model's attention provides a *low-noise benefit* (signal enhancement signature). If yes, the model's attention is empirically aligned with human covert attention.

**Signal enhancement as the architectural commitment.** The Feedback Transformer's multiplicative gain ([feedback_transformer](research_db/concepts/feedback_transformer.md)) implements *signal enhancement* — it multiplies attended signal projections, boosting their contribution to the attention map. This matches the Lu-Dosher empirical pattern. The architectural choice is empirically warranted.

**Reframing in predictive-coding terms.** The Lu-Dosher signal enhancement is the *gain-modulation* form of attention; Feldman & Friston 2010 reframes this as *precision-weighting*. The two frameworks are mathematically equivalent at the appropriate limit. The user's program is theoretically aligned with both.

**Pre-stimulus vs stimulus-driven attention.** Lu & Dosher use *cued* attention (deployed before the stimulus). The recurrent ViT's cue mechanism is the architectural analog. The empirical match between cued covert attention and the model's cue-driven attention is the foundational empirical target.

The recurrent ViT paper cites Lu & Dosher 1998 in its bibliography (ref [49]). Future manuscripts that test the recurrent ViT's attention mechanism should explicitly use the Lu-Dosher methodology and cite this paper.

## 8. Citations to follow

- `cameron2002_covert_attention_contrast` — companion contrast-gain study. In seed, full depth.
- `solomon2004_cues_sensitivity` — companion cue-effect study. In seed, full depth.
- `reynolds_heeger2009_normalization` — normalization model of attention. In seed, full depth.
- `feldman_friston2010_attention_free_energy` — precision-weighting framework. In seed, full depth.
- `dosher_lu2000_mechanisms_attention` — Dosher & Lu follow-up. Not in seed.
- `pestilli_carrasco2005_attention_gain` — Pestilli & Carrasco gain-modulation. Not in seed.
- `posner1980_orienting` — foundational Posner paradigm. In seed, full depth.
