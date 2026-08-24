# Publication plan — "A recurrent vision transformer shows signatures of primate visual attention"

Morgan, Albanna, Herman. Synthesized 2026-06-21 from the three James meetings
(2026-04-14, 2026-04-28, 2026-06-09), the manuscript+supplement, and local experiment status.

---

## 0. The one thing that matters most: scope discipline

James's most recent guidance (2026-06-09) is explicit and it **overrides the
architecture-exploration program** currently consuming the laptop:

> "I think the architectural changes probably don't make sense [for this manuscript]."
> "this model learns from reward, unlike every other attention model … and the attention
> perturbations. I just want to lean heavily on that."
> "I want to use common non-human-primate attention task structures … versus just validity."

This splits cleanly into **two papers**:

- **Paper A — the empirical ARVIT manuscript** (the named manuscript). Keep the
  *existing* canonical architecture (multiplicative recurrent ViT + xLSTM + distributional
  actor–critic). Train it with the new stable **harness** on a **battery of standard NHP
  attention tasks**, add **causal-perturbation predictions**, fix the analyses James flagged.
  This is the fix for the first-submission reviewers' "limited in scope" critique.

- **Paper B — the normative theory preprint** ("when is attention beneficial" /
  performance-asymmetry / accidental-hit / set-size). Short, focused, bioRxiv, fast venue.
  James first author; cited by Paper A.

**Out of scope for both papers** (→ a *future, separate* deep-dive): split actor/critic
pathways, cross-attention, broadcast/FiLM feedback, VQ codebook ("attention as lookup
table"), the v11/v12/v13/v14/v15 ladder. These are good research but James has said twice
they do not belong in the publishable manuscript, and the split-actor/critic + cross-talk
variants empirically *destroy* the cueing effect (v11_part3/part4 collapse; the
"made the model more powerful but lost the cueing effect" result).

---

## 1. Paper A — the empirical ARVIT manuscript

### 1a. What is already done (do NOT redo)
- Canonical model + N=4 validity task; psychometrics/chronometrics; validity→threshold
  shift; cueing effect strongest at 100% (Figs 1–3).
- Attention dynamics: cue-lock, maintenance through blank, anticipatory pre-change,
  onset dip, capture (Fig 4).
- Causal α-perturbation → FEF/SC parallels incl. SC "dual effect" (Fig 5).
- Alternative-model ablations (Mem-as-Tokens, Additive, Supervised-actions/beliefs) →
  multiplicative + RL necessary (Table 1).
- **Supplement already has the SDT d′-vs-criterion decomposition** (engages Luo & Maunsell
  2018 and Gupta 2024), TD-error/value, entropy/uncertainty (Monosov), decoding analyses.

### 1b. Cheap analysis fixes James explicitly asked for — DO FIRST
- **E5. Per-validity / per-proportion breakdowns.** Re-plot performance-vs-reward and the
  cueing/validity effects split by each validity level. James predicts effects concentrate
  at high validity, near-zero at low validity. (2026-06-09 ask.)
- **E6. Attention-map visualization fix.** Stop averaging over full 5×5 quadrants (incl.
  irrelevant border sub-patches); use the single relevant patch / proper normalization that
  sums to 1. Then **re-run the attention-ramping analysis restricted to a fixed change-time
  subset** to disambiguate evidence-integration from a variable-change-time averaging
  artifact. Needed before any attention map is trustworthy.

### 1c. The core new program — the NHP task battery (the reviewer fix)
Implement each task in `ChangeDetectionEnv` (the env is a clean gym env; see §4 for the
concrete hooks), train the **canonical** model with the **harness**, and for each task run
the same downstream pipeline (behavior → SDT → causal perturbation → prediction).

- **E1a. Luo & Maunsell reward-structure task.** Colored/value cue; "sensitivity sessions"
  (large reward at one location regardless of hit/CR) vs "criterion sessions" (manipulate
  hit-vs-correct-reject reward ratio); event-locked forced response (respond within ~2 steps
  / guaranteed later super-threshold change). → directly engages their sensitivity claim.
- **E1b. Krauzlis attend-here/ignore-here selective task.** Uncued changes must be ignored
  (declaring on an uncued change = 0 reward) → the ∂EV/∂HR_uncued = 0 paradigm; the cleanest
  causal-perturbation testbed.
- **E1c. (optional) Baruni/Salzman orientation-discrimination task.** 2-AFC orientation
  judgment (toward vertical vs horizontal) with relative-value cues (target-in-RF value vs
  distractor); criterion can't be gamed → tests absolute-vs-relative value coding.

- **E2. Behavioral signatures per task** (reuse logistic-fit + Bayesian CIs).
- **E3. d′-vs-criterion decomposition per task** (extend the existing Supplement SDT
  analysis). Target headline: the model **reconciles the V4 literature** — bias at
  *change-time* → sensitivity (d′); reward/value structure → criterion; which one a given
  paradigm exposes depends on its design. This answers James's "is value modulation a
  separate signal?" puzzle architecturally.
- **E4. Causal attention perturbations per task + NOVEL predictions.** Clamp α at cue-time
  and change-time; state what the analogous NHP manipulation (FEF/SC/LIP microstim or
  inactivation) should produce in each task. **Vet that the predictions are non-pedestrian
  before committing** (James's condition). This is differentiator #2.

### 1d. The set-size bridge (your 9-stimulus interest) — connects A and B
- **E7. Set-size sweep K = 2, 4, 9** on the **canonical** architecture + harness. Show the
  cueing/false-alarm benefit and the magnitude of attention allocation **grow with set
  size**, matching Paper B's gradient prediction. This is the empirical confirmation of the
  theory's novel core and your own hypothesis ("more significant attention usage at 9").
  **Caveat:** the current `setsize9` run uses the v11_part2 *cross-talk* architecture (out of
  scope) and may have collapsed to always-wait (the v12 config notes cross-attn+broadcast
  both collapsed on 9-stim). Re-run on the canonical model. See §3.

---

## 2. Paper B — the normative theory preprint

Short, self-contained, fast venue. The genuinely novel core James verified ("no one has
taken this approach … of looking at when it is valuable to have a difference in performance
in an attention task").

- **T1. Write the algebra independently of the Claude draft.** EV as a linear function of
  {HR_cued, HR_uncued, FAR_cued, FAR_uncued} given reward structure and validity; attention
  defined operationally as a **performance asymmetry** (HR_cued ≠ HR_uncued); the global
  optimum (all hits, no FA) collects all reward but is *not* attention.
- **T2. The accidental-hit + set-size result (the headline).** In a union/non-spatial
  binary-response task, raising the uncued false-alarm rate is beneficial because some FAs
  are accidentally real hits; FA converts into hit ("injects a criterion component"). This
  benefit **trades off at K=2, is flat at K=3, flips positive at K=4**, and should keep
  growing toward K=9. Vanishes for spatial responses or discrimination tasks.
- **T3. Unified gradient-space map of paradigms.** Validity, VDA, Luo & Maunsell sensitivity,
  Krauzlis cluster together; Baruni discrimination points orthogonally (hit-rate axis only).
- **T4. Resolve/scope the V=1 anomaly.** Confirm whether the 100%-validity deviation from the
  gradient prediction arises *only* when the net is trained with a 100%-valid cue (a
  generalization/task-structure artifact) — not a gradient effect.
- **T5. ARVIT consistency plot.** Observed cueing effect vs predicted gradient differential
  G = ∂EV/∂HR_cued − ∂EV/∂HR_uncued across trained nets; also the experimental-design lever
  (target a large G to manufacture a large cued-vs-uncued difference).
- **T6. Define G properly; clean the figures** (drop the unified-colormap heat maps James
  disliked).

Meta-decisions that are James's, not ours: final theory/empirical split, target venue,
authorship. We support, we don't decide.

---

## 3. Verdict on your in-flight experiments

| Experiment | Verdict | Why |
|---|---|---|
| **9-stimulus run (setsize9)** | **Keep, but re-scope** | It's the empirical set-size bridge (E7). But re-run on the *canonical* arch + harness, not the v11_part2 cross-talk variant (out of scope, may have collapsed). |
| Split actor/critic (v11_part3/4) | **Defer / dead-end for cueing** | Empirically destroys the cueing effect (collapse to always-wait). Matches James's own "lost the cueing effect" result. |
| Cross attention | **Defer** | Architectural exploration; separate deep-dive. |
| Attention-as-lookup-table (VQ codebook, v12) | **Defer → its own future paper** | You already sensed this; James's scope guidance agrees. |
| Broadcast + FiLM (current live runs) | **Defer** | Architectural changes James explicitly excluded from this manuscript. These are the Herman/Morgan broadcast-feedback idea — good, but not this paper. |

**Compute note:** the three live MPS jobs (`setsize9_v12`, `setsize9_broadcast`,
`v11_part2_broadcast`) are all *off the critical path* for the paper. Freeing that compute
lets you run the canonical-arch battery (E1) and set-size sweep (E7) one job at a time
(laptop CPU must not be over-subscribed).

---

## 4. How to set up the battery tasks in `ChangeDetectionEnv`

The env (`reset()` sets `cue_index`, `proportion`, `change_true`, `change_index`,
`orientation_change`, `valid`; `step()` has 2 actions and the reward branch) is the single
hook point:

- **Value/reward (Luo & Maunsell):** add `cue_value` (e.g. red=5 / blue=1) drawn in
  `reset()` and rendered into the cue; in `step()` pay `cue_value` on a correct cued
  detection. "Sensitivity session" = high value at one location regardless of hit/CR;
  "criterion session" = scale the hit-vs-correct-reject reward ratio. Add an event-locked
  response window (declare within ~2 steps of change or it's a miss) so the agent can't wait
  out the trial.
- **Krauzlis attend/ignore:** in `step()`, declaring on a change at an *uncued* location pays
  0 (the change is to be ignored); only cued-location changes are rewarded.
- **Baruni discrimination:** change `action_space` to the 2-AFC orientation response and pay
  on correct discrimination (no FA/CR branch); cues carry relative target-vs-distractor value.
- **Set size:** generalize `N_STIMULI` (the setsize9 env already does 9 on a 3×3 grid);
  K=2 and K=4 are sub-cases (mask unused locations). Keep patch size / VAE fixed for
  apples-to-apples.

---

## 5. Suggested sequence

1. **Week 0 (now, cheap):** E5 (per-validity breakdowns) + E6 (attention-map fix + fixed
   change-time ramp). These are direct James asks and need no new training.
2. **Week 0–1:** T1–T2 (write the theory algebra + set-size derivation) — paper B's core, no
   compute. Vet the V=1 anomaly (T4).
3. **Week 1–3:** E1 battery — implement Luo & Maunsell + Krauzlis envs, train canonical model
   with harness (one job at a time), run E2–E4 per task.
4. **In parallel:** E7 canonical set-size sweep (K=2/4/9) → the A↔B bridge.
5. **Week 3+:** T3/T5 (gradient-space map + consistency plot), assemble Paper B preprint;
   fold battery + predictions into Paper A; draft the "novel causal-manipulation predictions"
   section.

---

## 6. What I can do for you now (respecting the laptop)
- Implement E5/E6 and the battery envs (E1) as code — read/write only, no training.
- Write the Paper B theory LaTeX (T1–T2) from the verified algebra.
- Load a trained checkpoint and run a specific analysis (SDT, decoding, perturbation)
  **one at a time, thread-capped, only after the live training jobs are stopped** — tell me
  which and I'll do it carefully.
- Draft the Paper A "task battery + predictions" section and the reviewer-response framing.
