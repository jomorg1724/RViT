---
id: sutton_barto2018_rl_intro
title: "Reinforcement Learning: An Introduction (2nd ed.)"
authors:
  - "Sutton, Richard S."
  - "Barto, Andrew G."
year: 2018
venue: "MIT Press"
doi: ""
arxiv: ""
url: "http://incompleteideas.net/book/the-book-2nd.html"
tags:
  - reinforcement-learning
  - deep-learning
  - review
concepts:
  - actor-critic
  - ppo
  - reinforce
  - gae
  - distributional-rl
  - reward-modulated-attention
related:
  - schulman2017_ppo
  - schulman2016_gae
  - mnih2014_recurrent_attention
  - ha_schmidhuber2018_world_models
  - botvinick2020_deep_rl_neuro
  - hafner2020_dreamer
  - glimcher2011_dopamine_rpe
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_125
status: full
depth: full
last_updated: "2026-05-14"
---

# Reinforcement Learning: An Introduction (2nd ed.)

## 1. Abstract

*Reinforcement Learning: An Introduction* (2nd edition, MIT Press, 2018) is the canonical graduate textbook on reinforcement learning, written by two of the field's founders. It develops the RL problem from first principles — agent, environment, reward, value, policy — and builds up the algorithmic core of the field in a single coherent narrative. Part I treats tabular methods (multi-armed bandits, finite Markov decision processes, dynamic programming, Monte Carlo methods, temporal-difference learning, n-step bootstrapping, and planning/Dyna). Part II treats approximate methods (on-policy and off-policy prediction and control with function approximation, eligibility traces, and policy-gradient methods). Part III treats psychology and neuroscience connections, frontiers, and case studies (TD-Gammon, Watson, Atari DQN, AlphaGo, human-level robotic skill). The 2nd edition adds substantial new material on policy-gradient methods (REINFORCE, actor-critic, off-policy actor-critic), eligibility traces in their modern unified form, the deadly triad of off-policy + bootstrapping + function approximation, and an updated neuroscience chapter centred on the dopamine reward-prediction-error hypothesis. The book is the *de facto* foundation that essentially every subsequent RL paper — including all of those the user's program builds on — assumes.

## 2. Why this matters for us

Sutton & Barto 2018 is the textbook foundation under the RL machinery used in PRISM v1 and PRISM v2, and the substrate on which the user's "RL hub" in the multi-hub program is built. Every RL-flavored decision in the program — the actor-critic split in PRISM v1's controller, the choice of PPO ([schulman2017_ppo](schulman2017_ppo.md)) over vanilla policy gradient, the use of GAE ([schulman2016_gae](schulman2016_gae.md)) for advantage estimation, the framing of attention-as-action in recurrent-attention models ([mnih2014_recurrent_attention](mnih2014_recurrent_attention.md)), and the interpretation of the dopamine RPE signal ([glimcher2011_dopamine_rpe](glimcher2011_dopamine_rpe.md)) as biological TD-error — descends from this book's algorithmic and conceptual scaffolding. It is the single most-cited reference that the user's program *relies on without arguing for*.

## 3. Key claims (key principles)

1. **The RL problem.** RL is the problem of learning what to do — how to map situations to actions — so as to maximize a numerical reward signal, by trial-and-error interaction with an environment that the agent does not know.
2. **The Markov decision process.** Sequential decision-making under uncertainty is formalized as a tuple $(\mathcal{S}, \mathcal{A}, p, r, \gamma)$ with state, action, transition dynamics, reward, and discount; the Markov property lets value functions decompose recursively.
3. **The Bellman equation.** The value of a state under a policy satisfies $v_\pi(s) = \sum_a \pi(a|s) \sum_{s',r} p(s', r | s, a) [r + \gamma v_\pi(s')]$; the optimal value function satisfies the Bellman optimality equation, and dynamic programming exploits these recursions when the model is known.
4. **Generalized policy iteration.** Almost every RL method — DP, Monte Carlo, TD, actor-critic — can be seen as an instance of the same loop: alternate (or interleave) policy evaluation with policy improvement until both stabilize at an optimal policy and optimal value function.
5. **Temporal-difference learning.** TD methods $V(S_t) \leftarrow V(S_t) + \alpha [R_{t+1} + \gamma V(S_{t+1}) - V(S_t)]$ combine the sample-based learning of Monte Carlo with the bootstrapping of DP; they learn online, from incomplete episodes, and converge under mild conditions.
6. **The exploration–exploitation trade-off.** Any RL agent must balance exploiting current knowledge against exploring to improve it; $\epsilon$-greedy, optimistic initialization, UCB, and Thompson sampling are the canonical strategies.
7. **Q-learning and Sarsa.** Off-policy (Q-learning) and on-policy (Sarsa) TD control are the two principal tabular control algorithms; they differ in whether the bootstrap target uses the current behaviour policy or the greedy improvement.
8. **Function approximation and the deadly triad.** Combining off-policy learning, bootstrapping, and function approximation can produce divergence; the book carefully delineates which combinations are safe and which require care (e.g., importance-sampling, emphatic TD, gradient-TD).
9. **Eligibility traces.** The $\lambda$ family ($TD(\lambda)$, true online $TD(\lambda)$, Sarsa($\lambda$)) unifies MC and TD as endpoints of a spectrum, with eligibility traces providing a computationally efficient incremental implementation.
10. **The policy-gradient theorem.** $\nabla_\theta J(\theta) \propto \mathbb{E}_\pi[\nabla_\theta \log \pi_\theta(a|s) \, q_\pi(s,a)]$ — the gradient of expected return with respect to policy parameters can be estimated from sampled trajectories, giving REINFORCE, actor-critic, and (with constraints) PPO/TRPO.
11. **Actor-critic.** Combining a parameterized policy (actor) with a learned value baseline (critic) reduces variance without introducing bias; the critic supplies a TD-error advantage signal that the actor uses to update.
12. **Planning and learning are the same algorithm.** Dyna and related architectures show that model-based planning updates and model-free learning updates have the same form when the model produces simulated experience; this licenses the use of learned world models.
13. **Reward is enough (the reward hypothesis).** All of what we mean by goals and purposes can be well thought of as maximization of the expected value of the cumulative sum of a received scalar reward signal.
14. **The dopamine RPE hypothesis.** TD-error matches, with quantitative precision, the firing patterns of midbrain dopamine neurons, providing the field's clearest computational-neuroscience bridge.

## 4. Methods (pedagogical approach)

The book is *constructive*. It develops each algorithm by first stating a problem (e.g., "estimate $v_\pi$ for a known policy"), introducing the simplest method that solves it (iterative policy evaluation), then progressively relaxing assumptions (unknown model → Monte Carlo; long episodes → TD; large state spaces → function approximation; stochastic policies → policy gradient). Each chapter ends with a *unified view* diagram showing where the new method fits in the algorithmic landscape (sample backups vs. expected backups; shallow vs. deep backups; on-policy vs. off-policy).

Notation is consistent across the entire 500-page book: capital letters for random variables, lowercase for realized values, $\pi$ for policies, $v$ and $q$ for value functions, $\hat{v}$ and $\hat{q}$ for approximators, $w$ and $\theta$ for parameters. The notation table in the front matter is referenced throughout and is itself a contribution to the field's lingua franca.

Pseudocode for every algorithm is supplied in a uniform format and is directly implementable. Exercises range from analytic derivations to programming projects (gridworld, blackjack, mountain car, the racetrack). The book is designed to be read in order; each chapter assumes the previous ones.

The 2nd edition reorganizes the 1st edition's material around three parts (tabular methods; approximate methods; psychology / neuroscience / case studies / frontiers) and adds substantial new content on policy gradients, the deadly triad, true online $TD(\lambda)$, average-reward formulations, and an expanded neuroscience treatment. Roughly a third of the 2nd edition is new material relative to the 1st.

## 5. Results (the body of RL the book established)

The book is not a research report and contains no novel results; it is the *consolidation* of the field's results into a single corpus. The "results" it establishes are:

- **The tabular RL canon.** DP (policy iteration, value iteration), Monte Carlo prediction and control, TD(0), Sarsa, Q-learning, expected Sarsa, double Q-learning, n-step methods, Dyna-Q — each with convergence guarantees under stated assumptions.
- **The approximation canon.** Linear function approximation with on-policy semi-gradient methods (provably convergent), off-policy linear methods with importance sampling and gradient-TD (convergent under stronger assumptions), nonlinear (neural) approximation (no convergence guarantees but empirically successful, e.g. DQN).
- **The eligibility-trace canon.** True online $TD(\lambda)$ as the modern unified treatment that subsumes earlier accumulating and replacing traces.
- **The policy-gradient canon.** REINFORCE, REINFORCE with baseline, one-step actor-critic, $n$-step actor-critic, continuing actor-critic with average reward.
- **Worked case studies.** TD-Gammon (Tesauro), Samuel's checkers player, Watson's Daily Double wagering, Atari DQN, AlphaGo, human-level robotic skill — each presented as a concrete instance of the algorithmic principles, with enough detail to see *how* the principle was deployed.
- **The neuroscience bridge.** Chapters 14–15 lay out the psychological (classical / operant conditioning) and neuroscientific (dopamine, basal ganglia, hippocampus) parallels in enough detail to be the standard cross-disciplinary reference.

## 6. Critique / limitations

The book deliberately *does not* cover several major directions that have become central since publication:

- **Deep RL specifics.** DQN and policy-gradient methods are presented at the level of the underlying RL principles, but modern deep-RL engineering — replay buffers, target networks, distributional value functions, Rainbow, IMPALA, distributed actor-learner architectures — is gestured at but not developed. The user should look to subsequent papers ([schulman2017_ppo](schulman2017_ppo.md), [schulman2016_gae](schulman2016_gae.md), Mnih et al. 2015 DQN, [hafner2020_dreamer](hafner2020_dreamer.md)) for the engineering depth.
- **Model-based RL with learned world models.** The book covers planning with *known* models (Dyna, MCTS); it touches but does not develop end-to-end *learned* world models in the sense of [ha_schmidhuber2018_world_models](ha_schmidhuber2018_world_models.md), PlaNet, Dreamer, MuZero. This is the most consequential omission for the user's program.
- **Multi-agent RL.** Largely absent. The book is a single-agent treatment; the competitive coalition framework the user proposes ([the_user_architectural_program](../threads/the_user_architectural_program.md) §5) requires multi-agent / game-theoretic RL machinery that lies outside this book.
- **Inverse RL, imitation learning, and reward learning.** Briefly mentioned but not developed. The "where does the reward come from" question is treated as out of scope.
- **Hierarchical RL.** Options framework is briefly discussed (§17.1) but the modern hierarchical-RL literature (feudal networks, option-critic, HIRO) is not.
- **Partial observability.** POMDPs are mentioned but the recurrent-policy / belief-state literature ([mnih2014_recurrent_attention](mnih2014_recurrent_attention.md), recurrent DRQN, attention-based POMDP policies) is not developed.
- **Off-policy evaluation and safe RL.** Touched on in Chapter 11 but not deeply.

The book is also *deliberately non-rigorous* by the standards of, e.g., Bertsekas & Tsitsiklis. Proofs are sketched rather than stated formally; the goal is intuition and implementability, not theorem-proving. Readers seeking convergence proofs should consult the cited literature.

Finally, the reward hypothesis itself (claim 13) is taken as a working assumption rather than defended philosophically. Recent critiques (e.g., LeCun's JEPA stance) push back on the universality of scalar reward as the right learning signal.

## 7. Connection to our work

Sutton & Barto 2018 sits beneath the user's program at the level of the *RL hub* and the *RL training procedure for PRISM*. Four specific connections:

**(a) PRISM v1's actor-critic controller.** PRISM v1's policy ([Prism/docs/THESIS.md](../../archive/Prism/docs/THESIS.md) §2.6) is an actor-critic in the textbook sense: a parameterized policy $\pi_\theta(a|s)$ trained by policy gradient with a learned value baseline $\hat{v}_w(s)$ supplying the advantage. The book's Chapter 13 is the load-bearing reference. PPO ([schulman2017_ppo](schulman2017_ppo.md)) is the clipped-objective variant used in practice, but the underlying actor-critic skeleton is from this book.

**(b) The reward-modulated-attention frame for recurrent attention.** RAM ([mnih2014_recurrent_attention](mnih2014_recurrent_attention.md)) frames glimpse selection as a policy-gradient problem with REINFORCE — directly using the textbook's Chapter 13 algorithm. The user's program inherits this framing: any time attention is treated as an action (rather than as a differentiable softmax), the textbook's policy-gradient theorem is the underlying machinery.

**(c) The dopamine RPE / TD-error bridge.** [glimcher2011_dopamine_rpe](glimcher2011_dopamine_rpe.md) and [botvinick2020_deep_rl_neuro](botvinick2020_deep_rl_neuro.md) lean on the book's Chapter 15 treatment of dopamine as TD-error. The user's "RL hub" in the multi-hub architecture ([the_user_architectural_program](../threads/the_user_architectural_program.md) §5) is biologically motivated by this bridge: an RL hub competing for self-attention control is *implementing* what midbrain dopamine signals are believed to implement in cortex.

**(d) The world-model gap.** The book treats planning with *known* models, leaving *learned* world models as a frontier. The user's program ([the_user_architectural_program](../threads/the_user_architectural_program.md) §5, world-model emergence) and the [ha_schmidhuber2018_world_models](ha_schmidhuber2018_world_models.md) / [hafner2020_dreamer](hafner2020_dreamer.md) line of work fill this gap. The user's architectural commitment to *competition-emergent* world models is one step beyond the book's coverage and beyond Dreamer's explicit world-model training.

The Recurrent ViT paper (2502.10955) cites this book as reference 125 — the standard citation for "the RL background you should already have if you're reading our paper" — without engaging algorithmically with any specific chapter. The deeper engagement happens at the PRISM level.

## 8. Citations to follow (specific chapters / topics worth following)

- Chapter 6 (Temporal-Difference Learning) — the algorithmic core of the entire field; every modern RL method bootstraps from a TD target.
- Chapter 12 (Eligibility Traces) — modern unified treatment; true online $TD(\lambda)$ is the substrate for n-step actor-critic in PRISM.
- Chapter 13 (Policy Gradient Methods) — the direct ancestor of [schulman2017_ppo](schulman2017_ppo.md) and [schulman2016_gae](schulman2016_gae.md); read alongside PPO/GAE deepenings.
- Chapter 15 (Neuroscience) — dopamine RPE, basal-ganglia actor-critic, the cortical RPE literature; read alongside [glimcher2011_dopamine_rpe](glimcher2011_dopamine_rpe.md) and [botvinick2020_deep_rl_neuro](botvinick2020_deep_rl_neuro.md).
- Chapter 17 (Frontiers) — options framework, intrinsic motivation, designing reward signals; relevant to the user's competition-emergent program where intrinsic competitive pressure plays the role of an exploration bonus.
- Williams 1992 (REINFORCE) — the policy-gradient origin paper; should be added as a stub.
- Watkins & Dayan 1992 (Q-learning) — the off-policy TD origin paper; should be added as a stub.
- Tesauro 1995 (TD-Gammon) — the first deep success of TD learning; instructive for the connectionist-RL bridge.
- Mnih et al. 2015 (DQN) — the modern deep-RL inflection point; should be added as a stub.
- Bertsekas & Tsitsiklis 1996 (Neuro-Dynamic Programming) — the formal companion to this book; for readers wanting convergence proofs.
