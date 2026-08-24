# A Recurrent Vision Transformer Learns a Posner-Style Change-Detection Task: Behaviour, Attention, Latent Codes, and Value

### A mechanistic deep dive into a memory-as-tokens recurrent attention model trained by reinforcement learning

---

## Abstract

We present a comprehensive mechanistic characterization of a recurrent vision
transformer (RViT+, "v5" memory-as-tokens variant) trained by reinforcement
learning to perform a Posner-style cued change-detection task. The agent views a
50×50 RGB video of four oriented Gabor patches, is shown a coloured spatial cue
whose reliability and reward value vary trial-to-trial, and must press at the
moment one patch changes orientation — withholding on no-change trials. The model
is conv-free: each frame is patchified into a 10×10 grid of tokens which a
two-layer transformer encoder processes by treating its own recurrent memory **as
tokens** (self-attention over [patch ++ H₁ ++ H₂] = 3·N tokens per layer), with
per-layer LSTM memories carried across frames; two transformer-decoder heads with
a CLS read-out implement a policy actor and a distributional (QR-DQN) critic.

Across five analyses we find: **(1) Behaviour.** The trained agent produces a
textbook psychometric function (P(hit) rising monotonically with orientation-change
magnitude) and chronometric function (reaction time falling with magnitude), with a
robust spatial-cueing benefit — validly cued changes are detected at lower
thresholds and shorter latencies than invalidly cued changes — and value-directed
attention, with higher-reward (red) cues detected better and faster than
lower-reward (blue) cues. False alarms on no-change trials are rare.
**(2) Attention.** Mapping per-head, per-layer attention across all four
transformers, and projecting the summed-column α statistic back onto the stimulus,
reveals a sharp functional dissociation: the encoder's attention is near-uniform
(a learned distributed read of the whole display), while the decoder's final-layer
CLS read-out is spatially sharp and snaps onto the changed quadrant at change onset.
**(3) Latent codes.** Linear decoders recover cue colour and cue reliability at
ceiling, the changed location and change magnitude well above chance (emerging only
after change onset), and an explicit elapsed-time clock, from the recurrent memory.
**(4) Causal attention.** Additive per-head attention biasing produces only modest,
inconsistent behavioural shifts — the distributed memory-as-tokens code is robust to
single-head perturbation, in contrast to the clean causal control obtainable in
simpler attention bottlenecks. **(5) Value.** The critic is well-calibrated:
state values track the discounted expected reward almost exactly (slope ≈ 1, near-
identity calibration), are ordered by cue value (≈5/3/1 for red/green/blue), rise as
the rewarded change approaches, and the distributional spread (an uncertainty proxy)
resolves around a clearly-seen change but grows around a near-threshold one. Attention
manipulations leave value and detection largely intact while shifting the critic's and
policy's uncertainty monotonically — the value-side reflection of the distributed code.

Together these results show that an RL-trained recurrent transformer solves the task
by a division of labour between a distributed sensory encoder and a sharp, change-
triggered decision read-out, and reproduces several hallmark signatures of covert
spatial and value-directed attention at the behavioural level while implementing them
through a mechanism that is mechanistically distinct from a single attentional
bottleneck.

---

## 1. Introduction

Covert visual attention is classically probed with the Posner cueing paradigm: a
spatial cue precedes a target, and behaviour reveals a *validity effect* — faster,
more accurate responses when the cue correctly predicts the target location — that
scales with the cue's reliability. A parallel literature on *value-directed
attention* shows that the reward associated with a location or feature further
biases perception and response. These phenomena are usually studied in humans and
animals; a complementary question is whether, and how, an artificial agent trained
purely to maximize reward on such a task develops the same behavioural signatures,
and what internal mechanism it uses to do so.

This paper studies one such agent in depth. The model — RViT+ (v5) — is a recurrent
vision transformer trained end-to-end by reinforcement learning on a cued
change-detection environment. It is deliberately conv-free and recurrent: rather
than a convolutional feature stem, the image is cut into patches and embedded as
tokens; rather than feed-forward processing, two transformer layers carry per-layer
recurrent memories across video frames, and — the defining feature of this variant —
they incorporate that memory **as additional tokens** in the self-attention, so each
layer attends jointly over the current patch tokens and all of its memory rows. A
policy head and a distributional value head, each a small transformer with a CLS
read-out, turn the recurrent state into an action and a value estimate.

Because attention is both the computational primitive of the architecture and the
psychological object of the task, the model is an unusually direct substrate for
asking *what attention does* inside a trained network. We exploit this with five
linked analyses, organised to move from behaviour to mechanism:

1. **Psychometrics & chronometrics.** We characterise accuracy and reaction time as
   a function of change magnitude across every cue valid/invalid combination, cue
   reliability, and cue value, establishing that the agent reproduces the
   behavioural hallmarks of spatial and value-directed attention.

2. **Attention maps & the α projection.** We extract per-head, per-layer attention
   for all four transformers (two encoder layers, the actor decoder, the critic
   decoder) and introduce a simple, intuitive read-out: the *α* statistic — the
   summed column attention to a patch divided by the number of query tokens —
   projected back onto a box the shape of the input image.

3. **Latent decoding.** We ask what task variables (cue colour, cue reliability,
   change location, change magnitude, change timing) are linearly decodable from the
   recurrent latents, and when in the trial each becomes available.

4. **Causal attention manipulation.** We intervene directly on the pre-softmax
   attention logits of individual heads to make the encoder more or less responsive
   to the stimulus, and measure the causal effect on detection behaviour and value —
   testing whether attention here is a manipulable control knob or a distributed,
   redundant code.

5. **Value and uncertainty.** We test whether the critic learned *appropriate*
   values (calibration against realised returns, ordering by reward, dynamics around
   the change), quantify the distributional uncertainty of the value estimate, and
   measure how attention manipulations distort value.

The contributions are (i) a complete behavioural phenotype of an RL-trained
recurrent transformer on a cued change-detection task; (ii) a per-head, per-layer
attention atlas with an interpretable spatial projection; (iii) a decoding map of
the recurrent latent code; (iv) a causal test of attention's behavioural leverage;
and (v) a calibration and uncertainty analysis of the learned value function. The
emerging picture is of a *distributed encoder / sharp decoder* division of labour
that produces attention-like behaviour without a single attentional bottleneck.

### 1.1 Background and related work

The task is a dynamic, response-based variant of the **Posner spatial-cueing
paradigm** (Posner, 1980), in which a spatial cue precedes a target and behaviour
reveals faster, more accurate responses on validly cued trials; the cue's reliability
modulates the size of this validity effect. We additionally vary the reward associated
with the cue, engaging **value-directed attention**, the finding that reward history
and value bias attentional selection independently of physical salience (Anderson,
Laurent & Yantis, 2011). Reproducing both effects in a single trained agent lets us ask
where each is implemented.

The model belongs to the family of **vision transformers** (Dosovitskiy et al., 2021),
which tokenise an image into patches and process them with self-attention (Vaswani et
al., 2017), here made *recurrent* by carrying per-layer memories across frames and —
distinctively — by treating those memories as additional attention tokens. It is
trained by reinforcement learning with a **distributional value critic** in the
quantile-regression style of QR-DQN (Dabney et al., 2018) and an actor objective in the
**maximum-a-posteriori policy-optimisation** family (Abdolmaleki et al., 2018), which
gives us a principled, distribution-valued value head to interrogate.

Methodologically we draw on three interpretability traditions: **attention-map
analysis** (reading per-head attention weights, here summarised by the α projection);
**linear decoding / population read-out** (training simple decoders on internal
activity to ask what is represented and when), the machine-learning analogue of
multivariate pattern analysis in neuroscience; and **activation intervention** (editing
internal signals — here the pre-softmax attention logits — and measuring the causal
effect on behaviour). Bringing these to bear on one reward-trained recurrent
transformer is what lets us connect its attentive *behaviour* to its internal
*mechanism*.

---

## 2. Methods

### 2.1 The change-detection environment

Each trial is a 29-frame, 50×50 RGB video. Frame 0 is blank; frame 1 displays a
**spatial cue**; frame 2 is blank; from frame 3 onward the display shows four
oriented **Gabor patches**, one in each 25×25 quadrant (top-left = S1, bottom-left =
S2, top-right = S3, bottom-right = S4). Each Gabor's orientation is fixed per trial
(plus small per-frame orientation noise). On a change trial (probability ½), at a
randomly drawn **change time** Tc ∈ [11, 25] one patch's orientation steps by a
signed magnitude Δθ ∈ [−64°, +64°]; on a no-change trial no patch ever changes.

The **cue** (frame 1) is a coloured disc-and-ring glyph drawn in one quadrant. Its
**position** (left ⇒ S1 top-left, or right ⇒ S4 bottom-right) indicates the likely
change location; its **colour** (red, green, blue) signals the reward delivered for
a correct detection (5, 3, 1 respectively); and its **ring proportion** p ∈ {0.25,
0.5, 0.75, 1.0} sets both the fraction of the ring drawn (a visible reliability
signal) and the probability the change actually occurs at the cued location. Thus a
*valid* trial is one where the change appears at the cued quadrant, an *invalid*
trial one where it appears elsewhere, and p is the displayed cue reliability.

The agent emits a binary action each frame: **wait** (0) or **press** (1). Pressing
before Tc ends the trial with zero reward (a premature/false-alarm error). Pressing
at or after Tc on a change trial yields the cue-colour reward (a hit). Pressing on a
no-change trial yields zero. Waiting through the final frame yields the cue-colour
reward on no-change trials (a correct rejection) and zero on missed change trials.
Optimal behaviour is therefore to press as soon as a change is detected and to
withhold otherwise — a speed/accuracy trade-off whose difficulty is set by Δθ. Hits
define a **reaction time** RT = (press frame − Tc).

For analysis we use a *forced-trial* harness that overrides individual latent
factors (cue side, colour, ring, change presence/time/location, Δθ magnitude) while
randomising the rest, and either lets the agent act greedily (argmax policy) or
forces it to wait so every trial runs the full episode (used whenever we need the
attention/latent/value time-course over the whole trial). Unless stated, the change
is placed at the cued S1 location for *valid* conditions and at a random uncued
quadrant for *invalid* conditions.

### 2.2 The RViT+ v5 architecture

The model has ~1.62 M parameters and four transformer stacks. *(Full hyperparameters
in Appendix A.)*

**Patch embedding (conv-free).** Each 50×50×3 frame is reshaped into a 10×10 grid of
non-overlapping 5×5×3 patches (N = 100 tokens; each 25×25 Gabor quadrant is exactly a
5×5 block of tokens). A shared two-layer MLP (75 → 128 → 128) with LayerNorm expands
each raw patch to the model width d = 128, and a learned positional embedding is added.

**Memory-as-tokens encoder.** Two recurrent layers each maintain a memory state
$H_\ell \in \mathbb{R}^{N\times128}$. At each frame, layer ℓ forms the token sequence
[ patch tokens + source-tag ++ H₁ + pos + tag ++ H₂ + pos + tag ] of length 3·N =
300, runs a pre-norm transformer encoder layer (4 heads) over it, and uses the
*patch-token outputs* (the first N positions) to drive a shared LSTM cell that
updates that layer's memory. Layer 2 consumes layer 1's output and the just-updated
H₁, giving a hierarchical recurrence. The two memory states H₁, H₂ are the encoder's
output, read by both decoders.

**Actor and critic decoders.** Each head concatenates the two memory states into a
2·N = 200-token sequence, prepends a learned **CLS** token, adds a positional
embedding, runs a two-layer transformer (4 heads), and decodes the CLS row through a
two-layer MLP. The **actor** emits two action logits. The **critic** is
distributional: a learned per-action code is added to the input tokens and the
decoder is run once per action, emitting Q(s, a, ·) as 51 quantiles (QR-DQN);
the state value V(s) is the policy-weighted (expected-SARSA, stop-grad-on-π) mixture
of the action quantile distributions.

**Training.** The agent was trained by reinforcement learning with a distributional
QR-DQN critic, a PAC actor loss (an MPO closed-form E-step plus a behaviour-cloning
term, replacing PPO's clipped surrogate), a periodically-updated target network, a
short critic burn-in, and prioritized episode replay. The analyses below were run on
the converged model (asymptotic behaviour; reported metrics reflect behaviour, not a
training-iteration count).

### 2.3 Faithful attention extraction and the α statistic

To read attention without perturbing the trained computation we reimplemented every
transformer's multi-head self-attention from its own weights (in-projection, scaled
dot-product, soft-max, out-projection), verified to reproduce the stock module's
output to < 10⁻⁵ on the encoder memories and both decoder read-outs (so in eval-mode,
with dropout disabled, the recomputed forward is identical to the model's own). This
recomputation both exposes the per-head attention weights and provides the single
injection point for the causal experiment (§2.5).

For an attention matrix A with query index *i* and key index *j*, we summarise the
attention *received* by key *j* with the **α statistic**

> α_j = ( Σ_i A[i, j] ) / (number of query tokens),

i.e. the mean incoming attention to token *j*. For the encoder the queries are all
3·N tokens and *j* runs over the N patch (image) keys; for the decoders the query is
the CLS read-out row and α_j sums the H₁ and H₂ contributions of patch position *j*.
Because patch token *j* corresponds to a 5×5 image block, the N-vector α reshapes to
the 10×10 grid and is **projected back onto a 50×50 box** (nearest-neighbour block
expansion) so it can be overlaid directly on the stimulus — an intuitive, image-space
view of where each head is "looking." We never average over heads (heads specialise
and can attend to opposite locations, so head-averaging cancels real structure); all
maps are per head, per layer.

### 2.4 Linear decoding of latents

To ask what the network represents, we recorded, at every frame of a large bank of
fully-randomised forced-wait trials, the token-mean and per-quadrant-pooled H₁/H₂
memories and the actor/critic CLS read-outs, and trained cross-validated linear
decoders (multinomial logistic for categorical targets, ridge for continuous
targets; 5-fold CV; standardised features; label-shuffled controls) for each task
variable from each latent at each timestep. This yields a temporal decoding curve
(when does information become available?) and a peak-decodability summary. Targets:
cue colour (3-way), cue reliability (4-way and ordinal), changed location (4-way),
change magnitude (|Δθ| regression), whether the change has occurred yet (binary,
per frame), change onset time (regression), and absolute frame index (a clock
control).

### 2.5 Causal attention manipulation

We added a constant bias *b* to the pre-softmax attention logits of a single encoder
(layer, head) over the patch (image) keys, broadcast across all queries: *b* > 0
forces that head to attend more to the stimulus, *b* < 0 to attend less (toward the
recurrent memory). We swept *b* ∈ [−6, +6] for each of the eight encoder heads (2
layers × 4 heads) individually and for all heads jointly, holding the change at a
near-threshold magnitude (where there is room to move), and read off the causal
effect on P(hit), RT, premature rate, the value of acting, and uncertainty —
comparing every bias level on the *same* trials (matched seeds) for a paired
estimate.

### 2.6 Value and uncertainty measures

We summarised the critic's distributional output two ways: the **standard deviation**
of its 51 quantiles, and a differential-entropy-like **quantile entropy** (treating
consecutive quantiles as equal-probability bins). Calibration was assessed by
regressing the predicted $V(s_t)$ on the realised discounted Monte-Carlo return-to-go
under the agent's own greedy policy, pooled over visited states. Policy entropy is
the Shannon entropy of the action distribution.

---

![Cued change-detection task. A 29-frame trial: blank, a coloured spatial cue (here red, top-left/S1, ring proportion 0.75 signalling reward 5 and a 75 %-reliable location), blank, then four Gabor patches; at the change time one patch's orientation steps (here S1, |Δθ| = 55°). The agent presses to report the change.](figs/fig_task.png)

![The RViT+ v5 architecture. Each frame is patchified (no convolution) into 100 tokens; a two-layer encoder processes them by attending jointly over the patch tokens and its own recurrent memory rows (memory-as-tokens), updating per-layer LSTM memories carried across frames; transformer-decoder actor and critic heads read the two memory states through a CLS token.](figs/fig_arch.png)

## 3. Results

We organise the results from behaviour to mechanism. Section 3.1 establishes the
behavioural phenotype; 3.2 maps attention across all four transformers and
introduces the encoder/decoder dissociation; 3.3 reads out the latent code; 3.4
intervenes causally on attention; 3.5 dissects the value function.

### 3.1 The agent reproduces the behavioural signatures of spatial and value-directed attention

**Psychometric and chronometric functions.** Detection accuracy rises monotonically
with orientation-change magnitude, from near-zero at |Δθ| = 2° to ceiling by ≈ 25–32°,
and median reaction time falls correspondingly (from ≈ 10 frames near threshold to a
single frame for large changes) — the textbook psychometric/chronometric pair
(Fig. \ref{fig:psy}A). A two-parameter logistic gives a 50 %-detection threshold of
≈ 9.7° (valid) with a steep slope (width ≈ 2.5°). False alarms are rare: on no-change
trials the agent correctly withholds on **97.8 %** of trials (false-alarm rate 2.2 %),
and the premature-press rate on change trials is near zero — the agent has learned the
withhold-until-confirmed criterion the reward structure demands.

**Spatial cueing (validity) effect.** Validly cued changes (change at the cued S1
location) are detected better and faster than invalidly cued ones (change at an uncued
location) throughout the rising part of the curve — e.g. at |Δθ| = 10° P(hit) = 0.55
(valid) versus 0.42 (invalid), and at 12° 0.70 versus 0.56 — converging only once the
change is supra-threshold. The fitted threshold is lower for valid than invalid trials
(**9.65° vs 10.99°**, a cueing benefit of **Δx₅₀ ≈ 1.3°**; Fig. \ref{fig:psy}). The
effect is spatially symmetric across cue-left and cue-right (Fig. \ref{fig:side}), and —
matching the classic prediction that the cueing benefit scales with cue reliability — the benefit grows
modestly with the *displayed* ring reliability (Δx₅₀ ≈ 1.2° at ring 0.25 rising to
≈ 1.7° at ring 1.0; Fig. \ref{fig:ring}): the valid threshold is essentially constant
(≈ 9.5°) while the invalid threshold worsens as the cue looks more reliable, exactly as
a stronger cue prior should cost more when it misleads.

**Value-directed attention.** Higher-value cue colours yield better and faster
detection at fixed change magnitude: red (reward 5) > green (3) > blue (1) at every
sub-ceiling magnitude — at |Δθ| = 10°, P(hit) = 0.69 / 0.63 / 0.25 for red / green /
blue, with red also responding a frame or two faster (Fig. \ref{fig:val}). The agent
thus allocates more effective sensitivity to changes that are worth more — the
behavioural signature of value-directed attention, whose value-function substrate we
identify in §3.5.

These behavioural signatures — graded detection, a reliability-scaled spatial validity
effect, value-directed sensitivity, and a near-perfect withholding criterion —
establish that the trained agent behaves like an attentive observer; the remaining
sections ask how.

![**Psychometric and chronometric functions.** P(hit) (left) and median RT (right) versus orientation-change magnitude, valid (change at cued S1) versus invalid (change at uncued), with logistic fits; the valid threshold sits left of the invalid threshold (cueing benefit Δx₅₀ ≈ 1.3°). \label{fig:psy}](figs/exp1A_core.png)

![**Cueing benefit scales with displayed cue reliability.** Left: 50 % detection threshold for valid and invalid trials versus the ring proportion. Right: the cueing benefit (invalid − valid threshold) grows with displayed reliability. \label{fig:ring}](figs/exp1C_ring.png)

At the **fully reliable cue (ring = 1.0)** the full valid-vs-invalid psychometric and
chronometric functions show the largest cueing effect of any reliability level: the
fitted thresholds are 9.6° (valid) versus 11.2° (invalid), a benefit of **Δx₅₀ ≈ 1.6°**
(versus ≈ 1.3° at ring 0.75), with the invalid curve shifted rightward and its RTs
elevated through the rising regime while the valid curve is essentially unchanged from
ring 0.75 (Fig. \ref{fig:ring1}). This is the expected pattern: a maximally reliable cue
builds the strongest spatial prior, which helps when it is correct (valid, already near
the reliability-independent ceiling for the cued read-out) and costs the most when it
misleads (invalid).

![**Full valid-vs-invalid psychometric/chronometric at ring = 1.0 vs 0.75.** Solid = fully reliable cue (ring 1.0), dashed = partial (0.75). The validity gap (valid above invalid in P(hit); valid faster in RT) is present at both reliabilities and is largest at ring 1.0, where the invalid curve is most right-shifted. \label{fig:ring1}](figs/exp1_core_compare_ring.png)

![**Value-directed attention.** P(hit) (left) and RT (right) versus change magnitude for blue/green/red cues (reward 1/3/5); higher-value cues are detected better and faster. \label{fig:val}](figs/exp1D_value.png)

![**Spatial symmetry control.** The valid/invalid psychometric and chronometric split, computed separately for cue-left (S1) and cue-right (S4) trials, is closely matched across the two cue sides — the cueing effect is not an artefact of one location. \label{fig:side}](figs/exp1B_side.png)

### 3.2 An attention atlas: a distributed encoder and a sharp, change-triggered decoder

Mapping per-head, per-layer attention across all four transformer stacks reveals a
sharp **functional dissociation** between the encoder and the decision read-out.

**The encoder reads the whole display.** The two memory-as-tokens encoder layers
attend almost uniformly over the patch grid throughout the trial: the most-attended
patch receives a per-key α of only ≈ 0.02–0.03 (encoder L1) and ≈ 0.005 (encoder L2),
a few-fold above the uniform floor but with no sharp spatial peak. Within this
diffuse read there is, however, a clean **top-down cue prior**: at the cue frame
(t = 1), encoder-L1 heads 0 and 3 transiently concentrate on the *cued* quadrant,
raising its share of the patch-attention budget to ≈ 0.46–0.50 — roughly twice the
0.25 uniform share — and they do so for whichever side the cue indicates (top-left
for cue-left, bottom-right for cue-right), independent of where the change will later
occur (Fig. \ref{fig:diss}, left column). Crucially, this cue orienting is *transient*:
within two frames the encoder returns to a near-uniform spatial read, and — most
tellingly — it shows **no** spatial response at the change itself. The encoder never
"points at" the changed patch (Fig. \ref{fig:enctraj}).

![**Per-head encoder L1 quadrant attention over the trial** (valid cue-left trial). Heads 0 and 3 spike on the cued top-left (S1) quadrant at the cue frame (t = 1, dotted); all four quadrants then converge to a near-uniform read, with no divergence at the change (t = 15, dashed). The encoder's only spatial act is the transient cue prior. \label{fig:enctraj}](figs/exp2_traj_enc_L1_VALID_cueLeft_chgS1.png)

**The decoder points at the change.** The actor and critic decoders are a different
animal. Their first layer is near-uniform (CLS-attention perplexity ≈ 99/100 effective
patches), but their **final layer is spatially sharp and change-triggered**. The
actor decoder's layer-2 head 2 carries a weak cue prior early in the trial (≈ 0.40–0.46
share on the cued quadrant at the cue frame), then at change onset **snaps onto the
changed quadrant**, reaching ≈ 0.88–0.95 of its CLS attention there within the change
frame and **≈ 1.0 a few frames later** (Fig. \ref{fig:diss}, right column; Fig.
\ref{fig:overlay}). The critic's layer-2 read-out (for the press action) behaves
similarly, locking onto the changed quadrant for the value-of-pressing.

**The decoder read-out is bottom-up and validity-independent.** The decisive test is
the *invalid* condition, where the cue points at S1 but the change occurs at S4. Here
the encoder's cue prior still sits on the cued S1 quadrant, but the actor's layer-2
read-out tracks the **actual change at S4** — reaching a post-change attention share of
0.99 on S4 versus 0.01 on the cued S1 (compared with 1.00 on S1 / 0.00 elsewhere when
the change is valid). The decision read-out is therefore driven bottom-up by the
change, not by the cue, which is exactly what allows the agent to detect invalidly
cued changes at all (the behavioural validity effect, §3.1, is the residual cost of
the encoder's transient cue prior, not a failure to read the change).

This is the central mechanistic finding: **spatial selectivity for the change lives
in the decoder's final-layer CLS read-out, not in the encoder.** The encoder is a
distributed sensor carrying a transient top-down cue prior; the decoder is a sharp,
bottom-up change locator that implements the press decision. The α-projection
overlays (Fig. \ref{fig:overlay}) make this visible directly in image space: at change
onset the actor-decoder heads light up as a bright spotlight precisely on the changed
Gabor, while the encoder maps remain a near-flat wash over the whole display.

Consistent with a distributed encoder, the encoder's patch-versus-memory attention
budget is stable across the trial (the heads divide their attention between the image
tokens and the recurrent memory rows without a large change-locked shift), indicating
that the encoder's contribution to detection is carried by the *content* of its
distributed read and its recurrent memory, not by a spatial re-allocation of
attention (Fig. \ref{fig:budget}).

![**Encoder patch-versus-memory attention budget over the trial**, per head and condition. Each head divides its attention between the image (patch) tokens and the recurrent memory rows; the split is roughly stable across the trial and shows no large change-locked reallocation (change at the dashed line), consistent with a distributed sensory read whose detection signal lives in content and memory rather than in a moving spatial budget. \label{fig:budget}](figs/exp2_budget.png)

![**The encoder/decoder dissociation.** Per-quadrant attention share over the trial for a representative encoder head (left) and the actor decoder's change-reading head (right), for a valid trial (top; cue and change both at S1) and an invalid trial (bottom; cue at S1, change at S4). The encoder head spikes on the *cued* quadrant at the cue (t = 1, dotted) and is otherwise uniform, never responding to the change (t = 15, dashed). The decoder head snaps onto the *changed* quadrant at change onset — S1 when valid, S4 when invalid — proving a bottom-up, validity-independent change read-out. \label{fig:diss}](figs/fig_dissociation.png)

![**α projected onto the stimulus** for the actor decoder's final layer (valid trial, cue+change at S1). Rows are heads, columns are frames; each panel overlays the α attention map (inferno) on the stimulus. At the change frame (t = 15) and after, head 2 (and head 1) form a sharp spotlight on the changed top-left Gabor. \label{fig:overlay}](figs/exp2_overlay_actor_L2_VALID_cueLeft_chgS1.png)

### 3.3 What the recurrent latents represent

Cross-validated linear decoding of the recurrent memories (2000 fully-randomised
trials; balanced accuracy for categorical targets, R² for continuous; label-shuffled
controls at chance) shows that the network holds a rich, well-structured code, and —
read frame by frame — reveals *when* each variable becomes available (Fig.
\ref{fig:decode}).

**Cue identity is encoded immediately and at ceiling.** Both the **cue colour**
(3-way) and the **cue reliability/proportion** (4-way) jump from chance before the
cue to **perfect decoding (balanced accuracy 1.00) at the cue frame**, from *every*
latent we tested (token-mean H₁/H₂, per-quadrant pools, and both decoder CLS read-
outs). The two then diverge over the trial in a behaviourally sensible way: cue
**colour — which sets the reward and is needed at the decision — is maintained at 1.00
for the whole episode**, whereas cue **proportion — the reliability prior, most useful
early — fades** (1.00 at the cue → 0.57 by t = 8 → 0.37 by t = 15). The network keeps
the value-relevant cue feature alive and lets the now-superseded reliability signal
decay.

**The change variables emerge only after the change, as accumulating evidence.**
Whether a change has occurred ("change present", binary) is decodable at **≈ 0.87
balanced accuracy from the change-time onward** and at chance before it — a clean
detection signal. The **changed location** (4-way) is best read from the *spatially
pooled* layer-1 memory (h1_quad = 0.89 peak, versus only ≈ 0.48 from the token-mean
that discards spatial layout), confirming that the encoder holds *where* the change is
in its spatial token arrangement rather than as a pooled summary. Its time-course is
revealing: it sits at a **cue-based prior of ≈ 0.45** before the change (above the 0.25
chance floor because the change is statistically tied to the cued location, which is
visible from t = 1), then **climbs to 0.89** as the change is seen and integrated
(0.53 → 0.64 → 0.78 → 0.89 across the post-change frames). The **change magnitude**
(|Δθ|, R² up to 0.64) and **change onset time** (R² up to 0.68) are, by contrast,
decodable *only after* the change and rise monotonically frame by frame (magnitude
R²: ≈ 0 pre-change → 0.10 → 0.32 → 0.63), the signature of evidence accumulation; both
are best read from the token-mean memory, consistent with their being global scalars
rather than spatial quantities. Finally, an explicit **elapsed-time clock** is strongly
encoded (absolute frame index, R² = 0.97), giving the agent the temporal reference it
needs to distinguish a premature press from a valid one.

In short, the recurrent code cleanly separates *cue variables* (available
instantaneously at the cue, value-feature maintained / reliability decayed) from
*change variables* (absent until the change, then accumulating), and represents the
change's location spatially but its magnitude and timing as pooled scalars — a
latent geometry that mirrors the encoder/decoder division of §3.2.

![**Temporal linear decoding of task variables from the v5 latents.** Each panel plots cross-validated decodability (balanced accuracy or R²) versus frame for each latent; dotted line = cue (t = 1). Cue colour/reliability are decodable at ceiling from the cue onward; change location/magnitude/onset and "change present" rise only after the change, the signature of evidence accumulation. \label{fig:decode}](figs/exp3_temporal_decoding.png)

**Decoding the full, un-pooled latent.** Mean- and quadrant-pooling are
analysis-side reductions; the model itself never averages its tokens — the encoder
memory is 100 token-vectors and the decoders read them through a CLS token that
attends over all of them. To check that pooling does not hide information, we also
decoded from the **entire flattened memory** (all 100 × 128 = 12,800 dimensions of H₁
and of H₂, and both concatenated, 25,600), at the diagnostic frames, through a
leakage-free within-fold PCA (a linear projection — not averaging — that regularises
the p ≫ n regression; shuffle controls confirm the scores are genuine, Fig.
\ref{fig:flat}). Three things emerge:

1. **Nothing is hidden by pooling.** Given enough trials, the full latent recovers
   essentially all the information the best pooled feature carries — cue colour and
   reliability at ceiling, change location 0.86 (flat) versus 0.91 (quad), magnitude
   R² 0.62–0.65 (flat, marginally *above* pooled), onset R² 0.65 — so the pooled
   read-outs of the previous paragraph are faithful summaries, not artefacts.
2. **Mean-pooling specifically destroys *location*.** The changed quadrant decodes at
   0.91 from the spatially-structured quad pool and 0.86 from the flat memory but only
   **0.34 from the token-mean** — averaging over tokens discards exactly the spatial
   information the change-location read-out needs, whereas non-spatial variables
   (colour, reliability, magnitude, onset, presence) decode equally well from the mean
   because they are carried in a distributed, location-independent form.
3. **Location lives in layer-1 memory, not layer-2.** The changed quadrant decodes at
   0.86 from flat H₁ but only 0.37 from flat H₂ — the first encoder memory is the
   spatial sensory store, while the second carries a more abstract, less spatially
   localised code. Conversely the decoder CLS read-outs discard task-irrelevant detail
   (cue reliability drops to ≈ 0.5, change onset to ≈ 0.3–0.5 from the CLS) while
   preserving decision-relevant variables (colour, change-present) — a read-out that
   compresses the recurrent code toward what the decision needs.

![**Decoding from the full flattened latent versus pooled versus CLS** (bars = cross-validated decodability; × = label-shuffled control at chance). The un-pooled flat latent matches the best pooled feature for every variable; mean-pooling uniquely collapses change-location (0.34) that quad/flat preserve (0.91/0.86); and change-location lives in flat H₁ (0.86), not flat H₂ (0.37). \label{fig:flat}](figs/exp3b_flat_decoding.png)

### 3.4 Causally manipulating attention

Can the agent be made more or less responsive to changes by intervening on attention?
We added a constant bias *b* ∈ [−6, +6] to the pre-softmax attention logits of an
encoder head over the image (patch) keys and re-ran behaviour under the greedy policy
at a near-threshold magnitude (|Δθ| = 10°, baseline P(hit) ≈ 0.54), comparing every
bias level on matched trials (Fig. \ref{fig:causal}).

**Single-head effects are real but small and mostly non-monotonic.** Across the eight
encoder heads the induced swing in P(hit) over the full bias range was modest (≈ 0.05–
0.14, against a per-cell binomial SEM of ≈ 0.03). The clearest effect was **encoder
layer-1 head 0**, where enhancing its attention to the image raised detection from
≈ 0.48 (strong suppression) to ≈ 0.61 (strong enhancement) — a monotone ≈ 0.13 gain in
responsiveness, the single best "knob" we found. But most heads produced smaller,
**non-monotonic** changes that hover within a few SEM of baseline, and the heads do not
share a sign (enhancing some helps, others hurt). No single head is a decisive gate on
the stimulus.

**Jointly biasing all heads does not cleanly move detection — but it does move
uncertainty.** Biasing *every* encoder head's patch attention together left P(hit)
essentially flat and noisy across the bias range (≈ 0.50–0.60, no monotone trend) and
premature pressing at zero throughout — detection is robust to the manipulation. What
*does* change monotonically is the **critic's distributional uncertainty**: the quantile
entropy of the value-of-pressing rises steadily as patch attention is increased (≈ 0.30
at strong suppression → ≈ 0.55 at strong enhancement), and the policy entropy rises with
it (and the press-over-wait value advantage is least negative under strong suppression).
So the readable causal consequence of perturbing encoder attention is on the agent's
*uncertainty*, not on its *decision*.

**Interpretation.** This is the behavioural counterpart of the distributed encoder of
§3.2: because no single head (and not even the whole encoder's spatial allocation) is
the bottleneck through which stimulus evidence must pass — the evidence is carried
redundantly across heads and in the recurrent memory, and the *decision* is made by the
decoder's change-reading head — perturbing encoder attention is largely compensated and
fails to act as a clean responsiveness lever. This contrasts with simpler models that
have a single attentional gate, where the same intervention cleanly scales detection. It
is an honest negative result, and it is itself evidence for distributed coding;
§4.5 notes that the natural place to regain causal control is the decoder's
change-reading head, which §3.2 identifies as the true decision bottleneck.

![**Causal attention manipulation.** Left: P(hit) versus per-head patch-attention bias for each of the eight encoder heads (L1 blue, L2 red); dashed = baseline. Right: jointly biasing all heads leaves detection flat/noisy while the critic's distributional entropy and the policy entropy shift monotonically. Attention here is a soft lever on uncertainty, not a decisive lever on the decision. \label{fig:causal}](figs/exp4_perhead_behaviour.png)

### 3.5 The value function is calibrated, value-directed, and distorted by attention

**The critic is well-calibrated.** Regressing the critic's predicted state value
V(s) on the realised discounted Monte-Carlo return-to-go under the agent's own greedy
policy, pooled over 30,506 visited states, gives a near-identity calibration: slope
**0.908**, intercept 0.156, **R² = 0.611** (Fig. \ref{fig:value}, lower-left). The
value head is therefore not merely monotone but quantitatively close to the true
expected return.

**Values are value-directed.** Split by cue colour, the value time-courses are
cleanly ordered by reward at every point after the cue (Fig. \ref{fig:value},
upper-left). At the cue the agent already values the trial at roughly the reward on
offer (V ≈ 4.07 / 2.41 / 0.56 for red / green / blue, whose rewards are 5 / 3 / 1),
and as the rewarded change is detected the value rises to **≈ 5.0 / 3.0 / 0.9** — i.e.
the critic recovers the cue-colour reward almost exactly. No-change trials sit at a
flat intermediate value (≈ 2.4, the discounted correct-rejection payoff) and never
rise, so the critic also separates change from no-change. The **advantage of pressing
over waiting**, Q(press) − Q(wait), is negative before and at the change and crosses
zero only **1–2 frames after change onset** (and later for low-value blue than for
high-value red), exactly the dynamics required for a correct press: the value of
acting overtakes the value of waiting only once the change has been confirmed, and the
threshold to act is reached sooner when more reward is at stake — the value-level
substrate of the behavioural value-directed-attention effect (§3.1).

**Distributional uncertainty resolves around the decision.** The critic's quantile
spread, an outcome-uncertainty proxy, has a striking signal-dependent dynamic. For a
**suprathreshold** change the spread *collapses* as the change is detected (it falls
sharply from the cue to the change frame), i.e. detecting an obvious change **resolves**
value uncertainty. For a **near-threshold** change the opposite holds — the spread
*increases* after the change (quantile entropy ≈ 0.08 before versus ≈ 0.65 after) —
because when the change is barely visible the *outcome itself* (whether the agent will
correctly detect and press in time) is genuinely uncertain. The critic thus encodes
not just expected value but a calibrated, stimulus-dependent uncertainty about it.

**Attention shifts uncertainty more than value.** Re-running the value read-out under
an all-heads patch-attention bias at a *suprathreshold* change shows the value of
pressing is **robust** (V(press) ≈ 2.96–2.99 across the whole bias range): when the
stimulus is unambiguous the distributed encoder delivers the evidence regardless of how
its attention is nudged, and the value built on it barely moves. What *does* move
monotonically is **uncertainty** — both the critic's quantile entropy and the policy
entropy rise as patch attention is increased. The same pattern holds near threshold
(§3.4): detection and the premature-press rate are robust to the manipulation, while the
critic's quantile entropy shifts monotonically with the bias (and the press-over-wait
advantage is least negative under strong suppression). The value estimate is therefore
built on the encoder's distributed stimulus read but is **buffered** against
perturbation of any single attention channel — the value-side reflection of the
distributed-coding result of §3.4. Attention's most reliable causal handle on this
network is the agent's uncertainty, not its valuation or its choice.

![**The value function.** Upper-left: value time-courses by cue colour (change trials), ordered by reward and rising to the reward magnitude at the change (dashed); no-change trials flat. Upper-middle/right: press-over-wait advantage and critic quantile entropy. Lower-left: calibration of predicted V against realised Monte-Carlo return (near identity). Lower-right: value/entropy under an all-heads attention bias (suprathreshold; value robust, uncertainty shifts). \label{fig:value}](figs/exp5_value_timecourse.png)

![**Critic calibration and attention distortion.** Left: predicted V(s) versus realised discounted return-to-go (slope 0.91, R² 0.61, near the identity). Right: value and critic entropy under an all-heads patch-attention bias. \label{fig:calib}](figs/exp5_calibration_attn.png)

## 4. Discussion

### 4.1 A distributed encoder and a sharp decoder

The dominant theme across every analysis is a **division of labour between a
distributed sensory encoder and a sharp, decision-locked read-out**. The memory-as-
tokens encoder behaves as a near-uniform sensor: it spreads attention broadly over
the display, carries a transient top-down cue prior at cue onset, and never spatially
orients to the change. All of the sharp, change-locked spatial structure lives in the
*decoder's* final-layer CLS read-out, which snaps onto the changed location at change
onset and reaches near-total concentration there a few frames later. The recurrent
memory states, read linearly, contain the change's location, magnitude and timing as
soon as the change is visible — so the encoder is *representing* the change in its
content even while not *attending* to it spatially, and the decoder's job is to query
that content and convert it into a localised decision.

This architecture is worth contrasting with the intuitive picture of covert attention
as a single moving "spotlight" in the sensory representation. Here there is a
spotlight — the α-projection overlays show it clearly — but it sits at the *read-out*
stage, downstream of a sensory encoder that does not itself move a spotlight to the
change. The encoder's only spatial act is the brief, top-down cue prior. The model has
thus discovered a two-stage solution: a stable distributed sensory code plus a sharp
decision query, rather than a single attentional bottleneck that both senses and
decides.

### 4.2 Behavioural signatures without a behavioural bottleneck

Despite this non-canonical mechanism, the agent reproduces the textbook behavioural
signatures of attention. It shows a graded psychometric function and a decreasing
chronometric function; a spatial-cueing validity effect (better, faster detection for
validly cued changes); and value-directed attention (better, faster detection for
higher-reward cue colours). The mechanistic analyses locate the *source* of each:

- The **validity effect** is the behavioural residue of the encoder's transient cue
  prior and of the decoder's early cue-biased read-out. Because the decoder ultimately
  tracks the change bottom-up, invalid changes are still detected — just at a small
  cost in threshold and latency, exactly the signature seen in humans.
- **Value-directed attention** is grounded in the critic: state values are ordered by
  cue colour and scale with the reward on offer, and this value signal — available from
  the cue frame — biases the speed/accuracy trade-off toward faster, more confident
  pressing for high-value cues.

That a reward-trained network reproduces these effects "for free," and that we can
point to where each lives inside it, is the paper's main positive message for using
such models as testbeds for theories of attention.

### 4.3 Why causal attention manipulation is only partly effective

A simpler model with a single attentional gate can be made dramatically more or less
responsive by turning that gate up or down. Here, biasing the pre-softmax logits of a
single encoder head toward or away from the image produces only modest, head-dependent
behavioural shifts, and even biasing all heads jointly moves detection less than one
might expect. The reason is exactly the distributed encoder identified above: no single
head is the bottleneck through which stimulus evidence must pass, so perturbing one
head is largely compensated by the others and by the recurrent memory. The intervention
is not inert — some heads reliably raise or lower detection and shift value and
uncertainty in interpretable directions — but the lever is soft, not decisive. This is
an honest negative result with a mechanistic explanation, and it is itself evidence for
distributed coding: robustness to single-head perturbation is the flip side of the
encoder's diffuse, redundant read.

### 4.4 A calibrated, value-directed critic

The critic is the cleanest success. Its scalar value tracks the discounted Monte-Carlo
return almost on the identity line; its values are ordered red > green > blue at very
nearly the true reward magnitudes; it rises as a rewarded change approaches and
discriminates change from no-change trials; and its distributional spread behaves as an
uncertainty signal that resolves around the decision. Attention manipulations distort
value monotonically and sensibly — starving the encoder of stimulus evidence lowers the
value of acting and changes the policy's confidence — which both validates the value
read-out and demonstrates that the encoder's stimulus read is what the value is built
on.

### 4.5 Limitations and future directions

Several caveats bound these conclusions. (i) They characterise a *single* trained
network; replication across seeds and across the sibling architectures (e.g. the
FiLM-modulated encoder of the v4 variant, which gates attention rather than treating
memory as tokens) would establish which findings are architecture-general. (ii) Linear
decoding establishes *availability* of information, not that the network uses it in
that form. (iii) The causal manipulation is one specific intervention (an additive,
constant logit bias on patch keys); other interventions — temperature scaling,
head ablation, training-time attention shaping, or biasing the decoder rather than the
encoder — may have larger or qualitatively different effects, and biasing the decoder's
change-reading head is a natural next experiment given that that is where the spatial
selectivity lives. (iv) Time-courses were measured under a forced-wait policy to keep
trials full-length; under the acting policy the same computations unfold but truncate
at the press. (v) The task, though rich, is a controlled laboratory environment; the
generality of the encoder/decoder dissociation to naturalistic vision is open.

The most promising direction is to use the decoder's change-reading head as a causal
handle: because it is the genuine bottleneck for the press decision, manipulating *it*
(rather than the distributed encoder) should yield the clean responsiveness control
that the encoder manipulation did not — turning the present mechanistic map into a set
of testable causal predictions.

## 5. Conclusion

A recurrent vision transformer trained purely to maximise reward on a cued
change-detection task learns to behave like an attentive observer — graded detection,
faster and more accurate responses for validly cued and higher-value targets, and
appropriate withholding — while implementing that behaviour through a mechanism that is
mechanistically distinct from a single attentional spotlight in the sensory code. A
distributed memory-as-tokens encoder carries a transient top-down cue prior and a
diffuse sensory read; a sharp transformer-decoder read-out queries that code and locks
onto the changed location bottom-up to drive the press; and a well-calibrated,
value-directed distributional critic supplies the value signal that shapes the
speed/accuracy trade-off. The recurrent latents make the change's identity, location,
magnitude and timing linearly available; attention can be nudged but not switched,
reflecting the distributed code; and value tracks reward almost exactly and bends
predictably under attention manipulation. The result is a complete, figure-grounded
account of *where* — across four transformers, a recurrent memory, and a value head —
an RL-trained network puts the computations of spatial and value-directed attention.

## Appendix A — Architecture and training hyperparameters

| Component | Setting |
|---|---|
| Input | 50×50×3 RGB, 29 frames/trial |
| Patch embedding | 5×5 patches → 10×10 = 100 tokens; MLP 75→128→128 + LayerNorm; learned positional embedding |
| Model width *d* | 128 (d_model = d_mem, required by memory-as-tokens) |
| Encoder | 2 memory-as-tokens layers, 4 heads each; self-attention over 3·N = 300 tokens; per-layer shared LSTM memory; 1 inner iteration/frame; pre-norm, GELU |
| Decoders | actor + critic, each 2-layer transformer (4 heads), CLS read-out over 2·N = 200 memory tokens + learned positional embedding; 2-layer MLP head |
| Critic | distributional QR-DQN, 51 quantiles, action injected as additive input code; V via expected-SARSA (stop-grad on π) |
| Actor | 2 actions (wait/press); init logit bias [0, −1.5] |
| Parameters | ≈ 1.62 M |
| RL objective | PAC actor loss (MPO closed-form E-step + behaviour-cloning blend) + distributional QR-DQN critic |
| Stabilisers | target network (hard copy every 100 steps), critic burn-in (20 iters), prioritized episode replay (capacity 200, 4 replays/iter, α = 0.6, β = 0.4→1.0) |
| Optimisation | Adam, lr 3·10⁻⁴, 4 epochs/iter, grad-clip 0.5, γ = 0.99, entropy coef 0.01 |
| Environment | change time Tc ∈ [11, 25]; |Δθ| ≤ 64°; cue value red/green/blue = 5/3/1; ring reliability ∈ {0.25, 0.5, 0.75, 1.0} |

## Appendix B — Per-head attention taxonomy (encoder L1 and decoder L2)

Attention shares (fraction of the patch / CLS attention budget on the named quadrant)
at the cue frame (t = 1) and after change onset (t ≈ change + 3), pooled over trials,
for the valid cue-left condition (cue and change at S1 top-left). "Cue prior" = share
on the cued quadrant at the cue; "change read-out" = share on the changed quadrant
after the change. Heads not listed are near-uniform.

| Transformer · head | Role | Cue-frame share (cued quad) | Post-change share (changed quad) |
|---|---|---|---|
| Encoder L1 · head 0 | top-down cue orienter | ≈ 0.50 | uniform (≈ 0.25) |
| Encoder L1 · head 3 | top-down cue orienter | ≈ 0.49 | uniform (≈ 0.25) |
| Encoder L1 · heads 1,2 | diffuse sensory read | ≈ 0.26 | uniform |
| Encoder L2 · all heads | diffuse / memory read | ≈ uniform | uniform |
| Actor decoder L2 · head 2 | bottom-up change locator | ≈ 0.40 (weak prior) | ≈ 1.00 |
| Actor decoder L2 · head 1 | change locator | ≈ 0.40 | ≈ 0.95 |
| Critic decoder L2 · head 3 | value-of-press change locator | ≈ 0.31 | ≈ 0.74–0.93 |
| Critic decoder L2 · head 1 | value-of-press change locator | ≈ 0.47 | ≈ 0.62–0.77 |

On invalid trials (cue at S1, change at S4) the encoder cue-prior heads keep their
share on S1 while the decoder change-reading heads move their post-change share onto
S4 (≈ 0.99), confirming the dissociation.

## Appendix C — Analysis settings

All analyses use the converged model and the faithful attention re-implementation
(verified to match the trained forward to < 10⁻⁷). Behavioural cells use 300 trials
each unless noted; the latent-decoding bank uses 2000 fully-randomised forced-wait
trials with 5-fold cross-validated linear decoders and label-shuffled controls;
the causal sweep uses 256 matched-seed trials per bias level at a near-threshold
|Δθ| = 10°; value time-courses use forced-wait rollouts (400 trials/cell) and
calibration uses 1200 greedy-policy trials. Large-batch rollouts are processed in
trial-chunks of 400 to bound memory; chunking is verified to reproduce the single-batch
result exactly.

---

*Figures referenced in the text are generated by the analysis scripts
(`exp1`–`exp5`, `exp2_attention_alpha`, and the task/architecture/dissociation
figure builders) and accompany this report.*

## References

Abdolmaleki, A., Springenberg, J. T., Tassa, Y., Munos, R., Heess, N., & Riedmiller, M.
(2018). Maximum a Posteriori Policy Optimisation. *International Conference on Learning
Representations (ICLR)*.

Anderson, B. A., Laurent, P. A., & Yantis, S. (2011). Value-driven attentional capture.
*Proceedings of the National Academy of Sciences*, 108(25), 10367–10371.

Dabney, W., Rowland, M., Bellemare, M. G., & Munos, R. (2018). Distributional
Reinforcement Learning with Quantile Regression. *AAAI Conference on Artificial
Intelligence*.

Dosovitskiy, A., Beyer, L., Kolesnikov, A., Weissenborn, D., Zhai, X., Unterthiner, T.,
et al. (2021). An Image is Worth 16×16 Words: Transformers for Image Recognition at
Scale. *International Conference on Learning Representations (ICLR)*.

Posner, M. I. (1980). Orienting of attention. *Quarterly Journal of Experimental
Psychology*, 32(1), 3–25.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser,
Ł., & Polosukhin, I. (2017). Attention Is All You Need. *Advances in Neural Information
Processing Systems (NeurIPS)*.
