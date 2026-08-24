---
type: conversation
agent: constructive-rebuilder
prompt_version: 0.2
run_id: rb-023-2026-05-26
started: 2026-05-26T00:30:00Z
ended: 2026-05-26T01:30:00Z
worked_on: RB-026
output_kind: derivation
claims_touched: [C2, A1]
artifacts_written:
  - Rebuild/derivations/C2--non-monotonic-vda-rho.md
  - Rebuild/derivations/verify_C2_rho/verify.py
  - Rebuild/derivations/verify_C2_rho/output.json
  - Rebuild/CLAIM_LEDGER.md (top reconcile + C2 row)
  - Rebuild/REBUILD_BACKLOG.md (RB-026 done + RB-038, RB-039, RB-040 spawned)
  - Rebuild/rebuilder_state.json (runs_completed → 23)
  - Rebuild/BUILD_LOG.md (rb-023 entry)
papers_added: []
spawned_tasks: [RB-038, RB-039, RB-040]
---

# rb-023 — C2 r†(v;ρ) closed-form derivation

## What I built

`Rebuild/derivations/C2--non-monotonic-vda-rho.md` (~36 KB, 7 sections +
Verification + Extensions) — an independent re-derivation of the C2
escape threshold $r^{\dagger}(v)$ in the rebuild's voice at $\rho = 0$
(Proposition 2.1), then extended to $\rho > 0$ (Proposition 4.1) using the
same one-factor Gauss–Hermite quadrature that
`Rebuild/model/core.py:p_no_fa_grid` already uses for the equicorrelated
no-FA orthant probability. The ρ-aware closed form is the boxed Eq. 4.1

$$
  r^{\dagger}(v; \rho)
  \;=\;
  \frac{K_u(v; \rho)}{(N - 1)\,K_c(v; \rho)},
$$

with $K_c, K_u$ defined in Eqs. 3.8–3.9 in terms of the **asymmetric P3
criterion optimum** $(c^{\star}_c(\rho), c^{\star}_u(\rho))$ at $\alpha = 1/N$
and the ρ-aware $d$-gradient integrals $I_c, I_u$ from Eqs. 3.4–3.5.

The companion verification script `verify_C2_rho/verify.py` is
deterministic and produces `output.json` with sha256
`ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`.

## How it connects to the ledger

- **C2 row.** Discharges the `closed-form r†(v;ρ) derivation pending`
  license; the rebuilt-strength column now includes the ρ-aware
  Proposition 4.1, the structural ρ→0 collapse, the 5/5 drift-sign
  match with rb-006 empirical $\Delta r^{\star}$, and the 6/6
  boundary-FD sign-flip. Live label CONFIRMED-UNDER-ATTACK unchanged.
- **A1 row.** No formal label change, but the row's
  `Rebuild/derivations/A1--rho-channel.md` §4.2 channel (b)
  (concentration-cost relaxation) now has an analytic substrate — the
  closed-form $r^{\dagger}(v;\rho)$ predicts where the escape band's
  lower edge drifts in $\rho$. Live label CONTESTED unchanged.

## Simulation evidence

- `Rebuild/derivations/verify_C2_rho/output.json` (sha256 `ddbd3988…`,
  deterministic; reruns produce byte-identical bytes).
- **§5.1 ρ=0 recovery:** max\|Δ\| = 4.9 × 10⁻⁴ across $v \in \{1,2,3,5,8,10\}$
  (binary at v=2). Residual is `C_GRID Δc=0.05` quantisation of
  $(c^{\star}_c, c^{\star}_u)$ on the rebuilt model's criterion grid —
  *not* a formula discrepancy.
- **§5.2 Drift prediction:** $\Delta r^{\dagger}(v) > 0$ at *every* $v$
  (+3.0% at v=1 → +29.7% at v=8). All 5/5 closed-form drift signs match
  rb-006 empirical $\Delta r^{\star}$ signs at $v \in \{2,3,5,8,10\}$.
- **§5.3 Boundary FD sign-flip:** 6/6 confirmed at $(v, \rho) \in \{1,2,3\} \times \{0, 0.2\}$
  probes.

## What the manuscript can now say

At the C2-row strength ceiling:

> The escape threshold $r^{\dagger}(v;\rho)$ admits the closed form
> Eq. 4.1; the lower edge of the VDA-positive band drifts upward in
> $\rho$ at every $v$ in the empirical envelope, predicted by the
> closed form and confirmed at all 5/5 tested $v \ne 1$ in rb-006.

The manuscript's `Rebuild/manuscript/sections/results.tex` §results-c2
forward-reference paragraph (currently "deferred to the §appendix
derivation queued as RB-026") can now cite the derivation file directly.
The manuscript update is queued as **RB-038**.

## Next increment

The natural next priority is **RB-038** (manuscript fold-in of the
rb-023 closed form into §results-c2 or as a new §appendix-derivation-C2
subsection). Alternatives: **RB-025** (A1 cell-wise sign-flip sim, the
empirical companion to this analytic statement; medium priority, prereq
RB-005 done); **RB-021** (A8 N-dim uncued sweep, completing the
heterogeneity thread; low priority, prereq RB-017 done); **RB-033** (A3
formal derivation; low priority, prereq RB-019 done).

## Wiki cross-references

Sweep keywords: {asymmetric P3 criterion, escape threshold,
equicorrelated d-gradient, one-factor Gauss–Hermite, boundary FOC,
criterion liberality, concentration cost relaxation, ρ-aware closed
form}.

- `[[cohen_maunsell2009_correlations]]` — empirical anchor for the
  $\rho \in [0, 0.4]$ envelope (cited §6, already wired).
- `[[ruff_cohen2016_cross_area_correlations]]` — sign-dependent
  correlation structure motivating equicorrelation specificity (cited
  §6, already wired).
- `[[srinath2021_attention_information_flow]]` — supra-pairwise
  amplification (cited §6, already wired).
- Slepian 1962 / Tong 1990 — math-methods gap, cited by full
  bibliographic reference; research_db stubs deferred per reviewer
  CR-035/CR-037 scope (inherited from rb-008/rb-014/rb-017/rb-018).

No new research_db/papers/ stubs added; `audit.py` not re-run (no wiki
writes).

## Process notes

- The reviewer's `r_dagger()` (rb-006 `run.py` L218–265) uses the
  **asymmetric** P3 criterion optimum (c_c ≠ c_u in general because
  $V v \ne 1 - V$); my first pass used the symmetric criterion (c_c =
  c_u), which gave a ~60% discrepancy in the ρ=0 recovery. After
  switching to the asymmetric P3 optimum (Eq. 1.4 of the derivation),
  recovery collapsed to max\|Δ\| = 4.9 × 10⁻⁴ — the C_GRID-quantisation
  noise floor at the chosen grid resolution. The lesson is logged in
  §1.2 of the derivation (the asymmetric booking) so a future reader
  can see why the symmetric ansatz is wrong from the outset.
- The closed-form $r^{\dagger}(v;\rho)$ predicts the *escape-band lower
  edge*, not the *peak location*. The peak drift $\Delta r^{\star}$ is
  larger in magnitude than the closed-form $\Delta r^{\dagger}$ (e.g.
  +0.13 vs +0.005 at v=2), but the *sign* matches at all 5/5 tested $v$
  — the closed form is the right qualitative predictor even though a
  full peak-location closed form would need to additionally model
  $\alpha^{\star}_{\mathrm P_1}$ above escape. The scope §6 makes this
  explicit; RB-039 is the natural follow-up if a tighter peak predictor
  is wanted.
- Verification script reuses the rebuilt model's `_GH_Z, _GH_W`,
  `p_no_fa_grid`, `d_prime_asym`, `optimal_R` byte-for-byte, so the
  $\rho$-aware $I_c, I_u$ integrals are computed by the same quadrature
  the model uses for the orthant probability itself. This is the
  recovery-contract globality discussed in
  `Rebuild/derivations/A1--rho-channel.md` §6.
