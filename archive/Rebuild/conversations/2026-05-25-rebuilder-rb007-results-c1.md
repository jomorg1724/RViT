---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-007-2026-05-25
started: 2026-05-25T13:55:00Z
ended: 2026-05-25T14:30:00Z
worked_on: RB-009
output_kind: manuscript
claims_touched: [C1, A1]
artifacts_written:
  - Rebuild/manuscript/sections/results.tex (§results-c1 prose, replacing rb-005 placeholder)
  - Rebuild/manuscript/figures/cf_histogram.png (copied from sims/C1--cf-distribution/output/figures/)
  - Rebuild/manuscript/figures/cf_heatmap.png   (copied from sims/C1--cf-distribution/output/figures/)
  - Rebuild/manuscript/figures/cf_curves.png    (copied from sims/C1--cf-distribution/output/figures/)
  - Rebuild/manuscript/refs.bib (added MullerFindlay1987)
  - Rebuild/manuscript/main.pdf (12 pages, 897 327 bytes; rebuilt via pdflatex × 4 incl. bibtex)
  - Rebuild/CLAIM_LEDGER.md (C1 row backing updated; reconcile-line bumped to rb-007)
  - Rebuild/REBUILD_BACKLOG.md (RB-009 marked done with notes block)
  - Rebuild/rebuilder_state.json (runs_completed 6→7, RB-009 added to manuscript_sections_drafted and done_task_ids, rb_007_manuscript_pdf_bytes recorded)
  - Rebuild/BUILD_LOG.md (rb-007 entry appended)
  - Rebuild/conversations/2026-05-25-rebuilder-rb007-results-c1.md (this file)
papers_added: []
spawned_tasks: []
---

# rb-007 — §results-C1 manuscript prose

## What I built

The §results-C1 subsection of the rebuilt manuscript, replacing the
placeholder bracket rb-005 left in `Rebuild/manuscript/sections/results.tex`.
The increment parallels rb-006 (§results-C2) in structure: a claim-
restatement paragraph pinned to the live verdict label, a numbered
definition equation, four tables, three figures, an A1 sensitivity
paragraph that operationalises the three-levers convention, and
scope-and-reproducibility paragraphs.

Numbers and figures all trace to the rb-003 simulation
`Rebuild/sims/C1--cf-distribution/` (output digest `91fc4692…`); no
new simulation was run.

Build verification: 3-pass `pdflatex` + 1 `bibtex` pass (the new
`MullerFindlay1987` citation required it). Final PDF: 12 pages /
897 327 bytes (was 7 / 542 463 at rb-006). No undefined references
after the final pass.

## How it connects to the ledger

This increment discharges the manuscript half of the C1 row in the
verdict ledger. The live label is `CONTESTED`
(`Critique/verdicts/C1--criterion-fraction-floor.md`); the §results-C1
prose now states C1 at exactly the defensible strength the §3.1 of
the mission file licenses: a distributional/central-tendency result
with explicit corner regions. The original paper's categorical floor
`CF ∈ [0.60, 0.96]` is retracted in `\section{Results}` (introductory
paragraph) and in `tab:cf-distribution`. The substantive "criterion
typically dominates" reading survives via the medians (variant A
$0.7552$, variant B $0.7682$), and the corner where attention
re-allocation overtakes the criterion lever is quantified in
`tab:cf-quadrants` (benefit-dominant low-validity quadrant: variant
B median $0.51$, $78\%$ of cells below $0.6$, strict min $0.30$).

The A1 row's `\rho`-sensitivity discharge for this section adheres
to the three-levers convention established in rb-006 (and in
`\section{Results}`): instead of a dedicated A1 subsection, the
$\rho \in \{0, 0.2\}$ comparison appears alongside the C1 marginals
(`tab:cf-rho-sensitivity`) and as a cell-wise Δ-distribution
(`tab:cf-delta-distribution`). The variant-A 84%-one-sided / variant-B
64%-mixed asymmetry is reported honestly as a *directional
sensitivity*, not as a uniform claim — preserving the rb-002 / rb-003
caveat that variant-B CF is essentially flat in $\rho$ at the
headline cell and mixed-sign across the sweep.

The §5.5 inherited-paper claim that "independence upper-bounds VDA"
is retracted along the CF axis here, with explicit variant-
dependent qualification: independence upper-bounds *the criterion
fraction* on a strong majority of variant-A cells (one-sided), but
does not upper-bound it at all on variant-B cells.

No label drift this run; the live ledger files match the §3 table.

## Simulation evidence

- `Rebuild/sims/C1--cf-distribution/output/results.json`, digest
  `91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`
  (rb-003 / RB-005).
- Recovery against the reviewer's
  `Critique/replications/C1--criterion-fraction-floor/`: cell-wise
  `max|ΔCF| = 1.47e-6`, `max|ΔR(P1..P4)| ≤ 5.65e-7` across all 4,410
  cells; ULP-scale `1 - Phi(-b)` vs `Phi(b)` reordering in the
  reviewer's `floor_R`. The agreement is well past the four-decimal
  precision of any reported headline number.
- Figures (`cf_histogram.png`, `cf_heatmap.png`, `cf_curves.png`)
  copied from `Rebuild/sims/C1--cf-distribution/output/figures/` to
  `Rebuild/manuscript/figures/`; included as `fig:cf-histogram`,
  `fig:cf-heatmap`, `fig:cf-curves`.

## What the manuscript can now say

> *"Across the paper's primary 4{,}410-cell $(\Rsens, \valid, \val)$
> sweep at $(\Nloc, \dprimemax, f_0, h) = (4, 2, 0.5, \sqrt{})$, the
> criterion fraction $\CF$ is distributed over $[0.5587, 1.0000]$ in
> variant~A and $[0.3040, 1.0000]$ in variant~B with median $0.7552$
> (A) / $0.7682$ (B). The inherited paper's stated range
> $\CF \in [0.60, 0.96]$ is retracted on both ends; the substantive
> 'criterion typically dominates' reading is sustained at the median.
> The criterion lever cedes to attention re-allocation in the
> benefit-dominant low-validity corner: variant~B median $0.51$ with
> $78\%$ of cells below $0.6$ and strict minimum $0.30$ in that
> quadrant. Promoting the A1 independence assumption to $\rho = 0.2$
> triples variant-A $\mathrm{frac}<0.6$ ($0.07 \to 0.22$), drops the
> variant-A strict minimum below $0.50$, and orders $\CF(0.2) \le
> \CF(0)$ in $84\%$ of variant-A cells. The same ordering is mixed in
> variant~B ($64\%$ / $24\%$ / $13\%$ dec.\ / inc.\ / flat):
> independence upper-bounds $\CF$ on a typical variant-A cell but not
> uniformly, and does not upper-bound $\CF$ at all in variant~B."*

The section does *not* yet claim: (i) a conservation-family band on
any of the headline numbers (deferred to RB-019 / §limitations);
(ii) a closed-form regime boundary for the CF<0.5 corner (deferred
to RB-024); (iii) a cell-wise VDA Δ-distribution (deferred to
RB-025); (iv) any quantitative statement at finer $\rho$ resolution
(deferred to RB-023).

## Next increment

**RB-003 — A1 derivation in clean LaTeX.** This is the increment
that unblocks RB-004 (§model section), which is currently a stub
that both §results-C1 and §results-C2 forward-reference via
`\ref{sec:model}`. The derivation promotes the equicorrelated
one-factor Gauss–Hermite quadrature `P_no-fa(ρ)` and the Slepian-
monotonicity argument from `Critique/derivations/A1--correlated-fa-
upper-bound.md` into `Rebuild/derivations/A1--rho-channel.md`,
re-derived in the rebuild's voice rather than copied. Per mission
§4.1 the model→sim→derivation→manuscript dependency order makes
this the highest-leverage available unblock for the manuscript
spine.

Backup picks if RB-003 turns out to need more compute budget than
~15 min: **RB-008 (C4 inversion sim)** — opens an entirely new
claim pipeline, parallels the rb-004 cadence, and would unblock
RB-012 (C4 §results subsection).

## Wiki cross-references

- `research_db/papers/muller_findlay1987_sensitivity_criterion.md` —
  the foundational SDT decomposition of spatial cuing into
  sensitivity vs. criterion components; the conceptual ancestor of
  the criterion-fraction quantity. Cited in the §results-C1 claim-
  restatement paragraph (`\cite{MullerFindlay1987}`); bib entry
  added to `refs.bib` with DOI `10.3758/bf03203097`.
- `research_db/papers/hawkins1990_attention_detectability.md`,
  `research_db/papers/luo_maunsell2018_criterion_sensitivity.md`,
  `research_db/papers/sridharan2017_sc_sensitivity_bias.md` —
  immediate descendants in the same lineage; consulted via the
  related-papers block of `muller_findlay1987`. Not cited this
  increment; candidates for the §intro literature anchor when
  that section is filled (currently a stub).
- No new `research_db/papers/` stubs were added; `audit.py` not
  run.
