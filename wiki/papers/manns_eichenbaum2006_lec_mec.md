---
id: manns_eichenbaum2006_lec_mec
title: "Evolution of declarative memory"
authors:
  - "Manns, Joseph R."
  - "Eichenbaum, Howard"
year: 2006
venue: "Hippocampus"
doi: "10.1002/hipo.20205"
arxiv: ""
url: "https://onlinelibrary.wiley.com/doi/10.1002/hipo.20205"
tags:
  - primate-neurophysiology
  - cortical-anatomy
  - review
concepts:
  - lec-mec-factorization
  - factorized-representations
  - feature-binding
  - bidirectional-hierarchical-feedback
  - multi-compartmental-memory
related:
  - higgins2017_factorized_representations
  - choi2023_msi_review
  - senkowski_engel2024_multi_timescale_msi
relevance_to:
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Evolution of declarative memory

## 1. Abstract

The review considers research on the hippocampus and related parahippocampal areas in humans and experimental animals and advances three main points. First, many of the anatomical details of the hippocampus and the adjacent cortical areas of the parahippocampal region are conserved across mammals. Second, the functional role of these areas in declarative memory is also conserved across species. Third, an evolutionary approach is key to understanding how local circuitry of the hippocampus and parahippocampal region supports declarative memory. The authors propose a schematic model in which two separate streams of information converge on the hippocampus: a spatial-context stream arriving via the postrhinal cortex (parahippocampal cortex in primates) and the medial entorhinal area (MEC), and a nonspatial item stream arriving via the perirhinal cortex and the lateral entorhinal area (LEC). The underlying local-circuit computations integrate these streams into item-in-context representations that are taken to underlie episodic memory in humans and spatial memory in animals.

(Source: PubMed PMID 16881079, full abstract retrieved via NCBI eutils on 2026-05-15; published in *Hippocampus* 16(9):795–808, DOI 10.1002/hipo.20205. The paraphrase above tracks the published abstract closely.)

## 2. Why this matters for us

The Manns–Eichenbaum scheme is the canonical mammalian biological precedent for *architecturally enforced factorization* of memory: two anatomically distinct cortical input streams (one for the *what*, one for the *where*) maintain their identities through cortex, project into structurally distinct entorhinal subdivisions (LEC vs MEC), and only converge inside the hippocampus where item-in-context binding occurs. This maps onto the user's commitment, in PRISM v2 and the multi-hub program (see `threads/the_user_architectural_program.md` §3, §5), to maintain *multiple recurrent compartments* with distinct content roles — in particular a multi-sensory-integration (MSI) hub holding item / featural information and a slow-memory or world-model hub holding spatial / contextual information — rather than collapsing both into a single recurrent state. The biology supplies an existence proof that explicit anatomical factorization, not just statistical disentanglement at the read-out, is the strategy a mammalian brain actually uses for declarative memory.

The paper is also one of two anchors (with Higgins et al. 2017) for the `factorized-representations` concept node in this database's taxonomy, and the sole anchor for `lec-mec-factorization`. It supplies the *neuroscience* half of the case for factorization; Higgins et al. supplies the *machine-learning* half. Together they establish that the architectural commitment is neither idiosyncratic nor unmotivated.

## 3. Key claims

1. The internal anatomy of the hippocampus (DG, CA3, CA1, subiculum) and the parahippocampal region (perirhinal, postrhinal/parahippocampal, lateral and medial entorhinal areas) is conserved across mammals to a degree that supports a single functional template.
2. The functional role of these structures in declarative memory — defined by the authors as flexible, relational memory for items embedded in contexts — is similarly conserved across rodents, non-human primates, and humans, despite surface differences in task ecology (spatial mazes vs episodic verbal recall).
3. Two anatomically segregated cortical streams supply qualitatively different information to the hippocampus: a *spatial / contextual* stream through postrhinal cortex → medial entorhinal area (MEC), and a *nonspatial / item* stream through perirhinal cortex → lateral entorhinal area (LEC).
4. The hippocampus is the first stage at which these two streams are obligatorily combined; its computational role is therefore *item-in-context binding*, with downstream consequences for episodic recall, novelty detection, and flexible behavioral guidance.
5. Apparent species-specific specializations (rodent place cells, primate object-trace cells, human episodic recall) are surface manifestations of the same item-in-context circuit operating over species-appropriate inputs.
6. Episodic memory in humans and spatial memory in animals are not different computations on different substrates but the *same* item-in-context computation operating in different ecological regimes — verbal-narrative items embedded in temporal contexts for humans, spatial-foraging items embedded in environmental contexts for rodents.
7. The evolutionary stability of this circuit reflects a deep computational requirement (relational binding of separable factors), not historical contingency; convergent and conserved features should be expected wherever the same task pressures recur.

## 4. Methods

This is a synthetic review rather than a primary report. The methods amount to (a) a comparative anatomical synthesis across rodent, carnivore, non-human primate, and human studies of the hippocampal formation and parahippocampal region, drawing on tract-tracing, cytoarchitecture, and lesion literatures; (b) a comparative functional synthesis across single-unit electrophysiology in rodents and primates, lesion and inactivation studies in animals, and neuropsychological / neuroimaging findings in humans; and (c) the articulation of a schematic two-stream convergence model — perirhinal/LEC carrying nonspatial item information and postrhinal/MEC carrying spatial context — that the authors argue best accommodates the comparative data. No new statistical analyses are introduced; the contribution is a unifying framework over prior empirical work.

The anatomical scaffold rests on the well-characterized cortical inputs to entorhinal cortex: visual and visuospatial cortical areas (including retrosplenial cortex) project preferentially to postrhinal / parahippocampal cortex and onward to MEC, while polymodal association cortices encoding object and item information project preferentially to perirhinal cortex and onward to LEC. The trisynaptic pathway (entorhinal cortex → dentate gyrus → CA3 → CA1) then provides the canonical convergence substrate, with direct entorhinal projections to CA1 and CA3 supplying an additional, monosynaptic route. The review's diagrammatic model is essentially a coarse box-and-arrow rendering of this anatomy, with arrows labeled by the *kind* of information each pathway is hypothesized to carry rather than by any quantitative connectivity weight.

## 5. Results

Because this is a review, "results" should be read as the empirical regularities the authors marshal in support of the model. They argue that:

- The cytoarchitectonic and connectional plan of the parahippocampal region is recognizable across mammals studied to date, with homologous perirhinal, postrhinal/parahippocampal, and entorhinal subdivisions identifiable in rodent, carnivore, and primate.
- Single-unit recordings in rodent LEC reveal weak spatial tuning but selectivity for objects and odors, whereas MEC contains the now-canonical grid cells, head-direction cells, and border cells that code for spatial location and heading.
- Perirhinal lesions in rodents and primates impair object-recognition and item-familiarity judgments while sparing spatial navigation; postrhinal/parahippocampal lesions show the converse profile.
- Hippocampal lesions disrupt the *combination* of these inputs — item-in-context tasks (object-place associations, episodic recall, contextual fear) are reliably impaired, while either component alone may survive.
- Human neuroimaging is consistent: parahippocampal cortex activates for scene and spatial-context processing, perirhinal cortex for item and familiarity processing, and the hippocampus for relational binding.

The review supplies no new numbers; its quantitative force lies in the breadth of the comparative evidence it integrates rather than in any single effect size.

Two specific empirical regularities are worth highlighting because they bear most directly on the architectural argument. First, the rodent single-unit dissociation between LEC and MEC reported by Hargreaves and colleagues (cited approvingly in the review) shows that the *same population* of neurons in MEC carries strong spatial-rate-coded information about position in an environment, while neurons in LEC show weak spatial modulation and instead encode the presence and identity of objects within that environment. This is a circuit-level instance of factorized representation, not merely a behavioral dissociation across lesion groups. Second, hippocampal CA1 and CA3 neurons reliably show conjunctive coding for item-in-place — firing for a particular object only in a particular location — that is *not* observed at the same intensity in either entorhinal subdivision in isolation, evidence that the convergence is informative and not merely additive.

A third empirical thread the review weaves in is the developmental and comparative consistency of the lesion phenotype. Selective hippocampal damage in human amnesic patients (the canonical H.M. and R.B. cases, and the more anatomically precise patients reviewed by Squire and colleagues) produces a deficit in item-in-context recall while sparing item familiarity and gist; lesions restricted to perirhinal cortex in non-human primates produce the converse profile (impaired object recognition, spared spatial memory); lesions of the postrhinal cortex in rats produce yet a third profile (impaired spatial-context learning, spared object recognition). The cross-species coherence of this three-way dissociation is the strongest single piece of evidence the review marshals.

A fourth thread, more directly architectural, is the *direction* of information flow. The review emphasizes that the perirhinal–LEC and postrhinal–MEC streams are not parallel copies of the same input filtered through different anatomy; they receive *different* cortical inputs (object-coding ventral-stream cortex into perirhinal; scene-coding retrosplenial / parietal cortex into postrhinal) and produce *different* downstream activations. The factorization is therefore inherited from upstream cortical specialization, not constructed de novo at the entorhinal stage. For our purposes, this means the architectural analog is not an unsupervised disentanglement objective applied to a single sensory stream, but a *commitment to keep separate streams separate* through the depth of the architecture — exactly what the multi-hub design enforces.

## 6. Critique / limitations

The factorization is cleaner in cartoon than in cortex. Subsequent work (e.g., reports of object-vector cells in MEC, social- and time-coding cells in LEC) has complicated the strict spatial-vs-nonspatial dichotomy: LEC carries time and event-structure information beyond pure items, and MEC carries more than pure metric space. The two-stream story should be read as a *first-order* anatomical-functional dissociation rather than a strict factorization. A second limitation is that the review's "evolutionary" framing is largely comparative-anatomical; it does not engage phylogenetic-comparative methods or quantitative homology arguments, and so the claim that the circuit is functionally conserved rests on convergent lesion / recording phenomenology rather than on an explicit evolutionary model. Third, the model is silent on the *learning rules* by which item and context streams come to converge appropriately in CA3 / CA1 — a gap that later work on theta-paced encoding (e.g., the authors' own subsequent Neurobiology of Learning and Memory 2007 paper) attempts to fill. Fourth, the review predates the modern understanding of grid cells as a population code with explicit factorization-into-modules properties, and so its treatment of MEC's representational geometry is necessarily coarse.

A fifth, methodological limitation worth flagging for our purposes is the *granularity mismatch* between the box-and-arrow model and the underlying single-unit data. The review treats LEC and MEC as if each were a single homogeneous population, but each subdivision has well-documented superficial (layer II) vs deep (layer V/VI) laminar dissociations, and the layer II reuniens / island vs ocean cell distinction in MEC has substantial functional consequences. The two-stream summary, while useful, abstracts over real heterogeneity that any neurally realistic computational model would have to confront.

A sixth caveat is the directionality assumption. The review treats LEC and MEC primarily as *inputs* to the hippocampus, with their content essentially set by upstream cortical projections. Subsequent work has documented strong hippocampus-to-entorhinal feedback via deep entorhinal layers, raising the possibility that LEC and MEC are themselves *recurrent participants* in the loop rather than mere relay stations. For the user's architecture this is, if anything, encouraging: it means the biological precedent supports bidirectional rather than feedforward inter-hub communication, consistent with the Feedback Transformer's commitment to Q/K/V exchange in both directions.

Finally, the review predates two important computational developments that have since reshaped the conversation: (a) the Tolman-Eichenbaum Machine (Whittington et al. 2020), which makes the LEC/MEC factorization computationally explicit as factorized embeddings bound by hippocampal indices; and (b) successor-representation accounts of hippocampal coding, which reinterpret MEC's spatial signal as a temporal-difference-discounted state representation rather than a metric map. Both developments are friendly to the Manns–Eichenbaum framework but expose it as a *structural diagram* awaiting a computational instantiation. The user's program, in offering a concrete neural-network instantiation of multi-stream-then-convergence, is itself one such candidate computational instantiation.

## 7. Connection to our work

The Manns–Eichenbaum scheme is one of the load-bearing biological references for the user's commitment to *factorized representations across distinct memory compartments*, articulated in `threads/the_user_architectural_program.md` §3 (multi-compartmental, hierarchical, bidirectionally-connected memory) and §5 (multi-hub multi-objective system). Three connections are specific enough to be worth pinning down.

First, the **MSI / slow-memory split parallels the LEC / MEC split**. The user's MSI hub (see `threads/the_user_architectural_program.md` §5 and `concepts/multi_hub_multi_objective_system.md`) is responsible for fast featural integration across modalities — the architectural homolog of the perirhinal → LEC item / nonspatial pathway. The user's slow-memory or world-model hub holds longer-timescale contextual representations — the architectural homolog of the postrhinal → MEC spatial-context pathway. The hippocampus's role as the obligatory convergence stage maps onto the user's central feedback-transformer attention module (see `concepts/feedback_transformer.md` referenced in the thread), where the two hubs' Q/K/V contributions are bound element-wise before softmax. The biological precedent is not that the modules are merely *learnable in principle* but that nature found an architectural solution in which the factorization is *enforced anatomically*, supplying a strong inductive bias that no end-to-end statistical objective is asked to discover from scratch.

Second, the dual-stream structure supplies a **biologically grounded answer to "why two memory compartments rather than one"** that supplements the dual-timescale Mujika–Tallec story cited in PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.3). The Mujika–Tallec argument is essentially about gradient flow and credit assignment over time. The Manns–Eichenbaum argument is about *content type*: items and contexts have different statistical structure (high-frequency, identity-coded vs low-frequency, place-coded), benefit from different representational geometries, and only need to be bound at the moment of episodic encoding. Both arguments motivate dual-compartment memory; together they motivate dual compartments that differ *both* in timescale *and* in content role.

Third, the convergence-only-at-the-hippocampus design pattern licenses the user's commitment to **late, attention-mediated binding** rather than early concatenation of hub states. In the user's architecture (see thread §1, the Feedback Transformer), hub memories are kept separate and broadcast into the central attention computation via element-wise Hadamard products on Q and K, never via state concatenation. The Manns–Eichenbaum diagram is essentially the same: LEC and MEC outputs remain separate through their entorhinal stations and converge only via the hippocampal trisynaptic loop. This is the biological analog of the user's architectural rule that hubs interact through Q/K modulation rather than through input concatenation, and it is the section of the literature most directly anchoring that rule.

Concretely, this maps to a design rule the user could enforce in PRISM v2 and any descendant of the multi-hub system: hub states should be projected into the central attention layer via their own Q/K/V heads (one set per hub), and the *only* combination operation prior to softmax should be the element-wise Hadamard product specified in the Feedback Transformer equations (see thread §1). Concatenation, summation prior to projection, or shared Q/K/V heads across hubs would all amount to "mixing the streams before the hippocampus" and would erase the architectural factorization that the Manns–Eichenbaum scheme indicates is biologically load-bearing.

A counterweight: the post-2006 literature has muddied the strict LEC-spatial / MEC-nonspatial dichotomy (see §6). This complicates but does not vacate the connection — it actually strengthens the case that the user's hubs need not be cleanly "sensory" vs "spatial" either, only architecturally distinct compartments whose roles emerge from their inputs and objectives.

A fourth, more speculative connection bears on the *iterative variational encoder–decoder* of §4 of the thread. Hippocampal pattern completion in CA3 — the canonical attractor-network reading of recurrent hippocampal dynamics — is the biological analog of the iterative forward-reasoning loop the user proposes, in which the encoder is shown the same input repeatedly and the latent state evolves toward an attractor. The factorized LEC / MEC inputs are then the analog of the user's structured guide state $\tilde H_0$, whose factorization is enforced by an architectural commitment (matrix-normal latent with row-covariance penalty) rather than learned from scratch. The biological precedent is that the system that *most successfully* implements iterative attractor-completion in nature does so over inputs that are already factorized at the level of cortical anatomy, not over an unstructured high-dimensional sensory blob.

A fifth connection is to the **competition-emergent predictive coding** thesis of §5 of the thread. The LEC and MEC populations are precisely the kind of rival coalitions the user's theoretical argument requires: they share downstream readout bandwidth (the hippocampus's finite capacity for binding), they have distinct objective signals (item-recognition vs spatial-navigation behavior), and they must coordinate without either overwriting the other's representation. The fact that the brain solves this coordination problem with *anatomical separation up to the convergence stage* rather than with within-stream gating supports the user's architectural rule that hub-level competition should be implemented at the attention layer (where Q/K contributions arbitrate) rather than at the input layer (where contributions would merely sum). The biological precedent is that competing coalitions stay *physically distinct* up to the latest possible binding stage, and the user's architecture follows the same rule.

A sixth, more cautionary, connection points back to the database's reading order. The thread (§7) prioritizes papers on multi-compartmental memory and bidirectional hierarchical feedback. The Manns–Eichenbaum entry should be read as supplying the *content-factorization* dimension that those other papers do not — Mujika–Tallec covers timescale factorization, Sherman's CTC review covers cortico-thalamo-cortical loop factorization, but only the LEC/MEC story covers factorization along the spatial-vs-nonspatial axis. The combination of all three is what the multi-hub system aims to instantiate.

Finally, an evaluation hook: if the user's program produces a multi-hub system trained on a sufficiently rich item-in-context task (a memory-augmented video task with both object-identity and scene-context structure, for instance), one would expect — by the biological analogy — that the MSI hub and the slow-memory hub spontaneously specialize along an item/context axis even without an explicit factorization loss. A direct empirical test would be to apply a linear decoder for object identity and a separate linear decoder for spatial context to each hub's representation and report the decoding accuracy. The Manns–Eichenbaum prediction is that decoding accuracy will be dissociated — high object-identity decoding from the MSI hub and high spatial-context decoding from the slow-memory hub — with poor performance on the swapped pairings. This is a falsifiable, directly testable empirical commitment that this paper's biology underwrites.

The pattern of overlap between the user's architecture and the Manns–Eichenbaum diagram is striking enough to bear summary. The user has *MSI / slow-memory / world-model* hubs where biology has *LEC / MEC / hippocampus*; the user has *Feedback Transformer Q/K/V exchange* where biology has *hippocampal trisynaptic convergence*; the user has *bidirectional ascending/descending projections* where biology has *deep-entorhinal feedback to neocortex*. The mapping is structural rather than literal — there is no claim that the user's MSI hub is anatomically a model of LEC — but the architectural design pattern is the same, and the biology supplies an existence proof that such a design is sufficient for the kind of relational item-in-context computation declarative memory requires.

## 8. Citations to follow

- hasselmo2005_theta_encoding_retrieval — Hasselmo's theta-phase model of LEC/MEC routing, candidate for explaining *when* the two streams are read into the hippocampus.
- hargreaves2005_lec_mec_dissociation — Hargreaves, Rao, Lee & Knierim, the foundational rodent single-unit dissociation of LEC (weakly spatial) vs MEC (grid cells).
- knierim2014_functional_correlates_lec_mec — Knierim, Neunuebel & Deshmukh comparative review, extends and complicates the strict dichotomy.
- tsao2018_integrating_time_lec — Tsao et al. (Nature) on time coding in LEC, directly relevant to the §6 critique that LEC is not purely "item".
- hafting2005_grid_cells — the foundational MEC grid-cell paper, currently absent from this database.
- okeefe_dostrovsky1971_place_cells — the foundational hippocampal place-cell paper, anchoring the spatial side of declarative memory.
- squire_zola1996_declarative_memory — the canonical declarative-memory framework the review extends to a circuit-level model.
- ranganath_ritchey2012_two_cortical_systems — extends the perirhinal/LEC vs parahippocampal/MEC dissociation to a posterior medial / anterior temporal system framework in humans.
- whittington2020_tem — the Tolman-Eichenbaum Machine, a computational model that operationalizes exactly the LEC/MEC factorization as factorized embeddings bound by hippocampal indices; directly relevant to the user's architectural program.
- eichenbaum_yonelinas_ranganath2007_mtl_memory — comprehensive review extending the present model's circuit picture to a full medial-temporal-lobe theory of memory.
- deshmukh_knierim2011_lec_objects — direct rodent single-unit demonstration of object-coding in LEC, the empirical pillar of the "item" half of the factorization.
- diehl2017_grid_modules — population-level evidence that MEC grid cells are organized into discrete modules with distinct spatial scales, a finer-grained factorization within the spatial stream that the review's coarse "MEC = space" label elides.
- van_strien_cappaert_witter2009_anatomy_review — detailed quantitative review of hippocampal–parahippocampal connectivity, the anatomical reference standard underlying the box-and-arrow diagrams of Manns & Eichenbaum.
- stachenfeld2017_successor_representation — proposes MEC encodes a predictive successor representation, recasting the spatial side of the factorization as a temporal-difference signal and tightening the bridge to RL-style world models.
