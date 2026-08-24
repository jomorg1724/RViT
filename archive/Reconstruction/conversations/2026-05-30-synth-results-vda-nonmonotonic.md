---
type: conversation
agent: paper-writer
prompt_version: "0.2"
run_id: A7E3F1C9-2B58-4D6E-8F01-3C9A7E0B16D2
started: 2026-05-30T23:55:00Z
ended: 2026-05-30T23:59:59Z
worked_on: "SY-004 — Results §4.2: VDA non-monotonic in r, closed-form escape threshold"
output_kind: section
section_touched: "sections/results.tex (sec:results-vda-nonmonotonic)"
artifacts_consumed:
  - "Rebuild/CLAIM_LEDGER.md (C2 row, A1 row — silent strength ceiling)"
  - "Rebuild/manuscript/sections/results.tex §results-c2 (validated prose, equations, tables, figures)"
  - "Rebuild/sims/C2--vda-vs-r-vfamily/output/figures/{r_dagger_vs_v,vda_curves_vfamily}.png"
  - "Rebuild/manuscript/main.tex / Reconstruction main.tex notation block (\\newcommand)"
firewall_violations_fixed: 0
gaps_opened: 0
gaps_closed: 0
compiles: true
pages: 13
---

# What I wrote

Added the paper's confident centerpiece as a new Results subsection,
`sec:results-vda-nonmonotonic` ("The value-directed attention benefit is
non-monotonic in the benefit/cost ratio"), appended after the §4.1
conservation-robustness paragraph. Five paragraphs:

1. **Lead** — $\VDA(\Rsens) = \Rpone - \Rptwo$ rises from zero, peaks in
   an interior band, decays to zero; this shape is the model's signature.
2. **Closed-form escape threshold** — $\rdagger(\val) =
   K_u(\val)/[(\Nloc-1)K_c(\val)]$ (Eqs eq:r-dagger, eq:K-c, eq:K-u),
   from $\partial_\alpha\Rpone|_{1/\Nloc}=0$; a theorem of the model
   definitions, full derivation deferred to the Supplementary.
3. **Threshold falls with cued value** — Table r-dagger-family
   ($\rdagger$ 0.343→0.016 across $\val=1..10$) + Fig r_dagger_vs_v.
4. **Peak sits inside the predicted band** — peak $r^\star>\rdagger(\val)$
   for every $\val$ (Table peak-vs-threshold, 84-pt log-grid), supported
   on $(\rdagger(\val),\rdagger(1))$; peak height grows 0.012→0.183 with
   $\val$ (Fig vda_curves_vfamily).
5. **Decorrelation sensitivity** — $\corr:0\to0.2$ suppresses the peak
   for $\val\le8$, amplifies at $\val=10$; $r^\star$ drifts up; the
   closed-form $\rdagger(\val;\corr)$ drifts up +3%..+30% and sign-matches
   the empirical peak drift at every $\val\neq1$. Stated positively: the
   decorrelation lever is signed by the task's value structure — the
   operational content of the three-lever decomposition.
6. **Scope** — additive conservation, $\valid=0.5$; $\corr$-aware
   derivation and conservation-band sensitivity deferred to Supplementary
   / Discussion.

Two figures copied from the C2 sim output into `manuscript/figures/`.

# Grounding (assertion → evidence)

See TRACE.md rows V0–V7. Every number in Tables r-dagger-family,
peak-vs-threshold, rho-sensitivity and both figures derives from the
$84\,r\times5\,v\times2\,\rho$ C2 sweep (output sha256 09ecef3c…); the
closed-form $\rdagger$ and its $\corr$-aware extension from the C2
derivation file (Props 2.1, 4.1). The criterion fraction and the
$\corr$-recovery contract were already defined in the Model — not
redefined here, only used.

# Strength check

Nothing exceeds the ceiling. The non-monotonicity is the one finding the
ceiling licenses as a confident centerpiece (LEDGER:C2), so it is stated
plainly. The decorrelation result is held to LEDGER:A1 strength —
reported as a $\val$-signed model property, with the empirical peak-drift
table as data and the closed-form lower-edge drift as the mechanistic
counterpart; no claim that independence is a uniform upper bound on VDA,
and no comparison to any absent statement.

# Firewall sweep

Grep over `results.tex` for the full banned-vocabulary set (reconstruct,
rebuild, synthesiz, inherited, original, prior, previous, published,
critique, reviewer, verdict, ledger, provenance, defensible, restate,
retract, rb-/RB-/CR-/sha256, Rebuild/, Critique/, research_db, §5.5,
CONFIRMED/CONTESTED, claim ids C1–5/A1–8) → **zero hits**. The source
prose I drew on was dense with this vocabulary ("the inherited paper",
"live skeptical-reviewer verdict", "the original paper's §5.5 framing is
retracted", rb-002, sha256 paths); all of it was lifted as science only
and rewritten in positive standalone voice. No violations introduced.

# Gaps

None. Every number and both figures existed in validated outputs.

# Compile

`pdflatex ×2 + bibtex` + third pass, all exit 0. 13 pages (was 10), 0
undefined references, 0 undefined citations. Forward references to the
$\corr$-aware derivation and drift table point at `sec:appendix`
(Supplementary stub exists; the detailed content lands under SY-011) —
the `\ref`s resolve, so no dangling reference.

# Next increment

SY-005 — first interleaved coherence pass over Intro + Model + Results
§4.1–§4.2 (four sections integrated; a pass is due per mission §4.1).
Check notation drift vs the `\newcommand` block, duplicated definitions,
dangling `\ref`, intro previews vs body strength, figure/caption
consistency, and clear the known overfull `\hbox` (~52pt) in Model §2.4;
re-sweep the firewall. Then SY-006 (Results §4.4, the graded VDA regime).

# Drift watch

No ledger drift observed for C2 (CONFIRMED-UNDER-ATTACK) or A1
(CONTESTED, promoted to the $\corr$ lever) relative to the strengths I
wrote to. The §4.2 statements sit at or below their ledger rows.
