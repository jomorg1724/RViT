---
type: verdict
claim_id: A3
claim_statement: "The benefit/cost asymmetry obeys additive conservation β+γ=2; the paper (§5.5) asserts the multiplicative alternative βγ=1 yields quantitatively different results but the qualitative findings (non-monotonic VDA, no inversion, criterion dominance) are robust."
paper_section: "§5.5 (Limitations); the constraint enters §2.4"
current_label: CONTESTED
attacks_tried:
  - vector: re-derivation
    run_id: run-010
    outcome: "robustness claim survived at the reference slice; non-monotonic VDA and no-inversion robust; criterion dominance survives but erodes to a thin margin (CF floor 0.601→0.507)"
  - vector: replication
    run_id: run-011
    outcome: "criterion-dominance robustness FAILS as a per-cell claim within the paper's own grid: βγ=1 doubles the criterion-subordinate fraction (4.0%→8.3% of 4,410 cells; 191 cells flip from CF≥0.5 to CF<0.5), concentrated in the benefit-dominant high-r corner. Survives only as a central-tendency claim (median CF 0.7605→0.7578)."
load_bearing_for:
  - "§2.4 (the β,γ asymmetric-scaling definitions)"
  - "§4.1 / §5.1 (C1 criterion fraction; 'criterion is always the largest contributor' / criterion-dominance narrative)"
  - "§4.3 / §4.6 (C2 non-monotonic VDA peak)"
  - "§5.5 robustness assertion"
  - "§6 conclusion (the categorical findings)"
last_updated: "2026-05-24"
prompt_version_observed: "0.2"
---

# Verdict: additive (β+γ=2) vs multiplicative (βγ=1) conservation — A3

## Claim as written in the paper

§5.5 (Limitations), p.8, verbatim:

> "Third, the $\beta + \gamma = 2$ constraint conserves total attention
> magnitude; alternative constraints (e.g., multiplicative
> $\beta\gamma = 1$) could yield quantitatively different results,
> though the qualitative findings—non-monotonic VDA, no inversion,
> criterion dominance—should be robust."

A3 (mission §2.7) names the additive conservation rule as a
load-bearing assumption. The verdict tests the paper's own
**robustness claim** about replacing it with $\beta\gamma=1$.

## Why this matters

The constraint enters the model at §2.4: it is the single equation
that turns the asymmetry *ratio* $r=\beta/\gamma$ into concrete weights
$(\beta,\gamma)$. Every headline number (C1 criterion fraction, C2 VDA
peak, C4 no-inversion) is computed at one specific choice of that
equation. If the qualitative findings flip under the equally-natural
$\beta\gamma=1$, then C1–C4 are partly artifacts of a modelling
convenience rather than properties of "value-directed attention", and
the §6 categorical conclusions would need scoping. The paper concedes
quantitative sensitivity but bets the qualitative story is invariant —
and never runs the alternative to check. **For the user's PRISM
program** the stakes are concrete: PRISM's FiLM modulation
(`Prism/film.py`) is a *multiplicative* gain plus additive offset
(`reynolds_heeger2009_normalization` →
`Prism/docs/THESIS.md` §2.4), so PRISM lives closer to the
*multiplicative* side of this very dichotomy; which constraint the
normative predictions assume changes what PRISM's attention
trajectories should look like.

## Version 0.1 — 2026-05-22

### What this version did

**Attack vector: re-derivation** (mission §3.2), with a focused
single-slice replication for numerical corroboration (mission §8.5 —
not the full 4,410-row sweep). Derivation:
`Critique/derivations/A3--multiplicative-conservation.md`. Code/output:
`Critique/replications/A3--multiplicative-conservation/`.

Solved both conservation rules under the common ratio constraint
$\beta/\gamma=r$:

$$
\text{additive: } \beta_+=\tfrac{2r}{r+1},\ \gamma_+=\tfrac{2}{r+1};
\qquad
\text{multiplicative: } \beta_\times=\sqrt r,\ \gamma_\times=\tfrac1{\sqrt r}.
$$

**Theorem (common rescaling).** $\beta_\times/\beta_+ = \gamma_\times/\gamma_+ = \kappa(r)$
with $\kappa(r)=\tfrac{r+1}{2\sqrt r}=\cosh(\tfrac12\ln r)\ge1$, equality
iff $r=1$. So $(\beta_\times,\gamma_\times)=\kappa(r)\,(\beta_+,\gamma_+)$:
the multiplicative weights are the additive weights scaled by **one
common factor** $\kappa\ge1$, verified numerically to $8.9\times10^{-16}$.

Consequences (each tested on the reference slice $N=4$, $d'_{\max}=2$,
$f_0=0.5$, $\sqrt\cdot$, $V=0.5$, $v=5$, Variant A):

1. **Magnitude is NOT conserved by $\beta\gamma=1$.**
   $\beta_\times+\gamma_\times=2\kappa(r)\ge2$. The paper's phrase
   "$\beta+\gamma=2$ conserves total attention magnitude" is an
   *additive-only* property; $\beta\gamma=1$ conserves the *geometric*
   mean and lets the arithmetic mean inflate ($+74\%$ at $r=0.1,10$;
   $+20\%$ at the VDA peak). Geometrically the hyperbola $\beta\gamma=1$
   lies on/above the line $\beta+\gamma=2$ (AM–GM), tangent only at
   $(1,1)$ — so $\beta\gamma=1$ is *uniformly more aggressive*.

2. **C2 non-monotonic VDA — ROBUST.** Two-limit theorem
   ($\text{VDA}\to0$ as $r\to0,\infty$) holds under both rules because
   both have $\beta(0)=0$ and $\gamma(\infty)=0$. Slice: peak shifts
   $r=0.398\to0.316$ (deeper cost-dominant) and rises $+14\%$
   ($0.0797\to0.0909$); curve stays cleanly single-peaked.

3. **C1 criterion dominance — SURVIVES but ERODES.** $R(P3),R(P4)$ are
   *family-independent* (both sit at $\alpha=1/N$ where $\beta,\gamma$
   multiply a zero bracket), so only the $R(P1)$ denominator moves. CF
   floor drops $0.601\to0.507$ over the slice — still $>0.5$ (criterion
   captures the majority) but by only $0.007$ at $r=10$.

4. **C4 no inversion — ROBUST within $V\ge1/N$.** $\min\alpha^\star=1/N$
   exactly across the reference $r$-grid and the most-adversarial
   $V\ge1/N$ cells at $r=10$. The CR-004 location-count-asymmetry
   mechanism is $\beta,\gamma$-independent in its structural ingredients.

5. **C5 cross-check (free).** At $r=1$ the two families return identical
   numbers (VDA $0.03983$, CF $0.7282$, $\alpha^\star_{P1}1.000$,
   $\alpha^\star_{P2}0.750$) — the constraint-agnosticism proved in the
   C5 v0.2 verdict, confirmed numerically.

### Verdict

**Label: OPEN → WEAKLY-SUPPORTED.** No named qualitative finding broke
under $\beta\gamma=1$ on the reference slice, so the §5.5 robustness
assertion survives its first attack vector. Per mission §6 a single
vector cannot elevate beyond WEAKLY-SUPPORTED. The label is *not*
CONFIRMED-CONDITIONAL because the one slice tested is insufficient to
certify the conditional, and *not* CONTESTED because nothing actually
flipped — but the verdict carries a **flagged risk**: criterion
dominance survives by only $0.007$ at the slice's worst point, and C1 is
*already* CONTESTED under the additive rule (run-003: CF down to $0.304$
in variant-B / low-$V$ / high-$v$ cells *outside* this slice). Because
$\beta\gamma=1$ lowers CF wherever $R(P1)$ can grow, those cells will
plausibly push CF **below $0.5$** under $\beta\gamma=1$ — i.e. criterion
dominance may *fail* in part of the space the paper claims robustness
for. Deciding that requires the full multiplicative sweep (CR-008, the
designated second vector).

A secondary, citable sharpening: the paper's incidental claim that
$\beta+\gamma=2$ "conserves total attention magnitude" is true only for
the additive rule; $\beta\gamma=1$ does not conserve it, so the two
constraints are not interchangeable reparameterisations. This matters
because the canonical neural model of attention — divisive
normalization (`reynolds_heeger2009_normalization`) — is a
*multiplicative/divisive* operation, so $\beta\gamma=1$ is arguably the
*more* biologically defensible conservation rule. The paper picked the
additive form for tractability and asserted (correctly, so far) that the
qualitative story does not depend on it; but the constraint it dismisses
is the one closer to the dominant mechanistic account, which raises the
stakes of the CR-008 follow-up.

### Evidence

- Derivation (full LaTeX, Theorem + 3 propositions):
  `Critique/derivations/A3--multiplicative-conservation.md`.
- Replication slice (Blocks 0–3, both families):
  `Critique/replications/A3--multiplicative-conservation/`
  (`run.py`, `output/results.json`, `output/run.log`, `notes.md`).
- `[[reynolds_heeger2009_normalization]]` (full) — divisive normalization
  models attention as per-neuron multiplicative gain on a numerator
  ($G_E$, the $\beta$ "benefit" analog) and/or suppressive pool ($G_S$,
  the $\gamma$ "cost" analog); a divisive (multiplicative-flavoured)
  conservation, so $\beta\gamma=1$ is the more normalization-aligned
  rule. Cited for the biological-defensibility point and §5.4's
  gain-vs-suppression interpretation of $r$.
- `[[maunsell2015_attention_mechanisms]]`, `[[luo_maunsell2018_criterion_sensitivity]]`
  — the SDT sensitivity/criterion substrate the model rests on; bear on
  the criterion-dominance (C1) erosion finding.
- `[[reynolds1999_competitive_v2_v4]]`, `[[desimone_duncan1995_biased_competition]]`
  — biased competition is a zero-sum (additive-flavoured) reallocation
  account; supports the §5.1 framing the additive rule encodes.
- `[[coalition_resource_competition]]` (concept) — the user's
  finite-resource-allocation framing; the "$\beta+\gamma=2$ conserves
  total magnitude" assumption is literally a resource-conservation
  constraint, and §5.1's zero-sum reallocation is its behavioural face.

### Implications for PRISM (mission §3.5)

A3 touches C2 and C4 (behavioural predictions), so per §3.5: PRISM v1/v2
implement attention as FiLM — a *multiplicative* per-location gain plus
additive offset (`Prism/film.py`; `reynolds_heeger2009_normalization` →
`Prism/docs/THESIS.md` §2.4; `perez2018_film`). PRISM therefore sits on
the *multiplicative* side of this dichotomy, closer to $\beta\gamma=1$
than to the paper's $\beta+\gamma=2$. The slice predicts that, relative
to the additive normative model, the multiplicative one shows (i)
modestly *larger* value-directed reallocation (peak VDA $+14\%$, shifted
into the cost-dominant regime) and (ii) modestly *less* pure-criterion
routing (CF floor lower). Translated: a PRISM agent, if it has internalised
something like the normative optimum, should if anything show *slightly
more* attentional reallocation toward value and *slightly weaker*
criterion-only encoding than the paper's additive figures suggest. This
is checkable against the trained-agent $\alpha$ trajectories in
`Prism/figures/avg_alpha_*.pdf` and the saliency analyses
(`Prism/analysis/avg_saliency_*.py`): the prediction is a small upward
bias in measured value-reallocation vs the additive normative baseline,
not a qualitative difference (both rules keep non-monotonic VDA, no
inversion, criterion-majority).

### Loose ends

- **CR-008 (designated second vector, replication, HIGH-promoted):** run
  the full multiplicative $(V,v,\text{variant})$ sweep restricted to the
  cells where additive CF $<0.60$ (run-003 phase-A output), to decide
  whether criterion dominance (CF $>0.5$) survives $\beta\gamma=1$
  globally or *breaks* — the one place A3 could move to CONTESTED.
- **Spawn (sensitivity):** does the C2 peak-shift direction
  ("left + up under $\beta\gamma=1$") persist across the $f_0$ and $h$
  secondary sweeps, where $\kappa(r)$ interacts with the CR-001
  $r^\dagger(v)$ escape thresholds?
- **Spawn (literature, low):** the $\beta\gamma=1$-vs-normalization point
  deserves a firsthand citation beyond the wiki's
  `reynolds_heeger2009_normalization` full entry — confirm whether any
  primate study has directly contrasted additive vs divisive
  conservation of attentional gain across locations.
- A third constraint family ($\beta+\gamma=$ const $\ne2$, or
  $\beta^p+\gamma^p=$ const) is untested; A3 as written only brackets the
  two the paper names.

### Wiki cross-references

(Mission §11 sweep — anchors in §11.1 plus A3-specific terms
{conservation, total/gain magnitude, divisive normalization,
multiplicative/additive gain, surround suppression, lateral inhibition,
zero-sum reallocation, resource competition}.)

- `[[reynolds_heeger2009_normalization]]` — cited in §Evidence / §Verdict:
  divisive (multiplicative) normalization makes $\beta\gamma=1$ the more
  mechanism-aligned conservation; substrate for §5.4's $r$ = gain-vs-
  suppression reading.
- `[[maunsell2015_attention_mechanisms]]` — cited: SDT sensitivity/criterion
  dissociation underlying the CF (C1) erosion finding.
- `[[luo_maunsell2018_criterion_sensitivity]]` — cited: reward asymmetry
  loads on criterion (β-side) vs sensitivity; bears on criterion dominance.
- `[[reynolds1999_competitive_v2_v4]]` — cited: competitive (zero-sum)
  reallocation, the additive-conservation analog in cortex.
- `[[desimone_duncan1995_biased_competition]]` — cited: biased-competition
  zero-sum framing behind §5.1.
- `[[coalition_resource_competition]]` (concept) — cited: the user's
  finite-resource-conservation program; frames "conserves total magnitude"
  and the PRISM implication.
- `[[carrasco2011_visual_attention_25y]]` — consulted; review-level
  gain-field account, subsumed by the Reynolds-Heeger citation; not
  separately load-bearing here.
- `[[bisley_goldberg2010_parietal_priority]]`, `[[bisley_mirpour2019_priority_map]]`,
  `[[rust_cohen2022_priority_coding]]` — consulted (priority-map anchor);
  concern *where* attention is allocated, not the conservation form —
  unrelated on inspection for this structural/numerical claim.
- dopamine/RPE/basal-ganglia (`glimcher2011_dopamine_rpe`,
  `dabney2020_distributional_dopamine`, `bolton2015_dopamine_sc`,
  `essig_felsen2016_dopamine_sc`), LIP (`roitman_shadlen2002_lip_rt`),
  FEF/SC (`moore_armstrong2003_fef_microstim`, `bollimunta2018_fef_sc_covert`),
  saccade/oculomotor — consulted (§11.1 anchors); these concern the
  *source/encoding* of value signals, not the structural form of the
  benefit/cost conservation constraint — unrelated on inspection.
- No floating-point / numerical-methods or "conservation-constraint
  comparison" literature exists in `research_db/` (expected gap; the
  attack is internal to the model + the Reynolds-Heeger mechanism point).

## Version 0.2 — 2026-05-24

### Previous frontmatter (v0.1, run-010)

```yaml
current_label: WEAKLY-SUPPORTED
attacks_tried:
  - vector: re-derivation
    run_id: run-010
    outcome: "robustness claim survived at the reference slice; non-monotonic
      VDA and no-inversion robust; criterion dominance survives but erodes to a
      thin margin (CF floor 0.601→0.507)"
last_updated: "2026-05-22"
```

### What this version did

**Attack vector: replication** (mission §3.2), the designated *second* vector
for A3 (CR-008, promoted to high by run-010). Where CR-040 (v0.1, re-derivation)
tested the βγ=1 swap on one reference slice (V=0.5, v=5, variant A) and found
criterion dominance eroding to a thin margin (CF floor 0.601→0.507), this run
attacks the open question that left A3 below CONFIRMED-CONDITIONAL: **does that
erosion push the criterion fraction strictly below 0.5 in the cells where it is
already most fragile under the additive rule the paper actually uses?**

Code / output: `Critique/replications/A3--multiplicative-conservation/cr008_cf_floor/`
(`cr008_run.py`, `output/results.json`, `output/run.log`, `README.md`, `notes.md`).

Design (mission §8.5 — one focused replication): take the **590 cells** of the
paper's 4,410-cell primary grid where run-003's additive C1 sweep found
**CF < 0.60** (the at-risk set $S$), recompute the additive CF (cross-check) and
compute the multiplicative CF ($\beta=\sqrt r$, $\gamma=1/\sqrt r$) on each, at
run-003's *exact* configuration ($N=4$, $d'_{\max}=2$, $f_0=0.5$, $\sqrt\cdot$;
A&S Φ; $\Delta c=0.05$; $\Delta\alpha=0.02\cup\{1/N\}$). A cheap full-grid
multiplicative sweep gives the global statistics and bounds flips outside $S$.

**Validation (all exact).** The local $\beta\gamma=1$ map is bit-identical to
run-010's parent script (max dev $0.0$); the recomputed additive CF reproduces
run-003's stored CF **bit-for-bit** over all 590 cells (max$|\Delta|=0.0$); and
$R(P3),R(P4)$ are confirmed family-independent (max$|\Delta|=0.0$), so only the
$R(P1)$ denominator moves between families. An independent from-scratch
re-implementation of the worst cell reproduced both numbers ($\text{CF}_\times=0.2309$,
$\text{CF}_+=0.3040$). The run is deterministic (re-run bit-identical).

**Findings.**

1. **$\text{CF}_\times \le \text{CF}_+$ uniformly**, $\Delta\text{CF}\in[-0.109,
   \,0.000]$ with **max exactly $0.0$** — $\beta\gamma=1$ never *raises* CF, and
   equals it only where the optimum stays at $\alpha^\star=1/N$ (no
   reallocation). This numerically confirms the v0.1 mechanism: since
   $(\beta,\gamma)_\times=\kappa(r)(\beta,\gamma)_+$ with $\kappa\ge1$, $\beta\gamma=1$
   amplifies reallocation wherever it already helps, raising $R(P1)$ and lowering
   the CF whose denominator it is.

2. **The criterion-subordinate region roughly doubles.** Over the full
   4,410-cell grid, cells with CF $<0.5$ grow from **177 (4.01 %)** under additive
   to **368 (8.34 %)** under multiplicative — **191 cells flip** from
   criterion-dominant to criterion-subordinate purely because of the constraint
   swap (0 recover). The minimum CF deepens from $0.304$ to $0.231$ at the same
   cell ($r=10$, $V=0.25$, $v=4$, variant B — the C1 argmin).

3. **But the central tendency is essentially unchanged:** median CF
   $0.7605\to0.7578$. The new failures are concentrated in the **benefit-dominant
   high-$r$ corner** ($r\gtrsim2.5$, predominantly variant B but including variant
   A at $r=10$) — the *same* corner C1 already contested under the additive rule,
   now deepened and widened, not relocated. The VDA peak (C2) lives at *low* $r$
   ($\approx0.3$) and is untouched, consistent with CR-040 finding C2 robust:
   criterion-dominance erosion and VDA non-monotonicity occupy opposite ends of
   the $r$-axis.

### Verdict

**Label: WEAKLY-SUPPORTED → CONTESTED.** A credible attack succeeded against
the *criterion-dominance* conjunct of the §5.5 robustness claim. The claim is
**not** robust to the conservation form as a per-cell / categorical statement —
the very statement the paper makes in §4.1 ("criterion adjustment is **always**
the single largest contributor to value-related reward"): switching to
$\beta\gamma=1$ roughly **doubles** the fraction of the paper's own grid where
criterion is *not* the larger contributor (CF $<0.5$), with 191 cells flipping.
Because these flips are *inside* the paper's stated 4,410-cell scope, this is
not a CONFIRMED-CONDITIONAL ("survives within scope, fails outside") — it fails
within scope. It is not REFUTED, because the substantive content survives as a
central-tendency claim (median CF unchanged at $\approx0.76$; $\approx92\%$ of
cells remain criterion-dominant under $\beta\gamma=1$) and the failures stay in
the benefit-dominant corner C1 already flagged.

This mirrors the agent's treatment of C1 and C3: a categorical/per-cell wording
is too strong, the substantive bulk finding survives, and a weaker
reformulation is proposed. **Proposed reformulation of §5.5 / §6:** of the three
qualitative findings §5.5 claims are robust to the conservation rule, two
(non-monotonic VDA, no inversion) are robust (CR-040), and criterion dominance
is robust *as a central-tendency statement* (median CF $\approx0.76$, $\approx92\%$
of cells criterion-dominant under both rules) but **boundary-sensitive**: under
$\beta\gamma=1$ the criterion-subordinate fraction roughly doubles
($4.0\%\to8.3\%$), concentrated in the benefit-dominant high-$r$ regime. The
manuscript should report criterion dominance as *typically* — not *always* —
the larger contributor, and note that the boundary of the criterion-dominant
region depends on the conservation form. This sharpening is consequential
because divisive normalization (`reynolds_heeger2009_normalization`,
`reynolds_chelazzi2004_attentional_modulation`) makes $\beta\gamma=1$ the *more*
biologically defensible rule, so the eroded boundary is not a worst-case
curiosity but arguably the more mechanistically apt regime.

The criterion-fraction *decomposition itself* (the metric being argued over)
rests on the empirically-grounded dissociation of attentional sensitivity and
criterion effects (`muller_findlay1987_sensitivity_criterion`,
`luo_maunsell2018_criterion_sensitivity`, `sridharan2017_sc_sensitivity_bias`):
both channels are real and separable, so "which captures the majority of the
value-related gain, and does that depend on the conservation rule" is a
well-posed empirical question — and the answer is "criterion usually, but the
margin and the exceptions depend on the rule."

### Evidence

- Replication: `Critique/replications/A3--multiplicative-conservation/cr008_cf_floor/`
  — full grid table, decomposition, validation checks, determinism re-run.
  Headline: additive CF$<0.5$ = 177/4410 (4.01 %), median 0.7605;
  multiplicative CF$<0.5$ = 368/4410 (8.34 %), median 0.7578; 191 new flips,
  0 recovered; $\Delta\text{CF}\in[-0.109,0.000]$; min CF$_\times$ = 0.231.
- Cross-validated against run-003's C1 sweep
  (`Critique/replications/C1--criterion-fraction-floor/output/results.json`):
  recomputed additive CF bit-identical (max$|\Delta|=0.0$).
- Mechanism from the v0.1 derivation
  (`Critique/derivations/A3--multiplicative-conservation.md`): rescaling theorem
  $(\beta,\gamma)_\times=\kappa(r)(\beta,\gamma)_+$, $\kappa(r)=\cosh(\tfrac12\ln r)\ge1$.
- `[[reynolds_heeger2009_normalization]]`, `[[reynolds_chelazzi2004_attentional_modulation]]`
  (the latter added to the citation set this version) — divisive
  (multiplicative) normalization makes $\beta\gamma=1$ the more mechanism-aligned
  rule; raises the stakes of the eroded boundary.
- `[[muller_findlay1987_sensitivity_criterion]]` (surfaced by this run's §11
  sweep; not cited in v0.1) — behavioural demonstration that spatial cueing
  produces dissociable sensitivity *and* criterion effects; the empirical
  grounding of the criterion-vs-reallocation decomposition CF measures.
- `[[luo_maunsell2018_criterion_sensitivity]]`, `[[sridharan2017_sc_sensitivity_bias]]`,
  `[[maunsell2015_attention_mechanisms]]` — the SDT criterion/sensitivity
  substrate; bear on the CF metric's interpretation.

### Implications for PRISM (mission §3.5)

This sharpens the v0.1 prediction. PRISM v1/v2 implement attention as FiLM — a
*multiplicative* per-location gain (`Prism/film.py`;
`reynolds_heeger2009_normalization` → `Prism/docs/THESIS.md` §2.4;
`perez2018_film`), i.e. PRISM sits on the $\beta\gamma=1$ side. The full-grid
result says: relative to the additive normative model, a multiplicative-gain
agent should show criterion capturing a *minority* of the value-related gain
(CF $<0.5$) roughly twice as often, **specifically in the benefit-dominant /
high-value-contrast regime** ($r$ large — strong cued benefit relative to uncued
cost). Concretely, in PRISM training conditions with high value contrast and a
strongly weighted cued location, the trained agent's value encoding should lean
*more* on $\alpha$-reallocation (attention) and *less* on pure criterion shift
than the paper's additive figures imply. This is checkable against
`Prism/figures/avg_alpha_*.pdf` (expect larger $\alpha$ toward the cued/high-value
location in high-contrast conditions) and the saliency analyses
(`Prism/analysis/avg_saliency_*.py`). The qualitative ceilings hold (no inversion;
non-monotonic VDA; criterion still usually the larger channel) — the difference
is a regime-localised shift in *which* mechanism dominates value encoding when
the benefit/cost asymmetry is large.

### Loose ends

- **CR-044 (spawn, sensitivity, low):** Δα=0.005 spot-check on the borderline
  flips (CF$_\times\in[0.48,0.50)$) to tighten the exact flip count by ±a few;
  the conclusion is grid-robust (ΔCF magnitudes 15–50× the grid error) but the
  precise "191" is grid-dependent at the unit level.
- **CR-042 (already queued, sensitivity):** does the doubling-of-failures pattern
  hold across the $f_0$ and $h$ secondary sweeps, or is it specific to $f_0=0.5,
  \sqrt\cdot$? $\kappa(r)$ interacts with $f'(1/N)$, so lower $f_0$ (larger
  reallocation gain) may erode CF further — pushing A3 from CONTESTED toward a
  stronger CONTESTED, or revealing the additive grid is the benign case.
- **Variant decomposition:** the new flips are predominantly variant B; a clean
  A-vs-B split of the criterion-subordinate fraction under each rule would say
  whether the conservation form matters more for value-coupled (A) or fixed (B)
  correct-rejection payoffs. (Cheap; fold into CR-042.)
- **Third constraint family** ($\beta^p+\gamma^p=$ const) still untested; A3 as
  written brackets only the two rules the paper names.

### Wiki cross-references

(Mission §11 sweep — §11.1 anchors plus A3/CF-specific terms {criterion,
signal detection, sensitivity, divisive/multiplicative/additive gain,
normalization, conservation, criterion dominance}.)

- `[[muller_findlay1987_sensitivity_criterion]]` — **cited (new this version)**:
  behavioural sensitivity-vs-criterion dissociation in spatial cueing; the
  empirical grounding for the CF decomposition the verdict argues over.
- `[[reynolds_chelazzi2004_attentional_modulation]]` — **cited (new this
  version)**: review carrying the `divisive-normalization` concept; reinforces
  (with Reynolds-Heeger) that $\beta\gamma=1$ is the more mechanism-aligned rule,
  which is what makes the eroded boundary consequential.
- `[[reynolds_heeger2009_normalization]]` — cited (carried from v0.1): divisive
  (multiplicative) normalization ⇒ $\beta\gamma=1$ more biologically apt.
- `[[luo_maunsell2018_criterion_sensitivity]]`, `[[sridharan2017_sc_sensitivity_bias]]`,
  `[[maunsell2015_attention_mechanisms]]` — cited: SDT criterion/sensitivity
  substrate underlying the CF metric and its erosion.
- `[[reynolds1999_competitive_v2_v4]]`, `[[desimone_duncan1995_biased_competition]]`
  — consulted (carried): zero-sum (additive-flavoured) competition; the
  conceptual analog of the rule the paper chose.
- `[[coalition_resource_competition]]` (concept) — cited (carried): the user's
  finite-resource-conservation framing; "conserves total magnitude" is a
  resource-conservation constraint and frames the PRISM implication.
- `[[cameron2002_covert_attention_contrast]]`, `[[lu_dosher1998_external_noise]]`,
  `[[prinzmetal2005_rt_vs_accuracy]]` — consulted (psychophysics of attention on
  sensitivity vs decision); bear on the reality of the sensitivity channel but
  add nothing beyond Müller & Findlay for this numerical claim — unrelated on
  inspection here.
- dopamine/RPE/basal-ganglia (`glimcher2011_dopamine_rpe`,
  `dabney2020_distributional_dopamine`, `bolton2015_dopamine_sc`), LIP/FEF/SC
  (`bisley_goldberg2010_parietal_priority`, `bisley_mirpour2019_priority_map`,
  `rust_cohen2022_priority_coding`, `moore_armstrong2003_fef_microstim`),
  saccade/oculomotor — consulted (§11.1 anchors); concern the *source/where* of
  value signals, not the structural form of the benefit/cost conservation
  constraint — unrelated on inspection (consistent with v0.1).
- No floating-point / "conservation-constraint comparison" literature in
  `research_db/` (expected gap; the attack is internal to the model).
