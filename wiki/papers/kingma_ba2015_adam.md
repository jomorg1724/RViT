---
id: kingma_ba2015_adam
title: "Adam: A Method for Stochastic Optimization"
authors:
  - "Kingma, Diederik P."
  - "Ba, Jimmy"
year: 2015
venue: "ICLR"
doi: ""
arxiv: "1412.6980"
url: "https://arxiv.org/abs/1412.6980"
tags:
  - deep-learning
  - methodology
concepts: []
related:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - hochreiter_schmidhuber1997_lstm
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-13"
---

# Adam: A Method for Stochastic Optimization

## 1. Abstract

We introduce Adam, an algorithm for first-order gradient-based optimization of stochastic objective functions, based on adaptive estimates of lower-order moments. The method is straightforward to implement, is computationally efficient, has little memory requirements, is invariant to diagonal rescaling of the gradients, and is well suited for problems that are large in terms of data and/or parameters. The method is also appropriate for non-stationary objectives and problems with very noisy and/or sparse gradients. The hyper-parameters have intuitive interpretations and typically require little tuning. Some connections to related algorithms, on which Adam was inspired, are discussed. We also analyze the theoretical convergence properties of the algorithm and provide a regret bound on the convergence rate that is comparable to the best known results under the online convex optimization framework. Empirical results demonstrate that Adam works well in practice and compares favorably to other stochastic optimization methods.

## 2. Why this matters for us

Adam is the optimizer used to train the published Recurrent ViT (2502.10955), PRISM v1, and PRISM v2, and is the default optimizer across the user's GridCell-RNN / Feedback-Transformer / iterative-VAE experiments. This is a *foundational infrastructure* citation, not an architectural-inspiration one: the user's program presupposes that a per-parameter adaptive first-order method with bias-corrected moment estimates will train deep recurrent transformer stacks to convergence on noisy, sparse, and non-stationary gradient signals — exactly the regime in which Adam was designed to dominate. Every loss curve in the program is implicitly a curve produced by Adam with near-default $(\beta_1, \beta_2, \epsilon)$.

## 3. Key claims

1. Maintaining exponential moving averages of the gradient (first moment $m_t$) and the squared gradient (uncentered second moment $v_t$) yields a per-parameter step size that adapts to both gradient direction and gradient scale.
2. Initializing the moments at zero biases them toward zero in early iterations; analytic bias-correction $\hat m_t = m_t / (1-\beta_1^t)$, $\hat v_t = v_t / (1-\beta_2^t)$ removes this bias and is critical for early-stage stability.
3. The effective per-step magnitude is approximately bounded by the learning rate $\alpha$, $|\Delta\theta_t| \lesssim \alpha$, which gives Adam an automatic "trust region" property and makes the learning rate easier to set than for plain SGD.
4. Adam is invariant to diagonal rescaling of the gradient: scaling every coordinate of $g_t$ by a constant changes neither the update direction nor the effective step.
5. Under standard online-convex-optimization assumptions, Adam achieves an $O(\sqrt{T})$ regret bound comparable to the best known results.
6. The default hyperparameters $\alpha = 10^{-3}, \beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$ work across a wide range of architectures and datasets with minimal tuning.
7. AdaMax: a variant using the $\ell_\infty$-norm rather than the second moment yields a stable alternative for problems with extreme gradient outliers.

## 4. Methods

At each step $t$, given the stochastic gradient $g_t = \nabla_\theta f_t(\theta_{t-1})$:

$$
m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t, \qquad v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t \odot g_t
$$

Bias-correct:

$$
\hat m_t = \frac{m_t}{1-\beta_1^t}, \qquad \hat v_t = \frac{v_t}{1-\beta_2^t}
$$

Update:

$$
\theta_t = \theta_{t-1} - \alpha \cdot \frac{\hat m_t}{\sqrt{\hat v_t} + \epsilon}
$$

Defaults: $\alpha = 10^{-3}, \beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$. Memory cost is two $\mathbb{R}^d$ tensors per parameter tensor, doubling optimizer state versus plain SGD.

The bias-correction terms can be folded into the learning rate via the substitution $\alpha_t = \alpha \sqrt{1-\beta_2^t} / (1-\beta_1^t)$, which is the form most implementations use in the inner loop.

Adam is best understood as a synthesis of two ideas: momentum (the EMA of $g_t$, as in heavy-ball / Polyak momentum) and per-coordinate adaptive step sizes from the second moment (as in AdaGrad and RMSProp). Unlike AdaGrad's $\sum_\tau g_\tau^2$, the EMA in $v_t$ down-weights old gradients, which keeps the step from collapsing to zero on long training runs — the property that makes Adam appropriate for non-stationary objectives.

Theoretical analysis (Theorem 4.1) proves a regret bound $R(T) = O(\sqrt{T})$ for convex $f_t$ under boundedness assumptions on the gradient and the parameter trajectory.

## 5. Results

**MNIST logistic regression.** Adam matches or slightly exceeds SGD+Nesterov and AdaGrad on training-cost trajectory; AdaGrad slows once the effective step decays.

**MNIST multilayer NN (2-layer fully-connected, 1000 units, dropout).** Adam reaches a lower training cost than SGD+Nesterov, AdaGrad, RMSProp, and SGD-with-momentum within the same number of epochs; AdaGrad stalls earliest.

**CIFAR-10 ConvNet.** Adam converges substantially faster than SGD+Nesterov, AdaGrad, and RMSProp in the early epochs and reaches comparable or lower training loss at the end. Bias correction is shown to be critical: without it, Adam early-on resembles RMSProp without momentum and trains less stably.

**IMDB bag-of-words sentiment classification (sparse-gradient regime).** Adam outperforms AdaGrad and SGD+Nesterov, validating the claim that the EMA-based second moment handles non-stationary and sparse-gradient settings better than the cumulative-sum-based AdaGrad.

**Bias-correction ablation.** Comparing Adam to a version with $\beta_2$ set close to 1 and no bias correction shows that bias correction is what allows large $\beta_2$ to be safely used; without it, early-step magnitudes are too small and convergence is slow.

## 6. Critique / limitations

**Non-convergence on convex problems (Reddi et al. 2018, "On the Convergence of Adam and Beyond").** The original Theorem 4.1 has a flaw: the proof assumes a monotonicity property of $\hat v_t$ that does not hold in general for the EMA second moment. There exist simple stochastic convex problems on which Adam provably fails to converge to the minimum. AMSGrad (Reddi et al.) and its descendants fix this by taking $\max(\hat v_{t-1}, \hat v_t)$. In practice Adam still works on most deep-learning problems, but the original theoretical guarantee is now considered void.

**Generalization gap relative to SGD+Momentum.** Multiple follow-up studies (Wilson et al. 2017, "The Marginal Value of Adaptive Gradient Methods") report that for some computer-vision benchmarks (ImageNet ResNets), Adam-trained models have worse test accuracy than well-tuned SGD+Momentum even when training loss is comparable. The "flat minima vs sharp minima" interpretation is debated.

**Weight-decay coupling.** As pointed out by Loshchilov & Hutter (AdamW, 2017), implementing $L_2$ regularization as an addition to the gradient (the way it is done in nearly every deep-learning framework's Adam) is *not* equivalent to weight decay under an adaptive method, and the standard practice damages generalization. AdamW decouples weight decay from the adaptive step and is now the de-facto optimizer for transformer training, including ViT and the user's Recurrent ViT codebase.

**$\epsilon$ is load-bearing.** Although described as a "numerical stability" constant, the choice of $\epsilon$ materially changes optimization in late training when $\sqrt{\hat v_t}$ is small. ViT-scale models often use $\epsilon = 10^{-6}$ or larger, not the default $10^{-8}$.

**Memory cost.** Doubling optimizer state is a real cost at billion-parameter scale; 8-bit Adam (Dettmers et al. 2022) and shampoo / second-order alternatives have been motivated partly by this.

**Bias correction interaction with warmup.** Modern transformer training pipelines (Vaswani 2017 onward) layer Adam with linear or cosine learning-rate warmup. Adam's own implicit bias correction does not substitute for warmup; the two address different pathologies (initial moment underestimation vs initial gradient instability in deep stacks with high-variance attention layers).

## 7. Connection to our work

Adam is the optimizer that trains every model in the user's architectural program. The role is foundational rather than inspirational, but several specific design decisions in the program lean on Adam's particular properties:

**Recurrent ViT (2502.10955).** Training a transformer with recurrent feedback from $H^{(t-1)}$ produces a gradient signal whose magnitude varies dramatically across (a) attention parameters, (b) feedforward MLP parameters, (c) the LSTM-style gate parameters in the memory cell, and (d) the patch-embedding stem. Adam's per-parameter step size normalization is exactly what allows a single learning rate to train all four sub-systems simultaneously. The Recurrent ViT paper's training recipe uses Adam (or AdamW); without per-coordinate adaptation, the gate parameters and the attention parameters would need different learning rates.

**PRISM v1 / v2.** PRISM's prediction-error gating ($\mathcal{L}_\text{recon}$ + the inner variational-inference loop in `THESIS.md` §2.8) produces sparse, heavy-tailed gradient distributions when the predictor is well-trained and most patches are accurately predicted — exactly the IMDB-style sparse-gradient regime where Adam outperforms AdaGrad/SGD in §5. The EMA second moment $v_t$ keeps the per-coordinate step alive for rarely-updated parameters; AdaGrad would let them die.

**Iterative variational encoder–decoder.** The $n_{FR} \to n_{BR}$ rollout with KL regularization (`the_user_architectural_program.md` §4) produces a non-stationary loss surface: the KL term, the per-step MSE weights $\gamma_i = e^{i - n_{BR}}$, and the row-independence penalty all evolve as the model learns to use the guide. Adam's claim 3 (key claims, above) — appropriateness for non-stationary objectives — is the load-bearing property.

**Multi-hub multi-objective system.** The MSI / RL / VAE hubs each contribute a loss with potentially different gradient scales. The bias-correction step (claim 2) keeps the optimizer from undershooting in the first few hundred iterations after a new hub is added or unfrozen — important for staged-training protocols.

**Practical recommendation flowing back into the codebase.** Given the §6 critique, the program should standardize on **AdamW** (Loshchilov & Hutter 2017) rather than Adam-with-L2, especially for the ViT-scale Feedback Transformer stack. The user's existing checkpoints almost certainly already use AdamW under the PyTorch default; this paper is cited as the conceptual foundation, with the practical update being AdamW + linear warmup + cosine decay. None of this changes the architectural claims; it is a hyperparameter-engineering footnote.

The connection here is deliberately brief: Adam is plumbing. It enters the database because it is cited in `thesis_md`, because reviewers will expect to see it, and because the §6 critique (AMSGrad, AdamW, generalization gap) is the kind of optimizer-side context the user should keep in mind when comparing the Recurrent ViT / PRISM training curves against published baselines.

## 8. Citations to follow

- `duchi2011_adagrad` — AdaGrad, the cumulative-second-moment ancestor that Adam improves on for non-stationary objectives. Not in seed.
- `tieleman_hinton2012_rmsprop` — RMSProp lecture-note origin; closest direct ancestor (EMA second moment, no bias correction, no first moment). Not in seed.
- `reddi2018_amsgrad` — exposes the convergence flaw in Adam's Theorem 4.1 and proposes the $\max$-based fix. Important §6 reference. Not in seed.
- `loshchilov_hutter2017_adamw` — decoupled weight decay; the de-facto optimizer for ViT-scale transformer training in the user's codebase. Not in seed; should be added.
- `wilson2017_marginal_value_adaptive` — the generalization-gap critique of adaptive methods. Not in seed.
- `dettmers2022_8bit_adam` — 8-bit Adam, memory-cost mitigation at scale. Not in seed.
- `polyak1964_momentum` — heavy-ball momentum, one of Adam's two conceptual ancestors. Not in seed.
- `nesterov1983_accelerated_gradient` — Nesterov momentum, baseline in the §5 experiments. Not in seed.
- `sutskever2013_importance_of_initialization` — momentum + initialization scaling for deep nets; contemporary baseline. Not in seed.
