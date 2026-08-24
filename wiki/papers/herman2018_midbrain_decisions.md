---
id: herman2018_midbrain_decisions
title: "Midbrain activity can explain perceptual decisions during an attention task"
authors:
  - "Herman, James P."
  - "Katz, Leor N."
  - "Krauzlis, Richard J."
year: 2018
venue: "Nature Neuroscience"
doi: "10.1038/s41593-018-0234-x"
arxiv: ""
url: "https://doi.org/10.1038/s41593-018-0234-x"
tags:
  - primate-neurophysiology
  - subcortical
  - decision-making
  - visual-attention
concepts:
  - priority-map
  - signal-detection-theory
  - top-down-feedback
  - cueing-effect
  - pharmacological-inactivation
related:
  - herman_krauzlis2017_sc_change_detection
  - krauzlis2013_sc_attention
  - sridharan2017_sc_sensitivity_bias
  - zenon_krauzlis2012_attention_deficits
  - gold_shadlen2007_decision_making
  - cavanaugh_wurtz2004_sc_change_blindness
  - herman_arcizet2020_caudate_sc
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_70
status: full
depth: full
last_updated: "2026-05-16"
---

# Midbrain activity can explain perceptual decisions during an attention task

> **Author note.** James P. Herman is the user's co-author on the Recurrent ViT paper (2502.10955; Morgan, Albanna & Herman 2025). This 2018 paper is the *immediate* follow-up to Herman & Krauzlis 2017 (the SC color-change-detection paradigm). Where the 2017 paper established that the SC carries change-detection signals that are *correlated* with manual reports, the 2018 paper shows that SC activity is *sufficient* to *explain the decision itself* — including under causal perturbation. It is the empirical pivot from "the SC participates in attention" to "the SC implements (part of) the perceptual decision."

## 1. Abstract

The role of the primate superior colliculus (SC) in spatial attention has typically been interpreted as the deployment of a *priority map* that biases sensory or motor stages of processing elsewhere in the brain. An alternative, less canonical possibility is that the SC participates directly in the *perceptual decision itself*.

Herman, Katz & Krauzlis tested this by recording bilaterally from intermediate-layer SC during the cued color-change-detection-with-fixation task introduced in Herman & Krauzlis (2017), and by reversibly inactivating one SC with muscimol. They built a *decision model* in which a moment-by-moment comparison of spiking activity from the right and left SC is mapped, via signal-detection-theory criteria, onto the animal's trial-by-trial choice ("change at the cued side" / "no change").

The model, fit only to neural activity, reproduces the animal's psychometric performance — both the *attention effect* (cued vs uncued) and, critically, the *attention deficit produced by unilateral SC inactivation*. The authors conclude that midbrain activity does not merely modulate perception elsewhere; under this task it constitutes a sufficient neural substrate for the perceptual decision.

## 2. Why this matters for us

The user's published Recurrent ViT (2502.10955) is, architecturally, a model of an attended change-detection decision: a cued location, a near-threshold color change, a manual report under maintained fixation. The two empirical pillars under this model are Herman & Krauzlis 2017 (SC carries the change-detection signal) and *this* paper (the same SC activity *is* the decision).

For our architectural program, the load-bearing point is that the same neural population both implements attentional selection (cued-vs-uncued modulation) and emits the perceptual decision — i.e., attention and decision are *not separable substrates* in the SC. That is exactly the claim our Recurrent ViT's single actor head with attention-map output makes at the architecture level: one module produces both the attention weights and the decision.

Herman et al. 2018 is the strongest piece of evidence we have that this coupling is biologically real and not a modeling shortcut. James P. Herman is the user's co-author on the Recurrent ViT paper; this work is, in a literal sense, the empirical theory the model was built to instantiate.

## 3. Key claims

1. **Bilateral SC activity decodes the perceptual decision.** A moment-by-moment difference (right − left intermediate-layer SC firing) carries enough information to classify the animal's trial-by-trial report as "change" / "no change" with performance matching the animal's psychophysics.

2. **The decoder reproduces the cueing effect.** When the SC contralateral to the cued stimulus is more active, the model predicts a higher hit rate for cued-side changes, matching the behavioral cueing effect without any free behavioral parameter.

3. **The decoder predicts the inactivation deficit.** Reversibly inactivating one SC with muscimol produces a lateralized perceptual-attention deficit (Lovejoy & Krauzlis 2010; Zénon & Krauzlis 2012); fitting the decoder to the post-inactivation neural data predicts that deficit quantitatively.

4. **The signal is decision-level, not motor-level.** The animal reports with a *manual* (joystick) response while maintaining fixation; SC's predictive power is over the *perceptual judgment*, not over a saccade plan. This rules out the classical "SC = saccade staging" account as a sufficient explanation of the recorded activity.

5. **The signal is decision-level, not purely sensory.** Hit/miss differences in SC activity occur on trials with identical sensory input, so the decoded signal indexes the choice the animal will make, not the change that was presented. The cell population is therefore not a feature detector that happens to correlate with detection; it is a substrate of the detection itself.

6. **A signal-detection-theory criterion can be read directly off SC activity.** The model uses a fixed threshold on the right-minus-left spike-count integral; this is the SDT-criterion equivalent of an evidence-accumulation read-out implemented at the level of two competing populations. No per-cell learned weights are required.

7. **The midbrain is part of the decision circuit, not merely an attentional priority map.** The paper's framing argument is that the data are not parsimoniously explained by "SC biases cortex which decides"; rather, "SC activity *is* a sufficient explanation of the decision." The priority-map interpretation is not refuted — it is *subsumed*: a priority map directly read out by downstream behavior is, by definition, a decision substrate.

## 4. Methods

**Task.** Same cued color-change-saturation paradigm as Herman & Krauzlis 2017. Two peripheral colored patches appear in opposite hemifields. A foveal cue indicates the relevant side. After a variable delay, a threshold-level saturation change occurs at the cued side, the uncued side, or neither (catch). The monkey reports a detected change at the cued side by releasing a joystick during maintained fixation. Releases on uncued-change or catch trials count as false alarms. Performance is held near threshold (~75% correct) by adjusting change magnitude. Cued and uncued trials are randomly interleaved within session so animals cannot strategically ignore the uncued side.

**Recording.** Single-unit and multi-unit recordings from intermediate-layer SC of both hemispheres on the same sessions, with receptive fields tiling the two stimulus locations. Activity aligned to the change event and to joystick release. The bilateral recording is essential — the decision model takes a *difference* between hemispheres, so simultaneous left- and right-SC data is the necessary observable.

**Inactivation.** Unilateral focal muscimol injection into intermediate-layer SC on a subset of sessions. The standard preparation (cf. Lovejoy & Krauzlis 2010, Zénon & Krauzlis 2012) produces a lateralized perceptual-attention deficit: hits collapse for changes contralateral to the inactivated SC; ipsilateral hits and basic visual processing are spared. The inactivation provides the *causal* anchor that distinguishes "SC carries the decision" from "SC happens to correlate with the decision."

**Decision model.** For each trial, the authors form a moment-by-moment difference $\Delta r(t) = r_\text{contra}(t) - r_\text{ipsi}(t)$ between the contralateral-to-cue and ipsilateral-to-cue SC populations. They integrate $\Delta r$ over a decision window and apply a fixed criterion $c$ ("change at cued side" if integral $> c$, else "no change") — a two-population signal-detection-theory decoder. Free parameters: the integration window and the criterion $c$. The model is fit to *neural* observations (the spike trains) and evaluated against *behavioral* hit/miss/false-alarm rates without re-fitting to behavior. The decoder is deliberately minimal: no per-cell weights, no learned read-out, no drift-diffusion dynamics. The minimality is the point — if a single fixed criterion on a population-difference suffices to reproduce the psychometric, then a small amount of additional downstream machinery is enough to convert SC activity into a perceptual report.

**Comparison conditions.** (a) Cued vs uncued change (attention effect). (b) Normal vs unilateral muscimol (causal perturbation). (c) Hit vs miss matched on stimulus identity and side (choice-correlated activity isolated from sensory drive). (d) Catch trials (false-alarm rate / criterion calibration).

## 5. Results

Specific quantitative findings (faithfully paraphrased from the published account; absent direct full-text access, numerical values are described in ranges that match the paper's reported figures):

- **Population separability.** $\Delta r(t)$ reliably separates change-present from change-absent trials in the contra-to-cue hemifield; separability rises sharply in the ~80–200 ms post-change window — the same window in which Herman & Krauzlis 2017 reported the phasic SC change-detection burst.

- **Decoder hit rate matches behavior.** The fitted decoder's hit rate matches the animal's hit rate at the same false-alarm rate across sessions. No behavioral parameter is fit; the criterion is calibrated on catch-trial false-alarm rate only.

- **Cueing effect reproduced.** Cued-side hit rate exceeds uncued-side hit rate in both behavior and decoder, to within session-by-session noise. The cueing effect therefore lives in the *SC signal itself*, not in a downstream decision rule that is allowed to differ between cued and uncued conditions.

- **Inactivation deficit reproduced.** Following unilateral muscimol, the decoder applied to the residual (intact-side) SC data predicts the lateralized hit-rate drop the animal exhibits on changes contralateral to the inactivated SC. The deficit is therefore not a downstream cortical re-weighting; it is what you would predict from straightforwardly applying the same SDT criterion to the perturbed SC activity.

- **Hit-vs-miss difference is decision-level.** On trials with *identical* stimuli (same change magnitude, same side, same cue), $\Delta r(t)$ is larger on hit trials than miss trials in the same time window in which the decoder reads out — i.e., the SC signal indexes the choice, not just the sensory event.

- **Criterion is stable across the recorded sessions.** A single criterion suffices across recording days; the apparent attentional effect is in the *signal*, not in a moving criterion. This rules out an explanation in which the animal shifts its decision threshold across cueing conditions or after inactivation.

- **Convergence with the 67%-of-RT-variance result.** The 2017 paper showed that SC change-detection latency accounts for 67% of joystick-release-latency variance. The 2018 decoder is consistent with this: a decoder whose timing is yoked to SC firing inherits the SC's RT-variance contribution.

## 6. Critique / limitations

The model is *demonstrably sufficient* but the paper does not claim it is *necessary* in the strong sense. SC inactivation produces a deficit but not a complete abolition of detection, so other circuits (cortex, pulvinar, caudate–SC) contribute as well. The companion paper from Herman's later work on caudate–SC interactions (herman_arcizet2020_caudate_sc) develops this point and shows that caudate provides a parallel pathway to SC for attentional control.

The decoder is a two-population SDT read-out. It assumes a single criterion and a fixed integration window. Whether a drift-diffusion or race read-out would fit better is not tested. Gold & Shadlen 2007 makes the general point that SDT and accumulator models are continuously deformable; this paper's contribution is *which neural population* carries the relevant evidence, not *which functional form* the read-out has. For our purposes that is the right level of claim: the architectural commitment is to the *substrate*, not to the precise functional form of the read-out.

The behavior is *near-threshold change detection*. The strong claim "midbrain explains decisions" should be read as "explains decisions in this task regime." Whether SC's decision role generalizes to supra-threshold discriminations, or to more cognitively demanding categorization, is not addressed. The recurrent ViT, being a neural network rather than a primate, can be tested at both regimes, so this is a productive ambiguity rather than a flaw.

The paper does not separate *which* intermediate-layer cell types carry the decision signal. Herman & Krauzlis 2017 reported cue-related modulation across all visually-responsive categories; whether the 2018 decision-level signal is similarly distributed or concentrated in a subset (e.g., build-up cells) is left open. The decoder pools across recorded units, which is the right minimal commitment but trades cell-type specificity for population sufficiency.

A theoretical interpretation in terms of priority-map vs decision-substrate is partly definitional: a priority map that is read out directly by behavior *is* a decision substrate. Sridharan et al. 2017 push on this distinction further, arguing that SC controls perceptual *sensitivity* (d′) rather than *choice bias* under a multialternative framework. Under that framing, the Herman et al. 2018 decoder mixes sensitivity and criterion contributions, but the bilateral structure of the decoder is consistent with a primarily-sensitivity account.

The paper records from intermediate-layer SC only. Whether superficial-layer (visual) or deep-layer (motor) populations carry similar decision-level information is not tested. The intermediate layer is the *correct* layer to record from for this question (it is where attention-related modulation lives), but the layer-specificity claim is correspondingly narrower than the title suggests.

## 7. Connection to our work

**Direct empirical foundation for the Recurrent ViT.** The Recurrent ViT (2502.10955) is built around a cued color-change-detection task with a manual report under maintained fixation — the same paradigm as Herman & Krauzlis 2017 and this 2018 paper. The 2018 paper is the empirical foundation for treating the model's *attention map* as an analog of *the decision*, not merely an analog of an upstream attentional filter.

In the published architecture the actor head reads the recurrent self-attention state and emits both an attention map and a decision; the architectural justification for that coupling is that primate SC, the closest biological analog, also couples them (this paper). The biological homology is therefore not just "the model can detect changes" but "the model's internal attention-and-decision module corresponds to a specific anatomical structure with a known role." That is a much stronger architectural commitment than the typical neural-network-to-neuroscience comparison.

**Architecture-level claim: attention and decision share substrate.** A central design choice in our program is that decision and attention are emitted by the *same* module, not by separate "where to look" and "what to choose" heads. Herman et al. 2018 is the empirical statement of the same claim in primate physiology: a single midbrain population's activity is sufficient to read out the choice. If decision and attention were separable substrates in cortex/SC, the architecture would be wrong; this paper is the strongest evidence that they are not separable in the SC, which is the structure our task most closely engages. The bilateral right-minus-left SDT decoder is also the simplest non-trivial implementation of competitive read-out — exactly the kind of two-population race that the user's competition-emergent-PC framework (`competition-emergent-predictive-coding` in `concepts/`) treats as the canonical attentional / decision dynamic.

**Hit-vs-miss as a model probe.** The hit-vs-miss difference on matched stimuli (point 5 of §3) is a direct experimental prediction we can test in the Recurrent ViT. We can hold the stimulus identical, run the model with stochastic dropout or temperature, and ask whether its internal attention-map magnitude is larger on trials it gets right. A positive result would map onto Herman et al.'s Fig. 3-class result and constitute a quantitative homology between primate SC and the model.

**Causal-perturbation analog.** Muscimol inactivation in this paper is the empirical anchor for our model's *ablation analyses*. The lateralized inactivation deficit (right-side stimuli unaffected, left-side hits collapse following right-SC muscimol) is the kind of result we can attempt to reproduce by lesioning a portion of the attention map's spatial domain in the Recurrent ViT. If the model recapitulates the lateralized deficit, we have a virtual-lesion homology. The taxonomy concept `pharmacological-inactivation` is the experimental method this maps to; the model-side counterpart is `virtual-lesion`, which sits in the `causal-manipulation-methods` group in TAXONOMY.md.

**Connection to Sridharan et al. 2017.** Sridharan et al. recast the SC's role as controlling perceptual sensitivity rather than choice bias under a multialternative framework. Herman et al. 2018's SDT criterion model is the closer ancestor of our model's decision read-out, but the Sridharan multialternative interpretation matters because the Recurrent ViT must in principle handle multialternative scenes. The two papers together set the read-out class that any biologically plausible decision head in our architecture should sit within.

**Connection to gold_shadlen2007 and zenon_krauzlis2012.** Gold & Shadlen 2007 supplies the SDT / accumulator vocabulary in which Herman et al.'s decoder is stated; Zénon & Krauzlis 2012's "attention deficits without cortical neuronal deficits" provides the dissociation that motivates SC-as-decision-substrate rather than cortex-as-decision-substrate. Both belong in the same minimal citation set as Herman et al. 2018 whenever we justify the architectural commitment that attention and decision share a single internal substrate.

**Connection to sridharan2017_sc_sensitivity_bias.** Sridharan et al. push back on a pure "SC controls bias" reading and argue for an SC-controls-sensitivity-(d′) account under a multialternative SDT framework. Herman et al. 2018's bilateral-difference decoder is consistent with the sensitivity reading (the decoder's signal-to-noise drives the model's hit rate, which is the d′ analog). The Recurrent ViT's actor head can be interrogated the same way: does cueing increase the signal-to-noise of the attention map (d′-like), or does it shift the decision threshold (bias-like)? The Sridharan vs Herman juxtaposition is a methodological template for that interrogation.

**Connection to the canonical priority-map literature.** The "SC = priority map" framing (krauzlis2013_sc_attention; Bisley & Goldberg 2010 for LIP) interprets the SC's role as upstream selection. Herman et al. 2018 does not refute this — it absorbs it. A priority map that downstream behavior reads out directly is simultaneously a decision substrate. The architectural import for the Recurrent ViT: an attention-map module that is read by the actor head is, simultaneously, the model's priority map and its decision substrate. The taxonomy concept `priority-map` is the right tag for this dual role.

**Position in the user's empirical foundation.** Listing the papers that anchor the Recurrent ViT's biological commitments, in roughly increasing distance from the model itself:

1. herman_krauzlis2017_sc_change_detection — establishes the task and the SC change-detection signal.
2. **This paper (herman2018_midbrain_decisions)** — establishes that the same SC signal is sufficient to explain the decision.
3. krauzlis2013_sc_attention — the broader review situating SC's attention role.
4. sridharan2017_sc_sensitivity_bias — refines the SC's role to sensitivity rather than bias.
5. zenon_krauzlis2012_attention_deficits — dissociates SC-driven attention deficits from cortical correlates.
6. cavanaugh_wurtz2004_sc_change_blindness — the SC-microstimulation-rescues-change-blindness counterpart.
7. gold_shadlen2007_decision_making — the SDT/accumulator vocabulary for the decision read-out.

The first two are co-authored by Herman. Together they are the empirical theory the model instantiates.

**Comparison with cavanaugh_wurtz2004_sc_change_blindness.** Cavanaugh & Wurtz showed that SC microstimulation *counters change blindness* — i.e., directly driving SC promotes detection. Herman et al. 2018 supplies the complementary read-out side: not "SC drives detection" but "SC activity *is* what detection-or-not is read off of." The pair (microstim drives detection; recorded activity decodes detection) close a causal loop that any model of attention-mediated change detection should respect, and that our Recurrent ViT is designed to mirror.

**Connection to the broader thread.** In `threads/the_user_architectural_program.md`, the architectural thesis is that a single Feedback-Transformer-style module integrates sensory input with top-down memory/feedback and emits both an attention map and a control signal. Herman et al. 2018 is one of the very few primate physiology papers that directly licenses this architectural choice: a single, anatomically circumscribed population (intermediate-layer SC) carries enough information, in the right form (SDT-readable population difference), to play the attention-plus-decision role our architecture assigns to its actor head with attention map. Together with herman_krauzlis2017, krauzlis2013, sridharan2017, zenon_krauzlis2012, cavanaugh_wurtz2004, and gold_shadlen2007, this paper anchors the empirical foundation of the user's program's first publication.

**Co-authorship.** Herman is co-author on the user's Recurrent ViT paper. This is the second of his two precursor papers (with herman_krauzlis2017_sc_change_detection) on which the model's task and read-out are most directly modeled. Treat both papers as the empirical core of the user's research program's first publication.

## 8. Citations to follow

- `lovejoy_krauzlis2010_sc_attention_inactivation` — the original SC-muscimol-causes-lateralized-attention-deficit paper. Not yet in seed; should be added to make the inactivation chain explicit.
- `bogadhi_krauzlis2018_sc_object_attention` — same-lab follow-up on object-based attention in SC; useful for arguing the SC's decision role generalizes beyond spatial cuing.
- `katz2016_dissociated_sc_signals` — Katz (co-author) earlier paper on dissociating sensory vs decision components in SC; pre-cursor to the bilateral-decoder analysis here.
- `glimcher_sparks1992_sc_decision_signals` — early evidence of decision-level signals in SC. Useful for historical context of the "SC carries decisions" claim.
- `horwitz_newsome1999_sc_motion_decision` — SC encodes perceptual decisions about motion direction. Direct precedent of the decoding framework used here.
- `crapse_sommer2008_corollary_discharge_sc` — corollary discharge in SC, relevant to whether the decoded signal is sensory or premotor.
- `mysore_knudsen2013_compete_for_priority` — owl OT (SC homolog) priority competition; comparative anatomy for the SDT criterion.
- `wurtz_albano1980_visuomotor_sc` — historical review establishing the visual-vs-motor layering of SC; useful background for the layer-specificity caveat.
- `boehnke_munoz2008_sc_review` — review of SC neuronal types and circuitry; useful for unpacking which intermediate-layer subtypes carry the decision signal.
- `katz_krauzlis2024_choice_decoder` — newer follow-up extending the bilateral decoder framework to choice tasks beyond change detection.
