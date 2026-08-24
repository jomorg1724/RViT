---
id: ditterich2003_microstim_rt
title: "Microstimulation of visual cortex affects the speed of perceptual decisions"
authors:
  - "Ditterich, Jochen"
  - "Mazurek, Mark E."
  - "Shadlen, Michael N."
year: 2003
venue: "Nature Neuroscience"
doi: "10.1038/nn1094"
arxiv: ""
url: "https://doi.org/10.1038/nn1094"
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
  - salzman1990_mt_microstim
  - salzman_newsome1994_winner_take_all
  - hanks2006_lip_microstim
  - roitman_shadlen2002_lip_rt
  - gold_shadlen2007_decision_making
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - pubmed
status: summary
depth: full
last_updated: "2026-07-04"
---

# Microstimulation of visual cortex affects the speed of perceptual decisions

## 1. Abstract

Ditterich, Mazurek & Shadlen applied electrical microstimulation to direction-selective columns in extrastriate visual area MT/V5 while monkeys performed a **reaction-time** version of the random-dot motion direction-discrimination task. Whereas earlier MT-microstimulation work (Salzman et al.) established that stimulation *biases choices* toward the stimulated column's preferred direction, this study added the **chronometric (decision-latency) dimension**. Stimulation not only shifted choices toward the preferred direction but also *systematically altered reaction times*: it **quickened** decisions made in the preferred direction and **slowed** decisions made in the opposite (null) direction — an effect visible even on trials where the animal ultimately chose against the stimulated direction. The joint pattern of choice and RT effects was quantitatively consistent with MT activity supplying the momentary sensory evidence to a **bounded evidence-accumulation (drift-diffusion) decision process**: microstimulation acts by adding an offset to the accumulating decision variable, so the bound is reached sooner for one alternative and later for the other. The paper is a foundational demonstration that a causal manipulation of a *sensory* representation propagates predictably through an accumulator to shape both *what* is decided and *how fast*.

## 2. Why this matters for us

This paper is one of the clearest biological precedents for the program's core **causal-perturbation method**: the `attn_clamp` additive bias on attention logits that nudges the model's attention map toward or away from a location. Ditterich et al. do the electrophysiological version of exactly that — they inject an additive drive into a spatially/feature-tuned sensory population (an MT direction column) and read out the consequences on the downstream decision. The key methodological lesson for us is that they read out **two channels at once**: the *choice* (which alternative) and the *chronometry* (how fast). Our RViT program has both available for free — the QR-DQN actor emits a discrete policy (the choice) and the number of recurrent steps to commitment is a natural reaction-time surrogate — so this paper defines the *pair of dependent measures* a clean in-silico microstimulation experiment should report, not just the choice-bias curve.

It also pins down *where in the circuit* the manipulation lives. Ditterich et al. stimulate a **sensory** node (MT) that feeds evidence *into* an accumulator that lives elsewhere (LIP/FEF). The signature of a sensory-node perturbation is specific: the effect scales/interacts with the physical stimulus and looks like an added drift term, so it speeds one direction and slows the other roughly symmetrically. That is a different fingerprint from perturbing the *accumulator itself*. This distinction is precisely the fork the program cares about — whether an `attn_clamp` is being applied at the PRIORITY perception stage (sensory-node analog) or deeper toward the VALUE / QR-DQN accumulator (decision-node analog) — and this paper gives us the ground-truth behavioral signature of the sensory case to check our model against.

## 3. Key claims

1. **MT microstimulation biases choices toward the stimulated column's preferred direction**, replicating and extending the classic Salzman/Newsome result in a reaction-time paradigm.
2. **Microstimulation changes decision latency, not just choice.** It *shortened* RTs for decisions made in the stimulated (preferred) direction and *lengthened* RTs for decisions made in the opposite direction.
3. **The RT effect appears even on opposite-direction choices** — i.e., stimulation left a chronometric fingerprint on trials where it did *not* win the choice, showing it perturbs the ongoing deliberation rather than merely re-labeling the outcome.
4. **The joint choice + RT data are quantitatively captured by a bounded accumulation (drift-diffusion) model** in which stimulation adds an offset to the sensory evidence entering the integrator.
5. **MT supplies momentary evidence to a downstream integrator.** The results are consistent with MT activity being *read into* an accumulation process (in LIP/FEF) rather than MT itself being the site of accumulation or commitment.
6. **A single mechanism — additive drive on the evidence — accounts for both dependent measures**, unifying the choice-bias and chronometric effects under one parameter change.

## 4. Methods

- **Task.** Two-alternative random-dot motion **direction-discrimination** in a **reaction-time** design: the monkey viewed a dynamic random-dot kinematogram at variable motion coherence and reported perceived net direction with a saccade *whenever it was ready*, yielding both accuracy and a measured decision latency on every trial.
- **Neural manipulation.** Electrical **microstimulation** delivered to direction-selective columns in **MT/V5**, identified physiologically by their preferred direction, during a subset of trials interleaved with unstimulated controls.
- **Design.** Coherence was varied across a range (including zero-coherence trials) and stimulation was applied on half of trials, so choice-probability *and* RT could be compared stimulated-vs-control as a function of signed motion strength.
- **Analysis.** Psychometric (proportion preferred-direction choices vs coherence) and **chronometric** (mean RT vs coherence, split by chosen direction) functions were fit. A **bounded evidence-accumulation / drift-diffusion model** was fit to the joint choice-and-RT data, with microstimulation modeled as an added offset to the momentary evidence feeding the integrator; alternative accounts (e.g., a pure choice-bias with no evidence effect) were compared against this.

## 5. Results

- **Choice bias.** Stimulation shifted the psychometric function toward the electrode's preferred direction — more preferred-direction choices at matched coherence, strongest near threshold, as expected from the MT-microstimulation literature.
- **Chronometric asymmetry.** Stimulation produced a directionally *asymmetric* RT effect: **faster** responses for preferred-direction choices and **slower** responses for null-direction choices, relative to control.
- **Effect survives on the losing side.** The RT slowing on opposite-direction trials shows stimulation biased the *deliberation* itself — it did not simply relabel outcomes but changed the time course of accumulation on trials that still ended in the non-stimulated choice.
- **Model fit.** A single drift-diffusion model in which stimulation adds a fixed offset to the evidence stream reproduced *both* the shifted psychometric function and the asymmetric chronometric functions. The offset-on-evidence account outperformed accounts that treated stimulation as a late, post-decisional bias.
- **Interpretation.** The data localize MT's role to *supplying sensory evidence* that is then integrated to a bound downstream; the bound-crossing (commitment) machinery is elsewhere. Microstimulation is, functionally, an added drift term.

## 6. Critique / limitations

- **Sensory site, inferred mechanism.** The accumulator itself (LIP/FEF) was not recorded here; the drift-diffusion interpretation is inferred from behavior + model fitting, not from simultaneously observing the downstream integrator. The RT signature is *consistent* with an added-evidence account but does not directly image the accumulation.
- **Microstimulation is spatially/functionally coarse.** Electrical stimulation excites a volume of tissue with mixed tuning and unknown antidromic/network spread; "the preferred direction of the column" is an idealization. The injected signal is not a clean, graded, single-feature drive of known magnitude.
- **Effect size depends on column selectivity and stimulation parameters** (current, site homogeneity), which vary across penetrations; the mapping from stimulation current to equivalent added coherence is estimated, not fixed.
- **Two-alternative, one feature dimension.** The task isolates a single motion axis with two responses. Whether the same additive-drift account holds for many-alternative or higher-dimensional decisions (or for feature dimensions other than direction) is an extrapolation.
- **Non-decision time and urgency.** RT-based DDM fits must partition latency into decision vs non-decision components and assume a particular bound policy (fixed vs collapsing); different assumptions can absorb some of the chronometric effect.

## 7. Connection to our work

**(a) Biological precedent for `attn_clamp`.** This is arguably the sharpest single-study justification for the program's causal-perturbation operator. `attn_clamp` adds a bias to the model's attention logits at a chosen location; Ditterich et al. add electrical drive to a tuned sensory population and show it behaves like adding an **offset to the evidence** feeding a bounded integrator. That is exactly the functional form our additive-logit clamp is meant to instantiate. Their result licenses the interpretation of an `attn_clamp` toward a location as "inject evidence for that location's alternative," and predicts the *shape* of the expected effect (a shifted policy plus an asymmetric change in steps-to-commitment).

**(b) Sensory node vs decision node — which layer to clamp.** Ditterich et al. perturb a **sensory** node (MT/V5), upstream of the accumulator. In our architecture the sensory-node analog is the **PRISM perception stage / PRIORITY stream** (the recurrent-ViT self-attention that forms the spatial map), *not* the VALUE / QR-DQN accumulator. So the direct mapping is: clamping attention logits in the perception/PRIORITY layer ≈ MT microstimulation; clamping or offsetting the QR-DQN value estimate (the accumulator/decision node) would instead be the **LIP-microstimulation** analog (cf. `hanks2006_lip_microstim`). The two should leave *different fingerprints* — a perception-layer clamp should interact with stimulus strength and speed one alternative while slowing the other (the Ditterich signature); a value/accumulator-layer clamp should look more like a shift of the starting point or bound. Running both clamp sites in-silico and matching each to its biological signature is a concrete, high-value experiment this paper defines.

**(c) The `motion4` battery is the RL task this lives in.** Crucially, Ditterich et al. used **random-dot motion direction-discrimination** — which is exactly the paradigm the newly built **`motion4`** environment reproduces (moving-dot fields swapped in for Gabors, whole architecture otherwise unchanged). That makes `motion4` the *native* substrate for reproducing this study: we can add an `attn_clamp` biasing the model toward one motion direction's location/feature during a `motion4` trial and read out (i) the shift in the QR-DQN policy (choice bias) and (ii) the change in recurrent steps-to-commitment (chronometric effect), split by the model's chosen direction. Matching the **asymmetric RT signature** — faster for the clamped direction, slower for the opposite, present even on opposite-direction choices — would be a strong in-silico replication.

**(d) Directly testable read-out prediction.** The paper's added-drift account predicts a *graded, coherence-interacting* effect: the clamp should matter most near psychometric threshold and its RT signature should be direction-asymmetric rather than a uniform speed-up. This is a falsifiable prediction on the RL policy. It also sets up the companion winner-take-all-vs-averaging question (see `salzman_newsome1994_winner_take_all`): does a clamp toward one location make the policy *commit* to that location (winner-take-all) or *blend* the clamped and stimulus-driven evidence (averaging)? Our QR-DQN actor's response distribution under graded clamp strength directly adjudicates this on `motion4`.

## 8. Citations to follow

- `salzman1990_mt_microstim` — the foundational MT-microstimulation choice-bias result this paper extends into the RT domain. On valid list; card not yet in seed.
- `salzman_newsome1994_winner_take_all` — winner-take-all vs averaging read-out of MT microstimulation; the read-out question for our clamp experiment. On valid list; card not yet in seed.
- `hanks2006_lip_microstim` — microstimulation of the *decision* node (LIP) rather than the sensory node; the decision-layer analog of our clamp. On valid list; card not yet in seed.
- `roitman_shadlen2002_lip_rt` — LIP ramp-to-bound in the RT motion task; the accumulator this study feeds into. On valid list.
- `gold_shadlen2007_decision_making` — canonical drift-diffusion review; the framework the joint choice+RT fit rests on. In seed, full depth.
- Mazurek, Ditterich, Palmer & Shadlen (2003), "A role for neural integrators in perceptual decision making" — companion integrator-model paper. Not in seed.
- Ditterich (2006), "Stochastic models of decisions about motion direction" — follow-up modeling of the chronometric data. Not in seed.
