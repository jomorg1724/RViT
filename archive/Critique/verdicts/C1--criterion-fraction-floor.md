---
type: verdict
claim_id: C1
claim_statement: "Across the full parameter sweep (4,410 combinations), the criterion fraction is between 0.60 and 0.96."
paper_section: "§4.1 (last paragraph); see also Figure 2 caption and §6 Conclusion"
current_label: CONTESTED
attacks_tried:
  - vector: sensitivity
    run_id: run-003
    outcome: "claim refuted as written; my replication finds CF ∈ [0.30, 1.00] across the 4,410 swept rows. Variant A min CF = 0.5587; variant B min CF = 0.3040. The substantive 'criterion typically dominates' spirit survives (median CF ≈ 0.76, 80%+ of rows have CF ≥ 0.50) but the categorical [0.60, 0.96] range is too strong."
load_bearing_for:
  - "§5.1 'Why Criterion Dominates' (the qualitative theoretical argument is unaffected, but the quantitative magnitude statement is)"
  - "§5.2 'Implications for Experimental Design' (recommends *interpreting the absence of VDA in high-validity paradigms as evidence of criterion dominance*; the CF floor's overstatement weakens that recommendation slightly)"
  - "§5.3 'Implications for Computational Models' (the 'criterion captures most value-related reward' assertion that the user's PRISM-style models should inherit a criterion-like value-encoding mechanism)"
  - "§6 Conclusion ('criterion adjustment consistently captures the majority of value-related reward')"
last_updated: 2026-05-17
prompt_version_observed: "0.1"
---

# Verdict: criterion fraction always in [0.60, 0.96]

## Claim as written in the paper

> *§4.1 (Criterion Adjustment Dominates Value Encoding), last
> paragraph.* "This pattern holds across the full sweep: the
> criterion fraction ranges from 60% to 96% across all (r, V, v)
> combinations tested. Criterion adjustment is always the single
> largest contributor to value-related reward."
>
> *§4.1 (specific reference points).* "In the cost-dominant regime
> (r = 0.3), the criterion fraction reaches 96%. ... In the symmetric
> case (r = 1.0), the criterion fraction is 73%. Even in the
> benefit-dominant regime (r = 3.2), where attention is cheap to
> deploy, criterion still accounts for 64% of total gain."
>
> *§6 Conclusion.* "Criterion adjustment consistently captures the
> majority of value-related reward."

## Why this matters

C1 is the paper's *flagship* quantitative claim. It supplies the
top-line message: criterion adjustment captures 60–96% of value-
related reward across the swept space, with the implication that
any model (biological or computational) that implements only
attention reallocation, lacking a criterion mechanism, will leave
"most" of the available reward on the table. Three downstream
conclusions in the paper rest on C1:

1. **§5.2 — experimental design.** The "when VDA should NOT be
   expected" rubric ("standard spatial cueing paradigms with high
   validity ... are predicted to show negligible VDA regardless of
   other parameters") is justified by C1's quantitative magnitude:
   if criterion captures 60–96% of the gain, the remaining 4–40% is
   the VDA + validity-attention slice, of which VDA in turn is a
   small portion. If C1's floor is overstated (e.g. the true min is
   30% in variant B), then "negligible VDA" mis-states the available
   non-criterion share.
2. **§5.3 — computational models.** The advice that "models such as
   recurrent vision transformers ... may discover this efficient
   routing without explicit instruction, finding that criterion
   adjustment captures value-related reward while attention serves
   primarily validity-driven functions" rests on C1's claim that
   criterion *captures most* of the reward. A trained model that
   routes through attention rather than criterion would, on C1, be
   leaving 60–96% of the available reward unattained — a strong
   normative argument for the model architecture the paper
   recommends. Weaken C1, and the architectural recommendation
   becomes a softer "criterion is *often* enough" rather than
   "criterion is *always* sufficient".
3. **§6 — the headline thesis.** The conclusion's phrasing
   "criterion adjustment consistently captures the majority of
   value-related reward" presupposes C1. With C1 as written, the
   statement is true (60% > 50% always). With C1 weakened to the
   replication's actual finding (min CF = 30% in variant B), the
   statement is no longer always true — *most* of the time criterion
   does dominate, but in 8% of swept variant-B rows it does not.

For the user's PRISM v1/v2 program (mission §3.5), C1 has the
following implication: trained agents are predicted to route most
value-related reward through criterion-like mechanisms. The user's
PRISM v1 implements both attention (saliency masks via the
$\alpha$ map) and an implicit criterion (the policy's choice
threshold for declaring a change). If PRISM agents trained on a
Posner change-detection task consistently encode value via the
criterion analogue (the policy threshold) more strongly than via
the saliency mask, that is empirical convergence with C1's spirit.
If the *opposite* — value is encoded preferentially via the
saliency mask, and the policy threshold is value-invariant — that
would be empirical *evidence against* C1's spirit, and would either
(a) place the trained model in the V = 1/N corner of the sweep, or
(b) suggest training dynamics deviate from the normative optimum.
The user's `Prism/figures/avg_alpha_*.pdf` and
`Prism/analysis/avg_saliency_*.py` artifacts are first-party data
to consult on this point.

## Version 0.1 — 2026-05-17

### What this version did

**Attack vector:** sensitivity (mission §3.2).
**Method.** Replicated the paper's 4,410-row primary parameter
sweep (r ∈ {21 log-pts in [0.1, 10.0]} × V ∈ {21 pts in [1/N, 1.0]}
× v ∈ {1, 2, 3, 4, 5} × variant ∈ {A, B}, fixed N = 4, d'_max = 2.0,
f_0 = 0.5, h = √, α-grid Δα = 0.02, c-grid Δc = 0.05 on [-3, 3]).
Computed CF = (R(P3) - R(P4)) / (R(P1) - R(P4)) per row. Located
argmin CF in the swept space. Anchored a Phase B extrapolation
probe at the argmin: pushed r > 10, f_0 < 0.1, h ∈ {a^3, a^4},
N ∈ {8, 16, 32}, v ∈ {10, 20, 50, 100}, and joint combos outside
the paper's sweep, to see whether plausible extrapolations push CF
further below 0.50.

Full code, data, and decomposition at
`Critique/replications/C1--criterion-fraction-floor/`.

### Verdict

**CONTESTED.** The claim as written is too strong. Specifically:

| Statement                                          | Status     |
|----------------------------------------------------|------------|
| CF ∈ [0.60, 0.96] across all 4,410 (r, V, v) rows  | **FALSE**  |
| CF ≥ 0.50 across all 4,410 rows                    | **FALSE**  |
| CF ≥ 0.50 across variant A's 2,205 rows            | TRUE       |
| CF ≥ 0.56 across variant A's 2,205 rows            | TRUE       |
| CF ≥ 0.60 across variant A's 2,205 rows            | FALSE (7% of rows below) |
| Median CF ≈ 0.76 (both variants)                   | TRUE       |
| At r = 1.0, V ≈ 0.5, v = 5, variant A: CF ≈ 0.73   | TRUE (mine: 0.728) |
| At r = 3.2, V ≈ 0.5, v = 5, variant A: CF ≈ 0.64   | TRUE (mine: 0.642) |
| At r = 0.3, V ≈ 0.5, v = 5, variant A: CF ≈ 0.96   | **FALSE** (mine: 0.854; Figure 2 visual: ~0.85) |
| Substantive: "criterion *typically* dominates"     | TRUE       |

The verdict label is CONTESTED (mission §3.1: "at least one
credible attack succeeded; the claim's headline statement is too
strong as written and the verdict proposes a weaker reformulation").

**Why not REFUTED.** Mission §6 requires REFUTED to have "an
explicit pointer to ... a derivation error, replication failure, or
literature contradiction ... that the agent judges the paper cannot
survive without substantive revision." The CF range is wrong, but
the paper *can* survive: a quantitative re-statement preserving the
core scientific point is straightforward (see "Proposed weaker
reformulation" below). The §5.1 theoretical argument (criterion is
costless, attention is zero-sum) is unaffected; the §5.3
architectural recommendation needs only mild softening.

**Why not WEAKLY-SUPPORTED.** The attack succeeded: 13.4% of swept
rows fall below the stated 0.60 floor; 4.0% fall below 0.50. This
is a clear failure of the categorical claim, not "no attack tried
yet".

### Proposed weaker reformulation

The paper's §4.1 last paragraph and §6 Conclusion can be re-stated
to preserve the substantive scientific point without the false
categorical floor:

> *Revised §4.1.* "Across the swept (r, V, v, variant) space,
> criterion adjustment captures the majority of value-related
> reward in 88% of the 4,410 combinations (CF ≥ 0.50 in 96% of
> rows). The criterion fraction ranges from 0.56 to 1.00 in
> variant A and from 0.30 to 1.00 in variant B. Violations of CF ≥
> 0.60 concentrate at high r (the benefit-dominant regime, where
> attention is cheap), low V (especially V near 1/N, where the cue
> conveys little validity information and the β/γ asymmetry alone
> drives attention reallocation), and v ∈ {1, 2} (where the value
> gradient is weak). Reference points: at r = 1.0 (symmetric),
> CF = 73%; at r = 3.2 (benefit-dominant), CF = 64%; at r = 0.3
> (cost-dominant), CF ≈ 85% (see Figure 2)."

The revision (a) preserves the "majority of value-related reward"
language for the *typical* case, (b) replaces the false [0.60, 0.96]
range with the true [0.30, 1.00] (or [0.56, 1.00] in variant A),
(c) names the parameter regions where the floor fails, and (d)
corrects the r = 0.3 reference from 96% to ≈ 85% (consistent with
Figure 2). The paper's §5.1 theoretical argument and §5.2 / §5.3
applied recommendations carry through with only minor softening.

### Evidence

- **Replication output:** `Critique/replications/C1--criterion-fraction-floor/output/results.json` —
  full 4,410-row decomposition + Phase B extrapolations. Variant A
  argmin: (r=10, V=0.55, v=1) → CF = 0.5587. Variant B argmin:
  (r=10, V=0.25, v=4) → CF = 0.3040.
- **Reference-point validation:** code matches paper at r = 1.0
  (mine 0.728 vs 0.73) and r = 3.2 (mine 0.642 vs 0.64) to within
  0.002 of CF. The r = 0.3 reference (paper text: 96%) is
  inconsistent with both my replication (0.85) and the paper's own
  Figure 2 (visual reading: ~0.85). See
  `Critique/replications/C1--criterion-fraction-floor/notes.md` §1
  for the diagnostic trace.
- **Phase B extrapolations:** anchored at the V = 1/N variant B
  argmin, pushing r > 10 takes CF down to 0.26 (asymptote at r → ∞).
  All other extrapolation axes (f_0 < 0.1, h ∈ {a^3, a^4}, N > 4,
  v > 5, joint combos) push CF *upward* from the V = 1/N anchor.
  The paper's swept r range already captures essentially the
  worst-case CF for the swept (V, v, variant) regime.
- **Mechanism:** the low-CF regime is driven by two factors. (i)
  At V = 1/N, the β/γ asymmetry creates an attention-reallocation
  incentive even at v = 1 (when the cue is value-symmetric), because
  the β-scaled cued gain (weight 1/N) exceeds the γ-scaled uncued
  loss (weight (N-1)/N) by factor ~r at large r. The paper's policy
  decomposition attributes this gap to "validity-attention", but at
  V = 1/N it is purely β/γ-asymmetry-driven. (ii) Variant B's
  CR = 1 (value-decoupled) shrinks the unbiased-baseline reward P4
  relative to P1, inflating the denominator R(P1) - R(P4) and
  shrinking CF.
- **Literature anchors** (see
  `Critique/evidence/C1--criterion-fraction-floor.md` for full
  treatment):
  - [[muller_findlay1987_sensitivity_criterion]] — foundational
    SDT decomposition of cueing into sensitivity and criterion
    components. Establishes dissociability but is silent on the
    CF *floor*.
  - [[hawkins1990_attention_detectability]] — foundational
    sensitivity-side cueing evidence. Establishes attention has a
    sensitivity component; not bearing on the CF floor.
  - [[luo_maunsell2018_criterion_sensitivity]] — neural-substrate
    paper localising criterion to LPFC and sensitivity to visual
    cortex. Provides the biological grounding for the
    independent-mechanism model the paper uses; not bearing on
    the CF floor.
  - [[sridharan2017_sc_sensitivity_bias]] — multialternative SDT
    framework with empirical convergence: bias (criterion) is the
    primary SC attention effect in multialternative tasks. Direct
    qualitative support for "criterion typically dominates", but
    does not pin a quantitative floor.

### Implications for PRISM v1/v2

If C1's *spirit* survives (criterion typically dominates), then
PRISM agents trained on the Posner change-detection task in
`Prism/env.py` are predicted to encode reward value preferentially
through the policy's decision threshold ("criterion analogue")
rather than through the $\alpha$ saliency mask. Empirically:
- `Prism/analysis/avg_saliency_*.py` outputs and
  `Prism/figures/avg_alpha_*.pdf` should show $\alpha$ trajectories
  that are *value-invariant* across the trained value distribution
  in most operating regimes, with value-dependent shifts only in
  the narrow regime C2/C3 predicts.
- The policy's decision threshold (the implicit criterion in the
  PPO actor's logit-to-action mapping) should show *value-dependent
  shifts*. This is the architectural analogue of the criterion
  adjustment mechanism.

C1's *categorical 60–96% floor* failing does not change this
prediction qualitatively, but it does mean PRISM's empirical
attention-reallocation share could plausibly exceed 40% in the
high-r / low-V corners of the trained reward landscape — a
finding that, if observed, would *not* refute the paper's
substantive claim, just the categorical version. The user's
follow-up experiments should look for this corner-case behaviour
specifically.

### Loose ends

1. **The r = 0.3 paper-vs-replication disagreement.** The paper's
   text "96%" and my 0.85 differ by 11 percentage points. The
   paper's Figure 2 visual reading is consistent with my 0.85. The
   discrepancy is unlikely to be a code bug (r = 1.0 and r = 3.2
   match precisely). Most likely it is a transcription error in the
   manuscript text. Confirming this would require either (a) the
   paper's actual computational code (not provided), or (b) the
   authors' clarification. Flag for owner attention.
2. **The V = 1/N degeneracy as a recurring model edge case.**
   CR-014 noted the V = 1/N boundary in the context of C4
   (no-inversion). The current run surfaces the same boundary
   driving low CF in variant B. The boundary is in the paper's
   primary sweep but is not discussed. A focussed verdict on the
   V = 1/N corner (a new spawned task) would unify the C1, C4, and
   any future low-V findings under a single derivation: "what
   exactly happens at the validity-symmetric boundary, and which
   of the paper's claims hold there?"
3. **The "validity-attention gain" naming at V = 1/N.** At V = 1/N
   the gap R(P2) - R(P3) is not driven by validity (there is none).
   It is β/γ-asymmetry-driven attention reallocation at v = 1. The
   policy decomposition does not distinguish these mechanisms. A
   re-derivation attack (similar to CR-001's analytic skeleton for
   C2) could partition the R(P2) - R(P3) gap into a
   validity-driven component (scaling with V - 1/N) and an
   asymmetry-driven component (scaling with r at V = 1/N). Flagged
   as a follow-up.
4. **Literature on empirical criterion-fraction floors.** The wiki
   does not appear to contain a primary study that directly measures
   "what share of value-related reward gain comes from criterion
   adjustment vs. attention reallocation" in a controlled Posner
   change-detection task. If such a study exists, citing it would
   provide independent empirical evidence on the floor. Flagged as
   a potential CR-002.5 literature deepening.

### Wiki cross-references

§11 keyword sweep. Most relevant wiki entries (the full sweep notes
are in `Critique/evidence/C1--criterion-fraction-floor.md`):

- [[muller_findlay1987_sensitivity_criterion]] — cited in §"Version
  0.1 / Evidence"; foundational SDT-cueing source.
- [[hawkins1990_attention_detectability]] — cited; foundational
  sensitivity-side cueing source. Unrelated to the specific floor.
- [[luo_maunsell2018_criterion_sensitivity]] — cited in
  "Implications for PRISM" and "Evidence"; neural-substrate
  dissociability.
- [[sridharan2017_sc_sensitivity_bias]] — cited as the strongest
  empirical convergence with the criterion-dominates spirit.
- [[carrasco2011_visual_attention_25y]] — cited as background; not
  load-bearing.
- [[failing_theeuwes2018_selection_history]] — flagged for follow-up.
- [[hickey2010_reward_salience_acc]] — flagged for follow-up.
- [[reynolds_chelazzi2004_attentional_modulation]] — not consulted;
  bears on gain modulation, more relevant to A2.
- [[reynolds_heeger2009_normalization]] — not consulted; bears on
  the β/γ asymmetry foundations, more relevant to A2.

No new wiki stubs were added in this run.
