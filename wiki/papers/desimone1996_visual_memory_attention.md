---
id: desimone1996_visual_memory_attention
title: "Neural mechanisms for visual working memory and their role in attention"
authors:
  - "Desimone, Robert"
year: 1996
venue: "Proceedings of the National Academy of Sciences"
doi: "10.1073/pnas.93.24.13494"
arxiv: ""
url: "https://doi.org/10.1073/pnas.93.24.13494"
tags:
  - primate-neurophysiology
  - visual-attention
  - working-memory
  - theoretical-essay
concepts:
  - biased-competition
  - attentional-template
  - top-down-feedback
  - working-memory-persistent-activity
related:
  - moran_desimone1985_selective_attention
  - desimone_duncan1995_biased_competition
  - awh2006_attention_wm
  - kiyonaga_egner2013_wm_internal_attention
  - olivers2011_wm_states_attention
  - panichello_buschman2021_shared_mechanisms
  - funahashi1989_mnemonic_dlpfc
  - miller_cohen2001_pfc_function
  - reynolds_chelazzi2004_attentional_modulation
  - constantinidis2018_persistent_activity
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - vit_paper_ref_100
status: full
depth: full
last_updated: "2026-05-16"
---

# Neural mechanisms for visual working memory and their role in attention

## 1. Abstract

Desimone reviews three classes of neuronal effect observed in macaque visual cortex during memory-demanding tasks and uses them to extend the biased-competition framework (Desimone & Duncan 1995) by an explicit working-memory mechanism. The three effects are: (i) *repetition suppression* — a reduction in the response of inferior temporal (IT) cortex neurons to a repeated visual stimulus, observed both at short (within-trial) and long (cross-session) timescales, intrinsic to visual cortex and not dependent on prefrontal feedback; (ii) *enhancement* — an increased response in IT neurons to objects whose behavioral relevance has been learned, dependent on intact feedback from prefrontal cortex; and (iii) *delay activity* — sustained, stimulus-selective firing of IT and prefrontal neurons during the delay period of a working-memory task, again requiring intact prefrontal-temporal interactions. Desimone argues that the enhancement and delay-activity effects are not separate from attention but instead constitute the neural mechanism by which the *contents of working memory bias visual processing toward stimuli that match the held template*. Because biased competition holds that multiple stimuli within a receptive field compete for representation, and because memory-driven enhancement and delay activity tilt that competition, memory will often *determine* which stimulus wins the competition and therefore which stimulus is attended. The paper is the founding explicit identification of working-memory templates with the source of the top-down attentional bias signal in extrastriate visual cortex.

## 2. Why this matters for us

Desimone 1996 is the canonical paper that *fuses* working memory and selective attention into a single mechanism — the same fusion that Awh, Vogel & Oh (2006), Olivers et al. (2011), Kiyonaga & Egner (2013), and Panichello & Buschman (2021) later formalize at the cognitive and neural-population level, and the same fusion that the user's architectural program builds into its basic primitives. Three concrete hooks for our work. First, the *enhancement* effect — held WM content multiplicatively boosts IT responses to matching stimuli — is the biological substrate that the Recurrent ViT's hidden-state-to-attention pathway, PRISM v1's $M_t$-driven FiLM modulation, and the Feedback Transformer's $s_q \odot c_q$ Q/K-projection structure all implement: a memory state modulating a sensory processing stage. Second, the *delay activity* in IT and PFC is the empirical analog of every persistent recurrent state in our architectures ($H^{(t-1)}$ in the Recurrent ViT; $M_{t-1}$ in PRISM; the GridCell RNN's $C_i^{(t)}$). Third, the explicit identification of the attentional bias signal with the contents of working memory licenses our architectural commitment to treat *one* substrate — recurrent memory feedback into attention — as doing *both* jobs: maintaining behaviorally relevant content across time *and* biasing the current attention map. This is the conceptual root of the user's "attention and WM are the same mechanism" position.

## 3. Key claims

1. **Three principal mnemonic effects on visual cortex neurons.** Repetition suppression, enhancement, and delay activity together describe how learning and memory modulate visual stimulus representations in adult monkey cortex.
2. **Repetition suppression is intrinsic to visual cortex.** Repeated presentation of a stimulus reduces IT-cell responses to it, both within trials (short-term) and across sessions (long-term). This effect persists after prefrontal disconnection — it is *internal* to visual cortex.
3. **Enhancement requires prefrontal feedback.** When a behaviorally relevant target is presented, IT responses to it are *enhanced* relative to identical physical stimulation in a non-target context. This effect *requires intact projections from prefrontal cortex*: PFC lesions abolish it.
4. **Delay activity requires prefrontal feedback.** Sustained, stimulus-selective firing during a working-memory delay is observed in both IT and prefrontal cortex; the IT delay activity depends on prefrontal feedback (PFC lesions disrupt it), but PFC delay activity does not depend on IT (the source of the persistent representation is prefrontal).
5. **The enhancement and delay-activity effects are mechanisms of attention.** Because biased competition (Desimone & Duncan 1995) holds that multiple stimuli within an IT/V4 receptive field compete for representation, a memory-driven gain boost on the held template's representation gives that representation an advantage in the competition.
6. **Memory determines competition winners.** "Memory will often determine the winner of these competitions and, thus, will determine which stimulus is attended." Working memory is not separate from attention; it is the *source* of the attentional bias signal.
7. **Attention is a single mechanism with multiple sources.** Bottom-up salience, behavioral relevance learned over training, and the currently held working-memory template all operate through the *same* competition substrate in extrastriate cortex; they differ only in the source of the bias.
8. **PFC as the source of top-down bias.** Inferior prefrontal cortex (and dorsolateral PFC, following Funahashi 1989) hosts the persistent neuronal representations that supply the descending bias signal to IT during both memory maintenance and target-directed attention.
9. **Repetition suppression and enhancement work on the same population from opposite ends.** The same IT cells whose responses are *suppressed* by familiar irrelevant stimuli are *enhanced* when the stimulus becomes a behaviorally relevant target — both are competition-shaping mechanisms acting on the same substrate.

## 4. Methods

The paper is a review/synthesis, not a primary experiment, but its conclusions rest on a specific corpus of single-unit electrophysiology done by Desimone's group and collaborators in the early 1990s.

**Repetition suppression evidence.** IT recordings during repeated presentations of the same image (Miller, Li & Desimone 1991, 1993; Li, Miller & Desimone 1993). On each trial, a sample image is shown, followed by a sequence of test images; the monkey responds when the sample reappears. IT neurons show progressively reduced responses to repeated non-target test stimuli — a "passive" adaptation effect that does not depend on the stimulus being task-relevant. The same population shows long-term suppression for stimuli the animal has seen many times in past training.

**Enhancement evidence.** Chelazzi, Miller, Duncan & Desimone (1993, 1998) recorded from IT during a visual search task in which the monkey was cued with a target image at the start of each trial and then had to find that target among distractors in an array. After the cue and a delay, the IT response to the target stimulus (when later presented in the search array) was enhanced relative to the same stimulus presented as a distractor on a different trial — the *physical* stimulus identical, the *behavioral relevance* different. The enhancement is selective: only IT cells whose preferred stimulus matched the cued target showed the boost.

**Delay activity evidence.** Fuster & Jervey (1981) and Miyashita & Chang (1988) recorded delay-period activity in IT during delayed-match-to-sample; Funahashi, Bruce & Goldman-Rakic (1989) recorded delay-period activity in dlPFC during oculomotor delayed-response. Desimone draws on his group's IT recordings during delayed-match-to-sample (Miller, Li & Desimone 1993; Miller & Desimone 1994) showing IT cells that maintain a stimulus-selective elevated firing rate across an empty delay between sample and probe.

**Causal evidence for PFC dependence.** Inferior prefrontal cortex lesions (Bauer & Fuster 1976; Fuster, Bauer & Jervey 1985) abolish IT delay activity and target enhancement; the *visual* responses of IT cells remain intact, but the *memory-driven* modulation collapses. This is the load-bearing evidence that the descending bias signal originates in PFC and arrives at IT via cortico-cortical feedback projections.

**Framework.** Desimone embeds these results into the biased-competition framework of Desimone & Duncan (1995). The within-RF competition substrate of Moran & Desimone (1985) is preserved; the new contribution is to identify the *source* of the attentional bias as PFC-resident working-memory representations.

## 5. Results

The principal quantitative observations across the cited literature:

- **Repetition suppression magnitude.** IT responses to repeated stimuli are reduced by ~25–50% relative to novel stimuli, with the largest reductions on the first 2–3 repetitions and a slower asymptotic decline thereafter (Miller et al. 1991, 1993).
- **Stimulus-selective suppression.** The suppression is *stimulus-specific*: a cell whose response to image A is suppressed by repetition continues to respond normally to a novel image B. The effect is not generalized fatigue.
- **Long-term suppression.** Stimuli the animal has been exposed to extensively across training sessions show ~30–40% reduced IT responses relative to novel stimuli, persisting for days to weeks.
- **PFC-independence of suppression.** PFC lesions do not abolish repetition suppression in IT, indicating that the effect is intrinsic to visual cortex.
- **Enhancement magnitude (Chelazzi et al. 1993).** When the target of a visual search matches an IT cell's preferred stimulus, the cell's response to that stimulus in the search array is elevated relative to the same stimulus as distractor by a factor of ~1.5–2× during the search-execution phase.
- **Selectivity of enhancement.** Only IT cells whose preferred stimulus matches the cued target show the enhancement; non-matching cells show no enhancement or mild suppression — consistent with biased competition.
- **Delay-period firing rates.** IT delay activity in delayed-match-to-sample tasks is ~2–4× baseline for the preferred stimulus and near-baseline for the non-preferred stimulus, sustained across delays of several seconds.
- **PFC-dependence of delay activity.** Following inferior PFC lesion, IT delay activity collapses while IT visual responses remain intact (Fuster et al. 1985). The same lesion impairs the animal's behavioral performance on delayed-match-to-sample.
- **PFC delay activity is more robust.** dlPFC delay neurons (Funahashi et al. 1989) maintain selective firing across delays of 3–6 s without IT input, suggesting PFC is the *source* of the persistent representation that drives IT delay activity via feedback.
- **Within-RF competition with WM bias.** Chelazzi et al.'s search arrays put target and distractor stimuli within a single IT RF; the WM-driven enhancement of the target response coincides with *suppression* of the distractor response — the classic Moran & Desimone 1985 competition phenomenon, but now with the bias supplied by the held WM template.

## 6. Critique / limitations

The paper is a synthesis and inherits the empirical limitations of its source studies. The single-unit recordings were performed in small numbers of macaques and small numbers of cells per area; population-scale replication came later (Chelazzi et al. 1998 with hundreds of IT cells; Reynolds, Chelazzi & Desimone 1999 for V2/V4). The conclusions about PFC dependence rely on lesion data from the 1976–1985 Fuster work, where the lesions were large and likely included multiple PFC subregions; finer dissection of which prefrontal area supplies which signal had to await later studies (Miller & Cohen 2001; Tomita et al. 1999 cooling experiments).

The paper treats *one* working-memory representation as the source of bias, but does not address the multi-item case — what happens when several items are held in WM and which one acts as the attentional template. This question is the explicit focus of Olivers et al. (2011), who propose that only the *active* item functions as a template (one-item-at-a-time), while "accessory" items are maintained without biasing attention. Desimone 1996's framing implicitly assumes a single-item template and does not distinguish this from the multi-item case.

The mechanism by which PFC-resident persistent activity is converted to a gain modulation in IT is not specified by the paper. Desimone proposes feedback projections from PFC to IT, but the cellular mechanism — multiplicative gain modulation, additive bias, modulation of normalization pool — is left underspecified. Reynolds & Heeger (2009) later formalize this as the *attention field* multiplying the stimulus-driven normalization, providing one concrete proposal; Spratling (2008) provides another in predictive-coding terms.

The repetition-suppression vs. enhancement dichotomy is presented as cleanly distinct: suppression is PFC-independent, enhancement is PFC-dependent. Subsequent work has complicated this — Tomita et al. (1999) showed that *long-term* IT representations also depend on PFC during retrieval, and the distinction between "intrinsic" and "PFC-dependent" effects is gradient rather than dichotomous.

Finally, the paper assumes a particular causal ordering: WM template held in PFC → descending bias to IT → competition in IT → which-stimulus-is-attended outcome. The alternative ordering — that attention and WM are *simultaneous expressions* of a single competition process spanning both areas, with no causal precedence — is consistent with the data and is the position later taken by Awh, Vogel & Oh (2006) and Panichello & Buschman (2021). Desimone 1996 does not adjudicate between these.

## 7. Connection to our work

Desimone 1996 is the *founding explicit identification* of working memory with the top-down attentional bias signal and is the conceptual ancestor of the entire WM-as-attentional-template tradition (Awh 2006; Olivers 2011; Kiyonaga & Egner 2013; Panichello & Buschman 2021). For the user's program, this paper anchors five concrete commitments.

**Attention and WM as one mechanism — the user's central position.** The user's architectural program (`the_user_architectural_program` §1, §3) treats recurrent memory feedback into self-attention as a *single* substrate that does the work of both maintaining behaviorally relevant content and biasing the current attention map. Desimone 1996 is the founding biological warrant for this commitment: IT enhancement and delay activity are not two separate phenomena (memory + attention) but two expressions of the same process — a PFC-resident persistent representation that biases the within-RF competition in IT. This is the same architectural pattern as the Recurrent ViT's $H^{(t-1)}$ entering the attention map computation (§3 of 2502.10955), PRISM v1's $M_t$ FiLM modulation (`THESIS.md` §2.4), and the Feedback Transformer's $s_q \odot c_q$ Q/K projection (`feedback_transformer` concept). One memory state, two functions.

**IT memory-tuned neurons as biological substrate for PRISM's WM-driven attention map.** PRISM v1's central architectural move (`THESIS.md` §2.6) is to compute the attention map *from the working-memory state* rather than from sensory input directly — prediction-error gating where the error is computed against the WM-held template. Desimone 1996's enhancement effect is exactly this: IT cells whose preferred stimulus matches the held template show boosted responses to matching sensory input. This is the cellular signature of "WM determines the attention map." The user's architectural choice to drive attention from $M_t$ rather than from $X_t$ has its biological warrant in this paper's central result.

**Persistent activity and the recurrent state primitive.** The delay-activity literature Desimone reviews (Fuster, Miyashita, Funahashi, Miller & Desimone) is the founding empirical basis for the *recurrent-state* primitive in computational models — the assumption that representations can be maintained across time by sustained neural firing in the absence of the driving stimulus. Every recurrent state in the user's program ($H^{(t-1)}$, $M_{t-1}$, $C_i^{(t)}$, the GridCell RNN's internal grid) is computationally what IT and PFC delay activity is biologically. The `working-memory-persistent-activity` concept tag is shared across this paper, `funahashi1989_mnemonic_dlpfc`, `constantinidis2018_persistent_activity`, and the user's architectural-program thread.

**Hierarchy-specific top-down feedback supports multi-compartmental design.** The PFC-IT directional feedback that Desimone establishes — PFC delay activity is robust without IT input, but IT delay activity collapses without PFC input — is direct support for the user's *diminishing-feedback-into-deeper-layers* commitment (`the_user_architectural_program` §3). The user's three-layer memory stack assigns deeper layers (analogous to PFC) more autonomy and shallower layers (V4/IT) more feedback dependence — exactly the empirical asymmetry Desimone documents at the PFC ↔ IT interface.

**Conceptual lineage to Awh 2006, Olivers 2011, Kiyonaga & Egner 2013, Panichello & Buschman 2021.** Desimone 1996 is the proximate cause of each of these later integrative papers. Awh et al. (2006) take Desimone's identification of WM and attention as the starting point and review the cognitive-psychological evidence; Olivers et al. (2011) refine it by distinguishing active templates from accessory items; Kiyonaga & Egner (2013) recast WM as "internal attention" — selection among internal representations — using the same shared-resource logic; Panichello & Buschman (2021) provide the population-coding-level demonstration that the same prefrontal mechanisms support both selection in WM and selection of perception. Each of these papers is downstream of Desimone 1996, and the user's program reads them as a coherent argument for the architectural commitment that *one* recurrent-memory substrate supplies the attentional bias.

**Connection to moran_desimone1985_selective_attention.** Moran & Desimone (1985) is the empirical substrate (within-RF competition between two visual stimuli) onto which Desimone 1996 grafts the working-memory mechanism. M&D 1985 established *that* attention gates within-RF competition; Desimone 1996 identifies *who supplies the gating signal* — the held WM template, with PFC as its anatomical home. Reading the two papers together gives the full biased-competition-with-WM-source story that the user's program operationalizes.

**Connection to desimone_duncan1995_biased_competition.** D&D 1995 lays out the biased-competition framework as a general theory of selective attention; Desimone 1996 is the explicit extension of that framework by a working-memory mechanism. Where D&D 1995 leaves "what supplies the bias" as a generic top-down signal, Desimone 1996 identifies it concretely as PFC-resident WM content and reviews the lesion and recording evidence. For the user's program, both papers must be read as a pair: D&D 1995 supplies the within-RF competition substrate, Desimone 1996 supplies the source of the bias.

**Connection to funahashi1989_mnemonic_dlpfc.** Funahashi et al. (1989) is the founding demonstration of stimulus-selective delay activity in primate dlPFC during the oculomotor delayed-response task. Desimone 1996 cites this work as the prefrontal half of the IT-PFC delay-activity story and uses it to argue that the *source* of the persistent representation lies in PFC. In the user's architectural program, this is the empirical warrant for treating the deepest layer of the multi-compartmental memory ($C_3$ in the 3-layer reference design) as the analog of PFC — the layer that holds representations across the longest timescales and supplies feedback to shallower layers (`the_user_architectural_program` §3).

**Connection to miller_cohen2001_pfc_function.** Miller & Cohen (2001) generalize Desimone 1996's PFC-as-source-of-bias claim into the broader "PFC as biased-competition controller of task-relevant cognition" account. They extend the biased-competition logic from visual cortex to the whole cortical hierarchy: PFC's persistent representations are the *task set* that biases competition not just in IT but across all cortical regions involved in performing the current task. For the user's program, this licenses scaling the PFC-IT feedback motif into the *coalition-competition* thesis (`the_user_architectural_program` §5) — multiple PFC-like control hubs, each maintaining its own persistent representation, all competing to bias the shared attention substrate.

**Implications for the recurrent ViT's per-pass attention dynamics.** The user's Food-101 classifier observation (`the_user_architectural_program` §6) — that attention maps "focus, defocus, and reactivate over recurrent steps" — reads naturally through Desimone 1996's lens. Each recurrent pass updates the WM-analog $H^{(t-1)}$, which then re-biases the attention competition on the next pass; the iterative refinement of the attention map is exactly the iterative tightening of the WM-driven bias on the within-RF competition. The qualitative attention-dynamics observation thus has a concrete biological referent in Desimone's enhancement-plus-delay-activity mechanism.

**Implications for change detection.** Change detection (the central task of 2502.10955 and PRISM) is inherently a WM-vs-current-input comparison: the previous frame's content is held in WM and the current frame must be matched against it. Desimone 1996's enhancement and delay-activity mechanisms are exactly the substrate for this comparison — IT cells whose preferred stimulus matches the held template are tonically elevated, so when the current frame contains that stimulus, the IT response reflects both the bottom-up sensory signal *and* the memory-driven bias. A change (held template ≠ current stimulus) corresponds to a mismatch between the WM-biased expectation and the current IT response — exactly the prediction-error signal PRISM v1 uses to drive its attention map.

## 8. Citations to follow

- `chelazzi_etal1993_competing_visual_stimuli` — Chelazzi, Miller, Duncan & Desimone 1993, the IT visual-search recordings that anchor the *enhancement* effect in this review. Not yet in seed; load-bearing for the WM-as-bias mechanism.
- `miller_li_desimone1991_short_term_memory` — Miller, Li & Desimone 1991, the founding IT repetition-suppression paper. Not yet in seed.
- `miller_desimone1994_parallel_neuronal_mechanisms` — Miller & Desimone 1994, IT delay-activity and repetition-suppression in delayed-match-to-sample. Not yet in seed.
- `fuster_jervey1981_inferotemporal_neurons` — Fuster & Jervey 1981, founding IT delay-activity recording. Not yet in seed.
- `miyashita_chang1988_neuronal_correlate` — Miyashita & Chang 1988, IT delay-period stimulus-selective firing. Not yet in seed.
- `funahashi1989_mnemonic_dlpfc` — Funahashi, Bruce & Goldman-Rakic 1989, dlPFC delay-activity in oculomotor delayed-response. Already in seed.
- `fuster_bauer_jervey1985_functional_interactions` — Fuster, Bauer & Jervey 1985, the PFC-lesion-abolishes-IT-delay-activity result. Not yet in seed; load-bearing for the PFC-as-source-of-bias claim.
- `tomita1999_topdown_signal_from_prefrontal` — Tomita, Ohbayashi, Nakahara, Hasegawa & Miyashita 1999, the cooling experiment that causally demonstrates PFC → IT feedback for retrieval. Not yet in seed.
- `desimone_duncan1995_biased_competition` — the 1995 review that supplies the biased-competition framework this paper extends. Already in seed, full depth.
- `moran_desimone1985_selective_attention` — the founding within-RF competition demonstration. Already in seed, full depth.
- `awh2006_attention_wm` — the cognitive-psychology extension of Desimone 1996's WM-attention identification. Already in seed, full depth.
- `olivers2011_wm_states_attention` — the active-vs-accessory-template refinement. Already in seed, full depth.
- `kiyonaga_egner2013_wm_internal_attention` — WM as internal attention; the shared-resource formalization. Already in seed, full depth.
- `panichello_buschman2021_shared_mechanisms` — the population-coding demonstration of shared PFC mechanisms. Already in seed.
- `miller_cohen2001_pfc_function` — generalizes PFC-as-bias-source to all task-relevant cognition. Already in seed.
- `reynolds_chelazzi2004_attentional_modulation` — review that integrates Desimone 1996's mechanisms with the normalization-model account. Already in seed.
