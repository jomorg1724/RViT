---
id: lemeur2006_coherent_attention
title: "A coherent computational approach to model bottom-up visual attention"
authors:
  - "Le Meur, Olivier"
  - "Le Callet, Patrick"
  - "Barba, Dominique"
  - "Thoreau, Dominique"
year: 2006
venue: "IEEE TPAMI"
doi: "10.1109/TPAMI.2006.86"
arxiv: ""
url: "https://people.irisa.fr/Olivier.Le_Meur/publi/LeMeur_IEEEPAMI.pdf"
tags:
  - saliency-models
  - visual-attention
  - methodology
concepts:
  - priority-map
  - divisive-normalization
  - attentional-spotlight
  - orientation-selectivity
  - gabor-receptive-fields
related:
  - itti_koch2001_saliency_review
  - koch_ullman1984_winner_takes_all
  - mehrani_tsotsos2023_attention_grouping
  - wolfe2021_guided_search_6
  - treisman_gelade1980_feature_integration
  - hassanin2024_attention_dl_survey
  - hubel_wiesel1962_receptive_fields
  - reynolds_heeger2009_normalization
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_27
status: full
depth: full
last_updated: "2026-05-16"
---

# A coherent computational approach to model bottom-up visual attention

> **Sourcing note.** Deepened from the author's posted manuscript (Le Meur, IRISA copy at `https://people.irisa.fr/Olivier.Le_Meur/publi/LeMeur_IEEEPAMI.pdf`); cross-checked against the PubMed record (PMID 16640265 — the correct PMID; the stub's reference to 16683053 appears to be a transcription error). The paper is IEEE TPAMI vol. 28 no. 5, pp. 802–817, May 2006, DOI `10.1109/TPAMI.2006.86`. Quantitative numbers below come directly from the manuscript's Tables 3–6.

## 1. Abstract

The paper proposes a bottom-up saliency model whose stages each correspond to a documented property of the human visual system (HVS) and which is built from a single "coherent psychovisual space" rather than from an ad hoc cascade of feature contrasts. The pipeline takes a still color image through three stages — visibility (Krauskopf opponent-color transform, contrast sensitivity functions, perceptual decomposition into 17 achromatic and 5+5 chromatic subbands, intra- and inter-channel masking), perception (achromatic-channel reinforcement by chromatic context plus oriented difference-of-Gaussian center–surround inhibition), and perceptual grouping (long-range facilitative interactions implemented with Butterfly filters along the preferred orientation) — and produces a saliency map. The model is calibrated against an eye-tracking experiment in which up to 40 observers free-viewed 46 natural images for 15 s, and is compared against Itti et al. 1998 on 10 original color pictures using linear correlation coefficient and Kullback–Leibler divergence between predicted and human fixation-density maps. With a central-Gaussian weighting that reflects the eye-tracking experimental constraints, the proposed model reaches an average correlation of 0.70 vs. Itti's 0.66 (a 6% relative gain at 14 s viewing) and improves KL by roughly 10%. The paper is offered both as a model of involuntary attention and as an engineering tool for image browsing, coding, and quality assessment.

## 2. Why this matters for us

Le Meur et al. 2006 is the most thoroughly psychophysics-grounded entry in the bottom-up-saliency lineage that begins with Koch & Ullman 1985 and that Itti & Koch 2001 reviews. For our purposes it is the *strongest version of the hand-engineered saliency model* — i.e., the most generous opponent against which the user's program (learned attention in the Recurrent ViT, prediction-error-driven attention in PRISM) should be benchmarked. It is cited as ref [27] in the Recurrent ViT paper (arXiv:2502.10955) precisely because it is the canonical "coherent psychovisual" saliency model that the deep-learning attention literature displaces. The paper also operationalizes several mechanisms — contrast normalization to a visibility threshold, masking, oriented long-range facilitation — that re-appear as learned phenomena in deep attention models and that our work claims emerge from end-to-end training rather than from explicit construction.

## 3. Key claims

1. Bottom-up visual attention can be modeled as a cascade of three biologically-motivated stages — visibility, perception, perceptual grouping — that operate within a single "coherent psychovisual space" rather than as independent feature-contrast pipelines.
2. Transforming RGB into Krauskopf's $(A, Cr_1, Cr_2)$ opponent space and decomposing each component into psychovisually-defined subbands (17 for the achromatic component, 5 each for $Cr_1$ and $Cr_2$, with non-dyadic radial selectivity and orientation selectivity that grows with radial frequency) gives a substrate in which contrast sensitivity and masking can be applied uniformly.
3. Normalizing each subband by its own differential visibility threshold $T_{i,j,C}(x,y) = T^{intra}_{i,j,C} \prod T^{inter}_{i,j,C' \to i,j,C}$ produces feature maps in units of "just-noticeable difference," so that signals from different channels and modalities can be combined without ad hoc per-channel scaling.
4. Achromatic conspicuity should be reinforced where it co-occurs with chromatic contrast: $R^{(2)}_{i,j,A} = R^{(1)}_{i,j,A}(1 + \eta_{Cr_1}\Delta_{Cr_1} + \eta_{Cr_2}\Delta_{Cr_2})$, where the $\Delta$'s are locally oriented chromatic gradients aligned with the achromatic subband's preferred orientation.
5. Oriented center–surround inhibition (a difference-of-Gaussians weighting elongated along the subband's orientation) suppresses subband responses that fall in extended uniform regions, mimicking non-classical-receptive-field modulation in V1.
6. Long-range facilitation via Butterfly filters along the preferred orientation strengthens responses that are part of a co-aligned, collinear contour — a Gestalt grouping mechanism motivated by Kapadia et al.'s primate physiology of long-range horizontal connections.
7. With a center-biased Gaussian weighting (forced by the eye-tracking experimental setup, in which observers fixate the screen center at stimulus onset), the proposed model outperforms Itti's reference saliency model in linear correlation with human fixation density by about 6% on average across viewing times of 4 s, 10 s, and 14 s, and reduces Kullback–Leibler divergence to human maps by roughly 10%.
8. Disabling the achromatic-reinforcement-by-chromatic-context module and the visual masking modules degrades performance, demonstrating that both biologically-motivated mechanisms make distinct contributions to the saliency prediction.

## 4. Methods

The pipeline (their Fig. 3) processes a still color picture through three sequential stages.

**Visibility.** RGB is transformed to LMS cone responses, then to Krauskopf's opponent space by the linear map
$$ (A, Cr_1, Cr_2)^\top = M \cdot (L, M, S)^\top, \quad M = \begin{pmatrix} 1 & 1 & 0 \\ 1 & -1 & 0 \\ -0.5 & -0.5 & 1 \end{pmatrix} $$
where $A$ is the pure achromatic axis and $Cr_1, Cr_2$ are the red–green and blue–yellow chromatic axes. Each component is filtered by its CSF: Daly's 2D anisotropic CSF for $A$; the analytic forms (their eqs. 2, 3)
$$ S_{Cr_1}(w,\theta) = \frac{33}{1 + (w/5.52)^{1.72}}(1 - 0.27\sin 2\theta), \quad S_{Cr_2}(w,\theta) = \frac{5}{1 + (w/4.12)^{1.64}}(1 - 0.24\sin 2\theta) $$
are low-pass with cutoffs of 5.5 and 4.1 cycles per degree respectively, encoding the known greater sensitivity to low- and mid-frequency chromatic information. Each component is then decomposed into psychovisual subbands: 17 for $A$ (four radial crowns I–IV with increasing orientation selectivity, non-dyadic radial spacing); 5 each for $Cr_1$ and $Cr_2$ (two crowns). Each subband $R^{(0)}_{i,j,C}(x,y)$ is normalized by its differential visibility threshold $T_{i,j,C}$, which is itself the product of an intra-channel masking term (Daly's pedestal-effect model for $A$, Le Callet's model for $Cr_1, Cr_2$, their eqs. 4–5) and inter-channel masking terms (Models A and B, their eqs. 6–7, capturing both facilitation and pure masking depending on subband identity; their Table 2 enumerates the 30+ admissible cross-channel interactions). The output $R^{(1)}_{i,j,C}(x,y) = R^{(0)}_{i,j,C}(x,y)/T_{i,j,C}(x,y)$ is in units of just-noticeable visibility.

**Perception.** Two operations are applied to the achromatic subbands. *Achromatic reinforcement by chromatic context* multiplies each $R^{(1)}_{i,j,A}$ by $(1 + \eta_{Cr_1}\Delta_{Cr_1} + \eta_{Cr_2}\Delta_{Cr_2})$, where the $\Delta$'s are locally oriented chromatic gradients computed in an anisotropic neighborhood aligned with subband $(i,j)$'s preferred orientation. *Oriented center–surround inhibition* subtracts a DoG-weighted local average from the subband: $R^{(3)}_{i,j,A} = H(R^{(2)}_{i,j,A} - R^{(2)}_{i,j,A} * \omega_{\sigma_x,\sigma_y})$, with $H$ a half-wave rectifier, and $\omega$ the normalized rectified part of a DoG kernel rotated to the subband's preferred orientation.

**Perceptual grouping.** Long-range collinear facilitation is implemented by a Butterfly filter $B_{i,j,A}(x,y) = D_{i,j}(x,y) \cdot C_r(x,y) * G(x,y)$, the product of a directional cosine bump $D_{i,j}$ (eq. 16, opening angle $\alpha$ tuned to the subband's orientation selectivity) with a circular proximity term $C_r$ smoothed by a 2-D Gaussian. The filter is split into two half-butterflies $B^0, B^1$; the facilitative factor (eq. 17) is the ratio of their summed responses to a saturating denominator, and reinforces collinear, co-oriented configurations. The final subband $R^{(4)}_{i,j,A} = R^{(3)}_{i,j,A}(1 + \kappa^{iso} f^{iso}_{i,j,A})$ amplifies regions that participate in long contours, mimicking Gestalt continuation.

**Saliency map and central bias.** The achromatic subbands are summed directly across orientation and crown to give a saliency map $S(x,y)$. To match the experimental constraint that observers fixated the screen center at stimulus onset, $S$ is multiplied by an anisotropic Gaussian $\exp(-(x-x_0)^2/2\sigma_x^2 - (y-y_0)^2/2\sigma_y^2)$ with $\sigma_x \approx 2.5°$ optimized on 18 calibration pictures (their Fig. 7).

**Eye-tracking ground truth.** Forty-six pictures (10 originals × 4-5 degraded versions) were free-viewed by up to 40 observers for 15 s on a calibrated CRT (Cambridge Research Corp. eye tracker, accuracy < 0.5°). Fixations were aggregated across observers and smoothed by a 2-D Gaussian to give a fixation-density map per image (their Fig. 2).

## 5. Results

The evaluation compares the proposed model against Itti et al. 1998 on the 10 original color pictures. The metrics are linear correlation coefficient (CC) between the predicted and the human density map and the Kullback–Leibler divergence (KL).

**Correlation coefficient (their Tables 3, 4).** Without the central-Gaussian weighting, the proposed model averages CC = 0.44 against Itti's 0.37 (t-test $p > 0.3$, not significant). With the central Gaussian, the proposed model reaches 0.70 vs. Itti's 0.66 (t-test $p > 0.02$). A pure central Gaussian alone (no saliency content) gives CC = 0.64, slightly worse than either bottom-up model — i.e., most of the CC headline reflects the central-fixation prior, with the saliency models adding a few percentage points on top. The 6% relative gain of the proposed model over Itti's holds across viewing times of 4, 10, and 14 seconds (their Table 4, rows "Correlation coefficients").

**Kullback–Leibler divergence (their Tables 4, 5).** The proposed model improves KL over Itti's by 1.5% at 4 s, 12.5% at 10 s, and 13.0% at 14 s. The image-wise comparison against the average inter-observer $KL_{avg}$ (their Table 5) shows that for pictures with a single small region of interest (e.g., *Kayak*), Itti's iterative normalization wins; for pictures with many salient regions, the proposed model's coherent visibility normalization wins.

**Component ablation (their Table 6).** With both viewing times, the full model averages CC = 0.50 (14 s) / 0.45 (4 s). Disabling visual masking (VM) drops these to 0.46 / 0.41 and disabling achromatic reinforcement by chromatic context (AR) to 0.47 / 0.43. The masking module contributes roughly +0.04 CC (about 9% relative gain) and is largest at stimulus onset, consistent with its bottom-up nature. The achromatic reinforcement contributes +0.03 CC, concentrated on pictures with strong color content (e.g., *Kayak*, *Bikes*).

**Application example (their §5.4, Fig. 9).** Saliency-based thumbnails — crops of the most salient region — preserve image content better than down-sampled thumbnails on a 9-image gallery.

## 6. Critique / limitations

- **Central bias does most of the work.** The pure central-Gaussian weighting alone gives CC = 0.64 against the proposed model's 0.70, and the t-test on the unweighted comparison against Itti's model is not significant ($p > 0.3$). The headline 6% advantage is therefore a small marginal gain on top of a strong fixation prior that the model does not derive from first principles but installs by hand to compensate for the eye-tracking experimental design. Subsequent benchmarks that decorrelate from central bias (e.g., shuffled-AUC) tend to compress these advantages further.
- **No top-down or temporal mechanism.** The model is strictly bottom-up and static. It has nothing to say about task set, scene gist, or eye-movement history once the saliency map is computed; like Itti–Koch, it predicts the same scanpath for the same image every time, modulo WTA + inhibition of return that is not actually implemented here (the published model produces a saliency map only; the WTA is shown in Fig. 3 as the visualization on 20 fixation points but not part of the quantitative evaluation).
- **Hand-engineered everywhere.** Every parameter is set by appeal to psychophysics (Daly 1993, Le Callet 2001) or fixed at biologically-plausible defaults. The 17-subband decomposition, the masking models A and B, the Butterfly opening angle, the achromatic-reinforcement gains $\eta_{Cr_1}, \eta_{Cr_2} = 1$, the central-Gaussian $\sigma_x = 2.5°$ — none are learned. Modern learned-saliency models (DeepGaze, SALICON, ML-Net; see `hassanin2024_attention_dl_survey`) close the headline gap and surpass this model on benchmark datasets by learning all of these knobs end-to-end.
- **Engineering vs. neuroscience claim conflation.** The paper oscillates between treating the pipeline as a *model of involuntary attention* and as a *useful tool for image coding and browsing*. The two claims are not equivalent. The image-coding application (Fig. 9) is unaffected by whether the central bias reflects neural priority maps or experimental artifact, but the neural-modeling claim is.
- **Feature channels remain fixed.** As in Itti–Koch, the channel set (intensity, two chromatic opponents, four orientations) is committed in advance. Faces, text, and other category-specific saliency are out of scope unless they happen to manifest as low-level contrast. This is the same critique that motivated DeepGaze-class models.
- **Color information enters in only one direction.** Chromatic context reinforces achromatic conspicuity, but the final saliency map is computed solely from achromatic subbands. Pure-chromatic saliency (isoluminant red on green) is by construction outside the model's expressive range — a substantive limitation given that this configuration is the prototypical pop-out demonstration.
- **No account of dynamic stimuli.** The model handles still images. Motion saliency (the channel that several subsequent saliency models add) is absent, which limits comparability to the change-detection regime of the Recurrent ViT.
- **No mechanism for unexpected change.** Like Itti–Koch, the saliency of a location depends only on its own current features and their surround. A region whose features are unchanged but whose *content has been swapped* (the change-detection regime) is no more salient than before the change, unless the new content happens to be locally more contrastive. The model cannot in principle solve the cued change-detection task this manuscript targets.

## 7. Connection to our work

Le Meur et al. 2006 belongs to a tight cluster of pre-deep-learning saliency papers (Koch & Ullman 1985 → Itti, Koch & Niebur 1998 → Itti & Koch 2001 → Le Meur et al. 2006) that the user's published Recurrent ViT explicitly contextualizes its learned attention against. The connection runs along the same axes laid out in `itti_koch2001_saliency_review.md` §7, with three specific refinements that this paper enables.

**1. The strongest hand-engineered opponent.** Itti–Koch is the textbook contrast target; Le Meur et al. is the *psychophysically-tuned* version with explicit visibility-threshold normalization, intra/inter-channel masking, and Gestalt-style long-range facilitation. When framing the Recurrent ViT and PRISM as displacing the saliency-map abstraction, Le Meur et al. is the version of the abstraction that we should cite for the claim that we are not displacing a strawman. The headline numbers (CC = 0.70 with center weighting, CC = 0.44 without) are also the right baseline numbers to keep in mind: any learned attention model that materially improves over 0.70 on a central-Gaussian-weighted human-fixation comparison is doing real work beyond fixation-prior matching.

**2. Conceptual sibling, not foundation, of the Itti–Koch architecture.** Le Meur et al. share the Koch & Ullman 1985 skeleton — feature pyramids, oriented channels, fusion, saliency map, optional WTA — but build a different normalization machine inside it: rather than Itti's iterative $(M - \bar m)^2$ operator that promotes maps with one dominant peak, they normalize every subband by its own differential visibility threshold, then apply oriented center–surround DoG inhibition. Both schemes reduce to *divisive normalization* on subband responses — Le Meur's masking pipeline is in fact a multi-channel divisive normalization with experimentally-fitted gain functions (their eqs. 4–8). This connects the saliency-model lineage to the Reynolds–Heeger normalization-model lineage on the neural side (`reynolds_heeger2009_normalization`) and, on the deep-learning side, to the divisive normalization that emerges inside trained CNN / ViT attention maps (cf. `hassanin2024_attention_dl_survey`).

**3. Phenomena the user's program inherits even without inheriting the architecture.** Several Le Meur mechanisms reappear as *emergent* behaviors that we predict (and to some extent observe) in the Recurrent ViT and PRISM. (i) *Visibility-threshold normalization* — the Recurrent ViT's softmax over learned Q/K projections is structurally a normalization step that should map to JND-like units after task-driven training. (ii) *Achromatic reinforcement by chromatic context* — cross-channel modulation falls out of multi-head attention's mixing of feature subspaces; the user's Feedback Transformer (§1 of `the_user_architectural_program.md`) makes this fully general across arbitrary feedback sources, of which Le Meur's chromatic gradient is just one hard-coded instance. (iii) *Long-range collinear facilitation* — the Butterfly filter implements precisely the kind of oriented long-range interaction that vision-transformer attention can in principle learn, since attention is not constrained to local neighborhoods. The user's eye-tracking results (`the_user_architectural_program.md` §6) are the right empirical testbed for whether this emerges without the explicit Butterfly construction.

**4. Why we cite this paper, not just Itti–Koch.** The Recurrent ViT paper cites both Itti & Koch 2001 (ref [26]) and Le Meur et al. 2006 (ref [27]) because Le Meur et al. is the canonical reference *for the version of bottom-up saliency that takes psychophysical evidence seriously*. Citing only Itti–Koch reads as critiquing a 25-year-old skeleton; citing Le Meur et al. anchors the contrast against the most carefully constructed version of the same idea that the pre-deep-learning saliency literature produced. For the manuscript's framing of learned vs. engineered attention this matters: we are claiming that end-to-end training subsumes not just the 1998 Itti–Koch normalization but also the 2006 Le Meur visibility-threshold + masking + Butterfly machinery.

**5. The change-detection regime is still outside the model's scope.** As with Itti–Koch, Le Meur et al. compute saliency from the current image alone, with no memory and no expectation about future input. The cued change-detection task in the Recurrent ViT paper has the property that the *changed location may have lower bottom-up saliency than other locations in the scene* (a small color shift, a moved object). The Le Meur pipeline has no architectural hook to detect this — there is no $H^{(t-1)}$ to compare against, no prediction-error map (PRISM's $S_t = \tilde X_t - \hat X_t$), no recurrent state at all. This is the cleanest way to phrase what learned, recurrent, memory-conditioned attention buys that the strongest hand-engineered saliency model cannot.

**Useful residue for our writing.** When we need a *concrete number* for "what a strong bottom-up saliency model predicts about human fixations on natural images," CC = 0.70 (with central Gaussian, 14 s viewing) and the +6%/+10% margins over Itti–Koch are the right defaults. When we need the *psychophysical anchor* for divisive normalization as a saliency mechanism, the chain of masking equations 4–8 is the right citation. When we need the *theoretical position to displace*, the three-stage visibility → perception → grouping cascade is the canonical pre-deep-learning architecture and the Recurrent ViT's learned attention is its successor.

## 8. Citations to follow

- `koch_ullman1984_winner_takes_all` — already in seed; the architectural skeleton the model inherits.
- `itti_koch2001_saliency_review` — already in seed; the canonical review and the explicit comparison target.
- `reynolds_heeger2009_normalization` — already in seed; the principled formulation of divisive normalization that subsumes the masking pipeline here.
- `hassanin2024_attention_dl_survey` — already in seed; documents the displacement of pre-deep-learning saliency by learned models on benchmark datasets.
- `mehrani_tsotsos2023_attention_grouping` — already in seed; the most recent saliency-grouping work that should be read alongside Le Meur's perceptual-grouping stage.
- `wolfe2021_guided_search_6` — already in seed; the competing top-down-weighted saliency framework that the bottom-up models are pitted against.
- `treisman_gelade1980_feature_integration` — already in seed; the FIT origin of the feature-channel decomposition this paper instantiates psychophysically.
- Daly (1993) *The Visible Differences Predictor* — *not yet in seed*; supplies the achromatic CSF and intra-channel masking model (their eq. 4); foundational for any quantitative HVS-grounded saliency model.
- Le Callet & Barba (2001/2003) — *not yet in seed*; supplies the chromatic intra-channel masking model (their eq. 5).
- Itti, Koch & Niebur (1998) PAMI — *not yet in seed*; the reference model this paper is benchmarked against (CC and KL values in Tables 3–5).
- Krauskopf, Williams & Heeley (1982) — *not yet in seed*; the opponent-color space used here.
- Kapadia, Westheimer & Gilbert (1995, 1999) — *not yet in seed*; the primate physiology of long-range horizontal connections that motivates the Butterfly facilitation.
- Parkhurst, Law & Niebur (2002) — *not yet in seed*; the eye-tracking benchmark and the central-bias analysis the paper builds on.
- Wooding (2002) — *not yet in seed*; the fixation-density-map / coverage methodology adopted here.
- Tsotsos et al. (1995) *Selective Tuning* — *not yet in seed*; the hierarchical-WTA variant in the same lineage.
