# RB-021 — A8 N-dim uncued allocation sweep under the rebuild's added levers

**Run id:** rb-027 (2026-05-30) · **Output digest:** `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b` · **Wall clock:** ~72 s

## What this sim tests

The reviewer's `Critique/replications/A8--heterogeneous-uncued/run.py`
(CR-036) established that under the inherited (ρ=0, p=1) model, A8
(homogeneous-uncued allocation) is **innocuous at the model's own optimum**:
the full-simplex optimum coincides with the homogeneous-constrained one
to within the allocation-grid discretisation slack across every tested cell.

The rebuilt model adds two further levers that the A8 result has not been
tested against:

| Lever | Source | Notes |
|---|---|---|
| ρ — equicorrelated noise | A1 channel (rb-001 / rb-002 / rb-008) | Reviewer A8 sim was ρ=0 only. |
| p — conservation order | A3 family (rb-015 / rb-016 / rb-017) | Reviewer A8 sim was p=1 (additive) only. |

This sim lifts the CR-036 test to (ρ, p) ∈ {0, 0.2} × {1, 0} (the 2×2
joint cube) and asks: **does A8 ever begin to bind under the rebuild's
added levers?**

## Substrate

All policies are scored through `Rebuild/model/__init__.py er_full_policy`
(rb-020, sha256 `883ea15a…`, 7/7 PASS), which composes:

- `d_prime_hetero` (rb-019, byte-for-byte against `d_prime_asym`),
- `beta_gamma(r, p)` (rb-015, the power-mean conservation family),
- the one-factor Gauss-Hermite reduction for P_no-fa(ρ) (rb-001),
- the grouped-criterion optimiser `optimal_ER_general` (rb-020).

Recovery contracts:

- **rb-001** `test_recovery.py` (7/7 PASS, sha256 `d3c62215…`).
- **rb-015** `test_conservation_family.py` (14/14 PASS, sha256 `f4f57a89…`).
- **rb-019** `test_heterogeneous_r.py` (5/5 PASS, sha256 `0486921f…`).
- **rb-020** `test_general_policy.py` (7/7 PASS, sha256 `883ea15a…`).

All four contracts re-verified unchanged after this sim (the sim is a
pure consumer of `er_full_policy`; no model code touched).

## Three blocks

### Part 1c — full-simplex vs homogeneous optimum across (ρ, p)

Six cells (CR-036's "decisive_cells", verbatim) × ρ ∈ {0, 0.2} × p ∈ {1, 0}
= 24 panel evaluations. Each panel compares:

- `R_homog` — homogeneous-constrained optimum (α-grid step 0.005, uncued
  forced to (1−α)/(N−1) each);
- `R_full`  — unconstrained full-N simplex optimum (allocation grid step 0.05,
  heterogeneous uncued allowed).

`dR := R_full − R_homog`. A8 is said to **bind** if `dR > 1e-3` (above the
grid-discretisation slack) **and** `uncued_spread > 0.05`. The threshold is
identical to CR-036.

### Part 1 curvature — equal-split R″(0) along [+1, +1, −2]

Five cells (CR-036's Part-1 cell list trimmed for budget) × (ρ, p) panels
= 20 panel evaluations. At the homogeneous α*, compute the second derivative
of R along the symmetry-preserving redistribution direction [+1, +1, −2]:

- R″(0) < 0 ⇒ equal-split is a local max (A8 is locally robust).
- R″(0) > 0 ⇒ equal-split is a local min (A8 locally binds — the optimiser
  would concentrate the uncued budget).

### Part 2 — anti-cued graded suppression at ρ ∈ {0, 0.2}

Replicates CR-036 Part 2 (the Wang-Theeuwes statistical-learning link):
N=4, value-blind v=1, V=0.40, r=0.398, variant A. Loc 0 = cued (V), loc 3 =
anti-cued (validity w_anti ∈ {0.20, 0.175, …, 0.025, 0.0}), loc 1, 2 share
the remainder w_rest = (1 − V − w_anti)/2. Jointly optimise (a_cued, a_anti)
on a step-0.02 grid; report whether a_anti* declines monotonically with
w_anti AND whether a_anti* < a_rest* (strict suppression).

## Headline findings

### F1 — recovery PASS at (ρ=0, p=1)

The (ρ=0, p=1) panel of Part 1c reproduces the reviewer's CR-036 Part-1c
result exactly: **0/6 cells bind**, max `dR = 6.82×10⁻⁴` (below the
1×10⁻³ slack threshold). The maximum spread in the rebuild-replicated
panel is 0.300 at the symm-stress-r2 cell; CR-036 reports `unc_spread =
0.300` at the same cell. Recovery of the inherited A8-innocuous result
is structural.

### F2 — A8 **does** bind at (p=0, r=10, V=1/N) — a brand-new finding

At the `symm-stress-r10` cell (V=0.25 = 1/N, v=1, r=10, variant A) under
**multiplicative** conservation (p=0):

| panel | R_homog | R_full | dR | a_cued (full) | uncued_spread | binds? |
|---|---:|---:|---:|---:|---:|---:|
| ρ=0.0, p=0 | 0.67363 | 0.67643 | **+2.79×10⁻³** | 0.500 | 0.500 | **TRUE** |
| ρ=0.2, p=0 | 0.68110 | 0.68479 | **+3.68×10⁻³** | 0.500 | 0.500 | **TRUE** |

The full optimum splits attention as `a_cued=0.5` with uncued spread 0.5
(two slots get the bulk, one slot is zero). The homogeneous optimum sits
at `a_cued≈0.05` with all uncued slots equal. The conservation form
**changes the A8 binding** in this benefit-dominant high-r, value-blind
corner.

**ρ amplifies the binding by 32%**: dR(ρ=0.2) / dR(ρ=0) = 3.68 / 2.79 = 1.32.

At p=1 (additive), the same cell shows `dR = −1.38×10⁻³` (the full-simplex
optimum *underperforms* the homogeneous one by the grid-discretisation
slack) — the dR sign-flips under the conservation order, which is the
mechanism: at p=0 (multiplicative) `β·γ = 1` so `β = √r` and `γ = 1/√r`,
amplifying the gain branch at large r relative to p=1 additive (`β =
2r/(r+1) ≈ 2`, `γ ≈ 0`).

### F3 — R″(0) < 0 in 20/20 panels — equal-split is always a local max

Across the 5 × 4 = 20 (cell, ρ, p) panels of Part 1, the curvature R″(0)
along the symmetric redistribution direction is negative in every panel.
**Equal-split is a local maximum at the homogeneous α* in every tested
cell, regardless of (ρ, p)**. The F2 finding above is therefore a
**non-local A8 binding**: the homogeneous optimum is locally stable but
globally dominated by a far-away concentrated allocation (a_cued sits at
0.05 in the homogeneous panel, jumps to 0.50 in the full-simplex panel).

### F4 — ρ-amplification of |R″(0)| at p=1: small and non-uniform

| cell | |R″(0)|_ρ=0 | |R″(0)|_ρ=0.2 | ratio |
|---|---:|---:|---:|
| v1-cost-dom | 2.261 | 2.462 | 1.089 |
| v1-reference | 1.318 | 1.496 | 1.135 |
| v1-symmetric | 1.750 | 1.647 | **0.941** |
| v1-benefit-dom | 141.0 | 146.8 | 1.041 |
| v1-lowV | 2.269 | 2.347 | 1.035 |

Mean ratio = 1.048, max = 1.135. The rb-021/A2 finding that "ρ amplifies
the criticality residual by ~2×" **does NOT generalise to the A8 N-dim
uncued question**: amplification is small (< 1.14×) and non-uniform
(v1-symmetric *suppresses* by 6%). A1 and A8 compose more orthogonally
than A1 and A2 do.

### F5 — anti-cued graded suppression survives ρ=0.2

At both ρ panels, the optimal a_anti* declines **monotonically** as the
anti-cued slot's validity w_anti drops from 0.20 to 0.00, and **stays
strictly below** a_rest* in every w_anti tested. ρ=0.2 only weakly
perturbs the gradient: it delays the w_anti at which a_anti collapses to
zero (ρ=0: w_anti ≈ 0.075 ⇒ a_anti = 0; ρ=0.2: w_anti ≈ 0.050 ⇒ a_anti =
0), consistent with the A1 channel preserving rather than abolishing the
suppression mechanism. The Wang-Theeuwes statistical-learning suppression
link of CR-036 Part 2 thus **generalises across the rebuilt model's
correlation channel**.

## Reproducibility

- **Deterministic digest**: `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b`
  — sha256 of the canonical (sort_keys, indent=2) JSON dump of `results`
  with `wall_clock_seconds` removed. Verified byte-identical across reruns.
- **Canonical bytes** persisted alongside the human-readable dump as
  `output/results.canonical.json` so a verifier can re-compute the sha256
  without re-running the sim.
- **Pre-computed digest** persisted as `output/results.json.deterministic_sha`.
- **No randomness**: this is a deterministic numerical sim. The only
  "randomness" comes from grid resolution (alpha 0.005, c 0.05, full-simplex
  0.05, anti-cued 0.02).
- **Recovery contracts** (model-test sha256 unchanged after sim):
  `d3c62215…` (rb-001) · `f4f57a89…` (rb-015) · `0486921f…` (rb-019) ·
  `883ea15a…` (rb-020).

## Figures

- `output/figures/a8_simplex_dr.png` — dR (full − homog) bar chart across
  cells × (ρ, p). The F2 binding shows as the two red bars at
  symm-stress-r10 under p=0.
- `output/figures/a8_curvature.png` — R″(0) heatmap across (cell, ρ),
  one panel per p. All cells negative (red below the white = 0 line).
- `output/figures/a8_anticued_suppression.png` — a_anti* and a_rest* vs
  w_anti, one panel per ρ. The graded-suppression curve.

## Scope

- **A2 vs A8 compositional asymmetry**: the rb-021 (A2) sim found
  ρ-amplification of ~2× on the equal-split criticality residual. F4
  here shows that finding does NOT generalise to A8 — the A8 R″(0)
  curvature responds much less to ρ. The two heterogeneity assumptions
  (per-location r_i vs per-location uncued allocation) compose with
  the A1 channel differently.

- **Conservation-form dependence of A8 binding**: F2 is, to our knowledge,
  the first quantitative statement that A8 binds at all in this model
  family. The binding emerges at p=0 (multiplicative) but NOT at p=1
  (additive). This is the cleanest single rebuild contribution over
  CR-036's "A8 innocuous everywhere" headline — the rebuild model's
  joint (p × A8) sweep reveals an A8 binding that the inherited
  conservation rule structurally hid.

- **Recovery scope**: F1 is the universal-statement guarantee for the
  manuscript's §extensions-A8 subsection — the inherited model
  reproduces, and the new findings are additive to it.

- **Variant B**: variant A only. CR-036's `C1-contested-cnr` row is the
  one variant-B cell tested; dR < 0 in all four (ρ, p) panels (≤
  −2.28×10⁻³) so the spread A8 binding is variant-A-specific in the
  tested set. A focused variant-B replication is queued as a follow-up.

- **r-grid resolution**: the p=0 binding at r=10 is on a discrete r-grid
  shared with CR-036. The rb-016 / rb-019 r-grid (21-point log) does not
  include r=10 as a separately-tested anchor; the closest cell is the
  symm-stress cell tested here. A finer r-grid around r ∈ {5, 10, 20}
  to bracket the p=0 binding onset is queued as a follow-up.

## Cross-links

- **CR-036** (`Critique/replications/A8--heterogeneous-uncued/`) — the
  reviewer's ρ=0 / p=1 baseline this sim extends.
- **rb-020** (`Rebuild/model/`) — the `er_full_policy` driver this sim
  consumes.
- **rb-016** (`Rebuild/sims/A3--conservation-band/`) — the conservation
  family's effect on C1/C2 headline numbers; F2 is the first conservation-
  band finding on A8.
- **rb-021** (`Rebuild/sims/A2--heterogeneous-r/`) — the A2 heterogeneity
  sim whose ρ-amplification F4 fails to generalise to A8.
- **A8 verdict** (`Critique/verdicts/A8--heterogeneous-uncued.md`) — the
  live ledger row (CONFIRMED-CONDITIONAL); F2 is the first finding to
  add a conditional to the rebuild's A8 row beyond CR-036.
