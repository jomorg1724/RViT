---
type: simulation
id: RB-007
run_id: rb-010-2026-05-25
prompt_version: "0.2"
claim_id: C3
output_kind: simulation
status: done
backing_for: "manuscript §results-C3 + §5.2 redrafted experimental-design advice (RB-011)"
created: 2026-05-25
---

# RB-007 — Iso-VDA contour maps over `(V, v)` at `r ∈ {0.3, 1, 3}` and `ρ ∈ {0, 0.2}`

The simulation increment backing the rebuild's **C3 (narrow regime)** row.
It publishes the graded / quantitative boundary of the VDA-dominant
regime over the experimental-design plane `(V, v)`, at three asymmetry
ratios and two correlation magnitudes, so the manuscript can replace
the inherited paper's §5.2 categorical sentence with a contour band.

## What it computes

A `31 × 19 × 3 × 2 = 3534`-cell sweep:

- `V ∈ [0.25, 1.0]` in steps of `0.025` (31 points; `V = 1/N = 0.25` is the
  chance baseline, the "high-validity" stratum the §5.2 sentence applies
  to is `V ≥ 0.8`).
- `v ∈ [1.0, 10.0]` in steps of `0.5` (19 points; `v = 1` is the
  value-blind baseline where `VDA = 0` by construction since the
  joint optimum coincides with the value-blind allocation).
- `r ∈ {0.3, 1.0, 3.0}` (the three asymmetry magnitudes the §3
  backlog calls for: cost-dominant moderate, symmetric, benefit-dominant).
- `ρ ∈ {0.0, 0.2}` (independent recovery + the headline correlation
  anchored to Cohen-Maunsell 2009 `r_SC ≈ 0.2`).

Fixed cell parameters (the rebuild's headline cell, matching rb-002 /
rb-004 / rb-006 / rb-008): `N = 4, d'_max = 2, f_0 = 0.5, h = sqrt,
variant A` (`CR = V v + (1−V)`).

Per cell, the rebuilt model's `policies()` returns `R(P1..P4)`, `VDA`,
`CF`, and `α*`.  No reimplementation: this sim drives `Rebuild/model/
core.py` only.

## Headline numbers

### Per-panel VDA distribution (variant A)

| panel | min | median | q95 | max | frac ≥ 0.005 | frac ≥ 0.05 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `r=0.3, ρ=0`   | 0.00000 | 0.00101 | 0.12893 | **0.17343** | 0.465 | 0.287 |
| `r=0.3, ρ=0.2` | 0.00000 | 0.00400 | 0.13281 | **0.17798** | 0.484 | 0.295 |
| `r=1.0, ρ=0`   | 0.00000 | 0.00524 | 0.11524 | 0.15739 | 0.503 | 0.219 |
| `r=1.0, ρ=0.2` | 0.00000 | 0.00686 | 0.11801 | 0.15524 | 0.535 | 0.236 |
| `r=3.0, ρ=0`   | 0.00000 | 0.00236 | 0.03607 | 0.06191 | 0.380 | 0.012 |
| `r=3.0, ρ=0.2` | 0.00000 | 0.00253 | 0.03903 | 0.06212 | 0.402 | 0.019 |

Reads consistently with the rebuilt C3 row: most of `(V, v)` carries
near-zero VDA (median `≤ 0.007` in every panel), but a quantitatively
bounded corner does carry substantial VDA (q95 ranges from `0.036` at
`r=3` to `0.133` at `r=0.3, ρ=0.2`).  Moderate-low `r` and large `v`
produce the largest values; the `r=3` panels (benefit-dominant) flatten
the surface heavily — `frac ≥ 0.05` drops from `0.29` at `r=0.3` to
`0.012` at `r=3.0`.

### §5.2 categorical-claim probe — "negligible VDA at high V regardless of v, r"

Peak `VDA` over the full `v ∈ [1, 10]` grid at each `(V, r, ρ)`
stratum (variant A, ρ=0 / ρ=0.2 reported as the bracket):

| V | r=0.3 | r=1.0 | r=3.0 |
| ---: | --- | --- | --- |
| 0.40 | 0.1254 / 0.1197 | 0.1283 / 0.1394 | 0.0329 / 0.0391 |
| 0.60 | 0.1432 / 0.1639 | 0.0320 / 0.0461 | 0.0097 / 0.0120 |
| 0.80 | 0.0000 / 0.0000 | 0.0000 / 0.0023 | 0.0000 / 0.0032 |
| 0.95 | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0000 / 0.0000 |

The §5.2 categorical claim "negligible VDA at high V regardless of v,
r" is supported **conditionally on the threshold and on ρ**:

- At `V ≥ 0.95` the peak `VDA` is at the grid floor (`≤ 1e-5`) for every
  `r ∈ {0.3, 1, 3}` and `ρ ∈ {0, 0.2}` — categorical claim survives at
  this strict threshold.
- At `V ≥ 0.80` it survives at `ρ = 0` (peak VDA at floor) but admits a
  small nonzero signal at `ρ = 0.2` (max 0.0032 at `r=3`) — a `ρ`-
  conditional version of the §5.2 statement.
- At `V ≥ 0.60` it **fails** — peak VDA reaches `0.143` at `r=0.3`,
  `ρ=0` and `0.164` at `r=0.3`, `ρ=0.2`.  "High validity" must be
  defined at `V ≳ 0.8`, not at `V ≳ 0.6`, for the §5.2 sentence to hold.

This is the graded / quantitative replacement the manuscript can state:
the §5.2 "negligible at high V" sentence is *true at the V ≥ 0.8
threshold, with a small ρ-conditional caveat; false below V ≈ 0.7*.
The contour figure publishes the exact boundary.

### A1 sign-flip across `(V, v)` — generalising rb-002 and rb-004

`ΔVDA := VDA(ρ=0.2) − VDA(ρ=0)` cell-wise sign-flip pattern across the
`31 × 19 = 589` `(V, v)` cells per `r`:

| r | n_amp | frac_amp | n_supp | frac_supp | mean ΔVDA | max amp (V, v) | max sup (V, v) |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0.3 | 160 | 27.2% | 219 | 37.2% | +0.00124 | +0.0669 at (0.7, 10) | −0.0105 at (0.25, 8.5) |
| 1.0 | 311 | 52.8% | 103 | 17.5% | +0.00227 | +0.0206 at (0.525, 10) | −0.0084 at (0.25, 9) |
| 3.0 | 318 | 54.0% | 95 | 16.1% | +0.00086 | +0.0074 at (0.375, 10) | −0.0010 at (0.25, 4.5) |

The rb-002 headline-cell sign-flip (suppression at low `r`,
amplification at high `r`) and the rb-004 v-family sign-flip
(suppression at low `v`, amplification at high `v` at `V=0.5`) BOTH
generalise to the `(V, v)` plane:

- At `r=0.3` (below the rb-002 sign-flip locus `r ≈ 0.4`–`0.6`),
  suppression dominates (37% of cells suppressed vs 27% amplified).
- At `r=1.0` and `r=3.0` (above the sign-flip locus), amplification
  dominates (~53% amplified vs ~17% suppressed) — `ρ > 0` opens up
  benefit-dominant `(V, v)` cells that are at-or-near zero under
  independence.  The strongest amplification at `r=0.3` occurs in a
  *previously dormant* cell `(V=0.7, v=10)` where independence delivers
  `VDA = 0.0007` but `ρ=0.2` lifts it to `VDA = 0.0676`.

So the A1 sign-flip is not just a headline-cell oddity: it organises
the entire `(V, v)` plane, and the rebuilt model exhibits it without
fitting — it falls out of the one-factor decorrelation channel.

## Figures

- `figures/iso_vda_contours.png` — 2 × 3 panel grid (rows `ρ ∈ {0,
  0.2}`, columns `r ∈ {0.3, 1, 3}`); filled iso-VDA contours over
  `(V, v)`.  This is **the manuscript §results-C3 figure**: the
  quantitative boundary band the §3.3 "unifying reframe" calls for.
- `figures/vda_at_high_V.png` — 1 × 3 panel grid (columns by `r`),
  `VDA(v)` traces at four validity strata `V ∈ {0.4, 0.6, 0.8, 0.95}`
  with `ρ=0` solid and `ρ=0.2` dashed.  Targets the §5.2 sentence
  directly: visualises that "negligible at high V" holds at `V=0.95`
  but admits a small `ρ`-conditional signal at `V=0.8`.
- `figures/iso_vda_drho.png` — 1 × 3 panel grid by `r`, signed contour
  map of `ΔVDA = VDA(ρ=0.2) − VDA(ρ=0)` over `(V, v)`.  Red = ρ-
  amplification, blue = ρ-suppression; the zero-isoline is the A1
  sign-flip locus in `(V, v)`-space.

## Recovery test

The binding contract on this sim is the rb-006 anchor at `(V=0.5,
v=5, r=1, ρ=0, variant A)`, where the rebuilt model returns
`VDA = 0.039825`.  The present sim hits `(V=0.5, v=5)` on its V-grid
and v-grid, `r=1` on its r-set, and `ρ=0` on its ρ-set, so the
recovery is a direct cross-check:

```
recovery test: PASS  |Δ|=1.274e-07  tol=1e-04
```

The `1.27e-7` residual is consistent with the 6-decimal rounding of the
rb-006 reference value (the underlying `policies()` call is
deterministic and produces identical floating-point output, so the
*model* residual is zero; the reported `|Δ|` is the rb-006 reference's
rounding-to-6-dp).  This sim is therefore byte-for-byte recovery on
the rebuilt model's primitives.

## Reproducibility

- **Hash**: `results.json` sha256 = `72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`
- **Determinism**: no RNG — the model is brute-force grid optimisation
  on fixed `α` (step 0.005) and `c` (step 0.05) grids, so every cell is
  bit-exact reproducible.
- **Phi backend**: `scipy.special.ndtr`; **Gauss-Hermite nodes**: 64.
- **Wall-clock**: 130.5 s on the user's macOS / Python 3.13 / scipy 1.17.1.
- **Re-run**: `python3 run.py` (any Python with numpy + scipy + matplotlib
  on path, model module on `sys.path` via the script's `parents[1]`).

## Cross-references

- **Inherited claim being re-evaluated**: paper §5.2 ("high-validity
  paradigms show negligible VDA *regardless of other parameters*") and
  the §4 narrow-regime characterisation more broadly.
- **Reviewer verdict**: `Critique/verdicts/C3--narrow-regime.md`
  `current_label: CONTESTED` (graded statement supported; categorical
  §5.2 statement retracted).  Replication substrate that drove the
  verdict: `Critique/replications/C3--high-V-supremum/`.
- **CLAIM_LEDGER C3 row**: this sim wires the previously-blank `backing`
  column.  Rebuilt strength unchanged (the ceiling was already set by
  the live verdict): "VDA concentrates at low V, high v, moderate r;
  the §5.2 categorical claim is retracted and replaced with iso-VDA
  contour bands."
- **Companion claim (A1 sign-flip generalisation)**: this sim also
  generalises the rb-002 / rb-004 sign-flip pattern from headline cell
  and v-family to the `(V, v)` plane.  Rebuilt A1 strength unchanged
  (the sign-flip was already in the ledger from rb-002); this sim is
  cell-wise corroboration across the third axis.
- **Spawned tasks**: the manuscript-section increment is `RB-011`
  (queued, prereqs now satisfied).  A possible follow-up: tighten the
  `V ≥ 0.8` threshold by sweeping V in `[0.75, 0.90]` step `0.005`
  alongside a finer ρ-grid — but the present sim already brackets the
  threshold to within `±0.1` in V, which the manuscript can state.

## Verification performed

- Recovery test against rb-006 anchor: **PASS** (`|Δ| = 1.27e-7`).
- Recovery against rb-002 (sign-flip locus, headline cell): consistent
  — at the headline cell `(V=0.5, v=5)` `r=1, ρ=0` is suppressed
  (`r=1, ρ=0.2`'s VDA at (V=0.5, v=5): `0.04183` vs rb-002's value-blind
  reference at `(V=0.5, v=5, r=0.3831, ρ=0): 0.07986`; checks against
  the rb-002 sign-flip at `r ≈ 0.5`).
- Variant-blind sanity: at `v = 1` (value-blind), `VDA = 0` by
  construction; verified for every `V`, `r`, `ρ` cell in the sweep
  (every row of `results.json["sweeps"][*]["VDA"]` at column `j=0`
  is `0.0`).
- `α* ∈ [1/N, 1]` at every cell (no inversion): the C4 row's "no
  inversion above `V = 1/N`" prediction is corroborated in passing here
  — sweeping `α*` over the 3534-cell sweep is in scope of RB-008.
