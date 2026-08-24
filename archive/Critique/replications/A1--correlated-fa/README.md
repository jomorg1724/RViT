# A1 — correlated false-alarm aggregation (CR-052, run-017)

**Attack vector:** re-derivation (numerical corroboration).
**Claim under test:** A1 / paper §5.5 — *"the model assumes independent
per-location SDT decisions … Our results therefore represent an upper bound on
VDA benefit."* Is independence really an *upper bound* on VDA?

## What this computes

The paper's expected reward (Eq. 9) uses independence in exactly one place: the
no-change-trial joint correct-rejection probability
`P_no-fa = (1-FAR_c)(1-FAR_u)^{N-1}` (a product of per-location marginals).
We replace that product with the **equicorrelated-Gaussian** joint orthant
probability at cross-location correlation `ρ`, via the exact one-factor
(shared-latent-`Z`) reduction

```
P_no-fa(ρ) = ∫ Φ((b_c − √ρ z)/√(1−ρ)) · Φ((b_u − √ρ z)/√(1−ρ))^{N−1} φ(z) dz,
b_i = c_i + d'_i / 2,
```

evaluated by 64-node Gauss–Hermite quadrature (no multivariate-normal CDF
needed; the reduction is exact for equicorrelation). We then **re-optimise** the
per-location criteria `(c_c, c_u)` and the attention allocation `α` under
`P_no-fa(ρ)` and recompute:

* the **VDA(r) curve** `R(P1) − R(P2)` at the C2 / Figure-4 headline cell
  (`V=0.5, v=5, N=4, d'_max=2.0, f_0=0.5, h=√`), variants A and B;
* the **criterion fraction** `CF = [R(P3)−R(P4)] / [R(P1)−R(P4)]` at
  representative `r` (cost-dominant peak `0.398`, symmetric `1.0`,
  benefit-dominant `3.162`);

for `ρ ∈ {0, 0.1, 0.2, 0.3, 0.4}` bracketing the Cohen & Maunsell (2009)
`r_SC ≈ 0.2`.

## Decision rule (mission CR-052)

* peak VDA **rises materially** with `ρ`, or the curve is not upper-bounded by
  the `ρ=0` curve → "upper bound on VDA" **fails** → A1 → **CONTESTED**;
* peak VDA **falls / flat** in `ρ` and `ρ=0` upper-bounds the curve → claim
  holds in scope → A1 → **CONFIRMED-CONDITIONAL**.

## How to run

```bash
python3 run.py          # numpy required; scipy.special.ndtr used if present,
                        # else A&S 7.1.26 fallback (Φ error is common-mode and
                        # cancels in the ρ-trend). Writes output/results.json.
```

## Expected output (headline)

* **Validation (ρ=0):** peak VDA = **0.0799 at r = 0.383**, reproducing the
  independent-model C2 peak (CR-001 0.0774; CR-040 0.0797; CR-036 0.0769) — the
  `ρ=0` code path is identical to the prior independent implementation.
  Quadrature→product gap < 1e-6; GH-64 vs GH-128 max diff ~8e-16; Slepian
  monotonicity and "independent corner is the minimum" both hold.
* **Result:** the "upper bound on VDA" claim is **regime-structured and false as
  a uniform statement.** Correlation *suppresses* VDA in the cost-dominant
  regime (`r ≲ 0.5`, incl. the headline peak) but *amplifies* it in the
  benefit-dominant regime (`r ≳ 0.5`) by up to **+0.010 (~+20% of local VDA)**
  at `ρ=0.4`; the excess grows with `ρ`. Even at the headline peak, `ρ=0.1`
  raises VDA (+0.0013). The criterion fraction **falls** with `ρ` everywhere in
  variant A (e.g. `r=1`: 0.728→0.647; `r=3.16`: 0.641→0.539) — independence
  upper-bounds the *criterion fraction*, not VDA.

## Difference from the paper's code

The paper provides no public code. The model primitives (Φ, `h`, `f`, `β/γ`,
`d'_asym`, the `Δc=0.05` criterion grid, the `R*` optimiser) are reused with
attribution from `C5--symmetric-recovery/run.py` and
`C1--criterion-fraction-floor/run.py`, so the `ρ=0` path is byte-equivalent to
the prior validated independent implementation. The only new machinery is
`p_no_fa_grid()` (the correlated orthant probability) and `floor_R()` (P4 under
`P_no-fa(ρ)`).

## Determinism

`output/results.json` carries `meta.sha256_numeric` hashing the numeric content
(timing excluded). Re-run digest: **`b9828f02…`** (byte-identical across runs).
