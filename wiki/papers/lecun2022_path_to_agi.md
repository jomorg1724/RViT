---
id: lecun2022_path_to_agi
title: "A Path Towards Autonomous Machine Intelligence (Version 0.9)"
authors:
  - "LeCun, Yann"
year: 2022
venue: "OpenReview (position paper, Meta AI)"
doi: ""
arxiv: ""
url: "https://openreview.net/forum?id=BZ5a1r-kVsf"
tags:
  - theoretical-essay
  - world-models
  - self-supervised-learning
  - deep-learning
  - predictive-coding
concepts:
  - world-model-emergence
  - hierarchical-predictive-coding
  - variational-free-energy
  - active-inference
  - system-1-vs-system-2
  - generative-decoder
  - precision-weighting
  - coupled-rnn-world-models
  - iterative-variational-encoder-decoder
related:
  - bardes2023_vjepa
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - schmidhuber2015_learn_to_think
  - hawkins2021_thousand_brains
  - pezzulo_parr_friston2024_active_inference
  - friston2010_fep_unified_theory
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# A Path Towards Autonomous Machine Intelligence (Version 0.9)

## 1. Abstract

LeCun's position paper proposes a blueprint for autonomous intelligence built around six interacting modules:

- A *perception* module encoding the current state of the world into a latent state $s_t$.
- A *world model* that predicts future states $\hat s_{t+1}$ given an action $a_t$ and an exogenous latent $z_t$ capturing residual uncertainty.
- A *short-term memory* buffering state and prediction history for replay, bootstrapping, and partial-observability handling.
- An *actor* proposing action sequences $a_{t:t+T}$ over a planning horizon.
- A *cost* module split between hard-wired *intrinsic* costs (homeostatic / safety drives) and a learned *critic* that supplies a trainable scalar value.
- A *configurator* that takes a task description and conditions all five other modules — biasing perception, the world model, and the actor toward task-relevant content.

The central technical proposal is the Joint Embedding Predictive Architecture (JEPA), a non-generative, non-contrastive self-supervised objective in which two encoders produce embeddings of two related views $x$, $y$; a predictor maps $\text{Enc}(x)$ plus a latent $z$ to a prediction of $\text{Enc}(y)$. Collapse is prevented by information-maximization (VICReg-style variance/covariance terms) or by an EMA target, not by negative pairs. A hierarchical extension, H-JEPA, stacks JEPAs so that successively higher levels predict over longer temporal horizons and coarser abstraction levels, enabling Mode-2 (deliberative, model-based) planning by gradient-based or sampling-based action search through the cost landscape. Mode-1 (reactive) policy is a separate amortized network distilled from Mode-2 traces. The architecture is presented as a path away from autoregressive generative pretraining and toward energy-based, hierarchical, predictive cognition.

## 2. Why this matters for us

This is the most prominent published *contemporary* of the user's architectural program. Both commit to (a) world-model-based learning as the substrate for intelligence rather than pure supervised pattern matching, (b) hierarchical predictive coding in **latent** rather than pixel space, and (c) a roughly variational / active-inference framing in which prediction error is the central learning signal. The paper is cited in the user's private notes as load-bearing for the architectural program, and the V-JEPA paper (`bardes2023_vjepa`) is the principal experimental instantiation of the JEPA branch of this proposal. Reading it deeply lets us state precisely *where the user's program diverges from LeCun's* — divergences that are not cosmetic but go to the heart of what each architecture commits to about the role of competition, RL, and selective memory in intelligence.

## 3. Key claims

1. Autonomous intelligence requires a *single, modular* cognitive architecture; supervised learning, autoregressive generative modeling, and current RL each address only fragments of the problem.
2. The world model is the load-bearing component; learning it is the single hardest unsolved problem in AI.
3. World models should be **predictive in a learned latent space**, not generative in pixel space — pixel reconstruction wastes capacity on details that are inherently unpredictable.
4. The right self-supervised objective for learning latent predictors is the Joint Embedding Predictive Architecture (JEPA): predict $\text{Enc}(y)$ from $\text{Enc}(x)$ plus a latent $z$, with **non-contrastive** anti-collapse regularization (information maximization or EMA targets).
5. Hierarchy is essential: H-JEPA stacks JEPAs so that higher layers operate at coarser spatial and longer temporal scales, supporting hierarchical planning over abstract sub-goals.
6. Action selection should run in two modes — Mode-1 (a fast amortized policy network) for reactive behavior, and Mode-2 (gradient-based or sampled trajectory optimization over the learned world model) for deliberative planning.
7. The cost / critic module is split between *intrinsic* (hard-wired, e.g., homeostatic) and *trainable* terms; this is the structural analog of a multi-objective reward hierarchy and is what gives the agent a non-trivial value system.
8. The whole architecture is naturally written as an energy-based model: training minimizes an energy that scores compatible state-action-prediction tuples; inference (perception, planning) is minimization of the same energy with respect to latents, actions, or both.
9. The path forward does **not** involve scaling autoregressive language models; LLM-style approaches lack a world model, lack persistent memory, and lack the capacity to plan via simulation.

## 4. Methods

This is a position paper, not an experimental one; the "methods" are architectural proposals. The most concrete pieces are below.

**The six-module architecture.** Perception $P$ produces a state estimate $s_t = P(x_t, s_{t-1})$ from raw input and prior state. World model $W$ predicts $\hat s_{t+1} = W(s_t, a_t, z_t)$ given action $a_t$ and a residual-uncertainty latent $z_t$. Short-term memory $M$ stores recent states and predictions. Actor $A$ proposes action sequences $a_{t:t+T}$. Cost $C = C_\text{intrinsic} + C_\text{critic}$ scores resulting trajectories. Configurator $K$ takes a task description and modulates all five other modules — biasing perception toward task-relevant features, biasing the actor toward goal-consistent actions, biasing the world model toward task-relevant predictions.

**JEPA training.** Given two related views $x$, $y$ (e.g., adjacent video frames, or a masked image and its target), train encoders $s_x = \text{Enc}_x(x)$, $s_y = \text{Enc}_y(y)$ and a predictor $\hat s_y = \text{Pred}(s_x, z)$. The loss is

$$
\mathcal{L}_\text{JEPA} = \| \hat s_y - s_y \|^2 + \lambda_\text{anti-collapse} \cdot R(s_x, s_y)
$$

where $R$ is either (a) a VICReg-style variance + covariance penalty that pushes per-dimension variance up to a target and off-diagonal cross-dimension covariances down toward zero, or (b) implicit through a stop-gradient and an EMA target encoder $\bar\theta \leftarrow \alpha\bar\theta + (1-\alpha)\theta$ (as in BYOL/I-JEPA). The latent $z$ carries the information about $y$ that cannot be predicted from $x$ alone; it is either inferred by minimization (per-example or amortized) or sampled from a prior.

**H-JEPA.** A stack of JEPAs $(\text{JEPA}_1, \ldots, \text{JEPA}_L)$ in which level $\ell+1$ operates on the latent state produced by level $\ell$ and predicts over a longer temporal horizon. Higher levels are trained on coarser-grained data (sub-sampled in time, pooled in space). Hierarchical planning then proceeds top-down: pick an abstract sub-goal at level $L$, expand into a sequence of finer sub-goals at level $L-1$, and so on until concrete actions at level $1$. The structural analogy is to a cortical hierarchy with progressively larger receptive fields and progressively slower temporal dynamics.

**Energy-based formulation.** Each module defines an energy term. The total energy is

$$
E(x, s, a, z) = E_\text{perc}(x, s) + E_\text{world}(s, a, z, s') + E_\text{cost}(s, a)
$$

Training minimizes $E$ with respect to parameters; inference (perception, planning) minimizes $E$ with respect to $s$, $a$, and $z$ for fixed observation $x$. LeCun's claim is that this is more flexible than the probabilistic formulation because $E$ does not have to integrate to 1 and so admits much richer functional forms.

**Mode-1 / Mode-2.** Mode-2 is the explicit energy minimization above — slow but model-based. Mode-1 is an amortized policy $\pi_\theta(a \mid s)$ trained by behavior cloning on Mode-2's outputs, giving fast reactive behavior in well-practiced situations. The framing is explicitly Kahnemanian: Mode-1 is System-1, Mode-2 is System-2, and skill acquisition is the gradual handoff from 2 to 1.

**Training the world model.** The world model is trained on logged $(s_t, a_t, s_{t+1})$ tuples by the JEPA objective applied to consecutive states (so $x = (s_t, a_t)$, $y = s_{t+1}$). The latent $z_t$ absorbs all aspects of $s_{t+1}$ that are not predictable from $(s_t, a_t)$ — environmental stochasticity, partial observability, hidden state.

## 5. Results

This is a position paper. No experiments are reported within it. The empirical content lives in subsequent / contemporary work cited in the proposal:

- BYOL, SimSiam, VICReg, Barlow Twins — non-contrastive self-supervised methods that demonstrate JEPA-style training works without negative pairs.
- I-JEPA (Assran et al. 2023) — image-only JEPA achieving competitive ImageNet linear-probe results without pixel reconstruction.
- V-JEPA (`bardes2023_vjepa`) — video JEPA achieving ~80% Kinetics-400 top-1 with frozen features (the most direct empirical instantiation of the JEPA branch).
- Model-based RL precursors — *World Models* (`ha_schmidhuber2018_world_models`) and *Dreamer* (`hafner2020_dreamer`) supply the empirical basis for Mode-2 planning over learned world models, though both predict in pixel/observation space rather than JEPA latents.

The position paper's quantitative arguments are about *what should not work* (pixel-prediction generative pretraining at internet scale, pure LLMs without a world model) rather than what does — its falsifiable predictions are operationalized only in the follow-on JEPA papers.

## 6. Critique / limitations

The paper is programmatic; large parts of the proposed architecture have no working implementation. In particular:

- The **configurator** is the most under-specified module. LeCun describes it as a system-level task-conditioning controller but does not say how it is trained, what its inputs look like, or how it interacts with the actor/cost split. The functional role overlaps with both prompting in LLMs and goal-conditioning in hierarchical RL, neither of which is referenced as a baseline.
- **Mode-2 planning** is asserted to work by gradient descent on action sequences through the world model. In practice this is brittle when the world model is imperfect (the planner exploits model errors). The paper does not address model-exploitation pathologies, which are well-known in MPC and model-based RL.
- The **non-contrastive anti-collapse mechanisms** (VICReg, EMA) are presented as solved; in fact the theoretical understanding of why they avoid collapse is still incomplete (see §6 of `bardes2023_vjepa`).
- **H-JEPA hierarchy** is presented as obviously beneficial but no hierarchical JEPA was working at the time of writing. Subsequent work (I-JEPA, V-JEPA) has implemented only flat JEPA; a hierarchical variant that matches the abstraction-and-timescale story in the paper does not yet exist at the time of this entry.
- The **critic / intrinsic-cost split** is invoked as the agent's "value system" but the paper does not specify what intrinsic costs should be — i.e., what plays the role of homeostatic drives, novelty bonuses, or empowerment terms. This is exactly the question the active-inference literature (`pezzulo_parr_friston2024_active_inference`) has been pressing on for two decades.
- There is no explicit treatment of **competition between modules**. The configurator is presented as a benevolent dispatcher, not a coalition that has to win bandwidth from rivals. This is a deep divergence from the user's program (see §7).
- The paper's **rejection of LLM-style autoregressive pretraining** is sweeping and, in hindsight, has not aged uniformly well: scaling has produced surprisingly broad capabilities. JEPA's contrastive-free latent prediction may end up *complementary* to autoregression rather than a replacement for it.
- **Short-term memory** appears as a buffer for replay and partial-observability handling but is not given a capacity-limited, selective-encoding character. There is no notion of working-memory bottleneck in the cognitive-neuroscience sense — exactly the property the Recurrent ViT and PRISM exist to model. LeCun treats memory as a tape; the user's program treats it as a strategically allocated, capacity-limited resource.
- The **action-as-latent-variable** trick used at planning time conflates exploration over actions with inference over hidden states, which the active-inference literature (`pezzulo_parr_friston2024_active_inference`) keeps distinct via the expected-free-energy decomposition. LeCun's energy is not decomposed that way; the consequences for exploration are unaddressed.

## 7. Connection to our work

LeCun's program and the user's architectural program (`threads/the_user_architectural_program.md`) share three deep commitments and diverge on three equally deep ones. Spelling out both sides is the point of this entry.

**Shared commitments.**

1. *Latent-space predictive coding.* Both programs reject pixel-level reconstruction as the right pretraining target and commit to predicting in a learned latent space. PRISM v1's feature-PC term (`THESIS.md` §2.11) and the Recurrent ViT's prediction loss are the user's instantiation of this; JEPA is LeCun's.
2. *Hierarchy.* Both commit to a hierarchical predictive stack. H-JEPA's layers operate at progressively coarser spatial/temporal scales; the user's three-layer GridCell-RNN stack with descending conv projections and ascending conv-transpose projections (see §3 of the program thread) implements an equivalent hierarchy with explicit cortex-style anatomy (V1 → V2/V4 → IT).
3. *Variational / active-inference framing.* The user's iterative variational encoder-decoder (§4 of the program thread) explicitly identifies its KL regularizer with Friston's free-energy principle. LeCun's energy-based formulation of the whole architecture is the same idea written in the EBM idiom — minimize a free-energy-like global energy over latents and actions.

**Divergences.**

1. *Contrastive vs competition.* LeCun's anti-collapse machinery is information-theoretic (VICReg / EMA) and treats the question "what makes representations non-degenerate?" as a technical training problem. The user's program treats non-degeneracy as the *consequence* of inter-coalition competition for limited self-attention bandwidth — the `competition-emergent-predictive-coding` thesis (§5 of the program thread). In the user's view, the reason representations specialize is not that we add a covariance penalty but that different hubs are competing for control of the attention map, and specialization is the strategic response. LeCun's framework has no analog of this.
2. *Explicit RL hub vs implicit policy.* LeCun's actor is trained either by Mode-2 distillation or by gradient through the world model. The user's program commits to a separate, full-strength RL hub (the MSI/RL/VAE multi-hub system) whose objective is in genuine tension with the perceptual and reconstructive objectives, and which is the dominant pressure shaping what the world model learns. The published Recurrent ViT and PRISM both train with PPO; this is *not* present in LeCun's six-module architecture in a substantive way.
3. *Strategic prediction error vs sensory prediction error.* In LeCun's account prediction error is sensory — the world model's prediction misses the next state. In the user's reformulation (§5 of the program thread) the more fundamental prediction error is *strategic* — the failure to predict what competing internal coalitions are about to represent. Top-down feedback is opponent modeling. This reframing has no analog in LeCun's proposal and is, in the user's notes, the most important original theoretical contribution of the program.

**Concretely for our published / proposed work.** The Recurrent ViT (2502.10955) and PRISM v1/v2 sit on the JEPA side of the spectrum at the level of self-supervised pretraining (both predict in latent space, both use hierarchical structure) but on the *user-program* side at the level of architecture (explicit recurrent working-memory bottleneck, explicit RL action head, explicit prediction-error map readout). V-JEPA is the cleanest published JEPA baseline; PRISM v2 is the closest published instance of the user's program. The relationship is roughly:

$$
\text{PRISM v2} \approx \text{V-JEPA} + \text{recurrent memory bottleneck} + \text{RL head} + \text{spatial prediction-error map}
$$

Symmetrically:

$$
\text{user's full program} \approx \text{H-JEPA} + \text{multi-hub competition} + \text{Feedback-Transformer integration} + \text{strategic prediction error}
$$

**Specific design decisions LeCun's paper bears on.**

- The *recurrent-state-as-feedback* commitment in the Feedback Transformer (program thread §1) is in tension with H-JEPA's purely feedforward predictor architecture. LeCun's H-JEPA does not have descending feedback from level $\ell+1$ back into level $\ell$ during inference — it predicts top-down only at planning time. The user's program puts this descending feedback *into every forward pass*, anatomically grounded in Weiler et al. 2025's L6 corticocortical pathway.
- The *configurator* role in LeCun's architecture maps onto what the user's program splits among (a) the RL hub conditioning the attention map and (b) the task-dependent reward shaping of the multi-objective system. The user's commitment is that this conditioning is not a separate centralized controller but an emergent property of inter-hub competition.
- The *latent uncertainty variable* $z$ in JEPA is functionally close to the variational posterior over the guide in the user's iterative variational encoder-decoder (program thread §4). Both inject stochasticity to absorb residual unpredictability and both regularize this latent against a prior. The user's formulation is explicitly variational (KL to unit Gaussian + matrix-normal structure over patches); LeCun's is more loosely specified.

**Bottom-line takeaway.** If H-JEPA were extended with a recurrent memory bottleneck at every level, an RL hub competing with the world-model hub for self-attention control, and an explicit prediction-error-map readout, the result would be approximately the user's full architectural program. That this convergence is non-trivial — that two independent research lines arrive at overlapping commitments from very different starting points — is itself an argument for the architectural choices, and a reason to treat LeCun's paper as a *friendly contrast* rather than a competitor.

## 8. Citations to follow

- `assran2023_ijepa` — the image JEPA, principal empirical instantiation alongside V-JEPA.
- `grill2020_byol` — BYOL, the EMA-target trick used by JEPA variants.
- `bardes2022_vicreg` — VICReg variance/covariance/invariance regularization; LeCun's preferred anti-collapse mechanism. Worth adding.
- `kahneman2011_thinking_fast_slow` — System-1/System-2 framing that motivates the Mode-1/Mode-2 split. Background.
- `friston2010_fep_unified_theory` — already in seed; the variational / energy framing LeCun's EBM formulation generalizes.
- `tenenbaum2011_grow_a_mind` — model-based cognition / probabilistic-program account, an alternative path to the same problem.
- `schmidhuber2015_learn_to_think` — already in seed; the coupled-RNN controller/world-model decomposition LeCun's architecture reinvents in places.
- `ha_schmidhuber2018_world_models` — already in seed; the canonical generative world-model demonstration that JEPA aims to supersede with latent prediction.
