---
id: bisley_mirpour2019_priority_map
title: "The neural instantiation of a priority map"
authors:
  - "Bisley, James W."
  - "Mirpour, Koorosh"
year: 2019
venue: "Current Opinion in Psychology"
doi: "10.1016/j.copsyc.2019.01.002"
arxiv: ""
url: "https://doi.org/10.1016/j.copsyc.2019.01.002"
tags:
  - primate-neurophysiology
  - parietal-cortex
  - prefrontal-cortex
  - subcortical
  - review
  - visual-attention
concepts:
  - priority-map
  - top-down-feedback
  - attentional-spotlight
related:
  - bisley_goldberg2010_parietal_priority
  - krauzlis2013_sc_attention
  - moore_armstrong2003_fef_microstim
  - desimone_duncan1995_biased_competition
  - mirpour2010_ppc_microstim
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_98
status: full
depth: full
last_updated: "2026-05-16"
---

# The neural instantiation of a priority map

## 1. Abstract

The term *priority map* is commonly used to describe a map of the visual scene in which objects and locations are represented by their *attentional priority* — itself a combination of low-level salience and top-down control. Bisley & Mirpour examine how such a map may be represented at the neuronal level. They propose that there is **not a single, common map** in the brain, but that a number of cortical areas work together to generate the resultant behavior. Specifically: the lateral intraparietal area (LIP) of posterior parietal cortex provides a *simple representation of attentional priority*, which *remaps across saccades* so that there is an apparent allocentric map in a region with retinocentric encoding scheme. The frontal eye field (FEF) of prefrontal cortex receives the responses from LIP but can *suppress* them to control the flow of eye-movement behavior. The intermediate layers of the superior colliculus (SCi) reflect the *final saccade goal*. Together, these areas function to guide eye movements and may play a similar role in allocating covert visual attention.

## 2. Why this matters for us

Bisley & Mirpour 2019 is the *modern multi-area* synthesis of priority-map computation in primate brain. It refines Bisley & Goldberg 2010 ([bisley_goldberg2010_parietal_priority](research_db/papers/bisley_goldberg2010_parietal_priority.md)) by emphasizing that priority is not implemented in one place but is *distributed* across LIP, FEF, and SC, with different roles for each. For the user's program, this paper supports the architectural commitment that *no single layer or hub* computes the full attention map — different aspects (priority computation, suppression, motor selection) are distributed across components. The recurrent ViT's attention map is therefore a *unified* AI homolog of what biology splits across multiple substrates.

## 3. Key claims

1. **Priority is distributed.** No single brain region computes "the" priority map. LIP, FEF, and SCi each contribute distinct aspects.
2. **LIP supplies the basic priority representation.** LIP encodes attentional priority (combining bottom-up salience with top-down control) with retinotopic / spatial topography.
3. **LIP priority remaps across saccades.** When the eye moves, the LIP representation of a stable-in-world location moves on the LIP map so that the world-centered location stays consistent. This is *predictive remapping* — a form of perceptual stability.
4. **FEF receives but can suppress LIP signals.** Frontal eye field can *modulate* the priority signal it receives from LIP — including suppressing locations to prevent eye movements there. This is the "flow control" role of FEF.
5. **SCi reflects the final saccade goal.** By the time priority reaches the intermediate layers of SC, it is consolidated into a final saccade-target choice. SCi represents *what the eyes will do*, not the upstream priority computation.
6. **Covert attention may use the same machinery.** The areas that guide overt saccades (LIP, FEF, SCi) are likely the same ones that guide covert attention. The architecture is shared between covert and overt attention.
7. **Predictive remapping is an integral part of the priority computation.** Remapping isn't a downstream consequence; it's *part* of how the priority map is computed across the saccade transition.

## 4. Methods

A narrative review covering primate single-unit recording in LIP, FEF, and SC during attention and saccade tasks. The Bisley-Mirpour lab and others' contributions are synthesized into the distributed-priority-map framework.

The review emphasizes:
- **Single-unit evidence** for distinct roles of LIP, FEF, SCi.
- **Inactivation evidence** that each area contributes uniquely to behavior.
- **Connectivity** that allows the distributed computation (LIP → FEF, FEF → SCi, LIP → SCi).

## 5. Results

The principal empirical claims the review consolidates:

- **LIP priority signal.** LIP cells encode both stimulus salience (bottom-up) and task-relevance (top-down), with activity proportional to overall priority at each location.
- **Predictive remapping.** Around the time of a saccade, LIP cells with RFs that *will* contain a stimulus after the saccade begin to respond, even before the eye movement completes. This remapping requires anticipated input from the eye-movement command.
- **FEF suppression.** FEF can suppress LIP-derived priority signals at task-irrelevant locations, effectively controlling which locations get further processing or saccade selection.
- **SCi as the final saccade goal.** SCi activity at a specific retinotopic site predicts the saccade direction; the activity is the "final answer" of the saccade-selection computation.
- **Covert attention parallels.** Behavioral and neural signatures of covert attention closely match those of saccade target selection, suggesting shared circuitry.

## 6. Critique / limitations

The framework is *primate-focused*. Mouse and other species have less elaborate posterior parietal cortex; the LIP-equivalent in mouse is contested. Generalization across species is plausible but not directly addressed.

The review focuses on the *spatial* aspects of priority. Feature-based and object-based attention engage additional mechanisms (ventral stream, IT) not addressed here.

The "distributed" claim is presented as a refinement over a "single priority map" view but the relative contributions of LIP, FEF, SCi are still being worked out. The review presents the framework; specific contributions are quantified in subsequent papers.

The temporal dynamics of the priority computation across LIP → FEF → SCi are not exhaustively characterized. How information flows in time, and what each area's "snapshot" of priority looks like at different latencies, is an active research area.

The framework doesn't engage with predictive-coding or precision-weighting interpretations explicitly. The priority computation is described in salience-vs-control terms; the predictive-coding reinterpretation (priority as inverse variance, or as posterior probability) is consistent but not made.

## 7. Connection to our work

This paper supports the user's architectural commitments at the *distributed-mechanism* level:

**No single "attention" layer in the architecture.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) distributes attention computation across multiple hubs and a central self-attention substrate. Bisley & Mirpour's "distributed priority" framing is the biological precedent: attention isn't computed in one place; it's distributed.

**The Feedback Transformer as the unified architectural homolog.** The user's program *unifies* what biology distributes. The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) combines bottom-up sensory input and top-down feedback in a single architectural primitive. Biology does this across multiple regions; the user's architecture compresses the computation. Future architectural variants could *explicitly* distribute attention computation across multiple architectural components (one for LIP-like priority, one for FEF-like suppression, one for SCi-like target selection) — a future direction motivated by Bisley & Mirpour 2019.

**Predictive remapping as a future model feature.** Bisley & Mirpour emphasize the *predictive remapping* of priority across saccades. The recurrent ViT does not produce overt saccades, so remapping is not architecturally needed; however, the *prediction* of where information will be relevant in the next timestep — across an attention shift — is the same kind of computation. PRISM v2's slow memory could be extended to perform predictive-remapping-style updates, anticipating which locations will be relevant at the next timestep.

**Suppression in FEF as a future-direction architectural feature.** The framework treats FEF as a *suppression* substrate that prevents inappropriate eye movements. The user's program currently emphasizes *enhancement* via multiplicative feedback; an explicit *suppression* pathway (analogous to FEF's role in the priority map) would be a useful architectural addition.

**Multi-component priority computation in the multi-hub system.** Each hub in the user's multi-hub system could be interpreted as one of Bisley & Mirpour's distributed priority-map components: the RL hub contributes outcome-priority signals (FEF-like control); the MSI hub contributes sensory-priority signals (LIP-like priority); the central attention substrate combines them into the final selection (SCi-like target selection). This is one of several mappings that the architectural framework admits.

The recurrent ViT paper cites Bisley & Mirpour 2019 in its bibliography (ref [98]). Future manuscripts that elaborate the distributed-attention framework should cite this paper as the modern multi-area synthesis.

## 8. Citations to follow

- `bisley_goldberg2010_parietal_priority` — earlier LIP-focused review. In seed, full depth.
- `krauzlis2013_sc_attention` — SC review. In seed, full depth.
- `moore_armstrong2003_fef_microstim` — FEF microstim. In seed, full depth.
- `mirpour2010_ppc_microstim` — PPC microstim and priority. In seed.
- `bisley_goldberg2003_lip_remapping` — LIP remapping foundation. Not in seed.
- `desimone_duncan1995_biased_competition` — biased competition (priority precursor). In seed, full depth.
- `goldberg2002_attention_parietal` — early LIP-attention review. Not in seed.
