---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.1
run_id: run-002
started: 2026-05-17T13:30:00Z
ended: 2026-05-17T14:30:00Z
worked_on: C2
attack_vector: sensitivity
verdict_touched: C2--non-monotonic-vda
verdict_after: CONFIRMED-UNDER-ATTACK
papers_read:
  - muller_findlay1987_sensitivity_criterion
  - hawkins1990_attention_detectability
  - lu_dosher1998_external_noise
  - solomon2004_cues_sensitivity
papers_added: []
spawned_tasks:
  - CR-017
  - CR-018
  - CR-019
---

# C2 sensitivity probe — closed-form $r^\dagger(v)$ vs Figure 6

## What I attacked

**C2** (mission §2.6, paper §4.3): *VDA benefit is non-monotonic in
$r$, peaking near $r \approx 0.3$ in the cost-dominant regime, and
approaching $0$ at both extremes.* Specifically the paper's
**secondary-sweep narrative** in §4.6 / Figure 6: how the peak
location and magnitude of $\mathrm{VDA}(r)$ shift as the baseline
sensitivity $f_0$, transfer-function family $h$, and set size $N$
vary across the values $\{0.1, 0.3, 0.5, 0.7\} \times \{a, \sqrt{a},
a^{0.3}, a^2\} \times \{2, 4\}$.

## How I attacked it

**Sensitivity probe** (mission §3.2). The CR-001 re-derivation
produced a closed-form *escape threshold*

$$
r^\dagger(v) \;=\; G_u(V, N, c_c^\star, c_u^\star) \,\bigm/\, \bigl[(N-1)\,G_c(v, V, N, c_c^\star, c_u^\star)\bigr]
$$

where $G_c, G_u$ are the partial derivatives of $E[R]$ w.r.t.
$d'_c, d'_u$ at $\alpha = 1/N, d_c = d_u = d'_{\text{base}}$. The
threshold defines the **lower edge** of the non-zero VDA interval
$(r^\dagger(v), \infty)$. The peak of $\mathrm{VDA}(r)$ lives in
$(r^\dagger(v), r^\dagger(1))$, so the *direction* in which the peak
shifts under a parameter change is the direction in which both
$r^\dagger(v=5)$ and $r^\dagger(v=1)$ shift.

I implemented the closed-form expressions in
`Critique/replications/C2--non-monotonic-vda/sensitivity/run.py` and
swept the paper's secondary-sweep parameter triplets, comparing
closed-form direction predictions against an empirical $\mathrm{VDA}(r)$
sweep at each combination. The empirical sweep used an extended
log-$r$ grid $[10^{-2}, 10^1]$ at 31 points (the paper's primary
grid is $[10^{-1}, 10^1]$ at 21 points; extension was needed
because the closed-form predicts $r^\dagger(v=5) < 0.02$ for
$f_0 = 0.1$ and $h = a^2$).

## What I found

**Direction-of-shift summary:**

| sweep | $r^\dagger(v=5)$ | $r^\star_{\text{emp}}$ | paper §4.6 claim | match |
|-------|-----------------:|-----------------------:|-----------------|------:|
| $f_0 \in \{0.1, 0.3, 0.5, 0.7\}$ | 0.014, 0.028, 0.050, 0.066 | 0.10, 0.25, 0.40, 0.50 | peak ↓ in $r$ as $f_0$ ↓ | ✓ |
| $h \in \{a, \sqrt{a}, a^{0.3}, a^2\}$ | log-width 1.02, 0.83, **0.76**, **1.27** | peak VDA 0.082, 0.080, 0.043, 0.025 | $a^{0.3}$ compresses, $a^2$ stretches | ✓ |
| $N \in \{2, 4\}$ | 0.266, 0.050 | 5.01, 0.40 | "similar pattern, slightly ↑ VDA" | direction ✓; magnitude understated by paper |

**Three findings beyond direction matching:**

1. **The closed-form is exact in non-clamping regimes.** For $N=2,
   V=0.5$: closed-form $r^\dagger(v=5) = 0.2655$ and the empirical
   P1 escape (where $\alpha^\star_{\mathrm{P1}}$ first exceeds $1/N$
   in the sweep) lies in $r \in (0.251, 0.316)$. Closed-form
   $r^\dagger(v=1) = 1.0000$ and the empirical P2 escape lies in
   $r \in (1.000, 1.259)$. Both predictions hit within one
   log-grid step.

2. **The closed-form is a conservative upper bound in the clamping
   regime.** For $f_0 = 0.1$ and $h = a^2$ (extreme baseline-
   sensitivity / accelerating-returns), $\alpha^\star_{\mathrm{P1}}
   = 1.0$ at every $r$ in the swept range — well before the
   closed-form $r^\dagger(v=5)$. Mechanism: the $d'$ clamping
   ($d' \geq 0$, mission §2.4) bounds the cost of large-$\alpha$
   deviations, which the infinitesimal-deviation gradient cannot
   see. The non-monotonicity is *still empirically present* in
   the clamping regime; only the *prediction of the escape point*
   shifts.

3. **A subsidiary §4.6 wording weakens; C2 unaffected.** The
   paper writes "Lower $f_0$ shifts the peak VDA higher". My
   empirical peak VDA is non-monotonic in $f_0$ (max at
   $f_0 = 0.3$, not at $f_0 = 0.1$). Could be $\alpha$-grid
   resolution (paper uses 0.005, I use 0.01) — a candidate
   refinement task — or a real refinement to the paper's wording.

I also corrected a sign-transcription error from the CR-001
derivation §2.3: $G_c$ and $G_u$ are *sums* of two positive
contributions (the hit-rate term and the no-FA-survival term both
*raise* $E[R]$ as $d'_x$ rises), not differences. The minus sign
in the $\alpha$-gradient comes from the Jacobian $\partial d'_u/
\partial \alpha = -\gamma d'_{\max} f'(1/N)/(N-1)$. The derivation
verbal expansion was internally consistent at the gradient level
but ambiguous at the term level; the python implementation in
the bootstrap-001 era happened not to be exercised at this point
because the bootstrap replication uses full numerical optimisation
rather than the closed form.

## Verdict movement

**WEAKLY-SUPPORTED → CONFIRMED-UNDER-ATTACK.**

Two distinct attack vectors (re-derivation in bootstrap-001;
sensitivity probe here) have now failed to falsify C2. The
elevation is justified per mission §3.1 because the sensitivity
probe goes beyond mere "second attack" status — it shows that the
paper's three independent-looking §4.6 narrative claims (sensitivity
to $f_0$, sensitivity to $h$, sensitivity to $N$) are all
*derived* from one analytic expression, the closed-form
$r^\dagger(v)$ from CR-001.

The verdict is **not** uplifted with reservations: the closed-form
is not the *peak location* but the *lower edge of the non-zero
VDA interval*. The peak location depends on the rate at which
$\alpha^\star_{\mathrm{P2}}$ closes to $\alpha^\star_{\mathrm{P1}}$
above $r^\dagger(1)$, which the closed-form does not directly
constrain. So the elevation is *qualified* in the sense that
"C2's non-monotonicity is derived" (true) but "C2's specific peak
at $r \approx 0.3$ at the paper's primary regime is derived" (only
partially — the peak lives in an interval the closed-form
provides, but the peak itself is a numerical not analytic
prediction).

## Next-attack recommendation

The natural next move on C2 is **CR-013** (high-resolution Figure 4
replication at $\Delta\alpha = 0.005$). The motivation has weakened
since CR-014 — the qualitative-direction agreement is strong
enough that C2's verdict is now CONFIRMED-UNDER-ATTACK — but
CR-013 would still resolve the peak-location specificity
(currently the agent's grid puts the peak at $r = 0.398$ vs the
paper's $r \approx 0.3$).

The higher-value next moves are the spawned tasks:

- **CR-017** (re-derivation): extend $r^\dagger$ to the clamping
  regime, replacing the small-deviation gradient with a finite-
  deviation comparison at $\alpha = 1$. This would unify the
  non-clamping and clamping regimes under one analytic prediction.
- **CR-018** (literature): the $f_0$-VDA non-monotonicity I
  surfaced is a refinement to the paper's §4.6 wording — a
  literature attack on whether empirical low-baseline-sensitivity
  paradigms show the paper's predicted monotonic ↑VDA or the
  agent's non-monotonic pattern would feed §5.2's experimental-
  design recommendation.
- **CR-019** (verdict refinement on C4): the $V = 1/N$
  degeneracy at $N=2$ surfaced here should be noted when CR-004
  (C4 re-derivation) is taken on.

In §3.3-default ordering, the next pick is **CR-002** (C1
sensitivity attack on criterion-fraction floor), since it remains
the highest-priority unblocked seed task. CR-017 and CR-018 are
spawned at medium priority; CR-002 is high.

## Wiki cross-references

(See verdict file Version 0.2 "Wiki cross-references" sub-block for
the full sweep. Headline new engagements this run:)

- `[[muller_findlay1987_sensitivity_criterion]]` — cited as the
  foundational SDT dissociation underlying the policy
  decomposition.
- `[[hawkins1990_attention_detectability]]` — cited as the
  empirical evidence that attention modulates $d'$, supporting
  the $\beta$-channel.
- `[[lu_dosher1998_external_noise]]` — cited as the canonical
  signal-enhancement vs distractor-exclusion taxonomy that
  underlies the paper's $\beta/\gamma$ parameterisation.
- `[[solomon2004_cues_sensitivity]]` — flagged as bearing on A6
  (homogeneous decision rule) and A1 (independence), but not on
  C2 itself; not load-bearing for this verdict.

Per mission §11, no missing wiki entries that bore on the
direction-of-shift findings; the SDT/attention literature in
`research_db/papers/` was sufficient. No new stubs added this
run.
