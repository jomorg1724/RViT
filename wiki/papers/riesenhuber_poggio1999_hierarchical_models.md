---
id: riesenhuber_poggio1999_hierarchical_models
title: "Hierarchical models of object recognition in cortex"
authors:
  - "Riesenhuber, Maximilian"
  - "Poggio, Tomaso"
year: 1999
venue: "Nature Neuroscience"
doi: "10.1038/14819"
arxiv: ""
url: "https://www.nature.com/articles/nn1199_1019"
tags:
  - theoretical-essay
  - early-visual-cortex
  - cortical-anatomy
concepts:
  - ventral-stream-hierarchy
  - orientation-selectivity
  - gabor-receptive-fields
related:
  - hubel_wiesel1962_receptive_fields
  - hubel_wiesel1968_macaque
  - dicarlo2012_object_recognition
  - tanaka1996_it_object_vision
  - kietzmann2019_recurrence_required
  - kriegeskorte2008_rsa
  - dosovitskiy2020_vit
  - felleman_vanessen1991_hierarchical_cortex
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-15"
---

# Hierarchical models of object recognition in cortex

## 1. Abstract

Visual processing in cortex is classically modeled as a hierarchy of increasingly sophisticated representations, naturally extending the model of simple to complex cells of Hubel and Wiesel. Surprisingly, little quantitative modeling has been done to explore the biological feasibility of this class of models to explain aspects of higher-level visual processing such as object recognition. We describe a new hierarchical model consistent with physiological data from inferotemporal cortex that accounts for this complex visual task and makes testable predictions. The model is based on a MAX-like operation applied to inputs to certain cortical neurons that may have a general role in cortical function.

## 2. Why this matters for us

HMAX is the **direct conceptual ancestor of modern convolutional and patch-token vision architectures** and the most influential explicit instantiation of the simple-complex template-matching/pooling motif (Hubel & Wiesel 1962, in seed) at the scale of the whole ventral stream. The user's program — the Feedback Transformer, the GridCell-RNN stack, and the hierarchical multi-compartmental memory (`threads/the_user_architectural_program.md` §§1–3) — inherits HMAX's V1 → V2 → V4 → IT hierarchical decomposition, channel-expansion-with-spatial-reduction structure, and the principle that *invariance is built by pooling over a set of position- or scale-specific feature detectors*. HMAX is simultaneously the user's **architectural foil**: it is strictly feedforward, has no attention, no recurrence, no top-down feedback, and no memory. Its inability to solve tasks that demand any of those mechanisms — change detection, sustained tracking, contextual disambiguation — is precisely the gap the Recurrent ViT, PRISM v1, and PRISM v2 are designed to close. Reading HMAX is reading what visual cortex looks like if you take only the feedforward kernel of Hubel & Wiesel 1962 and project it through six cortical stages; the user's program is what you get when you add attention, recurrence, and bidirectional feedback to that foundation.

## 3. Key claims

1. **A purely feedforward hierarchy of alternating template-matching ("S" layers) and MAX-pooling ("C" layers) suffices to model the principal phenomena of view-based object recognition** in primate IT — selective tuning to specific objects with substantial position and scale invariance.
2. **The MAX-like operation** — a cortical neuron whose output approximates the maximum over its set of afferent inputs — **is the key nonlinearity that builds invariance** without losing feature specificity, and is biologically plausible as a soft-max-like nonlinear pooling implementable via local divisive normalization or lateral inhibition.
3. **S layers (S1, S2)** perform **Gaussian-tuned template matching** over their afferents (oriented Gabor filters at S1, more complex feature combinations at S2), producing units that fire most strongly for a specific input pattern at a specific location and scale — the artificial counterpart of simple cells / V4 feature-combination cells.
4. **C layers (C1, C2)** perform **MAX pooling** over S-layer afferents that share a preferred feature but differ in position and scale — producing units invariant to position and scale within a pooling window, the artificial counterpart of complex cells / IT view-tuned units.
5. **A four-stage model (S1 → C1 → S2 → C2) followed by view-tuned units (VTUs)** matches the qualitative receptive-field and invariance properties of V1 (S1, C1), V4 (S2, C2), and IT (VTUs), respectively, with each successive stage operating at larger spatial scales, broader invariance, and more complex feature combinations.
6. **The same MAX-pooling principle that builds position invariance can also build invariance to other dimensions** — scale (by pooling over multiple S-layer scales), view (by pooling over view-tuned S-layer outputs), and clutter tolerance (by selecting the best-matching feature rather than averaging) — making MAX a general-purpose cortical operation.
7. **The model fits Logothetis-Pauls-Poggio paperclip-recognition data**: VTUs trained on a particular 3-D paperclip generalize to novel views of the same paperclip in the way IT neurons in trained monkeys do, including the typical degree of view tuning and the residual invariance to small rotations.
8. **MAX pooling preserves selectivity in clutter better than linear summation does** — a population of MAX-pooled C2 units presented with two objects in their receptive field responds primarily to the better-matching object, whereas a linearly pooled population responds to a contaminated mixture. This is HMAX's prediction for the clutter-tolerance of IT cells.
9. **The model makes testable physiological predictions** — in particular about the form of multi-stimulus tuning curves (MAX-like rather than sum-like) and about the invariance ranges expected at successive ventral-stream stages — that subsequent work (Lampl et al. 2004; Gawne & Martin 2002) has examined empirically.

## 4. Methods

**Architecture.** Four feedforward layers alternating "S" template-matching units with "C" MAX-pooling units:

- **S1.** A bank of oriented Gabor-like filters at multiple scales and orientations, applied densely across the visual field. Each S1 unit responds to an oriented edge / bar at a specific position, orientation, and spatial scale. This is the V1-simple-cell stage and the artificial analogue of Hubel & Wiesel 1962's simple cells.
- **C1.** MAX-pooling units that pool over a small neighbourhood of S1 units sharing the same preferred orientation but differing in position and scale, producing position- and scale-invariant orientation responses. This is the V1-complex-cell stage; the MAX over scale is HMAX's specific innovation beyond the classical Hubel & Wiesel complex cell.
- **S2.** Template-matching units that respond maximally to a specific combination of C1 afferents — e.g., a specific spatial configuration of two or more oriented features at fixed relative positions. S2 units are tuned by Gaussian radial-basis-functions over their C1 afferent activity pattern; they are the artificial analogue of V4 feature-combination cells (Pasupathy & Connor 2001; Gallant et al. 1993).
- **C2.** MAX-pooling units that pool over S2 units of the same feature template at different positions and scales, producing position- and scale-invariant feature-combination responses. The C2 stage is HMAX's analogue of IT-level position/scale-invariant feature representations.

The model is closed with **view-tuned units (VTUs)** — Gaussian-tuned radial-basis-function units over C2 activations — that fire selectively for a specific object viewed from a specific viewpoint. Multiple VTUs tuned to different views of the same object can then be pooled to create object-tuned units invariant to viewpoint.

**The MAX operation.** Each C-layer unit's output is approximately
$$
y = \max_i x_i
$$
over its set of S-layer afferents $\{x_i\}$, implementable in continuous form by
$$
y = \big(\sum_i x_i^p \big)^{1/p}
$$
for large $p$, or by lateral-inhibition / divisive-normalization circuits ($y_i \propto x_i^q / (\sigma + \sum_j x_j^q)$ for large $q$ followed by summation). The paper argues this is biologically plausible because (a) it can be approximated by feedforward inhibitory pools with simple cells, and (b) it explains observed nonlinear summation in cortical responses to multi-stimulus displays.

**Template-matching (S) units.** S-layer responses follow a Gaussian tuning function over the input pattern:
$$
y = \exp\!\left(-\frac{\|x - w\|^2}{2\sigma^2}\right)
$$
where $w$ is the unit's preferred input pattern (template) and $x$ is the current afferent activity pattern. This is the radial-basis-function template-matching motif Poggio & Edelman 1990 introduced as a model of view-based recognition.

**Training.** S1 filters are hand-designed Gabors at multiple orientations and scales. C1 pooling is hand-designed. S2 templates and VTU centres are *learned* from training images (paperclips for the Logothetis comparison, or other object sets) by selecting C1 / C2 activity patterns elicited by example stimuli and using those as RBF centres. The model is therefore mostly *configured* rather than gradient-descent-trained; no end-to-end backpropagation is used.

**Model fits.** The model's VTU responses are compared to IT cells recorded by Logothetis, Pauls & Poggio 1995 in monkeys trained to recognize 3-D paperclips. The model's clutter-tolerance is compared to IT recordings under multi-stimulus presentations.

## 5. Results

- **View-tuned recognition.** A VTU trained on a single paperclip view fires maximally for that view and exhibits Gaussian tuning over rotations away from it. The width of the tuning curve in the model (typically ±20–30° for the paperclip task) matches the tuning widths reported by Logothetis, Pauls & Poggio 1995 for IT cells in trained monkeys.
- **Pooling across views yields object-tuned, view-invariant units.** A weighted sum over several VTUs tuned to different views of the same object produces a unit that fires for any view of that object — the artificial analogue of IT object cells that show partial view invariance.
- **Position invariance.** C2-stage and VTU responses are largely invariant to translations of the object across a substantial portion of the visual field, with the degree of invariance increasing from C1 (small) through C2 (moderate) to VTUs (large) — paralleling the increase in receptive-field size from V1 through V4 to IT.
- **Scale invariance.** Same pattern as position invariance: VTUs respond to the trained object across a roughly twofold range of scales, with scale invariance built by C-layer MAX pooling across S-layer scale channels.
- **Clutter tolerance.** When two paperclips are presented simultaneously in a single C2 unit's pooling region, the C2 unit's response is approximately equal to its response to whichever paperclip alone elicits the higher response — the MAX prediction. Linear-summation pooling would predict additive interference; MAX pooling preserves the stronger signal. The authors argue that this matches the qualitative behaviour of IT cells in multi-stimulus displays (Sato 1989; Miller et al. 1993).
- **Generalization to novel views.** VTUs trained on a small number of views of a paperclip generalize partially to novel intermediate views, with generalization falling off smoothly with angular distance — the same shape as the IT data.
- **Comparison to alternatives.** A purely linear-pooling variant (replacing MAX with SUM) fails to exhibit either the sharp tuning or the clutter tolerance of IT cells. The MAX nonlinearity is load-bearing.
- **Predictions.** The paper predicts (a) that IT multi-stimulus responses should be approximately MAX-like rather than sum-like (subsequently supported in some regimes by Gawne & Martin 2002 but partially refuted by Zoccolan et al. 2005, which found averaging-like behaviour for many IT cells); (b) that the spatial receptive-field size and invariance range should grow progressively along the ventral stream; (c) that view-tuned cells should be a generic computational stage and that view-invariant object cells should emerge from pooling over view-tuned afferents.

## 6. Critique / limitations

- **Strictly feedforward.** HMAX has no recurrent connections, no top-down feedback, no attentional modulation, and no memory. It cannot model any phenomenon that requires temporal integration (change detection, motion in cluttered scenes), context-dependent disambiguation, or task-dependent gain modulation. Subsequent work (Kietzmann et al. 2019, in seed; Kar et al. 2019) has demonstrated that recurrence is *required* to match cortical dynamics on hard, ambiguous, or temporally extended visual tasks.
- **MAX is empirically only sometimes right.** The prediction that IT cells respond to multi-stimulus displays via a MAX operation has been only partially supported. Zoccolan, Cox & DiCarlo 2005 reported that most IT cells show responses closer to an *average* of the constituent single-stimulus responses, not a max, contradicting HMAX's central nonlinearity claim. Subsequent reconciliations (Reynolds & Heeger 2009, in seed; normalization models) recast both MAX and AVG as limiting cases of divisive normalization with different gain parameters, salvaging HMAX as a special case but undermining its claim that MAX is the universal cortical operation.
- **Hand-designed templates and pooling.** S1 Gabors, C1/C2 pooling neighbourhoods, and feature-combination templates are largely hand-engineered or selected from example responses rather than learned end-to-end. The model achieves its biological plausibility partly by *fiat* — feature selectivity is built in, not derived from training data. Modern CNNs (LeCun et al. 1998; Krizhevsky et al. 2012; trained-on-ImageNet) and self-supervised models learn analogous features from data and outperform HMAX dramatically on natural-image tasks (DiCarlo et al. 2012, in seed; Yamins et al. 2014).
- **Limited stimulus set.** The principal empirical comparison is to Logothetis-Pauls paperclip data — a deliberately impoverished, low-clutter, geometrically simple stimulus set. The model has not been shown to scale to natural-image recognition at the level of modern deep networks, and the original HMAX implementation was outperformed by trained CNNs once large image datasets and gradient-based training became available (Serre, Wolf & Poggio 2007 partially extended HMAX but still trailed deep CNNs).
- **No account of dynamics.** All HMAX predictions are about asymptotic firing rates; the model is silent on the temporal evolution of cortical responses (which Kietzmann et al. 2019 and Kar et al. 2019 show contains task-relevant information unattainable from a feedforward sweep).
- **No attention.** HMAX assumes the input is already segmented and centred. The role of selective attention in restricting the effective input to a sub-region of the scene (Reynolds & Heeger 2009; Desimone & Duncan 1995, both in user's program seed) is outside HMAX's scope. The user's program treats attention as a core ingredient missing from HMAX.
- **No learning of feature selectivity.** Beyond VTU training, the model does not learn S2 feature templates from data in the modern sense; subsequent extensions (Serre et al. 2007) added an unsupervised feature-learning stage, but the original 1999 paper sidesteps the learning problem that is the central concern of modern representation learning.
- **One-dimensional view of invariance.** Position, scale, and view invariance are built one at a time by stacked MAX operations. The combinatorial explosion of MAX pools required for *joint* invariance to many transformations is a known weakness of factored-invariance models, addressed only later by capsule networks (Hinton et al. 2018), equivariant networks (Cohen & Welling 2016), and learned feature pooling in modern CNNs.
- **No segmentation, no binding.** HMAX produces a vector of activations over features; it does not solve the binding problem of associating which features belong to which object in a cluttered scene. Slot-attention models (Locatello et al. 2020) and feature-binding accounts (Reynolds & Desimone 1999; Treisman & Gelade 1980) address this problem outside HMAX.

## 7. Connection to our work

This paper is the canonical artificial-architecture realization of the simple-complex hierarchy that Hubel & Wiesel 1962 (in seed) discovered in V1, projected through the whole ventral stream. It is simultaneously the **direct ancestor** of every architectural choice in the user's program and the **explicit foil** that motivates each of the components the user adds on top.

**HMAX as ancestor of CNNs and ViT patch tokenisation.** HMAX's S-layer template matching is the ancestor of the convolutional layer: a bank of feature detectors, each replicated across spatial positions, computing local linear-then-nonlinear matches. HMAX's C-layer MAX pooling is the literal ancestor of the *max-pool* layer in LeNet (LeCun et al. 1998), AlexNet (Krizhevsky et al. 2012), and VGG (Simonyan & Zisserman 2014). The alternation S→C→S→C in HMAX is the alternation conv→pool→conv→pool in every classical CNN. The ViT (Dosovitskiy et al. 2020, in seed) replaces the explicit MAX-pool with patch tokenisation and attention-based aggregation, but the broad architectural commitment — local feature extraction followed by spatial aggregation, repeated at increasing scale — is unchanged from HMAX. The user's program (`threads/the_user_architectural_program.md` §3) inherits this through the GridCell-RNN stack: each layer's spatially-independent processing (SIP) plays HMAX's S-layer role, and the Feedback Transformer's spatial mixing plays HMAX's C-layer role, but in a recurrent, multi-source-feedback variant.

**HMAX as the empirical / quantitative bridge from V1 to IT.** Hubel & Wiesel 1962 sketched a serial pooling within V1 (simple → complex); HMAX extends that template through V4 (S2/C2) to IT (VTUs), giving the first quantitatively-tested model of the full V1 → V2 → V4 → IT hierarchy that Felleman & Van Essen 1991 mapped anatomically and DiCarlo et al. 2012 (both in seed) reviewed empirically. The user's three-layer reference design (program §3) — V1-level Layer 1, V2/V4-level Layer 2, IT-level Layer 3 — is structurally isomorphic to HMAX S1/C1, S2/C2, VTUs, with the channel-expansion-and-spatial-reduction conv stacks playing the role of HMAX's increasing receptive-field size and feature complexity at each stage.

**HMAX as the architectural foil — what the user's program adds.** The published Recurrent ViT (2502.10955), PRISM v1, and PRISM v2 are each defined in part by *what HMAX lacks*. HMAX has no attention — the user's program adds the Feedback Transformer (program §1). HMAX has no recurrence — the user's program adds patch-wise LSTM / GridCell-RNN memory (program §2). HMAX has no top-down feedback — the user's program adds bidirectional hierarchical feedback with descending and ascending projections (program §3). HMAX has no learned objective beyond classification — the user's program adds the iterative variational encoder-decoder objective (program §4). The phrase "HMAX-with-attention-and-recurrence" is a fair one-sentence summary of the Recurrent ViT's relationship to HMAX; PRISM v1 and v2 are then further specializations of that recurrent variant for change detection.

**Why HMAX fails at change detection.** The published Recurrent ViT's central empirical demonstration — that recurrence allows the model to detect changes between two images presented in sequence — is precisely the task HMAX cannot solve. HMAX's feedforward sweep over each image produces an activation pattern that is a *static* description of that image; nothing in HMAX integrates information across time. Detecting a change requires comparing two such patterns, which in turn requires a memory state that holds the first image's representation during the second image's processing. The user's program supplies that memory state and, crucially, *integrates* it with the second image's processing via the Feedback Transformer rather than as a downstream comparison step. Kietzmann et al. 2019 (in seed) reports the broader claim that recurrence is required for cortically-faithful object recognition under challenging conditions; the user's program builds on Kietzmann's claim by providing a specific recurrent architecture that supersedes HMAX.

**HMAX's MAX operation vs. the Feedback Transformer's softmax.** HMAX's MAX-over-afferents nonlinearity and the transformer's softmax-over-tokens are formally related: a soft-MAX is the limit of softmax as the temperature goes to zero, and the soft-MAX itself is the limit of $\big(\sum_i x_i^p\big)^{1/p}$ as $p \to \infty$. The Feedback Transformer therefore inherits HMAX's MAX-like selection of dominant input but generalizes it (a) to a *learned*, *content-dependent* weighting rather than a fixed pooling, and (b) to integration of multiple feedback sources (`threads/the_user_architectural_program.md` §1) rather than to a single feedforward pool. The transition from HMAX MAX-pooling to transformer softmax-attention is the central architectural transition the user's program is built around.

**HMAX's invariance-by-pooling as substrate for IT object representations.** The view that IT-level object representations are *constructed* by pooling over view-tuned and position-specific afferents — rather than being innately invariant — is HMAX's central proposal and the framing on which Tanaka 1996 (in seed) and DiCarlo, Zoccolan & Rust 2012 (in seed) build their reviews of IT function. The user's program takes the same view of representation construction but adds that the pooling must be (a) attentionally gated (Reynolds-Heeger normalization, in seed), (b) recurrent (Kietzmann 2019, in seed), and (c) influenced by predictive top-down signals from competing coalitions (program §5, competition-emergent predictive coding).

**HMAX's no-feedback assumption vs. the user's bidirectional hierarchical feedback.** Felleman & Van Essen 1991 (in seed) catalogued the *bidirectional* anatomical connectivity of the visual hierarchy — every feedforward projection has a matching feedback projection. HMAX ignores this anatomical reality. The user's program (`threads/the_user_architectural_program.md` §3) takes the bidirectional connectivity seriously and embeds it as a core architectural commitment: every layer's GridCell-RNN receives both descending and ascending feedback. HMAX is the *feedforward-only* limit of the user's architecture, recoverable by zeroing all ascending and most descending projections.

**HMAX and the RSA-based comparison to brain data.** Kriegeskorte 2008 (in seed) introduced representational similarity analysis (RSA) as a method for comparing model representations to brain measurements. HMAX was an early target of RSA-style comparisons to IT data (Kriegeskorte et al. 2008; Cadieu et al. 2014); modern deep CNNs trained on ImageNet *outperform* HMAX at predicting IT responses, suggesting that learned feature templates capture cortical representations better than HMAX's hand-engineered ones. The user's program, by inheriting both HMAX's architectural template and the modern learned-feature-template advances of CNNs / ViTs, aims to combine the biological grounding of HMAX with the representational power of modern deep models.

**Summary connection.** HMAX is the *minimal* feedforward-hierarchy model of object recognition consistent with Hubel & Wiesel 1962. The user's Recurrent ViT and PRISM systems are *maximal* descendants of the same template, with attention, recurrence, multi-compartmental memory, and bidirectional feedback added to convert a static feedforward filter bank into a recurrent dynamical system capable of temporal integration, contextual modulation, and competition-emergent predictive coding. The lineage Hubel & Wiesel 1962 → HMAX 1999 → DiCarlo 2012 → Kietzmann 2019 → Recurrent ViT 2025 is the through-line of the user's architectural commitment.

## 8. Citations to follow

- `logothetis_pauls_poggio1995_paperclip` — Logothetis, Pauls & Poggio 1995, the IT recording study on paperclip-trained monkeys that HMAX's VTU stage is fit to. Not yet in seed.
- `fukushima1980_neocognitron` — Fukushima's neocognitron, the first explicit hierarchical simple/complex artificial network derived from Hubel & Wiesel; HMAX's direct architectural ancestor. Not yet in seed.
- `poggio_edelman1990_view_based` — Poggio & Edelman 1990, the radial-basis-function view-based recognition model that HMAX's VTU stage operationalizes. Not yet in seed.
- `serre_wolf_poggio2007_robust_object_recognition` — Serre, Wolf, Poggio et al. 2007, the natural-image extension of HMAX with learned S2 features and competitive performance on natural images. Not yet in seed.
- `pasupathy_connor2001_v4_shape` — Pasupathy & Connor 2001, the V4 shape-tuning data that S2 / C2 units are claimed to model. Not yet in seed.
- `gawne_martin2002_max_it` — Gawne & Martin 2002, IT recordings testing the MAX prediction in multi-stimulus displays. Not yet in seed.
- `zoccolan_cox_dicarlo2005_clutter` — Zoccolan, Cox & DiCarlo 2005, the partial refutation showing average-like rather than MAX-like multi-stimulus responses in IT. Not yet in seed.
- `yamins2014_performance_optimized_hierarchy` — Yamins et al. 2014, the demonstration that ImageNet-trained CNNs outperform HMAX at predicting IT responses. Not yet in seed.
- `cadieu2014_dnn_match_it` — Cadieu et al. 2014, RSA-based comparison of CNNs and HMAX to IT data. Not yet in seed.
- `kar2019_evidence_recurrent_it` — Kar, Kubilius, Schmidt, Issa & DiCarlo 2019, the demonstration that recurrence is required for IT to solve challenging-image trials that feedforward CNNs fail. Companion to Kietzmann 2019. Not yet in seed.
- `serre_oliva_poggio2007_rapid_categorization` — Serre, Oliva & Poggio 2007, HMAX-based account of ultra-rapid scene categorization. Not yet in seed.
- `perrett_oram1993_view_invariance` — Perrett & Oram 1993, the early view-tuned-cell account of IT face processing that HMAX builds on. Not yet in seed.
- `tanaka1993_inferotemporal_columns` — Tanaka 1993, the columnar organization of IT object representations, complementing Tanaka 1996 (in seed). Not yet in seed.
- `riesenhuber_poggio2000_models_obj_recognition` — Riesenhuber & Poggio 2000 follow-up review elaborating HMAX. Not yet in seed.
