---
type: verdict
claim_id: C4
claim_statement: "Inverted attention (α* < 1/N) is never optimal across the paper's 4,410-row primary sweep."
paper_section: §4.5
current_label: CONFIRMED-CONDITIONAL
attacks_tried:
  - vector: re-derivation
    run_id: run-006
    outcome: empirical claim survived; theoretical justification refined; conditional V ≥ 1/N shown necessary
  - vector: literature
    run_id: run-007
    outcome: claim survived within V ≥ 1/N scope; distractor-suppression literature maps to the anti-cued (V<1/N) regime where the model itself predicts inversion, so it is consistent not contradictory; value-driven capture positively supports no-inversion at the cued location
load_bearing_for:
  - "§4.5 (named claim)"
  - "§5.1 (mechanistic argument that VDA is a zero-sum reallocation game)"
  - "§5.2 (experimental-design recommendation — implicitly assumes V ≥ 1/N)"
last_updated: 2026-05-19
prompt_version_observed: 0.1
---

# Verdict: Inverted attention is never optimal (C4)

## Claim as written in the paper

§4.5 ("Inverted Attention is Never Optimal"), verbatim:

> Across all 4,410 rows of the primary sweep — spanning $r \in [0.1, 10]$, $V \in [0.25, 1.0]$, $v \in \{1, \dots, 5\}$, and both reward variants — the optimal $\alpha^\star$ is always $\geq 1/N$. The $\alpha$ grid was extended below $1/N$ (down to 0.02), allowing the optimiser to discover inverted attention (preferentially attending away from the high-value location) if it were ever beneficial. It never is.
>
> This result follows from the reward structure: attending away from the high-value cued location means (a) the cued location's $d'$ drops below baseline, scaled by the cost factor $\gamma$, while (b) uncued locations' $d'$ rises above baseline, scaled by the benefit factor $\beta$. Since $v \geq 1$ and $V \geq 1/N$, the weighted reward loss at the high-value cued location always exceeds the gain at low-value uncued locations, regardless of $r$. In the most cost-dominant regime ($r \to 0$), the optimal strategy converges to uniform attention ($\alpha^\star = 1/N$), never below it.

## Why this matters

C4 is one of the paper's three categorical claims (along with C1's *criterion fraction always $\in [0.60, 0.96]$* and C3's *negligible VDA at $V \geq 0.75$*). Of the three, C4 is the most theoretically loaded: it asserts a *structural* property of the model — that one half of the $\alpha$ space is normatively dead — rather than a numerical regularity. The mechanistic argument in §5.1 ("VDA is a zero-sum reallocation game") implicitly leans on C4 to justify the framing: if inversion could ever be optimal, "zero-sum reallocation" would have a non-trivial third option (attend *away*). The §5.2 experimental-design recommendation (high-V paradigms should show negligible VDA) similarly assumes the canonical attention-toward-cue allocation is the only normative option.

For the PRISM program (§3.5 of mission): C4 makes a falsifiable normative prediction. If a PRISM-trained agent at $V \geq 1/N, v \geq 1$ ever exhibits $\alpha(t) < 1/N$ in steady state, that is either a learning failure or a model mismatch. Conversely, if PRISM is trained under anti-cue conditions ($V < 1/N$), the normative prediction (this verdict, §6) is that the agent *should* learn $\alpha^\star < 1/N$ — a strong testable claim.

---

## Version 0.1 — 2026-05-18

### What this version did

**Re-derivation attack** (one of mission §3.2's four attack vectors).
Re-derived the one-sided boundary derivative $\partial \mathbb{E}[R]/\partial \alpha|_{1/N}$ from the model's defining equations and characterized when the local-test interpretation of §4.5 holds. Then ran a numerical sweep (Step A, Step B, Step C in the companion script `Critique/replications/C4--no-inversion/run.py`) to corroborate the analytical predictions and probe the anti-cue regime the paper does not test.

### Verdict

**WEAKLY-SUPPORTED.** The empirical headline of C4 survives the first attack vector, but the *theoretical justification* the paper offers in §4.5 is incomplete: a refined derivation is needed before this can elevate to CONFIRMED-UNDER-ATTACK. Specifically:

1. **Empirical claim survives.** Across the 4,410 rows of the primary sweep ($N=4$, $V \in [1/N, 1.0]$, $v \in \{1,\dots,5\}$, both variants), no row has $\alpha^\star_{P_1} < 1/N$ or $\alpha^\star_{P_2} < 1/N$. Independently corroborated by the existing CR-002 phase-A sweep at `Critique/replications/C1--criterion-fraction-floor/output/results.json` (which records $\alpha^\star$ for all 4,410 cells; we verify zero inversions by direct query) and by Step B of CR-004 (fine-grid $\Delta\alpha = 0.005$ at the cells flagged by the boundary closed form as analytically most-adversarial).

2. **Theoretical justification refined.** The paper's "regardless of $r$" wording reads as a local cost-vs-benefit argument at $\alpha = 1/N$. That local argument is **wrong**: the left one-sided derivative is

   $$\left.\frac{\partial \mathbb{E}[R]}{\partial \alpha}\right|_{1/N^-} = \frac{2 d'_{\max} f'(1/N)}{r+1}\left[A_0 - \frac{r}{N-1} B_0\right]$$

   (derivation §3, where $A_0, B_0$ are $r$-independent boundary partials), which changes sign at $r^\star_{\mathrm{inv}}(V, v, N) := (N-1) A_0/B_0$. **49.0% of the swept $(V, v, \text{variant})$ cells at $N=4$ have $r^\star_{\mathrm{inv}} \in [0.1, 10]$** — the paper's swept $r$ range straddles the local-inversion threshold in roughly half of cells. At the corner $(V=1/N=0.25, v=1)$, $r^\star_{\mathrm{inv}} = 1$ exactly (derivation §5), and for $r > 1$ the point $\alpha = 1/N$ is a local *minimum* with both branches increasing $\mathbb{E}[R]$. The model is genuinely bimodal at this corner.

3. **Correct mechanism named.** What guarantees no global inversion is a **location-count asymmetry** combined with a value-weight inequality, not the local balance argument:

   - At the right extreme $\alpha \to 1$, the single cued location reaches $d'_c = d'_{\max} f(1) = d'_{\max}$ (per-location ceiling).
   - At the left extreme $\alpha \to 0$, the $N-1$ uncued locations each reach only $d'_u = d'_{\text{base}} + \beta[d'_{\max} f(1/(N-1)) - d'_{\text{base}}]$, with $f(1/(N-1)) < 1$ for $N \geq 3$. **No uncued location reaches $d'_{\max}$** because they share what the cued has alone.
   - The per-channel reward weights $w_c = V v$ and $w_u = (1-V)/(N-1)$ satisfy $w_c \geq w_u \iff V \geq 1/[(N-1) v + 1]$. For $v \geq 1$, this simplifies to $V \geq 1/N$ — the paper's stated condition. Equality only at $(V=1/N, v=1)$.

   The right branch dominates globally because the *bigger* d' lives on the *more-valuable* channel. The argument is *structural* (depends on $N \geq 3$ + $w_c \geq w_u$), not local (cost vs benefit at $\alpha = 1/N$).

4. **The conditional V ≥ 1/N, v ≥ 1 is necessary.** Step C(iii) directly tests the regime where the location-count argument flips: at $V < 1/N$ with $v = 1$ and $N = 2$, the global optimum is $\alpha^\star < 1/N$. Specifically, at $(V=0.25, v=1, N=2)$: $\alpha^\star_{\mathrm{global}} = 0.180$ at $r=1$, dropping to $\alpha^\star_{\mathrm{global}} = 0.020$ at $r=10$. Inversion is normatively optimal — the model produces it cleanly when $w_c < w_u$. These cells are *outside* the paper's primary sweep ($N = 4$ only) but *inside* the paper's stated V-range $[0.25, 1.0]$ if one were to interpret §4.5's "spanning ... $V \in [0.25, 1.0]$" as a property of the model independent of $N$. The paper's wording (the closing "never below it" with no $V \geq 1/N$ qualifier on the categorical sentence) overstates the model's robustness.

### CR-019 resolution

CR-019 (spawned by CR-014) asked whether C4's categorical statement should be tightened to $V > 1/N$ (strict) rather than $V \geq 1/N$ (weak). This run resolves CR-019 cleanly:

- At $V = 1/N$, $v = 1$, $r \leq 1$: the model is at the boundary of the location-count asymmetry; $\mathbb{E}[R]$ is constant in a neighborhood of $\alpha = 1/N$; the optimum picks $\alpha = 1/N$ but ties exist. CR-014 found a $P_2$-side $\alpha^\star = 0.02$ which is one of many tied optima.
- At $V = 1/N$, $v = 1$, $r > 1$: the right branch wins strictly (location-count asymmetry breaks the tie). Right-branch optimum exceeds left-branch optimum by 0.005 to 0.014 reward units across $r \in (1, 10]$ at $(V=0.25, v=1, N=4)$ — small but non-zero.

C4's wording does **not** require strengthening to $V > 1/N$: $V = 1/N$ is fine. The CR-014 numerical $\alpha^\star = 0.02$ was a *left-branch local maximum* found because the value-blind $P_2$ at $v = 1$ has a degenerate objective (ties broken by grid+argmax). The right-branch global optimum is the canonical answer. **CR-019 is answered in the negative**; no wording change is needed in C4 to address it. The verdict body documents the bimodality so a future reader does not mistake the left-branch local max for a counterexample.

### Evidence

- Closed-form derivation: `Critique/derivations/C4--no-inversion.md` (10 sections).
- Numerical replication: `Critique/replications/C4--no-inversion/run.py` and `output/results.json`.
- Independent corroboration of zero inversions across 4,410 primary-sweep rows: `Critique/replications/C1--criterion-fraction-floor/output/results.json` (phase_A.rows; query for `alpha_p1 < 0.25` or `alpha_p2 < 0.25` returns empty).
- Anti-cue counterexample: Step C(iii) of CR-004 — at $(V=0.25, v=1, N=2, r=1)$: $\alpha^\star_{\mathrm{global}} = 0.180 < 1/N = 0.5$.
- Boundary symmetric corner: derivation §5 — $r^\star_{\mathrm{inv}}(V=1/N, v=1) = 1$ exactly, independent of $N$.

### Wiki cross-references

Mission §11 keyword sweep performed across the anchor list and C4-specific keywords (inverted attention, anti-cue, counterpredictive cue, distractor suppression, normative observer, priority map, IOR). Hits:

- [[posner1980_orienting]] — full-depth. Classic chance-validity (V=1/N=0.25 at $N=4$) result: no validity effect. **Cited** as the empirical analog of the model's V=1/N degeneracy: when the cue carries no spatial information, observers do not reallocate attention. Direction: supports C4 at the V=1/N corner.

- [[failing_theeuwes2018_selection_history]] — full-depth. Value-driven attentional capture: observers fail to suppress previously-rewarded distractors even when normatively they should. **Cited** as both supporting C4 ("inversion away from value is hard") and *caveating* it ("observers may *fail to invert* when normative theory says they should — but they may also fail to *not* invert if they have learned to suppress; see suppression-history literature below"). Direction: mixed — supports the no-inversion behavioural pattern at $V \geq 1/N$ but signals that the *behavioural* picture is more complicated than the model's normative picture.

- [[hickey2010_reward_salience_acc]] — full-depth. Single-trial reward at $V=1/N$ shifts next-trial attention toward the high-reward location. **Cited** as supporting the model's location-count argument: the reward signal pulls observers toward the rewarded location, not away from it. Direction: supports.

- [[thomsen2005_conflicting_cues_fmri]] — full-depth. Exogenous-invalid / endogenous-valid: observers down-weight an invalid peripheral cue, but with a measurable RT cost. **Cited** as the closest behavioural analog of anti-cue inversion: observers *can* partially invert when they know the cue is misleading, but the inversion is incomplete and effortful. Direction: contradicts the strong reading of C4 ("never optimal") if applied to "never observed" but the model is normative, not descriptive — this is a noted gap, not a refutation.

- [[luo_maunsell2018_criterion_sensitivity]] — full-depth. Cued macaque task: reward asymmetry shifts criterion not sensitivity. **Cited** as indirect support: in the cued ($V \geq 1/N$) regime, reward effects load on criterion, consistent with C4 (no allocation inversion observed).

- [[sridharan2017_sc_sensitivity_bias]] — full-depth. SC manipulations affect bias at high V. **Cited** as indirect support for the same reason.

- [[ghose_maunsell2002_task_timing]] — full-depth. Attention as optimal resource allocation. **Cited** as the normative-framing parallel — the paper's modelling tradition.

- [[reynolds_heeger2009_normalization]] — full-depth. Normalization model. **Cited** at the concept level: the normalization framework has no symmetric "inversion" branch and so the no-inversion claim is inherited from the same kind of gain-asymmetry argument the paper makes. Direction: supports the no-inversion *spirit* but not via the same mechanism (normalization is divisive-gain, not allocation).

- [[bisley_mirpour2019_priority_map]] — full-depth. Priority map architecture (LIP/FEF). **Cited** as the neural substrate that *implements* attentional priority but does not, in standard formulations, support inversion (negative weights). Direction: consistent with no-inversion under $V \geq 1/N$ but does not adjudicate the conditional.

- [[bisley_goldberg2010_parietal_priority]] — full-depth. Same vein. **Unrelated on inspection** for the specific inversion question; cited as background.

- [[desimone_duncan1995_biased_competition]] — full-depth. Biased competition. **Cited** at concept level: cued location wins through inhibition of competitors, which is the inverse mechanism of inversion. Supports no-inversion.

- [[koch_ullman1984_winner_takes_all]] — full-depth. Saliency map + WTA. **Unrelated on inspection** for inversion specifically — WTA selects the *max*, no concept of negative weighting in the canonical formulation.

- [[itti_koch2001_saliency_review]] — full-depth. Same. **Unrelated on inspection** for the specific inversion question.

- [[wolfe2021_guided_search_6]] — full-depth. Guided search. **Unrelated on inspection** for inversion; guided search has no negative weighting in its standard formulation, but the *prioritization* it implements is the same family of mechanism C4 references.

- [[mirpour2010_ppc_microstim]] — full-depth. PPC microstimulation biases saccade target selection. **Unrelated on inspection** for inversion — bias is toward, not away.

- [[hawkins1990_attention_detectability]] — full-depth. SDT-of-attention foundation. **Cited** as background for the model's SDT machinery; not specifically about inversion.

- [[gupta_sridharan2024_presaccadic_change]] — full-depth. Presaccadic attention does *not* facilitate change detection. **Spawned CR-031** as a candidate counterexample: if presaccadic attention can be allocated *against* a normatively-favored location without behavioural cost, the paper's normative framing may not match behaviour. Direction: tangentially constrains C4.

- [[herman_krauzlis2017_sc_change_detection]] — full-depth. SC in primate change-detection — same task class as the paper. **Cited** as the natural empirical substrate but does not directly speak to inversion.

- Concept page [[competition_emergent_predictive_coding]] — concept-level. **Cited** at the concept level for the priority/competition framing that underwrites the model's no-inversion result.

- Thread page `threads/the_user_architectural_program.md` — **Cited** for the §3.5 PRISM implications. The PRISM v1/v2 attention trajectories from `Prism/figures/avg_alpha_*.pdf` are the natural empirical test of C4 in a recurrent-network setting.

**Wiki entries not consulted but worth a future stub (spawned CR-032):**
- Wang & Theeuwes 2018 *Statistical learning of distractor locations* — distractor-suppression literature. Empirically, observers *do* learn to suppress (down-weight) high-probability-distractor locations, which is the behavioural near-analog of inversion at $V < 1/N$. Would constitute a literature-attack second vector on the refined C4 (V ≥ 1/N conditional).
- Geng 2014 *Attentional mechanisms of distractor suppression*.
- Anderson, Laurent, Yantis 2011 — value-driven capture origin paper.

Searched terms: *value-directed attention, reward-modulated attention, attentional capture, selection history, criterion shift, signal detection theory, d-prime, normalization model, gain modulation, surround suppression, priority map, LIP, FEF, V4, parietal, frontal eye field, biased competition, dopamine, RPE, basal ganglia, oculomotor, saccade, change detection, Posner cueing, cue validity, inhibition of return, inverted attention, anti-cue, counter-predictive cue, distractor suppression, normative observer*. Coverage: high (existing wiki has 236 papers, 15 concept pages, threads). No web fetches consumed this run (0 of soft cap 2).

### Loose ends

- **Second attack vector not yet executed.** Mission §3.1: elevation to CONFIRMED-UNDER-ATTACK requires two distinct attack vectors. The natural second vector is **CR-031 — literature attack** on whether human/primate observers in cued change-detection at $V \geq 1/N$ ever exhibit behavioural $\alpha^\star < 1/N$ (e.g. via fixation eccentricity or microsaccade-rate proxies), or whether distractor-suppression learning (Wang & Theeuwes 2018; Geng 2014) constitutes a *de facto* behavioural inversion. Until executed, the verdict cannot elevate beyond WEAKLY-SUPPORTED.

- **The β/γ kink at α = 1/N is unmentioned in the paper.** The derivation §1 surfaces a kink in $d'(\alpha)$ at $\alpha = 1/N$ whenever $r \neq 1$ — a non-smooth point in the value function. The paper's optimizer (grid search) is insensitive to this, but any gradient-based attentional model (e.g. PRISM's policy gradient) would not handle it cleanly. This is a candidate paper note for the authors (proposed wiki entry: "Smoothness of attention allocation models at the uniform point") rather than a verdict-shaping finding. Spawned **CR-033** as a low-priority sensitivity question: does the kink at $\alpha = 1/N$ affect the convergence of the joint optimum at α-grid resolutions coarser than $\Delta\alpha = 0.005$?

- **Anti-cue regime ($V < 1/N$) at $N = 4$.** Step C(iii) tested only $N = 2$ because at $N = 4$, $V_{\min} = 1/N = 0.25$ in the paper's sweep. A more thorough test would sweep $V < 1/N$ at $N = 4$ (e.g. $V \in [0.05, 0.20]$) and confirm the inversion threshold is the same closed-form $r^\star_{\mathrm{inv}}$. Spawned **CR-034** as a low-priority derivation extension.

### Next-attack recommendation

The strong next pick is **CR-031** — literature attack on whether behaviour-versus-normative-prediction matches in the cued ($V \geq 1/N$) regime. Two sub-questions:

(i) Does anyone report behavioural $\alpha^\star < 1/N$ at $V \geq 1/N$ via eye-tracking / microsaccade-rate proxies? (If yes, the paper's normative framing has a behavioural counterexample; verdict may move to CONTESTED.)

(ii) Is the distractor-suppression literature (Wang & Theeuwes 2018; Geng 2014; Vatterott & Vecera 2012) interpretable as behavioural inversion at $V \geq 1/N$ in the model's terms? (If yes, "inversion is never optimal" needs to be paired with "but observers may learn inversion-like suppression" — a richer story.)

Either sub-question is one wiki sweep + one web fetch (for Wang & Theeuwes 2018) away from a CONTESTED-or-CONFIRMED verdict elevation. The literature attack is the cheapest path to a second attack vector.

### Implications for PRISM v1/v2

C4 makes a direct, falsifiable normative prediction about PRISM-trained agents:

1. **At training conditions where $V \geq 1/N$ and $v \geq 1$** (the standard PRISM v1/v2 setup per `Prism/env.py`), the trained agent's attention trajectory $\alpha(t)$ should never settle below $1/N$. If it does, that is a learning failure or a model mismatch — a useful diagnostic.

2. **At anti-cue training conditions ($V < 1/N$)**, the trained agent *should* learn $\alpha^\star < 1/N$. The closed-form prediction from derivation §7: for $V = 0.25, v = 1, N = 2, r \in \{1, 5, 10\}$, the normative $\alpha^\star$ is $\{0.18, 0.02, 0.02\}$ respectively. PRISM trained under these conditions has a known target.

3. **The bimodality at $V = 1/N$ exactly** predicts that PRISM trained at $V = 1/N$ should be **history-dependent**: depending on initialisation, the agent may converge to either the right-branch global optimum or (rarely, in the $r > 1$ regime) get stuck in the left-branch local maximum. The user's `Prism/analysis/avg_alpha_*.py` trajectory analyses could test this — running multiple seeds at $V = 1/N, v = 1$ and checking the bimodal distribution of converged $\alpha^\star$ values would be a strong falsification target for the model.

The location-count asymmetry mechanism named in §6 of the derivation is a *qualitative* prediction that any policy-gradient attention learner with the same value structure should reproduce. This is a higher-leverage claim than the categorical no-inversion: it predicts which way PRISM's allocation will favor under variant value/validity structures.

---

## Version 0.2 — 2026-05-19

### Previous frontmatter (from Version 0.1)

```yaml
current_label: WEAKLY-SUPPORTED
attacks_tried:
  - vector: re-derivation
    run_id: run-006
    outcome: empirical claim survived; theoretical justification refined
last_updated: 2026-05-18
```

### What this version did

**Literature attack** (the second of mission §3.2's four attack vectors;
the first was the run-006 re-derivation). Adjudicated the two
sub-questions the Version 0.1 verdict flagged as the path to a second
vector:

- **(i)** Does the behavioural literature report $\alpha^\star < 1/N$ at a
  *validly cued / high-value* location ($V \geq 1/N$), e.g. via
  eye-tracking / microsaccade / fixation-eccentricity proxies?
- **(ii)** Is the distractor-suppression-learning literature
  interpretable as behavioural inversion *in the model's terms*?

Evidence gathered from the local wiki (Failing & Theeuwes 2018,
Hickey 2010, Posner 1980, Bisley & Mirpour 2019, Desimone & Duncan 1995,
Gupta & Sridharan 2024 — all full-depth) plus one PubMed pass
(2 calls: 1 search + 1 metadata batch) returning the canonical
statistical-learning-of-distractor-suppression cluster: Wang & Theeuwes
2018a (stubbed this run), Wang, Samara & Theeuwes 2019 (eye-tracking),
Kong et al. 2020 (biased-competition probe). Full dossier:
`Critique/evidence/C4--no-inversion.md` (Version 0.1 section).

### Verdict

**CONFIRMED-CONDITIONAL** (was WEAKLY-SUPPORTED). The label moves because
a *second distinct attack vector* (literature) has now failed to falsify
C4 within the paper's stated scope, and has independently corroborated
the conditional $V \geq 1/N$ that the run-006 re-derivation showed to be
necessary. It is **CONFIRMED-CONDITIONAL** rather than
CONFIRMED-UNDER-ATTACK because the claim provably *fails outside* that
scope (the model itself produces $\alpha^\star < 1/N$ at $V < 1/N$, per
CR-004), so the honest label is the one that spells out the conditional.

The reasoning, sub-question by sub-question:

1. **Sub-question (ii) — distractor suppression is not a counterexample.**
   The single behavioural phenomenon that looks like "attending below
   uniform to a location" is statistical-learning-driven suppression of a
   high-probability-**distractor** location (Wang & Theeuwes 2018a:
   reduced capture + reduced target-selection efficiency, spatial
   gradient, awareness-independent; Wang, Samara & Theeuwes 2019: fewer
   saccades land there, raised saccade latency to targets there;
   Kong et al. 2020: suppressing it reallocates resource to the target).
   But the suppressed location is the location *least* likely to contain
   the **target** — in the paper's model, a location with target-validity
   below $1/N$, i.e. **anti-cued**. CR-004/run-006 established in closed
   form that the model's normative optimum at $V < 1/N$ (with $v=1$, so
   $w_c < w_u$) *is* $\alpha^\star < 1/N$. So learned distractor
   suppression is the model's **own prediction** in the anti-cued regime,
   not a violation of C4's $V \geq 1/N$ claim. The phenomenon that
   superficially threatened C4 turns out to land exactly where the model
   independently says inversion *should* occur — a convergence, not a
   contradiction.

2. **Sub-question (i) — no inversion at the cued/high-value location.** No
   study reports the mirror effect: observers do *not* allocate below the
   uniform rate to a high-target-probability / high-value validly-cued
   location. Value-driven capture (Anderson-Laurent-Yantis-style, reviewed
   in Failing & Theeuwes 2018; single-trial in Hickey 2010) shows the
   *opposite* — attention is pulled *toward* reward-associated locations
   even maladaptively, resisting strategic suppression. The Gupta &
   Sridharan 2024 candidate counterexample (presaccadic attention not
   facilitating change detection) is a *failure of facilitation*, not
   active below-uniform allocation away from a cued location, so it does
   not falsify C4. Sub-question (i) resolves in the negative.

3. **Scope note (the load-bearing interpretive step).** There are exactly
   two ways to map distractor-location suppression onto the model's
   single-cued / homogeneous-uncued geometry, and **both leave C4 intact**:
   *(a)* identify the suppressed location with the model's cued slot ⇒ it
   is anti-cued ($V<1/N$) and the model predicts $\alpha^\star<1/N$ there
   (consistent); *(b)* identify it with one of the $N-1$ uncued slots ⇒
   the observer is allocating *heterogeneously* among uncued locations,
   which the model cannot represent (its uncued allocation is homogeneous
   at $(1-\alpha)/(N-1)$) — so it is *out of C4's scope* and governed by a
   separate, currently-unnamed homogeneity assumption (see Loose ends /
   proposed A8).

The substantive content of §4.5 (no inversion across the primary sweep),
§5.1 (zero-sum reallocation — *positively corroborated* by Kong et al.
2020's "suppress here ⇒ more there" reciprocity), and §5.2 (high-V design
recommendation) all survive. The only thing that remains contestable is
the paper's *categorical wording* ("never below it", with no $V \geq 1/N$
qualifier on the closing sentence), which run-006 already flagged.

### Evidence

- Evidence dossier: `Critique/evidence/C4--no-inversion.md` (Version 0.1
  section) — full per-source breakdown with directions and weights.
- New wiki stub:
  `research_db/papers/wang_theeuwes2018_statistical_learning_distractor_suppression.md`
  (depth: abstract; PubMed PMID 29309194, DOI 10.1037/xhp0000472). Audit
  clean (exit 0; 240 papers, 5 abstract-depth).
- Carried-over model fact: `Critique/derivations/C4--no-inversion.md` §7
  (anti-cue $\alpha^\star$ at $V<1/N$) and the run-006 replication
  `Critique/replications/C4--no-inversion/run.py` Step C(iii).
- Citations by full bibliographic reference (read this run, not stubbed;
  queued CR-035): Wang, Samara & Theeuwes (2019) Atten Percept Psychophys
  81(6):1813–1821, DOI 10.3758/s13414-019-01708-5; Kong, Li, Wang &
  Theeuwes (2020) PLoS ONE 15(6):e0233544, DOI 10.1371/journal.pone.0233544.
  (According to PubMed.)

### Wiki cross-references

Mission §11 keyword sweep performed across the full §11.1 anchor list,
with this run's focus on the suppression / selection-history / capture
sub-cluster (the broader anatomical anchors — LIP, FEF, V4, dopamine,
RPE, basal ganglia, normalization, surround suppression — were swept at
full depth in Version 0.1 and are not re-litigated here). Tools:
`Glob papers/*`, `Grep` on {distractor suppression, statistical learning,
value-driven, anti-cue, suppression history, down-weight,
counter-predictive} across `research_db/`. Hits and disposition:

- [[wang_theeuwes2018_statistical_learning_distractor_suppression]] —
  abstract (added this run). **Cited** as primary evidence for
  sub-question (ii); the anti-cued mapping is the crux of the verdict.
- [[failing_theeuwes2018_selection_history]] — full. **Cited**; review
  separating facilitatory capture (supports C4 at $V\geq 1/N$) from
  inhibitory suppression (anti-cued, $V<1/N$). Its §8 already lists the
  Wang & Theeuwes id as a citation-to-follow — now realised.
- [[hickey2010_reward_salience_acc]] — full. **Cited**; value pulls
  toward, not away (supports).
- [[posner1980_orienting]] — full. **Cited**; $V=1/N$ chance-validity
  boundary — no reallocation (supports the degeneracy point).
- [[gupta_sridharan2024_presaccadic_change]] — full. **Cited**; resolves
  sub-question (i) candidate counterexample in the negative.
- [[bisley_mirpour2019_priority_map]] — full. **Cited**; priority-map
  substrate has no native attend-away channel, only competitive
  reallocation; also surfaces the homogeneous-uncued limitation.
- [[desimone_duncan1995_biased_competition]] — full. **Cited**;
  biased-competition is the substrate of the Kong et al. 2020 reallocation
  and of the §5.1 zero-sum framing (supports).
- [[carlisle_kristjansson2018_wm_priming]] — full (surfaced by grep on
  "priming"/selection-history). **Unrelated-on-inspection / background**:
  intertrial WM priming is another selection-history facilitation toward
  recently-attended features; consistent with "history biases toward, not
  away", but not a direct C4 test. Noted, not cited in body.
- [[hikosaka2006_bg_reward_eyes]] — full (surfaced by grep on "reward").
  **Unrelated-on-inspection / background**: basal-ganglia reward biasing
  of saccades is reward-*toward*; consistent direction, not a direct test.
- [[spratling2008_pc_biased_competition]], [[itti_koch2001_saliency_review]],
  [[baluch_itti2011_topdown_mechanisms]] — full (grep hits). **Background**:
  competition/saliency substrates with non-negative weighting; consistent
  with no-inversion spirit, not direct tests.
- Concept [[priority-map]] (TAXONOMY) — **Cited** at concept level; the
  suppression literature's mechanism (priority-map plasticity) is the
  shared substrate.

Taxonomy gap surfaced (per mission §4.2 / §8.1; not acted on — owner's
prerogative): `research_db/TAXONOMY.md` has no `selection-history` or
`statistical-learning-of-priority` concept. The Wang & Theeuwes stub was
filed under closest-fit `priority-map`. The owner may wish to add a
`selection-history` concept that would aggregate
failing_theeuwes2018_selection_history, hickey2010_reward_salience_acc,
carlisle_kristjansson2018_wm_priming, and the new Wang & Theeuwes stub.

### Loose ends

- **Homogeneous-uncued allocation is an unnamed load-bearing assumption.**
  The scope note's mapping (b) shows the model *cannot represent*
  heterogeneous down-weighting of a single uncued location — yet that is
  exactly what statistical-learning distractor suppression does. The model
  assumes every uncued location receives $(1-\alpha)/(N-1)$ uniformly
  (paper §2.3 / mission §2.3). This is not in the mission's A1–A7 list. It
  is a genuine candidate **A8**. Spawned **CR-036** and flagged
  `proposed_mission_change: true` in the backlog for owner ratification.
- **Anderson-Laurent-Yantis 2011 and Geng 2014 still unstubbed.** Cited
  here only via the Failing & Theeuwes 2018 review's synthesis. Direct
  stubs would let a future run quote the value-driven-capture effect sizes
  and the suppression-as-distinct-system argument firsthand. Spawned
  **CR-037** (folds in the leftover CR-032 scope).
- **CONFIRMED-UNDER-ATTACK is reachable but not warranted yet.** If a third
  vector (e.g. a replication that explicitly adds a heterogeneous-uncued /
  anti-cued single location and confirms the model reproduces the Wang &
  Theeuwes suppression gradient) succeeded, the *conditional* claim could
  arguably elevate. But the categorical claim cannot, given the known
  out-of-scope failure. The conditional is the right object to keep
  testing.

### Next-attack recommendation

Two reasonable next picks, in priority order:

1. **CR-036 (replication, the homogeneous-uncued / proposed-A8
   assumption).** Extend the model to allow one uncued location to carry a
   distinct (lower) "validity" and re-derive/replicate whether the optimal
   policy reproduces the Wang & Theeuwes spatial suppression gradient. This
   is the highest-leverage follow-up: it directly tests whether the
   paper's homogeneity simplification changes any headline claim, and it
   connects the critique to a concrete empirical effect. It also feeds A2.
2. **CR-005 (C5 replication).** C5 remains the only *untouched* headline
   claim; a confirming replication of the $r=1$ symmetric recovery builds
   the substrate for the A3/A5/A6 assumption sweeps. Lower information per
   run, but it completes the "one verdict file per headline claim" goal.

Recommendation: **CR-036 first** (it is the substantive descendant of this
run's central finding), then **CR-005** to close out the headline-claim
coverage.

### Implications for PRISM v1/v2

This run sharpens the C4 PRISM prediction in a directly testable way:

1. **Distractor-statistics training should induce below-uniform allocation
   at the high-distractor location, and the model says this is correct.**
   If PRISM (`Prism/env.py`) is trained with a spatial distractor
   regularity (one location disproportionately carrying salient
   non-targets), the normative prediction — now triangulated by both the
   model's anti-cue derivation and the Wang & Theeuwes / Kong behavioural
   results — is that the trained agent's allocation $\alpha(\text{that
   location})$ should fall *below* uniform, while target-location
   allocation rises (zero-sum reallocation). The user's
   `Prism/analysis/avg_alpha_*.py` trajectories are the natural place to
   look for this signature, and `Prism/figures/avg_alpha_*.pdf` the place
   to report it.

2. **Homogeneous-uncued is a PRISM-relevant modelling choice, not just an
   abstraction.** PRISM's attention head *can* express heterogeneous
   spatial allocation (it is a full spatial map), so PRISM is strictly
   more expressive than the paper's model on exactly the axis (mapping b)
   that the suppression literature exercises. A PRISM agent could
   therefore exhibit learned single-location suppression that the paper's
   normative model cannot represent at all — meaning PRISM is a candidate
   testbed for the proposed-A8 extension before any analytic model is
   written. This is a place where the user's architecture is ahead of the
   normative model, not behind it.

3. **Value-driven capture as a training-stability caveat.** The capture
   literature (resisting suppression of once-rewarded features even when
   maladaptive) predicts that a PRISM agent over-trained on a high-value
   location may be *slow to re-allocate* when value structure changes — a
   plasticity/forgetting consideration for curriculum design, and a
   behavioural analogue the user could deliberately elicit.

---
