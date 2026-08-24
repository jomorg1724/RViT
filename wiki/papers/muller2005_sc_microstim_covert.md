---
id: muller2005_sc_microstim_covert
title: "Microstimulation of the superior colliculus focuses attention without moving the eyes"
authors:
  - "Müller, Jorge R."
  - "Philiastides, Marios G."
  - "Newsome, William T."
year: 2005
venue: "PNAS"
doi: "10.1073/pnas.0408311101"
arxiv: ""
url: "https://doi.org/10.1073/pnas.0408311101"
tags:
  - primate-neurophysiology
  - subcortical
  - lesion-microstimulation
  - visual-attention
  - psychophysics
concepts:
  - microstimulation
  - cueing-effect
  - attentional-spotlight
  - psychometric-function
  - signal-detection-theory
related:
  - cavanaugh_wurtz2004_sc_change_blindness
  - cavanaugh2006_brain_stim_attention
  - gattass_desimone2014_sc_microstim
  - krauzlis2013_sc_attention
  - sridharan2017_sc_sensitivity_bias
  - bollimunta2018_fef_sc_covert
  - moore_armstrong2003_fef_microstim
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Microstimulation of the superior colliculus focuses attention without moving the eyes

## 1. Abstract

The superior colliculus (SC) is a midbrain structure that orchestrates rapid saccadic eye movements, overtly shifting both gaze and attention from one point in space to another. Müller, Philiastides, and Newsome asked whether the SC also contributes to *covert* spatial attention — directing focus to a peripheral location while the eyes remain fixed. While macaque monkeys performed a demanding peripheral motion-direction discrimination, the authors delivered weak electrical microstimulation to intermediate-layer SC sites at currents *below* the threshold required to evoke a saccade. Subthreshold stimulation improved discrimination performance — lowering motion-coherence thresholds — specifically at the visual-field location encoded by the stimulated SC site, and not at a control location in the opposite hemifield. The effect could not be attributed to a general increase in arousal or vigilance because of its spatial specificity, and it could not be attributed to a covert saccade because eye position was monitored and fixation was strictly enforced. The result provides direct causal evidence that the primate SC participates in the control of covert spatial attention, complementing its well-documented role in overt orienting.

## 2. Why this matters for us

Müller et al. 2005 is one of the two foundational SC-microstimulation results (alongside Cavanaugh & Wurtz 2004) that anchor the user's program on the subcortical side of attention. Two specific links to the architecture stand out. First, the result establishes that a *non-cortical* node can causally inject an attention-like modulation into perceptual processing — i.e., the source of top-down attention is *not* uniquely cortical. This licenses the user's multi-hub design, in which attention can be sourced from any hub whose internal state competes for control of the central self-attention map. Second, the demonstration that subthreshold electrical perturbation produces graded perceptual improvement is the experimental analog of the recurrent ViT's attention-map perturbation experiment (2502.10955 §6.6): a small additive or multiplicative push to the attention substrate produces a behavioral shift, without requiring the system to make a full categorical "decision" (saccade / no-saccade). Both are evidence that attention modulation is naturally graded and additive on top of the sensory pathway.

## 3. Key claims

1. **SC microstimulation lowers motion-coherence discrimination thresholds.** With subthreshold currents, the psychometric function for direction discrimination shifts toward lower coherence — the monkey detects motion direction at coherences that would otherwise be at chance.
2. **The effect is retinotopically specific.** Improvement occurs only at the visual-field location encoded by the stimulated SC site; performance at a mirror-symmetric control location in the opposite hemifield is unchanged or slightly impaired (consistent with the limited-capacity character of attention).
3. **The effect is not a covert saccade.** Eye position is monitored throughout each trial; trials with detectable saccades are excluded. Stimulation currents are explicitly chosen below the saccade threshold for each site.
4. **The effect is not generalized arousal.** Pure arousal or vigilance increases would benefit both hemifields. The spatial selectivity of the improvement rules this out.
5. **The SC is causally engaged in covert spatial attention.** Combined with the spatial selectivity and the subthreshold-stimulation constraint, the result is direct causal evidence — not just correlation — that the primate SC contributes to covert attention.
6. **Perceptual *enhancement* by transient brain stimulation.** The paper is notable as one of very few causal manipulations that *improves* perceptual performance rather than degrading it.

## 4. Methods

**Subjects and task.** Two rhesus macaques, head-fixed, performed a two-alternative motion-direction discrimination on a random-dot kinematogram (RDK) presented at a peripheral location. The RDK was a square aperture of coherently moving dots embedded in a field of randomly moving noise dots, with motion coherence varied across trials to construct a psychometric function. The monkey reported the perceived motion direction by a saccade to one of two response targets.

**Distracter and attentional load.** A second flickering or moving distracter patch was presented elsewhere in the visual field, requiring the monkey to deploy attention to the SC-encoded location rather than free-view. This is the standard manipulation to ensure the task taxes covert spatial attention.

**SC microstimulation.** Microelectrodes were lowered into intermediate / deeper SC layers (the layers that integrate visual and saccade-related signals). At each site, the saccade threshold was first determined: the lowest current that reliably evoked a saccade to the site's response-field location. Stimulation in the attention task was then delivered at currents *below* this threshold — typically a fraction of the saccade-threshold current. Stimulation trains were brief (tens of ms) and timed to overlap the motion stimulus.

**Spatial controls.** The RDK aperture was centered on the SC response field for "in-RF" trials. For control trials, the RDK was placed at the mirror-symmetric location in the opposite hemifield; the same stimulation pulse was delivered on a fraction of those trials. Comparing the in-RF stim effect to the control-location stim effect isolates retinotopic specificity.

**Eye-position enforcement.** Fixation windows were tight; trials with saccades during the stimulation epoch were excluded from the psychometric analysis. This is what allows the "without moving the eyes" claim.

**Analysis.** Psychometric functions (proportion correct vs motion coherence) were fit with a cumulative Gaussian or Weibull. The principal dependent variable was the motion-coherence threshold (the coherence at a fixed performance level, e.g. 75% correct). The microstimulation effect was the leftward shift of the psychometric function — a lower threshold — at the in-RF location.

## 5. Results

The key quantitative findings reported by the authors:

- **Threshold reduction at the in-RF location.** Subthreshold SC microstimulation produced a significant decrease in motion-coherence threshold at the location encoded by the stimulated SC site. The magnitude of the improvement is comparable to the cueing benefit produced by a visual attentional cue at the same location.
- **No improvement at the control location.** Stimulation produced no facilitation — and in some sites a slight impairment — at the mirror-symmetric control location, consistent with attention being a limited resource that, when redirected to one location, is withdrawn from elsewhere.
- **Effect scales with current.** Within the subthreshold range, larger currents produce larger threshold reductions, up to the saccade-evoking threshold (beyond which the trial is aborted as a saccade-execution event).
- **Effect is independent of overt eye movements.** Trials with any detectable saccade were excluded; the threshold reduction persists in the strict-fixation subset.
- **Effect generalizes across SC sites.** The improvement was observed across multiple recording sites in two monkeys, indicating a generic property of intermediate-layer SC stimulation rather than a peculiarity of a single site.
- **Effect timing.** The improvement requires stimulation during or just before the motion stimulus; long pre-stimulus or post-stimulus stimulation does not produce the same benefit, ruling out trivial arousal/motivation accounts.

## 6. Critique / limitations

The stimulation is electrical, activating a mixed population of intermediate-layer SC cells (visuomotor neurons, build-up neurons, saccade-related burst neurons, and fibers of passage). The cell-type specificity of the attentional benefit cannot be inferred from electrical methods alone; later optogenetic and pharmacological work (reviewed in Krauzlis 2013) has begun to refine this.

The behavioral readout is a single perceptual threshold. Sridharan et al. 2017 ([sridharan2017_sc_sensitivity_bias](research_db/papers/sridharan2017_sc_sensitivity_bias.md)) re-analyzed paradigms in this family with a multi-alternative signal-detection framework and showed that SC manipulations affect perceptual *bias* (choice criterion) more robustly than perceptual *sensitivity* (d′). Whether the threshold shift here is purely sensitivity, purely bias, or a mixture is not separable in the original 2AFC analysis.

The "without moving the eyes" claim depends on the spatial resolution of the eye-tracker and the exclusion criterion. Microsaccades below the detection threshold cannot be ruled out, although their amplitude (<0.5°) is too small to account for the spatial selectivity at peripheral RDK locations.

Generality across feature dimensions is limited. The paper tests motion-direction discrimination; whether SC stimulation facilitates other discriminations (orientation, color, shape) was not directly tested. Cavanaugh & Wurtz 2004 ([cavanaugh_wurtz2004_sc_change_blindness](research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md)) extended a related claim to motion change-detection, and Herman & Krauzlis 2017 to color, but the full feature-generality of the SC attention signal remains an open question.

Finally, the result establishes *sufficiency* of SC activation for an attention-like shift, but does not establish *necessity*. Inactivation studies (Lovejoy & Krauzlis 2010) are the necessary complement.

## 7. Connection to our work

This paper is one of the load-bearing causal demonstrations behind the user's commitment to a *graded, additive, multi-source* model of attention.

**The recurrent ViT's perturbation experiment.** In 2502.10955 §6.6, the authors perturb the attention map by injecting small additive / multiplicative biases at the network's source-of-attention substrate and report behavioral shifts on change-detection. The Müller et al. result is the SC-microstimulation analog: a small electrical perturbation at the attention source produces a graded perceptual benefit, without the system needing to commit to a discrete saccade. The recurrent ViT's perturbation methodology is conceptually identical — a small, sub-decision-threshold push at the attention substrate that shifts behavior in a graded way.

**Covert attention without overt action.** PRISM v1 and the recurrent ViT do not move "eyes": they have no overt action channel. The system's only "action" is the attention map itself. Müller et al. is the experimental demonstration that the SC — biologically the overt-action structure — can implement *covert* attention with the eyes still. This validates the architectural commitment to model attention as a purely internal modulation, decoupled from any overt action: in the recurrent ViT, attention shifts happen entirely within the attention map, with no "saccade" head, and there is biological precedent that this internal-only mode is realistic.

**The SC as a subcortical attention hub in the multi-hub design.** The user's program (§5 of `the_user_architectural_program`) envisions multiple hubs — MSI, RL, VAE — each able to inject feedback into a central self-attention substrate via the Feedback Transformer. Müller et al. (alongside Cavanaugh & Wurtz 2004 and Bollimunta et al. 2018) is direct evidence that the biological brain has a *subcortical* hub doing exactly this kind of attention injection in parallel with cortical hubs (FEF, LIP). A future PRISM-style architecture could include an explicit "SC-like" subcortical hub whose feedback is injected at the attention-map level; this paper is the load-bearing biological precedent.

**Subthreshold stimulation as the analog of graded attention modulation.** Müller et al. explicitly use currents *below* the saccade threshold. The behavioral benefit scales smoothly with current. This matches the recurrent ViT's *multiplicative-feedback* variant (2502.10955 §6.7), where the feedback signal is a graded multiplicative gain on the attention map rather than a categorical token-replacement. Real attention is graded; the SC mechanism is graded; the Feedback Transformer's multiplicative pathway is graded. The three layers of the argument line up.

**Spatial selectivity supports the priority-map view of attention.** The retinotopic specificity of Müller et al.'s effect — improvement only at the SC-encoded location — is consistent with the SC implementing a *spatial priority map*, the same representational substrate the user's GridCell RNN approximates. The user's grid of recurrent states across spatial positions is, in effect, an architectural priority map; the SC's intermediate-layer retinotopy is the biological version. See also `krauzlis2013_sc_attention` for the broader priority-map framing.

The recurrent ViT paper does not cite Müller et al. directly (the SC-microstimulation precedent it cites is Cavanaugh & Wurtz 2004). Future manuscripts on the perturbation methodology should cite Müller et al. as a second, *quantitative-psychophysics* precedent: it is the SC paper that demonstrates a *threshold-level* perceptual benefit rather than just a change-detection benefit.

## 8. Citations to follow

- `lovejoy_krauzlis2010_sc_inactivation` — the necessity complement (SC inactivation impairs covert attention). Not yet in seed; should be added.
- `cavanaugh_wurtz2004_sc_change_blindness` — sibling SC-microstimulation result with change-detection task. In seed, full depth.
- `cavanaugh2006_brain_stim_attention` — Cavanaugh follow-up disentangling stim-as-attention vs stim-as-cue. In seed.
- `krauzlis2013_sc_attention` — review framing of SC's role as priority map. In seed.
- `sridharan2017_sc_sensitivity_bias` — re-analysis of SC manipulation paradigms (including this one) with d′ vs criterion separation. In seed, full depth.
- `bollimunta2018_fef_sc_covert` — direct FEF vs SC comparison for covert attention. In seed.
- `gattass_desimone2014_sc_microstim` — extension of the SC-microstimulation-and-attention paradigm. In seed.
- `moore_armstrong2003_fef_microstim` — the FEF analog of this result; the canonical pairing. In seed.
