---
id: friston2010_fep_unified_theory
title: "The free-energy principle: a unified brain theory?"
authors:
  - "Friston, Karl"
year: 2010
venue: "Nature Reviews Neuroscience"
doi: "10.1038/nrn2787"
arxiv: ""
url: ""
tags:
  - free-energy-principle
  - predictive-coding
  - theoretical-essay
  - review
concepts:
  - variational-free-energy
  - active-inference
  - precision-weighting
  - hierarchical-predictive-coding
  - generative-decoder
  - bidirectional-hierarchical-feedback
  - iterative-variational-encoder-decoder
related:
  - rao_ballard1999_predictive_coding
  - feldman_friston2010_attention_free_energy
  - bastos2012_canonical_microcircuits
  - buckley2017_fep_mathematical
  - mazzaglia2022_fep_deep_learning
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# The free-energy principle: a unified brain theory?

## 1. Abstract

The free-energy principle (FEP) proposes that all self-organizing systems — including the brain — minimize an upper bound on their surprise (negative log-evidence) called the variational free energy. Under standard assumptions (Gaussian likelihoods, point-estimate or Laplace posteriors), free-energy minimization decomposes into two interpretable terms: an accuracy term (squared prediction error) and a complexity term (KL divergence between posterior and prior). The brain implements free-energy minimization via two coupled mechanisms: perception (updating the brain's internal generative model to better explain sensory input) and active inference (selecting actions to make sensory input more predictable). The paper unifies perception, learning, attention, and action under a single variational objective, and provides a theoretical bridge between predictive-coding accounts of perception and reward-maximization accounts of behavior.

## 2. Why this matters for us

The free-energy principle is PRISM's overarching theoretical framework. The auxiliary loss used in PRISM is the variational free-energy accuracy term, under a Gaussian likelihood assumption (`THESIS.md` §2.11). The same framework justifies (a) PRISM's single-objective architecture (no task-specific auxiliary losses), (b) the inner variational-inference loop (`THESIS.md` §2.8) as iterative free-energy minimization with respect to the posterior, (c) the precision-weighting interpretation of the saliency map (`THESIS.md` §2.6, citing Friston). Without the FEP, the "single loss for any temporal sensory environment" claim PRISM makes would be ad-hoc.

## 3. Key claims

1. Free-energy minimization is a necessary consequence of any self-organizing system that maintains itself in a non-equilibrium steady state against entropic decay; it is not a hypothesis to be tested but a constraint that any such system must satisfy.
2. Variational free energy $F = -\langle \log p(o, s) \rangle_q + \langle \log q(s) \rangle_q$ is an upper bound on surprise $-\log p(o)$; minimizing $F$ minimizes surprise.
3. Under Gaussian likelihoods and point-estimate posteriors, free energy reduces to squared prediction error plus a KL-divergence term; perception is therefore prediction-error minimization (the Rao-Ballard form).
4. Action serves the same objective: the system acts to make sensory input conform to its internal model. This is "active inference" — perception by attention to current evidence, action by attention to future evidence.
5. Attention corresponds to precision-weighting of sensory channels: high-precision channels are those where the generative model expects to see substantial prediction error and is willing to integrate it strongly. Attention is therefore intrinsic to the free-energy framework, not an add-on.
6. The framework unifies several otherwise disparate theories: predictive coding (Rao & Ballard 1999), the Bayesian brain hypothesis, the infomax principle, optimal control theory, and reward-maximizing accounts of behavior.

## 4. Methods

The paper is a theoretical synthesis, not an empirical study. Its core technical content is the variational decomposition:

$$
F = \underbrace{D_\text{KL}[q(s) \| p(s | o)]}_{\geq 0} \underbrace{- \log p(o)}_{\text{surprise}}
$$

so that $F \geq -\log p(o)$ for any choice of approximate posterior $q$. Minimizing $F$ both improves $q$ (the perception step, since $D_\text{KL}$ vanishes when $q = p(s|o)$) and minimizes surprise. Under specific assumptions:

- **Laplace approximation** ($q$ is Gaussian centered at the posterior mode): free energy becomes a quadratic in the posterior mean.
- **Gaussian likelihood** ($p(o|s) = \mathcal{N}(g(s), \Sigma)$): the accuracy term becomes squared prediction error weighted by precision $\Sigma^{-1}$.
- **Hierarchical generative model**: free energy decomposes into a sum over levels, with each level minimizing its own residual prediction error.

The result is a framework that derives, from variational principles alone, the Rao-Ballard hierarchical predictive-coding architecture and its precision-weighting attention mechanism.

Active inference adds a second variational step: actions are selected to minimize expected free energy under the agent's model of future observations. This is what distinguishes Friston's framework from pure predictive-coding accounts of perception.

## 5. Results

The paper presents no new empirical results. Its contributions are:

- A unified theoretical framework that derives several previously separate cortical/cognitive theories from a single variational objective.
- A precise mapping between the cortical architecture (hierarchical, with feedback and feedforward pathways, with neuromodulatory gain control) and the components of variational free-energy minimization.
- A program of research: subsequent work has tested specific FEP predictions in fMRI, EEG, and behavior, with mixed success.

The paper is widely cited but its empirical predictions are loose — the framework is flexible enough to accommodate many findings post-hoc.

## 6. Critique / limitations

The FEP has been criticized for being empirically un-falsifiable in its strong form: any biological observation can be reinterpreted as free-energy minimization under some choice of generative model, prior, and likelihood. This is the principal criticism (van Es 2021; Colombo & Wright 2021): the framework's flexibility makes it hard to specify what would falsify it.

The precise mapping to cortical anatomy is also under-determined. Bastos et al. (2012) propose a specific canonical-microcircuit form, but alternative laminar mappings of "prediction" and "error" cells exist (Spratling 2008; Heeger 2017 "theory of cortical function").

The active-inference component is mathematically natural but computationally expensive: optimizing over future actions under uncertainty is intractable for any but the simplest environments. Practical implementations (e.g., the AIF tutorials by Sajid et al. 2021) rely on heavy approximations whose biological realism is unclear.

From a machine-learning perspective, FEP shares structure with variational autoencoders (Kingma & Welling 2014) and amortized variational inference. The conceptual contribution of FEP over standard VI is mostly its biological interpretation, not new mathematical content.

## 7. Connection to our work

PRISM v1 is a Friston-framework model in the following precise sense (`THESIS.md` §1.3, §2.11):

- The generative model is the pair $(\tilde g, g)$ of pixel and feature decoders.
- The posterior is the recurrent memory state $M_t$, treated as a point estimate (Laplace approximation).
- The free-energy accuracy term is the squared prediction error $\|x_t - \tilde g(M_{t-1})\|^2$ plus the feature-level $\|V_t - g(M_{t-1})\|^2$.
- The inner variational-inference loop (`THESIS.md` §2.8) is iterative gradient descent on free energy with respect to $M$.
- The saliency map $S_t$ is the per-location prediction-error magnitude — exactly the quantity Friston identifies with precision-weighted attention.

PRISM does *not* implement active inference. The action policy is a learned reinforcement-learning actor optimizing reward, not expected free energy. This is a deliberate simplification (see `THESIS.md` §5 "Discussion": active inference is listed as future work). The combined PPO + free-energy objective is therefore not a pure-FEP architecture; it is a hybrid that uses the FEP for perception/memory and standard RL for action.

PRISM v2 inherits this framing and extends it to two levels (`PRISM_V2_PROPOSAL.md` §4): the total free-energy functional sums accuracy terms at the V1 and V2 levels, with the cross-level error propagation implementing the inter-level free-energy gradient that Friston (2010) and Bastos et al. (2012) propose.

The bitter-lesson-compliance argument (`THESIS.md` §1.4) is strongest in the FEP framework: free energy depends only on observations, predictions, and posterior — never on task-specific quantities. The same objective is appropriate for any temporal sensory environment, exactly the property the Sutton "bitter lesson" argues for.

## 8. Citations to follow

- `rao_ballard1999_predictive_coding` — the predictive-coding antecedent that Friston's framework generalizes.
- `feldman_friston2010_attention_free_energy` — Friston's specific treatment of attention as precision-weighting; companion paper.
- `bastos2012_canonical_microcircuits` — the canonical-microcircuit operationalization of Friston's framework in cortex.
- `buckley2017_fep_mathematical` — mathematical review aimed at non-Friston readers; essential reading for the formal content.
- `mazzaglia2022_fep_deep_learning` — recent attempt to scale FEP-style architectures using deep learning.
- `parr_friston2019_active_inference_review` — review of active-inference applications; candidate for addition.
