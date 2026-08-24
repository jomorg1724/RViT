---
type: derivation
claim_id: A8
attack: re-derivation
companion_replication: Critique/replications/A8--heterogeneous-uncued/run.py
companion_verification: Critique/replications/A8--heterogeneous-uncued/cr045_rederivation_check/
prompt_version: 0.2
run_id: run-013
created: 2026-05-24
---

# A8 — "Homogeneous-uncued allocation does not bias C1–C5": re-derivation

> **Assumption under attack (paper §2.2, verbatim).** *"The observer allocates
> attention $\alpha \in [0,1]$ to the cued location. The remaining attention is
> distributed equally among uncued locations, so each receives
> $(1-\alpha)/(N-1)$. At uniform attention, $\alpha = 1/N$ and all locations are
> treated identically."*

A8 forces the uncued budget $B := 1-\alpha$ to be split **equally** among the
$N-1$ uncued locations, collapsing the policy space to one dimension in
$\alpha$. The replication CR-036 (run-012) established **numerically** that this
is innocuous for the headline claims — under equal uncued validity the equal
split is the *optimum*, not merely the imposed choice, at every swept cell — and
left A8 `WEAKLY-SUPPORTED`, with the designated second vector being a closed-form
proof of two propositions:

- **(a) Homogeneity-optimality.** Under equal uncued validity, the equal split
  maximises $\mathbb{E}[R]$ over the uncued simplex (criteria re-optimised).
- **(b) Cued-absorption pre-emption.** Wherever the uncued subspace *would*
  prefer to concentrate, the cued allocation is driven to $\alpha^\star\to1$, so
  no uncued budget survives and A8 never binds at the model's own optimum.

This file proves both, reusing the C4 location-count / value-weight machinery
(`Critique/derivations/C4--no-inversion.md` §6). Notation is mission §2
throughout. Numerical corroboration (independent of CR-036's `run.py`) is in
`Critique/replications/A8--heterogeneous-uncued/cr045_rederivation_check/`.

---

## 0. Setup: the heterogeneous-allocation reward and the uncued subspace

Locations $i=0,\dots,N-1$, location $0$ cued. Allocation vector
$\mathbf a=(a_0,\dots,a_{N-1})$, $a_i\ge0$, $\sum_i a_i=1$. Under **equal uncued
validity** the weights are
$$
w_0 = V,\quad w_i=\tfrac{1-V}{N-1}\ (i\ge1),\qquad
u_0=v,\quad u_i=1\ (i\ge1),
$$
so the value$\times$validity weight is $\omega_0=Vv$ for the cued and
$\omega_u=\tfrac{1-V}{N-1}$ for **every** uncued location — they are
*exchangeable*. The generalised per-location sensitivity (the unique
generalisation of Eqs. (7)–(8) consistent with the §2.3 reversal note; see
`notes.md` §1) is
$$
d'_i = \max\!\Big(d'_{\text{base}} + s_i\big[d'_{\max} f(a_i)-d'_{\text{base}}\big],\,0\Big),\qquad
s_i=\begin{cases}\beta(r) & a_i\ge 1/N\\ \gamma(r) & a_i< 1/N\end{cases}
\tag{0.1}
$$
with $\beta=\tfrac{2r}{r+1}$, $\gamma=\tfrac{2}{r+1}$, $f(a)=f_0+(1-f_0)h(a)$,
$d'_{\text{base}}=d'_{\max}f(1/N)$. With per-location criteria $c_i$ and
$\mathrm{HR}_i=\Phi(d'_i/2-c_i)$, $\mathrm{FAR}_i=\Phi(-d'_i/2-c_i)$, the reward
(generalising Eq. (9)) is
$$
\mathbb{E}[R](\mathbf a,\mathbf c)
= \tfrac12\sum_i \omega_i\,\mathrm{HR}_i
+ \tfrac12\,\mathrm{CR}\prod_i\big(1-\mathrm{FAR}_i\big),
\qquad \omega_0=Vv,\ \omega_{i\ge1}=\omega_u.
\tag{0.2}
$$

Fix the cued allocation at $a_0=\alpha$ and the budget $B=1-\alpha$. The
**uncued subspace** is the simplex
$\Delta_B=\{(a_1,\dots,a_{N-1}):a_i\ge0,\ \sum a_i=B\}$. Write the value function
(criteria optimised) as
$$
\mathcal V(a_1,\dots,a_{N-1}) := \max_{\mathbf c}\ \mathbb{E}[R](\alpha,a_1,\dots,a_{N-1};\mathbf c).
\tag{0.3}
$$
The equal split is $\bar a := B/(N-1)$ at every uncued slot.

---

## 1. Proposition (a), part 1 — equal split is always a critical point (exact)

$\mathcal V$ is a **symmetric** function of $(a_1,\dots,a_{N-1})$: permuting the
uncued allocations permutes a set of exchangeable locations (equal $\omega_u$,
equal value, equal transfer function), and both the sum $\sum_i\mathrm{HR}_i$ and
the product $\prod_i(1-\mathrm{FAR}_i)$ in (0.2) are symmetric under that
permutation; the inner $\max_{\mathbf c}$ preserves symmetry. Hence for any
transposition $\tau$ of two uncued slots, $\mathcal V(\mathbf a)=\mathcal V(\tau\mathbf a)$.

The equal-split point $\bar{\mathbf a}=(\bar a,\dots,\bar a)$ is the unique fixed
point of all such $\tau$ in $\Delta_B$. A differentiable symmetric function has
equal partials there: $\partial_{a_i}\mathcal V|_{\bar{\mathbf a}}=\mu$ for all
$i$, so the gradient is parallel to the simplex normal $(1,\dots,1)$ and its
projection onto the tangent space $T=\{\boldsymbol\delta:\sum_i\delta_i=0\}$ is
**zero**. Therefore $\bar{\mathbf a}$ is a critical point of $\mathcal V$ on
$\Delta_B$ — *exactly, for every $r$, every $h$, every cell*. (Numerically,
$\mathcal V'(0)=O(10^{-5})$ to grid resolution; verification log
`curvature_and_absorption.log`, block [V1/V2], column `R'(0)`.)

Whether it is a **maximum** is the content of part 2.

---

## 2. Proposition (a), part 2 — the restricted Hessian is a scalar $\lambda$

At $\bar{\mathbf a}$ the stabiliser is the full symmetric group $S_{N-1}$ acting
on the uncued slots. The tangent space $T$ (zero-sum vectors over $N-1$
coordinates) is the **standard representation** of $S_{N-1}$, which is
*irreducible*. The Hessian of $\mathcal V$ restricted to $T$ commutes with this
action, so by Schur's lemma it is a scalar multiple of the identity:
$$
\boxed{\ \nabla^2_T\mathcal V\big|_{\bar{\mathbf a}} = \lambda\, I_{N-2}\ }\qquad
\text{for a single scalar }\lambda.
\tag{2.1}
$$
Equal split is a strict local **max** iff $\lambda<0$, a strict local **min**
iff $\lambda>0$. One number decides it. Taking the pure two-slot exchange
$\boldsymbol\delta=(+1,-1,0,\dots)$ (so $\|\boldsymbol\delta\|^2=2$),
$$
\lambda = \tfrac12\,\frac{d^2}{dt^2}\,\mathcal V(\bar a+t,\ \bar a-t,\ \bar a,\dots)\Big|_{t=0}.
\tag{2.2}
$$
(Cross-check: the symmetric direction $(+1,+1,-2)$ used by CR-036 has
$\|\cdot\|^2=6$, so its second derivative equals $6\lambda$;
the verification reproduces both, block [V1/V2].)

### 2.1  Closed form for $\lambda$ on the smooth $\gamma$-branch ($\bar a<1/N$)

When $\bar a<1/N$ strictly, all uncued slots sit on the **loss branch**
($s_i=\gamma$, no kink crossing for small $t$). Write the single-slot
sensitivity map $g(a)=d'_{\text{base}}+\gamma[d'_{\max}f(a)-d'_{\text{base}}]$, so
$$
g'(a)=\gamma\,d'_{\max}(1-f_0)h'(a)>0,\qquad
g''(a)=\gamma\,d'_{\max}(1-f_0)h''(a).
\tag{2.3}
$$
Let $d=g(\bar a)$, $c=c_u^\star$ the symmetric uncued criterion, and define the
SDT shorthands at the operating point
$$
x_H=\tfrac d2-c,\quad x_F=\tfrac d2+c,\quad
\mathrm{HR}_d=\tfrac12\phi(x_H),\ \mathrm{HR}_{dd}=-\tfrac14 x_H\phi(x_H),\
G=\Phi(x_F),\ G_d=\tfrac12\phi(x_F),\ G_{dd}=-\tfrac14 x_F\phi(x_F).
$$
Differentiating (0.2) along the exchange (envelope theorem holds the criteria;
the criterion-coupling correction is treated in §2.3) gives, after collecting
the cued and "other-uncued" factors into constants,
$$
\lambda \;=\; \underbrace{\tfrac12\omega_u\big[\mathrm{HR}_{dd}\,g'^2 + \mathrm{HR}_d\,g''\big]}_{\textstyle \lambda_{\mathrm{HR}}}
\;+\; \underbrace{Q\big[\,G\big(G_{dd}g'^2+G_d g''\big) - G_d^2\,g'^2\,\big]}_{\textstyle \lambda_{\mathrm{noFA}}},
\tag{2.4}
$$
with $Q=\tfrac12\,\mathrm{CR}\,(1-\mathrm{FAR}_0)\,G^{\,(N-1)-2}\ge0$ the constant
cued$\times$other-uncued no-FA factor. **This closed form matches a
fixed-criterion finite difference to 5 decimal places** across all four $h$ and
$r\in\{0.398,0.5,1,2\}$ (verification log `closedform_lambda_and_kink.log`,
block (A); every row flagged agreement, max discrepancy $<10^{-3}$ at
$\varepsilon=10^{-4}$).

### 2.2  Sign of $\lambda$: the no-FA term is unconditionally spreading

Rewrite $\lambda_{\mathrm{noFA}}$ using $\log$-derivatives. Since
$2G G_{dd}-2G_d^2 = 2G^2\big[(\log G)''\big]$ and $G_d g''$ is the only $h''$
term,
$$
\lambda_{\mathrm{noFA}} = Q\Big[\,G^2\,g'^2\,(\log G)'' \;+\; G\,G_d\,g''\,\Big].
\tag{2.5}
$$
Two facts settle its sign for **concave-or-linear $h$**:

1. **$(\log G)''<0$.** $G=\Phi(x_F)$ and the standard normal CDF is
   **log-concave** (a classical fact: $\Phi$ is a one-dimensional log-concave
   distribution function), so $\log\Phi$ is concave and
   $(\log G)''=G_{dd}/G-(G_d/G)^2<0$. This is the multiplicative-coupling /
   Jensen penalty: splitting the no-FA mass unequally *lowers* the product
   $\prod(1-\mathrm{FAR}_i)$.
2. **$g''\le0$.** For $h$ concave or linear ($h''\le0$), (2.3) gives $g''\le0$;
   with $G,G_d>0$ the term $G G_d g''\le0$.

Hence $\lambda_{\mathrm{noFA}}\le0$ unconditionally for concave-or-linear $h$ —
the correct-rejection channel **always** rewards spreading. The HR channel
$\lambda_{\mathrm{HR}}$ can be positive only through (i) $\mathrm{HR}_{dd}>0$,
i.e. a **conservative** criterion $c>d/2$ ($x_H<0$), or (ii) $g''>0$, i.e.
**accelerating** $h$. The arithmetic outcome (verification block (A)):

| $h$ | $\lambda$ at the smooth point ($\alpha{=}0.7$, $\bar a{=}0.1$, value-blind) | verdict |
|---|---|---|
| $a^{0.3}$ (strongly diminishing) | $-0.50\to-0.24$ over $r\in[0.4,2]$ | max ✓ |
| $\sqrt a$ (default) | $-0.34\to-0.16$ | max ✓ |
| $a$ (linear) | $-0.011\to-0.003$ | max ✓ ($\lambda_{\mathrm{noFA}}$ beats a small $+\lambda_{\mathrm{HR}}$) |
| $a^2$ (accelerating) | $+0.048\to+0.024$ | **min** — smooth-branch concentration |

So **for three of the paper's four transfer forms ($a^{0.3},\sqrt a,a$) the equal
split is a strict local max on the smooth branch; only the accelerating $a^2$
flips $\lambda>0$.** This is exactly the "Schur-concave for concave-or-linear
$h$" claim CR-045 asked for: a symmetric function with $\nabla^2_T\preceq0$ is
Schur-concave, and a Schur-concave function on $\Delta_B$ is maximised at the
majorisation-minimal point $\bar{\mathbf a}$ (the equal split is majorised by
every other vector of the same sum). The $a^2$ exception is handled by
proposition (b) — and is shown there to be *vacuous* because cued-absorption
drives $B\to0$ fastest precisely for accelerating $h$.

### 2.3  The criterion-coupling correction is the right sign for us

$\mathcal V$ optimises criteria, so the true restricted Hessian is the Schur
complement $\nabla^2_T\mathcal V = \mathbb E_{aa}-\mathbb E_{ac}\mathbb
E_{cc}^{-1}\mathbb E_{ca}$. Because $\mathbb E_{cc}\prec0$ at the criterion
maximum, the correction $-\mathbb E_{ac}\mathbb E_{cc}^{-1}\mathbb E_{ca}\succeq0$
is **positive semidefinite** — re-optimising criteria can only make $\mathcal V$
*less* concave than the fixed-criterion form (2.4). Two consequences, both
honest:

- Where (2.4) already gives $\lambda<0$ **and** the fully re-optimised finite
  difference also gives $\lambda<0$ (verification block [V1/V2]: $\lambda<0$ at
  every smooth cell tested, e.g. $-0.13$ at $r{=}0.398$ to $-3.25$ at $r{=}5$ for
  $\sqrt a$), the conclusion is safe: the PSD correction did not overturn the
  sign.
- The correction is *why* I cannot prove $\lambda<0$ from fixed-criterion
  concavity alone for the borderline $a^2$ case; the numerics (not a fixed-$c$
  bound) carry the $a^2$ sign, and proposition (b) makes it moot regardless.

---

## 3. The kink at $\bar a = 1/N$: equal split is a CUSP, not a smooth extremum

When the cued allocation is at uniform ($\alpha=1/N$), the budget is
$B=1-1/N$ and the equal split puts **every** uncued slot at exactly
$\bar a=(1-1/N)/(N-1)=1/N$ — i.e. *on the $\beta/\gamma$ kink* of (0.1). This is
the regime of CR-036's "forced uncued budget" (Part 1b), where 8/12 cells were
found to favour concentration. The re-derivation explains it cleanly.

Along the exchange $a_1=1/N+t,\ a_2=1/N-t$: for $t>0$ slot 1 is a **gain**
($s=\beta$) and slot 2 a **loss** ($s=\gamma$); for $t<0$ the roles swap. To
first order the perturbed sensitivities are
$$
d_1(t)+d_2(t) = 2d'_{\text{base}} + (\beta-\gamma)\,\kappa\,|t| + O(t^2),
\qquad \kappa:=d'_{\max}f'(1/N)>0,
\tag{3.1}
$$
a **cusp** in $|t|$ (the $|t|$ because the steep-$\gamma$ / shallow-$\beta$ slopes
do not cancel across the kink). Consequently $\mathcal V(t)$ has the one-sided
expansion $\mathcal V(t)=\mathcal V(0)+m\,|t|+O(t^2)$ with
$$
\operatorname{sign}(m)=\operatorname{sign}(\beta-\gamma)=\operatorname{sign}(r-1).
\tag{3.2}
$$
So at the forced-uniform budget:

- $r<1$ ($\beta<\gamma$, cost-dominant): $m<0$, equal split is a **sharp local
  max** (spreading) — A8 is *strictly* optimal;
- $r>1$ ($\beta>\gamma$, benefit-dominant): $m>0$, equal split is a **sharp
  local min** (concentration favoured) — A8 *binds*;
- $r=1$: $\beta=\gamma$, no kink, $m=0$ (flat to first order).

The verification (block (B)) confirms this is a genuine cusp, not a second-order
effect: the one-sided slope $(\mathcal V(\varepsilon)-\mathcal V(0))/\varepsilon$
converges to a nonzero constant ($-0.021$ at $r{=}0.5$, $+0.021$ at $r{=}2$,
$\approx0$ at $r{=}1$) while the central second difference scales as $1/\varepsilon$
($\varepsilon\cdot\text{2nd-diff}\approx$ const). **CR-036's reported
"$R''(0)>0$" at the benefit-dominant forced cells was therefore measuring the
cusp slope $m>0$, not a curvature**; the present analysis replaces the
grid/$\varepsilon$-dependent magnitudes with the exact first-order law (3.2). The
concentration tendency is *the same $\beta>\gamma$ asymmetry that drives the
entire paper* — winner-take-all on the gain branch.

This is the crux: **A8 binds only when the uncued slots can reach the $1/N$
kink, which requires a large uncued budget *and* benefit-dominance ($r>1$).**
Proposition (b) shows those two conditions cannot co-occur at the model's own
optimum.

---

## 4. Proposition (b) — cued-absorption pre-empts every binding case

**Claim.** In any cell where the uncued subspace favours concentration
(accelerating $h$, or the benefit-dominant kink $r>1$), the joint optimum drives
$\alpha^\star\to1$, so $B=1-\alpha^\star\to0$ and the uncued split is
immaterial: $\mathcal V$ is the same all-on-cued policy whether or not A8 is
imposed.

**Mechanism (reusing C4 §6).** Two structural facts about where a unit of budget
earns the most:

1. **Value-weight inequality.** From C4 Eq. (6.4), $w_c\ge w_u$
   $\iff V\ge \tfrac{1}{(N-1)v+1}$, which for $v\ge1$ is implied by
   $V\ge1/N$, with equality only at the corner $(V=1/N,v=1)$. The cued slot is
   the most-valuable-or-equal location.
2. **Location-count asymmetry.** From C4 §6(a): at $\alpha\to1$ the *single*
   cued slot reaches the per-location ceiling $d'_{\max}$, whereas concentrating
   the uncued budget onto one winner can lift it to at most
   $d'_{\text{base}}+\beta[d'_{\max}f(B)-d'_{\text{base}}]<d'_{\max}$ (for any
   $B<1$), and the $N-1$ uncued must share what the cued holds alone.

A winner-take-all dynamic on the *gain* branch ($\beta$ large, $r>1$, or
$h$ accelerating) is exactly what makes a single high-$d'$ location beat several
mediocre ones — but ingredients 1–2 say the **cued** slot is the strictly better
recipient of that dynamic: higher (or equal) reward weight *and* a strictly
higher achievable $d'$. So whenever the asymmetry rewards creating a winner, the
cued slot wins the competition for the budget first. Formally, the marginal value
of the next unit of budget satisfies
$$
\left.\frac{\partial \mathbb E[R]}{\partial a_0}\right|_{\text{gain}}
=\beta\,d'_{\max}f'(a_0)\,M_0
\;\ge\;
\beta\,d'_{\max}f'(a_{\text{win}})\,M_{\text{win}}
=\left.\frac{\partial \mathbb E[R]}{\partial a_{\text{win}}}\right|_{\text{gain}},
\tag{4.1}
$$
because $M_0\ge M_{\text{win}}$ ($w_c\ge w_u$, and the cued sits nearer the
high-leverage part of its curve as it approaches $d'_{\max}$). C4's empirical
table (its §5) shows the consequence directly: under $V\ge1/N,v\ge1$,
$\alpha^\star$ rises monotonically toward $1$ as $r$ grows
($0.46\to0.66\to0.81\to0.96$ for $r=1.6\to10$ even at the *weakest* corner
$V{=}1/N,v{=}1$; faster for $v>1$).

**Numerical confirmation of the mutual exclusion** (verification block [V4] and
the $\Delta R$ table, run from scratch). Optimising jointly over $(\alpha,\text{uncued
winner share})$ at the headline-relevant cells, on the paper's $\Delta\alpha=0.005$
grid:

| $h$ | regime | $\alpha^\star$ | $B=1-\alpha^\star$ | winner share | $\Delta R=R_{\text{uncon}}-R_{\text{homog}}$ |
|---|---|---|---|---|---|
| $\sqrt a$ | C2-ref $v{=}5$, $r{\ge}2$ | $1.000$ | $0$ | — | $0$ |
| $\sqrt a$ | C1 corner $r{=}0.4$ | $0.26$ | $0.74$ | $\approx$homog | $-1.1\times10^{-4}$ |
| $a^2$ (worst for (a)) | every headline cell | $1.000$ | $0$ | — | $0$ exactly |
| $a^{0.3}$ | high-$V$ $v{=}5$, $r{=}10$ | $1.000$ | $0$ | $1.0$ | $+6.6\times10^{-13}$ |

Across **all four $h$ and all swept regimes**, $\max|\Delta R|=1.4\times10^{-4}$
(a coarse-winner-grid snap, *negative*), far below any headline-number
resolution. The decisive line: **for the accelerating $h=a^2$ — the only case
where proposition (a)'s smooth-branch $\lambda>0$ — cued-absorption is *total*
($\alpha^\star=1$, $B=0$ exactly), so $\Delta R=0$ exactly.** The two effects are
perfectly anti-correlated: the more $h$ accelerates (the more the uncued subspace
wants a winner), the harder the optimum drives $\alpha^\star\to1$ and empties the
uncued budget. A8 never binds at the model's own optimum.

---

## 5. Where A8 *does* bind — the conditional, made precise

Proposition (b) leaves exactly two residual regions, both outside the headline
claims' scope:

1. **The degenerate corner $V=1/N,\ v=1$.** Here $w_c=w_u$ (C4 Eq. 6.4 with
   equality), cued/uncued labels are meaningless (cf. CR-019), and at the forced
   kink $r>1$ the model is genuinely indifferent among single-winner policies.
   CR-036 saw a $+6.8\times10^{-4}$ blip here; it is value-blind ($v=1$) so it
   cannot touch any VDA / criterion-fraction number, and is within grid slack
   (resolution hygiene → CR-046). **Vacuous for C1–C5.**
2. **Heterogeneous uncued validity.** If the $N-1$ uncued slots have *unequal*
   target-validity, the exchange symmetry of §1 is broken and the equal split is
   no longer even a critical point. Relaxing A8 there produces a graded
   suppression of the low-validity (anti-cued) slot — CR-036 Part 2; the
   Wang & Theeuwes (2018) signature. This is a **scope enrichment, not a bias**:
   the paper's model is defined only for equal uncued validity, so C1–C5 are
   unaffected; the heterogeneous-validity model is a strictly larger object.

Hence the conditional on the verdict: A8 is innocuous for C1–C5 **conditional on
equal uncued validity** (and modulo the vacuous $V{=}1/N,v{=}1$ corner).

---

## 6. Refined statement of A8

> **A8 (refined).** Under equal uncued validity, homogeneous-uncued allocation
> is not merely an assumption but the *optimum* in the swept regimes, so it does
> not bias C1–C5. Two independent forces guarantee this. (i) **Homogeneity-
> optimality:** $\mathbb{E}[R]$ is a symmetric function of the uncued allocation,
> so the equal split is always a critical point; its restricted Hessian is a
> scalar $\lambda=\lambda_{\mathrm{HR}}+\lambda_{\mathrm{noFA}}$, and the
> correct-rejection term $\lambda_{\mathrm{noFA}}\le0$ unconditionally (log-
> concavity of $\Phi$), giving $\lambda<0$ — equal split is a strict local max —
> for the diminishing/linear transfer forms $a^{0.3},\sqrt a,a$. The only
> concentration pressures are the accelerating form $a^2$ (smooth-branch
> $\lambda>0$) and the benefit-dominant kink $r>1$ at a forced uniform budget
> (a *cusp* with one-sided slope $\propto\beta-\gamma$). (ii) **Cued-absorption
> pre-emption:** both concentration pressures are subsets of the winner-take-all
> regime, and by the value-weight inequality ($w_c\ge w_u$ under $V\ge1/N,v\ge1$)
> plus the location-count asymmetry (only the cued slot reaches $d'_{\max}$), the
> cued slot wins the budget first, driving $\alpha^\star\to1$ and $B\to0$ before
> any uncued concentration can act — fastest exactly for the accelerating $a^2$
> that most wanted to concentrate. Net effect on the headline numbers:
> $\max|\Delta R|=1.4\times10^{-4}$ across all four $h$ and all swept cells,
> within grid slack; $=0$ exactly for $a^2$. A8 binds only (a) at the degenerate
> value-blind $V=1/N,v=1$ corner (vacuous) and (b) under heterogeneous uncued
> validity (a scope enrichment, not a C1–C5 bias).

---

## 7. Summary table — verdict-relevant quantities

| Quantity | Value or expression |
|---|---|
| Equal-split critical point on $\Delta_B$ | always (exchange symmetry §1), exact $\forall r,h$ |
| Restricted Hessian | scalar $\lambda I$ ($S_{N-1}$ standard-rep irreducible, §2) |
| Closed-form $\lambda$ (smooth $\gamma$-branch) | $\lambda=\tfrac12\omega_u[\mathrm{HR}_{dd}g'^2+\mathrm{HR}_d g'']+Q[G(G_{dd}g'^2+G_d g'')-G_d^2 g'^2]$, Eq. (2.4) |
| no-FA term sign | $\lambda_{\mathrm{noFA}}=Q[G^2g'^2(\log G)''+GG_d g'']\le0$ for concave/linear $h$ (log-concavity of $\Phi$) |
| $\lambda$ sign by $h$ (smooth branch) | $a^{0.3},\sqrt a,a$: $\lambda<0$ (max); $a^2$: $\lambda>0$ (min) |
| Kink $\bar a=1/N$ (forced uniform budget) | cusp; one-sided slope $m$, $\operatorname{sign} m=\operatorname{sign}(\beta-\gamma)=\operatorname{sign}(r-1)$ |
| Cued-absorption | $\alpha^\star\to1\Rightarrow B\to0$; fastest for accelerating $h$ |
| $\max|\Delta R|$ (unconstrained $-$ homog), all $h$, swept cells | $1.4\times10^{-4}$ (grid-snap); $0$ exactly for $a^2$ |
| Residual binding region | $V{=}1/N,v{=}1$ corner (vacuous) + heterogeneous validity (scope, not bias) |
| Analytic $\lambda$ vs fixed-$c$ finite diff | agree to $<10^{-3}$ (5 d.p.), all $h,r$ — verification block (A) |

---

## 8. Connections to the broader critique

- **Mirror of the C4 location-count machinery.** Proposition (b) is C4 §6 run in
  the other direction: C4 used $w_c\ge w_u$ + location-count to forbid
  *inversion* ($\alpha^\star<1/N$); A8 uses the same two facts to force
  *absorption* ($\alpha^\star\to1$) and thereby empty the uncued budget. Both
  the no-inversion floor and the homogeneity-non-binding result are corollaries
  of the single inequality "the cued slot is the better recipient of attention
  under $V\ge1/N,v\ge1$."

- **Contrast with A3 (CONTESTED).** A3's $\beta\gamma=1$ swap *changed* a
  headline conjunct (criterion dominance) within the grid. A8's relaxation
  changes nothing within the grid ($\Delta R\le1.4\times10^{-4}$). The paper's
  *named* §5.5 limitation (A3) is the consequential one; its *unnamed* §2.2
  simplification (A8) is benign — because, uniquely among the assumptions, the
  optimiser would make A8's choice unprompted.

- **The log-concavity of $\Phi$ is the load-bearing analytic fact.** It is what
  makes the correct-rejection channel a pure spreading force
  ($\lambda_{\mathrm{noFA}}\le0$). The same property underwrites the uniqueness
  of the criterion optimum in C4/C5; here it is doing geometric work on the
  allocation simplex. Worth flagging as a recurring lever in this model class.

- **Implications for PRISM (§3.5).** PRISM's softmax allocation is the
  A8-*relaxed* model. The re-derivation sharpens the run-012 prediction into a
  decision rule: trained PRISM agents should spread uncued attention
  *homogeneously* in the swept regimes **because equal spreading is the optimum
  there**, and should break homogeneity into a single winner **only** if their
  learned transfer is accelerating (FiLM multiplicative gain is the relevant
  analogue, the $\beta\gamma=1$ side flagged in A3) *and* the cued slot has not
  already absorbed the budget — a corner the normative model says is empty. The
  cleanest PRISM falsification is the anti-cued (heterogeneous-validity)
  manipulation: §5 predicts a *graded* suppression that homogeneous A8 cannot
  represent.

---

*End of derivation. Numerical companion (independent of CR-036's `run.py`) in
`Critique/replications/A8--heterogeneous-uncued/cr045_rederivation_check/`
(`verify_curvature_and_absorption.py`, `verify_closedform_lambda_and_kink.py`,
and the `output/*.log` transcripts). Verdict file at
`Critique/verdicts/A8--heterogeneous-uncued.md` (Version 0.2).*
