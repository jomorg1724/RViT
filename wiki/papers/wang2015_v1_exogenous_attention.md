---
id: wang2015_v1_exogenous_attention
title: "Modulation of Neuronal Responses by Exogenous Attention in Macaque Primary Visual Cortex"
authors:
  - "Wang, Feng"
  - "Chen, Minggui"
  - "Yan, Yin"
  - "Zhaoping, Li"
  - "Li, Wu"
year: 2015
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.0527-15.2015"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.0527-15.2015"
tags:
  - primate-neurophysiology
  - early-visual-cortex
  - visual-attention
  - posner-cuing
concepts:
  - gain-modulation
  - top-down-feedback
  - attentional-spotlight
  - cueing-effect
related:
  - mcadams_maunsell1999_v4_tuning
  - reynolds_heeger2009_normalization
  - cameron2002_covert_attention_contrast
  - sharma2015_attention_temporal_v1
  - treue_martinez_trujillo1999_feature_attention
  - desimone_duncan1995_biased_competition
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_61
status: full
depth: full
last_updated: "2026-05-16"
---

# Modulation of Neuronal Responses by Exogenous Attention in Macaque Primary Visual Cortex

## 1. Abstract

Wang, Chen, Yan, Zhaoping, and Li used chronically implanted microelectrode arrays to record from awake macaque V1 while exogenous (involuntary, stimulus-driven) attention was manipulated by a bright annular cue presented either surrounding the receptive field of the recorded population or in the opposite hemifield. After variable cue-to-probe stimulus-onset asynchronies (SOAs), an oriented grating probe was presented at the recorded location. Behavior was assessed in both a passive fixation task and a reaction-time detection task. Exogenous attention produced a *transient* increase in V1 neuronal response, peaking 40–100 ms after probe onset and present only at short SOAs (under ~240 ms), with the time course matching the classical psychophysical signature of exogenous orienting. The facilitation habituated with repeated identical cues but was restored by novel cues. Simultaneously cueing both locations abolished the effect. The behavioral cueing effect on reaction time tracked the V1 neural modulation in both magnitude and SOA dependence. The authors conclude that involuntary attention modulates the earliest stage of cortical visual processing on a fast, automatic, and saliency-driven timescale that is dissociable from endogenous (voluntary) attentional gain.

## 2. Why this matters for us

Wang et al. 2015 is the definitive single-unit evidence that *exogenous* attention — the fast, stimulus-driven, reflexive form — modulates V1 firing rates in primate, with a characteristic 40–100 ms onset and a short-SOA-only time course. For the user's program this paper does work that McAdams & Maunsell 1999 does not: it shows that V1 gain modulation can be driven without any voluntary top-down attentional set, on the timescale of a single feedforward sweep plus one cortical feedback iteration. This is the cellular-level analog of the very first recurrent pass of a Recurrent ViT — saliency-induced, automatic, fast, and operating directly on V1-level features — and it constrains how short and how strong the *first* recurrent step in the user's architecture ought to be. It is the empirical reference point for treating the bottom-up-only initial pass and the first feedback-augmented pass as functionally distinct, rather than as identical instances of the same recurrent step.

## 3. Key claims

1. **Exogenous attention modulates V1 firing rate in awake macaque.** A bright peripheral cue presented before the probe stimulus transiently increases V1 response to the probe when the cue is co-localized with the receptive field.
2. **The modulation is fast — peaks 40–100 ms post probe onset.** The effect is on the *initial* component of the V1 response, not on a late top-down-amplified component.
3. **The modulation is short-SOA-only.** Facilitation is present at cue-probe SOAs below ~240 ms and absent at long SOAs, matching the classical exogenous-orienting time course (Posner 1980; Nakayama & Mackeben 1989).
4. **The effect habituates with cue repetition.** Repeated identical cues progressively lose their facilitatory effect, but a novel cue restores it — a signature of automatic, saliency-driven (not voluntary) capture.
5. **Dual cueing abolishes the effect.** Presenting cues at both the receptive-field location and the opposite hemifield eliminates the facilitation, consistent with a winner-take-all competitive selection rather than a distributed enhancement.
6. **Behavior tracks physiology.** Reaction-time cueing benefits show the same SOA profile as the V1 neural facilitation, establishing a direct behavioral correlate of the V1 modulation.
7. **Exogenous attention dissociates from endogenous attention.** The fast onset, short-SOA-only profile, habituation, and dual-cue cancellation distinguish this modulation from the slower, sustained, voluntary modulations documented by McAdams & Maunsell, Treue & Martínez Trujillo, and others.

## 4. Methods

**Subjects and recordings.** Awake macaques with chronically implanted multi-electrode arrays in V1. Receptive fields were mapped on each channel; probe stimulus locations and the array channels analyzed were chosen so that the probe fell inside the RF of the recorded population. The use of chronic multi-electrode arrays — rather than acute single-electrode recordings — gives stable cross-session sampling of the same V1 neurons, which is essential for the cue-habituation analysis where the same cells must be tracked across many cue repetitions.

**Stimuli and cueing.** A bright annular cue appeared either at the recorded population's receptive-field location (*valid* trial) or at the mirrored location in the opposite hemifield (*invalid* trial). After a variable SOA the oriented-grating probe stimulus appeared inside the RF. Critical SOAs spanned roughly 40–500 ms, covering the classical exogenous-orienting window (Posner 1980; Nakayama & Mackeben 1989). A dual-cue condition presented cues at both the RF location and the mirrored location simultaneously, dissociating attentional selection from generalized arousal.

**Tasks.** Two tasks dissociated automatic capture from task-driven effects: (a) a passive fixation task in which the monkey only had to hold gaze, with no behavioral report tied to the cue, isolating the *involuntary* component of the modulation; (b) a reaction-time detection task in which the monkey reported probe onset, allowing the behavioral cueing benefit to be measured and correlated with the V1 neural facilitation in the same animal under near-identical stimulus conditions.

**Analyses.** Probe-evoked firing rates were computed in narrow time windows (notably the 40–100 ms post-probe window) and compared between valid and invalid conditions across SOAs. Habituation analyses tracked the modulation across blocks of repeated cues, with planned introductions of novel cues (varied in feature such as color or shape) to test recovery. Dual-cue trials tested whether facilitation summed, saturated, or cancelled. The narrow analysis window is critical: classical endogenous-attention paradigms average over long sustained windows, which would smear out a 40–100 ms transient. By contrast, this paper's temporally precise analysis is what makes the exogenous-vs-endogenous dissociation visible at the single-unit level.

## 5. Results

- **Magnitude and time course of V1 facilitation.** Valid-cued V1 responses exceeded invalid-cued responses transiently within the 40–100 ms post-probe window when SOA was below ~240 ms. The effect is on the initial response component, not on a late sustained phase.
- **SOA dependence.** Facilitation was strongest at short SOAs and decayed to baseline by ~240–300 ms, reproducing in V1 the classical psychophysical exogenous-cueing time course.
- **Habituation.** Repeated presentations of the same cue led to progressive decay of the facilitation. Introducing a novel cue (different feature) restored the effect — diagnostic of a saliency- or novelty-based capture mechanism rather than a learned top-down set.
- **Dual-cue cancellation.** When both potential target locations were cued simultaneously, the facilitation disappeared. The mechanism is therefore *selective* between locations, not a generalized arousal-driven gain.
- **Behavior–physiology match.** Reaction-time benefits on valid trials tracked the V1 facilitation in SOA dependence and in cue-novelty sensitivity, supporting a causal interpretation that V1 modulation is part of the chain producing the behavioral cueing effect.
- **Dissociation from endogenous attention.** Voluntary, sustained attentional effects (as in McAdams & Maunsell) have slower onset, persist over long SOAs, and do not habituate to repeated cues; the present effect has the opposite signature on each of those three axes (onset latency, SOA persistence, habituation).
- **Comparison to the V4 endogenous baseline.** The V1 exogenous facilitation magnitude is broadly comparable to the ~8% V1 endogenous gain reported by McAdams & Maunsell — both are in the modest-modulation regime relative to V4 endogenous effects (~26%) — but its time course is sharply transient rather than sustained, supporting two functionally distinct V1 attentional mechanisms rather than a single graded effect.
- **Novelty as the relevant variable.** Whether a cue facilitates or not depends not on its absolute properties but on whether it differs from recent cues. This is the key population-level result and the diagnostic feature that distinguishes saliency-driven capture from a learned top-down set.
- **Selectivity rather than gain.** The dual-cue cancellation result implies that the V1 modulation is fundamentally about *selecting one location over another*, not about raising V1 gain at any salient location independently. Two equally salient cues do not produce twice the V1 facilitation — they produce none, because the selection mechanism has no basis for choosing.

## 6. Critique / limitations

The study cannot fully disambiguate a *bottom-up sensory* contribution to the cue-probe interaction (e.g., forward masking, contrast adaptation, response normalization driven by the salient cue itself) from a *top-down or recurrent* attentional gain on V1. The dual-cue cancellation and the novelty-restoration argue against a purely sensory account, but a normalization-style explanation in which the cue restructures the local contrast-response landscape remains partially viable (see Reynolds & Heeger 2009).

The 40–100 ms window is consistent with the earliest V1 response, but it is also consistent with a fast feedback loop through extrastriate areas (V2, V4) returning to V1 within tens of milliseconds. The paper does not localize the *source* of the modulation; the V1 effect could be intrinsic, fed back from V2/V4, or fed back from pulvinar/SC. Disambiguating sources requires causal perturbation (lamina-specific recording, optogenetics, cortico-thalamic inactivation), which this paper does not provide.

The habituation analysis relies on across-block comparison and may be confounded with task adaptation, motivational drift, or electrode-stability effects over a recording session. The novelty-restoration result mitigates but does not eliminate this concern.

The effect size, although robust at the population level, is moderate per channel; single-neuron variability is high. The paper does not characterize subpopulations of V1 cells that might be differentially susceptible (e.g., layer 4C versus supragranular, simple versus complex, magnocellular- versus parvocellular-dominated columns).

The cue is a high-luminance annulus — an unusually salient stimulus. Whether the same V1 modulation arises for more naturalistic exogenous cues (a face, an abrupt object onset, a looming stimulus) is left open. The generalization from luminance saliency to feature saliency in V1 is not directly tested here.

Finally, the paper documents the *phenomenology* of exogenous V1 modulation but does not propose a mechanism. The relationship of the present effect to the multiplicative-gain framework of McAdams & Maunsell (V4, endogenous) and Treue & Martínez Trujillo (MT, feature-based) is not formally analyzed. Whether exogenous attention is a faster instance of the same gain mechanism or a structurally distinct operation is left open.

## 7. Connection to our work

This paper is the empirical anchor for the user's commitment that V1-level features can be modulated by attention *on a single feedback iteration's timescale*, automatically and without voluntary control. It bears on three specific design choices in the user's architectural program.

**The first recurrent pass of the Recurrent ViT is not redundant.** The published Recurrent ViT (2502.10955) repeats self-attention with feedback memory over $T$ passes. A common reviewer concern is whether the first pass with no useful memory state is wasted computation. Wang et al. show that in real V1, a saliency-driven modulation appears within 40–100 ms of probe onset — i.e., within roughly the first feedforward-plus-feedback cycle. The corresponding architectural prediction is that *even the second recurrent pass* (the first one that can carry information from the first pass) should produce a measurable, automatic, saliency-driven adjustment of the attention map, before any sustained voluntary attentional set develops. The user's Food-101 attention-map observation that "maps focus, defocus, and reactivate" over recurrent passes is consistent with this: an exogenous-style salience grab on the first informative pass, followed by slower endogenous-style settling.

**Feedback Transformer feedback sources are not all the same.** The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) admits an arbitrary number of recurrent feedback sources from parallel and hierarchical memory states. Wang et al.'s dissociation between exogenous and endogenous V1 modulation suggests that these sources should be *functionally distinguished*: a fast, transient, automatic feedback source (a saliency map, a pulvinar-style fast pulse) versus a slow, sustained, task-driven feedback source (a working-memory state, an RL-hub policy state). The user's multi-hub multi-objective system (`the_user_architectural_program.md` §5) already commits to multiple parallel feedback sources; Wang et al. argue that one of them should have the *short-SOA, habituating, novelty-sensitive* profile of exogenous attention, not the sustained profile of working memory.

**Novelty habituation as a regularizer.** Wang et al.'s habituation-with-novelty-recovery is a striking computational signature. In the user's competition-emergent predictive-coding account ([competition-emergent-predictive-coding](research_db/concepts/competition-emergent-predictive-coding.md)), the salience-driven hub competes for attention bandwidth against the working-memory and RL hubs. If the salience hub's contribution did not habituate, it would always win at salient locations, and other hubs would never get bandwidth. The habituation Wang et al. document is a biological implementation of the necessary load-balancing: salience grabs attention transiently, then yields. PRISM v2's hierarchical FiLM and the user's gridcell-rnn gating should plausibly include an analogous adaptation-to-repetition mechanism on the fastest feedback channel, so that the salience source self-attenuates after consecutive identical inputs.

**V1 is the right level for the bottom of the hierarchy.** The user's multi-compartmental memory's Layer 1 ([multi-compartmental-memory](research_db/concepts/multi-compartmental-memory.md)) is paired with V1-level visual features. Wang et al. show that V1, not just V4/IT, is genuinely a site of attentional modulation in primate — both endogenous (per McAdams & Maunsell's smaller V1 effect) and exogenous (this paper). This warrants placing recurrent feedback on the *first* layer of the user's stack, not only on deeper layers, contrary to architectures that treat V1 as a fixed feedforward stem.

**Dual-cue cancellation favors competitive normalization at V1.** Wang et al.'s finding that simultaneous cueing at two locations abolishes the facilitation is the V1-level analog of biased competition (Desimone & Duncan 1995): two equally salient candidates cancel rather than additively summing. This is precisely the competitive-selection-via-softmax behavior of standard transformer attention. The user's Feedback Transformer inherits this property by construction (softmax over keys forces selection); Wang et al. provide single-unit evidence that real V1 implements the same competitive selection on exogenous cues. The Recurrent ViT's softmax attention is not just a deep-learning convention but the biologically correct operator for the kind of selection V1 itself performs.

**Bridge to the connection between exogenous capture and contrast.** Cameron, Tai & Carrasco 2002 (`cameron2002_covert_attention_contrast`) establishes the behavioral counterpart of this paper in humans: exogenous covert attention enhances contrast sensitivity with a similar SOA profile. Together with Reynolds & Heeger 2009's normalization model and Sharma et al. 2015's temporal V1 attention study, Wang et al. complete a four-paper cluster that anchors the user's V1-level attention modeling: behavior (Cameron), V1 single units endogenous (McAdams & Maunsell), V1 single units exogenous (Wang), and unifying mechanism (Reynolds & Heeger).

**Implication for the PRISM v1/v2 prediction-error pathway.** PRISM v1's prediction-error map is computed from the difference between a top-down prediction and the V1-level features (`THESIS.md` §2). The Wang et al. result implies that the V1 features themselves are already attention-modulated on a fast, automatic, novelty-driven timescale before any top-down prediction is computed. A PRISM-style prediction-error pathway should therefore read from a V1 representation that already carries an exogenous gain field — and conversely, the *first* prediction error the network sees should reflect cues' saliency-driven capture, not just the higher-level template mismatch. This argues for either (a) a saliency-precomputation stage between sensory input and the prediction-error subtraction in PRISM v2, or (b) treating PRISM v2's fastest memory state as carrying the saliency-modulated V1 representation rather than the raw V1 representation.

**Calibration target.** Wang et al.'s 40–100 ms window and short-SOA-only profile give a concrete *temporal* benchmark for any model claiming V1-level biological plausibility. A Recurrent ViT that produces attention-map changes on the first informative pass — but whose modulation does not subsequently decay as identical input is repeated — fails to reproduce the exogenous-attention habituation signature. Adding a simple exponential decay on the fastest feedback channel, with reset on input change, would be the minimal architectural change required to reproduce Wang et al.'s population-level result.

## 8. Citations to follow

- `posner1980_orienting_attention` — the foundational psychophysics of exogenous vs endogenous cueing whose neural correlate this paper supplies. Not yet in seed; high priority.
- `nakayama_mackeben1989_transient_sustained` — the classic dissociation of fast transient (exogenous) from slow sustained (endogenous) attention that defines the SOA windows used here. Not yet in seed.
- `cameron2002_covert_attention_contrast` — human-behavioral counterpart of this paper. In seed.
- `reynolds_heeger2009_normalization` — normalization framework that could subsume both the multiplicative-gain and the cue-driven V1 modulation. In seed, full depth.
- `mcadams_maunsell1999_v4_tuning` — the endogenous-attention V1/V4 counterpart against which this paper's exogenous-attention V1 effect should be contrasted. In seed, full depth.
- `sharma2015_attention_temporal_v1` — companion V1 temporal-attention study from the same era. In seed.
- `treue_martinez_trujillo1999_feature_attention` — feature-based gain modulation; complements the present location-based exogenous result. In seed, full depth.
- `desimone_duncan1995_biased_competition` — biased-competition framework whose dual-cue prediction this paper confirms at the V1 level. In seed, full depth.
- `zhaoping2002_v1_saliency` — Li Zhaoping's V1 saliency map theory, of which this paper is a partial empirical test. Co-authored by Zhaoping. Not yet in seed; high priority.
- `bisley_goldberg2010_attention_lip` — LIP priority-map account that posits the source signal modulating V1 in studies like this. Not yet in seed.
