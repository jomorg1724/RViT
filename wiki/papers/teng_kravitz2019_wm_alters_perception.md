---
id: teng_kravitz2019_wm_alters_perception
title: "Visual working memory directly alters perception"
authors:
  - "Teng, Chunyue"
  - "Kravitz, Dwight J."
year: 2019
venue: "Nature Human Behaviour"
doi: "10.1038/s41562-019-0606-6"
arxiv: ""
url: "https://doi.org/10.1038/s41562-019-0606-6"
tags:
  - working-memory
  - visual-attention
  - psychophysics
  - early-visual-cortex
concepts:
  - attentional-template
  - working-memory-persistent-activity
  - top-down-feedback
  - gain-modulation
  - psychometric-function
related:
  - awh2006_attention_wm
  - kiyonaga_egner2013_wm_internal_attention
  - desimone1996_visual_memory_attention
  - panichello_buschman2021_shared_mechanisms
  - olivers2011_wm_states_attention
  - gupta_sridharan2024_presaccadic_change
  - gazzaley_nobre2012_topdown
  - bays2024_wm_representation
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_38
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual working memory directly alters perception

## 1. Abstract

Visual working memory (VWM) is known to recruit posterior perceptual cortices, creating overlap with the neural populations that support perception itself. Teng & Kravitz ask whether that overlap leaves a behavioural fingerprint: does merely *holding* a feature in VWM bias how an observer subsequently *sees* an independent test stimulus? Across multiple psychophysical experiments using colour and orientation, they show that the content of VWM produces directional, feature-specific biases in basic perceptual reports of new stimuli, even when those stimuli are entirely task-irrelevant to the memory load. The bias is bidirectional — perceptual stimuli also pull memory reports — and its pattern matches the tuning structure expected if memory and perception share early visual representations. The authors conclude that VWM does not merely *gate* attention to incoming stimuli; it *directly alters* the perceptual representation itself, consistent with a sensory-recruitment account in which the same neural substrate supports maintenance and perception.

## 2. Why this matters for us

Teng & Kravitz 2019 is the strongest behavioural demonstration we have that the contents of working memory *change what is seen*, not just what is selected. For the user's program — in which a single recurrent state $H^{(t)}$ feeds back into the self-attention substrate and modulates the bottom-up sensory projection $s_q, s_k, s_v$ via element-wise Hadamard product — this is the cognitive-science evidence that real biological systems do precisely this: the memory state is not an external bias on a decision stage, it is mixed into the perceptual signal itself. This directly licenses the Feedback Transformer's commitment to integrating recurrent state at the Q/K/V level rather than only at a decision head, and it grounds the iterative-VAE framing in which the decoder uses WM to actively reconstruct perception.

## 3. Key claims

1. **WM content biases perceptual reports of new stimuli.** Holding a colour or orientation in VWM shifts the reported value of a subsequent, independent test stimulus toward (or systematically away from) the memorised value.
2. **The effect is not attentional capture.** The memorised feature is held over the maintenance interval and the probe occurs during that interval; the memorised feature is task-irrelevant to the probe judgement, so classic attentional-capture or response-priming explanations are insufficient.
3. **The interference is bidirectional.** Perception of intervening stimuli also distorts the eventual memory report, with a comparable feature-specific signature.
4. **The bias pattern matches feature-tuning curves.** The magnitude and direction of the bias depend on the distance in feature space between the memorised and test values, in a manner consistent with overlapping populations of feature-tuned neurons.
5. **Shared substrate, not modular interface.** The data are most parsimoniously explained by VWM and perception relying on the *same* early-visual populations (sensory-recruitment account), rather than separate representations that exchange signals through an interface.
6. **The effect is robust across features.** The same qualitative pattern holds for colour and for orientation, two feature dimensions with well-characterised early-visual tuning, supporting generality rather than a stimulus-specific artefact.
7. **The effect depends on active maintenance.** Reducing the need to maintain the sample (e.g., post-cueing that it is no longer relevant) reduces or abolishes the perceptual bias, confirming that the modulator is the *active memory representation*, not the residual bottom-up trace of having seen the sample.
8. **Magnitude is comparable to sensory adaptation.** The behavioural shift caused by held-in-mind contents is on the same order as the shift produced by direct prolonged sensory exposure, suggesting that the memory representation engages the same gain-modulation machinery that sensory adaptation does.

## 4. Methods

A series of psychophysical experiments in adult human observers. Each trial follows a delayed-estimation structure with an interleaved perceptual probe.

**Memory phase.** A sample stimulus (a coloured patch or an oriented Gabor, depending on experiment) is presented briefly; the observer is instructed to maintain its colour or orientation across a delay for later reproduction.

**Perceptual probe.** During the delay, a perceptual test stimulus appears. The observer makes a perceptual judgement about this stimulus on a continuous report scale (e.g., adjusting a colour wheel or rotating an orientation dial) — this report is treated as a measurement of how the probe was *perceived*, not as a memory probe of the original sample.

**Memory report.** After the delay, the observer reproduces the memorised sample on the same continuous scale.

**Critical manipulation.** The feature distance between the held-in-memory sample and the perceptual probe is parametrically varied across trials, so the analyst can plot the perceptual report's *bias* (signed deviation from the true probe value) as a function of this distance.

**Counterfactual / control conditions.** Conditions vary the load (single item vs multiple), the relevance of the memorised feature, and the timing of the probe within the delay, allowing the authors to argue that attentional capture, response priming, and decision-stage carryover cannot fully account for the result.

**Analyses.** Continuous-report data are fit with standard mixture or precision models for memory; perceptual bias is analysed as signed angular (or chromatic) error as a function of memory–probe distance, yielding the canonical "Mexican-hat" / derivative-of-Gaussian bias signature when neighbouring tuned populations interact.

**Why this design isolates representational overlap.** The crucial design feature is that the perceptual probe is *task-irrelevant to the memory load*: observers are not asked to compare the probe to the sample, and the probe's feature value is uncorrelated with the eventual memory test. Any influence of the memorised value on the probe report must therefore arise from a *passive* property of the maintenance representation — i.e., from its overlap with the substrate on which the probe is itself represented — rather than from a decision strategy that weighs memory against probe. This is the load-bearing methodological point of the paper, and it is what licenses the sensory-recruitment interpretation over a downstream-interface account.

## 5. Results

The principal quantitative pattern: perceptual reports of the probe are systematically *shifted* relative to the probe's true value as a function of the held-in-memory feature.

- **Direction of bias.** At small feature distances between memory and probe, the perceptual report is *attracted* toward the memorised value; at intermediate distances, the report is *repelled* away. This is the signature of overlapping, tuned, mutually inhibiting populations — the same signature that has long been reported for *purely perceptual* serial dependence and adaptation phenomena.
- **Magnitude.** Bias magnitudes are small but reliable on the order of a few degrees (orientation) or a few degrees of colour-wheel angle, comparable to perceptual adaptation effects from prolonged sensory exposure — except here the inducer was never seen during the probe, only held in mind.
- **Bidirectional interference.** The memory report at the end of the trial is *also* biased by the intervening probe, with a comparable feature-distance dependence, indicating that probe perception leaves a residue in memory just as memory leaves a residue in probe perception.
- **Robustness across features.** The same qualitative bias profile is obtained for colour and for orientation, suggesting the mechanism is general across early-visual feature dimensions rather than specific to one cortical map.
- **Dissociation from response-stage explanations.** Controls (e.g., manipulating which feature is task-relevant; varying the probe's position in the delay) rule out a purely decision-stage account: the bias depends on what is actively *maintained*, not on what is *reported*.
- **Maintenance-dependent effect.** The bias is present when the sample is actively held (high-load or instructed-maintain conditions) and is reduced or absent in conditions that discourage maintenance, indicating that the modulator is the *active memory representation*, not the prior bottom-up exposure to the sample.
- **Feature-specificity within a dimension.** Within colour, the bias is organised around chromatic angle; within orientation, around orientation angle. Cross-feature controls (memorise orientation, probe colour) do not produce the bias, ruling out a generic arousal or task-set explanation.

The combined picture: a feature-specific, tuning-curve-shaped, maintenance-dependent, bidirectional influence of memory contents on the perception of an unrelated stimulus, of a magnitude comparable to classical sensory adaptation but driven by the internal state rather than by external input.

## 6. Critique / limitations

The work is *behavioural* throughout; the sensory-recruitment interpretation rests on inference from the bias signature rather than on direct neural measurement. The authors acknowledge this and frame the paper as a behavioural complement to the fMRI and electrophysiology literature on VWM in early visual cortex (Harrison & Tong 2009; Serences et al. 2009 — not yet in seed). A reader who is sceptical of the sensory-recruitment account could still defend a model in which a higher-level WM representation projects feature-specific top-down feedback that *modulates gain* in early visual cortex without sharing the representational substrate. The bias data alone do not distinguish these.

The effect sizes are modest. The biases are reliable across observers but small in absolute terms, and they live alongside much larger sources of perceptual error (sensory noise, response noise). Whether the same bias structure scales to richer naturalistic stimuli is an open question.

The feature dimensions tested (colour, orientation) are exactly those where early-visual tuning is best characterised. Generalisation to higher-level features (faces, objects, scenes) is plausible but not demonstrated. The Gupta & Sridharan 2024 presaccadic-change line of work suggests that similar memory–perception coupling extends to spatial position around saccades, but the parametric tuning-curve test has not been replicated for those features in this paradigm.

The paper does not adjudicate the *direction of causation* at the neural level. The bidirectionality of the behavioural interference is consistent with shared substrate, but a one-way top-down account with a separate WM store could in principle produce the same pattern under suitable assumptions. Causal manipulation (TMS to early visual cortex during the delay) would be needed to settle the issue and is not part of this paper.

Finally, the paper does not engage with computational accounts. The bias signature it reports is exactly the kind of behaviour that a recurrent generative-model or attractor-network account predicts (Wei & Stocker 2015 on Bayesian observers; sensory-recruitment models of VWM), but the authors do not formalise such a model.

A further open question: the paper conflates "shared substrate" with "direct modulation of perception". Sensory recruitment is one mechanism by which a memorised feature can shape perceptual reports, but a top-down predictive-coding loop — in which a higher-level WM representation projects a feature-specific *expectation* that biases lower-level inference — would produce the same behavioural bias signature without requiring the WM and perceptual representations to *be* the same neurons. Distinguishing these would require neural data with the resolution to track which population drives which, which this paper does not attempt. For the user's architectural program both mechanisms are interesting; the predictive-coding interpretation in particular is the one the Feedback Transformer most directly instantiates.

## 7. Connection to our work

Teng & Kravitz 2019 is *cognitive-science evidence for the central architectural commitment of the user's program*: that working memory does not sit outside perception as a separate store consulted by attention; it is *mixed into the perceptual representation itself*, with measurable consequences for what observers see. Every component of the user's program treats memory and perception as sharing a substrate; this paper supplies the behavioural counterpart.

**Feedback Transformer integration at Q/K/V.** The Feedback Transformer (thread §1) mixes recurrent state $C_i$ into the bottom-up sensory projections $s_q, s_k, s_v$ via element-wise Hadamard product *before* the softmax — i.e., the memory contribution alters the inner-product geometry that the attention head reads off the image, not a downstream decision. Teng & Kravitz's demonstration that the memorised feature shifts the *perceptual report* of an unrelated probe is the behavioural prediction this architecture makes: if memory modulates perception at the representational substrate, then holding a feature in mind should bias the perceived value of new stimuli with a tuning-curve-shaped signature. The published Recurrent ViT (2502.10955) instantiates this at one feedback source; the present paper says biology does it too.

**Single shared recurrent state.** The recurrent ViT maintains a single $H^{(t)}$ that serves both attention-guidance and WM-maintenance, consistent with Awh, Vogel & Oh 2006 ([awh2006_attention_wm](awh2006_attention_wm.md)) and Kiyonaga & Egner 2013 ([kiyonaga_egner2013_wm_internal_attention](kiyonaga_egner2013_wm_internal_attention.md)). Teng & Kravitz extend the shared-substrate claim one step further: not just that attention and WM share resources, but that WM and *perception* do. For the user's architecture this means the recurrent state should be expected to bias not only which tokens win the attention competition but also the *featural content* of the representation that downstream layers read.

**Iterative variational encoder–decoder.** In the iterative-VAE framing (thread §4), the decoder is initialised from the encoder's guide $H_{n_{FR}}$ and produces reconstruction proposals $\tilde X_\tau$ that are iteratively refined. The interpretation natural to Teng & Kravitz is that the decoder *uses WM to actively reconstruct perception* — the held-in-memory contents bias the proposal at every backward-reasoning step. This is exactly the bidirectional interference the paper reports at the behavioural level: memory shapes the perceptual proposal, and the perceptual evidence updates the memory state, with both processes living on the same representational substrate.

**Connection to Desimone 1996.** Desimone 1996 ([desimone1996_visual_memory_attention](desimone1996_visual_memory_attention.md)) provides the neural counterpart at the single-unit level — IT neurons' delay-period activity carries the maintained stimulus and biases responses to subsequent stimuli. Teng & Kravitz 2019 is the behavioural human-psychophysics counterpart of that finding, extended to early-visual feature dimensions (colour, orientation) rather than IT-level object features. Together they bracket the WM-alters-perception claim from neurophysiology (Desimone) and behaviour (Teng & Kravitz). The user's Feedback Transformer is consistent with both: the recurrent state feeding back into Q/K/V is, at the cellular level, the kind of memory-driven gain modulation Desimone reports.

**Connection to Panichello & Buschman 2021.** Panichello & Buschman 2021 ([panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md)) show that PFC implements *shared* control mechanisms for attention and WM. Teng & Kravitz extend the shared-mechanism story downward into early visual cortex: not only do PFC populations multiplex attention and WM, but the substrate where the perceptual signal lives is itself modulated by WM. The user's architecture spans both: the deep memory layers ($C_3$ in the 3-layer reference design, thread §3) play a PFC-like role, while the shallow memory layer $C_1$ — bound to V1-level patches — is the substrate where Teng & Kravitz's effect would live in the model.

**Connection to Olivers 2011 and memory-guided attention.** Olivers et al. 2011 ([olivers2011_wm_states_attention](olivers2011_wm_states_attention.md)) argue that the *state* of a WM representation (active vs accessory) determines whether it guides attention. Teng & Kravitz say something stronger: even when the memorised feature is *not* the basis for selection, it still shifts perceptual reports. For the user's architecture this implies that *any* recurrent state with non-zero coupling into the Feedback Transformer leaves a perceptual fingerprint, not only those that win the attention competition. The selection question (Olivers) and the representation question (Teng & Kravitz) are dissociable, and the user's architecture should be tested against both.

**Connection to Gupta & Sridharan 2024.** Gupta & Sridharan 2024 ([gupta_sridharan2024_presaccadic_change](gupta_sridharan2024_presaccadic_change.md)) report that presaccadic remapping interacts with WM contents to bias change detection at the saccade target. This is the same logic as Teng & Kravitz — WM contents shape early perceptual processing — extended to the spatial-remapping domain. Together they support the broader claim that WM is not a separate store but a continuous modulator of perceptual processing across feature, space, and time.

**Connection to the iterative-VAE objective.** The reconstruction-loss term in the iterative VAE (thread §4) weights $\sum_i \gamma_i \cdot \text{MSE}[\tilde X_i, X]$ across $n_{BR}$ decoder proposals. If the decoder's hidden state $\tilde H_\tau$ truly functions as working memory, Teng & Kravitz predict that early reconstruction proposals will be *biased* toward the contents of $\tilde H_0 = H_{n_{FR}}$ in a feature-tuning-curve sense, with the bias dissipating across iterations as the proposal converges. This is a concrete, testable consequence of treating the decoder as performing iterative WM-driven reconstruction rather than feedforward decoding.

**Connection to PRISM's inner variational-inference loop.** PRISM v1's inner loop (THESIS.md §2.8) updates a single $M_t$ at each timestep by minimising a variational free-energy objective. Teng & Kravitz's bidirectional interference is the prediction at the behavioural level: the memory state biases the perceptual likelihood at each inner-loop iteration, and the perceptual evidence updates the memory state in turn. The Mexican-hat bias signature is the cognitive-science footprint of the very Bayesian-update dynamics PRISM formalises.

**Multi-compartmental memory and the locus of the effect.** Within the user's 3-layer reference design (thread §3), $C_1$ is the V1-paired memory layer and is the most direct architectural homologue of the early-visual populations Teng & Kravitz invoke. The deeper $C_2, C_3$ layers correspond to higher-level WM representations. The behavioural prediction is that ablating top-down feedback from $C_2, C_3$ to $C_1$ should attenuate the perceptual bias, while leaving the bottom-up encoding intact. This is a concrete causal test of the layered-feedback architecture using a paradigm imported directly from the cognitive-science literature.

**Empirical test for the user's program.** A direct cognitive-science prediction of the Feedback Transformer is that a trained recurrent ViT, prompted with a sample stimulus and then probed with a perceptual judgement, should show a *tuning-curve-shaped bias* in its probe-report as a function of memory–probe feature distance. This is a relatively cheap test on Food-101 / synthetic stimuli, and a positive result would be a non-trivial behavioural alignment between the architecture and human psychophysics. A negative result would suggest the published single-feedback-source RViT is not yet rich enough to reproduce the human effect, and would motivate the multi-source feedback the full Feedback Transformer affords.

**Locating the paper in the WM–attention–perception triad.** Awh, Vogel & Oh 2006 established the *attention–WM* coupling; Kiyonaga & Egner 2013 promoted that coupling to "WM as internal attention"; Panichello & Buschman 2021 added a shared PFC control substrate; Olivers et al. 2011 separated active from accessory WM states; Desimone 1996 identified the IT-neuron substrate for the maintained representation. Teng & Kravitz 2019 closes the triangle by showing that the *perceptual* leg — the third side of the WM–attention–perception triangle — is also part of the shared substrate. This is the leg the user's program needs most: it justifies treating the recurrent memory state as part of the *perceptual representation itself*, not as an external bias on perception.

## 8. Citations to follow

- `harrison_tong2009_decoding_orientation_wm` — fMRI decoding of orientation maintained in VWM from early visual cortex (V1, V2). Direct neural support for sensory recruitment.
- `serences2009_stimulus_specific_delay_wm` — Stimulus-specific delay-period activity in early visual cortex during VWM. Companion to Harrison & Tong.
- `pasternak_greenlee2005_wm_sensory_cortex` — Review of WM in sensory cortex. Background for the sensory-recruitment account.
- `wei_stocker2015_bayesian_observer_perceptual_bias` — Bayesian-observer model of perceptual bias from prior knowledge; provides the computational frame Teng & Kravitz do not formalise.
- `fischer_whitney2014_serial_dependence` — Serial dependence in perception; the closest perceptual analog of the bias Teng & Kravitz report, but driven by recent sensory history rather than active VWM.
- `ester2015_feature_specific_wm_v1` — Feature-specific VWM representations in human V1. Independent neural evidence for the substrate the paper invokes.
- `zhang_luck2008_wm_precision` — Precision-based models of VWM that the continuous-report methodology rests on.
- `soto2008_wm_capture` — Held-in-WM features capture attention; the attentional-capture phenomenon Teng & Kravitz dissociate their perceptual-bias effect from.
- `bae_luck2017_dissociable_decoding` — Dissociable decoding signatures for active vs latent WM content; bears on whether the bias is driven by active or passive states.
- `souza_oberauer2016_in_context_memory` — Context-driven biases on continuous-report WM; methodological complement to the Teng-Kravitz design.
