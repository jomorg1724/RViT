---
id: desposito_postle2015_wm_neuroscience
title: "The Cognitive Neuroscience of Working Memory"
authors:
  - "D'Esposito, Mark"
  - "Postle, Bradley R."
year: 2015
venue: "Annual Review of Psychology"
doi: "10.1146/annurev-psych-010814-015031"
arxiv: ""
url: "https://www.annualreviews.org/doi/10.1146/annurev-psych-010814-015031"
tags:
  - working-memory
  - prefrontal-cortex
  - delay-activity
  - mvpa
  - cognitive-control
  - review
concepts:
  - multi_compartmental_memory
  - cortico-basal-ganglia-thalamic-loops
  - top-down-feedback
  - error-gated-update
related:
  - baddeley_hitch1974_working_memory
  - postle2006_wm_emergent
  - stokes2015_activity_silent_wm
  - christophel2017_distributed_wm
  - sreenivasan_desposito2019_delay_activity
  - constantinidis2018_persistent_activity
  - panichello_buschman2021_shared_mechanisms
  - mcnab_klingberg2008_pfc_bg_wm
  - lisman_grace2005_hippocampal_vta
relevance_to:
  - prism_v1
  - prism_v2
  - rvit_plus
seed_source:
  - manual_deep_dive_2026_05_23
status: full
depth: full
last_updated: "2026-05-23"
---

# The Cognitive Neuroscience of Working Memory

## 1. Abstract

> "For more than 50 years, psychologists and neuroscientists have recognized the importance of a working memory to coordinate processing when multiple goals are active and to guide behavior with information that is not present in the immediate environment. In recent years, psychological theory and cognitive neuroscience data have converged on the idea that information is encoded into working memory by allocating attention to internal representations, whether semantic long-term memory (e.g., letters, digits, words), sensory, or motoric. Thus, information-based multivariate analyses of human functional MRI data typically find evidence for the temporary representation of stimuli in regions that also process this information in nonworking memory contexts. The prefrontal cortex (PFC), on the other hand, exerts control over behavior by biasing the salience of mnemonic representations and adjudicating among competing, context-dependent rules. The 'control of the controller' emerges from a complex interplay between PFC and striatal circuits and ascending dopaminergic neuromodulatory signals." (D'Esposito & Postle 2015, *Annu. Rev. Psychol.* 66:115-142, abstract.)

## 2. Why this matters for us

D'Esposito & Postle 2015 is the canonical *modern* synthesis of working-memory neuroscience, and it states the field's prevailing position cleanly: WM is not a dedicated buffer, it is *attention applied to internal representations*. This is the load-bearing biological warrant for the user's program-level claim that memory and attention are not separable architectural components — they share substrate. Every aspect of the user's architecture that conflates memory-state maintenance with attentional control — the Feedback Transformer's central attention as both memory-update gate and inter-hub arbiter, the recurrent ViT's attention-driven memory update, PRISM v2's gated-by-attention memory write — has its biological warrant here. The review also crystallizes the *content/control* dissociation: WM contents reside in domain-specific posterior cortex (sensory recruitment), while PFC supplies the *control* (gating, biasing, rule selection) over those contents. This maps directly onto the user's architectural split between *hub-internal* recurrent memory (the content) and the *central attention substrate* (the control).

## 3. Key claims

1. WM is best understood as attention directed to internal representations rather than a dedicated storage system — the "emergent property" view (Postle 2006) is now the field's default.
2. Storage and processing emerge from the same cortical regions that perform domain-specific perception/action — the *sensorimotor recruitment* hypothesis.
3. MVPA of fMRI data localizes mnemonic content to sensory/posterior regions, not PFC, during delay periods — early visual cortex through parietal stores orientation, color, motion content even when univariate BOLD returns to baseline.
4. PFC's role is *cognitive control* — biasing, gating, and selecting representations — not maintaining the contents.
5. Persistent delay-period firing is not synonymous with WM storage and may instead reflect attention, control, or response preparation.
6. Striato-cortical loops gated by dopamine implement *updating* and *protection* of WM contents — the classic Frank/O'Reilly working-memory-as-gating model.
7. Damage to PFC produces deficits primarily in *control* aspects of WM (manipulation, interference resolution), not basic storage of small loads.
8. The PFC's contribution can itself be modulated — the "control of the controller" — by ascending dopaminergic signals and by striato-pallido-thalamic loops, putting PFC in a recursive arbitration position.

## 4. Methods

This is a narrative review synthesizing single-unit electrophysiology (primate dorsolateral PFC delay tasks from Funahashi, Goldman-Rakic, Miller, Constantinidis), human lesion neuropsychology, neuroimaging (univariate BOLD and multivoxel/MVPA fMRI), TMS, and pharmacological/computational evidence on the neural bases of working memory. The review is organized around three core questions: (a) *where* WM contents are represented in the brain — posterior sensory-cortex (storage) vs PFC (control), (b) what *role* PFC plays — content vs control, and (c) *how* PFC interacts with subcortical and dopaminergic systems for the "control of the controller." The argument structure is to take each classical "WM is in PFC" finding (delay firing, lesion deficits, frontal BOLD) and re-examine it in light of MVPA and TMS data that put content-specific decoding in posterior cortex; the resulting synthesis treats PFC as a meta-controller whose contribution is biasing and adjudication rather than storage.

## 5. Results

The review consolidates a set of empirical results that constitute the modern WM neuroscience consensus:

- **MVPA decodes orientation, color, and motion content from V1-V4 during WM delays** even when univariate BOLD returns to baseline (Harrison & Tong 2009; Serences et al. 2009) — the foundational result for sensory recruitment.
- **PFC decoding accuracy is often weaker than sensory cortex** for stimulus-specific features in delayed-recognition paradigms; PFC content selectivity emerges only when the task requires categorical, rule-related, or transformed codes (Freedman, Miller).
- **TMS to occipital cortex during the delay disrupts WM for visual features**; TMS to PFC disrupts cognitive-control aspects of WM but spares simple feature retention.
- **Lesions confined to lateral PFC produce mild deficits on simple span tasks** but larger deficits on manipulation/interference tasks — replicated across multiple patient series.
- **Dopamine D1 agonists improve WM performance in monkeys** following an inverted-U dose-response curve (Williams & Goldman-Rakic 1995; Vijayraghavan et al. 2007), demonstrating the dopaminergic neuromodulation of PFC delay activity.
- **Striatal activity tracks updating events** in n-back and reference-back tasks (Cools, Frank), supporting the gating model where striatum gates entry to and update of PFC WM representations.
- **Persistent PFC firing tracks task rules, response selection, and attended-item identity** rather than purely passive content maintenance — a re-interpretation of the classical Funahashi/Goldman-Rakic delay-firing literature.
- **TMS to lateral PFC can reactivate "unattended" but task-relevant items** held in posterior cortex (Rose et al. 2016) — direct evidence for PFC's role in mnemonic control rather than storage, and for the activity-silent storage of momentarily unattended items.

## 6. Critique / limitations

This review states the field's modern consensus but several aspects of its synthesis remain contested or underspecified.

- **Largely a narrative synthesis rather than systematic/quantitative meta-analysis.** The selection of evidence is curated; competing primary-source positions (e.g., Constantinidis et al. 2018, who defend persistent activity as the core mechanism) are acknowledged but not adjudicated by a formal data-pooling method.
- **Null-result-driven inference.** The argument that PFC does not store content is partly inferred from weaker MVPA decoding in PFC than in sensory cortex; absence of decoding is not absence of representation, particularly when SNR and voxel-size differ across regions.
- **MVPA sensitivity differences across cortex** can confound the sensorimotor-recruitment argument; the inference that "stronger decoding = greater representational role" assumes equal decoding sensitivity, which is not established.
- **Limited treatment of subcortical contributions beyond striatum.** Thalamus, hippocampus, and the brainstem dopaminergic system are mentioned but not deeply integrated; the review does not engage with thalamocortical sustaining circuits (which became more prominent in Sreenivasan & D'Esposito 2019).
- **Downplays category-level and abstract codes in PFC.** Freedman, Miller, and Wallis have shown robust category/rule representations in PFC that the "PFC does not store content" framing tends to obscure; these are arguably *content* representations of a different kind.
- **Does not deeply engage with capacity-limit/resource models** (Bays & Husain 2008; Zhang & Luck 2008; Ma, Husain & Bays 2014) — the slot-vs-resource debate is largely orthogonal to the review's content/control distinction.
- **Written before broad uptake of activity-silent WM evidence.** Some claims (especially around persistent activity as a proxy for content maintenance) need updating in light of Stokes 2015, Wolff et al. 2017, and Rose et al. 2016.
- **Treatment of WM/LTM interactions and the episodic buffer is brief** — the hippocampus-WM interface (which the user's program engages via [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md) and [whittington2020_tem](whittington2020_tem.md)) is largely outside scope.
- **The "control of the controller" via dopamine is asserted but not mechanistically derived** — the relation between dopamine, striatal gating, and PFC delay representations is invoked but not formally modeled at the circuit level.

## 7. Connection to our work

D'Esposito & Postle 2015 is the *biological warrant* for several of the user's most consequential architectural commitments.

**Touchpoint 1: memory is attention applied to internal representations.** The review's central claim — that WM = attention applied to internal representations — is the biological warrant for the user's program-level decision to share substrate between memory and attention. In the user's architecture, the central self-attention of the Feedback Transformer is *simultaneously* the inter-hub attention mechanism and the memory-update gate; there is no architectural separation between "attention" and "memory update." This is directly Postle/D'Esposito's emergent-property view at the circuit level: WM contents arise as the joint state of (a) hub-internal recurrent memory holding the content and (b) central attention biasing access to that content.

**Touchpoint 2: content/control dissociation as hub vs central-attention.** The review's content/control dissociation — domain-specific posterior cortex stores the *content*, PFC supplies the *control* — maps directly onto the user's hub/central-attention split. Each hub (visual, motor, memory) is the *content holder* (analog of posterior sensory cortex), and the Feedback Transformer's central self-attention is the *controller* (analog of PFC). The user's architecture therefore inherits a biologically-licensed division of labor rather than imposing an arbitrary one.

**Touchpoint 3: PFC delay activity as control, not content — implications for hub state interpretation.** The reinterpretation of PFC delay firing as control rather than content has a direct architectural consequence: the user's memory hub's recurrent state should not be expected to encode raw sensory content; it should encode *control variables* — attention priors, rule indicators, decision thresholds — that bias other hubs. The visual hub holds the visual content; the memory hub holds the *meta-content* (what to attend to, what rule applies, what to integrate). This re-targets the user's empirical analyses: probing the memory hub for raw stimulus features may fail not because the architecture is broken but because the architecture is correctly recapitulating the PFC-as-controller logic.

**Touchpoint 4: striato-cortical gating as the architectural template for the slow-memory write gate.** The review's emphasis on striatal gating of PFC WM updates — the Frank/O'Reilly framework — is the biological warrant for the user's *gated* memory updates ([concepts/error-gated-update.md] family). PRISM v2's slow-memory write gate, the recurrent ViT's attention-modulated memory update, and the Feedback Transformer's update gate with bias = 0 ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md) Refinement 3) are all architectural instantiations of striatal gating: a learned gate decides when content is admitted into a slowly-evolving memory store. The biological warrant gives the architectural choice a substantive grounding rather than an ad-hoc engineering motivation.

**Touchpoint 5: dopaminergic neuromodulation as a higher-order gate.** The "control of the controller" — dopaminergic modulation of PFC delay activity — is the biological template for the third-level control hierarchy in the user's program: a neuromodulatory signal (e.g., novelty-driven dopamine from Lisman-Grace, [lisman_grace2005_hippocampal_vta](lisman_grace2005_hippocampal_vta.md)) modulates the central attention substrate, which modulates the hubs. This is a three-level architecture: (i) hub-internal content, (ii) central-attention control over hubs, (iii) neuromodulatory control over central attention. The user's program already commits to (i) and (ii); D'Esposito-Postle's "control of the controller" is the biological warrant for the third level.

**Touchpoint 6: distributed storage is multi-compartmental memory.** The review's distributed storage finding — content lives in V1-V4 and parietal and to-be-acted-upon premotor cortex simultaneously, with different abstraction levels — is the biological warrant for the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commitment. The V1-paired/V2-paired/V4-paired memory layer split (PRISM v2 / user's program) directly recapitulates the distributed-cortical-storage finding: shallow memory carries low-level feature codes, deeper memory carries category/rule codes, all simultaneously active. The architectural choice has direct biological warrant.

**Touchpoint 7: dual roles for delay activity in the recurrent ViT.** The review's reinterpretation of delay-period firing as carrying control and rule information, not just maintenance, suggests that the recurrent ViT's per-step hidden state $H^{(t)}$ should be interpreted in a hybrid way: parts of $H^{(t)}$ are the *content* being maintained (raw feature codes), and parts are the *control* (attention prior, task variable). Analyses of $H^{(t)}$ that lump all components together will miss this dissociation; the architecturally-correct probe should disentangle content-coding vs control-coding subspaces, perhaps via demixed PCA or similar population-analysis methods (Murray, Bernacchia et al. 2017).

## 8. Citations to follow

- `sreenivasan_curtis_desposito2014_persistent_activity_revisited` — the immediate precursor *TiCS* paper that reframes persistent activity; the conceptual bridge between D'Esposito 2007 and this 2015 review. Not in seed.
- `lara_wallis2015_pfc_wm` — companion piece in *Frontiers in Systems Neuroscience* that explicitly defends PFC's role in goal-directed control; the contrast view to overly-strong sensory recruitment. Not in seed.
- `riley_constantinidis2016_persistent_activity_wm` — defends a continued central role for persistent activity; the most direct response to the activity-silent / sensory-recruitment line. Not in seed.
- `ester_sprague_serences2015_parietal_frontal_mnemonic` — stimulus-specific mnemonic representations in parietal and frontal cortex; key MVPA evidence for distributed storage. Not in seed.
- `rose_larocque_postle2016_tms_reactivation` — TMS-driven reactivation of latent WM items, *Science* — the most decisive evidence for activity-silent storage. Not in seed.
- `lundqvist_herman_miller2018_delay_activity_yes` — "Working memory: delay activity, yes! Persistent activity? Maybe not." — the gamma/beta-burst alternative. Not in seed.
- [constantinidis2018_persistent_activity](constantinidis2018_persistent_activity.md) — the persistent-activity defense; the contrast position. In seed.
- [stokes2015_activity_silent_wm](stokes2015_activity_silent_wm.md) — the activity-silent framework that this review touches on but does not fully integrate. In seed.
- [christophel2017_distributed_wm](christophel2017_distributed_wm.md) — the explicit distributed-WM review that complements this one. In seed.
- [sreenivasan_desposito2019_delay_activity](sreenivasan_desposito2019_delay_activity.md) — the direct follow-up review by Sreenivasan and one of these authors, four years later. In seed.
- [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) — the empirical demonstration of shared attention-WM mechanisms in PFC; the modern follow-on. In seed.
- `serences2016_storage_review` — Serences' review of visual short-term memory storage mechanisms; the sensory-recruitment update. Not in seed.
- `manohar_zokaei2019_attending_in_wm` — neural mechanisms of attending to items in WM; an integrative review of attention-WM crossover. Not in seed.
