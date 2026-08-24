---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.1
run_id: bootstrap-001
started: 2026-05-17T12:00:00Z
ended: 2026-05-17T12:30:00Z
worked_on: C2
attack_vector: re-derivation
verdict_touched: C2--non-monotonic-vda
verdict_after: WEAKLY-SUPPORTED
papers_read:
  - luo_maunsell2018_criterion_sensitivity
  - reynolds_heeger2009_normalization
papers_added: []
spawned_tasks:
  - CR-013
  - CR-014
  - CR-015
  - CR-016
---

# Bootstrap run: re-derive non-monotonic VDA (C2)

## What I attacked

**Claim C2** (mission §2.6; paper §4.3): "VDA benefit is non-monotonic
in $r$, peaking near $r \approx 0.3$ in the cost-dominant regime, and
approaching $0$ at both extremes." The reference regime is the paper's
Figure 4 setting: $N=4$, $d'_{\max}=2.0$, $f_0=0.5$, $h(a)=\sqrt{a}$,
$V=0.5$, $v=5$, Variant A.

This was the first task in the bootstrap backlog (CR-001), seeded as
the default per mission §8.6: C2 is the paper's most distinctive
finding, so confirming or breaking it sets the tone for the whole
critique. Re-derivation was chosen over replication because the math
is tractable enough to surface skipped steps that a black-box
replication would miss.

## How I attacked it

Two-step re-derivation attack:

1. **Symbolic re-derivation** of the model in mission §2.4–§2.5, then
   a two-limit theorem: I showed analytically that $\mathrm{VDA}(r)
   \to 0$ in both the $r \to 0^+$ and $r \to \infty$ limits, with
   strict positivity on an interior interval. The mechanism: distinct
   escape thresholds $r^\dagger(v) < r^\dagger(1)$ for P1 vs P2 (the
   value-blind baseline), with the VDA gap being the interval over
   which P1 has escaped uniform attention but P2 has not. The
   closed-form escape threshold (derivation Eq. (2.5)):
   $r^\dagger(v) = G_u / [(N-1) G_c(v)]$, where $G_c, G_u$ are
   $v$-dependent and $v$-independent reward-density factors at
   uniform attention.

2. **Numerical corroboration** via a minimal Python implementation of
   P1/P2/P3/P4 on the paper's $r$-grid. Scipy was unavailable in the
   sandbox (disk full), so I hand-rolled $\Phi$ via `math.erf`. Grid
   resolution $\Delta\alpha=0.01$, $\Delta c = 0.05$ — coarser by 2×
   in $\alpha$ than the paper.

## What I found

The re-derivation **succeeds** — the model's definitions force
non-monotonicity. The numerical sweep corroborates:

| $r$ | $\alpha^\star_{\mathrm{P1}}$ | $\alpha^\star_{\mathrm{P2}}$ | VDA |
|---:|---:|---:|---:|
| 0.10 | 0.95 | **0.25 = 1/N** | 0.0155 |
| 0.32 | 0.99 | **0.25 = 1/N** | 0.0737 |
| 0.40 | 0.99 | 0.32 | **0.0774 (peak)** |
| 1.00 | 1.00 | 0.75 | 0.0395 |
| 10.0 | 1.00 | 0.99 | 0.0019 |

The agent's peak ($r = 0.398$, VDA $= 0.0774$) is one log-grid step
to the right of the paper's reported $r \approx 0.3$, VDA $\approx
0.080$; the gap is sub-grid-resolution at $\Delta\alpha=0.01$. The
qualitative non-monotonicity, the asymptotic decline to $\sim 0$ at
both extremes, and the saturation of $\alpha^\star_{\mathrm{P2}}$ to
exactly $1/N$ on a finite cost-dominant interval — all are
quantitatively confirmed.

The derivation surfaces **one expository gap** in the paper: §4.3
gives the right narrative ("squeeze from two directions") but does
not derive the existence of two distinct escape thresholds or
provide the closed form (2.5). A future revision could strengthen
the paper's exposition by including this — it converts the empirical
"VDA peaks at $r \approx 0.3$" into the analytic "VDA is positive
exactly on $(r^\dagger(v), \infty)$ with peak controlled by [closed-
form expression]." Not an error, but a missed opportunity.

## Verdict movement

**Before this run:** no verdict file existed.

**After this run:** `Critique/verdicts/C2--non-monotonic-vda.md`
exists at label **WEAKLY-SUPPORTED**.

Per mission §3.1, a single successful attack vector does not
justify CONFIRMED-UNDER-ATTACK; that requires $\geq 2$ distinct
attack vectors across separate runs. This run executed one
(re-derivation). A second attack vector — either a high-resolution
replication of Figure 4 or a sensitivity probe predicted by
derivation Eq. (2.5) — would, if it also fails to falsify, justify
elevation to CONFIRMED-UNDER-ATTACK.

## Next-attack recommendation

**Spawn CR-013 (replication-attack on C2):** Reproduce Figure 4
numerically at the paper's grid resolution $\Delta\alpha = 0.005$,
across the full $v \in \{1,2,3,4,5\}$ envelope. The agent's current
peak at $r=0.398$ versus the paper's $r \approx 0.3$ should resolve
to either match (paper $\rightarrow$ CONFIRMED-UNDER-ATTACK) or
shift (forces verdict-revisit). This is the natural next attack
because (a) the re-derivation has already paid down the analytic
cost so a focussed replication is high-information-per-unit-time,
(b) sub-grid disagreement in the agent's pilot is precisely the
ambiguity a replication resolves.

**Also spawn CR-014 (sensitivity-attack on C2):** Use derivation
Eq. (2.5) to predict how the peak location $r^\star$ depends on
$f_0, N$, and the choice of $h$. Compare to the paper's Figure 6
(robustness to $f_0$, $h$, $N$). If the closed-form prediction
matches the empirical pattern, the C2 verdict can elevate to
CONFIRMED-UNDER-ATTACK after one more vector. If it disagrees
(e.g. peak shifts with $h$ in a way the closed form does not
predict), the analytic skeleton has a missing piece — a more
informative finding than further confirmation.

## Wiki cross-references

Mission §11 sweep over the §11.1 keyword anchors. Per-entry
adjudication is in `Critique/verdicts/C2--non-monotonic-vda.md`
under `### Wiki cross-references`. Headlines:

- `[[luo_maunsell2018_criterion_sensitivity]]` — **cited inline**.
  Provides direct empirical support for the criterion/sensitivity
  dissociation that underlies the paper's "independent benefit
  and cost" conceptual move. LPFC neurons modulate with both
  components in distinguishable patterns, supporting the claim
  that benefit and cost can be independently parameterised.
- `[[reynolds_heeger2009_normalization]]` — **cited inline**. The
  paper's $\beta/\gamma$ split operationalises the normalization
  model's separable excitatory ($G_E$) and suppressive ($G_S$)
  gains. Strong theoretical scaffold for the model's premise.
- `[[mcadams_maunsell1999_reliability]]` — **cited inline**.
  β-side empirical substrate (multiplicative sensitivity gain).
- `[[maunsell2015_attention_mechanisms]]` — **spawned CR-015**:
  next-run literature pull for A2 (single global $r$ assumption).
- `[[cohen_maunsell2009_correlations]]`, `[[srinath2021_attention_information_flow]]`
  — flagged for CR-006 (A1 attack) and CR-007 (A2 attack).
- `[[hickey2010_reward_salience_acc]]`, `[[failing_theeuwes2018_selection_history]]`,
  `[[bhatnagar2022_attention_choice_metaanalysis]]` — relevant to
  whether VDA is empirically observed (C3 attack, CR-003), not to
  the non-monotonicity shape of C2.
- Searched terms returning no relevant hits this run: *priority
  map LIP*, *FEF microstimulation*, *saccade*. (These would bear
  on the brain's circuit-level value-attention machinery but not
  on the specific non-monotonicity-in-$r$ claim.)

The agent observed that no wiki entry exists for
`maunsell_treue2006` (the canonical feature-vs-spatial attention
dissociation review). Spawned CR-016 to consider adding a stub if
the literature for A2 (CR-007) calls for it.
