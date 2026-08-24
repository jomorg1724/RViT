---
id: banino2021_pondernet
title: "PonderNet: Learning to Ponder"
authors:
  - "Banino, Andrea"
  - "Balaguer, Jan"
  - "Blundell, Charles"
year: 2021
venue: "ICML Workshop (AutoML)"
doi: ""
arxiv: "2107.05407"
url: "https://arxiv.org/abs/2107.05407"
tags:
  - deep-learning
  - recurrent-networks
  - theoretical-essay
concepts:
  - adaptive-computation-time
  - recurrence-for-temporal-dynamics
  - slow-fast-recurrence
  - inner-inference-loop
related:
  - graves2016_act
  - bai_kolter_koltun2019_deep_equilibrium_models
  - wang2025_hierarchical_reasoning_model
  - schmidhuber2015_learn_to_think
  - hochreiter_schmidhuber1997_lstm
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-15"
---

# PonderNet: Learning to Ponder

## 1. Abstract

PonderNet is an algorithm that enables a neural network to learn end-to-end *how many computational steps* to apply to a given input, by re-casting Graves's (2016) Adaptive Computation Time as a probabilistic halting process. At each step $n$ a step function $s(\cdot)$ produces a prediction $\hat y_n$, an updated hidden state $h_{n+1}$, and a scalar *halting probability* $\lambda_n \in [0,1]$ — the conditional probability of halting *now* given that the network has not halted before. The halting distribution is therefore the generalized-geometric $p_n = \lambda_n \prod_{j<n}(1 - \lambda_j)$. The training loss is the expected per-step prediction loss under this distribution plus a KL regularizer toward a geometric prior with hyperparameter $\lambda_p$. The result is a principled, unbiased-gradient adaptive-computation procedure that (i) dramatically outperforms ACT on synthetic extrapolation tasks (parity), (ii) matches state of the art on bAbI question answering with roughly 6× less computation than Universal Transformer, and (iii) achieves a new state of the art (97.86% on A–C indirect inference) on the paired associative inference benchmark.

## 2. Why this matters for us

PonderNet is the *direct architectural ancestor* of the iterate-count $n_{FR}$ that controls forward-reasoning in the user's recurrent ViT and in the iterative variational encoder–decoder of the architectural program. The Recurrent ViT and PRISM both run a *fixed* number of recurrent passes over the input; PonderNet provides a principled framework for letting the network *learn* how many passes to take, where "principled" means: (a) the halting head is a normal neural-network sigmoid producing $\lambda_n$, (b) the loss is a per-step likelihood weighted by the halting probability, (c) computational cost is controlled by a single intuitive hyperparameter $\lambda_p$ (the prior expected halt rate), and (d) gradients are unbiased. For PRISM v2 in particular — where the rationale for any specific $n_{FR}$ is currently hand-tuned — PonderNet offers a concrete drop-in replacement: train a per-task or per-image $\lambda_n$ head on top of the existing recurrent backbone, regularize toward a moderate $\lambda_p$, and let the network discover when the guide $H_n$ has converged enough.

## 3. Key claims

1. Adaptive computation can be formulated as a *Bayesian halting process*: the network outputs $\lambda_n$ at each step, and the halting time $N$ is distributed as $p_n = \lambda_n \prod_{j=1}^{n-1}(1-\lambda_j)$.
2. The training objective is $\mathcal{L} = \mathbb{E}_{n \sim p}\big[\mathcal{L}_{\text{rec}}(y, \hat y_n)\big] + \beta\, D_\text{KL}\big[p_n \,\Vert\, p_G(\lambda_p)\big]$, where $p_G(\lambda_p)$ is a geometric distribution with rate $\lambda_p$. The reconstruction term is *maximum-likelihood per step*, weighted by the halting probability, rather than ACT's ponder-cost penalty on the *expected step count*.
3. The KL term plays two roles: it regularizes the expected number of steps toward $1/\lambda_p$, and — because the prior assigns nonzero mass to every step — it incentivizes the network to *also* produce competent predictions at every $n$, not just the halting step. This yields cleaner gradients than ACT's terminal-step ponder penalty.
4. Gradients of the loss with respect to the network's parameters are unbiased: the per-step loss can be computed exactly because the halting distribution is over a discrete random variable with closed-form weights $p_n$. ACT's gradients, by contrast, are biased because the ponder cost backpropagates only through the final unrolled step.
5. The hyperparameter $\lambda_p$ has a clear interpretation: the expected number of ponder steps under the prior is $1/\lambda_p$. ACT's $\tau$ (the ponder-cost weight) has no comparable closed-form meaning and is notoriously unstable to tune.
6. **Extrapolation.** On the synthetic *parity* task — predicting the parity of a binary vector with variable numbers of nonzero entries — PonderNet generalizes from training inputs of one length to test inputs $3.2\times$ longer, while ACT remains near chance.
7. **Generalization to language.** On bAbI question answering, PonderNet matches state of the art using ~1,658 total ponder steps across a benchmark where Universal Transformer uses ~10,161.
8. **Reasoning benchmark.** On paired associative inference, PonderNet reaches 97.86% on the A–C indirect inference subtask, vs Universal Transformer's 85.60% and matching the specialized MEMO baseline.

## 4. Methods

**Step function.** A weight-tied recurrent block $s$ that maps the input $x$ and previous hidden state $h_n$ to a triple
$$
(\hat y_n,\; h_{n+1},\; \lambda_n) = s(x,\, h_n),
$$
where $\hat y_n$ is the per-step prediction, $h_{n+1}$ the updated state, and $\lambda_n \in [0,1]$ a scalar halting probability (sigmoid head on a linear map of $h_{n+1}$). The architecture of $s$ is arbitrary — the paper experiments with MLP, GRU, LSTM, and Universal-Transformer step functions.

**Halting process.** The halting random variable $N$ takes value $n$ with probability $p_n = \lambda_n \prod_{j<n}(1-\lambda_j)$, the generalized geometric distribution induced by the (input-dependent, time-varying) Bernoulli sequence $\{\lambda_j\}$. At inference time, the network samples $N$ once and emits $\hat y_N$; in practice a maximum step budget $N_{\max}$ is imposed and probability mass beyond it is assigned to step $N_{\max}$.

**Loss.** Two additive terms:
$$
\mathcal{L} \;=\; \underbrace{\sum_{n=1}^{N_{\max}} p_n \,\mathcal{L}_{\text{rec}}(y, \hat y_n)}_{\text{expected per-step loss}}
\;+\;
\beta \, \underbrace{D_\text{KL}\!\left[\, p_n(\lambda_1,\ldots,\lambda_{N_{\max}}) \;\Vert\; p_G(n;\lambda_p) \,\right]}_{\text{halting-distribution regularizer}}.
$$
The reconstruction term is a *maximum-likelihood* objective weighted by halting mass — every step is supervised, with weight equal to that step's halting probability. The KL term penalizes deviation of the empirical halting distribution from a geometric prior $p_G(n;\lambda_p) = \lambda_p(1-\lambda_p)^{n-1}$, where $\lambda_p$ is a single scalar hyperparameter.

**Gradients.** The reconstruction term is a closed-form sum over $N_{\max}$ terms; gradients pass cleanly through both $\hat y_n$ and (via $p_n$) through every preceding $\lambda_j$. No surrogate or REINFORCE estimator is needed. This is the central technical advantage over ACT.

**Architectures and tasks.**
- *Parity task:* a GRU step function over a one-hot input encoding; training on sequences with up to $k$ nonzero entries, test on sequences with $\sim 3k$ nonzero entries.
- *bAbI:* Universal-Transformer–style transformer block as $s$.
- *Paired associative inference:* the same transformer block, swapped in for the Universal Transformer baseline.

## 5. Results

**Parity task.** On the standard 64-bit parity extrapolation benchmark, PonderNet achieves near-perfect accuracy at sequences $3.2\times$ longer than the training distribution, while ACT collapses to near-chance. The number of ponder steps grows roughly linearly with sequence length — i.e., the model learns to allocate more compute when the input is harder.

**bAbI 10k.** PonderNet matches state of the art on all 20 tasks. Mean error 0.15 ± 0.9, versus Universal Transformer's 0.29 ± 1.4. Total ponder steps across the benchmark: ~1,658 vs ~10,161 for Universal Transformer — a roughly 6× reduction in compute at equal-or-better accuracy.

**Paired Associative Inference.** A–C indirect inference accuracy: PonderNet 97.86%, Universal Transformer 85.60%, MEMO (a specialized memory model) tied with PonderNet. PonderNet thus matches a memory-augmented architecture using only a vanilla transformer step function, suggesting the gains come from adaptive depth rather than a richer memory primitive.

**Sensitivity to $\lambda_p$.** The paper reports stable training over a range of $\lambda_p \in [0.05, 0.5]$, with the *learned* mean halting step tracking $1/\lambda_p$ up to task-dependent shifts. This stands in contrast to ACT, where small changes in the ponder-cost weight $\tau$ can swing the learned step count by an order of magnitude.

**Step-count adaptivity vs. input difficulty.** A qualitative finding reported in the paper: on the parity task, the learned mean number of ponder steps grows with the number of nonzero entries in the input. The model genuinely allocates more compute to harder inputs, rather than just learning a fixed average step count. This is the property that distinguishes PonderNet from any architecture with a fixed-but-tunable depth.

## 6. Critique / limitations

The paper is an ICML workshop submission rather than a full conference paper, and the experimental scope reflects that: three tasks, modest scale, no images, no continuous-output tasks, no on-policy RL setting. The halting head $\lambda_n$ is a single scalar per step, with no per-token / per-position granularity — a notable gap given that vision-transformer applications would benefit from *per-patch* adaptive depth (the network might want to ponder more on cluttered patches than on background patches).

The KL regularizer assumes a geometric prior, which is the maximum-entropy distribution on $\mathbb{N}$ given a fixed mean. This is a defensible default but is not necessarily the right prior for tasks where the optimal step count is bimodal (easy vs. hard inputs) or heavy-tailed. The paper doesn't experiment with alternative priors.

The unbiased-gradient argument is correct but conditional on the maximum step budget $N_{\max}$. Probability mass beyond $N_{\max}$ is collapsed onto step $N_{\max}$, which biases gradients in a way that becomes severe if $\lambda_p$ is small and $N_{\max}$ is short. The interaction between $\lambda_p$ and $N_{\max}$ is not characterized.

The training procedure runs all $N_{\max}$ steps every iteration (to compute the per-step weights $p_n$), so PonderNet does *not* save training-time compute — only inference-time compute. The savings are realized only at deployment, where the network can halt early.

Finally, the paper does not test whether the *learned* halting distribution is interpretable: does the model halt early on "easy" inputs and ponder on "hard" ones in a way a human would endorse? The qualitative results are suggestive but not systematic.

## 7. Connection to our work

PonderNet is the direct architectural ancestor of the *iterate-count* $n_{FR}$ that controls forward-reasoning depth in the user's recurrent ViT (2502.10955) and in the iterative variational encoder–decoder of the architectural program ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §4). At present, $n_{FR}$ is a *fixed* hyperparameter chosen by the experimenter. PonderNet supplies the missing principled framework for letting the network *learn* $n_{FR}$ per-input.

**The Bayesian halting distribution as a principled iterate-count framework.** The user's program currently treats $n_{FR}$ and $n_{BR}$ (the backward-reasoning step count) as architectural hyperparameters. PonderNet's $p_n = \lambda_n \prod_{j<n}(1-\lambda_j)$ is a drop-in replacement: add a halting head $\lambda_n$ on top of the encoder's guide $H_n$, weight the per-step KL/reconstruction losses by $p_n$, regularize the halting distribution toward a geometric prior, and the network learns when the guide has converged. This is a concrete architectural extension that should be implementable as a small modification to the existing Recurrent ViT or PRISM training loop.

**Lineage: ACT → PonderNet → HRM's halting head.** This paper sits squarely on the variable-compute lineage that runs from [graves2016_act](research_db/papers/graves2016_act.md) (the predecessor, which introduced the *idea* of learned step counts but with biased gradients and an unintuitive ponder cost), through PonderNet (which fixes the gradient and hyperparameter issues), to [wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md) (which uses a Q-learning-based halting head on top of HRM's hierarchical-convergence inner loop). HRM cites PonderNet as the design ancestor of its halting mechanism. The user's program inherits the adaptive-computation commitment via HRM and via [bai_kolter_koltun2019_deep_equilibrium_models](research_db/papers/bai_kolter_koltun2019_deep_equilibrium_models.md), which provides the orthogonal *training* framework (implicit gradients at the converged fixed point) for the same variable-compute regime.

**Per-task PonderNet-trained PRISM iterate count — a concrete architectural extension.** The most actionable proposal: at the top of the PRISM v2 encoder stack, add a per-step halting head $\lambda_n$ that reads from the slow memory $M_t^{(\text{slow})}$. Train with a geometric prior $\lambda_p \approx 0.2$ (matching the current default $n_{FR} = 5$). The expected outcome is that PRISM learns to ponder more on harder change-detection inputs (cluttered scenes, ambiguous targets) and less on easy ones, recovering the inference-time efficiency that the Recurrent ViT currently leaves on the table. The KL-to-prior structure also provides a principled way to *anneal* $\lambda_p$ during training: start with a higher prior ($\lambda_p = 0.5$, expected 2 steps) for cheap warmup, lower it ($\lambda_p = 0.1$, expected 10 steps) for fine-tuning on hard examples.

**Connection to [schmidhuber2015_learn_to_think](research_db/papers/schmidhuber2015_learn_to_think.md).** Schmidhuber's coupled-controller / world-model framework is a *generalization* of the adaptive-computation idea: the controller learns not just *how long* to ponder but *what computation* to perform on the world model. PonderNet can be viewed as a scalar projection of that more ambitious program onto a single dimension (depth). The user's multi-hub architecture is closer to Schmidhuber's full program; PonderNet is the natural starting point for adding adaptive depth to it.

**Relation to DEQ.** DEQ ([bai_kolter_koltun2019_deep_equilibrium_models](research_db/papers/bai_kolter_koltun2019_deep_equilibrium_models.md)) and PonderNet attack the *same* problem — variable, possibly-unbounded recurrent depth — but from orthogonal angles. DEQ finds a fixed point and trains by implicit differentiation at that point; PonderNet keeps explicit unrolling but learns when to stop. They are composable: a DEQ-style step function could itself be wrapped in a PonderNet halting head, giving "stop iterating once the implicit gradient says the residual is small enough." This is one direction the architectural program could grow.

**Limitation for our use case.** PonderNet's halting head is a *single scalar* per step. For a vision-transformer encoder operating over a 2D grid of patches, the natural extension is a *per-patch* halting head — let some patches halt early while others continue pondering. This would couple naturally with the Feedback Transformer primitive (the halting probability could itself be one of the feedback signals integrated into Q/K/V projections), but the per-patch extension is not in the original PonderNet paper and would require new work.

**Relation to LSTM-based memory.** PonderNet's step function is generic and is demonstrated with both [hochreiter_schmidhuber1997_lstm](research_db/papers/hochreiter_schmidhuber1997_lstm.md)-style cells and transformer blocks. For the user's GridCell RNN primitive — itself an LSTM-derivative gated unit with Feedback Transformer integration — this means PonderNet can be applied at the granularity of the GridCell RNN as the recurrent block, with $\lambda_n$ reading from the integrated GridCell state. The KL regularizer's principled-prior structure is especially attractive in the multi-compartmental memory setting: different layers in the hierarchical memory stack could carry *different* $\lambda_p$ values, capturing the intuition that deeper / slower layers should ponder longer than shallow / faster ones. This is the natural PonderNet analog of the slow-fast-recurrence commitment.

**What PonderNet does *not* supply.** PonderNet learns *when* to stop but not *what* the iteration should compute. It does not address the question of whether the recurrent dynamics converge to a meaningful fixed point (DEQ's territory), nor whether iteration count *generalizes* the way the architectural program needs (HRM's hierarchical-convergence argument). PonderNet is therefore a complement to, not a replacement for, the DEQ/HRM lineage. The combination — a DEQ-style step function inside a PonderNet halting wrapper inside the HRM hierarchical-convergence structure — would be the maximally principled instantiation of variable-compute recurrence for the user's program.

## 8. Citations to follow

- `graves2016_act` — the immediate predecessor that introduced learned step counts; PonderNet's central contribution is fixing ACT's biased gradients and unintuitive hyperparameter. In seed, stub; should be deepened in tandem with this entry.
- `dehghani2018_universal_transformer` — the Universal Transformer baseline that PonderNet outperforms with 6× less compute on bAbI. Not in seed; worth adding as it's another adaptive-computation architecture and the natural baseline for any PonderNet-on-vision extension.
- `banino2020_memo` — the paired-associative-inference baseline (MEMO) that PonderNet ties on the A–C task. Not in seed; relevant to memory-augmented reasoning.
- `bolukbasi2017_adaptive_neural_networks` — earlier work on adaptive computation in feedforward networks (early-exit classifiers). Not in seed; useful for the broader adaptive-computation literature.
- `figurnov2017_spatially_adaptive_computation` — spatially adaptive computation in ConvNets, the closest precursor to the *per-patch* extension of PonderNet that our program would need. Not in seed; high-value addition.
- `chung2017_hierarchical_multiscale_rnn` — hierarchical multi-scale RNN with learned boundary detectors, structurally similar to PonderNet's halting mechanism. Not in seed.
