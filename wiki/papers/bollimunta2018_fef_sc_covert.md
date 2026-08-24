---
id: bollimunta2018_fef_sc_covert
title: "Comparing frontal eye field and superior colliculus contributions to covert spatial attention"
authors:
  - "Bollimunta, Anil"
  - "Bogadhi, Amarender R."
  - "Krauzlis, Richard J."
year: 2018
venue: "Nature Communications"
doi: "10.1038/s41467-018-06042-2"
arxiv: ""
url: "https://doi.org/10.1038/s41467-018-06042-2"
tags:
  - primate-neurophysiology
  - prefrontal-cortex
  - subcortical
  - visual-attention
  - change-detection
  - lesion-microstimulation
concepts:
  - priority-map
  - top-down-feedback
  - attentional-spotlight
  - pharmacological-inactivation
  - microstimulation
  - cueing-effect
related:
  - krauzlis2013_sc_attention
  - moore_armstrong2003_fef_microstim
  - cavanaugh_wurtz2004_sc_change_blindness
  - herman_krauzlis2017_sc_change_detection
  - clark2015_prefrontal_attention
  - sridharan2017_sc_sensitivity_bias
  - zenon_krauzlis2012_attention_deficits
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_67
status: full
depth: full
last_updated: "2026-05-16"
---

# Comparing frontal eye field and superior colliculus contributions to covert spatial attention

## 1. Abstract

The causal roles of the frontal eye fields (FEF) and superior colliculus (SC) in spatial selective attention have not been directly compared. Reversible inactivation is an established method for testing causality but comparing results between FEF and SC is complicated by differences in size and morphology of the two brain regions. Here we exploited the fact that inactivation of FEF and SC also changes the metrics of saccadic eye movements, providing an independent benchmark for the strength of the causal manipulation. Using monkeys trained to covertly perform a visual motion-change detection task, we found that inactivation of either FEF or SC could cause deficits in attention task performance. However, SC-induced attention deficits were found with saccade changes half the size needed to get FEF-induced attention deficits. Thus, performance in visual attention tasks is vulnerable to loss of signals from either structure, but suppression of SC activity has a more devastating effect.

## 2. Why this matters for us

Bollimunta, Bogadhi & Krauzlis 2018 is the *first direct, within-subject, common-task* comparison of FEF and SC causal contributions to covert attention. For the user's program, this is the load-bearing reference for treating the FEF (cortical) and SC (subcortical) as *parallel-but-asymmetric* attention substrates — the analog of the recurrent ViT's twin perturbation experiments and of the multi-hub system's competing cortical and subcortical influences on the central self-attention substrate. The result that the SC has the *larger* causal effect when matched for saccade-metric impairment is a quantitative bound on the relative weighting the user's program might place on subcortical-style vs. cortical-style feedback sources.

## 3. Key claims

1. **Both FEF and SC inactivation cause covert attention deficits.** Muscimol inactivation in either region produces lateralized impairments in motion-change detection in the affected visual field.
2. **Saccade metrics provide a common causal-strength benchmark.** Because muscimol injection also disrupts saccades, the *size* of the saccade impairment (latency and peak-velocity asymmetry) can be used to match inactivation efficacy across structurally heterogeneous regions.
3. **SC has a larger attention effect per unit saccade impairment.** Linear regressions of detection deficit on saccade latency asymmetry yield slope 0.31 ± 0.03 for SC vs 0.08 ± 0.03 for FEF — roughly a fourfold difference (p < 0.001).
4. **Threshold for reliable attention deficit is roughly half for SC.** Logistic regression: SC-induced attention deficits emerge at saccade-latency differences of 50–75 ms; FEF-induced deficits require 100–150 ms. SC velocity threshold 250–350°/s; FEF threshold 350–500°/s. FEF needs 40–100% larger saccade impairment to produce a reliable attention deficit.
5. **Bilateral asymmetry signature is preserved.** Inactivation reduces detection at the affected location and *increases* it at the unaffected location, consistent with biasing a winner-take-all competition between hemifields.
6. **Effects are not explained by scotoma differences.** SC and FEF inactivations were matched (no significant differences) on scotoma-to-stimulus distance, stimulus-scotoma overlap, and scotoma area.
7. **The result is robust to the choice of saccade benchmark.** Using memory-guided rather than visually guided saccades would only *strengthen* the SC > FEF asymmetry, because FEF inactivation is known to produce relatively larger memory-guided-saccade deficits.

## 4. Methods

Two adult macaques (9–11 kg) were implanted with head-posts and chambers giving access to FEF (chamber angled 30° lateral, aimed 18 mm lateral, 25 mm anterior to interaural) and SC (chamber angled 38° posterior, aimed at midline 15 mm above and 1 mm posterior to interaural). Both monkeys ran two interleaved tasks:

- **Delayed visually guided saccade task.** Fixate central spot 500 ms, peripheral target appears, monkey holds fixation 1–2 s, central spot extinguishes, monkey saccades to target. Target locations varied to map saccade latency and peak velocity across the visual field — provides the independent benchmark.

- **Covert motion-change detection.** Two random-dot-motion patches (3° radius, 8–10° eccentricity, mirror-symmetric across fixation) appear during fixation. Dot-direction draws come from $\mathcal{N}(\text{mean}, 16°)$. On 66% of trials, one patch's mean direction changes 1–3 s after onset. Monkey releases joystick within 300–800 ms to report. Joystick release is *spatially neutral* — the perceptual choice is dissociated from the motor output. Foveal-attention (FA) control trials require the monkey to report a fixation-luminance change while *ignoring* peripheral motion changes — a control on attention allocation.

**Causal manipulation.** Reversible inactivation by muscimol (5 mg/mL, GABA-A agonist). SC: 0.3–0.5 μL ($n = 46$ sessions; monkey 1: 18, monkey 2: 28). FEF: 1.5–3.0 μL ($n = 23$ sessions; monkey 1: 8, monkey 2: 15). FEF volume larger to compensate for FEF's coarser retinotopic map and larger physical extent; this produced scotomas matched on retinotopic extent and stimulus overlap. Sham controls ($n = 30$, including saline). Injection sites pre-localized by single-unit recording and electrical microstimulation (FEF 40 μA, SC 20 μA, 70 ms train, 350 Hz, biphasic 0.25 ms pulses) to confirm FEF or SC intermediate layers.

**Quantification.** For each session, compute (i) *detection-rate asymmetry* between affected and unaffected hemifields, before vs during inactivation, and the change induced by inactivation; (ii) *saccade-latency asymmetry* and *peak-velocity asymmetry* between hemifields under inactivation. Relate the two via orthogonal linear regression and via logistic regression (probability of significant attention deficit as a function of saccade-metric change). Bootstrap-resampled slope tests; Wilcoxon rank-sum for slope and bin-wise comparisons.

## 5. Results

- **Psychometric shifts.** In example experiments, full psychometric curves shifted rightward (higher detection thresholds) for changes in the affected hemifield during both SC and FEF inactivation (both p < 0.001). Detection thresholds slightly *decreased* in the unaffected hemifield (SC before 21.7, during 19.2, p < 0.001; FEF before 15.0, during 13.8, p < 0.001).
- **Saccade benchmark — examples.** In an example SC experiment, saccade latencies were 259 ± 9 ms (affected) vs 175 ± 8 ms (unaffected); in an example FEF experiment, 291 ± 9 ms (affected) vs 175 ± 7 ms (unaffected). Comparable disruption.
- **Reproducibility.** Significant detection-threshold increases inside the affected hemifield in 3/3 SC experiments and 4/5 FEF experiments with full psychometric curves; complementary decreases outside in 3/3 SC and 4/5 FEF.
- **Aggregate population.** Across 46 SC + 23 FEF + 30 sham sessions: detection-rate asymmetry changes were large and consistent in SC, smaller in FEF, near zero in sham.
- **Linear regression (detection-deficit vs saccade-latency asymmetry).** SC slope 0.31 ± 0.03 (df = 45, $R = 0.83$); FEF slope 0.08 ± 0.03 (df = 22, $R = 0.70$). Slope difference significant at p < 0.001.
- **Linear regression (detection-deficit vs saccade-velocity asymmetry).** SC slope 0.06 ± 0.01 ($R = 0.78$); FEF slope 0.02 ± 0.01 ($R = 0.68$). Slope difference p < 0.001.
- **Logistic-regression thresholds.** SC reliably impairs attention at saccade-latency asymmetries of 50–75 ms and velocity asymmetries of 250–350°/s. FEF requires 100–150 ms and 350–500°/s respectively. The FEF threshold is ~2× the SC threshold in latency and ~1.5× in velocity.
- **Subsample control.** Randomly subsampling 23 SC sessions to match the FEF sample size 1000 times: SC slope > FEF slope in 999/1000 (latency) and 998/1000 (velocity) draws; SC logistic midpoint < FEF midpoint in 999/1000 (latency).
- **Scotoma matching.** No significant differences (Wilcoxon rank-sum) between SC and FEF in scotoma center-to-stimulus distance (p = 0.64), stimulus-scotoma overlap (p = 0.46), or scotoma area (p = 0.08).

## 6. Critique / limitations

The result establishes a *quantitative asymmetry* but does not establish *mechanism*. The paper's discussion offers candidate explanations — FEF as evolutionarily newer specialization for foveal-vision-in-primates, SC as evolutionarily older substrate closer to action selection — without testing them.

**Visually guided vs memory-guided saccades.** The authors use visually guided saccades as their benchmark. The FEF is known to be especially important for memory-guided saccades; using memory-guided saccades would have produced larger FEF-induced saccade deficits without changing the attention-task effects, *amplifying* the SC > FEF asymmetry. The authors argue this strengthens their conclusion, and the argument is sound, but the asymmetric reliance of the two regions on different saccade types remains a confound to interpret precisely.

**Attention-related vs saccade-related neurons in FEF.** In FEF, attention-related neurons (supragranular layers) and saccade-related neurons (infragranular) may be partially dissociated cell populations. The authors note that GABA-A receptors are present across all cortical layers and that muscimol spread (≥2 mm radius) should suppress both populations — but the inference that the saccade-deficit benchmark indexes attention-related neuronal suppression *equally well in FEF and SC* is load-bearing and not directly verified.

**Task type.** The covert motion-change detection task may favor SC over FEF. The authors acknowledge that tasks requiring foveal-shift planning (rather than covert detection during fixation) might reveal larger FEF effects. The SC > FEF result, then, is specific to this *class* of covert attention, not a global statement about FEF's role.

**Two animals.** Standard for primate neurophysiology but limits inference about population-level generality.

**The "bias the competition" framing.** The improvement in the unaffected hemifield during inactivation is interpreted as biased-competition unmasking, but the same data pattern could arise from baseline-shift, criterion-shift, or reward-allocation accounts. The paper does not distinguish these.

**Pharmacology vs activity-specificity.** Muscimol is a broad GABA-A agonist that suppresses all activity in its volume of spread, not just task-relevant activity. The "SC has a larger effect" conclusion is therefore strictly about *suppression of total local activity* in the two regions, not about suppression of a specific functional sub-population. Optogenetic targeting (cf. mouse SC work, e.g., Hu & Dan 2021) is the next-generation refinement.

**No FEF-SC simultaneous inactivation.** A natural follow-up — does FEF + SC joint inactivation produce a super-additive deficit, or do they converge on the same downstream computation? — is not pursued. The paper's framing assumes additive/independent contributions but does not test the assumption.

## 7. Connection to our work

This paper supplies a *direct, quantitative* anchor for several architectural and experimental decisions in the user's program.

**Twin cortical/subcortical perturbations in the recurrent ViT.** The recurrent ViT (2502.10955) treats its attention map as the AI homolog of primate spatial-attention substrates. Bollimunta et al. 2018 establishes that the two principal primate sources — FEF (cortical) and SC (subcortical) — have *quantitatively different* causal contributions when measured against a common task. The user's twin-perturbation experiment design (perturbing the attention computation in different ways, analogous to FEF vs SC microstimulation/inactivation) is biologically warranted: the brain itself has parallel attention substrates with measurably distinct effect sizes. Future recurrent-ViT perturbation experiments should explicitly target this asymmetry — perturbations on the central self-attention substrate (the SC analog) should be predicted to produce *larger* behavioral deficits than perturbations on the top-down feedback projection from a memory hub (the FEF analog).

**Asymmetric weighting in the multi-hub system.** The multi-hub multi-objective system ([multi_hub_multi_objective_system](../concepts/multi_hub_multi_objective_system.md)) posits MSI, RL, and VAE hubs all feeding back into a central self-attention substrate. Bollimunta et al. 2018 suggests that the central substrate (SC analog) is *more critical* than any single hub's contribution (FEF analog) — i.e., the user's competition-emergent-PC account ([competition_emergent_predictive_coding](../concepts/competition_emergent_predictive_coding.md)) is consistent with a structural commitment in which the central self-attention substrate is the bottleneck through which hub influence is gated. Hubs compete *for* the central substrate; loss of the central substrate is more devastating than loss of any one hub. This is an architectural prediction the user's ablation experiments should test.

**Saccade-metric-as-benchmark methodology.** The paper's methodological move — using an independently observable "motor metric" to calibrate the strength of a causal manipulation — translates directly to the user's program. Ablations of the feedback transformer's connections to different hubs ([feedback_transformer](../concepts/feedback_transformer.md)) should be calibrated against an independent "motor" metric (e.g., next-step prediction error on a downstream RL task) before comparing their effects on attention-map quality. Without such a common benchmark, ablations of structurally heterogeneous components (e.g., a small subcortex-like hub vs a large cortex-like hub) cannot be fairly compared — exactly the problem this paper solved at the primate level.

**Krauzlis lab continuity.** This is a Krauzlis-lab paper. The user's prior co-author work with Herman & Krauzlis 2017 ([herman_krauzlis2017_sc_change_detection](herman_krauzlis2017_sc_change_detection.md)) on SC change detection sits in the same intellectual lineage; Bollimunta et al. 2018 is the *cross-region comparison* that contextualizes the SC-only findings of Herman & Krauzlis 2017. The user's program inherits the lab's commitment to causal manipulation as the gold standard for attribution of function — a commitment the ablation methodology in the recurrent ViT paper directly implements.

**Connection to Krauzlis 2013 review.** Krauzlis, Lovejoy & Zénon 2013 ([krauzlis2013_sc_attention](krauzlis2013_sc_attention.md)) argued that SC's contribution is partially independent of cortical mechanisms. Bollimunta et al. 2018 strengthens this: not only is the SC contribution partially independent, it is *larger* on this benchmark — the SC is not a downstream relay of cortical attention signals but a co-equal (or even dominant) substrate. The user's architecture should not be designed as cortex-dominant with subcortical relay; the central self-attention substrate must be a first-class, possibly dominant, computational element.

**Predicted ablation pattern.** A specific prediction for the recurrent ViT change-detection benchmark (2502.10955 §6.7): if perturbations to the central attention computation (SC analog) and to the feedback-projection pathway from the memory hub (FEF analog) are calibrated against a common "motor" benchmark (e.g., reconstruction loss or next-step decoder loss), the central-attention perturbation should produce a steeper degradation curve. This is a direct empirical analog of the Bollimunta result, ripe for testing.

## 8. Citations to follow

- `lovejoy_krauzlis2010_inactivating_sc` — Lovejoy & Krauzlis SC inactivation; the methodological precursor for the SC arm. Not yet in seed.
- `zenon_krauzlis2012_attention_deficits` — Zénon & Krauzlis quantitative attention deficits during SC inactivation. In seed.
- `wardak2006_fef_inactivation` — Wardak FEF muscimol inactivation in visual search; FEF-arm precursor. Not yet in seed.
- `monosov_thompson2009_fef_attention` — FEF attention vs saccade neurons across cortical layers, relevant to the supragranular/infragranular dissociation cited in §6. Not yet in seed.
- `bogadhi_bollimunta2018_fef_smooth_pursuit` — companion work on FEF inactivation and smooth pursuit by same group. Not yet in seed.
- `bogadhi_bollimunta2019_sc_fmri` — fMRI accompaniment to the SC inactivation data. Not yet in seed.
- `schall_thompson1999_fef_target_selection` — FEF target-selection foundational work. Not yet in seed.
- `mcpeek_keller2004_sc_target_selection` — SC target-selection foundational work. Not yet in seed.
