---
id: herman_krauzlis2017_sc_change_detection
title: "Color-change detection activity in the primate superior colliculus"
authors:
  - "Herman, James P."
  - "Krauzlis, Richard J."
year: 2017
venue: "eNeuro"
doi: "10.1523/ENEURO.0046-17.2017"
arxiv: ""
url: "https://doi.org/10.1523/ENEURO.0046-17.2017"
tags:
  - primate-neurophysiology
  - subcortical
  - change-detection
  - visual-attention
  - posner-cuing
concepts:
  - priority-map
  - top-down-feedback
  - cueing-effect
  - validity-effect
related:
  - cavanaugh_wurtz2004_sc_change_blindness
  - krauzlis2013_sc_attention
  - moore_armstrong2003_fef_microstim
  - bisley_goldberg2010_parietal_priority
  - posner1980_orienting
  - bollimunta2018_fef_sc_covert
  - herman2018_midbrain_decisions
  - herman_arcizet2020_caudate_sc
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_58
status: full
depth: full
last_updated: "2026-05-16"
---

# Color-change detection activity in the primate superior colliculus

> **Author note.** James P. Herman is the third author of the user's published paper (2502.10955, Morgan, Albanna & Herman 2025). This paper is the closest published precursor — it establishes the SC color-change-detection paradigm that the recurrent ViT and PRISM are modeled on.

## 1. Abstract

The primate superior colliculus (SC) is a midbrain structure that participates in the control of spatial attention. Previous studies have mostly used *luminance-based* visual features (motion, contrast) and *saccadic eye movements* as the behavioral response, both of which are known to modulate SC activity. To explore the limits of the SC's involvement in spatial attention, Herman & Krauzlis recorded SC neuronal activity during a task using **color** — a visual feature dimension not traditionally associated with the SC — and required monkeys to detect threshold-level changes in the saturation of a cued stimulus by *releasing a joystick during maintained fixation*. Using this color-based spatial attention task, the authors found substantial cue-related modulation in all categories of visually responsive neurons in the intermediate layers of the SC. Notably, near-threshold changes in color saturation (both increases and decreases) evoked *phasic bursts of activity* with magnitudes as large as those evoked by stimulus onset. This change-detection activity had two distinctive features: activity for hits was *larger* than for misses, and the timing of change-detection activity accounted for 67% of joystick-release latency, even though it preceded the release by at least 200 ms. The authors conclude that SC activity denotes *behavioral relevance* of the stimulus regardless of feature dimension, and that phasic event-related SC activity is suitable to guide the selection of *manual* as well as saccadic responses.

## 2. Why this matters for us

This is *the* directly load-bearing precursor paper for the recurrent ViT and PRISM. James P. Herman is the third author of the user's published paper. Herman & Krauzlis 2017 establishes the *color-change-detection-with-manual-response* paradigm that the recurrent ViT is built around, and shows that SC activity carries change-detection signals on a feature dimension (color) and via a motor pathway (joystick release) the SC was not previously known to participate in. The user's recurrent ViT replicates this paradigm: a cued stimulus, a near-threshold color change, a non-saccadic response. PRISM is trained on a closely-matched task. The empirical match between the recurrent ViT's behavioral signatures and Herman & Krauzlis 2017's primate SC physiology is the strongest argument the user's program has for biological relevance.

## 3. Key claims

1. **SC activity tracks color changes.** Visually-responsive SC neurons in intermediate layers (the same layers known for attention modulation) show phasic responses to threshold-level color saturation changes — both increases and decreases.
2. **The activity is *behaviorally relevant*.** Activity for *hit* trials (detected changes followed by correct response) is larger than for *miss* trials (undetected changes). The SC neuron's response covaries with whether the animal will report the change.
3. **The activity precedes the response by ~200 ms.** Change-detection activity in SC occurs before the manual response, so it cannot merely be a motor-preparation signal. It is a *perceptual / decision* signal in SC.
4. **The timing accounts for 67% of RT variance.** Trial-by-trial variation in the SC's change-detection latency predicts the joystick-release latency. The SC is not just *correlated* with detection — it is *temporally upstream* of the behavioral response.
5. **The activity is for manual responses, not saccades.** The animals are required to maintain fixation throughout; no saccades are made. The SC's involvement in manual change-detection is therefore independent of overt eye-movement.
6. **The activity is for color, not just luminance.** SC has historically been associated with luminance-based features. The result that color changes also drive SC activity shows that the SC's attention-related role generalizes across feature dimensions.
7. **Cue-related modulation in all visually-responsive categories.** Not just one cell type — *all* categories of visually responsive SC neurons in intermediate layers show cue-related modulation, supporting a general role for SC in attention-guided perception.

## 4. Methods

**Task.** Monkeys maintained fixation while two stimuli (saturated colored patches) appeared in the periphery. A spatial cue indicated which stimulus to attend. After a delay, one of the stimuli underwent a *threshold-level* color saturation change (increase or decrease). The monkey reported the change by *releasing a joystick* (not by making a saccade). The cued vs uncued contrast measures attention; hit vs miss contrast measures detection covariation.

**Recordings.** Single-unit extracellular recordings from intermediate-layer SC neurons during task performance. Multiple cell categories distinguished (visually responsive, build-up cells, etc.).

**Analyses.** (a) Cue-related modulation: comparison of cued-stimulus-RF vs uncued-stimulus-RF activity. (b) Change-detection activity: response to the color change, separated into hits and misses. (c) Temporal latency of change-detection activity, related to joystick-release latency.

**Behavior.** Discrimination accuracy and joystick-release latency. The animals are highly trained; performance is near-threshold (≈75% correct at the chosen color-change magnitude).

## 5. Results

The principal quantitative findings:

- **Cue-related modulation.** All visually-responsive cell categories in intermediate-layer SC show cue-related modulation. Activity for cued-stimulus-RF trials is significantly higher than for uncued-stimulus-RF trials, in the range of ~20–40% increase.
- **Change-detection activity.** Threshold-level color changes evoke *phasic* SC responses with magnitudes comparable to stimulus-onset responses.
- **Hit vs miss.** Change-detection activity is *larger* on hit trials than miss trials. The activity is causally relevant to detection.
- **Latency of change-detection activity.** Peak activity is at ≈200 ms after the color change.
- **RT variance.** Trial-by-trial variation in change-detection latency accounts for 67% of variance in joystick-release latency. This is a strong upstream relationship.
- **Hit and miss for both increases and decreases.** The same cell type responds to both color-saturation increases and decreases, supporting a *change-magnitude* readout rather than a feature-specific response.

## 6. Critique / limitations

The task uses *near-threshold* changes. Whether the SC's role in change detection scales to *supra-threshold* changes (where detection is trivial) is not addressed. Plausibly the SC's contribution is *most* visible at threshold, where the animal needs the SC's attention-modulated signal to detect the change.

The recordings are from a single-unit perspective. Population-level dynamics of the SC during change detection — which would more clearly speak to "the SC's contribution to the decision" rather than "individual cells respond" — would require larger-scale recording.

The animals are highly trained. Whether the SC's role is *learned* over training or is *intrinsic* to SC anatomy is not addressed. The activity might emerge specifically because the animals have learned to use the SC for this task.

The task focuses on *attended* trials (cued stimulus). Whether the SC also carries change-detection activity for *unattended* changes is not directly tested. The cue is present on every trial; unattended-change-detection performance would require a different paradigm.

The paper doesn't directly engage with predictive-coding or precision-weighting interpretations. The SC's change-detection activity is *consistent* with carrying a prediction error or an attentional precision signal, but the specific theoretical framing is not made.

## 7. Connection to our work

This is the *direct* precursor paper for the user's program:

**The recurrent ViT's task is a direct adaptation.** 2502.10955's paradigm — a spatial cue, a near-threshold color change at one of two locations, a manual response while maintaining fixation — is the *same* paradigm Herman & Krauzlis 2017 used in macaque. The recurrent ViT is a computational model of the SC's change-detection-with-attention task, scaled up to deep neural networks.

**The change-detection activity in the recurrent ViT.** The recurrent ViT learns to produce attention maps that peak at the cued location and that further increase magnitude at the moment of the change. This is the architectural analog of the SC's cue-related modulation plus change-detection activity. The recurrent ViT's attention map is the AI homolog of intermediate-layer SC activity.

**Hit vs miss in the model.** The Herman-Krauzlis finding that SC activity is larger on hits than misses is the empirical pattern the user's models should reproduce. PRISM and the recurrent ViT both report decision-related dynamics in their internal states; an explicit hit-vs-miss analysis of model activity (analog of Herman-Krauzlis Fig. 3) would be a useful empirical test.

**RT variance attribution.** Herman-Krauzlis attribute 67% of RT variance to SC change-detection latency. The recurrent ViT could be analyzed the same way: what fraction of its model RT variance is attributable to its attention-map dynamics? If the model gives a similar fraction, the architectural homology is empirically supported.

**Manual responses, not saccades.** The Herman-Krauzlis finding that SC contributes to manual change-detection (not just to saccade target selection) is the empirical basis for treating the recurrent ViT's *non-saccadic* response (it produces decisions, not eye movements) as a legitimate model of SC-mediated attention. The recurrent ViT is therefore a model of the *broader* attention-mediated perceptual decision-making the SC supports.

**Author overlap.** Herman is the senior author / mentor of the user's recurrent ViT paper. The architectural commitment to a recurrent change-detection paradigm is partly attributable to Herman's prior empirical work on this exact paradigm. Herman & Krauzlis 2017 is therefore a *foundational* citation for the user's program, both intellectually and through co-authorship.

## 8. Citations to follow

- `cavanaugh_wurtz2004_sc_change_blindness` — earlier SC-change-blindness work. In seed, full depth.
- `krauzlis2013_sc_attention` — SC-attention review. In seed, full depth.
- `posner1980_orienting` — the foundational Posner cuing paradigm. In seed, full depth.
- `moore_armstrong2003_fef_microstim` — FEF parallel. In seed, full depth.
- `bisley_goldberg2010_parietal_priority` — LIP priority maps. In seed, full depth.
- `herman2018_midbrain_decisions` — Herman's follow-up on midbrain decisions. In seed.
- `herman_arcizet2020_caudate_sc` — Herman's caudate-SC work. In seed.
- `bollimunta2018_fef_sc_covert` — FEF vs SC for covert attention. In seed.
