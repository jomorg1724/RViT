---
id: sherman2022_ctc_loop
title: "Conserved patterns of functional organization between cortex and thalamus in mice"
authors:
  - "Miller-Hansen, Andrew J."
  - "Sherman, S. Murray"
year: 2022
venue: "PNAS"
doi: "10.1073/pnas.2201481119"
arxiv: ""
url: "https://doi.org/10.1073/pnas.2201481119"
tags:
  - primate-neurophysiology
  - cortical-anatomy
  - subcortical
concepts:
  - cortico-thalamo-cortical-loops
  - transthalamic-pathway
  - top-down-feedback
  - feedback-transformer
related:
  - weiler2025_l6_corticocortical
  - bastos2012_canonical_microcircuits
  - felleman_vanessen1991_hierarchical_cortex
  - mckinnon_mo_sherman2025_transthalamic_v1
  - sherman_guillery2011_distinct_functions
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Conserved patterns of functional organization between cortex and thalamus in mice

> **Identity note.** The user's notes cite "Sherman (2022) — Functions of the cortico-thalamo-cortical loop." Within Sherman's 2022 output, the canonical functional-organization paper is this one (Miller-Hansen & Sherman, PNAS 2022). It is the best-matching paper for the user's intended citation; future revisions should confirm against the user's original source. The id `sherman2022_ctc_loop` is preserved per the no-rename rule.

## 1. Abstract

Higher-order thalamic nuclei contribute to sensory processing via projections to primary and higher cerebral cortical areas, but it is unknown which of their cortical and subcortical inputs contribute to their distinct output pathways. The authors used subpopulation-specific viral strategies in mice to anatomically and physiologically dissect pathways of the higher-order thalamic nuclei of the somatosensory and visual systems (the posterior medial nucleus and pulvinar). Using complementary optogenetics and electrical stimulation, they show that synapses in cortex from higher-order thalamus have functionally divergent properties in primary vs. higher cortical areas. Higher-order thalamic projections onto excitatory targets in S1 and V1 are weakly modulatory, while projections to S2 and higher visual areas are strong drivers of postsynaptic targets. Then, using transsynaptic tracing verified by optogenetics, they show that posterior-medial cells projecting to S1 are driven by L5 neurons in S1, S2, and M1, and that pulvinar cells projecting to V1 are driven by L5 neurons in V1 and higher visual areas. Therefore, in both systems, L5 of primary and higher cortical areas drives transthalamic feedback modulation of primary sensory cortex through higher-order thalamus. The results support the hypothesis that direct corticocortical projections are paralleled by transthalamic pathways, even in the feedback direction, with feedforward transthalamic pathways acting as drivers and feedback through thalamus acting as modulators.

## 2. Why this matters for us

This paper supplies the second of the two major feedback substrates the user's program rests on. Where Weiler 2025 establishes the direct L6 corticocortical feedback route, Miller-Hansen & Sherman 2022 establishes the parallel *transthalamic* route — L5 → higher-order thalamus → cortical area. Crucially, the two routes have different functional signatures: transthalamic feedback projections to primary cortex are *modulatory* (weak, non-driving), in contrast to the driver projections that go to higher cortical areas. This is precisely the functional asymmetry that PRISM v2's slow-FiLM modulation captures: top-down feedback to V1 should *modulate* feedforward processing rather than dictate it. Sherman's "driver vs modulator" distinction is the empirical foundation for that architectural choice.

## 3. Key claims

1. Higher-order thalamic nuclei (posterior medial, pulvinar) receive driving input from cortical L5 cells across multiple areas, including the same primary cortex they project back to (V1→pulvinar→V1; S1→PoM→S1) and from higher cortical areas (S2→PoM, higher visual→pulvinar).
2. Higher-order thalamic projections back to *primary* sensory cortex (S1, V1) are functionally *modulatory* — they cause subthreshold, non-driving postsynaptic responses.
3. Higher-order thalamic projections to *higher* cortical areas (S2, higher visual) are functionally *driving* — they cause strong, suprathreshold responses analogous to first-order thalamic drivers.
4. The transthalamic pathway therefore parallels the direct corticocortical pathway: feedforward transthalamic projections (primary cortex → higher-order thalamus → higher cortex) act as drivers, while feedback transthalamic projections (higher cortex → higher-order thalamus → primary cortex) act as modulators.
5. This functional asymmetry is conserved between the visual and somatosensory systems, suggesting a general organizing principle rather than a system-specific accident.

## 4. Methods

Subpopulation-specific viral strategies in mice. Anterograde tracers and AAV-channelrhodopsin injections target L5 cells in specific cortical areas, allowing the authors to identify (a) which higher-order thalamic neurons receive driving input from each cortical area and (b) which cortical neurons receive return projections from the higher-order thalamus. Optogenetic activation of the driver inputs in the higher-order thalamus and recording of postsynaptic responses in target cortical neurons allow classification of each projection as "driver" (large EPSP, paired-pulse depression, suprathreshold) vs "modulator" (small EPSP, paired-pulse facilitation, subthreshold). Transsynaptic tracing (mono-synaptic rabies) verifies the cortico-thalamo-cortical circuit topology.

## 5. Results

**Visual system.** L5 cells in V1 drive pulvinar neurons. Those pulvinar neurons in turn project back to V1 with modulatory synaptic properties (small EPSPs, paired-pulse facilitation). L5 cells in higher visual areas also drive pulvinar neurons, and those pulvinar projections to higher visual areas are also strong drivers.

**Somatosensory system.** The same pattern: L5 in S1 drives posterior medial nucleus (PoM) neurons; PoM projections back to S1 are modulatory; L5 in S2 and M1 drives PoM; PoM projections forward to S2 are drivers.

**Generalization.** In both systems, the rule "feedforward transthalamic = driver, feedback transthalamic = modulator" holds. The driver/modulator distinction maps onto the functional hierarchy: information flowing *up* the cortical hierarchy via thalamus drives the target; information flowing *down* via thalamus modulates the target.

## 6. Critique / limitations

The driver/modulator distinction is operationally defined (synaptic strength, paired-pulse behavior, postsynaptic suprathreshold response). It is a useful classification but the boundary is not always sharp; some projections show intermediate properties. The paper doesn't quantify how often the binary classification fails.

The mouse cortex has a less elaborated higher visual hierarchy than primate cortex. The "higher visual area → pulvinar → V1" loop in mouse is grounded but is a simpler version of the primate pulvinar-cortex circuit. Direct extrapolation to primate visual processing is plausible but not demonstrated.

The paper establishes the *anatomy and synaptic physiology* of the transthalamic pathway. It does not establish a *behavioral* role — McKinnon, Mo & Sherman 2025 (a follow-up from the same lab) does that, by showing that optogenetic suppression of the V1→pulvinar driver impairs visual discrimination, providing the causal evidence Miller-Hansen & Sherman 2022 lacks.

The paper does not relate the transthalamic feedback to predictive coding directly. The "modulator" classification is compatible with a predictive-coding role (top-down modulation gates or precision-weights ascending evidence) but the paper does not draw the connection.

## 7. Connection to our work

This paper supports two specific architectural commitments in the user's program:

**Commitment 1: Feedback is modulatory, not driving** ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §1; [PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.4). PRISM v2's hierarchical FiLM applies a learned gain-and-bias modulation from $M^{\text{slow}}_{t-1}$ to the V1 feature map, rather than replacing or driving that map. Sherman's driver/modulator dichotomy provides the empirical justification: top-down feedback to V1 (whether via direct L6 CC projection per Weiler 2025 or transthalamic projection per this paper) is biologically modulatory, not driving. The FiLM mechanism is the computational analog. The Feedback Transformer (`concepts/feedback_transformer.md`) generalizes this: per-state Q/K/V projections combined via Hadamard product before softmax is a modulation of attention, not a replacement of sensory queries.

**Commitment 2: Parallel feedback pathways are the norm** ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §3). The user's multi-compartmental memory has explicit parallel feedback inputs at every layer (descending from above, ascending from below, lateral from parallel hubs). Sherman shows that real cortex implements both *direct* (L6 CC, per Weiler) and *transthalamic* (this paper) feedback in parallel — the biological precedent for the multi-source feedback design.

**Commitment 3: The cortico-thalamo-cortical loop as a generalized memory route** ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) — implicit in the slow-memory design). The slow $M^{\text{slow}}$ state is not anatomically a thalamic state, but functionally it plays the role Sherman attributes to higher-order thalamus: slow-evolving, modulatory, integrating across cortical areas. Future extensions of PRISM that explicitly model a thalamic relay between memory states could cite this paper as motivation.

The recurrent ViT paper (2502.10955) does not invoke the transthalamic pathway. The user's program does, but only implicitly — Sherman's anatomy is a candidate biological warrant for the slow-FiLM mechanism, not a derivation of it.

## 8. Citations to follow

- `mckinnon_mo_sherman2025_transthalamic_v1` — causal optogenetic test of the V1 transthalamic circuit in a discrimination task. Direct follow-up. In seed, full depth (2025 paper).
- `sherman_guillery2011_distinct_functions` — the Sherman lab's foundational review distinguishing driver vs modulator. In seed, full depth.
- `usrey_alitto2015_visual_thalamus` — review of thalamic visual processing. Not in seed.
- `bastos2012_canonical_microcircuits` — predictive-coding interpretation of cortical feedback that's consistent with Sherman's modulator finding. In seed, full depth in this session.
- `weiler2025_l6_corticocortical` — the parallel direct corticocortical feedback route. In seed, full depth in this session.
- `roth_dahmen2016_pulvinar_modulatory` — pulvinar's modulatory role in attention. Not in seed.
