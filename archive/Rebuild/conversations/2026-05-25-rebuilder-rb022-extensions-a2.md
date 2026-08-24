---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-022-2026-05-25
started: 2026-05-25T23:50:00Z
ended: 2026-05-25T23:59:00Z
worked_on: RB-035
output_kind: manuscript
claims_touched: [A2]
artifacts_written:
  - Rebuild/manuscript/sections/extensions.tex (appended §extensions-A2 subsection, ≈370 LaTeX lines)
  - Rebuild/manuscript/figures/a2_vda_curves_spread.png (copied from sims/A2--heterogeneous-r/output/figures/)
  - Rebuild/manuscript/figures/a2_vda_peak_band.png (copied from sims/A2--heterogeneous-r/output/figures/)
  - Rebuild/manuscript/figures/a2_cf_contested_corner.png (copied from sims/A2--heterogeneous-r/output/figures/)
  - Rebuild/manuscript/refs.bib (+6 bib entries for heterogeneity citations)
  - Rebuild/manuscript/main.pdf (rebuilt; 40 pages / 2,379,430 bytes)
  - CLAIM_LEDGER.md (A2 row backing column updated; header reconcile-line moved to rb-022)
  - REBUILD_BACKLOG.md (RB-035 → done)
  - BUILD_LOG.md (rb-022 entry header + body)
  - rebuilder_state.json (RB-035 → done; runs_completed 21 → 22; manuscript_sections_drafted += RB-035; rb_022_manuscript_pdf_bytes)
papers_added: []
spawned_tasks: []
---

# rb-022 — §extensions-A2 manuscript subsection (RB-035)

## What I built

A full §extensions-A2 subsection in `Rebuild/manuscript/sections/extensions.tex`, sibling to the §extensions-A3 subsection that landed in rb-017. The file's section structure is now `\section{Lever extensions}` containing two filled subsections (§extensions-A3 conservation-family band, §extensions-A2 within-display heterogeneity) — matching the order in which the levers were wired into the rebuilt model (A3 at rb-015/rb-016; A2 at rb-019/rb-020/rb-021). The §extensions-A8 sibling subsection remains a STUB pending RB-021 (the A8 N-dim uncued sim).

The subsection contents (≈370 LaTeX lines added):

1. **Claim restatement** at defensible CONFIRMED-CONDITIONAL strength — between-preparation reading $R_1$ adopted explicitly in §model; within-display $R_2$ presented as the model extension this subsection quantifies; rebuild's claim is that heterogeneity is a bounded perturbation, not abolition. Six heterogeneity citations from research_db papers stubs (McAdams-Maunsell 1999, Reynolds-Heeger 2009, Treue 1999, Carrasco 2011, Ghose-Maunsell 2002, Sani 2017).
2. **Heterogeneous-$r$ d$'$-map** (Eq. d-prime-hetero) stating $d'_i(\alpha_i, r_i; p)$ with per-slot branch criterion + recovery contract notes (rb-019 byte-for-byte sha256 `0486921f…`; rb-020 $\le 2.78\times 10^{-10}$ sha256 `883ea15a…`).
3. **Empirical-band paragraph + Table tab:a2-rb021-summary** — 5-test summary of the rb-021 sim at the C2 headline cell, four columns ($\rho \times s$), all cells drawn verbatim from `results.json`.
4. **Four numbered findings**: (F1) equal-split criticality conditional on homogeneity, $\rho$ amplifies the residual ~2×; (F2) allocation $\Delta R \le 1.48\times 10^{-4}$ cost-dominant with **A1 $\rho=0.2$ suppression by ~50%**, $\Delta R = 0$ exactly benefit-dominant; (F3) **C2 peak coordinates invariant under spread at fixed $\rho$**, A1 offset $\Delta\mathrm{VDA}^\star = 0.00158$ itself spread-invariant — **A1 and A2 compose orthogonally at the C2 peak**; (F4) variant-B contested-CF corner moves UP by $+0.0015$ / $+0.0016$ at $s = 0.3$ — corner not deepened by A2 at either $\rho$ panel.
5. **Three figures** copied from `Rebuild/sims/A2--heterogeneous-r/output/figures/` to `Rebuild/manuscript/figures/` with `a2_` prefix.
6. **Scope paragraph** deferring variant-B (RB-036), larger multiplicative spreads (RB-037), N-dim A8 sim (RB-021), and a closed-form $\Delta R = O(\mathrm{Var}(\boldsymbol{r}))$ derivation.
7. **Reproducibility paragraph** citing rb-021 sha256 `22b183f9…`, rb-019 sha256 `0486921f…`, rb-020 sha256 `883ea15a…`, plus the rb-021-embedded recovery contract.

The manuscript build is 4-pass pdflatex+bibtex clean. One TeX Live 2026basic gap surfaced — `multirow.sty` is not in `basic`. **Fix**: restructured Table 4's column header to use plain `\multicolumn{2}{c}` over a single `Test` label row, no `multirow` required. Same visual layout. PDF: **40 pages / 2,379,430 bytes** (was 35 pages / 2,165,118 at rb-018 = +5 pages, +214 KB). 0 undefined references, 0 LaTeX warnings beyond cosmetic hyperref Unicode messages on math macros in cross-ref titles.

## How it connects to the ledger

The A2 verdict (`Critique/verdicts/A2--single-global-r.md`) is `current_label: CONFIRMED-CONDITIONAL` (live). The verdict's two-vector argument:

- **Vector 1 (literature, run-014)** — the empirical premise of a single global $r$ is decisively false (V1-vs-V4, eccentricity, feature similarity, task timing all heterogeneous).
- **Vector 2 (re-derivation, run-015)** — under the between-preparation reading $R_1$, heterogeneity's consequence is bounded: $\Delta R \le 1.5\times 10^{-4}$ over all interior cells at $\pm 30\%$ uncued spread; equal-split is critical iff $r_i$ are equal but the restricted Hessian stays negative-definite on the smooth branch; cued-absorption pre-emption empties the uncued budget at every value-contrast cell; the C2 peak is essentially invariant under spread; the variant-B contested-CF corner is not deepened.

The §extensions-A2 subsection adopts these two strengths exactly:
- The empirical-premise sentence cites the 6 heterogeneity papers.
- The model extension states the d$'$-map (Eq. d-prime-hetero) with rb-019 + rb-020 recovery contracts.
- The 4 findings reproduce the live-verdict numerics on the rebuild's own substrate (rb-021), with one new finding the reviewer's CR-048 did not surface: **A1 $\rho=0.2$ suppresses the cost-dominant $\Delta R$ by ~50%** (the reviewer's harness was $\rho=0$ only).

**Strength ceiling honoured**: the subsection never claims heterogeneity abolishes any C-row finding. Every "invariant" or "bounded" word is hedged to the (variant, $\rho$, $s$, cell) panel actually probed; variant-B replication, larger multiplicative spreads, and the full N-dim simplex are explicitly listed in the Scope paragraph as deferred.

**Discharge column**: the CLAIM_LEDGER A2 row's backing column gains "Manuscript drafted: …§extensions-A2 (rb-022, RB-035)". Strength unchanged — the row was already licensed at "bounded perturbation, no headline claim shifted" by rb-021; rb-022 turns that license into a written subsection in the PDF.

## Simulation evidence

This is a manuscript-prose increment. All numerical content is drawn verbatim from the rb-021 sim's `results.json` (sha256 `22b183f942d6b1f8868848ec1143ab959afd78c72cd6d3704763eedf5713e615`, 27.2 s wall-clock on python3.13 / scipy 1.17.1 / numpy 2.4.4, deterministic — re-run produces byte-identical `results.json`). Every claim maps to a specific cell of Table tab:a2-rb021-summary or to one of the three figures.

No new sim was run; no new model code was written. The pre-existing recovery contracts of the rebuilt model module are unchanged:
- rb-001 `test_recovery.py` sha256 `d3c62215…` (A1 $\rho \to 0$ recovery, 7/7 PASS) — untouched.
- rb-015 `test_conservation_family.py` sha256 `f4f57a89…` (A3 conservation-family, 14/14 PASS) — untouched.
- rb-019 `test_heterogeneous_r.py` sha256 `0486921f…` (A2 d$'$-map homogeneous-$r$, 5/5 PASS) — untouched, cited.
- rb-020 `test_general_policy.py` sha256 `883ea15a…` (A8 N-dim full policy, 7/7 PASS) — untouched, cited.

## What the manuscript can now say

The exact claim §extensions-A2 may now state at the rebuild-strength ceiling:

> "Within-display heterogeneity admits per-location $r_i$ and breaks the equal-split exchange symmetry the homogeneous A8 result relies on. Empirically, however, this is a bounded perturbation on every headline number probed: at $V=0.5, v=5, N=4$, peak $\mathrm{VDA}$ and peak $r^\star$ are invariant to $\le 10^{-5}$ absolute under $\pm 30\%$ uncued spread at every $\rho \in \{0, 0.2\}$, and the A1 $\rho$-channel offset at the peak is itself spread-invariant — the A2 and A1 levers compose orthogonally at the C2 peak. The allocation deviation $\Delta R$ is bounded by $1.5\times 10^{-4}$ at the cost-dominant probe cell and is zero exactly at the benefit-dominant cued-absorption cell at every $(s, \rho)$; one suggestive asymmetry — $\rho=0.2$ suppresses the cost-dominant $\Delta R$ by $\sim 50\%$. At the rb-005 variant-B minimum-CF corner, $s=0.3$ raises $\mathrm{CF}$ by $+0.0015$ ($\rho=0$) and $+0.0016$ ($\rho=0.2$) — the contested-CF corner is not deepened by A2 spread, regardless of $\rho$." (`Rebuild/sims/A2--heterogeneous-r/`, pre-hash sha256 `22b183f9…`, 27 s wall-clock.)

It does **not** yet license:

- (a) any variant-B statement about the four findings — requires RB-036, queued.
- (b) any statement about multiplicatively asymmetric uncued spreads with $k \in \{1.5, 3\}$ under $\rho$ — requires RB-037, queued.
- (c) any N-dim full-simplex result (the §extensions-A8 sibling subsection) — requires RB-021 (A8 N-dim sim), queued.
- (d) any closed-form $\Delta R$-vs-$\mathrm{Var}(\boldsymbol{r})$ scaling theorem — requires a future formal derivation increment.

## Next increment

**RB-021** (A8 N-dim uncued allocation sweep — sibling to rb-021 the A2 sim, sweeping the heterogeneous-uncued simplex policy through `er_full_policy` to test whether the A8 homogeneity-optimality condition holds beyond the reviewer's headline cell). That sim's results feed a §extensions-A8 subsection in the same `extensions.tex` file, completing the heterogeneity thread architecturally: §extensions-A3 done (rb-017), §extensions-A2 done (rb-022, this run), §extensions-A8 still queued.

Alternative parallel options (all unblocked):
- RB-026 (C2 $r^\dagger(v; \rho)$ closed-form, prereq RB-006 done) — promote the rb-004 $r^\dagger(v)$ to joint $(v, \rho)$ via the same one-factor GH reduction.
- RB-033 (A3 formal derivation, prereq RB-019 done) — fills the §appendix-deriv-a3 stub.
- RB-024 (closed-form CF<0.5 boundary, prereq RB-005 done) — sharpen the empirical 22% frac<0.6 at $\rho=0.2$ into a closed-form predicate over $(r, V)$ at fixed $v$.
- RB-036 / RB-037 (variant-B / multiplicative-spread A2 replications).

RB-021 is preferred — it discharges the A8 row's last queued sim license, leaving the rebuilt manuscript with the A1 + A3 + A2 + A8 lever quartet all wired AND prose-documented; the limitations / abstract / intro increments then become the remaining structural manuscript work.

## Wiki cross-references

Wiki sweep performed for keywords {within-display heterogeneity, location-specific gain, feature-similarity gain, eccentricity sign-reversal, task timing, gain modulation, equal-split criticality, exchange symmetry, simplex tangent gradient, allocation deviation, cued absorption, C2 peak invariance, variant-B contested-CF corner, criterion fraction, A1×A2 interaction, between-preparation reading}. All 6 cited papers already have research_db stubs:
- `research_db/papers/mcadams_maunsell1999_v4_tuning.md` — McAdams & Maunsell 1999, J Neurosci, V4 orientation-tuning attention.
- `research_db/papers/reynolds_heeger2009_normalization.md` — Reynolds & Heeger 2009, Neuron, normalization model.
- `research_db/papers/treue_martinez_trujillo1999_feature_attention.md` — Treue & Martínez Trujillo 1999, Nature, feature-based attention.
- `research_db/papers/carrasco2011_visual_attention_25y.md` — Carrasco 2011, Vision Research, 25-year review.
- `research_db/papers/ghose_maunsell2002_task_timing.md` — Ghose & Maunsell 2002, Nature, task timing gates V4 attentional modulation.
- `research_db/papers/sani2017_temporal_v4_gain.md` — Sani et al. 2017, J Neurophysiology, temporally evolving V4 gain.

No new `research_db/papers/` stubs added — every needed citation was already wired. `audit.py` not re-run (no wiki writes).
