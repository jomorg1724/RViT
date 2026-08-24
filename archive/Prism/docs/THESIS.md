# PRISM: A Predictive-Coding Convolutional Architecture for Cued Visual Change Detection

**Author:** Jonathan Morgan
**Date:** 2026-04-30
**Status:** Manuscript draft — Introduction and Methods complete; Results templated; Discussion and Conclusion pending experimental completion.

---

## Abstract

We introduce PRISM (Predictive Recurrent Inference via Self-Modulation), a small, all-convolutional, recurrent neural architecture for visual working memory and cued change detection. PRISM is grounded in three principles drawn from cortical neuroscience: a topographically organized convolutional hierarchy with no dense long-range projections, mnemonic feedback that modulates perception via top-down generative predictions and multiplicative gain, and a derived attention readout that arises naturally as the prediction error of the model's own generative model. The architecture's only auxiliary objective is the variational free-energy / predictive-coding error, which is universal across temporal sensory environments and free of task-specific information. We train PRISM end-to-end on a Posner-style cued change-detection task using a recurrent proximal-policy-optimization scheme augmented with a self-supervised generative-modeling pretrain phase. Behavioral and representational results are presented in Section 4 (pending) and contextualized against parallel measurements from primate visual cortex and human psychophysics.

---

## 1. Introduction

### 1.1 Detecting change against a noisy background

Visual change detection is among the most fundamental cognitive tasks. Animals must continuously monitor their visual surround for behaviorally relevant transitions — a movement at the periphery, a shift in orientation of a tracked object, the appearance of a salient feature — while suppressing incessant per-frame sensory noise from saccadic jitter, retinal nonstationarities, and photoreceptor variability. The primate brain solves this problem with a specialized cascade of visual, parietal, and frontal areas whose architecture has been mapped in considerable detail (Felleman & Van Essen, 1991; Bisley & Goldberg, 2010). At the behavioral level, the cued change-detection paradigm — a variant of the Posner cueing task (Posner, 1980) — has long served as the standard probe of how endogenous attention and working memory cooperate to support this monitoring function.

The cued change-detection paradigm presents the observer with a brief cue stimulus that probabilistically indicates the location at which a subsequent change is most likely to occur. The observer must maintain the cue's identity and location across a delay period during which a noisy multi-element display is shown, and must produce a response when, and only when, a target change occurs. Performance on this task is determined by a tightly coupled set of cognitive subprocesses: visual encoding of the cue, sustained working-memory maintenance of cue-relevant features across the delay, top-down attentional gain at the cued location, evidence accumulation across noisy stimulus frames, and a decision rule for action initiation. Each of these subprocesses has been the target of substantial neurophysiological and behavioral investigation, and a useful computational model of the task should make falsifiable claims about all of them.

A useful computational model should not merely reproduce average behavioral accuracy. It should predict the full psychometric curve of detection accuracy as a function of orientation-change magnitude, exhibit the validity-effect speedup of reaction times at cued locations, and (perhaps most importantly) make falsifiable claims about the internal representations and cortical signals that support these behaviors. The present work introduces PRISM, a compact convolutional-recurrent neural architecture that aspires to this standard.

### 1.2 Lessons and limits of the classical attentional spotlight

The most influential computational metaphor for visual attention has been Posner's "spotlight" — a movable beam of enhanced processing that the observer voluntarily directs at a single location (Posner, 1980; Treisman & Gelade, 1980). The spotlight metaphor inspired generations of attention models in cognitive psychology and, more recently, in machine learning, including the recurrent-models-of-visual-attention line that uses REINFORCE to learn discrete glimpse locations (Mnih et al., 2014; Ba et al., 2015).

Careful psychophysical and neurophysiological investigation has progressively undermined the spotlight account in its strongest form. Carrasco (2011) reviews two and a half decades of evidence indicating that covert spatial attention does not behave like a winner-take-all gate but rather as a graded multiplicative gain modulation distributed across the visual field. Reynolds and Heeger (2009) formalized this as the normalization model of attention, in which top-down signals adjust the parameters of a per-neuron divisive-normalization circuit, producing a continuous, per-channel, per-location modulation rather than a discrete pointer. Itti and Koch (2001) earlier developed the influential saliency-map view, in which what is conventionally called attention is the readout of a feature-based novelty signal that is itself computed in a distributed manner across visual cortex.

This reorientation has significant implications for computational modeling. If covert attention is not a softmax-over-locations pointer but a distributed gain field, then any architecture that reifies attention as a learned spatial-softmax primitive is committing to a discredited theoretical claim. PRISM accordingly contains no softmax-over-locations operation anywhere in its computational graph. The interpretable attention map that the architecture exposes is instead a derived quantity — the per-location magnitude of the model's own prediction error against its top-down generative model — which we argue is closer in spirit both to the modern saliency literature and to the predictive-coding account of cortical attention.

### 1.3 Predictive coding and the free-energy principle

The predictive-coding framework, introduced by Rao and Ballard (1999) and elaborated by Friston (2010) into the broader free-energy principle, posits that the cortical hierarchy implements a generative model of sensory input. Higher levels send top-down predictions to lower levels via descending feedback projections; lower levels send back the residual prediction errors. Perception, in this view, is the recurrent computation that minimizes prediction error along the entire hierarchy — equivalently, that minimizes a variational free-energy functional under a generative-model assumption.

The predictive-coding view supplies an elegant resolution to two otherwise puzzling features of cortical anatomy. The predominance of feedback projections — at every level of the visual hierarchy, descending fibers outnumber ascending fibers, often by an order of magnitude (Felleman & Van Essen, 1991) — finds a natural explanation as the substrate for top-down predictions, which would otherwise have no obvious computational role. And the persistent recurrent activity observed in prefrontal cortex during working-memory delays (Goldman-Rakic, 1995; Constantinidis et al., 2018) can be reinterpreted not as passive storage but as the iterative settling of a posterior estimate under a generative model — precisely the operation that Friston's variational interpretation of free-energy minimization predicts.

This view has direct architectural consequences for any model intent on biological plausibility. The architecture must contain a feedforward encoder that maps observations to features; a top-down generative decoder that predicts features (or raw observations) from internal state; a residual-error pathway that signals where predictions fail; and a recurrent state-update mechanism that incorporates error information into the model's posterior. PRISM realizes each of these requirements explicitly, and the dominant auxiliary objective during training is the variational free-energy accuracy term — under a Gaussian likelihood assumption, simply the squared prediction error against a learned generative model.

### 1.4 The bitter lesson and the discipline of generic objectives

A second motivation for restricting PRISM's auxiliary loss to the predictive-coding term is methodological. Sutton's "Bitter Lesson" (Sutton, 2019) argues that the most enduring progress in artificial intelligence has come from objectives and architectures that scale with data and compute rather than from objectives that encode hand-crafted task knowledge. A model that achieves high performance on a particular benchmark by virtue of bespoke per-task auxiliary supervision — a probe predicting cue color from memory, a regularizer that pushes attention onto the cued location at the cue frame — has not solved a more general problem; it has annotated the benchmark.

PRISM is designed to comply with this discipline. The single auxiliary objective, minimization of variational free energy / predictive coding error, is universal across any temporal sensory environment with a generative-model interpretation. Replacing the change-detection task with moving MNIST, Atari, or any other partially observable visual control problem requires no surgery to the loss function. We argue that this is the right standard against which to judge a candidate cortical architecture: not whether it can be tuned to fit a particular task with bespoke supervision, but whether the same general objective produces task-relevant representations across a broad family of environments.

### 1.5 Contributions

Within this framing, the present work makes the following contributions. We develop PRISM, a small (~250K-parameter) all-convolutional recurrent architecture that combines a topographic feedforward feature hierarchy, top-down feature-wise linear modulation from working memory to perception, an explicit generative decoder that produces a derived prediction-error saliency map, an error-gated convolutional gated recurrent unit for memory binding, and a $K$-iteration inner loop of variational inference per environment step. We frame the entire system within the free-energy principle and use only its accuracy term as the auxiliary objective during reinforcement-learning training. We deploy PRISM on a Posner-style cued change-detection task and present a battery of analyses bridging machine-learning evaluation (psychometric and chronometric curves, ablation studies) and neuroscience-style probes (causal manipulation of the saliency map, decoding of cue features from working-memory state, comparison of internal-state dynamics to known properties of primate prefrontal and parietal cortex). Results are reported in Section 4 (pending experimental completion); the present manuscript focuses on the architectural and mathematical specification and the analytical framework within which the results will be interpreted.

---

## 2. Methods

### 2.1 The cued change-detection task

The task environment is a variant of the Posner cueing paradigm with reward-modulated cue colors. Each trial spans $T = 30$ discrete environmental steps with display structure as follows. Steps $t = 0$ and $t = 2$ display a uniform black field. Step $t = 1$ displays a single cue stimulus consisting of a colored disc — red, green, or blue, with reward magnitudes $\rho \in 5, 3, 1$ respectively — surrounded by a partial annular ring whose subtended angle indicates the cue validity proportion $p \in 1.0, 0.75, 0.5, 0.25$. The cue is positioned in either the top-left or the bottom-right quadrant of the $50 \times 50$-pixel field. From step $t = 3$ onward the display contains four spatially separated Gabor patches, one in each quadrant, with independent random baseline orientations $\phi_q \in [0°, 360°)$. Per-frame independent Gaussian orientation noise of standard deviation $\sigma_\text{noise} = 10°$ is added to each Gabor at every step.

With probability $\frac{1}{2}$ the trial contains a target change. The change time $t^\star$ is drawn uniformly from $11, 12, \ldots, 25$, the change magnitude $\Delta\phi$ is drawn uniformly from $[-\theta, \theta]$ with $\theta = 65°$ at the start of curriculum, and the changed patch is determined by the cue: with probability $p$ the changed patch is the cued one, and with probability $1 - p$ it is one of the three uncued patches selected uniformly. The agent observes RGB frames and emits one of two actions per step: "wait" (action 0) or "report change" (action 1). Reporting prior to $t^\star$ produces zero reward and terminates the trial as a false alarm. Reporting at $t \ge t^\star$ when a change has occurred yields the cue-color-determined reward $\rho$ as a correct hit. Failing to report by step $T$ when no change occurred yields the same color-determined reward as a correct rejection; failing to report when a change occurred yields zero as a miss.

This task structure jointly probes cue encoding into working memory at $t = 1$, maintenance of the cue's identity and location across the variable delay until $t^\star$, sustained vigilance over four spatial locations under per-frame orientation noise, detection of a small orientation change against the noise, and an action policy that balances false-alarm and miss costs against the reward gradient set by cue color. An oracle policy with full state access achieves expected return $\approx 2.98$ per trial against a theoretical maximum of $3.0$, the residual gap arising from a small fraction of trials with $|\Delta\phi| < 5°$ that are below the per-frame orientation-noise floor. A policy that always selects "wait" achieves $1.47$ from correct rejections alone, which constitutes the trivial floor against which any learned policy must improve.

### 2.2 Architecture overview

PRISM processes the observation stream one step at a time, maintaining a single recurrent state $M_t \in \mathbb{R}^{B \times C_M \times H \times W}$ across timesteps, with $C_M = 32$ and $H = W = 12$ in the default configuration. At each step the system performs the following operations in sequence. The current frame $x_t \in \mathbb{R}^{B \times 3 \times 50 \times 50}$ is encoded by a feedforward convolutional V1 stem to a feature volume $V_t \in \mathbb{R}^{B \times C_V \times 12 \times 12}$ with $C_V = 64$. Top-down FiLM modulation from $M_{t-1}$ produces a modulated perceptual code $P_t$ of the same shape. Two top-down generative predictions are produced from $M_{t-1}$: a pixel-space prediction $\hat x_t = \tilde g(M_{t-1})$ used for the dominant predictive-coding objective, and a feature-space prediction $\hat V_t = g(M_{t-1})$ used internally by the working-memory update. The pixel-space prediction error $x_t - \hat x_t$, downsampled to the feature grid resolution, defines the saliency map $S_t \in \mathbb{R}^{B \times 1 \times 12 \times 12}$ — the architecture's interpretable attention readout. The convolutional gated recurrent unit then updates $M$ to $M_t$ using $P_t$, the feature-space error $E_t = V_t - \hat V_t$, and the saliency-amplified update gate. An inner $K$-iteration loop refines $M_t$ via gradient descent on the variational free-energy functional. A multi-pool decision readout collapses $M_t$ and $S_t$ into a small state vector $s_t$ that is consumed by separate actor and critic heads.

The remainder of this Methods section specifies each component in detail, with particular attention to the mapping between architectural choices and their neuroscientific motivation. The default hyperparameters used in the present experiments are summarized in Table 1.

### 2.3 V1 stem: bottom-up feature extraction

The V1 stem is a three-layer convolutional encoder with strides $(2, 2, 1)$, kernel sizes $(5, 3, 3)$, and channel counts $(C_V/2, C_V, C_V)$, producing $V_t \in \mathbb{R}^{B \times C_V \times 12 \times 12}$ from the $50 \times 50$ RGB input. The first layer has receptive field comparable to the spatial period of the Gabor stimuli, in deliberate analogy to the orientation-selective simple cells of primary visual cortex (Hubel & Wiesel, 1962; De Valois & De Valois, 1988). The second and third layers progressively abstract spatial features in the manner of V2 and V4. Each convolutional layer is followed by GroupNorm (Wu & He, 2018) and a GELU nonlinearity. We use GroupNorm rather than BatchNorm because the recurrent rollouts process episodes in lockstep with very small effective batches per timestep, making BatchNorm statistics unreliable; this is a standard choice for recurrent vision architectures.

The mapping from the four 25×25-pixel Gabor patches to a 6×6 sub-region each in the 12×12 feature grid is not enforced explicitly. The network discovers any topographic organization that benefits the predictive-coding objective. This is again in deliberate analogy to cortex, where the retinotopic organization of V1, V2, and V4 emerges through development rather than being hard-coded; we make no architectural commitment to a particular grid-to-quadrant mapping.

### 2.4 FiLM modulation: top-down gain pathway

Following Perez et al. (2018), top-down modulation from working memory to perception is implemented via Feature-wise Linear Modulation. Two $1 \times 1$ convolutional layers map $M_{t-1}$ to per-location, per-channel multiplicative and additive modulation parameters,

$$
\gamma_t = \mathrm{Conv}*{1 \times 1}^{C_M \to C_V}(M*{t-1}), \qquad \beta_t = \mathrm{Conv}*{1 \times 1}^{C_M \to C_V}(M*{t-1}),
$$

which are applied elementwise to the bottom-up features:

$$
P_t = \gamma_t \odot V_t + \beta_t.
$$

The use of $1 \times 1$ kernels enforces a topographic mapping: location $(i, j)$ in memory modulates location $(i, j)$ in perception, with no spatial cross-talk. This implements precisely the form of attentional modulation described by the normalization model of attention (Reynolds & Heeger, 2009), in which top-down signals adjust the gain of cortical neurons via per-location, per-channel multiplicative scaling and additive offset. We initialize $\gamma$-bias to $1$ and $\beta$-bias to $0$ with small-Gaussian conv weights, so that FiLM is the identity at random initialization and the network must earn its modulation through training. The biological correlate of FiLM is the rich set of feedback projections from prefrontal and parietal cortex to V1–V4, which gain-modulate the firing rates of visual neurons in a manner that depends on top-down task and memory state (Reynolds & Chelazzi, 2004; Maunsell, 2015).

### 2.5 Top-down generative decoders

Two top-down decoders produce predictions of the current sensory state from the previous memory state. The pixel decoder $\tilde g$ is a small upsampling network of approximately seven thousand parameters: a $3 \times 3$ convolution from $C_M$ to a small hidden dimension, a bilinear interpolation to the input resolution, a second $3 \times 3$ convolution, and a final $3 \times 3$ projection to the pixel channels. Its output $\hat x_t = \tilde g(M_{t-1}) \in \mathbb{R}^{B \times 3 \times 50 \times 50}$ is the principal target of the predictive-coding objective. The feature decoder $g$ is structurally similar but maps $M_{t-1}$ directly to feature-space predictions $\hat V_t = g(M_{t-1}) \in \mathbb{R}^{B \times C_V \times 12 \times 12}$ at the same spatial resolution as the V1 stem output. Both decoders are zero-initialized at the output layer, so $\hat x_0$ and $\hat V_0$ are approximately zero at the start of training, and the prediction error $E_0$ approximately equals the bottom-up code $V_0$ — the network begins maximally surprised by everything, which is the appropriate initial condition for a generative model under construction.

These decoders implement the descending-feedback pathway of the predictive-coding hierarchy. Their existence and their explicit role as generators of testable predictions, rather than as black-box transformations, is what makes PRISM a predictive-coding model in the sense of Rao and Ballard (1999), and not merely a model with feedback connections. The biological correlate of these decoders is the population of feedback-projecting cortical neurons that send top-down predictions from higher to lower visual areas; their failure to suppress lower-level activity reveals where the cortical generative model is wrong, which is the substrate of the prediction error coded in superficial-layer pyramidal neurons (Bastos et al., 2012).

### 2.6 The prediction-error map as a derived saliency signal

The prediction-error map is the conceptual core of PRISM's attention mechanism. Given the bottom-up frame $x_t$ and the top-down prediction $\hat x_t$, the per-location prediction-error magnitude is

$$
S_t(i, j) = \sqrt{\frac{1}{C_x} \sum_{c} \left(x_{t,c,i,j} - \hat x_{t,c,i,j}\right)^2 + \epsilon},
$$

pooled to the feature-grid resolution by adaptive average pooling. This map is non-negative, vanishes only where prediction matches observation, and has no learnable parameters of its own — it is a strictly derived quantity. Crucially, $S_t$ functions throughout PRISM exactly where a learned attention map would function in a more conventional architecture: it gates the working-memory update (Section 2.7) and weights the pooling that produces the decision readout (Section 2.9). The architecture uses prediction error in place of a softmax pointer.

This identification of attention with prediction error has direct neuroscientific support. Itti and Koch (2001) show that bottom-up saliency, the principal driver of involuntary attention, is well modeled as a per-location feature-anomaly signal — precisely a prediction-error magnitude relative to an implicit local feature distribution. Spratling (2008) demonstrates that the standard biased-competition account of attention can be reformulated as predictive coding, with the competition arising naturally from the gain modulation that prediction-error minimization induces. Friston (2010) argues that attention, in the sense of the precision-weighting of sensory channels, is intrinsic to the variational free-energy framework: high-precision channels are exactly those where the generative model expects to see substantial prediction error and is willing to integrate it strongly. PRISM operationalizes this last point by amplifying the working-memory update gate at locations of high prediction error.

### 2.7 Error-gated convolutional GRU memory

The recurrent state $M_t \in \mathbb{R}^{B \times C_M \times H \times W}$ is updated by a convolutional gated recurrent unit (Ballas et al., 2016) whose update gate is amplified by the per-location prediction-error magnitude. The standard ConvGRU equations,

$$
r_t = \sigma\left(W_r \star [M_{t-1}, P_t]\right), \qquad \tilde C_t = \tanh\left(W_c \star [r_t \odot M_{t-1}, P_t, E_t]\right), \qquad u_t^\text{base} = \sigma\left(W_u \star [M_{t-1}, P_t]\right),
$$

are augmented with a saliency-modulated update gate

$$
u_t = \min\left(u_t^\text{base} \odot (1 + \lambda \bar S_t), 1\right),
$$

where $\bar S_t$ is the per-batch-normalized saliency map and $\lambda \ge 0$ is a learned scalar parameterized as $\mathrm{softplus}$. The memory update is then a convex combination

$$
M_t = (1 - u_t) \odot M_{t-1} + u_t \odot \tilde C_t.
$$

This implements the principle "write to memory more strongly where predictions failed" — the discrete-time analogue of saying that the gradient of variational free energy with respect to $M$ is concentrated at locations of high prediction error. The form is a direct convolutional generalization of the standard gated recurrent unit with a saliency-modulated gate, retaining the topographic structure of $M$ throughout.

The biological correlate is the conjunction of two known properties of cortical and hippocampal memory circuits. First, working-memory traces in dorsolateral prefrontal cortex are spatially organized: stimulus-selective persistent activity is observed in cells whose receptive fields overlap the encoded location (Funahashi et al., 1989; Goldman-Rakic, 1995). Second, novelty (the hippocampal correlate of prediction error) gates encoding into long-term memory via dopaminergic modulation (Lisman & Grace, 2005). The error-gated update implements a compressed analogue of both phenomena: writes are spatially structured and amplified by surprise.

### 2.8 Inner variational-inference loop

Following the working-memory compute-depth hypothesis (Morgan, 2026), the GRU update is followed by $K$ iterations of a learned inner refinement step. At each iteration the decoder is re-evaluated on the current memory iterate, the new prediction error is computed, and an update direction is produced by a small two-layer convolutional block:

$$
\hat V_t^{(k)} = g\left(M_t^{(k)}\right), \qquad E_t^{(k)} = V_t - \hat V_t^{(k)}, \qquad M_t^{(k+1)} = M_t^{(k)} + \epsilon\mathrm{ErrBlock}\left(E_t^{(k)}, M_t^{(k)}\right).
$$

The interpretation is precise: each iteration is one step of gradient descent on the variational free-energy functional with respect to $M$, with $\epsilon$ as the step size. Under standard smoothness assumptions on the decoder, the Banach contraction theorem gives geometric convergence of $M_t^{(k)}$ to the variational fixed point $M^\star$ within a basin around the true posterior mode.

This recasts the prior compute-depth hypothesis in the language of variational inference. The previously informal claim that working memory must do iterative work becomes the precise claim that working memory implements iterative free-energy minimization with respect to its own posterior, a computation that single-step recurrent updates cannot in general implement to sufficient accuracy. Persistent prefrontal activity during working-memory delays (Constantinidis et al., 2018) acquires a corresponding mechanistic interpretation as the time course of this iterative settling. The default $K = 2$ in the current experiments. The inner block carries approximately nine thousand parameters and is weight-tied across iterations, so the per-step compute cost scales linearly in $K$ with no parameter overhead. Section 4 reports a $K$-sweep that tests the prediction that performance and run-to-run variance both improve with iteration depth.

### 2.9 Decision readout

The actor and critic networks consume a low-dimensional summary of the recurrent state. We compute three pooling operations on a four-channel evidence projection $d_t = \mathrm{Conv}_{1 \times 1}^{C_M \to 4}(M_t)$. The global average pool $g_t = \mathrm{GAP}(d_t) \in \mathbb{R}^{B \times 4}$ summarizes overall memory state. The saliency-weighted global pool

$$
e_t = \frac{\sum_{i,j} S_t(i,j)d_t(i,j)}{\sum_{i,j} S_t(i,j) + \epsilon} \in \mathbb{R}^{B \times 4}
$$

captures memory state at locations of high prediction error. A coarse-grid pool aggregates the saliency-weighted evidence at $G \times G = 2 \times 2$ cells

$$
c_t = \frac{\mathrm{AdaptivePool}*{2 \times 2}(S_t \odot d_t)}{\mathrm{AdaptivePool}*{2 \times 2}(S_t) + \epsilon} \in \mathbb{R}^{B \times 4 \times 2 \times 2},
$$

providing per-quadrant saliency-weighted features so the actor can localize where surprise is concentrated. Concatenated, these yield a 24-dimensional state vector $s_t$ consumed by the heads.

This is the only place in PRISM where a non-convolutional reduction across the spatial axis occurs. The reduction uses no learned spatial weights of its own — both the saliency map and the coarse-grid pool are derived signals — which makes the decision readout a thin biologically defensible interface to the action-selecting circuit. Cortical decision areas including the lateral intraparietal area, the frontal eye field, and parietal area 5 compute global summaries by integrating over spatially organized inputs; the present readout uses prediction-error-weighted integration as the principal pooling rule, in analogy to the well-documented saliency-weighted integration observed in lateral intraparietal cortex (Bisley & Goldberg, 2010).

### 2.10 Actor-critic heads and reinforcement-learning training

Two two-layer multilayer perceptrons map $s_t$ to action logits and a scalar value estimate, respectively. The actor outputs $n_a = 2$ logits parameterizing a categorical distribution over actions; the critic produces a single scalar $V(s_t)$ used as the baseline for advantage estimation. We initialize the actor's output bias to $[0, -4]$ so that the initial probability of the change-reporting action is $\sigma(-4) \approx 0.018$ — a conservative prior that ensures episodes survive long enough for the perceptual and memory machinery to receive useful learning signal. This is a generic init choice analogous to the +1 forget-gate-bias trick for LSTMs (Jozefowicz et al., 2015), and it is essential here because the task terminates the trial whenever the agent reports change, so a uniform initial policy would yield identically zero return: nearly every episode would be a one-step false alarm.

The agent is trained with recurrent proximal policy optimization (Schulman et al., 2017; Pleines et al., 2022) with truncated backpropagation through time at $T_\text{bptt} = 16$ steps. Generalized advantage estimation (Schulman et al., 2016) with $\gamma = 0.95$ and $\lambda = 0.95$ produces the advantage signal. The policy loss is the standard PPO clipped surrogate, the value loss is a mean squared error against bootstrapped returns, and an entropy bonus with coefficient $0.005$ provides a small exploration pressure. Adam (Kingma & Ba, 2015) is used with learning rate $3 \times 10^{-4}$ and gradient norm clipping at $0.5$.

### 2.11 The variational free-energy objective

The auxiliary objective minimized jointly with the policy and value losses is the variational free-energy accuracy term. Under a Gaussian likelihood $p(V_t | M_t) = \mathcal{N}(V_t; g(M_t), \sigma^2 I)$ with point-estimate posterior, variational free energy reduces to the squared prediction error scaled by a constant. We use three contributions. The forward pixel term $x_t - \tilde g(M_{t-1})^2$ provides the principal generative-model target and supplies the saliency signal. The autoencoding term $x_t - \tilde g(M_t)^2$ provides a complementary signal that is trivially trainable from random initialization, because the encoded state $M_t$ depends on $x_t$ by construction, so the decoder can always extract some information from it. This second term breaks the cold-start zero-attractor that would otherwise trap a pure-forward predictive model in a constant-output local optimum: in early training the forward decoder, given an uninformative initial memory, has its optimal output at zero, which yields zero gradient and prevents the encoder–decoder pair from ever escaping the constant-prediction equilibrium. The autoencoding term sidesteps this pathology because its decoder always has nonzero gradient with respect to its input. The feature term $V_t - g(M_{t-1})^2$ provides explicit gradient to the feature decoder used by the inner variational-inference loop. With default coefficients $(\alpha_\text{fwd}, \alpha_\text{auto}, \alpha_\text{feat}) = (1.0, 1.0, 0.1)$ the total auxiliary loss is

$$
\mathcal{L}*\text{PC} = \alpha*\text{fwd}\bigx_t - \tilde g(M_{t-1})\big^2 + \alpha_\text{auto}\bigx_t - \tilde g(M_t)\big^2 + \alpha_\text{feat}\bigV_t - g(M_{t-1})\big^2.
$$

Combined with the PPO loss, the full training objective is

$$
\mathcal{L} = \mathcal{L}*\text{PPO} + c_v\mathcal{L}*\text{value} - c_H \mathcal{L}*\text{entropy} + c*\text{PC}\mathcal{L}_\text{PC},
$$

with $c_v = 0.5$, $c_H = 0.005$, and $c_\text{PC} = 1.0$.

The bitter-lesson audit (Section 1.4) is exhausted by this single formula: $\mathcal{L}*\text{PC}$ depends only on $(x_t, M_t, M*{t-1})$ and the model's own learned predictions, with no reference to the cue, the change-detection task, the reward palette, or any other environment-specific quantity. The same loss is appropriate for any temporal sensory environment with a Gaussian-likelihood generative model.

### 2.12 Training procedure

The full training procedure has three stages. A predictive-coding pretrain phase of $N_\text{pretrain} = 2000$ iterations forces the agent's action to "wait" at every step, so all episodes complete in full and the predictive-coding losses receive uniform support across the trial timeline. During this phase, only $\mathcal{L}*\text{PC}$ contributes to the loss; the policy and value losses are zero. The purpose is to bring the perceptual encoder, decoders, and recurrent memory to a non-trivial joint optimum before reinforcement-learning chaos perturbs them. An inner-loop warmup phase of $N*\text{K-warmup} = 5000$ iterations forces the inner-loop iteration count $K$ to zero, so memory updates depend only on the GRU and not on iterated free-energy descent through partially trained decoders. This avoids amplifying decoder noise during early learning. After both warmups complete, the system trains end-to-end with the full PPO + PC objective.

Hyperparameters are summarized in Table 1. Training runs on a single laptop-class machine at approximately one episode per second for the default model size. The total parameter count is approximately 250,000, distributed across the V1 stem (≈58K), the FiLM modulation (≈4K), the feature decoder (≈28K), the pixel decoder (≈7K), the GRU (≈100K), the inner ErrBlock (≈37K), and the readout-actor-critic stack (≈13K).

#### Table 1. Default hyperparameters.


| Component  | Parameter                                                   | Value              |
| ---------- | ----------------------------------------------------------- | ------------------ |
| V1 stem    | feature channels $C_V$                                      | 64                 |
| Memory     | channels $C_M$                                              | 32                 |
| Memory     | spatial size $H \times W$                                   | 12 × 12            |
| Decoders   | pixel-decoder hidden                                        | 16                 |
| Inner loop | iterations $K$                                              | 2                  |
| Inner loop | step size $\epsilon$                                        | 0.1                |
| Decision   | evidence channels                                           | 8                  |
| Decision   | coarse grid $G$                                             | 2                  |
| Heads      | actor / critic hidden                                       | 128                |
| Init       | actor logit bias                                            | $[0.0, -4.0]$      |
| PC loss    | $\alpha_\text{fwd}, \alpha_\text{auto}, \alpha_\text{feat}$ | $(1.0, 1.0, 0.1)$  |
| PPO        | learning rate                                               | $3 \times 10^{-4}$ |
| PPO        | clip range                                                  | 0.2                |
| PPO        | epochs per update                                           | 4                  |
| PPO        | $\gamma, \lambda_\text{GAE}$                                | 0.95, 0.95         |
| PPO        | entropy coefficient                                         | 0.005              |
| PPO        | value coefficient                                           | 0.5                |
| PPO        | gradient clip                                               | 0.5                |
| BPTT       | truncation length                                           | 16                 |
| Schedule   | PC pretrain iterations                                      | 2,000              |
| Schedule   | inner-K warmup iterations                                   | 5,000              |
| Run        | episodes per iteration                                      | 8                  |


---

## 3. Results

Results are organized into eight analyses, each combining a standard machine-learning evaluation with a complementary neuroscience-style probe. Quantitative values are pending experimental completion; the present subsections specify the analytical framework and prior expectations against which the results will be interpreted.

### 3.1 Learning dynamics and sample efficiency

We will report rolling-window mean reward and trial-correctness over the course of training as a function of episode count. The expected curve passes through the never-press baseline (mean return 1.47) by the end of the predictive-coding pretrain phase, climbs through it during the early reinforcement-learning phase, and approaches the oracle ceiling near 2.98 at convergence. We will additionally report the per-component loss curves — forward PC, autoencoding PC, feature PC, policy, value, entropy — to confirm that the cold-start bootstrapping problem identified in Section 2.11 is resolved by the autoencoding term: specifically, that the forward-PC term decreases below the constant-prediction floor of approximately $0.025$ as the autoencoding term provides initial gradient to the decoder.

We will report, in particular, the time-course of the rolling reaction-correctness rate as it rises through the never-press floor (which represents pure correct-rejection performance) and into the regime where the agent is also producing correct hits. The crossover from "always wait" to "wait and detect" is the principal qualitative learning event, and its timing relative to the PC pretrain phase, the inner-K warmup phase, and the first PPO update will be diagnostic of which architectural component most rate-limits the learning.

### 3.2 Psychometric analysis

For each trained model we will evaluate detection performance on a held-out battery of trials spanning the full range of orientation-change magnitudes $|\Delta\phi|$, cue validity $p$, and cue color. We will plot psychometric curves of correct-detection probability against $|\Delta\phi|$ for each cue-validity condition, and compare to the standard signal-detection model

$$
P(\text{hit} \mid |\Delta\phi|, p) = \Phi\left(\frac{|\Delta\phi|}{\sigma_\text{eff}(p)}\right),
$$

where $\sigma_\text{eff}(p)$ is a fitted per-condition effective noise. The expectation, derived from the psychophysics literature on cued detection (Carrasco, 2011; Posner, 1980), is that $\sigma_\text{eff}$ decreases monotonically with $p$ (the validity effect) and that the slope of $\sigma_\text{eff}$ versus $p$ provides a quantitative comparison point against published human data on attentional facilitation. We will additionally report the false-alarm rate as a function of cue color, anticipating that the reward gradient $\rho \in 1, 3, 5$ shifts the model's decision threshold in the direction predicted by signal-detection theory: more conservative reporting on low-reward (blue) trials, more liberal on high-reward (red) trials.

### 3.3 Chronometric analysis

We will extract per-trial reaction time as the number of frames between the change onset $t^\star$ and the agent's report. We will plot reaction-time distributions stratified by cue validity and change magnitude, and fit the standard drift-diffusion model (Ratcliff, 1978; Gold & Shadlen, 2007) with parameters drift rate $v$, decision threshold $a$, and non-decision time $T_\text{er}$. The expectations are that drift rate scales with $|\Delta\phi|$, that valid-cue trials show higher drift rates and (potentially) lower decision thresholds, and that the median reaction time shortens with increasing $|\Delta\phi|$ in a manner consistent with primate reaction-time data on similar perceptual-decision tasks (Roitman & Shadlen, 2002; Hanks & Summerfield, 2017). We will additionally report the false-alarm time distribution on no-change trials, and compare the conditional accuracy function (the dependency of accuracy on within-trial reaction time) to human data on speeded perceptual decisions.

### 3.4 Saliency-map dynamics across the trial

The interpretable attention readout $S_t(i, j)$ will be plotted as a heatmap movie across the trial timeline for several representative cueing conditions, including all crossings of cue position (top-left, bottom-right) by validity proportion ($p \in 1.0, 0.75, 0.5, 0.25$). We expect to observe a peak at the cue location at $t = 1$, transient saliency at the four Gabor onsets at $t = 3$, low saliency throughout the baseline-orientation period, and a sharp rise at the changed location at $t \ge t^\star$. We will quantify saliency localization by computing the per-quadrant saliency mass $\sum_{(i,j) \in q} S_t(i, j)$ and plotting it as a stacked time series across the trial.

The spatial distribution of saliency mass at $t = t^\star + 1$ will be compared to the cue-condition-conditional posterior over the changed quadrant: under high-validity cues a well-trained agent should show saliency concentrated at the cued location; under low-validity cues the saliency map should distribute more diffusely, reflecting genuine uncertainty about where to look. Comparisons will be made to the human covert-attention literature on cued change detection (Hollingworth et al., 2008) and to functional-magnetic-resonance-imaging measurements of visual-cortex activation under spatial cueing (Brefczynski & DeYoe, 1999), in which retinotopically organized cortex shows enhancement at attended locations even in the absence of overt eye movements.

### 3.5 Causal manipulations of the saliency map

Following the methodology of microstimulation and lesion studies in primate parietal and superior collicular cortex (Cavanaugh & Wurtz, 2004; Müller et al., 2005; Cutrell & Marrocco, 2002), we will perform causal manipulations of $S_t$ during inference and measure the resulting behavioral changes. Three manipulations are planned. First, saliency clamping: $S_t$ will be forced to a target value at a specific quadrant for a specific time window, in analogy to electrical microstimulation of attention-priority maps in the superior colliculus or in the lateral intraparietal area. Second, saliency suppression: $S_t$ will be set to zero at a specific quadrant, in analogy to lesion or pharmacological inactivation of cortical attention areas. Third, saliency redistribution: the spatial distribution of saliency mass will be altered while the total is held fixed, in analogy to cortical reweighting paradigms.

The expectations, derived from the primate microstimulation literature, are that artificially elevating saliency at the cued location reduces miss rate and shortens reaction time, in analogy to the priority-map enhancement observed under collicular microstimulation; that suppressing saliency at the changed quadrant produces deficit patterns analogous to spatial neglect (Heilman et al., 2003); and that redistributing saliency away from the cued location during the maintenance period produces selective deficits on valid-cue trials with relatively spared performance on invalid-cue trials. Critically, because $S_t$ in PRISM is a derived quantity rather than a learned softmax, these manipulations probe the architecture's reliance on its own self-generated attention signal rather than on a separately optimized attention parameter; they are therefore tests of the predictive-coding-as-attention hypothesis.

### 3.6 Decoding cue features from working memory

To probe what information is actually carried by the recurrent state $M_t$, we will train linear decoders on $M_t$ at each timestep $t$ to predict the cue color, the cue position, and the cue-validity proportion. We expect linear decodability of all three features to rise sharply between $t = 1$ and $t = 2$, plateau at near-perfect accuracy through the maintenance period, and (for the cue-position decoder) remain elevated through the change-detection window. We will additionally compute the representational dissimilarity matrix (Kriegeskorte et al., 2008) of $M_t$ at the moment of change report, to test whether the recurrent state at decision time is organized primarily by cue identity (the prediction of a working-memory account) or by stimulus identity (the prediction of a pure-perceptual account). Comparisons will be made to monkey prefrontal-cortex single-unit data on cue-feature maintenance during working-memory delays (Constantinidis et al., 2018).

A complementary decoding analysis will probe the per-channel structure of $M_t$. We will fit linear decoders to individual channels of $M_t$ and identify which channels carry which task variables (cue color, cue position, per-quadrant baseline orientation, per-quadrant change indicator). A successful PRISM should show clean factorization of these variables onto distinct memory channels — analogous to the segregation of feature-dimension-specific working-memory traces observed in different prefrontal subpopulations (Riley & Constantinidis, 2016).

### 3.7 Inner-loop variational-inference depth

We will sweep $K \in 0, 1, 2, 4, 8$ and re-train PRISM under each setting, measuring asymptotic accuracy and across-seed variance. The expectations, formalized in the working-memory compute-depth hypothesis (Morgan, 2026), are that asymptotic accuracy is monotonically non-decreasing in $K$ over the swept range, that the largest jump occurs between $K = 1$ and $K = 2$, and that across-seed standard deviation of asymptotic accuracy decreases strictly with $K$. We will additionally verify the Banach-contraction prediction by measuring the residual $M_t^{(k+1)} - M_t^{(k)}_F$ as a function of inner iteration $k$ and confirming geometric decay on solved trials. A failure of geometric decay on a particular trial — that is, a trial on which the inner loop does not converge — should predict a subsequent error on that trial; this is a within-model prediction with no published neuroscientific analogue but a clear test in PRISM itself.

### 3.8 Component ablation studies

To isolate the contribution of individual architectural components, we will perform a series of ablations. Removal of FiLM modulation forces $\gamma \equiv 1, \beta \equiv 0$, eliminating the top-down gain pathway. Replacement of the error-gated GRU with a vanilla per-channel GRU eliminates the spatial structure of memory updates. Replacement of the autoencoding PC term with the forward-only formulation, which exhibited the cold-start zero-attractor in pilot experiments, tests whether the bootstrapping argument of Section 2.11 is causally supported. Removal of the inner variational-inference loop ($K = 0$) tests the WM compute-depth hypothesis. Each ablation produces a falsifiable prediction about which behavioral or representational signature should disappear, in conjunction with a corresponding neuroscience parallel: lesions of feedback projections (analogous to FiLM removal) are predicted to abolish top-down attentional facilitation; cooling of dorsolateral prefrontal cortex (analogous to GRU replacement) is predicted to abolish cue maintenance across the delay; pharmacological disruption of dopaminergic novelty signaling (analogous to disabling the error-gated update) is predicted to spare baseline performance but disrupt the binding of new information into memory.

---

## 4. Results — Quantitative Findings

*Pending experimental completion. Quantitative results from the analyses templated in Section 3 will be reported here.*

---

## 5. Discussion

*Pending. The Discussion will address: comparison with prior architectures including the recurrent-models-of-visual-attention line (Mnih et al., 2014), slot-attention object-centric models (Locatello et al., 2020), and pure transformer-based working-memory models; a precise statement of which neuroscientific predictions PRISM makes that are not made by spotlight or attention-softmax models; limitations of the present implementation, including the small action space and the absence of an explicit precision-weighting mechanism that a fuller free-energy implementation would include; and future directions including hierarchical predictive coding, expected-free-energy action selection (active inference), and transfer to other partially observable visual-control tasks.*

---

## 6. Conclusion

*Pending experimental completion.*

---

## References

Ba, J., Mnih, V., & Kavukcuoglu, K. (2015). Multiple object recognition with visual attention. *International Conference on Learning Representations*.

Ballas, N., Yao, L., Pal, C., & Courville, A. (2016). Delving deeper into convolutional networks for learning video representations. *International Conference on Learning Representations*.

Bastos, A. M., Usrey, W. M., Adams, R. A., Mangun, G. R., Fries, P., & Friston, K. J. (2012). Canonical microcircuits for predictive coding. *Neuron*, 76(4), 695–711.

Bisley, J. W., & Goldberg, M. E. (2010). Attention, intention, and priority in the parietal lobe. *Annual Review of Neuroscience*, 33, 1–21.

Brefczynski, J. A., & DeYoe, E. A. (1999). A physiological correlate of the 'spotlight' of visual attention. *Nature Neuroscience*, 2(4), 370–374.

Buckley, C. L., Kim, C. S., McGregor, S., & Seth, A. K. (2017). The free-energy principle for action and perception: a mathematical review. *Journal of Mathematical Psychology*, 81, 55–79.

Carrasco, M. (2011). Visual attention: the past 25 years. *Vision Research*, 51(13), 1484–1525.

Cavanaugh, J., & Wurtz, R. H. (2004). Subcortical modulation of attention counters change blindness. *Journal of Neuroscience*, 24(50), 11236–11243.

Constantinidis, C., Funahashi, S., Lee, D., Murray, J. D., Qi, X. L., Wang, M., & Arnsten, A. F. T. (2018). Persistent spiking activity underlies working memory. *Journal of Neuroscience*, 38(32), 7020–7028.

Cutrell, E. B., & Marrocco, R. T. (2002). Electrical microstimulation of primate posterior parietal cortex initiates orienting and alerting components of covert attention. *Experimental Brain Research*, 144(1), 103–113.

De Valois, R. L., & De Valois, K. K. (1988). *Spatial Vision*. Oxford University Press.

Felleman, D. J., & Van Essen, D. C. (1991). Distributed hierarchical processing in the primate cerebral cortex. *Cerebral Cortex*, 1(1), 1–47.

Friston, K. (2010). The free-energy principle: a unified brain theory? *Nature Reviews Neuroscience*, 11(2), 127–138.

Funahashi, S., Bruce, C. J., & Goldman-Rakic, P. S. (1989). Mnemonic coding of visual space in the monkey's dorsolateral prefrontal cortex. *Journal of Neurophysiology*, 61(2), 331–349.

Gold, J. I., & Shadlen, M. N. (2007). The neural basis of decision making. *Annual Review of Neuroscience*, 30, 535–574.

Goldman-Rakic, P. S. (1995). Cellular basis of working memory. *Neuron*, 14(3), 477–485.

Hanks, T. D., & Summerfield, C. (2017). Perceptual decision making in rodents, monkeys, and humans. *Neuron*, 93(1), 15–31.

Heilman, K. M., Watson, R. T., & Valenstein, E. (2003). Neglect and related disorders. In K. M. Heilman & E. Valenstein (Eds.), *Clinical Neuropsychology* (4th ed., pp. 296–346). Oxford University Press.

Hollingworth, A., Richard, A. M., & Luck, S. J. (2008). Understanding the function of visual short-term memory: transsaccadic memory, object correspondence, and gaze correction. *Journal of Experimental Psychology: General*, 137(1), 163–181.

Hubel, D. H., & Wiesel, T. N. (1962). Receptive fields, binocular interaction and functional architecture in the cat's visual cortex. *Journal of Physiology*, 160(1), 106–154.

Itti, L., & Koch, C. (2001). Computational modelling of visual attention. *Nature Reviews Neuroscience*, 2(3), 194–203.

Jozefowicz, R., Zaremba, W., & Sutskever, I. (2015). An empirical exploration of recurrent network architectures. *International Conference on Machine Learning*.

Kingma, D. P., & Ba, J. (2015). Adam: a method for stochastic optimization. *International Conference on Learning Representations*.

Kriegeskorte, N., Mur, M., & Bandettini, P. A. (2008). Representational similarity analysis — connecting the branches of systems neuroscience. *Frontiers in Systems Neuroscience*, 2, 4.

Lisman, J. E., & Grace, A. A. (2005). The hippocampal-VTA loop: controlling the entry of information into long-term memory. *Neuron*, 46(5), 703–713.

Locatello, F., Weissenborn, D., Unterthiner, T., Mahendran, A., Heigold, G., Uszkoreit, J., Dosovitskiy, A., & Kipf, T. (2020). Object-centric learning with slot attention. *Advances in Neural Information Processing Systems*.

Maunsell, J. H. R. (2015). Neuronal mechanisms of visual attention. *Annual Review of Vision Science*, 1, 373–391.

Mnih, V., Heess, N., Graves, A., & Kavukcuoglu, K. (2014). Recurrent models of visual attention. *Advances in Neural Information Processing Systems*.

Morgan, J. (2026). Working memory compute-depth hypothesis. Internal manuscript, AttentionManuscript repository.

Müller, J. R., Philiastides, M. G., & Newsome, W. T. (2005). Microstimulation of the superior colliculus focuses attention without moving the eyes. *Proceedings of the National Academy of Sciences*, 102(3), 524–529.

Perez, E., Strub, F., De Vries, H., Dumoulin, V., & Bengio, A. (2018). FiLM: visual reasoning with a general conditioning layer. *AAAI Conference on Artificial Intelligence*.

Pleines, M., Pallasch, M., Zimmer, F., & Preuss, M. (2022). Generalization, mayhems and limits in recurrent proximal policy optimization. *arXiv preprint* arXiv:2205.11104.

Posner, M. I. (1980). Orienting of attention. *Quarterly Journal of Experimental Psychology*, 32(1), 3–25.

Rao, R. P. N., & Ballard, D. H. (1999). Predictive coding in the visual cortex: a functional interpretation of some extra-classical receptive-field effects. *Nature Neuroscience*, 2(1), 79–87.

Ratcliff, R. (1978). A theory of memory retrieval. *Psychological Review*, 85(2), 59–108.

Reynolds, J. H., & Chelazzi, L. (2004). Attentional modulation of visual processing. *Annual Review of Neuroscience*, 27, 611–647.

Reynolds, J. H., & Heeger, D. J. (2009). The normalization model of attention. *Neuron*, 61(2), 168–185.

Riley, M. R., & Constantinidis, C. (2016). Role of prefrontal persistent activity in working memory. *Frontiers in Systems Neuroscience*, 9, 181.

Roitman, J. D., & Shadlen, M. N. (2002). Response of neurons in the lateral intraparietal area during a combined visual discrimination reaction time task. *Journal of Neuroscience*, 22(21), 9475–9489.

Schulman, J., Moritz, P., Levine, S., Jordan, M., & Abbeel, P. (2016). High-dimensional continuous control using generalized advantage estimation. *International Conference on Learning Representations*.

Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). Proximal policy optimization algorithms. *arXiv preprint* arXiv:1707.06347.

Spratling, M. W. (2008). Predictive coding as a model of biased competition in visual attention. *Vision Research*, 48(12), 1391–1408.

Sutton, R. S. (2019). The bitter lesson. Online essay.

Treisman, A. M., & Gelade, G. (1980). A feature-integration theory of attention. *Cognitive Psychology*, 12(1), 97–136.

Wu, Y., & He, K. (2018). Group normalization. *European Conference on Computer Vision*.