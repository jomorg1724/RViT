---
id: bastos2015_laminar_macaque
title: "Visual areas exert feedforward and feedback influences through distinct frequency channels"
authors:
  - "Bastos, André Moraes"
  - "Vezoli, Julien"
  - "Bosman, Conrado Arturo"
  - "Schoffelen, Jan-Mathijs"
  - "Oostenveld, Robert"
  - "Dowdall, Jarrod Robert"
  - "De Weerd, Peter"
  - "Kennedy, Henry"
  - "Fries, Pascal"
year: 2014
venue: "Neuron"
doi: "10.1016/j.neuron.2014.12.018"
arxiv: ""
url: "https://doi.org/10.1016/j.neuron.2014.12.018"
tags:
  - primate-neurophysiology
  - cortical-anatomy
  - predictive-coding
concepts:
  - hierarchical-predictive-coding
  - cortical-microcircuit-model
  - top-down-feedback
related:
  - bastos2012_canonical_microcircuits
  - felleman_vanessen1991_hierarchical_cortex
  - keller_mrsic_flogel2018_pc_review
  - friston2010_fep_unified_theory
  - wang2025_hierarchical_reasoning_model
relevance_to:
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-16"
---

# Visual areas exert feedforward and feedback influences through distinct frequency channels

> **Identity note.** The paper was published online in late 2014 in *Neuron*; volume 85(2) appeared in early 2015 and many citations record it as a 2015 paper. The stub id `bastos2015_laminar_macaque` is preserved per the no-rename rule; the frontmatter `year` is set to 2014 to match the actual publication date.

## 1. Abstract

Visual cortical areas subserve cognitive functions by interacting in both feedforward and feedback directions. While feedforward influences convey sensory signals, feedback influences modulate feedforward signaling according to the current behavioral context. The authors investigate whether these interareal influences are subserved differentially by *rhythmic synchronization*. They correlate frequency-specific directed influences among 28 pairs of visual areas in macaque with anatomical metrics of the feedforward or feedback character of the respective interareal projections. The result: feedforward influences are carried by **theta-band (~4 Hz) and gamma-band (~60–80 Hz)** synchronization, and feedback influences by **beta-band (~14–18 Hz)** synchronization. The functional directed influences constrain a functional hierarchy similar to the anatomical hierarchy, but exhibiting task-dependent dynamic changes — particularly with regard to the hierarchical positions of frontal areas. Feedforward and feedback signaling use distinct frequency channels, suggesting that they subserve differential communication requirements.

## 2. Why this matters for us

Bastos 2015 (Neuron) is the empirical test of the Bastos 2012 canonical-microcircuit prediction ([bastos2012_canonical_microcircuits](research_db/papers/bastos2012_canonical_microcircuits.md)). The 2012 paper predicted a feedforward-vs-feedback frequency asymmetry; the 2015 paper measures it directly in macaque with simultaneous laminar recordings across 28 area pairs. The result is the strongest single piece of empirical evidence for the predictive-coding canonical-microcircuit framework, and is the load-bearing primate-data citation for [hierarchical_predictive_coding](research_db/concepts/hierarchical_predictive_coding.md) as a real cortical computation rather than a theoretical proposal. The user's commitment to slow-fast recurrence ([slow_fast_recurrence](research_db/concepts/slow_fast_recurrence.md)) and feedback substrates ([threads/feedback_substrates.md](research_db/threads/feedback_substrates.md)) gains primate-data support from this paper.

## 3. Key claims

1. Feedforward and feedback information flow between cortical areas in macaque are *frequency-segregated*: feedforward by theta + gamma, feedback by beta.
2. The frequency separation is robust across 28 pairs of visual areas, including V1, V2, V4, TEO, DP, MT, MST, and parts of frontal cortex. It is not a peculiarity of one area pair.
3. The frequency segregation correlates with *anatomical* hierarchy: pairs with stronger anatomical feedforward markers show stronger theta/gamma directed influence; pairs with stronger feedback markers show stronger beta directed influence.
4. **Functional hierarchy from frequencies.** Computing each area's average position based on its frequency-specific directed influences produces a hierarchy that closely matches the Felleman & Van Essen 1991 anatomical hierarchy. This is the first empirical recovery of the cortical hierarchy *from physiology alone*.
5. **Task-dependent dynamics.** Frontal areas shift their hierarchical position depending on task demands, indicating that the hierarchy is not rigid but is dynamically modulated by behavioral context.
6. The 4 Hz theta component of feedforward signaling is *new* compared to the Bastos 2012 prediction (which emphasized gamma only). Theta-gamma coupling for feedforward signaling is a novel empirical observation requiring extension of the theoretical framework.

## 4. Methods

Simultaneous laminar recordings in macaque visual cortex using electrocorticography (ECoG) over a large cortical surface, capturing local field potentials from 28 pairs of cortical areas during visual tasks. Time-resolved spectral analysis decomposed signals into theta (3–7 Hz), alpha (8–12 Hz), beta (14–18 Hz), and gamma (60–80 Hz) bands.

For each area pair and each frequency band, the authors computed *Granger causality* in both directions to characterize directed influences. The frequency-specific directed influence (FF or FB) was then correlated with an anatomical metric of the projection's feedforward or feedback character: the fraction of supragranular layers of origin (SLN, from Markov, Kennedy et al. quantitative tracing studies in macaque).

The resulting frequency-vs-SLN correlations identify which frequencies carry feedforward (positive correlation with SLN) and feedback (negative correlation with SLN) information.

To extract a functional hierarchy, the authors computed for each area its average frequency-weighted position (the difference between feedforward and feedback influences across its connections). Areas with strong feedforward output and weak feedback input rank high; areas with strong feedback output and weak feedforward input rank low.

## 5. Results

The principal quantitative findings:

- **Frequency segregation.** Feedforward Granger causality is concentrated in theta and gamma. Feedback Granger causality is concentrated in beta. The frequency-vs-SLN correlation is strong (r > 0.7 in the cited frequency bands) and significant.
- **Functional hierarchy.** The frequency-based functional hierarchy matches the Felleman & Van Essen anatomical hierarchy with high agreement (the rank-order correlation is reported as significant).
- **Task-dependent shifts.** Frontal areas (specifically frontal eye fields and prefrontal areas) shift hierarchical positions depending on task demands, with the magnitude of the shift correlating with task-relevant attention.
- **Robustness across area pairs.** The frequency segregation holds across the majority of the 28 tested pairs, not just for a few canonical pairs.

The empirical finding refines the Bastos 2012 prediction: feedforward signaling has two components (theta + gamma) rather than just gamma; feedback is beta (not alpha-beta as broadly assumed).

## 6. Critique / limitations

The recordings are from macaque visual cortex during specific visual tasks. Generalization to other cortical systems (somatosensory, motor, association) is plausible but not directly tested. The frequency segregation is plausibly a general cortical principle, but the specific frequency bands may differ across systems.

The Granger causality analysis assumes the signal is stationary over the analysis window. Real cortical activity is highly non-stationary, with rapid changes during behavior. The analysis windows are short (~100s of ms) but the assumption of within-window stationarity is an approximation.

The functional hierarchy is computed *across* areas using *averaged* frequency influences. It is not a per-trial readout — within a single trial, the hierarchy may be more or less rigid than the average suggests. Dynamic hierarchies on shorter timescales are an active research area.

The relationship between the theta component of feedforward signaling and *attentional sampling* (which is rhythmic in the theta band; Fiebelkorn & Kastner 2019) is not addressed in the 2015 paper but has become an active research topic. The theta-band feedforward signaling may be the substrate of rhythmic attentional sampling.

The work does not engage with the *content* of the signaling — what information is being passed in each frequency band. The Bastos 2012 microcircuit framework predicts errors in feedforward and predictions in feedback; the 2015 paper provides frequency-channel evidence but does not directly test the content interpretation. Direct empirical tests (recording from putative error vs prediction neurons) are still ongoing.

The work is from a single macaque population (with multiple animals) but the recording technique (ECoG) has spatial limitations compared to laminar electrode arrays. Subsequent work with depth-electrode arrays has refined the picture of which laminar layers contribute to which frequency band.

## 7. Connection to our work

This paper is the strongest empirical support for the predictive-coding canonical-microcircuit framework in primate, and is the load-bearing citation for several of the user's architectural commitments:

**Frequency-as-timescale separation in PRISM v2.** PRISM v2's fast and slow memory states ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) operate at different effective timescales (fast: per-step gate probability ≈0.27; slow: ≈0.05). Bastos 2015's feedforward-gamma / feedback-beta separation supplies the primate-physiology warrant: the fast memory's effective update rate is in the gamma-band-analog range; the slow memory's is in the beta-band-analog range. The frequency separation is the biological precedent for the user's architectural choice.

**Theta-gamma feedforward as inspiration for HRM's hierarchical convergence.** HRM ([wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md)) uses two nested computational rates (L module rapidly converging; H module updating once per L convergence). The Bastos 2015 theta-gamma feedforward finding is a biological precedent for nested feedforward timescales: gamma carries moment-to-moment evidence; theta carries the slower envelope. The user's program could explicitly model both fast (gamma) and slow (theta) feedforward channels.

**Beta-band feedback as the slow-FiLM modulation.** PRISM v2's slow-FiLM pathway ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.4) provides top-down modulation from slow memory to V1 features. Bastos 2015 identifies beta-band synchronization as the feedback channel; PRISM v2's slow modulation is the architectural analog. Future variants could explore whether explicitly imposing a beta-band-analog timescale on the feedback projection improves model behavior.

**Task-dependent hierarchy shifts as the multi-hub design's empirical signature.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) predicts that the central self-attention substrate is dominated by different hubs depending on task context. Bastos 2015's finding that frontal areas shift hierarchical position with task demands is the empirical counterpart: cortex doesn't have a rigid hierarchy; it's task-modulated. The multi-hub architecture's competition for the central substrate is the user's program's mechanism for this flexibility.

**Functional hierarchy recovery.** The paper's recovery of the cortical hierarchy from frequency-band physiology alone is a remarkable empirical result — the cortex's anatomy is *also* its physiology. For the user's program, this is a methodological precedent: trained multi-hub systems' learned communication structures should also recover the imposed architectural hierarchy.

## 8. Citations to follow

- `bastos2012_canonical_microcircuits` — the theoretical prediction this paper tests. In seed, full depth.
- `felleman_vanessen1991_hierarchical_cortex` — the anatomical hierarchy. In seed.
- `markov_kennedy2014_consensus_macaque` — the quantitative anatomical tracing data. Not in seed; should be added.
- `buffalo2011_laminar_alpha_gamma` — earlier empirical evidence of laminar frequency separation. Not in seed.
- `michalareas2016_alpha_gamma_human_meg` — human-MEG replication. Not in seed.
- `fiebelkorn_kastner2019_rhythmic_attention` — theta-band rhythmic attentional sampling. Not in seed.
- `vezoli2021_brain_state_hierarchy` — task-dependent hierarchy dynamics. Not in seed.
- `keller_mrsic_flogel2018_pc_review` — modern empirical review of PC. In seed, full depth.
