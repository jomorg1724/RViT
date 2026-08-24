---
id: cavanaugh2006_brain_stim_attention
title: "Enhanced performance with brain stimulation: attentional shift or visual cue?"
authors:
  - "Cavanaugh, James"
  - "Alvarez, Bryan D."
  - "Wurtz, Robert H."
year: 2006
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.2376-06.2006"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.2376-06.2006"
tags:
  - primate-neurophysiology
  - subcortical
  - lesion-microstimulation
  - change-detection
  - visual-attention
concepts:
  - microstimulation
  - cueing-effect
  - attentional-spotlight
  - top-down-feedback
related:
  - cavanaugh_wurtz2004_sc_change_blindness
  - gattass_desimone2014_sc_microstim
  - moore_armstrong2003_fef_microstim
  - krauzlis2013_sc_attention
  - muller2005_sc_microstim_covert
  - sridharan2017_sc_sensitivity_bias
  - reynolds_chelazzi2004_attentional_modulation
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_45
status: full
depth: full
last_updated: "2026-05-16"
---

# Enhanced performance with brain stimulation: attentional shift or visual cue?

## 1. Abstract

The premotor theory of visual spatial attention proposes that the same brain activity that prepares for saccades to one part of the visual field also facilitates visual processing at that same region of the visual field. Strong support comes from improvements in performance by electrical stimulation of presaccadic areas, including the frontal eye field and superior colliculus (SC). Interpretations of these stimulation experiments are hampered by the possibility that stimulation might be producing an internal visual flash or phosphene that attracts attention as a real flash would. The authors tested this phosphene hypothesis in the SC by comparing the effect of interchanging real visual stimuli and electrical stimulation. They first presented a veridical visual cue at the time SC stimulation improved performance; if a phosphene improved performance at this time, a real cue should do so in the same manner, but it did not. They then changed the time of SC visual-motor stimulation to when they ordinarily presented the veridical visual cue, and failed to improve performance. Last, they shifted the site of SC stimulation from the visual-motor neurons of the SC intermediate layers to the visual neurons of the superficial layers to determine whether stimulating visual neurons produced a larger improvement in performance, but it did not. The experiments provide evidence that a phosphene is not responsible for the shift of attention that follows SC stimulation. This added evidence of a direct shift of attention is consistent with a key role of the SC in the premotor theory of attention.

## 2. Why this matters for us

This paper is the *control experiment* that licenses interpreting SC microstimulation (Cavanaugh & Wurtz 2004) as a genuine attentional manipulation rather than as an artifact of an evoked sensory percept. For the recurrent ViT's perturbation experiments (2502.10955 §6.6) the exact same logical hazard applies: when one perturbs an internal attention map and observes a behavioral shift, the shift could reflect a genuine reweighting of internal "attention" *or* it could reflect a spurious sensory-cue analog injected by the perturbation itself. Cavanaugh, Alvarez & Wurtz 2006 is the methodological template for distinguishing the two hypotheses by interchanging real and artificial cues across time and location and by varying the laminar identity of the stimulated population. The paper is also the second instalment of the Cavanaugh-Wurtz lineage that anchors the SC microstimulation framework in our literature stack.

## 3. Key claims

1. **The phosphene hypothesis is the load-bearing alternative.** Any improvement in detection following microstimulation of a presaccadic area could be explained either by a genuine attentional shift or by an internally evoked sensory cue (a phosphene) that attracts exogenous attention exactly as a real flash would; the two accounts must be disentangled before microstimulation results can support the premotor theory.
2. **Real cues at the SC-stim time do not mimic SC-stim.** Presenting a veridical visual cue at the precise moment in the trial when SC stimulation normally improves performance does *not* reproduce the SC-stim benefit. If SC stimulation were merely producing an internal flash, a real flash at the same time should give an equal or larger benefit; it does not.
3. **SC-stim at the cue time does not mimic real cues.** Reciprocally, moving the SC visual-motor stimulation pulse to the time slot when the visual cue is normally presented fails to recreate the cue's benefit. The SC-stim effect is locked to its specific temporal window in the trial — characteristic of an attentional shift, not of a transient sensory flash.
4. **Superficial-layer stimulation does not enhance the effect.** Stimulating the *visual* neurons of the SC superficial layers — the cells most likely to produce a phosphene-like sensory percept — produces no larger improvement than stimulating the visual-motor cells of the intermediate layers. If a phosphene were the active ingredient, the more visual site should give the larger effect; it does not.
5. **The active site is the visual-motor intermediate layer.** The behavioral improvement is associated specifically with stimulation of intermediate-layer visual-motor neurons (the layer that participates in the premotor saccade-preparation circuit), not with the purely visual superficial-layer neurons.
6. **The result is consistent with the premotor theory.** The pattern of dissociations — temporal specificity, laminar specificity, non-equivalence to real cues — is what one expects if SC stimulation directly engages the premotor attentional mechanism rather than evoking a sensory cue.
7. **Microstimulation can be a clean attentional probe.** Subthreshold, intermediate-layer SC microstimulation is, by the experiments here, neither an evoked phosphene nor a generic cue — it is a targeted attentional manipulation, defensible as such against the standard sensory-injection objection.

## 4. Methods

**Animals and task.** Two macaques performed the motion-change-detection task from Cavanaugh & Wurtz (2004): a set of moving stimuli is presented; a brief blank interval introduces a global transient; the display reappears with one stimulus's motion direction changed; the monkey reports the changed stimulus, typically by saccade to its location. Performance without intervention exhibits change blindness — accuracy below the unmasked baseline, longer reaction times.

**SC microstimulation.** Tungsten microelectrodes recorded and stimulated SC sites. Stimulation was *subthreshold* for evoked saccades (currents below the saccade threshold for that site, typically tens of microamps). The retinotopic location encoded at the stimulated SC site was determined from saccade endpoints elicited at suprathreshold currents and from visual receptive-field mapping.

**Three interchange manipulations.** The novel contribution is a 2 × 2 × 2 set of cue-vs-stim comparisons:

- *Manipulation 1 — real cue at the SC-stim time.* On a subset of trials a veridical visual cue (a small flash) was presented at the temporal locus where SC stimulation normally improves performance. If SC stim acted as a phosphene, a real flash at that time should give the same or a larger benefit.
- *Manipulation 2 — SC stim at the visual-cue time.* The SC stimulation pulse was shifted to the temporal locus where the veridical visual cue is normally presented. If SC stim acted as a flash, this displaced stim should now play the role of a normal cue.
- *Manipulation 3 — laminar identity of the stim site.* Stimulation was applied either to *visual-motor* neurons of the intermediate layers (the standard Cavanaugh-Wurtz 2004 site) or to the *visual* neurons of the superficial layers. Phosphenes, when evocable at all, are more readily produced by stimulating purely visual cells; thus a larger superficial-layer effect would support the phosphene account.

**Behavioral measures.** Change-detection accuracy and reaction time, conditioned on cue type, stimulation type, stimulation timing, and stimulated layer. Comparisons used within-session contrasts. Stimulated and unstimulated trials were interleaved.

**Logic of the dissociation.** The three manipulations are designed to be jointly diagnostic. If SC stimulation acts as an internal phosphene, then (i) a real flash at the stim-equivalent time should reproduce the stim benefit; (ii) stim shifted to the cue-equivalent time should reproduce the cue benefit; (iii) stimulating purely visual cells (superficial-layer neurons) should produce a *larger* phosphene and therefore a larger behavioral effect than stimulating visual-motor cells (intermediate-layer neurons). The premotor attention account makes the opposite predictions on all three axes. The paper reports failures of all three phosphene-predicted equivalences, providing a triple dissociation rather than relying on any single contrast.

## 5. Results

The paper reports three principal dissociations.

- **Temporal interchange, real cue at stim time.** A veridical visual cue presented at the stim-equivalent time produces a substantially *smaller* improvement than the same cue at its standard time, and a smaller improvement than SC stim at the stim-equivalent time. The temporal window for an exogenous flash to drive attention to the change location differs from the window in which SC stim is effective.
- **Temporal interchange, stim at cue time.** SC stimulation delivered at the cue-equivalent temporal slot fails to reproduce the cue effect. The SC-stim benefit is thus not a generic "cue-like" event that can be slotted in wherever a cue would work; it operates in its own characteristic time window.
- **Laminar interchange.** Stimulating the visual neurons of the SC superficial layers produces no greater improvement than stimulating the visual-motor neurons of the intermediate layers — and in fact is generally *less* effective. This is the opposite of what the phosphene hypothesis predicts: the cells most likely to evoke an internal flash give the smaller behavioural effect.
- **Magnitude of the intermediate-layer effect.** Consistent with Cavanaugh & Wurtz (2004), subthreshold intermediate-layer SC stimulation produced reliable improvements in change-detection accuracy and RT at the stimulated site's retinotopic location, without evoking saccades.
- **Asymmetry of cue and stim.** Cue and stim are not interchangeable along either the temporal or the laminar axis. They behave like two distinct interventions that converge on a common downstream readout (improved change detection at one location), not like two instances of the same intervention.
- **Saccade-thresholded calibration.** Across sites, stimulation currents were tuned to remain below the per-site saccade threshold. The behavioral effects were obtained without any contamination by overt eye movements, confirming the covert-attention interpretation.
- **Retinotopic specificity preserved.** As in 2004, the SC-stim benefit was specific to the retinotopic location encoded at the stimulated site; performance at unstimulated locations was unaffected, so the manipulation is a *spatially* targeted attentional bias rather than a generalized arousal effect.

The paper relies on within-session, within-subject comparisons; precise effect sizes are reported figure by figure in the published article and are not rehearsed verbatim here, but the qualitative pattern — dissociation across all three manipulations — is the load-bearing result. The pattern is consistent across the two animals, with the magnitude of the dissociation in line with the 2004 cue-vs-stim equivalence result.

## 6. Critique / limitations

The argument is *eliminative*: the paper does not directly show what SC stimulation is doing, only that it is unlikely to be acting as an evoked phosphene. A residual possibility is that SC stimulation produces a non-phosphene-like internal cue (e.g., a motor-set signal) that nevertheless is not the attentional mechanism the premotor theory invokes; the paper does not rule out every conceivable "cue analog," only the specific sensory-flash account.

The negative results — real cue at stim time, stim at cue time, superficial-layer stim — could in principle reflect under-powered manipulations rather than true null effects. The paper reports the comparisons with within-session, within-subject statistics, but the strongest reading depends on accepting that the *opposite* pattern would have been seen had the phosphene hypothesis held. With only two macaques, the inference rests on consistency across sessions rather than on a large between-subject sample.

Electrical stimulation in the intermediate layers activates a heterogeneous population. The paper localises the effect to "visual-motor" neurons rather than to "visual" neurons by laminar dissection, but does not identify a cell type or projection target. Later optogenetic and inactivation work (Krauzlis 2013, Krauzlis, Lovejoy & Zénon 2013; Müller et al. 2005; Bollimunta, Bogadhi & Krauzlis 2018) refines this anatomical specificity.

The paradigm remains motion-change detection, inheriting the feature-dimension limitations noted for Cavanaugh & Wurtz 2004. Whether the phosphene-control logic generalises to colour, orientation, or shape change-detection is an empirical question; later work in other dimensions has not contradicted it but has not explicitly re-run the cue-stim interchange either.

The premotor theory itself remains controversial. The paper's contribution is to remove one alternative explanation for the SC-stim attentional effects; it does not adjudicate between premotor and biased-competition or priority-map accounts of attention. The result is therefore best read as *necessary* support for the SC's role as a genuine attention source, not as *sufficient* support for the premotor theory in particular.

The asymmetry of the laminar interchange is partly a property of the SC's anatomical organisation: superficial-layer cells are densely visual but project predominantly to pulvinar and onward to cortex, whereas intermediate-layer cells participate in the saccadic output circuit. The behavioral effect's localisation to the intermediate layer is consistent with the premotor theory but is also consistent with any account in which the *output-projecting* SC population is the relevant source — a distinction the paper cannot resolve. Disentangling premotor from output-projection accounts requires the kind of pathway-specific perturbations (chemogenetic / optogenetic targeting of identified projection populations) that postdate the paper.

## 7. Connection to our work

This paper is the methodological hinge between the SC microstimulation literature and the recurrent ViT's internal-perturbation experiments. Three concrete connections.

**Genuine attention vs spurious cue analog in the recurrent ViT.** The recurrent ViT (2502.10955 §6.6) reports that perturbing the model's internal attention map produces behavioural shifts on change-detection trials, and §6.7 frames this as the AI analog of FEF / SC microstimulation. The hazard Cavanaugh, Alvarez & Wurtz address in macaques is the *direct analog* of an objection one can raise against any such internal-perturbation result in a deep network: perhaps the perturbation does not modulate "attention" at all but acts as an injected sensory cue at the perturbed location, biasing downstream readouts much as an extra patch token would. The 2006 paper's dissociation strategy — interchange the perturbation with a veridical cue across time, across the perturbation site's laminar/structural identity, and across the temporal window of effect — is directly portable to the ViT perturbation methodology. Concretely, the analog experiments are: (a) inject a perturbation of equal energy into the *input* patch grid at the same retinotopic location and time, and check that it does *not* produce the same behavioural shift; (b) shift the perturbation's pass index (e.g., apply it at pass 1 vs pass 3 of the recurrent loop) and check that the behavioural effect is locked to a specific recurrence pass; (c) compare perturbations applied at "visual-motor" depth (later layers / decoder hub) with those applied at "visual" depth (early patch-embedding layers) and verify that the effect is *not* maximal at the early-vision site. These three controls translate the Cavanaugh-Alvarez-Wurtz logic into a deep-network setting and would convert §6.6 from a suggestive demonstration into a falsifiable attentional manipulation. The thread `the_user_architectural_program` §1 (Feedback Transformer) and §3 (multi-compartmental memory) make these controls especially apt: with multiple hubs and multiple recurrent layers, the "laminar" interchange has natural counterparts.

**The Cavanaugh-Wurtz lineage.** The 2004 paper [cavanaugh_wurtz2004_sc_change_blindness](cavanaugh_wurtz2004_sc_change_blindness.md) established that subthreshold SC microstimulation produces change-detection benefits indistinguishable from a visual cue's. The 2006 paper closes the natural follow-up loophole: that the apparent equivalence might be because both manipulations introduce a sensory event at the same retinotopic location. Together the two papers form a tight evidentiary unit: SC stim mimics a cue *behaviourally*, yet is dissociable from a cue *mechanistically*. Any citation of the 2004 result in a manuscript on the recurrent ViT's perturbation methodology should be paired with a citation to this 2006 control paper to forestall the obvious reviewer objection.

**The SC microstim framework as a literature anchor.** Cavanaugh, Alvarez & Wurtz 2006 sits at the centre of the SC microstim framework that also includes [muller2005_sc_microstim_covert](muller2005_sc_microstim_covert.md) (covert attention without saccades), [gattass_desimone2014_sc_microstim](gattass_desimone2014_sc_microstim.md) (extension to feature-based covert attention), [moore_armstrong2003_fef_microstim](moore_armstrong2003_fef_microstim.md) (the FEF cortical parallel), [krauzlis2013_sc_attention](krauzlis2013_sc_attention.md) (the integrative review), and [sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md) (the sensitivity-vs-bias decomposition of SC's attentional contribution). The 2006 paper is what makes the rest of this stack interpretable as evidence about attention rather than about phosphene-evoking flashes. For our purposes — modelling attention with feedback-transformer-style internal sources — the framework licenses treating subcortical and cortical microstim alike as causal probes of attentional source populations, which is the empirical pattern the recurrent ViT's perturbation experiments are designed to mimic in silico.

**Subthreshold stim and graded modulation.** As in 2004, the *subthreshold* character of the stimulation matters: the manipulation is graded, sufficient to bias attention but insufficient to evoke action. This is the empirical analog of the multiplicative, graded character of the Feedback Transformer's feedback contribution to the Q / K / V projection (thread `the_user_architectural_program` §1). The 2006 paper's dissociations strengthen the case that this graded SC signal is a *genuine* attentional source rather than a sensory injection — which is precisely the claim one wants to make about graded multiplicative feedback in the recurrent ViT.

**Implications for the perturbation methodology in §6.6 of 2502.10955.** A clean way to import the 2006 paper's logic into the recurrent ViT literature is to state, for the published perturbation experiment, the *three* control comparisons it does not yet contain: (1) an input-side patch perturbation of matched energy and location; (2) a perturbation applied at a non-canonical recurrence step; and (3) a perturbation applied at the earliest patch-embedding layer rather than at a deeper memory hub. The expected pattern under the "genuine attention" hypothesis is that the published deep, on-pass perturbation produces the largest behavioral shift; the three controls produce attenuated or qualitatively different shifts. Reporting this triple dissociation would put the recurrent ViT's claim on the same evidentiary footing as the SC microstim claim post-2006, and removes the principal reviewer objection — that any deep-network perturbation merely mimics a sensory cue — that would otherwise dog the result.

## 8. Citations to follow

- `moore_armstrong2003_fef_microstim` — the cortical (FEF) parallel; already in seed at full depth.
- `muller2005_sc_microstim_covert` — covert attention via SC microstim without eye movements; in seed.
- `goldberg_wurtz1972_sc_attention` — the foundational SC-and-attention single-unit paper that Cavanaugh-Wurtz 2006 cites as the lineage anchor; not yet in seed but worth a stub for the lineage.
- `moore_armstrong_fallah2003_visuomotor_covert` — Moore, Armstrong & Fallah Neuron 2003 "Visuomotor origins of covert spatial attention"; the FEF-side argument that the same circuit drives saccade preparation and covert attention. Not yet in seed; high-priority addition.
- `glimcher_sparks1993_sc_low_frequency` — low-frequency SC stim and saccades; methodological precedent for the subthreshold regime. Not in seed.
- `tehovnik2005_phosphene_v1_review` — Tehovnik, Slocum, Carvey & Schiller on phosphene induction and saccade generation from striate cortex; the closest published treatment of the phosphene hypothesis Cavanaugh-Alvarez-Wurtz refute. Not in seed; useful for the methodology thread.
- `reynolds_chelazzi2004_attentional_modulation` — Reynolds & Chelazzi Annu Rev review cited as the contemporary attention-modulation framework. In seed, full depth.
- `ruff2006_tms_fmri_frontal` — Ruff et al. concurrent TMS-fMRI; the human-causal-perturbation analog. Not in seed; relevant for cross-species generalisation of the perturbation methodology.
- `treue_maunsell1999_mt_mst_attention` — Treue & Maunsell on attentional modulation of motion processing in MT/MST; the downstream-cortex side of the same task family used in the change-detection paradigm. Not yet in seed.
- `wurtz_mohler1976_sc_enhanced` — Wurtz & Mohler on enhanced visual responses in SC superficial layer cells; foundational for the laminar dissection used in manipulation 3. Not in seed.
- `tehovnik2003_v1_microstim_saccades` — Tehovnik, Slocum & Schiller on saccades evoked by V1 microstimulation; relevant negative control for the "stim acts as cue" hypothesis at a different stimulation site. Not in seed.
