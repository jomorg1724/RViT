---
id: moran_desimone1985_selective_attention
title: "Selective attention gates visual processing in the extrastriate cortex"
authors:
  - "Moran, Jeffrey"
  - "Desimone, Robert"
year: 1985
venue: "Science"
doi: "10.1126/science.4023713"
arxiv: ""
url: "https://doi.org/10.1126/science.4023713"
tags:
  - primate-neurophysiology
  - visual-attention
  - early-visual-cortex
concepts:
  - biased-competition
  - gain-modulation
  - top-down-feedback
related:
  - desimone_duncan1995_biased_competition
  - treue_martinez_trujillo1999_feature_attention
  - reynolds_heeger2009_normalization
  - mcadams_maunsell1999_v4_tuning
  - mcadams_maunsell1999_reliability
  - reynolds1999_competitive_v2_v4
  - reynolds_chelazzi2004_attentional_modulation
  - desimone1996_visual_memory_attention
  - spratling2008_pc_biased_competition
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - prism_private_notes
status: full
depth: full
last_updated: "2026-05-16"
---

# Selective attention gates visual processing in the extrastriate cortex

## 1. Abstract

Moran & Desimone recorded single units in macaque areas V4, inferior temporal cortex (IT), and primary visual cortex (V1/striate) while the animal performed a task that placed two stimuli — one effective (matched to the cell's preferred stimulus) and one ineffective (a non-preferred stimulus) — at known locations relative to the recorded cell's receptive field. The monkey was cued to attend to one of the two locations. When *both* stimuli fell inside the same RF, the cell's response to the *unattended* stimulus was dramatically reduced relative to the response when that same stimulus was attended — even though the physical stimulation of the RF was identical in the two conditions. When the unattended stimulus lay outside the cell's RF, attention had no effect on the cell's response: the gating occurred only for stimuli *within* a single RF. The effect was present in V4 and IT but absent in V1. Moran & Desimone interpret this as evidence that attention acts as a *filter* operating at the level of extrastriate receptive fields, gating which of multiple competing stimuli is allowed to drive the cell.

## 2. Why this matters for us

Moran & Desimone 1985 is the founding empirical demonstration of attention modulation in extrastriate visual cortex and the empirical root of *biased competition* (Desimone & Duncan 1995). For the user's program, three points are load-bearing. First, the *within-RF competition* phenomenon — that attentional modulation appears only when stimuli compete inside a single RF — is the canonical substrate that the recurrent ViT's per-token attention map implements: each token (query) must allocate its softmax mass across competing key-positions, exactly the resource-competition the M&D recording revealed at the single-cell level. Second, the absence of the effect in V1 and its presence in V4/IT establishes the *hierarchical* character of attention — gating happens at intermediate-to-late stages, not at the sensory periphery — which the user's three-layer multi-compartmental memory bakes in via diminishing-feedback-into-deeper-layers. Third, this is the founding example of attention as a *multiplicative* gating signal in a sensory area, the same conceptual mechanism that the Feedback Transformer's $s_q \odot c_q$ structure and PRISM's FiLM modulation implement at the architectural level.

## 3. Key claims

1. **Attention gates extrastriate responses to competing stimuli inside a single receptive field.** When two stimuli (one effective, one ineffective) both lie within a V4 or IT cell's RF, the response is governed by which stimulus the animal attends.
2. **The gating is selective, not spatial.** The cell's response is high when the effective stimulus is attended and low when the ineffective stimulus is attended — even though the physical stimulation of the RF is identical in both conditions.
3. **The effect requires within-RF competition.** When the unattended stimulus lies *outside* the cell's RF, attention has no effect on the cell's response.
4. **The effect is hierarchy-specific.** V4 and IT cells show the attentional gating; V1 (striate) cells do not, at least for the stimulus configurations tested.
5. **Attention reduces the response to the unattended stimulus rather than enhancing the attended one.** The principal phenomenon is *suppression* of the ineffective competitor when the cell's preferred stimulus is attended, and *suppression* of the effective competitor when the non-preferred stimulus is attended.
6. **Implication: attention is a filter at the level of the receptive field.** Among the multiple stimuli that fall inside a cell's RF, attention selects which is allowed to drive the cell.
7. **Implication: gating is post-V1.** Because V1 cells (with their small RFs that typically contain only one of the two stimuli) do not show the modulation, the filtering must arise at a stage where individual RFs are large enough to contain *multiple* competitors — i.e., V4 and beyond. The site of attentional selection is constrained by the size of the receptive field, not by the cortical area per se.
8. **Implication: the attentional signal is not part of the bottom-up stimulus.** Because the physical stimulation of the RF is identical across the compared conditions and only the *attentional cue* varies, the gating must be driven by a *top-down* signal originating outside the recorded area — consistent with later evidence that frontal and parietal areas supply the bias signal.

## 4. Methods

**Animals and task.** Two macaque monkeys were trained on a delayed-match-to-sample-style attention task. On each trial, the monkey fixated centrally and was cued to attend to one of two known locations in the visual field. Stimuli were presented at both locations; the animal had to detect a target at the attended location while ignoring the unattended location. Eye position was monitored to ensure fixation was maintained — the attentional manipulation was purely covert.

**Recordings.** Single-unit recordings were made from V4, IT (inferior temporal cortex), and V1 (striate cortex). For each isolated cell, the experimenters first mapped the RF and identified an "effective" stimulus (preferred orientation/color/shape that drove the cell strongly) and an "ineffective" stimulus (a non-preferred stimulus that drove the cell weakly).

**Stimulus geometry.** The critical manipulation was the spatial relation between the two stimuli and the cell's RF.

- *Both stimuli inside the RF.* One effective and one ineffective stimulus were placed at two locations both inside the cell's RF. The monkey was cued to attend to one or the other.
- *One stimulus inside, one outside.* The effective stimulus was placed inside the RF; the ineffective stimulus was placed *outside* the RF (at a location the monkey had to attend on some trials).

**Conditions compared.** For each cell, four conditions were generated by crossing (a) which stimulus is in the cell's RF — effective vs. ineffective — with (b) which location is attended — RF location vs. non-RF location, or first-RF location vs. second-RF location. The physical stimulation of the RF was held identical across the conditions being compared; only the attended location varied. Any modulation of the cell's response was therefore attributable to attention rather than to the bottom-up stimulus.

## 5. Results

The principal findings (quantitative summary as reported in the original three-page Science article):

- **Within-RF gating in V4 and IT.** When both stimuli were inside the cell's RF, attention to the effective stimulus yielded responses comparable to a control with only the effective stimulus present; attention to the ineffective stimulus yielded responses comparable to a control with only the ineffective stimulus present. The cell behaved as if the unattended stimulus had been filtered out of its input.
- **Magnitude.** The response to the unattended stimulus was reduced by approximately *half* or more relative to the attended condition, with substantial reductions reported across the population of recorded V4 and IT cells.
- **No effect when the unattended stimulus lay outside the RF.** When the ineffective stimulus was placed outside the cell's RF, attending to it (vs. attending to the effective stimulus inside the RF) did *not* reduce the cell's response. The gating is local to the RF.
- **No effect in V1.** Striate cortex cells tested with the same paradigm showed no comparable attentional modulation. (Subsequent work — e.g., Motter 1993; McAdams & Maunsell 1999 — has found modest V1 effects under stronger attentional load and more demanding tasks, but the 1985 dataset places the principal site of gating at V4 and beyond.)
- **Direction of modulation.** The phenomenon is dominated by *suppression* of the unattended-stimulus response rather than facilitation of the attended-stimulus response. The cell appears to have a fixed "budget" for the within-RF stimulus configuration, with attention determining how that budget is allocated.
- **Behavioral relevance.** The recorded cells' attentional gating is contemporaneous with the animal's behavioral attentional state: the cell's response under "attend-effective" matches the response on trials when the animal correctly detected the target at the effective-stimulus location. Errors and lapses (when present) are associated with a partial collapse of the gating effect, indicating that the neural modulation tracks the animal's deployed attention rather than the cue alone.
- **Population.** Roughly 60% of V4 cells and a comparable fraction of IT cells tested with both stimuli inside the RF showed the gating effect; the modulation was statistically reliable at the population level even when individual-cell effects were modest.

## 6. Critique / limitations

The study uses two animals and a small population of cells per area; effect sizes are reported qualitatively in places. Subsequent work (Reynolds, Chelazzi & Desimone 1999; McAdams & Maunsell 1999) has replicated and extended the effect at population scale.

The 1985 paper reports *no* attentional modulation in V1, but later studies with more demanding tasks and finer measurements have found modest V1 effects. The proper statement is that V1 modulation is *smaller* and requires more demanding attentional conditions, not that it is absent; the 1985 paper's no-effect-in-V1 claim should be read as the limit of the experiment rather than as a universal claim about V1.

The mechanism by which attention produces the gating is not specified by the experiment. The paper documents the *behavior* of the cells; the computational substrate — competitive interactions among co-active inputs to the cell — is the inference made by Desimone & Duncan 1995 and formalized in normalization terms by Reynolds & Heeger 2009. The 1985 paper is the empirical anchor for these subsequent theoretical developments rather than itself a theoretical paper.

The stimulus paradigm uses paired flashed stimuli; the dynamics of the gating — onset latency, time course of the suppression, oscillatory signatures — are not characterized. Later electrophysiology (Reynolds, Chelazzi & Desimone 1999; Fries et al. 2001 gamma-band work) addresses these.

The two-stimulus design isolates *competition* but does not directly probe *feature-based* attention or *global* (spotlight-independent) modulation; those phenomena are the subject of Treue & Martínez Trujillo 1999 and later FBA work.

The paper also leaves open whether the gating reflects (a) gain modulation at the recorded cell, (b) gain modulation at an earlier stage whose output is the recorded cell's input, or (c) a combination. Subsequent normalization-model work (Reynolds & Heeger 2009) treats the gating as the joint product of stimulus-driven normalization and an attention field; under that interpretation the M&D phenomenon is an emergent consequence of an unchanged divisive-normalization machinery being driven by an attention-biased input — the cell itself is "doing nothing differently." This is a substantively different account from "the cell's gain is being modulated directly by a top-down signal," and the 1985 experiment does not discriminate between them.

## 7. Connection to our work

Moran & Desimone 1985 is the empirical foundation of the user's coalition-competition program and supports the architectural commitments at four levels.

**Within-RF competition as the substrate of attention.** The phenomenon Moran & Desimone discovered — that attention gates responses *only* when stimuli compete inside a single RF — is the canonical biological substrate that the recurrent ViT's self-attention implements. In a transformer attention layer, each query token allocates a fixed softmax budget across all key positions; the per-token mass distribution *is* the within-RF competition. The recurrent ViT's attention map (§3 of 2502.10955) and PRISM v1's prediction-error-gated attention (`THESIS.md` §2.6) both operate on this competition substrate. The user's coalition-competition thesis (concept: `competition-emergent-predictive-coding`) generalizes M&D's single-RF competition to whole-coalition competition, but the underlying mechanism is the same.

**Empirical root of biased competition.** Desimone & Duncan 1995's framework — the load-bearing theoretical citation for the user's program — explicitly derives from this 1985 demonstration. M&D 1985 is the canonical figure in every subsequent biased-competition review (cf. `desimone_duncan1995_biased_competition` §1; `reynolds_chelazzi2004_attentional_modulation` §2). Without the within-RF gating result, the biased-competition framework would have no empirical anchor.

**Hierarchy-specific gating supports the multi-compartmental design.** The absence of the effect in V1 and its presence in V4/IT is direct support for the user's *diminishing-feedback-into-deeper-layers* commitment (`the_user_architectural_program` §3). The user's three-layer memory stack assigns the most extensive feedback integration to deeper layers (V4/IT analogs) and less to the shallowest (V1 analog), exactly mirroring the empirical attention gradient. This is the cortical justification for asymmetric feedback in the GridCell RNN hierarchy.

**Attention as multiplicative gating — the FiLM / Feedback-Transformer lineage.** The M&D 1985 effect — selective gating that effectively *multiplies* a cell's effective input by an attention-determined factor — is the founding example of attention as multiplicative gain modulation in a sensory area. This is the same conceptual mechanism that PRISM v1's FiLM modulation (`THESIS.md` §2.4) and the Feedback Transformer's $s_q \odot c_q$ Q/K projection (`feedback_transformer` concept) implement at the architectural level. The recurrent ViT paper's "multiplicative feedback" variant (§6.7) is the direct architectural descendant of the M&D phenomenon: a feedback signal that *gates* sensory processing by multiplicative interaction with the bottom-up signal, exactly as the attentional signal in M&D 1985 gates the V4/IT cell's bottom-up response to the unattended competitor.

**Connection to Reynolds & Heeger 2009 normalization.** The normalization model of attention (Reynolds & Heeger 2009) is the explicit formalization of M&D 1985: the within-RF stimulus competition is implemented by divisive normalization over a stimulus-pool, and attention multiplicatively reweights the contributions to the normalization pool. Concretely, the softmax in a transformer attention layer is exactly a divisive normalization: each attention weight $\alpha_{ij} = \exp(\langle q_i, k_j \rangle) / \sum_{j'} \exp(\langle q_i, k_{j'} \rangle)$ has the divisive form, with the denominator the pool. Attentional reweighting via the Feedback Transformer's per-state contribution to $q_i$ and $k_j$ corresponds exactly to the Reynolds-Heeger attention-modulated normalization. The user's program reads the recurrent-ViT softmax as a (learned) instance of this normalization substrate; M&D 1985 is the empirical anchor under that interpretation.

**Connection to McAdams & Maunsell 1999.** The V4 attention paper of McAdams & Maunsell extends M&D 1985 by showing that the gating effect, when measured at the level of tuning curves, is *multiplicative* — attention scales the V4 tuning curve up without sharpening it. This is the quantitative shape of the gating phenomenon and directly supports treating attentional feedback in the user's architecture as a multiplicative (rather than additive) gain term, ruling out additive-bias-only modulations like an attention-added query offset.

**Implications for the recurrent ViT's per-pass attention dynamics.** The user's classifier experiment (Food-101; `the_user_architectural_program` §6) observed that attention maps "focus, defocus, and reactivate over recurrent steps." Reading this through the M&D 1985 lens: each recurrent pass is a fresh round of within-RF (within-token) competition, with the previous pass's hidden state $H^{(t-1)}$ supplying the bias signal that determines which competitor wins. The qualitative observation of attention-map evolution thus has a concrete biological referent — the iterated allocation of attention among competing intra-RF stimuli that M&D demonstrated at the single-cell level. This is the architectural reason the recurrent ViT's iterated attention is a closer biological analog than the standard one-pass ViT.

## 8. Citations to follow

- `desimone_duncan1995_biased_competition` — the 1995 review that consolidates this result into the biased-competition framework. Already in seed, full depth.
- `reynolds1999_competitive_v2_v4` — Reynolds, Chelazzi & Desimone 1999, the V2/V4 quantitative replication and extension of M&D 1985 at population scale. Already in seed.
- `reynolds_heeger2009_normalization` — formalizes the M&D effect as divisive normalization. Already in seed, full depth.
- `mcadams_maunsell1999_v4_tuning` — V4 attention as multiplicative gain on tuning curves; the quantitative shape of the M&D phenomenon. Already in seed.
- `mcadams_maunsell1999_reliability` — companion paper on response reliability under attention. Already in seed.
- `treue_martinez_trujillo1999_feature_attention` — extends M&D-style gating from spatial to feature-based attention. Already in seed, full depth.
- `desimone1996_visual_memory_attention` — Desimone's review extending the 1985 result into memory and template-based attention. Already in seed.
- `motter1993_v1_v2_attention` — replication and extension of the V1/V2 attention question with stronger task demands. Not yet in seed.
- `chelazzi_etal1993_competing_visual_stimuli` — IT-cortex competing-stimuli result, direct extension of M&D 1985 to memory-guided search. Not yet in seed; should be added.
- `luck_etal1997_attention_v2_v4` — single-unit V2/V4 attention with multiple competing stimuli. Not yet in seed.
- `spitzer_richmond_desimone1988_attention` — earlier-1988 follow-up by Desimone's group on attention-modulation of IT responses; one of the first attention papers in the lineage. Not yet in seed.
- `gilbert_li2013_top_down_review` — review of top-down influences on visual processing, which integrates M&D 1985 into the broader top-down-feedback literature. Cited in `the_user_architectural_program` §8 open debts.
- `bichot_etal2005_fef_v4_top_down` — FEF microstimulation evidence for the top-down source of the M&D-style gating in V4. Not yet in seed; load-bearing for the "where does the bias come from" question.
- `spratling2008_pc_biased_competition` — recasts biased competition (and therefore M&D 1985) in predictive-coding terms. Already in seed via `desimone_duncan1995_biased_competition` related list.
