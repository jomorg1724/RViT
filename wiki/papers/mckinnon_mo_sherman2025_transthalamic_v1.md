---
id: mckinnon_mo_sherman2025_transthalamic_v1
title: "Disruption of Transthalamic Circuitry from the Primary Visual Cortex Impairs Visual Discrimination in Mice"
authors:
  - "McKinnon, Claire"
  - "Mo, Christina"
  - "Sherman, S. Murray"
year: 2025
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.0002-25.2025"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.0002-25.2025"
tags:
  - primate-neurophysiology
  - subcortical
  - lesion-microstimulation
  - cortical-anatomy
concepts:
  - cortico-thalamo-cortical-loops
  - transthalamic-pathway
  - optogenetic-perturbation
  - feedback-transformer
related:
  - sherman2022_ctc_loop
  - sherman_guillery2011_distinct_functions
  - weiler2025_l6_corticocortical
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-14"
---

# Disruption of Transthalamic Circuitry from the Primary Visual Cortex Impairs Visual Discrimination in Mice

## 1. Abstract

Layer 5 (L5) of the cortex provides strong driving input to higher-order thalamic nuclei (such as the pulvinar in the visual system), forming the basis of cortico-thalamo-cortical (transthalamic) circuits. These circuits provide a communication route between cortical areas in parallel to direct corticocortical connections, but their specific role in perception and behavior remains unclear. Using targeted optogenetic inhibition in mice of both sexes performing a visual discrimination task, the authors selectively suppressed the corticothalamic input from L5 cells in V1 at their terminals in the pulvinar. This suppresses transthalamic circuits from V1 specifically; any effect on direct corticocortical projections and local V1 circuitry must result from transthalamic inputs (e.g., V1 → pulvinar → V1). Such suppression of transthalamic processing during visual stimulus presentation significantly impaired discrimination performance across different orientations. The impact on behavior was specific to the portion of visual space that retinotopically coincided with the V1 L5 corticothalamic inhibition. The results highlight the importance of incorporating L5-initiated transthalamic circuits into cortical processing frameworks, particularly those addressing how the hierarchical propagation of sensory signals supports perceptual decision-making.

## 2. Why this matters for us

This is the causal-manipulation counterpart to Miller-Hansen & Sherman 2022 ([sherman2022_ctc_loop](research_db/papers/sherman2022_ctc_loop.md)). The 2022 paper established the anatomy and synaptic physiology of the V1 → pulvinar → V1 transthalamic feedback loop; this 2025 paper shows that suppressing the L5 → pulvinar driver projection *causally impairs visual discrimination*. The transthalamic pathway is not just an anatomical curiosity — it is a load-bearing computational substrate for visual perception. For the user's program, this paper is the strongest empirical evidence that *top-down modulation* via a parallel feedback route is necessary for cortical processing, supporting the architectural commitment to multi-source feedback ([feedback_transformer](research_db/concepts/feedback_transformer.md), [bidirectional_hierarchical_feedback](research_db/concepts/bidirectional_hierarchical_feedback.md)).

## 3. Key claims

1. Optogenetic suppression of the V1 L5 → pulvinar terminals — which selectively suppresses the V1 transthalamic feedback loop without affecting direct V1 → other cortex projections — significantly *impairs* visual discrimination in mice.
2. The behavioral impairment is *retinotopically specific*: only stimuli appearing in the part of visual space corresponding to the suppressed V1 L5 cells show impaired discrimination.
3. The impairment is *behaviorally relevant*: it occurs during stimulus discrimination, not just during baseline cortical activity. The transthalamic loop is doing perceptually load-bearing work.
4. The result *establishes causality* for the Sherman framework: the transthalamic loop is not merely correlated with cortical processing; suppressing it produces a measurable behavioral deficit.
5. The retinotopic specificity rules out a generalized arousal or attention effect — the impairment is *spatially precise*, consistent with the spatial structure of the V1 → pulvinar → V1 loop.
6. The result supports the conceptual framework in which cortical communication uses *parallel direct and transthalamic substrates*, with the transthalamic loop carrying behaviorally-essential modulatory information.

## 4. Methods

**Task.** Mice were trained on an orientation-discrimination task with drifting gratings presented at retinotopically-controlled locations. The task required discriminating between different orientations across the visual field.

**Optogenetic manipulation.** Selective optogenetic inhibition of V1 L5 corticothalamic *terminals* in the pulvinar (not the L5 somata in V1). This is achieved by expressing inhibitory opsin (typically Halorhodopsin or eOPN3) in V1 L5 cells via Cre-dependent viral injection in a Cre line targeting L5 corticothalamic projection neurons, then illuminating only the pulvinar with light. The cell bodies in V1 continue firing; only the L5 → pulvinar terminals are silenced.

This terminal-specific silencing is the methodologically critical point: it isolates the *transthalamic* contribution from any direct effect on L5 cells. If suppressing the loop has a behavioral effect, the effect must be transthalamic.

**Comparison conditions.** Trials with optogenetic inhibition (during stimulus presentation) compared to trials without inhibition. Behavior measured as discrimination accuracy as a function of stimulus orientation and retinotopic location.

**Retinotopic specificity test.** Optogenetic inhibition was localized to a small retinotopic region in V1; stimuli were presented either in the affected location (test) or in unaffected locations (control). Behavioral impairment was predicted only for the affected location.

## 5. Results

The principal quantitative findings:

- **Discrimination impairment.** Trials with optogenetic suppression of the V1 → pulvinar driver showed *significantly reduced* discrimination accuracy compared to control trials. The magnitude of the impairment was substantial (the authors report it as significant across multiple orientations).
- **Retinotopic specificity.** The impairment was present only for stimuli in the visual-space region retinotopically corresponding to the suppressed V1 L5 cells. Stimuli at uncued retinotopic locations were unimpaired, ruling out a generalized cortical-arousal or attention effect.
- **Stimulus specificity.** The impairment was present during stimulus discrimination, not in baseline behavior. The transthalamic loop is engaged during active perception.
- **Generalization across orientations.** The effect was robust across multiple grating orientations, not specific to one feature.

The causal evidence is therefore tight: the L5 → pulvinar → V1 transthalamic loop is *behaviorally necessary* for normal visual discrimination at the spatial scale of the manipulated cortical column.

## 6. Critique / limitations

The experiment is in mouse cortex. The pulvinar-V1 loop in mouse is structurally simpler than the primate pulvinar-V1 loop; specifically, the mouse pulvinar (LP) has a less elaborated topographic organization than primate pulvinar. Generalization to primate is plausible but not directly tested.

The orientation-discrimination task is a low-level perceptual task. Whether the transthalamic loop also supports higher-level cognitive tasks (object recognition, scene categorization) is not addressed. The role of the transthalamic loop may scale with task complexity.

The optogenetic inhibition is acute (during the stimulus presentation). It does not address *learning* effects — whether the transthalamic loop is necessary for *learning* discrimination versus for *executing* learned discrimination. Chronic suppression experiments would address this.

The behavioral impairment is measured as discrimination accuracy. The result doesn't yet identify what *aspect* of perception is impaired — whether contrast sensitivity, orientation tuning, attentional gating, or some combination. Subsequent work using more fine-grained psychophysical measures could refine the picture.

The work doesn't engage with the predictive-coding framework directly. The transthalamic loop is described in terms of "modulatory feedback" without reference to predictive-coding's specific functional interpretation (prediction-error or precision-weighting). The user's program would interpret the loop's role through that framework; the McKinnon paper itself is theoretically agnostic.

## 7. Connection to our work

This paper provides causal validation for several of the user's architectural commitments:

**The slow-FiLM mechanism in PRISM v2.** PRISM v2's slow-FiLM modulation ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.4) provides top-down modulation from $M^{\text{slow}}$ to V1 features. McKinnon et al. 2025 is the causal-manipulation evidence that this kind of modulation is *necessary* for normal perception. Specifically, the result that suppressing the V1 → pulvinar → V1 feedback loop impairs discrimination is the empirical counterpart of the architectural prediction that removing PRISM v2's slow-FiLM should degrade change-detection performance. Future PRISM v2 ablation experiments should be benchmarked against this empirical pattern.

**Retinotopic-specific feedback as a load-bearing design choice.** The paper's finding that the behavioral impairment is *spatially specific* — only the retinotopic region with suppressed transthalamic input is impaired — supports the architectural commitment to *spatially-precise* top-down feedback. The Feedback Transformer's slow-FiLM upsampling ([feedback_transformer](research_db/concepts/feedback_transformer.md)) explicitly preserves spatial structure when projecting feedback from slow memory to V1 features; this matches the biological precision the paper documents.

**The transthalamic loop as a candidate slow-memory substrate.** The user's slow memory state $M^{\text{slow}}$ ([multi_compartmental_memory](research_db/concepts/multi_compartmental_memory.md)) is *functionally* analogous to higher-order thalamus: slow-evolving, modulatory, integrating across cortical areas. Future architectural extensions could make this analogy explicit by introducing a thalamic-relay layer between memory levels, with the relay's state updated by gating dynamics rather than direct gradient flow. McKinnon et al. supplies the causal motivation for this kind of extension.

**Optogenetic perturbation as the experimental analog of attention-map ablation.** The recurrent ViT paper (2502.10955) reports that targeted perturbations of the attention map produce behavioral effects analogous to FEF microstimulation. McKinnon et al. extends this analogy to feedback pathways: perturbing a specific feedback substrate (V1 → pulvinar) produces a retinotopically-specific behavioral effect. Future experiments perturbing specific Feedback Transformer feedback sources should expect retinotopically-specific effects of the kind McKinnon et al. document biologically.

## 8. Citations to follow

- `sherman2022_ctc_loop` — the anatomical and synaptic-physiology precursor. In seed, full depth.
- `sherman_guillery2011_distinct_functions` — the foundational driver-modulator framework. In seed.
- `weiler2025_l6_corticocortical` — parallel direct-corticocortical feedback substrate. In seed, full depth.
- `roth_dahmen2016_pulvinar_modulatory` — pulvinar's modulatory role in attention. Not in seed.
- `saalmann2012_pulvinar_attention` — pulvinar's role in selective attention. Not in seed.
- `purushothaman2012_pulvinar_v1_gain` — pulvinar's role in V1 gain control. Not in seed.
- `cortes_grimaldos_2024_transthalamic_review` — recent review of transthalamic circuits. Not in seed.
