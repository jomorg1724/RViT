---
id: gold_shadlen2007_decision_making
title: "The neural basis of decision making"
authors:
  - "Gold, Joshua I."
  - "Shadlen, Michael N."
year: 2007
venue: "Annual Review of Neuroscience"
doi: "10.1146/annurev.neuro.29.051605.113038"
arxiv: ""
url: "https://doi.org/10.1146/annurev.neuro.29.051605.113038"
tags:
  - primate-neurophysiology
  - decision-making
  - review
concepts:
  - drift-diffusion-model
  - chronometric-function
  - psychometric-function
  - signal-detection-theory
related:
  - mante2013_context_dependent_pfc
  - bisley_goldberg2010_parietal_priority
  - summerfield_delange2014_expectation
  - roitman_shadlen2002_lip_rt
  - ratcliff1978_drift_diffusion
  - hanks_summerfield2017_perceptual_decisions
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# The neural basis of decision making

## 1. Abstract

The study of decision making spans varied fields — neuroscience, psychology, economics, statistics, political science, and computer science. Despite this diversity of applications, most decisions share *common elements*: deliberation and commitment. Gold & Shadlen evaluate progress in understanding how these basic elements of decision formation are implemented in the brain. They focus on simple decisions that can be studied in the laboratory but emphasize *general principles* likely to extend to other settings.

## 2. Why this matters for us

Gold & Shadlen 2007 is the canonical review of *perceptual decision-making* in the framework that PRISM v1's actor head and the recurrent ViT's response generation are built on. The paper formalizes decision-making as *evidence accumulation* with a *threshold for commitment*, embodied in the drift-diffusion model (DDM) family. For the user's program, this paper is the load-bearing reference for treating the recurrent ViT's response — and PRISM's policy — as the result of a *bounded evidence-accumulation process* over the recurrent state. The paper also establishes the methodological framework for *psychometric* and *chronometric* analysis of behavior — the same framework the recurrent ViT paper (2502.10955) uses to characterize cue-validity effects.

## 3. Key claims

1. **Decisions have deliberation and commitment.** Two universal elements: a deliberation phase (evidence accumulation) and a commitment moment (threshold crossing, response initiation).
2. **Evidence accumulates linearly over time.** During deliberation, the decision variable integrates evidence approximately linearly. The drift rate reflects evidence strength; the integration produces a decision variable that grows toward a threshold.
3. **Commitment is threshold-crossing.** When the decision variable crosses an absorbing threshold, the response is initiated. The threshold determines speed-accuracy trade-off: lower threshold → faster, less accurate; higher threshold → slower, more accurate.
4. **Neural correlates: LIP and FEF accumulator neurons.** In primate, LIP and FEF cells show *ramp-like* activity during deliberation that scales with stimulus strength and predicts the response. The activity reaches a fixed threshold at the moment of commitment.
5. **The DDM framework unifies many empirical phenomena.** RT distributions, accuracy as a function of stimulus strength, speed-accuracy trade-offs, sequential effects — all are captured by DDM with appropriate parameters.
6. **The framework extends beyond perceptual decisions.** Value-based decisions (economic), memory-guided decisions, and motor decisions can all be cast in DDM terms. The framework is *unified across decision types*.
7. **Decision variables are read out from accumulator neurons by *threshold-crossing* downstream cells.** Saccade-related neurons in SC and FEF act as threshold detectors that fire when the accumulator reaches a critical level.

## 4. Methods

A narrative review covering primate single-unit recording, psychophysics, computational modeling, and theoretical analysis of perceptual decision-making. The Shadlen lab's work is central, with extensive coverage of other groups' contributions.

Key elements:
- **Random-dot motion task** as the experimental paradigm: variable-coherence motion stimuli, RT or fixed-duration responses.
- **DDM as the unifying computational framework:** evidence accumulation, drift rate, threshold, non-decision time.
- **LIP and FEF recordings:** ramp activity, threshold-crossing, decision-variable encoding.
- **Theoretical analysis:** how DDM parameters map onto neural circuit-level dynamics.

## 5. Results

The principal empirical claims the review consolidates:

- **LIP ramp activity.** During motion-direction discrimination, LIP cells show *ramping* activity with slopes proportional to motion coherence and an apparent absorbing threshold near the moment of saccade initiation.
- **Threshold-crossing.** The activity at the moment of saccade initiation is approximately constant across coherences — the cell's "threshold" doesn't depend on stimulus strength.
- **Speed-accuracy trade-off.** Adjusting the implicit threshold (e.g., by time pressure or reward asymmetry) produces the predicted DDM speed-accuracy curves.
- **Bias and starting-point effects.** Reward asymmetries and prior expectations shift the starting point of the decision variable, biasing choices.
- **Many cortical areas show accumulation signatures.** Beyond LIP, FEF and dlPFC show similar ramp-like activity in decision tasks.
- **Subcortical decision contributions.** SC and basal ganglia contribute to the threshold-crossing / response-initiation aspect of the decision.

## 6. Critique / limitations

The DDM is a *simple model*. Real decisions involve more complex dynamics: non-linear evidence accumulation, multiple stages, attention-modulated drift rates, etc. The DDM captures the broad picture but glosses over details that may matter empirically.

The review focuses on *simple perceptual decisions*. Decisions with multiple alternatives, with deferral options, or with deliberation over long timescales require extensions to the framework.

The neural-correlate claims are about *individual cells*. Population-level decoding (which the Shadlen lab and others have since pursued) gives a richer picture, sometimes showing patterns the single-cell view misses. The 2007 framing predates the most sophisticated population analyses.

The framework treats decisions as *bottom-up* — driven by evidence accumulation toward a fixed threshold. Top-down modulations (attention, prior expectations) are included but as *parameters* of the model rather than as integral parts of the deliberation. More recent work (Summerfield & de Lange 2014) emphasizes top-down influences more heavily.

The framework doesn't engage with the *predictive-coding* tradition. The drift-rate parameter could be reframed in PC terms (as prediction-error-weighted drift), but the 2007 review doesn't make the connection.

## 7. Connection to our work

This paper is the canonical theoretical framework for decision dynamics in the user's program:

**The recurrent ViT's response as accumulator-threshold-crossing.** The recurrent ViT's response is produced when its attention map peaks at a specific location for sufficient time — operationally analogous to accumulator-threshold-crossing in DDM. The recurrent ViT's RT distributions and accuracy patterns should follow DDM predictions; verifying this empirically would validate the architectural homology.

**PRISM v1's actor as a threshold-crossing reader.** PRISM v1's actor head reads the recurrent state and produces a discrete action when a threshold is reached. This is the architectural form of the DDM commitment phase. The Gold-Shadlen framework supplies the cognitive-neuroscience vocabulary for what PRISM v1's actor is doing.

**Speed-accuracy trade-off as architectural parameter.** The DDM speed-accuracy trade-off (modulated by threshold) is a quantitative empirical pattern. PRISM and the recurrent ViT have implicit thresholds (e.g., the temperature of the softmax, the policy entropy regularization). Tuning these should produce DDM-like speed-accuracy curves; this is a testable empirical prediction.

**Validity-related drift-rate effects.** The recurrent ViT's faster RT at validly-cued locations is exactly the DDM prediction of "valid cue increases drift rate." The Gold-Shadlen framework supplies the theoretical interpretation of the recurrent ViT's chronometric signature.

**Multi-hub decisions.** In the user's multi-hub system, decisions are formed by integrating contributions from multiple hubs. The DDM framework generalizes to multi-channel integration; each hub's contribution can be thought of as a separate drift component, with the total decision variable being a weighted sum. This is a natural extension of the Gold-Shadlen framework.

**Bias and prior effects.** DDM's "starting-point bias" framing is the architectural analog of the user's program's commitment to *prior knowledge* (from slow memory / context hubs) biasing decisions. Both PRISM v2 and the multi-hub system would predict bias-related shifts in their decision behavior; the DDM framework supplies the methodology for measuring them.

PRISM v1's THESIS document cites Gold & Shadlen 2007. The recurrent ViT paper doesn't cite it explicitly, but the chronometric analysis (cue-validity effects on RT) is methodologically aligned with the framework.

## 8. Citations to follow

- `mante2013_context_dependent_pfc` — context-dependent decision dynamics. In seed, full depth.
- `bisley_goldberg2010_parietal_priority` — LIP priority and decisions. In seed, full depth.
- `summerfield_delange2014_expectation` — expectation in decisions. In seed, full depth.
- `roitman_shadlen2002_lip_rt` — Roitman & Shadlen LIP RT paper. In seed.
- `ratcliff1978_drift_diffusion` — original DDM. In seed.
- `hanks_summerfield2017_perceptual_decisions` — review of decision-making. In seed.
- `hanks_kiani_shadlen2014_relationship_decision_neural` — Hanks-Kiani-Shadlen relationship paper. Not in seed.
- `ratcliff_mckoon2008_dpd_decision_review` — Ratcliff DPD review. Not in seed.
