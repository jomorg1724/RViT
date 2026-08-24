---
id: clark2015_prefrontal_attention
title: "Visual attention: linking prefrontal sources to neuronal and behavioral correlates"
authors:
  - "Clark, Kelsey"
  - "Squire, Ryan Fox"
  - "Merrikhi, Yaser"
  - "Noudoost, Behrad"
year: 2015
venue: "Progress in Neurobiology"
doi: "10.1016/j.pneurobio.2015.06.006"
arxiv: ""
url: "https://doi.org/10.1016/j.pneurobio.2015.06.006"
tags:
  - visual-attention
  - prefrontal-cortex
  - review
  - primate-neurophysiology
  - lesion-microstimulation
concepts:
  - top-down-feedback
  - gain-modulation
  - cueing-effect
  - validity-effect
related:
  - moore_armstrong2003_fef_microstim
  - bisley_goldberg2010_parietal_priority
  - desimone_duncan1995_biased_competition
  - feldman_friston2010_attention_free_energy
  - panichello_buschman2021_shared_mechanisms
  - mante2013_context_dependent_pfc
  - boshra_kastner2022_attention_control
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_2
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual attention: linking prefrontal sources to neuronal and behavioral correlates

## 1. Abstract

Attention is a means of flexibly selecting and enhancing a subset of sensory input based on the current behavioral goals. Numerous signatures of attention have been identified throughout the brain, and experimenters are seeking to determine *which of these signatures are causally related to the behavioral benefits of attention*, and *the source of these modulations within the brain*. Clark et al. review the neural signatures of attention throughout the brain, their theoretical benefits for visual processing, and their experimental correlations with behavioral performance. They emphasize the importance of measuring *cue benefits* as a way to distinguish between impairments on an attention task (which may instead be visual or motor impairments) and *true attentional deficits*. They examine evidence for various areas proposed as sources of attentional modulation within the brain, with a focus on the *prefrontal cortex*. Finally, they review studies that link sources of attention to its neuronal signatures elsewhere in the brain.

## 2. Why this matters for us

Clark et al. 2015 is the canonical *prefrontal-sources-of-attention* review, providing the empirical evidence for treating PFC as the source of top-down attention signals. This is the load-bearing citation for the recurrent ViT's analogy to FEF / dlPFC sources: the recurrent memory state plays the role of PFC's top-down signal source; the Feedback Transformer's attention map is the modulation target. The paper is also the methodological reference for measuring *cue validity effects* — the empirical signature the recurrent ViT replicates and that defines a "true attentional deficit" rather than a generic perceptual or motor failure.

## 3. Key claims

1. **Attention has multiple neural signatures.** Across visual cortex, parietal cortex, FEF, dlPFC, SC, pulvinar, basal ganglia — neural correlates of attention have been observed in many regions. The question is *which* signatures are *causal* and which are *downstream*.
2. **Cue benefits distinguish true attention from confounds.** When a cued (high-validity) trial shows a benefit over a neutral trial, and an invalid (low-validity) trial shows a cost relative to neutral, the effects are *true attentional* in origin. Deficits that don't show cue-validity dependence are likely visual or motor rather than attentional.
3. **PFC is a leading source candidate.** FEF (frontal eye field) and dlPFC (dorsolateral prefrontal cortex) microstimulation experiments produce attention-like behavioral effects (Moore & Armstrong 2003, [moore_armstrong2003_fef_microstim](research_db/papers/moore_armstrong2003_fef_microstim.md)). Their inactivation impairs attention-task performance.
4. **PFC → sensory cortex top-down modulation is the mechanism.** Neural signatures of attention in visual cortex (V4, IT) depend on intact PFC; lesions or pharmacological inactivation of PFC reduces or eliminates these signatures.
5. **The same PFC mechanism supports memory-guided behavior.** The "source signal" from PFC isn't specific to attention; it's about goal-relevant maintenance and selection — which can drive attention, WM-guided behavior, or both.
6. **The framework predicts cue benefits as the diagnostic.** Studies of attention should report cue benefits explicitly; without them, claimed attentional effects could be visual or motor in origin.
7. **Theoretical benefits of attention.** Improvements in target processing, faster RTs, increased d-prime, reduced criterion variability — all are expected behavioral consequences of attention. The paper catalogs which theoretical benefits each empirical signature supports.

## 4. Methods

A narrative review covering primate single-unit, microstimulation, lesion, and pharmacological-inactivation studies of attention. The Noudoost lab's own work and others' contributions are synthesized into a framework that emphasizes:
- **Causal evidence**: microstimulation and inactivation studies as the gold standard for source identification.
- **Cue benefits**: behavioral signatures that distinguish true attention from confounds.
- **PFC sources**: FEF and dlPFC as the strongest source candidates.
- **Functional asymmetry**: source vs target distinction (PFC = source; visual cortex = target).

The review's contribution is the *methodological emphasis on cue benefits* and the *causal-evidence summary* for PFC as the attention source.

## 5. Results

The principal empirical claims the review consolidates:

- **FEF microstimulation** produces attention-like effects in V4 and other visual areas (Moore & Armstrong 2003; Moore & Fallah 2004). Microstim shifts the spatial focus of attention without producing eye movements (when applied at subthreshold currents).
- **FEF inactivation** impairs cued-attention task performance, with the deficit being specific to attention rather than to perception or motor output.
- **dlPFC** also contributes to attention; reversible inactivation impairs WM-guided attention tasks.
- **Cue benefits scale with cue validity** in normal animals and humans; pathological attention conditions (neglect, ADHD) show altered cue-benefit profiles consistent with disrupted attention sources.
- **PFC → V4 functional connectivity** is enhanced during attended-stimulus trials, consistent with PFC providing top-down signals to V4 that modulate the visual response.
- **Pharmacological dissociation.** Dopamine D1 manipulation in dlPFC modulates attention performance, suggesting dopamine signals in PFC contribute to the source-of-attention computation.

## 6. Critique / limitations

The framework focuses on *sources* of attention. The *downstream* mechanisms by which the source signal modulates sensory cortex (precision-weighting, divisive normalization, multiplicative gain) are referenced but not the focus. Subsequent work (Bastos 2012/2015; Spratling 2008; Feldman & Friston 2010) provides the modulatory-mechanism details.

The PFC-source claim is strong for FEF and dlPFC; weaker for other PFC subregions. Some PFC subregions (ACC, OFC) may contribute differently or to different forms of attention.

The framework is *primate-centric*. The mouse-attention literature (where most modern optogenetic work is done) is less developed; the Clark et al. framework may need extension to mouse cortex.

The review predates much of the more recent shared-attention-WM work (Panichello & Buschman 2021). The "source" framing implicitly treats PFC's attention function as distinct from its other roles; subsequent work (Panichello & Buschman) emphasizes a *domain-general controller* role that supports multiple functions.

The framework doesn't engage with *predictive-coding* interpretations explicitly. PFC's role as a *source of priors* (Friston 2005) or *precision controller* (Feldman & Friston 2010) is consistent with Clark et al.'s "source signal" framing but not made explicit.

## 7. Connection to our work

This paper is the canonical reference for the recurrent ViT's PFC analog and for the methodological framework of measuring cue-validity effects:

**The recurrent memory state as the PFC analog.** The recurrent ViT's $H^{(t)}$ plays the role of PFC's top-down signal: it carries goal-relevant information across time, and modulates attention via feedback. Clark et al. supplies the biological precedent: PFC is the source; visual cortex is the target.

**FEF microstim analog.** The recurrent ViT paper (2502.10955 §6.6) reports that targeted perturbations of the attention map produce behavioral effects analogous to FEF microstimulation. Clark et al. supplies the methodological framework for this analogy: FEF is a PFC source for attention; its perturbation produces attention-like behavioral effects.

**Cue benefits as the diagnostic.** The recurrent ViT reports faster RT and higher accuracy at cued locations, with effects scaling with cue validity. Clark et al.'s framework establishes this as the *diagnostic criterion* for true attention: any architectural claim of "attentional" effects in PRISM or related models must report cue-benefit profiles. The user's program is consistent with this requirement.

**PFC's role as goal-relevant maintenance.** The recurrent ViT's recurrent state carries goal-relevant information (the cue location); PRISM v2's slow memory carries task context. Clark et al.'s framing of PFC as a *general goal-maintenance source* (not specific to attention) is compatible with the unified attention-WM substrate the user's program commits to.

**Multi-hub system framing.** In the multi-hub system, the RL hub (analog of dlPFC) and the central self-attention substrate (analog of FEF) together generate the top-down signals that modulate sensory processing. Clark et al.'s emphasis on PFC as the source aligns with the user's architectural commitment.

The recurrent ViT paper cites Clark et al. 2015 in its bibliography (ref [2]). Future manuscripts that argue for the architectural analogy between the recurrent ViT and PFC should cite this paper as the canonical primate-source review.

## 8. Citations to follow

- `moore_armstrong2003_fef_microstim` — the foundational FEF microstim result. In seed, full depth.
- `bisley_goldberg2010_parietal_priority` — parietal priority maps (parallel substrate). In seed, full depth.
- `desimone_duncan1995_biased_competition` — biased competition (downstream mechanism). In seed, full depth.
- `feldman_friston2010_attention_free_energy` — precision-weighting framework. In seed, full depth.
- `panichello_buschman2021_shared_mechanisms` — modern shared attention-WM. In seed, full depth.
- `moore_fallah2004_fef_microstim_subthreshold` — Moore lab's follow-up. Not in seed.
- `noudoost_moore2011_d1_pfc_attention` — dopamine D1 in PFC attention. Not in seed.
- `mante2013_context_dependent_pfc` — PFC as recurrent dynamical system. In seed, full depth.
- `boshra_kastner2022_attention_control` — modern attention-control review. In seed.
