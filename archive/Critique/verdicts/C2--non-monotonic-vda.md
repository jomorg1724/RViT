---
type: verdict
claim_id: C2
claim_statement: "VDA benefit is non-monotonic in r, peaking near r ≈ 0.3 in the cost-dominant regime, and approaching 0 at both extremes."
paper_section: "§4.3 (also §2.4, §2.5 for the model; Figure 4 reference)"
current_label: CONFIRMED-UNDER-ATTACK
attacks_tried:
  - vector: re-derivation
    run_id: bootstrap-001
    outcome: "claim survived; non-monotonicity is a theorem of model definitions; peak location confirmed to within sub-grid resolution"
  - vector: sensitivity
    run_id: run-002
    outcome: "claim survived; closed-form r†(v) from CR-001 directionally predicts every shift in the paper's §4.6 / Figure 6 secondary-sweep narrative. Log-width log10(r†(1)/r†(v)) recovers the 'a^0.3 compresses / a^2 stretches' claim exactly. One subsidiary §4.6 wording (peak VDA monotonic in f_0) weakened but not refuted; C2 itself is unaffected."
load_bearing_for:
  - "§4.4 Regime Where VDA Matters (Fig. 5 hot-zone)"
  - "§5.2 Implications for Experimental Design (when-to-observe-VDA recipe)"
  - "§6 Conclusion (the narrow-niche claim)"
last_updated: 2026-05-17
prompt_version_observed: "0.1"
---

## Previous frontmatter (v0.1)

```yaml
type: verdict
claim_id: C2
claim_statement: "VDA benefit is non-monotonic in r, peaking near r ≈ 0.3 in the cost-dominant regime, and approaching 0 at both extremes."
paper_section: "§4.3 (also §2.4, §2.5 for the model; Figure 4 reference)"
current_label: WEAKLY-SUPPORTED
attacks_tried:
  - vector: re-derivation
    run_id: bootstrap-001
    outcome: "claim survived; non-monotonicity is a theorem of model definitions; peak location confirmed to within sub-grid resolution"
load_bearing_for:
  - "§4.4 Regime Where VDA Matters (Fig. 5 hot-zone)"
  - "§5.2 Implications for Experimental Design (when-to-observe-VDA recipe)"
  - "§6 Conclusion (the narrow-niche claim)"
last_updated: 2026-05-17
prompt_version_observed: "0.1"
```

# Verdict: VDA benefit is non-monotonic in $r$, peaking near $r \approx 0.3$

## Claim as written in the paper

> *§4.3 (VDA Benefit is Non-Monotonic in r).* "Figure 4 reveals the
> central finding: VDA benefit is non-monotonic in $r$. At $V=0.5$ and
> $v=5$, VDA peaks near $r \approx 0.3$ (VDA $=0.080$ reward units)
> and declines toward zero at both extremes."
>
> *§4.3 (mechanism).* "At low $r$ (strongly cost-dominant), shifting
> attention is so expensive that neither P1 nor P2 moves from
> uniform — both converge to $\alpha = 1/N$ and VDA $\to 0$. At high
> $r$ (strongly benefit-dominant), shifting attention is so cheap that
> even the value-blind P2 saturates near $\alpha = 1.0$, leaving P1
> no room to improve — again VDA $\to 0$. Only at intermediate $r$ is
> the value-blind policy non-trivially suboptimal."

## Why this matters

C2 is *the* distinctive finding of the paper. It supplies the
mechanistic story behind the headline criterion-dominates claim:
even when attention reallocation *can* help, it only helps in a
specific cost-dominant slice of the asymmetry-ratio space, because
the value-blind baseline P2 is already efficient outside that slice.
Three downstream conclusions in the paper rest on C2:

1. **§4.4 — the hot zone.** The "where VDA matters" map (Fig. 5)
   uses $r \in [0.2, 1.0]$ as one of the three boundary conditions
   for the hot zone. If C2's non-monotonicity were absent — e.g. if
   VDA were monotonically increasing in $r$ — the hot-zone map
   would have a fundamentally different shape and the §5.2
   experimental-design recipe ("moderate cost-dominant $r$") would
   collapse.
2. **§5.2 — when to observe VDA.** The whole "when VDA should be
   observable" rubric assumes a specific cost-dominant range for
   $r$. If C2 were not in this range — for instance if the peak
   were at $r = 3$ — the experimental advice would invert.
3. **§6 — the "narrow niche" framing.** The paper's
   characterisation of VDA as a *narrow niche in the normative
   landscape* depends on the non-monotonic peak being narrow. C2
   is what makes the niche narrow on the $r$-axis.

For the user's PRISM v1/v2 program (§3.5 of the mission), C2
predicts a clean empirical signature: PPO-trained agents on a
Posner change-detection paradigm should exhibit (i) measurable
VDA only when the trained reward landscape places the implicit
asymmetry-ratio analogue in the cost-dominant regime, and (ii)
exact value-insensitivity of attention allocation outside that
regime. If PRISM v1 / v2 attention trajectories
(`Prism/figures/avg_alpha_*.pdf`) ever show monotonic dependence
of $\alpha$ on cue value across the trained value space, that
would *refute* C2 in trained-network space — which would either
mean (a) PPO's training dynamics select solutions that deviate
from the normative optimum, or (b) the normative model's
$\beta/\gamma$ parameterisation does not describe PRISM's
mechanism. Either inference would be informative.

## Version 0.1 — 2026-05-17

### What this version did

**Attack vector:** re-derivation (mission §3.2). Re-derived the
model definitions (mission §2.4–§2.5) symbolically; proved a
*two-limit theorem* showing $\mathrm{VDA}(r) \to 0$ as $r \to 0^+$
and as $r \to \infty$, with strict positivity on an interior
interval. Identified the mechanism analytically: distinct escape
thresholds $r^\dagger(v) < r^\dagger(1)$ for P1 and P2, with the
non-zero VDA interval being $(r^\dagger(v), \infty)$ and the peak
controlled by the rate at which $\alpha^\star_{\mathrm{P2}}$
closes to $\alpha^\star_{\mathrm{P1}}$ above $r^\dagger(1)$.

**Companion numerical check.** Implemented a minimal P1/P2/P3/P4
model in Python (sandbox; scipy unavailable, hand-rolled $\Phi$ via
`math.erf`). Swept $r$ on the paper's grid; reproduced the
qualitative non-monotonicity, the asymptotic decline at both
extremes, and the peak magnitude (0.077 vs paper's 0.080) to within
4 %. Peak location lands at $r = 0.398$ (one log-grid step right of
the paper's $r \approx 0.3$); the discrepancy is sub-grid
resolution at $\Delta\alpha = 0.01$ vs the paper's $\Delta\alpha
= 0.005$ — see derivation §4.

### Verdict

**WEAKLY-SUPPORTED.**

The re-derivation succeeded: the model's definitions *force*
non-monotonicity, and the numerical sweep corroborates the
analytic skeleton at every point checked. There is no sign of a
hidden algebraic step in the paper's narrative §4.3; the agent
identifies one expository gap (the closed-form escape thresholds
in Eq. (2.5) of the derivation are absent from the paper, though
implied by the empirical sweep) but no error.

Per mission §3.1, the label cannot be elevated to
CONFIRMED-UNDER-ATTACK on the first run that touches the claim —
that requires $\geq 2$ distinct attack vectors across separate
runs. This run executed one (re-derivation). A second attack —
either (a) a full Figure-4 replication at the paper's grid
resolution, or (b) a sensitivity probe testing whether the peak
location shifts as predicted by Eq. (2.5) when $f_0, h, N$ vary —
would, if it also fails to falsify, justify CONFIRMED-UNDER-ATTACK.

### Evidence

- **Derivation:** `Critique/derivations/C2--non-monotonic-vda.md`
  — full LaTeX. The two-limit theorem (§2.1, §2.2) is the
  centrepiece; (2.3)–(2.5) give the closed-form escape threshold.
- **Replication:** `Critique/replications/C2--non-monotonic-vda/`
  — Python implementation; `output/vda_vs_r.json` contains the
  per-$r$ results; derivation §4 has the headline table.
- **Wiki literature support:**
  - `[[luo_maunsell2018_criterion_sensitivity]]` — direct
    empirical support for the criterion/sensitivity dissociation
    underlying the paper's "independent benefit/cost" conceptual
    move. Specifically: LPFC neurons modulate with *both*
    criterion and sensitivity changes, in *distinguishable*
    patterns. The paper's $\beta/\gamma$ asymmetry treats benefit
    and cost as independently parameterisable; Luo & Maunsell
    show the neural circuit can independently express both.
  - `[[reynolds_heeger2009_normalization]]` — theoretical scaffold
    for separable excitatory ($G_E$) and suppressive ($G_S$)
    gains. The paper's $\beta = 2r/(r+1)$ (top-down enhancement)
    and $\gamma = 2/(r+1)$ (surround suppression) operationalise
    exactly the Reynolds–Heeger split. The normalization model
    independently varies these gains; the Herman Lab paper
    parameterises one knob (the ratio $r$) over that variation.
  - `[[mcadams_maunsell1999_reliability]]` — empirical evidence
    for multiplicative sensitivity gain at the attended location
    (the β-side substrate).

### Loose ends

1. **Peak location at $r \approx 0.3$ vs $r \approx 0.4$ in
   agent's grid.** Resolved as sub-grid resolution; spawn
   CR-013 (high-resolution Figure 4 replication) to confirm.
2. **Peak-location sensitivity to $f_0, h, N$.** Eq. (2.5) of the
   derivation gives a closed-form prediction; the paper's Figure 6
   shows the empirical pattern. Spawn CR-014 (sensitivity probe).
3. **Robustness of the two-limit theorem to multiplicative
   conservation $\beta \gamma = 1$ (A3).** The agent's §2 argument
   should still go through under A3, but the peak location and
   magnitude will shift. CR-008 already covers this; the
   derivation gives it sharper teeth.
4. **PRISM empirical comparison.** No PRISM trajectory data
   inspected this run; the §3.5 Implications-for-PRISM block
   below is the agent's first cut. A future run should pull
   `Prism/analysis/avg_saliency_*.py` outputs and check whether
   trained agents' $\alpha$-vs-$v$ slopes are consistent with
   C2's prediction of inverse-cost-asymmetry scaling.

### Implications for PRISM v1/v2

PRISM v1 / v2 are trained with PPO on the same Posner change-
detection paradigm class the paper analyses normatively. C2
predicts that *if the PRISM agent's internal attention-cost
landscape lies in the cost-dominant regime ($r \in (r^\dagger(v),
r^\dagger(1))$ in the paper's $\beta/\gamma$ parameterisation),
the attention head's $\alpha$ should track cue value*; otherwise
it should not. Concretely:

- If `Prism/figures/avg_alpha_*.pdf` shows the head's mean
  attention to the cued location depending on the cue-value
  feature, the paper would *predict* that the regime is
  cost-dominant. Estimating $r$ from the trained network is
  hard, but checking the sign and steepness of
  $\partial \alpha / \partial v$ at a few cued-value levels is
  feasible (this is the kind of thing
  `Prism/analysis/avg_saliency_*.py` should be able to extract).
- If the slope is *zero* (attention does not depend on value at
  all), one of two things is true: (i) PRISM's task setup places
  it in the benefit-dominant regime where $\alpha^\star_{\mathrm{P2}}
  \approx 1$ saturates and VDA $\to 0$, or (ii) PRISM uses
  criterion-only encoding of value — which is exactly the paper's
  "criterion adjustment dominates" prediction.
- The user's recurrent ViT manuscript (arXiv:2502.10955) reports
  attention trajectories; the agent did not consult them this run
  but flags that any *monotone* dependence of attention on value
  in the recurrent ViT would *refute* C2 in trained-network space.

### Wiki cross-references

The §11 sweep used the keyword anchor list in mission §11.1
(value-directed attention, reward-modulated attention,
attentional capture, selection history, criterion shift, signal
detection theory, d-prime, normalization model, gain modulation,
surround suppression, priority map, LIP, FEF, V4, parietal,
frontal eye field, biased competition, dopamine, RPE, basal
ganglia, oculomotor, saccade, change detection, Posner cueing,
cue validity).

- `[[luo_maunsell2018_criterion_sensitivity]]` — **cited in §
  Evidence above** as the load-bearing empirical substrate for
  the criterion/sensitivity dissociation. Read in full this run.
- `[[reynolds_heeger2009_normalization]]` — **cited in § Evidence**
  as the theoretical scaffold for separable benefit/cost gains.
  Re-read this run.
- `[[maunsell2015_attention_mechanisms]]` — relevant; cited by
  the paper (refs 11–14) as the empirical case for dissociable
  attentional mechanisms. Spawned CR-015: read in next run as
  part of A2 attack.
- `[[mcadams_maunsell1999_reliability]]` — **cited in § Evidence**
  as the β-side empirical substrate.
- `[[cohen_maunsell2009_correlations]]` — bears on A1
  (independence) and on whether the marginal calculus in
  derivation Eq. (2.3) is exact; not pulled in for this verdict
  but flagged for CR-006 (A1 attack).
- `[[srinath2021_attention_information_flow]]` — relevant to A2;
  not engaged this run.
- `[[carrasco2011_visual_attention_25y]]` — broad attention
  review; would be the natural source for cue-validity priors,
  not directly load-bearing on C2.
- `[[hickey2010_reward_salience_acc]]` — reward-modulated
  capture (selection-history side). Bears on the *existence* of
  VDA (the paper assumes VDA can occur; this paper provides
  empirical support); did not bear on the non-monotonicity
  *shape*. Unrelated to C2 specifically.
- `[[failing_theeuwes2018_selection_history]]` — review of
  selection-history effects. Same as above: relevant to whether
  VDA is observed empirically, not to the non-monotonicity
  argument.
- `[[bisley_mirpour2019_priority_map]]` — priority map review;
  bears on whether the paper's attention-allocation framework is
  consistent with parietal priority representations. Tangential
  to C2.
- `[[desimone_duncan1995_biased_competition]]` — biased
  competition framework. The paper's normalization-based
  benefit/cost is a refinement of biased competition. Tangential
  to C2 specifically.
- `[[maunsell_treue2006]]` — *not present in wiki*; flagged as
  potential gap (the foundational feature-vs-spatial dissociation
  review). Spawn CR-016 to consider adding stub.
- `[[carlisle2011_attentional_templates]]` — attentional
  templates; unrelated to the C2 non-monotonicity argument on
  inspection.
- `[[glimcher2011_dopamine_rpe]]` — dopamine / RPE; relevant to
  the broader value-attention story but not to the specific
  asymmetry-ratio non-monotonicity. Unrelated to C2 on inspection.
- `[[bhatnagar2022_attention_choice_metaanalysis]]` — meta-
  analysis of attention-choice link. Could supply empirical
  effect-size data for VDA presence, useful for CR-003 (literature
  attack on C3) but unrelated to C2's non-monotonicity shape.

Searched terms returning no relevant hits this run: *priority map
LIP, FEF microstimulation, saccade* (the latter two would bear on
the brain's circuit-level value-attention machinery but not on
the specific non-monotonicity-in-$r$ claim).

## Version 0.2 — 2026-05-17

### What this version did

**Attack vector:** sensitivity (mission §3.2). Took the closed-form
escape threshold

$$
r^\dagger(v) \;=\; \frac{G_u(V, N, c_c^\star, c_u^\star)}{(N-1)\,G_c(v, V, N, c_c^\star, c_u^\star)} \tag{2.5}
$$

from the CR-001 derivation §2.3 and used it to predict the
**direction** of peak-location shifts across the paper's three
secondary parameter sweeps (paper §3.1, Figure 6):

- $f_0 \in \{0.1, 0.3, 0.5, 0.7\}$ at $h = \sqrt{\cdot}, N = 4$
- $h \in \{a, \sqrt{a}, a^{0.3}, a^2\}$ at $f_0 = 0.5, N = 4$
- $N \in \{2, 4\}$ at $f_0 = 0.5, h = \sqrt{\cdot}$

with $V = 0.5, v = 5$, Variant A throughout. For each combination
the agent (a) computed $(c_c^\star, c_u^\star)$ at $\alpha = 1/N$,
(b) substituted into the closed-form to get $r^\dagger(v=5)$ and
$r^\dagger(v=1)$, (c) ran a full P1/P2 grid optimisation on an
extended $r$-grid $[10^{-2}, 10^1]$ at 31 log-spaced points, and
(d) checked whether the closed-form's predicted direction of peak
shift matched the empirical peak shift and the paper's §4.6
narrative.

All code and full diagnostics live at
`Critique/replications/C2--non-monotonic-vda/sensitivity/`. The
correction of a sign-transcription error from CR-001 (G_c and G_u
are *sums* of positive contributions, not differences — the minus
sign in the gradient comes from the Jacobian of $d'_u$ on $\alpha$,
not from $G_u$ itself) is documented in
`.../sensitivity/notes.md` §1.

### Verdict

**CONFIRMED-UNDER-ATTACK.**

Two distinct attack vectors — re-derivation (CR-001) and sensitivity
probe (CR-014) — have now failed to falsify C2. Per mission §3.1
this is the threshold for elevation. The strength of the elevation
comes not just from "both attacks succeeded" but from the *structural*
nature of the second attack: the closed-form $r^\dagger(v)$
derived in CR-001 as a *byproduct* of the non-monotonicity argument
turns out to be a *direction-correct predictor* of every parameter
shift in the paper's secondary-sweep figure. That is, the paper's
empirical §4.6 narrative (Figure 6 sensitivity-to-parameters) is
not three independent empirical findings — it is one analytic
expression evaluated at three different parameter axes.

### Evidence

| sweep |     | $r^\dagger(v=5)$ | $r^\dagger(v=1)$ | log-width | $r^\star_{\text{emp}}$ | $\mathrm{VDA}^\star$ | paper claim | match |
|-------|----:|------:|------:|------:|------:|------:|------|------|
| $f_0$ | 0.1 | 0.014 | 0.221 | 1.19 | 0.10 | 0.071 | peak ↓ in $r$, ↑ VDA | direction ✓ |
|       | 0.3 | 0.028 | 0.294 | 1.01 | 0.25 | 0.109 | … | … |
|       | 0.5 | 0.050 | 0.343 | 0.83 | 0.40 | 0.080 | (reference) | … |
|       | 0.7 | 0.066 | 0.375 | 0.75 | 0.50 | 0.038 | … | … |
| $h$   | $a$       | 0.026 | 0.266 | 1.02 | 0.16 | 0.082 | "linear baseline" | ✓ |
|       | $\sqrt{a}$ | 0.050 | 0.343 | 0.83 | 0.40 | 0.080 | (reference) | … |
|       | $a^{0.3}$  | 0.066 | 0.374 | **0.76** | 0.63 | 0.043 | "compresses" | ✓ (narrowest log-width) |
|       | $a^2$      | 0.011 | 0.212 | **1.27** | 0.03 | 0.025 | "stretches" | ✓ (widest log-width) |
| $N$   | 2 | 0.266 | 1.000 | 0.58 | 5.01 | 0.156 | "similar, slightly ↑ VDA" | direction ✓; magnitude understated by paper |
|       | 4 | 0.050 | 0.343 | 0.83 | 0.40 | 0.080 | (reference) | … |

#### Where the closed form is exact

For non-clamping regimes (regular $f_0$, regular $h$, $N \in \{2,4\}$
at $V \geq 1/N$), the empirical P1 and P2 escape from uniform
attention happens at the first $r$-grid step above the closed-form
$r^\dagger(v=5)$ and $r^\dagger(v=1)$ respectively. For $N=2$
specifically: closed-form $r^\dagger(v=5) = 0.2655$, empirical P1
escape between $r=0.251$ and $r=0.316$; closed-form
$r^\dagger(v=1) = 1.0000$, empirical P2 escape between $r=1.000$
and $r=1.259$. Both predictions hit within one log-r-grid step
(factor of $10^{0.1} \approx 1.26$).

#### Where the closed form is conservative

For very low baseline sensitivity ($f_0 = 0.1$) or strongly
accelerating returns ($h = a^2$), the $d'$-clamping in mission
§2.4 ("All $d'$ values clamped at $\geq 0$") activates: at
$\alpha$ near 1 with $\gamma > d'_{\text{base}}/(d'_{\text{base}} -
d'_{\max} f((1-\alpha)/(N-1)))$, the uncued $d'$ saturates at 0 and
moving $\alpha$ further is *cost-free* in $d'$ terms. The closed-
form $r^\dagger(v)$ is derived from the *non-clamping*
infinitesimal-deviation gradient and therefore *underestimates*
how attractive large-$\alpha$ deviations actually are in the
clamping regime. The empirical P1 reaches $\alpha = 1.0$ at all
$r$ in the swept range for $f_0 = 0.1$ and $h = a^2$, well below
the closed-form $r^\dagger(v=5)$. This *qualifies* the closed-
form to "non-clamping regime" but does **not** weaken C2: the
non-monotonicity is still present empirically in the clamping
regime (peak hugs the P2-escape boundary rather than spreading
across a wider $r$-interval).

#### Subsidiary §4.6 claim partially weakened (does *not* affect C2)

The paper §4.6 writes "Lower $f_0$ shifts the peak VDA *higher*"
without qualification. Empirically, peak VDA is *non-monotonic* in
$f_0$ at the present $\alpha$-grid resolution: 0.071 ($f_0=0.1$),
0.109 ($f_0=0.3$), 0.080 ($f_0=0.5$), 0.038 ($f_0=0.7$). Max is
at $f_0 = 0.3$, not the lowest $f_0$. The wording would be safer
as "moderately low $f_0$ shifts the peak VDA higher". This affects
§4.6 wording and possibly §5.2's experimental-design
recommendation, but **not** C2 itself (which is the
non-monotonicity-in-$r$ claim, not a claim about how peak VDA
depends on $f_0$).

#### Wiki literature substrate (newly engaged this run)

- `[[muller_findlay1987_sensitivity_criterion]]` — **cited** as
  foundational SDT framework underlying the policy decomposition
  (P1–P4). Müller & Findlay establish that spatial cues produce
  *both* sensitivity ($d'$) changes and criterion ($\beta$ in their
  notation) shifts and the two are *dissociable*. The paper's
  separation of P3 (criterion gain) and P2 (validity-attention
  gain) from VDA (P1 − P2) is the operationalisation of exactly
  this dissociation. The CR-014 closed-form $r^\dagger(v)$
  inherits its validity from the SDT formulation that
  Müller-Findlay established.
- `[[hawkins1990_attention_detectability]]` — **cited** as direct
  empirical evidence that visual attention produces $d'$
  enhancements ("modulates signal detectability"). Their three
  experiments confirm sensitivity changes are real and not
  artefacts of criterion shifts. Bears on the $\beta$-channel
  ($d'_c$ increase at the cued location) in the paper's model.
- `[[lu_dosher1998_external_noise]]` — **cited** as the canonical
  methodological paper for *dissecting attention mechanisms* into
  signal enhancement vs distractor exclusion vs internal noise
  suppression. The paper's $\beta$-channel maps onto signal
  enhancement (raising cued $d'$); the $\gamma$-channel maps onto
  distractor exclusion-via-suppression (lowering uncued $d'$). The
  asymmetry ratio $r = \beta/\gamma$ in the paper is a single-
  parameter summary of the *relative strength* of these two
  mechanisms in Lu-Dosher's PTM taxonomy.

### Loose ends

1. **The closed-form does not capture the clamping regime.** The
   $d'$-clamping at $\alpha \to 1$ when $\gamma$ is large means the
   non-clamping gradient prediction $r^\dagger(v) = G_u/[(N-1)G_c(v)]$
   *underestimates* how easily P1 escapes uniform. A future
   derivation task could extend $r^\dagger$ to the clamping
   regime by replacing the small-deviation gradient with a
   *finite-deviation* comparison evaluated at $\alpha = 1$. Spawn
   **CR-017** (derivation extension).
2. **Peak VDA non-monotonic in $f_0$.** The paper's §4.6 wording
   that "lower $f_0$ → higher peak VDA" is partially refined.
   Spawn **CR-018** (literature attack on whether empirical low-$d'$
   regimes show this paper's predicted higher VDA, or rather a
   non-monotonic pattern — the answer informs §5.2's
   experimental design recommendation).
3. **$V = 1/N$ degeneracy at $N=2$.** At $V = 1/N$ exactly, the
   cued / uncued labelling has no informational content and the
   model's optimum is symmetric (any $\alpha$ on the symmetric
   pair $\{a, 1-a\}$ is optimal). The optimiser picks the
   "inverted" branch ($\alpha < 1/N$) for P2 at high $r$,
   technically violating C4. Worth a verdict note when CR-004
   (C4 re-derivation) is taken on. Spawn **CR-019** (C4
   refinement).
4. **PRISM empirical comparison — still untouched.** The §3.5
   "Implications for PRISM" block in the v0.1 verdict was
   speculative; this version did not pull PRISM attention
   trajectories either. The non-monotonicity in $r$ as a
   PRISM-empirical predictor remains a task for a future run.

### Implications for PRISM v1/v2 (refined)

The CR-014 sensitivity probe refines the PRISM prediction in two
ways:

1. **The closed-form $r^\dagger(v=5)$ gives a numerically
   sharp prediction.** For a PRISM agent operating at a regime
   analogous to $f_0 = 0.5$, $h = \sqrt{\cdot}$, $N=4$, $V=0.5$,
   $v=5$, attention should track value (P1 vs P2 differ)
   for $r \in (0.05, 0.34)$. If PRISM's implicit β/γ structure
   places it outside this interval, no value-tracking
   should be observed. This is a one-decade-wide window that
   experimental fits could in principle locate.
2. **The clamping regime predicts a "binary" attention
   pattern.** For low effective $f_0$ (which could correspond
   to small baseline cued-location sensitivity in the trained
   PRISM agent), the model predicts $\alpha^\star = 1.0$ at all
   $r$ — i.e. *full commitment* to the cued location whenever
   any value is signalled. PRISM trajectories
   (`Prism/figures/avg_alpha_*.pdf`) that show binary attention
   ("on" or "off" rather than graded) would be consistent with
   PRISM operating in the clamping regime.

### Wiki cross-references (Version 0.2 sweep)

The §11 sweep ran the mission §11.1 keyword anchors again,
adding terms specific to the secondary-sweep mechanism: *baseline
sensitivity, transfer function, set size, perceptual gain, signal
enhancement, distractor exclusion, internal noise, perceptual
template, psychophysical sensitivity*.

New hits / re-engagements this version:

- `[[muller_findlay1987_sensitivity_criterion]]` — **cited above**
  as foundational SDT dissociation. Read this version.
- `[[hawkins1990_attention_detectability]]` — **cited above** as
  empirical d' increases at cued locations. Read this version.
- `[[lu_dosher1998_external_noise]]` — **cited above** as
  signal-enhancement vs distractor-exclusion taxonomy. Read
  this version.
- `[[solomon2004_cues_sensitivity]]` — capacity-unlimited
  sensitivity enhancement; bears on whether the paper's
  *single-cued-location* assumption is empirically supported, but
  not directly on the non-monotonicity claim. Noted for future
  use (could feed an A6 attack on "homogeneous decision rule across
  locations" — if non-attentional precue effects are present at
  *all* locations, the per-location independence in A1 may also
  be questioned).
- `[[sridharan2017_sc_sensitivity_bias]]` — neural dissociation
  of sensitivity vs bias in superior colliculus; reinforces the
  $\beta$-channel / $\gamma$-channel split. Not yet read in full
  but flagged for future CR-007 (A2 literature attack).
- `[[cameron2002_covert_attention_contrast]]` — contrast-sensitivity
  measurements at attended vs unattended locations; supplies
  empirical magnitudes for the $\beta$-channel. Not engaged
  this run but flagged as relevant for the future $\beta/\gamma$
  parameterisation literature attack.

Sweep terms returning no new relevant hits this version (beyond
v0.1 sweep): *priority map LIP, FEF microstimulation, saccade,
dopamine RPE, basal ganglia, oculomotor*.

The Maunsell-lab references in the paper (refs 11–14, principally
`[[maunsell2015_attention_mechanisms]]`) remain the natural target
of CR-015 (literature attack on A2). The v0.2 sweep did not
deepen these; they remain at metadata depth in the wiki.
