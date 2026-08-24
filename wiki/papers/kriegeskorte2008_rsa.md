---
id: kriegeskorte2008_rsa
title: "Representational similarity analysis: connecting the branches of systems neuroscience"
authors:
  - "Kriegeskorte, Nikolaus"
  - "Mur, Marieke"
  - "Bandettini, Peter A."
year: 2008
venue: "Frontiers in Systems Neuroscience"
doi: "10.3389/neuro.06.004.2008"
arxiv: ""
url: "https://www.frontiersin.org/articles/10.3389/neuro.06.004.2008/full"
tags:
  - methodology
  - representational-geometry
  - neuro-ai-bridging
  - human-neuroimaging
concepts:
  - representational-dissimilarity-matrix
related:
  - dicarlo2012_object_recognition
  - kietzmann2019_recurrence_required
  - riesenhuber_poggio1999_hierarchical_models
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-13"
---

# Representational similarity analysis: connecting the branches of systems neuroscience

## 1. Abstract

A fundamental challenge for systems neuroscience is to quantitatively relate its three major branches of research: brain-activity measurement, behavioral measurement, and computational modeling. Using measured brain-activity patterns to evaluate computational network models is complicated by the need to define the correspondency between the units of the model and the channels of the brain-activity data (single-cell recordings, fMRI voxels). Similar correspondency problems complicate relating activity patterns between different measurement modalities, between subjects, and between species. To bridge these divides, the authors propose abstracting from the activity patterns themselves and computing **representational dissimilarity matrices (RDMs)**, which characterize the information carried by a given representation in a brain or model. Building on a rich psychological and mathematical literature on similarity analysis, they propose a new experimental and data-analytical framework — **representational similarity analysis (RSA)** — in which multi-channel measures of neural activity are quantitatively related to each other and to computational theory and behavior by comparing RDMs. They demonstrate RSA by relating fMRI representations of visual objects in early visual cortex and the fusiform face area to computational models spanning a wide range of complexities. RDMs are simultaneously related via second-level multidimensional scaling and tested using randomization and bootstrap techniques.

## 2. Why this matters for us

RSA is THE methodological framework for comparing model representations to brain representations without solving the impossible "which model unit corresponds to which neuron" problem. For the user's program, this is the bridge between architectural commitments (Feedback Transformer, multi-compartmental memory, descending/ascending projections) and the biological cortex those commitments are claimed to mimic. If we want to argue that the Recurrent ViT's iterated attention dynamics or PRISM's hierarchical predictive coding *match* primate visual cortex, RDMs are the lingua franca in which that claim is tested. Every modern model-brain comparison paper (Yamins-DiCarlo, Schrimpf Brain-Score, Cichy et al., Kietzmann et al.) builds on Kriegeskorte 2008.

## 3. Key claims

1. The "correspondency problem" — how to map model units to brain channels — blocks direct comparison of internal representations across modalities, subjects, species, and between brains and models.
2. Computing pairwise **dissimilarities between condition-specific activity patterns** abstracts away from the units' identities while preserving the relational structure that defines a representation.
3. The full set of pairwise dissimilarities for $N$ conditions forms a symmetric $N \times N$ **representational dissimilarity matrix (RDM)** with zeros on the diagonal.
4. RDMs from different measurement modalities (fMRI, single-unit, MEG, behavior, models) are directly comparable because they share the same condition indexing, even though the underlying "channels" are incommensurable.
5. **Second-order comparison** — correlating RDMs across modalities — quantifies how well one representation predicts another, and is the basis for model evaluation and cross-species/cross-modality alignment.
6. Spearman rank correlation between RDMs, with significance assessed by condition-label randomization and bootstrap over stimuli, gives an assumption-light statistical framework that generalizes from the sampled conditions to the population of conditions.
7. RSA naturally supports a new experimental design — **condition-rich ungrouped-events designs** — in which many stimuli are presented individually rather than blocked, trading per-contrast efficiency for representational coverage.
8. The framework licenses a new layer of analysis ("representational connectivity"): measuring how much two regions' RDMs share over and above what either shares with the stimulus.

## 4. Methods

**Data-analytical primitive.** For each of $N$ experimental conditions, estimate a multi-channel activity pattern $\mathbf{r}_i \in \mathbb{R}^C$ — voxels for fMRI, neurons for electrophysiology, units for a model. Compute a pairwise dissimilarity $d_{ij} = D(\mathbf{r}_i, \mathbf{r}_j)$ for every pair. Default $D$ is **1 minus the Pearson correlation** between activity patterns, which is invariant to per-pattern additive and multiplicative shifts. Alternatives include Euclidean distance, Mahalanobis distance, and absolute regional-mean difference.

**RDM.** The matrix $\mathbf{R} \in \mathbb{R}^{N \times N}$ with entries $d_{ij}$ is the RDM. It is symmetric with zero diagonal. The upper (or lower) triangle, with $N(N-1)/2$ unique entries, is the data summary.

**Second-order comparison.** Given two RDMs $\mathbf{R}^{(A)}$ and $\mathbf{R}^{(B)}$ from different modalities/regions/models, compute the **Spearman rank correlation** $\rho$ over their upper-triangle entries. Spearman avoids assuming a linear relation between dissimilarity scales that may have very different ranges and noise structures.

**Statistical inference.**
- *Randomization test.* Permute condition labels (10,000 permutations); for each permutation, reorder one RDM's rows and columns and recompute $\rho$. The fraction of permuted correlations $\geq$ the observed value is the one-sided $p$-value.
- *Bootstrap.* Resample conditions with replacement (e.g., 96 conditions sampled 100 times). For each resample, recompute the RDMs and their correlation. The bootstrap distribution gives error bars on the RDM-similarity estimate and generalizes from the sampled stimuli to a hypothetical population of stimuli.

**Visualization.** Multidimensional scaling (MDS) embeds an RDM into 2D so distances approximate the dissimilarities, exposing the representational geometry as a constellation of conditions. A "second-level" MDS over the matrix of inter-RDM similarities visualizes how *brains and models cluster in representation space*.

**Experimental design.** The authors advocate **condition-rich ungrouped-events designs**: many distinct stimuli (e.g., 96 unique images), each shown briefly (≈300 ms) with short stimulus-onset asynchrony (≈4 s), without blocking by category. This sacrifices efficiency for any single category contrast but exposes the full pairwise structure needed to estimate an $N \times N$ RDM.

**Demonstration application.** 96 object images (animate/inanimate, faces/bodies/objects, etc.) shown to human subjects under fMRI. RDMs computed for V1, early visual cortex, and the fusiform face area (FFA). Models compared: silhouette-overlap, raw pixel correlation, V1-like Gabor, smoothed V1, HMAX C1/C2 features (Riesenhuber & Poggio), and conceptual category-prototype models. Cross-species comparison used 92 of the 96 images previously shown to macaques during IT single-unit recording.

**Representational connectivity.** The authors propose a generalization of functional connectivity in which two regions are "representationally connected" to the extent that their RDMs covary across stimuli over and above what each shares with a stimulus model. Unlike voxel-correlation functional connectivity, representational connectivity is invariant to which voxels carry which features, so it survives the same correspondency problem RSA was built to solve.

## 5. Results

- **EVC fit.** The best-fitting model for early visual cortex was a smoothed silhouette/V1 model. The smoothing reflected the spatial pooling inherent in fMRI voxels and was empirically necessary to match the cortical RDM.
- **FFA fit.** The face-animal-prototype conceptual model produced the best correspondence with FFA. Among computational models, HMAX-C2 features fit best — consistent with FFA representing higher-order shape/category structure.
- **Cross-hemisphere consistency.** Left and right FFA RDMs were highly correlated; likewise for left and right parahippocampal place areas. RSA recovers a known functional symmetry without requiring inter-hemispheric voxel correspondence.
- **Cross-species alignment.** RDM correlation between macaque IT (single-unit recordings) and human IT (fMRI) over the shared 92 images was **$\rho = 0.49$, $p < 0.0001$** — a striking demonstration that two radically different measurement modalities, in two different species, encode the same object structure when read through the lens of RSA.
- **Statistical power.** Randomization tests over 10,000 permutations gave well-calibrated null distributions; bootstrap error bars on inter-RDM correlations were narrow enough to discriminate among competing models.
- **MDS of RDMs across regions and models.** A second-level multidimensional scaling over inter-RDM similarity placed each (region, subject) and each model as a point in a 2D plane. Regions of comparable function across subjects clustered tightly; computational models clustered separately from cortical regions, with HMAX-C2 closest to FFA and silhouette closest to EVC. The plot is a single-glance summary of where each model sits in the space of cortical representations.
- **Robustness to subject and run.** Within-subject and across-subject reproducibility of FFA and EVC RDMs was high; RSA results did not depend on the specific subset of runs or voxels used, as long as the voxel set was anatomically defined and sufficiently large.

## 6. Critique / limitations

**What RSA throws away.** Computing dissimilarities discards the absolute spatial layout of activity in the cortex (or in a model). RSA characterizes *what* is represented in a region but not *where* within the region; mappings between specific neurons/voxels and specific features cannot be recovered from an RDM alone.

**Hemodynamics filter.** What pattern information survives the fMRI hemodynamic transform is not fully characterized. The empirical success of "smoothed" models for EVC suggests fMRI undersamples high-spatial-frequency tuning structure (e.g., V1 orientation columns), so RDMs from fMRI cannot be expected to mirror single-unit RDMs in detail.

**Noise model.** Correlation-distance RSA assumes the noise across channels is roughly isotropic. Multivariate-noise structure (correlated noise across voxels or neurons) can inflate or deflate apparent dissimilarities. Subsequent work — crossnobis / linear-discriminant-contrast / pattern-component models (Walther, Nili, Diedrichsen 2016) — patches this gap.

**Spearman rank correlation.** It is robust to monotone transforms but discards quantitative dissimilarity information. When a model produces dissimilarities on a meaningfully linear scale, Pearson or weighted measures may have more power. Choice of inter-RDM metric is itself a methodological decision (see Diedrichsen & Kriegeskorte 2017).

**Information bottleneck.** RSA evaluates representations only at the *level of pairwise condition distances*. Two representations with identical RDMs can still differ in higher-order tensor structure (triplet relations, manifold curvature). For exhaustive comparison one must move to richer geometries (manifold capacity, mutual information).

**Stimulus-set dependence.** The RDM is a function of the chosen stimuli; conclusions generalize only to the sampled stimulus space. The bootstrap over conditions partially addresses this but cannot extrapolate beyond the sampling distribution.

**Subsequent work.** RSA has been extended to noise-corrected distances (Nili et al. 2014, Walther et al. 2016), encoding-model variants (Diedrichsen & Kriegeskorte 2017), temporally resolved RSA over MEG (Cichy et al. 2014), and large-scale deep-network benchmarking (Yamins et al. 2014, Schrimpf et al. 2018 Brain-Score). The 2008 paper is the canonical entry point but is no longer state of the art for noise modeling.

**Caveat about second-order interpretation.** A high RDM correlation between a model and a brain region tells us the two representations *sort condition pairs similarly*; it does not tell us they implement the same computation. Two models with identical RDMs over a stimulus set can have very different internal mechanics. RSA is necessary but not sufficient for claiming mechanistic correspondence.

## 7. Connection to our work

This paper is the **methodological bridge** between every architectural commitment in the user's program and the cortex those commitments aspire to model. Three uses are immediate.

**(a) Validating the Recurrent ViT against primate visual cortex.** The Recurrent ViT (2502.10955) claims that its iterated attention dynamics resemble primate covert-attention dynamics. RSA is how that claim is empirically tested. Procedure: run the network on the same image set used in a primate IT or human fMRI experiment, extract activations at each recurrent step $t = 1, \ldots, T$ and each layer, compute an RDM per (layer, step), and correlate against the cortical RDMs. The user's Food-101 result that "attention dynamics evolve nontrivially over passes" becomes a falsifiable claim under RSA: do later-step RDMs become *more* correlated with IT than early-step RDMs, as one would expect if recurrence implements a settling process toward an object-representation attractor? See [kietzmann2019_recurrence_required](kietzmann2019_recurrence_required.md), which used precisely this RSA-over-time logic to argue that recurrence is required to match human IT.

**(b) Comparing PRISM v1 and v2 against fMRI/MEG.** PRISM v1's predictive-coding pathway and PRISM v2's hierarchical FiLM both make commitments about the *representational geometry* at each layer. RSA gives an apples-to-apples comparison: compute RDMs at PRISM's $M_t$ states and compare to RDMs at corresponding cortical levels (V1, V2/V4, IT). A specific test: PRISM v2's slow/fast memory predicts that the *slow* memory RDM should correlate with IT (slowly changing object structure) while the *fast* memory RDM should correlate with V1 (rapidly changing input structure). This is the standard hierarchical-RSA test (DiCarlo et al. 2012, [dicarlo2012_object_recognition](dicarlo2012_object_recognition.md)).

**(c) Cross-layer / cross-state RSA inside the architecture.** The multi-compartmental memory commitment (§3 of [the_user_architectural_program](../threads/the_user_architectural_program.md)) gives several recurrent states $C_1, C_2, C_3$ at different spatial resolutions and channel dimensions. Standard concatenation is impossible (different shapes); but RSA is shape-agnostic. Compute an RDM per state per time step and analyze (i) which states cluster together in representational geometry, (ii) whether descending/ascending projections produce smooth transitions in RDM-space, and (iii) whether competition-emergent predictive coding (§5 of the thread) manifests as a diverging-then-converging RDM trajectory under inter-hub conflict. This is a model-internal diagnostic enabled entirely by Kriegeskorte 2008.

**(d) Why RSA is uniquely well-suited to the program.** The Feedback Transformer integrates feedback at the level of Q/K/V projections. There is no natural way to align a model unit with a cortical neuron. RSA's escape from the correspondency problem is exactly what licenses comparing this architecture to cortex at all. Any subsequent neural-fit benchmarking (Brain-Score, Algonauts, the Allen Institute Visual Coding dataset) will use RSA or an RSA-derivative as the metric.

**Specific hyperparameter to record.** When running RSA, the inter-RDM correlation needs an upper bound — the *noise ceiling* — that captures the maximum achievable correlation given measurement noise. Nili et al. 2014 give the standard upper/lower noise-ceiling estimators. Any RSA comparison reported for our models must include noise ceilings; reporting a raw $\rho$ without a ceiling is meaningless because it conflates model quality with data quality.

**(e) RSA as a diagnostic for competition-emergent predictive coding.** The user's central theoretical thesis (§5 of the thread) predicts that, under inter-hub conflict, hubs develop *opponent models* of each other expressed in their own representational geometry. An operational test: train the multi-hub system on conflicting objectives, then compute the RDM of hub $A$'s state conditioned on hub $B$'s state being held fixed across stimuli (a partial-RDM construction). If the partial RDMs change systematically with $B$'s state — and if the change predicts $B$'s subsequent behavior — that is RSA-grade evidence for strategic opponent modeling. Without RSA, there is no obvious way to phrase this prediction quantitatively, since the hubs have different dimensionalities and live in unrelated coordinate systems.

**(f) Reading order within the broader literature.** [riesenhuber_poggio1999_hierarchical_models](riesenhuber_poggio1999_hierarchical_models.md) supplies the HMAX C1/C2 features used as one of the model RDMs in the original demonstration; this is the conceptual ancestor of the deep-CNN-to-IT comparisons that dominate today. The user's program is a *recurrent* generalization of the HMAX-to-IT picture, and RSA is what lets us slot a recurrent model into the same evaluation pipeline.

## 8. Citations to follow

- `nili2014_rsa_toolbox` — the RSA toolbox paper; introduces noise ceilings and crossnobis-style improvements. Essential for any actual implementation. Not yet in seed.
- `walther2016_crossnobis` — cross-validated Mahalanobis (crossnobis) distance for unbiased pattern dissimilarity. Not yet in seed.
- `diedrichsen_kriegeskorte2017_rsa_encoding` — unifies RSA with encoding models. Not yet in seed.
- `yamins2014_predictive_models_it` — first deep-CNN-to-IT comparison using RSA + regression; the template for model-brain benchmarking. Not yet in seed.
- `schrimpf2018_brainscore` — large-scale benchmark that operationalizes RSA-style comparisons across many models and cortical regions. Not yet in seed.
- `cichy2014_meg_fmri_rsa` — temporally resolved RSA combining MEG and fMRI. Directly relevant to the Recurrent ViT's *time-resolved* attention claims. Not yet in seed.
- `khaligh_razavi_kriegeskorte2014_deep_models_it` — deep models match IT representational geometry; a direct precursor to the framing used here. Not yet in seed.
- `kriegeskorte2008_match_human_monkey_it` — companion paper, same year, on the cross-species human-monkey IT match. Not yet in seed.
- `haxby2001_distributed_object_representations` — the methodological ancestor (pattern-similarity in fMRI). Not yet in seed.
- `edelman1998_representation_similarity_visual` — Edelman's similarity-based representation framework. Not yet in seed; conceptual root of RSA.
