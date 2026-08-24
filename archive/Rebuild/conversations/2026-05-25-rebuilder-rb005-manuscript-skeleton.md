---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-005-2026-05-25
started: 2026-05-25T13:25:00Z
ended:   2026-05-25T13:30:00Z
worked_on: RB-022
output_kind: manuscript
claims_touched: [cross-cutting]
artifacts_written:
  - Rebuild/manuscript/main.tex
  - Rebuild/manuscript/sections/abstract.tex
  - Rebuild/manuscript/sections/intro.tex
  - Rebuild/manuscript/sections/model.tex
  - Rebuild/manuscript/sections/results.tex
  - Rebuild/manuscript/sections/limitations.tex
  - Rebuild/manuscript/sections/methods.tex
  - Rebuild/manuscript/sections/appendix.tex
  - Rebuild/manuscript/refs.bib
  - Rebuild/manuscript/BUILD.md
  - Rebuild/manuscript/main.pdf
papers_added: []
spawned_tasks: []
---

# rb-005 — manuscript LaTeX skeleton

## What I built

A compileable LaTeX skeleton at `Rebuild/manuscript/`:

- `main.tex` — `article` class with the project's standard packages,
  theorem environments, and a complete macro family for the VDA
  notation (`\dprime`, `\VDA`, `\CF`, `\corr`, `\rdagger`, `\rstarinv`,
  `\PnoFA`, `\Rsens`, `\val`, `\valid`, `\Nloc`, …). Body is seven
  `\input{}` calls into `sections/`.
- Seven section stub files under `sections/`: `abstract.tex`,
  `intro.tex`, `model.tex`, `results.tex` (with four results
  subsections C1/C2/C3/C4), `limitations.tex`, `methods.tex`, and
  `appendix.tex` (with three appendix subsections deriv-A1,
  deriv-C2, C5). Each stub is a block comment naming the RB-NNN
  increment that will fill it and the `CLAIM_LEDGER.md` row that
  bounds the allowed strength, followed by an anticipated-contents
  paragraph in proper LaTeX.
- `refs.bib` — Slepian 1962 and Cohen & Maunsell 2009 as the two
  seed entries actually cited by the appendix stub.
- `BUILD.md` — toolchain documentation (`pdflatex` × 3 with one
  `bibtex` in the middle), per-section authoring workflow, and a
  caveats block recording that `latexmk`, `siunitx`, and `cleveref`
  are all absent from the sandbox's TeX Live 2026basic install.
- `main.pdf` — 3-page compiled output (build verification artifact).

The skeleton is intentionally thin: the §3.3 "distributional and
conditional by default" voice is encoded at the abstract / intro /
results section-header level so subsequent prose increments inherit
the framing without having to re-derive it.

## How it connects to the ledger

rb-005 is a *manuscript* output_kind that **changes no claim's
strength**. Its function is to create a fully-wired home for every
row of `CLAIM_LEDGER.md`. Per-section anchor map:

| `CLAIM_LEDGER.md` row | section file                  | section label                |
|---|---|---|
| C1                    | `sections/results.tex`        | `sec:results-c1`             |
| C2                    | `sections/results.tex`        | `sec:results-c2`             |
| C3                    | `sections/results.tex`        | `sec:results-c3`             |
| C4                    | `sections/results.tex`        | `sec:results-c4`             |
| C5                    | `sections/appendix.tex`       | `sec:appendix-c5`            |
| A1 (ρ channel)        | `sections/model.tex` + appendix | `sec:model`, `sec:appendix-deriv-a1` |
| A2 / A8 (heterogeneity) | `sections/limitations.tex`  | `sec:limitations`            |
| A3 (conservation family) | `sections/limitations.tex` | `sec:limitations`            |
| A6 (decision-noise)   | `sections/limitations.tex`    | `sec:limitations`            |
| A4 / A5 / A7 (unattacked) | `sections/limitations.tex` | `sec:limitations`            |

The `CLAIM_LEDGER.md` "last reconciled" stamp was bumped to rb-005
with the note "no label drift; rb-005 was a manuscript-skeleton
increment".

## Simulation evidence

This run was a manuscript increment, not a simulation increment, so
the §5 simulation mandate doesn't bite directly. The
manuscript-increment analogue of a recovery test is the build
verification:

- Build: `pdflatex` → `bibtex` → `pdflatex` → `pdflatex`, all four
  passes exit 0 cleanly.
- Output: `main.pdf` 3 pages, 316934 bytes, PDF version 1.7.
- Log: zero undefined references; warnings are only cosmetic
  Overfull/Underfull \hbox lines caused by long file-path literals
  inside stub brackets.

No `output/` directory or sha256 digest applies (the artifact is
human-authored LaTeX, not deterministic numeric output).

## What the manuscript can now say

Nothing new — rb-005 is a wiring increment, not a content increment.
The first prose increment that lands (most likely RB-010 covering
§results-C2) will be the first to "say" anything; its allowed
strength is bounded by `CLAIM_LEDGER.md` row C2 verbatim.

## Next increment

Single best pick: **RB-010** — draft §results-C2. Why:

- rb-004's `Rebuild/sims/C2--vda-vs-r-vfamily/` supplies the most
  analytic content per word of any single available source: the
  `r†(v)` v-family table, the peak-vs-threshold consistency table,
  the v-dependent A1 sign-flip in Δpeak, and two ready-to-include
  figures (`vda_curves_vfamily.png`, `r_dagger_vs_v.png`).
- It is a pure prose increment with no further sim/derivation
  prerequisite, so an honest 10–20 min budget fits comfortably.
- It exercises the manuscript-section workflow end-to-end (figure
  copy from sims/, citation of sha256 and reviewer-derivation file,
  wiki sweep before declaring section done) so subsequent
  manuscript increments inherit a working pattern.

Strong secondary alternatives:

- **RB-003** (A1 ρ-channel derivation increment) — unblocks RB-004
  model section, which is the spine of the "three levers" reframe.
  Derivation-track, not prose-track, so a different cognitive mode.
- **RB-007** (C3 iso-VDA contour-map sim) — finishes the
  central-tendency confident-spine sim sweep (C1, C2, C3) before
  pivoting to prose at all.

## Wiki cross-references (§7.3 sweep)

No sweep this run. Per mission §11, the §11.1-style mechanism-keyword
sweep is required *before declaring any manuscript section done*.
rb-005 declared **no section done** — only stubs — so the sweep
obligation does not apply this run. Each subsequent per-section
content increment (RB-010, RB-009, RB-013, …) will run its own sweep
before marking its section done.
