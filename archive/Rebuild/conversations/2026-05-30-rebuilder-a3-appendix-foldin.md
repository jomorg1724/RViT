---
type: conversation
agent: constructive-rebuilder
prompt_version: "0.2"
run_id: rb-046-2026-05-30
started: 2026-05-30T12:30:00Z
ended: 2026-05-30T13:00:00Z
worked_on: RB-046
output_kind: manuscript
claims_touched: [A3, C5, C2]
artifacts_written:
  - Rebuild/manuscript/sections/appendix.tex (sec:appendix-deriv-a3 subsection rewritten; §appendix-c5 cross-reference extended)
  - Rebuild/manuscript/sections/extensions.tex (three forward references discharged; one new forward-reference paragraph added)
  - Rebuild/manuscript/main.tex (new \DKL macro)
  - Rebuild/manuscript/main.pdf (55 pages / 2,790,640 bytes)
  - Rebuild/CLAIM_LEDGER.md (top reconcile + A3 row backing extended)
  - Rebuild/REBUILD_BACKLOG.md (RB-046 → done)
  - Rebuild/rebuilder_state.json (runs_completed 29 → 30)
  - Rebuild/BUILD_LOG.md (rb-046 entry prepended)
papers_added: []
spawned_tasks: []
---

# rb-046 — §appendix-deriv-a3 manuscript fold-in

## What I built

A ≈220-LaTeX-line `sec:appendix-deriv-a3` subsection in
[Rebuild/manuscript/sections/appendix.tex](../manuscript/sections/appendix.tex),
replacing the 15-line rb-017 stub at line 530. The new subsection
mirrors the structure of `sec:appendix-deriv-c2` (the rb-024 fold-in
pattern) and folds the rb-029 derivation file
([Rebuild/derivations/A3--power-mean-conservation.md](../derivations/A3--power-mean-conservation.md),
≈50 KB / 1026 lines) into the manuscript's formal appendix. Five
content blocks:

1. **Closed-form weights.** Boxed Equation~\eqref{eq:a3d-closed-form-weights}
   gives $\cost(\Rsens; p) = (2/(\Rsens^p+1))^{1/p}$,
   $\benefit = \Rsens\,\cost$ by direct substitution into
   $M_p(\benefit, \cost) = 1$ with $\benefit/\cost = \Rsens$. Three
   identities (I-1) ratio, (I-2) symmetric corner, (I-3) spread sign.
2. **HLP monotonicity in pointwise KL-divergence form.** Boxed
   Equation~\eqref{eq:a3d-hlp-kl}:
   $\partial \ln \cost/\partial p =
   -(1/p^2)\,\DKL(\mathrm{Bern}(\theta_p) \| \mathrm{Bern}(1/2))$
   with $\theta_p = \Rsens^p/(\Rsens^p+1)$. The classical HLP power-
   mean monotonicity inequality, in exact pointwise form for this
   family. Sign corollary Equation~\eqref{eq:a3d-mono-sign} +
   continuity-through-zero via $-(\ln \Rsens)^2/8$ limit.
3. **Symmetric corner + C5 corollary.** Proposition
   `prop:a3d-symmetric-corner` ($\benefit(1; p) = \cost(1; p) = 1$,
   full proof) + Corollary `cor:a3d-c5-invariance` (C5 conservation-
   form-invariance, full proof from the $\dprime$-map at
   $\Rsens=1$). The §appendix-c5 conservation-form-invariance
   paragraph picks up a formal cross-reference to these.
4. **Full three-step proof of Proposition
   `prop:r-dagger-invariance`.** Step 1: sensitivities $p$-independent
   at $\alpha=1/\Nloc$ via the vanishing bracket
   $\dprimemax\,f(1/\Nloc) - \dprime_{\mathrm{base}}$. Step 2: P3-
   optimal criteria $p$-independent by functional composition. Step
   3: $K_c, K_u$ ratio $p$-independent at the $p$-independent
   operands. Promotes the rb-017 §extensions-A3 proof sketch to a
   structural derivation tied to a specific property of the
   $\dprime$-map at the uniform allocation.
5. **d'-channel chain rule for $\partial \CF/\partial p$.** Equations
   `eq:a3d-chain-rule` / `eq:a3d-dprime-of-p` establish
   $\partial \dprime_c/\partial p \le 0$ and
   $\partial \dprime_u/\partial p \ge 0$ for $\alpha \ge 1/\Nloc$
   (opposite-sign $d'$ channels). Proposition
   `prop:a3d-rp3-invariance` ($\partial \Rpthree/\partial p \equiv 0$
   at $\alpha = 1/\Nloc$, full proof — the one analytic full-strength
   substatement) + the open-conjecture statement that the uniform
   inequality $|\partial_p \Rpfour| \le |\partial_p \Rpone|$ holding
   at $0$ reverse flips empirically on the $4{,}410$-cell grid would
   integrate to $\Delta\CF \le 0$.

## How it connects to the ledger

Discharges the A3 row's `appendix.tex:530` stub completely. The A3
thread is now wired across all FOUR output kinds for the first time
of any claim in the rebuild: **model (rb-015, RB-015), sim (rb-016,
RB-019), manuscript-extensions (rb-017, RB-034), derivation (rb-029,
RB-033), and manuscript-appendix (rb-046, RB-046)** — five
increments × four output kinds × A3 coverage.

The C5 row picks up a tighter cross-reference: the §appendix-c5
paragraph now points at Proposition `prop:a3d-symmetric-corner` and
Corollary `cor:a3d-c5-invariance` instead of the bare Section pointer
to §extensions-A3. The C2 row's `prop:r-dagger-invariance` picks up
the full three-step structural proof in the appendix; the inline
proof sketch in §extensions-A3 is preserved verbatim, and a one-
paragraph forward reference now points readers at the appendix
proof.

**No label drift in the live ledger.** All 10 verdict labels still
match the §3 table of `agents/paper_rebuilder_prompt.md` v0.2 (only
the §3 A6 entry remains stale; already flagged in CLAIM_LEDGER at
rb-018; not re-flagging).

## Simulation evidence

This run is pure manuscript prose — no model edits, no new sims, no
new bib entries. All numerical witnesses are inherited from rb-001 /
rb-015 / rb-016 / rb-029 and cited in the new subsection's
Reproducibility paragraph:

- rb-001 `test_recovery.py` digest
  `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`
  (recovery contract at $\Rsens=1$).
- rb-015 `test_conservation_family.py` digest
  `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`
  (family identities, symmetric-corner invariants; 14/14 PASS).
- rb-016 Block B sim digest
  `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`
  (`recovery.test_3_r_dagger_p_invariance`, max $|\Delta| = 0.0$
  across $p \in \{0, 1/2, 1\} \times \val \in \{2, 3, 5, 8, 10\}$).
- rb-029 finite-difference verification of Equation~\eqref{eq:a3d-hlp-kl}
  at 7 test pairs (LHS$-$RHS $\le 1.5\times10^{-10}$).

## Build / verification

- PDF: 55 pages / 2,790,640 bytes (was 53 / 2,763,376 at rb-028 =
  +2 pages, +27,264 bytes). Comparable to the rb-024
  §appendix-deriv-c2 fold-in pattern (appendix subsections without
  figures land lighter than results/extensions subsections).
- Build 4-pass clean: pass 1 hit two macro-stub misses (`\DKL`, no
  prior macro — fixed by adding
  `\newcommand{\DKL}{D_{\mathrm{KL}}}` to `main.tex` line 79; and
  `\Pthree`/`\Pone`/`\Pfour`/`\Ppolicy`/`\Ethree[\Rew]`/`\Rpi`, no
  prior macros — fixed by inline replacement with
  `\textrm{P3}`/`\textrm{P1}`/`\textrm{P4}`/`\textrm{P}`/`\Rpthree`/`R_{\mathrm{P}_i}`
  per the manuscript convention of plain-text policy labels). After
  fixes: pass 1 OK → bibtex no-op (0 new bib entries) → passes 2–4
  (settled; 0 undefined refs; 0 non-hyperref warnings).
- Cross-reference resolution verified via `pdftotext`: the new
  subsection appears in the PDF at pages 49–54 with all eight new
  labels resolved, and the four cross-reference updates in
  §extensions-A3 and §appendix-c5 all render the new appendix
  sections as printed numbers.

## What the manuscript can now say

Quoted verbatim ceilings (also captured in BUILD_LOG.md rb-046):

- "By the Hardy--Littlewood--Pólya power-mean monotonicity inequality,
  $\partial \ln \cost/\partial p = -(1/p^2)\,\DKL(\mathrm{Bern}(\theta_p)
  \,\|\, \mathrm{Bern}(1/2))$ (Equation~\eqref{eq:a3d-hlp-kl})."
- "C5 symmetric recovery is conservation-form-invariant:
  $\benefit(1; p) = \cost(1; p) = 1$ at every $p$
  (Proposition~\ref{prop:a3d-symmetric-corner}) and the asymmetric
  $\dprime$-map collapses pointwise to the symmetric baseline at
  $\Rsens = 1$ (Corollary~\ref{cor:a3d-c5-invariance})."
- "Proposition~\ref{prop:r-dagger-invariance} admits a full three-
  step proof: vanishing-bracket sensitivities at $\alpha = 1/\Nloc$;
  P3-optimal criteria $p$-independent; $K_c, K_u$ ratio
  $p$-independent. Numerical witness rb-016 max $|\Delta| = 0$."
- "The chain-rule analysis reduces $\partial \CF/\partial p$ to a
  competition between cued and uncued $d'$-channel gradients,
  establishes $\partial \Rpthree/\partial p \equiv 0$ at
  $\alpha = 1/\Nloc$ (Proposition~\ref{prop:a3d-rp3-invariance}),
  and identifies the uniform inequality $|\partial_p \Rpfour| \le
  |\partial_p \Rpone|$ as the closed-form conjecture whose
  empirical validity on the $4{,}410$-cell grid backs
  Theorem~\ref{thm:delta-cf-monotone}."

The manuscript does **not** license: a uniform closed-form proof of
$\Delta\CF \le 0$ (chain rule identifies the open inequality, does
not close it); a joint $(p, \corr)$ sensitivity (rb-016 is
$\corr = 0$ only); any new conservation-family member outside
Equation~\eqref{eq:a3d-closed-form-weights}.

## Next increment

Per mission §4.1, the highest-priority unblocked tasks (all the
RB-046-style "discharge a queued stub" jobs are now done; this is a
parallel-option decision):

- **RB-024** — C1 closed-form CF<0.5 boundary derivation. Prereq
  RB-005 done at rb-003. Natural rhythm match to RB-046.
- **RB-029** — A1 dormant-cell amplification follow-up sim. Prereq
  RB-010 done at rb-010. Most striking single qualitative finding
  available.
- **RB-040** — Slepian-gradient analytic locus for the cell-wise
  $\partial\VDA/\partial\rho$ surface. Prereq RB-025 done at
  rb-025. Would close the A1 manuscript-side architecturally.
- A manuscript-bookend increment (abstract / intro / limitations /
  methods) — the manuscript content sections are now wired (model,
  results-C1/C2/C3/C4, extensions-A3/A2/A8, appendix-derivation-A1/
  C2/C5/A3); the next architectural move is the bookend.

I recommend RB-024 as the next increment — "finish what's wired" is
the same rhythm RB-046 just discharged, and it's the only C1
derivation thread still open.

## Wiki cross-references

§11.1 mechanism-keyword sweep across `research_db/`: keywords
{power mean, generalised Hölder mean, Hardy-Littlewood-Pólya,
conservation, β+γ=2, β·γ=1, KL divergence, Jensen's inequality,
envelope theorem, criterion fraction sensitivity,
conservation-form-invariance, $p$-invariance, symmetric corner,
Sterbenz lemma}. The new appendix subsection cites HLP1934 only
(wired at rb-017); Bullen 2003 / Cover-Thomas 2006 are cited by
full bibliographic reference in the long-form derivation file
`Rebuild/derivations/A3--power-mean-conservation.md` (rb-029) and
are not re-cited in the manuscript subsection per the math-methods
scope inherited from rb-008 / rb-014 / rb-015 / rb-017. No new
`research_db/papers/` stubs; `audit.py` not re-run.
