---
id: graves2016_act
title: "Adaptive Computation Time for Recurrent Neural Networks"
authors:
  - "Graves, Alex"
year: 2016
venue: "arXiv:1603.08983"
doi: ""
arxiv: "1603.08983"
url: "https://arxiv.org/abs/1603.08983"
tags:
  - recurrent-networks
  - deep-learning
  - methodology
concepts:
  - adaptive-computation-time
  - inner-inference-loop
  - lstm-cell
related:
  - hochreiter_schmidhuber1997_lstm
  - bai_kolter_koltun2019_deep_equilibrium_models
  - banino2021_pondernet
  - schmidhuber2015_learn_to_think
  - wang2025_hierarchical_reasoning_model
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-16"
---

# Adaptive Computation Time for Recurrent Neural Networks

## 1. Abstract

This paper introduces Adaptive Computation Time (ACT), an algorithm that allows recurrent neural networks to learn how many computational steps to take between receiving an input and emitting an output. ACT requires minimal architectural changes to a standard RNN, remains deterministic and differentiable, and does not add noise to the parameter gradients. The mechanism augments each RNN cell with a sigmoidal "halting unit" that emits, at each intra-step of pondering, a probability that the network should stop computing and output the current state. A user-tunable "ponder cost" is added to the training loss to penalize excessive computation. ACT is evaluated on four synthetic algorithmic tasks (parity of binary vectors, binary logic operations, integer addition, sort of real numbers) and on character-level language modeling on the Hutter Prize Wikipedia dataset. On the synthetic tasks ACT dramatically improves accuracy by adapting the number of internal steps to problem difficulty; on Wikipedia the perplexity gains are modest but ACT reveals interpretable allocation patterns — extra compute is spent at hard transitions such as spaces, end-of-sentence, and the boundaries of named entities.

## 2. Why this matters for us

ACT is the **prototypic formalization of learning per-input compute depth in a recurrent network**, and it is therefore the direct conceptual ancestor of the recurrent ViT's iterate count $n_{FR}$ (forward-reasoning passes over a static image) and $n_{BR}$ (backward-reasoning passes through the decoder). The user's program currently *fixes* $n_{FR}$ and $n_{BR}$ as hyperparameters; ACT supplies the explicit mathematical machinery (halting probability + cumulative-halting threshold + ponder-cost penalty) for learning these counts per-image, per-region, or per-hub. This is the mechanism PonderNet ([banino2021_pondernet]) later refined into a Bayesian halting distribution, and which HRM ([wang2025_hierarchical_reasoning_model]) replaced with a Q-learning halt head. ACT is the common ancestor of all three.

## 3. Key claims

1. RNNs can be augmented with a sigmoidal halting unit to learn variable per-input compute time, with no addition of noise to gradient estimates.
2. The halting mechanism is fully differentiable end-to-end: the output and updated state at each external time-step are convex combinations of the intra-step outputs and states, weighted by halting probabilities.
3. A *ponder cost* $\rho(t) = N(t) + R(t)$ — the number of ponder steps plus a fractional "remainder" — penalizes excessive computation when added to the task loss with weight $\tau$.
4. On algorithmic synthetic tasks (parity, logic, addition, sort) ACT substantially outperforms fixed-compute LSTM baselines and the learned step counts correlate with task difficulty.
5. On character-level language modeling, perplexity gains from ACT are modest, but the learned ponder budget is *interpretable*: extra steps cluster at high-entropy positions (word boundaries, sentence ends, named-entity boundaries).
6. The ponder-cost weight $\tau$ is the principal hyperparameter; it controls the speed/accuracy trade-off, and its choice depends only on the task, not the architecture.

## 4. Methods

**The halting unit.** At each external time-step $t$, the standard RNN update is iterated up to $M$ times. On the $n$-th intra-step, the cell produces a candidate state $s_n^t$ and output $y_n^t$ as usual, plus a scalar halting probability

$$
h_n^t = \sigma(W_h s_n^t + b_h) \in [0, 1].
$$

**Cumulative halting threshold.** Pondering continues until the cumulative halting probability $\sum_{n=1}^{N} h_n^t \geq 1 - \varepsilon$, where $\varepsilon$ is a small constant (e.g. $0.01$). Define $N(t)$ as the smallest $N$ satisfying this inequality, capped at $M$. The remainder is

$$
R(t) = 1 - \sum_{n=1}^{N(t) - 1} h_n^t,
$$

and the effective halting weights are $p_n^t = h_n^t$ for $n < N(t)$ and $p_{N(t)}^t = R(t)$ (so that $\sum_n p_n^t = 1$).

**Final output and state.** The state passed to the next external time-step and the output emitted at time $t$ are mean-field averages of the intra-step values weighted by the halting probabilities:

$$
s_t = \sum_{n=1}^{N(t)} p_n^t \, s_n^t, \qquad y_t = \sum_{n=1}^{N(t)} p_n^t \, y_n^t.
$$

This is the load-bearing trick: because $s_t$ and $y_t$ are smooth functions of $\{h_n^t\}$, gradients flow through the halting mechanism without resort to REINFORCE or other stochastic estimators.

**Ponder cost.** Define the per-step ponder cost

$$
\rho(t) = N(t) + R(t),
$$

i.e. the (real-valued) total time the network spent at step $t$. The training objective is

$$
\mathcal{L} = \mathcal{L}_\text{seq} + \tau \sum_t \rho(t),
$$

where $\mathcal{L}_\text{seq}$ is the task loss (cross-entropy, MSE, etc.) and $\tau$ is the ponder-cost weight. The gradient of $\rho(t)$ with respect to the halting unit parameters provides the pressure to reduce pondering when possible.

**Maximum ponder steps.** The author imposes a hard cap $M$ (typically 20 or 100). Empirically the network rarely uses the full budget; the cap exists as a safety bound during training.

**Architecture.** ACT is applied to a standard one-layer LSTM. The only architectural addition is a single linear projection $W_h, b_h$ from the cell state to the halting scalar — i.e. a few hundred extra parameters per layer.

## 5. Results

**Parity.** A standard LSTM cannot learn parity of 64-bit binary vectors (accuracy near chance). An ACT-LSTM with $\tau = 10^{-3}$ achieves >99% accuracy by learning to take more ponder steps when more bits are set to 1. Learned $\rho(t)$ scales roughly linearly with bit-count.

**Logic.** Composing $k$ binary boolean operations: ACT learns to allocate compute proportional to $k$, achieving near-perfect accuracy where the fixed-compute baseline fails for $k > 5$.

**Addition.** Adding two $n$-digit integers: ACT allocates roughly $n$ ponder steps and achieves >99% per-digit accuracy. Fixed-compute baselines fail to generalize beyond their training depth.

**Sort.** Sorting sequences of real numbers: ACT achieves comparable accuracy to fixed-depth baselines but with much less average compute per element.

**Hutter Prize Wikipedia (character-level LM).** ACT yields modest BPC (bits-per-character) improvements (~1.39 → ~1.36 BPC range for the best configurations vs. matched LSTM baseline), but the more striking result is the *interpretability* of the ponder map: extra ponder steps cluster at spaces (predicting word identity), sentence boundaries (predicting topic shifts), and the first character of capitalized words / named entities.

**Sensitivity to $\tau$.** The ponder weight $\tau$ trades off task accuracy against compute. There is a broad regime of $\tau$ values that work well; performance degrades gracefully outside this range. The author reports that tuning $\tau$ over 1–2 orders of magnitude is sufficient in practice.

## 6. Critique / limitations

The ponder cost $\rho(t) = N(t) + R(t)$ is a heuristic, not a Bayesian objective. The remainder $R(t)$ is added to make $\rho(t)$ differentiable in the halting parameters, but it has no principled probabilistic interpretation — $\rho(t)$ is neither an expected compute time under a halting distribution nor a tight upper bound on one. PonderNet ([banino2021_pondernet]) directly attacks this point: it reinterprets $\{h_n^t\}$ as a proper categorical / geometric distribution over halt steps and replaces the ad-hoc ponder cost with a KL term against a geometric prior.

The mean-field averaging $s_t = \sum_n p_n^t s_n^t$ is not what a "real" variable-depth network does — a real variable-depth net halts at one specific step and outputs the state at that step. Graves's mean-field averaging is the differentiable surrogate; whether it converges to the same solution as the discrete halting it approximates is unclear and not addressed empirically.

The ponder budget is allocated *per external time-step*, not per token group or per region. For vision applications (which this paper does not address), one would want per-patch or per-region budgets — extending ACT to spatially varying compute is non-trivial.

The maximum ponder count $M$ is a hyperparameter; if $M$ is too small the network is starved of compute on hard inputs, if too large training becomes expensive. The paper offers no principled way to choose $M$.

The language-modeling gains are modest. The author argues this is because character-level prediction is relatively uniform in difficulty across positions, but the result also suggests that ACT's benefits may be concentrated on tasks with sharply input-dependent difficulty (algorithmic tasks) rather than smoothly varying ones (natural language). For our vision use case — where image difficulty *does* vary sharply per-image — this critique is encouraging rather than damning.

The paper trains on synthetic algorithmic tasks where ground-truth difficulty is known. Whether ACT learns the right allocation under real-world supervision (when difficulty is implicit in the training signal) is only weakly tested by the Wikipedia experiment.

## 7. Connection to our work

Graves 2016 is the **mathematical scaffolding for variable-depth recurrence**, which is exactly the missing ingredient in the user's iterative variational encoder–decoder ([iterative-variational-encoder-decoder]). Several specific points of contact:

**ACT is the prototype of $n_{FR}$ and $n_{BR}$.** The user's iterative-VAE construction (`the_user_architectural_program.md` §4) runs the encoder for $n_{FR}$ forward-reasoning steps on the same image, then runs the decoder for $n_{BR}$ backward-reasoning steps. Both counts are currently fixed hyperparameters. Graves's ACT supplies the precise mechanism for *learning* $n_{FR}$ and $n_{BR}$ per-image: replace the fixed loop bound with a cumulative-halting threshold over a per-pass halting scalar $h_n = \sigma(W_h H_n)$, average the outputs by halting probabilities, and add $\tau \rho$ to the loss. This is a near-mechanical port from the LSTM case to the recurrent-ViT case. The published recurrent ViT (2502.10955) and PRISM v1/v2 effectively *fixed* the iterate count; ACT is the path to *learning* it.

**Per-region or per-patch halting.** A more ambitious extension uses the user's grid-cell structure ([gridcell-rnn]): each grid cell gets its own halting unit, so different patches can ponder for different lengths. This would let the network spend more compute on visually difficult regions (occluded, textured, ambiguous) and less on easy ones (sky, flat backgrounds). The mean-field averaging extends naturally per-cell; the only architectural cost is one extra scalar per grid cell.

**Per-hub halting in the multi-hub system.** In the user's MSI / RL / VAE multi-hub architecture ([multi-hub-multi-objective-system]), each hub could halt independently — the RL hub might converge quickly on familiar states while the VAE hub keeps refining its reconstruction. ACT supplies the per-stream halting mechanism without requiring inter-hub synchronization.

**Relation to DEQ and HRM.** ACT and DEQ ([bai_kolter_koltun2019_deep_equilibrium_models]) are two answers to the same question — "how should a recurrent network decide when it has computed enough?" — pointing in opposite directions. DEQ runs the recurrence to convergence at a fixed point and trains via implicit differentiation; the "depth" is determined by the convergence rate of $f$. ACT learns an *explicit* halting policy that may halt long before fixed-point convergence (or run past it). HRM ([wang2025_hierarchical_reasoning_model]) blends both: it uses DEQ-style one-step implicit gradient for the inner module, and a Q-learning halt head (an RL variant of ACT's halting unit) for the outer module. For the user's program, ACT is the simpler, faster-to-adopt option; DEQ is the principled limit; HRM is the most empirically validated hybrid.

**Connection to PonderNet's Bayesian halting.** ACT's $\{h_n^t\}$ are not a probability distribution; PonderNet ([banino2021_pondernet]) reinterprets them as a categorical/geometric halting distribution and replaces the ad-hoc ponder cost with a KL term against a geometric prior. For the user's variational framework — where KL terms against priors are already the central regularizer — PonderNet's formulation will likely be a cleaner fit than ACT's raw ponder cost. The connection between the iterative-VAE KL ($D_{KL}[q_\theta(\tilde H_0 \mid H_{n_{FR}}) \| p(\tilde H_0)]$) and a PonderNet-style KL over the halting distribution is worth working out explicitly.

**LSTM dependency.** ACT is built on top of LSTM ([hochreiter_schmidhuber1997_lstm]); the user's program is built on top of LSTM-style gating in the GridCell RNN. ACT therefore composes naturally with the existing recurrent primitive without requiring a different cell type. The single architectural addition is the halting linear projection $W_h$.

**Schmidhuber's "Learn to Think" connection.** Schmidhuber's 2015 coupled-RNN proposal (`schmidhuber2015_learn_to_think`) anticipates many of the same themes — a controller that learns to *inspect* a predictive world model and decide how long to interrogate it. ACT formalizes the "how long" question concretely; Schmidhuber's framing motivates *why* learning that is valuable in the first place. The user's multi-hub program is the synthesis: many hubs, each with its own ACT-style budget, all feeding a central self-attention substrate.

## 8. Citations to follow

- `banino2021_pondernet` — PonderNet, the direct Bayesian successor to ACT. Already in seed.
- `schmidhuber2015_learn_to_think` — Schmidhuber's coupled-RNN framework that anticipates variable-compute controllers. Already in seed.
- `bai_kolter_koltun2019_deep_equilibrium_models` — DEQ, the fixed-point alternative to ACT. In seed, full depth.
- `hochreiter_schmidhuber1997_lstm` — the LSTM cell ACT builds on. In seed.
- `graves2014_neural_turing_machines` — Graves's earlier external-memory model; same author, same year-region, same motivation (programs over data). Not in seed; add.
- `figurnov2017_spatially_adaptive_computation` — extends ACT to per-region budgets in convolutional residual networks; directly relevant to per-patch halting in the recurrent ViT. Not in seed; add.
- `eyzaguirre2020_dact_bert` — applies ACT-style halting to transformers; the closest published analog to ACT-for-ViT. Not in seed; add.
- `dehghani2018_universal_transformer` — universal transformer with ACT-style dynamic halting at the token level. Not in seed; add as a high-priority extension paper.
