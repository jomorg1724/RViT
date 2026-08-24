---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-018-2026-05-25
started: 2026-05-25T20:25:00Z
ended:   2026-05-25T20:45:00Z
worked_on: RB-013
output_kind: manuscript
claims_touched: [C5, A3]
artifacts_written:
  - Rebuild/manuscript/sections/appendix.tex (§appendix-C5 subsection: stub → full ~140 lines / ~8 KB)
  - Rebuild/manuscript/refs.bib (+2 entries: Sterbenz1974, Goldberg1991)
  - Rebuild/manuscript/main.pdf (rebuilt; 35 pages / 2,165,118 bytes; was 33 / 2,152,496 at rb-017)
  - Rebuild/CLAIM_LEDGER.md (header reconcile line + C5 row backing column)
  - Rebuild/REBUILD_BACKLOG.md (RB-013 queued → done)
  - Rebuild/rebuilder_state.json (atomic; runs 17 → 18; RB-013 added to done_task_ids and manuscript_sections_drafted; rb_018_manuscript_pdf_bytes field added)
  - Rebuild/BUILD_LOG.md (rb-018 entry: in_progress header pre-execution → full done body post-execution)
papers_added: []
spawned_tasks: []
---

# rb-018 — §appendix-C5 (manuscript increment) — DONE

## What I built

A full §appendix-C5 subsection in `Rebuild/manuscript/sections/appendix.tex`,
replacing the rb-005 stub placeholder. Two propositions:

- **Proposition prop:c5-realnumber (real-number recovery at $r=1$)** — universal
  over $(V, v, N, d'_{\max}, f_0, h, \rho)$. $\beta(1) = \gamma(1) = 1$ are
  exact floats, so the asymmetric per-location sensitivity rule
  $d'_i(\alpha) = d'_{\mathrm{base}} + s_i(r)\,(d'_{\max} f(\alpha) - d'_{\mathrm{base}})$
  collapses to $d'_i(\alpha) = d'_{\max} f(\alpha)$, the symmetric rule.
  Identical $d'$ arrays force identical $\alpha^\star, c_c^\star, c_u^\star,
  R^\star, \mathrm{CF}$ as real-number identities.

- **Proposition prop:c5-sterbenz (bit-exact symmetric recovery on the
  validation configuration)** — at the published config $(N=4, d'_{\max}=2.0,
  f_0=0.5, h=\sqrt{\cdot}, \mathrm{variant\ A})$: $a = d'_{\mathrm{base}} = 1.5$
  and the swept range $x = d'_{\max} f(\alpha) \in [1.0, 2.0]$ sits inside the
  Sterbenz band $[a/2, 2a] = [0.75, 3.0]$ for every grid point, hence the
  round-trip $a + (x-a) = x$ returns bit-for-bit, so
  $\max|\Delta\alpha^\star| = 0$ and $\max|\Delta R^\star| = 0$ exactly
  (not merely to machine epsilon).

Plus: a scope clause with the explicit off-band threshold
$f_0 < h(1/N)/(1+h(1/N)) = 1/3$ at $h=\sqrt{\cdot}, N=4$ (Eq.
eq:c5-sterbenz-threshold); a smooth-centre paragraph noting the asymmetric
slope ratio $\beta(r)/\gamma(r) = r$ is differentiable through $r=1$ with the
reviewer's continuity-probe slope $\approx 0.084$ reward units per unit $r$
cited as witness; a C5 conservation-form-invariance paragraph cross-referencing
§extensions-A3 (the corollary block there already cross-references
`sec:appendix-c5`, so both sides are now closed); and a reproducibility
paragraph citing the recovery-test pinned numerics at $r=1$ ($\VDA=0.039825$,
$\CF=0.728228$, $R_{P1}=2.317239$ all matched to max-abs-diff $0.0$) plus
sha256 `d3c62215…` (rb-001 recovery-test JSON) and sha256 `f4f57a89…`
(rb-015 conservation-family-test JSON).

Two new bib entries (Sterbenz1974, Goldberg1991), both cited by full
bibliographic reference per the math-methods scope inherited from rb-008/rb-017
(Slepian 1962, Tong 1990, HLP1934). No research_db/papers/ stubs added.

## How it connects to the ledger

Discharges the C5 row's `manuscript drafted:` license in `CLAIM_LEDGER.md`. The
live C5 verdict (CONFIRMED-UNDER-ATTACK, `Critique/verdicts/C5--symmetric-recovery.md`
v0.2 / 2026-05-22) gives:

- the real-number identity from Theorem 1 of the reviewer's derivation
  (`Critique/derivations/C5--symmetric-recovery.md`), restated here as
  Proposition prop:c5-realnumber in the rebuild's voice;
- the Sterbenz-lemma bit-exact bound from Theorem 2 of the same derivation,
  restated here as Proposition prop:c5-sterbenz;
- the off-band threshold $f_0 < h(1/N)/(1+h(1/N))$ from the reviewer's scope
  clause, made explicit here as Eq. eq:c5-sterbenz-threshold;
- the smooth-continuation observation from the reviewer's Block 4 continuity
  probe, restated as the smooth-centre paragraph;
- the conservation-form-invariance from rb-015's
  `test_p0_symmetric_corner_identity`, restated as a closing cross-reference
  to §extensions-A3.

The rebuilt manuscript may now state the C5 result at exactly this strength.
Over-statement (e.g. asserting the literal "0.0" as universal, or asserting a
knife-edge transition at $r=1$) is precisely the failure the rebuild exists to
fix and is avoided here by the explicit scope clause and smooth-centre
paragraph.

The mission §3.1 C5 row says: *"keep as an appendix consistency result; state
'machine precision' as the universal claim and note that the literal '0.0' is
configuration-specific (Sterbenz-lemma band), and that $r=1$ is the smooth
centre of the family, not a knife-edge."* The §appendix-C5 subsection lands
all three: (i) the universal claim is the real-number identity in Proposition
prop:c5-realnumber; (ii) the configuration-specificity of $0.0$ is
Proposition prop:c5-sterbenz with the explicit off-band threshold; (iii) the
smooth-centre is the dedicated paragraph with the continuity-probe slope.

## Simulation evidence

No new simulation. The §appendix-C5 subsection cites the existing recovery
contract framework:

- `Rebuild/model/tests/test_recovery.py` (rb-001) — seven recovery checks all
  PASS, sha256 `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`.
  Relevant for §appendix-C5:
  - `test_p_no_fa_rho0_equals_product` — binary equality of the $\rho=0$
    quadrature shortcut to the inherited product $\Phi(b_c)\,\Phi(b_u)^{N-1}$
    of Eq. eq:pnofa-indep; max-abs-diff $0.0$.
  - `test_policy_recovery_at_reference_r` at $r = 1.0$ — pins $\VDA = 0.039825$,
    $\CF = 0.728228$, $R_{P1} = 2.317239$, all to max-abs-diff $0.0$ against the
    reviewer's logs at
    `Critique/replications/A1--correlated-fa/output/results.json`. This is the
    direct numerical witness for Proposition prop:c5-realnumber at the headline
    cell.

- `Rebuild/model/tests/test_conservation_family.py` (rb-015) — 14/14 PASS,
  sha256 `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`.
  Relevant for §appendix-C5:
  - `test_symmetric_corner_invariant` — PASS binary, verifies
    `policies(r=1, p=0) == policies(r=1, p=1)` numerically.
  - `test_p0_symmetric_corner_identity` — PASS to floating-point identity,
    closed-form witness for $\beta(1, p) = \gamma(1, p) = 1$ at every $p$.
  This is the numerical witness for the conservation-form-invariance paragraph.

No new figures (consistent with the light-touch scope; the §appendix-C5
subsection has no figures of its own — the result is a numerical identity, not
a curve or surface).

## What the manuscript can now say

The rebuilt §appendix-C5 may state C5 as follows (the exact claim now
licensed):

> "At $r = 1$ the asymmetric benefit/cost family collapses to
> $\beta(1) = \gamma(1) = 1$, and the asymmetric implementation evaluated at
> $r = 1$ produces the same $d'$ arrays as the symmetric special case —
> a real-number identity, universal over $(V, v, N, d'_{\max}, f_0, h, \rho)$
> (Proposition prop:c5-realnumber). At the validation configuration the
> Sterbenz lemma additionally gives a bit-exact guarantee: every swept output
> $x = d'_{\max} f(\alpha) \in [1.0, 2.0]$ sits inside the band
> $[a/2, 2a] = [0.75, 3.0]$ with $a = d'_{\mathrm{base}} = 1.5$, so the
> round-trip $a + (x-a) = x$ is exact, hence $\max|\Delta\alpha^\star| = 0$ and
> $\max|\Delta R^\star| = 0$ exactly (Proposition prop:c5-sterbenz). The
> hypothesis is sufficient but not necessary: off the band (notably
> $f_0 < h(1/N)/(1+h(1/N)) = 1/3$ at $h = \sqrt{\cdot}, N = 4$) the recovery is
> exact only to machine precision ($\sim 1$ ulp). The universal statement is
> 'identical to machine precision'; the literal '$0.0$' of the published
> Appendix~A is a structural guarantee of the chosen validation config, not a
> property of the model. The collapse at $r = 1$ is the smooth interior of a
> two-sided family rather than a removable singularity: the asymmetric slope
> ratio $\beta(r)/\gamma(r) = r$ is differentiable through $r = 1$, with
> $\max|\Delta R^\star|$ scaling linearly in $|r - 1|$ at slope
> $\approx 0.084$ reward units per unit shift in $r$ (reviewer continuity probe
> at the headline cell). The result is conservation-form-invariant by
> construction: at $r = 1$ the family identity $\beta / \gamma = 1$ forces
> $\beta = \gamma$, and any power-mean constraint $M_p(\beta, \gamma) = 1$
> then forces $\beta = \gamma = 1$ for every $p$, so the entire argument holds
> under any conservation rule in the power-mean family
> (Section~\ref{sec:extensions-a3} corollary)."

It does **not** yet license:

- (a) the literal "$0.0$" as a universal property of the model — only as a
  validation-config statement under variant~A;
- (b) any new behavioural / empirical claim — C5 is a consistency result;
- (c) the conservation-form-invariance under conservation choices outside the
  power-mean family $M_p(\beta, \gamma) = 1$ (e.g. an exotic non-power-mean
  rule);
- (d) a closed-form rule for how the smooth-centre slope $\approx 0.084$
  reward units per unit shift in $r$ depends on cell parameters — only its
  value at the headline cell from the reviewer's continuity probe.

## Next increment

Cleanest next single-increment: **RB-014 — A2 heterogeneous-r model extension
(model)** — `extensions.tex` is already structured by rb-017 to host one
subsection per lever extension, and A2/A8 is the natural successor thread to
A3 in the same file. Medium effort; prereq RB-001 done.

Alternatives, in priority order:
- **RB-026 — C2 r†(v) ρ>0 closed-form (derivation)** — fills the
  §appendix-deriv-c2 stub and extends the closed-form r†(v) machinery to the
  A1 channel; prereq RB-006 done.
- **RB-033 — A3 formal derivation (derivation)** — fills the §appendix-deriv-a3
  stub placed by rb-017; prereq RB-019 done.
- **RB-024 — C1 closed-form CF<0.5 boundary (derivation)** — would let
  §results-c1 replace "frac<0.6 = 22%" with a closed-form predicate; prereq
  RB-005 done.

Dependency-order preference is model → simulation → derivation → manuscript,
so RB-014 is preferred (opens a new model extension thread); RB-026 and RB-033
are appendix-derivation infills.

## Wiki cross-references

Mechanism-keyword sweep performed: {Sterbenz lemma, floating-point arithmetic,
IEEE-754, machine precision, symmetric special case, bit-exact recovery,
ULP, rounding error, real-number identity, smooth centre of family, β/γ kink,
gain modulation, surround suppression}.

- No `research_db/papers/` stubs hit on any sweep key — math-methods gap,
  inherited from rb-008 (Slepian 1962, Tong 1990) and rb-017 (HLP1934).
  Out of rebuilder scope per the reviewer's CR-035/CR-037 backlog. The
  Sterbenz1974 and Goldberg1991 citations in §appendix-C5 use the full
  bibliographic reference in refs.bib.
- The interpretive note "$r=1$ is the balanced gain-modulation vs suppression
  null" implicitly references the same `reynolds_heeger2009_normalization`
  substrate cited from §model (rb-009) and §extensions-A3 (rb-017); no new
  citation introduced here (the §appendix-C5 paragraph cross-references
  Definition def:three-levers in §model rather than citing the substrate
  directly).
- audit.py not re-run (no wiki writes).
