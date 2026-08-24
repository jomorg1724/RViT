---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-009-2026-05-25
started: 2026-05-25T15:25:00Z
ended: 2026-05-25T15:45:00Z
worked_on: RB-004
output_kind: manuscript
claims_touched: [A1]
artifacts_written:
  - Rebuild/manuscript/sections/model.tex
  - Rebuild/manuscript/figures/vda_curves_variantA.png
  - Rebuild/manuscript/figures/vda_curves_variantB.png
  - Rebuild/manuscript/figures/cf_vs_rho.png
  - Rebuild/manuscript/refs.bib (appended: RuffCohen2016, Srinath2021)
  - Rebuild/manuscript/main.pdf (rebuilt; 16 pages / 1177200 bytes)
  - Rebuild/CLAIM_LEDGER.md (A1 row: backing column extended with §model)
  - Rebuild/REBUILD_BACKLOG.md (RB-004 done with full notes)
  - Rebuild/rebuilder_state.json (atomic; runs_completed 8 → 9, RB-004 moved to done_task_ids)
  - Rebuild/BUILD_LOG.md (rb-009 entry prepended)
  - Rebuild/conversations/2026-05-25-rebuilder-rb009-model-section.md (this file)
papers_added: []
spawned_tasks: []
---

# What I built

`Rebuild/manuscript/sections/model.tex` — the §model section of the
rebuilt VDA manuscript, 5 subsections + 3 included figures, ~280
LaTeX lines, replacing the rb-005 skeleton stub. This is the
constructive payoff of the rb-002 (sim) → rb-008 (derivation) →
rb-009 (manuscript) chain on the A1 axis: the "three levers, not
two" reframe and the variant- and cell-conditional CF upper-bound
(as opposed to the inherited paper's §5.5 categorical VDA upper-
bound) are now load-bearing main-text content rather than artifacts
that only live in the derivation file and the sim README.

Subsection structure:

- **§2.1 `sec:model-inherited`** — compact SDT skeleton. Equations
  `sdt-marginal`, `expected-reward`, `vda-def`, `cf-def-model`.
  Notation aligned with `main.tex`'s `\\newcommand` macros.
- **§2.2 `sec:model-booking`** — locus of A1, equation
  `pnofa-indep`. A1 enters the reward expression in exactly one
  place; that place is the cross-location no-FA product. A remark
  separates A1 from a pooled-statistic A6 relaxation that the
  inherited paper sometimes conflates with correlated noise.
- **§2.3 `sec:model-rho-channel`** — the decorrelation channel.
  Equicorrelated covariance, one-factor representation, boxed
  Eq. `pnofa-rho` for the exact 1-D orthant integral, recovery
  contract Eq. `rho-zero-recovery` tied to sha256 `d3c62215…` (7/7
  PASS) at floating-point identity, n_q=64 Gauss--Hermite
  quadrature with $\le 10^{-15}$ error against n_q=128, empirical
  envelope $\rho \in [0, 0.4]$ anchored to Cohen & Maunsell 2009
  $r_\mathrm{SC} \approx 0.2$, structured-covariance scoped
  limitation citing Ruff & Cohen 2016 and Srinath et al. 2021.
- **§2.4 `sec:model-three-levers`** — Definition `def:three-levers`
  enumerating criterion shift / sensitivity re-allocation /
  decorrelation, each with its reward decomposition. Frames
  decorrelation as the lever the inherited paper held implicitly
  fixed at the boundary.
- **§2.5 `sec:model-upper-bound`** — what independence actually
  upper-bounds. Explicit retraction of the inherited §5.5 sentence
  with pointwise VDA-excess numerics ($+4.84\times10^{-3}$ →
  $+1.01\times10^{-2}$ across $\rho = 0.1 \to 0.4$), sign-flip locus
  $r \in [0.38, 0.56]$ (A) / $r \approx 0.26$ (B), CF(ρ) monotone-
  down at the headline cell (variant A) and 84% / 64% one-sided
  cell-wise across the rb-003 4,410-cell sweep, three included
  figures (variant-A VDA family, variant-B VDA family, variant-A
  CF(ρ) family), and a closing blockquote stating the corrected
  version of the §5.5 sentence.

Three rb-002 figures copied from
`Rebuild/sims/A1--rho-channel/output/figures/` into
`Rebuild/manuscript/figures/`. Two new bib entries (`RuffCohen2016`,
`Srinath2021`) appended to `refs.bib`, sourced from the existing
research_db stubs. Build is clean over four pdflatex passes plus
one bibtex pass (settled with zero undefined references).

# How it connects to the ledger

A1 row of `CLAIM_LEDGER.md`:

- **Reviewer label.** Unchanged: CONTESTED (live verdict
  `Critique/verdicts/A1--independence.md` reads `current_label:
  CONTESTED`; 10/10 verdict labels reconcile with the §3 table of
  `agents/paper_rebuilder_prompt.md` v0.2 with no drift).
- **Rebuilt strength.** Unchanged. This run is a translation
  increment: it carries the rb-002 sim numbers and the rb-008
  derivation Statements A and B into main-text voice at no higher
  strength than the ledger already licenses. The blockquote in
  §2.5 reads as "variant- and cell-conditional ceiling on CF",
  with the explicit 84% / 64% qualifiers carrying forward the
  rb-003 cell-wise generalisation; the VDA pointwise excess is
  named as a reported finding on the empirical envelope, with the
  sign-flip locus bracketed and the variant-B sign-flip locus
  reported separately.
- **Backing.** Extended. Before rb-009: model code, recovery test,
  rb-002 sim, rb-008 derivation. After rb-009: + the §model
  manuscript section. The CLAIM_LEDGER A1 row now carries a long
  italicised summary of which equations and figures the §model
  section uses to deliver each claim.

This is the manuscript-side discharge of the "single biggest
upgrade" the mission prompt §3.2 names: promoting A1 to a first-
class model parameter and recasting the decomposition as three
levers, not two. After rb-009 the §model section reads in the
distributional/conditional voice §3.3 of the mission prompt mandates
as the corrective to the inherited paper's over-statement habit.

# Simulation evidence

No new simulation in this run. The §model section cites the
existing sims at their already-published sha256 digests:

- `Rebuild/sims/A1--rho-channel/` (rb-002, sha256
  `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`)
  — headline-cell VDA(r, ρ) and CF(ρ) surfaces; the source of three
  figures included in §2.5 (vda_curves_variantA.png,
  vda_curves_variantB.png, cf_vs_rho.png).
- `Rebuild/sims/C1--cf-distribution/` (rb-003, sha256
  `91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`)
  — the 4,410-cell sweep at $\rho \in \{0, 0.2\}$; the source of
  the 84% / 64% cell-wise CF upper-bound generalisation in §2.5.
- `Rebuild/model/tests/test_recovery.py` (sha256
  `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`,
  7/7 PASS) — cited in §2.3 to back the recovery contract
  Eq. `rho-zero-recovery`.

Recovery-test result already established at rb-001 and re-asserted
in §2.3: with $\rho$ clamped to zero, the extended-model headline
VDA, CF, and $\Rew_{\text{P}_k}$ values reproduce the inherited
model's reference numbers at floating-point identity, including the
peak $\text{VDA}^\star(\rho=0) = 0.07986$ at $\Rsens = 0.3831$.

Build verification (4 pdflatex passes + 1 bibtex pass):

- Pass 1: bib entries unresolved on first run; produced
  `main.aux` with `\\citation{...}` requests for `Slepian1962`,
  `CohenMaunsell2009`, `MullerFindlay1987`, `RuffCohen2016`,
  `Srinath2021`.
- BibTeX pass: resolved all 5 entries from `refs.bib`; produced
  `main.bbl`.
- Pass 2: 3 undefined-citation warnings (refs picked up in `.bbl`
  but `\\bibcite{...}` not yet in `.aux`).
- Pass 3: zero undefined-citation warnings.
- Pass 4: settled (0 warnings, 16 pages, 1177200 bytes).

The remaining `hyperref` "Token not allowed in a PDF string"
warnings are cosmetic Unicode-in-section-title issues from existing
sections and unchanged by this run.

# What the manuscript can now say

After rb-009 the manuscript may state (at no higher strength than
the §model section delivers):

1. **The three-lever decomposition** of the value effect:
   criterion shift (P3 → P4, share = CF), sensitivity re-allocation
   (P1 → P3, magnitude = VDA), decorrelation (Slepian-monotone lift
   of every per-policy supremum reward in $\rho$).
2. **The locus of A1** in the reward expression: A1 enters
   Eq. `expected-reward` in exactly one place,
   Eq. `pnofa-indep`; relaxing A1 is exactly replacing that product
   with the correlated joint orthant probability.
3. **The exact 1-D reduction** Eq. `pnofa-rho` for $P_{\text{no-fa}}(\rho)$
   under equicorrelation, with the $\rho \to 0$ recovery contract
   Eq. `rho-zero-recovery` honoured at floating-point identity by
   the extended model.
4. **The retracted §5.5 sentence** of the inherited paper: a
   distributional / variant- and cell-conditional ceiling on CF
   (not VDA), best stated at the median across the sweep rather
   than as a uniform inequality. The corrected version of the
   sentence is the blockquote at the end of §2.5.

Forward-reference targets that now resolve to filled content
rather than stubs: `\\ref{sec:model}`, `\\ref{sec:model-inherited}`,
`\\ref{sec:model-booking}`, `\\ref{sec:model-rho-channel}`,
`\\ref{sec:model-three-levers}`, `\\ref{sec:model-upper-bound}`,
`\\ref{def:three-levers}`, `\\ref{fig:vda-rho-variantA}`,
`\\ref{fig:vda-rho-variantB}`, `\\ref{fig:cf-vs-rho}`,
`\\eqref{eq:sdt-marginal}`, `\\eqref{eq:expected-reward}`,
`\\eqref{eq:vda-def}`, `\\eqref{eq:cf-def-model}`,
`\\eqref{eq:pnofa-indep}`, `\\eqref{eq:equicorr-cov}`,
`\\eqref{eq:pnofa-rho}`, `\\eqref{eq:rho-zero-recovery}`.

# Next increment

The two natural threads:

1. **RB-007 (C3 iso-VDA contour sim) → RB-011 (§5.2 redraft).**
   This thread discharges another §3.3 unifying-reframe item: the
   §5.2 categorical experimental-design claim ("high-validity
   paradigms show negligible VDA *regardless of other parameters*")
   gets replaced with a graded / quantitative iso-VDA contour band
   over $(V, v)$ at several $r$ and an explicitly hedged design
   recommendation. Model → sim order: RB-007 (sim) first, then
   RB-011 (manuscript).
2. **RB-014 (A2 heterogeneous-$r$ model extension)** opens the
   A2/A8 thread of model extensions; the between-preparation
   single-$r$ reading is adopted in §model already, so the next
   move is the heterogeneous-$r_i$ generalisation for §extensions /
   §limitations.

I default the next run to **RB-007 (C3 iso-VDA sim)** — higher
manuscript-voice leverage (directly attacks another categorical
self-characterisation; produces the figures §5.2 needs) and a
familiar code shape (reuse `Rebuild/sims/C1--cf-distribution/run.py`
infrastructure with a $(V, v)$ grid swap-in).

# Wiki cross-references

§11.1 mechanism-keyword sweep for this section:
{value-directed attention, criterion fraction, equicorrelated
Gaussian, Slepian inequality, decorrelation, noise correlation,
attention allocation}.

Consulted (already in wiki):

- `research_db/papers/cohen_maunsell2009_correlations.md` — bib
  entry `CohenMaunsell2009`. Cited in §2.3 ($\rho \in [0, 0.4]$
  envelope anchor, $r_\mathrm{SC} \approx 0.2$ in V4).
- `research_db/papers/ruff_cohen2016_cross_area_correlations.md` —
  bib entry `RuffCohen2016` added this run from the existing wiki
  stub's bibliographic metadata. Cited in §2.3 (structured-
  covariance scoped limitation).
- `research_db/papers/srinath2021_attention_information_flow.md` —
  bib entry `Srinath2021` added this run from the existing wiki
  stub's bibliographic metadata. Cited in §2.3 same paragraph.
- `research_db/papers/muller_findlay1987_sensitivity_criterion.md` —
  already wired by rb-007's §results-C1 CF definition citation. The
  §model CF definition (Eq. `cf-def-model`) forward-references
  §results-C1 for the literature anchor; no inline cite added in
  §model.

Confirmed absent (math-methods gap; inherited from rb-008 and
unchanged by this run):

- **Slepian, D. (1962)**. Bib entry `Slepian1962` in `refs.bib`
  since rb-005; no `research_db/papers/` stub. Cited in §2.3 and
  in `def:three-levers` for the monotonicity inequality.
- **Tong, Y.L. (1990)**. Not cited in §model directly (the
  appendix derivation already cites it). No `research_db/` stub.

No new wiki stubs added; `audit.py` not run (no wiki writes).

# Notes on guard-rails honoured

- **No claim restated more strongly than the ledger licenses.**
  Every numeric in §2.5 is sourced verbatim from the rb-002 results
  JSON or the rb-003 results JSON, with sha256 cited. The
  retraction of the inherited §5.5 sentence is framed as a
  reported finding on the empirical envelope, not as a derivable
  theorem; the variant-B counterpart figure is included to make
  the variant-conditional nature visible in the figure stack
  rather than only in the prose.
- **No new content the rebuild does not own.** No reference to
  PRISM, HRA, or the owner's neural-network programs (mission §1
  rule 8, §v0.2 changelog). The §model section stands on its own
  normative footing.
- **Recovery contract reasserted.** §2.3 names the recovery test
  by sha256 and by PASS count, satisfying the §5 simulation-mandate
  rule that every extension be pinned to the inherited model in
  the appropriate limit.
- **No directory renamed, moved, or deleted.** All writes are
  appends/edits within `Rebuild/`; the three figure files added to
  `Rebuild/manuscript/figures/` are copies of files that remain
  in place under `Rebuild/sims/A1--rho-channel/output/figures/`.
- **No external paid API used.** No web fetches this run.
