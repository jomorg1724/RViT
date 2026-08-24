# Act I — Visual-attention detection (VDA) environments: draft Results integration

**Role in the manuscript.** Act I is the lead empirical result. A single recurrent vision-transformer with
spatial working memory, trained only by reinforcement to detect a change among cued Gabor stimuli, is
subjected to an exhaustive eight-analysis battery on two set sizes (vda1, one monitored stimulus; vda4,
four). The same battery is applied to both feedback routings — the multiplicative PRIORITY reader
(`affine_ew`) and the memory-token VALUE reader (`crossattn1`) — so every phenomenon is reported as a
mechanism, and several are causally dissociated by routing. Each subsection below states the finding, the
supporting number/figure, and the human/primate result it reproduces (ledger entry in brackets).

Figures live in `RViT_plus_paper_jepa_grid9/vda_sweep/figs/`.

---

## 1. Psychometrics and reaction time — the cueing benefit is a set-size effect, and validity is inert
*Figures: psychometric curves + RT-vs-Δ per cue condition (vda_fig_psych).*

Detection is a monotone psychometric function of change magnitude Δ in every condition, and the model is
faster for larger Δ (RT falls with Δ) — the basic behavioral signature of a graded detector. The
spatial-cueing benefit (cued threshold below uncued) **emerges with set size**: negligible at vda1, it
opens to a **+4.1° threshold gap for crossattn1 and +2.2° for affine_ew at vda4**. Critically, the benefit
is **flat across cue validity** (proportion 25→100%): the model gains from *where* it is told to look but
not from *how predictive* the cue is. This is the parametric noise-limited signature — the cueing benefit
grows as competing stimuli are added — and it sets up the validity-blindness whose mechanism §5 exposes.
**[E2: noise-limited set-size account; E1 mechanism 2, efficient selection.]**

## 2. Attention maps and the α₁ time-course — orient, then sustain or release
*Figures: per-colour super-figures (4 validity × 7 frames) + α₁ line plots (alpha1_lines, super_vda4_crossattn1_*).*

The attention map is a priority map over patches. Both readers **orient to the cued location at cue onset**
(crossattn1 α₁ ≈ 0.72–0.76 at t1, well above the 0.25 uniform baseline). Two dissociations follow. (i)
**Maintenance:** crossattn1 *sustains* attention on the cued patch through to the change (α₁ ≈ 0.37–0.54 >
uniform), whereas affine_ew *releases* it back toward uniform (~0.25) once the stimulus is on — the
controlled-vs-reflexive split. (ii) **Set-size dilution:** sustained attention weakens as monitored load
rises (α₁ ≈ 0.54 at vda1 → 0.37 at vda4). The map is **validity-blind** (indistinguishable across
proportion) and **value is not written into it** (attention maps are identical across cue colour) — the cue's
predictiveness and worth do not shape *where* attention goes. The sustained-through-blank component is the
observable substrate of attention-based rehearsal. **[E4: attention-based rehearsal; E5: priority map.]**

## 3. Signal-detection read-out — attention moves the criterion in all readers; sensitivity only in the priority reader
*Figure: c(α₁) and d′(α₁) curves under the graded attention clamp (sdt_curves).*

Sweeping the attention bias on the cued patch from suppress (α₁=0) to enhance (α₁=1) and reading out
signal-detection quantities gives the paper's central dissociation. **Criterion c falls monotonically with
attention in every model** (vda4: crossattn1 0.79→−0.27; affine_ew 1.42→−0.60) — enhancing attention makes
the detector **more liberal**, the textbook attentional criterion shift. **Sensitivity d′ splits by routing:**
for crossattn1 it is **flat** across the clamp (2.4–2.7) — the decision runs from memory, so frame-attention
moves the *criterion* but not the *sensitivity*; for affine_ew d′ is **attention-load-bearing** — suppressing
attention collapses it (0.63/1.45) and natural/enhanced restores it (~2.0–2.7). This is the direct
realization of Carrasco's still-open trichotomy in one system: gain (§2/§6), efficient selection (§1), and a
**decision-criterion effect that is dissociable from sensitivity by routing.** **[E1: all three accounts,
and their dissociation.]**

## 4. Distributional-critic uncertainty — misdirected attention manufactures false certainty
*Figure/data: policy entropy, critic quantile spread, declare rate under attention manipulation (vda_fig_entropy → entropy.npz).*

On a real change at the *uncued* patch, three attention conditions are compared. Attending the change
raises detection; **misdirecting attention onto the empty cued patch produces the diagnostic failure — but
only in the priority reader.** affine_ew, misdirected, **misses the change (declare 0.68→0.24) while becoming
more confident** (policy entropy 0.053→0.035): it reports "no change" precisely because it was aimed wrong.
crossattn1, misdirected, misses somewhat but its entropy *rises* (0.104→0.118) — the memory-based reader
stays appropriately uncertain. The split follows §3 exactly: affine_ew's sensitivity is attention-mediated,
so blinding it yields confident errors; crossattn1 is memory-buffered, so it "knows" it is unsure. (A
sub-finding: even in affine_ew the *critic's* quantile spread widens under misdirection — the value system
registers the problem while the policy commits.) This is a model-level account of how attentional
misallocation produces confident perceptual errors. **[E1 mechanism 1/3; novel uncertainty read-out.]**

## 5. Temporal decoding from memory — value is maintained, validity is perceived then discarded, change is built online
*Figure: decode balanced-accuracy vs timestep, four variables × two readers (decode_curves).*

Decoding task variables from the working-memory state at each frame gives the mechanistic capstone and the
model's LIP-like position code. **(i) Value (cue colour) is latched at cue onset and held perfectly** —
balanced accuracy 1.00 from t1 through t6 in both readers. **(ii) Validity (proportion) is perceived at the
cue and discarded within one step** — a transient spike at t1 (0.44 crossattn1; **0.75 affine_ew — it reads
validity strongly**) that falls to chance by t2. This *is* the mechanism of the §1 validity-blindness: the
predictiveness is available but never enters maintained memory; both readers are validity-blind by
**discarding**, not by failing to perceive. **(iii) Change presence and location are constructed online** —
flat at chance through t4, jumping only at the change frame (presence 0.75/0.81; location 0.50/0.54 at t5,
rising at t6). The decodable, position-specific memory of the change is the model's parietal position code;
that this code appears exactly when the change occurs, and the value code from cue onset, shows the memory
holds *what matters, when it matters.* **[E5: LIP position-specific memory; mechanism of E2 validity-blindness.]**

## 6. Attentional microstimulation — injecting priority evokes a false detection, gated to the monitored location
*Figure: false-detection rate vs injected α at cued vs uncued sites (microstim_curves).*

Injecting attention onto a patch on *no-change* trials tests the causal converse of §3: does surplus
priority conjure a percept? **Injecting at the cued (monitored) patch evokes false detections** — the
false-alarm rate rises monotonically with injection strength (~0.03→0.12, ×4, both readers) — whereas
**injecting at an uncued patch does nothing** (flat, ~0.05–0.10). The evoked false percept is **spatially
gated to where the model is already monitoring**, the causal mirror of the criterion shift in §3 and the
model analogue of evoking detections by stimulating a parietal/collicular priority map. This is also the
within-task bridge to Act II's Luo–Maunsell result, where the same clamp machinery reproduces the
sensitivity/criterion double dissociation. **[E5: attentional modulation of detection thresholds, causal;
bridges to Luo (Act II).]**

---

## Synthesis — one system, dissociated mechanisms, two routings
Across the battery the two feedback routings occupy different points of the attention literature. The
**VALUE reader (`crossattn1`)** is the *controlled* system: it sustains attention to the change (§2),
decides from memory so its sensitivity is clamp-robust (§3), stays appropriately uncertain under
misdirection (§4), and reads validity most strongly at the cue before discarding it (§5). The **PRIORITY
reader (`affine_ew`)** is the *reflexive* system: it releases attention after orienting (§2), its
sensitivity is attention-mediated (§3), and misdirection makes it confidently wrong (§4). Both share the
criterion effect (§3), the online change code (§5), and the location-gated microstimulation effect (§6).
The headline is Carrasco's: three accounts of how attention helps — gain, efficient selection, criterion —
are not competing but co-present in one mechanism, and the model **dissociates** what behavior alone could
only hedge as "all three likely contribute."

## Act II hand-off (second task result)
The same model and the same attention-clamp machinery are then taken to established primate paradigms:
the **Luo–Maunsell sensitivity/criterion double dissociation** (reproduced: at Δ=18 the sensitivity task
moves d′, Δd′≈1.1–1.5 with low FA; the criterion task moves bias, FA 0.17–0.18 — with the mechanistic
follow-up localizing the criterion effect to the decision stage and the sensitivity effect to attentional
gain, cleanly for crossattn1), and the **Baruni relative-value** test (a principled null: the high-sensitivity
regime is absolute-value, not relative — cross-paper consistency rather than a miss). Act II shows the Act I
mechanisms transfer to the tasks the primate literature actually used.

---
*Figure inventory:* alpha1_lines · super_vda4_crossattn1_{red,green,blue} · sdt_curves · decode_curves ·
microstim_curves · (psychometrics + entropy panels to render from their npz). All computed on the trained
vda1/vda4 d128 models, both routings.
