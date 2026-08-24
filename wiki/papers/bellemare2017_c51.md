---
id: bellemare2017_c51
title: "A Distributional Perspective on Reinforcement Learning"
authors:
  - "Bellemare, Marc G."
  - "Dabney, Will"
  - "Munos, Rémi"
year: 2017
venue: "ICML"
doi: ""
arxiv: "1707.06887"
url: "https://arxiv.org/abs/1707.06887"
tags:
  - reinforcement-learning
  - deep-learning
concepts:
  - distributional-rl
related:
  - dabney2018_qr_dqn
  - dabney2020_distributional_dopamine
  - botvinick2020_deep_rl_neuro
  - sutton_barto2018_rl_intro
  - schulman2017_ppo
relevance_to:
  - prism_v2
seed_source:
  - manual
status: stub
depth: abstract
last_updated: "2026-05-19"
---

# A Distributional Perspective on Reinforcement Learning

## 1. Abstract

(Paraphrase from arXiv:1707.06887 abstract; verbatim text via [arxiv.org/abs/1707.06887](https://arxiv.org/abs/1707.06887). Full-depth read deferred.)

The paper argues for the fundamental importance of the **value distribution**: the distribution of the random return $Z^\pi(s, a)$ received by a reinforcement learning agent, in contrast to traditional methods that focus only on its expectation $Q^\pi(s, a) = \mathbb{E}[Z^\pi(s, a)]$. The authors give theoretical contributions for both policy evaluation and control: they show that the distributional Bellman operator is a contraction in the Wasserstein metric for policy evaluation but is **not** in general a contraction in the control setting, revealing a distributional instability. They propose a new algorithm — later known as **C51** (51 atoms over a fixed support) — applying a categorical projection of Bellman's equation to approximate the value distribution. Empirical results on the Arcade Learning Environment (57 Atari games) yielded state-of-the-art performance over DQN at the time, demonstrating that learning the value distribution as an auxiliary signal can improve sample efficiency and final performance even when only the mean is used for action selection.

## 8. Citations to follow

(Stub depth; full citation trail deferred.)

- `dabney2018_qr_dqn` — Quantile-regression successor that replaces the C51 categorical projection with a parametrization in *quantile* space, removing the fixed-support restriction (already stubbed).
- `mnih2015_dqn` — Mnih et al. 2015 *Nature*, "Human-level control through deep reinforcement learning"; the DQN baseline that C51 extends and outperforms across the Atari-57 suite. Not yet in db.
- `dabney2018_iqn` — Dabney, Ostrovski, Silver, Munos 2018 "Implicit Quantile Networks for Distributional Reinforcement Learning"; further generalization of QR-DQN with implicit quantile parametrization. Not yet in db.
- `rowland2018_analysis_categorical` — Rowland, Bellemare, Dabney et al. 2018 "An Analysis of Categorical Distributional Reinforcement Learning"; the theoretical follow-up that formalizes the categorical projection's contraction properties. Not yet in db.
