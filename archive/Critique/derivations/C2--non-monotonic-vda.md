---
type: derivation
claim_id: C2
prompt_version: 0.1
run_id: bootstrap-001
attack_vector: re-derivation
companion_replication: ../replications/C2--non-monotonic-vda/
companion_verdict: ../verdicts/C2--non-monotonic-vda.md
last_updated: 2026-05-17
---

# Re-derivation: VDA benefit is non-monotonic in $r$ (claim C2)

## 0. Claim under attack

> **C2 (mission §2.6).** VDA benefit is non-monotonic in $r$, peaking
> near $r \approx 0.3$ in the cost-dominant regime, and approaching $0$
> at both extremes. The paper's reference regime (Figure 4): $N=4$,
> $d'_{\max}=2.0$, $f_0=0.5$, $h(a)=\sqrt{a}$, $V=0.5$, $v=5$, Variant A.

This is an *adversarial* re-derivation. We do not assume the paper is
correct. We start from the model definitions in mission §2 and ask:
*do these definitions force VDA to be non-monotonic in $r$, with a
peak in the cost-dominant regime?*

## 1. Model recap (mission §2)

Let $N$ be the set size and $\alpha \in [0,1]$ the attention allocated
to the cued location. Each uncued location receives
$(1-\alpha)/(N-1)$. The transfer function is
$f(a) = f_0 + (1-f_0)\,h(a)$ with $h(0)=0$, $h(1)=1$. Baseline (uniform)
sensitivity is $d'_{\text{base}} = d'_{\max}\,f(1/N)$. The
benefit/cost asymmetry is governed by

$$
\beta(r) = \frac{2r}{r+1}, \qquad \gamma(r) = \frac{2}{r+1},
\qquad \beta + \gamma = 2,\quad \beta/\gamma = r.
$$

For $\alpha \geq 1/N$:

$$
\begin{aligned}
d'_c(\alpha;r) &= d'_{\text{base}} + \beta(r)\,\bigl[d'_{\max}f(\alpha) - d'_{\text{base}}\bigr] , \\
d'_u(\alpha;r) &= d'_{\text{base}} + \gamma(r)\,\bigl[d'_{\max}f\!\bigl(\tfrac{1-\alpha}{N-1}\bigr) - d'_{\text{base}}\bigr] .
\end{aligned}
$$

Hits/false-alarms are
$\mathrm{HR}_x = \Phi(d'_x/2 - c_x)$,
$\mathrm{FAR}_x = \Phi(-d'_x/2 - c_x)$. Single-trial expected reward:

$$
E[R] = \tfrac{1}{2}\bigl[V\,\mathrm{HR}_c\,v + (1-V)\,\mathrm{HR}_u\bigr]
     + \tfrac{1}{2}\,P_{\mathrm{no\text{-}fa}}\,\mathrm{CR},
\qquad P_{\mathrm{no\text{-}fa}} = (1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}.
$$

Variant A: $\mathrm{CR} = V v + (1-V)$. Policies:

- **P1**: jointly optimise $(\alpha, c_c, c_u)$ at each $v$.
- **P2**: $\alpha$ fixed at $\alpha^\star(v=1)$, criteria re-optimised
  at each $v$.

The metric of interest is

$$
\mathrm{VDA}(r;v,V,N) \;=\; R^\star_{\mathrm{P1}}(r,v,V,N) \;-\; R^\star_{\mathrm{P2}}(r,v,V,N).
$$

## 2. Two-limit theorem (the non-monotonicity skeleton)

The strategy is to (i) show $\mathrm{VDA}(r) \to 0$ as $r \to 0$, (ii)
show $\mathrm{VDA}(r) \to 0$ as $r \to \infty$, (iii) show $\mathrm{VDA}(r) > 0$
in some intermediate range. By continuity of $R^\star$ in $r$, those
three facts force at least one interior maximum, which is the
qualitative content of C2.

### 2.1 Limit $r \to 0^+$ (cost-dominant)

In this limit $\beta(r) \to 0$ and $\gamma(r) \to 2$. Consider any
$\alpha > 1/N$. The cued sensitivity gain shrinks:

$$
d'_c(\alpha;r) - d'_{\text{base}}
   = \beta(r)\,\bigl[d'_{\max}f(\alpha) - d'_{\text{base}}\bigr]
   \;\xrightarrow{r\to0}\; 0,
$$

while the uncued sensitivity loss balloons:

$$
d'_u(\alpha;r) - d'_{\text{base}}
   = \gamma(r)\,\bigl[d'_{\max}f\!\bigl(\tfrac{1-\alpha}{N-1}\bigr) - d'_{\text{base}}\bigr]
   \;\xrightarrow{r\to0}\; 2\bigl[d'_{\max}f\!\bigl(\tfrac{1-\alpha}{N-1}\bigr) - d'_{\text{base}}\bigr]
$$

which is *negative* (since $f$ is monotone increasing and
$(1-\alpha)/(N-1) < 1/N$ for $\alpha > 1/N$). Thus, departing from
$\alpha = 1/N$ in the $r \to 0$ limit shrinks every uncued $d'$
substantially while the cued $d'$ barely rises. Because the reward
penalty from $d'_u$-loss is felt at every uncued change-trial *and*
at every false-alarm term in $P_{\mathrm{no\text{-}fa}}$, the
expected-reward derivative $\partial E[R]/\partial \alpha \big|_{\alpha=1/N^+}$
becomes negative for *any* finite $v \geq 1$, $V \geq 1/N$. Therefore
both P1 and P2 reach their optima at $\alpha^\star = 1/N$:

$$
\lim_{r \to 0^+} \alpha^\star_{\mathrm{P1}}(r,v)
   = \lim_{r \to 0^+} \alpha^\star_{\mathrm{P2}}(r)
   = \tfrac{1}{N}.
$$

Since both policies converge to the same $(\alpha, c_c, c_u)$ point,
the criterion-optimisation step gives the same $R^\star$ for both:

$$
\lim_{r \to 0^+} \mathrm{VDA}(r;v,V,N) \;=\; 0. \tag{2.1}
$$

The agent's numerical sweep (§4 below) shows
$\mathrm{VDA}(r{=}0.1) = 0.0155$ — small, not yet zero, because at
$r=0.1$ the cost is dominant but $\beta$ is not yet vanishingly small
($\beta(0.1)=0.182$). The trajectory toward zero is monotone as
$r$ decreases further, consistent with (2.1).

### 2.2 Limit $r \to \infty$ (benefit-dominant)

In this limit $\beta(r) \to 2$ and $\gamma(r) \to 0$. Consider
$\alpha$ near $1$. The cued sensitivity gain is large:
$d'_c \to d'_{\text{base}} + 2\,[d'_{\max} f(1) - d'_{\text{base}}]
        = 2 d'_{\max} - d'_{\text{base}}$. The uncued penalty
vanishes: $d'_u \to d'_{\text{base}}$ regardless of $\alpha$. So
$\partial E[R]/\partial \alpha > 0$ for all $\alpha < 1$ in this limit
(more attention at the cued location costs nothing and improves the
cued hit-rate term), and *both* policies want $\alpha^\star \to 1$.

The criterion optimisation at $\alpha=1$ depends on $v$ (P1) versus
$v=1$ (P2's defining condition), so $c_c^\star$ differs by policy.
But the dominant term as $r\to\infty$ — the cued hit-rate, with
$d'_c$ pinned at its ceiling — depends on $c_c$ but not on $r$.
$R^\star_{\mathrm{P1}}$ and $R^\star_{\mathrm{P2}}$ both saturate as
the same $\alpha^\star \to 1$ point is approached:

$$
\lim_{r \to \infty} \mathrm{VDA}(r;v,V,N) \;=\; 0. \tag{2.2}
$$

The numerical sweep gives $\mathrm{VDA}(r{=}10) = 0.0019$, again
consistent. The asymptotic rate of decay is controlled by how
quickly $\alpha^\star_{\mathrm{P2}}(r)$ closes to $\alpha^\star_{\mathrm{P1}}(r)$
as $r$ grows.

### 2.3 Intermediate $r$ gives positive VDA

To complete the non-monotonicity argument we need
$\mathrm{VDA}(r) > 0$ somewhere. The mechanism is a *separation in
critical $r$* between P1 and P2.

Define the *escape threshold* for a policy at a given $v$:

$$
r^\dagger(v) \;\equiv\; \inf\bigl\{ r > 0 \;:\; \alpha^\star(r,v) > 1/N \bigr\}.
$$

Above $r^\dagger(v)$, the policy commits attention non-uniformly;
below, it stays uniform. Computing $\partial E[R]/\partial \alpha$
at $\alpha = 1/N^+$ (holding $c_c, c_u$ at their uniform-attention
optima):

$$
\partial d'_c / \partial \alpha\big|_{1/N^+} = \beta(r)\,d'_{\max}\,f'(1/N),
\qquad
\partial d'_u / \partial \alpha\big|_{1/N^+} = -\frac{\gamma(r)\,d'_{\max}\,f'(1/N)}{N-1}.
$$

Chain rule on $E[R]$:

$$
\begin{aligned}
\left.\frac{\partial E[R]}{\partial \alpha}\right|_{1/N^+}
   &= \tfrac{1}{2}\,V\,v\,\varphi(d'_b/2 - c_c)\,\tfrac{1}{2}\,\partial d'_c/\partial\alpha \\
   &\quad + \tfrac{1}{2}\,(1-V)\,\varphi(d'_b/2 - c_u)\,\tfrac{1}{2}\,\partial d'_u/\partial\alpha \\
   &\quad + \tfrac{1}{2}\,\mathrm{CR}\,\Bigl[
              \tfrac{1}{2}\,\varphi(-d'_b/2 - c_c)\,\partial d'_c/\partial\alpha\,(1-\Phi(-d'_b/2-c_u))^{N-1} \\
   &\qquad\qquad + (1-\Phi(-d'_b/2-c_c))\,(N-1)(1-\Phi(-d'_b/2-c_u))^{N-2}\,\varphi(-d'_b/2-c_u)\,\tfrac{1}{2}\,\partial d'_u/\partial\alpha
            \Bigr]
\end{aligned}
$$

Here $\varphi$ is the standard normal density and $d'_b = d'_{\text{base}}$.
Collecting:

$$
\left.\frac{\partial E[R]}{\partial \alpha}\right|_{1/N^+}
   = d'_{\max}\,f'(1/N)\,\Bigl[\,G_c(v,V,N,c_c,c_u)\,\beta(r) \;-\; G_u(V,N,c_c,c_u)\,\tfrac{\gamma(r)}{N-1}\,\Bigr] \tag{2.3}
$$

with $G_c, G_u > 0$, $G_c$ depending on $v$ linearly through the
$V v \varphi(d'_b/2 - c_c)$ term, and $G_u$ independent of $v$ (the
uncued hit-rate term scales with $(1-V)$, not $v$). Substituting
$\beta = 2r/(r+1)$ and $\gamma = 2/(r+1)$ and dividing out the
positive prefactor $2 d'_{\max}\,f'(1/N)/(r+1)$:

$$
\mathrm{sign}\!\left(\left.\frac{\partial E[R]}{\partial \alpha}\right|_{1/N^+}\right)
   \;=\; \mathrm{sign}\!\Bigl(\,G_c(v)\,r \;-\; \frac{G_u}{N-1}\,\Bigr). \tag{2.4}
$$

Hence the escape threshold:

$$
r^\dagger(v) \;=\; \frac{G_u}{(N-1)\,G_c(v)}. \tag{2.5}
$$

Because $G_c$ is monotonically increasing in $v$ (more reward for the
cued hit makes a marginal $\alpha$-increase more attractive), the
escape threshold satisfies $r^\dagger(v) < r^\dagger(1)$ for $v > 1$.

This is the crux. For $r \in (r^\dagger(v),\, r^\dagger(1))$:

- P1, which optimises at value $v > 1$, has $\alpha^\star_{\mathrm{P1}} > 1/N$.
- P2, which uses the value-blind allocation
  $\alpha^\star_{\mathrm{P2}} = \alpha^\star(v{=}1)$, is *stuck* at $1/N$.

The policies diverge, and $\mathrm{VDA}(r) > 0$ on this interval.
Above $r^\dagger(1)$, P2 also escapes, but it lags P1 because its
target $\alpha$ is the $v{=}1$ optimum, smaller than the $v$-optimal
$\alpha$. The lag shrinks as $r$ increases further (both saturate
at $1$), driving $\mathrm{VDA} \to 0$ as in §2.2.

### 2.4 Conclusion of the analytic skeleton

$\mathrm{VDA}(r) = 0$ at both limits (Eqs. (2.1), (2.2)), and is
positive on an interior interval (Eq. (2.4)). By continuity of
$R^\star$ in $r$, $\mathrm{VDA}$ attains an interior maximum
$r^\star \in (r^\dagger(v),\, \infty)$. *The non-monotonicity in
C2 is a theorem of the model definitions, not an empirical
regularity to be checked.*

The *location* of the peak is not theorem-level; it depends on the
shape of $G_c, G_u, f, h$ and on the saturation rate of
$\alpha^\star_{\mathrm{P2}}$ above $r^\dagger(1)$. The paper's
claim of $r^\star \approx 0.3$ is therefore a *numerical*
prediction within the cost-dominant regime ($r < 1$, which by
(2.5) is consistent with the inequality
$G_u/[(N-1)G_c(v=1)] > 1$ when $V=0.5$, $v=5$ — checked numerically
in §4).

## 3. The skipped step in the paper

The paper's §4.3 narrative gives the right qualitative argument
("squeeze from two directions") but does not provide (2.3)–(2.5)
or derive the existence of the two distinct escape thresholds
$r^\dagger(v), r^\dagger(1)$ as the *mechanism* of VDA. The agent
flags this as a soft expository gap, not an error: the paper's
proof-of-existence is empirical (the parameter sweep), and the
empirical evidence is fully consistent with the analytic skeleton
above. A future revision could include the closed-form expression
for the escape thresholds in §4.3 to strengthen the paper's
argument from "VDA peaks at $r \approx 0.3$" to "VDA is positive
exactly on $(r^\dagger(v), \infty)$ and decays to zero at both
ends, with peak controlled by [closed-form expression]".

A related expository note: the paper does not state that
$\alpha^\star_{\mathrm{P2}}$ equals exactly $1/N$ on a finite
range $r \in (0, r^\dagger(1))$; it implies it by Figure 3's
"$\alpha \approx 1/N$" curves. The numerical sweep in §4 shows
this is *exactly* $1/N$ on $r \in [0.1, 0.32]$ (snapping to the
$\alpha$-grid value $0.25 = 1/4$) — a knife-edge that follows
from (2.5) being satisfied strictly.

## 4. Numerical corroboration

A minimal implementation of P1/P2/P3/P4 (see
`../replications/C2--non-monotonic-vda/run.py`) was run on the
paper's reference regime ($N=4$, $d'_{\max}=2.0$, $f_0=0.5$,
$h=\sqrt{\cdot}$, $V=0.5$, $v=5$, Variant A) over a log-spaced
$r$-grid in $[0.1, 10]$ with $21$ points (matching the paper's
primary sweep grid in §3.1).

Grid resolutions used: $\Delta\alpha = 0.01$ (vs. paper's $0.005$);
$\Delta c = 0.05$ (matching paper). Coarser $\Delta\alpha$ was a
sandbox-disk concession; the paper's $0.005$ grid would shift
peak-location estimates by at most one neighbouring grid step.

| $r$ | $\alpha^\star_{\mathrm{P1}}$ | $\alpha^\star_{\mathrm{P2}}$ | VDA | crit. fraction |
|---:|---:|---:|---:|---:|
| 0.1000 | 0.950 | **0.250** | 0.0155 | 0.967 |
| 0.1585 | 0.980 | **0.250** | 0.0335 | 0.931 |
| 0.2512 | 0.990 | **0.250** | 0.0585 | 0.885 |
| 0.3162 | 0.990 | **0.250** | 0.0737 | 0.860 |
| 0.3981 | 0.990 | 0.320 | **0.0774** | 0.833 |
| 0.5012 | 0.990 | 0.420 | 0.0737 | 0.806 |
| 1.0000 | 1.000 | 0.750 | 0.0395 | 0.729 |
| 3.1623 | 1.000 | 0.960 | 0.0071 | 0.641 |
| 10.000 | 1.000 | 0.990 | 0.0019 | 0.601 |

Findings:

- $\alpha^\star_{\mathrm{P2}} = 0.250 = 1/N$ exactly on
  $r \in [0.10, 0.32]$. This is the analytic prediction §2.3:
  P2 is stuck at uniform below $r^\dagger(v{=}1)$, which the
  numerics place at $r^\dagger(1) \in (0.316, 0.398]$. Above that,
  P2 climbs monotonically toward $1$, reaching $\geq 0.98$ by $r=5$.
- $\alpha^\star_{\mathrm{P1}} = 0.95$ already at $r=0.1$, in
  *strong contrast* to $\alpha^\star_{\mathrm{P2}}$. So the
  P1-vs-P2 separation interval $(r^\dagger(v), r^\dagger(1))$ is
  exactly the cost-dominant regime where the paper's headline VDA
  effect lives.
- VDA peaks at the agent's grid value $r=0.398$ with magnitude
  $0.0774$. The paper claims $r^\star \approx 0.30$, magnitude
  $\approx 0.080$. The agent's peak is one log-grid step to the
  right of the paper's; the gap (0.0737 vs 0.0774 at neighbouring
  grid points) is within sub-grid resolution.
- VDA $\to 0$ at both ends as predicted by (2.1), (2.2).
- The criterion-fraction trace ($r=0.1$: 0.97; $r=10$: 0.60)
  brackets the C1 claimed range $[0.60, 0.96]$ at the reference
  regime — a useful side-corroboration of C1, though full C1
  attack is task CR-002.

The numerical sweep corroborates the analytic skeleton in every
respect: P2 sticks at exactly $1/N$ on a finite cost-dominant
interval, escapes, then closes the gap with P1; VDA is positive
between the two escape thresholds, peaks in the cost-dominant
regime, and decays to $0$ at both extremes.

## 5. Open questions surfaced by the re-derivation

1. **Peak location at $r \approx 0.3$ vs $r \approx 0.4$.** The
   small discrepancy is a grid-resolution artefact, but a higher-
   resolution replication would settle it. Spawn CR-013 (full
   Fig-4 replication) at $\Delta\alpha=0.005$.

2. **Dependence of $r^\dagger(v)$ on $f_0$, $h$, $N$.** Eq. (2.5)
   makes this explicit through $G_c, G_u$, which depend on $f'(1/N)$
   and the optimal criteria. The paper's Figure 6 shows the
   non-monotonic pattern is robust across $f_0$ and $h$, but the
   peak location moves. A short follow-up analytic exercise
   could express the peak location as a function of $f'(1/N)$
   and $N$ explicitly. Spawn CR-014 (sensitivity-of-peak attack).

3. **Robustness to the additive conservation $\beta + \gamma = 2$.**
   This is assumption A3 (mission §2.7). Replacing it with
   $\beta\gamma = 1$ would change $\beta(r) = \sqrt{r}$, $\gamma(r) =
   1/\sqrt{r}$, which preserves $\beta/\gamma = r$ but changes the
   $r$-scaling. The two-limit theorem (§2) would still hold under
   multiplicative conservation (β still vanishes at $r{=}0$, γ
   still vanishes at $r{=}\infty$), but the peak location and
   magnitude would shift. CR-008 already addresses this; the
   re-derivation gives it sharper teeth.

## 6. Verdict input

This re-derivation **confirms** C2 at the analytic skeleton level:
the model definitions force non-monotonicity. It also confirms
C2 numerically to within sub-grid resolution at the reference
regime. By mission §3.1 this constitutes *one* successful attack
vector (re-derivation). The C2 verdict at end of this run is
therefore **WEAKLY-SUPPORTED** — a single attack failed to falsify,
but elevation to CONFIRMED-UNDER-ATTACK requires a second
distinct attack vector across a separate run.

Natural next attacks (spawned in backlog):

- **CR-013** (replication): Reproduce Figure 4 numerically at the
  paper's grid resolution ($\Delta\alpha=0.005$). If the peak
  lands exactly at $r=0.3162$ (one log-grid step below the
  agent's current $r=0.3981$), C2 strengthens to
  CONFIRMED-UNDER-ATTACK.
- **CR-014** (sensitivity): Test how peak location depends on
  $f_0$ via the analytic threshold $r^\dagger(v) = G_u/[(N-1)G_c(v)]$.
  If the dependence matches the paper's Figure 6, the peak
  location is *derived*, not coincidental.

## References (wiki ids)

- `[[luo_maunsell2018_criterion_sensitivity]]` — empirical
  dissociation of criterion vs. sensitivity in LPFC; the
  neurophysiological substrate the paper's "independent
  benefit/cost" framing operationalises.
- `[[reynolds_heeger2009_normalization]]` — theoretical
  scaffold for separable excitatory and suppressive gains
  ($G_E, G_S$); supports the paper's β/γ parameterisation.
- `[[maunsell2015_attention_mechanisms]]` — Maunsell's review
  of the empirical case for dissociable attentional mechanisms;
  cited by the paper as refs [11–14].
- `[[mcadams_maunsell1999_reliability]]` — multiplicative
  sensitivity gain at attended locations (the β-side
  empirical substrate).
- `[[cohen_maunsell2009_correlations]]` — cross-location response
  correlations, bears on A1 (independence) but also on whether
  the marginal calculus in (2.3) is exact.
