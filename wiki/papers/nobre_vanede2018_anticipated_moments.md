---
id: nobre_vanede2018_anticipated_moments
title: "Anticipated moments: temporal structure in attention"
authors:
  - "Nobre, Anna C."
  - "van Ede, Freek"
year: 2018
venue: "Nature Reviews Neuroscience"
doi: "10.1038/nrn.2017.141"
arxiv: ""
url: "https://doi.org/10.1038/nrn.2017.141"
tags:
  - visual-attention
  - review
  - human-neuroimaging
  - psychophysics
  - primate-neurophysiology
concepts:
  - top-down-feedback
  - attentional-template
  - gain-modulation
  - cueing-effect
  - recurrence-for-temporal-dynamics
related:
  - gazzaley_nobre2012_topdown
  - ghose_maunsell2002_task_timing
  - sani2017_temporal_v4_gain
  - jaramillo_zador2011_auditory_temporal
  - posner1980_orienting
  - summerfield_delange2014_expectation
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_65
status: full
depth: full
last_updated: "2026-05-14"
---

# Anticipated moments: temporal structure in attention

## 1. Abstract

The brain is increasingly recognized as a *predictive organ* that anticipates attributes of incoming sensory input to support adaptive perception and action. Selective-attention research has historically emphasized *where* and *what* to attend, treating *when* as a secondary or nuisance dimension. Nobre & van Ede review the growing body of work establishing **temporal attention** — the prioritization of behaviorally relevant *moments in time* — as a first-class component of the attention literature. They survey the diverse forms of temporal structure the brain exploits (hazard rates over a foreperiod; rhythmic regularities; learned associations between cues and target onset times; sequential dependencies), the behavioral signatures of temporal-attention deployment, the neural mechanisms by which prospective signals modulate sensory and motor processing prior to anticipated events, and the integration of temporal with spatial and feature-based attention. They argue that anticipation in time is not a peripheral curiosity but a *general principle* by which the brain allocates limited processing resources across the temporal as well as the spatial structure of the environment.

## 2. Why this matters for us

This is the canonical review of *temporal attention* — attention to "when" rather than to "where" or "what" — from the same lab that produced [gazzaley_nobre2012_topdown](research_db/papers/gazzaley_nobre2012_topdown.md). For the user's program it is the load-bearing empirical anchor for the claim that recurrent state should *temporally* modulate sensory processing. The Recurrent ViT's central architectural commitment — that a cue presented at timestep $t-k$ should shape attention to a target arriving at timestep $t$ — is the AI analog of the temporal-attention deployment Nobre & van Ede catalog. PRISM v2's slow memory, similarly, is a candidate substrate for the *temporal-context* representation that supports rhythmic and associative timing predictions. Where Gazzaley & Nobre 2012 establishes the *spatial* top-down mechanism, Nobre & van Ede 2018 establishes that the *same* top-down architecture operates over time — the empirical foundation for a unified spatiotemporal attention model in recurrent transformers.

## 3. Key claims

1. **Temporal attention is a first-class selection dimension.** The brain prioritizes moments in time using mechanisms analogous to — and partly overlapping with — those for spatial and feature-based attention.
2. **Multiple sources of temporal structure are exploited.** The review distinguishes (a) *hazard-rate / foreperiod* effects (conditional probability of target onset given elapsed time), (b) *rhythmic* expectations (periodic regularities entraining neural oscillations), (c) *associative* / *cue-based* temporal expectations (learned mappings from a cue to a target latency), and (d) *sequential* dependencies (one event predicting the timing of the next).
3. **Temporal expectations enhance behavior.** Anticipated targets are detected and identified faster and more accurately than unanticipated ones; in many paradigms, accuracy benefits accompany the classic reaction-time benefits.
4. **Pre-target neural signatures index temporal anticipation.** Anticipated moments are marked by stimulus-specific alpha-band desynchronization over sensory cortex, beta-band motor preparation, and pre-stimulus shifts in firing-rate baselines and gain in extrastriate visual cortex.
5. **Temporal attention modulates sensory gain at the anticipated moment.** Single-unit work in macaque V4 ([ghose_maunsell2002_task_timing](research_db/papers/ghose_maunsell2002_task_timing.md); [sani2017_temporal_v4_gain](research_db/papers/sani2017_temporal_v4_gain.md)) shows that neural gain peaks at the expected target time, even in the absence of a stimulus event.
6. **Temporal attention can be dissociated from arousal and motor preparation.** Although temporal expectations engage motor-preparation circuits, behavioral and neural signatures dissociate from non-specific arousal or simple readiness, supporting a genuinely *selective* temporal-attention mechanism.
7. **Temporal attention interacts with spatial and feature attention.** Temporal cues amplify the effect of valid spatial cues and feature cues; temporal expectations route prioritization to the spatial location / feature dimension that is relevant at the anticipated moment.
8. **Temporal attention is supported by a frontoparietal control network.** Left inferior parietal cortex, dorsolateral PFC, premotor cortex, and the cerebellum are repeatedly implicated as sources of temporal-attention signals; the targets are sensory cortex (gain modulation) and motor cortex (preparatory beta).
9. **Rhythmic attention entrains oscillations.** Periodic structure entrains delta- and theta-band cortical oscillations such that the high-excitability phase aligns with the anticipated event time — a mechanism distinct from interval-based hazard-rate prediction.
10. **The framework generalizes across modalities.** Auditory ([jaramillo_zador2011_auditory_temporal](research_db/papers/jaramillo_zador2011_auditory_temporal.md)) and somatosensory studies recapitulate the visual findings, suggesting temporal attention is a domain-general resource-allocation principle.

## 4. Methods

A narrative review of human psychophysics, human neuroimaging (EEG, MEG, fMRI), and primate single-unit and LFP work on temporal anticipation. The authors organize the literature around three axes:

- **Source of temporal information.** Foreperiod / hazard rate; rhythm; associative cuing; sequential structure.
- **Cognitive operation.** Anticipation of *when* a target will occur, independent of *where* or *what*; interaction of temporal with spatial / feature expectations.
- **Neural level.** Behavioral effects, EEG/MEG markers (CNV, alpha desynchronization, beta motor preparation, oscillatory entrainment), fMRI of frontoparietal control networks, single-unit gain modulation in extrastriate cortex.

The synthesis frames temporal attention as a *prospective* selection mechanism that uses learned or inferred temporal regularities to bias processing toward anticipated moments. The authors take a deliberate stance against the historical treatment of timing as a *control variable* (something to be randomized away in psychophysical designs) and reframe it as a *content variable* — a dimension along which attentional priority can be allocated. The framing is the temporal analog of Posner's 1980 reframing of spatial attention as a deployable selection resource.

## 5. Results

The principal empirical claims the review consolidates:

- **Foreperiod / hazard-rate effects.** When the time elapsed since a warning cue increases without the target appearing, the conditional probability of imminent target onset rises. Reaction times decrease monotonically with foreperiod under aged hazard distributions, and rise sharply when the hazard distribution is non-monotonic — a behavioral signature of subjects' explicit tracking of conditional target probability.
- **Contingent negative variation (CNV).** A slow scalp-negative EEG potential between warning cue and target, indexing temporal-anticipation buildup; its amplitude scales with the precision of the temporal expectation.
- **Pre-target alpha desynchronization.** Over visual cortex contralateral to anticipated visual targets, alpha (8–12 Hz) power decreases in the seconds preceding target onset, with the timing of the desynchronization tracking the expected target time.
- **Beta-band motor preparation.** Contralateral sensorimotor beta (~20 Hz) decreases prior to anticipated response moments; the timing aligns with the expected target rather than with the warning cue.
- **Macaque V4 gain modulation.** Ghose & Maunsell 2002 and Sani et al. 2017 show that V4 neurons increase firing-rate gain at the *expected* target time, with the gain profile peaking at the most-likely-target moment and falling off at less-likely times — even when no target is presented.
- **Rhythmic-attention entrainment.** Periodic visual or auditory streams entrain delta/theta cortical phase such that the high-excitability phase coincides with expected target moments; perceptual sensitivity and reaction times are modulated by the phase of the entrained oscillation at target onset (Large & Jones 1999; Lakatos et al. 2008).
- **Cue-based associative temporal attention.** Symbolic cues that predict target latency produce reaction-time and accuracy benefits comparable in magnitude to spatial cueing effects ([coull_nobre1998_neural_temporal](research_db/papers/coull_nobre1998_neural_temporal.md), the foundational paradigm); these effects engage left inferior parietal cortex and dorsolateral PFC.
- **Interaction with spatial attention.** When temporal and spatial cues are combined, the benefits are super-additive in some conditions and additive in others, suggesting overlapping but partially dissociable control mechanisms.
- **Cross-modal generalization.** Auditory temporal-attention effects (Jaramillo & Zador 2011, ferret A1 gain modulation; Lange et al., Kotz & Schwartze in humans) parallel the visual results.

## 6. Critique / limitations

The review is correlational and methodologically heterogeneous: many of the synthesized effects come from different tasks, modalities, and species, and the integration into a single "temporal attention" construct is partly interpretive. Whether the operations called *foreperiod hazard*, *rhythmic entrainment*, and *associative temporal cuing* recruit a single shared mechanism or merely co-occur under the label "temporal anticipation" is not fully settled. Subsequent work (e.g., Breska & Deouell 2017; Herbst & Obleser 2019) has begun to dissociate rhythmic from interval-based mechanisms, suggesting the review's umbrella may need to be split.

The relation between *temporal attention* and *temporal expectation* is partly definitional. The authors largely conflate the two; later treatments (e.g., Nobre & van Ede 2023) more carefully distinguish *attention* (resource allocation) from *expectation* (probabilistic belief). The mechanistic claim that temporal attention modulates gain "in the same way" as spatial attention does is most strongly supported in V4 single-unit work and weaker for human neuroimaging, where the spatial resolution is insufficient to make the claim cleanly.

The review predates much of the predictive-coding literature's engagement with timing. Connections to active-inference accounts of temporal precision (Friston-style precision-weighting on prediction-error channels over time) are noted only briefly. Subsequent work has filled this gap.

The frontoparietal-control claims rest mostly on fMRI activation overlap; whether the *same* neural population in left inferior parietal cortex serves spatial and temporal cuing requires causal manipulation (TMS, lesion) that the review summarizes but does not fully resolve.

## 7. Connection to our work

This paper supplies the empirical neural-mechanism support for **temporal anticipation as a recurrent-ViT design constraint**, and it complements Gazzaley & Nobre 2012 ([gazzaley_nobre2012_topdown](research_db/papers/gazzaley_nobre2012_topdown.md)) by extending the top-down-modulation framework from space to time.

**Recurrent ViT's temporal cue-target structure.** The Recurrent ViT (2502.10955) is trained on tasks where a cue at timestep $t-k$ informs decisions about a target at timestep $t$. The architectural mechanism is that the recurrent memory state $H^{(t-1)}$ is integrated into the self-attention computation at time $t$ (§6.7, multiplicative-feedback variant). Nobre & van Ede 2018 is the canonical empirical signature this architecture aims to reproduce: a pre-target pre-cued state — held across the foreperiod — that modulates sensory gain at the anticipated moment. The empirical claim that V4 gain peaks at the expected target time (Ghose & Maunsell 2002; Sani et al. 2017) is the cellular-level counterpart of the recurrent ViT's pre-target attention-map modulation. The user's `feedback-transformer` primitive is the architectural vehicle by which a temporally-distant cue modulates attention to a present target.

**PRISM's slow memory as temporal context.** PRISM v2's slow memory (`PrismV2/docs/PRISM_V2_PROPOSAL.md` §3.3) is updated at a slower timescale than the fast memory. The architectural rationale has so far been framed in terms of *stable feature context*; Nobre & van Ede 2018 supplies a complementary motivation — slow memory is also a candidate substrate for *temporal context* in the sense Nobre & van Ede describe: foreperiod-elapsed tracking, hazard-rate computation, rhythmic-phase representation. The slow-memory commitment is biologically warranted not only as spatial-context but as temporal-context.

**Hierarchical-feedback timescales = nested temporal expectations.** The user's program (§3 of `threads/the_user_architectural_program.md`) commits to a hierarchy of memory layers operating at different update timescales — fast at shallow / V1-paired layers, slow at deep / IT-paired layers. Nobre & van Ede 2018 catalog at least two distinct temporal-anticipation regimes (sub-second rhythmic entrainment vs. multi-second hazard-rate tracking) that map naturally onto a two-timescale memory architecture. The architectural commitment is biologically warranted as a temporal-multiplexing substrate.

**Spatial-and-temporal attention unified through the feedback transformer.** The user's `feedback-transformer` primitive integrates feedback at the Q/K/V level of self-attention. Because the feedback source $C_i$ can encode either spatial structure (which patches matter), temporal structure (which timesteps matter), or both jointly (which patches matter at which times), the same architectural mechanism that Gazzaley & Nobre 2012 motivate for *spatial* top-down modulation extends — under Nobre & van Ede 2018 — to *temporal* top-down modulation. The unified architecture is biologically warranted at both axes of selection.

**Pre-target gain modulation = pre-target attention-map modulation.** The recurrent ViT's attention maps in the pre-target frames (visible in the supplementary attention-map figures of 2502.10955) should, on this account, focus on the cued location *before* the target appears. The V4-gain finding of Ghose & Maunsell 2002 and Sani et al. 2017 is the empirical anchor for this prediction. Future probes of the recurrent ViT's behavior on temporally-cued tasks should test for exactly this pre-target pre-localized gain.

**Hazard-rate computation as recurrent-state evolution.** The Nobre & van Ede review highlights that subjects' reaction-time profiles track the *conditional* probability of target onset given elapsed time — i.e., they integrate a hazard-rate function over the foreperiod. The recurrent ViT's $H^{(t)}$ evolves with each timestep over the cue-target interval; the architectural prediction is that $H^{(t)}$ should encode (implicitly or explicitly) this elapsed-time-conditional belief, even though the training signal does not name it. This is a falsifiable prediction: probing $H^{(t)}$ across the foreperiod should reveal monotonic or aged-hazard-shaped representations.

**Competition framing.** Under the user's competition-emergent-PC thesis (§5 of the architectural-program thread), pre-target gain modulation is an *opponent-modeling* signal — the cued coalition is mobilizing resources to win the attention competition at the anticipated moment. Nobre & van Ede's findings on pre-target alpha desynchronization and V4 gain are then the empirical signature of cued coalitions pre-allocating against the predicted strategic moment.

The recurrent ViT paper cites Nobre & van Ede 2018 in its bibliography (ref [65]). Future manuscripts on PRISM v2 or the multi-hub system should cite this paper jointly with Gazzaley & Nobre 2012 as the empirical neural-mechanism support for unified spatiotemporal top-down modulation.

## 8. Citations to follow

- `coull_nobre1998_neural_temporal` — foundational PET study of associative temporal cuing; the original "Posner cuing in time" paradigm. Not yet in seed; should be added.
- `ghose_maunsell2002_task_timing` — macaque V4 single-unit gain peaks at expected target time. In seed, full depth.
- `sani2017_temporal_v4_gain` — modern replication and extension of Ghose & Maunsell with population recordings. In seed.
- `jaramillo_zador2011_auditory_temporal` — auditory cortex gain modulation by temporal expectation in ferret A1. In seed.
- `posner1980_orienting` — the spatial-attention companion paradigm Nobre & van Ede generalize to time. In seed.
- `summerfield_delange2014_expectation` — distinction between attention and expectation; closely related conceptual scaffolding. In seed.
- `lakatos2008_oscillatory_entrainment` — rhythmic-entrainment mechanism in primate A1 / V1. Not yet in seed; load-bearing for the rhythmic-attention claim.
- `large_jones1999_dynamic_attending` — psychological theory of dynamic attending and oscillatory attention. Not yet in seed.
- `breska_deouell2017_dissociating_rhythmic_interval` — dissociation of rhythmic from interval-based temporal attention. Not yet in seed; addresses §6 critique.
- `gazzaley_nobre2012_topdown` — companion spatial top-down review. In seed, full depth.
- `nobre_vanede2023_attention_expectation` — Nobre & van Ede follow-up sharpening the attention-vs-expectation distinction §6 critiques. Worth adding when the program engages predictive-coding-vs-attention dissociations directly.
- `kotz_schwartze2010_cortical_subcortical_timing` — cortico-subcortical timing networks (cerebellum, basal ganglia) for temporal expectation; complements the frontoparietal-control claim. Not yet in seed.
