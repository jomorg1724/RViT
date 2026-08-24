# MAH v1 source-panel inventory and VDA analogue requirements

Date: 2026-07-11

## Authority and counting rule

This inventory is grounded in the active `includegraphics` objects in:

- `source_material/mah/source_v1/main.tex`;
- `source_material/mah/source_v1/supplement/supplement.tex`;
- the 22 referenced source images themselves; and
- the rendered 23-page source PDF, `source_material/mah/2502.10955v1.pdf`.

Commented-out figure environments are excluded. The active source contains five main-paper figure objects and seventeen supplement figure objects. A source panel is counted from an explicit panel letter where present. Unlettered composites are split into scientifically coherent subpanels so that architecture, behavior, representation, decoding, intervention, value, and training-signal claims cannot be silently conflated.

Status vocabulary follows `STYLE_AND_QA_STANDARD.md`: `complete`, `partial`, `available`, `training`, `blocked`, `undefined`, and `inapplicable`. “Meaningful analogue” means that the estimand exists for the VDA environment; it does not mean that a current artifact is scientifically ready.

## Main paper

### M1 — task structure and cue semantics

Source: `figures/OrientationChangeTask_wbg.png`; label `fig:environment`; `main.tex:162-175`.

| Panel group | Source content | VDA analogue and prerequisite |
|---|---|---|
| M1a | Seven-step trial sequence: blank, cue, blank, array onset, maintenance, possible change, response. | Defined for every registered historical, comparator, probe, and fixed-grid task. Deterministic task specification is sufficient. |
| M1b | Cue at either S1 or S4, with displayed-validity ring configurations 25%, 50%, 75%, and 100%. | Defined for value-cued tasks. `validity4` requires a neutral/non-value cue. `vda_excl` has only the target-valid configuration; 25–75% alternatives are inapplicable. |
| M1c | Example change at the cued or opposing location. | Defined only when both locations can be active. Uncued-location change is undefined for singleton tasks and the target-only exclusion branch. |

Current figure-build disposition: rendered and visually inspected for the deterministic M1 schematic across 14 tasks (`validity4`, VDA1/2/4/9/16, exclusion, two probe variants, and fixed1/2/4/9/16). The coverage matrix remains `partial` until manuscript placement. These figures establish task semantics only; they contain no model measurement.

### M2 — model architecture

Source: `figures/figModel2.png`; label `fig:model`; `main.tex:179-190`.

| Panel group | Source content | VDA analogue and prerequisite |
|---|---|---|
| M2a | Patched scene and low-level visual features. | Defined for all VDA environments; geometry and token count must come from the resolved task/model configuration. |
| M2b | Self-attention with recurrent mnemonic feedback and attended context. | Defined per architecture family, not per task instance. The VDA series must distinguish `affine_ew`, `crossattn1`, and any other implemented routing rather than redraw the MAH mechanism generically. |
| M2c | Patch-wise recurrent memory update. | Defined when the checkpoint uses that memory mechanism; width and patch count must be recorded. |
| M2d | Actor/critic readout and recurrent temporal loop. | Defined for RL checkpoints. Probe variants reuse a base checkpoint and must not be drawn as separately trained models. |

Current disposition: rendered and visually inspected as a deterministic, source-hashed specification for the shared pipeline plus the admitted `affine_ew` and `crossattn1` routing families. The coverage matrix remains `partial` until manuscript placement. Dimensions remain symbolic or run-resolved, so the diagram does not inherit hard-coded four-patch or 1024-wide labels for controlled 16-token or d128 runs.

### M3A–F — behavioral cue effects

Source: `figures/fig_CUEeffect.png`; label `fig:behavior`; `main.tex:193-227`.

| Panel | Source estimand | VDA analogue and prerequisite |
|---|---|---|
| M3A | Response rate versus orientation change for four cue validities, change at S1. | Requires deterministic evaluation trials across change magnitude and displayed validity, with realized validity retained separately. |
| M3B | Response rate for S1 versus S4 changes under a 25% S1 cue. | Requires at least two active locations. Undefined for singleton; target-only exclusion has no ordinary uncued branch. |
| M3C | Response rate for S1 versus S4 changes under a 100% S1 cue. | Same location prerequisite; invalid/opposing trials must exist under the task's historical or controlled semantics. |
| M3D | Reaction time counterpart of M3A. | Requires an explicit trial-end convention and response-time support counts. |
| M3E | Reaction time counterpart of M3B. | Same as M3B plus reaction-time support. |
| M3F | Reaction time counterpart of M3C. | Same as M3C plus reaction-time support. |

Current disposition: eight historical figure sets are rendered, placed, and visually inspected for VDA1/2/4/9 × `affine_ew`/`crossattn1`, regenerated from the checksum-recorded aggregate `psych.npz` cache without checkpoint reruns. VDA1 uncued-location panels are explicitly `undefined`; historical VDA16 remains `blocked`; controlled checkpoints remain unavailable or training. The NPZ fields are labeled `uncued` but do not embed the evaluated spatial index, so the manuscript does not rename them as geometrically opposing locations. Lack of uncertainty, seed replication, and embedded producer/checkpoint lineage remains explicit. Probe variants are not separately trained behavior conditions.

### M4A–D — internal allocation

Source: `figures/newAttentionPlots.png`; label `fig:attention`; `main.tex:230-254`.

| Panel | Source estimand | VDA analogue and prerequisite |
|---|---|---|
| M4A | Attention maps for four cue validities across t=0…6 on no-change trials. | Requires architecture-specific attention/allocation tensors, shared scales, and task-aware geometry. `affine_ew` allocation must not be mislabeled as transformer attention. |
| M4B | S1 allocation at change time versus orientation change when S1 changes. | Requires event-time allocation and deterministic S1-change trials. |
| M4C | S1 allocation at change time when another location changes. | Requires a genuine uncued/opposing active location; undefined for singleton and target-only exclusion. |
| M4D | S1 and S4 allocation over trial time on no-change trials. | Requires at least two active locations and explicit location indexing. |

Current disposition: `partial` for archived historical conditions through `attn.npz`; `blocked` for controlled checkpoints. Allocation is evidence about model routing, not represented content.

### M5A–F — causal allocation intervention

Source: `figures/fig_attendMod.png`; label `fig:2`; `main.tex:257-276`.

| Panel | Source estimand | VDA analogue and prerequisite |
|---|---|---|
| M5A–C | Response-rate psychometrics under no clamp, change-location clamp, and competing-location clamp for low/high cue and cued/opposing change conditions. | Requires a supported intervention operator, paired trial seeds, valid clamp fields, natural controls, and at least two active locations for competitor panels. |
| M5D–F | Reaction-time counterparts of M5A–C. | Same intervention prerequisites plus trial-end timing. |

Current disposition: `partial` for historical affine checkpoints through the archived microstimulation bundle; cross-attention high-token clamp fields are invalid and must remain excluded. Controlled panels are `blocked` pending accepted checkpoints and a corrected paired-intervention cache.

## Supplement

### S1 — high-level recurrent agent over time

Source: `suppFigures/NetworkModelCircuit.png`; label `fig:ModHighLevel`; `supplement.tex:118-123`.

Single unlettered temporal schematic: image → self-attention → recurrent state → actor/critic, unrolled across consecutive timesteps. Meaningful once per architecture family. Current disposition: `available`.

### S2 — patch-based recurrent memory without cross-patch mixing

Source: `suppFigures/LSTMNoAttention.png`; label `fig:patch_based_LSTM`; `supplement.tex:140-147`.

Single schematic showing four parallel, weight-shared recurrent updates and spatially arranged memory. Meaningful once per architecture family. Current disposition: `available`.

### S3 — immediate-input self-attention before memory

Source: `suppFigures/SAplusLSTM.png`; label `fig:attention`; `supplement.tex:176-181`.

Single schematic separating the immediate visual scene, attention-derived visual percept, and recurrent memory update. A VDA analogue must use the implemented routing names and equations. Current disposition: `available`.

### S4 — recurrent feedback into allocation

Source: `suppFigures/SAplusLSTMplusRecurrentFeedback.png`; label `fig:self_attention_recurrent`; `supplement.tex:209-214`.

Single schematic showing immediate input and mnemonic feedback jointly shaping the attended visual percept. Meaningful per routing architecture, not per environment. Current disposition: `available`.

### S5 — memory-as-token alternative

Source: `suppFigures/MemTokensResult.png`; label `fig:MemAsToken`; `supplement.tex:223-231`.

Coherent subpanels: S5a architecture; S5b–d three response-rate psychometrics; S5e allocation over time. This is an alternative architecture comparison, not a required duplicate for every VDA task. Current disposition: `inapplicable` to an environment-only VDA manuscript unless a matching memory-token checkpoint family is admitted to scope.

### S6 — additive Q/K/V feedback alternative

Source: `suppFigures/AdditiveResult.png`; label `fig:AdditiveFeedback`; `supplement.tex:264-270`.

Coherent subpanels: S6a additive-feedback architecture; S6b–d behavioral psychometrics; S6e allocation over time. Current disposition: `inapplicable` unless a matching architecture family and checkpoints are admitted.

### S7 — multiplicative Q/K/V feedback alternative

Source: `suppFigures/MultiplicativeResult.png`; label `fig:QKVs`; `supplement.tex:327-333`.

Coherent subpanels: S7a multiplicative-feedback architecture; S7b–d behavioral psychometrics; S7e allocation over time. A VDA routing comparison may have a conceptual analogue, but `affine_ew` and `crossattn1` must not be relabeled as this source mechanism. Current disposition: `partial` only at the conceptual architecture-comparison level; empirical reproduction is `blocked` without matched valid checkpoints.

### S8 — decoding change location from all mnemonic slots

Source: `suppFigures/ConfusionMatricesMemoryClassificationToChange.png`; label `fig:ConfMatHAllSlots`; `supplement.tex:639-645`.

Four five-class confusion matrices: t=5 and t=6, each under natural allocation and maximal S1 allocation. Classes are no change and change at S1–S4. Requires held-out decoding, normalized rates, raw support, exact state/time identity, and a valid intervention. Current disposition: `partial` through archived decoding products; corrected cache absent. Location decoding is undefined when fewer than two active locations exist, and four-location classification is undefined outside four-active-item tasks.

### S9 — all-slot location decoding across S1 allocation conditions

Source: `suppFigures/decodingHAttentionS1.png`; label `fig:ConfMatHAllSlotsCue025`; `supplement.tex:647-654`.

Eight five-class confusion matrices: rows t=5 and t=6; columns natural 25% cue, uniform allocation, S1 allocation inhibited, and S1 allocation maximized. Requires the S8 decoder plus three valid intervention conditions. Current disposition: `blocked` pending corrected intervention-decoding caches. Four-class location structure is undefined for singleton/two-item tasks.

### S10 — binary change decoding from the first mnemonic slot

Source: `suppFigures/decodingH1AttentionS1.png`; label `fig:ConfMatFirstSlot`; `supplement.tex:658-665`.

Six binary confusion matrices: rows t=5 and t=6; columns natural allocation, maximal S1 allocation, and zero S1 allocation. The scientific question is whether one memory slot carries distributed change information. Requires held-out binary decoding and valid interventions. Current disposition: `blocked` for corrected analysis.

### S11 — decoding from the actor network’s first activation

Source: `suppFigures/confusionMatrixMu1.png`; label `fig:ActorLayer1Activation`; `supplement.tex:669-678`.

Eight matrices: a 2×2 group of five-class change-location matrices (t=5/t=6 × natural/maximal S1 allocation) and a 2×2 group of binary change-occurrence matrices under the same conditions. Requires an actor hidden layer with stable identity and corrected held-out decoders. Current disposition: `blocked`; actor-layer identity must be recorded rather than inferred from an old script.

### S12 — graded S1-attention impairment in actor decoding

Source: `suppFigures/confusionMatrixMu1_inhibitAttention.png`; label `fig:ActorLayer1ActivationS1Changes`; `supplement.tex:681-687`.

Ten binary confusion matrices: rows t=5 and t=6; columns form a graded relaxation of S1 allocation inhibition for S1-change trials. Requires a supported dose parameter, paired evaluation trials, and actor-layer decoding. Current disposition: `blocked`.

### S13 — actor-logit geometry by change location and magnitude

Source: `suppFigures/LogitsAndStimulusIntensities.png`; label `fig:LogitsChangeLocation`; `supplement.tex:692-699`.

Ten panels: one all-trial scatter colored by continuous change magnitude and its density counterpart, followed by scatter/density pairs for changes at S1, S2, S3, and S4. Axes are Wait and Declare-Change logits. Requires cached trial-level logits, change magnitude, location, and density-estimation parameters. Current disposition: `blocked`; no accepted VDA-series logit cache has been established.

### S14 — actor-logit geometry under S1 allocation interventions

Source: `suppFigures/LogitsAndS1Attention.png`; label `fig:LogitsS1Attention`; `supplement.tex:701-708`.

Six panels arranged as three scatter/density pairs: natural S1-change trials, S1 allocation maximized, and S1 allocation minimized. Requires S13 plus valid paired intervention data. Current disposition: `blocked`.

### S15A–I — TD error, value, and policy behavior

Source: `suppFigures/ValuefigureThree.png`; label `fig:3`; `supplement.tex:721-741`.

| Panel group | Source estimand | Requirement |
|---|---|---|
| S15A–C | TD error versus orientation change under cue/change-location conditions and selected allocation clamps. | Trial-level reward, value estimates, next-state values, terminal handling, and exact TD convention. |
| S15D–F | TD error versus allocation dose or orientation change for matched and mismatched intervention locations. | Valid paired intervention and location semantics. |
| S15G | Value estimate versus orientation change with allocation maximized at the change location. | Critic output and intervention cache. |
| S15H | Value estimate versus allocation dose for an opposing-location change. | Two active locations and critic output. |
| S15I | Hit rate versus allocation dose. | Paired behavioral intervention trials. |

Current disposition: `blocked`; archived manuscript prose is not a substitute for a versioned trial-level cache.

### S16A–F — criterion and sensitivity under allocation manipulation

Source: `suppFigures/CritSens.png`; active label `fig:2`; `supplement.tex:828-856`.

The active image visibly contains six panels, not twelve:

- S16A: criterion versus S1 allocation at change time;
- S16B: criterion versus S1 allocation at cue time while allocation at the eventual change location is maximized at change time;
- S16C: criterion versus S1 allocation at cue time;
- S16D–F: sensitivity counterparts of S16A–C.

Each panel compares 25%/100% S1 cues and S1/S4 change locations, with natural-condition points overlaid. The active caption is stale: it describes A–C hit rates, D–F reaction times, and G–L criterion/sensitivity, but the included image has only A–F criterion/sensitivity. Reproduction must follow the estimands visible in the included image and explicitly document the source-caption conflict rather than invent G–L.

Current disposition: `partial` for archived affine microstimulation evidence; `blocked` for corrected controlled analyses. Location-specific panels are undefined for singleton tasks and partly inapplicable to target-only exclusion.

### S17 — supervised-action, supervised-belief, and RL training signals

Source: `suppFigures/supervised_versus_RL.png`; label `fig:supervised`; `supplement.tex:861-902`.

Twelve panels in a 4×3 matrix. Columns are supervised actions, supervised beliefs, and reinforcement learning. The first three rows are behavioral response-rate comparisons; the fourth row is allocation across trial time. This is a training-objective comparison, not an automatic per-environment requirement. Current disposition: `inapplicable` to the present VDA environment series unless matched supervised checkpoint families are deliberately trained and admitted.

## Cross-environment applicability rules

1. M1 is required for every registered task; it is the only source object that can be complete without a learned checkpoint.
2. M2 and S1–S4 are required once per implemented architecture/routing family, with task-specific geometry annotations where geometry changes.
3. M3 and M4 are broadly applicable to trained value-cued tasks, but comparator/probe/singleton/exclusion semantics can make individual location or validity panels undefined or inapplicable.
4. M5, S9–S12, S14–S16 require valid interventions; they cannot be inferred from natural trials.
5. S8–S12 require corrected held-out decoders with named state, time, label, chance level, support, and seed split.
6. S13–S15 require trial-level policy/critic caches; figure pixels or reported prose are not numerical evidence.
7. S5–S7 and S17 are architecture/training-objective comparisons. They should not be duplicated across every VDA environment unless their compared model families exist.
8. Historical, comparator, probe, and controlled fixed-grid evidence remain separate columns in the coverage matrix. A source analogue shared in scientific meaning does not transfer empirical completion between those lineages.

## Immediate matrix consequences

- Expand the matrix from figure-object rows to the panel groups above.
- Record the S16 source-caption/image contradiction explicitly.
- Keep `vda_probe_cued` and `vda_probe_uncued` at M1 complete but analysis-blocked; they have no dedicated trained checkpoint evidence.
- Keep `validity4` separate from value-cued VDA because the value cue and several cue-value claims are inapplicable.
- Mark singleton location-comparison and location-decoding panels `undefined`, not merely missing.
- Mark source-only architecture and supervised-training comparisons `inapplicable` unless their model families enter scope.
- Do not promote archived `psych.npz`, `attn.npz`, `decode.npz`, or `microstim.npz` to controlled evidence; their present role is historical/partial pending corrected provenance and producers.
