---
id: keller_mrsic_flogel2018_pc_review
title: "Predictive processing: a canonical cortical computation"
authors:
  - "Keller, Georg B."
  - "Mrsic-Flogel, Thomas D."
year: 2018
venue: "Neuron"
doi: "10.1016/j.neuron.2018.10.003"
arxiv: ""
url: "https://doi.org/10.1016/j.neuron.2018.10.003"
tags:
  - predictive-coding
  - review
  - primate-neurophysiology
  - cortical-anatomy
concepts:
  - hierarchical-predictive-coding
  - rao-ballard-coding
  - cortical-microcircuit-model
  - prediction-error-map
  - top-down-feedback
  - apical-basal-dendritic-integration
related:
  - rao_ballard1999_predictive_coding
  - bastos2012_canonical_microcircuits
  - friston2010_fep_unified_theory
  - spratling2008_pc_biased_competition
  - clark2013_whatever_next
  - aitchison_lengyel2017_pc_bayesian
  - wen2018_deep_pc_networks
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Predictive processing: a canonical cortical computation

## 1. Abstract

This Perspective describes predictive processing as a computational framework for understanding cortical function in the context of emerging evidence, with a focus on sensory processing. The authors discuss how the predictive processing framework may be implemented at the level of cortical circuits and how its implementation could be falsified experimentally. They summarize the general implications of predictive processing on cortical function in healthy and diseased states. The Perspective explicitly aims to take predictive processing from a theoretical proposal (Rao & Ballard 1999; Friston 2010) to an empirically testable account of canonical cortical computation, naming specific cell types, synaptic connections, and experimental signatures that would corroborate or falsify the framework.

## 2. Why this matters for us

This is the modern review the user's program builds on. Where Rao & Ballard 1999 introduced predictive coding as a theoretical reframing and Bastos et al. 2012 mapped it onto a canonical cortical microcircuit, Keller & Mrsic-Flogel 2018 brings the framework forward by ten more years of experimental work — specifically the optogenetic and two-photon-imaging studies in mouse V1 that have produced the cleanest single-cell evidence of prediction-error signals. PRISM v1 and v2 are both designed as predictive-coding architectures; this paper is the load-bearing review that situates them in the contemporary literature.

## 3. Key claims

1. Predictive processing is a *canonical* cortical computation — it applies across primary sensory cortices, association cortices, and motor cortex, not just to early visual processing as in the original Rao-Ballard formulation.
2. The framework predicts the existence of two functionally distinct cell populations at every cortical level: *representation neurons* coding the current best estimate of latent causes, and *prediction-error neurons* coding the residual between the actual sensory input and the descending prediction.
3. Specific empirical signatures should follow: cells should respond more strongly to *unexpected* stimuli than to expected ones (the prediction-error signature), and the population response to a stimulus should be smaller when the stimulus is preceded by a valid predictive cue.
4. Implementations of the framework in cortical microcircuits should respect anatomical constraints: descending predictions are routed via L5/L6 corticocortical and corticothalamic projections; ascending errors are routed via L2/3 → L4 → L2/3 forward projections. (This refines and slightly differs from Bastos's specific laminar mapping.)
5. The framework provides a unified account of multiple cortical phenomena: surround suppression, mismatch responses, expectation effects, attention as precision weighting, and altered cortical responses in schizophrenia and autism. The unifying theme is that all of these are consequences of one computational principle (minimize prediction error) operating in cortical circuits with specific anatomical structure.
6. Falsification routes: cells with the predicted differential responses to expected vs unexpected stimuli should be identifiable; specific circuit elements (e.g., L2/3 prediction-error cells receiving L5 descending prediction inputs) should show the predicted patterns of synaptic input; targeted disruption of prediction sources should specifically increase the response of prediction-error cells.

## 4. Methods

A narrative review. The authors synthesize a decade of experimental work in mouse primary visual cortex from labs that have used closed-loop virtual-reality paradigms (where the visual feedback either matches the animal's locomotion or is intentionally mismatched), two-photon calcium imaging (to record from hundreds of neurons simultaneously), and optogenetic perturbations (to dissect circuit elements). The most cited experiments are from the Keller lab itself (Keller, Bonhoeffer & Hübener 2012; Zmarz & Keller 2016; Attinger, Wang & Keller 2017) and from collaborators.

The review's contribution is organizational: it argues that the body of empirical results from these closed-loop paradigms is collectively consistent with a specific predictive-processing implementation in mouse V1, and it specifies what new experiments would test the framework further.

## 5. Results

The empirical body the review draws on yields the following experimental signatures (each cited in the review with specific papers):

- **Mismatch responses in mouse V1.** Cells in mouse V1 respond strongly to visuomotor mismatches (e.g., the animal runs but the visual flow stops) that cannot be predicted from either the visual input or the running command alone. The mismatch response is consistent with a prediction-error signal.
- **Expectation suppression.** Stimuli that match an established prediction elicit weaker V1 responses than unexpected stimuli of equal physical salience.
- **Layer-specific patterns.** Mismatch responses are concentrated in specific cortical layers (L2/3) and are sensitive to the inactivation of long-range inputs from premotor/parietal areas — consistent with the proposed circuit: top-down prediction comes from higher areas, and the L2/3 cells compute the residual.
- **Precision-weighting effects.** When the predictive cue's reliability is varied, V1 responses scale in a manner consistent with the prediction-error pathway being weighted by the cue's reliability (precision).
- **Disease phenotypes.** In schizophrenia and autism, behavioral and neural responses are consistent with abnormal prediction-error weighting — too high in autism (over-weighting of sensory input vs prediction), too low in some accounts of schizophrenia (over-weighting of prediction vs sensory input).

These are qualitative-to-moderately-quantitative findings; the review's claim is that the *pattern* across many studies is consistent with predictive processing, not that any single study definitively establishes it.

## 6. Critique / limitations

The framework's principal weakness, acknowledged in the review, is *underspecification*. "Predictive processing" can be implemented in many ways, with different choices for: (a) which cell types code predictions vs errors; (b) whether predictions are additive or multiplicative; (c) how precision weighting is implemented; (d) whether learning is end-to-end or local. Different implementations make different empirical predictions, and the existing data are consistent with several. Until specific implementations are pinned down, "predictive processing" risks becoming a framework that explains everything and predicts little.

The mouse V1 closed-loop paradigm is influential but has limitations. The animal's task is engineered, the predictions are simple (running speed → visual flow), and the cortical signatures may not generalize to richer naturalistic tasks. Critics have argued that the "mismatch response" can be reproduced by simpler accounts (e.g., divisive normalization with adaptation) without requiring explicit prediction-error machinery (Spratling 2008 in the original mathematical framework, more recently in mouse-V1-specific re-analyses).

The clinical applications (schizophrenia, autism) are speculative. The behavioral phenotypes are consistent with abnormal precision weighting, but the brain-level evidence is far from definitive.

The review does not engage with deep-learning implementations of predictive coding (Wen et al. 2018; Pinchetti et al. 2024) or with the broader free-energy framework that subsumes predictive coding (Friston 2010, 2019). The relationship between Keller & Mrsic-Flogel's circuit-level account and the variational-Bayes framework is referenced but not formalized.

## 7. Connection to our work

This paper is the contemporary anchor for both PRISM v1 and PRISM v2's architectural commitment to predictive coding. Specifically:

- **Prediction-error map as the core signal** ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.6; [PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10). PRISM's saliency-gated update is built around the prediction-error signal $S_t = |\tilde X_t - X_t|$, which is the Keller-Mrsic-Flogel "prediction-error neuron" output. The Rao-Ballard 1999 formulation provides the architectural template; Keller-Mrsic-Flogel 2018 provides the modern empirical grounding for taking the prediction-error neuron as a real cellular substrate rather than a theoretical convenience.
- **The mismatch / expectation suppression behavior.** PRISM is trained on change-detection. Behaviorally, change-detection requires the system to identify unexpected events — exactly the regime where Keller's framework predicts maximum prediction-error response. The recurrent ViT's "attention to cued location" effect can be interpreted in the same framework: the cue establishes a prediction, and the change at the cued location is the prediction-error signal that the attention map should highlight.
- **Layer-specific implementations.** PRISM v2 commits to a two-level cortical hierarchy ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10), with cross-level error and prediction flow. Keller-Mrsic-Flogel 2018 supplies the cell-type and layer assignments that PRISM v2's components are anatomically homologous to: feedforward V1→V2 encoders ↔ L4→L2/3→L5 ascending error pathway; descending V2→V1 modulation ↔ L5/L6 descending prediction pathway.
- **Precision weighting as attention.** The user's program treats top-down feedback as multiplicative modulation (FiLM in PRISM, multi-source Q/K/V Hadamard product in the Feedback Transformer). This is the precision-weighting interpretation of attention in the predictive-processing framework — top-down signals scale the gain of prediction errors, exactly as the review describes.

The Recurrent ViT manuscript (2502.10955) is conservative about invoking predictive coding. The user's program is not: predictive coding is the theoretical foundation of the entire architecture. Keller & Mrsic-Flogel 2018 is the most-cited modern review on the topic and is the appropriate primary citation for the framework in any follow-up paper.

## 8. Citations to follow

- `keller_bonhoeffer_hubener2012_visual_flow_prediction` — original closed-loop mouse V1 paper. Not in seed.
- `attinger_wang_keller2017_mismatch_v1` — mismatch-response paper. Not in seed.
- `zmarz_keller2016_unmatched_visual_flow` — V1 mismatch in head-fixed mice. Not in seed.
- `bastos2012_canonical_microcircuits` — the prior canonical-microcircuit review. In seed, full depth.
- `rao_ballard1999_predictive_coding` — the foundation. In seed; full depth.
- `friston2010_fep_unified_theory` — the FEP umbrella. In seed; full depth.
- `clark2013_whatever_next` — the philosophical framing of predictive processing. In seed.
- `aitchison_lengyel2017_pc_bayesian` — formal relation between PC and Bayesian inference. In seed.
- `spratling2008_pc_biased_competition` — alternative implementation. In seed.
- `wen2018_deep_pc_networks` — deep PC networks. In seed.
