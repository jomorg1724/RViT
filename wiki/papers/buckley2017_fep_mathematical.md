---
id: buckley2017_fep_mathematical
title: "The free energy principle for action and perception: A mathematical review"
authors:
  - "Buckley, Christopher L."
  - "Kim, Chang Sub"
  - "McGregor, Simon"
  - "Seth, Anil K."
year: 2017
venue: "Journal of Mathematical Psychology"
doi: "10.1016/j.jmp.2017.09.004"
arxiv: "1705.09156"
url: "https://arxiv.org/abs/1705.09156"
tags:
  - free-energy-principle
  - predictive-coding
  - review
  - theoretical-essay
concepts:
  - variational-free-energy
  - hierarchical-predictive-coding
  - active-inference
  - precision-weighting
  - inner-inference-loop
  - generative-decoder
  - iterative-variational-encoder-decoder
related:
  - friston2006_free_energy_brain
  - friston2005_cortical_responses
  - friston2010_fep_unified_theory
  - feldman_friston2010_attention_free_energy
  - pezzulo_parr_friston2024_active_inference
  - clark2013_whatever_next
  - aitchison_lengyel2017_pc_bayesian
  - mazzaglia2022_fep_deep_learning
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-18"
---

# The free energy principle for action and perception: A mathematical review

## 1. Abstract

The "free energy principle" (FEP) has been suggested to provide a unified theory of the brain, integrating data and theory relating to action, perception, and learning. The theory and implementation of the FEP combines insights from Helmholtzian "perception as inference," machine-learning theory, and statistical thermodynamics. Here, the authors provide a detailed mathematical evaluation of a suggested biologically plausible implementation of the FEP that has been widely used to develop the theory. The objectives are (i) to describe within a single article the mathematical structure of this implementation of the FEP; (ii) provide a simple but complete agent-based model utilising the FEP; (iii) disclose the assumption structure of this implementation of the FEP to help elucidate its significance for the brain sciences.

## 2. Why this matters for us

Buckley, Kim, McGregor & Seth (2017) is the **mathematical core** of the free-energy principle — a 77-page step-by-step derivation that strips Friston's framework down to the assumptions actually needed to obtain a tractable update rule. Where Friston (2006, 2010) sketches the theory and Pezzulo–Parr–Friston (2024) gives the modern unifying gloss, Buckley et al. spell out, equation by equation, *exactly* how variational free energy collapses to predictive coding under the Laplace approximation plus a hierarchical Gaussian generative model. For the user's program, this paper supplies the falsifiable mathematical structure that any architecture claiming to "implement predictive coding" — including PRISM v1's inner-inference loop, PRISM v2's two-level message passing, and the iterative variational encoder–decoder of `the_user_architectural_program.md` §4 — must satisfy or explicitly deviate from. It is the bridge between the FEP and the iterative-VAE framework: the variational-inference loop is the shared structural primitive.

## 3. Key claims

1. Variational free energy $F$ is defined as the KL divergence between an internal recognition density $q(\vartheta;\mu)$ (R-density) and a generative joint $p(\vartheta,\varphi)$ (G-density); algebraically $F = D_\text{KL}[q\|p(\vartheta|\varphi)] - \ln p(\varphi)$, so $F$ upper-bounds the surprisal $-\ln p(\varphi)$ that organisms must minimise to resist dispersion.
2. Under the **Laplace approximation** (R-density is Gaussian, $q(\vartheta;\mu,\zeta) = \mathcal{N}(\vartheta;\mu,\zeta)$) and the assumption that the energy $E(\vartheta,\varphi) = -\ln p(\vartheta,\varphi)$ is smooth near the mode, the variance can be solved in closed form ($\zeta^* = [d^2 E/d\vartheta^2]_\mu^{-1}$) and $F$ reduces to a function of the *mean* $\mu$ alone — the "Laplace-encoded energy."
3. With a hierarchical Gaussian generative model $\varphi = g(\mu;\theta) + z$, $\mu = \bar\mu + w$, the Laplace-encoded energy becomes a quadratic sum of **precision-weighted prediction errors** $E = \frac{1}{2\sigma_z}\varepsilon_z^2 + \frac{1}{2\sigma_w}\varepsilon_w^2 + \frac{1}{2}\ln(\sigma_z\sigma_w)$ where $\varepsilon_z = \varphi - g(\mu)$ is sensory error and $\varepsilon_w = \mu - \bar\mu$ is the model error — recovering the Rao-Ballard predictive-coding objective from a single variational quantity.
4. **Perception** is gradient descent on the Laplace-encoded energy with respect to brain states: $\dot\mu_\alpha = -\kappa \nabla_{\mu_\alpha} E$. In generalised coordinates of motion, the dynamic version requires the correction $\dot{\tilde\mu} - D\tilde\mu = -\kappa\nabla_{\tilde\mu} E$ so the gradient vanishes when the "path of the mode" equals the "mode of the path."
5. **Action** is the symmetric dual: $\dot a = -\kappa_a (d\varphi/da)(dE/d\varphi)$. The brain does not infer hidden environmental causes via action — it changes sensory input until it matches the brain's predictions. This requires only an inverse model of how sensation depends on action (reflex arcs over proprioception, per Friston 2010).
6. **Learning** extends the same gradient-descent machinery to parameters $\theta$ and hyperparameters (precisions) $\sigma$ of the G-density: a slow gradient flow on $E$ with respect to these terms implements approximate Empirical-Bayes parameter estimation, formally equivalent to a generalised E–M procedure.
7. **Hierarchical extension.** Stacking the generative model so that the prior $\bar\mu^{(i)}$ at one level is supplied by the level above produces *empirical priors* and reduces FEP to canonical predictive coding in cortical hierarchies — but only under explicit Gaussian, sharp-peak, and weak-covariance assumptions.
8. A **complete agent-based simulation** (a 1-D thermostat agent with three-orders-deep generalised coordinates) demonstrates that the same set of ODEs jointly produces perception (state inference from noisy temperature sensing) and action (locomotion to a desired temperature) under one objective, with no separate utility function.

## 4. Methods

The paper is theoretical/expository, presented in nine sections with an explicit assumption ledger.

**§3 — IFE setup.** Define the recognition density $q(\vartheta;\mu)$ and generative density $p(\vartheta,\varphi) = p(\varphi|\vartheta)p(\vartheta)$. Construct informational free energy
$$F = \int d\vartheta\, q(\vartheta) \ln \frac{q(\vartheta)}{p(\vartheta,\varphi)} = D_\text{KL}[q\|p(\vartheta|\varphi)] - \ln p(\varphi).$$
$F$ is computable (depends only on $q$ and $p$) and upper-bounds surprisal via Jensen.

**§4 — Laplace approximation of the R-density.** Set $q(\vartheta;\mu,\zeta) = \mathcal{N}(\mu,\zeta)$. Substitute, Taylor-expand $E(\vartheta,\varphi)$ around $\mu$, integrate. The first-order term vanishes because the integral is the mean; the second-order term gives $\frac{1}{2}[d^2E/d\vartheta^2]_\mu \zeta$. Set $\partial F/\partial\zeta = 0$ to obtain $\zeta^* = [d^2 E/d\vartheta^2]_\mu^{-1}$ and re-substitute. Result: $F$ becomes a function of $\mu$ and sensory input only — no integrals remain.

**§5 — Hierarchical Gaussian G-density.** Specify $\varphi = g(\mu;\theta) + z$ with $z \sim \mathcal{N}(0,\sigma_z)$ and $\mu = \bar\mu + w$ with $w \sim \mathcal{N}(0,\sigma_w)$. Multiplying likelihood and prior and taking $-\ln$ gives the Laplace-encoded energy as a sum of squared, precision-weighted prediction errors (Eq. 25). Extend to multivariate independent case (Eq. 32) and to dynamic generative models in generalised coordinates of motion $\tilde\mu = (\mu, \mu', \mu'', \ldots)$, $D\tilde\mu = (\mu', \mu'', \ldots)$, where $D$ is the shift operator (Eq. 44–47).

**§6 — Perception via recognition dynamics.** Gradient descent $\dot\mu_\alpha = -\kappa\nabla_{\mu_\alpha} E$ in the static case; in generalised coordinates $\dot\mu_{\alpha[n]} - D\mu_{\alpha[n]} = -\kappa\nabla_{\tilde\mu_\alpha} E$ (Eq. 50). Equilibrium is when the path of the mode equals the mode of the path.

**§7 — Active inference and agent-based model.** Action gradient $\dot a = -\kappa_a (d\varphi/da)(dE/d\varphi)$ (Eq. 52). The worked example is a 1-D agent on a frictionless plane sensing temperature $T(\vartheta) = T_0/(\vartheta^2 + 1)$ and its temporal derivative. The agent's generative model encodes a stable attractor at $T_\text{desire}$; minimising $E$ in joint $(\mu,a)$-space drives the agent to the desired temperature via combined state inference and motion. Two coupled ODE systems (Eq. 59 for $\mu$, plus the action equation) yield a complete behavioural agent.

**§8 — Hierarchical learning.** Add a slow gradient-descent on parameters $\theta$ and precisions $\sigma$. The hierarchical G-density supplies empirical priors at each level, recovering Friston-Rao-Ballard predictive coding with precision-weighted error message passing between adjacent layers.

**§9 — Assumption ledger.** The paper closes by listing exactly the assumptions used (Laplace, sharp-peak, weak-covariance, Gaussian innovations, mean-field over levels, separation of timescales between $\mu$, $\theta$, $\sigma$). The authors explicitly do *not* take a position on whether the assumptions are biologically realistic; they only flag what is load-bearing.

## 5. Results

There are no benchmark numbers. The deliverables are:

- A **single self-contained derivation** from the variational objective $F$ to the Rao-Ballard precision-weighted prediction-error equations, with every assumption made explicit.
- A **closed-form Laplace variance** $\zeta^* = [d^2 E/d\vartheta^2]_\mu^{-1}$ that eliminates one degree of freedom and exposes that under the Laplace approximation only first-order Gaussian statistics need be tracked by neural activity.
- An **agent-based simulation** (Section 7) showing that the same ODEs jointly produce perception (the brain state $\mu$ tracks the true temperature) and action (the agent moves to $T_\text{desire}$) with no separate utility function. The simulation is qualitative (no metrics reported); its purpose is existence-proof rather than benchmark.
- An **assumption ledger** identifying exactly which of Friston's claims depend on which approximations — a contribution other surveys (Friston 2010, Pezzulo–Parr–Friston 2024) leave implicit.

## 6. Critique / limitations

The paper is deliberately a mathematical review, not an empirical study, so the relevant limitations are about the *target framework* it formalises and about the formalisation itself.

**Load-bearing approximations.** The reduction of $F$ to a quadratic prediction-error sum depends on (a) Gaussian R-density, (b) sharp peak of $q$ around $\mu$ so the Taylor expansion of $E$ truncates at second order, (c) Gaussian innovations $z, w$, and (d) weak covariance between environmental variables. Real cortical statistics (heavy-tailed firing, discrete spikes, strong correlations between cells) violate all four. The paper notes these but does not attempt empirical validation.

**The generalised-coordinates apparatus.** The distinction between $\dot{\tilde\mu}$ (kinematic time derivative) and $D\tilde\mu$ (the encoded trajectory) is mathematically necessary for dynamic models but is not biologically motivated; whether real neurons compute in generalised coordinates is unestablished.

**Inverse model for action.** Active inference reduces motor control to gradient descent on $E$ via $d\varphi/da$, but the inverse model $\varphi(a)$ has to come from somewhere. Friston's appeal to proprioceptive reflex arcs is one option; the paper does not commit to a substrate. This is the same gap noted in `friston2006_free_energy_brain` §6.

**Falsifiability.** The framework is highly flexible — many cognitive phenomena can be re-described as "gradient descent on some $E$." The 2017 paper is *more* falsifiable than the 2010 review because it pins down the assumptions, but the assumption set is rarely tested in any one experiment.

**Distance from ML practice.** The Laplace-encoded energy is structurally identical to a Gaussian negative-log-likelihood with priors; modern ML treats the same object as a VAE ELBO (Kingma & Welling 2014) without the FEP packaging. The 2017 paper's contribution is the *biological interpretation*, not new variational mathematics. The flip side is that ML benchmarks of pure-FEP architectures are sparse.

**No empirical engagement.** The agent-based example is illustrative. There is no comparison to neural data or to alternative formalisations of predictive coding (e.g., Spratling's biased-competition account, Aitchison & Lengyel's PC-without-Bayes critique).

## 7. Connection to our work

This paper is the **mathematical scaffolding** that everything FEP-flavoured in the user's program rests on. Friston (2006, 2010) supplies the conceptual frame; Pezzulo–Parr–Friston (2024) supplies the modern unification; **Buckley et al. (2017) is the reference any reviewer can audit when checking what PRISM or the iterative-VAE actually instantiates.**

- **PRISM v1's inner-inference loop is the discrete-time analogue of Eq. 48.** `THESIS.md` §2.8's iterative refinement of the memory state $M_t$ by descending on prediction error is exactly $\dot\mu = -\kappa\nabla_\mu E$ in the Buckley et al. setup, with $\mu \leftrightarrow M_t$ and $E$ the Laplace-encoded energy under PRISM's Gaussian-likelihood reconstruction loss. PRISM does not use generalised coordinates of motion, which means PRISM's implicit generative model is static rather than dynamic; this is a *deliberate* simplification PRISM v2 partially relaxes via its slow/fast memory pair.

- **PRISM's reconstruction + feature-prediction losses are the multivariate Laplace-encoded energy.** `THESIS.md` §2.11's pixel and feature MSE losses are the two precision-weighted prediction-error terms of Eq. 32 ($\varepsilon_z$ from sensory mismatch, $\varepsilon_w$ from prior/feature mismatch). The fact that PRISM weights these by fixed scalars rather than learned precisions $\sigma^{-1}$ is the explicit deviation from full FEP — making PRISM a *fixed-precision* FEP agent. Restoring learned precisions would be a one-line change with direct theoretical justification from §5 of this paper.

- **PRISM v2's two-level structure is the hierarchical generative model of §8.** `PRISM_V2_PROPOSAL.md` §4's V1-level and V2-level errors map directly onto adjacent levels of the Buckley et al. hierarchy: the cross-level term in PRISM v2 corresponds to $\partial g^{(i)}/\partial\mu^{(i)}$ propagating prediction errors between levels. Buckley et al. §8 gives the message-passing equations PRISM v2 would have to satisfy to count as a literal hierarchical-FEP implementation.

- **The iterative variational encoder–decoder maps onto §4 + §6.** `the_user_architectural_program.md` §4's $n_{FR}$-step forward reasoning is gradient descent on $E$ over the guide $\tilde H_0$ (the Laplace mean) for a fixed image — Buckley et al. Eq. 48 applied repeatedly. The $n_{BR}$-step backward reasoning then re-samples the recognition density and runs the decoder, exactly the recognition-dynamics half of the active-inference loop. The user's KL-on-$\tilde H_0$ regulariser **is** the variational free-energy bound this paper derives. This is the cleanest existing match between the user's program and the FEP literature.

- **Precision-as-attention.** Buckley et al. derive precision-weighted prediction error from first principles (Eq. 32) but treat the precisions $\sigma$ as separately optimised slow parameters. The user's competition-emergent-predictive-coding thesis (`the_user_architectural_program.md` §5) can be cast as a precision-control story: hubs win the attention competition by getting their precision weights right on the relevant feedback channels. This connects the user's framework to Feldman & Friston (2010) via the precise mechanism Buckley et al. expose.

- **Falsifiable predictions.** Buckley et al. provide the criterion for what PRISM/recurrent-ViT must *compute* to count as predictive coding: at convergence, the activity should satisfy $\nabla_\mu E = 0$ where $E$ is the Laplace-encoded energy under PRISM's generative assumptions. If a probe of PRISM's converged state shows residual gradient (i.e., the inner loop doesn't actually reach a fixed point of the Laplace energy), that is direct evidence PRISM is *not* implementing FEP-style inference, regardless of behavioural success. This is the kind of architectural audit the user's program needs.

- **Bridge to iterative-VAE.** The shared structural primitive between FEP and the iterative-VAE is **iterative gradient descent on a variational free-energy objective**. Buckley et al. make this primitive precise; the user's $n_{FR} \to n_{BR}$ schedule operationalises it. This paper is therefore the load-bearing theoretical bridge between Friston's program and the user's encoder–decoder construction (Encoder-Decoder Architecture note, §1, point 4).

The relationship to the user's competition-emergent-predictive-coding thesis is best framed as follows: Buckley et al. derive PC for a *single* agent's variational inference. The user's thesis nests this — each coalition runs its own FEP loop where the "environment" includes other coalitions. The mathematics of Buckley et al. is unchanged inside each coalition; the novelty is in the coupling between coalitions. Citing this paper provides the technical baseline against which the inter-coalition extension must be specified.

## 8. Citations to follow

- `friston2008_variational_filtering` — generalised coordinates of motion, the substrate for Buckley et al. §5.2; not yet in seed but cited heavily here.
- `dauwels2007_variational_message_passing` — alternative formal derivation of the message-passing implementation; useful for distinguishing Laplace-FEP from ensemble-learning FEP.
- `bogacz2017_tutorial_predictive_coding` — companion tutorial in the same JMP special issue; explicitly designed to be read alongside this paper. Would be a natural near-twin entry.
- `kingma_welling2014_vae` — the ML twin of Eq. 14–16; the same Laplace-style variational bound is the VAE ELBO. Critical for the iterative-VAE bridge.
- `parr_friston2019_active_inference_review` — the active-inference review that builds on §7. Not yet in seed.
- `da_costa2020_active_inference_discrete` — discrete-state FEP for environments where Gaussian/Laplace assumptions fail. Not in seed.
- `tschantz2020_active_inference_continuous` — continuous-state active inference benchmarked on RL tasks; tests whether Buckley-style FEP scales. Not in seed.
- `mazzaglia2022_fep_deep_learning` — FEP-for-DL bridge. Already in seed.
