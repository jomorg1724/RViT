# A6 — heterogeneous decision rule (CR-011, run-018)

Numerical corroboration for the A6 re-derivation
(`Critique/derivations/A6--heterogeneous-decision-rule.md`). A6 (mission
§2.7): the paper's SDT decision machinery is **homogeneous** across
locations — the same equal-variance Gaussian transform (internal noise
σ = 1) at every location, with only the free parameters d'_i (set by
attention) and c_i (set by the optimiser) differing. The paper never
states A6; it is implicit in §2.2 and is the unstated half of the §5.5
sentence *"the model assumes independent per-location SDT decisions;
real observers emit a single global response …"* (run-017/CR-052
identified the "single global response" clause as A6, distinct from the
A1 independence clause).

## What it computes

A per-location decision-noise scale `s_i ≥ 1` (cued `s_c`, uncued `s_u`)
generalises the rates to
`HR_i = Φ((d'_i/2 − c_i)/s_i)`, `FAR_i = Φ((−d'_i/2 − c_i)/s_i)`.
The paper is the `s_i ≡ 1` corner.

- **Block 0 — validation.** `s ≡ 1` reproduces the C1 headline criterion
  fraction (CF = 0.7282 at r=1, V=0.5, v=5, variant A; C1 code 0.728)
  and the C2 VDA peak (0.0797 @ r=0.398; C2 ≈0.0799@0.383). The Prop-1
  pointwise identity `Φ((d/2−c)/s) = Φ((d/s)/2 − c/s)` holds to 1.1e-16.
- **Block 1 — Prop 1 (fixed heterogeneous noise is absorbed).** On a
  criterion grid wide enough that neither parameterisation clips
  ([-8,8]), the CF computed with explicit `(s_c,s_u)` equals the CF
  computed from rescaled sensitivities `(d_c/s_c, d_u/s_u)` with `s≡1`,
  to grid resolution (max |Δ| = 1.7e-5, → grid floor as Δc→0). ⇒ the
  P1–P4 decomposition is **structurally invariant** under fixed
  heterogeneous machinery: only the per-location *effective* sensitivity
  changes (same class as a d'_max / f_0 perturbation).
- **Block 2 — Prop 2 (attention-coupled noise is a third lever).** With
  `s_i(a_i) = √(1 + κ(1 − h(a_i)))` (decision noise falls as attention
  rises; κ=0 = paper), the criterion fraction **deflates** 0.728 → 0.626
  (κ:0→1, wide-grid guard) while the total achievable gain *grows*
  0.62 → 0.78 — attention now buys sensitivity reallocation AND
  noise reduction, so the criterion-fraction metric no longer cleanly
  partitions "criterion vs attention." The C2 VDA peak also collapses
  (0.0797@0.398 → 0.0013@0.100).

## Expected output

`python3 run.py` → `output/results.json`. Console prints all three
blocks. Runtime ≈ 35 s (the wide-grid blocks evaluate a 1601² criterion
grid per cell). Numeric content is deterministic: sha256 `d6741d48…`
(byte-identical across re-runs, excluding the `elapsed_s` timing field).

## Relation to the paper's code

No paper code is available; this is an independent implementation. The
model primitives (Φ, f, β/γ, d'(α), Eq. 9 reward, P1–P4 / CF) are copied
with attribution from `C1--criterion-fraction-floor/run.py`; the only new
machinery is the per-location decision-noise scale `s_i` in the rate
functions and the `s(α)` coupling for Prop 2.

## Caveat

The default [-3,3] criterion grid (paper's grid) **clips** the uncued
criterion once `s_u` is large (the optimal physical criterion grows with
s to hold FAR fixed), spuriously inflating CF (e.g. 0.814 vs the correct
0.789 at s_u=2). Block 1 therefore uses a [-8,8] grid; Block 2 includes a
wide-grid guard at κ=1. This is a discretisation caveat, not a structural
finding.
