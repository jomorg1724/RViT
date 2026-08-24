---
id: sridharan2017_sc_sensitivity_bias
title: "Does the superior colliculus control perceptual sensitivity or choice bias during attention? Evidence from a multialternative decision framework"
authors:
  - "Sridharan, Devarajan"
  - "Steinmetz, Nicholas A."
  - "Moore, Tirin"
  - "Knudsen, Eric I."
year: 2017
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.4505-14.2017"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.4505-14.2017"
tags:
  - primate-neurophysiology
  - subcortical
  - lesion-microstimulation
  - visual-attention
  - theoretical-essay
concepts:
  - signal-detection-theory
  - microstimulation
  - top-down-feedback
related:
  - muller_findlay1987_sensitivity_criterion
  - hawkins1990_attention_detectability
  - luo_maunsell2018_criterion_sensitivity
  - cavanaugh_wurtz2004_sc_change_blindness
  - krauzlis2013_sc_attention
  - bisley_goldberg2010_parietal_priority
  - moore_armstrong2003_fef_microstim
  - bollimunta2018_fef_sc_covert
  - gupta_sridharan2024_presaccadic_change
  - muller2005_sc_microstim_covert
  - zenon_krauzlis2012_attention_deficits
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_71
status: full
depth: full
last_updated: "2026-05-16"
---

# Does the superior colliculus control perceptual sensitivity or choice bias during attention? Evidence from a multialternative decision framework

## 1. Abstract

Distinct networks in the *forebrain* and the *midbrain* coordinate to control spatial attention. The critical involvement of the superior colliculus (SC) — the central midbrain attention structure — has been shown by four seminal published studies in monkeys performing *multialternative* attention tasks. However, due to the lack of a mechanistic framework for interpreting behavioral data in such tasks, the *nature* of the SC's contribution to attention has remained unclear. Sridharan, Steinmetz, Moore & Knudsen present and validate a novel decision framework for analyzing behavioral data in multialternative attention tasks and apply this framework to re-examine the four seminal SC-attention studies. Their model is a *multidimensional extension to signal detection theory* that distinguishes two major classes of attentional mechanisms: those that alter the quality of sensory information ("sensitivity"), and those that alter the selective gating of sensory information ("choice bias"). Model-based simulations and re-analyses of the published data revealed a *converging pattern*: **choice-bias changes, rather than sensitivity changes, were the primary outcome of SC manipulation**. The SC contributes to attentional performance *predominantly by generating a spatial choice bias* for stimuli at a selected location — and this bias *operates downstream* of forebrain mechanisms that enhance sensitivity. The findings produce a *testable mechanistic framework* of how the midbrain and forebrain networks interact to control spatial attention.

## 2. Why this matters for us

Sridharan, Steinmetz, Moore & Knudsen 2017 is a *critical* paper for the user's program because it argues that the SC — long thought to be the *source* of attention in many accounts — actually contributes mostly to *choice bias* (criterion), not to *sensitivity*. This is the *opposite* of what many earlier accounts assumed. For the user's program, this paper provides:
- A formal *multialternative SDT framework* that the recurrent ViT could be analyzed with.
- A *partitioning* of attention sources: cortex (forebrain) → sensitivity; SC (midbrain) → bias. This partitioning predicts that *different architectural components* of the user's model implement different SDT effects.
- An important nuance for the FEF microstim analogy: FEF microstim may *also* produce primarily bias effects, not sensitivity effects.

## 3. Key claims

1. **Multialternative attention tasks require a multidimensional SDT framework.** Standard 2-alternative SDT analysis (d', β) doesn't directly apply to multi-stimulus tasks with multiple possible response locations. Sridharan et al. develop the generalization.
2. **Multialternative SDT separates sensitivity from bias.** The framework can dissect the cognitive components of behavior in multi-stimulus attention tasks.
3. **The SC produces choice bias, not sensitivity changes.** Re-analysis of four published SC-manipulation studies (microstimulation and inactivation) shows that the *behavioral effects* are consistent with bias changes, not sensitivity changes.
4. **SC operates downstream of forebrain sensitivity mechanisms.** The forebrain (cortex, particularly V4 / LIP / FEF) implements the sensitivity changes; the SC takes the sensitivity-modulated information and applies a *bias* on top of it.
5. **Implications for the FEF-SC attention loop.** FEF and SC are tightly connected. Sridharan et al.'s framework predicts that FEF microstimulation may also produce bias effects (downstream of sensitivity); detailed SDT analyses of FEF manipulations are needed.
6. **Testable mechanistic framework.** The framework predicts: forebrain inactivation should eliminate sensitivity changes; SC inactivation should eliminate bias changes. These predictions can be tested directly with concurrent inactivation experiments.

## 4. Methods

**Mathematical framework.** Sridharan et al. develop a generalization of standard SDT to *multialternative* tasks (more than 2 response options). The framework explicitly partitions:
- **Sensitivity (d') parameters:** the discriminability of each stimulus given its underlying signal strength.
- **Choice-bias (criterion) parameters:** the response-mapping rule given the signals, including any spatial bias.

The framework's parameters can be fit to *behavioral data* (hit rates, false-alarm rates, response distributions) from any multialternative attention task.

**Re-analysis of published data.** Four seminal SC-manipulation studies are re-analyzed:
- Two microstimulation studies (Müller, Philiastides & Newsome 2005; Cavanaugh & Wurtz 2004).
- Two inactivation studies (Zénon & Krauzlis 2012; another).

For each, the original behavioral data are fit with the multialternative SDT framework, and the SC-manipulation effects are partitioned into sensitivity and bias components.

**Convergent finding.** Across all four studies, the SC-manipulation effects loaded primarily on the bias component, not on the sensitivity component.

## 5. Results

The principal quantitative findings:

- **All four SC-manipulation studies show bias-dominant effects.** The behavioral consequences of SC microstimulation and inactivation are well explained by changes in choice bias, not in sensitivity.
- **The multialternative SDT framework provides a unified mechanistic interpretation.** Across studies with different methodologies, the same conclusion emerges: SC affects bias.
- **Forebrain manipulations (separately, in the literature) show sensitivity effects.** V4 and LIP manipulations primarily produce sensitivity changes (consistent with Cohen & Maunsell, Mitchell et al.).
- **The dissociation is meaningful.** Different brain regions are doing different SDT-distinct components of attention — not just "more attention" in different brains.
- **Predictive testability.** The framework predicts specific patterns for novel experiments combining SC and forebrain manipulations.

## 6. Critique / limitations

The framework is *re-analysis* of existing data. The published studies were not designed to dissociate sensitivity from bias; the multialternative SDT framework is applied post-hoc. Direct experiments designed for this dissociation would be more conclusive.

The "sensitivity in cortex, bias in SC" dichotomy is *clean but possibly oversimplified*. Real brain function involves substantial cross-talk between cortex and SC; the partition may be a useful first-pass description but not the full picture.

The multialternative SDT framework has many free parameters. Whether the data uniquely determine the parameters or whether the fits are underdetermined is partially addressed but not exhaustively.

The framework is applied to *visuospatial* attention. Feature-based attention and object-based attention may have different cortex-vs-midbrain partitions.

The paper's conclusion about FEF microstim is *predicted* but not directly tested. Subsequent analyses of FEF manipulations using the framework would test the prediction.

## 7. Connection to our work

This paper has important implications for the user's program's interpretive framework:

**Revising the SC-microstim analogy.** The recurrent ViT paper (2502.10955) argues that perturbations to the attention map produce behavioral effects *analogous to FEF microstimulation* (Moore & Armstrong 2003, [moore_armstrong2003_fef_microstim](research_db/papers/moore_armstrong2003_fef_microstim.md)) — and by extension SC microstimulation (Cavanaugh & Wurtz 2004). Sridharan et al. now suggest that those microstimulation effects are *primarily bias effects*, not sensitivity effects. The recurrent ViT's analogous perturbation effects may also be primarily bias-driven; this is a testable prediction.

**Architectural decomposition: which components produce sensitivity vs bias?** In the user's multi-hub system, different hubs and the central self-attention substrate likely produce different SDT components. Sridharan et al.'s framework suggests:
- Sensitivity-changes ← Feedback Transformer's V1-level gain (analog of cortex).
- Bias-changes ← decision-level mechanisms in the actor head + slow memory's context (analog of SC + LPFC bias).

**The central self-attention substrate spans both.** Sridharan-Steinmetz-Moore-Knudsen partition forebrain (cortex) and midbrain (SC) into sensitivity vs bias. The user's central self-attention substrate may serve *both* functions, since it integrates contributions from cortex-analog and SC-analog hubs.

**Testable predictions for the recurrent ViT.** If the recurrent ViT is analyzed with the multialternative SDT framework, the attention-map perturbations should partition into sensitivity vs bias components. The decomposition can validate the architectural homology with biological attention.

**The user's program's prediction.** The user's competition-emergent-PC thesis predicts that attention effects emerge from inter-hub competition. Different hubs may contribute different SDT components. This is a substantive empirical prediction that the multialternative SDT framework can test.

The recurrent ViT paper cites Sridharan et al. 2017 in its bibliography (ref [71]). Future manuscripts that interpret model perturbation effects should adopt the multialternative SDT framework to properly attribute the components.

## 8. Citations to follow

- `muller_findlay1987_sensitivity_criterion` — foundational SDT-attention paper. In seed, full depth.
- `hawkins1990_attention_detectability` — sensitivity foundation. In seed, full depth.
- `luo_maunsell2018_criterion_sensitivity` — LPFC's role in both components. In seed, full depth.
- `cavanaugh_wurtz2004_sc_change_blindness` — one of the re-analyzed SC studies. In seed, full depth.
- `krauzlis2013_sc_attention` — SC review. In seed, full depth.
- `muller2005_sc_microstim_covert` — Müller, Philiastides, Newsome SC microstim. In seed.
- `zenon_krauzlis2012_attention_deficits` — Zénon & Krauzlis SC inactivation. In seed.
- `bollimunta2018_fef_sc_covert` — FEF vs SC covert attention. In seed.
- `gupta_sridharan2024_presaccadic_change` — Sridharan lab's most recent presaccadic-attention paper. In seed, full depth.
