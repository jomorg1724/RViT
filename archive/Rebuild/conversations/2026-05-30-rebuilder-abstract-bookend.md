---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-047-2026-05-30
started: 2026-05-30T13:00:00Z
ended: 2026-05-30T13:45:00Z
worked_on: RB-047
output_kind: manuscript
claims_touched: [cross-cutting]
artifacts_written:
  - Rebuild/manuscript/sections/abstract.tex (replaced rb-005 stub; ~85 LaTeX lines, ~430 words)
  - Rebuild/manuscript/main.pdf (rebuilt; 55 pages / 2,792,842 bytes; +2,202 bytes vs rb-046)
  - Rebuild/REBUILD_BACKLOG.md (RB-047 added in_progress → done)
  - Rebuild/BUILD_LOG.md (rb-047 entry, full body)
  - Rebuild/CLAIM_LEDGER.md (reconcile paragraph updated to rb-047)
  - Rebuild/rebuilder_state.json (atomic update; runs_completed 30 → 31)
papers_added: []
spawned_tasks: []
---

# rb-047 — abstract bookend (manuscript)

## What I built

The first cover-to-cover narrative of the rebuilt manuscript:
replaced the rb-005 abstract stub in
[Rebuild/manuscript/sections/abstract.tex](Rebuild/manuscript/sections/abstract.tex)
with a 4-paragraph honest abstract (~430 words, ~85 LaTeX lines) at
the §3.3 unifying-reframe voice. Every quantitative claim in the
abstract is at the band / distributional / conditional strength its
row of `CLAIM_LEDGER.md` licenses. The original-paper categorical
phrasings — `CF` floor `[0.60, 0.96]`, "negligible regardless of
other parameters", uniform no-inversion, A1 upper bound on `VDA` —
appear only as what is being retracted, never as what is being
stated.

**Paragraph structure:**

1. The original question (cued $\val \ge 1$, $\valid \in [1/\Nloc,
   1]$ change-detection) + the three-lever decomposition (criterion
   + sensitivity + decorrelation; cross-references `sec:model`,
   `def:three-levers`) + the ρ-channel one-factor Gauss–Hermite
   reduction with $\corr \to 0$ FP-identity recovery + the lead
   voice sentence: "every headline result at its defensible
   distributional, graded, or conditional strength rather than as a
   categorical floor."

2. The four C-row headline results: C1 ($\CF$ concentrated in
   $[0.30, 1.00]$, median $0.76$; inherited $[0.60, 0.96]$ retracted
   on both ends; $\corr = 0.2$ drops strict min below $0.5$); C2
   (non-monotonicity + closed-form $\rdagger(\val) = K_u/[(\Nloc -
   1) K_c]$ + $\corr > 0$ extension + conservation-form-invariance);
   C3 (graded contour band; $\valid \ge 0.95$ at grid floor under
   any $(\Rsens, \corr)$; $\valid \ge 0.80$ survives only at
   $\corr = 0$; $\valid \ge 0.60$ fails); C4 (conditional theorem
   with explicit boundary $\valid \ge 1/[(\Nloc - 1) \val + 1]$ +
   **anti-cue inversion** as new falsifiable prediction with
   $36.1\%$ incidence at $\Nloc = 4$); C5 (universal real-number
   identity, conservation-form-invariant by construction).

3. The A1 §model-upper-bound retraction: independence is **not** an
   upper bound on $\VDA$; what it actually upper-bounds is the
   criterion fraction, and only in variant A; $\partial \VDA /
   \partial \corr$ sign-flip near $\Rsens \approx 0.5$, with the
   cell-wise crossover sweeping past $\Rsens \approx 0.79$.

4. The three extension levers (A2 heterogeneous-$\Rsens$ as bounded
   perturbation; A3 power-mean conservation-family band; A8 N-dim
   policy with new conditional binding at multiplicative
   conservation) + the closing voice clause stating that every
   quantitative claim is backed by a sim + recovered limit +
   deterministic output hash + figure under `Rebuild/sims/`, every
   novel proposition is derived under `Rebuild/derivations/`, and
   nothing in the abstract exceeds its row of `CLAIM_LEDGER.md`.

## How it connects to the ledger

The abstract is a **summary**, not a fresh claim. It discharges no
new verdict and moves no rebuilt strength. Every numerical or
qualitative assertion in it is sourced from a single row of
[CLAIM_LEDGER.md](../CLAIM_LEDGER.md):

| Abstract claim | CLAIM_LEDGER row | Verdict label |
| --- | --- | --- |
| Three-lever reframe; ρ → 0 FP-identity recovery | A1 row | CONTESTED |
| `CF ∈ [0.30, 1.00]`, median 0.76, `[0.60, 0.96]` retracted | C1 row | CONTESTED |
| `r†(v) = K_u/[(N-1) K_c]`, ρ > 0 extension, $p$-invariance | C2 row | CONFIRMED-UNDER-ATTACK |
| Graded $\valid$ thresholds (0.95 / 0.80 / 0.60) | C3 row | CONTESTED |
| Conditional theorem + anti-cue inversion 36.1% at N=4 | C4 row | CONFIRMED-CONDITIONAL |
| Universal real-number identity at $r=1$ | C5 row | CONFIRMED-UNDER-ATTACK |
| A1 upper-bounds CF (variant A), sign-flip at $r ≈ 0.5$ | A1 row | CONTESTED |
| A2 bounded perturbation, A3 power-mean band, A8 new conditional | A2 / A3 / A8 rows | CONFIRMED-CONDITIONAL / CONTESTED / CONFIRMED-CONDITIONAL |

No verdict label moved this run; no row's rebuilt strength changed;
the only `CLAIM_LEDGER.md` edit is the rb-047 reconcile paragraph
recording that the abstract has been wired and that no drift was
observed.

## Simulation evidence

This run produced no new simulations. The abstract is the canonical
summary of simulation outputs that have already landed:

- A1: `Rebuild/sims/A1--rho-channel/` (sha256
  `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`)
  and `Rebuild/sims/A1--vda-signflip-cellwise/`
  (`489c7c2581d1e940cfc67427e0793959bb33b24afda075ee648743aa2ac659ea`).
- C1: `Rebuild/sims/C1--cf-distribution/`
  (`91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`).
- C2: `Rebuild/sims/C2--vda-vs-r-vfamily/`
  (`09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`).
- C3: `Rebuild/sims/C3--iso-vda-Vv/`
  (`72820559e1c1ab1919f74308623eaf4230aa3ea92ad3d9c62d81e993e4f27de6`).
- C4: `Rebuild/sims/C4--anti-cue-inversion/`
  (`6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`).
- A2: `Rebuild/sims/A2--heterogeneous-r/`
  (`22b183f942d6b1f8868848ec1143ab959afd78c72cd6d3704763eedf5713e615`).
- A3: `Rebuild/sims/A3--conservation-band/`
  (`055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`).
- A8: `Rebuild/sims/A8--nd-uncued-sweep/`
  (`beb2aa879402e5c9f4c354a2c9f53a98c466d0989085dc8c78370be99dee290b`).

Each sim has a recovery test against the inherited model in its
appropriate limit; each is cited (transitively, through the body
sections) by the abstract. No new figure is added (the abstract is
prose only, no `\includegraphics`).

## What the manuscript can now say

The rebuilt paper has, for the first time, a cover-to-cover
narrative:

```
abstract (rb-047 NEW) → intro stub → model (rb-009; rb-026 fold-in)
   → results-c1 (rb-007) → results-c2 (rb-006)
   → results-c3 (rb-011) → results-c4 (rb-013)
   → extensions-A3 (rb-017) → extensions-A2 (rb-022) → extensions-A8 (rb-028)
   → limitations stub → methods stub
   → appendix-C5 (rb-018) → appendix-deriv-C2 (rb-024) → appendix-deriv-A3 (rb-046)
```

55-page PDF, 2,792,842 bytes, 0 undefined refs, 0 LaTeX warnings.

The abstract may now be quoted verbatim as the rebuild's short-form
position statement; the intro, limitations, and methods bookends
can lean on its voice and citation network when they are drafted.

## Next increment

**§limitations bookend** (replace the rb-005 stub in
`sections/limitations.tex`). Rationale: the stub already lists the
four sub-items the section will fold in — A3 conservation-family
band, A2/A8 heterogeneity, A6 deferral, A4/A5/A7 open scope — and
each of those is wired in the body. The section is a natural
counterpart to the abstract: where the abstract lists what the
rebuilt paper *says*, the limitations section lists what it
*does not say* and why. Lifting the §scope paragraphs from each
body section into a single bookend voice is a clean, well-bounded
next increment.

Alternatives, all unblocked: §intro bookend; §methods bookend;
RB-024 (C1 closed-form CF<0.5 boundary derivation); RB-029
(A1 dormant-cell amplification follow-up sim); RB-040
(Slepian-gradient analytic locus for cell-wise $\partial \VDA /
\partial \corr$). All low-priority sharpening passes; the
manuscript can already state every C/A claim at its licensed
strength without them.

## Wiki cross-references

Sweep keywords for this run: {value-directed attention, criterion
fraction, decorrelation lever, three-lever decomposition, anti-cue
inversion, conservation family, equicorrelated Gaussian, escape
threshold, narrow regime, central tendency, distributional vs
categorical claim, symmetric recovery}.

Every paper the abstract alludes to is already wired through body
sections (the abstract has zero direct `\cite{}` keys beyond
cross-references to the rebuild's own sections): CohenMaunsell2009,
MullerFindlay1987, Slepian1962, HLP1934, RuffCohen2016, Srinath2021,
McAdamsMaunsell1999, ReynoldsHeeger2009, Treue1999, Carrasco2011,
GhoseMaunsell2002, Sani2017, Sterbenz1974, Goldberg1991,
WangTheeuwes2018, WangSamaraTheeuwes2019, KongLiWangTheeuwes2020,
FailingTheeuwes2018, Hickey2010, Posner1980.

No `research_db/papers/` stubs added this run; `audit.py` not
re-run (no wiki writes). The math-methods gap (Slepian 1962,
Tong 1990, HLP 1934, Bullen 2003, Sterbenz 1974, Goldberg 1991,
Cover & Thomas 2006) remains as inherited from rb-008 / rb-013 /
rb-014 / rb-017 / rb-029 — out of rebuilder scope per the
reviewer's CR-035 / CR-037 backlog.
