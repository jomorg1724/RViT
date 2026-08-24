---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-011-2026-05-25
started: 2026-05-25T16:35:00Z
ended: 2026-05-25T17:05:00Z
worked_on: RB-011
output_kind: manuscript
claims_touched: [C3, A1]
artifacts_written:
  - Rebuild/manuscript/sections/results.tex (§results-c3 section, full draft replacing 9-line stub)
  - Rebuild/manuscript/figures/iso_vda_contours.png (copied from rb-010 sim output)
  - Rebuild/manuscript/figures/vda_at_high_V.png   (copied from rb-010 sim output)
  - Rebuild/manuscript/figures/iso_vda_drho.png    (copied from rb-010 sim output)
  - Rebuild/manuscript/main.pdf (recompiled, 21 pages / 1,570,450 bytes)
  - Rebuild/CLAIM_LEDGER.md (C3 row backing column extended; reconcile-line updated)
  - Rebuild/REBUILD_BACKLOG.md (RB-011 in_progress → done with full notes)
  - Rebuild/rebuilder_state.json (runs_completed 10→11, manuscript_sections_drafted, done_task_ids/open_task_ids, rb_011_manuscript_pdf_bytes)
  - Rebuild/BUILD_LOG.md (rb-011 entry, header pre-execution + body post-execution)
papers_added: []
spawned_tasks: []
---

# rb-011 — manuscript §results-c3 (graded regime boundary) + §5.2 redraft

## What I built

`Rebuild/manuscript/sections/results.tex` §results-c3 section: a
seven-paragraph full draft (~280 LaTeX lines) replacing the 9-line
stub left by rb-005. The section is the manuscript translation of
the rb-010 iso-VDA simulation; every number it cites is sourced
directly from `Rebuild/sims/C3--iso-vda-Vv/output/results.json`
(sha256 `72820559…`) with the block-keys recorded in each table
caption.

The seven paragraphs:

1. **Claim restated at defensible strength** — names the live C3
   verdict (`CONTESTED`), preserves the qualitative ``narrow regime''
   reading, retracts the inherited §5.2 categorical
   ``regardless of other parameters'' wording, and announces the
   graded / quantitative replacement.
2. **Iso-VDA contour band over $(V, v)$** — describes the
   $31 \times 19 \times 3 \times 2 = 3{,}534$-cell sweep design
   and inserts `Figure fig:iso-vda-contours`
   (`iso_vda_contours.png`, 2×3 panel grid; rows $\rho$, columns $r$).
3. **Distributional summary across panels** — `Table tab:c3-marginals`,
   per-panel $\VDA_{\min}/$ median $/q_{95\%}/\VDA_{\max}/
   \mathrm{frac}\!\ge\!0.005 / \mathrm{frac}\!\ge\!0.05$, sourced
   from `summary.r=<r>__rho=<rho>`.
4. **§5.2 replacement** — `Table tab:c3-highV-probe` (4×3 high-$V$
   probe), three threshold itemize statements, a boxed blockquote
   replacement sentence, and `Figure fig:vda-at-high-V`
   (`vda_at_high_V.png`, $V$-strata curves per $r$).
5. **A1 sign-flip across $(V, v)$** — `Figure fig:iso-vda-drho`
   (`iso_vda_drho.png`, signed $\Delta\VDA$ contour) and
   `Table tab:c3-sign-flip` (3-row per-$r$ frac amp / frac supp /
   mean $\Delta$ / max amp $(V, v)$ / max sup $(V, v)$, sourced
   from `rho_sensitivity.r=<r>`). The dormant-cell amplification at
   $(V, v, r) = (0.7, 10, 0.3)$, $\VDA = 0.0007 \to 0.0676$ at
   $\rho = 0.2$ (96×), is flagged as the candidate falsifiable A1
   prediction.
6. **Scope** — variant-B band → RB-027; threshold sharpening →
   RB-028; dormant-cell closeup → RB-029; broader-sweep cell-wise
   sign-flip → RB-025 (all cross-referenced).
7. **Reproducibility** — sha256 `72820559…`; recovery against
   rb-006 anchor $|\Delta\VDA| = 1.27 \times 10^{-7}$ (residual
   = rb-006's 6-dp rounding; model residual = 0); value-blind
   sanity $v=1 \Rightarrow VDA = 0$ identically across every cell.

Three figures copied from `Rebuild/sims/C3--iso-vda-Vv/output/figures/`
into `Rebuild/manuscript/figures/`.

Build chain: 1× pdflatex (3 undefined refs on pass 1) + bibtex +
2× pdflatex (0 undefined on pass 3). PDF: 21 pages / 1,570,450 bytes
(was 16 / 1,177,200 at rb-009 → +5 pages, +393 KB).

## How it connects to the ledger

- **C3 — narrow VDA regime** — live `current_label: CONTESTED`. This
  run discharges the *manuscript-prose* slot in the C3 backing
  column; the previous backing entry ended with ``Manuscript prose
  queued (RB-011)''. The C3 *rebuilt strength* in `CLAIM_LEDGER.md`
  is unchanged: every per-sentence claim in the §results-c3 section
  is at-or-below the strength rb-010 established. The boxed §5.2
  blockquote replacement explicitly preserves the inherited paper's
  intent ($V$-high paradigms can target a negligible-VDA regime) but
  attaches the quantitative threshold ($V \gtrsim 0.95$
  unconditionally; $V \gtrsim 0.8$ if $r_{SC} \le 0.2$) and the
  retraction of the ``regardless of other parameters'' wording
  (failed empirically at $V \in [0.6, 0.8)$ in the cost-dominant
  $r$-stratum, where peak VDA reaches 0.16 in the rb-010 sweep).
- **A1 — per-location SDT independence** — live `current_label:
  CONTESTED`. This run extends the A1 backing column with a
  *passing* §results-c3 reference: the cross-axis sign-flip
  generalisation across $(V, v)$ (cost-dominant $r=0.3$
  suppression-dominated; symmetric and benefit-dominant
  $r \in \{1, 3\}$ amplification-dominated) was already wired in
  the A1 row's rebuilt-strength column at rb-010; the §results-c3
  paragraph is the main-text expression of it. A1 rebuilt-strength
  unchanged.

No other rows touched.

**Drift check.** All 10 live verdict labels re-glob'd at start of
run; all match the §3 table of `agents/paper_rebuilder_prompt.md`
v0.2 (only A6 remains stale at WEAKLY-SUPPORTED vs §3's
OPEN/in-progress — direction unchanged, already flagged in
`CLAIM_LEDGER.md` ``Drift from §3'' block; not load-bearing for
this increment).

## Simulation evidence

This is a manuscript-only increment; no new simulation was run.
The rb-010 outputs are consumed verbatim. The numerical contract
inherited and re-cited:

- **Sim digest** (rb-010 `results.json`): sha256
  `72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`.
- **Recovery test** (rb-010 vs rb-006 anchor at $(V, v, r, \rho) =
  (0.5, 5, 1.0, 0)$): expected $\VDA = 0.039825$, observed
  $\VDA = 0.0398251274\ldots$, $|\Delta| = 1.27 \times 10^{-7}$
  vs tolerance $10^{-4}$ → **PASS**. The residual is the rb-006
  reference's 6-dp rounding; the rebuilt `policies()` call is
  bit-exact deterministic so the model residual is zero.
- **Value-blind sanity**: the $v = 1$ column is identically zero
  across every $(V, r, \rho)$ cell (value-blind baseline ⇒
  $\VDA = 0$ by construction). Cited in the §results-c3
  reproducibility paragraph.

The §results-c3 reproducibility paragraph re-states all three
contracts verbatim.

## What the manuscript can now say

The exact rebuilt-strength ceiling on C3 (now wired in both
backing artifacts and main-text prose):

> Across $(V, v) \in [0.25, 1.0] \times [1, 10]$ for $r \in
> \{0.3, 1, 3\}$ and $\rho \in \{0, 0.2\}$ (variant A, headline
> cell), VDA concentrates at low $V$, high $v$, moderate-low $r$:
> peak VDA $= 0.17$ at $r = 0.3$ falls to $0.06$ at $r = 3$. The
> inherited §5.2 categorical claim `negligible VDA at high $V$
> regardless of other parameters' is supported conditionally: at
> $V \ge 0.95$ peak VDA $\le 10^{-5}$ for every $(r, \rho)$ in the
> envelope; at $V \ge 0.80$ $\le 0.003$ with a small
> $\rho$-conditional caveat; at $V \ge 0.60$ it fails (peak $0.16$).
> The rebuilt §5.2 recommendation is therefore: target $V \gtrsim
> 0.95$ unconditionally, or $V \gtrsim 0.8$ if $r_{SC} \le 0.2$;
> the inherited $0.75$ threshold is too permissive.

The §results-A1 voice picks up a passing corroboration in
§results-c3: the rb-002 / rb-004 sign-flip generalises to the
$(V, v)$ plane (cell-wise pattern is $r$-dependent: $r = 0.3$
suppression-dominated, $r \ge 1$ amplification-dominated).
Strongest single amplification at $(V, v, r) = (0.7, 10, 0.3)$
lifts $\VDA = 0.0007 \to 0.0676$ at $\rho = 0.2$ — the candidate
falsifiable A1 prediction the rebuild may state in
§limitations / §design recommendations.

## Next increment

Three queued tasks have all prereqs satisfied (`RB-001` is the
common model prereq, done):

1. **RB-008** — C4 anti-cue inversion simulation. *Preferred.* The
   third headline-claim sim and the rebuild's only entirely new
   falsifiable prediction beyond the inherited paper's results
   (anti-cue inversion of $\alpha^\star$ below $V = 1/N$). The
   model machinery is already in place (the rebuilt `policies()`
   brackets $\alpha^\star$ to $[1/N, 1]$ by construction; rb-010
   verified ``no inversion above $V = 1/N$'' in passing across
   3,534 cells). The §results-c3 prose has established the
   methodological template ($(V, v)$ cell sweep, conditional
   threshold reporting, sign-flip generalisation) that RB-008 will
   reuse directly. Reuses `Critique/derivations/C4--no-inversion.md`
   for the closed-form $r^\star_{\mathrm{inv}}(V, v, N, \mathrm{CR})
   = (N-1) A_0 / B_0$ threshold.
2. **RB-014** — A2 heterogeneous-$r$ model extension. Opens the
   A2/A8 heterogeneity thread; useful but a model-tier task
   (heavier than a sim) so produces a smaller user-visible PDF
   increment per run.
3. **RB-013** — §appendix-C5 light-touch consistency result. No
   new sim needed (the $\rho \to 0$ recovery test in `model/tests`
   already covers $r = 1$ symmetric recovery); a short appendix
   subsection that wires C5 into the manuscript at its
   defensible strength (``machine precision'' universal,
   ``literal 0.0'' configuration-specific). Low effort, low
   marginal headline-claim coverage gain.

Recommend **RB-008** as the next run's primary target. RB-013 is
a good parallel candidate if RB-008 hits an unexpected blocker.

## Wiki cross-references

Mechanism-keyword sweep against `research_db/` (mission §11) ---
keywords: `iso-VDA`, `narrow regime`, `validity threshold`,
`experimental design`, `signal detection theory`,
`cross-location correlation`, `equicorrelated Gaussian`.

- `papers/cohen_maunsell2009_correlations.md` — wired; cited in
  §results-c3 paragraph 4 (§5.2 replacement) as the $r_{SC} \approx
  0.2$ V4 anchor for the $\rho$-conditional threshold ($V \gtrsim
  0.8$ if $r_{SC} \le 0.2$). Bibtex entry already in
  `refs.bib` from rb-009; no addition needed.
- `papers/ruff_cohen2016_cross_area_correlations.md` — wired by
  §model section (rb-009); not load-bearing here (the §results-c3
  paragraph treats $\rho$ as a single equicorrelation magnitude,
  not as structured covariance).
- `papers/srinath2021_attention_information_flow.md` — wired by
  §model section (rb-009); not load-bearing here.
- `papers/muller_findlay1987_sensitivity_criterion.md` — wired by
  §results-c1; not cited again in §results-c3 (the criterion-vs-attention
  vocabulary is already established).
- No new external citation introduced by this manuscript increment;
  the contour band, the §5.2 threshold table, and the sign-flip
  generalisation are theorems of the rebuilt model's own definitions.
- `audit.py` not re-run (no wiki writes this run).
