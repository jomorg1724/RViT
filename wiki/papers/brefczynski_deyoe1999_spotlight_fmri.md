---
id: brefczynski_deyoe1999_spotlight_fmri
title: "A physiological correlate of the 'spotlight' of visual attention"
authors:
  - "Brefczynski, Julie A."
  - "DeYoe, Edgar A."
year: 1999
venue: "Nature Neuroscience"
doi: "10.1038/7280"
arxiv: ""
url: "https://doi.org/10.1038/7280"
tags:
  - human-neuroimaging
  - visual-attention
  - early-visual-cortex
concepts:
  - attentional-spotlight
  - topographic-organization
  - retinotopy
  - gain-modulation
related:
  - silver2005_topographic_parietal
  - posner1980_orienting
  - moran_desimone1985_selective_attention
  - cameron2002_covert_attention_contrast
  - reynolds_heeger2009_normalization
  - sharma2015_attention_temporal_v1
  - wang2015_v1_exogenous_attention
  - treisman_gelade1980_feature_integration
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-16"
---

# A physiological correlate of the 'spotlight' of visual attention

## 1. Abstract

Brefczynski & DeYoe used 3T fMRI to localize the neural correlate of the long-hypothesized "attentional spotlight" in human visual cortex. While maintaining central fixation, subjects covertly shifted attention among targets embedded in a dense, spatially-extensive array of distractors. By systematically varying the *attended* visual-field location while holding the *physical* stimulus identical, the authors isolated activity attributable purely to the locus of covert attention. The principal finding: the cortical topography of the purely attention-driven activity *precisely matched* the retinotopic topography that the same locations produced when they were physically stimulated and passively viewed. This retinotopic attention map was present in V1 and propagated through V2, V3, V4, and the dorsal/ventral occipital regions. Attention thus generates a localized, retinotopically-organized BOLD enhancement at the spatial coordinates of the attended location — a direct physiological correlate of the "spotlight" concept inherited from the cognitive-psychology tradition (Posner 1980; Treisman; Eriksen). The result reframed what had previously been a behavioral metaphor as a measurable, area-by-area cortical signature, opening a fifteen-year line of work on the gain mechanisms (Reynolds & Heeger 2009 normalization model), priority sources (Silver, Ress & Heeger 2005), and temporal dynamics (Martínez et al. 1999) of attentional control in human cortex.

## 2. Why this matters for us

This is the foundational human-imaging demonstration that *covert spatial attention modulates V1-level activity in a retinotopically-organized way*. For the user's program, the entry licenses three claims that are otherwise circumstantial. First, the recurrent ViT's per-patch attention map is *not* a decision-stage artifact: real human cortex maintains a retinotopic attentional gain map down at the earliest cortical processing stage, so a patch-indexed (i.e., retinotopic) modulation in the architecture is biologically warranted. Second, the V1-level BOLD enhancement is *gain-like and stimulus-aligned*, not a separate spotlight that competes with the feature stream — supporting the multiplicative-feedback formulation of attention used in the Feedback Transformer ($s_q \odot c_q$) and in PRISM's FiLM modulation. Third, in combination with Silver, Ress & Heeger 2005, this paper establishes that retinotopic attention maps exist at *both* the priority-source level (parietal) and the gain-target level (V1) — exactly the descending-projection structure that the user's multi-compartmental memory implements.

## 3. Key claims

1. **Covert spatial attention produces localized BOLD enhancement in retinotopically-defined regions of human V1, V2, V3, V3A, V4, and adjacent occipital cortex** corresponding to the attended visual-field location.
2. **The attention-driven topography precisely matches the stimulus-driven topography** at the same locations: the cortical pixel activated by attending to position $(r, \theta)$ is the same pixel activated by passively viewing a stimulus at $(r, \theta)$.
3. **The effect is present at the level of primary visual cortex (V1)**, not only at extrastriate stages — refining the Moran & Desimone 1985 single-unit picture, which found V4/IT but not V1 effects, by demonstrating with population-level BOLD that attentional modulation does reach V1 in humans.
4. **The modulation occurs without changes in eye position**: fixation was monitored, and attention shifts were purely covert.
5. **The attention-driven activity is *additive* to (and largely independent of) the stimulus-driven activity**: attending to a location enhances response there even when the physical stimulus at that location is constant and identical to non-attended trials.
6. **Attention "moves" through cortex**: when the cued location is varied across trials, the attention-driven cortical activation moves smoothly through cortex along the same retinotopic gradient that a physical stimulus would traverse.
7. **The effect is consistent with the cognitive-psychology spotlight metaphor** (Posner 1980; Eriksen & Yeh 1985; Treisman) — but now grounded in a specific physiological substrate (retinotopic BOLD enhancement in occipital cortex).

## 4. Methods

Subjects performed a covert-attention task in a 3T fMRI scanner while fixating centrally. The visual display contained a dense array of small target patches and distractors filling much of the visual field. On each block the subject was cued to direct attention covertly to one specific location in the array and to detect/discriminate a brief feature change there, while ignoring identical-looking changes at all other locations. Across blocks, the *cued* location was systematically varied to tile the visual field at multiple eccentricities and polar angles. Eye position was monitored to confirm fixation.

The critical contrast: BOLD response on trials when location $(r, \theta)$ was *attended* minus BOLD response on otherwise-matched trials when the same location was *not* attended (subject attended elsewhere). Because the physical stimulus array was constant, this contrast isolates attention-driven activity from stimulus-driven activity.

Separate scans used standard rotating-wedge / expanding-ring retinotopic mapping (DeYoe et al. 1996; Engel et al. 1994; Sereno et al. 1995) to localize visual areas V1, V2, V3, V3A, V4 and to recover their retinotopic phase maps. The attention-driven phase maps were then registered against the stimulus-driven phase maps on the flattened cortical surface, allowing direct pixel-by-pixel comparison.

The analysis quantifies (a) the cortical location of attention-driven activation as a function of cued visual-field location and (b) the degree of overlap (correlation, registration) between attention-driven and stimulus-driven retinotopic maps.

## 5. Results

- **Pixel-level co-registration of attention and stimulus maps.** When attention was directed to visual-field location $(r, \theta)$, the cortical site of maximum attention-driven BOLD was the same as (or within a few millimeters of) the site that the physical stimulus at $(r, \theta)$ activated. The match held across V1, V2, V3, V3A, V4, and into ventral/dorsal extrastriate regions.
- **V1 is implicated.** The attentional spotlight produces a measurable BOLD signature at the V1 level — not exclusively at extrastriate stages. This was a significant refinement of the M&D 1985 picture and aligned with concurrent findings (Tootell et al. 1998; Gandhi, Heeger & Boynton 1999; Somers et al. 1999) that attention reaches V1.
- **Attention-driven amplitude grows with task difficulty.** When the discrimination at the cued location was made harder, the attention-driven BOLD enhancement at the corresponding retinotopic site grew, suggesting the modulation reflects effortful gain rather than incidental task-related signals.
- **Smooth cortical motion under attention shifts.** As the cued location was moved smoothly across the array, the activated cortical region moved smoothly along the corresponding retinotopic gradient — qualitatively as if a "spotlight" of cortical activity were traversing the visual cortex map.
- **The attention-driven response can be large relative to the unattended baseline** — on the order of a substantial fraction of the response elicited by passive viewing of the same stimulus, indicating that attention is not a small perturbation but a major contributor to V1-level BOLD.
- **Multiple visual areas tile the same retinotopic locus.** Because V1, V2, V3, V3A, and V4 each have their own retinotopic map, attending to a single visual-field location produces enhancement at *multiple* cortical sites — one per area, each at the corresponding map coordinate. The spotlight is therefore not a single localized blob but a *stack* of co-registered blobs spanning the early-visual-cortex hierarchy.
- **The effect generalizes across eccentricities tested in the array** (out to several degrees), consistent with cortical-magnification-corrected scaling: peripheral attended locations activate the peripheral representation in cortex, central locations activate the foveal representation.

## 6. Critique / limitations

The paper is correlative. BOLD is a slow, indirect proxy for neural activity, and large-amplitude V1 BOLD modulation is consistent with multiple underlying neural mechanisms (gain on the same population, recruitment of additional neurons, top-down baseline shift, vascular coupling effects). Subsequent single-unit work in macaque (McAdams & Maunsell 1999; Reynolds, Chelazzi & Desimone 1999; Reynolds & Heeger 2009 normalization model) has had to disentangle these.

The retinotopic phase analysis assumes a smoothly varying spatial preference across the cortical surface. The "spotlight" interpretation is biased *toward* retinotopic organization by the analysis pipeline. Non-retinotopic forms of attention (feature-based, object-based) would not show up cleanly in this paradigm. Subsequent work (Treue & Martínez Trujillo 1999; Saenz, Buracas & Boynton 2002; Liu, Larsson & Carrasco 2007) has had to extend the imaging picture to those non-spatial modes.

The Moran & Desimone 1985 single-unit result that V1 was *not* modulated, by contrast, suggests that population-level BOLD enhancement in V1 may reflect *some* mechanism (e.g., top-down baseline activity or a small per-neuron gain summed across population) that single-cell recording at the time was not optimally placed to detect. The two literatures are not in flat contradiction — they probe different scales — but the discrepancy was for years an active question (Roelfsema, Lamme & Spekreijse 1998; Posner & Gilbert 1999; reviews in Carrasco 2011).

The paper does not propose a specific *computational model* of how the V1 spotlight is generated (top-down projection from parietal/FEF priority maps, local recurrent enhancement, divisive normalization with gain). That gap is filled by the subsequent normalization-model literature (Reynolds & Heeger 2009) and by the imaging-of-priority-source literature (Silver, Ress & Heeger 2005; Kastner et al. 1999; Corbetta & Shulman 2002).

The dense-array task confines the analysis to *spatial* attention; the paradigm cannot directly speak to feature-based or object-based attention, where the modulation pattern would not be expected to follow the same retinotopic alignment. The user's program, in contrast, requires the attention map to integrate spatial, feature, and object-based selection in a single representation; the imaging side of that integration was developed in subsequent work (Saenz, Buracas & Boynton 2002; Serences & Boynton 2007).

The Brefczynski/DeYoe BOLD enhancement is *additive* with the stimulus response in the simplest analysis, but the underlying neural operation may be *multiplicative gain* on the input. BOLD is too coarse to distinguish these decisively; psychophysical work (Cameron, Tai & Carrasco 2002) provides the contrast-gain evidence that fixes this mechanism.

## 7. Connection to our work

Brefczynski & DeYoe 1999 is the *human-imaging anchor* for the recurrent ViT's spatial attention map. The connections to the user's architectural program are direct.

**The fMRI spotlight = the recurrent ViT's per-patch attention weight.** The recurrent ViT (2502.10955) produces a self-attention map indexed by input patches, where each patch corresponds to a retinotopic location in the input image. The row-summed (or column-summed) attention magnitude at each patch is a *retinotopic gain signal*: how much the model's representation is pulling from that input location. This is the structural counterpart of the Brefczynski/DeYoe finding — a retinotopic BOLD enhancement at the attended location. The paper supplies the empirical license for interpreting the ViT attention map as a *spotlight*: the human brain does in fact maintain a localized, retinotopically-aligned enhancement at the attended location, exactly the operation the ViT's softmax-weighted patch read-out implements.

**Attention modulates V1, not just decision-stage.** A live concern about transformer-style attention as a model of biological attention is that the softmax operates over already-encoded tokens and might therefore look more like a *decision-stage* mechanism than an early-sensory one. Brefczynski & DeYoe rule this out empirically: spatial attention modulates V1-level BOLD. The ViT's attention map, being patch-indexed, is also a V1-level construct — each patch corresponds roughly to a V1-receptive-field region in input-image coordinates. The user's commitment to placing the Feedback Transformer at *every level* of the multi-compartmental memory hierarchy (`the_user_architectural_program.md` §1, §3), including the V1-paired Layer 1, is biologically licensed by this paper.

**Multiplicative gain on bottom-up sensory, not separate spotlight stream.** The Feedback Transformer's $s_q \odot c_q$ structure (sensory projection $\odot$ feedback contribution) implements attention as a *multiplicative gain on the same population* that carries the bottom-up signal. Brefczynski & DeYoe's finding that the attention-driven map *co-registers* with the stimulus-driven map at the pixel level — same cortical site, scaled response — is the imaging counterpart of this commitment. The alternative architecture (a separate "spotlight" population at a different cortical site) is ruled out by the co-registration result.

**Connection to silver2005_topographic_parietal.** Silver et al. show retinotopic attention maps in *parietal* cortex (IPS1/IPS2); Brefczynski & DeYoe show retinotopic attention maps in *occipital* cortex (V1–V4). Together they trace the descending-projection structure: a priority-bearing retinotopic map in parietal cortex projects down to V1/V4 to produce retinotopic gain there. This is the cortical architecture of the user's multi-compartmental memory: Layer 3 (parietal-analog priority map) sends ascending projections to Layer 1 (V1-analog feature stack), and the feedback shows up as a retinotopic gain map at the V1 level. Two papers in the database now anchor each end of this descending-projection arc.

**Connection to moran_desimone1985_selective_attention.** Moran & Desimone reported attentional modulation in V4/IT but *not* V1 at the single-unit level in macaque. Brefczynski & DeYoe report it in V1 at the population level in human. The discrepancy is informative: V1 modulation at the population level is too small per-neuron to reliably detect in 1985 single-unit recordings, but is reliably present when summed across the V1 population in BOLD. For the user's architecture, this resolves a potential conflict: the ViT-attention modulation is intrinsically a *population* operation (the softmax is applied across all tokens), and the Brefczynski/DeYoe paper supports interpreting it as such — V1-level attentional gain *is* present, just only visible at the population scale.

**Connection to posner1980_orienting.** Posner established the *behavioral* phenomenology of covert attention — the spotlight metaphor itself. Brefczynski & DeYoe supply the *physiological* substrate of Posner's spotlight. The ViT attention map, viewed as a computational model, sits between these two: it predicts both the behavioral cueing effects (faster/more accurate read-out at the attended location) and the physiological signature (retinotopic enhancement in early visual cortex).

**Connection to cameron2002_covert_attention_contrast.** Cameron, Tai & Carrasco showed that covert attention produces *contrast gain* (psychometric shift, not scaling). Brefczynski & DeYoe show that the cortical substrate of that contrast gain is a retinotopically-aligned BOLD enhancement at V1. The two papers together specify the gain operation (contrast gain, multiplicative) and its cortical location (V1, retinotopic), which jointly justify the architectural choice of multiplicative, patch-indexed attention modulation in the Feedback Transformer.

**Stack of co-registered attention maps = multi-layer ViT attention.** The Brefczynski/DeYoe result that *each* of V1, V2, V3, V3A, V4 shows its own retinotopic attention enhancement at the same visual-field location is the cortical analog of a multi-layer ViT in which each transformer block computes its own attention map over patches indexed in the same input geometry. The user's three-layer multi-compartmental memory (`the_user_architectural_program.md` §3) — V1-paired Layer 1, V2/V4-paired Layer 2, IT-paired Layer 3 — is the natural architectural translation. Brefczynski & DeYoe license the claim that real cortex maintains a *stack* of retinotopic attention maps, not a single one.

**Concrete manuscript hook.** When the Recurrent ViT manuscript (or PRISM v1's THESIS.md) argues that the model's attention map is biologically interpretable as an early-visual-cortex gain map, the canonical citation pair is Brefczynski & DeYoe 1999 (V1-level retinotopic gain) + Silver, Ress & Heeger 2005 (parietal-level priority source). When the discussion extends to multi-layer recurrent processing in occipital cortex, the same paper supplies the multi-area co-registered-stack observation.

## 8. Citations to follow

- `tootell1998_retinotopy_attention` — Tootell, Hadjikhani, Hall, Marrett, Vanduffel, Vaughan & Dale, *Neuron* 1998. The other major retinotopic-attention paper of the same era. Direct empirical companion; should enter the database.
- `gandhi_heeger_boynton1999_v1_attention` — *PNAS* 1999. Independent V1 attentional-modulation result published the same year. Important triangulation point.
- `somers1999_v1_attention_modulation` — Somers, Dale, Seiffert & Tootell, *PNAS* 1999. The third concurrent V1 attention demonstration. Three independent groups converging on the V1 result.
- `kastner1999_directed_attention` — Kastner, Pinsk, De Weerd, Desimone & Ungerleider, *Neuron* 1999. Baseline activity during directed attention without visual stimulation — the top-down-only version of the same effect.
- `kastner1998_mechanisms_attention` — Kastner, De Weerd, Desimone & Ungerleider, *Science* 1998. Mechanisms of directed attention in extrastriate cortex.
- `corbetta_shulman2002_attention_review` — *Nat Rev Neurosci* review of dorsal/ventral attention networks. The canonical review framing the parietal-to-occipital descending projection.
- `posner_gilbert1999_attention_primary_visual` — Posner & Gilbert review of attention effects in primary visual cortex. Reconciles the single-unit / BOLD discrepancy.
- `roelfsema_lamme_spekreijse1998_v1_attention` — V1 attentional modulation in macaque using a different paradigm; complements the human-imaging picture.
- `martinez1999_attention_eeg_fmri` — Martínez, Anllo-Vento, Sereno, Frank, Buxton, Dubowitz, Wong, Hinrichs, Heinze & Hillyard, *Nat Neurosci* 1999. Combined EEG/fMRI of spatial attention; localizes earliest cortical attention effects in time and space.
- `engel_glover_wandell1997_retinotopy` — methodological foundation for the retinotopic-mapping analysis used here.
- `deyoe1996_mapping_human_visual_cortex` — DeYoe et al. *PNAS* 1996, the retinotopic mapping methodology DeYoe brought to this paper as senior author.
- `treisman_gelade1980_feature_integration` — feature-integration theory, the cognitive-psychology framework whose spatial-spotlight mechanism this paper makes physiological.
- `eriksen_yeh1985_spotlight` — earlier behavioral spotlight work whose physiological counterpart this paper supplies.
- `saenz_buracas_boynton2002_feature_attention_fmri` — extends the spotlight-imaging program to *feature-based* attention; the natural next paper in the imaging arc.
- `serences_boynton2007_feature_attention_global` — global-vs-local feature attention in fMRI; further extension of the Brefczynski-DeYoe imaging paradigm beyond pure spatial attention.
