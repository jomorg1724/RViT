---
id: hafner2020_dreamer
title: "Dream to Control: Learning Behaviors by Latent Imagination"
authors:
  - "Hafner, Danijar"
  - "Lillicrap, Timothy"
  - "Ba, Jimmy"
  - "Norouzi, Mohammad"
year: 2020
venue: "ICLR"
doi: ""
arxiv: "1912.01603"
url: "https://arxiv.org/abs/1912.01603"
tags:
  - deep-learning
  - reinforcement-learning
  - world-models
concepts:
  - coupled-rnn-controller-model
  - world-model-emergence
  - coupled-rnn-world-models
related:
  - ha_schmidhuber2018_world_models
  - schmidhuber2015_learn_to_think
  - bardes2023_vjepa
  - lecun2022_path_to_agi
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Dream to Control: Learning Behaviors by Latent Imagination

## 1. Abstract

Dreamer is a reinforcement-learning agent that learns long-horizon visual control tasks from images. It learns a *world model* — a recurrent state-space model (RSSM) — that compresses pixel observations into a low-dimensional latent space and predicts future latents conditioned on actions. The agent then learns an actor-critic policy *purely by latent imagination*: it generates simulated rollouts inside the world model and propagates analytic value gradients backward through the imagined rollouts to train both the policy (actor) and value function (critic). On 20 challenging visual control tasks from the DeepMind Control Suite, Dreamer outperforms model-free baselines (D4PG, A3C) in data-efficiency, computational cost, and final task performance. The paper establishes that *training inside a learned world model* is a competitive — and often superior — alternative to model-free RL for visual control, and that analytic value gradients through the world model are an effective training mechanism.

## 2. Why this matters for us

Dreamer is the modern mature instance of the Schmidhuber 2015 / Ha & Schmidhuber 2018 coupled-RNN world-model paradigm. It is the contemporary benchmark against which the user's multi-hub program would be compared on RL tasks. Architecturally, Dreamer is what PRISM v2 *plus* a learned predictive head on the slow memory would converge toward: a stack of recurrent modules trained on a combination of reconstruction (V), prediction (M), and reward (C). The paper is the load-bearing reference for treating world-model-based RL as a viable scaled-up paradigm; if the user's multi-hub system is to be empirically competitive with current SOTA, it must be benchmarked against Dreamer-class models.

## 3. Key claims

1. A *recurrent state-space model* (RSSM) can be trained jointly to reconstruct observations, predict next latents, and predict rewards. The joint training produces a world model that supports policy learning through imagination.
2. The RSSM separates stochastic and deterministic components: a deterministic recurrent state $h_t$ carries information through time, and a stochastic latent state $s_t$ captures the uncertainty in the current observation. The architecture is more sophisticated than Ha & Schmidhuber's MDN-RNN.
3. **Analytic value gradients.** The actor and critic are trained via differentiable rollouts through the world model. The critic's predicted value is backpropagated through the imagined sequence to compute policy gradients. This is *more efficient* than the evolutionary search Ha & Schmidhuber used.
4. **Pure latent imagination.** The policy is trained *entirely* on simulated rollouts inside the world model, with no real-environment interaction during the imagination phase. Only the world model is trained from real-environment data.
5. **Data efficiency.** Dreamer is substantially more data-efficient than model-free baselines, reaching equivalent performance with far fewer environment steps.
6. **Robust to long horizons.** The 15-step imagination horizon is sufficient for the Control Suite tasks; the analytic-gradient framework handles long-horizon credit assignment that pure model-free methods struggle with.

## 4. Methods

**RSSM.** The world model is the RSSM, with three components:
- **Encoder.** Maps observation $o_t$ to a stochastic latent $s_t \sim q(s_t | h_t, o_t)$, where $h_t$ is the deterministic recurrent state.
- **Deterministic recurrence.** $h_{t+1} = f(h_t, s_t, a_t)$, where $f$ is a GRU.
- **Transition prior.** $p(s_{t+1} | h_{t+1})$, predicting the next stochastic latent without seeing $o_{t+1}$.

The world model is trained on real environment rollouts with three loss terms:
- *Reconstruction:* $\log p(o_t | h_t, s_t)$ — the observation can be reconstructed from the latent.
- *Reward prediction:* $\log p(r_t | h_t, s_t)$ — the reward can be predicted from the latent.
- *Prior matching:* $\text{KL}(q(s_t|h_t, o_t) \| p(s_t|h_t))$ — the encoder distribution matches the transition prior.

**Actor and critic.** A policy $\pi(a_t|h_t, s_t)$ and value function $v_\phi(h_t, s_t)$, both small MLP networks. Trained on imagined rollouts of length $H$ (typically 15 steps) inside the RSSM. The actor's loss is the negated $\lambda$-return from the imagined rollout; the critic's loss is the squared error against the $\lambda$-return target. Gradients flow backward through the imagined rollout to compute the actor's policy gradient.

**Training loop.** Alternate between (a) collecting environment data with the current policy, (b) training the RSSM on a batch of real rollouts, (c) generating imagined rollouts and training actor/critic on them.

## 5. Results

The principal quantitative findings:

- **DeepMind Control Suite (20 tasks).** Dreamer achieves higher mean episode return than model-free baselines (D4PG, A3C) across the suite. The performance gap is largest on tasks with long horizons and sparse rewards.
- **Data efficiency.** Dreamer reaches equivalent performance with ≈10× fewer environment steps than D4PG on several tasks.
- **Compute efficiency.** Dreamer is comparable in wall-clock time per training step but achieves better performance per step due to the analytic-gradient training scheme.
- **Imagination horizon.** Performance is robust to imagination horizons in the 10–20 step range; longer horizons introduce more error in long-rollout predictions.
- **Visual generalization.** The learned latents capture task-relevant structure; Dreamer agents trained on one task variant generalize to held-out variants reasonably well.

Subsequent work (Dreamer v2, v3) has extended the framework to Atari and other benchmarks, establishing Dreamer-class architectures as a leading model-based RL paradigm.

## 6. Critique / limitations

The world model is trained on pixel reconstruction. This is computationally expensive (high-dimensional output) and the reconstruction objective may not be optimal for representation learning — the model may waste capacity on perceptually-irrelevant pixel details. LeCun's JEPA framework ([lecun2022_path_to_agi](research_db/papers/lecun2022_path_to_agi.md)) argues for latent-only prediction instead.

The imagination horizon is fixed (typically 15 steps). Beyond this horizon, the predictions degrade due to accumulating model errors. For tasks requiring planning over much longer horizons, additional hierarchical structure is needed.

The RSSM has a deterministic-stochastic decomposition that is principled but somewhat arbitrary. Whether the right decomposition is what Dreamer uses, or something different (e.g., a fully variational latent, a pure deterministic latent, a hybrid with different proportions) is not exhaustively explored.

The actor and critic are small MLPs operating on the world model's latent. Whether they should be larger and more expressive (and what the trade-off is) is task-dependent. The Dreamer architecture concentrates capacity in the world model.

The framework requires *real* environment data for world-model training. The agent does interact with the environment; the "training in the dream" applies only to the actor-critic. This is a more modest claim than Ha & Schmidhuber's "the policy never sees the real environment."

The paper does not address competitive multi-objective training. Dreamer's actor, critic, and world model are *cooperative* — each is trained to make the others' jobs easier. The user's competition-emergent-PC thesis would say that competitive coupling produces fundamentally different (and possibly better) representations. This is a theoretical contrast, not a critique of Dreamer's empirical claims.

## 7. Connection to our work

Dreamer is the modern benchmark for the architectural class the user's program belongs to:

**RSSM as a structural analog of PRISM v2 with predictive head.** PRISM v2's slow memory ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) is structurally similar to the RSSM's deterministic recurrence $h_t$; the fast memory is more like the stochastic latent $s_t$ (it's updated more frequently and may have noise from the moment-to-moment input). Adding a predictive head to PRISM v2's slow memory — predicting future $M^{\text{slow}}$ from current $M^{\text{slow}}$ and action — would make PRISM v2 functionally analogous to the RSSM.

**Analytic value gradients as a training scheme.** PRISM v1 and v2 are trained with PPO (model-free policy gradient). Dreamer's analytic-value-gradient training through the world model is a more sample-efficient alternative. If the user's multi-hub system is extended to RL tasks, the Dreamer training scheme is a natural choice — train hubs from real data; train policy from imagined rollouts inside the trained hubs.

**Latent imagination as the empirical test of world-model emergence.** The user's [world_model_emergence](research_db/concepts/world_model_emergence.md) prediction is that a world model should emerge from multi-hub competition *without* explicit M training. The empirical test (Evolution of Architecture §"Predictive Coding from Competition") is to roll out a trained system in its own latent space and measure trajectory coherence. Dreamer's analytic-value-gradient mechanism *is* trajectory rollout through the world model. The technical machinery for the user's experimental test is borrowed directly from Dreamer.

**Benchmark target.** If the user's multi-hub system is to be evaluated on RL tasks, the DeepMind Control Suite is a natural benchmark. Dreamer is the SOTA model-based baseline; the user's program would need to match or exceed Dreamer's performance to validate the competitive-multi-hub commitment.

**Competition vs cooperation.** The user's program contrasts with Dreamer on the cooperation-vs-competition axis. Dreamer's components cooperate; the user's hubs compete. Whether the architectural choice produces different empirical performance — and what tasks would discriminate the two — is an open empirical question. The most direct test would be a multi-hub system trained with hub-specific objectives on a Control-Suite-like task, compared to a Dreamer baseline on the same task.

The recurrent ViT and PRISM papers don't engage with Dreamer. Any future manuscript on the multi-hub system that touches on RL tasks should benchmark against Dreamer.

## 8. Citations to follow

- `ha_schmidhuber2018_world_models` — the founding empirical predecessor. In seed, full depth.
- `schmidhuber2015_learn_to_think` — the conceptual ancestor. In seed, full depth.
- `hafner2019_planet` — PlaNet, the immediate predecessor. Not in seed.
- `hafner2021_mastering_atari_dreamer_v2` — Dreamer v2 on Atari. Not in seed.
- `hafner2023_dreamer_v3` — Dreamer v3 across many environments. Not in seed.
- `schrittwieser2020_muzero` — MuZero, model-based RL with learned value/policy. Not in seed.
- `lecun2022_path_to_agi` — JEPA position paper, contrasting with pixel reconstruction. In seed.
- `bardes2023_vjepa` — V-JEPA, latent-prediction self-supervised world model. In seed, full depth.
