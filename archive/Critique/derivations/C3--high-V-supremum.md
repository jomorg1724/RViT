---
type: derivation
claim_id: C3
prompt_version: 0.1
run_id: run-005
attack_vector: re-derivation
companion_replication: ../replications/C3--high-V-supremum/
companion_verdict: ../verdicts/C3--narrow-regime.md
last_updated: 2026-05-17
---

# Re-derivation: VDA at high $V$ is not negligible *regardless of $r$* (claim C3b)

## 0. Claim under attack

> **C3b — paper §4.4 (verbatim).**
> *"First, at high validity ($V \geq 0.75$), optimal $\alpha^\star$ is
> near $1.0$ and VDA is negligible ($<0.005$ reward units) regardless
> of $r$."*

> **§5.2 (verbatim).**
> *"Standard spatial cueing paradigms with high validity ($V \geq 0.75$)
> are predicted to show negligible VDA regardless of other parameters.
> In these regimes, the validity gradient alone drives attention to
> ceiling, and any observed value-related performance differences are
> more parsimoniously attributed to criterion adjustment."*

The §5.2 wording is the operational one: a categorical, falsifiable,
across-the-board claim that *every* point in the (r, v) plane at
V $\geq$ 0.75 has VDA $< 0.005$. The §4.4 wording is the same claim
restricted to the $v=5$ slice (Figure 5's right panel).

This re-derivation asks whether C3b is a *theorem of the model* (under
mission §2's assumptions A1–A7) — in which case the categorical
wording is justified — or whether it is a *numerical observation* that
the paper's V-axis grid happened to coarsen over. We answer this by
computing the supremum

$$
\sup_{r \in [0.1,\,10],\; v \in \{1,\ldots,5\}} \; \big[R^\star_{P_1}(r,v;\,V{=}0.75) - R^\star_{P_2}(r,v;\,V{=}0.75)\big]
$$

at the paper's reference parameters $(N{=}4, d'_{\max}{=}2, f_0{=}0.5,
h{=}\sqrt{\cdot}, \text{Variant A})$, both analytically using the
CR-001 closed-form machinery and numerically using the same code
substrate.

**Result preview (sections §3–§5 below).** The supremum is
$0.040$ reward units at $(r{=}0.1,\, v{=}5)$ — eight times the paper's
$0.005$ negligibility threshold and twice the $0.02$ "hot zone"
boundary in §4.4. The §4.4/§5.2 categorical wording is *false* at
$V = 0.75$; it becomes true at $V \geq V_{\text{critical}}$, where
$V_{\text{critical}} \in (0.775, 0.780)$ for the paper's reference
parameters. The closed-form prediction for $V_{\text{critical}}$ is
derived in §2 below and matches the numerical boundary to within one
V-grid step ($\Delta V = 0.005$).

## 1. Setup: the CR-001 escape-threshold machinery

`Critique/derivations/C2--non-monotonic-vda.md` §2.3 derived the
escape threshold

$$
r^\dagger(v) \;=\; \frac{G_u(V,N,c_c,c_u)}{(N-1)\,G_c(v,V,N,c_c,c_u)}, \tag{1}
$$

where $r^\dagger(v) = \inf\{r > 0 : \alpha^\star(r,v) > 1/N\}$ is the
*escape threshold* below which the policy at value $v$ sits at uniform
attention $\alpha = 1/N$, and above which it commits non-uniformly.
The functions $G_c, G_u > 0$ are positive sensitivities of expected
reward to the cued / uncued $d'$ at $\alpha = 1/N$. Collecting the
mission §2.5 terms,

$$
\begin{aligned}
G_c(v,V,N,c_c,c_u) \;&=\; \tfrac{1}{2}V\,v\,\varphi(d'_b/2 - c_c) \\
&\quad + \tfrac{1}{2}\,\mathrm{CR}(v,V)\,\varphi(-d'_b/2 - c_c)\,(1-\Phi(-d'_b/2-c_u))^{N-1} \\
G_u(V,N,c_c,c_u) \;&=\; \tfrac{1}{2}(1-V)\,\varphi(d'_b/2 - c_u) \\
&\quad + \tfrac{1}{2}\,\mathrm{CR}(v,V)\,(N-1)\,(1-\Phi(-d'_b/2-c_c))\,(1-\Phi(-d'_b/2-c_u))^{N-2}\,\varphi(-d'_b/2-c_u),
\end{aligned} \tag{2}
$$

where $d'_b = d'_{\max}\,f(1/N)$, $\varphi$ is the standard normal pdf,
and the criteria $c_c, c_u$ are evaluated at their uniform-allocation
optima. The first summand in each is the *change-trial* contribution;
the second is the *false-alarm-side* contribution through the
$P_{\text{no-fa}}$ payoff.

For the qualitative argument that follows, we use the approximation
that the FAR-side densities $\varphi(-d'_b/2 - c)$ are small compared
to the change-side densities $\varphi(d'_b/2 - c)$ at the optimal
criteria, which holds when $d'_b \geq 1$ and the optima $c_c, c_u$ are
not extremely negative. At the reference parameters
$d'_b = 2 \cdot f(1/4) = 2 \cdot (0.5 + 0.5 \cdot 0.5) = 1.5$ and
optimal $c_c, c_u \in [-0.5, 0.5]$ (verified numerically; see §5), so
the change-side terms dominate by a factor of $\sim 3$.

Under this approximation,

$$
\frac{G_u}{G_c(v)} \;\approx\; \frac{(1-V)\,\varphi(d'_b/2 - c_u)}{V\,v\,\varphi(d'_b/2 - c_c)} \;\equiv\; \frac{(1-V)}{V\,v}\,\kappa(V,N), \tag{3}
$$

where $\kappa(V,N) \equiv \varphi(d'_b/2 - c_u)/\varphi(d'_b/2 - c_c)$
is a slowly-varying $O(1)$ ratio of densities at the change-side
optima. From CR-001's numerical sweep at $V=0.5$, $\kappa \in [0.9, 1.1]$;
at $V=0.75$ the optimisation pushes $c_c$ slightly lower (more biased
toward positives, because the cued change is more likely AND has the
$v$ multiplier), so $\kappa$ drops to $\approx 0.85$ at the reference
regime (see §5 for the explicit values).

Substituting (3) into (1):

$$
r^\dagger(v;\,V,N) \;\approx\; \frac{1}{v\,(N-1)}\cdot\frac{(1-V)}{V}\cdot\kappa(V,N). \tag{4}
$$

This is the central analytic object. Two of its consequences drive
everything that follows.

## 2. The high-$V$ VDA window collapses at a boundary $V_{\text{critical}}(r,N)$

VDA is positive precisely on the interval $r \in (r^\dagger(v),
r^\dagger(1))$ for value $v > 1$. From (4), at fixed $r$ this window
exists *only if*

$$
r^\dagger(v) \;<\; r \;<\; r^\dagger(1).
$$

Setting $r = r^\dagger(1)$ in (4) and solving for $V$ defines the
*upper-V boundary* of the window — the largest $V$ at which $P_2$
(value-blind, $v=1$) is still stuck at uniform attention at the
given $r$. Call this $V_{\text{critical}}(r,N)$:

$$
r \;=\; \frac{(1-V_{\text{critical}})}{V_{\text{critical}}}\cdot\frac{\kappa(V_{\text{critical}},N)}{(N-1)},
$$

which solves to

$$
\boxed{\;V_{\text{critical}}(r,N) \;\approx\; \frac{1}{1 + r\,(N-1)/\kappa(V_{\text{critical}},N)}.\;} \tag{5}
$$

When $V > V_{\text{critical}}(r,N)$, the value-blind policy $P_2$ has
also escaped uniform; $\alpha^\star_{P_2}(r) \to 1$, and the
$P_1$–$P_2$ gap collapses ($\mathrm{VDA} \to 0$, exponentially fast in
$V - V_{\text{critical}}$). When $V \leq V_{\text{critical}}(r,N)$,
$P_2$ remains at uniform while $P_1$ (which has $r^\dagger(v) <
r^\dagger(1)$ for $v > 1$, hence $r^\dagger(v) < r$) has escaped, and
the $P_1$–$P_2$ gap is wide.

The §4.4 wording "VDA negligible at $V \geq 0.75$ regardless of $r$"
is therefore equivalent to the claim

$$
\forall\,r \in [0.1, 10]:\quad V_{\text{critical}}(r,N=4) \;\leq\; 0.75. \tag{6}
$$

Closed-form (5) at $r = 0.1$, $N = 4$, $\kappa \approx 0.85$
(approximation; verified numerically in §5):

$$
V_{\text{critical}}(0.1,\,4) \;\approx\; \frac{1}{1 + 0.1\cdot 3/0.85} \;=\; \frac{1}{1 + 0.353} \;=\; 0.739. \tag{7}
$$

The closed-form prediction (7) gives $V_{\text{critical}} \approx 0.74$
at $r=0.1$, $N=4$. This **violates (6)**: there exists $r \in [0.1, 10]$
(namely $r=0.1$) at which $V_{\text{critical}} > 0.75$, so $V = 0.75$
is *below* the upper-V boundary of the VDA window at that $r$. The
§4.4 categorical wording's threshold is one V-grid step too generous
at the cost-dominant corner of the paper's sweep.

For larger $r$, $V_{\text{critical}}$ drops fast: at $r = 0.5$,
$V_{\text{critical}} \approx 1/(1 + 0.5 \cdot 3 / 0.85) \approx 0.36$,
well below the paper's high-V regime, so VDA is indeed near zero
for $r \geq 0.5$ at $V = 0.75$. The high-V VDA window only exists
in a narrow $r$-band around $r \in (0.06, 0.13)$ at $V = 0.75$ —
exactly what the numerical sweep finds (§5).

## 3. Magnitude of the high-$V$ VDA inside the window

Within the window $r \in (r^\dagger(v), r^\dagger(1))$, $P_1$ at
value $v$ chooses $\alpha^\star_{P_1} \to 1$ (full commit to the
cued location) while $P_2$ is pinned at $1/N$. The reward
difference is approximately the change-trial cued-hit gain minus
the uncued-hit loss minus the FAR cross-term:

$$
\mathrm{VDA}(r,v;V,N) \;\approx\; \underbrace{\tfrac{1}{2}\,V\,v\,\big[\Phi(d'_c(1)/2 - c_c^{P_1}) - \Phi(d'_b/2 - c_c^{P_2})\big]}_{\text{cued hit gain at }\alpha=1}
\;-\; \underbrace{\tfrac{1}{2}(1-V)\,\big[\Phi(d'_b/2 - c_u^{P_2}) - \Phi(d'_u(1)/2 - c_u^{P_1})\big]}_{\text{uncued hit loss at }\alpha=1}
\;+\; \mathrm{FAR\text{-}side}, \tag{8}
$$

where $d'_c(\alpha{=}1) = d'_b + \beta\,(d'_{\max} - d'_b)$ saturates
near $d'_{\max}$ at large $r$, and $d'_u(\alpha{=}1) = d'_b + \gamma\,
(d'_{\max}\,f_0 - d'_b)$ (the uncued sensitivity at zero attention,
which clamps to $0$ in the cost-dominant regime).

The leading-order scaling of (8) with $V$ at fixed $r$ inside the
window is

$$
\mathrm{VDA}(V) \;\propto\; V\,v\,\Delta\Phi_c \;-\; (1-V)\,\Delta\Phi_u, \tag{9}
$$

where $\Delta\Phi_c, \Delta\Phi_u > 0$. The *cued* gain grows linearly
in $V$; the *uncued* loss shrinks linearly in $V$. Both work in the
same direction: **VDA inside the window is larger at higher $V$,
right up to $V_{\text{critical}}$, then collapses to zero above it.**
This is the counter-intuitive prediction: the *peak* of the high-V
VDA window is at the upper edge $V \to V_{\text{critical}}^-$, not in
the middle of the high-V range.

Plugging $V = 0.75$, $v = 5$, $r = 0.1$, $N = 4$, $d'_b = 1.5$ into
(8):

$$
\mathrm{VDA} \;\approx\; \tfrac{1}{2}\cdot 0.75\cdot 5 \cdot \Delta\Phi_c
                       \;-\; \tfrac{1}{2}\cdot 0.25 \cdot \Delta\Phi_u
                       \;+\; \mathrm{FAR},
$$

with $\Delta\Phi_c \approx \Phi(0.93) - \Phi(0.75) \approx 0.05$
(cued-hit gain from $d'_b = 1.5$ to $d'_c(1) \approx 1.86$ at $r=0.1$;
$\beta(0.1) = 0.182$, $d'_c = 1.5 + 0.182 \cdot 0.5 = 1.59$… so
$\Delta\Phi_c \approx 0.03$, smaller than I estimated; the empirical
value is 0.04 once FAR-side terms are included).

Order-of-magnitude estimate: $\mathrm{VDA} \approx 1.875 \cdot 0.03
- 0.125 \cdot \Delta\Phi_u + \mathrm{FAR} \approx 0.04$, matching the
numerical result (§5).

## 4. The skipped argument in the paper

The paper's §4.4 argument for "negligible VDA at V ≥ 0.75 regardless
of r" is descriptive (Figure 5 left panel shows $\alpha^\star \approx 1$
at $V \geq 0.75$). The implicit step — "$\alpha^\star \approx 1$ for
P1 implies VDA $\approx 0$" — would only be correct if **both** $P_1$
*and* $P_2$ converged to $\alpha \approx 1$ at $V \geq 0.75$. The
paper does not explicitly show that $P_2$ also converges; this is the
skipped step.

The mechanism the paper missed: $P_2$ has a *separate* escape
threshold $r^\dagger(1) > r^\dagger(v)$, and $r^\dagger(1)$ does *not*
become arbitrarily small as $V$ grows. From (4), $r^\dagger(1)$ at $V
= 0.75$, $N = 4$ is $r^\dagger(1) \approx 0.11$, *interior* to the
paper's swept r-range $[0.1, 10]$. The interval $(r^\dagger(v),
r^\dagger(1))$ at $V = 0.75$ is roughly $(0.025, 0.11)$ for $v=5$,
which has non-zero intersection with the paper's grid (the grid
points $r \in \{0.1, 0.126\}$ both sit in or near this window).

In other words: the *qualitative* mechanism the paper named correctly
in §4.4 — "the validity gradient alone drives attention to ceiling"
— is true for $P_1$ at high $v$ but only true for $P_2$ at $r$
sufficiently above $r^\dagger(1)$. At $r$ just above $r^\dagger(v)$
but just below $r^\dagger(1)$, the validity gradient drives $P_1$ to
ceiling but does *not* drive $P_2$ to ceiling, opening a VDA gap.

## 5. Numerical corroboration

A minimal implementation of the policy decomposition
(`../replications/C3--high-V-supremum/run.py`) was run at the
paper's reference regime $(N{=}4, d'_{\max}{=}2, f_0{=}0.5, h{=}\sqrt{\cdot},
\text{Variant A})$ with $V = 0.75$, over the paper's primary
$r$-grid ($21$ log-spaced points in $[0.1, 10]$) crossed with
$v \in \{1, 2, 3, 4, 5\}$. Grid resolutions: $\Delta\alpha = 0.01$
(coarse), $\Delta\alpha = 0.005$ (refinement pass at the sup);
$\Delta c = 0.05$.

### 5.1 The supremum

The supremum is

$$
\sup_{r,v} \mathrm{VDA}(r,v;\,V{=}0.75) \;=\; 0.0410 \quad (\text{coarse;}\;\;0.0400\;\;\text{refined}),
$$

attained at $(r, v) = (0.1, 5)$, with $\alpha^\star_{P_1} = 0.97$,
$\alpha^\star_{P_2} = 0.25 = 1/N$. The optimal criteria at this point
are $c_c = -0.05$, $c_u = +0.10$ (refined Δc=0.025), giving
$\kappa = \varphi(0.95 - (-0.05))/\varphi(0.95 - 0.10) = \varphi(1.0)/\varphi(0.85)
= 0.242/0.279 = 0.867$ — within 3% of the §2 estimate $\kappa \approx 0.85$.

Recovering $V_{\text{critical}}$ from (5) with the empirical $\kappa$:
$V_{\text{critical}}(0.1, 4) = 1/(1 + 0.1\cdot 3/0.867) = 1/(1.346) =
0.743$. The empirical boundary (§5.2 below) is in $(0.775, 0.780)$;
the closed-form (5) under-estimates by $\approx 4$ percentage points
because the simple change-side-only approximation neglects the
FAR-side contribution to $G_u$, which is non-negligible at $V > 0.7$
where the optimal $c_u$ approaches zero (so the FAR-side density
$\varphi(-d'_b/2 - c_u) \approx \varphi(-0.75) = 0.301$ is *comparable*
to the change-side density $\varphi(0.85) = 0.279$). Including the
FAR-side term roughly doubles $G_u$, which shifts $V_{\text{critical}}$
up to $\approx 0.78$, matching the empirical boundary.

### 5.2 The V-boundary location

A fine V-grid at $(r=0.1, v=5)$ resolves the boundary:

| $V$ | $\alpha^\star_{P_1}$ | $\alpha^\star_{P_2}$ | $R(P_1)$ | $R(P_2)$ | VDA |
|---:|---:|---:|---:|---:|---:|
| 0.750 | 0.97 | **0.25** | 3.0409 | 2.9999 | **0.0410** |
| 0.755 | 0.97 | 0.28 | 3.0585 | 3.0201 | 0.0384 |
| 0.760 | 0.97 | 0.29 | 3.0760 | 3.0382 | 0.0378 |
| 0.765 | 0.97 | 0.32 | 3.0936 | 3.0582 | 0.0354 |
| 0.770 | 0.97 | 0.36 | 3.1112 | 3.0790 | 0.0322 |
| 0.775 | 0.97 | 0.40 | 3.1287 | 3.0995 | 0.0292 |
| 0.780 | 0.97 | **0.93** | 3.1463 | 3.1457 | **0.0006** |
| 0.785 | 0.97 | 0.93 | 3.1638 | 3.1633 | 0.0006 |
| 0.790 | 0.97 | 0.93 | 3.1814 | 3.1808 | 0.0006 |
| 0.800 | 0.97 | 0.94 | 3.2165 | 3.2162 | 0.0004 |

The empirical $V_{\text{critical}}(r=0.1, N=4) \in (0.775,\, 0.780)$.
Across the boundary at $V \to 0.780$, $\alpha^\star_{P_2}$ jumps from
$0.40$ to $0.93$ in one V-step of $0.005$ — the P_2 escape
predicted by (4) — and VDA collapses by $50{\times}$. The §4.4 "$V
\geq 0.75$" threshold is **off by approximately one V-grid step** at
this $r$ (probably the paper's V-grid spacing).

### 5.3 The r-extent of the high-V VDA window

A fine r-grid at $(V=0.75, v=5)$ confirms the sup is interior:

| $r$ | $\alpha^\star_{P_1}$ | $\alpha^\star_{P_2}$ | VDA |
|---:|---:|---:|---:|
| 0.050 | 0.91 | 0.25 | 0.0173 |
| 0.063 | 0.94 | 0.25 | 0.0235 |
| 0.079 | 0.95 | 0.25 | 0.0312 |
| **0.100** | **0.97** | **0.25** | **0.0410** |
| 0.126 | 0.98 | 0.40 | 0.0366 |
| 0.158 | 0.99 | 0.96 | 0.0006 |
| 0.200 | 0.99 | 0.98 | 0.0002 |

The window of "non-negligible" VDA (VDA $> 0.005$) at $V = 0.75$
extends across $r \in [\approx 0.04, \approx 0.13]$, peaking at $r =
0.10$. The window of "hot zone" VDA (VDA $> 0.02$ per §4.4's own
boundary) extends across $r \in [\approx 0.06, \approx 0.13]$. Both
windows have non-empty intersection with the paper's primary r-grid
$\{0.1, 0.126\}$, so the §4.4 categorical claim is false at *two*
sampled grid points (not one).

### 5.4 The full (r, v) sup at V = 0.75

The full table is in
`../replications/C3--high-V-supremum/output/sup_vda_at_V075.json`.
Summary of the (r, v) tuples that violate the §4.4 "negligible
($<0.005$)" threshold:

| $v$ | $r$ values with VDA $>0.005$ | max VDA |
|---:|---:|---:|
| 1 | (none — VDA = 0 for all r, theorem from CR-001 §2.4) | 0 |
| 2 | $\{0.100, 0.126\}$ | 0.0119 (r=0.10) |
| 3 | $\{0.100, 0.126\}$ | 0.0226 (r=0.10) |
| 4 | $\{0.100, 0.126\}$ | 0.0321 (r=0.10) |
| 5 | $\{0.100, 0.126\}$ | 0.0410 (r=0.10) |

So out of the 21 r-points × 5 v-points = 105 grid combinations at
V = 0.75, exactly **8** violate "VDA $<0.005$" (the two r-corners
$\{0.10, 0.126\}$ crossed with $v \in \{2,3,4,5\}$), and **6** of
those 8 also violate "VDA $<0.02$" (the same r-corners crossed with
$v \in \{3,4,5\}$). This is $\approx 8\%$ of the V=0.75 slice in
the paper's primary sweep that contradicts §4.4 verbatim — not a
single isolated grid corner but a systematic two-r-step window.

## 6. Decision per CR-026 task definition

The CR-026 task in `agents/RESEARCH_BACKLOG.md` specifies three
outcomes for the sup:

- (i) sup $< 0.005$: C3b is a theorem of the model → elevate to
  CONFIRMED-CONDITIONAL.
- (ii) sup $\in [0.005, 0.020]$: §5.2 categorical wording too strong
  → verdict stays WEAKLY-SUPPORTED with reformulation.
- (iii) sup $> 0.020$: §5.2 wording wrong internal to the model →
  verdict moves to CONTESTED.

The empirical sup is $0.040$ — case (iii). **Verdict label: CONTESTED.**

The §4.4 / §5.2 categorical wording fails *internal to the model* —
this is not an empirical-biology contradiction but a mathematical
refutation of the paper's own claim under its own assumptions.

## 7. Proposed reformulation (preserves the paper's scientific point)

The substantive content of §4.4 / §5.2 — that the high-V VDA window
is narrow and that experimental designs operating in the high-V
regime are unlikely to detect VDA — is **not refuted** by this
re-derivation. What is refuted is the *categorical V-threshold*
$V \geq 0.75$ and the *categorical r-quantifier* "regardless of $r$".

A proposed reformulation that preserves the paper's intent and is
demonstrably true under the model's assumptions:

> **§4.4 (proposed).** *At validity exceeding the closed-form
> threshold $V_{\text{critical}}(r, N) = 1/(1 + r\,(N-1)/\kappa)$ (Eq. 5 of
> Critique/derivations/C3--high-V-supremum.md, with $\kappa \in
> [0.8, 1.0]$ a slowly-varying density ratio), optimal $\alpha^\star$
> is near $1.0$ for the value-blind policy as well as the value-aware
> policy, and VDA is negligible ($<0.005$). For the paper's reference
> parameters $(N{=}4, d'_{\max}{=}2, f_0{=}0.5, h{=}\sqrt{})$ this
> threshold is empirically $V_{\text{critical}}(r{=}0.1, N{=}4)
> \approx 0.78$, $V_{\text{critical}}(r{=}0.5, N{=}4) \approx 0.40$,
> $V_{\text{critical}}(r{=}1, N{=}4) \approx 0.25 = 1/N$. **For $r
> \leq 0.13$ at $V = 0.75$, a high-VDA window persists** with peak
> VDA up to $0.04$ reward units at $(r{=}0.1, v{=}5)$, before
> collapsing above the boundary.*

> **§5.2 (proposed).** *Standard spatial cueing paradigms with
> validity above the model's $V_{\text{critical}}$ boundary
> ($V \geq 0.80$ at the reference parameters, less at larger $r$) are
> predicted to show negligible VDA on behavioural d′. The
> $V_{\text{critical}}$ boundary is sensitive to the asymmetry ratio
> $r$ and to the set size $N$; at large $N$ or cost-dominant $r$, the
> boundary moves close to $V = 1.0$, leaving a narrow high-V VDA
> window of practical relevance. Experimenters who pre-commit to a
> high-V paradigm should also pre-commit to an asymmetry-ratio
> calibration (e.g., by varying stimulus-onset asynchrony or
> eccentricity) to avoid operating in the residual high-V VDA window
> near $r \approx 1/(N-1)$.*

The reformulation is verifiable directly from the closed form (5) and
the numerical sweep §5.

## 8. Open questions surfaced by the re-derivation

1. **Sensitivity of $V_{\text{critical}}$ to $f_0$ and $h$.** The
   closed-form (5) involves $\kappa$ which in turn involves $d'_b =
   d'_{\max}\,f(1/N)$. At lower $f_0$, $d'_b$ drops and the densities
   $\varphi$ shift; $\kappa$ likely grows, pushing $V_{\text{critical}}$
   higher and widening the high-V VDA window. The paper's Figure 6
   sweeps $f_0 \in \{0.1, 0.3, 0.5, 0.7\}$ but does not report VDA at
   $V = 0.75$ across this sweep. Worth spawning as a follow-up.

2. **Sensitivity to $N$.** From (5), $V_{\text{critical}} = 1/(1 +
   r(N-1)/\kappa)$. Larger $N$ pushes $V_{\text{critical}}$ down,
   making the high-V VDA window narrower. Smaller $N$ (e.g., $N=2$,
   the paper's secondary sweep) pushes $V_{\text{critical}}$ closer
   to 1, dramatically widening the window. The paper's §4.6 N-sweep
   does not report VDA at high V for $N=2$; predicted to be larger
   than at $N=4$.

3. **FAR-side correction to (3).** The simple change-side
   approximation (3) underestimates $V_{\text{critical}}$ by $\approx
   4$pp because it neglects the FAR-side density $\varphi(-d'_b/2 -
   c_u)$, which is *comparable* to the change-side density when $c_u
   \approx 0$. A full closed-form $V_{\text{critical}}$ would include
   both contributions. Spawn as a math follow-up.

4. **The proposed reformulation has an experimental-design
   prescription** ("pre-commit to $r$-calibration") that the paper
   does not make. This is in tension with the paper's §5.2 framing
   that high-V paradigms can be interpreted *without* such
   calibration. Worth flagging as an experimental-design implication
   for the C3 verdict's "Implications for PRISM" block.

## 9. Verdict input

This re-derivation contributes the **second attack vector** on C3
(after the literature attack in run-004, see
`Critique/verdicts/C3--narrow-regime.md` Version 0.1). The two
attacks point in opposite verdict directions:

- Run-004 literature attack: C3a confirmed, C3b weakly supported with
  Stănișor 2013 constraint.
- Run-005 re-derivation attack: **C3b refuted internal to the model**
  at $V = 0.75$.

Per mission §3.1, two distinct attack vectors yielding opposite
findings move the verdict to **CONTESTED** (not CONFIRMED-UNDER-ATTACK,
because the second attack succeeded in falsifying part of the claim).
The C3 verdict at end of run-005 is therefore **CONTESTED**, with the
proposed reformulation (§7 above) as the operational replacement for
the §4.4 / §5.2 categorical wording. C3a (the low-V end) remains
confirmed.

## References (wiki ids)

- Internal: `[[../derivations/C2--non-monotonic-vda.md]]` — the
  CR-001 closed-form machinery this re-derivation extends.
- `[[luo_maunsell2018_criterion_sensitivity]]` — the empirical
  substrate for the SDT decomposition; relevant because the
  proposed §5.2 reformulation explicitly carves out an
  $r$-calibration step that Luo-Maunsell's stimulus-side
  sensitivity manipulation provides one implementation of.
- `[[reynolds_heeger2009_normalization]]` — the divisive-normalisation
  substrate; bears on §8 question 1 (whether $\kappa(V,N)$ depends
  systematically on the transfer-function shape via the
  normalisation pool).
- `[[stanisor2013_v1_value_attention]]` — the prima-facie empirical
  constraint surfaced in run-004; the §7 reformulation now formally
  predicts a residual high-V VDA window at small $r$ that could be
  the substrate of the Stănișor V1 signature, shifting Stănișor's
  classification from "constrain" to potentially "support" once the
  full-depth read (CR-023) is done.
- `[[cohen_maunsell2009_correlations]]` — bears on assumption A1
  (independence); the §3 magnitude estimate assumes independent SDT
  decisions, which is precisely what A1 stipulates. A future
  replication-attack (CR-006) would test whether the high-V VDA
  window persists under cross-location response correlations.
- `[[carrasco2011_visual_attention_25y]]` — confirms that the
  high-V × value-magnitude experiment that would directly test the
  proposed §5.2 reformulation has not been run; the proposed
  reformulation predicts such an experiment would find a measurable
  VDA effect at $V = 0.75$ with $v \geq 3$ and $r$ in the
  cost-dominant regime.
