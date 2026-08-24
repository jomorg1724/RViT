---
id: ernst_banks2002_cue_combination
title: "Humans integrate visual and haptic information in a statistically optimal fashion"
authors:
  - "Ernst, Marc O."
  - "Banks, Martin S."
year: 2002
venue: "Nature"
doi: "10.1038/415429a"
arxiv: ""
url: "https://doi.org/10.1038/415429a"
tags:
  - psychophysics
  - human-neuroimaging
concepts:
  - bayesian-cue-integration
  - multi-sensory-integration
  - precision-weighting
related:
  - jordan2023_dendritic_bayesian
  - feldman_friston2010_attention_free_energy
  - choi2023_msi_review
  - senkowski_engel2024_multi_timescale_msi
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Humans integrate visual and haptic information in a statistically optimal fashion

## 1. Abstract

When a person looks at an object while exploring it with their hand, vision and touch both provide information for estimating the object's properties. Vision frequently dominates the integrated visual-haptic percept (for size, shape, or position judgments), but in some circumstances the percept is clearly affected by haptics. The authors propose that a general principle — *minimizing variance in the final estimate* — determines the degree to which vision or haptics dominates. This principle is realized by *maximum-likelihood estimation* combining the two cues. To investigate cue combination quantitatively, the authors first measured the variances associated with visual and haptic estimation of object height. They then constructed a maximum-likelihood integrator using these measured variances. The model behaved very similarly to human subjects in a visual-haptic task. The nervous system therefore appears to combine visual and haptic information in a fashion similar to a *maximum-likelihood integrator*. Visual dominance occurs when the variance associated with visual estimation is lower than that associated with haptic estimation.

## 2. Why this matters for us

Ernst & Banks 2002 is the canonical psychophysical demonstration of *Bayes-optimal multisensory integration* in humans. It is the load-bearing empirical evidence that the brain combines cues from different modalities by *precision-weighting* — exactly the architectural commitment of the Feedback Transformer's multiplicative integration and the user's MSI hub. The paper supplies the *behavioral* signature that any architectural account of multisensory integration must reproduce: when cue variances are varied, the integrated percept's weighting between cues shifts in proportion to the inverse variances. The user's program inherits this as a target empirical pattern for the MSI hub.

## 3. Key claims

1. **The principle.** When the brain integrates multiple sensory cues, it does so by *minimizing variance in the final estimate*. This is the maximum-likelihood estimator: the optimal Bayesian combination under Gaussian assumptions.
2. **The mathematical form.** Under Gaussian assumptions, the optimal combination weights each cue's estimate by its inverse variance (precision):

$$
\hat S_{\text{combined}} = \frac{\sigma_V^{-2} \hat S_V + \sigma_H^{-2} \hat S_H}{\sigma_V^{-2} + \sigma_H^{-2}}, \qquad \sigma_{\text{combined}}^{-2} = \sigma_V^{-2} + \sigma_H^{-2}
$$

where $\hat S_V, \hat S_H$ are the visual and haptic single-cue estimates and $\sigma_V, \sigma_H$ are their standard deviations.

3. **Empirical test design.** Measure the variances of single-cue (vision-only, haptics-only) estimates of object size; predict the bimodal estimate's variance and bias from the maximum-likelihood formula; compare predicted to measured bimodal behavior.
4. **Visual dominance is variance-driven, not modality-driven.** When the visual variance is low (under normal lighting), vision dominates the percept. When the visual variance is artificially increased (by adding noise to the visual stimulus), the percept shifts toward the haptic cue. The brain doesn't have a fixed visual preference — it uses whichever cue is more reliable.
5. **Quantitative match.** The maximum-likelihood model predicts bimodal-estimate variance and bias with high accuracy across multiple noise conditions. The data fit is tight, not just qualitatively right.
6. **Bayes-optimal integration is the right level of description.** Whatever neural mechanism implements the integration, the behavioral output matches the Bayesian-optimal computation. The brain has somehow learned the right algorithm.

## 4. Methods

**Stimulus.** Subjects judged the height of a virtual rectangular block presented via a haptic device (a force-feedback handle) and a binocular visual display. The visual stimulus was a rendered image of the block; the haptic stimulus was the felt height of the block when the handle was moved between top and bottom.

**Single-cue experiments.** Subjects judged height with vision only or haptics only (the other modality was blocked). The variance of the judgments gives the per-cue precision.

**Bimodal experiments.** Subjects judged height with both cues present. Discrepancies between the cues were introduced (the visual height was offset from the haptic height by a small amount the subject couldn't reliably detect). The subject's bimodal judgment was then a *weighted combination* of the two cues, with the weight measurable from the offset's effect on the percept.

**Manipulation of cue reliability.** Visual noise was systematically varied by adding random pixel noise to the visual stimulus, increasing the variance of the single-cue visual estimate. The bimodal judgment was then re-measured at each noise level.

**Comparison.** The maximum-likelihood predicted bimodal weight (computed from the measured single-cue variances) was compared to the empirically measured bimodal weight.

## 5. Results

The principal quantitative findings:

- **Single-cue precision.** Visual estimation of height had standard deviation ≈ 0.7 mm; haptic estimation ≈ 1.3 mm (in the baseline condition). The visual cue was therefore more precise.
- **Bimodal weight.** With noiseless visual stimulus, subjects weighted vision ≈ 70% and haptics ≈ 30% — close to the maximum-likelihood prediction of $\sigma_V^{-2} / (\sigma_V^{-2} + \sigma_H^{-2})$ given the measured variances.
- **Visual-noise modulation.** As visual noise increased, the bimodal weight on vision *decreased* and the weight on haptics *increased*, matching the maximum-likelihood prediction at each noise level. The fit was high quantitatively, not just qualitatively.
- **Bimodal precision.** The variance of the bimodal estimate was *lower* than either single-cue variance — exactly the Bayesian-optimal prediction. The integration is genuinely beneficial, not just averaging.
- **Visual dominance dissolves at high noise.** When visual variance exceeded haptic variance, haptics became the dominant cue. Modality is not innately prioritized; reliability is.

## 6. Critique / limitations

The experiments use *simple cues* with known Gaussian noise. Real-world multisensory perception involves more complex cues with non-Gaussian noise, structured biases, and prior information. The Bayes-optimal framework still applies in principle but its empirical predictions become harder to test.

The single-cue variances are measured from psychophysical thresholds. These thresholds may not perfectly capture the brain's internal noise. The maximum-likelihood prediction is therefore sensitive to the assumption that the measured variance equals the brain's true uncertainty.

The framework assumes *independent* noise sources in the two modalities. If the noises are correlated (e.g., shared attention fluctuations affect both vision and haptics), the integration is no longer Bayes-optimal under the simple formula. The paper doesn't engage with correlated noise.

The Bayes-optimal account is a *behavioral* description. The neural mechanism implementing the integration is not addressed. Subsequent work (Jordan et al. 2023; Ma et al. 2006) has proposed neural-level implementations; the 2002 paper is silent.

The framework focuses on *spatial* cue combination (object size, position, shape). Whether it generalizes to *temporal* multisensory integration (audio-visual speech, motion-direction combination) is partially confirmed by subsequent work but not by the original paper.

## 7. Connection to our work

This paper is the canonical psychophysical reference for the user's commitments to multisensory integration and precision-weighting:

**The MSI hub's behavioral target.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) includes an MSI hub that integrates sensory inputs from multiple modalities. The Ernst-Banks behavioral pattern — precision-weighted combination with weights that track cue reliabilities — is the *empirical target* the MSI hub should reproduce. Any future MSI-hub model should be benchmarked against the Ernst-Banks-style cue-combination behavior.

**Precision-weighting as architectural commitment.** The Feedback Transformer's multiplicative structure ([feedback_transformer](research_db/concepts/feedback_transformer.md)) and PRISM's saliency-gated update both implement precision-weighting at the network level. Ernst-Banks supplies the behavioral validation: real human percepts show precision-weighting; the user's architectures aim to reproduce this. Feldman & Friston 2010 ([feldman_friston2010_attention_free_energy](research_db/papers/feldman_friston2010_attention_free_energy.md)) gives the theoretical link between Ernst-Banks-style optimal cue combination and predictive-coding precision-weighting; the two are mathematically equivalent in the appropriate limit.

**Cellular implementation via Jordan 2023.** Ernst-Banks is the behavioral phenomenon; Jordan et al. 2023 ([jordan2023_dendritic_bayesian](research_db/papers/jordan2023_dendritic_bayesian.md)) is the proposed cellular implementation in conductance-based dendrites. The user's program adopts Jordan's framework as the cellular substrate; Ernst-Banks is the load-bearing behavioral citation that the cellular framework is designed to reproduce.

**Multi-hub competition with precision-weighted integration.** The user's multi-hub system extends Ernst-Banks-style precision-weighting from sensory-cue combination to *hub-level* combination: hubs compete for control of the central self-attention substrate via Q/K/V projections combined with multiplicative weighting. The mathematical machinery is the same; the user's contribution is the scaling-up to hub-level.

**Modality dominance shifts with reliability.** Ernst-Banks's finding that vision/haptic dominance shifts with noise is the empirical signature of *adaptive* precision-weighting. The user's program's commitment to learned (rather than fixed) hub weights inherits this adaptivity: different tasks should produce different effective hub weights based on which hub is most reliable for the current input.

The recurrent ViT paper doesn't address multisensory integration directly. PRISM v1 and v2 are also single-modality. Future extensions to multi-modal architectures (audio-vision RL, embodied perception) should cite Ernst & Banks 2002 as the founding cue-combination reference.

## 8. Citations to follow

- `jordan2023_dendritic_bayesian` — cellular Bayesian-integration implementation. In seed, full depth.
- `feldman_friston2010_attention_free_energy` — variational framework subsuming cue combination. In seed, full depth.
- `ma2006_bayesian_decoding_pop_codes` — population-code Bayesian decoding. Not in seed.
- `kording_wolpert2004_bayesian_decision` — Bayesian decision-making in motor control. Not in seed.
- `alais_burr2004_audiovisual_optimal` — audiovisual extension of Ernst-Banks. Not in seed.
- `pouget_beck_drugowitsch_latham2013_probabilistic_brains` — review of probabilistic brain models. Not in seed.
- `senkowski_engel2024_multi_timescale_msi` — multi-timescale MSI review. In seed.
- `choi2023_msi_review` — recent MSI review. In seed.
