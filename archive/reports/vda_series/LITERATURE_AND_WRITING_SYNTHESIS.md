# VDA literature and scientific-writing synthesis

## Purpose and authority

This brief converts the MAH manuscript structure and the local neuroscience evidence notes into writing rules and testable interpretation boundaries for the VDA reproduction series. It is a routing and drafting aid, not a substitute for the primary papers. Quantitative or causal claims must still trace to the cited source, producer, checkpoint, and cached analysis artifact.

The local load-bearing notes reviewed here are:

- `research_db/papers/carrasco2011_visual_attention_25y.md`;
- `research_db/papers/herman_krauzlis2017_sc_change_detection.md`;
- `research_db/papers/luo_maunsell2018_criterion_sensitivity.md`;
- `research_db/papers/moore_armstrong2003_fef_microstim.md`;
- `research_db/papers/cavanaugh_wurtz2004_sc_change_blindness.md`;
- `research_db/papers/luck_vogel1997_wm_capacity.md`;
- `research_db/papers/awh_jonides2001_overlapping_attention_wm.md`;
- `research_db/papers/panichello_buschman2021_shared_mechanisms.md`.

The source-paper structure comes from `reports/vda_series/source_material/mah/source_v1/main.tex` and `supplement/supplement.tex`. The local MAH PDF was separately rendered and inspected across all 23 pages.

## Companion-manuscript boundary

The publication program contains two related but non-interchangeable arguments:

1. The **empirical RViT/VDA manuscript** asks what trained recurrent models do, what information their states expose, and which model interventions causally alter their behavior.
2. The **normative VDA manuscript** asks when value-dependent reallocation of perceptual sensitivity improves expected reward relative to criterion adjustment and decorrelation.

The normative analysis makes no circuit-level implementation claim. The empirical model does not establish that it implements the normative optimum. In empirical task names, `VDA` remains the historical environment-family label; when discussing the normative mechanism, define VDA narrowly as value-dependent **sensitivity** reallocation rather than any value-dependent criterion shift.

## Governing narrative

The VDA papers should proceed from what the task requires to what the model does, then to what an intervention changes, and only then to biological interpretation. This order is both scientifically safer and easier to read:

1. Define the observable task: cue, value, displayed validity, realized target distribution, delay, change, and response.
2. Establish behavior: accuracy, hit and false-alarm structure, psychometric threshold, chronometric behavior, sensitivity, and criterion.
3. Establish representation: attention maps, memory or actor decoders, temporal geometry, and uncertainty.
4. Establish intervention: paired, location-specific injection and inhibition with the same checkpoint and matched trial stream.
5. Test alternatives: external-noise exclusion, criterion-only explanations, decoding without behavioral consequence, and architecture/objective comparators.
6. Interpret cautiously: identify a model–experiment correspondence, state what is shared, and state what is not established.

MAH uses the main text to carry this causal arc and the supplement to expose architecture details, alternate mechanisms, decoder structure, actor geometry, value/temporal-difference signals, signal-detection decomposition, and objective comparisons. The VDA series should retain that division rather than compressing several distinct estimands into one crowded page.

## Evidence ladder and permitted language

| Evidence class | What it can establish | What it cannot establish |
|---|---|---|
| Task-derived schematic | Geometry, timing, active-item count, and sampling semantics | Learned behavior, convergence, mechanism, or capacity |
| Behavioral evaluation | What one checkpoint does on specified held-out trials | Training-run replication, internal representation, or biological mechanism |
| Decoder or geometry analysis | Information available to a fitted readout under an explicit split | Use by the policy, persistent maintenance, necessity, or causal control |
| Attention-map summary | The model's recorded routing/gating tensor under named semantics | A literal neural attention map or functional necessity |
| Paired model intervention | Sensitivity of behavior to a defined model component under the tested perturbation | Biological equivalence to FEF, SC, LPFC, or cortical stimulation |
| Cross-checkpoint comparison | Association among separately trained checkpoints | A within-model dose response, a pure capacity law, or convergence |
| Matched multi-seed controlled series | Training-distribution uncertainty under the controlled protocol | Human or primate cognitive capacity without a separate correspondence argument |

Use “corresponds to,” “is structurally analogous to,” or “tests a model-level counterpart of.” Do not write that a tensor “is FEF,” a recurrent state “is working memory,” an actor layer “is LPFC,” or a routing intervention “is SC stimulation.”

## Source-specific constraints

### Carrasco: behavior before gain language

Carrasco's review supports the need to distinguish faster responding from improved discriminability and to separate contrast-gain, response-gain, spatial-resolution, and external-noise accounts. A leftward psychometric shift, a vertical response change, a change in d′, and a change in criterion are not interchangeable. “Gain modulation” is a phenomenological description shared by multiple mechanistic frameworks; a multiplicative operation in the model does not by itself identify the biological mechanism.

VDA implication: report psychometric and chronometric curves beside d′ and criterion. Use `vda_excl` to test the distractor-exclusion prediction rather than inferring external-noise reduction from ordinary cueing alone.

### Herman and Krauzlis: detection timing and behavior covariation

The relevant empirical sequence is cue modulation, change-evoked activity, hit–miss differentiation, and activity latency relative to the manual response. The result is stronger than a static map because the neural signal covaries with detection and precedes the response. It nevertheless does not license naming an arbitrary model layer as SC.

VDA implication: align model signals to the change event, separate hit and miss trials, and relate signal latency to response latency. A temporal correspondence is meaningful only when event definitions, trial filtering, and response timing are explicit.

### Moore–Armstrong and Cavanaugh–Wurtz: spatially specific causal tests

These studies motivate retinotopically specific causal interventions. Their load-bearing logic is not merely that stimulation changes performance; it is that the intervention is spatially matched, subthreshold or behaviorally controlled, and compared with nonmatching locations or conditions.

VDA implication: pair attention injection and inhibition at cued, changed, and control locations on the same checkpoint and matched trials. Describe this as a model-level causal perturbation with spatial specificity. Do not infer tissue identity or biological stimulation equivalence.

### Luo and Maunsell: criterion is not sensitivity

Signal-detection theory partitions behavioral change into sensitivity and criterion. LPFC modulation accompanied both forms of attentional change, with distinguishable signatures, while the broader literature cited by the note associates visual-cortical modulation more selectively with sensitivity. This argues against a monolithic “attention signal.”

VDA implication: every intervention and value manipulation should report d′ and criterion separately. A performance gain driven by a liberal declaration policy must not be described as improved sensory representation. A faithful Luo–Maunsell analogue requires manipulations designed to dissociate sensitivity and criterion, not merely post hoc decomposition of one reward condition.

### Luck and Vogel: capacity is an object-level behavioral claim

The classic result concerns the number of integrated objects retained under a specific human change-detection paradigm. It is not a theorem that every visual memory system has four slots.

VDA implication: fixed-grid set-size experiments must vary active items while preserving geometry, token count, observation size, architecture, training budget, and seed protocol. Report representation and prediction before interpreting capacity. A threshold trend across historical VDA1/2/4/9 checkpoints is not a pure capacity law because task semantics, geometry, and interfaces differ.

### Awh and Jonides: rehearsal needs a delay-specific test

The review links spatial rehearsal to selective attention through facilitation at remembered locations and disruption when attention is drawn elsewhere. Mere cue-location decodability does not establish rehearsal, and change-location decoding at the event does not establish delay maintenance.

VDA implication: use a delay probe at remembered and uncued locations to test facilitation, then a matched disruption or attentional-shift manipulation to test necessity. Label an unexecuted probe protocol as pending and a decoder-only result as representational, not causal rehearsal evidence.

### Panichello and Buschman: shared control requires matched tasks and dynamics

The study motivates population-level representational transformation and a distinction between shared control in PFC and independent representations elsewhere. The shared-mechanism claim comes from matched attention and selection-from-working-memory tasks, not from one task alone.

VDA implication: examine time-resolved representational geometry and whether selected information enters a common output subspace. Do not claim a domain-general controller unless matched sensory-attention and memory-selection tasks demonstrate a shared transformation with held-out validation.

## Testable VDA hypotheses and required measures

| Hypothesis | Required measures | Minimum falsifier or boundary |
|---|---|---|
| Valid cues improve perceptual sensitivity | Psychometric threshold, d′, false alarms, RT/latency | Criterion shifts without d′ improvement |
| Value changes selection rather than only declaration policy | Location-specific d′ and attention/representation measures plus criterion | Global criterion shift with no location-specific representational or sensitivity effect |
| Recorded attention routing is behaviorally functional | Paired inject/inhibit interventions, matched trials, cued/change/control locations | Routing changes without a reproducible behavioral effect |
| Detection signals precede and predict response | Event-aligned hit/miss trajectories and trial-level signal-to-response latency relation | Signal appears only after response or does not distinguish outcomes |
| Spatial attention contributes to delay rehearsal | Cued-versus-uncued delay probes and a matched disruption test | Decoder-only availability or probe facilitation without disruption sensitivity |
| Set-size effects reflect controlled capacity pressure | Fixed 4×4 geometry, 16 tokens, matched architecture/budget/seeds, behavior and representation | Historical mixed-geometry association or one incomplete seed |
| Selection is a temporal representational transformation | Held-out subspace/trajectory analysis with explicit time alignment | Static separability alone |
| Attention reduces distractor-related external noise | `vda_excl` target-alone versus distractor-present contrast with paired intervention | Equal benefit when no distractor is present, absent other mechanism evidence |

## Figure and prose rules

1. Start each results section with the estimand and denominator, not with a model tensor name.
2. State task semantics locally in every caption that compares historical environments, including displayed versus realized validity.
3. Give every prominent number an evidence class and artifact field. “Reported” values must not be phrased as independently regenerated.
4. Keep behavior, representation, and intervention in separate panels or clearly separated panel groups.
5. Put negative and undefined results in the figure program. Singleton change-location or uncued comparisons are scientifically undefined, not missing data.
6. Use event-aligned time axes and mark cue, array onset, change, and response windows consistently.
7. Use color plus line style, marker, fill, or texture; do not encode a condition only by hue.
8. Distinguish evaluation-trial uncertainty from training-seed uncertainty. Never use repeated trials from one checkpoint as if they were independent trained models.
9. Place the limitation beside the claim it constrains. Do not collect all epistemic boundaries in a distant discussion paragraph.
10. End each environment paper by resolving the opening task question, then identify the next experiment required to distinguish remaining mechanisms.

Every caption must identify the checkpoint/run and model variant, task and realized validity, intervention and control, sample size and its unit (trials, batches, or independently trained seeds), summary statistic and uncertainty, chance or uniform baseline, supported conclusion, and explicit non-conclusion.

Use the following terms consistently:

- **attention/priority map:** model allocation weights over locations; reserve *saliency* for a measured stimulus-driven quantity;
- **working-memory state:** a recurrent latent state; `d_mem`, hidden width, and decoder accuracy are not human memory span;
- **sustained cue-directed attention:** an acceptable temporal description; *rehearsal* requires behavioral benefit and causal delay-period evidence;
- **perturbation, clamp, injection, virtual lesion:** model-side terms; “microstimulation analogue” requires an immediate scope boundary;
- **decodable:** information available to the fitted probe, with cue location separated from change location and delay codes separated from event-time codes.

## Currently unsupported manuscript claims

Until the missing analyses are completed, do not claim:

- a cross-routing PRIORITY-versus-VALUE dissociation from an affine-only comparison;
- a quantitative three-way Carrasco decomposition or dedicated external-noise result;
- “validity blindness” caused by forgetting, sustained delay-period cue-location memory, or attention-based rehearsal;
- a working-memory-capacity law from `d_mem` or the mixed historical VDA1/2/4/9 ladder;
- biological homology to FEF, SC, LIP, or LPFC;
- communication-subspace rotation or rerouting without a cross-validated communication-geometry analysis;
- convergence, replication, or population-level robustness from one checkpoint or one completed logged phase;
- that historical VDA16 is a completed negative result.

The SC sensitivity-versus-choice-bias literature must be presented as task- and analysis-dependent. The local `herman2018_midbrain_decisions.md` card contains language that conflicts with the local Sridharan record, whose abstract attributes the reanalyzed SC manipulation effects primarily to choice bias. Resolve this against the primary papers before publication; do not silently choose the architecturally convenient interpretation.

## Drafting template for a result paragraph

A strong paragraph should answer four linked questions in connected prose: What observable changed? Which cached measure and checkpoint establish it? Which mechanism remains consistent with that change? What alternative or missing control prevents a stronger interpretation? The paragraph should not begin with a brain-region analogy, and the analogy should never outrun the model-level evidence.

## Current program boundary

The deterministic M1 task schematics now document the historical VDA environments, the `validity4` comparator, both zero-shot delay-probe variants, and all five controlled fixed-grid environments, but they are not learned-model results. Historical VDA16 remains partial/incomplete with an unknown stop reason; task correctness was near chance at checkpoint 599. The controlled `vda_fixed16` seed-0 run is prospective, single-seed, and in progress. Neither lineage currently supports a completed VDA16 capacity conclusion.
