---
id: aitchison_lengyel2017_pc_bayesian
title: "With or without you: predictive coding and Bayesian inference in the brain"
authors:
  - "Aitchison, Laurence"
  - "Lengyel, Máté"
year: 2017
venue: "Current Opinion in Neurobiology"
doi: "10.1016/j.conb.2017.08.010"
arxiv: ""
url: "https://doi.org/10.1016/j.conb.2017.08.010"
tags:
  - predictive-coding
  - theoretical-essay
  - review
concepts:
  - hierarchical-predictive-coding
  - variational-free-energy
  - prediction-error-map
  - precision-weighting
related:
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - clark2013_whatever_next
  - keller_mrsic_flogel2018_pc_review
  - spratling2008_pc_biased_competition
  - srinivasan1982_predictive_coding_retina
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# With or without you: predictive coding and Bayesian inference in the brain

## 1. Abstract

Two theoretical ideas have emerged recently with the ambition to provide a unifying functional explanation of neural population coding and dynamics: *predictive coding* and *Bayesian inference*. Aitchison & Lengyel describe the two theories and their combination into a single framework: **Bayesian predictive coding**. They clarify how the two theories can be distinguished, despite sharing core computational concepts and addressing an overlapping set of empirical phenomena. They argue that predictive coding is an *algorithmic/representational motif* that can serve several different computational goals — of which Bayesian inference is but one. Conversely, while Bayesian inference can utilize predictive coding, it can also be realized by a variety of other representations. The paper critically evaluates the experimental evidence for Bayesian predictive coding and discusses how to test it more directly.

## 2. Why this matters for us

Aitchison & Lengyel 2017 is the *clarifying* paper that distinguishes predictive coding (an algorithm) from Bayesian inference (a computational goal). The distinction matters because the user's program ([hierarchical_predictive_coding](research_db/concepts/hierarchical_predictive_coding.md)) explicitly adopts both — predictive coding as the architectural form, Bayesian inference as the normative justification. This paper provides the precise vocabulary for keeping the two separate. Specifically, it clarifies that the architectural commitments of PRISM (hierarchical, descending predictions, ascending errors) can be motivated by different computational goals than just Bayesian inference — e.g., efficient coding (Srinivasan 1982), strategic competition (the user's thesis), and others.

## 3. Key claims

1. **Predictive coding is an algorithm, not a goal.** It is a *representational motif*: a specific scheme for how information is computed and transmitted (descending predictions, ascending errors). It says nothing intrinsic about *why* the brain uses this scheme.
2. **Bayesian inference is a computational goal, not an algorithm.** It is a normative claim about *what the brain should compute* (posterior distributions over latent causes). It can be realized by many different algorithmic implementations.
3. **The two are distinct but combinable.** Bayesian predictive coding is the *combination*: predictive coding as the algorithmic implementation of Bayesian inference. But the algorithm and the goal can be combined differently, or kept separate.
4. **Predictive coding can serve non-Bayesian goals.** Examples include: redundancy reduction (Srinivasan 1982, where the goal is *efficient coding* in the information-theoretic sense), maximum-likelihood estimation, and even simple decorrelation. The architecture is the same; the objective differs.
5. **Bayesian inference can be realized without predictive coding.** Sampling-based representations (e.g., probabilistic population codes via Poisson firing) and parallel approximate inference (e.g., distributed parameter representations) are alternatives that don't use the prediction-error / generative-decoder architecture.
6. **The empirical signatures don't uniquely distinguish.** Mismatch responses, expectation suppression, and laminar frequency patterns are consistent with many implementations of "Bayesian predictive coding," not just the Rao-Ballard / Bastos canonical microcircuit.
7. **Specific predictions for direct tests.** The paper proposes empirical signatures that would distinguish predictive-coding from sampling-based Bayesian implementations, e.g., differences in the trial-by-trial dynamics of neural responses to repeated stimuli.

## 4. Methods

A theoretical / review paper. The authors compare the formal structure of predictive coding (Rao-Ballard 1999, Friston 2010) with the formal structure of Bayesian inference (Knill & Pouget 2004, Pouget et al. 2013, Ma et al. 2006). They identify the points of overlap (both can produce the same empirical signatures) and the points of divergence (different algorithmic implementations, different empirical signatures in fine-grained tests).

The synthesis emphasizes that:
- **Bayesian predictive coding** is the combination most aligned with the Friston tradition.
- **Sampling-based Bayes** is the alternative that doesn't require an explicit prediction-error representation.
- **Predictive-coding-without-Bayes** is the third option: descending predictions and ascending errors used for non-Bayesian goals.

The paper then surveys empirical evidence and assesses which framework each piece of evidence best supports.

## 5. Results

The principal claims and recommendations:

- **The framework is empirically *under-determined*.** Most empirical signatures cited in support of predictive coding (Rao-Ballard's extra-classical RF effects, Keller's mouse-V1 mismatch responses, Bastos's laminar frequencies) are consistent with non-Bayesian predictive coding *and* with Bayesian predictive coding *and* with sampling-based Bayesian inference. The framework choice is therefore underconstrained by current data.
- **Single-cell statistics can distinguish.** The trial-by-trial Poisson-like variability of cortical responses is naturally explained by sampling-based Bayesian inference; it requires additional assumptions in a pure-predictive-coding framework.
- **The combination is currently the best-supported.** Bayesian predictive coding — predictive coding implementing Bayesian inference — accounts for most of the empirical data, with the caveat that other combinations remain viable.
- **Direct tests of representation matter.** Distinguishing the frameworks requires *direct manipulation* of neural codes (e.g., perturbations during inference), not just observation of behavior or single-cell responses. The paper outlines candidate experiments.

## 6. Critique / limitations

The paper is a *clarifying review* without new empirical data. Its conclusions about the relative empirical support are based on assessment of existing literature, not new experiments.

The "predictive coding without Bayes" option is *underdeveloped*. The paper acknowledges it as a possibility (Srinivasan-style efficient coding) but doesn't survey deeply what the alternative computational goals could be. The user's coalition-competition thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) is exactly this kind of alternative goal — strategic competition rather than Bayesian inference — but is not anticipated by Aitchison & Lengyel.

The "sampling-based Bayes" framing assumes Poisson-like single-cell variability is the right signature. This is a contested empirical claim; some single-cell dynamics are not well-described by Poisson statistics.

The empirical signatures of "Bayesian predictive coding" vs "non-Bayesian predictive coding" are not crisply distinguished. The paper identifies candidate tests but doesn't carry them out.

The paper doesn't engage with the *deep-learning* implementations of predictive coding (Wen et al. 2018; Pinchetti et al. 2024). These models can in principle be evaluated against the framework distinctions but the 2017 paper predates the more recent benchmarking.

The paper is *cortex-centric*. Subcortical structures and their role in implementing or supporting Bayesian predictive coding are not addressed.

## 7. Connection to our work

This paper supplies precise theoretical vocabulary for the user's program's commitments:

**PRISM's architecture is predictive coding; its goal is configurable.** PRISM v1 and v2 implement Rao-Ballard predictive coding architecturally. Aitchison & Lengyel's distinction lets us say *what computational goal* the architecture serves: in PRISM v1, it's variational free-energy minimization (Friston-style Bayesian inference); in the user's coalition-competition extension, it's *strategic competition with rivals*. The architecture is the same; the goal differs.

**The user's competition-emergent-PC thesis as a non-Bayesian predictive coding.** The user's thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) is that predictive coding emerges *from competition* rather than from Bayesian inference. Aitchison & Lengyel's framework — *predictive coding as algorithm; the goal can differ* — gives the user's thesis a clean theoretical position: the architectural commitments stay; the *justification* changes.

**Distinguishing PRISM from sampling-based Bayesian alternatives.** Aitchison & Lengyel's discussion of sampling-based Bayesian inference is relevant: PRISM is *not* a sampling-based architecture. It maintains a single point estimate (the memory state) plus a variational distribution over the latent code. The architectural commitment is a *parametric* posterior rather than a *sampled* one — a Friston-style choice over the Knill-Pouget alternative.

**Empirical-test guidance.** The paper's recommendation to use direct neural perturbation to distinguish frameworks aligns with the recurrent ViT paper's attention-map ablation methodology (2502.10955 §6.6) and with the user's program's broader commitment to causal manipulation. The Aitchison-Lengyel framing is the theoretical justification for why these experiments matter.

**Multi-hub system framing.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) commits to *different hubs implementing different objectives*. Aitchison & Lengyel's separation of algorithm from goal makes this principled: each hub can use the same predictive-coding architecture but pursue a different computational goal (Bayesian inference for VAE; reward maximization for RL; mutual-information maximization for MSI). The architectural cleanliness depends on the algorithm-vs-goal distinction.

The recurrent ViT paper doesn't engage with this distinction. PRISM v1 makes the algorithm-and-goal couplings implicitly. Future manuscripts that clarify the user's program should cite Aitchison & Lengyel 2017 to make the algorithm-vs-goal separation explicit.

## 8. Citations to follow

- `rao_ballard1999_predictive_coding` — the predictive-coding algorithm. In seed, full depth.
- `friston2010_fep_unified_theory` — Friston's variational Bayesian inference. In seed, full depth.
- `clark2013_whatever_next` — philosophical synthesis. In seed, full depth.
- `keller_mrsic_flogel2018_pc_review` — empirical review. In seed, full depth.
- `spratling2008_pc_biased_competition` — alternative non-explicit-error implementation. In seed, full depth.
- `knill_pouget2004_bayesian_brain` — Bayesian-brain foundation. Not in seed.
- `ma2006_bayesian_decoding_pop_codes` — sampling-based Bayesian alternative. Not in seed.
- `pouget_beck_drugowitsch_latham2013_probabilistic_brains` — broader Bayesian-brain review. Not in seed.
- `srinivasan1982_predictive_coding_retina` — efficient-coding origin of predictive coding. In seed, full depth.
