---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-050-2026-05-31
started: 2026-05-31T08:00:00Z
ended: 2026-05-31T08:30:00Z
worked_on: RB-050
output_kind: manuscript
claims_touched: [cross-cutting]
artifacts_written:
  - Rebuild/manuscript/sections/methods.tex
  - Rebuild/manuscript/main.pdf
  - Rebuild/CLAIM_LEDGER.md
  - Rebuild/REBUILD_BACKLOG.md
  - Rebuild/rebuilder_state.json
  - Rebuild/BUILD_LOG.md
papers_added: []
spawned_tasks: []
---

# rb-050 — §methods bookend: the rebuilt simulation infrastructure

## What I built

Replaced the rb-005 stub at `Rebuild/manuscript/sections/methods.tex`
(34 lines, ~70% placeholder) with a self-contained 5-subsection §methods
bookend (~250 LaTeX lines, ~1,700 words). The section catalogues the
rebuild's simulation infrastructure paralleling the original paper's §3
methods, with content organised by infrastructure tier rather than by
claim:

- **§8.1 The validated reference implementation** — `Rebuild/model/core.py`
  starting as a copy of `Critique/replications/C5--symmetric-recovery/`
  (byte-exact inherited backwards compat by construction), extended along
  four orthogonal axes (A1 ρ channel, A3 power-mean conservation family,
  A2 per-location $r_i$, A8 $N$-dim allocation simplex). Each axis gated
  by a recovery test.

- **§8.2 Recovery contracts** — Table `tab:methods-recovery` with all
  four sha256 digests verbatim from `rebuilder_state.json`:
  `d3c62215…` (A1, ρ→0); `f4f57a89…` (A3, p→1);
  `0486921f…` (A2, uniform $r_i$);
  `883ea15a…` (A8, homogeneous uncued).

- **§8.3 Simulation protocol** — five-point discipline + Table
  `tab:methods-sims-summary` listing all nine wired sims with output
  digest prefixes and manuscript cross-references.

- **§8.4 Derivations** — the four `Rebuild/derivations/` files (A1, C2,
  C4, A3) with their backing scope and verification.

- **§8.5 Reproducibility and the rebuild contract** — the
  simulate-first-write-second operating mode, software deps, and the
  full reproducibility ledger (`rebuilder_state.json` + `BUILD_LOG.md`
  + `CLAIM_LEDGER.md`).

The mid-build correction was identical to rb-049's: the first draft used
`\citep{Slepian1962}` (natbib) but the manuscript loads no natbib;
pass 1 fatal `! Undefined control sequence l.323 \citep`; fixed inline
to `\cite{}` before re-running pass 1.

## How it connects to the ledger

The §methods bookend changes no claim's rebuilt strength: it is a
catalogue of the infrastructure that already backs every wired claim.
What it does is make the rebuild's reproducibility contract explicit
and locatable. With §methods drafted, **all four bookends are now in
place (abstract + intro + limitations + methods)** and the rebuilt
manuscript is structurally complete for the first time:

```
abstract → intro → model → results × 4 → extensions × 3 →
limitations → methods → appendix × 3
```

Zero skeleton stubs remain. The "Last reconciled with live ledger" entry
in `CLAIM_LEDGER.md` is rewritten for rb-050, with the rb-049 paragraph
moved into "Previous reconcile" position.

Live-ledger sanity check (re-read at run start): all 10 verdict labels
still match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2 —
A1 CONTESTED, A2 CONFIRMED-CONDITIONAL, A3 CONTESTED, A6
WEAKLY-SUPPORTED (the §3 entry remains stale — already flagged in
CLAIM_LEDGER since rb-018), A8 CONFIRMED-CONDITIONAL, C1 CONTESTED,
C2 CONFIRMED-UNDER-ATTACK, C3 CONTESTED, C4 CONFIRMED-CONDITIONAL,
C5 CONFIRMED-UNDER-ATTACK. No drift; no §3-table update needed.

## Simulation evidence

No new sim ran this increment — §methods is pure manuscript prose
catalogueing existing infrastructure. The four recovery-test digests
cited in Table `tab:methods-recovery` are unchanged
(`d3c62215…` / `f4f57a89…` / `0486921f…` / `883ea15a…`), as are the
nine output digests in Table `tab:methods-sims-summary` (b692c064…,
91fc4692…, 09ecef3c…, 72820559…, 6ad651d6…, 489c7c25…, 22b183f9…,
055bf4ec…, beb2aa87…). All quoted verbatim from `rebuilder_state.json`.

Build evidence: 4-pass pdflatex+bibtex clean (after the `\citep`→`\cite`
fix). Pass 1 OK with ~60 forward-reference warnings (normal pass-1
behaviour for new labels); bibtex 0 new entries; pass 2 all references
resolved; passes 3 and 4 byte-identical to pass 2 at 63 pages /
2,860,922 bytes, settled, 0 undefined references, 0 non-hyperref
warnings. vs rb-049 baseline 2,815,939 bytes / 59 pages →
**+4 pages, +44,983 bytes** — the largest bookend yet because both
`tab:methods-recovery` and `tab:methods-sims-summary` are full-width
tabular blocks that the abstract / intro / limitations bookends did not
contain.

## What the manuscript can now say

The manuscript is structurally complete. The §methods section is the
canonical place a reader looks to verify any quantitative statement,
providing the full sha256 ledger that pins each claim to its
reproducible artifact. The §methods §8.5 reproducibility paragraph
states the three-artifact rule (recovery contract + deterministic sim
digest + (for novel propositions) derivation) and the
simulate-first-write-second operating mode that licenses the
manuscript's distributional/graded/conditional voice.

The §methods section adds no new claim and tightens no existing claim;
it makes the rebuild contract from the mission file (§5, §6, §10)
externally readable from the manuscript itself.

## Next increment

With the structural arc closed, every remaining queued task tightens an
existing result rather than adding a structural section. High-yield
sharpening candidates (all medium-or-low priority):

- **RB-024** (closed-form $\CF < 0.5$ boundary derivation) — only C1
  derivation thread still open; would let §results-C1 replace the
  empirical "22% of cells" with a closed-form predicate.
- **RB-029** (A1 dormant-cell amplification follow-up sim) — most
  striking single qualitative finding of rb-010; would add another
  falsifiable behavioural prediction to §model-upper-bound.
- **RB-040** (Slepian-gradient analytic locus for the cell-wise
  $\partial \VDA / \partial \corr$ surface) — would close A1
  manuscript-side architecturally, paralleling the rb-046 A3 closure.
- **RB-039** (finer $\corr$-grid for $\rdagger(\val; \corr)$) — would
  tighten Table `tab:r-dagger-rho-drift` toward a smooth curve.

Natural next: **RB-024** by the "discharge what is wired but not yet
derived" rhythm.

## Wiki cross-references

Sweep performed across `research_db/`; keywords {validated reference
implementation, recovery contract, simulation protocol, deterministic
digest, sha256 fingerprint, canonical JSON output, reproducibility,
equicorrelated Gaussian, one-factor Gauss-Hermite reduction, power-mean
conservation family, HLP monotonicity, simulate-first-write-second,
rebuild contract}. Every cited paper already wired (Slepian1962 from
rb-008). 0 new wiki stubs; `audit.py` not re-run (no wiki writes).

## Files written

- `Rebuild/manuscript/sections/methods.tex` — stub replaced by full
  bookend.
- `Rebuild/manuscript/main.pdf` — rebuilt 63 pages / 2,860,922 bytes
  (was 59/2,815,939 at rb-049).
- `Rebuild/CLAIM_LEDGER.md` — top reconcile paragraph rewritten for
  rb-050.
- `Rebuild/REBUILD_BACKLOG.md` — RB-050 entry added at top of recent
  block, status `done`.
- `Rebuild/rebuilder_state.json` — atomically rewritten;
  `runs_completed` 33 → 34, `done_task_ids` adds RB-050,
  `manuscript_sections_drafted` extended, `next_task_id_counter`
  50 → 51, `rb_050_manuscript_pdf_bytes` = 2860922 added.
- `Rebuild/BUILD_LOG.md` — rb-050 header written before drafting
  (crash-recoverable in_progress marker), body filled at end of run.
- `Rebuild/conversations/2026-05-31-rebuilder-methods-bookend.md`
  (this file).

No model edits; no new sims; no new bib entries; no new wiki stubs.
