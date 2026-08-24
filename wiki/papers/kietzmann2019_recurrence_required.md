---
id: kietzmann2019_recurrence_required
title: "Recurrence is required to capture the representational dynamics of the human visual system"
authors:
  - "Kietzmann, Tim C."
  - "Spoerer, Courtney J."
  - "Sörensen, Lynn K. A."
  - "Cichy, Radoslaw M."
  - "Hauk, Olaf"
  - "Kriegeskorte, Nikolaus"
year: 2019
venue: "PNAS"
doi: "10.1073/pnas.1905544116"
arxiv: ""
url: "https://doi.org/10.1073/pnas.1905544116"
tags:
  - human-neuroimaging
  - deep-learning
  - neuro-ai-bridging
  - representational-geometry
  - recurrent-networks
concepts:
  - recurrence-for-temporal-dynamics
  - ventral-stream-hierarchy
  - top-down-feedback
  - representational-dissimilarity-matrix
  - bidirectional-hierarchical-feedback
related:
  - mante2013_context_dependent_pfc
  - dicarlo2012_object_recognition
  - felleman_vanessen1991_hierarchical_cortex
  - kriegeskorte2008_rsa
  - dosovitskiy2020_vit
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_111
status: full
depth: full
last_updated: "2026-05-16"
---

# Recurrence is required to capture the representational dynamics of the human visual system

## 1. Abstract

The human visual system is an intricate network of brain regions that enables object recognition. Despite its abundant lateral and feedback connections, object processing is commonly viewed and studied as a feedforward process. The authors measure and model the rapid representational dynamics across multiple stages of the human ventral stream using time-resolved brain imaging (MEG) and deep learning. They observe substantial representational transformations during the first 300 ms of processing within and across ventral-stream regions. Categorical divisions emerge in sequence, cascading forward and in reverse across regions, and Granger causality analysis suggests bidirectional information flow between regions. Recurrent deep neural network models clearly outperform parameter-matched feedforward models in their ability to capture the multi-region cortical dynamics. Targeted virtual cooling experiments on the recurrent deep network models further substantiate the importance of their lateral and top-down connections. The results establish that *recurrent* models are required to understand information processing in the human ventral stream.

## 2. Why this matters for us

Kietzmann et al. 2019 is the canonical empirical result establishing that the human visual system does not implement pure feedforward processing — that lateral and feedback connections are necessary to explain the empirical representational dynamics. This is the load-bearing reference for the user's commitment to recurrent vision architectures. The recurrent ViT (2502.10955) is built on the premise that visual processing requires recurrence; this paper is the strongest empirical evidence for that premise from the human-MEG side. PRISM v2's two-level hierarchy with cross-level feedback ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10) is the architectural form Kietzmann's "lateral and top-down connections are important" empirical finding points to.

## 3. Key claims

1. Representational dynamics in the human ventral stream show substantial *temporal evolution* during the first ~300 ms of stimulus processing. Pure feedforward models predict a single rapid sweep; the data show multiple cycles of representational transformation.
2. Categorical structure emerges *in sequence* across regions, with later-emerging categories at later times, but also shows *reverse cascading*: information appears at downstream regions, then re-emerges at upstream regions at later latencies. This is the empirical signature of feedback.
3. Granger causality analysis on the MEG data confirms *bidirectional* information flow between ventral-stream regions, with both feedforward and feedback components having significant effects.
4. Recurrent CNN models (using lateral and top-down connections at each level) capture the empirical dynamics *substantially better* than parameter-matched feedforward CNN models. The difference is large, not marginal.
5. *Virtual cooling* experiments — selectively disabling lateral or top-down connections at specific levels of the trained recurrent model — confirm that these connections are doing computational work, not just adding parameters. Their disabling specifically impairs the model's match to the empirical dynamics.
6. The empirical pattern is *not* explained by single-frame processing variants. Adding depth, capacity, or training data to feedforward models does not close the gap with recurrent models on the dynamics-matching benchmark.

## 4. Methods

**Data.** MEG recordings from healthy adult participants viewing natural object images, with single-trial resolution. The MEG signals were source-reconstructed and assigned to anatomical ROIs (early visual cortex, ventral temporal cortex, fusiform face area, lateral occipital cortex) using inverse modeling.

**Representational dynamics analysis.** For each ROI and each time point, the representational dissimilarity matrix (RDM) was computed across the stimulus set (Kriegeskorte 2008 framework, [kriegeskorte2008_rsa](research_db/papers/kriegeskorte2008_rsa.md)). The RDMs were then compared across ROIs and time points to characterize how representations evolve.

**Model comparison.** Feedforward CNNs (with various depths) and recurrent CNNs (with lateral and top-down connections) were trained on the same object-recognition task. The trained models' RDMs were extracted at each level and compared to the empirical MEG RDMs. The match between model RDMs and empirical RDMs was quantified as a fit metric.

**Virtual cooling.** In the trained recurrent CNN, specific connection types (lateral, top-down) at specific levels were silenced ("cooled") and the resulting model's RDMs were compared to the empirical data. If silencing impaired the match, the silenced connection was doing computational work.

**Granger causality.** On the empirical MEG data, Granger causality between ROIs was computed to characterize directionality of information flow. Significant Granger causality in both directions indicates bidirectional information flow.

## 5. Results

The principal quantitative findings:

- **Recurrent models > feedforward models** on the dynamics-matching benchmark. The recurrent CNNs' match to the empirical MEG RDMs is substantially better than parameter-matched feedforward CNNs, with the gap being largest in the time range 150–300 ms after stimulus onset.
- **Categorical structure emerges in sequence and reverse.** The forward cascade (earlier categories at earlier regions, later categories at later regions) is augmented by a *reverse* cascade in which later-emerging information re-appears at upstream regions. This is consistent with feedback information flow.
- **Granger causality is bidirectional.** Both feedforward and feedback Granger causality components are significant, with the feedback component peaking later in time (consistent with the reverse-cascade observation).
- **Virtual cooling.** Silencing top-down connections in the recurrent model specifically impairs the match to the empirical dynamics at the lower-region ROIs (V1-analog, V2-analog), confirming that the empirical dynamics in early visual cortex include a feedback component.
- **Effect size.** The recurrent-vs-feedforward gap on the dynamics benchmark is large enough to be unlikely to close with more capacity, more data, or deeper feedforward models within the standard feedforward architecture class.

## 6. Critique / limitations

The MEG source-reconstruction has limited spatial resolution. The ROI assignment of the source signals is an approximation; bleed-through across ROIs is possible. The Granger causality findings rest on the spatial separation being clean, which is not strictly true with MEG.

The recurrent models are trained on object recognition. They are not directly tested on the same dynamics task they're evaluated on (they're trained on object recognition, the empirical match is to the dynamics). The match could be enhanced by training models specifically on dynamics-matching, but this would conflate the architecture's expressive power with the training objective's specificity.

The "recurrence" the paper establishes is recurrent computation at a single timescale. It does not distinguish between *short-range recurrent* connections (lateral, intra-area) and *long-range recurrent* connections (cross-area feedback). The user's program commits to both; Kietzmann's data support the importance of both but doesn't fully separate them.

The empirical signature — categories cascading forward then reverse — is consistent with feedback predictions in the predictive-coding framework (Bastos 2012). The paper doesn't engage with the predictive-coding interpretation explicitly, but the data are consistent with it.

The paper does not address why feedforward models *underperform* the data. The implicit story is "feedforward models can't capture the temporal dynamics because they don't have a temporal-dynamics mechanism," but the explanation is more nuanced — feedforward models *do* have a sequence of stages, just not a recurrence. Whether the gap could be closed with sufficiently deep feedforward models is an open empirical question; the paper presents evidence that within reasonable depths it cannot.

## 7. Connection to our work

This paper is the canonical empirical anchor for the user's commitment to recurrent visual architectures:

**Recurrent ViT's premise.** The recurrent ViT paper (2502.10955) builds on the architectural commitment that vision requires recurrence. Kietzmann et al. 2019 is the canonical empirical evidence from the human-MEG side. Any future manuscript on the recurrent ViT should cite this paper as the empirical foundation for the architectural choice.

**Multi-stage feedback as the empirical pattern.** The paper's "reverse cascade" — categorical information appearing at downstream regions and then *re-emerging* at upstream regions at later latencies — is the empirical signature of multi-stage feedback. PRISM v2's two-level hierarchy with cross-level feedback ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.10) implements exactly this kind of feedback pattern.

**Granger-causal bidirectional flow as the empirical analog of the Feedback Transformer.** The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) implements bidirectional information flow by integrating feedback from many sources into the attention computation. Kietzmann's Granger-causal bidirectional MEG result is the empirical pattern this is designed to reproduce.

**Virtual cooling as the experimental analog of feedback-source ablation.** The paper's virtual cooling experiments demonstrate that specific feedback connections are doing computational work. The user's program commits to *gateable* feedback ([bidirectional_hierarchical_feedback](research_db/concepts/bidirectional_hierarchical_feedback.md), "ability to shut off feedback") — the experimental analog would be to ablate specific feedback sources in the trained multi-hub system and verify their causal role. Kietzmann's methodology is the template.

**Limits of feedforward models.** Kietzmann's finding that feedforward CNNs underperform recurrent CNNs on the dynamics benchmark is the strongest argument for *why* the user's program insists on recurrence. The published recurrent ViT and PRISM are both recurrent; future iterations should benchmark against feedforward baselines on dynamics-matching tasks to confirm the architectural commitment is paying off.

## 8. Citations to follow

- `spoerer2020_recurrent_vision` — Spoerer et al. follow-up showing recurrent CNNs can flexibly trade speed and accuracy. Not in seed; should be added.
- `kriegeskorte2008_rsa` — RSA methodology. In seed.
- `dicarlo2012_object_recognition` — the ventral-stream framework. In seed.
- `felleman_vanessen1991_hierarchical_cortex` — the laminar hierarchy. In seed.
- `mante2013_context_dependent_pfc` — recurrent dynamics in PFC. In seed, full depth.
- `nayebi2018_task_driven_models` — task-driven CNNs of the ventral stream. Not in seed.
- `kar2019_evidence_recurrent_processing` — empirical evidence for recurrent processing in monkey ventral stream. Not in seed.
- `kietzmann2018_dnn_review` — review of deep nets as models of cortex. Not in seed.
