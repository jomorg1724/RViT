---
id: gattass_desimone2014_sc_microstim
title: "Effect of microstimulation of the superior colliculus on visual space attention"
authors:
  - "Gattass, Ricardo"
  - "Desimone, Robert"
year: 2014
venue: "Journal of Cognitive Neuroscience"
doi: "10.1162/jocn_a_00570"
arxiv: ""
url: "https://doi.org/10.1162/jocn_a_00570"
tags:
  - primate-neurophysiology
  - subcortical
  - lesion-microstimulation
  - visual-attention
concepts:
  - microstimulation
  - cueing-effect
  - gain-modulation
  - priority-map
  - top-down-feedback
related:
  - cavanaugh_wurtz2004_sc_change_blindness
  - krauzlis2013_sc_attention
  - moore_armstrong2003_fef_microstim
  - mirpour2010_ppc_microstim
  - desimone_duncan1995_biased_competition
  - sridharan2017_sc_sensitivity_bias
  - bollimunta2018_fef_sc_covert
  - herman_krauzlis2017_sc_change_detection
  - moran_desimone1985_selective_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_117
status: full
depth: full
last_updated: "2026-05-16"
---

# Effect of microstimulation of the superior colliculus on visual space attention

## 1. Abstract

We investigated the effect of microstimulation of the superficial layers of the superior colliculus (SC) on the performance of animals in a peripheral detection paradigm while maintaining fixation. In a matching-to-sample paradigm, a sample stimulus was presented at one location followed by a brief test stimulus at that (relevant) location and a distractor at another (irrelevant) location. While maintaining fixation, the monkey indicated whether the sample and the test stimulus matched, ignoring the distractor. The relevant and irrelevant locations were switched from trial to trial. Cells in the superficial layers of SC gave enhanced responses when the attended test stimulus was inside the receptive field compared with when the (physically identical) distractor was inside the field. These effects were found only in an "automatic" attentional cueing paradigm, in which a peripheral stimulus explicitly cued the animal as to the relevant location in the receptive field. No attentional effects were found with block of trials. The transient enhancement to the attended stimulus was observed at the onset and not at the offset of the stimulus. Electrical stimulation at the site corresponding to the irrelevant distractor location in the SC causes it to gain control over attention, causing impaired performance of the task at the relevant location. Stimulation at unattended sites without the presence of a distractor stimulus causes little or no impairment in performance. The effect of stimulation decays with successive stimulations. The animals learn to ignore the stimulation unless the parameters of the task are varied.

## 2. Why this matters for us

Gattass & Desimone 2014 is the second pillar — together with Cavanaugh & Wurtz 2004 ([cavanaugh_wurtz2004_sc_change_blindness](research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md)) — of the SC-microstimulation evidence base that the recurrent ViT's perturbation experiment (2502.10955 §6.6) is the AI analog of. Where Cavanaugh & Wurtz showed that subthreshold SC stimulation *facilitates* attention at a cued location, Gattass & Desimone show the complementary *interference* effect: stimulating an SC site that encodes an irrelevant distractor location causes it to win the attentional competition, *impairing* performance at the genuinely relevant location. This is the SC analog of Moore & Armstrong's FEF microstimulation work, and — crucially — it is co-authored by Robert Desimone, the originator of the biased-competition framework (Desimone & Duncan 1995). The paper therefore links subcortical attention machinery directly to the cellular-level competitive account that the user's program ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md)) generalizes into multi-hub coalition competition.

## 3. Key claims

1. **Attentional enhancement in superficial SC.** Cells in the *superficial* (visual) layers of the SC show enhanced responses to physically identical stimuli when those stimuli are the attended target rather than the to-be-ignored distractor. This pushes the locus of SC attention modulation up from the intermediate layers (Cavanaugh & Wurtz) into the visual layers themselves.
2. **Automatic cueing required.** The attentional gain is observed only when an explicit peripheral cue marks the relevant location on each trial (an "automatic" cue). Block designs in which the relevant location is held constant for many trials produce no enhancement — implying the effect depends on trial-by-trial reorientation rather than on stable strategic set.
3. **Onset-locked, transient gain.** The enhancement is locked to stimulus onset and is transient; the offset of the stimulus does not produce a comparable enhancement.
4. **Microstimulation at a distractor site captures attention.** Subthreshold microstimulation at the SC site encoding the *distractor* location causes that distractor to gain control over attention, producing *impaired* discrimination at the relevant location. This is a causal demonstration that SC activity *is* a sufficient priority signal.
5. **Stimulation without a competing distractor is roughly innocuous.** Stimulation at unattended retinotopic sites in the absence of a competing stimulus does not strongly impair performance — the effect is competitive, not a generic disruption.
6. **Adaptive ignoring.** The behavioral impact of SC stimulation decays with repetition: the animal learns to ignore the stimulation. The effect is restored when task parameters change. Attention to electrical stimulation is itself plastic.
7. **Locus in the superficial (visual) layers.** Unlike Cavanaugh & Wurtz 2004, whose stimulation targeted intermediate (sensorimotor) SC layers, the recording effects here are in the superficial visual layers — establishing that the attention modulation visible in SC is not exclusively a property of the saccade-related sensorimotor sheet but already present at the visual input stage of the structure.

## 4. Methods

**Task.** A matching-to-sample paradigm under fixation. On each trial: (i) a sample stimulus appears at one peripheral location, (ii) after a delay, a test stimulus appears at the same (relevant) location while a distractor appears at a second (irrelevant) location, (iii) the monkey reports match vs non-match between sample and test by manual response, ignoring the distractor. Fixation is required throughout — the attention shift is covert. Relevant and irrelevant locations are swapped trial-by-trial in the "automatic cue" condition (the relevant location is wherever the sample just appeared, so the sample itself acts as an exogenous cue); in the "block" condition, the relevant location is held constant for many consecutive trials.

**Recording.** Single-unit recordings from the superficial visual layers of SC during task performance. The receptive field of each recorded cell was mapped before each session. The placement of test vs distractor was counterbalanced trial-by-trial so that each unit was assayed in both conditions with physically identical stimuli inside its RF, isolating the attentional effect from any stimulus-driven differences.

**Microstimulation.** Subthreshold (sub-saccadic) electrical microstimulation was delivered to SC sites whose retinotopic encoding matched either the irrelevant distractor location or an otherwise unattended location. Stimulation was timed to coincide with the test/distractor display. Stimulation parameters were below the threshold for evoking saccades — the manipulation is purely a perturbation of the SC priority signal, not a motor command, so fixation is maintained throughout.

**Design contrasts.** Three principal contrasts: (a) test-in-RF vs distractor-in-RF, isolating attentional gain in the recording experiment; (b) automatic-cue trials vs block trials, isolating the cue-driven nature of the gain; (c) stim-at-distractor-site vs stim-at-neutral-site vs no-stim, isolating the *competitive* nature of the microstimulation effect.

**Behavioral measures.** Match/non-match accuracy on the discrimination, RT, and the across-trial decay of the stimulation effect. The decay analysis tracks how the impairment caused by SC stimulation evolves over successive stimulation trials and across changes in task parameters.

**Why the automatic vs block contrast matters.** In the automatic-cue condition the sample stimulus is an exogenous spatial cue: it tells the animal where the relevant location will be on the upcoming test display. In the block condition the relevant location is known *a priori* — there is no per-trial cue because the animal already knows. The dissociation is therefore between *transient, cue-driven* attention shifts (where SC participates) and *sustained, endogenous* attentional set (where, by this measure, SC apparently does not). This dovetails with the broader characterization of the SC as a node specializing in exogenous-orienting rather than endogenous-maintenance attention.

## 5. Results

The principal quantitative findings:

- **Attentional enhancement, superficial layers.** Single-unit firing rates in superficial SC were higher when the attended test stimulus was in the RF than when the physically identical distractor was in the RF. The two conditions are matched stimulus-by-stimulus, so the modulation is purely attentional — not a feature- or contrast-driven response difference.
- **Onset-locked, automatic-cue-dependent.** Enhancement appeared at stimulus onset and was abolished under block-of-trials designs in which the relevant location was held constant. It is the transient orienting response to a fresh cue that drives the SC modulation, not a stable strategic attentional set.
- **No offset enhancement.** The transient enhancement is locked to *onset*; comparable enhancement is not seen at stimulus offset, ruling out a generic arousal account.
- **Distractor-site stimulation impairs the task.** Stimulating an SC site whose RF contained the distractor caused the distractor to win the attentional competition: discrimination accuracy at the relevant location dropped substantially relative to no-stim baselines.
- **Stimulation at neutral sites is benign.** Stimulating SC sites that encoded locations without a competing stimulus produced little or no behavioral impairment, isolating the effect as one of *competitive capture* rather than generic disruption of fixation, motor planning, or arousal.
- **Adaptive decay.** The behavioural impact of stimulation shrank across repeated stimulation trials — the animal learned that the electrically-induced "cue" was uninformative and behaviorally ignored it. Changing task parameters reinstated the effect, demonstrating that the discount is context-specific rather than a fatigue or adaptation artifact.

## 6. Critique / limitations

The paper combines two methods (recording + stimulation) on a small monkey cohort; the stimulation experiments are not powered for fine parametric mapping over current, frequency, or train duration. The cell counts in the recording component are also modest by current standards, so the effect-size distribution of attentional enhancement across superficial SC is only coarsely characterized.

The "automatic vs block" cueing dissociation is intriguing but is reported at one level of design contrast. A more graded manipulation of cue informativeness — varying cue validity continuously, or varying the predictive horizon — would clarify whether the SC modulation tracks transient phasic orienting per se or the predictive value of the cue. As reported, the dissociation could be explained either by an exogenous-attention account (only sudden onsets recruit SC) or by a predictive-coding account (only events with unresolved spatial expectations recruit SC).

Electrical stimulation, as in all such work, activates an inhomogeneous population of SC neurons and fibres of passage. The cellular substrate of the attention-capture effect is therefore not identified. Subsequent optogenetic and pharmacological work in SC (Krauzlis 2013 review; Bollimunta, Bogadhi & Krauzlis 2018) has refined the cell-type-specific story, and any modern replication should pair behavioral microstimulation with optogenetic targeting.

The adaptive-decay observation is striking but underexplored: it implies that the SC priority signal can be discounted when it stops carrying behavioral information, which raises mechanistic questions the paper does not answer. Where does the downstream "discounting" occur — within SC itself, in the SC→pulvinar→cortex pathway, or in cortical priority maps (LIP, FEF) that pool SC and cortical input? The Sridharan et al. 2017 sensitivity/bias decomposition (`sridharan2017_sc_sensitivity_bias`) is one tool that could be brought to bear.

The paper does not formally connect its results to the biased-competition framework Desimone co-developed (Desimone & Duncan 1995). The connection is left for the reader; in this database we make it explicit in §7.

The paper also does not engage with the parallel cortical microstimulation literature (Moore & Armstrong 2003 for FEF; later work in LIP and PPC). Reading it in isolation, one would not learn that the SC effect coexists with — and partly overlaps — equivalent effects at multiple cortical priority nodes. The Krauzlis 2013 review covers this synthesis; this paper is best read alongside it.

## 7. Connection to our work

This paper supplies four foundations for the user's program. The first three are common to all SC-microstimulation evidence and shared with the companion entry [cavanaugh_wurtz2004_sc_change_blindness](research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md); the fourth is unique to this paper, arising from its co-authorship by Desimone and its explicit competitive design.

**SC microstimulation as the biological analog of attention-map perturbation.** The recurrent ViT (2502.10955 §6.6) introduces perturbations directly into the model's attention map and reports behavioral consequences analogous to FEF microstimulation (Moore & Armstrong 2003). Gattass & Desimone 2014 is the SC analog. Critically, it demonstrates the *adversarial* form of the perturbation: stimulating a site encoding the wrong location captures attention and impairs performance. This is the biological precedent for perturbation experiments that introduce *misleading* priority signals into the model rather than only facilitatory ones — a richer experimental protocol than the recurrent ViT paper currently reports.

The companion paper [cavanaugh_wurtz2004_sc_change_blindness](research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md) supplies the facilitatory pole (SC stim improves detection at the cued location); the present paper supplies the adversarial pole (SC stim at the wrong location impairs detection at the correct one). The recurrent ViT's perturbation methodology should be evaluated against both poles — a model whose attention can be improved by adding bias to the target's attention slot but cannot be *misled* by adding bias to a distractor's slot would be a poor mechanistic match for biological attention.

**Biased competition at the architectural scale.** Desimone is the co-author of the biased-competition framework (Desimone & Duncan 1995), which the user's program ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §5) generalizes from cell-level competition for representational bandwidth to coalition-level competition for self-attention control. Gattass & Desimone 2014 is biased competition realized causally: a subcortical priority node, electrically driven, biases the cortical attentional competition by injecting a stronger signal at the distractor location. The user's "competition-emergent predictive coding" thesis predicts exactly this: any hub that wins the priority competition gains representational bandwidth, and the SC is one such hub at the subcortical level.

In the user's formal account of the competition ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §5, "Formal account of the competition"), the final Q vector for stimulus $i$ is $q_i = s_{q,i} \odot (c^{(\text{RL})}_{q,i} + c^{(\text{dec})}_{q,i})$ and the attention score $\alpha_i = \langle q_i, k_i \rangle$ depends multiplicatively on all hubs' contributions. SC microstimulation is the biological injection of a large, spatially-targeted $c^{(\text{SC})}_q$ term — one whose magnitude wins the competition for the corresponding spatial slot. The behavioral impairment Gattass & Desimone observe is the predictable consequence: the distractor's $\alpha_i$ exceeds the target's, and the readout downstream attends to the wrong location. This is as direct a biological validation of the user's "hubs compete by manipulating Q/K projections" formalism as the literature offers.

**The Feedback Transformer as the architectural substrate.** In the Feedback Transformer primitive ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §1), every recurrent state projects its own Q/K/V that combines with the bottom-up sensory projection prior to softmax. An SC-analog hub would be one such recurrent state — a low-resolution, retinotopically-organized priority map that injects multiplicative gain into the cortical attention competition. Gattass & Desimone 2014 supplies the empirical grounding: such a hub, when stimulated at the wrong location, should *redirect* the model's attention to that location and impair performance — exactly the architectural test the user's program suggests for the multi-hub system.

Practically, this paper argues for explicitly adding an SC-analog hub to the multi-hub system once the core MSI + RL + VAE triple is working. The hub would be retinotopically organized, would receive bottom-up visual input and top-down task signals, and would inject its Q/K projections into the central Feedback Transformer. The validation test follows directly from Gattass & Desimone: drive the hub's activation at a non-target retinotopic slot and verify that change-detection accuracy at the target slot drops, recovering after some number of consecutive misleading drives (the "adaptive discounting" signature).

**Adaptive discounting as a regularizer.** The decay of the stimulation effect across trials — the animal learning to ignore an uninformative cue — is the biological analog of the "ability to shut off feedback inputs" the user identifies as a key design choice in the multi-compartmental memory ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §3). If a hub provides feedback that is consistently uninformative, the receiving layer can discount it. The SC's behavioral discounting establishes that this kind of plasticity operates on real subcortical attention signals, not only on idealized memory inputs.

**Onset-locked transient gain matches the GridCell RNN update rhythm.** The result that SC enhancement is locked to stimulus *onset* and not offset aligns with the user's GridCell RNN ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §2), where each new input drives an SIP proposal that is then integrated with feedback states. A "phasic" priority hub that fires only at input onsets fits naturally into this rhythm: it would supply a transient bias to the Feedback Transformer's K/V projections at the moment a new stimulus arrives, exactly the temporal profile Gattass & Desimone report.

**A concrete recurrent-ViT experiment.** The paper suggests a specific experiment for the recurrent ViT that goes beyond 2502.10955 §6.6. Currently the perturbation experiment biases the model's attention map at a single retinotopic location and reports detection-time changes. Gattass & Desimone's design adds two structures: (i) a *competing* stimulus at a separate retinotopic location, and (ii) trial-by-trial swapping of which location is "relevant." The recurrent-ViT analog would inject attention-map perturbations at the *distractor* location during a change-detection trial with two candidate change loci, and measure whether change-detection accuracy at the relevant location is correspondingly impaired. The prediction — that competitive capture should replicate in the model — is a sharp falsifiable test of the biased-competition account at the architectural level, and one that the published recurrent ViT could be retrained to support with no architectural change.

The 2502.10955 paper lists this work as reference [117] (`seed_source: vit_paper_ref_117`). The companion entry [cavanaugh_wurtz2004_sc_change_blindness](research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md) covers the facilitatory side of SC stimulation; this entry covers the adversarial side. Together they bracket the design space for any SC-analog hub the user's program might eventually add to the multi-hub system.

## 8. Citations to follow

- `cavanaugh_wurtz2004_sc_change_blindness` — facilitatory SC-stim companion; together with this paper, brackets the bidirectional behavioral consequences of SC priority signals. In seed, full depth.
- `moore_armstrong2003_fef_microstim` — FEF-microstim analog; the cortical-source counterpart to the present subcortical-source result. In seed.
- `desimone_duncan1995_biased_competition` — Desimone's theoretical frame; the present paper is biased competition realized causally at the SC level. In seed.
- `krauzlis2013_sc_attention` — modern SC-attention review; situates this paper within the broader SC-attention literature. In seed.
- `mirpour2010_ppc_microstim` — PPC-microstim parallel; demonstrates that priority-map perturbation is not unique to SC. In seed.
- `sridharan2017_sc_sensitivity_bias` — SC contribution to perceptual sensitivity vs decision bias under stimulation; refines the priority-map interpretation. In seed.
- `moran_desimone1985_selective_attention` — extrastriate gating result; the cellular template for the attentional-enhancement assay used here. To add.
- `bollimunta2018_fef_sc_covert` — FEF vs SC covert-attention dissociation; identifies where the SC's contribution is necessary vs sufficient. In seed.
- `herman_krauzlis2017_sc_change_detection` — color change-detection follow-up to the Cavanaugh & Wurtz paradigm; relevant for translating the present matching-to-sample design into change-detection space. In seed.
