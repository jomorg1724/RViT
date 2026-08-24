---
id: wayne2018_merlin
title: "Unsupervised Predictive Memory in a Goal-Directed Agent (MERLIN)"
authors:
  - "Wayne, Greg"
  - "Hung, Chia-Chun"
  - "Amos, David"
  - "Mirza, Mehdi"
  - "Ahuja, Arun"
  - "Grabska-Barwinska, Agnieszka"
  - "Rae, Jack"
  - "Mirowski, Piotr"
  - "Leibo, Joel Z."
  - "Santoro, Adam"
  - "Gemici, Mevlana"
  - "Reynolds, Malcolm"
  - "Harley, Tim"
  - "Abramson, Josh"
  - "Mohamed, Shakir"
  - "Rezende, Danilo"
  - "Saxton, David"
  - "Cain, Adam"
  - "Hillier, Chloe"
  - "Silver, David"
  - "Kavukcuoglu, Koray"
  - "Botvinick, Matt"
  - "Hassabis, Demis"
  - "Lillicrap, Timothy"
year: 2018
venue: "arXiv preprint (never peer-reviewed)"
doi: "10.48550/arXiv.1803.10760"
arxiv: "1803.10760"
url: "https://arxiv.org/abs/1803.10760"
tags:
  - reinforcement-learning
  - memory
  - predictive-coding
  - external-memory
  - hippocampus
  - partial-observability
concepts:
  - coupled_rnn_world_models
  - hierarchical_predictive_coding
  - multi_compartmental_memory
  - error-gated-update
  - top-down-feedback
related:
  - hafner2023_dreamerv3
  - ha_schmidhuber2018_world_models
  - whittington2020_tem
  - lisman_grace2005_hippocampal_vta
  - banino2018_vector_navigation
  - schrittwieser2020_muzero
  - bardes2023_vjepa
  - stachenfeld2017_predictive_map
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# Unsupervised Predictive Memory in a Goal-Directed Agent (MERLIN)

## 1. Abstract

> "Animals execute goal-directed behaviours despite the limited range and scope of their sensors. To cope, they explore environments and store memories maintaining estimates of important information that is not presently available. Recently, progress has been made with artificial intelligence (AI) agents that learn to perform tasks from sensory input, even at a human level, by merging reinforcement learning (RL) algorithms with deep neural networks, and the excitement surrounding these results has led to the pursuit of related ideas as explanations of non-human animal learning. However, we demonstrate that contemporary RL algorithms struggle to solve simple tasks when enough information is concealed from the sensors of the agent, a property called \"partial observability\". An obvious requirement for handling partially observed tasks is access to extensive memory, but we show memory is not enough; it is critical that the right information be stored in the right format. We develop a model, the Memory, RL, and Inference Network (MERLIN), in which memory formation is guided by a process of predictive modeling. MERLIN facilitates the solution of tasks in 3D virtual reality environments for which partial observability is severe and memories must be maintained over long durations. Our model demonstrates a single learning agent architecture that can solve canonical behavioural tasks in psychology and neurobiology without strong simplifying assumptions about the dimensionality of sensory input or the duration of experiences." (Wayne et al. 2018, arXiv:1803.10760, abstract.)

## 2. Why this matters for us

MERLIN is the *deepest existing demonstration* that *what is stored in memory matters more than capacity* — adding memory to a deep RL agent is not enough; the memory must be *shaped by a predictive objective* for the agent to use it effectively. For the user's program, this is the *load-bearing biological-AI synthesis paper* that demonstrates how to combine RL with predictive memory in a single architecture. MERLIN is also one of the cleanest illustrations of an architectural principle the user's program inherits: *unsupervised predictive losses* — not just reward — should shape the memory's contents. The agent's memory is written by a process that includes *predicting future observations*, not just predicting future reward; this ensures the memory stores information that is useful for the *world model* (and thereby downstream RL) rather than only information that is immediately reward-relevant. For the user's program, this licenses the architectural commitment to *auxiliary unsupervised losses* alongside primary task losses — a commitment central to the [multi_hub_multi_objective_system](../concepts/multi_hub_multi_objective_system.md) framework. MERLIN also explicitly maps onto hippocampal-cortical memory theories (Tulving's episodic memory, complementary learning systems), giving the architectural design biological warrant.

## 3. Key claims

1. *Standard RL with LSTM fails* under severe partial observability *even with adequate memory size* — capacity is not the bottleneck.
2. *What is stored in memory matters as much as how much can be stored* — the memory's *contents* must be shaped by an objective that promotes task-relevant information storage.
3. A *predictive (unsupervised) auxiliary objective* shapes memory writes that are useful for control — reconstruction and future-observation prediction biases the memory toward predictive content.
4. A *differentiable read-head over a large external memory* ("Memory-Based Predictor") plus an LSTM controller enables solving classical psychology / neurobio tasks.
5. The architecture maps onto *hippocampal/cortical memory theories* (Tulving's episodic memory, complementary learning systems by McClelland & O'Reilly).
6. Generalizes across navigation, memory-arena, latent-learning, and episodic-recall tasks within a single agent — a substantial multi-task capability.
7. Memory writes are *append-only*; the memory grows monotonically and the read mechanism (attention-based) retrieves relevant past content.
8. The agent shows *Tulving-style what/where/when representations* in qualitative analysis — the architecture spontaneously develops biological-memory-like organization.

## 4. Methods

MERLIN combines four major components. (i) A *variational encoder* that compresses each timestep's observation, reward, and previous action into a latent state $z_t$ via amortized variational inference. (ii) A *Memory-Based Predictor (MBP)* that performs key-value reads from a large slot-based external memory and predicts future returns and observations via a generative model; the MBP defines a forward dynamics model in the latent space. (iii) A *policy network* that consumes the latents and memory reads and is trained with an off-policy actor-critic (Retrace-style importance correction). (iv) An *unsupervised reconstruction + KL loss* for the latent $z$, which is the critical auxiliary signal — it biases the encoder and (via the MBP's read keys) the memory to store predictively-useful information. Memory is written by appending the latent $z_t$ each step; memory grows monotonically over an episode. Critically, *gradients from the prediction loss flow back into the encoder and into the choice of read keys*, biasing memory to encode predictively useful information rather than reward-relevant only. The architecture is trained with distributed actors (hundreds of parallel rollouts) for many environment steps.

## 5. Results

Key empirical anchors:

- **Memory Suite (13 tasks in DM Lab + bespoke):** MERLIN reaches near-human or above-human scores while LSTM-A3C baselines fail (>50% gap on most tasks).
- **Goal Navigation:** with random goal locations, MERLIN reaches ~95% optimal returns vs ~30-40% for LSTM-A3C.
- **Latent learning task:** MERLIN successfully transfers maps learned in a reward-free exploration phase to a test phase; baseline LSTM agents do not — directly demonstrating the value of unsupervised memory shaping.
- **Episodic recall task:** MERLIN recalls a probe image after >100 s of distractor frames at >90% accuracy — long-horizon retrieval.
- **Sample efficiency:** MERLIN reaches asymptote in approximately 2-3× fewer environment steps than LSTM-A3C on most memory tasks.
- **Qualitative neural analysis:** memory contents and read patterns show what/where/when separability matching Tulving's episodic-memory theory.
- **Robustness across partial-observability regimes:** performance improvements relative to LSTM-A3C *grow* as partial observability worsens (longer occlusion windows, larger memory horizons).

## 6. Critique / limitations

MERLIN is influential but has substantial limitations.

- **Architecture is highly complex**; many moving parts (MBP, policy, value, prior/posterior, retrieval weights) with no public reference implementation — reproducibility has been a persistent problem.
- **Compute-heavy:** 100s of distributed actors, weeks of training on the original setup; the architecture is not affordable for typical academic labs.
- **"Single architecture solves many tasks" claim hides per-task tuning** of memory size and reward shaping; the apparent generality required careful per-task engineering.
- **Predictive loss is reconstruction-based** — degrades with high-dimensional or distractor-rich observations, in line with the JEPA critique ([lecun2022_path_to_agi](lecun2022_path_to_agi.md)).
- **No formal benchmark comparison against simpler baselines** such as R2D2 (Kapturowski et al. 2019) or transformer-XL agents (Parisotto et al. 2020) which appeared later and may match MERLIN with simpler architectures.
- **Never peer-reviewed**; remains an arXiv tech report — limited formal scrutiny relative to its influence.
- **Memory is monotonically growing (write-only)**, creating O(T) cost; a pruning / consolidation policy is not learned.
- **Theoretical interpretation as a model of hippocampus is suggestive but lacks rigorous neural alignment metrics** — the biological-model framing is somewhat post-hoc.

## 7. Connection to our work

MERLIN is one of the most consequential architectural references for the user's program because it instantiates several of the user's most-load-bearing commitments in a working RL agent.

**Touchpoint 1: unsupervised predictive auxiliary loss shapes memory — the multi-hub multi-objective principle.** MERLIN's central insight — that the memory contents are shaped by an *auxiliary predictive loss* on top of the primary RL objective — is the cleanest existing demonstration of the user's [multi_hub_multi_objective_system](../concepts/multi_hub_multi_objective_system.md) commitment. The user's program inherits this principle: each hub has its own loss (RL, VAE reconstruction, V-JEPA-style prediction), and the *joint* training across multiple losses produces representations richer than any single loss alone. MERLIN demonstrates this works for RL + reconstruction; the user's program generalizes to RL + reconstruction + V-JEPA-style + competition.

**Touchpoint 2: predictive memory as the architectural target.** MERLIN's MBP is a *predictive* memory: it stores latents shaped by future-observation prediction. The user's program's deepest memory compartment should play an analogous role: hold representations that support *forward prediction* of the system's internal state ([world_model_emergence](../concepts/world_model_emergence.md) thesis). MERLIN's architecture is the constructive evidence that this commitment is achievable in deep RL agents — and the empirical evidence that it produces substantial benefits over standard RL+memory architectures.

**Touchpoint 3: differentiable read-head over external memory — Feedback Transformer analog.** MERLIN's attention-based memory reads (differentiable key-value attention over the memory slots) is structurally analogous to the user's Feedback Transformer central self-attention. In MERLIN, the controller queries the memory via attention; in the user's architecture, hubs query each other via central self-attention. The architectural homology is deep: MERLIN's memory is the *external* analog of the user's *distributed-across-hubs* memory, and the attention-based read mechanism is shared. The user's program inherits the architectural pattern: differentiable attention over a stored representation supports flexible read-out of past content.

**Touchpoint 4: partial-observability tasks as the key empirical regime.** MERLIN's principal demonstrated advantage over LSTM-A3C is in *severe partial-observability* tasks — exactly the regime the user's program is engineered for. The user's recurrent ViT and PRISM are evaluated on change detection (a partial-observability task: the system must store the previous scene to compare against the current scene). The user's program should be evaluated on MERLIN-style benchmarks (DM Lab Memory Suite or analogs) to demonstrate that the multi-compartment memory hierarchy outperforms standard recurrent baselines under partial observability. This is a concrete experimental program.

**Touchpoint 5: episodic-memory mapping — Tulving's what/where/when in the user's hubs.** MERLIN spontaneously develops what/where/when separability in its memory contents — the Tulving-style episodic memory organization. The user's architecture should produce analogous separability: the multi-compartment memory's shallow compartment encodes *what* (perceptual content), deeper compartments encode *where* (spatial/relational context) and *when* (temporal context). The architectural prediction: probing the user's compartments should reveal Tulving-like factorization, with each compartment specializing in one of the what/where/when axes.

**Touchpoint 6: hippocampal mapping — biological warrant via Lisman-Grace.** MERLIN's authors explicitly map the MBP onto hippocampal episodic memory. The user's program connects this further via [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md): MERLIN's predictive memory should be *gated by novelty* (not just by recency), with novel-vs-expected mismatch driving memory writes. The user's program adds the *novelty gate* to MERLIN's predictive memory — an architectural extension that the original MERLIN does not commit to but that biological warrant supports.

**Touchpoint 7: latent-learning generalization as a direct empirical target.** MERLIN's latent-learning result (reward-free exploration phase, transfer to test phase with rewards) is a *direct empirical target* for the user's program. The user's multi-compartment architecture should support this: in exploration, the system builds a multi-compartment representation of the environment without reward; in test, the representations are leveraged to solve the task quickly. This validates the *unsupervised pre-training* aspect of the user's program — that the multi-hub system's competition-driven representations are genuinely useful for downstream tasks even without task-specific training.

**Touchpoint 8: limitations as opportunities — JEPA-style replacement of reconstruction loss.** MERLIN's reconstruction-loss-driven memory shaping is its principal limitation — it spends capacity on reconstructing irrelevant pixel detail. The architectural opportunity for the user's program: replace MERLIN's pixel-reconstruction loss with a JEPA-style latent-prediction loss ([bardes2023_vjepa](bardes2023_vjepa.md), [assran2023_ijepa](assran2023_ijepa.md)), getting the predictive-memory benefits without the pixel-detail penalty. The user's iterative VAE, configured to predict in its own latent space rather than at the pixel level, is the architectural instantiation of this MERLIN+JEPA hybrid. The user's program is therefore positioned to *improve over MERLIN* by combining MERLIN's predictive-memory architecture with the modern JEPA loss insights.

## 8. Citations to follow

- `hung2019_value_transport_nat_comm` — *Nature Communications* — optimizing agent behavior over long time scales by transporting value. Not in seed.
- `parisotto2020_gated_transformer_xl_icml` — *ICML* — stabilizing Transformers for RL (Gated Transformer-XL); the transformer alternative. Not in seed.
- `lampinen2021_hierarchical_memory_neurips` — *NeurIPS* — towards mental time travel; hierarchical memory for RL agents. Not in seed.
- `kapturowski2019_r2d2_iclr` — *ICLR* — recurrent experience replay in distributed RL (R2D2); the simpler-baseline comparison. Not in seed.
- `banino2020_memo_iclr` — *ICLR* — MEMO: a deep network for flexible combination of episodic memories. Not in seed.
- `ritter2018_meta_episodic_recall_icml` — *ICML* — meta-learning with episodic recall. Not in seed.
- `pritzel2017_neural_episodic_control_icml` — *ICML* — neural episodic control; the predecessor work. Not in seed.
- `fortunato2019_generalization_multiset_memory` — generalization of RL with multiset generative memory. Not in seed.
- [whittington2020_tem](whittington2020_tem.md) — TEM; the neuroscience-side architectural sibling. In seed.
- `goyal2022_retrieval_augmented_rl_icml` — *ICML* — retrieval-augmented RL; the modern descendant. Not in seed.
- [hafner2023_dreamerv3](hafner2023_dreamerv3.md) — DreamerV3; the contrast world-model architecture. In seed.
- [ha_schmidhuber2018_world_models](ha_schmidhuber2018_world_models.md) — the original world-model paper. In seed.
- [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md) — the novelty-gated memory mechanism that should be added to MERLIN's predictive memory. In seed.
- [banino2018_vector_navigation](banino2018_vector_navigation.md) — the grid-cell RL agent (DeepMind sibling paper). In seed.
- [stachenfeld2017_predictive_map](stachenfeld2017_predictive_map.md) — the predictive-map framework that MERLIN's predictive memory instantiates. In seed.
