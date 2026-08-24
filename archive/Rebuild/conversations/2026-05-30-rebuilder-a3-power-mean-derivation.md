---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-029-2026-05-30
started: 2026-05-30T00:00:00Z
ended: 2026-05-30T00:00:00Z
worked_on: RB-033
output_kind: derivation
claims_touched: [A3, C5, C2]
artifacts_written:
  - Rebuild/derivations/A3--power-mean-conservation.md (49720 bytes / 1020 lines)
  - Rebuild/CLAIM_LEDGER.md (top reconcile rewritten; A3 row backing extended)
  - Rebuild/REBUILD_BACKLOG.md (RB-033 → done; RB-046 spawned)
  - Rebuild/rebuilder_state.json (runs_completed → 29)
  - Rebuild/BUILD_LOG.md (rb-029 entry)
papers_added: []
spawned_tasks: [RB-046]
---

# rb-029 — A3 power-mean conservation family derivation

## What I built

The rebuild's first formal A3 derivation, at
[Rebuild/derivations/A3--power-mean-conservation.md](Rebuild/derivations/A3--power-mean-conservation.md)
(≈50 KB / 1020 lines, 9 sections + Verification + Extensions). The
file promotes the rb-017 §extensions-A3 manuscript sketch into a full
mathematical derivation in the rebuild's voice. The reviewer has no A3
derivation file — the verdict at
[Critique/verdicts/A3--multiplicative-conservation.md](Critique/verdicts/A3--multiplicative-conservation.md)
relies on the replication numerics — so this derivation is the project's
unique formal A3 statement.

The architectural moves:

- **§2.** Power-mean family $\PowerMean_p(\benefit, \cost) = 1$ with
  $\benefit/\cost = \Rsens$; closed-form $\cost(\Rsens; p) =
  (2/(\Rsens^p+1))^{1/p}$, $\benefit = \Rsens\cost$ (Eq. 2.3, boxed)
  by direct substitution. Limits $p=1$ additive, $p=0$ multiplicative
  (via a series-expansion computation), $p=-1$ harmonic. Three
  preserved identities (ratio, symmetric corner, sign of spread).
- **§3.** The Hardy–Littlewood–Pólya power-mean monotonicity inequality
  translated to a pointwise KL-divergence closed form:
  $$
    \partial \ln \cost / \partial p
    \;=\;
    -\frac{1}{p^2}\,D_{\mathrm{KL}}\!\bigl(\mathrm{Bern}(\theta_p)
            \,\|\,\mathrm{Bern}(1/2)\bigr),
    \quad
    \theta_p = \frac{\Rsens^p}{\Rsens^p+1}.
  $$
  Eq. 3.3 is *boxed* — this is the formal derivation's headline new
  identity, the rebuild's improvement over the verdict's textbook
  citation of HLP. Corollary 3.1 states both $\benefit$ and $\cost$
  are strictly decreasing in $p$ for $\Rsens \ne 1$.
- **§4.** Proposition 4.1 (symmetric corner identity $\benefit(1; p) =
  \cost(1; p) = 1$, full proof) + Corollary 4.2 (C5 conservation-form-
  invariance, full proof from the $\dprime$-map evaluation at $\Rsens =
  1$). The §appendix-c5 forward reference to "the conservation-form-
  invariance corollary" now has an analytic backing.
- **§5.** Full three-step proof of Proposition 5.1 ($\rdagger(\val)$
  $p$-invariance), promoting the rb-017 §extensions-A3 sketch.
- **§6.** d'-channel chain rule for $\partial\CF/\partial p$ via the
  envelope theorem: $\partial \Rpthree/\partial p \equiv 0$ at $\alpha
  = 1/N$ analytically; $\partial\CF/\partial p$ sign reduces to a
  competition between two $\dprime$-channel gradients (Eqs. 6.3–6.6);
  the uniform closed-form proof of $\Delta\CF \le 0$ remains open. The
  rebuild's two-tier statement of the A3 lever is now: (i) analytic
  full strength = $\rdagger, \Rpthree$ $p$-invariance; (ii) empirical
  full strength + chain-rule motivation = $\Delta\CF \le 0$ at $0/4410$
  reverse flips on the C1 sweep.

## How it connects to the ledger

**Discharges** the A3 row's "Derivation §appendix-derivation-A3
(RB-033) remains low-priority" license that has carried since rb-017.
The A3 row is now fully wired across model (rb-015), sim (rb-016),
manuscript-extensions (rb-017), AND derivation (rb-029). No remaining
A3 strands of the rebuild substrate are missing.

The C2 row gains a full formal proof of Proposition prop:r-dagger-invariance
(rb-017 stated only a sketch); the C5 row's appendix subsection (rb-018
sec:appendix-c5) gains its forward-referenced conservation-form-invariance
corollary as an analytic statement (Corollary 4.2). Strength on all
three rows is unchanged: the derivation deepens the analytic backing,
not the ceiling on the claims.

**No label drift in the live ledger** (10/10 verdict labels still match
the §3 table of `agents/paper_rebuilder_prompt.md` v0.2; A6 stale entry
already flagged in CLAIM_LEDGER at rb-018).

## Simulation evidence

This is a derivation-only increment — no new sim was needed (rb-015
family-identity test and rb-016 conservation-band sim already provide
all numerical backing). But the derivation embeds one new numerical
cross-check: **Eq. 3.3 (the KL form) was verified by finite-difference
at 7 test pairs** $(\Rsens, p) \in \{(0.3548, 0.5), (0.3548, 1),
(10, 1), (10, 0.5), (3.162, 2), (0.5, -1), (5.0, 1.5)\}$ with central
FD $\epsilon = 10^{-6}$. LHS-RHS agreement $\le 1.5\times 10^{-10}$ in
every case; at $\Rsens = 1$ both sides are exactly $0$. The check is a
reproducible derivation of the beta_gamma closed form and Bernoulli
definition (~10-line Python from the §3.2 algebra), and is reported
inline as the verification rationale of §3.3.

Pre-existing sim digests cited:

- **rb-015** `test_conservation_family.py` sha256
  `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`
  (14/14 PASS) — backs Eqs. 2.3, Proposition 4.1, Corollary 4.2 numerics.
- **rb-016** `Rebuild/sims/A3--conservation-band/output/results.json`
  sha256 `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`
  — backs Proposition 5.1 numerically (TEST 3 to FP identity across
  $p$), Corollary 3.1 numerics at the peak cell ($+13.72\%$ shift of
  $\cost$ at $\Rsens = 0.3548$ going $p = 1 \to 0$), and §6.4 empirical
  $\Delta\CF \le 0$ at $0/4410$ reverse flips.

All four model-test recovery digests unchanged after this derivation
(pure consumer of substrate; no model code, no test code touched).

## What the manuscript can now say

Five new statements landed at appendix-derivation strength, listed in
verbatim form in the BUILD_LOG `rb-029` entry. In summary:

1. Power-mean family is the canonical generalisation of A3 (Eq. 2.3).
2. HLP monotonicity has a pointwise KL-divergence closed form (Eq. 3.3,
   verified to $1.5 \times 10^{-10}$).
3. C5 corollary holds at every $p$ (Corollary 4.2, full proof).
4. $\rdagger(\val)$ is $p$-invariant with a full three-step proof
   (Proposition 5.1).
5. The d'-channel chain rule reduces $\partial\CF/\partial p$ to a
   competition between two $\dprime$-gradients; uniform closed-form
   proof of $\Delta\CF \le 0$ remains open.

The manuscript does not yet license the manuscript-side discharge of
the §appendix-deriv-a3 stub at
[Rebuild/manuscript/sections/appendix.tex:530](Rebuild/manuscript/sections/appendix.tex:530)
— queued as RB-046 (spawned this run, medium priority, parallels the
rb-023 → rb-024 §appendix-deriv-c2 pattern).

## Next increment

Per §4.1 of the mission, the highest-priority unblocked open task is
**RB-046** (§appendix-deriv-a3 manuscript fold-in, spawned this run,
medium priority — natural rhythm match to rb-023→rb-024). Alternative
parallel options: **RB-024** (C1 closed-form CF<0.5 boundary derivation,
prereq RB-005 done), **RB-029** (A1 dormant-cell amplification follow-up
sim, the most striking single qualitative finding of rb-010 deserving a
clean falsifiable closeup), **RB-040** (Slepian-gradient analytic locus
for the cell-wise $\partial\VDA/\partial\rho$ surface). RB-046 is
preferred because it discharges the rb-017 stub completely and closes
the A3 row's last open manuscript thread, before the manuscript work
shifts toward abstract / intro / limitations bookends.

## Wiki cross-references

§11.1 mechanism-keyword sweep across `research_db/` performed for
keywords {power mean, generalised Hölder mean, Hardy-Littlewood-Pólya,
conservation, β+γ=2, β·γ=1, KL divergence, Jensen's inequality,
envelope theorem, criterion fraction sensitivity}. All needed
mathematical references either:

- already wired in `Rebuild/manuscript/refs.bib` from prior runs:
  `HLP1934` (Hardy–Littlewood–Pólya 1934, added at rb-017),
  `Sterbenz1974` (added at rb-018),
- or cited by full bibliographic reference per the math-methods scope
  inherited from rb-008/rb-014/rb-017 and the reviewer's CR-035/CR-037
  scope: Bullen 2003 *Handbook of Means and Their Inequalities*,
  Cover & Thomas 2006 *Elements of Information Theory*.

No new `research_db/papers/` stubs added; `audit.py` not re-run (no
wiki writes). The math-methods stubs gap is unchanged — same status as
rb-008/rb-014/rb-015/rb-017/rb-023.

The derivation cites the reviewer's verdict
([Critique/verdicts/A3--multiplicative-conservation.md](Critique/verdicts/A3--multiplicative-conservation.md))
and the A3 replication
([Critique/replications/A3--multiplicative-conservation/](Critique/replications/A3--multiplicative-conservation/))
as the empirical anchor for §1.3 and §6.4 (the $0/4410$ reverse-flip
finding the rebuild restates at full empirical strength).
