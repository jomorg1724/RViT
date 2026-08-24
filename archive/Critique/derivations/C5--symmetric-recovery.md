---
type: derivation
claim_id: C5
title: "Symbolic re-derivation of the r=1 symmetric recovery, with a Sterbenz bit-exactness lemma"
paper_section: "Appendix A (Validation: Symmetric Special Case), Figure 7"
attack_vector: re-derivation
run_id: run-009
prompt_version: 0.2
created: 2026-05-22
companion_replication: Critique/replications/C5--symmetric-recovery/
---

# Re-derivation: $r=1$ recovers the symmetric special case (C5)

This file is the **re-derivation attack** on C5 (mission §3.2), the
second distinct attack vector after the run-008 replication. The
replication (`Critique/replications/C5--symmetric-recovery/run.py`)
*measured* the paper's "maximum difference: 0.0" and reproduced it
exactly. This file *proves* it: it shows symbolically that the
recovery is a real-number identity, and proves the bit-for-bit
"0.0" with a floating-point lemma the paper does not state. Per §5.3,
every step is shown; the one place the paper skips the mechanism is
flagged explicitly.

The float-arithmetic propositions below were checked independently of
run-008's optimiser by `/tmp` script reproduced verbatim in §5; its
output is pasted in §5 and matches run-008's `notes.md` table.

---

## 1. Setup and notation

We restate only the pieces of mission §2.3–§2.4 the recovery needs.

**Domains.** $N \in \mathbb{Z}_{\ge 2}$ locations; attention
$\alpha \in [0,1]$ on the cued location; transfer function
$f(a) = f_0 + (1-f_0)\,h(a)$ with floor $f_0 \in (0,1)$, shape
$h:[0,1]\to[0,1]$ monotone with $h(0)=0,\,h(1)=1$ (here $h(a)=\sqrt a$),
maximal sensitivity $d'_{\max} > 0$. Baseline (uniform-attention)
sensitivity

$$
d'_{\text{base}} \;:=\; d'_{\max}\, f\!\left(\tfrac{1}{N}\right) \;>\;0 .
\tag{1}
$$

**Asymmetry weights** (mission §2.4), $r>0$:

$$
\beta(r) = \frac{2r}{r+1}, \qquad \gamma(r) = \frac{2}{r+1},
\qquad \beta+\gamma = 2, \quad \beta/\gamma = r .
\tag{2}
$$

**Asymmetric sensitivity map** ("the model"). Writing the per-branch
argument $a_c=\alpha$ (cued) and $a_u=\tfrac{1-\alpha}{N-1}$ (uncued),
and the *raw transfer output* $x_\bullet := d'_{\max} f(a_\bullet)$,

$$
\boxed{\;d'^{\,\text{asym}}_{\bullet}(r) \;=\; d'_{\text{base}} \;+\; s_\bullet(r)\,\bigl[\,x_\bullet - d'_{\text{base}}\,\bigr]\;}
\qquad s_c=\beta(r),\ s_u=\gamma(r),
\tag{3}
$$

with the clamp $d'\!\leftarrow\!\max(d',0)$ applied afterwards (it is
inert on the validation config, where $d' \ge 1.0$; see §3 footnote).

**Symmetric map** ("a single shared transfer function governs both
benefit and cost", Appendix A). This is the model with *no* $\beta/\gamma$
re-scaling — the transfer output used directly:

$$
\boxed{\;d'^{\,\text{sym}}_{\bullet} \;=\; x_\bullet \;=\; d'_{\max} f(a_\bullet)\;}.
\tag{4}
$$

Both maps feed the **same** downstream SDT / reward / optimiser stack
(mission §2.2, §2.5): same $\mathrm{HR}=\Phi(d'/2-c)$, same
$\mathrm{FAR}=\Phi(-d'/2-c)$, same $\mathbb{E}[R]$, same $(\alpha,c)$
grid optimiser. Therefore the optimal policy $(\alpha^\star, c^\star)$
and optimal reward $R^\star$ can differ between the two maps **only**
through the $d'(\alpha)$ arrays they produce. The claim C5 is exactly
the statement that, at $r=1$, those arrays coincide.

---

## 2. Theorem 1 — the recovery is a real-number identity

> **Theorem 1.** Over the reals, $d'^{\,\text{asym}}_{\bullet}(1) = d'^{\,\text{sym}}_{\bullet}$
> for both branches $\bullet \in \{c,u\}$ and every $\alpha\in[0,1]$.
> Consequently $\alpha^\star, c^\star, R^\star$ are identical between
> the two models at $r=1$.

**Proof.** Evaluate (2) at $r=1$:

$$
\beta(1) = \frac{2\cdot 1}{1+1} = \frac{2}{2} = 1,
\qquad
\gamma(1) = \frac{2}{1+1} = \frac{2}{2} = 1 .
\tag{5}
$$

Substitute $s_\bullet = 1$ into (3):

$$
d'^{\,\text{asym}}_{\bullet}(1)
= d'_{\text{base}} + 1\cdot\bigl[x_\bullet - d'_{\text{base}}\bigr]
= d'_{\text{base}} + x_\bullet - d'_{\text{base}}
= x_\bullet
= d'^{\,\text{sym}}_{\bullet}. \qquad\blacksquare
\tag{6}
$$

The cancellation $d'_{\text{base}} - d'_{\text{base}} = 0$ is the
entire content of the reduction: at $r=1$ the affine map
$x \mapsto d'_{\text{base}} + s(x-d'_{\text{base}})$ has unit
slope and a fixed point at $d'_{\text{base}}$, i.e. it is the identity
on $x$. Because the downstream stack is a deterministic function of the
$d'$ arrays alone, identical arrays $\Rightarrow$ identical
$(\alpha^\star,c^\star,R^\star)$. This is the sense in which the paper's
word **"reduces"** is exactly correct — it is an algebraic identity,
not an approximation.

**What the paper does not show, and why it matters.** Appendix A asserts
the reduction ("reduces to a symmetric special case") and then validates
it *numerically* ("maximum difference: 0.0"). The two-line algebra (5)–(6)
is never written. That is harmless for the real-number claim — but it
leaves the **bit-exact** "0.0" looking like an empirical surprise rather
than a structural guarantee. §3 supplies the missing mechanism, which is
where the only genuine subtlety lives.

**Geometric remark (consistency with the C4 derivation).**
`Critique/derivations/C4--no-inversion.md` §1 already noted that the
$d'(\alpha)$ kink at $\alpha=1/N$ (where the cued branch switches which
side of $d'_{\text{base}}$ it sits on) has left/right slope ratio
$\beta/\gamma = r$; the kink vanishes iff $\beta=\gamma$, i.e. $r=1$.
Theorem 1 is the same fact viewed globally: at $r=1$ the two affine
pieces share unit slope, so the piecewise map is the single smooth
curve $x_\bullet$. The two derivations corroborate.

---

## 3. Theorem 2 — bit-exactness via Sterbenz's lemma

Theorem 1 is a statement about reals. The paper's Figure 7 makes a
stronger, machine-level claim: "maximum difference: **0.0**", i.e. the
two code paths return *bit-identical* IEEE-754 binary64 values, so even
the argmax-over-grid step cannot separate them. This needs a
floating-point argument because, in general,
$\mathrm{fl}\bigl(a + \mathrm{fl}(s\cdot\mathrm{fl}(x-a))\bigr)$
is **not** guaranteed to equal $x$.

Let $\mathrm{fl}(\cdot)$ denote round-to-nearest binary64. Three facts
compose.

**Fact A — the weights are exact ones.** $\beta(1)$ and $\gamma(1)$ are
computed as $\mathrm{fl}(2\cdot 1)/\mathrm{fl}(1+1) = 2.0/2.0$. Each of
$2.0,\,1.0$ is exactly representable; $\mathrm{fl}(2.0/2.0)=1.0$ exactly.
So in code $s_\bullet = 1.0$ **bit-exactly**, with hex bit-pattern
`0x1.0000000000000p+0` (verified, §5 P1).

**Fact B — multiplication by $1.0$ is the identity in IEEE-754.** For
any finite double $y$, $\mathrm{fl}(1.0 \cdot y) = y$ exactly (the exact
product $1\cdot y = y$ is representable, so rounding is inert). Hence
$\mathrm{fl}(s_\bullet \cdot d) = d$ for $d=\mathrm{fl}(x-a)$.
(Verified on $10^7$ random doubles, §5 bonus.) The asymmetric code path
at $r=1$ therefore reduces, *bit-for-bit*, to

$$
d'^{\,\text{asym}}_{\bullet}(1) \;=\; \mathrm{fl}\!\bigl(a + \mathrm{fl}(x_\bullet - a)\bigr),
\qquad a := d'_{\text{base}} .
\tag{7}
$$

**Fact C — Sterbenz's lemma.** *If two finite floating-point numbers
$a,x$ of the same radix satisfy $a/2 \le x \le 2a$ (equivalently
$x/2 \le a \le 2x$), then $x-a$ is exactly representable and
$\mathrm{fl}(x-a) = x-a$* (Sterbenz 1974; Goldberg 1991, Thm. cited as
the "Sterbenz lemma"). No rounding occurs in the subtraction.

> **Theorem 2 (bit-exact recovery).** Suppose every transfer output
> $x_\bullet = d'_{\max} f(a_\bullet)$ that the sweep evaluates lies in
> the **Sterbenz band**
> $\;\mathcal B := [\,d'_{\text{base}}/2,\; 2\,d'_{\text{base}}\,]$.
> Then $d'^{\,\text{asym}}_{\bullet}(1) = x_\bullet = d'^{\,\text{sym}}_{\bullet}$
> *bit-for-bit*, hence the optimiser returns identical
> $(\alpha^\star,c^\star,R^\star)$ and the maximum difference is exactly
> $0.0$.

**Proof.** Fix a branch and let $x=x_\bullet \in \mathcal B$,
$a=d'_{\text{base}}$. By Fact C, $\mathrm{fl}(x-a)=x-a$ exactly; call this
exact difference $d$. Then $a+d = x$ as reals, and $x$ is itself a
representable double (it is the stored grid value), so
$\mathrm{fl}(a+d) = x$. Combining with (7) and Facts A–B,
$d'^{\,\text{asym}}_{\bullet}(1) = \mathrm{fl}(a+\mathrm{fl}(x-a)) = x$,
bit-identical to $d'^{\,\text{sym}}_{\bullet} = x$. Identical $d'$ arrays
feed the identical downstream stack, so every optimiser output matches
bit-for-bit and $\max|\Delta\alpha^\star| = \max|\Delta R^\star| = 0.0$.
$\blacksquare$

**Band membership at the validation config.** $N=4$, $d'_{\max}=2.0$,
$f_0=0.5$, $h=\sqrt{\cdot}$:

$$
d'_{\text{base}} = 2.0\,\bigl(0.5 + 0.5\sqrt{1/4}\bigr) = 2.0\cdot 0.75 = 1.5,
\qquad
\mathcal B = [0.75,\ 3.0].
\tag{8}
$$

Because $h=\sqrt{\cdot}$ is monotone with $f\in[f_0,1]=[0.5,1.0]$, every
transfer output obeys $x = 2.0\,f \in [1.0,\,2.0]$. Since
$[1.0,2.0]\subset[0.75,3.0]=\mathcal B$, Theorem 2's hypothesis holds at
**every** grid point of **both** branches (the uncued argument
$\tfrac{1-\alpha}{N-1}\in[0,1]$ gives the same $f$-range). Verified
directly (§5 P2): swept $x$-range $[1.0,2.0]$, all inside band,
`np.array_equal(asym_r1, sym) = True`, `max|delta| = 0.0`. Hence the
paper's "0.0" is a **structural guarantee of the validation config**,
not a numerical coincidence — the missing mechanism from §2.

> Footnote on the clamp. The post-map clamp $d'\!\leftarrow\!\max(d',0)$
> is a common-mode operation applied identically to both code paths; on
> the validation config all $d'\ge 1.0>0$ so it is inert and cannot
> create a discrepancy. Off-config it remains common-mode, so it never
> *introduces* a difference (it can only mask one), and is immaterial to
> Theorems 1–2.

---

## 4. Scope of the literal "0.0" — where Theorem 2's hypothesis fails

Theorem 2's hypothesis ($x\in\mathcal B$ for all swept $x$) is
**sufficient but not necessary**, and it can fail. The band is
$[d'_{\text{base}}/2, 2d'_{\text{base}}]$ with $d'_{\text{base}}\propto f(1/N)$,
while the smallest swept output is $x_{\min} = d'_{\max} f(0) = d'_{\max} f_0$.
The lower band edge bites when

$$
d'_{\max} f_0 \;<\; \tfrac12 d'_{\max} f\!\left(\tfrac1N\right)
\;\Longleftrightarrow\;
f_0 \;<\; \tfrac12\Bigl(f_0 + (1-f_0)\,h\!\left(\tfrac1N\right)\Bigr)
\;\Longleftrightarrow\;
f_0 \;<\; \frac{h(1/N)}{1+h(1/N)} .
\tag{9}
$$

For $h=\sqrt{\cdot}$, $N=4$: $h(1/4)=1/2$, so the threshold is
$f_0 < (1/2)/(3/2) = 1/3$. Thus **$f_0 \lesssim 0.33$ pushes the
low-attention transfer outputs below the band**, and Sterbenz no longer
*guarantees* an exact subtraction; the round-trip $a+(x-a)$ may then
round by up to $\tfrac12$ ulp, i.e. $\sim 10^{-16}$ relative.

The §5 P3 probe confirms this and reproduces run-008's `notes.md` table
exactly (independent code):

| $d'_{\max}$ | $f_0$ | swept $x$ | band $\mathcal B$ | $x\subset\mathcal B$? | $\max\lvert\Delta d'\rvert$ | bit-identical |
|---|---|---|---|---|---|---|
| 1.0 | 0.1 | [0.100,1.000] | [0.275,1.100] | no | 2.78e-17 | **no** |
| 1.0 | 0.3 | [0.300,1.000] | [0.325,1.300] | no | 0.0 | yes |
| 1.0 | 0.5 | [0.500,1.000] | [0.375,1.500] | yes | 0.0 | yes |
| 2.0 | 0.1 | [0.200,2.000] | [0.550,2.200] | no | 5.55e-17 | **no** |
| 2.0 | 0.3 | [0.600,2.000] | [0.650,2.600] | no | 0.0 | yes |
| **2.0** | **0.5** | **[1.000,2.000]** | **[0.750,3.000]** | **yes** | **0.0** | **yes (paper config)** |
| 3.0 | 0.1 | [0.300,3.000] | [0.825,3.300] | no | 1.11e-16 | **no** |
| 3.0 | 0.3 | [0.900,3.000] | [0.975,3.900] | no | 1.11e-16 | **no** |
| 3.0 | 0.5 | [1.500,3.000] | [1.125,4.500] | yes | 0.0 | yes |

Reading: (i) inside the band $\Rightarrow$ bit-exact, every time — the
implication of Theorem 2 holds with no exceptions; (ii) outside the band
$\Rightarrow$ *may* drift by $\sim 1$ ulp — 4 of the 9 shown (and 4 of 15
swept) configs lose bit-identity; (iii) "sufficient not necessary" is
visible in the $(1.0,0.3)$ and $(2.0,0.3)$ rows, which sit just outside
$\mathcal B$ yet remain exact because those particular operands still
subtract without rounding.

**Precise statement for the manuscript.** Two true statements, one scoped
and one universal:

- *Scoped (what Appendix A claims):* at $N=4,\ d'_{\max}=2.0,\ f_0=0.5,\ \sqrt{\cdot}$
  the maximum difference is **exactly $0.0$** — proven (Theorem 2 + (8)),
  not merely observed.
- *Universal (what generalises):* for any config, $r=1$ recovers the
  symmetric model **as reals** (Theorem 1) and *to machine precision*
  ($\le 1$ ulp on $d'$, which the grid argmax rounds to $0$ for
  $\alpha^\star$ and to $\sim 10^{-16}$ for $R^\star$); the literal
  $0.0$ holds iff the swept sensitivity range stays in $\mathcal B$, e.g.
  whenever $f_0 \ge h(1/N)/(1+h(1/N))$ (= $1/3$ for $h=\sqrt\cdot,N=4$).

This is the substance behind the **CR-039 / CR-041** owner-facing note.

---

## 5. Numerical verification (independent of run-008's `run.py`)

The script below was run in the sandbox this run; output pasted verbatim.
It checks Facts A–B and Theorems 1–2 directly, without importing the
optimiser, so it is a genuinely independent confirmation.

```python
import numpy as np
def beta(r):  return 2.0*r/(r+1.0)
def gamma(r): return 2.0/(r+1.0)
def f(a, f0): return f0 + (1.0-f0)*np.sqrt(a)
# P1: beta(1)=gamma(1)=1 exact
b1, g1 = beta(1.0), gamma(1.0)               # -> 1.0, hex 0x1.0...p+0, ==1.0 True
# P2: Sterbenz band, validation config N=4, dmax=2, f0=0.5 -> dbase=1.5
N, dmax, f0 = 4, 2.0, 0.5
dbase = dmax*f(1.0/N, f0)                     # 1.5 ; band [0.75, 3.0]
alpha = np.linspace(0,1,100001)
x = np.concatenate([dmax*f(alpha,f0), dmax*f((1-alpha)/(N-1),f0)])  # in [1.0,2.0]
rt = dbase + beta(1.0)*(x - dbase)            # asymmetric-at-r=1 path
# np.array_equal(rt, x) -> True ; max|rt-x| -> 0.0
# P3: vary (dmax,f0); inside band => 0.0, low-f0 (outside) => ~1 ulp
```

```
P1  beta(1) = 1.0  hex= 0x1.0000000000000p+0  ==1.0 exactly: True
P1  gamma(1)= 1.0  hex= 0x1.0000000000000p+0  ==1.0 exactly: True
P2  validation config: d'_base = 1.5  Sterbenz band [a/2,2a] = [0.75, 3.0]
P2  swept x range = [1.0, 2.0]  all inside band: True
P2  np.array_equal(asym_r1, sym) : True   max|delta| = 0.0
P2  subtraction-exact (a+(x-a)==x): True
P3  (table reproduced in §4)
bonus  1.0*x == x for 1e7 random doubles: True
```

All three propositions hold. The off-band drift values
(2.78e-17, 5.55e-17, 1.11e-16) match run-008's `notes.md` table to the
digit, cross-validating the two independent implementations.

---

## 6. Outcome and verdict movement

The re-derivation **goes through** with no skipped step and no surprise:

1. Theorem 1 proves the recovery is a real-number identity — the word
   "reduces" is exact, resting only on $\beta(1)=\gamma(1)=1$ (5).
2. Theorem 2 proves the bit-exact "0.0" from Sterbenz's lemma plus the
   band membership $[1.0,2.0]\subset[0.75,3.0]$ that the validation config
   happens to satisfy — supplying the mechanism Appendix A asserts but
   does not derive.
3. §4 delimits the literal "0.0": it is config-specific (fails for
   $f_0 \lesssim 1/3$ at $N=4,\sqrt\cdot$); the universal statement is
   "machine precision, $\le 1$ ulp."

This is a **second, methodologically distinct** attack vector on C5
(re-derivation, after run-008's replication), and it failed to falsify
the claim — it strengthened it to a theorem. Per mission §3.1/§6, C5
therefore elevates **WEAKLY-SUPPORTED → CONFIRMED-UNDER-ATTACK**. The
companion verdict file records the elevation with both vectors listed.

---

## References

- Sterbenz, P. H. (1974). *Floating-Point Computation.* Prentice-Hall.
  (The subtraction lemma: $a/2 \le x \le 2a \Rightarrow \mathrm{fl}(x-a)=x-a$.)
- Goldberg, D. (1991). "What Every Computer Scientist Should Know About
  Floating-Point Arithmetic." *ACM Computing Surveys* 23(1):5–48.
  (Standard reference statement of Sterbenz's lemma and IEEE-754
  round-to-nearest semantics.)
- Target paper, Appendix A and Figure 7 (`Critique/source/main.pdf`, p.8):
  the claim being re-derived.
- `Critique/replications/C5--symmetric-recovery/` (run-008): the first
  attack vector (replication); this derivation promotes its Block-2/3
  findings to proofs.
- `Critique/derivations/C4--no-inversion.md` §1 (run-006): the
  $\beta/\gamma$ kink-slope analysis that Theorem 1 corroborates at $r=1$.
