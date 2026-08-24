---
id: knudsen2007_fundamental_components
title: "Fundamental components of attention"
authors:
  - "Knudsen, Eric I."
year: 2007
venue: "Annual Review of Neuroscience"
doi: "10.1146/annurev.neuro.30.051606.094256"
arxiv: ""
url: "https://doi.org/10.1146/annurev.neuro.30.051606.094256"
tags:
  - visual-attention
  - review
  - theoretical-essay
concepts:
  - biased-competition
  - top-down-feedback
  - gain-modulation
  - attentional-template
  - working-memory-persistent-activity
  - priority-map
related:
  - desimone_duncan1995_biased_competition
  - miller_cohen2001_pfc_function
  - awh2006_attention_wm
  - bisley_goldberg2010_parietal_priority
  - treue_martinez_trujillo1999_feature_attention
  - gilbert_li2013_topdown
  - reynolds_heeger2009_normalization
  - sridharan2017_sc_sensitivity_bias
  - moran_desimone1985_selective_attention
  - itti_koch2001_saliency_review
  - koch_ullman1984_winner_takes_all
  - bundesen2005_neural_theory_attention
  - posner1980_orienting
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_75
status: full
depth: full
last_updated: "2026-05-16"
---

# Fundamental components of attention

## 1. Abstract

A mechanistic understanding of attention is necessary for the elucidation of the neurobiological basis of conscious experience. This chapter presents a framework for thinking about attention that facilitates the analysis of this cognitive process in terms of underlying neural mechanisms. Four processes are fundamental to attention: working memory, top-down sensitivity control, competitive selection, and automatic bottom-up filtering for salient stimuli. Each process makes a distinct and essential contribution to attention. Voluntary control of attention involves the first three processes (working memory, top-down sensitivity control, and competitive selection) operating in a recurrent loop. Recent results from neurobiological research on attention are discussed within this framework.

## 2. Why this matters for us

Knudsen 2007 is the most direct conceptual ancestor of the user's multi-hub framing. Where Desimone & Duncan 1995 supplied the competition substrate, and Reynolds & Heeger 2009 supplied a computational form (normalization), Knudsen supplied the *decomposition*: attention is not one mechanism but four, operating together in a recurrent loop. The user's program — a Feedback Transformer that integrates bottom-up sensory input with multiple recurrent feedback states (RL hub, decoder hub, slow memory) — is, at the architectural level, an instantiation of Knudsen's four-process scheme. Each component has a structural analog in the user's architecture: working memory ↔ PRISM ConvGRU plus slow memory; competitive selection ↔ competition-emergent-PC and the attention map itself; top-down sensitivity control ↔ FBA / FiLM modulation; top-down bias ↔ the Feedback Transformer. This paper supplies the textbook-level claim that a multi-hub architecture is the *right* shape for an attention system, independent of any specific implementation choice.

## 3. Key claims

1. **Attention decomposes into four fundamental processes**: (a) working memory, (b) top-down sensitivity control, (c) competitive selection, and (d) automatic bottom-up filtering for salient stimuli. Each is necessary; none is sufficient.
2. **Working memory is constitutive of attention**, not merely correlated with it. The maintained content of WM specifies what is being attended; sustained activity in prefrontal and parietal cortex is the candidate substrate.
3. **Top-down sensitivity control is gain modulation**. Higher-order regions (PFC, parietal) project descending signals that adjust the gain/responsiveness of early sensory neurons in a content-specific way, increasing the signal-to-noise of attended representations *before* the competitive stage.
4. **Competitive selection is the winner-take-all stage**. Multiple candidate representations compete for control of downstream processing; the winner becomes the focus of conscious attention. The substrate is the receptive-field-level competition documented by Moran & Desimone 1985 and Desimone & Duncan 1995, plus priority maps in parietal cortex and superior colliculus.
5. **Bottom-up salience filtering is automatic and exogenous**. Stimulus-driven properties (luminance contrast, novelty, motion) are filtered for behavioral relevance in early sensory pathways, independently of voluntary control. This is the Koch & Ullman 1984 / Itti & Koch 2001 saliency pathway.
6. **The first three processes operate in a recurrent loop.** WM holds the goal; sensitivity control adjusts gain to favor goal-relevant features; competitive selection picks the winner; the winner updates WM. The loop is the substrate of *voluntary* (endogenous) attention.
7. **Bottom-up filtering interacts with the loop but is not part of it.** Salient stimuli inject novel candidates into the competitive-selection stage that the WM-driven loop would otherwise have suppressed, accounting for involuntary attentional capture.
8. **The framework is cross-species and cross-modality.** The four processes can be identified in vertebrates from owls (Knudsen's own auditory-spatial work in the barn owl) through primates, and apply across visual, auditory, and somatosensory modalities.

## 4. Methods

A theoretical / synthetic review. Knudsen synthesizes results from his own work on the barn-owl auditory space map and the optic tectum (an evolutionary homolog of the superior colliculus) with the primate visual-attention literature (Desimone, Duncan, Reynolds, Maunsell, Goldberg, Bisley) and the human working-memory and saliency literatures. There are no new experiments; the contribution is the four-component decomposition and its mapping onto a recurrent-loop architecture.

The argument structure is:
- Step 1: argue from behavioral and clinical phenomena (neglect, attentional blink, change blindness, capture) that no single mechanism can explain the range of attentional phenomena.
- Step 2: identify the four candidate processes as the minimal set that accounts for the phenomenology.
- Step 3: map each process onto a neural substrate (PFC/PPC for WM; PFC/PPC descending projections for sensitivity control; V1–V4 receptive-field competition plus LIP/SC priority maps for competitive selection; SC / pulvinar bottom-up pathways for salience filtering).
- Step 4: assemble the substrates into a recurrent loop and show how each empirical signature (cueing effects, WM-driven attention, exogenous capture, neglect) follows from disturbing one node of the loop.

## 5. Results

The review's "results" are the empirical signatures the four-component framework predicts and accommodates:

- **Working-memory templates bias subsequent perception.** Holding a feature in WM (e.g., "find the red item") biases attention toward matching stimuli, even when WM content is task-irrelevant (Soto et al.; Olivers et al. — both subsequent confirmations).
- **Gain modulation of single units in V1/V2/V4** by attention is ≈20–50% in primate single-unit data (Treue & Martinez-Trujillo 1999 feature attention; McAdams & Maunsell 1999; Reynolds & Chelazzi 2004). This is the sensitivity-control signature.
- **Receptive-field-level competition in V4/IT** when two stimuli fall in one RF (Moran & Desimone 1985). This is the competitive-selection signature.
- **Priority maps in LIP and SC** integrate top-down and bottom-up signals into a single attentional priority code (Bisley & Goldberg 2010 — published after Knudsen but anticipated by him). The maps' read-out drives both overt eye movements and covert attention.
- **Saliency-driven capture** by abrupt onsets, luminance contrast, or motion is automatic and resistant to voluntary suppression (Itti & Koch 2001; Theeuwes literature). This is the bottom-up filter signature.
- **Lesion dissociations.** PFC lesions impair WM and top-down control; parietal lesions impair competitive selection and produce neglect; SC/pulvinar lesions impair salience-driven capture. Each lesion isolates one node of the four-component loop.

## 6. Critique / limitations

The framework is *qualitative*. It specifies the components and their interactions but does not commit to a computational form for any one of them. The competitive selection stage, in particular, is described in winner-take-all language; whether it is implemented by divisive normalization (Reynolds & Heeger 2009), predictive coding (Spratling 2008), or biased competition (Desimone & Duncan 1995) is left open. The same is true for sensitivity control — gain modulation is named, but the actual gain function and its biophysical basis are not specified.

The decomposition is *modular* in a way that real cortex is not. Knudsen treats WM, sensitivity control, and competitive selection as separable modules with distinct neural substrates. In practice the substrates overlap heavily: LIP encodes WM, priority, and salience simultaneously (Bisley & Goldberg 2010); PFC encodes WM and provides top-down control (Miller & Cohen 2001); even V4 shows attentional gain modulation that is partly WM-driven (Awh et al. 2006). The modular language is a useful framing but understates the integration.

The recurrent loop is *underspecified temporally*. Knudsen treats the loop as cyclic but does not characterize its frequency, phase, or relationship to neural oscillations. Subsequent rhythmic-attention literature (Fiebelkorn & Kastner; Helfrich; Landau & Fries) shows attention has a ≈4–8 Hz sampling rhythm with discrete phases — a level of temporal structure the 2007 framework does not anticipate.

The bottom-up filter is described as automatic and obligatory. Subsequent selection-history literature (Failing & Theeuwes 2018) shows that "automatic" capture is partly history-driven and therefore not strictly bottom-up. The clean exogenous / endogenous split Knudsen draws is increasingly blurred in the empirical record.

The framework is silent on *learning*. It describes the steady-state operation of an adult attention system but says nothing about how the components are wired up developmentally, or how the loop's parameters are tuned to task demands. This is appropriate for a 2007 review but means the framework does not directly engage with the machine-learning version of the same questions (meta-learning, learned attention).

The framework is also silent on the *operational signatures* that distinguish the components in behavior. Sridharan et al. 2017 — a decade later — supplied the operational decomposition (perceptual sensitivity vs choice bias via SDT and m-ADC) that Knudsen's conceptual decomposition lacked. Knudsen's framework names the components; Sridharan's operationalizes them.

## 7. Connection to our work

This paper is, more than any other single citation, the textbook-level justification for the user's multi-hub architectural program. The four-component decomposition is the most direct conceptual ancestor of the user's multi-hub framing.

**The four components map directly onto the user's architecture.**

- **Working memory ↔ PRISM ConvGRU + slow memory.** Knudsen's WM is the maintained content that specifies what is being attended. PRISM v1's ConvGRU (`THESIS.md` §2.3) maintains a per-pixel spatially-structured memory; PRISM v2's slow memory (`PRISM_V2_PROPOSAL.md` §3.3) maintains a longer-timescale task-relevant context. Together they instantiate Knudsen's WM at two timescales — the fast/slow split that Mujika et al. 2017 and Tallec & Ollivier 2018 argued is necessary for stable recurrent computation.
- **Competitive selection ↔ competition-emergent-PC and the central attention map.** Knudsen's competitive-selection stage is the winner-take-all over candidate representations. The user's competition-emergent-PC thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) generalizes this from receptive-field-level competition to coalition-level competition for control of the central self-attention map. The attention map itself — softmax over Q·K — is a soft winner-take-all and therefore a direct mechanistic instantiation of Knudsen's competitive-selection node.
- **Sensitivity control ↔ FBA / FiLM modulation.** Knudsen's top-down sensitivity control adjusts neural gain in a content-specific way before competition. PRISM v1's FiLM modulation (`THESIS.md` §2.4) and PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) inject γ, β scaling at the input of the feature stack — gain modulation in the exact sense Knudsen intends. Feature-Based Attention (Treue & Martinez-Trujillo 1999) is the primate-neurophysiology evidence for the same gain mechanism.
- **Top-down bias ↔ the Feedback Transformer.** Knudsen's framework requires a route by which WM content reaches the competitive-selection stage to bias it. The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) is exactly this route in the user's architecture: it admits recurrent feedback states (drawn from WM, RL, decoder hubs) into the Q/K/V projections that drive the central attention competition. The Hadamard combination of sensory and feedback projections is the bias operation.

**The recurrent-loop structure is the user's architectural commitment.** Knudsen's central claim is that voluntary attention requires the first three processes operating in a *recurrent loop*. The user's architecture commits to this: feedforward sensory input enters the Feedback Transformer; the output updates the GridCell RNN states (WM); the updated states feed back into the next Feedback Transformer pass (bias); the bias adjusts the next competitive selection; the selection updates the GridCell RNN again. This is Knudsen's loop, instantiated. The Recurrent ViT paper (2502.10955) describes the single-step version of this loop; the iterative-VAE construction ([iterative_variational_encoder_decoder](research_db/concepts/iterative_variational_encoder_decoder.md)) runs the loop for $n_{FR}$ encoder steps and $n_{BR}$ decoder steps.

**The framework supports the multi-hub program at the architectural level.** Knudsen does not propose multi-hub competition (his framework is single-stream within a modality), but the *shape* of his decomposition — multiple components, each with a distinct role, integrated by a recurrent loop — is the shape of the user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)). The user's contribution is to scale the four-process scheme from within-modality components to across-hub coalitions, with each hub potentially implementing its own internal four-process loop.

**Cross-reference with Sridharan 2017.** Knudsen 2007 is the *conceptual* decomposition; Sridharan et al. 2017 (`papers/sridharan2017_sc_sensitivity_bias.md`) is the *operational* decomposition. Sridharan uses signal-detection theory and the m-ADC model to behaviorally dissociate sensitivity (Knudsen's sensitivity control output) from choice bias (Knudsen's WM / template output) and shows that SC microstimulation modulates sensitivity selectively. The pair is load-bearing: cite Knudsen for the framework, Sridharan for the operational test.

**Connection to other entries.** The four-component framework anchors a cluster of cross-references:
- [desimone_duncan1995_biased_competition](papers/desimone_duncan1995_biased_competition.md): supplies the competitive-selection substrate.
- [miller_cohen2001_pfc_function](papers/miller_cohen2001_pfc_function.md): supplies the WM and top-down-control substrate in PFC.
- [awh2006_attention_wm](papers/awh2006_attention_wm.md): supplies the WM-attention link Knudsen invokes as constitutive.
- [bisley_goldberg2010_parietal_priority](papers/bisley_goldberg2010_parietal_priority.md): supplies the parietal priority map that integrates sensitivity-control and competitive-selection outputs.
- [treue_martinez_trujillo1999_feature_attention](papers/treue_martinez_trujillo1999_feature_attention.md): supplies the gain-modulation signature of sensitivity control.
- [gilbert_li2013_topdown](papers/gilbert_li2013_topdown.md): supplies the descending-projection anatomy that implements top-down bias.
- [reynolds_heeger2009_normalization](papers/reynolds_heeger2009_normalization.md): supplies the computational form (normalization) for competitive selection.
- [sridharan2017_sc_sensitivity_bias](papers/sridharan2017_sc_sensitivity_bias.md): supplies the operational dissociation that Knudsen's conceptual decomposition predicted.

## 8. Citations to follow

- `koch_ullman1984_winner_takes_all` — Knudsen's competitive-selection node is descended from this paper's winner-take-all account. In seed.
- `itti_koch2001_saliency_review` — Knudsen's bottom-up filter is the saliency pathway. In seed.
- `moran_desimone1985_selective_attention` — Knudsen's competitive-selection substrate. In seed.
- `bundesen2005_neural_theory_attention` — TVA, a contemporaneous formal theory of attention overlapping Knudsen's framework in scope. In seed.
- `duncan2010_review_attention` — Duncan's later integrative review that revisits the biased-competition / four-component synthesis. Not in seed; candidate for future addition.
- `posner1980_orienting` — the cueing paradigm whose effects Knudsen's framework must accommodate. In seed.
- `petersen_posner2012_attention_20y` — Petersen & Posner's complementary three-network framework (alerting, orienting, executive). Not in seed; candidate for future addition.
- `corbetta_shulman2002_control_attention` — the dorsal/ventral attention-network framework, complementary to Knudsen's components. Not in seed; candidate for future addition.
- `kastner_ungerleider2000_attention_review` — the canonical fMRI-based attention review of the same era. Not in seed; candidate for future addition.
