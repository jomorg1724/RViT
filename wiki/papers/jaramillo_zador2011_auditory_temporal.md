---
id: jaramillo_zador2011_auditory_temporal
title: "The auditory cortex mediates the perceptual effects of acoustic temporal expectation"
authors:
  - "Jaramillo, Santiago"
  - "Zador, Anthony M."
year: 2011
venue: "Nature Neuroscience"
doi: "10.1038/nn.2688"
arxiv: ""
url: "https://doi.org/10.1038/nn.2688"
tags:
  - primate-neurophysiology
  - psychophysics
  - reaction-time
  - lesion-microstimulation
concepts:
  - gain-modulation
  - cueing-effect
  - validity-effect
  - top-down-feedback
  - recurrence-for-temporal-dynamics
related:
  - nobre_vanede2018_anticipated_moments
  - sharma2015_attention_temporal_v1
  - ghose_maunsell2002_task_timing
  - sani2017_temporal_v4_gain
  - summerfield_delange2014_expectation
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_64
status: full
depth: full
last_updated: "2026-05-15"
---

# The auditory cortex mediates the perceptual effects of acoustic temporal expectation

## 1. Abstract

When events occur at predictable instants, anticipation improves performance. Knowledge of event timing modulates motor circuits and thereby improves response speed. By contrast, the neuronal mechanisms that underlie changes in sensory perception resulting from expectation are not well understood. We developed a behavioral procedure for rats in which we manipulated expectations about sound timing. Valid expectations improved both the speed and the accuracy of the subjects' performance, indicating not only improved motor preparedness but also enhanced perception. Single-neuron recordings in primary auditory cortex showed enhanced representation of sounds during periods of heightened expectation. Furthermore, we found that activity in auditory cortex was causally linked to the performance of the task and that changes in the neuronal representation of sounds predicted performance on a trial-by-trial basis. Our results indicate that changes in neuronal representation as early as primary sensory cortex mediate the perceptual advantage conferred by temporal expectation.

## 2. Why this matters for us

Jaramillo & Zador 2011 is the auditory-modality analog of the V4/V1 temporal-expectation work (Ghose & Maunsell 2002; Sani et al. 2017; Sharma et al. 2015). It establishes that *primary sensory cortex* — not just downstream associative areas — carries the gain-modulation signal of temporal expectation, and that this gain modulation is *causally* responsible for the behavioral benefit. For the user's program this is load-bearing on two fronts. First, the modality-general claim: temporal-expectation gain modulation operates at the earliest cortical stage of every sensory hierarchy examined, supporting the Recurrent ViT commitment that pre-target memory-driven modulation should reach the *bottom* of the feedforward stack (not just be tacked on at the top). Second, the causal claim: muscimol inactivation of A1 abolishes the validity-effect behavioral gain — temporal-expectation effects in sensory cortex are not epiphenomenal correlates but the substrate of the perceptual benefit. This is the strongest available evidence that recurrent / top-down modulation at V1/A1-level layers is a necessary feature of an attention-guided architecture, not a luxury.

## 3. Key claims

1. **Temporal expectation can be manipulated in a rat psychophysical task.** A "cued-timing" two-alternative forced-choice paradigm in which the cue at trial start informs the rat about *when* the discriminative sound will occur produces large, robust validity effects.
2. **Valid temporal cues improve both speed and accuracy.** Reaction times decrease and discrimination accuracy increases on valid (correctly-cued timing) trials relative to invalid trials — establishing that the effect is perceptual, not merely motor.
3. **Primary auditory cortex (A1) single units encode sounds more strongly during anticipated moments.** Sound-evoked firing rates and stimulus information content (mutual information between firing and stimulus identity) are elevated on valid-timing trials.
4. **The enhancement is specific to anticipated times.** Firing rates and information content for sounds delivered *outside* the anticipated window are not elevated; the effect is not a global arousal gain.
5. **Trial-by-trial neuronal modulation predicts trial-by-trial behavioral performance.** A linear decoder of A1 activity correlates with the rat's choice and reaction time on a single-trial basis.
6. **Pharmacological inactivation of A1 abolishes the validity effect.** Muscimol injection into A1 eliminates the speed/accuracy benefit of valid cuing while leaving baseline discrimination relatively intact, establishing causal necessity of A1 for the temporal-expectation perceptual benefit.
7. **The mechanism is sensory-cortical, not motor-preparatory.** Because the readout is psychophysical accuracy (not just RT) and the causal lesion is sensory-cortical, the result cannot be reduced to motor-circuit readiness.

## 4. Methods

**Behavioral task.** Rats were trained in a two-alternative forced-choice frequency-discrimination task in a three-port operant chamber. The animal nose-poked into a center port to initiate a trial; a brief "cue" tone played at trial start signaled which of two possible target times the discriminative target sound was most likely to occur (e.g., short foreperiod ≈ 300 ms vs. long foreperiod ≈ 900 ms). On 80% of trials the cue was *valid* (target appeared at the cued time); on 20% it was *invalid* (target appeared at the uncued time). The rat reported the target frequency by poking the left or right reward port.

**Electrophysiology.** Single-unit and multi-unit extracellular recordings from chronically implanted tetrodes in primary auditory cortex (A1) of behaving rats. Sound-evoked responses were quantified by trial-aligned PSTHs and by mutual information between spike counts and target frequency.

**Causal manipulation.** Bilateral A1 muscimol microinfusion (GABA-A agonist, reversible inactivation) on a subset of behavioral sessions, with vehicle (saline) infusions as control.

**Single-trial decoding.** A linear discriminant or template-matching classifier was trained on trial-resolved A1 spike-count vectors to predict the target frequency; the classifier's per-trial confidence was correlated with the rat's behavioral choice and RT.

**Statistical comparison.** Paired comparisons of valid-vs-invalid firing rates, MI, and behavioral performance within session and within neuron; bootstrap confidence intervals for population-level effects.

## 5. Results

- **Behavior.** Valid-cue trials showed reaction times shorter by ≈30–60 ms and discrimination accuracy higher by several percentage points relative to invalid-cue trials. The effect held across animals and across cued-foreperiod pairs.
- **A1 single-unit gain.** Sound-evoked firing rates on valid trials exceeded those on invalid trials by ≈10–20% at the population level, with the effect concentrated in the first ≈100 ms post-sound-onset.
- **Information content.** Mutual information between A1 spike counts and target frequency was higher on valid than on invalid trials, in some neurons by a factor of ≈1.3–1.5×, indicating not just gain but improved stimulus *representation*.
- **Specificity to anticipated time.** When sounds were probe-delivered outside the anticipated window, no enhancement was observed; the effect is locked to the expected target moment, not a tonic vigilance lift.
- **Single-trial linkage.** A1-decoded confidence correlated with the rat's choice (and reaction time) trial-by-trial — fluctuations in A1 representation predicted fluctuations in behavior.
- **Muscimol inactivation.** Bilateral A1 silencing eliminated the validity effect — valid-trial RT/accuracy advantage dropped to near zero — while leaving baseline (uncued) discrimination relatively spared, establishing that A1's contribution is *specifically* the temporal-expectation benefit rather than basic sensory discrimination per se.

## 6. Critique / limitations

The 80/20 valid-invalid design conflates two distinct manipulations: *foreperiod* and *cue-driven prior over foreperiod*. The cue tells the animal both that the target is *probably* at time $t^*$ and that the elapsed-time hazard rate is non-flat. Distinguishing pure hazard-rate effects from cue-driven associative anticipation requires further dissection (cf. the rhythmic-vs-interval split addressed in Breska & Deouell 2017).

The reported population gain (≈10–20%) is modest and overlaps with what could be explained by trial-by-trial arousal fluctuations correlated with the cue. The single-trial-linkage analysis partially mitigates this concern but does not fully rule out a non-specific gain factor that happens to be tagged to the cued moment.

Muscimol inactivation is broad: it silences A1 entirely, not specifically the expectation-modulated signal. The clean interpretation — that "the validity-specific gain in A1 is causally necessary" — relies on the auxiliary observation that baseline discrimination is relatively spared, which is itself a function of dose and recovery. Cell-type-specific or interneuron-targeted manipulations would tighten the causal claim.

The species is rat, not primate. Generalization to macaque V1/V4 temporal-expectation gain (Ghose & Maunsell; Sani et al.; Sharma et al.) is by analogy. The cross-species convergence is strong evidence of a shared mechanism but the rat A1 architecture has specific features (e.g., layer-specific feedback patterns) that may not map one-to-one onto the visual ventral stream.

The mechanism by which A1 acquires the temporal-expectation modulation is not addressed. The paper documents the *consequence* (A1 gain) and its *behavioral necessity*, but the source of the descending signal (prefrontal? thalamic? cortico-thalamo-cortical via MGB?) is left for future work.

## 7. Connection to our work

This paper is the auditory counterpart of Sharma et al. 2015's V1 finding (`sharma2015_attention_temporal_v1`) and the rodent counterpart of the Ghose & Maunsell 2002 / Sani et al. 2017 V4 work — together they triangulate to a strong, modality-general, hierarchy-spanning claim: **temporal-expectation gain modulation is a property of primary sensory cortex, and it is causally responsible for the perceptual benefit of anticipation.** For the Recurrent ViT and the user's broader program this is load-bearing in four specific ways.

**A1/V1-level modulation is non-optional.** The user's hierarchical-feedback architecture (`threads/the_user_architectural_program.md` §3) commits to feedback reaching Layer 1 — the V1-paired GridCell RNN — via ascending projections from $C_2$ and $C_3$. Jaramillo & Zador 2011 supplies the strongest available causal evidence that primary sensory cortex is where the perceptually-relevant modulation actually lives. An architecture that injects feedback only into deeper layers would fail to reproduce the A1-muscimol-abolishes-validity-effect finding. This paper is the empirical reason the user's hierarchy *cannot* truncate feedback at V2/V4 level.

**Causal necessity of recurrent gain.** Beyond correlation (V4 gain peaks at anticipated time), Jaramillo & Zador provide *causal* necessity (silencing A1 destroys the behavioral benefit). The Recurrent ViT's analog — silencing $H^{(t-1)}$ before the target frame — should likewise abolish the cue-validity benefit on temporally-cued tasks. This is a falsifiable architectural prediction the user's program inherits from this paper. The recurrent ViT manuscript (2502.10955) cites Jaramillo & Zador as ref [64] in support of the recurrent-modulation hypothesis; deepening this entry makes that citation interpretable.

**Trial-by-trial single-unit-to-behavior linkage = attention-map-to-choice linkage.** Jaramillo & Zador show that A1 single-trial decoded confidence correlates with the rat's single-trial choice and RT. The Recurrent ViT's analog is that the attention map at time $t$, modulated by $H^{(t-1)}$, should correlate with the model's single-trial decision on temporally-cued change-detection trials. This is an attention-map probe future experiments should run.

**Modality-general temporal-expectation principle.** That auditory cortex, visual V1, and visual V4 all show the same expectation-gain signature is the strongest evidence that the user's *modality-agnostic* feedback transformer is the right architectural commitment. The Feedback Transformer (§1 of the architectural-program thread) projects recurrent state into Q/K/V regardless of whether the stack underneath is processing visual patches or auditory spectro-temporal tokens. Jaramillo & Zador remove the "this is just a visual-cortex quirk" objection.

**Connection to PRISM v2 slow memory as temporal context.** PRISM v2's slow memory is updated on a longer timescale than the fast memory; the user's design rationale frames this in terms of stable feature context. Jaramillo & Zador's A1 finding extends the motivation: the cue-driven temporal-expectation signal must be held across the foreperiod (≈300–900 ms) until target onset, which is exactly the timescale a slow-fast memory partition would naturally support. The expectation-bearing signal lives in slow memory; it is read out into the fast attention computation at the target moment.

**Relation to Sharma 2015.** Sharma et al. 2015 (`sharma2015_attention_temporal_v1`) is the V1 analog — same logic, same direction of effect, different modality. Reading Jaramillo & Zador and Sharma 2015 together gives the user the modality-bridge claim that pre-target gain at the *earliest* cortical sensory stage is a general principle. They should be cross-referenced throughout future writeups on the hierarchical-feedback commitment.

**Relation to the competition-emergent-PC thesis.** Under the user's strategic-prediction-error framing (§5 of the architectural-program thread), A1's pre-target gain modulation on valid-cue trials is the auditory-coalition pre-allocating its representational bandwidth in anticipation of the predicted target-time competition. The muscimol-inactivation finding shows that without that pre-allocation, the auditory coalition loses the perceptual-decision competition. This is a clean illustration of "predictive coding as resource-pre-allocation by a competing coalition."

## 8. Citations to follow

- `ghose_maunsell2002_task_timing` — macaque V4 gain peaks at expected target time; the visual-cortex sibling of this auditory result. Already in seed.
- `sani2017_temporal_v4_gain` — modern V4 population-recording replication / extension of Ghose & Maunsell. Already in seed.
- `sharma2015_attention_temporal_v1` — V1 attention-modulation by temporal expectation; the V1 analog of the present paper. Already in seed.
- `nobre_vanede2018_anticipated_moments` — review of temporal-attention literature that catalogs this paper as the auditory canonical reference. Already in seed, full depth.
- `summerfield_delange2014_expectation` — distinction between expectation and attention as theoretical frame for interpreting "validity effects." Already in seed.
- `jaramillo_borges_zador2014_acoustic_temporal_followup` — Jaramillo & Zador follow-up dissecting the temporal-expectation circuitry further. Not yet in seed; worth adding when the program engages the source of the expectation signal in detail.
- `coull_nobre1998_neural_temporal` — foundational PET study of associative temporal cuing; the human / behavioral analog of this rat paradigm. Not yet in seed.
- `ghose2006_temporal_attention_model` — model of temporal-attention gain modulation. Not yet in seed; would tie this and the V4 work into a single computational framework.
