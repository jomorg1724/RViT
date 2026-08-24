---
id: thompson1996_fef_stages
title: "Perceptual and motor processing stages identified in the activity of macaque frontal eye field neurons during visual search"
authors:
  - "Thompson, Kirk G."
  - "Hanes, Doug P."
  - "Bichot, Narcisse P."
  - "Schall, Jeffrey D."
year: 1996
venue: "Journal of Neurophysiology"
doi: "10.1152/jn.1996.76.6.4040"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/8985899/"
tags:
  - primate-neurophysiology
  - prefrontal-cortex
  - visual-attention
  - decision-making
  - reaction-time
concepts:
  - signal-detection-theory
  - priority-map
  - attentional-template
  - chronometric-function
  - top-down-feedback
related:
  - moore_armstrong2003_fef_microstim
  - bisley_goldberg2010_parietal_priority
  - clark2015_prefrontal_attention
  - bollimunta2018_fef_sc_covert
  - krauzlis2013_sc_attention
  - gold_shadlen2007_decision_making
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_62
status: full
depth: full
last_updated: "2026-05-15"
---

# Perceptual and motor processing stages identified in the activity of macaque frontal eye field neurons during visual search

## 1. Abstract

The latency between the appearance of a popout search display and the eye movement to the oddball target of the display varies from trial to trial in both humans and monkeys. The source of the delay and variability of reaction time is unknown but has been attributed to as yet poorly defined decision processes. Neural activity was recorded in the frontal eye field (FEF), an area regarded as playing a central role in producing purposeful eye movements, of monkeys (Macaca mulatta) performing a popout visual search task. Eighty-four neurons with visually evoked activity were analyzed; twelve had a phasic response associated with stimulus presentation, while the remainder had more tonic responses that persisted through the saccade. Visual response latencies of FEF neurons were determined using a Poisson spike train analysis: the mean visual latency was 67 ms (minimum = 35 ms, maximum = 138 ms), and latencies did not differ significantly between target-alone, target-with-distractors, and distractor conditions. The initial visual activation of FEF neurons does not discriminate the target from the distractors of a popout array, but the activity evolves to a state that discriminates whether the target is within the receptive field. Using a signal-detection-theory analysis, the authors determined when the activity of single FEF neurons reliably indicates whether the target or distractors are present within their response fields; this time of target discrimination partitions the reaction time into a perceptual stage and a motor stage. Target discrimination occurred most often between 120 and 150 ms after stimulus presentation. After separating trials into short, medium, and long saccade latency groups, saccade latency was not correlated with the duration of the perceptual stage but was correlated with the duration of the motor stage. The variability observed in saccade latencies during simple visual search is therefore largely due to postperceptual motor processing following target discrimination; signatures of both perceptual and postperceptual processing are evident in FEF, and procrastination in the output stage may prevent stereotypical behavior that would be maladaptive in a changing environment.

## 2. Why this matters for us

Thompson et al. 1996 is the foundational empirical demonstration that a single brain region — FEF — carries two separable signals: an early *perceptual* signal that resolves target identity (a priority map), and a later *motor* signal that produces the saccade. Both the Recurrent ViT (2502.10955) and the user's broader architectural program lean on this decomposition: the published ViT predicts per-quadrant change-detection responses by computing a saliency-like attention map at each time step (`§4.1`, `§6.6`) and then mapping it to an action through a softmax over the same tokens, exactly paralleling Thompson's perceptual-then-motor partition. Cited as reference 62 in 2502.10955, this paper anchors the claim that FEF activity *is* the priority map that downstream motor circuits then read.

## 3. Key claims

1. Visual-response latencies of FEF neurons (mean 67 ms) do not differ between target-only, target-with-distractors, and distractor-only conditions — the initial visual transient is stimulus-driven, not target-selective.
2. FEF activity evolves over time to discriminate target from distractors within the receptive field; the discriminative signal emerges between 120 and 150 ms post-stimulus.
3. Signal-detection analysis on single-cell spike trains identifies a "target-discrimination time" that cleanly partitions reaction time into a perceptual stage (stimulus onset → discrimination) and a motor stage (discrimination → saccade).
4. Across trial-latency groups (short / medium / long saccades), the perceptual stage duration is constant; only the motor stage duration covaries with RT.
5. Therefore RT variability on this simple search task is not perceptual-discrimination variability but post-perceptual motor variability — a "procrastination" in the output stage rather than uncertainty in the priority map.
6. FEF therefore implements both perceptual selection (priority map) and motor commitment (saccade trigger), and these are temporally separable within the same population.

## 4. Methods

Two macaque monkeys performed a popout visual search task: on each trial a fixation point was followed by an array of one oddball target (defined by a single feature: color or shape) embedded among homogeneous distractors. The monkey was rewarded for a single saccade to the target. Single-unit recordings were made in FEF; receptive fields were mapped, and 84 visually responsive neurons were analyzed. Twelve showed phasic visual transients only; 72 had more tonic, visuomovement-like responses.

For each cell, three conditions were compared: target alone in the RF, target in the RF with distractors elsewhere, and distractor in the RF with the target elsewhere. Visual-response onset latency was estimated using a Poisson spike-train analysis that detects the first significant deviation from baseline.

Target-discrimination time was estimated by treating, at each post-stimulus time bin, the firing-rate distributions on "target-in-RF" vs. "distractor-in-RF" trials as the two distributions of a signal-detection problem and computing $d'(t)$ or equivalently the area under the ROC curve. The discrimination time is the first bin at which the ROC area exceeds a fixed criterion (a $d'$ threshold) and remains above it. Reaction time was then partitioned: perceptual stage = stimulus onset to discrimination time; motor stage = discrimination time to saccade. Trials were sorted into short / medium / long RT terciles, and the two stage durations were regressed against RT.

## 5. Results

- Mean FEF visual latency: 67 ms (range 35–138 ms). Latencies to target alone vs target+distractors vs distractors alone were statistically indistinguishable.
- Initial visual response is non-selective: the first ~50–80 ms of FEF activity does not encode target identity.
- Target discrimination time, by signal-detection: peak of the distribution between 120 and 150 ms after stimulus onset.
- Mean saccade latency in this task: on the order of 200–300 ms.
- Across short / medium / long RT terciles: perceptual stage (stimulus → discrimination) remains roughly constant; motor stage (discrimination → saccade) accounts for essentially all of the RT variance.
- Both phasic-only and visuomovement neurons show the perceptual-discrimination signal; the visuomovement neurons additionally show the perimovement motor signal.

The quantitative takeaway is that on this task, FEF "knows" the answer ~50–150 ms before it executes the saccade, and the bulk of trial-to-trial RT variance comes from variability in that post-knowledge interval.

## 6. Critique / limitations

The result is specific to popout search with a salient, easily discriminable target. With harder conjunction search, more difficult discriminations, or distractor heterogeneity, the perceptual stage lengthens and may carry more of the RT variance; Bichot & Schall (1999, 2002) and others later demonstrate exactly this. Generalizing "RT variance is motor" beyond easy popout is therefore unwarranted.

The signal-detection criterion for "discrimination time" is somewhat arbitrary — different thresholds shift the absolute discrimination time, though the rank-ordering across conditions is robust. Sato, Watanabe & Thompson (2001) refined the criterion using ROC area.

FEF is not the only locus of priority-map computation: LIP (Bisley & Goldberg 2010), SC (Krauzlis 2013, McPeek & Keller 2002), and pulvinar all carry similar discrimination signals. Thompson et al. do not establish FEF as causally necessary for target selection — that requires inactivation studies (Wardak, Ibos, Duhamel & Olivier 2006; Schiller & Tehovnik 2003).

The "procrastination in the output stage" interpretation is suggestive rather than mechanistic. Why the motor stage varies so much is not explained; subsequent drift-diffusion models (Hanes & Schall 1996 — by the same group — and Gold & Shadlen 2007) provide a more principled account in which the post-discrimination period is itself an accumulation-to-bound process with stochastic accumulation rate.

The paper does not distinguish bottom-up popout salience from top-down task-set; in popout the two are confounded. Bichot & Schall (1999) later separate them and show that FEF carries both bottom-up and top-down components.

## 7. Connection to our work

This paper is one of the load-bearing empirical anchors for the architectural program along three axes.

**Perceptual-vs-motor decomposition in the Recurrent ViT.** The Recurrent ViT (2502.10955) instantiates a softmax-attention map $\alpha^{(t)} \in \Delta^4$ over the four quadrants at each time step, followed by an action head producing a response distribution (`§3.2`, Figure 3). The attention map plays the role of Thompson's perceptual discrimination signal — "which quadrant carries the target?" — while the action head plays the role of the motor signal — "do I commit to a response now?" The empirical match between model attention and monkey behavior (Figure 5, `§4.3`) is therefore directly comparable to Thompson's two-stage decomposition: the model reaches a confident attention map well before it commits to an action, mirroring the 120–150 ms perceptual stage that precedes saccade initiation by a further 80–150 ms.

**FEF as priority-map source for top-down modulation.** Thompson's discrimination signal is what Moore & Armstrong (2003; in this database) later show is transmitted to V4 as a gain modulation. The pair of papers establishes (a) that FEF computes a target-vs-distractor map and (b) that this map causally biases visual cortex. PRISM's $S_t$ saliency map (THESIS.md §2.4) and the Recurrent ViT's $\alpha^{(t)}$ are both computational analogs of this priority map; the FiLM modulation from $M_{t-1}$ to $V_t$ in PRISM, and the memory-feedback into self-attention in the ViT (`§6.7`), are both computational analogs of the FEF→V4 transmission. PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) further generalizes this to a multi-level priority cascade.

**Multi-hub system in the user's broader program.** In the user's architectural program (`threads/the_user_architectural_program.md` §1, §5), the Feedback Transformer accepts hub-specific feedback at the Q/K/V projection level. Thompson's data shows that a *single* neural population (FEF) carries both the perceptual coalition's vote (priority map) and the motor coalition's commitment (saccade trigger), and that these are temporally interleaved on the same neurons. This is precisely the prediction of the multi-hub / Feedback-Transformer architecture: an RL/motor hub and a perceptual hub both feed back into the same self-attention substrate, producing time-varying mixtures of perceptual and motor information at any given recording site. The "procrastination" interpretation — that the brain holds off committing in order to remain adaptive — is also consonant with the competition-emergent-predictive-coding thesis: a hub that commits too early loses access to subsequent updates from competing hubs and is therefore selected against.

**Feedback Transformer interpretation of the discrimination dynamics.** Thompson's data shows that FEF visual responses *evolve* from non-selective at 67 ms to target-selective at 120–150 ms; this is roughly 50–80 ms of within-area recurrent or feedback dynamics. The Feedback Transformer's defining commitment — that each cortical processing step integrates top-down and lateral feedback in a single self-attention operation — predicts exactly this kind of late-developing selectivity, with the early transient reflecting feedforward drive and the late selective signal reflecting integration of feedback from upstream hubs (parietal priority, IT object identity, RL value).

**Concrete Recurrent ViT analogue to test.** A direct prediction of the connection is that the recurrent ViT's per-step attention map should show low target/non-target discrimination at the earliest recurrent steps and rising discrimination at later steps, with the absolute commitment time (action head argmax) lagging the discrimination time. This is the model-level analog of Thompson's two-stage finding and is readily measurable from `attention_logits` and `action_logits` over recurrent passes in the existing model.

## 8. Citations to follow

- `hanes_schall1996_neural_control_saccade_initiation` — sister paper from the same group; the drift-diffusion/accumulator account of saccade initiation in FEF. Pairs with Thompson 1996 as the motor-stage mechanism.
- `bichot_schall1999_topdown_fef` — separates top-down task-set from bottom-up popout salience in FEF; refines the priority-map interpretation.
- `sato_watanabe_thompson2001_search_efficiency` — extends the ROC-discrimination analysis to harder search; perceptual stage *does* scale with task difficulty.
- `schall2001_brain_decision` — review by senior author tying FEF data to the broader perceptual-decision framework.
- `thompson_bichot2005_visual_salience_fef` — full review of the priority-map interpretation of FEF.
- `mcpeek_keller2002_sc_target_selection` — analogous target-selection signal in superior colliculus; needed to assess FEF specificity.
- `wardak2006_fef_inactivation_search` — FEF inactivation degrades search performance, supplying the causal complement Thompson 1996 lacks.
- `gold_shadlen2007_decision_making` — review formalizing the discrimination-then-commit framework Thompson's data anchors.
