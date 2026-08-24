---
id: rust_cohen2022_priority_coding
title: "Priority coding in the visual system"
authors:
  - "Rust, Nicole C."
  - "Cohen, Marlene R."
year: 2022
venue: "Nature Reviews Neuroscience"
doi: "10.1038/s41583-022-00582-9"
arxiv: ""
url: "https://doi.org/10.1038/s41583-022-00582-9"
tags:
  - visual-attention
  - primate-neurophysiology
  - review
concepts:
  - priority-map
  - gain-modulation
  - attentional-spotlight
  - top-down-feedback
related:
  - bisley_goldberg2010_parietal_priority
  - bisley_mirpour2019_priority_map
  - desimone_duncan1995_biased_competition
  - cohen_maunsell2009_correlations
  - reynolds_heeger2009_normalization
  - mante2013_context_dependent_pfc
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_5
status: full
depth: full
last_updated: "2026-05-16"
---

# Priority coding in the visual system

## 1. Abstract

Although we are continuously bombarded with visual input, only a fraction of incoming visual events is perceived, remembered or acted on. The neural underpinnings of various forms of visual priority coding — including perceptual expertise, goal-directed attention, visual salience, image memorability and preferential looking — have been studied largely in isolation. Rust & Cohen synthesize information from these different examples to review recent developments in our understanding of visual priority coding and its neural correlates, with a focus on the role of behavior to evaluate candidate correlates. They propose that the brain combines different types of priority into a unified priority signal while also retaining the ability to differentiate between them, and that this is achieved by leveraging *partially overlapping low-dimensional neural subspaces* for each type of priority that are shared with the downstream neural populations involved in decision-making. They close by describing the gulfs in understanding that have resulted from different research approaches, and point toward future directions for fundamental insights about neural coding and how prioritization influences visually guided behavior.

## 2. Why this matters for us

Rust & Cohen 2022 is the most recent canonical review of *priority coding* as a unifying neural principle and is the direct biological analog of the user's central self-attention substrate ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)). Where Bisley & Goldberg 2010 framed priority spatially in LIP, Rust & Cohen broaden the framework: priority is a *multi-source*, *multi-form* signal (salience, goals, expertise, memorability, looking preference) merged into a shared low-dimensional subspace that downstream decision populations read out. That is structurally what the user's Feedback Transformer does — it integrates many feedback sources into one attention map that downstream layers and motor outputs consume. The recurrent ViT (2502.10955) cites this review as ref [5] because the model's self-attention map functions exactly as such a unified priority readout.

## 3. Key claims

1. Diverse visual phenomena — bottom-up salience, goal-directed attention, perceptual expertise, image memorability, preferential looking — are different *types* of priority but share a common neural function: they bias which visual events get perceived, remembered, or acted on.
2. The brain combines these heterogeneous priority signals into a **unified priority signal** that downstream decision and motor populations can read out, while still retaining the ability to *differentiate* between priority types when task demands require it.
3. The mechanism for both unification and differentiation is **partially overlapping low-dimensional neural subspaces**: each priority type occupies its own subspace, but the subspaces share dimensions that the downstream decision population aligns with.
4. Priority is not localized to one area. Multiple cortical (LIP, FEF, V4, IT) and subcortical (SC, pulvinar, basal ganglia) populations contribute, with priority signals appearing throughout the visual hierarchy and decision pathway.
5. Behavior is the indispensable criterion for evaluating whether a neural signal is a priority signal: a candidate correlate that does not predict trial-by-trial behavior cannot be assigned the priority role, however suggestive its tuning.
6. Different research traditions (psychophysics, single-unit electrophysiology, fMRI, theory) have produced *fragmented* accounts of priority. The synthesis the review offers is that these are different windows on a single underlying low-dimensional code.
7. Open questions concern (a) how priority subspaces are formed during learning, (b) how the brain switches read-out alignment when goals change, and (c) how the cortical and subcortical contributions are coordinated in time.

## 4. Methods

A narrative review of primate single-unit physiology, primate and human imaging, and computational/theoretical work spanning roughly 2010–2022. No new empirical data are presented. The contribution is a *conceptual unification*: priority is reframed from a spatial map in one area (the Bisley & Goldberg 2010 view) to a *low-dimensional shared subspace* distributed across many populations.

The review's methodological frame is that of *population-level neural-coding analysis*. Key techniques surveyed include linear decoding, demixed PCA, choice probability, noise-correlation analysis, and behavioral-readout-aligned subspace methods (the "decision subspace" tradition associated with the Cohen lab and collaborators). These methods are the empirical basis for the claim that priority occupies a *low-dimensional* subspace rather than being distributed over the full neural-activity manifold.

The review explicitly treats *behavior* as the validator: a population-level signal qualifies as priority only if it predicts trial-by-trial perceptual, mnemonic, or motor output. This is a sharper criterion than tuning-based or selectivity-based criteria favored in earlier eras.

## 5. Results

The principal empirical syntheses the review consolidates:

- **Low dimensionality of priority signals.** Across LIP, FEF, V4, and IT, the dimensions of neural-activity space that *predict behavior* are far fewer than the population's intrinsic dimensionality. Demixed PCA and choice-aligned axes recover a small number (~1–10) of priority dimensions.
- **Partial overlap across priority types.** Salience, goal-directed attention, and memorability subspaces share substantial — but not full — overlap. Shared dimensions explain the *unification*; non-shared dimensions explain the brain's ability to *differentiate* priority types.
- **Behavior-aligned readout.** Linear decoders aligned with behavior recover priority more cleanly than decoders aligned with stimulus identity, even in areas (e.g., V4) traditionally treated as stimulus-encoding.
- **Distribution across areas.** Priority signals are found in LIP, FEF, V4, IT, SC, pulvinar, and basal-ganglia targets. No single area is *the* priority area; rather, priority is a distributed code with area-specific weighting.
- **Noise-correlation structure.** Attention reduces shared noise variance along the decoding axis, consistent with the idea that priority modulation operates within the decision-relevant subspace.
- **Memorability is a priority signal.** Highly memorable images elicit stronger and more decodable IT and MTL responses, behaving like a passively-evoked priority signal even without explicit attention.
- **Cross-task subspace alignment.** When the task changes, the *read-out direction* changes more than the *priority directions themselves*, consistent with downstream populations re-aligning to existing subspaces rather than the encoding population restructuring.

The review does not commit to specific numbers throughout — it is a survey — but the qualitative pattern is robust across the cited studies.

## 6. Critique / limitations

The review's central construct — the *unified low-dimensional priority subspace* — is descriptive rather than mechanistic. It does not specify *how* the partially-overlapping subspaces are formed during development or learning, nor *how* downstream populations dynamically realign their read-out to match task demands. These are pointed out as open questions but not resolved.

The subspace framing is dependent on the choice of decoder. Linear decoders favor low-dimensional structure; nonlinear or kernel-based decoders may recover priority along higher-dimensional axes. The review does not engage seriously with how decoder choice shapes the conclusion.

The framework is *agnostic to the integration mechanism*. Bisley & Goldberg 2010 propose that LIP integrates bottom-up and top-down inputs to produce a priority map; Rust & Cohen do not specify a comparable mechanism for how heterogeneous priority types (salience, expertise, memorability) get summed into the unified signal. The shared-subspace formalism is a *result* of integration, not a *model of* it.

The treatment of subcortical contributions (SC, pulvinar) is comparatively thin. Subsequent work (Halassa & Sherman 2019; cortico-thalamo-cortical literature) has emphasized the pulvinar's role in coordinating cortical priority; Rust & Cohen acknowledge this but do not develop it.

The review is largely retinotopic and spatial. Feature-based and object-based priority are mentioned but not given the same depth as spatial priority. The user's program — where priority must operate over patches in a transformer (a *featural*-spatial hybrid) — would benefit from the feature-priority extension that this review only gestures at.

Finally, the review does not engage with the predictive-coding tradition (Rao & Ballard 1999; Friston 2010). Priority and prediction are framed as independent, although in the user's program (and in some recent theoretical work) they are tightly coupled — priority modulates the precision of prediction errors, and prediction errors update priority.

## 7. Connection to our work

Rust & Cohen 2022 is the *single most important biological reference* for the central self-attention substrate in the user's architectural program. The connection is structural, not metaphorical, and it touches several specific design commitments.

**The central self-attention substrate is a priority subspace.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) places a shared self-attention map at the center, fed by an MSI hub, an RL hub, and a VAE hub. Each hub injects its own contribution into the attention competition via Feedback-Transformer Q/K/V projections. Rust & Cohen's *partially-overlapping low-dimensional subspaces* is the exact biological analog: each hub-like priority type (salience, goal, memorability) occupies its own subspace within a shared substrate, and the downstream readout aligns with the combined signal. The user's coalition-resource-competition account ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) supplies the *mechanism* that Rust & Cohen leave open: hubs compete for representation in the shared subspace, and the overlap structure emerges from that competition.

**The Feedback Transformer integrates priority types.** The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) takes the Hadamard product of bottom-up sensory $s_q \odot \sum_k c^{(k)}_q$ before the softmax. This is the architectural mechanism by which heterogeneous feedback sources are merged into a single attention map — the computational answer to Rust & Cohen's question of how diverse priority types are unified. Up to twelve feedback sources have been integrated in the user's Video VAE work; the Rust & Cohen framework predicts that the resulting attention maps should exhibit partially-overlapping low-dimensional priority subspaces, one per feedback source, with shared dimensions where the priority sources agree.

**The published Recurrent ViT (2502.10955) cites this as ref [5].** The ViT paper's self-attention map is the unified priority readout that Rust & Cohen describe; the model's cued-attention effects, faster correct-trial dynamics, and behavior-predictive attention dynamics all instantiate the Rust & Cohen claim that priority signals are *behavior-aligned*. The model's perturbation experiments (analogous to FEF microstim) are perturbations of the priority subspace.

**PRISM v1 uses prediction error as priority.** PRISM v1 (`THESIS.md` §2.4) replaces softmax attention with a prediction-error map. In Rust & Cohen's framework this is a substantive theoretical claim: that *one specific axis* of the priority subspace — the axis aligned with the precision-weighted prediction error — is sufficient for change-detection behavior. The Rust & Cohen review does not engage with predictive-coding, so this is the user's own extension: priority *is* (or at least includes) precision-weighted prediction error.

**Cross-task subspace alignment ↔ Recurrent ViT's task-conditioning.** Rust & Cohen note that when the task changes, downstream readouts realign to existing priority subspaces. The Recurrent ViT and PRISM models inherit this property: the same memory state and attention substrate support different downstream heads (change detection, classification, reconstruction). The user's program predicts that switching tasks should re-align readout while leaving the central substrate largely intact — an empirically testable claim once a multi-task variant is trained.

**Behavior as the validation criterion.** Rust & Cohen insist that priority signals must predict trial-by-trial behavior. The Recurrent ViT paper validates its attention dynamics against behavior (RT, accuracy, cue effects). This methodological alignment is not coincidental: it is the standard the user's program inherits, and it is the standard against which PRISM v1 and v2 must be measured.

**The unresolved question Rust & Cohen pose — how priority subspaces are formed — is what the user's competition-emergent-PC thesis answers.** Priority subspaces emerge from inter-hub competition for the limited attention substrate; the partially-overlapping structure is the equilibrium of that game ([competition_emergent_predictive_coding](research_db/concepts/competition_emergent_predictive_coding.md)). This is one of the cleanest places where the user's theoretical contribution goes beyond the review's open questions.

## 8. Citations to follow

- `bisley_mirpour2019_priority_map` — direct precursor; spatial priority in LIP, FEF, SC. In seed.
- `bisley_goldberg2010_parietal_priority` — canonical priority-map paper. In seed, full depth.
- `cohen_maunsell2009_correlations` — noise-correlation reductions under attention; methodological backbone of the subspace claim. In seed.
- `reynolds_heeger2009_normalization` — divisive normalization as the mechanism behind attentional gain modulation that operates within the priority subspace. In seed.
- `desimone_duncan1995_biased_competition` — biased-competition framework, the cellular-level precursor of the subspace account. In seed, full depth.
- `mante2013_context_dependent_pfc` — context-dependent PFC dynamics, the populational analog of task-dependent readout realignment. In seed.
- `halassa_sherman2019_pulvinar` — pulvinar's role in coordinating cortical priority. Not yet in seed; should be added.
- `bashivan_kar_dicarlo2019_neural_population_control` — using neural-population control to probe behavior-aligned subspaces in IT. Not yet in seed.
- `isik_carlson2018_memorability` — image memorability as a passive priority signal. Not yet in seed.
- `semedo2019_cortical_communication_subspaces` — communication subspaces between visual areas; the populational machinery that priority subspaces share with. Not yet in seed.
