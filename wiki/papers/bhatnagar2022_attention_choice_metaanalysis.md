---
id: bhatnagar2022_attention_choice_metaanalysis
title: "A meta-analysis on the effect of visual attention on choice"
authors:
  - "Bhatnagar, Roopali"
  - "Orquin, Jacob L."
year: 2022
venue: "J Exp Psychol Gen"
doi: "10.1037/xge0001204"
arxiv: ""
url: "https://doi.org/10.1037/xge0001204"
tags:
  - visual-attention
  - decision-making
  - review
  - psychophysics
concepts:
  - drift-diffusion-model
  - reward-modulated-attention
  - priority-map
  - cueing-effect
related:
  - desimone_duncan1995_biased_competition
  - gold_shadlen2007_decision_making
  - krauzlis2013_sc_attention
  - bisley_goldberg2010_parietal_priority
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_4
status: full
depth: full
last_updated: "2026-05-15"
---

# A meta-analysis on the effect of visual attention on choice

## 1. Abstract

Decision makers attend more to preferred choice options and to the ultimately chosen option, but does visual attention influence preferences and choice? Several theories suggest that attention has a causal effect on preferences and choice, and a growing number of studies have examined the question with experimental methods. However, the evidence for an effect of attention on choice is mixed and highly contended. To advance the debate on the role of attention in decision making, the authors meta-analyze studies that manipulate attention to choice options and measure the effect on two-alternative preferential choices. Three different methods for manipulating attention are identified: studies manipulating total exposure time enhance choice probability for the attended option the most (P = .541, 95% CI [.523, .560], p < .001), followed by studies controlling the location of the last fixation (P = .532, 95% CI [.518, .547], p < .001). Studies manipulating the location of the first fixation do not differ from chance level choice proportions (P = .507, 95% CI [.497, .516], p = .18). The PET-PEESE analysis suggests a small degree of publication bias which results in a slight reduction of effect sizes. A meta-regression with absolute attention difference as predictor confirms the robustness of the findings. The findings show the relevance of assuming an effect of attention on choice but also indicate a need for further model development to account for the complete pattern of attention effects.

## 2. Why this matters for us

The recurrent ViT paper (2502.10955) cites this meta-analysis as ref [4] in establishing that visual attention causally biases value-based choice — not merely tracking preference but actively shaping it. This is the empirical anchor for the user's broader architectural commitment that attention is the *control substrate* through which competing internal hubs (sensory, RL, default-mode) influence behavior.

If attention only *correlated* with choice, the multi-hub competition story in [the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §5 would lose its central mechanism: there would be no reason for hubs to compete for attention, because attention wouldn't move outcomes. Bhatnagar & Orquin's quantitative case — that attention manipulation moves choice probabilities by 3–4 percentage points across hundreds of experiments — provides the empirical license to treat the central self-attention map in the multi-hub architecture as a *causal* bottleneck on behavior, not just a readout.

The result that exposure-time manipulations have the largest effect and first-fixation manipulations have essentially no effect also bears directly on the temporal-integration story implicit in the recurrent ViT's iterative passes: attention's behavioral consequences emerge through sustained processing, which is exactly what the recurrent architecture's repeated passes over a static image are designed to model.

## 3. Key claims

1. **Total-exposure-time manipulations causally enhance choice for the attended option.** Averaged across the included studies, the attended option is chosen with probability P = .541 (95% CI [.523, .560]), reliably above chance. Exposure time is the manipulation class with the largest and tightest effect.
2. **Last-fixation manipulations also causally enhance choice, with smaller effect.** P = .532 (95% CI [.518, .547]) — the well-known "gaze cascade" effect is real but moderate. Controlling which option is fixated at the moment of choice shifts choice probability by roughly 3 percentage points.
3. **First-fixation manipulations do *not* causally shift choice.** P = .507 (95% CI [.497, .516], p = .18) — early attention alone is insufficient; sustained processing matters. The tight CI rules out any but a negligible average effect.
4. **The effects are not artifacts of publication bias.** PET-PEESE correction reduces effect sizes only slightly; the qualitative pattern survives. The literature is not significantly inflated by selective reporting.
5. **Effect size scales with absolute attention difference.** Meta-regression confirms that the more attention is biased toward one option, the larger the choice-probability shift. The relationship is monotonic, consistent with an accumulator account in which attention multiplicatively scales evidence intake.
6. **Existing models account for parts but not all of the pattern.** The asymmetry between exposure-time, last-fixation, and first-fixation effects challenges single-mechanism accounts (pure evidence-accumulation, pure mere-exposure, pure gaze-cascade). The authors call for hybrid models that combine attention-gated accumulation with additional mechanisms.
7. **The findings establish a causal direction, not just a correlation.** Because the meta-analysis is restricted to *manipulation* designs (random assignment of attention), the inference that attention causes choice is licensed; the much larger correlational literature on attention-choice covariation cannot establish causation by itself.

## 4. Methods

A pre-registered meta-analysis of experimental studies on two-alternative preferential choice in which attention to one of the two options is *manipulated* (not merely measured) and choice proportion is the dependent variable. The literature search drew from PsycInfo, Web of Science, and Google Scholar; inclusion criteria require an experimental design with random assignment, a binary preferential choice outcome, and an attention manipulation directed at one of the two options rather than at extraneous stimuli.

Three manipulation classes are distinguished and analyzed separately:

- **Total exposure time.** One option is displayed for a longer cumulative duration than the other (e.g., 900 ms vs. 300 ms per display cycle, or alternating presentation with asymmetric durations). The manipulation increases the *aggregate* attention to the favored option without controlling specific fixation events.
- **Last-fixation location.** The trial terminates when the participant's gaze lands on the experimenter-designated option, ensuring the favored option is the last attended option at the time of choice. This isolates the *gaze cascade* mechanism — the empirical observation that gaze shifts increasingly toward the to-be-chosen option in the final moments before commitment.
- **First-fixation location.** The participant's first saccade is forced or cued to one option, typically via an asymmetric pre-cue, abrupt onset, or salience manipulation. This isolates the *attentional onset* mechanism: whether merely attending first is enough to bias choice.

For each study, the effect-size statistic is the choice proportion P for the attention-favored option, with chance level fixed at P = .5. Random-effects meta-analysis (REML estimator) is applied within each manipulation class. Heterogeneity is quantified by τ² and I². Publication-bias correction uses PET-PEESE (precision-effect test with precision-effect-estimate with standard error), which regresses observed effect on standard error and reports the intercept as the bias-corrected effect. A meta-regression uses the absolute attention difference (e.g., 600 ms exposure asymmetry) as a continuous moderator to test the dose-response prediction.

The sample of included studies is sized in the dozens per manipulation class, contributing hundreds of effect sizes overall. Studies of value-based or preferential choice between visual options (food, gambles, consumer products, faces) dominate; perceptual choice and memory-based choice without visual options are excluded. The authors also code study-level moderators (stimulus type, participant age, display duration) for sensitivity analyses.

The decision to analyze the three manipulation classes separately, rather than pooling them, is methodologically important: pooling would obscure the qualitative asymmetry that becomes the most theoretically informative result. Each class corresponds to a different conceptual hypothesis about *which* aspect of attention matters: aggregate dwell (exposure), terminal state (last fixation), or onset (first fixation). The separation lets the meta-analysis adjudicate among them.

## 5. Results

Headline numbers (replicating the abstract):

- **Total exposure time:** P = .541, 95% CI [.523, .560], p < .001. This is the largest, most robust effect. Translated to choice odds, the attended option is chosen ≈ 1.18× as often as the unattended option, a meaningful but not dominant bias.
- **Last fixation:** P = .532, 95% CI [.518, .547], p < .001. Smaller than exposure but reliably non-zero — the gaze-cascade signature reproduces across studies.
- **First fixation:** P = .507, 95% CI [.497, .516], p = .18. Indistinguishable from chance. The CI is tight enough to argue that any first-fixation effect, if it exists, is at most ≈ 0.016 in choice probability — practically negligible.
- **Publication-bias-corrected estimates:** PET-PEESE shrinks the exposure and last-fixation effects only modestly (a few thousandths of a probability point); both remain significant. The first-fixation null is unaffected.
- **Dose-response:** the meta-regression on absolute attention difference is positive and significant — larger asymmetries produce larger choice shifts, consistent with a monotonic causal relationship rather than a threshold effect.
- **Heterogeneity:** I² is moderate-to-high within each manipulation class, indicating that the random-effects pooled estimate masks real cross-study variation. Moderator analyses suggest stimulus type (food vs. gambles vs. faces) accounts for some of the variation but does not flip the qualitative pattern.

The asymmetry across manipulation classes is itself the most consequential result: it argues that attention's effect on choice is mediated by *sustained processing* (which exposure-time and last-fixation manipulations engage) rather than by *attention onset* per se (which first-fixation manipulations engage). The data are most naturally read as evidence for an accumulator account in which attention multiplies the rate of evidence accumulation in favor of the attended option, integrated over the dwell duration. The Krajbich-style attentional drift-diffusion model (aDDM) predicts exactly this signature: gaze-contingent multiplicative gain on evidence accumulation produces large effects when the gain is applied for long durations (exposure manipulation) or applied to the final pre-decision moment (last-fixation manipulation), but only chance-level effects when the gain is applied at the start of a trial that lasts much longer than the manipulation window (first-fixation manipulation).

The PET-PEESE analysis is worth dwelling on because the broader behavioral-economics literature on attention-choice has been criticized as susceptible to publication bias. Bhatnagar & Orquin's finding that PET-PEESE-corrected estimates remain significant for the exposure and last-fixation classes is a meaningful defense of the literature: even after adjusting for the funnel-plot asymmetry typical of selectively reported small studies, the causal-attention-on-choice effect remains. The first-fixation null, being already at zero, is unaffected by correction — i.e., there is no hidden small-study effect being suppressed there either.

The meta-regression on absolute attention difference adds a *dose-response* signature: studies with larger asymmetries between the two options' attention allocations produce larger choice shifts. This is the strongest evidence in the meta-analysis that the relationship is genuinely causal rather than a confound — confounded relationships do not typically show dose-response, while true causal effects do (the Bradford Hill criterion).

## 6. Critique / limitations

The included studies are heterogeneous in stimulus class (food, gambles, consumer products, faces), manipulation strength, and participant population. The authors handle this with random-effects models and subgroup analyses, but residual heterogeneity remains and limits generalization to specific decision domains. The pooled estimates should be read as cross-domain averages, not as predictions for a specific stimulus class.

Two-alternative preferential choice is a narrow slice of decision making. The findings do not directly speak to multi-alternative choice (where attention can sample three or more options and the gaze-cascade dynamics may differ), value-from-description choice (no visual stimuli, no fixation manipulation possible), or perceptual choice (where attention's role is established but mechanistically distinct — attention modulates *sensory* gain rather than *value* integration).

The first-fixation null is a population-level average over manipulations that vary widely in onset timing, cue type, and stimulus salience. A null at this level of aggregation does not rule out task-specific first-fixation effects; it constrains the *average* causal contribution of first-fixation attention across the included paradigm space. In particular, first-fixation manipulations with very short total trial durations (where the first fixation is also nearly the last) may behave more like last-fixation manipulations; the meta-analysis pools across these.

The meta-analysis does not distinguish overt (gaze-shift) from covert (no-gaze-shift) attention manipulations. Most manipulations are gaze-based; the inference that "attention" causes choice is, strictly, that *gaze-defined* attention causes choice. The framework leaves open whether covert attention alone (without supporting saccades) carries the same causal weight, and the broader literature suggests covert effects exist but may be smaller. This matters for any architecture that models attention separately from gaze, including the recurrent ViT (which has no gaze model at all — its attention is purely covert at the level of spatial token weighting).

The theoretical interpretation — attention multiplies evidence-accumulation rates — is consistent with the data but not uniquely identified by them. Mere-exposure accounts (Zajonc-style affective consequences of repeated exposure), fluency accounts (attention increases processing fluency, which is mistaken for preference), and gaze-cascade self-reinforcement accounts (preferring an option causes gaze, which feeds back to amplify preference) can each accommodate parts of the pattern. The authors' call for "further model development" acknowledges this. Discriminating among these accounts requires designs that decouple exposure, evaluation, and gaze choice — work that lies beyond the meta-analytic remit.

The reported effect sizes are *averages* over individuals. Trial-by-trial or individual-difference heterogeneity may be substantial: some participants in some studies show much larger attention-driven choice shifts (especially in value-low / preference-weak trials), while others show essentially no effect. The meta-analytic pooling cannot recover this within-study variance, which is the more relevant quantity for theories of individual decision making.

The choice of P (raw choice proportion) rather than a log-odds or Cohen-d style effect size has both advantages and limitations. The advantage is interpretability: a 0.04 shift in P is immediately readable. The limitation is that P-based effects compress near the .5 chance floor, so two studies with very different signal strengths can yield similar P estimates if both are far enough from ceiling. This is mostly a concern for large-effect studies, which the meta-analysis does not contain — most included effects are in the moderate range where the linear-P scale and the log-odds scale agree closely.

Finally, the meta-analysis says nothing about *mechanism* at the neural level. It is a behavioral synthesis, and the inference that attention's behavioral effect operates through evidence-accumulation (as opposed to mere exposure or fluency) is theoretical rather than directly demonstrated by the data. Bridging to neural mechanism requires either neuroimaging or primate-physiology evidence beyond this meta-analytic remit.

## 7. Connection to our work

This paper is the empirical license for several architectural commitments in the user's program. The connections operate at three levels: as direct empirical motivation for treating attention as a causal control variable, as a quantitative target for any model claiming to reproduce attention-driven choice, and as a constraint on the temporal structure of attention-driven biasing.

**The central self-attention map as a causal bottleneck on choice.** In [the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §5, hubs compete for control of a central attention substrate, and the winning hub's representation drives behavior. This story is only architecturally meaningful if attention *causes* downstream choice, not merely correlates with it. Bhatnagar & Orquin's meta-analysis is the strongest single piece of evidence in the human-behavior literature that the causal direction goes attention → choice (under controlled manipulation), with effect sizes large enough to matter (3–4 percentage-point shifts) and robust enough to survive publication-bias correction. The multi-hub architecture is, on this reading, a mechanistic implementation of *how* the brain implements the attention-to-choice causal pathway: hubs that win the central-attention competition have their preferred option chosen more often.

The directionality matters because the converse story — that choice causes attention — would license a quite different architecture, one in which a value-computing module first picks an option and then directs attention to it for confirmation. Bhatnagar & Orquin's manipulation designs rule out the pure-confirmation story: when the experimenter (rather than the participant's preference) drives attention, choice still shifts. The architectural commitment to attention-as-cause therefore has empirical backing, not merely conceptual appeal.

**The temporal-integration interpretation maps onto the recurrent ViT's iterative passes.** The result that exposure-time manipulations dominate first-fixation manipulations argues that attention's effect is *integrative* over time, not punctate. This aligns with the recurrent ViT's commitment (paper 2502.10955) that iterative recurrent passes over a static stimulus accumulate evidence — attention dynamics evolve nontrivially across passes (§6, classifier-on-Food-101 visualizations), and behavior locks in only after the trajectory has stabilized. The user's interpretation of the Food-101 "attention map evolves over passes" observation as the model's analog of evidence accumulation is consistent with Bhatnagar & Orquin's claim that *sustained* attention is what drives choice.

This temporal-integration framing also rules out certain architectural shortcuts. An architecture that decides on the first recurrent pass and uses subsequent passes only for refinement would not reproduce the human signature; one that integrates attention multiplicatively over passes (as the Feedback Transformer does) would. The meta-analysis thus provides empirical support not just for "recurrence in vision models" generically, but specifically for the *integrative* form of recurrence the user's program is built around.

**Implication for RL-hub design.** A future RL hub in the multi-hub architecture should bias the central attention map *gradually*, integrating its bias over multiple recurrent passes rather than imposing a one-shot first-pass preference. The first-fixation null in this meta-analysis is the human-behavior counterpart of the claim that one-shot top-down biasing is too weak to determine outcomes; sustained biasing (over many recurrent passes / dwell time) is what matters. This suggests the RL hub's contribution to the Q/K projections in the Feedback Transformer (`the_user_architectural_program` §5 "Formal account") should be persistent across recurrent steps, not transient.

Concretely, the RL hub's per-step contribution $c^{(\text{RL})}_q, c^{(\text{RL})}_k$ should evolve slowly across recurrent passes (e.g., as an EMA of a value-tracking state), rather than being recomputed sharply at each pass. The biological analog is the slow drift of value-coded firing in vmPFC and OFC during deliberation, which acts as a persistent bias on action-selection circuits in basal ganglia and frontal cortex. This persistence-over-deliberation is exactly the temporal property Bhatnagar & Orquin's exposure-time dominance argues for at the behavioral level.

**Bridge between biased-competition theory and behavior.** Desimone & Duncan 1995 ([desimone_duncan1995_biased_competition](research_db/papers/desimone_duncan1995_biased_competition.md)) established biased competition at the receptive-field level using single-unit data. Bhatnagar & Orquin extend the causal chain to whole-organism behavior: the attention bias that wins the RF-level competition propagates to a measurable shift in preferential choice. Together they bracket the user's argument that competition for attention is the load-bearing mechanism from neurons (Desimone & Duncan) to behavior (Bhatnagar & Orquin). The intervening links — priority-map computation in posterior parietal cortex, value integration in vmPFC, and accumulator dynamics in oculomotor circuits — are the implementation details that the multi-hub architecture must respect if it is to reproduce both endpoints of the chain.

**Effect-size calibration.** The 3–4 percentage-point shift Bhatnagar & Orquin report sets a quantitative target for any model that claims to implement attention-as-choice-bias. A computational architecture in which attention completely determines choice (P → 1.0 for the attended option) would be too strong; one in which attention is decorrelated from choice (P = .5) would be too weak. The empirical target is moderate: attention biases choice but does not fully determine it. In the user's multi-hub framing, this constrains how dominant the central self-attention map can be over downstream readout — the readout must remain partially independent of the attention bottleneck so that other factors (option value, base preferences, motor noise) can pull behavior off the attention-dictated outcome at the observed rate.

This calibration target also rules out an "attention as gating" extreme in which only the attended option is even represented downstream — that would produce near-ceiling P values. The data say attention *biases* but does not *gate*. A multi-head attention mechanism with moderate softmax temperature (so that low-probability tokens still get nonzero weight) is consistent with this; a hard-gating mechanism (top-k with k=1) is not. The recurrent ViT's standard softmax attention satisfies this requirement automatically.

**Connection to the cueing-effect concept.** The first-fixation null connects to the recurrent ViT's Posner-cuing experiments (paper 2502.10955 §5). In Posner cuing, a brief peripheral cue at trial onset biases later target processing. The recurrent ViT replicates the human signature (faster RT and higher accuracy at the cued location, scaling with cue validity). Bhatnagar & Orquin's first-fixation null says the *raw onset bias* alone does not move choice; the bias must be sustained or integrated. In the recurrent ViT this corresponds to the requirement that the cue token persists across recurrent passes (rather than being injected only at t=0). The Posner-cuing result and Bhatnagar & Orquin's exposure-time dominance both argue for the same architectural commitment: *persistent* feedback across passes, not a transient first-pass injection.

**Priority-map interpretation.** Bhatnagar & Orquin's data are also compatible with a priority-map account (Bisley & Goldberg 2010, [bisley_goldberg2010_parietal_priority](research_db/papers/bisley_goldberg2010_parietal_priority.md)) in which attention modulates a parietal priority map that gates oculomotor and decision readout. The dose-response result — larger attention asymmetries produce larger choice shifts — is the priority-map signature: the readout depends monotonically on the priority value at the option's location. The user's multi-hub architecture can be read as a priority-map implementation: the central self-attention map *is* the priority map, and hubs compete to shape it.

**Drift-diffusion implementation.** The aDDM-compatible reading of the meta-analysis suggests that future implementations of the RL hub should compute, for each option, an *evidence-accumulation* trajectory whose drift rate is multiplicatively gated by the current attention weight on that option. This is straightforwardly compatible with the Feedback Transformer Q/K structure: attention weights (post-softmax) at the option's spatial token act as the multiplicative gate on a value-accumulator readout. The choice is the option whose accumulator first crosses a threshold. This concrete reduction makes the user's multi-hub story testable against human aDDM fits.

In the user's existing change-detection benchmark (paper 2502.10955), there is no value-based choice — the task is to localize change. But the architectural primitive is the same: the recurrent ViT integrates attention-weighted features across multiple passes, with the integrated signal driving a final readout. Re-purposing this primitive for value-based choice would require adding (a) a value-encoding head over each option's spatial tokens, and (b) an accumulator that integrates the value-encoded signal weighted by attention. Both are minor architectural additions; the recurrent infrastructure is already in place.

**The empirical scope of the program's "attention-causes-behavior" claim.** Importantly, Bhatnagar & Orquin's findings apply specifically to *value-based preferential choice* with visual stimuli. They do not establish that attention causes behavior in general — perceptual decisions, memory-based decisions, motor decisions, and language production may follow different rules. The user's program should be careful to scope its causal claims to the same domain where they have empirical support, or to extend them only where convergent evidence (e.g., from primate microstimulation work on FEF and LIP, or from human TMS over parietal cortex) supports the extension.

**Relation to the recurrent ViT's change-detection benchmark.** The recurrent ViT paper (2502.10955) is benchmarked primarily on change detection — a *perceptual*, not value-based, task. Bhatnagar & Orquin's findings do not directly validate the recurrent ViT's design choices for that benchmark. They license a different claim: that the recurrent ViT's architectural commitments (especially the persistent feedback across passes) are appropriate *if* the architecture is to be extended toward value-based choice in future work. The meta-analysis is therefore best read as a forward-looking justification for architectural choices whose payoff lies in tasks beyond the published change-detection result, including the RL-hub extensions sketched in the user's notes.

**Convergence with subcortical attention literature.** Krauzlis et al. 2013 ([krauzlis2013_sc_attention](research_db/papers/krauzlis2013_sc_attention.md)) argues that the superior colliculus is a causal node in attention-driven behavioral selection in primates. The Bhatnagar & Orquin meta-analysis is the human-behavioral counterpart of that claim: in both literatures, attention is shown to be a causal driver of choice rather than a passive correlate. Together they support a view in which the central self-attention map in the user's multi-hub architecture corresponds, biologically, to a distributed parietal-collicular priority map whose state directly determines selection.

**Implications for evaluation of the multi-hub design.** If the user's program produces a working multi-hub system trained on a value-based choice task, the natural human-behavior comparison would be against the Bhatnagar & Orquin numbers. A successful model should reproduce: (i) the qualitative asymmetry across manipulation classes, (ii) the moderate effect-size magnitude (3–4 percentage point shift, not winner-take-all), and (iii) the monotonic dose-response. Producing these three signatures is a substantively meaningful behavioral validation independent of any task-accuracy metric. This is a more demanding bar than is typical for ML architecture papers, but it is the bar implied by the user's program's commitment to model human-like attention dynamics.

**The first-fixation null as an evaluation constraint.** A particularly diagnostic test for the multi-hub architecture would be whether it produces the first-fixation null: if the model is given a brief one-pass attentional bias toward one option but then allowed many recurrent passes of equal-attention processing, does the choice probability remain near .5? An architecture that *fails* this test — that locks in a choice from the first pass regardless of subsequent integration — would be qualitatively misaligned with human behavior. The recurrent ViT's persistent feedback across passes is the architectural feature that would let it pass this test.

## 8. Citations to follow

- `krajbich2010_attentional_ddm` — Krajbich, Armel & Rangel's attentional drift-diffusion model is the canonical computational account that Bhatnagar & Orquin's data partly support. Should be added; the aDDM is the most explicit formal bridge between attention and choice.
- `shimojo2003_gaze_cascade` — the original "gaze cascade" report; foundational for the last-fixation manipulation class. Establishes the empirical phenomenon that the meta-analysis aggregates over.
- `armel2008_biasing_simple_choices` — early causal-attention-on-choice manipulation by exposure time, a representative study in the included pool. Establishes the exposure-time paradigm.
- `cavanagh2014_attention_value` — DDM-and-attention work that bears on the meta-regression dose-response result; refines the aDDM with value-modulated gain.
- `pieters2008_advertising_attention` — exposure-time attention manipulations in applied advertising contexts; broadens the cross-domain robustness claim into consumer-behavior settings.
- `glaholt2009_eye_movements_decision` — eye-tracking-and-choice work that influences how last-fixation effects are interpreted; methodological precedent for fixation-controlled choice designs.
- `orquin_loose2013_attention_decision` — Orquin's own earlier review of attention and decision processes; theoretical background to the meta-analysis and source of the three-manipulation-class taxonomy used here.
- `gluth2018_attention_value` — Gluth et al. work on attention-value interaction in value-based decisions; relevant to the moderator analyses.
- `smith_krajbich2018_choice_eyetracking` — eye-tracking and choice in multi-alternative settings; identifies where the two-alternative meta-analytic findings would and would not generalize.
- `tavares2017_value_attention_vmpfc` — neuroimaging work on the value-attention interaction in vmPFC; provides the neural substrate bridge for the attention-choice causal pathway documented behaviorally here.
- `vaidya2018_neural_substrates_choice` — review of neural substrates of value-based decision making; complementary biological grounding for the behavioral meta-analytic finding.
- `polania2014_neural_oscillations_value` — EEG signatures of value-attention interaction during preferential choice; bears on whether the meta-analytic effect has identifiable neural correlates.
