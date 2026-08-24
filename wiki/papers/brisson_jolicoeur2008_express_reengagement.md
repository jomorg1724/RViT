---
id: brisson_jolicoeur2008_express_reengagement
title: "Express attentional re-engagement but delayed entry into consciousness following invalid spatial cues in visual search"
authors:
  - "Brisson, Benoit"
  - "Jolicoeur, Pierre"
year: 2008
venue: "PLoS ONE"
doi: "10.1371/journal.pone.0003967"
arxiv: ""
url: "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0003967"
tags:
  - visual-attention
  - posner-cuing
  - psychophysics
  - human-neuroimaging
  - reaction-time
concepts:
  - validity-effect
  - cueing-effect
  - chronometric-function
  - attentional-spotlight
  - gain-modulation
related:
  - posner1980_orienting
  - muller_findlay1987_sensitivity_criterion
  - nobre_vanede2018_anticipated_moments
  - egly1994_object_attention
  - thomsen2005_conflicting_cues_fmri
relevance_to:
  - recurrent_vit
  - prism_v1
seed_source:
  - vit_paper_ref_48
status: full
depth: full
last_updated: "2026-05-15"
---

# Express attentional re-engagement but delayed entry into consciousness following invalid spatial cues in visual search

## 1. Abstract

In predictive spatial-cueing studies, reaction times are shorter for targets appearing at cued locations (valid trials) than at uncued locations (invalid trials) — the canonical Posner validity effect. The authors recorded ERPs while subjects performed a visual-search variant of the predictive-cue paradigm in order to localise the processing stage at which the cost of an invalid cue is paid.

They tracked the standard early sensory components (P1, N1) and two later lateralised components: the N2pc, an index of attentional selection of a lateralised target, and the SPCN (sustained posterior contralateral negativity), an index of transfer and maintenance of the selected item in visual short-term memory. P1 amplitude was enhanced contralateral to the cued location, confirming that attention was deployed.

Critically, the N2pc *onset latency* was statistically indistinguishable between valid and invalid trials, indicating that attentional re-engagement at the true target location following an invalid cue is essentially express — too fast to leave a chronometric trace at the selection stage. In contrast, SPCN onset was delayed by ~45 ms on invalid trials, and the SPCN delay correlated with the RT validity effect across subjects, whereas the N2pc delay did not.

The authors conclude that the validity effect reflects a bottleneck *after* visuospatial selection — at the gate that admits the selected representation into visual short-term memory and conscious report — rather than at the selection stage itself.

## 2. Why this matters for us

The paper is a chronometric dissection of exactly the trial type the Recurrent ViT and PRISM v1 both stake their behavioural prediction on: the invalid cue. Posner 1980 establishes that invalid trials are slower; Brisson & Jolicoeur 2008 says *where in the processing chain that slowing lives*.

For our purposes the load-bearing claim is that spatial reorienting after an invalid cue is fast enough to look instantaneous at the N2pc — i.e., the attentional state can flip from cued to true-target location with no measurable cost — but the system pays a separable cost in the readout-into-memory stage. This is the empirical scaffold for distinguishing two different things our models could be doing on invalid trials: failing to redirect their internal "attention" map, versus redirecting it cheaply but paying for it downstream in the recurrent memory / decision readout. The dissociation is directly relevant to the Recurrent ViT's invalid-trial dynamics and to PRISM's competition over the priority map versus its memory transfer.

## 3. Key claims

1. P1 sensory-gain enhancement contralateral to the cue confirms that the predictive cue deployed spatial attention before target onset, ruling out an account in which subjects ignore the cue and pay the validity cost only retrospectively.
2. N2pc onset latency does *not* differ between valid and invalid trials (181 vs 187 ms; F<1), implying attentional re-engagement at the true target location is essentially express — no measurable chronometric cost at the selection stage.
3. N2pc amplitude is also unchanged across validity (−1.52 vs −1.60 µV; F<1), implying selection on invalid trials is not only as fast but as strong as selection on valid trials.
4. SPCN onset latency *is* delayed on invalid trials (~355 vs ~400 ms; F_adj(1,15)=32.89, p<.0001), implying the cost is paid at the transfer-to-VSTM / consciousness stage.
5. SPCN amplitude is also reduced on invalid trials (−1.40 vs −0.23 µV; F(1,15)=5.24, p<.04), consistent with reduced or noisier VSTM encoding on invalid trials in addition to the latency cost.
6. The SPCN delay correlates with the behavioural RT validity effect across subjects (r=.503, p<.047), while the N2pc delay does not (r=−.203, p>.45) — locating the validity effect causally at the VSTM-gating stage.
7. By implication, the Posner validity effect should not be modelled as a single late-stage delay nor as a single early-stage delay, but as a dissociation between an early, possibly automatic reorienting and a later, capacity-limited admission to working memory.

## 4. Methods

**Task.** Predictive spatial-cueing visual search. Each trial begins with central fixation and two lateral placeholder boxes 3.5° from fixation. After a 700–850 ms baseline, one of the placeholders briefly (100 ms) changes colour — the spatial cue. After an 800 ms cue–target SOA the target display appears: 1°×1° coloured squares with a small gap whose side defines the response. The placeholder colours are drawn from an equiluminant set (red, blue, green, yellow) and the colours used in the target display differ from those used in the cue display, ruling out simple feature-priming explanations.

**Cue-validity manipulation.** Of trials containing a target, 75% were valid (target at cued location) and 25% were invalid (target at the opposite location); a further 20% of all trials were no-target catch trials on which two distractors were presented and no response was required. The 75/25 ratio is the standard manipulation that motivates voluntary endogenous deployment of attention to the cued side. The 800 ms cue–target SOA places the trial well inside the regime where endogenous orienting has completed but exogenous capture has decayed.

**EEG recording.** 64 electrodes referenced to averaged mastoids, sampled at 256 Hz, low-pass filtered at 40 Hz; epochs ran from 100 ms pre-target to 600 ms post-target.

**ERP components.** Four components were analysed:

- Early lateralised sensory potentials: P1 contralateral enhancement and N1 ipsilateral enhancement, both indexed at lateral occipital electrodes and used to confirm that attention was deployed to the cue prior to target onset.
- N2pc: a 210–290 ms contralateral-vs-ipsilateral negativity at PO7/PO8, taken as the index of attentional selection of the lateralised target item from among distractors.
- SPCN (sustained posterior contralateral negativity): the continuation of the N2pc beyond ~350 ms at the same electrodes, taken as the index of transfer to and maintenance in visual short-term memory.

**Statistics.** For each component the authors estimated onset latency by a jackknife procedure (leave-one-out grand averages, with the F statistic adjusted by Ulrich & Miller's correction to account for the inflated power induced by the jackknife). They tested cue-validity effects on both amplitude (mean voltage in a fixed time window) and latency (jackknifed onset estimate) with repeated-measures ANOVA. Across-subject Pearson correlations linked component-latency effects to behavioural RT effects, testing whether subjects with larger neural-latency effects also showed larger behavioural costs.

**Subjects.** N=16 (mean age 22.9, 11 female) survived from an initial sample of 22; the remainder were excluded for excessive EEG artefacts or low task accuracy. Ages ranged 19–35 years.

**Trial counts.** Each subject contributed enough trials that, after artefact rejection and the 25%-invalid contingency, both N2pc and SPCN difference waves were stable at the single-subject level for the planned valid-vs-invalid contrasts. Exact per-condition trial counts are reported in the paper's methods table.

**Eye-movement control.** Trials with horizontal eye movements (detected via the horizontal EOG channel) were rejected to ensure that the lateralised ERP components reflect *covert* attention and not eye-movement artefact. This is standard for N2pc/SPCN designs and is what licences the interpretation of the contralateral negativity as an index of covert selection rather than overt orienting.

## 5. Results

**Behaviour.** RT was 685 ms valid vs 714 ms invalid, a 29 ms validity effect (F(1,15)=16.04, p<.002). Accuracy was at ceiling and did not differ (95.5% valid vs 94.9% invalid, p>.27). The behavioural validity effect therefore lives entirely in RT, not accuracy — the canonical pattern for endogenous Posner cueing at long SOA.

**Early sensory cueing.** P1 was reliably larger contralateral (0.91 µV) than ipsilateral (0.55 µV) to the cued side (F(1,15)=17.77, p<.001). N1 showed the reciprocal ipsilateral enhancement (−4.41 µV ipsilateral vs −4.02 µV contralateral to the cued/attended side; F(1,15)=9.80, p<.007). Both effects confirm covert spatial deployment of attention to the cue prior to target onset and rule out a "no-attention" account of the invalid-trial cost.

**N2pc (selection).** Amplitude was statistically identical across validity conditions (−1.52 µV valid vs −1.60 µV invalid; F<1). Onset latency differed by only 6 ms (181 ms valid vs 187 ms invalid) and did not reach significance after the jackknife correction (F_adj<1). Across subjects, the small N2pc-latency effect did *not* correlate with the RT validity effect (r=−.203, p>.45). On every measure that bears on the selection stage, the invalid cue is essentially free.

**SPCN (memory transfer / consciousness).** Amplitude was substantially larger on valid than invalid trials (−1.40 µV vs −0.23 µV; F(1,15)=5.24, p<.04). Onset latency was reliably delayed by ~45 ms on invalid trials (355 ms valid vs 400 ms invalid; F_adj(1,15)=32.89, p<.0001). Across subjects, the SPCN-latency effect *did* correlate with the RT validity effect (r=.503, p<.047). On every measure that bears on the memory-transfer stage, the invalid cue is expensive.

**The dissociation.** The same invalid-cue manipulation produces a 0–6 ms (null) cost at the N2pc-selection stage and a ~45 ms (highly reliable) cost at the SPCN-VSTM stage. Only the latter predicts individual differences in the behavioural RT cost. The 29 ms behavioural RT effect is therefore consistent with — and in fact considerably smaller than — the SPCN delay, suggesting the SPCN-stage delay propagates partially but not entirely into the response, perhaps because part of the SPCN delay is absorbed by parallel processing in motor preparation.

**Summary chronometry.** A useful way to read the numbers: by ~187 ms the brain has already selected the *correct* target item even on invalid trials, just as fast as on valid trials. By ~355 ms a valid trial's representation has been transferred into VSTM and the decision can proceed; by ~400 ms an invalid trial's representation has finally also been transferred. The 45 ms gap between these two transfer events is the chronometric home of the validity effect.

**Behavioural-to-neural concordance.** The behavioural 29 ms RT effect is smaller than the 45 ms SPCN-latency effect, which is itself fully reliable. The most natural interpretation is that the SPCN delay is the most upstream stage on which the invalid cue has an effect, and that motor preparation partially overlaps with VSTM encoding so that the SPCN delay does not propagate one-for-one into the response. The N2pc null is harder to reconcile with any account in which reorienting itself takes measurable time.

## 6. Critique / limitations

**Component-stage identification.** The selection-vs-VSTM dissociation depends on accepting the N2pc and SPCN as veridical, dissociable indices of the corresponding cognitive stages. The N2pc is well established as an index of lateralised attentional selection (Eimer 1996; Luck & Hillyard 1994), but the inference that "express N2pc onset" implies "zero-cost selection" assumes that any selection-stage cost would show up as a latency shift rather than an amplitude shift or a process not visible at the scalp. A small selection-stage cost paid as, e.g., reduced selection precision or a wider attentional aperture would not necessarily move N2pc onset and would be invisible here.

**Amplitude vs latency.** The amplitude data (identical N2pc amplitudes but a sharply attenuated SPCN on invalid trials) is more equivocal than the latency dissociation. An attenuated SPCN is plausibly consistent with reduced or noisier transfer of the target representation into VSTM, rather than with a pure delay; if the underlying interpretation is reduced fidelity of transfer, the "delayed entry into consciousness" framing is misleading. The latency dissociation, by contrast, is unambiguous: ~6 ms at N2pc, ~45 ms at SPCN.

**Endogenous regime.** The 75/25 design with a long 800 ms SOA is endogenous and well outside the exogenous-capture window. Whether the same dissociation holds for short-SOA peripheral cues — where exogenous capture dominates and reorienting may itself be exogenous and stimulus-bound — is an open question. The express-reengagement claim is therefore best read as a claim about *endogenous* reorienting at long SOA, not about reorienting in general.

**Statistical power.** Subject-level correlations between component-latency effects and RT effects (r=.503 across 16 subjects) are underpowered: the SPCN-RT correlation just clears p<.05 and the contrast with the null N2pc-RT correlation (r=−.203) is suggestive rather than decisive. A within-subject single-trial analysis — e.g., regressing trial-level SPCN onset on trial-level RT — would be a stronger test of the same dissociation, and is not present in this paper.

**"Consciousness" interpretation.** The framing "delayed entry into consciousness" relies on identifying the SPCN/CDA family with working-memory encoding and, through working memory, with conscious access. The identification is standard but not uncontroversial: SPCN amplitude tracks the number of items maintained in VSTM (Vogel & Machizawa 2004), but its identification with conscious access *per se* leans on a substantive theoretical claim about VSTM and consciousness that the paper itself does not separately establish. A weaker and more defensible reading is that the SPCN delay reflects a delay in *task-relevant working-memory encoding*; consciousness is a strong gloss on this.

**Catch-trial fraction.** With 20% no-target catch trials and 80% target trials of which only 20% are invalid, the absolute number of invalid trials per subject is modest, which is part of why the SPCN-RT correlation is the noisiest reliable effect in the paper.

**Visual search vs. simple detection.** The task embeds the Posner cue inside a two-item visual search rather than the simple one-target detection of the canonical Posner paradigm. The dissociation is therefore most directly a claim about *search-with-cueing* rather than about cueing in isolation. Whether the same selection-vs-VSTM dissociation would emerge in a simple detection task — where there is no rival item to select against — is not directly tested here.

**No-target catch trials are not separately analysed.** The 20% no-target trials function as a behavioural control against premature responding but are not used to estimate baseline component latencies. A more aggressive design would include a no-cue baseline, allowing decomposition into cost (invalid − neutral) and benefit (neutral − valid) at each component, in the spirit of Posner's original cost-benefit dissociation.

**Single SOA.** Only one cue–target SOA (800 ms) is tested. The express-reengagement claim could plausibly weaken or break at shorter SOAs where the cued attentional state may not yet be fully established; the long-SOA regime tested here is the one most favourable to the dissociation.

## 7. Connection to our work

The Recurrent ViT and PRISM both predict and measure invalid-trial behaviour; this paper tells us what that behaviour decomposes into in humans, and the decomposition is directly mappable onto our architectures.

**Recurrent ViT — invalid-trial dynamics and recovery.** In `2502.10955` (Figure 3C/F) the model recovers from an invalid cue across recurrent steps, and the validity-effect signature in our model is the drop in hit rate / extra recurrent steps required to reach correct response on invalid trials. The Brisson–Jolicoeur dissociation predicts a specific *internal* signature: the self-attention map (the analog of N2pc selection) should reorient to the true change location with little to no extra latency, while the hidden state $H^{(t)}$'s readout into a confident decision (the analog of SPCN-gated VSTM transfer) should pay the bulk of the cost.

Concretely, the prediction we should test is that the *first* recurrent step at which the model's attention map peaks on the true target location is roughly the same on valid and invalid trials, but the step at which the readout head crosses its decision threshold is reliably later on invalid trials. The right measurements are (i) the step-index of attention-map peak on the true-change patch, valid vs invalid, and (ii) the step-index at which the classification logit crosses a fixed margin, valid vs invalid. The B–J prediction is that (i) is invariant and (ii) is reliably delayed. If our model instead shows a sluggish (i) — the attention map itself is slow to redirect — that is a substantive divergence from the human chronometric pattern and tells us the model is paying its invalid-trial cost at the wrong stage.

**PRISM v1 — response to invalid cues.** In `Prism/docs/THESIS.md` §2.4 and §3.2 the model defines attention as prediction-error magnitude, and the memory $M_t$ is updated by a gated mechanism that consults that error. The Brisson–Jolicoeur result therefore separates two things our PRISM evaluation should not conflate: (a) the speed at which the prediction-error map relocates from the cued to the true-change location on invalid trials (the express-N2pc analog), and (b) the speed at which $M_t$ absorbs the relocated content into a decision-supporting representation (the SPCN-VSTM analog).

The `PROJECT_PLAN.md` P2.2 psychometric validity figure currently measures only end-to-end validity effects — a single number per validity condition. The temporal-reorienting question motivates an additional analysis that tracks both quantities through time on invalid trials: a time-resolved trace of (a) the peak location of the prediction-error map, and (b) the entropy / margin of the decision distribution conditioned on $M_t$. If PRISM reproduces the human pattern, (a) should equilibrate within one or two steps of cue–target SOA and (b) should lag by several steps — and the lag, across model seeds, should predict the seed-level RT validity effect just as the SPCN delay does across subjects in B–J.

**The temporal-attention reorienting question.** Brisson & Jolicoeur show that reorienting *in space* has a structure — fast at selection, slow at memory transfer. The open analog in our work, in conversation with the "anticipated moments" thread (Nobre & Van Ede 2018), is whether reorienting *in time*, when the model's temporal prior about *when* a change will occur is violated, shows the same fast-selection / slow-memory-transfer split, or whether time and space reorienting are computationally different. The pair of variables identified by this paper (early selection latency, late readout latency) is the natural axis along which to ask that question of our models: a model that maintains a *separate* temporal-prior memory compartment is predicted to exhibit a B–J-like dissociation when the temporal prior is violated; a model that conflates spatial and temporal priors into a single state is not.

**Multi-compartmental memory licence.** The paper also licenses a more general architectural point about the user's program (`threads/the_user_architectural_program.md` §3): a multi-compartmental memory in which one compartment hosts the priority map (the N2pc analog) and another hosts the VSTM gate (the SPCN analog) is exactly the kind of architecture in which the human dissociation is natural. Models that collapse those two compartments into a single recurrent state are predicted to fail at reproducing the dissociation — they will pay the invalid-cue cost either entirely early or entirely late, depending on which timescale the single state runs on. This is a positive empirical test for the multi-compartmental commitment, complementary to the cortex-mapping arguments already in the thread.

**Where each architecture pays.** A useful table for our own reference:

- In the published Recurrent ViT, the analog of the N2pc-selection variable is the self-attention map at recurrent step $t$ (which patches dominate the softmax); the analog of the SPCN variable is the recurrent hidden state $H^{(t)}$ at the same step (which feeds the readout).
- In PRISM v1, the analog of the N2pc-selection variable is the prediction-error map (which patches show high reconstruction error); the analog of the SPCN variable is the slow memory $M_t$ updated by gated integration of that error.
- In PRISM v2's slow/fast decomposition (`PRISM_V2_PROPOSAL.md` §3.3), the N2pc analog naturally maps onto the fast state, the SPCN analog onto the slow state — making PRISM v2 the architecture that most cleanly admits the Brisson–Jolicoeur dissociation as a falsifiable prediction.

**A specific experiment.** Concretely, the Brisson–Jolicoeur design can be ported wholesale into our environments: take any of the change-detection benchmarks, set cue validity to 75%/25%, and measure (for each model under test) two latencies — the step at which the model's "selection" variable peaks on the change patch, and the step at which the model's "readout" variable produces a confident decision. Compute their validity-effect difference.

The B–J prediction is selection-latency-effect ≈ 0 and readout-latency-effect > 0, with the second predicting the model's overall RT-equivalent. A model that fails this dissociation in either direction is paying its invalid-cue cost at the wrong stage and is therefore behaviourally Posner-correct for the wrong internal reason. This is the kind of structured behavioural-and-internal test that distinguishes our program from a black-box benchmark report.

**Caveat on the analogy.** The mapping of model variables onto N2pc / SPCN is an analogy, not an identity claim. Brisson & Jolicoeur's components are lateralised difference waves at posterior electrodes; our model variables are activation patterns over patch tokens. The mapping is justified by the *functional* roles the components and variables play — selection vs. memory transfer — not by any commitment that the model's variables produce the same scalp signature. The point of the comparison is to test whether the *same functional dissociation* shows up in our systems.

**Relation to the Posner foundational entry.** Where `posner1980_orienting` supplies the canonical validity effect and the spotlight metaphor, Brisson & Jolicoeur 2008 supplies the chronometric internals: a single behavioural validity effect decomposes into a near-zero cost at the selection stage and a sizeable cost at the VSTM-gate stage. Together they motivate the architectural reading that any model attempting to reproduce Posner-style behaviour must contain at least two functionally distinct stages capable of accumulating cost separately. A single-stage attention mechanism is consistent with the Posner data but inconsistent with the Brisson–Jolicoeur data — exactly the kind of constraint a paper-level database is for.

**Open questions our work could answer.** Brisson & Jolicoeur leave several questions unanswered that our computational models are well placed to address. First, is the express-reengagement claim regime-specific to long-SOA endogenous cueing, or general? Our environments admit arbitrary SOAs cheaply and so can sweep this parameter. Second, does the dissociation invert under load — e.g., when VSTM is concurrently occupied? PRISM's $M_t$ admits direct load manipulation by varying its dimension. Third, is the SPCN-stage cost a pure delay, an amplitude reduction, or both? Our model variables admit direct dual measurement in a way the scalp signal does not. Each of these is an experiment we can run on the modelling side that is genuinely difficult on the human side.

## 8. Citations to follow

- `eimer1996_n2pc` — Eimer 1996, the foundational N2pc paper establishing the component as an index of lateralised attentional selection. Required to ground claim 2.
- `luck_hillyard1994_n2pc_search` — Luck & Hillyard 1994, the parallel N2pc-in-visual-search foundation. Pairs with Eimer to anchor the selection-stage identification.
- `jolicoeur2008_spcn_vstm` — Jolicoeur and colleagues on the SPCN/CDA as an index of visual short-term memory load. Required to ground claim 3.
- `vogel_machizawa2004_cda_capacity` — Vogel & Machizawa 2004, the canonical demonstration that CDA amplitude tracks VSTM set size. Anchors the SPCN-as-VSTM identification.
- `wolfe1994_guided_search` — Wolfe's guided-search account of visual search, the task framework Brisson & Jolicoeur embed the Posner cue inside. Useful for placing the result in the search-vs-cueing literature.
- `thomsen2005_conflicting_cues_fmri` — Thomsen et al. fMRI of invalid-cue reorienting (TPJ/IPS), the neural-substrate complement to this paper's scalp-ERP dissociation.
- `corbetta_shulman2002_control_networks` — Corbetta & Shulman's dorsal/ventral attention-networks framework, in which invalid cues are the canonical driver of ventral-network reorienting.
- `ulrich_miller2001_jackknife` — Ulrich & Miller's jackknife correction for ANOVA on latency estimates, the statistical procedure used here for N2pc/SPCN onsets. Methodological citation.
- `hillyard1998_p1_attention` — Hillyard et al. on P1 amplitude as the index of early sensory gain under spatial attention. Anchors the P1 contralateral-enhancement claim.
