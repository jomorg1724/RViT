---
id: kiyonaga_egner2013_wm_internal_attention
title: "Working memory as internal attention: toward an integrative account of internal and external selection processes"
authors:
  - "Kiyonaga, Anastasia"
  - "Egner, Tobias"
year: 2013
venue: "Psychonomic Bulletin & Review"
doi: "10.3758/s13423-012-0359-y"
arxiv: ""
url: "https://doi.org/10.3758/s13423-012-0359-y"
tags:
  - working-memory
  - visual-attention
  - review
  - theoretical-essay
concepts:
  - attentional-template
  - working-memory-persistent-activity
  - top-down-feedback
related:
  - awh2006_attention_wm
  - gazzaley_nobre2012_topdown
  - panichello_buschman2021_shared_mechanisms
  - olivers2011_wm_states_attention
  - bahle2018_wm_attention_architecture
  - mante2013_context_dependent_pfc
  - vanmoorselaar2014_template_competition
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_14
status: full
depth: full
last_updated: "2026-05-16"
---

# Working memory as internal attention: toward an integrative account of internal and external selection processes

## 1. Abstract

Working memory (WM) and attention have been studied as *separate cognitive constructs*, although it has long been acknowledged that attention plays an important role in controlling the activation, maintenance, and manipulation of representations in WM. WM has, conversely, been thought of as a means of maintaining representations to voluntarily guide perceptual selective attention. It has more recently been observed, however, that the contents of WM can *capture visual attention*, even when such internally maintained representations are irrelevant — and often disruptive — to the immediate external task. The precise relationship between WM and attention remains unclear, but they appear to *bidirectionally impact one another*, whether or not internal representations are consistent with the external perceptual goals. This reciprocal relationship seems to be constrained by *limited cognitive resources* to handle demands in either maintenance or selection. Kiyonaga & Egner propose that the close relationship between WM and attention may be best described as a *give-and-take interdependence* between attention directed toward either actively maintained internal representations (traditionally considered WM) or external perceptual stimuli (traditionally considered selective attention), *underpinned by their shared reliance on a common cognitive resource*. WM and attention should no longer be considered as separate systems or concepts but as *competing and influencing one another* because they rely on the same limited resource.

## 2. Why this matters for us

Kiyonaga & Egner 2013 is the canonical *theoretical-unification* paper for WM and attention — the framing that "WM is internal attention; attention is external WM." This is the cognitive-science version of the user's architectural commitment that the recurrent ViT's recurrent state $H^{(t)}$ serves *both* attention-guidance and WM-maintenance through a single architectural substrate. For the user's program, this paper is the theoretical anchor for the unified-substrate commitment that Awh-Vogel-Oh 2006 ([awh2006_attention_wm](research_db/papers/awh2006_attention_wm.md)) catalogs behaviorally, Gazzaley-Nobre 2012 ([gazzaley_nobre2012_topdown](research_db/papers/gazzaley_nobre2012_topdown.md)) supports neurally, and Panichello-Buschman 2021 ([panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md)) confirms at the single-unit level.

## 3. Key claims

1. **WM and attention should be a single construct.** The traditional distinction — WM = maintenance of internal representations; attention = selection of external representations — masks a deeper unity. The two should be conceptualized as facets of one process.
2. **WM contents capture attention.** Even when irrelevant to the current task, WM contents bias visual attention toward stimuli that match them. This is the *involuntary* form of memory-guided attention.
3. **Attention shapes WM.** External attention to specific features or locations enhances the precision of WM representations of those features / locations.
4. **The relationship is *bidirectional*.** Either direction (WM → attention or attention → WM) can dominate depending on task demands.
5. **Shared resource pool.** WM and attention share a limited cognitive resource — engaging one reduces the capacity available for the other. This shared-pool framing is the theoretical commitment.
6. **The unified framing has clinical and applied implications.** Attention deficits in ADHD, neglect, and aging may reflect *shared-resource* impairments rather than separate WM and attention deficits.
7. **The cognitive-resource view connects to neural circuitry.** PFC + PPC implement the shared resource; their activity modulates both attention and WM via top-down signals to sensory cortex.

## 4. Methods

A narrative review and theoretical paper. The authors synthesize behavioral, neuroimaging, and neurophysiological evidence into the unified-resource framework. Key elements:
- **Behavioral evidence** that WM contents capture attention even when irrelevant (Soto, Heinke, Humphreys 2005; Olivers and colleagues).
- **Behavioral evidence** that holding more items in WM impairs concurrent attention.
- **Neuroimaging evidence** that PFC + PPC are engaged in both WM maintenance and attentional control.
- **Theoretical argument** that the parsimony of unified accounts is preferable to dual-mechanism accounts.

## 5. Results

The principal arguments and supporting evidence:

- **Memory-guided attention capture.** Subjects holding a WM-template (e.g., a colored shape) show involuntary attention to matching items in a subsequent display, even when the items are task-irrelevant.
- **Capacity interaction.** Performance on attention tasks decreases when concurrent WM load is high; performance on WM tasks decreases when concurrent attention demand is high.
- **Neural overlap.** PFC, PPC, and feature-selective sensory cortex are engaged by both attention and WM tasks with similar activation patterns.
- **Dissociations support shared resource, not shared substrate.** Some experimental conditions reveal dissociations (attention without WM-load effects, or WM-load without attention effects) — but the dissociations reflect different demands on the *same* underlying resource, not different mechanisms.

## 6. Critique / limitations

The "shared resource" framing is *underspecified*. What exactly the resource is — neural-firing capacity, computational throughput, energy budget, cognitive working space — is not pinned down. Different specifications make different empirical predictions.

The framework treats WM and attention as a single construct. The Awh-Vogel-Oh 2006 framework emphasizes that *varieties* of WM and *varieties* of attention exist; conflating them all into "shared resource" may be too crude. Subsequent work (Panichello & Buschman 2021) refines this by identifying *which* mechanisms are shared (PFC control mechanisms) vs distinct (parietal and visual cortex).

The capacity-interaction evidence is correlational. Causal manipulation (e.g., reducing PFC activity during a dual-task) would more decisively support the shared-resource claim.

The framework doesn't directly engage with predictive-coding or Bayesian-brain accounts. The "shared resource" might be reinterpreted as "shared precision-weighting" in the FEP framework; this connection is not made.

The clinical-applied implications are speculative. Whether attention deficits in ADHD reflect a shared-resource impairment, a specific attention deficit, or a specific WM deficit is unresolved.

## 7. Connection to our work

This paper provides the *theoretical* framing for the user's program's unified-substrate commitment:

**The recurrent ViT's recurrent state serves both attention and WM.** Kiyonaga & Egner's "WM as internal attention" is the cognitive-science version of the architectural commitment that the recurrent ViT's $H^{(t)}$ serves both. The single recurrent state guides attention (via the Feedback Transformer's feedback projection) and maintains task-relevant context across trials (WM). The architectural unification is theoretically justified by Kiyonaga-Egner.

**Memory-guided attention as the cue mechanism.** The recurrent ViT's cue mechanism — present a cue at time $t$, attend to the cued location at time $t+1$ — is the architectural form of "WM contents (held in the recurrent state) guide attention." This is exactly what Kiyonaga-Egner describe.

**Shared capacity.** Kiyonaga-Egner's "shared resource" framing has architectural consequences: the recurrent state's fixed dimensionality is *the* shared resource pool. Increasing WM demand (tracking more items) should reduce attention precision (lower softmax sharpness); increasing attention demand (multiple cued locations) should reduce WM-content fidelity. Empirically testing this on the recurrent ViT would validate the shared-resource interpretation.

**Multi-hub system framing.** In the user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)), each hub maintains its own state. The shared central self-attention substrate is the analog of Kiyonaga-Egner's "shared resource." Hubs compete for control of this shared resource — exactly the "competition for shared resource" framing.

**Reciprocal influence.** Kiyonaga-Egner's framing — WM and attention bidirectionally influence each other — is the architectural form of *recurrence in the user's program*. The recurrent ViT's memory state at time $t$ depends on attention at time $t-1$, and attention at time $t$ depends on memory at time $t-1$. The bidirectional influence is the architectural feature that makes the unified substrate possible.

The recurrent ViT paper cites Kiyonaga & Egner 2013 in its bibliography (ref [14]). Future manuscripts that argue for the unified WM-attention substrate should cite this paper as the theoretical anchor.

## 8. Citations to follow

- `awh2006_attention_wm` — behavioral catalogue of attention-WM interactions. In seed, full depth.
- `gazzaley_nobre2012_topdown` — neural common mechanism. In seed, full depth.
- `panichello_buschman2021_shared_mechanisms` — single-unit confirmation. In seed, full depth.
- `olivers2011_wm_states_attention` — WM states guide attention. In seed, full depth.
- `soto_heinke_humphreys2005_memory_attention_capture` — foundational WM-capture paper. Not in seed.
- `mante2013_context_dependent_pfc` — PFC as shared dynamical system. In seed, full depth.
- `vanmoorselaar2014_template_competition` — template-attention competition. In seed.
- `bahle2018_wm_attention_architecture` — WM architecture for attention. In seed.
