---
id: carlisle2011_attentional_templates
title: "Attentional templates in visual working memory"
authors:
  - "Carlisle, Nancy B."
  - "Arita, Jason T."
  - "Pardo, David"
  - "Woodman, Geoffrey F."
year: 2011
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.1818-11.2011"
arxiv: ""
url: "https://www.jneurosci.org/content/31/25/9315"
tags:
  - working-memory
  - visual-attention
  - human-neuroimaging
concepts:
  - attentional-template
  - working-memory-persistent-activity
  - cueing-effect
related:
  - olivers2011_wm_states_attention
  - vanmoorselaar2014_template_competition
  - awh2006_attention_wm
  - bahle2018_wm_attention_architecture
  - desimone_duncan1995_biased_competition
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_18
status: full
depth: full
last_updated: "2026-05-14"
---

# Attentional templates in visual working memory

## 1. Abstract

Models of attention propose that visual search is guided by an *attentional template* held in working memory (WM) that biases perceptual processing in favor of template-matching inputs. However, the empirical claim that templates are actively maintained in WM (rather than retrieved from long-term memory) has remained difficult to test directly, because behavioral measures of "template engagement" cannot distinguish active maintenance from passive retrieval.

Carlisle, Arita, Pardo & Woodman use the **contralateral delay activity (CDA)** — an EEG marker of the active maintenance of items in visual WM — to show that during visual search, observers maintain a representation of the search target in WM that has the electrophysiological signature of an *attentional template*. The CDA scales with the number of target features held, parallel to its scaling with WM load in non-search paradigms.

Critically, when the same target is searched for repeatedly across trials, the CDA *decreases* over repetitions while search efficiency *increases*, indicating that the template is gradually *transferred from WM to long-term memory (LTM)*. The CDA reduction tracks behavioral measures of search automatization on a trial-by-trial basis. When the target identity changes, the CDA recovers to its initial amplitude, demonstrating that the WM→LTM handoff is template-specific.

The result establishes the CDA as a neural index of attentional templates and demonstrates a learning-driven WM→LTM handoff for templates that nevertheless continue to guide attention. This bridges two literatures: the WM-attention interaction tradition (Awh, Vogel, Luck; Soto et al.) and the long-term memory guidance-of-search tradition (Chun & Jiang's contextual cueing; Hutchinson & Turk-Browne).

The paper is one of the most-cited demonstrations of the WM-substrate of attentional control. Its core methodological contribution — using CDA as an index of the active template — has been widely adopted (Reinhart & Woodman 2014; van Moorselaar et al. 2014; Hakim et al. 2019).

## 2. Why this matters for us

Carlisle et al. 2011 is the canonical empirical demonstration that the "attentional template" — the top-down bias that steers visual selection — is a maintained representation in visual WM, with a measurable neural signature (CDA). This is the *operational evidence* for the architectural commitment, made implicitly by the recurrent ViT and explicitly by PRISM, that an attended location/feature is held in a recurrent state that biases the next-step attention map.

Beyond the basic WM-template demonstration, the paper identifies a *training-dependent* shift from WM to LTM: with repetition, templates can drive attention without requiring active WM maintenance. This has direct implications for how PRISM's slow memory might pre-load templates that started life as WM contents — the slow memory is a model-side analog of the "template store" that the brain accumulates with practice. The paper is therefore both a foundation for the basic template construct and a constraint on how a multi-timescale memory architecture should distribute template storage across its components.

For the recurrent ViT specifically, the paper licenses an interpretation of the recurrent state as a model-side CDA: the state encodes the current attentional template, with its contribution to the next-step attention map analogous to the CDA's underlying neural activity biasing the next-saccade priority map. This interpretation makes specific, testable predictions about how the recurrent state should change over time and across repeated trial structures.

## 3. Key claims

1. **Templates are in WM during search.** The CDA — an EEG marker known to track items actively maintained in visual WM — is present during the retention interval before each search display, with amplitude scaling with the number of target features held.
2. **CDA reflects the template specifically.** The CDA is observed not just for any memorized item, but specifically for the item that will guide the upcoming search — i.e., the template, not an arbitrary WM load. This positions the CDA as a *functional* neural marker rather than a generic memory marker.
3. **Templates transfer to LTM with repetition.** When the same target is used across many trials, the CDA *decreases* across repetitions, indicating reduced reliance on active WM maintenance. The transfer is gradual rather than all-or-none.
4. **Behavioral search efficiency increases as CDA decreases.** Search RT speeds up across repetitions in parallel with CDA reduction, consistent with the template's effectiveness being preserved as it migrates from WM to LTM.
5. **Novel templates re-engage the CDA.** When the target identity changes, the CDA returns to its initial high amplitude, demonstrating that the WM→LTM handoff is template-specific, not a general adaptation effect or fatigue artifact.
6. **The CDA is a neural index of the active template.** The paper establishes the CDA as a usable signature for tracking the maintenance state of attentional templates — a methodological contribution exploited by subsequent literature (Olivers et al. 2011; van Moorselaar et al. 2014; Reinhart & Woodman 2014).
7. **Templates can be maintained even when offloaded.** The behavioral guidance of attention by the target continues after the CDA has decreased, implying that templates in LTM can still exert top-down bias on selection — i.e., the template-guidance function is preserved across the WM→LTM transfer.
8. **Search automatization is a memory-system handoff.** Practice-induced speedup in visual search reflects not just stimulus-response learning but a redistribution of which memory system carries the template, with implications for theories of cognitive automatization more broadly.

## 4. Methods

Healthy adult participants performed a visual search task with concurrent high-density EEG recording. Each trial sequence: (i) a *cue display* indicating the search target (a single shape, lateralized to one hemifield); (ii) a *retention interval* of ~1 second during which CDA was measured at posterior-lateral electrodes contralateral vs ipsilateral to the cued hemifield; (iii) a *search display* containing the target plus distractors, with participants reporting a target-specific feature (typically the orientation of a line segment within the target shape) as quickly and accurately as possible.

The CDA itself is computed as the difference in event-related potential (ERP) at posterior-lateral electrodes (typically PO7/PO8 and surrounding sites) between contralateral and ipsilateral hemispheres relative to the cued (memorized) hemifield, in a time window (~300–1000 ms post-cue) corresponding to the WM retention period. Prior work (Vogel & Machizawa 2004) established the CDA as scaling with the number of items maintained in visual WM, plateauing at the individual's WM capacity (~3–4 items).

Two experimental manipulations isolate the WM→LTM template-transfer effect:

- **Memory-load manipulation.** The number of target features held in WM varied across conditions (one vs two features per target). CDA amplitude was expected to scale with load, replicating Vogel & Machizawa for the template-specific case.
- **Repetition manipulation.** The same target identity was repeated across many consecutive trials (typically up to 7 repetitions), then switched to a new identity. CDA was measured as a function of repetition number, with the prediction that CDA would decrease across repetitions if the template were being transferred to a non-WM store.

Key dependent measures: CDA amplitude during the retention interval; search RT and accuracy on the search display; and the trial-by-trial correlation between single-trial CDA amplitude and single-trial RT, which provides the within-subject evidence for the template-engagement interpretation.

The critical design feature is the *factorial combination* of memory load with target repetition. This permits dissociating effects of "template complexity" (more features → larger CDA, slower search) from effects of "template familiarity" (more repetitions → smaller CDA, faster search). The full design space looks like a 2 (load) × 7 (repetition) within-subjects matrix, with CDA and RT measured in each cell.

A secondary control verifies that the CDA decrease is not driven by trivial sensory adaptation: target identities are randomly drawn from a large stimulus set across blocks, with target features (color, shape) varied independently. The CDA decrease occurs only across repetitions of the *same* target — repetitions of similar-but-different targets do not yield a CDA decrease, ruling out sensory habituation as a confound.

Statistical analysis used repeated-measures ANOVA across the load × repetition factorial, with planned contrasts for the linear trend of CDA across repetitions and the load × repetition interaction. Single-trial CDA-RT correlations were computed within subjects and aggregated using Fisher's z-transform to assess group-level effects.

## 5. Results

The principal quantitative findings:

- **CDA scales with target features.** Two-feature templates produced significantly larger CDA amplitudes than one-feature templates during initial repetitions, consistent with active WM maintenance scaling with load. The effect replicates the canonical Vogel & Machizawa (2004) result in the template-specific regime.
- **CDA decreases across repetitions.** Over the first ~5–7 repetitions of the same target, CDA amplitude declined toward baseline. After sufficient repetitions, the CDA was effectively absent — the template was no longer drawing on active WM maintenance resources.
- **Search RT decreases in parallel.** Search RT decreased monotonically across repetitions and reached an asymptote concurrent with the CDA reaching baseline, indicating that template-guided search became increasingly efficient as the template was offloaded.
- **CDA-RT correlation across trials.** Trial-by-trial CDA amplitude correlated with single-trial RT: trials with larger CDA showed *slower* RTs (template not yet automatized, still requiring effortful WM maintenance) and trials with smaller CDA showed *faster* RTs (template offloaded to LTM and acting efficiently). This within-subject correlation is the key evidence that the CDA and RT changes share a common cause.
- **Reset on target change.** When the target identity changed, the CDA returned to its initial amplitude on the first trial with the new target and then decayed again with repetition — confirming template specificity and ruling out generic adaptation, fatigue, or expectation effects as confounds.
- **Search accuracy preserved.** Accuracy remained high throughout, confirming that the WM→LTM transfer did not degrade the template's functional role; templates in LTM continue to guide selection as effectively as templates in WM.
- **Memory-load × repetition interaction.** The CDA reduction across repetitions was observed for both one-feature and two-feature templates, suggesting that the WM→LTM transfer is a general phenomenon not limited to simple templates. However, the higher-load condition retained a residual CDA longer than the low-load condition, consistent with two-feature templates requiring more repetitions before fully transferring.
- **No CDA decrease for novel targets.** When target identity varied trial-to-trial (no repetition), no CDA decrease was observed across the corresponding trial-position range, confirming that the effect requires target identity to repeat.
- **Behavioral magnitude.** The RT speedup across repetitions was on the order of ~100 ms over the first 5–7 repetitions, consistent with prior behavioral studies of search practice effects.
- **CDA reduction is graded, not stepwise.** The CDA decline across repetitions is approximately monotonic and exponential-decay-like rather than abrupt, supporting a gradual-transfer interpretation rather than a discrete switch between memory systems.
- **Symmetric effects across hemispheres.** The CDA effect was symmetric across left- and right-hemifield cues, ruling out lateralized attention or hemispheric specialization as a confound.
- **Individual differences.** Subjects with higher CDA-amplitude differences across the load manipulation also showed larger CDA-RT correlations across repetitions, suggesting that template engagement is more measurable in subjects with cleaner CDA signals.

## 6. Critique / limitations

The CDA is a contralateral-vs-ipsilateral difference signal; the inference that it indexes a "template" specifically (as opposed to any laterally-cued WM content) rests on the additional design feature that the WM item is in fact the search target. The paper does not fully dissociate "template" from "currently-attended laterally-cued item" — these are intentionally confounded by design. A control condition with a memorized-but-task-irrelevant item would be needed to fully isolate the template role; the Olivers et al. 2011 active/accessory framework subsequently provides that dissociation.

The "transfer to LTM" inference is indirect. The decrease in CDA could in principle reflect (a) compression of the WM representation rather than transfer to a separate LTM store, (b) habituation of the CDA-generating neural population, or (c) shift from a sustained-activity code to a synaptic-trace code within the same population. Subsequent work (Reinhart et al. 2012; Woodman et al. 2013) has supported the LTM-transfer reading but has not eliminated all alternatives — the distinction between "WM-with-synaptic-traces" and "LTM" is partly definitional.

The paradigm uses a single repeated target. Whether templates for *multiple* simultaneous targets can be transferred independently to LTM, or whether multi-template scenarios prevent transfer altogether, is an open question; van Moorselaar et al. 2014 addresses related issues for multi-template competition and finds capacity limits on simultaneous template guidance.

The CDA is an aggregate over many neurons across posterior electrodes; the underlying neural substrate (which cortical areas, which populations) cannot be resolved by the paper's EEG methodology. Subsequent fMRI work (e.g., Soto et al. 2007; Bettencourt & Xu 2016) supplies the spatial localization but at the cost of temporal resolution, so the two measures only partially triangulate the underlying substrate.

The behavioral measure of "template engagement" is RT speedup, which can also reflect motor learning, decision-criterion shifts, response-mapping practice, or perceptual priming. The paper's argument is that the CDA-RT *correlation* across trials rules out pure motor explanations, but the dissociation is not airtight — a CDA-independent contribution to RT speedup could co-vary with the CDA decrease without being causally linked to the template.

Finally, the paradigm constrains targets to be lateralized; whether central or distributed templates show the same WM→LTM transfer profile is untested. This is a methodological constraint imposed by the CDA's reliance on hemispheric lateralization, not a substantive theoretical commitment, but it means the paper's conclusions formally generalize only to lateralizable templates.

A separate concern is that the paradigm uses brief retention intervals (~1 sec) and trials are densely spaced. The conclusion that templates can move from "WM" to "LTM" within ~5–7 repetitions presses against conventional definitions of LTM (which typically require minutes-to-hours of consolidation). The CDA-fading effect may better be characterized as a shift from WM to *intermediate-term* memory or to a *procedural* template store — the boundary between WM and LTM in this paradigm is not crisp.

Relatedly, the paper does not test retention across longer delays. Whether the offloaded template persists across a session break, across a day, or across longer intervals is unaddressed; Reinhart & Woodman 2014 partially fills this gap by showing TMS-induced disruption of the offloaded template at longer delays.

## 7. Connection to our work

This paper provides the *empirical anchor* for several architectural commitments in the user's program:

**The recurrent ViT cue mechanism as a CDA analog.** The recurrent ViT's cue input establishes which item should drive subsequent attention — i.e., it instantiates an attentional template in the model's recurrent state. Carlisle et al. supplies the neural signature (CDA) for this construct in primate cortex. A direct analogy is: the recurrent-state contribution to the next-step attention map plays the architectural role that the CDA's underlying neural maintenance plays in cortex. Probing the recurrent state for template-like representations (e.g., via linear decoding of the cued target's identity or location from the recurrent state across timesteps) is the model-side analog of measuring CDA. The expected signature: decoding accuracy should be high for the cued target during the maintenance window between cue and search/response, and should scale with the number of features the template carries — paralleling the load-dependence of the CDA.

**PRISM's slow memory as a template-LTM store.** PRISM v2's slow memory (`PRISM_V2_PROPOSAL.md` §3.3) is positioned as a long-timescale state that maintains task-relevant context. Carlisle et al.'s WM→LTM transfer finding suggests a concrete computational role for slow memory: it can absorb templates that were initially held in the fast/WM state, freeing fast memory for new task contents while preserving the template's guidance over attention. The empirical observation that *behavior remains template-guided after the CDA fades* implies that the slow-memory representation can still exert top-down bias — i.e., slow memory should project into the attention pathway even when it is no longer being actively rehearsed. Architecturally this means the slow-memory state should feed into the Feedback Transformer's Q/K/V projection alongside the fast/WM state, with the relative weighting of the two contributions shifting toward slow memory as the template becomes practiced.

**Active vs accessory distinction (per Olivers et al. 2011).** Carlisle et al. is the empirical demonstration of an *active* template in WM (large CDA, drives attention). Olivers et al. ([olivers2011_wm_states_attention](olivers2011_wm_states_attention.md)) places this in the broader active/accessory framework. The recurrent ViT's recurrent state architecturally embodies the active template — a single cued location dominating the next-step attention map. The Olivers framework suggests we should also model an "accessory" state of maintained-but-not-attention-guiding items; the recurrent ViT does not currently make this distinction. The Carlisle paradigm offers a clean test: a model trained on this kind of repeated-target search should show a model-side correlate of the WM→LTM shift, while a model that treats all maintained items identically should not.

**Multi-hub system and template handoff.** In the user's multi-hub architecture, the WM→LTM template transfer corresponds to a hand-off between a fast hub (rapid binding of a new template) and a slow hub (long-term storage of well-practiced templates). The fact that the *transfer is gradual and not all-or-none* (the CDA decays over ~5–7 repetitions) suggests the slow hub should accumulate evidence across repetitions rather than overwriting on each trial — a constraint on the update rule for slow memory. Specifically, the slow hub's update should integrate over many recent observations of the same template, with an effective time constant of several trials. PRISM v2's slow-fast recurrence (with its explicit slow-timescale memory) directly implements this constraint.

**Empirical hook for our model.** A direct test of the analogy: train the recurrent ViT on repeated presentations of the same cued target and measure the magnitude of the recurrent-state contribution to attention across repetitions. If the model exhibits a Carlisle-like decrease in recurrent-state reliance (with attention performance preserved), this is evidence that something LTM-like has emerged in the model's weights. PRISM v1 with its inner-loop variational inference (`THESIS.md` §2.8) is well-positioned to exhibit this pattern: the inner loop may converge faster across repetitions as the prior over $M_t$ tightens. Quantitatively, the recurrent-state contribution can be ablated (replaced by zero) across repetitions; if attention performance is preserved at late repetitions but degraded at early repetitions, this would mirror the Carlisle CDA-RT dissociation.

**Biased-competition framing.** The Carlisle template is best understood as a Desimone-Duncan biased-competition signal: a top-down bias originating in PFC (or PFC-like memory areas) that boosts the competitive weight of template-matching units in visual cortex. The recurrent ViT's recurrent-state contribution to the attention softmax is the architectural homolog of this biasing signal: it is added to the bottom-up Q/K projections before the softmax, exactly as biased competition predicts top-down templates should multiplicatively modulate the gain of visual units. Carlisle et al. operationalizes "what the template is made of" (a CDA-generating sustained activity pattern); Desimone & Duncan supplies the computational role (biasing competition); our architecture supplies the implementation (recurrent-state contribution to attention).

**Competition-emergent predictive coding angle.** In the user's competition-emergent-PC thesis (`thread §5`), the template can be reframed as a *prediction about which item the system's "search hub" expects to be relevant* — a hub-specific prediction that biases the central self-attention. The CDA's WM→LTM transfer corresponds to the search-hub's prediction being absorbed into the hub's slow-timescale weights, freeing fast-state capacity for new predictions. The fact that template guidance survives the CDA fade is consistent with the prediction having been incorporated into the hub's connectivity structure — a more permanent form of "competing for attention" than active maintenance.

**Implication for training curricula.** A practical consequence: if PRISM's slow memory is to play the role of the LTM template store, training curricula should include repeated exposures to the same task contexts so that slow memory has the opportunity to accumulate template information across episodes. Single-shot, randomly-resampled training (the default in many RL/curriculum settings) may suppress the very dynamic Carlisle et al. identifies. The Carlisle paradigm itself, replayed in a model-training context, would be a useful benchmark: train on N-shot repeats of the same cued target, then test whether the model exhibits Carlisle-like template offloading.

**Quantitative target.** The Carlisle CDA half-life of ~3 repetitions provides a quantitative reference: a slow memory whose template-accumulation time constant is on this order would best match the empirical phenomenology. If PRISM's slow memory has a much longer time constant (e.g., hundreds of episodes), the architecture would still capture the *direction* of the WM→LTM shift but would not match the empirical *rate*. This is one of the relatively few quantitative empirical constraints available for tuning slow-memory hyperparameters.

**Connection to the iterative variational encoder-decoder.** The user's iterative VAE construction (`Private & Shared` notes; thread §4) involves $n_{FR}$ forward-reasoning passes over the same image. Carlisle et al.'s finding that template engagement evolves across repetitions of the same target is the cognitive-science analog: each forward-reasoning pass plays the role of a repetition, and the encoder's guide $H_t$ becomes progressively less reliant on active WM-style state while still steering the decoder. The exponential weighting $\gamma_i = e^{i - n_{BR}}$ favoring later passes is consistent with the Carlisle pattern: later passes (later repetitions) carry the more refined, automatized template.

**Specific architectural prediction.** A multi-compartmental memory with both fast and slow states should show, when trained on Carlisle-style repeated-target search, a *crossover* in the relative magnitudes of the fast-state and slow-state contributions to the attention map across repetitions. Early repetitions: fast state dominates (high "model CDA"). Late repetitions: slow state dominates (low "model CDA" but preserved attention-guidance). This crossover is the architectural signature the user's program should reproduce.

**Caveat on the analogy.** Translating Carlisle et al. to a deep-learning context requires that "trial repetitions" map onto something meaningful in the model's training/inference regime. For PRISM trained on iid sampled change-detection episodes, the Carlisle dynamic does not arise — each episode has a novel template. The Carlisle phenomenology becomes relevant when (i) the model is exposed to repeated-task structure during training, or (ii) the within-episode dynamics of template engagement (across recurrent passes within a single trial) play the role of "repetitions." Both interpretations are consistent with the user's program; they correspond to slow-timescale vs fast-timescale instantiations of the same WM→LTM shift.

The recurrent ViT paper cites Carlisle et al. 2011 in its bibliography (ref [18]) as evidence for the attentional-template construct.

## 8. Citations to follow

- `vogel_machizawa2004_cda_capacity` — original CDA paper; foundational methodology for the entire CDA literature, establishing the load-scaling and capacity-plateau properties exploited by Carlisle. Not yet in seed.
- `awh2006_attention_wm` — broader attention-WM framework reviewing the bi-directional coupling between WM and attention. In seed.
- `desimone_duncan1995_biased_competition` — biased-competition origin of the template construct; the computational role that Carlisle's CDA operationalizes. In seed.
- `soto_heinke_humphreys2005_memory_attention_capture` — behavioral demonstration that WM contents capture attention; the behavioral counterpart to Carlisle's electrophysiological finding. Not yet in seed.
- `olivers2011_wm_states_attention` — active vs accessory framework that subsumes Carlisle's findings into a more general taxonomy of WM states. In seed, full depth.
- `vanmoorselaar2014_template_competition` — multi-template competition; tests the capacity-of-1 claim implicit in Carlisle's single-target paradigm. In seed.
- `woodman_arita_luck2009_template_search` — prior work from the same lab on templates in search; methodological predecessor to the present paper. Not yet in seed.
- `reinhart_woodman2014_template_ltm` — explicit follow-up on the WM→LTM transfer mechanism, with causal manipulation (TMS) over PFC. Not yet in seed.
- `bahle2018_wm_attention_architecture` — architectural model of WM-attention interaction that incorporates the Carlisle WM→LTM transfer. In seed.
- `chun_jiang1998_contextual_cueing` — long-term memory guidance of visual search; a closely related literature that Carlisle's WM→LTM result bridges to. Not yet in seed.
- `bettencourt_xu2016_template_substrate` — fMRI localization of template representations; the spatial-localization counterpart to Carlisle's temporally-resolved CDA. Not yet in seed.
