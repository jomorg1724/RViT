---
id: ghose_maunsell2002_task_timing
title: "Attentional modulation in visual cortex depends on task timing"
authors:
  - "Ghose, Geoffrey M."
  - "Maunsell, John H. R."
year: 2002
venue: "Nature"
doi: "10.1038/nature01057"
arxiv: ""
url: "https://www.nature.com/articles/nature01057"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
  - psychophysics
concepts:
  - gain-modulation
  - attentional-spotlight
  - top-down-feedback
  - recurrence-for-temporal-dynamics
related:
  - sani2017_temporal_v4_gain
  - nobre_vanede2018_anticipated_moments
  - reynolds_heeger2009_normalization
  - kietzmann2019_recurrence_required
  - mante2013_context_dependent_pfc
  - desimone_duncan1995_biased_competition
  - treue_martinez_trujillo1999_feature_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_59
status: full
depth: full
last_updated: "2026-05-16"
---

# Attentional modulation in visual cortex depends on task timing

## 1. Abstract

Paying attention to a stimulus selectively increases the ability to process it; classical accounts of this attentional enhancement treat the resulting modulation of sensory neurons as a quasi-static gain set by where (and on what) the subject attends, held roughly constant for the duration of the attended interval. Ghose and Maunsell trained two macaques on a change-detection task in which the probability of the to-be-detected event was systematically structured across time within a trial, so that the subjects' temporal expectation of the event varied continuously throughout the wait period rather than being uniform.

Recording from area V4 while the monkeys performed the task, the authors show that the magnitude of attentional modulation of V4 firing rates tracked the trial-by-trial time course of event probability rather than remaining constant for the duration of attended viewing. Modulation was largest at the moments when the change was most likely to occur, and was correspondingly reduced when the event was unlikely or had already passed. The behavioural hit-rate distribution as a function of within-trial time mirrored the V4 modulation profile, tying the neural signal directly to behavioural readiness.

Attentional modulation of sensory cortex is therefore not a static spatial / feature-based gain but a temporally dynamic signal that reflects the subject's anticipation of when behaviourally relevant events will occur, and that is rebuilt as task statistics change.

## 2. Why this matters for us

The user's program treats attention as a *recurrent state* that evolves over time within a stimulus presentation, not as a fixed transformation of a static input. Ghose & Maunsell 2002 is the canonical primate-physiology evidence that exactly this is what cortex does: V4's attentional gain is a function of within-trial time, slaved to the subject's internal estimate of event probability.

The Recurrent ViT's commitment to temporally evolving self-attention maps across recurrent passes (`2502.10955` §6.7; Food-101 attention-map visualisations in the user's *Classifier* note) and PRISM's commitment to a time-varying FiLM modulation $\gamma_t, \beta_t$ produced by a recurrent memory state $M_t$ are both architectural bets that this Ghose-Maunsell-style temporal dynamic is the right level of description for cortical attention, and the right behavioural target for a biologically plausible attention module. The paper is therefore a load-bearing empirical anchor for the user's commitment to *recurrent* attention rather than feedforward attention, and a direct prediction-target for the dynamics of attention weights / FiLM gains across recurrent steps.

## 3. Key claims

1. Attentional modulation of V4 neurons is not constant across the duration of an attended trial; it varies systematically with within-trial time.
2. The temporal profile of V4 modulation tracks the probability distribution of the behaviourally relevant event, peaking when the event is most likely and falling when the event is unlikely.
3. The behavioural hit-rate distribution as a function of within-trial time covaries with the V4 modulation profile, linking the neural signal to behavioural readiness.
4. Modulation magnitude is dynamic on the timescale of a single trial (hundreds of milliseconds to seconds), not only across trial blocks; the same neuron exhibits different attentional gain at different moments of the same trial.
5. The temporal profile is reorganised within tens of trials when the event-probability distribution is changed, showing that the underlying signal is learned online and reflects current task statistics rather than a fixed wiring property.
6. The result generalises the spatial / feature-based gain framework of attention to a third, temporal axis: attention is *when* as well as where and what, and the three axes are not separable in V4 firing rates.
7. Modulation magnitudes are graded rather than all-or-none, supporting normalisation / gain-field accounts of attention over discrete spotlight accounts.
8. The temporal-expectation signal that drives the V4 modulation must originate outside V4 itself, since V4 has no direct access to abstract task-timing statistics; the paper localises a *consequence* of the signal in V4 without identifying its source.

## 4. Methods

**Animals and task.** Two macaque monkeys were trained on a delayed change-detection task. The animal fixated a central spot, two peripheral grating stimuli were presented, and on each trial one of the gratings changed at an unpredictable but task-structured time. The temporal distribution of the change event was deliberately non-uniform across the trial wait period — for example, the change probability could be peaked at one or more specific moments and low at others — so that the monkey could (and behaviourally did) acquire an internal model of "when" the change was most likely within the trial. The animal reported the change by making a saccade or releasing a bar, with reward contingent on correct, timely detection.

**Recording.** While the monkeys performed this task, single-unit activity was recorded extracellularly from area V4. The stimulus configuration was arranged so that one of the gratings fell inside the receptive field of the recorded neuron and the other lay outside it, allowing the same physical stimulus to be presented under both the "attend in" and "attend out" conditions in interleaved blocks.

**Operationalisation of attentional modulation.** Attentional modulation was operationalised as the difference (or ratio) in firing rate to an identical stimulus when it was the attended target versus when it was the unattended distractor. By replaying the same neutral stimulus at many within-trial times under both attention conditions, the authors could read off a *time course* of attentional modulation against within-trial time, separated from any stimulus-driven response transient. This is the methodological key: any apparent time course in the firing rate would otherwise be confounded with the stimulus onset transient.

**Behavioural quantification.** Behavioural readiness was quantified in parallel by binning hit rates and false-alarm rates as a function of within-trial time, producing a behavioural readiness function for each event-probability distribution that could be overlaid on the neural modulation function. The experimental block structure ensured that each animal had time to acquire the relevant temporal statistics before the recording window. The probability distributions used spanned simple peaked, double-peaked, and broad profiles, so that the neural-behavioural alignment could be tested under non-trivially different temporal expectations rather than only a single canonical shape.

## 5. Results

**Temporal profile of V4 gain tracks event probability.** The principal finding is that attentional modulation of V4 firing rates has a non-flat temporal profile that mirrors the event-probability distribution imposed by the task. When the change was scheduled to be most likely early in the wait period, V4 modulation rose early and decayed later; when it was scheduled to be most likely late, modulation rose late. The neural profile peaked at the moment of maximum event probability rather than being uniformly elevated across the attended interval.

**Same cell, different profiles.** Critically, the same V4 neuron showed a different temporal profile of modulation under different event-probability schedules, confirming that the time course is a property of the task-and-state, not of the cell. This rules out the trivial reading that some V4 neurons are simply "early" cells and others "late."

**Neural-behavioural alignment.** The behavioural hit-rate distribution as a function of within-trial time covaried with the V4 modulation profile: monkeys were faster and more sensitive at the moments where V4 gain was highest, and slower / less sensitive at moments where V4 gain was reduced. The neural and behavioural readiness functions were thus aligned within a single experimental block, providing a tight link between sensory-cortex gain and behavioural state.

**Online learning of the time course.** The temporal profile of modulation reorganised within tens of trials when the event-probability distribution was changed, showing that the underlying signal is learned online and reflects the subject's current expectations, not a fixed sensory-cortical property. The paper does not require the modulation to be all-or-none; rather, it is a *graded* gain whose magnitude is itself a function of time, consistent with the normalisation / gain-field family of attention models (Reynolds & Heeger 2009) rather than with a discrete spotlight.

**Population-level robustness.** Effects were robust across the recorded population: the temporal modulation was visible at the level of individual cells and amplified at the level of population averages, indicating that the temporal-expectation signal reaches V4 in a distributed rather than channel-specific way. The authors do not require all V4 cells to share an identical time course; rather, the population code as a whole tracks the event-probability distribution in a way that an ideal-observer readout could exploit.

## 6. Critique / limitations

**No source identification.** The paper does not isolate the cortical *source* of the temporal-expectation signal that reshapes V4 gain. Frontal (FEF, dlPFC) and parietal (LIP) areas are the candidate generators, and pulvinar / thalamic loops have since been implicated; but Ghose & Maunsell 2002 only documents that V4 receives such a signal, not where it is computed. Causal manipulations of candidate generators (microstimulation, inactivation) appear in later literature and are required to settle the mechanistic question.

**Sample size and quantitative fit.** Only two animals contributed data, and the recorded population, while substantial for single-unit primate work, is not large by modern standards. The functional form of the relation between event probability and modulation magnitude is described qualitatively (peaks align; troughs align) rather than fit to a single quantitative model. A formal hazard-function fit — predicting modulation magnitude at each within-trial moment as a function of the conditional probability of the event given that it has not yet occurred — would have tightened the claim; that step is taken in subsequent V4 work (Janssen & Shadlen 2005 in LIP; later V4 papers).

**Correlation vs. causation.** The paper documents covariation between V4 modulation and behavioural hit rates but does not establish causation. It remains possible that both V4 modulation and behaviour are driven by a third, upstream signal (priority map, FEF preparatory activity), with V4 a passive readout rather than a causal contributor to the behavioural improvement. Decoding analyses on the V4 population data would be needed to determine whether V4 itself carries enough information for the observed behaviour.

**Normalisation mapping not specified.** The interaction with the divisive-normalisation framework of attention (Reynolds & Heeger 2009) is implicit: the temporally varying gain can in principle be absorbed into a time-varying $G_E$ or $G_S$ inside the normalisation model, but Ghose & Maunsell do not commit to a normalisation-based parameterisation, leaving the mapping to that subsequent theoretical framework as later work. As a corollary, the paper does not distinguish a "contrast-gain over time" account from a "response-gain over time" account; both are consistent with the data as reported.

**Generality.** Finally, the result is established for a single sensory area (V4) and a single task family (change detection with structured temporal statistics). Whether the same temporal-gain dynamic appears in earlier (V1, V2) or later (IT) areas, and under qualitatively different task structures (visual search, free viewing), is not addressed here and remains an open empirical question that bears directly on which hierarchical level of an artificial system should host the time-varying gain.

**Mechanistic agnosticism.** The paper treats the V4 modulation as a single scalar (the gain on the firing rate) and does not separate it into a contrast-gain component, a response-gain component, an additive bias, or a feature-selective gain. Modern accounts may further decompose the signal, but this paper's contribution is at the coarser level of "the gain exists, and it is time-varying" rather than at the level of "the gain has this specific mechanistic form."

## 7. Connection to our work

The Recurrent ViT (`2502.10955`) commits architecturally to the position that attention is a *function of a recurrent memory state* $H_t$, and therefore is intrinsically time-varying. The published paper reports a single-layer, single-feedback-source instance (§6.7) in which the attention map at each recurrent step is conditioned on $H_{t-1}$, with the three integration variants — tokens, additive, multiplicative — all sharing this dependency on a recurrent state. The attention-map visualisations in the user's *Classifier* note on Food-101 show maps that focus, defocus, and reactivate across recurrent passes — i.e., a Ghose-Maunsell-like time course produced by the architecture's own dynamics rather than imposed by the task. This paper is therefore a direct primate-level prediction of what the Recurrent ViT does: the gain field at a sensory-feature level is a non-trivial function of within-trial time, learned to align with the temporal structure of behaviourally relevant events. The empirical existence of such a signal in V4 is also a sanity check that the recurrent-ViT attention dynamics are biologically plausible rather than an artefact of overparameterised softmax-attention.

PRISM v1's FiLM modulation $P_t = \gamma_t \odot V_t + \beta_t$ (`THESIS.md` §2.4) is built around a memory state $M_t$ whose update is gated by prediction error. The gain $\gamma_t$ is therefore time-varying by construction, and the recurrent update rule fixes the temporal profile of $\gamma_t$ in response to the input sequence — exactly the role that the time-varying gain plays in V4 in this paper. PRISM's temporal saliency-gating, in which $\gamma_t$ rises and falls as the memory state predicts upcoming task-relevant moments, is the architectural analog of the Ghose-Maunsell finding: an internal model of when something behaviourally relevant will appear modulates a per-location gain field on the sensory features. PRISM v2's slow / fast memory partition (`PRISM_V2_PROPOSAL.md` §3.3) generalises this to two timescales, predicting (if Ghose & Maunsell's framework is right) that *V4-level* gain should be slaved to a fast memory while higher-level featural gain should be slaved to a slower one.

The paper also supports the Feedback Transformer primitive (`threads/the_user_architectural_program.md` §1). The Feedback Transformer integrates a recurrent state $C_i$ into the Q/K/V of self-attention via element-wise broadcasting, and Ghose-Maunsell-style temporal gain is precisely what such broadcasting produces when $C_i$ carries an expectation-of-event-time signal: the attention map's gain field becomes a function of within-trial time without any explicit timing input. The user's commitment that the Feedback Transformer should be the substrate of attention rather than a vanilla self-attention block over a static input is partially licensed by results like this one — static-image self-attention cannot, by construction, reproduce the temporal dynamics that Ghose & Maunsell document in V4. Only a *recurrent* attention mechanism, in which the gain on each sensory feature is conditioned on a recurrent state that itself encodes the temporal statistics of the task, can match the V4 data.

Relative to Reynolds & Heeger 2009, which provides the *what* of attentional modulation (graded, normalisation-based gain), Ghose & Maunsell provide the *when*: the gain has a non-trivial time course tied to the subject's temporal model of the task. PRISM's FiLM stack therefore must implement both: a per-location, per-channel multiplicative gain (Reynolds-Heeger) whose magnitude is itself a learned function of time (Ghose-Maunsell), with both functions implemented by the same recurrent memory state. The Recurrent ViT's softmax-attention map plays the symmetric role: the attention weights are spatially graded (Reynolds-Heeger compatible) and time-varying (Ghose-Maunsell compatible) by virtue of being recomputed from a recurrent $H_t$ at each pass.

This paper also bears on the user's central commitment that attention is intrinsically *recurrent* rather than feedforward. Static feedforward self-attention, evaluated once on an image, cannot have a "time course"; the only time it has is its single forward pass. To reproduce the Ghose-Maunsell phenomenon, an architecture must either (a) be unrolled across recurrent steps with a state that integrates task-temporal statistics, as the Recurrent ViT does, or (b) be applied to an explicit time-stamped sequence with a memory that propagates expectation across steps, as PRISM does on video. Either route requires recurrence, and the user's program's commitment to recurrent attention across both architectures is therefore directly supported. A purely feedforward attention module — even with sophisticated multi-head structure — is empirically inadequate as a model of V4-level attention under task-timing manipulations of the kind reported here.

**Hypothesis for the manuscript.** If the manuscript is to argue that the Recurrent ViT is a primate-grade model of attention, the time course of attention weights across recurrent passes — measured on a task with structured temporal statistics — should mirror the V4 modulation profile reported here. The user's *Classifier* note on Food-101 already qualitatively shows attention maps that "focus, defocus, and reactivate"; quantifying this against a Ghose-Maunsell-style probability schedule would convert the qualitative match into a falsifiable prediction. Conversely, if PRISM is to be presented as the more biologically faithful architecture, the temporal profile of $\gamma_t$ should track an analogous schedule when PRISM is trained on a change-detection sequence with structured event timing.

**Connection to the multi-compartmental memory stack.** In the user's 3-layer hierarchical design (`threads/the_user_architectural_program.md` §3), layer 1 is paired with V1-level features and layer 2 with V2/V4-level features. Ghose-Maunsell's V4 finding therefore localises the time-varying gain to layer 2 of the user's stack. A layered prediction follows: in the user's architecture, the GridCell RNN state $C_2$ should show within-trial temporal dynamics matched to event-probability schedules, while $C_1$ (V1-level) need not. This is a concrete empirical handle for the user's program: a layer-wise dissociation predicted by combining Ghose-Maunsell with the user's hierarchical-memory hypothesis.

## 8. Citations to follow

- `sani2017_temporal_v4_gain` — direct follow-up characterising the temporal evolution of V4 gain across trial phases; refines Ghose-Maunsell with denser temporal sampling.
- `nobre_vanede2018_anticipated_moments` — human-level review of temporal-expectation effects on perception and neural responses; cross-species generalisation.
- `reynolds_heeger2009_normalization` — the normalisation-model substrate into which the Ghose-Maunsell temporal gain naturally embeds.
- `kietzmann2019_recurrence_required` — argues recurrence is necessary for primate-like visual dynamics; Ghose-Maunsell is a key empirical anchor for that claim.
- `mante2013_context_dependent_pfc` — PFC source of context-dependent modulatory signals that could drive the V4 gain profile documented here.
- `bisley_goldberg2010_priority_map` — candidate generator of the temporal-expectation signal in parietal cortex; not yet in seed.
- `janssen_shadlen2005_hazard_lip` — LIP encoding of the hazard function of upcoming events; the most plausible upstream source of the V4 time course.
- `nobre2007_temporal_expectation` — psychophysical foundations of temporal-expectation effects on attention.
- `desimone_duncan1995_biased_competition` — classical biased-competition account; Ghose-Maunsell adds the temporal dimension absent from that framework.
- `moran_desimone1985_selective_attention_v4` — the original attentional-modulation-in-V4 result that Ghose-Maunsell builds on; documents the static gain that this paper recasts as dynamic.
- `reynolds_chelazzi2004_attentional_modulation_review` — review of V4 attentional modulation including the static-gain results; provides the baseline that Ghose-Maunsell complicates.
- `engel2001_dynamic_predictions` — earlier proposal that top-down signals are dynamic predictions; theoretical anchor for the time-varying gain.
- `treue_martinez_trujillo1999_feature_attention` — feature-similarity gain in MT; the spatial-feature counterpart to the temporal gain reported here.
