---
type: evidence-dossier
claim_id: C1
short_slug: criterion-fraction-floor
prompt_version: "0.1"
last_updated: 2026-05-17
runs_touched:
  - run-003 (CR-002, sensitivity-attack, 2026-05-17)
---

# Evidence dossier — C1 (criterion fraction floor)

Accumulating literature and replication evidence on the paper's
claim that the criterion fraction is bounded in [0.60, 0.96] across
the swept 4,410-combination parameter grid.

## Version 0.1 — 2026-05-17 (run-003, CR-002)

The first attack on C1 is a **replication-based sensitivity probe**
(documented at `Critique/replications/C1--criterion-fraction-floor/`).
The principal new evidence is the agent's own replication output,
which finds CF as low as 0.30 inside the paper's swept space. The
following entries record wiki / literature evidence consulted in the
course of this run.

### Source: own replication (CR-002, 2026-05-17)

- **Bears on the claim how:** Direct numerical replication of the
  paper's 4,410-row primary sweep using mission §2 model definitions.
  Implements the policy decomposition (P1, P2, P3, P4) exactly as
  the paper describes; verifies the model matches the paper at two
  of three §4.1 reference points (r = 1.0 → CF = 0.728 vs paper
  0.73; r = 3.2 → CF = 0.642 vs paper 0.64).
- **Direction:** contradicts (the categorical 60–96% claim);
  supports (the spirit of "criterion typically dominates").
- **Quantitative weight:** strong. Independent re-implementation
  agrees with the paper's text at two of three reference points and
  with the paper's *figure* at all three. The 11-percentage-point
  disagreement at r = 0.3 is in the *paper's* favour-of-the-claim
  direction (so my replication is conservative).
- **What the verdict file did with this:** drove the verdict
  movement from OPEN to CONTESTED. Specific numerical anchors:
  variant A min CF = 0.5587 at (r=10, V=0.55, v=1); variant B min
  CF = 0.3040 at (r=10, V=0.25, v=4).

### Source: [[muller_findlay1987_sensitivity_criterion]] (depth: full)

- **Bears on the claim how:** Müller & Findlay 1987 is the
  foundational psychophysical demonstration that Posner-style cueing
  produces *both* sensitivity (d') changes and criterion (β)
  changes, which can be dissociated by SDT analysis. The paper's
  entire criterion-vs-attention partition inherits this framework.
- **Direction:** supports (the *dissociability* of the two
  mechanisms); does not directly bear on the CF *floor* value.
- **Quantitative weight:** medium-to-strong. Foundational paper for
  the SDT methodology used; cited by the target paper as ref [1].
  Müller & Findlay measure criterion shifts but do not quantify a
  criterion-fraction floor, so the wiki entry is silent on whether
  CF ≥ 0.60 is empirically plausible. Their data is consistent with
  CF being large in human cueing tasks, but does not pin a number.
- **What the verdict file did with this:** cited as the canonical
  source of the SDT-cueing dissociation; noted as not providing
  independent numerical evidence on the CF floor.

### Source: [[hawkins1990_attention_detectability]] (depth: full)

- **Bears on the claim how:** Hawkins 1990 extends Müller & Findlay's
  dissociation with a denser psychophysical sweep, showing that
  attention produces measurable *sensitivity* improvements
  (not just criterion shifts) when the discrimination is hard. The
  paper cites this as ref [2] and uses it to motivate the
  sensitivity-side mechanism.
- **Direction:** unrelated on inspection re: the CF floor. Bears on
  whether attention has a *non-zero* sensitivity component (yes),
  not on whether criterion adjustment captures *most* of the
  value-related reward in a normative model.
- **Quantitative weight:** medium for the model's foundations; not
  weight-bearing for the specific [0.60, 0.96] range.
- **What the verdict file did with this:** cited as part of the
  paper's foundational SDT-cueing literature; not load-bearing for
  the CF-floor refutation.

### Source: [[luo_maunsell2018_criterion_sensitivity]] (depth: full)

- **Bears on the claim how:** Luo & Maunsell 2018 localises the
  criterion vs sensitivity components to LPFC vs visual cortex
  respectively, demonstrating their *neural* dissociability. This
  is the empirical foundation for the paper's claim (§5.4) that the
  asymmetry ratio r reflects two dissociable mechanisms.
- **Direction:** supports (the model's premise of independent
  benefit and cost). Does not directly bear on the CF floor.
- **Quantitative weight:** strong for the *modelling-assumption*
  side (Luo & Maunsell licence the independent-mechanism story);
  not weight-bearing for the specific [0.60, 0.96] range.
- **What the verdict file did with this:** cited in the
  "Implications for PRISM" block as biological grounding for the
  criterion vs attention partition the user's recurrent ViT
  architecture also implements (Feedback Transformer's V1-level
  gain = sensitivity component; central self-attention substrate =
  criterion component, per the user's program).

### Source: [[sridharan2017_sc_sensitivity_bias]] (depth: full)

- **Bears on the claim how:** Sridharan et al. develop a
  *multialternative SDT framework* (the most direct empirical
  analogue of the target paper's N-location SDT setup) and apply it
  to re-analyse four SC-attention studies. **Principal finding:
  bias (criterion) is the predominant SC attention effect, not
  sensitivity.** This is direct empirical convergence with the
  target paper's normative criterion-dominates claim.
- **Direction:** supports (the spirit of C1: criterion dominates).
  Does not bear on the specific [0.60, 0.96] range — Sridharan
  measures bias and sensitivity contributions to attention performance
  but does not quantify a "criterion fraction" of total available
  reward gain. The bias-dominates finding is qualitatively aligned
  with CF ≥ 0.5, but is silent on whether CF ≥ 0.6.
- **Quantitative weight:** strong for the qualitative point (bias /
  criterion is the *primary* SC attention mechanism in
  multialternative tasks); medium for the model's general
  premises.
- **What the verdict file did with this:** cited as the most
  directly comparable *empirical* finding to the paper's normative
  result. Noted that the empirical literature has not directly tested
  the specific 0.60 floor; that test would require psychophysical
  data on a Posner change-detection task with controlled (r, V, v)
  manipulation, which to the agent's knowledge has not been
  published.

### Source: [[carrasco2011_visual_attention_25y]] (depth: summary)

- **Bears on the claim how:** Carrasco's 25-year review summarises
  the cumulative evidence that spatial attention enhances perceptual
  sensitivity at attended locations. This is the *opposite-direction*
  evidence — sensitivity gains are real and consequential.
- **Direction:** does not directly contradict C1 — C1 is about
  *relative share* of value-related reward gain, not about whether
  attention has a sensitivity component. Carrasco's review does not
  partition the share.
- **Quantitative weight:** medium for the broader landscape; light
  for the specific CF floor.
- **What the verdict file did with this:** cited as part of the
  background showing attention's perceptual reality, noting it does
  not bear on the criterion-share number.

### Sources NOT consulted in this run but flagged for future C1 work

- `failing_theeuwes2018_selection_history` — selection history
  literature; might bear on whether trained agents (PRISM, e.g.)
  exhibit criterion-side or attention-side value encoding. Flag for
  follow-up if a learning-dynamics attack on A4 makes the
  cross-reference relevant.
- `hickey2010_reward_salience_acc` — ACC reward-modulated attention;
  bears on whether reward propagates to criterion (decisional) or
  attention (perceptual) machinery in trained animals. Flag for
  future CF-prior-empirical-literature deepening.

## Wiki cross-references (run-003)

This is the §11 sweep block referenced by the verdict file:

- [[muller_findlay1987_sensitivity_criterion]] — cited in
  verdict §"Version 0.1 — Evidence"; foundational SDT-cueing source.
- [[hawkins1990_attention_detectability]] — cited; foundational
  sensitivity-side cueing source. Unrelated to the specific floor.
- [[luo_maunsell2018_criterion_sensitivity]] — cited in
  "Implications for PRISM" block; neural-substrate dissociability.
- [[sridharan2017_sc_sensitivity_bias]] — cited as the strongest
  empirical convergence with the criterion-dominates spirit.
- [[carrasco2011_visual_attention_25y]] — cited as background; not
  load-bearing.
- [[failing_theeuwes2018_selection_history]] — flagged for follow-up,
  not consulted.
- [[hickey2010_reward_salience_acc]] — flagged for follow-up, not
  consulted.
- [[reynolds_chelazzi2004_attentional_modulation]] — not consulted;
  bears on attentional gain modulation, may inform A2 follow-ups.
- [[reynolds_heeger2009_normalization]] — not consulted; bears on
  the model's β/γ asymmetry foundations, more relevant to A2.

No new wiki stubs were added in this run.
