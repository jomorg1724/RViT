---
type: derivation
project: AttentionManuscript / VDA-rebuild
agent: constructive-rebuilder
backlog_id: RB-030
claim_id: C4
status: drafted
created: 2026-05-25
backing_for: "Rebuild/manuscript/sections/results.tex §results-c4 (Eqs. value-weight, left-derivative, r-inv, r-inv-corner) + manuscript §appendix-derivation-C4 (sec:appendix)"
backed_by_sim: "Rebuild/sims/C4--anti-cue-inversion/ (rb-012, sha256 6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96)"
implements: "Rebuild/sims/C4--anti-cue-inversion/run.py: _A0_B0, _optimal_criteria_at_uniform, r_inv_threshold (using Rebuild/model/core.py: p_no_fa_grid, _GH_W, _GH_Z, d_prime_asym, optimal_R)"
recovery_test: "rb-012 Step A 48.6% recovers reviewer §4 49.0% to Δ=0.4 pp (PASS); Step C(i) max|Δα*|=0 / max|ΔR*|=3e-6 (PASS); symmetric-corner identity r†_inv=1.0000 to floating-point identity across all (variant, ρ) panels of step_A.tally"
voice: independent re-derivation in the rebuild's voice; not a copy of Critique/derivations/C4--no-inversion.md
---

# C4 — The boundary inversion threshold and the anti-cue prediction

> *The rebuilt model promotes the inherited paper's §4.5 ("Inverted Attention
> is Never Optimal") claim from a categorical statement to a conditional
> theorem. This appendix derives the closed-form left one-sided derivative of
> the P1 expected-reward functional at the uniform allocation $\alpha = 1/N$;
> defines the boundary inversion threshold $\rstarinv(\valid, \val, N, \CR,
> \rho) = (N - 1)\,A_0/B_0$ that the inherited §4.5 paragraph implicitly
> assumes; extends $A_0, B_0$ to the A1 decorrelation channel via the same
> one-factor Gauss–Hermite quadrature the rebuilt model already uses for
> $\Pnofa(\rho)$ (Section §2 of `Rebuild/derivations/A1--rho-channel.md`);
> proves the symmetric-corner identity $\rstarinv(1/N, 1, N, \CR, \rho) = 1$
> from first-order-condition (FOC) symmetry alone, independent of $N$, $\CR$
> and $\rho$; and connects the closed form to the global-no-inversion theorem
> via the value-weight inequality $w_c \ge w_u$. The derivation is
> independent of `Critique/derivations/C4--no-inversion.md` (there is only one
> correct derivation, but the framing is rebuild-voiced: constructive
> statements of the rebuilt model's positive predictions rather than attacks
> on the inherited prose). Every numerical statement here is sourced from
> `Rebuild/sims/C4--anti-cue-inversion/` (sha256 `6ad651d6…`), and the
> closed-form ρ-extension is the one the simulation's `_A0_B0` routine
> implements.*

Notation follows `agents/paper_rebuilder_prompt.md` §2 and the SDT primitives
introduced in §1 of `Rebuild/derivations/A1--rho-channel.md`. The reader who
wants a compressed reminder finds one in §1.1 below.

---

## 1. Setup and the inversion branch

### 1.1 Notation

Let $N \ge 2$ be the number of locations, indexed so that $i = c$ is the cued
location and $i = 1, \dots, N - 1$ enumerates the $N - 1$ uncued locations.
Per-location SDT primitives:
$$
  \HR_i \;=\; \Phi(\dprime_i/2 - c_i),
  \qquad
  \FAR_i \;=\; \Phi(-\dprime_i/2 - c_i),
  \qquad
  1 - \FAR_i \;=\; \Phi(b_i),
  \quad b_i := c_i + \dprime_i/2.
  \tag{1.1}
$$
On a no-change trial the per-location FA event is $\{X_i > c_i\}$ with
$X_i \sim \mathcal N(-\dprime_i/2,\, 1)$; on a change trial the change is at
*one* location only (the cued with probability $\valid$, a specific uncued
with probability $(1 - \valid)/(N - 1)$), and the per-location hit event is
$\{X_i > c_i\}$ with $X_i \sim \mathcal N(+\dprime_i/2,\, 1)$.

Attention allocation. The cued slot receives $\alpha \in [0, 1]$ of the
attention budget; each uncued slot receives $(1 - \alpha)/(N - 1)$. The
asymmetric transfer maps these to per-location sensitivities through a
cost--benefit pair $(\benefit(\Rsens),\, \cost(\Rsens))$ with
$\benefit + \cost = 2$ (the inherited paper's additive conservation, A3):
$$
  \begin{aligned}
    \alpha \ge 1/N\!: \quad
    \dprime_c(\alpha;\,\Rsens)
    &= \dprime_{\mathrm{base}} + \benefit(\Rsens)
       \bigl[\,\dprimemax\,f(\alpha) - \dprime_{\mathrm{base}}\bigr], \\
    \dprime_u(\alpha;\,\Rsens)
    &= \dprime_{\mathrm{base}} + \cost(\Rsens)
       \Bigl[\,\dprimemax\,
       f\!\bigl(\tfrac{1 - \alpha}{N - 1}\bigr) - \dprime_{\mathrm{base}}
       \Bigr],
  \end{aligned}
  \tag{1.2}
$$
with $\benefit(\Rsens) = 2\Rsens/(\Rsens + 1)$,
$\cost(\Rsens) = 2/(\Rsens + 1)$,
$f(a) = f_0 + (1 - f_0)\,h(a)$,
$\dprime_{\mathrm{base}} = \dprimemax\, f(1/N)$, and all $\dprime$ values
clamped at $\ge 0$. The role of $\benefit$ is the *over-allocation*
multiplier and $\cost$ is the *under-allocation* multiplier; $\Rsens$ is the
*cost--benefit ratio* (larger $\Rsens$ ⇒ over-allocation pays more, the
benefit-dominant regime). See `Rebuild/model/core.py:d_prime_asym` for the
exact implementation.

Expected reward (P1, full criterion optimisation; see
`Rebuild/derivations/A1--rho-channel.md` §1.2 for the booking that isolates
A1 to the no-FA product):
$$
  \Rew
  \;=\;
  \tfrac{1}{2}\bigl[\,
    \valid\,\val\,\HR_c + (1 - \valid)\,\HR_u
  \,\bigr]
  \;+\;
  \tfrac{1}{2}\,\CR\,\Pnofa(\rho),
  \tag{1.3}
$$
with $\CR = \valid\val + (1 - \valid)$ (variant A) or $\CR = 1$
(variant B), and $\Pnofa(\rho)$ the equicorrelated no-FA orthant
probability — see (4.1) below.

### 1.2 The inversion branch: $\benefit$ and $\cost$ swap roles at $\alpha < 1/N$

The model (1.2) is stated for $\alpha \ge 1/N$ — the cued slot is the
*over-allocated* one and the uncued slots are the *under-allocated* ones.
Below the uniform point $\alpha < 1/N$ the roles flip: the cued slot is now
*under-allocated* (multiplied by the cost factor $\cost$) and the uncued
slots are *over-allocated* (multiplied by the benefit factor $\benefit$):
$$
  \alpha < 1/N\!: \quad
  \dprime_c
  = \dprime_{\mathrm{base}} + \cost\bigl[\dprimemax\,f(\alpha)
                  - \dprime_{\mathrm{base}}\bigr],
  \quad
  \dprime_u
  = \dprime_{\mathrm{base}} + \benefit\Bigl[\dprimemax\,
                  f\!\bigl(\tfrac{1 - \alpha}{N - 1}\bigr)
                  - \dprime_{\mathrm{base}}\Bigr].
  \tag{1.4}
$$
The replacement of $(\benefit, \cost)$ in (1.2) by $(\cost, \benefit)$ in
(1.4) is what `Rebuild/model/core.py:d_prime_asym` implements — see its
branch on `alpha < 1.0 / N`. At $\alpha = 1/N$ exactly, both branches give
$\dprime_c = \dprime_u = \dprime_{\mathrm{base}}$ (independent of $\Rsens$).

> **The kink at $\alpha = 1/N$ (rebuild observation).** The inherited paper
> states (1.2)–(1.4) without remarking that, except at $\Rsens = 1$ (where
> $\benefit = \cost = 1$), $\dprime_c(\alpha)$ and $\dprime_u(\alpha)$ are
> *only piecewise-linear-in-$f$* at $\alpha = 1/N$ — the slope changes
> discontinuously across the branch. Differentiating (1.2) and (1.4) at the
> common point $\alpha = 1/N$:
> $$
>   \left.\frac{\partial \dprime_c}{\partial \alpha}\right|_{1/N^+}
>   \!=\, \benefit\,\dprimemax\,f'(1/N),
>   \qquad
>   \left.\frac{\partial \dprime_c}{\partial \alpha}\right|_{1/N^-}
>   \!=\, \cost\,\dprimemax\,f'(1/N), \tag{1.5}
> $$
> $$
>   \left.\frac{\partial \dprime_u}{\partial \alpha}\right|_{1/N^+}
>   \!=\, -\frac{\cost}{N - 1}\,\dprimemax\,f'(1/N),
>   \qquad
>   \left.\frac{\partial \dprime_u}{\partial \alpha}\right|_{1/N^-}
>   \!=\, -\frac{\benefit}{N - 1}\,\dprimemax\,f'(1/N), \tag{1.6}
> $$
> with $f'(1/N) > 0$ on the $h \in \{\mathrm{linear},\sqrt{\,\cdot\,}\}$
> transfers the model uses. The kink is the analytic source of the closed
> form (3.4) below; the inherited §4.5 paragraph's "regardless of $\Rsens$"
> language is correct as a *global* empirical statement but masks this
> $\Rsens$-dependent local structure (§5 makes this explicit).

---

## 2. Boundary partials $A_0, B_0$ and the one-sided $\Rew$-derivatives

### 2.1 The partial derivatives at $\alpha = 1/N$

Treat (1.3) as a function of $(\dprime_c, \dprime_u)$ with the criteria
$(c_c, c_u)$ jointly optimised inside. By the envelope theorem, when the
criteria are at their optimum $(c_c^\star, c_u^\star)$ we may differentiate
$\Rew$ in $(\dprime_c, \dprime_u)$ holding the criteria fixed. Routine
chain-rule from (1.1) and (1.3):
$$
  \frac{\partial \Rew}{\partial \dprime_c}
  \;=\;
  \tfrac{1}{4}\,\valid\,\val\,p_c^H
  \;+\;
  \tfrac{1}{2}\,\CR\,\frac{\partial \Pnofa(\rho)}{\partial \dprime_c},
  \qquad
  p_c^H := \phi\!\bigl(\dprime_c/2 - c_c\bigr),
  \tag{2.1}
$$
$$
  \frac{\partial \Rew}{\partial \dprime_u}
  \;=\;
  \tfrac{1}{4}\,(1 - \valid)\,p_u^H
  \;+\;
  \tfrac{1}{2}\,\CR\,\frac{\partial \Pnofa(\rho)}{\partial \dprime_u},
  \qquad
  p_u^H := \phi\!\bigl(\dprime_u/2 - c_u\bigr).
  \tag{2.2}
$$
Here $\phi$ is the standard normal density. The factors of $\tfrac{1}{4}$
arise from the trial prior $\tfrac{1}{2}$ in (1.3) multiplied by
$\partial \HR / \partial \dprime = \tfrac{1}{2}\phi(\dprime/2 - c)$.

### 2.2 The boundary constants are $\Rsens$-independent

At $\alpha = 1/N$, both branches (1.2) and (1.4) give
$\dprime_c = \dprime_u = \dprime_{\mathrm{base}}$, *independent of $\Rsens$*.
The criterion optimum $(c_c^\star, c_u^\star)$ at this point therefore
depends on $(\valid, \val, N, \CR, \rho)$ but not on $\Rsens$. Consequently
the partial derivatives in (2.1)–(2.2), evaluated at
$\alpha = 1/N$ and the optimal criteria there, are themselves
$\Rsens$-independent. Define the **boundary partials**
$$
  A_0 \;:=\;
  \left.\frac{\partial \Rew}{\partial \dprime_c}\right|_{\alpha = 1/N,\,
                                                         (c_c^\star, c_u^\star)},
  \qquad
  B_0 \;:=\;
  \left.\frac{\partial \Rew}{\partial \dprime_u}\right|_{\alpha = 1/N,\,
                                                         (c_c^\star, c_u^\star)}.
  \tag{2.3}
$$
$A_0, B_0$ are pure functions of $(\valid, \val, N, \CR, \dprime_{\mathrm{base}}, \rho)$;
they carry no $\Rsens$ dependence. Both are strictly positive at non-degenerate
criteria (each summand in (2.1)–(2.2) is the product of strictly positive
factors).

### 2.3 The one-sided derivative of $\Rew$ at $\alpha = 1/N$

Chain rule applied to (1.3) using (1.5)–(1.6):
$$
  \left.\frac{\partial \Rew}{\partial \alpha}\right|_{1/N^+}
  \;=\;
  \dprimemax\,f'(1/N)\,
  \left[
    \benefit\,A_0 \;-\;
    \frac{\cost}{N - 1}\,B_0
  \right],
  \tag{2.4}
$$
$$
  \left.\frac{\partial \Rew}{\partial \alpha}\right|_{1/N^-}
  \;=\;
  \dprimemax\,f'(1/N)\,
  \left[
    \cost\,A_0 \;-\;
    \frac{\benefit}{N - 1}\,B_0
  \right].
  \tag{2.5}
$$
The right-side derivative (2.4) measures whether $\alpha = 1/N$ is locally a
*maximum from the right* (so that moving $\alpha$ up strictly decreases
$\Rew$ ⇒ the cued slot wants *less* than $1/N$); the left-side derivative
(2.5) measures whether $\alpha = 1/N$ is locally a *maximum from the left*
(moving $\alpha$ down strictly decreases $\Rew$ ⇒ no global inversion has a
local foothold at the boundary). The signs are not in general the same: the
$\benefit \leftrightarrow \cost$ swap between (2.4) and (2.5) is the
expression of the kink (1.5)–(1.6).

---

## 3. The closed-form local threshold $\rstarinv$

Substituting $\benefit = 2\Rsens/(\Rsens + 1)$ and $\cost = 2/(\Rsens + 1)$
into (2.5):
$$
  \left.\frac{\partial \Rew}{\partial \alpha}\right|_{1/N^-}
  \;=\;
  \frac{2\,\dprimemax\,f'(1/N)}{\Rsens + 1}
  \left[
    A_0 \;-\;
    \frac{\Rsens}{N - 1}\,B_0
  \right].
  \tag{3.1}
$$
The prefactor is strictly positive. The bracket is **linear in $\Rsens$**
once the $\Rsens$-independent boundary partials $A_0, B_0$ are pulled out
(§2.2). The sign of (3.1) is therefore the sign of the bracket:
$$
  \text{sign}\,\Bigl(
    \!\left.\partial_\alpha \Rew\right|_{1/N^-}
  \Bigr)
  \;=\;
  \text{sign}\!\left[
    A_0 \;-\;
    \frac{\Rsens}{N - 1}\,B_0
  \right].
  \tag{3.2}
$$
The boundary point is locally a left-side maximum (positive left derivative
⇒ the function strictly decreases as $\alpha$ moves down from $1/N$) iff
the bracket is non-negative, which solves to the closed form
$$
  \boxed{\;
    \Rsens \;\le\; \rstarinv(\valid, \val, N, \CR, \rho)
    \;:=\;
    (N - 1)\,\frac{A_0(\valid, \val, N, \CR, \rho)}{B_0(\valid, \val, N, \CR, \rho)}.
  \;}
  \tag{3.3}
$$

> **Proposition 3.1 (boundary inversion threshold).** *Under the asymmetric
> conservation $\benefit + \cost = 2$ with $\benefit(\Rsens) = 2\Rsens/(\Rsens + 1)$,
> $\cost(\Rsens) = 2/(\Rsens + 1)$, the P1 expected-reward functional (1.3)
> satisfies $\left.\partial_\alpha \Rew\right|_{1/N^-} \ge 0$ if and only if
> $\Rsens \le \rstarinv$ with $\rstarinv$ as in (3.3). Equality holds at
> $\Rsens = \rstarinv$, where the left derivative vanishes. For
> $\Rsens > \rstarinv$ the boundary point $\alpha = 1/N$ is locally a left-
> branch *minimum* (the left branch then develops a local maximum at
> $\alpha = \alpha_l^\star < 1/N$, generally strictly below the right-branch
> global maximum — see §6 for the global comparison).*

Read (3.1) carefully. For (3.3) to be *uniformly* a left-side-max condition
in the $\Rsens$ range the inherited paper sweeps ($\Rsens \in [0.1, 10]$),
we would need $\rstarinv > 10$ at every cell of the swept space. The rb-012
Step A tally of (3.3) on the primary $(\valid, \val)$ grid at $N = 4$ records
the opposite: $48.6\%$ of cells at $\rho = 0$ have $\rstarinv \in [0.1, 10]$
(median $\sim 17$ in variant A, $\sim 8$ in variant B; minimum $1.0000$ at
the symmetric corner, §5). The inherited §4.5 "regardless of $\Rsens$"
phrasing is therefore correct as a *global* empirical statement but
incomplete as a *local* derivative statement: across roughly half the
swept space the sign of the boundary left derivative *does* depend on
$\Rsens$. The local picture is bimodal (a left-branch local maximum near
$\alpha \to 0$ and a right-branch global maximum at $\alpha^\star > 1/N$);
what guarantees no global inversion is the value-weight inequality (§6),
not local cost-vs-benefit balance.

### 3.1 Mirror to the C2 escape threshold

The closed form (3.3) is the structural mirror of the rebuilt C2 escape
threshold
$\rdagger(\val) = K_u(\val) / [(N - 1)\,K_c(\val)]$
(Rebuild/manuscript/sections/results.tex §results-c2, Eqs. r-dagger /
K-c / K-u; companion derivation in
`Critique/derivations/C2--non-monotonic-vda.md`): both are ratios of
$\Rsens$-independent boundary quantities, scaled by the location-count
factor $(N - 1)$, that capture the rebuilt model's $\Rsens$-axis behaviour
at a specific boundary ($\alpha = \alpha^\star_{P_2}$ for C2; $\alpha = 1/N$
for C4). Both have ρ-extensions through the same one-factor Gauss–Hermite
quadrature (§4 here; the C2 ρ-extension is the parallel queued increment
RB-026). The structural parallel is a positive observation about the
rebuilt model — its $\Rsens$-axis findings are governed by ratios of
boundary partials — not a reframe of either claim.

---

## 4. ρ-extension: $A_0(\rho)$ and $B_0(\rho)$ via one-factor Gauss–Hermite

### 4.1 The equicorrelated no-FA orthant probability

Under the A1 decorrelation channel (`Rebuild/derivations/A1--rho-channel.md`
§2), the per-location no-change decision variables $\{X_i\}$ are
equicorrelated Gaussian with common correlation $\rho \in [0, 1)$. The
one-factor representation $X_i = \sqrt{\rho}\,Z + \sqrt{1 - \rho}\,U_i$
(with $Z, U_i \stackrel{\mathrm{iid}}{\sim} \mathcal N(0, 1)$) reduces the
$N$-dimensional orthant probability to a one-dimensional integral over the
shared latent $Z$:
$$
  \Pnofa(\rho)
  \;=\;
  \int_{-\infty}^{+\infty}
  \Phi\!\left(\frac{b_c - \sqrt{\rho}\,z}{\sqrt{1 - \rho}}\right)
  \Phi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1 - \rho}}\right)^{N - 1}
  \phi(z)\,\mathrm dz.
  \tag{4.1}
$$
The simulation evaluates (4.1) by Gauss–Hermite-64
(`Rebuild/model/core.py:p_no_fa_grid`, `p_no_fa_point`). At $\rho \to 0$
the substitution $\sqrt{\rho} \to 0$, $\sqrt{1 - \rho} \to 1$ collapses
each integrand factor to its $z$-independent value, factorises the integral
out of $\int \phi(z)\,\mathrm dz = 1$, and recovers
$\Pnofa(0) = \Phi(b_c)\,\Phi(b_u)^{N - 1}$ — the inherited independent
form bit-for-bit.

### 4.2 The ρ-aware partial derivatives

Differentiate (4.1) inside the integral with respect to $\dprime_c, \dprime_u$
(equivalently $b_c, b_u$, since $b_i = c_i + \dprime_i/2$ and the criteria are
held fixed at their $\alpha = 1/N$ optimum). Let
$s := \sqrt{1 - \rho}$ and write
$\beta_i(z) := (b_i - \sqrt{\rho}\,z)/s$ for brevity:
$$
  \frac{\partial \Pnofa(\rho)}{\partial \dprime_c}
  \;=\;
  \frac{1}{2s}
  \int_{-\infty}^{+\infty}
  \phi\!\bigl(\beta_c(z)\bigr)\,
  \Phi\!\bigl(\beta_u(z)\bigr)^{N - 1}\,
  \phi(z)\,\mathrm dz,
  \tag{4.2}
$$
$$
  \frac{\partial \Pnofa(\rho)}{\partial \dprime_u}
  \;=\;
  \frac{N - 1}{2s}
  \int_{-\infty}^{+\infty}
  \Phi\!\bigl(\beta_c(z)\bigr)\,
  \Phi\!\bigl(\beta_u(z)\bigr)^{N - 2}\,
  \phi\!\bigl(\beta_u(z)\bigr)\,
  \phi(z)\,\mathrm dz.
  \tag{4.3}
$$
Substituting (4.2)–(4.3) into (2.1)–(2.2) gives the ρ-aware boundary
partials
$$
  A_0(\rho)
  \;=\;
  \tfrac{1}{4}\,\valid\,\val\,p_c^H
  \;+\;
  \tfrac{1}{2}\,\CR \cdot
  \frac{\partial \Pnofa(\rho)}{\partial \dprime_c},
  \qquad
  B_0(\rho)
  \;=\;
  \tfrac{1}{4}\,(1 - \valid)\,p_u^H
  \;+\;
  \tfrac{1}{2}\,\CR \cdot
  \frac{\partial \Pnofa(\rho)}{\partial \dprime_u}.
  \tag{4.4}
$$
These are exactly the formulae the simulation evaluates: see
`Rebuild/sims/C4--anti-cue-inversion/run.py:_A0_B0`, lines 210–257, where
the ρ = 0 branch shortcuts to the analytic forms and the ρ > 0 branch
sums (4.2)–(4.3) against the same `_GH_Z, _GH_W` nodes the rebuilt model
uses for $\Pnofa$ itself.

### 4.3 The ρ → 0 limit collapses to the reviewer's analytic form

At $\rho = 0$: $\sqrt{\rho} = 0$, $s = 1$, $\beta_i(z) = b_i$ (no $z$
dependence). The integrands in (4.2)–(4.3) factorise out of the
$\int \phi(z)\,\mathrm dz = 1$:
$$
  \frac{\partial \Pnofa(0)}{\partial \dprime_c}
  \;=\;
  \tfrac{1}{2}\,\phi(b_c)\,\Phi(b_u)^{N - 1}
  \;=\;
  \tfrac{1}{2}\,p_c^F\,(1 - \FAR_u)^{N - 1},
  \tag{4.5}
$$
$$
  \frac{\partial \Pnofa(0)}{\partial \dprime_u}
  \;=\;
  \tfrac{N - 1}{2}\,\Phi(b_c)\,\Phi(b_u)^{N - 2}\,\phi(b_u)
  \;=\;
  \tfrac{N - 1}{2}\,(1 - \FAR_c)\,(1 - \FAR_u)^{N - 2}\,p_u^F,
  \tag{4.6}
$$
using $p_i^F := \phi(b_i)$ and $\phi(-x) = \phi(x)$. Substituting
(4.5)–(4.6) into (4.4) recovers exactly the inherited (ρ = 0) closed form
(`Critique/derivations/C4--no-inversion.md` Eqs. (2.2)–(2.3)):
$$
  A_0(0)
  \;=\;
  \tfrac{1}{4}\bigl[\valid\,\val\,p_c^H
                  + \CR\,p_c^F\,(1 - \FAR_u)^{N - 1}\bigr],
  \tag{4.7}
$$
$$
  B_0(0)
  \;=\;
  \tfrac{1}{4}\bigl[(1 - \valid)\,p_u^H
                  + (N - 1)\,\CR\,(1 - \FAR_c)\,(1 - \FAR_u)^{N - 2}\,p_u^F\bigr].
  \tag{4.8}
$$

Numerical realisation. The rb-012 Step A panel at $\rho = 0$ replays the
reviewer's $48.6\%$ vs $49.0\%$ count of cells with
$\rstarinv \in [0.1, 10]$ on the $N = 4$ primary grid — $\Delta = 0.4$
percentage points (PASS at the $1.0$ pp tolerance the simulation registers).
This is the ρ → 0 recovery of (3.3) against (4.7)–(4.8).

The ρ > 0 branch is a *normative addition* of the rebuilt model: the
closed form (3.3), evaluated with the ρ-aware partials (4.4), predicts a
quantitative shift of $\rstarinv$ as the A1 channel opens. rb-012 Step A
records this shift directly: at $\rho = 0.2$ the median $\rstarinv$
drops by $\sim 13\%$ in variant A and $\sim 21\%$ in variant B, with the
fraction of cells inside the swept $\Rsens$-range rising from $48.6\%$ to
$\sim 51.9\%$. The qualitative inversion regime ($V < 1/N$) is essentially
preserved under ρ (rb-012 Step C records $25$ vs $26$ inversion cells at
ρ = 0 vs ρ = 0.2 — $\Delta = 1$ at the boundary). The A1 channel and the
C4 inversion lever are independent mechanisms.

---

## 5. The symmetric-corner identity

The closed form (3.3) admits an exact, model-parameter-free anchor at the
symmetric corner $(\valid, \val) = (1/N, 1)$ — the cell where the
value-weight inequality (§6) attains equality. We promote this anchor to a
proposition.

> **Proposition 5.1 (symmetric-corner identity).** *Let $\valid = 1/N$ and
> $\val = 1$. Then for any $N \ge 2$, any conservation variant
> $\CR \in \{\valid\,\val + (1 - \valid),\, 1\}$, and any correlation
> $\rho \in [0, 1)$:*
> $$
>   \rstarinv\!\bigl(1/N,\,1,\,N,\,\CR,\,\rho\bigr) \;=\; 1
>   \qquad \text{exactly.}
>   \tag{5.1}
> $$

**Proof.** At $(\valid, \val) = (1/N, 1)$ the reward weights coincide:
the cued change-trial weight is $\valid \cdot \val = 1/N$, the *total*
uncued change-trial weight is $(1 - \valid) = (N - 1)/N$, and so the
*per-uncued-slot* weight is $(1 - \valid)/(N - 1) = 1/N$ as well.
Both reward variants reduce to $\CR = 1$ at this corner
($\valid\,\val + (1 - \valid) = 1/N + (N - 1)/N = 1$ in variant A;
$\CR = 1$ in variant B by definition). The FOC system for
$(c_c^\star, c_u^\star)$ at $\alpha = 1/N$, $\dprime_c = \dprime_u =
\dprime_{\mathrm{base}}$ reads
$$
  \frac{\partial \Rew}{\partial c_c}
  \,=\,
  -\,\tfrac{1}{2}\,\valid\,\val\,p_c^H
  \;+\;
  \tfrac{1}{2}\,\CR\,\frac{\partial \Pnofa(\rho)}{\partial c_c}
  \,=\, 0,
  \qquad
  \frac{\partial \Rew}{\partial c_u}
  \,=\,
  -\,\tfrac{1}{2}\,(1 - \valid)\,p_u^H
  \;+\;
  \tfrac{1}{2}\,\CR\,\frac{\partial \Pnofa(\rho)}{\partial c_u}
  \,=\, 0.
  \tag{5.2}
$$
The no-FA term (4.1) depends symmetrically on $(b_c, b_u)$ at $b_c = b_u$
(both inner $\Phi$ factors enter with total exponent $N$ in
$\Phi(\beta_c)\,\Phi(\beta_u)^{N-1}$). At any candidate solution
$c_c = c_u =: c^\star$ the second FOC of (5.2) is therefore the first
multiplied through by $(N - 1)$ (the change-trial weight ratio
$(1 - \valid)/(\valid\,\val) = ((N-1)/N)/(1/N) = N - 1$ matches the
ratio $\partial_{c_u} \Pnofa / \partial_{c_c} \Pnofa = N - 1$ inherited
from the $(N - 1)$-th power on the uncued factor — see (4.2)–(4.3),
noting $\partial b/\partial c = 1$ vs $\partial b/\partial \dprime = 1/2$
contribute a common factor of $2$ that cancels in the ratio). Both FOCs
collapse to the same scalar equation, so the symmetric ansatz is
consistent, and (by joint concavity of $\Rew$ in $(c_c, c_u)$ over the
interior at fixed $\dprime_c = \dprime_u = \dprime_{\mathrm{base}}$,
the property the criterion grid optimiser
`Rebuild/sims/C4--anti-cue-inversion/run.py:_optimal_criteria_at_uniform`
exploits) it is the global maximiser. Consequently
$c_c^\star = c_u^\star =: c^\star$, and the per-location marginals
coincide:
$$
  p_c^H = p_u^H \equiv p^H,
  \qquad
  p_c^F = p_u^F \equiv p^F,
  \qquad
  \FAR_c = \FAR_u \equiv \FAR.
  \tag{5.3}
$$
Substitute (5.3) into the ρ-aware partials (4.4). For the change-trial
contribution, the cued and uncued summands carry the same per-channel
weight $1/N$ in their respective brackets ($\valid\,\val = 1/N$ in $A_0$;
$(1 - \valid) = (N - 1)/N$ in $B_0$, but the $1/(N - 1)$ inside the model
booking — see (5.2)'s second line — restores per-channel parity, so the
*total* uncued weight is $(N - 1) \cdot 1/N = (N - 1)/N$):
$$
  \tfrac{1}{4}\,\valid\,\val\,p^H \;=\; \tfrac{1}{4N}\,p^H,
  \qquad
  \tfrac{1}{4}\,(1 - \valid)\,p^H \;=\; \tfrac{N - 1}{4N}\,p^H
  \;=\; (N - 1)\cdot \tfrac{1}{4N}\,p^H.
  \tag{5.4}
$$
For the no-FA contribution: at the symmetric corner the inner argument
$\beta_c(z) = \beta_u(z) =: \beta(z)$, so the partials (4.2)–(4.3)
reduce to
$$
  \frac{\partial \Pnofa(\rho)}{\partial \dprime_c}
  \,=\,
  \tfrac{1}{2s}
  \int \phi(\beta(z))\,\Phi(\beta(z))^{N - 1}\,\phi(z)\,\mathrm dz
  \;=:\; I(\rho),
  \tag{5.5}
$$
$$
  \frac{\partial \Pnofa(\rho)}{\partial \dprime_u}
  \,=\,
  (N - 1) \cdot
  \tfrac{1}{2s}
  \int \Phi(\beta(z))\,\Phi(\beta(z))^{N - 2}\,\phi(\beta(z))\,\phi(z)\,\mathrm dz
  \;=\;
  (N - 1)\,I(\rho).
  \tag{5.6}
$$
Therefore
$$
  A_0(\rho) \,=\, \tfrac{1}{4N}\,p^H + \tfrac{1}{2}\,\CR\,I(\rho),
  \qquad
  B_0(\rho) \,=\, (N - 1)\,\bigl[\tfrac{1}{4N}\,p^H + \tfrac{1}{2}\,\CR\,I(\rho)\bigr]
  \,=\, (N - 1)\,A_0(\rho).
  \tag{5.7}
$$
Substituting into (3.3):
$$
  \rstarinv \;=\; (N - 1)\,\frac{A_0(\rho)}{B_0(\rho)}
  \;=\; \frac{(N - 1)\,A_0(\rho)}{(N - 1)\,A_0(\rho)}
  \;=\; 1.
  \tag{5.8}
$$
The cancellation is exact, *independent of* $N$ (which appears in both
numerator and denominator and cancels), *independent of* $\CR$ (since
$\CR = 1$ at this corner under both variants), and *independent of*
$\rho$ (which enters only through $I(\rho)$, common to $A_0$ and $B_0$).
QED.

**Remark (numerical realisation).** The rb-012 simulation Step A registers
$\min \rstarinv = 1.0000$ in every $(\text{variant}, \rho)$ panel of the
primary $(\valid, \val)$ grid at $N = 4$
(`Rebuild/manuscript/sections/results.tex` Table tab:c4-rstar-tally, sourced
from `step_A.tally.variant_A__rho_0.0`, `step_A.tally.variant_A__rho_0.2`,
`step_A.tally.variant_B__rho_0.0`, `step_A.tally.variant_B__rho_0.2`). The
identity (5.1) is recovered to floating-point identity in all four panels,
including the ρ = 0.2 cases — confirming the ρ-cancellation of (5.7)
holds under the Gauss–Hermite-64 quadrature the simulation uses, not just
in symbolic form.

**Remark (the bimodal local picture at the corner).** At
$(\valid, \val) = (1/N, 1)$, $\rstarinv = 1$, so (3.1) reads
$\left.\partial_\alpha \Rew\right|_{1/N^-} \propto A_0\,(1 - \Rsens)$
and (symmetrically, by (2.4))
$\left.\partial_\alpha \Rew\right|_{1/N^+} \propto A_0\,(\Rsens - 1)$.
For $\Rsens > 1$ both branches *increase* $\Rew$ as $\alpha$ moves
away from $1/N$ — $\alpha = 1/N$ is a local *minimum*. The model is
bimodal in $\alpha$ at this corner; the right-branch maximum still
dominates globally (rb-012 Step D records $\alpha^\star \ge 1/N$ in
every primary-sweep cell), and the left-branch local maximum sits near
the grid edge $\alpha \to 0$. The corner is the analytic anchor the
rebuilt manuscript quotes in place of the inherited paper's narrative
"$\Rsens \to 0$ converges to uniform attention" — that narrative is
correct for $\Rsens \le 1$ at this corner (where the local picture is
monotone) but masks the bimodality that opens up at $\Rsens > 1$.

---

## 6. Value-weight inequality and the global no-inversion theorem

The closed form (3.3) describes the *local* picture at $\alpha = 1/N$.
The *global* no-inversion claim of the inherited §4.5 paragraph
(``$\alpha^\star \ge 1/N$ across all 4,410 rows'') requires a different
argument: a comparison of the right-branch and left-branch *global maxima*
of $\Rew$, not their derivatives at the boundary. The mechanism is a
combination of a value-weight inequality and a location-count asymmetry.

### 6.1 The value-weight inequality

Booking the reward (1.3) by per-channel weight:
$$
  w_c \;:=\; \valid \cdot \val
  \quad \text{(cued change-trial weight)},
  \qquad
  w_u \;:=\; \frac{1 - \valid}{N - 1}
  \quad \text{(per-uncued change-trial weight)}.
  \tag{6.1}
$$
Routine algebra:
$$
  w_c \;\ge\; w_u
  \;\;\iff\;\;
  \valid\,\val\,(N - 1) \;\ge\; (1 - \valid)
  \;\;\iff\;\;
  \valid \;\ge\; \frac{1}{(N - 1)\,\val + 1}.
  \tag{6.2}
$$
The right-hand side of (6.2) is bounded above by $1/N$ for $\val \ge 1$
(with equality only at $\val = 1$), so
$$
  \valid \;\ge\; 1/N \;\;\text{and}\;\; \val \;\ge\; 1
  \;\;\implies\;\;
  w_c \;\ge\; w_u,
  \tag{6.3}
$$
with equality only at the symmetric corner of §5. This is **Eq.
value-weight** of the manuscript §results-c4 paragraph "Mechanism and
the value-weight inequality".

### 6.2 Location-count asymmetry

At the right extreme $\alpha \to 1$, the single cued location reaches its
per-location ceiling $\dprime_c = \dprimemax\,f(1) = \dprimemax$
(via (1.2) with $f(1) = 1$). At the left extreme $\alpha \to 0$, the
$N - 1$ uncued locations *share* the budget at $(1 - \alpha)/(N - 1)$ each,
so each reaches only
$\dprime_u = \dprime_{\mathrm{base}} + \benefit\bigl[\dprimemax\,f(1/(N - 1))
- \dprime_{\mathrm{base}}\bigr] \le \dprimemax$, with strict inequality
whenever $f(1/(N - 1)) < 1$ — that is, whenever $1/(N - 1) < 1$, i.e.
$N \ge 3$. For $N \ge 3$, **no left-branch allocation reaches the
per-location ceiling**; the right branch alone can attain $\dprimemax$.

### 6.3 Combination: global no-inversion theorem (conditional)

Combining (6.3) and the location-count asymmetry §6.2:

> **Theorem 6.1 (global no-inversion).** *Under
> $\valid \ge 1/N$ and $\val \ge 1$ (equivalently, the sharp form
> $\valid \ge 1/[(N - 1)\val + 1]$), the global maximum of the P1 expected
> reward (1.3) satisfies $\alpha^\star \ge 1/N$: the right-branch global
> maximum strictly dominates the left-branch global maximum for any
> $\Rsens \in (0, \infty)$, with equality at the symmetric corner of §5
> for $\Rsens \le 1$.*

**Sketch.** At any right-branch allocation $\alpha$, the cued slot
carries weight $w_c \ge w_u$ (by 6.3) and its $\dprime_c$ can reach
$\dprimemax$ (the location ceiling); at any left-branch allocation,
the per-slot weight on the over-allocated uncued locations is $w_u \le w_c$
and their $\dprime_u$ is capped strictly below $\dprimemax$ for $N \ge 3$
(by §6.2). The right branch therefore gets the *bigger* $\dprime$ on the
*more-valuable* channel; the left branch gets the *smaller* $\dprime$ on
the *less-valuable* channel(s). For any $\Rsens$ this strictly favours
the right-branch global maximum. (A full proof requires checking the
strict-inequality bookkeeping at the boundary $\Rsens \to 0$ — see
rb-012 Step B for the empirical primary-sweep confirmation across 12
adversarial probes, $0$ global inversions, both $\rho \in \{0, 0.2\}$.
The inherited paper's empirical 4,410-row claim is the primary
*observational* anchor for the theorem.)

### 6.4 Failure of the conditional: the anti-cue prediction

Theorem 6.1 holds **only** under both inequalities of (6.3) — most
relevantly, $\valid \ge 1/N$ (or the sharp form $\valid \ge 1/[(N - 1)\val + 1]$).
When the validity is below the chance level $\valid < 1/N$, the value-weight
inequality (6.3) flips:
$$
  \valid \;<\; 1/[(N - 1)\,\val + 1]
  \;\;\implies\;\;
  w_c \;<\; w_u.
  \tag{6.4}
$$
The per-channel uncued weight strictly exceeds the cued weight. The
location-count asymmetry §6.2 still caps the left branch at
$\dprime_u < \dprimemax$, but the per-channel reward now favours the
uncued slots, and the cued cap of $\dprimemax$ no longer compensates.
For $\Rsens$ sufficiently large (the benefit-dominant regime), the global
maximum *crosses below* $1/N$ — an anti-cue inversion.

The rebuilt model predicts this inversion as a *positive consequence* of
the normative framework, not as a bug. rb-012 Step C records it
empirically at $N = 4$ (the inherited paper's primary topology) across
$V \in \{0.05, 0.10, 0.15, 0.20\}$, $\val \in \{1, 3, 5\}$,
$\Rsens \in \{0.1, 0.5, 1, 3, 5, 10\}$, $\rho \in \{0, 0.2\}$: 36.1%
of probed anti-cue cells exhibit $\alpha^\star_{\mathrm{global}} < 1/N$
at $\rho = 0$ (34.7% at $\rho = 0.2$), with the $\val$-stratification
($75\%$ at $\val = 1$, $20.8\%$ at $\val = 3$, $12.5\%$ at $\val = 5$)
matching the sharp boundary $\valid < 1/[(N - 1)\val + 1]$: at $\val = 5$,
$N = 4$ the boundary collapses to $\valid < 1/16 \approx 0.0625$ (only
$V = 0.05$ qualifies); at $\val = 1$ the boundary is the universal
$\valid < 1/N$ and inversion is dense. The anti-cue inversion is the
**new falsifiable prediction** the rebuild adds to the inherited paper
(`Rebuild/manuscript/sections/results.tex` §results-c4, "Anti-cue
inversion prediction" paragraph).

---

## 7. Numerical realisation and the sim attribution

All numerical claims in this derivation are sourced from
`Rebuild/sims/C4--anti-cue-inversion/` (RB-008, run id rb-012), output
sha256 `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`,
17.4 s wall-clock on python3.13 / scipy 1.17.1 / numpy 2.4.4. The
correspondence between this derivation's equations and the simulation's
code is:

| derivation equation | simulation code (`run.py` line) | result key in `output/results.json` |
| --- | --- | --- |
| (3.3) closed-form $\rstarinv$ | `r_inv_threshold()` lines 260–278 | `step_A.tally.variant_<X>__rho_<rho>` |
| (4.4) ρ-aware $A_0, B_0$ | `_A0_B0()` lines 210–257 | (intermediate; not stored per-cell) |
| (4.5)–(4.6) ρ = 0 collapse | `_A0_B0()` lines 223–233 (analytic branch) | `recovery_step_Ci.rows` (PASS) |
| (4.2)–(4.3) ρ > 0 quadrature | `_A0_B0()` lines 239–253 (GH branch) | `step_A.tally.variant_<X>__rho_0.2` |
| (5.1) symmetric-corner identity | `r_inv_threshold()` evaluated at (V=1/N, v=1) | `min(step_A.r_inv_star)` = 1.0000 in all 4 panels |
| (6.4) anti-cue boundary $V < 1/[(N-1)v+1]$ | `step_C` probe grid (`run.py` Step C) | `step_C.incidence_by_v_rho0`, `step_C.incidence_by_r_rho0` |

Two recovery tests are recorded by the simulation:

- **Recovery #1 (ρ = 0 vs the inherited closed form).** rb-012 Step A
  evaluates (3.3) on the inherited $N = 4$ primary $(\valid, \val,
  \mathrm{variant})$ grid at $\rho = 0$ and tallies $\rstarinv \in [0.1,
  10]$: $48.6\%$ of $210$ cells, against the reviewer's $49.0\%$
  (`Critique/derivations/C4--no-inversion.md` §4). $\Delta = 0.4$
  percentage points, PASS at the simulation's $1.0$ pp tolerance. The
  residual is a grid-tie reclassification near the $\rstarinv \in
  \{0.1, 10\}$ borders, not a numerical drift in (4.4) at ρ = 0.

- **Recovery #2 (ρ = 0 against Step C(i) of the reviewer's derivation).**
  rb-012 evaluates the full $\Rew(\alpha)$ curve at $(\valid, \val, N) =
  (0.25, 1, 4)$, variant A, $\rho = 0$, $\Rsens \in \{0.1, 1, 1.585,
  2.512, 3.981, 10\}$ and compares $(\alpha^\star, R^\star)$ against
  the reviewer's Step C(i) table: $\max\,|\Delta\alpha^\star| = 0$
  (floating-point identity), $\max\,|\Delta R^\star| = 3 \times 10^{-6}$
  (PASS at tolerances $5 \times 10^{-4}$, $5 \times 10^{-5}$).

- **Identity #3 (symmetric-corner, ρ > 0 inclusive).** The minimum of
  $\rstarinv$ in every $(\text{variant}, \rho)$ panel of `step_A.tally`
  is $1.0000$ to floating-point identity, including the ρ = 0.2
  panels. This is (5.1) recovered against the one-factor GH-64
  quadrature, not just in symbolic form — a stronger statement than
  recovery #1 (which is a numerical match against the inherited form;
  the symmetric-corner identity is an algebraic cancellation that
  survives the quadrature exactly).

---

## 8. Scope and what the derivation does *not* claim

- **The closed form (3.3) is a local statement.** It describes the sign
  of $\left.\partial_\alpha \Rew\right|_{1/N^-}$. A negative left
  derivative does **not** imply a global inversion; it implies only a
  *left-branch local maximum* at $\alpha = \alpha_l^\star < 1/N$. The
  global no-inversion claim under $\valid \ge 1/N$ is Theorem 6.1, and
  the right-branch maximum strictly dominates the left-branch local
  maximum across the inherited paper's primary sweep (rb-012 Step B:
  $0/12$ global inversions across all 12 adversarial cells under both
  $\rho \in \{0, 0.2\}$).

- **The ρ-extension (4.2)–(4.4) is for equicorrelated noise only.** It
  inherits the same scoped limitation as the rebuilt model's $\Pnofa(\rho)$
  routine (Section §6 of `Rebuild/derivations/A1--rho-channel.md`): a
  structured covariance (distance-dependent, attention-modulated)
  would require either a richer reduction or a Monte-Carlo evaluation
  of the orthant probability and is out of scope for this derivation.

- **The conservation rule is the inherited $\benefit + \cost = 2$
  (additive A3).** Under a multiplicative conservation $\benefit \cdot
  \cost = 1$, equations (1.5)–(1.6) and hence (2.4)–(2.5) change form,
  and the closed-form threshold (3.3) takes a different shape (see
  `Critique/derivations/C4--no-inversion.md` §10's brief sketch for
  the multiplicative analog). The rebuilt model's conservation-family
  extension is the parallel queued increment RB-015/RB-019 (A3); when
  it lands, the manuscript will report (3.3) as a band over the
  conservation family rather than as a point.

- **The global no-inversion theorem (Theorem 6.1) is stated with an
  empirical-anchor sketch, not a fully formal proof.** The
  $\dprime$-ceiling argument of §6.2 and the value-weight inequality of
  §6.1 jointly *necessitate* right-branch dominance under (6.3), but a
  formal envelope-theorem argument over the joint $(c_c, c_u)$
  optimisation at every $\alpha$ requires more bookkeeping than this
  derivation undertakes. The rebuild treats the 4,410-row primary
  sweep + the rb-012 Step B 12-cell adversarial probe (both records $0$
  global inversions under $\valid \ge 1/N$, $\val \ge 1$, $N = 4$) as
  the *observational* anchor for Theorem 6.1, and the value-weight
  inequality + location-count asymmetry as the *mechanistic
  explanation*. A formal proof is a candidate spin-off increment.

- **The anti-cue prediction (§6.4) is stated at $N = 4$ and variant A.**
  Step C of rb-012 ran only variant A at $N = 4$ within the wall-clock
  budget; the variant-B replication is RB-031 (queued), and the
  V-threshold sharpening at $\val = 1$ (the universal $\valid < 1/N$
  boundary) is RB-032 (queued). The qualitative pattern across the
  $(r, v, V)$ stratifiers in §6.4 is preserved across ρ ∈ {0, 0.2}
  (rb-012 Step C: $26$ vs $25$ inversions, $\Delta = 1$).

---

## 9. References

- Inherited paper §4.5 ("Inverted Attention is Never Optimal"),
  `Critique/source/main.pdf` (Herman Lab, 2026-04-09).
- Reviewer's parallel derivation in attack voice:
  `Critique/derivations/C4--no-inversion.md` (run-006, 2026-05-18) —
  same math, different framing.
- Companion simulation: `Rebuild/sims/C4--anti-cue-inversion/`
  (RB-008, rb-012, sha256 `6ad651d648ae597cdfb28c6fd19b6261e4f9d5cb96b599557e10aad47ffd6d96`).
- Manuscript §results-c4 (`Rebuild/manuscript/sections/results.tex`)
  drafted at rb-013 (RB-012) — this derivation backs Eqs.
  `value-weight`, `left-derivative`, `r-inv`, `r-inv-corner` of that
  section.
- The ρ-extension machinery (one-factor Gauss–Hermite reduction of the
  equicorrelated orthant) is the same construction used in
  `Rebuild/derivations/A1--rho-channel.md` §2 (RB-003, rb-008).
- Slepian D., 1962. "The one-sided barrier problem for Gaussian noise."
  *Bell System Technical Journal* 41(2): 463–501. (Foundational result
  for the orthant monotonicity used in §2.3 of the companion A1
  derivation; not invoked here.)
- Tong Y. L., 1990. *The Multivariate Normal Distribution*. Springer.
  (Reference for the one-factor representation used to reduce (4.1)
  to a one-dimensional integral.)

The two textbook references (Slepian, Tong) are cited by full
bibliographic reference rather than `research_db/papers/` id — both
are mathematical-methods classics that the rebuild's wiki does not yet
stub (a gap shared with `Rebuild/derivations/A1--rho-channel.md`).
This is a documented gap, not a defect; no new wiki stub is added by
this derivation.

---

**Verification performed.**

- (4.5)–(4.6) ρ = 0 collapse: verified by inspection of
  `Rebuild/sims/C4--anti-cue-inversion/run.py:_A0_B0` lines 223–233
  against (4.7)–(4.8); the analytic branch is exactly the inherited
  closed form.
- (5.1) symmetric-corner identity: verified algebraically in §5
  (proof of Proposition 5.1) and numerically against
  `step_A.tally.variant_<X>__rho_<rho>.min_r_inv_star = 1.0000` in all
  four panels (variant A/B × $\rho$ ∈ {0, 0.2}).
- (3.3) recovery vs reviewer §4: 48.6% vs 49.0%, $\Delta = 0.4$ pp
  (PASS at 1.0 pp tolerance, rb-012 recovery #1).
- (2.4)–(2.5) one-sided derivatives: cross-check at the symmetric
  corner against (5.3)–(5.7) — both branches reduce to
  $A_0\,(\Rsens - 1)$ (right) / $A_0\,(1 - \Rsens)$ (left) up to
  the strictly positive prefactor of (3.1), so the sign-flip is
  exactly at $\Rsens = 1 = \rstarinv$ as required.
- (6.2) value-weight inequality: verified algebraically — the
  reverse implication is routine; the forward implication is
  $V[(N-1)v + 1] \ge 1$ algebraically equivalent to
  $V \ge 1/[(N-1)v + 1]$.
- ρ > 0 sign-flip-locus shift (rb-012 Step A): median $\rstarinv$
  drops 13% (variant A) and 21% (variant B) from $\rho = 0$ to
  $\rho = 0.2$; the fraction with $\rstarinv \in [0.1, 10]$ rises
  from $48.6\%$ to $51.9\%$ (variant-pooled). Consistent with the
  partial derivative $\partial \rstarinv / \partial \rho$ being
  negative on average across the primary grid — a candidate
  follow-up derivation (Slepian-style monotonicity on the
  ratio $A_0/B_0$ as a function of $\rho$).

**Extensions to consider.**

1. **Closed form for $\partial \rstarinv / \partial \rho$.** The
   simulation records a $\sim 13$–$21\%$ drop in median $\rstarinv$
   from $\rho = 0$ to $\rho = 0.2$; an analytic sign on this drop
   (analogous to the Slepian-style sign argument in §3 of
   `Rebuild/derivations/A1--rho-channel.md`) would let the manuscript
   state the direction of the A1 shift as a theorem rather than an
   empirical observation. Candidate spin-off increment.
2. **Variant B anti-cue replication.** rb-012 Step C runs variant A
   only. RB-031 is queued and would extend the anti-cue prediction
   across the reward convention.
3. **Conservation-family band on (3.3).** RB-015/RB-019 will produce
   $A_0, B_0$ under a parameterised conservation family with additive
   and multiplicative as special cases. The closed form (3.3) then
   becomes a band over the family rather than a point. The structural
   pattern (3.3) — ratio of $\Rsens$-independent boundary partials
   scaled by $(N - 1)$ — is *robust* in form to A3, but the band
   width is informative for the rebuilt paper's headline numbers.
4. **Heterogeneous-$r_i$ generalisation.** Under A2 relaxation
   (heterogeneous per-location $r_i$, queued increment RB-014/RB-018),
   the $\benefit, \cost$ pair becomes location-indexed. The boundary
   left derivative at $\alpha = 1/N$ then carries a vector of
   $(\benefit_i, \cost_i)$ rather than a scalar pair, and (3.3)
   generalises to an $N$-dimensional sign-flip condition rather than
   a scalar threshold. This is a substantive extension worth a
   dedicated derivation increment if the rebuilt model goes there.

*End of derivation.*
