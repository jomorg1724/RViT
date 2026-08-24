---
id: hickey2010_reward_salience_acc
title: "Reward changes salience in human vision via the anterior cingulate"
authors:
  - "Hickey, Clayton"
  - "Chelazzi, Leonardo"
  - "Theeuwes, Jan"
year: 2010
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.1026-10.2010"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.1026-10.2010"
tags:
  - visual-attention
  - human-neuroimaging
  - dopamine
  - psychophysics
concepts:
  - reward-modulated-attention
  - priority-map
  - attentional-template
  - gain-modulation
related:
  - desimone_duncan1995_biased_competition
  - glimcher2011_dopamine_rpe
  - failing_theeuwes2018_selection_history
  - monosov2020_outcome_uncertainty
  - krauzlis2013_sc_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_89
status: full
depth: full
last_updated: "2026-05-15"
---

# Reward changes salience in human vision via the anterior cingulate

## 1. Abstract

Reward-related mesolimbic dopamine steers animal behavior, creating automatic approach toward reward-associated objects and avoidance of objects unlikely to be beneficial. Theories of dopamine suggest that this reflects underlying biases in perception and attention, with reward enhancing the representation of reward-associated stimuli such that attention is more likely to be deployed to the location of these objects.

Using measures of behavior and brain electricity in male and female humans, the authors demonstrate this to be the case. Sensory and perceptual processing of reward-associated visual features is facilitated such that attention is deployed to objects characterized by these features in subsequent experimental trials. This is the case even when participants know that a strategic decision to attend to reward-associated features will be counterproductive and result in suboptimal performance.

Other results show that the magnitude of visual bias created by reward is predicted by the response to reward feedback in anterior cingulate cortex (ACC), an area with strong connections to dopaminergic structures in the midbrain. The authors conclude that reward has an impact on vision that is independent of its role in the strategic establishment of endogenous attention, and that reward acts to change visual salience and thereby plays an important and undervalued role in attentional control.

## 2. Why this matters for us

The user's program contains an explicit RL hub that injects Q/K contributions into the central self-attention substrate, and the published Recurrent ViT is trained with reward signals (PPO-style updates) on change-detection. Hickey, Chelazzi & Theeuwes 2010 is the canonical human-neuroimaging demonstration that reward *automatically* re-weights visual salience even against the observer's strategic interest, with the bias magnitude predicted by ACC reward-feedback response.

This makes the paper a direct empirical anchor for two architectural commitments: (i) treating learned attention patterns in the recurrent ViT as a reward-shaped priority map rather than a purely top-down endogenous template; (ii) reading the multi-hub system's RL contribution to the central attention map as an architectural analog of ACC-mediated reward biasing. It is also one of the load-bearing citations for the user's competition-emergent-PC thesis, since it shows the reward system competing for control of the attention substrate even when doing so harms the observer.

## 3. Key claims

1. **Reward biases subsequent attentional selection independent of strategy.** On trial $n+1$, attention is preferentially deployed to objects sharing the color of the trial-$n$ target only when trial $n$ was rewarded with a high (vs low) magnitude. The effect persists when participants know it is counterproductive.
2. **The bias is automatic, not endogenous.** Because high reward is associated with the target color that *changes from trial to trial*, the rational strategy is to ignore color; the observed bias therefore reflects an involuntary salience change, not strategic top-down attention.
3. **The bias appears in early sensory ERPs.** N2pc (an electrophysiological index of attentional selection, ~200 ms post-stimulus, contralateral posterior scalp) is larger to high-reward-color distractors than to low-reward-color distractors on the *following* trial.
4. **ACC reward-feedback response predicts the magnitude of the attentional bias.** Across participants, the amplitude of the ACC-localized feedback-related negativity (FRN) to high-vs-low-reward outcomes correlates with the size of the subsequent attentional bias toward the rewarded color.
5. **Reward changes salience, not just response.** The locus of the effect (early N2pc, color-specific, prior to overt response) implies that reward operates on the visual priority map rather than on motor/decision stages.
6. **A new role for ACC in attentional control.** ACC is positioned not only as a performance/conflict monitor but as the source of reward-driven salience biasing, via its known projections to/from midbrain dopaminergic structures.
7. **The framework subsumes "value-driven attentional capture" before that label existed.** The paper predates the formal naming of value-driven attentional capture (Anderson, Laurent & Yantis 2011) but supplies the demonstration that reward associations *acquired within a session* are sufficient to drive subsequent involuntary capture — and that the neural correlate is in a reward-coding region, not in the dorsal frontoparietal attention network.
8. **Reward biasing is dissociable from explicit cognitive control.** The bias operates on the visual system before strategic top-down control can intervene, consistent with the temporal profile of the ACC reward-feedback response feeding into visual cortex via dopaminergic projections on a faster timescale than dorsolateral-PFC-mediated strategic biasing. This makes the effect parametrically distinct from Posner-cuing-style endogenous attention even though the surface behavior (faster RT at a primed location) is similar.

## 4. Methods

Human participants (N = 14) performed an additional-singleton visual search task while EEG was recorded. On each trial, observers reported the orientation of a line segment inside a uniquely-shaped target (a diamond among circles, or a circle among diamonds). The target's color was randomly assigned to red or green on each trial, with the distractor singleton taking the complementary color. The target shape (diamond vs circle) varied trial-to-trial as well.

Reward feedback followed each correct trial: a random draw determined whether the trial was a "high reward" (≈10 cents) or "low reward" (≈1 cent) trial, with high/low signaled visually after the response. Critically, reward magnitude was random and *unrelated* to performance on the rewarded trial — there was no informational basis for the observer to associate any feature with reward.

The principal behavioral analysis examined trial $n+1$ as a function of trial $n$ reward magnitude and color repetition. The principal EEG analyses examined:
- The N2pc on trial $n+1$ as an index of attentional capture by the distractor when its color matched the trial-$n$ target color; modulated by trial-$n$ reward magnitude.
- The feedback-related negativity (FRN) on trial $n$, source-localized to ACC (BA 24/32) using standard dipole / sLORETA approaches, as the index of ACC reward-feedback response.
- Across-participant correlation between FRN amplitude and the magnitude of the trial-$n+1$ N2pc / RT bias.

A second logical strand uses the *singleton-distractor* design (Theeuwes 1992 paradigm) so that the distractor is *physically* salient — a uniquely-colored item that under default attentional capture predictions should always pull attention. The reward manipulation is therefore tested against a strong baseline of bottom-up salience, and the diagnostic dependent variable is whether previous-trial reward shifts the *modulation* of that capture. This is the design feature that lets the paper isolate a reward-driven *change* in salience rather than a generic priming or expectation effect: the bottom-up salience of the distractor is held constant; only the reward history of its color varies.

The reward-feedback display is brief (a small numeric or graphical indicator of the trial's payoff) and is followed by an inter-trial interval long enough to dissociate the reward-related ERP from the next trial's stimulus-locked activity. This temporal isolation lets the FRN be extracted cleanly and lets the trial-$n+1$ N2pc be measured uncontaminated by reward-feedback responses on trial $n$. Behavioral analyses condition on accuracy on trial $n$ (only correct trials enter the trial-$n+1$ analysis), removing one obvious confound; error-trial dynamics are reported separately.

EEG preprocessing follows standard ERP-analysis conventions for the field: ICA-based ocular-artifact removal, bandpass filtering tuned to preserve both the early N2pc window and the somewhat later FRN window, and contralateral-minus-ipsilateral difference-wave computation for the N2pc (the standard isolation of the attention-related signal from the bilateral visual response). Statistical tests on ERP amplitudes use mean-amplitude windows around the canonical peak latencies rather than peak-picking, which is the methodologically more conservative choice.

Reward-magnitude and color assignment are fully counterbalanced across trials and across participants: red and green serve equally often as target and distractor colors, and the high/low reward outcomes are equiprobable on correct trials. This rules out a long-run color-frequency or color-asymmetry confound. Participants are paid the cumulative reward at the end of the session, so the within-session incentive structure is intact even though each individual trial's reward is small.

## 5. Results

**Behavioral.** After a high-reward trial, RT was significantly slowed on trial $n+1$ when the distractor matched the trial-$n$ target color (i.e., attention was captured by the previously-rewarded color). After a low-reward trial, the same color-match condition produced a smaller or absent slowing. The effect was on the order of 10–20 ms, statistically reliable, and present despite no incentive (and indeed counter-incentive) to attend to color.

**N2pc.** A larger N2pc to the distractor was observed on trial $n+1$ when the distractor matched the trial-$n$ target color following a high-reward trial — an electrophysiological signature of attentional capture. The latency (~200–300 ms) places the effect at perceptual/attentional, not motor, stages.

**FRN / ACC.** A robust FRN was elicited by the reward-feedback display on trial $n$, with larger amplitude for low-reward (negative-prediction-error) outcomes consistent with the established RPE interpretation. Source localization placed the generator in dorsal ACC.

**Cross-participant correlation.** The amplitude of the participant's FRN difference (high minus low reward) significantly predicted the magnitude of the trial-$n+1$ attentional bias (both behavioral RT cost and N2pc enhancement). Participants with stronger ACC reward responses showed stronger subsequent attentional biases. This is the load-bearing correlational claim linking ACC to reward-driven salience.

**Control conditions.** The effect cannot be reduced to simple color priming: the rewarded color *changed unpredictably* across trials, so a color-repetition account would predict equal facilitation regardless of trial-$n$ reward magnitude. The reward-magnitude $\times$ color-repetition interaction is the diagnostic signature that distinguishes reward-driven salience from generic feature priming, and it is significant in both the RT and N2pc measures. The pattern is also asymmetric: reward enhances capture by the *previously-rewarded* color rather than suppressing capture by the previously-unrewarded color, consistent with a gain-modulation account of priority-map weights.

**Strategic-counterproductivity check.** Because the rewarded target color is unpredictable across trials, a rational observer should attempt to *suppress* color as a basis for selection — the optimal strategy is to ignore previous-trial color and rely on the shape singleton that defines the current target. The persistence of the reward-driven color bias under these conditions is therefore not just "non-strategic" but actively *counter-strategic*. Post-experiment debriefing confirms most participants are aware that color is uninformative, ruling out the explanation that the bias reflects an explicit (if suboptimal) belief about color-reward contingency.

**Latency profile.** The N2pc effect emerges in the canonical 180–300 ms window and resolves before the later motor-preparation components (LRP). This places the reward-driven bias within the perceptual / attentional-selection stage rather than the response-selection stage, ruling out an account in which reward biases motor priors rather than visual salience. The behavioral RT effect is consistent in sign with the ERP effect, providing a coherent convergent picture across measures.

**Magnitude.** The behavioral RT cost of attentional capture by the previously-rewarded color is on the order of 10–20 ms, and the N2pc-amplitude enhancement is on the order of a few microvolts at posterior electrode sites. Both are modest in absolute terms but reliable, and both reflect *one trial* of reward conditioning rather than a built-up associative history — the smallness of the effect is therefore a feature, not a bug: it demonstrates that even a single reward outcome perturbs the salience map enough to be detected behaviorally and electrophysiologically on the next trial.

## 6. Critique / limitations

The correlation is across only N = 14 participants, which is small for an across-subject brain–behavior correlation. Subsequent reward-priority-map work (Anderson, Laurent & Yantis 2011 in *PNAS*; Failing & Theeuwes 2018 review) replicates the behavioral effect at scale but the across-subject ACC–bias correlation specifically has not been as robustly replicated in larger samples.

EEG source localization to ACC is inherently indirect. While the FRN is one of the most reliably ACC-localized ERP components, the spatial resolution does not differentiate ACC sub-regions, and the inference that ACC *causes* the salience change rather than merely correlating with it is not directly supported. fMRI and lesion follow-ups would be needed for a stronger causal claim; the paper itself is appropriately cautious on this point but the discussion sometimes elides the gap.

The effect operates on a single-trial timescale and uses a small reward differential (1 vs 10 cents). Whether the same mechanism scales to the multi-trial reinforcement-learning regime in which a feature becomes persistently reward-associated is a separate empirical question, addressed by Anderson et al. 2011 and subsequent work on value-driven attentional capture.

The paper does not distinguish between "reward changes salience on the priority map" and "reward changes the readout from the priority map." Both produce the observed N2pc effect. Subsequent single-unit work in macaque (Peck et al. 2009 in V4; Stănișor et al. 2013 in V1) localized at least part of the modulation to early visual cortex, supporting the salience-map account, but the 2010 paper alone cannot resolve this.

The role of dopamine is inferred rather than measured. The ACC–midbrain connection is invoked but no pharmacological manipulation is performed. The dopaminergic mechanistic story is therefore a plausible interpretation, not a demonstration. Subsequent work using L-DOPA / haloperidol manipulations (e.g., in patient populations and pharmacological-fMRI designs) is needed to close the loop; the 2010 paper is best read as motivating that follow-up rather than completing it.

A subtler limitation is the absence of any *temporal-decay* characterization. The effect is measured at lag-1 (trial $n \to n+1$) only; whether it persists over longer lags, accumulates over many trials, or interacts with extinction is not addressed. Anderson, Laurent & Yantis 2011 and subsequent value-driven-attentional-capture literature show that the effect can persist for hundreds of trials and even across days under appropriate training schedules, so the 2010 paper is the *minimal-paradigm* version of a phenomenon that is robust across many task structures — but the parametric characterization is downstream of this paper, not in it.

The N2pc itself, as an index, is also indirect: it is a difference-wave signature whose source localization is consistent with extrastriate visual cortex but does not uniquely pinpoint a generator. Treating "N2pc enhancement" as direct evidence of "salience-map gain change" is an inferential step the paper assumes more than demonstrates. This caveat does not undermine the qualitative reward-biases-attention claim but does soften the *salience-map* framing in particular — the same data are compatible with a slightly later attentional-selection account that does not require literal gain changes on early sensory units.

Finally, the across-participant brain–behavior correlation is reported as a Pearson correlation on a small N without correction for multiple comparisons across the many ERP windows and electrode sites considered, and without a held-out validation. Standard contemporary practice (e.g., Vul et al. 2009-style critiques) would flag this as a high-variance inferential procedure even at $p < .05$. The paper's overall reward-biases-attention conclusion is supported by the within-subject ERP and RT effects independently of this correlation, so even if the cross-subject FRN-N2pc correlation does not survive replication at scale, the central claim is robust; but the *specific* localization to ACC depends on this correlation surviving, and that is an empirical fact about a small sample, not a foregone conclusion.

## 7. Connection to our work

This paper is one of the key empirical anchors for treating the recurrent ViT's reward training signal as something that should be expected to *automatically* shape its learned attention maps in feature-specific ways — even ways the task structure does not endorse.

**RL hub as ACC analog.** In the multi-hub program (§5 of `threads/the_user_architectural_program.md`), the RL hub contributes $c^{(\text{RL})}_q, c^{(\text{RL})}_k$ projections that bias the central self-attention competition (`feedback-transformer`). Hickey et al. 2010 is the human-neuroimaging case that ACC, an established RL-error-computing region, exerts precisely this kind of bias on visual attention. Reading the architectural RL hub as the computational analog of ACC's role in attention is empirically supported here.

**Reward-shaped attention in the published Recurrent ViT.** The published change-detection model (2502.10955) is trained with reward (PPO-style). The user's program predicts — and Hickey et al. supply the biological precedent for predicting — that the learned attention patterns will not be pure endogenous templates but will include reward-shaped feature biases that persist across trials and may even harm performance in transfer settings. The "attention dynamics evolve nontrivially over passes" observation in the Food-101 classifier experiments is consistent with the same phenomenology at the network level: reward-trained attention is not a clean endogenous template.

**Salience-map / priority-map substrate.** The paper's framing places reward modulation on a *salience* (priority) map, in the Itti-Koch / Bisley-Goldberg tradition. The recurrent ViT's spatial attention map plays the same architectural role: a single substrate that integrates bottom-up, top-down, and reward bias. The Feedback Transformer's element-wise combination of sensory and feedback Q/K projections (`feedback-transformer` concept) is the formal mechanism by which a reward-hub contribution would re-weight the attention substrate exactly as Hickey et al. describe at the behavioral / ERP level.

**Competition-emergent PC support.** The thesis (§5 of the program thread) predicts that hubs compete for control of the attention substrate even when doing so is locally suboptimal — coalitions secure resources by being predictive about rivals, not by being aligned with the observer's strategic goals. Hickey et al.'s key result — that reward-driven bias appears *despite* being counterproductive — is exactly the signature competition-emergent PC predicts: a coalition (the reward / ACC / dopamine coalition) wins control of the attention substrate because it has the predictive infrastructure to do so, even when its winning hurts the overall objective. This is one of the cleanest behavioral demonstrations of an internal hub overriding strategic top-down control.

**Biased competition extension.** Compared to Desimone & Duncan 1995 (`desimone_duncan1995_biased_competition`) where the bias signals come from frontal/parietal endogenous-attention regions and WM templates, Hickey et al. supply a third bias source: the reward system via ACC. The user's multi-hub program is already committed to multiple bias sources feeding a single competitive substrate, so this paper extends the source roster in exactly the architecturally-relevant direction.

**Gain-modulation locus.** The paper's effect is best described as a *gain* change on feature-tuned units rather than a threshold or all-or-none gating: capture is enhanced for the previously-rewarded color while remaining capture-by-salience for the unrewarded one. This maps cleanly onto the Feedback Transformer's Hadamard-product combination (`gain-modulation` concept), in which a feedback Q/K contribution multiplicatively scales the sensory Q/K rather than replacing or thresholding it. The architectural commitment is therefore the right *kind* of modulation for the biological mechanism the paper identifies.

**Connection to selection-history priority.** The paper is one of the founding citations for the now-standard tri-partite division of attentional priority into endogenous, exogenous, and *selection-history* components (Awh, Belopolsky & Theeuwes 2012). Selection history — of which reward history is the principal case — is precisely the component a trained neural network *automatically* accumulates and therefore the one most likely to drive learned-attention pathologies in the recurrent ViT. The paper supplies both the empirical evidence that this third source exists and a candidate neural locus (ACC) for it.

**Limitation flag for the published model.** The paper also flags a risk: if reward-driven attention biases can override strategy in humans, the published Recurrent ViT may inherit pathological feature biases from its training reward signal that would not appear in standard supervised training. This is worth tracking in transfer / OOD evaluation of the published model and successor architectures.

**Concrete operationalization for the multi-hub experiment.** §5 of the program thread proposes an empirical test: train MSI / RL / VAE hubs on conflicting objectives, then probe whether the system has learned an implicit world model of its internal competitors. Hickey et al. supply a behavioral readout template for that test. Specifically, a Hickey-style trial-$n$/$n+1$ reward-history analysis on the multi-hub system would diagnose whether the RL hub has learned to bias the central attention substrate independently of the strategically-correct task signal. If the model shows a Hickey-style counter-strategic carryover — and if that carryover correlates across training seeds with an analog of the FRN (the RL-hub's reward-prediction-error magnitude on trial $n$) — that is direct architectural-level evidence for the competition-emergent-PC mechanism the user is proposing. The paper therefore is not just a citation but a template for a quantitative diagnostic experiment on the multi-hub system.

**Suggested variants on architectural choices.** Taking the Hickey result seriously suggests two concrete design knobs worth exploring in the recurrent ViT and PRISM successors. First, the strength of the RL-hub Q/K contribution should likely be *learnable per layer*, not fixed: the biological evidence is that ACC's influence on the attention substrate is gated and graded, not all-or-none. Second, an analog of the "extinction" condition — periods of training in which the previously-rewarded feature is no longer reinforced — should be included in evaluation, since the value-driven-attentional-capture literature consistently shows that the bias outlasts the contingency. Failure to test extinction would mean the model is evaluated only on training-distribution alignment, missing the regime where the Hickey-style mechanism is most diagnostically visible.

**Anchor for the ACC-as-bias-source story across the thread.** In the user's notes, the RL hub is sometimes glossed as "basal-ganglia-like" and sometimes as "ACC-like." Hickey et al. is the citation that licenses the ACC framing specifically for visual-attention biasing, distinct from the BG framing more natural for action selection. Tagging the RL hub's *attention-biasing function* as ACC-mediated (rather than BG-mediated) lets the architectural story line up with the human neuroimaging literature on selection-history priority and with the broader Botvinick-Braver framing of ACC as integrator of reward and control.

**Relation to the eye-tracking result.** The Evolution-of-Architecture eye-tracking experiment (§6 of the program thread) trains a hierarchical RViT to predict human fixations. Hickey et al. predicts that humans' fixations in any task with even mild reward structure will carry selection-history signatures that pure-bottom-up saliency models will miss. If the eye-tracking dataset includes any reward / payoff structure, the recurrent ViT — with its capacity for reward-shaped attention via the RL hub or via implicit reward-correlated supervision — should be more competitive with human gaze than a feedforward saliency model. This makes Hickey et al. relevant not only to the change-detection paper but to the broader empirical program of matching human attention dynamics.

**Interaction with PRISM's prediction-error attention.** PRISM v1 uses prediction error rather than softmax attention as the substrate for selection (`THESIS.md` §2.4). If reward biases attention via a salience-map gain change, PRISM v1's prediction-error-driven selection should *also* be susceptible to reward-shaped distortion, but via a different mechanism: the prediction-error map's amplitude would be reward-modulated rather than the attention-softmax's argmax. Hickey et al. is silent on this distinction (the experiment is at the behavior + ERP level), but the architectural prediction is testable in PRISM by training with reward and probing whether the prediction-error map shows the analog of a Hickey-style trial-$n$/$n+1$ carryover. This is a non-trivial empirical contribution PRISM v2 could make to the value-driven-attention literature.

**Status as a "Posner-adjacent" anchor for the program.** §7 of the program thread asks whether new papers anchor the *architectural* side or the *task* side of the program. Hickey et al. is a behavioral / human-neurophysiology paper, not an architectural one, and so anchors the task side: it specifies a *phenomenon* (reward-driven selection-history bias) that any architecturally adequate model of attention should reproduce. Together with the Posner-cuing literature (endogenous bias), the singleton-capture literature (exogenous bias), and the WM-template literature (template-driven bias), Hickey et al. completes the four-corner empirical landscape against which the recurrent ViT and PRISM successors must be evaluated. A model that captures Posner-cuing but fails the Hickey-style reward carryover is empirically incomplete in a way the program's multi-hub commitment is meant to address.

**Summary of the hook.** The shortest version: Hickey et al. 2010 is the cleanest single demonstration that reward modifies the visual priority map directly, automatically, and against strategic interest, with ACC as the candidate neural source. Every architectural commitment in the user's program that puts a reward / RL hub in contact with the attention substrate inherits both the empirical license and the empirical obligation of this paper: license to expect such biases to emerge in trained networks, obligation to design evaluations that detect them.

**Compatibility with predictive-coding framings.** Within a predictive-coding (Rao-Ballard / Friston) framework, the Hickey et al. result reads as reward modulating the *precision* of feature-tuned prediction-error units in early visual cortex via descending dopaminergic / ACC signals. This is consistent with the precision-weighting reformulation of biased competition (Feldman & Friston 2010) and with Spratling's PC-formulation, but goes beyond either by adding a *reward* source of precision modulation. In the user's competition-emergent-PC reformulation, reward biasing is exactly the case where a competing coalition (the reward / dopamine / ACC coalition) wins control of a shared substrate by predicting its rivals — here, by predicting which visual features will be informative for upcoming behavior.

## 8. Citations to follow

- `anderson_laurent_yantis2011_value_attention` — *PNAS* paper extending the single-trial effect to persistent value-driven attentional capture with trained color-reward associations. The canonical scaling-up of the Hickey 2010 result.
- `peck2009_v4_reward` — single-unit recording in macaque V4 showing reward-driven modulation of feature-tuned responses. Provides the cellular substrate that ERP work like Hickey et al. infers only indirectly.
- `stanisor2013_v1_reward` — V1 single-unit work on reward modulation. Pushes the locus of reward-driven salience even earlier than V4 and constrains the depth at which reward-shaped priority must be implemented in the visual hierarchy.
- `holroyd_coles2002_frn_theory` — the FRN-as-ACC-RPE-signal theoretical framework, on which the source-localization interpretation in this paper rests. Required reading to evaluate the strength of the ACC-locus claim.
- `botvinick_braver2015_motivation_control` — review framing ACC as integrating reward / cost signals into cognitive control. Connects this paper's ACC story to the broader cognitive-control literature.
- `awh_belopolsky_theeuwes2012_top_down_bottom_up_selection_history` — the framework that explicitly added "selection history" (including reward history) as a third source of attentional priority beyond endogenous and exogenous, with this 2010 paper as a load-bearing citation.
- `chelazzi2013_reward_visual_cortex` — Chelazzi's review of reward effects in visual cortex, expanding the single-author story and reviewing the macaque single-unit follow-ups.
- `theeuwes1992_singleton_capture` — the additional-singleton paradigm this paper uses; the foundational bottom-up-capture demonstration.
- `failing_theeuwes2018_selection_history` — already in seed candidates. The contemporary review of selection-history (including reward-history) effects on attention; Hickey 2010 is one of its anchor citations.
- `hickey2014_reward_visual_cortex_review` — Hickey's own later review of reward and visual cortex, useful for the trajectory of the research program from this 2010 paper onward.
