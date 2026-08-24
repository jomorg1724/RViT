---
type: derivation
claim_id: A2
attack: re-derivation
interaction_with: A8
companion_verification: Critique/replications/A2xA8--heterogeneous-r/
prompt_version: 0.2
run_id: run-015
created: 2026-05-24
---

# A2×A8 — "Does within-display heterogeneous $r_i$ bias C1–C5?": re-derivation

> **Assumption under attack (paper §2.4, verbatim).** *"We parameterize the
> asymmetry between attentional benefit and cost with a ratio $r>0$. … The ratio
> $r$ reflects the relative efficacy of attentional enhancement versus
> suppression."* with $\beta(r)=2r/(r+1)$, $\gamma(r)=2/(r+1)$. The model uses a
> **single** $r$ for every location, feature, and the whole trial (A2). §5.5 names
> the limitation: *"real neural circuits may have location-specific,
> feature-specific, or time-varying asymmetries."*

The literature attack CR-007/run-014 settled the **premise**: a single global
$r$ is empirically false under the *within-display* reading R2 (the benefit:cost
asymmetry is location-/feature-/time-specific — `reynolds_heeger2009`,
`mcadams_maunsell1999_v4_tuning`, `treue_martinez_trujillo1999`, `sani2017`,
`carrasco2011`), while benign under the *between-preparation* reading R1 (the
100-fold $r$-sweep covers wherever a preparation lands, and C1–C5 are
$r$-indexed). It left A2 `WEAKLY-SUPPORTED` with the decisive **consequence**
question routed here: *under R2, does replacing the single $r$ with a
per-location vector $r_i$ shift any headline number C1–C5?*

This is a re-derivation of the **A2×A8 interaction**, because the obstacle is
geometric. CR-045/run-013 proved A8 (homogeneous-uncued allocation) is the
*optimum*, not merely the imposed choice — but that proof rests entirely on the
uncued slots being **exchangeable**, which (CR-045 §1) requires equal uncued
validity **and a single global $r$**. A per-location $r_i$ breaks exchangeability
even at equal validity. The question is whether the optimal allocation then
deviates from equal-split *enough to move a C1–C5 number*. Notation is mission §2
throughout; the C4 location-count machinery and the CR-045 §2–§4 apparatus are
reused. Numerical corroboration (independent grid computation) is in
`Critique/replications/A2xA8--heterogeneous-r/`.

---

## 0. Setup: the heterogeneous-$r$ model and what it breaks

Locations $i=0,\dots,N-1$, location $0$ cued, with **equal uncued validity** so
the value$\times$validity weights are $\omega_0=Vv$ (cued) and
$\omega_{i\ge1}=\omega_u:=\tfrac{1-V}{N-1}$ (every uncued). Promote the single
global $r$ to a **per-location vector** $\mathbf r=(r_0,\dots,r_{N-1})$, giving
$\beta_i=\beta(r_i)=\tfrac{2r_i}{r_i+1}$, $\gamma_i=\gamma(r_i)=\tfrac{2}{r_i+1}$.
The generalised per-location sensitivity (paper Eqs. (7)–(8) with $r\to r_i$;
note $d'_{\text{base}}=d'_{\max}f(1/N)$ is **$r$-independent**, so a per-location
$r_i$ rescales only that location's *departure*, never the common baseline):
$$
d'_i = \max\!\Big(d'_{\text{base}} + s_i\big[d'_{\max} f(a_i)-d'_{\text{base}}\big],\,0\Big),\qquad
s_i=\begin{cases}\beta_i & a_i\ge 1/N\\[2pt]\gamma_i & a_i< 1/N.\end{cases}
\tag{0.1}
$$
Reward (paper Eq. (9) generalised), criteria $c_i$ optimised:
$$
\mathcal V(a_1,\dots,a_{N-1}) := \max_{\mathbf c}\Big[\tfrac12\sum_i \omega_i\,\mathrm{HR}_i
+ \tfrac12\,\mathrm{CR}\textstyle\prod_i(1-\mathrm{FAR}_i)\Big],
\tag{0.2}
$$
on the uncued simplex $\Delta_B=\{(a_1,\dots,a_{N-1}):a_i\ge0,\ \sum a_i=B\}$ at
fixed cued allocation $a_0=\alpha$, $B=1-\alpha$. Equal split $\bar a:=B/(N-1)$.

**What breaks.** In CR-045 §1, $\mathcal V$ was a *symmetric* function of the
uncued allocations: permuting them permuted exchangeable locations (equal
$\omega_u$, equal value, **equal transfer function** $s$). With distinct
$r_i\Rightarrow$ distinct $s_i$, the slots have **distinct transfer functions**,
so $\mathcal V$ is *no longer symmetric* and the $S_{N-1}$ argument that forced
the equal-split gradient to vanish (and the Hessian to be a scalar) fails. We
must recompute the gradient and bound the deviation directly.

---

## 1. Proposition (a) — equal split is generically NOT a critical point

Fix $\alpha$ with $\bar a<1/N$ (the smooth $\gamma$-branch; the kink $\bar a=1/N$
is §3). Write $\Delta:=d'_{\text{base}}-d'_{\max}f(\bar a)>0$ (positive on the
loss branch), so at equal split
$$
d_i = d'_{\text{base}}-\gamma_i\,\Delta,\qquad
\frac{\partial d_i}{\partial a_i}\Big|_{\bar a}=\gamma_i\,\rho,\quad
\rho:=d'_{\max}(1-f_0)h'(\bar a)>0.
\tag{1.1}
$$
The **free partial** of $\mathcal V$ (envelope theorem: criteria at their optimum
$c_i^\star$), for an uncued slot $i$, is
$$
g_i:=\frac{\partial\mathcal V}{\partial a_i}\Big|_{\bar{\mathbf a}}
=\underbrace{\Big[\tfrac12\omega_u\,\mathrm{HR}_d(d_i,c_i^\star)
+\tfrac12\,\mathrm{CR}\,P_{-i}\,G_d(d_i,c_i^\star)\Big]}_{=:M_i\ (\text{marginal value of }d_i)}\cdot\;\gamma_i\,\rho,
\tag{1.2}
$$
with $\mathrm{HR}_d=\tfrac12\phi(d_i/2-c_i^\star)$,
$G_d=\tfrac12\phi(d_i/2+c_i^\star)$ (since $1-\mathrm{FAR}=\Phi(d/2+c)$), and
$P_{-i}=\prod_{j\ne i}(1-\mathrm{FAR}_j)$. Both the level $d_i$ (1.1) and the
optimal criterion $c_i^\star$ depend on $\gamma_i$, so **$g_i$ depends on slot $i$
only through $r_i$**. The tangent gradient on $\Delta_B$ is the projection onto
$\{\sum_i\delta_i=0\}$:
$$
g_i^{\,T}=g_i-\bar g,\qquad \bar g=\tfrac1{N-1}\textstyle\sum_{j\ge1} g_j .
\tag{1.3}
$$
If all $r_i$ are equal, all $g_i$ coincide and $g_i^{\,T}\equiv0$ — the CR-045
result. If the $r_i$ differ, $g_i^{\,T}\not\equiv0$ generically:
$$
\boxed{\;\text{equal split is a critical point of }\mathcal V\text{ on }\Delta_B
\iff g_i\ \text{constant in }i \iff r_i\ \text{constant in }i.\;}
\tag{1.4}
$$
To first order in the spread $\delta\gamma_i:=\gamma_i-\bar\gamma$, $g_i\approx
\bar g + g'(\bar\gamma)\,\delta\gamma_i$, so $g_i^{\,T}=O(\text{spread})$ — the
criticality defect is *linear* in the heterogeneity. **Direction:** $g_i$
increases with $\gamma_i$ (the steeper-recovery, more cost-dominant, *smaller*
$r_i$ slot has the larger marginal value of budget), so the optimum tilts budget
**toward the more cost-dominant uncued locations** — it recovers the slots that
lose the most $d'$ under deprivation.

**Numerical confirmation** (`verify_heterogeneous_r.py`, block (a); cell $V=0.5$,
$v=5$, variant A). At spread 0, $g=(0.39942,0.39942,0.39942)$ and the tangent
gradient is $(0,0,0)$ to machine precision. At ±30% ($r_i=0.28,0.40,0.52\Rightarrow
\gamma_i=1.562,1.429,1.316$), $g=(0.4568,0.39941,0.35566)$, tangent gradient
$(+0.053,-0.0045,-0.048)$, $\|g^T\|=7.2\times10^{-2}$ — nonzero, ordered as (1.2)
predicts ($g$ increases with $\gamma_i$, i.e. decreases with $r_i$).

So proposition (a) of CR-045 **fails** under heterogeneity: equal split is no
longer guaranteed optimal. The verdict therefore turns on the *magnitude* of the
resulting deviation — propositions (b) and (c).

---

## 2. Proposition (b) — the reward deviation is second-order in $\mathrm{var}(r_i)$

The optimal deviation from equal-split and the reward it buys are governed by the
tangent gradient (1.3) and the restricted Hessian $H_T:=\nabla^2_T\mathcal V$. Even
though $H_T$ is no longer the clean scalar $\lambda I$ of CR-045 §2 (the $S_{N-1}$
symmetry is broken), **it remains negative-definite on the smooth $\gamma$-branch
for concave/linear $h$**, by the same mechanism: the diagonal blocks carry the
per-slot $\lambda_{\mathrm{HR},i}+\lambda_{\mathrm{noFA},i}$, and the
correct-rejection term
$$
\lambda_{\mathrm{noFA},i}=Q_i\big[G_i^2 g_i'^2(\log G_i)''+G_iG_{d,i}g_i''\big]\le0
\quad\text{unconditionally for concave/linear }h,
\tag{2.1}
$$
because **$\Phi$ is log-concave** ($(\log G)''<0$) and $g_i''\le0$ — *exactly the
CR-045 §2.2 argument, applied per slot*. Heterogeneous $r_i$ changes the per-slot
slope $g_i'=\gamma_i\rho$ but not the sign of (2.1): the spreading force of the
no-false-alarm channel is **$r$-independent in sign**. (The off-diagonal coupling
enters only through the shared $P_{-i}$ factor and is $O(G_dG_d)$, subdominant.)
Hence $H_T\prec0$ and the constrained optimum is a small interior tilt
$$
\delta\mathbf a^\star \approx (-H_T)^{-1} g^T = O\!\big(\text{spread}\big),
\qquad
\Delta R := \mathcal V(\bar{\mathbf a}+\delta\mathbf a^\star)-\mathcal V(\bar{\mathbf a})
\approx \tfrac12\,(g^T)^{\!\top}(-H_T)^{-1}g^T = O\!\big(\mathrm{var}(r_i)\big).
\tag{2.2}
$$
The reward gain from re-optimising the uncued split is **second order in the
heterogeneity** (quadratic in the spread $\Leftrightarrow$ linear in
$\mathrm{var}(r_i)$), because the gradient is $O(\text{spread})$ and the curvature
$|H_T|$ is bounded below by the log-concavity floor. With $|H_T|$ *large* on the
cost-dominant branch (the strong spreading force, $\lambda\sim-0.3$ to $-3$ in
CR-045), the tilt and its reward are tiny.

**Numerical confirmation** (`verify_deviation_interior.py`; value-blind
cost-dominant cells, fine simplex search). At P2 cells with non-trivial budget:

| cell | spread | $\mathrm{var}(r_i)$ | $\Delta R$ | best uncued |
|---|---|---|---|---|
| $\alpha{=}0.26,r{=}0.3$ | 0.1 / 0.2 / 0.3 | $6.0/24/54\times10^{-4}$ | $7.0/18/30\times10^{-6}$ | $\approx$equal, tilt to $0.25,0.25,0.24$ |
| $\alpha{=}0.32,r{=}0.4$ | 0.1 / 0.2 / 0.3 | $11/43/96\times10^{-4}$ | $2.8/8.5/15.0\times10^{-5}$ | tilt to $0.25,0.25,0.18$ |

$\Delta R$ vanishes at spread 0, grows smoothly with $\mathrm{var}(r_i)$ (the
$\Delta R/\mathrm{var}$ ratios are $O(10^{-2})$ and slowly decreasing — pure
second-order away from the kink, with a *sub-quadratic cusp correction* as $\bar
a\to1/N$, see §3), and the tilt of the optimal allocation is marginal (toward the
smaller-$r_i$ slots, as §1 predicts). **The maximum $\Delta R$ over all interior
cells and spreads tested is $1.50\times10^{-4}$ — the CR-045 homogeneous-case
grid slack itself.** Relaxing A8 under ±30% heterogeneous $r$ buys *less than the
homogeneous-case grid resolution*.

---

## 3. Cued-absorption pre-emption is $r$-INDEPENDENT

CR-045 §4 showed that wherever the uncued subspace *would* prefer to concentrate,
the cued slot absorbs the budget ($\alpha^\star\to1$, $B\to0$) before any uncued
misallocation can act. **That mechanism never used the uniformity of $r$**, so it
survives heterogeneity intact. Its two ingredients are structurally
$r$-independent:

1. **Value-weight inequality** $w_c\ge w_u$ $\iff V\ge\tfrac{1}{(N-1)v+1}$,
   implied by $V\ge1/N,v\ge1$ (C4 Eq. 6.4) — a statement about *validity and
   value only*, with no $r$ in it.
2. **Location-count asymmetry** — at $\alpha\to1$ the single cued slot reaches
   $d'_{\text{base}}+\beta_0(d'_{\max}-d'_{\text{base}})>d'_{\text{base}}$ for any
   $r_0>0$ (since $\beta_0>0$, $d'_{\max}>d'_{\text{base}}$), while each of the
   $N{-}1$ uncued falls to $d'_{\text{base}}+\gamma_i(d'_{\max}f_0-d'_{\text{base}})
   <d'_{\text{base}}$. The cued is strictly highest regardless of the $r_i$.

So at any cell with genuine value contrast the budget is cued-absorbed and the
uncued heterogeneity is moot. **Numerical:** at the C2 headline cell ($V=0.5$,
$v=5$, variant A) even the *cost-dominant* $r_{\text{cued}}=0.4$ gives
$\alpha^\star=1.000$ ($B=0$), and the ±30% deviation $\Delta R=0$ exactly; the
benefit-dominant $r_{\text{cued}}=3.0$ likewise gives $\alpha^\star=1.000$,
$\Delta R=0$.

**The cost-dominant kink also survives.** Where the budget is *not* absorbed (the
value-blind P3 policy, $\alpha=1/N$, $B=1-1/N$, every uncued exactly on the
$\beta/\gamma$ kink), CR-045 §3 found a cusp with one-sided slope
$\operatorname{sign}(m)=\operatorname{sign}(r-1)$. In the cost-dominant regime
($r_i<1$ for all uncued) $m_i<0$ per slot, so equal-split is a *sharp local max*
even under heterogeneity — the spreading force wins slot-by-slot.
**Numerical:** at P3 ($\alpha=1/N$, $r_{\text{cued}}=0.3$ and $0.2$), $\Delta R=0$
*exactly* across all spreads up to ±30%. Since the criterion fraction uses
$R(\text{P3})$, this means **the A8-relaxation leaves CF untouched** at the
cost-dominant cells.

The deviation $\Delta R$ of §2 is therefore confined to the *intermediate*
interior cells (P2 with $\bar a$ just below $1/N$), where it is bounded by
$1.5\times10^{-4}$.

---

## 4. Consequence for C1–C5 (the level effect, A8 imposed)

Independently of the allocation interaction (§1–§3), heterogeneous $r_i$ change
the uncued $d'$ *levels* even at equal allocation, so they could in principle move
a headline number through the level alone. This is the genuine A2 effect, and it
is the run-014 "reframing" question. Holding the paper's homogeneous-uncued
allocation (A8 imposed) and letting the uncued $r_i$ spread around $r_{\text{cued}}$:

- **C2 (non-monotonic VDA).** The two-limit mechanism (CR-001/CR-040) is driven by
  the **cued** location's ratio: VDA$\to0$ as $\beta_0(r_{\text{cued}})\to0$
  ($r_{\text{cued}}\to0$) and as the value-blind policy saturates
  ($r_{\text{cued}}\to\infty$). The uncued $r_i$ enter only as bounded nuisance
  parameters. **Numerical:** VDA peak is essentially fixed under ±30% spread
  ($0.0771\to0.0770$, $r_{\text{peak}}=0.398$ unchanged); even the larger
  asymmetric spreads $r_i=r_{\text{cued}}\cdot\{1/k,1,k\}$ keep it at
  $0.0765$–$0.0798$ @ $r_{\text{cued}}\approx0.36$. **C2 reframes cleanly**: the
  non-monotonic peak survives as a statement about $r_{\text{cued}}$, exactly the
  run-014 conjecture — it does *not* refute.

- **C4 (no inversion).** The CR-004/run-006 proof rests on the location-count
  geometry and $w_c\ge w_u$, both **$r$-independent** (§3). Heterogeneous $r_i$
  rescale departures but not the geometry, so C4 is robust. (Not re-measured this
  run; structural argument, consistent with §3.)

- **C1 (criterion fraction).** Already CONTESTED (boundary-sensitive). **Numerical:**
  at the contested corner ($r_{\text{cued}}=10$, $V=0.25$, $v=4$, variant B) the CF
  is $0.3040\to0.3055$ under ±30% spread — **not deepened** (marginally higher).
  R2 heterogeneity does not worsen C1's contested corner.

No headline claim is **shifted** by within-display heterogeneity: C2 reframes
(peak stable), C4 robust, C1 corner unchanged, and (from §2–§3) the
A8-relaxation moves nothing beyond $1.5\times10^{-4}$.

---

## 5. Refined statement of A2 (the conditional)

> **A2 (refined).** The model's single global asymmetry ratio $r$ is empirically
> false under within-display heterogeneity (R2, CR-007), but the reliance does
> **not** bias the headline conclusions C1–C5, conditional on (i) equal uncued
> validity and (ii) a moderate spread of the per-location $r_i$. Two
> $r$-independent forces guarantee this. **(a) Criticality defect is bounded:**
> heterogeneous $r_i$ break the uncued exchange symmetry, so equal-split is
> generically *not* a critical point (tangent gradient $\propto$ spread of
> $\gamma_i$), but the restricted Hessian stays negative-definite on the smooth
> branch (log-concavity of $\Phi$ is $r$-independent), so the optimal tilt and its
> reward are *second order* in $\mathrm{var}(r_i)$ — $\max\Delta R=1.5\times10^{-4}$
> across all interior cells at ±30%, the homogeneous-case slack. **(b)
> Cued-absorption pre-emption** (C4 §6, $r$-independent) empties the uncued budget
> ($\alpha^\star\to1$) at every value-contrast cell, and the cost-dominant kink
> spreading force keeps equal-split optimal at P3, so the criterion fraction is
> untouched. **Level effect:** with allocation held homogeneous, C2's
> non-monotonic VDA peak survives as a statement about the *cued* ratio
> $r_{\text{cued}}$ (a reframing, not a refutation), C4 is robust ($r$-independent
> geometry), and C1's already-contested corner is not deepened. A2 is therefore
> the **most R1-defensible of the paper's named simplifications**: the
> between-preparation reading is discharged by the $r$-sweep, and the
> within-display reading — though empirically real — is shown bounded.

This is the unifying result of the A2/A3/A8 heterogeneity arc:

| assumption | named in §5.5? | verdict | why |
|---|---|---|---|
| **A3** (conservation form $\beta+\gamma=2$ vs $\beta\gamma=1$) | yes | **CONTESTED** | a within-scope alternative *shifts* a headline conjunct (criterion dominance) |
| **A8** (homogeneous uncued allocation) | no | **CONFIRMED-CONDITIONAL** | the optimiser makes A8's choice unprompted under equal validity + single $r$ |
| **A2** (single global $r$) | yes | this run | breaks A8's exchangeability, but the deviation is $O(\mathrm{var}\,r_i)$ and pre-empted by cued-absorption — no headline shift |

The residual A2 risk is *exactly* the A2×A8 coupling, and it is bounded.

---

## 6. Connections to the broader critique

- **The A2/A3/A8 arc closes.** A2 and A8 share the same protective mechanism
  (cued-absorption + log-concavity spreading), and both are benign *within the
  swept regimes*; A3 is the lone CONTESTED member because its alternative changes
  the conservation *form* that sets the magnitudes, not the allocation geometry.
  The referee theme: the paper's *unnamed* simplification (A8) and the
  R1-reading of its *named* one (A2) are both discharged by the optimiser's own
  behaviour; only A3 bites within the grid.

- **Log-concavity of $\Phi$ is again the load-bearing analytic fact** — it makes
  the correct-rejection channel a pure spreading force *per slot*, independent of
  the per-slot $r_i$. The same property carries C4/C5 uniqueness and the CR-045
  homogeneity proof; here it survives the loss of symmetry.

- **C2 reframing → CR-049.** This run gives the first-pass numerical reframing
  (peak stable in $r_{\text{cued}}$); CR-049 is the dedicated replication that
  maps VDA vs $r_{\text{cued}}$ across spreads at full resolution. The §2 bound
  guides which spreads are worth simulating (the effect is $O(\mathrm{var}\,r_i)$).

- **Implications for PRISM (§3.5).** PRISM's per-location/per-channel FiLM gain has
  no global-ratio constraint, so PRISM is simultaneously the A2- and A8-relaxed
  model. The re-derivation sharpens the prediction: trained PRISM agents may learn
  *heterogeneous* effective $r_i$ across the display (eccentricity-/channel-
  dependent — checkable against `Prism/analysis/avg_saliency_*.py`), and §1 says
  this would make their uncued allocation slightly *unequal even at equal
  validity*, tilted toward the more cost-dominant (smaller-$r_i$) locations. But §2
  says the tilt is small ($O(\mathrm{var}\,r_i)$) and §3 says it vanishes wherever
  the cued slot absorbs the budget — so PRISM should still show *near*-homogeneous
  uncued spreading in the swept regimes, with a measurable but second-order
  asymmetry tracking its learned $r_i$ heterogeneity. The trajectory (not the
  snapshot) is the right comparison, given PRISM's recurrence (Sani 2017 /
  Ghose-Maunsell time-varying gain).

---

*End of derivation. Numerical companion (independent grid computation) in
`Critique/replications/A2xA8--heterogeneous-r/` (`verify_heterogeneous_r.py`,
`verify_deviation_interior.py`, `output/*.json`, `output/*.log`). Verdict file at
`Critique/verdicts/A2--single-global-r.md` (Version 0.2).*
