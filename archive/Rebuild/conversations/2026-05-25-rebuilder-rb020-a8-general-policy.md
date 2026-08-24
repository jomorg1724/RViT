---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-020-2026-05-25
started: 2026-05-25T22:00:00Z
ended: 2026-05-25T22:55:00Z
worked_on: RB-017
output_kind: model
claims_touched: [A8, A2, A3, A1]
artifacts_written:
  - Rebuild/model/core.py (added optimal_ER_general, er_full_policy, homogeneous_validity, helpers _hr_omf_grids, _omf_grid_correlated)
  - Rebuild/model/__init__.py (re-exports er_full_policy, homogeneous_validity, optimal_ER_general)
  - Rebuild/model/tests/test_general_policy.py (NEW; 7 tests, 9,985 cells, sha256 883ea15a…)
  - Rebuild/model/tests/general_policy_output.json (NEW)
  - Rebuild/model/README.md (extended to four extension axes; full A8 recovery-test row)
  - Rebuild/CLAIM_LEDGER.md (A8 row rewritten; A2 tail updated)
  - Rebuild/REBUILD_BACKLOG.md (RB-017 done; follow-up implications noted)
  - Rebuild/BUILD_LOG.md (run entry body)
  - Rebuild/rebuilder_state.json (atomic update)
papers_added: []
spawned_tasks: []   # RB-018 and RB-021 already exist; unblocked rather than spawned
---

# rb-020 — A8 N-dim uncued allocation policy/optimiser (RB-017)

## What I built

The rebuilt model module gained a fourth extension axis: **A8 N-dim
heterogeneous allocation**, exposed as the grouped-criterion optimiser
`optimal_ER_general(d_vec, wu_vec, n_vec, CR, rho)` and the full-policy
driver `er_full_policy(alloc, valid, v, r_vec, cell)` (`Rebuild/model/
core.py`). Both compose cleanly with the three earlier extensions:

- **A1 (rho channel, rb-001).** The joint no-FA probability is the
  one-factor Gauss-Hermite integral
  `INT prod_g Phi((c_g + d_g/2 - sqrt(rho) z)/sqrt(1-rho))^{n_g} phi(z) dz`,
  evaluated with the same `(_GH_Z, _GH_W)` quadrature `p_no_fa_grid`
  uses.
- **A2 (heterogeneous-r d'-map, rb-019).** Per-location d' comes from
  `d_prime_hetero(alloc, r_vec, ..., p)`; `r_vec` can be an N-vector or
  a scalar broadcast.
- **A3 (conservation family, rb-015).** The conservation order
  `cell.cons_p` flows through `beta_gamma(r_i, p)` at each location,
  giving the same band-of-conservation-rules behaviour the homogeneous
  pipeline exposes.

The grouped form folds locations sharing both `(d_i, w_i u_i)` into a
single group with multiplicity `n_g`; by symmetry of the reward, group
members share an optimal `c_g`, so the inner criterion optimisation is
G-dimensional rather than N-dimensional. The optimiser switches mode by
group count: exact 1-D argmax over `C_GRID` at G=1; exact 2-D argmax
over `C_GRID × C_GRID` at G=2 (same machinery as the homogeneous
`optimal_R`, generalised by the `n_g` exponents); multi-restart
coordinate ascent from `2^G + 1` seeds at G≥3 (each restart sweeps
1-D-per-group exact-argmax until criteria stop changing).

This lifts the reviewer's A8 grouped-criterion machinery
(`Critique/replications/A8--heterogeneous-uncued/run.py`, CR-036,
run-012, validated by the A8 verdict) into the rebuilt module with
three structural extensions over the reviewer's substrate: the **rho
channel** (the reviewer's A8 code uses ρ=0 only), the **conservation
order p** (the reviewer's A8 code uses additive only), and a **wider
criterion grid** (the rebuilt module's `C_GRID = [-3, 3] step 0.05`
vs the reviewer's `[-2.5, 2.5] step 0.05`).

## How it connects to the ledger

**A8 (live: CONFIRMED-CONDITIONAL).** The §3.2 mission directive for
A8 is: "state the homogeneity result as conditional, and present the
N-dimensional heterogeneous-uncued policy space as the honest
generalisation. Sim: reuse `Critique/replications/A8--heterogeneous-
uncued/run.py`." rb-020 discharges the model-side prerequisite: any
N-dim allocation, any heterogeneous validity, any per-location r_vec,
any rho, any conservation order p can now be scored via
`er_full_policy`. The rebuilt strength is unchanged (the A8 condition
itself stands at CONFIRMED-CONDITIONAL); what changed is that the
*generalisation* is now mechanically available in the rebuilt module,
not just in the reviewer's external script.

**A2 (live: CONFIRMED-CONDITIONAL).** The rb-019 (RB-014) note
explicitly deferred the downstream wiring: "Downstream pipeline
(P_no_fa, optimal_R, policies) remains scalar in (d_c, d_u); promoting
it to the full heterogeneous regime is RB-017's task." That deferral
is now closed: `er_full_policy(alloc, valid, v, r_vec, cell)` accepts
an N-vector `r_vec` and threads it through `d_prime_hetero` into the
joint no-FA integral and the criterion optimisation. The A2 row of
CLAIM_LEDGER has been updated to point at this driver as the
heterogeneous-r scoring path.

**A3 (live: CONTESTED).** No new claim; the conservation order
threading is a pure preservation of rb-015's contract through the new
machinery. TEST 4 of the new recovery suite confirms `p ∈ {0, 0.5,
1.0}` all flow correctly.

**A1 (live: CONTESTED).** No new claim; the rho channel passes through
the joint integrand identically to `p_no_fa_grid`'s reduction. TEST 2
of the new recovery suite confirms ρ=0.2 routes through the GH path on
both sides and agrees to 2.78e-10.

## Simulation evidence

**Recovery contract** (`Rebuild/model/tests/test_general_policy.py`,
9,985 evaluations across 7 tests, sha256
`883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39`):

| TEST | scope | n_cells | max\|d\| | tol | result |
| --- | --- | --- | --- | --- | --- |
| 1 | ρ=0 recovery, full α grid × {r in 5} × {V in 3} × {v in 2}, variant A, p=1 | 4,530 | 2.77e-10 | 1e-9 | PASS |
| 2 | ρ=0.2 recovery, same grid | 4,530 | 2.78e-10 | 1e-9 | PASS |
| 3 | variant B (CR=1), headline cell, α grid × {ρ in {0, 0.2}} | 302 | 1.19e-10 | 1e-9 | PASS |
| 4 | conservation family p ∈ {0, 0.5, 1.0}, ρ=0, variant A, α grid | 453 | 2.11e-10 | 1e-9 | PASS |
| 5 | grouping/method check (G=1 / G=2 / G=2 branches) | 3 cells | — | — | PASS |
| 6 | r_vec = [r,r,r,r] scalar broadcast equivalence, ρ ∈ {0, 0.2} | 186 | 0.0 | 1e-9 | PASS |
| 7 | G=4 multi-restart smoke check on heterogeneous validity | 1 | finite | — | PASS |

The 1e-9 tolerance (versus the rb-019 `d_prime_hetero` byte-for-byte
contract) is the **structural wu-reconstruction error** the grouped
form introduces: `n_u · wu_u = (N-1) · ((1-V)/(N-1))` evaluates in two
float operations that do not reconstruct `(1-V)` exactly when
`(1-V)/(N-1)` is not representable, e.g. `(1-0.5)/3 = 0.16666…64` and
`3 · 0.16666…64 ≈ 0.4999…996`. The legacy `optimal_R` writes
`(1-V) · hr_u` directly, so the inner reward off by ULP × cell-value
gives the observed ~3e-10. This is documented in the test docstring
and is six orders of magnitude tighter than any reported manuscript
number, so it is recovery-quality. TEST 6 confirms there is no
additional slack introduced by promoting scalar r to an N-vector
broadcast (max|d|=0.0 to floating-point identity, because
`d_prime_hetero` with uniform `r_vec` already matches `d_prime_asym`
byte-for-byte from rb-019).

**Pre-existing recovery tests re-run.** All three earlier recovery
contracts hold with their original digests unchanged:

- `test_recovery.py` (rb-001 A1 ρ-channel): 7/7 PASS, sha256
  `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`
  unchanged.
- `test_conservation_family.py` (rb-015 A3): 14/14 PASS, sha256
  `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`
  unchanged.
- `test_heterogeneous_r.py` (rb-019 A2): 5/5 PASS, sha256
  `0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`
  unchanged.

The rb-020 increment is **purely additive** to the existing public
surface — no behavioural change to `policies`, `optimal_R`,
`p_no_fa_grid`, `d_prime_asym`, `d_prime_hetero`, or `beta_gamma`.

## What the manuscript can now say

This is a model-only increment; no manuscript section is drafted this
run. The rebuilt §extensions-A8 subsection (a future RB-NN increment)
can state:

> "We score policies over the full N-dimensional allocation simplex via
> a grouped-criterion optimiser (`er_full_policy` in §methods), which
> composes the A1 decorrelation channel, the A3 conservation family,
> and the A2 heterogeneous-r d'-map at no additional cost. Recovery
> contract: under the inherited homogeneous reduction the optimiser
> reproduces `optimal_R(d_c, d_u, ...)` to 1e-9 absolute across the
> headline α × r × V × v × variant × ρ × p grid (9,985 cells, max|d|
> = 2.78e-10; see `Rebuild/model/tests/test_general_policy.py`)."

The §extensions-A8 quantitative content (how does the A8 condition
fare beyond the reviewer's headline-cell numerics? does the suppression
gradient generalise?) is the RB-021 sim's job. The §extensions-A2
content (do C2 non-monotonicity and C1 CF distribution survive
heterogeneous r_i?) is the RB-018 sim's job. Both sims can now run
against the rebuilt module's machinery directly rather than re-using
the reviewer's substrate.

## Next increment

**RB-018 (A2 heterogeneous-r sweep)** is the natural next pick. Its
prereq RB-014 was already done; the rb-019 note had implicitly deferred
it pending the downstream pipeline (now in place). RB-018 answers the
A2 row's headline empirical question — "do the C2 non-monotonicity and
the C1 CF distribution survive heterogeneous r_i?" — and feeds a
manuscript §extensions-A2 subsection that mirrors §extensions-A3.

**RB-021 (A8 N-dim uncued sweep)** is the parallel pick. The A8 verdict
already establishes the headline-cell innocuity; the sim's job is to
extend this beyond the headline cell (anti-cue regime, heterogeneous
validity, accelerating-h cells where the live verdict §re-derivation
flags the smooth-Hessian flip).

Lower-priority parallel options: RB-024 (C1 closed-form CF<0.5
boundary), RB-026 (C2 r†(v;ρ) closed form), RB-033 (A3 formal
derivation in the rebuild's voice).

## Wiki cross-references

Wiki sweep performed for keywords {N-dim allocation, grouped criterion,
coordinate ascent, equicorrelated Gaussian, joint no-false-alarm,
power-mean conservation, heterogeneous r, anti-cue, Wang-Theeuwes
suppression gradient}. No new `research_db/papers/` stubs added:

- The A8 reviewer-substrate citations (CR-036 / run-012 / `Critique/
  replications/A8--heterogeneous-uncued/run.py`) are internal to the
  Critique/ tree.
- The A8 behavioural-literature citations
  (`wang_theeuwes2018_statistical_learning_suppression`,
  `wang_samara_theeuwes2019`, `kong_li_wang_theeuwes2020`,
  `failing_theeuwes2018`, `hickey2010`, `posner1980`) were stubbed in
  rb-012/rb-013 (RB-008/RB-012) for the §results-C4 section and are
  cited by name in `Rebuild/manuscript/refs.bib`; no new stub work is
  required.
- The math-methods gap (Slepian 1962, Tong 1990, HLP 1934, Sterbenz
  1974, Goldberg 1991) inherited from rb-008/rb-014/rb-015/rb-018
  remains; same scope decision (cited by full bibliographic reference,
  research_db stubs deferred to the reviewer's CR-035/CR-037 backlog).

No `audit.py` re-run (no wiki writes).

---

## Verification performed

- All 4 recovery-test suites pass:
  `test_recovery.py` 7/7 (sha256 `d3c62215…` unchanged),
  `test_conservation_family.py` 14/14 (sha256 `f4f57a89…` unchanged),
  `test_heterogeneous_r.py` 5/5 (sha256 `0486921f…` unchanged),
  `test_general_policy.py` 7/7 (sha256 `883ea15a…`, NEW).
- TEST 1+2 (rho ∈ {0, 0.2}) confirm the rho-channel composition is
  numerically clean across 9,060 cells.
- TEST 5 confirms the grouping logic correctly distinguishes G=1 from
  G=2 (alpha = 1/N with V ≠ 1/N stays G=2 because wu differs even
  though d collides) and exercises the exact 1-D and 2-D paths, never
  silently falling into coord-ascent for cases the exact path covers.
- TEST 6 confirms scalar-r and uniform-r-vector are byte-identical
  through `d_prime_hetero` (carries the rb-019 contract through to the
  new policy layer).
- TEST 7 confirms the G≥3 multi-restart path runs and returns a finite,
  sensible reward on the only construction that forces G=4 (per-location
  validity (0.4, 0.3, 0.2, 0.1)).
- Pre-existing module-level digest checks all pass; the rb-020
  increment is purely additive — no behaviour of any existing public
  surface (policies, optimal_R, d_prime_asym, d_prime_hetero,
  beta_gamma, p_no_fa_grid, p_no_fa_point) changed.

## Extensions to consider

- A6 attention-coupled decision noise (if A6 lands at CONTESTED): the
  `er_full_policy` driver is the natural home for a per-location
  decision-noise scaling σ_i(α), folded into the d'_i scaling. Wait
  for the live verdict.
- Anti-cue regime (alpha < 1/N): the `d_prime_hetero` per-slot
  gain/loss branch already handles alpha < 1/N; `er_full_policy`
  inherits this via the d'-map. RB-021 (A8 sim) can probe the anti-cue
  regime directly without further model wiring.
- Structured Σ (non-equicorrelated, block-covariance): the joint
  no-FA integral as written uses the one-factor reduction; a
  block-covariance extension would need a multi-dim quadrature. Out of
  scope for now.
