---
id: mazzaglia2022_fep_deep_learning
title: "The free energy principle for perception and action: a deep learning perspective"
authors:
  - "Mazzaglia, Pietro"
  - "Verbelen, Tim"
  - "Çatal, Ozan"
  - "Dhoedt, Bart"
year: 2022
venue: "Entropy"
doi: "10.3390/e24020301"
arxiv: ""
url: "https://doi.org/10.3390/e24020301"
tags:
  - free-energy-principle
  - deep-learning
  - world-models
  - review
concepts:
  - variational-free-energy
  - active-inference
  - generative-decoder
  - inner-inference-loop
  - hierarchical-predictive-coding
  - precision-weighting
  - curiosity-driven-learning
related:
  - pezzulo_parr_friston2024_active_inference
  - friston2010_fep_unified_theory
  - hafner2020_dreamer
  - ha_schmidhuber2018_world_models
  - schmidhuber2015_learn_to_think
  - bardes2023_vjepa
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_95
status: full
depth: full
last_updated: "2026-05-15"
---

# The free energy principle for perception and action: a deep learning perspective

## 1. Abstract

The free energy principle, and its corollary active inference, constitute a bio-inspired theory that assumes biological agents act to remain in a restricted set of preferred states of the world, i.e., they minimize their free energy. Under this principle, biological agents learn a generative model of the world and plan actions in the future that will maintain the agent in a homeostatic state that satisfies its preferences. This framework lends itself to being realized in silico, as it comprehends important aspects that make it computationally affordable, such as variational inference and amortized planning. In this work, the authors investigate the tool of deep learning to design and realize artificial agents based on active inference, presenting a deep-learning–oriented presentation of the free energy principle, surveying works that are relevant in both machine learning and active inference areas, and discussing the design choices that are involved in the implementation process. The manuscript probes newer perspectives for the active inference framework, grounding its theoretical aspects into more pragmatic affairs, and offers a practical guide to active inference newcomers and a starting point for deep learning practitioners who would like to investigate implementations of the free energy principle.

## 2. Why this matters for us

Mazzaglia, Verbelen, Çatal & Dhoedt 2022 is the *deep-learning–facing* companion to the Friston-tradition free-energy literature. Where Pezzulo-Parr-Friston 2024 ([pezzulo_parr_friston2024_active_inference](pezzulo_parr_friston2024_active_inference.md)) reads the framework from the neuroscience side, this review reads it from the ML side — concretely identifying which variational-autoencoder, world-model, and model-based-RL ideas already implement pieces of active inference, and which design choices a practitioner must make to actually build one. For the user's program, PRISM v1's inner variational-inference loop ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.8, §2.11) and the iterative variational encoder-decoder ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §4) are precisely the kinds of architectures this paper surveys, situating them in a deep-active-inference lineage that is publishable as ML rather than as theoretical neuroscience.

## 3. Key claims

1. **The free energy principle has a clean deep-learning translation.** Variational free energy can be implemented with amortized encoders (recognition networks) and decoders (generative networks), with standard reparameterization, exactly as in a VAE — making active inference computationally tractable and trainable by gradient descent.
2. **Active inference unifies perception, action, and learning.** Perception is variational inference over latent states; learning is variational inference over model parameters; action is the minimization of *expected* free energy over future trajectories. All three reduce to the same gradient signal under appropriate generative models.
3. **Expected free energy decomposes into "instrumental" and "epistemic" terms.** The action-selection objective naturally splits into a reward-like term (preferences over outcomes) and an information-gain term (uncertainty reduction). This gives a principled account of curiosity that does not require an extrinsic exploration bonus.
4. **Deep active-inference agents are world-models with priors over preferences.** Existing world-model architectures (Ha-Schmidhuber, PlaNet, Dreamer) can be reinterpreted as active-inference agents once a prior over preferred observations is added; their planning step becomes expected-free-energy minimization.
5. **Hierarchical generative models with temporal depth are the natural extension.** Multi-level latent models with slow-fast timescales generalize the single-level VAE-style active-inference agent into a temporally-deep predictive system matching the cortex-like commitments of the FEP tradition.
6. **Design choices matter empirically.** The choice of amortized vs. iterative inference, of policy parameterization, of prior over preferences, and of approximate-posterior family are not merely cosmetic — they determine which behaviors emerge and which benchmarks the agent can match. The paper surveys these systematically.
7. **Open problems are concrete.** Scaling deep active inference to high-dimensional pixel observations, matching Dreamer-class performance on Atari/Control, and learning hierarchical preferences are open and tractable.

## 4. Methods

A *survey* paper with a tutorial spine. The paper has three layers.

The *theoretical* layer derives variational free energy for a generative model $p_\theta(o_{1:T}, s_{1:T}, a_{1:T})$ over observations $o$, latent states $s$, and actions $a$. With an amortized recognition network $q_\phi(s_t \mid o_{\le t}, a_{<t})$, the per-step free energy is
$$
\mathcal{F}_t = \mathbb{E}_{q_\phi}\big[\log q_\phi(s_t) - \log p_\theta(o_t, s_t \mid s_{t-1}, a_{t-1})\big],
$$
which is the negative ELBO of a sequential VAE plus an action-conditioned transition. *Expected* free energy for a future policy $\pi$ is
$$
\mathcal{G}(\pi) = \mathbb{E}_{q(o_\tau, s_\tau \mid \pi)}\big[\log q(s_\tau \mid \pi) - \log p(o_\tau, s_\tau)\big]
$$
and decomposes into an *epistemic* term (mutual information between latent and observation under the policy) and an *instrumental* term (KL between predicted observations and preferred ones).

The *architectural* layer surveys how published deep-learning systems realize these equations. The authors map: VAE → static-observation perception under FEP; sequential VAEs / state-space VAEs → temporally-extended perception; world models (Ha-Schmidhuber, PlaNet, Dreamer) → action-conditioned generative models; soft actor-critic and policy-gradient methods → tractable amortizations of expected-free-energy minimization; intrinsic-motivation / curiosity methods (RND, Disagreement, Plan2Explore) → epistemic-term implementations.

The *design-choice* layer discusses, for a would-be implementer, the consequences of (i) the choice of latent-space dimensionality and structure, (ii) amortized vs. iterative posterior inference, (iii) the form of the prior over preferred observations (Gaussian targets, logistic-classifier targets, demonstration-distillation), (iv) the policy parameterization (discrete planner vs. amortized actor), and (v) the use of hierarchical / temporally-deep generative models.

The paper does not present new experiments. All quantitative claims are second-hand from the surveyed literature.

## 5. Results

The principal substantive points consolidated by the survey:

- **Equivalence map.** Standard ML systems are placed in correspondence with active-inference components: VAEs ↔ perception; sequential VAEs / RSSMs ↔ temporally-extended perception; Dreamer-style policies ↔ amortized expected-free-energy minimizers; RND-style intrinsic motivation ↔ epistemic-term proxies.
- **Curiosity from epistemic value.** Agents trained to minimize expected free energy spontaneously perform information-seeking behavior in toy environments; explicit "curiosity bonuses" are unnecessary because the epistemic term supplies them. Empirical demonstrations from Friston-tradition discrete agents and from continuous-state deep agents (e.g., Tschantz et al.) are consolidated.
- **Sample-efficiency improvements.** Deep active-inference agents are reported to be more sample-efficient than vanilla model-free RL on small benchmarks (mountain-car, cartpole, simple navigation), at the cost of additional model-training complexity.
- **Scalability gap.** No surveyed deep-active-inference agent matches Dreamer or MuZero on Atari at the time of writing. The framework is competitive on small benchmarks but the scaling story is open.
- **Hierarchical pilots.** Early hierarchical / temporally-deep active-inference deep agents (Pezzulo & Rigoli; Friston et al. discrete hierarchies; Çatal et al. continuous) show the framework can be extended in depth, but mature ML-scale demonstrations are not yet available.

## 6. Critique / limitations

The paper is a *survey*, not an empirical contribution. Readers seeking benchmark numbers must follow the citations rather than the paper itself.

The framework's *generality is a double-edged sword*. Mazzaglia et al. are admirably explicit that many ML systems can be reinterpreted as active inference; critics argue that this reinterpretation is sometimes *cosmetic* — adding the FEP vocabulary on top of a standard VAE or Dreamer agent does not necessarily yield new architectural insight. The paper occasionally elides this distinction.

The *expected-free-energy* objective has several non-equivalent formulations in the literature (Friston et al. 2015 vs. da Costa et al. 2020 vs. amortized variants). The paper surveys these but does not strongly adjudicate; a reader implementing the framework must still make a choice that the paper itself does not pin down.

The *scaling gap* relative to Dreamer / MuZero is acknowledged but underexplored. Whether the gap is intrinsic (the framework is fundamentally limited) or contingent (the right scaling hasn't been tried) is unsettled.

The paper is *Ghent-school-aligned*. Alternative deep-FEP traditions (e.g., the Friston-Buckley-Tschantz continuous-state line; the discrete-state hierarchical line) are referenced but the synthesis is from the authors' own implementation experience, which biases the design-choice discussion toward continuous-state amortized agents.

The *biological plausibility* of the surveyed architectures is largely set aside. Mazzaglia et al. focus on engineering, not on neural-implementation faithfulness — which is appropriate for the ML audience but means the paper does not adjudicate the cortical-microcircuit claims of the Friston-Bastos tradition.

## 7. Connection to our work

This paper is the natural ML-side citation for several of the user's commitments:

**Inner-loop variational inference as PRISM's auxiliary objective.** PRISM v1's inner-loop variational-free-energy loss ([Prism/docs/THESIS.md](Prism/docs/THESIS.md) §2.8, §2.11) is exactly the kind of amortized-VAE active-inference loss this paper surveys. Manuscripts framing PRISM as deep active inference should cite Mazzaglia et al. alongside Pezzulo-Parr-Friston — this paper supplies the *ML* lineage; Pezzulo-Parr-Friston supplies the *neuroscience* lineage.

**Iterative encoder-decoder as deep active inference.** The user's iterative variational encoder-decoder ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §4) is a temporally-extended VAE with $n_{FR}$ recognition steps and $n_{BR}$ generative steps. This is structurally a sequential active-inference agent without an action variable; adding an action conditioning to the decoder would convert it directly into a world-model-style deep-FEP agent of the kind Mazzaglia et al. survey. The user's program therefore has a natural extension to a planning agent that this paper supplies the template for.

**Multi-hub multi-objective system as decomposed expected free energy.** The user's multi-hub program ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) trains separate hubs on perception (MSI), action (RL), and reconstruction (VAE) objectives. Mazzaglia et al.'s decomposition of expected free energy into instrumental and epistemic terms gives a principled reading of this multi-hub structure: the MSI hub minimizes a perception-side variational free energy, the RL hub minimizes an instrumental term, and the VAE hub minimizes the reconstruction term. The user's multi-hub competition is then an implementation of a decomposed FEP objective.

**Hierarchical temporally-deep models.** The user's hierarchical multi-compartmental memory ([multi_compartmental_memory](research_db/concepts/multi_compartmental_memory.md)) with slow-fast timescales matches the hierarchical extensions of active inference that Mazzaglia et al. flag as the natural next step. Their survey indicates this is an *open* engineering direction in deep FEP, supporting the user's architectural bet rather than reporting a settled solution.

**Curiosity from epistemic value.** If the user adds intrinsic-motivation training to the MSI hub (as suggested in [the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §5), this paper supplies the deep-active-inference justification: the epistemic term of expected free energy *is* a curiosity signal, derivable from a single variational principle rather than added as an ad-hoc bonus. This is the natural ML reference, alongside Schmidhuber 2015 ([schmidhuber2015_learn_to_think](schmidhuber2015_learn_to_think.md)).

**Connection to the recurrent ViT.** The recurrent ViT paper (2502.10955) cites this work as ref [95] in its discussion of predictive-coding-adjacent architectures. The Mazzaglia et al. survey is the contemporary ML-tradition reference for the FEP framework the recurrent ViT's memory mechanism implicitly approximates.

**Contrast with JEPA / V-JEPA.** Bardes et al.'s V-JEPA ([bardes2023_vjepa](bardes2023_vjepa.md)) explicitly avoids pixel-level reconstruction, in contrast to the VAE-style decoder of deep active inference. Mazzaglia et al.'s survey gives the FEP side of this trade-off, against which a manuscript can position the user's iterative-VAE program as a *reconstructive* deep-FEP system rather than a JEPA-style energy-based one.

## 8. Citations to follow

- `friston2010_fep_unified_theory` — foundational FEP paper. In seed.
- `ha_schmidhuber2018_world_models` — world models with RNN dynamics. In seed.
- `hafner2020_dreamer` — Dreamer model-based RL. In seed.
- `schmidhuber2015_learn_to_think` — controller / model coupled RNNs. In seed.
- `tschantz2020_active_inference_continuous` — continuous-state deep active inference. Not in seed.
- `da_costa2020_active_inference_discrete` — discrete-state active inference. Not in seed.
- `friston2015_active_inference_epistemic` — Friston's expected-free-energy decomposition. Not in seed.
- `catal2020_active_inference_navigation` — Ghent-school continuous deep active inference. Not in seed.
- `sajid2021_active_inference_demystified` — pedagogical companion to this survey. Not in seed.
- `millidge2021_whence_efe` — analysis of expected-free-energy formulations. Not in seed.
