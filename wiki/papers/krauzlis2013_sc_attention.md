---
id: krauzlis2013_sc_attention
title: "Superior colliculus and visual spatial attention"
authors:
  - "Krauzlis, Richard J."
  - "Lovejoy, Lee P."
  - "Zénon, Alexandre"
year: 2013
venue: "Annual Review of Neuroscience"
doi: "10.1146/annurev-neuro-062012-170249"
arxiv: ""
url: "https://doi.org/10.1146/annurev-neuro-062012-170249"
tags:
  - primate-neurophysiology
  - subcortical
  - review
  - visual-attention
  - lesion-microstimulation
concepts:
  - priority-map
  - top-down-feedback
  - attentional-spotlight
related:
  - cavanaugh_wurtz2004_sc_change_blindness
  - herman_krauzlis2017_sc_change_detection
  - moore_armstrong2003_fef_microstim
  - bisley_goldberg2010_parietal_priority
  - posner1980_orienting
  - herman_arcizet2020_caudate_sc
  - hu_dan2021_ic_sc_attention
  - bollimunta2018_fef_sc_covert
  - muller2005_sc_microstim_covert
  - zenon_krauzlis2012_attention_deficits
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_81
status: full
depth: full
last_updated: "2026-05-16"
---

# Superior colliculus and visual spatial attention

## 1. Abstract

The superior colliculus (SC) has long been known to be part of the network of brain areas involved in spatial attention, but recent findings have *dramatically refined* understanding of its functional role. The SC both *implements the motor consequences of attention* and plays a *crucial role in the process of target selection* that precedes movement. Moreover, even in the absence of overt orienting movements, SC activity is related to shifts of *covert* attention and is *necessary* for the normal control of spatial attention during perceptual judgments. The neuronal circuits that link the SC to spatial attention may include attention-related areas of the cerebral cortex, but recent results show that the SC's contribution involves mechanisms that operate *independently* of the established signatures of attention in visual cortex. These findings raise new issues and suggest novel possibilities for understanding the brain mechanisms that enable spatial attention.

## 2. Why this matters for us

Krauzlis, Lovejoy & Zénon 2013 is the canonical *modern review* of the SC's role in attention. It establishes that the SC is *not just* a motor structure (saccade generator) but is a *primary* substrate of spatial attention — and that its contribution is partially *independent* of cortical attention mechanisms. For the user's program, this paper is the load-bearing reference for treating the SC as a parallel substrate of attention alongside cortical sources (FEF, LIP, dlPFC). The recurrent ViT's attention map, by analogy, is partly a model of SC priority-map dynamics, not just of cortical attention computations.

## 3. Key claims

1. **SC contributes to covert attention.** SC activity is correlated with covert attention shifts, even when no overt eye movement occurs. This is a substantive shift from the older view that SC is purely a saccade-execution structure.
2. **SC is *necessary* for normal attention.** Lesion and inactivation studies show that SC inactivation specifically impairs attentional task performance, beyond any impairment of saccade execution.
3. **SC implements *both* motor and attentional consequences.** The intermediate layers of SC integrate visual sensory input, attentional priority signals, and motor planning. The same neurons can contribute to multiple functions depending on context.
4. **SC's contribution is partially independent of cortical mechanisms.** Some attentional signatures (e.g., performance benefits at cued locations) survive SC inactivation; others are eliminated. This dissociation argues that the SC and cortex contribute *partially distinct* attentional signals.
5. **SC is a priority-map substrate.** Like LIP (Bisley & Goldberg 2010), SC has the structural properties of a priority map: spatial topography, integration of bottom-up and top-down inputs, and downstream control of motor and attentional behaviors.
6. **Microstimulation studies confirm causality.** Subthreshold SC stimulation produces attention-like behavioral effects (Cavanaugh & Wurtz 2004), supporting the causal role.
7. **SC's input sources include LIP, FEF, and direct retinal input.** The SC is positioned to receive both cortical attention signals and bottom-up sensory information, integrating them into a unified priority signal.

## 4. Methods

A narrative review covering primate single-unit recording, microstimulation, and lesion / inactivation studies of SC during attention tasks. The Krauzlis lab and others' contributions over decades are synthesized into the modern view of SC as an *attention-relevant* structure.

The review's principal arguments rest on:
- **Single-unit recordings** showing SC activity modulated by attention even in the absence of saccades.
- **Microstimulation** producing behavioral attention-like effects (Cavanaugh & Wurtz 2004; Müller et al. 2005).
- **Inactivation studies** producing attention deficits independent of saccade-execution deficits.
- **Comparison studies** showing SC vs cortical signatures of attention dissociate under specific manipulations.

## 5. Results

The principal empirical claims the review consolidates:

- **Covert attention modulation in SC.** SC neurons in intermediate layers show enhanced responses to attended stimuli, even when no eye movement is planned or executed.
- **SC inactivation impairs covert attention.** Reversible inactivation (muscimol injection) of SC produces specific deficits in covert attention tasks, separable from saccade-execution deficits.
- **SC microstimulation shifts attention.** Subthreshold SC stimulation at a specific retinotopic site produces attention-like behavioral effects at that location (faster RT, better detection).
- **Independence from cortical signatures.** Some attention effects in V4 and other visual cortex are *preserved* under SC inactivation; this suggests SC and cortex contribute distinct signals. Conversely, some behavioral attention effects are *eliminated* under SC inactivation but the cortical signatures remain — showing the SC contribution is behaviorally important but not via the cortical attention modulation.
- **SC is upstream of attention-related caudate activity.** Herman, Arcizet & Krauzlis 2020 ([herman_arcizet2020_caudate_sc](research_db/papers/herman_arcizet2020_caudate_sc.md)) shows that attention-related caudate modulation requires intact SC — establishing the SC's upstream role in the broader attention network.

## 6. Critique / limitations

The review is *primate-focused*. Mouse SC has been less studied for attention; some properties may differ between species.

The "independence from cortical mechanisms" claim is *partial*. SC and cortex are anatomically connected (LIP and FEF project to SC; SC projects back via thalamus). The dissociation between SC and cortex is about *which* attention signatures survive which manipulations — not about the SC being a fully independent attention system.

The framework characterizes SC as a *priority-map substrate*. The specific *content* of the SC priority map (which features are prioritized, on what timescales) is less fully developed than for LIP. Subsequent work (e.g., Herman & Krauzlis 2017 for color) has begun to fill this in.

The review predates the more recent optogenetic work in mouse SC (e.g., Hu & Dan 2021, [hu_dan2021_ic_sc_attention](research_db/papers/hu_dan2021_ic_sc_attention.md)) that has further refined the cellular contributions to attention. The 2013 framework is the macaque-electrophysiology synthesis; mouse-optogenetic refinements have followed.

The review doesn't engage with predictive-coding or precision-weighting interpretations. The SC's role is characterized in *priority-map* terms, not in PC terms. The two frameworks are compatible but not made explicit.

## 7. Connection to our work

This paper supports several architectural commitments in the user's program:

**SC as a parallel substrate for the recurrent ViT.** The recurrent ViT's attention map is partly modeled on cortical attention sources (FEF, LIP) and partly on subcortical (SC). Krauzlis et al. 2013 is the canonical citation for the SC's role in covert attention — the foundational support for treating subcortical attention sources as comparable to cortical ones.

**The SC as a *priority-map* in the user's program.** The Krauzlis-Bisley-Goldberg framework treats SC and LIP as parallel priority-map substrates. The user's central self-attention substrate ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) is the AI homolog of *both* SC and LIP combined; the architecture doesn't distinguish them.

**SC microstimulation as the analog of model perturbation.** The 2502.10955 perturbation experiment is conceptually analogous to SC microstimulation (Cavanaugh & Wurtz 2004) and FEF microstimulation (Moore & Armstrong 2003). Both attention sources can be perturbed to produce attention-like behavioral effects; the user's model perturbation is the network-level analog.

**SC's covert-attention role.** The recurrent ViT models *covert* attention (no eye movements; attention is internal to the model). Krauzlis et al. 2013 establishes that the SC's role in *covert* attention — not just overt saccade-target-selection — is robust. The user's covert-attention architecture is biologically warranted.

**Independence from cortex for some attention effects.** Krauzlis's finding that some attention effects survive SC inactivation while others don't is methodologically useful for the user's program: model ablation experiments should expect that perturbing one attention substrate (e.g., the Feedback Transformer's feedback projection) may preserve some attention effects while eliminating others. The dissociation pattern is a target for the user's program's ablation experiments to reproduce.

The recurrent ViT paper cites Krauzlis et al. 2013 in its bibliography (ref [81]). Future manuscripts on the recurrent ViT's attention mechanism should cite this paper for the SC's role.

## 8. Citations to follow

- `cavanaugh_wurtz2004_sc_change_blindness` — foundational SC microstim attention. In seed, full depth.
- `herman_krauzlis2017_sc_change_detection` — Krauzlis lab's color-change result. In seed, full depth.
- `moore_armstrong2003_fef_microstim` — FEF parallel. In seed, full depth.
- `bisley_goldberg2010_parietal_priority` — LIP priority map. In seed, full depth.
- `bollimunta2018_fef_sc_covert` — FEF vs SC covert attention. In seed.
- `lovejoy_krauzlis2010_inactivating_sc` — Lovejoy & Krauzlis SC inactivation. Not in seed.
- `zenon_krauzlis2012_attention_deficits` — Zénon & Krauzlis attention deficits. In seed.
- `muller2005_sc_microstim_covert` — SC microstim and covert attention. In seed.
- `herman_arcizet2020_caudate_sc` — Herman, Arcizet, Krauzlis caudate-SC. In seed.
