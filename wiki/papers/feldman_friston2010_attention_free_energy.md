---
id: feldman_friston2010_attention_free_energy
title: "Attention, uncertainty, and free-energy"
authors:
  - "Feldman, Harriet"
  - "Friston, Karl J."
year: 2010
venue: "Frontiers in Human Neuroscience"
doi: "10.3389/fnhum.2010.00215"
arxiv: ""
url: "https://doi.org/10.3389/fnhum.2010.00215"
tags:
  - free-energy-principle
  - visual-attention
  - theoretical-essay
  - posner-cuing
  - predictive-coding
concepts:
  - precision-weighting
  - attention-as-prediction-error
  - variational-free-energy
  - active-inference
  - hierarchical-predictive-coding
  - cueing-effect
related:
  - friston2010_fep_unified_theory
  - rao_ballard1999_predictive_coding
  - bastos2012_canonical_microcircuits
  - keller_mrsic_flogel2018_pc_review
  - desimone_duncan1995_biased_competition
  - spratling2008_pc_biased_competition
  - posner1980_orienting
  - pezzulo_parr_friston2024_active_inference
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_92
status: full
depth: full
last_updated: "2026-05-16"
---

# Attention, uncertainty, and free-energy

## 1. Abstract

The authors propose that attention can be understood as inferring the *precision* (inverse variance) of sensory data during hierarchical perception. Under the free-energy principle, neuronal activity encodes a probabilistic representation of the world that optimizes free-energy in a Bayesian fashion; because free-energy bounds surprise or the negative log-evidence for internal models, this optimization can be regarded as evidence accumulation or generalized predictive coding. Crucially, both *predictions* about the state of the world generating sensory data *and* the *precision* of those data must be optimized. If precision depends on the state of the world being inferred, one can explain many aspects of attention. The authors illustrate this with neuronal simulations of the Posner spatial-cuing paradigm, generating both psychophysical and electrophysiological responses consistent with attentional bias or gating, competition for attentional resources, attentional capture, and the speed-accuracy trade-off. With both attended and non-attended stimuli simultaneously, biased competition for neuronal representation emerges as a principled property of Bayes-optimal perception.

## 2. Why this matters for us

Feldman & Friston 2010 is the canonical paper for the *attention-as-precision-weighting* interpretation. It is the load-bearing citation for the user's commitment to multiplicative gain modulation as the architectural substrate of attention. The Feedback Transformer's Hadamard-product structure ([feedback_transformer](research_db/concepts/feedback_transformer.md)) is the network-level implementation of the precision-weighting mechanism this paper formalizes. The recurrent ViT paper (2502.10955) reports cued-attention effects (faster RT and higher accuracy at the cued location, scaling with cue validity) — Feldman & Friston explain *why* those effects should follow from a Bayes-optimal architecture: cue validity is a prior on precision, and precision controls the gain on prediction-error signals from the cued location.

## 3. Key claims

1. Attention is not a separate cognitive process but the operation of *precision inference* within the standard free-energy framework. The brain estimates both the latent causes of sensations (mean) and the reliability of the data (precision); attention is the latter.
2. Under hierarchical predictive coding, precision controls the gain on prediction-error pathways. Increasing precision at a given level scales up the contribution of that level's prediction errors to higher-level state updates — *enhancing* attended information.
3. State-dependent precision (precision that depends on the current inferred state) is sufficient to generate the empirical signatures of selective attention: spatial cuing effects, validity-dependent reaction time changes, attentional capture, biased competition for representation.
4. The Posner spatial-cuing paradigm is reproduced quantitatively. A precision parameter controlled by the cue produces faster mean responses and higher accuracy at the cued location, with the magnitude of the effect scaling with cue validity — exactly the empirical signature.
5. Biased competition (Desimone & Duncan 1995) emerges naturally: when two stimuli compete for representation, the one with higher precision (attended) wins the competition. Biased competition does not need to be added as a separate mechanism; it is a consequence of precision-weighted Bayesian inference.
6. The framework provides a single computational substrate for spatial attention, feature attention, attentional capture, and the speed-accuracy trade-off — all four are different parameterizations of state-dependent precision.

## 4. Methods

Theoretical and simulation paper. The authors formulate the free-energy minimization problem with explicit precision parameters: at each hierarchical level, the prediction error $\epsilon_\ell = r_\ell - g_{\ell+1}(r_{\ell+1})$ is weighted by a precision $\pi_\ell$, giving the free-energy term $\pi_\ell \epsilon_\ell^2 / 2$. The model assumes that $\pi_\ell$ depends on the inferred state at the next-higher level — i.e., the brain infers not only what's there but also how reliable each sensory channel is.

They implement two-level neuronal simulations of the Posner cuing paradigm. A cue arrives at one of two spatial locations; the cue increases the precision parameter for that location's prediction-error pathway. A target then appears, either at the cued location (valid) or the opposite location (invalid). The model produces simulated psychophysical reaction times and accuracy plus simulated electrophysiological responses (event-related potentials). Cue-validity effects are reproduced by setting different invalid-trial precision values.

For biased competition, two stimuli are presented simultaneously; the cue determines which receives higher precision. The model's representation of each stimulus is then plotted as a function of cue location.

## 5. Results

The simulations reproduce:

- **Spatial cuing effects.** Cued targets elicit faster reaction times and higher accuracy than uncued targets. The effect grows with cue validity (the proportion of valid trials).
- **Cost-benefit pattern.** Valid cues produce a benefit (faster RT than neutral); invalid cues produce a cost (slower RT than neutral). The cost-benefit asymmetry matches the empirical Posner-paradigm pattern.
- **Biased competition for representation.** When two stimuli compete for neuronal representation, the cued stimulus wins — the model's "neuronal" response is dominated by the attended item, matching Reynolds & Chelazzi 2004 single-cell results.
- **Speed-accuracy trade-off.** Increasing precision speeds the response but at the cost of integration; varying precision globally produces a smooth speed-accuracy trade-off curve.
- **Endogenous vs exogenous attention.** Endogenous (cued) attention corresponds to a top-down precision modulation from higher cortical levels; exogenous (capture) attention corresponds to a bottom-up modulation driven by stimulus-level precision (high-contrast, novel, or otherwise salient stimuli). Both fall out of the same framework with different parameter settings.

## 6. Critique / limitations

The framework is theoretical. The precision-weighting mechanism is mathematically natural but its biological implementation is underspecified. Candidate substrates include cholinergic neuromodulation (Bastos 2012 canonical microcircuit), inhibitory SST+/VIP+ gating of apical dendrites (Larkum 2013), and pulvinar-mediated gating (Sherman 2022). The paper does not commit to one; the empirical adjudication is still ongoing.

The simulations are stylized. The Posner paradigm is reproduced qualitatively but the model has many free parameters (precision values, time constants, gain functions). The fit to empirical RT distributions is at the level of "matches the qualitative pattern," not "predicts quantitative numbers without parameter tuning."

The framework reduces attention to one variable (precision). This may be an oversimplification. Real attention has spatial, feature, and object-based components that may need separate mechanisms. The paper argues these can all be captured by state-dependent precision, but doesn't demonstrate this for, say, feature-based attention with naturalistic stimuli.

The relationship between precision weighting and the Spratling 2008 biased-competition reframing is not fully worked out. Both papers reproduce Posner-style effects; the difference is that Spratling does it without explicit precision parameters, using only the architecture of predictive coding plus competitive dynamics. The two accounts may be equivalent at the population level.

The simulations do not engage with the temporal dynamics of attention beyond the cue-target interval. Real attention has rich temporal structure (rhythmic sampling, theta-band fluctuations); the paper's framework can in principle accommodate these but does not yet.

## 7. Connection to our work

This paper is the load-bearing theoretical citation for several architectural commitments in the user's program:

**The Feedback Transformer's multiplicative structure as precision weighting.** The Feedback Transformer ([concepts/feedback_transformer.md](research_db/concepts/feedback_transformer.md)) combines sensory and feedback Q/K projections via Hadamard product. Under Feldman & Friston's framework, this is precision weighting at the attention-map level: the feedback projection $c_q$ acts as a *precision* modulator on the sensory projection $s_q$. Q–K inner products grow where both factors agree (high precision, attended location) and shrink where they disagree (low precision, ignored location). The Feedback Transformer is therefore the network-level analog of state-dependent precision.

**Cued attention in the recurrent ViT.** The 2502.10955 result that cued targets show faster RT and higher accuracy, scaling with cue validity, is exactly the empirical signature Feldman & Friston's framework predicts. The recurrent ViT's cue token sets a *precision* on the spatial map; the change-detection process is then gated by that precision. This is the predictive-coding interpretation of the published result.

**PRISM's saliency-gated update.** PRISM v1 ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.7) uses the prediction-error magnitude $|S_t|$ to gate the memory update. Feldman & Friston's framework reframes this: the update gate is precision-weighted (precision is high where the prediction-error is large), and the resulting state update is the Bayesian posterior given current evidence weighted by reliability.

**Biased competition as Bayes-optimal.** The user's competition-emergent-PC thesis ([concepts/coalition_resource_competition.md](research_db/concepts/coalition_resource_competition.md)) treats competition between coalitions as a *strategic* phenomenon. Feldman & Friston's biased-competition derivation is the *Bayes-optimal* analog: when two stimuli compete for representation, precision-weighting determines the winner. The user's program extends this from sensory-stimulus competition to *coalition* competition; the precision-weighting mathematics is the same.

The recurrent ViT paper does not cite Feldman & Friston explicitly. Any manuscript extending the recurrent ViT into a predictive-coding-explicit framework should cite this paper as the canonical attention-as-precision-weighting reference.

## 8. Citations to follow

- `friston2010_fep_unified_theory` — the broader free-energy framework. In seed, full depth.
- `bastos2012_canonical_microcircuits` — the laminar implementation of precision weighting. In seed, full depth.
- `rao_ballard1999_predictive_coding` — the predictive-coding foundation. In seed, full depth.
- `spratling2008_pc_biased_competition` — alternative biased-competition account. In seed, full depth.
- `desimone_duncan1995_biased_competition` — the biased-competition framework. In seed, full depth.
- `pezzulo_parr_friston2024_active_inference` — modern active-inference review. In seed.
- `parr_friston2019_active_inference_review` — active inference review; not in seed but a natural addition.
- `hohwy2012_predictive_processing_attention` — philosophical analysis of attention-as-precision. Not in seed.
