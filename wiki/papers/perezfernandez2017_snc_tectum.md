---
id: perezfernandez2017_snc_tectum
title: "Direct dopaminergic projections from the SNc modulate visuomotor transformation in the lamprey tectum"
authors:
  - "Pérez-Fernández, Juan"
  - "Kardamakis, Andreas A."
  - "Suzuki, Daichi G."
  - "Robertson, Brita"
  - "Grillner, Sten"
year: 2017
venue: "Neuron"
doi: "10.1016/j.neuron.2017.09.051"
arxiv: ""
url: "https://pubmed.ncbi.nlm.nih.gov/29107519/"
tags:
  - subcortical
  - dopamine
  - lesion-microstimulation
concepts:
  - reward-modulated-attention
  - gain-modulation
  - top-down-feedback
related:
  - bolton2015_dopamine_sc
  - essig_felsen2016_dopamine_sc
  - hikosaka2006_bg_reward_eyes
  - glimcher2011_dopamine_rpe
  - krauzlis2013_sc_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_87
status: full
depth: full
last_updated: "2026-05-15"
---

# Direct dopaminergic projections from the SNc modulate visuomotor transformation in the lamprey tectum

## 1. Abstract

Dopamine neurons in the SNc play a pivotal role in modulating motor behavior via striatum. Here, the authors show that the same dopamine neuron that targets striatum also sends a direct branch to the optic tectum (the lamprey homologue of mammalian superior colliculus). Whenever SNc neurons are activated, both targets will therefore be affected. Visual stimuli (looming objects or moving bars) activate SNc dopamine neurons coding stimulus saliency and also elicit distinct tectally-mediated motor responses (eye movements, orienting, evasive turns) that are modulated by the dopamine input. Whole-cell recordings from tectal projection neurons and interneurons show that dopamine, released by SNc stimulation, increases or decreases excitability depending on whether the cell expresses the D1 or the D2 receptor. SNc thus exerts its effects on the visuomotor system through a combined effect directly on tectum and also via striatum. This direct SNc modulation occurs regardless of striatum and represents a novel mode of motor control conserved from the earliest vertebrates.

## 2. Why this matters for us

This paper is the most direct evidence available that the dopamine→optic-tectum projection is an evolutionarily ancient component of the vertebrate visuomotor blueprint, not a mammalian innovation. The lamprey, which diverged from the mammalian lineage roughly 560 Mya, already wires SNc collaterals directly onto tectal neurons carrying D1 and D2 receptors. Combined with Bolton et al. 2015 (a parallel finding in the mammalian superior colliculus from a diencephalic dopamine source) and Essig & Felsen 2016, this anchors the claim that subcortical reward-modulated attention — gain control of an orienting / priority map by a dopaminergic salience signal — is a *universal* vertebrate architecture. For the user's program (`threads/the_user_architectural_program.md` §5), this is exactly the evidence the RL hub's universality argument needs: the dopaminergic signal that biases attention is not a cortical add-on but a phylogenetic floor.

## 3. Key claims

1. Single SNc dopaminergic neurons send collateralized axons to both striatum and the optic tectum in lamprey (retrograde double-labelling).
2. SNc dopamine neurons are activated by behaviorally salient visual stimuli (looming, moving bars), with firing scaling to stimulus salience rather than to motor output.
3. Tectal projection neurons and local interneurons express either D1 or D2 receptors; dopamine bidirectionally modulates their excitability (D1-positive cells depolarize / increase firing; D2-positive cells hyperpolarize / decrease firing).
4. SNc stimulation modulates the amplitude and probability of tectally-evoked visuomotor responses (orienting toward small moving bars; evasive turns away from looming stimuli).
5. The direct SNc→tectum pathway operates in parallel with, and independently of, the classical SNc→striatum→tectum indirect route; it represents a previously uncharacterized mode of motor control.
6. The pathway is homologous to the Bolton et al. 2015 diencephalic-DA→superior-colliculus pathway in mammals, supporting deep evolutionary conservation.

## 4. Methods

Adult lamprey (*Lampetra fluviatilis*) in vitro semi-intact and isolated-brain preparations were used.

- **Tract tracing.** Retrograde tracers (Neurobiotin, dextran-conjugated rhodamine / fluorescein) injected separately into striatum and into optic tectum, followed by tyrosine-hydroxylase (TH) immunohistochemistry in mesencephalic SNc. Double-labelled TH+ neurons confirm single-cell collateralization.
- **Extracellular recording.** Multi-unit and single-unit recordings from identified SNc dopamine neurons (TH+ post-hoc) during presentation of full-field looming and translating-bar visual stimuli delivered to the intact eye of the semi-intact preparation.
- **Whole-cell patch.** Tectal projection neurons (identified by retrograde label from reticulospinal targets) and tectal interneurons were patched. Dopamine was either bath-applied (10–100 µM) or released endogenously by trains of electrical stimulation in SNc; D1 (SCH-23390) and D2 (sulpiride) antagonists used pharmacologically.
- **Behavioral readout.** In the semi-intact preparation, eye movements and body-axis bending in response to visual stimuli were quantified before and during SNc microstimulation, with and without tectal D1/D2 antagonism.
- **Receptor mapping.** Single-cell RT-PCR (or in-situ hybridization) for D1 vs. D2 transcripts on patched, biocytin-filled tectal cells to correlate physiological response to dopamine with receptor identity.

## 5. Results

- **Collateralization.** A substantial fraction of SNc TH+ neurons (the paper reports tens of percent, on the order of ~40% in the relevant rostro-lateral SNc band) were retrogradely double-labelled from striatum and tectum.
- **Visual responses of SNc neurons.** SNc dopamine units fired phasically to looming and to moving-bar stimuli with latencies of tens of ms; firing rate scaled with stimulus salience (looming velocity, contrast) rather than with the resulting motor act.
- **Bidirectional dopamine modulation in tectum.** D1-expressing tectal cells showed depolarization and increased input resistance / firing in response to dopamine; D2-expressing cells showed hyperpolarization / decreased firing. Both effects were blocked by the corresponding receptor antagonist.
- **Behavioral gain.** SNc stimulation increased the probability and amplitude of tectally-elicited orienting eye movements toward a small moving bar; the same SNc stimulation also potentiated evasive turns away from looming stimuli. Tectal infusion of D1+D2 antagonists abolished the SNc-driven modulation while leaving baseline tectal visuomotor responses largely intact, confirming that the modulation is local to tectum (not a downstream striatal effect).
- **Striatal independence.** The behavioral effects of the direct SNc→tectum branch persisted after striatal silencing (local anesthetic / pharmacological block of striatum), establishing the direct pathway as functionally sufficient.

## 6. Critique / limitations

- **In vitro semi-intact preparation.** Behavior is reduced to reflex-like orienting and evasive responses under controlled visual stimulation; the paper does not — and cannot — speak to cognitive or learned attentional set in the lamprey.
- **Coarse cell typing.** D1 vs. D2 identity is treated as a binary label per cell; coexpression and gradient effects are not deeply addressed. In mammals, D1/D2 coexpression on the same cell is non-trivial and likely matters here.
- **Salience vs. reward.** The SNc firing is correlated with stimulus salience, but the paper does not show classical RPE-like phasic firing to learned reward predictors, so the homology to mammalian midbrain DA RPE (Glimcher 2011) is anatomical and physiological at the level of *salience signalling*, not yet at the level of reward prediction error per se.
- **Branching fraction.** The exact percentage of dual-projecting SNc neurons is preparation-dependent; cross-comparison with Bolton 2015 (which identifies a diencephalic, not midbrain, DA source in mouse SC) is suggestive of conservation but the source nuclei differ in the two species, raising a question about strict homology of the projection neuron.
- **Receptor pharmacology.** Bath dopamine concentrations (10–100 µM) used in slice are well above in-vivo synaptic concentrations; the inferred bidirectional D1/D2 effect is qualitatively correct but precise gain functions are not constrained.
- **Looming vs. bar dichotomy.** The behavioral distinction between approach (orienting) and avoidance (escape) responses is presented as cleanly read out from the tectum; subsequent work (Suzuki, Pérez-Fernández et al. follow-ups) shows the situation is more complex, with separable medial vs. lateral tectal sub-circuits each receiving distinct DA modulation.

## 7. Connection to our work

The user's architectural program (`threads/the_user_architectural_program.md` §5) commits to a multi-hub system in which one hub is an RL hub whose dopamine-derived signal modulates the global self-attention / priority map. The universality argument for that commitment runs as follows: **if** the dopamine-to-priority-map projection is a phylogenetically ancient, conserved feature of vertebrate brains, **then** the RL-hub modulation of attention is not an arbitrary engineering choice but recapitulates a 500-million-year-old organizing principle of biological attention. Pérez-Fernández et al. 2017 is one of the two anchor papers (with Bolton 2015) that supplies the empirical ground for the antecedent.

Specifically:

1. **Direct DA→tectum projection in lamprey** establishes the pathway in the *earliest extant vertebrate*. The mammalian superior colliculus / optic tectum is the canonical orienting / priority map (Krauzlis 2013, Hikosaka 2006); having direct dopaminergic input onto it from the SNc — i.e., the same population that does the well-known striatal modulation — means the architecture "midbrain reward signal directly biases the orienting/priority map" is present at the root of the vertebrate tree.
2. **D1 / D2 bidirectional gain** matches the user's `gain-modulation` concept: the RL hub's contribution to the self-attention Q/K projection is plausibly *bidirectional* (excite or suppress per-cell), not a single-sign salience boost. This biological motif licenses an architectural choice in the Feedback Transformer (§1 of the user's program) where the RL hub can both promote and demote tokens.
3. **Salience-coded SNc firing in response to looming / bars** maps onto the published Recurrent ViT's bottom-up sensory salience signal (the patches whose features dominate the attention map before recurrent feedback arrives). The lamprey result says: in real brains, an external dopaminergic salience channel parallels the local feedforward salience channel and *both* arrive at the priority map. The Feedback Transformer's design — multiple feedback sources element-wise broadcast into Q/K — is the natural architectural analogue.
4. **Striatal independence** matters for hub design. The user's program treats hubs as having direct feedback into the central self-attention module, not as having to route through other hubs. Pérez-Fernández 2017 demonstrates that real cortex-equivalent (tectum) circuitry indeed receives DA modulation directly, bypassing the striatal "main route." This is direct biological evidence for the user's multi-hub topology (each hub feeds the central attention map; routing is parallel, not serial).
5. **Relation to Bolton 2015.** Both papers identify a direct DA → orienting-map projection but disagree on the source nucleus (SNc here; diencephalic A13-like region in Bolton). The conservative reading — that *some* direct DA → priority-map projection is present in all vertebrates while the specific source nucleus varies — is exactly what the universality argument needs.

For the Recurrent ViT paper (2502.10955), this paper supports the choice (§6.7) to add an external, top-down feedback channel into the attention map rather than restricting feedback to feedforward features only. For PRISM v2 (`PRISM_V2_PROPOSAL.md`), it supports the proposed RL/value-feedback channel into the memory hub. For the architectural program more broadly, it is one of the two load-bearing citations under §5 ("Connection to literature") on whether a multi-hub system with a dopaminergic / RL-style modulator is biologically grounded.

## 8. Citations to follow

- redgrave_gurney1999_short_latency_sc_da — Redgrave & Gurney's classical argument that short-latency tectal-to-SNc signals carry salience, the input side of the loop closed by this paper.
- pombal_megias2003_lamprey_basal_ganglia — Anatomical characterization of lamprey basal ganglia that motivates the lamprey-mammalian homology claim.
- ericsson_grillner2013_lamprey_evolution — Grillner-lab synthesis of the conservation of basal-ganglia / tectal circuitry across vertebrates.
- saitoh_menard2007_tectum_da_modulation — Earlier evidence for dopaminergic modulation of tectal circuits in lamprey.
- suzuki_perez2019_lamprey_tectum_motor — Direct follow-up dissecting medial vs. lateral tectal sub-circuits and their differential DA modulation.
- mcelvain2021_specificity_dopamine_collaterals — Modern circuit-tracing characterization in rodents of how widely individual midbrain DA neurons collateralize, directly relevant to the claim of a single neuron branching to striatum and tectum.
