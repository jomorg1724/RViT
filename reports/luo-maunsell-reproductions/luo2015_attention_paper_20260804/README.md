# Luo/Maunsell phase-resolved attention paper (2026-08-04)

Short research paper re-expressing the archived Luo & Maunsell change-detection attention
arrays in the VDA-series common-quadrant display convention, resolved by frame and by
environment condition.

## Contents

| Path | What it is |
|---|---|
| `luo2015_attention_paper_20260804.pdf` | The compiled paper (8 pages) |
| `paper/main.tex` | Source; compiles with `pdflatex` (TeX Live 2022) |
| `figures/attention_time_condition_visual.{pdf,png}` | Fig. 3 — visual-key quadrant maps, 4 conditions x 7 frames |
| `figures/attention_time_condition_memory.{pdf,png}` | Fig. 4 — recurrent-memory-key quadrant maps, same layout |
| `figures/attention_timecourse_conditions.{pdf,png}` | Fig. 5 — incoming mass, source share, tested-query routing over time |
| `figures/behaviour_curves.{pdf,png}` | Fig. 2 — psychometric / SDT / chronometric |
| `figures/task_trial_montage.{pdf,png}` | Fig. 1 — copied from the 2026-08-03 assay |
| `figure_statistics.json` | Every number quoted in the paper, per condition and frame |

## Provenance

Producer: `analysis/make_luo2015_vda_style_attention_figs.py`. It is a pure re-plotting
step — it reruns no checkpoint and trains nothing. Input is the frozen
`data/fixed_condition_attention.npz` cache from
`reports/luo2015_scientific_assay_20260803_production`, itself derived from the frozen
checkpoint snapshot in `reports/luo2015_attention_snapshot_20260802_production`
(iteration 12,899, SHA-256 `2c4a6d2d21bd9698387f7a4b27cbc242c7f3bb097868518deb7790ae1c8b339f`,
`memory_noise_std = 0.64`).

Rebuild the figures with:

```bash
python analysis/make_luo2015_vda_style_attention_figs.py --output-root reports/luo2015_attention_paper_20260804
```

## Validity

**The upstream checkpoint lineage is marked `INVALID_TASK_CONTRACT`.** It was trained under
the pre-fix orientation generator (fixed session base orientations, curriculum-coupled)
rather than the enforced `independent_uniform_axial_0_180` contract. No behavioural, d',
criterion, psychometric, lesion, or Luo-replication claim from it is admissible, and the
producer script for the snapshot now refuses that checkpoint outright. Section 5 of the
paper states this and scopes every claim accordingly. What transfers to a corrected retrain
is the measurement and display methodology, not the numbers.
