---
type: conversation
agent: skeptical-reviewer
prompt_version: 0.1
run_id: run-006
started: 2026-05-18T12:00:00Z
ended:   2026-05-18T13:30:00Z
worked_on: C4 (with CR-019 piggyback)
attack_vector: re-derivation
verdict_touched: C4--no-inversion
verdict_after: WEAKLY-SUPPORTED
papers_read:
  - posner1980_orienting
  - failing_theeuwes2018_selection_history
  - hickey2010_reward_salience_acc
  - thomsen2005_conflicting_cues_fmri
  - luo_maunsell2018_criterion_sensitivity
  - sridharan2017_sc_sensitivity_bias
  - ghose_maunsell2002_task_timing
  - reynolds_heeger2009_normalization
  - bisley_mirpour2019_priority_map
  - bisley_goldberg2010_parietal_priority
  - desimone_duncan1995_biased_competition
  - koch_ullman1984_winner_takes_all
  - itti_koch2001_saliency_review
  - wolfe2021_guided_search_6
  - mirpour2010_ppc_microstim
  - hawkins1990_attention_detectability
  - gupta_sridharan2024_presaccadic_change
  - herman_krauzlis2017_sc_change_detection
papers_added: []
spawned_tasks:
  - CR-031   # literature attack on C4 conditional via distractor-suppression learning
  - CR-032   # add stubs for Wang & Theeuwes 2018, Geng 2014, Anderson Laurent Yantis 2011
  - CR-033   # sensitivity of joint optimiser to the β/γ kink at α=1/N
  - CR-034   # anti-cue regime (V<1/N) at N=4 — derivation extension
---

# C4 re-derivation: the boundary inversion threshold

## What I attacked

The C4 categorical claim from paper §4.5: "the optimal $\alpha^\star$ is always $\geq 1/N$" across the 4,410-row primary sweep. The paper's stated justification: the cued-side weighted reward loss "always exceeds the gain at low-value uncued locations, regardless of $r$".

I also picked up the piggyback task **CR-019** (spawned by CR-014 in run-002), which asked whether C4's $V \geq 1/N$ qualifier should be tightened to $V > 1/N$ in light of the optimiser finding $\alpha^\star = 0.02$ for the value-blind policy $P_2$ at $V = 1/N$ in the secondary sweep. CR-019 was explicitly prereqed on CR-004 and designed to be addressed in the same run.

## How I attacked it

**One attack vector: re-derivation** (with numerical corroboration). The decision to make this a re-derivation rather than a replication: C4 has both an empirical part (a categorical statement about a numerical sweep) and a theoretical part ("regardless of $r$"). A replication would reproduce the empirical part but leave the theoretical part unexamined; a re-derivation can adjudicate both.

I derived the one-sided derivative $\partial \mathbb{E}[R]/\partial \alpha$ at $\alpha = 1/N$ from the model's defining equations and turned it into a closed-form inversion threshold $r^\star_{\mathrm{inv}}(V, v, N, \mathrm{CR}) = (N-1) A_0/B_0$, where $A_0, B_0$ are r-independent boundary partials. Then numerical corroboration: (Step A) evaluate $r^\star_{\mathrm{inv}}$ across the paper's primary $(V, v, \text{variant})$ grid at $N = 4$ to count how often the local-inversion threshold falls inside the swept $r$ range; (Step B) at the cells flagged as most adversarial by Step A, compute the full $\mathbb{E}[R](\alpha)$ curve at $\Delta\alpha = 0.005$ to determine the *global* argmax; (Step C) test the anti-cue regime ($V < 1/N$) that the paper does not sweep, to characterise where C4 actually fails.

Full derivation in `Critique/derivations/C4--no-inversion.md` (10 sections; LaTeX-rendered math). Numerical companion in `Critique/replications/C4--no-inversion/run.py` with output in `output/results.json` and `output/run.log`.

## What I found

**1. Empirical C4 holds across the entire 4,410-row primary sweep, independently corroborated.** Zero inversions of $\alpha^\star_{P_1}$ or $\alpha^\star_{P_2}$ in the existing CR-002 phase-A sweep (queried directly from `output/results.json`). Step B of CR-004 reproduces this at fine grid resolution at the analytically most-adversarial cells — global argmax is always in the right branch ($\alpha^\star \in [0.95, 1.00]$ at $r=10$).

**2. The paper's theoretical justification ("regardless of $r$") is incomplete.** The left one-sided derivative at $\alpha = 1/N$ is

$$\left.\frac{\partial \mathbb{E}[R]}{\partial \alpha}\right|_{1/N^-} = \frac{2 d'_{\max} f'(1/N)}{r+1}\bigl[A_0 - \frac{r}{N-1} B_0\bigr],$$

linear in $r$ once the r-independent boundary partials are pulled out. The sign flips at $r^\star_{\mathrm{inv}} = (N-1) A_0/B_0$. **At 103 of 210 swept $(V, v, \text{variant})$ cells (49.0%), $r^\star_{\mathrm{inv}}$ falls inside the paper's swept $r \in [0.1, 10]$ range** — meaning the local cost-vs-benefit balance argument the paper makes *fails* in roughly half of the cells. At the symmetric corner $(V = 1/N, v = 1)$, $r^\star_{\mathrm{inv}} = 1$ exactly (derivation §5), and for $r > 1$ the point $\alpha = 1/N$ is a local *minimum* — both branches escape uniform attention.

**3. Correct mechanism named: location-count asymmetry.** What guarantees global no-inversion across the primary sweep is *not* the local balance argument but a structural fact the paper does not name: at $\alpha \to 1$, the single cued location reaches $d'_{\max}$; at $\alpha \to 0$, the $N-1$ uncued locations each reach only $d'_{\text{base}} + \beta[d'_{\max} f(1/(N-1)) - d'_{\text{base}}]$, with $f(1/(N-1)) < 1$ for $N \geq 3$. Combined with the value-weight inequality $w_c \geq w_u$ (equivalent to $V \geq 1/[(N-1) v + 1]$, which for $v \geq 1$ simplifies to $V \geq 1/N$ — the paper's stated condition), this produces strict right-branch dominance globally.

**4. Anti-cue counterexample. C4 fails outside the conditional.** At $(V = 0.25, v = 1, N = 2)$ — anti-cue regime where $V < 1/N = 0.5$ and the cued location is *both* less probable and less valuable per channel — the global optimum is **inverted**: $\alpha^\star_{\mathrm{global}} = 0.180$ at $r = 1$, dropping to $\alpha^\star_{\mathrm{global}} = 0.020$ at $r = 10$. These cells are outside the paper's primary sweep ($N = 4$ only) but inside the V-range $[0.25, 1.0]$ the paper writes as if it were a general property. The model itself does not categorically rule out inversion — it produces it cleanly when the location-count argument flips.

**5. CR-019 resolved.** At $V = 1/N$, $v = 1$, $r > 1$, the model is bimodal in $\alpha$. The right-branch global optimum (at $\alpha \sim 0.96$) exceeds the left-branch local optimum (at $\alpha \sim 0.02$) by 0.005 to 0.014 reward units across $r \in (1, 10]$ at $N = 4$. C4's wording does **not** need to be tightened to $V > 1/N$; $V = 1/N$ is fine because the right branch still wins strictly (by location-count asymmetry) for $r > 1$ and ties for $r \leq 1$. The CR-014 observation of $\alpha = 0.02$ for $P_2$ at $N = 2, V = 0.5, v = 1$ was the left-branch local maximum, found by a value-blind optimiser that did not visit the right branch.

## Verdict movement

- **Before**: OPEN (bootstrap-seeded, no attack vector executed).
- **After**: WEAKLY-SUPPORTED (mission §3.1: one attack vector executed; elevation to CONFIRMED-UNDER-ATTACK requires a second vector).

The empirical headline survives one direct attack; the theoretical justification is substantively refined; the conditional $V \geq 1/N, v \geq 1$ is now mechanistically explained (location-count asymmetry, not local balance); and the boundary closed form $r^\star_{\mathrm{inv}}$ is a new derived quantity the paper missed — mirror-symmetric to the CR-001 closed form $r^\dagger(v)$ for the C2 non-monotonicity.

## Next-attack recommendation

**CR-031 — literature attack on C4 conditional via distractor-suppression learning.** Two sub-questions:

(i) Do behavioural cueing studies at $V \geq 1/N$ ever exhibit eye-tracking / microsaccade signatures of $\alpha < 1/N$? (Tangential candidate: Gupta & Sridharan 2024 on presaccadic-attention-not-helping-change-detection.)

(ii) Is the distractor-suppression literature (Wang & Theeuwes 2018 *Statistical learning of distractor locations*; Geng 2014 *Attentional mechanisms of distractor suppression*; Vatterott & Vecera 2012) interpretable as behavioural inversion at $V \geq 1/N$ in the model's terms?

A literature attack on either sub-question would constitute the second vector required for CONFIRMED-UNDER-ATTACK (mission §3.1), or surface a behavioural pattern that moves the verdict to CONTESTED. The wiki has none of Wang & Theeuwes 2018, Geng 2014, or Anderson, Laurent & Yantis 2011 as stubs yet — adding two of these (via one PubMed fetch, soft cap OK) would be the natural attack execution.

## Wiki cross-references

(See verdict body for the full §11 sweep table — repeated here in condensed form to satisfy the conversation-page protocol per mission §5.1.)

- [[posner1980_orienting]] — cited as the V=1/N=chance-validity empirical baseline (no behavioural effect at V=1/N).
- [[failing_theeuwes2018_selection_history]] — cited as both supporting C4 ("inversion away from value is hard") and caveating it (suppression-history literature suggests *behavioural* inversion can be learned).
- [[hickey2010_reward_salience_acc]] — cited as supporting the model's location-count argument (reward signal pulls toward, not away).
- [[thomsen2005_conflicting_cues_fmri]] — cited as behavioural analog of partial anti-cue inversion (PFC override of invalid peripheral cue, with RT cost).
- [[luo_maunsell2018_criterion_sensitivity]] — cited as indirect support: in cued macaque tasks, reward shifts criterion not allocation.
- [[sridharan2017_sc_sensitivity_bias]] — cited as same vein.
- [[ghose_maunsell2002_task_timing]] — cited as the normative-attention-allocation paradigm.
- [[reynolds_heeger2009_normalization]] — cited at concept level for the gain-asymmetry framing.
- [[bisley_mirpour2019_priority_map]] — cited as neural substrate consistent with no-inversion under $V \geq 1/N$.
- [[bisley_goldberg2010_parietal_priority]] — unrelated on inspection.
- [[desimone_duncan1995_biased_competition]] — cited at concept level (cued wins via inhibition of competitors).
- [[koch_ullman1984_winner_takes_all]] — unrelated on inspection.
- [[itti_koch2001_saliency_review]] — unrelated on inspection.
- [[wolfe2021_guided_search_6]] — unrelated on inspection.
- [[mirpour2010_ppc_microstim]] — unrelated on inspection (bias is toward, not away).
- [[hawkins1990_attention_detectability]] — cited as SDT-of-attention background.
- [[gupta_sridharan2024_presaccadic_change]] — spawned CR-031 candidate counterexample.
- [[herman_krauzlis2017_sc_change_detection]] — cited as same-task-class empirical substrate.
- concept page [[competition_emergent_predictive_coding]] — cited at concept level for priority/competition framing.
- thread page `threads/the_user_architectural_program.md` — cited for §3.5 PRISM implications.

Searched anchor terms per mission §11.1 + C4-specific keywords (inverted attention, anti-cue, counterpredictive cue, distractor suppression, normative observer, priority map, IOR). No web fetches consumed this run (0 of soft cap 2). No new stubs added.
