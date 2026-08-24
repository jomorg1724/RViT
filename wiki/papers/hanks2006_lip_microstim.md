---
id: hanks2006_lip_microstim
title: "Microstimulation of macaque area LIP affects decision-making in a motion discrimination task"
authors:
  - "Hanks, Timothy D."
  - "Ditterich, Jochen"
  - "Shadlen, Michael N."
year: 2006
venue: "Nature Neuroscience"
doi: "10.1038/nn1683"
arxiv: ""
url: "https://doi.org/10.1038/nn1683"
tags:
  - primate-neurophysiology
  - lesion-microstimulation
  - decision-making
  - parietal-cortex
  - psychophysics
concepts:
  - microstimulation
  - drift-diffusion-model
  - priority-map
  - hidden-state-perturbation
related:
  - salzman1990_mt_microstim
  - salzman1992_mt_microstim_methods
  - ditterich2003_microstim_rt
  - salzman_newsome1994_winner_take_all
  - roitman_shadlen2002_lip_rt
  - gold_shadlen2007_decision_making
  - cavanaugh_wurtz2004_sc_change_blindness
  - bollimunta2018_fef_sc_covert
  - dabney2018_qr_dqn
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - pubmed
status: summary
depth: full
last_updated: "2026-07-04"
---

# Microstimulation of macaque area LIP affects decision-making in a motion discrimination task

## 1. Abstract

The lateral intraparietal area (LIP) contains neurons whose firing rates ramp up during perceptual decisions about random-dot motion, in a manner that resembles the accumulation of noisy sensory evidence toward a decision bound. Whether this ramping *causes* the decision, or merely reflects it, is a correlational question that recording alone cannot settle. Hanks, Ditterich & Shadlen applied weak electrical microstimulation to clusters of LIP neurons while monkeys performed a reaction-time direction-discrimination task, in which the animal reported the net direction of a noisy random-dot display by making a saccade to one of two choice targets. The stimulated LIP cluster was chosen so that its spatial response field overlapped one of the two choice targets. Microstimulation systematically biased the monkey's *choices* toward the target inside the response field, sped up reaction times for choices *into* that field, and slowed reaction times for choices *away* from it — without the stimulation itself directly evoking a saccade. The results causally implicate LIP in the *formation* of the decision (the accumulation of evidence toward a bound), not in the sensory encoding of the motion signal. This is the decision-stage counterpart to Salzman & Newsome's microstimulation of the sensory motion area MT: stimulating MT injects *evidence*, whereas stimulating LIP injects *accumulated evidence / decision bias*.

## 2. Why this matters for us

Our program builds a small recurrent vision-transformer (conv front-end → recurrent-ViT self-attention with a feedback mechanism → spatial xLSTM working memory → distributional QR-DQN actor-critic) trained by RL to reproduce primate visual-attention signatures, and its signature causal-perturbation tool is the **attn_clamp**: an additive bias on the model's attention logits that pushes the attention map toward or away from a location — the in-silico analog of microstimulation. This paper is the canonical *decision-node* microstimulation experiment, and it matters to us precisely because it dissociates two things our architecture keeps separate. Stimulating a **sensory** area (MT) injects fresh evidence; stimulating a **decision/association** area (LIP) injects a bias into the *already-integrated* quantity that a bound-crossing readout consumes. In our stack those are different injection sites: the perception/attention layers versus the xLSTM accumulator and the QR-DQN value head. Hanks et al. give us the biological ground truth for what should happen when we clamp at the *decision* end rather than the *sensory* end — a signed shift in choice proportion plus the characteristic RT asymmetry (faster toward, slower away). It also anchors the reaction-time discipline: LIP's causal effect shows up as much in *chronometry* as in choice, which is exactly the readout our recurrent model produces (a policy over WAIT/act with a distribution of decision times), and which the newly built **motion4** environment (random-dot motion-direction change-detection, a Cavanaugh & Wurtz 2004 analog reusing the whole architecture with only the pixels changed) makes directly testable.

## 3. Key claims

1. **LIP microstimulation biases choice toward the response-field target.** Injecting current into an LIP cluster whose response field overlapped one choice target increased the proportion of choices to that target — a signed, spatially specific bias.
2. **The effect is chronometric, and asymmetric.** Microstimulation *shortened* reaction times for choices into the stimulated response field and *lengthened* reaction times for choices away from it. The speed-up and slow-down are the signature of adding to an evidence accumulator that is racing toward one of two bounds.
3. **No direct saccade evocation.** The stimulation currents did not, by themselves, trigger saccades; the behavioral consequences are decision biases, not motor artifacts. This distinguishes the result from stimulation of oculomotor structures at suprathreshold current.
4. **LIP is a decision/association node, not a sensory-encoding node.** Because MT (sensory) and LIP (post-sensory accumulator) sit at different stages, stimulating LIP injects into the *integrated* decision variable rather than into the momentary motion evidence — the causal complement to Salzman & Newsome's MT work.
5. **Consistent with bounded-accumulation (drift-diffusion / race) models.** The joint pattern of choice bias and the toward/away RT asymmetry is quantitatively captured by adding an offset to the accumulated evidence in a race-to-bound model, tying the causal manipulation to the same framework that describes LIP ramping activity (Roitman & Shadlen 2002; Gold & Shadlen 2007).

## 4. Methods

**Task.** A monkey viewed a dynamic random-dot kinematogram whose dots carried a variable net motion strength (coherence) in one of two opposite directions. In the *reaction-time* version, the animal was free to respond whenever ready by making a saccade to whichever of two choice targets matched the perceived motion direction; decision time was therefore under the animal's control and measurable on every trial.

**Target-in-field configuration.** Recording first identified LIP neurons and their spatial response fields. A stimulation site was selected so that one of the two saccade choice targets fell *inside* the response field of the stimulated cluster; the opposite target fell outside it. This makes the response-field target the "preferred" choice for that cluster.

**Microstimulation.** Weak electrical microstimulation (a train of biphasic pulses at low current, delivered through the recording/stimulating electrode) was applied on a randomly interleaved subset of trials, time-locked to the motion-viewing / decision-formation epoch. Currents were kept low enough that stimulation alone did not evoke saccades.

**Behavioral readout.** For each coherence and each stimulation condition (stim vs no-stim), the experimenters measured (a) the proportion of choices to each target — the psychometric function — and (b) the distribution of reaction times, split by choice direction (into vs away from the stimulated field) — the chronometric function.

**Modeling.** Choice and RT data were fit with bounded-accumulation (drift-diffusion / race) models. The microstimulation effect was modeled as an added signal to the evidence accumulated in favor of the response-field target, and the fit was checked against both the choice bias and the toward/away RT asymmetry simultaneously.

## 5. Results

- **Signed choice bias.** Microstimulation shifted the psychometric function so that more choices went to the response-field target across coherences — an additive bias in favor of the stimulated alternative, largest where the sensory evidence was weak (low coherence) and the decision was most uncertain.
- **RT asymmetry.** Reaction times for choices *into* the stimulated field were shortened, and RTs for choices *away* were lengthened. This double-signed chronometric effect is the fingerprint of biasing an accumulator rather than biasing a motor plan or a sensory gain.
- **No motor artifact.** Stimulation did not evoke saccades on its own; effects were expressed through the decision, not through triggered movements.
- **Model account.** A bounded-accumulation model with an added offset to the response-field evidence reproduced the joint choice-and-RT pattern, linking the causal perturbation to the same evidence-accumulation account that describes LIP's ramping activity during unstimulated decisions.
- **Interpretation.** LIP participates causally in *decision formation* — the transformation of momentary sensory evidence into a committed choice — rather than in encoding the sensory motion signal itself. The result is the decision-stage complement to sensory-area (MT) microstimulation.

## 6. Critique / limitations

Electrical microstimulation activates a heterogeneous population near the electrode (mixed tuning, passing fibers, inhibitory as well as excitatory cells); it is not cell-type specific, so "stimulating LIP" is coarser than the accumulator-offset interpretation implies. The clean drift-diffusion account is a *sufficient* model, not a proof that LIP is the accumulator — an upstream or parallel structure biased by the same current could, in principle, produce a similar behavioral signature. The response-field-overlap design means the injected bias is inherently *spatial* (tied to the saccade target geometry), which entangles "decision variable" with "saccade goal / priority-map" interpretations; teasing decision from motor-intention is partly a matter of task framing. Effects are strongest at low coherence, so the manipulation is most legible exactly where behavior is noisiest. Finally, the study addresses two-alternative motion discrimination with a saccadic readout; whether the same causal role generalizes to change-detection, multi-alternative, or non-oculomotor report is left open (and is where a model that can vary the task cheaply is useful).

## 7. Connection to our work

**(a) Biological precedent for attn_clamp.** This is one of the two anchor microstimulation results our attn_clamp perturbation is designed to emulate — the *decision-node* anchor. Where Salzman & Newsome's MT work is the precedent for perturbing a **sensory** stage, Hanks et al. is the precedent for perturbing a **post-sensory accumulator**. The attn_clamp (additive bias on attention logits) is literally an "extra current" added at a chosen stage of the network, and this paper tells us what the *signed, chronometric* behavioral consequence of such a stage-specific injection should look like when the target stage is the decision variable rather than the sensory input.

**(b) Sensory node vs decision node — and where it maps in our stack.** This paper perturbs a **decision node (LIP)**, *not* a sensory motion area (MT/V5). That distinction is the crux for us. Clamping our **perception/attention layers** (the conv front-end + recurrent-ViT attention map) is the analog of MT-style sensory microstimulation — it changes what evidence enters the loop. Clamping toward a target at the **decision end** — biasing the xLSTM accumulator state or adding an offset to the QR-DQN action-value for the corresponding choice — is the analog of *this* paper's LIP microstimulation: it biases the already-integrated quantity that the policy reads out. The falsifiable prediction is a *dissociation*: a perception-layer clamp should behave like injecting evidence (its effect should scale with, and interact with, stimulus coherence/strength), whereas a value/accumulator clamp should behave like injecting accumulated evidence (a more coherence-independent additive choice bias plus the toward/away RT asymmetry Hanks et al. observed). Reproducing that asymmetry — faster decisions toward the clamped location, slower away — from the model's own distribution of decision times would be a strong LIP-analog result.

**(c) motion4 as the RL task to test it in.** The obvious testbed is the just-built **motion4** environment: random-dot motion-direction change-detection, the same architecture with only the pixels swapped (moving-dot fields instead of Gabors). motion4 is the closest env we have to Hanks et al.'s random-dot motion task, which makes it the natural place to run a two-target, decision-node attn_clamp and read off the psychometric shift and the chronometric (WAIT-time / RT) asymmetry against motion strength. Because motion4 reuses the whole stack, the *same* clamp machinery can be applied at the perception layer vs the value/accumulator layer to run the sensory-vs-decision dissociation above within one environment.

**(d) A directly testable read-out prediction.** Hanks et al. and the Salzman lineage motivate a concrete winner-take-all-vs-averaging question on our RL policy. If the model's decision stage does bounded accumulation with a hard bound, a decision-node clamp toward one alternative should *not* smoothly average two evidence sources but should tip a competition — a clamp that adds to one accumulator disproportionately captures the choice as coherence weakens (a winner-take-all signature), and its RT effect should be biphasic (speed toward / slow away) rather than a uniform latency shift. If instead the QR-DQN value head effectively *averages*, the clamp would produce a graded, symmetric bias with no toward/away RT split. The distributional (QR-DQN) critic gives us an extra lever here: the clamp's effect on the *quantiles* of the return distribution (does it shift the whole distribution, or fatten one tail?) is a finer read-out than choice proportion alone, and lets us test whether the model's "LIP" behaves like a bounded accumulator in a way the biology could not easily expose.

## 8. Citations to follow

- `salzman1990_mt_microstim` — the sensory-stage microstimulation anchor (MT); the complement to this decision-stage result. In valid set.
- `salzman1992_mt_microstim_methods` — methods/parametrics for MT microstimulation of direction discrimination. In valid set.
- `ditterich2003_microstim_rt` — microstimulation effects on the *time course* of decision-making; ties current injection to the accumulation dynamics. In valid set.
- `salzman_newsome1994_winner_take_all` — winner-take-all vs averaging read-out from combined motion signals; directly motivates the read-out prediction in §7(d). In valid set.
- `roitman_shadlen2002_lip_rt` — the LIP recording basis (ramping-to-bound during RT motion discrimination) that this causal study confirms. In valid set.
- `gold_shadlen2007_decision_making` — the evidence-accumulation / bounded-integration framework the result is fit within. In valid set.
- `dabney2018_qr_dqn` — the distributional value head in our stack; relevant to the quantile-level read-out prediction. In valid set.
