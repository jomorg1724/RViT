---
id: roitman_shadlen2002_lip_rt
title: "Response of neurons in the lateral intraparietal area during a combined visual-discrimination reaction-time task"
authors:
  - "Roitman, Jamie D."
  - "Shadlen, Michael N."
year: 2002
venue: "Journal of Neuroscience"
doi: "10.1523/JNEUROSCI.22-21-09475.2002"
arxiv: ""
url: "https://www.jneurosci.org/content/22/21/9475"
tags:
  - primate-neurophysiology
  - parietal-cortex
  - decision-making
  - reaction-time
concepts:
  - drift-diffusion-model
  - signal-detection-theory
  - priority-map
  - chronometric-function
  - psychometric-function
related:
  - ratcliff1978_drift_diffusion
  - gold_shadlen2007_decision_making
  - bisley_goldberg2010_parietal_priority
  - hanks_summerfield2017_perceptual_decisions
  - sridharan2017_sc_sensitivity_bias
  - hawkins1990_attention_detectability
  - luo_maunsell2018_criterion_sensitivity
relevance_to:
  - recurrent_vit
  - prism_v1
  - prism_v2
seed_source:
  - thesis_md
status: full
depth: full
last_updated: "2026-05-15"
---

# Response of neurons in the lateral intraparietal area during a combined visual-discrimination reaction-time task

## 1. Abstract

Roitman & Shadlen (2002) record single-unit activity from area LIP in two rhesus macaques performing a *reaction-time* (RT) version of the random-dot motion direction-discrimination task originally established by Newsome, Britten and colleagues. On each trial the monkey fixates centrally while a random-dot kinetogram of variable motion *coherence* (0%, 3.2%, 6.4%, 12.8%, 25.6%, 51.2%) is shown; one of two saccade targets falls inside the recorded neuron's response field. The monkey is free to indicate its perceived direction by a saccade to one of the two targets as soon as it is ready, yielding a joint measurement of choice probability and reaction time. The principal finding is that LIP neurons whose response field contains the chosen target exhibit *ramp-like* increases in firing rate during motion viewing, with the *slope* of the ramp scaling with motion coherence — steeper for stronger, easier motion. Activity converges to a *common, stereotyped firing rate* (~50–70 spikes/s) immediately preceding the saccade, regardless of coherence, consistent with the hypothesis that LIP integrates a noisy motion-evidence signal until a fixed threshold is crossed, at which point a saccade is committed. On error trials the same convergence is observed for the *chosen* (incorrect) target. The full pattern — coherence-dependent build-up, threshold-independent commitment, faster RT and higher accuracy with stronger motion — quantitatively matches the predictions of the *drift-diffusion model* (Ratcliff 1978; see [ratcliff1978_drift_diffusion](ratcliff1978_drift_diffusion.md)) applied to bounded accumulation of perceptual evidence. The paper is the canonical demonstration that an *abstract cognitive variable* — the accumulated evidence for one of two choices — has a discoverable *neural correlate* in dorsal-stream cortex.

## 2. Why this matters for us

This is the foundational neurophysiology paper that grounds the entire decision-as-accumulation framework in actual primate cortex. For our program it does two indispensable jobs. First, it supplies the *neural existence proof* that drift-diffusion (Ratcliff 1978) is more than a phenomenological curve-fit: there are cells whose firing-rate trajectories *are* the diffusion variable, with slope set by evidence quality and a fixed crossing threshold setting the response. Second, it identifies *where* that accumulation lives — LIP, the parietal area we already cite via [bisley_goldberg2010_parietal_priority](bisley_goldberg2010_parietal_priority.md) as the canonical *priority map*. Combined, these two functions — priority/salience map *and* perceptual evidence accumulator — make LIP the most natural biological analog of the recurrent ViT's per-token attention values: a population of spatially-organised units whose graded activations both encode "where to deploy resources" and "how much evidence has accumulated to commit to a response there." The recurrent ViT's $n_{passes}$ inner iterations are then the architectural analog of LIP's within-trial integration window.

## 3. Key claims

1. **LIP firing rates ramp during motion viewing in a coherence-dependent manner.** When the chosen saccade target is in the response field, firing rate increases monotonically from motion onset, with steeper ramps for higher coherence.
2. **A common firing-rate threshold marks decision commitment.** Across coherences, in the ~80–100 ms preceding the saccade, firing rates converge to approximately the same stereotyped value (~50–70 spikes/s), independent of how long it took to get there.
3. **Latency to the ramp onset is ~190–220 ms after motion onset**, consistent with a fixed sensory-encoding delay before evidence integration begins.
4. **Activity on error trials looks like activity on correct trials for the chosen direction.** When the monkey saccades to $T_{in}$ (the response-field target) despite the motion favouring $T_{out}$, the firing-rate trajectory and pre-saccadic level match the correct-$T_{in}$ trajectory, not the correct-$T_{out}$ trajectory — i.e., LIP encodes the *chosen* response, not the *correct* one.
5. **The opposite-choice population shows complementary dynamics.** When the saccade is to $T_{out}$, the recorded $T_{in}$-preferring cell's firing rate ramps *downward* with coherence-dependent slope, consistent with two competing accumulators with anti-correlated drift.
6. **The build-up slope and commitment threshold jointly predict both choice probability and RT.** Slower (low-coherence) integration produces longer RTs and more errors; faster (high-coherence) integration produces shorter RTs and fewer errors — quantitatively matching DDM predictions with shared parameters across the coherence range.
7. **LIP is therefore the candidate neural substrate of Ratcliff's diffusion variable** for two-alternative perceptual decisions in the visuomotor domain.

## 4. Methods

**Subjects and task.** Two adult rhesus macaques, head-fixed, performed a two-alternative motion-direction discrimination. After fixation, a $5°$-diameter random-dot kinetogram appeared at the centre of gaze; on a fraction of dots specified by the trial's *coherence* level, a coherent left-or-right motion was imposed, with the remaining dots replotted at random. Coherence was drawn from $\{0\%, 3.2\%, 6.4\%, 12.8\%, 25.6\%, 51.2\%\}$ with direction (left/right) randomised across trials. Two saccade targets, $T_{in}$ (inside the recorded neuron's response field) and $T_{out}$ (in the diametrically opposite location), were illuminated throughout. The monkey was rewarded for a saccade to the target congruent with the net motion direction. Crucially, the monkey was *free to respond at any time after motion onset*: the trial structure was reaction-time, not fixed-duration, so each trial yielded both a choice and an RT.

**Neural recording.** Single-unit extracellular activity was recorded from area LIP using tungsten microelectrodes. Cells were selected for inclusion based on (i) a clear visual or memory-saccade response field and (ii) persistent or peri-saccadic activity for saccades to $T_{in}$ in a memory-saccade pre-test. A total of roughly 50–60 cells across the two monkeys contributed to the principal analyses.

**Behavioural model.** A drift-diffusion model with drift rate scaling linearly with motion coherence ($v = k \cdot c$), fixed boundary separation $a$, and non-decision time $T_{er}$ was fit to the joint choice-and-RT data (cf. Ratcliff 1978, [ratcliff1978_drift_diffusion](ratcliff1978_drift_diffusion.md)). The same model was then used to predict the *expected* neural ramp slopes as a function of coherence.

**Neural analysis.** Firing rates were computed in sliding windows aligned to motion onset (to reveal build-up) and to saccade onset (to reveal commitment threshold). Build-up rates were estimated by linear regression of firing rate on time over the post-latency epoch (~200–400 ms after motion onset, before the earliest saccades). Error trials were analysed separately, sorted by the monkey's *choice* rather than by the correct direction.

## 5. Results

**Behaviour.** Accuracy was a monotonically increasing function of coherence (psychometric function), ranging from chance at 0% to >95% correct at 51.2%. Mean RT decreased with coherence (chronometric function), from ~1.4 s at 0% coherence down to ~0.5 s at 51.2%. The DDM with $v = k c$, fixed $a$, and one $T_{er}$ fit both psychometric and chronometric functions with shared parameters — a hallmark DDM signature.

**Ramp slopes scale with coherence.** Build-up rate (spikes/s$^2$) for cells preferring the chosen target $T_{in}$ was a monotonically increasing function of coherence: shallow ramps at low coherence, steep ramps at high coherence. The slope ratio across the coherence range was approximately a factor of 2–3.

**Threshold convergence.** When firing rates were aligned to saccade onset, the firing rates in the ~80 ms immediately preceding the saccade converged to a *common, coherence-independent* level of approximately 50–70 spikes/s. This is the signature predicted by a bounded-accumulator model: the time to threshold varies with drift, but the threshold itself does not.

**Error trial signature.** On error trials, the firing-rate trajectory for the recorded $T_{in}$-preferring cell looked like the *correct* $T_{in}$-trial trajectory — i.e., it ramped up to threshold and the monkey saccaded to $T_{in}$, even though the actual motion was in the $T_{out}$ direction. This dissociates the neural correlate from the stimulus and ties it to the *decision*.

**Anti-ramping for the opposite choice.** When the monkey chose $T_{out}$, the $T_{in}$-preferring cell's firing rate *decreased* below baseline at a coherence-dependent rate. This is consistent with two competing accumulators with opposite-sign drift, or equivalently with a single accumulator and a complementary readout.

**Quantitative DDM match.** The estimated build-up rates and the inferred threshold, plugged into a DDM with neural-scale parameters, reproduced the observed psychometric and chronometric functions — establishing that the *cognitive* and *neural* accumulators have matching dynamics, not merely qualitatively similar shapes.

## 6. Critique / limitations

**Correlation, not causation.** The paper establishes a tight *correlation* between LIP firing and the decision variable but does not show that perturbing LIP changes the decision. Subsequent work — most directly Hanks, Ditterich & Shadlen (2006) microstimulation; Katz, Yates, Pillow & Huk (2016) optogenetic inactivation; and the multi-area perturbation literature reviewed in [hanks_summerfield2017_perceptual_decisions](hanks_summerfield2017_perceptual_decisions.md) — has produced more nuanced causal evidence. Katz et al. notably reported that pharmacological LIP inactivation in macaque has *modest* effects on motion discrimination, suggesting LIP's accumulator may be one of several parallel circuits rather than the unique decision substrate.

**Two-alternative only.** The task is strictly 2AFC with two saccade targets. The multi-alternative extension — relevant for the user's program because the recurrent ViT operates over many candidate spatial locations — requires the modelling vocabulary of [sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md). Whether LIP cells implement multi-target accumulation by population dynamics over many simultaneously-active priority-map sites, or by something more like winner-take-all between paired accumulators, remains an active question.

**Scalar readout, high-dimensional reality.** The DDM-style scalar accumulation account is a *projection* of richer population dynamics. Mante et al. (2013) showed that PFC during context-dependent decisions occupies high-dimensional state space with task-relevant dimensions selected by gating. By analogy, LIP's apparent scalar ramp is likely a low-dimensional projection of population-level dynamics involving many co-active cells.

**Priority-map confound.** Bisley & Goldberg (2010) ([bisley_goldberg2010_parietal_priority](bisley_goldberg2010_parietal_priority.md)) argue that LIP is best understood as a *priority map* — a spatial representation of behavioural priority that integrates bottom-up salience, top-down goals, and learned reward. Under this view, what Roitman & Shadlen call "evidence accumulation" is one specific computation that the priority map happens to support in this particular task, not a unique signature of LIP. The two framings are not contradictory but their reconciliation requires the priority-map machinery to *include* an integration time-constant tuned by task demands.

**LIP vs. other accumulator candidates.** Similar coherence-dependent ramps have been reported in FEF (Kim & Shadlen 1999), dorsal LPFC (Kim & Shadlen 1999), the caudate (Ding & Gold 2010), and the superior colliculus (Horwitz & Newsome 1999; Crapse, Lau & Basso 2018) — i.e., the accumulator signature is *distributed*. The single-region focus of Roitman & Shadlen 2002 is a clean experimental simplification, not a claim of localisation.

**Static decision boundary.** The threshold appears coherence-independent in the data, but more recent collapsing-bound and urgency-gating analyses (Cisek et al. 2009; Drugowitsch et al. 2012; Hawkins et al. 2015) argue that under different reward / time-pressure regimes the effective bound *does* collapse. The 2002 finding is consistent with a stationary bound *within the regime tested*; the wider parameter space remains an open question.

## 7. Connection to our work

Roitman & Shadlen 2002 is the load-bearing reference connecting our program's two distinct treatments of "graded resource allocation over locations": (i) the *attention / priority* reading — every per-token attention weight in the recurrent ViT is the architectural analog of an LIP firing rate at the corresponding spatial location; and (ii) the *evidence accumulation / actor* reading — the recurrent ViT's outputs across $n_{passes}$ recurrent iterations are the architectural analog of LIP's within-trial ramp, with the final commit step playing the role of threshold crossing. The paper *unifies* these two readings empirically: in LIP, they are the same population.

**LIP firing rates as the natural analog of recurrent ViT attention values.** The recurrent ViT (2502.10955) emits a per-token attention weight at every recurrent pass. Roitman & Shadlen's coherence-dependent ramps — steeper for stronger evidence, converging to a common pre-saccadic level — are exactly the dynamics we would *expect* the recurrent ViT's attention values to show, *if* the architecture is behaving as a biological accumulator. This is a falsifiable prediction: visualising the recurrent ViT's attention-map evolution over passes for high-contrast vs low-contrast change events should produce LIP-style ramp-and-threshold dynamics. The Food-101 visualisations qualitatively described in the [the_user_architectural_program](../threads/the_user_architectural_program.md) thread ("attention maps focus, defocus, and reactivate over recurrent passes") are consistent with this prediction but have not been quantified in DDM/LIP terms.

**The recurrent ViT actor head as LIP-to-SC readout.** In the canonical primate circuit, LIP's accumulator output is read out by the superior colliculus and brainstem saccade generators, which threshold and translate the parietal signal into an eye movement. In the recurrent ViT, an *actor head* maps from token-level attended representations to a discrete output (change/no-change, saccade location). The architectural parallel is direct: LIP-style accumulation feeds an actor-style threshold readout, exactly the structure Ratcliff 1978 formalised mathematically and Roitman-Shadlen 2002 demonstrated neurally.

**LIP is sensitivity / accumulation; SC is bias.** The decision-framework cluster in the database makes a critical distinction between *sensitivity* (drift rate $v$ in DDM, $d'$ in SDT) and *bias* (criterion in SDT, starting point $z$ in DDM). [sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md) and [luo_maunsell2018_criterion_sensitivity](luo_maunsell2018_criterion_sensitivity.md) localise *bias* manipulation to the superior colliculus, with V4 and other extrastriate visual areas (and LIP) modulating *sensitivity*. Roitman-Shadlen fits this picture: LIP build-up *slope* (sensitivity) scales with evidence quality, while the *threshold* (bias / commitment criterion) is determined elsewhere — plausibly by the SC's readout dynamics. For our program, this means LIP-like accumulator activations belong in the *encoder / memory* side of the recurrent ViT (where evidence is integrated), while the threshold / commit step belongs in the *actor head*, and these two should be cleanly architecturally separable. The published recurrent ViT does not yet enforce this separation explicitly; PRISM v1's variational inner loop ([the_user_architectural_program](../threads/the_user_architectural_program.md), THESIS §2.8) comes closer in spirit because it iterates until convergence — i.e., an implicit threshold on accumulated prediction-error.

**Connection to the DDM theoretical scaffold.** Ratcliff 1978 ([ratcliff1978_drift_diffusion](ratcliff1978_drift_diffusion.md)) is the abstract theory; Roitman-Shadlen 2002 is the neural instantiation. Together they define the *bounded-accumulation* framework we will use to interpret recurrent ViT response timing. The fitting strategy is: extract per-pass logits from the recurrent ViT actor head, treat the cumulative log-odds as the diffusion variable, fit a DDM with shared $v$ across difficulties and a learned commitment threshold, and compare the resulting parameters across architectures. PRISM v1 and PRISM v2 should be analysable in the same framework, with the inner variational loop counts playing the role of "ramps" and the variational convergence criterion playing the role of "threshold."

**Connection to LIP as priority map.** [bisley_goldberg2010_parietal_priority](bisley_goldberg2010_parietal_priority.md) frames LIP as a multi-purpose priority map. Our central self-attention module — which integrates feedback from many memory hubs and produces a per-token attention map — is the architectural analog of this multi-purpose priority surface, with the per-token attention values playing the role of priority. The Roitman-Shadlen result tells us that *the same population code that represents priority also implements perceptual evidence accumulation when that is the task demand*. For our program, this is the licence to use a single attention map for both "where to look" (saliency / priority) and "what to commit to" (decision variable), rather than insisting on architecturally distinct modules.

**Hanks & Summerfield 2017 ([hanks_summerfield2017_perceptual_decisions](hanks_summerfield2017_perceptual_decisions.md))** extends the Roitman-Shadlen-style analysis across species (monkey, rat, human) and across modalities (vision, audition); it is the natural review companion when arguing that the DDM-style accumulation found in macaque LIP is a general computational principle rather than a species-specific quirk.

**Gold & Shadlen 2007 ([gold_shadlen2007_decision_making](gold_shadlen2007_decision_making.md))** is the canonical review that builds on Roitman-Shadlen 2002 to articulate the *log-likelihood ratio* interpretation of LIP ramps: the firing rate is not merely "an accumulator" but specifically the accumulated log-odds of one alternative over another given observed evidence, which connects directly to the Bayesian readings of attention and prediction-error in [the_user_architectural_program](../threads/the_user_architectural_program.md). For our program this matters because it licenses interpreting the recurrent ViT's per-pass attention values as *log-evidence* contributions, which makes the cross-pass dynamics formally Bayesian rather than merely heuristic.

**Hawkins 1990 ([hawkins1990_attention_detectability](hawkins1990_attention_detectability.md))** is the original behavioural dissociation of sensitivity from criterion that the Sridharan and Luo-Maunsell papers extend; the Roitman-Shadlen LIP result sits *between* these — it is the neural mechanism that turns Hawkins's behavioural sensitivity into a measurable per-cell signal — and the three together pin down where in the brain each component of the SDT/DDM decomposition lives.

**Connection to attention literatures.** Although the recorded LIP cells are usually described in terms of "decision" rather than "attention," the spatial structure — response-field selectivity, contralateral organisation, integration of bottom-up plus top-down signals — is the same machinery the attention literature invokes (Bisley-Goldberg priority map; Reynolds-Heeger normalisation model). Our program's commitment to a *single* central self-attention substrate that does both is consistent with this empirical convergence in primate LIP.

## 8. Citations to follow

- `shadlen_newsome1996_motion_processing_lip` — the earlier fixed-duration motion-task LIP study Roitman-Shadlen builds on; should be added as a stub.
- `hanks_ditterich_shadlen2006_microstimulation_lip` — microstimulation of LIP during the RT motion task, the causal follow-up to Roitman-Shadlen 2002. Not yet in seed.
- `kim_shadlen1999_fef_lpfc_motion` — the parallel FEF/dlPFC accumulator finding. Not yet in seed.
- `ding_gold2010_caudate_decision` — caudate accumulator activity in the same task. Not yet in seed.
- `horwitz_newsome1999_sc_motion` — SC ramping in the motion task; complements [sridharan2017_sc_sensitivity_bias](sridharan2017_sc_sensitivity_bias.md). Not yet in seed.
- `mazurek_roitman_ditterich_shadlen2003_neural_implementation` — the formal mapping from DDM math to LIP-style population dynamics. Not yet in seed.
- `huk_shadlen2005_lip_integration` — direct demonstration that LIP integrates motion energy over time. Not yet in seed.
- `katz_yates_pillow_huk2016_optogenetic_lip` — optogenetic inactivation showing modest LIP role; the causal counterpoint to the strong correlational story. Not yet in seed.
- `drugowitsch_etal2012_optimal_temporal_integration` — optimal vs observed integration time-constants; modern reanalysis of the Roitman-Shadlen data. Not yet in seed.
- `crapse_lau_basso2018_sc_perceptual` — SC accumulator dynamics in perceptual decisions, with explicit comparison to LIP. Not yet in seed.
