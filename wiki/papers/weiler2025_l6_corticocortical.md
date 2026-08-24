---
id: weiler2025_l6_corticocortical
title: "Layer 6 corticocortical neurons are a major route for intra- and interhemispheric feedback"
authors:
  - "Weiler, Simon"
  - "Teichert, Manuel"
  - "Margrie, Troy W."
year: 2025
venue: "eLife"
doi: "10.7554/eLife.100478"
arxiv: ""
url: "https://doi.org/10.7554/eLife.100478"
tags:
  - primate-neurophysiology
  - cortical-anatomy
concepts:
  - top-down-feedback
  - cortical-microcircuit-model
  - layer-6-corticocortical
  - feedback-transformer
  - apical-basal-dendritic-integration
related:
  - bastos2012_canonical_microcircuits
  - felleman_vanessen1991_hierarchical_cortex
  - larkum2013_apical_basal
  - sherman2022_ctc_loop
  - mckinnon_mo_sherman2025_transthalamic_v1
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-18"
---

# Layer 6 corticocortical neurons are a major route for intra- and interhemispheric feedback

## 1. Abstract

The neocortex comprises anatomically discrete yet interconnected areas that are symmetrically located across the two hemispheres. Determining the logic of these macrocircuits is necessary for understanding high-level brain function. In mice, the authors mapped the areal and laminar organization of the ipsi- and contralateral cortical projection onto the primary visual, somatosensory, and motor cortices. Although the ipsilateral hemisphere is the primary source of cortical input, there is substantial contralateral symmetry regarding the relative contribution and areal identity of input. Laminar analysis of input areas shows that excitatory layer 6 corticocortical cells (L6 CCs) are a major projection pathway within and between the two hemispheres. Analysis of the relative contribution of inputs from supra- (feedforward) and infragranular (feedback) layers reveals that contra-hemispheric projections reflect a dominant feedback organization compared to their ipsi-cortical counterpart. The magnitude of the interhemispheric difference in hierarchy is largest for sensory and motor projection areas due to a proportional increase in input from L6 neurons. L6 CCs therefore not only mediate long-range cortical communication but also reflect its inherent feedback organization.

## 2. Why this matters for us

This is the biological substrate of the Feedback Transformer's central commitment — that cortical processing routinely integrates feedback from many sources (parallel and hierarchical, intra- and inter-hemispheric) into single sensory-processing stages. The user's Evolution of Architecture document explicitly invokes Weiler 2025 as the rationale for the multi-source feedback design (Layer 6 CCs as the route for the kind of integration the Feedback Transformer formalizes computationally). The paper turns a long-standing anatomical claim ("cortex has lots of feedback") into a quantitative one with a specific laminar address: L6 corticocortical projections, not L5 or L2/3, are the dominant interhemispheric route, and they reflect a feedback-dominated hierarchy.

## 3. Key claims

1. The ipsilateral hemisphere supplies most cortical input to V1, S1, and M1, but the contralateral hemisphere makes substantial, symmetric contributions; the same set of areas projects on both sides.
2. Laminar analysis of the projecting cells shows that excitatory layer 6 corticocortical (L6 CC) cells are a major source of long-range cortical projections — both intra- and inter-hemispheric.
3. The ratio of supragranular (feedforward, Felleman & Van Essen-style) to infragranular (feedback) input is shifted toward feedback for contralateral projections compared to ipsilateral projections, in agreement with the standard feedforward/feedback laminar criterion.
4. The interhemispheric feedback bias is largest for primary sensory (V1, S1) and motor (M1) target areas, and the increase is specifically driven by a higher proportional contribution from L6 neurons, not L5 or L2/3.
5. L6 CCs therefore have a dual role: they (a) carry long-range cortical communication and (b) bias that communication toward a feedback-style organization, providing an anatomical implementation of cross-area and cross-hemispheric feedback predicted by predictive-coding and biased-competition frameworks.

## 4. Methods

The authors mapped cortical inputs to three primary areas (V1, S1, M1) in mice using retrograde tracers and a viral whole-brain input-mapping strategy. They quantified, for each input area, both the *intensity* (number of labeled cells) and *laminar distribution* (proportion in L2/3 vs L5 vs L6) of projections onto V1, S1, and M1. Inputs were partitioned by hemisphere (ipsi- vs contralateral) and by anatomical category (sensory, motor, frontal, medial, lateral). A "feedback index" was computed from the ratio of infragranular (L5+L6) to supragranular (L2/3) labeled cells, following the Felleman & Van Essen 1991 laminar criterion.

## 5. Results

Quantitatively, the contralateral hemisphere supplies a substantial fraction of total cortical input to V1 (roughly comparable in identity to ipsilateral, smaller in magnitude). The laminar profile of contralateral projections is shifted toward L6 compared to ipsilateral projections from the same areas — L6 cells contribute a higher proportion of cells in contralateral than ipsilateral projections. The feedback-index difference between hemispheres is largest for sensory (V1, S1) and motor (M1) target areas, and is driven by L6 proportional increase rather than L5 or L2/3. Frontal, medial, and lateral target areas show smaller hemispheric asymmetry in the feedback index. The L6 CC population is therefore both quantitatively major and qualitatively shifted toward feedback relative to other excitatory pyramidal populations contributing to long-range cortical communication.

## 6. Critique / limitations

The data are anatomical: cell-counting and laminar-distribution measurements quantify *who projects where*, not what those projections compute. The "feedback" designation rests on the Felleman & Van Essen 1991 supragranular-vs-infragranular criterion, which is itself a proxy for functional feedback rather than direct evidence. The paper does not show, e.g., that suppressing L6 CC projections specifically impairs predictive-coding-like top-down influences (that would require targeted optogenetic inactivation paired with behavior — c.f. McKinnon, Mo & Sherman 2025).

The results are in mouse cortex; extrapolation to primate cortex (where Felleman & Van Essen's original criterion was developed) is plausible but not demonstrated. Mouse cortex has different relative cell-class proportions and a less elaborated supragranular layer than primate cortex; the magnitude of the L6 contribution may differ.

The laminar criterion treats "feedback" as a binary category, but real cortical feedback is graded and has multiple subtypes (driver vs modulator; Sherman & Guillery 2011). The paper does not distinguish these subtypes within the L6 CC population, so the functional heterogeneity inside "L6 feedback" is collapsed.

The paper does not directly address inter-hemispheric *timing* — whether L6 CC feedback arrives before, with, or after local L2/3 processing. This timing is the operational signature of feedback in predictive-coding models.

## 7. Connection to our work

This is the load-bearing biological motivation for the Feedback Transformer (`concepts/feedback_transformer.md`, [threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1). The Feedback Transformer is the computational primitive that integrates arbitrary recurrent feedback sources into self-attention; Weiler 2025 establishes that real cortex routinely does the *anatomical* analog of this — a single cortical area receives feedback projections from many other areas (both hemispheres), and the dominant route is a specific cell class (L6 CCs).

Specifically:

- **Multiple feedback sources at one node.** The Feedback Transformer integrates an arbitrary number of recurrent states ($C_i$) into a single self-attention layer. Weiler shows that V1, S1, and M1 each receive projections from a *bilateral, multi-area* set of source regions, with L6 CCs being a major contributor. The Feedback Transformer's multi-source structure is therefore anatomically warranted — cortex doesn't just integrate one feedback source per layer.
- **Feedback as a distinguished class.** The paper's quantification of the supragranular/infragranular ratio supports treating top-down feedback as architecturally distinct from feedforward signals. PRISM v2 makes this commitment explicit: the slow-FiLM pathway from $M^{\text{slow}}_{t-1}$ is anatomically modeled on the L6 CC feedback projection ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.4 — top-down modulation injected at the input to the V1 stage).
- **Diminishing feedback to deeper layers.** Weiler reports the L6 feedback bias is largest for *primary* sensory and motor areas (V1, S1, M1). This is consistent with the user's architectural commitment ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3) that shallower memory layers receive feedback from many sources while deeper layers receive feedback from few — primary cortices are the deepest "consumers" of feedback in Weiler's data.

The recurrent-ViT paper (2502.10955) does not invoke L6 CCs explicitly, but the Feedback Transformer generalization in the user's notes is the architectural primitive Weiler's anatomy directly motivates. Any future manuscript that extends the recurrent ViT to multi-source feedback should cite Weiler 2025 as the biological warrant.

## 8. Citations to follow

- `felleman_vanessen1991_hierarchical_cortex` — the original laminar feedforward/feedback criterion. Already in seed.
- `sherman2022_ctc_loop` — the transthalamic feedback pathway (Miller-Hansen & Sherman 2022), a complementary route to direct cortico-cortical L6 CC feedback. In seed, full depth in this session.
- `larkum2013_apical_basal` — the cellular mechanism by which L6/L5 apical-dendrite feedback is integrated at the pyramidal-cell level. In seed, full depth.
- `harris_shepherd2015_cortical_neuron` — modern review of cortical cell-class taxonomy (L2/3, L4, L5IT/PT, L6 CT/CC). Not in seed.
- `markov_kennedy2014_consensus_macaque` — quantitative connectivity matrix of macaque cortex; primate analog of Weiler's mouse data. Not in seed.
- `mckinnon_mo_sherman2025_transthalamic_v1` — optogenetic inactivation of L5→pulvinar→V1 transthalamic circuit, showing causal role in visual discrimination. In seed, full depth but a natural companion to Weiler.
