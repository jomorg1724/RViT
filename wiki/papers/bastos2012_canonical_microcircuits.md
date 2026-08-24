---
id: bastos2012_canonical_microcircuits
title: "Canonical microcircuits for predictive coding"
authors:
  - "Bastos, Andre M."
  - "Usrey, W. Martin"
  - "Adams, Rick A."
  - "Mangun, George R."
  - "Fries, Pascal"
  - "Friston, Karl J."
year: 2012
venue: "Neuron"
doi: "10.1016/j.neuron.2012.10.038"
arxiv: ""
url: "https://doi.org/10.1016/j.neuron.2012.10.038"
tags:
  - predictive-coding
  - cortical-anatomy
  - review
  - theoretical-essay
concepts:
  - hierarchical-predictive-coding
  - rao-ballard-coding
  - cortical-microcircuit-model
  - prediction-error-map
  - top-down-feedback
  - apical-basal-dendritic-integration
  - bidirectional-hierarchical-feedback
  - feedback-transformer
related:
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - keller_mrsic_flogel2018_pc_review
  - felleman_vanessen1991_hierarchical_cortex
  - larkum2013_apical_basal
  - bastos2015_laminar_macaque
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Canonical microcircuits for predictive coding

## 1. Abstract

This Perspective considers the influential notion of a canonical (cortical) microcircuit in light of recent theories about neuronal processing. The authors reconcile quantitative studies of microcircuitry with the functional logic of neuronal computations. They revisit the established idea that message passing among hierarchical cortical areas implements a form of Bayesian inference — paying careful attention to the implications for intrinsic connections among neuronal populations. By deriving canonical forms for these computations, one can associate specific neuronal populations with specific computational roles. This analysis discloses a correspondence between the microcircuitry of the cortical column and the connectivity implied by predictive coding, and provides intuitive insights into the functional asymmetries between feedforward and feedback connections and the characteristic frequencies over which they operate.

## 2. Why this matters for us

Bastos et al. 2012 is the bridge between the abstract Rao-Ballard / Friston framework and a *specific* anatomically-constrained microcircuit implementation. The paper assigns specific layer populations to the prediction and error roles, and derives a frequency signature (gamma feedforward, alpha/beta feedback) that has become the empirical workhorse of testing predictive coding in primates. PRISM v2's commitment to a two-level cortical hierarchy with cross-level error and prediction flow ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10) is built on this microcircuit template.

## 3. Key claims

1. The canonical cortical microcircuit (Douglas & Martin 1991, 2004) and the connectivity implied by predictive coding under hierarchical Bayesian inference correspond at a specific level of detail: both posit distinct excitatory populations in superficial vs deep layers with specific intrinsic and extrinsic connectivity rules.
2. **Superficial pyramidal cells (L2/3) code prediction errors.** They receive forward input from L4 (via L2/3 stellate cells) and feedback inhibition gated by descending predictions. Their outputs project forward up the hierarchy.
3. **Deep pyramidal cells (L5/L6) code predictions.** They send descending feedback to lower areas. Their activity represents the current best estimate of latent causes at this hierarchical level.
4. **Frequency signature.** Feedforward signaling (prediction errors, L2/3 → next-area L4) is biased toward gamma-band oscillations (~30–80 Hz). Feedback signaling (predictions, L5/L6 → previous-area L1/L5) is biased toward alpha/beta-band oscillations (~8–30 Hz). This frequency asymmetry has been confirmed by laminar recordings in macaque (e.g., Buffalo et al. 2011; Bastos's own subsequent work).
5. **Precision weighting via classical neuromodulators.** Acetylcholine (ACh) and noradrenaline (NA) modulate the gain of prediction-error pathways (postsynaptic excitability of L2/3 cells), effectively implementing precision weighting on a circuit-level rather than at the level of explicit gain factors in equations.

## 4. Methods

A theoretical/synthesis paper. The authors derive a generative model in which each cortical level $i$ predicts the activity of level $i-1$ via descending connections, and the residual error is propagated upward via ascending connections. They then map this onto the canonical-microcircuit anatomy by aligning the equations of belief propagation onto specific cell populations and connection patterns. The mapping is derivational rather than empirical — the paper asks "if predictive coding is implemented in cortex, where would each computation live?" and answers via the structure of the equations.

The frequency-signature predictions are derived from the time constants of the corresponding equations and from the established differential frequency content of superficial vs deep cortical layers in laminar recordings.

## 5. Results

The principal *predictions* (not experimental results — this is a theoretical paper):

- L2/3 pyramidal cells should show the empirical signatures of prediction-error neurons: increased response to unexpected stimuli, decreased response to expected stimuli, gamma-band signaling to the next cortical area.
- L5/L6 pyramidal cells should show the empirical signatures of representation neurons: sustained activity reflecting the current best estimate, descending alpha/beta-band signaling to the previous cortical area.
- Inhibitory cell populations (PV+, SST+) implement the gain-control and gating functions: descending predictions modulate the inhibition of L2/3 cells, suppressing the prediction-error response for expected stimuli.
- Cross-area coherence in gamma (feedforward) and alpha/beta (feedback) is the macro-level signature of these microcircuit predictions and should be observable in simultaneous laminar recordings from connected areas.
- Disorders of cortical function with abnormal prediction-error processing (schizophrenia, autism) should show altered laminar-frequency signatures.

Subsequent experimental work (notably Bastos's own 2015 *Neuron* paper with laminar macaque recordings) has confirmed several of these predictions, particularly the feedforward-gamma / feedback-alpha frequency asymmetry.

## 6. Critique / limitations

The mapping of prediction vs error to specific layer populations is *one* among several possible mappings. Heeger 2017 proposed an alternative in which L5 codes predictions and L4 codes errors (without the L2/3-error role); Spratling's biased-competition framework reproduces many of the same empirical effects without explicit error neurons at all. The Bastos mapping is a leading proposal but not the unique one consistent with the data.

The frequency signature, while empirically supported in macaque, has been called into question in some experimental conditions and species. The mapping of "feedforward = gamma" and "feedback = alpha/beta" may be coarser than the data support; some studies find substantial feedback-direction gamma in specific behavioral contexts.

The paper does not engage seriously with deep-learning implementations of predictive coding or with the practical challenge that PC networks have so far underperformed standard supervised deep nets on object recognition (Wen et al. 2018; Pinchetti et al. 2024). The derivational elegance of the framework has not yet translated into competitive empirical models.

The microcircuit mapping is for primate cortex (specifically based on the Douglas-Martin canonical microcircuit). Rodent cortex has different relative layer thicknesses and somewhat different intrinsic connectivity; the Bastos mapping may need modification for mouse-V1 predictive-coding implementations (Keller & Mrsic-Flogel 2018 partially addresses this).

## 7. Connection to our work

Bastos 2012 is the architectural template for PRISM v2's two-level structure ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10). The specific correspondences:

- **Layer 1 of PRISM v2 ↔ V1 microcircuit.** The fast memory state $M^{\text{fast}}$ (12×12 patch grid, V1 features) and its associated prediction-error pathway $E_{V_1}$ map onto Bastos's V1 microcircuit: L4 ↔ feedforward sensory input; L2/3 ↔ prediction-error neurons; L5/6 ↔ representation neurons (with $M^{\text{fast}}$ as the current best estimate).
- **Layer 2 of PRISM v2 ↔ V2 microcircuit.** The slow memory state $M^{\text{slow}}$ (6×6 patch grid, V2 features) and its associated prediction-error pathway $E_{V_2}$ map onto Bastos's V2 microcircuit, one hierarchical level up.
- **Cross-level error and prediction flow.** PRISM v2's ascending error pathway ($E_{V_1}$ feeds into $M^{\text{slow}}$ update) ↔ Bastos's L2/3 → next-area-L4 feedforward route. PRISM v2's descending prediction pathway (slow-FiLM modulation of V1 features) ↔ Bastos's L5/L6 → previous-area-L1 feedback route.
- **Frequency separation as slow-fast timescales.** Bastos's feedforward-gamma / feedback-alpha distinction maps onto PRISM v2's update-gate bias asymmetry ($b_u^{\text{fast}} = -1$ for fast memory, $b_u^{\text{slow}} = -3$ for slow memory). The fast memory's frequent updates (~27% per step) capture the gamma feedforward timescale; the slow memory's rare updates (~5% per step) capture the alpha/beta feedback timescale.

PRISM v1 ([Prism/docs/THESIS.md](Prism/docs/THESIS.md)) is single-level and therefore can be read as one half of Bastos's two-level mapping. PRISM v2 closes the loop and is the most faithful implementation of the Bastos canonical microcircuit in the user's program. The Feedback Transformer ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1) further generalizes this to multi-area feedback at every level — Bastos provides the two-area-pair template; the Feedback Transformer scales it to N areas.

Any manuscript that extends the recurrent ViT into a multi-level predictive-coding architecture should cite Bastos 2012 as the canonical microcircuit reference, alongside Rao & Ballard 1999 (the foundation), Friston 2010 (the variational framework), and Keller & Mrsic-Flogel 2018 (the modern empirical anchor).

## 8. Citations to follow

- `bastos2015_laminar_macaque` — Bastos's own follow-up with laminar macaque recordings testing the feedforward-gamma / feedback-alpha prediction. In seed, full depth.
- `douglas_martin2004_canonical_microcircuit` — the original Douglas-Martin canonical microcircuit. Not in seed.
- `markov_kennedy2014_consensus_macaque` — quantitative cortical connectivity matrix in macaque. Not in seed.
- `buffalo2011_laminar_alpha_gamma` — early empirical evidence of laminar frequency separation. Not in seed.
- `heeger2017_alternative_pc` — alternative L4/L5 mapping. Not in seed.
- `larkum2013_apical_basal` — the cellular mechanism for prediction-error integration at the pyramidal-cell level. In seed, full depth.
- `keller_mrsic_flogel2018_pc_review` — modern empirical review. In seed, full depth.
