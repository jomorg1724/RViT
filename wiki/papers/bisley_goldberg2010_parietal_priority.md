---
id: bisley_goldberg2010_parietal_priority
title: "Attention, intention, and priority in the parietal lobe"
authors:
  - "Bisley, James W."
  - "Goldberg, Michael E."
year: 2010
venue: "Annual Review of Neuroscience"
doi: "10.1146/annurev-neuro-060909-152823"
arxiv: ""
url: "https://doi.org/10.1146/annurev-neuro-060909-152823"
tags:
  - primate-neurophysiology
  - parietal-cortex
  - review
  - visual-attention
concepts:
  - priority-map
  - attentional-spotlight
  - top-down-feedback
related:
  - krauzlis2013_sc_attention
  - moore_armstrong2003_fef_microstim
  - boshra_kastner2022_attention_control
  - desimone_duncan1995_biased_competition
  - silver2005_topographic_parietal
  - bisley_mirpour2019_priority_map
  - mirpour2010_ppc_microstim
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_74
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Attention, intention, and priority in the parietal lobe

## 1. Abstract

For many years there has been a debate about the role of the parietal lobe in the generation of behavior: does it generate movement plans (intention) or does it choose objects in the environment for further processing (attention)? Bisley & Goldberg propose a unifying answer through their analysis of the lateral intraparietal area (LIP), which has been shown to play independent roles in target selection for saccades and the generation of visual attention. Based on results from a variety of tasks, they propose that LIP acts as a **priority map** in which objects are represented by activity proportional to their behavioral priority. The priority map combines bottom-up inputs (e.g., a rapid visual response) with an array of top-down signals (e.g., a saccade plan, attentional bias). The spatial location representing the peak of the map is used by the oculomotor system to target saccades and by the visual system to guide visual attention. The framework resolves the attention-versus-intention debate by making both downstream consequences of a shared *priority* representation.

## 2. Why this matters for us

Bisley & Goldberg 2010 is the canonical reference for the *priority map* concept: a representation of behavioral importance over visual space that drives both attention and overt action. This is the biological substrate of the user's central self-attention substrate ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)), which serves the same role — a shared map of importance/priority that integrates contributions from many hubs and guides both attention and action. The recurrent ViT (2502.10955) implicitly computes a priority map: the self-attention map peaks at locations the model treats as relevant, and behavioral output (change-detection accuracy) depends on the peak's location. Bisley & Goldberg supplies the neurobiological framework for thinking about what that attention map *is* and what it's *for*.

## 3. Key claims

1. The role of the parietal lobe (specifically LIP) has been debated as either an *attention map* (target selection) or an *intention map* (saccade plan). The two are not separable functionally; the same LIP neurons can be shown to participate in both.
2. The resolution: LIP implements a **priority map** — a representation of *behavioral priority* at each location in visual space, with activity proportional to how behaviorally important that location is.
3. The priority map combines *bottom-up* signals (rapid visual responses to salient stimuli) and *top-down* signals (saccade plans, attentional bias, task context). Both contribute to the activity level at each location.
4. The peak of the priority map is used *downstream* by multiple systems: the oculomotor system (for saccade target selection), the visual system (for attentional gain modulation), and the cognitive system (for working memory selection). The priority map is therefore a *shared resource*.
5. The resolution of the attention-versus-intention debate is: *both*. They are different downstream consequences of the priority map's contents, not different functions of LIP.
6. The framework generalizes to other priority-map structures: superior colliculus, FEF, and pulvinar are all candidate priority-map substrates with overlapping but distinct contributions.

## 4. Methods

A narrative review of primate single-unit recording, microstimulation, and inactivation studies of the LIP area. The review consolidates evidence from many labs (Bisley's own group, Goldberg's, plus others) over decades of work. No new experimental data are presented; the contribution is the *priority-map* synthesis.

The principal evidence sources are:
- Free-viewing tasks where LIP activity tracks the spatial structure of behavioral relevance.
- Visual-search tasks where LIP activity scales with target probability.
- Saccade tasks where LIP activity predicts saccade targets and timing.
- Cued-attention tasks where LIP activity rises at attended locations even without saccade plans.
- Microstimulation studies showing that LIP activity is *causal* for both attention shifts and saccade plans.

## 5. Results

The principal empirical claims the review consolidates:

- **Behavioral-priority representation.** LIP neuronal activity at a location scales with the location's behavioral relevance, integrating bottom-up salience and top-down task context.
- **Spatial selectivity.** LIP cells have spatial receptive fields, and the map of activity across cells encodes a spatial priority distribution.
- **Cue-validity effects.** Validly-cued locations show enhanced LIP activity; invalidly-cued show suppression. The effect strength matches behavioral priority.
- **Saccade and attention coupling.** Microstimulation of LIP biases both saccade targets and the locus of covert attention. The effects are tightly coupled, supporting the shared-priority-map account.
- **Independent of motor output.** LIP activity is high at attended locations even when no overt eye movement is planned, ruling out a pure motor-planning role.
- **Independent of stimulus presence.** LIP activity persists at remembered locations during delay periods, ruling out a pure stimulus-encoding role.
- **The same neurons participate in both.** LIP cells that encode saccade targets and LIP cells that encode attention locus largely overlap — the same population.

## 6. Critique / limitations

The priority-map concept is *descriptive*; it does not specify the computational mechanism by which priority is computed. Bottom-up salience and top-down attention bias must somehow be integrated to produce the final activity at each LIP location, but the integration rule is not specified. Modern computational models (Itti & Koch saliency maps; reinforcement-learning models of attention) propose specific integration rules; this review does not commit.

The framework is *cortical*. It does not engage seriously with subcortical priority-map substrates (superior colliculus, pulvinar). Subsequent work (Krauzlis 2013 SC review) has emphasized SC's role in attention; the relative contributions of LIP vs SC remain a research question.

The "saccade" vs "attention" distinction is partly artificial. Many real-world tasks have both covert and overt attentional components; the priority map serves both, but the dynamics of switching between covert and overt attention are not characterized in detail.

The framework is *spatial*. Modern attention research increasingly emphasizes feature-based and object-based attention, in addition to spatial attention. Whether priority maps generalize to feature or object spaces (with priority computed in those spaces rather than in retinotopic space) is unsettled. Bisley & Goldberg implicitly commit to retinotopic priority; the user's program would need feature- and object-priority extensions to be biologically complete.

The downstream consequences of the priority map are described in terms of "the visual system uses it to guide attention" — but the specific mechanism (gain modulation, feature gating, normalization) is not detailed. The link to Reynolds & Heeger 2009 normalization or to the predictive-coding precision-weighting framework (Feldman & Friston 2010) is not made.

## 7. Connection to our work

This paper supports several architectural commitments in the user's program:

**The central self-attention substrate as a priority map.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) places a shared self-attention substrate at the center. Bisley & Goldberg's priority-map framework is the biological precedent: a shared representation of behavioral importance, fed by many sources, used by many downstream systems. The architectural commitment is the same.

**The Feedback Transformer as a priority-integration mechanism.** The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) integrates bottom-up sensory and top-down feedback Q/K projections via Hadamard product to produce the attention map. This is the computational analog of LIP integrating bottom-up salience with top-down attention bias to produce the priority map.

**Attention as a downstream consequence of the priority map.** The recurrent ViT's behavioral signatures (cued-attention effects, faster RT, higher accuracy at cued locations) are exactly the *downstream consequences* of the priority-map peak that Bisley & Goldberg describe. The framework is the biological account of why these signatures should follow from a priority-map-based architecture.

**Priority-map perturbation as the FEF microstim analog.** The recurrent ViT paper (2502.10955) reports that targeted perturbations of the attention map produce performance shifts analogous to FEF microstimulation in primates (Moore & Armstrong 2003 — `papers/moore_armstrong2003_fef_microstim.md`). FEF microstim works because FEF is a priority-map substrate; perturbing the priority map shifts attention and behavior. Bisley & Goldberg's framework is the conceptual machinery for understanding why the ViT perturbations work.

**Priority-map saturation and capacity limits.** Bisley & Goldberg note that the priority map has *finite capacity* — only so many locations can be high-priority simultaneously. The user's competition-emergent-PC thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) generalizes this: the central self-attention substrate has bounded bandwidth, and hubs compete for representation in it. Bisley & Goldberg's empirical capacity argument is the smaller-scale precedent for the user's coalition-level framing.

The recurrent ViT paper cites Bisley & Goldberg in its references (ref [74]) and the user's thesis cites it as well. The full-depth deepening makes the priority-map framework available as a citable concept in future manuscript revisions.

## 8. Citations to follow

- `krauzlis2013_sc_attention` — SC's contribution to the priority map. In seed.
- `bisley_mirpour2019_priority_map` — Bisley's follow-up review on neural priority maps. In seed.
- `mirpour2010_ppc_microstim` — microstimulation of PPC for attention. In seed.
- `moore_armstrong2003_fef_microstim` — FEF microstim. In seed, full depth.
- `silver2005_topographic_parietal` — fMRI topographic mapping of parietal attention. In seed.
- `goldberg2002_attention_parietal` — earlier review of the same area. Not in seed.
- `bisley2011_neural_priority_review` — companion review. Not in seed.
- `desimone_duncan1995_biased_competition` — biased competition. In seed, full depth.
