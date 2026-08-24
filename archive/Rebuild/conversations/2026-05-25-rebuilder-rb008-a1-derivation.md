---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-008-2026-05-25
started: 2026-05-25T14:35:00Z
ended: 2026-05-25T15:00:00Z
worked_on: RB-003
output_kind: derivation
claims_touched: [A1]
artifacts_written:
  - Rebuild/derivations/A1--rho-channel.md
  - Rebuild/CLAIM_LEDGER.md (A1 row backing column + reconcile-line updated)
  - Rebuild/REBUILD_BACKLOG.md (RB-003 status queued → done)
  - Rebuild/rebuilder_state.json (RB-003 added to derivations_written + done_task_ids)
  - Rebuild/BUILD_LOG.md (rb-008 entry prepended)
  - Rebuild/conversations/2026-05-25-rebuilder-rb008-a1-derivation.md (this file)
papers_added: []
spawned_tasks: []
---

## What I built

`Rebuild/derivations/A1--rho-channel.md` — the rebuild's own independent
derivation of the decorrelation channel that the rebuilt model wires in,
in seven sections plus a Verification block and an Extensions block.

The derivation establishes, in the rebuild's constructive voice (not
the reviewer's attack voice):

1. **§1 — Locus of A1.** A1 enters $\mathbb E[R]$ in exactly one
   place: the no-FA product (Eq. 1.4). The change-trial bracket is
   linear in marginal hit rates and never multiplies across locations,
   so relaxing A1 means *exactly* replacing that one product. This
   isolates A1 cleanly from assumption A6.
2. **§2 — Exact 1-D reduction.** Equicorrelation lets the orthant
   probability collapse to a 1-D integral via the one-factor
   representation (Eq. 2.2); the resulting boxed Eq. (2.3) is exactly
   what `Rebuild/model/core.py:p_no_fa_point` / `:p_no_fa_grid`
   implement (Gauss–Hermite-64, Eq. 2.5). $\rho \to 0$ recovers the
   inherited product to floating-point identity (Eq. 2.4).
3. **§3 — Slepian monotonicity (Prop. 3.1) → per-policy reward bounds
   (Cor. 3.2).** All four policies P1–P4 have $R(\mathrm P_k;\rho)$
   non-decreasing in $\rho$.
4. **§4 — VDA sign is not determined by Cor. 3.2.** Two competing
   channels: (a) criterion devaluation pushes CF down in $\rho$;
   (b) concentration-cost relaxation pushes VDA up in $\rho$ at high
   $r$. Sign-flip in $r$ where the channels balance. Statements A
   (CF upper-bound, variant A) and B (sign-flip locus $r \in [0.38,
   0.56]$) are the rebuilt model's normative claims.
5. **§5 — Numerical realisation.** All numerics tied to
   `Rebuild/sims/A1--rho-channel/` sha256 `b692c064…` and cross-
   referenced to the cell-wise CF ordering from
   `Rebuild/sims/C1--cf-distribution/` sha256 `91fc4692…`.
6. **§6 — Scope.** Equicorrelation specificity, magnitude envelope,
   recovery contract globality, explicit non-promises (RB-023 / RB-025 /
   RB-026 forwarded; structured-covariance scoped out).
7. **§7 — References.** Slepian 1962, Tong 1990, Cohen & Maunsell 2009,
   Ruff & Cohen 2016, Srinath et al. 2021, plus the `Rebuild/model/`
   identifiers the derivation describes.

This is the first artifact in `Rebuild/derivations/`. No new
simulation; no new code. The derivation is *pure formalisation* of
material the model and the sims have already produced — exactly the
operating mode for a derivation increment under §4 of the mission.

## How it connects to the ledger

A1's live verdict is **CONTESTED**. The rebuilt strength the
manuscript may state is the central-tendency / conditional form
already in the CLAIM_LEDGER row: independence upper-bounds CF (variant
A only) and the pointwise upper-bound on VDA fails. The derivation
formalises that strength by:

- Pinning the *exact* form of A1's relaxation (Booking, §1.2) —
  removing any ambiguity about whether A1 is the no-FA product or a
  pooled-detection global rule.
- Proving the orthant monotonicity (Prop. 3.1, citing Slepian 1962)
  and the per-policy reward bound (Cor. 3.2) — both true, neither
  sufficient to upper-bound VDA.
- Explicating the two-channel decomposition (§4) that makes the
  sign-flip in $r$ a *mechanistic* prediction of the rebuilt model
  rather than an empirical curiosity.
- Naming the empirical envelope (Statement B, $r \in [0.38, 0.56]$
  across $\rho \in [0.1, 0.4]$) within which the sign-flip is
  certified, and what is *not* yet certified (closed-form
  $r^\dagger(v;\rho)$ → RB-026; tighter sign-flip bracket → RB-023).

No live-verdict label drifted from `agents/paper_rebuilder_prompt.md`
v0.2 §3 today (all 10 verdict files match; A6 still WEAKLY-SUPPORTED
per the existing flag).

## Simulation evidence

The derivation cites two simulations and one model test, all already
landed:

- `Rebuild/sims/A1--rho-channel/` (rb-002, sha256
  `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`)
  — every numerical statement in §5 sources from this sim's
  `output/results.json`.
- `Rebuild/sims/C1--cf-distribution/` (rb-003, sha256
  `91fc4692dbc106eca9c90770c79e22f7f4757d76421ed55e7e8e91f80e44706c`)
  — §5.3 cites the 84%/64% cell-wise CF ordering from the 4,410-cell
  sweep to generalise the headline-cell upper-bound across the
  parameter space.
- `Rebuild/model/tests/test_recovery.py` (sha256
  `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`,
  7/7 PASS) — guarantees the model honours Eq. (2.4) at $\rho = 0$.

Each numbered equation in the derivation is bound to a specific
implementation token in `Rebuild/model/core.py` (table in BUILD_LOG).
There is no formula in the derivation that the code does not exercise.

## What the manuscript can now say

The §appendix-derivation-A1 subsection of `Rebuild/manuscript/main.tex`
may state (verbatim ceiling):

> *"The rebuilt model promotes the per-location-independence
> assumption to a tunable equicorrelation parameter $\rho \in [0, 1)$.
> The reward decomposes such that A1 enters $\mathbb E[R]$ in exactly
> one place — the no-false-alarm product (Eq. 1.4) — and replacing
> that product by the exact equicorrelated joint orthant probability
> (Eq. 2.3, a one-dimensional integral via the one-factor
> representation 2.2) is the faithful and complete relaxation of A1
> within the model's reward structure. The independent corner $\rho =
> 0$ is recovered to floating-point identity (Eq. 2.4). Slepian's
> monotonicity (Proposition 3.1) makes the orthant probability — and
> therefore each policy's supremum reward (Corollary 3.2) — non-
> decreasing in $\rho$. The value-directed-attention difference
> $\mathrm{VDA}(\rho) = R(\mathrm P_1;\rho) - R(\mathrm P_2;\rho)$ is
> not sign-determined by Corollary 3.2; it splits into two competing
> channels (criterion devaluation vs concentration-cost relaxation)
> whose relative weight depends on the cost--benefit ratio $r$. At
> the headline cell this yields two falsifiable statements: (A) the
> criterion fraction is non-increasing in $\rho$ in variant A; (B)
> the sign of $d\mathrm{VDA}/d\rho$ flips with $r$ in the band
> $r \in [0.38, 0.56]$ across $\rho \in [0.1, 0.4]$. The inherited
> §5.5 'upper bound on VDA' self-characterisation is therefore
> retracted; what independence upper-bounds is the criterion fraction
> in variant A, not VDA."*

This is exactly the strength the C2 / A1 / C1 manuscript ceiling has
been bound to since rb-002 — now underwritten by a derivation, not
only by a simulation.

The §model section of the manuscript may, separately, cite this
derivation as the formal justification for the "three levers, not
two" reframe and for displaying Eq. (2.3) as the rebuilt model's
no-FA primitive.

## Next increment

**RB-004 — manuscript §model section.** Its prereqs were `[RB-002,
RB-003]`; both are now done. RB-004 is the single most consequential
manuscript section remaining: it carries the "three levers, not two"
reframe, displays Eq. (2.3) as the rebuilt model's no-FA primitive,
and ties together A1 (this run), the C1 distributional restatement
(rb-007), and the C2 closed-form r† (rb-006) into a coherent model
spine. Estimated wall-clock ~10–15 min for prose + `pdflatex` × 3
build.

Alternative same-priority picks:

- **RB-007** (C3 iso-VDA contour sim) — opens C3 results subsection.
  Independent of RB-004; could be parallel.
- **RB-008** (C4 inversion sim with $V < 1/N$ anti-cue prediction)
  — opens C4 results subsection. Independent of RB-004.

The natural model→sim→derivation→manuscript order (§4.1) and the
load-bearing centrality of the §model section argue for RB-004 next.

## Wiki cross-references

Mechanism-keyword sweep on the derivation's content (equicorrelated
Gaussian, orthant probability, Slepian, attention noise correlations,
value-directed attention, multivariate sensitivity, Gauss–Hermite
quadrature):

- **[[cohen_maunsell2009_correlations]]** — `research_db/papers/`,
  cited as the empirical anchor for $\rho \approx 0.2$ in V4
  ($r_\mathrm{SC}$ measurement).
- **[[ruff_cohen2016_cross_area_correlations]]** — `research_db/papers/`,
  cited in the §6 structured-covariance scope limitation.
- **[[srinath2021_attention_information_flow]]** — `research_db/papers/`,
  cited in the §6 supra-pairwise limitation.
- **Slepian 1962** *Bell Syst. Tech. J.* 41(2):463–501 — NOT in
  `research_db/`. Math-methods gap (same gap the reviewer flagged for
  C5 and A8 derivations). Cited by full bibliographic reference; no
  stub written in this run (out of scope).
- **Tong 1990** *The Multivariate Normal Distribution* (Springer,
  §5.1) — NOT in `research_db/`. Same gap. Cited by full reference.

No new `research_db/papers/` stubs added; `audit.py` not invoked
(no write to wiki).

## Notes on the independence requirement

The mission directs that this derivation be authored *independently*
against the inherited model rather than copied from
`Critique/derivations/A1--correlated-fa-upper-bound.md`. I read the
reviewer's derivation as a single dense input, set it aside, and
re-derived from `Rebuild/model/core.py` and from first principles of
the equicorrelated reduction. The underlying mathematics is the same
because the mathematics is determined by the model (there is one
correct reduction of an equicorrelated orthant probability and one
correct version of Slepian's inequality); the differences from the
reviewer's derivation are exactly the differences mandated by the
constructive voice:

- The reviewer organises around the *attack target* ("the §5.5
  sentence is false"); the rebuild organises around *positive model
  statements* (Statements A and B of §4.3 as the rebuilt model's
  claims).
- The reviewer's narrative pivot is "two competing channels →
  refutation of the uniform sign"; the rebuild's narrative pivot is
  "two competing channels → the rebuilt model's predictions are
  Statements A and B".
- Fresh equation labels (Eqs. 1.1–6.x) keyed to the rebuilt notation;
  fresh `Rebuild/model/` implementation pointers; fresh empirical
  envelope statements tied to the rebuild's own sim digests.
- Section ordering rearranged so §4 ends with "Statements A and B"
  rather than with "the paper's claim is false"; §5 is positive
  realisation rather than attack adjudication; §6 is scope rather
  than verdict implication.

The mathematics in §2 and §3 must agree with the reviewer's
derivation (any other derivation would be wrong); the wrapper —
voice, framing, target — is the rebuild's own.
