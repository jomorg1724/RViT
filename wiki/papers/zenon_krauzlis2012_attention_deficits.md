---
id: zenon_krauzlis2012_attention_deficits
title: "Attention deficits without cortical neuronal deficits"
authors:
  - "Zénon, Alexandre"
  - "Krauzlis, Richard J."
year: 2012
venue: "Nature"
doi: "10.1038/nature11497"
arxiv: ""
url: "https://doi.org/10.1038/nature11497"
tags:
  - primate-neurophysiology
  - subcortical
  - lesion-microstimulation
  - visual-attention
  - change-detection
concepts:
  - pharmacological-inactivation
  - top-down-feedback
  - priority-map
  - signal-detection-theory
  - cueing-effect
related:
  - sridharan2017_sc_sensitivity_bias
  - krauzlis2013_sc_attention
  - cavanaugh_wurtz2004_sc_change_blindness
  - herman_krauzlis2017_sc_change_detection
  - bisley_goldberg2010_parietal_priority
  - moore_armstrong2003_fef_microstim
  - muller2005_sc_microstim_covert
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_69
status: full
depth: full
last_updated: "2026-05-16"
---

# Attention deficits without cortical neuronal deficits

## 1. Abstract

Spatial visual attention modulates neuronal responses throughout the visual cortex, providing a likely neuronal correlate of the perceptual benefits afforded by attention. Recent work has identified the superior colliculus (SC) — a midbrain structure historically associated with eye movements — as critical for the *behavioural* control of spatial attention, raising the question of whether the SC operates by adjusting the well-established cortical signatures of attention or by an independent route. Zénon & Krauzlis trained two macaques on a motion-change-detection task that required covert spatial attention: two moving-dot stimuli were placed in diagonally opposite locations, a cue indicated which stimulus to attend, and the animal reported a brief change in motion direction at the cued location while ignoring a distractor change at the uncued location. Local muscimol injections were used to *transiently inactivate* the intermediate / deep layers of the SC at a site whose movement field overlapped one of the two stimulus locations. They simultaneously recorded single units in motion-sensitive extrastriate cortex (MT / MST). SC inactivation produced *large attention deficits* — sharply reduced hit rates and elevated misses for cued stimuli in the affected hemifield, with little change for the contralateral hemifield. **Yet the standard cortical signatures of attention were entirely preserved**: cue-driven firing-rate enhancement, attention-modulation indices, neuronal ROC discriminability, Fano factors and pairwise noise correlations in MT / MST were statistically indistinguishable from the no-inactivation baseline. The authors conclude that the SC contributes to spatial attention through mechanisms that are *independent* of the classic attentional gain signature in visual cortex.

## 2. Why this matters for us

This is one of the *four seminal SC-manipulation studies* re-analyzed by Sridharan et al. 2017 (`sridharan2017_sc_sensitivity_bias`) and is the *cleanest published demonstration* of a behaviour-cortex dissociation in attention: a focal causal manipulation produces large behavioural deficits *without* changing the textbook cortical attention signature.

For the user's program this paper supplies:

- **Hard empirical evidence that attention is not implemented by a single substrate.** Different hubs contribute different functional components and can be dissociated by focal manipulation.
- **The specific result that the SC contributes the *bias* component of signal-detection-theory attention while cortex (V4 / MT) contributes the *sensitivity* component.** This is the seminal data point that Sridharan et al. 2017 generalize to a four-study claim.
- **A direct architectural prediction.** A model that recruits a single attention substrate cannot reproduce this dissociation. The recurrent ViT's SC-analog should therefore be implemented as a separate bias-contributing hub rather than as further modulation of the cortical-analog attention map.
- **An *in-silico* dissociation experiment**: ablate the SC-analog hub and look for the same cortex-preserved-behaviour-impaired signature. The change-detection paradigm of Cavanaugh & Wurtz 2004 and Herman & Krauzlis 2017 — the recurrent ViT's task setting — is the natural in-silico vehicle.

## 3. Key claims

1. **SC is causally necessary for normal covert spatial attention.** Muscimol inactivation of the intermediate / deep SC produces selective, large attention deficits at locations represented by the inactivated SC site.
2. **Cortical attention signatures are preserved despite the behavioural deficit.** Cue-driven firing-rate enhancement, attention-modulation indices, neuronal ROC discriminability, Fano factors, and pairwise noise correlations in MT / MST are unchanged by SC inactivation.
3. **The cortex-SC routes are functionally dissociable.** The dissociation between unchanged cortical attentional modulation and impaired behaviour implies that the SC's attentional contribution operates through a route that is not reflected in standard cortical gain signals.
4. **The classic cortical-modulation account of attention is therefore *incomplete*.** Whatever produces the cue-driven gain in MT / MST is *not sufficient* for normal attentional performance; a parallel SC-mediated mechanism is required.
5. **Implication for the locus of control.** The behavioural deficit's pattern is consistent with the SC contributing a *spatial selection / priority* signal rather than a sensory-gain signal — anticipating the bias-not-sensitivity interpretation that Sridharan et al. 2017 later makes formal under multialternative SDT.

## 4. Methods

**Behavioural task.** Two macaques performed a Posner-style covert spatial-attention task with a motion-change report. On each trial the animal fixated centrally while two patches of moving random dots were presented in diagonally opposite peripheral locations. A small central cue indicated which of the two patches was task-relevant. After a variable delay one (or both) patches underwent a brief change in motion direction; the animal released a lever (or made a saccade-free response) when the *cued* patch changed and withheld responding when only the *uncued* patch changed. The two-patch geometry makes the task a classic two-alternative spatial-attention probe with measurable hit rates, false-alarm rates and reaction times.

**SC inactivation.** A guide tube + injectrode assembly delivered small volumes of the GABA-A agonist *muscimol* (sub-microlitre) to the intermediate / deep layers of the SC at a site whose visuomotor response field overlapped one of the two stimulus locations. Inactivation extent was *operationally verified* by mapping saccade velocities across the visual field — sub-normal peak velocities into the affected field confirm a functional lesion of the targeted SC zone. Behaviour and recordings were compared between pre-injection (or vehicle / no-injection) trials and post-injection trials in the same session.

**Simultaneous cortical recordings.** Single-unit and multi-unit activity was recorded from extrastriate motion-processing cortex (MT and MST) using standard electrophysiology, with receptive fields positioned to overlap the visual stimuli. Standard attention-related response metrics were computed: cue-driven mean firing-rate enhancement, attention-modulation index ($\text{AMI}=(R_{\text{att}}-R_{\text{unatt}})/(R_{\text{att}}+R_{\text{unatt}})$), neuronal ROC discriminability between attended-vs-unattended conditions, Fano factor of spike-count variability, and pairwise spike-count noise correlations across the recorded population during the delay epoch.

**Comparisons.** For each metric the authors compared (i) attended-vs-unattended within the no-inactivation condition and (ii) the *change* in that attention effect produced by SC inactivation. The critical statistical test is whether SC inactivation reduces the attention-related modulation in cortex — the null result on this test is the paper's main finding.

## 5. Results

The principal quantitative findings:

- **Behaviour.** SC inactivation reduced hit rates for the cued stimulus in the affected hemifield substantially (large effect sizes) while leaving uncued / contralateral performance comparatively unchanged. False alarms to the uncued patch in the affected field were elevated, consistent with a loss of spatially-selective gating. The selectivity is anatomically tight — the deficit follows the SC site's visual field representation as mapped by saccade-velocity assays.
- **Cortical firing rates: unchanged.** Mean cue-driven firing-rate enhancement in MT / MST was statistically indistinguishable from the no-inactivation condition. Attention-modulation indices showed no significant reduction.
- **Discriminability: unchanged.** Neuronal ROC area for attended-vs-unattended trials — the conventional discriminability metric — was not reduced by SC inactivation.
- **Variability: unchanged.** Fano factors were unchanged. Pairwise noise correlations during the delay epoch were unchanged.
- **Dissociation.** Behavioural attention effect: large reduction. Cortical attention effect: no reduction. The two normally co-vary trial-by-trial in the no-inactivation condition; SC inactivation breaks the link.

The summary table that emerges:

| Measure | Direction in no-inactivation cue-attention | Effect of SC inactivation |
| --- | --- | --- |
| Hit rate at cued contralateral location | High | Sharply reduced |
| False-alarm rate at uncued contralateral location | Low | Elevated |
| MT/MST cue-driven firing-rate enhancement | Present | Preserved |
| MT/MST attention-modulation index | Positive | Preserved |
| MT/MST neuronal ROC discriminability | Higher in attended | Preserved |
| MT/MST Fano factor | Lower in attended | Preserved |
| MT/MST pairwise noise correlations | Lower in attended | Preserved |

The behaviour column is fully consistent with a *bias* deficit — the animal can no longer preferentially read out the cued location — while every cortical measure of attentional gain on the representation of that location is intact.

## 6. Critique / limitations

The recordings are from motion-sensitive extrastriate areas (MT / MST), not from V4. Subsequent literature sometimes refers to the result as showing preserved "V4-style" attention modulation, but the actual recordings target the motion-processing stream appropriate for the motion-change task. Whether the same dissociation holds in V4 for colour / form attention tasks must be inferred. (Herman & Krauzlis 2017 then complements this on the SC-side by showing colour-change-detection activity in the SC itself.)

The unchanged-cortex result is a *null* result on cortical attention modulation. Statistical power for the null is partially addressed (large $n$ trials and units, multiple metrics), but the paper cannot rule out small residual changes below detection.

The muscimol inactivation is *focal*; SC retains substantial intact tissue. The interpretation is therefore *necessity of this SC zone for normal attention*, not "the SC alone implements attention". A complete bilateral SC silencing might produce different cortical effects.

The two-alternative geometry conflates spatial selection with stimulus-discriminability mechanisms. Sridharan et al. 2017 explicitly addresses this by re-fitting the data under a *multialternative* SDT framework and shows that the SC effect partitions onto the *choice-bias* parameter, not the sensitivity parameter — a much sharper claim than this paper made.

The paper does not record from sources upstream of MT / MST that could supply attentional gain (FEF, LIP, pulvinar). It is therefore agnostic about the *route* by which SC inactivation produces the behavioural deficit — whether the SC contribution is via direct premotor / response-selection pathways, via pulvinar back to cortex without affecting the recorded gain metrics, or via a third route.

## 7. Connection to our work

This paper is *structurally important* for the user's architectural program in three ways.

**(a) Architecture-level evidence for multi-hub attention.** The behaviour-cortex dissociation directly motivates the user's commitment to a *multi-hub-multi-objective-system* (`the_user_architectural_program` §5): no single substrate implements attention; different hubs contribute different functional components and may dissociate under causal manipulation. A model in which one attention map fully determines behaviour cannot reproduce this dissociation. The recurrent ViT (2502.10955) currently uses a *single* attention substrate; a clean architectural translation of Zénon & Krauzlis 2012 would split attention into at least two contributors — a cortex-analog gain on the value path of the Feedback Transformer, and an SC-analog *bias hub* whose contribution does not enter via gain on representational units.

**(b) Bias-not-sensitivity at the implementation level.** Sridharan et al. 2017 (`sridharan2017_sc_sensitivity_bias`) re-analyzed this paper under multialternative SDT and concluded that the SC contributes *choice bias*, not sensitivity. Combined with the present paper's finding of preserved cortical gain, the natural architectural prediction is: SC-analog hubs should add their contribution *downstream* of representational encoding, into the decision / readout, rather than upstream as multiplicative gain on $V$. In Feedback-Transformer terms, the SC-analog hub would contribute primarily through the actor / readout pathway or through an additive shift on $Q\cdot K$ that biases *selection* without changing the representational discriminability of $V$. This is a falsifiable architectural commitment: a model whose SC-analog operates only via $V$-gain should *not* exhibit the cortex-preserving behavioural deficit under SC-analog ablation.

**(c) Specific prediction for SC-analog ablation in the recurrent ViT.** If the user introduces an SC-analog bias hub into the recurrent ViT, the following pattern should hold under hub ablation: ablating the cortex-analog gain pathway should reduce both behavioural performance and the attention-map gain signature; ablating the SC-analog bias hub should reduce behavioural performance *without* reducing the attention-map gain signature. This is the direct in-silico analog of Zénon & Krauzlis's dissociation and would constitute strong evidence that the model captures the multi-hub structure of biological attention. The change-detection paradigm (Herman & Krauzlis 2017; Cavanaugh & Wurtz 2004) is the natural task setting because it is the closest published precursor of the recurrent ViT's task and is one of the four tasks re-analyzed by Sridharan et al. 2017.

**(d) Connection to priority-map literature.** Bisley & Goldberg 2010 (`bisley_goldberg2010_parietal_priority`) place LIP as a cortical priority map; the present paper places the SC as a *parallel* priority structure whose contribution is not exhausted by cortical gain. The user's architecture should therefore admit *multiple priority maps* — at minimum a cortex-analog and an SC-analog — feeding into the central self-attention substrate via the Feedback Transformer. This is consistent with the user's commitment to *bidirectional-hierarchical-feedback*: priority signals enter as additional feedback streams alongside hierarchical memory states.

The recurrent ViT paper cites this work as reference [69]. Future manuscripts interpreting recurrent-ViT perturbation results should cite this paper as the empirical anchor for the claim that not every behavioural attention effect must show up as a cortical-attention-map effect.

## 8. Citations to follow

- `lovejoy_krauzlis2010_sc_inactivation` — earlier Krauzlis-lab demonstration that SC inactivation impairs target selection without affecting saccade execution; precursor to this paper. Not yet in seed.
- `mcpeek_keller2004_sc_target_selection` — SC inactivation impairs target selection in visual search. Not yet in seed.
- `cohen_maunsell2009_attention_correlations` — the cortical-noise-correlation reduction-with-attention result whose preservation under SC inactivation is the surprising null. Not yet in seed.
- `mitchell2009_v4_noise_correlations` — companion V4 noise-correlation paper. Not yet in seed.
- `treue_maunsell1996_motion_attention` — original MT/MST attentional-modulation finding whose preservation Zénon & Krauzlis demonstrate. Not yet in seed.
- `lovejoy_krauzlis2017_sc_visual_attention` — follow-up establishing the SC role in non-spatial attention. Not yet in seed.
