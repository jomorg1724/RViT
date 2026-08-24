---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-026-2026-05-30
started: 2026-05-30T07:56:00Z
ended: 2026-05-30T08:08:00Z
worked_on: RB-041
output_kind: manuscript
claims_touched: [A1]
artifacts_written:
  - Rebuild/manuscript/sections/model.tex (§sec:model-upper-bound continuation, +≈155 LaTeX lines)
  - Rebuild/manuscript/figures/a1cw_vda_delta_distribution.png (copied from rb-025 sim)
  - Rebuild/manuscript/figures/a1cw_signflip_by_r.png (copied)
  - Rebuild/manuscript/figures/a1cw_vda_sign_heatmap_v5.png (copied)
  - Rebuild/manuscript/main.pdf (regenerated, 45 pages / 2,587,742 bytes)
  - Rebuild/CLAIM_LEDGER.md (top reconcile paragraph + A1 row backing column tail)
  - Rebuild/REBUILD_BACKLOG.md (RB-041 status → done with notes)
  - Rebuild/rebuilder_state.json (runs_completed → 26; RB-041 added to done; manuscript_sections_drafted appended; rb_026_manuscript_pdf_bytes = 2,587,742)
  - Rebuild/BUILD_LOG.md (rb-026 entry)
  - Rebuild/conversations/2026-05-30-rebuilder-a1-cellwise-model-foldin.md (THIS file)
papers_added: []
spawned_tasks: []
---

## What I built

A four-block continuation of the §model §5.5-replacement subsection
(`sec:model-upper-bound`) in
[Rebuild/manuscript/sections/model.tex](Rebuild/manuscript/sections/model.tex),
inserted after the existing corrected §5.5 blockquote and replacing
the trailing "Statement~B... queued as RB-025 / RB-023 / RB-026"
paragraph that has been in the file since rb-009. The four blocks
fold the rb-025 cell-wise sign-flip distribution into manuscript
prose at the strength the A1 row of `CLAIM_LEDGER.md` already licensed:

1. **Cell-wise generalisation paragraph** — at $\rho = 0.2$, the
   central anchor of the $\rho \in [0, 0.4]$ empirical band of
   §model-rho-channel, the $4{,}410$-cell sweep of §results-c1
   licenses a cell-wise distributional statement. Per-cell
   $\Delta\VDA = \VDA(\rho{=}0.2) - \VDA(\rho{=}0)$ classified at
   $|\Delta\VDA| > 10^{-6}$ yields variant-A fractions
   $18.3\%$ amp / $28.2\%$ supp / $53.5\%$ inactive, variant-B
   $12.2\% / 27.5\% / 60.3\%$. The variant-A maximum cell-wise
   amplification ($+4.97 \times 10^{-2}$) is $5.3\times$ the
   rb-002 single-cell maximum at $(\valid, \val, \Rsens) =
   (0.5, 5, 0.4)$ ($+9.4 \times 10^{-3}$ at $\rho = 0.2$;
   Figure~\ref{fig:vda-rho-variantA}). The rb-002 observation was
   a typical-magnitude snapshot; the largest excursions sit
   elsewhere in $(\valid, \val, \Rsens)$.
2. **Table tab:a1cw-summary** — 11 rows × 2 variant columns:
   fraction counts ($n_{\mathrm{amp}}, n_{\mathrm{supp}},
   n_{\mathrm{inactive}}$), per-cell $\Delta\VDA$ quantiles
   (min / $q_{0.05}$ / $q_{0.50}$ / $q_{0.95}$ / max / mean),
   and the cell-wise crossover $\Rsens^{\times}$. Numbers sourced
   verbatim from
   `Rebuild/sims/A1--vda-signflip-cellwise/output/results.json`
   (sha256 `489c7c25…`); this is a pure citation, no algebra.
3. **Two-statement paragraph** —
   *(i) Cell-wise crossover.* Stratifying by $\Rsens$ on the
   21-point log$_{10}$-grid and tabulating
   $\mathrm{frac}_{\mathrm{amp}}(\Rsens)$ and
   $\mathrm{frac}_{\mathrm{supp}}(\Rsens)$ over $(\valid, \val)$,
   the cell-wise crossover sits at $\Rsens^{\times}(\mathrm{A})
   \approx 0.794$ in variant~A; variant~B never crosses. The
   variant-A nearest-cell sweep at $\valid = 0.5125$, $\val = 5$
   reproduces rb-002's small-$\Rsens$-suppression /
   large-$\Rsens$-amplification pattern with nearest-cell crossover
   $\Rsens \approx 0.398$ within the rb-003 $\valid$-grid
   perturbation of $+0.0125$ off rb-002's $\valid = 0.5$.
   *(ii) Spatial structure at $\val = 5$.* The mean $\Delta\VDA$
   surface over $(\valid, \Rsens)$ at $\val = 5$ is the cell-wise
   companion to Figure~\ref{fig:iso-vda-drho} of §results-c3:
   amplification concentrates at moderate-to-low $\valid$ and
   moderate-to-large $\Rsens$; suppression concentrates at high
   $\valid$ and small $\Rsens$. Variant~B is uniformly more
   suppression-favoring than variant~A.
4. **Three new figure floats**, copied from the rb-025 sim output
   to `Rebuild/manuscript/figures/` with `a1cw_` prefix and
   `\includegraphics`-d at $0.86\linewidth$:
   `fig:a1cw-delta-distribution`,
   `fig:a1cw-signflip-by-r`,
   `fig:a1cw-sign-heatmap-v5`.

Two outdated cross-references were also corrected in place:
the analytic sign-flip locus formerly "queued as RB-026" is now
cited as Section~\ref{sec:appendix-deriv-c2},
Proposition~\ref{prop:r-dagger-rho},
Equation~\ref{eq:r-dagger-rho} (folded in at rb-024 via RB-038);
the finer-$\rho$ grid extension remains queued as RB-023; the
analytic Slepian-gradient locus for the cell-wise
$\partial\VDA/\partial\rho$ surface is queued as RB-040.

No model edits, no derivation edits; pure prose + figure +
table increment.

## How it connects to the ledger

**Discharges:** the A1 row's `rb-025 cell-wise distribution can be
folded into §model §5.5-replacement (sec:model-upper-bound) in a
follow-up manuscript edit` license (the §5.5 retraction blockquote
has been in `model.tex` since rb-009; the cell-wise generalisation
was structurally available since rb-025; this run turns the rb-025
artifact into manuscript prose with stable Table~/~Figure labels).

The A1 row strength is unchanged. The row was already licensed at
"cell-wise distributional statement at $\rho = 0.2$" by the rb-025
sim; rb-026 turns that license into prose. After rb-026 the A1 row
is fully wired across:

- **sim**: rb-002 (single-cell pointwise) + rb-025 (cell-wise
  distribution across the C1 sweep)
- **derivation**: rb-008 (`Rebuild/derivations/A1--rho-channel.md`
  §1–§7, Slepian monotonicity on $\CF$ as Proposition 3.1, two-channel
  decomposition §4, Statements~A and B §4.3)
- **manuscript-model**: rb-009 (5 subsections; §model-upper-bound
  blockquote retracting §5.5) + rb-026 (cell-wise continuation)
- **manuscript-appendix**: cross-pinned via §appendix-deriv-c2
  (rb-024, RB-038, ρ-aware closed-form lower edge of the escape
  band — the second channel of the A1 two-channel decomposition).

The only remaining A1 threads are RB-023 (finer-$\rho$ grid,
low priority) and RB-040 (analytic Slepian-gradient locus for the
cell-wise $\partial\VDA/\partial\rho$ surface, low priority).

**Label drift:** none. 10/10 verdict labels still match the §3 table
of `agents/paper_rebuilder_prompt.md` v0.2; only the §3 A6 entry
remains stale (already flagged below in the ledger).

## Simulation evidence

No new sim run this turn — this is a pure manuscript-prose increment.
All numerical content folded into the four blocks above draws from
the rb-025 `Rebuild/sims/A1--vda-signflip-cellwise/output/results.json`
(pre-embed sha256 `489c7c2581d1e940cfc67427e0793959bb33b24afda075ee648743aa2ac659ea`),
which is itself a pure consumer of rb-003's
`Rebuild/sims/C1--cf-distribution/output/results.json`
(sha256 `91fc4692…`, validated against the reviewer's CR-002 at
`max|ΔCF| = 1.47e-6` across 4,410 cells). The three structural
recovery contracts of rb-025 (source-payload sha guarantee;
sign-flip at nearest cell V = 0.5125 reproducing rb-002's
V = 0.5 pattern; cell-wise crossover $0.794 \ge$ rb-002 headline
crossover $0.464$) are the upstream guarantee; nothing in this
run requires new numerical evidence.

The three new figures
(`a1cw_vda_delta_distribution.png`,
 `a1cw_signflip_by_r.png`,
 `a1cw_vda_sign_heatmap_v5.png`)
in `Rebuild/manuscript/figures/` are byte-identical copies of the
rb-025 figures in `Rebuild/sims/A1--vda-signflip-cellwise/output/figures/`.

### Build details

4-pass pdflatex clean. Pass 1: OK, no errors; "There were undefined
references" + "Label(s) may have changed" warnings (expected — the
new `tab:a1cw-summary`, `fig:a1cw-*` labels not yet in `.aux`); 45
pages, 2,587,682 bytes. bibtex: no new `\cite{}` commands, no-op.
Pass 2: 45 pages, 2,587,742 bytes (cross-refs resolved). Pass 3:
45 pages, 2,587,742 bytes (0 undefined refs, 0 errors). Pass 4:
byte-identical to pass 3 — settled. Final PDF: **45 pages /
2,587,742 bytes** (was 43 / 2,413,318 at rb-024 = +2 pages,
+174,424 bytes).

## What the manuscript can now say

At the A1-row strength ceiling, with the new §sec:model-upper-bound
continuation backing it:

> At $\rho = 0.2$, the central anchor of the
> $\rho \in [0, 0.4]$ empirical band, the rebuilt expected-reward
> expression delivers cell-wise amplification
> ($\Delta\VDA > +10^{-6}$) in $18.3\%$ of variant-A cells of the
> primary $4{,}410$-cell sweep and cell-wise suppression in
> $28.2\%$; variant~B is uniformly more suppression-favoring
> ($12.2\%$ amp / $27.5\%$ supp). The maximum cell-wise
> amplification (variant~A, $+4.97 \times 10^{-2}$) is $5.3\times$
> the rb-002 single-cell maximum at $(\valid, \val, \Rsens) =
> (0.5, 5, 0.4)$ ($+9.4 \times 10^{-3}$). The cell-wise crossover
> $\Rsens^{\times}(\mathrm{A}) \approx 0.794$ — the smallest
> $\Rsens$ at which amplification overtakes suppression across
> $(\valid, \val)$ — sits to the right of the rb-002 single-cell
> crossover ($\Rsens \approx 0.464$) because higher-$\valid$
> cells dominate the sweep and pull the cell-wise crossover right;
> variant~B never crosses. The inherited paper's §5.5
> "upper bound on VDA" framing therefore fails cell-wise as well
> as pointwise; the cell-wise companion to the C3 thread's iso-
> $\Delta\VDA$ heatmap (Figure~\ref{fig:iso-vda-drho}) at fixed
> $\val = 5$ shows amplification concentrating at moderate-to-low
> $\valid$ and moderate-to-large $\Rsens$, the opposite cell
> region from suppression.

It does **not** yet license:

- (a) a closed-form prediction of which $(\valid, \val, \Rsens)$
  cell maximises amplification — the cell-wise maximum is empirical;
  the analytic locus is queued as RB-040 (Slepian-gradient analogue);
- (b) a cell-wise sign-flip statement at $\rho$ values other than
  $0.2$ — the rb-025 distribution is reported at $\rho = 0.2$ only;
  the finer-grid extension is queued as RB-023;
- (c) a *quantitative* generalisation across higher correlations
  ($\rho > 0.4$) — outside the empirical envelope of CohenMaunsell2009.

## Next increment

The natural next increment is **RB-021** (A8 N-dim uncued sweep,
prereq RB-017 done at rb-020) — the only sibling §extensions
subsection (`extensions.tex` already hosts §extensions-A3 from
rb-017 and §extensions-A2 from rb-022; §extensions-A8 is the
remaining structural slot). The A8 row of `CLAIM_LEDGER.md` is
already wired through model (`er_full_policy` at rb-020) but its
sim → manuscript thread is empty. Landing RB-021 completes the
heterogeneity thread architecturally before the manuscript work
shifts to the abstract / intro / limitations bookends.

Alternative parallel options, all unblocked:

- **RB-033** (A3 formal derivation in the rebuild's voice, prereq
  RB-015 done at rb-015) — fills the `§appendix-deriv-a3` stub
  placed by rb-017; parallel to the RB-030 / §appendix-deriv-c4
  path landed by rb-014;
- **RB-024** (C1 closed-form CF $< 0.5$ boundary derivation,
  prereq RB-005 done at rb-003) — would let §results-c1 replace
  `frac < 0.6 = 22%` with a closed-form predicate;
- **RB-040** (Slepian-gradient analogue for the cell-wise
  $\partial\VDA/\partial\rho$ locus, prereq RB-026 / now done
  alongside RB-038's derivation) — the formal companion to this
  run's empirical cell-wise statement.

RB-021 is preferred — it lands the last extension subsection and
matches the "finish what's already wired" rhythm of rb-024 / rb-026
before the bookends begin.

## Wiki cross-references

Wiki sweep performed for keywords {cell-wise sign-flip,
$\partial\VDA/\partial\rho$, amplification incidence,
cost-dominant vs benefit-dominant regime,
criterion devaluation, concentration-cost relaxation,
A1 two-channel decomposition, Slepian-gradient}. All cited
literature (CohenMaunsell2009, RuffCohen2016, Srinath2021) already
wired from rb-008/rb-009 via §model cross-references; Slepian 1962
and Tong 1990 still cited by full bibliographic reference (math-
methods scope inherited from rb-008/rb-014/rb-017/rb-018 per
reviewer CR-035/CR-037 — out of rebuilder scope). No new
`research_db/papers/` stubs added; `audit.py` not re-run (no wiki
writes).
