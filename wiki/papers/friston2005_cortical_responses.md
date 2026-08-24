---
id: friston2005_cortical_responses
title: "A theory of cortical responses"
authors:
  - "Friston, Karl"
year: 2005
venue: "Philosophical Transactions of the Royal Society B"
doi: "10.1098/rstb.2005.1622"
arxiv: ""
url: "https://doi.org/10.1098/rstb.2005.1622"
tags:
  - free-energy-principle
  - predictive-coding
  - theoretical-essay
  - cortical-anatomy
concepts:
  - variational-free-energy
  - hierarchical-predictive-coding
  - rao-ballard-coding
  - expectation-maximization-inference
related:
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - bastos2012_canonical_microcircuits
  - clark2013_whatever_next
  - pezzulo_parr_friston2024_active_inference
  - felleman_vanessen1991_hierarchical_cortex
  - sherman_guillery2011_distinct_functions
  - bastos2015_laminar_macaque
  - larkum_zhu_sakmann1999_bac_firing
  - spratling2008_pc_biased_competition
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# A theory of cortical responses

## 1. Abstract

This article concerns the nature of evoked brain responses and the principles underlying their generation. Friston starts with the premise that the sensory brain has evolved to *represent* or *infer* the causes of changes in its sensory inputs. The problem of inference is well formulated in statistical terms, and the statistical fundaments of inference afford important constraints on neuronal implementation. By formulating Helmholtz's ideas on perception in terms of modern-day statistical theories, one arrives at a model of perceptual inference and learning that explains a remarkable range of neurobiological facts. Both inference (perceptual inference) and learning (perceptual learning) can be resolved using exactly the same principle: minimizing the brain's *free energy*, as defined in statistical physics. The framework rests on empirical Bayes and hierarchical models of how sensory input is caused. The hierarchical structure enables the brain to construct prior expectations in a dynamic and context-sensitive fashion. The treatment predicts: hierarchical sensory cortex; reciprocal connections; functional asymmetry between forward (driving) and backward (driving + modulatory) connections; associative plasticity; spike-timing-dependent plasticity; extra-classical receptive-field effects; long-latency / endogenous evoked components; attenuation of prediction-error responses with perceptual learning; mismatch negativity (MMN), P300, repetition suppression; behavioral correlates including priming and global precedence; and many others.

## 2. Why this matters for us

Friston 2005 is the *foundational paper* of the free-energy-principle / variational-Bayesian-cortex framework. Where Rao & Ballard 1999 introduced hierarchical predictive coding as a specific computational architecture, Friston 2005 *generalizes* it to a full variational-Bayes framework grounded in statistical physics. The paper is the immediate ancestor of Friston 2010 ([friston2010_fep_unified_theory](research_db/papers/friston2010_fep_unified_theory.md)) and the basis for almost every subsequent active-inference paper. For the user's program, this paper is the load-bearing citation for treating PRISM's variational free-energy auxiliary loss ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.11) as a principled biological model rather than just an engineering trick.

## 3. Key claims

1. **The brain infers causes of sensory input.** The cortex's primary computation is *inference* — estimating latent causes of sensory data — formalized in statistical terms.
2. **Free-energy minimization unifies inference and learning.** Both perceptual inference (estimating states from observations) and perceptual learning (estimating parameters from many observations) minimize the same quantity: the *variational free energy* $\mathcal{F} = \langle \log q - \log p \rangle$. Inference updates states; learning updates parameters; both decrease free energy.
3. **Empirical Bayes and hierarchical models.** The framework rests on hierarchical generative models where each level provides priors for the level below. The hierarchy implements *empirical Bayes*: priors are estimated from data rather than fixed.
4. **Specific architectural predictions.** The framework predicts:
   - Sensory cortex should be hierarchical.
   - Connections should be reciprocal (forward + backward).
   - Forward connections should be *driving*; backward connections should be both *driving and modulatory*.
5. **Specific physiological predictions.** Associative plasticity should be the rule; spike-timing-dependent plasticity is consistent with the framework.
6. **Specific electrophysiological predictions.** Classical and extra-classical receptive-field effects, long-latency / endogenous components of evoked responses, attenuation of responses to predicted stimuli, mismatch negativity (MMN), P300, repetition suppression — all fall out of the framework.
7. **Specific psychophysical predictions.** Priming and global precedence — phenomena where context affects perception — are framework consequences.

## 4. Methods

This is a *theoretical / synthesis paper*. Friston builds the framework step by step:

**Step 1 — Helmholtzian perception.** The brain infers causes from sensory effects. This is the Helmholtz unconscious-inference framing.

**Step 2 — Bayes as the optimal inference rule.** Posterior over latent causes given observations $o$ and prior $p(c)$: $p(c|o) \propto p(o|c) p(c)$. For most realistic generative models, exact Bayesian inference is intractable.

**Step 3 — Variational approximation.** Approximate the true posterior $p(c|o)$ with a tractable distribution $q(c)$. Minimize the KL divergence $\text{KL}(q \| p(\cdot|o))$. This is variational Bayes. The free-energy bound: $\log p(o) \geq -\mathcal{F}[q, p]$ where $\mathcal{F}$ is the variational free energy.

**Step 4 — Inference is free-energy minimization.** Updating $q$ to track the changing posterior is implemented by gradient descent on $\mathcal{F}$. This gives a continuous-time inference dynamics that the cortex's recurrent activity is hypothesized to implement.

**Step 5 — Learning is also free-energy minimization.** Learning the generative model parameters is implemented by gradient descent on the *expected* free energy across many observations. The same loss; different optimization variables.

**Step 6 — Hierarchical models give empirical Bayes.** Stacking generative-model layers, with each layer's expectations being the next layer's priors, implements empirical Bayes. The hierarchy is the architectural form.

**Step 7 — Map onto cortical anatomy.** Forward (ascending) projections carry prediction errors; backward (descending) projections carry predictions. Reciprocal connectivity is the cortical architectural form. Bastos et al. 2012 ([bastos2012_canonical_microcircuits](research_db/papers/bastos2012_canonical_microcircuits.md)) later refined this with cell-type-specific predictions.

## 5. Results

The framework makes a remarkable number of empirical predictions, all of which fall out of the same free-energy-minimization principle:

- **Hierarchical reciprocal cortex.** Confirmed by Felleman & Van Essen 1991 ([felleman_vanessen1991_hierarchical_cortex](research_db/papers/felleman_vanessen1991_hierarchical_cortex.md)) anatomical work and subsequent connectivity studies.
- **Forward = driving, backward = modulatory + driving.** Confirmed by Sherman & Guillery work ([sherman_guillery2011_distinct_functions](research_db/papers/sherman_guillery2011_distinct_functions.md)) and subsequent macaque studies (Bastos 2014, [bastos2015_laminar_macaque](research_db/papers/bastos2015_laminar_macaque.md)).
- **Associative plasticity.** STDP at apical dendrites (Larkum 1999, [larkum_zhu_sakmann1999_bac_firing](research_db/papers/larkum_zhu_sakmann1999_bac_firing.md)) confirms.
- **Extra-classical receptive-field effects.** Rao & Ballard 1999 showed these emerge naturally in hierarchical predictive-coding networks.
- **Mismatch negativity (MMN), P300, repetition suppression.** All have been reproduced by predictive-coding models with appropriate parameters.
- **Behavioral correlates.** Priming (faster RT to expected stimuli), global precedence (large-scale structure processed before details) — both consistent with predictive-coding architecture.

## 6. Critique / limitations

The framework's *empirical predictions* are well-supported but not *uniquely* supported. Many predictions (mismatch responses, expectation suppression, laminar asymmetry) can be reproduced by alternative architectures (divisive normalization with feedback, Spratling 2008). The framework's *generality* is both its strength and its weakness.

The mathematical machinery is *substantial*. The variational free energy framework, the empirical Bayes hierarchy, the connection to statistical physics — all require significant theoretical background to apply correctly. The framework's translation to specific empirical predictions can be opaque.

The paper is *theoretical*. No new experimental data are presented; the contribution is the framework. Empirical validation has come from many subsequent papers; Friston 2005 establishes the framework.

The relation to *biological substrates* is suggestive rather than determinate. The framework predicts hierarchical cortex with reciprocal connections; it doesn't uniquely specify which cell types implement which computational role. Bastos 2012 added the cell-type assignments; Friston 2005 is silent on them.

The mathematical commitments (Gaussian likelihoods, mean-field approximation, gradient-descent dynamics) are *modelling choices*. The framework would survive different choices, but specific empirical predictions might differ.

The framework is *cortex-centric* — it focuses on sensory cortex and inference. The integration with subcortical structures (basal ganglia, thalamus, cerebellum) and with reward / motor learning is left to subsequent work.

## 7. Connection to our work

This paper is the *direct theoretical ancestor* of PRISM's variational free-energy framework:

**PRISM's variational free-energy loss.** PRISM v1's auxiliary objective ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.11) is the variational free energy applied to the predictive-coding architecture. Friston 2005 is the foundational citation for treating this as a principled biological model rather than just a tractable approximation.

**The inference-and-learning unification.** PRISM's training mechanism updates both states (the recurrent memory) and parameters (the network weights) via gradient descent on the same overall objective. Friston 2005 supplies the theoretical framing: inference and learning are both free-energy minimization, with the same loss function over different variables.

**The hierarchy-as-empirical-Bayes framing.** PRISM v2's two-level hierarchy ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10) implements empirical Bayes: the V2-level memory state acts as a prior for the V1-level inference. Friston's hierarchical-empirical-Bayes framing is the theoretical commitment.

**Forward driving + backward driving-and-modulatory.** PRISM v2's slow-FiLM mechanism modulates V1 features via the slow memory. This matches Friston's prediction that backward connections are both driving and modulatory. The architectural choice is biologically warranted.

**Extension to the user's coalition-competition framing.** Friston 2005 frames the *goal* of cortical computation as inferring causes of sensory input. The user's coalition-competition thesis reinterprets the goal: top-down predictions are predictions of *competing coalitions*, not just of sensory input. The architectural commitments (hierarchical, reciprocal, free-energy-minimizing) are inherited; the goal is reframed. This is one of the user's substantive theoretical extensions of the Friston tradition.

The recurrent ViT paper cites Friston 2010 in its bibliography (refs [91]–[95]). Friston 2005 is the earlier, more architectural-focused paper. Future manuscripts on PRISM should cite both: Friston 2005 for the variational-cortex framing, Friston 2010 for the unified-brain-theory generalization.

## 8. Citations to follow

- `friston2010_fep_unified_theory` — the next-step generalization to "free energy principle." In seed, full depth.
- `rao_ballard1999_predictive_coding` — the predictive-coding architecture. In seed, full depth.
- `bastos2012_canonical_microcircuits` — cell-type-level implementation. In seed, full depth.
- `clark2013_whatever_next` — philosophical synthesis. In seed, full depth.
- `pezzulo_parr_friston2024_active_inference` — modern active-inference review. In seed, full depth.
- `friston_kilner_harrison2006_free_energy_brain` — the parallel 2006 paper. In seed.
- `friston2003_dynamic_causal_modelling` — DCM foundation. Not in seed.
- `friston_kiebel2009_predictive_coding` — explicit predictive-coding implementation of the framework. Not in seed.
