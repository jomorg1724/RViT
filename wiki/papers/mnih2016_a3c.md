---
id: mnih2016_a3c
title: "Asynchronous Methods for Deep Reinforcement Learning"
authors:
  - "Mnih, Volodymyr"
  - "Badia, Adrià Puigdomènech"
  - "Mirza, Mehdi"
  - "Graves, Alex"
  - "Lillicrap, Timothy P."
  - "Harley, Tim"
  - "Silver, David"
  - "Kavukcuoglu, Koray"
year: 2016
venue: "ICML 2016"
doi: ""
arxiv: "1602.01783"
url: "https://arxiv.org/abs/1602.01783"
tags:
  - reinforcement-learning
  - deep-learning
  - recurrent-networks
concepts:
  - actor-critic
  - reinforce
related:
  - schulman2016_gae
  - schulman2017_ppo
  - pleines2022_recurrent_ppo
  - sutton_barto2018_rl_intro
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - botvinick2020_deep_rl_neuro
  - glimcher2011_dopamine_rpe
  - mnih2014_recurrent_attention
  - hochreiter_schmidhuber1997_lstm
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Asynchronous Methods for Deep Reinforcement Learning

## 1. Abstract

We propose a conceptually simple and lightweight framework for deep reinforcement learning that uses asynchronous gradient descent for optimization of deep neural network controllers. We present asynchronous variants of four standard reinforcement learning algorithms and show that parallel actor-learners have a stabilizing effect on training allowing all four methods to successfully train neural network controllers. The best performing method, an asynchronous variant of actor-critic, surpasses the current state-of-the-art on the Atari domain while training for half the time on a single multi-core CPU instead of a GPU. Furthermore, we show that asynchronous actor-critic succeeds on a wide variety of continuous motor control problems as well as on a new task of navigating random 3D mazes using a visual input.

## 2. Why this matters for us

A3C is the canonical *asynchronous actor-critic* recipe and the conceptual ancestor of every modern parallel-rollout policy-gradient algorithm — including the PPO+GAE pipeline (`schulman2017_ppo`, `schulman2016_gae`) used by the published Recurrent ViT (2502.10955), PRISM v1, PRISM v2, and the user's broader multi-hub RL hub. Two architectural commitments transfer directly to our work. First, the actor-critic decomposition — a policy head $\pi_\theta(a \mid s)$ and a value head $V_\phi(s)$ sharing a common feature trunk — is the structural template for the recurrent ViT's actor and value heads sharing the recurrent memory state. Second, the asynchronous-parallel rollout pattern — many independent actor-learners exploring different parts of state space concurrently and pushing updates to a shared parameter server — is conceptually aligned with the multi-hub competition architecture in which parallel hubs each maintain their own memory states and contribute concurrently to a shared self-attention substrate. The paper also introduces the LSTM-A3C variant, the first widely-used recurrent policy network and the direct ancestor of recurrent PPO (`pleines2022_recurrent_ppo`).

## 3. Key claims

1. Asynchronous gradient descent across many parallel actor-learners stabilizes deep RL *without* an experience-replay buffer, because the diversity of concurrent exploration trajectories decorrelates updates in the same way replay does for off-policy methods.
2. The four standard one-machine RL algorithms — 1-step Q-learning, 1-step Sarsa, $n$-step Q-learning, and advantage actor-critic — each admit a stable asynchronous parallel-actor variant under this framework.
3. The asynchronous advantage actor-critic (A3C) variant is the best of the four; it surpasses the prior Atari SOTA (Dueling DQN, Prioritized DQN, Gorila) while training on a 16-core CPU in roughly half the wall-clock time of the GPU baselines.
4. A3C extends naturally beyond discrete-action Atari to continuous-control MuJoCo tasks (via a Gaussian policy head) and to first-person 3D navigation (Labyrinth) with an LSTM-augmented policy network, demonstrating the same algorithmic recipe across action spaces and observation modalities.
5. Adding an entropy bonus $\beta H(\pi_\theta(\cdot \mid s_t))$ to the policy loss discourages premature convergence to deterministic policies and was empirically necessary for stable Atari training.
6. The asynchronous setup obviates the need for specialized RL hardware: the entire system runs on commodity multi-core CPUs without GPU acceleration, dramatically lowering the barrier to scaled experimentation.
7. The Hogwild-style lock-free asynchronous parameter updates do not destabilize learning in practice, even though the theoretical guarantees of standard SGD no longer hold.

## 4. Methods

**Setting.** Standard discounted MDP with policy $\pi_\theta(a \mid s)$ and value baseline $V_\phi(s)$, both sharing a CNN trunk (and an LSTM cell on top, for the recurrent variant). The framework runs $N$ asynchronous actor-learner threads (typically $N = 16$ on a 16-core CPU), each with its own environment instance and its own thread-local copy of the parameters.

**Forward / rollout per thread.** Each thread rolls out $t_\max$ steps (typically $t_\max = 5$ for Atari, $20$ for LSTM-A3C) of on-policy experience from its own environment, accumulating $(s_t, a_t, r_t)$. At the end of the segment, it bootstraps with the value head: $R = V_\phi(s_{t_\max})$ if the segment did not terminate, $R = 0$ otherwise.

**$n$-step advantage estimator.** Walking backward through the segment, the thread computes the discounted return and the advantage:
$$
R \leftarrow r_t + \gamma R, \quad \hat A_t = R - V_\phi(s_t).
$$
This is the $n$-step advantage estimator — a special case of GAE with $\lambda = 1$ truncated at $t_\max$, equivalent to mixing one-step TD bootstraps with the empirical Monte-Carlo return inside the segment.

**Actor-critic loss.** Per segment, each thread accumulates gradients of
$$
\mathcal{L} = -\sum_t \log \pi_\theta(a_t \mid s_t)\, \hat A_t \;-\; \beta \sum_t H(\pi_\theta(\cdot \mid s_t)) \;+\; \frac{1}{2}\sum_t (R_t - V_\phi(s_t))^2
$$
where $H(\pi) = -\sum_a \pi(a) \log \pi(a)$ is the policy entropy and $\beta = 0.01$ is the entropy-bonus coefficient. The critic loss is a half-MSE between the segment return $R_t$ and the value head's prediction.

**Asynchronous Hogwild updates.** After accumulating per-segment gradients, each thread pushes them directly to the shared parameter server using shared-memory RMSProp (lock-free; "Hogwild!"-style). The thread then pulls the latest parameters and rolls out the next segment. There is no synchronization barrier; threads run independently, and the stale-gradient overlap is small because rollouts are short ($t_\max$ steps).

**Architectures.** Atari: a 16x16 / 32x32 conv-stack feeding a 256-unit FC layer, then split into a softmax policy head and a scalar value head. LSTM-A3C: identical CNN trunk, followed by a 256-unit LSTM cell, then the same split heads. MuJoCo: a small MLP with a Gaussian policy (state-dependent mean, state-independent log-stddev). Labyrinth (3D maze): CNN + LSTM + policy/value heads.

**Four async variants.** Beyond A3C the paper benchmarks: (i) async 1-step Q-learning with target network; (ii) async 1-step Sarsa; (iii) async $n$-step Q-learning. All four variants share the asynchronous-actor-learner framework; only the gradient computation per segment differs.

**Hyperparameters.** $\gamma = 0.99$. RMSProp with shared statistics. Learning rate sampled log-uniformly from $[10^{-4}, 10^{-2}]$. Entropy coefficient $\beta = 0.01$. Reward clipping to $[-1, +1]$ on Atari.

## 5. Results

**Atari (57 games).** A3C with $N = 16$ CPU threads achieves a *mean human-normalized score* of $\approx 853\%$ across 57 games after 4 days of training (LSTM-A3C variant), surpassing all prior published baselines including DQN, Double DQN, Dueling DQN, Prioritized DQN, and Gorila DQN. Median human-normalized score reaches $\approx 117\%$, the first method to clear the 100% median bar. The feedforward A3C reaches comparable performance in roughly half the wall-clock time of the GPU-based DQN family on a single 16-core CPU.

**Wall-clock efficiency.** A3C reaches DQN's final Atari score in approximately *1 day* of 16-core CPU training versus DQN's 8-10 days on a single GPU — roughly an order of magnitude speedup in wall-clock terms per game, and orders of magnitude cheaper in hardware.

**Async variant comparison.** A3C outperforms async $n$-step Q-learning, which outperforms async 1-step Q-learning, which outperforms async 1-step Sarsa, on average across the Atari suite. The actor-critic advantage estimator and entropy bonus together account for the gap.

**MuJoCo continuous control.** A3C with a Gaussian policy solves all the MuJoCo tasks from MNIH-DM internal suite — including high-dimensional bipedal and quadrupedal locomotion — within hours on a single CPU machine, achieving final returns competitive with prior trust-region methods (TRPO, the contemporaneous SOTA) but with substantially less compute.

**Labyrinth (3D maze).** LSTM-A3C learns to navigate randomized first-person 3D mazes from raw pixel input, demonstrating that the recurrent variant integrates partial-observability information across time. This is the first demonstration of an actor-critic recurrent policy on a 3D visual navigation task and the proximate ancestor of all subsequent recurrent-PPO work on partially-observable environments.

**Scaling with thread count.** Wall-clock time-to-convergence on Atari decreases roughly linearly with the number of parallel actor-learners up to $N = 16$, with diminishing returns beyond that.

## 6. Critique / limitations

A3C is on-policy and uses no experience replay; it therefore burns experience that off-policy methods could reuse, and on Atari it is sample-inefficient compared to off-policy DQN variants (despite winning on wall-clock time). The asynchronous-parallelism wall-clock win comes at the cost of substantially higher *total environment-step* counts.

The Hogwild lock-free asynchronous updates have no convergence guarantees for non-convex deep networks. The paper demonstrates empirical stability but does not characterize the regimes (network depth, learning rate, thread count) in which asynchronous stale gradients begin to degrade learning. Subsequent work (A2C, the synchronous variant) showed that synchronous batched updates often match or exceed A3C's performance, suggesting that the asynchrony itself was a hardware convenience rather than an algorithmic necessity.

The $n$-step advantage estimator with truncated $t_\max$ is biased at the segment boundary by the bootstrapped $V_\phi(s_{t_\max})$, which is also stale by the time the thread's segment completes. GAE ($\lambda < 1$, `schulman2016_gae`) generalizes the bias–variance trade-off cleanly and is the modern default; A3C's $n$-step recipe is the $\lambda = 1$-within-segment, $\lambda = 0$-at-truncation special case.

The trust-region issue addressed by TRPO and PPO is absent: A3C uses a vanilla policy-gradient update with entropy regularization as the only stabilizer. Empirically this is sufficient on Atari but breaks on harder continuous-control tasks at scale, which is one reason PPO (`schulman2017_ppo`) eventually replaced A3C as the default deep RL recipe in most settings.

The LSTM-A3C variant is presented as a straightforward extension, but the paper does not address the more subtle issues that arise with recurrent policies — segment-boundary state-handling, value-function staleness across segments, BPTT through the LSTM cell with asynchronous updates — that Pleines et al. 2022 (`pleines2022_recurrent_ppo`) later systematizes. The Labyrinth results are presented qualitatively without a sample-efficiency or stability ablation.

All results are on tasks where the reward signal is dense enough for $n$-step bootstrapping to work; sparse-reward and long-horizon tasks (e.g., Montezuma's Revenge) remain unsolved by A3C and motivated the subsequent literature on intrinsic motivation, hierarchical RL, and model-based RL.

The asynchronous framework predates and is conceptually distinct from the *distributed* RL frameworks (IMPALA, Ape-X, R2D2, SEED RL) that followed; A3C scales to one machine, not many, and the importance-sampling corrections needed for true distributed off-policy actor-critic are absent.

## 7. Connection to our work

A3C is structurally upstream of the entire RL stack the user's program uses, and its architectural commitments propagate into both the published Recurrent ViT and the multi-hub multi-objective system.

**The actor-critic decomposition as architectural template.** The Recurrent ViT (2502.10955) attaches an actor head and a value head to the recurrent memory state $H_t$. This is exactly A3C's design: a shared feature trunk (in A3C, a CNN; in the recurrent ViT, the self-attention + memory stack) feeds split policy and value heads. The user's multi-hub program (`multi_hub_multi_objective_system`) preserves this template in its RL hub — the RL hub maintains a memory state $C^{RL}_t$ that conditions both an actor and a value head, with the value head's advantage signal computed via GAE (the modern descendant of A3C's $n$-step advantage). A3C is the conceptual proof that this two-headed architecture is *sufficient* — no auxiliary discriminator, no Q-table, no model-based rollout — to train deep policy networks on rich observation streams.

**Async-parallel rollout and multi-hub competition.** A3C's central architectural insight is that *parallel actors exploring concurrently* can substitute for experience replay as the decorrelation mechanism. The user's multi-hub program builds on a structurally similar premise at a different scale: parallel *hubs* (MSI, RL, VAE) each maintain their own memory states and contribute concurrently to a shared self-attention substrate, with competition among hubs serving as the architectural pressure that gives rise to predictive coding (`competition_emergent_predictive_coding`). A3C's parallel-actor framework is the closest published precedent for "parallel concurrent computational entities with a shared parameter substrate" in the deep RL literature, and the user's multi-hub system can be read as the cross-objective generalization of A3C's parallel-actor architecture — instead of $N$ copies of the same actor sharing parameters, the user proposes $K$ different-objective hubs sharing a self-attention substrate.

**The LSTM-A3C variant and the recurrent ViT actor.** A3C's LSTM variant is the immediate ancestor of the recurrent ViT's actor: in both cases, a recurrent state $H_t$ accumulates evidence over a temporally-extended rollout, and the actor head's logit is conditioned on $H_t$ rather than just on $s_t$. The user's Feedback Transformer generalizes the LSTM in this role — instead of a single LSTM cell feeding the actor head, the user's program admits arbitrarily many recurrent memory states feeding both heads through the FT's Q/K/V structure. The architectural commitment is the same; only the recurrent primitive differs.

**The entropy bonus and exploration.** A3C's entropy bonus $\beta H(\pi_\theta)$ is preserved in PPO (`schulman2017_ppo`) and therefore in the Recurrent ViT's training loop. The user's program inherits this exploration regularizer — an important design choice when the actor head is conditioned on a high-capacity recurrent memory that could otherwise rapidly collapse onto a deterministic policy and lose the exploration signal needed for credit assignment over long change-detection rollouts.

**Connection to neuroscience and the RL hub.** A3C's $n$-step advantage estimator is built on TD residuals $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$, the same quantity hypothesized to be encoded by midbrain dopamine neurons (`glimcher2011_dopamine_rpe`, `botvinick2020_deep_rl_neuro`). In the user's multi-hub program, the RL hub's training loop is the algorithmic stand-in for striatal TD-learning, and A3C's parallel-actor structure has a loose biological echo in the multiple cortico-basal-ganglia-thalamic loops that operate in parallel on different action repertoires.

**Why A3C and not just PPO?** PPO is the descendant the user actually uses, but A3C is the load-bearing conceptual reference for two reasons. First, A3C established that on-policy actor-critic with a shared trunk is *sufficient* — a result PPO inherits but did not establish. Second, the asynchronous-parallel framework is the closest published analog to the multi-hub competition architecture, and PPO's typical implementation (synchronous A2C-style batched updates) abstracts that away. For the user's multi-hub design, A3C is the more directly relevant precedent.

## 8. Citations to follow

- `williams1992_reinforce` — REINFORCE, the policy-gradient algorithm A3C's actor loss instantiates. Not in seed.
- `sutton1988_td_learning` — TD($\lambda$) and eligibility traces, the conceptual ancestor of $n$-step bootstrapping. Not in seed; high priority.
- `mnih2015_dqn` — DQN, the off-policy replay-buffer alternative A3C explicitly contrasts against. Not in seed; high priority for the off-vs-on-policy dichotomy.
- `mnih2014_recurrent_attention` — RAM, the same first-author's earlier glimpse-based recurrent attention model trained with REINFORCE. In seed.
- `hochreiter_schmidhuber1997_lstm` — LSTM cell used in LSTM-A3C. In seed.
- `schulman2015_trpo` — TRPO, the contemporaneous trust-region alternative that A3C outperforms on wall-clock time but not always on sample efficiency. Not in seed.
- `schulman2017_ppo` — PPO, the clipped-surrogate descendant that supersedes A3C as the default deep RL recipe. In seed, full depth.
- `schulman2016_gae` — GAE, the bias-variance-tunable generalization of A3C's $n$-step advantage. In seed, full depth.
- `recht2011_hogwild` — the lock-free asynchronous SGD framework A3C's parameter updates inherit from. Not in seed.
- `espeholt2018_impala` — IMPALA, the distributed off-policy actor-critic with V-trace correction that supersedes A3C at the multi-machine scale. Not in seed.
- `wang2017_acer` — ACER, the off-policy variant of A3C with experience replay and Retrace targets. Not in seed.
- `pleines2022_recurrent_ppo` — best practices for recurrent PPO; the systematic treatment of issues A3C's LSTM variant first encountered. In seed.
