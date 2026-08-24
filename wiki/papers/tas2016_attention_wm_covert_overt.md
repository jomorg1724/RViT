---
id: tas2016_attention_wm_covert_overt
title: "The relationship between visual attention and visual working memory encoding: A dissociation between covert and overt orienting"
authors:
  - "Tas, A. Caglar"
  - "Luck, Steven J."
  - "Hollingworth, Andrew"
year: 2016
venue: "JEP: HPP"
doi: "10.1037/xhp0000212"
arxiv: ""
url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC4977214/"
tags:
  - visual-attention
  - working-memory
  - change-detection
  - psychophysics
concepts:
  - attentional-spotlight
  - working-memory-persistent-activity
  - feature-binding
related:
  - awh2006_attention_wm
  - hoffman2016_attention_eye_movements
  - vanede2019_gaze_internal_wm
  - gupta_sridharan2024_presaccadic_change
  - kiyonaga_egner2013_wm_internal_attention
  - olivers2011_wm_states_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_107
status: full
depth: full
last_updated: "2026-05-16"
---

# The relationship between visual attention and visual working memory encoding: A dissociation between covert and overt orienting

## 1. Abstract

There is substantial debate over whether visual working memory (VWM) and visual attention constitute a single system for the selection of task-relevant perceptual information or whether they are distinct systems that can be dissociated when their representational demands diverge. Tas, Luck and Hollingworth contrast two predictions: a single-system account predicts that any focal deployment of attention to a secondary object during a VWM retention interval should encode that object and overwrite or interfere with the stored items; a dissociable-systems account predicts that interference arises only when the attentional act itself entails *perceptual encoding* — paradigmatically a saccade, which obligatorily samples its target — and not when attention is merely covertly oriented. Across five experiments using a color change-detection paradigm with a task-irrelevant secondary object presented during the retention interval, the authors find that saccades to the secondary object produce substantial interference with VWM, whereas covert shifts of attention to the same object — verified to be focal by independent detection and discrimination probes — produce no measurable interference. The results support the dissociable-systems view: spatial attention and VWM encoding can be decoupled when the selective demands of the two systems diverge.

## 2. Why this matters for us

Tas, Luck & Hollingworth 2016 is the most direct empirical justification for treating *covert spatial attention* as the operative regime of the Recurrent ViT and PRISM.

The recurrent ViT (2502.10955) models change-detection without any saccadic sampling: there is no foveation step, no retinal magnification, and no overt gaze redirection — the attention map is entirely covert and parallel across patches.

Tas et al. show that this is the regime in which attention and VWM encoding are *decoupled*: a covertly attended distractor does not corrupt the VWM trace. This justifies one of the published architecture's key simplifications — namely that the recurrent memory state $H^{(t)}$ persists *across* the cue / blank / target sequence without being overwritten by every salient blob the attention map highlights along the way.

In contrast, an overt-attention regime (a glimpse-style RAM model) would force the network into an active-sampling discipline in which each fixation *commits* to encoding what it samples. The Tas et al. dissociation is therefore the cleanest empirical argument that the modelling decision of full-field-parallel versus glimpse-based attention is not just a computational convenience but a substantive cognitive-regime choice.

## 3. Key claims

1. **Saccades obligatorily encode their target into VWM.** When the secondary object during the retention interval became the goal of an executed saccade, change-detection accuracy dropped substantially, consistent with the saccade target being written into VWM and either overwriting or competing with the items being maintained.
2. **Covert attention to the secondary object does not encode it into VWM.** When the same secondary object was focally attended without an accompanying saccade, change-detection performance was statistically indistinguishable from a no-secondary-object baseline.
3. **The dissociation is not an artifact of weak covert attention.** Independent detection and discrimination probes (Exps. 4–5) confirmed that the covertly attended object was attended with high precision; the absence of interference cannot be explained by failure to attend.
4. **The dissociation is not an artifact of saccades to empty space.** Exp. 2 controlled for the motoric act of the saccade itself by including saccades to empty locations; interference scaled with whether the saccade had an object as target, ruling out a pure oculomotor explanation.
5. **Encoding precedes saccade completion.** Exp. 3 showed that the encoding effect is already present before the saccade lands, consistent with the pre-saccadic shift of attention being the encoding event.
6. **The single-system view of attention–WM identity is too strong.** The widely cited claim that "attention to X is encoding X into VWM" must be qualified: this holds for the overt-orienting case but not for the covert-orienting case.

## 4. Methods

A color change-detection paradigm with five experimental conditions:

- **Memory array.** A small set of colored squares (the to-be-remembered items) was presented briefly.
- **Retention interval.** During the retention period, a *secondary object* — explicitly task-irrelevant and not predictive of the test probe — was presented at a peripheral location.
- **Orientation manipulation.** Participants either (i) executed an *overt* saccade to the secondary object (Exps. 1–3) or (ii) attended it *covertly* without moving the eyes (Exps. 4–5).
- **Test.** A single test item probed memory for one of the original colors; participants reported same / different.
- **Controls.** Exp. 2 added a saccade-to-empty-space control. Exps. 4–5 added independent perceptual probes at the secondary-object location, requiring detection or discrimination, to verify the locus of covert attention.

The dependent variable was change-detection accuracy as a function of secondary-object presence × orienting mode. The critical comparison was the interaction: presence of a secondary object should hurt VWM only in the saccade conditions, not in the covert-attention conditions.

## 5. Results

- **Saccade block (Exp. 1).** Significant memory decrement when a secondary object was present versus absent: $F(1,19) = 9.1$, $p = .007$.
- **Fixation block (Exp. 1).** No reliable difference; $F < 1$; Bayes factor favored the null by $\approx 4.2\times$.
- **Omnibus covert conditions (Exps. 4–5).** Combined data again showed no reliable effect; $F < 1$; null favored by $\approx 7.7\times$.
- **Saccade-to-empty control (Exp. 2).** Interference scaled with the presence of an object at the saccade target, not with the saccade itself.
- **Pre-saccadic timing (Exp. 3).** Interference was present even when the test array probed VWM before the saccade had completed, locating the encoding event at the pre-saccadic attention shift.
- **Detection / discrimination probes (Exps. 4–5).** Performance on the covert-attention probe at the secondary-object location was high — covert attention *was* allocated — yet VWM was unaffected.

Together the pattern is a clean double dissociation: saccade-without-object spares VWM; covert-attention-to-object spares VWM; only the conjunction (saccade *to* object) interferes.

The effect sizes are large and the Bayes-factor evidence for the null in the covert conditions is non-trivial. The pattern replicates the earlier Hollingworth & Luck 2009 finding that saccade targets are obligatorily encoded into VWM, while extending it by showing that the obligatoriness is *specific to the saccadic regime* rather than being a general property of focal attention.

## 6. Critique / limitations

The dissociation rests on a *null result* for the covert-attention condition. Although the Bayes factors favor the null (4.2× and 7.7× in favor of no interference), a null result is intrinsically harder to interpret than a positive interference effect, and small interference effects below the experiment's detection threshold cannot be ruled out. The authors mitigate this with a within-subjects design and converging probes, but a high-precision continuous-report VWM measure (Bays & Husain 2008-style mixture modelling, decomposing precision and guess-rate) would have given a stronger upper bound on hidden interference and could have detected sub-item-loss precision degradation invisible in a same/different change-detection metric.

The paradigm tests *encoding into VWM* during the *retention* interval. It does not directly address the converse direction (whether contents of VWM bias attention) — that is the "memory-guided attention" branch covered by Soto, Heinke & Humphreys 2005 and Olivers, Peters, Houtkamp & Roelfsema 2011, both flagged in the awh2006_attention_wm entry. The dissociation Tas et al. demonstrate is therefore one-directional, and a full account of the attention–WM interface requires both directions.

The stimuli are simple colored squares with a single secondary object. The dissociation might weaken with naturalistic stimuli, multiple competing distractors, or feature-bound objects requiring full object-level binding for VWM encoding. Hollingworth's later work on memory-guided gaze control (Hollingworth & Luck 2009; Hollingworth et al. 2013) is consistent with this caveat: when the task explicitly requires binding the attended object to a behavioral plan, even covert attention may become a stronger encoding trigger.

The account does not commit to a mechanism that links saccade preparation specifically to VWM-encoding. Why does the *pre-saccadic shift of attention* obligatorily encode but the *purely covert shift of attention* not? Candidate mechanisms include corollary-discharge signals from oculomotor centers (FEF, superior colliculus) that gate hippocampal / parietal encoding circuits, or a representational requirement that saccade landing positions be specified in object-centered coordinates that demand object-level binding. Subsequent work — Hoffman 2016, Gupta & Sridharan 2024 on presaccadic change-detection — has attempted to decompose this with behavioral and modelling tools, but the mechanistic question remains open.

The paper predates the recent literature reframing WM as *internal attention* (Kiyonaga & Egner 2013; van Ede 2019; Panichello & Buschman 2021). In that frame, the dissociation Tas et al. document is between *external covert orienting* (which does not engage internal-attention reentrant pathways into WM) and *overt orienting* (whose presaccadic attention has stronger reentrant pathways via FEF / superior colliculus). The 2016 paper does not articulate this framing, but the empirical pattern is fully compatible with it and arguably provides the cleanest behavioral footprint of the underlying circuitry.

## 7. Connection to our work

This paper underwrites a key but usually-implicit modelling choice in the Recurrent ViT and PRISM lineage: **our models operate in the covert-attention regime.** Several consequences follow.

**The Recurrent ViT's attention is a covert spotlight.** The published model (2502.10955) processes the full 224×224 image at every timestep via patchwise self-attention; the attention map highlights regions but does not reposition the input. There is no foveation, no glimpse cropping, no log-polar retinotopy. By Tas et al.'s logic, this places the model squarely in the regime where attending an object *does not commit it to VWM* — and thus where the recurrent memory state $H^{(t)}$ is free to maintain the cue-defined target across distractor activations in the attention map. This is what makes single-state recurrence viable for cue / blank / target sequences: the attention map can briefly highlight a distractor between cue and target without that distractor being written into the WM substrate.

**Contrast with overt-attention / glimpse-model architectures.** RAM-style glimpse models (Mnih et al. 2014, recurrent-attention concept) and active-vision frameworks (Hoffman 2016, hoffman2016_attention_eye_movements) implement the overt-orienting regime — every glimpse is a foveation, every foveation obligatorily writes into the read-out state. Such models are computationally cheaper but structurally rule out the dissociation Tas et al. document. The Recurrent ViT's choice to use covert (parallel, full-field) attention rather than glimpse-based attention is, in this light, not merely an engineering convenience but a *substantive commitment* about which cognitive regime the model targets.

**Implications for the cue-condition mechanism.** The recurrent ViT's cue token (presented before the target image) sets up a memory state that biases the subsequent attention map. This is exactly the WM → attention direction Awh, Vogel & Oh 2006 describe (awh2006_attention_wm). Tas et al. give the converse-direction null: an attention-map activation during retention does *not* automatically reshape the memory state. The asymmetry — WM biases attention but covertly-deployed attention does not rewrite WM — is built into the architecture by giving $H^{(t)}$ a *gated* update (whether implicit in self-attention or explicit in PRISM's FiLM / Feedback-Transformer layers). The covert/overt dissociation is the cognitive-science precedent for this gating asymmetry.

**Implications for the user's broader program.** The Feedback Transformer (the_user_architectural_program §1) integrates feedback from many recurrent states into a single self-attention pass. If those feedback states represent VWM content, Tas et al. caution that the *integration* of a transient attention-map activation back into the WM state should not be obligatory: the architecture should permit attention to highlight a region without that region's content overwriting the corresponding memory compartment. This is naturally accommodated by the multi-compartmental memory design (the_user_architectural_program §3), in which each memory layer has its own learned gating over feedback inputs — including the option to reject feedback from the current attention activation. The covert-vs-overt dissociation is empirical justification that real cognition has exactly this gating.

**Connection to presaccadic-attention literature.** Tas et al.'s Exp. 3 result — encoding precedes saccade completion — locates the obligatory encoding at the *presaccadic shift*. Gupta & Sridharan 2024 (gupta_sridharan2024_presaccadic_change) directly probe this with change-detection paradigms in macaques, and van Ede 2019 (vanede2019_gaze_internal_wm) shows the analogous link in the reverse direction (gaze biases reflect internal WM access). Hoffman 2016 (hoffman2016_attention_eye_movements) is the synthesis review. The Tas et al. paper is the cleanest behavioral demonstration that the two regimes — covert and overt — produce different VWM consequences; the rest of the cluster supplies neural and computational mechanism.

**Position in the four-paper attention-WM cluster.** Within the database, four papers anchor the cognitive-science framing for the Recurrent ViT's covert-attention design:

1. `awh2006_attention_wm` — establishes that attention and WM are dissociable but multiplexed varieties of a shared substrate.
2. `tas2016_attention_wm_covert_overt` — *this paper* — refines the dissociation along the covert / overt axis, identifying the regime in which our model operates.
3. `hoffman2016_attention_eye_movements` — synthesis review on the attention–eye-movement coupling, providing the broader theoretical frame.
4. `gupta_sridharan2024_presaccadic_change` and `vanede2019_gaze_internal_wm` — neural and behavioral mechanism for the presaccadic encoding and the gaze–WM coupling respectively.

Together this cluster justifies the architectural choice to (a) use parallel rather than glimpse-based attention, (b) maintain a single recurrent memory state across the cue / blank / target sequence, and (c) interpret that state as a covert-attention WM template rather than as a gaze-trajectory buffer.

**Specific variant for future modelling.** If we wanted to test whether the Recurrent ViT genuinely behaves in the covert regime, the analog of Tas et al.'s manipulation would be: insert a salient task-irrelevant distractor during the retention interval (between cue and target) and test whether change-detection accuracy suffers. The dissociable-systems prediction — which our architecture instantiates — is that performance should be largely spared even when attention-map visualizations show the distractor briefly capturing the spotlight. A graded version of the test would parametrically vary distractor salience (Itti–Koch saliency, contrast, motion) and look for a step function rather than a smooth monotone in interference: a step at the salience threshold where the distractor "wins" the attention competition would suggest the gating is binary, whereas a smooth interference curve would indicate the memory state is leaky and the model is more strongly committed to the single-system regime than the architecture nominally implies. This is a tractable empirical follow-up that maps directly onto an existing behavioral paradigm.

## 8. Citations to follow

- `hollingworth_luck2009_gaze_vwm` — Hollingworth & Luck demonstration that saccade targets are obligatorily encoded; the empirical precursor cited heavily in Tas et al.'s motivation. Not yet in seed.
- `hollingworth2013_memory_gaze_control` — Hollingworth et al. on memory-guided gaze; the converse direction to Tas et al. Not yet in seed.
- `kiyonaga_egner2013_wm_internal_attention` — Kiyonaga & Egner, WM as internal attention; reframes Tas et al.'s dissociation in the modern WM-as-attention literature. In seed.
- `olivers2011_wm_states_attention` — Olivers et al., active vs accessory WM states and their differential coupling to attention. In seed.
- `soto2005_memory_guided_attention` — Soto, Heinke & Humphreys on WM-template-guided attentional capture; the canonical demonstration of the converse-direction effect. Not yet in seed.
- `bays_husain2008_dynamic_shifts` — Bays & Husain on continuous-report VWM, providing the high-precision measure that would strengthen the Tas et al. null. Not yet in seed.
- `mnih2014_ram_glimpse` — RAM-style glimpse model; the canonical overt-attention deep-learning architecture against which the Recurrent ViT's covert design contrasts. Not yet in seed.
- `posner1980_orienting_attention` — Posner's foundational covert-attention paradigm; defines the covert-attention regime that Tas et al. exploit. Not yet in seed.
- `deubel_schneider1996_saccade_attention` — Deubel & Schneider on the obligatory pre-saccadic attention shift; the perceptual analog of the encoding obligatoriness Tas et al. document. Not yet in seed.
