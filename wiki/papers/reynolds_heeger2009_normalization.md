---
id: reynolds_heeger2009_normalization
title: "The normalization model of attention"
authors:
  - "Reynolds, John H."
  - "Heeger, David J."
year: 2009
venue: "Neuron"
doi: "10.1016/j.neuron.2009.01.002"
arxiv: ""
url: ""
tags:
  - visual-attention
  - normalization-model
  - primate-neurophysiology
  - theoretical-essay
concepts:
  - divisive-normalization
  - gain-modulation
  - feature-wise-linear-modulation
  - multiplicative-feedback
related:
  - desimone_duncan1995_biased_competition
  - carrasco2011_visual_attention_25y
  - perez2018_film
  - maunsell2015_attention_mechanisms
  - itti_koch2001_saliency_review
  - treue_martinez_trujillo1999_feature_attention
relevance_to:
  - prism_v1
  - prism_v2
  - recurrent_vit
seed_source:
  - thesis_md
status: full
depth: full
last_invariant: "spotlight is not winner-take-all"
last_updated: "2026-05-16"
---

# The normalization model of attention

## 1. Abstract

The normalization model of attention reformulates divisive normalization — a canonical cortical computation that scales each neuron's response by the pooled activity of its neighbors — as the substrate on which top-down attention operates. Attention is modeled as a per-neuron, per-location multiplicative gain that adjusts the parameters of the divisive normalization circuit. This single mechanism reproduces a wide range of attentional phenomena: contrast-gain changes (attention shifts the contrast-response function leftward), response-gain changes (attention multiplies firing rates by a constant factor), and the distinction between feature-based and spatial attention. The model unifies what had been viewed as separate "spotlight," "biased competition," and "feature-similarity gain" accounts into one parameterized cortical circuit.

## 2. Why this matters for us

Reynolds & Heeger is the theoretical justification for PRISM's FiLM-based modulation. PRISM's top-down pathway from working memory to perception (`THESIS.md` §2.4) is exactly the per-location, per-channel multiplicative gain $\gamma$ plus additive offset $\beta$ that the normalization model specifies. The argument that attention is *not* a softmax-over-locations winner-take-all gate but rather a graded gain field is the empirical foundation for PRISM's rejection of softmax-attention primitives (`THESIS.md` §1.2).

## 3. Key claims

1. Visual cortical neurons implement divisive normalization: a neuron's response is its excitatory drive divided by a normalization pool (the activity of nearby and similarly-tuned neurons), plus a constant.
2. Attention modulates divisive normalization by adjusting the gain of either the numerator (excitatory drive) or the denominator (normalization pool) on a per-neuron, per-location basis.
3. The same model parameter ranges produce qualitatively different attention signatures: contrast gain (a leftward shift of the contrast-response function) when the stimulus is in the receptive field; response gain (a multiplicative scaling of the response) when the stimulus dominates the receptive field.
4. The model unifies spatial attention (gain applied at the cued location) and feature-based attention (gain applied to neurons tuned to the attended feature) as different parameterizations of the same circuit.
5. Attention is *distributed and graded*, not winner-take-all. The gain field is continuous across space and feature dimensions; there is no discrete "selected" location.

## 4. Methods

The model is mathematical, not experimental. A neuron's response is given by:

$$
R = G_E \frac{E}{G_S S + \sigma}
$$

where $E$ is the excitatory drive (bottom-up tuning to the stimulus), $S$ is the normalization pool (suppressive influence from neighbors), $\sigma$ is a constant, and $G_E, G_S$ are per-neuron gain factors. Attention is implemented by modulating $G_E$ and/or $G_S$ on a per-location, per-feature basis. When $G_E$ is enhanced at the attended location, the neuron's response to the attended stimulus is boosted; when $G_S$ is suppressed (reducing the suppressive pool), responses are similarly boosted but with a different contrast-response signature.

The paper derives, in closed form, the conditions under which the model produces contrast gain versus response gain versus a mixture. Predictions are compared to single-unit data from V4 and MT (Reynolds & Chelazzi 2004; Treue & Martínez-Trujillo 1999) and to psychophysical contrast-response data (Carrasco & Yeshurun 1998).

## 5. Results

Quantitative predictions:

- When the stimulus is smaller than the receptive field, attention produces contrast gain (a horizontal shift of the contrast-response function by ~0.3 log units in V4 data).
- When the stimulus is larger than the receptive field, attention produces response gain (multiplicative scaling by a factor of ~1.5×).
- The transition between regimes depends on the ratio of stimulus size to receptive-field size, which the model predicts and matches data.
- Feature-based attention is reproduced by applying the gain to all neurons tuned to the attended feature, not just those at the attended location — predicting the global feature-attention effects measured by Treue & Martínez-Trujillo.

The model is therefore *not* an empirical paper in the strict sense; it is a theoretical framework that reproduces existing empirical observations. Its predictive power is tested in subsequent work.

## 6. Critique / limitations

The model has many free parameters (the spatial extent of the normalization pool, the tuning width, the form of the suppressive nonlinearity), and it is possible to fit a wide range of data by adjusting them. Whether the model has genuine predictive power versus being a flexible curve-fitting framework is debated.

The biological substrate of the "gain" — whether $G_E$ corresponds to a thalamocortical input, a top-down feedback signal, or a neuromodulatory state — is not specified by the model. This makes the model architecturally agnostic but also weakens its biological-plausibility claim.

The model is silent on the *source* of the attentional gain signal. Where does the top-down command originate? The model presupposes such a signal exists but provides no account of its generation. The PFC/FEF/SC priority-map literature (Bisley & Goldberg 2010; Krauzlis et al. 2013) provides this account but at the cost of additional architectural commitment.

The "attention is not winner-take-all" claim, while well-supported by the empirical data, has been argued not to settle the debate. Some attentional phenomena (covert search, change blindness) seem to require something closer to discrete selection. Modern syntheses (Carrasco 2011) accept the gain-field account as the default but allow that selection-like dynamics can emerge under specific conditions.

## 7. Connection to our work

PRISM v1's FiLM layer (`Prism/film.py`) is precisely the Reynolds-Heeger gain-modulation primitive instantiated convolutionally:

$$
P_t = \gamma_t \odot V_t + \beta_t
$$

where $\gamma_t$ (per-location, per-channel multiplicative gain) is the architectural analog of $G_E$ in Reynolds-Heeger, and the residual modulation $\beta_t$ adds flexibility beyond pure gain. The use of $1 \times 1$ kernels enforces a topographic, per-location modulation — exactly the spatial-locality structure Reynolds-Heeger requires.

The architectural commitment that follows from Reynolds-Heeger is that PRISM contains *no softmax-over-locations operation*. This is not a stylistic choice; it is a substantive theoretical claim that follows from accepting the graded-gain account of attention (`THESIS.md` §1.2). Architectures that include a learned softmax-over-locations are, in this view, committing to a discredited "spotlight" theory.

PRISM v2 extends the modulation to two cortical levels (`PRISM_V2_PROPOSAL.md` §3.4), with both a within-level FiLM (fast memory → V1 features) and a cross-level FiLM (slow memory → V1 features via upsampling). Reynolds & Heeger explicitly propose precisely this kind of multiplicative-gain composition at each level of the visual hierarchy, which justifies the v2 stacking.

The Recurrent ViT does include softmax attention (it is a Transformer-based architecture). The Reynolds-Heeger framework is not the basis for the ViT paper; the ViT contribution is orthogonal, showing that recurrent memory + softmax attention can recapitulate primate-like attention behavior. The two papers (Recurrent ViT and PRISM) therefore explore opposite sides of the same empirical target.

## 8. Citations to follow

- `desimone_duncan1995_biased_competition` — the prior dominant framework; Reynolds-Heeger argues their model subsumes biased competition.
- `carrasco2011_visual_attention_25y` — historical review documenting the shift from spotlight to gain-field accounts.
- `perez2018_film` — the FiLM paper; the ML primitive PRISM uses to implement the Reynolds-Heeger gain.
- `treue_martinez_trujillo1999_feature_attention` — the feature-based attention data Reynolds-Heeger reproduces; candidate for addition.
- `carrasco_yeshurun1998_contrast_attention` — contrast-response psychophysics; candidate for addition.
