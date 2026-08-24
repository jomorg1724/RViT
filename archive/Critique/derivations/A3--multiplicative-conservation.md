# Re-derivation: the multiplicative alternative $\beta\gamma=1$ to assumption A3

**Claim / assumption attacked:** A3 (mission §2.7) — the benefit/cost
asymmetry is governed by the *additive* conservation rule
$\beta+\gamma=2$. The paper flags the alternative in §5.5 (p.8):

> "the $\beta + \gamma = 2$ constraint conserves total attention
> magnitude; alternative constraints (e.g., multiplicative
> $\beta\gamma = 1$) could yield quantitatively different results,
> though the qualitative findings—non-monotonic VDA, no inversion,
> criterion dominance—should be robust."

**Attack vector:** re-derivation (mission §3.2), with a focused
replication slice (`Critique/replications/A3--multiplicative-conservation/`)
for numerical corroboration.

**Run:** run-010, prompt v0.2, 2026-05-22, task CR-040.

---

## 0. Setup and notation

The asymmetric per-location sensitivities (mission §2.4) are

$$
d'_{\text{cued}}(\alpha) = d'_{\text{base}} + \beta\,\big[\,d'_{\max} f(\alpha) - d'_{\text{base}}\,\big],
\qquad
d'_{\text{uncued}}(\alpha) = d'_{\text{base}} + \gamma\,\big[\,d'_{\max} f\!\big(\tfrac{1-\alpha}{N-1}\big) - d'_{\text{base}}\,\big],
$$

with $d'_{\text{base}} = d'_{\max} f(1/N)$, all $d'$ clamped at $\ge 0$,
and the $(\beta,\gamma)$ roles swapping across the kink $\alpha=1/N$.
The two scalars $\beta,\gamma>0$ are pinned by **two** conditions:

1. the **ratio** condition (definitional, common to all variants):
   $$\beta/\gamma = r, \qquad r>0; \tag{R}$$
2. a **conservation** condition that fixes the overall scale. The
   paper uses the *additive* rule
   $$\beta+\gamma = 2 \quad\text{(A3)}, \tag{C\(_+\)}$$
   and floats the *multiplicative* rule
   $$\beta\gamma = 1 \quad\text{(the §5.5 alternative)}. \tag{C\(_\times\)}$$

This derivation solves both, proves they are related by a single
closed-form rescaling, derives the consequences for the three named
qualitative findings, and checks each against the slice.

---

## 1. The two weight families in closed form

### 1.1 Additive (the model, A3)

Substituting $\beta=r\gamma$ from (R) into (C$_+$):
$r\gamma+\gamma=2 \Rightarrow \gamma=\tfrac{2}{r+1}$, hence

$$
\boxed{\;\beta_{+}(r)=\frac{2r}{r+1},\qquad \gamma_{+}(r)=\frac{2}{r+1}\;}
\tag{1}
$$

matching mission §2.4. Range: $\beta_{+}\in(0,2)$, $\gamma_{+}\in(0,2)$;
both bounded.

### 1.2 Multiplicative (the §5.5 alternative)

Substituting $\beta=r\gamma$ into (C$_\times$):
$r\gamma^2=1 \Rightarrow \gamma=r^{-1/2}$, hence

$$
\boxed{\;\beta_{\times}(r)=\sqrt{r},\qquad \gamma_{\times}(r)=\frac{1}{\sqrt{r}}\;}
\tag{2}
$$

Range: $\beta_{\times}\in(0,\infty)$, $\gamma_{\times}\in(0,\infty)$;
**unbounded** — the larger weight diverges as $r$ leaves $1$.

### 1.3 Agreement at $r=1$ (the C5 bridge)

At $r=1$, (1) gives $(\beta_+,\gamma_+)=(1,1)$ and (2) gives
$(\beta_\times,\gamma_\times)=(1,1)$. Both families collapse to the
symmetric pair, so **C5's symmetric recovery is constraint-agnostic**:
$\beta\gamma=1 \wedge \beta+\gamma=2 \Rightarrow \beta=\gamma=1$ is the
unique common solution. The slice confirms this — at $r=1$ the two
families return *identical* $\text{VDA}=0.03983$, $\text{CF}=0.7282$,
$\alpha^\star_{P1}=1.000$, $\alpha^\star_{P2}=0.750$ to all printed
digits. The A3 content therefore lives **entirely off** $r=1$.

---

## 2. The rescaling theorem — multiplicative $=$ $\kappa(r)\times$ additive

**Theorem 1.** *For all $r>0$,*
$$
\frac{\beta_{\times}(r)}{\beta_{+}(r)} \;=\; \frac{\gamma_{\times}(r)}{\gamma_{+}(r)} \;=\; \kappa(r), \qquad
\kappa(r) := \frac{r+1}{2\sqrt{r}} = \tfrac12\!\left(\sqrt{r}+\tfrac1{\sqrt r}\right) = \cosh\!\big(\tfrac12\ln r\big).
$$

*Proof.* 
$\dfrac{\beta_\times}{\beta_+} = \dfrac{\sqrt r}{\,2r/(r+1)\,} = \dfrac{\sqrt r\,(r+1)}{2r} = \dfrac{r+1}{2\sqrt r}$,
and
$\dfrac{\gamma_\times}{\gamma_+} = \dfrac{r^{-1/2}}{\,2/(r+1)\,} = \dfrac{r+1}{2\sqrt r}$.
The two ratios coincide. Writing $r=e^{u}$ gives
$\kappa = \tfrac12(e^{u/2}+e^{-u/2}) = \cosh(u/2)$. $\;\square$

So $(\beta_\times,\gamma_\times) = \kappa(r)\,(\beta_+,\gamma_+)$: the
multiplicative weights are the additive weights scaled by **one common
factor** $\kappa(r)$.

**Corollary 1.1 (properties of $\kappa$).**
$\kappa(r)\ge 1$ with equality iff $r=1$ (it is $\cosh$ of something);
$\kappa(1/r)=\kappa(r)$ (symmetric in $\ln r$); $\kappa\to\infty$ as
$r\to 0^+$ or $r\to\infty$. Numerically $\kappa(0.3)\approx1.20$ (at the
VDA peak), $\kappa(0.1)=\kappa(10)\approx1.74$ (at the swept extremes).
Verified to $8.9\times10^{-16}$ across the grid (slice Block 0).

**Corollary 1.2 (no magnitude conservation under $\beta\gamma=1$).**
$$
\beta_\times+\gamma_\times = \kappa(r)\,(\beta_++\gamma_+) = 2\kappa(r) \ge 2,
\qquad
\beta_+\gamma_+ = \frac{4r}{(r+1)^2} = \frac{1}{\kappa(r)^2}\le 1 .
$$
Thus the paper's phrase *"$\beta+\gamma=2$ conserves total attention
magnitude"* is an **additive-only** property. The multiplicative rule
conserves the *geometric* mean ($\sqrt{\beta\gamma}=1$) and lets the
*arithmetic* mean inflate as $\kappa(r)$. The two constraints are **not
interchangeable reparameterisations**: no additive $r'$ reproduces a
multiplicative weight pair, because $\beta_++\gamma_+\equiv 2$ can never
equal $2\kappa>2$.

**Corollary 1.3 (geometric picture).** In the $(\beta,\gamma)$ quadrant
the additive family is the segment of the line $\beta+\gamma=2$; the
multiplicative family is the branch of the hyperbola $\beta\gamma=1$. By
AM–GM, $\beta+\gamma\ge 2\sqrt{\beta\gamma}=2$ on the hyperbola, so the
hyperbola lies **on or above** the line everywhere, **tangent only at**
$(1,1)$. Hence the $\beta\gamma=1$ model imposes *uniformly larger
departures* from baseline than $\beta+\gamma=2$, except at $r=1$ where
they touch. This single fact predicts the *direction* of every
quantitative shift below (larger VDA, lower CF) before any sweep.

---

## 3. Consequence for C2 — the two-limit theorem is constraint-robust

The non-monotonicity claim C2 rests (CR-001, derivation
`C2--non-monotonic-vda.md`) on a *two-limit theorem*: $\text{VDA}(r)\to0$
as $r\to0^+$ and as $r\to\infty$, with strict positivity on an interior
interval. The mechanism is that the **benefit** weight on the cued
location vanishes at small $r$ (so P1 cannot out-earn the value-blind
P2) and the **cost** weight on the uncued locations vanishes at large
$r$ (so both P1 and P2 drive $\alpha\to1$ and the gap closes).

**Proposition 3.1.** *Both conservation rules satisfy*
$\beta(0^+)=0$ *and* $\gamma(\infty)=0$, *so the two-limit theorem — and
hence the qualitative non-monotonicity of C2 — holds under both.*

*Proof.* Additive: $\beta_+(0)=0$, $\gamma_+(\infty)=0$ from (1).
Multiplicative: $\beta_\times(0)=\sqrt 0=0$, $\gamma_\times(\infty)=1/\sqrt\infty=0$
from (2). At $r\to0^+$ the cued bracket in $d'_{\text{cued}}$ is
multiplied by $\beta\to0$, so $d'_{\text{cued}}\to d'_{\text{base}}$ for
every $\alpha\ge1/N$; P1's only lever (boost the cued location) is
disabled, so $\alpha^\star_{P1}\to1/N$, the same uniform allocation P2
takes at $v=1$ — hence $\text{VDA}\to0$. At $r\to\infty$ the uncued
bracket is multiplied by $\gamma\to0$, so reallocating toward the cued
location costs nothing; both P1 and P2 push $\alpha\to1$ and the gap
closes — $\text{VDA}\to0$. $\;\square$

The slice corroborates and quantifies (Block 1):

| family | peak $r$ | peak VDA | $\text{VDA}(0.1)$ | $\text{VDA}(10)$ |
|---|---|---|---|---|
| additive | $0.398$ | $0.0797$ | $0.0185$ | $0.00085$ |
| multiplicative | $0.316$ | $0.0909\ (+14\%)$ | $0.0411$ | $0.00317$ |

Both single-peaked in the cost-dominant regime $r<1$. The peak shifts
**one log-grid step left** ($0.398\to0.316$, deeper into
cost-dominance) and rises **14%** under $\beta\gamma=1$ — exactly the
direction Corollary 1.3 predicts, since $\kappa(r)>1$ inflates the
interior departures while leaving the two vanishing limits intact. The
additive peak $0.0797$ lands on the paper's Figure-4 reference
($\sim0.080$), validating the implementation. **C2 qualitative claim:
robust; quantitative location/magnitude: shifts as the paper warned.**

---

## 4. Consequence for C1 — criterion dominance survives but erodes

$\text{CF}(r) = \dfrac{R(P3)-R(P4)}{R(P1)-R(P4)}$. The policies P3 and P4
both sit at $\alpha=1/N$, where the brackets in §0 are *exactly zero*
(since $f(1/N)=f(1/N)$), so $d'_{\text{cued}}=d'_{\text{uncued}}=d'_{\text{base}}$
**regardless of $\beta,\gamma$**.

**Proposition 4.1.** *$R(P3)$ and $R(P4)$ are identical under both
conservation rules; the entire constraint-dependence of CF is carried
by the denominator $R(P1)$.*

*Proof.* Immediate from the previous sentence: at $\alpha=1/N$ the
weights multiply $0$, so the P3/P4 sensitivities — and the rewards
optimised over criteria from them — do not see $\beta,\gamma$.
$\;\square$

Because the hyperbola lies above the line (Cor. 1.3), the P1 attentional
gain $R(P1)-R(P4)$ is *larger* under $\beta\gamma=1$ wherever the cued
boost is the binding lever (large $r$, where $\beta_\times=\sqrt r$
greatly exceeds $\beta_+\to2$). A larger denominator with a fixed
numerator gives a **smaller** CF. The slice (Block 2):

| family | $\text{CF}(0.1)$ | $\text{CF}(1)$ | $\text{CF}(10)=\min$ |
|---|---|---|---|
| additive | $0.961$ | $0.728$ | $\mathbf{0.601}$ |
| multiplicative | $0.917$ | $0.728$ | $\mathbf{0.507}$ |

Criterion dominance (CF $>0.5$: criterion captures the *majority* of
value-related reward) **survives at this slice**, but the floor drops
$0.601\to0.507$ — only $0.007$ above the $50\%$ line at $r=10$.

**Loose end → second vector.** C1 is *already* CONTESTED under the
additive rule (run-003: CF down to $0.304$ in variant-B, low-$V$,
high-$v$ cells *outside* this slice). Since $\beta\gamma=1$ lowers CF
wherever $R(P1)$ can grow, those same cells will plausibly push CF
**below $0.5$** under $\beta\gamma=1$ — i.e. criterion dominance may
*fail* in part of the space the paper claims robustness for. This slice
does not visit those cells (mission §8.5). The full multiplicative
replication is the designated second attack (CR-008).

---

## 5. Consequence for C4 — no inversion is constraint-robust within $V\ge1/N$

The no-inversion result (CR-004, derivation `C4--no-inversion.md`) is
driven by **location-count asymmetry** combined with the value-weight
inequality: at $\alpha\to1$ the single cued location reaches
$d'_{\max}f(1)=d'_{\max}$, whereas at $\alpha\to0$ each of the $N-1$
uncued locations reaches only $d'_{\text{base}}+\beta[d'_{\max}f(1/(N-1))-d'_{\text{base}}]<d'_{\max}$
for $N\ge3$; with $w_c=Vv\ge w_u=(1-V)/(N-1)$ (i.e. $V\ge1/N$ for
$v\ge1$) the right branch dominates globally.

The *structural* ingredients — $f(1)=1$ vs $f(1/(N-1))<1$, and
$w_c\ge w_u$ — **do not involve $\beta,\gamma$**, so the global
no-inversion conclusion is insensitive to the conservation rule within
$V\ge1/N$. (The CR-004 *boundary threshold* $r^\star_{\text{inv}}$ does
involve $\beta,\gamma$ and so moves in $r$-space under $\beta\gamma=1$,
but it governs only the local one-sided derivative, not the global
argmax.) Slice Block 3 confirms: $\min\alpha^\star_{P1/P2}=0.2500=1/N$
across the reference $r$-grid and the most-adversarial $V\ge1/N$ cells at
$r=10$, under multiplicative — **no inversion**. (C4 already provably
*fails* for $V<1/N$ under *both* rules; that is the CONFIRMED-CONDITIONAL
scope of C4, not re-opened here.)

---

## 6. Verdict implication

The paper's §5.5 robustness claim has three conjuncts; under the
multiplicative constraint $\beta\gamma=1$, on the reference slice:

1. **non-monotonic VDA** — ROBUST (two-limit theorem, Prop. 3.1; peak
   shifts $0.398\to0.316$, $+14\%$);
2. **no inversion** — ROBUST within $V\ge1/N$ (location-count
   mechanism, §5);
3. **criterion dominance** — SURVIVES-BUT-ERODES (CF floor
   $0.601\to0.507$; thin margin; may break in the cells where C1 is
   already CONTESTED — flagged as CR-008).

No qualitative finding broke on this slice, so the robustness claim is
**WEAKLY-SUPPORTED** (first attack vector; per mission §6 cannot elevate
on one run). The incidental claim *"$\beta+\gamma=2$ conserves total
attention magnitude"* should be read narrowly: $\beta\gamma=1$ does
**not** conserve it (Cor. 1.2), and that magnitude inflation
$\kappa(r)$ is the single mechanism behind all three quantitative
shifts.

### What the paper does and does not show
- **Does:** name $\beta\gamma=1$ as the alternative and assert
  qualitative robustness (§5.5).
- **Does not:** run it; quantify the shift; or note that $\beta\gamma=1$
  fails to conserve total magnitude (so the two rules are not
  symmetric). This derivation supplies all three.

### Designated next attacks (spawned)
- **CR-008** (replication, second vector): full multiplicative
  $(V,v,\text{variant})$ sweep restricted to the cells where additive
  CF $<0.60$ (run-003 output), to decide whether criterion dominance
  (CF $>0.5$) survives $\beta\gamma=1$ globally or breaks.
- **CR-0xx** (sensitivity): does the C2 peak-shift direction
  ("left+up under $\beta\gamma=1$") hold across the $f_0$ and $h$
  secondary sweeps, where $\kappa(r)$ interacts with the $r^\dagger(v)$
  escape thresholds of CR-001?

---

## Appendix — symbols

| symbol | meaning |
|---|---|
| $r$ | benefit/cost asymmetry ratio, $\beta/\gamma=r$ |
| $\beta_+,\gamma_+$ | additive weights, $2r/(r+1),\,2/(r+1)$ |
| $\beta_\times,\gamma_\times$ | multiplicative weights, $\sqrt r,\,1/\sqrt r$ |
| $\kappa(r)$ | rescaling factor $(r+1)/(2\sqrt r)=\cosh(\tfrac12\ln r)$ |
| $f(\alpha)$ | transfer function $f_0+(1-f_0)h(\alpha)$ |
| $d'_{\text{base}}$ | $d'_{\max}f(1/N)$, uniform-allocation sensitivity |
| VDA | $R(P1)-R(P2)$, value-directed-attention benefit |
| CF | criterion fraction $[R(P3)-R(P4)]/[R(P1)-R(P4)]$ |
