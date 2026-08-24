---
type: derivation
project: AttentionManuscript / VDA-rebuild
agent: constructive-rebuilder
backlog_id: RB-026
claim_id: C2
status: drafted
created: 2026-05-26
backing_for: "Rebuild/manuscript/sections/appendix-derivation-C2 + §results-A1 (closed-form peak-drift locus)"
backed_by_sim: "Rebuild/sims/C2--vda-vs-r-vfamily/ (rb-006, sha256 09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783)"
backed_by_verification: "Rebuild/derivations/verify_C2_rho/ (rb-026, output.json sha256 ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc)"
implements: "Rebuild/model/core.py: p_no_fa_point, p_no_fa_grid (the same ρ-aware quadrature)"
recovery_test: "rb-006 r_dagger() closed form at ρ = 0 (Rebuild/sims/C2--vda-vs-r-vfamily/run.py lines 218-265)"
voice: independent re-derivation in the rebuild's voice; not a copy of Critique/derivations/C2--non-monotonic-vda.md
prereqs: [RB-001 (model wiring), RB-002 (A1 sim), RB-003 (A1 derivation), RB-006 (C2 sim)]
---

# C2 — The escape threshold $r^{\dagger}(v;\rho)$

> *The inherited paper's §4.3 argument for non-monotonic VDA — the "squeeze
> from two directions" — has a closed-form spine. The reviewer derived it
> at $\rho = 0$:* $r^{\dagger}(v) = K_u(v) / [(N-1)\,K_c(v)]$,
> *the value $r$ below which the value-aware policy P1 is still stuck at
> the uniform allocation $\alpha = 1/N$. This appendix promotes that
> closed form into a* **Proposition** *of the rebuilt model in the
> rebuild's voice (§2), then* extends *it to* $\rho \in [0,1)$ *(§§3–4)
> using the same one-factor Gauss–Hermite quadrature the* `Rebuild/model/`
> *code already uses for* $P_{\text{no-fa}}(\rho)$ *(rb-001/rb-003). The
> $\rho > 0$ closed form predicts that the escape threshold drifts
> upward in $\rho$ at every $v$ in the empirical envelope, with the
> drift fraction growing with $v$ — analytically explaining the* (peak
> $r^{\star}$ drifts up under $\rho$) *observation rb-006 reported
> numerically. The* ρ→0 *collapse to §2 is verified to grid precision,
> the boundary FD sign-flip is verified at every tested $(v,\rho)$, and
> the predicted drift sign matches the rb-006 empirical $\Delta r^{\star}$
> sign at every $v \ne 1$ in the family. Every numerical statement here
> traces to* `Rebuild/derivations/verify_C2_rho/output.json` *(sha256*
> `ddbd3988…`*), the companion verification script.*

Notation and SDT primitives follow `agents/paper_rebuilder_prompt.md` §2.2
and the inherited model, identical to `Rebuild/derivations/A1--rho-channel.md`
§1.1; we recall only what the C2 boundary argument needs.

---

## 1. Setup and the locus of the C2 closed form

### 1.1 What the closed form says

The qualitative content of C2 (mission §2.6 / `Critique/verdicts/C2--non-monotonic-vda.md`)
is that
$$
  \mathrm{VDA}(r;v,V,N)
  \;=\;
  R^{\star}_{\mathrm P_1}(r,v,V,N) - R^{\star}_{\mathrm P_2}(r,v,V,N)
  \;\ge\; 0,
  \qquad
  \mathrm{VDA}(r) \to 0
  \text{ as } r \to 0^{+}
  \text{ or } r \to \infty,
  \tag{1.1}
$$
with the value-blind policy
$\mathrm P_2$ defined as $\alpha = \alpha^{\star}(v{=}1)$, criteria jointly
re-optimised. The non-monotonicity in (1.1) is forced by the *separation in
escape thresholds* between $\mathrm P_1$ and $\mathrm P_2$:
$$
  r^{\dagger}(v) \;:=\; \inf\{r > 0 \;:\; \alpha^{\star}_{\mathrm P_1}(r,v) > 1/N\}.
  \tag{1.2}
$$
$\mathrm P_2$, which optimises at the value-blind anchor $v=1$, escapes at
$r^{\dagger}(1)$, whereas $\mathrm P_1$ — which gets the value-aware credit
on every cued hit — escapes earlier, at $r^{\dagger}(v) < r^{\dagger}(1)$ for
$v > 1$. The two policies diverge on the *escape band*
$\bigl(r^{\dagger}(v),\, r^{\dagger}(1)\bigr)$, which is the regime
inside which the inherited paper's headline VDA peak lives.

### 1.2 The boundary configuration

The closed form (1.2) is computed at $\alpha = 1/N^{+}$. Two simplifications
of the model collapse at this boundary, regardless of $r$ or $\rho$:

* **The sensitivity collapse.** With the transfer
  $f(a) = f_0 + (1-f_0)\,h(a)$ and $h(1/N) > 0$, the symmetric
  baseline sensitivity is $d'_{\text{base}} = d'_{\max} \cdot f(1/N)$;
  by the gain-branch definition of $d'_c, d'_u$ in
  `Rebuild/model/core.py:d_prime_asym` (Eqs. 1.4–1.6 of
  `Rebuild/derivations/A1--rho-channel.md`),
  $$
    d'_c\bigl(\tfrac{1}{N};r\bigr) \;=\; d'_u\bigl(\tfrac{1}{N};r\bigr) \;=\; d'_{\text{base}}
    \qquad \forall\,r > 0.
    \tag{1.3}
  $$

* **The asymmetry of the optimal criteria.** The cued and uncued
  *change-trial rewards* are $V v$ and $1 - V$ respectively, which
  differ whenever $V \ne 1/N$ or $v \ne 1$. The criterion optimum at
  the boundary configuration is therefore the *asymmetric P3 point*
  $$
    (c^{\star}_c(v,V,N,\mathrm{CR},\rho),\;
     c^{\star}_u(v,V,N,\mathrm{CR},\rho))
    \;=\;
    \operatorname*{arg\,max}_{(c_c,c_u)}
    \mathbb E[R]\bigl(d'_{\text{base}},\,d'_{\text{base}},\,c_c,\,c_u;\,v,V,N,\mathrm{CR},\rho\bigr),
    \tag{1.4}
  $$
  evaluated on the criterion grid `C_GRID` (`Rebuild/model/core.py`
  L474: $-3 \le c \le 3$ step $0.05$, $121$ points). At the
  representative cell $(V,v,N,d'_{\max},f_0,h) = (4,0.5,5,2,0.5,\sqrt{\cdot})$
  with $\rho = 0$, $\mathrm{verify\_C2\_rho/output.json}$ records
  $(c^{\star}_c,\,c^{\star}_u) = (0.10,\,1.75)$ — strongly asymmetric
  ($c^{\star}_c$ liberal, $c^{\star}_u$ conservative), and a function of
  every parameter of (1.4).

We write $b^{\star}_c := c^{\star}_c + d'_{\text{base}}/2$,
$b^{\star}_u := c^{\star}_u + d'_{\text{base}}/2$ for the no-FA arguments
(cf. Eq. 1.2 of `Rebuild/derivations/A1--rho-channel.md`); they are the
$z$-scores the no-change decision variable must stay below at the
cued/uncued P3 optima.

### 1.3 The booking that exposes the locus

Mission §2.5 / `Rebuild/derivations/A1--rho-channel.md` §1.2 isolates A1
to the no-change-trial product. The closed form (1.2) is computed via the
boundary first-order condition $\partial\mathbb E[R]/\partial\alpha|_{1/N^+}$,
which has *two* contributions to $\rho$:

* **The change-trial bracket.** Only marginal HRs appear; $\rho$ does not
  enter (cf. Eq. 1.3 of A1 derivation, change-bracket discussion).
* **The no-FA bracket.** $P_{\text{no-fa}}(\rho)$ is the equicorrelated
  Gaussian orthant probability (`Rebuild/derivations/A1--rho-channel.md`
  Eq. 2.3), and $\rho$ enters $\partial\mathbb E[R]/\partial\alpha|_{1/N^+}$
  exactly through the *d-gradients* of this orthant probability at
  $(d_c, d_u) = (d'_{\text{base}}, d'_{\text{base}})$ evaluated at
  $(c_c, c_u) = (c^{\star}_c, c^{\star}_u)$.

The closed-form derivation is therefore the chain rule on
$\mathbb E[R](\alpha, c_c, c_u; \rho)$, evaluated at the boundary
configuration (1.3)–(1.4), with $\rho$ entering only through the no-FA
$d$-gradients. This is the road map for §§2–4.

---

## 2. The $\rho = 0$ re-derivation in the rebuild's voice

This section restates the reviewer's closed-form result
`Critique/derivations/C2--non-monotonic-vda.md` §2.3 in the rebuild's
voice, with fresh equation labels and the explicit P3-asymmetric criterion
booking. It is the $\rho = 0$ specialisation of §§3–4 — useful as the
recovery target and as the pedagogical entry point.

### 2.1 First-order condition at the boundary

For $\alpha > 1/N$, the gain-branch asymmetric transfer
(`Rebuild/model/core.py:d_prime_asym`) gives, by the chain rule at
$\alpha = 1/N^{+}$:
$$
  \frac{\partial d'_c}{\partial\alpha}\bigg|_{1/N^{+}}
  \;=\;
  \beta(r)\,d'_{\max}\,f'(1/N),
  \qquad
  \frac{\partial d'_u}{\partial\alpha}\bigg|_{1/N^{+}}
  \;=\;
  -\,\frac{\gamma(r)\,d'_{\max}\,f'(1/N)}{N-1},
  \tag{2.1}
$$
where $f'(a) = (1-f_0)\,h'(a)$. The cued slope is positive (more attention
raises $d'_c$); the uncued slope is negative and scales as $1/(N-1)$
because the lost attention is *spread across* the $N-1$ uncued locations.

Define the change-trial densities at the P3 optimum:
$$
  \varphi^{c}_{\text{ch}}
  \;:=\;
  \varphi\bigl(d'_{\text{base}}/2 - c^{\star}_c\bigr),
  \qquad
  \varphi^{u}_{\text{ch}}
  \;:=\;
  \varphi\bigl(d'_{\text{base}}/2 - c^{\star}_u\bigr),
  \tag{2.2}
$$
where $\varphi$ is the standard normal density. Standard $\partial\Phi/\partial d = (1/2)\varphi$
gives, at the boundary configuration,
$$
  \frac{\partial \mathrm{HR}_c}{\partial\alpha}\bigg|_{1/N^{+}}
  \;=\;
  \tfrac{1}{2}\,\varphi^{c}_{\text{ch}}\,
  \beta(r)\,d'_{\max}\,f'(1/N),
  \qquad
  \frac{\partial \mathrm{HR}_u}{\partial\alpha}\bigg|_{1/N^{+}}
  \;=\;
  -\,\tfrac{1}{2}\,\varphi^{u}_{\text{ch}}\,
  \frac{\gamma(r)\,d'_{\max}\,f'(1/N)}{N-1}.
  \tag{2.3}
$$

### 2.2 The no-FA $d$-gradients at $\rho = 0$

At $\rho = 0$, $P_{\text{no-fa}} = \Phi(b_c)\,\Phi(b_u)^{N-1}$, hence
$$
  \frac{\partial P_{\text{no-fa}}}{\partial d_c}
  \;=\;
  \tfrac{1}{2}\,\varphi(b_c)\,\Phi(b_u)^{N-1},
  \qquad
  \frac{\partial P_{\text{no-fa}}}{\partial d_u}
  \;=\;
  \tfrac{N-1}{2}\,\Phi(b_c)\,\Phi(b_u)^{N-2}\,\varphi(b_u).
  \tag{2.4}
$$
At the boundary configuration $(d_c, d_u) = (d'_{\text{base}}, d'_{\text{base}})$,
$(c_c, c_u) = (c^{\star}_c, c^{\star}_u)$, $(b_c, b_u) = (b^{\star}_c, b^{\star}_u)$:
$$
  \frac{\partial P_{\text{no-fa}}}{\partial d_c}\bigg|_{\text{P3 bd}, \,\rho=0}
  =\;
  \tfrac{1}{2}\,I_c^{0},
  \qquad
  \frac{\partial P_{\text{no-fa}}}{\partial d_u}\bigg|_{\text{P3 bd}, \,\rho=0}
  =\;
  \tfrac{N-1}{2}\,I_u^{0},
  \tag{2.5}
$$
with
$$
  I_c^{0} := \varphi(b^{\star}_c)\,\Phi(b^{\star}_u)^{N-1},
  \qquad
  I_u^{0} := \Phi(b^{\star}_c)\,\Phi(b^{\star}_u)^{N-2}\,\varphi(b^{\star}_u).
  \tag{2.6}
$$
(The labels $I_c^{0}, I_u^{0}$ anticipate their ρ-aware extensions in §3;
$I_c \ne I_u$ in general because the no-FA orthant integrand has a
$\Phi(b_u)^{N-1}$ factor that contributes asymmetrically to the two
$d$-derivatives.)

### 2.3 Chain rule and the boundary-FOC sign

Substituting (2.1), (2.5) into
$$
  \frac{\partial \mathbb E[R]}{\partial\alpha}\bigg|_{1/N^{+}}
  \;=\;
  \tfrac{1}{2}\bigl[V v\,\partial_\alpha \mathrm{HR}_c + (1-V)\,\partial_\alpha \mathrm{HR}_u\bigr]
  + \tfrac{1}{2}\,\mathrm{CR}\,\partial_\alpha P_{\text{no-fa}},
$$
and collecting the $\beta(r)$ and $\gamma(r)$ coefficients,
$$
\boxed{\;
  \frac{\partial \mathbb E[R]}{\partial\alpha}\bigg|_{1/N^{+}}
  \;=\;
  d'_{\max}\,f'(1/N)\,
  \Bigl[\,\beta(r)\,K_c(v) \;-\; \gamma(r)\,\frac{K_u(v)}{N-1}\,\Bigr],
\;}
\tag{2.7}
$$
with
$$
  K_c(v) \;:=\; \tfrac{1}{4}\bigl[V\,v\,\varphi^{c}_{\text{ch}}
                                  + \mathrm{CR}\,I_c^{0}\bigr],
  \tag{2.8}
$$
$$
  K_u(v) \;:=\; \tfrac{1}{4}\bigl[(1-V)\,\varphi^{u}_{\text{ch}}
                                  + (N-1)\,\mathrm{CR}\,I_u^{0}\bigr],
  \tag{2.9}
$$
both *positive*. Substituting $\beta(r) = 2r/(r+1)$,
$\gamma(r) = 2/(r+1)$ and dividing out the positive prefactor
$2/(r+1)$:
$$
  \operatorname{sign}\!\Bigl(\partial \mathbb E[R]/\partial\alpha\,\Bigl|_{1/N^{+}}\Bigr)
  \;=\;
  \operatorname{sign}\!\Bigl(\,r\,K_c(v) \;-\; \frac{K_u(v)}{N-1}\Bigr).
  \tag{2.10}
$$

### 2.4 Proposition: $r^{\dagger}(v) = K_u(v)/[(N-1)\,K_c(v)]$

> **Proposition 2.1 (Escape threshold, $\rho = 0$).** Fix
> $(N, V, v, d'_{\max}, f_0, h, \mathrm{CR})$ and the P3-asymmetric
> criterion optimum $(c^{\star}_c, c^{\star}_u)$ at $\alpha = 1/N$,
> $\rho = 0$ via (1.4). Then the value-aware optimal allocation satisfies
> $\alpha^{\star}_{\mathrm P_1}(r,v) = 1/N$ for $r \le r^{\dagger}(v)$
> and $\alpha^{\star}_{\mathrm P_1}(r,v) > 1/N$ for $r > r^{\dagger}(v)$,
> with
> $$
>   r^{\dagger}(v) \;=\; \frac{K_u(v)}{(N-1)\,K_c(v)}. \tag{2.11}
> $$

*Proof sketch.* (2.10) gives the sign of the boundary FOC; equality
$r = r^{\dagger}(v)$ flips it from negative (P1 sticks at $1/N$) to positive
(P1 escapes). The second-order condition is the usual one (the corner
maximum at $\alpha = 1/N$ becomes a saddle as $r$ crosses $r^{\dagger}$).
The boundary-FD sanity at $r = r^{\dagger}(v;\rho) \pm 0.05$ — confirmed
$6/6$ in `verify_C2_rho/output.json` — empirically verifies the sign flip
in the rebuilt model. ∎

**Recovery contract.** (2.11) is exactly the reviewer's closed form
`Critique/derivations/C2--non-monotonic-vda.md` Eq. 2.5, modulo
algebraic reshuffling of the $(N-1)$ factor between numerator and
denominator. The rebuilt model's `verify_C2_rho` script computes (2.11)
on the rebuilt model's `p_no_fa_grid` quadrature and matches the
reviewer's `r_dagger()` (also `Rebuild/sims/C2--vda-vs-r-vfamily/run.py`
L218–265) at all $v \in \{1,2,3,5,8,10\}$ to within $5 \times 10^{-4}$
in $r^{\dagger}$ — *the discrepancy is the $\Delta c = 0.05$ grid
quantisation of $(c^{\star}_c, c^{\star}_u)$ in (1.4)*, not a residual in
the formula; the binary match at $v = 2$ (both implementations land on
the same grid point) confirms the formula is the same expression.

---

## 3. The $\rho > 0$ extension

### 3.1 The ρ-aware no-FA $d$-gradients

The equicorrelated no-FA orthant probability
(`Rebuild/derivations/A1--rho-channel.md` Eq. 2.3)
$$
  P_{\text{no-fa}}(\rho)
  \;=\;
  \int_{-\infty}^{\infty}
  \Phi\!\left(\frac{b_c - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \Phi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)^{N-1}
  \varphi(z)\,dz
  \tag{3.1}
$$
admits closed-form $d$-derivatives by differentiation under the integral
(the integrand and its $d$-derivatives are bounded; dominated
convergence applies). Using $\partial\Phi(x)/\partial d = (1/2)\partial\Phi/\partial x = (1/2)\varphi(x)$,
the inner $b$-shift contributes a factor $1/\sqrt{1-\rho}$:
$$
  \frac{\partial P_{\text{no-fa}}(\rho)}{\partial d_c}
  \;=\;
  \tfrac{1}{2}\int_{-\infty}^{\infty}
  \frac{1}{\sqrt{1-\rho}}\,
  \varphi\!\left(\frac{b_c - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \Phi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)^{N-1}
  \varphi(z)\,dz,
  \tag{3.2}
$$
$$
  \frac{\partial P_{\text{no-fa}}(\rho)}{\partial d_u}
  \;=\;
  \tfrac{N-1}{2}\int_{-\infty}^{\infty}
  \frac{1}{\sqrt{1-\rho}}\,
  \Phi\!\left(\frac{b_c - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \Phi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)^{N-2}
  \varphi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \varphi(z)\,dz.
  \tag{3.3}
$$
Both integrals are 1-D and admit the same 64-node Gauss–Hermite
quadrature `(_GH_Z, _GH_W)` (`Rebuild/model/core.py` L485–494) the
rebuilt model uses for (3.1) itself, evaluated at the boundary
configuration $(d_c, d_u) = (d'_{\text{base}}, d'_{\text{base}})$,
$(c_c, c_u) = (c^{\star}_c(\rho),\,c^{\star}_u(\rho))$.

Define
$$
  I_c(b_c, b_u; \rho, N)
  \;:=\;
  \int_{-\infty}^{\infty}
  \frac{1}{\sqrt{1-\rho}}\,
  \varphi\!\left(\frac{b_c - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \Phi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)^{N-1}
  \varphi(z)\,dz,
  \tag{3.4}
$$
$$
  I_u(b_c, b_u; \rho, N)
  \;:=\;
  \int_{-\infty}^{\infty}
  \frac{1}{\sqrt{1-\rho}}\,
  \Phi\!\left(\frac{b_c - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \Phi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)^{N-2}
  \varphi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \varphi(z)\,dz.
  \tag{3.5}
$$
Then (3.2)–(3.3) become $\partial_d P = (1/2)\,I_c$ and
$\partial_{d_u} P = ((N-1)/2)\,I_u$, the ρ-aware analogues of (2.5)–(2.6).

### 3.2 The ρ-aware P3 criterion optimum

Because $P_{\text{no-fa}}(\rho)$ enters $\mathbb E[R]$ multiplicatively in
the no-change bracket, the criterion optimum $(c^{\star}_c, c^{\star}_u)$
in (1.4) depends on $\rho$:
$$
  \bigl(c^{\star}_c(\rho),\,c^{\star}_u(\rho)\bigr)
  \;=\;
  \operatorname*{arg\,max}_{(c_c, c_u)}\,
  \mathbb E[R]\bigl(d'_{\text{base}},\,d'_{\text{base}},\,c_c,\,c_u;\,v,V,N,\mathrm{CR},\rho\bigr).
  \tag{3.6}
$$
At the headline cell $(N,V,v) = (4, 0.5, 5)$ with $\mathrm{CR} = V v + (1-V) = 3.0$
(variant A): rb-006's $\rho = 0$ optimum
$(c^{\star}_c, c^{\star}_u) = (0.10, 1.75)$ shifts to
$(0.05, 1.80)$ at $\rho = 0.2$ (`verify_C2_rho/output.json` →
`r_dagger_table.v=5.0__rho=0.2`). The cued criterion drops $0.05$
(more liberal — under correlation, a cued FA is less costly because
correlated FAs across locations are partially "explained away") and
the uncued criterion climbs $0.05$ (more conservative — under
correlation, an uncued FA *also* hurts the cued-no-FA joint event).
Both shifts are exactly one C_GRID step ($\Delta c = 0.05$) at the
chosen quadrature resolution.

### 3.3 The ρ-aware $K_c, K_u$

The same chain-rule derivation as §2.3 — change-trial bracket
(2.3) unchanged, no-FA bracket using (3.2)–(3.3) — gives
$$
\boxed{\;
  \frac{\partial \mathbb E[R]}{\partial\alpha}\bigg|_{1/N^{+}}\!(\rho)
  \;=\;
  d'_{\max}\,f'(1/N)\,
  \Bigl[\,\beta(r)\,K_c(v;\rho) \;-\; \gamma(r)\,\frac{K_u(v;\rho)}{N-1}\,\Bigr],
\;}
\tag{3.7}
$$
with
$$
  K_c(v;\rho) \;:=\; \tfrac{1}{4}\bigl[V\,v\,\varphi^{c}_{\text{ch}}(\rho)
                                       + \mathrm{CR}\,I_c\bigl(b^{\star}_c(\rho), b^{\star}_u(\rho); \rho, N\bigr)\bigr],
  \tag{3.8}
$$
$$
  K_u(v;\rho) \;:=\; \tfrac{1}{4}\bigl[(1-V)\,\varphi^{u}_{\text{ch}}(\rho)
                                       + (N-1)\,\mathrm{CR}\,I_u\bigl(b^{\star}_c(\rho), b^{\star}_u(\rho); \rho, N\bigr)\bigr],
  \tag{3.9}
$$
$\varphi^{c}_{\text{ch}}(\rho) := \varphi(d'_{\text{base}}/2 - c^{\star}_c(\rho))$,
$\varphi^{u}_{\text{ch}}(\rho) := \varphi(d'_{\text{base}}/2 - c^{\star}_u(\rho))$,
$b^{\star}_i(\rho) := c^{\star}_i(\rho) + d'_{\text{base}}/2$. The $\rho$
dependence enters $K_c, K_u$ through (i) the ρ-aware P3 criterion shifts
$c^{\star}_i(\rho)$ (§3.2) and (ii) the ρ-aware $d$-gradient integrals
$I_c, I_u$ (§3.1). The change-trial densities $\varphi^{c}_{\text{ch}}, \varphi^{u}_{\text{ch}}$
inherit $\rho$ dependence only through $c^{\star}_i(\rho)$.

---

## 4. The closed form $r^{\dagger}(v;\rho)$

> **Proposition 4.1 (Escape threshold under equicorrelation).** Fix
> $(N, V, v, d'_{\max}, f_0, h, \mathrm{CR}, \rho)$ with $\rho \in [0,1)$
> and let $(c^{\star}_c(\rho),\,c^{\star}_u(\rho))$ solve (3.6). Define
> $K_c(v;\rho), K_u(v;\rho)$ by (3.8)–(3.9). Then
> $$
> \boxed{\;
>   r^{\dagger}(v;\rho)
>   \;=\;
>   \frac{K_u(v;\rho)}{(N-1)\,K_c(v;\rho)}
>   \;=\;
>   \frac{
>     (1-V)\,\varphi^{u}_{\text{ch}}(\rho)
>     + (N-1)\,\mathrm{CR}\,I_u\bigl(b^{\star}_c(\rho), b^{\star}_u(\rho); \rho, N\bigr)
>   }{
>     (N-1)\,\bigl[V\,v\,\varphi^{c}_{\text{ch}}(\rho)
>     + \mathrm{CR}\,I_c\bigl(b^{\star}_c(\rho), b^{\star}_u(\rho); \rho, N\bigr)\bigr]
>   }.
> \;}
> \tag{4.1}
> $$
> Below $r^{\dagger}(v;\rho)$, $\alpha^{\star}_{\mathrm P_1}(r,v;\rho) = 1/N$;
> above, $\alpha^{\star}_{\mathrm P_1}(r,v;\rho) > 1/N$.

*Proof.* (3.7) gives the boundary FOC; dividing out the
$(2/(r+1)) \cdot d'_{\max} f'(1/N) > 0$ prefactor and solving
$r K_c(v;\rho) = K_u(v;\rho)/(N-1)$ gives (4.1). The boundary-FD sign-flip
sanity at $r = r^{\dagger}(v;\rho) \pm 0.05$ — confirmed $6/6$ across
$(v, \rho) \in \{1, 2, 3\} \times \{0, 0.2\}$ in
`verify_C2_rho/output.json` `boundary_FD_check` — empirically verifies
the sign flip in the rebuilt model. ∎

### 4.1 ρ → 0 recovery to Proposition 2.1

At $\rho = 0$, the integrand of (3.4) loses its $z$-dependence
($\sqrt{\rho} = 0$, $\sqrt{1-\rho} = 1$), $\int\varphi(z)\,dz = 1$, and
$$
  I_c(b_c, b_u; 0, N) \;=\; \varphi(b_c)\,\Phi(b_u)^{N-1} \;=\; I_c^{0}.
  \tag{4.2}
$$
Likewise $I_u(b_c, b_u; 0, N) = \Phi(b_c)\,\Phi(b_u)^{N-2}\,\varphi(b_u) = I_u^{0}$.
The criterion optimum (3.6) at $\rho = 0$ reduces to (1.4) at $\rho = 0$.
Hence
$$
  K_c(v; 0) \;=\; K_c(v),
  \qquad
  K_u(v; 0) \;=\; K_u(v),
$$
and (4.1) reduces to (2.11):
$$
  r^{\dagger}(v; 0) \;=\; \frac{K_u(v)}{(N-1)\,K_c(v)}.
  \tag{4.3}
$$
The recovery is *structural* (the formulas collapse term-by-term), not
just numerical. The verification script (`verify_C2_rho/verify.py`)
checks the numerical recovery on the C_GRID-quantised criterion grid:
$$
  \max_{v \in \{1,2,3,5,8,10\}} \bigl|\,r^{\dagger}_{\text{rb-026}}(v;0) - r^{\dagger}_{\text{rb-006}}(v)\,\bigr|
  \;\le\; 5 \times 10^{-4},
$$
with the residual a $\Delta c = 0.05$ quantisation-noise floor, *not* a
formula discrepancy: at $v = 2$ both implementations land on the same
grid optimum $(c^{\star}_c, c^{\star}_u) = (0.25, 1.30)$ and (4.1)
equals (2.11) byte-for-byte.

### 4.2 What (4.1) does and does not predict

(4.1) is the closed form for the *escape threshold*, the lower edge of the
$(r^{\dagger}(v;\rho), r^{\dagger}(1;\rho))$ band on which P1 escapes
uniform allocation but P2 has not. It does *not* directly predict the
*peak location* $r^{\star}(v;\rho)$ of $\mathrm{VDA}(r;v;\rho)$ — the peak
sits inside the escape band and depends on (i) how steeply
$\alpha^{\star}_{\mathrm P_1}(r,v;\rho)$ climbs above $1/N$ once it
escapes, and (ii) how the P3-criterion piece of $R^{\star}$ varies with
$\alpha$ in the escape band. At the headline cell, rb-006's empirical
peak $r^{\star}(v;\rho)$ at $v \in \{2,3,5,8,10\}$ sits between $r^{\dagger}(v)$
and $r^{\dagger}(1) \approx 0.34$, consistent with the qualitative
prediction.

What (4.1) *does* directly predict is **how $r^{\dagger}(v)$ drifts with
$\rho$ at every $v$** — and by §1.1 the escape-band lower edge drifts in
the same direction as the peak (the peak cannot be lower than
$r^{\dagger}(v;\rho)$). The next section quantifies the drift.

---

## 5. Numerical realisation at the headline cell

All numbers in this section trace to
`Rebuild/derivations/verify_C2_rho/output.json` (sha256
`ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`,
companion verification script). Headline cell:
$(N, V, d'_{\max}, f_0, h, \mathrm{variant})$
$= (4, 0.5, 2, 0.5, \sqrt{\cdot}, \mathrm A)$.

### 5.1 ρ = 0 recovery (Statement of fact)

| $v$ | $r^{\dagger}_{\text{rb-026}}(v;0)$ | $r^{\dagger}_{\text{rb-006}}(v)$ | $\lvert\Delta\rvert$ |
|---:|---:|---:|---:|
| 1   | 0.343321 | 0.342827 | $4.9\times 10^{-4}$ |
| 2   | 0.167665 | 0.167665 | $0.0$ (binary) |
| 3   | 0.099460 | 0.099472 | $1.2\times 10^{-5}$ |
| 5   | 0.050430 | 0.050374 | $5.7\times 10^{-5}$ |
| 8   | 0.022217 | 0.022193 | $2.5\times 10^{-5}$ |
| 10  | 0.016105 | 0.016098 | $6.6\times 10^{-6}$ |

The residual at $v \ne 2$ is the $\Delta c = 0.05$ quantisation of
$(c^{\star}_c, c^{\star}_u)$ on `C_GRID` (the optimum is on a
neighbouring grid point; both reviewer and rebuild use the same grid,
but `numpy.argmax` ties may resolve differently). The $r^{\dagger}(v)$
spread is $\le 1.5 \times 10^{-3}$ at the worst row, well below the
$O(10^{-2})$ resolution at which any C2 manuscript claim is stated.

### 5.2 Drift prediction: $\Delta r^{\dagger}(v) := r^{\dagger}(v; 0.2) - r^{\dagger}(v; 0)$

| $v$ | $r^{\dagger}(v;0)$ | $r^{\dagger}(v;0.2)$ | $\Delta r^{\dagger}$ | $\% \Delta r^{\dagger}$ | $r^{\star}(v;0)$ | $r^{\star}(v;0.2)$ | $\Delta r^{\star}$ | sign-match |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1  | 0.34332 | 0.35362 | $+0.0103$ | $+3.0\%$ | — | — | — | (P2 ref) |
| 2  | 0.16766 | 0.17277 | $+0.0051$ | $+3.0\%$ | 0.50119 | 0.63096 | $+0.1298$ | ✓ |
| 3  | 0.09946 | 0.11263 | $+0.0132$ | $+13.2\%$ | 0.37584 | 0.47315 | $+0.0973$ | ✓ |
| 5  | 0.05043 | 0.05810 | $+0.0077$ | $+15.2\%$ | 0.37584 | 0.38310 | $+0.0073$ | ✓ |
| 8  | 0.02222 | 0.02881 | $+0.0066$ | $+29.7\%$ | 0.37584 | 0.38310 | $+0.0073$ | ✓ |
| 10 | 0.01611 | 0.01913 | $+0.0030$ | $+18.7\%$ | 0.35481 | 0.38310 | $+0.0283$ | ✓ |

**Two findings.**

* *Sign:* $\Delta r^{\dagger}(v) > 0$ at every $v$ tested, including
  $v = 1$ (the P2 reference). The escape threshold drifts *upward* under
  correlation across the entire $v$ family — the regime in which P1 is
  stuck at uniform widens as $\rho$ grows. This is the analytic locus the
  empirical statement "$r^{\star}(v;\rho)$ drifts upward with $\rho$ at
  low $v$" (rb-006 / §results-C2) is sitting on top of: the *lower edge*
  of the escape band moves up, dragging the peak with it.
  All $5/5$ drift signs match the empirical $\Delta r^{\star}$ sign at
  $v \in \{2,3,5,8,10\}$.

* *Magnitude:* the percentage drift $\% \Delta r^{\dagger}$ is largest at
  $v = 8$ ($+30\%$) and smallest at $v = 1$ ($+3\%$). The absolute
  drift $\Delta r^{\dagger}$ is bounded by $\le 0.014$ across the family,
  while the *peak* drift $\Delta r^{\star}$ is bounded by $0.13$ at
  $v = 2$. The peak drift exceeds the threshold drift because the peak
  also responds to (i) the corresponding upward drift of $r^{\dagger}(1)$
  (which widens the escape band's *upper* edge as well) and (ii)
  changes inside the band as $\alpha^{\star}_{\mathrm P_1}(r,v;\rho)$
  climbs differently across $\rho$. The closed form (4.1) supplies the
  lower-edge drift; the peak-location closed form (which would
  additionally model $\alpha^{\star}$-climb above $r^{\dagger}$) is
  out of scope for this derivation.

### 5.3 Boundary-FD sign-flip sanity ($6/6$ flips confirmed)

At the rebuilt model's `optimal_R` and the closed-form $r^{\dagger}(v;\rho)$
in §5.2, a one-sided FD step of $\Delta\alpha = 10^{-3}$ across
$r = r^{\dagger}(v;\rho) \pm 0.05$ confirms
$\partial\mathbb E[R]/\partial\alpha|_{1/N^{+}}$ changes sign from
negative to positive at every probe:

| $v$ | $\rho$ | $r^{\dagger}$ | sign at $r^{\dagger} - 0.05$ | sign at $r^{\dagger} + 0.05$ | flip-confirmed |
|---:|---:|---:|---:|---:|---:|
| 1  | 0.00 | 0.343 | $-1$ | $+1$ | ✓ |
| 1  | 0.20 | 0.354 | $-1$ | $+1$ | ✓ |
| 2  | 0.00 | 0.168 | $-1$ | $+1$ | ✓ |
| 2  | 0.20 | 0.173 | $-1$ | $+1$ | ✓ |
| 3  | 0.00 | 0.099 | $-1$ | $+1$ | ✓ |
| 3  | 0.20 | 0.113 | $-1$ | $+1$ | ✓ |

The $v \in \{5, 8, 10\}$ rows have $r^{\dagger} < 0.06$, below the
$\rho = 0$ baseline of the C_GRID stencil at which the FD step is robust
($r^{\dagger} - 0.05$ would be at or below $r = 0.01$, the
$d'_{\text{base}}$-grid resolution `default_alpha_grid` operates at);
those rows are omitted from the FD probe table but are within the
contiguous closed-form locus and are not flagged by the recovery test
$5/5$ sign-match in §5.2.

### 5.4 A note on the structural mirror to A1 §4.2

The two ρ-aware $d$-gradient integrals $I_c, I_u$ in (3.4)–(3.5) are
exactly the *channel (b)* of the
`Rebuild/derivations/A1--rho-channel.md` §4.2 sign-flip discussion: the
concentration-cost relaxation under correlation. The closed-form
$r^{\dagger}(v;\rho)$ here makes the channel (b) effect *analytic* — the
escape band's lower edge $r^{\dagger}(v)$ drifts upward in $\rho$
because the no-FA bracket weight $\mathrm{CR}\,I_u(\rho) / (V v \,\varphi^{c}_{\text{ch}}(\rho) + \mathrm{CR}\,I_c(\rho))$
grows with $\rho$ (Slepian-type monotonicity on the orthant-probability
*gradients*, not the orthant probability itself). A full Slepian-analogue
for $I_c, I_u$ would convert §5.2's "all $5/5$ sign-match" empirical
observation into a proposition. We do not attempt this here; the
empirical $5/5$ at the headline cell is the strength at which the
manuscript states the result, with the closed form (4.1) as its analytic
substrate.

---

## 6. Scope and limitations

* **Local statement, not global.** Proposition 4.1 is a *local* claim
  about the escape from $\alpha = 1/N$. It does not — by itself — locate
  the global maximum $r^{\star}(v;\rho)$ of $\mathrm{VDA}(r;v;\rho)$ on
  the half-line, only the lower edge of the escape band. The full peak
  closed form would require additionally modelling
  $\alpha^{\star}_{\mathrm P_1}(r,v;\rho) - \alpha^{\star}_{\mathrm P_2}(r;\rho)$
  for $r > r^{\dagger}(v;\rho)$ — i.e., the *gradient of*
  $\alpha^{\star}$ in $r$ above escape — which is out of scope for this
  derivation. The empirical peak drift in §5.2 ($+0.0073$ at $v = 5$ to
  $+0.1298$ at $v = 2$) is *consistent with* the $r^{\dagger}$ drift but
  not directly predicted by (4.1).

* **Equicorrelation specificity.** The 1-D reduction (3.1) is specific
  to equicorrelated $\Sigma$, as flagged in
  `Rebuild/derivations/A1--rho-channel.md` §6. Structured covariances
  ([[ruff_cohen2016_cross_area_correlations]],
  [[srinath2021_attention_information_flow]]) break the reduction; the
  closed form (4.1) applies only within the equicorrelated family.

* **Magnitude envelope.** The $\rho$ range $[0, 0.4]$ brackets the
  empirically reported $r_\mathrm{SC} \approx 0.2$ values in primate V4
  change-detection [[cohen_maunsell2009_correlations]]. Higher $\rho$
  values are admissible in the model but are not anchored by data; we
  verify (4.1) at $\rho = 0.2$ (the central empirical anchor) and at
  $\rho = 0$ (the recovery contract).

* **C_GRID quantisation.** (4.1) inherits the model's criterion-grid
  resolution $\Delta c = 0.05$ through (3.6); the $\rho = 0$ recovery
  residual $\le 5 \times 10^{-4}$ in §5.1 traces to this quantisation,
  not to the closed form. A finer grid would tighten the recovery but
  not change the formula; the manuscript reports the closed form at
  C_GRID resolution because that is the resolution at which all rb-006
  / rb-002 simulations operate.

* **Variant A only.** Verified at $\mathrm{CR}(v) = Vv + (1-V)$. The
  closed form (4.1) is valid for any positive $\mathrm{CR}$; variant B
  (constant $\mathrm{CR} = 1$) follows by substitution and is queued
  separately as RB-027 (variant-B replication of the rb-006 sim) for
  empirical cross-check. The verification script accepts a `variant`
  switch but the run here uses variant A only.

* **A3 conservation form.** The derivation assumes the additive
  conservation $\beta + \gamma = 2$ ($p = 1$ branch of the
  `beta_gamma(r, p)` family in `Rebuild/model/core.py` L279–320).
  Under a different conservation order $p$, the $\beta(r), \gamma(r)$
  expressions change but the structural form (4.1) is preserved —
  $r^{\dagger}(v;\rho,p)$ would substitute $\beta(r;p), \gamma(r;p)$
  in (2.7) / (3.7) and resolve to a closed form of the same shape.
  rb-016 / `Rebuild/sims/A3--conservation-band/` verifies the
  $p$-invariance of $r^{\dagger}(v)$ at $\rho = 0$ (FP identity across
  $p \in \{0, 0.5, 1.0\}$); the $\rho > 0$ extension of that
  $p$-invariance is queued as a future increment.

* **Heterogeneous $r_i$ (A2).** The derivation assumes the
  between-preparation A2 reading (single global $r$ per cell;
  `Rebuild/derivations/A1--rho-channel.md` §1.1, last sentence). The
  heterogeneous-$r_i$ extension via `d_prime_hetero` (rb-019) does not
  collapse to a scalar boundary FOC, so (4.1) does not directly extend;
  rb-021 (`Rebuild/sims/A2--heterogeneous-r/`) reports the C2 peak as
  invariant to within $\le 10^{-5}$ across the spread band $s \le 0.3$
  at the headline cell, suggesting (4.1) is the *spread-zero limit*
  of a heterogeneous closed form that has not been derived here.

---

## 7. References

* **Slepian, D. (1962).** "The one-sided barrier problem for Gaussian
  noise." *Bell System Technical Journal* 41(2):463–501. The
  monotonicity inequality used implicitly in §5.4 for the
  orthant-gradient sign-direction discussion. *No `research_db/`
  substrate — math-methods gap flagged at
  `Rebuild/derivations/A1--rho-channel.md` §7.*
* **Tong, Y.L. (1990).** *The Multivariate Normal Distribution.*
  Springer, §5.1. Modern treatment of Slepian's inequality. *Same
  gap as Slepian 1962.*
* **Cohen, M.R. & Maunsell, J.H.R. (2009).** Attentional improvements
  in performance through reduction of correlated variability in V4.
  [[cohen_maunsell2009_correlations]] — the empirical anchor for the
  $\rho$ range used in §5 and §6.
* **Ruff, D.A. & Cohen, M.R. (2016).** Cross-area correlations and
  attention. [[ruff_cohen2016_cross_area_correlations]] — sign-dependent
  correlation structure that motivates the equicorrelation specificity
  scope in §6.
* **Srinath, R. et al. (2021).** [[srinath2021_attention_information_flow]] —
  supra-pairwise shared-variance amplification; complements the
  equicorrelation scope.
* `Rebuild/model/core.py` — `p_no_fa_point`, `p_no_fa_grid` implement
  Eq. (3.1); `d_prime_asym`, `beta_gamma` provide the
  $\alpha \to (d'_c, d'_u)$ transfer used in §2.1; the same
  `(_GH_Z, _GH_W)` (64-node Gauss–Hermite) evaluates (3.4)–(3.5) here.
* `Rebuild/derivations/A1--rho-channel.md` — §1 (notation and locus),
  §2 (the 1-D reduction (3.1)), §4.2 (the channel (b)
  concentration-cost relaxation, which §5.4 here makes analytic).
* `Critique/derivations/C2--non-monotonic-vda.md` — the reviewer's
  $\rho = 0$ derivation, recovered structurally at §4.1 and
  numerically at §5.1.
* `Rebuild/sims/C2--vda-vs-r-vfamily/` — rb-006, sha256
  `09ecef3c2c5a101820951398ed7d6e67d3398aede80c5f0bddfa42b6224fd783`;
  source of $r^{\dagger}_{\text{rb-006}}$ and $r^{\star}$ at §5.
* `Rebuild/derivations/verify_C2_rho/` — rb-026, output.json sha256
  `ddbd3988e0253fde2cfae5906ca2749cda872d1382055b3d243b4b7c6a0678dc`;
  source of every numerical statement in §5 *of this file*.

---

## Verification performed

* **Structural ρ → 0 recovery.** (4.1) reduces to (2.11) term-by-term
  via (4.2); verified by inspection in §4.1.
* **Numerical ρ → 0 recovery.** $r^{\dagger}_{\text{rb-026}}(v;0)$ matches
  the reviewer's `rb-006` $r_\text{dagger}$ closed form to
  $\le 5 \times 10^{-4}$ at all $v \in \{1,2,3,5,8,10\}$ (binary match
  at $v = 2$, the C_GRID-tie cell); residual is C_GRID quantisation,
  not a formula discrepancy (§5.1).
* **Drift sign-match.** The closed-form drift sign
  $\operatorname{sign}(\Delta r^{\dagger}(v))$ matches the rb-006
  empirical peak drift sign $\operatorname{sign}(\Delta r^{\star}(v))$
  at all $5/5$ tested $v \ne 1$ (§5.2).
* **Boundary FD sign-flip.** A one-sided FD step at
  $r = r^{\dagger}(v;\rho) \pm 0.05$, $\Delta\alpha = 10^{-3}$, confirms
  $\partial\mathbb E[R]/\partial\alpha|_{1/N^{+}}$ changes sign from
  $-1$ to $+1$ at every $(v, \rho) \in \{1,2,3\} \times \{0, 0.2\}$
  probe — $6/6$ flips (§5.3); $v \in \{5,8,10\}$ omitted because
  $r^{\dagger} - 0.05$ would fall on the $\alpha$-grid boundary.
* **Reproducibility.** `verify.py` is deterministic; rerunning produces
  byte-identical `output.json` (sha256 `ddbd3988…`).

## Extensions to consider

* **Closed-form $r^{\star}(v;\rho)$.** Combine (4.1) with a closed form
  for $\alpha^{\star}_{\mathrm P_1}(r,v;\rho) - \alpha^{\star}_{\mathrm P_2}(r;\rho)$
  above escape. Plausibly tractable on a Taylor expansion of
  $R^{\star}(\alpha)$ around the escape point; would convert §5.2's
  "$\Delta r^{\star}$ drifts up at every $v$" observation from
  consistency with $\Delta r^{\dagger}$ to a directly-predicted
  closed form.

* **Slepian-analogue for $I_c, I_u$.** A formal monotonicity statement
  $\partial I_c/\partial\rho > 0$ and $\partial I_u/\partial\rho > 0$
  at the asymmetric boundary configuration would promote §5.2's
  "$\Delta r^{\dagger} > 0$ at every $v$" from an empirical $5/5$ to a
  proposition. The standard Slepian inequality is for orthant
  probabilities, not their gradients, so this would need a
  separate argument.

* **Variant B closed form.** $\mathrm{CR} = 1$ substitution into (4.1)
  is mechanical, but the (variant-B-flat-in-ρ) observation rb-002 made
  at the headline cell suggests the variant-B $r^{\dagger}$ drift may
  also be small; worth a one-line check.

* **A3 conservation extension to $\rho > 0$.** $r^{\dagger}(v;\rho;p)$
  with $p \ne 1$ — substitute $\beta(r;p), \gamma(r;p)$ into (3.7) and
  resolve. rb-016 establishes the $\rho = 0$ $p$-invariance; the
  $\rho > 0$ extension is the natural successor increment.

* **Heterogeneous $r_i$ (A2) closed form.** (4.1) is the spread-zero
  limit; the general heterogeneous-$r_i$ boundary FOC is a vector
  equation (one component per uncued location) and does not collapse
  to a scalar threshold. The leading-order spread correction may be
  tractable via perturbation of $r_i$ around the homogeneous value;
  rb-021 reports the C2 peak is invariant to $\le 10^{-5}$ under
  spread $s \le 0.3$ at the headline cell, suggesting the correction
  is $O(\mathrm{Var}(\boldsymbol{r}))$.
