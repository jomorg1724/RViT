---
id: mishkin1983_two_pathways
title: "Object vision and spatial vision: two cortical pathways"
authors:
  - "Mishkin, Mortimer"
  - "Ungerleider, Leslie G."
  - "Macko, Kathleen A."
year: 1983
venue: "Trends in Neurosciences"
doi: "10.1016/0166-2236(83)90190-X"
arxiv: ""
url: "https://doi.org/10.1016/0166-2236(83)90190-X"
tags:
  - primate-neurophysiology
  - cortical-anatomy
  - lesion-microstimulation
  - review
concepts:
  - ventral-stream-hierarchy
  - dorsal-stream
  - topographic-organization
  - feature-binding
related:
  - bisley_goldberg2010_parietal_priority
  - krauzlis2013_sc_attention
  - dicarlo2012_object_recognition
  - tanaka1996_it_object_vision
  - silver2005_topographic_parietal
  - felleman_vanessen1991_hierarchical_cortex
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-22"
---

# Object vision and spatial vision: two cortical pathways

## 1. Abstract

Mishkin, Ungerleider & Macko consolidate a decade of behavioural-lesion and anatomical-tracer work in macaque to argue that extrastriate visual cortex is organised into **two functionally and anatomically segregated cortical pathways**, both originating in striate cortex (V1) and prestriate areas (V2, V3, V4) but diverging into anatomically distinct multisynaptic projection systems. A **ventral pathway** projects from V1 through V2, V4, and posterior inferior temporal cortex (TEO) to anterior inferior temporal cortex (TE) and onward into limbic and prefrontal targets; lesions along this pathway selectively impair tasks requiring discrimination of *object identity* — pattern, colour, shape, and visual feature recognition — while sparing spatial tasks. A **dorsal pathway** projects from V1 through V2, V3, and the middle temporal area (MT/V5) to the posterior parietal cortex (areas 7a, LIP, VIP, MST) and onward into frontal eye-field and premotor targets; lesions along this pathway selectively impair tasks requiring *spatial relations* among objects — visually-guided reaching, landmark discrimination, and spatial localisation — while sparing object recognition. The authors summarise the dissociation in the now-canonical formula that the ventral stream computes "**what**" an object is and the dorsal stream computes "**where**" it is, and propose that this segregation reflects an evolutionary solution to two computationally distinct sub-problems of vision that share a common early-cortical front-end but require divergent downstream processing.

## 2. Why this matters for us

This paper is the foundational statement of the **dorsal/ventral dichotomy** that grounds the user's multi-hub architectural program (`threads/the_user_architectural_program.md` §3, §5). The user's commitment to **multiple parallel recurrent compartments** with distinct content domains — spatial vs object, attention vs identity, location vs feature — has its biological precedent in Mishkin et al.'s two-pathway scheme. PRISM v1's spatially-organised ConvGRU memory $M_t \in \mathbb{R}^{H \times W \times C}$ is a **dorsal-stream analogue**: it maintains *where* relevant content lives in retinotopic space. A complementary object-identity / feature-binding compartment — present implicitly in the recurrent ViT's deeper channel-rich representations but not yet broken out as a separate hub — would be the **ventral-stream analogue**. The recurrent ViT's self-attention substrate, in which the same softmax map operates over a shared patch grid, spans both streams in the user's framing: it both indexes spatial priority (dorsal-like) and integrates feature content (ventral-like). The paper supplies the empirical license for committing to **architecturally segregated hubs** rather than a single monolithic memory: real cortex has solved its representational problem this way, and the lesion dissociations are double — damage to one pathway spares the other, so the segregation is functionally load-bearing rather than ornamental.

## 3. Key claims

1. **Two anatomically distinct cortical visual pathways** emerge from striate and prestriate cortex: a ventral pathway terminating in inferior temporal cortex and a dorsal pathway terminating in posterior parietal cortex.
2. **The ventral pathway mediates object vision** — the discrimination, recognition, and memory of *what* an object is (pattern, shape, colour, texture, feature combinations).
3. **The dorsal pathway mediates spatial vision** — the perception and use of *where* objects are located relative to each other and to the observer (spatial relations, landmark, visually-guided action).
4. **Lesion dissociations are double**: posterior inferior temporal lesions impair pattern/object tasks while sparing spatial tasks; posterior parietal lesions impair spatial tasks while sparing pattern/object tasks. Neither result reduces to a generalised "harder task" account.
5. **Both pathways are multisynaptic and hierarchical**, with successive cortico-cortical projections (V1 → V2 → V4 → TEO → TE ventrally; V1 → V2/V3 → MT → MST → 7a dorsally), each stage adding selectivity. Lesions at any node along a stream produce qualitatively similar but not identical impairments, indicating progressive elaboration rather than localised function.
6. **Both pathways share an early-cortical front-end** (V1, V2) before divergence, so deficits restricted to one modality require lesions at or beyond the point of divergence.
7. **Each pathway has a characteristic downstream limbic / frontal target**: the ventral pathway projects onward to amygdala, perirhinal cortex, and ventrolateral prefrontal cortex (linking object identity to value and memory); the dorsal pathway projects onward to hippocampus (via parahippocampal cortex) and dorsolateral prefrontal cortex (linking spatial relations to navigation and motor planning).
8. **The two pathways respect a representational division of labour** that is computationally well-motivated: object identity is *invariant* over location and viewpoint, while spatial location is *invariant* over identity and feature content. Solving both problems with one representation is in tension; dedicating distinct populations to each is a natural solution.

## 4. Methods

The 1983 paper is a **synthetic review** rather than a primary experimental report. Its argument rests on three converging method-types.

**Behavioural-lesion dissociations.** Macaques received bilateral aspiration or stereotactic lesions of either posterior inferior temporal cortex (TEO/TE) or posterior parietal cortex (areas 7a, VIP, LIP, MST collectively termed "PP"). Animals were then trained / re-tested on two task families:

- *Object-discrimination learning sets* — visual pattern discriminations (colour, shape, texture), object-quality memory, delayed match-to-sample on objects, concurrent-object discrimination.
- *Spatial-discrimination learning sets* — landmark discrimination ("approach the food well closer to the cylinder"), spatial-position discrimination, visually-guided reaching, spatial delayed-response.

The diagnostic result is the **double dissociation**: TE-lesioned animals are impaired on the first family but spared on the second; PP-lesioned animals are impaired on the second but spared on the first. The double dissociation is the load-bearing experimental design — it rules out a single-factor "task difficulty" or "generalised deficit" account.

**Anatomical-tracer studies.** Tritiated-amino-acid anterograde and HRP retrograde tracers were injected at multiple stations along each putative pathway to establish that the implicated areas are in fact monosynaptically or disynaptically connected in the sequence V1 → V2 → V4 → TEO → TE (ventral) and V1 → V2/V3 → MT → MST → 7a (dorsal), with crossing projections between streams kept relatively sparse. This work established that the lesion dissociations align with anatomical connectivity, not merely with cytoarchitectonic landmarks.

**Single-unit physiology.** The review draws on contemporary recordings showing that inferior temporal neurons are tuned to complex objects and features but have very large, often bilateral receptive fields with poor spatial selectivity, while parietal neurons in 7a, LIP, and MT have well-defined receptive fields, encode spatial location and direction-of-motion, but are largely indifferent to object identity. The complementary physiological tuning supports the lesion-based functional assignment.

## 5. Results

The 1983 paper does not report new quantitative data; it summarises and interprets a multi-year programme. The relevant numerical anchors come from the underlying primary papers and are recapitulated here:

- **Pattern-discrimination performance** drops to chance after bilateral TE lesion, while concurrent visual-spatial controls remain at pre-operative levels (≈ 90 % correct). The deficit is severe (often > 1000 additional trials to reach criterion compared with intact controls) and durable across re-testing.
- **Landmark-discrimination performance** drops to chance after bilateral PP lesion, while pattern-discrimination tested on the same animals remains at pre-operative levels. The deficit is symmetric in magnitude to the TE→pattern deficit but acts on the opposite task type.
- **Anatomical convergence**: tracer injections show that the V1 → V2 → V4 → TEO → TE chain forms a continuous corticocortical sequence with each stage projecting to the next at near-monosynaptic latency; similarly for the V1 → V2/V3 → MT → MST → 7a chain. Cross-stream projections (e.g., V4 ↔ MT) exist but are quantitatively a minority of the projection budget.
- **Receptive-field scaling**: along the ventral stream, receptive fields grow from ≈ 1° at V1 to > 20° at TE, and tuning shifts from oriented edges (V1) to colour and form (V4) to complex objects (TE). Along the dorsal stream, receptive fields grow comparably but tuning shifts from oriented edges (V1) to direction of motion (MT) to position-and-attention combined (LIP/7a) rather than to object identity.
- **The two streams diverge at or just after V2**: lesions at V1 disrupt both modalities equally (a generalised visual deficit); lesions at V2/V3 produce intermediate effects; lesions at TEO or MT produce stream-specific deficits; lesions at TE or PP produce maximally stream-specific deficits. The graded localisation supports the hierarchical-stream interpretation.

## 6. Critique / limitations

- **The "what / where" formula is too tidy.** Goodale & Milner (1992) reframed the dorsal stream as the *vision-for-action* pathway and the ventral stream as the *vision-for-perception* pathway, arguing that the dorsal stream encodes spatial relations *in the service of motor control* rather than spatial perception per se. The clearest evidence is patient DF, who has ventral-stream damage and cannot consciously recognise object orientation but can pre-shape her hand correctly when reaching to grasp the same object — a dissociation the 1983 framework cannot easily accommodate. The "where" label became "how" in the next generation of the framework.
- **The streams are not anatomically segregated.** Subsequent tracer work (Felleman & Van Essen 1991; Markov et al. 2014) showed dense cross-stream projections at every level. The clean two-pathway picture is a useful first-order abstraction but obscures substantial inter-stream communication that is necessary for binding object identity to location (the "binding problem"). The 1983 paper acknowledges crossing projections but treats them as minor.
- **The ventral / dorsal split does not respect the temporal-versus-parietal division of frontal feedback.** Anterior IT projects to ventrolateral PFC, while posterior parietal projects to dorsolateral PFC, but both targets receive bottom-up convergence from the *opposite* stream as well (Petrides & Pandya 2007). The clean prefrontal segregation in Mishkin et al. is an idealisation.
- **Spatial vision is itself heterogeneous.** Object-relative spatial coding (this fork is to the left of that one) is partially dissociable from observer-relative coding (the fork is to my right) and from action-relevant coding (the fork is within reach). Lesion deficits within the "dorsal stream" are heterogeneous across these sub-domains (Milner & Goodale 2008), again pointing to finer-grained anatomy than two streams.
- **Lesion-based localisation has well-known limits.** Bilateral aspiration of cortical tissue damages fibres of passage as well as the targeted area, and the post-operative deficit may reflect partial damage to distant structures. The 1983 inferences are nonetheless robust because they are corroborated by anatomical-tracer and electrophysiological convergence — but the lesion methodology alone would not establish the two-stream claim.
- **Object identity and spatial position are computed in cortex *and* in subcortex.** The superior colliculus (Krauzlis 2013; `krauzlis2013_sc_attention`) computes a spatial priority map largely in parallel with cortical streams, and lesions to SC produce attentional / spatial deficits not predicted from cortex alone. The two-pathway framework is cortex-centric and underweights the parallel sub-cortical contribution.
- **The single-unit data on which the ventral-stream characterisation rests later proved more graded than the review suggests.** Tanaka 1996 (`tanaka1996_it_object_vision`) showed that IT neurons are tuned to "critical features" — moderately complex feature conjunctions — rather than to whole objects, and that columnar organisation of feature tuning is the unit of IT representation. The "object cells" picture in the 1983 paper is an over-simplification of what later turned out to be a more compositional code.
- **No causal role for attention is captured.** Attention modulates both streams strongly (Bisley & Goldberg 2010, `bisley_goldberg2010_parietal_priority`; Reynolds et al. 1999), but the 1983 framework treats the streams as feedforward identification / localisation pipelines. The interactive role of top-down attention in shaping stream activity — which is central to the user's program — is absent.
- **The role of recurrence within and between streams is not addressed.** The 1983 picture is essentially feedforward: each stream is a hierarchical chain of cortico-cortical projections from sensory to associative cortex. Subsequent work has documented dense feedback within each stream (Lamme & Roelfsema 2000) and dense cross-stream feedback at intermediate levels (Gilbert & Li 2013). The strict two-pathway abstraction is silent about the recurrent dynamics that drive the user's architectural commitments.
- **No quantitative model.** The paper does not commit to a generative or computational account of how the two streams compute their respective representations, what objective each is optimised for, or how their outputs are integrated downstream. The user's program treats both streams as components of a unified competition for self-attention control, which is a level of theoretical commitment well beyond the 1983 review.

## 7. Connection to our work

This paper is the foundational neuroscientific anchor for the user's commitment to **architecturally segregated, content-specialised hubs** within a single recurrent system (`threads/the_user_architectural_program.md` §3 *Multi-compartmental memory* and §5 *Competition-emergent predictive coding*). Three distinct connection-points warrant emphasis.

**Dorsal / ventral segregation → multi-hub multi-objective system.** The user's `multi-hub-multi-objective-system` concept (TAXONOMY.md §"Core mechanisms"; `concepts/multi_hub_multi_objective_system.md`) commits to maintaining distinct recurrent compartments for distinct representational domains, each with its own memory state and update dynamics, all feeding back into a central self-attention substrate. Mishkin et al. 1983 is the canonical biological precedent: cortex implements *exactly this strategy* by maintaining functionally distinct dorsal and ventral processing streams that share an early sensory front-end (V1/V2) and a downstream attention / decision substrate (PFC) but diverge in their content. The user's planned spatial-attention hub maps onto the dorsal stream — both compute *where* relevant content is and gate spatial deployment of resources — while a future object-binding hub would map onto the ventral stream — computing *what* is at each location and binding feature combinations into object representations.

**PRISM v1's ConvGRU memory as dorsal-stream analogue.** PRISM v1's spatial memory $M_t \in \mathbb{R}^{H \times W \times C}$ (`Prism/docs/THESIS.md` §2.4) maintains a *retinotopically organised* state in which the spatial structure of the input is preserved across the channel dimension. This is structurally the dorsal-stream commitment: location is represented by the location of activation, not by the identity of activation. The single-unit physiological signature of parietal cortex — large but well-localised receptive fields that prefer spatial position over feature identity — is precisely the property the ConvGRU's channel-thin, spatially-shallow memory commits to. The connection to Silver et al. 2005 (`silver2005_topographic_parietal`) on retinotopic attention maps in human IPS is direct: IPS1/IPS2 *are* dorsal-stream retinotopic priority maps, and PRISM's $M_t$ is the architectural analogue.

**A future ventral-stream-analogue hub for feature binding.** The user's program (`threads/the_user_architectural_program.md` §3) describes a 3-layer GridCell-RNN stack in which deeper layers have lower spatial resolution and higher channel dimensionality. The deepest layer is the natural locus for an **object-identity compartment** — a ventral-stream-like representation in which retinotopic location is partially collapsed and feature content is amplified. The 1983 paper licenses the *segregation* itself (rather than treating object identity as derived from spatial information by a single shared encoder), and the receptive-field scaling along the ventral stream (V1 ≈ 1° → TE > 20°) supports the architectural choice of channel-expanding / spatially-reducing descending projections. The Tanaka 1996 follow-up (`tanaka1996_it_object_vision`) elaborates the columnar feature-tuning structure that such a hub should implement at its deepest layer.

**The recurrent ViT's self-attention substrate spans both streams.** The published Recurrent ViT (2502.10955) maintains a single hidden state $H^{(t)}$ over a patch grid; its self-attention map is patch-retinotopic (dorsal-like — *where* matters) but its value vectors carry channel-rich feature content (ventral-like — *what* lives there). The user's framing (`threads/the_user_architectural_program.md` §1) is that the central self-attention substrate is a *shared resource* over which dorsal-style and ventral-style hubs compete; the single ViT layer in the published work collapses this competition into a single map. PRISM v2's slow/fast dual memory (`PRISM_V2_PROPOSAL.md` §3.3) is a partial unbundling — but unbundles along the *temporal* axis (fast vs slow timescale) rather than along the *content* axis (spatial vs object). Mishkin et al. licenses the content axis as a complementary and well-motivated dimension of separation, suggesting that a future architecture could maintain two parallel slow/fast memories — one dorsal-content, one ventral-content — both feeding back into a single attention map.

**Connection to the priority-map literature.** Bisley & Goldberg 2010 (`bisley_goldberg2010_parietal_priority`) treats LIP — the apex of the dorsal stream — as a priority map for visual attention. Krauzlis 2013 (`krauzlis2013_sc_attention`) treats the superior colliculus as a parallel sub-cortical priority map. In both cases the spatial substrate is dorsal-stream-like: a retinotopic distribution of behavioural relevance. Mishkin et al. 1983 is the framing paper that establishes *why* the dorsal pathway is the right place to look for such maps: it is the stream that solves the "where" problem, and the priority map is the high-level "where + how important" representation that the dorsal stream's apex regions naturally maintain. The user's central self-attention substrate inherits this lineage — it is a learned priority map over the patch grid, with the same dorsal-stream functional signature.

**The Goodale-Milner refinement and PRISM v2.** Goodale & Milner's reformulation (perception vs action) is the natural next-generation framing for PRISM v2's coupling of memory to decision-making. The dorsal stream's role as a vision-for-action substrate (Milner & Goodale 2008) maps directly onto the user's interpretation of $M_t$ as a *task-relevant* representation rather than a faithful copy of the visual input. PRISM v1's choice to read change-detection decisions directly off $M_t$ is functionally a "vision-for-action" commitment: the spatial memory exists to drive a behaviour (the change-localisation response), not to support post-hoc perceptual report. Bridging from Mishkin et al. to Goodale & Milner is therefore the natural way to motivate PRISM v2's planned action-gated memory updates.

**Implications for the binding problem.** The 1983 separation makes feature binding a problem the brain has to solve at the *interface* between streams. The user's `feature-binding` concept (TAXONOMY.md) is precisely about how a multi-hub architecture re-binds object identity to location after segregated processing. The competition-emergent predictive-coding thesis (`threads/the_user_architectural_program.md` §5) supplies a candidate mechanism: feature binding emerges as a Nash equilibrium in which the dorsal-content hub correctly predicts what the ventral-content hub is computing at each location and vice versa, and the prediction-error gradient drives both hubs to maintain mutually consistent representations.

## 8. Citations to follow

- `ungerleider_mishkin1982_two_visual_systems` — the 1982 *Analysis of Visual Behavior* chapter that is the primary statement of the two-pathway dissociation, of which the 1983 *TINS* article is the synoptic version. Not yet in seed.
- `goodale_milner1992_what_how` — the next-generation refinement that recasts the dorsal stream as *vision-for-action* rather than *vision-for-location*. The single most-important follow-up. Not yet in seed.
- `milner_goodale2008_two_visual_systems_review` — a 25-year retrospective on the two-pathway / perception-action dichotomy. Not yet in seed.
- [felleman_vanessen1991_hierarchical_cortex](felleman_vanessen1991_hierarchical_cortex.md) — the canonical hierarchical wiring diagram that elaborates the two-pathway architecture across 32 cortical areas; cited in `threads/the_user_architectural_program.md` and in the DB at depth: full.
- `gross1972_inferotemporal_responses` — Gross's foundational demonstration of complex-object tuning in IT, the physiological anchor for the ventral-stream characterisation. Not yet in seed.
- `desimone1984_stimulus_selective_it` — IT stimulus-selective responses; the empirical detail behind the "what" stream characterisation. Not yet in seed.
- `andersen1985_lip_spatial` — Andersen's posterior-parietal spatial-tuning recordings; the physiological anchor for the dorsal-stream characterisation. Not yet in seed.
- `maunsell_vanessen1983_mt_directional` — Maunsell & Van Essen's MT directional-tuning paper, the canonical dorsal-stream physiology reference. Not yet in seed.
- `wilson_oscalaidhe_goldmanrakic1993_dissociation_pfc` — dorsal-vs-ventral PFC dissociation for spatial vs object working memory, extending the two-pathway scheme into PFC. Not yet in seed.
- `kravitz2011_new_neural_framework_visuospatial` — Kravitz et al.'s update arguing for *three* visual pathways (parieto-medial, parieto-premotor, parieto-prefrontal) within what Mishkin called the dorsal stream. Not yet in seed.
- `kravitz2013_ventral_visual_pathway` — Kravitz et al.'s parallel update on the ventral stream's sub-divisions. Not yet in seed.
- `freud2016_what_versus_how` — recent re-evaluation of the Goodale-Milner what/how dichotomy in humans. Not yet in seed.
- `markov2014_weighted_directed_macaque` — quantitative tract-tracing of macaque cortical connectivity that revises the strict two-stream segregation toward a denser, weighted graph. Not yet in seed.
