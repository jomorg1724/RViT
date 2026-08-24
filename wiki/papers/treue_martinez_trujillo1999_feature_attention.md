---
id: treue_martinez_trujillo1999_feature_attention
title: "Feature-based attention influences motion processing gain in macaque visual cortex"
authors:
  - "Treue, Stefan"
  - "Martínez Trujillo, Julio C."
year: 1999
venue: "Nature"
doi: "10.1038/21176"
arxiv: ""
url: "https://doi.org/10.1038/21176"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
concepts:
  - gain-modulation
  - top-down-feedback
related:
  - reynolds_heeger2009_normalization
  - cameron2002_covert_attention_contrast
  - desimone_duncan1995_biased_competition
  - reynolds1999_competitive_v2_v4
  - mcadams_maunsell1999_v4_tuning
relevance_to:
  - recurrent_vit
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Feature-based attention influences motion processing gain in macaque visual cortex

## 1. Abstract

Changes in neural responses based on *spatial attention* have been demonstrated in many areas of visual cortex, indicating that the neural correlate of attention is an enhanced response to stimuli at an attended location and reduced responses to stimuli elsewhere. Treue & Martínez Trujillo demonstrate **non-spatial, feature-based attentional modulation** of visual motion processing — and show that attention *increases the gain* of direction-selective neurons in visual cortical area **MT** *without narrowing the direction-tuning curves*. These findings place important constraints on the neural mechanisms of attention. The authors propose to unify the effects of spatial location, direction of motion, and other features of the attended stimuli in a **'feature similarity gain model'** of attention.

## 2. Why this matters for us

Treue & Martínez Trujillo 1999 is the founding paper of *feature-based attention* (FBA) — the framework that attention modulates visual processing not just spatially but also along feature dimensions (motion direction, color, orientation, etc.). The feature-similarity-gain model has become the standard model for FBA. For the user's program, this paper is the load-bearing citation for treating attention as something that operates *across the entire visual field* on feature-tuned representations, not just as a spotlight over locations. The recurrent ViT's attention map is spatial; extending it to feature-based attention is a future architectural direction warranted by this paper.

## 3. Key claims

1. **Attention has both spatial and feature-based components.** Spatial attention modulates responses based on stimulus location; feature-based attention modulates responses based on stimulus features (e.g., motion direction).
2. **FBA produces gain changes in feature-tuned cortical neurons.** In MT (a direction-selective area), attention to one motion direction increases the response of neurons tuned to that direction, *globally* across the visual field.
3. **The effect is *multiplicative gain*, not tuning sharpening.** Attention scales the direction-tuning curve up without narrowing it. The cell's preferred direction doesn't change; its response to all directions scales by a factor depending on attentional similarity.
4. **The feature-similarity-gain model.** The size of the attentional gain is proportional to the *similarity* between the cell's preferred feature and the attended feature. Cells tuned exactly to the attended feature get the largest gain; cells tuned to the opposite feature get the smallest (sometimes even suppression).
5. **The framework unifies spatial and feature attention.** Spatial attention can be reframed as "feature-similarity gain in space" — neurons tuned to attended locations get higher gain. Feature attention is "feature-similarity gain in feature space." The mechanism is the same.
6. **FBA operates *globally* across the visual field.** Unlike spatial attention (which is location-specific), FBA modulates responses everywhere — at attended and unattended locations alike. This is a strikingly non-local form of attention.
7. **Implications for visual processing.** FBA suggests the brain has a rich *attentional architecture* that operates on multiple stimulus dimensions, not just on a spotlight in space.

## 4. Methods

**Task.** Macaque monkeys performed a motion-direction-discrimination task. Two random-dot motion fields were displayed; the monkey reported subtle changes in one of them. Attention was directed to the *direction* of motion (feature-based) rather than just to a location.

**Recordings.** Single-unit recordings from neurons in area MT (direction-selective extrastriate cortex). The cell's preferred direction was first characterized.

**Manipulation.** The attended direction was varied: sometimes the attended stimulus moved in the cell's preferred direction; sometimes in the anti-preferred direction; sometimes in intermediate directions.

**Comparison.** The cell's response to a *non-attended* stimulus at *non-cell-RF* location was measured across conditions. If attention is purely spatial, attention to a stimulus at a different location shouldn't affect responses to non-attended stimuli at the cell's RF. But FBA predicts modulation based on directional similarity, regardless of location.

## 5. Results

The principal quantitative findings:

- **Cell responses are modulated by FBA even when the cell's RF stimulus is unattended.** Modulation magnitude depends on the *similarity* between the cell's preferred direction and the attended direction.
- **Maximum gain at matched direction.** When the attended direction matches the cell's preferred direction, the cell's response to its own RF stimulus increases by ≈10–20%.
- **Suppression at opposite direction.** When the attended direction is opposite to the cell's preferred direction, the cell's response *decreases*.
- **Tuning is preserved.** The cell's *tuning curve shape* (the relationship between stimulus direction and cell response) doesn't narrow; it just scales up or down. Multiplicative gain, not tuning sharpening.
- **Global effect.** The FBA modulation applies *everywhere* in the visual field, not just at the attended location.

## 6. Critique / limitations

The result is for *motion processing* in MT. Whether the same mechanism applies to other feature dimensions (color in V4; orientation in V1; faces / objects in IT) has been confirmed by subsequent work but not by this paper alone.

The framework is *single-unit-level*. Population-level dynamics of FBA — how the gain pattern propagates through cortical hierarchies, how it interacts with spatial attention at the level of receptive-field interactions — is partially addressed by subsequent work.

The multiplicative-gain framing assumes the attentional input *only* scales the existing tuning. More recent work has shown that *additional* effects on tuning sharpness, response onset, and oscillatory dynamics also occur. The 1999 paper isolates the gain effect.

The "feature-similarity" framework is *parametric*. The exact functional form of the similarity-gain relationship varies across studies; the 1999 paper establishes the qualitative pattern.

The framework doesn't directly engage with the *normalization* tradition (Reynolds & Heeger 2009). The two can be reconciled — feature-attention gain can be implemented via normalization-modulated gain — but the 1999 paper is silent on normalization.

## 7. Connection to our work

This paper supports the user's program at the level of *attention beyond spatial-selection*:

**Beyond spatial attention.** The recurrent ViT's attention map is *spatial* — it computes per-patch attention weights. Treue & Martínez Trujillo establish that real attention has a *feature-based* component that operates non-spatially. Future architectural extensions could add a *feature-based attention map* over the model's channel dimensions, complementing the spatial attention over patches.

**Feature-similarity-gain at the channel level.** The Feedback Transformer's multiplicative gain ([feedback_transformer](research_db/concepts/feedback_transformer.md)) currently scales Q/K projections by feedback projections. A natural extension is *channel-wise* gain that depends on the feedback's preferred features — exactly the FBA mechanism. PRISM v2's FiLM modulation already operates channel-wise; extending it to feature-similarity-gain would be a future direction.

**Unifying spatial and feature attention.** The Treue-Martínez Trujillo framework — both are gain modulation, just along different dimensions — supports treating attention in the user's program as a *general* multi-dimensional gain mechanism. This is the architectural commitment behind the user's central self-attention substrate operating on both spatial and feature dimensions.

**Global modulation.** FBA's *global* effect — modulating responses everywhere in the visual field — is a striking architectural feature. The Feedback Transformer's softmax attention is *local* (sums to 1 across positions). Adding a *feature-attention* pathway that applies global gain to specific feature channels would more faithfully model the FBA-spatial-attention dichotomy.

**Multi-hub system framing.** In the multi-hub system, different hubs may attend to different stimulus dimensions: MSI hub → spatial; some specialized hub → feature. The hubs' contributions to the central attention substrate would then be both spatial and featural.

The recurrent ViT paper does not directly engage with feature-based attention. Treue & Martínez Trujillo 1999 is a future-direction citation for extending the architecture beyond pure spatial attention.

## 8. Citations to follow

- `reynolds_heeger2009_normalization` — normalization model that subsumes FBA. In seed, full depth.
- `cameron2002_covert_attention_contrast` — contrast-gain in spatial attention. In seed, full depth.
- `desimone_duncan1995_biased_competition` — biased-competition framework. In seed, full depth.
- `reynolds1999_competitive_v2_v4` — companion competitive-modulation paper. In seed.
- `martinez_trujillo_treue2004_attention_tuning` — follow-up on tuning curves. Not in seed.
- `saenz_buracas_boynton2002_global_fba` — fMRI confirmation in humans. Not in seed.
- `maunsell_treue2006_feature_based_attention_review` — review of FBA. Not in seed.
- `mcadams_maunsell1999_v4_tuning` — V4 attention paper. In seed.
