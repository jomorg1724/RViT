# 03 — The 9-STIMULUS (set-size 9 / SS9 / "grid9") JEPA model

**WHAT THIS IS:** agent-to-agent handoff for the nine-stimulus (3×3 Gabor grid, `vda9`) conv-frontend V-JEPA recurrent-ViT model at `/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_grid9/`, covering BOTH feedback variants — `crossattn1` (PRIORITY = memory-token reader) and `affine_ew` (element-wise memory gate) — with file:line pointers, exact checkpoints, run commands, and the set-size × validity findings.

Sibling docs (all present on disk): [`01_reference_paper.md`](01_reference_paper.md) · [`02_model_4stim.md`](02_model_4stim.md) · `03_model_9stim.md` (this file) · [`04_report_paper_formatting.md`](04_report_paper_formatting.md) · [`05_research_reading.md`](05_research_reading.md) · [`README.md`](README.md) (index — **start here**).

Terminology convention (do not deviate): the two feedback streams are **PRIORITY** (drives the decision/policy — the memory→attention channel that decides where to look and when to declare) and **VALUE** (drives valuation — the distributional critic reads the same memory). NOT "salience/top-down". `crossattn1` exposes PRIORITY as explicit memory-key attention; `affine_ew` exposes it as an element-wise gate on the visual tokens.

---

## 1. What this model IS, and how it relates to / diverges from the SS4 conv model

One sentence: **the exact same conv-frontend + recurrent-multiplicative-ViT + spatial-xLSTM + V-JEPA network as the SS4 model (`RViT_plus_paper_jepa_conv/`), env-parametrized up to a 3×3 = 9-Gabor grid on a 75×75 image, one token per Gabor (9 tokens, not 4).**

- The repo `RViT_plus_paper_jepa_grid9/` is a **copy of `RViT_plus_paper_jepa_conv/`** — identical `model.py`, `paper_encoder.py`, `conv_frontend.py`, `paper_heads.py`, `ppo.py`, `train_rl.py`. The ONLY thing that changes SS4→SS9 is the **env** (`envs/tasks.py::VDA9Env`, grid 3×3, `image_size=75`, cues at corners `[0,8]`, extra proportion `0.0`) and the `--task vda9` selection that propagates `grid_rows=grid_cols=3, image_size=75` into the model constructor.
- **It IS a 3×3 grid of 9 Gabors.** `envs/base.py:91-93` — `cell_bounds(75,3)` gives row/col edges `[0,25,50,75]`, so nine 25×25 cells, row-major. `envs/base.py:135-141` renders one disc-masked Gabor per cell; `_gabor` (`base.py:165-174`) is the identical Gabor function used at SS4, just tiled 3×3. Each cell is 25×25 px — **the same per-patch pixel size as SS4** (SS4 = 50px/2 = 25px cells; SS9 = 75px/3 = 25px cells). So the SE-ResNet front-end sees an identically-sized patch; only the count and image size grow.
- **Patch/token layout: 9 patches vs 4.** `conv_frontend.py::ConvPatchFrontEnd.__init__` (`conv_frontend.py:94-118`) is grid-parametric: `n_patch = grid_rows*grid_cols` = 9, `pos_dim = n_patch` = 9 (one-hot over 9 positions), `token_dim = 128 + 9 + 8 = 145` (SS4 was `128+4+8 = 140`). Row-major patch boundaries (`conv_frontend.py:105-107`) are computed to match the env cell order, so **token i ⇔ stimulus i** exactly (P0=TL, P2=TR, P4=center, P6=BL, P8=BR). The `forward` (`conv_frontend.py:127-137`) crops the 9 cells, encodes each with the SHARED SE-ResNet, and concatenates `[emb128 ‖ pos9 ‖ temporal8]`.
- **Divergence in the readout width:** the flattened readout is `n_patch * d_mem`. At SS4/d128 that is `4*128 = 512`; at SS9/d128 it is `9*128 = 1152` (`paper_encoder.py:491`, `readout_dim = n_patch * d_mem`). The actor/critic MLP input dims scale accordingly — this is why an SS4 checkpoint cannot be loaded into an SS9 model and vice-versa.
- **Stale-comment trap:** `model.py:1-13`, `conv_frontend.py:5-8/30-34`, and `paper_encoder.py:33` still say "4 patches / N_PATCH=4 / 4×140 / (B,4,4)". These docstrings/module constants are **inherited and NOT authoritative** — `N_PATCH=4` in `conv_frontend.py:30` and `paper_encoder.py:33` are module-level DEFAULTS that are overridden by the constructor args at build time. The live code is fully grid-parametric. Do not trust the "4" in any docstring; trust the constructor path `train_rl.py:144 → task_grid("vda9")=(3,3) → RViTPaperModel(grid_rows=3, grid_cols=3, image_size=75)`.
- **Guard that enforces the divergence:** `model.py:60-62` — the VAE front-end is HARD-REFUSED for any non-(2×2)/non-50px layout; SS9 REQUIRES `--conv-frontend`. There is no VAE path for grid9.

---

## 2. Full architecture with file:line pointers

Data path per online step (`model.py::rl_step`, `model.py:116-132`):

1. **Front-end** `ConvPatchFrontEnd` (`conv_frontend.py:94-137`): 75×75×3 → nine 25×25×3 patches → shared SE-ResNet (`stem` + `SEResBlock` ×3, `conv_frontend.py:109-113`; GroupNorm not BatchNorm because rollout is batch=1, `conv_frontend.py:37-41`; SqueezeExcite `conv_frontend.py:58-70`) → global-avg-pool → **RMSNorm** (no mean-subtract, preserves the colour-DC that carries the VALUE cue, `conv_frontend.py:44-55/115`) → 128-d. Token = `[emb128 ‖ pos9 ‖ temporal8] = 145`. `~594K` front-end params (same order as SS4; SE-ResNet is grid-independent, shared across patches). Temporal one-hot indexes the LOGICAL frame `t // frame_repeat` (`model.py:119`); at SS9 `frame_repeat=1` so logical=physical.
2. **Recurrent ViT** `RecurrentViTxLSTM` (`paper_encoder.py:440-556`), built with `n_patch=9, d_token=145, d_mem=128`:
   - **PRIORITY / feedback attention** — the `--feedback`-selected module (`paper_encoder.py:460-483`). For SS9 the two live variants are `CrossAttentionXH` (`paper_encoder.py:116-142`, selected for `crossattn1`) and `ElementwiseAffineSelfAttention` (`paper_encoder.py:276-317`, selected for `affine_ew`). See §3.
   - **Spatial xLSTM** `SpatialXLSTM` (`paper_encoder.py:368-395`): the paper (H,C,N,M) xLSTM update, per patch, independent; `cell="xlstm"` for both SS9 variants. `d_mem=128`.
   - `crossattn1` is a **single-LSTM** cross-attention (`paper_encoder.py:460-464`): `cross=False`, so the one cell's H feeds BOTH the cross-attention AND the readout. `affine_ew` is likewise single-LSTM (`two_lstm=False`). Neither SS9 variant uses a second xLSTM.
3. **Readout**: flatten `H` (B,9,128) → 1152, `paper_encoder.py:491`.
4. **Heads** `paper_heads.py`: `FFActor` (3× ELU trunk → 2 logits {wait, declare}, `paper_heads.py:24-39`, `init_action_bias=[0.0,-1.5]`) and `QRCritic` (distributional, `n_quantiles=5`, `paper_heads.py:42-65`); `derive_V` = policy-weighted quantile mixture.
5. **V-JEPA head** `JEPAStructuredHead` (`paper_heads.py:68-86`): 4 heads × 256 protos on the xLSTM cell output, per-head softmax; used ONLY for the temporal self-distillation loss (`jepa_center` DINO-centering buffer, `model.py:81-82`; student@t → EMA-teacher@t+1 in `ppo.py`). Does NOT change the memory. `--jepa-coef 0.5`.

Structural differences from the SS4 repo: **none in the .py logic** — same files, same classes. The differences are entirely (a) the env grid (`VDA9Env`), (b) the resulting `n_patch=9 / token_dim=145 / readout=1152`, and (c) the `d_mem=128` default used in every SS9 run (the repo's top-level default is 1024, but every grid9 checkpoint was trained with `--d-mem 128`, and two `_d256` variants exist).

Attention-clamp / causal-perturbation plumbing (needed for the "stimulation" figures) is dispatched to every clamp-applying module at `paper_encoder.py:546-548` — both `CrossAttentionXH` and `ElementwiseAffineSelfAttention` accept `attn_clamp`. For `crossattn1` the clamp keys are **0–8 = image keys, 9–17 = memory keys** (`paper_encoder.py:133-139`); `repro9_core.py:49-56` clamps BOTH the image and memory key for a location (`_loc_keys(18,i)=[i,9+i]`). For `affine_ew` there are only 9 self-attention keys.

---

## 3. `affine_ew` vs `crossattn1` at SS9 (PRIORITY / VALUE)

Both feed the SAME xLSTM and the SAME actor(PRIORITY-driven)/critic(VALUE-driven) heads. They differ ONLY in how memory H enters the ViT — i.e. how PRIORITY is computed:

| | `crossattn1` | `affine_ew` |
|---|---|---|
| module | `CrossAttentionXH` (`paper_encoder.py:116-142`) | `ElementwiseAffineSelfAttention` (`paper_encoder.py:276-317`) |
| memory→attention | `Q=W_q(X)`, `K=[W_kx(X) ‖ W_kh(H)]`, `V=[W_vx(X) ‖ W_vh(H)]` — **9 image + 9 memory keys** (18 total) | `X' = γ(H)⊙X + β(H)` (element-wise vectors, γ init=1, β init=0, NO `1+`), then plain self-attn over 9 tokens |
| attention map shape | (B,9,18) — PRIORITY is legible as memory-key attention | (B,9,9) — PRIORITY is baked into the gate, attention is over 9 self-keys |
| residual | `Z = X + AV` (`paper_encoder.py:141`) | `Z = X + A·V(X')` (`paper_encoder.py:316`) — **X-residual, NOT X'-residual** (see caveat below) |
| dd9 attention keys | `keys=18`, lock read on MEMORY keys `9+i` | `keys=9`, lock read on the (only) self keys `i` |
| character | competitive key/value read → **sharp** cue read (α₁≈0.89) and a memory-side change-lock that is validity-gated | multiplicative gate → **modest** cue read (α₁≈0.18–0.40), bottom-up salience that locks any big Δθ regardless of cue |

**CAVEAT — a manuscript/code mismatch to know:** the repro9 papers describe both variants' residual as `Z=X'+AV` (`paper9_affine_ew.tex:190`) and label `affine_ew` "multiplicative-gating". The code is `Z = X + A·V` where V is computed from the modulated `X'` (`paper_encoder.py:308-316`) — i.e. the residual is the *unmodulated* X, and the gate only affects Q/K/V. This is a wording gap in the paper, not a code bug; if you rebuild figures, cite the code.

Terminology note: the `affine_ew` repro9 paper calls the mechanism "element-wise multiplicative-gating" (its Fig 2 says `X'=γ(H)⊙X+β(H)`). That is `affine_ew`, NOT the paper's original `multiplicative` feedback (`MultiplicativeSelfAttention`, `paper_encoder.py:38-81`), which is a DIFFERENT module not trained at SS9.

---

## 4. Task / env: SS9 change-detection, cue, validity, value, set-size

`VDA9Env` (`envs/tasks.py:44-54`) subclasses `BaseChangeDetectionEnv` (`envs/base.py`):

- **Grid / geometry:** `grid_rows=grid_cols=3`, `image_size=75`; nine 25×25 disc-masked Gabors, row-major (`base.py:91-93`). Cue can appear only at the two corners `cue_positions=[0,8]` (TL=S1, BR=S9) — same corner-cue design as SS4's `[0,3]`.
- **Timeline (paper 7-step, `base.py:124-143`):** t=0 blank · **t=1 cue** (`_render_cue`, `base.py:145-163`, white disc + ring-arc whose completeness = `proportion` = displayed validity; disc/ring coloured by the VALUE cue) · t=2 blank · t=3–6 Gabors with per-frame orientation noise `σ=5` · **change fixed at t=5** (`min=max=5`), Δθ ~ U(−θ,θ), θ starts 65. 50% change trials.
- **VALUE cue:** `value_cues=True` (`tasks.py:52`) → cue disc/ring is RED(=5) / GREEN(=3) / BLUE(=1); reward on a correct response = the colour's value (`base.py:177-181`). VALUE is visible only because the front-end is 3-channel + RMSNorm (no mean-subtract). This is why SS9 uses `vda9` (value-directed) not the uniform-reward `setsize9`.
- **VALIDITY:** ring completeness ∈ `proportions=(0.0, 0.25, 0.5, 0.75, 1.0)` (`tasks.py:53`). **SS9 adds `0.0` = NO ring = uninformative** (not present at SS4's `(0.25,…,1.0)`). On a change trial the change is at the cued cell w.p. `proportion`, else uniform over ALL nine (`base.py:115-121`). So `P(valid|change) = proportion + (1−proportion)/9`; **p=0 ⇒ 1/9 ≈ 0.111 uniform** (the SS9 chance floor, vs SS4's 1/4).
- **Set-size manipulation:** SS9 is the K=9 point of the K∈{2,4,9} family. Note there are TWO ways set size is realized in this repo: (a) `vda9` = value-directed 9-grid (what the SS9 JEPA model is actually trained on), and (b) `setsize9` = uniform-reward 9-grid (`tasks.py:57-69`, `SetSizeEnv._GRIDS[9]=(3,3)`) which is the env used by the *separate* older `RViT_plus_setsize9` v11_part2 experiment (that one COLLAPSED to always-press — do not confuse it with this JEPA model).
- Actions: 0=wait, 1=declare change. Reward: hit (declare at ≥ change) = value; correct-reject (no press by T) = value; premature/FA = 0 (`base.py:188-206`).

---

## 5. Training recipe + curriculum

Same paper harness as SS4 (`ppo.py` = PAC + QR-DQN + PER + EMA target). Config `config/default.json`: lr 3e-4, γ **0.95**, entropy 0.01, PAC bc_alpha 0.1, `ema_decay 0.995` (hard-copy off), PER capacity 1000 / n_replay 4, burn_in 20, `n_quantiles 5`, `episodes_per_iter 8`, `save_every 200`. V-JEPA: `jepa_coef 0.5`, 4 heads × 256 protos, temporal student→EMA-teacher (`jepa_ema_decay 0.996`), τ_student 0.1, τ_teacher 0.04→0.07 over 300 iters, center momentum 0.9.

**Curriculum:** the paper shrinking-θ curriculum EXISTS (`base.py:208-221`: once rolling accuracy ≥0.85 over 1000 trials, drop max|Δθ| by 3° to a floor of 8°) but is **OFF by default** (`train_rl.py:45`, `--curriculum` flag). Every grid9 checkpoint was trained with **curriculum OFF** — `env/theta` stays pinned at 65.0 in all four `metrics.csv` (verified: last rows show `theta=65.0`). So SS9 difficulty is FIXED at θ=65, not annealed.

Canonical SS9 run commands (d128, the trained configuration):
```bash
# crossattn1 (PRIORITY = memory-key reader), d_mem=128
.venv/bin/python RViT_plus_paper_jepa_grid9/train_rl.py --device mps --init-mode fresh \
  --task vda9 --T 7 --min-change-time 5 --max-change-time 5 --cell xlstm \
  --feedback crossattn1 --conv-frontend --jepa-coef 0.5 --d-mem 128 \
  --checkpoint-dir ~/rvit_plus_checkpoints/paper_jepa_grid9

# affine_ew (element-wise memory gate), d_mem=128
.venv/bin/python RViT_plus_paper_jepa_grid9/train_rl.py --device mps --init-mode fresh \
  --task vda9 --T 7 --min-change-time 5 --max-change-time 5 --cell xlstm \
  --feedback affine_ew --conv-frontend --jepa-coef 0.5 --d-mem 128 \
  --checkpoint-dir ~/rvit_plus_checkpoints/paper_jepa_grid9_affine_ew
```
To RESUME instead of restart, swap `--init-mode fresh` → `--init-mode resume` (auto-discovers `rvit_plus_rl_latest.pt` in the ckpt dir, `train_rl.py:194-213`). Note `--task vda9` sets `grid_rows/cols=3, image_size=75` automatically via `task_grid` — do NOT pass grid flags. `--vae-checkpoint` is refused with `--conv-frontend` (`train_rl.py:171-172`).

The d256 variants were run identically with `--d-mem 256 --checkpoint-dir ~/rvit_plus_checkpoints/paper_jepa_grid9{,_affine_ew}_d256`.

---

## 6. Key FINDINGS — the set-size × validity result (VERIFIED against repo9 npz + deepdive9)

Two DISTINCT validity measurements exist at SS9; keep them separate.

### (a) repro9 Fig-4 — α₁ (attention on the cued corner at the change frame) vs DISPLAYED validity, iter 2999

Verified from `repro9/data_fig4_crossattn1.npz` / `data_fig4_affine_ew.npz` (key `a1cue`/`a1unc`, first Δ bin):

- **`crossattn1` grid9 USES validity** — this is the headline "0.12→0.31" claim. α₁ at the change frame grows monotonically with displayed validity: `a1cue` (cued-corner change) `0.127 → 0.133 → 0.226 → 0.294 → 0.298` for val `0.0/0.25/0.5/0.75/1.0`; `a1unc` (uncued-corner change) `0.153 → 0.125 → 0.244 → 0.326 → 0.301`. Roughly **0.12–0.15 at 0% → ~0.30 at 100%** (uniform baseline = 0.111). The repro9 paper (`paper9_crossattn1.tex:73-79`) states this as "α₁ grows ≈0.12→0.31". **This is real and verified**, and it is what makes SS9 crossattn1 different from ALL FOUR SS4 variants (which were validity-INVARIANT in their attention).
- **`affine_ew` grid9 uses validity even MORE strongly**, and its α₁ is Δθ-tuned (change-lock is bottom-up): `a1cue` at DE≈0 grows `0.147 → 0.134 → 0.33 → 0.373 → 0.425` (val 0→1), and — critically — `a1cue` RISES with Δθ (e.g. val 1.0: `0.425 → 0.473 → 0.575 → 0.767 → 0.854 → 0.872 → 0.887` across Δ) while `a1unc` FALLS with Δθ. The repro9 paper (`paper9_affine_ew.tex:79-80`) reports "α₁ 0.15→0.48 from 0%→100%". So affine_ew shows a mild cued-threshold shift AND validity-graded reallocation AND (unlike SS4) causally-live clamps.

Note both variants' **change-location DECODING from the memory `loc__*` is flat at 0.111** in this fig4 npz — that array is the location-decoder chance floor, NOT the attention; do not misread it as "no signal". The attention (`a1*`) is where the validity effect lives.

### (b) deepdive9 change-lock — the SS4-vs-SS9 invalid-cue dissociation (the `project_setsize_invalid_manuscript` result)

This is the sharper, more important finding. Verified from `deepdive9/data_dd9_crossattn1.npz` (iter **4599**) and `data_dd9_affine_ew.npz` (iter **4399**). Change-lock = attention on the CHANGED location at the change frame f5 and f5+1=f6; uniform baseline = 0.111. VALID = change@cued corner, INVALID = change@opposite corner:

- **`crossattn1`: invalid change-lock is ABOLISHED at SS9.** VALID f5=0.80, f6=0.97 (locks hard, memory keys). **INVALID f5=0.03, f6=0.05** — *below* uniform, i.e. the model NEVER re-points onto an uncued change; it stays locked on the (wrong) cued location and goes blind. (Numbers are near-identical at prop 1.0 and prop 0.0, and for both cue corners — robust.)
- **Contrast with SS4** (`RViT_plus_paper_jepa_conv/deepdive/summary_dd2.npz`, per the memory): at SS4 the invalid change-lock RECOVERS one frame late — INVALID f5≈−0.03 (excess), **f6≈+0.70** (reaches the uncued change at f6). So the invalid-cue cost scales from a **recoverable 1-frame delay at SS4** to a **categorical attentional failure at SS9**. This is the central set-size × validity result.
- **`affine_ew` is the CONTROL and is validity-IMMUNE for the lock:** INVALID STILL LOCKS at SS9 — f5=0.72, f6=0.68 (VALID f5=0.84, f6=0.76). Bottom-up salience grabs any large orientation change regardless of the cue, so the catastrophic invalid scaling is SPECIFIC to the top-down cue-gated PRIORITY reader (`crossattn1`) — which is also the mechanism that produces the cueing benefit. This dovetails with (a): affine_ew's α₁ is Δθ-tuned (grabs the change) whereas crossattn1's memory-lock is cue-gated.

Mechanism framing (for the SS9 paper): biased-competition / normalization — more competitors (9 vs 4) means top-down reallocation away from the cued item fails; maps to Posner invalid-cost growing with set size, and to SC/priority-map commitment. Falsifiable prediction: invalid-cue behavioural cost grows with set size (testable in NHP/human covert attention).

### PREDICTIONS vs TRAINED-AND-MEASURED — read this before citing any behavioural number

- **MEASURED (attention, read-only from the frozen model):** everything in (a) and (b) above is attention-map data pulled from checkpoints — these are real measurements. The repro9 full-figure papers (iter 2999) and the deepdive9 change-lock (iter 4399/4599) are attention/decoding measurements.
- **PREDICTION (behaviour):** the large SS9 *behavioural* invalid-cost is a **PREDICTION, not measured data**, in the `setsize_invalid` manuscript. The SS9 valid/invalid behavioural psychometric has NOT been run to convergence. `deepdive9/dd9_psych.py` is the script that WOULD measure it (torch rollouts) but was not run against a converged model.
- **STALE-DATA TRAP (do not step on this):** `RViT_plus_paper_jepa_grid9/analysis/deepdive_out/behavior.npz` (2382 bytes, dated Jun 29) is a **byte-identical inherited copy of the SS4 pipeline's behavior.npz — it is NOT real SS9 behaviour.** Never read it as SS9 data. Verified it still exists on disk.
- **CHECKPOINT-ITER MISMATCH (do not conflate):** the repro9 papers are built at **iter 2999** (matches the CURRENT `paper_jepa_grid9/rvit_plus_rl_latest.pt` and `_affine_ew`, both `iter=2999`). But the **deepdive9 change-lock npz were computed at iter 4599 (cross) / 4399 (affine)** — a LATER checkpoint that has since been overwritten (the live `latest.pt` are back at 2999, because the metrics.csv show the run continuing but the `.pt` you have on disk are the 2999 saves). So the dd9 npz are frozen artifacts of a checkpoint you can no longer reload. If you re-run dd9 against the current `latest.pt` (2999) the numbers will differ slightly. **The dd9 npz remain the source of record for the change-lock claim; do not silently re-measure and assume equivalence.**

### Maturity / where things actually stand (from live metrics.csv, verified)

All four grid9 runs are **mid-training, NOT converged, NOT a ceiling** ([[feedback_report_cumulative_training]], [[feedback_prove_dont_guess]] — judge by rolling behaviour, not the iter field):
- `paper_jepa_grid9` (crossattn1 d128): last logged iter **~3021**, rolling correct **~0.83**, θ pinned 65. (`latest.pt` saved at iter 2999.)
- `paper_jepa_grid9_affine_ew` (affine_ew d128): last iter **~3043**, rolling **~0.84**. (`latest.pt` iter 2999.)
- `paper_jepa_grid9_d256` (crossattn1 d256): last iter **~2077**, rolling **~0.80**. (`latest.pt` iter 1999.)
- `paper_jepa_grid9_affine_ew_d256` (affine_ew d256): last iter **~3323**, rolling **~0.64** (still climbing / noisier). (`latest.pt` iter 3199.)

So SS9 is learning (rolling ~0.80–0.84 for d128, well above the 0.111 chance floor and above the SS9 v11_part2 model that collapsed at chance) but is NOT at the SS4 maturity (~0.86). The repro9 papers correctly frame every figure as "mid-training snapshot, qualitative signatures present."

---

## 7. File map · run commands · checkpoint locations

Repo root: `/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_grid9/`

| file | role |
|---|---|
| `model.py` | `RViTPaperModel` — grid-parametric (`grid_rows/cols/image_size`); enforces conv-frontend for non-2×2 (`:60-62`). Stale "4-patch" docstrings. |
| `conv_frontend.py` | `ConvPatchFrontEnd` SE-ResNet, grid-parametric (`n_patch=rows*cols`, token=`128+n_patch+8`). |
| `paper_encoder.py` | `RecurrentViTxLSTM` + all feedback modules. SS9 uses `CrossAttentionXH` (`:116`) and `ElementwiseAffineSelfAttention` (`:276`). `SpatialXLSTM` (`:368`). |
| `paper_heads.py` | `FFActor`, `QRCritic`, `JEPAStructuredHead`. |
| `ppo.py` | PAC + QR-DQN + PER + EMA + V-JEPA trainer (env-agnostic). |
| `train_rl.py` | one trainer; `--task vda9` → grid (3,3), 75px. |
| `envs/base.py` | `BaseChangeDetectionEnv` (grid-parametric render/reward/curriculum). |
| `envs/tasks.py` | `VDA9Env` (`:44`), `SetSizeEnv` (`:57`), registry via `envs/__init__.py::TASKS`. |
| `config/default.json` | γ 0.95, ema 0.995, jepa knobs, PER. |
| `repro9/` | full-figure reproduction (Figs 1–17) at iter 2999. `repro9_core.py` (loader `:16-22` auto-matches LayerNorm out_norm), `repro9_fig{1..17}.py`, `run9_model.sh` (`SNAP FB LAB`), `run9_supp.sh`, `data_fig*_{crossattn1,affine_ew}.npz`, `paper9_{crossattn1,affine_ew}.tex/.pdf` (compiled). `dose9_uncued.py` + `data_dose_grid9.npz` (uncued dose-response). |
| `deepdive9/` | `dd9_attn.py` (change-lock, source of the SS9 invalid result), `dd9_psych.py` (valid/invalid psychometric — NOT yet run at convergence), `data_dd9_{crossattn1,affine_ew}.npz` (iter 4599/4399), `figs/`. |
| `analysis/` | inherited SS4-shaped deep-dive scripts + `deepdive_out/behavior.npz` **(STALE — do not use)**. |

**Checkpoints** (`~/rvit_plus_checkpoints/`, OUTSIDE the Drive-synced repo):
- `paper_jepa_grid9/rvit_plus_rl_latest.pt` — crossattn1 d128, **iter 2999**, + `metrics.csv` (live to ~3021).
- `paper_jepa_grid9_affine_ew/rvit_plus_rl_latest.pt` — affine_ew d128, **iter 2999**, metrics to ~3043.
- `paper_jepa_grid9_d256/rvit_plus_rl_latest.pt` — crossattn1 d256, **iter 1999**, metrics to ~2077.
- `paper_jepa_grid9_affine_ew_d256/rvit_plus_rl_latest.pt` — affine_ew d256, **iter 3199**, metrics to ~3323.
- Each ckpt dict is `{"iter", "model_state_dict"}` ONLY (no `model_kwargs` in `latest.pt`) — you must reconstruct the model with the exact kwargs (`cell="xlstm", feedback=<fb>, d_mem=128, conv_frontend=True, grid_rows=3, grid_cols=3, image_size=75, jepa_n_heads=4, jepa_proto_dim=256, seq_len=7`) as `repro9_core.py:18-19` / `dd9_attn.py:16-17` do.

**Analysis run commands** (ONE torch job at a time, machine free — see §8):
```bash
# full-figure reproduction (crossattn1 example); LAB is a free label
RViT_plus_paper_jepa_grid9/repro9/run9_model.sh \
  ~/rvit_plus_checkpoints/paper_jepa_grid9/rvit_plus_rl_latest.pt crossattn1 grid9_cross
# change-lock attention (regenerates data_dd9_<fb>.npz + figs)
OMP_NUM_THREADS=3 .venv/bin/python RViT_plus_paper_jepa_grid9/deepdive9/dd9_attn.py \
  ~/rvit_plus_checkpoints/paper_jepa_grid9/rvit_plus_rl_latest.pt crossattn1
# valid/invalid psychometric (turns the SS9 behavioural PREDICTION into data)
OMP_NUM_THREADS=3 .venv/bin/python RViT_plus_paper_jepa_grid9/deepdive9/dd9_psych.py \
  ~/rvit_plus_checkpoints/paper_jepa_grid9/rvit_plus_rl_latest.pt crossattn1
```
`repro9_core.py`/`dd9_*.py` auto-select `mps` and `torch.mps.empty_cache()` after each rollout; `torch.set_num_threads(3)`.

---

## 8. Current operational state / gotchas (same infra caveats as SS4)

- **MPS conv-backward memory leak** ([[reference_torch212_conv_backward_leak]]): torch 2.12 MPS+CPU autograd leaks ∝ conv op count; it bites **end-to-end conv training** (which SS9 IS — the SE-ResNet trains from pixels every step), ~4MB/iter → OOM ~10k iters. This is likely why the grid9 runs are checkpointed at low iters (1999–3199) and appear to have been restarted (the metrics.csv continue past the `latest.pt` iter). Mitigation: batched-patch encode + auto-resume wrapper; **measure current RSS via `ps`, not `ru_maxrss` peak**. Forward-only analysis (repro9/dd9) does NOT trigger the leak (no backward).
- **Laptop CPU cap** ([[feedback_cap_cpu_on_laptop]]): NEVER stack all-core torch jobs; the machine has crashed from this. Hard-cap `OMP_NUM_THREADS=3` / `torch.set_num_threads(3)` (already in every script), ONE job at a time, check `load` first. The dd9/repro9 scripts already honor this.
- **Loader gotcha:** the checkpoints were trained when `front.out_norm` was `LayerNorm`; the current code has `RMSNorm`. `repro9_core.py:20` / `dd9_attn.py:18` / `dd9_psych.py:25` all patch `m.front.out_norm = nn.LayerNorm(128)` when the state-dict contains `front.out_norm.bias`, then assert 0 missing / 0 unexpected. Reuse that pattern for any new SS9 loader or the load will silently drop `out_norm.bias`.
- **Two "setsize9" repos exist — do not confuse:** THIS model (`vda9` JEPA, learning, ~0.83) vs the OLDER `RViT_plus_setsize9/` (v11_part2 cross-talk on uniform-reward `setsize9`, which **COLLAPSED to always-press at chance**, [[project_rvit_plus_setsize9]]). The JEPA/conv front-end is what made SS9 learnable.

---

## What the next agent MUST know

- **The SS9 model is the SS4 conv-JEPA model with the env swapped to a 3×3 / 9-Gabor / 75px `vda9` grid** (one token per Gabor, 9 tokens, token_dim=145, readout=1152). Same `.py`. Do NOT trust the "4-patch" docstrings/`N_PATCH=4` module constants — the code is grid-parametric; the constructor path (`--task vda9 → grid (3,3), 75px`) is authoritative. VAE front-end is hard-refused; SS9 is conv-only.
- **Two live variants, both `cell=xlstm`, `d_mem=128`, single-LSTM:** `crossattn1` (PRIORITY = 9 image + 9 memory keys, legible memory-side change-lock) and `affine_ew` (PRIORITY = element-wise γ⊙X+β gate, bottom-up salience). `affine_ew` in the repo IS the paper's "element-wise multiplicative-gating"; it is NOT the original `multiplicative` module.
- **The headline set-size × validity result (VERIFIED):** invalid-cue change-lock RECOVERS one frame late at SS4 (f6≈+0.70) but is **ABOLISHED at SS9 for `crossattn1`** (INVALID f5=0.03, f6=0.05 ≈ uniform — goes blind to uncued changes). `affine_ew` is the control: INVALID still locks (f5=0.72, f6=0.68) because bottom-up salience is cue-independent. Source: `deepdive9/data_dd9_{crossattn1,affine_ew}.npz`.
- **Separately, `crossattn1` grid9 USES displayed validity** (α₁ at the change frame ≈0.12 at 0% → ≈0.30 at 100%); `affine_ew` uses it even more (≈0.15→0.48) AND its α₁ is Δθ-tuned. This is NEW vs SS4, where all four variants were validity-invariant. Source: `repro9/data_fig4_*.npz` (iter 2999).
- **What is MEASURED vs PREDICTED:** all the above are ATTENTION measurements. The large SS9 *behavioural* invalid-cost is a **PREDICTION** — `dd9_psych.py` exists to measure it but has NOT been run to convergence. The behavioural psychometric is the top TODO once a run converges and the machine is free.
- **Three data traps:** (1) `analysis/deepdive_out/behavior.npz` is a STALE SS4 copy — never read it as SS9. (2) The dd9 change-lock npz are from iter **4599/4399**, but the current `latest.pt` are iter **2999** (crossattn/affine d128) — a checkpoint you can no longer reload; treat the npz as the frozen record. (3) The repro9 papers are iter 2999. Everything is **mid-training, not a ceiling** — judge by live rolling correct (~0.80–0.84 d128), not the iter field.
- **Infra:** end-to-end conv training triggers the torch-2.12 MPS conv-backward leak (measure RSS via `ps`, expect restarts ~few-k iters). Forward-only analysis is safe. ONE capped torch job at a time; scripts already set `threads=3` + `mps.empty_cache()`. Loader must patch `out_norm → LayerNorm(128)` before `load_state_dict`.
