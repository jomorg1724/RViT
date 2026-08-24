# A6 corroboration — notes, caveats, assumption sweeps

## Headline numbers (run-018, 2026-05-25)

| quantity | value | reference |
|---|---|---|
| CF headline (r=1,V=.5,v=5,A), s≡1 | 0.7282 | C1 code 0.728 ✓ |
| VDA peak, s≡1 | 0.0797 @ r=0.398 | C2 ≈0.0799@0.383 ✓ |
| Prop-1 pointwise identity max err | 1.11e-16 | exact |
| Prop-1 CF(explicit) − CF(reparam), wide grid | ≤ 1.7e-5 | → 0 (Δc→0) |
| Prop-2 CF deflation κ:0→1 (wide grid) | 0.728 → 0.626 (−0.102) | robust |
| Prop-2 total gain growth κ:0→1 | 0.62 → 0.78 | attention's reach grows |
| Prop-2 VDA peak κ=1 | 0.0013 @ r=0.100 | C2 peak collapses |

Numeric content sha256 `d6741d48…` (deterministic; `elapsed_s` excluded).

## What changed when (assumption sweep log)

1. **Fixed heterogeneous decision noise (Prop 1) changes NOTHING
   structural.** The reward is *exactly* the paper's reward with each
   location's sensitivity rescaled d'_i → d'_i/s_i (Block-0 identity to
   1e-16; Block-1 CF agreement to grid resolution on a non-clipping
   grid). So a fixed (s_c, s_u) is a per-location d'-perturbation, in the
   same class as the secondary-sweep parameters d'_max and f_0 — the
   criterion-vs-attention decomposition's *form* is untouched. The CF
   *value* moves (e.g. 0.728→0.789 when s_u=2, i.e. more decision noise
   at the uncued locations), but the interpretation ("share of the gain
   captured by criterion at uniform attention") is preserved.

2. **Attention-COUPLED decision noise (Prop 2) cracks the metric's
   interpretation.** When s_i = s(a_i) with s'<0, the α-lever has two
   sub-effects (spatial d' reallocation + noise reduction), so the
   P3→P1 increment the criterion fraction books to "attention" now
   bundles a *second* mechanism. CF deflates (−0.10) and the total gain
   grows — attention does more than the model credits. The interpretive
   crack holds regardless of the numerical sign; the direction (CF down)
   matches the CR-055 prediction and the A1-ρ result (CR-052: CF fell
   under correlation too).

## Caveats / traps

- **Criterion-grid clipping.** The default [-3,3] grid (paper's grid)
  silently clips the uncued criterion once s_u ≳ 1.5 — the optimal
  *physical* criterion must move further from the midpoint to hold FAR
  fixed under inflated noise. This was caught when the explicit-vs-
  reparam gap (a Prop-1 identity that MUST hold in the continuum) failed
  to shrink with Δc; widening to [-8,8] resolved it to 1.7e-5. The
  default-grid CF for large s is therefore an over-estimate (0.814 vs
  correct 0.789 at s_u=2; 0.638 vs correct 0.626 at κ=1). Anyone
  extending this code to large decision noise MUST widen the criterion
  grid. (Mirrors the C5 floating-point / A8 grid-slack caveats: the
  numerics have to be watched at the edges of the parameter space.)

- **The s(α) coupling is illustrative, not estimated.** `s(a)=√(1+κ(1−h(a)))`
  is one plausible one-parameter family (decision noise highest at zero
  attention, no excess at full attention). The *magnitude* of the CF
  deflation depends on κ and the coupling form; the *direction* and the
  structural point (attention becomes a compound lever) do not. A
  literature-grounded coupling (e.g. tying s to the Cohen–Maunsell
  correlation-reduction magnitude) is the natural CR-spawn.

- **This is the mission's A6 (heterogeneous MACHINERY).** The §5.5
  "single global response" reading (one pooled decision variable / one
  global criterion) is a *different* relaxation that overlaps A1 (the
  Eq. 9 FA product) — flagged in the derivation §5 and spawned as a
  follow-up, not executed here.

## Spawned

- CR-056 (A6 second vector — single-global-criterion DOF-reduction
  replication: constrain c_c=c_u and re-run the C1 grid; tests the
  §5.1 "criterion can independently encode value at each location"
  claim head-on and the CR-055 prediction directly).
- CR-057 (A6 literature — is the decision-noise/criterion lever
  attention- AND value-modulated? luo_maunsell2018 dissociation +
  Cohen–Maunsell decorrelation as the empirical s(α); links to CR-053).
