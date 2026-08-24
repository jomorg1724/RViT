---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.2
run_id: run-010
started: 2026-05-23T03:15:25Z
ended: 2026-05-23T03:52:00Z
worked_on: A3
attack_vector: re-derivation
verdict_touched: A3--multiplicative-conservation
verdict_after: WEAKLY-SUPPORTED
papers_read: [reynolds_heeger2009_normalization, maunsell2015_attention_mechanisms, luo_maunsell2018_criterion_sensitivity, reynolds1999_competitive_v2_v4, desimone_duncan1995_biased_competition, carrasco2011_visual_attention_25y, coalition_resource_competition]
papers_added: []
spawned_tasks: [CR-008 (promoted to second-vector, replication), CR-042 (sensitivity: peak-shift across f_0/h), CR-043 (literature: additive-vs-divisive conservation primate citation)]
---

# A3 — does the §5.5 robustness claim survive the βγ=1 swap? (CR-040)

## What I attacked

Assumption **A3** (mission §2.7): the benefit/cost asymmetry obeys the
*additive* conservation rule $\beta+\gamma=2$. The paper flags this in
§5.5 (p.8) and asserts a falsifiable robustness claim: replacing it with
the *multiplicative* $\beta\gamma=1$ "could yield quantitatively
different results, though the qualitative findings—non-monotonic VDA, no
inversion, criterion dominance—should be robust." First touch on A3
(verdict was non-existent); this is the substantive bridge from the
just-closed C5 into the assumption layer (CR-040, spawned by run-009).

## How I attacked it

**Re-derivation** (mission §3.2), corroborated by **one focused
replication slice** (mission §8.5 — not the 4,410-row sweep). I solved
both conservation rules under the shared ratio $\beta/\gamma=r$, proved
a closed-form relation between the two weight families, and then swapped
the β/γ map in an independent re-implementation of the §2.5 policy
decomposition (reusing the C5/C2 substrate) to read off the C2 VDA peak,
the C1 criterion fraction, and a C4 no-inversion check at the paper's
reference regime.

## What I found

**The two families are one rescaling apart.** Additive
$\beta_+=2r/(r+1),\gamma_+=2/(r+1)$; multiplicative
$\beta_\times=\sqrt r,\gamma_\times=1/\sqrt r$. Both give $(1,1)$ at
$r=1$. The key theorem: $\beta_\times/\beta_+=\gamma_\times/\gamma_+=\kappa(r)=\frac{r+1}{2\sqrt r}=\cosh(\tfrac12\ln r)\ge1$
(verified to $8.9\times10^{-16}$), so $(\beta_\times,\gamma_\times)=\kappa(r)(\beta_+,\gamma_+)$.
Therefore $\beta_\times+\gamma_\times=2\kappa\ge2$: **$\beta\gamma=1$ does
not conserve total magnitude** — the paper's "conserves total attention
magnitude" is additive-only. Geometrically the hyperbola $\beta\gamma=1$
sits on/above the line $\beta+\gamma=2$ (AM–GM), tangent only at $(1,1)$,
so $\beta\gamma=1$ is uniformly more aggressive.

On the reference slice ($N=4,d'_{\max}=2,f_0=0.5,\sqrt\cdot,V=0.5,v=5$,A):

- **C2 non-monotonic VDA — robust.** Two-limit theorem ($\text{VDA}\to0$
  at $r\to0,\infty$) holds under both rules ($\beta(0)=0,\gamma(\infty)=0$
  in both). Peak shifts $0.398\to0.316$ and rises $+14\%$
  ($0.0797\to0.0909$). (My additive $0.0797$ ≈ the paper's Figure-4
  $\sim0.080$, validating the implementation.)
- **C1 criterion dominance — survives, erodes.** $R(P3),R(P4)$ are
  family-independent (both at $\alpha=1/N$, weights × zero bracket); only
  $R(P1)$ moves. CF floor drops $0.601\to0.507$ — still $>0.5$ but by
  only $0.007$ at $r=10$.
- **C4 no inversion — robust within $V\ge1/N$.** $\min\alpha^\star=1/N$
  exactly across the slice and the adversarial $r=10$ cells.
- **C5 cross-check (free):** at $r=1$ both families return identical
  numbers — the constraint-agnosticism proved in the C5 v0.2 verdict.

## Verdict movement

**(none) → WEAKLY-SUPPORTED.** No named qualitative finding broke under
$\beta\gamma=1$ on this slice, so the §5.5 robustness assertion survives
its first attack vector; per mission §6 one vector cannot elevate
further. Not CONTESTED (nothing flipped) but flagged-risk: criterion
dominance survives by only $0.007$, and C1 is *already* CONTESTED under
the additive rule in low-$V$/high-$v$/variant-B cells *outside* this
slice — where $\beta\gamma=1$ (which lowers CF wherever $R(P1)$ grows)
will plausibly push CF below $0.5$. That is the one place A3 could move
to CONTESTED; deciding it needs the full multiplicative sweep.

## Next-attack recommendation

**CR-008 (replication, promoted to the designated second vector):** run
the multiplicative sweep restricted to the run-003 cells where additive
CF $<0.60$, and test whether criterion dominance (CF $>0.5$) survives
$\beta\gamma=1$ globally or breaks. If it breaks, A3 → CONTESTED and the
§6 "criterion dominance" categorical needs scoping.

## Wiki cross-references

- `[[reynolds_heeger2009_normalization]]` — cited: divisive
  (multiplicative) normalization makes $\beta\gamma=1$ the more
  mechanism-aligned conservation; substrate for §5.4's $r$ = gain (β) vs
  suppression (γ) reading.
- `[[maunsell2015_attention_mechanisms]]`, `[[luo_maunsell2018_criterion_sensitivity]]`
  — cited: SDT sensitivity/criterion substrate behind the CF (C1) erosion.
- `[[reynolds1999_competitive_v2_v4]]`, `[[desimone_duncan1995_biased_competition]]`
  — cited: biased-competition zero-sum reallocation = the additive
  analog in cortex (§5.1 framing).
- `[[coalition_resource_competition]]` (concept) — cited: the user's
  finite-resource-conservation program; frames "conserves total
  magnitude" and the PRISM implication.
- `[[carrasco2011_visual_attention_25y]]` — consulted; subsumed by the
  Reynolds-Heeger citation, not separately load-bearing.
- `[[bisley_goldberg2010_parietal_priority]]`, `[[bisley_mirpour2019_priority_map]]`,
  `[[rust_cohen2022_priority_coding]]` — consulted (priority-map anchor);
  about *where* attention goes, not the conservation form — unrelated on
  inspection.
- dopamine/RPE/basal-ganglia, LIP, FEF/SC, saccade/oculomotor (§11.1
  anchors) — consulted; concern the *source* of value signals, not the
  structural conservation form — unrelated on inspection.
- No conservation-constraint-comparison or numerical-methods literature
  in `research_db/` (expected gap).
