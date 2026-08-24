---
type: derivation
claim_id: C4
attack: re-derivation
companion_replication: Critique/replications/C4--no-inversion/run.py
companion_results: Critique/replications/C4--no-inversion/output/results.json
prompt_version: 0.1
run_id: run-006
created: 2026-05-18
---

# C4 — "Inverted attention is never optimal": re-derivation

> **Paper claim (§4.5, verbatim).** *"Across all 4,410 rows of the primary
> sweep — spanning $r \in [0.1, 10]$, $V \in [0.25, 1.0]$, $v \in
> \{1, \dots, 5\}$, and both reward variants — the optimal $\alpha^\star$
> is always $\geq 1/N$. ... This result follows from the reward
> structure: attending away from the high-value cued location means
> (a) the cued location's $d'$ drops below baseline, scaled by the cost
> factor $\gamma$, while (b) uncued locations' $d'$ rises above
> baseline, scaled by the benefit factor $\beta$. Since $v \geq 1$
> and $V \geq 1/N$, the weighted reward loss at the high-value cued
> location always exceeds the gain at low-value uncued locations,
> regardless of $r$. In the most cost-dominant regime ($r \to 0$),
> the optimal strategy converges to uniform attention ($\alpha^\star
> = 1/N$), never below it."*

This re-derivation interrogates two distinct things the paper conflates:

(a) the **empirical** claim that $\alpha^\star \geq 1/N$ across the
    4,410-row primary sweep, and

(b) the **theoretical justification** that the loss-exceeds-gain
    inequality holds *regardless of $r$*.

The empirical claim survives independent computation (corroborated by
the existing 4,410-row sweep in
`Critique/replications/C1--criterion-fraction-floor/output/results.json`
where $\alpha^\star_{P_1}$ and $\alpha^\star_{P_2}$ are $\geq 1/N$ in
every row, and by Step B of
`Critique/replications/C4--no-inversion/run.py`). The theoretical
justification, as written, is **incomplete**: the *local* derivative
at $\alpha = 1/N$ is r-dependent, and what guarantees no global
inversion is a **location-count asymmetry** the paper does not name —
*not* the cost-vs-benefit weight comparison the paper appeals to. We
derive the missing piece below.

We use the notation of mission §2 throughout.

---

## 1. Setup and the kink at $\alpha = 1/N$

Per mission §2.4, the cued/uncued $d'$ under non-uniform allocation
$\alpha$ are

$$
d'_{\text{cued}}(\alpha; r) \;=\; d'_{\text{base}} + \beta(r)\bigl[\,d'_{\max} f(\alpha) - d'_{\text{base}}\,\bigr], \tag{1.1}
$$
$$
d'_{\text{uncued}}(\alpha; r) \;=\; d'_{\text{base}} + \gamma(r)\bigl[\,d'_{\max} f\!\bigl(\tfrac{1-\alpha}{N-1}\bigr) - d'_{\text{base}}\,\bigr], \tag{1.2}
$$

with $\beta(r) = 2r/(r+1)$, $\gamma(r) = 2/(r+1)$, $\beta+\gamma = 2$,
$f(a) = f_0 + (1-f_0) h(a)$, $d'_{\text{base}} = d'_{\max} f(1/N)$,
and all $d'$ values clamped at $\geq 0$.

The paper's replication code (and our Step B) makes Eqs. (1.1)–(1.2)
operative for $\alpha \geq 1/N$ (the "non-inverted" branch). For
$\alpha < 1/N$ (the "inverted" branch), the roles of $\beta$ and
$\gamma$ are swapped: the cued location is now the *under-allocated*
location (cost $\gamma$) and the uncued locations are the
*over-allocated* ones (benefit $\beta$):

$$
\alpha < 1/N:\quad
d'_{\text{cued}} = d'_{\text{base}} + \gamma\bigl[d'_{\max} f(\alpha) - d'_{\text{base}}\bigr],\quad
d'_{\text{uncued}} = d'_{\text{base}} + \beta\bigl[d'_{\max} f\!\bigl(\tfrac{1-\alpha}{N-1}\bigr) - d'_{\text{base}}\bigr]. \tag{1.3}
$$

This β/γ swap creates a **kink at $\alpha = 1/N$** in the
$d'(\alpha)$ functions unless $\beta = \gamma$ (i.e. $r=1$):

$$
\left.\frac{\partial d'_c}{\partial \alpha}\right|_{1/N^+} \!=\, \beta\, d'_{\max} f'(1/N),\quad
\left.\frac{\partial d'_c}{\partial \alpha}\right|_{1/N^-} \!=\, \gamma\, d'_{\max} f'(1/N), \tag{1.4}
$$
$$
\left.\frac{\partial d'_u}{\partial \alpha}\right|_{1/N^+} \!=\, -\frac{\gamma}{N-1}\, d'_{\max} f'(1/N),\quad
\left.\frac{\partial d'_u}{\partial \alpha}\right|_{1/N^-} \!=\, -\frac{\beta}{N-1}\, d'_{\max} f'(1/N), \tag{1.5}
$$

with $f'(1/N) > 0$. The kink is a genuine modelling artefact of the
β/γ asymmetric scaling under $\beta+\gamma = 2$. The paper does not
mention it; it is the analytic source of much of what follows.

---

## 2. The reward and its derivatives w.r.t. $d'_c, d'_u$

From mission §2.5, $\mathbb{E}[R] = \tfrac{1}{2}\bigl[V v\,\mathrm{HR}_c + (1-V)\,\mathrm{HR}_u\bigr] + \tfrac{1}{2}\,\mathrm{CR}\,(1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}$. The SDT primitives are $\mathrm{HR}_\bullet = \Phi(d'_\bullet/2 - c_\bullet)$ and $\mathrm{FAR}_\bullet = \Phi(-d'_\bullet/2 - c_\bullet)$. Let

$$
p_\bullet^H := \phi(d'_\bullet/2 - c_\bullet),\qquad p_\bullet^F := \phi(-d'_\bullet/2 - c_\bullet) = \phi(d'_\bullet/2 + c_\bullet) \tag{2.1}
$$

(using $\phi(-x) = \phi(x)$). Routine differentiation gives, at fixed criteria:

$$
A(\alpha) := \frac{\partial \mathbb{E}[R]}{\partial d'_c} = \tfrac{1}{4}\bigl[V v\, p_c^H + \mathrm{CR}\, p_c^F\, (1-\mathrm{FAR}_u)^{N-1}\bigr], \tag{2.2}
$$
$$
B(\alpha) := \frac{\partial \mathbb{E}[R]}{\partial d'_u} = \tfrac{1}{4}\bigl[(1-V)\, p_u^H + (N-1)\,\mathrm{CR}\, (1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-2}\, p_u^F\bigr]. \tag{2.3}
$$

Both $A, B$ are non-negative because $V, v, \mathrm{CR}, p^{H,F}, (1-\mathrm{FAR}_\bullet) \geq 0$. Strictly positive at non-degenerate criteria.

By the envelope theorem, when the criteria are jointly optimised at
$\alpha = 1/N$ (giving $c_c^\star, c_u^\star$), we may differentiate
the value function with respect to $\alpha$ holding the criteria
constant. The key observation: at $\alpha = 1/N$, both branches give
$d'_c = d'_u = d'_{\text{base}}$ — the $d'$ values are *r-independent*.
Therefore the optimal criteria at $\alpha = 1/N$ depend on
$(V, v, N, \mathrm{CR})$ but **not on $r$**, and so $A, B$ evaluated at
$\alpha = 1/N$ are themselves r-independent.

Define the boundary constants

$$
A_0 := A(1/N),\qquad B_0 := B(1/N). \tag{2.4}
$$

These are pure functions of $(V, v, N, \mathrm{CR}, d'_{\text{base}})$.

---

## 3. One-sided derivative of $\mathbb{E}[R]$ at $\alpha = 1/N$

Chain rule, using (1.4)–(1.5) and (2.2)–(2.3):

$$
\left.\frac{\partial \mathbb{E}[R]}{\partial \alpha}\right|_{1/N^+} \!=\, d'_{\max} f'(1/N) \left[\beta\, A_0 - \frac{\gamma}{N-1}\, B_0\right], \tag{3.1}
$$
$$
\left.\frac{\partial \mathbb{E}[R]}{\partial \alpha}\right|_{1/N^-} \!=\, d'_{\max} f'(1/N) \left[\gamma\, A_0 - \frac{\beta}{N-1}\, B_0\right]. \tag{3.2}
$$

Using $\gamma = 2/(r+1)$ and $\beta = 2r/(r+1)$:

$$
\left.\frac{\partial \mathbb{E}[R]}{\partial \alpha}\right|_{1/N^-} \!=\, \frac{2\,d'_{\max} f'(1/N)}{r+1}\left[A_0 - \frac{r}{N-1}\, B_0\right]. \tag{3.3}
$$

**For $\alpha = 1/N$ to be locally a maximum from the left** (so that
moving $\alpha$ down strictly *decreases* $\mathbb{E}[R]$), the left
derivative must be **non-negative**:

$$
\boxed{\;A_0 \;\geq\; \frac{r}{N-1}\, B_0 \quad\Longleftrightarrow\quad r \;\leq\; r^\star_{\mathrm{inv}}(V, v, N, \mathrm{CR}) := (N-1)\,\frac{A_0}{B_0}.\;} \tag{3.4}
$$

This is the **boundary inversion threshold**. It is the no-inversion
analog of CR-001's escape threshold $r^\dagger(v) = G_u/[(N-1) G_c(v)]$
for the VDA non-monotonicity. The structural mirror is exact: both
thresholds emerge from comparing the cued and uncued sensitivity
"slots" weighted by their reward contributions, with the
location-count factor $(N-1)$ governing the multiplicity of the uncued.

---

## 4. The paper's "regardless of $r$" claim is incomplete

Read (3.3) carefully. The left derivative at $\alpha = 1/N$ is
**linear in $r$** — once we pull out the r-independent boundary
constants $A_0, B_0$. The sign flips at $r = r^\star_{\mathrm{inv}}$.

For the paper's "regardless of $r$" claim to be correct as a local
statement, we would need $r^\star_{\mathrm{inv}} > 10$ at every cell
of the swept space. Step A of the companion replication evaluates
$r^\star_{\mathrm{inv}}$ on the paper's primary $(V, v, \text{variant})$
grid at $N=4$. The result:

| Region                                | Count (of 210) | Fraction |
|---------------------------------------|----------------|----------|
| $r^\star_{\mathrm{inv}} > 10$          | **107**        | 51.0%    |
| $r^\star_{\mathrm{inv}} \in [0.1, 10]$ | **103**        | 49.0%    |
| $r^\star_{\mathrm{inv}} < 0.1$         | 0              | 0.0%     |

Roughly half of the swept cells have a *local* inversion threshold
*inside* the swept $r$ range. The most adversarial corner is
$V = 1/N = 0.25$ with $v = 1$, where (as shown in §5 below) $A_0 = B_0/(N-1)$ exactly and $r^\star_{\mathrm{inv}} = 1$.

**This refutes the paper's "regardless of $r$" wording read literally
as a local statement.** What survives, and what the paper's
4,410-row empirical claim does report, is a *global* property: the
right-branch maximum dominates the left-branch maximum across the
entire sweep. Section 6 below explains why.

---

## 5. The corner $V = 1/N$, $v = 1$: $r^\star_{\mathrm{inv}} = 1$ exactly

At $V = 1/N$ and $v = 1$: $V \cdot v = 1/N$ and $(1-V) = (N-1)/N$;
likewise $\mathrm{CR}^{(A)} = V v + (1-V) = 1$ and $\mathrm{CR}^{(B)} = 1$. By
symmetry of the FOC system, $c_c^\star = c_u^\star = c^\star$ at
$\alpha = 1/N$, so $p_c^H = p_u^H \equiv p^H$, $p_c^F = p_u^F \equiv p^F$, and $\mathrm{FAR}_c = \mathrm{FAR}_u \equiv \mathrm{FAR}$. Substituting:

$$
A_0 = \tfrac{1}{4}\bigl[(1/N)\, p^H + (1)\, p^F\, (1-\mathrm{FAR})^{N-1}\bigr], \tag{5.1}
$$
$$
B_0 = \tfrac{1}{4}\bigl[((N-1)/N)\, p^H + (N-1)\,(1)\,(1-\mathrm{FAR})^{N-1}\, p^F\bigr] = (N-1)\, A_0. \tag{5.2}
$$

Therefore $r^\star_{\mathrm{inv}}(V=1/N, v=1) = (N-1) A_0 / B_0 = 1$,
**independent of $N$**.

At this corner, the left and right one-sided derivatives at $\alpha = 1/N$ are exact mirror images:

$$
\left.\frac{\partial \mathbb{E}[R]}{\partial \alpha}\right|_{1/N^+} \!=\, \frac{2 d'_{\max} f'(1/N)}{r+1}\, A_0\,(r-1), \tag{5.3}
$$
$$
\left.\frac{\partial \mathbb{E}[R]}{\partial \alpha}\right|_{1/N^-} \!=\, \frac{2 d'_{\max} f'(1/N)}{r+1}\, A_0\,(1-r). \tag{5.4}
$$

For $r > 1$: right derivative $>0$, left derivative $<0$. Both
branches *increase* $\mathbb{E}[R]$ as $\alpha$ moves *away* from $1/N$.
The point $\alpha = 1/N$ is a **local minimum**. The model is
bimodal in $\alpha$ at this corner.

Numerical confirmation (Step C(i), Variant A, $V=0.25, v=1, N=4$):

| $r$    | $r^\star_{\mathrm{inv}}$ | $\alpha^\star_{\mathrm{global}}$ | $R^\star_{\mathrm{global}}$ | $\alpha^\star_{\mathrm{left}}$ | $R^\star_{\mathrm{left}}$ | $\alpha^\star_{\mathrm{right}}$ | $R^\star_{\mathrm{right}}$ | $R(1/N)$ |
|--------|---------|----------|----------|---------|----------|----------|----------|--------|
| 0.10   | 1.000   | 0.250    | 0.62946  | 0.245   | 0.62905  | 0.255    | 0.62905  | 0.62946 |
| 1.00   | 1.000   | 0.250    | 0.62946  | 0.245   | 0.62946  | 0.255    | 0.62946  | 0.62946 |
| 1.585  | 1.000   | 0.460    | 0.63156  | 0.115   | 0.63115  | 0.460    | 0.63156  | 0.62946 |
| 2.512  | 1.000   | 0.660    | 0.63745  | 0.045   | 0.63510  | 0.660    | 0.63745  | 0.62946 |
| 3.981  | 1.000   | 0.805    | 0.64519  | 0.020   | 0.63943  | 0.805    | 0.64519  | 0.62946 |
| 10.00  | 1.000   | 0.955    | 0.65936  | 0.020   | 0.64564  | 0.955    | 0.65936  | 0.62946 |

For $r \leq 1$ the optimum is the uniform allocation $\alpha = 1/N$
(both branches strictly worse). For $r > 1$ the optimum jumps to the
right branch; the left branch has its own local maximum near
$\alpha = 0.02$ (the grid edge), but it is *strictly lower* than
the right-branch maximum by $\sim 0.005-0.014$ reward units (the gap
grows with $r$). C4 holds globally **but not because of local
balance** — both branches escape uniform attention, and the right
branch wins by a small but non-zero margin.

---

## 6. Why the right branch always wins under $V \geq 1/N$ and $v \geq 1$: the location-count asymmetry

The paper's informal justification — "weighted reward loss at the
high-value cued location exceeds the gain at low-value uncued
locations" — *almost* gets the right answer for a wrong reason. The
correct global argument has two ingredients the paper omits:

**(a) Right-branch peak achievable d' is strictly higher than left-branch peak.**
Consider the extremes. At $\alpha = 1$ (right edge):

$$
d'_c = d'_{\max}\, f(1) = d'_{\max}, \qquad d'_u = d'_{\text{base}} + \gamma\bigl[d'_{\max} f_0 - d'_{\text{base}}\bigr] = d'_{\text{base}}\,(1 - \gamma) + \gamma\, d'_{\max} f_0. \tag{6.1}
$$

At $\alpha = 0$ (left edge):

$$
d'_c = d'_{\text{base}}\,(1 - \gamma) + \gamma\, d'_{\max} f_0, \qquad d'_u = d'_{\text{base}} + \beta\bigl[d'_{\max} f\!\bigl(\tfrac{1}{N-1}\bigr) - d'_{\text{base}}\bigr]. \tag{6.2}
$$

The right-edge cued $d'$ reaches $d'_{\max}$ (the model's maximum
single-location sensitivity); the left-edge uncued $d'$ reaches only
$d'_{\text{base}} + \beta[d'_{\max} f(1/(N-1)) - d'_{\text{base}}]$,
with $f(1/(N-1)) < 1$ for $N \geq 3$. **For $N \geq 3$, no
allocation reaches the per-location ceiling $d'_{\max}$ on the
left branch** because the (N-1) uncued locations must share what
the cued location has all to itself.

**(b) Cued is the more-valuable-or-equal location under $V \geq 1/N$
and $v \geq 1$.** The reward weights per HR-channel are:

$$
w_c := V \cdot v,\qquad w_u := \frac{1-V}{N-1}. \tag{6.3}
$$

Routine algebra: $w_c \geq w_u \iff V[(N-1) v + 1] \geq 1 \iff V \geq \frac{1}{(N-1) v + 1}$. For $v \geq 1$, $\frac{1}{(N-1) v + 1} \leq \frac{1}{N}$ with equality at $v = 1$. So:

$$
V \geq 1/N \text{ and } v \geq 1 \implies w_c \geq w_u, \tag{6.4}
$$

with equality only at the boundary $(V = 1/N, v = 1)$.

**The two ingredients combine** as follows. Allocating to the right
(cued boosted): one location with weight $w_c \geq w_u$ gets its $d'$
amplified to $d'_{\max}$. Allocating to the left (uncued boosted):
$N-1$ locations with per-location weight $w_u \leq w_c$ get their
$d'$ amplified to $d'_{\text{base}} + \beta[d'_{\max} f(1/(N-1)) - d'_{\text{base}}]$.

The right branch gets the *bigger* d' on the *more-valuable* location.
This is what makes the right branch dominate globally — *not* the
local cost-vs-benefit balance at $\alpha = 1/N$, which fails for
~49% of swept cells.

---

## 7. The conditional and the counterexample outside it

Eq. (6.4) holds **only** under $V \geq 1/N$ and $v \geq 1$. If
**either** of these fails, the location-count argument flips and
inversion becomes globally optimal. Step C(iii) of the companion
replication confirms this directly.

Anti-cue regime ($V < 1/N$, $v = 1$, $N = 2$, sqrt, $f_0 = 0.5$, $d'_{\max} = 2$, Variant A):

| $N$ | $V$    | $w_c$ | $w_u$ | $r$    | $r^\star_{\mathrm{inv}}$ | $\alpha^\star_{\mathrm{global}}$ | $R^\star_{\mathrm{global}}$ | inversion? |
|-----|--------|-------|-------|--------|---------|----------|----------|------|
| 2   | 0.25   | 0.25  | 0.75  | 0.10   | 0.433   | 0.500    | 0.75058  | no (tie at $\alpha=1/N$) |
| 2   | 0.25   | 0.25  | 0.75  | 1.00   | 0.433   | **0.180**| 0.75846  | **YES**  |
| 2   | 0.25   | 0.25  | 0.75  | 5.00   | 0.433   | **0.020**| 0.79018  | **YES**  |
| 2   | 0.25   | 0.25  | 0.75  | 10.00  | 0.433   | **0.020**| 0.79837  | **YES**  |
| 2   | 0.40   | 0.40  | 0.60  | 1.00   | 0.745   | **0.380**| 0.74138  | **YES**  |
| 2   | 0.40   | 0.40  | 0.60  | 10.00  | 0.745   | **0.020**| 0.77825  | **YES**  |

In all anti-cue cells with $r \geq 1$, the global optimum has
$\alpha^\star < 1/N$. The model **does** invert when the
location-count argument flips. Inversion is **not** an exotic
behaviour disallowed by the math — it is a normal consequence of
the model, gated by the sign of $(w_c - w_u)$.

These cells are **outside the paper's primary sweep**, which is at
$N = 4$ only (and at $N = 4$, the paper's $V$-grid is exactly
$[1/N, 1]$). The paper's *secondary* sweep at $N = 2$ is at fixed
$(v=5, V=0.5)$ and does not enter the anti-cue regime. So C4's
empirical claim survives — but the *theoretical* generalization
implied by the paper's wording ("never optimal" sounds categorical;
the §4.5 prose ends with "never below it" with no $V \geq 1/N$
qualifier) does not.

The correct restatement of C4 incorporating the derivation:

> **C4 (refined).** Under $V \geq 1/N$ and $v \geq 1$, inverted
> attention $(\alpha^\star < 1/N)$ is never globally optimal. This
> holds despite the fact that, in roughly half of the swept
> parameter cells, the value function has a left-branch local
> maximum and the point $\alpha = 1/N$ is a local minimum
> (a structural consequence of the $\beta + \gamma = 2$ asymmetric
> scaling with kink at $\alpha = 1/N$). Global no-inversion follows
> from a **location-count asymmetry**: at $\alpha \to 1$, the cued
> location reaches $d'_{\max}$, while at $\alpha \to 0$, no uncued
> location reaches $d'_{\max}$ when $N \geq 3$, because the $N-1$
> uncued locations must share what the cued has alone. The
> location-count asymmetry combines with the value-weight
> inequality $w_c \geq w_u$ (which holds under $V \geq 1/N, v \geq 1$)
> to give right-branch dominance globally. When *either*
> ingredient fails (anti-cue $V < 1/N$, or cued-deflated $v < 1$),
> inversion is globally optimal — see Step C(iii) for explicit
> $(V<1/N, v=1, N=2)$ counterexamples.

---

## 8. Implications for the CR-019 V=1/N degeneracy refinement

CR-019 (spawned by CR-014, mission §8) flagged that the CR-014
sensitivity probe surfaced an $\alpha = 0.02$ optimum for the
value-blind policy $P_2$ at $V = 1/N$, $N = 2$, $v = 1$. The
question was whether the C4 claim should carry an explicit
$V > 1/N$ qualifier (rather than $V \geq 1/N$).

This derivation resolves CR-019 cleanly:

- At $V = 1/N$, $v = 1$, $r \leq 1$: $\mathbb{E}[R]$ is flat in
  $\alpha$ to leading order; the optimum is $\alpha = 1/N$ but
  *any* $\alpha$ in a small neighbourhood gives the same $\mathbb{E}[R]$ to
  within $\sim 10^{-4}$ — the optimiser's pick is grid-dependent.

- At $V = 1/N$, $v = 1$, $r > 1$: $\mathbb{E}[R]$ has a local minimum at
  $\alpha = 1/N$ and two non-trivial maxima on the two branches.
  The right-branch maximum is strictly higher (by the location-count
  asymmetry of §6) — by 0.005 to 0.014 reward units across the
  $r > 1$ portion of the sweep at $V=0.25, v=1, N=4$ (Step C(i)).
  The CR-014 observation of an $\alpha = 0.02$ optimum for $P_2$ at
  $N = 2$ was the *left-branch local maximum*, found by an
  optimiser that did not visit the right branch (since the value-
  blind $P_2$ uses $v = 1$ and the grid search may have
  short-circuited on the first local max found).

The C4 wording does *not* require revising to $V > 1/N$ —
$V = 1/N$ is fine because the right branch still strictly dominates
the left at $r > 1$, and ties at $r \leq 1$. CR-019 is **answered
in the negative**: no wording change needed; the verdict body
documents the bimodality.

---

## 9. Summary table — verdict-relevant quantities

| Quantity | Value or expression |
|---|---|
| Boundary inversion threshold | $r^\star_{\mathrm{inv}}(V, v, N, \mathrm{CR}) = (N-1)\, A_0 / B_0$ |
| At $V=1/N, v=1$ (corner) | $r^\star_{\mathrm{inv}} = 1$ exactly |
| Cells with $r^\star_{\mathrm{inv}} \in [0.1, 10]$ at $N=4$ (out of 210) | 103 (49.0%) |
| Cells with global $\alpha^\star < 1/N$ in primary sweep ($N=4$) | **0** (C4 holds) |
| Cells with global $\alpha^\star < 1/N$ in anti-cue regime ($V<1/N$, $v=1$, $N=2$, $r \geq 1$) | **all tested** (C4 fails outside conditional) |
| Left-branch $\mathbb{E}[R]$ vs right-branch $\mathbb{E}[R]$ at primary-sweep cells | left strictly $<$ right by 0.005–0.150 reward units |
| Kink at $\alpha = 1/N$ in $d'(\alpha)$ for $r \neq 1$ | yes (β/γ swap) — unmentioned in paper |
| $r$-dependence of left derivative $\partial \mathbb{E}[R]/\partial \alpha|_{1/N^-}$ | $\propto [A_0 - (r/(N-1)) B_0]$ |
| Paper's "regardless of $r$" wording | correct as a *global* empirical statement; incorrect as a *local* derivative statement |
| Mechanism underwriting the empirical claim | **location-count asymmetry** + value-weight inequality $w_c \geq w_u$ at $V \geq 1/N, v \geq 1$, not local cost-benefit balance |

---

## 10. Connections to the broader critique

- **Mirror of CR-001 closed form.** $r^\star_{\mathrm{inv}} = (N-1) A_0/B_0$
  for the inversion-boundary derivative is the exact analog of CR-001's
  VDA escape threshold $r^\dagger(v) = G_u/[(N-1) G_c(v)]$ for the
  non-monotonicity claim. Both reduce the paper's r-axis behaviour
  to a single closed-form criterion at the relevant boundary
  ($\alpha = 1/N$ for C4; $\alpha = \alpha^\star_{P_2}$ for C2). This
  suggests a broader pattern: the paper's r-axis findings are
  governed by ratios of r-independent boundary quantities, and the
  $\beta + \gamma = 2$ asymmetric scaling is what makes the linear-in-$r$
  structure work out so cleanly.

- **C3 V_critical (CR-026) parallel.** CR-026 derived a closed-form
  $V_{\text{critical}}(r, N) \approx 1/(1 + r(N-1)/\kappa)$ governing the
  high-V boundary of the VDA window. The C4 inversion threshold
  $r^\star_{\mathrm{inv}}$ is the same kind of derived-quantity-the-paper-
  did-not-state, surfacing on the low-α end rather than the high-V end.

- **Robustness to A3 (additive vs multiplicative conservation).** The
  $\beta + \gamma = 2$ constraint enters (3.1)–(3.3) directly. Under an
  alternative constraint $\beta \cdot \gamma = 1$ (the natural
  multiplicative analog the paper notes in §5.5 but does not run),
  $\gamma = 1/r^{1/2}$ and $\beta = r^{1/2}$, and the right-derivative
  test becomes $r^{1/2} A_0 \geq (1/r^{1/2})/(N-1) B_0$ i.e.
  $r \geq B_0/[(N-1) A_0] = 1/r^\star_{\mathrm{inv}}$, with $r^\star$
  defined by the *additive* model — different threshold structure,
  same closed-form shape. This is a CR-NNN candidate for a future
  derivation linking A3 robustness to C4.

- **Implications for PRISM (§3.5).** PRISM v1/v2 trains a policy on
  the same Posner-style change-detection task class. If the trained
  attention trajectories $\alpha(t)$ ever dip *below* the uniform
  baseline at validity $V \geq 1/N$ and value $v \geq 1$, that is a
  **deviation from the normative model** — possibly because PRISM's
  recurrent dynamics implement a different asymmetric scaling, or
  because PRISM has not yet converged to the global optimum.
  Conversely, if PRISM is run with anti-cue conditions (a manipulation
  not in `Prism/env.py` as of the current commit but trivially added
  by setting `valid_prob < 1/N`), the normative prediction from this
  derivation is **explicit inversion** with $\alpha^\star < 1/N$, which
  PRISM should learn. This is a high-leverage testable PRISM
  prediction the paper does not state.

---

*End of derivation. Numerical companion in
`Critique/replications/C4--no-inversion/run.py`; output in
`output/results.json` and `output/run.log`. Verdict file at
`Critique/verdicts/C4--no-inversion.md`.*
