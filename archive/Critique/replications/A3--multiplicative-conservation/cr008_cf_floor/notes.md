# CR-008 — notes, caveats, and the honest decomposition

## Why the literal CR-008 rule was refined

The run-010 re-scope of CR-008 stated the decision rule as: "report whether any
cell has CF_mult<0.5. If yes → A3 → CONTESTED; if no → CONFIRMED-CONDITIONAL."
Taken literally this is blunt, because **177 of the 590 at-risk cells already
have additive CF < 0.5** — C1's contested corner (run-003 found 4.0 % of the
grid below 0.5, argmin 0.304). CF_mult<0.5 in *those* cells is not attributable
to the constraint swap; criterion dominance already failed there under the rule
the paper actually uses. So "any CF_mult<0.5" would trigger CONTESTED trivially
and for the wrong reason.

The constraint-**attributable** signal is therefore decomposed into:

- **New flips:** cells with CF_add ≥ 0.5 but CF_mult < 0.5. These are cells the
  paper would call criterion-dominant under its own additive rule that become
  criterion-subordinate *only because of* the βγ=1 swap. **191** over the full
  grid (190 inside S; 1 cell with additive CF ∈ [0.60, 0.61) flipped, caught by
  the Block-C full sweep — see "Why the full grid" below).
- **Global fraction + median:** criterion-subordinate fraction doubles
  4.0 %→8.3 %; median CF unchanged 0.7605→0.7578.

The verdict rests on this decomposition, not on the blunt rule. This is logged
explicitly so a future referee sees the reasoning, per mission §6 (do not
overclaim).

## Mechanism (why CF_mult ≤ CF_add always, with equality only at α*=1/N)

CF = (R(P3)−R(P4)) / (R(P1)−R(P4)). R(P3), R(P4) sit at α=1/N where the
asymmetric scaling multiplies the zero bracket d'_max f(1/N) − d'_base = 0, so
they are **family-independent** (verified: max|Δ| = 0.0 between additive and
multiplicative). Only the denominator R(P1) moves. The rescaling theorem
(CR-040) gives (β,γ)_× = κ(r)(β,γ)_+ with κ(r) = (r+1)/(2√r) ≥ 1, so βγ=1
amplifies both the cued benefit and the uncued cost. Wherever reallocation
already helps (R(P1) > R(P3)), it helps *more* under βγ=1 ⇒ R(P1)_× ≥ R(P1)_+
⇒ CF_× ≤ CF_+. Empirically ΔCF ∈ [−0.109, 0.000] with **max exactly 0.0** —
βγ=1 never raises CF, and equals it exactly in cells where the optimum stays at
α=1/N (no reallocation, e.g. the V→1/N degenerate column or cost-dominant
small-r cells). This confirms the A3 v0.1 verdict's predicted direction.

## Why the failure corner is high-r (benefit-dominant), not low-r

The new flips span r ≈ 2.5–10 (β > γ, benefit-dominant). At high r, β_× = √r
outgrows β_+ = 2r/(r+1) (at r=10: 3.16 vs 1.82), so the multiplicative cued
benefit is much larger, R(P1) reallocation gain is larger, CF is lower. The
VDA peak (C2) lives at *low* r (≈0.3, cost-dominant) and is untouched — consistent
with CR-040 finding C2 robust. So the criterion-dominance erosion and the VDA
non-monotonicity occupy opposite ends of the r-axis; they do not interact.

## Why the full grid (Block C) was worth running despite the §8.5 "one slice" rule

Restricting to additive-CF<0.60 (per the task) is sufficient to find essentially
all new flips, but the worst erosion (ΔCF=−0.109) slightly exceeds the 0.10
margin from 0.60, so a cell with additive CF ∈ [0.60, 0.61) *can* flip — and
exactly one did. The full 4,410-cell multiplicative sweep (cheap, ~10 s of the
21 s total once P2/VDA are skipped — CF needs only P1,P3,P4) bounds new flips
everywhere and yields the decisive global statistic (fraction doubles; median
unchanged). It is one focused replication of one assumption (A3), one attack
vector (replication) — within §8.5.

## Validation checks (all pass)

- `beta_gamma_multiplicative` ≡ parent `../run.py`: max|dev| = 0.0.
- Recomputed additive CF vs run-003 stored CF over all 590 cells: max|Δ| = 0.0
  (bit-identical; same Φ, grids, equations).
- R(P3), R(P4) additive-vs-multiplicative: max|Δ| = 0.0 (family-independence).
- Determinism: re-run produces bit-identical `results.json` (sans `elapsed_s`).
- Independent from-scratch re-implementation (no shared code) of the worst cell
  (r=10,V=0.25,v=4,B): CF_mult = 0.2309, CF_add = 0.3040 — both reproduced.

## Caveats / loose ends

- **Grid resolution.** Δα=0.02, Δc=0.05 (run-003's grid; validated against the
  paper to 0.002 of CF at r=1.0 and r=3.2 in CR-002). The ΔCF magnitudes driving
  the flips (0.03–0.11) are 15–50× any plausible grid error, so the flip count
  is robust to resolution. A Δα=0.005 spot-check on a handful of borderline
  flips (CF_mult ∈ [0.48, 0.50)) would tighten the exact count by ±a few; spawned
  as a low-priority follow-up (CR-044).
- **Φ approximation.** A&S 7.1.26 (max abs err ~1.5e-7); both families use the
  same Φ so the error cancels in CF_mult − CF_add and in the family comparison.
- **Variant coverage.** New flips are predominantly variant B but include
  variant A at the highest r (r=10). The doubling is not a single-variant artefact.
- **Only two conservation rules bracketed.** Like CR-040, this tests β+γ=2 vs
  βγ=1; intermediate families (β^p+γ^p=const) are untested.
