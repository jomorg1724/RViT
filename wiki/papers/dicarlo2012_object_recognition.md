---
id: dicarlo2012_object_recognition
title: "How does the brain solve visual object recognition?"
authors:
  - "DiCarlo, James J."
  - "Zoccolan, Davide"
  - "Rust, Nicole C."
year: 2012
venue: "Neuron"
doi: "10.1016/j.neuron.2012.01.010"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/22325196/"
tags:
  - primate-neurophysiology
  - review
  - early-visual-cortex
  - neuro-ai-bridging
  - representational-geometry
concepts:
  - ventral-stream-hierarchy
  - unsupervised-ventral-stream-model
  - representational-dissimilarity-matrix
  - top-down-feedback
  - bidirectional-hierarchical-feedback
related:
  - hubel_wiesel1962_receptive_fields
  - hubel_wiesel1968_macaque
  - tanaka1996_it_object_vision
  - mishkin1983_two_pathways
  - riesenhuber_poggio1999_hierarchical_models
  - felleman_vanessen1991_hierarchical_cortex
  - kriegeskorte2008_rsa
  - kietzmann2019_recurrence_required
  - dosovitskiy2020_vit
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-16"
---

# How does the brain solve visual object recognition?

## 1. Abstract

Mounting evidence suggests that "core object recognition" — the ability to rapidly recognize objects despite substantial appearance variation — is solved in the brain via a cascade of reflexive, largely feedforward computations that culminate in a powerful neuronal representation in the inferior temporal cortex. However, the algorithm that produces this solution remains poorly understood. Here the authors review evidence ranging from individual neurons and neuronal populations to behavior and computational models. They propose that understanding this algorithm will require using neuronal and psychophysical data to sift through many computational models, each based on building blocks of small, canonical subnetworks with a common functional goal: progressively *untangling* the object-identity manifolds that arrive at the retina into a linearly separable representation in IT cortex.

## 2. Why this matters for us

This is the modern definitive review of the feedforward primate ventral-stream story: V1 → V2 → V4 → IT as a cascade of canonical subnetworks that progressively *untangles* object manifolds until a downstream decoder can read out identity by a simple linear classifier. Every neuro-AI bridging argument the user's program makes — that the Recurrent ViT's layered self-attention mimics ventral-stream untangling, that PRISM's hierarchical memory tracks V1/V4/IT-like representations, that descending/ascending projections implement the canonical cortical loop — descends from this paper's conceptual frame. The "many-to-one → untangled manifolds" formulation is the *neuro-AI Rosetta stone* between Hubel-Wiesel-style receptive fields ([hubel_wiesel1962_receptive_fields](hubel_wiesel1962_receptive_fields.md)), Tanaka-style IT feature columns ([tanaka1996_it_object_vision](tanaka1996_it_object_vision.md)), and the ViT's transformation of an image through stacked transformer blocks ([dosovitskiy2020_vit](dosovitskiy2020_vit.md)). DiCarlo's framework also names the *baseline* — pure feedforward untangling — that recurrence-based extensions ([kietzmann2019_recurrence_required](kietzmann2019_recurrence_required.md), and the user's Recurrent ViT) are claimed to improve on.

## 3. Key claims

1. **Core object recognition is a real, behaviorally measurable competence.** Primates and humans can identify objects within ~200 ms across substantial variation in position, scale, pose, and clutter — fast enough that the underlying neural computation must be largely (though not exclusively) feedforward.
2. **The ventral stream is the substrate.** Information flows from retina → LGN → V1 → V2 → V4 → posterior IT (PIT) → central/anterior IT (CIT/AIT), with each stage performing a stereotyped local computation on the output of the previous stage.
3. **Object identity lives on low-dimensional manifolds in the high-dimensional neural state space.** At the retina and V1, the manifold for a given object — the set of all population responses to identity-preserving image transformations (translation, scaling, rotation, illumination) — is highly *curved and tangled* with the manifolds for other objects, so no linear hyperplane can separate them.
4. **The ventral stream's job is to *untangle* those manifolds.** Successive stages re-represent the input so that the per-object manifolds become flatter and more separable, until in IT a *linear classifier* on the population vector can support category-level and identity-level discrimination at primate-behavior levels.
5. **The canonical local computation is an AND-OR pair.** Each stage builds new tuning by conjunctively combining (AND-like) lower-stage features at specific locations, and pools (OR-like, max-like, or average-like) over nuisance variation. Repeated AND-OR layers can in principle produce arbitrarily complex, invariant tuning — this is the abstract form of HMAX-style architectures ([riesenhuber_poggio1999_hierarchical_models](riesenhuber_poggio1999_hierarchical_models.md)).
6. **IT population codes are read out by simple decoders.** Linear classifiers trained on ~100–200 randomly sampled IT neurons can match primate behavioral performance on core recognition tasks, validating the "untangled-manifold + linear-readout" account.
7. **The neural code is distributed, not grandmotherly.** Single IT neurons are broadly tuned across many objects; identity is encoded in the *pattern* across the population, not by single-cell selectivity. This is the empirical anchor for representational-similarity-based analysis ([kriegeskorte2008_rsa](kriegeskorte2008_rsa.md)).
8. **Feedforward suffices for "core" recognition, but feedback is real and unexplained.** The authors are explicit that anatomical feedback connections are abundant and likely matter for occluded, ambiguous, or attention-modulated recognition — but the ~200 ms behavioral window leaves room for at most one or two recurrent passes. The feedforward sweep is the load-bearing computation for the *core* problem.
9. **The remaining open problem is the *algorithm*.** The architecture (feedforward hierarchy of AND-OR stages) and the *target* representation (untangled manifolds at IT) are well established. What is poorly understood is which specific local learning rule, which specific operations, and which specific subnetwork wiring produce the empirical sequence of receptive-field properties along V1 → V2 → V4 → IT.

## 4. Methods

This is a review; the "methods" are the integrated body of single-unit electrophysiology, fMRI, psychophysics, lesion/causal manipulation, and computational modeling literatures the authors synthesize. The conceptual framework introduced is mathematical, not experimental:

**Manifold formalism.** For an object $o$, let $\mathcal{T}$ denote the set of identity-preserving transformations (translations, scalings, rotations, illuminations, etc.). The *object manifold* at neural stage $L$ is the set
$$\mathcal{M}_o^{(L)} = \{ \mathbf{r}^{(L)}(T(o)) : T \in \mathcal{T} \} \subset \mathbb{R}^{N_L}$$
where $\mathbf{r}^{(L)}$ is the population response vector at stage $L$ and $N_L$ is the number of neurons. Recognition is the problem of finding a *separating manifold* — ideally a hyperplane — between $\mathcal{M}_{o_1}^{(L)}$ and $\mathcal{M}_{o_2}^{(L)}$.

**Tangling diagnostic.** At early stages (retina, V1), the manifolds are highly curved and inter-twined because identity-preserving transformations produce large displacements in $\mathbf{r}$ while different objects can produce small displacements. A linear classifier fails. At IT, the manifolds are approximately flat and well-separated; a linear classifier succeeds. *Untangling* is the operational definition of what the ventral stream computes.

**Canonical subnetwork.** Each ventral-stream stage implements (in this framework) a small AND-OR module: an AND-like nonlinear combination produces tuning for *conjunctions* of lower-stage features (building selectivity), and an OR-like pooling over a local neighborhood produces tolerance to *variation* in the position/scale/pose at which those conjunctions appear (building invariance). The repeated AND-OR composition is what flattens manifolds.

**Readout test.** The authors review evidence that linear classifiers on IT population activity — trained on a held-out fraction of trials — match primate behavioral accuracy on rapid object discrimination at the trial-by-trial level. This is the operational validation of "untangling" as the right description of what IT computes.

**Computational-model evaluation programme.** The authors propose (this is the paper's *manifesto* component) that the field should sift through candidate algorithms by training each on a common image set, computing per-stage neural representations, and benchmarking the model representations against single-unit and population data from the corresponding cortical stages. This is the programme that subsequently produced Yamins et al. 2014, Khaligh-Razavi & Kriegeskorte 2014, and Brain-Score (Schrimpf 2018).

## 5. Results

This is a review; the relevant numbers are integrated findings:

- **Behavioral speed.** Core object recognition is performed within **~100–200 ms** of stimulus onset in primates, leaving ~70–100 ms for the ventral-stream sweep itself once retinal and motor latencies are subtracted.
- **Single-IT-cell selectivity.** Typical IT neurons respond to **>10%** of natural object images at >50% of their maximum rate — i.e., broad tuning, not grandmother cells.
- **Tolerance ranges.** IT neurons preserve object preference across position shifts of **~2–4° of visual angle** and scale changes of a factor of **~2**, far larger than the corresponding V1 ranges (~0.1–0.5° position tolerance, no scale tolerance).
- **Population readout.** Linear classifiers trained on **~200 randomly sampled IT neurons** match primate behavior on 8-way object categorization tasks; equivalent classifiers trained on V1 populations of the same size *fail*, even with much larger populations. The capacity gap is the empirical signature of untangling.
- **Anatomical scope.** The ventral stream comprises ~5–7 successive cortical stages (V1, V2, V4, PIT, CIT, AIT) over a wiring depth of ~3–4 synaptic relays from V1 to anterior IT, consistent with the ~70–100 ms feedforward sweep budget at ~10–20 ms per stage.
- **Feedback abundance.** Anatomical descending projections outnumber ascending ones at each stage by a substantial factor (citing [felleman_vanessen1991_hierarchical_cortex](felleman_vanessen1991_hierarchical_cortex.md)), yet the authors argue these contribute relatively little to the *core* (rapid, isolated, unambiguous) recognition case.
- **Model-cortex match.** HMAX-style hierarchical models with hand-designed C1/C2 features (Riesenhuber & Poggio 1999, [riesenhuber_poggio1999_hierarchical_models](riesenhuber_poggio1999_hierarchical_models.md)) capture only part of IT's representational structure — a gap that subsequently *deep CNNs trained on ImageNet* substantially closed (Yamins et al. 2014, post-dating this review).

## 6. Critique / limitations

**Feedforward bias.** The 2012 framing privileges the feedforward sweep. Subsequent work — including [kietzmann2019_recurrence_required](kietzmann2019_recurrence_required.md) and Kar et al. 2019 — has shown that even *core* recognition has substantial recurrent contributions for *challenging* images (occlusion, clutter, low contrast). The "largely feedforward" qualifier is doing real work in the abstract; the paper is sometimes cited as if feedforward were sufficient, which it is not.

**Manifolds as metaphor vs. mechanism.** The untangling framework is conceptually clean and predictively useful, but the actual *manifold geometry* in early visual cortex is much higher-dimensional and harder to characterize than the cartoon "tangled" → "flat" picture suggests. Subsequent work on *manifold capacity* (Chung, Lee & Sompolinsky 2018) made these notions quantitative, and the picture is more nuanced.

**Algorithm gap.** As the authors themselves note, the framework specifies the *target* of the ventral-stream computation (untangling) and the *architectural class* (hierarchical AND-OR) but leaves the *learning algorithm* unspecified. The subsequent 2014–2018 deep-CNN revolution showed that *one* algorithm (supervised backprop on ImageNet) gets close, but biological plausibility remains an open question.

**Limited engagement with attention and dynamics.** The review treats core recognition as essentially attention-free and time-locked. The user's program (and the Recurrent ViT) takes the contrary stance that *attention and recurrence are mechanistic, not auxiliary*, even for static images. The 2012 framing does not preclude this but does not push for it.

**No quantitative bridge to predictive coding.** The paper does not engage with Rao-Ballard or Friston-style predictive coding. The user's program (and the broader neuro-AI literature) treats predictive coding as a *plausible algorithmic story* for what the canonical AND-OR subnetwork is *actually computing*; DiCarlo et al. leave that question open.

**The IT-as-endpoint assumption.** The review takes IT as the readout-ready representation. Subsequent work has shown that downstream regions (perirhinal cortex, prefrontal cortex) also contribute to recognition behavior, particularly for difficult or familiarity-modulated discriminations. IT is *necessary* but not always sufficient.

**Sampling bias in single-unit data.** The single-unit IT statistics cited are biased toward neurons that fire robustly to recorded stimulus sets. The fraction of IT cells that are highly selective, narrowly tuned, or active only in naturalistic / behavioral contexts is plausibly underestimated.

## 7. Connection to our work

This paper is the *conceptual scaffolding* under every neuro-AI bridging claim the user's program makes. Five specific connection points:

**(a) Hierarchical untangling as the conceptual ancestor of the ViT.** The Vision Transformer ([dosovitskiy2020_vit](dosovitskiy2020_vit.md)) takes a tangled pixel-space representation and, through stacked self-attention + MLP blocks, transforms it into a linearly classifiable embedding at the [CLS] token. This is *manifold untangling by another name*. DiCarlo et al.'s AND-OR formulation maps to the transformer block almost component-for-component: self-attention's $QK^T$ matmul implements a content-addressed conjunctive (AND-like) selection over tokens, and the subsequent MLP + residual stream implements pooling / re-weighting (OR-like). The ViT is, in this sense, *the modern hierarchical untangling network* that DiCarlo et al. were asking the field to find — minus the biological-plausibility constraints. The Recurrent ViT extends this with temporal iteration, adding recurrent untangling on top of feedforward untangling.

**(b) Recurrence as *dynamic* untangling on top of feedforward untangling.** The 2012 review treats feedforward untangling as the core computation and feedback as a modifier. [kietzmann2019_recurrence_required](kietzmann2019_recurrence_required.md) showed empirically that this is incomplete: the empirical IT representation only reaches its untangled state through recurrent dynamics, and feedforward CNNs cannot capture the temporal evolution. The Recurrent ViT (2502.10955) is *built* on this extension. Its iterated attention dynamics over recurrent passes are the architectural realization of "dynamic untangling": each pass refines the manifold separation in a way no single feedforward pass can. The user's Food-101 observation that "attention dynamics evolve nontrivially over passes" is the model-internal signature of this iterated untangling.

**(c) RSA as the empirical test of untangling.** [kriegeskorte2008_rsa](kriegeskorte2008_rsa.md) provides the quantitative test of whether a model's per-stage representations untangle the way IT does. Procedure: compute RDMs at each stage of the Recurrent ViT and at each recurrent step; compare to monkey IT and human ventral-stream RDMs over the same stimulus set; verify that later stages / later steps produce RDMs that match IT and that earlier stages match V1/V4. DiCarlo et al.'s framework supplies the *prediction* (untangling progresses up the hierarchy and through time), RSA supplies the *measurement*.

**(d) PRISM's hierarchical memory tracks the V1/V4/IT progression.** The user's multi-compartmental memory commitment (§3 of [the_user_architectural_program](../threads/the_user_architectural_program.md)) — three stacked GridCell RNNs with descending conv projections producing progressively coarser, channel-richer states — is the architectural form of DiCarlo's V1 → V4 → IT progression. Layer 1's small-RF, fine-spatial state mirrors V1; Layer 3's large-RF, abstract-channel state mirrors IT. The descending-projection design choice (spatial reduction + channel expansion) is the user's *explicit translation* of the canonical AND-OR subnetwork's "build conjunctions, pool over nuisance variation" prescription into convolutional form. PRISM v2's slow/fast memory ([PRISM_V2_PROPOSAL.md](../../archive/Prism/docs/PRISM_V2_PROPOSAL.md) §3.3) further matches DiCarlo's hint that deeper stages should integrate more slowly — IT-level identity changes only when the object changes, not when its position shifts.

**(e) ConvGRU memory as temporal untangling for change detection.** The published Recurrent ViT and PRISM apply DiCarlo's spatial-untangling insight to a *temporal* domain. The change-detection task requires not just untangling one frame's object manifold but also untangling *trajectories* in manifold space — distinguishing "same object, moved" from "different object". PRISM's ConvGRU memory (and PRISM v2's dual ConvGRUs) accumulates evidence across time, effectively performing untangling along the *temporal* dimension on top of the per-frame spatial untangling that the ViT backbone provides. This is the user's program extending DiCarlo et al. from static-image recognition to dynamic-scene change detection.

**(f) The feedforward-vs-recurrent contrast as the central architectural question.** DiCarlo et al. claim feedforward suffices for core recognition; Kietzmann et al. claim recurrence is required for the empirical dynamics; the user's Recurrent ViT claims that even *better* untangling can be achieved with iterated attention. These three positions form a coherent debate, and the user's published change-detection results are evidence on the side of "recurrence adds something." Any future manuscript should cite this paper as the *baseline* the recurrent-vision argument is improving on, not as a competing claim — DiCarlo et al. explicitly leave room for feedback to matter for non-core cases.

**Specific hyperparameter to record.** When benchmarking the Recurrent ViT against ventral-stream data (the natural follow-up to DiCarlo's review), report per-layer and per-recurrent-step RDM correlations against monkey IT (e.g., from the Majaj et al. 2015 dataset that Brain-Score uses). The expected pattern is that early ViT blocks correlate with V4, late ViT blocks correlate with IT, and later recurrent steps tighten the IT correlation. Departures from this pattern are diagnostic of where the architecture does or does not implement the ventral-stream-style untangling DiCarlo et al. describe.

## 8. Citations to follow

- `yamins2014_predictive_models_it` — first deep-CNN-to-IT comparison; the empirical realization of DiCarlo's "sift computational models against neural data" programme. Not yet in seed.
- `cadieu2014_dnn_object_recognition` — Cadieu et al. comparing CNNs to IT on Brain-Score-precursor benchmarks. Not yet in seed.
- `schrimpf2018_brainscore` — the operationalized benchmark for "which model best matches the ventral stream." Not yet in seed.
- `chung_lee_sompolinsky2018_manifold_capacity` — formal manifold-geometry analysis that operationalizes DiCarlo's "untangling" claim with explicit capacity measures. Not yet in seed.
- `majaj2015_simple_learned_decoders` — the canonical IT readout dataset; quantifies how few IT neurons suffice for primate-level recognition. Not yet in seed.
- `kar2019_evidence_recurrent_processing` — empirical evidence that recurrent processing is required for *challenging* core recognition, qualifying DiCarlo's "largely feedforward" claim. Not yet in seed.
- `khaligh_razavi_kriegeskorte2014_deep_models_it` — RSA-based deep-model-vs-IT comparison, precursor to Brain-Score. Not yet in seed.
- `serre_oliva_poggio2007_feedforward_categorization` — psychophysical evidence for the ~150 ms feedforward sweep. Not yet in seed.
- `logothetis_sheinberg1996_visual_object_recognition` — earlier review establishing the IT-as-object-representation framework. Not yet in seed.
- `rust_dicarlo2010_selectivity_tolerance_v4_it` — quantitative selectivity/tolerance comparison along V4 → IT, the empirical anchor for the "untangling" claim. Not yet in seed.
