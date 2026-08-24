# PRISM — Project Plan & Experimental Roadmap

**Target venues:** NeurIPS (main track or D&B) and PNAS.
**Status (as of last edit):** Training has crossed chance for the first time. Move into systematic characterization.
**Living document.** Updated by humans and by scheduled Claude cowork instances. See "How to use this document" below.

---

## 0. How to use this document

This is the living master plan. A scheduled Claude cowork run (hourly or daily) should read this from top to bottom every time before doing anything else. The order of operations for any cowork session is:

1. Read the **Current State** block immediately below.
2. Read the **Standing Analyses** section (Section 4) to see what should run on every check-in regardless of phase.
3. Look at the **Active Phase** (Section 5) and identify the lowest-numbered task whose status is `[ ]` (todo) and whose dependencies are all `[x]` (done).
4. Execute that task. Limit a single hourly run to at most one task; a daily run can chain.
5. Update the task's status, append to the **Progress Log** (Section 9), and commit the document.
6. If a task surfaces a new finding that changes what we should do next, add it to the **Decision Log** (Section 8) before exiting.

**Status codes used throughout:**

- `[ ]` todo, dependencies satisfied
- `[~]` in progress (include the iteration / commit / date with this marker)
- `[x]` complete (include path to the output artifact)
- `[!]` blocked (include reason)
- `[?]` needs human decision before proceeding

**Naming convention for task IDs:** `P{phase}.{task}.{subtask}`. E.g., `P2.3.b` is Phase 2, Task 3, subtask b. Cite these IDs in commits, in figure captions, and in the manuscript Methods.

**File layout for outputs:**

- Trained checkpoints: `Prism/checkpoints/{run_name}/`
- Analysis scripts: `Prism/analysis/{phase}_{topic}.py`
- Figures: `Prism/figures/{phase}_{task}_{descriptor}.pdf` and `.png`
- Tables: `Prism/tables/{phase}_{task}.csv`
- Per-task analysis notebooks (optional, for exploration): `Prism/notebooks/{phase}_{task}.ipynb`
- Per-experiment configs: `Prism/config/{exp_name}.json`
- Per-experiment training logs: `Prism/logs/{run_name}.jsonl`

---

## 1. Current State

**Last updated:** 2026-04-30 (initial draft).

**Headline:** First training run has finally surpassed the never-press baseline (return > 1.47). Architecture v0 is `Prism/` at HEAD with the autoencoding PC term, actor-bias init, error-gated GRU, two-decoder PC, K=2 inner loop. Now we lock the architecture and proceed to systematic characterization.

**Architecture freeze:** Code in `Prism/{stem,film,decoder,memory,readout,losses,model,ppo,train}.py` and `Prism/config/prism_config.json` is the canonical "PRISM v1" referenced by all subsequent analyses. Any architecture change forks a new version (`PRISM v2`, etc.) and is logged in the Decision Log.

**Currently running:** [fill in: which run name, started when, ETA, target metric]

**Next milestone:** Phase 1 multi-seed training (P1.1) and the first full psychometric battery (P2.1).

---

## 2. Terminology and notation (canonical)

These definitions are used everywhere in this document, in the manuscript, and in code/analysis variable names.

**Stimulus locations (always indexed by quadrant):**

- `S_1` — top-left quadrant of the 50×50 display (pixel rows 0–24, cols 0–24)
- `S_2` — bottom-left quadrant (rows 25–49, cols 0–24)
- `S_3` — top-right quadrant (rows 0–24, cols 25–49)
- `S_4` — bottom-right quadrant (rows 25–49, cols 25–49)

The env code currently uses `cue_position ∈ {'left', 'right'}` mapped to `{S_1, S_4}`. Throughout this plan and the manuscript, refer to cue/change locations exclusively by `S_i`.

**Cueing:**

- `Cue S_i` — a cue stimulus was presented at location $S_i$ at trial step $t = 1$. Only `Cue S_1` and `Cue S_4` exist in the current env; trials may be classified by which.
- `Validity` $p \in \{1.0, 0.75, 0.5, 0.25\}$ — the visible proportion of the cue's annular ring. Equals the conditional probability that the change, if present, occurs at the cued location: $P(\text{change at } S_i \mid \text{Cue } S_i, \text{change present}) = p$.
- `Cue RM` (Reward Magnitude) — a categorical label encoded in the cue's color. `Red → ρ = 5`, `Green → ρ = 3`, `Blue → ρ = 1`. The agent receives reward $\rho$ on a correct hit or correct rejection at the trial's color.

**Change events:**

- `Change S_j` — a change, if present, occurs at location $S_j$. Used in conjunction with cue notation: `Cue S_1, Change S_1` is a *valid* trial (change at cued location); `Cue S_1, Change S_4` is the maximally *invalid* trial (change at the diagonally opposite location).
- $\Delta$ or `Delta` — the explicit signed orientation change magnitude on a trial when a change occurs, drawn from $\mathcal{U}(-\theta, \theta)$ with $\theta = 65°$ at curriculum start. We always plot psychometrics against $|\Delta|$.
- $t^\star$ — the change time, drawn from $\mathcal{U}\{11, \ldots, 25\}$.

**Internal model variables:**

- `α_i` — aggregated attention on stimulus position $S_i$. Defined precisely as the sum of the saliency map $S_t$ over the spatial cells comprising quadrant $S_i$:
  $$\alpha_i(t) = \sum_{(h, w) \in \text{cells}(S_i)} S_t(h, w),$$
  where `cells(S_i)` is the set of grid cells in the 12×12 saliency-map grid that fall inside quadrant $S_i$ (a 6×6 sub-grid). Often normalized so $\sum_i \alpha_i(t) = 1$ for visualization; report both the raw and normalized form.
- $M_t$ — the recurrent memory state.
- $S_t$ — the per-cell saliency map (the prediction-error magnitude pooled to the 12×12 grid).

**Trial taxonomy used for stratifying every analysis:**

A trial is uniquely classified by the tuple `(Cue S_i, Validity p, Cue RM ρ, Change present?, Change S_j (if present), |Δ| (if present), t^* (if present))`. Most analyses condition on a subset of these.

The headline cueing comparisons are:

- **Valid-cue, valid-change** (the canonical valid trial): `Cue S_1, Change S_1` and `Cue S_4, Change S_4`.
- **Valid-cue, opposite-change** (the canonical invalid trial): `Cue S_1, Change S_4` and `Cue S_4, Change S_1`. Most diagnostic when **Validity = 1.0** because the model "should not" expect a change at the un-cued location.

---

## 3. High-level phase roadmap

Phases run roughly in sequence, but the standing analyses (Section 4) and Phase 0 housekeeping run continuously.

| Phase | Title | Output venue role |
|---|---|---|
| **0** | Foundation: training stability, multi-seed runs, infrastructure | Methods (training procedure, reproducibility) |
| **1** | Behavioral baseline: learning curves, basic correctness | Section "Learning dynamics" of Results |
| **2** | Psychometrics: full Δ × cue × validity × RM × location battery | Headline figures of Results |
| **3** | Chronometrics: RT distributions, drift-diffusion fits | Headline figures of Results |
| **4** | Attention map (α_i) characterization across all cueing conditions | Headline figures of Results |
| **5** | Causal manipulations of α_i (microstimulation, lesion, redistribution analogues) | Headline figures of Results; the cross-disciplinary core |
| **6** | Working-memory representational analyses (decoding, RSA, cross-temporal) | Results + Discussion |
| **7** | Inner-loop variational-inference depth: K-sweep and convergence diagnostics | Results (compute-depth hypothesis) |
| **8** | Component ablations | Results (ablation table) |
| **9** | Generalization & bitter-lesson tests on a second environment | Results / Discussion |
| **10** | Comparison baselines (vanilla recurrent, transformer, slot-attention) | Results (comparison table) |
| **11** | Neuroscientific cross-validation: compare to published primate / human data | Discussion |
| **12** | Manuscript polish, figures, supplementary, submission | Manuscript itself |

Each phase has multiple tasks below.

---

## 4. Standing analyses (run on every cowork check-in)

These are non-blocking and produce the dashboards that a hourly cowork should keep fresh. They are not part of the publication directly but they are the early-warning system for everything else.

- `[ ] SA.1` Tail the most recent training run's `logs/{run_name}.jsonl` and update `figures/standing_training_curves.png` with rolling reward, correctness, L_PC (forward, autoenc, feature), L_V, H, KL, mean episode length. One panel each. Mark vertical lines at the PC-pretrain → RL transition and the inner-K warmup boundary. Output: `figures/standing_training_curves.png`.
- `[ ] SA.2` Recompute the per-component parameter count and total parameter count from the current `model.py` and write to `tables/param_budget.csv`. Flag any change since the previous count.
- `[ ] SA.3` Sanity-check the latest checkpoint by running 200 evaluation episodes and reporting mean return, correct rate, and mean episode length. Compare to the training-time rolling stats; if the gap exceeds one standard deviation flag it in the Decision Log.
- `[ ] SA.4` On any architecture change (any modification to `model.py`, `decoder.py`, `memory.py`, `readout.py`, `losses.py`), re-run the verification suite in `tests/` (shapes, identity-at-init, contraction, PPO smoke). Any failure blocks all downstream tasks until resolved.
- `[ ] SA.5` Diff the training config between the current run and the previous archived run; log any change in the Decision Log so the experimental record is unambiguous.

---

## 5. Phase tasks

### Phase 0 — Foundation

- `[ ] P0.1` **Training stability validation.** Run two consecutive 50K-iter training runs from the same seed with the current config and confirm reward curves are bit-identical (Adam epsilon and PyTorch determinism toggled). DoD: side-by-side comparison plot in `figures/P0_1_determinism.pdf` showing the two curves overlap; max divergence $< 10^{-6}$ in mean return at every checkpoint.
- `[ ] P0.2` **Episode-collection profiling.** Profile `collect_episodes` and `ppo_update` for the default config; identify the dominant cost. Write to `notebooks/P0_2_profile.ipynb`. DoD: a Pareto chart of CPU time per call site, and a recommendation on whether vectorizing the env (currently single-env) would help.
- `[ ] P0.3` **Vectorized env wrapper (if P0.2 indicates).** Implement a minimal `VecChangeDetectionEnv` that runs `n_envs` copies in parallel via process pool. Hook into `collect_episodes`. DoD: 4× speedup at `n_envs=4` with bit-identical reward distributions.
- `[ ] P0.4` **Multi-seed training infrastructure.** Add a `--seeds` flag to `train.py` that spawns one run per seed with deterministic naming `prism_v1_seed{N}_{date}`. Each writes its own JSONL log. DoD: command `python3 train.py --seeds 0 1 2 3 4` produces 5 separate checkpoint directories.
  - Depends on: `[x] SA.4`
- `[ ] P0.5` **Checkpoint loader / replay tool.** Build `analysis/replay_checkpoint.py` that loads a checkpoint, runs N evaluation episodes, and dumps per-step `(x_t, M_t, S_t, action_logits, value, reward, done)` tuples to an HDF5 file for downstream analysis. This is the workhorse used by every subsequent phase. DoD: HDF5 schema documented in `analysis/HDF5_SCHEMA.md`; round-trip test passes (load → reproduce reward curve).
  - Depends on: `[x] P0.4`
- `[ ] P0.6` **Trial-classifier utility.** Build `analysis/classify_trials.py` that, given a replay HDF5, tags each trial with `(Cue S_i, Validity, Cue RM, Change S_j or none, Δ, t^*)`. This is the canonical stratification used in Phases 2–6. DoD: classifier round-trips with the env's internal state (i.e., re-running the env with the recorded actions reproduces the recorded observations and rewards).
  - Depends on: `[x] P0.5`
- `[ ] P0.7` **Curriculum on θ.** Add an optional θ-anneal schedule to the env (start at 65, anneal to 5 over the course of training when rolling correctness exceeds a threshold). Document the policy in `docs/CURRICULUM.md`. DoD: training run with curriculum reaches lower θ than the baseline at matched compute, with the schedule logged to JSONL.
- `[ ] P0.8` **Architecture freeze and tag.** Tag the current `git` commit as `prism-v1` and lock the architecture for all Phase 1–8 results. Any subsequent architecture change forks `prism-v2` and re-runs all dependent analyses. DoD: tag visible in `git log`, noted in `Section 1 — Current State`.

### Phase 1 — Behavioral baseline

- `[ ] P1.1` **Multi-seed final training.** Train 8 seeds (0–7) of `prism-v1` with the curriculum from P0.7 to convergence (target: rolling reward stable above 2.5 for 1000 iterations, or 200K iterations whichever is first). DoD: 8 checkpoints in `checkpoints/prism_v1_seed{0..7}_final/`. Total wallclock: ~7 days at one episode/sec, 1.6M episodes per seed.
  - Depends on: `[x] P0.4`, `[x] P0.7`, `[x] P0.8`
- `[ ] P1.2` **Across-seed learning curves.** Plot mean ± SD across the 8 seeds of: rolling reward, correctness rate, L_PC components, mean episode length, and KL. Annotate the never-press baseline (1.47), oracle ceiling (2.98), and curriculum θ schedule. Output: `figures/P1_2_learning_curves.pdf`. DoD: figure committed; mean asymptotic reward and SD reported in `tables/P1_2_summary.csv`.
  - Depends on: `[x] P1.1`
- `[ ] P1.3` **Per-seed evaluation battery.** For each seed, run 5000 evaluation episodes at θ = 65° (the easiest curriculum setting) and at θ = 30° (a harder one). Report per-seed (mean reward, correct rate, false-alarm rate, miss rate) at each θ in `tables/P1_3_per_seed_eval.csv`. DoD: table and per-seed scatter in `figures/P1_3_per_seed_eval.pdf`.
  - Depends on: `[x] P1.1`
- `[ ] P1.4` **Baseline policy benchmarks.** Re-run the oracle, never-press, always-press-at-t=11, and uniform-random policies for 5000 episodes at θ ∈ {65°, 30°, 10°}. Report return distributions. DoD: histogram comparison in `figures/P1_4_baseline_policies.pdf`; the 1.47/2.98 numbers in the manuscript get cited from this file.

### Phase 2 — Psychometrics

The full psychometric battery is 2 (Cue S_i ∈ {S_1, S_4}) × 4 (Validity) × 3 (Cue RM) × 4 (Change S_j ∈ {S_1, ..., S_4}, conditioned on change present) × N_trials_per_Δ × 10 Δ-bins. By exploiting symmetry between (Cue S_1) and (Cue S_4) we can collapse to roughly 4 × 3 × 4 × 10 × 250 ≈ 120 K trials per seed per battery. Eight seeds → ≈ 1M trials per full battery. At ~30 steps/trial this is ≈ 30M model-step inference calls per battery — about a day of wallclock at the current per-step cost.

- `[ ] P2.1` **Full psychometric battery, primary.** For each of the 8 seeds, run the battery defined above with $|\Delta|$ binned at $\{2°, 5°, 10°, 15°, 20°, 30°, 40°, 50°, 65°\}$. Use the same RNG seed for cue/change identities across model seeds so model effects are isolated from trial-set variability. Output: HDF5 trial dumps in `analysis/psychometric_runs/seed{0..7}/`.
  - Depends on: `[x] P1.1`, `[x] P0.5`, `[x] P0.6`
- `[ ] P2.2` **Validity-effect headline figure.** Plot psychometric curves of $P(\text{hit} \mid |\Delta|, \text{cue condition})$ for the four validity-effect comparisons:
  - `Cue S_1, Change S_1, Validity ∈ {1.0, 0.75, 0.5, 0.25}` (graded valid)
  - `Cue S_1, Change S_4, Validity ∈ {1.0, 0.75, 0.5, 0.25}` (graded invalid)
  - `Cue S_4, Change S_4, Validity ∈ {1.0, 0.75, 0.5, 0.25}` (mirror of valid)
  - `Cue S_4, Change S_1, Validity ∈ {1.0, 0.75, 0.5, 0.25}` (mirror of invalid)
  
  Average across the two cue positions where appropriate (after confirming symmetry in P2.4). Fit a cumulative-Gaussian to each curve and extract threshold and slope. The headline panel: `Cue S_1 Change S_1 vs Cue S_1 Change S_4 at Validity = 1.0` — the maximally diagnostic comparison the user flagged. Output: `figures/P2_2_psychometric_validity.pdf` and `tables/P2_2_thresholds.csv`.
  - Depends on: `[x] P2.1`
- `[ ] P2.3` **Reward-magnitude effect figure.** Plot psychometric curves stratified by Cue RM $\rho \in \{1, 3, 5\}$ at validity = 1.0. Test whether higher RM lowers detection threshold (would be evidence of reward-modulated attentional gain). Output: `figures/P2_3_psychometric_RM.pdf`.
  - Depends on: `[x] P2.1`
- `[ ] P2.4` **Symmetry test.** Verify that `Cue S_1 / Change S_1` and `Cue S_4 / Change S_4` produce statistically indistinguishable psychometric curves (same logic for the off-cue pairs). Use a permutation test on the threshold parameter; report p-value per validity level. If symmetry holds, all subsequent figures collapse cue position. Output: `tables/P2_4_symmetry_pvalues.csv`.
  - Depends on: `[x] P2.1`
- `[ ] P2.5` **Cross-location asymmetry analysis.** Confirm that off-cue change locations $S_2$ and $S_3$ (the two not-cued, not-opposite quadrants) show indistinguishable performance from each other; if not, investigate why. Output: `figures/P2_5_offcue_locations.pdf`.
  - Depends on: `[x] P2.1`
- `[ ] P2.6` **False-alarm characterization.** Plot the false-alarm rate (proportion of `Change present = no` trials on which the agent reports change) as a function of Cue RM and Validity. Does the model become more conservative (lower FA) on low-RM trials, in line with reward-weighted signal-detection theory? Output: `figures/P2_6_false_alarms.pdf`.
  - Depends on: `[x] P2.1`
- `[ ] P2.7` **Comparison to human cued-detection psychometrics.** Find published human psychometric data on Posner cueing of orientation discrimination (target citation candidates: Carrasco & Yeshurun 2009, Lu & Dosher 1998). Overlay the model's threshold-vs-validity curve on the human data with appropriate axis scaling. Output: `figures/P2_7_model_vs_human.pdf`. This is one of the figures that makes the paper land at PNAS rather than a pure ML venue.
  - Depends on: `[x] P2.2`

### Phase 3 — Chronometrics

Reaction time per trial is defined as `RT = action_step − change_step` for hit trials. For false alarms it is `RT_FA = action_step − cue_step`. We always report distributions, not just means.

- `[ ] P3.1` **RT distribution extraction.** For each replay HDF5 from P2.1, extract per-trial RT (or `NaN` for misses and correct rejections). Save to `analysis/rt_data/seed{0..7}.parquet`. DoD: file sanity-checked against trial counts.
  - Depends on: `[x] P2.1`
- `[ ] P3.2` **RT distributions stratified by validity and |Δ|.** Plot the conditional RT distribution (median, IQR, 90th percentile) versus $|\Delta|$ for each validity level. Test the prediction that RT shortens with $|\Delta|$ (evidence accumulation). Output: `figures/P3_2_rt_vs_delta.pdf`.
  - Depends on: `[x] P3.1`
- `[ ] P3.3` **Validity speedup of RT.** Plot mean RT for `Cue S_1, Change S_1` versus `Cue S_1, Change S_4` at Validity = 1.0, as a function of $|\Delta|$. The headline prediction is that valid trials show shorter RT at every $|\Delta|$. Compute the validity-effect magnitude (RT_invalid − RT_valid) and compare to published Posner-cueing RT effects (~30–50 ms in humans, scaled appropriately for the model's frame-discrete time). Output: `figures/P3_3_validity_speedup.pdf` and `tables/P3_3_validity_effect.csv`.
  - Depends on: `[x] P3.1`
- `[ ] P3.4` **Drift-diffusion model fit.** For each (Cue, Validity, |Δ|) condition, fit a drift-diffusion model (Ratcliff 1978) using the HDDM Python package to extract drift rate $v$, decision threshold $a$, non-decision time $T_\text{er}$, and starting-point bias $z$. Test predictions: $v$ scales with $|\Delta|$; $v$ is higher on valid than invalid trials; $a$ may be lower on high-RM trials. Output: `tables/P3_4_ddm_fits.csv` and `figures/P3_4_ddm_parameter_landscapes.pdf`.
  - Depends on: `[x] P3.1`
- `[ ] P3.5` **Speed-accuracy tradeoff.** Plot the conditional accuracy function: P(correct | RT) versus RT, stratified by $|\Delta|$. The prediction is that faster reports are more accurate at high $|\Delta|$ but less accurate at low $|\Delta|$ (the canonical SAT shape). Output: `figures/P3_5_sat.pdf`.
  - Depends on: `[x] P3.1`
- `[ ] P3.6` **False-alarm timing.** For false-alarm trials, plot the distribution of `RT_FA` versus the would-be change time $t^*$. Does the model false-alarm uniformly across the trial timeline, or does it concentrate FAs near the cue (over-reaction to surprise)? Output: `figures/P3_6_fa_timing.pdf`.
  - Depends on: `[x] P3.1`
- `[ ] P3.7` **Chronometric comparison to published primate RT data.** Overlay the model's RT-vs-$|\Delta|$ relation on monkey LIP RT data from coherence-discrimination tasks (Roitman & Shadlen 2002) with appropriate scaling. Output: `figures/P3_7_model_vs_monkey_rt.pdf`.
  - Depends on: `[x] P3.4`

### Phase 4 — Attention map (α_i) dynamics

- `[ ] P4.1` **α_i extraction from replay.** Implement `analysis/extract_alpha.py` that reads a replay HDF5 (which contains $S_t$ at every step), computes $\alpha_i(t) = \sum_{(h,w) \in S_i} S_t(h, w)$ per quadrant, and writes per-trial $\alpha_i$ time series to a new HDF5. Provide both raw and normalized ($\alpha_i / \sum_j \alpha_j$) variants. DoD: per-trial $\alpha$-traces queryable by `(Cue, Change, Validity, RM)`.
  - Depends on: `[x] P0.5`, `[x] P0.6`
- `[ ] P4.2` **α_i headline trajectories.** Plot mean $\alpha_i(t)$ across trials, $i \in \{S_1, S_2, S_3, S_4\}$, for the four canonical cueing conditions:
  - `Cue S_1, Change S_1, Validity = 1.0` (canonical valid)
  - `Cue S_1, Change S_4, Validity = 1.0` (canonical invalid; biggest cue–change conflict)
  - `Cue S_1, Change none, Validity = 1.0` (no-change trial)
  - `Cue S_1, Change S_1, Validity = 0.25` (low-validity but valid)
  
  Predicted observations: $\alpha_{S_1}$ peaks at $t = 1$ (cue onset), stays elevated through the maintenance period (top-down enhancement at cued location), and either spikes again (valid change) or cedes mass to $\alpha_{S_4}$ (invalid change) when the change occurs. Overlay the curves for the four conditions in stacked panels. Output: `figures/P4_2_alpha_trajectories.pdf`. **Headline figure.**
  - Depends on: `[x] P4.1`
- `[ ] P4.3` **α_i heatmap movies.** For 5 representative trials per cue condition, render the full 12×12 saliency map $S_t$ as an animated heatmap (PDF page per timestep, stitched as PNG sequences in `figures/P4_3_movies/`). Comment on the qualitative dynamics in `figures/P4_3_caption.md`.
  - Depends on: `[x] P4.1`
- `[ ] P4.4` **Cue-encoding latency.** Define the cue-encoding latency as the first timestep $t$ at which $\alpha_{\text{Cue position}}(t) - \alpha_{\text{other quadrants}}(t)$ exceeds 2 SD of the pre-cue (t=0) distribution. Report the mean latency and its distribution per Validity condition. Compare to monkey LIP cue-onset latencies from cueing experiments (Bisley & Goldberg 2003, ~50–80 ms). Output: `tables/P4_4_cue_latency.csv`, `figures/P4_4_cue_latency.pdf`.
  - Depends on: `[x] P4.1`
- `[ ] P4.5` **Change-detection latency.** Define analogously for the change frame: first $t > t^\star$ at which $\alpha_{\text{Change position}}(t)$ exceeds 2 SD of its pre-change baseline. Test prediction: latency shortens with $|\Delta|$ and with valid-cueing. Output: `tables/P4_5_change_latency.csv`, `figures/P4_5_change_latency.pdf`.
  - Depends on: `[x] P4.1`
- `[ ] P4.6` **Maintenance-period attention quality.** Quantify how cleanly $\alpha_i$ tracks the cued location through the maintenance period (steps $t = 2$ to $t^\star - 1$). Compute per-validity the average $\alpha_{\text{cued}}(t) / \sum_j \alpha_j(t)$ over the maintenance window. Predicted: high-validity trials show $> 0.4$ (concentrated), low-validity trials show $\approx 0.25$ (uniform). Output: `figures/P4_6_maintenance_attention.pdf`.
  - Depends on: `[x] P4.1`
- `[ ] P4.7` **Validity-modulated cueing index.** Construct the cueing index $\text{CI}(t) = \alpha_{\text{cued}}(t) - \frac{1}{3}\sum_{i \neq \text{cued}} \alpha_i(t)$ as a single scalar measure of cue-driven attention. Plot CI(t) per validity condition. The CI vs validity slope is the key parameter to compare to the human "valid minus invalid" RT difference. Output: `figures/P4_7_cueing_index.pdf`.
  - Depends on: `[x] P4.1`
- `[ ] P4.8` **Reward-magnitude modulation of α.** Test whether high-RM cues produce stronger cueing than low-RM cues (would imply value-modulated attentional priority, a key finding from Maunsell 2004). Plot CI(t) stratified by Cue RM. Output: `figures/P4_8_RM_modulation.pdf`.
  - Depends on: `[x] P4.7`

### Phase 5 — Causal manipulations of α (the cross-disciplinary core)

These are the experiments that distinguish PRISM from purely correlative models. For each manipulation we both characterize the behavioral effect and we relate it to a published primate or human causal experiment.

- `[ ] P5.1` **Manipulation harness.** Build `analysis/causal_manipulate.py` that wraps `forward_step` and allows three classes of manipulation to be applied to $S_t$ before it is used by the GRU's update gate or by the decision readout: clamp (force $S_t$ at quadrant $i$ to a target value), suppress (force $S_t$ at quadrant $i$ to zero), and redistribute (rescale $S_t$ so a target proportion of mass falls at a target quadrant while the total is preserved). DoD: harness runs end-to-end, with a unit test confirming that with no manipulation the trajectory matches the unmodified model bit-exactly.
  - Depends on: `[x] P0.5`
- `[ ] P5.2` **Microstimulation analogue (clamping at the cued location).** Run 5000 trials per cue condition with $S_t$ clamped HIGH at the cued location for $t \in [t_{\text{onset}}, t_{\text{onset}} + d]$ for various $(t_{\text{onset}}, d)$ pairs. Predicted: improved hit rate and shortened RT on valid trials; mixed effects on invalid trials. Cross-reference: SC microstimulation (Cavanaugh & Wurtz 2004, Müller et al. 2005) and LIP microstimulation (Cutrell & Marrocco 2002) experiments that bias attentional priority. Output: `figures/P5_2_microstim_cued.pdf`, `tables/P5_2_effects.csv`.
  - Depends on: `[x] P5.1`, `[x] P1.1`
- `[ ] P5.3` **Microstimulation analogue at uncued location.** Same as P5.2 but clamp at the un-cued location. Predicted: improves invalid-trial detection at the cost of valid-trial speed. This dissociation is the key falsifiable prediction. Output: `figures/P5_3_microstim_uncued.pdf`.
  - Depends on: `[x] P5.1`
- `[ ] P5.4` **Lesion analogue (suppression).** Suppress $S_t$ at a specific quadrant for the entire trial. Test prediction: deficits selective to changes occurring at the suppressed location, in analogy to spatial neglect. Output: `figures/P5_4_lesion.pdf` and a panel showing per-quadrant detection accuracy with each quadrant lesioned.
  - Depends on: `[x] P5.1`
- `[ ] P5.5` **Causal cross-quadrant redistribution.** Hold the total $\sum_i \alpha_i$ fixed but force a fraction $f$ of mass to a target quadrant. Sweep $f$ from 0 (none at target) to 1 (all at target). The "active" quadrant should produce a continuous improvement in detection at that quadrant and continuous deficits elsewhere. The shape of this curve tells us how linearly $\alpha$ translates to behavior. Output: `figures/P5_5_redistribution.pdf`.
  - Depends on: `[x] P5.1`
- `[ ] P5.6` **Maintenance-period vs change-window manipulation timing.** Run P5.2 with $t_{\text{onset}}$ varied over the trial (cue period $t \in [1, 2]$, early maintenance $[3, 7]$, late maintenance $[8, 10]$, change window $[11, 25]$). Identify the temporal window in which clamping has the largest behavioral effect. Predicted: largest effects in the cue and early-maintenance windows, where information about cue identity is being committed to memory. Output: `figures/P5_6_timing.pdf`.
  - Depends on: `[x] P5.2`
- `[ ] P5.7` **Disable saliency entirely (uniform attention control).** Replace $S_t$ with a constant uniform map for all $t$. Predicted: performance drops near uniformly across all conditions, eliminating validity effects entirely. This is the strongest test of the claim that the saliency map is functional. Output: `figures/P5_7_uniform_attention.pdf`.
  - Depends on: `[x] P5.1`
- `[ ] P5.8` **Cross-validation with published microstimulation effects.** For each of P5.2–P5.7, write a paragraph in `figures/P5_caption.md` mapping the model's effect to the closest-published primate or human manipulation. This is the text that goes into the main paper's Discussion.
  - Depends on: `[x] P5.2`–`[x] P5.7`

### Phase 6 — Working-memory representational analyses

- `[ ] P6.1` **Linear decoders over time.** Train ridge-regression linear decoders on $M_t$ at each timestep $t \in [0, 29]$ separately, predicting (a) cue position $S_i \in \{S_1, S_4\}$, (b) cue color $\in \{R, G, B\}$, (c) validity $p \in \{0.25, 0.5, 0.75, 1.0\}$, (d) per-quadrant baseline orientation (4 separate decoders), (e) change-presence $\in \{0, 1\}$, (f) change location $\in \{S_1, ..., S_4\}$, (g) $\Delta$ (regression). Plot per-target accuracy/$R^2$ as a function of $t$. Output: `figures/P6_1_decoding.pdf`, `tables/P6_1_decoding.csv`.
  - Depends on: `[x] P0.5`, `[x] P0.6`, `[x] P1.1`
- `[ ] P6.2` **Cross-temporal decoding.** Train decoders on $M_{t_1}$ and test on $M_{t_2}$ for all $(t_1, t_2)$ pairs to construct a temporal generalization matrix (King & Dehaene 2014). Diagonal blocks above the off-diagonal indicate stable representations. Output: `figures/P6_2_cross_temporal.pdf` per target variable.
  - Depends on: `[x] P6.1`
- `[ ] P6.3` **Representational dissimilarity matrix (RSA).** Compute per-condition RDMs of $M_t$ at $t \in \{2, 7, t^\star - 1, t^\star + 1, T-1\}$. Compare to model RDMs corresponding to "cue identity," "stimulus identity," "task variable" (i.e., reward magnitude × validity). Quantify which model fits best at each timepoint via Spearman rank correlation. Output: `figures/P6_3_rsa.pdf`, `tables/P6_3_rsa.csv`.
  - Depends on: `[x] P0.5`
- `[ ] P6.4` **Per-channel selectivity analysis.** For each channel $c \in [0, C_M)$ of the memory state, test linear selectivity to each task variable (cue color, cue position, change location, $|\Delta|$). Identify "cue channels," "stimulus channels," "decision channels." Visualize as a $C_M \times $ task-variable selectivity matrix. Output: `figures/P6_4_channel_selectivity.pdf`.
  - Depends on: `[x] P6.1`
- `[ ] P6.5` **Memory-state geometry over the trial.** Apply PCA to $M_t$ collapsed across trials but kept per-timestep. Plot the first 2 PCs as scatter clouds, colored by trial type, at $t \in \{1, 2, t^\star - 1, t^\star + 1\}$. Predicted: at $t = 1$ the cloud separates by cue position; at $t = 2$ it adds separation by cue color and validity; at $t = t^\star + 1$ it separates by change location (when present). Output: `figures/P6_5_pca_geometry.pdf`.
  - Depends on: `[x] P0.5`
- `[ ] P6.6` **Comparison to monkey PFC working-memory data.** Find published PFC delay-period decoding data on Posner-style or working-memory tasks (target: Constantinidis et al., 2018 review's data tables; Wallis & Miller 2003 if RM-modulation data needed). Side-by-side plot of model-decoding accuracy versus monkey-decoding accuracy across analogous task variables. Output: `figures/P6_6_model_vs_monkey_decoding.pdf`. **Headline neuroscience figure.**
  - Depends on: `[x] P6.1`

### Phase 7 — Inner-loop variational inference depth ($K$-sweep)

- `[ ] P7.1` **K-sweep training.** Re-train PRISM at $K \in \{0, 1, 2, 4, 8\}$, three seeds per setting (15 runs total). Use the same curriculum and total budget. Output: 15 checkpoints in `checkpoints/prism_v1_K{0,1,2,4,8}_seed{a,b,c}/`.
  - Depends on: `[x] P0.7`
- `[ ] P7.2` **Asymptotic accuracy vs K.** Plot mean and SD of asymptotic correctness rate against $K$, with the WM compute-depth hypothesis prediction overlaid (monotone non-decreasing, biggest jump from 1→2). Output: `figures/P7_2_K_asymptote.pdf`, `tables/P7_2_K_asymptote.csv`.
  - Depends on: `[x] P7.1`
- `[ ] P7.3` **Across-seed variance vs K.** Plot SD of asymptotic correctness across seeds against $K$. Predicted: strict decrease in SD with $K$ (P2 of the hypothesis). Output: `figures/P7_3_K_variance.pdf`.
  - Depends on: `[x] P7.1`
- `[ ] P7.4` **Banach contraction diagnostic.** For each trained $K \in \{2, 4, 8\}$ checkpoint, replay 1000 trials and at each step record the inner-loop residuals $\|M_t^{(k+1)} - M_t^{(k)}\|_F$. Test geometric decay on solved trials and failure to decay on subsequent-error trials. Output: `figures/P7_4_contraction.pdf`.
  - Depends on: `[x] P7.1`
- `[ ] P7.5` **Test-time K mismatch.** Train at $K_{\text{train}} = 8$, test at $K_{\text{test}} \in \{0, 1, 2, 4, 8, 16\}$. Predicted (P5 of WM hypothesis): performance degrades when $K_{\text{test}} < K_{\text{train}}$. Output: `figures/P7_5_test_K.pdf`.
  - Depends on: `[x] P7.1`
- `[ ] P7.6` **Compute-cost vs accuracy frontier.** Plot Pareto frontier of correctness rate vs FLOPs (computed analytically from $K$ and per-component costs). Show that compute-depth scaling outperforms width-scaling on a per-FLOP basis. Output: `figures/P7_6_pareto.pdf`.
  - Depends on: `[x] P7.1`

### Phase 8 — Component ablations

Each ablation re-trains 3 seeds for compute-economy. Ablations:

- `[ ] P8.1` **No FiLM.** Force $\gamma = 1, \beta = 0$ throughout. DoD: training run + psychometrics + α-trajectories versus full PRISM.
- `[ ] P8.2` **No autoencoding PC term.** Set $\alpha_\text{auto} = 0$. Predicted: cold-start zero-attractor returns; training fails to bootstrap.
- `[ ] P8.3` **No forward PC term.** Set $\alpha_\text{fwd} = 0$. Predicted: saliency map degenerates because it's derived from forward error; degraded behavior.
- `[ ] P8.4` **No inner WM ($K = 0$).** Equivalent to a row of P7.1 but written into the ablation table.
- `[ ] P8.5` **No actor bias init.** Initialize actor logits with zero bias instead of $[0, -4]$. Predicted: training fails (returns identically zero) because of bootstrapping starvation.
- `[ ] P8.6` **No PC pretrain.** Skip the forced-action-0 pretrain phase. Predicted: slower convergence; possibly oscillatory.
- `[ ] P8.7` **No coarse-grid readout.** Set `decision_coarse_grid = 1`, recovering the original 8-d state vector. Predicted: actor cannot localize surprise; degraded validity effect.
- `[ ] P8.8` **Memory width sweep.** Train at $C_M \in \{8, 16, 32, 64\}$ to dissociate compute-depth (Phase 7) from capacity. Predicted: compute-depth helps more per-FLOP than capacity.
- `[ ] P8.9` **Ablation table assembly.** Aggregate P8.1–P8.8 into a single ablation table reporting (asymptotic correctness, mean RT at $|\Delta| = 30°$, validity-effect magnitude) per ablation. Output: `tables/P8_ablations.csv`, `figures/P8_ablation_summary.pdf`.

### Phase 9 — Generalization & bitter-lesson tests

- `[ ] P9.1` **Moving-MNIST environment.** Implement a minimal moving-MNIST gym wrapper: a digit moves across a 50×50 frame at random velocity, "change" = sudden velocity vector flip at a random time. Same action structure as ChangeDetectionEnv. DoD: env runs, oracle policy verified.
- `[ ] P9.2` **Train PRISM on moving-MNIST without architecture changes.** Use the identical PRISM model and identical loss. Only the curriculum and possibly $\theta$-equivalent (here, velocity-flip magnitude) differ. Output: `checkpoints/prism_v1_movingMNIST_seed{0..2}/`.
  - Depends on: `[x] P9.1`, `[x] P0.8`
- `[ ] P9.3` **Bitter-lesson validation table.** Side-by-side performance of PRISM on ChangeDetectionEnv and on moving-MNIST, with the identical loss formula and architecture. The fact that no aux-loss surgery was required is the headline. Output: `tables/P9_3_transfer.csv`, `figures/P9_3_transfer.pdf`.
  - Depends on: `[x] P9.2`
- `[ ] P9.4` **Out-of-distribution θ.** Train at θ = 65° curriculum-annealed to 30°; test at θ ∈ {5°, 10°, 50°}. Quantify graceful degradation. Output: `figures/P9_4_ood_theta.pdf`.

### Phase 10 — Comparison baselines

For each baseline, train 3 seeds with comparable parameter budget (~250K) and the same training compute.

- `[ ] P10.1` **Vanilla CNN+LSTM+PPO baseline.** Standard architecture: CNN encoder → LSTM → MLP heads. No FiLM, no PC loss, no inner loop. Use only RL signal. DoD: training run + psychometrics. Predicted: fails to learn meaningful change detection; settles at the never-press baseline.
- `[ ] P10.2` ~~**The original JointTraining model.**~~ **Removed** — the v0 backbone (`joint_rvt_backbone.py`) was deleted when the project was pruned to PRISM v1 + v2 only. If a baseline comparison against an end-to-end PPO architecture without PC is still needed for methodological fairness, restore from git history or rely on P10.1 (vanilla CNN+LSTM+PPO) as the substitute control.
- `[ ] P10.3` **Spotlight baseline (RAM-style).** Implement Mnih et al.'s recurrent attention model adapted to this env: discrete glimpse locations, REINFORCE on glimpse policy, classifier head. Train 3 seeds. Predicted: attention spotlight learns to track cue but fails on uncued-change trials. This baseline operationalizes the "spotlight is dead" claim.
- `[ ] P10.4` **Slot-attention baseline (Locatello-style).** Implement slot attention with K=4 slots over the conv-backbone features; recurrent slot updates; classifier head. Predicted: slots bind to the four Gabor patches but the "which slot is the cue?" assignment is unstable.
- `[ ] P10.5` **Comparison table assembly.** Aggregate all baselines into one table reporting (correctness, RT, validity effect, parameter count, FLOPs/episode). Output: `tables/P10_5_baselines.csv`, `figures/P10_5_baselines.pdf`.

### Phase 11 — Neuroscientific cross-validation

- `[ ] P11.1` **Map PRISM components to cortical areas.** Produce a single annotated diagram with each PRISM module labeled by its claimed cortical homologue (V1 stem ↔ V1, FiLM ↔ feedback projections from PFC, generative decoders ↔ V1-projecting feedback layers, GRU ↔ dlPFC working memory, inner loop ↔ recurrent PFC dynamics, decision readout ↔ LIP/FEF, actor/critic ↔ basal ganglia / motor cortex). Output: `figures/P11_1_neural_homologue.pdf`.
- `[ ] P11.2` **Lesion-effect comparison.** For each ablation in Phase 8, find the closest published lesion or pharmacological inactivation experiment in primates / humans. Build a mapping table: (PRISM ablation, behavioral signature, primate analog, primate signature). Output: `tables/P11_2_lesion_map.csv`.
- `[ ] P11.3` **Single-cell RDM matching.** Where published single-cell PFC data is available (e.g., Funahashi et al. 1989 mnemonic activity tuning), compute the RDM of monkey neurons across stimuli and compare to PRISM's per-channel RDM. Output: `figures/P11_3_single_cell_RDM.pdf`.
- `[ ] P11.4` **fMRI BOLD comparison (stretch).** If a public fMRI dataset on Posner-cued change detection is accessible, compute voxel-wise activation under valid vs invalid trials and compare to PRISM's per-quadrant attention modulation. This is the kind of cross-modal validation that lands a paper at PNAS. Output: `figures/P11_4_fmri.pdf` if data accessible; otherwise note as a future direction.

### Phase 12 — Manuscript polish & submission

- `[ ] P12.1` **Update Methods section** of `THESIS.md` with finalized hyperparameters, training schedule, all configs.
- `[ ] P12.2` **Fill Section 4 (Results)** of `THESIS.md` with the figures and quantitative findings from Phases 1–11. Each subsection of THESIS Section 3 maps to a Phase.
- `[ ] P12.3` **Write Discussion** in `THESIS.md`. Cover (a) the spotlight-versus-distributed-gain debate and how PRISM bears on it; (b) what neuroscience predictions PRISM makes that no spotlight model does (the validity-effect generalization across off-cue locations); (c) limitations: small action space, no precision-weighting, no truly hierarchical PC; (d) future directions.
- `[ ] P12.4` **Write Abstract and Introduction polish pass.** Update the existing draft with the most striking quantitative results.
- `[ ] P12.5` **Build Figure 1.** A composite of the architecture diagram (P11.1), the canonical α-trajectory headline (P4.2), and the validity-effect psychometric headline (P2.2). This is the figure the editor sees first.
- `[ ] P12.6` **Build Figure 2.** Causal manipulation panel from Phase 5.
- `[ ] P12.7` **Build Figure 3.** Memory decoding from Phase 6.
- `[ ] P12.8` **Build Figure 4.** WM compute-depth from Phase 7.
- `[ ] P12.9` **Build Supplementary Figure set** for Phase 8 ablations, Phase 9 transfer, Phase 10 baselines.
- `[ ] P12.10` **Reference manager.** Migrate the bibliography in THESIS.md to BibTeX (`docs/refs.bib`); ensure every reference cited in the paper text is in the .bib.
- `[ ] P12.11` **Internal review.** Hand the manuscript to a non-author for feedback before submission.
- `[ ] P12.12` **Format for target venue.** PNAS template if going to PNAS; NeurIPS template if going to NeurIPS. Both have hard page limits and figure constraints; mark which one we're targeting and finalize.
- `[ ] P12.13` **Submit.**

---

## 6. Cowork hourly-run protocol

When a scheduled cowork instance starts, the protocol is exactly:

1. `git pull` (or equivalent) to get the latest version of this document.
2. Read Section 1 (Current State).
3. Run all `SA.*` standing analyses in Section 4.
4. If any SA flags an issue (especially SA.4 test failures), STOP, write the issue to the Decision Log, and exit. Do not proceed to phase tasks if the verification suite is failing.
5. Find the lowest-numbered phase task with status `[ ]` and all dependencies `[x]`. Pick that one.
6. Update its status to `[~]`. Note the run ID and start time in-line.
7. Execute the task. Save outputs to the documented paths. Most tasks should complete within 1 hour; if not, leave status as `[~]`, write a "still running" note, and exit. The next cowork can either continue or pick a different task.
8. On completion: change status to `[x]`, append the artifact path, and add a one-line entry to the Progress Log.
9. If the task surfaced any new finding, blocker, decision, or surprise, add it to the Decision Log.
10. Commit and push.

A daily run can chain through multiple `[ ]` tasks, but should still respect dependencies and the SA gate.

---

## 7. Risk register and contingencies

- **Training divergence after P0.8 freeze.** If the v1 architecture stops converging on a fresh seed, do not silently re-jig hyperparameters. Open `[?]` in the Decision Log and surface to the human. Architecture stability is more important than any single seed's score.
- **Multi-seed variance is high (> 30% of mean).** Phase 1.2 outputs will reveal this. If true, it indicates either (a) inadequate inner-K (test in Phase 7), or (b) actor-bootstrapping fragility (re-test P8.5 with stronger init), or (c) genuine multi-modal solutions that the seeds find. Each has a different remedy.
- **Causal manipulations in Phase 5 produce no behavioral effect.** This would mean $\alpha$ is not actually functional. Open the question of whether the readout is pooling over $\alpha$ in a way the actor exploits. P5.7 is the diagnostic: if uniform-attention performs as well as full PRISM, then the model is not using attention causally and we have an architecture problem, not a manipulation problem.
- **Generalization to moving-MNIST fails (Phase 9).** The bitter-lesson claim weakens. Discuss honestly in the manuscript; do not hide. Consider it as a future-work pointer.
- **Decoder collapse returns at scale.** If the autoencoding term proves insufficient at the larger model widths in P8.8, escalate to a contrastive PC variant (van den Oord 2018 CPC).

---

## 8. Decision Log

Append-only. Each entry is a date-stamped paragraph noting a decision made, who/what made it, and the reasoning. The latest decisions go at the bottom.

- *2026-04-30* — Architecture v1 frozen at HEAD with the autoencoding PC term, actor-bias init [0, -4], coarse-grid readout (G=2), decision_channels=8, inner_K=2, inner_K_warmup=5000, pc_pretrain=2000, entropy_coef=0.005. Justification: training first crossed chance (return > 1.5) under this config. Any change forks v2.
- *[future entries]*

---

## 9. Progress Log

Append-only. Each entry is `YYYY-MM-DD HH:MM | Task ID | Owner | One-line summary | Artifact path`.

- *2026-04-30 — | — | jonathan | Initial PROJECT_PLAN.md drafted. | docs/PROJECT_PLAN.md*
- *[future entries]*

---

## 10. Open questions / parking lot

- Should we add a `Cue S_2` and `Cue S_3` (currently only `Cue S_1` and `Cue S_4` exist in env)? Would let us dissociate the "diagonal opposite" psychometric from the "adjacent" one.
- Should the Cue RM be confounded with cue color (currently it is)? A clean experiment would orthogonalize color and reward magnitude.
- Should we include human psychophysics data collection (run the same task on humans) for direct comparison? This would dramatically strengthen the PNAS angle but adds infrastructure.
- For Phase 5, should we also clamp $S_t$ to specific spatial patterns (e.g., a Gabor-shaped saliency) to test pattern-specific effects?

---

## 11. Out of scope (intentional non-goals for this paper)

These are tempting but explicitly excluded from the scope of this manuscript to keep it focused. Note them so the cowork doesn't drift into them.

- Active inference for action selection (replace reward with expected-free-energy minimization). Tempting because it would unify the framework, but adds architectural complexity disproportionate to its incremental contribution.
- Hierarchical predictive coding (multi-level PC with errors at every layer). Worth doing but a separate paper.
- Spiking-neuron implementation. A separate methodological project.
- Continuous-action variants. The two-action setup is sufficient for the cueing-paradigm comparisons.
- Pretraining on natural-image datasets (ImageNet etc.). Out of scope for the bitter-lesson framing; would dilute the "same loss, any env" claim.

---

*End of PROJECT_PLAN.md. This document is the source of truth for what gets done next on this project. Every change to it should be committed with a message starting `[plan]`.*
