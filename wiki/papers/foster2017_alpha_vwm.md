---
id: foster2017_alpha_vwm
title: "Alpha-band activity reveals spontaneous representations of spatial position in visual working memory"
authors:
  - "Foster, Joshua J."
  - "Bsales, Emma M."
  - "Jaffe, Russell J."
  - "Awh, Edward"
year: 2017
venue: "Current Biology"
doi: "10.1016/j.cub.2017.09.031"
arxiv: ""
url: "https://www.cell.com/current-biology/fulltext/S0960-9822(17)31196-X"
tags:
  - visual-working-memory
  - spatial-attention
  - alpha-oscillations
  - inverted-encoding-model
  - eeg
  - binding
concepts:
  - top-down-feedback
  - bidirectional_hierarchical_feedback
  - multi_compartmental_memory
related:
  - awh_jonides2001_overlapping_attention_wm
  - vanede2019_gaze_internal_wm
  - schneegans_bays2017_feature_binding_wm
  - bays_husain2008_dynamic_resources
  - sreenivasan_desposito2019_delay_activity
  - stokes2015_activity_silent_wm
  - bahle2018_wm_attention_architecture
  - pertzov_husain2014_location_wm
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

# Alpha-band activity reveals spontaneous representations of spatial position in visual working memory

## 1. Abstract

> "An emerging view suggests that spatial position is an integral component of working memory (WM), such that non-spatial features are bound to locations regardless of whether space is relevant. For instance, past work has shown that stimulus position is spontaneously remembered when non-spatial features are stored. Item recognition is enhanced when memoranda appear at the same location where they were encoded, and accessing non-spatial information elicits shifts of spatial attention to the original position of the stimulus. However, these findings do not establish that a persistent, active representation of stimulus position is maintained in WM because similar effects have also been documented following storage in long-term memory. Here, we show that the spatial position of the memorandum is actively coded by persistent neural activity during a non-spatial WM task. We used a spatial encoding model in conjunction with EEG measurements of oscillatory alpha-band (8-12 Hz) activity to track active representations of spatial position. The position of the stimulus varied trial-to-trial but was wholly irrelevant to the tasks. We nevertheless observed active neural representations of the original stimulus position that persisted throughout the retention interval." (Foster, Bsales, Jaffe & Awh 2017, *Current Biology* 27(20):3216-3223, abstract.)

## 2. Why this matters for us

Foster et al. 2017 is the cleanest empirical demonstration that *spatial position is automatically encoded into visual working memory even when it is task-irrelevant*, and that this spatial code is *active throughout the retention interval* — visible in scalp alpha-band oscillations and decodable with an inverted encoding model. For the user's program, this is foundational on three fronts. First, it provides the cognitive-psychology warrant for the user's *spatial-grid memory architecture* ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md)): the memory state is organized as a spatial grid because *biological VWM is fundamentally spatially organized*, even for non-spatial content. Second, it validates the user's V1-paired shallow memory: spatial position should be encoded at the V1 level (high spatial resolution, fine retinotopic detail), exactly the architectural slot the user's $M_{fast}$ / $C^{(1)}$ memory occupies. Third, the demonstration that the alpha-band signature carries *target-vs-distractor distinction* (Exp 2a-c) provides empirical evidence for the *selectivity* of WM storage — only attended content gets actively maintained — which directly licenses the user's attention-gated memory-update architecture.

## 3. Key claims

1. Spatial position is *automatically* coded into active neural representations during WM storage of non-spatial features (e.g., color) — even when location is wholly task-irrelevant.
2. Alpha-band (8-12 Hz) scalp topography supports an inverted encoding model (IEM) that reconstructs location-tuned channel-tuning functions (CTFs) throughout the delay period.
3. The spatial code *persists* across the entire retention interval, not just at encoding — diagnostic of active maintenance rather than passive sensory lingering.
4. Spatial representations of *remembered targets* are stronger than those of *to-be-ignored distractors* — refuting a purely passive lingering-sensory account; selectivity is implemented at the storage level.
5. Findings support spatial position as a *scaffold* or *binding feature* for visual WM, even when irrelevant — non-spatial content is bound to space whether or not space is reportable.
6. Alpha activity provides a noninvasive readout of internal attentional/WM spatial state, opening a methodological window into VWM contents.
7. The target-vs-distractor effect emerges only after the initial encoding window (early sensory activity does not discriminate), localizing selectivity to maintenance rather than perception.

## 4. Methods

Five EEG experiments (Ns 10-17 after exclusions). Subjects held a non-spatial feature (color) in WM and reported it via continuous color-wheel response. Stimulus location varied across 8 angular bins but was task-irrelevant. Alpha-band power (8-12 Hz) topographies were entered into an inverted encoding model trained with leave-one-out cross-validation to reconstruct location-selective CTFs over the delay. Experiments 2a-c manipulated whether the lateralized stimulus was a target (to be remembered) vs distractor (to be ignored); Experiment 3 dissociated *active storage* from *passive lingering* by manipulating whether non-spatial features were actually stored vs merely perceived. The IEM is a critical methodological tool: it projects scalp topography into a hypothesized population-tuning space (8 spatial channels at 45° spacing), training on a subset of trials and testing on held-out trials, with CTF slope (linear regression of channel responses by distance from veridical position) as the readout of spatial selectivity.

## 5. Results

Headline quantitative results:

- **Alpha CTF spatial selectivity was reliably above chance throughout the delay** ($p < 0.01$, permutation tests) — diagnostic of active spatial maintenance.
- **Target CTF > distractor CTF in Exp 2a-c** ($p < 0.001$ in 2a, 2b) — selectivity is implemented at the maintenance level, not just at the sensory level.
- **In Exp 3, no target-distractor difference during early encoding** (0-500 ms, $p = 0.42$) but **reliable difference across the full delay** (150-1500 ms, $p < 0.01$) — implicating active storage rather than sensory carryover.
- **Behavioral mixture-model fits showed precise color recall and near-zero guessing**, validating that subjects were performing the WM task and storing the cued feature.
- **Eye-movement controls:** residual HEOG < 3 μV; gaze variation across positions < 0.05° of visual angle — ruling out oculomotor confounds.
- **Reconstruction used 8 spatial channels** (45° wedges); CTF slope quantified by linear regression of channel responses against angular distance from veridical position.
- **The spatial code emerges very early** (~150 ms post-stimulus) and persists for the full retention interval (~1500 ms) without significant decay, suggesting a robust active code.

## 6. Critique / limitations

The Foster-et-al finding is widely cited but has well-documented methodological and conceptual caveats.

- **IEM "reconstructions" recover the experimenter's chosen model rather than the underlying neural tuning** (Gardner & Liu 2019; Sprague et al. 2018) — the recovered CTFs depend on the assumed channel basis, and CTF slope changes can reflect SNR rather than representational changes.
- **Small samples** (n ≈ 10-17) with notable exclusion rates (up to 30%) limit statistical power and replicability; the magnitude of effects is small relative to inter-subject variance.
- **Alpha topography conflates spatial attention and spatial WM**; this paper cannot fully disentangle the two (Foster & Awh 2019 explicitly highlight this) — the alpha code might reflect ongoing covert attention to the remembered location rather than memory storage per se.
- **Position was always relevant at encoding** (foveation/saccade target) — the "task-irrelevant" framing applies only to the response, not to perceptual processing. Spatial information may be encoded automatically *because* the perceptual system uses it, not because WM "spontaneously" stores it.
- **Evidence that alpha-tracked code reflects storage per se vs covert attention to the remembered location remains debated** — the dissociation is methodologically hard.
- **All experiments use single-item WM loads**; multi-item generalization was demonstrated later (Sutterer et al. 2019) but with degraded selectivity.
- **Reverse inference from alpha to "WM content"** assumes a fixed mapping from oscillatory signal to representational state that may break with task changes.
- **No causal manipulation** (TMS/tACS) of alpha to test necessity — the evidence is correlational, not causal.

## 7. Connection to our work

Foster et al. 2017 is one of the most architecturally consequential VWM papers for the user's program because it directly validates the *spatial-grid* organization of the user's memory state.

**Touchpoint 1: spatial position is the binding feature — biological warrant for the spatial-grid memory.** The Foster-et-al finding that spatial position is automatically coded into VWM *even when it is task-irrelevant* is the biological warrant for the user's architectural commitment to a *spatial-grid* memory state ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md)). Each grid cell $C^{(t)}_{ij}$ in the user's memory holds the content at spatial position $(i, j)$ — even if the task does not require spatial location to be reported. The architectural choice has direct biological warrant: VWM is fundamentally spatially organized, so the user's memory state should be too. Memory architectures that *do not* organize content by spatial position (e.g., a single global pooled vector) discard the spatial scaffolding that Foster-et-al show is the actual organization of biological VWM.

**Touchpoint 2: shallow memory should be paired with V1-equivalent spatial resolution.** The retinotopic-precision of the alpha-band spatial code (8 angular bins covering the full visual field, each ~45°) is the empirical anchor for the user's [multi_compartmental_memory](../concepts/multi_compartmental_memory.md) commitment to *high spatial resolution in shallow memory*. The shallowest memory layer ($M_{fast}$ / $C^{(1)}$ at 12×12 spatial resolution) is the architectural slot that holds the fine-grained retinotopic information Foster-et-al document. The user's choice of V1-paired shallow memory is therefore biologically licensed, not merely an engineering convenience.

**Touchpoint 3: selectivity at storage — target-vs-distractor dissociation as architectural validation.** The Foster-et-al finding that target spatial code > distractor spatial code (and only after the initial encoding window) is the empirical signature of *attention-gated storage*: not all content reaches active maintenance, only attended content does. This validates the user's attention-modulated memory update: the attention map weights the contributions to the memory update, so attended content gets stored with high fidelity and unattended content gets stored with low fidelity. The architectural commitment to a multiplicative attention gate on the memory write directly reproduces the empirical selectivity Foster-et-al document.

**Touchpoint 4: persistent active maintenance — implications for the gate dynamics.** The Foster-et-al persistence finding — spatial code stable across 1500 ms — predicts that the user's $M_{fast}$ should hold spatial-content actively (with the gate keeping the state fresh, not letting it decay) across the relevant trial timescales. The user's gate-bias = 0 architectural choice ([concepts/gridcell_rnn.md](../concepts/gridcell_rnn.md) Refinement 3) achieves this: every step refreshes the state, preventing decay. This is the architectural instantiation of active maintenance.

**Touchpoint 5: alpha-band as the architectural analog of attention-modulated gain.** Alpha oscillations modulate cortical excitability — they are widely interpreted as a gain-control / suppression signal that locally enhances or suppresses processing. In the user's architecture, the *attention map* from the central self-attention plays an analogous role: it modulates which spatial locations / hubs get processed strongly versus weakly. The Foster-et-al alpha-band readout of spatial WM is therefore architecturally homologous to the *attention map* in the user's models. This suggests a concrete empirical analysis: the user's attention map at each spatial position should track the alpha-band IEM-derived spatial code in matched human experiments — a direct neural-model comparison.

**Touchpoint 6: spatial position as the *binding* feature — implications for object-feature representation.** The Foster-et-al claim that spatial position is the *binding* feature (non-spatial content is bound to location) connects to [schneegans_bays2017_feature_binding_wm](schneegans_bays2017_feature_binding_wm.md). The architectural implication is that the user's grid-cell memory state should hold *bound* representations: each grid cell $C^{(t)}_{ij}$ holds both *what* (channel content) and *where* (implicit in the grid index), and the binding is automatic by virtue of the spatial organization. The user's architecture therefore naturally implements the spatial-scaffolding binding mechanism Foster-et-al document, without requiring explicit binding operations.

**Touchpoint 7: convergence with van Ede on gaze-tracking-internal-WM.** Foster et al.'s alpha-band finding converges with van Ede, Chekroud & Nobre 2019 ([vanede2019_gaze_internal_wm](vanede2019_gaze_internal_wm.md)), which shows that microsaccades during the WM retention interval track the *remembered* spatial position. Both findings converge on the conclusion that *internal attention to WM contents* is spatially organized and behaviorally measurable. The user's architecture predicts this: the central attention substrate, when querying $M_{fast}$ for content at a particular spatial position, should produce a coherent spatial bias that an external observer could read off the attention map. The convergence across paradigms strengthens the architectural commitment to spatial-grid memory.

## 8. Citations to follow

- `foster_awh2019_alpha_spatial_attention_review` — *Curr Opin Psychol* — "The role of alpha oscillations in spatial attention"; the authors' modern synthesis. Not in seed.
- `sutterer2019_item_specific_delay_activity_plos_bio` — *PLOS Biology* — item-specific delay activity demonstrating concurrent storage of multiple active representations; the multi-item extension. Not in seed.
- `sutterer2019_alpha_ltm_neurophysiology` — *J Neurophysiology* — alpha-band tracking retrieval from LTM; the long-term-memory extension. Not in seed.
- `vanmoorselaar2018_distractor_alpha` — *J Neurosci* — distractor-related alpha effects. Not in seed.
- `adam_robison_vogel2018_alpha_lapses_cerebral_cortex` — *Cerebral Cortex* — alpha tracks momentary WM lapses; the behavioral-state extension. Not in seed.
- `boettcher_gresch_nobre_vanede2021_temporal_dynamics_elife` — *eLife* — temporal dynamics of spatial WM in alpha. Not in seed.
- `hakim_vogel2019_cda_alpha_dissociation_psych_sci` — *Psych Sci* — CDA vs alpha dissociation; the multi-component WM signature. Not in seed.
- [vanede2019_gaze_internal_wm](vanede2019_gaze_internal_wm.md) — human gaze tracks internal attention in WM; the converging modality. In seed.
- [schneegans_bays2017_feature_binding_wm](schneegans_bays2017_feature_binding_wm.md) — neural architecture for feature binding in VWM; the binding mechanism. In seed.
- [pertzov_husain2014_location_wm](pertzov_husain2014_location_wm.md) — location-WM interaction; the foundational behavioral evidence. In seed.
- `schneider_mertes_wascher2018_alpha_retrocued_wm` — *Sci Reports* — alpha lateralization for retro-cued spatial WM. Not in seed.
- `liu_theeuwes2022_alpha_load` — *JoCN* — alpha selectivity declines with load; the multi-item limit. Not in seed.
