---
id: carlisle_kristjansson2018_wm_priming
title: "How visual working memory contents influence priming of visual attention"
authors:
  - "Carlisle, Nancy B."
  - "Kristjánsson, Árni"
year: 2018
venue: "Psychological Research"
doi: "10.1007/s00426-017-0866-6"
arxiv: ""
url: "https://link.springer.com/article/10.1007/s00426-017-0866-6"
tags:
  - working-memory
  - visual-attention
  - psychophysics
concepts:
  - attentional-template
  - cueing-effect
related:
  - carlisle2011_attentional_templates
  - awh2006_attention_wm
  - olivers2011_wm_states_attention
  - desimone1996_visual_memory_attention
  - panichello_buschman2021_shared_mechanisms
  - vanmoorselaar2014_template_competition
  - kiyonaga_egner2013_wm_internal_attention
  - failing_theeuwes2018_selection_history
  - desimone_duncan1995_biased_competition
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - vit_paper_ref_21
status: full
depth: full
last_updated: "2026-05-16"
---

# How visual working memory contents influence priming of visual attention

## 1. Abstract

Models of attentional selection routinely distinguish goal-directed (top-down) and stimulus-driven (bottom-up) control. A growing body of work has identified a third channel — selection history, including intertrial priming — that biases selection independently of either. Carlisle & Kristjánsson examine the interaction between two memory systems that contribute to this third channel: the explicit visual working memory (WM) that holds an attentional template, and the implicit short-term memory that drives intertrial *priming of pop-out* (PoP).

Participants performed a colour pop-out search task in which target and distractor colours could repeat or swap between consecutive trials. Concurrently, they maintained a colour swatch in WM whose identity could match either the upcoming target, the upcoming distractors, or be unrelated. The standard PoP signature — faster search when target/distractor colours repeat than when they swap — was measured as a function of the WM content.

The principal finding is asymmetric. When WM held a *distractor-matching* colour, intertrial priming was disrupted: the speed-up from repeated target/distractor identities was attenuated or eliminated. When WM held a *target-matching* colour, priming was preserved (and search overall was faster, replicating standard WM-attention coupling effects). The implicit priming system and the explicit WM template can therefore conflict with one another, and explicit WM contents can override or interfere with the priming signal when they assign a feature to the opposite role (distractor vs target).

The authors conclude that priming and WM-based templates are *separable but interacting* sources of top-down bias on the attentional priority map. Both feed into the same selection bottleneck, and when their signals diverge, the system does not simply sum them: the explicit template can suppress the priming-driven bias. This places selection-history/priming on the same conceptual footing as WM templates — both are internally-maintained biases on attention — while preserving the empirical dissociation between active rehearsal and passive trace.

## 2. Why this matters for us

This paper supplies the empirical evidence that **selection history (priming) is a distinct, third channel of attentional control** alongside top-down templates and bottom-up salience, and that this third channel is implemented by a *different* memory system from the WM-based template. For the user's architectural program — and especially for any multi-compartmental memory account of attention — this is decisive: a faithful model of the attentional priority map must integrate at least two internal memory streams (template + priming trace) with the bottom-up sensory drive. A single recurrent state that mixes them together cannot reproduce the Carlisle-Kristjánsson dissociation.

For the recurrent ViT and PRISM, the result motivates an explicit fast/slow or template/trace separation in the memory architecture, and provides a behavioural benchmark (target-WM vs distractor-WM × repeat vs swap) on which any such architecture's interaction signature can be tested.

## 3. Key claims

1. **Priming of pop-out is a robust intertrial bias.** Repeating target and distractor colours across successive pop-out trials speeds search; swapping them slows it, replicating the canonical Maljkovic & Nakayama (1994) PoP effect.
2. **Holding a target-matching colour in WM facilitates search.** Replicates the classical Soto/Olivers WM-attention finding: WM contents that match the search target are an additional source of top-down bias.
3. **Holding a distractor-matching colour in WM disrupts intertrial priming.** The standard PoP advantage from repeated target/distractor identities is attenuated or eliminated when WM holds the distractor colour.
4. **The disruption is content-specific, not load-related.** Adding a colour to WM that is unrelated to the search display does not eliminate priming — the effect requires conflict between the explicit WM content and the implicit priming trace.
5. **WM templates and priming are separable memory systems.** The fact that explicit WM contents can override priming, but priming nonetheless persists under WM load when no conflict exists, demonstrates that the two are not the same mechanism.
6. **Both systems feed a common priority map.** The interaction between WM contents and priming is asymmetric (distractor-WM disrupts; target-WM facilitates) — consistent with both signals being integrated into a single map of attentional priority, where their contributions can be additive or subtractive depending on assignment.
7. **Selection history is a third control channel.** The findings position priming on a par with top-down (template) and bottom-up (salience) control, and identify WM as the arbitrator between conflicting top-down sources.

## 4. Methods

Adult human participants performed a colour pop-out visual search task while concurrently holding a colour in visual working memory. Each trial unfolded as:

1. **Memory cue.** A coloured swatch presented at fixation specified the colour to maintain in WM for later report.
2. **Retention interval.** A brief delay during which the WM colour was held.
3. **Search display.** A pop-out array containing one target of a unique colour among uniformly-coloured distractors. The participant identified a feature of the target (typically a notch orientation) as quickly and accurately as possible.
4. **Memory probe.** A colour was shown; participants reported whether it matched the swatch held in WM.

The critical manipulations were factorial:

- **WM content × search role.** The WM colour could be (i) target-matching (same colour as the upcoming search target), (ii) distractor-matching (same colour as the upcoming distractors), or (iii) unrelated.
- **Intertrial transition.** Target and distractor colours either *repeated* from the previous trial (PoP repeat) or *swapped* (the previous distractor colour became the current target colour, and vice versa) — the canonical Maljkovic-Nakayama PoP contrast.

Primary dependent measure was search RT on the search display; accuracy on both search and memory probe served as controls to confirm WM was actually maintained. The PoP magnitude was operationalised as the RT difference (swap − repeat).

Statistical analysis used repeated-measures ANOVAs across the WM-content × transition factorial, with planned contrasts on PoP magnitude across WM-content levels. The crucial test was the *interaction*: PoP magnitude × WM-content. A significant interaction with reduced PoP in the distractor-WM condition is the signature finding.

A secondary experiment varied the WM colour assignment from trial to trial so that the WM colour's role (target vs distractor vs unrelated) was itself the manipulated variable on a per-trial basis, ruling out block-level strategy as the source of the effect.

## 5. Results

The principal quantitative findings:

- **PoP replicated.** Across all WM conditions combined, swap trials were slower than repeat trials, with the canonical PoP magnitude of tens of milliseconds.
- **Target-WM facilitates search.** Overall RT was reduced when WM held a target-matching colour, replicating the standard guided-search-by-WM effect (Soto et al. 2005; Olivers 2009). PoP was preserved or slightly enhanced.
- **Distractor-WM disrupts priming.** When WM held a distractor-matching colour, the PoP magnitude was significantly attenuated; the RT advantage for repeat trials over swap trials shrank toward zero. The PoP × WM-content interaction was robust.
- **No disruption from unrelated WM content.** Holding an unrelated colour did not change PoP magnitude relative to baseline, ruling out generic WM-load explanations.
- **Memory accuracy preserved.** Probe-match performance was high across conditions, confirming that the WM content was actually held throughout the search.
- **The effect is on the priming signal, not on overall search.** Mean RT in the distractor-WM condition was slowed (consistent with WM-driven capture by distractors — the classical Soto-style finding), but the *intertrial* advantage from feature repetition was specifically blunted, not the search itself.
- **Asymmetry across roles.** Target-WM contributes additively to the template-style bias; distractor-WM acts subtractively against the priming-driven bias. The two memory systems thus interact in role-dependent ways rather than simply summing.

The numerical magnitudes reported are in the range typical for PoP studies (10–40 ms per repeat-vs-swap contrast under baseline conditions; PoP attenuation of more than half in the distractor-WM condition).

## 6. Critique / limitations

The paradigm uses colour as the priming dimension. Whether the same WM × priming interaction obtains for shape, orientation, location, or higher-order features is not directly tested. Subsequent work (e.g., Kristjánsson's later studies on feature-priming and the priming-of-distractor literature) suggests the effect generalises, but the paper itself constrains the conclusion to the colour-priming case.

The "memory system" interpretation rests on a behavioural dissociation rather than a neural one. The paper does not include electrophysiology or imaging that would directly localise the priming trace versus the WM template (cf. Carlisle et al. 2011's CDA work). The conclusion that priming and WM are *separate* memory systems is therefore inferred from functional dissociation, not from independent neural substrates — though convergent EEG/fMRI evidence from related work (Bahle et al. 2018; Reinhart & Woodman 2014) supports the architectural claim.

The design pits explicit WM content against implicit priming trace, but does not unambiguously distinguish "implicit short-term memory" from "longer-term selection history" (e.g., statistical learning). The PoP signal collapses across both. Subsequent reviews (Failing & Theeuwes 2018 — in the database) decompose selection history further into priming, reward history, and statistical learning; the present paper's conclusions apply most directly to short-window intertrial priming.

The single-target design does not test whether *multi-target* priming (e.g., when several target features could repeat) interacts with WM the same way. The capacity-of-template-guidance literature (van Moorselaar et al. 2014) suggests there are sharp limits on parallel template maintenance; the paper does not extend its conclusions into that regime.

The PoP × WM interaction is asymmetric, but the paper does not push hard on *why* explicit WM content can suppress priming specifically. Mechanistically, two stories are compatible with the data: (a) the WM-template signal and the priming signal both enter a winner-take-all competition for control of the attentional priority map, with the more recent / more explicit signal winning when they conflict; or (b) the WM template *re-labels* the colour in the priority map (a previously-rewarded distractor colour becomes a currently-required attentional anchor), erasing the priming-trace's contribution. The paper does not adjudicate between these.

The connection between the present findings and the more general selection-history literature (Awh, Belopolsky & Theeuwes 2012; Failing & Theeuwes 2018) is implicit rather than explicit. The paper precedes Failing & Theeuwes 2018 by a year and helps establish the empirical phenomenon that the Failing review subsequently formalises into the third-channel framework.

Finally, the paradigm requires the participant to use the WM colour for a probe at the end of the trial, ensuring active maintenance. Whether merely-cued-but-not-probed colours (the "accessory" state in Olivers et al. 2011) produce the same disruption is an open question this paper does not address.

## 7. Connection to our work

This paper is a load-bearing empirical anchor for two architectural commitments in the user's program:

**(a) Selection history as a third channel.** The dominant Posner-school account of attention has two channels — top-down (template) and bottom-up (salience). Awh, Belopolsky & Theeuwes 2012 and Failing & Theeuwes 2018 (in the database, [failing_theeuwes2018_selection_history](failing_theeuwes2018_selection_history.md)) argued that selection history is a third, dissociable channel. Carlisle & Kristjánsson 2018 is one of the cleanest behavioural demonstrations that this third channel has its *own* memory substrate, independent of the WM-based template, by showing that explicit WM content can override the priming trace only when their assignments conflict.

For the recurrent ViT and PRISM, this means the recurrent state cannot be a single undifferentiated memory that conflates "what I am told to look for" with "what was recently selected". A faithful architecture needs at least two channels of internal feedback to the attention computation: an explicit-template stream (cued, fast-updating, supports active rehearsal) and a selection-history stream (implicit, slow-decaying, accumulates across trials). The user's Feedback Transformer primitive (`the_user_architectural_program` §1) is well-suited to this: it admits an arbitrary number of recurrent feedback sources at the Q/K/V projection, each carrying its own modulation of the attention map. A two-stream instantiation — fast template + slow priming — is the minimal Carlisle-Kristjánsson-faithful model.

**(b) Joining the WM-attention unification thread.** The paper sits squarely in the conceptual lineage running through Desimone 1996 ([desimone1996_visual_memory_attention](desimone1996_visual_memory_attention.md)), Desimone-Duncan 1995, Awh et al. 2006 ([awh2006_attention_wm](awh2006_attention_wm.md)), Olivers et al. 2011 ([olivers2011_wm_states_attention](olivers2011_wm_states_attention.md)), Kiyonaga & Egner 2013 ([kiyonaga_egner2013_wm_internal_attention](kiyonaga_egner2013_wm_internal_attention.md)), and Panichello & Buschman 2021 ([panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md)). The unifying claim across this lineage is that WM and attention share mechanisms — WM contents bias selection, and selecting an item moves it into WM. Carlisle & Kristjánsson refines this by showing that the WM-attention coupling is itself *mediated* by a third memory system (priming), and that the three (template / priming / salience) coexist on a common priority map but are dissociable. This is precisely the multi-compartmental view that the user's program (`the_user_architectural_program` §3) commits to architecturally.

**Architectural implications for the Feedback Transformer.** The Carlisle-Kristjánsson asymmetry — target-WM facilitates, distractor-WM suppresses priming — places a specific constraint on how the template and priming streams should combine in the Feedback Transformer:
- They cannot be averaged or concatenated naively; their interaction is *role-dependent*, with the template stream sometimes adding to and sometimes subtracting from the priming-driven bias.
- A natural architectural instantiation is to let each stream contribute its own $c_q, c_k$ feedback to the attention computation, but to let the template stream's contribution carry a *sign* (positive for target-matching, negative for distractor-matching) that can override the always-positive priming trace.
- Concretely, in the user's notation: $\alpha_{ij} \propto \langle s_{q,i} \odot (c^{template}_{q,i} + c^{priming}_{q,i}), s_{k,j} \odot (c^{template}_{k,j} + c^{priming}_{k,j}) \rangle$ — where the template contribution can be negative for distractor-matching cues. This naturally reproduces the WM-priming interaction.

**PRISM's slow memory as the priming substrate.** The user's PRISM v2 slow-memory commitment (`PRISM_V2_PROPOSAL.md` §3.3) takes its strongest motivation from the Carlisle 2011 WM→LTM template-transfer result. Carlisle & Kristjánsson 2018 deepens this: slow memory should also carry the implicit selection-history trace that survives WM displacement and that biases selection in the absence of an active template. The slow memory in PRISM v2 is not merely a "consolidated template store" — it is the architectural locus of selection history more broadly, including intertrial priming. This recasts the slow/fast distinction from a *timescale* contrast (slow = old, fast = new) into a *system* contrast (slow = implicit/automatic, fast = explicit/controlled), more in line with the Carlisle-Kristjánsson dissociation.

**Connection to van Moorselaar et al. 2014.** [vanmoorselaar2014_template_competition](vanmoorselaar2014_template_competition.md) shows that only one template can actively guide attention at a time. Carlisle & Kristjánsson clarifies what happens when that single active template is *displaced* (or, more interestingly, *misassigned* — held while looking for a different feature): the priming stream takes up the slack, and conflicts arise. A model with a single-template fast memory plus a multi-feature priming slow memory naturally exhibits both signatures: a one-at-a-time active template, with a richer history-of-selection trace in the background.

**Connection to Panichello-Buschman.** [panichello_buschman2021_shared_mechanisms](panichello_buschman2021_shared_mechanisms.md) argues that the same neural code supports both perception-driven and memory-driven attentional selection. Carlisle & Kristjánsson 2018 is the behavioural counterpart: not only do perception and memory share a code, but they share a *priority map* whose contributions from different memory streams can conflict. A model with a single shared priority map fed by multiple memory streams (the user's Feedback Transformer architecture) is well-positioned to reproduce both literatures simultaneously.

**Empirical hook for our model.** The Carlisle-Kristjánsson paradigm is small enough to be embedded as a model-side benchmark for any recurrent attention architecture. The diagnostic signature is: (i) target-WM speedup, (ii) distractor-WM disruption of intertrial priming, (iii) no effect from unrelated WM content. A recurrent ViT or PRISM trained on colour-pop-out search with a concurrent WM probe should reproduce all three. Failure to reproduce (ii) specifically would be evidence that the architecture conflates template and priming streams. This is one of the most directly-portable cognitive-science benchmarks for the user's program.

**Competition-emergent predictive coding angle.** Under the user's competition-emergent-PC thesis (`the_user_architectural_program` §5), the template and priming streams correspond to two hubs competing for control of the central self-attention. Their conflict — in the distractor-WM-disrupts-priming case — is the behavioural signature of inter-hub competition. The empirical asymmetry (template can override priming, but priming persists when no conflict exists) reads naturally as the template hub having a higher gain on the attention competition under explicit-task conditions, while the priming hub dominates under implicit/automatic conditions. This maps onto a plausible developmental or training-curriculum gradient: priming-style implicit biases form first, template-style explicit biases come online when task demands and active maintenance recruit fast memory.

**Quantitative target.** The Carlisle-Kristjánsson PoP-attenuation magnitude (roughly halving the repeat-vs-swap RT advantage) is a quantitative benchmark for the strength of the template-priming interaction. A model whose template stream has too weak a gain will not reproduce the attenuation; one with too strong a gain will eliminate priming entirely, even in the no-conflict condition. The right calibration is a model in which the template can *modulate* but not *erase* the priming signal — paralleling the human asymmetric interaction.

## 8. Citations to follow

- `maljkovic_nakayama1994_priming_pop_out` — the foundational priming-of-pop-out paper; provides the baseline PoP signature on which the present study's interaction is measured. Not yet in seed.
- `soto2005_wm_capture` — behavioural demonstration that WM contents capture attention; the target-WM-facilitation half of the present study's design. Not yet in seed.
- `awh_belopolsky_theeuwes2012_top_down_bottom_up_obsolete` — the influential review that first formalised selection history as a third channel; the conceptual frame in which Carlisle & Kristjánsson sits. Not yet in seed.
- `kristjansson_campana2010_priming_review` — review of priming in visual search; methodological context for the present paradigm. Not yet in seed.
- `theeuwes2013_feature_based_priming` — feature-based priming and its theoretical implications. Not yet in seed.
- `olivers2011_wm_states_attention` — active vs accessory taxonomy; the conceptual framework that distinguishes template-driving vs incidentally-maintained WM contents. In seed, full depth.
- `awh2006_attention_wm` — broader attention-WM coupling review. In seed.
- `kiyonaga_egner2013_wm_internal_attention` — formalises the equivalence between WM and internal attention. In seed.
- `panichello_buschman2021_shared_mechanisms` — shared neural code for perception-driven and memory-driven attention. In seed.
- `failing_theeuwes2018_selection_history` — the third-channel review; published the same year. In seed, full depth.
- `vanmoorselaar2014_template_competition` — capacity limits on simultaneous template guidance. In seed.
- `carlisle2011_attentional_templates` — the CDA-based template paper from the same first author; methodological predecessor. In seed, full depth.
