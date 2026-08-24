---
id: haber2015_cbgtc_circuits
title: "Corticostriatal circuitry"
authors:
  - "Haber, Suzanne N."
year: 2016
venue: "Dialogues in Clinical Neuroscience"
doi: "10.31887/DCNS.2016.18.1/shaber"
arxiv: ""
url: "https://doi.org/10.31887/DCNS.2016.18.1/shaber"
tags:
  - cortical-anatomy
  - subcortical
  - review
concepts:
  - cortico-basal-ganglia-thalamic-loops
  - reward-modulated-attention
  - priority-map
related:
  - hikosaka2006_bg_reward_eyes
  - mcnab_klingberg2008_pfc_bg_wm
  - herman_arcizet2020_caudate_sc
  - botvinick2020_deep_rl_neuro
  - glimcher2011_dopamine_rpe
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Corticostriatal circuitry

> **Identity note.** The user's notes cite "Haber (2015) — Cortico-basal ganglia-thalamic circuits in goal-directed behavior." Haber's canonical review on corticostriatal circuitry in *Dialogues in Clinical Neuroscience* (vol. 18, issue 1) appeared in early 2016 and is the closest published match; the volume's nominal year is sometimes cited as 2015. The id `haber2015_cbgtc_circuits` is preserved per the no-rename rule; the frontmatter `year` is set to 2016 to match the actual publication date.

## 1. Abstract

Corticostriatal connections play a central role in developing appropriate goal-directed behaviors, including the motivation and cognition to develop appropriate actions to obtain a specific outcome. The cortex projects to the striatum topographically — different regions of the striatum have been associated with different functions: the ventral striatum with reward; the caudate nucleus with cognition; and the putamen with motor control. However, corticostriatal connections are more complex, and interactions between functional territories are extensive. These interactions occur in specific "convergence zones" where terminal fields from different functional cortical regions overlap. The review provides an overview of the connections from cortex to striatum and their role in integrating information across reward, cognitive, and motor functions, with emphasis on the interface between functional domains within the striatum.

## 2. Why this matters for us

The user's multi-hub multi-objective system ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5 — competition-emergent predictive coding) posits an RL hub that interfaces with MSI and VAE hubs through a shared self-attention substrate. Haber's review is the biological substrate for the RL hub. The cortico-basal ganglia-thalamic (CBGTC) loop is the brain's canonical RL machinery: it integrates reward signals from dopamine with cortical state representations from multiple functional territories, and produces action-selection / attention-prioritization signals that close back onto cortex via thalamic projections. The "convergence zones" Haber emphasizes — sites where reward, cognition, and motor information overlap — are the anatomical analog of the user's competitive arena for self-attention control.

## 3. Key claims

1. Corticostriatal projections are topographic: distinct cortical regions project to distinct striatal subdivisions (ventral striatum ← orbital/medial PFC, reward; caudate ← dorsolateral PFC, cognition; putamen ← motor/premotor cortex, motor).
2. Despite topographic organization, the boundaries between functional territories are not sharp. Terminal fields from different functional cortical regions overlap in specific *convergence zones* within the striatum.
3. These convergence zones provide the anatomical substrate for cross-domain integration — reward signals can influence cognitive processing, cognitive signals can influence motor planning, and so on, all via striatal interactions.
4. The CBGTC loop is closed: striatal output via the globus pallidus and substantia nigra returns to cortex through the thalamus (mediodorsal nucleus, VA/VL nuclei), preserving the topography of the corticostriatal input.
5. Dopaminergic projections from the substantia nigra (SNc) and ventral tegmental area (VTA) provide reward-prediction-error signals that modulate corticostriatal plasticity, biasing the loop toward outcomes that have been rewarded in the past.

## 4. Methods

A narrative anatomical review. The paper synthesizes decades of tract-tracing work in macaque (and complementary rodent data) to map the cortico-striatal-pallidal-thalamic-cortical loop. The "convergence zone" analysis in particular draws on Haber's own anatomical tracing work in macaque, identifying specific striatal locations where terminal fields from multiple cortical regions overlap. No new experimental data are presented; the contribution is a synthesis and a conceptual framing.

## 5. Results

The principal anatomical findings the review consolidates:

- **Ventral striatum** receives convergent input from orbital PFC (vmPFC, OFC), ventral ACC, hippocampus, and amygdala. This is the reward-evaluation hub.
- **Caudate nucleus (head and body)** receives convergent input from dorsolateral PFC (dlPFC, areas 9, 46) and dorsal ACC. This is the cognitive-control hub.
- **Putamen** receives convergent input from primary motor cortex (M1), premotor cortex, and supplementary motor area (SMA). This is the motor-control hub.
- **Convergence zones** at the boundaries between these territories — particularly in the medial caudate, where dlPFC and ACC inputs overlap — provide sites where reward signals can shape cognitive processing.
- **Output pathways.** The direct pathway (striatum → GPi/SNr → thalamus → cortex) facilitates selected actions; the indirect pathway (striatum → GPe → STN → GPi/SNr → thalamus → cortex) suppresses competing actions.
- **Dopamine.** SNc and VTA dopamine neurons innervate the striatum with regional specificity: VTA → ventral striatum (reward), SNc → dorsal striatum (cognition/motor). Dopamine is the teaching signal for corticostriatal plasticity.

## 6. Critique / limitations

The review is anatomical and conceptual; it does not propose a computational model of how the CBGTC loop implements RL. The link to RL theory (Schultz, Dayan, Sutton & Barto) is referenced but not formalized in this paper.

The convergence-zone idea is qualitative. The exact spatial extent of convergence zones, their cell-type composition, and the synaptic-level integration rules at convergence sites are not quantified. Subsequent work (Choi, Tanimura, Vage, Yates & Haber 2016; Choi, Ding & Haber 2017) refines this by identifying specific cell-level convergence sites with retrograde tracing.

The macaque-centric anatomy may not generalize cleanly to rodents (different relative sizes of striatal subdivisions, different cortical projection topography). Heilbronner et al. (2016, from the Haber lab) directly addresses rodent–primate homology of the corticostriatal system; that paper should be cited alongside this one when extrapolating between species.

The review does not engage with attention-relevant subcortical structures beyond the CBGTC loop proper (e.g., superior colliculus, pulvinar). Visual-attention applications of this anatomy require integrating with Krauzlis-style SC literature and Saalmann-style pulvinar literature.

## 7. Connection to our work

The CBGTC loop is the biological substrate of the RL hub in the user's multi-hub system ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5). The relevant correspondences:

- **The RL hub maintains its own memory state** ([threads/the_user_architectural_program.md](research_db/threads/the_user_architectural_program.md) §5). Anatomically, the RL hub's state is distributed across the ventral striatum (value), dorsal striatum (action), and OFC (outcome representation). The CBGTC loop is the closed circuit by which this state is updated.
- **The RL hub feeds back into a central self-attention substrate.** Anatomically, the CBGTC loop closes back onto cortex via thalamic projections to PFC, ACC, and motor cortex. The user's design places this feedback at the level of a shared self-attention module; biologically, the CBGTC output enters cortex via thalamic relays.
- **Convergence zones as the arena of competition.** The user's hypothesis that hubs *compete* for control of self-attention has its anatomical analog in Haber's convergence zones: striatal sites where reward, cognition, and motor signals overlap and where dopamine-modulated synaptic competition determines which signal wins.
- **Dopamine as the teaching signal for the competition.** Haber's coverage of dopaminergic projections from SNc/VTA to striatum is the biological substrate for the RL hub's gradient signal. The user's competition-emergent-PC theory predicts that this teaching signal should also implicitly train the *other* hubs to predict the RL hub's behavior — a testable extension Haber's anatomy does not address but is compatible with.

This paper sits at the intersection of two of the user's anchor concepts: `competition_emergent_predictive_coding` (the CBGTC loop is one of the competing coalitions) and `multi-hub-multi-objective-system` (the CBGTC loop is the RL hub's architectural substrate). It does not directly support the recurrent ViT paper, but it is essential for any future paper that extends the program to include reward-driven attention.

## 8. Citations to follow

- `haber_knutson2010_reward_circuit` — Haber's earlier review on the reward circuit specifically. Not in seed.
- `heilbronner2016_rat_primate_homology` — rat–primate corticostriatal homology (PMID 27450032, from the Haber lab). Should be added if the user's program targets rodent models.
- `choi2016_pfc_parietal_striatum_hub` — empirical convergence-zone identification (PMID 27646127, Haber lab). Companion paper.
- `hikosaka2006_bg_reward_eyes` — basal ganglia control of eye movements via SC. In seed.
- `schultz_dayan_montague1997_dopamine_rpe` — the formal RPE theory of dopamine. Not in seed.
- `glimcher2011_dopamine_rpe` — review of the RPE hypothesis. In seed.
- `botvinick2020_deep_rl_neuro` — deep RL and the brain. In seed.
