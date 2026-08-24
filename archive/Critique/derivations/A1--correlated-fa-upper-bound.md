# Re-derivation: does per-location independence (A1) upper-bound the VDA benefit?

**Claim under attack (A1 / paper §5.5, verbatim):**
> "the model assumes independent per-location SDT decisions; real observers
> emit a single global response, introducing dependencies that could alter the
> optimal policy. Our results therefore represent an **upper bound on VDA
> benefit**."

**Attack vector:** re-derivation (CR-052, run-017), with independent numerical
corroboration in `Critique/replications/A1--correlated-fa/`.
**Designated role:** the *second* A1 vector (the first, run-016, was literature
and left A1 `WEAKLY-SUPPORTED`); this run is the sign-decider.

This derivation (i) fixes *where* independence enters the paper's reward;
(ii) writes the exact correlated generalisation; (iii) proves the
Slepian monotonicity that pins each policy's reward; (iv) shows the VDA
*difference* is **not** sign-determined by that monotonicity, exhibiting two
competing channels; and (v) reports the numerical adjudication, which **refutes
the uniform "upper bound on VDA" reading**.

---

## 1. Setup and the locus of independence

### 1.1 Notation and SDT primitives

Mission §2.1–§2.5. Equal-variance Gaussian SDT: at location $i$, the decision
variable on a **no-change** trial is $X_i \sim \mathcal N(-d'_i/2,\,1)$ and a
*false alarm* is the event $\{X_i > c_i\}$; on a **change** trial at $i$ it is
$X_i \sim \mathcal N(+d'_i/2,\,1)$ and a *hit* is $\{X_i > c_i\}$. Hence

$$
\mathrm{HR}(d',c)=\Phi\!\big(\tfrac{d'}{2}-c\big), \qquad
\mathrm{FAR}(d',c)=\Phi\!\big(-\tfrac{d'}{2}-c\big),
$$

and the per-location **no-false-alarm** probability is

$$
1-\mathrm{FAR}_i \;=\; \Phi\!\big(\tfrac{d'_i}{2}+c_i\big) \;=\; \Phi(b_i),
\qquad b_i := c_i + \tfrac{d'_i}{2}\in\mathbb R .
\tag{1.1}
$$

$b_i$ is the $z$-score threshold below which $X_i$ stays on a no-change trial:
$P(X_i\le c_i)=\Phi\big(c_i-(-d'_i/2)\big)=\Phi(b_i)$, consistent with (1.1).

### 1.2 Where A1 enters — exactly one place

The expected reward (mission §2.5, paper Eq. 9) is

$$
\mathbb E[R]
=\underbrace{0.5\,\big[\,V\,\mathrm{HR}_c\,v + (1-V)\,\mathrm{HR}_u\,\big]}_{\text{change trial (prob }0.5)}
\;+\;
\underbrace{0.5\;P_{\text{no-fa}}\;\mathrm{CR}}_{\text{no-change trial (prob }0.5)} ,
\tag{1.2}
$$

with $\mathrm{CR}=V v+(1-V)$ (variant A) or $1$ (variant B), and

$$
P_{\text{no-fa}}^{\text{indep}}
=(1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}
=\Phi(b_c)\,\Phi(b_u)^{N-1}.
\tag{1.3}
$$

**Observation (the booking).** The change-trial term of (1.2) is *linear* in the
marginal hit rates $\mathrm{HR}_c,\mathrm{HR}_u$. On a change trial the change is
at **one** location only (the cued, w.p. $V$; a specific uncued, w.p.
$(1-V)/(N-1)$), so detection reward never forms a cross-location product.
**The only cross-location product in the whole reward is $P_{\text{no-fa}}$**,
Eq. (1.3). Independence (A1) *is* that product, and nothing else.

Therefore replacing (1.3) by the correlated joint orthant probability is the
**faithful and complete** relaxation of A1 within this reward structure
(*Booking 1*). The alternative *Booking 2* — correlation changing a *pooled*
population sensitivity $d'^2\propto(\Delta\mu)^\top\Sigma^{-1}(\Delta\mu)$ — has
no locus in (1.2): there is no pooled detection statistic, so Booking 2 requires
a **global** "change-detected-somewhere" decision rule, which is assumption
**A6** (single global response), *not* A1. This disentangles the two clauses
§5.5 bundles: *"independent per-location SDT decisions"* $=$ A1 (Booking 1,
this file); *"emit a single global response"* $=$ A6 (Booking 2, CR-011).

---

## 2. The correlated decision model and its exact 1-D reduction

Let the no-change decision variables be jointly Gaussian with standardised
marginals and **equicorrelation** $\rho\in[0,1)$:
$\mathbf X\sim\mathcal N(\boldsymbol\mu,\Sigma)$, $\mu_i=-d'_i/2$,
$\Sigma_{ii}=1$, $\Sigma_{ij}=\rho\ (i\neq j)$. Use the one-factor
representation

$$
X_i = \mu_i + \sqrt{\rho}\,Z + \sqrt{1-\rho}\,\varepsilon_i,
\qquad Z,\varepsilon_i\stackrel{\text{iid}}{\sim}\mathcal N(0,1),
\tag{2.1}
$$

which reproduces $\operatorname{Var}(X_i)=\rho+(1-\rho)=1$ and
$\operatorname{Cov}(X_i,X_j)=\rho$. Conditioning on the **shared factor** $Z=z$
makes the locations independent:

$$
P(X_i\le c_i\mid z)
=\Phi\!\left(\frac{c_i-\mu_i-\sqrt\rho\,z}{\sqrt{1-\rho}}\right)
=\Phi\!\left(\frac{b_i-\sqrt\rho\,z}{\sqrt{1-\rho}}\right).
$$

Integrating out $Z$ gives the **exact** correlated no-false-alarm probability:

$$
\boxed{\;
P_{\text{no-fa}}(\rho)
=\int_{-\infty}^{\infty}
\Phi\!\left(\frac{b_c-\sqrt\rho\,z}{\sqrt{1-\rho}}\right)
\Phi\!\left(\frac{b_u-\sqrt\rho\,z}{\sqrt{1-\rho}}\right)^{N-1}
\varphi(z)\,dz \;}
\tag{2.2}
$$

with $\varphi$ the standard normal density. This is a **one-dimensional**
quadrature — no $N$-variate normal CDF is required; the reduction is exact for
equicorrelation. At $\rho=0$: $\sqrt\rho=0$, $\sqrt{1-\rho}=1$, the integrand is
constant in $z$, and $\int\varphi=1$, so
$P_{\text{no-fa}}(0)=\Phi(b_c)\Phi(b_u)^{N-1}$ — Eq. (1.3) recovered exactly.

*Numerical realisation.* 64-node Gauss–Hermite quadrature of (2.2)
(substitution $z=\sqrt2\,t$); GH-64 vs GH-128 agree to $7.8\times10^{-16}$,
$\sum$weights $=1$ to machine precision, and $P_{\text{no-fa}}(10^{-6})$ matches
the product to $3.4\times10^{-7}$. (Replication validation block.)

---

## 3. Slepian monotonicity: independence is the FA-penalty-maximising corner

**Proposition 3.1 (Slepian, 1962).** For a multivariate normal with standardised
marginals, the orthant probability $P(\forall i:\,X_i\le c_i)$ is
non-decreasing in each off-diagonal correlation. For exchangeable
equicorrelation, $P_{\text{no-fa}}(\rho)$ is non-decreasing in $\rho$, so

$$
P_{\text{no-fa}}(\rho)\;\ge\;P_{\text{no-fa}}(0)=\Phi(b_c)\Phi(b_u)^{N-1}
\qquad\forall\,\rho\ge 0,
\tag{3.1}
$$

with strict inequality for $\rho>0$ at finite thresholds. *(Verified numerically:
$P_{\text{no-fa}}(\rho)$ is monotone $\uparrow$ over $\rho\in\{0,.05,.1,.2,.3,.4,.6,.8\}$
and $\rho=0$ is the minimum.)*

**Consequence.** The **independent corner $\rho=0$ minimises** the
correct-rejection reward $0.5\,P_{\text{no-fa}}\,\mathrm{CR}$ and therefore
**maximises** the aggregate false-alarm penalty. Equivalently: positive
correlation *relaxes* the multiple-comparisons pressure that, in the independent
model, forces conservative criteria to keep the $N$-fold FA product small. This
confirms the run-016 closed-form claim that the paper's reported quantities are
computed at the stiffest-FA-penalty boundary in correlation space.

**Corollary 3.2 (each policy reward rises with $\rho$).** Fix $\alpha$ (hence
$d'_c,d'_u$). Because the hit terms in (1.2) are $\rho$-independent and
$P_{\text{no-fa}}(\rho)\ge P_{\text{no-fa}}(0)$ *pointwise* in $(c_c,c_u)$,

$$
R^\star(\alpha;\rho)
:=\max_{c_c,c_u}\mathbb E[R]
\;\ge\; R^\star(\alpha;0),\qquad\text{non-decreasing in }\rho .
\tag{3.2}
$$

So $R(\mathrm P1),R(\mathrm P2),R(\mathrm P3),R(\mathrm P4)$ **all rise** with
$\rho$.

---

## 4. The VDA difference is NOT sign-determined — two competing channels

The VDA benefit is a **difference** of two rewards that (3.2) only tells us both
increase:

$$
\mathrm{VDA}(\rho)=R(\mathrm P1;\rho)-R(\mathrm P2;\rho),
$$

$\mathrm P1$ jointly optimising $(\alpha,c_c,c_u)$ at value $v$, $\mathrm P2$
freezing $\alpha=\alpha^\star(v{=}1)$ and re-optimising criteria. Monotonicity
(Cor. 3.2) says nothing about the sign of the *difference*. Two mechanisms push
opposite ways:

* **(a) Criterion-devaluation.** Raising $\rho$ inflates $P_{\text{no-fa}}$ most
  at liberal criteria (small $b$, where $\Phi$ is far from $1$ and has room to
  rise). This flattens the reward's dependence on the criteria, shrinking the
  *gain* from moving criteria off the floor: $R(\mathrm P3)-R(\mathrm P4)$ falls
  as a fraction of the total. The criterion lever is **devalued**, shifting
  value-encoding load toward attention.

* **(b) Concentration-cost relaxation.** At high $v$, $\mathrm P1$ concentrates
  attention ($\alpha\!\uparrow$), raising $d'_c$ but **lowering $d'_u$**, which
  raises $\mathrm{FAR}_u$ — a cost compounded over $N-1$ locations in the
  product (1.3). Under $\rho>0$ the aggregate penalty of those $N-1$ degraded
  uncued FARs is **relaxed** (Prop. 3.1), so concentrating attention is
  *cheaper* and value-directed attention ($\mathrm P1$ over $\mathrm P2$)
  becomes **more** rewarding $\Rightarrow$ $\mathrm{VDA}\uparrow$.

The paper's §5.5 implicitly assumes channel (b) is absent — that "dependencies
can only reduce the achievable policy advantage." That step is **never derived**.
The monotonicity that *is* true (Cor. 3.2) is about levels, not the difference;
the difference's sign is an empirical question. We resolve it numerically.

---

## 5. Numerical adjudication (corroboration)

Headline cell $V=0.5,\,v=5,\,N=4,\,d'_{\max}=2,\,f_0=0.5,\,h=\sqrt{\cdot}$,
variant A; $\rho\in\{0,0.1,0.2,0.3,0.4\}$ bracketing Cohen & Maunsell (2009)
$r_{SC}\approx0.2$. Full data: `replications/A1--correlated-fa/output/results.json`
(numeric digest `b9828f02…`, byte-identical on re-run).

### 5.1 The VDA$(r)$ curve is *reshaped*, with a crossover at $r\approx0.5$

| $r$ | $\rho{=}0$ | $\rho{=}0.2$ | $\rho{=}0.4$ | $\Delta$ at $\rho{=}0.4$ |
|---|---|---|---|---|
| 0.100 | 0.01848 | 0.01268 | 0.00257 | $-0.0159$ |
| 0.316 | 0.07632 | 0.07045 | 0.05970 | $-0.0166$ |
| **0.383** (peak) | **0.07986** | 0.07955 | 0.07355 | $-0.0063$ |
| 0.562 | 0.06905 | 0.07166 | 0.07230 | $\mathbf{+0.0033}$ |
| **0.825** | 0.04860 | 0.05730 | 0.05866 | $\mathbf{+0.0101}$ |
| 1.000 | 0.03983 | 0.04565 | 0.04823 | $\mathbf{+0.0084}$ |
| 3.162 | 0.00809 | 0.00960 | 0.01154 | $\mathbf{+0.0035}$ |
| 10.00 | 0.00085 | 0.00184 | 0.00166 | $\mathbf{+0.0008}$ |

**The sign of $d\mathrm{VDA}/d\rho$ depends on $r$:** correlation **suppresses**
VDA in the cost-dominant regime ($r\lesssim0.5$, which contains the C2 peak) and
**amplifies** it throughout the benefit-dominant regime ($r\gtrsim0.5$), by up
to $+0.0101$ at $r\approx0.825,\rho=0.4$ — about **$+20\%$ of the local VDA**.
The excess over the $\rho=0$ curve **grows monotonically with $\rho$**
(max excess $+0.0048,+0.0087,+0.0098,+0.0101$ at $\rho=0.1,0.2,0.3,0.4$).

A single "upper bound on VDA" statement therefore **cannot be correct**: it would
require $d\mathrm{VDA}/d\rho\le0$ everywhere, but the sign flips at $r\approx0.5$.

### 5.2 Even the headline peak is not upper-bounded

At the peak $r\approx0.383$: $\mathrm{VDA}(\rho{=}0.1)=0.08110>0.07986=\mathrm{VDA}(\rho{=}0)$
($+0.0013$). So the independent model does **not** upper-bound VDA even at its
own peak for small correlation. For the empirically central $\rho\approx0.2$ the
peak is essentially unchanged ($0.0796$ vs $0.0799$, $-0.4\%$) and it falls for
$\rho\ge0.3$ — so the **C2 headline number ($\sim0.08$) is robust**; what fails
is the *directional self-characterisation*, not the magnitude.

### 5.3 What independence *does* upper-bound: the criterion fraction

The criterion fraction $\mathrm{CF}=[R(\mathrm P3)-R(\mathrm P4)]/[R(\mathrm P1)-R(\mathrm P4)]$
**falls monotonically with $\rho$** (variant A):

| $r$ | $\rho{=}0$ | $\rho{=}0.2$ | $\rho{=}0.4$ |
|---|---|---|---|
| 0.398 | 0.8295 | 0.8071 | 0.7875 |
| 1.000 | 0.7282 | 0.6903 | 0.6473 |
| 3.162 | 0.6409 | 0.5936 | 0.5386 |

This is exactly channel (a): relaxing the FA penalty **devalues the criterion
lever**, so criterion's *share* of value encoding shrinks. The correct reading
of §5.5 is therefore the **inverse** of what the paper wrote:

$$
\mathrm{CF}(\rho{=}0)\;\ge\;\mathrm{CF}(\rho),\qquad\text{i.e. independence
upper-bounds the \emph{criterion fraction}, not the VDA.}
$$

The paper attributes "$60$–$96\%$ of value-related reward to criterion" at
$\rho=0$, the criterion-maximising corner. Under empirically realistic
correlation that share drops (at $r=3.16$, $\rho=0.4$: $0.64\to0.54$, toward the
$0.5$ dominance boundary — deepening the same benefit-dominant corner where C1 is
already CONTESTED, run-003, and where A3's $\beta\gamma=1$ swap already pushed
CF down, run-011). The three relaxations compound in one corner.

*(Variant B: VDA is tiny ($\sim0.003$–$0.004$) and the relative upper-bound
excess is large but absolute negligible; CF is higher and roughly flat because
the fixed CR removes the value-coupling that drives the variant-A mechanism. The
variant-A result is the load-bearing one.)*

---

## 6. The unstated step, and the verdict implication

**The paper's derivation gap.** §5.5 states the "upper bound on VDA benefit"
with **no derivation**. The implicit premise — dependencies can only *reduce* the
realisable VDA — is false: the only valid monotonicity (Cor. 3.2,
$\partial R^\star/\partial\rho\ge0$ per policy) concerns *levels*, and the VDA
*difference* genuinely rises in the benefit-dominant regime via channel (b). The
claim does not follow from the paper's own model.

**Verdict implication (A1: WEAKLY-SUPPORTED $\to$ CONTESTED).** A second,
distinct attack vector (re-derivation + corroboration) has now *succeeded*: the
§5.5 directional self-characterisation is too strong as written. It should be
reformulated as:

> Positive cross-location decision correlations $\rho$ leave the headline VDA
> peak ($\sim0.08$ at $r\approx0.38$) essentially unchanged for empirically
> central $\rho\approx0.2$, but the independent model is **not** a uniform upper
> bound on VDA: in the benefit-dominant regime ($r\gtrsim0.5$) correlation
> *amplifies* VDA by up to $\sim20\%$ (at $\rho=0.4$), the excess growing with
> $\rho$. Independence instead upper-bounds the **criterion fraction**
> ($\mathrm{CF}(0)\ge\mathrm{CF}(\rho)$), so it *over-states* criterion's share
> of value encoding. The §5.2 design advice ("VDA negligible outside the narrow
> regime") inherits the benefit-dominant-tail error.

This is `CONTESTED`, not `REFUTED`: the headline magnitudes survive (C2 peak
robust; CF still $>0.5$ in the cited cells), and A1 remains the field-standard
behavioural idealisation (run-016, [[hawkins1990_attention_detectability]]). It
is not `CONFIRMED-CONDITIONAL` because the attack *shifted the interpretation of
a quantity the paper actively uses* (the §5.5→§5.2 directional chain), which the
CR-052 decision rule designates as failure.

---

## 7. References

- **Slepian, D. (1962).** "The one-sided barrier problem for Gaussian noise."
  *Bell System Technical Journal* 41(2):463–501. — Monotonicity of Gaussian
  orthant probabilities in the correlations (Prop. 3.1). *No wiki substrate
  (math-methods gap; mirrors the C5 floating-point and A8 majorization gaps).*
- **Cohen, M.R. & Maunsell, J.H.R. (2009).** [[cohen_maunsell2009_correlations]]
  — macaque change-detection with a peripheral validity cue; $r_{SC}\approx0.2$;
  $>80\%$ of attention's behavioural benefit via correlation reduction. Sets the
  empirically relevant $\rho$ range and motivates the whole attack.
- **Ruff, D.A. & Cohen, M.R. (2016).** [[ruff_cohen2016_cross_area_correlations]]
  — sign-dependent (within-down / between-up) correlation structure; equicorr-
  elation is a deliberate simplification (one counterexample suffices to refute
  a uniform bound).
- **Srinath, R. et al. (2021).** [[srinath2021_attention_information_flow]] —
  supra-pairwise shared-variance amplification; caps any "add a single $\rho$"
  patch.
- Paper Eq. (9) / §2.5 (the $P_{\text{no-fa}}$ product); §5.5 (the claim);
  mission §2.1–§2.5, §2.7 A1/A6.
- Reuses the independent-model optimiser from
  `Critique/replications/C5--symmetric-recovery/` and `C1--criterion-fraction-floor/`.

*Companion replication:* `Critique/replications/A1--correlated-fa/` (run.py,
README.md, notes.md, output/results.json).
