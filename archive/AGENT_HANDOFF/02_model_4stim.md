# 02 — The 4-stimulus (SS4) conv-JEPA model: `affine_ew` and `crossattn1`

WHAT THIS IS: agent-to-agent handoff for the set-size-4 (`vda4`, 2×2 grid) recurrent-ViT covert-attention model at `/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv/`, covering BOTH feedback variants — `affine_ew` (PRIORITY-stream, bottom-up salience lock) and `crossattn1` (VALUE-stream, memory-as-tokens cross-attention).

Sibling handoff docs (same dir `/Users/jonathanmorgan/AttentionManuscript/AGENT_HANDOFF/`): `01_reference_paper.md` · `02_model_4stim.md` (this file) · `03_model_9stim.md` · `04_report_paper_formatting.md` · `05_research_reading.md` · [`README.md`](README.md) (index — **start here**).

---

## 1. What this model IS (one paragraph)

A recurrent vision transformer that learns *covert spatial attention* purely from sparse reward on a cued orientation-change-detection task. It is our clean-room re-implementation of the Morgan/Albanna/Herman paper net, but with three deliberate simplifications so it learns perception **from raw pixels** with no pretrained VAE: (i) a small SE-ResNet conv front-end (`conv_frontend.py`, `--conv-frontend`) replaces the paper's VAE encoder, trained end-to-end; (ii) a compact `d_mem=128` spatial xLSTM instead of 1024; (iii) an auxiliary V-JEPA temporal self-distillation head (`--jepa-coef 0.5`) that shapes the recurrence. The rest is paper-faithful: four 25×25 patches → 4×140 tokens → recurrent-ViT self-attention with memory→vision feedback → per-patch spatial xLSTM → flattened `4×128=512` readout → distributional QR-DQN actor-critic. The **only architectural knob that changes between the two models this doc covers is `--feedback`**: `crossattn1` (memory feedback as extra key/value tokens) vs `affine_ew` (memory feedback as an element-wise affine gate on the visual tokens). Both are trained on the `vda4` task (2×2 = set-size 4, coloured value cue + validity ring). Class name for the whole net: `RViTPaperModel` in `model.py`.

---

## 2. Architecture pipeline, end-to-end (exact symbols + file:line)

`RViTPaperModel.__init__` — `model.py:34-74`. Sub-modules assembled: `self.front` (conv or VAE front-end), `self.encoder` (`RecurrentViTxLSTM`), `self.actor_head` (`FFActor`), `self.critic_head` (`QRCritic`), optional `self.jepa_head` (`JEPAStructuredHead`).

Online step is `RViTPaperModel.rl_step` — `model.py:108-124`. Whole-trajectory re-encode (used by the PAC update and all analysis) is `RViTPaperModel.forward_rl_sequence` — `model.py:127-152`.

### 2a. Conv SE-ResNet front-end — `conv_frontend.py`
Class `ConvPatchFrontEnd` (`conv_frontend.py:94-129`). Per 50×50×3 RGB frame:
- Split into FOUR 25×25 patches in cell order `[TL, TR, BL, BR]` == `[S1, TR, BL, S4]`, so **patch index == cue_index == change_index** (`conv_frontend.py:123`). This is load-bearing for every analysis: token `i` ⇔ stimulus `i`.
- Each patch → shared CNN `_encode_patch` (`conv_frontend.py:111-116`): `stem` (3×3 conv→GroupNorm→SiLU) → `stage1` SEResBlock 25→13 (32→64ch) → `stage2` 13→7 (64→128ch) → `stage3` 7→7 (128→128ch, extra depth) → `AdaptiveAvgPool2d(1)` → `RMSNorm` → 128-d `ô_i`. `SEResBlock` = Conv-GN-SiLU → Conv-GN → `SqueezeExcite` → +residual → SiLU (`conv_frontend.py:73-91`).
- **GroupNorm not BatchNorm** (`_gn`, `conv_frontend.py:37-41`): the front-end runs at batch=1 during the recurrent online rollout, BN running-stats are fragile there.
- **RMSNorm not LayerNorm** (`conv_frontend.py:44-55`): scale-matches the embedding into the ViT WITHOUT mean-subtraction, because the value cue is COLOUR and a mean-subtracting norm would attenuate a uniform colour DC offset. ⚠️ GOTCHA: the `crossattn1` deep-dive checkpoint (iter 9599) was trained when `out_norm` was `LayerNorm`; the current code has `RMSNorm`. Loading an old checkpoint silently drops `front.out_norm.bias` — analysis loaders must auto-match LayerNorm and assert 0 missing/0 unexpected (see `deepdive/dd_core.py`).
- Token assembly (`conv_frontend.py:118-129`): `x_i = [ô_i(128) ‖ ρ_i(4 one-hot pos) ‖ τ(8 one-hot time)] = 140`. Output `X ∈ ℝ^{B×4×140}`. Timestep one-hot uses the LOGICAL frame `t // frame_repeat`, clamped to slots `[0,7]`. Constants: `N_PATCH=4`, `O_FLAT2=128`, `POS_DIM=4`, `TEMP_DIM=8`, `TOKEN_DIM=140` (`conv_frontend.py:30-34`). ~594K (0.59M) front-end params, trained end-to-end (no pretrain, no reconstruction).

### 2b. Recurrent-ViT self-attention encoder — `paper_encoder.py`
Class `RecurrentViTxLSTM` (`paper_encoder.py:440-556`). Constructed with `feedback=…, d_mem=128, cell="xlstm"`. It picks the attention module by `--feedback` (dispatch at `paper_encoder.py:460-483`) then runs a per-patch `SpatialXLSTM`. `forward_step` — `paper_encoder.py:505-556`. Single-LSTM path (both `crossattn1` and `affine_ew` are single-LSTM here): attention produces `Z ∈ ℝ^{B×4×140}`, `SpatialXLSTM` maps `Z → H1 ∈ ℝ^{B×4×128}`, heads read `H1` (`paper_encoder.py:551-556`). Token/attention layout is 4 query patches; attention map is `(B,4,4)` for `affine_ew` or `(B,4,8)` for `crossattn1` (see §3).

`SpatialXLSTM` — `paper_encoder.py:368-395`. Exact paper xLSTM: `W_{i,f,o,u} ∈ ℝ^{140×128}` (input, biased), `R_{i,f,o,z} ∈ ℝ^{128×128}` (recurrent, bias-free); stabiliser `M=max(F̃+M_prev, Ĩ)`, `I=exp(Ĩ−M)`, `F=exp(F̃+M_prev−M)`, `O=σ(Õ)`, `U=tanh(Ũ)`, `N=F·N_prev+I`, `C=C_prev·F+U·I`, `H=O·(C/(N+1e-8))`. State tuple = `(H,C,N,M)` each `(B,4,128)`, init all zeros (`init_states`, `paper_encoder.py:496-503`).

### 2c. Readout + heads — `paper_heads.py`
Readout is the flattened cell: `H1.flatten(1) ∈ ℝ^{B×512}` (4 patches × 128). The paper drops the 4-patch structure at the RL agent; `readout_dim = n_patch*d_mem = 512` (`paper_encoder.py:491`; with default d_mem=1024 it would be 4096 — the docstrings still say 4096, but for THESE models d_mem=128 → 512).
- `FFActor` (`paper_heads.py:24-39`): `512 → Linear256-ELU ×3 → Linear(2)` → policy logits over 2 actions. `init_action_bias=[0.0, -1.5]` (biased toward action 0 = wait at init).
- `QRCritic` (`paper_heads.py:42-65`): same 3-ELU trunk → `Linear(A*N)` → `(B, 2, 5)` quantiles per action (`n_quantiles=5`, QR-DQN). `derive_V` (`paper_heads.py:60-65`): `V_dist = Σ_a π(a)·Q_dist(a)`, `V_scalar = mean(V_dist)`.
- Actions: `0=wait`, `1=declare-change`.

### 2d. JEPA self-distillation head — `paper_heads.py:68-86`
`JEPAStructuredHead` (built only when `jepa_coef>0`, `model.py:70-74`). Reads the recurrent CELL output per patch token: `LayerNorm(d_mem) → MLP(512-GELU-512-GELU) → Linear(n_heads*proto_dim)` → `(…, 4, 256)` logits, softmaxed over `proto_dim` per head. Per token → 4 distributions; across 4 patches → 16 independent softmaxes. Used ONLY for the distillation loss — it does NOT change the memory. `jepa_center` buffer `(4,4,256)` is the DINO teacher-centering buffer, lives on the STUDENT only. `RViTPaperModel.jepa_logits` — `model.py:154-156`.

---

## 3. EXACTLY how `affine_ew` differs from `crossattn1`

Both share the front-end, xLSTM, heads, JEPA, task, and training recipe. They differ ONLY in `self.encoder.attn` (selected at `paper_encoder.py:460-483`) — i.e. HOW the recurrent memory `H1` feeds back onto the visual tokens before attention. Use PRIORITY / VALUE stream language:

### `crossattn1` → `CrossAttentionXH` (`paper_encoder.py:116-142`) — the VALUE stream
Memory-as-tokens (paper's "concatenation" mechanism). Queries come from the image only; keys/values span BOTH image and memory:
```
Q = W_q(X)                               ∈ (B,4,140)
K = [W_kx(X) ‖ W_kh(H1)]                 ∈ (B,8,140)   keys 0-3 IMAGE, 4-7 MEMORY
V = [W_vx(X) ‖ W_vh(H1)]                 ∈ (B,8,140)
A = softmax(QKᵀ/√140)                    ∈ (B,4,8)     each query attends over 8 keys
Z = X + A·V                              residual = X
```
Attention map is `(B,4,8)`. The current image ALSO enters `Z` through the residual `X` regardless of `A`, so suppressing image-key attention does not blind the model to the current frame — that residual path is why "detection rides in on the residual" in the causal analysis. `attn_clamp` additively biases pre-softmax key logits `j∈{0..3}` image, `{4..7}` memory (`paper_encoder.py:136-139`).

**What it buys (VALUE stream, valuation/decision-refining):** a *frame-gated* algorithm — the image is read essentially only on the cue frame (`t=1`), then the model runs from memory. The memory read produces a *cue-timed change-lock*: validly cued changes lock at `t=5`, invalidly cued changes lock one frame later at `t=6` — the attentional analogue of the behavioural cueing benefit. Hard attention clamps are a STRONG causal lever (dual effect present — see §6).

### `affine_ew` → `ElementwiseAffineSelfAttention` (`paper_encoder.py:276-317`) — the PRIORITY stream
Element-wise affine gate on the tokens, then STANDARD self-attention over the 4 image patches (no memory-key column):
```
b   = tanh(bottleneck(H1))               d_hyper=64
γ   = gen_scale(b)   ∈ (B,4,140)         element-wise SCALE   (bias-init 1 ⇒ γ=1 at start)
β   = gen_shift(b)   ∈ (B,4,140)         element-wise SHIFT   (zero-init ⇒ β=0 at start)
X'  = γ ⊙ X + β                          NO `1+` identity term (unlike FiLM)
Q,K,V = W_XQ/K/V(X')
A   = softmax(QKᵀ/√140)                  ∈ (B,4,4)   query→image-patch only
Z   = X + A·V                            residual = X
```
Init `γ→1, β→0 ⇒ X'=X ⇒ plain self-attention at start (alive)`; a zero-init scale would give `X'≈0` → dead attention (`gen_scale.bias` init to ones, `paper_encoder.py:296`). Attention map is `(B,4,4)`. `attn_clamp` biases pre-softmax patch-key logits `j∈{0..3}` (`paper_encoder.py:311-314`).

⚠️ TERMINOLOGY TRAP: the `affine_ew` **repro paper** (`repro/paper_affine_ew.tex`) markets this as the paper's "multiplicative-gating" feedback mechanism (`X'=γ(H)⊙X+β(H)`). That is a presentation choice mapping it onto the paper's three-mechanism taxonomy (concat/additive/multiplicative). In the CODE it is `ElementwiseAffineSelfAttention` / `--feedback affine_ew`. Do not confuse with `--feedback multiplicative` (the paper's pure Hadamard `Q=(XW)⊙(HW)` in `MultiplicativeSelfAttention`, `paper_encoder.py:38-81`) or `--feedback affine` (the full d×d scale-MATRIX version `AffineModulatedSelfAttention`, `paper_encoder.py:217-273`). `affine_ew` is the diagonal/element-wise one.

**What it buys (PRIORITY stream, drives the deployment):** a *bottom-up salience lock* — attention orients to the cue (transient), releases at the blank, re-acquires the cued patch as Gabors appear, then **locks onto ANY large orientation change on the change frame regardless of whether it was cued** (valid AND invalid at `t=5`). This is a priority-map/salience grab. Consequently hard clamps are a WEAK causal lever (no dual effect — see §6).

Dispatch note: `crossattn` (2-LSTM) vs `crossattn1` (1-LSTM) both map to `CrossAttentionXH`, but `crossattn1` does NOT force a second LSTM (`paper_encoder.py:460-464`); these SS4 models use `crossattn1`. `forward_step` forwards `attn_clamp` to all clamp-applying modules incl. `CrossAttentionXH`, `ElementwiseAffineSelfAttention`, `AffineModulatedSelfAttention`, `MultiplicativeSelfAttention` (`paper_encoder.py:546-550`) — a fixed latent bug that used to silently no-op clamps on the affine variants.

---

## 4. The task / environment (SS4 change-detection)

Task name `vda4` → `VDAEnv` (`envs/tasks.py:36-41`), a 2×2 grid subclass of `BaseChangeDetectionEnv` (`envs/base.py:32`). Registry in `envs/tasks.py` + `envs/__init__.py`; `make_env("vda4", …)`.

- **Grid:** 2×2 = 4 Gabor stimuli, one per quadrant, indexed row-major `[S1=TL, TR, BL, S4=BR]`.
- **Timeline (T=7 logical frames):** `t=0` blank · `t=1` cue · `t=2` blank · `t=3-6` four oriented Gabors (independent orientation noise `σ=5` each frame) · **change fixed at `t=5`** (`min_change_time=max_change_time=5`). Rendering in `_next_observation` (`envs/base.py:124-143`).
- **Cue:** coloured disc marking one quadrant, drawn at `t=1` (`_render_cue`, `envs/base.py:145-163`). Cue restricted to `cue_positions` — for `vda4` this defaults to all 4 (Validity4Env restricts to `[0,3]`=S1/S4; VDAEnv does not override, so it can cue any quadrant).
- **Validity:** encoded by the cue-ring completeness = `proportion p ∈ {0.25, 0.5, 0.75, 1.0}` = P(a change, if it occurs, is at the cued quadrant). On change trials, `_draw_change_index` (`envs/base.py:115-121`) puts the change at the cued patch w.p. `p`, else a uniform random patch. Because the "else" is uniform over all patches (incl. the cued one), the EMPIRICAL cued-change probability is higher than nominal `p` (~46% at the 25% ring) — the repro papers state this caveat.
- **Value cue:** `value_cues=True` for VDAEnv → cue COLOUR signals reward magnitude: `red=5, green=3, blue=1` (`color_values`, `envs/base.py:82`); `_reward_value` (`envs/base.py:177-181`). This is the "vda" = value-directed attention.
- **Reward structure (`step`, `envs/base.py:188-206`):** action `1` (declare) on/after the change on a real reportable change → `_reward_value()` (value-weighted); declaring early or on a no-change trial → 0 (false alarm), trial ends. Waiting through a no-change trial to `t≥T` → `_reward_value()` (correct rejection). `info["correct"] = reward>0`. So both hits and correct rejections are rewarded — a conservative "wait" strategy still earns CR reward.
- **Orientation-change magnitude:** `Δ ~ U(−θ, θ)` where `θ = env.theta` is the current curriculum max (`orientation_change`, `envs/base.py:104`). Change applied to the changed patch's orientation from the change frame on (`envs/base.py:137-138`).
- Observation = `(50,50,3)` float32 in `[-1,1]`.

---

## 5. Training recipe

Entry point `train_rl.py` → `ppo.train` (`ppo.py:752`). Objective = PAC actor + QR-DQN critic + PER replay + EMA target + JEPA aux. Config defaults in `config/default.json`; CLI overrides in `train_rl.py:41-125`.

- **Actor = PAC** (Springenberg/Abdolmaleki et al. 2024 = MPO E-step + behavioural cloning), replacing PPO's clipped surrogate. `mpo_temperature=0.1` (η in the E-step), `bc_alpha=0.1` (0=pure MPO, 1=pure BC) (`ppo.py:461-463`, config). The MPO reference policy is computed from the EMA target `π_θ'`.
- **Critic = distributional QR-DQN**, 5 quantiles, quantile-Huber loss `qr_kappa=1.0`, `value_coef=0.5`, `gamma=0.95`.
- **PER = prioritized EPISODE replay** (Schaul 2016) at episode granularity: fresh on-policy episodes + replay episodes; `buffer_capacity=1000`, `per_n_replay=4`, `per_alpha=0.6`, `per_beta 0.4→1.0`, `per_priority_clip=50`. Buffer class `EpisodeReplayBuffer` (`ppo.py:79-173`) — a FIFO ring buffer of complete episodes with prioritized (PER, Schaul 2016) sampling; the class name says `EpisodeReplayBuffer`, the prioritization is in its `push`/`sample`.
- **EMA target model θ'** (`ema_decay=0.995`): created as `copy.deepcopy(model)`, params frozen, updated each iter `θ' ← decay·θ' + (1−decay)·θ` on BOTH params and buffers (`ppo.py:795-867`). Replaces the hard-copy target (`target_update_period=0`). Used for the critic TD target AND the MPO reference policy.
- **JEPA teacher** (`jepa_coef=0.5`): a SEPARATE `copy.deepcopy(model)` EMA net, `jepa_ema_decay=0.996` (DECOUPLED from the RL target), PARAMETERS-ONLY EMA (no buffer copy — the `jepa_center` buffer must stay on the student) (`ppo.py:813-878`). Student@t predicts EMA-teacher@t+1 (temporal V-JEPA, `jepa_temporal=True`); DINO centering (`center_momentum=0.9`) + temperatures `τ_s=0.1`, `τ_t 0.04→0.07` warmup over 300 iters (`ppo.py:505-515`, `569-577`). 4 heads × 256 protos. Teacher logits computed once/update from `forward_rl_sequence(return_cell=True)` → `jepa_logits`.
- **Curriculum (paper, in `envs/base.py`):** `Δ~U(−θ,θ)`, θ starts at `theta_start=65`; when success ≥ `curr_threshold=0.85` over a NON-OVERLAPPING window of `curr_window=1000` trials, drop θ by `curr_step=3.0°`, floored at `theta_floor=8`. `_update_curriculum` (`envs/base.py:208-221`): appends per-trial correctness to `_recent_correct`, and ONLY at each 1000-trial block boundary checks the block mean and drops θ, then RESETS the list. `curr_decay=0.9` is a legacy multiplicative fallback used only if `curr_step≤0`. NOTE: curriculum is OFF by default at the CLI — the env default is `curriculum=True` (`envs/base.py:54`) but `train_rl.py:137` passes `curriculum=args.curriculum` and `--curriculum` is `action=store_true` (default False), so the flag overrides the env default to OFF unless you pass `--curriculum`. The README canonical commands do NOT show `--curriculum`, yet the two live runs were launched WITH it — proven on disk by θ having moved off 65 (crossattn1 θ=62, affine_ew θ=50; θ can only change when curriculum is ON). θ is logged to `metrics.csv` (`env/theta`) each iteration.
- Loop: `iters=50000 × episodes_per_iter=8`, `lr=3e-4`, `grad_clip=0.5`, `entropy_coef=0.01`, `burn_in_iters=20`. `save_every=200` → `rvit_plus_rl_latest.pt` (holds `model_state_dict` + `theta`); final → `rvit_paper_vda4_final.pt`. metrics.csv appended+flushed each iter.

---

## 6. Key empirical findings per variant (VERIFIED against the repo papers)

Ranked SS4 headline: same conv-JEPA net, ONE knob (`--feedback`) flips the attentional phenotype. Findings below are quoted from `repro/paper_{crossattn1,affine_ew}.tex`, `deepdive/conv_deepdive.tex` (crossattn1, iter 9599, ≈0.87), `deepdive_affine/affine_ew_deepdive.tex` (affine_ew, iter 4199, ≈0.83), and `project_setsize_invalid_manuscript.md`.

**Shared across both variants:**
- Orderly sigmoidal psychometric + chronometric functions; genuine spatial cueing benefit (valid changes detected at lower Δ than invalid). crossattn1 deep-dive natural behaviour (iter 9599): correct 0.865, hit 0.76, CR 0.96, FA 0.044, presses cluster on the change frame. affine_ew ≈0.83 correct.
- **Both are VALIDITY-INVARIANT** in attention AND behaviour: fitted psychometric threshold (Position) is FLAT across displayed validity (crossattn1 13.8/13.8/13.9/14.0°; affine_ew 12.5/12.8/13.1/12.3°). The cueing benefit exists but does NOT scale with displayed proportion. Mechanism differs (below).
- Both reproduce the SDT "stimulation" dissociation: graded attention biasing TOWARD the change lowers the criterion `c` and preserves/raises `d'`; biasing AWAY reduces `d'`.
- Cue position + cue value decode perfectly from the cell at `t=1` onward and are MAINTAINED; change presence/location decode sharply at `t=5`.

**`crossattn1` (VALUE stream) — memory change-lock, strong causal lever:**
- Frame-gated attention: reads the image only at the cue frame, runs from memory otherwise. Cue-frame read is spatially precise (non-cued queries place ≈1.0 on the cued image patch, per-query).
- Change-lock is in MEMORY and cue-timed: VALID locks at `t=5` (excess +0.20/+0.24 over uniform 0.25), strong at `t=6` (+0.74/+0.75); INVALID has NO lock at `t=5` (−0.03/−0.02) and locks only at `t=6` (+0.69/+0.70). One frame of attentional cueing benefit. (Table in `conv_deepdive.tex`.)
- Validity/value are read at the cue frame but act at the DECISION, not on the map ("recurrence computes, attention reflects": change decodable at `t=5`, one frame before the invalid-attention lock at `t=6`).
- **Hard clamps = STRONG causal lever with a DUAL EFFECT** (`paper_crossattn1.tex`): clamping attention onto an uncued change `α4=1` raises detection `0.67→0.81` at Δ=18°; suppressing the cued location `α1=0` ALSO raises it `0.67→0.75` (the SC-inactivation dual effect). Parametric shift grades the threshold `13.8°→17.6°` as `α1: 1.0→0.1`. Enhancing `α4` on an uncued change: hit rate `30%→66%`.
- Causal: suppressing ALL memory keys costs ~0.1–0.15 at high magnitude but detection SURVIVES (0.98→0.84 at 28°) — change rides the residual `X`; memory read refines.

**`affine_ew` (PRIORITY stream) — bottom-up salience lock, weak causal lever:**
- Attention schedule: orient (0.73 to cued at `t=1`) → release at blank (0.22 at `t=2`) → re-acquire cued patch over Gabor frames (0.44→0.80) → lock on change.
- **Change-lock is BOTTOM-UP**: fires for BOTH valid AND invalid changes on the change frame `t=5` (attention to changed patch: valid 1.00, invalid 0.92; decaying by `t=6` to 0.71/0.54). Any large orientation step pulls attention regardless of the cue. This is a priority/salience grab.
- **Validity discarded, not just unused**: proportion is decoded at 0.99 at `t=1` but COLLAPSES to chance (0.22) by the Gabor onset `t=3` — perceived then discarded within two frames. Position + value ARE retained. This is the mechanistic reason attention/behaviour cannot scale with validity.
- Value (colour) IS retained → mild decision effect (red=5 detected best: 0.90 > green 0.85 > blue 0.81 at 28°); cue-frame focus varies by colour but NOT monotonically with value (a low-level colour-appearance effect on the front-end, not value gain).
- **Hard clamps = WEAK causal lever, NO dual effect** (`paper_affine_ew.tex`): `α4=1` on an uncued change gives 0.65→0.65 (no gain); `α1=0` slightly LOWERS detection 0.65→0.61; parametric threshold stays flat (~12.2–13.4° across α1). BUT graded biasing still moves the SDT criterion (`V:4.18→4.31`, `c:0.31→0.12`). So attention enters as a soft rescaling, not a competitive key/value → strong graded decision influence, weak hard override. Enhancing `α4` on uncued change: hit `52%→~64%` (peak near α4=0.5), non-monotone.

**Cross-variant SS4→SS9 hook (see `03_model_9stim.md`):** at SS9 the crossattn1 (top-down) invalid change-lock is ABOLISHED (never recovers), while affine_ew's bottom-up lock STILL fires for invalid changes — the invalid-cue cost scales catastrophically with set size ONLY for the top-down cue-gated reader. SS9 behaviour is stated as a PREDICTION (mid-training), not measured.

---

## 7. File map · run commands · checkpoints

### File map (`RViT_plus_paper_jepa_conv/`)
| file | what |
|---|---|
| `model.py` | `RViTPaperModel` — assembles front-end/encoder/heads/JEPA; `rl_step`/`forward_rl_sequence`/`jepa_logits`. |
| `conv_frontend.py` | `ConvPatchFrontEnd` (SE-ResNet, `--conv-frontend`) + `SEResBlock`/`SqueezeExcite`/`RMSNorm`. THE front-end for these models. |
| `paper_encoder.py` | `RecurrentViTxLSTM` + all feedback modules incl. `CrossAttentionXH` (crossattn1) and `ElementwiseAffineSelfAttention` (affine_ew) + `SpatialXLSTM`. |
| `paper_heads.py` | `FFActor`, `QRCritic`, `JEPAStructuredHead`. |
| `vae_frontend.py` / `vae.py` / `patch_embed.py` / `pretrain_vae.py` | the OLD paper VAE front-end path — NOT used by these conv models. |
| `envs/base.py` | `BaseChangeDetectionEnv` (timeline, render, reward, curriculum). |
| `envs/tasks.py` | `VDAEnv` (=vda4), `Validity4Env`, `SetSizeEnv`, `LuoMaunsellEnv`, `KrauzlisEnv`. |
| `envs/__init__.py` | `TASKS` registry, `make_env`, `task_grid`. |
| `ppo.py` | PAC + QR-DQN + PER + EMA target + JEPA teacher trainer; `train()`, `PPOConfig`, `EpisodeReplayBuffer` (the PER episode buffer). |
| `train_rl.py` | CLI entry; builds env+model+`PPOConfig`, handles fresh/warm_start/resume, saves. |
| `config/default.json` + `config/loader.py` | default hyperparams + checkpoint-load helpers. |
| `repro/` | full 17-figure reproduction: `repro_core.py`, `repro_supp.py`, `repro_fig{1..17}.py`, `run_model.sh`, `run_supp.sh`, `paper_crossattn1.tex`/`.pdf`, `paper_affine_ew.tex`/`.pdf`, frozen `data_fig*_{crossattn1,affine_ew}.npz`. |
| `deepdive/` | crossattn1 single-variant deep-dive: `conv_deepdive.tex`/`.pdf`, `dd_core.py`, `dd1..dd5*.py`, `summary_dd*.npz`. |
| `deepdive_affine/` | affine_ew deep-dive: `affine_ew_deepdive.tex`/`.pdf`, `dda_core.py`, `dda_*.py`, `summary_dda_*.npz`. |
| `attn_maps/` | attention-map analysis scripts (`run_conv.py`, etc.). |
| `analysis/`, `tests/`, `reviews/` | analysis utilities, tests, critic output. |

### Run commands (established style — `source .venv/bin/activate && python …`, plain `python`, change only what's needed)
```bash
# crossattn1 (VALUE stream) — canonical SS4 run  (checkpoint dir is paper_jepa_conv_d128)
source .venv/bin/activate && python RViT_plus_paper_jepa_conv/train_rl.py \
  --device mps --init-mode fresh --T 7 --min-change-time 5 --max-change-time 5 \
  --cell xlstm --feedback crossattn1 --conv-frontend --jepa-coef 0.5 --d-mem 128 \
  --checkpoint-dir ~/rvit_plus_checkpoints/paper_jepa_conv_d128

# affine_ew (PRIORITY stream) — canonical SS4 run
source .venv/bin/activate && python RViT_plus_paper_jepa_conv/train_rl.py \
  --device mps --init-mode fresh --T 7 --min-change-time 5 --max-change-time 5 \
  --cell xlstm --feedback affine_ew --conv-frontend --jepa-coef 0.5 --d-mem 128 \
  --checkpoint-dir ~/rvit_plus_checkpoints/paper_jepa_conv_affine_ew
```
To CONTINUE a run after an OOM (see §8), swap `--init-mode fresh` for `--init-mode resume` (auto-discovers `rvit_plus_rl_latest.pt` in the checkpoint dir, restores weights AND θ if `--curriculum` AND the checkpoint actually carries a `theta` key). Add `--curriculum` — the live metrics.csv shows θ moving (62/50), so both live runs were launched with it. ⚠️ The crossattn1 `_latest.pt` has NO `theta` key (older save format), so a `--curriculum` resume from it will NOT restore θ — it falls back to `--theta-start` (65). Pass `--theta-start 62` when resuming crossattn1 (see §7 checkpoint note). Cap CPU: `export OMP_NUM_THREADS=3 MKL_NUM_THREADS=3`; ONE torch job at a time (see `feedback_cap_cpu_on_laptop`).

Regenerate the full figure set for a variant (strictly sequential on MPS):
```bash
RViT_plus_paper_jepa_conv/repro/run_model.sh <snapshot.pt> crossattn1 crossattn1
RViT_plus_paper_jepa_conv/repro/run_model.sh <snapshot.pt> affine_ew  affine_ew
```

### Checkpoints (`~/rvit_plus_checkpoints/`)
- `paper_jepa_conv_d128/` — the **crossattn1** SS4 model. `rvit_plus_rl_latest.pt` + `metrics.csv`. (dir name says d128, feedback is crossattn1 — do NOT assume a `..._crossattn1` dir exists; it doesn't.) VERIFIED crossattn1 from the on-disk state-dict: `encoder.attn` holds `{W_q, W_kx, W_kh, W_vx, W_vh}` = `CrossAttentionXH`'s projections (the `W_kh`/`W_vh` memory-key/value columns are the fingerprint). `lstm.W_i.weight` is `(128,140)` and `actor_head.net.0.weight` is `(256,512)` → d_mem=128, readout=512 (both variants).
- `paper_jepa_conv_affine_ew/` — the **affine_ew** SS4 model. `rvit_plus_rl_latest.pt`, `rvit_paper_vda4_final.pt`, `metrics.csv`. VERIFIED affine_ew from `encoder.attn` = `{W_XQ, W_XK, W_XV, bottleneck, gen_scale, gen_shift}` = `ElementwiseAffineSelfAttention`; the `_final.pt` `model_kwargs` = `feedback=affine_ew, d_mem=128, conv_frontend=True, cell=xlstm`.
- The current trainer writes `*_latest.pt = {iter, model_state_dict, theta}` (`ppo.py:937-938`) and `*_final.pt = {iter, model_state_dict, model_kwargs, task}` (`train_rl.py:259-260`). ⚠️ ON DISK the affine_ew `rvit_plus_rl_latest.pt` DOES carry `theta` (=50.0), but the crossattn1 (`paper_jepa_conv_d128`) `rvit_plus_rl_latest.pt` was saved by an OLDER build and has top-level keys `{iter, model_state_dict}` ONLY — NO `theta`. On a `--curriculum` resume from that file, `train_rl.py:214` does `_ck.get("theta") → None`, so θ falls back to `--theta-start` (65) — a live instance of the θ-reset gotcha in §8. If you resume the crossattn1 run, pass `--theta-start 62` (its last logged θ) or it will jump back to 65.
- Deep-dive analysis snapshots referenced by the papers: crossattn1 iter 9599 (conv_deepdive), 12799 (repro); affine_ew iter 4199 (deepdive), 6599 (repro). These are earlier frozen snapshots — the LIVE checkpoints are further along.

---

## 8. CURRENT OPERATIONAL STATE (critical) — the Apple-MPS memory leak

Source: `reference_torch212_conv_backward_leak.md`. Read it before any long training.

- **Symptom:** conv-frontend RL training on **MPS** climbs system RSS ~1.5–4 MB/iter → OOM (`zsh: killed`) at ~iter 10–12k / ~3–4h. Hits ALL four conv models (both SS4 variants + both SS9 variants).
- **Root cause (confirmed by web search + from-scratch measurement):** a KNOWN, still-OPEN leak in PyTorch's Apple-MPS backend (allocator / graphCache: `MPSAllocator.mm`, `MPSStream.mm`, `MPSEvent.mm`). Reported as pytorch/pytorch **#164299** (MPS leaks, open Sept 2025) and **#16445** (Conv2d RAM growth, "particularly serious in reinforcement learning"), plus #125217/#145374/#77753/#121113. NOT our code, NOT a missing detach, NOT the SE-ResNet — reproduces with a stock `nn.Conv2d`+`nn.GroupNorm` stack.
- **Device-specific:** MPS leaks (+19 KB/it linear, unbounded); **CPU is FLAT**. **Version-independent** (torch 2.8/2.12/2.12.1 identical — downgrading does NOT help). NOT fixed by `empty_cache()`/`synchronize()`/`gc.collect()`.
- **Invisible to torch counters:** `torch.mps.current/driver_allocated_memory()` stay flat while true RSS climbs. MEASURE with `ps -o rss= -p <pid>` (CURRENT rss) or Activity Monitor. Do NOT use `resource.getrusage().ru_maxrss` (that is PEAK/monotonic → freed memory looks permanently leaked). Take the baseline AFTER warmup.
- **Why only this model:** the paper VAE front-end was FROZEN (no conv backward); ViZDoom models are conv-free. The SE-ResNet is the first deep end-to-end conv path on MPS.
- **No clean in-code fix. Two options, and the user's CHOICE:** (1) train on CPU (leak-free, ~2.5–3× slower, ~0.55 vs ~1.57 it/s, runs to completion); (2) **live with it on MPS and RELOAD from `rvit_plus_rl_latest.pt` after each OOM** (~10k iters/session) — this is the user's long-standing workflow and what they chose 2026-07-03. **Do NOT rebuild the model, add a batched-patch, or add an auto-resume wrapper** — the user explicitly REJECTED and reverted all of that; it doesn't address the cause.
- **⚠️ Curriculum-reload interaction (real, important):** the curriculum success window (`envs/base.py:_update_curriculum` / `_recent_correct`) is a non-overlapping 1000-trial block, checked only at block boundaries, and is NOT saved in the checkpoint — only `theta` is. Every reload WIPES the window, and the post-reload accuracy dip keeps each fresh block under 0.85, so **θ can FREEZE across reloads** even though the displayed rolling `correct=` (a separate deque mean) briefly exceeds 0.85. If θ stalls across reloads, persist `_recent_correct` (running sum + count) in the checkpoint.
- **Live state as of this handoff (from `metrics.csv`):** crossattn1 (`paper_jepa_conv_d128`) ~iter 10048, rolling correct ~0.83, θ=62 (metrics.csv confirmed: iter 10048, `rolling/correct_rate=0.83`, `env/theta=62.0`). affine_ew (`paper_jepa_conv_affine_ew`) ~iter 1127 and still advancing, rolling ~0.845, θ=50 (metrics.csv confirmed: iter 1127, `rolling/correct_rate=0.845`, `env/theta=50.0` — a restarted/fresh run, much earlier in iters than the deep-dive snapshots but already at comparable behaviour). Both θ have MOVED off 65 (crossattn1 65→62 = one drop, affine_ew 65→50 = five drops of 3°), which only happens with the curriculum ON — this is the on-disk proof that these live runs were launched with `--curriculum`. Judge maturity by behaviour (rolling correct), NOT the iter field — the same model is reloaded+retrained cumulatively (see `feedback_report_cumulative_training`).

---

## What the next agent MUST know

- **ONE knob = ONE phenotype.** `--feedback crossattn1` (VALUE stream, memory change-lock, strong causal dual-effect lever) vs `--feedback affine_ew` (PRIORITY stream, bottom-up salience lock, weak hard-clamp lever). Everything else (front-end, xLSTM d128, heads, JEPA, task, recipe) is identical. Selected at `paper_encoder.py:460-483`.
- **These are the d_mem=128 conv-frontend models** → readout is `4×128=512`, NOT 4096 (docstrings that say 4096 assume d_mem=1024). Attention map is `(B,4,8)` for crossattn1 (8 keys: 4 image + 4 memory) and `(B,4,4)` for affine_ew.
- **BOTH SS4 variants are validity-INVARIANT** (flat cued threshold ~13–14° / ~12–13°). This is a real result, not a bug — validity is perceived at the cue then not maintained (affine_ew literally discards it by `t=3`). Do NOT "fix" it. Contrast: SS9 crossattn1 DOES start to use validity (α1 grows 0.12→0.31) — see `03_model_9stim.md`.
- **crossattn1 hard clamps move behaviour (dual effect); affine_ew hard clamps do NOT** (0.65→0.65). Both respond to GRADED biasing in SDT terms. Don't report affine_ew's flat clamp as a null model — it's the key dissociation (graded decision influence preserved, hard override weak).
- **MPS leak is not ours and not fixable in code.** Reload-after-OOM (~10k iters/session) is the accepted workflow. Never add auto-resume/batched-patch (rejected). Watch θ freezing across reloads (curriculum window not checkpointed).
- **Measure, don't guess** (`feedback_prove_dont_guess`): trust the live `metrics.csv` over stale `*_latest.pt`; a flat RL plateau is not a ceiling; use `ps` current-rss not `ru_maxrss`; run every cue×change dissociation BOTH ways (cue@S1/chg@S4 and cue@S4/chg@S1).
- **Checkpoint dir naming trap:** crossattn1 lives in `~/rvit_plus_checkpoints/paper_jepa_conv_d128/` (NOT `..._crossattn1`); affine_ew in `..._affine_ew/`.
- **`affine_ew` repro paper calls itself "multiplicative-gating"** to map onto the paper's mechanism taxonomy — in code it is `ElementwiseAffineSelfAttention` / `--feedback affine_ew`, distinct from `--feedback multiplicative` and `--feedback affine` (d×d matrix).
- **Laptop discipline** (`feedback_cap_cpu_on_laptop`): ONE torch job at a time, `OMP/MKL_NUM_THREADS=3`, no Workflow fan-out for compute — stacking all-core torch jobs crashed the MacBook before.
- **Manuscripts are standalone** (`feedback_manuscript_no_meta`): the repro/deep-dive `.tex` must NOT expose build process/iter numbers as "early"/scaffolding. THIS handoff doc is the opposite — internal, exposes everything.
