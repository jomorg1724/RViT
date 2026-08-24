---
id: hawkins2021_thousand_brains
title: "A Thousand Brains: A New Theory of Intelligence"
authors:
  - "Hawkins, Jeff"
year: 2021
venue: "Basic Books"
doi: ""
arxiv: ""
url: ""
tags:
  - theoretical-essay
  - review
  - cortical-anatomy
  - predictive-coding
concepts:
  - cortical-microcircuit-model
  - hierarchical-predictive-coding
  - multi-hub-multi-objective-system
  - competition-emergent-predictive-coding
  - world-model-emergence
  - parallel-recurrent-units
  - feature-binding
  - top-down-feedback
related:
  - clark2013_whatever_next
  - friston2010_fep_unified_theory
  - lecun2022_path_to_agi
  - schmidhuber2015_learn_to_think
  - pearl2018_book_of_why
  - marcus2025_llm_critique
  - bastos2012_canonical_microcircuits
  - felleman_vanessen1991_hierarchical_cortex
  - weiler2025_l6_corticocortical
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# A Thousand Brains: A New Theory of Intelligence

## 1. Abstract

*A Thousand Brains* is Jeff Hawkins's book-length popular synthesis of work done at Numenta over roughly fifteen years on the neocortex as a uniform learning machine. Building on Mountcastle's hypothesis that all cortical columns execute a common algorithm, Hawkins argues that every column independently learns a complete model of objects in the world by combining sensory input with a *reference frame* signal carried by grid-cell-like and place-cell-like neurons in deep cortical layers. Because there are roughly 150,000 columns per neocortex, the brain holds not one model of the world but thousands of partial, redundant models that vote — over long-range cortico-cortical projections — to produce a single, stable perceptual experience. The theory unifies perception, conceptual knowledge, and the cortical anatomy of layers, columns, and long-range projections under one mechanism. Part II extrapolates the theory to machine intelligence, arguing that current deep-learning systems lack reference frames, sensorimotor loops, and column-level voting, and that progress towards AGI will require these. Part III is more speculative, addressing existential risk, the long-term future of intelligence, and the value of preserving knowledge beyond a single civilization.

## 2. Why this matters for us

Hawkins 2021 is the canonical popular statement of an architectural commitment that runs *directly parallel* to the user's program: many independent, complete models of the world, communicating via a shared bandwidth-limited channel, with the unified percept emerging from competition / voting across them. Where Clark 2013 ([clark2013_whatever_next](research_db/papers/clark2013_whatever_next.md)) supplies the philosophical framing of cortex-as-prediction-machine, Hawkins supplies the *architectural* commitment that the unit of prediction is the cortical column, not a global cortex-wide generative model, and that consensus across thousands of columns is the mechanism by which a coherent percept emerges. This is the same architectural intuition the user articulates in `multi_hub_multi_objective_system` and in the competition-emergent-PC thesis: many hubs / columns each holding a partial model, communicating through a bottleneck (self-attention for the user; long-range L2/3 projections and voting for Hawkins), with the percept being the consensus.

## 3. Key claims

1. **Mountcastle's hypothesis is correct and load-bearing.** The neocortex is uniform: roughly 150,000 cortical columns each execute the same canonical algorithm. Sensory modality, hierarchical level, and conceptual abstraction differ only in input and connectivity, not in the underlying computation.
2. **Each column is a complete sensorimotor modeler.** A column learns full 3D object models, not features. A V1 column does not merely detect edges — it predicts what edge it will sense next given the motor command being issued. The output of a column is an object identity (or a small set of compatible identities), not a feature vector.
3. **Reference frames are the central computational primitive.** Each column attaches sensory observations to a *location* in an object-centered reference frame. Grid-cell-like neurons in deep cortical layers (layer 6 in Hawkins's account) provide the location code; "what" features in middle layers are bound to "where" coordinates from below.
4. **Sensorimotor loops, not static images, are the right computational frame.** Recognition is the result of a sequence of sensations integrated through known motor commands — analogous to recognizing a coffee cup by moving your fingers over it. Static-image classification is a degenerate, biologically atypical special case.
5. **Thousands of columns vote to produce a unified percept.** Each column's hypothesis about object identity is broadcast over long-range L2/3 cortico-cortical projections. Columns that agree reinforce one another; conflicting hypotheses suppress one another. The final, stable, agreed-upon identity is the percept.
6. **Concepts are objects in abstract reference frames.** High-level cortical regions extend the same machinery to mathematical, social, and linguistic concepts: a concept like *democracy* is structured in a reference frame the same way a coffee cup is structured in 3D space.
7. **Current deep learning is incomplete in specific ways.** It lacks reference frames, lacks sensorimotor loops, lacks column-level voting, and treats hierarchy as a feature-extraction stack rather than a confederation of complete modelers. Hawkins argues this explains the brittleness, sample-inefficiency, and lack of common-sense reasoning in current systems.
8. **The "old brain" / "new brain" distinction matters for AI safety.** The neocortex is a model-builder; motivational drives are in subcortical structures. Hawkins argues that intelligence per se does not entail goals, and that AI risk discussions conflate the two. Part III is built on this distinction.
9. **Knowledge as a substrate-independent legacy.** Hawkins closes Part III with a long-time-horizon argument that the value of intelligence lies in the knowledge it generates, that knowledge is substrate-independent, and that humanity's project ought to include preserving and transmitting that knowledge beyond Earth and beyond biological humans — a claim more philosophical than scientific, but one that frames the book's ambitions.

## 4. Methods

The book is a popular-science synthesis with no new empirical contribution. Its technical substrate is the Numenta research program — primarily Hawkins, Ahmad, Cui, Lewis (2017, *Frontiers in Neural Circuits*, "A theory of how columns in the neocortex enable learning the structure of the world") and follow-on papers culminating in the explicit Thousand Brains framework (Hawkins, Lewis, Klukas, Purdy, Ahmad 2019, "A framework for intelligence and cortical function based on grid cells in the neocortex"). Those papers describe HTM (Hierarchical Temporal Memory) and the column model in computational detail, with simulations showing that a single column augmented with grid-cell-like location signals can learn 3D objects from sensorimotor exploration, and that multi-column voting accelerates recognition.

The book itself proceeds in three parts:

- **Part I — A new understanding of the brain.** Chapters lay out Mountcastle's uniformity hypothesis, grid cells (Moser & Moser 2014 work in MEC), the reference-frame extension to the neocortex, columnar voting, and the extension of the framework to abstract concepts.
- **Part II — Machine intelligence.** Hawkins contrasts the Thousand Brains framework with deep learning, arguing for sensorimotor embodiment, reference frames, and continuous learning as required ingredients for AGI.
- **Part III — Human intelligence.** Speculations on AI risk, the future of intelligence as a substrate-independent property, and the long-term cultural project of preserving knowledge.

The technical commitments — column-as-complete-modeler, reference-frame binding, voting via L2/3 — are stated in the book but derived in the underlying Numenta papers, particularly the 2017 column paper, the 2019 framework paper, and the HTM technical reports on sparse distributed representations and sequence memory.

## 5. Results

The principal qualitative claims the book makes good on:

- **Reference-frame learning in a single column.** Numenta's column model learns 3D object representations from sensorimotor input. Simulated columns recognize objects (the canonical demos use small libraries of CAD-like 3D objects) more reliably and with fewer touches than feature-only baselines. The location signal is what allows partial sensory evidence to be unambiguously attached to a hypothesized object.
- **Voting accelerates and stabilizes recognition.** Multiple columns observing different parts of the same object converge on a shared identity faster than a single column alone — and recover from local ambiguity by drawing on globally consistent evidence. This is the operational form of the "thousand brains" idea.
- **The framework is consistent with cortical anatomy.** Layers 2/3 carry the long-range column-to-column projections used for voting; layers 5/6 carry the location / reference-frame information; layer 4 is the sensory input gateway. Hawkins is explicit that the framework is a hypothesis about *how* the canonical cortical microcircuit (Felleman & Van Essen 1991; Bastos et al. 2012) implements the algorithm.
- **Extension to abstract concepts.** Hawkins offers existence-proof arguments — not formal demonstrations — that the same machinery can support mathematical and linguistic concepts. The reference-frame primitive becomes a general "space" in which the concept is structured.

The book does not present new quantitative benchmarks beyond what the underlying Numenta papers report. It is more a *unification* of the existing Numenta work, plus a positioning of that work against deep learning and against existential-risk discourse, than a fresh empirical claim.

## 6. Critique / limitations

The strongest critique is *empirical*. Mountcastle's uniformity hypothesis is a *modeling commitment*, not a settled fact: cortical areas differ in cytoarchitecture, neurotransmitter densities, gene-expression profiles, and connectivity. Treating the column as the unit of a literally uniform algorithm requires absorbing those differences into "input and connectivity," which risks unfalsifiability. Many neuroscientists accept a *weak* form of uniformity (shared canonical microcircuit) without endorsing Hawkins's *strong* form (identical algorithm).

The framework's claim that each column learns *complete* object models is anatomically aggressive. The volume of synapses required to store a 3D model in a single cortical column is not obviously available, and the framework relies heavily on sparse distributed representations to claim the capacity is there. The empirical verification — for the column model, not the book — comes from HTM simulations, not from neural recordings showing object-identity coding in V1 columns.

The grid-cell-in-neocortex claim is the most controversial. There is good evidence for grid cells in entorhinal cortex (Hafting, Fyhn et al. 2005); the extrapolation to a generic location signal in every cortical column is theoretically appealing but empirically thin. Some evidence of object-vector cells and other reference-frame-like codes in cortex exists, but the strong reading — that L6 of every cortical column carries grid-cell-like activity — is not yet established.

The Part-II claims about deep learning are *qualitatively right but operationally vague*. The argument that DL lacks reference frames and embodiment is widely shared; what Hawkins does not provide is a concrete recipe for incorporating these into a scalable training setup competitive with the empirical successes of large transformers. The Numenta system has not, as of 2021, shown benchmark-competitive results on standard ML problems, which limits the persuasive force of the prescription.

The "old brain / new brain" framing for AI safety has been criticized as oversimplified. Critics (including those in the AI-safety community Hawkins addresses) argue that motivational drives in advanced AI systems will not respect the neuroanatomical separation that Hawkins relies on; goal-directedness can emerge from the optimization process itself, not only from a separate motivational module. Marcus and others critical of current LLMs ([marcus2025_llm_critique](research_db/papers/marcus2025_llm_critique.md)) are sympathetic to the diagnosis but tend to disagree about the cure: Hawkins's prescription is biologically specific (reference frames, sensorimotor loops, columns), Marcus's is more methodological (hybrid symbolic/neural). The two critiques converge on what is wrong with deep learning but diverge on what to do about it.

The book is popular science and elides technical detail. The book is best read together with the underlying Numenta papers; readers looking only at the book may be left with a clear architectural intuition but no usable mathematical or algorithmic specification. In particular, the *learning rule* by which a column acquires its 3D object models from sensorimotor data is stated informally; the corresponding Numenta papers use a specific HTM learning rule with sparse distributed representations, which is non-standard within mainstream ML and has not been shown to scale as gradient-based learning has.

Finally, Hawkins's framing is *cortex-centric* and *column-centric*. Subcortical contributions to behavior (basal ganglia, thalamus, cerebellum, brainstem) are bracketed into the "old brain." The user's program, which makes the cortico-basal-ganglia-thalamic loop ([cortico_basal_ganglia_thalamic_loops](research_db/concepts/cortico_basal_ganglia_thalamic_loops.md)) load-bearing for the RL hub, is more anatomically inclusive than Hawkins's framework.

## 7. Connection to our work

The Thousand Brains framework runs *strikingly parallel* to the user's architectural program; the connection is the load-bearing reason the entry is in this database.

**Many independent models contributing to a shared representation.** Hawkins's central architectural claim — that the cortex is not one model but thousands of partial, redundant models in conversation — is structurally the same commitment the user makes in `multi_hub_multi_objective_system`. The user's MSI hub, RL hub, VAE hub, and putative further hubs are functional analogues of Hawkins's cortical columns: each maintains its own internal state, builds its own (partial) model of the world, and contributes to a shared self-attention computation. The shared self-attention map is the user's analogue of Hawkins's L2/3 voting fabric: a bandwidth-limited, competitive bottleneck through which all the partial models must speak.

**Voting / competitive aggregation.** Hawkins describes voting as the mechanism by which agreeing columns reinforce one another and conflicting columns suppress one another, producing a stable percept. The user's competition-emergent-PC thesis ([competition_resource_competition](research_db/concepts/coalition_resource_competition.md)) is the same architectural commitment expressed in different vocabulary: hubs compete for control of the self-attention map by manipulating the inner-product space of Q and K; cooperating hubs reinforce one another's contribution, conflicting hubs suppress. The mathematical mechanism differs — Hawkins's voting is a column-to-column message-passing protocol, the user's is element-wise modulation of Q/K projections in a Feedback Transformer (`feedback_transformer`) — but the architectural commitment is the same: consensus across many partial models, mediated by a competitive bottleneck.

**Cortical column as a complete pattern-recognition unit.** Hawkins's column-is-complete-modeler claim is stronger than the user's hub-as-complete-modeler claim — the user's hubs are functionally specialized (MSI vs RL vs VAE), whereas Hawkins's columns are functionally identical and differ only in input. But both reject the canonical deep-learning picture in which intelligence is a feature-extraction stack culminating in a single decision head. Both insist on distributed, redundant, complete modelers.

**World-model emergence.** Hawkins's framework predicts that the *unified* world model — the thing the agent acts on — emerges from the conversation across columns, not from a separately-trained world model. This is precisely the prediction made by the user's empirical test plan for `world_model_emergence`: train hubs on conflicting objectives; afterwards train a separate decoder to predict the global internal state at $t+1$ from the global state at $t$; if iterative roll-out produces long-range coherent prediction, an emergent world model has arisen from competition. Hawkins's framework supplies a complementary theoretical reason to expect this: voting produces a globally consistent percept because that is the equilibrium of the column-voting dynamics, even though no column was individually trained to produce that percept.

**Reference frames vs. self-attention.** The one place where the frameworks differ substantively is the *substrate* of cross-column communication. Hawkins commits to explicit reference-frame coordinates carried by grid-cell-like neurons; the user commits to self-attention over patch tokens with feedback integration via the Feedback Transformer. These are not the same primitive. Hawkins's framework predicts that location signals are explicit and separable from feature signals; the user's framework predicts that location and feature are entangled in the patch-token representation, with positional encoding (`positional-encoding`) supplying weak prior structure. This is a falsifiable point of contact: a system built on Hawkins's framework should show separable location representations in deep recurrent layers; one built on the user's program should show entanglement modulated by attention.

**Connection to Schmidhuber, LeCun, and the broader AGI debate.** Hawkins 2021, Schmidhuber 2015 ([schmidhuber2015_learn_to_think](research_db/papers/schmidhuber2015_learn_to_think.md)), and LeCun 2022 ([lecun2022_path_to_agi](research_db/papers/lecun2022_path_to_agi.md)) form a triangle of position pieces from senior researchers about what intelligence requires beyond current deep learning. Schmidhuber emphasizes coupled RNNs (controller + predictive world model); LeCun emphasizes JEPA-style joint-embedding predictive architectures with hierarchical world models; Hawkins emphasizes columns with reference frames. The user's program inherits something from each: Schmidhuber's coupled-RNN framing motivates the multi-hub competition; LeCun's hierarchical world model motivates the multi-compartmental memory; Hawkins's columns motivate the architectural commitment to many partial modelers feeding a shared bottleneck. None of these three is sufficient on its own — but together they triangulate a research direction that the user's program operationalizes more concretely than any of the three.

**Implication for PRISM v2 and the recurrent ViT.** The Thousand Brains framework is a strong external endorsement of the multi-hub direction for PRISM v2 — it is independent evidence, from a different research community, that intelligence is best understood as a confederation of partial modelers. The recurrent ViT, with its single feedback source, is at the Hawkins-style "single column" end of the spectrum; PRISM v2 with its slow-fast memory ([PRISM_V2_PROPOSAL.md](Prism/docs/PRISM_V2_PROPOSAL.md) §3.3) is a two-column system; the full multi-hub system is the natural endpoint. A manuscript positioning the multi-hub system should cite Hawkins 2021 as the architectural precedent and explicitly contrast the user's self-attention bottleneck against Hawkins's L2/3 voting bottleneck.

## 8. Citations to follow

- `mountcastle1978_columnar_organization` — Mountcastle's original cortical-uniformity hypothesis; foundational for the framework.
- `hawkins2017_columns_neocortex` — Hawkins, Ahmad, Cui & Lewis, *Frontiers in Neural Circuits*; the technical column model that the book popularizes.
- `hawkins2019_thousand_brains_framework` — Hawkins, Lewis, Klukas, Purdy & Ahmad, *Frontiers in Neural Circuits*; the explicit Thousand Brains paper with simulations.
- `hafting2005_grid_cells` — Hafting, Fyhn et al., *Nature*; the discovery of grid cells in entorhinal cortex that the framework extrapolates to neocortex.
- `moser_moser2008_grid_cells_review` — Edvard and May-Britt Moser's reviews of the grid-cell system.
- `mountcastle1957_modality_columnar` — Mountcastle's original single-unit evidence for columnar organization in somatosensory cortex.
- `felleman_vanessen1991_hierarchical_cortex` — in seed; the canonical hierarchy on which Hawkins's framework sits.
- `bastos2012_canonical_microcircuits` — in seed; the canonical microcircuit Hawkins maps the column algorithm onto.
- `weiler2025_l6_corticocortical` — L6 corticocortical neurons (already In seed, full depth for user's program); these are the candidate substrate for Hawkins's location signal.
