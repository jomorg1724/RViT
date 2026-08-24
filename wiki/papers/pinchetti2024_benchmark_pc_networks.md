---
id: pinchetti2024_benchmark_pc_networks
title: "Benchmarking Predictive Coding Networks -- Made Simple"
authors:
  - "Pinchetti, Luca"
  - "Qi, Chang"
  - "Lokshyn, Oleh"
  - "Olivers, Gaspard"
  - "Emde, Cornelius"
  - "Tang, Mufeng"
  - "M'Charrak, Amine"
  - "Frieder, Simon"
  - "Menzat, Bayar"
  - "Bogacz, Rafal"
  - "Lukasiewicz, Thomas"
  - "Salvatori, Tommaso"
year: 2024
venue: "arXiv"
doi: ""
arxiv: "2407.01163"
url: "https://arxiv.org/abs/2407.01163"
tags:
  - predictive-coding
  - deep-learning
  - bio-plausible-learning
  - methodology
concepts:
  - hierarchical-predictive-coding
  - rao-ballard-coding
  - variational-free-energy
  - prediction-error-map
  - inner-inference-loop
related:
  - wen2018_deep_pc_networks
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
  - mazzaglia2022_fep_deep_learning
  - bai_kolter_koltun2019_deep_equilibrium_models
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-15"
---

# Benchmarking Predictive Coding Networks -- Made Simple

## 1. Abstract

In this work, we tackle the problems of efficiency and scalability for predictive coding networks (PCNs) in machine learning. To do so, we propose a library, called PCX, that focuses on performance and simplicity, and use it to implement a large set of standard benchmarks for the community to use for their experiments. As most works in the field propose their own tasks and architectures, do not compare one against each other, and focus on small-scale tasks, a simple and fast open-source library and a comprehensive set of benchmarks would address all these concerns. Then, we perform extensive tests on such benchmarks using both existing algorithms for PCNs, as well as adaptations of other methods popular in the bio-plausible deep learning community. All this has allowed us to (i) test architectures much larger than commonly used in the literature, on more complex datasets; (ii) reach new state-of-the-art results in all of the tasks and datasets provided; (iii) clearly highlight what the current limitations of PCNs are, allowing us to state important future research directions.

## 2. Why this matters for us

PRISM v1 and v2 commit, at the architectural level, to a predictive-coding-style inner inference loop (`THESIS.md` §2.8 — the per-step variational update of $M_t$). Whether such a loop can be made to scale at all — i.e., whether predictive-coding networks are competitive with backprop-trained CNNs at the parameter counts and dataset sizes our change-detection and video-VAE benchmarks demand — is an open empirical question that this paper is the most direct attempt to answer. The paper's headline finding is that with their PCX library, PC reaches near-backprop accuracy on CIFAR-10 / CIFAR-100 / Tiny ImageNet with VGG-5-class architectures, but performance *degrades* when depth is increased to VGG-7 because of an "energy imbalance" pathology between deep and shallow layers. This is precisely the regime PRISM v1's stacked-PC-block architecture lives in; the paper's diagnostics tell us what to monitor and what to engineer against.

## 3. Key claims

1. A fast, JAX-based open-source PC library (PCX) is feasible; it is ~3–4x faster than prior PC implementations and brings PCN training within a constant factor of backprop wall-clock time.
2. With careful per-task hyperparameter tuning, six PC variants (standard PC, incremental PC, Monte-Carlo PC, positive / negative / centered nudging) approach backprop accuracy on MLPs and small ConvNets (VGG-5) across MNIST, FashionMNIST, CIFAR-10, CIFAR-100, and Tiny ImageNet.
3. PC underperforms backprop reliably as depth grows: VGG-7 is worse than VGG-5 under PC, contradicting the deep-learning norm of monotonic gains with depth.
4. The mechanism is an "energy imbalance" — at convergence of the inner inference loop, prediction-error energy concentrates in the output layer and is up to six orders of magnitude smaller in the first hidden layer, starving early-layer weight updates of gradient signal.
5. Wide networks under Adam are unstable in a way backprop networks are not: the range of learning rates that produces stable PC training shrinks with width.
6. PC autoencoders match or modestly beat backprop on reconstruction MSE for CIFAR-10 — i.e., the generative regime is the most competitive setting for PC.
7. Scalability — not biological plausibility — is identified as the field's central open problem; the authors call for regularization or normalization techniques that re-balance the per-layer error energy.

## 4. Methods

**Predictive coding formulation.** A PCN is a hierarchical Gaussian generative model $p(x_0, x_1, \ldots, x_L) = \prod_\ell \mathcal{N}(x_\ell ; f_\ell(x_{\ell+1}; W_\ell), \sigma^2 I)$ with free-energy

$$
\mathcal{F}(\{x_\ell\}, \{W_\ell\}) = \sum_\ell \tfrac{1}{2} \|x_\ell - f_\ell(x_{\ell+1}; W_\ell)\|^2.
$$

Training alternates two phases per minibatch:
- **Inference phase.** With weights $W$ frozen and the input and (for discriminative tasks) target clamped to $x_0$ and $x_L$, run $T$ steps of gradient descent on $\mathcal{F}$ in the latent activations: $x_\ell \leftarrow x_\ell - \eta_x \, \partial \mathcal{F} / \partial x_\ell$.
- **Learning phase.** Take one gradient step on $W$ at the inferred latents: $W_\ell \leftarrow W_\ell - \eta_W \, \partial \mathcal{F} / \partial W_\ell$. The gradient is purely local — depends only on the pre- and post-synaptic activations and the local error term $\epsilon_\ell = x_\ell - f_\ell(x_{\ell+1}; W_\ell)$.

**Algorithm variants.** (i) *Standard PC*: alternating inference / learning as above. (ii) *Incremental PC (iPC)*: weights are updated *during* inference, every step, rather than only after $T$ steps. (iii) *Monte-Carlo PC (MCPC)*: latents are stochastic. (iv) *Positive / Negative / Centered Nudging (PN, NN, CN)*: the output is nudged toward the target with strength $\beta \in (0, 1)$ (positive), away from the prediction (negative), or both (centered) — direct analogs of Scellier-style Equilibrium Propagation.

**Architectures.** MLPs (3 hidden layers, 128 units each) and convolutional VGG-style stacks (VGG-5 and VGG-7).

**Datasets.** Discriminative: MNIST, FashionMNIST, CIFAR-10, CIFAR-100, Tiny ImageNet. Generative: MNIST, FashionMNIST, CIFAR-10, CelebA for autoencoding and associative-memory tasks.

**Hyperparameters.** Inference steps $T \in [12, 128]$ are swept; optimal $T$ is in the 50–100 range for the harder datasets. Inference learning rate $\eta_x = 1.0$. Weight learning rate $\eta_W$ requires per-dataset tuning and is the locus of the width-dependent instability the paper documents.

## 5. Results

**Discriminative accuracy (test, top-1):**

| Dataset | Architecture | Best PC variant | PC accuracy | BP baseline |
|---|---|---|---|---|
| MNIST | MLP | iPC | 98.45% | ~98.5% |
| FashionMNIST | MLP | iPC | ~90% | ~90% |
| CIFAR-10 | VGG-5 | CN | 89.47% | ~90% |
| CIFAR-100 | VGG-5 | CN | 67.19% | ~67% |
| Tiny ImageNet | VGG-5 | NN | 46.40% | ~47% |

**Depth pathology.** Switching VGG-5 → VGG-7 *reduces* PC test accuracy on CIFAR-100 by several points across all PC variants, while BP gains.

**Generative reconstruction (CIFAR-10 autoencoder, MSE ×10⁻³):** iPC 5.50 vs BP 6.17 — PC outperforms BP in the autoencoding regime.

**Energy imbalance (Sec. 5 of the paper).** Measured at the end of inference with the optimal small $\eta_W$, the L2 norm of the layer error $\|\epsilon_\ell\|^2$ in the first hidden layer is 6 orders of magnitude below that of the output layer. This holds across VGG-5 and VGG-7 and is the diagnostic the authors point to as the mechanism behind the depth pathology.

**Wall-clock.** PCX trains VGG-5 on CIFAR-100 in ~5.3 s per epoch vs. ~1.6 s for backprop — a 3.3x slowdown attributable to the $T$-step inference loop. This is the *best* multiplier reported in any open-source PC implementation; the previous reference library was another ~3–4x slower again.

## 6. Critique / limitations

The paper's most important contribution is honest and important — it documents that PCNs do not currently scale. But several caveats temper the result.

First, the comparison is to backprop with cross-entropy or squared-error losses on the same architectures. It does not control for the fact that PC's inner loop effectively performs $T$ extra forward-backward passes' worth of computation; a fair compute-matched comparison would give backprop $T$ extra training steps and is not reported.

Second, the "energy imbalance" diagnostic is a *correlate* of the depth pathology, not a proven cause. The paper does not show that explicitly re-balancing layer energies (e.g., by per-layer learning-rate scaling or by a precision-weighting term in $\mathcal{F}$) recovers backprop-level performance. Section 6.2 leaves this as future work.

Third, the architectures tested top out at VGG-7 ConvNets. No attention-based PCN is tested. Whether the depth pathology is specific to convolutional stacks or generic to PC is therefore unresolved. PRISM v1/v2 use attention-style memory, not VGG stacks, so this is the most important gap from our standpoint.

Fourth, no recurrent or video task is benchmarked. The discriminative regime is single-image classification only.

Fifth, the nudging variants (PN, NN, CN) blur the line between PC and Equilibrium Propagation; the paper acknowledges this but does not provide a unified theoretical analysis of when nudging-PC reduces to Eqprop.

Sixth, the dataset ceiling is Tiny ImageNet (200 classes, 64×64); ImageNet-1k is not reported, so the most demanding test of scalability is absent.

## 7. Connection to our work

The user's architectural program (`threads/the_user_architectural_program.md`) and PRISM v1 (`Prism/docs/THESIS.md`) commit to a predictive-coding-style update mechanism at multiple levels: the inner inference loop over $M_t$ in PRISM v1 (§2.8), the "competition-emergent predictive coding" thesis (Thread §5), and the bidirectional descending/ascending feedback in the multi-compartmental memory stack (Thread §3). Pinchetti et al. is the first paper to give us a *quantitative* picture of how a vanilla implementation of the PC inference loop scales, and the answer is sobering. Three specific implications for our work follow.

**(a) The depth pathology argues for hybrid PC + BP training.** PRISM v1's prediction-error-as-attention mechanism (§2.3) and inner inference loop (§2.8) sit inside a network whose outer training signal is end-to-end backprop, not pure PC. This paper supports that choice: pure PC training of the entire stack would inherit the depth pathology. PRISM should keep PC as an *architectural mechanism* (a way of computing attention from descending predictions) rather than promoting it to a learning rule.

**(b) The energy imbalance diagnostic is directly applicable to PRISM v2.** PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) injects descending memory at multiple depths; the user's reference 3-layer design (Thread §3, "Layer 1 / Layer 2 / Layer 3") has explicit channel and resolution mismatches across layers. Pinchetti et al.'s finding that PC errors concentrate in the deepest layer suggests that without an explicit per-layer normalization, deeper FiLM injections will dominate the loss surface and starve shallow injections — the analog of "first hidden layer is 6 orders of magnitude below the last layer." We should monitor per-layer FiLM-gradient norms and consider GroupNorm or layer-wise loss scaling (consistent with the MCLSTM finding in `memory/project_mclstm_architecture_findings.md` that GroupNorm was load-bearing for stable training).

**(c) The generative regime is the favorable one.** PC matches or beats BP on autoencoding (CIFAR-10 MSE) and underperforms on classification. This maps directly onto the user's Video VAE work (Thread §4 — "iterative variational encoder–decoder"), which is generative, and is consistent with the user's reported empirical success there (Thread §6 — "Video autoencoding" is the most successful instance of the program). The user's instinct to lead with the variational encoder-decoder over change-detection classification is supported by this paper's discriminative-vs-generative split.

**(d) Compute cost is a real constraint.** A 3.3x wall-clock penalty for the $T$-step inference loop is the *best case* reported. PRISM v1's variational inner loop has the same structure and will inherit this cost. The published Recurrent ViT (2502.10955) chose not to expose an inner loop at all, and is fast; PRISM v1's underperformance relative to v0 may partly reflect this compute trade-off. The DEQ literature (`bai_kolter_koltun2019_deep_equilibrium_models`) offers an orthogonal solution: backprop only through the final-step Jacobian at the converged fixed point, avoiding BPTT over the inner loop. That technique should be tried in PRISM v2 (and is already flagged in TAXONOMY.md as `one-step-implicit-gradient`).

In short: this paper does not refute the architectural program, but it sets the empirical expectation that pure-PC training will plateau at VGG-5-class accuracy, and identifies the specific failure mode (energy imbalance, width-dependent instability) that future PC architectures — including ours — must address.

## 8. Citations to follow

- `scellier_bengio2017_equilibrium_propagation` — Eqprop; the nudging-PC variants in this paper are functionally close to Eqprop and the unified treatment is open.
- `millidge2022_pc_approximates_backprop` — theoretical result that PC inference converges to BP gradients; the depth pathology shown here is in tension with that limit and needs reconciling.
- `whittington_bogacz2017_pc_with_local_hebbian` — the local-learning-rule formulation Pinchetti et al. inherit; Bogacz is a coauthor.
- `salvatori2023_brain_inspired_pc_survey` — Salvatori (this paper's last author) PC survey; the broader context.
- `song2020_pc_arbitrary_graphs` — Song et al.'s "PC on arbitrary graphs"; relevant for whether the depth pathology is graph-topology-specific.
- `tschantz2023_hybrid_pc_eqprop` — hybrid PC/Eqprop training; relevant to the nudging variants.
- `lillicrap_etal2020_backprop_brain_review` — backprop-and-the-brain review; situates PC among other bio-plausible candidates.
