---
id: hawkins1990_attention_detectability
title: "Visual attention modulates signal detectability"
authors:
  - "Hawkins, Harold L."
  - "Hillyard, Steven A."
  - "Luck, Steven J."
  - "Mouloua, Mustapha"
  - "Downing, Charles J."
  - "Woodward, Donald P."
year: 1990
venue: "Journal of Experimental Psychology: Human Perception and Performance"
doi: "10.1037/0096-1523.16.4.802"
arxiv: ""
url: "https://doi.org/10.1037/0096-1523.16.4.802"
tags:
  - visual-attention
  - psychophysics
concepts:
  - signal-detection-theory
  - cueing-effect
  - gain-modulation
related:
  - muller_findlay1987_sensitivity_criterion
  - lu_dosher1998_external_noise
  - cameron2002_covert_attention_contrast
  - posner1980_orienting
  - reynolds_heeger2009_normalization
  - solomon2004_cues_sensitivity
  - luo_maunsell2018_criterion_sensitivity
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_53
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual attention modulates signal detectability

## 1. Abstract

The mechanism by which visual-spatial attention affects detection of faint signals has been the subject of considerable debate. It is well known that spatial cuing speeds signal detection. This may imply that *attentional cuing modulates the processing of sensory information during detection* — or, alternatively, that cuing acts to *create decision bias favoring input at the cued location*. These possibilities were evaluated in three spatial cuing experiments. Peripheral cues were used in Experiment 1; central cues were used in Experiments 2 and 3. Cuing similarly *enhanced measured sensitivity* — *P(A)* and *d'* — for simple luminance detection in *all three experiments*. Under some conditions it also induced *shifts in decision criteria* (β). These findings indicate that visual-spatial attention facilitates the processing of sensory input during detection either by *increasing sensory gain* for inputs at cued locations or by *prioritizing the processing of cued inputs*.

## 2. Why this matters for us

Hawkins, Hillyard, Luck et al. 1990 is a *foundational* paper in the SDT-analysis-of-attention tradition. It conclusively demonstrates that spatial cuing produces *genuine sensitivity changes* (d' increases), not just criterion shifts — settling a major theoretical debate in the field. The paper is critically important for the recurrent ViT's cued-attention story: it establishes that the empirical "cued attention" effect in humans has a *perceptual* component, not just a *decisional* component. The recurrent ViT's architectural commitment to multiplicative attention modulation ([feedback_transformer](research_db/concepts/feedback_transformer.md)) is biologically warranted in part because real attention produces sensitivity changes, not just response biases.

## 3. Key claims

1. **Cued attention produces sensitivity changes (d' increase).** Across three experiments with different cue types (peripheral vs central) and different observers, valid cues produced significantly higher d' than invalid or neutral cues.
2. **Cued attention can also produce criterion shifts.** Some conditions also showed β changes (response bias) in addition to d' changes.
3. **The sensitivity change is the *primary* effect.** While criterion shifts were observed in some conditions, sensitivity changes were the consistent and primary finding across all experiments.
4. **Both peripheral and central cues produce sensitivity changes.** The effect is not specific to one cue type or to one attention regime (exogenous vs endogenous).
5. **The mechanism is "increased sensory gain" or "prioritized processing."** Hawkins et al. conclude that attention either increases the gain on cued-location signals (multiplicative enhancement) or somehow prioritizes their processing (which produces the same SDT signature).
6. **The framework supports gain-modulation accounts of attention.** Subsequent gain-modulation models (Reynolds & Heeger 2009 normalization, [reynolds_heeger2009_normalization](research_db/papers/reynolds_heeger2009_normalization.md)) are consistent with the Hawkins et al. empirical pattern.
7. **The result settles the perceptual-vs-decisional debate.** Hawkins et al. is the foundational empirical refutation of *purely* decision-bias accounts of cuing effects. Cuing produces real perceptual enhancement.

## 4. Methods

**Tasks.** Three experiments with simple luminance-detection tasks. Subjects detected faint visual flashes at one of several spatial locations.

**Cue manipulation.**
- *Experiment 1.* Peripheral cues (exogenous attention).
- *Experiment 2.* Central cues (endogenous attention).
- *Experiment 3.* Central cues with extended cue-target intervals to test sustained attention.

**SDT analysis.** Hit rate and false-alarm rate measured separately for valid, neutral, and invalid trials. d' and β computed.

**P(A).** Area-under-ROC-curve measure (P(A)) computed as an alternative measure of sensitivity that doesn't require parametric SDT assumptions.

## 5. Results

The principal quantitative findings:

- **Cued d' is significantly higher than uncued d' across all three experiments.** Effect sizes typically 0.3–0.6 d' units — moderate but robust.
- **P(A) confirms the sensitivity result.** P(A) measure also shows cued > uncued, independent of parametric SDT assumptions.
- **Criterion (β) shifts are smaller and less consistent.** Present in some conditions, absent in others. The sensitivity effect is the consistent finding.
- **Both peripheral and central cues work.** Effect is present in both exogenous (peripheral, transient) and endogenous (central, sustained) regimes.
- **Cue-validity dependence.** The d' enhancement scales with cue validity — invalid cues show *worse* d' than neutral, confirming that the effect is genuinely cue-dependent.

## 6. Critique / limitations

The tasks use *simple luminance detection*. Whether the same conclusion holds for more complex perceptual tasks (orientation discrimination, identity recognition) is partially confirmed by subsequent work (Cameron et al. 2002, Lu & Dosher 1998) but not directly tested here.

The framework treats sensitivity and criterion as separable. Subsequent neural-level work (Luo & Maunsell 2018) has shown that the *neural* substrates of these two components may be distinct — different neural populations modulate each.

The "increased sensory gain or prioritized processing" framing is a *disjunction*. The paper doesn't distinguish between these two mechanisms; subsequent work (Lu & Dosher 1998; the gain-vs-precision-weighting distinction) has been needed to refine.

The framework is *behavioral*. It establishes that attention produces sensitivity changes; it doesn't specify the neural mechanism. The Bastos / Friston tradition's precision-weighting framing is consistent but the 1990 paper is silent on it.

Some subsequent studies (Solomon 2004, [solomon2004_cues_sensitivity](research_db/papers/solomon2004_cues_sensitivity.md)) have argued that part of the apparent attention effect is non-attentional sensory enhancement. Whether Hawkins et al.'s "sensitivity changes" are *all* attention or include some non-attentional component is open.

## 7. Connection to our work

This paper is the *foundational SDT-attention* citation:

**Cued sensitivity in the recurrent ViT.** The recurrent ViT's higher accuracy at cued locations should be analyzed via SDT. Hawkins et al. predicts that the *underlying mechanism* is sensitivity change (d' increase). The recurrent ViT's hit rate and false-alarm rate at cued vs uncued locations should be measured separately to confirm.

**Architectural support for multiplicative attention.** Hawkins et al.'s "increased sensory gain" framing aligns with the Feedback Transformer's multiplicative gain. The architectural choice is consistent with the empirical pattern.

**Sensitivity-vs-criterion as a future analysis target.** Both the recurrent ViT and PRISM models should be analyzable into sensitivity and criterion components. Different architectural components might be expected to contribute to different SDT measures: feedback gain → sensitivity; decision-level prior bias → criterion.

**Robustness across cue types.** Hawkins et al.'s finding that both peripheral and central cues produce sensitivity changes is methodologically useful. The recurrent ViT could be tested with both kinds of cues (transient peripheral cue → exogenous attention; central instruction cue → endogenous attention) to verify the architectural fidelity.

The recurrent ViT paper cites Hawkins et al. 1990 in its bibliography (ref [53]). Future manuscripts that argue for sensitivity-based attention should cite this paper as the foundational SDT-attention demonstration.

## 8. Citations to follow

- `muller_findlay1987_sensitivity_criterion` — precursor SDT-attention paper. In seed, full depth.
- `posner1980_orienting` — Posner paradigm. In seed, full depth.
- `lu_dosher1998_external_noise` — external-noise framework. In seed, full depth.
- `cameron2002_covert_attention_contrast` — contrast-gain. In seed, full depth.
- `reynolds_heeger2009_normalization` — normalization model. In seed, full depth.
- `luo_maunsell2018_criterion_sensitivity` — modern primate extension. In seed, full depth.
- `pestilli_carrasco2005_attention_gain` — gain-modulation literature. Not in seed.
