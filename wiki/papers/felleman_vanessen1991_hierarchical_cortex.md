---
id: felleman_vanessen1991_hierarchical_cortex
title: "Distributed hierarchical processing in the primate cerebral cortex"
authors:
  - "Felleman, Daniel J."
  - "Van Essen, David C."
year: 1991
venue: "Cerebral Cortex"
doi: "10.1093/cercor/1.1.1-a"
arxiv: ""
url: "https://doi.org/10.1093/cercor/1.1.1-a"
tags:
  - cortical-anatomy
  - primate-neurophysiology
  - review
  - theoretical-essay
concepts:
  - ventral-stream-hierarchy
  - dorsal-stream
  - top-down-feedback
  - cortical-microcircuit-model
  - hierarchical-predictive-coding
  - bidirectional-hierarchical-feedback
  - feedback-transformer
related:
  - bastos2012_canonical_microcircuits
  - sherman2022_ctc_loop
  - weiler2025_l6_corticocortical
  - keller_mrsic_flogel2018_pc_review
  - rao_ballard1999_predictive_coding
  - dicarlo2012_object_recognition
  - hubel_wiesel1962_receptive_fields
  - riesenhuber_poggio1999_hierarchical_models
  - miconi_vanrullen2016_feedback_attention
  - bastos2015_laminar_macaque
  - sherman_guillery2011_distinct_functions
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_110
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Distributed hierarchical processing in the primate cerebral cortex

## 1. Abstract

Felleman & Van Essen synthesize anatomical tract-tracing evidence from more than three decades of macaque neuroanatomy into a single, quantitatively explicit map of the primate visual cortex. Across the cortex they identify **32 visual and visual-association areas** linked by **305 distinct corticocortical pathways** (out of an upper bound of ~992 possible directed connections — a connectivity density of roughly **30–40%**). Each pathway is classified by its **laminar pattern of origin and termination** into one of three categories: **ascending** (feedforward; originates predominantly in superficial layers, terminates in layer 4), **descending** (feedback; originates in deep — and sometimes superficial — layers, terminates outside layer 4, especially in layers 1 and 6), or **lateral** (originates and terminates across all layers). Using the laminar-pattern asymmetries as edge constraints, the authors construct a partially-ordered **hierarchy** with at least **10 distinguishable levels** for visual cortex proper (and roughly 14 if subcortical inputs and hippocampal targets are added). The hierarchy contains two main streams, broadly identifiable with the dorsal (parietal, motion/space) and ventral (inferotemporal, form/object) pathways of Ungerleider & Mishkin (1982), and these streams are heavily cross-connected at every level. Crucially, **~90% of the 305 connections fit a single consistent global hierarchy**; ~10% of pathways are inconsistent with any one ordering, indicating the hierarchy is a strong but approximate organizing principle rather than a strict tree. The resulting diagram — a stack of areas with reciprocal ascending and descending links between most adjacent pairs and many non-adjacent pairs — has become the canonical diagram of the primate visual brain.

## 2. Why this matters for us

Felleman & Van Essen 1991 is the load-bearing anatomical citation for the user's commitment to **bidirectional hierarchical feedback** as an architectural primitive. The user's program (thread §3) builds a stack of GridCell RNNs paired with a V1 → V2/V4 → IT-style visual hierarchy, with explicit conv-stack descending projections and conv-transpose ascending projections that close a cortical-style loop at every level. That commitment rests on two empirical facts established here: (i) the primate visual cortex really is organized as a deep, partially-ordered hierarchy of dozens of areas, not a shallow stack or a flat lateral network; and (ii) every ascending pathway in that hierarchy has a corresponding descending pathway with a **distinct laminar signature**, making feedforward and feedback structurally separable. The asymmetry between ascending and descending laminar patterns is the empirical basis for the Feedback Transformer's commitment to **separate Q/K/V projections per feedback source** (and per direction): biological cortex does not pool ascending and descending streams into a single channel, and neither should the model. This paper is also the anatomical groundwork that licenses Bastos 2012's canonical microcircuit, Rao & Ballard 1999's predictive-coding hierarchy, Sherman-Guillery's transthalamic loops, and Weiler 2025's L6 corticocortical findings — every later work in our reading list assumes Felleman & Van Essen as its anatomical substrate.

## 3. Key claims

1. **The primate cerebral cortex contains a large, identifiable set of distinct visual areas** — at least 32 in macaque — defined by combinations of architectonics, topographic mapping, response properties, and connectivity.
2. **These areas are densely but selectively interconnected**: 305 directed pathways are documented, out of ~992 possible, giving a connectivity density of approximately 30–40%.
3. **Corticocortical pathways fall into three laminar categories** distinguishable by the layers of origin and termination — ascending (feedforward), descending (feedback), and lateral (same-level).
4. **Ascending pathways originate predominantly in superficial layers** (II/III) and **terminate in layer 4** (and lower III) of the target area; this is the canonical feedforward laminar signature.
5. **Descending pathways originate predominantly in deep layers** (V/VI), often with a superficial component, and **terminate outside layer 4**, with strong projections to layers 1 and 6; this is the canonical feedback laminar signature.
6. **Lateral pathways** originate and terminate across all layers (bilaminar / columnar pattern) and are characteristic of links between areas at the same hierarchical level.
7. **Using these laminar asymmetries as ordering constraints**, the 32 areas can be arranged into a **partially-ordered hierarchy with at least 10 distinct levels** in visual cortex proper (≈14 levels if retina, LGN, and hippocampus are included).
8. **The hierarchy is consistent with ~90% of observed pathways**; ~10% of pathways are inconsistent with any single global ordering, indicating that strict tree-like hierarchy is an approximation.
9. **The hierarchy contains two intertwined major streams** — broadly the dorsal/parietal (motion, space) and ventral/inferotemporal (form, object) streams of Ungerleider & Mishkin (1982) — with extensive cross-connections at every level rather than independent parallel pathways.
10. **Most paired areas are reciprocally connected** by both an ascending and a descending pathway, indicating that feedback is the rule, not the exception, in the visual cortex.
11. **The hierarchy extends to subcortical inputs and outputs**, including thalamic relay (LGN, pulvinar), superior colliculus, and hippocampal/parahippocampal targets, integrating the visual system with broader cortico-subcortical loops.
12. **The methodology of using laminar-pattern asymmetries as edges in a directed graph** is itself a methodological contribution — a way of inferring hierarchical position from microanatomy that has been reused, refined, and extended for decades after.

## 4. Methods

This is a synthesis paper, not a single empirical study. The methodological pillars are:

**Compilation of corticocortical pathways from the existing tract-tracing literature.** The authors aggregate retrograde and anterograde tracer studies (HRP, WGA-HRP, fluorescent retrograde tracers, autoradiographic anterograde tracers, etc.) from dozens of laboratories working in macaque (primarily *Macaca mulatta* and *M. fascicularis*) over the preceding ~25 years. Each pathway is recorded with its source area, target area, and reported laminar pattern of cells of origin (CO) and terminal labelling (TL).

**Definition of cortical areas.** A 32-area parcellation of macaque visual cortex is adopted, drawing on Van Essen's prior work and others'. Areas are defined by a confluence of criteria: architectonics (cytoarchitecture, myeloarchitecture, immunohistochemistry), topography (retinotopic / featuretopic maps), connectivity, and response properties. The full set includes occipital (V1, V2, V3, V3A, VP, MT, V4, V4t, MST, FST, …), parietal (LIP, VIP, MIP, 7a, …), and inferotemporal (TEO, TE, …) areas, plus polysensory and frontal-eye-field targets.

**Three-category laminar classification.** Each documented pathway is classified by its laminar pattern of cells of origin (predominantly superficial S, predominantly deep D, or bilaminar B) and laminar pattern of terminations (in layer 4 F for "feedforward-like", outside layer 4 M for "feedback-like" or "multilaminar"). Combinations of CO and TL yield three behavioural categories: **ascending** (S + F), **descending** (D or B + M), and **lateral** (B + columnar). Pathways that have been characterized for CO but not TL (or vice versa) are recorded with the partial information.

**Hierarchy construction.** Each ascending pathway places a "<" constraint between its source and target areas (source is lower than target); each descending pathway places ">". Lateral pathways constrain source and target to the same level. The authors then solve for the partial order on areas that satisfies the largest possible fraction of these constraints. Multiple consistent orderings exist; the canonical Felleman & Van Essen 1991 diagram (their Figure 4) is one such solution, displayed as a stack of levels with reciprocal ascending/descending arrows between most pairs.

**Goodness-of-fit accounting.** The authors quantify how many pathways are consistent vs. inconsistent with their preferred hierarchy. ~90% of pathways fit; ~10% remain inconsistent under any ordering and are noted as candidates for "skip-level" or "atypical" connections.

**Methodological caveat.** The synthesis depends on the accuracy and laminar specificity of the underlying tract-tracing studies, which vary in injection technique, tracer sensitivity, and laminar analysis. The 32-area parcellation is itself the subject of subsequent refinement (e.g., the merging or splitting of V3/VP, the parcellation of inferotemporal subdivisions). These limitations are acknowledged but the authors argue that the dominant statistical signal — ascending/descending asymmetry, hierarchical depth — is robust.

## 5. Results

The principal numerical findings have become standard reference data:

- **32 visual and visual-association areas** identified in macaque cortex.
- **305 directed corticocortical pathways** documented across the literature; this corresponds to **roughly 30–40% of the 992 = 32 × 31 possible directed connections**.
- **At least 10 distinguishable hierarchical levels** in visual cortex proper. Including retina, LGN, and hippocampal targets brings the count to roughly 14 levels.
- **~90% of pathways are consistent with a single global hierarchical ordering**; the remaining ~10% are inconsistent with any single ordering and represent "skip-level" or "atypical" connections.
- The hierarchy contains **two main intertwined streams** — dorsal (V1 → MT/MST/LIP/parietal) and ventral (V1 → V2/V4 → TEO/TE) — with **extensive cross-stream connections** at every level.
- The vast majority of area pairs that share any connection share a **reciprocal pair** of pathways — an ascending and a descending — rather than a unidirectional projection.
- The laminar signature of ascending vs. descending pathways is sharp enough to be diagnostic in the large majority of cases: e.g., V1 → V2 has the canonical superficial-origin / layer-4-target signature of an ascending pathway; V2 → V1 has the deep-origin / extragranular-target signature of a descending pathway.

The paper's **Figure 4** — the stacked-hierarchy diagram of all 32 areas with all 305 connections — is the most-reproduced single diagram in primate visual neuroscience and is the visual identity of the field for the subsequent generation of researchers.

## 6. Critique / limitations

The framework has been productively refined and contested over the subsequent three decades.

**Static, anatomical-only account.** The hierarchy is constructed from anatomical labelling alone; it does not specify the functional dynamics of feedforward vs. feedback signaling. Subsequent electrophysiology (Bastos et al. 2015 in seed; Buschman & Miller 2007) has shown that **gamma-band rhythms tend to dominate feedforward laminae** while **alpha/beta rhythms tend to dominate feedback laminae**, supplying the dynamic counterpart that the 1991 paper anticipated but did not establish.

**Hierarchy is approximate, not strict.** The ~10% of inconsistent pathways is not a small number — it implies that any single linear ordering is a partial fiction. Hilgetag, O'Neill & Young (1996) showed that the Felleman–Van Essen data admit **many statistically indistinguishable orderings**, not a unique solution. Modern reanalyses (Markov et al. 2014; Vezoli et al. 2021) have replaced the strict-level diagram with a **continuous hierarchy index** computed from the fraction of supragranular-layer neurons (SLN) projecting to each target.

**Macaque only.** All evidence is from macaque. Marmoset, owl monkey, and human cortex show partly different parcellations and connectivity (Wong-Riley parcellation studies, human DTI). The 32-area count and 10-level hierarchy are macaque-specific; cross-species generalization requires care.

**Area boundaries are unstable.** The 32-area parcellation has been substantially revised — V3/VP merged, additional inferotemporal and parietal subdivisions added (e.g., the Lewis & Van Essen 2000 parcellation), and ultimately superseded by the Markov et al. 2014 and Van Essen 2018 multi-modal cortical maps. The exact identity of each area is therefore historically contingent.

**Three-category laminar typology is coarse.** The S/B/D × F/M typology bins what is actually a continuous distribution of laminar patterns. Markov & Kennedy's group, in particular, has argued for a **graded** measure of hierarchical distance based on the SLN ratio rather than a discrete S/B/D code. This refinement preserves the qualitative result of Felleman & Van Essen but supplies a quantitative metric that 1991 lacked.

**Transthalamic pathways under-represented.** The 1991 synthesis is corticocortical-focused. Sherman & Guillery's transthalamic-loop framework (Sherman 2022 in seed; Sherman & Guillery 2011 in seed) argues that a large fraction of putatively "feedback" influence is in fact mediated by L5 → higher-order thalamus → cortex transthalamic drives, which Felleman & Van Essen does not catalogue. The L6-corticocortical findings of Weiler 2025 (in seed) similarly enrich the descending picture beyond what 1991 establishes.

**No functional weights.** The paper records only the presence/absence and laminar pattern of pathways, not their synaptic strength or behavioral contribution. Markov et al. 2014's quantitative tract tracing supplies the missing strength dimension and shows a **log-normal distribution** of connection weights spanning ~6 orders of magnitude — i.e., most edges are weak and a few are very strong.

Despite all these refinements, the core result — primate visual cortex is a deep, partially-ordered, reciprocally-connected hierarchy with distinct ascending and descending laminar signatures — has held up and is the empirical bedrock of every subsequent account.

## 7. Connection to our work

Felleman & Van Essen 1991 is the **empirical anatomical foundation** for the user's commitment to **bidirectional hierarchical feedback** as a load-bearing architectural primitive, and the most direct biological license for the **Feedback Transformer** primitive.

**Bidirectional hierarchical feedback (thread §3).** The user's 3-layer reference design — V1-paired Layer 1, V2/V4-paired Layer 2, IT-paired Layer 3, with explicit **descending conv-stack projections** (spatially-reducing, channel-expanding) and **ascending conv-transpose projections** (spatially-expanding, channel-reducing) — is a direct architectural translation of the Felleman–Van Essen reciprocal-pair finding (claim 10 above). The architectural commitment that *every* paired hierarchical level has both an ascending and a descending link is licensed precisely by the empirical observation that the vast majority of paired cortical areas are reciprocally connected. Without this paper, the bidirectional commitment looks like an arbitrary engineering choice; with it, the model recapitulates the empirically observed cortical wiring rule.

**Separate Q/K/V projections per feedback direction (Feedback Transformer, thread §1).** The Feedback Transformer's commitment to per-source Q/K/V projections — one set of projections for the bottom-up sensory stream, another for each descending or ascending memory feedback — finds its biological justification in the **laminar-signature asymmetry** between ascending and descending pathways (claims 4 and 5). Biological cortex distinguishes ascending and descending streams structurally at the synaptic level; the Feedback Transformer distinguishes them parametrically at the projection level. The architectural choice not to pool feedforward and feedback into a single channel mirrors the cortical observation that they do not share a laminar termination zone.

**Multi-stage processing in the recurrent ViT.** The Recurrent ViT paper (2502.10955) is a shallow specialization of the user's full hierarchical program — a single recurrent state H^{(t-1)} feeds back into a single attention layer. Scaling this to the multi-stage GridCell RNN stack envisioned in thread §3 requires answering "how many stages should the hierarchy have?" Felleman & Van Essen's **10-level macaque hierarchy** (claim 7) gives a principled biological ceiling: a stack of 3–10 levels is anatomically plausible, while a stack of 50 levels is not. The user's 3-layer reference design is at the low end of this range — a deliberate simplification chosen to keep the system tractable while preserving the qualitative hierarchical structure.

**Two intertwined streams justify multi-hub framing.** Claim 9 — that the hierarchy contains two main streams (dorsal/parietal and ventral/inferotemporal) with extensive cross-connections at every level — is the anatomical precedent for the user's multi-hub system (thread §5). The hubs (MSI, RL, VAE) are the deep-learning analogs of the dorsal and ventral streams (and additional functional streams), and the commitment that they cross-communicate at every level via the shared self-attention substrate is licensed by the cortical observation that the dorsal and ventral streams are not independent parallel pathways but extensively interlinked sub-hierarchies.

**Skip-level connections support diminishing-feedback design.** Claim 8 — that ~10% of pathways are inconsistent with any single ordering, indicating skip-level connections between non-adjacent areas — is the biological precedent for the user's "diminishing feedback into deeper layers" design (thread §3): Layer 0 receives feedback from C₁, C₂^{(UP)}, and C₃^{(UP²)} (three sources), Layer 2 from C₂ and C₃^{(UP)} (two), Layer 3 from only itself. The pattern of allowing shallower layers to receive feedback from multiple deeper levels (not just the adjacent one) is a direct architectural reflection of the skip-level reciprocal projections documented here.

**Companion to other foundational entries.** Felleman & Van Essen 1991 supplies the anatomical substrate that the following seed papers each build on or refine: `bastos2012_canonical_microcircuits` (the laminar microcircuit that implements the ascending/descending distinction); `bastos2015_laminar_macaque` (the gamma/alpha-beta rhythmic correlate of feedforward vs. feedback); `sherman2022_ctc_loop` and `sherman_guillery2011_distinct_functions` (the transthalamic complement to the corticocortical hierarchy); `weiler2025_l6_corticocortical` (the L6 corticocortical descending pathway); `keller_mrsic_flogel2018_pc_review` and `rao_ballard1999_predictive_coding` (the predictive-coding interpretation of the same hierarchy); `dicarlo2012_object_recognition` (the ventral-stream functional account); `hubel_wiesel1962_receptive_fields` (the V1 starting point of the hierarchy); `riesenhuber_poggio1999_hierarchical_models` (the computational HMAX abstraction); `miconi_vanrullen2016_feedback_attention` (feedback as attention modulator in a hierarchical model). Felleman & Van Essen 1991 is the anatomical "root" of this citation graph: every entry assumes its hierarchy and extends or refines it.

**Why this specifically licenses the Feedback Transformer's separation of Q/K/V per direction.** The structural asymmetry between layer-4-targeting ascending pathways and layer-1/6-targeting descending pathways implies that the cortical postsynaptic neurons see ascending and descending inputs through **distinct synaptic compartments** — and therefore can apply distinct dendritic / biophysical transformations to each. The Feedback Transformer's per-direction Q/K/V projections are the connectionist abstraction of this compartmental separation: one Q/K/V set is the "layer-4-equivalent" pathway, another is the "layer-1-equivalent" pathway, and the Hadamard product in the attention score (thread §1) is the read-out integration. The biological precedent is therefore not just "feedback exists" but "feedback enters the postsynaptic neuron through anatomically distinct channels" — exactly the architectural pattern the Feedback Transformer encodes.

## 8. Citations to follow

- `markov2014_quantitative_cortical_hierarchy` — Markov et al. 2014 quantitative tract tracing with SLN ratio as continuous hierarchy index. Not in seed; the modern successor to the F&V hierarchy.
- `vanessen1983_hierarchies_visual_cortex` — Van Essen & Maunsell 1983, the precursor to the 1991 synthesis. Not in seed.
- `ungerleider_mishkin1982_two_streams` — the dorsal/ventral two-streams hypothesis that F&V's hierarchy organizes around. Not in seed.
- `hilgetag1996_indeterminate_organization` — Hilgetag, O'Neill & Young 1996 showing many statistically indistinguishable orderings fit the F&V data. Not in seed; important critique.
- `maunsell_vanessen1983_connections_mt` — the MT connectional studies underlying the dorsal-stream segment of the hierarchy. Not in seed.
- `lewis_vanessen2000_corticocortical_parietal` — Lewis & Van Essen 2000 parietal parcellation update. Not in seed.
- `markov2013_weighted_cortical_network` — Markov et al. 2013 log-normal distribution of connection weights. Not in seed.
- `buschman_miller2007_topdown_bottomup` — Buschman & Miller 2007 dynamic correlate of feedforward vs. feedback signaling. Not in seed.
- `vezoli2021_cortical_hierarchy_lognormal` — Vezoli et al. 2021 updated hierarchy with log-normal weights. Not in seed.
- `barone2000_laminar_distance` — Barone et al. 2000 SLN-based hierarchical distance metric. Not in seed.
- `vanessen2018_multimodal_parcellation` — modern multi-modal cortical parcellation in human and macaque. Not in seed.
