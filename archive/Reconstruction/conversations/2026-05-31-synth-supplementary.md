---
type: conversation
agent: paper-writer
prompt_version: 0.2
run_id: E8F1A0D4-7C26-4B9A-A3E5-1F08C7B24D60
started: 2026-05-31T11:30:00Z
ended: 2026-05-31T12:00:00Z
worked_on: SY-011
output_kind: section
section_touched: sections/appendix.tex (Supplementary); refs.bib (+Tong1990); sections/discussion.tex (1 firewall fix)
artifacts_consumed:
  - "decorrelation-channel derivation (one-factor reduction, Slepian monotonicity, two-channel sign)"
  - "escape-threshold derivation (boundary FOC, rho-aware gradients, r-dagger(v;rho), drift table)"
  - "symmetric-recovery material (real-number identity, Sterbenz bit-exact band, smooth centre)"
  - "power-mean conservation derivation (closed-form weights, HLP-as-KL, invariances, CF chain rule)"
  - "CLAIM_LEDGER rows C2, C5, A3, A1 (silent strength ceiling)"
  - "model write-up PDF (notation for d'_base, b_i, the SDT primitives)"
firewall_violations_fixed: 1
gaps_opened: 0
gaps_closed: 0
compiles: true (33 pages)
---

# SY-011 — Supplementary derivations and extensions

## What I wrote

The Supplementary was a red one-line stub at the start of the run, yet
two main-text sections already forward-referenced it for derivations a
reader would expect to find:

- **Model §reward** ends "the full derivation of (the correlated no-FA
  integral) and this monotonicity is in the Supplementary material."
- **Results §4.2** ends "its derivation is given in the Supplementary
  material."

So the increment had a clear, unblocked target. I wrote the whole
Supplementary as four subsections in original venue voice:

1. **The correlated no-false-alarm probability and its monotonicity.**
   The one-factor representation, conditional independence given the
   shared latent, and the integrate-out step that yields the boxed
   one-dimensional integral `eq:pnofa-rho`; the 64- vs 128-node
   Gauss–Hermite agreement; the orthant-monotonicity Proposition
   (`prop:orthant-monotone`) and its per-policy reward corollary
   (`cor:policy-monotone`); and the positive two-channel account of why
   the sign of $\partial\VDA/\partial\corr$ depends on $\Rsens$.
2. **Closed-form escape threshold.** Boundary collapse to
   $\dprime_{\mathrm{base}}$; the two $\corr$-aware gradient integrals
   `eq:gh-grad-c`/`eq:gh-grad-u`; the boundary first-order condition
   `eq:boundary-foc-rho` with $K_c(\val;\corr),K_u(\val;\corr)$; the
   boxed threshold Proposition `prop:escape-rho` (`eq:r-dagger-rho`); the
   structural $\corr\to0$ recovery to the Results closed form
   `eq:r-dagger`; and the drift table `tab:r-dagger-rho-drift`.
3. **Symmetric recovery at unit benefit/cost ratio.** The universal
   real-number identity `prop:symmetric-recovery`; the bit-exact
   Sterbenz-band identity `prop:bitexact-recovery` with its off-band
   threshold `eq:sterbenz-threshold`; and the smooth-centre paragraph
   (unit ratio is the balanced null, not a knife-edge).
4. **The power-mean conservation family.** Closed-form weights
   `eq:power-mean-weights`; HLP monotonicity as a KL-divergence identity
   `eq:hlp-kl`; the symmetric-corner identity `prop:symmetric-corner` and
   its recovery corollary; the full three-step proof that the escape
   threshold is conservation-form invariant `prop:escape-invariance`; and
   the criterion-fraction chain rule with the one analytic invariant
   (`prop:p3-invariance`) and the honestly-open uniform $\Delta\CF\le0$
   bound stated as an empirical result over 4,410 cells.

All labels are descriptive and claim-id-free; the standard normal density
glyph is `\varphi` throughout (matching the body), and `\Phinorm` is the
CDF. One genuine, verifiable citation (`Tong1990`, Springer 1990) was
added to back the Slepian Proposition alongside the already-wired
`Slepian1962`.

## Grounding

Nineteen scientific assertions, every one traced in TRACE.md (rows
P1–P19) to validated derivation material, the reference implementation's
documented behaviour, or a real citation. Editorial connective tissue
(the subsection intro, the transitions between propositions) asserts
nothing beyond what those rows license. No figure is placed — the section
is pure derivation — so no figure could be wanted-but-absent here.

## Strength check

Used the ledger silently as the ceiling and stayed under it on every row:

- **C2** is "Confirmed, strengthened by the closed form": I state
  `eq:r-dagger-rho` as a Proposition, the $\corr\to0$ recovery as
  structural, and the drift as positive at every $\val$ with a 5/5
  sign-match — exactly the ledger's licensed content. The $\corr=0$
  column of `tab:r-dagger-rho-drift` reproduces the already-written
  `tab:r-dagger-family` (0.343 … 0.016) digit-for-digit.
- **C5** is "Confirmed consistency result; machine precision universally,
  literal $0.0$ config-specific; $\Rsens=1$ smooth centre": I wrote
  exactly that two-tier statement, with the off-band threshold and the
  smooth-centre continuity, never as a correction of anything.
- **A3** is "general conservation family, headline numbers as bands": I
  present the family and its invariances at full strength but mark the
  uniform $\Delta\CF\le0$ closed form **open**, reporting only the
  empirical 4,410-cell statement (0 reverse flips, frac$<0.5$
  $4.0\%\to8.3\%$, median move $<0.005$).
- **A1** monotonicity (Proposition) and the two-channel sign of
  $\partial\VDA/\partial\corr$ — stated as model properties, with the
  sign as a question the model answers, not a theorem of monotonicity.

Nothing is invented; nothing is stated above its row.

## Firewall sweep

The source derivation material is dense with build-machinery language
("the inherited paper's §5.5", "the reviewer's attack form", "promote …
in the rebuild's voice", file paths, sha256 digests, rb-/RB- ids, "the
published Appendix A"). None of it reached the page: the Supplementary
was composed positively from the mathematics, not transcribed.

- First-pass grep on the new file: only two `inherit` hits, both ordinary
  mathematical usage ("the density terms inherit $\corr$ only through
  $c_i^\star$"; "$\partial_p\Rpone$ and $\partial_p\Rpfour$ inherit the
  moving optimum"). Reworded to `depend on` / `carry` as insurance.
- Whole-manuscript grep then caught one **pre-existing** comparison-hedge
  in `sections/discussion.tex` line 56 — "…a substantial tail, **not a
  categorical split**", the precise "not a categorical floor" pattern the
  firewall names. Rewritten to the positive "…a substantial tail across
  the parameter space." No number or strength changed.
- Final whole-manuscript sweep (banned vocabulary + comparison-hedges):
  **zero hits.** `firewall_clean` stays true.

## Gaps

None opened. G-001 (the Model §2.3 attention-to-$d'$ illustration figure,
owner-mediated) remains the single open gap, untouched this run.

## Compile

`pdflatex` ×3 + `bibtex`, all exit 0. **33 pages** (was 26), 0 undefined
references or citations, largest overfull box 3.0 pt (one display fix
removed a 32.7 pt box in S.1). `Tong1990` added to `refs.bib` and
resolved by bibtex with no warnings.

## Next increment

**SY-012 — full pre-abstract coherence pass.** Its last prerequisite
(SY-011) is now done. The Supplementary adds roughly thirty new
`\ref`/`\eqref` targets and four propositions, so the next run should
verify the complete cross-reference graph end to end, confirm the Methods
"→ Supplementary" pointers resolve to the right subsections, reconcile
notation across Methods↔Supplementary ($\dprime_{\mathrm{base}}$, the
GH-node count, the $b_i$ convention), and confirm G-001 is the only open
placeholder. After that coherence pass, the abstract (SY-013) is written
from the finished body, then the front/back-matter pass (SY-014).

## Drift watch

- The $\corr=0$ escape-threshold values in `tab:r-dagger-rho-drift` must
  stay identical to `tab:r-dagger-family` if either is ever re-evaluated;
  they currently match exactly.
- The Supplementary references `eq:beta-gamma` (additive rule) and
  `def:three-levers`; the coherence pass should confirm the
  conservation-family framing here (additive = $p{=}1$ endpoint) reads
  consistently with the Methods "power-mean family → Supplementary"
  pointer and the Discussion conservation-band paragraph.
- A1's two-channel sign story in S.1 and the empirical sign-flip reported
  in Results §4.2/§4.3 should be checked for consistent wording in the
  coherence pass (both say the sign flips with $\Rsens$; no number is
  duplicated, so this is a wording check only).
