# CR-048 / run-015 — numerical corroboration for the A2×A8 re-derivation

Companion to `Critique/derivations/A2xA8--heterogeneous-r-allocation.md`
(the primary deliverable; this directory is the verification harness, in
the spirit of `A8--heterogeneous-uncued/cr045_rederivation_check/`).

**Question.** A2 (paper §2.4) governs the benefit/cost asymmetry by a
single global ratio `r`. CR-045/run-013 proved A8 (homogeneous-uncued
allocation) is the *optimum* — but its exchange-symmetry argument
*requires* a single global `r`. Under a heterogeneous per-location ratio
vector `r_i`, does equal-split stay optimal, and does any C1/C2 headline
number shift?

## Files

- `verify_heterogeneous_r.py` — Part 1. Generalises the validated
  general-N model (`../A8--heterogeneous-uncued/run.py`) so each location
  carries its own `r_i` (only the per-location departure scaling `s_i`
  changes; the baseline `d'_base = d'_max·f(1/N)` is `r`-independent).
  Tests: (a) criticality of equal-split (tangent gradient), (b) allocation
  deviation at the headline cell, (c) C2 VDA-peak reframing in `r_cued`
  under uncued spreads, and the C1 contested-corner CF. Validates that
  `spread=0` reproduces the single-`r` model exactly. Runtime ~10 s.
- `verify_deviation_interior.py` — Part 2. Measures the A8-relaxed
  allocation deviation `ΔR = V(simplex-opt) − V(equal)` at INTERIOR-α
  cells (the value-blind P2/P3 regime, where the uncued budget `B=1−α`
  is non-trivial), with a fine simplex search, to test the `O(var r_i)`
  scaling and the bound. Runtime ~28 s.
- `output/` — `results.json`, `deviation_interior.json`, run logs.

## Headline results (deterministic; `results.json` sha256 `2659d7b5…`)

- **Validation (spread=0).** C2 peak VDA*=0.0771 @ `r_cued`=0.398; C1 CF
  0.866/0.729/0.640 @ r=0.3/1.0/3.2 — matches run-003/010/012 and the
  CR-022 `r`=0.3 transcription-error flag. The hetero code reduces to the
  single-`r` model exactly.
- **(a) Criticality breaks.** At ±30% spread the uncued tangent gradient
  is `‖g−mean‖`=7.2×10⁻² (nonzero); at spread 0 it is 0.0 — equal-split is
  generically NOT a critical point under heterogeneous `r`.
- **(b) Deviation bounded.** `max ΔR = 1.50×10⁻⁴` over all interior cells
  and spreads ≈ the CR-045 homogeneous slack (1.4×10⁻⁴). At P3 (α=1/N,
  cost-dominant) `ΔR=0` exactly (the kink spreading force survives
  heterogeneity); at the value-contrast P1 cell `ΔR=0` (cued-absorption,
  α*=1, B=0); at P2 cells `ΔR` grows smoothly with var(`r_i`).
- **(c) C2 reframes.** VDA peak stable under ±30% (0.0771→0.0770, `r_peak`
  fixed at 0.398); even k=1.5/3 spreads keep it at 0.0765–0.0798 @ `r_cued`
  ≈0.36. C1 contested corner CF 0.3040→0.3055 (not deepened).

**Conclusion.** Within-display heterogeneity (R2) is empirically real
(CR-007) but its consequence for C1–C5 is bounded: no headline claim is
shifted. See the derivation file for the closed-form argument.
