---
id: salzman1990_mt_microstim
title: "Cortical microstimulation influences perceptual judgements of motion direction"
authors:
  - "Salzman, C. Daniel"
  - "Britten, Kenneth H."
  - "Newsome, William T."
year: 1990
venue: "Nature"
doi: "10.1038/346174a0"
arxiv: ""
url: "https://doi.org/10.1038/346174a0"
tags:
  - primate-neurophysiology
  - lesion-microstimulation
  - visual-attention
  - psychophysics
  - decision-making
concepts:
  - microstimulation
  - drift-diffusion-model
  - signal-detection-theory
  - hidden-state-perturbation
related:
  - salzman1992_mt_microstim_methods
  - salzman_newsome1994_winner_take_all
  - ditterich2003_microstim_rt
  - hanks2006_lip_microstim
  - roitman_shadlen2002_lip_rt
  - gold_shadlen2007_decision_making
  - cavanaugh_wurtz2004_sc_change_blindness
  - muller2005_sc_microstim_covert
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - pubmed
status: summary
depth: full
last_updated: "2026-07-04"
---

# Cortical microstimulation influences perceptual judgements of motion direction

## 1. Abstract

Neurons in the middle temporal visual area (MT/V5) of the macaque are direction-selective and are organized into columns of common preferred direction. Salzman, Britten & Newsome asked whether this direction-selective signal is causally used by the animal to judge motion direction, or whether it merely correlates with perception. They trained monkeys on a two-alternative, near-threshold direction-discrimination task using stochastic (random-dot) motion, with the dot patch positioned over the receptive field of a recorded MT column and the two choice directions set to the column's *preferred* direction versus the *opposite* (null) direction. On a subset of trials they applied weak electrical microstimulation to the direction-selective column during stimulus presentation. Microstimulation biased the monkey's direction judgements toward the direction encoded by the stimulated neurons — the animal reported the preferred direction more often, and its psychometric function shifted as though the sensory evidence for the preferred direction had been increased. This is the foundational causal demonstration that the activity of a small population of direction-selective MT neurons directly influences a perceptual decision, converting a decades-old correlation between MT firing and motion perception into a causal link.

## 2. Why this matters for us

This is the biological archetype of the exact experiment our program runs *in silico*. Our causal-perturbation method injects an additive bias into the model's attention logits (the `attn_clamp`) to push the recurrent-ViT's attention toward or away from a chosen location and then reads out the change in the RL policy. Salzman 1990 is precisely that manipulation in a monkey: inject current into a feature-selective column, hold everything else fixed, and measure how the *choice* moves. It establishes the logic our program relies on — that a targeted, sub-behavioral perturbation of a mid-level sensory representation produces a lawful, *directional* shift in the decision, not just a nonspecific disruption. It is also the paper that makes our new `motion4` battery legitimate. `motion4` is a random-dot MOTION-direction change-detection environment (a Cavanaugh & Wurtz 2004-style task with moving-dot fields swapped in for Gabors), and its stimulus — near-threshold stochastic dots, two opposed directions — is the direct descendant of the Salzman/Britten/Newsome display. When we clamp attention in `motion4` and watch the QR-DQN policy tilt toward one direction, Salzman 1990 is the primate result that says such a tilt is exactly what a real direction-selective substrate does under microstimulation.

## 3. Key claims

1. **MT direction signals are causal, not merely correlational.** Microstimulating a direction-selective MT column shifts perceptual judgements toward the stimulated column's preferred direction, establishing a causal contribution of MT activity to motion perception.
2. **The effect is direction-specific.** The bias follows the *preferred* direction of the stimulated column — stimulation adds evidence for that direction, it does not just degrade or randomize performance.
3. **The bias is graded and interacts with the stimulus.** The manipulation shifts the psychometric function (the probability of choosing "preferred" as a function of motion coherence), consistent with microstimulation *adding* to the sensory evidence rather than overriding the decision outright.
4. **Columnar organization is exploitable.** Because MT is organized into direction-of-motion columns, a single microelectrode can bias a local pool of similarly-tuned neurons — the spatial grain at which stimulation is effective matches the functional architecture.
5. **A small local population can move a global percept.** Activating a modest number of neurons at one MT site is sufficient to change the animal's report, implying the readout downstream weights this signal heavily.

## 4. Methods

**Subjects & task.** Rhesus monkeys performed a two-alternative forced-choice direction-discrimination task. On each trial a patch of dynamic random dots moved with a controlled fraction of dots (coherence) in one of two opposed directions; the monkey reported perceived direction with an eye movement to one of two targets.

**Stimulus placement.** The random-dot patch was centered on the receptive field of a recorded MT/V5 cluster, and the two response alternatives were aligned to that cluster's *preferred* direction and its *opposite* (null) direction, so that any stimulation-induced bias would be maximally interpretable.

**Near-threshold titration.** Motion coherence was set around psychophysical threshold and varied across a range, yielding a psychometric function so that shifts could be measured as a change in the point of subjective equality / bias rather than only as an accuracy change.

**Microstimulation.** On a randomly interleaved subset of trials, weak electrical microstimulation (low-current pulse trains through the recording microelectrode) was delivered to the direction-selective column during the motion epoch. Stimulated and non-stimulated trials were compared within session.

**Readout.** The dependent measure was the proportion of "preferred-direction" choices as a function of coherence, compared between stimulated and unstimulated trials; a stimulation-induced horizontal shift of the psychometric function indexes added evidence for the preferred direction.

## 5. Results

- On stimulated trials the monkeys chose the stimulated column's *preferred* direction significantly more often than on matched unstimulated trials.
- The psychometric function shifted horizontally toward the preferred direction — the manipulation behaved like an *increment in motion evidence* for that direction rather than a nonspecific impairment.
- The bias was specific to the direction encoded at the stimulation site; stimulating a column tuned to a different direction moved choices toward *that* direction.
- The effect was reliable across sites and animals, and was obtained with modest currents that did not evoke overt behavior beyond the choice bias, indicating a genuinely perceptual (rather than motor) locus.
- Qualitatively, the size of the induced bias was consistent with the added artificial signal summing with the real sensory evidence carried by the same and neighboring columns.

## 6. Critique / limitations

Electrical microstimulation is spatially and cell-type nonselective: it activates a local population of mixed cells (and fibers of passage) around the electrode, so the "column" being driven is only approximately the intended direction pool; later optogenetic and refined-current work sharpens this. The technique also cannot cleanly dissociate whether the added signal enters the decision at MT itself or is inherited by downstream accumulators — that dissociation required the later LIP microstimulation experiments (Hanks 2006) and reaction-time variants (Ditterich 2003). The 1990 report is a fixed-duration paradigm and therefore speaks to choice bias but not directly to the *dynamics* of evidence accumulation. Finally, the inference that a "small" population suffices is model-dependent: how many effective neurons the current recruits is uncertain, so the strong claim about downstream weighting is qualitative. The full methodological treatment (current levels, site criteria, controls) appears in the companion 1992 methods paper.

## 7. Connection to our work

**(a) Biological precedent for `attn_clamp`.** Our causal-perturbation operator adds a bias to the model's attention logits at a target location and reads the resulting change in the QR-DQN policy. Salzman 1990 is the canonical microstimulation experiment this operation is modeled on: a weak, targeted current *adds direction-specific evidence* and the animal's choice shifts lawfully toward it. Their psychometric shift is the animal-side counterpart of the policy shift we measure when we clamp attention — both are "inject a small signal at a feature-selective node, measure the decision tilt."

**(b) Sensory node, not decision node.** Critically for how we map our layers, Salzman perturbs a *sensory* representation — direction-selective MT/V5 — not a decision/accumulator area. The correct analog inside the recurrent-ViT is therefore a perturbation of the PERCEPTION stage (the conv front-end / recurrent-ViT feature tokens that carry stimulus-direction information), *not* the value/accumulator/QR-DQN readout. This is the complement to the LIP microstimulation line (Hanks 2006), which perturbs the DECISION node and maps to clamping the accumulator/value side. Our program can and should run both variants and contrast them: clamping the PRIORITY-stream features that encode motion direction (the MT analog) versus biasing the VALUE/accumulator readout (the LIP analog). A dissociation in how the RL policy responds to the two clamps is a direct model-side test of the sensory-vs-decision distinction that Salzman 1990 opened.

**(c) The RL task where this is tested: `motion4`.** `motion4` is the environment purpose-built for this comparison. It is random-dot motion-direction change-detection — the Cavanaugh & Wurtz change-detection frame with the Salzman-style stochastic-dot, opposed-direction stimulus — and it reuses the entire architecture with only the pixels swapped (moving-dot fields instead of Gabors). Because the task variable is now *motion direction*, an `attn_clamp` on the direction-carrying perception tokens is the faithful in-silico replay of Salzman's MT microstimulation, and the change-detection readout gives us a behavioral bias curve directly comparable to their psychometric shift.

**(d) A directly testable read-out prediction: winner-take-all vs averaging.** Salzman's follow-up (Salzman & Newsome 1994) showed that when a *coherent* motion stimulus and MT microstimulation specify two different directions, the animal's report tends toward a winner-take-all (vector-selection) rather than an averaging outcome. This is a falsifiable prediction on our RL policy: in `motion4`, present real coherent motion in direction A while `attn_clamp` injects evidence for direction B, and inspect whether the QR-DQN policy selects one direction (winner-take-all) or interpolates its change-report toward an intermediate direction (averaging). Whether our distributional actor-critic reproduces the winner-take-all readout — and at what relative stimulus/clamp strength the crossover occurs — is a concrete signature that connects our architecture to the primate motion-decision literature.

## 8. Citations to follow

- `salzman1992_mt_microstim_methods` — the companion methods paper (currents, site criteria, controls) for this experiment. In seed.
- `salzman_newsome1994_winner_take_all` — combines real motion with stimulation; establishes the winner-take-all vs averaging readout central to our prediction (d). In seed.
- `ditterich2003_microstim_rt` — reaction-time variant; probes the *dynamics* of how the injected signal enters accumulation. In seed.
- `hanks2006_lip_microstim` — the LIP (decision-node) parallel; the sensory-vs-decision contrast for mapping our perception-clamp vs value-clamp. In seed.
- `roitman_shadlen2002_lip_rt` — LIP accumulation signals in the same random-dot task; the accumulator our VALUE stream is analogized to. In seed.
- `gold_shadlen2007_decision_making` — synthesis of the sensory→decision framework these experiments built. In seed.
