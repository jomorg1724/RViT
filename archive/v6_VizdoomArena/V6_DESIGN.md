# V6 — Multi-Layer Feedback Transformer for ViZDoom Deathmatch ("Arena")

**Status:** designed + implemented 2026-06-09. Target platform: MacBook Pro, MPS GPU.

## Goal

A novel **multi-layer feedback transformer** that learns the ViZDoom
`deathmatch` scenario (the "arena": a large room, monsters spawn continuously,
weapons/ammo/medkits scattered around the perimeter, +1 frag per kill, 4200-tic
episodes, skill 3) — built from the ingredients this repo has shown to actually
work, with **interpretable, causally manipulable attention** as a first-class
design constraint.

## What carried over (the proven core)

From the v5 / v5_part2 successes (and the user's explicit attribution):

1. **Prioritized episode/segment replay** (Schaul 2016) — priority = mean
   per-step quantile-Huber error, ∝ p^α sampling, IS-weight correction β→1.
2. **The exact RL algorithm** — PAC (Perceiver-Actor-Critic, Springenberg et
   al. 2024): closed-form discrete MPO E-step against a lagged reference policy
   + behavioral-cloning blend, driven directly by a **distributional QR-DQN
   critic** (51 quantiles, quantile-Huber, expected-SARSA V with stop-grad π).
   No PPO surrogate, no GAE.
3. **Target network** — v5 hard-copied θ→θ′ every 100 steps; v6 uses the
   smoother **EMA/Polyak form** (θ′ ← (1−τ)θ′ + τθ after every optimizer step,
   τ=0.01 ⇒ ~100-step time constant, same lag scale as v5). The target provides
   BOTH the critic's TD bootstrap and the MPO E-step reference policy π_θ′.
4. **Memory-as-tokens cross-attention** — v5_part2's encoder attention over
   memory tokens was the *causally decision-moving* pathway (|Δhit|=0.12);
   v5's layer-wise hierarchical LSTM memories produced the cleanest emergent
   attention semantics (L1 = top-down orienter, L2 = temporal monitor).
5. **Conv-free patchify** (reshape + per-patch MLP), per-token LSTM memory,
   transformer decoders with CLS readout, small-init output heads, entropy
   0.01 / γ 0.99, Adam 3e-4 + two-stage grad clipping.

## The novel encoder: hierarchical cross-attention feedback (`encoder.py`)

v5 self-attends over the full `[patch ++ H₁ ++ H₂]` (3N×3N, then slices);
v5_part2 cross-attends once and feeds two *stacked* LSTMs from a single block.
**V6 combines them**: a stack of L cross-attention layers, each with **its own
token-memory**, plus a new third token source — **game-state tokens**:

```
per frame t, per layer ℓ = 1..L:
    state_toks = [vitals | weapon | last-action]  embeddings    (S=3 tokens)
    K/V_ℓ  =  [ X_ℓ  ++  H₁..H_L (+pos+tag)  ++  state_toks ]   (N·(1+L)+S keys)
    Z_ℓ    =  CrossAttnBlock_ℓ( Q = X_ℓ,  KV = K/V_ℓ )          (N queries → N outputs)
    H_ℓ,C_ℓ ← LSTMCell_ℓ( Z_ℓ, (H_ℓ, C_ℓ) )                     per-token memory write
    X_{ℓ+1} = Z_ℓ                                               hierarchy
```

- **Multi-layer feedback**: every layer reads ALL layers' memories (earlier
  layers' already this-frame-updated, later layers' previous-frame — exactly
  v5's hierarchical update order), so feedback is both lateral and top-down.
- **Perceiver-style cost**: only N queries (48 for the 6×8 patch grid), so
  attention is N×(N(1+L)+S) instead of v5's (3N)². MPS-friendly.
- **Game-state tokens** are K/V-only (never queried, no recurrence): three
  semantically fixed tokens — vitals (health, armor), weapon (selected weapon
  one-hot + ammo), last action. Attention to them is directly readable
  ("checks ammo before switching weapon", "monitors health when hurt").

### Interpretability is structural, not post-hoc

- `forward_step(..., return_attn=True)` returns per-layer maps
  `(B, heads, N, N(1+L)+S)` with a documented, named **key layout**
  (`encoder.key_layout()` → `{"patch": …, "H1": …, "H2": …, "vitals": …}`).
  Each query is a patch with a known image position (row-major 6×8 grid over
  the 60×80 frame), so maps overlay directly onto pixels.
- **Causal manipulation is built into the forward pass**: every attention call
  (encoder layers AND both decoders) accepts an additive pre-softmax bias
  (`attn_bias`), implemented through `nn.MultiheadAttention`'s float
  `attn_mask` — the *faithful* mechanism of v5's deep-dive `dd_core`, but native
  to the model instead of a re-implementation. Bias a key group up/down and
  measure Δpolicy/ΔQ with zero code surgery.
- The ViZDoom **labels buffer** gives per-object bounding boxes, so
  `analysis/attention_maps.py` computes a quantitative
  *attention-on-enemies / on-items / on-background* decomposition every frame,
  plus the causal experiment (boost/suppress enemy-patch keys → measure
  Δp(ATTACK), ΔQ) automatically.

## Decoders (`decoder.py`)

Both heads read the concatenation of all L memories `[CLS ++ H₁ ++ … ++ H_L]`
(1+L·N tokens) through a 2-layer pre-norm transformer (attention exposed +
bias-injectable, same as the encoder), CLS → ≥2-layer MLP head:

- **Actor** → logits `(B, A)`.
- **Critic** → `(B, A, n_quantiles)` in a **single pass** (the CLS readout maps
  to A×51 outputs). v5's per-action input-encoding critic re-ran the decoder
  once per action — fine for A=2, a 14× cost at A=14, so v6 trades it away.
  PAC only needs Q̄(s,·) per action; how Q is parameterized is orthogonal.
- `derive_V`: expected-SARSA V_dist = Σ_a sg[π(a|s)]·Q(s,a,:) — unchanged.

## Environment (`env.py`)

`deathmatch.cfg` (the arena), frame-skip 4, `RES_160X120` CRCGCB → 2×2 average
pool → **(3, 60, 80) uint8**, patchified at 10 px → 48 tokens. 14 discrete
button combos (noop / attack / forward / forward+attack / turns / forward+turns
/ strafes / backward / attack+turns / next-weapon). Feature vector (25-d):
health, armor, ammo (normalized) + weapon one-hot(8) + last-action one-hot(14).

Reward shaping from game-variable deltas (all weights in config):
`+1.0·Δkills  +0.01·Δdamage_dealt  −0.005·Δdamage_taken  −1.0·death`.
Frags remain the headline metric; shaping only densifies credit. Auto-reset on
done; completed-episode stats (frags, shaped return, length) ride on `info`.

## Trainer (`trainer.py`) — what changed vs. v5's `ppo.py` and why

Arena episodes are ~1050 steps (4200 tics / skip 4); v5's
full-episode-BPTT update (T=29) cannot scale to that. v6 therefore trains on
**fixed-length segments** (R2D2, Kapturov et al. 2019):

- The collector runs ONE persistent env, carries the recurrent state across
  segment boundaries, and stores each segment with its **initial recurrent
  state** (stored-state strategy) + T+1 frames (the extra frame feeds the
  bootstrap). Episode ends inside a segment → done flag + state reset to the
  learned H₀ (both at collection and re-encode time).
- **PER at segment granularity** — same priority/IS math as v5, segment instead
  of episode.
- **Replay burn-in** (default 8 steps): the first steps of each re-encoded
  segment are excluded from every loss and from priorities — they only warm the
  recurrent state from the (slightly stale) stored init.
- **n-step distributional targets** (default n=3, config `n_step`; n=1
  recovers v5's exact form): G⁽ᵏ⁾_t = r_t + γ(1−d_t)·G⁽ᵏ⁻¹⁾_{t+1}, V from the
  EMA target net. Standard for sparse-ish rewards (R2D2 uses n=5).
- **EMA target** after every optimizer step (see above).
- **Warmup phase** (replaces v5's force-wait burn-in): first `warmup_iters`
  iterations collect with a uniform-random policy and train the critic only
  (actor frozen) — fills the buffer and settles the value scale before the
  policy moves.

Everything else — the MPO E-step / BC blend, quantile-Huber, masked weighted
means, priority refresh, two-stage gradient clipping, NaN-guard skip — is the
v5 trainer verbatim.

## Defaults (≈1.8 M params)

`d_model=d_mem=128`, `enc_heads=8` (16-d heads, the v5_part2 choice),
`enc_layers=2`, `dec_heads=8`, `dec_layers=2`, `n_quantiles=51`, `drop=0.1`,
`seg_len=64`, `segments_per_iter=4` (+`per_n_replay=4` replay), `n_epochs=1`,
`lr=3e-4`, `γ=0.99`, `entropy=0.01`, `η=0.1`, `bc_α=0.1`, `ema_τ=0.01`,
buffer 512 segments (uint8 frames ≈ 0.5 GB RAM).

Checkpoints go to `~/rvit_plus_checkpoints/v6_vizdoom_arena/` — **outside** the
Drive-synced repo (Drive was observed corrupting live checkpoints; same policy
as v5).

## Run-1 postmortem (2026-06-10) — wall-shooting collapse, diagnosed & fixed

Run 1 (15.5k iters, ~4M env steps) converged to a degenerate "walk forward,
spin left, hold the trigger" policy: 3 of 14 actions carried all probability,
only 33.7% of trigger-pulls had a monster visible, kills stayed at the random
baseline while entropy collapsed 2.64 → 0.3. Two verified root causes:

1. **The kill reward was never contingent on the agent.** `KILLCOUNT` is the
   GLOBAL map kill tally: a pure-noop policy "earns" 1.017 kills/episode from
   monster infighting (60-episode test, `HITCOUNT==0` asserted throughout).
   "Shoot a wall" and "hunt monsters" scored identically, so there was no
   gradient between them; the only player-attributed term (damage, 0.01/hp)
   was 100× weaker. *Fix:* kill bonus gated on same-step ΔDAMAGECOUNT/ΔHITCOUNT
   (player-attributed — both verified 0 vs walls and under noop), damage →
   0.02/hp, +0.5/hit landed, −0.01/round fired (wall-spray now strictly
   negative), +0.01/HP from medkits. KILLCOUNT stays a *metric* only.
2. **The MPO E-step reference is the EMA of the policy being trained** —
   a positive-feedback loop: π_ref chases π, compounding any tiny persistent
   Q-edge into full collapse. Faithful simulation: η=0.1 → entropy 2.64→0.003
   on a 0.05 Q-edge (even with bc_α=0); η=1.0 → stable. entropy_coef=0.01 was
   10–100× too weak; BC self-imitation amplified it. *Fix:* η → 1.0, reference
   mixed with 5% uniform (can never zero-out an action — breaks the loop at
   the source), entropy_coef → 0.1, bc_α → 0.05, plus a 5% ε-uniform floor
   during collection so the replay distribution can't collapse either.

Also removed: the `next_weapon` action (one press strands the agent on the
0-ammo fist — verified irreversible with only fist+pistol owned; weapon
upgrades happen via the engine's auto-switch-on-pickup), so **A=13**. Reward
bookkeeping itself audited clean (deltas across auto-reset, n-step done
handling, PER priority slicing all verified correct). Run 2 restarts FRESH —
the collapsed checkpoint's reference policy and KILLCOUNT-trained quantiles
would actively fight the corrected objective. Leading health indicators for
run 2: entropy stabilizing >1.5 early, kills/ep vs the 1.0 noop-infight
baseline, fraction of trigger-pulls with a monster visible vs 33.7%.

## Running

```bash
.venv/bin/python -m v6_VizdoomArena.tests.test_v6        # unit + smoke tests
.venv/bin/python v6_VizdoomArena/train_rl.py             # train (auto-selects MPS)
.venv/bin/python v6_VizdoomArena/train_rl.py --iters 200 --device cpu   # quick check
.venv/bin/python v6_VizdoomArena/analysis/attention_maps.py \
    --checkpoint ~/rvit_plus_checkpoints/v6_vizdoom_arena/v6_latest.pt  # overlays + enemy-attention + causal probe
```
