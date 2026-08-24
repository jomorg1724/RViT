# RViT+ FiLM — battery reproduction scaffold

One canonical architecture, one harness, every environment we need to (re)train for the
paper — all standardized on a **stable, neuroscientifically-plausible FiLM** memory
feedback. Built 2026-06-21.

## What this is

The published model's memory→attention feedback is multiplicative (`Q = X·W ⊙ H·W`),
which can be unstable, and the "naive broadcast" variant (a product `Π(1+gate)` over many
terms) explodes. This directory standardizes on the **FiLM form** — a *single*
multiplicative gain gate with the top-down projection **zero-initialised**:

```
Q = W_XQ(X) ⊙ (1 + W_HQ(H1))      # queries: FiLM-gated by the feedback memory H1
K = W_XK(X) ⊙ (1 + W_HK(H1))      # keys: same (W_HQ, W_HK ZERO-init ⇒ gate=1 at init)
Q, K ← LayerNorm                  # keep logits bounded before softmax
V = W_V(H2)                        # values come from the DEEP memory H2
Z = W_reduce( concat[X, softmax(QKᵀ/√d)·V] ) + FFN     # X = residual via CONCAT-then-project
H1 = LSTM1(Z) ;  H2 = LSTM2(Z)     # both memories updated from Z
actor, critic  read  Z             # Z drives both LSTMs and both heads
```

The single multiplicative gain gate `(1 + W_H·H1)` with zero-init top-down is stable
(feedback OFF at init, no explosion — unlike the `Π(1+gate)` broadcast) and is the
biologically-grounded reading (Reynolds–Heeger multiplicative attentional gain). The roles
are clean: **H1** (short-term feedback) gain-modulates the query/key matching; **H2** (deep
memory) supplies the attended *content* (the values); **X** is the bottom-up residual,
combined with the attention output by a learned concat-projection; and the integrated
output **Z** updates both memories and feeds the policy/value heads. `--readout {Z|H1|H2}`
can instead expose a memory for ablation (default Z). The dual-stream split,
cross-attention, broadcast-product, and VQ-codebook variants are deliberately **not** here.

## Front-end: straight pixels → linear → transformer (no conv)

The default is a **pixel** patch-embed (`front_end.py`): crop one cell per stimulus,
flatten the RAW pixels, linearly project to `d_model`, add a positional embedding — the
standard ViT patch embedding, **no convolution**.

- An earlier conv front-end pooled each patch 24→12→2×2 with RL-only training (no
  reconstruction pressure) and discarded the subtle orientation-change signal — the model
  learned to *press* but never *when*, and collapsed to premature pressing.
- Straight pixels keep the full signal; the linear map can realise an oriented-filter bank
  and the transformer + LSTM do the rest.
- One front-end covers the whole battery (K=2/4/9, Luo–Maunsell, Krauzlis); a per-cell
  resize to a canonical square keeps the flattened dim fixed across grid geometries.

`--front-end conv|mlp` remain as alternatives, and `front_end.py` keeps a `vae_frozen`
stub for exact paper-faithful reproduction if pixels prove insufficient.

**One token per stimulus.** The image is split into the stimulus grid (2×2, 3×3, 1×2…),
one token per cell, so the attention map is a clean K-token array that is directly
interpretable **and** directly manipulable for causal-perturbation experiments — the
property James wants (vs the 100-token 10×10 grid he flagged as un-manipulable).

## Layout

```
RViT_plus_battery/
  front_end.py   ConvPatchFrontEnd (default) / MLP / vae_frozen stub
  encoder.py     SingleStreamFiLMEncoder + FiLMBlock (+ attn_clamp perturbation hook)
  model.py       RViTPlusModel (harness-compatible: init_states/rl_step/forward_rl_sequence)
  decoder.py     actor/critic 1D-conv heads        (reused from the working harness)
  ppo.py         PER + PAC + QR-DQN trainer         (reused)
  config/        loader.py + default.json
  train_rl.py    --task selects env + grid; one trainer for all tasks
  envs/          base.py + tasks.py + registry (TASKS / make_env / task_grid)
  analysis/      common.py, e5_validity_breakdown.py, e6_attention_maps.py
  tests/         test_film.py (9 checks, all green)
```

## Task timeline (paper 7-step)

All tasks use the published **7-step** structure: t=0 black · t=1 cue · t=2 black · t=3–6
stimuli · **change fixed at t=5**, noise σ=5. Override with `--T --min-change-time
--max-change-time --noise` (e.g. the longer random-onset variant `--T 29 --min-change-time
11 --max-change-time 25`). A curriculum shrinks the max orientation change Δ (`env.theta`)
×0.9 once rolling accuracy clears 85% over 200 trials.

## Environments (the battery)

| task | env | grid | reward | purpose |
|---|---|---|---|---|
| `validity4` | Validity4Env | 2×2 | uniform | canonical published main result |
| `vda4` | VDAEnv | 2×2 | coloured value cue | value-directed attention |
| `setsize2/4/9` | SetSizeEnv | 1×2 / 2×2 / 3×3 | uniform | set-size manipulation (K-scaling) |
| `luo_maunsell_sensitivity` | LuoMaunsellEnv | 2×2 | value at one location | sensitivity-session reward structure |
| `luo_maunsell_criterion` | LuoMaunsellEnv | 2×2 | hit↔CR ratio | criterion-session reward structure |
| `krauzlis` | KrauzlisEnv | 2×2 | cued-only reportable | attend-here/ignore-here (∂EV/∂HR_uncued=0) |

## Run

Train (one task at a time — the laptop must not be over-subscribed; checkpoints go to
`~/rvit_plus_checkpoints/film_<task>/` by default):

```bash
.venv/bin/python RViT_plus_battery/train_rl.py --task validity4 --iters 15000 --device mps
.venv/bin/python RViT_plus_battery/train_rl.py --task krauzlis  --iters 15000 --device mps
.venv/bin/python RViT_plus_battery/train_rl.py --task setsize9  --iters 15000 --device mps
```

Analysis (E5 = per-validity breakdown; E6 = fixed attention-map viz + fixed-change-time
ramp). **Run only when training jobs are stopped** (these load a model and roll out):

```bash
python RViT_plus_battery/analysis/e5_validity_breakdown.py --checkpoint <ckpt> --task validity4 --out reports/e5_validity4.csv
python RViT_plus_battery/analysis/e6_attention_maps.py     --checkpoint <ckpt> --task validity4 --fixed-change-time 18 --out reports/e6_validity4
```

## Status

All 9 sanity tests pass; the full PAC+QR-DQN+PER loop runs end-to-end with the FiLM model
(verified 2-iter on CPU). **Nothing has been trained yet** — these are prepared, ready to
launch. Default hyperparameters mirror the working v11_part2 harness (lr 3e-4, γ 0.99,
entropy 0.01, PAC η 0.1, target update 100, PER capacity 200 / n_replay 4).

Recommended first runs to reproduce the paper on FiLM: `validity4` (the main result),
then `krauzlis` and `luo_maunsell_*` (the battery that answers the "limited in scope"
reviewers), then `setsize{2,4,9}` for the set-size scaling.
