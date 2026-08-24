---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-011
started: 2026-05-24T01:16:30Z
ended: 2026-05-24T01:55:00Z
worked_on: A3
attack_vector: replication
verdict_touched: A3--multiplicative-conservation
verdict_after: CONTESTED
papers_read:
  - muller_findlay1987_sensitivity_criterion
  - reynolds_chelazzi2004_attentional_modulation
  - luo_maunsell2018_criterion_sensitivity
  - sridharan2017_sc_sensitivity_bias
  - reynolds_heeger2009_normalization
  - maunsell2015_attention_mechanisms
  - coalition_resource_competition
papers_added: []
spawned_tasks: [CR-044]
---

# A3 second vector: criterion dominance is not robust to the conservation rule as a per-cell claim

## What I attacked

Assumption **A3** (mission §2.7; paper §5.5, p.8): the benefit/cost asymmetry
obeys the *additive* conservation rule $\beta+\gamma=2$. The paper names the
*multiplicative* alternative $\beta\gamma=1$ and asserts that swapping it in
"could yield quantitatively different results, though the qualitative
findings—non-monotonic VDA, no inversion, **criterion dominance**—should be
robust." CR-040 (run-010, re-derivation) confirmed the first two findings and
found criterion dominance *eroding* to a thin margin on the V=0.5, v=5 reference
slice (CF floor 0.601→0.507), leaving A3 at WEAKLY-SUPPORTED with one flagged
risk: C1 is *already* CONTESTED under additive (run-003 found CF as low as 0.304
in the low-V/high-v/variant-B corner), and since $\beta\gamma=1$ lowers CF
wherever $R(P1)$ grows, those cells might push CF below 0.5. I attacked exactly
that question, as the designated second vector (CR-008).

## How I attacked it

**Replication** (mission §3.2). I took the **590 cells** of the paper's
4,410-cell primary grid where run-003's C1 sweep found additive CF $<0.60$ (the
at-risk set), recomputed the additive CF (cross-check) and computed the
multiplicative CF ($\beta=\sqrt r$, $\gamma=1/\sqrt r$) on each, at run-003's
*exact* configuration ($N=4$, $d'_{\max}=2$, $f_0=0.5$, $\sqrt\cdot$; A&S Φ;
$\Delta c=0.05$; $\Delta\alpha=0.02\cup\{1/N\}$). Code:
`Critique/replications/A3--multiplicative-conservation/cr008_cf_floor/cr008_run.py`,
reusing the `beta_gamma_multiplicative` map from the run-010 parent script
(asserted bit-identical). A cheap full 4,410-cell multiplicative sweep gave the
global statistics. The literal CR-008 rule ("any CF_mult<0.5 → CONTESTED") I
refined, because 177 of the at-risk cells *already* have additive CF<0.5
(C1's contested corner): the constraint-attributable signal is **new flips**
(CF_add≥0.5 → CF_mult<0.5), not the blunt count.

## What I found

Validation first: the local $\beta\gamma=1$ map equals the parent's (dev 0.0);
the recomputed additive CF reproduces run-003's stored CF **bit-for-bit** over
all 590 cells (max$|\Delta|=0.0$); $R(P3),R(P4)$ are family-independent
(max$|\Delta|=0.0$); an independent from-scratch recompute of the worst cell
gave $\text{CF}_\times=0.2309$, $\text{CF}_+=0.3040$; the run is deterministic.

The result:

| quantity | additive $\beta+\gamma=2$ | multiplicative $\beta\gamma=1$ |
|---|---|---|
| criterion-subordinate cells (CF$<0.5$), full grid | 177 / 4410 (**4.01 %**) | 368 / 4410 (**8.34 %**) |
| median CF, full grid | 0.7605 | 0.7578 |
| min CF (at $r{=}10,V{=}0.25,v{=}4$,B) | 0.3040 | 0.2309 |

**191 cells flip** from criterion-dominant (CF$\ge0.5$) to criterion-subordinate
(CF$<0.5$) purely because of the constraint swap; **0 recover** ($\Delta\text{CF}
\in[-0.109,0.000]$, max exactly $0$ — $\beta\gamma=1$ never *raises* CF). So the
criterion-subordinate region **roughly doubles**. But the **median CF is
essentially unchanged** (0.7605→0.7578): the bulk of the space stays strongly
criterion-dominant, and the new failures sit in the **benefit-dominant high-$r$
corner** ($r\gtrsim2.5$) — the same region C1 already contested under additive,
now deepened and widened, not relocated. The VDA peak (C2) lives at low $r$ and
is untouched.

## Verdict movement

**A3 WEAKLY-SUPPORTED → CONTESTED.** A credible attack succeeded against the
*criterion-dominance* conjunct of §5.5, specifically the §4.1 wording
"criterion adjustment is **always** the single largest contributor": under
$\beta\gamma=1$ it is *not* the larger contributor in roughly twice as many of
the paper's own cells. Because the flips are *inside* the paper's stated scope,
this cannot be CONFIRMED-CONDITIONAL; because the substance survives as a
central-tendency statement (median CF $\approx0.76$, $\approx92\%$ of cells
criterion-dominant under both rules) and the failures stay in the
already-flagged corner, it is not REFUTED. The pattern mirrors C1 and C3: a
per-cell/categorical wording is too strong, the bulk finding survives, a weaker
reformulation is proposed (report criterion dominance as *typically* not
*always* the larger contributor, and note its boundary depends on the
conservation form). The sharpening matters because divisive normalization makes
$\beta\gamma=1$ the *more* biologically apt rule, so the eroded boundary is not
a corner curiosity. The two A3 vectors (CR-040 re-derivation, CR-008
replication) now agree on direction; the replication's grid-wide reach is what
turns the v0.1 "flagged risk" into a settled CONTESTED.

## Next-attack recommendation

**CR-042** (already queued, sensitivity): does the doubling-of-failures pattern
persist across the $f_0$ and $h$ secondary sweeps, or is it specific to the
$f_0=0.5,\sqrt\cdot$ reference config? Lower $f_0$ raises the reallocation gain
($f'(1/N)$ grows), so $\beta\gamma=1$ may erode CF *further* at low $f_0$ —
either strengthening the CONTESTED or revealing the additive reference grid is
the benign case. This is the highest-leverage A3 follow-up. Newly spawned
**CR-044** (low) is the Δα=0.005 grid-robustness spot-check on the borderline
flips. With A3 now CONTESTED on two vectors, the broader frontier shifts to the
untouched assumptions — **CR-036** (A8 heterogeneous-uncued, de-risked substrate)
and **CR-006/CR-007** (A1 independence / A2 single global $r$).

## Wiki cross-references

(Full block in the verdict file v0.2.)

- `[[muller_findlay1987_sensitivity_criterion]]` — cited (new): behavioural
  sensitivity-vs-criterion dissociation; the empirical grounding of the CF
  decomposition. Surfaced by this run's §11 sweep; absent from v0.1.
- `[[reynolds_chelazzi2004_attentional_modulation]]` — cited (new): carries the
  `divisive-normalization` concept; reinforces $\beta\gamma=1$ as the
  mechanism-aligned rule.
- `[[reynolds_heeger2009_normalization]]` — cited (carried): divisive =
  multiplicative normalization, the biological-aptness point.
- `[[luo_maunsell2018_criterion_sensitivity]]`, `[[sridharan2017_sc_sensitivity_bias]]`,
  `[[maunsell2015_attention_mechanisms]]` — cited: SDT criterion/sensitivity
  substrate behind the CF metric.
- `[[coalition_resource_competition]]` (concept) — cited: the
  finite-resource-conservation framing and the PRISM implication.
- §11.1 anchors dopamine/RPE/LIP/FEF/SC/saccade/priority-map — consulted,
  unrelated on inspection (value *source/where*, not conservation *form*),
  consistent with v0.1. No new stub added; no floating-point /
  conservation-comparison literature in the wiki (expected gap).
