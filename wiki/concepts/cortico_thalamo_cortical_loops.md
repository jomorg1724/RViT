---
id: cortico_thalamo_cortical_loops
type: concept
title: "Cortico-thalamo-cortical loops (transthalamic pathways)"
papers:
  - sherman2022_ctc_loop
  - sherman_guillery2011_distinct_functions
  - mckinnon_mo_sherman2025_transthalamic_v1
  - weiler2025_l6_corticocortical
  - felleman_vanessen1991_hierarchical_cortex
  - bastos2012_canonical_microcircuits
  - boshra_kastner2022_attention_control
  - choi2023_msi_review
source_documents:
  - "Private & Shared-4/Evolution of Architecture (§ Hierarchical Memory Layers)"
last_updated: "2026-05-18"
---

# Cortico-thalamo-cortical loops (transthalamic pathways)

## Definition

A class of long-range cortical communication pathways in which signaling between cortical areas is routed *via* a higher-order thalamic nucleus (pulvinar in the visual system, posterior medial nucleus in the somatosensory system, mediodorsal nucleus in cognitive systems), rather than via direct corticocortical projections. The basic loop is:

$$
\text{Cortical area A (L5)} \;\longrightarrow\; \text{higher-order thalamic nucleus} \;\longrightarrow\; \text{Cortical area B}
$$

The path-A-to-thalamus projection is a **driver** synapse (large EPSP, paired-pulse depression, suprathreshold postsynaptic response); the thalamus-to-path-B projection's synaptic properties depend on whether the loop is *feedforward* (driver, like a first-order thalamic relay) or *feedback* (modulator, small EPSP, paired-pulse facilitation, subthreshold).

The framework was introduced by Sherman & Guillery (`papers/sherman_guillery2011_distinct_functions.md`) and quantified anatomically and physiologically in mouse by Miller-Hansen & Sherman 2022 (`papers/sherman2022_ctc_loop.md`). Causal evidence comes from McKinnon, Mo & Sherman 2025 (`papers/mckinnon_mo_sherman2025_transthalamic_v1.md`), which showed that optogenetic suppression of the V1 → pulvinar driver impairs visual discrimination.

## The two parallel feedback substrates

Long-range cortical communication is implemented via two anatomically and functionally distinct substrates:

| Substrate | Anatomical route | Synaptic class | Cellular source |
|---|---|---|---|
| Direct corticocortical | A (L2/3, L5, L6) → B (L1, L4, etc.) | Modulatory (mostly) | L6 corticocortical neurons (Weiler 2025) dominate feedback direction |
| Transthalamic | A (L5) → higher-order thalamus → B | Driver if feedforward, modulator if feedback | L5 cortical pyramidal cells |

Both substrates carry feedback (`concepts/bidirectional_hierarchical_feedback.md`), and both contribute to top-down modulation of sensory processing. The Sherman framework treats the two as a *redundant pair*: information flowing up the cortical hierarchy is duplicated through both routes, with thalamus serving as a state-keeping intermediary.

## Why the redundancy is meaningful

The transthalamic loop is not redundant with the direct corticocortical pathway because:

- **Thalamic gating.** The higher-order thalamic nucleus can gate the loop on or off via state-dependent excitability (sleep-vs-wake, attention-vs-inattention). Direct corticocortical pathways do not have this gating mechanism.
- **Driver/modulator distinction.** Sherman & Guillery argue that thalamic relays are the natural carriers of *driving* information between cortical areas, with direct corticocortical pathways carrying more *modulatory* information. The two-pathway design routes the right signal through the right substrate.
- **Multimodal integration.** Higher-order thalamic nuclei receive input from multiple cortical areas and other subcortical structures, allowing them to integrate signals from many sources before relaying to the target. Direct corticocortical pathways are area-pair-specific.

## Implications for the user's program

The user's multi-compartmental memory (`concepts/multi_compartmental_memory.md`) does not currently include a thalamic-relay analog. The slow $M^{\text{slow}}$ state in PRISM v2 plays a *functional* role analogous to higher-order thalamus — slow-evolving, modulatory, integrating across cortical areas — but is not anatomically distinguished as a separate relay. Future architectural extensions could explicitly introduce a thalamic-relay layer between memory levels, with the relay's update governed by gating dynamics (Sherman's "modulator switch") rather than direct gradient flow.

More immediately, the Sherman framework supports the architectural commitment that *top-down modulation should be modulatory, not driving*. PRISM v2's slow-FiLM mechanism implements this (modulating gain rather than dictating activity). The biological warrant is the Sherman driver/modulator dichotomy applied to the feedback direction.

## Connection to attention

Pulvinar's modulatory role in attention has been well-documented (Saalmann et al. 2012; reviewed in Boshra & Kastner 2022, `papers/boshra_kastner2022_attention_control.md`). The pulvinar–cortical loop is one of the canonical transthalamic feedback substrates and is centrally implicated in selective attention. The user's program's attention mechanisms (Feedback Transformer with modulatory feedback) are functionally consistent with this anatomical substrate.

## Connection to multisensory integration

Choi et al. 2023 (`papers/choi2023_msi_review.md`) catalogs the transthalamic pathway as one of three principal integration motifs in mammalian multisensory integration, alongside direct corticocortical and association-cortex convergence. The review documents that higher-order thalamic nuclei (pulvinar for vision, posterior medial for somatosensation) carry cross-modal driver inputs from L5 of one sensory cortex and project to a different sensory cortex — instantiating the Sherman–Guillery transthalamic motif as an MSI substrate, not only a within-modality feedback substrate. For the user's program, this means the transthalamic motif is one of the natural substrates for *cross-hub* communication in the multi-hub system (`concepts/multi_hub_multi_objective_system.md`): cross-modal binding is implemented partly through transthalamic relays rather than only through direct corticocortical projections.

## Connection to other concepts

- `bidirectional_hierarchical_feedback` — transthalamic feedback is one of the two substrates.
- `multi_compartmental_memory` — could be extended with thalamic-relay layers.
- `cortico_basal_ganglia_thalamic_loops` — the sibling thalamic-relay loop. CBGTC routes cortex → basal ganglia → thalamus → cortex (an action-selection / RL loop); the cortico-thalamo-cortical loop routes cortex → higher-order thalamus → cortex (a sensory / cognitive integration loop). The two share the thalamic-relay-as-gating-substrate logic but differ in which subcortical structure does the gating; together they constitute the cortex's two principal thalamic computation lanes.
- `top-down-feedback` (tag) — transthalamic feedback is one route for top-down modulation.
- `precision_weighting_attention` — pulvinar's attentional gating is a candidate substrate for precision weighting.
- `cortical_microcircuit_model` — Bastos's microcircuit framework references thalamic input/output specifically.

## Connection to the literature

The Sherman-Guillery framework was developed in opposition to the older Felleman & Van Essen 1991 (`papers/felleman_vanessen1991_hierarchical_cortex.md`) corticocortical-only model of the visual hierarchy. The current consensus is that the two substrates coexist and play complementary roles.

The Weiler 2025 paper on L6 corticocortical neurons (`papers/weiler2025_l6_corticocortical.md`) provides the parallel-substrate evidence: direct L6 CC projections are a major route for the feedback that Sherman's framework attributes (also) to transthalamic loops. The two papers together establish that real cortex has multiple, anatomically distinct feedback substrates running in parallel — the biological precedent for the user's multi-source feedback design.

## Open questions

1. **What information is in the transthalamic loop vs the direct corticocortical pathway?** Both carry "feedback" but probably encode different content. The Sherman-Guillery driver/modulator framing suggests a partition but doesn't fully specify it.
2. **How does the thalamic nucleus gate the loop?** Cortical drivers, attention modulators, neuromodulators, and inhibitory input from the thalamic reticular nucleus all influence the gating. The relative contributions are unsettled.
3. **Does the architecture need an explicit thalamic-relay layer?** The user's program's slow memory is *functionally* like a thalamic relay but not anatomically distinguished. Whether an explicit relay layer would help is open.
