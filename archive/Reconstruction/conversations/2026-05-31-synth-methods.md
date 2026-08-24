---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: B7E3F0A2-1D4C-4F8A-9E2B-6C5A0D7E13F4
started: 2026-05-31T00:00:00Z
ended: 2026-05-31T00:00:00Z
worked_on: SY-010
output_kind: section
section_touched: sections/methods.tex
artifacts_consumed:
  - Reconstruction/manuscript/sections/model.tex (equations lifted by \ref)
  - Reconstruction/manuscript/sections/results.tex (eq:r-dagger, eq:r-inv, eq:r-inv-corner)
  - Rebuild/model/core.py (criterion grid, alpha grids, GH-64 quadrature)
  - Rebuild/sims/C1--cf-distribution/{README.md,run.py}
  - Rebuild/sims/C2--vda-vs-r-vfamily/README.md
  - Rebuild/sims/C3--iso-vda-Vv/README.md
  - Rebuild/sims/C4--anti-cue-inversion/README.md
firewall_violations_fixed: 0
gaps_opened: []
gaps_closed: []
compiles: true
manuscript_pages: 26
---

# SY-010 — Methods

## What I wrote

The Methods section (`sec:methods`), placed at the end of the arc, in
detailed Nature Neuroscience voice. Seven subsections:

1. **Task and decision model** (`sec:methods-model`) — a compact recap
   of the SDT model referencing `eq:sdt-marginal`/`eq:expected-reward`,
   plus the headline perceptual cell $(\Nloc,\dprimemax,f_0,h) =
   (4,2,0.5,\sqrt\cdot)$ and the four `eq:h-forms` used for
   transfer-function robustness.
2. **Benefit, cost, and reward variants** (`sec:methods-asymmetry`) —
   the additive conservation rule `eq:beta-gamma`, the power-mean
   conservation family deferred to Supplementary, and the two reward
   variants (A value-coupled $\CR$, B fixed $\CR=1$).
3. **Correlated-noise channel** (`sec:methods-quadrature`) — the
   one-factor Gauss–Hermite quadrature for `eq:pnofa-rho`: 64 nodes,
   $\le10^{-15}$ vs a 128-node reference across $\corr\in\{0,.05,.1,.2,
   .3,.4\}$; headline $\corr\in\{0,0.2\}$ anchored to V4 spike-count
   correlation (`CohenMaunsell2009`).
4. **Policy optimisation** (`sec:methods-optimisation`) — exhaustive
   grid search; the 121-point criterion grid ($\Delta c=0.05$ over
   $[-3,3]$, floor fixes $c=0$); the attention grids ($[1/\Nloc,1]$ for
   P1/P2, extended to $[0.02,1]$ for the distributional and anti-cue
   sweeps so $\alphacued<1/\Nloc$ is admissible, $\alphacued=1/\Nloc$ for
   P3/P4); value-blind caching.
5. **Parameter sweeps** (`sec:methods-sweeps`) — the four sweeps with
   exact grid sizes: distributional (22 $\Rsens$ × 21 $\valid$ × 5 $\val$
   × 2 variants = 4,620 nominal, 4,410 valid); VDA($\Rsens$) family
   (83-point log grid, $\val\in\{2,3,5,8,10\}$); iso-VDA ($31\times19
   \times3\times2 = 3{,}534$); inversion (closed-form $\rstarinv$ on 420
   cells + 197-point $\alpha$ verification + the anti-cue grid + a 544-cell
   $\alphacued^*$ map).
6. **Validation** (`sec:methods-validation`) — the $\corr\to0$ recovery
   contract (`eq:rho-zero-recovery`) to floating-point precision; the
   closed-form/grid agreement ($\rdagger(\val)$ ordering vs the peak
   $\Rsens^*$, the exact symmetric-corner identity `eq:r-inv-corner`);
   the Slepian monotonicity sign check.
7. **Reproducibility** (`sec:methods-reproducibility`) — fully
   deterministic, no Monte-Carlo, fixed grids giving bitwise-reproducible
   output; Python with standard numerical libraries.

## Grounding (assertion → evidence)

Recorded in full as **ME1–ME7** in `TRACE.md`. Key points:

- All equations are **lifted by `\ref`/`\eqref`** from the already-written
  Model and Results — no derivation is repeated, no definition duplicated.
- Grid sizes/node counts/tolerances are grounded digit-for-digit in the
  sim READMEs and `Rebuild/model/core.py`: criterion grid `C_GRID =
  arange(-3,3,0.05)` (121 pts); C1 `run.py` `R_GRID` (22), `V_GRID` (21),
  `V_LIST` {1..5}, `ALPHA_GRID` (0.02 step); `gauss_hermite(64)`; C2's
  "83-point + pinned" r-grid; C3's $31\times19\times3\times2=3{,}534$;
  C4's Steps A–D (420 / 197 / 144 / 544).
- Methods makes **no scientific finding** — it documents procedure; the
  findings remain in Results at their traced strength.

## Strength check

Nothing exceeds the evidence. Every Methods number is a procedural fact
matched to the source. The recovery tolerance is stated **conservatively**
($<10^{-6}$) and as an internal $\corr\to0$ limit check, not as agreement
with any external substrate. The C4 incidence percentages (48.6% etc.)
are not re-reported here — they live in Results as model facts.

## Firewall sweep

`grep -niE` for the full banned-vocabulary set on `sections/methods.tex`:
**zero hits.** One deliberate suppression worth recording: the C1/C2/C4
READMEs validate by comparing the rebuilt model to an external "reviewer
substrate" (e.g. max $|\Delta\CF| = 1.47\mathrm{e}{-6}$ across 4,410
cells; recovery 48.6% vs a reported 49.0%). Surfacing those would import
"reviewer"/comparison framing, so the Methods frames validation **only**
as the model's own internal $\corr\to0$ limit and its closed-form/grid
self-consistency. No file paths, sha256 digests, or sim ids appear in the
prose. "Supplementary," not "Appendix."

## Gaps

None opened — Methods requires no figures. G-001 (the attention-to-$\dprime$
mapping figure in the Model) remains open and unchanged.

## Compile

`pdflatex`×3 + `bibtex`, then a re-pass after fixing one 6.2 pt overfull
box (the inline cell-parameter tuple in `sec:methods-sweeps`, respaced as
separate math atoms). Final build: **26 pages** (was 24), 0 undefined
references, 0 undefined citations, 0 overfull boxes.

## Next increment

SY-009 (coherence pass over Results + Discussion) is **due** — four
sections have landed since the last coherence pass (SY-005). The last
unwritten body section is SY-011 (Supplementary: symmetric recovery at
$\Rsens=1$; the $\rdagger$ closed form; the conservation family), which
should also **close the two Methods forward-refs** to Supplementary
(`sec:appendix`). Recommended order: SY-009 → SY-011 → SY-012 (whole-paper
coherence) → SY-013 (Abstract, written last) → SY-014 (frontmatter /
draft-complete milestone).

## Drift watch

- The README cross-substrate recovery numbers are external comparisons;
  kept out of the manuscript by design (above). If a later run is tempted
  to quote them as validation, it must not — restate as the internal
  limit check.
- Methods now forward-refs `sec:appendix` for (a) the conservation family
  and (b) the $\rdagger$ / recovery derivations. Those refs currently
  resolve to the Supplementary stub; SY-011 must land real content so the
  whole-paper coherence pass (SY-012) finds no dangling promise.
- Grounding verified · Firewall clean · Compile verified (26 pp, 0 warnings).
