---
type: notes
sub_type: sensitivity-probe
claim_id: C2
run_id: run-002
last_updated: 2026-05-17
---

# Sensitivity probe — notes & caveats

## 1. Sign-error correction relative to bootstrap-001 derivation

The CR-001 derivation §2.3 stated the gradient

$$
\left.\frac{\partial E[R]}{\partial \alpha}\right|_{1/N^+}
   = d'_{\max}\,f'(1/N)\,\Bigl[\,G_c(v)\,\beta(r) \;-\; G_u\,\tfrac{\gamma(r)}{N-1}\,\Bigr]
$$

with $G_c, G_u > 0$. The verbal expansion in §2.3 wrote $G_c$ and
$G_u$ as the *signed* contributions of each term in $E[R]$, which
can be misread (and was misread on the first translation of the
derivation into code) as having a *minus sign* between the
hit-rate and no-FA-survival contributions. The correct algebra is
that *both* the hit-rate term and the no-FA-survival term are
*positive* contributions to $\partial R/\partial d'_x$:

$$
\frac{\partial R}{\partial d'_c}
   = \tfrac{1}{4} V v\,\varphi\!\bigl(\tfrac{d'_b}{2} - c_c\bigr)
   + \tfrac{1}{4}\mathrm{CR}\,\varphi\!\bigl(-\tfrac{d'_b}{2} - c_c\bigr)\,
       \bigl(1-\Phi(-\tfrac{d'_b}{2} - c_u)\bigr)^{N-1}
$$

(raising $d'_c$ both increases the cued hit rate and decreases the
cued false-alarm rate, hence helps the no-FA product). Same for
$\partial R/\partial d'_u$ (both terms positive). The minus sign in
the $\alpha$-gradient comes from the *Jacobian*
$\partial d'_u/\partial \alpha|_{1/N^+} = -\gamma d'_{\max} f'(1/N)/(N-1)$,
not from $G_u$.

Once the python implementation in `run.py:G_coefs(...)` used the
correct sum-of-positives convention, $G_c, G_u > 0$ for all 10
secondary-sweep combinations and $r^\dagger(v) > 0$ as expected.

The derivation file `Critique/derivations/C2--non-monotonic-vda.md`
§2.3 should be re-checked at next revision to ensure the verbal
expansion in equation (2.3) cannot be misread as having internal
subtractions. (The agent's policy is to not modify previously-
written verdict / derivation files arbitrarily, so I am noting
the clarification here rather than editing the derivation file in
place; flagged as a candidate improvement task.)

## 2. The closed-form is the *non-clamping* escape threshold

The closed-form $r^\dagger(v) = G_u/[(N-1)G_c(v)]$ derives from the
**infinitesimal-deviation** gradient at $\alpha = 1/N^+$. It tells
us when moving $\alpha$ slightly above $1/N$ improves $E[R]$. In
regimes where the global optimum is far from $1/N$ (e.g.
$\alpha^\star = 1.0$) *and* the $d'$ clamp is active ($d'_u = 0$
at large $\alpha$), the marginal-deviation argument no longer
predicts the global optimum, because the clamp *bounds* the cost
of large-$\alpha$ deviations.

Concretely, at $f_0 = 0.1$ ($N=4, V=0.5, v=5, h=\sqrt{\cdot}$):
$d'_{\text{base}} = 1.10$, and at $\alpha = 1$ the uncued
$d'_u = d'_{\text{base}} + \gamma(d'_{\max} f(0) - d'_{\text{base}}) = 1.10 + \gamma \cdot (0.2 - 1.1) = 1.10 - 0.9\gamma$.
This goes negative when $\gamma > 1.22$, i.e. $r < 0.64$. In that
regime the clamp $d'_u \geq 0$ activates: the cost of
$\alpha = 1$ saturates at "all uncued $d' = 0$" and stops getting
worse as $r$ decreases. Result: even at $r = 0.01$ (extremely
cost-dominant in the no-clamp sense), the empirical
$\alpha^\star_{\mathrm{P1}} = 1.0$ — the bounded cost is overcome
by even tiny cued reward improvements.

This is *not* a failure of the analytic skeleton. It is a refinement
that surfaces when the model's $d'$-clamping (mission §2.4 "All
$d'$ values clamped at $\geq 0$") activates. A future derivation
task (CR-017) could extend $r^\dagger(v)$ to include the
clamping correction.

## 3. The N=2 edge — V = 1/N is degenerate

The model is informationally symmetric at $V = 1/N$ (cued and
uncued locations have equal change-trial probability). For $N=2$,
$V = 0.5 = 1/N$, so the paper's reference regime $(V=0.5, v=5)$ at
$N=2$ is *at* the boundary. The validity gradient that drives
$\alpha^\star \geq 1/N$ (mission §2.4 "for $\alpha < 1/N$, the
roles reverse") vanishes; any $\alpha$ giving the same $d'_c$ and
$d'_u$ pair (e.g. $\alpha = 0.02$ and $\alpha = 0.98$) is
equivalently optimal.

The optimizer picks one of the symmetric optima. At high $r$ the
optimizer for P2 (which uses $\alpha^\star(v=1)$) tends to pick
$\alpha = 0.02$ — i.e. attention *inverted* away from the "cued"
location. This is not a refutation of C4 ($\alpha^\star \geq 1/N$
never below) because at $V = 1/N$ exactly the labelling of "cued"
is meaningless. The paper's primary sweep uses $V \in [0.25, 1.0]$
which for $N=2$ includes $V = 0.25 < 1/N$ — a region that is
*literally meaningless* for $N=2$ (validity below $1/N$ means the
"cued" location is *less* likely than uniform). The paper's
Figure 6 right panel almost certainly includes this boundary
behavior.

When CR-004 (C4 re-derivation) is taken on, this should be noted:
the categorical "no inversion" claim implicitly requires $V > 1/N$,
not just $V \geq 1/N$. At $V = 1/N$ the claim becomes vacuous
(inversion is permitted by the symmetry of the problem).

## 4. Resolution choices

- $\alpha$ grid: 0.01 (vs paper's 0.005). Coarser. Effect on peak
  $r$ estimation is *not* fatal because the $r$-grid resolution
  dominates: the $r$-grid steps are factor-of-1.26 ≈ 0.1-decade
  apart, while the $\alpha$ grid steps would only change peak r
  if there's a P2 escape between grid points — which is the
  $f_0=0.1$ and $h=a^2$ behaviour where the empirical peak hugs the
  P2-escape boundary.
- $c$ grid: 0.05 over $[-3.0, 3.5]$. Extended upward from the
  bootstrap-001 range $[-2.5, 2.5]$ because low-$f_0$ regimes have
  $c_u^\star \approx 2.5$ at the grid boundary. The extension
  resolved the boundary; no further changes needed at this
  $V, v, N$ regime.
- $r$ grid: 31 log-spaced points in $[10^{-2}, 10^1]$. Extended
  downward from the bootstrap-001 range $[10^{-1}, 10^1]$ because
  the closed-form predicts $r^\dagger(v=5) < 0.02$ for $f_0=0.1$
  and $h=a^2$.

The script runs in roughly 15–20 seconds on the sandbox; no scipy
is required (Phi/phi via `math.erf`).

## 5. Verdict-shaping observations

- **Two attack vectors on C2 have failed to falsify.** CR-001
  (re-derivation) and CR-014 (sensitivity probe) both confirm
  C2. The CR-014 probe goes beyond CR-001 by deriving the
  *direction* of every parameter dependence in §4.6 from the same
  analytic expression — strengthening the inference from "the
  paper's claim survives a re-derivation at one regime" to "the
  paper's claim is a property of the model's analytic
  structure across the entire secondary-sweep grid".

- **One subsidiary §4.6 claim weakens.** Peak VDA is non-monotonic
  in $f_0$ (max around $f_0=0.3$, not at $f_0=0.1$). The
  experimental-design recommendation in §5.2 ("low $f_0$") still
  holds in the comparative sense (lower $f_0$ in $\{0.3, 0.5,
  0.7\}$ gives higher VDA), but the unqualified "lower $f_0$ →
  higher VDA" wording in §4.6 should be restricted to "moderately
  low $f_0$".

- **Two refinement tasks spawn**: CR-017 (extend $r^\dagger$ to the
  clamping regime), CR-018 ($f_0$-VDA literature attack). One
  follow-up on C4: CR-019 (no-inversion claim at $V = 1/N$).
