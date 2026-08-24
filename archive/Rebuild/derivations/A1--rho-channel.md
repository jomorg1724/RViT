---
type: derivation
project: AttentionManuscript / VDA-rebuild
agent: constructive-rebuilder
backlog_id: RB-003
claim_id: A1
status: drafted
created: 2026-05-25
backing_for: "Rebuild/manuscript/sections/appendix-derivation-A1 (and the §model 'three levers, not two' reframe)"
backed_by_sim: "Rebuild/sims/A1--rho-channel/ (rb-002, sha256 b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614)"
implements: "Rebuild/model/core.py: p_no_fa_point, p_no_fa_grid"
recovery_test: "Rebuild/model/tests/test_recovery.py (sha256 d3c62215cedbe2f797c484a8d76e8bef1d5ac42cdb3092ff099a34aea1b6f18f, 7/7 PASS)"
voice: independent re-derivation in the rebuild's voice; not a copy of Critique/derivations/A1--correlated-fa-upper-bound.md
---

# A1 — The decorrelation channel

> *The rebuilt model promotes the inherited paper's per-location-independence
> assumption (A1) to a tunable equicorrelation parameter $\rho \in [0,1)$. This
> appendix derives the equicorrelated reward in closed form, exhibits the exact
> one-dimensional reduction that the model's `p_no_fa_*` routines implement,
> proves the per-policy monotonicity that pins the reward levels, and then
> shows that this monotonicity does **not** sign-determine the value-directed-
> attention (VDA) difference. The latter splits into two competing channels
> whose relative weight depends on the cost--benefit ratio $r$. The
> consequence — that independence upper-bounds the **criterion fraction** but
> not VDA — is the rebuilt model's normative replacement for the inherited
> §5.5 self-characterisation. Every numerical statement here is sourced from
> the `Rebuild/sims/A1--rho-channel/` deliverable, sha256
> `b692c064…`, and every formula is the one the `Rebuild/model/core.py`
> code implements.*

Notation and SDT primitives follow `agents/paper_rebuilder_prompt.md` §2.2
and the inherited model. The reader who wants a compressed reminder will find
one in §1.1 below.

---

## 1. Setup and the locus of A1

### 1.1 Notation

Let $N \ge 2$ be the number of locations, indexed so that $i=c$ is the cued
location and $i=1,\dots,N-1$ enumerates the $N-1$ uncued locations. Each
location carries an equal-variance Gaussian decision variable: on a no-change
trial at $i$,
$$
  X_i \;\sim\; \mathcal N\!\big(-d'_i/2,\; 1\big),
  \qquad
  \text{a false alarm is the event } \{X_i > c_i\};
$$
on a change trial at $i$ the mean is $+d'_i/2$ and a hit is again
$\{X_i > c_i\}$. The per-location hit and false-alarm rates are
$$
  \mathrm{HR}_i \;=\; \Phi(d'_i/2 - c_i), \qquad
  \mathrm{FAR}_i \;=\; \Phi(-d'_i/2 - c_i),
  \tag{1.1}
$$
and the per-location no-FA probability is
$$
  1 - \mathrm{FAR}_i \;=\; \Phi(b_i),
  \qquad
  b_i := c_i + d'_i/2 \in \mathbb R .
  \tag{1.2}
$$
The variable $b_i$ is the $z$-score the no-change decision variable must
stay below; raising $b_i$ makes the criterion stricter (smaller
$\mathrm{FAR}_i$). The cued sensitivity $d'_c$ and uncued sensitivity
$d'_u$ are determined by the attention allocation $\alpha \in [0,1]$ and
the cost--benefit ratio $r$ through the asymmetric transfer
$d'_c = d'_{\max} \cdot f(\alpha;\,\beta(r))$,
$d'_u = d'_{\max} \cdot f(1 - \alpha;\,\gamma(r))$ — see
`Rebuild/model/core.py:d_prime_asym` for the exact form used in
recovery tests and simulations. Per A2 we operate with a single global
$r$ in the headline analysis (`agents/paper_rebuilder_prompt.md` §3.2);
heterogeneous $r_i$ is treated as a separate extension (RB-014/RB-018).

### 1.2 The reward and the booking that exposes A1

Mission §2.5 (and the inherited paper's Eq. 9) gives the expected reward as
$$
  \mathbb E[R]
  \;=\;
  \tfrac{1}{2}\big[\,V\,\mathrm{HR}_c\,v + (1-V)\,\mathrm{HR}_u\,\big]
  \;+\;
  \tfrac{1}{2}\,P_{\text{no-fa}}\,\mathrm{CR},
  \tag{1.3}
$$
with cue validity $V \in [1/N,\,1]$, value $v \ge 1$, and correct-rejection
reward $\mathrm{CR} = Vv + (1-V)$ (variant A) or $\mathrm{CR} = 1$
(variant B). The first bracket is the *change-trial* expected reward, the
second is the *no-change-trial* expected reward (each trial type has prior
$1/2$).

We need to be explicit about where the per-location-independence assumption
A1 enters this expression. On any change trial the change is at *one*
location only — the cued, with probability $V$, or a specific uncued, with
probability $(1-V)/(N-1)$ — so the change-trial bracket reduces to per-
location *marginal* hit rates and never multiplies probabilities across
locations. The only cross-location product in (1.3) is therefore the
no-change-trial probability that no location false-alarms:
$$
  P_{\text{no-fa}}^{\text{indep}}
  \;=\;
  (1 - \mathrm{FAR}_c)(1 - \mathrm{FAR}_u)^{N-1}
  \;=\;
  \Phi(b_c)\,\Phi(b_u)^{N-1}.
  \tag{1.4}
$$

> **Booking.** The independence assumption A1 enters $\mathbb E[R]$ in
> *exactly one place* — the product (1.4). Replacing this product by the
> correlated joint orthant probability is therefore the faithful and
> complete relaxation of A1 within the reward structure (1.3).

This booking matters because it separates A1 from a different relaxation
the inherited paper's §5.5 sometimes conflates with it: a *global*
"change-detected-somewhere" decision rule. The latter would introduce
correlation through a pooled detection statistic and is a relaxation of
assumption A6 (homogeneous decision rule), not of A1. A1 is exactly
(1.4); nothing more, nothing less.

---

## 2. The correlated decision model and its exact 1-D reduction

### 2.1 The equicorrelated joint distribution

Let the no-change decision variables be jointly Gaussian with standardised
marginals and equicorrelation $\rho \in [0,1)$:
$$
  \mathbf X \;\sim\; \mathcal N(\boldsymbol\mu,\,\Sigma),
  \quad
  \mu_i = -d'_i/2,
  \quad
  \Sigma_{ii} = 1,
  \quad
  \Sigma_{ij} = \rho \ (i\neq j).
  \tag{2.1}
$$
Equicorrelation is the natural one-parameter relaxation of A1: it admits
an exact dimension reduction (below) and covers the empirically central
"shared-attention" correlation structure measured in primate area V4 by
[[cohen_maunsell2009_correlations]] ($r_\mathrm{SC} \approx 0.2$ in
foveal change-detection), which is the empirical anchor used to set the
rebuilt model's $\rho$ band.

### 2.2 The one-factor representation

Decompose each $X_i$ into a shared latent and an idiosyncratic component:
$$
  X_i \;=\; \mu_i \,+\, \sqrt{\rho}\;Z \,+\, \sqrt{1-\rho}\;\varepsilon_i,
  \qquad
  Z,\varepsilon_1,\dots,\varepsilon_N \stackrel{\text{iid}}{\sim} \mathcal N(0,1).
  \tag{2.2}
$$
This reproduces $\operatorname{Var}(X_i) = \rho + (1-\rho) = 1$ and
$\operatorname{Cov}(X_i, X_j) = \rho$ for $i \neq j$, recovering (2.1).
Conditioning on $Z = z$ makes the locations independent — exactly the
behaviour that makes a 1-D quadrature exact for equicorrelation.

### 2.3 The exact joint orthant probability

For the no-FA event on a no-change trial we want $\Pr(\bigcap_i \{X_i \le c_i\})$.
Conditional on $Z = z$,
$$
  \Pr(X_i \le c_i \mid Z = z)
  \;=\;
  \Phi\!\left(\frac{c_i - \mu_i - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
  \;=\;
  \Phi\!\left(\frac{b_i - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right),
$$
using $\mu_i = -d'_i/2$ and $b_i = c_i + d'_i/2$. Independence of the
$\varepsilon_i$ given $Z$ lets us multiply across $i$, then integrate $Z$
out against the standard normal density $\varphi(z) = (2\pi)^{-1/2}
e^{-z^2/2}$. The result is the **exact** one-dimensional integral
$$
\boxed{\;
P_{\text{no-fa}}(\rho)
\;=\;
\int_{-\infty}^{\infty}
\Phi\!\left(\frac{b_c - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)
\Phi\!\left(\frac{b_u - \sqrt{\rho}\,z}{\sqrt{1-\rho}}\right)^{N-1}
\varphi(z)\,dz.
\;}
\tag{2.3}
$$
Equation (2.3) is exact for any $N$ and any $\rho \in [0,1)$. No
multivariate-normal CDF is needed; equicorrelation collapses the
$N$-dimensional integral to a one-dimensional one through (2.2).

### 2.4 $\rho \to 0$ recovery and Sterbenz centre

At $\rho = 0$ the integrand of (2.3) is constant in $z$
($\sqrt{\rho} = 0$ kills the $z$-dependence, $\sqrt{1-\rho} = 1$ is the
identity scaling), $\int \varphi = 1$, and (2.3) reduces to (1.4):
$$
  P_{\text{no-fa}}(0)
  \;=\;
  \Phi(b_c)\,\Phi(b_u)^{N-1}.
  \tag{2.4}
$$
This is the **recovery contract** the rebuilt model is bound to honour:
the inherited (independent-SDT) reward must be reproduced exactly when
$\rho = 0$. The corresponding recovery test
`Rebuild/model/tests/test_recovery.py` checks this on all four
single-cell reference values inherited from
`Critique/replications/A1--correlated-fa/`, and on the headline
peak-VDA value $\mathrm{VDA}^\star(\rho{=}0) \approx 0.07986$; all
passes are bit-for-bit identical to floating-point representation
(sha256 `d3c62215…`).

### 2.5 Numerical realisation

The rebuilt model uses 64-node Gauss–Hermite quadrature in `Rebuild/
model/core.py:p_no_fa_point` and `:p_no_fa_grid` to evaluate (2.3).
With the standard substitution $z = \sqrt{2}\,t$, the integral becomes
$$
  P_{\text{no-fa}}(\rho)
  \;=\;
  \frac{1}{\sqrt{\pi}}\int_{-\infty}^{\infty}
  \Phi(\xi_c(t)) \,\Phi(\xi_u(t))^{N-1}\, e^{-t^2}\,dt,
  \qquad
  \xi_i(t) := \frac{b_i - \sqrt{2\rho}\,t}{\sqrt{1-\rho}},
  \tag{2.5}
$$
which Gauss–Hermite-$n_q$ approximates as
$\frac{1}{\sqrt{\pi}}\sum_{k=1}^{n_q} w_k \,\Phi(\xi_c(t_k))\,\Phi(\xi_u(t_k))^{N-1}$.
At $n_q = 64$ the quadrature is agreeing with $n_q = 128$ to better than
$10^{-15}$, $\sum_k w_k = \sqrt{\pi}$ to machine precision, and
$P_{\text{no-fa}}(10^{-6})$ matches (2.4) to $3.4\times 10^{-7}$. This
buys the recovery-test identity at $\rho = 0$ and a uniform stiffness
of $\le 10^{-12}$ across the operating $\rho$ band of the rebuilt
manuscript ($\rho \in \{0,\,0.05,\,0.1,\,0.2,\,0.3,\,0.4\}$).

---

## 3. Slepian monotonicity and per-policy reward bounds

### 3.1 The orthant probability is monotone in $\rho$

**Proposition 3.1 (Slepian 1962; equicorrelated specialisation).** For a
multivariate normal vector $\mathbf X$ with standardised marginals, the
orthant probability $\Pr(\bigcap_i \{X_i \le c_i\})$ is non-decreasing in
each off-diagonal correlation $\Sigma_{ij}$ for every fixed threshold
vector $(c_1,\dots,c_N)$. For the equicorrelated covariance (2.1),
$$
  P_{\text{no-fa}}(\rho)
  \;\ge\;
  P_{\text{no-fa}}(0)
  \;=\;
  \Phi(b_c)\,\Phi(b_u)^{N-1}
  \quad\forall\,\rho \in [0,1),
  \tag{3.1}
$$
with strict inequality for $\rho > 0$ at finite thresholds.

*Source.* The general statement is Slepian's monotonicity inequality
[Slepian 1962, *Bell System Tech. J.* 41(2):463–501]; an accessible
modern treatment is Tong, *The Multivariate Normal Distribution* (1990,
§5.1). The equicorrelated form follows by applying the inequality to
each pair-correlation simultaneously. We verified (3.1) numerically on
the rebuilt model's quadrature (2.3) at $\rho \in
\{0,\,0.05,\,0.1,\,0.2,\,0.3,\,0.4,\,0.6,\,0.8\}$ for the headline
sensitivity profile of `Rebuild/sims/A1--rho-channel/` and for a battery
of off-headline cells in the C1 sweep (`Rebuild/sims/C1--cf-distribution/`,
rb-003): monotonicity holds everywhere checked, consistent with
Proposition 3.1.

> **Interpretation.** Positive correlation $\rho > 0$ *relaxes* the
> multiple-comparisons pressure that, in the independent model, forces
> the $N$-fold no-FA product (1.4) toward zero whenever any one
> $\Phi(b_i)$ is less than one. Equivalently: the independent corner
> $\rho = 0$ is the **stiffest-FA-penalty boundary** of the
> equicorrelated family — it *maximises* the aggregate cost of holding
> $N$ false-alarm rates below threshold simultaneously.

### 3.2 Per-policy reward monotonicity

Fix an attention allocation $\alpha$ (hence $d'_c, d'_u$). The change-trial
bracket of (1.3) is $\rho$-independent (it involves only marginal HRs); the
no-change-trial bracket scales linearly in $P_{\text{no-fa}}(\rho)$ with
coefficient $\tfrac{1}{2}\mathrm{CR} \ge 0$. So (3.1) gives, pointwise in
$(c_c, c_u)$,
$$
  \mathbb E[R](\alpha, c_c, c_u; \rho)
  \;\ge\;
  \mathbb E[R](\alpha, c_c, c_u; 0).
$$
Taking the supremum over $(c_c, c_u)$ on both sides preserves the
inequality (a pointwise bound implies the same bound on the sup):
$$
  R^{\star}(\alpha; \rho)
  \;:=\;
  \sup_{c_c, c_u}\,\mathbb E[R](\alpha, c_c, c_u; \rho)
  \;\ge\;
  R^{\star}(\alpha; 0).
  \tag{3.2}
$$

**Corollary 3.2.** Each of the inherited four nested policies P1–P4 has
its supremum reward non-decreasing in $\rho$:
$$
  R(\mathrm P_k; \rho)
  \;=\;
  \sup_{\alpha \in \mathcal A_k, c_c, c_u}\,\mathbb E[R](\alpha, c_c, c_u; \rho)
  \;\ge\;
  R(\mathrm P_k; 0),
  \qquad k \in \{1,2,3,4\},
  \tag{3.3}
$$
since (3.2) holds for *every* $\alpha$ — including the constrained
allocation sets $\mathcal A_k$ defining P2/P3/P4 — and the sup over a
fixed feasible set preserves the inequality.

---

## 4. The sign of $d\mathrm{VDA}/d\rho$ — two competing channels

### 4.1 Why Corollary 3.2 does not pin the VDA sign

The value-directed-attention benefit is, in the rebuilt notation
($\mathrm P1$ = jointly optimised $(\alpha, c_c, c_u)$ at value $v$;
$\mathrm P2$ = $\alpha$ frozen at $\alpha^{\star}(v{=}1)$, criteria
re-optimised),
$$
  \mathrm{VDA}(\rho)
  \;=\;
  R(\mathrm P_1; \rho) - R(\mathrm P_2; \rho).
  \tag{4.1}
$$
Corollary 3.2 says both terms in (4.1) are non-decreasing in $\rho$. It
does **not** say anything about the *difference*; if two non-decreasing
functions differ by a fixed gap, that gap can move either way.

This is the load-bearing observation. The inherited paper's §5.5
sentence "our results therefore represent an upper bound on VDA
benefit" is a sign claim about (4.1), and no derivation of that sign
claim from Corollary 3.2 — or from anything else — exists. The
rebuilt model treats the sign as an empirical (and analytic)
*question*, not a theorem.

### 4.2 Two channels, opposite signs

The two mechanisms that drive $d\mathrm{VDA}/d\rho$ are:

* **Channel (a): criterion devaluation.** Raising $\rho$ inflates
  $P_{\text{no-fa}}(\rho)$ most at liberal criteria — at small $b_i$, where
  $\Phi(b_i)$ is far from $1$ and has room to grow. The no-change-trial
  bracket of (1.3) is therefore flattened across $(c_c, c_u)$, which
  shrinks the *gain* from moving criteria off their floors. Concretely,
  $R(\mathrm P_3) - R(\mathrm P_4)$ — the chunk of reward attributable to
  optimising criteria alone — *falls* relative to $R(\mathrm P_1) -
  R(\mathrm P_4)$. The criterion lever is **devalued**, and the
  criterion fraction
  $\mathrm{CF}(\rho) := \big[R(\mathrm P_3;\rho) - R(\mathrm P_4;\rho)\big]
  / \big[R(\mathrm P_1;\rho) - R(\mathrm P_4;\rho)\big]$
  decreases in $\rho$. (Numerically verified — see §5.)

* **Channel (b): concentration-cost relaxation.** At high $v$ the
  optimal allocation in $\mathrm P_1$ concentrates attention on the cued
  location ($\alpha^{\star} \uparrow$), raising $d'_c$ but **lowering**
  $d'_u$ by the asymmetric transfer of `d_prime_asym`. Lower $d'_u$
  raises $\mathrm{FAR}_u$ — and that increase is compounded over $N - 1$
  uncued locations through the no-FA product (1.4). Under $\rho > 0$
  Proposition 3.1 says that aggregate FA penalty is *relaxed*: the
  $\Phi(b_u)^{N-1}$ factor's drop is dampened by the orthant
  monotonicity. Concentration is therefore *cheaper* under correlation,
  so $\mathrm P_1$ pulls ahead of $\mathrm P_2$ more strongly, and
  $\mathrm{VDA}(\rho) \uparrow$.

Channel (a) acts on the criterion margin; channel (b) acts on the
concentration margin. Their relative magnitudes depend on which lever
is the rate-determining one at the operating point. In the
cost-dominant regime ($r$ small, $\beta(r) \ll 1$ relative to
$\gamma(r)$, see `Rebuild/model/core.py:beta_gamma`) the concentration
lever is suppressed and channel (b) is weak; channel (a) wins,
$d\mathrm{VDA}/d\rho < 0$. In the benefit-dominant regime ($r$ large,
$\beta(r) \gg \gamma(r)$) the concentration lever is the value-encoding
mechanism and channel (b) wins, $d\mathrm{VDA}/d\rho > 0$. There is
therefore a **sign-flip in $r$**, located where the two channels
balance.

### 4.3 The implication for the rebuilt manuscript

The rebuilt model **does not** assert that independence upper-bounds
VDA. What it asserts, derivably:

> **Statement A (CF upper-bound, variant A).** At fixed
> $(N, v, V, d'_{\max}, f_0, h)$ in variant A reward
> ($\mathrm{CR} = Vv + (1-V)$), the criterion fraction $\mathrm{CF}(\rho)$
> is non-increasing in $\rho$ along the empirical envelope spanned by
> `Rebuild/sims/A1--rho-channel/`, with the inherited independent corner
> $\rho = 0$ as its empirical maximiser at every $r$ tested.

> **Statement B (sign-flip in $r$).** The sign of $d\mathrm{VDA}/d\rho$
> is positive throughout the benefit-dominant regime and negative
> throughout the cost-dominant regime, with the sign-flip located in
> the band $r \in [0.38, 0.56]$ at the headline cell $(N, V, v,
> d'_{\max}, f_0, h) = (4, 0.5, 5, 2, 0.5, \sqrt{\cdot})$ (variant A).

Both statements are restricted to the parameter envelope of the
backing simulation; neither is a theorem about an unbounded family.
The empirical bracket is the disciplined version of what §5.5 of the
inherited paper was reaching for.

---

## 5. Numerical realisation at the headline cell

All numbers in this section trace to `Rebuild/sims/A1--rho-channel/`
(rb-002, sha256 `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`),
which evaluates the equations of §1–§3 on the headline cell
$(N, V, v, d'_{\max}, f_0, h) = (4, 0.5, 5, 2, 0.5, \sqrt{\cdot})$ for
$\rho \in \{0, 0.1, 0.2, 0.3, 0.4\}$ on a log-spaced $r$ grid with the
inherited paper's reference points pinned.

### 5.1 Recovery at $\rho = 0$ (Statement of fact)

Single-cell $\mathrm{VDA}$, $\mathrm{CF}$, and $R_{\mathrm P_k}$ at
$r \in \{0.398, 1.0, 3.162\}$ (variant A) match the
`Critique/replications/A1--correlated-fa/` reference numbers with
$\max|\Delta| = 0$ across all reported digits; peak
$\mathrm{VDA}^{\star}(\rho{=}0) = 0.07986$ at $r = 0.3831$ is reproduced
identically. Slepian monotonicity (3.1) holds across $\rho \in
\{0,\,0.05,\,0.1,\,0.2,\,0.3,\,0.4,\,0.6,\,0.8\}$, consistent with
Proposition 3.1.

### 5.2 The pointwise upper-bound on VDA *fails*

| $\rho$ | $\mathrm{VDA}^{\star}$ | $r^{\star}$ | max excess over $\mathrm{VDA}(r;0)$ | first sign-flip $r$ |
|---:|---:|---:|---:|---:|
| 0.0 | 0.07986 | 0.3831 | — | — |
| 0.1 | 0.08110 | 0.3831 | $+4.84\times 10^{-3}$ | $\approx 0.38$ |
| 0.2 | 0.07955 | 0.3831 | $+8.73\times 10^{-3}$ | $\approx 0.42$ |
| 0.3 | 0.07763 | 0.3980 | $+9.83\times 10^{-3}$ | $\approx 0.50$ |
| 0.4 | 0.07368 | 0.3980 | $+1.01\times 10^{-2}$ | $\approx 0.56$ |

The pointwise inequality $\mathrm{VDA}(r;\rho) \le \mathrm{VDA}(r;0)$
fails for every $\rho > 0$; the max excess grows monotonically with
$\rho$. The headline peak $\mathrm{VDA}^{\star}$ is essentially
unchanged at empirically central $\rho \approx 0.2$ (matching the
[[cohen_maunsell2009_correlations]] $r_\mathrm{SC} \approx 0.2$ in
V4), so the C2 magnitude survives; what fails is the *uniform sign*
of the difference. This realises Statement B of §4.3.

### 5.3 The CF upper-bound holds (variant A; flat in variant B)

| $r$     | $\mathrm{CF}(0)$ | $\mathrm{CF}(0.1)$ | $\mathrm{CF}(0.2)$ | $\mathrm{CF}(0.3)$ | $\mathrm{CF}(0.4)$ |
|---:|---:|---:|---:|---:|---:|
| 0.398 | 0.8295 | 0.8181 | 0.8071 | 0.7969 | 0.7875 |
| 1.000 | 0.7282 | 0.7097 | 0.6903 | 0.6698 | 0.6473 |
| 3.162 | 0.6409 | 0.6180 | 0.5936 | 0.5673 | 0.5386 |

CF is monotone-decreasing in $\rho$ at every $r$ tested in variant A,
across both the cost-dominant ($r = 0.398$), symmetric ($r = 1$), and
benefit-dominant ($r = 3.162$) anchors. This is Statement A of §4.3,
and it is exactly the bound the §5.5 sentence of the inherited paper
*should* have stated.

In variant B (no value-scaling on correct rejections,
$\mathrm{CR} = 1$), $\mathrm{CF}(\rho)$ is essentially flat at the
headline cell — the small bumps in rb-002 are not monotone. The rebuilt
manuscript reports the CF upper-bound as a **variant-A result** and
variant B as a sensitivity in which the effect washes out.

The variant-B caveat generalises across the full $4{,}410$-cell C1 sweep
(`Rebuild/sims/C1--cf-distribution/`, rb-003): in variant A, the
cell-wise ordering $\mathrm{CF}(\rho{=}0.2) \le \mathrm{CF}(\rho{=}0)$
holds in $84\%$ of cells (one-sided over the entire sweep, not the
single-cell anchor); in variant B it holds in only $64\%$ of cells
($24\%$ increase, $13\%$ flat). The "independence upper-bounds CF"
statement, then, is best stated at the *median* across the sweep — the
rebuilt manuscript's distributional voice (§3.3 of the mission
prompt). What it cannot be stated as is a uniform inequality.

---

## 6. Scope and limitations

* **Equicorrelation specificity.** The exact 1-D reduction (2.3) is
  specific to equicorrelated $\Sigma$. Structured covariances —
  within-down / between-up sign patterns
  [[ruff_cohen2016_cross_area_correlations]], supra-pairwise
  shared-variance amplification [[srinath2021_attention_information_flow]] —
  break the dimension reduction and require either a multivariate normal
  CDF evaluation or a different factorisation. Because Slepian
  monotonicity (Prop. 3.1) is *pairwise* and a single sign-flipped pair
  is enough to refute a uniform sign claim on the dependence in the
  general case, the empirical sign-flip we exhibit here for the
  equicorrelated family already establishes that no uniform "upper bound
  on VDA" can survive in the broader covariance space. The conservative
  conclusion: the rebuilt model treats $\rho$ as the **first-order**
  correlation parameter and flags structured-covariance extensions as a
  scoped limitation (RB-016/RB-020 if A6 lands; otherwise as
  out-of-scope literature).

* **Magnitude envelope.** The $\rho$ range $[0, 0.4]$ brackets the
  empirically reported $r_\mathrm{SC}$ values in primate V4 change-
  detection. Higher $\rho$ values are extrapolations the rebuilt
  manuscript does not warrant from the data; they remain admissible in
  the model and produce continued monotone CF decrease in variant A but
  are not used to anchor any headline claim.

* **Recovery contract is global.** The $\rho \to 0$ recovery covers all
  downstream rebuild artifacts that consume `p_no_fa_*`. Any future
  model extension that re-implements no-FA computation (e.g. RB-014's
  heterogeneous-$r$ extension, RB-015's conservation family) must pass
  this same contract under its own $\rho = 0$ limit; otherwise it is
  not certified for the rebuilt manuscript.

* **What this derivation does not prove.** A closed-form expression for
  $r^\dagger(v; \rho)$, the analytic location of the VDA peak under
  $\rho > 0$, is queued as RB-026 (it requires substituting the
  $\partial P_{\text{no-fa}}(\rho)/\partial d'_c$ and
  $\partial P_{\text{no-fa}}(\rho)/\partial d'_u$ Gauss–Hermite
  gradients into the §2.3 of the inherited paper's first-order
  condition; the present derivation establishes existence of the
  sign-flip but locates it empirically only). A finer-$\rho$ bracket of
  the sign-flip is queued as RB-023. A cell-wise sign-flip map across
  the full C1 sweep is queued as RB-025.

---

## 7. References

* **Slepian, D. (1962).** "The one-sided barrier problem for Gaussian
  noise." *Bell System Technical Journal* 41(2):463–501. Monotonicity
  of Gaussian orthant probabilities in the correlation entries
  (Proposition 3.1). *No `research_db/` substrate — math-methods gap
  flagged as a candidate stub for a later increment.*
* **Tong, Y.L. (1990).** *The Multivariate Normal Distribution.*
  Springer, §5.1. Modern treatment of Slepian's inequality and the
  equicorrelated specialisation. *No `research_db/` substrate — same
  gap as Slepian 1962.*
* **Cohen, M.R. & Maunsell, J.H.R. (2009).** Attentional improvements
  in performance through reduction of correlated variability in V4.
  [[cohen_maunsell2009_correlations]] — the empirical anchor for the
  $\rho$ range and the motivation for promoting A1 to a tunable model
  parameter. Reports $r_\mathrm{SC} \approx 0.2$ in macaque V4 during
  a peripheral-validity-cue change-detection task; more than $80\%$ of
  attention's behavioural benefit traces to decorrelation in this
  paradigm. Sets the rebuilt model's $\rho \in [0, 0.4]$ envelope.
* **Ruff, D.A. & Cohen, M.R. (2016).** Cross-area correlations and
  attention. [[ruff_cohen2016_cross_area_correlations]] — sign-dependent
  (within-area-down / between-area-up) correlation structure;
  motivates the equicorrelated form as a deliberate simplification
  rather than a literal model of cortical covariance.
* **Srinath, R. et al. (2021).** [[srinath2021_attention_information_flow]] —
  supra-pairwise shared-variance amplification; caps any "single $\rho$"
  patch and motivates the structured-covariance limitation noted in §6.
* `Rebuild/model/core.py` — `p_no_fa_point`, `p_no_fa_grid` implement
  Eq. (2.3); `d_prime_asym`, `beta_gamma` provide the
  $\alpha \to (d'_c, d'_u)$ transfer used in §4.2 channel (b).
* `Rebuild/model/tests/test_recovery.py` — recovery test enforcing
  Eq. (2.4); 7/7 PASS, sha256 `d3c62215…`.
* `Rebuild/sims/A1--rho-channel/` — backing simulation, sha256
  `b692c06456530ccd1b319762d8a948814324d3129f39902ce9531a66d1206614`;
  source of every number in §5.
* `Rebuild/sims/C1--cf-distribution/` — the $4{,}410$-cell sweep
  (rb-003, sha256 `91fc4692…`) used in §5.3 for the cell-wise CF
  ordering generalisation beyond the single headline cell.

---

## Verification performed

* **Recovery (Eq. 2.4)** numerically verified at $\rho = 0$ to
  floating-point identity across all reviewer reference cells; cf. §5.1.
* **Slepian monotonicity (Eq. 3.1)** numerically verified for the
  headline sensitivity profile and across the C1 sweep at $\rho \in
  \{0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8\}$; no violation observed.
* **Per-policy monotonicity (Cor. 3.2)** verified at each P1–P4 reward
  on the rb-002 grid by inspection of the per-$\rho$ supremum reward
  arrays.
* **Sign-flip locus (§4.3 Statement B)** localised to $r \in [0.38, 0.56]$
  at the headline cell and reproduced across $\rho \in [0.1, 0.4]$ —
  rb-002 max excess monotone in $\rho$.
* **Quadrature error** at $n_q = 64$ versus $n_q = 128$ verified
  $\le 10^{-15}$ at all rb-002 evaluation points.

## Extensions to consider

* **RB-023.** Tighter bracketing of the sign-flip $r$ over a finer
  $\rho$ grid (e.g. $\rho \in \{0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2\}$),
  with additional off-headline cells, to determine whether the headline-
  cell sign-flip locus generalises.
* **RB-025.** Cell-wise sign-flip map across the C1 sweep (parallel to
  the cell-wise CF $\Delta$-distribution rb-003 already publishes).
* **RB-026.** Closed-form $r^\dagger(v;\rho)$ — substitute the
  Gauss–Hermite gradients $\partial P_{\text{no-fa}}/\partial d'_c$,
  $\partial P_{\text{no-fa}}/\partial d'_u$ into the §2.3 first-order
  condition of the inherited paper's C2 derivation. This would
  promote Statement B from "empirical sign-flip in $[0.38, 0.56]$"
  to an analytic locus $r^\dagger(v;\rho) - r^\dagger(v;0)$ drift law.
* **Structured covariance.** A scoped extension beyond equicorrelation,
  requiring either a multivariate-normal CDF backend or an alternative
  factorisation. Not in the rebuilt manuscript's current scope.
