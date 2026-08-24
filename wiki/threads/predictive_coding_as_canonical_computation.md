---
id: predictive_coding_as_canonical_computation
type: thread
title: "Predictive coding as canonical cortical computation"
papers:
  - srinivasan1982_predictive_coding_retina
  - rao_ballard1999_predictive_coding
  - friston2005_cortical_responses
  - friston2010_fep_unified_theory
  - feldman_friston2010_attention_free_energy
  - bastos2012_canonical_microcircuits
  - spratling2008_pc_biased_competition
  - clark2013_whatever_next
  - aitchison_lengyel2017_pc_bayesian
  - keller_mrsic_flogel2018_pc_review
  - wen2018_deep_pc_networks
  - pinchetti2024_benchmark_pc_networks
  - bastos2015_laminar_macaque
  - shipp2024_visual_pc_computational
  - pezzulo_parr_friston2024_active_inference
  - larkum2013_apical_basal
  - jordan2023_dendritic_bayesian
  - urbanczik_senn2014_predictive_dendrite
concepts:
  - hierarchical-predictive-coding
  - rao-ballard-coding
  - prediction-error-map
  - precision-weighting
  - variational-free-energy
  - active-inference
  - apical-dendrite-coincidence-detection
last_updated: "2026-05-13"
---

# Predictive coding as canonical cortical computation

This thread traces the predictive-coding (PC) framework from its retinal origins through its variational-Bayes generalization, its microcircuit implementation, its empirical testing in mouse and macaque visual cortex, and its current state as a candidate canonical computation of the cortex. The framework is the theoretical foundation of PRISM v1 and v2 and the architectural template against which the user's competition-emergent reframing is positioned.

---

## 1. Retinal origins (1982)

The framework's earliest formulation is in the retina: Srinivasan, Laughlin & Dubs 1982 (`papers/srinivasan1982_predictive_coding_retina.md`) proposed that retinal horizontal cells subtract a *prediction* of the photoreceptor signal (computed from neighboring photoreceptors) from the bipolar-cell input, leaving a residual that carries the local *novelty*. This is predictive coding in miniature: the predicted signal is removed at one stage, and only the unexpected residual proceeds.

The retinal account established the core architectural idea — that ascending pathways carry residuals, not raw signals — but in a one-level, hardwired form.

## 2. Cortical formulation (1999)

Rao & Ballard 1999 (`papers/rao_ballard1999_predictive_coding.md`) generalized the retinal idea to a *hierarchical* model of visual cortex: each level predicts the activity of the level below via descending generative connections; the ascending pathway carries the prediction-error residual. The framework explained extra-classical receptive-field effects (end-stopping, contextual suppression) as the V1-level prediction errors that remain after V2's contextual prediction has explained away the classical RF response. This was the founding paper of cortical predictive coding.

## 3. Variational generalization (2005, 2010)

Friston 2005 (`papers/friston2005_cortical_responses.md`) and Friston 2010 (`papers/friston2010_fep_unified_theory.md`) generalized Rao-Ballard from a specific estimation procedure to *variational free-energy minimization*. The free-energy framework provides:

- A principled probabilistic interpretation: prediction errors are gradients of a log-evidence approximation.
- *Precision weighting*: prediction errors are scaled by the inverse variance of the corresponding likelihood, making attention a natural part of the framework (`papers/feldman_friston2010_attention_free_energy.md`).
- *Active inference*: actions are selected to minimize expected future free energy, unifying perception and action.

Friston's framework subsumes Rao-Ballard as a special case (Gaussian likelihoods, point-estimate posteriors) and provides the variational foundation that PRISM's inner inference loop (`Prism/docs/THESIS.md` §2.11) is built on.

## 4. Microcircuit implementation (2012)

Bastos, Usrey, Adams, Mangun, Fries & Friston 2012 (`papers/bastos2012_canonical_microcircuits.md`) bridged Friston's framework to specific cortical microcircuits. Their canonical mapping:

- Superficial pyramidal cells (L2/3) code prediction errors, send feedforward gamma (30–80 Hz).
- Deep pyramidal cells (L5/L6) code predictions, send feedback alpha/beta (8–20 Hz).
- Neuromodulators (ACh, NA) implement precision weighting at the circuit level.

The paper made the framework *anatomically testable*: specific cell populations should show specific signatures.

## 5. Alternative implementations

Spratling 2008 (`papers/spratling2008_pc_biased_competition.md`) showed that the empirical signatures of Rao-Ballard — surround suppression, end-stopping, contextual modulation — can be reproduced by a divisive-normalization model with feedback, *without* explicit error neurons. This is important because it shows that the PC framework is not uniquely supported by the data; alternative architectures produce the same population-level phenomena.

Heeger 2017 proposed an alternative laminar mapping (L5 codes predictions, L4 codes errors). The empirical adjudication between Bastos and Heeger is ongoing.

Aitchison & Lengyel 2017 (`papers/aitchison_lengyel2017_pc_bayesian.md`) related PC to Bayesian inference more generally, characterizing when PC implements true Bayesian inference versus when it implements only approximate (variational) inference.

## 6. Cellular substrate (2013)

Larkum 2013 (`papers/larkum2013_apical_basal.md`) provided the cellular substrate that underlies the framework at the single-neuron level: the BAC mechanism (`concepts/apical_basal_dendritic_integration.md`) implements an AND-gate between basal (bottom-up) and apical (top-down) input in pyramidal cells. The cellular AND-gate is the biophysical foundation that the network-level Rao-Ballard architecture rests on.

Urbanczik & Senn 2014 (`papers/urbanczik_senn2014_predictive_dendrite.md`) gave a biologically-plausible local plasticity rule based on the same compartmental structure: apical dendrite predicts somatic spike rate, plasticity minimizes the discrepancy.

## 7. Modern empirical synthesis (2018)

Keller & Mrsic-Flogel 2018 (`papers/keller_mrsic_flogel2018_pc_review.md`) reviewed a decade of mouse-V1 closed-loop experiments that produced the cleanest single-cell evidence of prediction-error signals: mismatch responses in visuomotor experiments, expectation suppression for predictable stimuli, layer-specific patterns consistent with the Bastos microcircuit. The review argued that predictive processing is a *canonical* cortical computation — applying across cortices, not just to early sensory processing.

This was a meaningful step because it took the framework from "elegant theory consistent with the data" to "specific empirical signatures with confirmation in multiple labs."

## 8. Laminar macaque confirmation (2015)

Bastos et al. 2015 (`papers/bastos2015_laminar_macaque.md`) tested the 2012 microcircuit prediction directly with simultaneous laminar recordings in macaque V1, V2, V4. They confirmed the feedforward-gamma / feedback-alpha asymmetry. This is the strongest direct empirical evidence for the Bastos canonical-microcircuit framework.

## 9. Bayesian-dendritic interpretation (2023)

Jordan, Sacramento, Wybo, Petrovici & Senn 2023 (`papers/jordan2023_dendritic_bayesian.md`) formalized the cellular substrate as Bayes-optimal cue integration: apical dendrites encode priors, basal dendrites encode likelihoods, the soma computes the posterior. This was a normative justification for the multiplicative integration the framework needs — not just "the brain does this" but "Bayes says it should."

## 10. Deep-learning instantiations (2018, 2024)

Wen et al. 2018 (`papers/wen2018_deep_pc_networks.md`) trained deep predictive-coding networks on object recognition and found that they substantially underperformed standard supervised networks. Pinchetti et al. 2024 (`papers/pinchetti2024_benchmark_pc_networks.md`) systematically benchmarked PC networks and confirmed: the framework's theoretical elegance has not yet translated into competitive deep-learning models.

This is the major open empirical challenge for the framework: if predictive coding is the canonical cortical computation, scaling it up should produce competitive AI. So far it doesn't.

## 11. Current state (2024)

Shipp 2024 (`papers/shipp2024_visual_pc_computational.md`) and Pezzulo, Parr & Friston 2024 (`papers/pezzulo_parr_friston2024_active_inference.md`) review the current state. The framework is more empirically grounded than at any prior time, with specific cell populations identified, frequency signatures confirmed, and a unified active-inference extension that handles perception, action, and learning. The principal open challenges are: (a) scaling to competitive deep-learning performance; (b) resolving the laminar-mapping ambiguities (Bastos vs Heeger; explicit error neurons vs Spratling-style normalization); (c) integrating the framework with non-sensory cortical phenomena.

## 12. Implications for our work

The user's program (`threads/the_user_architectural_program.md`, `concepts/competition_emergent_predictive_coding.md`) accepts the architectural commitments of predictive coding — hierarchical generative model, descending predictions, ascending errors — and reframes the *motivation*. The conventional account says PC exists because predicting the sensory periphery is useful. The user's account says PC exists because predicting *competing coalitions* is a winning strategy under metabolic constraint. The two motivations are not mutually exclusive: sensory predictive coding is the special case where the "competitor" is the sensory periphery.

The user's contribution is therefore not a *replacement* of the predictive-coding framework but an *extension*: a new motivation that explains the framework's ubiquity beyond sensory cortex and makes specific empirical predictions (inter-hub anti-correlation; scaling with compute budget; ablation-sensitivity) that conventional PC does not make.

PRISM v1 and v2 are predictive-coding architectures in the Rao-Ballard tradition. The architectural commitments are conventional; the theoretical motivation is the user's reframing.

## Cross-references

- `concepts/hierarchical_predictive_coding` — the framework's architectural commitments.
- `concepts/apical_basal_dendritic_integration` — the cellular substrate.
- `concepts/precision_weighting_attention` — how attention fits into the framework.
- `concepts/competition_emergent_predictive_coding` — the user's reframing.
- `threads/the_user_architectural_program` — the user's broader program of which PC is one component.
