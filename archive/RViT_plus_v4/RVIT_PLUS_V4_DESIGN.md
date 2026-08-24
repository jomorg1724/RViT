# RViT+ v4 — conv-free, RL-only design

**Status:** implemented + smoke-validated 2026-06-03. Fresh-init only (no v3
checkpoint is loadable — the architectures share no tensor names).

## Motivation

v1–v3 built perception from a convolutional V1 stem plus convolutional
descend/ascend pyramids between three spatial memory layers, with several
self-supervised auxiliaries (video reconstruction, then cosine predictive
coding, then discrete JEPA / DreamerV3 latents). v4 takes the opposite bet:
**drop every convolution and every non-RL objective**, and test whether a pure
patch-token + recurrent-attention model, trained from reward alone, learns the
Posner change-detection task.

What stays is exactly the RL machinery that was working in v3:

- **PAC actor loss** (MPO E-step + behavioral cloning) — replaces the PPO surrogate.
- **Distributional QR-DQN critic** (quantile-Huber on the executed action).
- **Prioritized episode replay** (episode-level PER with IS-weight correction).

## Architecture

```
frame x_t  (B, 3, 50, 50)
   │
   │  PatchEmbed         reshape into 10×10 patches of 5×5 px, flatten (→75 dims),
   ▼                     per-patch MLP Linear→GELU→Linear→LayerNorm (75→128→d_model),
   │                     (NO Conv2d anywhere)
tokens  (B, 100, d_model)  + learned positional embedding
   │
   │  FeedbackTransformerEncoder.forward_step   (2 layers, persistent memory)
   ▼
   ├─ layer 1: FiLM-modulated self-attn over 100 tokens, memory H₁ steers Q/K/V,
   │           LSTMCell updates H₁,C₁           → recurrent state H₁ (B,100,d_mem)
   └─ layer 2: same, consuming layer-1 output    → recurrent state H₂ (B,100,d_mem)
        │
        │  concat([H₁, H₂])  →  (B, 200, d_mem)   ("both recurrent states")
        │  + decoder positional embedding
        │  prepend a learned CLS token →  (B, 201, d_mem)
        ▼
   ┌─ ActorDecoder   : 2-layer TransformerEncoder, read CLS → Linear → (B, n_actions)
   └─ CriticDecoder  : 2-layer TransformerEncoder, read CLS → Linear → (B, n_actions, n_quantiles)
                       V derived from Q and π by expected SARSA, stop-grad on π
```

The recurrent memory `(H₁,C₁,H₂,C₂)` persists across the episode's frames; the
caller carries it through `rl_step` (online) or it is looped inside
`forward_rl_sequence` (update). On the first frame the **learned initial memory
H0 already modulates attention**, so top-down feedback is active from t=0
(thereafter it carries the previous frame's state).

### The feedback transformer block (`feedback_transformer.py`)

A direct adaptation of Jonathan's `RecBlock` / `FeedbackTransformer` from
`PalladioWikiMCP/habit_formation/sequence_models/feedback_model.py`. Per layer,
per frame:

```
Q = g_q(W_qh·H)·(W_qx·LN(X)) + b_q(W_qh·H)      # FiLM: memory modulates the query
K = g_k(W_kh·H)·(W_kx·LN(X)) + b_k(W_kh·H)      #   "      "        "    the key
V = g_v(W_vh·H)·(W_vx·LN(X)) + b_v(W_vh·H)      #   "      "        "    the value
Z = X + Out(MHSA(Q,K,V)) ;  Z = Z + FFN(LN(Z))  # standard transformer residuals
H,C ← LSTMCell(Z, (H,C))                         # one shared cell over all 100 rows
```

The FiLM gate (`g·proj + b`) is how carried memory **steers** the current
frame's attention — the multiplicative term is the cheap sign-flip / gain
control the program's `concepts/feedback_transformer.md` motivates (Larkum
apical modulation / Reynolds–Heeger gain). `d_model == d_mem == 128` by default
so the projections line up cleanly. `n_FR` inner iterations per frame default to
1 (one pass; Palladio behavior).

### The decoders (`decoder.py`)

Both heads subclass one `_TwoLayerTransformerDecoder` body and are instantiated
**twice as separate-weight modules** — exactly the `mk_tx(); mk_tx()` pattern in
Palladio's `FBT_AC`. Each ingests the concatenation of both recurrent states
(`2 × n_tokens` content tokens), adds a positional embedding (position alone
encodes both source layer and patch index), prepends a CLS token, runs a 2-layer
`nn.TransformerEncoder`, and reads its scalar output off the CLS position. The
critic keeps `taus` and `derive_V` so `ppo.py` is unchanged from its v3 form.

## What was removed vs. kept

| Removed (v3 → gone in v4)              | Kept (RL machinery, verbatim)            |
|----------------------------------------|------------------------------------------|
| `V1Stem` conv stem                     | PAC actor loss (MPO E-step + BC)         |
| conv descend/ascend pyramids           | QR-DQN distributional critic + quantile-Huber |
| `RViTPlusVideoDecoder` + recon loss    | Prioritized episode replay (PER) + IS weights |
| `VAELatentSampler` / KL                | `derive_V` expected-SARSA, stop-grad π   |
| predictive-coding / discrete-JEPA heads| `init_action_bias`, advantage-free actor |
| `split_c3` C₃ specialists, recon pretrain | 1-step distributional TD target        |

## Experiential supervised-contrastive auxiliary (`ppo.py` + `model.py`)

Added 2026-06-05. A SupCon (Khosla et al. 2020, the L_out^sup form) auxiliary that
shapes the recurrent states by **experiential outcome** — the only non-RL signal
in v4, but it is reward/action-derived, not self-supervised. Refs cached in
`refs/` (SupCon `2004.11362`, CPC `1807.03748`); the in-repo precedent is
`RViT_plus/ppo.py::_actor_contrastive` (same env, same `(action, reward)` labels),
and the design echoes Palladio's BC-FBT journey-matching (trial-level, outcome-aware).

- **What is contrasted.** Each episode's **terminal** recurrent state `Hℓ` (last
  valid step, token-mean-pooled) → a per-layer projection head (`Linear→GELU→Linear`,
  L2-normalized, discarded at inference) → embedding `zℓ`. Applied to **both** H₁
  and H₂ (one head each).
- **The experiential label.** The trial's outcome class from `(terminal action,
  reward)`: default `action × reward-sign` → 4 classes (hit / miss / false-alarm /
  correct-reject); `--contrastive-reward-magnitude` uses reward value `{0,1,3,5}`
  (cue colour) → up to 8 classes. (In this env the action *sequence* is waits-then-
  optional-press, so the terminal action + episode length capture it; press-latency
  can be folded into the label — see `_experiential_labels`.)
- **The loss.** `supcon_loss` = L_out^sup: pull same-outcome trials' `zℓ` together,
  push different-outcome apart, summed over the two layers, weighted by
  `contrastive_coef` (default 0.1), τ=0.1. Gradient flows the experiential force
  into the encoder; anchors with no in-batch positive are skipped.
- **Disable** with `--no-contrastive` (drops the heads) or `--contrastive-coef 0`
  (keeps heads, zero loss).

## PAC target network (`ppo.py`)

Added 2026-06-06 — this was specified in PAC (*Offline Actor-Critic RL Scales*,
Springenberg et al. 2024, §3.2) from the start and had been omitted; it is the
main stabilizer for the bootstrapped actor-critic. A time-lagged copy θ′ is kept
(trainer-owned — `copy.deepcopy(model)`, frozen; **not** in the model's
`state_dict`), hard-copied from θ every `target_update_period` optimizer steps
(default 100; `0` disables → old online bootstrap). θ′ feeds **both**:

- **the critic's distributional TD target** — `target_q = r + γ·V_dist_{θ′}(s′)`
  (the bootstrap distribution no longer moves every step), and
- **the MPO E-step reference policy** — `q(a|s) = softmax_a[ log π_θ′(a|s) +
  Q̄(s,a)/η ]` (PAC: "the target policy π_θ′ … as the reference policy"). With a
  stable lagged reference the improved policy stops chasing the online policy's
  own tail.

Side benefit: using π_θ′ as the reference removed the old `n_actions == 2`
restriction (the E-step no longer reconstructs π_old from a stored scalar), so
the actor loss is now general over the action count. The target is rebuilt fresh
on resume (resume is weight-only regardless).

## Key design decisions (and where to change them)

1. **Patch grid = 10×10 (patch_size 5, 100 tokens).** 50 isn't divisible by 16,
   so a literal "16×16 grid" can't tile the image. `patch_size ∈ {1,2,5,10,25,50}`
   divides 50; 5 is the cleanest fine grid and aligns with the env's 2×2 Gabor
   quadrants (each quadrant = a 5×5 patch block). Change with `--patch-size`.
2. **Decoder reads the memory hidden states H₁,H₂** (not the per-frame token
   outputs Z) — the H's are what *recur* across frames, matching "the recurrent
   states should have n_tokens tokens." 2 layers → 2 states → `2·n_tokens` input.
3. **Actor and critic decoders are separate-weight, same-architecture.** This
   follows the Palladio reference. If "the same decoder for the actor" was meant
   as *shared weights*, that is a small refactor (split the body into one shared
   module with two output heads) — flagged here, not yet done.
4. **No recon pretrain.** v3 forced action=0 for N iters to warm the encoder on
   the reconstruction loss; v4 has no self-supervised signal, so it learns from
   reward immediately. `init_action_bias=[0,-1.5]` keeps early episodes long
   enough (P(press)≈0.18) to generate signal.

## Running

```bash
# smoke tests (shapes → rl_step → ppo_update → end-to-end train w/ PER):
.venv/bin/python -m RViT_plus_v4.tests.test_v4

# train (config: RViT_plus_v4/config/rvit_plus_config.json):
.venv/bin/python RViT_plus_v4/train_rl.py                      # full 2000-iter run
.venv/bin/python RViT_plus_v4/train_rl.py --iters 500 --device mps
```

Checkpoints are written to `~/rvit_plus_checkpoints/v4` (**outside** the repo) —
the AttentionManuscript repo is a Google Drive sync root and Drive was observed
rewriting checkpoints mid-run, which can corrupt them. Copy a final checkpoint
back in manually if you want it backed up, but never during a live run.

## Default model size

`d_model=d_mem=128`, `enc_heads=dec_heads=4`, `enc_layers=dec_layers=2`,
`n_quantiles=51`, `contrastive_dim=128` → **~1.97M trainable params**; ~8.5 s/iter on CPU for
8 fresh + 4 replay episodes × 4 epochs (faster on MPS).
