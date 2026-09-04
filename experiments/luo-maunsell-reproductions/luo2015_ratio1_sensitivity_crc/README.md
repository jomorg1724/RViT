# Ratio-1 Luo–Maunsell sensitivity sweep (CRC)

Five seeds per counterphase lineage, trained with **H:CR = 1 at both locations** and
measured in the same job. Ten runs, `l40s`, ~2.2–2.6 h each.

## Why this table

Luo & Maunsell *titrated* the hit:correct-rejection reward ratio per location, during each
session, until the animal's criterion was unbiased there. The published 0.7 and 1.1 are the
averaged **outputs** of that procedure, not settings they started from. The August runs used
them as fixed constants, which is not the same experiment.

With change and no-change trials equally likely and no penalty for misses or false alarms,
the reward-optimal criterion at a location is

```
beta* = R_CR / R_hit          c* = ln beta* / d'
```

so unequal ratios across locations *force* a criterion difference. For 0.7 / 1.1,
Δ ln β\* = 0.452, predicting Δc\* of +0.20 to +0.25 across the d′ range those policies
reached — against an observed Δc of +0.23. The August criterion shift was not a failure to
hold criterion constant; it was the reward table being paid for exactly that shift. Reaching
the |Δc| ≤ 0.2 specificity target with that table would have needed d′ ≥ 2.26 at *both*
locations, and those policies ran 1.67–2.10. The test was arithmetically unpassable as
designed.

Setting the ratio to 1 at both locations makes ln β\* = 0 at both, so the reward-optimal
criterion is **zero at both locations for any pair of d′ values** and Δc\* = 0 exactly. A
criterion difference is no longer something the reward table pays for.

| Location | hit | CR | H:CR | mean |
|---|---|---|---|---|
| high-value | 5.0 | 5.0 | 1.0 | 5.0 |
| low-value | 1.0 | 1.0 | 1.0 | 1.0 |

Miss = FA = 0, unchanged. The 5:1 value manipulation is preserved intact, carried entirely
by the mean. `--reward-scale 0.3333…` is unchanged from August; it multiplies hit and CR
alike and so cannot affect β\*.

**A residual Δc is still expected.** Zero *reward-optimal* criterion difference does not mean
zero *measured* criterion difference — the agent may carry an intrinsic bias, exactly as the
monkeys did. Measuring that residual is a result in its own right, and it is what the
titration variant is for.

## Design

- **5 seeds per lineage** (42–46), both counterphase lineages, 10 runs. The August
  difference-in-differences had one model per lineage, so its interval was over trials with
  no between-model error term, and the counterphase was badly asymmetric
  (Δd′ = +0.433 at loc 0 against +0.053 at loc 3). Five seeds buy a real error term.
- **Everything else identical to August** — dual actor/critic streams, `d_mem=128`,
  crossattn1 + xLSTM, JEPA 0.5 per branch, γ=1.0, mnemonic noise 0.075, sensory noise 5°,
  curriculum 65°→8°, 20,000 iterations, 8 episodes/iter. Only the ratios and the seed move.
- **Dense θ grid** at measurement: 12–56° in ten steps, retaining 38/47/50 so the numbers
  stay directly comparable to the August report. Three θ values exactly saturate the
  equal-variance SDT model and leave no residual degrees of freedom to estimate the variance
  ratio from; ten is enough to fit d′(θ) later. It costs nothing extra — same rollouts, more
  conditions.
- Primary endpoint: counterphased Δd′ between locations. Specificity check: |Δc| ≤ 0.2.

## Files

| file | |
|---|---|
| `train_and_measure.slurm` | one array task = train one policy **and** measure it |
| `run_ratio1_sdt.py` | frozen-policy SDT assay for a single checkpoint, dense θ |
| `assemble_eval_tree.sh` | rebuilds the flat source layout the assay expects |
| `analyze_did.py` | cross-run counterphased DiD; CPU-only, runs after the sweep |

## Running it

```bash
# once, on CRC
bash assemble_eval_tree.sh <repo-src> /ix/jpherman/hermanj/rvit_ratio1/tree
cp train_and_measure.slurm analyze_did.py /ix/jpherman/hermanj/rvit_ratio1/tree/

cd /ix/jpherman/hermanj/rvit_ratio1/tree
sbatch -M gpu --array=0-9 train_and_measure.slurm

# after all ten finish
python analyze_did.py --results /ix/jpherman/hermanj/rvit_ratio1/results \
                      --output  /ix/jpherman/hermanj/rvit_ratio1/results/did.json
```

Array tasks 0–4 are `high_loc=0`, tasks 5–9 are `high_loc=3`; seeds 42–46 in each.
Re-running the array is idempotent: a task whose final checkpoint already exists skips
training and re-runs only the assay.

## Three things that will bite

1. **Never run from the repo root.** `code/` is a package with an `__init__.py`, so it
   shadows Python's stdlib `code` module — which `pdb` imports — giving a confusing
   circular-import crash. `cd` into the eval tree first.
2. **CRLF.** A Windows clone (`core.autocrlf=true`) gives every text file CRLF, which breaks
   `set -o pipefail` in shell scripts and changes every provenance hash. `git archive` does
   *not* save you — it applies the same conversion on export. Strip CRs after upload.
3. **The assay's flat layout.** `luo2015_analysis` and `experiments/luo2015_episodic` locate
   the repo by walking up a fixed number of parents and import `envs` / `model` as top-level
   modules. The 2026-08-23 consolidation split them apart, so the assay does not run against
   the repo as laid out. `assemble_eval_tree.sh` rebuilds the layout rather than patching the
   path arithmetic, which keeps the measurement code byte-identical to what produced the
   August numbers.

## Not this experiment

The per-location **titration** variant — adjusting H:CR until the *measured* criterion is
unbiased — is the faithful reproduction of what L&M did, and is separate work. Two notes for
whoever builds it:

- The `high_hit_cr_ratio` / `low_hit_cr_ratio` parameters added for this experiment are the
  handle a titration controller needs; `set_condition()` recomputes the table from them.
- **Flush the replay buffer at each titration step.** `EpisodeReplayBuffer` in `ppo.py` is a
  FIFO ring that persists for the whole run and stores `rewards` as precomputed tensors
  reused verbatim on replay, so after a reward change the critic trains on a mixture of two
  reward functions until the buffer turns over — 125 iterations at the effective capacity of
  1000 (set in `config/default.json`, which overrides the dataclass default of 200) and 8
  fresh episodes per iteration. There is no flush method, but `build_training_checkpoint`
  deliberately excludes replay, so a stop/resume already gives a clean buffer.
