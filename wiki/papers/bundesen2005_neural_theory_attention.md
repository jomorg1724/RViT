---
id: bundesen2005_neural_theory_attention
title: "A neural theory of visual attention: bridging cognition and neurophysiology"
authors:
  - "Bundesen, Claus"
  - "Habekost, Thomas"
  - "Kyllingsbæk, Søren"
year: 2005
venue: "Psychological Review"
doi: "10.1037/0033-295X.112.2.291"
arxiv: ""
url: "https://doi.org/10.1037/0033-295X.112.2.291"
tags:
  - visual-attention
  - psychophysics
  - theoretical-essay
  - primate-neurophysiology
concepts:
  - biased-competition
  - attentional-template
  - gain-modulation
  - signal-detection-theory
  - priority-map
  - divisive-normalization
  - top-down-feedback
related:
  - desimone_duncan1995_biased_competition
  - reynolds_heeger2009_normalization
  - wolfe2021_guided_search_6
  - kruger2017_tva_salience
  - itti_koch2001_saliency_review
  - bisley_goldberg2010_parietal_priority
  - sridharan2017_sc_sensitivity_bias
  - moran_desimone1985_selective_attention
  - reynolds1999_competitive_v2_v4
  - luo_maunsell2018_criterion_sensitivity
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# A neural theory of visual attention: bridging cognition and neurophysiology

## 1. Abstract

The Neural Theory of Visual Attention (NTVA) is a neural-level interpretation of Bundesen's (1990) Theory of Visual Attention (TVA). Its central claim is that *visual processing capacity is distributed across stimuli by dynamic remapping of the receptive fields of cortical cells*, such that more cortical cells (more processing resources) are devoted to behaviorally important objects than to less important ones. NTVA inherits TVA's two core equations — a *weight equation* that maps the perceived importance of a stimulus into an attentional weight, and a *rate equation* that maps weights and pertinence values into the per-stimulus rate at which categorizations are made — and gives them a cortical implementation in terms of two complementary mechanisms: *filtering*, which adjusts the number and gain of cells representing each stimulus, and *pigeonholing*, which adjusts the bias toward particular perceptual categories. NTVA quantitatively accounts for a wide range of attentional phenomena in human reaction times and error rates (whole-report, partial-report, single-stimulus and search paradigms) and simultaneously reproduces firing-rate signatures observed in primate V1, V2, V4 and IT under spatial and feature attention (response enhancement, contrast-gain shifts, receptive-field contraction around the attended object). The theory bridges the cognitive (psychophysical) and neurophysiological levels with one mathematical framework.

## 2. Why this matters for us

NTVA is the *closest existing published precedent* for the formal move the Recurrent ViT makes: it treats attention as a quantitative scaling of representational resources (cells / receptive-field area / firing rate) under a top-down weight that itself emerges from a competition. TVA's weight equation has the structure of a softmax-weighted sum of pertinence values, with the resulting weights driving stochastic race-to-threshold dynamics over categorizations — *exactly* the role the recurrent ViT's per-iterate attention map plays over its tokens. NTVA's rate equation, $v = \eta \beta w / W$, makes the iterate-count / processing-rate trade-off explicit and predicts that recurrent passes should narrow the receptive fields of attended units (the "filtering" mechanism) while preserving categorization bias (the "pigeonholing" mechanism). This is the formal basis for the recurrent ViT's iterate-narrow-narrow dynamics, and the cleanest psychophysical theory we can map the architecture's behavior against.

## 3. Key claims

1. **Two-equation core (inherited from TVA, 1990).** Attention obeys a weight equation $w_x = \sum_{j \in R} \eta(x, j)\, \pi_j$ (where $\eta(x, j)$ is the strength of the sensory evidence that object $x$ belongs to category $j$ and $\pi_j$ is the pertinence — current behavioral importance — of category $j$) and a rate equation $v(x, i) = \eta(x, i)\, \beta_i\, w_x / \sum_{z \in S} w_z$ (where $\beta_i$ is a perceptual-decision bias for category $i$). The first determines *who wins* the competition; the second determines *how fast* the winners get categorized.
2. **Filtering vs pigeonholing decomposition.** Attention has two distinct effects. *Filtering* operates by adjusting the attentional weights $w_x$ — i.e., by reallocating cells / receptive-field territory to objects with higher pertinence; this is the *sensitivity* component. *Pigeonholing* operates by adjusting the perceptual-decision biases $\beta_i$ — i.e., by tilting the categorization race toward task-relevant categories; this is the *criterion / bias* component.
3. **Receptive-field remapping is the cortical substrate of filtering.** The number of cortical cells effectively representing a stimulus, and the size of their receptive fields, is dynamically reallocated by attention: attended stimuli recruit more cells and have their cells' RFs shrink to better isolate the attended object from clutter. Unattended stimuli lose cells; their representations broaden and weaken. This is the cortical implementation of "redistribution of processing capacity."
4. **Two waves of selection.** Attention proceeds in two waves: a first wave in which attentional weights are computed and broadcast to cortex (priors derived from the weight equation), and a second wave in which RF remapping and gain changes occur in cortex (the implementation of filtering). The waves correspond to the priority-map computation and its cortical consequence.
5. **NTVA explains primate single-unit attention effects.** Response enhancement under spatial attention (Moran & Desimone 1985; Reynolds et al. 1999), contrast-gain shifts (Reynolds & Chelazzi 2004), and RF shrinkage around an attended stimulus all fall out of the dynamic RF-remapping account.
6. **NTVA explains human psychophysics.** Whole-report, partial-report, single-stimulus, and visual-search RT/error patterns are quantitatively predicted by the same equations, with the same parameter set fit per subject.
7. **The theory unifies "early" vs "late" selection.** Filtering changes who is represented (early-like); pigeonholing changes how representations are categorized (late-like). Both happen in parallel; the early/late dichotomy is dissolved.

## 4. Methods

NTVA is a theoretical / synthetic paper. The contribution is a *mathematical framework* and an interpretive mapping from that framework onto cortical mechanisms, not new experimental data.

The TVA equations are inherited verbatim from Bundesen (1990). Let $S$ be the set of stimuli in the display and $R$ the set of perceptual categories the subject is prepared to use. The *attentional weight* of stimulus $x \in S$ is

$$w_x = \sum_{j \in R} \eta(x, j)\, \pi_j$$

where $\eta(x, j) \geq 0$ is the strength of sensory evidence that $x$ is a member of category $j$, and $\pi_j \geq 0$ is the pertinence (top-down importance) of category $j$. The *processing rate* by which stimulus $x$ is categorized as belonging to $i$ is

$$v(x, i) = \eta(x, i)\, \beta_i\, \frac{w_x}{\sum_{z \in S} w_z}$$

where $\beta_i \in [0, 1]$ is a perceptual-decision bias. Categorizations are independent Poisson races; the first category to cross a recognition threshold wins. From these two equations the full set of TVA-derived predictions (whole-report curves, partial-report selectivity, search efficiency, attentional blink, etc.) follows.

NTVA's added move is the neural interpretation. *Filtering* is implemented by changing the number of cortical cells representing each object: high-$w$ stimuli recruit more cells with smaller, better-localized RFs; low-$w$ stimuli get fewer cells with larger, more cluttered RFs. *Pigeonholing* is implemented by gain-modulation on feature-selective cells, biasing categorical readout toward task-relevant features. The mapping is illustrated quantitatively against published primate single-unit data from V1, V2, V4 and IT.

## 5. Results

NTVA reproduces, with one parameter set per subject, the following psychophysical signatures:

- **Whole-report performance.** Number of items correctly reported as a function of exposure duration, with the empirical asymptote at ~4 items and the time constant ~70–100 ms, follows directly from the rate equation.
- **Partial-report selectivity.** When subjects are cued to report a subset (e.g., red letters among green), reporting accuracy for cued items is ~3× that for uncued items at short exposures, matching the prediction from raising $\pi_\text{red}$.
- **Single-stimulus reaction time.** Mean RT and RT distributions are predicted by the inverse of the rate equation under a one-stimulus display, with $\beta_i$ controlling correct/error trade-offs.
- **Visual search.** The shape of search functions (set-size effects, target/distractor similarity effects) emerges from the relative weights $w_\text{target} / w_\text{distractor}$ given by the weight equation.

NTVA reproduces, qualitatively and where data permit quantitatively, the following primate single-unit signatures under attention:

- **Response enhancement.** Attending to a stimulus inside the RF multiplies firing rate by a factor of ~1.2–1.5 in V4 and IT (Moran & Desimone 1985; Reynolds et al. 1999) — predicted as the consequence of recruiting more cells with sharper RFs centered on the attended object.
- **Contrast-gain shifts.** Attention shifts the contrast-response function leftward (Reynolds & Chelazzi 2004) — predicted as the consequence of pigeonholing-driven gain changes.
- **Receptive-field shrinkage / remapping.** With two stimuli in the RF, the cell's response approaches that of the attended stimulus alone (the canonical biased-competition result of Moran & Desimone 1985) — interpreted as the cell's effective RF having "shrunk" to exclude the unattended stimulus.
- **Pop-out / set-size effects.** Search-array neural signatures in V4 / IT track the weight-equation predictions for $w_\text{target} / w_\text{distractor}$.

The headline quantitative claim is that *one* mathematical framework, with a small number of free parameters, simultaneously fits cognitive data (whole-report, partial-report, RT) and neural data (firing rates, RF effects) for individual subjects / animals.

## 6. Critique / limitations

The model is *high-level*. The "redistribution of cells" mechanism is specified at the population level but not at the synaptic or circuit level — NTVA does not commit to whether RF remapping is driven by gain modulation (à la Reynolds & Heeger 2009 normalization) or by precision-weighting (à la Feldman & Friston 2010) or by predictive-coding-style competition (à la Spratling 2008). All three are compatible. The normalization model of attention, published four years later, can be viewed as a more circuit-level instantiation of NTVA's filtering mechanism.

The "pertinence" parameter $\pi_j$ is exogenous. The theory tells us what attention *does* given a setting of pertinences, but not how pertinences are computed or maintained — the working-memory / priority-map machinery (Bisley & Goldberg 2010; Awh & Vogel 2008) is left outside the framework. NTVA is therefore complementary to, rather than competitive with, priority-map and template-based accounts.

The TVA core is *parallel-race*: every stimulus is categorized independently and races to threshold. This excludes serial-search accounts (Treisman & Gelade FIT; Wolfe Guided Search). NTVA can fit the *shape* of search functions but does not commit to the serial/parallel debate at the mechanistic level. Wolfe's Guided Search 6.0 (2021) is the most direct alternative framework and uses a different vocabulary (priority map + serial selection through bottleneck) for overlapping data.

The mapping from "number of cells" to firing-rate predictions is somewhat post-hoc. NTVA does not derive a closed-form prediction for, e.g., the precise contrast-gain shift; it shows that the qualitative form follows from the equations. Subsequent normalization-model work (Reynolds & Heeger 2009) makes sharper closed-form predictions.

The two-wave structure of attention is not strongly constrained empirically. The first wave (weight computation) and second wave (RF remapping) are inferred rather than directly measured.

The theory was published in 2005; downstream work on temporal dynamics of attention (rhythmic attention, microsaccade-locked sampling), on subcortical contributions (Krauzlis et al. 2013; Sridharan et al. 2017), and on attention as precision-weighting in active-inference frameworks (Feldman & Friston 2010) all extend or refine NTVA's account.

## 7. Connection to our work

NTVA is the most precise existing precedent for the formal structure of the Recurrent ViT and for several specific design choices in PRISM v1 / v2.

**TVA's weight equation maps onto recurrent ViT attention scores.** The weight $w_x = \sum_j \eta(x, j)\, \pi_j$ has exactly the structure of a soft-attention readout: $\eta(x, j)$ is the inner product between a stimulus's feature representation and a category template, and $\pi_j$ is the top-down weighting applied to that template. The recurrent ViT's attention map at iterate $t$, $\alpha_t = \text{softmax}(Q_t K_t^\top / \sqrt{d})$, is the *normalized form* of NTVA's $w_x / \sum_z w_z$ — i.e., the relative-weight term that appears in the rate equation. The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) goes one step further: the top-down feedback Q/K projections that combine with sensory Q/K via Hadamard product are the architectural analog of $\pi_j$ — the pertinence weights that bias the competition. This means our attention scores are *literally* a learned approximation of NTVA's weight equation, with the per-iterate feedback playing the role of pertinence.

**TVA's rate equation maps onto the recurrent ViT's iterate count.** The rate equation $v(x, i) = \eta \beta w / W$ predicts that, for a fixed weight distribution, the number of categorizations completed scales linearly with elapsed time. In the recurrent ViT this corresponds to the number of recurrent iterates $n_{FR}$: each iterate is one "categorization step." NTVA therefore provides the formal justification for treating iterate count as the architectural analog of psychophysical exposure duration — and predicts the experimentally observed pattern that more iterates yield more accurate categorizations up to an asymptote determined by the weight distribution.

**Filtering vs pigeonholing maps onto sensitivity vs bias.** NTVA's *filtering* (adjusting $w_x$ by reallocating cells / RF territory) is the *sensitivity* component of attention in SDT terms; its *pigeonholing* (adjusting $\beta_i$ by gain-modulating feature-selective readouts) is the *bias / criterion* component. This is precisely the partition Sridharan et al. (2017) and Luo & Maunsell (2018) extract from multialternative SDT analyses of cortical vs subcortical attention sources — see [sridharan2017_sc_sensitivity_bias](research_db/papers/sridharan2017_sc_sensitivity_bias.md). The recurrent ViT's behavior under cued attention should partition along the same axis: cue-driven changes in iterate dynamics correspond to filtering (sensitivity); learned readout biases on the classifier head correspond to pigeonholing (criterion). This gives us a principled SDT-style analysis to run on the recurrent ViT's outputs.

**Dynamic RF remapping is the formal basis for iterate-narrow-narrow dynamics.** NTVA's central neural claim — that attended stimuli have their cortical RFs shrink and re-center on the attended object — is the *quantitative* prediction underlying the recurrent ViT's "iterate-narrow-narrow" attention-map dynamics qualitatively observed on Food-101 (`Private & Shared-2/Classifier`). What the user's notes describe as "attention maps focus, defocus, and reactivate over recurrent passes" is, in NTVA terms, the iterate-by-iterate adjustment of attentional weights followed by the corresponding RF-remapping (in our architecture: the attention scores narrowing toward semantically relevant tokens). NTVA predicts that this dynamic should be a *monotone narrowing* over iterates for a fixed pertinence vector, with re-broadening only when the pertinence vector itself updates. This is a directly testable claim on the recurrent ViT.

**Relation to normalization.** Reynolds & Heeger's normalization model of attention (2009; [reynolds_heeger2009_normalization](research_db/papers/reynolds_heeger2009_normalization.md)) is the circuit-level instantiation of NTVA's filtering mechanism — divisive normalization with attention as a per-neuron multiplicative gain is one specific way to implement "redistribution of cells / RF area." PRISM's FiLM modulation (`THESIS.md` §2.4) is therefore double-licensed: by normalization (the circuit form) and by NTVA (the psychophysical theory the normalization model implements). The two papers should be cited together whenever the user's program invokes attention as multiplicative gain.

**Relation to biased competition.** NTVA *contains* biased competition (Desimone & Duncan 1995; [desimone_duncan1995_biased_competition](research_db/papers/desimone_duncan1995_biased_competition.md)) as the cortical implementation of the weight equation. The Moran & Desimone 1985 result that a cell with two stimuli in its RF responds as though only the attended one is present is, in NTVA, the consequence of the cell's effective RF having shrunk to exclude the unattended object — i.e., that cell's contribution to $\eta(x, j)$ has been reallocated. The user's coalition-competition thesis is therefore the *next* level of generalization: NTVA scales biased competition from RF to population; the user's program scales it from population to coalition.

**Relation to Guided Search and saliency.** Wolfe's Guided Search 6.0 (2021; [wolfe2021_guided_search_6](research_db/papers/wolfe2021_guided_search_6.md)) is a *competitor* framework that uses a different vocabulary — priority maps with serial selection through a bottleneck — for an overlapping data set. The recurrent ViT is closer in spirit to NTVA than to Guided Search: it is parallel, all tokens are categorized simultaneously, and the "bottleneck" emerges from softmax normalization rather than serial gating. Krüger, Tünnermann & Scharlau (2017; [kruger2017_tva_salience](research_db/papers/kruger2017_tva_salience.md)) explicitly fits TVA to salience-search data, providing a bridge between NTVA and the saliency-model literature ([itti_koch2001_saliency_review](research_db/papers/itti_koch2001_saliency_review.md)).

**Relation to priority maps.** Bisley & Goldberg 2010 ([bisley_goldberg2010_parietal_priority](research_db/papers/bisley_goldberg2010_parietal_priority.md)) provides the parietal substrate for the pertinence vector $\pi_j$: LIP encodes a priority map that NTVA can treat as the source of pertinence values. The recurrent ViT's top-down feedback at iterate $t$ plays the same role.

## 8. Citations to follow

- `bundesen1990_tva` — the original TVA paper. Foundational. Not in seed.
- `bundesen_habekost2008_principles_visual_attention` — book-length treatment of TVA/NTVA with worked examples. Not in seed.
- `duncan_humphreys1989_search_similarity` — the similarity-theory predecessor to TVA's search-function predictions. Not in seed.
- `logan1996_ctva` — CODE Theory of Visual Attention; extension of TVA to spatial selection. Not in seed.
- `bundesen1990_tva_psychological_review` — superseded by the 2005 paper but provides cleaner equation derivations. Not in seed.
- `treisman_gelade1980_fit` — Feature Integration Theory; the principal serial-search alternative to TVA. Not in seed.
- `luo_maunsell2018_criterion_sensitivity` — modern SDT analysis of cortical attention; aligns with NTVA's filtering/pigeonholing partition. Likely in seed via Sridharan thread.
- `vangisbergen_etal1981_visual_search_RT` — empirical search-RT data NTVA targets. Not in seed.
- `chelazzi1993_neural_basis_VS` — IT-neuron data NTVA fits for the visual-search case. Not in seed.
