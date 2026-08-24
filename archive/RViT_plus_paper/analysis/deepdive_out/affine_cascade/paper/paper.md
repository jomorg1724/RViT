## Abstract

We give a mechanistic deep dive on **affine\_cascade**, a recurrent vision transformer for cued
orientation-change detection built from *two* affine-modulated self-attention stages and *two*
spatial LSTM memories, read out by a *split* actor/critic head: the first stage's memory $H_1$
feeds the critic and the second stage's memory $H_2$ feeds the actor. Trained from sparse reward
on the seven-step, four-stimulus task with a frozen pretrained VAE front-end (snapshot at
$24{,}000$ iterations), the agent detects changes at near-ceiling for large changes (cued hit
$0.985$, false-alarm $0.083$) and shows a reliability-scaled spatial cueing benefit (cued-versus-
uncued threshold advantage growing from $+1.1^\circ$ at $25\%$ to $+4.9^\circ$ at $75\%$ cue
reliability). Four mechanistic analyses reveal a clean **stage dissociation**: (i) the first
transformer *orients to the cue* — its attention to the cued patch swaps with the cue (cue@$S_1\to
S_1$, cue@$S_4\to S_4$) and climbs to $\approx0.8$ during the stimulus even with no change, with a
further bump to $0.93$ when a change occurs there — whereas the second transformer's attention is
position-biased and does not track the cue (cue-following index $+0.66$ vs $+0.02$); (ii) the
*critic's* memory $H_1$ maintains the cue location at
ceiling ($1.00$) for the entire trial, whereas the *actor's* memory $H_2$ lets it decay to
$\approx 0.6$; (iii) the critic is modestly calibrated and its outcome uncertainty falls with
evidence ($0.28\to0.06$); and (iv) — unlike the lab's split-readout cross-talk model — biasing
either transformer's attention is a *weak* causal lever on behaviour, indicating that
affine\_cascade computes through feature-wise affine modulation ($\Gamma,\beta$) rather than
through attention reallocation. The picture is of a two-stage agent whose first stage does the
perceptual work and holds the cue, and whose second stage reads a processed decision signal.

## 1. Introduction

The recurrent vision transformer parses each video frame into spatial tokens, runs a recurrent
self-attention block whose attention is computed jointly from the image and a working memory,
writes that memory with a spatial LSTM, and reads it with a distributional actor--critic head.
The **affine\_cascade** variant studied here makes two design choices at once: it stacks *two*
such stages in a cascade, and it *splits* the readout so the two streams feed different heads.
Each stage's attention is **affine-modulated** — the memory derives a feature scale-matrix
$\Gamma$ and shift $\beta$ that transform the image before a standard self-attention
($X' = \Gamma(H)X + \beta(H)$). This report asks what each stage computes, where the cue is held,
which stream carries the decision, and whether attention is the causal lever.

### 1.1 The architecture in one paragraph

Per frame, stage one applies affine self-attention to the VAE tokens $X$ with feedback from its
own memory, $Z_1 = \mathrm{SA}_{\mathrm{aff}}(X;H_1)$, and writes $H_1 \leftarrow \mathrm{LSTM}_1(Z_1)$;
stage two applies affine self-attention to $Z_1$ with feedback from $H_2$,
$Z_2 = \mathrm{SA}_{\mathrm{aff}}(Z_1;H_2)$, and writes $H_2 \leftarrow \mathrm{LSTM}_2(Z_2)$. The
actor reads the flattened $H_2$; the critic reads the flattened $H_1$. By construction $H_1$ is
independent of stage two, so the critic pathway is a strict prefix of the actor pathway.

## 2. Methods

### 2.1 Task and front-end

The seven-step cued change-detection task presents a blank frame, a spatial cue (a ring whose
completeness encodes reliability) at one of two locations, a blank, then four noisy Gabor
quadrants; on half the trials one quadrant changes orientation at $t=5$. Reward is uniform
($+1$ for a correct detection after the change or a correct rejection) and the cue is achromatic,
so — unlike the long-task v-series — there is *no* value-by-colour structure to report. The
front-end is a reconstruction-pretrained, frozen patch-VAE producing four $140$-d tokens.

### 2.2 Faithful extraction and intervention

All analyses use the model's own forward step. The two attention maps $\mathrm{aw}_1,\mathrm{aw}_2$
(one per transformer, each $4\times4$) and the two memories $H_1,H_2$ are read directly from the
recurrent state. For the causal experiment we add a logit bias to a chosen patch's attention
column in either transformer ($\mathtt{attn\_clamp}=\{\mathrm{t1|t2}:\{j:b\}\}$) and sweep $b$.

### 2.3 Analyses

Behaviour (psychometric/chronometric by cue reliability, cued vs.\ uncued); attention allocation
(per-frame spatial maps and cued-patch timecourses for both transformers); temporal linear
decoding of task variables from $H_1$ vs.\ $H_2$ (balanced-accuracy logistic readouts, 3-fold CV);
causal attention biasing; and value/critic calibration.

## 3. Results

### 3.1 Behaviour: a reliability-scaled cueing benefit

The agent solves the task: the cued psychometric function is steep and saturates near $1.0$ for
large changes (cued hit $0.985$ at $\Delta=64^\circ$), with a false-alarm rate of $0.083$
(Figure 1). The cued curve sits left of the uncued one — a spatial cueing benefit — and the
threshold advantage grows with displayed cue reliability, from $+1.1^\circ$ at $25\%$ to
$+2.6^\circ$ at $50\%$ to $+4.9^\circ$ at $75\%$. At $100\%$ reliability the measured benefit
falls back to $+1.1^\circ$; this is an artefact of the protocol rather than the model, because a
perfectly reliable cue makes *uncued* change trials off-distribution. Reaction time decreases
mildly with change magnitude.

![Behaviour. **A:** cued psychometric by displayed cue reliability. **B:** cued vs.\ uncued at $100\%$ reliability. **C:** chronometric reaction time vs.\ change magnitude. Thresholds and false-alarm rates are printed beneath; the cued advantage grows from $25\%$ to $75\%$ reliability.](figs/fig_behaviour.pdf){width=100%}

### 3.2 Attention allocation: stage one orients to the cue, stage two does not

The two transformers allocate attention very differently (Figures 2, 3). **Stage one orients to
the cued location.** With the cue forced at $S_1$, its attention to $S_1$ climbs through the
stimulus period to $0.79$ *even on no-change trials*; move the cue to $S_4$ and the peak follows
(attention to $S_4$ reaches $0.79$, while attention to $S_1$ falls to $0.13$) — a cue-following
index of $+0.66$. An actual change at the attended location adds a further bump (to $0.93$). This
is a genuine cue-orienting attention, and it is notable: the lab's multiplicatively-gated model is
change-locked and does *not* orient on this task. **Stage two does not track the cue.** Its
attention is position-biased: at the cue/blank frames it fixates a single quadrant ($S_4$ for a
left cue; the top-right quadrant for a right cue) regardless of where the cue actually is, and is
diffuse thereafter (cue-following index $+0.02$).

![Per-frame attention maps for both transformers, $100\%$ cue at $S_1$ (top-left, cyan), no-change and change conditions; scores printed in each $2\times2$ cell. Stage one (T1$\to H_1\to$critic) concentrates on the cued quadrant during the stimulus ($0.79$ with no change) and reaches $0.93$ when a change occurs there; stage two (T2$\to H_2\to$actor) fixates an off-cue quadrant at the cue/blank frames (here $1.00$ on $S_4$) and is diffuse later.](figs/fig_attention_maps.pdf){width=92%}

![Cue-following (no change): attention to $S_1$ vs.\ $S_4$ over the trial, per transformer (rows) and cue position (columns). Stage one's peak *swaps* with the cue — it orients; stage two's peak stays on the same quadrant regardless of the cue — it does not follow. Same forced-cue protocol as Figure 2.](figs/fig_attention_timecourse.pdf){width=100%}

### 3.3 What the two memories hold: the critic's memory keeps the cue

Temporal linear decoding (Figure 4) reveals the deepest dissociation. The **cue location** decodes
at ceiling from *both* memories at cue onset, but only the **critic's** memory $H_1$ *maintains* it
— staying at $\approx1.00$ through the entire delay and stimulus period — while the **actor's**
memory $H_2$ lets it decay to $\approx0.6$ by the decision. Cue reliability is decodable only
transiently around the cue. The changed location is decoded only weakly from either memory
($\le0.45$, chance $0.25$). So the cue prior lives in the first-stage memory that feeds the critic,
not in the actor's memory; the actor reads a representation from which the raw cue has largely
washed out.

![Temporal linear decoding of task variables from memory, $H_1$ (critic) vs.\ $H_2$ (actor). **A:** cue location is *maintained* at ceiling in $H_1$ but decays in $H_2$. **B:** reliability decodes transiently. **C:** the changed location is only weakly linearly available in either memory.](figs/fig_decoding.pdf){width=100%}

### 3.4 Causal attention: a weak lever — computation is in the modulation, not the map

Biasing either transformer's attention toward the changed quadrant over $b\in[-6,6]$ moves
behaviour only slightly (Figure 5). Stage-one bias has a small *negative* effect on the hit rate
($0.917\to0.867$ as bias goes $0\to+6$; $-0.09$ over the full sweep); stage-two bias has no
consistent effect ($\pm0.05$, no trend); and neither bias moves the critic's outcome uncertainty
(flat at $\approx0.12$). This is markedly different from the lab's split-readout *cross-talk* model,
where salience clamps strongly move the decision and top-down clamps move value. The natural
reading is mechanistic: affine\_cascade does its work through the *feature-wise affine modulation*
$\Gamma(H)X+\beta(H)$ applied before attention, so reweighting the post-modulation attention map is
a weak intervention. The decision is robust to where attention points.

![Causal attention. **A:** biasing each transformer's attention toward the changed quadrant barely moves the decision (hit rate). **B:** and does not move the critic's uncertainty. Attention reallocation is a weak lever in this model, unlike the cross-talk variant.](figs/fig_causal.pdf){width=88%}

### 3.5 A calibrated critic whose uncertainty tracks evidence

The distributional critic (which reads $H_1$) is modestly calibrated: per-step predicted value
correlates with the realised discounted return ($r=0.22$), state value rises over the trial as
evidence accumulates, and — the cleanest value signature — the critic's outcome uncertainty
(quantile spread just after the change) falls monotonically as the change becomes more detectable
($0.28$ at $\Delta=4^\circ \to 0.06$ at $\Delta=64^\circ$; Figure 6). More detectable changes
leave the value function more certain about the outcome.

![Value / critic. **A:** state value over the trial, change vs.\ no-change. **B:** critic calibration (per-step predicted value vs.\ realised return). **C:** outcome uncertainty falls as the change grows more detectable.](figs/fig_value.pdf){width=100%}

## 4. Discussion

**A two-stage division of labour.** The results cohere into a single account. The first stage —
its attention, its memory $H_1$, and the critic it feeds — does the *perceptual* work: it *orients*
attention to the cued quadrant (the peak tracks the cue) and holds the cue location at ceiling for
the whole trial. The second stage — $H_2$ and the actor — reads a *processed* signal in which the
raw cue has decayed, and issues the decision. That the **critic** ends up holding the stimulus while the
**actor** holds a more abstract code is the opposite of the naive expectation, and follows directly
from the cascade: because the actor's memory is two transformations downstream of the image, the
linearly-recoverable stimulus content has been transformed away by the time it reaches $H_2$.

**Stage one orients to the cue — but the orienting is a correlate, not the lever.** Unlike the
multiplicatively-gated model, affine\_cascade *does* produce a cue-orienting attention map (stage
one, §3.2). Yet biasing that map barely moves behaviour (§3.4). These are reconciled by where the
computation lives: the cue prior is held in the memory $H_1$ (decodable at ceiling all trial), the
stimulus is transformed by the feature-wise affine modulation $\Gamma,\beta$, and the attention
map is a *readout* of that orienting rather than the causal bottleneck. So the cueing benefit is
memory-borne and the decision is robust to attention clamps, even though the attention visibly
follows the cue — the map reflects the computation without gating it.

**Limitations.** This is a snapshot at $24{,}000$ of $50{,}000$ iterations (cued hit already
$0.985$ at large $\Delta$); the analysis should be re-run at convergence. The $100\%$-reliability
cueing point is confounded by off-distribution uncued trials. The causal null is a property of
this model's mechanism, but the clamp acts only on the post-modulation attention; a complementary
intervention on $\Gamma,\beta$ would localise the computation more directly and is the natural next
experiment.

## 5. Conclusion

affine\_cascade learns cued change detection well and exposes a clean two-stage dissociation: a
first stage that orients attention to the cue and holds it for the critic, and a second stage that
reads a processed code for the actor. Its cueing benefit is memory-borne and reliability-scaled,
its critic is calibrated with evidence-tracking uncertainty, and — distinctively — its decision is
computed through affine feature modulation rather than attention reallocation, making the attention
map a weak causal lever. The model is a strong, interpretable candidate whose mechanism differs
informatively from the multiplicative and cross-talk variants.
