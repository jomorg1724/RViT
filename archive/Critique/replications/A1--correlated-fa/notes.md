# Notes — A1 correlated-FA replication (CR-052, run-017)

## The single modelling decision: where correlation enters (the "booking")

The CR-052 task flagged the hardest honest sub-question: *where to book
correlation-mediated effects.* The answer is forced by the paper's own reward
structure (Eq. 9), and it is clean:

* The change-trial term `0.5[V·HR_c·v + (1−V)·HR_u]` is **linear** in the
  marginal hit rates. On a change trial the change is at exactly **one**
  location, so detection reward never forms a cross-location product —
  correlation has no aggregation point to enter.
* The no-change-trial term `0.5·P_no-fa·CR` is the **only** place a
  cross-location product appears. Independence (A1) *is* that product.

Therefore **Booking 1** — correlation enters `P_no-fa` and nowhere else — is the
**faithful and complete** relaxation of A1 within the paper's reward structure.
This run implements Booking 1.

**Booking 2** — correlation also changing a *pooled / population* `d'`
(the I-neur reading, `d'^2 ∝ (Δμ)ᵀ Σ⁻¹ (Δμ)`) — has no locus in Eq. 9 because
there is no pooled detection statistic; it would require a **global** "change
detected somewhere" decision rule. That is assumption **A6** (single global
response / homogeneous decision rule, CR-011), *not* A1. This cleanly
**disentangles** the two clauses the paper's §5.5 sentence bundles together
("independent per-location SDT decisions" = A1; "real observers emit a single
global response" = A6). The A1 test is Booking 1; the Booking-2 sensitivity
question is routed to A6/CR-011 (see verdict loose ends).

## Why the equicorrelation 1-D reduction is exact (not an approximation)

Equicorrelation admits the one-factor representation
`X_i = −d'_i/2 + √ρ Z + √(1−ρ) ε_i` with `Z, ε_i ~ N(0,1)` iid. Conditional on
`Z=z` the locations are independent, so the joint orthant probability factorises
*inside the integral*. The only numerical error is the Gauss–Hermite quadrature
of a smooth integrand (products of Φ): GH-64 vs GH-128 agree to ~8e-16, far past
convergence. No `scipy.stats.multivariate_normal` / Genz routine is used, so the
result is exact and portable. (scipy was available this run for `ndtr`, but the
correlated integral never needs the MVN-CDF.)

## Validation chain (ρ=0 must be the independent model)

* `p_no_fa_grid(·, ρ=0)` returns the exact product `Φ(b_c)Φ(b_u)^{N−1}` (special
  case); `p_no_fa_grid(·, ρ=1e-6)` matches it to 3e-7 (the `√(1−ρ)` limit).
* Σ of GH weights = 1.000000000000 (probability normalisation exact).
* **Slepian monotonicity verified numerically:** `P_no-fa(ρ)` is non-decreasing
  in `ρ` and `P_no-fa(0) = min` — the independent corner maximises the aggregate
  FA penalty (confirms the run-016 closed-form claim).
* **ρ=0 peak VDA = 0.0799 at r=0.383**, inside the band of all prior independent
  reproductions of the C2 peak (CR-001 0.0774@0.398; CR-040 0.0797; CR-036
  0.0769@0.398). The `ρ=0` code path therefore reproduces the headline number.

## What changed when (the assumption sweep, one axis: ρ)

Per mission §8.5 (one focused relaxation, not a multi-assumption sweep), the only
swept axis is the decision correlation `ρ ∈ {0,0.1,0.2,0.3,0.4}`, at the fixed
C2 headline cell. Findings:

1. **VDA(r) is reshaped, not uniformly shifted.** Crossover at `r ≈ 0.5`:
   suppressed below, amplified above. So the sign of `dVDA/dρ` *depends on r* —
   which is exactly why a single "upper bound" statement cannot be right.
2. **The headline peak is robust** to the empirically central `ρ≈0.2`
   (0.0796 vs 0.0799, −0.4%); the C2 number survives.
3. **The criterion fraction falls monotonically with ρ** (variant A) — the true
   "upper bound" object is CF, not VDA. CF(ρ=0) over-states criterion's share.
4. **Variant B**: VDA is tiny (~0.003–0.004) and noisy; the relative upper-bound
   excess is large but absolute negligible. CF is higher and roughly flat
   (the fixed CR removes the value-coupling that drives the variant-A mechanism).

## Caveats / scope

* Equicorrelation is the simplest correlated model; real `Σ` has structure
  (within-area down, between-area up — ruff_cohen2016; supra-pairwise —
  srinath2021). Equicorrelation with `ρ>0` is sufficient to **refute** a uniform
  upper bound (one counterexample suffices); a structured `Σ` could move the
  magnitude either way and is a spawned follow-up.
* `α` grid `[1/N, 1]` step 0.005 (no-inversion per C4, valid for `V=0.5≥1/N`);
  criterion grid `Δc=0.05` (paper). Peak-`r` resolution is the log-grid step.
* The amplification is largest in the benefit-dominant tail (`r≳0.5`), which is
  the regime where C1's criterion fraction is *already* contested (run-003) and
  where A3's βγ=1 swap *already* deepened the failure — so the three assumption
  relaxations (A1, A3, and the C1 corner) compound in the same corner.
