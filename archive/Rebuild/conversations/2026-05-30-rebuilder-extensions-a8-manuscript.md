---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-028-2026-05-30
started: 2026-05-30T09:03:00Z
ended: 2026-05-30T09:14:00Z
worked_on: RB-042
output_kind: manuscript
claims_touched: [A8, A1, A3]
artifacts_written:
  - Rebuild/manuscript/sections/extensions.tex (≈420 LaTeX lines added: §extensions-A8 subsection + 4-word edit to §extensions intro)
  - Rebuild/manuscript/figures/a8_simplex_dr.png (copied from sim)
  - Rebuild/manuscript/figures/a8_curvature.png (copied from sim)
  - Rebuild/manuscript/figures/a8_anticued_suppression.png (copied from sim)
  - Rebuild/manuscript/main.pdf (recompiled: 51 pages / 2,763,376 bytes)
  - Rebuild/CLAIM_LEDGER.md (A8 row backing column updated; "Last reconciled" updated to rb-028)
  - Rebuild/REBUILD_BACKLOG.md (RB-042 → status: done)
  - Rebuild/rebuilder_state.json (atomic write via tempfile + mv; runs_completed 27→28; RB-042 added to done_task_ids; rb_028_manuscript_pdf_bytes recorded)
  - Rebuild/BUILD_LOG.md (rb-028 entry inserted at top)
papers_added: []
spawned_tasks: []
---

## What I built

I drafted the **§extensions-A8** subsection of the rebuilt manuscript
(`Rebuild/manuscript/sections/extensions.tex`), discharging RB-042 and
landing the manuscript-side companion to the rb-027 A8 N-dimensional
uncued-allocation sweep. The subsection follows the established
§extensions-A3 (rb-017) and §extensions-A2 (rb-022) rhythm:
claim-restatement at defensible strength → lifted-model paragraph →
empirical sweep description → numbered Findings → Scope-and-what-
remains → Reproducibility. I also touched the section's introductory
paragraph (lines 38–53 of the section file) to update its bookkeeping
("Two further" → "Three further"; "A2/A8" → "A2, A8 split"), since A8
is now its own subsection rather than co-listed with A2 as a stub.

The subsection includes:

- **Claim restatement** at the live A8 ceiling (CONFIRMED-CONDITIONAL):
  homogeneity is innocuous at the model's own optimum under the
  inherited $(\corr = 0, p = 1)$ regime; the rebuild adds one new
  conditional from the rb-027 sweep at $p = 0$.
- **Lifted policy-space paragraph** stating the rebuilt model's
  $N$-dimensional simplex policy through `er_full_policy(alloc,
  valid, v, r_vec, cell)` (rb-020 sha256 `883ea15a…`, 7/7 PASS,
  $\max|\Delta| \le 2.78\times 10^{-10}$ recovery contract against
  `optimal_R` under canonical homogeneous allocation), with the
  grouped cued/uncued criterion structure made explicit and the A1
  channel threaded end-to-end through the joint no-FA integrand.
  The d-prime map is cross-referenced to `eq:d-prime-hetero` of
  §extensions-A2 (so no equation is restated).
- **Table tab:a8-rb027-summary** — a 24-row Part 1c × p table over the
  six CR-036 decisive cells × $(\corr, p) \in \{0, 0.2\} \times
  \{0, 1\}$, reporting $\Delta R$, uncued spread, and a binds yes/no
  column. The two binding panels (both at symm-stress-r10 under
  $p = 0$) are bolded.
- **Five findings F1–F5** as separate `\paragraph{}`-headed blocks
  with three accompanying figures:
  1. **F1**: structural recovery at $(\corr = 0, p = 1)$ — 0/6 binds,
     max $\Delta R = 6.82 \times 10^{-4}$.
  2. **F2**: the new conditional — A8 binds at $p = 0$ in the
     symm-stress-r10 cell ($V = 1/N = 0.25$, $v = 1$, $r = 10$,
     variant A) with $\Delta R = +2.79 \times 10^{-3}$ at $\corr = 0$
     and $+3.68 \times 10^{-3}$ at $\corr = 0.2$; ρ amplifies by 32%.
     Full-simplex optimum at $(0.5, 0, 0, 0.5)$ vs homogeneous
     $\alpha_c \approx 0.05$. At $p = 1$ same cell shows $\Delta R < 0$
     — the sign-flip is the conservation-form mechanism. Figure
     `fig:a8-simplex-dr` overlays all 24 panels.
  3. **F3**: non-local character — $R''(0)$ along the symmetry-
     preserving redistribution direction is negative in 20/20 panels
     of (cell × ρ × p), so equal-split is a local max everywhere
     tested. The F2 binding is therefore globally optimal at a
     far-away simplex corner that local gradient information from the
     homogeneous policy cannot find. Figure `fig:a8-curvature`.
  4. **F4** + **Table tab:a8-rho-curv-ratio**: ρ-amplification of
     $|R''(0)|$ at $p = 1$ is mean 1.048, max 1.135, min 0.941 (one
     cell suppresses by 6%) — much weaker than the rb-021/A2 ~2×
     amplification of the equal-split criticality residual. The
     subsection states the interpretation: A2 breaks per-location
     asymmetry exchange symmetry which the joint no-FA integrand
     inherits directly; A8 breaks per-location allocation exchange
     symmetry which the integrand inherits only through second-order
     curvature on a homogeneous $\dprime$ — a higher-order coupling
     that is small.
  5. **F5**: Wang–Theeuwes-style anti-cued graded suppression
     monotone + strictly below at both $\corr \in \{0, 0.2\}$; ρ
     only weakly perturbs (shifts the $a_{\mathrm{anti}}^\star = 0$
     collapse from $w_{\mathrm{anti}} = 0.075$ to $0.050$). Figure
     `fig:a8-anticued-suppression`. The behavioural-anchor paragraph
     cites two pre-existing bib entries (no new bib).
- **Scope** explicitly deferring variant-B replication (RB-043), finer
  r-grid (RB-044), $N > 4$ generalisation, sim-boundary hardening
  (RB-045), and the closed-form A8-binding-onset locus (a future
  Slepian-style derivation — not queued because the standard Slepian
  inequality bounds orthant probabilities not their gradients, and
  the derivation is non-trivial).
- **Reproducibility** paragraph citing the rb-027 deterministic
  sha256 `beb2aa87…` and four pre-existing recovery contracts
  unchanged (rb-001 / rb-015 / rb-019 / rb-020).

## How it connects to the ledger

The subsection lands the §extensions-A8 manuscript prose at the
**rebuild-strength ceiling** licensed by the live A8 verdict
(CONFIRMED-CONDITIONAL) plus the new conditional licensed by rb-027.
Specifically:

- F1 lands the "A8 innocuous at the model's own optimum" headline at
  the **defensible** structural-reproduction strength (it is a
  reproduction of CR-036, not an independent statement).
- F2 lands the **new conditional** the rebuild contributes (A8 binds
  at $p = 0$ in the high-r symm-stress cell, ρ-amplified by 32%) —
  stated only as a conditional, not as a uniform statement.
- F3 keeps the "non-local" qualifier explicit, so the reader knows the
  binding cannot be approximated by local curvature.
- F4 reports the ρ-amplification ratios as a band (max 1.135, min
  0.941, mean 1.048) per the §3.3 unifying-reframe convention — not as
  a uniform amplification factor.
- F5 keeps the Wang–Theeuwes citation at "the rebuilt model offers a
  normative-optimal mechanism" strength, not at "uniquely predicted by
  the rebuilt model" — the latter would over-state the result.

The A8 row in `CLAIM_LEDGER.md` is updated to note the manuscript
subsection backing; **no strength change** (the row was already
licensed at the joint structural-recovery + new-conditional ceiling
by rb-027; rb-028 turns that license into manuscript prose with a
stable table / figure / proposition label set).

**No verdict-label drift in the live ledger.** All 10 labels match
the §3 table of `agents/paper_rebuilder_prompt.md` v0.2 (the A6 drift
to WEAKLY-SUPPORTED was already flagged in the CLAIM_LEDGER
front-matter at rb-018).

## Simulation evidence

This is a manuscript-increment run; no new simulation is produced.
All numerics flow from existing artefacts:

- **rb-027** A8 N-dim sweep, deterministic sha256
  `beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b`,
  72.2 s wall-clock on python3.13 / scipy 1.17.1 / numpy 2.4.4. The
  source `results.json` was read at
  `Rebuild/sims/A8--nd-uncued-sweep/output/results.json`.
- **Three figures** copied from
  `Rebuild/sims/A8--nd-uncued-sweep/output/figures/` to
  `Rebuild/manuscript/figures/` with the `a8_` prefix:
  - `a8_simplex_dr.png` — Finding 2 headline bar chart.
  - `a8_curvature.png` — Finding 3 curvature heatmap.
  - `a8_anticued_suppression.png` — Finding 5 graded-suppression curve.
- **Four model-test recovery contracts** are cited by digest in the
  Reproducibility paragraph and unchanged after this run (no model
  code touched):
  - rb-001 `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`
    (A1 channel, 7/7 PASS)
  - rb-015 `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`
    (A3 conservation family, 14/14 PASS)
  - rb-019 `0486921f8a4e253a1682ee0731e52c7de800bf6c3dbb1b5e8ff3200602454c7e`
    (heterogeneous-r d-prime map, 5/5 PASS)
  - rb-020 `883ea15af9fd069e04c05ff156d65f33a7d25278891092539c6441d2248c3d39`
    (N-dim general policy, 7/7 PASS)

**Build verification**: 4-pass `pdflatex` + `bibtex` clean (pass 1 OK
→ bibtex no-op → pass 2 settles refs → pass 3 byte-stable, 0
undefined refs, 0 LaTeX warnings beyond cosmetic hyperref
Unicode-token-in-section-header warnings — the same set seen at
rb-022 and rb-026). Final PDF: **51 pages, 2,763,376 bytes** (was 49
pages / 2,587,742 bytes at rb-026 — +2 pages, +175,634 bytes, in line
with the rb-017 +6 / rb-022 +5 §extensions-subsection precedent;
slightly lighter because rb-028 reuses `eq:d-prime-hetero` from
§extensions-A2 rather than re-stating the d-prime map).

## What the manuscript can now say

At the rebuild-strength ceiling, the §extensions-A8 subsection
licenses the following statements:

1. The inherited homogeneous-uncued allocation lifts to the full
   $\Nloc$-simplex via `er_full_policy`, which reproduces the
   inherited model under the canonical homogeneous allocation to
   $\max|\Delta| \le 2.78 \times 10^{-10}$ at both $\corr \in \{0,
   0.2\}$ (rb-020 recovery contract).
2. Under the inherited $(\corr = 0, p = 1)$ pair, A8 is innocuous at
   every CR-036 decisive cell (F1 replicates the reviewer's headline
   exactly: 0/6 binds, max $\Delta R = 6.82 \times 10^{-4}$).
3. Under multiplicative conservation $p = 0$, A8 binds at the
   high-$\Rsens$ symmetric-stress benefit-dominant corner ($\valid =
   1/\Nloc$, $\val = 1$, $\Rsens = 10$, variant A) by $\Delta R = +2.79
   \times 10^{-3}$ at $\corr = 0$ and $+3.68 \times 10^{-3}$ at
   $\corr = 0.2$ — a 32% A1 amplification.
4. Equal-split is a local maximum at the homogeneous $\alpha^\star$
   in every $(\text{cell}, \corr, p)$ panel tested, so the
   Finding-2 binding is non-local.
5. The Wang–Theeuwes-style anti-cued graded-suppression gradient of
   CR-036 Part 2 survives the A1 channel at $\corr \in \{0, 0.2\}$,
   preserving the rebuilt model's behavioural-anchor finding.

The manuscript does **not** license statements about $N > 4$
generalisation, variant-B reproduction of F2, the exact $r$-locus of
the F2 binding's onset/termination, or a closed-form A8-binding
predicate — all queued (or, for the closed-form predicate,
acknowledged as a non-trivial future derivation).

## Next increment

Per §4.1 of the mission, the natural next increment is one of:

- **RB-033 (A3 derivation)** — power-mean conservation family in the
  rebuild's voice; would convert the empirical Theorem 3.2 and
  Proposition 3.1 of §extensions-A3 into a formal Hardy–Littlewood–
  Pólya argument and land an `§appendix-deriv-A3` companion to
  rb-024's `§appendix-deriv-C2`. Low priority but a clean derivation
  increment.
- **RB-029 (A1 dormant-cell amplification sim)** — finer V-grid on the
  rb-010 sign-flip map at $r = 0.3$ (cost-dominant), bracketing the
  $(V \approx 0.7, v = 10)$ "dormant cell" where independence
  delivers $\VDA \approx 0.0007$ but $\corr = 0.2$ lifts it to
  $0.0676$. This is the most striking single qualitative finding of
  rb-010 and would feed a falsifiable-prediction paragraph in
  §results-A1 / the §5.2-replacement design recommendations.
- **RB-040 (C2 Slepian-analogue derivation)** — formal proof of
  $\partial I_c/\partial\rho > 0$ and $\partial I_u/\partial\rho > 0$
  at the asymmetric P3 boundary, promoting rb-023's 5/5 empirical
  sign-match to a proposition.

I do not promote any of these to immediate execution; the next
scheduled run will pick from `REBUILD_BACKLOG.md` per the standard
selection rule.

## Wiki cross-references

No `research_db/` sweep was performed this run. Rationale: the
§extensions-A8 subsection cites only artefacts already in the
rebuilt manuscript ecosystem (`eq:d-prime-hetero` from §extensions-A2,
`er_full_policy` from `Rebuild/model/`, the rb-027 sim, four
pre-existing recovery digests) plus two pre-wired behavioural
citations (`wang_theeuwes2018_statistical_learning_distractor_suppression`
and `failing_theeuwes2018_selection_history`, both already in
`refs.bib` from rb-013). No new external-literature claims were
introduced; no new mechanisms or concepts were named that would
require a wiki entry. `python3 research_db/tools/audit.py` was not
re-run (no wiki writes).
