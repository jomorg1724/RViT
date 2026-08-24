---
id: wen2018_deep_pc_networks
title: "Deep Predictive Coding Network for Object Recognition"
authors:
  - "Wen, Haiguang"
  - "Han, Kuan"
  - "Shi, Junxing"
  - "Zhang, Yizhen"
  - "Culurciello, Eugenio"
  - "Liu, Zhongming"
year: 2018
venue: "arXiv (cs.CV); later ICML 2018"
doi: ""
arxiv: "1802.04762"
url: "https://arxiv.org/abs/1802.04762"
tags:
  - predictive-coding
  - deep-learning
  - recurrent-networks
concepts:
  - hierarchical-predictive-coding
  - generative-decoder
  - prediction-error-map
  - top-down-feedback
  - rao-ballard-coding
related:
  - rao_ballard1999_predictive_coding
  - pinchetti2024_benchmark_pc_networks
  - friston2010_fep_unified_theory
  - kietzmann2019_recurrence_required
  - mazzaglia2022_fep_deep_learning
  - bardes2023_vjepa
  - bastos2012_canonical_microcircuits
  - spratling2008_pc_biased_competition
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-16"
---

# Deep Predictive Coding Network for Object Recognition

## 1. Abstract

The paper introduces a deep predictive coding network (PCN) — a bidirectional, recurrent convolutional architecture inspired by Rao-Ballard predictive coding in the visual cortex.

Each layer of the network produces both a feedforward representation and a top-down reconstruction of the layer below it; the residual between actual and predicted lower-level activity is the prediction error, which is propagated upward to refine the higher-level state. The same architecture is iterated for several cycles of recursive bottom-up–top-down computation, so that the representation at any layer is progressively refined over time without adding parameters.

On CIFAR-10, CIFAR-100, SVHN, and MNIST, the PCN consistently outperforms its feedforward-only counterpart, and accuracy improves with additional cycles. The contribution is to demonstrate that the Rao-Ballard inferential loop, when stacked into a deep convolutional hierarchy and trained discriminatively with cross-entropy, yields a measurable improvement over a matched feedforward baseline on standard object-recognition benchmarks.

## 2. Why this matters for us

This is the canonical modern attempt to scale Rao & Ballard's two-level predictive-coding architecture into a deep convolutional network trained on real image-classification benchmarks. It is the empirical bridge between the theoretical predictive-coding tradition (Rao & Ballard 1999; Friston 2010) and the deep-learning practice that the user's program inhabits.

For PRISM, it supplies two things:

1. A worked example that the predictive-coding inferential loop *does* yield gains over a feedforward baseline when integrated into a CNN, supporting the architectural commitment of PRISM v1 and v2 to a top-down generative pathway plus a prediction-error map.
2. A cautionary datapoint about the *ceiling* of straightforward "deep Rao-Ballard" architectures — PCN beats its own feedforward baseline but does not approach the state-of-the-art set by deeper supervised CNNs (ResNet, WideResNet) on the same benchmarks.

This is the practical-limits result that motivates moving beyond a pure deep PC implementation toward hybrid designs (PRISM v1's GRU memory; PRISM v2's slow/fast dual memory; the user's full Feedback Transformer program).

## 3. Key claims

1. The Rao-Ballard predictive-coding inferential loop can be instantiated in a deep convolutional architecture and trained end-to-end by backpropagation with a standard discriminative loss.
2. At each layer, feedback connections carry top-down predictions of the lower layer's representation; feedforward connections carry the residual prediction error to the higher layer.
3. Recursive iteration of the bottom-up–top-down computation refines the representation over computational time, effectively producing a deeper network in time without additional parameters.
4. On CIFAR-10, CIFAR-100, SVHN, and MNIST, the PCN outperforms a matched feedforward-only baseline, and the accuracy improves monotonically with the number of cycles up to a saturation point.
5. The improvement is consistent across datasets and depths, indicating that the predictive-coding loop is a generally useful architectural addition to a feedforward backbone, not a dataset-specific trick.

## 4. Methods

**Architecture.** The PCN is a stack of convolutional layers indexed $\ell = 1, \dots, L$. Each layer maintains an internal representation $r_\ell$.

The feedforward pathway computes a candidate representation from the layer below,
$$\tilde r_\ell = f(W_\ell^{ff}\, r_{\ell-1}),$$
where $W_\ell^{ff}$ is a learned convolutional kernel and $f$ a pointwise nonlinearity (ReLU).

The feedback pathway computes a top-down prediction of the lower layer from the higher layer,
$$\hat r_{\ell-1} = g(W_\ell^{fb}\, r_\ell),$$
where $W_\ell^{fb}$ is a learned (deconvolutional / transposed-convolutional) kernel.

The prediction error at layer $\ell-1$ is the residual
$$\epsilon_{\ell-1} = r_{\ell-1} - \hat r_{\ell-1}.$$
The representation at layer $\ell$ is updated by a gated combination of the feedforward candidate and a correction driven by the error from below,
$$r_\ell^{(t+1)} = (1 - \alpha) r_\ell^{(t)} + \alpha\big(\tilde r_\ell + W_\ell^{ff}\, \epsilon_{\ell-1}\big),$$
with a similar update rule for the lower layers driven by the descending prediction.

This is the Rao-Ballard update written in the deep-network idiom: the residual error replaces the raw feedforward activity as the bottom-up signal once the prediction is online. The learned $W^{ff}$ and $W^{fb}$ matrices play the role of Rao and Ballard's encoder and decoder $U$; the difference is that they are not tied (they are not required to be transposes of one another) and that the nonlinearity is the modern ReLU rather than a generative-Gaussian likelihood.

**Iteration.** Given an input image, the network is initialised by a single feedforward pass producing $r_\ell^{(0)}$ at every layer. The PCN then runs $T$ cycles of the bottom-up–top-down update (typical $T \in \{3, 4, 5, 6\}$ in the experiments). The final representation $r_L^{(T)}$ feeds a linear classifier producing class logits.

The parameters $W^{ff}_\ell$, $W^{fb}_\ell$, and the gating coefficient $\alpha$ are shared across all $T$ cycles. The effective depth of the unrolled computation is therefore $T \cdot L$, but the parameter count is fixed at the single-pass count.

**Training.** The whole network — feedforward weights, feedback weights, classifier — is trained end-to-end on the standard image-classification objective (softmax cross-entropy on the class label) using stochastic gradient descent with momentum. No explicit reconstruction loss is added; the prediction error is purely a computational mechanism inside the inferential loop, not a training signal. Gradients flow through all $T$ cycles via backpropagation through time. The number of unrolled cycles at training time and at inference time is the same, although the paper also reports cross-cycle ablations in which the network is trained at one $T$ and evaluated at another.

**Relationship to Rao-Ballard.** The PCN is a faithful deep-network realisation of the Rao-Ballard two-level inferential update generalised to $L$ levels and to learned convolutional encoders/decoders. The principal departures from the 1999 paper are:

1. end-to-end discriminative training rather than unsupervised generative-model training on natural-image patches;
2. learned nonlinear convolutional encoders rather than linear-Gaussian encoders;
3. a fixed number of cycles rather than gradient descent to convergence;
4. the residual error is computed at every level of a deep stack rather than only between two levels;
5. parameter tying across cycles (a recurrent network unrolled in computational time) rather than per-iteration parameters.

The construction preserves the load-bearing Rao-Ballard commitments — descending feedback as prediction, ascending feedforward as error — while shedding the generative-model loss that originally justified them.

## 5. Results

**Headline result.** On all four benchmarks the PCN beats a matched feedforward-only baseline (same parameter count, same training schedule, $T=1$ cycle = pure feedforward). The reported improvement is consistent across datasets: roughly a 1–3 percentage-point reduction in test error over the feedforward baseline at the best cycle count, with the gain growing with depth of the backbone.

**Cycle-count dependence.** The dependence on the number of cycles is monotonic but saturating: most of the gain is captured by $T = 3$ or $T = 4$ cycles, with further cycles giving diminishing returns and the curve flattening by $T \approx 6$. The behaviour is consistent with the Rao-Ballard prediction that the inferential loop converges to a fixed point in a small number of iterations.

**Cross-dataset consistency.** The qualitative pattern — feedforward baseline at $T=1$, monotone improvement to a saturation cycle, marginal gains thereafter — holds across CIFAR-10, CIFAR-100, SVHN, and MNIST. The relative gain is largest on the harder benchmarks (CIFAR-100) and smallest on the saturated ones (MNIST), consistent with the intuition that the inferential loop helps most when the feedforward representation is genuinely uncertain.

**Comparison to SOTA.** The absolute accuracies the PCN achieves are competitive with mid-2010s supervised CNNs but do not match the state-of-the-art set by very-deep residual networks (ResNet, WideResNet, DenseNet) on the same benchmarks. The paper's framing is therefore comparative-to-baseline rather than headline-to-SOTA: the predictive-coding loop is shown to be a useful architectural addition, not a replacement for the depth and capacity of leading supervised CNNs.

**Qualitative analyses.** The paper also reports visualisation of the prediction-error maps and of the representational dynamics across cycles. The error maps decrease in magnitude as cycles proceed, consistent with the inferential-loop interpretation; the representation at higher layers shows progressive sharpening of class-relevant features. These analyses are qualitative rather than quantitative, but they support the mechanistic reading of the architecture.

## 6. Critique / limitations

**The empirical ceiling against SOTA.** The most important caveat is the one the paper itself does not stress: the PCN's gains are over its own feedforward ablation, not over the best contemporary supervised CNNs. Subsequent empirical benchmarking (Pinchetti et al. 2024) has confirmed that deep predictive-coding networks of this kind systematically underperform comparable-depth backpropagation-trained networks on object-recognition tasks, particularly as scale increases. The PCN is therefore best read as evidence that the Rao-Ballard loop is *useful* in deep architectures, not as evidence that it is *sufficient* to compete with the best feedforward designs.

**Discriminative training versus the generative motivation.** The architectural choice to train with a purely discriminative loss elides the question that motivates predictive coding in the first place — whether the prediction error is doing the work of approximate Bayesian inference or merely serving as a learned auxiliary feature. The paper does not test whether the same gain could be obtained by other forms of residual or recurrent connection (e.g., generic gated recurrence, dense feedback without an explicit predictive interpretation). Spratling-style alternatives (Spratling 2008) — where the same end-stopping phenomena are reproduced by divisive-normalisation feedback without explicit error neurons — are not addressed.

**Mechanism vs. effective depth.** The cycle-count dependence is reported but its mechanistic interpretation is thin. Whether the gain reflects refinement of the latent state toward a generative-model fixed point or simply increased effective depth (parameter sharing across cycles) is not separated experimentally. The two hypotheses have very different implications for scaling: under the fixed-point reading, gains should saturate; under the effective-depth reading, gains should track parameter count and the cycles should be replaceable by un-tied per-cycle parameters.

**No unsupervised baseline.** The training regime is fully supervised. The unsupervised generative-modelling stance that motivates Rao-Ballard (and that underlies the Friston free-energy generalisation) is not tested. The PCN therefore does not address the central theoretical claim that predictive coding is a self-supervised learning principle; it tests only the inferential loop as a feedforward-augmenting mechanism.

**Benchmark scope.** The benchmarks are small (CIFAR, SVHN, MNIST). No ImageNet result is reported; no transfer to video, object detection, or self-supervised learning is shown. The video-prediction sibling of the PCN — Lotter, Kreiman & Cox's PredNet (2017) — uses a closely related architecture with a reconstruction loss but is a separate work; the two lines do not converge.

**No biological validation.** Although motivated by Rao & Ballard's neurophysiological claims (Gabor RFs, end-stopping, surround suppression), the PCN is not evaluated on whether it reproduces any of these effects. The motivation is biological, the validation is purely benchmark accuracy.

## 7. Connection to our work

The deep PCN is the closest direct precedent in the literature for the PRISM-style architecture and for the user's broader program (`threads/the_user_architectural_program.md` §3). PRISM v1's commitment to a feedforward V1 stem, a top-down generative decoder, and a prediction-error map (`THESIS.md` §2.5–§2.6) is structurally the same construction as Wen et al.'s PCN, with three substantive differences:

- PRISM v1 trains the decoder on a reconstruction loss (free-energy / ELBO interpretation, `THESIS.md` §2.11), where the PCN trains end-to-end on classification cross-entropy. PRISM therefore exercises the *generative* interpretation of predictive coding that Wen et al. set aside. The PCN's choice is defensible — discriminative training is what produces state-of-the-art classification — but it leaves the unsupervised representation-learning thesis untested.
- PRISM v1 uses the prediction-error map as an attention / saliency signal that modulates a recurrent memory (the saliency-gated GRU update, `THESIS.md` §2.7), where the PCN re-injects the error into the same feedforward stack. The user's reformulation casts the error as the bottom-up input to a separate memory pathway, not as a perturbation of the encoder representation. This is closer in spirit to Friston (2010) and to the user's competition-emergent reformulation (`threads/the_user_architectural_program.md` §5).
- PRISM v2 stacks two cortical levels with cross-level error and prediction flow (`PRISM_V2_PROPOSAL.md` §3.10); the PCN stacks many levels but with a single inferential loop per pair, not the two-level dual-memory structure that PRISM v2 commits to. PRISM v2's slow / fast dual memory has no analog in the PCN.

The user's full program (Feedback Transformer; multi-compartmental memory; iterative variational encoder–decoder; competition-emergent predictive coding) goes substantially beyond the PCN in three ways:

1. feedback is integrated into the Q/K/V structure of self-attention rather than as a convolutional residual;
2. the memory is multi-compartmental and bidirectionally hierarchical rather than a single recurrent stack;
3. the predictive-coding interpretation is recast as a strategic response to inter-coalition competition rather than as a sensory-prediction architecture (`threads/the_user_architectural_program.md` §5).

**Practical-limits lesson.** The PCN's empirical ceiling — gains over feedforward baselines, no match for ResNet — is the central practical lesson for the program. It tells us that a naive deep Rao-Ballard implementation is not, by itself, the route to state-of-the-art recognition. The user's commitment to combine the predictive-coding loop with (a) recurrent memory, (b) variational training objectives, and (c) attention-based feedback integration is therefore not optional decoration; it is the substantive architectural bet that the additional structure is what turns a useful auxiliary mechanism into a competitive backbone.

**Task choice.** PRISM v1's change-detection benchmark — a task on which Rao-Ballard-style temporal prediction is the natural fit — is a deliberate choice of evaluation regime that avoids head-to-head competition with deep supervised CNNs on the object-recognition task on which the PCN was already shown to lose ground (`THESIS.md` §1.4, bitter-lesson framing). Change detection rewards the generative-model interpretation directly: the predicted next frame is the natural target the architecture is designed to compute.

**Saturation pattern.** The PCN's monotonic-but-saturating cycle-count effect is mirrored in the user's Food-101 classifier experiments (`threads/the_user_architectural_program.md` §6), where additional recurrent passes improve accuracy up to a saturation point. This is a small but real cross-confirmation: the inferential-loop interpretation of recurrence in vision predicts exactly the saturation pattern observed in both Wen et al. and the user's recurrent-ViT work. Whether the saturation reflects a fixed-point of an underlying generative model or a depth-effect of parameter sharing is the next question both lines should answer.

**What PRISM v2 borrows and what it does not.** PRISM v2 takes from Wen et al. the commitment to a multi-layer inferential loop, but explicitly does *not* take the parameter-sharing across cycles: PRISM v2's slow and fast memories have separate weights, separate update rates, and separate roles. The point of contact is the bidirectional convolutional decoder–encoder structure; the point of departure is the dual-memory pathway and the variational training objective.

## 8. Citations to follow

- `rao_ballard1999_predictive_coding` — the theoretical foundation; already in the database. The PCN is its deep-network instantiation.
- `pinchetti2024_benchmark_pc_networks` — direct benchmarking of PC networks against standard deep nets; quantifies the empirical ceiling Wen et al. flag implicitly.
- `friston2010_fep_unified_theory` — the variational-inference generalisation that the PCN's discriminative training elides; the route by which PRISM justifies the generative-loss interpretation Wen et al. do not test.
- `kietzmann2019_recurrence_required` — recurrence-is-required-for-cortex-like recognition; complementary evidence that the kind of inferential loop the PCN implements is necessary, not merely useful.
- `bastos2012_canonical_microcircuits` — laminar-microcircuit refinement of Rao-Ballard; relevant for understanding which parts of the PCN map to which cortical layers (In seed, full depth; candidate).
- `spratling2008_pc_biased_competition` — biased-competition alternative to explicit error neurons; the natural Spratling-style critique of the PCN architecture.
- `lotter2017_prednet` — Lotter, Kreiman & Cox's PredNet (arXiv:1605.08104); video-prediction sibling of the PCN, important contrast in training objective (next-frame reconstruction vs. classification).
- `han2018_deep_predictive_coding_unsupervised` — Wen-lab follow-up applying the same loop to unsupervised learning; tests the generative interpretation the 2018 paper sets aside.
