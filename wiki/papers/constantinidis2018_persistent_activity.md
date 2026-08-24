---
id: constantinidis2018_persistent_activity
title: "Persistent spiking activity underlies working memory"
authors:
  - "Constantinidis, Christos"
  - "Funahashi, Shintaro"
  - "Lee, Daeyeol"
  - "Murray, John D."
  - "Qi, Xue-Lian"
  - "Wang, Min"
  - "Arnsten, Amy F. T."
year: 2018
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.2486-17.2018"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.2486-17.2018"
tags:
  - primate-neurophysiology
  - prefrontal-cortex
  - working-memory
  - review
concepts:
  - working-memory-persistent-activity
  - slow-fast-recurrence
  - multi-compartmental-memory
related:
  - funahashi1989_mnemonic_dlpfc
  - goldman_rakic1995_cellular_wm
  - mante2013_context_dependent_pfc
  - masse2019_circuit_wm
  - vijayraghavan_everling2021_muscarinic_wm
  - wang2025_hierarchical_reasoning_model
  - attwell_laughlin2001_brain_energy_budget
  - laughlin1998_metabolic_cost
relevance_to:
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
  - prism_v2_proposal
status: full
depth: full
last_updated: "2026-05-16"
---

# Persistent spiking activity underlies working memory

> **Format note.** This was published as a "Dual Perspectives" paper in *J Neurosci* — the Constantinidis et al. position is paired with a counterpoint from Lundqvist, Herman & Miller (PMID 30089640) titled "Working Memory: Delay Activity, Yes! Persistent Activity? Maybe Not." Both should be read together; this entry treats the Constantinidis et al. position as the primary claim and references the counterpoint in §6.

## 1. Abstract

Persistent activity generated in the PFC during the delay period of working memory tasks represents information about stimuli held in memory and determines working memory performance. The authors argue that alternative models of working memory — those depending on rhythmic / oscillatory discharges or relying exclusively on short-term synaptic plasticity — are inconsistent with the neurophysiological data. Their position: stimulus-selective persistent firing of PFC neurons during the delay period is the substrate of working memory.

## 2. Why this matters for us

Constantinidis et al. 2018 is the canonical contemporary defense of *persistent activity* as the WM substrate. It establishes the empirical phenomenon that PRISM v2's slow memory ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) is the computational analog of: a representation that is maintained over many timesteps without being overwritten by new input. The user's commitment to multi-compartmental memory ([multi_compartmental_memory](research_db/concepts/multi_compartmental_memory.md)) and slow-fast recurrence ([slow_fast_recurrence](research_db/concepts/slow_fast_recurrence.md)) is grounded in this empirical phenomenon: real PFC neurons maintain stimulus-selective activity for seconds; the slow memory in PRISM v2 is the AI analog.

## 3. Key claims

1. PFC neurons exhibit *stimulus-selective persistent activity* during the delay period of working memory tasks — sustained firing rates that encode the specific stimulus held in memory.
2. The persistent activity is *causally* linked to working memory performance: trials with stronger persistent activity yield better memory retrieval; lesions or pharmacological manipulations that reduce persistent activity impair WM behavior.
3. The persistent activity is *generated in PFC* (and other association cortices), not inherited from sensory cortex. The persistence is the result of local recurrent network dynamics, supported by NMDA-receptor-dependent excitatory drive.
4. Alternative models that propose *no* persistent activity (with WM stored in short-term synaptic plasticity, or only in transient activity bursts) are inconsistent with the bulk of the neurophysiological data. The authors argue these models are based on subset of trials and underestimate the population-level persistence.
5. The persistent-activity hypothesis is consistent with the bump-attractor and line-attractor classes of recurrent-network models (Wang 1999; Compte et al. 2000), in which the network sustains itself in a marginally-stable attractor state.
6. The persistent activity is *modulated* by attention, reward, task demands, and cognitive load. It is not a fixed signal but is dynamically regulated by ongoing cognition.

## 4. Methods

This is a position paper, not a primary experimental study. The authors synthesize decades of single-unit recording data from macaque PFC during WM tasks. The principal data sources are Funahashi, Bruce & Goldman-Rakic 1989 ([funahashi1989_mnemonic_dlpfc](research_db/papers/funahashi1989_mnemonic_dlpfc.md)), Goldman-Rakic 1995 ([goldman_rakic1995_cellular_wm](research_db/papers/goldman_rakic1995_cellular_wm.md)), and many subsequent studies. The authors discuss the empirical support for persistent activity, address methodological critiques (single-trial vs trial-averaged analysis, sparse vs dense firing patterns), and argue for the persistence hypothesis.

The Lundqvist et al. counterpoint paper (PMID 30089640) re-analyzes the same data with single-trial methods and argues that the "persistent" activity is actually composed of *sparse transient bursts* — at any given moment, only a small subset of WM-encoding neurons are active, but the population as a whole maintains the representation. The two positions are not strictly mutually exclusive but disagree on what the right level of description is.

## 5. Results

The principal empirical claims the review consolidates:

- **Stimulus-selective delay activity.** Macaque dlPFC neurons show sustained firing-rate differences (lasting seconds) that encode specific stimuli held in WM. The selectivity is robust across many tasks and labs.
- **Causal role.** Inactivation of PFC or pharmacological blockade of NMDA receptors (which support the persistent firing) impairs WM behavior. Cooling or microstimulation of dlPFC disrupts trial-by-trial WM accuracy.
- **Population-level persistence.** Even if single neurons show variable, sparse firing, the *population* representation is decodable continuously across the delay period. The continuity at the population level is the right level of description for "persistent activity."
- **NMDA-receptor dependence.** The persistent activity is selectively sensitive to NMDA-receptor antagonists, supporting the model that recurrent excitatory dynamics sustained by slow NMDA receptors generate the persistence.
- **Attention and task-demand modulation.** Persistent activity strength scales with attention and task demands. This is consistent with the precision-weighting framework (Feldman & Friston 2010): attention sets the precision on the WM channel.
- **Dopamine modulation.** D1 receptor activation enhances PFC persistent activity (within an optimal range); too little or too much D1 stimulation impairs it. This is the substrate of the "inverted-U" relationship between dopamine and WM performance.

## 6. Critique / limitations

The Lundqvist et al. counterpoint (PMID 30089640) argues that:
- Trial-averaged analyses obscure transient burst patterns at the single-trial level.
- The persistence may be sparse and transient at any moment in time, with the population-level representation maintained by a *rotating subset* of neurons.
- This pattern has different computational implications than steady-state persistent firing — it suggests a role for transient burst events and possibly gamma-band oscillations.

The Constantinidis et al. response is that single-trial sparseness does not contradict the persistent-activity hypothesis at the population level. Both positions accept that the *population* sustains the representation; they disagree on the appropriate single-cell level of description.

The hypothesis is primarily a description of dlPFC working memory. Whether the same mechanism generalizes to other cortical areas and other forms of memory (e.g., sensory short-term memory, motor planning) is empirically open. Stokes et al. 2013 and subsequent work argue for *activity-silent* WM in some contexts — memories stored in synaptic weights rather than firing — which would be a complementary rather than competing substrate.

The persistent-activity framework is silent on *why* this specific implementation. Why would the brain maintain WM via metabolically expensive persistent firing rather than via cheap synaptic storage? Laughlin & Attwell metabolic-budget considerations ([laughlin1998_metabolic_cost](research_db/papers/laughlin1998_metabolic_cost.md), [attwell_laughlin2001_brain_energy_budget](research_db/papers/attwell_laughlin2001_brain_energy_budget.md)) make this an interesting question — persistent firing is expensive, so it should only be used when synaptic storage is inadequate. The paper doesn't address this metabolic argument.

The framework treats WM as a separate function from selective attention. Recent work (Awh & Vogel 2008; Olivers 2011; Panichello & Buschman 2021) increasingly treats WM and attention as a single shared-substrate phenomenon. The Constantinidis et al. paper does not engage with this unification.

## 7. Connection to our work

This paper supports the architectural commitment to *slow* memory states that are maintained over many timesteps:

**PRISM v2's slow memory $M^{\text{slow}}$.** PRISM v2 commits to a slow memory ([PrismV2/docs/PRISM_V2_PROPOSAL.md](PrismV2/docs/PRISM_V2_PROPOSAL.md) §3.3) updated rarely (per-step probability ~0.05 via gate-bias $b_u^{\text{slow}} = -3$). This is the computational analog of PFC persistent activity: a representation that is maintained over many timesteps and modulates downstream processing. Constantinidis et al. is the canonical citation for the biological phenomenon this is modeled on.

**Working-memory-persistent-activity as a load-bearing concept.** The taxonomy concept `working-memory-persistent-activity` is grounded in this paper plus Funahashi 1989 and Goldman-Rakic 1995. The user's program treats this as a *first-class* memory mechanism — not just one option among many but the default architectural commitment.

**The slow-fast recurrence framework.** The user's commitment to slow-fast recurrence ([slow_fast_recurrence](research_db/concepts/slow_fast_recurrence.md)) is in part justified by the empirical timescale separation between PFC slow dynamics (Constantinidis 2018) and earlier cortical fast dynamics (Buzsáki & Wang 2012). The slow module of HRM ([wang2025_hierarchical_reasoning_model](research_db/papers/wang2025_hierarchical_reasoning_model.md)) and PRISM v2's slow memory are both motivated by this empirical pattern.

**Multi-compartmental memory.** The user's program commits to multiple memory compartments running at different timescales ([multi_compartmental_memory](research_db/concepts/multi_compartmental_memory.md)). The slow compartments are the analog of PFC persistent-activity neurons; fast compartments are the analog of earlier-cortex transient-response neurons. Constantinidis et al. is the citation for the slow compartments.

**The Lundqvist counterpoint as architectural guidance.** The counterpoint paper's argument that single-trial activity is sparse and transient is relevant to the user's program too: PRISM v2's slow memory state could be implemented as either (a) a steady-state representation (Constantinidis position) or (b) a sequence of sparse, transient burst updates with a population-level persistence (Lundqvist position). The current PRISM v2 design is closer to (a), but the (b) variant is worth exploring, especially in conjunction with HRM-style hierarchical convergence ([hierarchical_convergence](research_db/concepts/slow_fast_recurrence.md) taxonomy concept) where the L module reaches local equilibria interspersed with H module updates.

## 8. Citations to follow

- `lundqvist_herman_miller2018_counterpoint` — the Lundqvist counterpoint position (PMID 30089640). *Should be added to seed.*
- `funahashi1989_mnemonic_dlpfc` — classic PFC persistent activity. In seed.
- `goldman_rakic1995_cellular_wm` — cellular basis of WM. In seed.
- `compte2000_bump_attractor` — bump-attractor model of WM. Not in seed.
- `wang1999_nmda_bistability` — NMDA-receptor model of persistent activity. Not in seed.
- `mante2013_context_dependent_pfc` — recurrent dynamics in PFC. In seed, full depth.
- `masse2019_circuit_wm` — modern circuit model of WM. In seed.
- `stokes2013_activity_silent_wm` — activity-silent WM. Not in seed.
- `vijayraghavan_everling2021_muscarinic_wm` — muscarinic neuromodulation of WM persistent activity. In seed.
