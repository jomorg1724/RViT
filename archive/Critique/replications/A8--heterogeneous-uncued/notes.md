# CR-036 / A8 — modelling notes, caveats, and the optimiser-validation story

## 1. The generalised β/γ rule (a modelling choice, stated explicitly)

The paper defines β/γ only for the cued-vs-uncued split (Eqs. 7–8) with the
note (§2.3): *"If α<1/N, the roles reverse: the cued location's departure is
scaled by γ and each uncued location's by β. All d′ values are clamped at
≥0."* To allow a *heterogeneous* allocation vector we must say what scaling a
location gets when there is no single "the uncued allocation." The unique
generalisation consistent with §2.3 ties the scaling to the **sign of each
location's own departure from the 1/N baseline**:

    d′_i = max( d′_base + s_i·[d′_max f(a_i) − d′_base], 0 ),
        s_i = β(r)  if a_i ≥ 1/N   (departure ≥ 0, a GAIN)
        s_i = γ(r)  if a_i <  1/N   (departure < 0, a LOSS)

This reduces *exactly* to Eqs. (7)–(8) in the homogeneous case (cued α≥1/N→β;
each uncued (1−α)/(N−1)≤1/N→γ) and to the paper's inverted branch when α<1/N.
It is the only rule that (a) is a function of a single location's allocation,
(b) matches both branches the paper states, and (c) is continuous in the
allocation except at the a_i=1/N kink the paper itself introduces. Any
alternative (e.g. a "cued-label" rule that keeps β on location 0 regardless of
its allocation) would contradict the §2.3 reversal note. Documented here so
the choice is auditable.

## 2. Criterion optimiser — why coordinate ascent needed hardening

The per-group criterion landscape is **bimodal**: a "liberal/detect" attractor
(small c, maximises HR) and a "conservative/avoid-FA" attractor (large c,
maximises the no-FA product). Plain coordinate ascent from a single seed CAN
stall at the wrong attractor — caught during validation: on the config
d′=(2.0,0.5), v=5, V=0.25, variant B it returned R=0.9492 vs the exact joint
2-D grid's 0.9987 (a 0.05 miss). Fix:

- **G ≤ 2** (the homogeneous case and all of the VALIDATION + R_homog cells):
  exact joint grid over the Δc=0.05 c-grid (1-D for G=1, full 2-D outer
  product for G=2) — identical machinery to the C4/C5 base optimiser.
- **G ≥ 3** (Part 2 anti-cued; the full-simplex Part 1c): multi-restart
  coordinate ascent over the 2^G corner seeds (each group started at its
  change-side OR its CR-side standalone argmax) plus the all-zero seed; each
  step is an exact 1-D argmax.

**Validation (re-run any time):**
- G=2 vs C4 `optimal_criteria_R` on 6 configs incl. the previously-failing
  variant-B ones: max|Δ| = 4.4e-16.
- G=3 multi-restart vs an exact joint 3-D grid on 6 random configs:
  max|Δ| = 0.0.

So every number in `results.json` rests on a criterion optimiser proven to
find the joint optimum (not a coordinate-wise local one).

## 3. Grid resolutions and the "ΔR within slack" reading (Part 1c)

`homogeneous_optimum` sweeps α on the paper's Δα=0.005 grid; the full simplex
(Part 1c) uses a coarser Δ=0.05 lattice over the 3-simplex (≈1771 points) for
tractability. So R_full can be *slightly below* R_homog purely from the coarser
α-resolution on the cued axis — that is why two headline cells show ΔR≈−4e-4 to
−8e-4 with a_cued_full=1.000, uncued_spread=0: the full optimum is the SAME
all-on-cued policy, just snapped to the coarser grid. The only positive ΔR is
+6.8e-4 at the V=1/N, v=1, r=2 stress cell — within the 0.05-grid slack, at the
degenerate boundary where cued/uncued labels are meaningless (cf. CR-019), and
value-blind (so it cannot touch VDA). Hence "A8 binds" is flagged only when
ΔR>1e-3 AND uncued_spread>0.05; nothing meets both. A finer-grid confirmation
of the V=1/N corner is a cheap spawned follow-up (does not move the verdict).

## 4. The benefit-dominant concentration result (Part 1b) — interpretation

R″(0)>0 in 8/12 forced-uniform cells means equal split is a local *minimum*
of E[R] in the uncued subspace whenever r≳1 (and for convex h even at r=1).
Mechanism: β>γ (benefit-dominant) amplifies gains and cheapens losses, so the
optimiser is rewarded for creating one high-d′ "winner" among the uncued
rather than several mediocre ones — the same winner-take-all pressure that, on
the cued axis, drives α*→1. This is **not** a counterexample to any headline
claim (Part 1c shows it never binds at the model's own optimum), but it
*refutes the implicit reading* that homogeneity is a neutral/definitional
choice: it is a genuine constraint that happens to be slack in exactly the
regimes the paper sweeps. A re-derivation proving "uncued-concentration ⇒
cued-absorption" in closed form is the designated second attack vector.

## 5. Part 2 (graded suppression) — scope

Run value-blind (v=1) at V=0.40 so the uncued locations carry real attention
and the suppression gradient is visible; at v=5 everything uncued is squeezed
to the floor and the gradient is invisible (a degeneracy, not an absence).
The gradient is robust across r∈{0.398,1,2}. At r=0.398 the homogeneous
sub-case (w_anti = baseline) returns a *perfectly uniform* optimum — re-
confirming Part 1 — and suppression switches on only as the slot's validity
drops, which is the clean signature. The "rest" uncued and the cued *gain*
the attention freed from the suppressed slot (Kong et al. 2020 reciprocity;
paper §5.1 zero-sum framing).

## 6. What this run did NOT do (loose ends → backlog)

- No closed-form re-derivation of the homogeneity-optimality / cued-absorption
  theorem (the designated second vector to elevate A8 past WEAKLY-SUPPORTED).
- No finer-grid check of the V=1/N, v=1, r=2 +6.8e-4 corner.
- Did not vary N (only N=4) or test heterogeneous *validity* with N>4 graded
  neighbours (a closer match to the Wang & Theeuwes spatial gradient).
- Feeds A2 (single-global-r): heterogeneous allocation and heterogeneous gain
  asymmetry are cousins; a heterogeneous-r extension is the natural sibling.
