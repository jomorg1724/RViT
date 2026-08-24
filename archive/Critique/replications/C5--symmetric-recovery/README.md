# C5 — Symmetric special-case recovery at r = 1 (CR-005)

**Claim under attack (C5, mission §2.6; paper Appendix A "Validation:
Symmetric Special Case", p.8):**

> At r = 1, the model's independent benefit and cost scaling reduces
> to a symmetric special case (β = γ = 1) where a single shared
> transfer function governs both benefit and cost. We validated this
> by comparing the r = 1 results against an independent implementation
> of the symmetric model across all 210 matched parameter combinations
> (N = 4, d'_max = 2.0, f_0 = 0.5, √· form). Optimal α* and R* values
> are identical to machine precision (maximum difference: 0.0;
> Figure 7).

**Attack vector:** replication (mission §3.2).

## What `run.py` computes

The 210 matched combinations are `V ∈ {21 pts in [1/N, 1]} × v ∈
{1..5} × variant ∈ {A, B}` at fixed `r = 1, N = 4, d'_max = 2.0,
f_0 = 0.5, h = √` (= 21 × 5 × 2 = 210, the paper's count). For each
combination the script computes the P1 joint optimum `(α*, R*)`
under two **independent** sensitivity maps and compares them:

- **Asymmetric (★):** the paper's general model `d'_c = d'_base +
  β(d'_max f(α) − d'_base)`, `d'_u = d'_base + γ(d'_max f((1−α)/(N−1))
  − d'_base)`, evaluated at `r = 1` (so `β = γ = 1.0` exactly). Copied
  with attribution from `C1--criterion-fraction-floor/run.py`.
- **Symmetric (☆):** the "single shared transfer function" form
  `d'_c = d'_max f(α)`, `d'_u = d'_max f((1−α)/(N−1))`, written from
  scratch — no β/γ, no `d'_base` reference point.

Both maps feed the *same* criterion/α grid optimiser, so the only
difference between the code paths is the d'(α) formula — exactly the
β = γ = 1 reduction C5 asserts.

Four blocks:

1. **Primary** — the 210-combo `max|Δα*|`, `max|ΔR*|`, plus the
   bit-identity of the d' arrays (`np.array_equal`).
2. **Sterbenz mechanism check** — why the recovery is *exact* and not
   merely ~1 ulp at this config (see below).
3. **Robustness probe** — vary `(f_0, d'_max)` off the validation
   config and locate where exact-0 gives way to a ~1-ulp gap.
4. **Continuity probe** — `max|Δ|` vs the symmetric model at
   `r ∈ {1±1e-3, 1±1e-6, 1}` to show r = 1 is the smooth limit, not a
   knife-edge.

## Expected vs observed

| Quantity (paper config) | Paper | This replication |
|---|---|---|
| `max|Δα*|` over 210 combos | 0.0 | **0.0** (exact) |
| `max|ΔR*|` over 210 combos | 0.0 | **0.0** (exact) |
| d' arrays bit-identical | (implied) | **True** (`np.array_equal`) |

`C5` is reproduced **exactly**, not merely to machine epsilon.

## Why exact, not ~1 ulp — Sterbenz's lemma

`β(1) = 2·1/(1+1) = 1` and `γ(1) = 2/(1+1) = 1` are both exact in
IEEE-754 binary64. The asymmetric map at r = 1 then computes
`a + (x − a)` with `a = d'_base` and `x = d'_max f(·)`, whereas the
symmetric map computes `x` directly. **Sterbenz's lemma:** if
`a/2 ≤ x ≤ 2a` then `fl(x − a) = x − a` exactly, whence
`fl(a + (x − a)) = x` bit-for-bit. At the validation config
`d'_base = 1.5` and every swept `x ∈ [1.0, 2.0] ⊂ [0.75, 3.0] =
[d'_base/2, 2 d'_base]`, so the round trip is exact for every grid
point → identical d', Φ tables, rewards, and grid argmaxima →
`max diff = 0.0`. The paper's headline "0.0" is therefore a
*guaranteed* consequence of the chosen config, not a lucky rounding.

Block 3 shows the converse: when `x` leaves the Sterbenz band (low
`f_0` relative to `d'_base`, e.g. `f_0 = 0.1`), the d' round trip can
incur a ~1-ulp gap (`~1e-17` to `1e-16`), so "max diff 0.0" becomes
"max diff ≈ machine-epsilon". Band membership is *sufficient* but not
*necessary* (`d_max=2, f_0=0.3` sits just outside the band yet is
still bit-exact). Detail in `notes.md`.

## How to run

```bash
cd Critique/replications/C5--symmetric-recovery
python3 run.py            # ~6 s; writes output/results.json + output/run.log
```

No scipy required (falls back to an A&S-7.1.26 numpy Φ; irrelevant to
C5 because *both* models call the *same* Φ, so any Φ error cancels in
the asymmetric−symmetric difference).

## Difference from the paper's own code

The paper's validation code is not available in this repo, so this is
a from-equations re-implementation. The agreement with the published
"0.0" confirms both (a) the algebraic reduction and (b) that the
paper's two code paths were, like these, numerically consistent at the
validation config.
