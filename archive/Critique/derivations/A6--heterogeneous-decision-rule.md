---
type: derivation
claim_id: A6
title: "Is the homogeneous-decision-rule assumption load-bearing for the criterion-vs-attention decomposition?"
attack_vector: re-derivation
run_id: run-018
prompt_version: "0.2"
date: 2026-05-25
companion_replication: Critique/replications/A6--heterogeneous-decision-rule/
---

# A6 — heterogeneous decision rule across locations

**Task:** CR-011 (folds in CR-055). Re-derive the optimal policy and the
P1–P4 decomposition under a heterogeneous decision rule (location-specific
decision noise), and decide whether the clean *criterion vs attention*
separation — on which the criterion-fraction metric and §5.1's "why
criterion dominates" argument rest — survives.

All notation follows mission §2. $\Phi$ is the standard normal CDF,
$\varphi$ its density. $N$ locations, one cued; allocation $\alpha$ to the
cued, $(1-\alpha)/(N-1)$ to each uncued.

---

## 1. What A6 is, and the two readings the paper bundles

The paper (paper §2.2; mission §2.2) makes every per-location decision with
the **same equal-variance Gaussian SDT machinery**, internal noise
normalised to unit variance:
$$
\mathrm{HR}_i = \Phi\!\left(\tfrac{d'_i}{2} - c_i\right),\qquad
\mathrm{FAR}_i = \Phi\!\left(-\tfrac{d'_i}{2} - c_i\right).
\tag{1}
$$
Only the **free parameters** differ across locations: the sensitivity
$d'_i$ (set by attention via the transfer function $f$ and the $\beta/\gamma$
asymmetry, mission §2.4) and the criterion $c_i$ (chosen by the optimiser;
two groups, cued/uncued, mission §2.5). **A6** is the *unstated* premise
that the transduction itself — the variance of the decision variable, the
functional form of the rate map — is **identical at every location**.

The paper names A6 only obliquely, in the first §5.5 limitation, where it is
*bundled with A1*:

> "First, the model assumes **independent per-location SDT decisions**;
> real observers emit a **single global response**, introducing
> dependencies that could alter the optimal policy. Our results therefore
> represent an upper bound on VDA benefit." (paper §5.5)

Run-017 / CR-052 disentangled the two clauses: the *"independent … product
$P_{\text{no-fa}}=(1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}$"* clause is
**A1** (Booking 1, now CONTESTED — `verdicts/A1--independence.md`), while the
*"single global response"* clause is **A6** (Booking 2, the
decision-architecture reading). This derivation attacks A6 in **two
readings**, in increasing severity:

- **A6-(i) Heterogeneous machinery** (the mission §2.7 reading, the
  literal CR-011 task): the same $N$-decision architecture, but the
  *transduction noise differs by location*, e.g. larger decision noise at
  the (less-attended) uncued locations. This is §§2–4 below.
- **A6-(ii) Single global response** (the §5.5 / CR-055 reading): the
  observer collapses the $N$ decision variables into **one** response
  with **one** criterion, so criterion can no longer be tuned per
  location. This is §5 below; it overlaps A1 and is flagged as the
  designated second vector.

The object under test in both readings is §5.1's load-bearing claim:

> "Criterion adjustment is costless: shifting $c$ at one location has no
> effect on $d'$ at any location. **It can therefore independently encode
> value at each location** without any perceptual tradeoff." (paper §5.1)

and the metric it justifies, the **criterion fraction**
$$
\mathrm{CF} \;=\; \frac{R(\mathrm{P3}) - R(\mathrm{P4})}{R(\mathrm{P1}) - R(\mathrm{P4})}
\tag{2}
$$
(P1 joint optimum; P3 criterion-optimised at uniform attention; P4 floor
$\alpha=1/N,c=0$; mission §2.5).

---

## 2. SDT with location-specific decision noise — setup

Add **late (decision/readout) noise** $\eta_i \sim \mathcal N(0,\sigma_{d,i}^2)$,
independent of the sensory evidence, to the per-location decision variable
$Y_i = X_i + \eta_i$. Under the unit-variance sensory code,
$$
\text{signal: } Y_i \sim \mathcal N(d'_i,\, 1+\sigma_{d,i}^2),\qquad
\text{noise: } Y_i \sim \mathcal N(0,\, 1+\sigma_{d,i}^2).
$$
Write the **effective decision SD**
$$
s_i \;=\; \sqrt{1+\sigma_{d,i}^2}\ \ge 1,\qquad s_i = 1 \iff \sigma_{d,i}=0\ \ (\text{the paper}).
\tag{3}
$$
Reporting "change" when $Y_i$ exceeds a threshold $\lambda_i$, and writing the
criterion in the paper's centred form $c_i = \lambda_i - d'_i/2$, gives
$$
\boxed{\;
\mathrm{HR}_i = \Phi\!\left(\frac{d'_i/2 - c_i}{s_i}\right),\qquad
\mathrm{FAR}_i = \Phi\!\left(\frac{-d'_i/2 - c_i}{s_i}\right).
\;}
\tag{4}
$$
A6-(i) holds iff $s_c = s_u = 1$. Heterogeneous machinery is $s_c \ne s_u$
(canonically $s_u > s_c$: noisier decisions at the less-attended locations).
The reward is mission §2.5 Eq. (9), unchanged, with the rates (4):
$$
\mathbb E[R](\alpha,c_c,c_u) = \tfrac12\!\left[V\,\mathrm{HR}_c\,v + (1-V)\,\mathrm{HR}_u\right]
+ \tfrac12\,(1-\mathrm{FAR}_c)(1-\mathrm{FAR}_u)^{N-1}\,\mathrm{CR}.
\tag{5}
$$

---

## 3. Proposition 1 — fixed heterogeneous noise is *absorbed*: the
##    decomposition is structurally invariant

**Claim.** For any **fixed** $(s_c,s_u)$, the optimal policy and the entire
P1–P4 decomposition are identical to the paper's, with each location's
sensitivity rescaled $d'_i \mapsto \tilde d'_i := d'_i/s_i$. Hence the
criterion fraction's *definition and interpretation* are unchanged; only its
numerical value moves, exactly as it would under a per-location change of
$d'_{\max}$ or $f_0$.

**Proof.** The rate map (4) satisfies the algebraic identity, for every $c_i$,
$$
\Phi\!\left(\frac{d'_i/2 - c_i}{s_i}\right)
= \Phi\!\left(\frac{d'_i/s_i}{2} - \frac{c_i}{s_i}\right)
= \Phi\!\left(\frac{\tilde d'_i}{2} - \tilde c_i\right),
\qquad \tilde d'_i := \frac{d'_i}{s_i},\ \ \tilde c_i := \frac{c_i}{s_i},
\tag{6}
$$
and likewise $\mathrm{FAR}_i = \Phi(-\tilde d'_i/2 - \tilde c_i)$. (Numerically
exact: the companion replication Block 0 verifies (6) pointwise to
$1.1\times10^{-16}$.) Substituting into (5),
$$
\mathbb E[R](\alpha,c_c,c_u;\,s_c,s_u)
= \mathbb E[R]_{\text{paper}}\!\bigl(\alpha,\ \tilde c_c,\ \tilde c_u;\ \tilde d'_c(\alpha),\ \tilde d'_u(\alpha)\bigr),
\tag{7}
$$
i.e. the noisy-machinery reward is the **paper's reward** evaluated at the
rescaled sensitivities and rescaled criteria. The map $c_i \mapsto \tilde c_i = c_i/s_i$
is a **bijection** of $\mathbb R$ (fixed $s_i>0$), and the optimiser searches
over all criteria, so
$$
\max_{c_c,c_u}\mathbb E[R](\alpha,\cdot\,;s)
= \max_{\tilde c_c,\tilde c_u}\mathbb E[R]_{\text{paper}}(\alpha,\cdot\,;\tilde d')
= R^\star_{\text{paper}}\!\bigl(\alpha;\tilde d'(\alpha)\bigr).
\tag{8}
$$
P1 maximises (8) over the *same* $\alpha$-grid; P3 is (8) at $\alpha=1/N$;
P4 is the $c=0$ reward, and $c=0 \Rightarrow \tilde c = 0$ so P4 is likewise
the paper's P4 at $\tilde d'$. Therefore
$$
R(\mathrm{P}k;\,s_c,s_u) = R(\mathrm{P}k)_{\text{paper}}\big|_{d'\to d'/s}\quad (k=1,2,3,4),
\qquad\text{so}\qquad
\mathrm{CF}(s_c,s_u) = \mathrm{CF}_{\text{paper}}\big|_{d'\to d'/s}. \qquad\blacksquare
$$

**Reading.** Fixed heterogeneous decision noise introduces **no new
functional form and no coupling between locations**; it only rescales each
location's *effective* sensitivity. The two control levers are still
$(\alpha;\,c_c,c_u)$, "criterion" is still the costless per-location lever and
"attention" still the zero-sum $d'$-reallocation lever — the §5.1 dichotomy
and the CF definition are intact. A6-(i) is therefore in the **same class as
a secondary-sweep parameter** (a per-location $d'_{\max}/f_0$): it moves the
numbers, never the structure.

*Caveat the paper's derivation would have to flag.* The rescaling is
$d'_i \to d'_i/s_i$, so a location with noisier machinery has *lower effective
sensitivity*. Because the uncued sensitivity already differs from the cued
(via $\beta/\gamma$ and the $(1-\alpha)/(N-1)$ split), a fixed $s_u>s_c$ simply
deepens that asymmetry; the companion replication finds CF rises modestly
(e.g. $0.728\to0.789$ at $s_u=2$, $V{=}0.5,v{=}5,r{=}1$). This is benign for
the headline claims but is *not nothing*: it means the reported CF range is
conditional on the (unstated) premise of equal machinery, and a referee can
ask how $s_u/s_c$ in a real preparation would shift it. Verdict-relevant but
not decomposition-breaking.

---

## 4. Proposition 2 — *attention-coupled* noise is a third lever: the
##    criterion fraction stops being a clean criterion-vs-attention split

Prop 1 used $s_i$ **constant in $\alpha$**. That is exactly the premise that
fails empirically: attention does not only multiply sensitivity — it reduces
decision/readout variability and interneuronal noise correlations
(`cohen_maunsell2009_correlations`; Mitchell, Sundberg & Reynolds 2009;
`luo_maunsell2018_criterion_sensitivity` shows criterion and sensitivity are
*dissociable* substrates of attention). Model this as $s_i = s(a_i)$ with
$s'<0$ (more attention $\Rightarrow$ less decision noise). Then **moving
$\alpha$ changes the effective sensitivity through two channels**:
$$
\frac{\partial}{\partial\alpha}\,\tilde d'_c(\alpha)
= \frac{\partial}{\partial\alpha}\frac{d'_c(\alpha)}{s_c(\alpha)}
= \underbrace{\frac{d'^{\,\prime}_c(\alpha)}{s_c}}_{\text{(I) sensitivity gain via } f}
\;-\;\underbrace{\frac{d'_c(\alpha)\,s'_c(\alpha)}{s_c^2}}_{\text{(II) noise reduction, } \ge 0 \text{ if } s'<0}.
\tag{9}
$$
By the chain rule the marginal reward gradient inherits both:
$$
\frac{\partial \mathbb E[R]}{\partial \alpha}
\;\supset\;
\frac{\partial \mathbb E[R]}{\partial \tilde d'_c}\,
\Bigl[\underbrace{d'^{\,\prime}_c/s_c}_{\text{(I)}} \;-\; \underbrace{d'_c\,s'_c/s_c^2}_{\text{(II)}}\Bigr]
\;+\;(\text{uncued terms}).
\tag{10}
$$

**Consequence for the decomposition.** The criterion fraction (2) books the
increment $R(\mathrm{P1})-R(\mathrm{P3})$ — the reward bought by *moving
$\alpha$ off uniform* — entirely to "attention." Under (10) that increment
now bundles **two mechanisms**: (I) the spatial reallocation of sensitivity
the paper means by "attention," and (II) an **attention-modulated reduction
of decision noise** that is *neither* criterion *nor* spatial reallocation.
The metric still returns a number, but it no longer partitions value-encoding
into the two mechanisms §5.1 claims to separate — channel (II) is silently
absorbed into "attention's share."

**Direction and magnitude (companion replication Block 2).** With the
illustrative one-parameter coupling
$$
s_i(a_i) = \sqrt{1 + \kappa\,(1 - h(a_i))},\qquad \kappa\ge 0,\quad \kappa=0\ \text{= paper},
\tag{11}
$$
(decision noise maximal at $a_i\to0$, no excess at $a_i\to1$) at the headline
cell $V{=}0.5,v{=}5,N{=}4,r{=}1,\sqrt{\cdot}$:

| $\kappa$ | CF | total gain $R(\mathrm{P1}){-}R(\mathrm{P4})$ | VDA $=R(\mathrm{P1}){-}R(\mathrm{P2})$ |
|---|---|---|---|
| 0.00 | 0.728 | 0.621 | 0.0398 |
| 0.25 | 0.692 | 0.675 | 0.0247 |
| 0.50 | 0.667 | 0.718 | 0.0064 |
| 1.00 | **0.626** (wide-grid) | 0.781 | 0.0000 |

CF **deflates** by $\approx0.10$ as $\kappa:0\to1$ while the total achievable
gain *grows* (0.62→0.78): attention buys more than the paper credits, so the
criterion's share shrinks. The *interpretive* crack (channel II is mis-booked)
holds for any $s'<0$; the *magnitude* depends on $\kappa$ and the coupling
form. The sign matches the A1 finding (`verdicts/A1--independence.md` V0.2:
CF fell as the false-alarm correlation $\rho$ rose) and the CR-055 prediction.
Secondary: the C2 VDA peak collapses ($0.0797@r{=}0.398 \to 0.0013@r{=}0.100$)
— attention-coupled noise makes concentration so cheap that the value-blind
P2 already saturates $\alpha\to1$, the same "no room for VDA" mechanism the
paper invokes at high $r$ (paper §4.3), now triggered by the noise channel.

---

## 5. The §5.5 reading — single global response (A6-(ii)): the analytic
##    skeleton (designated second vector)

The §5.5 phrase *"real observers emit a single global response"* is the more
severe relaxation. Operationalise its cleanest, A6-isolating form: the
observer still computes per-location evidence but is constrained to a
**single global criterion** $c_c = c_u = c$ (one response threshold), rather
than the paper's two-group $c_c \ne c_u$.

This attacks §5.1 head-on. §5.1's load-bearing sentence is that criterion
*"can independently encode value at each location."* Under a single global
criterion it **cannot**: lowering $c$ to harvest hits at the high-value cued
location simultaneously raises false alarms at the $N-1$ uncued locations
(each entering $P_{\text{no-fa}}$ with exponent $N-1$). The per-location
costlessness that makes criterion the dominant value-encoder is exactly the
degree of freedom the single-global-response observer loses.

**Analytic prediction (sign).** Write the criterion gain at uniform attention
$G_{\text{crit}} = R(\mathrm{P3}) - R(\mathrm{P4})$. With two free criteria the
P3 optimiser solves $\partial_{c_c}\mathbb E[R]=\partial_{c_u}\mathbb E[R]=0$
independently; the cued criterion can move to exploit $v$ without paying the
uncued FA cost. Constraining $c_c=c_u=c$ restricts the feasible set, so the
constrained optimum cannot exceed the free optimum:
$$
G_{\text{crit}}^{\,\text{global-}c} \;\le\; G_{\text{crit}}^{\,\text{per-loc}},
\qquad\text{with equality iff the unconstrained optimum already has } c_c^\star=c_u^\star.
\tag{12}
$$
The unconstrained optimum has $c_c^\star \ne c_u^\star$ whenever $v>1$ and
$V\neq 1/N$ (the cued location is worth more *and* more likely to change), so
the inequality is **strict** in precisely the regime where VDA matters. Hence
the numerator of CF falls. The denominator $R(\mathrm{P1})-R(\mathrm{P4})$
also falls (P1 loses the same DOF), but the criterion channel loses its
*defining* advantage (per-location value encoding), so on the §5.1 logic the
**criterion fraction should compound downward** — the CR-055 prediction, and
the same direction as Prop 2 and the A1-$\rho$ result. Quantifying (12) across
the grid is a bounded replication (constrain $c_c=c_u$ in the C1 optimiser and
re-run) and is the **designated A6 second vector** (CR-056).

**Overlap with A1.** A fuller "single global response" — one pooled decision
variable (e.g. a max- or sum-statistic over locations) — also dissolves the
Eq. (9) $P_{\text{no-fa}}$ *product*, which is precisely the A1 locus
(`verdicts/A1--independence.md`). So the §5.5 sentence's two clauses are not
independent: the global-response architecture implies *both* correlated
false alarms (A1) *and* a shared criterion (A6-(ii)). The clean separation is
that **A1 governs the FA-aggregation** (a product → an orthant probability)
while **A6-(ii) governs the criterion degrees of freedom** (two → one). This
derivation isolates the A6-(ii) DOF effect; the A1 FA-aggregation effect is
already CONTESTED.

---

## 6. What the re-derivation establishes

1. **A6-(i) fixed heterogeneous machinery is benign** (Prop 1, proved
   exactly and confirmed numerically to grid resolution): it is a
   reparametrisation $d'_i\to d'_i/s_i$; the P1–P4 decomposition and the CF
   definition are structurally invariant. Within the paper's stated model
   ($s\equiv1$), nothing breaks.
2. **The clean criterion-vs-attention interpretation is conditional on two
   premises the paper does not state and §5.5 itself flags as false:**
   (a) attention acts *only* on $d'$, not on decision noise (else Prop 2:
   "attention" becomes a compound lever and CF deflates $\approx0.10$); and
   (b) the criterion is *per-location*, not a single global response (else
   §5, ineq. (12): the §5.1 "independently encode value at each location"
   advantage is lost and CF compounds downward).
3. **No headline number shifts *within the paper's stated model.*** Both
   cracks require a model extension (a decision-noise channel; a global
   criterion) beyond what the paper computes. So A6 is a **scope/conditional**
   issue, not an internal error — paralleling A2 (run-014) and A1's first
   touch (run-016): the premise is shown vulnerable, not yet consequential
   within scope.

**Verdict implication.** First touch, one attack vector (re-derivation, with
numerical corroboration). Per mission §6 no elevation to CONFIRMED-* on a
single vector; per §3.1 the literal A6-(i) relaxation *failed to break* the
decomposition (a confirming result) ⇒ **WEAKLY-SUPPORTED**, with the
designated second vector specified (CR-056, the single-global-criterion
replication, which can settle CONFIRMED-CONDITIONAL vs CONTESTED).

---

## 7. Loose ends (→ backlog)

- **CR-056** (A6 second vector, replication): constrain $c_c=c_u$ in the C1
  criterion-fraction optimiser, re-run the 4,410-cell grid, and measure the
  CF deflation predicted by ineq. (12). Settles the A6 label.
- **CR-057** (A6 literature): is the decision-noise/criterion lever both
  attention- *and* value-modulated? `luo_maunsell2018` (dissociable criterion
  vs sensitivity), Cohen–Maunsell decorrelation as the empirical $s(\alpha)$;
  overlaps CR-053 (the A1 value×correlation gap).
- **Coupling form for Prop 2.** Replace the illustrative (11) with a
  literature-grounded $s(\alpha)$ (e.g. calibrated to the Cohen–Maunsell
  $\sim$80% correlation-reduction benefit) to pin the CF-deflation magnitude.
- **A6-(ii) ∩ A1.** A pooled-statistic global decision rule couples A6-(ii)
  to A1's $P_{\text{no-fa}}$ relaxation; a joint re-derivation would quantify
  the combined effect on CF (both push it down).
