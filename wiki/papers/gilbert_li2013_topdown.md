---
id: gilbert_li2013_topdown
title: "Top-down influences on visual processing"
authors:
  - "Gilbert, Charles D."
  - "Li, Wu"
year: 2013
venue: "Nature Reviews Neuroscience"
doi: "10.1038/nrn3476"
arxiv: ""
url: "https://doi.org/10.1038/nrn3476"
tags:
  - primate-neurophysiology
  - early-visual-cortex
  - review
  - theoretical-essay
concepts:
  - top-down-feedback
  - gain-modulation
  - cortical-microcircuit-model
related:
  - keller_mrsic_flogel2018_pc_review
  - bastos2012_canonical_microcircuits
  - weiler2025_l6_corticocortical
  - miconi_vanrullen2016_feedback_attention
  - rao_ballard1999_predictive_coding
  - felleman_vanessen1991_hierarchical_cortex
  - desimone_duncan1995_biased_competition
  - reynolds_heeger2009_normalization
  - moran_desimone1985_selective_attention
  - reynolds_chelazzi2004_attentional_modulation
  - hubel_wiesel1962_receptive_fields
  - baluch_itti2011_topdown_mechanisms
  - larkum2013_apical_basal
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Top-down influences on visual processing

## 1. Abstract

Reentrant or feedback pathways between cortical areas carry rich and varied information about behavioural context, including attention, expectation, perceptual task, working memory and motor commands. Neurons receiving such inputs effectively function as adaptive processors that are able to assume different functional states according to the task being executed. Recent data suggest that the selection of particular inputs, representing different components of an association field, enable neurons to take on different functional roles. In this review the authors discuss the various top-down influences exerted on the visual cortical pathways and highlight the dynamic nature of the receptive field, which allows neurons to carry information that is relevant to the current perceptual demands.

## 2. Why this matters for us

Gilbert & Li 2013 is the canonical modern review of top-down modulation in early visual cortex. It is the empirical and conceptual anchor for the user's commitment — encoded throughout the architectural program (`the_user_architectural_program.md` §3) — that V1 is not a passive feedforward feature extractor but a context-sensitive site of integration where descending signals from higher areas, lateral signals from same-level neighbours, and bottom-up sensory drive are *simultaneously* combined. The review's central claim — that the V1 receptive field is dynamic, with its tuning, gain, and spatial integration properties contingent on the current task — is precisely the empirical phenomenon the Feedback Transformer (`the_user_architectural_program.md` §1) is designed to instantiate computationally. The dual-mechanism framing the review pushes (feedback projections plus horizontal connections) is the dual-mechanism the bidirectional-hierarchical-feedback concept (ascending + descending conv projections plus lateral GridCell connectivity) captures architecturally.

## 3. Key claims

1. V1 (and every other visual area) receives massive reentrant input from higher areas — V2, V4, IT, MT, and via the pulvinar from many cortical and subcortical sites — carrying information about attention, expectation, task identity, working memory contents, and motor plans.
2. V1 neurons are *adaptive processors*: the same cell exhibits different tuning curves, different gain, and different contextual integration depending on what the animal is attending to and what task it is performing. Receptive-field properties are not fixed but task-dependent.
3. Top-down influences operate via at least two anatomically distinct routes: long-range corticocortical feedback projections (originating predominantly in deep layers of higher areas, terminating in superficial and deep layers of lower areas), and long-range horizontal intrinsic connections within a single area (pyramidal axons extending parallel to the cortical surface, linking neurons with similar orientation preferences across distant retinotopic locations).
4. Spatial attention, feature-based attention, object-based attention, perceptual task, object expectation, efference copy, working memory, and perceptual learning all leave specific, measurable signatures in V1 single-unit responses — they are not exclusively properties of higher cortical areas.
5. The most parsimonious circuit hypothesis is that descending feedback signals act as a *gating mechanism* that selectively recruits subsets of the horizontal-connection network, dynamically reconfiguring which lateral inputs are functionally effective. The same V1 cell can therefore implement different "association fields" (Field, Hayes & Hess 1993) at different moments.
6. The result is a network-level dynamic encoding: which information V1 carries at any moment is a joint function of the stimulus and the descending context. Decoding analyses show several-fold differences between attend-in vs attend-away conditions in V1 firing rates and in the information V1 carries about task-relevant stimulus dimensions.

## 4. Methods

A narrative review with no new empirical data. The authors synthesise roughly two decades of primate single-unit, fMRI, and behavioural results from their own lab (Rockefeller; Beijing Normal) and the broader field. The review is organised around six top-down phenomena — spatial attention, object/feature attention, perceptual task, object expectation, efference copy, and working-memory/perceptual-learning — and then steps up to (a) the network-level consequences of these single-cell effects and (b) the circuit-level mechanism (feedback + horizontal connections + gating). The most-cited experimental paradigms are: the three-line bisection task (used by the authors to demonstrate task-dependent V1 tuning); contour-integration and contour-tracing tasks; vernier discrimination; shape-expectation cuing; and the Schoups/Yang perceptual-learning protocol. Key cited collaborators and competitors include Maunsell, Treue, Reynolds, Desimone, Lamme, Roelfsema, Posner, Kastner, and Westheimer.

The review's organising construct is the *dynamic receptive field*: rather than treating the RF as a fixed feature-detector property of a cell, the authors argue the RF is a transient functional configuration that emerges from the combination of feedforward drive, lateral interaction, and descending modulation. Information-theoretic and decoding analyses are cited (rather than performed) to support the network-level claim that V1's *encoding capacity* — not merely its firing-rate gain — shifts with task.

## 5. Results

The review's empirical synthesis yields the following signatures, each with multiple supporting studies:

- **Minimum response field vs contextual receptive field.** Parafoveal V1 cells have classical RFs ~0.5° in diameter, but contextual modulation extends over many degrees of visual angle — far beyond the classical RF and far beyond the reach of feedforward LGN input alone.
- **Task-dependent V1 tuning.** In the three-line bisection task, V1 cells become more sensitive to displacements of the task-relevant lines than the task-irrelevant ones; the same cells show the opposite pattern when task relevance is reversed. The tuning *changes with the task*.
- **Contour integration is task-gated.** The collinear-flank facilitation of a central oriented bar is *much larger* when the animal is actively performing contour detection than when the same stimulus is shown passively — the horizontal-connection circuit is recruited by task demand, not by stimulus alone.
- **Curve tracing.** V1 cells with RFs along the attended curve show enhanced responses; cells along an ignored distractor curve do not — object-based attention reaches V1.
- **Shape expectation alters V1 selectivity.** Cuing the animal to expect a specific shape changes the shape selectivity of V1 neurons before the shape is presented.
- **Attentional modulation is competition-dependent.** Attentional effects in extrastriate cortex (and to a lesser extent V1) are several-fold larger when multiple stimuli compete within a receptive field — the Moran & Desimone 1985 / Reynolds 1999 biased-competition signature.
- **Learned cross-modal association in MT.** After training on an arrow-cued motion task, MT cells respond to a stationary arrow as if it were moving in the cued direction — top-down learned associations reshape feedforward-driven extrastriate responses.
- **Laminar specificity.** Feedforward projections originate predominantly in superficial layers; feedback originates in deep layers. This anatomical asymmetry is a constraint any circuit-level theory of top-down modulation must respect.
- **Long-range horizontal connections.** V1 pyramidal axons extending parallel to the cortical surface link cells with similar orientation preferences across retinotopic distances far exceeding the classical RF radius. The columnar specificity of these connections (orientation-aligned cells preferentially connected) is the anatomical substrate for the contour-integration "association field" the review treats as the principal lateral-circuit mechanism.
- **Top-down modulation precedes the stimulus.** Cuing paradigms reveal that V1 firing-rate baselines, and even tuning preferences, shift *before* the cued stimulus appears — top-down signals are not merely a feedback response to feedforward drive but an anticipatory bias that sets the stage for upcoming processing.

## 6. Critique / limitations

The review is a comprehensive *catalogue* of top-down phenomena but is light on mechanistic specifics. The proposed "input gating" mechanism — that descending signals selectively recruit horizontal connections — is presented as a working hypothesis rather than a tested model; the review does not commit to which cell types, which synapses, or which dendritic compartments implement the gate. (Larkum 2013, in the same year, proposed apical-dendrite coincidence detection as a candidate; Bastos et al. 2012 proposed a laminar predictive-coding mapping; Keller & Mrsic-Flogel 2018 later argued for specific prediction-error cell populations. Gilbert & Li 2013 stays agnostic.)

The review treats top-down influence largely as a *modulation* of feedforward-driven activity, without strongly committing to whether the top-down signal is a *prediction* (Rao & Ballard / Friston framework), a *gain control* (Reynolds-Heeger normalization), a *biased competition* (Desimone & Duncan), or a *gating signal* (the authors' preferred framing). Different theoretical accounts predict overlapping single-cell signatures, and the review does not adjudicate.

The data are overwhelmingly from awake-behaving primate single-unit work. Mouse-V1 closed-loop results (Keller, Bonhoeffer & Hübener 2012; Attinger et al. 2017), which arrived just after this review, are not engaged. The relationship between Gilbert & Li's "task-dependent receptive field" framing and the prediction-error / mismatch framing that dominates the modern mouse literature is therefore not worked out here.

Finally, the review is silent on computational implementations. It establishes that top-down influences are pervasive and quantitatively large, but does not connect to deep-network or recurrent-network models in which top-down feedback is implemented in concrete operations. Bridging that gap is what miconi_vanrullen2016_feedback_attention and the user's Recurrent ViT line of work attempt.

A subtler concern: the review's preferred framing — that top-down signals *select* among horizontal-connection inputs — treats the V1 cell as effectively a switch among pre-existing patterns of lateral connectivity. This is a strong commitment that competes with alternatives in which top-down signals *re-weight* feedforward drive directly (gain modulation; Reynolds-Heeger normalization), or *subtract* predicted activity from feedforward drive (Rao-Ballard prediction error). The review does not provide a decisive experimental test that distinguishes input gating from these alternatives, and the experimental signatures it catalogues (firing-rate changes, tuning-curve shifts, contextual modulation) are consistent with multiple mechanisms. From the user's program's perspective, this ambiguity is a feature rather than a bug: the Feedback Transformer's multiplicative Q/K gating sits at the architectural intersection of all three accounts.

## 7. Connection to our work

This paper is *directly* load-bearing for the user's architectural program, on at least four distinct points.

**(i) V1 is not a passive feature extractor.** The user's commitment, across the Recurrent ViT (2502.10955), PRISM v1, PRISM v2, and especially the Video VAE / hierarchical RViT work in the Evolution of Architecture notes, is that attention and memory modulate processing *at the earliest visual stages*, not just downstream. This commitment is empirically anchored in Gilbert & Li 2013. The Recurrent ViT's choice to apply self-attention to patch-level tokens at every recurrent iteration — rather than only at a high-level read-out — is the computational analog of the V1-level top-down modulation the review documents. The published change-detection result is, in this framing, evidence that even a single layer of patch-level recurrent attention is enough to recover task-relevant context modulation.

**(ii) Dual mechanism: descending feedback + lateral connections.** The review's principal mechanistic claim is that top-down modulation is implemented by two interacting routes — long-range corticocortical feedback and long-range horizontal intrinsic connections — and that the former gates the latter. This is precisely the dual structure the user's `bidirectional-hierarchical-feedback` concept captures: descending conv projections from deeper GridCell RNN layers supply the V2/V4-level "context," while the Feedback Transformer's same-level token-token self-attention (within a single GridCell RNN's grid) plays the role of horizontal intrinsic connections. The Feedback Transformer's gating, via Hadamard-product Q/K projections, is the computational analog of Gilbert & Li's input-gating proposal — descending signals modulate which lateral interactions are functionally effective on a given pass.

**(iii) Adaptive, task-dependent tuning.** The Recurrent ViT paper's qualitative finding (`the_user_architectural_program.md` §6) that attention maps "focus, defocus, and reactivate" over recurrent steps — and that the dynamics depend on image semantics — is exactly the V1 adaptive-processor phenomenology the review describes. Each recurrent iteration is a chance for the network's effective receptive field at every patch to reconfigure in response to the accumulating task context, mirroring the dynamic-RF phenomenology in primate V1. The review's emphasis on anticipatory (pre-stimulus) top-down modulation maps onto the role of the persistent recurrent state $H^{(t-1)}$ in the published Recurrent ViT: at every iteration, $H^{(t-1)}$ supplies a task-shaped prior that biases patch-level attention before the next forward sweep even begins, the computational analog of the cue-driven baseline shifts the review documents.

**(iv) Connection to the canonical-microcircuit / predictive-coding literature.** Gilbert & Li 2013 is the empirical companion to bastos2012_canonical_microcircuits (theory of feedforward/feedback laminar routing), keller_mrsic_flogel2018_pc_review (modern PC framing), weiler2025_l6_corticocortical (L6 as the dominant feedback route), and miconi_vanrullen2016_feedback_attention (a deep-network model of exactly the gating phenomenon Gilbert & Li describe). The user's program treats all five as facets of the same architectural commitment; Gilbert & Li 2013 supplies the broadest empirical synthesis on the primate side.

**(v) Specific architectural implications.** The laminar asymmetry the review documents — feedforward from superficial layers, feedback from deep layers — directly motivates the user's choice of asymmetric ascending/descending projections in the hierarchical GridCell stack (`the_user_architectural_program.md` §3): conv-transpose (channel-thin, spatially-broad) for ascending feedback paralleling deep-layer corticocortical projections, and channel-expanding spatially-reducing conv for descending feedforward paralleling superficial-layer routing. The review's observation that feedback effects are stronger when stimuli compete within an RF also supplies an empirical anchor for the user's claim that the Feedback Transformer's softmax-based competition (each token competing for attention budget) is where descending modulation should have its largest computational effect — not on isolated feedforward responses but on the dynamics of intra-token competition.

The review also bears on the user's `competition-emergent-predictive-coding` thesis indirectly. Gilbert & Li note that attentional modulation is sharply amplified when multiple stimuli compete within a receptive field — the Moran-Desimone / Reynolds biased-competition signature. The user's reformulation generalises this from intra-RF stimulus competition to inter-coalition representational competition, with top-down feedback playing the role of opponent-modelling. The review does not anticipate this generalisation, but its empirical observation that *competition is when top-down signals matter most* is consistent with it.

Finally, the review's framing of V1 neurons as "adaptive processors" that change function with task is the cleanest one-line statement of *why* the architectural commitment to recurrent self-attention at the patch level is a biologically motivated choice rather than an arbitrary engineering convenience. A purely feedforward ViT, however deep, cannot exhibit the within-image dynamics Gilbert & Li document; only an architecture in which V1-level features can be re-read after top-down context has propagated can. The Recurrent ViT is the minimum architecture that exhibits this property, and the user's larger program scales the same commitment to a full multi-layer cortex-like hierarchy.

**(vi) Contrast with the published Recurrent ViT's conservative framing.** The Recurrent ViT manuscript (2502.10955) frames its recurrent-attention mechanism as a sequence-modelling tool for change-detection without strong neuroscience commitments. The user's program, anchored in this review, takes a stronger position: patch-level recurrent attention is the computational implementation of the V1-level top-down modulation Gilbert & Li document. Adopting that stronger framing in a follow-up paper would warrant Gilbert & Li 2013 as a primary citation alongside Felleman & Van Essen 1991 and the canonical-microcircuit literature.

## 8. Citations to follow

- `field_hayes_hess1993_association_field` — the psychophysical "association field" construct underlying the contour-integration discussion. Not yet in seed.
- `kapadia_ito_gilbert_westheimer1995_v1_contextual` — Gilbert lab single-unit demonstration of contextual modulation in V1. Not yet in seed.
- `crick_koch1998_consciousness_v1` — feedback to V1 and the role of recurrence in awareness. Not yet in seed.
- `lamme_roelfsema2000_distinct_feedforward_feedback` — the cleanest theoretical separation of feedforward and feedback contributions to visual processing. Not yet in seed.
- `li_piech_gilbert2004_perceptual_learning_v1` — V1 single-unit changes with perceptual learning. Not yet in seed.
- `schoups_vogels_qian_orban2001_practising_orientation` — perceptual-learning effects on V1 orientation tuning. Not yet in seed.
- `kastner_ungerleider2000_attention_review` — companion review on attentional modulation in human visual cortex (fMRI). Not yet in seed.
- `larkum2013_apical_basal` — apical-dendrite coincidence detection as a candidate implementation of the gating proposal. Already in seed.
- `keller_mrsic_flogel2018_pc_review` — modern circuit-level predictive-processing review that complements Gilbert & Li. Already in seed; full depth.
- `bastos2012_canonical_microcircuits` — laminar predictive-coding microcircuit. Already in seed.
- `weiler2025_l6_corticocortical` — the L6 anatomical substrate for the descending route the review invokes. Already in seed.
- `miconi_vanrullen2016_feedback_attention` — deep-network computational model of feedback-gated attention. Already in seed.
- `baluch_itti2011_topdown_mechanisms` — companion review situating top-down attention in computational models. Already in seed.
