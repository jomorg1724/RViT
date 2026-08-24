---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-002-2026-05-25
started: 2026-05-25T00:00:00Z
ended: 2026-05-25T00:00:00Z
worked_on: RB-002
output_kind: simulation
claims_touched: [A1, C2]
artifacts_written:
  - Rebuild/sims/A1--rho-channel/run.py
  - Rebuild/sims/A1--rho-channel/README.md
  - Rebuild/sims/A1--rho-channel/output/results.json
  - Rebuild/sims/A1--rho-channel/output/figures/vda_curves_variantA.png
  - Rebuild/sims/A1--rho-channel/output/figures/vda_curves_variantB.png
  - Rebuild/sims/A1--rho-channel/output/figures/cf_vs_rho.png
  - Rebuild/CLAIM_LEDGER.md (A1 row updated with rb-002 backing + variant-B caveat)
  - Rebuild/REBUILD_BACKLOG.md (RB-002 -> done; +RB-023 spawned)
  - Rebuild/rebuilder_state.json (atomic; runs_completed 1 -> 2)
  - Rebuild/BUILD_LOG.md (rb-002 entry prepended)
papers_added: []
spawned_tasks: [RB-023]
---

# rb-002 — A1 ρ-channel headline simulation

## What I built

The first artifact under `Rebuild/sims/`:
`Rebuild/sims/A1--rho-channel/` — a manuscript-citable simulation that
sweeps the C2/Figure-4 headline cell (N=4, d'_max=2, f_0=0.5, h=√,
V=0.5, v=5), variants A and B, over ρ ∈ {0.0, 0.1, 0.2, 0.3, 0.4} and
a 28-point log-spaced r grid. Three deliverables landed under
`output/`: `results.json` (full numeric content + sha256), and three
PNG figures the rebuilt manuscript's §model and §results-A1 will
`\include{}`.

The script uses `Rebuild/model` as the single source of truth — no
primitives are re-implemented locally — and aborts with a non-zero
exit code if the ρ=0 recovery test fails.

## How it connects to the ledger

Discharges the simulation half of the A1 (CONTESTED) lever in the
[CLAIM_LEDGER](../CLAIM_LEDGER.md). The rebuilt strength the manuscript
may now state for A1 is exactly what the verdict licenses:

- The implicit §5.5 *pointwise upper bound on VDA* fails: at the
  headline cell, `VDA(r; ρ) > VDA(r; 0)` somewhere in r for every
  ρ > 0 (max excess +1.01e-2 at ρ=0.4; sign-flip r ≈ 0.38–0.56,
  variant A).
- Independence does upper-bound the **criterion fraction** in
  variant A monotonically: CF(0) ≥ CF(ρ) at every reference r ∈
  {0.398, 1.0, 3.162}.
- This upper-bound on CF is **variant-A specific** at the headline
  cell — variant B's CF(ρ) is essentially flat and not a clean
  upper-bound. The manuscript must therefore qualify the CF claim by
  reward convention. This caveat is the kind of distributional /
  conditional voice the prompt's §3.3 *unifying reframe* demands.

The C2 peak-VDA at ρ=0 (0.07986 at r=0.3831) is also corroborated as
a side product of the recovery test; C2's row in the ledger remains
unchanged but the cross-check is now byte-for-byte.

## Simulation evidence

- **Recovery, ρ=0** (variant A, three reference r):
  | cell    | rebuilt VDA | reviewer VDA | rebuilt CF | reviewer CF | max\|d\| |
  |---------|-------------|--------------|------------|-------------|----------|
  | r=0.398 | 0.0797189   | 0.0797189    | 0.829519   | 0.829519    | 0.00e+00 |
  | r=1.0   | 0.0398251   | 0.0398251    | 0.728228   | 0.728228    | 0.00e+00 |
  | r=3.162 | 0.0080890   | 0.0080890    | 0.640938   | 0.640938    | 0.00e+00 |
  Peak VDA(r; 0) = 0.07986 at r = 0.3831 (reviewer: 0.07986 @ r ≈ 0.383).

- **VDA(r) variant A peak-by-ρ** (from results.json `vda_curves_A.by_rho`):
  ρ ∈ {0.0, 0.1, 0.2, 0.3, 0.4} → peak VDA ∈
  {0.07986, 0.08110, 0.07955, 0.07763, 0.07368}, peak r ∈
  {0.3831, 0.3831, 0.3831, 0.3980, 0.3980}. Upper-bound check returns
  False for every ρ > 0; sign-flip r ∈ {0.383, 0.464, 0.562, 0.562}
  for ρ ∈ {0.1, 0.2, 0.3, 0.4}.

- **CF(ρ) variant A** at three r — monotone-down at every r (see
  build-log table). Variant B at the same r — essentially flat (small
  non-monotone bumps), reported honestly.

- **Slepian** sanity at fixed (d_c, d_u, c_c=c_u=0.5): P_no-fa(ρ)
  monotone-up across ρ ∈ {0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8};
  independence is the minimum.

- **Determinism**: sha256
  `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`.
  Re-running produces the same hash bit-for-bit.

Figures:
- [`output/figures/vda_curves_variantA.png`](../sims/A1--rho-channel/output/figures/vda_curves_variantA.png)
- [`output/figures/vda_curves_variantB.png`](../sims/A1--rho-channel/output/figures/vda_curves_variantB.png)
- [`output/figures/cf_vs_rho.png`](../sims/A1--rho-channel/output/figures/cf_vs_rho.png)

## What the manuscript can now say

The rebuilt §results-A1 section may state, citing this sim:

> *"At the C2 headline cell, promoting the per-location independence
> assumption (A1) to a tunable equicorrelation parameter ρ falsifies
> the §5.5 pointwise 'upper bound on VDA' self-characterisation:
> VDA(r; ρ) > VDA(r; 0) at r ≳ 0.5 for every ρ > 0 in our sweep
> (max excess +1.01% absolute reward at ρ = 0.4; peak VDA itself rises
> by +1.6% at ρ = 0.1). The correct statement of what independence
> upper-bounds is the **criterion fraction**: CF(r; 0) ≥ CF(r; ρ) at
> every r in our reference set under reward variant A, monotonically.
> The CF upper-bound is variant-specific — under variant B (uniform
> CR = 1) CF(ρ) is essentially flat at the headline cell — so we report
> the CF upper-bound as a variant-A result and the variant-B
> sensitivity as a qualifier rather than a universal claim. The
> mechanism is the Slepian-monotonicity of the equicorrelated Gaussian
> orthant probability (Slepian 1962): raising ρ raises P_no-fa, which
> in variant A pulls more reward through the no-change-trial term in
> proportion to V v + (1 − V), preferentially boosting R(P3) more in
> absolute but less in relative terms than R(P1) — see the derivation
> in Appendix A (forthcoming, RB-003)."*

It does **not** yet license the same statement at non-headline cells.
That is RB-005's job (the 4,410-cell distributional sweep at
ρ ∈ {0, 0.2}).

## Next increment

Two equally good candidates; both unblocked by rb-002:

- **RB-003** (derivation): promote the equicorrelated 1-D quadrature
  identity, the booking decomposition (A1 enters E[R] in exactly one
  place: P_no-fa), and the Slepian-monotonicity argument into
  `Rebuild/derivations/A1--rho-channel.md` (full LaTeX), authored
  independently against the inherited model rather than copied from
  `Critique/derivations/A1--correlated-fa-upper-bound.md`. This is the
  cleanest direct unblocker of RB-004 (the manuscript model section).

- **RB-005** (simulation): the C1 4,410-cell distributional sweep at
  ρ ∈ {0, 0.2}, which would let the rebuild extend the variant-A CF
  upper-bound from "the headline cell" to "across the published
  parameter sweep" — i.e. promote the rb-002 result from a single-cell
  demonstration to a distributional claim.

Default recommendation for rb-003: **RB-003** (derivation), because
the model section (RB-004) is the bottleneck for several downstream
results sections (RB-009, RB-010, RB-011, RB-012). Derivations are
also cheaper than full grid sweeps and keep wall-clock low.

The variant-B caveat surfaced today also spawned **RB-023** as a
low-priority follow-up: a finer ρ-grid that brackets the sign-flip
r* tightly and quantifies how generic the variant-B flat-CF result is
across (r, V, v). Worth doing before the manuscript §results-A1 is
sealed, but not on the critical path.

## Wiki cross-references

Pre-section §11-style mechanism-keyword sweep (the manuscript section
hasn't been drafted yet, but the sim's deliverables will land in it):

- `research_db/papers/cohen-maunsell-2009-attention-correlation.md` —
  the empirical anchor for the ρ ≈ 0.2 bracketing the sweep uses.
  Already in the wiki via the reviewer's run-016/017 citations. **No
  new stub needed.**
- `research_db/papers/slepian-1962-one-sided-barrier.md` — the
  monotonicity argument's primary source. Should be added as a stub
  *when RB-003 lands* (the derivation needs it; the sim only needs it
  for the Slepian-curve sanity check, which already runs against the
  model module's `slepian_curve()`). **Deferring the stub creation to
  rb-003** when the citation enters the manuscript.

No `research_db/` modifications this run. `audit.py` not invoked
(`-w` no-op).
