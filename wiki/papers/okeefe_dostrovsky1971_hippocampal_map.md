---
id: okeefe_dostrovsky1971_hippocampal_map
title: "The hippocampus as a spatial map. Preliminary evidence from unit activity in the freely-moving rat"
authors:
  - "O'Keefe, John"
  - "Dostrovsky, Jonathan"
year: 1971
venue: "Brain Research (Short Communication)"
doi: "10.1016/0006-8993(71)90358-1"
arxiv: ""
url: "https://doi.org/10.1016/0006-8993(71)90358-1"
tags:
  - hippocampus
  - place-cells
  - spatial-coding
  - cognitive-map
  - single-unit
  - foundational
concepts:
  - gridcell_rnn
  - multi_compartmental_memory
related:
  - hafting2005_grid_cells
  - whittington2020_tem
  - stachenfeld2017_predictive_map
  - behrens2018_cognitive_map
  - banino2018_vector_navigation
  - lisman_grace2005_hippocampal_vta
  - buzsaki2010_cell_assemblies
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# The hippocampus as a spatial map. Preliminary evidence from unit activity in the freely-moving rat

## 1. Abstract

The 1971 *Brain Research* paper was published as a Short Communication and **has no formal abstract** (the PubMed record confirms "No abstract available"). The opening of the paper describes recording from 76 hippocampal units in 23 freely-moving rats and reports that 8 units fired selectively as a function of the animal's position and orientation in the testing platform — the first empirical evidence for what would become known as *place cells*. The paper's central theoretical claim is that the hippocampus operates as a *spatial map* of the environment, rather than as a mnemonic or inhibitory structure as the prior literature had supposed.

## 2. Why this matters for us

O'Keefe & Dostrovsky 1971 is the *origin point* of the entire cognitive-map literature — the discovery that a piece of mammalian cortex maintains a *spatially-indexed* internal representation. For the user's program, this paper is the load-bearing biological warrant for the *spatial-grid* architectural commitment ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md)). The user's memory state $C^{(t)} \in \mathbb{R}^{n_{gh} \times n_{gw} \times n_C}$ — one state vector per spatial position — is the engineering instantiation of "one neuron per location": a *retinotopically-organized population* that holds content indexed by position. The user's architecture commits to this organization because biology does; O'Keefe & Dostrovsky is the founding empirical evidence for the biological commitment. The paper also matters as the conceptual root of the *spatial-vs-feature factorization* the user's program inherits via the medial-EC (spatial) / lateral-EC (feature) distinction ([concepts/multi_compartmental_memory.md](../concepts/multi_compartmental_memory.md)), which traces directly to the cognitive-map tradition O'Keefe initiated.

## 3. Key claims

1. Single units in the rat dorsal hippocampus (CA1) fire *selectively when the animal occupies particular locations* in its environment — "place units."
2. Place-related firing depends *jointly on position and head direction* in some units (the first hint of what would become "conjunctive" coding).
3. Hippocampal units *cannot be explained by simple sensory* (visual, auditory, olfactory) *or motor correlates alone* — the firing is allocentric, not egocentric.
4. The hippocampus may function as a *spatial reference map* of the environment rather than a purely mnemonic or inhibitory structure (the standing view at the time).
5. Place fields are *stable* across repeated entries to the same location within a session — diagnostic of a *learned* representation, not transient sensory activation.
6. Different units have *different preferred locations*, suggesting a *distributed* map: many cells with different place-tuning together tile the environment.
7. Place firing persists in the dark and across changes in proximal cues, arguing against a single-sensory-modality explanation and for an *integrative* representation.

## 4. Methods

Extracellular tungsten microelectrodes were chronically implanted in dorsal hippocampus (CA1) of 23 adult Long-Evans rats. Animals moved freely on an elevated platform and in test boxes while single-unit activity was recorded via a multi-channel cable to amplifiers and an audio monitor (a common 1970s setup). The authors classified units by manually correlating spike rate with the rat's position, head orientation, ongoing behavior, and discrete sensory stimuli. There were no automated tracking systems or quantitative place-field metrics at the time; classification was done by observation of spike-rate increases when the rat entered specific regions of the platform. The 8 "place units" met an informal criterion: firing rate increased substantially (often several-fold above baseline) when the rat entered a preferred portion of the environment, and decreased back to baseline elsewhere.

## 5. Results

The paper is brief (5 pages) and primarily descriptive; the headline results are:

- **76 units isolated across 23 rats.**
- **8/76 units (~10%) showed location-specific firing** meeting the authors' place criteria — the first empirical place cells.
- **Firing in place units increased sharply (often several-fold over baseline)** when the rat entered a preferred portion of the platform; firing decreased rapidly outside the preferred zone.
- **Some place units required a specific head orientation in addition to position** — the conjunctive position-direction code that later work expanded.
- **Many other units (majority)** fired in relation to discrete behaviors (e.g., grooming, drinking) rather than place — establishing that the hippocampus carries multiple categories of activity, not just spatial.
- **Place firing persisted in the dark and across changes in proximal cues**, arguing against a single-sensory explanation — diagnostic of an integrative / allocentric representation.
- **No correlation with theta-state EEG** was found in the 8 place units — an early observation that would be substantially revised by later work on theta phase coding (O'Keefe & Recce 1993).

## 6. Critique / limitations

The 1971 paper is a foundational empirical contribution but has numerous limitations by modern standards.

- **Very small sample (8 place units)** — preliminary descriptive report; the full statistical characterization of place cells came in Muller, Kubie & Ranck 1987 *J Neurosci*.
- **No quantitative metrics of place-field size, information content, or stability** — those concepts and metrics were developed by later work (Skaggs information measures, Muller-Kubie autocorrelation).
- **Single-electrode recording**; no population analysis or simultaneous multi-unit data. The ensemble-decoding evidence for the population-as-map (Wilson & McNaughton 1993) came two decades later.
- **Anatomical localization within CA1 imprecise by modern standards** (electrode tracks reconstructed post-hoc with limited spatial precision).
- **Environment was a simple elevated platform** — generality across environments (remapping; Bostock, Muller & Kubie 1991) not tested in the original paper.
- **Lacking lesion or causal evidence** linking place activity to navigation behavior; the causal evidence for hippocampal necessity for spatial learning came with Morris et al. 1982 *Nature* (water maze).
- **No control for path-integration vs allothetic cues** — the dissociation between idiothetic and allocentric inputs to place fields was developed later.
- **Theoretical "cognitive map" interpretation only fully developed later** in O'Keefe & Nadel 1978 *The Hippocampus as a Cognitive Map* (Oxford UP); the 1971 paper sketches the spatial-map interpretation but does not develop the cognitive-map framework.

## 7. Connection to our work

O'Keefe & Dostrovsky 1971 is the founding biological warrant for several of the user's most-load-bearing architectural commitments.

**Touchpoint 1: spatially-indexed memory state — the gridcell_rnn architectural commitment.** The paper's central empirical finding — that hippocampal cells fire selectively at specific spatial locations, forming a distributed map — is the founding biological warrant for the user's [gridcell_rnn](../concepts/gridcell_rnn.md) architectural commitment. The user's memory state $C^{(t)} \in \mathbb{R}^{n_{gh} \times n_{gw} \times n_C}$ — one state vector per spatial position — is the engineering instantiation of "one neuron per location" that O'Keefe-Dostrovsky discovered. The architecture commits to *spatial organization* of memory because biology does; the per-cell SIP and the per-grid FT integration ([gridcell_rnn.md](../concepts/gridcell_rnn.md) Refinements 1-3) are architectural choices that preserve and exploit this spatial organization. The biological warrant gives the design choice substantive grounding rather than being merely a convenience inherited from ConvGRU.

**Touchpoint 2: place fields as the architectural analog of attention-weight maps.** Place cells fire selectively for specific positions; the user's central self-attention map weights each spatial position. The architectural homology is: place-cell firing → attention weight at that position. When the user's central attention substrate places high weight on spatial position $(i, j)$, that position's grid-cell state is being *selectively activated* — directly analogous to a place cell's firing pattern. This is a structural homology, not merely metaphorical: the user's attention map *is* a learned, dynamic version of the place-cell population code.

**Touchpoint 3: conjunctive position-direction coding — the architectural prediction for the user's models.** O'Keefe-Dostrovsky's finding that some place units require a specific head direction in addition to position is the empirical anchor for *conjunctive* coding in spatial representation. The architectural prediction for the user's models: probing the grid-cell state should show that different *channels* in $C^{(t)}_{ij}$ at the same spatial position encode different *conjunctive features* (e.g., spatial position × object identity, spatial position × motion direction). This is what later work would call "grid × head direction conjunctive cells" (Sargolini et al. 2006) and is the empirical signature of *binding* implemented through spatial organization plus channel-dimension factorization.

**Touchpoint 4: cognitive map as the architectural-program horizon.** O'Keefe's later development of the cognitive-map framework ([behrens2018_cognitive_map](behrens2018_cognitive_map.md); [whittington2020_tem](whittington2020_tem.md)) — the hippocampus implements relational/structural maps that generalize beyond physical space — is the long-horizon architectural target for the user's program. The user's memory hierarchy should eventually support not just *physical spatial* maps (V1-paired, $C^{(1)}$) but *abstract relational* maps (deepest compartment): graphs of task variables, conceptual relations, social hierarchies. This is the long-term extension the cognitive-map literature licenses. O'Keefe-Dostrovsky 1971 is the founding empirical anchor for the entire trajectory.

**Touchpoint 5: hippocampus as the slow / episodic memory in the user's program.** O'Keefe-Dostrovsky establish the hippocampus as the substrate for spatially-indexed *episodic* storage. In the user's architecture, the *slow memory* compartment ($M_{slow}$ or the deepest compartment, gated by novelty as in [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md)) plays the architectural role of hippocampus. The user's program inherits a clean cortical-vs-hippocampal split: cortex / shallow memory holds the fast, continuously-updated perceptual content; hippocampus / slow memory holds the gated, novelty-driven episodic content. The 1971 paper is the founding empirical evidence for the hippocampal half of this split.

**Touchpoint 6: distributed map = multi-hub representation.** The "different units have different preferred locations" finding establishes the place-cell population as a *distributed* map. In the user's architecture, this maps onto the *distributed* representation across grid cells: no single grid cell holds the entire memory; the map is the joint state of all grid cells together. Decoding the user's memory state therefore requires *population* analysis, not single-cell readout — exactly as the modern hippocampal-decoding literature (Wilson & McNaughton 1993) eventually required for place cells.

**Touchpoint 7: dark-and-cue-change persistence — implications for the user's path-integration capability.** O'Keefe-Dostrovsky show that place firing persists in the dark and across changes in proximal cues — implicating an *integrative* representation that combines sensory and internal (e.g., proprioceptive, motor-efference) signals. The user's architecture should support analogous integration: the memory state should persist across input perturbations (dark frames, occlusions) by integrating internal dynamics with intermittent sensory input. The architectural commitment is to *recurrent integration*: the recurrent state survives input perturbations because it has internal dynamics that fill in missing input. The user's gridcell_rnn architecture, with its SIP + FT update structure and gate-bias-zero update dynamics, already supports this integration.

## 8. Citations to follow

- `okeefe_nadel1978_hippocampus_cognitive_map_book` — Oxford UP — the book-length elaboration that established the cognitive-map framework; the canonical follow-up. Not in seed.
- `muller_kubie_ranck1987_quantitative_place_fields_j_neurosci` — *J Neurosci* — quantitative place-field properties; the modern descriptive framework. Not in seed.
- `wilson_mcnaughton1993_ensemble_decoding_science` — *Science* — ensemble decoding of position from place-cell populations; the population-code demonstration. Not in seed.
- `skaggs_mcnaughton1996_replay_science` — *Science* — replay during sleep; the offline-consolidation finding. Not in seed.
- `okeefe_recce1993_phase_precession_hippocampus` — *Hippocampus* — theta phase precession; the temporal-coding extension. Not in seed.
- [hafting2005_grid_cells](hafting2005_grid_cells.md) — grid cells in entorhinal cortex; the medial-EC discovery that complements place cells. In seed.
- `moser_kropff_moser2008_spatial_review_annurev` — *Annu Rev Neurosci* — comprehensive review of place and grid cells. Not in seed.
- `leutgeb2005_independent_codes_ca3_ca1_science` — *Science* — independent codes in CA3/CA1; the within-hippocampus dissociation. Not in seed.
- `bostock_muller_kubie1991_remapping_hippocampus` — *Hippocampus* — remapping across environments; the environment-dependent representation finding. Not in seed.
- `morris1982_hippocampal_lesions_water_maze_nature` — *Nature* — hippocampal lesions impair spatial learning; the causal evidence for hippocampal necessity. Not in seed.
- [whittington2020_tem](whittington2020_tem.md) — TEM as the modern neural-network model of the cognitive map. In seed.
- [stachenfeld2017_predictive_map](stachenfeld2017_predictive_map.md) — predictive-map theory of hippocampal function. In seed.
- [behrens2018_cognitive_map](behrens2018_cognitive_map.md) — the modern cognitive-map review. In seed.
- [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md) — hippocampus-VTA loop for novelty-gated memory; the *function* of hippocampus the user's program builds on. In seed.
