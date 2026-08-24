---
id: feedback_substrates
type: thread
title: "Anatomical and computational substrates of cortical feedback"
papers:
  - felleman_vanessen1991_hierarchical_cortex
  - rao_ballard1999_predictive_coding
  - bastos2012_canonical_microcircuits
  - bastos2015_laminar_macaque
  - larkum2013_apical_basal
  - larkum_zhu_sakmann1999_bac_firing
  - sherman_guillery2011_distinct_functions
  - sherman2022_ctc_loop
  - mckinnon_mo_sherman2025_transthalamic_v1
  - weiler2025_l6_corticocortical
  - keller_mrsic_flogel2018_pc_review
  - jordan2023_dendritic_bayesian
  - urbanczik_senn2014_predictive_dendrite
  - reynolds_heeger2009_normalization
  - perez2018_film
  - feldman_friston2010_attention_free_energy
concepts:
  - top-down-feedback
  - cortical-microcircuit-model
  - cortico-thalamo-cortical-loops
  - transthalamic-pathway
  - layer-6-corticocortical
  - apical-dendrite-coincidence-detection
  - precision-weighting
last_updated: "2026-05-13"
---

# Anatomical and computational substrates of cortical feedback

This thread maps the biological substrates by which cortical feedback is implemented — at the levels of anatomy, cellular biophysics, microcircuit, and macro-scale architecture — and shows how the user's Feedback Transformer is the network-level abstraction that captures the *computational* function these substrates collectively serve. The thread is the biological warrant for the architectural commitment that feedback should be multi-source, multiplicative, and gateable.

---

## 1. The hierarchical-anatomy framework (1991)

Felleman & Van Essen 1991 (`papers/felleman_vanessen1991_hierarchical_cortex.md`) established the laminar criterion for distinguishing feedforward from feedback corticocortical projections: ascending projections terminate in L4 and originate in supragranular layers; descending projections terminate outside L4 (in L1, L5, L6) and originate in infragranular layers. The criterion produced a hierarchy of 32 visual cortical areas in macaque, with explicit feedforward/feedback labels on every projection. The framework remains the standard reference for cortical-area hierarchies.

This framework is *anatomical*. It tells you which projection is feedback by where it terminates, but not what the feedback *computes*.

## 2. The functional reframing as prediction (1999)

Rao & Ballard 1999 (`papers/rao_ballard1999_predictive_coding.md`) gave feedback projections a functional role: they carry *predictions* of the lower-area activity. The architectural commitment turned the descending pathway from "modulatory feedback of unspecified content" into "the brain's hierarchical generative model." This is the Rao-Ballard reframing.

## 3. The cellular substrate: pyramidal-cell coincidence detection (1999, 2013)

Larkum, Zhu & Sakmann 1999 (`papers/larkum_zhu_sakmann1999_bac_firing.md`) showed that L5 pyramidal cells implement an AND gate between basal (bottom-up) and apical (top-down) input via the BAC mechanism. Larkum 2013 (`papers/larkum2013_apical_basal.md`) generalized this from a single-cell phenomenon to a cortex-wide architectural principle: the pyramidal cell is the cellular AND-gate for top-down and bottom-up evidence.

This is the cellular level at which "feedback" actually contacts "feedforward" in a single neuron. Apical-dendrite input from L1 (top-down feedback) and basal input near the soma (bottom-up feedforward) are integrated multiplicatively via the BAC coincidence detector.

Jordan et al. 2023 (`papers/jordan2023_dendritic_bayesian.md`) formalized this as Bayes-optimal cue integration (apical = prior, basal = likelihood, soma = posterior). Urbanczik & Senn 2014 (`papers/urbanczik_senn2014_predictive_dendrite.md`) gave the local plasticity rule. Together these establish the cellular substrate of feedback integration.

## 4. The microcircuit: laminar implementation (2012, 2015)

Bastos et al. 2012 (`papers/bastos2012_canonical_microcircuits.md`) mapped the Rao-Ballard / Friston framework onto a canonical cortical microcircuit:

- Superficial pyramidal cells (L2/3) code prediction *errors* (feedforward gamma).
- Deep pyramidal cells (L5/L6) code *predictions* (feedback alpha/beta).
- Precision weighting via cholinergic and noradrenergic neuromodulation.

Bastos et al. 2015 (`papers/bastos2015_laminar_macaque.md`) confirmed the feedforward-gamma / feedback-alpha asymmetry with simultaneous laminar recordings in macaque V1, V2, V4. The microcircuit framework therefore has direct empirical support.

## 5. The two anatomical routes: direct corticocortical and transthalamic (2011, 2022, 2025)

Long-range cortical feedback is implemented via two parallel substrates:

**Direct corticocortical pathway.** Weiler, Teichert & Margrie 2025 (`papers/weiler2025_l6_corticocortical.md`) showed that excitatory layer-6 corticocortical (L6 CC) cells are a major route for both intra- and inter-hemispheric feedback. The L6 CC contribution is *especially* large for feedback projections to primary sensory cortex.

**Transthalamic pathway.** Sherman & Guillery 2011 (`papers/sherman_guillery2011_distinct_functions.md`) proposed and Miller-Hansen & Sherman 2022 (`papers/sherman2022_ctc_loop.md`) verified that corticocortical communication is *also* implemented via a transthalamic loop: L5 cells in cortex A drive higher-order thalamic neurons (pulvinar, posterior medial nucleus), which project back to cortex A or forward to cortex B. The thalamus-to-target synaptic properties depend on direction: feedforward transthalamic = driver, feedback transthalamic = modulator.

McKinnon, Mo & Sherman 2025 (`papers/mckinnon_mo_sherman2025_transthalamic_v1.md`) provides the causal evidence: optogenetic suppression of the V1→pulvinar driver impairs visual discrimination, showing that the transthalamic loop is functionally necessary for cortical processing.

The two substrates are not redundant. They have different functional properties (driver/modulator), different gating (thalamic state-dependent for transthalamic; not for direct), and probably carry partially different information. Real cortex therefore implements *parallel feedback substrates*, anatomically distinct, functionally complementary.

## 6. The empirical signatures (2018)

Keller & Mrsic-Flogel 2018 (`papers/keller_mrsic_flogel2018_pc_review.md`) reviewed the empirical signatures of feedback in mouse V1: mismatch responses for unpredicted visuomotor pairings, expectation suppression for predictable stimuli, layer-specific patterns consistent with the Bastos microcircuit. These are the empirical signatures by which feedback can be detected in single-cell or population recordings.

## 7. The computational analogs in AI

Three architectural primitives in modern AI capture aspects of cortical feedback:

- **Multiplicative gain modulation** (Reynolds & Heeger 2009, `papers/reynolds_heeger2009_normalization.md`): feedback as divisive normalization with multiplicative gain. The biophysical correlate is dendritic integration with conductance-based gain.
- **FiLM** (Perez et al. 2018, `papers/perez2018_film.md`): feature-wise linear modulation. Feedback conditioning produces per-channel scale and shift parameters applied to feedforward features. Used in PRISM v1 and v2.
- **Cross-attention / self-attention with feedback** (Vaswani 2017 and successors; the user's Feedback Transformer generalizes this): feedback as additional queries/keys/values integrated into the attention map. The user's program commits to multiplicative broadcasting before softmax.

## 8. Synthesis: what feedback is for

The collection of substrates suggests feedback serves several distinct computational functions:

| Function | Substrate(s) | Computational interpretation |
|---|---|---|
| Predictions of lower-level activity | L5/L6 → L1 corticocortical; pulvinar modulator output | Rao-Ballard generative model |
| Multi-source integration | L6 CC + transthalamic + lateral; apical dendritic AND-gate | Bayesian cue combination |
| Precision weighting / attention | SST+/VIP+ inhibitory gating of apical input; neuromodulators | Reliability-weighted gain on prediction errors |
| Context modulation | PFC → sensory cortex feedback | Task-conditional gain on sensory processing |
| Inter-area binding | Synchrony in feedback frequency bands (alpha/beta) | Coordinated representations across areas |

The user's Feedback Transformer (`concepts/feedback_transformer.md`) is the architectural primitive that aims to support all of these functions in a single computational mechanism: multi-source feedback integrated multiplicatively at the level of self-attention, with learned gating (per-source gates allowing the system to silence feedback that doesn't help).

## 9. Implications for the user's program

The user's commitment to multi-source feedback in the Feedback Transformer is biologically warranted by:

- **Weiler 2025**: real cortex has many feedback sources at every level.
- **Sherman 2022 + McKinnon 2025**: real cortex has parallel direct and transthalamic feedback substrates.
- **Larkum 2013 + Jordan 2023**: real cortex integrates feedback multiplicatively with bottom-up input at the cellular level.
- **Bastos 2012 + 2015**: real cortex separates feedforward and feedback into distinct frequency bands, supporting a directional asymmetry in computational role.
- **Keller-Mrsic-Flogel 2018**: real cortex shows the mismatch and expectation-suppression signatures predicted by the framework.

The biological case for the user's architectural commitments is therefore strong. The architectural commitments are not arbitrary choices; they are the network-level analogs of well-documented biological substrates.

## Cross-references

- `concepts/feedback_transformer` — the AI primitive.
- `concepts/apical_basal_dendritic_integration` — the cellular substrate.
- `concepts/cortico_thalamo_cortical_loops` — the transthalamic substrate.
- `concepts/hierarchical_predictive_coding` — the framework that gives feedback its computational role.
- `concepts/bidirectional_hierarchical_feedback` — the user's architectural commitment to cross-layer feedback.
