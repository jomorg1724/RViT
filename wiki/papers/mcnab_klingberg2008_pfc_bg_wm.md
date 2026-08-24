---
id: mcnab_klingberg2008_pfc_bg_wm
title: "Prefrontal cortex and basal ganglia control access to working memory"
authors:
  - "McNab, Fiona"
  - "Klingberg, Torkel"
year: 2008
venue: "Nature Neuroscience"
doi: "10.1038/nn2024"
arxiv: ""
url: "https://doi.org/10.1038/nn2024"
tags:
  - working-memory
  - prefrontal-cortex
  - subcortical
  - human-neuroimaging
concepts:
  - cortico-basal-ganglia-thalamic-loops
  - priority-map
  - working-memory-persistent-activity
related:
  - haber2015_cbgtc_circuits
  - hikosaka2006_bg_reward_eyes
  - awh2006_attention_wm
  - gazzaley_nobre2012_topdown
  - oberauer2002_access_wm
  - panichello_buschman2021_shared_mechanisms
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_17
status: full
depth: full
last_updated: "2026-05-14"
---

# Prefrontal cortex and basal ganglia control access to working memory

> **Source note.** The original article is paywalled (Nature Neuroscience). The summary below is reconstructed from the PubMed-indexed abstract and from secondary descriptions in review articles by the Klingberg group and others; the methods and results sections follow the standard reading of the 2008 paper in the WM-filtering literature.

## 1. Abstract

Working memory capacity is limited and varies markedly across individuals. One source of that limit is the filter that selects which information from the environment is admitted to working memory storage in the first place. McNab and Klingberg used fMRI in humans performing a visuospatial working memory task with cued distractors to ask which neural structures implement that filter. They found that activity in the prefrontal cortex and basal ganglia — and most specifically the globus pallidus — preceded the encoding of relevant items into posterior parietal storage regions, and that the magnitude of this prefrontal/basal-ganglia activity predicted, on a trial-by-trial basis and across individuals, the degree to which distractors were excluded from parietal storage. The pre-encoding gating activity also predicted individual differences in working memory capacity measured behaviorally. The authors interpret the result as evidence that the basal ganglia, under prefrontal control, gate access to working memory in the same way they are known to gate access to motor output, and that variability in this gate is one of the proximate neural substrates of individual differences in working memory capacity.

## 2. Why this matters for us

This is the foundational empirical demonstration that the basal ganglia gate access to working memory in humans. The user's program ([threads/the_user_architectural_program.md](../threads/the_user_architectural_program.md) §5) commits to an RL hub modeled on the cortico-basal-ganglia-thalamic (CBGTC) loop ([concepts/cortico_basal_ganglia_thalamic_loops.md](../concepts/cortico_basal_ganglia_thalamic_loops.md)) that competes for control of a central self-attention substrate. McNab–Klingberg is the empirical functional counterpart to the anatomy laid out in Haber 2016 ([papers/haber2015_cbgtc_circuits.md](haber2015_cbgtc_circuits.md)): Haber tells us the CBGTC loop is wired to integrate reward, cognition, and motor signals; McNab–Klingberg shows the same loop is causally implicated in deciding what enters working memory at all.

For the multi-hub architecture this is direct evidence that an RL-style gating signal can shape which items occupy the limited capacity of a downstream attention/WM module — exactly the role the RL hub plays in the user's design. The paper also supplies a critical individual-differences anchor: the *strength* of the gating signal predicts behavioral capacity, which means filter recruitment is a graded, trainable property of the circuit and not a binary on/off mechanism. The user's RL hub, trained by gradient descent on a reward signal, should likewise exhibit graded modulation strength across stimuli and across training stages.

## 3. Key claims

1. A prefrontal–basal-ganglia network is active **before** working-memory encoding, with cue-period BOLD that peaks prior to stimulus onset. The timing pattern is consistent with the network selecting what *will* be encoded rather than maintaining what has already been encoded.
2. Activity in the globus pallidus (and to a lesser extent the caudate and PFC) at the cue/filter stage predicts, on a within-subject basis, the degree to which distractor items are excluded from posterior parietal working-memory storage.
3. Across subjects, the magnitude of this prefrontal–basal-ganglia filtering activity correlates with behavioral working-memory capacity: people with stronger gating signals show smaller capacity decrements when distractors are present, while people with weaker gating signals show capacity decrements proportional to the number of distractors as if they were storing both targets and distractors indiscriminately.
4. Posterior parietal cortex (specifically the intraparietal sulcus, IPS) acts as the working-memory storage substrate; its load-dependent BOLD activity is the dependent variable that the prefrontal/basal-ganglia filter modulates downward when filtering succeeds.
5. The architecture of the result is gating in the basal-ganglia sense: a top-down PFC signal selects which items the basal ganglia "allow through" to cortical storage, formally analogous to the BG's role in selecting which motor programs reach thalamus and cortex.
6. The filter is *separable* from storage. Capacity is not a single number but the product of (a) storage volume and (b) filter selectivity; individual differences in WM capacity can be decomposed into these two factors and the globus-pallidus signal is a marker of factor (b).
7. The result implies that working-memory capacity is partly determined by an attentional control mechanism rather than by the maintenance hardware alone — collapsing a previously sharp boundary between "attention" and "WM" research.

## 4. Methods

Healthy adult human subjects performed an event-related fMRI experiment using a delayed-recall visuospatial working-memory task. The trial timeline had four phases:

1. **Cue (filter / no-filter).** A brief instruction cue indicated either that all upcoming items would be targets to remember ("no-filter" condition) or that only a colour-defined subset would be targets and the remainder would be distractors to ignore ("filter" condition).
2. **Stimulus array.** After a short interval, an array of colored items was presented briefly. In the filter condition the array contained both target-colored and distractor-colored items at fixed total set size; in the no-filter condition all items were target-colored.
3. **Delay.** A blank-screen retention interval during which the targets had to be maintained.
4. **Probe.** A single test item appeared and the subject reported (forced-choice) whether it matched one of the remembered target locations.

The cue therefore allowed the subject to prepare a filter *before* the items appeared, and total memory load was matched across conditions while distractor load varied — the crucial design feature that isolates filtering from sheer maintenance demand.

The key contrast was the BOLD response during the **cue/filter interval** — before any items were shown — between filter and no-filter trials. The authors reasoned that any region whose activity scales with the demand to exclude irrelevant items at this stage is implicated in the filter operation itself rather than in encoding or maintenance. Three further analyses sharpened the inference:

- **Storage as a function of filter activity.** Posterior parietal (intraparietal-sulcus) BOLD during the delay was taken as an index of how much information was actually stored, calibrated against a separate set-size manipulation in the no-filter condition that established the dose–response curve between number of stored items and parietal BOLD. The authors regressed delay-period parietal activity against cue-period prefrontal/basal-ganglia activity to test whether stronger filter activity predicted *less* irrelevant storage.
- **Individual-differences regression.** A behavioral capacity measure (a working-memory span estimate from a separate calibration session) was regressed against the cue-period BOLD signal in PFC, caudate, and globus pallidus to test whether subjects with greater filter recruitment also had greater behavioral capacity.
- **Anatomical ROI definition.** Basal-ganglia ROIs (caudate, putamen, globus pallidus) were defined from each subject's structural scan rather than from a group atlas, which mitigates the alignment problem typical for small subcortical structures and lends extra credibility to the pallidum-specific finding.

## 5. Results

- **Cue-period activation.** A network including left middle frontal gyrus / dorsolateral PFC and the basal ganglia (most prominently the globus pallidus, with additional caudate involvement) was significantly more active during the filter cue than the no-filter cue, with peak responses preceding stimulus onset. The activation pattern was preparatory rather than reactive.
- **Frontal localization.** The PFC activation centered on left middle frontal gyrus / dorsolateral PFC, consistent with the broader literature implicating dlPFC in top-down control of attention and WM. The lateralization to the left hemisphere is congruent with subjects performing a verbalizable spatial task.
- **Posterior parietal storage scales with filter strength.** Subjects (and trials) with greater prefrontal/basal-ganglia cue-period activity showed less parietal storage activity for distractor-containing arrays — interpreted as fewer distractors having reached storage. Conversely, subjects with weaker filter activity showed parietal BOLD that scaled with total array size (targets + distractors), as if they were storing both targets and distractors and paying the capacity cost.
- **Globus pallidus predicts individual capacity.** Cue-period BOLD in the globus pallidus correlated significantly with the behavioral working-memory capacity score across subjects. The PFC and caudate effects were in the same direction but the globus-pallidus correlation was the most robust, identifying the pallidum as the most discriminating node in the filter network and the proximate substrate of individual capacity differences.
- **Timing.** The filter activation peaked before the items to be remembered appeared, supporting a preparatory / gating interpretation rather than a maintenance or retrieval one. The temporal dissociation between the PFC/BG cue-period response and the parietal storage-period response is what licenses the causal-shaped reading: the gate fires, then storage occurs.
- **Behavior.** Higher filter recruitment was associated with smaller filter cost (i.e., smaller drop in performance when distractors were added), consistent with the activity being functionally protective of capacity.
- **No filter-related parietal activity at cue.** The parietal cortex itself did not show the cue-period filter response; its response was driven by storage demands during the encoding and delay phases. This argues against a parietal-only account of filtering: the gate is computed elsewhere, and parietal cortex shows only the *consequences* of gating in the form of reduced storage of irrelevant items.

These quantitative correlations between an explicit "exclude distractors" cue, a prefrontal–basal-ganglia preparatory signal, and posterior-parietal storage are what make the paper's gating claim causal-shaped rather than purely correlational. The result is robust enough that the McNab–Klingberg paradigm has since become a standard probe for clinical populations (ADHD, schizophrenia, Parkinson's) in which filter failures are hypothesized.

Two specific patterns deserve emphasis for our purposes. First, the *parietal* storage signal is the index of WM content, while the *pallidum* signal is the index of the gate — the spatial dissociation between content and gate is preserved in the user's architecture, where the central self-attention map is the content and the RL hub's modulation is the gate. Second, the filter manipulation matched total array size between filter and no-filter conditions; the difference therefore *cannot* be explained by raw sensory load and must reflect a top-down decision about what to admit. This eliminates the most obvious confound in any "gate" claim.

## 6. Critique / limitations

The result is correlational; fMRI cannot directly demonstrate that globus-pallidus activity *causes* exclusion from parietal storage. Subsequent causal evidence in patients (Parkinson's disease, basal-ganglia stroke) and from pharmacological manipulation of dopamine has been broadly consistent but is outside this paper's scope. A skeptic could in principle argue that PFC/BG activity is downstream of an even earlier filtering decision rather than the filter itself.

The spatial resolution of fMRI is poor for distinguishing internal globus-pallidus subdivisions (GPi versus GPe), which is exactly the distinction needed to discriminate direct-pathway (release) versus indirect-pathway (suppression) gating mechanisms. The authors interpret their pallidum signal in line with a direct-pathway "release-from-inhibition" account by analogy to motor gating, but cannot directly confirm it. Without GPi/GPe resolution, the paper cannot distinguish "open the gate to targets" from "close the gate to distractors" as the operative computation, and the user's architecture would benefit from knowing which it is.

The task uses only visuospatial WM with discrete colored items in a brief delay paradigm. Whether the same prefrontal–basal-ganglia filter operates for non-spatial content, for proactive interference inside WM (as opposed to filtering at encoding), or for longer maintenance intervals is not established here. Subsequent work in the same line (Awh & Vogel; Vogel, McCollough & Machizawa) has generalized the effect to other modalities, but the original paper's scope is narrow.

The "individual differences" correlation is across a modestly-sized sample (~25 subjects) and a single behavioral capacity score. Replication in larger samples and with more behavioral measures has been carried out by the Klingberg group and others; the original effect size should be cited cautiously and any *quantitative* use in our work should reference the replications rather than the 2008 numbers alone.

The paper does not engage with the dopaminergic teaching signal: it shows that the gate exists and that it varies across individuals, but not how the gate is learned or tuned. The reinforcement-learning interpretation is left implicit and depends on theoretical work elsewhere (Frank et al. 2001; O'Reilly & Frank 2006 PBWM model) to connect the gate to a reward-prediction-error training signal.

The paper does not address the *content* of the filter — whether the gate operates on spatial location, feature, or object-level representations. The cue in the filter condition specified targets by color, so the result is consistent with a feature-based gate, but a spatial-only or location-based reading cannot be excluded from the design.

## 7. Connection to our work

This paper is one of the load-bearing empirical anchors for the **RL hub** in the user's multi-hub multi-objective system ([threads/the_user_architectural_program.md](../threads/the_user_architectural_program.md) §5). Concretely:

- **The BG-as-gate analog.** The user's design places competition between hubs (MSI, RL, VAE) at the level of a shared self-attention substrate, with each hub contributing per-token Q/K/V modulations through the Feedback Transformer ([threads/the_user_architectural_program.md](../threads/the_user_architectural_program.md) §1, §5 "Formal account of the competition"). McNab–Klingberg shows that, biologically, exactly this kind of pre-encoding gating signal is implemented by a prefrontal–basal-ganglia loop. The RL hub's role — biasing the central attention map toward task-relevant items via learned, reward-shaped weights — is the computational job description the globus pallidus is doing in this fMRI study. In Feedback-Transformer terms, the BG output projecting via thalamus to cortex is the closest biological analog of the RL hub's $c^{(\text{RL})}_q, c^{(\text{RL})}_k$ contributions to the central Q/K projections.
- **Pairs with Haber 2016 as anatomy + function.** Haber ([papers/haber2015_cbgtc_circuits.md](haber2015_cbgtc_circuits.md)) supplies the wiring diagram of the CBGTC loop; McNab–Klingberg supplies the function for the WM/attention case. Together they give the user's RL hub a complete anatomical+functional precedent: cortex provides the candidate items, dopamine-modulated striatal plasticity shapes the gating policy, the pallidum issues the gate signal, and thalamic relays close the loop back onto cortical storage. The two papers should be cited as a pair whenever the user's program defends the BG-modelled RL hub.
- **Central attention gating, not just motor gating.** The classical BG story is motor selection (Mink 1996; Hikosaka — [papers/hikosaka2006_bg_reward_eyes.md](hikosaka2006_bg_reward_eyes.md) — for saccades). McNab–Klingberg generalizes that gating story to cognition: the same loop architecture gates access to working memory. This is the empirical license for the user's architectural claim that an RL-style hub can sit *upstream of* the central self-attention substrate and decide what gets through, not merely *downstream* selecting an action. Without McNab–Klingberg, the "BG gates attention" claim is a theoretical extrapolation from motor neuroscience; with it, the extrapolation is closed and the user's design is implementing a documented biological motif.
- **Limited capacity as a competition prize.** The user's competition-emergent-PC framing ([threads/the_user_architectural_program.md](../threads/the_user_architectural_program.md) §5) requires that the central attention map is a scarce resource that hubs compete for. McNab–Klingberg's individual-differences result — that capacity is limited, that the limit is set by the filter, and that subjects vary in filter strength — is direct evidence that the brain treats WM access as exactly such a scarce resource gated by a learned controller. The user's architecture inherits that interpretation almost literally: the central self-attention map plays the role of WM, and the RL hub plays the role of the McNab–Klingberg filter.
- **Preparatory, not reactive, gating.** The most distinctive empirical feature of the paper is that the PFC/BG filter signal fires *before* the items appear. In the user's design this maps onto a hub providing its modulation to the attention map *at the same time as* (or before) the sensory tokens arrive at self-attention — i.e., the RL hub's memory state $C^{(\text{RL})}$ contributes to Q/K *prior* to the softmax computing competition between sensory tokens. This rules out a purely post-hoc reweighting story and motivates designs in which the RL hub's state is computed on the previous step and is *ready* by the time current-step tokens enter.
- **Connection to the Recurrent ViT line.** The ViT paper's reference 17 (the seed source for this entry) treats McNab–Klingberg as biological motivation for the recurrent-memory feedback into self-attention. In the Recurrent ViT (2502.10955) the single memory state $H^{(t-1)}$ plays the role of the gate; the McNab–Klingberg result is one of the strongest pieces of biological evidence that a learned controller modulating attention from outside the cortical hierarchy is a feature of real cognitive systems, not an engineering convenience. The §6.7 ablations on tokens / additive / multiplicative feedback variants can be read as exploring different mathematical implementations of the same gating operation.
- **Connection to PRISM v2.** PRISM v2's hierarchical FiLM modulation (`PRISM_V2_PROPOSAL.md` §3.4) injects memory-driven gain into the feature stack. McNab–Klingberg motivates extending that single-source modulation toward a separate, RL-trained gate operating on the attention map itself rather than (or in addition to) on the feature stack — closer to the user's full Feedback Transformer commitment. The clinical observation that filter failures are diagnostic of ADHD/schizophrenia/Parkinson's also suggests that PRISM-style change-detection benchmarks could be productively reframed as filter-failure benchmarks, with intentional distractor manipulations probing whether the model's recurrent state actually gates or merely accumulates.
- **A falsifiable bridge from architecture to neural data.** The user's competition-emergent-PC test plan ([threads/the_user_architectural_program.md](../threads/the_user_architectural_program.md) §5 "Empirical test plan") proposes decoding inter-hub coordination from a multi-hub model. McNab–Klingberg gives a direct neural prediction with which such a model could be confronted: in a trained multi-hub model, *the RL hub's state must contain a representation of upcoming-trial distractors that predicts which sensory tokens will be attenuated in the attention map* — analogous to the globus-pallidus cue-period signal predicting parietal storage. This is a concrete, testable bridge between the architecture and the biological data.
- **Capacity as a learned hyperparameter.** McNab–Klingberg's individual-differences finding implies that filter strength is not a fixed parameter but varies as a function of training history and dopaminergic tone. In the user's architecture, this corresponds to the RL hub's parameters being trainable on a reward signal — i.e., a hub with more training (or higher gain on its reward signal) should produce stronger attention-map modulation. The user's program inherits a quantitative prediction here: ablation studies that reduce the RL hub's training signal should produce a graded reduction in distractor exclusion in the model, mirroring the human individual-differences result.

The bottom line: this paper turns the abstract claim "the brain has an RL gate on attention" into a concrete, regionally-specific, empirically-anchored claim. For the user's program it is one of the small set of papers that justify treating the RL hub as a first-class architectural component rather than a speculative add-on.

## 8. Citations to follow

- `mink1996_bg_motor_selection` — Mink's canonical "BG select competing motor programs" model, on which McNab–Klingberg's WM-gating analogy rests. Not in seed.
- `frank2001_bg_wm_gating` — Frank, Loughry & O'Reilly's computational model that explicitly proposed BG gating of PFC working memory. Direct theoretical antecedent. Not in seed.
- `oreilly2006_pbwm` — O'Reilly's prefrontal-cortex-basal-ganglia working-memory (PBWM) model, the formal RL account of BG gating of WM. The most direct theoretical companion to this paper. Not in seed.
- `klingberg2010_wm_training` — follow-up by the same group on training-induced changes in the same filter network, providing a plasticity-side complement to the cross-sectional individual-differences result here. Not in seed.
- `vogel_machizawa2004_cda_capacity` — the CDA marker of individual WM capacity, the EEG analog of the parietal-storage measure used here. Not in seed.
- `vogel_mccollough_machizawa2005_filtering` — the behavioral filtering-cost paradigm that this fMRI study operationalizes. Not in seed.
- `mcnab_klingberg2008_followups` — clinical extensions of the same paradigm in ADHD and Parkinson's that strengthen the causal reading. Not in seed.
- `haber2015_cbgtc_circuits` — anatomical companion, in seed.
- `hikosaka2006_bg_reward_eyes` — BG gating of saccades, the other major BG-gating system. In seed.
- `awh2006_attention_wm` — the conceptual sibling on attention–WM overlap. In seed (related).
- `gazzaley_nobre2012_topdown` — broader review of top-down filtering of perception and WM, in which this paper figures centrally. In seed (related).
- `panichello_buschman2021_shared_mechanisms` — shared neural mechanisms between attention and WM, with prefrontal recordings extending the McNab–Klingberg account to single-unit resolution. In seed (related).
