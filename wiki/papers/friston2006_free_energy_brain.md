---
id: friston2006_free_energy_brain
title: "A free energy principle for the brain"
authors:
  - "Friston, Karl"
  - "Kilner, James"
  - "Harrison, Lee"
year: 2006
venue: "Journal of Physiology - Paris"
doi: "10.1016/j.jphysparis.2006.10.001"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/17097864/"
tags:
  - free-energy-principle
  - predictive-coding
  - theoretical-essay
concepts:
  - variational-free-energy
  - hierarchical-predictive-coding
  - active-inference
  - generative-decoder
  - precision-weighting
  - rao-ballard-coding
related:
  - friston2010_fep_unified_theory
  - friston2005_cortical_responses
  - rao_ballard1999_predictive_coding
  - feldman_friston2010_attention_free_energy
  - pezzulo_parr_friston2024_active_inference
  - clark2013_whatever_next
  - buckley2017_fep_mathematical
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_91
status: full
depth: full
last_updated: "2026-05-16"
---

# A free energy principle for the brain

## 1. Abstract

By formulating Helmholtz's ideas about perception in terms of modern-day theories, one arrives at a model of perceptual inference and learning that can explain a remarkable range of neurobiological facts. Using constructs from statistical physics, the problems of inferring the causes of sensory input and learning the causal structure of their generation can be resolved using exactly the same principles, and inference and learning can proceed in a biologically plausible fashion. The ensuing scheme rests on Empirical Bayes and hierarchical models of how sensory input is caused; hierarchical models enable the brain to construct prior expectations in a dynamic and context-sensitive fashion. The paper shows that these perceptual processes are just one aspect of emergent behaviours of systems that conform to a free energy principle. The free energy considered here measures the difference between the probability distribution of environmental quantities that act on the system and an arbitrary distribution encoded by its configuration. The system can minimise free energy by changing its configuration to either affect the way it samples the environment or change the distribution it encodes — changes that correspond to action and perception respectively, and lead to the adaptive exchange with the environment that is characteristic of biological systems. The treatment assumes the system's state and structure encode an implicit, probabilistic model of the environment; minimisation of free energy then explains both cortical dynamics and structure.

## 2. Why this matters for us

This is the *founding* statement of the free-energy principle (FEP) — the explicit derivation that the 2010 *Nature Reviews Neuroscience* synthesis (`friston2010_fep_unified_theory`) presents as a settled framework. Everything PRISM v1 and v2 inherit from Friston — the variational-free-energy auxiliary loss (`THESIS.md` §2.11), the inner-inference loop as iterative free-energy minimisation (`THESIS.md` §2.8), the precision-weighting reading of saliency (`THESIS.md` §2.6), and the active-inference framing held in reserve for future PRISM — is first set out in this 2006 paper, in the company of explicit hierarchical generative models, Empirical-Bayes learning, and a derivation that bottoms out in Rao-Ballard predictive coding. Reading the 2006 paper alongside Friston 2010 separates *theorem* (what the FEP actually proves) from *interpretation* (the unifying-brain-theory gloss). PRISM cites Friston 2010 in the manuscript; the architectural debt is to *this* paper.

## 3. Key claims

1. Any self-organising system that resists thermodynamic dispersion to a non-equilibrium steady state must minimise the entropy of its sensory states, which is bounded above by *variational free energy* — a quantity the system can compute from internal states alone, without access to the true posterior.
2. Variational free energy decomposes as $F = -\langle \log p(o, \vartheta) \rangle_q + \langle \log q(\vartheta) \rangle_q$, equal to the KL divergence from the approximate posterior $q(\vartheta)$ to the true posterior $p(\vartheta|o)$ plus the negative log-evidence (surprise) $-\log p(o)$. Because the KL is non-negative, $F$ is an upper bound on surprise.
3. The brain encodes $q(\vartheta)$ implicitly in its physical configuration (synaptic weights, neural activity); minimising $F$ with respect to those degrees of freedom approximates Bayesian inference under a hierarchical generative model of sensory causes.
4. Two complementary moves minimise $F$: **perception** (updating internal states / parameters of $q$ to better match the posterior over hidden causes) and **action** (changing the world so sensory samples are better explained by the current model). The latter is the seed of *active inference*.
5. Under Empirical-Bayes hierarchical models with Gaussian assumptions, the free-energy gradient reduces to precision-weighted prediction errors propagated between adjacent levels — exactly Rao & Ballard's (1999) hierarchical predictive-coding scheme, now derived from a single variational objective rather than postulated.
6. Hierarchical priors are not fixed: empirical priors at each level are supplied by the level above, so context-sensitivity and learning of slow dynamics fall out of the same minimisation. This is the explicit form of "dynamic priors" that the 2010 paper takes for granted.
7. The same free-energy gradient drives both fast inference (state estimation) and slow learning (parameter estimation) by separating expectation steps over hidden states from maximisation-like steps over parameters — a generalised EM in continuous time.
8. Attention and uncertainty estimation enter via precision (inverse variance) parameters of the hierarchical Gaussian likelihoods; estimating precisions amounts to learning *how much to weight each prediction-error channel*, which is the FEP's account of attentional gain.

## 4. Methods

The paper is theoretical. The central mathematical move is to take a system with internal states $\mu$ and a recognition density $q(\vartheta; \mu)$ over hidden environmental causes $\vartheta$, and write the variational free energy

$$
F(\mu, o) = -\langle \log p(o, \vartheta) \rangle_{q(\vartheta;\mu)} - H[q(\vartheta;\mu)] = D_\text{KL}[q(\vartheta;\mu) \,\|\, p(\vartheta|o)] - \log p(o).
$$

Three structural assumptions then collapse $F$ to something the brain could plausibly compute:

- **Laplace approximation.** $q$ is Gaussian with mean $\mu_\vartheta$ and covariance $\Sigma_\vartheta$, parameterised by the system's physical state. $F$ becomes a quadratic in $\mu_\vartheta$ plus log-determinant terms.
- **Generative model in hierarchical Gaussian form.** Sensory input $o$ is generated by a cascade $\vartheta^{(i)} = g^{(i)}(\vartheta^{(i+1)}) + z^{(i)}$ with Gaussian innovations $z^{(i)} \sim \mathcal{N}(0, \Sigma^{(i)})$ at each level. The joint $\log p$ then decomposes additively over levels.
- **Mean-field over levels.** $q(\vartheta) = \prod_i q^{(i)}(\vartheta^{(i)})$, so the gradient at level $i$ depends only on neighbouring levels.

Under these, the free-energy gradient with respect to $\mu^{(i)}$ becomes a sum of two precision-weighted residuals — the prediction error *received* from level $i-1$ and the prediction error *sent* to level $i+1$:

$$
\dot \mu^{(i)} \propto -\frac{\partial F}{\partial \mu^{(i)}} = \Sigma^{(i),-1}\,\xi^{(i)} - \frac{\partial g^{(i)}}{\partial \mu^{(i)}}^\top \Sigma^{(i+1),-1}\,\xi^{(i+1)}
$$

with $\xi^{(i)} = \vartheta^{(i-1)} - g^{(i)}(\mu^{(i)})$. This is the Rao-Ballard message-passing scheme, now with the precisions $\Sigma^{(i),-1}$ identified as separate quantities the system also has to estimate (the seed of precision-as-attention).

Action enters as a second set of degrees of freedom: the system can change $o$ via motor effectors. Free-energy minimisation with respect to action gives policies that sample the world to confirm current predictions, anticipating the later "expected free energy" formulation.

The paper sketches an in-silico simulation of a single hierarchical Gaussian model exhibiting these dynamics, but the simulation is illustrative rather than benchmarked.

## 5. Results

There are no benchmark numbers. The paper's deliverables are:

- A formal derivation from variational principles alone of hierarchical predictive-coding message passing — the same scheme Rao & Ballard 1999 motivated phenomenologically.
- An identification of cortical hierarchy + descending predictions + ascending precision-weighted errors with the layered structure of $F$.
- An explicit reading of *precision* parameters as the substrate of attention and uncertainty estimation, anticipating Feldman & Friston (2010).
- The first published statement that perception and action are dual moves under one variational objective — the conceptual ancestor of active inference.

The illustrative simulation reproduces the qualitative dynamics: free energy decreases monotonically; posterior estimates track hidden causes; precision estimates rise on reliable channels.

## 6. Critique / limitations

The same flexibility-vs-falsifiability criticism that applies to Friston 2010 (van Es 2021; Colombo & Wright 2021) applies *a fortiori* here: the 2006 paper is where the framework is most permissive about what counts as a generative model and a prior, and so what counts as a successful FEP-style explanation.

The biological reduction relies on Gaussianity and the Laplace approximation. Real cortical statistics — heavy-tailed firing, non-Gaussian noise, discrete spiking — are not addressed. Later mathematical reviews (Buckley et al. 2017) make these assumptions explicit and show how much of the FEP's tractable structure depends on them.

The precision/attention identification is suggestive but underdetermined: many neuromodulatory and circuit-level mechanisms could implement gain control, and the paper does not commit to a specific cortical substrate. Bastos et al. 2012 supplies that commitment six years later.

The active-inference component is sketched, not developed. Selecting actions to minimise expected free energy is computationally intractable in any environment with non-trivial dynamics, and the 2006 paper does not yet engage with that intractability — later work (Friston et al. 2015 onwards) introduces the policy-evaluation machinery.

From an ML perspective, the variational decomposition is the same machinery later canonised in variational autoencoders (Kingma & Welling 2014); the 2006 contribution is biological interpretation, not new variational mathematics. Architectures built directly on the FEP (e.g., the "predictive coding networks" line) have not consistently outperformed standard deep learning on benchmarks.

## 7. Connection to our work

This is the founding FEP paper and the direct theoretical predecessor of Friston 2010 (`friston2010_fep_unified_theory`), to which PRISM's THESIS.md attaches its single-objective justification. PRISM v1 and v2 inherit, *via* the 2010 review, the variational-free-energy machinery first set down here:

- **The PRISM loss as FEP accuracy.** PRISM v1's pixel and feature prediction-error losses (`THESIS.md` §2.11) are the accuracy term of the variational free energy that this paper derives — under exactly the Gaussian-likelihood, Laplace-posterior assumptions made in §4. The decision to use a single squared-error objective for "any temporal sensory environment" is the 2006 paper's claim that one variational quantity suffices.
- **The inner-inference loop as gradient descent on $F$.** PRISM v1's inner loop over the memory state $M_t$ (`THESIS.md` §2.8) directly mirrors the $\dot \mu^{(i)} \propto -\partial F / \partial \mu^{(i)}$ dynamics in §4 of this paper: iterative refinement of a Laplace-posterior mean by gradient descent on the variational free energy.
- **Hierarchical message-passing as PRISM v2's two-level structure.** PRISM v2's V1-level and V2-level error propagation (`PRISM_V2_PROPOSAL.md` §4) is the two-level instance of the hierarchical message-passing scheme this paper derives. The cross-level error term in PRISM v2 corresponds to the $\partial g^{(i)} / \partial \mu^{(i)}$ projection that links adjacent levels of $F$.
- **Precision-weighted saliency.** PRISM's reading of the per-location prediction-error magnitude as a precision-weighted attention signal (`THESIS.md` §2.6) comes from §4 of this paper, where attention is identified with the $\Sigma^{(i),-1}$ precisions — later operationalised in Feldman & Friston (2010).
- **Active inference as deferred future work.** PRISM does *not* implement the second variational move (action selection by free-energy minimisation); the policy is learned by PPO, as in `THESIS.md` §5. The 2006 paper is the canonical reference for what PRISM would have to add to become a pure active-inference agent — a path the user's architectural program (`threads/the_user_architectural_program.md` §4) leaves open via the iterative variational encoder–decoder.

Relative to Friston 2010, this paper is the *technical* source: 2010 is the synthesis used in citations, but 2006 contains the derivation. For audits and reviewer responses about what the FEP actually proves versus what it claims, this is the reference to cite.

The user's reformulation of predictive coding as competition-emergent (`threads/the_user_architectural_program.md` §5) is best read *against* this paper: 2006 grounds predictive coding in a single agent's variational inference about sensory causes, while the user's account grounds it in *inter-coalition* competition for representational bandwidth. The two are not contradictory — competition-emergent PC can be cast as each coalition running its own FEP loop where the "environment" includes the other coalitions — but the 2006 derivation is the framework against which the user's reframing must explicitly differentiate itself.

## 8. Citations to follow

- `friston2005_cortical_responses` — the immediate predecessor on Empirical-Bayes hierarchical cortical responses; supplies the message-passing machinery this paper generalises.
- `rao_ballard1999_predictive_coding` — already in the database as a related entry; this paper's derivation reduces to Rao-Ballard under Gaussian assumptions.
- `feldman_friston2010_attention_free_energy` — operationalises this paper's precision-as-attention identification.
- `buckley2017_fep_mathematical` — the rigorous mathematical review that makes explicit which assumptions in §4 are load-bearing.
- `pezzulo_parr_friston2024_active_inference` — modern textbook treatment of active inference; the canonical reference for the action half of the 2006 derivation.
- `clark2013_whatever_next` — philosophical synthesis arguing predictive processing is the central organising idea of cognition; cites this paper as foundational.
