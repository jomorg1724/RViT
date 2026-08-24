---
type: verdict
claim_id: A2
claim_statement: "The benefit/cost asymmetry is governed by a single global ratio r; the paper's reliance on it does not bias the headline conclusions C1–C5."
paper_section: "§2.4 (assumption stated, Eqs. 5–6); §5.4 (biological interpretation); §5.5 (named limitation)"
current_label: CONFIRMED-CONDITIONAL
attacks_tried:
  - vector: literature
    run_id: run-014
    outcome: "premise refuted, headline-safety partially confirmed. The empirical premise (a single global r) is decisively false — the benefit:cost asymmetry is location-/eccentricity-specific (reynolds_heeger2009; mcadams_maunsell1999 V1-vs-V4 3× gradient; carrasco2011 eccentricity sign-reversal), feature-specific (treue_martinez_trujillo1999 feature-similarity gain), and time-varying (sani2017; ghose_maunsell2002); the paper concedes this in §5.4/§5.5. BUT under the between-preparation reading (R1), which the paper's 100-fold r-sweep operationalises and §5.4 explicitly adopts, the simplification is benign and the r-indexed headline claims are unaffected. The within-display reading (R2) is empirically real but its consequence for C1–C5 is unresolved → CR-048."
  - vector: re-derivation
    run_id: run-015
    outcome: "R2 consequence shown BOUNDED — no headline claim shifted. The A2×A8 interaction: a per-location r_i breaks the uncued exchange symmetry A8's optimality proof needs (CR-045 §1), so equal-split is generically NOT a critical point (tangent gradient ∝ spread of γ_i, verified ‖g−mean‖=0.072 at ±30% vs 0 at homogeneity). BUT (i) the restricted Hessian stays negative-definite on the smooth branch (log-concavity of Φ is r-independent), so the optimal allocation tilt and its reward are 2nd-order in var(r_i): max ΔR=1.5e-4 over all interior cells at ±30% (= the CR-045 homogeneous slack); (ii) cued-absorption pre-emption (C4 §6, structurally r-independent) empties the uncued budget (α*→1) at every value-contrast cell (ΔR=0 exactly at the C2 headline cell) and the cost-dominant kink keeps equal-split optimal at P3 (ΔR=0, so CF untouched); (iii) the LEVEL effect (A8 imposed) leaves C2's non-monotonic VDA peak essentially fixed (0.0771→0.0770, r_peak=0.398) — C2 REFRAMES in r_cued, run-014 conjecture confirmed — C4 robust (r-independent geometry), C1 contested corner not deepened (0.3040→0.3055). Two vectors now agree: single-r reliance is safe for C1–C5 conditional on equal uncued validity + moderate spread."
load_bearing_for: ["§2.4 benefit/cost model", "C2 VDA-vs-r non-monotonicity (the r-axis itself)", "C3 narrow-regime (moderate r)", "C4 no-inversion (r-independent in structure)", "A8 homogeneity-optimality (proved A2-conditional by CR-045/run-013)", "§5.2 experimental-design advice", "§5.4 biological interpretation of r"]
last_updated: "2026-05-24"
prompt_version_observed: "0.2"
# Previous frontmatter (v0.1, run-014): current_label was WEAKLY-SUPPORTED with a
# single literature attack (run-014); elevated to CONFIRMED-CONDITIONAL at v0.2
# (run-015) by the re-derivation second vector.
---

# Verdict: the single global asymmetry ratio r (A2)

## Claim as written in the paper

Paper §2.4 (verbatim): *"We parameterize the asymmetry between attentional
benefit and cost with a ratio $r>0$. When a location gains attention
relative to the uniform baseline, its $d'$ departure from baseline is scaled
by $\beta(r)$. When a location loses attention, the departure is scaled by
$\gamma(r)$:"* with $\beta(r)=2r/(r+1)$, $\gamma(r)=2/(r+1)$, *"These satisfy
$\beta+\gamma=2$ ... and $\beta/\gamma=r$. The ratio $r$ reflects the relative
efficacy of attentional enhancement versus suppression."* The benefit is
attributed to "top-down feedback from frontal eye fields and intraparietal
cortex" and the cost to "lateral inhibition and surround suppression"
(§2.4, refs [11–14]).

A2 is the assumption that **one** $r$ governs **every** location, **every**
feature, and the **whole trial** simultaneously. The paper names it as a
limitation in §5.5 (verbatim): *"the asymmetry ratio $r$ is a single global
parameter; real neural circuits may have location-specific, feature-specific,
or time-varying asymmetries."* It also concedes in §5.4 that *"empirical
measurements of attentional benefits and costs ... are often asymmetric and
depend on task parameters such as stimulus-onset asynchrony, eccentricity, and
set size [8,13,18]—could in principle locate specific experimental preparations
in the model's parameter space."*

**Two readings (decisive for this verdict).**

- **R1 — between-preparation:** $r$ is one constant *per preparation*,
  differing across preparations. The primary sweep $r\in[0.1,10]$ (100-fold)
  *is* the handling of R1; all of C1–C5 are stated as functions of, or across,
  $r$. §5.4 takes R1 explicitly.
- **R2 — within-display homogeneity:** one $r$ for all $N$ locations / all
  features / the whole trial at once. The model cannot represent per-location
  $r_i$, per-feature $r$, or $r(t)$. This is the form A2 actually asserts.

## Why this matters

Downstream in the **paper**: $r$ is the abscissa of the paper's most
distinctive finding (C2, VDA non-monotonic in $r$, peaking $r\approx0.3$), the
"moderate $r$" leg of the narrow-regime recipe (C3), and the parameter the
no-inversion proof (C4) is claimed to hold "regardless of." If the operative
$r$ were not a single number but a vector $r_i$ across the display, "VDA vs
$r$" would not even be a well-defined univariate curve, and the policy
decomposition would inherit nuisance parameters the sweep never explored.

Downstream in the **user's PRISM program** (§3.5): PRISM v1/v2 implement
attention as per-location, per-channel FiLM gain (`Prism/film.py`,
Reynolds-Heeger-style), with **no constraint that enhancement and suppression
share one global ratio**. PRISM is therefore architecturally the *A2-relaxed*
model, exactly as run-012/013 found it to be the *A8-relaxed* model — and the
two relaxations are coupled (a heterogeneous learned $r_i$ would itself break
the uncued exchangeability A8's optimality proof needs). Whether trained PRISM
agents exhibit a single effective benefit:cost ratio across the display or a
location-dependent one is checkable against `Prism/figures/avg_alpha_*.pdf` and
`Prism/analysis/avg_saliency_*.py`.

## Version 0.1 — 2026-05-24

### What this version did

**Attack vector: literature** (`Critique/evidence/A2--single-global-r.md`,
run-014, CR-007). A §11 sweep of the gain-modulation / normalization /
surround-suppression / feature-attention / temporal-attention cluster, reading
eight full-depth wiki entries that bear directly on whether the benefit:cost
asymmetry is one scalar. No web fetch needed (0 of 2 soft cap).

The evidence partitions cleanly along the R1/R2 split:

**The premise (single global $r$) is empirically false under R2 — four
independent axes of heterogeneity, all already in the wiki:**

1. **Location / eccentricity / configuration.** The normalization model
   ([[reynolds_heeger2009_normalization]]) derives that the *same* attentional
   gain yields contrast-gain or response-gain depending on the
   stimulus-size/RF-size ratio — the benefit:cost *form* is configuration-set.
   [[mcadams_maunsell1999_v4_tuning]] measures a *threefold* gain gradient
   (V1 ≈8%, V4 ≈26%) under identical task/stimulus — area/eccentricity-specific
   magnitude. [[carrasco2011_visual_attention_25y]] reports the strongest form:
   attention *helps* at some eccentricities and *hurts* at others
   (Yeshurun-Carrasco texture-segmentation) — a *sign reversal*, not merely a
   changing scalar.
2. **Feature.** [[treue_martinez_trujillo1999_feature_attention]]'s
   feature-similarity-gain model: gain runs continuously from enhancement
   (matched feature) to suppression (anti-preferred), applied globally — so a
   single display carries enhancement and suppression at different feature
   channels simultaneously.
3. **Time.** [[sani2017_temporal_v4_gain]] (gain *form* cycles
   contrast→response→contrast within one trial) and
   [[ghose_maunsell2002_task_timing]] (gain *magnitude* tracks the within-trial
   event-probability schedule; same neuron, different profiles).
4. **Mechanism multiplicity.** [[maunsell2015_attention_mechanisms]] (Key
   claim 9): "attention" is a *family* of partly-independent mechanisms "each
   with its own task dependence," and [[reynolds_chelazzi2004_attentional_modulation]]
   documents contrast- and selectivity-dependence of the gain. The single
   scalar $r$ coupling one benefit to one cost idealises a multi-substrate
   reality.

This is not a contrarian reading: it is the paper's own §5.5 sentence, and
the §5.4 [8,13,18] concession, vindicated by the primary literature the paper
cites ([11–14] *is* the Maunsell-lab dissociable-mechanisms cluster).

**But the headline-safety question splits by reading:**

- **Under R1 the simplification is benign and methodologically correct.**
  A fixed preparation has fixed geometry/SOA/eccentricity → one effective
  regime → one $r$. The 100-fold sweep covers wherever any preparation lands,
  and C1–C5 are $r$-indexed statements, so between-preparation heterogeneity
  changes *which point on the swept axis* a preparation occupies, not the
  truth of any claim. [[reynolds_chelazzi2004_attentional_modulation]]'s stable
  "~50%-effective-contrast" benefit and [[mcadams_maunsell1999_v4_tuning]]'s
  within-cell label-preserving single multiplier are the positive evidence that
  a per-preparation scalar $r$ is a *reasonable* idealisation. This is real
  confirmation, not a hedge: the paper's named limitation is, in its dominant
  reading, already discharged by the methodology.

- **Under R2 the simplification is empirically contraindicated, and the
  consequence for C1–C5 is the genuine open question.** A first-pass structural
  analysis (not a settled result — flagged for CR-048):
  - *C2* (non-monotonic VDA in $r$): the two-limit mechanism (CR-001/CR-040)
    turns on the *cued* location's $\beta\to0$ as its ratio $\to0$ and on the
    value-blind policy saturating as the ratio $\to\infty$. With $r_i$
    heterogeneous, "VDA vs $r$" is ill-posed as a univariate curve, but the
    non-monotonicity in the *cued* location's $r_\text{cued}$ (uncued $r_i$ as
    nuisance parameters) plausibly survives — a **reframing**, not a refutation.
  - *C4* (no inversion): the CR-004/run-006 proof rests on the *location-count
    asymmetry* (only the cued slot reaches $d'_{\max}$) and the value-weight
    inequality $w_c\ge w_u$, both **structurally $r$-independent**.
    Heterogeneous $r_i$ rescales departure magnitudes but not the geometry, so
    C4 is likely robust.
  - *C1* (criterion fraction): heterogeneous $r_i$ moves the attention-side
    reward gain; since C1 is already CONTESTED (boundary-sensitive) and A3
    showed CF is sensitive to the gain *form*, R2 could plausibly deepen the
    contested corner. Central tendency likely survives.

### Verdict

**Label: WEAKLY-SUPPORTED** (first vector, first touch; per mission §3.1/§6 a
single attack cannot elevate to CONFIRMED-*). The label attaches to the
operative question — *is the paper's reliance on a single global $r$ safe for
its headline conclusions?* — **not** to the empirical truth of the premise
(which is false under R2). The reasoning:

- The single-$r$ idealisation is **provably safe under R1** (the dominant,
  paper-endorsed reading): the $r$-sweep *is* the between-preparation handling,
  and the headline claims are $r$-indexed. This is why the verdict is supported
  rather than contested.
- It is **empirically contraindicated under R2**, and the within-display
  consequence for C1–C5 is **unresolved** — which is why the support is *weak*
  and *conditional*, pending the CR-048 re-derivation.

This mirrors the project's first-vector discipline (C3, C4, C5, A8 all entered
at WEAKLY-SUPPORTED after one vector). It does **not** go straight to CONTESTED
(unlike C1) because no attack this run *succeeded in shifting a headline claim*:
the between-preparation reading is benign and the within-display reading is
merely shown to be empirically motivated, not yet shown to be consequential.

**Comparison to the sibling assumption verdicts (the emerging referee theme).**
A2 sits between A3 and A8. A3 (conservation *form*, named in §5.5) went
CONTESTED because a within-scope alternative ($\beta\gamma=1$) shifted a
headline conjunct. A8 (allocation *homogeneity*, *unnamed*) went
CONFIRMED-CONDITIONAL because the optimiser makes A8's choice unprompted. A2
(asymmetry *uniformity*, named in §5.5) is, so far, the *most R1-defensible*
named simplification — the methodology already addresses its dominant reading —
with the residual risk localised to within-display heterogeneity, which is
precisely the A2×A8 coupling CR-045/run-013 exposed.

### Evidence

- `Critique/evidence/A2--single-global-r.md` (V0.1) — full dossier, eight
  full-depth entries classified by R1/R2 direction.
- Premise-false (R2): [[reynolds_heeger2009_normalization]],
  [[treue_martinez_trujillo1999_feature_attention]],
  [[maunsell2015_attention_mechanisms]], [[sani2017_temporal_v4_gain]],
  [[ghose_maunsell2002_task_timing]], [[carrasco2011_visual_attention_25y]],
  [[reynolds_chelazzi2004_attentional_modulation]],
  [[mcadams_maunsell1999_v4_tuning]].
- R1-benign / per-preparation-scalar reasonable:
  [[reynolds_chelazzi2004_attentional_modulation]] (~50%-contrast stability),
  [[mcadams_maunsell1999_v4_tuning]] (within-cell label-preserving multiplier).
- Paper's own concessions: §5.4 ([8,13,18] task-parameter dependence), §5.5
  (the verbatim A2 limitation).

### Loose ends

1. **The decisive question is a re-derivation, not a literature one**
   (→ **CR-048**, already spawned by run-013, here promoted to the designated
   A2 second vector). Let $r$ be a per-location vector $r_i$. (a) Is equal-split
   still a critical point of the uncued simplex? (Generically *no* — the
   exchange symmetry A8 (CR-045 §1) relied on is broken even at equal validity,
   which is the A2×A8 interaction.) (b) Does the deviation scale with
   $\mathrm{var}(r_i)$, and is it bounded by the cued-absorption pre-emption
   (CR-045 §4)? (c) Does a plausible spread (e.g. $\pm30\%$ around the global
   $r$) move any C1/C2 headline number beyond the $1.4\times10^{-4}$ slack
   CR-045 found for the homogeneous case? Outcome → A2 CONFIRMED-CONDITIONAL (if
   R2 is also bounded) or CONTESTED (if it shifts a headline claim).
2. **C2 reframing under heterogeneous $r$.** A focused replication/derivation:
   define VDA vs $r_\text{cued}$ holding the uncued $r_i$ fixed at a few
   spreads, and test whether the non-monotonic peak persists and how it moves
   with $\mathrm{var}(r_\text{uncued})$. (Spawn-candidate; lower priority than
   CR-048.)
3. **Sign-reversal regime** (Carrasco/Yeshurun): the model assumes the benefit
   is always $\ge$ baseline at the gaining location ($\beta\ge0$). At
   eccentricities where attention *hurts*, the effective $\beta$ is negative —
   outside the model's $r>0$ parameterisation entirely. Worth a one-line note in
   any §5.4 reformulation: the model's $r>0$ excludes the documented
   attention-impairs-segmentation regime. (Spawn-candidate, low.)
4. **A firsthand feature-specific-vs-spatial asymmetry citation.** The dossier
   leans on review-depth synthesis for the multiplicity claim; a firsthand
   primate paper contrasting spatial and feature gain magnitudes
   (e.g. Martínez-Trujillo & Treue 2004) would upgrade the R2 evidence from
   review- to primary-depth. (Spawn-candidate, low; ≤1 fetch — overlaps the
   long-standing CR-016 maunsell_treue2006 stub task.)

### Implications for PRISM v1/v2

PRISM's FiLM gain is per-location/per-channel with no global-ratio constraint,
so PRISM is the A2-relaxed model. Three predictions follow, all checkable
against existing artefacts: (i) trained PRISM agents' learned
enhancement-vs-suppression need **not** have a single effective ratio across
the display — `avg_saliency_*` maps should show eccentricity-/location-dependent
benefit:cost profiles (Reynolds-Heeger configuration-dependence, McAdams-Maunsell
gradient). (ii) Because a heterogeneous learned $r_i$ breaks the uncued
exchangeability A8's optimality proof needs, PRISM's homogeneous-uncued-spread
prediction (run-012/013) is itself *A2-conditional*: if PRISM learns
heterogeneous $r_i$, its uncued allocation may be heterogeneous even at equal
validity. (iii) Given PRISM's recurrence, the learned gain should be
time-varying within a trial (Sani 2017 / Ghose-Maunsell), so a single
`avg_alpha` snapshot understates the dynamics — the trajectory, not the
endpoint, is the right comparison. This makes A2 the assumption where the
normative model and PRISM diverge most sharply: the paper *assumes away* exactly
the heterogeneity PRISM is free to learn.

### Wiki cross-references

- [[reynolds_heeger2009_normalization]] — cited (lead R2-constraint:
  configuration-dependent gain form; lead R1-confirm: fixed geometry → one
  regime).
- [[treue_martinez_trujillo1999_feature_attention]] — cited (feature-axis R2
  refutation; feature-similarity gain).
- [[maunsell2015_attention_mechanisms]] — cited (hierarchy gradient +
  mechanism-multiplicity; the review behind the paper's [11–14]).
- [[sani2017_temporal_v4_gain]] — cited (time-axis R2: gain *form* non-stationary
  within trial).
- [[ghose_maunsell2002_task_timing]] — cited (time-axis R2: gain *magnitude*
  tracks event time).
- [[carrasco2011_visual_attention_25y]] — cited (eccentricity-axis R2,
  sign-reversal; grounds §5.4 [8,13,18]).
- [[reynolds_chelazzi2004_attentional_modulation]] — cited (contrast/selectivity
  dependence R2; ~50%-contrast stability R1).
- [[mcadams_maunsell1999_v4_tuning]] — cited (within-cell single multiplier R1;
  V1-vs-V4 3× gradient + cell-to-cell heterogeneity R2).
- [[luo_maunsell2018_criterion_sensitivity]] — cited (benefit/cost have distinct
  substrates; bridge to A1/A6).
- [[mcadams_maunsell1999_reliability]] — consulted; reliability/variance channel,
  A1-adjacent; noted not load-bearing for the uniformity question.
- [[reynolds1999_competitive_v2_v4]], [[moran_desimone1985_selective_attention]],
  [[desimone_duncan1995_biased_competition]] — consulted; ground the $\gamma$
  (cost/competition) side and the $r<1$ surround-suppression regime; cited in
  passing, not load-bearing for single-vs-heterogeneous $r$.
- [[moore_armstrong2003_fef_microstim]] — consulted; causal source of the
  $\beta$ (top-down-feedback) side; confirms the mechanism, silent on its
  uniformity. Noted.
- [[sridharan2017_sc_sensitivity_bias]], [[muller_findlay1987_sensitivity_criterion]],
  [[cohen_maunsell2009_correlations]] — consulted; SDT sensitivity/criterion +
  noise-correlation channels; A1/A6-adjacent, tangential to A2.
- [[failing_theeuwes2018_selection_history]], [[hickey2010_reward_salience_acc]],
  [[stanisor2013_v1_value_attention]] and the dopamine/RPE/basal-ganglia entries
  — value *source*, not asymmetry *form*; **unrelated on inspection** for A2.
- [[bisley_goldberg2010_parietal_priority]], [[bisley_mirpour2019_priority_map]],
  [[rust_cohen2022_priority_coding]] — priority map sets *where*, not the
  benefit:cost ratio; unrelated to the $r$-uniformity question.
- concept [[coalition_resource_competition]] — the finite-resource/zero-sum
  framing behind $\beta+\gamma=2$ and the PRISM bridge; cited for §3.5.
- §11.1 anchors *change detection / Posner cueing / cue validity*
  ([[posner1980_orienting]]) and *oculomotor / saccade* — task-foundation and
  premotor-overlap; not about $r$-heterogeneity; noted, unrelated on inspection.

## Version 0.2 — 2026-05-24

### What this version did

**Attack vector: re-derivation** (`Critique/derivations/A2xA8--heterogeneous-r-allocation.md`,
run-015, CR-048) with independent numerical corroboration
(`Critique/replications/A2xA8--heterogeneous-r/`). This is the **second distinct
attack vector** on A2 and the designated decider after the v0.1 literature attack
left the within-display (R2) consequence for C1–C5 unresolved. It attacks the
**A2×A8 interaction**: A8's homogeneity-optimality proof (CR-045/run-013) rests on
the uncued slots being *exchangeable*, which requires not just equal validity but
a **single global $r$**. The decisive question is whether a per-location ratio
vector $r_i$ (the R2 heterogeneity, empirically established in v0.1) makes the
optimal allocation deviate from equal-split *enough to shift a headline number*.

The result is **bounded — no headline claim is shifted by R2 heterogeneity**, on
three legs:

1. **Criticality breaks, as expected, but only to first order in the spread.**
   With distinct $r_i$, $\mathbb E[R]$ is no longer a symmetric function of the
   uncued allocations, so the $S_{N-1}$ argument fails and equal-split is
   *generically not a critical point*: the uncued tangent gradient is
   $g_i^T=g_i-\bar g$ with $g_i\propto\gamma_i\rho\cdot M_i$ depending on slot $i$
   only through $r_i$ (derivation Eq. 1.2), zero iff all $r_i$ equal. Verified
   numerically: $\|g^T\|=7.2\times10^{-2}$ at ±30% spread vs exactly $0$ at
   homogeneity. The optimum tilts budget *toward the more cost-dominant
   (smaller-$r_i$) uncued slots* — it recovers the locations that lose the most
   $d'$ under deprivation.

2. **But the deviation is second-order in $\mathrm{var}(r_i)$ and tiny.** The
   restricted Hessian stays negative-definite on the smooth $\gamma$-branch by the
   *same* log-concavity-of-$\Phi$ argument as CR-045 §2.2, applied per slot — the
   correct-rejection spreading force $\lambda_{\mathrm{noFA},i}\le0$ is
   **$r$-independent in sign**. So the optimal tilt is $O(\text{spread})$ and the
   reward it buys is $O(\mathrm{var}\,r_i)$. Measured across interior (value-blind,
   non-absorbed) cells with a fine simplex search: **$\max\Delta R=1.50\times10^{-4}$
   at ±30% — exactly the CR-045 homogeneous-case grid slack.** Relaxing A8 under
   heterogeneous $r$ moves nothing beyond grid resolution.

3. **Cued-absorption pre-emption is $r$-independent.** The C4 mechanism
   ($w_c\ge w_u$ from validity/value + the location-count asymmetry that only the
   cued slot reaches $d'_{\max}$) has no $r$ in it, so at every value-contrast cell
   the budget is cued-absorbed ($\alpha^\star\to1$, $B\to0$) and the uncued
   heterogeneity is moot. Verified: at the C2 headline cell ($V{=}0.5,v{=}5$) even
   the cost-dominant $r_{\text{cued}}=0.4$ gives $\alpha^\star=1$, $\Delta R=0$
   exactly. And at the cost-dominant kink (P3, $\alpha=1/N$) the per-slot spreading
   force keeps equal-split optimal under heterogeneity ($\Delta R=0$ across all
   spreads), so the **criterion fraction is untouched** by the A8-relaxation.

**Level effect (A8 imposed, the run-014 reframing question).** Holding the
homogeneous allocation and spreading the uncued $r_i$: C2's non-monotonic VDA peak
is essentially fixed ($0.0771\to0.0770$, $r_{\text{peak}}=0.398$ under ±30%; even
$k=1.5/3$ spreads keep it $0.0765$–$0.0798$ @ $r_{\text{cued}}\approx0.36$). **C2
reframes cleanly** as a statement about the *cued* ratio $r_{\text{cued}}$ — the
run-014 conjecture, now numerically confirmed. C4 is robust (its proof is
$r$-independent geometry). C1's already-contested corner ($r{=}10,V{=}0.25,v{=}4$,B)
is *not* deepened ($\text{CF}\ 0.3040\to0.3055$ under ±30%). Validation: at spread
$0$ the heterogeneous code reproduces the single-$r$ model exactly (C2 peak
$0.0771$@$0.398$; C1 CF $0.866/0.729/0.640$ — matching run-003/010/012 and the
CR-022 transcription-error flag).

### Verdict

**Label: WEAKLY-SUPPORTED → CONFIRMED-CONDITIONAL.** Two distinct attack vectors
(literature, run-014; re-derivation, run-015) have now failed to falsify the
*operative* claim — *the paper's reliance on a single global $r$ does not bias its
headline conclusions C1–C5*. The elevation is to CONFIRMED-**CONDITIONAL**, not
CONFIRMED-UNDER-ATTACK, for two honest reasons:

- The **empirical premise is false** under within-display heterogeneity (R2,
  established in v0.1). The verdict confirms *safety despite a false premise*, not
  the premise — so a bare "confirmed" would mislead.
- The safety is **conditional**, and the conditional is now spelled out precisely:
  it holds *within the swept regimes* conditional on **(i) equal uncued validity**
  (heterogeneous validity is a scope enrichment — graded anti-cued suppression,
  CR-036 Part 2 / Wang & Theeuwes — not a C1–C5 bias) and **(ii) a moderate spread
  of the per-location $r_i$** (the deviation is $O(\mathrm{var}\,r_i)$; an extreme
  spread is untested and could in principle matter). It also presupposes that
  $r_{\text{cued}}$ is the operative abscissa for C2 — which the reframing
  vindicates.

This places A2 alongside A8 (also CONFIRMED-CONDITIONAL, also conditional on equal
validity) and completes the A2/A3/A8 heterogeneity arc: the paper's *unnamed*
simplification (A8) and the *between-preparation* reading of its *named* one (A2)
are both discharged by the optimiser's own behaviour (cued-absorption +
log-concavity spreading, both $r$-independent); only **A3** (conservation *form*)
remains CONTESTED, because its alternative changes the magnitudes that set the
criterion-dominance margin rather than the allocation geometry.

### Evidence

- `Critique/derivations/A2xA8--heterogeneous-r-allocation.md` (the re-derivation):
  §1 closed-form tangent gradient (criticality break), §2 second-order
  $O(\mathrm{var}\,r_i)$ bound via per-slot log-concavity, §3 $r$-independent
  cued-absorption + cost-dominant-kink survival, §4 the C1–C5 level effect.
- `Critique/replications/A2xA8--heterogeneous-r/` — `verify_heterogeneous_r.py`
  (criticality, C2 reframing, C1 corner; validates spread=0 ≡ single-$r$ model),
  `verify_deviation_interior.py` (the $\max\Delta R=1.5\times10^{-4}$ bound at
  interior cells). Deterministic (`results.json` sha256 `2659d7b5…`, byte-identical
  on re-run).
- Heterogeneity premise (R2): the v0.1 cluster
  [[reynolds_heeger2009_normalization]], [[mcadams_maunsell1999_v4_tuning]],
  [[treue_martinez_trujillo1999_feature_attention]], [[sani2017_temporal_v4_gain]],
  [[ghose_maunsell2002_task_timing]], [[carrasco2011_visual_attention_25y]],
  [[maunsell2015_attention_mechanisms]], [[reynolds_chelazzi2004_attentional_modulation]].
- $r$-independent protective mechanism: [[koch_ullman1984_winner_takes_all]],
  [[itti_koch2001_saliency_review]] (WTA = the concentration pressure that
  cued-absorption pre-empts); the C4/CR-045 location-count machinery.

### Loose ends

1. **C2-reframing replication at full resolution** (→ **CR-049**, prereq now
   discharged by this run's analytic boundedness). This run's reframing is at the
   coarse ($\Delta\alpha=0.02$, 21-pt $r$-grid) resolution; CR-049 maps VDA vs
   $r_{\text{cued}}$ across spreads at the paper's full grid and confirms the peak
   trajectory. The §2 bound says the effect is $O(\mathrm{var}\,r_i)$, so the
   moderate spreads are the informative ones.
2. **Extreme-spread stress test.** The conditional (ii) is "moderate spread." A
   targeted probe at a large spread (e.g. one uncued slot at $r_i\to0$ or
   $r_i\to\infty$ while the cued stays moderate) would test whether the
   $O(\mathrm{var})$ bound degrades — but such a slot is empirically implausible
   within one display, so this is low priority. (Spawn-candidate, low.)
3. **The A2×A8 result feeds A1/A6.** §1's per-slot marginal-value structure assumes
   *independent* SDT decisions (A1) and a *homogeneous decision rule* (A6); under
   correlated decisions or heterogeneous decision noise the tangent gradient gains
   cross-terms. Noted for the A1 (CR-006) / A6 (CR-011) attacks; out of scope here.
4. **Sign-reversal regime** (Carrasco/Yeshurun, the v0.1 Loose-end #3) remains a
   §5.4 clarity note (→ **CR-050**): the model's $r>0$ ($\beta\ge0$) excludes the
   documented attention-*impairs* regime (effective $\beta<0$); not a C1–C5 bias.

### Implications for PRISM v1/v2 (update)

The re-derivation sharpens v0.1's prediction. PRISM is simultaneously the A2- and
A8-relaxed model (per-location/per-channel FiLM, no global-ratio constraint), so
trained agents may learn *heterogeneous* effective $r_i$ across the display
(eccentricity-/channel-dependent — checkable against
`Prism/analysis/avg_saliency_*.py`). §1 predicts this would make PRISM's uncued
allocation slightly *unequal even at equal validity*, tilted toward the more
cost-dominant (smaller-$r_i$) locations; §2 predicts the tilt is *small*
($O(\mathrm{var}\,r_i)$); §3 predicts it *vanishes* wherever the cued slot has
absorbed the budget. Net: PRISM should still show near-homogeneous uncued spreading
in the swept regimes, with a measurable but second-order asymmetry tracking its
learned $r_i$ heterogeneity — and, given recurrence, a *time-varying* gain
(Sani 2017 / Ghose-Maunsell), so the `avg_alpha` trajectory, not the snapshot, is
the right comparison.

### Wiki cross-references

- [[reynolds_heeger2009_normalization]], [[mcadams_maunsell1999_v4_tuning]],
  [[treue_martinez_trujillo1999_feature_attention]], [[sani2017_temporal_v4_gain]],
  [[ghose_maunsell2002_task_timing]], [[carrasco2011_visual_attention_25y]],
  [[maunsell2015_attention_mechanisms]],
  [[reynolds_chelazzi2004_attentional_modulation]] — re-cited (the R2-heterogeneity
  cluster from v0.1; this run inherits them as the empirical motivation for the
  per-location $r_i$ the re-derivation bounds).
- [[koch_ullman1984_winner_takes_all]], [[itti_koch2001_saliency_review]] — cited
  (WTA = the concentration pressure; the derivation §3 shows cued-absorption
  pre-empts it $r$-independently).
- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] — cited (the
  heterogeneous-*validity* scope boundary — distinct from the heterogeneous-$r$
  question here; the two heterogeneities are the A8 and A2 axes respectively).
- [[luo_maunsell2018_criterion_sensitivity]] — cited (benefit/cost have distinct
  substrates; consistent with per-location $r_i$ and bridges to A1/A6 Loose-end #3).
- [[reynolds1999_competitive_v2_v4]], [[desimone_duncan1995_biased_competition]] —
  consulted; zero-sum reallocation substrate; cited in passing.
- [[bisley_goldberg2010_parietal_priority]], [[bisley_mirpour2019_priority_map]],
  [[rust_cohen2022_priority_coding]] — the LIP priority map is the $N$-dimensional
  per-location substrate that the scalar $r$ (and the homogeneous allocation)
  project away; unrelated to the *magnitude bound* but the natural locus of any
  learned $r_i$ heterogeneity; noted.
- concept [[coalition_resource_competition]] — the finite-resource/zero-sum framing
  behind $\beta+\gamma=2$ and the PRISM bridge; cited for §3.5.
- [[cameron2002_covert_attention_contrast]] — surfaced by the sweep
  (covert-attention contrast thresholds); near-threshold/low-$f_0$ regime, not the
  $r$-uniformity question; unrelated on inspection.
- **Math-methods gap (no wiki substrate):** majorization/Schur-concavity, the
  $S_{N-1}$ standard representation, and log-concavity of $\Phi$ — the analytic
  levers of §1–§2 — have no entry in `research_db/` (expected, mirrors the C5
  floating-point and A8 Schur gaps; flagged, not filled).
- §11.1 value-source anchors (*reward-modulated attention, selection history,
  dopamine, RPE, basal ganglia*: [[failing_theeuwes2018_selection_history]],
  [[hickey2010_reward_salience_acc]], [[stanisor2013_v1_value_attention]],
  [[glimcher2011_dopamine_rpe]]) — value *source*, not asymmetry *form*; **unrelated
  on inspection** for the heterogeneous-$r$ allocation question.
