# MAH-to-VDA figure coverage matrix

Status vocabulary: **complete** = deterministic data, rendered figure, and manuscript placement exist; **partial** = an analog exists but omits source panels or lacks corrected provenance; **available** = a suitable preserved checkpoint or deterministic specification exists and the producer can be built; **training** = the checkpoint is not scientifically ready; **blocked** = a required checkpoint, cache, or producer is absent; **undefined** = the estimand does not exist for that environment and must receive an explicit explanatory panel; **inapplicable** = the source comparison is outside the environment's scientific scope.

## Canonical source inventory

The MAH v1 source has 22 active image objects: five in `main.tex` and seventeen in `supplement/supplement.tex`. Three commented long-task placeholders are excluded. Older VDA9 reports organize the science into seventeen informal blocks, but that does not reproduce all active source objects one-for-one. `MAH_SOURCE_PANEL_INVENTORY.md` is the definitive source-object and panel-group inventory. `PANEL_COVERAGE.csv` is the machine-readable environment matrix: 68 scientifically coherent panel groups × 14 registered environments = 952 explicit dispositions. It includes every M1–M5 and S1–S17 object, rather than treating an absent analogue as an omission.

| ID | Source image | Scientific purpose | Current VDA analog | Current global state |
|---|---|---|---|---|
| M1 | `OrientationChangeTask_wbg.png` | Seven-frame task and cue configurations | `vda_series/task_figures.py` and `reports/vda_series/figures/task/m1_task_<environment>.{pdf,png,json}` for fourteen VDA/comparator/probe environments | Complete for the admitted task-specification cells: deterministic products, manuscript placement, metadata, vector/raster exports, and rendered visual QA are present |
| M2 | `figModel2.png` | Full model information flow | `figures/architecture/m2_architecture.{pdf,svg,png}` with source-hashed metadata | Complete as a specification of inspected current source and placed in the manuscript; the historical M3 cache does not prove checkpoint-to-source revision identity |
| M3 | `fig_CUEeffect.png` | Six-panel psychometric/chronometric battery | Eight `figures/behavior/m3_behavior_<task>_<family>.{pdf,svg,png,json}` sets regenerated from `vda_sweep/figs/psych.npz` for VDA1/2/4/9 × `affine_ew`/`crossattn1` | Complete for the eight admitted placements; VDA1 uncued-location panels are explicitly undefined, the NPZ's `uncued` fields are not promoted to geometrically opposing locations, historical VDA16 remains blocked, and controlled series remain unavailable or training |
| M4 | `newAttentionPlots.png` | Time-resolved attention maps and scalar summaries | Provenance-closed first-wave VDA4/VDA9 products plus legacy `vda_sweep/attn.npz` and `repro9/fig4A-C_*` | M4B is complete for historical VDA4/VDA9 from exact iteration-19999 checkpoints with 96 trials and all query rows retained; cue-validity sweeps, invalid-change attention, and the registered S1/S4 temporal contrast remain partial |
| M5 | `fig_attendMod.png` | Causal attention manipulation on behavior | `vda_sweep/microstim.npz`, `repro9/fig5AF_*`, `fig5GK_*` | Partial; high-token cross-routing and paired-intervention provenance require corrected outputs |
| S1 | `NetworkModelCircuit.png` | High-level environment→Recurrent ViT→memory→agent circuit | folded into `repro9/fig2_schematic_*` | Missing as a one-to-one source analog |
| S2 | `LSTMNoAttention.png` | Patch-based recurrent-memory operation | no environment-specific source analog | Missing |
| S3 | `SAplusLSTM.png` | Spatial context entering recurrent memory | no environment-specific source analog | Missing |
| S4 | `SAplusLSTMplusRecurrentFeedback.png` | Recurrent feedback loop | folded into `repro9/fig2_schematic_*` | Missing as a one-to-one source analog |
| S5 | `MemTokensResult.png` | Memory-token architecture and behavior comparator | no admitted VDA-set-size comparator | Inapplicable to the current environment series; becomes blocked only if the comparator family is admitted |
| S6 | `AdditiveResult.png` | Additive-feedback architecture and behavior comparator | no admitted VDA-set-size comparator | Inapplicable to the current environment series; becomes blocked only if the comparator family is admitted |
| S7 | `MultiplicativeResult.png` | Multiplicative-feedback architecture and behavior | `repro9/fig567_affine_ew.png` is only a conceptual approximation | Inapplicable as a one-to-one source reproduction because VDA routing differs from the MAH multiplicative Q/K/V product |
| S8 | `ConfusionMatricesMemoryClassificationToChange.png` | Change-location decoding from full memory | legacy `vda_sweep/decode.npz`, `repro9/fig8_*` | Partial; VDA2/VDA9 legacy fields invalid and corrected versioned output pending |
| S9 | `decodingHAttentionS1.png` | Location decoding across attention interventions | `repro9/fig8_*`/`fig11_*` approximate | Partial; one-to-one panel mapping absent |
| S10 | `decodingH1AttentionS1.png` | Change-occurrence decoding from one memory slot | `repro9/fig9_*` | VDA9 analog exists; other environments absent |
| S11 | `confusionMatrixMu1.png` | Location and occurrence decoding from actor activation | `repro9/fig10_*` | VDA9 analog exists; other environments absent |
| S12 | `confusionMatrixMu1_inhibitAttention.png` | Graded actor-layer decoding under inhibition | `repro9/fig11_*` | VDA9 analog exists; other environments absent |
| S13 | `LogitsAndStimulusIntensities.png` | Actor-logit geometry by signal and location | `repro9/fig12_*` | VDA9 analog exists; other environments absent |
| S14 | `LogitsAndS1Attention.png` | Actor-logit geometry under attention manipulation | `repro9/fig13_*` | VDA9 analog exists; other environments absent |
| S15 | `ValuefigureThree.png` | Value and temporal-difference signals | `repro9/fig14_*` | VDA9 analog exists; other environments absent |
| S16 | `CritSens.png` | Six visible criterion/sensitivity panels A–F | `vda_sweep/sdt.npz`, `repro9/fig16_*` | Partial; corrected high-token cross-routing outputs pending. The active caption's references to A–L and hit-rate/reaction-time panels conflict with the included six-panel image and are not counted. |
| S17 | `supervised_versus_RL.png` | Supervised-action versus supervised-belief versus RL comparison | `repro9/fig17_*` is an unmatched approximation | Inapplicable to the admitted environment series because matched supervised checkpoint families do not exist |

## Panel-level matrix

`PANEL_COVERAGE.csv` is the authoritative panel-group × environment table. It was validated after generation for:

- 68 unique panel groups;
- all 22 active source objects, M1–M5 and S1–S17;
- all 14 registered environments;
- 952 populated status cells;
- status values restricted to `complete`, `partial`, `available`, `training`, `blocked`, `undefined`, and `inapplicable`.

The compiled manuscript contains 118 `complete` M1--M4 panel--environment cells. The two promotions are M4B for historical VDA4 and VDA9. Completion requires admitted evidence, manuscript placement or explicit accounting, and rendered-page QA; standalone figure generation alone is insufficient. Historical VDA16 result cells are `blocked`, not `training`; its archived iteration-599 lineage is incomplete. The separate controlled `vda_fixed16` seed-0 run was interrupted by `SIGKILL` after metrics through iteration 2880 and a checkpoint through iteration 2799. It has no final checkpoint or exact-resume state and remains `training`, not completed evidence.

The matrix also encodes three classes of honest absence:

1. `undefined` for estimands that cannot exist, such as opposing-location decoding in singleton tasks;
2. `inapplicable` for source-only architecture or training-signal comparisons outside the admitted VDA series; and
3. `blocked` for defined analyses whose checkpoint, corrected producer, or evidence cache is absent.

## Environment-level state

| Environment | Geometry/tokens | Checkpoint state | Existing manuscript/figure coverage | Required treatment |
|---|---:|---|---|---|
| `validity4` | 2×2 / 4 tokens / 4 active | Preserved affine and cross-attention comparator checkpoints | M1 complete as a standalone neutral-value comparator; one saved validity analysis but no dedicated manuscript | Use as the uniform-reward/non-value comparator; preserve archived cue-including realized-validity semantics |
| `vda1` | 2×2 / 4 tokens / 1 active | Preserved affine and cross-attention checkpoints | M1 complete as a standalone figure; six-panel battery summaries and set-size figures exist, but no full reproduction paper | Build all remaining defined panels; mark spatial cueing and change-location estimands undefined where no alternative location/class exists |
| `vda2` | 2×2 / 4 tokens / 2 active | Preserved affine and cross-attention checkpoints; canonical `_2x2` path | M1 complete as a standalone figure; six-panel battery summaries exist; legacy location decode invalid | Regenerate corrected decoding before manuscript claims |
| `vda4` | 2×2 / 4 active | Exact affine and cross-attention iteration-19999 checkpoints selected and hashed for the approved first wave | M1 and historical aggregate M3 complete; provenance-closed environment, 4×7 attention, and three-panel psychometric products placed as a separate checkpoint-recomputed section; M4B complete | Preserve the distinction between aggregate-cache and recomputed-checkpoint evidence; next add invalid-change attention, corrected decoding, and paired interventions |
| `vda9` | 3×3 / 9 active | Exact affine and cross-attention iteration-19999 checkpoints selected and hashed for the approved first wave | M1 and historical aggregate M3 complete; provenance-closed environment, 9×7 attention, and three-panel psychometric products placed as a separate checkpoint-recomputed section; M4B complete | Preserve the lower cross-attention S9 response as verified checkpoint behavior; next add invalid-change attention, corrected decoding, and paired interventions |
| historical `vda16` | 4×4 / 16 active | Partial/incomplete; stop reason unknown; task correctness remained near chance at checkpoint 599 | M1 complete as a task-derived schematic; no valid endpoint manuscript | May receive clearly provisional engineering diagnostics only; not a completed scientific reproduction |
| `vda_excl` | 1×2 exclusion paradigm | Preserved affine and cross-attention checkpoints | M1 complete as a standalone figure with the distractor-present and target-alone branches identified; no full reproduction paper | Define a paradigm-specific mapping rather than forcing invalid set-size panels |
| `vda_fixed1` | 4×4 / 16 tokens / 1 active | No trained checkpoint | M1 complete as a task-derived schematic; no model-result panels | Train matched seeds; singleton undefined panels remain explicit |
| `vda_fixed2` | 4×4 / 16 tokens / 2 active | No trained checkpoint | M1 complete as a task-derived schematic; no model-result panels | Train matched seeds, then full corrected battery |
| `vda_fixed4` | 4×4 / 16 tokens / 4 active | No trained checkpoint | M1 complete as a task-derived schematic; no model-result panels | Train matched seeds, then full corrected battery |
| `vda_fixed9` | 4×4 / 16 tokens / 9 active | No trained checkpoint | M1 complete as a task-derived schematic; no model-result panels | Train matched seeds, then full corrected battery |
| `vda_fixed16` | 4×4 / 16 tokens / 16 active | Seed-0 MPS run interrupted by `SIGKILL`; checkpoint through iteration 2799, metrics through 2880, no final checkpoint or exact-resume state | M1 task specification is placed and visually inspected; no admissible model-result panels | Any continuation is a new warm-start lineage, never an exact resume. Require an immutable accepted endpoint and matched independent seeds before scientific analysis. |
| `vda_probe_cued` | 2×2 / 4 active | No dedicated checkpoint; intended for zero-shot evaluation of a preserved VDA4 model | M1 complete with a cued-location delay probe; no completed probe analysis | Evaluate only as a matched pair with `vda_probe_uncued`; a decoder or actor response alone does not establish rehearsal |
| `vda_probe_uncued` | 2×2 / 4 active | No dedicated checkpoint; intended for zero-shot evaluation of a preserved VDA4 model | M1 complete with an uncued-location delay probe; no completed probe analysis | Use as the required control for the cued probe; add a causal delay disruption before rehearsal language |

## Next evidence build order

1. Preserve the approved first-wave production tree and its byte-identical manuscript snapshots; never substitute the rejected repository-resident production root.
2. Backfill remaining manifests and correct deterministic location-decoding and high-token clamp producers into versioned output paths.
3. Add the registered invalid-change M4 contrasts and matched-width analyses without promoting descriptive attention to causal evidence.
4. Extend the provenance-closed recomputation to historical VDA1/VDA2 only where estimands are defined; retain explicit singleton undefined cells.
5. Snapshot controlled fixed-grid checkpoints only when behavior warrants evaluation; never analyze a checkpoint while it is being overwritten.
6. Treat any controlled VDA16 continuation as a new warm-start lineage, then train matched `vda_fixed1/2/4/9/16` seed sets before capacity claims.
7. Add supervised, memory-token, and additive comparators only through explicitly matched training. Until then, S5, S6, and unavailable S17 cells remain visible rather than fabricated.
8. Repeat full dependency, manifest, and rendered-page review after every evidence-bearing manuscript revision.
