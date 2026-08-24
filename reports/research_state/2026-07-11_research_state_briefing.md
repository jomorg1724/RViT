# AttentionManuscript research-state briefing

**Audit date:** 2026-07-11  
**Scope:** manuscript lineage, MAH baseline, experiment artifacts, VDA set-size program, current directions, evidence quality, `research_db`, and non-destructive organization.  
**Companion inventory:** `reports/research_state/2026-07-11_battery_metrics_inventory.csv` (all 43 discovered `battery_sweep_results/**/metrics.csv` files).

## Executive judgment

The workspace contains two companion paper families that must not be collapsed into one lineage. “MAH” refers to the Morgan–Albanna–Herman empirical baseline, *A recurrent vision transformer shows signatures of primate visual attention* (arXiv:2502.10955v1). RViT+ and `reports/upgraded_paper/` extend that 2025 neural-model paper. A different 2026 paper, *When Does Value-Directed Attention Matter?*, is a normative signal-detection model. `Critique/`, `Rebuild/`, and `Reconstruction/` audit and correct that normative paper; they are not corrected editions of arXiv:2502.10955. The current empirical and normative manuscripts are companions, not successive versions.

The strongest current result is a four-point, single-checkpoint-per-condition set-size characterization of the affine-feedback model at 1, 2, 4, and 9 active stimuli. All four canonical runs contain 20,000 logged rows and final checkpoints; this establishes phase completion, not a formal convergence criterion or cumulative lifetime update count. Their displayed-validity threshold effects increase from approximately 0.15° to 2.21° across the ladder. Other mechanisms do not scale monotonically: clamp-induced sensitivity changes shrink with set size, criterion effects reverse locally, and sustained attention is not a monotone ladder. The result supports load-dependent validity use, but the simultaneous changes in grid, token count, task support, and training lineage prevent it from being called a pure capacity law.

VDA16 is not a completed failure. Its four preserved metrics phases stop at approximately 622–690 logged iterations; the newest checkpoints are at iteration 599. They remain near chance at the starting difficulty. Relative to a fresh 20,000-row phase, roughly 97% was not logged, but absent manifests and because resume counters can reset, cumulative lifetime training cannot be reconstructed exactly. The preserved evidence establishes only that learning had not begun by checkpoint 599; `results_vda_battery.tex:23-24` is wrong to describe that checkpoint as a consumed training budget.

The newest completed training direction is robustness and scaling around the Baruni/value task and the VDA ladder. A memory-noise perturbation of the Baruni `crossattn1` model reaches strong rolling accuracy even at noise σ=1.0, while the source code and exact flags needed to reproduce that perturbation are not present in the current `RViT_plus_paper_jepa_grid9/` tree. This is interesting evidence of state robustness but currently has only artifact-level, not reproducible-finding-level, status. Capacity (`d_mem=128` versus `256`) has preserved runs, contradicting the open manuscript section’s claim that the larger run was not preserved, but no matched behavioral battery has yet been run. Rehearsal has an implemented environment but no training or probe result.

The workspace is navigable only by prior knowledge. `research_db` is a strong literature corpus and a structurally clean graph, but it is not yet the project’s empirical memory: it has no findings notes, experiment briefs, conversations, current work nodes, or links to VDA1/2/4/9/16, the battery sweep, or the upgraded manuscript. The safest next move is not a bulk file reorganization. It is to add a canonical artifact registry and experiment findings layer, repair semantic contradictions, and only then decide which historical trees are superseded or archival.

## 1. Canonical source and manuscript lineage

| Layer | Canonical artifact | What it establishes | Status |
|---|---|---|---|
| Empirical Recurrent ViT / MAH baseline | arXiv:2502.10955v1 and its bundled supplement | Morgan, Albanna, and Herman’s 2025 recurrent neural model of cued orientation-change detection. Establishes primate-like psychometrics, cueing/RT effects, recurrent attention dynamics, decoding, SDT analyses, and causal attention perturbations. | Baseline for RViT+ and the upgraded empirical paper. No local PDF named for the arXiv ID was found. |
| RViT+ design and implemented extensions | `RVIT_PLUS_DESIGN.md`, `RViT_plus_paper_jepa_conv/`, and `RViT_plus_paper_jepa_grid9/` | May 2026 architecture proposal followed by several implemented SS4/SS9 variants and reproduction manuscripts. | Extensions/reproductions of the empirical MAH paper, not corrected editions. |
| Frozen normative source | `Critique/source/main.pdf` | *When Does Value-Directed Attention Matter? A Normative Model with Independent Attentional Benefit and Cost*; a stationary ideal-observer/SDT model with no transformer, recurrent memory, or actor–critic network. | Source audited by `Critique/`; separate from empirical MAH. |
| Normative critique and technical repair | `Critique/` and `Rebuild/manuscript/` | Audits categorical claims, then adds the correlation/decorrelation lever, distributional criterion results, escape thresholds, and broader conservation/allocation analyses. | `Rebuild/` is the deepest technical/provenance record. |
| Canonical corrected normative manuscript | `Reconstruction/manuscript/main.tex`, `main.pdf`, and `TRACE.md` | Public-facing reconstruction of the normative paper using Critique/Rebuild-supported claims. | Current normative manuscript; `model.tex:143-144` still contains editorial gap G-001. |
| Historical architecture program | `Prism/`, `PrismV2/`, `HRA/`, `RViT_plus/`, and `research_db/threads/rvit_plus_engineering.md` | PRISM, HRA, and early RViT+ design/failure history. The engineering thread contains valuable run-level lessons but stops in May 2026 and references obsolete canonical paths. | Historical evidence and design rationale. |
| Current executable empirical line | `RViT_plus_paper_jepa_grid9/` | Current task registry, model, training, VDA set-size analysis, and causal clamp harness. | Primary producer code for the latest manuscript. |
| Current run artifacts | `battery_sweep_results/` | Checkpoints and 43 metrics files spanning VDA, Validity4, Luo–Maunsell, Baruni, Krauzlis, motion, width, reward-scale, and memory-noise variants. | Primary run evidence, but lacks a manifest and consistent provenance. |
| Current empirical manuscript | `reports/upgraded_paper/manuscript/` and `EVIDENCE_LEDGER.md` | Paper A, the empirical companion to the normative paper; reports one `affine_ew` model rather than an architecture comparison. | Most current empirical prose, but not submission-final and stale in several places. |

The empirical MAH baseline uses a seven-step, 50×50-image cued orientation-change task, patch-preserving recurrent memory and attention, and sparse-reward actor–critic learning. Its supplement broadens the baseline with SDT decomposition, psychometric checks, TD/value and uncertainty analyses, decoding, implementation details, and alternative-model tests. The separate normative paper asks when criterion adjustment versus sensitivity reallocation should be used under benefit/cost asymmetry. Its corrected Reconstruction is the appropriate source for normative claims; applying those regimes to RViT+ still requires measured sensitivity, value representation, and causal interventions rather than name-level analogy.

## 2. Experimental program and findings

### 2.1 Historical architecture experiments

The early PRISM/HRA/RViT+ program is best understood as a sequence of mechanism-discovery experiments rather than as a single convergent model series. PRISM v1 established that prediction-error-driven memory can solve change detection without requiring interpretable softmax attention. PRISM v2 introduced hierarchical predictive coding and slow/fast memory but did not match v1. HRA exposed two concrete failures: unstable reinforcement-learning gradients and frozen deep states, followed by uniformly distributed Feedback-Transformer attention. Early RViT+ video-compression runs then isolated objective and architecture failures, including trivial mean/median reconstruction, vector-latent destruction of spatial memory, a broken content mask, decoder collapse, and the need for spatial latent states and mirrored recurrent decoding. These lessons are recorded in `research_db/threads/rvit_plus_engineering.md`, but the thread is historical rather than current; its header still says the canonical state is May 2026.

The current paper-oriented line simplifies that broader architecture into an executable recurrent detector with two routing variants: `affine_ew`, used as “the model” in the manuscript, and `crossattn1`, usually retained as an architectural comparison. The current claim surface should therefore be separated into model findings, routing comparisons, and broader architectural-program hypotheses.

### 2.2 Current battery training inventory

The 43 metrics files divide into the following families:

| Family | Artifact status | Training-level finding |
|---|---|---|
| Canonical VDA1/2/4/9, `d_mem=128`, both routings | 8 runs with 20,000 logged rows | Canonical affine final rolling-correct values are 0.800, 0.818, 0.873, and 0.808; VDA2 uses the `_2x2` checkpoint. These are completed logged phases, not proof of convergence. |
| VDA1/2/4/9, `d_mem=256`, both routings | 8 budget-complete runs | Affine remains successful across all four sizes. Cross-attention VDA9 is unstable at the end despite earlier successful learning. Width alone is not a monotone improvement. |
| VDA9 reward-scale × width variants | 8 budget-complete runs | The reward×10 condition is highly sensitive to routing and width. Only `crossattn1,d256` remains strongly successful late; the other reward×10 variants are weak or collapsed. Reward scaling is not a benign rescaling. |
| VDA2 2×2-grid replicas and exclusion | 4 budget-complete runs | Both routings learn the matched-grid VDA2 and exclusion tasks. These runs are useful controls for geometry and cue exclusion. |
| Validity4 | 2 budget-complete runs | Both routings learn, supporting graded validity analyses in the no-value-cue condition. |
| Luo–Maunsell sensitivity/criterion | 4 budget-complete runs | All four task/routing combinations train, but the published comparison is preliminary because the current manuscript uses cued, separately trained models rather than the faithful no-cue shared-base design. |
| Baruni baseline | 2 budget-complete runs | Both routings learn the task. Subsequent behavioral analysis reports an absolute-value/principled-null regime. |
| Baruni memory noise | 2 partial runs | `crossattn1` remains strong at σ=0.5 and σ=1.0 through roughly 19k iterations. Reproduction source/flags are missing from the canonical code tree. |
| Krauzlis | 2 budget-complete runs | Both collapse to an always-wait policy. This is an optimization/curriculum failure, not evidence against the selection mechanism. |
| Motion Zénon–Krauzlis | 2 partial runs | Both reach roughly 0.74–0.77 late rolling correctness at the starting difficulty but stop around 6.3k iterations; no behavioral mechanism analysis is preserved. |
| VDA16 | 4 interrupted runs | Checkpoint iteration 599; near-chance behavior; no scientific convergence verdict is possible. |
| Local MPS VDA16 | 1 very short run | Stops at iteration 86; smoke-level evidence only. |

The companion CSV provides path-level values for the 43 central battery rows. A 44th workspace metrics file exists under `RViT_plus_paper_jepa_conv/battery_sweep_results/`. “Budget complete” means the CSV contains 20,000 rows ending at iteration 19,999. It does not establish convergence, cumulative lifetime updates, replication, or confirmatory analysis; resume logic resets the iteration counter and overwrites `metrics.csv`.

### 2.3 VDA1/2/4/9 behavioral and mechanistic result

The saved NPZ files in `RViT_plus_paper_jepa_grid9/vda_sweep/figs/` were regenerated on 2026-07-07 from the `battery_sweep_results/pod2/ckpt2` checkpoints. For affine d128, mean cued thresholds are approximately 9.794°, 12.175°, 12.094°, and 12.138° for VDA1/2/4/9. The low-to-high displayed-validity threshold improvements are 0.148°, 0.193°, 0.979°, and 2.207°, increasing across this ladder. Clamp-induced sensitivity ranges move in the opposite direction—1.982, 1.647, 1.131, and 0.367—while criterion ranges are 1.020, 1.381, 1.622, and 1.048. The battery therefore contains multiple load-dependent signatures, not one scalar capacity curve.

The causal clamp remains the most defensible mechanistic result: suppressing cued-location attention degrades sensitivity and generally drives a conservative criterion, whereas enhancement pushes criterion liberal. The exact curves are not uniformly monotone—VDA9 criterion reverses at the high end—so manuscript descriptions should report curves or endpoint/range definitions explicitly. Value/colour remains perfectly decodable from cue onset through the final frame. Validity decoding is weakly maintained for VDA1/2/4 but strongly maintained at VDA9 (mean post-cue balanced accuracy approximately 0.247, 0.350, 0.309, and 0.701). That supports a high-load retention result, not retention in VDA4.

Several design confounds bound the set-size interpretation:

1. The canonical VDA2 analysis selects the separately trained `_2x2` run. VDA1/2/4 use four-token 2×2 models with different inactive-cell support, while VDA9 changes active count, token/readout dimensions, grid size, image size, and its training support includes an additional p=0 condition. The ladder is not a pure memory-load manipulation and is not literally an identical model/reward/curriculum comparison.
2. Displayed cue-validity semantics are inconsistent. `VDASetSizeEnv` forces an invalid trial to a different active item, while the base VDA environment samples the change location uniformly in the invalid branch, allowing it to land back on the cue. Equal displayed proportions do not imply equal realized cue validity across set sizes.
3. The current results are one checkpoint per condition. Analysis generation is unseeded, saved trial-level data and confidence intervals are absent, and evaluation batches do not estimate between-training-run uncertainty.
4. `vda_core.py` was extended beyond its original 1/2/4 scope, but `_loc_keys` still uses the global `NP=4`. High-set-size cross-attention clamps therefore target only the image key rather than the image and corresponding memory key. This does not invalidate the manuscript’s affine-only clamp figures, but it compromises high-set-size `crossattn1` comparisons.
5. The analysis hard-codes absolute workspace paths and source/checkpoint identities rather than consuming a run manifest.

### 2.4 Other current empirical findings

The Validity4 result is positive within its separately trained checkpoint: when cue validity is the only cue, cueing benefit, withdrawal from uncued locations, and cue-location attention scale with displayed validity. Current prose incorrectly calls this “the same trained model in another environment.” In the value-plus-validity sweep, VDA1/2/4 show weak post-cue validity maintenance while VDA9 maintains validity strongly. This is a cross-checkpoint load association, not yet a replicated causal demonstration that load makes reliability worth storing.

The Baruni analysis is a principled null in the baseline models: no robust relative-value allocation appears, consistent with an absolute-value/high-sensitivity regime. The newer memory-noise runs show training robustness but have not been passed through the behavioral/value battery. They therefore cannot yet be used to strengthen the normative claim.

The Luo–Maunsell result is promising but preliminary. The cued sensitivity model shows a larger Δd′ with low false alarms, while the criterion model raises false alarms with a smaller Δd′ change. However, `results_luomaunsell.tex:10-20` correctly notes that these are two separately trained cued models, not a cue-free, shared-base double dissociation matching the animal paradigm. The faithful environment exists in code, but the manuscript’s replacement analysis is not yet present.

The Krauzlis task is a training failure. Both models learn that waiting earns a high baseline and never explore declaring. The motion variant appears to partially escape this basin but is incomplete and unanalyzed. Neither family currently supports a manuscript-level superior-colliculus mechanism claim.

The capacity section is stale. Preserved `d_mem=128` and `256` checkpoints now exist for VDA1/2/4/9. Training performance does not show a simple capacity benefit: affine succeeds at both widths, while VDA9 cross-attention at 256 dimensions is unstable late. A matched psychometric, SDT, decoding, and clamp battery is still required before interpreting width as working-memory capacity.

The rehearsal claim is not complete. Attention remains elevated at the cued location during a blank frame, which is compatible with rehearsal. `DelayProbeEnv` is implemented, but no checkpoint, probe enhancement, or causal delay-clamp result was found. Sustained attention is therefore an observation; load-bearing rehearsal remains a hypothesis.

## 3. Current research direction

The empirically supported current direction is to convert the broad attention story into a boundary map: which attentional signatures survive increasing competition, routing changes, memory width, reward scaling, and state perturbation. The VDA ladder, width/reward variants, and Baruni memory-noise runs all point in this direction. Displayed-validity threshold benefit increases with the current set-size ladder, but clamp sensitivity, criterion, and sustained attention do not share one monotone profile. The project should resist turning those heterogeneous signatures into a single capacity narrative.

The next scientifically decisive direction is a controlled scaling design rather than simply resuming every unfinished run. A valid test would hold the visual field, token count, cue-validity semantics, reward scale, training budget, and analysis protocol fixed while varying active set size; then replicate each condition across training seeds. Only after that should VDA16 be used as the terminal point of a capacity curve. VDA16 can still be resumed as an engineering completion, but it will not by itself remove the 4→9 geometry confound.

The second priority is robustness and mechanism generalization. The memory-noise result should be made reproducible and evaluated with the same Baruni and state-decoding battery. The width comparison should use matched run IDs and held-out analyses. The faithful Luo–Maunsell shared-base protocol and delay-probe rehearsal test should come next because they close explicit manuscript promises. Motion/Krauzlis should remain secondary until the curriculum produces a stable, analyzable policy.

## 4. Evidence quality and manuscript corrections

| Issue | Consequence | Required correction |
|---|---|---|
| VDA16 described as exhausting its budget | Converts an interrupted run into a scientific failure | Replace with “interrupted at checkpoint 599; near chance; incomplete.” |
| Capacity section says d256 run was not preserved | Ignores current checkpoints and metrics | Update status; do not claim a behavioral capacity effect until battery analysis exists. |
| Discussion says monotone ladder is pending while results section reports 1/2/4/9 | Semantic staleness | Reconcile discussion and appendix with the current sweep. |
| “Trained to convergence” inferred from iter 19,999 | No convergence rule exists; resumes reset counters and overwrite metrics | Say “20,000-row logged phase with final checkpoint”; recover cumulative provenance where possible. |
| “Same model/reward/curriculum” wording across set sizes | Hides separate parameters plus differences in token/readout geometry and training support | Name each checkpoint and tabulate the matched and unmatched design dimensions. |
| Single-run checkpoints | Trial-level evaluation cannot establish training robustness | Add training seeds before publication-grade scaling claims. |
| Inconsistent validity generators and 4→9 geometry change | Confounds set-size effect | Introduce a fixed-grid controlled set-size environment and report realized validity. |
| Cross-attention high-K clamp indexing | Alternative-routing causal comparison is incomplete | Replace global `NP` with runtime token count and add tests for K=9/16. |
| Validity4 called the same trained model | The analysis loads a separately trained checkpoint | Correct model identity and attach every claim to its run ID. |
| Unseeded analyses and degenerate VDA2/VDA9 change-location labels | Prevent reproducible uncertainty and invalidate those location-decoding outputs | Seed and save trials; repair the decoding collector before interpreting change location. |
| Memory-noise artifacts lack producer source | Result cannot be reproduced from repository | Recover exact source/flags or mark the finding artifact-only. |
| Root is not a Git repository and checkpoints have sparse provenance | Commit-based reproduction is impossible | Record source-tree hash, config, environment, seed, command, and checkpoint hash in manifests. |

## 5. `research_db` audit

The database is structurally healthy. `tools/audit.py` reports 265 paper files, 16 concepts, six threads, 261 full-depth entries, four abstract-depth entries, and zero issues. The exported graph has 290 nodes and 2,873 edges. These are strong literature-library numbers.

Its semantic role is narrower than its conventions claim. The filesystem contains only `_conventions/`, `papers/`, `concepts/`, `threads/`, `tools/`, and `graph/`; there are no substantive `notes/`, `briefs/`, `conversations/`, `mocs/`, or operational pages. The graph has only three synthetic work nodes (`recurrent_vit`, `prism_v1`, `prism_v2`). Exact searches find no VDA1/2/4/9/16, `battery_sweep_results`, `affine_ew`, or `crossattn1` linkage. The RViT+ engineering thread is useful history but stale and over 100 KB.

The “zero issues” result validates the legacy schema, not the newer wiki contract. `audit.py` still enforces `status: stub|summary|full`, `last_updated`, and legacy lists, while `_conventions/FRONTMATTER.md` requires page `type`, lifecycle status, `created`, structured `see_also`, and TL;DR sections. None of the 265 papers has `type: paper` or `created`; graph construction likewise consumes legacy fields and hardcodes synthetic works. `README.md`, `HANDOFF.md`, and `INDEX.md` also contain materially stale counts and graph status.

The database should be extended, not replaced. Its stable paper IDs, taxonomy, graph builder, and reproducible-findings convention are useful. The missing layer is the project’s own evidence graph: project MOCs, experiments, runs, findings, claims, artifacts, and supersession relations.

## 6. Safe organization model

No active tree should be moved or deleted yet. The first organization pass should be additive and reversible:

1. Create a root artifact registry that assigns stable IDs and roles to source papers, manuscript trees, producer-code trees, experiments, runs, checkpoints, analyses, and derived figures.
2. Define one canonical producer for the current empirical paper (`RViT_plus_paper_jepa_grid9`) and label other executable trees as predecessor, experimental fork, or archive candidate without relocating them.
3. Give every run a manifest containing task, environment version, routing, dimensions, reward, curriculum, seed, command, source hash, checkpoint hash, completion reason, and expected analyses.
4. Give every manuscript claim a run/artifact pointer. Keep `EVIDENCE_LEDGER.md`, but make its identifiers resolve through the registry rather than raw paths.
5. Add real project `mocs/`, experiment/finding `notes/`, and `briefs/` rather than a parallel `works/` ontology. The first MOC should distinguish empirical MAH/Recurrent ViT, RViT+, the upgraded empirical paper, the original normative paper, and its Critique/Rebuild/Reconstruction lineage.
6. Split the RViT+ engineering monolith into dated run findings only after stable IDs and redirects exist.
7. Re-run graph build and audit, then add semantic checks: every active manuscript claim resolves to an artifact; every budget-complete run has a manifest; every stable finding has method, evidence, reproduction, and caveats.
8. Only after dependency discovery should duplicate/generated trees be proposed for archival relocation. Preserve compatibility links or redirect pages for every renamed ID.

## 7. Prioritized next steps

1. **Freeze claim semantics before more prose.** Correct empirical-versus-normative MAH lineage, VDA16, convergence, set-size comparability, capacity, discussion, appendix, and separately trained Validity4 wording. Do not add a pure capacity claim.
2. **Create run identities and provenance.** Start with the 43 central battery metrics rows, the additional convolutional metrics file, and all checkpoints used by `vda_sweep`. Hash the producer source because the root is not under Git.
3. **Repair and rerun the decoding battery.** Seed and save trial generation; include valid uncued changes for VDA2/VDA9; separate checkpoint-specific validity retention from degenerate change-location decoding.
4. **Fix and test the high-K cross-attention clamp.** Add runtime token-count indexing and tests for image+memory keys at 9 and 16 tokens.
5. **Design the controlled set-size replication.** Fixed grid/token count, identical realized-validity semantics, matched budget, at least multiple training seeds, preregistered analysis.
6. **Resume VDA16 only as an explicitly incomplete engineering run.** Preserve the old interrupted run ID and create a new resumed-run ID; do not overwrite.
7. **Run the matched d128/d256 behavioral battery.** Treat width as a model intervention only after held-out psychometric and invalid-cue analyses.
8. **Recover memory-noise source and analyze it.** If source cannot be recovered, keep the result labeled artifact-only.
9. **Complete the promised targeted experiments.** Faithful Luo–Maunsell shared-base/no-cue comparison, then delay-probe and delay-clamp rehearsal. Keep motion/Krauzlis behind a curriculum gate.
10. **Integrate current evidence into `research_db`.** Add real project MOCs, experiment/finding notes, briefs, and typed artifact links while supporting both legacy and new schemas during migration.

## Bottom line

The project has advanced beyond a single four-stimulus demonstration. It now has a credible causal attention battery across four trained set sizes and several robustness/intervention probes. Its main scientific risk is no longer absence of results; it is identity and comparability debt. Different checkpoints, task semantics, grids, forks, and manuscript generations are being discussed as if they were one continuous model. The next phase should make those identities explicit, replicate the core effects under controlled scaling, and use the wiki as the evidence-routing layer before any destructive reorganization.
