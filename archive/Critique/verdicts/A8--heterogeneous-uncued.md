---
type: verdict
claim_id: A8
claim_statement: "Homogeneous-uncued allocation — each uncued location gets exactly (1−α)/(N−1) — does not bias the paper's headline conclusions C1–C5."
paper_section: "§2.2 (assumption stated); not in the §5.5 limitations list"
current_label: CONFIRMED-CONDITIONAL
attacks_tried:
  - vector: replication
    run_id: run-012
    outcome: "claim survived — A8 is innocuous for C1–C5 (homogeneity is the optimum at every headline-relevant cell; constrained and unconstrained optima coincide). But A8 is NOT a trivially-free assumption: it binds under a forced benefit-dominant uncued budget, and relaxing it lets the model reproduce the Wang & Theeuwes suppression gradient."
  - vector: re-derivation
    run_id: run-013
    outcome: "claim survived (second distinct vector) — proved (a) homogeneity-optimality: equal split is always a critical point by exchange symmetry, restricted Hessian λ=λ_HR+λ_noFA, λ_noFA≤0 unconditionally (log-concavity of Φ) ⇒ λ<0 for concave/linear h (a^0.3,√a,a); only accelerating a^2 flips λ>0 on the smooth branch, and the forced-uniform-budget kink is a CUSP with one-sided slope sign(β−γ)=sign(r−1). (b) cued-absorption pre-emption: the value-weight inequality (w_c≥w_u under V≥1/N,v≥1) + C4 location-count asymmetry drive α*→1 fastest exactly for the accelerating h / benefit-dominant regimes that wanted to concentrate, so B=1−α*→0 and A8 never binds — max|ΔR(uncon−homog)|=1.4e-4 over all four h and all swept cells (=0 exactly for a^2). Conditional on equal uncued validity."
load_bearing_for: ["§2.2 model definition", "§2.5 policy decomposition (1-D α policy space)", "C1 criterion fraction", "C2 VDA non-monotonicity", "C4 no-inversion", "§5.2 experimental-design advice", "§6 conclusions"]
last_updated: "2026-05-24"
prompt_version_observed: "0.2"
---

# Verdict: Homogeneous-uncued allocation (A8) does not bias C1–C5

## Claim as written in the paper

Paper §2.2 (verbatim): *"The observer allocates attention $\alpha \in [0,1]$
to the cued location. The remaining attention is distributed equally among
uncued locations, so each receives $(1-\alpha)/(N-1)$. At uniform attention,
$\alpha = 1/N$ and all locations are treated identically."*

A8 is the assumption that the uncued budget $1-\alpha$ is split **equally**.
It makes the policy space **one-dimensional in $\alpha$** (plus two criteria),
which is what makes the §2.5 P1–P4 decomposition and the entire sweep
tractable. A8 is *implicit* — it is stated as a definitional choice in §2.2,
is **not** among the four limitations the paper lists in §5.5 (which name
A1 independence, A2 single-global-$r$, A3 additive conservation, A4
no-learning), and was surfaced as a load-bearing assumption by run-007/CR-031
and ratified into the mission at prompt v0.2.

## Why this matters

Downstream in the **paper**: every headline number (C1 criterion fraction,
C2 VDA-vs-$r$, C4 no-inversion) is computed by optimising over the 1-D
$\alpha$ policy. If the true (heterogeneous-allocation) optimum differed from
the homogeneous-constrained optimum, those numbers would be artefacts of the
restricted policy space. A8 also bounds the model's *empirical reach*: a model
that cannot represent unequal uncued weighting cannot speak to the large
statistical-learning-of-distractor-suppression literature (Wang & Theeuwes and
descendants), which measures exactly that.

Downstream in the **user's PRISM program** (§3.5): PRISM v1/v2 agents allocate
attention across a Posner-style change-detection display (`Prism/env.py`) with
**no homogeneity constraint** — the softmax over locations is free to be
heterogeneous. So PRISM is, architecturally, the A8-relaxed model. Whether
trained PRISM agents spread uncued attention homogeneously (as the normative
model's optimum does at its swept cells) or break homogeneity is directly
checkable against `Prism/figures/avg_alpha_trajectories_*.pdf` and
`avg_saliency_heatmap_*.pdf`.

## Version 0.1 — 2026-05-24

### What this version did

**Attack vector: replication** (`Critique/replications/A8--heterogeneous-uncued/`,
run-012). Built a general-$N$ optimal-observer model with an arbitrary
allocation vector $\mathbf a$ and validity vector $\mathbf w$ (location 0 =
cued), per-location sensitivities under the paper's $\beta/\gamma$ gain–loss
rule generalised to each location's own departure from the $1/N$ baseline
($s_i=\beta$ if $a_i\ge 1/N$ else $\gamma$ — the unique generalisation
consistent with the §2.3 "roles reverse" note), and per-location criteria
optimised exactly. It reduces identically to the paper's homogeneous model
(Eqs. 7–9). The criterion optimiser was **validated to machine precision**
against the C4 base optimiser (joint 2-D grid, $G\le2$: $\max|\Delta|=4.4\text{e-}16$,
including the previously-failing variant-B configs) and against a joint 3-D
grid ($G=3$: $\max|\Delta|=0$); see `notes.md` §2.

Three tests:

1. **VALIDATION.** The homogeneous model reproduces the headline numbers:
   C2 VDA peak $=0.0769$ at $r=0.398$ (paper Fig. 4 $\sim0.080$; run-010
   $0.0797$); C1 CF $=0.86/0.73/0.64$ at $r=0.3/1.0/3.2$ (matching run-003,
   including the known CR-022 $r=0.3$ transcription-error flag).

2. **Is homogeneity an OPTIMUM, not just an assumption?** Under *equal* uncued
   validity, fix the cued allocation at the homogeneous $\alpha^\star$ and scan
   the uncued split; also probe the curvature $R''(0)$ along the symmetric
   redistribution direction $[+1,+1,-2]$. **Result: equal-split is optimal in
   32/32 cells**, max $E[R]$ gain from any unequal split $=0.0$, with
   $R''(0)<0$ in every non-degenerate cell (e.g. $-2.26$ at $r{=}0.1$,
   value-blind). The **decisive test (Part 1c)** confirms it: the full
   unconstrained simplex optimum coincides with the homogeneous-constrained
   optimum at every headline-relevant cell (C2-reference, benefit-dominant
   $v{=}5$, the C1 contested corner): $a_{\text{cued}}^\star\to1$, uncued
   spread $=0$, $\Delta R$ within the $0.05$ allocation-grid slack. **So
   relaxing A8 leaves C1–C5 exactly unchanged.**

3. **But A8 is not a trivially-free assumption.** When a uniform cued
   allocation is **forced** ($\alpha=1/N$, giving every transfer form a real
   uncued budget, Part 1b), equal-split is *not* always optimal: **8/12 forced
   cells prefer to CONCENTRATE** the uncued budget ($R''(0)>0$, e.g. $+0.50$ to
   $+0.85$ at $r=2$ across all four $h$-forms). The pattern is mechanistic and
   is the **same $\beta/\gamma$ asymmetry that drives the whole paper**: the
   benefit-dominant regime ($r>1$, $\beta>\gamma$ ⇒ gains amplified, losses
   cheap) rewards a winner-take-all concentration; the cost-dominant regime
   ($r<1$, $\gamma>\beta$) rewards spreading ⇒ homogeneity. A8 is therefore a
   **genuine constraint that happens to be slack at the model's own optima**:
   wherever uncued-concentration is favoured ($r>1$), the cued allocation
   $a_{\text{cued}}^\star\to1$ first, so the uncued budget vanishes before the
   concentration tendency can bite (Part 1c confirms no cell binds).

4. **Relaxing A8 ENRICHES the model (heterogeneous validity).** Introduce one
   *anti-cued* slot (reduced target-validity $w_{\text{anti}}$) and jointly
   optimise the simplex, value-blind ($v=1$, $V=0.40$). The optimum reproduces
   a **graded suppression**: at $r=0.398$, $a_{\text{anti}}^\star$ falls
   monotonically $0.250\to0.220\to0.140\to0.010\to0.000$ as $w_{\text{anti}}$
   drops, going below the uniform baseline $1/N$ **and** below the
   higher-validity uncued slots, with the freed attention reallocated to the
   cued and "rest" slots. This matches the **Wang & Theeuwes (2018) spatial
   gradient of suppression** at low-target-probability locations and the
   Kong et al. (2020) reciprocity ("suppress here ⇒ more there"), and confirms
   in the affirmative the CR-031/run-007 conjecture that the model predicts
   $\alpha<1/N$ at anti-cued locations.

### Verdict

**WEAKLY-SUPPORTED.** This is the first run to touch A8; one attack vector
(replication) has been executed and it **failed to show that A8 biases the
headline conclusions**: under the paper's own equal-uncued-validity structure,
homogeneous allocation is the optimum (not merely an assumption) at every
swept cell, so the homogeneous-constrained and unconstrained optima coincide
and C1–C5 are exactly unchanged. Per mission §6 the verdict cannot elevate to
CONFIRMED-* on a single run/vector.

The support is **conditional in two precise senses** that the eventual label
should carry: (i) it holds *under equal uncued validity* — heterogeneous
validity is outside the model's scope, and relaxing A8 there produces a
suppression gradient the homogeneous model cannot represent (a scope
limitation, not a bias to C1–C5); (ii) the safety is a **structural
coincidence** of the benefit/cost-asymmetry mechanism (concentrate-favouring
$r>1$ ⇒ cued absorbs the budget), not a triviality — A8 *would* bind given a
forced benefit-dominant uncued budget. A re-derivation proving the
"uncued-concentration ⇒ cued-absorption" lemma in closed form is the
designated second vector; it would elevate A8 to **CONFIRMED-CONDITIONAL**
(conditional on equal uncued validity).

This is the **second assumption-layer verdict** (after A3) and, unlike A3
(CONTESTED), it is a *confirming* outcome for the paper's robustness: A8 is
the most defensible of the paper's simplifications because the optimiser would
make the same choice unprompted in the regimes the paper sweeps.

### Evidence

- Replication: `Critique/replications/A8--heterogeneous-uncued/run.py`,
  `output/results.json` (deterministic; re-run byte-identical, sha256
  `53e2d5f9…`), `README.md`, `notes.md`.
- Optimiser validation: machine-precision agreement with the C4 base optimiser
  (`Critique/replications/C4--no-inversion/run.py`) for $G\le2$ and with a
  joint 3-D grid for $G=3$.
- The empirical phenomenon Part 2 reproduces is
  [[wang_theeuwes2018_statistical_learning_distractor_suppression]] (abstract
  depth): *"a spatial gradient of suppression … scaled with the distance from
  the high-probability [distractor] location."*

### Loose ends

1. **Re-derivation (the designated second vector).** Prove analytically that
   (a) under equal uncued validity the equal split maximises $E[R]$ for
   concave-or-linear $h$ via Schur-concavity of the per-location reward, and
   (b) wherever the uncued subspace favours concentration ($r>1$), the cued
   allocation is driven to $a_{\text{cued}}^\star=1$, so A8 never binds at the
   model's own optimum. Elevates A8 → CONFIRMED-CONDITIONAL. → spawned **CR-045**.
2. **Finer-grid check of the one positive $\Delta R$** (V$=1/N$, $v=1$, $r=2$:
   $+6.8\text{e-}4$, within the $0.05$ simplex-grid slack, at the degenerate
   $V=1/N$ boundary where cued/uncued labels are meaningless, cf. CR-019).
   Pure resolution hygiene; does not move the verdict. → spawned **CR-046**.
3. **$N>4$ graded-neighbour suppression.** Part 2 used one anti-cued slot at
   $N=4$; a closer match to the Wang & Theeuwes *distance* gradient would put a
   graded validity profile across $N>4$ uncued locations. → spawned **CR-047**.
4. **Stub the Wang/Samara/Theeuwes 2019 + Kong 2020 follow-ups** (already
   queued as CR-035) so Part 2's gradient + reciprocity claims cite first-class
   wiki nodes rather than the abstract of the 2018 stub.

### Implications for PRISM v1/v2

The normative result is a concrete, falsifiable prediction for PRISM. The
A8-relaxed model says: **trained agents in the paper's swept regimes (moderate
$v$, $V\ge1/N$, cost-to-moderate $r$) should allocate uncued attention
*homogeneously*** — not because they are constrained to, but because equal
spreading is optimal there. PRISM's allocation is unconstrained
(`Prism/env.py` softmax over locations), so this is directly testable:
`Prism/figures/avg_alpha_trajectories_*.pdf` and `avg_saliency_heatmap_*.pdf`
should show roughly uniform weight across the non-cued / non-change locations
in the cued-trial conditions. **Two regimes where PRISM should break
homogeneity**, per Parts 1b/2: (i) if the learned benefit/cost asymmetry is
benefit-dominant ($r>1$-like — and note PRISM's FiLM gain is multiplicative,
the $\beta\gamma=1$ side flagged in the A3 verdict, which biases toward
stronger reallocation), trained agents should show **winner-take-all
concentration** rather than spreading; (ii) under any statistical regularity
that makes one location a reliable *non-target* (anti-cued), PRISM should learn
a **graded suppression** of that location — the Wang & Theeuwes signature — and
reallocate to the others (the zero-sum / biased-competition reciprocity that
the user's `concepts/coalition_resource_competition` frames as finite-resource
competition; lineage Desimone & Duncan 1995, Reynolds et al. 1999). A PRISM
run with a high-distractor-probability location would be the cleanest test, and
would also be the empirical bridge from the normative model to the user's
program.

### Wiki cross-references

- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] — **cited**
  (Evidence; Part 2): the empirical "spatial gradient of suppression" that the
  A8-relaxed optimum reproduces. The single most load-bearing wiki entry here.
- [[failing_theeuwes2018_selection_history]] — cited: selection-history review;
  the learning process that produces heterogeneous (anti-cued) validity.
- [[hickey2010_reward_salience_acc]] — cited: reward-driven priority that
  biases per-location weighting; complements the value side.
- [[bisley_mirpour2019_priority_map]], [[bisley_goldberg2010_parietal_priority]]
  — cited: the LIP **priority map** is the neural substrate of *per-location*
  (heterogeneous) allocation that A8 abstracts into a single scalar; the model's
  1-D $\alpha$ is a homogeneous projection of a genuinely $N$-dimensional map.
- [[koch_ullman1984_winner_takes_all]], [[itti_koch2001_saliency_review]] —
  cited: the saliency-map **winner-take-all** dynamic is precisely the
  benefit-dominant uncued-concentration tendency surfaced in Part 1b.
- [[desimone_duncan1995_biased_competition]], [[reynolds1999_competitive_v2_v4]],
  [[reynolds_heeger2009_normalization]] — cited: biased-competition / divisive
  normalization = the zero-sum reallocation (freed attention → other slots) seen
  in Part 2 and the Kong 2020 reciprocity.
- [[coalition_resource_competition]] (concept) — cited: the user's
  finite-resource competition framing of zero-sum allocation; the §3.5 PRISM
  bridge.
- [[stanisor2013_v1_value_attention]] — noted: high-$V$ value modulation;
  bears on the value side of heterogeneous priority but not central to A8.
- [[gupta_sridharan2024_presaccadic_change]] — unrelated on inspection for A8
  (a failure-of-facilitation result; relevant to C4, not the homogeneity of the
  uncued split).
- [[cohen_maunsell2009_correlations]] — unrelated on inspection for A8 (bears on
  A1 cross-location independence, a different assumption).
- Taxonomy gap (carried from the Wang & Theeuwes stub, surfaced to owner): the
  wiki has no `selection-history` / `statistical-learning-of-priority` concept;
  closest-fit `priority-map` was used. A8's suppression-gradient finding
  strengthens the case for adding one.
- §11.1 anchors searched and **unrelated on inspection** for A8: dopamine /
  RPE / basal-ganglia (value *source*, not allocation *geometry*), FEF / SC
  microstim (causal-manipulation foundation), V4 gain (within-RF, not
  across-location split), change-detection / Posner (task foundation, already
  established).

---

## Version 0.2 — 2026-05-24

### Previous frontmatter (preserved from Version 0.1)

```yaml
current_label: WEAKLY-SUPPORTED
attacks_tried:
  - vector: replication
    run_id: run-012
    outcome: "claim survived — A8 is innocuous for C1–C5 ... But A8 is NOT a trivially-free assumption: it binds under a forced benefit-dominant uncued budget, and relaxing it lets the model reproduce the Wang & Theeuwes suppression gradient."
last_updated: "2026-05-24"
prompt_version_observed: "0.2"
```

### What this version did

**Attack vector: re-derivation** (`Critique/derivations/A8--homogeneity-optimality.md`,
run-013; numerical corroboration independent of CR-036's `run.py` in
`Critique/replications/A8--heterogeneous-uncued/cr045_rederivation_check/`). This
is the **designated second vector** (A8 v0.1 Loose-end #1 / CR-045). It proves in
closed form the two propositions the CR-036 replication established only
numerically.

**Proposition (a) — homogeneity-optimality.** Under equal uncued validity the
uncued locations are exchangeable, so $\mathbb{E}[R]$ is a *symmetric* function
of the uncued allocation vector. Two consequences:

1. *Equal split is always a critical point* of the value function on the uncued
   simplex $\Delta_B$ — **exactly, for every $r$, every $h$** (a symmetric
   differentiable function has equal partials at the permutation-fixed point, so
   its simplex-tangent gradient vanishes). Numerically $\mathcal V'(0)=O(10^{-5})$
   to grid resolution.
2. The stabiliser is $S_{N-1}$, whose action on the zero-sum tangent space is the
   *irreducible* standard representation, so by Schur's lemma the restricted
   Hessian is a **single scalar** $\lambda I$ (derivation §2). Equal split is a
   strict local max iff $\lambda<0$. The closed form (derivation Eq. 2.4),
   $\lambda=\lambda_{\mathrm{HR}}+\lambda_{\mathrm{noFA}}$, **matches a
   fixed-criterion finite difference to 5 d.p.** across all four $h$ and
   $r\in\{0.398,0.5,1,2\}$. The correct-rejection term
   $\lambda_{\mathrm{noFA}}=Q[G^2g'^2(\log G)''+G G_d g'']\le0$
   **unconditionally** for concave/linear $h$, because $\Phi$ is **log-concave**
   ($(\log G)''<0$) — the no-FA channel is a pure spreading force. Hence
   $\lambda<0$ (equal split = strict local max) for the diminishing/linear forms
   $a^{0.3},\sqrt a,a$; only the accelerating $a^2$ gives smooth-branch
   $\lambda>0$ (numerically $+0.024$ to $+0.048$). This is the "Schur-concave for
   concave-or-linear $h$" result CR-045 asked for.

**The forced-uniform-budget kink, characterised exactly.** CR-036's
"$R''(0)>0$ in 8/12 forced cells" (the concentration finding) occurs at
$\alpha=1/N$, where the equal split puts every uncued slot *on* the
$\beta/\gamma$ kink ($\bar a=1/N$). The re-derivation shows this is a **cusp**,
not a curvature: $\mathcal V(t)=\mathcal V(0)+m|t|+O(t^2)$ with
$\operatorname{sign}(m)=\operatorname{sign}(\beta-\gamma)=\operatorname{sign}(r-1)$
(derivation §3). So at a forced uniform budget, equal split is a sharp max for
$r<1$ (cost-dominant, spreading) and a sharp min for $r>1$ (benefit-dominant,
winner-take-all) — the *same $\beta>\gamma$ asymmetry that drives the whole
paper*. The verification confirms the cusp signature directly: the one-sided
slope converges to a nonzero constant while the central second difference scales
as $1/\varepsilon$ (so CR-036's finite "$R''(0)$" magnitudes were
$\varepsilon$/grid artefacts of the cusp slope $m$, now replaced by the exact
first-order law).

**Proposition (b) — cued-absorption pre-emption.** A8 can bind only where the
uncued subspace favours concentration: the accelerating $h=a^2$, or the
benefit-dominant kink $r>1$. Both are subsets of the winner-take-all regime —
and by the **value-weight inequality** $w_c\ge w_u$ (C4 Eq. 6.4, holds under
$V\ge1/N,v\ge1$) plus the **location-count asymmetry** (only the cued slot
reaches $d'_{\max}$; the $N-1$ uncued must share), the cued slot is the strictly
better recipient of any winner-take-all dynamic, so it wins the budget first and
$\alpha^\star\to1$, $B=1-\alpha^\star\to0$ (derivation §4, reusing the C4
machinery). The two pressures are **perfectly anti-correlated**: the more $h$
accelerates (the more the uncued want a winner), the harder the optimum drives
$\alpha^\star\to1$ and *empties* the uncued budget. Decisive numerical check
(joint optimum over $(\alpha,\text{uncued winner share})$, from scratch, on the
paper's $\Delta\alpha=0.005$ grid): $\max|\Delta R_{\text{uncon}-\text{homog}}|
= 1.4\times10^{-4}$ across **all four $h$ and all swept regimes** (a coarse-grid
snap, negative); and for the accelerating $a^2$ — the only case with
proposition-(a) $\lambda>0$ — cued-absorption is *total* ($\alpha^\star=1$,
$B=0$ exactly, $\Delta R=0$ exactly). A8 never binds at the model's own optimum.

### Verdict

**WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL.** A second distinct attack vector
(re-derivation, run-013) has joined the first (replication, run-012) and failed
to falsify A8: both propositions go through analytically, with the closed forms
validated against independent finite differences. Per mission §3.1, elevation to
a CONFIRMED-* label is now licensed (two distinct vectors across two runs). The
label is **CONFIRMED-CONDITIONAL**, not CONFIRMED-UNDER-ATTACK, because the
no-bias result is *conditional* in two precise senses now proven rather than
asserted:

1. **Equal uncued validity.** The exchange-symmetry that makes equal-split a
   critical point breaks under heterogeneous uncued validity; there the model
   produces a graded suppression (CR-036 Part 2; Wang & Theeuwes signature).
   This is a **scope enrichment, not a C1–C5 bias** — the paper's model is
   defined only for equal uncued validity.
2. **The degenerate $V=1/N,\ v=1$ corner**, where $w_c=w_u$, cued/uncued labels
   are meaningless (cf. CR-019), and the forced kink at $r>1$ makes the model
   indifferent among single-winner policies. Value-blind, within grid slack
   (CR-036's $+6.8\times10^{-4}$ blip) — **vacuous for C1–C5** (resolution
   hygiene → CR-046).

This makes A8 the **best-defended of the paper's simplifications**: unlike A3
(CONTESTED — the $\beta\gamma=1$ swap changed a headline conjunct within the
grid), relaxing A8 changes nothing within the grid ($\Delta R\le1.4\times10^{-4}$),
because the optimiser would make A8's choice unprompted. The paper's *unnamed*
§2.2 simplification turns out benign; its *named* §5.5 limitation (A3) turned out
consequential.

### Evidence

- Re-derivation: `Critique/derivations/A8--homogeneity-optimality.md` (full
  LaTeX: exchange-symmetry critical-point proof §1; $S_{N-1}$/Schur scalar
  Hessian §2; closed-form $\lambda$ Eq. 2.4 + log-concavity sign §2.2; cusp law
  §3; cued-absorption §4 reusing C4 §6).
- Numerical corroboration (independent of CR-036's `run.py`):
  `Critique/replications/A8--heterogeneous-uncued/cr045_rederivation_check/`
  — `verify_curvature_and_absorption.py` (R'(0)≈0 critical point; smooth-branch
  λ<0; forced-kink sign(r−1); cued-absorption ΔR table) and
  `verify_closedform_lambda_and_kink.py` (analytic λ vs fixed-c finite diff,
  agree to 5 d.p.; 1/ε cusp scaling), with `output/*.log` transcripts.
- Reused machinery: `Critique/derivations/C4--no-inversion.md` §6 (value-weight
  inequality $w_c\ge w_u$; location-count asymmetry). The same inequality that
  forbids inversion (C4) forces cued-absorption (A8).
- The analytic load-bearing fact (**log-concavity of $\Phi$**) has no wiki
  literature substrate — an expected mathematical-methods gap (mirrors the C5
  floating-point gap).

### Loose ends

1. **CR-046** (finer-grid check of the $V=1/N,v=1,r=2$ $+6.8\times10^{-4}$
   corner) is now *explained* by §5.1: that corner is the vacuous degenerate
   boundary. CR-046 remains worthwhile pure resolution-hygiene but is downgraded
   — the re-derivation already shows the corner cannot affect C1–C5 (value-blind).
2. **CR-047** ($N>4$ graded-neighbour suppression matching the Wang & Theeuwes
   *distance* gradient) is unaffected and remains the natural enrichment task;
   it now also tests the §5-(2) heterogeneous-validity scope boundary at scale.
3. **A2 bridge.** Proposition (a)'s symmetry argument is specific to
   *homogeneous gain asymmetry* (a single global $r$). Under a heterogeneous
   $r_i$ (assumption A2), the uncued slots would no longer be exchangeable even
   at equal validity, and equal-split need not be a critical point. The A8
   re-derivation thus sharpens the A2 question: A2 and A8 interact, and a
   heterogeneous-$r$ extension is the natural next assumption-layer arc. → noted
   for CR-006/CR-007 (A1/A2) sequencing.
4. **Taxonomy gap (carried).** No `selection-history` /
   `statistical-learning-of-priority` concept in the wiki; and no math-methods
   tag for log-concavity / Schur-majorization. Surfaced to owner; not agent-
   editable per §4.2.

### Wiki cross-references (Version 0.2 sweep)

- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] — **cited**
  (carried from v0.1): the heterogeneous-validity enrichment (§5-(2)) reproduces
  its suppression gradient; the scope boundary of the equal-validity conditional.
- [[koch_ullman1984_winner_takes_all]], [[itti_koch2001_saliency_review]] —
  **cited**: the WTA dynamic is precisely the concentration pressure
  (accelerating $h$ / benefit-dominant kink) that proposition (b) shows is
  pre-empted by cued-absorption. (`tsotsos1988_complexity_vision` surfaced this
  sweep as an additional WTA-complexity entry — noted, not load-bearing.)
- [[desimone_duncan1995_biased_competition]], [[reynolds1999_competitive_v2_v4]],
  [[reynolds_heeger2009_normalization]] — **cited**: zero-sum reallocation /
  divisive normalization = the budget-conservation backdrop of cued-absorption
  (the freed budget goes to the cued slot).
- [[luo_maunsell2018_criterion_sensitivity]], [[maunsell2015_attention_mechanisms]],
  [[sridharan2017_sc_sensitivity_bias]], [[muller_findlay1987_sensitivity_criterion]]
  — **cited**: the SDT criterion/sensitivity substrate behind the HR vs no-FA
  decomposition of $\lambda$ (the criterion channel is where $\lambda_{\mathrm{HR}}$
  lives; the no-FA channel is the spreading force).
- [[bisley_mirpour2019_priority_map]], [[bisley_goldberg2010_parietal_priority]],
  [[rust_cohen2022_priority_coding]] — **cited**: the LIP priority map is the
  $N$-dimensional per-location substrate that A8 projects onto a scalar; the
  re-derivation says that projection is *lossless for behaviour* in the swept
  regimes (equal-split is the optimum) but lossy under heterogeneous validity.
- [[coalition_resource_competition]] (concept) — **cited**: the user's
  finite-resource / zero-sum framing; cued-absorption is "the highest-priority
  coalition member captures the shared resource," the §3.5 PRISM bridge.
- [[cohen_maunsell2009_correlations]] — noted: bears on A1 (cross-location
  independence), the assumption that interacts with A8 under heterogeneity; not
  central here.
- **Mathematical-methods gap (no wiki substrate):** log-concavity of $\Phi$,
  Schur-concavity / majorization, the $S_{N-1}$ standard-representation argument
  — no `papers/` or `concepts/` entry (the lone "Schur" grep hit is
  *Schurgin*, a WM-precision author, unrelated). Expected gap, mirrors the C5
  floating-point gap; flagged, not filled.
- §11.1 anchors searched and **unrelated on inspection**: dopamine / RPE /
  basal-ganglia (value source, not allocation geometry), FEF / SC microstim
  (causal foundation), V4 within-RF gain (not across-location split),
  change-detection / Posner (task foundation), `gupta_sridharan2024` (a C4
  failure-of-facilitation result).
