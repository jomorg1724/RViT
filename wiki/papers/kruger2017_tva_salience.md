---
id: kruger2017_tva_salience
title: "Measuring and modeling salience with the theory of visual attention"
authors:
  - "Krüger, Alexander"
  - "Tünnermann, Jan"
  - "Scharlau, Ingrid"
year: 2017
venue: "Attention, Perception, & Psychophysics"
doi: "10.3758/s13414-017-1325-6"
arxiv: ""
url: "https://link.springer.com/article/10.3758/s13414-017-1325-6"
tags:
  - saliency-models
  - visual-attention
  - psychophysics
concepts:
  - attentional-template
  - priority-map
  - signal-detection-theory
  - psychometric-function
  - chronometric-function
  - biased-competition
related:
  - bundesen2005_neural_theory_attention
  - itti_koch2001_saliency_review
  - baluch_itti2011_topdown_mechanisms
  - wolfe2021_guided_search_6
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_28
status: full
depth: full
last_updated: "2026-05-16"
---

# Measuring and modeling salience with the theory of visual attention

## 1. Abstract

Krüger, Tünnermann & Scharlau (2017) extend Bundesen's Theory of Visual Attention (TVA; Bundesen 1990; Bundesen, Habekost & Kyllingsbæk 2005) into the domain of bottom-up salience. The classical saliency-map literature (Itti & Koch 2001; Koch & Ullman 1985) quantifies salience as a scalar feature-anomaly score read off a feature-pyramid combination, but offers no behavioral measurement that ties this score to a parameter inside a falsifiable model of selection. TVA, by contrast, provides exactly such a parameter — the attentional weight $w_x$ in the weight equation, and the per-stimulus encoding rate $v_x$ in the rate equation — but has historically been applied to top-down (pertinence-driven) selection of report-set members in whole- and partial-report paradigms with letters and digits. The contribution of this paper is to (i) operationalize salience as the *attentional-weight ratio* derived from TVA's rate equation, measured via a temporal-order judgment (TOJ) paradigm that does not require maskable, highly-learned stimuli; (ii) parametrically vary orientation contrast and luminance contrast and fit the resulting psychometric functions with TVA's rate equation to extract per-condition weights; (iii) use Bayesian model comparison to test competing mathematical forms (linear, power, logistic) for how feature contrast maps to attentional weight; and (iv) test whether salience contributions from two feature dimensions combine additively or multiplicatively. The headline findings are that salience grows as a *power function* of feature contrast across both orientation and luminance dimensions, that contributions from the two dimensions combine *additively* (not multiplicatively) in the weight equation, and that the overall TVA capacity parameter $C$ remains approximately constant across salience manipulations — i.e., salience reallocates capacity rather than creating it. The work provides the first quantitative bridge between the saliency-map literature and TVA's weighted-selection framework.

## 2. Why this matters for us

The Recurrent ViT's per-patch attention scores $\alpha_{ij} = \mathrm{softmax}(Q_i K_j^\top / \sqrt{d})$ are a learned analog of TVA's *relative* attentional weight $w_x / \sum_z w_z$ — the same construct Krüger et al. measure psychophysically. This paper does for the bottom-up side of the recurrent ViT exactly what `bundesen2005_neural_theory_attention` does for the top-down side: it gives us a quantitative psychophysical theory of how a *purely sensory* feature-anomaly signal feeds into an attentional weight. That means the per-patch attention scores in the recurrent ViT have a directly testable prediction attached to them: when the input contains a feature-contrast singleton (orientation, luminance, color), the attention score on the singleton patch should grow as a power function of the contrast, with the per-iterate weight ratio matching the human TOJ-derived ratio. This is the cleanest mapping between recurrent-ViT attention maps and a published psychophysical theory that we have. Krüger et al. also tell us that bottom-up contributions across feature dimensions combine *additively in the weight equation* — which is a hard constraint on how multi-feature attention should compose in our architecture, and which conflicts with the multiplicative-gain account that normalization-model and FiLM-style modulation might suggest.

## 3. Key claims

1. **Salience is operationally identical to TVA's attentional weight.** A salient object is one whose pre-categorical sensory evidence raises its attentional weight $w_x = \sum_j \eta(x, j)\, \pi_j$ relative to other objects in the display, even with $\pi_j$ held constant. Salience is therefore *not* a separate construct from TVA's existing machinery; it is what $w_x$ does when driven by $\eta$ rather than $\pi$.
2. **The TOJ paradigm gives clean TVA fits to arbitrary stimuli.** Replacing the standard whole-report letter paradigm with two-stimulus temporal-order judgments allows TVA's rate equation to be fit to *any* paired stimuli (gratings, luminance patches, real-world objects), greatly broadening the empirical reach of the framework.
3. **Salience grows as a power function of feature contrast.** Bayesian model comparison among linear, logarithmic, logistic, and power-function mappings $\omega(\Delta\text{feature}) = a \cdot \Delta^b$ from contrast to weight selects the power function for both orientation and luminance contrast.
4. **Multi-dimensional salience adds additively in the weight equation.** When orientation contrast and luminance contrast are independently varied, the joint salience weight is the *sum* of the per-dimension power-function contributions, not their product. This is a constraint on how feature pyramids combine.
5. **TVA capacity $C$ is invariant across salience.** The total processing-capacity parameter $C = \sum_x v_x$ is statistically indistinguishable across high- and low-salience conditions; salience *redistributes* the same capacity across stimuli, consistent with NTVA's filtering account.
6. **The bottom-up / top-down decomposition falls out of $\eta$ vs $\pi$.** Bottom-up salience corresponds to changes in $\eta(x, j)$ (sensory evidence strength); top-down task-set effects correspond to changes in $\pi_j$ (pertinence). The same weight equation hosts both, providing a unified framework for the bottom-up-vs-top-down debate.

## 4. Methods

The paradigm is two-alternative temporal-order judgment (TOJ). On each trial, two stimuli — a *probe* and a *reference* — appear with a stimulus-onset asynchrony (SOA) drawn from a fixed set spanning $\pm 100$ ms. Participants report which appeared first. The psychometric function $P(\text{probe first} \mid \text{SOA})$ is fit by TVA's rate-equation prediction: under the parallel-race model, the probability that the probe finishes encoding to visual short-term memory first is a function of the two stimuli's encoding rates $v_p, v_r$ and the SOA. Specifically,

$$P(\text{probe first} \mid \mathrm{SOA}) = \int_0^\infty f_{v_p}(t) \cdot [1 - F_{v_r}(t - \mathrm{SOA})]\, dt$$

where $f_{v}, F_{v}$ are the exponential density and CDF of encoding completion under rate $v$. The per-trial $v$ values are constrained by TVA's rate equation $v_x = \eta(x)\, w_x / W \cdot C$ with $W = \sum_z w_z$ and $C$ the total processing capacity.

Experiments parametrically vary the *feature contrast* of the probe relative to the background while holding the reference identical to background context. Experiment 1 varies orientation contrast (gratings differing from a horizontal background by $\Delta\theta \in \{5°, 15°, 30°, 60°, 90°\}$). Experiment 2 varies luminance contrast (Michelson contrast $\Delta L \in \{0.05, 0.1, 0.2, 0.4, 0.8\}$). Experiment 3 crosses both dimensions in a $5 \times 5$ design.

Per-subject parameters $\{w_p(\Delta), w_r, C\}$ are estimated via Markov-chain Monte Carlo (MCMC) with weakly informative priors. *Salience* is then operationalized as the contrast-dependent weight ratio $\omega(\Delta) = w_p(\Delta) / w_r$.

Bayesian model comparison compares candidate functional forms for $\omega(\Delta)$:

- Linear: $\omega(\Delta) = a \cdot \Delta + b$
- Logarithmic: $\omega(\Delta) = a \cdot \log(\Delta + 1) + b$
- Logistic: $\omega(\Delta) = L / (1 + e^{-k(\Delta - \Delta_0)})$
- Power: $\omega(\Delta) = a \cdot \Delta^b + c$

Model selection uses Bayes factors / WAIC. For the two-dimensional experiment, additive ($\omega_{\text{joint}} = \omega(\Delta\theta) + \omega(\Delta L)$) and multiplicative ($\omega_{\text{joint}} = \omega(\Delta\theta) \cdot \omega(\Delta L)$) composition rules are compared.

## 5. Results

- **Power-function fit.** For orientation, the power-function model dominates with posterior probability $> 0.99$ against linear and logistic alternatives; the fitted exponent is $b \approx 0.6$ (sub-linear), implying diminishing returns of orientation contrast on salience.
- **Same for luminance.** Power function dominates for luminance contrast as well, with exponent $b \approx 0.5$.
- **Additive combination.** The joint orientation × luminance experiment selects the *additive* combination rule with Bayes factor > 10 against the multiplicative rule. Joint salience weight $\omega_{\text{joint}} = a_\theta \Delta\theta^{b_\theta} + a_L \Delta L^{b_L} + c$ fits within posterior uncertainty of the per-dimension fits.
- **Invariant capacity $C$.** Across all contrast levels and dimensions, posterior estimates of the per-subject $C$ overlap (typical $C \approx 40$–60 items/s); the differences are smaller than between-subject variability. Salience reallocates the same total rate budget.
- **Per-subject scaling.** Individual subjects show stable per-condition weight ratios across experimental sessions, supporting the TVA-as-trait-measurement program.
- **Range.** At maximum orientation contrast ($\Delta\theta = 90°$), the probe-to-reference weight ratio reaches $\omega \approx 4$–6; at minimum salience ($\Delta\theta = 5°$), $\omega \approx 1.1$–1.3. Luminance contrast gives a similar range. Combined high contrast in both dimensions pushes $\omega \approx 8$–10.

## 6. Critique / limitations

The TOJ paradigm constrains the model to two-stimulus displays. Extending TVA-based salience measurement to multi-stimulus arrays (the natural domain of Itti-Koch saliency maps) requires either repeated pairwise comparisons (combinatorially expensive) or a model extension that scales to $n > 2$. Neither is addressed here; the paper measures salience pairwise.

The functional forms compared are a small set. A more flexible Gaussian-process prior over $\omega(\Delta)$ would test the power-function commitment more strongly. The exponent estimates ($b \approx 0.5$–0.6) are not derived from first principles; they are descriptive.

Additivity across orientation and luminance is shown for two dimensions only. The Itti-Koch architecture combines five or more channels (color, orientation, intensity, motion, flicker). Whether additivity scales across more dimensions, or whether interaction terms emerge, is left open. The user's interest in multi-modal sensory integration via the Feedback Transformer is sensitive to this question.

The measurement uses simple geometric stimuli on uniform backgrounds. Real-world salience involves figure-ground segmentation, object-based grouping, and scene context, none of which are tested here. The bridge to the saliency-map literature is therefore partial: Krüger et al. measure the *output* of the bottom-up channel against TVA's weight equation, but do not constrain the *front-end feature extraction*. Itti-Koch-style center-surround pyramids are compatible with the result; so are deeper feed-forward feature hierarchies (e.g., DNN feature maps).

The TVA framework assumes parallel-race independent encoding. Serial-attention accounts (Wolfe Guided Search; Treisman FIT) make different predictions for the same psychophysical data; Krüger et al. show that TVA fits the TOJ data well but do not run a competitive comparison with serial models.

The capacity-invariance result is consistent with NTVA's "redistribution of cells" account but does not test the cellular implementation. Alternative implementations (divisive normalization with attention as multiplicative gain) make the same prediction.

Finally, the paper does not address dynamics. All measurements are time-integrated over a single trial; the within-trial trajectory of $w_x$ (which would correspond to the recurrent ViT's iterate-by-iterate attention dynamics) is not measured.

## 7. Connection to our work

Krüger, Tünnermann & Scharlau (2017) is the *quantitative bridge* between the saliency-map family ([itti_koch2001_saliency_review](research_db/papers/itti_koch2001_saliency_review.md), [baluch_itti2011_topdown_mechanisms](research_db/papers/baluch_itti2011_topdown_mechanisms.md)) and the TVA / NTVA framework ([bundesen2005_neural_theory_attention](research_db/papers/bundesen2005_neural_theory_attention.md)). It is the *parent paper's* (NTVA's) extension to the bottom-up direction — what NTVA does for top-down pertinence, Krüger et al. do for bottom-up sensory anomaly — and it sits at the most directly testable intersection of psychophysics and the recurrent ViT's per-patch attention scores.

**Salience as $w_x$ is the formal analog of the recurrent ViT's per-patch attention score.** When the recurrent ViT looks at a singleton-containing image, its per-patch attention $\alpha_{ij}$ at iterate $t$ should track $w_x / W$ for the singleton patch — i.e., should grow as a power function of the feature contrast that defines the singleton. This is a precise, quantitative prediction we can test by running the recurrent ViT on synthetic singleton stimuli (oriented gratings, luminance patches) at parametric contrast levels and measuring the singleton-patch attention score against the Krüger power-function form. A power-function-like dependence with sub-linear exponent ($b \approx 0.5$–0.6) would be strong evidence that the recurrent ViT has learned an attentional weighting consistent with the TVA framework. A failure (e.g., a step-function or linear dependence) would indicate that the recurrent ViT's bottom-up channel does not match the psychophysical signature.

**The additive composition rule constrains multi-modal feedback in the Feedback Transformer.** The recurrent ViT's Feedback Transformer (`feedback-transformer`) combines bottom-up sensory Q/K projections with feedback Q/K projections from multiple memory states via Hadamard product (multiplicative). Krüger et al. find that across *feature dimensions* (orientation and luminance), the bottom-up contribution to the weight is additive, not multiplicative. This is a hard empirical constraint: at the bottom-up level, multiplicative combination of feature-channel evidence overestimates joint salience. The recurrent ViT's architecture is multiplicative in the Q/K combination — which means if our learned bottom-up Q/K projections are interpreted as carrying single-feature evidence, the empirical fit will be wrong. The resolution is most likely that the *learned Q/K projections* implicitly mix across feature dimensions before the Hadamard step, recovering an additive composition at the level of feature contributions even though the architectural primitive is multiplicative. This is a sharp testable claim about what the projection weights have learned to encode.

**Capacity invariance maps to the recurrent ViT's softmax-row-sum constraint.** TVA's $C = \sum_x v_x$ being invariant under salience manipulation is mathematically homologous to the recurrent ViT's softmax constraint $\sum_j \alpha_{ij} = 1$ for each row. Salience in TVA reallocates a fixed total rate across stimuli; softmax in the recurrent ViT reallocates a fixed total attention mass across patches. The two are the same conservation law applied to different substrates. The reason the recurrent ViT can be read as a TVA-like system at all is that softmax enforces exactly the kind of capacity-bounded competition Krüger et al. document.

**TOJ paradigm as a behavioral analog for the recurrent ViT.** Krüger et al.'s TOJ paradigm gives a clean two-stimulus discrimination task that maps onto a two-patch attention competition in the recurrent ViT. This is the simplest behavioral task we can run on the recurrent ViT that licenses direct quantitative comparison against published human data: present two-patch stimuli with parametric contrast on one patch, measure the patch-level attention ratio over recurrent iterates, and compare against $\omega(\Delta)$. The iterate dimension also lets us measure the *dynamics* that Krüger et al. miss — within-iterate evolution of $w_x$.

**Bottom-up / top-down decomposition via $\eta$ vs $\pi$.** Krüger et al. preserve TVA's decomposition: $\eta$ carries sensory evidence; $\pi$ carries task pertinence. In the Feedback Transformer, $\eta$ corresponds to the bottom-up sensory Q/K projections $s_q, s_k$ derived from the image, and $\pi$ corresponds to the memory-feedback Q/K projections $c^{(k)}_q, c^{(k)}_k$ derived from the recurrent state. The architecture therefore *natively* implements TVA's two-source weight construction. Running the recurrent ViT with vs without memory feedback isolates the $\eta$ contribution (pure salience) from the combined $\eta \pi$ contribution (salience + pertinence), giving us a clean ablation for the bottom-up / top-down decomposition.

**Relation to NTVA (the parent paper).** Krüger et al. is the direct extension of [bundesen2005_neural_theory_attention](research_db/papers/bundesen2005_neural_theory_attention.md) into the salience domain. Where NTVA's filtering mechanism is driven by *pertinence* $\pi$ (top-down), Krüger et al. show that the same filtering can be driven by *sensory evidence strength* $\eta$ (bottom-up). The two papers should be cited as a pair whenever we invoke TVA-style weighted competition in the recurrent ViT.

**Relation to saliency maps.** Itti & Koch (2001; [itti_koch2001_saliency_review](research_db/papers/itti_koch2001_saliency_review.md)) and Baluch & Itti (2011; [baluch_itti2011_topdown_mechanisms](research_db/papers/baluch_itti2011_topdown_mechanisms.md)) provide the front-end feature-pyramid machinery that produces a scalar saliency score per location. Krüger et al. provide the *back-end measurement* that ties that score to a behavioral selection parameter. The two literatures are complementary: Itti-Koch gives the feature extraction; Krüger et al. give the selection model the extracted features feed. The recurrent ViT's learned patch features play the Itti-Koch role; its attention scores play the Krüger-TVA role.

**Relation to Guided Search.** Wolfe's Guided Search 6.0 ([wolfe2021_guided_search_6](research_db/papers/wolfe2021_guided_search_6.md)) uses a priority map with serial selection. Krüger et al.'s framework is parallel-race; it does not commit to a serial bottleneck. The recurrent ViT, being parallel over patches with softmax normalization, is closer in spirit to Krüger-TVA than to Guided Search.

## 8. Citations to follow

- `bundesen1990_tva` — the original 1990 TVA paper. Foundational; cited heavily throughout Krüger et al. Not in seed.
- `tunnermann_petersen2015_tva_toj` — Tünnermann, Petersen & Scharlau's earlier paper extending TVA to TOJ paradigms (Frontiers in Psychology 2015). Methodological foundation. Not in seed.
- `tunnermann_scharlau2016_fast_conspicuous` — Tünnermann & Scharlau (2016) "Fast and Conspicuous?" the immediate predecessor that introduces TVA-based salience. PMC4862317. Not in seed.
- `nordfang_dyrholm_bundesen2013_top_down_bottom_up` — Nordfang, Dyrholm & Bundesen's TVA extension separating bottom-up sensory evidence from top-down pertinence in the weight equation. Not in seed.
- `koch_ullman1985_shifts_visual_attention` — the original saliency-map proposal. Not in seed; should be added as the genesis of the saliency-map family.
- `kyllingsbaek2006_tva_modeling` — methodological reference for fitting TVA parameters. Not in seed.
- `bundesen_habekost2008_principles_visual_attention` — the TVA/NTVA book; reference for parameter estimation. Not in seed.
- `treisman_gelade1980_fit` — Feature Integration Theory; the serial-search alternative Krüger et al. do not test against. Not in seed.
- `duncan_humphreys1989_search_similarity` — Similarity-theory predecessor to TVA's search predictions. Not in seed.
