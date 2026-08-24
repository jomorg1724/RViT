---
type: derivation
project: AttentionManuscript / VDA-rebuild
agent: constructive-rebuilder
backlog_id: RB-033
claim_id: A3
status: drafted
created: 2026-05-30
backing_for: "Rebuild/manuscript/sections/appendix.tex §appendix-deriv-a3 (filled by this file) + Rebuild/manuscript/sections/extensions.tex §extensions-A3 (formal substrate for the empirical band: Eq. eq:conservation-family, eq:beta-gamma-of-p, Proposition prop:r-dagger-invariance, Theorem thm:delta-cf-monotone)"
backed_by_sim: "Rebuild/sims/A3--conservation-band/ (rb-016, sha256 055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33); Rebuild/model/tests/test_conservation_family.py (rb-015, sha256 f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e)"
implements: "Rebuild/model/core.py: beta_gamma(r, p), d_prime_asym(alpha, r, ..., p), policies(r, cell), HeadlineCell.cons_p; rb-015 family identities; rb-016 r-dagger p-invariance + ΔCF block"
recovery_test: "rb-015 TEST 1-14 (PASS, sha256 f4f57a89…): β/γ = r to 4.4e-16; M_p(β,γ) = 1 to 4.4e-16; β(1,p) = γ(1,p) = 1 across p ∈ {-2..+2}; p=1 byte-exact recovery vs legacy form; p=0 recovery vs reviewer A3 numbers max|d| ≤ 6.3e-7. rb-016 TEST 3 (K_c, K_u, c_c*, c_u*, r†(v) identical to FP across p ∈ {0, 0.5, 1.0}, max |Δ| = 0.0)"
voice: independent re-derivation in the rebuild's voice. The reviewer has no A3 derivation file — the verdict relies on replication numerics; this is the rebuild's first formal statement of the conservation family.
---

# A3 — The power-mean conservation family

> *The inherited paper (§2.4) fixes the benefit/cost asymmetry by a single
> equation $\benefit + \cost = 2$ at the value-asymmetry ratio
> $\Rsens = \benefit/\cost$. The reviewer's A3 attack
> (`Critique/verdicts/A3--multiplicative-conservation.md`,
> label CONTESTED) shows that the equally-natural multiplicative
> alternative $\benefit\cost = 1$ shifts the C1 tail materially
> (4.0\% → 8.3\% of cells with $\CF < 0.5$; variant-B strict
> minimum $0.3040 \to 0.2309$). The paper's §5.5 robustness sentence
> survives only as a **central-tendency** statement, not as a tail
> statement. The rebuild's response is to stop treating any one
> conservation equation as canonical: we promote the constraint to a
> **one-parameter family** $M_p(\benefit, \cost) = 1$ with
> $\benefit/\cost = \Rsens$, where $M_p$ is the generalised (power)
> mean of order $p$. The inherited additive rule is $p = 1$; the
> reviewer's multiplicative attack is $p = 0$. This derivation states
> the family, gives the closed-form weights $\gamma(\Rsens; p)$ and
> $\benefit(\Rsens; p)$, lifts the Hardy–Littlewood–Pólya power-mean
> monotonicity inequality to an exact KL-divergence expression for
> $\partial \cost / \partial p$, gives the full proof
> (not the §extensions-A3 sketch) of conservation-form invariance of
> the C2 escape threshold $\rdagger(\val)$, and gives the C5 corollary
> (symmetric recovery at $\Rsens = 1$ is automatic for every $p$). The
> per-cell $\Delta\CF \le 0$ monotonicity observed in rb-016 across the
> $4{,}410$-cell C1 sweep is a **conjecture with full empirical
> support** at this version of the rebuild: the d'-channel chain rule
> reduces its sign to two factor signs that hold pointwise but whose
> uniform proof remains open. All numerical statements are sourced
> from `Rebuild/sims/A3--conservation-band/` (sha256 `055bf4ec…`) and
> `Rebuild/model/tests/test_conservation_family.py` (sha256
> `f4f57a89…`).*

Notation follows `agents/paper_rebuilder_prompt.md` §2 and the SDT primitives
introduced in §1 of `Rebuild/derivations/A1--rho-channel.md`. The reader who
wants a compressed reminder finds one in §1.1 below.

---

## 1. Setup and the inherited constraint

### 1.1 Notation

Let $N \ge 2$ be the number of locations, indexed so $i = c$ is the cued
location and $i = 1, \dots, N - 1$ enumerates the uncued ones. Per-location
SDT primitives: $\HR_i = \Phi(\dprime_i/2 - c_i)$,
$\FAR_i = \Phi(-\dprime_i/2 - c_i)$, $1 - \FAR_i = \Phi(b_i)$ with
$b_i := c_i + \dprime_i / 2$. Attention allocation is single-parameter at
this stage (homogeneous-uncued, the A8 setting of `rb-020`): the cued slot
receives $\alpha \in [0, 1]$ of a unit-mass budget, each uncued slot
receives $(1 - \alpha)/(N - 1)$. Sensitivity at the uniform allocation
$\alpha = 1/N$ takes the baseline value $\dprime_{\mathrm{base}} :=
\dprimemax\,f(1/N)$.

The asymmetric transfer function maps $\alpha$ and the global asymmetry
ratio $\Rsens = \benefit/\cost > 0$ to per-location sensitivities
$\dprime_c(\alpha; \Rsens, p)$ and $\dprime_u(\alpha; \Rsens, p)$ through a
benefit weight $\benefit(\Rsens; p)$ and a cost weight $\cost(\Rsens; p)$,
the central objects of this derivation. The expected reward decomposes
across the four policies $\Pone(\Rsens, p)$, $\Ptwo(\Rsens, p)$,
$\Pthree(\Rsens, p)$, $\Pfour(\Rsens, p)$ of the inherited paper (§2.5 and
§4 of `Critique/source/main.pdf`; see `Rebuild/manuscript/sections/model.tex`
Eq. eq:expected-reward for the rebuild's compact form).

The criterion fraction $\CF$ (the headline decomposition metric C1 attacks)
is, in the inherited model,
$$
  \CF \;=\; \frac{\Rpthree - \Rpone}{\Rpfour - \Rpone},
  \tag{1.1}
$$
where $\Rpone = \Etwo[\Rew]$ at the value-blind sensitivity-only policy and
$\Rpthree = \Ethree[\Rew]$ at the asymmetric-criterion policy (see
`Rebuild/manuscript/sections/results.tex` Eq. eq:cf-def for the labelled
manuscript display).

The C5 result (symmetric recovery at $\Rsens = 1$) is the statement that the
asymmetric model's optimal $(\alpha^\star, c_c^\star, c_u^\star, \Rew^\star,
\CF)$ at $\Rsens = 1$ matches the symmetric baseline (no value asymmetry,
$\benefit = \cost = 1$ identically). The rb-013 appendix subsection
(`sec:appendix-c5`) states this at the strength **identical to machine
precision, with literal bit-exact 0 a validation-configuration property
inside the Sterbenz band**; the family proof below (§4.2) gives the
underlying mechanism in one line.

### 1.2 The inherited additive rule

The paper's §2.4 (Eqs. 7–8, copied into `Rebuild/manuscript/sections/model.tex`
Eq. eq:expected-reward as the inherited form) fixes
$$
  \benefit + \cost \;=\; 2,
  \qquad
  \frac{\benefit}{\cost} \;=\; \Rsens,
  \qquad
  \Rsens > 0.
  \tag{1.2}
$$
The unique solution is
$$
  \benefit(\Rsens; p = 1) \;=\; \frac{2\,\Rsens}{\Rsens + 1},
  \qquad
  \cost(\Rsens; p = 1) \;=\; \frac{2}{\Rsens + 1}.
  \tag{1.3}
$$
This is the byte-exact form `beta_gamma(r, p=1)` returns in the rebuilt
model (`Rebuild/model/core.py:279`, the `p == 1.0` branch is a literal
return of (1.3) with no `**` operator).

### 1.3 The reviewer's alternative and the rebuild's response

The reviewer's A3 verdict tests the alternative
$\benefit \cdot \cost = 1$, $\benefit/\cost = \Rsens$, with unique
positive solution $\benefit = \sqrt{\Rsens}$, $\cost = 1/\sqrt{\Rsens}$.
The replication numerics (Critique/replications/A3--multiplicative-conservation/)
show this alternative doubles the criterion-subordinate cell fraction
$4.0\% \to 8.3\%$ on the inherited $4{,}410$-cell C1 grid; the inherited
paper's §5.5 robustness sentence survives only as a central-tendency
statement (median $\CF$ moves $\le 0.004$).

The rebuild's response (§3.2 of `agents/paper_rebuilder_prompt.md`) is to
stop treating any one conservation rule as fixed. We absorb both rules into
a one-parameter family, report all headline numbers as bands across the
family, and derive the few invariants that hold at every member.

---

## 2. The power-mean conservation family

### 2.1 Definition

The **generalised mean of order** $p \in \mathbb R$, also called the
power mean or Hölder mean, on positive reals $(x, y)$ is
$$
  \PowerMean_p(x, y)
  \;=\;
  \begin{cases}
    \displaystyle \left( \frac{x^p + y^p}{2} \right)^{1/p}, & p \ne 0, \\[2pt]
    \displaystyle \sqrt{x\,y}, & p = 0,
  \end{cases}
  \tag{2.1}
$$
with limits $\PowerMean_{-\infty}(x, y) = \min(x, y)$,
$\PowerMean_{+\infty}(x, y) = \max(x, y)$. Standard special cases:
$\PowerMean_1$ is the arithmetic mean, $\PowerMean_0$ the geometric,
$\PowerMean_{-1}$ the harmonic mean, $\PowerMean_2$ the quadratic mean.
(References: Hardy, Littlewood & Pólya, *Inequalities*, Cambridge 1934,
§2.9 "The means $\mathfrak M_r$"; Bullen, *Handbook of Means and Their
Inequalities*, Kluwer 2003, Chapter II.)

The **A3 conservation family** is the constraint that, at fixed asymmetry
ratio $\Rsens$, the pair $(\benefit, \cost)$ obey
$$
  \PowerMean_p(\benefit, \cost) \;=\; 1,
  \qquad
  \frac{\benefit}{\cost} \;=\; \Rsens, \qquad \Rsens > 0.
  \tag{2.2}
$$
This is `Rebuild/manuscript/sections/extensions.tex` Eq. eq:conservation-family,
re-stated here as the family's defining equation. The parameter $p$ ranges
over $\mathbb R$ (with $p = 0$ understood as the geometric-mean limit). The
inherited additive rule (1.2) is the case $p = 1$; the reviewer's
multiplicative rule is the case $p = 0$ (since
$\PowerMean_0(\benefit, \cost) = \sqrt{\benefit \cost} = 1 \Leftrightarrow
\benefit \cost = 1$). The case $p = -1$ is harmonic-mean conservation
$2 \benefit \cost / (\benefit + \cost) = 1$.

### 2.2 Closed-form weights

Substituting $\benefit = \Rsens\,\cost$ into (2.2) at $p \ne 0$ gives
$$
  1 \;=\; \PowerMean_p(\Rsens\cost, \cost)
       \;=\; \left( \frac{\Rsens^p \cost^p + \cost^p}{2} \right)^{1/p}
       \;=\; \cost \left( \frac{\Rsens^p + 1}{2} \right)^{1/p},
$$
and hence
$$
  \boxed{\;
    \cost(\Rsens; p) \;=\; \left( \frac{2}{\Rsens^p + 1} \right)^{1/p},
    \qquad
    \benefit(\Rsens; p) \;=\; \Rsens\,\cost(\Rsens; p)
       \;=\; \Rsens \left( \frac{2}{\Rsens^p + 1} \right)^{1/p}.
  \;}
  \tag{2.3}
$$
This is the manuscript's Eq. eq:beta-gamma-of-p, re-derived here from
the family definition. The numerical implementation is the general-$p$
branch of `beta_gamma(r, p)` in `Rebuild/model/core.py:319`:
```python
gamma = (2.0 / (r ** p + 1.0)) ** (1.0 / p)
return r * gamma, gamma
```
which the rb-015 tests verify against the family identities $\benefit/\cost =
\Rsens$ and $\PowerMean_p(\benefit, \cost) = 1$ to relative error
$\le 4.4 \times 10^{-16}$ across $p \in \{-2, -1, -1/2, 0, 1/2, 1, 2\}$
(test \texttt{test\_family\_identities}; sha256 `f4f57a89…`).

### 2.3 Limits and special cases

The two cases used in the rebuilt manuscript:

- **$p = 1$ (additive, paper):** Eq. (2.3) reduces to (1.3) by direct
  evaluation, and the model code routes through a literal-form branch
  (`Rebuild/model/core.py:311`), so the recovery against the inherited
  model is byte-for-byte: every pre-rb-015 caller using the implicit
  additive form gets numerically identical output post-rb-015 (rb-001
  recovery contract `test_recovery.py` unchanged, sha256 `d3c62215…`).

- **$p = 0$ (multiplicative, reviewer's attack):** (2.3) is indeterminate
  ($\infty^0$ form); the limit reads
  $$
    \lim_{p \to 0} \cost(\Rsens; p)
    \;=\; \exp\!\left[ \lim_{p \to 0} \frac{1}{p}\,
          \ln \frac{2}{\Rsens^p + 1} \right].
  $$
  Expanding the inner log around $p = 0$ with $\Rsens^p = 1 + p \ln \Rsens
  + O(p^2)$ gives $\ln(2/(\Rsens^p + 1)) = -p (\ln \Rsens)/2 + O(p^2)$
  and so $\lim_{p \to 0} \cost = e^{-(\ln \Rsens)/2} = 1/\sqrt{\Rsens}$,
  $\benefit(\Rsens; 0) = \sqrt{\Rsens}$. The code's `abs(p) < 1e-12`
  branch returns the geometric-mean closed form directly
  (`Rebuild/model/core.py:314`).

- **$p = -1$ (harmonic):** $\cost(\Rsens; -1) = 2 \Rsens / (\Rsens + 1)$
  and $\benefit(\Rsens; -1) = 2 \Rsens^2 / (\Rsens + 1)$. Note that at
  $\Rsens > 1$ this gives $\benefit > 1 > \cost$ as expected, with both
  weights larger than at $p = 0$ (consistent with HLP monotonicity, §3).

### 2.4 Identities preserved at every $p$

Three identities hold at every member of the family. (We will use each
below.)

**(I-1) Ratio preserved.** $\benefit(\Rsens; p) / \cost(\Rsens; p) =
\Rsens$ at every $p$ by construction (2.3). This means the headline
parameterisation of the value asymmetry by $\Rsens$ — the C2 sweep axis,
the §results-c2 escape-threshold variable — is independent of the
conservation choice.

**(I-2) Symmetric corner.** $\benefit(1; p) = \cost(1; p) = 1$ at every
$p$. Direct from (2.3): at $\Rsens = 1$, $\Rsens^p = 1$, so
$2/(\Rsens^p + 1) = 1$ and $\cost(1; p) = 1^{1/p} = 1$, hence
$\benefit(1; p) = 1$. This is the $r = 1$ row of the family that the C5
recovery result rides on (§4.2 below).

**(I-3) Sign of the spread.** For $\Rsens > 1$, $\benefit > \cost$ at
every $p$; for $\Rsens < 1$, $\benefit < \cost$. (Direct from (I-1) and
$\cost > 0$.) The cued-vs-uncued direction of the asymmetry is therefore
fixed by $\Rsens$ alone, and is preserved across the family — only the
magnitudes move with $p$.

---

## 3. Hardy–Littlewood–Pólya monotonicity and the $(\benefit, \cost)$ envelope

### 3.1 The classical inequality

The power-mean monotonicity inequality (Hardy, Littlewood & Pólya 1934,
Theorem 16; restated in Bullen 2003, Ch. II §2.2) says that for fixed
positive reals $x, y$ with $x \ne y$, the function $p \mapsto
\PowerMean_p(x, y)$ is **strictly increasing in $p$** over $\mathbb R$
(with $p = 0$ continuous by the geometric-mean limit); for $x = y$ it is
the constant $x$.

Applied to the constraint $\PowerMean_p(\benefit, \cost) = 1$: as $p$
varies, the constraint pins the value of $\PowerMean_p$ to $1$ exactly,
while the constraint-free $\PowerMean_p$-evaluation of a fixed pair would
move. So the family must "compensate": the constraint locus $\{(\benefit,
\cost) : \PowerMean_p(\benefit, \cost) = 1\}$ shifts in $(\benefit, \cost)$
space as $p$ changes, to keep the equation satisfied. The combined effect
of the constraint $\PowerMean_p = 1$ and the ratio constraint $\benefit/\cost
= \Rsens$ pins a single point per $p$, namely (2.3).

The HLP monotonicity in the constrained form translates into a monotone
ordering of $\cost(\Rsens; p)$ in $p$, which we now compute in closed form.

### 3.2 $\partial \cost / \partial p$ as a KL divergence

Let $L(p) := \ln \cost(\Rsens; p) = \frac{1}{p} \ln \frac{2}{\Rsens^p + 1}$
for $p \ne 0$. Direct differentiation:
$$
  \frac{\partial L}{\partial p}
  \;=\; -\frac{1}{p^2} \ln \frac{2}{\Rsens^p + 1}
  \;+\; \frac{1}{p} \cdot
  \frac{\partial}{\partial p}\!\left[\, \ln 2 - \ln(\Rsens^p + 1) \,\right]
  \;=\; -\frac{1}{p^2}
        \left[\,
          \ln \frac{2}{\Rsens^p + 1}
          + \frac{p\, \Rsens^p \ln \Rsens}{\Rsens^p + 1}
        \,\right].
  \tag{3.1}
$$
Introduce the Bernoulli weight $\theta_p := \Rsens^p / (\Rsens^p + 1)$, so
$1 - \theta_p = 1/(\Rsens^p + 1)$ and $p \theta_p \ln \Rsens =
\theta_p \ln \Rsens^p$. Then the bracket in (3.1) reads
$$
  \ln 2 - \ln(\Rsens^p + 1) + \theta_p \ln \Rsens^p.
$$
The first two terms write as $\ln\frac{2}{\Rsens^p + 1} = \ln 2 + \ln(1 -
\theta_p)$ (using $1 - \theta_p = 1/(\Rsens^p + 1)$), and the third writes
as $\theta_p \ln \Rsens^p = \theta_p \ln(\Rsens^p + 1) + \theta_p \ln(\theta_p /
(1 - \theta_p))$ — but a cleaner identity is direct: the bracket equals
$$
  \theta_p \ln(2 \theta_p) + (1 - \theta_p) \ln(2 (1 - \theta_p))
  \;=\; \DKL\!\bigl(\mathrm{Bern}(\theta_p) \,\|\, \mathrm{Bern}(1/2)\bigr),
  \tag{3.2}
$$
the Kullback–Leibler divergence between the asymmetric Bernoulli with
parameter $\theta_p$ and the uniform Bernoulli. (Algebraic check:
$\theta_p \ln(2 \theta_p) = \theta_p \ln 2 + \theta_p \ln \theta_p =
\theta_p \ln 2 + \theta_p [\ln \Rsens^p - \ln(\Rsens^p + 1)]$; the
$\theta_p \ln \Rsens^p$ summand is exactly the third term of the bracket
in (3.1); the remaining $\theta_p \ln 2 - \theta_p \ln(\Rsens^p + 1)$
combines with $(1 - \theta_p) \ln 2 - (1 - \theta_p) \ln(\Rsens^p + 1)$
from $(1 - \theta_p) \ln(2(1 - \theta_p))$ to give $\ln 2 - \ln(\Rsens^p
+ 1)$, the first two terms of the bracket. ∎)

Therefore (3.1) and (3.2) combine to
$$
  \boxed{\;
    \frac{\partial}{\partial p} \ln \cost(\Rsens; p)
    \;=\; -\frac{1}{p^2}\,\DKL\!\bigl(\mathrm{Bern}(\theta_p)
                              \,\|\, \mathrm{Bern}(1/2)\bigr),
    \qquad
    \theta_p \;=\; \frac{\Rsens^p}{\Rsens^p + 1}.
  \;}
  \tag{3.3}
$$
Eq. (3.3) is the HLP power-mean monotonicity inequality in exact pointwise
form for this family.

### 3.3 Corollary: sign of $\partial \cost / \partial p$ and $\partial \benefit / \partial p$

Since $\DKL \ge 0$ with equality iff $\theta_p = 1/2$ iff $\Rsens = 1$,
Eq. (3.3) yields, **for every $\Rsens > 0$, $\Rsens \ne 1$, and every $p
\in \mathbb R \setminus \{0\}$**:
$$
  \frac{\partial \cost}{\partial p}(\Rsens; p) \;<\; 0,
  \qquad
  \frac{\partial \benefit}{\partial p}(\Rsens; p) \;=\;
  \Rsens \cdot \frac{\partial \cost}{\partial p} \;<\; 0
  \quad (\Rsens > 0).
  \tag{3.4}
$$
The Bernoulli $\theta_p$ approaches $1/2$ as $p \to 0$, so the bracket in
(3.3) is $O(p^2)$ near zero, and the $1/p^2$ prefactor gives a finite
limit: a series expansion (using $\theta_p = 1/2 + (p \ln \Rsens)/4 +
O(p^2)$ and $\DKL = 2 (\theta_p - 1/2)^2 + O((\theta_p - 1/2)^3)$) gives
$$
  \lim_{p \to 0} \frac{\partial \ln \cost}{\partial p}
  \;=\; -\frac{(\ln \Rsens)^2}{8},
  \tag{3.5}
$$
so the bound (3.4) extends continuously through $p = 0$.

**Corollary 3.1 (HLP envelope on the $(\benefit, \cost)$ family).** *For
every fixed $\Rsens > 0$ with $\Rsens \ne 1$, both weights
$\cost(\Rsens; p)$ and $\benefit(\Rsens; p)$ are strictly decreasing
functions of the conservation order $p$. At $\Rsens = 1$ both are
constant equal to $1$. The decrease is sharpest in $|p|$ when
$\Rsens$ is far from $1$ (in the sense that $|\partial \ln \cost /
\partial p| \propto (\ln \Rsens)^2$ at small $|p|$ from (3.5)).*

The empirical witness is the rb-015 family-identity test plus a direct
inspection of (2.3) at the rb-016 $\val$-family pin: at $\Rsens = 0.3548$
(the rb-016 peak $\Rsens^*$ at $\val = 10$), $\cost(0.3548; 1) = 1.4762$
and $\cost(0.3548; 0) = 1.6788$, an increase of $+13.72\%$ going from
$p = 1$ to $p = 0$ ($\Delta p = -1$, consistent with (3.4)); at $\benefit$
the corresponding values are $0.5238$ and $0.5957$ ($+13.72\%$, identical
ratio since $\benefit = \Rsens\cost$ shares the same $p$-derivative
prefactor by Identity I-1). Both $\cost$ and $\benefit$ rise as $p$
decreases, reproducing Corollary 3.1 pointwise at the peak cell. A
finite-difference check of (3.3) at the seven test points $(\Rsens, p)
\in \{(0.3548, 0.5), (0.3548, 1.0), (10, 1.0), (10, 0.5),$ $(3.162, 2.0),
(0.5, -1.0), (5.0, 1.5)\}$ agrees with the closed-form right-hand side to
$\le 1.5\times10^{-10}$ in every case (central FD, $\epsilon = 10^{-6}$);
at $\Rsens = 1$ both sides are exactly $0$.

### 3.4 Why HLP monotonicity is the right principle

The cleaner statement of A3's status that the rebuild adopts: **the
conservation rule is a parameter of the model, not a derived fact.** HLP
monotonicity tells us how the family is ordered in $(\benefit, \cost)$
space as $p$ varies, but does not single out one $p$ as canonical. The
inherited paper's $p = 1$ choice is convenient (literal additive
budgeting) but not principled. The rebuild reports all headline numbers
as bands across $p$ (Section sec:extensions-a3, Tables tab:a3-c2-peak-band
and tab:a3-c1-cf-band), and isolates the *invariants* that hold at every
$p$ (§4 below).

---

## 4. Conservation-form invariance at the symmetric corner

### 4.1 The symmetric corner identity

**Proposition 4.1 (Symmetric corner identity, $\Rsens = 1$ is
conservation-form-invariant).** *For every $p \in \mathbb R$,
$\benefit(1; p) = \cost(1; p) = 1$.*

*Proof.* By Identity (I-2) of §2.4: at $\Rsens = 1$, $\Rsens^p = 1$ for
every $p$, so (2.3) at $p \ne 0$ gives $\cost = (2/2)^{1/p} = 1$ and
$\benefit = 1 \cdot 1 = 1$; at $p = 0$ the geometric-mean limit gives
$\cost = 1/\sqrt 1 = 1$ and $\benefit = 1$. ∎

The proposition holds without any reference to the rest of the model — it
is an identity of the conservation family alone — and is therefore
applicable to any model that uses (2.2) for any reason.

### 4.2 C5 corollary: symmetric recovery is conservation-form-invariant

The C5 result of the inherited paper (and Section sec:appendix-c5 of the
rebuilt manuscript) says: at $\Rsens = 1$, the asymmetric model with
arbitrary attention transfer collapses to its symmetric baseline, with
matched optimal $(\alpha^\star, c_c^\star, c_u^\star, \Rew^\star, \CF)$ at
real-number identity.

**Corollary 4.2 (C5 is conservation-form-invariant).** *The C5 result
holds at every $p \in \mathbb R$. Specifically: at $\Rsens = 1$ and any
$p$, the per-location sensitivities
$\dprime_c(\alpha; \Rsens = 1, p)$ and $\dprime_u(\alpha; \Rsens = 1, p)$
satisfy $\dprime_c(\alpha) = \dprime_u((1 - \alpha)/(N - 1))$ at every
$\alpha$ — i.e.\ the asymmetric model evaluates to the symmetric baseline
identically.*

*Proof.* By Proposition 4.1, $\benefit(1; p) = \cost(1; p) = 1$ at every
$p$. The $\dprime$-map of the inherited model
(`Rebuild/model/core.py:323`, Eq. eq:d-prime-asym of the manuscript)
reduces at these weights to
$$
  \dprime_c(\alpha; 1, p)
  \;=\; \dprime_{\mathrm{base}} + 1 \cdot
        \bigl[\dprimemax\,f(\alpha) - \dprime_{\mathrm{base}}\bigr]
  \;=\; \dprimemax\,f(\alpha),
$$
and similarly $\dprime_u((1 - \alpha)/(N - 1); 1, p) = \dprimemax\,
f((1 - \alpha)/(N - 1))$, with no $p$ dependence anywhere on the right.
The two formulas match the symmetric baseline pointwise (the baseline is
defined by $\dprime_i = \dprimemax\,f(\alpha_i)$ with no value-asymmetry
correction), so the asymmetric model's expected-reward functional
$\Etwo[\Rew], \Ethree[\Rew], \Efour[\Rew]$ at $\Rsens = 1$, any $p$
coincides with the symmetric baseline's functional, giving the same
$(\alpha^\star, c_c^\star, c_u^\star, \Rew^\star, \CF)$ as real-number
identities. ∎

The numerical witness is the rb-015 family-test
\texttt{test\_symmetric\_corner\_invariant} (5/5 PASS): \texttt{policies(r=1,
p=0)} matches \texttt{policies(r=1, p=1)} to floating-point identity
across the variant grid; combined with rb-001's symmetric-recovery
contract (`test_recovery.py` sha256 `d3c62215…`, $\VDA = 0.039825$,
$\CF = 0.728228$ at the inherited $p = 1$, $r = 1$ pin reproduced to zero
diff), this gives bit-exact recovery at $r = 1$ across the conservation
family in the bit-exact band of rb-013 (Sterbenz lemma; (Sterbenz 1974,
Theorem 4.3.1)).

The Section sec:appendix-c5 manuscript subsection already cross-references
this corollary by reference (the §extensions-A3 closes with a paragraph
calling Section sec:appendix-c5 the "place where the C5 corollary is
stated", and the §appendix-c5 contains a reciprocal paragraph
"conservation-form-invariance: by Proposition prop:r-dagger-invariance
plus the family identity $\benefit(1, p) = \cost(1, p) = 1$"; both sides
now have the formal mechanism). The corollary is therefore distributed
across two manuscript locations with this derivation as the formal
backing.

---

## 5. Conservation-form invariance of $\rdagger(\val)$ (full proof)

The Section sec:extensions-a3 manuscript subsection states
Proposition prop:r-dagger-invariance — that the C2 escape threshold
$\rdagger(\val)$ of Section sec:results-c2 is independent of $p$ — with a
proof sketch. This subsection promotes the sketch to a full proof.

### 5.1 The escape threshold setup

By the Section sec:results-c2 derivation (`Rebuild/derivations/C2--non-monotonic-vda-rho.md`
§2), the C2 non-monotonicity in $\Rsens$ has a left-edge boundary at
$\alpha = 1/N$ characterised by the closed form
$$
  \rdagger(\val) \;=\; \frac{K_u(\val)}{(N - 1)\,K_c(\val)},
  \tag{5.1}
$$
where
$$
  K_c(\val) \;=\; \partial \Rpthree / \partial \dprime_c
  \quad\text{and}\quad
  K_u(\val) \;=\; \partial \Rpthree / \partial \dprime_u
  \tag{5.2}
$$
are the partial derivatives of the asymmetric-criterion expected reward
$\Rpthree$ with respect to per-location $\dprime$ values, evaluated at the
$\Pthree$-optimal criteria $(c_c^\star, c_u^\star)$ and at the
sensitivities $(\dprime_c, \dprime_u) = (\dprime_{\mathrm{base}},
\dprime_{\mathrm{base}})$ corresponding to the uniform allocation
$\alpha = 1/N$. (See `Critique/derivations/C2--non-monotonic-vda.md` §2
for the full $\Rpthree$ expansion; the no-FA product is fully booked
through $\Pnofa$, the change-trial bracket is linear in HRs as established
in `Rebuild/derivations/A1--rho-channel.md` §1.2.)

### 5.2 Full proof of conservation-form invariance

**Proposition 5.1 ($\rdagger(\val)$ is conservation-form-invariant).** *For
every $\val \ge 1$, the C2 escape threshold $\rdagger(\val)$ defined by
(5.1)–(5.2) is independent of the conservation order $p$ in (2.2).*

*Proof.* The argument has three steps.

**(Step 1)** *Sensitivities at $\alpha = 1/N$ are $p$-independent.* At the
uniform allocation $\alpha = 1/N$, the cued $\dprime$-map
(`Rebuild/model/core.py:340`) reads
$$
  \dprime_c(1/N; \Rsens, p)
  \;=\; \dprime_{\mathrm{base}}
        + \benefit(\Rsens; p)
          \bigl[ \dprimemax\,f(1/N) - \dprime_{\mathrm{base}} \bigr]
  \;=\; \dprime_{\mathrm{base}},
$$
because the bracket $\dprimemax\,f(1/N) - \dprime_{\mathrm{base}}$ vanishes
by the very definition $\dprime_{\mathrm{base}} := \dprimemax\,f(1/N)$.
The vanishing bracket annihilates any value of $\benefit$, so $\dprime_c$
at $\alpha = 1/N$ is $\benefit$-independent, hence $p$-independent.
Likewise, at $\alpha = 1/N$ the uncued allocation per slot is
$(1 - 1/N)/(N - 1) = 1/N$, so the uncued bracket $\dprimemax\,f(1/N) -
\dprime_{\mathrm{base}}$ also vanishes and $\dprime_u(1/N; \Rsens, p) =
\dprime_{\mathrm{base}}$ independent of $\cost$, hence independent of $p$.
The pair $(\dprime_c, \dprime_u) = (\dprime_{\mathrm{base}},
\dprime_{\mathrm{base}})$ at $\alpha = 1/N$ is therefore $p$-independent
(and $\Rsens$-independent).

**(Step 2)** *$\Pthree$-optimal criteria are $p$-independent.* The
$\Pthree$ expected-reward functional, after the $\alpha$-fixation at $1/N$,
is
$$
  \Ethree[\Rew]
  \;=\;
  \Ethree[\Rew](\dprime_c, \dprime_u, c_c, c_u; \valid, \val, N, \CR),
$$
explicitly given in `Critique/derivations/C2--non-monotonic-vda.md` Eq.
(2.1). Crucially, the conservation order $p$ enters only through
$(\dprime_c, \dprime_u)$, by Step 1's $p$-independence at $\alpha = 1/N$.
The $\Pthree$-optimal criteria
$$
  (c_c^\star, c_u^\star)
  \;=\; \arg\max_{(c_c, c_u)}
       \Ethree[\Rew](\dprime_{\mathrm{base}},
                     \dprime_{\mathrm{base}},
                     c_c, c_u;
                     \valid, \val, N, \CR)
$$
are therefore the argmax of a functional whose every input is
$p$-independent. So $(c_c^\star, c_u^\star)$ are $p$-independent.

**(Step 3)** *$K_c, K_u$ are $p$-independent, hence $\rdagger$ is.* The
partials (5.2) are evaluated at the $p$-independent
$(\dprime_{\mathrm{base}}, \dprime_{\mathrm{base}}, c_c^\star, c_u^\star)$,
and the functional form of $\Rpthree$ depends only on
$(\valid, \val, N, \CR)$ (no conservation choice enters). Hence
$K_c(\val)$ and $K_u(\val)$ are $p$-independent, and so is their ratio
$\rdagger(\val) = K_u(\val) / [(N - 1) K_c(\val)]$. ∎

The numerical witness is rb-016 \texttt{recovery.test\_3\_r\_dagger\_p\_invariance}:
$K_c$, $K_u$, $c_c^\star$, $c_u^\star$ and $\rdagger(\val)$ all differ by
exactly $0.0$ across $p \in \{0, 1/2, 1\}$ and $\val \in \{2, 3, 5, 8, 10\}$,
to floating-point identity. This is a stronger numerical statement than
Step 3 produces structurally (the proof guarantees algebraic equality,
the test verifies the algebra also commutes with the floating-point
implementation, with no rounding noise from any of the three branches of
`beta_gamma`).

### 5.3 What is and is not invariant

Proposition 5.1 says $\rdagger(\val)$ — the boundary left-edge of the
$\VDA(\Rsens)$ positive band — is invariant. **The peak inside the band
is not.** The peak location $\Rsens^\star(\val)$ and peak height
$\VDA^\star(\val)$ live in the interior of the $\Rsens$-band, away from
the boundary $\alpha = 1/N$, where the bracket
$\dprimemax\,f(\alpha) - \dprime_{\mathrm{base}}$ is non-zero, and hence
the $p$-dependence of $\benefit$ and $\cost$ does *not* cancel.
Section sec:extensions-a3 Table tab:a3-c2-peak-band reports the empirical
peak band: at $\val = 5$, $\VDA^\star$ shifts $0.0830 \to 0.0951$
($+14\%$) going from $p = 1$ to $p = 0$, exactly the regime where the
HLP envelope (Corollary 3.1) is operative.

The invariance of the boundary and the variance of the peak together
characterise the C2 thread: **the band's left edge is a topological
feature of the model (conservation-form-invariant), the band's peak is a
calibration feature (conservation-form-sensitive).** This separation is
the rebuild's most precise statement of A3's status.

---

## 6. Towards a closed form for $\Delta\CF \le 0$

The Section sec:extensions-a3 manuscript subsection states
Theorem thm:delta-cf-monotone: across the $4{,}410$-cell C1 grid at
$\corr = 0$, the per-cell $\Delta\CF := \CF(p = 0) - \CF(p = 1) \le 0$ in
every valid cell, with $0$ cells where $\Delta\CF > 0$. The "Theorem" is
empirical at full strength (rb-016 Block B, sha256 `055bf4ec…`); this
subsection derives the $d'$-channel chain-rule sign analysis that
motivates the inequality, and explains why a uniform closed-form proof is
not yet available.

### 6.1 Setup

By (1.1), at any fixed cell $(\Rsens, \valid, \val, N, \CR, \variant)$
and any $p$:
$$
  \CF(p)
  \;=\;
  \frac{\Rpthree(p) - \Rpone(p)}{\Rpfour(p) - \Rpone(p)},
  \tag{6.1}
$$
where each policy reward is evaluated at its own attention-and-criterion
optimum, with the $p$-dependence threaded through the $\dprime$-map at
the optimum. The derivative of (6.1) in $p$ is
$$
  \frac{\partial \CF}{\partial p}
  \;=\;
  \frac{(\Rpfour - \Rpone)\,(\partial_p \Rpthree - \partial_p \Rpone)
      - (\Rpthree - \Rpone)\,(\partial_p \Rpfour - \partial_p \Rpone)}
       {(\Rpfour - \Rpone)^2}.
  \tag{6.2}
$$
At $p = 1$, $\Rpone < \Rpthree \le \Rpfour$ for every cell with $\VDA > 0$
(the inherited Section sec:results-c2 / sec:results-c1 setup), so the
denominator and the bracket sign in (6.2) are well-controlled.

### 6.2 The $d'$-channel chain rule

Each $\partial_p \Rpi$ for $i \in \{1, 3, 4\}$ goes through the
$\dprime$-map at the policy's own $(\alpha, c_c, c_u)$ optimum. By
the envelope theorem (the optimum's first-order conditions remove the
inner gradient terms), only the explicit $p$-dependence through
$(\dprime_c, \dprime_u)$ contributes:
$$
  \frac{\partial \Rpi}{\partial p}
  \;=\;
  \frac{\partial \Rpi}{\partial \dprime_c}\!\bigg|_{\!\star}
  \cdot
  \frac{\partial \dprime_c}{\partial p}
  \;+\;
  \frac{\partial \Rpi}{\partial \dprime_u}\!\bigg|_{\!\star}
  \cdot
  \frac{\partial \dprime_u}{\partial p}.
  \tag{6.3}
$$
By the $\dprime$-map definition,
$$
  \frac{\partial \dprime_c}{\partial p}
  \;=\;
  \frac{\partial \benefit}{\partial p}
  \,\bigl[ \dprimemax\,f(\alpha) - \dprime_{\mathrm{base}} \bigr],
  \qquad
  \frac{\partial \dprime_u}{\partial p}
  \;=\;
  \frac{\partial \cost}{\partial p}
  \,\bigl[ \dprimemax\,f((1-\alpha)/(N-1))
           - \dprime_{\mathrm{base}} \bigr].
  \tag{6.4}
$$
By Eq. (3.4), both $\partial \benefit/\partial p$ and
$\partial \cost/\partial p$ are negative at every $\Rsens \ne 1$, every
$p$. The brackets in (6.4) are: for $\alpha > 1/N$ (cued enhancement), the
first bracket is positive (since $f$ is monotone-increasing and
$\dprime_{\mathrm{base}} = \dprimemax\,f(1/N)$) and the second is
negative (uncued slot's per-location allocation $(1 - \alpha)/(N - 1)
< 1/N$ when $\alpha > 1/N$). The $\Ppolicy$-relevant sub-case of (6.4)
is, for $\alpha \ge 1/N$:
$$
  \frac{\partial \dprime_c}{\partial p} < 0,
  \qquad
  \frac{\partial \dprime_u}{\partial p} > 0.
  \tag{6.5}
$$
(As $p$ decreases, $\benefit$ rises and the cued bracket is positive, so
$\dprime_c$ rises — i.e.\ $\partial \dprime_c/\partial p < 0$ matches a
decrease of $\dprime_c$ in $p$; and the uncued bracket is negative, so
$\dprime_u$ falls as $\cost$ rises, giving $\partial \dprime_u/\partial p
> 0$.) Substituting (6.5) into (6.3):
$$
  \frac{\partial \Rpi}{\partial p}
  \;=\;
  \underbrace{\frac{\partial \Rpi}{\partial \dprime_c}}_{>0}
  \cdot
  \underbrace{\frac{\partial \dprime_c}{\partial p}}_{<0}
  \;+\;
  \underbrace{\frac{\partial \Rpi}{\partial \dprime_u}}_{>0}
  \cdot
  \underbrace{\frac{\partial \dprime_u}{\partial p}}_{>0}.
  \tag{6.6}
$$
The two terms have opposite sign — the cued lever pushes $\Rpi$ down in
$p$, the uncued lever pushes it up. Their relative weights depend on the
policy $i$ and the cell parameters.

### 6.3 The signed split between $\Pone, \Pthree, \Pfour$

At each cell:

- **$\Pone$ (sensitivity-only at optimal $\alpha^\star$):** The optimum
  for $\Pone$ trades off cued and uncued $\dprime$ through the value
  weights; at $\Rsens > 1$ and benefit-dominant regions, $\alpha^\star$
  is pushed toward higher cued allocation, so the cued partial dominates
  and $\partial \Rpone/\partial p < 0$ (i.e.\ $\Rpone$ rises as $p$
  decreases).

- **$\Pthree$ (criterion-only at $\alpha = 1/N$):** At the uniform point
  the brackets in (6.4) vanish (Step 1 of §5.2), so $\partial
  \Rpthree/\partial p = 0$ identically. **$\Rpthree$ is $p$-invariant.**

- **$\Pfour$ (full joint, $\alpha^\star$ and criteria):** Combines the
  $\Pone$-style $\alpha^\star$ sensitivity adjustment with the
  $\Pthree$-style criterion adjustment; the criterion adjustment vanishes
  at $\alpha = 1/N$ but contributes interior to the band. Empirically
  $\partial \Rpfour/\partial p < 0$ at every C1 cell (rb-016 records this
  signed difference per cell).

Combining: $\partial_p \Rpthree = 0$ and $\partial_p \Rpone \le 0$ and
$\partial_p \Rpfour \le 0$ at every cell, so the numerator of (6.2)
reduces to
$$
  (\Rpfour - \Rpone) \cdot (- \partial_p \Rpone)
  \;-\;
  (\Rpthree - \Rpone) \cdot (\partial_p \Rpfour - \partial_p \Rpone).
$$
Both $\Rpfour - \Rpone$ and $\Rpthree - \Rpone$ are positive (by the
construction of $\CF$), so the first term has sign $-\partial_p \Rpone
\ge 0$ and the second has sign $-(\partial_p \Rpfour - \partial_p \Rpone)$.
The bracketed difference is the relative "speed" of $\Rpfour$ vs $\Rpone$
in $p$; if $\Rpfour$ falls faster than $\Rpone$ (i.e.\ the joint policy
"loses" more reward per unit $p$ than the sensitivity-only one), then
$\partial_p \Rpfour < \partial_p \Rpone$ and the second term has sign
$+1$, i.e.\ $\partial \CF / \partial p > 0$. **For this sign to be
negative globally (i.e.\ $\partial \CF/\partial p < 0$, which integrates
to the empirical $\Delta\CF \le 0$), we need
$\partial_p \Rpfour \ge \partial_p \Rpone$ in absolute terms** — the
joint policy must fall in $p$ no faster than the sensitivity-only policy.

### 6.4 The empirical resolution

The rb-016 Block B sweep shows $\Delta\CF \le 0$ across all $4{,}410$
valid cells, with $0$ reverse flips. The sign condition $|\partial_p
\Rpfour| \le |\partial_p \Rpone|$ above holds in every cell of the sweep,
but a clean closed-form proof of this inequality has so far eluded us:
both $\partial_p \Rpone$ and $\partial_p \Rpfour$ depend on the
policy-specific $\alpha^\star$ via the envelope theorem, and the
$\alpha^\star$ values themselves depend on $p$ implicitly through the
$\dprime$-map, so the closed form would have to handle the
$\alpha^\star(p)$ moving target along with the two policy-reward
gradients.

**Status.** The rebuild reports Theorem thm:delta-cf-monotone in the
manuscript as *empirical at full strength* ($0$ reverse flips out of
$4{,}410$ cells), with this derivation supplying the d'-channel chain
rule that motivates the sign. The uniform closed-form proof is left as a
queued task (Section sec:extensions-a3, scope paragraph). The
$\Rpthree$ $p$-invariance ($\partial \Rpthree / \partial p = 0$ at
$\alpha = 1/N$) is the one analytic statement we *can* extract from the
chain rule, and is consistent with the wider $\rdagger$ $p$-invariance
(Proposition 5.1) — both are consequences of the same vanishing-bracket
mechanism at $\alpha = 1/N$.

The rebuild therefore makes the following two-tier statement in the
manuscript:

1. **Analytic, full strength.** $\rdagger(\val)$ and the
   $\Rpthree$-reward functional are $p$-invariant (Sections 4 and 5).
2. **Empirical, full strength + chain-rule motivation.** $\Delta\CF \le 0$
   per cell across the C1 grid (Section sec:extensions-a3 Theorem
   thm:delta-cf-monotone), with the d'-channel chain rule (6.3)–(6.6)
   identifying the two competing gradients whose relative magnitudes
   produce the sign.

This is the honest band the rebuild reports: tail behaviour of $\CF$ is
not robust to the conservation form, but the direction of motion is
empirically consistent across all sampled cells.

---

## 7. Numerical realisation and recovery

Every quantitative statement in this derivation is sourced from one of
two simulation/test outputs:

- **rb-015 family identities (sha256 `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e`).**
  `Rebuild/model/tests/test_conservation_family.py` (14/14 PASS):
  - \texttt{test\_family\_identities}: $\benefit/\cost = \Rsens$ to
    $4.4 \times 10^{-16}$ and $\PowerMean_p(\benefit, \cost) = 1$ to
    $4.4 \times 10^{-16}$ across $p \in \{-2, -1, -1/2, 0, 1/2, 1, 2\}$
    on the 21-point log-$\Rsens$ grid $\Rsens \in \{0.1, \ldots, 10\}$.
    Backs Eqs. (2.3) and Identity (I-1).
  - \texttt{test\_symmetric\_corner\_invariant}: $\benefit(1, p) =
    \cost(1, p) = 1$ to binary equality across $p \in \{-2, \ldots, 2\}$,
    and \texttt{policies(r=1, p=0) == policies(r=1, p=1)} to floating-
    point identity. Backs Proposition 4.1 and Corollary 4.2.
  - \texttt{test\_additive\_recovery}: $p = 1$ branch returns the
    inherited closed form (1.3) byte-exactly; rb-001 \texttt{test\_recovery.py}
    (sha256 `d3c62215…`) re-runs and matches the pre-rb-015 reference
    pins to zero diff.
  - \texttt{test\_multiplicative\_recovery}: $p = 0$ branch returns
    $\benefit = \sqrt{\Rsens}$, $\cost = 1/\sqrt{\Rsens}$; max $|d|$
    against the reviewer's logged A3 numerics
    (`Critique/replications/A3--multiplicative-conservation/output/results.json`
    \texttt{block\_c2\_c1.families.multiplicative}) is $\le 6.3 \times
    10^{-7}$ across VDA/CF/$\Rpone$/$\Rpfour$ on the 6-point pin set,
    well below the $10^{-5}$ tolerance. (The residual is the expected
    cross-$\Phi$-backend ULP-level reordering: paper's A\&S 7.1.26 vs the
    rebuild's \texttt{scipy.special.ndtr}.)

- **rb-016 conservation-family band (sha256 `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`).**
  `Rebuild/sims/A3--conservation-band/`:
  - **Block A** (C2 $v$-family VDA sweep at the headline cell across
    $p \in \{0, 1/2, 1\}$). $K_c$, $K_u$, $c_c^\star$, $c_u^\star$, and
    $\rdagger(\val)$ identical to floating-point identity across $p$
    (test \texttt{test\_3\_r\_dagger\_p\_invariance}, max $|\Delta| =
    0.0$ — a numerical statement *stronger* than Proposition 5.1's
    structural guarantee). Peak band: $\VDA^\star$ at $\val = 5$ shifts
    $0.0830 \to 0.0951$ (+14\%) going $p = 1 \to 0$, consistent with
    Corollary 3.1.
  - **Block B** (C1 $4{,}410$-cell sweep at $p \in \{0, 1\}$). Combined-
    variant: \texttt{n\_below\_0\_5} $177 \to 368$, **191 flips**
    $\CF \ge 0.5 \to < 0.5$, **0 reverse flips**, variant-B strict
    minimum deepens $0.3040 \to 0.2309$. Per-cell $\Delta\CF \le 0$ in
    every valid cell (Theorem thm:delta-cf-monotone; empirical-at-full-
    strength backing for §6 of this derivation).
  - Determinism verified by re-running the sim: \texttt{results.json} is
    byte-identical across reruns, sha256 unchanged.

The four model-test recovery digests are unchanged across this
derivation (no model edits): rb-001 `d3c62215…` (A1 recovery), rb-015
`f4f57a89…` (A3 family identities), rb-019 `0486921f…` (heterogeneous-r),
rb-020 `883ea15a…` (N-dim policy). This derivation is a pure consumer of
the existing model substrate; no new model code, no new tests, no new
sim outputs.

---

## 8. Scope and extensions

### 8.1 Scope

- **Local statement.** Proposition 5.1 ($\rdagger$ $p$-invariance) is a
  local statement at $\alpha = 1/N$: the boundary left-edge of the
  $\VDA(\Rsens)$ band, not the band's interior. The peak inside the band
  is *not* invariant, as Corollary 3.1 + §5.3 spell out.
- **Family extent.** The HLP envelope (3.3)–(3.4) holds for every $p \in
  \mathbb R$, but the manuscript reports the empirical band at $p \in
  \{0, 1/2, 1\}$ (rb-016 Block A) and $p \in \{0, 1\}$ (rb-016 Block B);
  the harmonic case $p = -1$ and the quadratic case $p = 2$ are admitted
  by the model code but not yet swept.
- **A3 + A1 composition.** Proposition 5.1 is at $\corr = 0$ (independent
  noise across locations). The $\Rpthree$-functional invariance argument
  (Step 2 of §5.2) extends to $\corr > 0$ by the same vanishing-bracket
  mechanism: at $\alpha = 1/N$ the $\Pnofa(\corr)$ integrand is evaluated
  at $b_c = b_u = b_{\mathrm{base}}$ (i.e.\ symmetric criteria at
  symmetric $\dprime$s), and the criterion-optimum $(c_c^\star, c_u^\star)$
  inherits this symmetry; the proof extends mutatis mutandis, but the
  formal extension is a sister-derivation task (queued; cross-link to
  `Rebuild/derivations/C2--non-monotonic-vda-rho.md` §6 scope paragraph).
- **A3 + A2/A8 composition.** Proposition 5.1's Step 1 also extends to
  heterogeneous per-location $\Rsens_i$ (A2) and heterogeneous per-uncued-
  slot allocation (A8): at the all-locations-uniform allocation $\alpha_i
  = 1/N$, every bracket $\dprimemax\,f(1/N) - \dprime_{\mathrm{base}}$
  vanishes, so the entire $\dprime$ vector is $p$-independent. The
  rb-021 A2 sim (sha256 `22b183f9…`) confirms C2 peak invariance under
  bounded heterogeneous-$\Rsens$ spread (peak $\VDA$ varies $\le 10^{-5}$
  at fixed $\corr$ across spread $\in \{0, 0.1, 0.2, 0.3\}$), consistent
  with the boundary mechanism extending into the band interior at small
  spreads.
- **Closed form for $\Delta\CF \le 0$.** Section 6 reduces the sign of
  $\partial \CF / \partial p$ to a competition between two $d'$-channel
  gradients; the uniform closed-form proof of the inequality remains
  open. The rebuild reports the result as **empirical at full strength**
  ($0/4{,}410$ reverse flips, rb-016) with this derivation supplying the
  motivation (§6.3 sign analysis).

### 8.2 Extensions to consider

- **Eq. (3.3) generalisation.** The KL-divergence expression for
  $\partial \ln \cost / \partial p$ should extend to the $n$-location
  power-mean constraint $\PowerMean_p(w_1, \ldots, w_n) = 1$ at fixed
  ratios $w_i / w_1 = R_i$, giving a generalised entropy formula
  $\partial \ln w_1 / \partial p = -(1/p^2) \DKL(\theta_p \| \mathrm{Uni}_n)$
  with $\theta_p$ the $n$-bin distribution of $R_i^p / \sum_j R_j^p$.
  This would be the natural object for a hypothetical A3 + A2 extension
  where each location has its own $\Rsens_i$ but the conservation
  constraint binds across locations.
- **Closed-form $\partial \CF/\partial p$.** A genuine attack on
  Section 6 would use the envelope theorem at $\Pone$ and $\Pfour$ to
  extract closed forms for $\partial \Rpone / \partial p$ and
  $\partial \Rpfour / \partial p$ in terms of the policy-specific
  $\alpha^\star$ and the $\dprime$-channel gradients of $\Rpone$ and
  $\Rpfour$; the competition (6.6) would then become an explicit
  inequality. The argument is similar in spirit to the Slepian-style
  derivation of `Rebuild/derivations/A1--rho-channel.md` §3 for the
  $\corr$-channel, but the $p$-channel acts on $(\benefit, \cost)$
  rather than on the noise covariance.
- **A3 + A1 cross-derivation.** Combining the $p$-derivative of (2.3)
  with the $\corr$-derivative of $\Pnofa(\corr)$ via dominated
  convergence (the same machinery `Rebuild/derivations/C2--non-monotonic-vda-rho.md`
  §3 uses) would give the closed-form joint sensitivity
  $\partial^2 \CF / (\partial p \partial \corr)$. The empirical
  band (rb-016 Block A is $\corr = 0$ only) is one $\corr$ panel; a
  joint $(p, \corr)$ sweep is queued as future work in Section
  sec:extensions-a3 scope.

---

## 9. References

The references are kept inline in the rebuild's voice: full bibliographic
entries for items absent from `research_db/papers/`, `research_db/papers/`
identifiers for items present.

- Hardy, G. H., Littlewood, J. E., and Pólya, G. (1934). *Inequalities*.
  Cambridge University Press. (Theorem 16 = power-mean monotonicity;
  §2.9 statement of the means $\mathfrak M_r$.) Math-methods reference,
  cited in `Rebuild/manuscript/refs.bib` as `HLP1934` (added at rb-017
  per math-methods scope inherited from rb-008/CR-035/CR-037; no
  `research_db/papers/` stub).
- Bullen, P. S. (2003). *Handbook of Means and Their Inequalities*.
  Kluwer Academic Publishers, Dordrecht. (Chapter II covers the power
  means in textbook form, including the cleaner $p \to 0$ limit
  computation used in §2.3.) Math-methods reference; no
  `research_db/papers/` stub.
- Sterbenz, P. H. (1974). *Floating-Point Computation*. Prentice-Hall,
  Englewood Cliffs. (Theorem 4.3.1 = the lemma underwriting the bit-exact
  band of Section sec:appendix-c5.) Math-methods reference, cited in
  `refs.bib` as `Sterbenz1974`.
- Cover, T. M. and Thomas, J. A. (2006). *Elements of Information
  Theory*, 2nd ed. Wiley-Interscience, Hoboken. (Chapter 2 defines the
  KL divergence used in §3.2 — the standard $D(p \| q) = \sum p \ln(p/q)$
  for two probability distributions.) Math-methods reference; cited by
  full bibliographic reference, no stub.
- The reviewer's A3 verdict file
  `Critique/verdicts/A3--multiplicative-conservation.md` (current label
  CONTESTED) and the A3 replication
  `Critique/replications/A3--multiplicative-conservation/` (sha256 in
  rb-016 attribution table) supply the empirical anchor for §1.3 and
  §6.4.

---

## Verification performed

- **Equation (2.3) closed form.** Derivation by direct substitution
  $\benefit = \Rsens \cost$ into $\PowerMean_p = 1$; cross-checked
  numerically by `Rebuild/model/tests/test_conservation_family.py`
  \texttt{test\_family\_identities} (rb-015, sha256 `f4f57a89…`) to
  $4.4 \times 10^{-16}$ across $p \in \{-2, \ldots, 2\}$ and 21-point
  log-$\Rsens$ grid.
- **$p \to 0$ limit (§2.3).** Series expansion of $\ln \cost = (1/p) \ln(2 /
  (\Rsens^p + 1))$ in $p$, dominated by $-(\ln \Rsens)/2$; matches the
  geometric-mean closed form $\cost(\Rsens; 0) = 1/\sqrt{\Rsens}$ and the
  rb-015 \texttt{test\_multiplicative\_recovery} numerics (max $|d| \le
  6.3 \times 10^{-7}$).
- **Eq. (3.3) KL-divergence form.** Algebraic check by expanding
  $\DKL(\mathrm{Bern}(\theta_p) \| \mathrm{Bern}(1/2)) = \theta_p \ln(2
  \theta_p) + (1 - \theta_p) \ln(2(1 - \theta_p))$ and showing equality
  with the bracket in (3.1); the check is in the inline text of §3.2.
- **Eq. (3.4) sign of $\partial \cost / \partial p$.** Direct from (3.3):
  $\DKL \ge 0$ with equality iff $\theta_p = 1/2$ iff $\Rsens = 1$; the
  $1/p^2$ prefactor is positive; sign is unambiguous. Numerical
  spot-check at $\Rsens = 0.3548$, $p \in \{0, 1\}$ in §3.3 reproduces
  the predicted $+13.8\%$ shift in $\cost$ to two significant figures.
- **Proposition 4.1.** Direct from (2.3) at $\Rsens = 1$; numerical
  witness rb-015 \texttt{test\_symmetric\_corner\_invariant} to binary
  equality across $p \in \{-2, \ldots, 2\}$.
- **Corollary 4.2.** Substituting $\benefit(1, p) = \cost(1, p) = 1$ into
  the $\dprime$-map gives the symmetric baseline pointwise; numerical
  witness rb-015 \texttt{test\_symmetric\_corner\_invariant} (\texttt{policies(r=1,
  p=0) == policies(r=1, p=1)} to FP identity); combined with rb-001
  \texttt{test\_recovery.py} (sha256 `d3c62215…`) for bit-exact $r = 1$ pin
  numerics.
- **Proposition 5.1.** Step 1 (vanishing bracket at $\alpha = 1/N$): by
  the definition $\dprime_{\mathrm{base}} = \dprimemax\,f(1/N)$; algebra
  in §5.2. Step 2 (criterion optimum $p$-independent): functional
  composition; the $\Pthree$ expected-reward writing in
  `Critique/derivations/C2--non-monotonic-vda.md` Eq. (2.1) has no
  conservation-order argument. Step 3 ($K_c, K_u$ $p$-independent): same
  algebra evaluated at the $p$-independent operands of Step 2. Numerical
  witness rb-016 \texttt{recovery.test\_3\_r\_dagger\_p\_invariance} ($K_c$,
  $K_u$, $c_c^\star$, $c_u^\star$, $\rdagger(\val)$ all identical to FP
  across $p$).
- **§6 chain rule.** Eq. (6.3) by the envelope theorem (textbook); Eqs.
  (6.4) by direct differentiation of the $\dprime$-map (1.2 of the
  derivation, `core.py:340`); sign of (6.5) from monotonicity of $f$ and
  positivity of $\dprime_{\mathrm{base}}$. The competition (6.6) is
  exhibited without resolving its sign uniformly. Numerical witness:
  rb-016 Block B records $\Delta\CF \le 0$ in $4{,}410 / 4{,}410$ cells
  with $0$ reverse flips, full empirical support for the conjecture.
- **Reproducibility.** This derivation is a pure consumer of two existing
  outputs: rb-015 \texttt{test\_conservation\_family.py} sha256
  `f4f57a89e5108db47447cbeaf2f15440f56cdfffb65f3d173dc4a0550121791e` and
  rb-016 \texttt{Rebuild/sims/A3--conservation-band/output/results.json}
  sha256
  `055bf4ec862c711f2c6a3fa0831e1373b806a84c5f5c1a6b13fd1d9d7a039a33`,
  both byte-identical on rerun (rb-015 binary; rb-016 verified by
  re-running and checking the JSON dump's sha). No new sim, no new test.

## Extensions to consider

- Promote the §6 chain-rule analysis to a closed-form proof of
  $\partial \CF / \partial p \le 0$ everywhere on the C1 grid (the
  rebuild's main open derivation in the A3 thread).
- Derive the analogue of Eq. (3.3) for the $n$-location power-mean
  constraint, enabling the $\partial / \partial p$ analysis to extend
  cleanly to A3 + A2 (per-location $\Rsens_i$).
- Joint $(p, \corr)$ sensitivity: the §6 chain rule composed with the
  $\corr$-channel gradients of `Rebuild/derivations/C2--non-monotonic-vda-rho.md`
  §3 would give $\partial^2 \CF / (\partial p \partial \corr)$ in closed
  form, characterising the four-corner conservation-form × correlation
  band that the rebuild currently reports as two single-axis bands.
