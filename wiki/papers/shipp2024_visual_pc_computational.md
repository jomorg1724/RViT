---
id: shipp2024_visual_pc_computational
title: "Computational components of visual predictive coding circuitry"
authors:
  - "Shipp, Stewart"
year: 2024
venue: "Frontiers in Neural Circuits"
doi: "10.3389/fncir.2023.1254009"
arxiv: ""
url: "https://doi.org/10.3389/fncir.2023.1254009"
tags:
  - predictive-coding
  - review
  - cortical-anatomy
  - early-visual-cortex
concepts:
  - hierarchical-predictive-coding
  - prediction-error-map
  - precision-weighting
  - cortical-microcircuit-model
  - top-down-feedback
related:
  - rao_ballard1999_predictive_coding
  - bastos2012_canonical_microcircuits
  - bastos2015_laminar_macaque
  - keller_mrsic_flogel2018_pc_review
  - pezzulo_parr_friston2024_active_inference
  - larkum2013_apical_basal
  - friston2010_fep_unified_theory
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - programmatic_pubmed
status: full
depth: full
last_updated: "2026-05-16"
---

# Computational components of visual predictive coding circuitry

## 1. Abstract

If a full visual percept is to be understood as a *hypothesis*, then a neural *prediction* — although addressing one particular component of image content (3D organization, the interplay between lighting and surface color, the future trajectory of moving objects) — is the cellular implementation of that hypothesis. Because processing is hierarchical, predictions generated at one level are conveyed in a backward direction to a lower level, seeking to predict the neural activity at that prior stage of processing, and learning from errors signaled in the opposite direction. This is the essence of *predictive coding* — at once an algorithm for information processing and a theoretical basis for the operations performed by cerebral cortex. Neural models for the implementation of predictive coding invoke specific functional classes of neuron for generating, transmitting, and receiving predictions, and for producing reciprocal error signals. A third class — *precision* neurons — regulates the magnitude of error signals contingent upon the confidence placed upon the prediction (i.e., the reliability of the sensory data the prediction predicts). Shipp focuses on the predictive physiology of mouse and monkey visual cortex, summarizing and commenting on evidence to date and placing it in the context of the broader field. He concludes that predictive coding has a firm grounding in basic neuroscience and that there remains much to learn.

## 2. Why this matters for us

Shipp 2024 is the contemporary cell-type-level synthesis of the predictive-coding framework. Where Keller & Mrsic-Flogel 2018 ([keller_mrsic_flogel2018_pc_review](research_db/papers/keller_mrsic_flogel2018_pc_review.md)) emphasized closed-loop mouse-V1 experiments, Shipp 2024 emphasizes the *cellular implementation* — specifically, which cells should code predictions, which should code prediction errors, and which should code *precision*. The introduction of an explicit *precision-coding cell class* in the empirical synthesis is a substantive contribution beyond earlier reviews. For the user's program, this paper is the most up-to-date reference on the cellular substrate of predictive coding in visual cortex.

## 3. Key claims

1. Predictive coding is supported by three functional cell classes in visual cortex: **prediction neurons** (generating descending predictions), **error neurons** (computing residuals between prediction and bottom-up input), and **precision neurons** (regulating the magnitude of error signaling contingent on prediction reliability).
2. The framework is hierarchical: predictions generated at one cortical level address the predicted activity of the level below; errors propagate upward to update the higher level's prediction.
3. **Precision neurons** are a new class compared to Rao-Ballard's original two-class formulation. Their role is to *modulate the gain* of error pathways based on the confidence in the corresponding prediction.
4. The empirical evidence supports each cell class in mouse and macaque visual cortex, though the cell-class assignments remain debated. The framework is no longer purely theoretical; specific cell populations are putatively identified.
5. The ultimate source of predictions is multifactorial: knowledge of current environmental context plus the immediate past, allied to memory, lifetime experience, and evolutionary history.
6. The framework provides numerous experimental approaches: manipulate subjects' expectations (e.g., by training expected stimulus sequences), then examine neural signals elicited by surprising versus less-surprising visual stimuli. The expected-vs-surprising contrast is the experimental signature of predictive coding.
7. The framework has firm grounding in basic neuroscience but remains incomplete: many specific predictions (cell-class identifications, laminar mappings, frequency signatures) are partly supported by data and partly remain hypothetical.

## 4. Methods

A *narrative review*. Shipp synthesizes recent empirical work on predictive coding in mouse and macaque visual cortex, with focus on:
- Closed-loop visuomotor mismatch experiments (mouse V1; Keller group).
- Laminar recordings testing the Bastos 2012 canonical-microcircuit predictions (macaque; Bastos 2015 in particular).
- Cell-type-specific manipulations (optogenetics in mouse, neuropharmacology in macaque) probing the candidate prediction-error and precision cell classes.
- Theoretical work on the variational free-energy framework and active-inference extensions.

The review's contribution is the *cell-class-level synthesis* — specifically, the elevation of precision neurons to a first-class concept on par with prediction and error neurons.

## 5. Results

The principal empirical claims the review consolidates:

- **Mismatch responses (mouse V1).** Replicated across labs: V1 neurons show large responses to mismatches between predicted and actual visual input. Specific cell classes (likely L2/3 pyramidal cells with apical-dendrite top-down input) carry the mismatch signal.
- **Expectation suppression (mouse and macaque).** V1, V4, and IT cells show *suppressed* responses to expected stimuli compared to unexpected ones. The suppression scales with the strength of the expectation.
- **Laminar frequency signature (macaque).** Bastos 2015 confirmed feedforward theta/gamma and feedback beta; Shipp emphasizes this as the most robust signature of feedforward-vs-feedback distinction.
- **Precision-related neuromodulation.** Cholinergic and noradrenergic neuromodulation modulate the gain of error pathways; this is the candidate cellular substrate of precision weighting.
- **Cellular substrate via apical dendrites.** Larkum BAC mechanism and Jordan-style Bayesian dendrites are the candidate single-cell implementations of the prediction-error and precision computations.
- **Open questions.** The exact cell-class assignments are contested (Bastos vs Heeger mapping); the in-vivo direct evidence of individual prediction-error cells is sparse; the deep-learning instantiations of predictive coding underperform standard supervised networks.

## 6. Critique / limitations

The framework remains *partially testable*. Many specific predictions (cell-class identifications, precise laminar circuit mappings) require techniques that are not yet standard (e.g., cell-type-specific in-vivo optogenetics in macaque). The review is appropriately cautious about strong claims.

The empirical evidence is concentrated in mouse V1. Macaque evidence is mostly from laminar recordings (Bastos 2015) which characterize *frequency signatures* rather than cell-class participation. The gap between mouse cell-type evidence and macaque circuit evidence is acknowledged.

The introduction of *precision neurons* as a first-class cell class is a substantive theoretical commitment but is not yet firmly empirically established. Subsequent work needs to identify specific cell populations that match the precision-neuron functional profile (e.g., neurons whose gain modulates error neurons but whose activity itself doesn't carry error or prediction signals).

The framework's failure to translate into competitive deep-learning models is acknowledged but not deeply analyzed. Wen et al. 2018 and Pinchetti et al. 2024 show that deep PC networks underperform supervised baselines; whether this reflects a genuine architectural limitation or a training-procedure limitation is unsettled.

The review does not engage seriously with alternative frameworks (Spratling-style divisive normalization without explicit error neurons; Heeger-style alternative laminar mappings). The framework is presented as the leading account; competing accounts get less attention.

## 7. Connection to our work

This paper is the contemporary cell-type-level reference for the user's predictive-coding architectural commitments:

**Three cell classes mapped to PRISM v2's three computational substrates.** PRISM v2's two-level hierarchy ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10) has cells that compute predictions (the generative decoder output), errors (the prediction-error map), and gains/precision (the saliency-gated update). Shipp's three-class framework supplies the cellular interpretation: each of PRISM v2's computational substrates has a biological analog at the cell-class level.

**Precision neurons as a first-class concept.** The user's commitment to multiplicative integration ([feedback_transformer](research_db/concepts/feedback_transformer.md)) implements precision-weighting at the architectural level. Shipp 2024's elevation of precision neurons to a first-class cell class supports the user's architectural choice: precision-weighting isn't just a free parameter on top of predictions and errors; it has its own dedicated computational substrate.

**The cellular substrate via apical dendrites.** Shipp's brief discussion of Larkum-style apical-dendrite mechanisms as the candidate implementation of error/precision computation links the macroscopic predictive-coding framework to the cellular AND-gate that the user's program inherits. The Feedback Transformer's Hadamard product is the architectural analog of the cellular precision-modulation.

**Visual-cortex-specific framing.** Shipp's focus on mouse and macaque visual cortex makes the framework directly applicable to the recurrent ViT and PRISM, both of which are visual architectures. The empirical signatures Shipp catalogs (mismatch responses, expectation suppression, laminar frequency) are the targets a successful visual-PC architecture should reproduce.

**Translational gap.** Shipp acknowledges that deep PC networks underperform supervised baselines. This is a useful framing for the user's program: the user's program adopts predictive-coding *architectural commitments* (multi-source feedback, hierarchical compartments) but trains with backprop rather than with a pure predictive-coding objective. The hybrid may be the right level — keep the architectural insights, use a pragmatic training rule.

The recurrent ViT and PRISM papers cite earlier Friston / Rao-Ballard / Bastos papers. Future revisions should cite Shipp 2024 alongside Keller-Mrsic-Flogel 2018 as the contemporary empirical reviews of predictive coding in visual cortex.

## 8. Citations to follow

- `keller_mrsic_flogel2018_pc_review` — companion empirical review. In seed, full depth.
- `bastos2012_canonical_microcircuits` — canonical-microcircuit framework. In seed, full depth.
- `bastos2015_laminar_macaque` — laminar primate test. In seed, full depth.
- `rao_ballard1999_predictive_coding` — the founding paper. In seed, full depth.
- `friston2010_fep_unified_theory` — variational framework. In seed, full depth.
- `pezzulo_parr_friston2024_active_inference` — contemporary active-inference synthesis. In seed, full depth.
- `larkum2013_apical_basal` — apical-basal cellular framework. In seed, full depth.
- `walsh2020_precision_neuromodulation` — precision-weighting via neuromodulation. Not in seed.
- `de_lange2018_predictive_processing_review` — separate predictive-processing review. Not in seed.
