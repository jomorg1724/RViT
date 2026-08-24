---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-027-2026-05-30
started: 2026-05-30T00:00:00Z
ended: 2026-05-30T00:00:00Z
worked_on: RB-021
output_kind: simulation
claims_touched: [A8, A1, A3]
artifacts_written:
  - Rebuild/sims/A8--nd-uncued-sweep/run.py
  - Rebuild/sims/A8--nd-uncued-sweep/README.md
  - Rebuild/sims/A8--nd-uncued-sweep/output/results.json
  - Rebuild/sims/A8--nd-uncued-sweep/output/results.canonical.json
  - Rebuild/sims/A8--nd-uncued-sweep/output/results.json.deterministic_sha
  - Rebuild/sims/A8--nd-uncued-sweep/output/figures/a8_simplex_dr.png
  - Rebuild/sims/A8--nd-uncued-sweep/output/figures/a8_curvature.png
  - Rebuild/sims/A8--nd-uncued-sweep/output/figures/a8_anticued_suppression.png
  - Rebuild/CLAIM_LEDGER.md (top reconcile + A8 row backing column)
  - Rebuild/REBUILD_BACKLOG.md (RB-021 done; RB-042, RB-043, RB-044, RB-045 queued)
  - Rebuild/rebuilder_state.json
  - Rebuild/BUILD_LOG.md
papers_added: []
spawned_tasks: [RB-042, RB-043, RB-044, RB-045]
---

# rb-027 — RB-021 A8 N-dim uncued allocation sweep

## What I built

A simulation at `Rebuild/sims/A8--nd-uncued-sweep/` that lifts the reviewer's
CR-036 "A8 innocuous at the model's own optimum" finding from the inherited
(ρ=0, p=1) substrate to the rebuilt model's full (ρ × p) lever cube. The
sim composes the rebuilt `er_full_policy(alloc, valid, v, r_vec, cell)`
driver from rb-020 (sha256 `883ea15a…`, 7/7 PASS) with:

- **Part 1c**: full-simplex (step 0.05) vs homogeneous-constrained (α-grid
  step 0.005) optimum across CR-036's 6 decisive cells × ρ ∈ {0, 0.2} × p
  ∈ {1, 0} = 24 panels.
- **Part 1 curvature**: equal-split R″(0) along the symmetric redistribution
  direction [+1, +1, −2] at the homogeneous α*, across 5 CR-036 Part-1 cells
  × (ρ × p) = 20 panels.
- **Part 2**: anti-cued joint optimum on a step-0.02 grid, replicating
  CR-036 Part 2 (the Wang-Theeuwes statistical-learning link) at ρ ∈ {0, 0.2}
  for 9 anti-cued validity values per ρ panel.

Wall clock 72 s; deterministic sha256 of the canonical JSON dump (omitting
`wall_clock_seconds`): `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b`.
Verified byte-identical across reruns.

## How it connects to the ledger

- **A8 row, primary claim touched.** Discharges the "Sim (RB-021) still
  queued" license. The row's backing column now lists the rb-027 sim with
  the full F1–F5 finding block; the strength column gains **one new
  conditional**: at p=0 (multiplicative conservation), A8 binds in the
  high-r symmetric-stress benefit-dominant corner — ρ-amplified by 32%.
  The pre-existing "A8 innocuous at the model's own optimum under inherited
  (ρ=0, p=1)" claim remains confirmed (F1 recovery PASS).
- **A1 row, compositional axis.** F4 establishes that **ρ × A8 composition
  is more orthogonal than ρ × A2 composition** — the rb-021 A2 finding
  "ρ amplifies the equal-split criticality residual ~2×" does NOT
  generalise to the A8 N-dim uncued question (mean |R″(0)|-ratio 1.05,
  not 2). Refines the A1-channel-vs-other-lever composition picture.
- **A3 row, compositional axis.** F2 is a **conservation-form-dependent**
  A8 binding: it appears at p=0 (multiplicative) and disappears at p=1
  (additive). The A3 conservation order is the lever that unlocks the
  A8 binding, complementing the rb-016 A3-band finding (p=0 deepens C1's
  tail) with a structural A8 effect.
- **No verdict-label drift** (10/10 live verdict labels still match the §3
  table of `agents/paper_rebuilder_prompt.md` v0.2; only the §3 A6 entry
  remains stale, already flagged in CLAIM_LEDGER).

## Simulation evidence

### Numerical headlines (verbatim from `results.json` → summaries)

- **F1 recovery (ρ=0, p=1)**: 0/6 A8 binds; max dR = 6.82×10⁻⁴; threshold
  dR > 1×10⁻³ AND uncued_spread > 0.05.
- **F2 new conditional (p=0, symm-stress-r10)**: dR = +2.79×10⁻³ at ρ=0,
  +3.68×10⁻³ at ρ=0.2; full optimum at (a_cued=0.500, uncued_spread=0.500)
  vs homogeneous (a_cued≈0.050); ρ-amplification = 1.32×.
- **F3 curvature**: R″(0) negative in 20/20 (cell × ρ × p) panels. Largest
  |R″(0)| at v1-benefit-dom = 141 (ρ=0, p=1), driven by the small a_bar
  = 0.002 there.
- **F4 ρ-amplification at p=1**: mean ratio 1.048, max 1.135 (v1-reference),
  min 0.941 (v1-symmetric).
- **F5 anti-cued**: at both ρ panels, monotone-decreasing a_anti* AND
  a_anti* ≤ a_rest* AND strictly-below; ρ=0.2 only weakly perturbs the
  collapse w_anti at which a_anti hits 0 (from ~0.075 to ~0.050).

### Recovery contracts

- **Source**: rb-020 `er_full_policy` (sha256 `883ea15a…`, 7/7 PASS) — the
  sim is a pure consumer; no model code touched.
- **rb-001 `d3c62215…`**: unchanged after sim.
- **rb-015 `f4f57a89…`**: unchanged after sim.
- **rb-019 `0486921f…`**: unchanged after sim.
- **rb-020 `883ea15a…`**: unchanged after sim.

### Output hash

- Pre-computed: `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b`
  (deterministic sha256 of `output/results.canonical.json`).
- Persisted at `output/results.json.deterministic_sha`.

### Figures

- `output/figures/a8_simplex_dr.png` — headline F2 bar chart; the two red
  symm-stress-r10 bars at p=0 (rho=0, p=0 and rho=0.2, p=0) sit above the
  grey 1e-3 binding threshold; all other 22 bars sit below.
- `output/figures/a8_curvature.png` — diverging-colormap heatmap of R″(0)
  at the homogeneous α*; one panel per p; rows are ρ ∈ {0, 0.2}, columns
  are the 5 Part-1 cells. All cells red (negative).
- `output/figures/a8_anticued_suppression.png` — two-panel ρ × {a_anti*,
  a_rest*} vs w_anti curves; the a_anti* curve falls below the 1/N
  reference and below a_rest* across the gradient.

## What the manuscript can now say

At the A8-row strength ceiling, the §extensions-A8 manuscript subsection
(queued as RB-042) can state:

> The rebuilt model's lifted policy space — the N-dim uncued allocation
> simplex evaluated through `er_full_policy(alloc, valid, v, r_vec, cell)`
> — reproduces the reviewer's "A8 innocuous at the model's own optimum"
> headline (CR-036 Part 1c) exactly under the inherited (ρ=0, p=1) regime:
> across the 6 decisive cells, the full-simplex optimum coincides with
> the homogeneous-constrained one to within the 1×10⁻³ allocation-grid
> slack (max dR = 6.82×10⁻⁴). Under the rebuild's two added levers, A8
> acquires one new conditional: at multiplicative conservation (p=0),
> the high-r symmetric-stress benefit-dominant corner (V=1/N, v=1, r=10,
> variant A) admits a non-trivial full-simplex improvement of dR =
> +2.79×10⁻³ (ρ=0) → +3.68×10⁻³ (ρ=0.2), with the full optimum at
> (a_cued=0.5, uncued_spread=0.5) vs the homogeneous (a_cued≈0.05). The
> binding is non-local: R″(0) at the homogeneous α* along the symmetric
> uncued redistribution direction is negative in every tested cell, so
> equal-split remains a local max even where the global max lies far
> away. ρ=0.2 amplifies the binding by ~32%; ρ × A8 composition is
> more orthogonal than ρ × A2 composition (mean |R″(0)|-ratio 1.05 vs
> ~2× for A2 at the same cell list). The CR-036 anti-cued graded-
> suppression gradient (Wang-Theeuwes statistical-learning link)
> survives the correlation channel at ρ ∈ {0, 0.2}.

The manuscript does **not** yet license:
- variant-B replication of the F2 binding (RB-043),
- sharper r-grid bracketing of the p=0 binding onset (RB-044),
- closed-form predicate for the A8-binding boundary in (r, p, V, variant)
  — not yet queued.

## Next increment

**RB-042** — draft `Rebuild/manuscript/sections/extensions.tex §extensions-A8`,
sibling to the rb-022 §extensions-A2 subsection and the rb-017
§extensions-A3 subsection. This closes the last `§extensions` sibling
and discharges the rb-027 sim into manuscript prose, completing the
sim → manuscript-extensions wiring for the A2/A8 heterogeneity thread
(A2 done at rb-022; A3 done at rb-017; A8 pending).

The natural pattern: Table tab:a8-rb027-summary (24-row Part 1c block),
Findings F1–F5 each with a paragraph + figure, scope paragraph deferring
RB-043/RB-044, reproducibility paragraph citing the rb-027 deterministic
sha256. Expected build delta: ~3–4 pages added (extrapolated from rb-017's
+6 / rb-022's +5).

Dependency order: model (rb-020) → simulation (rb-027) → manuscript
(RB-042) — the standard §4.1 chain.

Parallel alternatives (all unblocked):
- **RB-033** — A3 formal derivation in rebuild's voice, fills the
  `§appendix-deriv-a3` stub placed by rb-017.
- **RB-024** — C1 closed-form CF<0.5 boundary derivation.
- **RB-040** — Slepian-gradient analytic locus for the cell-wise
  ∂VDA/∂ρ surface.

RB-042 is preferred — it lands the structural §extensions trio (A2, A3, A8)
before the manuscript work shifts toward the abstract / intro / limitations
bookends.

## Wiki cross-references

Sweep performed for keywords {N-dim uncued allocation, multi-dimensional
simplex policy, equal-split critical point, anti-cued graded suppression,
conservation × A8 interaction, ρ × A8 interaction, value-weight
inequality}.

- All behavioural citations needed for the Wang-Theeuwes link (Wang-
  Theeuwes 2018, Wang-Samara-Theeuwes 2019, Kong-Li-Wang-Theeuwes 2020,
  Failing-Theeuwes 2018, Hickey 2010, Posner 1980) already wired in
  `Rebuild/manuscript/refs.bib` from rb-013 (RB-012).
- All math-methods citations (Slepian 1962, Tong 1990, HLP1934, Sterbenz
  1974, Goldberg 1991) cited by full bibliographic reference per the
  math-methods scope inherited from rb-008 / rb-013 / rb-017 / CR-035 /
  CR-037 (not a rebuilder responsibility).
- **No new `research_db/papers/` stubs added**; `audit.py` not re-run
  (no wiki writes).

## Notes on execution

- Initial run crashed with `AssertionError: best_idx is None` in
  `Rebuild/model/core.py:965 optimal_ER_general`. Root cause: float-noise
  negative allocations from the simplex sweep (`a_rest = -1e-17` at the
  anti-cued joint optimum edge) → `np.sqrt(negative)` in `f_transfer` →
  NaN propagating through all criterion-grid evaluations → no seed beats
  `best_R = -inf`. Fixed at the sim boundary by clamping `np.maximum(alloc,
  0.0)` in the `_ER` wrapper before calling `er_full_policy`. The
  inherited model never produces negative alloc by construction so
  byte-for-byte recovery is preserved (no model code touched). Logged as
  RB-045 (low-priority model-side hardening).

- Determinism strategy: the initial `wall_clock_seconds` field in
  `results.json` broke byte-identical reruns. Switched the hash strategy
  to compute sha256 over a canonical (sort_keys=True, indent=2) JSON
  dump with `wall_clock_seconds` omitted. The canonical bytes are
  persisted alongside the human-readable dump so a verifier can
  re-compute the sha without re-running the sim.
