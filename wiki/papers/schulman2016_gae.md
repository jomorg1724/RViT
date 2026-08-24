---
id: schulman2016_gae
title: "High-Dimensional Continuous Control Using Generalized Advantage Estimation"
authors:
  - "Schulman, John"
  - "Moritz, Philipp"
  - "Levine, Sergey"
  - "Jordan, Michael I."
  - "Abbeel, Pieter"
year: 2016
venue: "ICLR"
doi: ""
arxiv: "1506.02438"
url: "https://arxiv.org/abs/1506.02438"
tags:
  - reinforcement-learning
  - deep-learning
concepts:
  - gae
  - actor-critic
  - reinforce
related:
  - schulman2017_ppo
  - pleines2022_recurrent_ppo
  - sutton_barto2018_rl_intro
  - botvinick2020_deep_rl_neuro
  - glimcher2011_dopamine_rpe
  - hafner2020_dreamer
  - ha_schmidhuber2018_world_models
  - babayan_uchida_gershman2018_belief_states_dopamine
  - friston2012_dopamine_active_inference
  - springenberg2024_offline_actor_critic
  - mnih2016_a3c
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# High-Dimensional Continuous Control Using Generalized Advantage Estimation

## 1. Abstract

Policy gradient methods are an appealing approach in reinforcement learning because they directly optimize the cumulative reward and can straightforwardly be used with nonlinear function approximators such as neural networks. The two main challenges are the large number of samples typically required, and the difficulty of obtaining stable and steady improvement despite the nonstationarity of the incoming data. The authors address the first challenge by using value functions to substantially reduce the variance of policy-gradient estimates at the cost of some bias, with an exponentially-weighted estimator of the advantage function that is analogous to TD($\lambda$). They address the second challenge by using a trust-region optimization procedure (TRPO) for both the policy and the value function, both represented by neural networks. The approach yields strong empirical results on highly challenging 3D locomotion tasks, learning running gaits for bipedal and quadrupedal simulated robots and a policy for a biped to stand up from lying on the ground. In contrast to prior work that uses hand-crafted policy representations, the neural-network policies map directly from raw kinematics to joint torques. The algorithm is fully model-free, and the amount of simulated experience required for the 3D-biped learning tasks corresponds to 1–2 weeks of real time.

## 2. Why this matters for us

GAE($\gamma$, $\lambda$) is the *advantage estimator* that PPO (`schulman2017_ppo`) — the training algorithm of the published Recurrent ViT (2502.10955), PRISM v1, and PRISM v2's actor — uses to convert noisy Monte-Carlo returns into a low-variance learning signal for the policy gradient. Without GAE the variance of the policy gradient over long recurrent rollouts is large enough to prevent stable training; with GAE, $\lambda$ becomes the bias–variance knob that determines how aggressively the value baseline absorbs long-horizon credit assignment versus how much the empirical return is trusted. Reading GAE carefully also gives us the canonical formulation of the *advantage function* itself, the TD($\lambda$)-style weighting that underlies most modern actor-critic algorithms, and the conceptual bridge between RL training of attention controllers and the dopamine-RPE / TD-learning literature in neuroscience (`glimcher2011_dopamine_rpe`, `babayan_uchida_gershman2018_belief_states_dopamine`).

## 3. Key claims

1. The standard policy-gradient theorem can be rewritten as an expectation over the *advantage function* $A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$; using $A^\pi$ instead of $Q^\pi$ or the raw return preserves the gradient direction in expectation while reducing variance.
2. A family of $k$-step advantage estimators $\hat A_t^{(k)}$ trades off bias (small $k$, heavy reliance on the bootstrapped value function) against variance (large $k$, heavy reliance on the empirical Monte-Carlo return).
3. The Generalized Advantage Estimator GAE($\gamma$, $\lambda$) is the exponentially-weighted average of these $k$-step estimators with weight $\lambda$, and admits the compact recursive form $\hat A_t = \delta_t + (\gamma \lambda)\,\hat A_{t+1}$ where $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$ is the one-step TD residual.
4. GAE is structurally analogous to the TD($\lambda$) eligibility-trace estimator of value functions, but operates on the *advantage* used inside the policy-gradient expectation rather than on the value target.
5. The discount factor $\gamma$ and the GAE parameter $\lambda$ play conceptually distinct roles: $\gamma$ shapes the *objective* (effective horizon of the return); $\lambda$ shapes the *estimator* (bias–variance trade-off given that objective).
6. Combining GAE with TRPO and a separately-trained value network produces a fully model-free actor-critic algorithm that solves high-dimensional continuous-control benchmarks — 3D bipedal/quadrupedal locomotion and standing-from-supine — using raw kinematics as observations.
7. The trust-region procedure can be applied to *both* policy and value updates; clipping the value update step bounds value-network drift between iterations and stabilizes the advantage estimate.

## 4. Methods

**Setting.** Infinite-horizon discounted MDP, policy $\pi_\theta(a \mid s)$, value function $V_\phi(s)$, both neural networks. The policy-gradient theorem gives
$$
\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\Big[\sum_{t=0}^{\infty} \Psi_t \, \nabla_\theta \log \pi_\theta(a_t \mid s_t)\Big]
$$
where $\Psi_t$ can be any of: the total return $\sum_{t'} r_{t'}$, the return-from-$t$, the action-value $Q^\pi(s_t, a_t)$, the advantage $A^\pi(s_t, a_t)$, or the TD residual $\delta_t$. Using $\Psi_t = A^\pi$ achieves the lowest asymptotic variance among unbiased estimators.

**$k$-step estimators.** Define $\hat A_t^{(k)} = \sum_{l=0}^{k-1} \gamma^l \delta_{t+l} = -V(s_t) + r_t + \gamma r_{t+1} + \ldots + \gamma^{k-1} r_{t+k-1} + \gamma^k V(s_{t+k})$. As $k$ grows, the estimator becomes less biased (depends less on $V$) and higher variance (depends more on noisy rewards); $k \to \infty$ recovers the Monte-Carlo advantage.

**GAE.** GAE($\gamma$, $\lambda$) is defined as the exponentially-weighted average
$$
\hat A_t^{\mathrm{GAE}(\gamma, \lambda)} = (1 - \lambda) \sum_{k=1}^{\infty} \lambda^{k-1} \hat A_t^{(k)} = \sum_{l=0}^{\infty} (\gamma \lambda)^l \, \delta_{t+l}.
$$
For a finite-horizon rollout of length $T$, the truncated form is $\hat A_t = \sum_{l=0}^{T-t-1} (\gamma\lambda)^l \, \delta_{t+l}$, computed efficiently by the backward recurrence $\hat A_t = \delta_t + \gamma \lambda \hat A_{t+1}$ with $\hat A_T = 0$. Recommended hyperparameters: $\gamma \in [0.99, 0.995]$, $\lambda \in [0.95, 0.99]$.

**Limit cases.** $\lambda = 0$ collapses GAE to the one-step TD residual $\delta_t$ — minimum variance, maximum bias, equivalent to actor-critic with a one-step bootstrap. $\lambda = 1$ recovers the Monte-Carlo advantage $\sum_l \gamma^l r_{t+l} - V(s_t)$ — unbiased given a perfect $V$, maximum variance.

**Trust-region policy optimization.** The policy update uses TRPO (Schulman et al. 2015): maximize a linearized surrogate $\hat{\mathbb{E}}_t[r_t(\theta)\, \hat A_t]$ subject to the constraint $\hat{\mathbb{E}}_t[\mathrm{KL}(\pi_{\theta_\text{old}}, \pi_\theta)] \leq \delta_\text{KL}$, solved by conjugate gradient + line search. The value function is updated by a trust-region least-squares fit to the Monte-Carlo target $\hat R_t = \hat A_t + V_\phi^\text{old}(s_t)$.

**Architectures.** Fully-connected MLPs with $\tanh$ nonlinearities. Policy: Gaussian with mean output by the network and a state-independent diagonal standard deviation. Value: scalar MLP head.

## 5. Results

**3D MuJoCo locomotion (humanoid, biped, quadruped, swimmer).** With GAE($\lambda = 0.96$) and $\gamma = 0.995$, TRPO learns running gaits for a 33-dimensional biped (Walker2d-like) and a 50-dimensional quadruped (cheetah-like) from raw kinematics. Final returns: humanoid $\approx 1400$ at 1M timesteps; biped $\approx 4500$; quadruped $\approx 4000$. These were SOTA on the 3D continuous-control suite at the time.

**Standing-from-supine humanoid.** The hardest task: 100M+ timesteps to learn, but the policy generalizes to perturbations.

**Ablation on $\lambda$.** $\lambda \in \{0, 0.5, 0.95, 0.97, 0.99, 1\}$ swept across all tasks. $\lambda \in [0.95, 0.99]$ is the sweet spot uniformly; $\lambda = 1$ (pure Monte-Carlo) gives unstable / divergent training on harder tasks because the variance blows up; $\lambda = 0$ (pure one-step) is biased enough that the policy never reaches the asymptotic return.

**Ablation on $\gamma$.** $\gamma \in \{0.96, 0.98, 0.99, 0.995, 1\}$. Higher $\gamma$ wins on harder tasks where credit must propagate over hundreds of steps; lower $\gamma$ wins on tasks with shorter effective horizons. The empirical recommendation is $\gamma \approx 0.99$–$0.995$.

**Sample efficiency.** All 3D locomotion tasks learned within 1–2 weeks of *simulated* real time. The biped-standing task is the most expensive: $\sim 10^8$ simulated steps, comparable to behavior-cloning-from-demonstration baselines but with no demonstrations.

## 6. Critique / limitations

GAE is *not* unbiased — for any $\lambda < 1$, the estimator's bias depends on how well $V_\phi$ approximates $V^\pi$. When the value function is poorly trained — early in learning, after a large policy change, or in regions of state space rarely visited — GAE advantages are systematically biased in ways that distort the policy gradient. The paper does not characterize this bias quantitatively.

The bias–variance trade-off is presented as a $\lambda$-sweep, but the *optimal* $\lambda$ depends on the value-function accuracy, rollout length, and task horizon. Practitioners use the paper's recommended $\lambda \approx 0.95$–$0.97$ as a default, but there is no principled procedure for adapting $\lambda$ online. Subsequent work (e.g., adaptive trace-decay schemes) addresses this only partially.

The TRPO trust-region wrapper is heavy: conjugate-gradient inner loops, Hessian-vector products, line search. PPO (`schulman2017_ppo`) explicitly replaces this with the simpler clipped-ratio surrogate while keeping GAE as the advantage estimator; in practice PPO+GAE is the modern de-facto recipe and TRPO+GAE is rarely run.

The paper's experiments are entirely *feedforward* MuJoCo continuous control. GAE's interaction with *recurrent* policies — where the value function is conditioned on a hidden state $V_\phi(s_t, H_t)$ that itself depends on the policy — is unaddressed. In recurrent settings, the truncated GAE recurrence at segment boundaries introduces additional bias because $\hat A_T \neq 0$ at the truncation point and is typically bootstrapped from a possibly stale $V_\phi$. This is the issue Pleines et al. 2022 (`pleines2022_recurrent_ppo`) systematizes.

GAE assumes a single scalar reward signal. The connection to *distributional* RL (e.g., PRISM v2's distributional Q-critic, Bellemare et al. 2017) is non-trivial; one would need to define a distributional advantage and a distributional TD residual, which the paper does not address.

The empirical wins are reported on simulated locomotion; transfer to real robots is not demonstrated in this paper and was the subject of years of follow-up work on sim-to-real.

## 7. Connection to our work

GAE is the *advantage-estimator backbone* of every PPO-trained component in the user's program. Its design choices propagate into the Recurrent ViT's change-detection actor, PRISM v1's prediction-error-driven attention controller, PRISM v2's actor head, and the RL hub of the broader multi-hub architecture (`multi_hub_multi_objective_system`).

**The advantage function and the actor head.** The Recurrent ViT (2502.10955) trains its actor with PPO, which means it computes $\hat A_t$ via GAE at every step. The actor's loss gradient is $\nabla_\theta \log \pi_\theta(a_t \mid s_t, H_t) \cdot \hat A_t$, and the value-network gradient is $\nabla_\phi (V_\phi(s_t, H_t) - \hat R_t)^2$ where the target $\hat R_t = \hat A_t + V_\phi^\text{old}(s_t, H_t)$. The advantage thus appears on *both* sides of the actor-critic system, and its variance directly determines training stability on long change-detection rollouts.

**The $\lambda$ knob and the recurrent-credit-assignment problem.** For change detection, the reward arrives many steps after the predictive evidence in the input stream. High $\lambda$ ($\approx 0.95$–$0.97$) keeps credit-assignment information flowing back through the GAE chain; low $\lambda$ forces the value head $V_\phi(s_t, H_t)$ to carry that information internally. In the user's program, $H_t$ is the recurrent ViT's full memory state, so low $\lambda$ shifts the burden of long-horizon credit assignment onto the *recurrent state itself* — a strong test of whether the memory architecture suffices to encode multi-step task structure without explicit return propagation. The recurrent ViT paper's choice of $\lambda \approx 0.95$ is the standard PPO default and a sensible starting point; ablating $\lambda$ would be an informative future experiment for probing what the recurrent state has learned.

**Connection to TD-learning and dopamine RPE.** The TD residual $\delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$ that GAE is built on is the same quantity hypothesized to be encoded by midbrain dopamine neurons (`glimcher2011_dopamine_rpe`, `babayan_uchida_gershman2018_belief_states_dopamine`, `friston2012_dopamine_active_inference`). GAE's $\lambda$-weighted sum of TD residuals is the *eligibility-trace* extension of dopamine RPE — the multi-step credit-assignment signal that classical TD($\lambda$) (Sutton 1988) proposes is computed by basal-ganglia microcircuits. The user's multi-hub program with an explicit RL hub can be read as a computational realization of cortico-basal-ganglia-thalamic credit assignment (`cortico_basal_ganglia_thalamic_loops`), in which the RL hub's PPO+GAE training loop is the algorithmic stand-in for striatal TD-learning.

**Trust regions vs. clipping; relevance to PRISM.** This paper is the *TRPO+GAE* recipe; PPO (`schulman2017_ppo`) is the simplified *clip+GAE* successor. PRISM v1 and v2 use PPO+GAE. The architectural design of the recurrent state is therefore decoupled from the choice of trust-region mechanism — only from GAE itself. The conceptual implication: any future replacement of PPO (e.g., distributional actor-critic à la Springenberg et al. 2024, `springenberg2024_offline_actor_critic`) will probably preserve GAE-style advantage estimation, so understanding GAE is a more durable architectural investment than understanding PPO's specific clip.

**The value head and the recurrent state.** GAE assumes a value function $V_\phi(s_t)$. In the user's program this becomes $V_\phi(s_t, H_t)$; the value head is conditioned on the same memory state that conditions the actor. This is the architectural reason the recurrent state must carry *both* task-relevant features (for the policy) *and* return-relevant features (for the value baseline) — and why a single integrated memory makes more sense than separate policy- and value-memories. The Feedback Transformer's role is to give *both* heads access to the same multi-source feedback, so the value head can use the same global structure as the actor when estimating $\hat A_t$.

**Multi-hub competition and shared advantage.** In the multi-hub system, the RL hub's PPO loss includes a GAE advantage computed from a hub-specific value head. If the value head is contaminated by representations driven by the VAE or MSI hub (because the central self-attention substrate is shared), the advantage estimate is biased by those competing hubs. This is the architectural mechanism by which inter-hub competition translates into the RL hub's training signal — a concrete computational instantiation of `competition_emergent_predictive_coding`.

## 8. Citations to follow

- `schulman2015_trpo` — TRPO, the trust-region policy update used in this paper. Not in seed; high priority.
- `kakade_langford2002_cpi` — conservative policy iteration, the conceptual ancestor of trust-region methods. Not in seed.
- `sutton1988_td_learning` — TD($\lambda$) and eligibility traces, the direct conceptual ancestor of GAE's $\lambda$-weighted sum. Not in seed; high priority for the TD / dopamine bridge.
- `williams1992_reinforce` — REINFORCE, the policy-gradient algorithm GAE supplies advantages to. Not in seed.
- `mnih2016_a3c` — A3C / A2C; uses a one-step or $n$-step advantage (special cases of GAE) for asynchronous actor-critic. In seed, full depth.
- `bellemare2017_distributional_rl` — distributional RL, the framework PRISM v2's critic adopts; the GAE-vs-distributional question is open. Not in seed.
- `wang2016_dueling_dqn` — dueling network architectures, an alternative explicit-advantage construction. Not in seed.
- `schulman2017_ppo` — PPO; uses GAE as its advantage estimator and is the modern default. In seed, full depth.
- `pleines2022_recurrent_ppo` — best practices for PPO + GAE with recurrent policies. In seed.
- `sutton_barto2018_rl_intro` — textbook treatment of advantage functions, eligibility traces, and TD($\lambda$). In seed.
