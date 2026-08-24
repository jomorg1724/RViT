---
id: schrittwieser2020_muzero
title: "Mastering Atari, Go, chess and shogi by planning with a learned model"
authors:
  - "Schrittwieser, Julian"
  - "Antonoglou, Ioannis"
  - "Hubert, Thomas"
  - "Simonyan, Karen"
  - "Sifre, Laurent"
  - "Schmitt, Simon"
  - "Guez, Arthur"
  - "Lockhart, Edward"
  - "Hassabis, Demis"
  - "Graepel, Thore"
  - "Lillicrap, Timothy"
  - "Silver, David"
year: 2020
venue: "Nature"
doi: "10.1038/s41586-020-03051-4"
arxiv: "1911.08265"
url: "https://www.nature.com/articles/s41586-020-03051-4"
tags:
  - reinforcement-learning
  - planning
  - world-models
  - mcts
  - latent-dynamics
  - deep-learning
concepts:
  - coupled_rnn_world_models
  - hierarchical_predictive_coding
  - world_model_emergence
  - error-gated-update
related:
  - hafner2023_dreamerv3
  - ha_schmidhuber2018_world_models
  - hafner2020_dreamer
  - wayne2018_merlin
  - bardes2023_vjepa
  - lecun2022_path_to_agi
  - banino2018_vector_navigation
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# Mastering Atari, Go, chess and shogi by planning with a learned model

## 1. Abstract

> "Constructing agents with planning capabilities has long been one of the main challenges in the pursuit of artificial intelligence. Tree-based planning methods have enjoyed huge success in challenging domains, such as chess and Go, where a perfect simulator is available. However, in real-world problems the dynamics governing the environment are often complex and unknown. In this work we present the MuZero algorithm which, by combining a tree-based search with a learned model, achieves superhuman performance in a range of challenging and visually complex domains, without any knowledge of their underlying dynamics. MuZero learns a model that, when applied iteratively, predicts the quantities most directly relevant to planning: the reward, the action-selection policy, and the value function. When evaluated on 57 different Atari games — the canonical video game environment for testing AI techniques, in which model-based planning approaches have historically struggled — our new algorithm achieved a new state of the art. When evaluated on Go, chess and shogi, without any knowledge of the game rules, MuZero matched the superhuman performance of the AlphaZero algorithm that was supplied with the game rules." (Schrittwieser et al. 2020, arXiv:1911.08265 v2, abstract.)

## 2. Why this matters for us

MuZero is the *most consequential demonstration* of a fundamentally different approach to world modeling: rather than predicting *observations* (Dreamer, MERLIN, JEPA), MuZero learns a *value-equivalent* latent dynamics model that predicts only the quantities relevant to planning (reward, value, policy). For the user's program, this is the most direct architectural contrast: the user's program inherits the *predictive-memory* commitment but MuZero shows that the predictive target can be much *narrower* than next-observation. The architectural implication is that *what* a world model predicts is a design choice with major consequences: pixel-level (DreamerV3, MERLIN) wastes capacity but provides rich training signal; latent-level (V-JEPA, I-JEPA) is more focused but harder to interpret; value-equivalent (MuZero) is the most narrowly scoped but only useful when reward signals are dense and well-defined. For the user's program, the MuZero alternative is *worth considering* as the design extreme: if the user's program ultimately commits to RL training, the value-equivalent abstraction may be appropriate for the deepest memory compartment's predictive role.

## 3. Key claims

1. A learned model that predicts *only reward/value/policy* (not pixels or full observations) suffices for planning in deep RL — value-equivalent abstraction is the right inductive bias.
2. MuZero *unifies* model-free Atari and model-based perfect-information game settings under one algorithm.
3. *Matches AlphaZero* on Go/chess/shogi *without access to rules or a simulator* — the model learns the rules implicitly.
4. *New SOTA on Atari 57* at the time of publication.
5. *Latent dynamics need not reconstruct observations* to be useful for planning — a substantive computational claim.
6. *Value-equivalent abstraction* is the right inductive bias for planning models — the model only needs to be predictive of plan-relevant quantities.
7. The architecture is *MCTS-in-latent-space*: planning operates in the learned latent representation, not the original observation space.
8. *No exploration mechanism beyond Dirichlet-noise prior*; relies on the search itself for exploration — this is a key limitation on hard-exploration tasks.

## 4. Methods

MuZero learns three networks. (i) A *representation function* $h$ that maps observations to a latent state $s_0$. (ii) A *dynamics function* $g$ that, given $(s_k, a_{k+1})$, produces $(s_{k+1}, r_{k+1})$ — the next latent and the immediate reward. (iii) A *prediction function* $f$ that produces (policy $p_k$, value $v_k$) from any latent $s_k$. The model is unrolled $K = 5$ steps during training to match observed (action, reward, value-target, policy-target) tuples; targets come from MCTS at the visited states (improved policies) and from n-step returns (improved values). At decision time, *MCTS with PUCT* is performed in the learned latent space (no environment queries) using priors from $p$ and bootstrap values from $v$. The model is trained end-to-end with *no reconstruction loss*; gradients flow only through the value/policy/reward heads. Reanalyze (later version) re-runs MCTS on stored experience to improve targets for off-policy learning. The architecture is large convolutional networks (ResNet-style for $h$, transformer-like for $g$ and $f$ in some implementations), trained for thousands of TPU-days.

## 5. Results

Headline empirical results:

- **Atari 57:** mean human-normalized score 4999%, median 2041% (200M frames) — state-of-the-art at the time of publication.
- **Outperforms R2D2** (the prior model-free SOTA) on 42/57 Atari games.
- **Go (19×19):** matches AlphaZero Elo (~5185) after 1M training steps *without rules* — the model learns rules implicitly via the search-and-train loop.
- **Chess:** 12-13 hours TPU training to surpass Stockfish-level play, matching AlphaZero performance.
- **Shogi:** surpasses Elmo Elo within 8 hours, matches AlphaZero.
- **MuZero Reanalyze:** 731% median Atari score with only 200 million frames re-used efficiently — a sample-efficient variant.
- **Search depth:** with only 50 simulations per move, retains ~90% of full-search Elo — even shallow MCTS is highly effective in the learned latent space.
- **Even a depth-1 (no search) MuZero** matches a model-free baseline; depth grows value of planning monotonically, with diminishing returns.

## 6. Critique / limitations

MuZero is impressive but has substantial limitations.

- **Compute requirements enormous** (thousands of TPU-days); inaccessible to most academic labs and not affordable for typical research budgets.
- **Latent dynamics provide no interpretability**; predicting only value/reward limits transfer to new tasks/rewards. A MuZero-trained model is largely useless if the reward function changes — the latent abstraction is *value-tuned* to the original reward.
- **Designed for deterministic environments**; performs poorly under stochastic dynamics without extensions (Stochastic MuZero, Antonoglou et al. 2022).
- **Continuous action spaces require Sampled MuZero variant** (Hubert et al. 2021); not native to the original algorithm.
- **Off-policy data reuse is limited**; sample efficiency on Atari still poor relative to EfficientZero (Ye et al. 2021), which adds reconstruction loss and self-supervised representation learning.
- **MCTS planning cost grows with action space**; impractical for large discrete or combinatorial actions.
- **Hyperparameters (Dirichlet noise, $c_{\text{PUCT}}$, unroll length) are sensitive and per-domain tuned** — the apparent algorithmic generality requires careful per-domain configuration.
- **No mechanism for exploration beyond Dirichlet-noise prior**; struggles on hard-exploration Atari (Montezuma, Pitfall, Private Eye).

## 7. Connection to our work

MuZero is one of the key architectural contrast papers for the user's program because it represents the *opposite extreme* in world-model design space: a tightly focused, value-equivalent latent model rather than a broad reconstruction-driven model.

**Touchpoint 1: value-equivalent abstraction as the architectural extreme.** MuZero's value-equivalent abstraction — predicting only reward / value / policy — is the *minimal* design for a planning-capable world model. The user's program lies elsewhere on the spectrum: the user's world model is expected to emerge from broader competition pressures (reconstruction, V-JEPA-style prediction, RL reward) and to support *flexible* downstream use beyond planning. The architectural contrast clarifies the user's commitment: the user's program prioritizes *flexibility* over *task-specific efficiency*. MuZero is more efficient at the specific planning task it was trained for; the user's program targets representations that are useful across many tasks because they were not value-tuned to any one.

**Touchpoint 2: MCTS-in-latent-space as a planning architectural pattern.** MuZero's MCTS operating in the learned latent space — *not* in the original observation space — is a substantive design lesson the user's program can adopt. If the user's program eventually adds explicit planning, that planning should operate in the *latent space of the deepest memory compartment*, not in the pixel space. This is the natural architectural choice given the user's multi-compartment hierarchy: the deepest compartment is the appropriate level of abstraction for planning, and a MuZero-style MCTS or value-iteration would operate there. The architectural pattern is *abstract-state planning*, with MuZero as the canonical demonstration.

**Touchpoint 3: gradient flow through search — implications for the user's iterative VAE.** MuZero's training has gradients flowing through the *MCTS-derived policy improvements* — the search itself becomes part of the training signal. This is structurally analogous to the user's [iterative_variational_encoder_decoder](../concepts/iterative_variational_encoder_decoder.md): the iterative refinement of the encoder's guide is itself part of the gradient signal that trains the encoder. The architectural lesson: *iterative computation should be part of the training-time inference*, not separated from it. The user's iterative VAE inherits this lesson.

**Touchpoint 4: planning depth as a learned-vs-fixed hyperparameter.** MuZero's result that even depth-1 search is useful, with planning value increasing monotonically with depth, suggests an architectural commitment: the user's program should support *variable planning depth* at inference time, with the depth adapted to the task. This connects to [banino2021_pondernet](banino2021_pondernet.md): the user's program should support adaptive computation time, with deeper planning for harder problems and shallow planning for easier ones. The architectural commitment is to *flexible inference-time computation*, with MuZero providing the empirical evidence that depth matters.

**Touchpoint 5: MuZero's failure on hard-exploration tasks — the user's competition-driven exploration opportunity.** MuZero struggles on hard-exploration tasks because its only exploration mechanism is Dirichlet noise on the policy prior. The user's program may have an architectural advantage here: *inter-hub competition* can drive exploration via the disagreement among hubs about what the optimal next action is. When hubs disagree, the system explores; when they agree, the system exploits. This is a *competition-driven exploration* mechanism that MuZero lacks. Empirically demonstrating that the user's multi-hub system outperforms MuZero on hard-exploration tasks (Montezuma, Pitfall) would be a substantial validation of the competition framework.

**Touchpoint 6: latent dynamics need not reconstruct observations — convergence with JEPA.** MuZero's commitment that latent dynamics need not reconstruct observations *to be useful for planning* converges with the JEPA program's claim that latent prediction is superior to pixel prediction. The user's program inherits this commitment: the architecture should not require pixel-level reconstruction to develop useful representations. The iterative VAE, if configured to predict in latent space rather than at the pixel level, is in the JEPA / MuZero lineage architecturally.

**Touchpoint 7: rules-from-experience — the architectural analog for the user's program.** MuZero learns the rules of chess / Go *implicitly* from training on game outcomes — it never receives an explicit rule encoding. This is a strong demonstration that *implicit rule learning* is achievable in deep RL with the right architecture. For the user's program, the architectural implication: the user's multi-hub system should be capable of *implicitly learning task structure* (transition rules, reward structure, latent variables) from the joint signal of its multiple losses, without any explicit task encoding. This is the user's program's [world_model_emergence](../concepts/world_model_emergence.md) thesis at its strongest.

**Touchpoint 8: compute cost — the dose-of-realism for the user's program.** MuZero's compute cost (thousands of TPU-days) is a sobering reminder that the user's program will face substantial training-cost challenges if it aspires to match modern RL agents. The user's architectural commitments (multi-compartment memory, Feedback Transformer, multi-hub competition) all add parameters and training cost. Realistic expectations: the user's program will need substantial compute scaling before it can match DreamerV3 / MuZero on full benchmarks. The architectural commitment to *efficient* training (gradient flow through all components from step zero, no warm-up phases) — already adopted in RViT+ ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md) Refinement 3) — is important to control this cost.

## 8. Citations to follow

- `ye2021_efficientzero_neurips` — *NeurIPS* — Mastering Atari Games with Limited Data (EfficientZero); the sample-efficient successor. Not in seed.
- `antonoglou2022_stochastic_muzero_iclr` — *ICLR* — planning in stochastic environments with a learned model (Stochastic MuZero). Not in seed.
- `hubert2021_sampled_muzero_icml` — *ICML* — learning and planning in complex action spaces (Sampled MuZero); continuous-action extension. Not in seed.
- `schrittwieser2021_muzero_unplugged_neurips` — *NeurIPS* — online and offline RL by planning with a learned model (MuZero Unplugged). Not in seed.
- `hamrick2021_role_of_planning_iclr` — *ICLR* — on the role of planning in model-based deep RL; the analytical follow-up. Not in seed.
- `grill2020_mcts_regularized_policy_icml` — *ICML* — Monte-Carlo tree search as regularized policy optimization; the theoretical interpretation. Not in seed.
- `mandhane2022_muzero_vp9` — MuZero with self-competition for VP9 video compression; the real-world application. Not in seed.
- `fawzi2022_alphatensor_nature` — *Nature* — discovering faster matrix multiplication algorithms with RL (AlphaTensor). Not in seed.
- [hafner2023_dreamerv3](hafner2023_dreamerv3.md) — DreamerV3; the contrast architecture with pixel-reconstruction world model. In seed.
- `hessel2021_muesli_icml` — *ICML* — Muesli: combining improvements in policy optimization; the modern alternative. Not in seed.
- `vanhasselt2019_parametric_models_neurips` — *NeurIPS* — when to use parametric models in RL; the critical context. Not in seed.
- [ha_schmidhuber2018_world_models](ha_schmidhuber2018_world_models.md) — the foundational world-models paper. In seed.
- [hafner2020_dreamer](hafner2020_dreamer.md) — Dreamer V1; the predecessor in the Dreamer lineage. In seed.
- [wayne2018_merlin](wayne2018_merlin.md) — MERLIN; the contrast architecture with predictive memory but no MCTS. In seed.
- [bardes2023_vjepa](bardes2023_vjepa.md) — V-JEPA; the latent-prediction architectural sibling. In seed.
- [lecun2022_path_to_agi](lecun2022_path_to_agi.md) — the JEPA position paper. In seed.
