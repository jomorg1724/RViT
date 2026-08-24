---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-017-2026-05-25
started: 2026-05-25T23:00:00Z
ended: 2026-05-25T23:30:00Z
worked_on: RB-034
output_kind: manuscript
claims_touched: [A3, C2, C1, C5]
artifacts_written:
  - Rebuild/manuscript/sections/extensions.tex (NEW)
  - Rebuild/manuscript/main.tex (one \input{} line added)
  - Rebuild/manuscript/sections/appendix.tex (one stub subsection added: sec:appendix-deriv-a3)
  - Rebuild/manuscript/refs.bib (one bib entry added: HLP1934)
  - Rebuild/manuscript/figures/vda_curves_pfamily_v5.png (copy from rb-016 sim)
  - Rebuild/manuscript/figures/vda_peak_band.png (copy from rb-016 sim)
  - Rebuild/manuscript/figures/cf_histogram_pfamily.png (copy from rb-016 sim)
  - Rebuild/manuscript/figures/delta_cf_distribution.png (copy from rb-016 sim)
  - Rebuild/manuscript/main.pdf (rebuilt; 33 pages / 2,152,496 bytes)
  - Rebuild/CLAIM_LEDGER.md (A3 row backing column extended; header reconcile line updated)
  - Rebuild/REBUILD_BACKLOG.md (RB-034 status queued → done; touched timestamp updated)
  - Rebuild/rebuilder_state.json (atomic write; runs 16 → 17; RB-034 added to done + manuscript_sections_drafted; rb_017_manuscript_pdf_bytes added)
  - Rebuild/BUILD_LOG.md (header pre-written for crash recovery; body appended at end of run)
papers_added: []
spawned_tasks: []
---

# rb-017 — manuscript increment: §extensions-A3 (RB-034)

## What I built

A new manuscript section file
`Rebuild/manuscript/sections/extensions.tex`, wired into `main.tex`
between `sections/results.tex` and `sections/limitations.tex`, whose
first subsection §extensions-A3 discharges RB-034. The section
restates A3 at central-tendency / conservation-family-band strength;
introduces the power-mean conservation family $M_p(\beta, \gamma) = 1$
with $\beta/\gamma = r$ (eq:conservation-family) and its closed-form
weight pair (eq:beta-gamma-of-p); reports the C2 conservation-family
band on the peak (Table tab:a3-c2-peak-band, Figure
fig:a3-vda-curves-p-v5); promotes the *conservation-form-invariance
of the closed-form C2 escape threshold* to a stated **Proposition 3.1
($\rdagger(v)$ is conservation-form-invariant)** with a one-paragraph
proof from the uniform-attention-point collapse $d_c = d_u =
d_{\mathrm{base}}$ at $\alpha = 1/N$; reports the C1 conservation-
family band on the 4,410-cell sweep (Table tab:a3-c1-cf-band, Figures
fig:a3-cf-hist-pfamily and fig:a3-delta-cf-distribution); promotes the
rb-016 cell-wise monotonicity finding to a stated **Theorem 3.2
(per-cell $\Delta\CF \le 0$ monotonicity, empirical)** — 87.7%
strict-dec variant A, 81.0% variant B, 0 cells with $\Delta\CF > 0$
out of 4,410; and lands a one-paragraph **C5 conservation-form-
invariance corollary** ($\beta(1, p) = \gamma(1, p) = 1$ at every $p$
from eq:beta-gamma-of-p, so the C5 symmetric recovery survives any
choice in the family). The section closes with a scope paragraph
deferring the joint $(p, \corr)$ sweep, the RB-033 formal derivation,
the closed-form $\Delta\CF \le 0$ proof, and the variant-B $\corr$-
flatness interaction, plus a reproducibility paragraph citing
sha256 `055bf4ec…`, the rb-015 model-test sha256 `f4f57a89…`, and all
four rb-016 recovery tests verbatim.

Companion stub §appendix-deriv-a3 placed in `sections/appendix.tex` to
clear the forward reference; one new bib entry added to refs.bib
(HLP1934 — Hardy--Littlewood--Pólya 1934 *Inequalities*, by full
bibliographic reference; the math-methods wiki gap inherited from
rb-008 stays untouched per the reviewer's CR-035/CR-037 scope).

Build verified: 4-pass pdflatex+bibtex clean (pass 1 hit one Undefined
control sequence on `\citep{HLP1934}` — fixed to `\cite{HLP1934}`
since natbib is not loaded; and one Undefined reference on
`sec:appendix-deriv-a3` — fixed by adding the appendix stub; then
pass 1 → bibtex (HLP1934 added) → pass 2 → pass 3 settled, 0
undefined refs). `main.pdf` is 33 pages / 2,152,496 bytes, up from
27 pages / 1,814,626 bytes at rb-013 (+6 pages, +338 KB).

## How it connects to the ledger

Discharges the A3 row's `Manuscript §extensions-A3 (RB-034) is now
unblocked` annotation in CLAIM_LEDGER.md. The manuscript now states A3
at exactly the strength the live A3 verdict
(`Critique/verdicts/A3--multiplicative-conservation.md`,
`current_label: CONTESTED`) licenses:

- *Central tendency robust* — median $\CF$ moves by $\le 0.004$ across
  $p \in \{0, 1\}$ in both variants. This is the §5.5 claim of the
  inherited paper, restated as a *bounded* claim with a concrete band
  rather than as an open promise of robustness.
- *Tail not robust* — strict min $\CF$ falls $0.559 \to 0.464$
  (variant A) and $0.304 \to 0.231$ (variant B); $\mathrm{frac}(\CF <
  0.5)$ roughly doubles ($4.0\% \to 8.3\%$ combined); $191$ cells flip
  from $\CF \ge 0.5$ to $\CF < 0.5$ with $0$ reverse flips. This is
  the reviewer's verdict-text Block-C1 prediction, reproduced
  verbatim, now stated as a *finding* of the rebuilt paper rather than
  as an attack on the original.
- *No cell-wise increase in $\CF$ under multiplicative scaling* —
  $\Delta\CF \le 0$ in every valid cell. **Novel to the rebuild.**
  Stated as Theorem 3.2 (empirical); the formal proof in the
  rebuild's voice is deferred to RB-033.

Discharges the C2 row's `manuscript drafted` annotation along the
conservation-form-invariance axis: Proposition 3.1 promotes the
empirical FP-identity observation (rb-016 TEST 3) to a formal
proposition with a self-contained one-paragraph proof.

Discharges the C5 row's `conservation-form-invariance` annotation:
the corollary $\beta(1, p) = \gamma(1, p) = 1$ at every $p$ is stated
explicitly in §extensions-A3 with a forward reference to the C5
appendix (RB-013) that is still queued; the corollary's numerical
witness is the rb-015 `test_symmetric_corner_invariant` pin.

Discharges the C1 row's conservation-family annotation: Table
tab:a3-c1-cf-band reports the full $\CF$ distribution side-by-side
for $p \in \{0, 1\}$ across both variants, reproducing the reviewer
verdict-text numbers and stating the band as a finding of the
rebuilt paper.

No claim in §extensions-A3 exceeds its ledger-licensed strength. In
particular, the section explicitly *excludes* any statement about
$\corr \ne 0$ in the conservation-family direction — the joint $(p,
\corr)$ sweep is in the §scope deferral list.

## Simulation evidence

This is a manuscript increment; the supporting numerics are all from
the rb-016 sim (`Rebuild/sims/A3--conservation-band/`, sha256
`055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`),
which was already verified at rb-016. Every numerical claim, table
entry, and figure citation in §extensions-A3 points back to a key in
`Rebuild/sims/A3--conservation-band/output/results.json`:

| §extensions-A3 element                          | results.json source                                              |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| Table tab:a3-c2-peak-band (peak band)           | `block_A_peaks.p=*__v=*`                                         |
| Figure fig:a3-vda-curves-p-v5                   | `block_A_sweeps.*` + figures/vda_curves_pfamily_v5.png           |
| Proposition 3.1 numerical witness               | `recovery.test_3_r_dagger_p_invariance` (max $|\Delta| = 0$)     |
| Figure fig:a3-vda-peak-band                     | `block_A_peaks` + `block_A_r_dagger_by_p_v` + figures/vda_peak_band.png |
| Table tab:a3-c1-cf-band (CF distribution)       | `block_B_summaries.p=*.variant_*` / `.combined`                  |
| Theorem 3.2 (per-cell $\Delta\CF \le 0$)        | `block_B_delta_CF.{A,B,combined}.frac_dec` / `.frac_inc`         |
| Figure fig:a3-cf-hist-pfamily                   | figures/cf_histogram_pfamily.png                                 |
| Figure fig:a3-delta-cf-distribution             | figures/delta_cf_distribution.png                                |
| Recovery Test 1                                 | `recovery.test_1_p1_pins`                                        |
| Recovery Test 2                                 | `recovery.test_2_p0_vs_reviewer`                                 |
| Recovery Test 3                                 | `recovery.test_3_r_dagger_p_invariance`                          |
| Recovery Test 4                                 | (per-variant median band from rb-003 cross-check, recorded in rb-016 conversation page) |

## What the manuscript can now say

The §extensions-A3 section is licensed to state, in the rebuilt
manuscript:

> *"Promoting the inherited additive conservation rule $\benefit +
> \cost = 2$ to the power-mean family $M_p(\benefit, \cost) = 1$ with
> $\benefit/\cost = \Rsens$, we recover the inherited model at $p = 1$
> and the reviewer's A3 multiplicative alternative at $p = 0$. The
> closed-form escape threshold $\rdagger(\val) = K_u(\val)/[(\Nloc -
> 1)\,K_c(\val)]$ of Section~\ref{sec:results-c2} is conservation-
> form-invariant by construction (Proposition 3.1), and the symmetric-
> recovery result at $\Rsens = 1$ survives any choice of $p$
> (corollary). The peak height of $\VDA(\Rsens)$ at the headline cell
> moves with $p$ — a $+14\%$ envelope at $\val = 5$ in the band
> $p \in \{0, 1\}$ — and is reported as a sensitivity. The $4{,}410$-
> cell C1 sweep at $\corr = 0$ has a $p$-robust central tendency
> (median $\CF$ moves by $\le 0.004$) and a $p$-fragile tail
> ($\mathrm{frac}(\CF < 0.5)$ roughly doubles, $191$ cells flip from
> the criterion-dominant to the criterion-subordinate region with $0$
> reverse flips); per-cell, $\Delta\CF \le 0$ in every valid cell
> (Theorem 3.2). The conservation rule is therefore a model
> *assumption*, not a derived statement, and the headline numbers
> properly stand as bands across the family rather than as points at
> one fixed choice."*

It does *not* yet license:
- *(a)* the joint $(p, \corr)$ sweep — the conservation-band numbers
  here are at $\corr = 0$ only; deferred.
- *(b)* a formal derivation of the family in the rebuild's voice with
  the Hardy--Littlewood--Pólya power-mean monotonicity argument and a
  closed-form algebraic proof of Theorem 3.2 — deferred to RB-033, for
  which a §appendix-deriv-a3 stub is placed in this run.
- *(c)* harmonic ($p = -1$) or super-additive ($p > 1$) numerics — the
  rb-016 sim runs $p \in \{0, 0.5, 1\}$ only; the family is stated for
  general $p$ but the empirical band is reported on the sweep grid.

## Next increment

Backlog status after this run: 17 done, 15 open, 2 blocked.
Recommended next increment, in priority order:

1. **RB-013 — §appendix-C5 light-touch consistency result** (low
   effort; prereq RB-001 done). The §extensions-A3 C5 corollary
   forward-references `sec:appendix-c5`, which is still a stub.
   Filling RB-013 closes that forward reference, completes the four
   headline-claim results subsections plus the C5 appendix, and turns
   the C5 row of CLAIM_LEDGER from "stub in appendix" to "drafted in
   appendix". One pdflatex compilation cycle; no new sim needed
   (`Rebuild/model/tests/test_recovery.py` rb-001 already covers $r=1$
   symmetric recovery to FP identity at $\corr = 0$, and the
   conservation-form-invariance corollary lands the same statement
   across any $p$).

2. **RB-014 — A2 heterogeneous-$r$ model extension** (medium effort;
   prereq RB-001 done). Opens the A2/A8 heterogeneity thread, which
   naturally feeds a future §extensions-A2-A8 subsection in the same
   `extensions.tex` file this run created — the file is already
   structured to host one subsection per lever extension.

3. **RB-033 — A3 formal derivation in the rebuild's voice** (low
   priority; prereq RB-015 done). Consolidates the conservation-
   family algebra into a proper appendix derivation
   `Rebuild/derivations/A3--conservation-family.md`, mirroring the
   RB-030 / §appendix-derivation-C4 path. The §extensions-A3
   Proposition 3.1 proof sketch can graduate to a formal proof, and
   Theorem 3.2 (per-cell $\Delta\CF \le 0$) can get a closed-form
   algebraic statement. The §appendix-deriv-a3 stub written this run
   is the landing pad.

RB-013 is the cleanest single next increment: it closes the cleanest
loose end (the §extensions-A3 forward reference to the C5 appendix)
and discharges the four-headline-claim spine.

## Wiki cross-references

Wiki sweep performed before declaring §extensions-A3 done. Keywords
{power mean, generalised mean, Hardy--Littlewood--Pólya, conservation
constraint, asymmetric scaling, $\beta + \gamma = 2$, $\beta\gamma =
1$, additive vs multiplicative conservation}. Results:

- `pearl2018_book_of_why.md` and `graves2016_act.md` matched the
  literal string "inequal" in unrelated contexts (causal inequalities;
  inequality-constrained gating). Not relevant.
- No `research_db/papers/` stub for Hardy--Littlewood--Pólya 1934
  *Inequalities*, the power-mean monotonicity, or any of the
  conservation-rule literature in attention/SDT. Same math-methods
  gap flagged by rb-008 (Slepian 1962, Tong 1990) and rb-014 (the
  conservation literature). Out of rebuilder scope per the
  reviewer's CR-035/CR-037 backlog; the citation in §extensions-A3
  uses the full bibliographic reference of refs.bib `HLP1934`.

No new `research_db/papers/` stubs added; `audit.py` not re-run (no
wiki writes).

## Files I touched

| file                                                                                                                 | what changed                                                                                                                  |
| -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `Rebuild/manuscript/sections/extensions.tex`                                                                         | NEW — §extensions section header + §extensions-A3 subsection (~340 LaTeX lines, $\sim$$17.5$ KB)                              |
| `Rebuild/manuscript/main.tex`                                                                                        | +1 line — `\input{sections/extensions.tex}` between results and limitations                                                   |
| `Rebuild/manuscript/sections/appendix.tex`                                                                           | +1 subsection — `sec:appendix-deriv-a3` stub (clears the forward reference from §extensions-A3)                               |
| `Rebuild/manuscript/refs.bib`                                                                                        | +1 entry — `HLP1934` (Hardy--Littlewood--Pólya 1934 *Inequalities*; by full bib reference; research_db stub deferred)         |
| `Rebuild/manuscript/figures/{vda_curves_pfamily_v5,vda_peak_band,cf_histogram_pfamily,delta_cf_distribution}.png`    | 4 figures copied from `Rebuild/sims/A3--conservation-band/output/figures/`                                                    |
| `Rebuild/manuscript/main.pdf`                                                                                        | rebuilt — 33 pages / 2,152,496 bytes (was 27/1,814,626 at rb-013)                                                             |
| `Rebuild/CLAIM_LEDGER.md`                                                                                            | header reconcile line updated to rb-017; A3 row backing column extended with the full §extensions-A3 content listing          |
| `Rebuild/REBUILD_BACKLOG.md`                                                                                         | RB-034 status `queued` → `done` (was set to `in_progress` during the run); notes prepended with the rb-017 disposition; touched timestamp updated |
| `Rebuild/rebuilder_state.json`                                                                                       | atomic write — runs 16 → 17; `RB-034` added to `done_task_ids` and `manuscript_sections_drafted`; `rb_017_manuscript_pdf_bytes` added |
| `Rebuild/BUILD_LOG.md`                                                                                               | header pre-written before execution for crash recovery; body appended at end of run                                           |
| `Rebuild/conversations/2026-05-25-rebuilder-rb017-extensions-a3.md`                                                  | NEW — this file                                                                                                               |

## Ledger reconciliation (vs.\ mission §3, prompt v0.2)

| claim | mission §3                | live verdict             | drift?       |
| ----- | ------------------------- | ------------------------ | ------------ |
| C1    | CONTESTED                 | CONTESTED                | no           |
| C2    | CONFIRMED-UNDER-ATTACK    | CONFIRMED-UNDER-ATTACK   | no           |
| C3    | CONTESTED                 | CONTESTED                | no           |
| C4    | CONFIRMED-CONDITIONAL     | CONFIRMED-CONDITIONAL    | no           |
| C5    | CONFIRMED-UNDER-ATTACK    | CONFIRMED-UNDER-ATTACK   | no           |
| A1    | CONTESTED                 | CONTESTED                | no           |
| A2    | CONFIRMED-CONDITIONAL     | CONFIRMED-CONDITIONAL    | no           |
| A3    | CONTESTED                 | CONTESTED                | no           |
| A6    | OPEN/in-progress          | **WEAKLY-SUPPORTED**     | yes (mild, flagged at rb-001) |
| A8    | CONFIRMED-CONDITIONAL     | CONFIRMED-CONDITIONAL    | no           |

A6's drift is unchanged from rb-001 (mild, pre-CONTESTED, direction
unchanged). RB-016 and RB-020 remain `blocked` waiting on a decisive
A6 label. No other drift.

## Why the next run should care

rb-017 turned the rb-015/rb-016 A3 wiring (model extension +
empirical band) into a manuscript-citable section, completing the
model→sim→manuscript dependency chain for A3 at central-tendency
strength. The rebuilt paper now has:

- four headline-claim results subsections drafted (§results-c1, -c2,
  -c3, -c4) plus a §model section drafted plus a §extensions section
  with one subsection drafted; and
- one of the three "load-bearing assumption" extensions
  (A3 conservation family) lifted from a verdict-row license to a
  written, figure-backed section.

The next single-increment moves are clean and unblocked: RB-013 closes
the §appendix-C5 stub that §extensions-A3 forward-references; RB-014
opens the A2/A8 heterogeneity thread into the same `extensions.tex`
file; RB-033 promotes Proposition 3.1 / Theorem 3.2 from their
in-section proof sketches to a formal appendix derivation.
