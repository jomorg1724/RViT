# Act II — Paradigm battery: the mechanisms transfer to established primate tasks

**Role.** Act I establishes, on the VDA environments, that one RL-trained recurrent vision-transformer realizes
and *dissociates* the attentional mechanisms. Act II shows those same mechanisms — and the same attention-clamp
machinery — reproduce results from the tasks the primate literature actually used. Same models (d128, conv
front-end, both routings), same clamp harness (`vda_core`). Two positive reproductions and one principled null.

---

## II.1 Luo–Maunsell sensitivity/criterion double dissociation *(positive)*
*Harness: `luo_core.py`/`luo_repro.py`/`luo_mechanism.py`.*

The Luo–Maunsell paradigm separates two reward regimes on the *same* stimuli: a **sensitivity** session (value
concentrated at one location) and a **criterion** session (global hit/CR reward). Reproduced as a clean double
dissociation. At Δ=18: the **sensitivity** manipulation moves **d′** (Δd′ = 1.46 crossattn1 / 1.09 affine_ew)
with low false alarms (0.04/0.02); the **criterion** manipulation moves **bias** (FA 0.17/0.18, Δd′ only
0.32/0.59). Sensitivity→d′, criterion→c — the signature dissociation.

**Mechanism** (the follow-up localizes each effect): the **criterion** effect is **decision-stage** — a shift in
the actor's declare-bias, present in *both* routings (+0.013 attention change, i.e. essentially none). The
**sensitivity** effect is **attentional gain** — an increase in attention to the rewarded location, **clean for
crossattn1** (+0.070 attention in the sensitivity session vs +0.013 in the criterion session) but **cue-locked in
affine_ew** (it attends the cued location in both sessions — the reflexive reader can't confine gain to the
reward-relevant location). So the model reproduces the behavioral dissociation *and* exposes that criterion is a
readout-stage effect while sensitivity is an attention-gain effect — with the controlled reader (crossattn1)
giving the cleanest V4-like gain signature. **[E1: gain vs criterion, dissociated; ties to Act I §3 SDT.]**

## II.2 Validity4 — the model USES spatial validity *(positive; the key contrast with the value-VDA)*
*Harness: `validity4_repro.py`.*

Validity4 is pure spatial validity — a cue ring whose *completeness* signals validity (P[change at cued]), with
**no value colour**. It is the clean complement to Act I's value-VDA, which perceived validity at the cue and then
**discarded** it (validity-flat psychometrics; validity decoded at t1 then gone by t2). Here, with no competing
value cue, **the model uses validity**, gradedly:
- **Cueing benefit grows monotonically with validity** (cued − uncued detection at Δ=26): crossattn1 −0.05 → 0.07
  → 0.14 → **0.18**; affine_ew 0.00 → 0.07 → 0.08 → **0.12** (validity 25→100%).
- **Uncued detection falls** as validity rises (crossattn1 0.88→0.69; affine_ew 0.94→0.86) — the model **diverts**
  resources from the uncued location as the cue becomes more predictive (a resource trade-off, not just a cued gain).
- **Cued-patch attention α₁ rises with validity**: crossattn1 0.36→0.42; affine_ew **0.27→0.48** (uniform = 0.25) —
  the model literally looks at the cued patch more when the ring says it is more reliable.

This is a graded, Posner-like validity effect, and the **dissociation from the value-VDA is the point**: when a
value cue competes, the model prioritizes value and discards validity (Act I §5); when validity is the *only* cue,
it is used. That explains *why* the value-VDA was validity-flat — value crowds validity out — and shows the
capacity to use validity is present, gated by what else is on the cue. **[E2/E3: the model reads cue predictiveness
when it is task-relevant; complements Act I's validity-discard mechanism.]**

## II.3 Baruni relative-value — a principled null *(consistent, not a miss)*
*Harness: `baruni_core.py`/`baruni_repro.py`.*

The Baruni relative-value test asks whether the model's value sensitivity is *relative* (context-dependent) rather
than absolute. It is **not**: the response is a weak **absolute** value effect (crossattn1 high-vs-low ~7pt; affine_ew
flat) with **no value-directed attention**. This is a *principled* null, not a failure: it is exactly what the
high-sensitivity, null-VDA normative regime predicts — the model operating in an absolute-value regime is the
consistent cross-paper prediction, and the reproduction confirms it rather than contradicting it. **[Cross-paper
consistency with the normative account.]**

---

## Synthesis
Act II carries the Act I mechanisms into the primate paradigms: the attention-clamp that gave the Act I SDT
dissociation reproduces the **Luo–Maunsell** sensitivity/criterion double dissociation (and localizes each stage);
**validity4** shows the model uses spatial validity when it is the operative cue, dissociating cleanly from the
value-VDA's validity-discard; and **Baruni** confirms the absolute-value regime the normative account predicts.
Throughout, the **crossattn1 (controlled) vs affine_ew (reflexive)** split recurs — crossattn1 gives the cleanest
reward-confined gain (Luo) and the memory-based validity use; affine_ew is more cue/ring-driven.

*Pending (always-wait collapse; env is sound):* the **Krauzlis** attend-here/ignore-here models did not train (θ
stuck at 65). The environment is **correctly designed** — a 2-stimulus filtering task (cued patch + one diagonal
foil) whose reward already pays a correct-withhold on a foil change (oracle-achievable correct-rate = **1.000**).
Both trained models nonetheless collapsed to **pure always-wait** (declare 0.00 on cued *and* foil changes, CR 1.00).
The always-wait basin is unusually sticky here because rewarding foil-withhold lifts the no-effort baseline to
~0.69–0.80 (vs 0.5 for validity4, which is why validity4 escaped and learned), so the risky "declare" action is
under-explored. Recovery is a **retrain with an anti-always-wait lever** — a proportion-warmup curriculum (start
all-cued so declaring bootstraps like validity4, then anneal foils in), a miss penalty, an exploration bonus, or the
ConvMGU perceptual recurrence — after which the SC spatial-selection result (Zénon & Krauzlis 2012 — SC inactivation
impairs selection, not sensitivity, testable via the cued-attention clamp) should be recoverable.

*Figures:* `luo_*`, `validity4_curves.png`, `baruni_*` in the respective analysis dirs / `vda_sweep/figs/`.
