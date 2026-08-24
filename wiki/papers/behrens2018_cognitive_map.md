---
id: behrens2018_cognitive_map
title: "What is a cognitive map? Organizing knowledge for flexible behavior"
authors:
  - "Behrens, Timothy E. J."
  - "Muller, Timothy H."
  - "Whittington, James C. R."
  - "Mark, Shirley"
  - "Baram, Alon B."
  - "Stachenfeld, Kimberly L."
  - "Kurth-Nelson, Zeb"
year: 2018
venue: "Neuron"
doi: "10.1016/j.neuron.2018.10.002"
arxiv: ""
url: "https://www.cell.com/neuron/fulltext/S0896-6273(18)30856-0"
tags:
  - hippocampus
  - cognitive-map
  - relational-memory
  - generalization
  - successor-representation
  - review
concepts:
  - multi_compartmental_memory
  - hierarchical_predictive_coding
  - world_model_emergence
  - coupled_rnn_world_models
related:
  - okeefe_dostrovsky1971_hippocampal_map
  - hafting2005_grid_cells
  - whittington2020_tem
  - stachenfeld2017_predictive_map
  - banino2018_vector_navigation
  - lisman_grace2005_hippocampal_vta
  - lecun2022_path_to_agi
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# What is a cognitive map? Organizing knowledge for flexible behavior

## 1. Abstract

> "It is proposed that a cognitive map encoding the relationships between entities in the world supports flexible behavior, but the majority of the neural evidence for such a system comes from studies of spatial navigation. Recent work describing neuronal parallels between spatial and non-spatial behaviors has rekindled the notion of a systematic organization of knowledge across multiple domains. We review experimental evidence and theoretical frameworks that point to principles unifying these apparently disparate functions. These principles describe how to learn and use abstract, generalizable knowledge and suggest that map-like representations observed in a spatial context may be an instance of general coding mechanisms capable of organizing knowledge of all kinds. We highlight how artificial agents endowed with such principles exhibit flexible behavior and learn map-like representations observed in the brain. Finally, we speculate on how these principles may offer insight into the extreme generalizations, abstractions, and inferences that characterize human cognition." (Behrens, Muller, Whittington, Mark, Baram, Stachenfeld & Kurth-Nelson 2018, *Neuron* 100(2):490-509, abstract.)

## 2. Why this matters for us

Behrens et al. 2018 is the *programmatic statement* of the modern cognitive-map framework: the hippocampal-entorhinal system implements a *general-purpose relational/cognitive map* whose computational principles (factorization of structure from content, abstract relational coding, successor-representation predictive computation) generalize *beyond physical space* to social hierarchies, conceptual continua, and arbitrary relational graphs. For the user's program, this is the *long-horizon architectural target*: the user's memory hierarchy should eventually support not just visual-spatial maps but *abstract relational* maps — the same kind of representation that humans use for flexible inference, planning, and generalization. The review is also the theoretical setup for [whittington2020_tem](whittington2020_tem.md) (TEM), which two years later instantiated the framework as a working neural network. The user's program inherits the cognitive-map ambition: the deepest memory compartment should be capable of holding *task-/relational-/conceptual* structure that generalizes across environments and supports the kind of zero-shot inference TEM achieves.

## 3. Key claims

1. The hippocampal-entorhinal system implements a *general-purpose relational/cognitive map*, not a purely spatial one — neural codes for non-spatial relational tasks are computed in the same circuits.
2. Map-like neural codes (place, grid, object-vector cells) *generalize to abstract feature spaces* (social hierarchy, conceptual continua, transitive-inference orderings).
3. *Factorization of structure* (graph relations) *from content* (sensory bindings) is a key computational principle — structure is the re-usable substrate, content is what gets bound.
4. *Generalization across environments* arises from re-use of an abstract structural code paired with new content bindings.
5. The framework *links classical cognitive-map theory* (Tolman) *with reinforcement-learning concepts* (successor representation, model-based RL) — uniting cognitive psychology with computational RL.
6. *Artificial agents endowed with such principles* (e.g., grid-like deep RL networks, predictive coding nets) *display map-like representations* — establishing that the cognitive-map framework is computationally instantiable.
7. *Human cognition's extreme abstraction* may exploit the same hippocampal-entorhinal machinery applied to non-spatial relational graphs — a strong claim about the substrate of high-level cognition.
8. The cognitive-map hypothesis offers a *unifying account* of episodic memory, planning, and inference — three apparently distinct cognitive functions implemented by the same circuit.

## 4. Methods

Conceptual review; no new data. The authors synthesize (i) rodent electrophysiology (place, grid, object-vector, splitter, lap cells); (ii) human fMRI of abstract spaces — Constantinescu et al. 2016 on grid-like 6-fold fMRI signal for abstract bird-stretching task; Schapiro et al. 2013 on community-structure detection; Garvert et al. 2017 on successor-like representations for abstract graphs; (iii) computational frameworks — successor representation (Stachenfeld et al. 2017), deep RL agents with grid-like representations (Banino et al. 2018, Cueva & Wei 2018), predictive models, structure-learning algorithms; (iv) human behavioral and social-cognition data. The argument structure is to canvas evidence that the hippocampal-entorhinal system encodes relational structure across *spatial*, *non-spatial perceptual* (e.g., sound frequency space), *abstract* (e.g., bird morphology), and *social* (e.g., hierarchies) domains, then to develop the computational principle of structure/content factorization as the unifying account.

## 5. Results

Key empirical anchors consolidated in the review (no new data):

- **Grid-like 6-fold fMRI signal in human EC for abstract bird-stretching task** (Constantinescu et al. 2016 *Science*) — the first demonstration that grid-like codes operate in conceptual space.
- **Successor-like representations recovered in human EC for non-spatial graph learning** (Garvert et al. 2017 *eLife*) — the SR framework operating in non-spatial domains.
- **Place-like cells encode position in abstract sound-frequency space in rodents** (Aronov, Nevers & Tank 2017 *Nature*) — the non-spatial place-cell demonstration.
- **Deep RL agents trained for navigation develop grid-like units** (Banino et al. 2018; Cueva & Wei 2018) — the ML-side evidence for the computational principle.
- **Hippocampal community structure detection in fMRI** (Schapiro et al. 2013) — the brain segments experience at relational boundaries.
- **Social-hierarchy encoding in hippocampal-amygdalar areas** (Kumaran et al. 2012) — the social-cognition extension.
- **Replay of non-spatial sequences in MEG** (Kurth-Nelson et al. 2016) — relational structure is replayed offline, just like spatial trajectories.
- **Schema-consistent learning is hippocampal-dependent and supports rapid generalization** (Tse et al. 2007 *Science*) — the substrate of schema-based inference.

## 6. Critique / limitations

This is a theoretical review with the limitations typical of programmatic statements.

- **A theoretical review — no novel data**; predictions remain to be tested prospectively. The empirical confirmation (especially of TEM's structured-remapping prediction) came in subsequent work.
- **Concept of "cognitive map" remains loosely defined**; risk of unfalsifiability when stretched across spatial, conceptual, social, and abstract modalities. The framework can absorb almost any positive finding by treating it as a new "map-like" representation.
- **Limited engagement with alternative accounts** — pure episodic-memory theories (Eichenbaum tradition), BTSP-based models, complementary learning systems (McClelland & O'Reilly). The review prefers the cognitive-map framework without adjudicating against these.
- **Treats spatial and non-spatial map representations as homologous** without resolving anatomical/circuit-level mappings. *Is* the same MEC circuit really computing the abstract bird-stretching grid? The neural-level evidence is correlational.
- **Computational frameworks discussed (SR, deep RL agents) have known limits** (scaling, biological plausibility, sample efficiency) not deeply critiqued.
- **Heavy weighting toward authors' own modeling lineage** (TEM precursor; SR co-authors Behrens, Stachenfeld); the review prefigures TEM 2020.
- **Bridges to human cognition are speculative** and lack causal evidence — the claim that "human abstract reasoning runs on the same hippocampal-entorhinal machinery" is intuitively appealing but not rigorously demonstrated.
- **Does not deeply address developmental / lifespan emergence** of map-like codes — when and how do these representations develop?

## 7. Connection to our work

Behrens et al. 2018 is the load-bearing theoretical reference for the user's program's long-horizon architectural ambition: building a system whose memory can generalize across not just physical space but *abstract relational structure*.

**Touchpoint 1: cognitive map as the long-horizon architectural target.** The Behrens-et-al cognitive-map framework — a general-purpose relational map applicable to spatial, conceptual, social, and abstract domains — is the *long-term architectural target* for the user's program. The user's deepest memory compartment should not be a spatial map of pixel positions (that's the shallow compartment's job); it should be a *relational/structural map* of task variables, action-conditioned transitions, conceptual relations. The user's program inherits the ambition: build an architecture whose deepest representational layer is *general-purpose relational*. The user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commitment already prepares the architectural ground for this — multiple compartments at different abstraction levels — and the cognitive-map framework provides the *biological target* for what the deepest compartment should be.

**Touchpoint 2: structure/content factorization — the central architectural commitment.** The review's central computational principle — factorization of *structure* (re-usable abstract relations) from *content* (specific sensory bindings) — is the *load-bearing computational commitment* of the cognitive-map framework, and is directly inherited in the user's program. The user's multi-compartmental memory should implement this factorization: the deepest compartment holds the *structure* (the re-usable graph), and intermediate/shallow compartments hold the *content* (the sensory bindings that get reattached to the structure in each new environment). This is the architectural blueprint for the long-horizon program.

**Touchpoint 3: generalization-through-re-use — the architectural rationale.** The cognitive-map framework's claim that *generalization arises from re-use of structural codes paired with new content bindings* provides the architectural rationale for the user's hierarchical-memory commitment. To support generalization across environments/tasks, the deepest compartment must be *task-invariant* (it carries the abstract structural code that re-applies across tasks), while shallower compartments are *task-specific* (they carry the per-task content bindings). The user's program inherits the rationale and the architecture has to support task-invariant deep storage — a strong design constraint.

**Touchpoint 4: link to RL — convergence with the user's world-model program.** The review's link between the cognitive-map framework and *reinforcement learning* (specifically the successor representation and model-based RL) converges with the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis. The cognitive map IS a world model: it predicts what will follow what, both spatially and relationally. The user's program is therefore licensed to interpret the user's architecture as a *computational instance of the cognitive-map framework*, with the world-model-emergence prediction being the empirical signature that the architecture has succeeded.

**Touchpoint 5: artificial agents developing grid-like codes — the empirical bridge to the user's models.** The review's emphasis that *artificial agents trained on the right tasks develop grid-like and place-like representations* (citing Banino et al. 2018, Cueva & Wei 2018) is the empirical bridge to the user's models. The architectural prediction: training the user's multi-compartment architecture on path-integration or navigation tasks should result in *emergent* map-like representations in the deeper compartments. The cognitive-map framework licenses this expectation; the empirical evidence from existing deep RL grid-cell agents supports it; the user's architecture should be able to reproduce and extend the demonstration.

**Touchpoint 6: human-abstract-cognition application — the manuscript-level framing.** The review's speculation that *human abstract reasoning runs on hippocampal-entorhinal machinery* provides the *manuscript-level framing* for the user's research program. The user's program is, ultimately, an attempt to build computational models of biologically-grounded attention and memory; the cognitive-map framework provides the high-level claim that *this is the substrate of human cognition*. The user's manuscript can position the program as: "computational models of the hippocampal-entorhinal cognitive map operationalized in deep neural-network terms" — a strong manuscript-level frame.

**Touchpoint 7: replay and offline consolidation — the gap in the user's program.** The review's mention of relational replay (Kurth-Nelson et al. 2016) and schema-consistent learning (Tse et al. 2007) points to a *gap* in the user's program: offline consolidation / replay is not currently part of the architectural commitments. The cognitive-map framework predicts that flexible relational learning requires offline replay (which the user's architecture does not yet implement) and that schema-consistent learning supports rapid generalization (which the user's architecture should target). This is a *direction for architectural extension*: add an offline-consolidation / replay mechanism to the user's program, perhaps as a *dream phase* in which the multi-hub system runs forward in imagination without external input, refining the relational structure in the deepest compartment.

**Touchpoint 8: convergence with TEM as the constructive instantiation.** Behrens et al. 2018 is the *theoretical framework*; [whittington2020_tem](whittington2020_tem.md) is its *constructive instantiation* in a trained neural network. For the user's program, the pair functions as: cognitive-map framework (Behrens) → architectural instantiation (TEM) → user's program (multi-compartment FT-coupled architecture). The user's program is the next instantiation in the lineage, scaling TEM's principles to richer sensory environments (vision, video) and additional architectural commitments (multi-hub competition, attention-mediated allocation, novelty-gated slow memory).

## 8. Citations to follow

- [whittington2020_tem](whittington2020_tem.md) — TEM as the constructive instantiation of the framework. In seed.
- `bellmund2018_navigating_cognition_science_review` — *Science* — navigating cognition with maps in humans. Not in seed.
- `park2020_abstract_relational_maps_neuron` — *Neuron* — abstract relational maps in humans. Not in seed.
- `bao2019_grid_primate_ec_visual_neuron` — *Neuron* — grid-like coding in primate EC for visual space. Not in seed.
- `liu_replay_structure_cell2021` — *Cell* — sequence replay of structure. Not in seed.
- `mok_love2019_non_spatial_concept_nat_comm` — *Nature Communications* — non-spatial concept representations. Not in seed.
- `eichenbaum2017_memory_cognitive_map_nrn` — *Nature Reviews Neuroscience* — memory and the cognitive map (related framing). Not in seed.
- `george2021_clone_structured_cognitive_graphs_nat_comm` — *Nature Communications* — clone graphs and hippocampus; the structural alternative model. Not in seed.
- `whittington_warren_behrens2022_tem_transformer_iclr` — *ICLR* — TEM-attention bridge; the modern follow-on. Not in seed.
- `schuck_niv2019_sequential_representations_science` — *Science* — sequential representations in hippocampus. Not in seed.
- `momennejad2020_learning_structures_curr_opin` — *Curr Opin Behav Sci* — learning structures from experience. Not in seed.
- `mcnamee2021_flexible_hippocampus_nat_neuro` — *Nature Neuroscience* — flexible HPC computation. Not in seed.
- [stachenfeld2017_predictive_map](stachenfeld2017_predictive_map.md) — the SR formalization that the cognitive-map review integrates. In seed.
- [hafting2005_grid_cells](hafting2005_grid_cells.md) — the grid-cell discovery; the spatial-map foundation. In seed.
- [okeefe_dostrovsky1971_hippocampal_map](okeefe_dostrovsky1971_hippocampal_map.md) — the place-cell discovery; the cognitive-map starting point. In seed.
- [banino2018_vector_navigation](banino2018_vector_navigation.md) — grid-like codes in deep RL agents; the ML demonstration. In seed.
- [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md) — the gating mechanism that controls map updates. In seed.
- [lecun2022_path_to_agi](lecun2022_path_to_agi.md) — the JEPA program that develops a world-model alternative; relates to the cognitive-map ambition. In seed.
