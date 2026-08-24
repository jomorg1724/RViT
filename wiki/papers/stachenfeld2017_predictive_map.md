---
id: stachenfeld2017_predictive_map
title: "The hippocampus as a predictive map"
authors:
  - "Stachenfeld, Kimberly L."
  - "Botvinick, Matthew M."
  - "Gershman, Samuel J."
year: 2017
venue: "Nature Neuroscience"
doi: "10.1038/nn.4650"
arxiv: ""
url: "https://www.nature.com/articles/nn.4650"
tags:
  - hippocampus
  - reinforcement-learning
  - successor-representation
  - predictive-coding
  - place-cells
  - grid-cells
concepts:
  - hierarchical_predictive_coding
  - coupled_rnn_world_models
  - multi_compartmental_memory
  - gridcell_rnn
  - world_model_emergence
related:
  - okeefe_dostrovsky1971_hippocampal_map
  - hafting2005_grid_cells
  - whittington2020_tem
  - behrens2018_cognitive_map
  - banino2018_vector_navigation
  - lisman_grace2005_hippocampal_vta
  - rao_ballard1999_predictive_coding
  - friston2010_fep_unified_theory
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# The hippocampus as a predictive map

## 1. Abstract

> "A cognitive map has long been the dominant metaphor for hippocampal function, embracing the idea that place cells encode a geometric representation of space. However, evidence for predictive coding, reward sensitivity and policy dependence in place cells suggests that the representation is not purely spatial. We approach this puzzle from a reinforcement learning perspective: what kind of spatial representation is most useful for maximizing future reward? We show that the answer takes the form of a predictive representation. This representation captures many aspects of place cell responses that fall outside the traditional view of a cognitive map. Furthermore, we argue that entorhinal grid cells encode a low-dimensionality basis set for the predictive representation, useful for suppressing noise in predictions and extracting multiscale structure for hierarchical planning." (Stachenfeld, Botvinick & Gershman 2017, *Nature Neuroscience* 20(11):1643-1653, abstract.)

## 2. Why this matters for us

Stachenfeld et al. 2017 reframes hippocampal place cells as encoding the *successor representation* (SR) — the expected discounted future state occupancy under the current policy — rather than as a geometric map of physical space. For the user's program, this is the *most direct biological warrant* for treating memory as a *predictive* representation: not a passive log of what has happened, but a *forward-looking* substrate that captures what is *likely to happen next*. The user's program inherits this commitment. The recurrent ViT's hidden state, PRISM's memory, and the gridcell_rnn architecture should be interpreted not as photographic snapshots of the past but as *predictive* summaries that bias the next prediction. The paper also matters because it explicitly proposes that *grid cells are eigenvectors of the SR* — a low-dimensional basis for predictive computation — providing a substantive computational interpretation of the user's multi-scale spatial memory hierarchy. The deepest, coarsest memory compartment is, on this view, the *lowest-frequency eigenvectors* of the system's predictive map: the basis for long-range, hierarchical prediction.

## 3. Key claims

1. Hippocampal place cells encode the *successor representation* (SR): the expected discounted future state occupancy under the current policy — a predictive representation rather than a geometric map.
2. SR explains *policy- and reward-dependent reshaping* of place fields (e.g., field skewing toward goals, elongation along trajectories) that the pure cognitive-map view cannot account for.
3. MEC grid cells are *eigenvectors* (low-dimensional basis) of the SR matrix; multiscale grids reflect eigenvectors of differing spatial frequency.
4. Grid modules support *hierarchical planning* and *noise reduction* in predictions — different scales provide different planning horizons.
5. SR predicts *community structure detection* — boundaries in the place-cell representation appear at bottlenecks in the transition graph.
6. The framework *unifies hippocampal roles* in navigation, memory, and reinforcement learning under a single computational principle.
7. SR provides a formal account of why hippocampus is implicated in *both spatial and non-spatial tasks* — the principle is predictive computation, not space per se.
8. *Predictions:* place-field shape should depend on behavior (direction of travel, policy); grid spacing should reflect graph spectral structure; field sizes should scale with discount factor (dorsal-ventral gradient).

## 4. Methods

Analytical/computational study. The authors derive the SR under a Markov decision process formalism: $M(s, s') = \mathbb{E}[\sum_{t=0}^{\infty} \gamma^t \mathbb{1}[s_t = s'] | s_0 = s]$, the expected discounted future occupancy of state $s'$ given that the agent starts in state $s$ and follows the current policy. They simulate place- and grid-field properties in 1D linear tracks, 2D open fields, T-mazes, and graph-structured environments (including community-structured graphs). Eigendecomposition of the SR yields predicted grid-like basis functions; the lowest eigenvectors are the coarsest spatial scales, higher eigenvectors progressively finer. Model outputs are compared qualitatively and quantitatively to published empirical phenomena: Mehta et al.'s backward skewing of place fields with experience; multi-compartment remapping; grid spacing gradients; community-structure detection in human fMRI (Schapiro et al. 2013). The analytical framework also derives predictions about how place fields should change as a function of reward locations, discount factor, and policy.

## 5. Results

Key simulation/analytical findings:

- **SR-derived place fields show backward skewing along directional tracks**, matching Mehta et al. (1997, 2000) — characteristic skewness develops with experience as the agent traverses the track repeatedly.
- **SR fields elongate toward reward locations** — consistent with goal-related field warping observed empirically.
- **SR fields fragment at environmental boundaries / topological bottlenecks**, reproducing multi-compartment place-cell data.
- **Eigenvectors of the SR matrix produce hexagonal grid-like patterns** in 2D open environments — providing a computational interpretation of grid cells as a *spectral basis* for the SR.
- **Grid spacing forms a geometric (multiscale) series** in line with empirically observed module spacings (Stensola et al. 2012).
- **In graphs with community structure, SR eigenvectors segment communities**, matching Schapiro et al. (2013) fMRI results on community detection in the human hippocampus.
- **The model reproduces splitter-cell-like responses** (route-dependent firing) on T-mazes.
- **Discount factor $\gamma$ controls predictive horizon and hence field size** — qualitatively matching the dorsal-ventral hippocampal field-size gradient (dorsal HPC: small fields, low $\gamma$; ventral HPC: large fields, high $\gamma$).

## 6. Critique / limitations

The SR framework is elegant but has well-documented limits and competing alternatives.

- **SR is policy-dependent** — does not naturally explain rapid re-planning after policy change. When the policy changes (e.g., goal location shifts), the SR has to re-learn from scratch; pure model-based methods can re-plan without re-learning.
- **Eigenvector account of grids requires aligning spectral and anatomical bases**; the biological learning rule for eigendecomposition is unspecified. *How* does the brain compute eigenvectors of the SR?
- **Does not explain hexagonal symmetry per se in 2D open fields** — eigenvectors of a generic graph Laplacian need not be hexagonal; the hexagonal pattern depends on boundary conditions and graph structure that are not derived in the paper.
- **Lacks mechanism for sensory binding, episodic memory, or pattern separation/completion** in CA3/DG — the SR framework is silent on the rich within-hippocampus circuit dynamics.
- **Most empirical comparisons are qualitative**; few new prospective predictions tested in the original paper. Stronger empirical validation came in later work (Momennejad et al. 2017 *Nat Hum Behav*; de Cothi & Barry 2020).
- **Does not address phase precession, theta sequences, or replay** — the temporal-coding richness of hippocampus is outside the framework's scope.
- **Competing models** (TEM by Whittington et al. 2020; oscillatory interference; continuous attractor networks) are not directly arbitrated against the SR account.
- **Conflates time-discounted future occupancy with neural firing rate** without explicit encoding/decoding mapping. The mapping from $M(s, s')$ to spike rate is not specified.

## 7. Connection to our work

Stachenfeld et al. 2017 is one of the architecturally most consequential papers for the user's program because it provides the *predictive-coding interpretation* of memory that the user's program already commits to architecturally.

**Touchpoint 1: memory as predictive representation — the foundational interpretation.** The SR framework's central claim — that the hippocampal memory representation is *forward-looking* (encoding what will happen next) rather than backward-looking (logging what happened) — is the cognitive-neuroscience source of the user's program-level commitment to *predictive memory*. The user's program ([world_model_emergence](../concepts/world_model_emergence.md), [hierarchical_predictive_coding](../concepts/hierarchical_predictive_coding.md)) treats the recurrent memory state as a substrate for *forward prediction*: the memory at $t$ should bias the prediction of inputs/outputs at $t+1$. Stachenfeld et al. provide the cleanest cognitive-neuroscience version of this commitment: the brain's most-studied memory structure is, computationally, *predictive*. The architectural commitment is therefore biologically licensed.

**Touchpoint 2: grid cells as eigenvectors — multi-scale memory as spectral decomposition.** The SR framework's identification of grid cells as *eigenvectors of the SR matrix* — low-dimensional, multi-scale basis functions — is the cleanest computational interpretation of the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) architecture. Each compartment in the user's hierarchy plays the role of a *band of SR eigenvectors*: the deepest, coarsest compartment is the *lowest-frequency* eigenvectors (long-range prediction, hierarchical planning); the shallowest, finest compartment is the *highest-frequency* eigenvectors (local prediction, immediate next step). The user's multi-scale spatial organization is therefore *computationally equivalent* to a spectral decomposition of the system's predictive map. This is a deep computational warrant for the architectural design, not merely an engineering convenience.

**Touchpoint 3: policy-dependence — implications for the user's action-conditioned memory.** The SR framework's policy-dependence — the predictive map changes when the policy changes — has direct architectural implications for the user's program. If the user's memory should encode forward predictions, then the memory dynamics should depend on the *policy* (the system's action distribution). In the user's multi-hub architecture, this means: hub-internal memory dynamics should be modulated by the *current policy / task* — perhaps via the central self-attention substrate that biases which hubs contribute to the memory update. This is the architectural instantiation of the SR's policy-dependence.

**Touchpoint 4: convergence with the world-model-emergence thesis.** The SR framework predicts that *forward-predictable internal states emerge from RL training* — the SR is the optimal representation for maximizing future reward, and an agent trained with RL should develop SR-like representations. This converges directly with the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis: predictive representations should emerge from competition-based training pressures, not just from explicit predictive losses. The SR framework provides one *specific class* of predictive representation (the policy-conditioned SR); the user's program predicts a broader emergence including episodic structure and abstract relational codes.

**Touchpoint 5: dorsal-ventral discount-factor gradient — the slow-fast memory split.** The SR framework's prediction that discount factor $\gamma$ controls field size — and hence the dorsal-ventral hippocampal field-size gradient corresponds to a $\gamma$ gradient — is the cleanest computational interpretation of the user's [slow_fast_recurrence](../concepts/slow_fast_recurrence.md) commitment. The "fast" memory ($M_{fast}$, short time constant, fine spatial scale) corresponds to *low $\gamma$* — short predictive horizon. The "slow" memory ($M_{slow}$, long time constant, coarse spatial scale) corresponds to *high $\gamma$* — long predictive horizon. The architectural choice of two (or more) timescales is therefore the engineering analog of the brain's $\gamma$ gradient — and the timescale separation should correspond to a *predictive-horizon separation*.

**Touchpoint 6: community-structure detection — the architectural prediction for the user's models.** The SR framework's prediction that the predictive map fragments at graph bottlenecks (community boundaries) — and the empirical confirmation in human fMRI (Schapiro et al. 2013) — provides a *behavioral signature* for the user's models. Training the user's model on a task with community structure (e.g., sequences with discrete event boundaries) should result in the memory representation showing increased *similarity* within communities and *dissimilarity* across communities. This is a clean empirical probe for whether the user's architecture has learned a predictive-map-like organization rather than a uniform feature representation.

**Touchpoint 7: SR as the architectural target for the deepest compartment — convergence with TEM.** Both Stachenfeld SR and Whittington TEM ([whittington2020_tem](whittington2020_tem.md)) propose that the deepest layer of the hippocampal-entorhinal hierarchy carries an *abstract structural / predictive* code. They differ in framework (SR is policy-discounted future occupancy; TEM is structural-content factorization with graph-based generalization) but converge on the architectural target: the deepest compartment should hold a *structural* representation that generalizes across tasks. The user's program inherits this convergence: the deepest compartment's target content is *structural/predictive*, and the user's architecture is licensed by *both* SR and TEM frameworks.

**Touchpoint 8: implications for the iterative VAE — predictive-coding rollouts.** The SR framework treats the memory representation as supporting *rollouts* — given a current state, predict the future distribution of states. The user's [iterative_variational_encoder_decoder](../concepts/iterative_variational_encoder_decoder.md) inherits a structurally analogous capability: the encoder produces a guide that the decoder uses for reconstruction, and iterative refinement supports *prediction* of held-out content. The architectural lesson from SR: the *predictive horizon* of the system is set by the depth of the iteration — more iterations enable longer-horizon prediction. The user's iterative VAE should therefore be evaluated on tasks of *varying predictive horizon* (next-step prediction, multi-step prediction, plan-out-to-goal) to fully characterize its predictive capacity.

## 8. Citations to follow

- `momennejad2017_sr_behavioral_humans_nhb` — *Nature Human Behaviour* — behavioral evidence for SR in humans. Not in seed.
- `russek2017_sr_model_based_hybrid_ploscb` — *PLoS Comput Biol* — SR and model-based RL hybrid. Not in seed.
- `gershman2018_sr_review_j_neurosci` — *J Neurosci* — review/critique of SR in brain. Not in seed.
- `garvert_dolan_behrens2017_sr_human_ec_elife` — *eLife* — SR-like structure in human EC for abstract graphs. Not in seed.
- [whittington2020_tem](whittington2020_tem.md) — TEM as an alternative/complementary framework. In seed.
- [behrens2018_cognitive_map](behrens2018_cognitive_map.md) — the cognitive-map review that places SR in the broader framework. In seed.
- `de_cothi_barry2020_sr_vs_grid_elife` — *eLife* — SR vs grid-cell models compared to data. Not in seed.
- [banino2018_vector_navigation](banino2018_vector_navigation.md) — grid units in deep RL agents; the ML demonstration that grid-like codes emerge under RL training. In seed.
- `geerts2020_sr_cognitive_flexibility_pnas` — *PNAS* — SR-based models of cognitive flexibility. Not in seed.
- `piray_daw2021_sr_successor_features_nat_comm` — *Nature Communications* — SR and successor features for planning. Not in seed.
- `stachenfeld2014_sr_grid_nips` — *NIPS* — earlier SR-grid proposal by the same authors. Not in seed.
- `george2021_clone_structured_cognitive_graphs_nat_comm` — *Nature Communications* — clone-structured cognitive graphs; the structural-alternative model. Not in seed.
- [okeefe_dostrovsky1971_hippocampal_map](okeefe_dostrovsky1971_hippocampal_map.md) — the founding place-cell paper; the predictive framework reinterprets place cells. In seed.
- [hafting2005_grid_cells](hafting2005_grid_cells.md) — the grid-cell discovery; the framework reinterprets grid cells as SR eigenvectors. In seed.
- [rao_ballard1999_predictive_coding](rao_ballard1999_predictive_coding.md) — the foundational predictive-coding paper; the broader framework. In seed.
- [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md) — the hippocampus-VTA loop; the gating mechanism for SR updates. In seed.
