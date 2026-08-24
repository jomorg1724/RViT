---
id: hafner2023_dreamerv3
title: "Mastering Diverse Domains through World Models"
authors:
  - "Hafner, Danijar"
  - "Pasukonis, Jurgis"
  - "Ba, Jimmy"
  - "Lillicrap, Timothy"
year: 2023
venue: "arXiv preprint (subsequently published in Nature 2025)"
doi: "10.48550/arXiv.2301.04104"
arxiv: "2301.04104"
url: "https://arxiv.org/abs/2301.04104"
tags:
  - world-models
  - reinforcement-learning
  - imagination
  - rssm
  - generalization
  - deep-learning
concepts:
  - coupled_rnn_world_models
  - hierarchical_predictive_coding
  - world_model_emergence
  - multi_compartmental_memory
  - slow_fast_recurrence
related:
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - bardes2023_vjepa
  - assran2023_ijepa
  - schrittwieser2020_muzero
  - wayne2018_merlin
  - banino2018_vector_navigation
  - lecun2022_path_to_agi
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# Mastering Diverse Domains through World Models

## 1. Abstract

> "Developing a general algorithm that learns to solve tasks across a wide range of applications has been a fundamental challenge in artificial intelligence. Although current reinforcement learning algorithms can be readily applied to tasks similar to what they have been developed for, configuring them for new application domains requires significant human expertise and experimentation. We present DreamerV3, a general algorithm that outperforms specialized methods across over 150 diverse tasks, with a single configuration. Dreamer learns a model of the environment and improves its behavior by imagining future scenarios. Robustness techniques based on normalization, balancing, and transformations enable stable learning across domains. Applied out of the box, Dreamer is the first algorithm to collect diamonds in Minecraft from scratch without human data or curricula. This achievement has been posed as a significant challenge in artificial intelligence that requires exploring farsighted strategies from pixels and sparse rewards in an open world. Our work allows solving challenging control problems without extensive experimentation, making reinforcement learning broadly applicable." (Hafner, Pasukonis, Ba & Lillicrap 2023, arXiv:2301.04104, abstract.)

## 2. Why this matters for us

DreamerV3 is the *modern standard* for world-model-based reinforcement learning — a single set of hyperparameters that solves >150 tasks across 8 domains, with the headline achievement of collecting diamonds in Minecraft from scratch (a task that requires exploring farsighted strategies under sparse rewards from raw pixels). For the user's program, DreamerV3 is the *principal explicit-world-model contrast architecture* to the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis: DreamerV3 trains a world model *explicitly* (via reconstruction loss) and uses it for imagination-based actor-critic; the user's program predicts that a world model should *emerge* from inter-hub competition *without* an explicit world-model objective. DreamerV3 is therefore the *baseline to beat* for the user's competition-emergent-PC thesis: if the user's multi-hub system can match DreamerV3's world-model quality without ever being told to learn a world model, that is a substantial theoretical result. The paper also matters for the architectural details: the RSSM (Recurrent State-Space Model) is a [coupled_rnn_world_models](../concepts/coupled_rnn_world_models.md) instantiation that the user's [slow_fast_recurrence](../concepts/slow_fast_recurrence.md) commitment is in dialogue with.

## 3. Key claims

1. A single fixed hyperparameter configuration solves >150 tasks across 8 domains (Atari, ProcGen, DMC, BSuite, Crafter, Minecraft, Atari 100k, Atari 200M) — demonstrating algorithmic generality.
2. *First algorithm to collect diamonds in Minecraft from scratch* (no demos / no curricula) — a notable open-world AI milestone.
3. *Symlog prediction, free bits, KL balancing, percentile return scaling* enable stable learning across domains where prior methods required per-domain tuning.
4. *World-model architecture (RSSM) scales monotonically* with parameter count; larger models are more sample-efficient on the same compute budget.
5. *Imagination-based actor-critic* with two-hot encoded returns avoids reward-scale tuning — a substantial robustness improvement.
6. Outperforms specialized SOTA baselines (IMPALA, PPO, SAC, Rainbow, MuZero) under matched budgets across most tasks.
7. *Stochastic + deterministic recurrent state* is the architectural sweet spot for video-based world modeling — discrete stochastic latents add expressivity without sacrificing stability.
8. *Engineering choices* (LayerNorm everywhere, unimix categorical latents, two-hot critic regression) are individually small but collectively decisive for cross-domain robustness.

## 4. Methods

DreamerV3 trains a Recurrent State-Space Model (RSSM) with discrete latent codes. The RSSM has a *deterministic-stochastic* hidden state: a GRU-like deterministic component carries long-range context, and a categorical stochastic component captures uncertainty. A CNN encoder maps raw observations into the stochastic component; a CNN decoder reconstructs observations as a reconstruction-loss training signal. Three additional prediction heads predict reward, episode continuation, and the next stochastic state (the dynamics model). At training time, the world model is rolled out in *imagination* for ~16 steps starting from a sampled real state; the actor and critic are trained on these imagined trajectories using lambda returns. The model improvements over DreamerV2 are engineering-level: (i) *symlog* transforms on rewards/values to handle the wide dynamic range across domains, (ii) *two-hot categorical regression* for the critic (instead of MSE) to handle multi-modal value distributions, (iii) *free bits* in the dynamics KL to prevent posterior collapse, (iv) *unimix categorical latents* (mixing uniform with categorical) for stable gradient flow, (v) *percentile return normalization* to make return scales consistent across domains, (vi) *LayerNorm throughout* the architecture. Same network sizes (XS, S, M, L, XL) and one hyperparameter set are used for every benchmark.

## 5. Results

Headline quantitative results:

- **Atari100k:** 125% human-normalized median (XL model) vs ~50% for IRIS/EfficientZero in matched regimes.
- **Crafter:** 14.77 reward score (single run, 1M steps), exceeding human and prior RL baselines.
- **DMC Proprio:** 783 mean return at 500K steps.
- **DMC Vision:** ~728 mean return at 1M steps.
- **Atari 200M:** surpasses Rainbow median; comparable to MuZero with far less compute.
- **Minecraft:** *first algorithm to obtain a diamond from scratch* within 100M environment steps.
- **BSuite, ProcGen** also solved with the same hyperparameters.
- **Scaling law:** increasing model size monotonically improves both final score and data efficiency on Crafter; large models are more sample-efficient at fixed environment-step budgets.

## 6. Critique / limitations

DreamerV3's headline claims need careful reading.

- **World model still falls short on long-horizon partial-observability tasks** (e.g., MERLIN-style memory tasks); the RSSM's recurrent state is not optimized for long-range retrieval. [wayne2018_merlin](wayne2018_merlin.md) outperforms DreamerV3 on memory-intensive tasks.
- **Pixel-reconstruction objective wastes capacity on irrelevant background**; performance degrades with visual distractors. The reconstruction-loss-driven world model spends capacity on visual minutiae that may not be task-relevant.
- **Compute cost remains substantial** (XL model ~16 GPU-days per Atari run); not affordable for typical academic labs.
- **"Single hyperparameter set" claim hides domain-specific action/observation wrappers and reward clipping defaults** — the apparent generality requires careful preprocessing per domain.
- **Imagination rollouts of 16 steps still limit long-horizon planning** vs tree search (MuZero's planning depth is unbounded in principle).
- **Stochastic discrete latents under-explored vs continuous**; mode collapse can occur on simple environments.
- **Minecraft diamond result relies on a specific block-action space** and dense shaping signals via item-collection rewards — the apparent "sparse reward" framing is partly cosmetic.
- **Reproducibility:** original JAX code had memory-management issues raised in GitHub issues, requiring official re-release.

## 7. Connection to our work

DreamerV3 is one of the most architecturally consequential modern world-model papers for the user's program because it provides both the *baseline to beat* and the *architectural reference* for explicit world-model training.

**Touchpoint 1: DreamerV3 as the principal contrast architecture to world_model_emergence.** DreamerV3 trains a world model *explicitly* via reconstruction loss; the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis predicts that a world model should *emerge* from inter-hub competition without an explicit world-model objective. DreamerV3 is therefore the *baseline to beat*: the user's multi-hub system must produce comparable forward-prediction quality on standard benchmarks (or at least standardized world-model-quality probes) *without* training on a world-model objective. The architectural contrast is sharp: DreamerV3's world model is built; the user's emerges. Empirically demonstrating this would be a major theoretical contribution.

**Touchpoint 2: RSSM as the architectural reference for coupled-RNN world models.** The Recurrent State-Space Model with deterministic + stochastic state is a textbook [coupled_rnn_world_models](../concepts/coupled_rnn_world_models.md) instantiation: the deterministic GRU-like component carries long-range context, the stochastic component captures uncertainty. This decomposition is structurally analogous to the user's [slow_fast_recurrence](../concepts/slow_fast_recurrence.md) commitment: a deterministic component that integrates over long timescales (the user's $M_{slow}$) and a faster stochastic component (the user's $M_{fast}$). DreamerV3 demonstrates that this decomposition *works at scale* — across 150+ tasks. The user's program inherits the architectural lesson: deterministic + stochastic state, multi-timescale, with explicit recurrence is a robust design pattern.

**Touchpoint 3: imagination-based actor-critic as the architectural template for the user's planning hub.** DreamerV3's training of policy and value on *imagined* trajectories (rollouts in the world model) is the architectural template for the user's planning hub: a hub that produces forward rollouts of the system's internal state and trains downstream control on those rollouts. The user's program can adopt this design: the slow memory compartment, paired with a learned forward-dynamics model, supports imagination rollouts; a separate actor-critic learns from the imagined trajectories. This is one route the user's multi-hub program can adopt for RL training.

**Touchpoint 4: pixel-reconstruction limitation — the JEPA / V-JEPA contrast.** DreamerV3's pixel-reconstruction objective is the principal limitation Yann LeCun's JEPA program ([lecun2022_path_to_agi](lecun2022_path_to_agi.md), [bardes2023_vjepa](bardes2023_vjepa.md), [assran2023_ijepa](assran2023_ijepa.md)) responds to: pixel prediction wastes capacity on irrelevant detail. The user's program inherits this critique: predicting in *latent* space rather than pixel space is the architecturally superior choice. The user's iterative VAE should be configured to predict in the latent space of its own encoder, not at the pixel level, to avoid the DreamerV3 pixel-capacity problem.

**Touchpoint 5: scaling-law evidence — model-size-matters argument.** DreamerV3's monotonic scaling — larger models are more sample-efficient — is empirical evidence that the user's program should not be conservative on model size. The architectural commitment to multi-compartment memory ([multi_compartmental_memory](../concepts/multi_compartmental_memory.md)) implies additional parameters; DreamerV3's scaling evidence licenses this investment. The user's reference RViT+ implementation (~1.36M params after refinements) is small by modern world-model standards; substantial scaling-up may be needed before the user's program produces DreamerV3-comparable performance.

**Touchpoint 6: DreamerV3's failure on long-horizon memory tasks — the user's opportunity.** DreamerV3 underperforms MERLIN-style architectures on long-horizon memory tasks. This is *exactly* the regime the user's program is optimized for — the multi-compartment memory hierarchy with slow-fast separation is precisely the architectural commitment that addresses long-horizon partial observability. The user's program has an architectural advantage that DreamerV3 lacks: explicit multi-timescale memory. The empirical demonstration of this advantage on the same benchmarks DreamerV3 underperforms on would be a strong validation of the user's multi-compartment commitment.

**Touchpoint 7: minecraft diamond as a long-horizon emergent-attention benchmark.** DreamerV3's headline result — Minecraft diamond from scratch — is a *long-horizon, sparse-reward, multi-stage* task that requires sustained attention to subgoals over thousands of timesteps. The user's program should be evaluated on similar long-horizon benchmarks; if the user's multi-hub competition produces sustained sub-goal-attention without DreamerV3's pixel-reconstruction objective, that would be a strong demonstration that competition can scaffold long-horizon attention. This is a concrete experimental target for the user's program.

**Touchpoint 8: engineering robustness lessons — symlog, free bits, LayerNorm.** DreamerV3's engineering improvements (symlog, free bits, two-hot critic, LayerNorm) are training-stability lessons the user's program should adopt. The user's recent RViT+ runs (run 5 collapse, run 6 surgical fix) demonstrate that engineering robustness matters; DreamerV3's lessons can be directly applied: LayerNorm at strategic locations, free bits in the KL term of the iterative VAE, symlog for reward/value heads if added to the user's program. These are *low-cost wins* that improve training reliability.

## 8. Citations to follow

- `hansen2024_tdmpc2_iclr` — *ICLR* — TD-MPC2: scalable, robust world models for continuous control; the contemporaneous alternative. Not in seed.
- `micheli2023_iris_iclr` — *ICLR* — "Transformers are sample-efficient world models" (IRIS); the transformer-based alternative. Not in seed.
- `robine2023_transformer_world_models_iclr` — *ICLR* — transformer-based world models with 100k interactions. Not in seed.
- `zhang2023_storm_neurips` — *NeurIPS* — STORM: efficient stochastic transformer-based world models for RL. Not in seed.
- `hafner2025_nature_dreamer_v3` — *Nature* — the peer-reviewed Nature version of DreamerV3 (2025). Not in seed.
- `wu2023_daydreamer_corl` — *CoRL* — DreamerV3 for physical robot learning. Not in seed.
- `alonso2024_diamond_neurips` — *NeurIPS* — DIAMOND: diffusion world models. Not in seed.
- `bruce2024_genie_icml` — *ICML* — Genie: generative interactive environments. Not in seed.
- [hafner2020_dreamer](hafner2020_dreamer.md) — DreamerV1 (or V2); the predecessor. In seed.
- [ha_schmidhuber2018_world_models](ha_schmidhuber2018_world_models.md) — the foundational world-models paper. In seed.
- [bardes2023_vjepa](bardes2023_vjepa.md) — V-JEPA, the JEPA-based contrast. In seed.
- [assran2023_ijepa](assran2023_ijepa.md) — I-JEPA, the image-side JEPA contrast. In seed.
- [schrittwieser2020_muzero](schrittwieser2020_muzero.md) — MuZero; the planning-with-learned-model alternative. In seed.
- [wayne2018_merlin](wayne2018_merlin.md) — MERLIN; the memory-augmented agent that outperforms DreamerV3 on memory tasks. In seed.
- [lecun2022_path_to_agi](lecun2022_path_to_agi.md) — the JEPA position paper that critiques reconstruction-based world models. In seed.
