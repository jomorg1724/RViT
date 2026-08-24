---
id: schmidhuber2015_learn_to_think
title: "On Learning to Think: Algorithmic Information Theory for Novel Combinations of RL Controllers and Recurrent Neural World Models"
authors:
  - "Schmidhuber, Juergen"
year: 2015
venue: "arXiv:1511.09249"
doi: ""
arxiv: "1511.09249"
url: "https://arxiv.org/abs/1511.09249"
tags:
  - deep-learning
  - reinforcement-learning
  - theoretical-essay
  - world-models
concepts:
  - world-model-emergence
  - coalition-resource-competition
  - multi-hub-multi-objective-system
  - recurrence-for-temporal-dynamics
  - coupled-rnn-controller-model
  - algorithmic-information-theory
  - curiosity-driven-learning
  - coupled-rnn-world-models
related:
  - sutton_barto2018_rl_intro
  - mante2013_context_dependent_pfc
  - botvinick2020_deep_rl_neuro
  - bardes2023_vjepa
  - lecun2022_path_to_agi
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# On Learning to Think: Algorithmic Information Theory for Novel Combinations of RL Controllers and Recurrent Neural World Models

> **Sourcing note (revised 2026-05-13).** The arXiv abstract page has been verified via WebFetch and confirms the title, sole author (Jürgen Schmidhuber), and high-level abstract content. The full PDF was downloaded but its binary stream could not be parsed for text extraction in this session, so specific equations, algorithmic implementations, and any empirical content in the body of the paper remain *unverified at the level of paragraph-by-paragraph detail*. The conceptual claims below — the controller (C) / recurrent world model (M) coupling; the algorithmic-information-theory framing; curiosity-driven training of M; the framework as the antecedent of Ha & Schmidhuber 2018 "World Models" — are confidently sourced from prior knowledge of this widely-cited paper. Equations or empirical numbers should still be verified against the PDF before being cited in a manuscript.

## 1. Abstract

The paper is a position piece in which Schmidhuber argues that the path to general-purpose problem-solving agents lies in combining two distinct recurrent neural networks: a reinforcement-learning controller (C) that selects actions to maximize reward, and a recurrent world model (M) that learns to predict the environment's response to those actions. Crucially, M can be trained by any unsupervised, self-supervised, or supervised signal — its objective is decoupled from C's reward — and once trained, M can be queried by C as a learned subroutine. C's "thinking" then consists of feeding inputs into M, reading M's outputs, and using them to inform action selection. The framework is grounded in algorithmic information theory: M compresses the regularities of the environment; C exploits this compression by reusing M's internal algorithms rather than re-deriving them. Schmidhuber argues that this division of labour solves the central inefficiency of pure RL — that the agent must learn both the environment and the policy from sparse reward signals — and is the principled architectural template for any agent that needs to reason, plan, or generalize.

## 2. Why this matters for us

This is the closest published antecedent to the user's multi-hub multi-objective architecture (`concepts/competition_emergent_predictive_coding.md`, `threads/the_user_architectural_program.md` §5). Schmidhuber's C–M pair is the two-hub special case of the user's MSI + RL + VAE multi-hub system; the user's competition-emergent-PC hypothesis generalizes Schmidhuber's framework from a single controller-and-model pair to many competing objective-specific hubs, each of which is *both* a controller and a model relative to the others. The architectural commitment that "each hub queries the others via learned input/output pathways" is taken directly from Schmidhuber. The Evolution of Architecture document cites this paper explicitly ("A Schmidhuber Aside") as the conceptual anchor for the multi-hub design.

## 3. Key claims

1. Reinforcement learning from sparse reward alone is informationally inefficient: the agent must learn both the environment's dynamics and the optimal policy from the same low-bandwidth signal. Separating environment-modelling from policy learning is fundamentally more efficient.
2. A recurrent neural world model M, trained by any learning principle, captures the algorithmic regularities of the environment in its weights and internal dynamics. M is, in effect, a learned compression of the environment.
3. A reinforcement-learning controller C can exploit M's compression by treating M as a queryable subroutine: C provides inputs to M, M computes outputs, and C uses those outputs as part of its own decision process. This is "thinking" in the sense of running internal simulations to inform action.
4. The C–M coupling is bidirectional in training: C's actions generate the trajectories M learns from, while M's predictions inform C's policy gradient. The system is a single coupled-RNN computation.
5. The algorithmic-information-theory framing — that the joint complexity of (environment + policy) is minimized when M and C share representations — provides a theoretical justification for the architecture beyond empirical performance.
6. The framework subsumes a range of more specialized architectures: model-based RL, planning networks, predictive-coding agents, and dreaming/simulation-based learning are all special cases of the C–M setup with particular constraints on M's training signal and C's access pattern.

## 4. Methods

The paper is primarily theoretical rather than experimental. Its content is a conceptual specification of the C–M architecture with arguments drawn from algorithmic information theory (Kolmogorov complexity, Levin's universal search) and a survey of prior work that can be reinterpreted in the framework. Specific technical content:

The world model M is a recurrent neural network — Schmidhuber's preferred LSTM variant in the paper's era — trained to predict next observations, next rewards, or other targets that capture environment dynamics. M's training is not tied to C's reward signal; it can be trained offline on demonstration data, online from C's interaction history, or via any combination of supervised/unsupervised signals.

The controller C is also a recurrent neural network, with action outputs trained by policy-gradient methods or evolutionary strategies. C's inputs include the current observation plus learned "queries" that are fed into M; C reads M's outputs at subsequent timesteps and uses them as input to its own policy.

The key architectural commitment is that C can write inputs to M and read outputs from M. This bidirectional interface is what makes M function as a queryable subroutine rather than a fixed module. Schmidhuber emphasizes that the *learning to query* — figuring out what inputs to send to M and how to use M's outputs — is itself part of C's learning problem.

The algorithmic-information-theory argument: M's weights encode a program that predicts environment dynamics. By the universality theorems of algorithmic information theory, sufficiently general computational substrates (RNNs are universal in this sense) can express any computable environment model. C's reuse of M's algorithms is then a search over "M-augmented programs" — programs that exploit M's compression rather than re-deriving every regularity.

## 5. Results

The paper does not report systematic empirical comparisons in the standard sense. It surveys prior architectures that can be reinterpreted as instances of the C–M framework — including Schmidhuber's earlier work on RNN-based RL and curiosity-driven exploration — and argues that the framework is the right organizing principle for the next generation of agent architectures. Specific quantitative claims should be sourced from the paper directly; the principal contribution is the conceptual unification, not a benchmark result.

The paper has been highly influential in setting up the agenda for subsequent work on world-model-based RL (Ha & Schmidhuber 2018 "World Models"; Dreamer; PlaNet; the V-JEPA line at Meta), which can all be read as instantiations of the C–M template with particular choices for M's training and C's access pattern.

## 6. Critique / limitations

The paper is programmatic rather than empirical. Its claims are conceptual: this is the right architecture, the algorithmic-information-theory framing is the right justification, prior work fits inside this framework. None of these are testable in isolation; they have to be evaluated by the quality of the architectures that follow from the framework. Ha & Schmidhuber's 2018 follow-up "World Models" (which trained a VAE + RNN world model and a small controller on Atari and car-racing tasks) is the first major empirical instantiation; its results — that the controller could be trained efficiently inside the world model alone — are the strongest evidence that the C–M template is more than rhetorical.

The framework leaves underspecified what M's training signal *should* be. Schmidhuber argues that M can be trained by any signal, but in practice the choice of signal — pixel reconstruction, next-frame prediction, latent JEPA-style prediction, contrastive learning — has enormous effects on what M learns and how usable it is for C. The framework is therefore a template that needs additional commitments to be instantiated.

The "thinking is querying M" framing privileges a particular access pattern (C writes, M reads, M writes, C reads) that may not be the only useful interaction structure. The user's multi-hub generalization allows symmetric mutual querying across many hubs, which is a meaningful departure.

The algorithmic-information-theory framing is more rhetorical than mathematical in the 2015 paper. The Kolmogorov-complexity arguments do not directly translate into algorithmic guidance for designing M or C. The framework's empirical traction has come from neural-network instantiations that are not driven by the AIT framing.

The paper predates the transformer (2017), the variational-autoencoder synthesis (which was contemporary in 2014 — Kingma & Welling), and the modern self-supervised learning literature. The C–M framework is general enough to accommodate these, but the specific architectural recommendations in the paper are LSTM-based and look dated by current standards.

## 7. Connection to our work

The user's multi-hub multi-objective system (Evolution of Architecture §"A General Purpose Multi-Objective System") is a direct generalization of Schmidhuber's C–M template:

- **Schmidhuber's C** corresponds to the user's RL hub $\mathcal{C}_Q$ in the multi-hub system.
- **Schmidhuber's M** corresponds to the user's VAE / decoder hub $\mathcal{C}_{\text{dec}}$ — the part trained on self-supervised reconstruction.
- **The user adds** an MSI (multi-sensory integration) hub as a third party, and the central self-attention substrate (the Feedback Transformer; `concepts/feedback_transformer.md`) as the shared bandwidth through which all hubs query each other.

The user's contribution beyond Schmidhuber is the **competition pressure**. Schmidhuber's C and M are cooperative — C reads M's outputs to make better decisions. The user's hubs *compete* for control of the central self-attention substrate, and the user's hypothesis (`concepts/competition_emergent_predictive_coding.md`) is that predictive coding emerges from this competition rather than from cooperative coupling. This is a substantive theoretical extension, not just an architectural generalization.

The published architectures relate to this paper as follows:

- **Recurrent ViT (2502.10955)** has only a single hub (actor-critic). It does not separate world-modelling from policy-learning, so it is a *less* Schmidhuber-like architecture than PRISM v2.
- **PRISM v1** has a stronger Schmidhuber-style separation: the generative decoder ($\tilde g, g$) is structurally analogous to M (it learns to predict the environment), and the actor-critic is analogous to C. The variational free-energy auxiliary loss is M's training signal; PPO is C's. This is the closest published instantiation of the C–M template in our work.
- **PRISM v2** retains this separation and adds the action-conditional distributional Q-critic (`Prism/docs/PRISM_V2/Q_CRITIC.md`), which is a step toward the multi-hub design. The Q-critic and the actor share the same backbone but optimize different objectives — proto-competition for backbone representations.

The user's proposed empirical test of competition-emergent PC — train multi-hub system, then probe whether a world model has emerged implicitly from inter-hub competition — is precisely the kind of falsifiable extension of Schmidhuber's framework that the 2015 paper invites but does not itself execute.

## 8. Citations to follow

- `ha_schmidhuber2018_world_models` — the first major empirical instantiation of the C–M template. In seed, full depth.
- `hafner2019_planet` — PlaNet, latent-space planning in a learned world model. In seed, full depth.
- `hafner2020_dreamer` — Dreamer (and v2, v3), the standard model-based RL benchmark architecture. In seed, full depth.
- `bardes2023_vjepa` — V-JEPA, the latent-prediction self-supervised model. In seed.
- `lecun2022_path_to_agi` — LeCun's JEPA position paper; a 2020s update of Schmidhuber's 2015 argument. In seed.
- `srivastava_greff_schmidhuber2015_lstm` — the modern LSTM design Schmidhuber's M would typically use. Candidate for addition.

## 9. Open questions for the deepening pass

1. **Empirical content.** What specific algorithmic implementations of the C–M template does the 2015 paper actually describe in detail? My entry above is largely conceptual; the paper may contain more specific algorithmic content (e.g., particular Q-update rules, particular forms of M's training loss) that should be sourced from the PDF.
2. **AIT formalism.** The algorithmic-information-theory arguments are rhetorical in my summary above. The paper has actual mathematical content (Solomonoff induction, Levin's universal search) that I have not included. A deepening pass should add the formal statements.
3. **Relation to PowerPlay.** Schmidhuber's PowerPlay framework (a parallel line of work from the same era) is closely related; the relationship should be characterized.
4. **The actual experimental results, if any.** The paper may report or cite empirical results on specific benchmarks; these should be added.
