---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-021-2026-05-25
started: 2026-05-25T23:00:00Z
ended: 2026-05-25T23:55:00Z
worked_on: RB-018
output_kind: simulation
claims_touched: [A2, A1]
artifacts_written:
  - Rebuild/sims/A2--heterogeneous-r/run.py
  - Rebuild/sims/A2--heterogeneous-r/README.md
  - Rebuild/sims/A2--heterogeneous-r/output/results.json
  - Rebuild/sims/A2--heterogeneous-r/output/figures/vda_curves_spread.png
  - Rebuild/sims/A2--heterogeneous-r/output/figures/vda_peak_band.png
  - Rebuild/sims/A2--heterogeneous-r/output/figures/cf_contested_corner.png
papers_added: []
spawned_tasks: [RB-035, RB-036, RB-037]
---

# rb-021 — A2 heterogeneous-r sweep simulation (RB-018)

## What I built

The rebuild's analogue of the reviewer's CR-048 / run-015
verification harness
(`Critique/replications/A2xA8--heterogeneous-r/verify_heterogeneous_r.py`),
scored end-to-end through the rebuilt module's `er_full_policy`
(rb-020) so the A1 ρ channel is preserved at every test.

`Rebuild/sims/A2--heterogeneous-r/run.py` is ~550 lines (heavily
commented; one section per test) carrying five independent probes:

0. **Validation (spread=0 byte-for-byte recovery).** At every (ρ, r)
   on the 21-point r-grid × 2 ρ = 42 cells of the headline cell
   (V=0.5, v=5), evaluate twice — once via the heterogeneous path
   with `spread=0`, once via the legacy `policies()`. Tolerance
   1e-9 (the rb-020 contract). **PASS:** max\|ΔVDA\| = 2.35e-10,
   max\|ΔCF\| = 2.98e-10.
1. **Criticality.** Tangent gradient on the uncued simplex at the
   interior-α cost-dominant cell (V=0.5, v=2, r=0.3, α*=0.660). The
   tangent norm ‖g − mean(g)‖ is exactly 0 at spread=0 (equal-split
   IS a critical point under homogeneous r), grows to 2.6e-3 at
   spread=0.3 ρ=0 and 5.8e-3 at spread=0.3 ρ=0.2 — ρ amplifies the
   asymmetry by ~2×.
2. **Allocation deviation, cost-dominant cell.** ΔR = R(simplex-opt)
   − R(equal-split) at the same (V=0.5, v=2, r=0.3, α*=0.660) cell,
   gridding the 2-D uncued simplex at step 0.02. ΔR scales linearly
   in var(r_i) at ρ=0 (1.4e-5 → 7.1e-5 → 1.5e-4) and **tightens
   under ρ=0.2 to 2.4e-5 → 7.5e-5** — ρ *suppresses* the cost-
   dominant allocation deviation by ~50%.
3. **Allocation deviation, benefit-dominant cell.** Same probe at
   (V=0.5, v=5, r=0.4, α*=1.000). ΔR = 0 exactly at every (spread,
   ρ) — cued absorption pre-empts the uncued lever regardless of ρ.
4. **C2 reframe — VDA peak vs r_cued across 8 (spread × ρ) panels.**
   At the headline cell (V=0.5, v=5), peak VDA varies by ≤ 1e-5
   across spreads ∈ {0, 0.1, 0.2, 0.3} at fixed ρ (0.07972 → 0.07971
   at ρ=0; 0.08130 → 0.08130 at ρ=0.2); peak r* fixed at 0.398 every
   panel. The ρ-channel offset at the peak (+0.00158) is itself
   spread-invariant.
5. **C1 contested corner.** Variant B, V=0.25, v=4, r=10 — the rb-005
   minimum-CF corner. spread=0.3 raises CF by +0.0015 (ρ=0) and
   +0.0016 (ρ=0.2). Corner not deepened by A2.

## How it connects to the ledger

A2 verdict (live): CONFIRMED-CONDITIONAL. The reviewer's reading is:
the empirical premise of a single global r is false but the
consequence for C1–C5 is *bounded*. The rebuild already adopted the
between-preparation reading and presented heterogeneous r_i as a
model extension (rb-019 `d_prime_hetero`, rb-020 `er_full_policy`).
rb-021 turns those wirings into an empirical band on the headline
numbers under the rebuilt model's full pipeline (ρ-aware,
conservation-aware).

**No strength change** in the A2 row of `CLAIM_LEDGER.md`. The row
was already licensed at "bounded perturbation, no headline claim
shifted"; rb-021 supplies the rebuild-voiced empirical artifacts.
The backing column gains the sim block and the four-finding
headline.

A small additional contribution to the A1 row: rb-021 documents that
the ρ-channel offset at the C2 peak is invariant under within-display
A2 spread up to ±30% — sharpens the A1 row's "three levers, not two"
framing by showing ρ and r are (at least at the headline cell)
mutually orthogonal in their effect on peak VDA.

## Simulation evidence

Pre-hash sha256: **`22b183f942d6b1f8868848ec1143ab959afd78c72cd6d3704763eedf5713e615`**.
Deterministic — verified across two independent re-runs.

Wall-clock: 27.2 s on python3.13 / scipy 1.17.1 / numpy 2.4.4.

Figures:
* `Rebuild/sims/A2--heterogeneous-r/output/figures/vda_curves_spread.png`
  — 8 VDA(r_cued) curves (2 ρ × 4 spread) overlaid. The four spread
  curves collapse to a single curve at each ρ — the C2 reframe
  headline.
* `vda_peak_band.png` — peak VDA★ and peak r★ vs spread. Two
  horizontal traces (one per ρ); the gap between them is the A1
  channel effect and is spread-invariant.
* `cf_contested_corner.png` — CF vs spread at the variant-B
  minimum-CF corner. Two flat horizontal traces (one per ρ); A2
  spread does not deepen the corner.

Pre-existing recovery contracts re-verified:
- rb-001 `test_recovery.py` sha256 `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f` unchanged (the sim doesn't touch model code).
- rb-020 `test_general_policy.py` sha256 `883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39` unchanged.

## What the manuscript can now say

The §extensions-A2 subsection (queued as **RB-035**) may state at the
strength quoted in the build log entry. The four findings (recovery,
criticality, ΔR bound + ρ-suppression, peak invariance, corner
non-deepening) are each backed by an explicit number + figure. The
mechanism for ρ-suppression of the cost-dominant ΔR is partially
explained in the README scope paragraph (the joint no-FA integral
under ρ>0 couples the heterogeneous d'_i partially across locations
— but no closed-form derivation is in scope this run).

## Next increment

Natural next: **RB-035** — draft §extensions-A2 manuscript subsection
(sibling to §extensions-A3 in `Rebuild/manuscript/sections/extensions.tex`).
Completes the A2 thread (model rb-019 → sim rb-021 → manuscript
rb-XXX) parallel to the A3 thread already at done (rb-015 → rb-016 →
rb-017). Then the rebuilt manuscript has the A1 + A3 + A2 levers
all wired AND prose-documented; A8 sim (RB-021) + its manuscript
subsection remain the last structural increments before the
abstract/intro/limitations sections can be drafted.

Parallel options (all unblocked, medium priority): RB-024 (C1
closed-form CF<0.5 boundary), RB-026 (C2 r†(v;ρ) closed form),
RB-033 (A3 formal derivation), RB-021 (A8 sim using `er_full_policy`).

## Implementation notes

One small finding logged in the run.py docstring: at the C2 headline
cell (V=0.5, v=5) every r in [0.1, 3.2] hits cued-absorption α*=1 in
the rebuilt model, vs the reviewer's CR-048 α*≈0.74 at his coarser
optimiser. So the criticality and allocation-deviation tests probe a
DIFFERENT interior-α cell (V=0.5, v=2, r=0.3, α*=0.660) — the rebuild's
analogue of the reviewer's "cost-dominant with large uncued budget"
regime. The C2 reframe sweep still uses the headline cell (V=0.5, v=5);
VDA(r) is non-monotonic there even though α*=1 throughout, because
VDA = R(P1) − R(P2) and R(P2) depends on α_vb = α*(v=1) which is
*interior*, so VDA(r) inherits its r-dependence through R(P2)'s
α_vb-evaluated d' map.

Initial run hit a NaN bug in the criticality finite-difference probe:
when α_at_test = 1.0 (cued absorption), the uncued allocation a_bar =
0 and the FD step a_bar - eps = -1e-4 triggered sqrt(negative) in the
h-transfer. Fixed by both (a) picking the interior-α cell (V=0.5, v=2,
r=0.3) and (b) capping eps_safe = min(eps, 0.45 * a_bar) so probes stay
strictly inside (0, 1).

Hash convention follows rb-016: `sha256_pre_hash` is the hash of the
JSON payload *before* the hash field is embedded; the printed digest
matches what re-running this script produces. `wall_clock_s` is
printed but deliberately NOT embedded in the hashed payload so
runtime noise across machines doesn't drift the digest.

## Wiki cross-references

Wiki sweep performed for keywords {heterogeneous r, within-display
heterogeneity, A2×A8 interaction, tangent gradient on simplex,
allocation deviation, equal-split criticality, cued absorption,
value-weight inequality, anti-cue, criterion fraction, correlated
noise, equicorrelated Gaussian}. No new `research_db/papers/` stubs
added — the citations needed are inherited from prior rb runs
(McAdams-Maunsell 1999, Reynolds-Heeger 2009, Treue 1999,
Carrasco 2011, Sani 2017, Ghose-Maunsell 2002 all in
`Critique/verdicts/A2--single-global-r.md`'s evidence dossier and
already mapped to research_db papers/ stubs via earlier reviewer
runs; CohenMaunsell2009 already wired). `audit.py` not re-run.

## Worktree / scope discipline

All artifacts under `Rebuild/`. No edits to anything outside `Rebuild/`.
No `Critique/` or `research_db/` writes. No renames or deletes. The
mission §1 override-resistant rule was not triggered.
