---
id: hierarchical_predictive_coding
type: concept
title: "Hierarchical predictive coding"
papers:
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - bastos2012_canonical_microcircuits
  - keller_mrsic_flogel2018_pc_review
  - shipp2024_visual_pc_computational
  - spratling2008_pc_biased_competition
  - feldman_friston2010_attention_free_energy
  - clark2013_whatever_next
  - aitchison_lengyel2017_pc_bayesian
  - wen2018_deep_pc_networks
  - pinchetti2024_benchmark_pc_networks
  - srinivasan1982_predictive_coding_retina
  - friston2005_cortical_responses
  - pezzulo_parr_friston2024_active_inference
  - bastos2015_laminar_macaque
  - dosovitskiy2020_vit
  - felleman_vanessen1991_hierarchical_cortex
  - jordan2023_dendritic_bayesian
  - larkum2013_apical_basal
source_documents:
  - "Prism/docs/THESIS.md (§ 1.3, 2.5–2.8)"
  - "PrismV2/docs/PRISM_V2_PROPOSAL.md (§ 3.10)"
last_updated: "2026-05-16"
---

# Hierarchical predictive coding

## Definition

A computational framework in which the cortex (or any hierarchical generative system) is modeled as a stack of layers, with each layer $\ell$ maintaining an internal estimate of latent causes that *predicts* the activity of the level below it, and the *residual prediction error* propagating upward to update the higher-level estimate. The defining commitments are:

1. **Descending predictions.** Each layer $\ell$ projects a top-down prediction $\hat r_\ell = g_\ell(r_{\ell+1})$ to the level below, via a learned generative decoder $g_\ell$.
2. **Ascending errors.** The ascending pathway from $\ell-1$ to $\ell$ carries the prediction-error residual $\epsilon_{\ell-1} = r_{\ell-1} - \hat r_{\ell-1}$, not the raw activity.
3. **State update.** The internal estimate $r_\ell$ is updated by gradient descent (or its inference-network amortization) on a free-energy-like loss that combines the level-below error and a prior on $r_\ell$: $r_\ell \leftarrow r_\ell + \eta\, U_\ell^\top \epsilon_{\ell-1} - \eta\, g'(r_\ell)$.

The framework was introduced as a theoretical reframing of feedforward visual processing by Rao & Ballard 1999 (`papers/rao_ballard1999_predictive_coding.md`), generalized to a full variational-Bayes framework by Friston (`papers/friston2010_fep_unified_theory.md`), mapped onto cortical microcircuits by Bastos et al. 2012 (`papers/bastos2012_canonical_microcircuits.md`), and reviewed empirically by Keller & Mrsic-Flogel 2018 (`papers/keller_mrsic_flogel2018_pc_review.md`) and Shipp 2024 (`papers/shipp2024_visual_pc_computational.md`).

## Why the framework is hierarchical

A single-level predictive-coding model can explain end-of-pipeline error signals but cannot explain why the cortex has many functional levels (V1 → V2 → V4 → IT) with the same internal structure repeated at each. The hierarchical extension says: each level both *generates predictions* for the level below and *receives errors* from it. Cross-level recursion gives the model the depth-of-hierarchy structure that biological vision (Felleman & Van Essen 1991, `papers/felleman_vanessen1991_hierarchical_cortex.md`) and modern deep nets (`papers/dosovitskiy2020_vit.md`) both exhibit.

## Cellular and laminar implementation

Bastos et al. 2012 propose a specific mapping onto cortical microcircuits:

| Computational role | Anatomical population | Frequency band |
|---|---|---|
| Prediction errors | Superficial pyramidal cells (L2/3) | Feedforward gamma (30–80 Hz) |
| Predictions | Deep pyramidal cells (L5/L6) | Feedback alpha/beta (8–20 Hz) |
| Precision weighting | Cholinergic / noradrenergic neuromodulation on L2/3 | — |

This mapping was tested experimentally by Bastos et al. 2015 (`papers/bastos2015_laminar_macaque.md`), which confirmed the feedforward-gamma / feedback-alpha asymmetry in macaque laminar recordings.

Larkum 2013 (`papers/larkum2013_apical_basal.md`) provides the cellular substrate at the single-neuron level: pyramidal cells integrate basal (bottom-up) and apical (top-down) input via the BAC mechanism, producing distinctive burst output when the two coincide. Jordan et al. 2023 (`papers/jordan2023_dendritic_bayesian.md`) formalizes this as Bayes-optimal cue integration — apical = prior, basal = likelihood, soma = posterior.

## Empirical signatures

The framework predicts that cortical activity should show:

- **Mismatch responses.** Cells respond more strongly to unexpected stimuli than to expected ones (because the unexpected stimulus produces a large prediction error). Confirmed in mouse V1 closed-loop experiments (Keller et al. 2012, Attinger et al. 2017; reviewed in Keller & Mrsic-Flogel 2018).
- **Expectation suppression.** Stimuli preceded by a valid predictive cue elicit weaker responses. Confirmed in macaque V1, V4, and IT.
- **Precision-weighted gain modulation.** When the predictive cue's reliability is varied, V1 responses scale in a manner consistent with reliability-weighted prediction-error pathways. Confirmed in attention paradigms (Feldman & Friston 2010, `papers/feldman_friston2010_attention_free_energy.md`).
- **Laminar frequency separation.** Feedforward signaling is gamma-band; feedback is alpha/beta. Confirmed in macaque laminar recordings (Bastos et al. 2015).
- **Altered prediction-error processing in disease.** Schizophrenia and autism show characteristic alterations in prediction-error magnitude and precision weighting, consistent with the framework's predictions.

## Alternative implementations

The Rao-Ballard architecture is not the unique implementation of predictive-coding-consistent dynamics. Major alternatives:

- **Spratling 2008** (`papers/spratling2008_pc_biased_competition.md`): A divisive-normalization model with feedback that reproduces the extra-classical receptive-field effects Rao-Ballard explains, without explicit error neurons. The empirical signatures of predictive coding can therefore be reproduced by a non-PC architecture.
- **Heeger 2017**: An alternative laminar mapping in which L5 codes predictions and L4 codes errors (without an L2/3 error role).
- **Friston 2010** (`papers/friston2010_fep_unified_theory.md`): Generalizes Rao-Ballard from least-squares estimation to variational Bayes; introduces precision weighting and active inference.
- **Wen et al. 2018, Pinchetti et al. 2024**: Deep neural network instantiations. Both show that deep PC networks under-perform standard supervised deep nets on object recognition, suggesting that the framework's elegance has not yet translated into competitive empirical models.

The empirical adequacy of predictive coding as a framework therefore depends on which specific implementation is endorsed; the framework is robust at the level of "the cortex implements hierarchical Bayesian inference with descending predictions and ascending errors," more contested at the level of specific cell-type assignments.

## Connection to PRISM

PRISM v1 (`Prism/docs/THESIS.md`) is, by explicit construction, a Rao-Ballard predictive-coding model: a feedforward feature encoder (V1 stem), a top-down generative decoder, a prediction-error pathway, and a recurrent state-update mechanism. PRISM v2 (`PrismV2/docs/PRISM_V2_PROPOSAL.md` §3.10) extends to two hierarchical levels with cross-level error and prediction flow — the canonical "closing the loop" form.

The user's program's *theoretical* extension — competition-emergent predictive coding (`concepts/competition_emergent_predictive_coding.md`) — reframes the descending predictions as predictions of *competing coalitions* rather than of sensory input. This is a substantive theoretical departure that retains the architecture's computational structure but changes what the prediction errors *mean*.

## Connection to other concepts

- `feedback_transformer` — the multi-source generalization of top-down prediction injection.
- `multi_compartmental_memory` — the multi-level state stack a hierarchical PC architecture needs.
- `bidirectional_hierarchical_feedback` — the cross-level routing of predictions and errors.
- `apical_basal_dendritic_integration` — the cellular substrate at the single-neuron level.
- `cortical_microcircuit_model` — Bastos's laminar mapping.
- `precision_weighting_attention` — attention as gain on prediction-error pathways.
- `competition_emergent_predictive_coding` — the user's reframing of why cortex is predictive.

## Open questions

1. **Are explicit prediction-error neurons real?** Optogenetic tagging of L2/3 cells as "prediction-error neurons" would settle this; current evidence is correlative.
2. **Why do deep PC networks under-perform supervised deep nets?** If the framework is empirically right, scaling should help; it doesn't yet.
3. **What is the relationship between hierarchical PC and biased competition?** Spratling 2008 argues they are equivalent at the population level; the user's competition-emergent thesis claims biased competition is the underlying optimization pressure.
4. **Precision weighting: neuromodulator or local circuit?** The Bastos 2012 framework places precision weighting on neuromodulators; alternatives place it on local SST+/VIP+ inhibitory circuitry (consistent with Larkum's BAC gating).
