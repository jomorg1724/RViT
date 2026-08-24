# Neuroscience motivation for the split μ/q cross-talk architecture

Literature dive 2026-06-21 (PubMed + Consensus, 6 parallel agents). Goal: can we motivate
the v11_part2-style architecture — two recurrent attention pathways, **μ** (→ actor/policy,
image-grounded, writes the shared memory) and **q** (→ critic/value, reads the shared
memory) — the way Morgan/Albanna/Herman motivated its attention design? Two empirical
results to motivate: **(R1)** learning requires the coupling (private memories → always-wait
collapse); **(R2)** the image-grounded μ pathway must drive the policy (swap → collapse).

Terminology: **μ** = policy/actor pathway, **q** = value/critic pathway. (Not
"salience/top-down".)

## Verdict
Motivatable — but **not** as "μ and q are two attention nodes." The honest framing is:
the **μ pathway = the image-grounded priority + commitment-to-orient integrator** (FEF
visual-cell control + SC commitment), and the **q pathway = the value/critic system**
(cortico-striatal / dopaminergic), with the **obligatory coupling = the actor-critic
credit-assignment principle**. The SC angle is the strongest and most on-brand (the paper
already uses SC perturbation parallels). Two framing risks must be managed (below).

## Pillar 1 — actor/critic is a real brain organization (motivates the split)
Dorsal striatum ≈ actor (policy), ventral striatum + dopamine ≈ critic (state value / TD
error). Anatomically distinct, functionally interdependent.
- O'Doherty, Dayan, Schultz, Deichmann, Friston, Dolan **2004 Science** (PMID 15087550) — keystone fMRI double dissociation (ventral = critic in Pavlovian+instrumental; dorsal = actor only when action required). ✓verified
- Colas, Pauli, Larsen, Tyszka, O'Doherty **2017 PLoS Comp Biol** (PMID 29049406) — supports actor/critic but finds action-value PEs throughout striatum too (clean split contested). ✓
- Rothenhoefer et al. **2017 J Neurosci** — primate VS lesions impair learning *stimulus* value, spare *action* value. ⚠Consensus-sourced, verify author/page.
- Maia **2009 CABN** (PMID 19897789); Joel, Niv, Ruppin **2002 Neural Networks** (PMID 12371510, *cautions* a literal critic-in-BG-anatomy is implausible). ✓
- Original adaptive-critic-BG model: Houk, Adams & Barto 1995 (book chapter — cite primary, not in PubMed).

**Strength: moderate-strong as organizing principle.** Caveat: it's *striatal*, not an
attention-node split; the clean dorsal/ventral split is itself contested.

## Pillar 2 — coupling is required (motivates R1)
Mechanism: the actor learns only via the **three-factor corticostriatal plasticity rule**
(pre × post × dopamine), and dopamine *is* the critic's prediction error. Sever it → the
actor has no teaching signal → cannot learn. This is the credit-assignment / "decoupling
breaks learning" argument, and it's a clean conceptual precedent for R1.
- Schultz, Dayan, Montague **1997 Science** (PMID 9054347) — dopamine ≈ TD prediction error. ✓
- Hollerman & Schultz **1998 Nat Neurosci** (PMID 10195164). ✓
- Kuśmierz, Isomura, Toyoizumi 2017 Curr Opin Neurobiol; Wärnberg & Kumar 2023 PNAS; Morita & Kato **2014 Front Neural Circuits** (PMID 24782717) — three-factor rule; value & policy bound in one closed loop. (first two ⚠Consensus; Morita&Kato ✓)

**Strength: strong as analogy.** ⚠ **FRAMING RISK A:** in the brain the coupling is a
*broadcast dopamine scalar* flowing **critic→actor**, NOT a shared recurrent working memory
that the *actor writes and both read*. Direction and substrate differ. Present as conceptual
motivation, not isomorphism.

## Pillar 3 — the grounded pathway must drive the decision (motivates R2)
The decision integrates **sensory evidence to a bound**; reward/prior act as a baseline/gain
offset, not a substitute for evidence; and the *sensory* stage is the causally necessary one.
- Roitman & Shadlen 2002 J Neurosci; Huk & Shadlen 2005; Gold & Shadlen 2007 Annu Rev; Ding & Gold 2011 — evidence accumulation to bound in LIP/FEF. ✓
- **Katz, Yates, Pillow & Huk 2016 Nature** (DOI 10.1038/nature18617) — inactivating sensory MT impairs discrimination; inactivating the *accumulating* LIP does not. The grounded representation is the necessary input. ✓ (the single best cite for R2)
- Rorie et al. 2010 PLoS ONE; Hanks et al. 2011 J Neurosci; Platt & Glimcher 1999 Nature — reward/prior enter as additive offset / baseline gain. ✓
- ⚠ **Contested:** Kloosterman 2019 eLife; Diaz 2024; Walsh 2024 — reward/prior can also shift drift rate / sensory gain (expectation can enter the evidence pathway).

**Strength: moderate, contested.** ⚠ Note: Pillar-1 (BG actor/critic) does **not** support
R2 — motivate R2 from this evidence-accumulation literature, not from striatal anatomy.

## The LIP / FEF / SC mapping (the crux) — honest verdict
**The two integrators do NOT map onto two distinct attention nodes.** LIP, FEF, and SC are
each a *single* priority map, not an actor/critic pair. So "μ = node X, q = node Y" within
the attention nodes is not supported. Instead, **all three sit on the μ side**, and q (value)
belongs downstream (striatum/dopamine/OFC).

- **SC → μ (strongest, most on-brand).** Image-grounded, causally necessary for *covert*
  attention, dissociable from cortical gain, and the *commitment/threshold* stage that turns
  accumulation into a committed response:
  - Lovejoy & Krauzlis 2010 Nat Neurosci (DOI 10.1038/nn.2470) — covert-attention "dual effect" of unilateral inactivation. ✓
  - Zénon & Krauzlis 2012 Nature (10.1038/nature11497) — SC inactivation → big attention deficit, cortical gain *unchanged*. ✓
  - Stine, Trautmann, Jeurissen, Shadlen 2023 Neuron (10.1016/j.neuron.2023.05.028) — SC = threshold that converts LIP accumulation into commitment. ✓
  - Bollimunta, Bogadhi & Krauzlis 2018 Nat Commun (10.1038/s41467-018-06042-2) — SC inactivation more devastating than FEF. ✓
  - Müller, Philiastides, Newsome 2005 PNAS — subthreshold SC microstim *enhances* covert attention. ✓
  - Herman, Arcizet & Krauzlis 2020 eLife (10.7554/eLife.53998) — caudate attention modulation *depends on* SC (SC↔caudate↔cortex loop = loose analog of "μ writes shared state"). ✓
- **FEF → μ.** A *controller* (not read-out) of attention; the attention signal is carried by
  **visual (image-grounded) cells**, while pure **movement cells are suppressed** during
  covert attention — the cleanest analog of R2 (the image-grounded signal does the work).
  Poor match for q (no value coding).
  - Moore & Fallah 2001 PNAS / 2003 J Neurophysiol — subthreshold FEF microstim enhances sensitivity. ✓
  - Armstrong & Moore 2007 PNAS; Wardak et al. 2006 J Neurosci (FEF needed for covert search); Gregoriou et al. 2009 Science / 2014 Nat Neurosci. ✓
  - Thompson, Biscoe, Sato 2005 J Neurosci — attention = enhanced *visual* cells, *movement* cells inhibited. ✓
- **LIP → straddles μ and q (the useful caution).** LIP carries BOTH accumulation/decision
  signals AND value/reward-probability signals on a **shared substrate** (Platt & Glimcher
  1999; Sugrue, Corrado, Newsome 2004; choice+confidence co-accumulation, Vivar-Lazo & Fetsch
  2025 Nat Neurosci ⚠preprint-grade). This *supports the shared-memory premise* (value &
  decision intertwined on one substrate) — but argues *against* μ and q being separate
  integrators. And Katz 2016 + Jeurissen 2022 Neuron show LIP accumulation is
  correlated-but-not-indispensable (distributed, redundant) → don't equate one model module
  with one area.

**Net:** μ ≈ the FEF-visual-cell + SC commitment integrator (image-grounded, drives & commits
the response); q ≈ the value/critic system (BG/dopamine — *not* an attention node); the
"shared recurrent memory, μ writes / both read" ≈ a *loop* (FEF↔V4, SC↔caudate↔cortex), not a
register in one area.

## Novelty
No prior model (found) splits a *recurrent vision encoder* into μ/q on a shared memory,
requires coupling for learning, or requires the *grounded* pathway to be the actor. Attention-
as-RL-policy work (Mnih 2014; Minut & Mahadevan 2001) treats attention as the action, no
policy/value split. The one ML result on actor/critic representation sharing (Garcin 2025
arXiv ⚠unverified) found the *opposite* for *feedforward* reps (separation helps) — a clean
contrast: our claim is that for a *recurrent, image-grounded* agent, coupling is required.
⚠ Not yet searched: active-inference attention, transformer-RL shared vs split policy/value
heads — do before claiming novelty in print.

## The falsifiable prediction that makes it paper-worthy
A **double dissociation** under perturbation: lesion/clamp **q** → value/context modulation
degrades, change *detection* spared; lesion **μ** → detection collapses. This maps directly
onto SC-inactivation abolishing covert detection (Zénon & Krauzlis 2012; Katz 2025) vs
value-circuit manipulation — and bridges back to the paper's existing FEF/SC causal-
perturbation framing. *This* is the neuroscience claim, beyond "RL needs a value estimate."

## Hardening experiments — a THREE-PART dissociation
Refinement: a *behavioural* "clamp q → detection spared" test is **trivial at inference**
(the critic doesn't drive the action), so it proves nothing on its own. The rigorous claim is
a dissociation across three complementary levels:

1. **Behavioural dissociation — at TRAINING time** (this is where it's non-trivial): the
   coupling-required + μ-must-drive-policy result. Already shown on T=29
   (v11_part2 0.868 vs v11_part4 independent 0.0 vs v11_part3 swap 0.0). HARDEN: replicate on
   the 7-step task + the battery (`--encoder crosstalk`), and add the **directionality**
   control (μ-writes-H2 vs q-writes vs both) and a **graded/bottlenecked** coupling channel
   (dose-response, find the minimum), so it's not all-or-nothing.
2. **Representational dissociation — at INFERENCE** (the clean, decodable test): decode
   change-EVIDENCE (change-present, change-location) vs VALUE/context (cue value, reliability,
   cued location) from Z_μ vs Z_q. Predict the cross-over: evidence ≫ from Z_μ, value/context
   ≫ from Z_q. → `analysis/e7_pathway_dissociation.py` (built; run on a trained crosstalk
   checkpoint, ideally `vda4`). This is the neuroscience-facing prediction: it says what should
   be decodable from a policy/commitment node (SC/FEF-visual) vs a value circuit.
3. **Causal-perturbation dissociation — at INFERENCE** (bridges to the paper's existing
   FEF/SC clamps): perturb the μ-stream attention → behaviour (hit rate / threshold) changes
   (the FEF-microstim / SC-inactivation analog); perturb the q-stream attention → value
   estimate (critic V) changes but behaviour is spared. The `attn_clamp` hook is wired for
   this; a perturbation runner is the next script.

## Framing for the neuroscience audience
Lead with the SC-grounded μ story (SC is the on-brand node — the paper already uses SC
perturbation parallels) and the representational + causal dissociations as PREDICTIONS for
the brain (what a value-circuit lesion vs an SC inactivation should do to decodability and
behaviour). Keep the actor-critic / credit-assignment machinery in the background (it's the
mechanism, not the pitch). The implicit thesis — never stated outright — is that a trained
network can generate specific, falsifiable neurophysiology predictions and thereby help steer
experiments and theory; let the dissociation predictions carry that, don't editorialize it.

## Verification status
PubMed-confirmed citations carry PMID/DOI above (✓). Consensus-sourced or preprint items
are flagged (⚠) and must be re-verified (author lists, pages, published DOIs) before going
into the manuscript. Houk/Adams/Barto 1995 is a book chapter (cite primary).
