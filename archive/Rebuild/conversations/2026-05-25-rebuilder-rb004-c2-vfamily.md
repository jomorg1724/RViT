---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-004-2026-05-25
started: 2026-05-25T12:52:00Z
ended: 2026-05-25T13:10:00Z
worked_on: RB-006
output_kind: simulation
claims_touched: [C2, A1]
artifacts_written:
  - Rebuild/sims/C2--vda-vs-r-vfamily/run.py
  - Rebuild/sims/C2--vda-vs-r-vfamily/README.md
  - Rebuild/sims/C2--vda-vs-r-vfamily/output/results.json
  - Rebuild/sims/C2--vda-vs-r-vfamily/output/figures/vda_curves_vfamily.png
  - Rebuild/sims/C2--vda-vs-r-vfamily/output/figures/r_dagger_vs_v.png
papers_added: []
spawned_tasks: [RB-026, RB-027]
---

## What I built

A simulation increment under `Rebuild/sims/C2--vda-vs-r-vfamily/` that
publishes the C2 non-monotonicity result at the headline cell — variant
A, `N=4, d'_max=2, f_0=0.5, h=sqrt, V=0.5` — at a v-family
`v ∈ {2, 3, 5, 8, 10}` on a high-resolution 84-point log-spaced
r-grid `r ∈ [0.1, 10]` (with the rb-002 reference pins `r ∈ {0.3831,
0.398, 1.0, 3.162}` baked into the grid), and overlays the rebuild's
A1 ρ channel at two values `ρ ∈ {0, 0.2}`. The headline contribution is
that each VDA(r) curve is annotated with the **closed-form escape
threshold r†(v)** derived in `Critique/derivations/C2--non-monotonic-vda.md`
§2.3, which the rebuild lifts from a §2.3 narrative into a published
analytic prediction with v-family numerics. The reviewer's derivation
gave the formula; the rebuild evaluates it at the P3-optimal criteria,
publishes the v-family table, and confirms the predicted ordering
`peak r* > r†(v)` for every v in the family.

The sim runs deterministically (no RNG; Gauss-Hermite quadrature is
fixed-table) in 18.9 s on the rebuilt model module
(`Rebuild/model/core.py`), with the byte-for-byte recovery contract
against rb-002 strengthened by a *fourth* pin at `r = 0.3831` (rb-002's
peak-r at the headline cell): the rb-004 VDA at that exact r is
`0.07985` vs rb-002's `0.07986` — Δ = 5.93e-6, within the 5-decimal
precision that rb-002's logged numbers carry. The finer 84-point grid
then raises the empirical peak to `VDA = 0.08300` at `r = 0.3758` (one
log-grid step left of rb-002's peak r), which is the rb-002 → rb-004
**grid-refinement gain**, not a regression.

## How it connects to the ledger

The live C2 verdict is `CONFIRMED-UNDER-ATTACK`. The mission §3.1 row
licenses C2 at its strengthened form: *"keep as a headline result and
strengthen it by stating the closed-form escape threshold r†(v) the
reviewer derived (the paper only showed the curve, not the
mechanism)."* This sim discharges the "strengthened headline" half of
that licence:

  * **Numerics.** r†(v) is published for v ∈ {1, 2, 3, 5, 8, 10}:
    `r†(v) = (0.343, 0.168, 0.099, 0.050, 0.022, 0.016)`. Monotone-
    decreasing in v as the §2.3 derivation predicts (more reward for
    the cued hit ⇒ marginal α-increase becomes attractive at lower
    r ⇒ smaller escape threshold).
  * **Empirical confirmation of §2.3.** The peak `r* = (0.501, 0.376,
    0.376, 0.376, 0.355)` for `v ∈ {2, 3, 5, 8, 10}` lies above r†(v)
    in every case (gap `+0.28` to `+0.35`). The peak r* clusters near
    `r†(v=1) ≈ 0.343` — sharper than the §2.3 derivation says
    explicitly, but exactly the §2.3 *mechanism*: VDA opens up where
    P1 has escaped (`r > r†(v)`) but P2 is still locked
    (`r < r†(v=1)`); the peak sits inside that interval.
  * **What the manuscript may now claim.** The CLAIM_LEDGER C2 row is
    upgraded from "confirmed; would-strengthen-with r†(v)" to
    "confirmed AND strengthened; r†(v) v-family numerics published".

The sim also touches **A1** (live `CONTESTED`) as a side product: the
ρ=0 vs ρ=0.2 overlay extends rb-002's headline-cell A1 result to the
v-family. The key finding is a **v-dependent sign-flip** of `Δpeak =
peak_VDA(ρ=0.2) − peak_VDA(ρ=0)`:

  | v   | Δpeak    |
  |----:|---------:|
  | 2   | −0.00197 |
  | 3   | −0.00407 |
  | 5   | −0.00345 |
  | 8   | −0.00067 |
  | 10  | **+0.00103** |

ρ=0.2 suppresses the peak at low v, and amplifies at v=10. This is the
rb-002 r-dependent A1 sign-flip generalised across the v-family — the
sign of `dVDA/dρ` at the peak depends on v, not just r. The
CLAIM_LEDGER A1 row already records the headline-cell sign-flip; this
v-family finding is **additional** material for the manuscript's
§results-A1 section (an open question for whether the rebuild wants to
include the variant-B parallel scan; spawned as RB-027 if so).

## Simulation evidence

- **Recovery** vs rb-002 at v=5, ρ=0, four pinned r values:
  - r=0.3831: VDA = 0.07985 vs 0.07986 (|Δ| = 5.93e-6) ✓
  - r=0.398:  VDA = 0.07972, CF = 0.82952 (|Δ| ≤ 1.07e-6) ✓
  - r=1.000:  VDA = 0.03983, CF = 0.72823 (|Δ| ≤ 4.87e-6) ✓
  - r=3.162:  VDA = 0.00809, CF = 0.64094 (|Δ| ≤ 1.73e-6) ✓
- **Grid-refinement gain**: finer-grid peak VDA = 0.08300 at r=0.3758
  (rb-002 peak was 0.07986 at r=0.3831). The original paper's peak
  number `≈ 0.080` is on the rb-002 / paper grid; the rebuild reports
  `0.083` on the finer grid as the value at the cell's true argmax.
- **r†(v) closed form**: monotone decreasing 0.343 → 0.168 → 0.099 →
  0.050 → 0.022 → 0.016 for v ∈ {1, 2, 3, 5, 8, 10}.
- **Peak consistency** (ρ=0): peak r* > r†(v) for every v; gap stable
  at +0.28 to +0.35; peak r* clusters near r†(v=1) ≈ 0.343 for v ≥ 3.
- **A1 v-dependent sign-flip** of Δpeak: suppression at v ∈ {2,3,5,8},
  amplification at v=10.
- **Output digest**: sha256 `09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`.
  Reproducible byte-for-byte on re-run (deterministic).

Figures:
- `output/figures/vda_curves_vfamily.png` — 2-panel (ρ=0 | ρ=0.2),
  five viridis-coloured VDA(r) curves per panel, peak markers, r†(v)
  vertical dashed lines on the ρ=0 panel.
- `output/figures/r_dagger_vs_v.png` — r†(v) trace v ∈ [1, 12], with
  family points highlighted and r†(v=1) reference line.

## What the manuscript can now say

The rebuilt §results-C2 may state:

> *"Non-monotonicity of VDA in r (C2) is a theorem of the model
> definitions: dE[R]/dα at α = 1/N has the sign of `K_c(v)·r −
> K_u/(N−1)`, so the escape threshold r†(v) := K_u(v) / [(N−1)·K_c(v)]
> separates the regime in which P1 commits attention non-uniformly
> from the regime in which P1 stays uniform. At the headline cell
> (N=4, V=0.5, variant A), r†(v) decreases monotonically from
> r†(v=1) = 0.343 to r†(v=10) = 0.016, and the empirical peak of
> VDA(r) lies above r†(v) for every v in {2, 3, 5, 8, 10} (gap +0.28
> to +0.35), clustering near r†(v=1) — exactly the §2.3 mechanism that
> VDA opens up where P1 has escaped uniform attention but P2 has not.
> Peak VDA magnitude grows monotonically with v (0.012 → 0.183 across
> the family). Promoting the A1 independence assumption to ρ = 0.2
> suppresses the peak at low v (−0.002 to −0.004) and amplifies it at
> v = 10 (+0.001), so the A1 sign-flip in dVDA/dρ has v-structure as
> well as r-structure."*

It does **not** yet license:
- a closed-form r†(v; ρ > 0) — the K_c, K_u formulas above assume
  ρ = 0 (the no-FA term factorises). A ρ > 0 closed form would
  predict the peak-r drift `0.501 → 0.631` (v=2) and `0.376 → 0.473`
  (v=3) observed empirically. Spawned RB-026.
- the same statement for variant B — needs RB-027 (low-priority
  follow-up).
- a conservation-family band on peak magnitudes — needs RB-019
  (A3 conservation generalisation).

## Wiki cross-references (mechanism-keyword sweep, mission §7.3)

Sweep keywords: "escape threshold", "value-directed attention",
"benefit-cost asymmetry", "criterion fraction", "non-monotonic"
across `research_db/papers/`, `research_db/concepts/`,
`research_db/threads/`.

- `research_db/papers/maunsell2015_attention_mechanisms.md` — review
  of dissociable attentional mechanisms (β/γ asymmetry). Cited in the
  paper's refs [11–14] and in the §2.3 derivation. The closed-form
  r†(v) gives Maunsell's "benefit vs cost" framing a model-internal
  knife edge — useful citation in the §results-C2 manuscript section.
- `research_db/papers/reynolds_heeger2009_normalization.md` —
  excitatory/suppressive gain decomposition; the theoretical
  scaffolding the β/γ parameterisation operationalises.
- `research_db/papers/mcadams_maunsell1999_reliability.md` —
  multiplicative sensitivity gain at attended locations (the β-side
  empirical substrate; r > 0 is the "benefit" side of the
  β/γ asymmetry).

No new stubs needed; existing wiki entries cover the citations the
strengthened C2 section will use. `audit.py` not run this run (no
wiki write).

## Next increment

The natural unblocked highest-priority next task is **RB-007** (C3
iso-VDA contour maps over (V, v) at r ∈ {0.3, 1, 3} and ρ ∈ {0, 0.2}),
which is independent of RB-006 but uses the same model module. It
gives the §results-C3 manuscript section its figure infrastructure and
replaces the paper's categorical §5.2 design advice (CONTESTED — "high
validity ⇒ negligible VDA regardless of other parameters") with a
quantitative iso-VDA contour band.

Alternatively, the unblocked **manuscript-skeleton** task **RB-022**
is now overdue: with four sim deliverables landed (rb-001 model,
rb-002 A1 headline-cell, rb-003 C1 distributional, rb-004 C2
v-family), the manuscript skeleton would let the next sections-RB
(RB-004, RB-009, RB-010) write directly into a real `manuscript/`
directory rather than continuing to defer.

The dependency-order argument (mission §4.1) suggests RB-022 first
then RB-010 (the C2 manuscript section, now unblocked by rb-004) or
RB-009 (the C1 manuscript section, unblocked by rb-003). Both
manuscript sections require RB-022 to exist; without the skeleton,
they would have to invent their own `\input{}` structure ad hoc.

## Ledger reconciliation (vs. mission §3, prompt v0.2)

Re-checked all 10 live verdict labels at the start of this run
(`grep current_label Critique/verdicts/*.md`). All 10 still match the
§3 table modulo the standing A6 drift (still WEAKLY-SUPPORTED, not
yet decisive). No new drift this run. CLAIM_LEDGER.md updated
"last reconciled" stamp to rb-004.
