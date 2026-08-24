---
id: hanks_summerfield2017_perceptual_decisions
title: "Perceptual decision making in rodents, monkeys, and humans"
authors:
  - "Hanks, Timothy D."
  - "Summerfield, Christopher"
year: 2017
venue: "Neuron"
doi: "10.1016/j.neuron.2016.12.003"
arxiv: ""
url: "https://doi.org/10.1016/j.neuron.2016.12.003"
tags:
  - decision-making
  - review
  - primate-neurophysiology
  - psychophysics
  - reaction-time
concepts:
  - drift-diffusion-model
  - signal-detection-theory
  - chronometric-function
  - psychometric-function
related:
  - ratcliff1978_drift_diffusion
  - gold_shadlen2007_decision_making
  - roitman_shadlen2002_lip_rt
  - sridharan2017_sc_sensitivity_bias
  - luo_maunsell2018_criterion_sensitivity
  - hawkins1990_attention_detectability
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-15"
---

# Perceptual decision making in rodents, monkeys, and humans

## 1. Abstract

Hanks & Summerfield (2017) review the field of perceptual decision making — the process by which observers categorize noisy sensory evidence into discrete responses — across the three principal model species: rodents, non-human primates, and humans. The review's central thesis is that, across these species, a common algorithmic framework applies: noisy momentary evidence about the state of the world is *accumulated over time* toward a decision boundary, with the response committed when accumulated evidence first crosses the boundary. The drift-diffusion model (DDM) and its bounded-accumulator relatives provide the canonical algorithmic vocabulary; signal-detection theory (SDT) provides the static-limit specialization. The authors survey the rapidly expanding rodent literature — primarily auditory and olfactory discrimination in head-fixed and freely-moving rats and mice, increasingly with optogenetic and large-scale-recording tools — and contrast it with the older monkey-neurophysiology canon (LIP, FEF, SC, PFC accumulator neurons) and the human-psychophysics / neuroimaging canon (EEG/MEG ramping signals, fMRI evidence-accumulation correlates). The review identifies points of cross-species convergence (the parietal-frontal accumulator architecture, the influence of prior probability and reward on bias parameters, urgency and collapsing-bound effects on RT) and points of divergence (rodents weight evidence less optimally than primates in some paradigms; humans show stronger prior-dependent and context-dependent modulation; cortical-region homologies between rodent PPC/M2/FOF and primate LIP/FEF remain contested). The synthesis is that perceptual decision making is one of the *best-understood examples of cross-species algorithmic continuity in cognitive neuroscience*, with computational vocabulary inherited from Ratcliff 1978 onwards proving robust to the species shift, while neural-implementation details remain species-specific and an active area of investigation.

## 2. Why this matters for us

Hanks & Summerfield 2017 is the modern cross-species cornerstone of the database's decision-framework cluster. It is the paper that licenses the user's program — and specifically the Recurrent ViT and PRISM v1/v2 — to *be interpreted as a model of primate perceptual decision making* rather than as a generic deep-learning classifier. The review establishes that the algorithmic vocabulary inherited from Ratcliff 1978 ([ratcliff1978_drift_diffusion](ratcliff1978_drift_diffusion.md)) applies across species, that the parietal-frontal accumulator architecture is conserved (the user's central self-attention substrate is the architectural homolog of the parietal priority map), and that species-specific differences in evidence weighting and prior integration are the right axes along which to plan cross-species validation of computational models. Most importantly: the recurrent ViT's actor head, accumulating evidence across recurrent passes toward a categorical output, *is* a DDM-style accumulator in this review's sense — and the review's framing tells us how to validate it against biology.

## 3. Key claims

1. **A common algorithmic framework applies across species.** Perceptual decisions in rodents, monkeys, and humans are well-described by bounded evidence-accumulation models — primarily the DDM and its multi-alternative / leaky / urgency-gated variants.
2. **The parietal-frontal accumulator architecture is broadly conserved.** Monkey LIP and FEF, rodent posterior parietal cortex (PPC), frontal orienting field (FOF), and secondary motor cortex (M2), and human intraparietal sulcus all show ramping / accumulator-like activity correlated with the developing decision.
3. **Prior probability and reward modulate decisions through bias-like parameters.** Across species, manipulations of stimulus probability or reward asymmetry produce shifts consistent with DDM starting-point ($z$) or non-stationary drift offsets — what SDT calls criterion shifts.
4. **Speed-accuracy tradeoff and urgency are general features.** Boundary separation ($a$) or collapsing-bound dynamics account for RT and accuracy patterns in all three species; humans and monkeys can be instructed to prioritize speed or accuracy, and rodents show similar tradeoffs through training-history and timing-pressure manipulations.
5. **Causal manipulation increasingly anchors the framework in neural circuits.** Microstimulation (monkeys), optogenetic perturbation (rodents), and TMS / tACS (humans) provide convergent causal evidence that the accumulator-like activity in PPC/FOF/LIP is necessary for the decision, not merely correlated with it.
6. **Cross-species differences are real and informative.** Rodents tend to weight early evidence more heavily and integrate over shorter timescales; primates integrate more uniformly across longer evidence streams; humans show the strongest context-dependence and prior-dependent gain modulation.
7. **The framework extends beyond simple 2AFC.** Multi-alternative tasks, value-based choices, confidence judgments, and metacognitive reports can be accommodated by extensions of the DDM (race models, leaky competing accumulator, multialternative SDT, post-decision processing models).
8. **Open questions concentrate on (a) circuit-level mechanism, (b) the locus of bound-crossing, and (c) the cortical-region homology problem between rodents and primates.** The behavioral phenomenology converges; the implementation still diverges across species.

## 4. Methods

The paper is a *narrative review*, not an empirical study. The authors organize the literature along three intersecting axes:

**By species.** Rodent paradigms surveyed include the Brunton-Brody-Hanks "Poisson clicks" task, olfactory mixture discrimination (Uchida-Mainen), accumulating-towers virtual-reality navigation (Harvey-Tank), and orientation discrimination in mice. Monkey paradigms include the random-dot motion task (Newsome / Shadlen / Roitman), reaction-time motion discrimination, weather-prediction-style probabilistic categorization, and value-based choice. Human paradigms include classical psychophysics (motion, contrast, orientation), perceptual categorization, confidence and metacognition tasks, and EEG/MEG/fMRI variants of all of the above.

**By computational model.** Models surveyed: Ratcliff DDM, two-stage diffusion (Ratcliff-McKoon 2008), leaky competing accumulator (Usher-McClelland 2001), urgency-gated / collapsing-bound models (Cisek 2009; Hawkins 2015), race models for multi-alternative choice, signal-detection theory and its multialternative extensions, attractor-network neural implementations (Wong-Wang 2006), and Bayesian observer models incorporating prior knowledge.

**By neural recording / manipulation method.** Single-unit recording in monkeys (LIP, FEF, MT, SC, PFC); large-scale population recording in rodents (PPC, FOF, M2, striatum); optogenetic inactivation and stimulation in rodents; electrical microstimulation in monkeys; EEG/MEG/fMRI in humans; TMS / tDCS / tACS as causal probes in humans. The authors organize the reviewed work into a matrix of *task × species × method × computational model* and identify both convergence and remaining tensions.

The methodological contribution of the review itself is the framing: *what would a complete cross-species theory of perceptual decision making look like*, and how close are we to it?

## 5. Results

The review reports synthesized findings rather than new data; the central results to extract are:

- **DDM-style accumulator dynamics reproduce behavioral choice and RT distributions across species** in the canonical 2AFC paradigms (motion, click counting, olfactory mixture, contrast discrimination).
- **Ramping firing rates correlated with the decision variable are observed in LIP (monkey), FOF/PPC/M2 (rat), and IPS/dlPFC analogs (human).** The slope of the ramp scales with stimulus strength (drift rate); the threshold at which ramps terminate scales with caution / boundary.
- **Optogenetic inactivation of rat FOF or PPC produces choice biases and accumulator-disruption signatures**, consistent with these regions implementing or maintaining the accumulator.
- **Microstimulation of monkey LIP biases choices in the direction of the stimulated neurons' preferred response**, again consistent with LIP carrying the decision variable.
- **Human EEG centro-parietal positivity (CPP) and MEG-localized parietal signals ramp with the developing decision** and terminate at choice commitment, mirroring monkey LIP findings.
- **Rodents show steeper integration kernels early in the trial than do primates**, suggesting either shorter integration time constants or non-uniform weighting strategies.
- **Prior probability manipulations produce starting-point shifts in DDM fits across all three species**, with the magnitude of the shift varying systematically with prior strength.
- **Multi-alternative tasks fit better with race models or multialternative SDT than with the strict 2AFC DDM**, supporting the move toward multialternative frameworks (e.g., Sridharan et al. 2017 [sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md)).

The single most consequential synthesis is that the field has produced *quantitative cross-species predictions* — fit the DDM to monkey behavior, predict the LIP firing rates; fit the same model to rat behavior, predict the FOF/PPC firing rates — and these predictions broadly hold up. This is the strongest case in systems neuroscience for cross-species algorithmic continuity.

## 6. Critique / limitations

The review is necessarily synthetic, and several tensions are noted but not resolved:

The **rodent-primate cortical-region homology problem** remains open. Rat FOF and PPC are claimed as homologs of monkey FEF and LIP, but the anatomical and functional correspondences are imperfect: rats lack the geometric retinotopy and the precise areal boundaries of primate parietal cortex, and FOF inactivation produces effects that LIP inactivation often does not. The "common architecture" claim is therefore stronger at the algorithmic level than at the implementation level.

The **uniformity of evidence weighting** assumed by the canonical DDM is contradicted by data from all three species under appropriate task conditions. Rats show *primacy* (early evidence weighted more), some monkey paradigms show *recency*, and humans show task-dependent kernels. The DDM in its 1978 form has a flat integration kernel; the modern literature is moving toward leaky / time-varying accumulators.

The **bound-crossing / commitment locus** is under-determined by the data. Multiple regions show ramping activity; which one *causes* the commitment to a response (vs which one merely tracks the decision variable) is still contested. SC, FOF, FEF, and motor cortex have all been proposed as the locus of commitment in different paradigms.

**Confidence and metacognition are treated as add-ons** rather than as core components of the framework. Subsequent work (Pouget, Kepecs, Fleming, etc.) has argued that the decision and its confidence are computed jointly; the review acknowledges this but does not fully integrate it.

**The framework is overwhelmingly oriented toward 2AFC and small-N-alternative paradigms.** The multi-alternative spatial-attention tasks central to the user's program (and to Sridharan et al. 2017) are mentioned but not deeply analyzed. The cross-species story is strongest where the task is simplest.

**Naturalistic, ecologically-relevant decisions** are largely outside the review's scope. The decisions surveyed are highly constrained laboratory tasks. How well the DDM framework extends to free-viewing, scene-understanding, or change-detection-in-natural-video remains an open empirical question — directly relevant to the user's program.

## 7. Connection to our work

Hanks & Summerfield 2017 is the *cross-species credibility argument* for the user's architectural program. Where Ratcliff 1978 ([ratcliff1978_drift_diffusion](ratcliff1978_drift_diffusion.md)) gives the mathematical machinery and Roitman & Shadlen 2002 ([roitman_shadlen2002_lip_rt](roitman_shadlen2002_lip_rt.md)) gives the monkey-LIP neural substrate, Hanks-Summerfield establishes that the *same framework* applies across rodents, monkeys, and humans — which is what licenses computational models like the recurrent ViT to be interpreted as models of primate decision making in the first place.

**Cross-species perspective justifies treating the recurrent ViT as a model of primate perceptual decision making.** The recurrent ViT (2502.10955) is trained on natural images and produces classification or change-detection outputs; one cannot map it directly to a particular species' brain. But the review's claim of cross-species algorithmic continuity means that *any* convergent computational mechanism in the model — bounded accumulation, prior-dependent bias, speed-accuracy tradeoff — corresponds to a genuine cross-species cognitive primitive rather than to an idiosyncrasy of one species' neuroanatomy. This is the licensing argument for interpreting the actor head's behavior in DDM terms.

**DDM-style evidence accumulation is the algorithmic substrate for the recurrent ViT's actor head accumulating across iterations.** The recurrent ViT's actor produces logits at each recurrent pass; under a halt-when-confident readout (or a softmax-temperature equivalent), these logits accumulate toward a committal decision. This is, in the Hanks-Summerfield framework, a DDM-like bounded accumulator with the number of passes playing the role of accumulator time and the boundary $a$ realized as a learned or fixed halting threshold (`adaptive-computation-time` in the taxonomy). PRISM v1's inner variational loop (`THESIS.md` §2.8) iterates until precision-weighted prediction error converges — formally the same kind of bounded accumulation in a different guise.

**LIP/PPC accumulation neurons are the biological correlate of accumulation-to-bound.** Roitman & Shadlen 2002 ([roitman_shadlen2002_lip_rt](roitman_shadlen2002_lip_rt.md)) is the canonical monkey-LIP demonstration; Hanks-Summerfield extends this to rat PPC/FOF/M2 and human IPS. The user's program's central self-attention substrate, which integrates contributions from many memory hubs and gates responses to the actor, has been argued in [the_user_architectural_program](../threads/the_user_architectural_program.md) to be the architectural analog of the parietal priority map. If so, then the temporal dynamics of attention scores during a recurrent rollout should be readable as accumulator ramps, with slopes scaling with stimulus quality.

**Connection to Gold & Shadlen 2007 ([gold_shadlen2007_decision_making](gold_shadlen2007_decision_making.md)) and Sridharan 2017 ([sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md)).** Gold-Shadlen is the monkey-centric review that Hanks-Summerfield updates and broadens to a cross-species perspective. Sridharan 2017 supplies the multialternative SDT framework that the recurrent ViT's multi-class outputs require — Hanks-Summerfield acknowledges the need for multialternative extensions but does not develop them. Together, the three reviews (Gold-Shadlen 2007, Hanks-Summerfield 2017, Sridharan 2017) form a coherent reading list: 2AFC primate neurophysiology → cross-species 2AFC algorithmic synthesis → multialternative spatial extension. The user's program needs all three because the recurrent ViT's task structure is multialternative, the algorithmic framework is DDM-style accumulation, and the biological grounding is cross-species rather than monkey-only.

**Species-specific differences inform PRISM's planned cross-species validation.** Hanks-Summerfield identifies rodent primacy bias, monkey near-uniform integration, and human context-dependent gain modulation as the three robust cross-species behavioral signatures. PRISM's planned validation against biology should not assume uniform integration; the model's predicted integration kernel, if extracted from the recurrent dynamics, should be matched against the appropriate species-specific kernel. If PRISM's evidence kernel looks rodent-like (front-loaded), it may model rat behavior well but not monkey; the cross-species framing tells us which validation target each variant of the model should be compared against. This is especially relevant for the change-detection paradigm, which has variants run in rats, monkeys, and humans.

**Connection to causal-manipulation reasoning.** The review repeatedly emphasizes that *causal* perturbation (optogenetics, microstimulation, TMS) is what distinguishes correlative ramping signals from genuine accumulator implementation. The user's program's `virtual-lesion` capability — ablating specific memory hubs, attention sources, or feedback pathways in the recurrent ViT or PRISM and measuring the effect on choice and RT — is the in silico analog of these causal manipulations and the appropriate validation methodology. The review effectively provides a list of perturbation-experiment templates the user can mimic computationally.

**Connection to PRISM v1's response generation.** PRISM v1's binary change/no-change output (`THESIS.md`) is exactly the 2AFC decision the review surveys. The full DDM parameter set — $v$ (drift) ↔ change-signal evidence quality, $z$ (start) ↔ prior on change-vs-no-change, $a$ (bound) ↔ halt threshold or pass count, $T_{er}$ (non-decision time) ↔ encoding + motor latency — gives a complete framework for fitting PRISM v1's behavior and comparing it to rodent, monkey, and human change-detection performance from the literature.

**Critical limitation for our work.** The review's framework is overwhelmingly 2AFC. The recurrent ViT and PRISM operate on tasks with more than two response options (multi-class image classification, spatial change-detection over a grid). The proper extension is via the multialternative SDT framework of Sridharan 2017 ([sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md)) combined with multi-accumulator race models. Hanks-Summerfield is the entry point but not the destination.

## 8. Citations to follow

- `brunton_etal2013_rats_humans_optimal_evidence` — Brunton, Botvinick & Brody, the Poisson-clicks task and demonstration that rats can integrate near-optimally; foundational for the rat side of the review. Not yet in seed.
- `uchida_mainen2003_olfactory_decision` — olfactory two-alternative discrimination in rats; the rodent paradigm complementing the monkey motion task. Not yet in seed.
- `harvey_coen_tank2012_ppc_navigation` — Harvey, Coen & Tank, accumulating-towers VR task in mice with PPC imaging. Not yet in seed.
- `erlich_etal2011_fof_rat` — Erlich, Bialek & Brody, frontal orienting field as rat-FEF homolog. Not yet in seed.
- `wong_wang2006_attractor_decision` — biologically-plausible attractor-network implementation of the DDM. Not yet in seed.
- `kepecs_etal2008_confidence_neural` — neural correlates of decision confidence in rats. Not yet in seed.
- `oconnell_etal2012_supramodal_cpp` — the human centro-parietal positivity as a supramodal EEG marker of evidence accumulation. Not yet in seed.
- `kiani_shadlen2009_confidence_lip` — neural representation of confidence in monkey LIP; the joint decision-confidence framing. Not yet in seed.
- `cisek_etal2009_decisions_action` — urgency-gated decision-making and collapsing bounds in monkeys. Not yet in seed.
- `hanks_etal2015_distinct_relationships` — Hanks et al., distinct relationships between accumulator activity and choice in rat FOF vs PPC. Not yet in seed.
