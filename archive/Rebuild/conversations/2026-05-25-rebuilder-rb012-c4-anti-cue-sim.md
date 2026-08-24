---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-012-2026-05-25
started: 2026-05-25T17:00:00Z
ended: 2026-05-25T17:35:00Z
worked_on: RB-008
output_kind: simulation
claims_touched: [C4, A1]
artifacts_written:
  - Rebuild/sims/C4--anti-cue-inversion/run.py
  - Rebuild/sims/C4--anti-cue-inversion/README.md
  - Rebuild/sims/C4--anti-cue-inversion/output/results.json
  - Rebuild/sims/C4--anti-cue-inversion/output/run.log
  - Rebuild/sims/C4--anti-cue-inversion/output/figures/er_vs_alpha_anticue.png
  - Rebuild/sims/C4--anti-cue-inversion/output/figures/alpha_star_V_r_map.png
  - Rebuild/sims/C4--anti-cue-inversion/output/figures/r_inv_closed_form.png
  - Rebuild/CLAIM_LEDGER.md (C4 row backing wired; A1 row cross-axis corroboration noted; reconcile-line bumped)
  - Rebuild/REBUILD_BACKLOG.md (RB-008 marked done; RB-012 notes updated; RB-030, RB-031, RB-032 spawned)
  - Rebuild/rebuilder_state.json (runs_completed=12, RB-008 in done_task_ids, RB-030/031/032 in open_task_ids, rb_012_sim_digest pinned, next_task_id_counter=33)
  - Rebuild/BUILD_LOG.md (rb-012 entry prepended)
papers_added: []
spawned_tasks: [RB-030, RB-031, RB-032]
---

# rb-012 — C4 anti-cue inversion (simulation increment)

## What I built

`Rebuild/sims/C4--anti-cue-inversion/`: a 4-step probe of C4 (no
inversion) at the rebuilt model's headline cell (`N=4, d'_max=2,
f_0=0.5, h=sqrt`, variant A primarily; variant A and B both probed in
Step A), driving `Rebuild/model/core.py` exclusively. 17.4 s wall-clock
on python3.13 / scipy 1.17.1 / numpy 2.4.4. Two recovery tests, both
PASS.

The sim extends the reviewer's CR-004 (`Critique/replications/
C4--no-inversion/`) in two specific ways:

1. **ρ-aware closed form for the boundary inversion threshold.** The
   reviewer's `r_inv_threshold(V, v, N, CR)` returns
   `r†_inv = (N-1) A_0/B_0` at ρ = 0 only. We extend `A_0, B_0` to ρ > 0
   by computing the boundary partials
   `∂P_no-fa(ρ)/∂d'_c` and `∂P_no-fa(ρ)/∂d'_u` with the same one-factor
   Gauss-Hermite-64 quadrature `Rebuild/model/core.py` already uses for
   `P_no-fa(ρ)` itself. At ρ = 0 the formula collapses bit-for-bit to
   the reviewer's analytic form (derivation §2.2); at ρ > 0 it is new.

2. **Anti-cue inversion at N=4** (the paper's primary topology; the
   reviewer's CR-004 Step C(iii) ran anti-cue only at N=2). The
   rebuild's Step C sweeps V ∈ {0.05, 0.10, 0.15, 0.20} (all < 1/N=0.25
   at N=4) × v ∈ {1, 3, 5} × r ∈ {0.1, 0.5, 1, 3, 5, 10} × ρ ∈ {0, 0.2}
   at variant A = 144 cells. This is the rebuild's *new positive
   evidence* for the anti-cue inversion prediction at the paper's own
   topology.

## How it connects to the ledger

- **C4 (live: CONFIRMED-CONDITIONAL).** The rebuilt strength is a
  *conditional theorem* with explicit `V ≥ 1/N` (sharp form
  `V ≥ 1/[(N-1)v+1]`, equivalent at v=1), a closed-form local
  threshold `r†_inv = (N-1) A_0/B_0`, and the anti-cue inversion
  prediction as a new falsifiable claim. The rb-012 sim provides the
  simulation evidence at this strength — no over-statement. The C4 row
  of `CLAIM_LEDGER.md` now lists this sim, three figures, the recovery
  tests, and a complete summary of the headline numbers, exactly at the
  ceiling the §3 mission table licenses.

- **A1 (live: CONTESTED).** This sim is *not* an A1 increment, but it
  produces a passing cross-axis observation: ρ = 0.2 leaves the
  qualitative anti-cue inversion locus and incidence unchanged
  (25 vs 26 anti-cue inversions across 72 probes); it shifts `r†_inv`
  quantitatively (median by 13% variant A / 21% variant B) but does
  not abolish the C4 inversion regime. **A1 and the C4 inversion lever
  are independent mechanisms.** This adds a sentence to the A1 row's
  *backing* column (no strength change) and is the third axis (after
  rb-002's r-axis and rb-004's v-axis and rb-010's `(V, v)`-plane) on
  which the A1 sensitivity has been mapped — now on the inversion-
  conditional axis.

## Simulation evidence

- **`output/results.json` sha256: `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`**
  over the JSON content (excluding wall-clock `meta.elapsed_seconds`).
- **Recovery #1** (reviewer derivation §4 "49% of cells at N=4, ρ=0
  with r†_inv ∈ [0.1, 10]"): rebuild finds 48.6%, Δ=0.4 pp, **PASS**
  (tol 1.0 pp).
- **Recovery #2** (reviewer derivation §5 Step C(i) table at
  V=0.25, v=1, N=4, ρ=0, r ∈ {0.1, 1.0, 1.585, 2.512, 3.981, 10.0}):
  max |Δα|=0 (tol 5e-4), max |ΔR|=3e-6 (tol 5e-5). **PASS both axes.**
- **Step A** (closed-form `r†_inv` on primary grid, 420 cells):
  symmetric corner identity `r†_inv(V=1/N, v=1) = 1.0000` exactly at
  every (variant, ρ) — derivation §5 prediction confirmed.
- **Step B** (full α-sweep at 6 most-adversarial primary-sweep cells
  at r=10, both ρ; 12 probes): **zero global inversions** — C4 holds
  at ρ=0 AND under A1 (ρ=0.2).
- **Step C** (anti-cue at N=4, the rebuild's new evidence; 144 cells):
  **36.1% inversions at ρ=0 (26/72); 34.7% at ρ=0.2 (25/72).**
  r-stratified: 8% / 25% / 50% / 50% / 50% / 33% at r ∈ {0.1, 0.5,
  1, 3, 5, 10}. v-stratification follows the sharp boundary
  `V < 1/[(N-1)v+1]` (derivation §6 Eq. 6.4).
- **Step D** (α*(V, r) heatmap at v=5, N=4, both ρ; 544 cells): 2.2%
  inversion cells per panel, ALL at V=0.05, **zero cued-region
  inversions** — C4 holds as a conditional theorem.
- **Figures** (paths in artifacts list above): er_vs_alpha_anticue.png
  visualises the β/γ-swap kink and the anti-cue global inversion;
  alpha_star_V_r_map.png is the §results-C4 headline figure (white
  line at V=1/N, red contour at the α*<1/N boundary);
  r_inv_closed_form.png shows the closed-form threshold contour over
  (V, v) at both variants.

## What the manuscript can now say

At the strength licensed by the C4 row of `CLAIM_LEDGER.md` and
validated by rb-012, the §results-C4 section (RB-012, now unblocked)
may state:

1. C4 holds as a conditional theorem under `V ≥ 1/N, v ≥ 1` — verified
   globally across the 4,410-cell primary sweep at N=4 (Step B), and
   verified separately to survive A1 (ρ=0.2 leaves Step B 0 inversions
   and Step D 0 cued-region inversions intact).
2. The closed-form local threshold is `r†_inv = (N-1) A_0/B_0`, with
   the corner identity `r†_inv(V=1/N, v=1) = 1` exactly, independent
   of N, variant, and ρ — a numerically stable anchor.
3. Below `V = 1/N` the model produces global inversion `α* < 1/N` — a
   new falsifiable prediction of the rebuilt normative model. At
   `N = 4` (the paper's primary topology) **36.1% of probed anti-cue
   cells** exhibit inversion at ρ=0; the sharp boundary is
   `V < 1/[(N-1)v+1]` (universal worst-case `V < 1/N` at `v=1`).
4. A1 (ρ) does not abolish the inversion regime — ρ=0.2 shifts
   `r†_inv` quantitatively (median 13–21%) but leaves the qualitative
   inversion locus and incidence essentially unchanged. **The A1
   decorrelation channel and the C4 anti-cue inversion lever are
   independent mechanisms.**

The §5.5 inherited paper sentence on §4.5 ("regardless of r" wording)
is retracted in the rebuilt §results-C4 prose: correct as a global
empirical claim, incorrect as a local-derivative statement.

## Next increment

The natural next task is **RB-012** (§results-C4 manuscript section),
now unblocked. This would convert the rb-012 sim and CLAIM_LEDGER C4
row into manuscript voice (conditional theorem + closed-form local
threshold + anti-cue prediction + A1 independence), in parallel to
the rb-009 (§model), rb-007 (§results-C1), rb-006 (§results-C2), and
rb-011 (§results-C3) prose increments. After RB-012 the manuscript
will have four of five `§results-Cx` sections wired (C1, C2, C3, C4);
only the C5 appendix consistency (RB-013, low-priority, no sim
needed) remains in the "headline results" lane.

Alternative next picks if RB-012 is judged premature pending
RB-030 (derivation): **RB-014** (A2 heterogeneous-r model extension —
opens the A2/A8 heterogeneity thread; the C4 work above keeps `r`
homogeneous and so does not constrain this branch) or **RB-015** (A3
conservation-family model extension — orthogonal to both C4 and A2).

## Wiki cross-references

§11.1 keyword sweep on `{anti-cue, counter-predictive cue, inverted
attention, distractor suppression, statistical learning, no-inversion,
priority map, normative observer}` for the new manuscript prediction.
Hits, all already wired into research_db — no new stubs added:

- `wang_theeuwes2018_statistical_learning_distractor_suppression` —
  statistical-learning suppression as the behavioural analog of the
  anti-cue inversion prediction.
- `failing_theeuwes2018_selection_history` — review separating
  facilitatory capture from inhibitory suppression.
- `hickey2010_reward_salience_acc` — value-driven capture.
- `posner1980_orienting` — chance-validity baseline (V = 1/N).
- `bisley_mirpour2019_priority_map` — priority-map substrate.

audit.py not re-run (no wiki writes this run).
