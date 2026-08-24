# Luo–Maunsell reproduction check: d_mem=128 dual-stream sensitivity pair (partial runs)

**Date:** 2026-08-18
**Status:** complete; verdict is a split result (sensitivity reproduced, specificity not)

## What this is

Two RunPod training runs of the `fresh_dualstream_dmem128_grid2_memnoise0075_gamma100_bc000_curriculum_sensitivity_runpod`
design were terminated early for cost. Their checkpoints were rescued and re-measured with
the repository's frozen-policy SDT assay to answer: *did these runs reproduce the
Luo & Maunsell (2015) sensitivity/criterion dissociation?*

## Verdict

| Target | Outcome |
|---|---|
| Positive counterphased Δd′ DiD | **reproduced** (+0.23 to +0.32, CI excludes zero at θ = 38°, 47°, 50°) |
| Sign-correct counterphasing, both lineages | **reproduced** |
| Symmetric counterphase | partial (Δd′ = +0.433 loc0 vs +0.053 loc3) |
| Criterion cross-effect inside \|Δc\| ≤ 0.2 | **not reproduced** (Δc_DiD ≈ +0.23, CI upper limit 0.276–0.291) |
| Strict behavioural dissociation | **not achieved** |
| LM *double* dissociation | not testable (criterion lineage unsupported in this design) |

**Key finding:** the criterion shift matches the *reward-optimal* criterion implied by the
task's own hit:correct-rejection ratios (0.7 high / 1.1 low) to within 0.03. Since
Δln β\* = 0.452 and c\* = ln β\*/d′, the ±0.2 target requires d′ ≥ 2.26 at both locations;
these policies achieve d′ = 1.67–2.10. The specificity test is therefore **unpassable as
designed** — the reward table must be criterion-titrated. Doubling d_mem did improve
criterion *calibration*: the d_mem=64 parent overshot the reward optimum by 2.1×, this
pair brackets it.

## Checkpoint status (important)

Both checkpoints are **partial** — the 20,000-iteration contract was not met, so the
repository's terminal validators (`iter == 19999`) were bypassed. Everything else in the
measurement contract was preserved.

| | loc 0 | loc 3 |
|---|---|---|
| Rescued iteration | 18,799 | 15,849 |
| Fraction of contract | 94% | 79% |
| Terminal θ | 47° | 38° |

The loc-0 run reached iteration ~19,516 before termination; the checkpoint written at
19,499 was not captured and no longer exists.

## Contents

- `report/main.tex`, `report/main.pdf` — the writeup (8 pages, 4 figures, 4 tables)
- `report/figs/` — figure PDFs
- `results/partial_sdt_results.json` — full assay output, both policies, all branches
- `results/analysis_summary.json` — derived quantities used in the writeup
- `code/run_partial_sdt.py` — the assay driver
- `code/analyze_and_plot.py` — analysis and figure generation

## Reproducing

The assay imports model and environment code from the **rescued pod source tree**, not the
working copy: `model.py`, `paper_encoder.py`, `ppo.py` and `train_rl.py` in the repo have
been modified since launch, while `envs/luo2015.py`, `envs/base.py` and
`luo2015_analysis/luo2015_core.py` are byte-identical to what was deployed.

```
cd C:\Users\jomor\runpod_rescue\20260817\eval_tree
python run_partial_sdt.py --trials 2000 --bootstrap-draws 5000 --common-thetas 38 47 50
```

Checkpoints were written under NumPy 2; loading them under NumPy 1 needs the
`numpy._core` module alias, which the driver installs.
