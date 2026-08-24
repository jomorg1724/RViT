---
id: pradel2021_sc_rmtg
title: "Superior Colliculus Controls the Activity of the Rostromedial Tegmental Nuclei in an Asymmetrical Manner"
authors:
  - "Pradel, Kamil"
  - "Drwięga, Gniewosz"
  - "Błasiak, Tomasz"
year: 2021
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.1556-20.2021"
arxiv: ""
url: "https://doi.org/10.1523/JNEUROSCI.1556-20.2021"
tags:
  - subcortical
  - dopamine
  - lesion-microstimulation
concepts:
  - priority-map
  - reward-modulated-attention
  - optogenetic-perturbation
related:
  - krauzlis2013_sc_attention
  - bolton2015_dopamine_sc
  - hikosaka2006_bg_reward_eyes
  - herman_arcizet2020_caudate_sc
  - essig_felsen2016_dopamine_sc
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_85
status: full
depth: full
last_updated: "2026-05-15"
---

# Superior Colliculus Controls the Activity of the Rostromedial Tegmental Nuclei in an Asymmetrical Manner

## 1. Abstract

Dopaminergic (DA) neurons of the midbrain are involved in controlling orienting and approach of animals toward relevant external stimuli. The firing of DA neurons is regulated by many brain structures; however, the sensory input is provided predominantly by the ipsilateral superior colliculus (SC). It is suggested that SC also innervates the contralateral rostromedial tegmental nucleus (RMTg) — the main inhibitory input to DA neurons. This study describes the physiology and anatomy of the SC–RMTg pathway. Using anterograde, retrograde, and transsynaptic tract-tracing in male Sprague Dawley rats, the authors show that RMTg is monosynaptically innervated predominantly by the lateral parts of the intermediate layer of the *contralateral* SC. In vivo silicon-probe electrophysiology combined with optogenetic stimulation of the SC reveals that activation of the contralateral SC *excites* the majority of RMTg neurons, while ipsilateral SC stimulation evokes mixed excitatory or inhibitory responses. Activating RMTg neurons that receive contralateral-SC input — or stimulating contralateral-SC axon terminals within RMTg — *inhibits* midbrain DA neurons. The pathway is positioned to mediate sensory-direction-dependent asymmetries in dopamine release between left and right striatum, and thereby to guide motivation-driven locomotion toward salient external stimuli.

## 2. Why this matters for us

Pradel, Drwięga & Błasiak 2021 is the load-bearing anatomical and physiological reference for an *inhibitory* SC → RMTg → DA pathway running *contralaterally*. It complements the well-known excitatory ipsilateral SC → SNc/VTA route (e.g., Comoli et al. 2003, May et al. 2009) by demonstrating that the same SC priority map asymmetrically reshapes the dopaminergic system on *both* sides of the brain — boosting DA contralateral to the stimulus and suppressing DA ipsilateral to it (via contralateral SC → RMTg → ipsilateral DA inhibition). For the user's architectural program — which treats SC as a priority-map analog of the central self-attention map and treats the RL hub as a downstream consumer of that priority signal — this paper supplies the concrete subcortical wiring diagram by which an attentional priority map controls the *reward / RL* circuitry. It is the empirical scaffolding for the program's commitment that the priority-map and RL-hub coalitions are anatomically coupled rather than independent.

## 3. Key claims

1. **The contralateral SC monosynaptically innervates RMTg.** Anterograde, retrograde, and transsynaptic tracing converge on the conclusion that RMTg-projecting SC neurons reside predominantly in the *lateral intermediate layer* of the *contralateral* SC.

2. **The SC → RMTg projection is asymmetrically excitatory.** Optogenetic activation of contralateral SC excites the majority of RMTg neurons; ipsilateral SC stimulation produces roughly equal excitatory and inhibitory responses. The contralateral pathway is therefore the dominant, sign-consistent driver of RMTg.

3. **Activated RMTg neurons inhibit midbrain DA neurons.** Optogenetic stimulation of contralateral-SC axon terminals in RMTg, or direct activation of the RMTg neurons receiving that input, suppresses DA-neuron firing in VTA / SNc on the same side as the activated RMTg.

4. **The pathway generates a lateralized DA asymmetry.** Because contralateral SC inhibits ipsilateral DA via RMTg, and ipsilateral SC excites ipsilateral DA directly (via the previously-established SC → SNc/VTA excitatory route), a unilateral SC activation produces *opposing* effects on the two hemispheres' dopaminergic output.

5. **The circuit is positioned to drive direction-of-motion.** Behavioral asymmetries (animals turn away from the higher-DA striatum, toward the lower-DA striatum's hemifield, i.e., toward the stimulus) imply this circuit converts a hemifield-localized sensory event into a directional motor / motivational drive.

6. **RMTg is the principal inhibitory relay from SC to DA.** The SC does not synapse heavily *directly* on DA neurons with inhibitory action; the inhibitory route is indirect, via RMTg, consistent with RMTg's broader role as the "tail of the VTA" / GABAergic gate on midbrain DA.

7. **The intermediate-layer SC carries both attention/orienting and reward-asymmetry signals.** The same SC subdivision that supports covert attention (Krauzlis et al. 2013) and saccade target selection sends a major projection to RMTg, suggesting these functions share a substrate.

## 4. Methods

**Subjects.** Adult male Sprague Dawley rats.

**Tract tracing.**
- *Anterograde:* AAV expressing fluorescent protein injected into SC; axon terminals visualized in RMTg by layer of origin.
- *Retrograde:* fluorescent retrograde tracer injected into RMTg; cell bodies counted in ipsi- and contralateral SC, partitioned by superficial / intermediate / deep layers and by medial / lateral subdivisions.
- *Transsynaptic:* monosynaptic tracing (rabies-based / AAV-mediated) to establish single-synapse SC → RMTg connectivity and identify the SC layer and laterality of origin without contamination by polysynaptic routes.

**In vivo electrophysiology + optogenetics.** ChR2 expressed in SC neurons via viral injection. Urethane-anesthetized rats received silicon-probe recordings in RMTg or in VTA / SNc. Either contralateral or ipsilateral SC was photostimulated with brief light pulses; spike responses on each unit were classified as excitatory, inhibitory, or unresponsive based on poststimulus time histograms relative to a pre-stimulus baseline window. A separate experimental arm photostimulated the *axon terminals* of contralateral SC neurons *within RMTg* (with the SC cell bodies left dark), while recording DA neurons in the ipsilateral-to-stimulated-RMTg VTA / SNc — this isolates the contralateral SC → RMTg → DA arc from any concurrent ipsilateral SC → DA effect.

**Cell-type identification.** DA neurons identified by canonical electrophysiological criteria (broad biphasic action-potential waveform, slow tonic firing rate ~2–8 Hz, characteristic interspike-interval distribution with burst-pause structure). RMTg neurons identified by location relative to stereotaxic landmarks and by electrophysiological profile consistent with the Jhou et al. 2009 description of "tail of VTA" GABAergic units.

**Statistics.** Proportions of excitatory / inhibitory / no-response cells compared between ipsi- and contralateral conditions using χ² / Fisher's exact tests; per-unit firing-rate changes pre/post photostimulation compared with paired nonparametric tests. Histological reconstruction confirms probe placement in RMTg and viral expression in the targeted SC subdivisions.

## 5. Results

- **Retrograde-tracing distribution.** The majority of RMTg-projecting SC neurons sit in the *lateral intermediate layer* of the *contralateral* SC. Ipsilateral SC contributes a smaller fraction of RMTg input.
- **Laminar specificity.** RMTg-projecting cells are concentrated in the *intermediate gray / intermediate white* layers, not the superficial visual-input layers. This locates the SC → RMTg projection in the orienting / motor-priority output stage of SC, not the bottom-up sensory stage.
- **Optogenetic activation of contralateral SC** elicits excitation in the *majority* of recorded RMTg neurons; a small minority show inhibition.
- **Optogenetic activation of ipsilateral SC** elicits roughly *equal proportions* of excitatory and inhibitory responses in RMTg, consistent with a weaker / more diffuse projection plus possible polysynaptic effects.
- **Terminal stimulation in RMTg.** Photostimulating contralateral-SC axon terminals *locally within RMTg* (bypassing SC cell bodies) drives RMTg neurons and *inhibits* DA neurons recorded in VTA / SNc on the side ipsilateral to the photostimulated terminals. This isolates the monosynaptic SC → RMTg → DA inhibitory arc from any concurrent direct SC → DA effect.
- **Latency.** Response latencies of RMTg units to SC photostimulation are short and consistent with monosynaptic transmission; DA-neuron inhibition follows with the additional delay expected of a disynaptic SC → RMTg → DA route.
- **Behavioral implication** (inferred, not directly tested): a hemifield-localized sensory event drives the contralateral-to-stimulus SC → excites contralateral-to-stimulus RMTg → inhibits ipsilateral-to-stimulus DA, while the ipsilateral-to-stimulus SC simultaneously excites ipsilateral-to-stimulus DA. Net effect: striatal DA asymmetry favoring the hemisphere contralateral to the stimulus, biasing motor output *toward* the stimulus.

Exact unit-count percentages and effect sizes are reported in the paper's Figures 2–6; the abstract emphasizes qualitative proportions and direction-of-effect rather than headline percentages.

## 6. Critique / limitations

The work is in *anesthetized* rats; behavioral correlation is inferred from the broader literature on striatal DA asymmetry and turning behavior rather than measured here. Awake-behaving extensions would tighten the bridge between the circuit's anatomy and the orienting / approach behavior it is hypothesized to drive — and would let the authors test whether spontaneous attentional / orienting events drive the contralateral SC → RMTg → DA inhibition at behaviorally relevant magnitudes.

The SC is treated as a *single output node* despite known cell-type heterogeneity (wide-field, narrow-field, stellate, GABAergic) in the intermediate layer. The paper identifies the *laminar* and *hemispheric* origin of RMTg-projecting cells but does not separate molecularly defined SC subtypes (e.g., Vglut2+ projection neurons, parvalbumin+ wide-field cells); whether one specific SC cell class is the RMTg driver is left open. This matters because different SC cell types carry different signal types — saccade-commands vs. visual transients vs. orienting commands — and the function of the SC → RMTg pathway depends on which.

The DA-neuron inhibition is demonstrated with *optogenetic* stimulation rather than during a behaviorally relevant sensory event. Whether *naturalistic* visual stimuli in the contralateral hemifield produce the same RMTg activation magnitude — sufficient to suppress DA firing — is not directly shown. The optogenetic perturbation is causal and clean, but the magnitude-of-effect under natural input remains to be quantified.

The asymmetry account is presented for visual / spatial orienting; the framework's generality across modalities (auditory, somatosensory SC inputs) is not addressed. Given that SC integrates multi-modal inputs in its deep layers, a unified account would predict the same RMTg-mediated DA asymmetry for cross-modal salient events.

The paper does not engage with the *attention* literature (Krauzlis et al. 2013; Cavanaugh & Wurtz 2004). The same intermediate-layer SC that projects to RMTg is the substrate Krauzlis identifies as critical for covert attention; the implications for *attention-mediated* DA modulation — i.e., whether covert-attention-driven SC priority changes drive DA asymmetry without overt orienting — are left for downstream work. The user's program would benefit from explicit experimental tests of this.

The paper is rodent-only. Whether the same contralateral SC → RMTg → DA architecture exists in primate (where the attention literature is most developed) is not directly established. Primate RMTg homologs exist, but the cross-species comparison of laterality and laminar origin is incomplete.

## 7. Connection to our work

This paper is the load-bearing reference for treating the SC priority map as an *upstream controller of the reward / RL system*, not merely a parallel attention substrate. Several components of the user's architectural program ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md)) depend on this:

**SC as priority map → RL hub.** The program treats the central self-attention map as the AI homolog of SC + LIP combined ([multi_hub_multi_objective_system](research_db/concepts/multi_hub_multi_objective_system.md)). The RL hub is one of the competing coalitions reading from and writing to that map. Pradel et al. 2021 establishes the biological correlate of this read-write relationship: SC's intermediate-layer priority signal *directly controls* DA-firing asymmetry via RMTg. The user's RL hub, by analogy, reads attention priority and produces a corresponding reward/value signal that competes for control of attention on the next step.

**Asymmetric inhibitory control as a substrate for competition.** The competition-emergent-PC thesis ([competition-emergent-predictive-coding](research_db/concepts/competition-emergent-predictive-coding.md)) requires that hubs *suppress* each other, not only excite. Pradel et al. show a concrete biological example: SC asymmetrically excites contralateral RMTg, which *inhibits* DA — i.e., one priority-map coalition (contralateral SC) suppresses an output coalition (ipsilateral DA) via a disinhibitory relay. This is the wiring pattern the user's program postulates at the algorithmic level.

**RMTg as a GABAergic gate analog.** RMTg's role as the "tail of the VTA" — a GABAergic gate sitting between sensory/cognitive priority and DA output — is the biological analog of the user's gated update structure in the GridCell RNN ([gridcell-rnn](research_db/concepts/gridcell-rnn.md)), in which a learned gate decides how much of a feedback-transformer output writes through to memory. The RMTg sits in precisely this position relative to DA. A model that includes both a priority map and an RL hub should incorporate a gating relay between them; Pradel 2021 names the brain region that performs this function.

**Hemispheric / spatial asymmetry as a design pattern.** The paper's central finding — that a *single* SC priority signal produces *opposing* effects on the two sides of the dopaminergic system — is methodologically suggestive for the user's multi-hub design. A single attention signal can be wired to *excite* one downstream hub while *inhibiting* another, producing competition by construction. The user's Feedback Transformer admits this: positive feedback weights from one hub and negative weights from another are equally permissible at the Q/K/V projection.

**Connection to the SC-attention literature.** Read alongside [krauzlis2013_sc_attention](research_db/papers/krauzlis2013_sc_attention.md), this paper closes a loop: Krauzlis shows the SC carries an attention/priority signal; Pradel shows the same intermediate-layer SC neurons control the DA system through RMTg. Together they support the program's commitment that the attention substrate and the RL/reward substrate are *anatomically and functionally entwined*, not modular. The user's architectural decision to feed the RL hub from the same self-attention map the perception system uses, rather than from a separate value-only stream, is biologically warranted by this chain.

**Connection to the broader DA-SC literature.** [bolton2015_dopamine_sc](research_db/papers/bolton2015_dopamine_sc.md) and [essig_felsen2016_dopamine_sc](research_db/papers/essig_felsen2016_dopamine_sc.md) establish the ipsilateral SC → DA excitatory route. Pradel 2021 supplies the missing contralateral inhibitory complement, completing the bilateral picture. [hikosaka2006_bg_reward_eyes](research_db/papers/hikosaka2006_bg_reward_eyes.md) supplies the basal-ganglia / saccade-reward integration story that closes the loop back to behavior; [herman_arcizet2020_caudate_sc](research_db/papers/herman_arcizet2020_caudate_sc.md) shows the same SC priority signal modulates the caudate. The user's program is best motivated by treating these as one coupled SC ↔ BG ↔ DA system, with the priority map at its center.

**Reward-modulated attention as a tagged concept.** This entry uses the `reward-modulated-attention` concept (from TAXONOMY.md), reflecting that the SC → RMTg → DA circuit is precisely the substrate by which reward signals are made *attention-contingent*: the priority map gates the DA signal, so reward delivery and attentional allocation become coupled at the circuit level. The user's program treats reward-modulated attention as the central organizing principle of the RL hub; Pradel 2021 is one of the strongest empirical anchors for that principle in the subcortical literature.

**Disinhibition as a primitive.** RMTg sits in a *disinhibitory* position: SC excitation of RMTg leads to DA *inhibition* (RMTg → DA is GABAergic). This SC ⊢⊣ DA chain is a two-stage sign flip. Architecturally, this is the kind of motif that lets a positive-going priority signal produce a negative-going downstream effect without the priority module itself needing to learn negative weights. The user's Feedback Transformer can implement this either with signed Q/K projections (one stage) or via a relay module that flips signs (two stages, biologically faithful). Pradel 2021 documents the brain's preference for the two-stage solution, which is also more compatible with the biophysical constraint that long-range projections are predominantly glutamatergic / excitatory.

**Implications for the central self-attention map.** The Feedback Transformer ([feedback-transformer](research_db/concepts/feedback-transformer.md)) integrates Q/K/V contributions from many recurrent feedback sources. Pradel 2021 motivates a specific instance of this: the priority-map module should project both into the *next* attention computation (as a top-down feedback source) *and* into the RL hub's value head. The RL hub then feeds back negatively-signed Q/K projections, modulating attention away from regions whose value contribution is suppressed by the priority signal. This is the algorithmic homolog of "SC excites contralateral RMTg → inhibits ipsilateral DA": the priority map exerts mixed-sign control over downstream reward populations.

**Implications for the recurrent ViT's perturbation experiment.** The Recurrent ViT paper (2502.10955) reports a perturbation analysis in which the attention map is artificially modified and the model's downstream behavior is measured. Pradel et al. provide the biological analog: optogenetic perturbation of SC produces direction-specific changes in DA firing downstream. The user's perturbation experiment and Pradel's perturbation experiment share the same logic — perturb the priority map, measure the downstream effect on a target system — at different levels of analysis.

**Caveat on level of analysis.** Pradel et al. work in anesthetized rats with optogenetic perturbation; the user's program is a transformer-based model trained on natural images / video. The cross-level mapping is at the *connectivity-pattern* level, not the cellular implementation. The architectural lesson — that priority maps directly control downstream reward circuitry with mixed-sign coupling — is robust to this level mismatch.

## 8. Citations to follow

- `comoli2003_sc_da` — Comoli et al. 2003, foundational ipsilateral SC → SNc excitatory pathway. Pradel 2021's anatomical reference point for the contralateral complement. Not yet in seed.
- `may2009_sc_da_pathway` — May et al. 2009 anatomy of SC → DA system. Anatomical context for the present paper. Not yet in seed.
- `jhou2009_rmtg` — Jhou et al. 2009 characterization of RMTg as "tail of the VTA" GABAergic gate. Foundational for the RMTg side. Not yet in seed.
- `barrot2012_rmtg_aversive` — Barrot et al. 2012 RMTg in aversive processing. Connects this circuit to negative-reward coding and provides the predictive-error / aversion interpretation of RMTg's role. Not yet in seed.
- `redgrave_gurney2006_sc_short_latency_da` — Redgrave & Gurney 2006 on short-latency DA via SC, the conceptual frame Pradel builds on. Not yet in seed.
- `dommett2005_sc_da_latency` — Dommett et al. 2005 on SC-driven short-latency DA bursts. Empirical anchor for the SC → DA route. Not yet in seed.
- `hikosaka2008_basal_ganglia_orienting` — extends the SC / BG orienting account this paper relies on for behavioral inference. Not yet in seed.
- `coddington_dudman2018_sc_da_movement` — Coddington & Dudman 2018 on movement-related signaling in DA neurons including SC contributions. Relevant for the motor-output side. Not yet in seed.
- `wickens2007_striatal_contrast` — Wickens et al. on left/right striatal-DA asymmetry and turning behavior, which underwrites the behavioral interpretation Pradel invokes. Not yet in seed.
