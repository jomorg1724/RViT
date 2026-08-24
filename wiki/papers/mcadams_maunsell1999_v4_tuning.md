---
id: mcadams_maunsell1999_v4_tuning
title: "Effects of attention on orientation-tuning functions of single neurons in macaque cortical area V4"
authors:
  - "McAdams, Carrie J."
  - "Maunsell, John H. R."
year: 1999
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.19-01-00431.1999"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.19-01-00431.1999"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
concepts:
  - gain-modulation
  - top-down-feedback
  - orientation-selectivity
related:
  - mcadams_maunsell1999_reliability
  - treue_martinez_trujillo1999_feature_attention
  - reynolds_heeger2009_normalization
  - desimone_duncan1995_biased_competition
  - reynolds1999_competitive_v2_v4
  - moran_desimone1985_selective_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_7
status: full
depth: full
last_updated: "2026-05-16"
---

# Effects of attention on orientation-tuning functions of single neurons in macaque cortical area V4

## 1. Abstract

McAdams & Maunsell examined how attention affected the orientation tuning of 262 isolated neurons in extrastriate area V4 and 135 neurons in area V1 of two rhesus monkeys. The animals performed a delayed match-to-sample task in which oriented stimuli were presented in the receptive field of the neuron being recorded; on some trials the animals were instructed to attend to those stimuli, and on others to attend to stimuli outside the receptive field. Orientation-tuning curves were constructed from neuronal responses in the two attentional states and fit with Gaussians. Attention enhanced responses in V4 (median 26% increase) and V1 (median 8% increase), but the *width* of the orientation-tuning curve was not systematically altered by attention. The effect was consistent with a **multiplicative scaling** of the driven response across all orientations. Undriven (spontaneous) activity was not systematically changed by attention.

## 2. Why this matters for us

McAdams & Maunsell 1999 is the canonical demonstration that spatial attention scales V4 orientation-tuning curves *multiplicatively* — the same response-gain mechanism that Treue & Martínez Trujillo establish for feature-based attention in MT. For the user's program this paper is the load-bearing single-unit evidence for treating the cortical implementation of attention as a *gain field over feature-tuned responses* rather than as a tuning-sharpening or additive-offset operator. The Feedback Transformer's element-wise (Hadamard) gating of Q/K/V — $q_i = s_{q,i} \odot (\sum_k c^{(k)}_{q,i})$ — implements precisely this multiplicative integration of feedback onto sensory tuning. The recurrent ViT's multiplicative-feedback variant (paper §6.7) inherits its biological warrant from this paper, and the choice of $\odot$ over $+$ in the user's published architecture is not an arbitrary engineering decision but the implementation-level reflection of the V4 phenomenology McAdams & Maunsell documented.

## 3. Key claims

1. **Attention increases V4 response gain by ≈26% on average.** In a delayed-match-to-sample task with oriented stimuli in the receptive field, attended responses were a median 26% larger than ignored responses.
2. **The same effect is present in V1, but smaller (≈8%).** Attention modulation grows along the ventral hierarchy.
3. **Tuning *width* is not changed by attention.** Gaussian fits to responses across 12 orientations show that the half-width parameter is statistically unchanged between attended and ignored conditions.
4. **The effect is well described as multiplicative scaling.** Attended responses are approximately equal to ignored responses times a fixed gain factor that does not depend on orientation. Equivalently: the response to all orientations is scaled by the same multiplier.
5. **Spontaneous (undriven) activity is not systematically modulated.** The gain is on the *driven* part of the response, not a uniform additive baseline shift.
6. **Multiplicative response gain is dissociable from tuning sharpening.** McAdams & Maunsell explicitly contrast their finding with the prediction of a sharpening-based attention account; their data favor pure gain over sharpening.
7. **Gain effect is graded along the hierarchy.** Both V1 and V4 show the same qualitative signature (multiplicative scaling with no width change), but the *magnitude* of the gain is roughly three times larger in V4 than V1, consistent with cumulative or hierarchically amplified top-down modulation.
8. **Preferred orientation is preserved.** Attention does not shift which orientation a cell represents — it only changes the strength with which the cell signals its preferred input, supporting a "label-preserving gain" view of attentional modulation.

## 4. Methods

**Subjects and task.** Two rhesus macaques performed a delayed match-to-sample task. An oriented Gabor or grating stimulus appeared at one of two locations; one was inside the receptive field of the neuron being recorded, one outside. Trial blocks instructed the monkey to attend to one location and report when a matching stimulus appeared there. The unattended location had stimuli of equivalent physical properties, so any difference in neural response between conditions is attributable to top-down attentional state, not bottom-up input. The use of a delayed match-to-sample paradigm, rather than a simpler cued-detection task, ensures that the monkey *uses* the attended stimulus's orientation information rather than merely orienting toward its location — i.e., it engages featural attention to orientation, not just spatial attention.

**Recordings.** Single-unit recordings from area V4 (n = 262 neurons) and area V1 (n = 135 neurons). Receptive fields were mapped using bar and grating stimuli; oriented test stimuli were then sized and positioned to drive each cell. The V1 sample provides a within-animal control on the magnitude of the attentional effect along the early ventral hierarchy.

**Stimuli.** Oriented stimuli at 12 orientations spanning 0°–180° in 15° steps were presented within the cell's receptive field. Each orientation was tested in both attended and unattended conditions, with trial order randomized within blocks to prevent the monkey from forming orientation-specific expectations within a block.

**Analysis.** Mean firing rate for each (orientation × attentional state) pair was computed. Gaussian tuning curves of the form
$$ r(\theta) = a \cdot \exp\!\big( -(\theta - \theta_0)^2 / (2\sigma^2) \big) + b $$
were fit separately to the attended and ignored conditions. The fitted parameters were compared: amplitude $a$ (driven response gain), preferred orientation $\theta_0$, tuning width $\sigma$, and baseline $b$ (undriven activity). A pure-gain model predicts $a_\text{att} > a_\text{ign}$ with $\sigma, b$ unchanged; a sharpening model predicts $\sigma_\text{att} < \sigma_\text{ign}$; an additive-modulation model predicts $b_\text{att} > b_\text{ign}$ with $a$ unchanged. The three models are formally separable on this dataset.

## 5. Results

The key quantitative findings:

- **V4 gain.** Median response amplitude was 26% higher under attention. The distribution of (attended − ignored) gain ratios was significantly shifted above 1.
- **V1 gain.** Median response amplitude was 8% higher under attention — smaller than V4 but still a significant positive shift, demonstrating that the modulation is present, though attenuated, at the earliest stage of cortical visual processing.
- **Tuning width unchanged.** The fitted Gaussian half-width $\sigma$ was statistically indistinguishable between attended and ignored conditions in both V4 and V1. This directly rules out the *sharpening* account of attentional modulation in this paradigm.
- **Preferred orientation unchanged.** Cells did not shift which orientation drove them best; attention reweighted the response amplitude without rotating tuning. The cell's identity as an orientation detector is preserved.
- **Spontaneous activity unchanged.** Fitted baseline $b$ did not differ systematically between conditions, ruling out a purely additive (DC-offset) account of the attentional modulation. The modulation acts on the *driven* response, not on the resting firing rate.
- **Multiplicative-gain fit quality.** Across the population, attended-vs-ignored response pairs at each orientation lay along a straight line through the origin with slope > 1 — the signature of multiplicative scaling, not of tuning reshaping. The line's slope (the attention-induced gain) was the single parameter that captured the modulation.
- **Robustness across the population.** The multiplicative-scaling description fit individual cells well, not only the population average. The conclusion is not an artifact of pooling cells with heterogeneous attentional signatures.
- **Comparison across areas.** The roughly threefold V4-vs-V1 gain ratio (26% / 8%) provides a within-experiment estimate of how attentional modulation grows along the early ventral hierarchy under identical task and stimulus conditions.

## 6. Critique / limitations

The conclusions rest on Gaussian fits. A more model-free analysis (e.g., normalizing each cell's tuning curve and comparing shapes directly) would be more robust to fit assumptions, though subsequent literature has largely confirmed the multiplicative-gain conclusion.

The study cannot distinguish *multiplicative gain on the input* from *multiplicative gain on the output* of a normalization stage. Reynolds & Heeger (2009) later show that input-side gain combined with divisive normalization can produce response-gain-like behavior under some regimes and contrast-gain-like behavior under others; the McAdams data are compatible with either source. Disambiguating these mechanisms requires varying stimulus contrast — which McAdams & Maunsell did not do — and was the contribution of subsequent work by Reynolds, Pasternak & Desimone (2000) and others.

The 8% V1 effect is smaller than effects reported by other V1 attention studies and barely above the noise floor for individual cells; the population-level shift is real, but the per-cell V1 modulation is weak. Whether the small V1 gain reflects a genuine V1 mechanism or back-propagated V4 modulation via feedback is not addressed here.

The effect size in V4 (26%) is for the gain *factor on top of the unattended response*. This is small relative to gain modulations reported in feature-based attention (where directional attention can produce 30–50% modulation; Treue & Martínez Trujillo 1999) or in some later studies using stronger attention manipulations. It is also small relative to the response modulations that competing stimuli can induce within a receptive field.

The study uses a single, well-isolated stimulus in the receptive field. Effects on attention with multiple competing stimuli in the RF — the biased-competition regime (Reynolds et al. 1999) — are not addressed here. The 26% gain figure is for the isolated-stimulus condition, not for competitive selection, and the multiplicative-gain conclusion may not extend cleanly to the multi-stimulus case.

The mechanism *producing* multiplicative gain is not addressed. The paper documents the phenomenology; the circuit-level implementation (normalization with attentional input, top-down gain field, NMDA-driven persistent modulation, cholinergic modulation, etc.) is left open. Pinning down the mechanism has taken two further decades of work and is still partly unsettled.

Finally, the population-level statistic obscures genuine heterogeneity: not every V4 cell shows multiplicative scaling, and some show small but reliable additive or non-uniform modulations. The 26% median is an aggregate, and the paper does not characterize the subpopulation that deviates from pure multiplicative scaling — leaving open whether attention has functionally distinct sub-effects on different V4 cell classes.

## 7. Connection to our work

This paper is the foundational single-unit evidence for the user's central architectural commitment that attention is implemented as *multiplicative gain on feature-tuned responses*.

**Direct support for Feedback-Transformer multiplicative integration.** The recurrent ViT paper (2502.10955 §6.7) describes three feedback-injection variants: tokens, additive, and multiplicative. The user's Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) commits architecturally to the multiplicative variant via the Hadamard product
$$\alpha_{ij} \propto \big\langle s_{q,i} \odot \sum_k c^{(k)}_{q,i},\; s_{k,j} \odot \sum_k c^{(k)}_{k,j} \big\rangle.$$
McAdams & Maunsell's V4 result is the biological warrant for this choice: real V4 neurons under attentional modulation behave as if their orientation-tuning curve has been scaled by a multiplicative gain factor — exactly what the Hadamard product implements at the level of Q/K projections. An additive feedback would predict a baseline shift; a sharpening feedback would predict a width change; *neither is what V4 does*. Multiplicative feedback is.

**Convergent evidence with Treue & Martínez Trujillo 1999.** Both papers — published in 1999 in adjacent issues — establish the same multiplicative-gain signature, in V4 (spatial attention, McAdams & Maunsell) and in MT (feature-based attention, Treue & Martínez Trujillo). Together they license the user's generalization: attention is gain modulation along whichever dimension is being attended (location, feature, channel). The Feedback Transformer is dimension-agnostic; its $\odot$ acts wherever the feedback projection has support.

**Hierarchical gradient of attention.** The 8% V1 / 26% V4 difference matches the user's multi-compartmental memory design, in which deeper layers carry more abstracted feedback (`thread/the_user_architectural_program.md` §3). The gradient of attentional gain along the ventral stream is consistent with descending projections that progressively concentrate attentional modulation at higher levels of the hierarchy.

**Predictive-coding / biased-competition framing.** McAdams & Maunsell's gain effect is the *neural correlate* of biased-competition's "weighted competitive interaction" (Desimone & Duncan 1995). In the user's competition-emergent-predictive-coding account ([competition-emergent-predictive-coding](research_db/concepts/competition-emergent-predictive-coding.md)), this gain is the mechanism by which a coalition wins the inner-product competition for the attention map. The 26% V4 modulation is a quantitative reference point: a successful Feedback-Transformer-based model should produce comparable attentional gain on its feature-tuned units.

**Constraint on PRISM v2's FiLM modulation.** PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4) is *linear* — both a multiplicative scale and an additive bias on features. McAdams & Maunsell show that the biologically validated effect is *purely multiplicative on the driven response, with no additive shift*. This argues for either zeroing the FiLM additive bias term or using FiLM only on the gain channel — a small design refinement justified by this paper.

**Empirical benchmark.** Beyond architectural warrant, the 26% V4 gain figure provides a concrete *target* against which to assess any model that claims biological plausibility for its attention mechanism. A Feedback-Transformer-based recurrent ViT trained on visual tasks should, when probed on its attended vs. unattended unit responses, exhibit gain modulations on this order of magnitude. A model with much larger modulations (e.g., several-fold gain) is using attention as a gating switch rather than as a graded gain field; a model with much smaller modulations (a few percent) is failing to exploit the multiplicative pathway. McAdams & Maunsell thus serve as a quantitative calibration point for biological-plausibility claims in the user's published Recurrent ViT and in any future multi-hub system.

**Implication for the recurrent ViT's attention-evolution result.** The Food-101 classifier note in the user's program reports that *attention dynamics evolve nontrivially over recurrent passes* — maps focus, defocus, and reactivate. McAdams & Maunsell's pure-gain result implies that such evolution, biologically interpreted, is a story about *gain reweighting* across feature-tuned channels rather than about reshaping or sharpening the channels themselves. The recurrent ViT's evolving attention map is, on this reading, the model's analog of attentional gain settling onto behaviorally relevant features over the course of recurrent computation — a direct functional analog of the McAdams-Maunsell phenomenon, lifted to the level of patch-token attention weights.

**Why not additive or sharpening feedback.** The three injection variants in the Recurrent ViT paper (§6.7) — token concatenation, additive feedback, and multiplicative feedback — are not equally well-motivated biologically. McAdams & Maunsell's null result for both width changes and baseline shifts is precisely the result that rules out sharpening- and additive-style mechanisms as the cortical default. Their data favor the multiplicative variant exclusively. This makes the multiplicative-feedback configuration of the Feedback Transformer the *biologically warranted* default, with the other two retained mainly as ablation baselines.

## 8. Citations to follow

- `mcadams_maunsell1999_reliability` — companion paper on attention-induced response reliability in V4. Already in seed.
- `treue_martinez_trujillo1999_feature_attention` — MT version of the same multiplicative-gain finding for feature-based attention. In seed, full depth.
- `reynolds_heeger2009_normalization` — normalization model that subsumes response gain vs. contrast gain. In seed, full depth.
- `desimone_duncan1995_biased_competition` — competitive framework whose gain-effect prediction this paper confirms. In seed, full depth.
- `reynolds1999_competitive_v2_v4` — companion V4 paper on competitive modulation in multi-stimulus regimes. In seed.
- `moran_desimone1985_selective_attention` — earliest V4 attention recordings (single stimulus vs. competing pair). In seed.
- `martinez_trujillo_treue2004_attention_tuning` — follow-up extending feature-similarity gain to tuning curves. Not yet in seed.
- `connor_preddie_gallant1997_v4_attention` — earlier V4 attention work using shifted stimuli. Not yet in seed.
- `reynolds_pasternak_desimone2000_attention_contrast` — contrast-gain vs. response-gain disambiguation, directly extending this paper. Not yet in seed.
- `cohen_maunsell2009_attention_pop_response` — population-level extension of single-cell gain effects in V4. Not yet in seed.
