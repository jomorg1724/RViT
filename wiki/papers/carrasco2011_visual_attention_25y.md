---
id: carrasco2011_visual_attention_25y
title: "Visual attention: the past 25 years"
authors:
  - "Carrasco, Marisa"
year: 2011
venue: "Vision Research"
doi: "10.1016/j.visres.2011.04.012"
arxiv: ""
url: "https://doi.org/10.1016/j.visres.2011.04.012"
tags:
  - visual-attention
  - psychophysics
  - review
  - posner-cuing
concepts:
  - cueing-effect
  - validity-effect
  - gain-modulation
  - attentional-spotlight
  - divisive-normalization
  - psychometric-function
  - chronometric-function
  - precision-weighting
related:
  - cameron2002_covert_attention_contrast
  - lu_dosher1998_external_noise
  - reynolds_heeger2009_normalization
  - desimone_duncan1995_biased_competition
  - treue_martinez_trujillo1999_feature_attention
  - posner1980_orienting
  - feldman_friston2010_attention_free_energy
  - moran_desimone1985_selective_attention
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_1
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual attention: the past 25 years

## 1. Abstract

Carrasco's 2011 *Vision Research* anniversary review synthesizes twenty-five years of psychophysical, electrophysiological, and neuroimaging research on *covert* visual attention — the selective deployment of processing resources without eye movements. The review is organized around two principal questions: (a) *why* attention is necessary (selection under limited capacity); and (b) *how* attention alters early visual processing. The paper distinguishes the major attention types — **spatial endogenous** (sustained, voluntary, central-cue-driven), **spatial exogenous** (transient, involuntary, peripheral-cue-driven), and **feature-based** (location-independent enhancement of a target feature value) — and surveys their measurable effects on *discriminability* (d′, accuracy, threshold) and *appearance* (perceived contrast, perceived spatial frequency, perceived speed). Carrasco emphasizes that covert attention does not merely speed responses (the Posner-style RT facilitation) but actually modifies the *spatial filters* through which the visual system samples the world: it boosts contrast sensitivity, increases spatial resolution, sharpens orientation tuning, and shifts appearance toward greater perceived intensity. The mechanistic synthesis converges on *gain modulation* — predominantly *contrast gain* for exogenous spatial attention and a mixture of *response gain* and contrast gain for endogenous and feature-based attention — formalized by the Reynolds & Heeger (2009) normalization model. The review concludes that attention is best understood as a *multiplicative modulation* of early visual responses, with the specific functional form (contrast vs response gain) depending on the relative sizes of the attention field and stimulus.

## 2. Why this matters for us

This is the canonical 25-year synthesis of visual-attention research and is the reason the user's program treats attention as multiplicative gain rather than as additive bias or as a routing switch. The Feedback Transformer's Hadamard-product structure ($q_i = s_{q,i} \odot \sum_k c^{(k)}_{q,i}$) is the architectural commitment that maps onto the *contrast-gain* mechanism Carrasco identifies as the dominant empirical signature of covert attention. The Recurrent ViT paper (2502.10955) cites this review as ref [1] precisely because every cued-attention claim in that paper inherits its empirical justification from the body of work Carrasco summarizes here.

## 3. Key claims

1. **Covert attention is real and functionally distinct from eye movement.** Attention to a location without fixating it produces measurable performance and appearance changes; the effect cannot be reduced to oculomotor preparation alone (though there is functional overlap with FEF / SC pre-saccadic activity).
2. **Three principal varieties of covert attention exist.** Endogenous (sustained, voluntary, ~300 ms time-to-engage), exogenous (transient, involuntary, peaks ~100 ms after a peripheral cue then decays), and feature-based (spatially global enhancement of a feature value, e.g., direction or color).
3. **Attention improves *discriminability*, not just decision criterion.** Across orientation, contrast, spatial-frequency, motion, and visual-search tasks, attention raises d′. This rules out a purely decisional account.
4. **Attention shifts the contrast psychometric function leftward (contrast gain) for exogenous cues.** Cameron, Tai & Carrasco (2002) and related psychophysics show the threshold shift; this is consistent with input-side multiplicative gain on the stimulus.
5. **Attention can scale the contrast psychometric function vertically (response gain) when the attention field is small relative to the stimulus.** The Reynolds & Heeger (2009) normalization model predicts the contrast-gain vs response-gain regime as a function of the attention-field / stimulus-size ratio; this prediction is borne out across paradigms.
6. **Attention increases spatial resolution at attended locations.** Yeshurun & Carrasco showed that attention can *help* on tasks where high resolution is beneficial (peripheral acuity) but can *hurt* on tasks where the local resolution is already too fine (texture segmentation at small scales) — direct evidence that attention modifies the *filters*, not merely the readout.
7. **Attention alters appearance, not just performance.** Carrasco, Ling & Read (2004) demonstrated that attended Gabor patches are perceived as having *higher contrast* than physically identical unattended patches; analogous shifts apply to perceived spatial frequency, gap size, flicker rate, and speed.
8. **Feature-based attention spreads globally across the visual field.** Enhancement of a feature value (e.g., upward motion) modulates neurons tuned to that feature throughout the visual field, including in unattended locations — distinguishing it from spatial attention.
9. **Attention sharpens tuning curves.** Single-unit recordings (Reynolds, Treue, Martinez-Trujillo) and human psychophysics show narrower orientation- and direction-tuning curves under attention.
10. **A normalization model unifies the findings.** Divisive normalization with an attention-gain field accounts for contrast-gain, response-gain, tuning sharpening, and surround-suppression effects within a single equation.

## 4. Methods

This is a narrative review, not an empirical paper, so the "methods" section catalogues the *paradigms* it synthesizes:

- **Posner spatial-cuing paradigm.** Central symbolic cue (endogenous) or peripheral abrupt-onset cue (exogenous), valid/invalid/neutral conditions, RT and accuracy as dependent measures.
- **Contrast psychometric function.** Proportion-correct (typically 2AFC orientation or detection) as a function of stimulus contrast, fit with a Weibull or logistic. Threshold and slope parameters extracted per condition.
- **External-noise paradigm (Lu & Dosher).** Performance vs external-noise level traces out a signature for *signal enhancement*, *external-noise exclusion*, or *internal-noise reduction*; covert attention typically shows signal-enhancement under low-noise and external-noise-exclusion under high-noise.
- **Texture-segmentation paradigm.** Test for the "central performance drop" — when attention helps vs hurts segmentation reveals whether attention is modifying the spatial filter.
- **Equivalent-input-noise / equivalent contrast.** Match an attended condition to an unattended condition by adjusting physical contrast; the matched contrast quantifies the attentional gain.
- **Feature-cuing.** Cue a feature value (e.g., "red", "leftward motion"); measure performance at all locations to dissociate spatial from feature-based effects.
- **Single-unit / fMRI BOLD.** Attentional modulation of contrast-response functions in V1–V4, MT, MST; sharpening of tuning curves in feature-attended conditions.

The review's analytical core is the **Reynolds & Heeger (2009) normalization model** of attention: a stimulus drive $E(x, \theta)$ is multiplied by an attention gain field $A(x, \theta)$, then divisively normalized by a suppressive pool. Whether attention produces contrast gain or response gain falls out of the ratio between the size of $A$ and the size of $E$.

## 5. Results

The review's principal *quantitative* claims, drawn from the literature it synthesizes:

- **Threshold shifts under exogenous attention.** Cued thresholds are 10–30% lower than neutral thresholds in clean (low-noise) orientation- and contrast-discrimination tasks (Cameron, Tai & Carrasco 2002; Lu & Dosher 1998).
- **Appearance shifts.** A 22%-contrast attended Gabor is perceived as roughly equal in contrast to a 28% unattended Gabor — i.e., attention produces an apparent contrast boost of ~6 percentage points at intermediate base contrasts (Carrasco, Ling & Read 2004).
- **Spatial-resolution effects.** Yeshurun & Carrasco's texture-segmentation studies show attention *impairs* segmentation at the eccentricities where intrinsic resolution exceeds the optimal scale for the texture — direct behavioral evidence for an attention-induced *narrowing* of spatial filters.
- **Time courses.** Exogenous attention peaks 100–120 ms post-cue and decays by 300 ms; endogenous attention engages over 200–300 ms and is sustainable for seconds (Nakayama & Mackeben 1989).
- **Normalization-model fits.** The Reynolds-Heeger model fits both contrast-gain (large stimulus, narrow attention) and response-gain (small stimulus, broad attention) regimes with the same parameter set, switching regimes purely as a function of stimulus/attention-field size.
- **Cortical modulation.** BOLD amplitude in V1–V4 increases 10–30% at attended locations; single-unit firing rates in V4/MT show comparable multiplicative scaling, with the gain factor depending on the contrast of the stimulus (Reynolds, Pasternak, Desimone 2000).

## 6. Critique / limitations

The review is comprehensive but inherits the field's load-bearing assumptions:

- **Gain modulation is a phenomenological description, not a mechanism.** Whether the underlying neural process is gain modulation per se, divisive normalization, precision-weighting (Feldman & Friston 2010), or biased competition (Desimone & Duncan 1995) is left as an open theoretical question. The review *prefers* the normalization framing but acknowledges that several frameworks can fit the same data.
- **The contrast-gain vs response-gain distinction is a fit-quality argument.** Different studies, using different stimulus and attention-field sizes, will favor one or the other; the normalization model rescues this by predicting the regime, but the data themselves do not uniquely determine the underlying form.
- **Covert vs overt overlap.** The premotor theory of attention argues attention is essentially planned-but-not-executed eye movement; Carrasco resists this reduction but the FEF/SC microstimulation work shows real causal coupling between the two systems.
- **Sustained-attention / temporal-attention coverage is thin.** The review emphasizes spatial and feature-based attention; temporal expectation, rhythmic attention, and prediction-driven attention receive much less treatment despite being central to subsequent work (Nobre, Jensen, etc.).
- **Object-based attention is treated relatively briefly.** Subsequent work (Scholl, Egly-Driver-Rafal cuing) has substantially elaborated object-based effects.
- **Causal interventions in humans remain limited.** Most causal evidence comes from monkey microstimulation and human TMS; the human-psychophysics core is necessarily correlational.

## 7. Connection to our work

This review is the empirical and conceptual backbone of the user's commitment to *attention as multiplicative gain*. The connections to the architectural program are several:

**Multiplicative gain ↔ Feedback Transformer Hadamard structure.** Carrasco's central conclusion — that attention is gain modulation on early visual responses — is precisely what the Feedback Transformer's element-wise multiplication of sensory and feedback Q/K/V tensors implements. The architectural form $q_i = s_{q,i} \odot \sum_k c^{(k)}_{q,i}$ is not arbitrary: it is the computational realization of contrast gain. The Recurrent ViT paper's "multiplicative feedback" variant (§6.7 of 2502.10955) is the operationalization Carrasco's review licenses.

**Posner cuing as the recurrent ViT's evaluation paradigm.** The cued-attention experiments in the Recurrent ViT paper are direct AI analogs of the Posner-style paradigms Carrasco synthesizes. The validity-effect, the cued-RT advantage, and the discriminability boost at cued locations are all phenomena the user's model should reproduce — and Carrasco's review establishes the quantitative targets.

**Contrast-gain regime for the recurrent ViT.** Cameron, Tai & Carrasco (2002) — already in the database — is the key empirical anchor for the *contrast-gain* signature: leftward shift of the contrast psychometric function rather than vertical scaling. The recurrent ViT's psychometric function (proportion-correct vs stimulus contrast at cued vs uncued locations) should likewise show a leftward shift if its attention mechanism is architecturally faithful to human attention.

**Normalization-model connection to biased competition.** Reynolds & Heeger (2009), the synthetic model Carrasco endorses, is a divisive-normalization formalization of the Desimone & Duncan (1995) biased-competition account — both of which appear in the user's `the_user_architectural_program` thread. The user's "competition-emergent predictive coding" (§5 of that thread) treats biased competition as the cellular-level instance of a more general coalition-level competition; Carrasco's review provides the psychophysical grounding for this competitive-attention picture.

**Feature-based attention and global feedback.** Carrasco's treatment of feature-based attention as *spatially global* (boosts the target feature value across the entire visual field, including unattended locations) maps onto the Feedback Transformer's design choice that feedback from a feature-tuned memory state modulates *all* tokens, not just spatially-cued ones. This is the architectural realization of feature-based attentional spread.

**Precision-weighting alternative.** Carrasco notes — without endorsing — that the gain-modulation findings can be reframed as *precision-weighting* in a hierarchical predictive-coding system (Feldman & Friston 2010). This is the framing the user's program ultimately favors: attention is precision over feedback signals, which appears as multiplicative gain in the linearized regime. Carrasco's review is thus consistent with both the engineering reality (Hadamard product) and the predictive-coding interpretation.

**PRISM v1 connection.** PRISM v1's FiLM modulation (`THESIS.md` §2.4) is an additive-then-multiplicative modulation of feature maps; Carrasco's review supports the multiplicative half. The pure prediction-error pathway in PRISM v1 is consistent with the precision-weighted reformulation of Carrasco's findings.

The recurrent ViT paper cites Carrasco 2011 as ref [1] — the single most-cited general reference on visual attention in the cognitive-science literature. Any future manuscript from the user's program that argues for multiplicative attention, cued attention, or feature-based attention should cite this review as the empirical foundation.

## 8. Citations to follow

- `reynolds_heeger2009_normalization` — the normalization model of attention that Carrasco endorses as the unifying framework. Already in seed at full depth.
- `cameron2002_covert_attention_contrast` — the key contrast-gain psychometric-function paper. Already in seed at full depth.
- `lu_dosher1998_external_noise` — the external-noise paradigm for diagnosing attentional mechanism. In seed, full depth.
- `desimone_duncan1995_biased_competition` — the biased-competition framework that the normalization model formalizes. In seed.
- `treue_martinez_trujillo1999_feature_attention` — feature-based attention's global spread. In seed.
- `posner1980_orienting` — the foundational spatial-cuing paradigm. In seed.
- `carrasco_ling_read2004_attention_appearance` — attention alters appearance, not just performance. Not in seed.
- `yeshurun_carrasco1998_attention_resolution` — attention modifies spatial resolution. Not in seed.
- `pestilli_carrasco2005_attention_gain` — Pestilli & Carrasco follow-up quantifying the gain factor. Not in seed.
- `feldman_friston2010_attention_free_energy` — precision-weighting reframing of attentional gain. In seed at full depth.
- `moran_desimone1985_selective_attention` — early single-unit evidence for attentional gating in extrastriate cortex. Listed in `the_user_architectural_program` open debts.
