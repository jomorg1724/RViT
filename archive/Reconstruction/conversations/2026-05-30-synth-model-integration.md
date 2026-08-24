---
type: conversation
agent: integrative-synthesizer
prompt_version: 0.1
run_id: B1F4A2E7-3C8D-4E55-9A21-7F0C6D9E8A14
started: 2026-05-30T22:00:00Z
ended: 2026-05-30T22:40:00Z
worked_on: SY-002
output_kind: section
section_touched: sections/model.tex
artifacts_consumed:
  - Critique/source/main.pdf (§2.1–2.5, pp.2–4) — structure
  - Rebuild/manuscript/sections/model.tex (rb-009) — harvest material
  - Rebuild/CLAIM_LEDGER.md (A1, C5 rows) — strength ceiling
  - Rebuild/derivations/A1--rho-channel.md — derivation reference
  - Rebuild/model/core.py, model/tests/test_recovery.py — recovery contract
gaps_opened: [G-001]
gaps_closed: []
compiles: true
pages: 7
---

# SY-002 — Model integration

## What I assembled

The reconstructed **Model** section, re-flowed from the rebuilder's
claim-organised `model.tex` into the original's §2 arc:

- **2.1 Task structure** — $\Nloc\ge2$ locations, value/validity cue,
  change-trial structure, per-location SDT marginals (Eq. sdt-marginal).
- **2.2 Attention allocation** — $\alphacued$/$\alphauncued$ shares,
  uniform $1/\Nloc$.
- **2.3 Attention-to-perception mapping** — transfer $f(a)$, four
  $h$-forms, the $\benefit(\Rsens)/\cost(\Rsens)$ asymmetry, the
  $\dprime_c/\dprime_u$ map with role-reversal/clamp and the symmetric
  $\Rsens{=}1$ centre.
- **2.4 Reward structure + decorrelation channel** — variants A/B, the
  expected-reward Eq., the locus of independence at $\PnoFA$, the
  equicorrelation covariance, the **boxed exact 1-D integral**
  $\PnoFA(\corr)$, and the $\corr{=}0$ floating-point recovery contract.
- **2.5 Policy decomposition** — P1–P4, the
  criterion/validity-attention/VDA gain split, the CF definition, and
  **Definition (the three levers)** = criterion / sensitivity /
  decorrelation.

Equations were lifted verbatim from the rebuilder's drafts so notation
matches the copied `\newcommand` block. Manuscript grew 3 → 7 pages.

## Provenance

The §5.2 mandate, discharged: TRACE rows **M1–M14** (`TRACE.md`, Model
block). Machinery/framing → ORIG §2.1–2.5 + RB:model.tex (verbatim
equations). Decorrelation channel (M9–M11, M14) → LEDGER:A1 +
RB:model.tex `eq:pnofa-rho` / `eq:rho-zero-recovery` /
`def:three-levers` + DERIV:A1--rho-channel.md + `model/core.py` +
`test_recovery.py`. C5 smooth-centre wording (M6) → LEDGER:C5. Every
citation resolves in `refs.bib`. No sentence without an artifact.

## Strength check

| Ledger row | How I wrote it | Did I exceed? |
|---|---|---|
| A1 | $\corr$ as a model parameter with an exact 1-D integral and a FP-identity recovery contract; "three levers, not two" Definition. The §5.5 "upper bound on VDA" claim is *named as open*, not asserted. | No — stated at model-parameter strength, empirical sign claims deferred. |
| C1 | CF is *defined* (Eq. cf-def); distribution explicitly deferred to Results. The retracted "$[0.60,0.96]$" floor does **not** appear in the Model. | No floor stated. |
| C5 | $\Rsens{=}1$ described as the "smooth centre" of the asymmetry family; exact properties pointed to the Appendix. | No — consistency framing only. |

**Key re-narrativisation call.** The rebuilder's `model.tex` second half
(`sec:model-upper-bound`: the §5.5 retraction, the cell-wise sign-flip
$\Delta\VDA$ distribution + `tab:a1cw-summary` + four A1 figures) is
*empirical* content the original raises in §5.5 (Discussion) and §4.3
(Results), not §2. Per **"the original wins on structure"** I deferred
all of it (carry-in note on SY-003), keeping the Model to machinery. M14
routes the upper-bound question forward without asserting or pre-rebutting
it — exactly the categorical-claim trap the agent family exists to avoid.

## Gaps

- **Opened G-001** — original Figure 1 (attention-to-$\dprime$ mapping,
  three $\Rsens$ regimes). No regenerated artifact exists under
  `Rebuild/`; the A1 sim emits only Results-A1 figures (vda_curves,
  cf_vs_rho). Pure model illustration, recoverable from
  `model/core.py:d_prime_asym` → owner-routed to the rebuilder.
  Non-blocking: a red placeholder sits in §2.3 and the section compiles.
- Closed: none.

## Compile

`pdflatex`×2 + `bibtex` + `pdflatex`. **7 pages**, 0 undefined
references/citations, 0 rerun requests, 0 non-hyperref warnings. No
`\includegraphics` in the Model (the one figure is the G-001 placeholder),
so no missing-figure errors.

## Next increment

**SY-003** — Results 4.1 (C1, criterion typically dominant): CF
distribution at distributional strength (median ≈0.76, $[0.30,1.00]$,
frac<0.6; **no floor**), the contested high-$r$ corner, the $\corr$
sensitivity (carried-in CF($\corr$) channel: cf_vs_rho). Place
cf_histogram / cf_heatmap / cf_curves; place the original's Figure 2
(reward decomposition) if a rebuilder artifact exists, else gap.

## Drift watch

Did not re-open `Critique/verdicts/` (the Model states A1 only at
model-parameter/recovery strength, comfortably inside the ledger ceiling;
the A1 row records no label drift as of rb-047). No action.

**Provenance verified** (M1–M14 each have a TRACE row).
**Compile verified** (7 pages, 0 warnings).
