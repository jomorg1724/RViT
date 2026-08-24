---
id: luo_maunsell2018_criterion_sensitivity
title: "Attentional changes in either criterion or sensitivity are associated with robust modulations in lateral prefrontal cortex"
authors:
  - "Luo, Thomas Zhihao"
  - "Maunsell, John H. R."
year: 2018
venue: "Neuron"
doi: "10.1016/j.neuron.2018.02.007"
arxiv: ""
url: "https://doi.org/10.1016/j.neuron.2018.02.007"
tags:
  - primate-neurophysiology
  - prefrontal-cortex
  - visual-attention
concepts:
  - signal-detection-theory
  - top-down-feedback
related:
  - muller_findlay1987_sensitivity_criterion
  - hawkins1990_attention_detectability
  - sridharan2017_sc_sensitivity_bias
  - mante2013_context_dependent_pfc
  - clark2015_prefrontal_attention
  - cohen_maunsell2009_correlations
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_72
status: full
depth: full
last_updated: "2026-05-16"
---

# Attentional changes in either criterion or sensitivity are associated with robust modulations in lateral prefrontal cortex

## 1. Abstract

Visual attention is associated with neuronal changes across the brain, and these widespread signals are generally assumed to underlie a *unitary* mechanism of attention. However, using signal detection theory, attention-related effects on performance can be partitioned into changes in either the subject's *criterion* or *sensitivity*. Neuronal modulations associated with *only sensitivity changes* were previously observed in *visual cortex*, raising questions about which structures mediate attention-related changes in *criterion* and whether individual neurons are involved in multiple components of attention. Luo & Maunsell recorded from monkey **lateral prefrontal cortex (LPFC)** and found that, *in contrast to visual cortex*, neurons in LPFC changed their firing rates, pairwise correlation, and Fano factor when subjects changed *either their criterion or their sensitivity*. These results indicate that attention-related neuronal modulations in *separate brain regions are not a monolithic signal* and instead can be linked to *distinct behavioral changes*.

## 2. Why this matters for us

Luo & Maunsell 2018 is the *neural-substrate* extension of the Müller-Findlay-tradition SDT analysis of attention. It localizes the *criterion* component of attention to LPFC — distinct from visual cortex, which carries the *sensitivity* component. The implication for architectural models: the user's program's distinction between *peripheral attention modulation* (the Feedback Transformer's gain on the V1 stem) and *central self-attention substrate* (the analog of LPFC) maps directly onto the Luo-Maunsell findings. The Feedback Transformer's V1-level gain implements the *sensitivity* component; the central self-attention substrate (and PFC-analog memory states) implements the *criterion* component. The architectural decomposition is biologically warranted.

## 3. Key claims

1. **Attention has two SDT components.** Standard cuing tasks produce both sensitivity and criterion changes. SDT analysis can dissect them.
2. **Visual cortex carries the sensitivity component.** Prior work (Cohen & Maunsell; Mitchell & Sundberg & Reynolds) established that V4 / IT neurons modulate with sensitivity changes but not criterion changes.
3. **LPFC carries both components.** Luo & Maunsell's recordings in macaque LPFC show that *the same neurons* modulate with both sensitivity changes and criterion changes — but in distinguishable ways.
4. **Different signatures within LPFC for the two components.** Firing rate, pairwise correlation, and Fano factor all change differently for sensitivity vs criterion conditions. LPFC encodes both, but with separable neural patterns.
5. **Attention-related neural modulations are *not* a monolithic signal.** Different brain regions carry different aspects of attention. The "attention signal" is a multi-region distributed phenomenon.
6. **LPFC is the bridge between perception and decision.** LPFC receives sensitivity information from visual cortex and produces criterion-related output that biases decisions.
7. **Implications for architectural models.** Models that treat attention as a single mechanism (e.g., one gain factor) are incomplete. The full picture requires sensitivity (perceptual) and criterion (decisional) components implemented in distinct architectural modules.

## 4. Methods

**Task (the "dissociation task", introduced in Luo & Maunsell 2015, Neuron; reused here).** Macaque monkeys performed a two-location cued orientation-change detection task. Two full-contrast Gabor samples appear on opposite sides of fixation; after a delay a single test Gabor reappears at ONE location, changed in orientation on 50% of trials (saccade to it = hit) or unchanged (withhold; a guaranteed-different second test keeps the animal engaged on correct-rejection trials). The decisive design feature: the PHYSICAL stimulus (contrast, size, orientation-change magnitude) is held IDENTICAL across conditions — this is exactly what removes the discriminability confound of the standard Posner task.

**Behavioral manipulations — BOTH via reward (the physical stimulus is never changed).**
- *Sensitivity manipulation.* Vary the AVERAGE reward per location (applied equally to hits and correct rejections, so the H:CR ratio stays fixed): a larger average reward at a location yields higher sensitivity (d') there, driven by attentional allocation.
- *Criterion manipulation.* Vary the hit-vs-correct-reject reward RATIO at a location (average held fixed) to shift the criterion (response bias) without changing d'.

These reward knobs independently change d' and β. (CORRECTION 2026-07-04: an earlier version of this card wrote "vary stimulus contrast or size" for the sensitivity manipulation — that describes the *generic* Posner attention task, NOT the Luo & Maunsell dissociation task, which controls sensitivity purely through average reward. Verified against the 2015 Methods, PMID 26050038.)

**Recordings.** Single-unit recordings in monkey LPFC during task performance. Several hundred neurons across multiple sessions.

**Analysis.**
- Firing-rate changes correlated with d' changes (sensitivity component).
- Firing-rate changes correlated with β changes (criterion component).
- Pairwise correlation analysis.
- Fano factor analysis.

The key contrast: do LPFC neurons show *different* neural signatures for sensitivity vs criterion changes?

## 5. Results

The principal quantitative findings:

- **LPFC neurons modulate with both sensitivity and criterion changes.** Most recorded neurons show firing-rate changes for both manipulations — but the *patterns* differ.
- **Sensitivity vs criterion produce distinguishable patterns.** The relative changes in firing rate, pairwise correlation, and Fano factor differ between sensitivity-driven and criterion-driven attention modulation.
- **Visual cortex shows only sensitivity changes.** Replication of prior findings: V4 and adjacent visual cortex show modulation correlated with d' but not with β.
- **LPFC is *uniquely* a multi-component substrate.** Among the recorded regions, LPFC is the only one that carries both SDT components.
- **The substrates are dissociable.** Within LPFC, the neural representation of sensitivity-related and criterion-related attention are *separable* — they're not just two labels for the same neural pattern.

## 6. Critique / limitations

The recordings are from LPFC only (within the macaque). Other PFC regions (dlPFC, vlPFC, ACC, OFC) may have different contributions; the framework characterizes LPFC specifically.

The analysis is *correlational*. LPFC activity correlates with both sensitivity and criterion changes; whether the activity *causes* the behavioral changes requires inactivation / microstimulation experiments.

The "separable patterns" claim is at the *neural-signature* level. Whether the underlying mechanism is two truly separate cell populations or one population with two operational modes is not fully resolved.

The framework doesn't engage with predictive-coding or precision-weighting interpretations. Sensitivity and criterion could be reframed as different *components of variational free-energy minimization* — sensitivity as perceptual precision, criterion as prior probability. The 2018 paper is silent on these reframings.

The change-detection task is highly trained. Whether the LPFC substrates are *intrinsic* or *learned* through task training is not addressed.

## 7. Connection to our work

This paper directly informs the user's program's architectural decomposition:

**Two architectural components for attention.** Luo & Maunsell's finding that LPFC implements both sensitivity *and* criterion supports the user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) treating different aspects of attention as different architectural components. The Feedback Transformer's perceptual gain → sensitivity; the central self-attention substrate's bias → criterion.

**PRISM v2's slow memory as the criterion-component substrate.** PRISM v2's slow memory ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) carries task-relevant context. Under the Luo-Maunsell framework, the slow memory's modulation of decision behavior would be the *criterion* component of attention — analogous to LPFC's criterion-related activity.

**Decomposing the recurrent ViT's attention effects.** The recurrent ViT's cued-attention effects should be decomposable into sensitivity and criterion components. The architectural commitments predict that the *Feedback Transformer* modulation produces sensitivity changes, while the *cue-driven shift in the recurrent state* produces criterion changes. Empirically testing this would validate the architectural decomposition.

**PFC as a multi-component controller.** Luo-Maunsell's finding that LPFC alone carries both components is consistent with Mante 2013 ([mante2013_context_dependent_pfc](research_db/papers/mante2013_context_dependent_pfc.md)) — PFC is a context-dependent dynamical system that implements multiple computational roles. The user's central self-attention substrate is the AI homolog.

**Distinct neural signatures for distinct cognitive functions.** Luo-Maunsell's finding that pairwise correlation and Fano factor distinguish sensitivity from criterion attention is methodologically suggestive: similar measures applied to the recurrent ViT's neural-population dynamics could reveal whether the model implements both components.

The recurrent ViT paper cites Luo & Maunsell 2018 in its bibliography (ref [72]). Future manuscripts that argue for the multi-component nature of attention in the user's program should cite this paper.

## 8. Citations to follow

- `muller_findlay1987_sensitivity_criterion` — foundational SDT-attention paper. In seed, full depth.
- `hawkins1990_attention_detectability` — sensitivity-changes foundation. In seed, full depth.
- `sridharan2017_sc_sensitivity_bias` — SC's role in bias vs sensitivity. In seed, full depth.
- `mante2013_context_dependent_pfc` — PFC as recurrent dynamical system. In seed, full depth.
- `clark2015_prefrontal_attention` — PFC sources of attention. In seed, full depth.
- `cohen_maunsell2009_correlations` — companion correlation-based analysis. In seed.
- `martinez_trujillo_gulli2018_dissecting_attention_lpfc` — the commentary on this paper. Not in seed.
