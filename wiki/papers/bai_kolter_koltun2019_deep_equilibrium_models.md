---
id: bai_kolter_koltun2019_deep_equilibrium_models
title: "Deep Equilibrium Models"
authors:
  - "Bai, Shaojie"
  - "Kolter, J. Zico"
  - "Koltun, Vladlen"
year: 2019
venue: "NeurIPS"
doi: ""
arxiv: "1909.01377"
url: "https://arxiv.org/abs/1909.01377"
tags:
  - deep-learning
  - recurrent-networks
  - theoretical-essay
  - methodology
concepts:
  - one-step-implicit-gradient
  - hierarchical-convergence
related:
  - wang2025_hierarchical_reasoning_model
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-14"
---

# Deep Equilibrium Models

## 1. Abstract

The paper introduces *Deep Equilibrium Models* (DEQ), an approach to sequential modeling in which a deep weight-tied feedforward network is reformulated as a *root-finding problem*: instead of computing through many sequential layers, find the fixed point $z^* = f(z^*; x; \theta)$ of the layer-update equation. Inference is performed by black-box root-finding (e.g., Broyden's method or fixed-point iteration); training uses *implicit differentiation* via the implicit function theorem to compute gradients through the equilibrium point. This enables "infinite-depth" weight-tied feedforward networks with *constant memory* in depth, in contrast to BPTT-style training which requires storing all intermediate activations. On sequence modeling benchmarks (WikiText-103 language modeling), DEQ-based transformers and trellis networks match or outperform parameter-matched baselines while using up to 88% less memory.

## 2. Why this matters for us

DEQ supplies the theoretical foundation for the *one-step implicit-gradient* training scheme that HRM ([wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md)) uses to avoid BPTT. The user's program may eventually adopt a similar training framework for the multi-hub architecture, especially as the hub stacks grow deep enough to make BPTT impractical. DEQ also gives a principled answer to the question "what does a deep recurrent network converge to?" — namely, a fixed point that can be characterized algebraically rather than just trained for. This is relevant to PRISM v2's slow memory dynamics (does it converge to a fixed point? what does that fixed point represent?) and to any future extension that aims to formalize the dynamical-system behavior of the user's architectures.

## 3. Key claims

1. Many sequence and recurrent models with weight-tied layers can be reformulated as root-finding for a fixed point $z^*$ satisfying $z^* = f(z^*; x; \theta)$, where $f$ is the weight-tied layer.
2. Inference at the fixed point can be performed by *black-box root-finding* (Broyden's method, Anderson acceleration, simple fixed-point iteration). The choice of root-finder affects inference speed but not the underlying solution.
3. **Implicit differentiation** allows training without unrolling. The gradient with respect to $\theta$ is $\partial z^* / \partial \theta = (I - \partial f / \partial z)^{-1} \cdot \partial f / \partial \theta$, computed at the converged fixed point. This requires solving a linear system (or approximating the inverse) but does *not* require storing intermediate activations.
4. **Memory complexity.** DEQ uses $O(1)$ memory in depth (only the fixed point and the Jacobian-vector products), in contrast to BPTT's $O(T)$ for $T$ unrolled steps. The paper reports memory savings of up to 88% over comparably-performing baselines.
5. **Empirical validation.** Two specific DEQ instantiations — transformer-based and TrellisNet-based — are compared to standard weight-untied transformers and TrellisNets on WikiText-103 language modeling. DEQ matches or exceeds the baselines' perplexity at comparable parameter counts.
6. The DEQ framework subsumes many existing recurrent architectures as special cases: any weight-tied feedforward network that converges to a fixed point can be cast as a DEQ; standard RNNs unrolled for $T$ steps approach the DEQ limit as $T \to \infty$.

## 4. Methods

**Forward pass.** Given input $x$ and parameters $\theta$, find $z^*$ such that $z^* = f(z^*; x; \theta)$ where $f$ is the layer-update function (a transformer block, a trellis-network block, etc.). The authors use Broyden's quasi-Newton method as the default root-finder; Anderson acceleration and pure fixed-point iteration are also tested.

**Backward pass.** The gradient $\nabla_\theta \mathcal{L}$ requires $\partial z^* / \partial \theta$. By the implicit function theorem applied to $g(z^*, \theta) = z^* - f(z^*; x; \theta) = 0$:

$$
\frac{\partial z^*}{\partial \theta} = -\left( \frac{\partial g}{\partial z^*} \right)^{-1} \frac{\partial g}{\partial \theta} = \left( I - \frac{\partial f}{\partial z^*} \right)^{-1} \frac{\partial f}{\partial \theta}.
$$

Computing this exactly requires solving an $n \times n$ linear system in the hidden-state dimension $n$. The authors use iterative methods (Krylov / Broyden) that compute the gradient with $O(n)$ memory.

**One-step gradient approximation.** As an alternative to the full implicit gradient, the authors propose approximating $(I - \partial f / \partial z^*)^{-1} \approx I$, giving $\partial z^* / \partial \theta \approx \partial f / \partial \theta$ evaluated at $z^*$. This is the "one-step" approximation HRM adopts; it is faster but introduces approximation error.

**Architectures tested.** The authors implement two DEQs: (a) DEQ-Transformer (a transformer block as $f$); (b) DEQ-TrellisNet (a TrellisNet block as $f$). Both are tested on WikiText-103.

## 5. Results

The principal quantitative findings:

- **Performance.** DEQ-Transformer (≈110M parameters) achieves WikiText-103 test perplexity of ~23.2, compared to the parameter-matched standard transformer baseline at ~24.0. DEQ-TrellisNet shows similar gains over TrellisNet baselines.
- **Memory.** DEQ uses constant memory in depth, achieving 88% memory reduction at comparable performance vs the deepest baseline they compare against.
- **Compute.** Inference time per token is comparable to baselines (Broyden's method requires several iterations but each iteration is cheaper than a deep-unrolled forward pass).
- **Convergence.** The fixed-point iteration converges in 10–25 iterations on average for the trained models. The "infinite depth" is in practice a few dozen effective layers.
- **One-step gradient.** Empirically, the one-step gradient approximation works almost as well as the full implicit gradient, with modest performance gaps in language modeling.

## 6. Critique / limitations

The DEQ framework requires the layer-update function $f$ to *have* a fixed point. Not all weight-tied feedforward networks converge — divergent or chaotic dynamics are possible. The authors restrict to architectures known to be contractive (transformers with layer normalization typically converge; arbitrary RNNs may not).

The implicit-gradient computation requires solving a linear system, which can be expensive for high-dimensional hidden states. For very large models, the gradient cost can dominate training time even though memory is $O(1)$.

The one-step gradient approximation introduces error. For well-converged fixed points and contractive $f$, the error is small; for marginal cases, it can be substantial. The empirical validation is limited to language modeling; whether the approximation works as well on other tasks is open.

The paper doesn't engage with biological plausibility. Subsequent work (e.g., HRM 2025) has argued that the implicit-gradient framework aligns with cortical credit assignment (short-range, temporally local), but the 2019 DEQ paper itself doesn't make this case.

The training procedure assumes the fixed point exists *during training*. Early in training, when parameters are random, the fixed point may not be well-defined or stable. The authors handle this with careful initialization and gradual training schedules; a fully principled solution to the early-training instability is still open.

## 7. Connection to our work

This paper supplies the foundational training framework for the user's most plausible future architectural extension:

**HRM's one-step implicit gradient is DEQ.** HRM ([wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md) §4) uses exactly the one-step gradient approximation from this paper. Specifically, HRM's "Output head → final state of H-module → final state of L-module → input embedding" gradient pathway is the DEQ one-step approximation applied to each of the two modules. The user's program inherits this through HRM: any future PRISM variant that uses the HRM-style hierarchical convergence ([hierarchical_convergence](research_db/concepts/slow_fast_recurrence.md)) can adopt the DEQ training scheme directly.

**O(1) memory for deep architectures.** The user's program commits to many-hub, multi-compartmental memory architectures ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md), [multi_compartmental_memory](research_db/concepts/multi_compartmental_memory.md)). At sufficient scale, BPTT through these systems will become impractical. DEQ provides the training framework that makes the scaling feasible: store only the final fixed-point states, compute gradients via implicit differentiation.

**Formalizing PRISM v2's dynamical-system behavior.** PRISM v2's slow memory is updated rarely (per-step probability ≈0.05). Over many steps, what does it converge to? DEQ provides the right vocabulary for asking this question: the slow memory is implementing a fixed-point iteration; the "what it converges to" is the fixed point $z^*$ of its update equation. Formal characterization of this fixed point — when it exists, how it depends on the input, whether it's stable — is a useful future analysis direction.

**Hub-level coordination as inter-hub fixed points.** In the multi-hub system, each hub maintains its own state; the hubs interact through the central self-attention substrate. The system's joint behavior can be cast as finding a joint fixed point across hubs — the equilibrium where each hub's state is consistent with all other hubs' contributions to the central substrate. DEQ supplies the training framework for this kind of joint-equilibrium computation; the implicit-gradient approach is the obvious training scheme for the multi-hub system at scale.

The recurrent ViT paper (2502.10955) uses standard BPTT through unrolled recurrence. PRISM v1 and v2 do the same. DEQ is therefore a *future* architectural direction for the user's program; it is not currently used.

## 8. Citations to follow

- `wang2025_hierarchical_reasoning_model` — HRM, the main current consumer of DEQ-style training. In seed, full depth.
- `bai2020_multiscale_deq` — Bai et al.'s follow-up on multi-scale DEQ. Not in seed.
- `el_ghaoui2021_implicit_models` — broader theoretical framework for implicit models. Not in seed.
- `winston_kolter2020_monotone_deq` — monotone DEQ ensuring convergence. Not in seed.
- `pokle2022_deep_equilibrium_approaches` — Pokle et al. review. Not in seed.
- `gu_kolter_anandkumar2022_neural_differential_equations` — connection to neural ODEs. Not in seed.
