# The Unified Percept: attention as the binding of a decision-relevant percept

*A working theory across the VDA set-size battery and the convolutional
recurrent-transformer memory — 2026-08-22*

---

## 1. The claim

**Attention is best understood not as a mechanism for routing information, but as
the operation that *unifies* a percept — the single, decision-relevant summary of
the current sensory scene — out of which all downstream decisions are derived.**

Everything we have built and measured in this project is, in retrospect, a
sequence of tests of this one claim. This document weaves the two strands of work
— the VDA set-size battery and the new convolutional memory — into that story.

## 2. Where the claim comes from: the MAH design

The starting point of the project (the Morgan/Albanna/Herman paper we set out to
reproduce) already contained the claim in architectural form. Its network is a
recurrent vision transformer whose attention is *modulated by working memory*:
the memory state is injected into the attention computation, so what the model
"attends to" at every moment is a product of both the current stimulus and the
remembered context. The paper's interpretability protocol is built around this:
intrinsic attention maps first, causal perturbations second, decoding and
signal-detection theory to connect the maps to behavior. The implicit theory is
that behavior is the readout of a *unified* internal state — a percept — and that
attention is the observable trace of how that state is assembled.

That is the theory we have been testing, often without saying so explicitly.

## 3. The VDA set-size evidence

The set-size battery (VDA4/VDA9/VDA16) was the first systematic test. The core
findings fit the theory:

- **Attention effects existed and were measurable.** The spatial attention
  measures showed the model concentrating its attentional resources where the
  task demanded — the cued location, the changed item.
- **Set size mattered.** As the number of items grew, performance and the
  attention signatures changed in the way a *limited binding resource* would
  predict: more items compete for the same unified slot, and attention — the
  unification operation — shows the strain.

If attention merely routed information, adding items would be a capacity problem
in the network. But the signature we observed — attention concentrating,
competition scaling with set size — is the signature of a *binding* process.

## 4. The crack: noise in the memory broke it

Then we added noise to the memory embeddings, and the effects did not reproduce.

This was the most informative negative result of the project, because of what it
implies. If attention is a unification operation that assembles the percept *out
of* the memory contents, then corrupting the memory should not merely degrade
performance — it should produce *dramatic, measurable changes in attention
itself*, as the system works harder to hold the percept together. The fact that
the effect instead *disappeared* — that the whole signature fell apart — told us
something was wrong. Our conclusion was the right one: **the architecture was
flawed.** Its attention was not doing unification. It was a learned shortcut, and
the noise exposed it.

## 5. What "flawed" turned out to mean

The long search that followed (the FSQ memory, the JEPA objectives, the
reconstruction variants, the association/predictive layers) was, in the light of
this theory, a search for an architecture whose attention *had* to do real work.
The failures were diagnostic:

- **Content-blind representations.** Temporal self-distillation alone taught the
  memory to predict *time*, not stimulus content — a representation that ignores
  the scene needs no attention.
- **Collapse to the uniform fixed point.** The self-supervised objectives were
  satisfiable by input-invariant codes, and the anti-collapse terms could be
  fooled by spatial variation or by the injected noise itself.
- **The change was the crux.** The task's decision-relevant event is a transient
  orientation step; every design that failed did so because the change never
  entered the representation, and therefore attention had nothing to unify.

Each failure sharpened the requirement: the architecture must make the *binding*
of the current sensory evidence into a decision-relevant state a necessary
operation, not an optional one.

## 6. The architecture that matches the theory

The convolutional recurrent-transformer memory was built to satisfy exactly that
requirement, and its central piece is a literal unification operator:

- **Convolutions at every layer.** Spatially local, translation-equivariant
  processing — the substrate of a perceptual map, not a global readout.
- **The per-pixel two-way gate.** At every pixel, the model computes
  `[A_X, A_H] = softmax(<Q, K_X>, <Q, K_H>)` and forms
  `attended = A_X · V_X + A_H · V_H` — a *per-pixel blend of the current visual
  evidence and the remembered state*. This is unification in its most direct
  form: every location decides, continuously, how much of the current stimulus
  and how much of memory should compose the percept there.
- **Concatenated residuals and squeeze-and-excitation.** The unified map is
  built by mixing, not by adding away — the percept is assembled from preserved
  parts.
- **A report read from the unified state, with full gradient flow.** The
  decision (change or no change) is derived from the pooled percept, and the
  learning signal is allowed to shape the entire assembly.

## 7. The signatures we now see

The preliminary results give the theory ground to stand on, precisely because the
attention is now *behaving* the way the theory says it must:

- **The change opens the gate at the changed cell.** At the change frame, the
  visual gate A_X rises by ~+0.05 specifically in the quadrant where the change
  occurred (+0.048 for a change on S1, +0.040 for a change on S4). Attention
  concentrates where the percept must be updated — it is *selecting the content
  that defines the decision*.
- **The cue is attended, with a validity gradient.** At the cue frame, the gate
  at the cued location is higher than elsewhere, and it decreases monotonically
  as cue validity drops (100% → 75% → 50% → 25%). Attention weighs the
  *reliability* of the information it binds — exactly what a unification
  operation should do.
- **The decision rides on the unified state, not on the head.** A fresh linear
  probe reads the change at ~87% accuracy from the frozen representation. The
  percept carries the decision; the readout is incidental.
- **Difficulty follows a ladder, not a wall.** Under the θ-curriculum, the model
  descends smoothly to θ≈32° and then plateaus near the 85% bar. We are not
  after a solver — the plateau is fine — but the smooth descent says the
  attention is tracking the actual difficulty of the percept to be formed.

The important contrast: **these are the effects the set-size battery showed us,
now re-emerging in a new architecture whose attention mechanism is explicit and
per-pixel.** The theory survived a change of architecture. That is the first
real evidence that we are measuring something about attention itself, and not an
artifact of one network.

## 8. The prediction the theory makes next

If the claim is right — attention *unifies* the percept — then the following
must hold:

**Adding noise to the memory should make the attention signatures more
dramatic, not less.** A noisier memory makes the remembered component of the
percept less trustworthy, so the unification operation must work harder: the
gates should show stronger spatial contrast, sharper openings at the change, and
a clearer validity gradient — the system leaning more heavily and more
selectively on the reliable visual evidence while explicitly re-weighting the
corrupted memory.

This is exactly the experiment that *failed* in the old architecture — the noise
killed the signature, which told us the attention was fake. Running the same
perturbation on the new architecture is therefore the cleanest test of the
theory we have. The next experiment doubles the noise on the memory. If the
attention signatures amplify, the theory gains predictive power: it will have
told us, in advance, what a perturbation would do. If they wash out again, the
theory — and the architecture — need another revision.

## 9. What would confirm the story

- Attention signatures that **amplify** under memory noise (the gate working
  harder), not degrade — unification under perturbation.
- Signatures that remain **localizable** (we can say *where* the percept is
  being assembled) across conditions and noise levels.
- Downstream decisions that remain **derivable from the unified state** by
  simple readouts, even as the raw stimulus becomes harder.

The project's goal was never a perfect solver. It was an architecture whose
attention we can read — a system in which "where is the model looking, and what
is it binding, and how does the decision follow from that" are answerable
questions. We are closer to that goal than we have ever been.
