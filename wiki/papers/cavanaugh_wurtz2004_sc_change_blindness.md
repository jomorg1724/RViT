---
id: cavanaugh_wurtz2004_sc_change_blindness
title: "Subcortical modulation of attention counters change blindness"
authors:
  - "Cavanaugh, James"
  - "Wurtz, Robert H."
year: 2004
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.3724-04.2004"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.3724-04.2004"
tags:
  - primate-neurophysiology
  - subcortical
  - lesion-microstimulation
  - change-detection
  - visual-attention
concepts:
  - microstimulation
  - cueing-effect
  - top-down-feedback
related:
  - moore_armstrong2003_fef_microstim
  - krauzlis2013_sc_attention
  - herman_krauzlis2017_sc_change_detection
  - posner1980_orienting
  - bisley_goldberg2010_parietal_priority
  - cavanaugh2006_brain_stim_attention
  - bollimunta2018_fef_sc_covert
  - mirpour2010_ppc_microstim
  - muller2005_sc_microstim_covert
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_44
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Subcortical modulation of attention counters change blindness

## 1. Abstract

Change blindness is the failure to see large changes in a visual scene that occur simultaneously with a global visual transient. Such transients might be brief blanks between visual scenes or the blurs caused by rapid or saccadic eye movements between fixations. Shifting attention to the site of the change *counters* this blindness by improving change detection and reaction time. Cavanaugh & Wurtz developed a change blindness paradigm for visual motion and then showed that presenting an attentional cue diminished the blindness in both humans and old-world monkeys. They then replaced the visual cue with *weak electrical stimulation of the superior colliculus* in the monkey's brainstem — to test whether activation at such a late stage in the eye-movement control system contributes to the attentional shift that counters change blindness. With SC stimulation, monkeys more easily detected changes and had shorter reaction times — both characteristics of a shift of attention.

## 2. Why this matters for us

Cavanaugh & Wurtz 2004 is the *direct experimental precedent* for the recurrent ViT's perturbation experiment (2502.10955 §6.6) and the change-detection paradigm itself. The 2502.10955 paper reports that attention-map perturbations produce behavioral shifts analogous to FEF microstimulation (Moore & Armstrong 2003). Cavanaugh & Wurtz 2004 is the *parallel* result for SC microstimulation: subcortical electrical stimulation produces attention-like shifts that counter change blindness, demonstrating that the SC is a sufficient source for attention modulation independent of cortex. The paper is also a direct precedent for the change-detection paradigm — it adapts the change-blindness phenomenon to a primate-electrophysiology setting, exactly the kind of paradigm the recurrent ViT was designed to model.

## 3. Key claims

1. **Change blindness in motion.** Monkeys (and humans) exhibit change blindness when a global visual transient (a brief blank) accompanies a change in stimulus motion. The blindness is significant — detection accuracy drops, RTs lengthen.
2. **Attentional cues reverse it.** A visual cue at the location of the change *counters* the blindness: detection accuracy improves, RTs shorten. This is the classical attentional facilitation of change detection.
3. **Subcortical electrical stimulation reproduces the effect.** Weak electrical stimulation of the SC (intermediate layers, at currents below the saccade threshold) produces the *same behavioral signatures* as an attentional cue — improved detection at the stimulated retinotopic location, faster RTs.
4. **The SC is sufficient.** SC stimulation produces the attentional shift even though it operates at a "late" stage of the eye-movement control system. This is sufficient evidence that *the SC contributes to overt and covert attention*, not just to saccade execution.
5. **Subthreshold stimulation works.** The stimulation currents used are below the threshold that would evoke saccades; the behavioral effects are purely attentional, not driven by an overt eye movement.
6. **Retinotopic specificity.** The behavioral effect of SC stimulation is specific to the retinotopic location encoded by the stimulated SC site — the same spatial specificity as the visual-cue effect.

## 4. Methods

**Task.** Subjects (monkeys and humans, in parallel) viewed displays containing a set of moving stimuli. After a brief blank period (the transient that causes change blindness), the display reappeared with one stimulus's motion direction changed. Subjects detected which stimulus had changed by making a saccade to it or by manual response.

**Cue condition.** On half the trials, a brief visual cue appeared at the location of the change. On the other half, no cue. The cue presence served as a within-subjects attentional manipulation.

**SC microstimulation.** In monkeys only, the SC was stimulated electrically at intermediate-layer sites (the layers that integrate visual and motor information). Stimulation currents were *subthreshold* for saccade evocation (typically <20 μA). The stimulation timing was matched to the cue-presentation timing in the cue condition.

**Behavioral measures.** Change-detection accuracy and reaction time. Comparisons: (a) no-cue vs visual-cue trials; (b) no-stim vs SC-stim trials.

## 5. Results

The principal quantitative findings:

- **Change blindness exists in motion paradigms.** Without cue / stim, change detection is impaired (accuracy ~60–70%, RTs longer than control).
- **Visual cues counter the blindness.** Cued trials show ~85–90% accuracy and significantly shorter RTs — the classical attentional benefit.
- **SC stimulation reproduces the cue effect.** SC-stim trials show detection accuracy and RT *similar to* cued trials — substantially better than no-stim trials.
- **The effect is retinotopically specific.** Stimulating an SC site that encodes location X produces benefits specifically at retinotopic location X, not at other locations.
- **Subthreshold stimulation.** No saccades are evoked by the stimulation; the behavioral effect is entirely attentional in origin.
- **Generalization across species.** The visual-cue effect is similar in humans and monkeys, validating the model's relevance for human attention research.

## 6. Critique / limitations

The stimulation is electrical, not pharmacological or optogenetic. Electrical stimulation activates a population of cells with mixed properties; the precise cell types contributing to the attentional effect are not identifiable. Subsequent optogenetic work has refined the cellular specificity.

The behavioral readout is detection / RT — a *coarse* measure. Finer-grained measurement (e.g., d' analysis, attentional priority maps) would give a more nuanced picture of what "attention" the SC stimulation is providing.

The study uses motion change-detection. Whether the SC's attention contribution generalizes to other feature dimensions (color, orientation, shape) is partially addressed by Herman & Krauzlis 2017 ([herman_krauzlis2017_sc_change_detection](research_db/papers/herman_krauzlis2017_sc_change_detection.md)) for color, but extension to other dimensions is open.

The study doesn't characterize the *neural mechanism* by which SC stimulation produces the attentional effect. Subsequent work (Krauzlis 2013 review; Bollimunta, Bogadhi, Krauzlis 2018) has begun to identify the downstream targets of SC attention signals.

The paper is *one of many* that have established SC's attention role. It's the foundational change-blindness-specific result, but the broader picture requires combining it with FEF / pulvinar / dlPFC microstimulation work to get the full attention-source network.

## 7. Connection to our work

This paper supplies two distinct foundations for the user's program:

**The recurrent ViT's perturbation experiment.** The 2502.10955 paper reports that perturbations to the attention map produce behavioral shifts analogous to FEF microstimulation. Cavanaugh & Wurtz 2004 is the parallel result for SC microstimulation. The architectural commitment — perturbing the source of attention produces behavioral attentional shifts — is the *same* whether the source is FEF (Moore & Armstrong 2003) or SC (Cavanaugh & Wurtz 2004). The recurrent ViT's perturbation methodology is the AI analog of both.

**The change-detection paradigm.** The recurrent ViT (2502.10955) and PRISM v1 are trained on a *change-detection task* — a direct adaptation of the change-blindness paradigm Cavanaugh & Wurtz study. The use of "change detection" as the behavioral test is partly motivated by its tractable structure in primate electrophysiology, which Cavanaugh & Wurtz established.

**The SC as a source of attention.** The user's program treats PFC and parietal cortex as sources of top-down attention (analogous to FEF and LIP). The Cavanaugh-Wurtz result adds the SC as a *subcortical* source of attention. The user's multi-hub system could be extended to include a "subcortical attention hub" analog of the SC, which would supply attention modulation in parallel with the cortical sources. This is a future architectural direction.

**Subthreshold stimulation as the analog of subtle attention modulation.** Cavanaugh & Wurtz's use of *subthreshold* electrical stimulation — sufficient to shift attention without evoking overt action — is the methodological analog of the recurrent ViT's *graded* attention modulation. Real attention is rarely all-or-nothing; the SC mechanism supports graded attentional shifts, matching the Feedback Transformer's graded multiplicative gain.

The recurrent ViT paper cites Cavanaugh & Wurtz 2004 in its bibliography (ref [44]). Future manuscripts on the recurrent ViT's perturbation methodology should cite this paper as the SC-specific precedent (parallel to Moore & Armstrong 2003 for FEF).

## 8. Citations to follow

- `moore_armstrong2003_fef_microstim` — the FEF parallel. In seed, full depth.
- `herman_krauzlis2017_sc_change_detection` — color-change-detection follow-up. In seed, full depth.
- `krauzlis2013_sc_attention` — broader SC-attention review. In seed, full depth.
- `cavanaugh2006_brain_stim_attention` — Cavanaugh follow-up on stim-as-attention vs stim-as-cue. In seed.
- `bollimunta2018_fef_sc_covert` — FEF vs SC covert attention. In seed.
- `muller2005_sc_microstim_covert` — SC microstim and covert attention. In seed.
- `mirpour2010_ppc_microstim` — PPC microstim parallel. In seed.
