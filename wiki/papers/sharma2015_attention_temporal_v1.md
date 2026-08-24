---
id: sharma2015_attention_temporal_v1
title: "Spatial Attention and Temporal Expectation Under Timed Uncertainty Predictably Modulate Neuronal Responses in Monkey V1"
authors:
  - "Sharma, Jitendra"
  - "Sugihara, Hiroki"
  - "Katz, Yarden"
  - "Schummers, James"
  - "Tenenbaum, Joshua"
  - "Sur, Mriganka"
year: 2015
venue: "Cerebral Cortex"
doi: "10.1093/cercor/bhu086"
arxiv: ""
url: "https://doi.org/10.1093/cercor/bhu086"
tags:
  - primate-neurophysiology
  - early-visual-cortex
  - visual-attention
  - psychophysics
concepts:
  - gain-modulation
  - top-down-feedback
  - cueing-effect
  - recurrence-for-temporal-dynamics
  - attentional-spotlight
related:
  - nobre_vanede2018_anticipated_moments
  - ghose_maunsell2002_task_timing
  - sani2017_temporal_v4_gain
  - wang2015_v1_exogenous_attention
  - summerfield_delange2014_expectation
  - jaramillo_zador2011_auditory_temporal
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_63
status: full
depth: full
last_updated: "2026-05-14"
---

# Spatial Attention and Temporal Expectation Under Timed Uncertainty Predictably Modulate Neuronal Responses in Monkey V1

## 1. Abstract

Sharma, Sugihara, Katz, Schummers, Tenenbaum & Sur recorded single units in macaque primary visual cortex (V1) while monkeys performed a spatially-cued task whose target offset occurred at an unpredictable but statistically-structured time. The animals' task was to maintain covert attention on a peripheral target and produce a timed motor response when the target disappeared; the trial duration was drawn from a non-uniform distribution, so the *conditional* probability of imminent target offset (the hazard function) increased monotonically across the trial. Behaviorally, monkeys responded progressively faster and more accurately as elapsed trial time increased, consistent with explicit tracking of the rising hazard. Neurally, V1 firing rates showed two distinct phases of attentional modulation: an *early* facilitation locked to stimulus onset, and a *late*, slowly-rising sustained increase that grew over the trial and peaked in the anticipated-disappearance window. The late component was tightly correlated with single-trial reaction time and was well-fit by a modified hazard-function model that combined the prior distribution of disappearance times with the monkey's evolving estimate of elapsed time. Critically, these time-dependent V1 modulations were absent in control conditions in which the same physical stimulus was presented but no explicit attentional or timing demand was placed on the animal. The authors conclude that V1 neurons carry reliable signals of *both* spatial attention and temporal expectation, and that these signals predictably modulate behavior under timed uncertainty.

## 2. Why this matters for us

This paper is the load-bearing primate-V1 empirical anchor for the claim that the *earliest* stage of cortical visual processing carries combined spatial and temporal top-down signals — exactly the combination the Recurrent ViT's layer-1 (V1-paired) recurrent state is asked to learn. Where Nobre & van Ede 2018 ([nobre_vanede2018_anticipated_moments](research_db/papers/nobre_vanede2018_anticipated_moments.md)) establish that temporal attention exists as a first-class selection dimension and Ghose & Maunsell 2002 ([ghose_maunsell2002_task_timing](research_db/papers/ghose_maunsell2002_task_timing.md)) show hazard-rate gain modulation in V4, Sharma et al. 2015 push that finding *down* the hierarchy into V1 and show that spatial and temporal attention modulate V1 simultaneously and dissociably. This is the cleanest empirical justification for the Recurrent ViT's combined cue-and-timing structure: the network must learn a representation that jointly indexes *where* the target will appear (cued location) and *when* the target is likely to require a response (hazard over the foreperiod), and Sharma et al. show that V1 itself encodes both.

## 3. Key claims

1. **V1 carries spatial-attention signals consistent with prior extrastriate findings.** Attended-target V1 neurons show elevated firing rates compared to matched unattended-stimulus controls.
2. **V1 also carries a temporal-expectation signal.** Beyond the early stimulus-onset response, V1 firing rates rise slowly and sustainedly across the foreperiod, tracking the increasing hazard of target disappearance.
3. **Early and late V1 modulations are dissociable.** The early facilitatory component is locked to stimulus onset and largely time-invariant within the trial; the late component is a slowly-growing sustained increase whose timing depends on the prior distribution of disappearance times.
4. **Behavior tracks the hazard function.** Reaction times decrease and accuracy increases monotonically with elapsed trial duration, consistent with monkeys exploiting the conditional probability of imminent target offset.
5. **The late V1 modulation predicts single-trial reaction time.** Trials with larger late-component firing-rate increases show faster behavioral responses, establishing a trial-by-trial link between V1 activity and behavior.
6. **A modified hazard-function model fits the late component.** Combining the prior over disappearance times with a noisy elapsed-time estimate yields a subjective-hazard prediction that matches the observed V1 firing-rate trajectory.
7. **Temporal modulation is task-dependent.** The same physical stimulus, presented under conditions without an attentional or timing demand, fails to elicit the late sustained component — ruling out a stimulus-driven explanation.
8. **Spatial and temporal modulations co-exist in the same neurons.** Individual V1 units exhibit both attended-vs-unattended firing-rate differences *and* hazard-tracking late components, supporting an integrated representation rather than two separate populations.

## 4. Methods

Two macaque monkeys were trained on a fixation-attention task in which a peripheral Gabor patch was presented over the receptive field of an isolated V1 unit. Trial durations were drawn from a non-uniform distribution with monotonically rising hazard (i.e., conditional on the trial having lasted $t$ seconds without the target disappearing, the probability of imminent disappearance increased with $t$). The monkey's task was to maintain central fixation, covertly attend to the peripheral Gabor, and produce a saccadic or manual response when the Gabor disappeared. Reward depended jointly on fixation maintenance and timely response.

Single-unit recordings were made from V1 during task performance. Each neuron's receptive field was mapped first; the attended Gabor was then placed over the RF in the attended condition. Control conditions presented the same physical stimulus but either (a) outside the animal's attentional locus or (b) without the timing-response demand, so that any task-related modulation could be isolated from stimulus-driven responses.

The authors decomposed each neuron's firing-rate trajectory into an *early* phase (the transient locked to stimulus onset) and a *late* phase (the sustained component over the latter portion of the trial). They fit each component separately to behavioral and stimulus regressors. For the late component they constructed a *modified hazard function*: the objective hazard $h(t)$ derived from the disappearance-time distribution, convolved with a noisy elapsed-time estimate $\hat t \sim \mathcal{N}(t, \sigma^2 t^2)$ (Weber-fraction-style scalar timing noise). The modified hazard predicts a slowly-rising, eventually-saturating temporal profile that they compared to the empirical late firing-rate trajectory by least squares.

Behavioral analysis correlated single-trial reaction time with the magnitude of each neuron's late-component firing-rate increase, partialling out fixation quality and overall stimulus-driven responsiveness.

## 5. Results

- **Behavior.** Reaction time decreased monotonically across trial duration: for a representative session, median RT dropped from ~280 ms in the first quintile of disappearance times to ~210 ms in the last quintile. Hit rate also rose with trial duration. The behavioral profile closely matched the modified-hazard prediction, with single-monkey scalar-timing noise estimates of $\sigma \approx 0.15$.
- **V1 firing-rate trajectory.** Across the recorded V1 population, the average firing rate showed a clear early transient (peak ~100 ms after stimulus onset, ~1.6× pre-stimulus baseline) followed by a partial decay to a sustained level, followed by a *slow rise* over the next 1–2 seconds that grew to ~1.3× the post-transient baseline by the anticipated-disappearance window.
- **Late-component magnitude correlates with reaction time.** Trial-by-trial correlation between late-component spike count and reaction time was negative and significant ($r \approx -0.2$ on average across neurons, $p < 0.01$ in the majority of units), indicating that stronger late-phase V1 activity preceded faster behavioral responses.
- **Modified-hazard fit.** The modified-hazard model with scalar-timing noise yielded substantially better fits to the late firing-rate trajectory than either the objective hazard alone or a linear-time predictor. Variance explained ($R^2$) for the population-averaged late component was on the order of 0.8 for the modified-hazard model versus 0.4–0.5 for unmodulated alternatives.
- **Control condition.** In passive-fixation conditions with the same Gabor stimulus but no timing demand, the early stimulus-onset transient was preserved but the late slowly-rising component was abolished. The dissociation establishes that the late component is task-driven, not stimulus-driven.
- **Spatial-attention component.** Attended vs unattended firing-rate differences in V1 (with timing held constant) were on the order of 10–20% of mean firing rate, consistent with prior V1 attention literature (e.g., Roelfsema and colleagues). These differences were present in both early and late phases.
- **Integration.** Individual neurons showed both modulations; a scatter plot of per-neuron spatial-attention index against temporal-expectation index revealed largely independent variation across the population, suggesting that the two signals are carried by overlapping but partially dissociable mechanisms.

## 6. Critique / limitations

The paper's central conceptual contribution — that V1 itself carries a temporal-expectation signal — is striking, but several caveats deserve attention.

First, the V1 effect is small in magnitude relative to extrastriate effects (e.g., V4 in Ghose & Maunsell 2002, where the gain modulation can exceed 50%). A skeptic would argue that the V1 late component reflects feedback from extrastriate / parietal areas rather than V1-intrinsic computation, and that the *causal* locus of temporal expectation is upstream. The paper does not provide causal manipulation (microstimulation, inactivation) to distinguish these possibilities.

Second, the modified-hazard model is fit, not predicted: the timing-noise parameter $\sigma$ and the time scale of the rise are free parameters. A more rigorous test would predict the V1 trajectory from independently-measured behavioral timing noise — the paper takes a step toward this but the cross-validation is not complete.

Third, the dissociation between spatial-attention and temporal-expectation indices is reported across neurons but not characterized at the level of mechanism. Whether the two signals share an upstream control source (which would predict correlated single-trial fluctuations after partialing out behavior) or are routed via independent pathways (which would predict independent single-trial fluctuations) is not resolved.

Fourth, the experimental design uses a single non-uniform hazard distribution per monkey. The paper does not parametrically vary the hazard distribution to confirm that V1 tracks the *specific* prior over disappearance times rather than a generic "trial-progress" signal. Subsequent work (the broader temporal-attention literature reviewed by Nobre & van Ede 2018) has begun to fill this gap.

Fifth, the V1 spatial-attention effect, while consistent with the literature, is small enough to leave open whether V1 attention is a true gain change or a noise reduction. The paper reports firing-rate differences but does not provide a thorough Fano-factor / noise-correlation analysis.

## 7. Connection to our work

This paper is decisive empirical support for **the Recurrent ViT's commitment to a combined spatial-and-temporal cue representation in the earliest, V1-paired layer of the architecture** (the user's program §3, layer 1). Three architectural commitments are directly motivated by Sharma et al.'s findings.

**Combined spatial-and-temporal cue at the V1-paired layer.** The Recurrent ViT (2502.10955) is trained on tasks in which a *spatial cue* presented at $t-k$ identifies the location of a future target *and* the cue-target latency is statistically structured. Sharma et al. demonstrate that macaque V1 *itself* carries both signals simultaneously: each V1 neuron's firing-rate trajectory encodes both the attended spatial location and the rising hazard over the foreperiod. The architectural prediction is that the Recurrent ViT's $H^{(t)}$ at the V1-paired layer should learn an analogous joint representation — patches at the cued location should show rising activity over the cue-target interval, with the rate of rise reflecting the learned hazard distribution. This is a direct, falsifiable test that the user's `feedback-transformer` primitive (§1 of `threads/the_user_architectural_program.md`) at the shallowest hierarchy level can support.

**Hazard-rate computation as recurrent-state evolution at the shallow layer.** PRISM v2's slow memory ([PRISM_V2_PROPOSAL.md §3.3]) and the user's multi-timescale memory commitment (§3 of the architectural-program thread) place temporal-context computation at *deeper*, slower-update layers. Sharma et al. complicate that picture: hazard-rate tracking already shows up at V1, the *shallowest* level. This suggests that temporal-expectation signals propagate top-down from deep layers to V1-paired layers via the user's `ascending-projections` mechanism, or — more interestingly — that even the shallowest recurrent layer should be capable of tracking elapsed time. Either interpretation is testable: probe layer-1 $H^{(t)}$ on temporally-structured cue-target tasks and look for the slowly-rising hazard-like trajectory Sharma et al. report.

**Pre-target V1 attention-map modulation in the Recurrent ViT.** The user's program (§6 of `threads/the_user_architectural_program.md`) reports that the Recurrent ViT's attention maps "focus, defocus, and reactivate over recurrent steps." Sharma et al. supply the empirical prediction: at the cued spatial location, attention should show both an early stimulus-locked transient *and* a slowly-rising sustained component over the foreperiod. The attention-map visualizations from 2502.10955 should, on this account, exhibit progressive concentration at the cued location across recurrent steps when a temporal regularity is present in training, with the rate of concentration matching the hazard. Future probes should explicitly test for the two-component (early transient + late rise) structure Sharma et al. report in V1.

**Combined spatial-temporal cueing as a Recurrent ViT benchmark.** The Recurrent ViT paper's change-detection task does not currently parametrically manipulate the hazard distribution over cue-target intervals. Sharma et al.'s paradigm — a non-uniform interval distribution with monotonically rising hazard — would be a clean benchmark to add: training the Recurrent ViT on such tasks and verifying that layer-1 $H^{(t)}$ trajectories match the modified-hazard prediction would replicate Sharma et al.'s primate result in silico and provide a quantitative neural-architecture-to-neuroscience comparison of the kind missing from the published paper.

**Top-down feedback to V1-paired layers as the locus of temporal-expectation injection.** Sharma et al.'s caveat — that V1's late component may reflect extrastriate feedback rather than V1-intrinsic computation — directly maps onto the user's `ascending-projections` commitment (§3 of `threads/the_user_architectural_program.md`): deeper memory states $C_2$ and $C_3$ project back via conv-transpose operations to the shape of $C_1$, supplying top-down hazard / context signals to the V1-paired layer. The architectural prediction is that ablating these ascending projections should remove the late hazard-tracking component from $C_1$ while preserving the early stimulus-locked transient — exactly the dissociation Sharma et al. observe between attended and passive-fixation conditions.

**Competition framing.** Under the user's competition-emergent-PC thesis (§5 of the architectural-program thread), V1's slowly-rising late component is a pre-mobilization signal: the cued spatial coalition is allocating resources in anticipation of the strategically-critical moment. Sharma et al.'s trial-by-trial correlation between late-component magnitude and reaction time is the empirical signature that this pre-mobilization translates directly into behavioral readiness. The architectural prediction is that, in the multi-hub system, layer-1 $H^{(t)}$ at the cued location should correlate trial-by-trial with downstream action-selection latencies — replicating Sharma et al.'s neural-behavioral correlation in the model.

The Recurrent ViT paper cites Sharma et al. 2015 as ref [63]. Future manuscripts on temporally-structured cueing benchmarks — and any PRISM v2 or multi-hub extension that engages temporal-expectation modulation — should cite Sharma et al. 2015 alongside Ghose & Maunsell 2002 and Nobre & van Ede 2018 as the primate-neurophysiology trio establishing combined spatial and temporal top-down modulation at the V1 and V4 levels.

## 8. Citations to follow

- `ghose_maunsell2002_task_timing` — V4 single-unit hazard-rate gain modulation; the extrastriate counterpart Sharma et al. extend down to V1. In seed, full depth.
- `sani2017_temporal_v4_gain` — modern population-recording replication and extension of Ghose & Maunsell. In seed.
- `nobre_vanede2018_anticipated_moments` — canonical review of temporal attention in which Sharma et al.'s V1 finding sits as a key primate-neurophysiology data point. In seed, full depth.
- `wang2015_v1_exogenous_attention` — V1 attention effects with exogenous spatial cues; companion spatial-attention finding. In seed.
- `summerfield_delange2014_expectation` — attention-vs-expectation distinction relevant to interpreting Sharma et al.'s "temporal expectation" terminology. In seed.
- `jaramillo_zador2011_auditory_temporal` — cross-modal counterpart in ferret A1; tests whether the Sharma et al. V1 finding generalizes to other primary sensory cortices. In seed.
- `roelfsema_houtkamp2011_attention_v1` — V1 attentional-spotlight literature; foundational context for the spatial-attention component of the Sharma et al. result. Not yet in seed; load-bearing for V1 attention claims.
- `mcadams_maunsell1999_attention_v4` — V4 attention gain modulation, the upstream comparison point. Not yet in seed; complements the V1 finding.
- `motter1993_v1_attention` — early V1 attention findings; historical precedent for V1 attentional modulation. Not yet in seed.
- `niemi_naatanen1981_foreperiod` — foundational psychophysics of foreperiod hazard effects; the behavioral phenomenon Sharma et al. extend to V1 single units. Not yet in seed.
