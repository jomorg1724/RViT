---
id: panichello_buschman2021_shared_mechanisms
title: "Shared mechanisms underlie the control of working memory and attention"
authors:
  - "Panichello, Matthew F."
  - "Buschman, Timothy J."
year: 2021
venue: "Nature"
doi: "10.1038/s41586-021-03390-w"
arxiv: ""
url: "https://doi.org/10.1038/s41586-021-03390-w"
tags:
  - working-memory
  - visual-attention
  - prefrontal-cortex
  - primate-neurophysiology
concepts:
  - attentional-template
  - working-memory-persistent-activity
  - top-down-feedback
  - multi-compartmental-memory
related:
  - awh2006_attention_wm
  - gazzaley_nobre2012_topdown
  - constantinidis2018_persistent_activity
  - mante2013_context_dependent_pfc
  - desimone_duncan1995_biased_competition
  - bisley_goldberg2010_parietal_priority
  - kiyonaga_egner2013_wm_internal_attention
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_15
status: full
depth: full
last_updated: "2026-05-16"
---

# Shared mechanisms underlie the control of working memory and attention

## 1. Abstract

Cognitive control guides behavior by controlling *what*, *when*, and *how* information is represented in the brain. For example, attention controls sensory processing — top-down signals from prefrontal and parietal cortex strengthen the representation of task-relevant stimuli. A similar 'selection' mechanism is thought to control the representations held 'in mind' — in working memory. The authors show that *shared neural mechanisms underlie the selection of items from working memory and attention to sensory stimuli*. They trained rhesus monkeys to switch between two tasks — either selecting one item from a set of items held in working memory or attending to one stimulus from a set of visual stimuli — and recorded simultaneously in PFC, posterior parietal, and visual cortex. Similar representations in **prefrontal cortex** encoded the control of both selection and attention, suggesting that PFC acts as a *domain-general controller*. By contrast, both attention and selection were represented *independently* in parietal and visual cortex. Both selection and attention facilitated behavior by *enhancing and transforming* the representation of the selected memory or attended stimulus. Specifically, during the selection task, memory items were initially represented in independent subspaces of neural activity in PFC; selecting an item caused its representation to *transform* from its own subspace to a new "output" subspace used to guide behavior. A similar transformation occurred for attention. The results suggest that PFC controls cognition by *dynamically transforming representations* to control what and when cognitive computations are engaged.

## 2. Why this matters for us

Panichello & Buschman 2021 is the *modern primate single-unit confirmation* of the shared-substrate framework for attention and WM. Where Awh et al. 2006 ([awh2006_attention_wm](research_db/papers/awh2006_attention_wm.md)) catalogs the behavioral evidence and Gazzaley & Nobre 2012 ([gazzaley_nobre2012_topdown](research_db/papers/gazzaley_nobre2012_topdown.md)) identifies the neural-region overlap, Panichello & Buschman provides the *single-unit-level* mechanism: PFC implements a *domain-general controller* that dynamically transforms representations to support both attention and WM. The paper is the most direct empirical evidence that attention and WM share a *computational mechanism* at the cellular level. For the user's program, this paper is the load-bearing citation for the architectural commitment that the central self-attention substrate (analog of PFC) implements both attention-guidance and WM-maintenance through the same machinery.

## 3. Key claims

1. **PFC is the domain-general controller for both attention and WM.** Single-unit recordings in macaque PFC show that the same population implements selection-from-WM and selection-from-sensory-input, with similar neural signatures across tasks.
2. **Parietal and visual cortex represent attention and WM independently.** Outside PFC, the two cognitive operations are dissociable at the single-unit level. The shared-substrate property is specific to PFC.
3. **Selection works by *dynamic representational transformation*.** In PFC, the selected item's representation *transforms* — moves from its own subspace in neural state space to a shared *output* subspace used to guide behavior. The transformation is the act of selection.
4. **The same transformation mechanism serves attention and WM.** The "output subspace" is the same regardless of whether the selected item comes from WM or from current sensory input.
5. **Initial representations are independent.** Before selection, each WM item (or each sensory stimulus) is represented in its *own* independent subspace in PFC. The independence allows multiple items to coexist without interference.
6. **Selection is a continuous transformation, not a switching event.** The geometric transformation that implements selection happens *gradually* over hundreds of milliseconds, with the magnitude of the transformation predicting behavioral performance.
7. **PFC's role is "what" and "when," not "where."** The selected representation's content (what is attended / remembered) and timing (when the selection occurs) are PFC's purview; spatial details are computed in parietal/visual cortex.

## 4. Methods

**Task design.** Rhesus monkeys trained on two tasks that share a common selection structure:
- **WM-selection task.** Sample stimulus shown, delay period, then a cue indicating which previously-shown item to report.
- **Attention task.** Multiple stimuli appear simultaneously; a cue indicates which one to attend; subsequent decision based on the attended stimulus.

The tasks are matched in their selection demands but differ in whether the selection is *from-memory* or *from-current-input*.

**Recordings.** Simultaneous multi-electrode recordings in PFC, posterior parietal cortex, and visual cortex during task performance.

**Analysis.** Population-level dynamics characterized using dimensionality reduction (PCA, demixed PCA), subspace identification (each item's representation has its own neural-state-space subspace), and trajectory analysis (movement of representations through subspaces over time).

**Comparison across tasks.** Same monkeys, same neurons (where possible), same analytical pipeline applied to both tasks. The match (or mismatch) in neural patterns characterizes whether the two tasks share mechanism.

## 5. Results

The principal quantitative findings:

- **PFC shows shared control across tasks.** The same subspace structure encodes the selection process in both tasks. The PFC population trajectory during selection is similar across the WM and attention versions.
- **Parietal and visual cortex show task-specific representations.** Attention is represented in visual / parietal cortex with one neural pattern; selection-from-WM is represented with a *different* pattern. The shared mechanism is specifically a PFC property.
- **Output subspace.** A specific subspace in PFC activity is associated with the *selected* representation. Items not selected stay in their own subspaces; selected items transform into the output subspace.
- **Trajectory dynamics.** The transformation from item-specific subspace to output subspace takes ≈200–400 ms, with the rate of transformation predicting behavioral accuracy.
- **Item-specific subspaces.** Each WM item has its own approximately-orthogonal subspace in PFC, allowing parallel maintenance without crosstalk.
- **Generalization.** The framework generalizes across stimulus types and across animal subjects, supporting the claim that this is a *general* PFC computation rather than a task-specific quirk.

## 6. Critique / limitations

The analyses are *population-level*. Single-unit responses are heterogeneous (mixed selectivity, varying tuning); the clean subspace structure is only visible at the population level. Whether the population-level structure reflects a specific cellular implementation or is an emergent property of recurrent PFC dynamics is not fully resolved.

The task design is *highly controlled*. Real-world cognition involves messier, more naturalistic attention-WM interactions. Whether the dynamic-transformation mechanism scales to naturalistic settings is an empirical open question.

The recordings are from PFC, PPC, and visual cortex. Other regions implicated in attention and WM (thalamus, basal ganglia, hippocampus) are not characterized. The "domain-general controller" claim is specifically about PFC; the broader brain network's contributions are not addressed.

The framework characterizes PFC's role as transformation; *how* the transformation is implemented at the synaptic level is not specified. Subsequent computational modeling (e.g., trained RNNs reproducing the dynamics, à la Mante 2013, [mante2013_context_dependent_pfc](research_db/papers/mante2013_context_dependent_pfc.md)) is needed to mechanistically explain the transformation.

The framework doesn't engage with *predictive coding*. The "dynamic transformation" framing is compatible with PFC implementing precision-weighted prediction errors but the paper doesn't draw the connection.

## 7. Connection to our work

This paper provides the *single-unit primate-data* support for the user's commitment to a shared attention-WM substrate:

**The central self-attention substrate as a domain-general controller.** The user's multi-hub system ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)) places a shared self-attention substrate at the center, with each hub contributing to and reading from it. Panichello & Buschman's finding that PFC is a *domain-general controller* for selection-from-WM and selection-from-sensory-input is the biological precedent for this architectural commitment.

**The Feedback Transformer as the transformation mechanism.** Panichello & Buschman identify *dynamic representational transformation* as the mechanism by which selection works in PFC. The Feedback Transformer ([feedback_transformer](research_db/concepts/feedback_transformer.md)) implements transformation: the Hadamard-product of sensory and feedback Q/K projections is the architectural form of "transform the input representation to a task-specific output."

**Subspace structure of memory.** Panichello & Buschman's finding that each WM item has its own neural subspace, with selection transforming items into a shared output subspace, suggests an architectural commitment for the user's multi-compartmental memory: each memory compartment (or each hub's memory state) should have its own representational subspace, with the central attention substrate as the "output subspace" all are transformed into when selected. The user's program's architectural cleanliness inherits from this finding.

**Mante 2013 + Panichello 2021 → PFC as recurrent dynamical system implementing context-dependent selection.** Combined with Mante 2013 ([mante2013_context_dependent_pfc](research_db/papers/mante2013_context_dependent_pfc.md)), Panichello & Buschman gives a unified picture: PFC is a recurrent dynamical system that selects task-relevant input from a larger candidate set via context-dependent transformation. The user's central self-attention substrate is the AI analog.

**The trajectory-based interpretation.** The recurrent ViT's attention map evolves over recurrent timesteps; the cued-attention effect develops gradually. This is the architectural analog of Panichello-Buschman's "selection happens over 200–400 ms." The architectural commitment to *dynamic* attention (rather than instantaneous selection) is biologically warranted.

**Multi-hub competition as multi-item subspace dynamics.** In the multi-hub system, hubs compete for control of the central substrate. Each hub's contribution can be thought of as occupying its own subspace; the central attention map is determined by which subspace dominates. Panichello-Buschman's framing of WM items as occupying orthogonal subspaces with selective transformation into a shared output subspace is the cognitive-neuroscience analog of this architectural mechanism.

The recurrent ViT paper cites Panichello & Buschman in its bibliography (ref [15]). Future manuscripts that elaborate the architectural commitment to shared attention-WM should cite this paper as the strongest single-unit support.

## 8. Citations to follow

- `awh2006_attention_wm` — behavioral framework. In seed, full depth.
- `gazzaley_nobre2012_topdown` — neuroimaging framework. In seed, full depth.
- `mante2013_context_dependent_pfc` — PFC as recurrent dynamical system. In seed, full depth.
- `constantinidis2018_persistent_activity` — WM persistent activity. In seed, full depth.
- `desimone_duncan1995_biased_competition` — biased competition for selection. In seed, full depth.
- `bisley_goldberg2010_parietal_priority` — parietal priority map. In seed, full depth.
- `kiyonaga_egner2013_wm_internal_attention` — WM as internal attention. In seed.
- `buschman_kastner2015_neural_substrates_attention` — Buschman's earlier attention review. Not in seed.
- `panichello_buschman2024_dynamic_control_pfc` — Panichello-Buschman follow-up work. Not in seed.
