---
id: whittington2020_tem
title: "The Tolman-Eichenbaum Machine: Unifying Space and Relational Memory through Generalization in the Hippocampal Formation"
authors:
  - "Whittington, James C. R."
  - "Muller, Timothy H."
  - "Mark, Shirley"
  - "Chen, Guifen"
  - "Barry, Caswell"
  - "Burgess, Neil"
  - "Behrens, Timothy E. J."
year: 2020
venue: "Cell"
doi: "10.1016/j.cell.2020.10.024"
arxiv: ""
url: "https://www.cell.com/cell/fulltext/S0092-8674(20)31388-X"
tags:
  - hippocampus
  - entorhinal-cortex
  - cognitive-map
  - relational-memory
  - neural-network
  - transformer
  - generalization
concepts:
  - gridcell_rnn
  - multi_compartmental_memory
  - world_model_emergence
  - bidirectional_hierarchical_feedback
  - coupled_rnn_world_models
related:
  - okeefe_dostrovsky1971_hippocampal_map
  - hafting2005_grid_cells
  - stachenfeld2017_predictive_map
  - behrens2018_cognitive_map
  - banino2018_vector_navigation
  - lecun2022_path_to_agi
  - vaswani2017_attention
  - lisman_grace2005_hippocampal_vta
relevance_to:
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# The Tolman-Eichenbaum Machine: Unifying Space and Relational Memory through Generalization in the Hippocampal Formation

## 1. Abstract

> "The hippocampal-entorhinal system is important for spatial and relational memory tasks. We formally link these domains, provide a mechanistic understanding of the hippocampal role in generalization, and offer unifying principles underlying many entorhinal and hippocampal cell types. We propose medial entorhinal cells form a basis describing structural knowledge, and hippocampal cells link this basis with sensory representations. Adopting these principles, we introduce the Tolman-Eichenbaum machine (TEM). After learning, TEM entorhinal cells display diverse properties resembling apparently bespoke spatial responses, such as grid, band, border, and object-vector cells. TEM hippocampal cells include place and landmark cells that remap between environments. Crucially, TEM predicts empirically recorded representations in complex non-spatial tasks. Additionally, TEM predicts hippocampal remapping is not random as previously believed; rather, structural knowledge is preserved across environments. We confirm this in simultaneously recorded place and grid cells." (Whittington, Muller, Mark, Chen, Barry, Burgess & Behrens 2020, *Cell* 183(5):1249-1263, abstract.)

## 2. Why this matters for us

Whittington et al. 2020 (TEM) is the *most architecturally relevant single neuroscience-meets-ML paper* for the user's program. It is the first formal model that *unifies* spatial and relational memory in a trained neural network whose internal units reproduce the major hippocampal-entorhinal cell types (grid, place, border, object-vector, landmark) and that *explicitly links to transformer-style attention* in the authors' follow-up work (Whittington, Warren & Behrens 2022 ICLR). For the user's program, TEM is foundational on three fronts. First, it provides the cleanest demonstration that *factorizing structure from content* — exactly the architectural choice the user's multi-compartmental memory commits to — produces a system that generalizes across environments and naturally develops cognitive-map-like representations. Second, it instantiates *graph-structured relational reasoning* as a neural-network computation, which is the long-horizon target for the user's deepest memory compartment. Third, it provides empirical predictions (structured remapping; same structural code re-bound to new content) that the user's models should reproduce — giving the user concrete behavioral signatures to validate the architecture against.

## 3. Key claims

1. Spatial and relational memory share an underlying *generalization mechanism* implemented by entorhinal-hippocampal circuitry — they are not separate systems.
2. MEC encodes a *structural basis* (graph-relational abstractions) *independent of sensory content* — the "where you are in the graph" code.
3. Hippocampus *binds the entorhinal structural basis to specific sensory observations* via a Hebbian fast-weight memory — the "what is at this graph location" binding.
4. A single trained network (TEM) reproduces grid, band, border, object-vector, place, and landmark cells — without any of them being hand-coded.
5. *Remapping is structured*: across environments, grid-to-place phase relationships are preserved — the structural code is re-used, only the content bindings change.
6. TEM generalizes to *non-spatial relational tasks* (transitive inference, social hierarchies, family trees, kinship graphs).
7. The model formalizes the *factorization of structure (where) from content (what)* — a clean computational principle.
8. TEM is mathematically related to graphical models and (later analyses by the same authors) to *transformer-style attention/memory* — explicitly linking hippocampus to modern ML attention mechanisms.

## 4. Methods

TEM is a recurrent neural network with two streams: a "g" stream (entorhinal-like) that learns abstract structural representations from a transition graph, and a "p" stream (hippocampal-like) that binds g to sensory observations via a Hebbian fast-weight memory. The g stream is a recurrent network whose state evolves under actions (transitions between graph nodes); the p stream takes the current g state and the current sensory observation and binds them, producing a hippocampal representation that the model can subsequently retrieve given either component. The network is trained by *self-supervised next-observation prediction* on random walks across families of graphs (2D worlds, hexagonal worlds, family trees, transitive-inference graphs). Crucially, the same g stream is re-used across graphs of the same structural type — even when the sensory bindings differ — which is the architectural mechanism for generalization. Learned units are compared post-hoc to single-cell electrophysiology from rodent MEC/HPC; new analyses of simultaneously recorded grid/place ensembles test the structured-remapping prediction.

## 5. Results

Headline empirical and simulation results:

- **All major MEC cell classes emerge after training**: hexagonal grid cells (with realistic gridness scores spanning the range observed in rats), band cells, border cells, object-vector cells. None of these were hand-coded into the architecture.
- **Multiple modular spacings emerge** in the grid cells, consistent with the dorsoventral spacing gradient ([hafting2005_grid_cells](hafting2005_grid_cells.md)).
- **TEM correctly predicts that place cells remap while grid cells coherently shift** — analyzed in simultaneously recorded ensembles (tens of cells from prior datasets); the structured-remapping prediction was confirmed in real data, validating the model.
- **TEM generalizes to novel graph structures after few transitions** (zero-shot inference of unseen edges) — the model exhibits *systematic generalization* from a training set of graphs to held-out graphs of the same family.
- **The model solves a 4-node transitive-inference task** analogous to behavioral data, demonstrating the framework's reach beyond physical space.
- **Structured remapping prediction confirmed**: phase offsets between grid cells preserved across environments in real data — a *prospective experimental prediction* the model made and the experiment confirmed.
- **TEM accounts for "splitter" and "non-grid spatial" cells** as emergent factors, providing a unified explanation for the apparent zoo of EC/HPC cell types.
- **Loss of g→p binding produces lesion-like deficits in relational tasks** — the model's lesion behavior matches biological lesion data.

## 6. Critique / limitations

TEM is the strongest current model in its class but has known limitations.

- **Training is purely supervised next-observation prediction**; biological learning rules (Hebbian, STDP, BTSP) are not specified. The model is a *computational* not *biological-mechanism* model.
- **Hippocampal Hebbian memory is highly idealized** (fast weights, no consolidation dynamics) — the model abstracts over the complex CA3/CA1/DG circuit dynamics.
- **Most "experimental" comparisons re-use existing datasets**; few prospective behavioral predictions tested in vivo by the same team (though the structured-remapping prediction was a notable exception).
- **Compute cost is significant**; biological plausibility of backprop-through-time as the learning algorithm is contested.
- **Model assumes graph structure of environment is known/given** as transition input — does not address how the structure itself is *learned* from raw sensory experience.
- **Does not address theta sequences, phase precession, or oscillatory dynamics** — the temporal-coding richness of biological hippocampus is abstracted away.
- **Limited test of scaling** to large, sensory-rich environments. The graphs are small; the sensory bindings are simple discrete tokens.
- **Single-task per network** — not lifelong learning across heterogeneous structures.
- **Closely related contemporaneous models** (Stachenfeld SR; CSCG by George et al. 2021) are not exhaustively compared; the field has multiple competing formal frameworks.

## 7. Connection to our work

TEM is one of the most architecturally consequential papers for the user's program because it instantiates several of the user's most-load-bearing commitments in a working neural network.

**Touchpoint 1: factorization of structure (where) from content (what) — the multi-compartmental architectural commitment.** TEM's central computational principle — separate the g stream (structural, "where in the graph") from the p stream (binding, "what is here") — is the cleanest formalization of the structure/content factorization the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commits to. The user's program has structurally analogous components: shallow memory holds *low-level perceptual content* (the "what"), while deeper memory should hold *task-/spatial-/relational-structure abstractions* (the "where in the abstract space"). TEM is the existence proof that this factorization, when implemented in a recurrent neural network, *develops the right computational properties* (grid-cell-like structural code, place-cell-like content binding, structured remapping) automatically.

**Touchpoint 2: the g stream as the architectural template for the user's deepest compartment.** TEM's g stream is a *recurrent* network whose state evolves under actions and whose internal units learn to represent *abstract structural relations* (e.g., grid cells for 2D space, equivalent abstract codes for transitive-inference graphs). This is the architectural template for the user's deepest memory compartment: its content should not be raw perceptual features (which belong to shallow compartments) but *abstract structural representations* — graphs of task variables, relational invariants, action-conditioned transitions. The user's program inherits a clean target for the deepest compartment: what TEM's g stream learns is what the deepest user-program compartment should learn.

**Touchpoint 3: TEM as transformer-attention link — convergence with the user's Feedback Transformer.** Whittington, Warren & Behrens 2022 (ICLR follow-up) shows that TEM's architecture is mathematically equivalent to a particular kind of *transformer with positional encodings* — the g stream's structural code is functionally analogous to positional encoding, and the p stream's content binding is functionally analogous to value computation. This is a *direct link* between the hippocampus and transformer-style attention: the user's Feedback Transformer central attention is therefore in the same architectural family as TEM, and the user's program is licensed to draw on the hippocampal-relational-memory literature as a biological framework for transformer-based memory architectures.

**Touchpoint 4: structured remapping as the architectural prediction for the user's models.** TEM's structured-remapping prediction (preserved phase offsets across environments) is the kind of *empirical signature* the user's models should reproduce: training the user's model on multiple environments and showing that the *structural* layer of the memory hierarchy (deepest compartment) preserves its internal organization across environments, while *content* layers (shallower compartments) re-bind to new sensory inputs. This is a concrete experimental probe for the user's multi-compartment design — and one of the cleanest tests of whether the architectural hierarchy has correctly implemented the structure/content factorization.

**Touchpoint 5: zero-shot generalization to new graph structures — the long-horizon target.** TEM generalizes to novel graphs of the same structural family after only a few transitions; this is the kind of *systematic generalization* that the user's program targets but has not yet achieved. The architectural lesson: generalization requires a *separate structural code* that can be re-used across content bindings. The user's program inherits this lesson and should prioritize architectural designs that maintain a clean separation between structure and content, with the structural component re-usable across tasks/environments.

**Touchpoint 6: convergence with `world_model_emergence`.** TEM trains by self-supervised next-observation prediction — *exactly* the kind of training signal the user's [world_model_emergence](../concepts/world_model_emergence.md) thesis predicts should produce world-model-like representations. TEM is therefore a *constructive proof* that the user's world-model-emergence thesis is at least achievable: with the right architecture (g/p factorization) and the right training signal (next-observation prediction), grid-like and place-like representations *do* emerge, providing a forward-predictable internal state. The user's program is licensed by TEM to expect that similar emergent world-model properties should arise in the multi-hub architecture under analogous training pressures.

**Touchpoint 7: g/p coupling as Hebbian fast-weight memory — the architectural alternative to the user's FT integration.** TEM's hippocampal stream uses a *Hebbian fast-weight memory* to bind g (structure) and observation (content). The user's architecture uses a *Feedback Transformer* attention pass for analogous integration. These are alternative integration mechanisms: TEM's is more biologically constrained (Hebbian, no backprop through the binding); the user's is more computationally flexible (full self-attention with gradient flow). The architectural comparison is a *design-space exploration question* — does the Hebbian fast-weight binding offer advantages over the FT integration for relational tasks? This is an open question worth empirical investigation.

**Touchpoint 8: implications for the user's iterative VAE.** TEM's recurrent g stream and the binding p stream form a coupled-RNN architecture; the user's [iterative_variational_encoder_decoder](../concepts/iterative_variational_encoder_decoder.md) is a different coupled architecture. The structural lesson from TEM: the *iteration* is essential — the network needs multiple updates to refine its structural/content bindings. The user's iterative VAE should therefore inherit TEM's lesson that the binding between structure and content is an iterative refinement, not a one-shot operation.

## 8. Citations to follow

- `whittington_warren_behrens2022_tem_transformer_iclr` — *ICLR* — TEM-transformer equivalence; the crucial bridge between hippocampus and modern ML attention. Not in seed.
- `george2021_clone_structured_cognitive_graphs_nat_comm` — *Nature Communications* — clone-structured cognitive graphs; the contemporaneous-alternative model. Not in seed.
- [banino2018_vector_navigation](banino2018_vector_navigation.md) — vector-based navigation in deep RL agents; the related ML-grid-cell demonstration. In seed.
- `whittington_behrens2022_structure_learning_nat_rev_neurosci` — *Nature Reviews Neuroscience* — review of structure learning; the authors' broader framework. Not in seed.
- `sorscher2023_unified_theory_grid_cells_neuron` — *Neuron* — unified theory of grid cells; the modern theoretical synthesis. Not in seed.
- `park2020_abstract_relational_maps_neuron` — *Neuron* — abstract relational maps in humans. Not in seed.
- `schapiro2017_community_structure_phil_trans_b` — *Phil Trans R Soc B* — community structure and hippocampus. Not in seed.
- [behrens2018_cognitive_map](behrens2018_cognitive_map.md) — the cognitive-map review that motivates the TEM framework. In seed.
- `liu_replay_structure_cell2021` — *Cell* — replay of structured experience. Not in seed.
- `mcnamee2021_flexible_hippocampus_nat_neuro` — *Nature Neuroscience* — flexible computation in HPC. Not in seed.
- `bakermans2024_action_conditioned_structure` — extensions to TEM with action-conditioned structure. Not in seed.
- `vaswani2017_attention` — *NeurIPS* — the original Transformer paper; later linked to TEM. Already in seed.
- [stachenfeld2017_predictive_map](stachenfeld2017_predictive_map.md) — the SR alternative model that TEM extends/contrasts. In seed.
- [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md) — the hippocampus-VTA novelty loop; the gating mechanism that complements TEM's binding mechanism. In seed.
