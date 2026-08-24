---
id: spratling2008_pc_biased_competition
title: "Predictive coding as a model of biased competition in visual attention"
authors:
  - "Spratling, M. W."
year: 2008
venue: "Vision Research"
doi: "10.1016/j.visres.2008.03.009"
arxiv: ""
url: "https://doi.org/10.1016/j.visres.2008.03.009"
tags:
  - predictive-coding
  - visual-attention
  - theoretical-essay
  - biased-competition
concepts:
  - biased-competition
  - rao-ballard-coding
  - attention-as-prediction-error
  - hierarchical-predictive-coding
  - divisive-normalization
related:
  - rao_ballard1999_predictive_coding
  - desimone_duncan1995_biased_competition
  - feldman_friston2010_attention_free_energy
  - reynolds_heeger2009_normalization
  - bastos2012_canonical_microcircuits
  - reynolds1999_competitive_v2_v4
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Predictive coding as a model of biased competition in visual attention

## 1. Abstract

Attention is widely held to enhance the response of cells encoding expected or predicted information through cortical feedback. The standard Rao-Ballard predictive coding theory proposes the opposite — that feedback acts to *suppress* information predicted by higher-level cortical regions. Spratling shows that despite this discrepancy, the predictive-coding model can be reformulated to simulate the empirical effects of attention. The key insight is a simple mathematical rearrangement of the predictive-coding equations that allows the model to be interpreted as a form of biased-competition (Desimone & Duncan 1995) model. Nonlinear extensions to the model further widen the range of attention phenomena it can explain. The paper resolves an apparent contradiction between the two frameworks and offers a unified account in which biased competition is the dynamic signature of predictive coding under attentional precision modulation.

## 2. Why this matters for us

Spratling 2008 is the canonical paper showing that the *biased-competition* and *predictive-coding* frameworks are reconcilable rather than mutually exclusive. This matters for the user's program because the architectural commitments of both frameworks are absorbed: predictive coding ([hierarchical_predictive_coding](research_db/concepts/hierarchical_predictive_coding.md)) provides the descending-prediction / ascending-error structure; biased competition provides the dynamic mechanism for selecting between competing representations; the user's coalition-competition extension ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) further scales the competition from receptive-field level to hub level. Spratling's reformulation is the bridge that makes the user's "competition-emergent PC" framing computationally coherent rather than rhetorical.

## 3. Key claims

1. The apparent conflict between predictive coding (feedback suppresses predicted activity) and attention data (feedback enhances attended activity) is *only* apparent. Both behaviors fall out of the same model with different parameter regimes.
2. The mathematical reformulation: predictive coding can be expressed as a divisive normalization in which the higher-level prediction divides (suppresses) the response *unless* the higher-level prediction is multiplied by an attention factor — in which case it *enhances* the response to predicted inputs. The architectural form is the same; only the sign and weight of the feedback projection change.
3. Under this reformulation, predictive-coding networks naturally implement biased competition. Two competing inputs compete for representation; the input that matches the higher-level prediction wins.
4. Nonlinear extensions (sigmoidal activation functions, multiplicative feedback) extend the model's empirical coverage to include attentional capture, distractor suppression, and the speed-accuracy trade-off.
5. Many of the empirical effects attributed to "biased competition" or "predictive coding" can be reproduced by a divisive-normalization-with-feedback architecture that does not require explicit prediction-error neurons. This means the empirical signatures of predictive coding are not unique evidence for the Rao-Ballard architecture; they are consistent with multiple implementations.
6. The reformulation suggests a unification: attention is the *gain* on top-down feedback in a predictive-coding network. Setting the gain produces either biased competition (high gain) or pure Rao-Ballard suppression (low gain) as limiting cases.

## 4. Methods

A theoretical / simulation paper. The author starts with the Rao-Ballard 1999 predictive-coding equations and derives an equivalent form using divisive normalization. The transformation:

In Rao-Ballard, the level-1 prediction error is $\epsilon = r - U r_h$ where $r$ is the bottom-up activity, $r_h$ is the higher-level state, and $U$ are the descending weights. The level-1 response of a unit is then the residual after the prediction has been subtracted.

Spratling reformulates this as a divisive normalization: each unit's output is its bottom-up input divided by (or modulated by) a context-dependent gain that depends on the higher-level prediction. Multiplicatively, with an attention parameter $\alpha$:

$$
r_{\text{out}} = \frac{r}{1 + \alpha \cdot U r_h}
$$

In this form, when $\alpha < 0$, increasing $r_h$ (a high-level prediction matching $r$) *enhances* the output — biased competition. When $\alpha > 0$, increasing $r_h$ suppresses the output — Rao-Ballard explaining-away. The two regimes correspond to different signs of the attention gain.

The author then runs neuronal-network simulations of standard attention tasks (Posner cuing, Reynolds attention modulation, biased-competition paradigms) and shows that the reformulated network reproduces the empirical effects.

## 5. Results

Quantitative simulation results:

- **Biased competition.** When two stimuli appear in the same receptive field and one is cued, the cued stimulus dominates the unit's response — matching Reynolds, Chelazzi & Desimone 1999 single-cell data.
- **Cue-validity dependence.** Cue validity (high vs low validity) modulates the cued/uncued response ratio, with the model's behavior matching the empirical psychophysical and neurophysiological data.
- **Spatial cuing effects.** Posner-paradigm RT and accuracy effects are reproduced.
- **Attentional gain modulation.** Reynolds' attention-modulation curves (gain change vs contrast) are reproduced; the model predicts a contrast-gain change rather than a response-gain change, consistent with the dominant empirical pattern.
- **Distractor suppression.** When distractors are added, the model's response to the target is enhanced and the response to distractors is suppressed — biased competition signature.
- **Speed-accuracy trade-off.** Varying the attention parameter $\alpha$ produces a smooth speed-accuracy trade-off, matching psychophysical data.

The architectural cost is low: the model has the same number of parameters as the original Rao-Ballard model plus one attention-gain parameter. The empirical coverage is broader than either pure biased competition or pure Rao-Ballard.

## 6. Critique / limitations

The reformulation is mathematically valid but conceptually awkward. The "attention parameter" $\alpha$ is a free knob that switches the model between Rao-Ballard suppression and biased-competition enhancement; the paper does not explain *why* attention should produce a sign change in the feedback gain. Subsequent work (Feldman & Friston 2010) gives a principled answer (precision weighting), but Spratling's paper itself treats $\alpha$ as a parameter rather than deriving its behavior.

The reformulation does not require explicit prediction-error neurons. This is presented as a strength (the model works without committing to specific cell types) but is actually a *challenge* for the Bastos 2012 microcircuit framework: the empirical signatures of predictive coding (mismatch responses, expectation suppression, laminar gamma/alpha asymmetry) are reproduced *without* the cell-type assignments that the Bastos framework relies on. The two papers therefore make different bets about the neural substrate.

The simulations use simplified stimuli (Gabor patches, dot fields). Generalization to naturalistic stimuli (objects, scenes, motion) is not demonstrated. Whether the divisive-normalization-with-feedback architecture scales to deep networks on object recognition is an open question; Wen et al. 2018 and Pinchetti et al. 2024 suggest deep PC networks underperform standard supervised networks, but those works use the standard Rao-Ballard formulation, not Spratling's reformulation.

The paper does not engage with the variational / Bayesian framing of free-energy (Friston 2010, Feldman & Friston 2010). The relationship between Spratling's divisive-normalization formulation and the variational Bayesian interpretation is unsettled; one might be the deterministic limit of the other, but the paper doesn't address this.

The dynamics of attention beyond the cue-target interval (rhythmic sampling, theta-band fluctuations, alpha-band gating) are not addressed. The model is a static-input attention model.

## 7. Connection to our work

This paper supports several of the user's architectural commitments at once:

**The Feedback Transformer's multiplicative structure as biased competition.** The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) integrates sensory and feedback Q/K via Hadamard product. Spratling's reformulation says that exactly this kind of multiplicative gain on feedback produces biased competition. The Feedback Transformer is therefore the architecturally clean implementation of Spratling's "multiplicative attention factor in a predictive-coding network."

**Reconciling PRISM v1's explanation-away decoder with attentional enhancement.** PRISM v1 ([Prism/docs/THESIS.md](Prism/docs/THESIS.md)) uses a Rao-Ballard-style generative decoder that subtracts predicted features from the input. Under pure Rao-Ballard, this *suppresses* attended (predicted) locations — the opposite of what attention should do. Spratling's reformulation resolves this: with the right gain on the feedback projection, the same architecture *enhances* attended locations. PRISM v1's saliency-gated update is the natural implementation: the prediction-error map gates *which* feedback gain regime applies at each location.

**Biased competition as the dynamic signature of competition-emergent PC.** The user's coalition-competition thesis ([coalition_resource_competition](research_db/concepts/coalition_resource_competition.md)) extends biased competition from receptive-field-level competition to coalition-level competition. Spratling's paper provides the mathematical proof that biased competition and predictive coding are the same framework at the receptive-field level — this is the precedent for scaling the same mathematics up to coalitions.

**Empirical adjudication needed.** The user's program is positioned in the predictive-coding tradition (with explicit prediction-error pathways in PRISM v1/v2). Spratling's paper is a reminder that the empirical signatures don't uniquely require this architecture. Future versions of PRISM should be benchmarked against Spratling-style divisive-normalization variants to determine whether the explicit prediction-error pathway is doing useful work or whether it's an architectural commitment with no empirical payoff.

The recurrent ViT paper (2502.10955) is closer to Spratling than to pure Rao-Ballard: it uses self-attention with feedback gain rather than explicit error neurons. Spratling's framework is therefore the natural theoretical home for the recurrent ViT's attention dynamics.

## 8. Citations to follow

- `desimone_duncan1995_biased_competition` — the biased-competition framework. In seed, full depth.
- `feldman_friston2010_attention_free_energy` — the variational reframing of the same idea. In seed, full depth.
- `rao_ballard1999_predictive_coding` — the predictive-coding foundation. In seed, full depth.
- `reynolds_heeger2009_normalization` — the normalization model of attention. In seed, full depth.
- `reynolds1999_competitive_v2_v4` — the empirical biased-competition data Spratling's model reproduces. In seed.
- `spratling2017_review_pc` — Spratling's later review of predictive-coding models. Not in seed.
- `bastos2012_canonical_microcircuits` — the canonical-microcircuit framework with explicit error neurons. In seed, full depth.
