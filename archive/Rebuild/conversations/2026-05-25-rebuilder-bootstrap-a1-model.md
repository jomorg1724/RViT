---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: 185e9941-2790-436e-958e-cb8470f17548
started: 2026-05-25T00:00:00Z
ended: 2026-05-25T00:00:00Z
worked_on: RB-001
output_kind: model
claims_touched: [A1, C5]
artifacts_written:
  - Rebuild/README.md
  - Rebuild/CLAIM_LEDGER.md
  - Rebuild/REBUILD_BACKLOG.md
  - Rebuild/BUILD_LOG.md
  - Rebuild/rebuilder_state.json
  - Rebuild/model/core.py
  - Rebuild/model/__init__.py
  - Rebuild/model/README.md
  - Rebuild/model/tests/test_recovery.py
  - Rebuild/model/tests/recovery_output.json
papers_added: []
spawned_tasks: []
---

# Bootstrap + A1 decorrelation channel (model increment)

This is the first run of the constructive rebuilder agent. The mission
file (`agents/paper_rebuilder_prompt.md` v0.2) prescribes the
bootstrap: create the `Rebuild/` skeleton, write the claim ledger,
seed the backlog, then execute the **A1 decorrelation channel** as the
first real increment (mission §9.6 default).

## What I built

A library, not a script. The reviewer's CR-052 replication
(`Critique/replications/A1--correlated-fa/run.py`, run-017) already
validates the equicorrelated-Gaussian extension byte-for-byte against
the inherited paper's headline numbers — that work is done, the
verdict ledger licenses it, and re-deriving it from scratch would
violate the simulation mandate's reuse rule (§5.2). What was missing
was the *packaged module* the rebuilt manuscript's downstream sims,
derivations, and figures will share. RB-001 produced that:

- `model/core.py` — model primitives (Phi, transfer family, beta/gamma,
  d_prime_asym, P_no_fa(rho) on the (c_c, c_u) grid, optimal_R,
  floor_R, P1–P4 policies, VDA, CF) lifted with attribution from the
  reviewer's run.py and the upstream C1/C5 replications.
- `model/__init__.py` — public surface: `HeadlineCell`, `policies`,
  `vda_curve`, `slepian_curve`, plus all primitives.
- `model/tests/test_recovery.py` — the contract every future extension
  must satisfy: rho->0 reproduces the inherited model exactly.
- `model/tests/recovery_output.json` — the test's numerical output +
  sha256 digest.

The rebuild's spine: every later increment (RB-002 sim, RB-003
derivation, RB-004 manuscript) imports from this module rather than
copying primitives into a new directory.

## How it connects to the ledger

A1 is live-labelled **CONTESTED** (`Critique/verdicts/A1--independence.md`,
v0.2, 2026-05-25). The reviewer's attack succeeded by re-deriving
P_no-fa under the equicorrelated-Gaussian model and re-optimising
criteria + alpha: dVDA/drho flips sign at r ~ 0.5, so the §5.5 "upper
bound on VDA" self-characterisation fails as a uniform statement.
Independence instead upper-bounds the criterion fraction.

RB-001 discharges the *model-level* response: the rebuilt model carries
rho as a first-class parameter and the inherited model is the rho=0
limit. The rebuilt strength now licensed (per `CLAIM_LEDGER.md` A1
row): *"Three levers, not two — criterion + sensitivity + decorrelation.
§5.5 'upper bound on VDA' retracted; what independence actually
upper-bounds is the criterion fraction."* No claim about the
*behaviour* of rho > 0 is yet licensed — that requires the simulation
(RB-002).

Coincidentally the recovery test also exercises C5 (symmetric recovery
at r = 1): the policy-level recovery check at `r = 1.0` lands at
VDA = 0.03983, CF = 0.72823, matching the reviewer's reference to
floating-point identity. So the recovery framework that RB-001
introduces is the same framework C5's appendix consistency result
(RB-013) will reuse.

## Simulation evidence

Recovery test: 7/7 PASS. Run with Python 3.13.x, numpy 2.4.4, scipy
1.17.1 (Phi backend = `scipy.special.ndtr`). nq = 64 Gauss–Hermite.

| check | result |
| --- | --- |
| `p_no_fa(rho=0)` == product (binary) | PASS (max\|diff\| = 0) |
| `p_no_fa(rho->0)` -> product, O(rho) scaling | PASS (3.56e-7 @ rho=1e-6, scales 10x with rho) |
| policy recovery @ r=0.398 | PASS (VDA d=+0.0e+00, CF d=+0.0e+00) |
| policy recovery @ r=1.0   | PASS (VDA d=+0.0e+00, CF d=+0.0e+00) |
| policy recovery @ r=3.162 | PASS (VDA d=+0.0e+00, CF d=+0.0e+00) |
| peak VDA(r) @ rho=0 ~ 0.0799 at r ~ 0.383 | PASS (0.07986 @ r=0.3831) |
| Slepian: P_no-fa(rho) monotone-up, rho=0 is minimum | PASS |

Determinism check: byte-identical sha256 on re-run.

**Output sha256:** `d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f`
**Artifact:** `Rebuild/model/tests/recovery_output.json`

No figure produced by RB-001 — recovery tests are textual contracts,
not manuscript figures. The first figures land in RB-002.

## What the manuscript can now say

Model section (RB-004, blocked on RB-002 + RB-003) may state, citing
RB-001:

> The rebuilt model promotes the per-location SDT independence
> assumption (A1) to a tunable equicorrelation parameter rho in [0,1).
> Because the change-trial reward term is linear in marginal hit
> rates, A1 enters the reward in exactly one place: the joint
> no-false-alarm probability on a no-change trial. We replace the
> inherited product Phi(b_c) Phi(b_u)^(N-1) with the exact
> equicorrelated-Gaussian orthant probability evaluated by 1-D
> Gauss–Hermite quadrature. The inherited paper's reward is recovered
> exactly as the rho = 0 case (Appendix A, Recovery Theorem).

Nothing yet may be said about *what changes* as rho rises. Manuscript
content concerning the sign-flip of `dVDA/drho`, the benefit-dominant
amplification, or the inversion of the CF upper bound waits for
RB-002.

## Next increment

**RB-002** — the A1 VDA(r, rho) and CF(rho) simulation, mirroring the
reviewer's run-017 surfaces but driven from `Rebuild/model/`. Produces
two figures (VDA(r) family-of-curves; CF(rho) at three r values) plus
the C2-cell numeric digest. Dependency order is then RB-003
(derivation) -> RB-004 (manuscript model section).

The mission's natural ordering (model -> sim -> derivation -> manuscript)
makes RB-002 the highest-priority unblocked task. Estimated wall-clock
~5 min reusing `model.vda_curve` and `model.policies`.

## Wiki cross-references (§11 sweep)

No new wiki stubs added this run. No manuscript section drafted, so
the mechanism-keyword sweep is deferred to the run that drafts the
section (RB-004 and onward). All references touched are inherited
through the reviewer's verdict files, which already cite them:

- `papers/cohen_maunsell2009_correlations` — empirical r_SC ~ 0.2
  range the rho channel is calibrated against.
- `papers/ruff_cohen2016_cross_area_correlations` — sign-dependent
  Sigma structure (within-down / between-up).
- `papers/srinath2021_attention_information_flow` — supra-pairwise
  shared-variance component caps an equicorrelation patch.
- `papers/hawkins1990_attention_detectability` — per-location SDT
  behavioural convention; anchors why A1 returns CONTESTED, not
  REFUTED.
- `papers/muller_findlay1987_sensitivity_criterion` — CF decomposition
  grounding.
- `papers/luo_maunsell2018_criterion_sensitivity` — dissociable
  criterion / sensitivity substrates.
- `papers/ernst_banks2002_cue_combination` — optimal-pooling-under-
  correlated-noise theory; ties Booking 2 to A6.

These will be cited explicitly in RB-003 (derivation) and RB-004
(manuscript), where the §11 sweep is required.

## Notes / Open

- **A6 ledger drift** (mission §3 → live): mission says
  "OPEN/in-progress at authoring", live verdict reads
  WEAKLY-SUPPORTED. Direction unchanged (pre-CONTESTED); the rebuilt
  strength for A6 is unchanged. Flagged `proposed_mission_change: true`
  in `CLAIM_LEDGER.md`. RB-016/RB-020 remain `blocked` waiting for a
  decisive label.
- **Compute environment.** `python3` resolves to 3.14 on the user's
  Mac, which has no numpy installed; `python3.13` and `python3.12`
  do. The recovery test uses absolute-path-friendly logic and works
  with either. Recorded in `model/README.md`.
- **No `--no-verify`, no `mv`, no `rm -rf`.** Override-resistant
  rules (§1, §10) honoured.
