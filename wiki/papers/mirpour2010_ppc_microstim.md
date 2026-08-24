---
id: mirpour2010_ppc_microstim
title: "Microstimulation of posterior parietal cortex biases the selection of eye movement goals during search"
authors:
  - "Mirpour, Koorosh"
  - "Ong, Wei Song"
  - "Bisley, James W."
year: 2010
venue: "Journal of Neurophysiology"
doi: "10.1152/jn.00397.2010"
arxiv: ""
url: "https://doi.org/10.1152/jn.00397.2010"
tags:
  - primate-neurophysiology
  - parietal-cortex
  - lesion-microstimulation
  - visual-attention
concepts:
  - microstimulation
  - priority-map
  - top-down-feedback
  - cueing-effect
related:
  - bisley_goldberg2010_parietal_priority
  - bisley_mirpour2019_priority_map
  - moore_armstrong2003_fef_microstim
  - cavanaugh_wurtz2004_sc_change_blindness
  - bollimunta2018_fef_sc_covert
  - krauzlis2013_sc_attention
  - cutrell_marrocco2002_ppc_microstim
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_66
status: full
depth: full
last_updated: "2026-05-16"
---

# Microstimulation of posterior parietal cortex biases the selection of eye movement goals during search

## 1. Abstract

Mirpour, Ong & Bisley (2010) test whether the lateral intraparietal area (LIP) of posterior parietal cortex (PPC) functions as a priority map governing target selection during free visual search. Two macaques performed a foraging-style search task in which several visually identical stimuli were arrayed across the display and the animal made unprompted saccades to inspect them in sequence. On a subset of trials, weak electrical microstimulation was delivered to a single LIP site at subthreshold currents — below the level required to evoke a saccade by stimulation alone — during the inter-saccadic fixation periods preceding goal selection. Stimulation produced a small but reliable bias in the animals' choice of next saccade goal: search targets near the retinotopic location encoded by the stimulated LIP site were selected more often than predicted by the no-stimulation baseline. The bias did not appear as an evoked saccade with stimulation-determined endpoint; rather it shifted the probability distribution over self-selected goals. The effect was consistent across stimulus configurations, demonstrating that LIP microstimulation biases goal *selection* rather than driving the saccade motor command directly. The result is causal evidence that LIP activity contributes to which target the oculomotor system chooses, supporting the priority-map account.

## 2. Why this matters for us

This paper is the parietal entry in the triad of causal microstimulation studies that license the recurrent ViT's perturbation methodology — Moore & Armstrong 2003 (FEF), Cavanaugh & Wurtz 2004 (SC), and Mirpour et al. 2010 (PPC/LIP). Each demonstrates that subthreshold electrical perturbation of a priority-map substrate biases attentional selection without dictating the motor act. The recurrent ViT (arXiv:2502.10955) reports an analogous result in silico: a graded perturbation of the self-attention map at a chosen spatial location shifts which target the model selects, without overriding the decoder's output. Mirpour et al. is the closest of the three precedents to the user's program because it is *parietal* — and the user's central self-attention substrate ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) is structurally a cortical priority map of the Bisley-Goldberg type, fed by many hubs and read out by downstream selection. The fact that microstimulation of LIP biases goal selection during *free search* — not a cued task — is the cleanest published analog of the recurrent ViT's selection behavior on its change-detection task.

## 3. Key claims

1. Subthreshold microstimulation of LIP biases the probability with which the animal selects the corresponding retinotopic location as its next saccade goal during free visual search.
2. The bias is a shift in goal *selection*, not an evoked saccade: stimulation does not trigger a saccade to a fixed endpoint determined by current; it shifts the distribution over self-generated goals.
3. The effect is consistent across stimulus configurations and target identities — the bias rides on top of the animal's task-driven search behavior rather than overriding it.
4. The result is the causal complement to LIP single-unit data: LIP activity at a location not only *correlates* with that location's priority but *contributes to* the downstream selection.
5. LIP therefore satisfies the operational definition of a priority map: a representation whose activity at each location is read out by the oculomotor (and, by extension, the attentional) system to determine selection.
6. The magnitude of the bias is small in absolute terms — a modest probability shift, not a deterministic capture — consistent with LIP being one of several parallel priority-map substrates (FEF, SC, pulvinar) that jointly determine selection.
7. The effect is *contextual*: it operates during the inter-saccadic planning window, when the priority map is being read out for the next saccade, not during fixation periods unrelated to goal selection. The timing specificity supports the interpretation that LIP activity contributes to selection at the *readout* stage rather than altering global arousal or motor readiness.

## 4. Methods

**Task.** Two macaques performed a foraging-style free-search task. Multiple visually identical stimuli were arrayed across the display; the animal was rewarded for finding a hidden target by inspecting stimuli with sequential saccades. Because the stimuli were identical, the animal's choice of next goal was driven by internally generated priority rather than by bottom-up feature distinctiveness — a clean readout of the priority map's contribution to selection.

**LIP mapping.** Each recording site in LIP was characterized electrophysiologically: the response field (RF) of neurons at the site was mapped using standard memory-saccade and visual-response paradigms. The retinotopic location encoded by the site was thus known prior to stimulation.

**Microstimulation protocol.** Weak electrical pulses (biphasic, sub-saccade-threshold currents — well below the level at which stimulation alone evokes a saccade) were delivered during the inter-saccadic fixation period preceding the animal's next goal selection. Stimulation timing was locked to the post-saccadic fixation onset, so it occurred during the planning window for the next saccade. On control trials, no stimulation was delivered.

**Dependent measure.** The choice probability of each search stimulus as the next saccade goal, as a function of its retinotopic distance from the stimulated LIP site's RF. Comparison: stim vs no-stim trials, matched for current task state.

**Controls.** Stimulation that was suprathreshold for saccade evocation was avoided. The analysis is restricted to trials in which the saccade endpoint reflected free choice, not stimulation-driven motor capture. Sessions and sites are pooled across multiple LIP recording locations and across multiple foraging arrays to ensure generalization. The dependence of the bias on retinotopic distance between the stimulated RF and each candidate stimulus serves as an internal control: locations far from the RF should show no effect, and the gradient of the effect with distance is itself a signature of priority-map readout.

**Behavioral baseline.** Each animal's spontaneous choice distribution across the array — driven by remembered target locations, search history, and visual salience — was characterized on no-stim trials before, after, and interleaved with stim trials. Comparison of stim vs no-stim distributions within sessions controls for changes in the animal's strategy or motivation across the recording session.

## 5. Results

The principal quantitative findings:

- **Selection bias toward the stimulated RF.** On microstimulation trials, the probability of the next saccade landing near the LIP site's RF increased, relative to the no-stim baseline. The shift is small in absolute magnitude — on the order of a few percentage points — but reliable across sites and animals.
- **No evoked-saccade endpoint.** Stimulation did not produce saccades with a fixed, stimulation-determined endpoint. The saccades landed on one of the array's search stimuli, just preferentially on stimuli near the stimulated location.
- **Consistency across configurations.** The bias appeared regardless of the spatial arrangement of search stimuli or which stimulus was the hidden target on a given trial. The effect therefore reflects a *general* increase in the priority assigned to the stimulated location, not a stimulus-specific or task-specific artifact.
- **Spatial specificity.** Stimuli closer (in retinotopic terms) to the stimulated LIP RF were preferentially selected; stimuli far from the RF were unaffected.
- **No reaction-time disruption.** The animals' search progressed at similar tempo on stim and no-stim trials; the stimulation biased *which* target was chosen, not *how quickly* the next saccade was launched.
- **Bias persists across stimulus identity.** Whether the hidden target was at the stimulated location or elsewhere, the bias toward the stimulated RF held. This rules out the possibility that LIP stimulation amplifies a feature-specific signal; the effect is on spatial priority directly.
- **No carryover to subsequent fixations.** The bias is restricted to the saccade immediately following stimulation. Saccades two and three steps later do not show a sustained bias, indicating that LIP microstimulation contributes to the immediate priority readout rather than altering longer-term search strategy.

The combination — selection bias, no motor capture, spatial specificity, no tempo disruption — is the signature of a *priority-map* perturbation: the stimulated activity is read out as a contribution to the priority distribution but does not override the selection mechanism itself.

## 6. Critique / limitations

The magnitude of the bias is small. A skeptic could argue that LIP microstimulation produces only a marginal contribution to selection, and that the dominant determinants of saccade goals are elsewhere (FEF, SC, or task-context signals from PFC). Mirpour et al. acknowledge this; their position is that LIP is *one of* several parallel priority-map substrates, and that the modest size of the effect is consistent with shared causation rather than against LIP's causal role.

Electrical microstimulation activates fibers of passage as well as local LIP neurons. The result therefore does not unambiguously localize the effect to LIP cell bodies; afferent or efferent fibers passing through the LIP at the stimulation site could in principle mediate part of the bias. Subsequent optogenetic and pharmacological-inactivation work has refined the cellular specificity, but the original microstimulation paradigm has this caveat.

The task is *free search* with identical stimuli, which is the cleanest readout of priority-map function but also a relatively narrow behavioral regime. Whether the same LIP perturbation biases selection in cued attention paradigms, in feature-search tasks with distinguishable stimuli, or in non-saccadic covert-attention paradigms is not directly addressed by this study (though Bisley & Goldberg's broader literature establishes the cued-attention case).

The selection bias is reported as a probability shift averaged over many trials. The *trial-by-trial* dynamics of how stimulation interacts with ongoing priority computation are not characterized — a more recent generation of work (Bisley & Mirpour 2019 review) addresses this question with finer-grained analyses.

The study does not engage with the question of whether the LIP contribution is mediated through downstream SC, through direct LIP→FEF projections, or through both. The causal chain from LIP perturbation to saccade goal is therefore established at the input (LIP) and output (selection) ends but not in between.

The result is bilateral-LIP-naive: only one hemisphere is stimulated at a time. Bilateral or contralateral-control stimulation might separate spatially specific from generic-arousal contributions. This is a methodological gap rather than a substantive concern.

A subtler interpretive question: is LIP's contribution to selection *necessary*, or merely *sufficient*? Microstimulation establishes sufficiency — that perturbing LIP activity biases selection — but does not establish that LIP is required for selection in normal behavior. Inactivation studies (pharmacological LIP silencing) are required for the necessity claim, and the relevant data come from subsequent work rather than from this paper. The asymmetry matters for the recurrent ViT analogy: the model's perturbation experiments demonstrate sufficiency of the attention map for selection, but a complementary set of *ablation* experiments (zeroing or uniformly setting the attention map) is required to demonstrate necessity. The user's program plans both kinds of manipulation.

The effect's directional consistency — bias toward, not away from, the stimulated RF — assumes that LIP activity codes priority by elevation. An alternative interpretation, in which LIP encodes inhibition-of-return or some other signal whose increase would suppress selection, is ruled out by the directionality observed. This is a clean piece of evidence on the *sign* of LIP's contribution to selection, even if its magnitude is modest.

## 7. Connection to our work

The recurrent ViT paper (arXiv:2502.10955) reports a class of perturbation experiments in which the model's self-attention map is artificially biased at a chosen spatial location and the downstream behavioral effects (response rate, reaction time, accuracy) are measured. The paper explicitly maps these manipulations to primate microstimulation experiments — Moore & Armstrong 2003 (FEF, [moore_armstrong2003_fef_microstim](research_db/papers/moore_armstrong2003_fef_microstim.md)) and Cavanaugh & Wurtz 2004 (SC, [cavanaugh_wurtz2004_sc_change_blindness](research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md)). Mirpour et al. 2010 is the third member of this triad, supplying the PPC/LIP causal precedent. All three are *subthreshold microstimulation of a priority-map substrate that biases selection without dictating motor output* — exactly the experimental design the recurrent ViT translates into the AI domain.

**Direct precedent for the recurrent ViT's perturbation methodology.** The recurrent ViT's biased-attention experiment biases the self-attention weight at one quadrant during the maintenance window and measures the shift in which target the model selects. Mirpour et al.'s LIP microstimulation biases the priority assigned to one retinotopic location during the pre-saccadic planning window and measures the shift in which target the animal selects. The two experiments are formally equivalent in their causal logic.

**Parietal substrate for the central self-attention map.** The user's central self-attention substrate ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) plays the role of a shared priority map fed by many hubs. Bisley-Goldberg 2010 supplies the framework; Mirpour et al. 2010 supplies the causal demonstration that perturbing this kind of map biases selection — i.e., that the architectural design is functionally consequential, not merely descriptive.

**Free-search task as a model for self-driven selection.** Unlike Moore & Armstrong (cued attention, fixation task) and Cavanaugh & Wurtz (change-blindness paradigm with explicit transients), Mirpour et al. use *free search* — the animal generates its own saccade sequence without external cues. This is the closest behavioral analog to the recurrent ViT's change-detection task, in which the model must internally allocate attention across multiple visual targets without explicit cueing. The user's program ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §4–5) treats internally-driven selection as the central computational problem; Mirpour et al. is the cleanest neurophysiological referent.

**Graded perturbation, not motor capture.** A central methodological point in 2502.10955 §6.6 is that the attention-perturbation experiments use *graded* biases rather than hard clamps — the model's selection is shifted, not overridden. This matches Mirpour et al.'s subthreshold protocol precisely: stimulation shifts the selection distribution, no saccade is evoked outright. The architectural commitment in the Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) — multiplicative integration of feedback into Q/K — naturally produces this kind of graded biasing rather than all-or-nothing override.

**Parallel priority-map substrates and coalition competition.** Mirpour et al.'s observation that the effect is modest fits the user's [competition-emergent-predictive-coding](research_db/concepts/competition-emergent-predictive-coding.md) framing: priority is computed jointly by many coalitions (LIP, FEF, SC, pulvinar in the brain; MSI/RL/VAE hubs in the user's architecture), and no single source dominates. Perturbing one source produces a proportional but not exhaustive bias — a prediction the user's multi-hub architecture should reproduce.

**Future P5-style experiments.** The PROJECT_PLAN.md Phase 5 microstimulation analog experiments — clamping the recurrent ViT's attention weights and observing downstream effects — should explicitly cite Mirpour et al. as the PPC precedent for the *free-search* variant of the protocol (as distinct from cued-task variants modeled on Moore & Armstrong, or change-detection variants modeled on Cavanaugh & Wurtz). Concretely, a free-viewing variant of the perturbation experiment — in which the model is given a multi-stimulus display and must internally select targets in sequence — would map cleanly to Mirpour's foraging task. The prediction is that biasing the recurrent ViT's attention weight at one quadrant should shift selection probability toward that quadrant by a small but reliable margin, with no override of the model's selection mechanism, matching the modest LIP-microstimulation effect size.

**Modest effect size as a sanity check, not a defect.** A naive reading would treat a small behavioral shift as a weak result. The user's program inverts this: a *modest* shift from a single-source perturbation is exactly what a multi-source priority map should produce. If the recurrent ViT's biased-attention manipulation produced an exhaustive selection capture, that would suggest the model has collapsed to a single source of priority — a failure of the multi-hub architecture. Mirpour et al. provides the calibration: in real cortex, single-substrate perturbation produces probability shifts of a few percentage points, not deterministic selection.

## 8. Citations to follow

- `bisley_mirpour2019_priority_map` — Bisley & Mirpour's follow-up review of neural priority maps. In seed.
- `bisley_goldberg2010_parietal_priority` — companion review establishing the priority-map framework. In seed, full depth.
- `moore_armstrong2003_fef_microstim` — FEF microstimulation parallel. In seed, full depth.
- `cavanaugh_wurtz2004_sc_change_blindness` — SC microstimulation parallel. In seed, full depth.
- `cutrell_marrocco2002_ppc_microstim` — earlier PPC microstimulation work; cued-attention paradigm rather than free search. In seed.
- `bollimunta2018_fef_sc_covert` — modern comparison of FEF and SC contributions to covert attention. In seed.
- `krauzlis2013_sc_attention` — SC attention review; broader subcortical context. In seed.
- `mirpour_bisley2012_search_priority` — Mirpour & Bisley follow-up on search and priority dynamics. Not yet in seed; candidate for addition.
- `ipata2006_lip_search` — earlier Bisley-lab paper on LIP activity during free search; methodological precursor. Not yet in seed; candidate for addition.
