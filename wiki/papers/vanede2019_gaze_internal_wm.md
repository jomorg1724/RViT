---
id: vanede2019_gaze_internal_wm
title: "Human gaze tracks attentional focusing in memorized visual space"
authors:
  - "van Ede, Freek"
  - "Chekroud, Sammi R."
  - "Nobre, Anna C."
year: 2019
venue: "Nature Human Behaviour"
doi: "10.1038/s41562-019-0549-y"
arxiv: ""
url: "https://www.nature.com/articles/s41562-019-0549-y"
tags:
  - working-memory
  - visual-attention
  - psychophysics
concepts:
  - attentional-spotlight
  - working-memory-persistent-activity
  - retinotopy
  - top-down-feedback
  - cueing-effect
related:
  - kiyonaga_egner2013_wm_internal_attention
  - awh2006_attention_wm
  - hoffman2016_attention_eye_movements
  - gupta_sridharan2024_presaccadic_change
  - gazzaley_nobre2012_topdown
  - panichello_buschman2021_shared_mechanisms
  - olivers2011_wm_states_attention
  - bisley_goldberg2010_parietal_priority
  - bisley_mirpour2019_priority_map
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_22
status: full
depth: full
last_updated: "2026-05-16"
---

# Human gaze tracks attentional focusing in memorized visual space

## 1. Abstract

When selecting an item from visual working memory, gaze becomes biased in the direction of the memorised location of that item — despite the fact that there is nothing physically present to look at, location was never asked about, and the memoranda were defined by non-spatial features (orientation, colour). Across four eye-tracking experiments (≈ 20–25 participants each, EyeLink 1000 at 1 kHz), van Ede, Chekroud & Nobre show that this gaze bias is composed of small but reliable shifts (microsaccade-scale, on the order of 0.1–0.2° of visual angle) that emerge ~300–600 ms after the central probe instructing which item to report and persist until response onset. The bias is observed only when the relevant item was not already in attentional focus: when an informative retro-cue was used to pre-focus the relevant item during the delay, the post-probe gaze bias disappeared. Across-trial variation in the gaze bias predicted across-trial variation in the working-memory readout benefit conferred by selecting that item. The authors conclude that the same oculomotor circuitry that supports covert deployment of *external* spatial attention also tracks the *internal* focusing of attention within working memory — internal attention is implemented in the same spatial / retinotopic coordinate system as external attention, even when the original stimulus is no longer present.

## 2. Why this matters for us

This paper is the cleanest behavioural demonstration that *internal* selection in working memory uses the *same spatial coordinate system* as *external* covert spatial attention, even after the inducing stimulus is gone. For the user's program that is direct empirical support for the architectural commitment that the recurrent ViT's spatial attention map ($\alpha_{ij}$ over patches) and the recurrent memory state $H^{(t)}$ live on the *same patch grid* and re-target the same locations when the input changes (a memorised location is "selected" by reactivating the attention map at its retinotopic coordinates). It also extends the Kiyonaga & Egner 2013 ([kiyonaga_egner2013_wm_internal_attention](kiyonaga_egner2013_wm_internal_attention.md)) "WM = internal attention" framing from a theoretical claim about *shared resources* to a measurable claim about a *shared spatial substrate*: not only do WM and attention share capacity, they share retinotopic geometry.

## 3. Key claims

1. **Gaze shifts toward memorised locations during internal selection.** When a central probe instructs participants to retrieve an item from VWM, gaze biases toward the location that item *used to occupy*, even though location was never task-relevant and the item is gone.
2. **The bias is spatial, not visual.** Nothing is on the screen at the biased location; the bias indexes retrieval of an *internal* representation of where the item was, not a re-fixation of a present object.
3. **The bias is composed of microsaccade-scale shifts.** Mean shift magnitudes ≈ 10–13% of the original eccentricity (≈ 0.15° at 5.7° eccentric stimuli); the dominant statistical effect is on *shift frequency*, not amplitude.
4. **The bias indexes focusing, not maintenance.** When a retro-cue during the delay pre-focuses the relevant item, the post-probe bias is abolished — the bias appears specifically when attention must be *redirected* to an unfocused memorandum.
5. **The bias is feature-general.** Equivalent biases are observed when the probed feature is orientation and when it is colour; the spatial reactivation does not depend on the feature dimension being interrogated.
6. **The bias predicts behaviour.** Across-trial gaze bias magnitude is correlated with the working-memory readout benefit on the same trial: stronger gaze tracking → better recall precision.
7. **Oculomotor engagement follows attention, not the other way around.** A control manipulation that mechanically displaced fixation by 0.5° produced gaze shifts of comparable magnitude but did not improve performance or reduce subsequent biases — i.e., gaze biases are a *read-out* of internal attention, not a cause of it.
8. **Internal and external attention share the same oculomotor substrate.** The simplest account is that the FEF / SC / parietal circuitry that drives covert external spatial attention is recruited identically when attention is deployed within working memory's spatial map.
9. **The bias is item-specific.** Two-item arrays produce biases toward the *probed* item's location, not toward the array centroid — the spatial reactivation indexes the selected item rather than the spatial extent of the memory array as a whole.

## 4. Methods

**Participants and apparatus.** Four eye-tracking experiments with healthy young adults (Exp 1, n=23 after exclusions; Exps 2–4, n=20 each). EyeLink 1000 monocular tracker at 1000 Hz, chin-rest at ~95 cm viewing distance, custom 7-position calibration after each block (5.7° spacing).

**Core task (Exp 1).** Participants encoded a memory array of two coloured, oriented bars at lateral positions (left / right of fixation, 5.7° eccentric). After a retention interval (~2 s), a central probe — a colour change at the fixation cross — indicated *which* of the two items to report. On half of trials the probed feature was orientation (adjust a probe bar to match the remembered orientation); on the other half it was colour (adjust a colour wheel to match the remembered colour). Crucially, **location was never the probed feature** and was never reported; the colour-of-the-fixation-cross simply identified one of the two memoranda.

**Retro-cue task (Exp 2).** A four-item array was used; midway through the retention interval an informative cue (100%-valid colour cue) or a neutral cue (uninformative grey) appeared centrally. The probe at retrieval was the same as in Exp 1. The logic: if the post-probe gaze bias reflects the *focusing* of an unfocused item, informative retro-cues that pre-focus the relevant item during the delay should *abolish* the post-probe bias.

**Control experiments (Exps 3–4).** Mechanical displacement of fixation by 0.5° (matched to the empirically observed gaze-bias magnitude); tests of feature generality across orientation-only and colour-only probes.

**Analyses.** Time-resolved horizontal gaze position locked to the probe, contrasted between *probed-left* and *probed-right* trials. Cluster-based permutation tests for time-course differences (the standard non-parametric correction for the multiple-comparisons problem in dense-sampled time series). Decomposition of bias into shift frequency × shift magnitude, with shifts detected by a velocity-threshold criterion adapted from Engbert & Kliegl 2003. Within-subject correlations of trial-by-trial gaze bias with recall precision (continuous reproduction error for orientation; circular distance for colour). Eye-tracking exclusion criteria: trials with blinks within the analysis window, or fixation deviations exceeding 2° from the central cross during the encoding or delay phase, were excluded prior to analysis.

**Statistical model.** Mixed-effects analyses with participant as random effect, item-location and trial-condition as fixed effects. Cohen's $d$ reported for pairwise contrasts.

## 5. Results

- **Direction of bias.** When the probed item had occupied the left, gaze shifted leftward; when it had occupied the right, gaze shifted rightward. Peak bias ≈ 2.62% of the 5.7° eccentricity, i.e. ~0.15° of visual angle.
- **Composition of bias.** Dominated by shift *frequency*: 0.245 toward-shifts per trial vs 0.096 away-shifts per trial ($t(19) = 8.058$, $p < 0.001$, $d = 1.68$). Modest amplitude effect: 12.47% toward vs 10.38% away ($t(19) = 3.576$, $p = 0.002$, $d = 0.746$).
- **Timing.** Bias onset ≈ 300–600 ms after the central probe, peaking before the response — matching the time-course of voluntary covert attention deployment.
- **Retro-cue abolition.** Informative cues during the delay eliminated the post-probe bias (cluster-based permutation $\Sigma T = -4516.7$, $p < 0.001$). Neutral cues left it intact.
- **Feature generality.** Significant bias for orientation reports ($\Sigma T = 3522.5$, $p < 0.001$) and for colour reports ($\Sigma T = 4065.3$, $p < 0.001$); statistically indistinguishable in magnitude.
- **Performance correlation.** Trials with stronger gaze bias toward the probed item's location showed greater recall benefit from selecting that item; the relationship was within-subject and significant.
- **Causal direction.** Externally induced 0.5° fixation displacements produced gaze shifts of comparable magnitude but did *not* improve recall precision and did *not* reduce the post-probe bias on subsequent trials — gaze tracking is downstream of, not driving, internal attentional focusing.
- **Memorandum specificity.** The bias is item-specific, not array-general: with two items at distinct locations, the gaze bias indexes the *probed* item's location, not the centroid of the array. This rules out a "spatial attention spreads over all memorised locations" account.
- **No bias on neutral trials.** When the central probe was uninformative (no item was selected), no gaze bias emerged. The bias is therefore tied to the *selection event*, not to general memory-maintenance demands.

## 6. Critique / limitations

- **The bias is small.** ~0.15° of visual angle at 5.7° eccentricity. This is below the resolution of most eye trackers and is barely detectable in single trials. Replication requires high-quality eye tracking and many trials per participant.
- **The probed-feature design constrains generalisation.** Location was never task-relevant, but the *encoding* phase made location available; the bias might reflect rehearsal of an encoded-but-unprobed feature rather than a generic spatial-indexing-of-memory operation. The retro-cue control rules out simple maintenance-bias accounts but does not rule out a strategic "use-the-space-to-organize-memory" account.
- **Microsaccades vs covert attention dissociations.** Hafed & Clark (2002) and subsequent work argues microsaccade direction can be dissociated from covert attention under some conditions. Van Ede et al. show *correlation* between gaze and memory performance, but stronger causal claims (e.g., FEF / SC microstimulation during the delay) would be needed to confirm shared circuitry.
- **No neural recording.** The "shared oculomotor substrate" claim is inferred behaviourally. Subsequent work (van Ede et al. 2020, *Trends Cogn Sci*; and the literature reviewed in [hoffman2016_attention_eye_movements](hoffman2016_attention_eye_movements.md)) is consistent with shared FEF / SC involvement, but the present paper does not directly demonstrate it.
- **Two-item / four-item arrays only.** Whether the gaze-tracks-WM phenomenon scales to larger working-memory loads (where item-level spatial indexing might compete with itself) is untested here.
- **No predictive-coding or model-level account.** The paper is purely empirical; it does not commit to any computational mechanism for why oculomotor circuitry would be recruited for internal selection. The shared-resource framing of Kiyonaga & Egner 2013 and the priority-map literature ([bisley_goldberg2010_parietal_priority](bisley_goldberg2010_parietal_priority.md), [bisley_mirpour2019_priority_map](bisley_mirpour2019_priority_map.md)) supply candidate mechanisms but are not engaged with directly.
- **Non-spatial WM is not addressed.** The design uses laterally-arranged spatial arrays. Whether the gaze-tracks-WM effect generalises to memoranda that are not spatially anchored (verbal WM, abstract category WM, semantic WM) is left open. If the effect is genuinely about a shared spatial substrate, it should be *absent* when the to-be-remembered material has no encoded location — a strong falsification test that this paper does not run.
- **Single-trial readout.** The trial-by-trial correlation with recall precision is statistically significant in aggregate, but the per-trial gaze signal is too small to support reliable single-trial decoding of *which* item is being attended. The bias is best understood as a population-average index of internal selection, not a single-trial neural-readout proxy.

## 7. Connection to our work

Van Ede, Chekroud & Nobre 2019 supplies the load-bearing behavioural evidence that *internal* working-memory attention shares the *spatial coordinate system* of external visual attention — even when the inducing stimulus is gone and location was never task-relevant. This is more than a "shared resource" claim (Kiyonaga & Egner 2013); it is a claim about *shared geometry*. Three threads of our program rest on it.

**Spatial persistence of the recurrent ViT's attention map.** The recurrent ViT (2502.10955) maintains a per-patch memory state $H^{(t)}$ on the same spatial grid as the patch-tokens. When the input frame changes — even when the inducing stimulus is gone — the attention map computed at $t+1$ retains information about the previous frame's spatial structure because $H^{(t)}$ is fed back into the Q / K / V projections. Van Ede et al.'s gaze-tracks-WM result is the cognitive-science analog of this: even when the inducing stimulus is removed, the spatial coordinates of the previous attentional focus are *reactivated* when an internal probe demands it. The Recurrent ViT predicts this behaviour by construction; van Ede et al. confirm that real human cognition does the same thing.

**The cue-selection mechanism in change detection.** The change-detection paradigm in the Recurrent ViT paper uses a cue at time $t$ that drives attention to a specific spatial location at time $t+1$. Van Ede et al. show that internal selection from a memorised array works analogously: a central probe (no spatial information) drives the gaze (a measurable correlate of spatial attention) to the memorised location. The Recurrent ViT's architectural commitment — that the *same* attention map serves both "where to look in the input" and "where the memorandum is in the maintained state" — is mechanistically endorsed by this paper.

**Connection to internal-attention literature anchors.** Together with [kiyonaga_egner2013_wm_internal_attention](kiyonaga_egner2013_wm_internal_attention.md) (theoretical unification of internal and external attention), [awh2006_attention_wm](awh2006_attention_wm.md) (behavioural overlap of attention and WM), [hoffman2016_attention_eye_movements](hoffman2016_attention_eye_movements.md) (premotor-theory linkage of attention and eye movements), and [gupta_sridharan2024_presaccadic_change](gupta_sridharan2024_presaccadic_change.md) (pre-saccadic attention shifts on change-detection tasks), the present paper closes the loop: WM is internal attention (Kiyonaga & Egner), internal attention uses the oculomotor system (van Ede et al.), the oculomotor system *is* the spatial-attention system (Hoffman; premotor theory), and the same circuit drives change-detection performance (Gupta & Sridharan). The Recurrent ViT's design — a single spatial attention map driving both perception and memory, modulated by feedback from the recurrent state — is the architectural compression of this whole behavioural chain.

**Implication for PRISM v1 and v2.** PRISM v1's prediction-error gating uses a single spatial precision map ($\Sigma_{t}$) that serves both inference (where prediction error is large) and memory update (which patches to write). The "shared spatial substrate" claim is implicit in this design. Van Ede et al.'s result that gaze-tracks-WM-in-the-absence-of-stimulus is empirical license for this commitment: human attentional and mnemonic substrates *do* share retinotopic geometry, so an architecture that conflates them is biologically plausible. PRISM v2's hierarchical FiLM with slow / fast memory ([PRISM_V2_PROPOSAL.md] §3.3 / §3.4) inherits this same shared-geometry commitment.

**The "competition for shared resource" framing.** In the user's multi-hub system (see [the_user_architectural_program](../threads/the_user_architectural_program.md) §1.5), hubs compete for control of a central spatial attention map. Van Ede et al.'s result that internal selection from WM uses the same map that drives gaze is direct evidence that the brain implements precisely this kind of shared-substrate competition — sensory selection and mnemonic selection contend for the same spatial-attention resource.

**Open empirical question.** The Recurrent ViT could be probed analogously: present a multi-item array at $t$, remove it, present a non-spatial cue at $t+1$, and measure whether the model's attention map at $t+1$ peaks at the *previous* location of the cued item. If yes, the model recapitulates van Ede et al. If no, this is a place the model and the data diverge and the architecture needs revision. This is a concrete, executable test of the shared-geometry commitment.

**Connection to the Feedback Transformer primitive.** The Feedback Transformer ([the_user_architectural_program](../threads/the_user_architectural_program.md) §1) projects the recurrent state $C_i$ into per-state $Q_{C_i}, K_{C_i}, V_{C_i}$ and combines these element-wise with the sensory projections before the softmax. The biological cash-out is that the recurrent feedback can re-target the attention map even when the sensory input changes, because $K_{C_i}$ carries the spatial *coordinates* of the previous attentional focus into the next attention computation. This is precisely the architectural mechanism by which the model produces the van-Ede-style effect: when the input changes (the memory array is gone), the model's attention still peaks at the old spatial location because the recurrent feedback's $K$ vectors encode that location. Without the Feedback Transformer's full Q / K / V structure — using e.g. FiLM modulation only at the feature stack as PRISM v1 does ([THESIS.md] §2.4) — the model could not as cleanly re-target attention to a *memorised* location, because the recurrent signal would only modulate features, not query / key vectors that determine *where* to attend. Van Ede et al. therefore *supports the Feedback Transformer over the FiLM-only alternative*: the data demand a mechanism where memory drives spatial attention, not just feature modulation.

**Implication for the iterative variational encoder-decoder.** In the $n_{FR} \to n_{BR}$ rollout ([the_user_architectural_program](../threads/the_user_architectural_program.md) §4), the decoder reconstructs the image iteratively from a guide $H_{n_{FR}}$. If the guide encodes a spatial attention map over patches, each iteration's reconstruction proposal is effectively a "fixation" within the maintained representation. The van Ede et al. result that internal selection drives the oculomotor system suggests that *the iterative decoder's reconstruction trajectory should look like a sequence of internal fixations* — i.e., the decoder's spatial focus at each $\tau$ should peak at a coherent location and shift in a trajectory-like manner across iterations. This is a testable model-behavioural prediction the user's program can make about its own decoder, motivated directly by this paper's empirical signature.

**Retro-cue abolition as an architectural diagnostic.** Van Ede et al.'s Exp 2 finding that a retro-cue *abolishes* the post-probe gaze bias has a direct architectural analog: if the recurrent ViT receives a spatial cue *during* a delay frame (i.e., the spatial focus has already been re-targeted within $H^{(t)}$), then there should be no further spatial-attention re-targeting when the final retrieval probe arrives — because the attention map is already where it needs to be. A model that *does* show further re-targeting on the probe frame in this condition would be over-using its attention mechanism relative to what humans do, and would suggest the model under-uses its recurrent state for predictive pre-allocation of attention. This is another concrete experimental match between the human behavioural signature and a testable model property.

**Why "shared spatial substrate" is stronger than "shared resource".** The Kiyonaga & Egner 2013 framing treats attention and WM as drawing on a single *quantity* of resource — a scalar budget that can be split between selection and maintenance. Van Ede et al.'s contribution is to show that the shared substrate is *spatially structured*: it is not just a budget but a topographic map. This matters for the user's architectural choices because a scalar-resource architecture would be content with a single recurrent-state vector that modulates a separate attention head; a topographic-substrate architecture demands that the recurrent state itself live on the same patch grid as the attention map, so that the *location* of attention and the *location* of memory contents are the same data structure. The recurrent ViT's per-patch $H^{(t)}$ is exactly this structure; PRISM v1's spatial precision map $\Sigma_t$ also satisfies it; a transformer with a single global memory token would not.

## 8. Citations to follow

- `hafed_clark2002_microsaccades_attention` — original demonstration that microsaccade direction tracks covert spatial attention. The methodological precursor for van Ede et al.'s analysis. Not yet in seed.
- `engbert_kliegl2003_microsaccades` — characterisation of microsaccade dynamics; methodological reference. Not yet in seed.
- `van_ede_nobre2023_attention_in_wm_review` — *Annual Review of Psychology* review by the same lab summarising the gaze-tracks-WM literature in its broader theoretical context. Not yet in seed.
- `corbetta_shulman2002_dorsal_ventral_attention` — dorsal-attention-network framework, the candidate neural substrate. Not yet in seed.
- `awh_jonides2001_overlapping_spatial_wm` — overlapping mechanisms for spatial WM and spatial attention; the precursor empirical case for shared geometry. Not yet in seed.
- `theeuwes2009_oculomotor_capture` — oculomotor capture and the premotor-theory-of-attention literature. Not yet in seed.
- `souza_oberauer2016_retro_cue_review` — review of retro-cue effects in WM, contextualising Exp 2's manipulation. Not yet in seed.
- `rizzolatti_riggio_dascola1987_premotor_attention` — premotor theory of attention; the original theoretical claim that motor planning circuitry implements covert attention. Not yet in seed.
- `van_ede_chekroud_stokes_nobre2019_orienting_within_wm` — companion paper from the same group on orienting within working memory using EEG; needed for the neural-substrate evidence the present paper lacks. Not yet in seed.
- `liu_2024_microsaccade_wm_review` — recent review of microsaccade signatures of internal attention; provides updated context. Not yet in seed.
