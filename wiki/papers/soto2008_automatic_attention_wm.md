---
id: soto2008_automatic_attention_wm
title: "Automatic guidance of attention from working memory"
authors:
  - "Soto, David"
  - "Hodsoll, John"
  - "Rotshtein, Pia"
  - "Humphreys, Glyn W."
year: 2008
venue: "Trends in Cognitive Sciences"
doi: "10.1016/j.tics.2008.05.007"
arxiv: ""
url: "https://www.sciencedirect.com/science/article/abs/pii/S1364661308001769"
tags:
  - visual-working-memory
  - attention-capture
  - top-down
  - templates
  - review
concepts:
  - top-down-feedback
  - coalition_resource_competition
  - bidirectional_hierarchical_feedback
related:
  - olivers2011_wm_states_attention
  - awh_jonides2001_overlapping_attention_wm
  - kiyonaga_egner2013_wm_internal_attention
  - carlisle2011_attentional_templates
  - carlisle_kristjansson2018_wm_priming
  - berggren_eimer2018_wm_load
  - vanmoorselaar2014_template_competition
  - postle2006_wm_emergent
  - panichello_buschman2021_shared_mechanisms
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

# Automatic guidance of attention from working memory

## 1. Abstract

> "Recent research has shown interactions between the process of keeping information 'online' in working memory, and the processes that select relevant information for a response. In particular, our ability to select stimuli in the environment can be modulated by whether the stimuli match the current contents of working memory. Guidance of selection from working memory occurs automatically, even when it is detrimental to performance. Neurophysiological data, from functional brain imaging, indicate that the interaction between working memory and attention is based on neuronal mechanisms distinct from the processes mediating 'bottom-up' priming effects from implicit memory. We discuss the importance of 'top-down' influences from working memory on the 'early' deployment of attention and on the processes that gate visual information into awareness." (Soto, Hodsoll, Rotshtein & Humphreys 2008, *Trends in Cognitive Sciences* 12(9):342-348, abstract.)

## 2. Why this matters for us

Soto et al. 2008 is the field-defining review of *WM-to-attention guidance*: items held in working memory automatically bias attention toward matching stimuli in the visual field, even when participants are explicitly told to ignore them and even when the bias is performance-hurting. For the user's program, this is the cognitive-psychology source of the *content-as-prior* mechanism: the contents of memory are not passive — they are *active priors* that modify the priority map that drives covert/overt attention. The user's architecture is built on this premise. The recurrent ViT's hidden state $H^{(t-1)}$ is queried during the attention computation over the current image, and the attention map is *conditioned* on the memory contents — exactly the WM-bias-on-selection mechanism Soto et al. document. The paper's most important architectural implication is that *no separate "attention template" component is needed*: the working memory itself, by virtue of being queried during attention computation, *is* the attentional template.

## 3. Key claims

1. Items held in WM bias attention toward matching stimuli in the visual field, even when participants are explicitly told to ignore them.
2. The bias is *automatic*: it occurs even when memory-matching items act as distractors and impair task performance — i.e., subjects cannot strategically suppress the effect.
3. The WM-attention coupling is mechanistically *distinct* from implicit/repetition priming (different neural signatures in fMRI and ERP).
4. Top-down WM templates modulate *early* stages of visual processing (extrastriate cortex, V4) rather than only late decision stages.
5. WM contents can *gate access to conscious awareness* (e.g., in attentional-blink and binocular-rivalry paradigms).
6. Capture occurs only when the item is *actively maintained* in WM, not merely passively encoded (perceived but not held).
7. The dorsolateral PFC and posterior parietal cortex are central nodes for biasing the priority map.
8. WM-to-attention guidance is *one* mechanism by which top-down control of attention is implemented; the broader implication is that attention and WM are tightly interleaved, not separable systems.

## 4. Methods

This is a narrative review synthesizing behavioral, eye-tracking, ERP, and fMRI studies — predominantly variants of the *Soto-lab WM-cued visual search paradigm*: a memorized sample (color/shape) is presented, followed by a search array in which the matching item is sometimes the target and sometimes a distractor. The principal manipulations: (a) cue validity (memorized item matches target on 50% / 33% / 0% of trials, to test whether guidance survives even when it is uninformative or counterproductive); (b) intervening verbal load and articulatory suppression to isolate the contribution of visual vs verbal WM; (c) attentional-blink and binocular-rivalry paradigms to test the consciousness-gating claim; (d) fMRI to localize the bias-generating regions (PFC, posterior parietal, extrastriate cortex). The review integrates these into the *automatic-guidance* synthesis: across paradigms, cues, and validity manipulations, the WM-matching item gets prioritized — diagnostic of automaticity.

## 5. Results

Key empirical anchors consolidated in the review:

- **Cuing benefit when WM cue matches target:** typically ~30-50 ms RT facilitation in visual search.
- **Cost when WM-matching item is a distractor:** ~20-40 ms slowing, present even at low cue validity (when the cue is uninformative or actively misleading).
- **Capture survives when participants are told the matching item will never be the target** — the strong "automaticity" demonstration; subjects cannot strategically suppress the bias even when given explicit incentive to do so.
- **fMRI:** enhanced BOLD in V4/LOC and SPL/IPS for displays containing a WM-matching distractor relative to neutral; the bias generates an *early* visual-cortex signature.
- **ERP:** the N2pc to the WM-matching distractor (~200-300 ms post-display) is the electrophysiological signature of early attentional capture by the WM template.
- **Articulatory suppression abolishes verbal WM cuing effects** but leaves visual cuing intact, dissociating the visual from verbal WM contributions.
- **Dual-task loading on the central executive** reduces but does not abolish guidance — the bias is partially automatic but can be modulated by executive load.
- **Consciousness-gating** — items matching WM contents are more likely to break through the attentional blink and to dominate in binocular rivalry, demonstrating that WM-to-attention bias reaches all the way to conscious access.

## 6. Critique / limitations

The "automaticity" claim has been substantially contested and the paradigm has methodological boundary conditions.

- **"Automaticity" claim contested:** Downing & Dodds (2004), Woodman & Luck (2007), and Carlisle & Woodman (2011) show that the guidance is strongly modulated by *strategy* and *cue validity*; under conditions where guidance is consistently counterproductive, subjects can substantially suppress it. The bias is therefore not strictly automatic in the Posnerian sense.
- **Olivers (2009)** and the broader Olivers/Roelfsema framework ([olivers2011_wm_states_attention](olivers2011_wm_states_attention.md)) argues effects depend on whether the WM cue is in an "active" or "accessory" state — only the active template guides attention; accessory items in WM do not. This undermines a strict any-item-in-WM-guides account.
- **The review draws heavily on the authors' own paradigm**; convergence across labs and tasks is partial. Some lab paradigms (e.g., Theeuwes-lab additional-singleton) show WM-driven guidance is much weaker or absent.
- **Verbal vs visual contributions to WM-driven capture are not cleanly disentangled** in many cited studies; the dissociation requires careful articulatory-suppression control.
- **Many cited experiments use only 1 item in WM**; generalization to multi-item WM — and the related "single-item template" hypothesis (Olivers; van Moorselaar) — is unresolved in the review.
- **Imaging evidence is correlational**; causal role of PFC bias signals not established (no TMS/lesion data at time of review).
- **Boundary conditions for capture** (set size, cue duration, intervening task, retention interval) are not systematically characterized.
- **No quantitative model of bias strength** as a function of WM content fidelity, attentional set, or competition with non-template-matching salient items.

## 7. Connection to our work

Soto et al. 2008 is the cognitive-psychology foundation of one of the user's most-load-bearing architectural commitments: *memory contents act as priors on attention*.

**Touchpoint 1: WM-as-attentional-template is the architectural core of the recurrent ViT.** The user's recurrent ViT integrates the previous memory state $H^{(t-1)}$ into the current attention computation: $A^{(t)} = \text{softmax}(Q(x^{(t)}, H^{(t-1)}) K(x^{(t)}, H^{(t-1)})^T)$. The attention map is *conditioned on memory contents*, which is *exactly* the Soto-et-al WM-template mechanism implemented in an attention-based architecture: items in $H^{(t-1)}$ bias the attention weights on the current input toward patches that match memory. The user's architecture therefore *automatically reproduces* the cardinal Soto-et-al phenomenon — WM contents guide attention — by construction. The biological warrant: this is not an engineering convenience, it is the empirically-correct architectural choice for biologically plausible attention-WM interaction.

**Touchpoint 2: automaticity as architectural inevitability.** The Soto-et-al automaticity finding — subjects cannot suppress WM-driven capture even when it hurts performance — has an immediate architectural reading: the attention computation is *structurally conditioned* on memory and cannot be selectively prevented from being so. In the user's recurrent ViT, this is true by construction: $H^{(t-1)}$ enters the attention computation as part of Q/K computation; there is no mechanism to "turn off" the memory's contribution. The architecture therefore predicts the empirical phenomenon by virtue of its structure, rather than as a learned property. This is the user's program at its strongest: the architecture *is* the theory.

**Touchpoint 3: early modulation of visual cortex — biological warrant for early-layer feedback.** The fMRI and ERP evidence that WM-driven biasing affects *early* visual processing (V4, N2pc at ~250 ms post-display) is the biological warrant for the user's commitment to feedback that reaches deep into the early-layer representations. The descending pathway from $H^{(t-1)}$ should modulate not only deep attention layers but should also bias the early/shallow representations — exactly what [bidirectional_hierarchical_feedback](../concepts/bidirectional_hierarchical_feedback.md) commits to. Soto et al. provide the empirical demonstration that this early biasing is the actual mechanism by which WM influences perception, validating the user's architectural commitment to descending feedback that reaches V1-V2-equivalent layers.

**Touchpoint 4: the active/accessory distinction maps onto the user's multi-compartmental memory.** The Olivers-Roelfsema active/accessory distinction — only items in the "active" WM state guide attention, accessory items do not — has a clean architectural homolog in the user's multi-compartmental memory: items in $M_{fast}$ (which directly conditions the current attention computation) play the active role, while items in $M_{slow}$ (which influences attention only via slow modulation) play the accessory role. This predicts a dissociation: probing the architecture should show that content in $M_{fast}$ produces stronger Soto-style capture than content in $M_{slow}$, matching the empirical active/accessory dissociation. The architectural design therefore naturally accommodates the empirical refinement of the original Soto-et-al automaticity claim.

**Touchpoint 5: bidirectional WM-attention coupling — the architectural symmetry.** Soto et al. focus on WM → attention (memory biases what is attended). The complement direction — attention → WM (only attended items get encoded into the next memory state) — is the symmetric phenomenon that the user's architecture also produces by construction: the attention map weights the contributions to the memory update, so items that win attention get integrated into memory. The user's architecture is therefore a *bidirectional* WM-attention coupling, of which Soto et al.'s WM → attention pathway is one half. The biological warrant for the symmetry comes from the Bays-Husain attention-mediated allocation finding (the complement half).

**Touchpoint 6: convergence with Panichello-Buschman and the shared-substrate thesis.** Soto et al. 2008 documents the *behavioral* phenomenon (WM contents guide attention); Panichello & Buschman 2021 ([panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md)) demonstrates the *neural* mechanism (PFC populations are shared between WM and attention control). The convergence is the cardinal evidence for the user's *shared-substrate* architectural commitment: there is no separate "attention module" and "memory module" in the user's design; they share the central self-attention substrate. The user's program is therefore biologically licensed at both the behavioral and the neural level.

**Touchpoint 7: implications for the change-detection task.** The recurrent ViT and PRISM are evaluated on change detection. The Soto-et-al lens predicts: the recurrent ViT's attention map on the current frame should show *enhanced weight on patches that match the previously-stored content* (analog of the Soto WM-matching capture). Empirically validating this — extracting attention maps and showing that previously-seen targets attract attention weight — would be a strong demonstration that the architecture has captured WM-to-attention bias rather than relying on bottom-up salience alone. This is a clean, novel empirical analysis the user can perform on the existing models.

## 8. Citations to follow

- [olivers2011_wm_states_attention](olivers2011_wm_states_attention.md) — different states in WM guide attention; the active/accessory refinement of the Soto-et-al automaticity claim. In seed.
- `carlisle_woodman2011_strategic_automatic_wm_guidance` — *JEP:HPP* — strategic vs automatic guidance; the principal challenge to the strict-automaticity claim. Not in seed.
- [vanmoorselaar2014_template_competition](vanmoorselaar2014_template_competition.md) — only one item guides attention; the single-template hypothesis. In seed.
- `gunseli_meeter_olivers2014_strategic_preparation` — *Cognition* — strategic preparation modulates capture. Not in seed.
- [carlisle2011_attentional_templates](carlisle2011_attentional_templates.md) — attentional templates in WM; the template-formation framework. In seed.
- [kiyonaga_egner2013_wm_internal_attention](kiyonaga_egner2013_wm_internal_attention.md) — "Working memory as internal attention"; the conceptual extension. In seed.
- `hollingworth_hwang2013_eye_movement_wm_guidance` — *Phil Trans B* — eye-movement evidence for WM-driven guidance. Not in seed.
- `sasin_nieuwenstein2016_attentional_blink_capture` — *JEP:HPP* — capture during the attentional blink. Not in seed.
- [berggren_eimer2018_wm_load](berggren_eimer2018_wm_load.md) — ERP dissociation of template-based vs priming guidance; the load manipulation. In seed.
- `foerster_schneider2019_naturalistic_search` — *Cognition* — WM-driven capture in naturalistic search. Not in seed.
- [awh_jonides2001_overlapping_attention_wm](awh_jonides2001_overlapping_attention_wm.md) — the foundational attention-WM overlap paper; the cognitive-psychology precursor. In seed.
- [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) — the shared-substrate neural mechanism; the modern convergence point. In seed.
