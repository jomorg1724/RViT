# OngoingRViTExperiments — Reorganization Manifest

**Created:** 2026-08-20
**Location:** `G:\Other computers\My Mac\AttentionManuscript\OngoingRViTExperiments\`
**Purpose:** Consolidate this PC's recent VDA set-size and Luo–Maunsell experiment work into three themed categories.

## Structure

```
OngoingRViTExperiments/
├── VDASetSizeAndMemory/                  # VDA4/VDA9/VDA16 set-size & attention runs + reports
│   ├── runs/         (126 files)  # vda4_crossattn1_*, vda4_affine_*, vda16_*, vda_fixed9_*, stream_factorial
│   ├── experiments/  (33 files)   # vda16_replication, vda_fixed9_controlled, vda_recommended_endpoints, vda_stream_factorial designs
│   └── reports/      (1982 files) # repo reports\vda_series (set-size reports) + vda_series_manuscript (workspace-root manuscript tree)
├── LuoMaunsellReproductions/
│   ├── runs/         (3561 files) # luo2015_grid20x20_* runs, runpod_exports, deployments, canaries, analyses, source tars
│   ├── experiments/  (74 files)   # luo2015_episodic designs (fresh_grid2, dualstream, gamma ladder, reward matrix)
│   ├── reports/      (136 files)  # luo2015_* report dirs (attention paper, scientific assay, dmem128 partial, ...)
│   ├── rescues/      (333 files)  # runpod_rescue\20260817 (loc0, loc3, eval_tree, report, rescue tars)
│   └── analysis/     (3 files)    # luo2015_analysis (luo2015_core.py)
└── RethinkingMemoryStabilityAndPercepts/
    ├── runs/         (348 files)  # vda4_transformer_memory_*, vda4_memory_noise_*, vda4_modern_* (JEPA), teacherac_ste, FSQ runs
    ├── experiments/  (59 files)   # vda4_memory_noise, vda4_spatial_discretization, vda4_transformer_memory designs
    ├── reports/      (79 files)   # memory-noise psychometric/comparison reports, synthesis_signal_coherence, lab notebook, literature briefs
    └── rescues/      (36 files)   # vda_synth
```

## Sources moved (from this PC)

| Source | Destination |
|---|---|
| `C:\Users\jomor\Documents\RViT_runs\*` (all run dirs + buckets) | split into the three categories' `runs\` |
| `C:\Users\jomor\runpod_rescue\20260817\` | `LuoMaunsellReproductions\rescues\` + `RethinkingMemoryStabilityAndPercepts\rescues\vda_synth` |
| `RViT_plus_paper_jepa_grid9\experiments\*` (design dirs) | categories' `experiments\` |
| `RViT_plus_paper_jepa_grid9\reports\*` (luo2015_* + vda_series) | `LuoMaunsellReproductions\reports\` + split `vda_series` reports |
| `RViT_plus_paper_jepa_grid9\luo2015_analysis\` | `LuoMaunsellReproductions\analysis\` |
| `...\reports\vda_series\` (workspace-root manuscript tree) | `VDASetSizeAndMemory\reports\vda_series_manuscript\` |
| `...\$dir\` (lab notebook) | `RethinkingMemoryStabilityAndPercepts\reports\lab_notebook\` |
| literature briefs (copies) | `RethinkingMemoryStabilityAndPercepts\reports\vda_series\` |

## Deliberately left in place

- **Active FSQ training run**: `C:\Users\jomor\Documents\RViT_runs\vda4_fsq2_c1_a01_j0001_lr2e4_s0_v1_prod_resume_20260819\` (training still running; will be moved after it completes).
- **Shared codebase** in the repo: `model.py`, `train_rl.py`, `ppo.py`, `envs/`, `tests/`, `scripts/`, `config/`, `analysis/` (analysis pipelines used by all categories), `vda_series/` (figure code), `runs/`, `vda_sweep/`, `deepdive9/`, etc.

## Notes / caveats

- Moved via `Move-Item` + `robocopy` merges because the Google Drive File Stream mount does not delete directory skeletons atomically and the local cache can report stale entries (ghost listings). All large content was verified at destination (byte/size checks) before sources were deleted.
- The `AttentionManuscript` root also contains `archive/` (deprecated Mac-era work, per earlier request) and `research_db/` + design docs (the wiki), which were untouched.
- Move logs: `move_log_cat1.txt`, `move_log_cat2.txt`, `move_log_cat3.txt`, `fixup_log.txt`, `fixup2_log.txt`, `final_verify_log.txt`, `definitive_log.txt` (in this folder).
