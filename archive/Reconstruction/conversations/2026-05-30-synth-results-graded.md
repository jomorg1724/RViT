---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: 7B3F1A92-5D2C-4E18-A6F0-3C91B47E2DA5
started: 2026-05-30T23:30:00Z
ended: 2026-05-30T23:59:59Z
worked_on: SY-006
output_kind: section
section_touched: "sections/results.tex (§4.3, sec:results-graded)"
artifacts_consumed:
  - "Rebuild/CLAIM_LEDGER.md (C3 row, A1 row — silent ceiling)"
  - "Rebuild/manuscript/sections/results.tex §results-c3 (content, re-voiced)"
  - "Rebuild/sims/C3--iso-vda-Vv/output/figures/{iso_vda_contours,vda_at_high_V,iso_vda_drho}.png"
firewall_violations_fixed: 0
gaps_opened: []
gaps_closed: []
compiles: "true (17 pages)"
---

# Run SY-006 — Results §4.3, the graded regime

## What I wrote

A new Results subsection, **§4.3 "The benefit is concentrated in a
graded regime"** (`sec:results-graded`), the third of the paper's four
findings. Structure, all in clean positive Nature Neuroscience voice:

1. **Opening.** Frames the finding as the natural sequel to the §4.2
   non-monotonicity: sweeping the design plane $(\valid,\val)$ shows the
   benefit is materially large only in a concentrated, graded-boundary
   corner.
2. **Iso-VDA contour band** (Fig `iso-vda-contours`, $2\times3$ panel):
   3,534-cell sweep at $(4,2,0.5,\sqrt{})$ var A; corner at low $\valid$
   / high $\val$ flattening along $\Rsens$ ($0.17\to0.16\to0.06$).
3. **Distribution** (Table `graded-marginals`): median $\VDA\le0.007$
   every panel; peak $0.173\to0.062$; frac$\ge0.05$ $28.7\%\to1.2\%$.
4. **Quantitative design threshold** (Table `graded-highV` + three
   conditional bullets + boxed recommendation + Fig `vda-at-high-V`):
   $\valid\ge0.95$ floor; $\valid\ge0.80$ floor at $\corr{=}0$ with a
   $\corr$-conditional sub-percent signal at $\corr{=}0.2$;
   $\valid\ge0.60$ substantial (peak $0.16$). Recommendation stated as
   the model's own prediction.
5. **Decorrelation reshapes the band** (Fig `iso-vda-drho` + Table
   `graded-signflip`): sign of $\partial\VDA/\partial\corr$ varies over
   the plane — cost-dominant suppression-dominated, symmetric/benefit-%
   dominant amplification-dominated; dormant-cell $\approx96\times$
   amplification at $(0.7,10,0.3)$ flagged falsifiable → Discussion.
6. **Scope.** Single config, var A, coarse $\corr$ grid; variant-B and
   conservation bands → Discussion; finer $\valid$-grid would sharpen
   the thresholds. Value-blind $\val=1$ identity as a consistency check.

## Grounding

| assertion | evidence |
| --- | --- |
| concentrated graded regime; contour band | LEDGER:C3; SIM:C3--iso-vda-Vv |
| 3,534-cell grid, config, panels | SIM:C3 (sweep design) |
| median/peak/frac numbers | SIM:C3 (`summary.r=<r>__rho=<rho>`) |
| corner flattening along $\Rsens$ | SIM:C3; Fig iso_vda_contours |
| high-$\valid$ probe (all entries) | SIM:C3 (`high_V_probe...max_VDA`) |
| design recommendation thresholds | LEDGER:C3; CohenMaunsell2009 ($r_{SC}\approx0.2$) |
| sign-flip fractions / extrema | SIM:C3 (`rho_sensitivity.r=<r>`); LEDGER:A1 |
| dormant-cell $96\times$ amplification | SIM:C3; LEDGER:C3+A1 |
| $\val=1\Rightarrow\VDA\equiv0$ | model theorem (value-blind collapse) |

All eight assertions logged as TRACE G0–G7.

## Strength check

Nothing exceeds the evidence. LEDGER:C3 licenses a **graded /
quantitative** statement — a contour band, explicitly *not* a
categorical floor; I wrote it exactly there. The high-validity design
guidance is stated positively as the model's prediction (the permissive
$\valid\ge0.75$ point is given as a quantitative fact of the sweep, not
as a correction of an external claim). The $\corr$ sign-flip and the
dormant-cell amplification sit at the joint C3+A1 ceiling and are
reported as model properties / a falsifiable prediction, not over-sold.

## Firewall sweep

Section authored from scratch in positive voice; no meta introduced.
The upstream source for this content was saturated with firewall
vocabulary ("inherited paper", "§5.2", "claim restated at defensible
strength", reviewer labels, `rb-`/`RB-` ids, `Rebuild/`/`Critique/`
paths, sha256, "queued increments") — **none** of it carried over. The
absent categorical statement is never referenced; the finding stands on
its own footing. `grep` for banned vocabulary across all `.tex`
(including comments): **0 hits.**

## Gaps

None opened, none closed. All three figures already existed under the
sim output and were copied directly. G-001 (the attention→$d'$ Model
figure) remains the sole open gap, untouched this run.

## Compile

Clean 3-pass `pdflatex` + `bibtex`: **17 pages** (was 13), 0 undefined
references, 0 undefined citations, 0 overfull boxes.

## Next increment

**SY-007** — Results §4.4–§4.5: the conditional no-inversion theorem
($\valid\ge1/\Nloc$), closed-form $r^\dagger_{\mathrm{inv}}$,
symmetric-corner identity, and anti-cue inversion as a new falsifiable
prediction; place `r_inv_closed_form`, `er_vs_alpha_anticue`,
`alpha_star_V_r_map`. Completes the Results arc and unblocks SY-008
(Discussion) and SY-009 (second coherence pass).

## Drift watch

- §4.3 forward-refs to `sec:discussion` for the variant-B and
  conservation-family bands; the stub exists so the ref resolves, but
  SY-009 must verify the Discussion actually states them once SY-008
  lands.
- $\valid=0.95$/$0.80$ thresholds are bracketed by the $0.025$ grid step;
  stated as "$\gtrsim$" and flagged as scope — a finer sweep (not yet
  available) would let a later run sharpen them. No invention.
- The dormant-cell amplification is currently a single-cell empirical
  observation; if SY-008 elevates it to a headline prediction, confirm
  it stays at the C3+A1 ceiling and is not overstated.
