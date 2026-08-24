---
id: dabney2020_distributional_dopamine
title: "A distributional code for value in dopamine-based reinforcement learning"
authors:
  - "Dabney, Will"
  - "Kurth-Nelson, Zeb"
  - "Uchida, Naoshige"
  - "Starkweather, Clara Kwon"
  - "Hassabis, Demis"
  - "Munos, Rémi"
  - "Botvinick, Matthew"
year: 2020
venue: "Nature"
doi: "10.1038/s41586-019-1924-6"
arxiv: ""
url: "https://doi.org/10.1038/s41586-019-1924-6"
tags:
  - reinforcement-learning
  - dopamine
  - neuro-ai-bridging
concepts:
  - distributional-rl
  - reward-modulated-attention
related:
  - bellemare2017_c51
  - dabney2018_qr_dqn
  - botvinick2020_deep_rl_neuro
  - babayan_uchida_gershman2018_belief_states_dopamine
  - glimcher2011_dopamine_rpe
  - hikosaka2006_bg_reward_eyes
  - monosov2020_outcome_uncertainty
relevance_to:
  - prism_v2
seed_source:
  - manual
status: stub
depth: abstract
last_updated: "2026-05-19"
---

# A distributional code for value in dopamine-based reinforcement learning

## 1. Abstract

(Verbatim from PubMed PMID 31942076 / DOI [10.1038/s41586-019-1924-6](https://doi.org/10.1038/s41586-019-1924-6). Full-depth read deferred.)

> Since its introduction, the reward prediction error theory of dopamine has explained a wealth of empirical phenomena, providing a unifying framework for understanding the representation of reward and value in the brain. According to the now canonical theory, reward predictions are represented as a single scalar quantity, which supports learning about the expectation, or mean, of stochastic outcomes. Here we propose an account of dopamine-based reinforcement learning inspired by recent artificial intelligence research on distributional reinforcement learning. We hypothesized that the brain represents possible future rewards not as a single mean, but instead as a probability distribution, effectively representing multiple future outcomes simultaneously and in parallel. This idea implies a set of empirical predictions, which we tested using single-unit recordings from mouse ventral tegmental area. Our findings provide strong evidence for a neural realization of distributional reinforcement learning.

The empirical contribution is single-unit recordings from mouse VTA dopamine neurons during a probabilistic reward task. The key prediction tested is that individual DA neurons should exhibit heterogeneous "optimism" — different cells should respond as if they represent different quantiles (or expectiles) of the reward distribution rather than all encoding the same scalar mean.

## 8. Citations to follow

(Stub depth; full citation trail deferred.)

- `lowet2020_distributional_dopamine_review` — Lowet, Zheng, Matias, Drugowitsch & Uchida 2020 *Trends in Neurosciences*; the review companion to the Dabney *Nature* paper. Not yet in db.
- `bellemare2023_distributional_rl_book` — Bellemare, Dabney & Rowland 2023 *Distributional Reinforcement Learning* (MIT Press, free draft online); the canonical textbook treatment of the algorithmic side. Not yet in db.
- `eshel2015_dopamine_reward_signals` — Eshel et al. 2015 *Nature*; the prior single-unit characterization of mouse VTA DA neuron heterogeneity that Dabney 2020 extends with the distributional framing. Not yet in db.
- `tian_uchida2015_dopamine_subtraction` — Tian & Uchida 2015 *Neuron*; reference-dependent dopamine subtraction (the asymmetric scaling between positive and negative RPEs that the distributional account explains via per-cell quantile assignment). Not yet in db.
