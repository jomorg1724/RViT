---
id: hollingworth2008_vstm_function
title: "Understanding the function of visual short-term memory: transsaccadic memory, object correspondence, and gaze correction"
authors:
  - "Hollingworth, Andrew"
  - "Richard, Ashleigh M."
  - "Luck, Steven J."
year: 2008
venue: "JEP: General"
doi: "10.1037/0096-3445.137.1.163"
arxiv: ""
url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC2784885/"
tags:
  - working-memory
  - visual-attention
  - change-detection
  - psychophysics
concepts:
  - feature-binding
  - working-memory-persistent-activity
related:
  - luck_vogel1997_wm_capacity
  - luck_vogel2013_wm_capacity_review
  - panichello_buschman2021_shared_mechanisms
  - cavanaugh_wurtz2004_sc_change_blindness
  - gupta_sridharan2024_presaccadic_change
  - hoffman2016_attention_eye_movements
  - bays2024_wm_representation
  - awh2006_attention_wm
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# Understanding the function of visual short-term memory: transsaccadic memory, object correspondence, and gaze correction

## 1. Abstract

Visual short-term memory (VSTM) has received intensive study over the past decade, with research focused on VSTM capacity and representational format. Yet, the *function* of VSTM in human cognition is not well understood. The authors propose that a core function of VSTM is to maintain the surface features of the current saccade target across the saccade itself, so that the target can be rapidly re-acquired if the eye lands off target. Across four experiments, the authors show that human observers correct errant saccades to a rotated target array with near-perfect accuracy and short (~220 ms) latency; that correction is driven by surface-feature matching rather than spatiotemporal extrapolation; that the correction process consumes VSTM resources (a concurrent change-detection load reduces both correction accuracy and color-memory K); and that the correction is largely automatic and occurs outside conscious awareness. The authors argue that VSTM is the substrate for transsaccadic memory, object correspondence, and gaze correction — three closely related functions that operate continuously in natural vision.

## 2. Why this matters for us

Hollingworth-Richard-Luck 2008 supplies the *functional rationale* for VSTM that the user's program implicitly relies on: VSTM is not a passive store but an active substrate for moment-to-moment scene continuity, object correspondence across rapid sensory disruptions (saccades), and re-acquisition of lost targets. The Recurrent ViT's change-detection task is precisely the laboratory abstraction of this natural function: detect whether the pre-disruption scene matches the post-disruption scene, where the hidden state $H^{(t-1)}$ is the model's VSTM analog. Hollingworth shows experimentally that human VSTM is *what gets used* for this comparison, that the resource is shared with explicit change-detection tasks (Exp 3, Cowan's K drops from 2.73 → 1.96 under dual-task), and that the function is largely automatic — properties the user's Recurrent ViT memory state should plausibly inherit if it is to be a credible model of VSTM. The 220 ms human correction-latency budget and the ~0.77-item capacity cost under dual-task are concrete numerical targets a putative VSTM model can be evaluated against.

## 3. Key claims

1. **VSTM maintains saccade target features across the saccade.** Pre-saccadic attention selects the target for preferential encoding into VSTM, and the encoded features are matched to post-saccadic visual input to verify (or repair) the eye's landing.
2. **Gaze correction is fast, accurate, automatic, and unconscious.** When the array is surreptitiously rotated during the saccade, observers correct to the original target with 87–98% accuracy at ~220 ms latency; ~30% of corrections occur without subjective awareness even when observers are explicitly instructed to inhibit them.
3. **Object correspondence is feature-based, not spatiotemporal.** Surface features (color, shape) — not retinal position or motion extrapolation — establish the link between pre- and post-saccadic representations of the same object.
4. **Gaze correction shares VSTM capacity with change detection.** A concurrent color change-detection task reduces correction accuracy (90.2% → 80.8%) and reduces color-memory Cowan's K (2.73 → 1.96); a verbal short-term-memory load does not interfere, isolating the shared resource as *visual* WM specifically.
5. **VSTM is the substrate for three integrated functions.** Transsaccadic memory (maintaining features across the saccade), object correspondence (matching pre- and post-saccadic objects), and gaze correction (re-acquiring missed targets) are three faces of one underlying VSTM mechanism.
6. **The function operates thousands of times per day.** Approximately 30–40% of saccades land off-target; with ~3 saccades per second, gaze correction is invoked on the order of $10^4$ times per waking day, making this arguably the most-used cognitive function the brain implements.
7. **A ~40 ms "memory cost" indexes the VSTM lookup itself.** Correction latency is reliably ~40 ms longer when the post-saccadic display contains distractors (requiring a VSTM-mediated match) than when only the target remains (allowing direct match). This isolates the VSTM read-out as a distinct, measurable processing stage.
8. **Distractor proximity modulates correction errors.** When the eye lands closer to a distractor than to the original target, correction accuracy drops from 91.6% to 82.4% — VSTM-based matching is biased by spatial weighting of the post-saccadic input, not a pure feature-purity test.
9. **Verbal-load specificity.** A concurrent verbal-WM load (digit string) does not interfere with gaze correction, isolating the resource as visual rather than central-executive. This is the same logic Baddeley uses to dissociate the phonological loop from the visuospatial sketchpad, applied here to a processing substrate.
10. **The "memory cost" is robust to display complexity.** The 39–46 ms penalty for full-array vs. single-object displays replicates across colored disks and grayscale novel objects, suggesting the cost indexes a stage of VSTM access rather than a perceptual property of the display.

## 4. Methods

Four behavioral experiments with N=12 participants each (separate samples).

**Experiment 1.** Color-disk arrays (12 colors); observer makes a saccade to a cued disk; on 1/3 of trials the array is rotated 15° during the saccade (under saccadic suppression). Full-array condition (post-saccade display contains all 12 disks) vs. single-object condition (only the rotated target disk remains). Measure: correction accuracy and corrective-saccade latency.

**Experiment 2.** Same paradigm but 8 complex novel grayscale objects (richer surface features) and a larger 22.5° rotation. Tests whether correction generalizes beyond color and depends on feature-based correspondence.

**Experiment 3.** Dual-task design crossing the gaze-correction task (8 novel objects) with a concurrent color change-detection task (5 colored patches held in VSTM during the saccade trial). Three blocked conditions: dual-task, gaze-correction-only, color-memory-only. A separate sub-experiment substitutes a verbal short-term-memory load (digit string) for the color-memory load to test specificity.

**Experiment 4.** Color-disk arrays with an outer ring landmark; explicit instructions to *not* correct errant saccades; subjective rotation-detection probes after each trial. Manipulates awareness to dissociate automatic correction from voluntary correction.

The critical methodological move is the *mid-saccade rotation*: by rotating the array during saccadic suppression, the authors create a controlled mismatch between the pre-saccadic target representation (held in VSTM) and the post-saccadic visual input. Correction performance then directly indexes the fidelity and use of the VSTM representation. The dual-task in Exp 3 then asks whether this VSTM representation shares capacity with a canonical change-detection memory load — the same paradigm Luck & Vogel 1997 used to establish the ~4-item ceiling.

## 5. Results

**Experiment 1.** Full-array correction accuracy 98.1%; single-object 100%. Latency: full-array 240 ms, single-object 201 ms. The 39 ms "memory cost" indexes the time to consult VSTM rather than match directly to the only post-saccade object.

**Experiment 2.** Full-array 87.0%, single-object 100%. Latency: 221 ms vs. 175 ms (46 ms memory cost). Distance-to-distractor correlated with accuracy ($r = -0.17$, $p < .001$); accuracy 91.6% when the eye lands closer to the target, 82.4% when closer to a distractor — consistent with a feature-comparison process that is biased by post-saccadic visual proximity.

**Experiment 3.** Dual-task gaze-correction accuracy dropped from 90.2% → 80.8%; latency 203 → 228 ms; color-memory K dropped from 2.73 → 1.96. Verbal-load condition: no significant interference (87.4% dual vs. 84.3% gaze-only, $p = .12$). The double dissociation isolates the shared resource to *visual* WM.

**Experiment 4.** Subjective rotation detection: 77% of rotation trials. Correction accuracy when observer reported being *unaware* of the rotation: 96%. Correction accuracy when aware *and* explicitly told to inhibit: 56% — i.e., observers cannot fully suppress the correction even with explicit instruction. Latency: 228 ms (unaware) vs. 225 ms (aware) — no slowing when aware. Awareness of having corrected: ~30% above chance, indicating most corrections are not consciously monitored.

**Conscious-control failure.** The drop from 96% (unaware) to 56% (instructed to inhibit but aware) in Exp 4 is striking: even with explicit instructions and conscious detection of the rotation, voluntary control only halves the correction rate. This indicates the VSTM-comparison process is so deeply ingrained that top-down inhibition cannot fully suppress it. For an artificial model of VSTM-based change detection, this maps onto an architectural feature, not a bug — the recurrent comparison should be a *default* operation rather than a gated one.

**Cross-experiment pattern.** Across all four experiments, three numbers anchor the phenomenon:

- Correction accuracy: 80–98%, depending on memory load and display complexity.
- Correction latency: 200–240 ms, with the ~40 ms "memory cost" robust across paradigms.
- VSTM capacity engaged: roughly one item's worth of K is consumed by the correction process (K = 2.73 → 1.96 = a loss of ~0.77 items under dual-task).

These numbers are the empirical targets a model of human VSTM-mediated change comparison should match.

**Latency-vs-accuracy trade-off.** Across conditions, the data trace a roughly invariant operating point: when a paradigm forces a faster correction (e.g., single-object display), accuracy approaches ceiling; when it forces a slower correction (full-array, dual-task), accuracy drops while latency increases modestly. There is no condition in which observers respond more slowly *and* less accurately than baseline, suggesting the underlying VSTM-comparison process is not a speed-accuracy tradeoff at the algorithmic level but a fixed-time match with output quality limited by the fidelity of the stored representation.

**Verbal-vs-visual dissociation.** The verbal-load null in Exp 3 is the load-bearing control: it rules out generic dual-task interference and forces the conclusion that gaze correction shares resources specifically with visual short-term storage. This is the same double-dissociation logic Baddeley used to establish the phonological loop / visuospatial sketchpad distinction, and it generalizes here to *processing* substrates, not just storage buffers.

## 6. Critique / limitations

Despite the methodological care, several limitations bound the inferences.

The paradigm uses arrays of discrete objects (disks, novel shapes), not naturalistic scenes. Whether the same VSTM mechanism scales to high-density scenes (and how it interacts with gist representations) is not directly tested here; Hollingworth's broader research program (e.g., scene-memory papers from the same lab) takes up that question.

N=12 per experiment is small by modern standards. Effect sizes are large, but the individual-differences structure that Luck & Vogel 2013 emphasizes (and that bears on the discrete-slot vs continuous-resource debate, [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)) is not analyzable at this sample size.

The "VSTM resource" interpretation of the dual-task interference rests on the verbal-load control. Subsequent work has shown that attentional / central-executive resources can produce similar interference patterns; the visual-WM interpretation is plausible but not uniquely diagnostic.

The paper *infers* feature-based correspondence from the rotation paradigm. It does not directly probe what representational format VSTM uses (continuous feature values? discrete slots? bound objects?). That question is taken up by the discrete-vs-continuous debate ([luck_vogel2013_wm_capacity_review](research_db/papers/luck_vogel2013_wm_capacity_review.md); [bays2024_wm_representation](research_db/papers/bays2024_wm_representation.md)).

The conscious-awareness dissociation in Exp 4 is striking but rests on subjective reports, which are an imperfect index of access consciousness. Replications with objective awareness measures (e.g., post-decision wagering) would strengthen the claim.

The authors do not commit to a neural substrate. They argue functionally for VSTM involvement but make no claim about which cortical area implements the comparison. The Cavanaugh-Wurtz subcortical line and the broader change-detection neuroimaging literature suggest distributed substrates (parietal, frontal, collicular) that the present behavioral paradigm cannot dissociate.

Finally, the "function" framing emphasizes one putative role (gaze correction) over alternatives (scene-gist construction, statistical learning, navigation). The paper does not argue this is VSTM's *only* function, but the focus on saccade-related processes leaves open how the same resource supports longer-timescale memory phenomena.

The mid-saccade rotation manipulation, while powerful, depends on saccadic suppression hiding the rotation itself. The 23–35% of trials on which observers *did* notice the rotation are analyzed separately, but a more refined awareness measure could re-partition the dataset and might change effect sizes. The qualitative pattern is robust, but the precise quantitative split between "automatic" and "voluntary" correction is paradigm-dependent.

## 7. Connection to our work

This paper is one of the most directly methodologically relevant entries in the database for the Recurrent ViT's change-detection task.

**VSTM as the substrate of the recurrent hidden state.** The Recurrent ViT (2502.10955) maintains a hidden state $H^{(t-1)}$ across the inter-stimulus disruption of a change-detection trial. Hollingworth's experiments establish that *human* VSTM is what gets used for this comparison in natural vision (across saccades) and in laboratory change-detection tasks (Exp 3). Treating $H^{(t-1)}$ as a VSTM analog is not metaphor; it is the same functional substrate the human brain uses for the same class of comparisons. This grounds the user's claim (`THESIS.md` §2) that the Recurrent ViT models a specifically VSTM-mediated computation.

**Change detection is the laboratory abstraction of gaze correction.** The user's recurrent-ViT training task — detect a change between a remembered scene and a current one — is the formal abstraction of what Hollingworth shows happens after every off-target saccade: compare remembered target features against current visual input, decide same / changed, and act accordingly. The 220 ms human correction latency sets a *biological time budget* against which the model's per-step inference budget can be compared.

**Shared resource between memory maintenance and comparison.** Exp 3's K-drop from 2.73 to 1.96 under dual-task shows that human VSTM is a shared resource between maintenance and comparison processes — not two separate buffers. This is consistent with the Recurrent ViT's single hidden state $H^{(t-1)}$ playing both roles, and with [panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md)'s neural finding that attention and WM share circuitry. PRISM v1's single $M_t$ state inherits the same architectural commitment.

**Feature-based correspondence, not position-based.** Hollingworth shows that object correspondence is *feature-based*: pre-saccadic surface features are matched against post-saccadic visual input, with retinal position playing a secondary role. This supports the Recurrent ViT's use of *content-based* token attention (rather than purely positional matching) for comparing $H^{(t-1)}$ to the current frame, and contrasts with purely spatiotemporal accounts of change detection.

**Automatic, unconscious operation.** Exp 4's finding that gaze correction proceeds even when observers are instructed to inhibit it, and largely without awareness, suggests that VSTM-based change comparison is a *default cognitive operation* — not a deliberative process. For the user's program, this matches the architectural commitment that the recurrent memory $H$ is updated *every step* without an explicit gate or attentional commit; the system always compares.

**Connection to saccadic change-detection literature.** [cavanaugh_wurtz2004_sc_change_blindness](research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md) and [gupta_sridharan2024_presaccadic_change](research_db/papers/gupta_sridharan2024_presaccadic_change.md) show that the superior colliculus participates in change detection across saccades. Hollingworth's behavioral work supplies the *psychophysical* counterpart: SC microstimulation modulates the same VSTM-based comparison Hollingworth probes behaviorally. The user's program's hierarchical memory ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §3) could in principle implement an SC-like fast subcortical comparison alongside a slower cortical VSTM comparison, with the Hollingworth-Cavanaugh-Gupta triad supplying the empirical constraints.

**Capacity-limited memory.** The K = 2.73 baseline in Exp 3 is consistent with [luck_vogel2013_wm_capacity_review](research_db/papers/luck_vogel2013_wm_capacity_review.md)'s ~4-item ceiling. Whether the Recurrent ViT's hidden-state representation exhibits a similar capacity ceiling when probed with multi-item change-detection arrays is an empirical question the user's program should ask directly.

**Implication for hidden-state update dynamics.** Hollingworth's data set a tight time budget: ~220 ms from saccade offset to corrective saccade onset includes encoding the post-saccadic scene, matching against VSTM, computing a corrective vector, and triggering the motor command. The matching step alone is therefore well under 100 ms — i.e., a *single forward pass* of a recurrent comparison, not an iterative-inference loop. This bears on PRISM v1's inner variational loop (`THESIS.md` §2.8) and on the user's iterative-VAE program ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §4): whatever $n_{FR} \to n_{BR}$ scheme is used, the *first-pass* output of the system must already be a viable change-detection answer, because biological vision does not have the time budget for a long iterative refinement on every saccade.

**Architectural prediction.** If the user's program is correct that VSTM is implemented as a shared substrate (cf. [panichello_buschman2021_shared_mechanisms](research_db/papers/panichello_buschman2021_shared_mechanisms.md)) and that comparison is a default operation, then ablating the recurrent hidden state in a trained Recurrent ViT should produce *exactly* the dual-task interference pattern Hollingworth shows — accuracy drops, latency-equivalent increases — and ablating verbal/symbolic side-information should not. This is a directly testable prediction the manuscript should make.

**Bridge to the hierarchical-memory program.** Hollingworth's data say nothing about whether VSTM is implemented at one level of the cortical hierarchy or many. The user's multi-compartmental memory ([the_user_architectural_program](research_db/threads/the_user_architectural_program.md) §3) commits to multiple GridCell RNN layers operating at different spatial / channel resolutions, with the V1-paired layer holding the most spatially-precise version of the scene. The behavioral prediction is that high-spatial-precision corrections (small rotations, small displacements) should rely more heavily on shallow-layer memory, while feature-identity corrections (object substitutions) should rely more heavily on deep-layer memory. Hollingworth's 15° vs 22.5° rotation conditions and color-vs-novel-object manipulations are within reach of an analogous model probe.

**Implication for the change-detection training curriculum.** Because human gaze correction is a *constantly invoked* operation, a biologically-motivated curriculum would expose the Recurrent ViT to many trials with mild scene perturbations (rotations, translations) interleaved with the canonical change-detection trials. The premise is that the model should *expect* small perturbations between memory and current observation and learn to ignore them while still detecting genuine changes. This matches Hollingworth's finding that human VSTM is tuned to a noise-tolerant comparison rather than an exact-match test.

**Why a single paper carries this much weight.** Hollingworth-Richard-Luck is the experimental work that turns VSTM from a *storage construct* into a *processing substrate*. The Recurrent ViT's premise — that change detection requires a recurrent state that compares across time — only earns biological grounding if VSTM is functionally what the brain uses for such comparisons. Hollingworth supplies precisely that grounding, with quantitative latency and accuracy numbers the model can be matched against.

**Connection to feature-binding.** The correspondence-by-features result implies that VSTM contents are *bound objects* — color, shape, and position are integrated such that an object can be tracked across the saccade. This bears on the user's interest in feature-binding as a memory primitive (concept tag `feature-binding`) and on PRISM v1's commitment that the memory state $M_t$ is a per-token vector rather than a global pooled representation. Per-token binding is the architectural commitment that mirrors object-file theory; Hollingworth's data are direct evidence for it at the behavioral level.

**Constraint on the published manuscript narrative.** When the Recurrent ViT manuscript (2502.10955) frames its results as a model of VSTM-based change detection, Hollingworth is the citation that converts that framing from a loose analogy into a quantitatively-bounded biological claim. Specifically, the paper should cite Hollingworth for (a) the empirical demonstration that VSTM is the resource used for change comparison across saccades, (b) the dual-task interference pattern that supports a shared-resource view of WM, and (c) the automaticity of the comparison — all three of which the Recurrent ViT's single-pass recurrent architecture matches more naturally than would an iterative inference scheme.

## 8. Citations to follow

- `irwin1991_transsaccadic_memory` — original transsaccadic-memory paradigm; not in seed.
- `henderson_hollingworth1999_scene_perception` — Hollingworth's scene-memory foundation; not in seed.
- `deubel_schneider1996_presaccadic_attention` — pre-saccadic attention to saccade target; not in seed.
- `kowler1995_attention_saccade` — attention-saccade coupling; not in seed.
- `currie2000_role_visual_memory_saccades` — early evidence for VSTM-based gaze correction; not in seed.
- `melcher2011_visual_stability` — visual stability across saccades; not in seed.
- `hoffman2016_attention_eye_movements` — attention–eye-movement link; in seed (full).
- `luck_vogel1997_wm_capacity` — the K ≈ 4 founding paper; in seed (full).
- `cavanaugh_wurtz2004_sc_change_blindness` — subcortical substrate for change detection across saccades; in seed (full).
- `cowan2001_magical_number_4` — Cowan's chunk-capacity review (the K-statistic used in Exp 3); not in seed.
- `kahneman_treisman1992_object_files` — the object-file framework underlying surface-feature correspondence; not in seed.
- `rensink2002_change_blindness_review` — review of the change-blindness paradigm Hollingworth's results bear on; not in seed.
- `awh2006_attention_wm` — attention–WM interaction; in seed.
- `panichello_buschman2021_shared_mechanisms` — neural evidence for shared WM/attention substrate; in seed.
- `gupta_sridharan2024_presaccadic_change` — presaccadic-change behavior and neural correlates; in seed.
