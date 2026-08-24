---
id: gupta_sridharan2024_presaccadic_change
title: "Presaccadic attention does not facilitate the detection of changes in the visual field"
authors:
  - "Gupta, Priyanka"
  - "Sridharan, Devarajan"
year: 2024
venue: "PLoS Biology"
doi: "10.1371/journal.pbio.3002485"
arxiv: ""
url: "https://doi.org/10.1371/journal.pbio.3002485"
tags:
  - visual-attention
  - psychophysics
  - change-detection
concepts:
  - signal-detection-theory
  - bayesian-cue-integration
related:
  - sridharan2017_sc_sensitivity_bias
  - cavanaugh_wurtz2004_sc_change_blindness
  - herman_krauzlis2017_sc_change_detection
  - muller_findlay1987_sensitivity_criterion
  - bisley_mirpour2019_priority_map
  - bays2024_wm_representation
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_109
status: full
depth: full
last_updated: "2026-05-16"
---

# Presaccadic attention does not facilitate the detection of changes in the visual field

## 1. Abstract

Planning a rapid eye movement (saccade) changes how we perceive our visual world. Even *before* we move the eyes, visual discrimination sensitivity improves at the impending target of eye movements — a phenomenon termed "presaccadic attention." Yet, it is unknown whether such presaccadic selection *merely affects perceptual sensitivity* or *also affects downstream decisional processes* such as choice bias. Gupta & Sridharan report a *surprising lack of presaccadic perceptual benefits* in a common, everyday setting — detection of *changes* in the visual field. Despite the lack of sensitivity benefits, *choice bias for reporting changes increased reliably for the saccade target*. With independent follow-up experiments, they show that presaccadic change detection is rendered more challenging because percepts at the saccade target location are biased toward, and more precise for, only the *most recent* of two successive stimuli. With a Bayesian model, they show how such perceptual and choice biases are crucial to explain the effects of saccade plans on change-detection performance. In sum: visual change-detection sensitivity does *not* improve presaccadically — a result readily explained by *teasing apart distinct components of presaccadic selection*. The findings may have critical implications for real-world scenarios (like driving) that require rapid gaze shifts in dynamically changing environments.

## 2. Why this matters for us

Gupta & Sridharan 2024 is a *contemporary* paper from the Sridharan lab (which developed the multialternative SDT framework, [sridharan2017_sc_sensitivity_bias](research_db/papers/sridharan2017_sc_sensitivity_bias.md)). The result is striking: presaccadic attention — which has been *widely* believed to facilitate visual processing at the saccade target — *does not* improve change-detection sensitivity. Instead, the apparent "enhancement" is *all* due to choice bias. This is a major refinement of the presaccadic-attention literature and is directly relevant to the recurrent ViT: the user's model implements *covert* attention without saccades, so presaccadic mechanisms are absent. But the framework — that change-detection effects can be due to bias rather than sensitivity — is methodologically central.

## 3. Key claims

1. **Presaccadic attention does *not* improve change-detection sensitivity.** Subjects making saccades to a target location do not show better sensitivity for detecting changes there than for non-target locations.
2. **But it *does* increase choice bias for reporting changes at the saccade target.** Subjects are biased to *say "change" occurred at the saccade target* even without improved discrimination.
3. **The bias mechanism: stimuli at the saccade-target location are biased toward (and more precise for) the most recent stimulus.** When two stimuli appear sequentially at the target location, the percept favors the more recent one — making detection of *changes* (which require comparing the two) harder, not easier.
4. **A Bayesian model explains the pattern.** Treating perception as Bayesian integration over noisy sensory samples — with a *prior* biasing toward recent stimuli — reproduces the empirical finding.
5. **Discrimination tasks show sensitivity benefits; change-detection tasks do not.** The "presaccadic enhancement" effect found in discrimination paradigms is *task-specific*: change detection has its own dynamics that are not captured by the discrimination paradigms.
6. **Implications for driving and real-world tasks.** The result has practical implications: tasks that require detecting changes (like driving with rapidly shifting gaze) do not benefit from the kind of perceptual enhancement presaccadic attention is sometimes claimed to provide.
7. **The bias dissociation matches Sridharan 2017 for SC.** Just as SC manipulations produce bias-not-sensitivity effects ([sridharan2017_sc_sensitivity_bias](research_db/papers/sridharan2017_sc_sensitivity_bias.md)), presaccadic *attention* also produces bias-not-sensitivity effects in change-detection.

## 4. Methods

**Tasks.** Multiple experiments:
- *Change-detection task* with brief blank between stimulus 1 and stimulus 2; subjects detected if a change occurred.
- *Subject planned a saccade* to one of the stimulus locations on each trial.
- *Comparison conditions:* attended (saccade-target) vs unattended (non-saccade-target) locations.

**Behavioral measures.** SDT analysis: hit rate, false-alarm rate, d', and choice bias. Change-detection performance was measured separately at the saccade-target and non-target locations.

**Bayesian modeling.** Model: perception is a noisy posterior over the true stimulus, with a *prior* biased toward recent stimuli (the most recent percept). Different parameter regimes were fit to the empirical data.

**Independent follow-up experiments.** Additional manipulations to confirm that the recent-stimulus bias is *causal* for the change-detection difficulty.

## 5. Results

The principal quantitative findings:

- **No sensitivity benefit at saccade target.** d' for change-detection at the saccade-target location was *not* higher than at non-target locations.
- **Choice bias increase at saccade target.** Subjects' response distributions showed an increased bias to report "change" at the saccade-target location, independent of actual changes.
- **Recent-stimulus precision dominance.** Independent experiments confirm that perception at the saccade target is biased toward and more precise for the most recent of two stimuli.
- **Bayesian model fits.** The empirical data are well-fit by a Bayesian observer with a recency-biased prior. The model reproduces both the sensitivity-null and the bias-positive findings.
- **Generalization across stimulus types.** The pattern is robust across multiple stimulus types (oriented gratings, dots, etc.).

## 6. Critique / limitations

The result is specific to *change-detection* tasks. *Discrimination* tasks (where the subject reports which of two stimuli was present, not whether a change occurred) often show presaccadic *sensitivity* benefits. The two paradigms tap different aspects of attention.

The Bayesian-recency-prior framework is a specific theoretical commitment. Alternative explanations (e.g., feature-trace decay, attentional capture by the most recent stimulus) could produce the same empirical pattern.

The framework is *behavioral*. Neural-substrate questions — where the bias is implemented, why the recent-stimulus prior emerges — are not directly addressed.

The result is for *human* subjects. Whether the same pattern holds in macaque (where most physiology is done) is partially addressed by Sridharan et al. 2017 but not directly tested by this paper.

The "no sensitivity benefit" claim is *specific to change-detection*. Generalizing this to "no presaccadic attention" would be incorrect — discrimination paradigms do show benefits.

## 7. Connection to our work

This paper has direct methodological implications for the recurrent ViT and PRISM:

**The recurrent ViT's change-detection paradigm and bias-vs-sensitivity.** The recurrent ViT (2502.10955) is trained on a *change-detection* task — exactly the task Gupta & Sridharan show is *not* improved by presaccadic attention. The user's task is *covert* (no saccades), so presaccadic mechanisms aren't directly relevant. But the *bias-vs-sensitivity decomposition* is critical: any "attention effect" the recurrent ViT shows should be partitioned into bias and sensitivity components.

**Recency biases in the recurrent model.** Gupta & Sridharan's finding that perception is biased toward the *most recent* stimulus is interesting for recurrent architectures: recurrent memory naturally biases toward recent input. The recurrent ViT might exhibit similar recency biases. Empirically characterizing this would be valuable.

**Bayesian-observer modeling of the recurrent ViT's behavior.** Gupta & Sridharan use a Bayesian observer model to explain the empirical pattern. The recurrent ViT's behavioral predictions could similarly be modeled with a Bayesian observer; comparing the recurrent ViT to the Bayesian model would reveal whether the architecture approximates Bayes-optimal behavior.

**The SC-as-bias finding extends.** Sridharan et al. 2017 showed SC produces bias; Gupta & Sridharan 2024 shows presaccadic attention (which is partly mediated by SC + FEF) also produces bias. The convergent pattern is: *attentional* effects in change-detection are largely bias-mediated, not sensitivity-mediated. This is methodologically important for interpreting the recurrent ViT's attention effects.

**Multi-hub system framing.** If different attention components (sensitivity vs bias) come from different hubs, the bias-only effect of presaccadic attention in change-detection suggests that whatever hub mediates presaccadic / motor-related attention contributes *bias*, not sensitivity. This is consistent with the SC-bias finding and suggests a partition of hubs by SDT component.

The recurrent ViT paper cites Gupta & Sridharan 2024 in its bibliography (ref [109]). Future manuscripts that report change-detection results should explicitly partition behavioral effects into sensitivity and bias components.

## 8. Citations to follow

- `sridharan2017_sc_sensitivity_bias` — companion SC-bias paper. In seed, full depth.
- `cavanaugh_wurtz2004_sc_change_blindness` — SC and change blindness. In seed, full depth.
- `herman_krauzlis2017_sc_change_detection` — SC color-change detection. In seed, full depth.
- `muller_findlay1987_sensitivity_criterion` — SDT-attention foundation. In seed, full depth.
- `bisley_mirpour2019_priority_map` — priority-map framework. In seed, full depth.
- `deubel_schneider1996_presaccadic_attention` — foundational presaccadic-attention paper. Not in seed.
- `kowler1995_perceptual_consequences_saccades` — perceptual consequences of saccades. Not in seed.
- `bays2024_wm_representation` — Bayesian-observer modeling. In seed, full depth.
