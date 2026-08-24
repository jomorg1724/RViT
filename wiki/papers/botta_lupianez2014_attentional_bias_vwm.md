---
id: botta_lupianez2014_attentional_bias_vwm
title: "Spatial distribution of attentional bias in visuo-spatial working memory following multiple cues"
authors:
  - "Botta, Fabiano"
  - "Lupiáñez, Juan"
year: 2014
venue: "Acta Psychologica"
doi: "10.1016/j.actpsy.2014.03.013"
arxiv: ""
url: "https://doi.org/10.1016/j.actpsy.2014.03.013"
tags:
  - working-memory
  - visual-attention
  - psychophysics
  - posner-cuing
concepts:
  - attentional-template
  - cueing-effect
  - validity-effect
  - working-memory-persistent-activity
  - attentional-spotlight
related:
  - vanmoorselaar2014_template_competition
  - carlisle2011_attentional_templates
  - awh2006_attention_wm
  - olivers2011_wm_states_attention
  - carlisle_kristjansson2018_wm_priming
  - kiyonaga_egner2013_wm_internal_attention
relevance_to:
  - recurrent_vit
seed_source:
  - vit_paper_ref_79
status: full
depth: full
last_updated: "2026-05-16"
---

# Spatial distribution of attentional bias in visuo-spatial working memory following multiple cues

## 1. Abstract

When attention is focused on one location, its spatial distribution depends on many factors — the distance between attended and target locations, the presence of visual meridians between them, and whether attention is oriented endogenously or exogenously. Far less is known about how attention distributes when more than one location is cued, and almost all such investigation has been confined to perception. Botta & Lupiáñez (2014) examine the spatial distribution of the *attentional bias in visuo-spatial working memory* (VSWM) following multiple cues, comparing endogenous (central, symbolic) and exogenous (peripheral) orienting and manipulating cue–target predictability. Their results show a systematic dissociation. Following two endogenous cues, the attentional bias on VSWM was modulated by visual meridians and by attentional split, but the distribution stayed *unipolar* (a single broad focus) regardless of cue predictability. Following two exogenous cues, the bias on VSWM distributed *unipolar or multi-modal* depending on the inter-cue distance, with larger effects for highly predictive cues. The work establishes that endogenous and exogenous orienting impose qualitatively different distributional constraints on the WM-attention substrate when more than one location must be prioritized.

## 2. Why this matters for us

The paper is the direct empirical counterpoint to van Moorselaar et al. (2014). Where van Moorselaar shows a *capacity-of-1* limit on the active template in feature-based WM, Botta & Lupiáñez ask the spatial-multiple-cue question: when two locations are cued, does the attentional bias on VSWM remain a single focus or can it split? Their answer is regime-dependent — endogenous orienting yields a unipolar distribution, exogenous orienting can yield a multi-modal distribution at sufficient inter-cue distance. For the user's program, this provides a quantitative behavioral target for the multi-template / multi-peak regime of the central self-attention map: spatial bottom-up cues can produce a multi-peak attention landscape; top-down symbolic cues drive the landscape to collapse to a single peak. The asymmetry maps cleanly onto the architectural distinction between the sensory pathway and the feedback pathway in the Feedback Transformer.

## 3. Key claims

1. **Unipolar bias under endogenous double-cueing.**
   When two locations are cued with central symbolic (endogenous) cues, the attentional bias on VSWM has a single broad focus rather than two separate peaks, regardless of cue-target predictability.
2. **Multi-modal bias under exogenous double-cueing.**
   When two locations are cued with peripheral (exogenous) cues, the bias on VSWM can split into two distinct peaks, with the split modulated by the distance between the two cued locations.
3. **Predictability modulates exogenous but not endogenous distribution.**
   The split / multi-modal pattern under exogenous cueing is more pronounced for highly predictive cues; endogenous double-cue distributions are largely unchanged by predictability manipulations.
4. **Meridian effects are endogenous-specific.**
   Visual meridians (vertical / horizontal) constrain the endogenous attentional bias on VSWM but have a weaker effect on the exogenous distribution.
5. **Attentional split exists in WM, not just perception.**
   The multi-modal exogenous pattern shows that the splitting of the attentional focus — previously documented for perception — also occurs in the *memory* representation of recently-encoded items, extending split-attention findings into the WM domain.
6. **Distinct architectural substrates for the two pathways.**
   The endogenous–exogenous dissociation requires that the two modes of orienting interact with the VSWM substrate in qualitatively different ways, not just with different magnitudes — consistent with separable cortical pathways for top-down and bottom-up spatial control.

## 4. Methods

A series of behavioral experiments combining a *spatial double-cueing* manipulation with a *VSWM probe* readout. The paradigm extends the standard Posner cuing logic — measuring how cue-induced attention shifts modulate post-cue processing — by reading out the resulting attentional bias from a memory representation rather than from perceptual responses.

**Trial structure.** Each trial began with the brief presentation of an array of items to be held in VSWM. Two locations were then cued, with cue type varied across blocks:

- *Endogenous cues:* central symbolic cues (e.g., two pointing arrows / symbols) indicating two peripheral locations.
- *Exogenous cues:* two peripheral abrupt-onset cues at the to-be-attended locations.

After a cue-target SOA, a probe was presented at one of the originally encoded VSWM locations and observers responded based on a memory-driven judgment (e.g., whether the probed location had been part of the memorized array, or a property of the memorized content at that location). The attentional bias on VSWM was operationalized as the reaction-time facilitation for probes at cued vs. uncued locations as a function of the probe's spatial position relative to the two cues.

**Spatial sampling.** Probes were placed at multiple locations along the line(s) connecting the two cues, at the cued locations themselves, between them, beyond them, and across the visual meridians. The full RT-by-position function characterizes the spatial *distribution* of the attentional bias — unimodal (a single peak between or around both cues), bipolar / multi-modal (two separate peaks at the cued locations), or otherwise.

**Cue–target predictability.** Independently manipulated: in some conditions the cues were highly predictive of the probed location; in others they were neutral / unpredictive. The contrast isolates the strategic / endogenous component of cue use from the automatic / exogenous component.

**Critical contrasts.**

- *Endogenous vs. exogenous orienting:* the central question of the paper.
- *Inter-cue distance:* near vs. far inter-cue distances test whether the distributional pattern depends on geometric separation of the two cues.
- *Meridian crossing:* probes that lie across a vertical or horizontal meridian test whether the bias respects hemifield boundaries.
- *Predictability:* high vs. low/neutral predictability test whether the spatial distribution is plastic with respect to strategic cue use.

The dependent measure is the RT facilitation function across probe positions; the key analysis is the shape of this function (uni- vs. multi-modal) as a function of cue type, distance, and predictability.

## 5. Results

Principal quantitative findings:

- **Endogenous double-cueing → unipolar bias.** The RT-facilitation function under two central symbolic cues showed a single broad peak rather than two distinct peaks at the cued locations. This was true at both near and far inter-cue distances and at both high and low predictability.
- **Exogenous double-cueing → distance-dependent multi-modality.** With two peripheral cues, the RT-facilitation function showed:
  - At short inter-cue distances, a single broad peak (uni-modal).
  - At larger inter-cue distances, two separated peaks at the cued locations (multi-modal / bipolar split).
- **Predictability scaling of exogenous effect.** The multi-modal exogenous pattern was magnified for highly predictive cues — the bias was larger overall and the two peaks more separated.
- **Predictability invariance of endogenous distribution.** The unipolar endogenous pattern was qualitatively unchanged across predictability conditions; only the overall magnitude varied.
- **Meridian effects.** The endogenous distribution was attenuated by meridian-crossing probes (a known signature of effortful, hemifield-bounded attentional deployment); the exogenous distribution was less constrained by meridians.
- **Replication across experiments.** The endogenous-unipolar / exogenous-multimodal dissociation held across experiments differing in encoding times, memory-set sizes, and probe procedures, supporting generality of the dissociation.

The headline pattern is the clean qualitative dissociation: *symbolic top-down cues* drive a single broad VSWM-attentional focus; *peripheral bottom-up cues* allow that focus to split into two when the cues are far enough apart and predictive enough.

## 6. Critique / limitations

The unipolar / multi-modal dichotomy is inferred from the *shape* of the RT-by-position function; in principle, a unimodal function with a flat top and a multi-modal function with shallow valleys could yield similar observable patterns. The authors guard against this by sampling many spatial positions, but a fully model-based parameterization (e.g., fitting one-Gaussian vs. two-Gaussian models) would tighten the inference.

The endogenous-vs-exogenous distinction is operationalized in the standard way — central symbolic vs. peripheral onset cues — but the two cue types also differ in stimulus energy, visual position, and temporal dynamics, all of which could in principle drive the dissociation independently of the endogenous/exogenous control distinction. Subsequent neural-level work would be needed to confirm that the architectural pathway difference, rather than the surface-feature difference, is doing the work.

The paper reads out attentional bias on VSWM via a *behavioral* probe; the neural realization (LIP / IPS for endogenous, SC / TPJ for exogenous, with relevant projections to PFC-WM areas) is inferred but not measured. The mapping from the behavioral distributional shape onto specific neural substrates is therefore a hypothesis, not a demonstration.

The link to van Moorselaar et al. (2014)'s capacity-of-1 finding is non-trivial: van Moorselaar's manipulation is over *feature*-based WM (color), and Botta & Lupiáñez's is over *spatial* attention biasing the VSWM map. Whether the two findings reflect the same single-active-template constraint, or qualitatively different rules for feature- vs. space-based template states, is unresolved. The retro-cue manipulation that fixed the capacity-of-1 in van Moorselaar is absent here; there is no direct comparison between a two-cue trial and a one-cue trial in the same observer.

The inter-cue distance modulating multi-modality could reflect attentional-spotlight zoom rather than true splitting — at small inter-cue distances, a single zoomed-in spotlight covers both cued locations and produces a unimodal pattern; only at large distances does a single spotlight become insufficient. A pure-zoom account is harder to reconcile with the endogenous-unipolar pattern, however, which is unimodal at all distances tested.

## 7. Connection to our work

Botta & Lupiáñez (2014) sits inside the WM–attention unification thread that anchors the user's program (Awh, Vogel & Oh 2006; Olivers et al. 2011; Carlisle et al. 2011; van Moorselaar et al. 2014; Kiyonaga & Egner 2013). Within that thread, Botta & Lupiáñez's specific contribution is the *spatial-multiple-cue* boundary condition: when more than one location must be biased in WM, what does the spatial distribution of the bias look like? Their answer — endogenous unipolar / exogenous multi-modal — gives the user's program a concrete behavioral target for the multi-peak regime of the central self-attention map.

**Multiple-cue WM as multi-template attention.** The recurrent ViT's softmax attention can in principle produce a single-peak (unimodal) or multi-peak (multi-modal) attention landscape. Van Moorselaar's capacity-of-1 result constrains the *feature-template* version of this to a single dominant peak. Botta & Lupiáñez's result refines the constraint for the *spatial* version: under top-down cueing, the single-peak regime is preserved; under bottom-up cueing, the system can hold a true multi-peak distribution at sufficient cue separation. For the user's multi-template attention in recurrent architectures, this licenses a regime split: the feedback / endogenous pathway produces a single-template attention map, but the bottom-up / exogenous pathway can produce a multi-template attention map. This is precisely the asymmetry implemented in the Feedback Transformer primitive (`the_user_architectural_program` §1): per-state Q/K/V projections combine via Hadamard products with the sensory Q/K, and the architectural latitude for multi-peak attention sits in the sensory pathway, not the feedback pathway.

**Connection to van Moorselaar 2014 template competition.** Van Moorselaar et al. (2014) ([vanmoorselaar2014_template_competition](research_db/papers/vanmoorselaar2014_template_competition.md)) shows that multiple memorized features collapse to a single active template; Botta & Lupiáñez show that multiple cued spatial locations can produce a multi-modal distribution under exogenous orienting. Together they bound the multi-template regime: in feature-based template-driven search, capacity-of-1 holds; in space-based, bottom-up-driven biasing, two peaks can co-exist. The architectural reading is that the *feedback* / top-down channel (where templates live in the user's program) is single-peak, while the *sensory* / bottom-up channel (where exogenous priority maps live) can be multi-peak. This is consistent with the unipolar / multi-modal dissociation reported here.

**Connection to Awh, Vogel & Oh 2006.** Awh, Vogel & Oh (2006) ([awh2006_attention_wm](research_db/papers/awh2006_attention_wm.md)) establish the WM-attention substrate at the conceptual level: spatial attention and spatial WM share the same priority-map substrate. Botta & Lupiáñez extend this by characterizing the *spatial distribution* of that shared substrate under multi-cue conditions, providing the high-resolution behavioral signature of the Awh–Vogel–Oh-style shared map.

**Connection to Olivers et al. 2011.** Olivers et al. (2011) ([olivers2011_wm_states_attention](research_db/papers/olivers2011_wm_states_attention.md)) proposes the active / accessory distinction; Botta & Lupiáñez's endogenous-unipolar result is consistent with one active spatial focus at a time under top-down control, while the exogenous-multi-modal result suggests the active-vs-accessory dichotomy may not apply cleanly to bottom-up spatial biasing.

**Connection to Carlisle 2011.** Carlisle et al. (2011) ([carlisle2011_attentional_templates](research_db/papers/carlisle2011_attentional_templates.md)) characterizes the formation of an attentional template under repeated use; Botta & Lupiáñez tests the spatial distribution side of the same phenomenon. The two complement each other: Carlisle is *which feature becomes a template*, Botta & Lupiáñez is *which space becomes biased*.

**Connection to Carlisle & Kristjánsson 2018.** Carlisle & Kristjánsson (2018) ([carlisle_kristjansson2018_wm_priming](research_db/papers/carlisle_kristjansson2018_wm_priming.md)) extends the template account into priming; Botta & Lupiáñez add the geometric / spatial-distribution dimension to the same multi-cue regime that priming studies probe in feature space.

**Connection to Kiyonaga & Egner 2013.** Kiyonaga & Egner (2013) ([kiyonaga_egner2013_wm_internal_attention](research_db/papers/kiyonaga_egner2013_wm_internal_attention.md)) articulates the WM = internal-attention identity claim. Botta & Lupiáñez's read-out — attentional bias *on VSWM contents* — is exactly the internal-attention regime Kiyonaga & Egner formalize, and the endogenous-unipolar / exogenous-multi-modal dissociation gives that internal-attention substrate its first detailed multi-cue distributional signature.

**Architectural implication for the recurrent ViT.** The recurrent ViT paper (2502.10955) cites this paper at ref [79]. The relevance is twofold. First, the endogenous-unipolar finding supports the single-peak softmax-attention regime the published model produces under recurrent-state-driven (top-down) bias: a sharp softmax that concentrates mass at one location is consistent with the canonical signature of human endogenous spatial attention under double-cueing. Second, the exogenous-multi-modal finding warns against assuming all attention maps must be single-peak: a bottom-up driven attention map *should* be permitted to split when two salient locations are separated, and the model's temperature / sharpening hyperparameters should not force unimodality in that regime. Practically, the model's softmax should remain flexible enough to express both single-peak (endogenous-style) and multi-peak (exogenous-style) attention. A direct empirical test in the model would be: present a single image with two equally-salient bottom-up targets, measure the model's attention map under a "free-viewing" (no recurrent-state bias) condition vs. a top-down-cued (recurrent-state-driven) condition, and check that the former produces a bimodal map at sufficient target separation while the latter collapses to a single peak — precisely the Botta-Lupiáñez dissociation.

**Architectural implication for PRISM v2.** PRISM v2's hierarchical FiLM and multi-memory commitments admit multiple feedback channels into the same prediction map. Botta & Lupiáñez suggests these channels should be *qualitatively asymmetric*: top-down memory feedback should drive a single-peak prediction, while bottom-up sensory feedback should be free to produce multi-peak. The natural architectural implementation is differential temperature / gain on the two pathways, with the feedback pathway running at higher effective sharpness than the sensory pathway. In PRISM v2's hierarchical FiLM (`PRISM_V2_PROPOSAL.md` §3.4), this corresponds to letting the higher-level memory channels (the endogenous-analog feedback) act through sharper modulation, while the lower-level sensory channels retain their natural multi-peak structure. This asymmetry is the architectural form of the endogenous-unipolar / exogenous-multi-modal dissociation.

**Cue-target predictability and the gain of feedback.** Botta & Lupiáñez's finding that predictability amplifies the exogenous multi-modal pattern but leaves the endogenous unipolar pattern qualitatively unchanged is itself an architectural cue. It suggests that the exogenous pathway is *gain-modulated* by predictability, while the endogenous pathway is already at ceiling on the unipolar regime. For the user's model, this maps onto a prediction: the bottom-up Hadamard-product contribution to the central attention map should scale with the reliability of bottom-up evidence, while the feedback contribution should drive toward sharp single-peak behavior independently of evidence reliability. This is a falsifiable hyperparameter prediction — the model's bottom-up vs. feedback gain schedule should differ in just this way.

**Summary.** Botta & Lupiáñez (2014) extend the WM-attention unification thread into multi-cue spatial territory, providing the qualitative dissociation that the central self-attention map should be capable of producing both unimodal and multi-modal distributions depending on the upstream driver — top-down feedback or bottom-up sensory drive. This is the empirical permission the user's program needs to allow the multi-peak regime in the bottom-up channel without giving up the single-template regime in the feedback channel.

## 8. Citations to follow

- `soto_heinke_humphreys2005_memory_attention_capture` — the foundational memory-driven capture paradigm whose spatial-distribution analogue Botta & Lupiáñez extend. Not yet in seed; high priority for the spatial-attention-as-WM-bias thread.
- `botta_santangelo2010_endogenous_exogenous_vswm` — Botta et al. (2010, QJEP) on endogenous-vs-exogenous attention effects on VSWM. Direct precursor to this paper; would clarify whether the single-cue version of these effects is consistent. Not yet in seed.
- `posner1980_orienting_attention` — the foundational endogenous / exogenous distinction. Probably already in seed under a different ID; verify.
- `castiello_umilta1990_size_attentional_focus` — early demonstration of the zoom-lens metaphor for attentional focus size, relevant to the inter-cue-distance modulation. Not yet in seed.
- `awh_pashler2000_evidence_split_attention` — empirical demonstration of split attention in perception, the parent finding that Botta & Lupiáñez extend into VSWM. Not yet in seed.
- `mcmains_somers2004_multiple_spotlights` — fMRI evidence for multiple attentional spotlights, neural analogue of the multi-modal exogenous pattern. Not yet in seed.
- `bundesen_habekost_kyllingsbaek2005_neural_theory_visual_attention` — neural-theory-of-visual-attention framework relevant to the WM-attention-priority substrate. Listed in the user's notes' debts list (the_user_architectural_program §8). Not yet in seed.
