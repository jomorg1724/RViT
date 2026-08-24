# `Rebuild/model/` — the rebuilt VDA model (v2)

## What this is

The canonical model implementation for the rebuilt Herman-Lab VDA paper.
It extends the inherited model (`Critique/source/main.pdf`,
2026-04-09) along **four axes** so far:

1. **A1 (rb-001).** Per-location decision independence is promoted to a
   tunable equicorrelation parameter `rho`. The inherited independent
   case is recovered exactly at `rho = 0`.
2. **A3 (rb-015).** The conservation rule `beta + gamma = 2` (paper's
   additive A3) is generalised to a **power-mean conservation family**
   with parameter `cons_p`. The inherited additive case is `cons_p = 1`
   (default, byte-exact back-compat); the multiplicative alternative
   `beta * gamma = 1` is `cons_p = 0`.
3. **A2 (rb-019).** The global benefit/cost asymmetry `r` is promoted
   to a per-location ratio vector `r_i`, exposed through
   `d_prime_hetero(alloc, r_vec, ...)` (the heterogeneous-r d'-map).
   The inherited single-`r` model is recovered byte-for-byte under
   uniform `r_vec` and the canonical homogeneous allocation.
4. **A8 (rb-020).** The 1-D allocation space (`alpha` for the cued
   slot, uniform `(1-alpha)/(N-1)` on each uncued slot) is promoted to
   the full N-dim allocation simplex. Scored via `er_full_policy(alloc,
   valid, v, r_vec, cell)` — the rho-aware grouped-criterion optimiser
   that composes cleanly with all three prior extensions. The inherited
   homogeneous case is recovered to **1e-9 absolute** (the gap is the
   ULP-level wu-reconstruction error `(N-1)·((1-V)/(N-1)) − (1-V)`;
   any sweep this drives reports headline numbers to no better than
   four decimal places, so 1e-9 is six orders of magnitude past
   sensitive).

All four extensions are gated by recovery tests under `tests/`. This
file documents what is in the module, what changed vs. the inherited
model, and the contract every future extension must satisfy.

## What changed vs. the inherited model

Inherited model (paper Eq. 9) — per-location SDT decisions are
independent on a no-change trial, so the joint no-false-alarm
probability is

```
P_no-fa^indep = Phi(b_c) * Phi(b_u)^(N-1)
```

with `b_i = c_i + d'_i / 2`. The skeptical reviewer's A1 verdict
(CONTESTED, run-017, `Critique/verdicts/A1--independence.md`) showed
this is empirically the wrong corner: cross-location noise correlations
are substantial in the paper's own paradigm
(`cohen_maunsell2009_correlations`, `r_SC ~ 0.2`), and the §5.5
"upper bound on VDA" self-characterisation fails as a uniform statement
— `dVDA/drho` flips sign near `r ~ 0.5`, with positive correlation
**amplifying** VDA in the benefit-dominant regime (`r >~ 0.5`) by up to
~20%, while suppressing it cost-dominant. Independence instead
upper-bounds the criterion fraction.

The rebuilt model replaces Eq. 9 with the exact equicorrelated-Gaussian
orthant probability,

```
P_no-fa(rho) = INT  Phi((b_c - sqrt(rho) z) / sqrt(1 - rho))
                  * Phi((b_u - sqrt(rho) z) / sqrt(1 - rho))^(N-1)
                  * phi(z) dz
```

evaluated by 1-D Gauss–Hermite quadrature (`nq = 64`, exact to ~1e-16
vs. `nq = 128`). The change-trial term is *linear* in marginal hit
rates and so independence enters in exactly this one place — this is
the "Booking 1" decomposition from
`Critique/derivations/A1--correlated-fa-upper-bound.md`. ("Booking 2",
a pooled-`d'` global rule, is assumption A6, not A1, and is not in this
module.)

### A3 conservation family (rb-015)

The paper fixes `beta + gamma = 2` (`beta = 2r/(r+1)`, `gamma = 2/(r+1)`).
The reviewer's A3 verdict (CONTESTED, run-011) shows that swapping to
the multiplicative alternative `beta * gamma = 1` roughly doubles the
criterion-subordinate fraction (4.0% → 8.3% of 4,410 cells). The
rebuilt model therefore treats conservation as a tunable parameter
rather than a fixed assumption.

We use the **power-mean conservation family** of order `p` indexed by
`cons_p`. The constraint is `M_p(beta, gamma) = 1` together with
`beta/gamma = r`; the closed-form solution is

```
gamma(r, p) = (2 / (r^p + 1))^(1/p),   beta(r, p) = r * gamma   (p != 0)
gamma(r, 0) = 1/sqrt(r),                beta(r, 0) = sqrt(r)     (p = 0)
```

Special cases recovered exactly:

| `p` | M_p | constraint | (beta, gamma) at `r = beta/gamma` |
| --- | --- | --- | --- |
| 1 | arithmetic | `beta + gamma = 2` (additive A3, paper) | `(2r/(r+1), 2/(r+1))` |
| 0 | geometric  | `beta * gamma = 1` (multiplicative)     | `(sqrt(r), 1/sqrt(r))` |
| -1 | harmonic  | `2 beta gamma / (beta+gamma) = 1`       | `((r+1)/2, (r+1)/(2r))` |

Invariants for all `p`:
- `beta(r,p) / gamma(r,p) = r` exactly (the asymmetry ratio is fixed by
  definition; `r > 1` benefit-dominant, `r < 1` cost-dominant, `r = 1`
  symmetric).
- `beta(1, p) = gamma(1, p) = 1` for every `p`. **The C5 symmetric-
  recovery result is conservation-form-invariant by construction.**

`cons_p` is exposed on `HeadlineCell`; its default is `1.0`, so every
existing simulation/sweep that uses the inherited additive form gets
*numerically identical* output post-rb-015. See
`tests/test_conservation_family.py` for the recovery contract.

### A2 heterogeneous-r d'-map (rb-019)

The paper governs the benefit/cost asymmetry by a SINGLE GLOBAL ratio
`r` (A2). The reviewer's A2 verdict (CONFIRMED-CONDITIONAL, run-015)
decomposes this into two readings: BETWEEN-PREPARATION (one effective
`r` per fixed preparation — what the `r`-sweep operationalises; benign)
and WITHIN-DISPLAY (one `r` for all locations / features / time at
once; empirically false per CR-007, within-display heterogeneity R2 is
real). The rebuild adopts the between-preparation reading in the model
statement and admits per-location `r_i` as a model EXTENSION via the
heterogeneous-r d'-map.

```
d'_i = max( d'_base + s_i (d'_max f(a_i) - d'_base),  0 )
s_i  = beta(r_i, p)   if a_i >= 1/N   (gain branch)
     = gamma(r_i, p)  if a_i <  1/N   (loss branch)
```

with `d'_base = d'_max f(1/N)` r-INDEPENDENT (paper Eq. 4), so a
per-location `r_i` changes only the per-location SCALING `s_i` of the
departure, never the common baseline (matches the reviewer's CR-048
derivation). The conservation order `p` propagates through
`beta_gamma(r_i, p)` at each location.

`d_prime_hetero(alloc, r_vec, d_max, f0, h, N, p=1.0)` is exposed
alongside the legacy `d_prime_asym(alpha, r, ...)`. The recovery
contract is: for uniform `r_vec` and the canonical homogeneous
allocation `canonical_alloc(alpha, N)`, the two functions return
**byte-identical** `(d_c, d_u)` values across the full alpha grid,
`r in {0.1, 0.3, 0.398, 1.0, 3.162, 10.0}`, `p in {0, 0.5, 1.0}`, and
`h in {"sqrt", "linear"}`. See `tests/test_heterogeneous_r.py`.

`HeadlineCell` is unchanged (still scalar `r` is supplied per-call via
`policies(r, cell)`); the heterogeneous regime is invoked directly via
`d_prime_hetero` and is wired into a heterogeneous-allocation policy
optimiser at rb-020 (RB-017 / A8) — see below.

### A8 N-dim uncued allocation (rb-020)

The paper's §2.2 forces the uncued budget `1 − α` into an *equal* split
across the `N − 1` uncued slots: each gets `(1 − α)/(N − 1)`. The
reviewer's A8 verdict (CONFIRMED-CONDITIONAL, run-012/run-013) shows
this is the unconstrained optimum at every headline-relevant cell —
equal split is always a critical point by exchange symmetry, and the
restricted Hessian is negative-definite for concave/linear `h` —
**conditional on equal uncued validity and on the cued slot's
value-weight dominance**. Outside that conditioning (heterogeneous
validity, anti-cue, or per-location `r_i`), the unconstrained optimum
can prefer an unequal split, so the rebuild must score policies over
the full N-dim allocation space.

`er_full_policy(alloc, valid, v, r_vec, cell)` takes a fully-specified
N-vector allocation `alloc` (∑aᵢ = 1, slot 0 cued by convention), an
N-vector validity `valid` (∑wᵢ = 1), the cued value `v`, an N-vector or
scalar `r_vec`, and a `HeadlineCell` carrying (N, d_max, f0, h_name,
variant, **rho, cons_p**). It returns

- `R` — expected reward at the policy with criteria optimised,
- `d_arr` — per-location `d'_i` via `d_prime_hetero`,
- `wu_arr` — per-location `w_i · u_i` (with `u_0 = v`, `u_{i>0} = 1`),
- `CR` — correct-rejection reward (`∑wᵢuᵢ` for variant A, `1` for B),
- `groups` — the (d, wu, n) tuples after grouping locations that share
  both `d'_i` and `wu_i` (since by symmetry they share an optimal `c_i`),
- `c_vals`, `c_idx` — the optimal per-group criteria,
- `method` — `"grid_1d"` (G = 1), `"grid_2d"` (G = 2), or
  `"coord_ascent_multi_restart"` (G ≥ 3).

The criterion optimisation is exact at grid resolution for G ≤ 2 (a
full 1- or 2-D argmax over `C_GRID`); for G ≥ 3 it uses multi-restart
coordinate ascent (seeded from `2^G` corner seeds plus the all-zero
seed; each restart is exact 1-D-per-group at grid resolution, sweeping
until criteria stop changing). The **rho channel is preserved**: the
joint no-FA probability is the one-factor Gauss-Hermite integral

```
P_no-fa(rho) = INT prod_g (Phi((c_g + d_g/2 - sqrt(rho) z) / sqrt(1-rho)))^{n_g} phi(z) dz
```

evaluated with the same 64-node quadrature `(_GH_Z, _GH_W)` the
homogeneous `p_no_fa_grid` uses. The **conservation order `p`** flows
through `d_prime_hetero(..., p=cell.cons_p)`, so any policy can be
scored at any `(rho, cons_p)` without additional code paths.

Recovery contract (`tests/test_general_policy.py`): under the canonical
homogeneous reduction (alloc = `canonical_alloc(alpha, N)`, valid =
`homogeneous_validity(V, N)`, `r_vec = r`), `er_full_policy` reproduces
the legacy `optimal_R(d_c, d_u, ...)` reward to **1e-9 absolute** across
the rb-001 alpha grid × `r ∈ {0.1, 0.398, 1, 3.162, 10}` × `V ∈ {0.3,
0.5, 0.7}` × `v ∈ {1, 5}` × `rho ∈ {0, 0.2}` × `p ∈ {0, 0.5, 1.0}` ×
variant `∈ {A, B}` — empirically `max|d| ≈ 2.78e-10` at the worst-case
cell. The gap is structural: the grouped form computes `n_u · wu_u =
3 · (1-V)/3` in two float operations and does not reconstruct `(1-V)`
bit-exactly when `(1-V)/3` is not representable. The reconstruction
error is six orders of magnitude tighter than any reported number.

Attention-coupled decision noise (A6) is queued as a separate backlog
item; if A6 lands at CONTESTED in the live verdict ledger it will fold
into this same general policy machinery as a per-location decision-noise
scaling `σ_i(α)`.

## Files

| file | purpose |
| --- | --- |
| `core.py` | model primitives (Phi, h, beta_gamma, d_prime_asym, P_no_fa, policies, sweeps) |
| `__init__.py` | re-exports the public surface |
| `tests/test_recovery.py` | the A1 `rho -> 0` recovery contract (rb-001) |
| `tests/recovery_output.json` | A1 recovery test output + sha256 digest |
| `tests/test_conservation_family.py` | the A3 conservation-family recovery contract (rb-015) |
| `tests/conservation_family_output.json` | A3 recovery test output + sha256 digest |
| `tests/test_heterogeneous_r.py` | the A2 homogeneous-r byte-for-byte recovery contract (rb-019) |
| `tests/heterogeneous_r_output.json` | A2 recovery test output + sha256 digest |
| `tests/test_general_policy.py` | the A8 N-dim allocation policy/optimiser recovery contract (rb-020) |
| `tests/general_policy_output.json` | A8 recovery test output + sha256 digest |

## The recovery contracts

Every future extension of this module must keep both recovery test
files passing: in the appropriate limit, the rebuilt model reproduces
the inherited Herman-Lab numbers *exactly*.

### A1 recovery (`tests/test_recovery.py`, rb-001)

- `p_no_fa(rho=0)` equals `Phi(b_c) * Phi(b_u)^(N-1)` to **binary
  equality** across the full criterion grid.
- `p_no_fa(rho -> 0)` converges to the product with the expected
  O(rho) scaling.
- Policy reward (P1–P4), VDA, and CF at `rho=0` match the reviewer's
  logged numbers (`Critique/replications/A1--correlated-fa/output/results.json`)
  to **floating-point identity** at `r in {0.398, 1.0, 3.162}`.
- Peak `VDA(r)` at `rho=0` lands at `0.0799` at `r=0.383`, matching the
  reviewer's run-017 C2 reproduction.
- Slepian monotonicity holds: `P_no-fa(rho)` is non-decreasing in
  `rho`, with the independent corner the minimum.

Output digest (current): `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`.

### A3 recovery (`tests/test_conservation_family.py`, rb-015)

- **Family identities**: `beta(r,p)/gamma(r,p) = r` to ~5e-16 across
  `r in {0.1..10}` × `p in {-2..+2}`; `M_p(beta, gamma) = 1` to ~5e-16;
  `beta(1, p) = gamma(1, p) = 1` binary for every `p` (C5
  conservation-form-invariance).
- **Additive `p = 1` byte-exact recovery**: `beta_gamma(r, p=1.0)`
  returns the legacy `(2r/(r+1), 2/(r+1))` bit-for-bit on the 21-point
  log-`r` grid; `policies(r, HeadlineCell(cons_p=1.0))` reproduces the
  rb-001 `REVIEWER_TARGETS_RHO0` pins to **zero diff** at
  `r in {0.398, 1.0, 3.162}`. **No legacy sim changes numerically.**
- **Multiplicative `p = 0` recovery vs reviewer A3**:
  `policies(r, HeadlineCell(cons_p=0.0))` reproduces the reviewer's
  logged A3 multiplicative-family numbers
  (`Critique/replications/A3--multiplicative-conservation/output/results.json`,
  `block_c2_c1.families.multiplicative`) on the 6-point pin set
  `r in {0.1, 0.316, 0.398, 1.0, 3.162, 10.0}` to within 1e-5
  (observed: max `|d|` ≤ 6.3e-7, well below the cross-Phi-backend ULP
  floor).
- **Symmetric corner identity**: `policies(r=1, cons_p=0)` equals
  `policies(r=1, cons_p=1)` to **floating-point identity** (the
  conservation choice is invisible at `r = 1`).

Output digest (current): `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`.

### A2 recovery (`tests/test_heterogeneous_r.py`, rb-019)

- **Homogeneous-r recovery on the gain-branch alpha grid** (alpha >= 1/N,
  default step 0.005): 5,436 cells across
  `h in {"sqrt", "linear"} × p in {0.0, 0.5, 1.0} × r in {0.1, 0.3, 0.398, 1.0, 3.162, 10.0}`
  with **binary equality** (`max|diff| = 0.0`) between
  `d_prime_hetero(canonical_alloc(alpha,N), r_uniform, ...)` and
  `d_prime_asym(alpha, r, ...)`.
- **Homogeneous-r recovery on the inversion-regime alpha grid**
  (alpha < 1/N): 468 cells, same `h × p × r` selection, again
  `max|diff| = 0.0`. Confirms the per-slot gain/loss branch criterion
  `a_i >= 1/N` correctly mirrors `d_prime_asym`'s else-branch.
- **Scalar-broadcast equivalence**: passing `r_vec` as a scalar is
  byte-identical to passing it as a uniform N-vector (72 cells,
  `max|diff| = 0.0`).
- **CR-048 / run-015 headline-cell spread=0 sanity**: at
  `(V=0.5, v=5, N=4, r=0.398, alpha=0.5, spread=0)`, the heterogeneous
  output reduces to the legacy `(d_c, d_u)` with `max|diff| = 0.0`.
- **Heterogeneous-r sign smoke**: at `spread=0.3` (uncued `r_i` =
  `r_cued · {0.7, 1.0, 1.3}`), `d_prime_hetero` returns a non-uniform
  uncued `d'`-vector ordered as predicted (`d_u_i` monotone-increasing
  in `r_i`, cued unchanged).

Output digest (current): `0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`.

### A8 recovery (`tests/test_general_policy.py`, rb-020)

- **TEST 1 — homogeneous-alloc recovery at `rho = 0` across the headline
  alpha × r × V × v grid** (4,530 cells: full
  `default_alpha_grid(4)` × `r ∈ {0.1, 0.398, 1, 3.162, 10}` × `V ∈
  {0.3, 0.5, 0.7}` × `v ∈ {1, 5}`, variant A, `p = 1`): `max|d| =
  2.77e-10` against the legacy `optimal_R(d_c, d_u, ...)` reward.
- **TEST 2 — same as TEST 1 but `rho = 0.2`**: engages the joint
  Gauss-Hermite quadrature path on both sides; 4,530 cells; `max|d| =
  2.78e-10`. The rho > 0 ULP slack is essentially the same as the rho =
  0 slack, confirming the wu-reconstruction error dominates over
  GH-quadrature associativity.
- **TEST 3 — variant B (CR = 1) sanity** at the headline cell across
  the alpha grid and `rho ∈ {0, 0.2}`: 302 cells; `max|d| = 1.19e-10`
  (smaller than variant A because no `V·v` scaling).
- **TEST 4 — conservation-family threading** at `p ∈ {0, 0.5, 1.0}` on
  the headline cell × alpha grid (151 cells each): all three `max|d| ≤
  2.11e-10`. The general optimiser threads `cell.cons_p` through
  `d_prime_hetero` correctly across the family.
- **TEST 5 — grouping / method check**: homogeneous alloc with `alpha
  != 1/N` gives `G = 2` and exact 2-D grid (`method = "grid_2d"`); at
  `alpha = 1/N` (where `d_c = d_u`) the `wu` still differs (`V·v` vs
  `(1-V)/(N-1)`) so it stays `G = 2`; a fully-symmetric cell (`V = 1/N,
  v = 1, alpha = 1/N`) collapses to `G = 1` (`method = "grid_1d"`).
- **TEST 6 — scalar-broadcast equivalence**: passing `r_vec = [r, r, r,
  r]` is byte-identical (`max|d| = 0.0` across 186 cells at `rho ∈ {0,
  0.2}`) to passing the scalar `r`, because `d_prime_hetero` with
  uniform `r_vec` is already byte-identical to `d_prime_asym` (rb-019
  contract).
- **TEST 7 — G ≥ 3 multi-restart smoke check**: at deliberately
  heterogeneous validity `(0.4, 0.3, 0.2, 0.1)` the optimiser hits
  `method = "coord_ascent_multi_restart"` with `G = 4` groups and
  returns a finite, sensible `R = 1.849` (vs `R = 1.845` for a pooled
  2-group sanity), confirming the coord-ascent path runs.

Output digest (current): `883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39`.

## Provenance

All primitives lifted with attribution from
- `Critique/replications/A1--correlated-fa/run.py` (CR-052, run-017,
  the equicorrelated-Gaussian extension)
- `Critique/replications/C5--symmetric-recovery/run.py` (P1–P4
  optimiser)
- `Critique/replications/C1--criterion-fraction-floor/run.py`
  (criterion-fraction decomposition)

The reviewer's verdict ledger validates these byte-for-byte against the
inherited paper's published numbers; we re-expose them as a library and
attach the recovery contract.

## How to run the recovery tests

```
cd Rebuild/
python3 -m model.tests.test_recovery               # A1: 7/7   sha256 d3c62215...
python3 -m model.tests.test_conservation_family    # A3: 14/14 sha256 f4f57a89...
python3 model/tests/test_heterogeneous_r.py        # A2: 5/5   sha256 0486921f...
python3 -m Rebuild.model.tests.test_general_policy # A8: 7/7   sha256 883ea15a...
```

## Public surface

```python
from model import HeadlineCell, policies, vda_curve, slepian_curve
from model.core import beta_gamma, d_prime_hetero, canonical_alloc, make_h

cell = HeadlineCell(N=4, V=0.5, v=5.0, rho=0.2, cons_p=1.0)
p = policies(r=0.398, cell=cell)
# p["VDA"], p["CF"], p["R_P1"], p["R_P2"], p["R_P3"], p["R_P4"],
# p["alpha_P1"], p["alpha_vb"]

# Conservation family direct:
b, g = beta_gamma(r=2.0, p=0.0)    # multiplicative: (sqrt(2), 1/sqrt(2))
b, g = beta_gamma(r=2.0, p=1.0)    # additive:       (4/3, 2/3)
b, g = beta_gamma(r=2.0, p=-1.0)   # harmonic:       (3/2, 3/4)

# Heterogeneous-r d'-map (A2 extension):
h = make_h("sqrt")
alloc = canonical_alloc(alpha=0.5, N=4)         # [0.5, 0.1667, 0.1667, 0.1667]
r_vec = [0.398, 0.279, 0.398, 0.517]            # spread=0.3 around r_cued=0.398
d_vec = d_prime_hetero(alloc, r_vec, d_max=2.0, f0=0.5, h=h, N=4, p=1.0)
# d_vec[0] = cued d' under r_cued=0.398; d_vec[1..3] = uncued d' under
# the spread r_uncued; uniform r_vec recovers d_prime_asym byte-for-byte.

# N-dim heterogeneous policy / optimiser (A8 + A2 + A3 + A1 combined):
from model import er_full_policy, homogeneous_validity
cell = HeadlineCell(N=4, V=0.5, v=5.0, rho=0.2, cons_p=1.0)
alloc = canonical_alloc(alpha=0.5, N=4)
valid = homogeneous_validity(V=0.5, N=4)        # canonical homogeneous validity
out   = er_full_policy(alloc, valid, v=5.0, r_vec=0.398, cell=cell)
# out["R"]      — optimal reward (criteria optimised, rho-aware)
# out["c_vals"] — per-group optimal criteria
# out["method"] — "grid_1d" | "grid_2d" | "coord_ascent_multi_restart"
# Any (alloc, valid, r_vec) can be scored — heterogeneous validity, anti-cue,
# unequal uncued split, per-location r_i.  Homogeneous reduction matches
# legacy `policies()` reward to 1e-9 absolute (see test_general_policy.py).
```

`HeadlineCell` defaults to the paper's C2 cell (V=0.5, v=5, N=4,
d'_max=2, f_0=0.5, h="sqrt", variant="A", rho=0, cons_p=1.0).
