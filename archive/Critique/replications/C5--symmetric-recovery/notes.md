# C5 replication — notes, caveats, and the assumption sweep

Run: run-008, prompt v0.2, 2026-05-20. Φ backend in this run:
`A&S 7.1.26 numpy-vectorised` (scipy absent in the sandbox).

## Headline numbers (Block 1, paper config N=4, d'_max=2.0, f_0=0.5, √)

- 210 combinations swept.
- d' arrays **bit-identical** (`np.array_equal` True on both cued and
  uncued over the α grid).
- `max|Δα*| = 0.0`, `max|ΔR*| = 0.0` — **C5's "max diff 0.0"
  reproduced exactly.** No argmax row had any non-zero difference.

This is a *confirming* replication: the paper ran this self-check
itself (Figure 7). The value of re-running it is (a) it independently
verifies the published number, (b) it builds the symmetric+asymmetric
substrate the A3 / A5 / A6 assumption sweeps will reuse, and (c) it
turns "0.0" from an asserted number into an *explained* one (Sterbenz).

## Block 2 — the Sterbenz mechanism

`d'_base = d'_max f(1/N) = 2.0·(0.5 + 0.5·√0.25) = 1.5`. Swept
`x = d'_max f(·) ∈ [1.0, 2.0]`. Sterbenz band `[d'_base/2, 2 d'_base]
= [0.75, 3.0] ⊇ [1.0, 2.0]`. Every x is inside → the subtraction
`x − d'_base` is exact → `d'_base + (x − d'_base) = x` bit-for-bit.
The asymmetric-at-r=1 and symmetric maps are therefore the *same
float* at every grid point, not merely close.

## Block 3 — assumption sweep: is "exactly 0.0" robust?

Varying `(f_0, d'_max)` (h = √, N = 4), checking d'-array bit-identity:

| d'_max | f_0 | swept x range | Sterbenz band | x inside? | max|Δd'| | bit-identical |
|---|---|---|---|---|---|---|
| 1.0 | 0.1 | [0.100, 1.000] | [0.275, 1.10] | no | 2.8e-17 | **no** |
| 1.0 | 0.3 | [0.300, 1.000] | [0.325, 1.30] | no | 0.0 | yes |
| 1.0 | 0.5 | [0.500, 1.000] | [0.375, 1.50] | yes | 0.0 | yes |
| 1.0 | 0.7 | [0.700, 1.000] | [0.425, 1.70] | yes | 0.0 | yes |
| 1.0 | 0.9 | [0.900, 1.000] | [0.475, 1.90] | yes | 0.0 | yes |
| 2.0 | 0.1 | [0.200, 2.000] | [0.55, 2.20] | no | 5.6e-17 | **no** |
| 2.0 | 0.3 | [0.600, 2.000] | [0.65, 2.60] | no | 0.0 | yes |
| **2.0** | **0.5** | **[1.000, 2.000]** | **[0.75, 3.00]** | **yes** | **0.0** | **yes (paper config)** |
| 2.0 | 0.7 | [1.400, 2.000] | [0.85, 3.40] | yes | 0.0 | yes |
| 2.0 | 0.9 | [1.800, 2.000] | [0.95, 3.80] | yes | 0.0 | yes |
| 3.0 | 0.1 | [0.300, 3.000] | [0.825, 3.30] | no | 1.1e-16 | **no** |
| 3.0 | 0.3 | [0.900, 3.000] | [0.975, 3.90] | no | 1.1e-16 | **no** |
| 3.0 | 0.5 | [1.500, 3.000] | [1.125, 4.50] | yes | 0.0 | yes |
| 3.0 | 0.7 | [2.100, 3.000] | [1.275, 5.10] | yes | 0.0 | yes |
| 3.0 | 0.9 | [2.700, 3.000] | [1.425, 5.70] | yes | 0.0 | yes |

Reading:

1. **Inside the Sterbenz band ⟹ bit-exact** (max|Δd'| = 0.0)
   in every case. The implication is one-directional and clean.
2. **Outside the band ⟹ MAY drift** by ~1 ulp (`1e-17`–`1e-16`):
   4 of 15 configs (the low-`f_0` ones whose x dips well below
   `d'_base/2`) lose bit-identity. Band membership is *sufficient*,
   not *necessary* — `d_max=2, f_0=0.3` and `d_max=1, f_0=0.3` sit
   just outside the band yet remain bit-exact because the particular
   operands still subtract exactly.
3. The paper's validation config `(d'_max=2.0, f_0=0.5)` sits
   comfortably inside the band, so its "max diff 0.0" is **structurally
   guaranteed**, not a numerical coincidence — but the literal "0.0"
   is a property of *that* config. The defensible universal statement
   is "identical to machine precision" (≤ ~1 ulp on d', which the grid
   argmax almost surely rounds away to 0 for α* and to ~1e-16 for R*).

So C5 as written (scoped to the 210 matched combos at the stated
config) is **exactly correct**. The only nuance for an editor: the
phrase "reduces exactly" is an algebraic truth (β(1)=γ(1)=1) and the
"0.0" is exact *here*, but readers should not generalise "0.0" to
arbitrary `(f_0, d'_max)` — there it is exact only to machine epsilon.

## Block 4 — continuity: r = 1 is the smooth limit, not a knife-edge

`max|Δ|` vs the symmetric model on 4 representative combos:

| r | max|Δα*| | max|ΔR*| |
|---|---|---|
| 0.999000 | 0.0 | 8.438e-05 |
| 0.999999 | 0.0 | 8.433e-08 |
| **1.000000** | **0.0** | **0.0** |
| 1.000001 | 0.0 | 8.433e-08 |
| 1.001000 | 0.0 | 8.428e-05 |

`max|ΔR*|` is linear in `|r − 1|` with slope ≈ 0.084 reward units per
unit r (8.43e-8/1e-6 ≈ 8.43e-5/1e-3 ≈ 0.084), and vanishes exactly at
r = 1. `α*` does not move at all over `r = 1 ± 1e-3` (the perturbation
is far below the Δα = 0.005 grid resolution). So the symmetric special
case is the genuine, smooth centre of the asymmetric family, not a
removable singularity or a discontinuous special-case branch.

## Caveats

- The paper's own validation code is unavailable here; this is a
  from-equations re-implementation. Agreement on "0.0" cross-validates
  the algebra, not the paper's specific code.
- The α* identity is grid-dependent only in the trivial sense that
  *both* models use the same grid; the result is grid-independent
  because the rewards are bit-identical at every grid point.
- Only one assumption axis was swept (the model config `(f_0, d'_max)`
  governing Sterbenz band membership), per mission §8.5 (one focused
  extension, not a multi-assumption blast). The β·γ = 1 alternative
  constraint (A3) is a *separate* claim — at r = 1 it also gives
  β = γ = 1, so it would recover the same symmetric point, but its
  off-r=1 behaviour is out of scope here and is tracked separately.
