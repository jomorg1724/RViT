---
id: summerfield_delange2014_expectation
title: "Expectation in perceptual decision making: neural and computational mechanisms"
authors:
  - "Summerfield, Christopher"
  - "de Lange, Floris P."
year: 2014
venue: "Nature Reviews Neuroscience"
doi: "10.1038/nrn3838"
arxiv: ""
url: "https://doi.org/10.1038/nrn3838"
tags:
  - predictive-coding
  - decision-making
  - review
  - human-neuroimaging
  - primate-neurophysiology
concepts:
  - hierarchical-predictive-coding
  - precision-weighting
  - attentional-template
  - drift-diffusion-model
related:
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - keller_mrsic_flogel2018_pc_review
  - feldman_friston2010_attention_free_energy
  - bisley_goldberg2010_parietal_priority
  - awh2006_attention_wm
  - bastos2012_canonical_microcircuits
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Expectation in perceptual decision making: neural and computational mechanisms

## 1. Abstract

Sensory signals are highly structured in both space and time. These structural regularities in visual information allow *expectations* to form about future stimulation, thereby facilitating decisions about visual features and objects. Summerfield & de Lange discuss how expectation modulates neural signals and behavior in humans and other primates. They consider how expectations *bias* visual activity before a stimulus occurs, and how neural signals elicited by *expected* and *unexpected* stimuli differ. They discuss how expectations may influence decision signals at the computational level. Finally, they consider the relationship between visual expectation and related concepts: *attention* and *adaptation*.

## 2. Why this matters for us

Summerfield & de Lange 2014 is the canonical review of *expectation* in perceptual decision-making — the cognitive/behavioral phenomenon that predictive-coding architectures aim to reproduce. It is the empirical companion to the theoretical predictive-coding reviews (Clark 2013, Friston 2010, Bastos 2012). For the user's program, this review establishes the *behavioral signatures* the recurrent ViT's cued-attention effects are part of: expectation-driven facilitation of attended stimuli, validity-dependent RT and accuracy effects, expectation-suppression of expected stimuli. The recurrent ViT paper (2502.10955) reports exactly these signatures; Summerfield & de Lange supplies the broader literature in which those results are situated.

## 3. Key claims

1. **Expectations form from structural regularities.** The visual world has spatial and temporal structure; the brain exploits this structure by forming expectations that bias subsequent perception.
2. **Expectations bias activity before the stimulus.** Pre-stimulus baseline activity in feature-selective neurons is *elevated* for expected stimuli, even before the stimulus appears. This is a *preparatory* signature of expectation.
3. **Expected stimuli elicit smaller neural responses (expectation suppression).** Stimuli that match prior expectations produce *suppressed* responses compared to unexpected stimuli of equal physical salience. This is the *posterior* signature of expectation.
4. **The suppression is consistent with predictive coding.** Under hierarchical PC, the expected stimulus is well-predicted by descending feedback; the residual error is small; hence the L2/3 prediction-error response is suppressed. Expectation suppression is the empirical signature of the predictive-coding architecture.
5. **Expectations and attention interact.** Both modulate sensory processing, but in distinct ways: attention *increases* responses to attended stimuli (gain); expectation *decreases* responses to expected stimuli (sharpening). The two are dissociable, but in the predictive-coding framework both fall out as different aspects of precision-weighting.
6. **Expectations influence decision computations.** Beyond modulating sensory responses, expectations bias the *decision* — shifting the decision threshold or the starting point of evidence accumulation in drift-diffusion models. This is the computational layer beyond raw sensory modulation.
7. **The distinction from adaptation.** Adaptation (response decrease after repeated stimulation) is sometimes confused with expectation suppression. The two are dissociable: adaptation occurs even without expectation; expectation suppression occurs even without adaptation.

## 4. Methods

A narrative review covering human fMRI/MEG, primate single-unit, and behavioral psychophysics. The authors synthesize work from many labs:

**Behavioral psychophysics.** Standard expectation paradigms: provide a cue (visual, auditory, or instructional) that creates an expectation about an upcoming stimulus; measure RT, accuracy, sensitivity, criterion changes when the stimulus matches vs violates the expectation.

**Neural recordings.** fMRI / MEG in humans and single-unit recordings in macaque, focusing on early visual cortex (V1, V4) and decision-related regions (LIP, FEF, DLPFC).

**Computational modeling.** Drift-diffusion / sequential-sampling models of decision-making, with expectation modeled as a bias on starting point or threshold.

The review's contribution is the *synthesis* — fitting many disparate empirical findings into a unified expectation-and-perception framework, with predictive coding as the theoretical scaffolding.

## 5. Results

The principal empirical claims the review consolidates:

- **Pre-stimulus expectation.** Multivariate fMRI patterns in early visual cortex *predict* the upcoming expected stimulus, even before the stimulus appears. The cortex carries the prediction in its baseline activity.
- **Expectation suppression.** Repeated cued contexts show *reduced* visual cortex responses to expected stimuli, consistent with the predictive-coding suppression mechanism.
- **Sharpened tuning vs gain modulation.** Expected stimuli sometimes produce sharpened receptive-field tuning rather than reduced overall responses; attention typically produces gain increase. The two effects are dissociable in some paradigms.
- **Decision-level effects.** Expectation shifts the starting point in drift-diffusion models (subject is more likely to choose the expected option even before evidence accumulates) and reduces the threshold (less evidence needed to commit to the expected choice).
- **Validity effects.** When a cue's validity is high (e.g., 80%), expectation effects are large; at low validity (e.g., 50%, neutral), effects are absent. The magnitude scales with the cue's reliability.
- **Posner paradigm.** The Posner spatial-cuing paradigm shows characteristic RT and accuracy benefits at the cued location, with the magnitude scaling with validity. The recurrent ViT (2502.10955) reproduces this empirical pattern.

## 6. Critique / limitations

The framework treats *expectation* and *attention* as related but distinct. The Friston / Feldman-Friston tradition treats attention as a special case of precision-weighted prediction. Whether the empirical distinction (gain increase for attention; suppression for expectation) is genuinely orthogonal or reduces to one mechanism with different parameters is unsettled. Summerfield & de Lange present the distinction as substantive; predictive-processing theorists argue for unification.

The review focuses on *visual* expectation. Auditory and multi-modal expectation are referenced but not as fully developed. The framework should generalize but the specifics may differ across modalities.

The *neural signatures* are correlational. Causal tests of the predictive-coding interpretation (e.g., perturbing the descending prediction signal and measuring downstream response) are rare. The framework's empirical adequacy rests on the pattern of correlations across many studies, not on direct causal manipulation.

The *decision-level effects* (drift-diffusion starting-point bias, threshold reduction) are computational descriptions, not mechanistic explanations. The cortical-circuit-level implementation of these computational effects is not fully specified.

The relationship to *predictive coding* is asserted but not rigorously tested. Many empirical signatures (expectation suppression, sharpened tuning) can be reproduced by alternative architectures (divisive normalization with feedback; Spratling 2008). The framework is consistent with but doesn't uniquely require predictive coding.

## 7. Connection to our work

This paper supplies the *behavioral / cognitive-science* framing for the recurrent ViT's cued-attention results and the broader user program:

**Cued-attention effects in the recurrent ViT.** The 2502.10955 result that cued targets show faster RT and higher accuracy, scaling with cue validity, is exactly the empirical pattern Summerfield & de Lange describe. The recurrent ViT's cue mechanism (presenting a cue token before the target) is the architectural analog of "create an expectation; measure its effect on perception."

**Expectation suppression as the predictive-coding signature.** PRISM v1's saliency-gated update ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.7) is gated by prediction-error magnitude. Stimuli that match the prediction produce *low* error and hence *small* memory updates — the architectural form of expectation suppression. Summerfield & de Lange is the empirical anchor for this architectural commitment.

**Pre-stimulus expectation as the slow-memory's role.** PRISM v2's slow memory ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) carries task-relevant context that modulates V1 processing via slow-FiLM. This is the architectural analog of "pre-stimulus expectation biases visual cortex activity." Summerfield & de Lange's review supplies the empirical pattern.

**Decision-level integration.** Beyond sensory modulation, expectation affects the *decision* itself (drift-diffusion starting point, threshold). The recurrent ViT's actor head implements a decision rule; whether the cued-attention effects in the recurrent ViT operate purely at the sensory level (attention map) or also at the decision level is an interesting empirical question. The decoder analysis in 2502.10955 §6.4 partially addresses this; future work could deepen the analysis along the Summerfield-de Lange decision-vs-sensory dissection.

**The expectation-attention distinction.** The user's program treats attention as multiplicative gain on Q/K projections (Feedback Transformer Hadamard product). Expectation in Summerfield & de Lange's framework is a separate construct that *biases* sensory responses. Reconciling the two: in the predictive-coding interpretation, both attention and expectation are precision-weighted prediction-error modulations, with different parameters. The user's program is committed to this unification.

**Multi-hub system framing.** In the user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)), different hubs would generate different kinds of expectations: the VAE hub generates sensory expectations (predict next observation); the RL hub generates outcome expectations (predict next reward); the MSI hub generates context expectations (predict task-relevant features). Each hub's prediction biases central attention via Q/K contributions. The Summerfield-de Lange framing scales to this multi-hub setting naturally.

## 8. Citations to follow

- `rao_ballard1999_predictive_coding` — predictive-coding foundation. In seed, full depth.
- `friston2010_fep_unified_theory` — variational framework. In seed, full depth.
- `keller_mrsic_flogel2018_pc_review` — empirical review of predictive coding. In seed, full depth.
- `feldman_friston2010_attention_free_energy` — attention-as-precision. In seed, full depth.
- `bastos2012_canonical_microcircuits` — laminar implementation. In seed, full depth.
- `kok_jehee_de_lange2012_less_more` — de Lange's empirical work on expectation suppression. Not in seed.
- `de_lange2018_predictive_processing_review` — de Lange's later review of predictive processing. Not in seed.
- `bell_summerfield2015_neural_expectation_attention` — Summerfield's later work. Not in seed.
- `awh2006_attention_wm` — attention-WM link. In seed, full depth.
