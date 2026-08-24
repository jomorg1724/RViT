# ConvMGU — perceptual ("visual-cortex") recurrence in the conv front-end

A conv-format recurrent cell inserted into `ConvPatchFrontEnd`, adding a FAST, short-timescale recurrence to
the perceptual stage — distinct from the slow xLSTM working memory downstream. Enabled with
`--conv-frontend --conv-recurrent` (motion variant; d_mem=128, affine_ew).

## What it is
- **Cell = ConvMGU** (single-gate Minimal Gated Unit — simpler than an LSTM/ConvGRU; one gate to bias):
  - `f    = σ(W_f·x + U_f·H_prev)` — retention gate (fraction of PAST kept)
  - `cand = tanh(GroupNorm(W_h·x + U_h·(f⊙H_prev)))` — bounded candidate (|cand|≤1 ⇒ state stays bounded)
  - `H    = f⊙H_prev + (1−f)⊙cand` — leaky integrate
  - all convs 3×3 (spatial recurrent interaction — needed so a moving Gabor's frame-to-frame displacement
    is representable; 1×1 would kill the motion signal).
- **Biased HIGH decay:** `W_f.bias = logit(retain)` (default retain=0.30 → bias=−0.8473); gate conv weights
  zero-init so at t=0 `f ≡ σ(bias) = retain` data-independently. e-fold τ≈0.83 frames — the state is the
  current frame + ~one integrated past step. The gate weights receive gradient, so the cell can LEARN a
  longer time constant if the task rewards it; only the START is biased short.
- **Insertion:** after **stage1** (64ch, 13×13). Run ConvMGU on the stage1 map → `concat([feat‖H])` = 128ch →
  1×1 `conv_reduce` back to 64ch → continue stage2/stage3/pool. Shared cell across the 4 patches; per-patch
  STATE (patches folded into batch B*4 for one conv call). `--conv-rec-stage 2` = after stage2 (128ch, 7×7).
- **State threading:** the model state tuple `(enc_state, t)` → `(enc_state, t, conv_state)`; reset per
  episode (zero at t=0) in `forward_rl_sequence`/`recon_loss`; carried opaquely by `ppo.py`. Stateless path
  (`conv_recurrent=False`) is byte-identical — existing VDA/motion checkpoints reload unchanged. +156k params.

## Why (literature) — fast recurrence in the visual cortex
Primate object vision is not a single feedforward sweep: a fast feedforward pass is followed by fast
intra-areal + feedback **recurrent** processing over the next tens of ms that refines ambiguous/challenging
images (Lamme & Roelfsema 2000; Lamme 1995). This late processing is temporally **fast and short-ranged**:
behaviorally-sufficient IT solutions for hard images arrive only ~30 ms later than easy ones, and silencing a
fast recurrent node (vlPFC) selectively abolishes the late-phase code, reverting IT/behavior to a
feedforward-only prediction (Kar et al. 2019; Kar & DiCarlo 2020). Recurrence buys effective depth in **time**
rather than parameters: shallow recurrent CNNs predict late IT as well as very-deep feedforward nets, and
compact ConvRNN/CORnet circuits are the leading brain-predictive models of ventral-stream dynamics
(Kietzmann et al. 2019; Spoerer et al. 2017; Kubilius et al. 2019 CORnet; Nayebi et al. 2022). We take this
literally: move a second recurrence out of token/working-memory space and INTO the convolutional front-end as
a lightweight ConvGRU maintaining a conv-format state `H_conv (n_patch×C×H×W)`, folded back via concat+reduce
exactly as compact RCNNs do. The **high-decay (~1-step) bias** models the "one or two extra recurrent
iterations" benefit rather than sustained maintenance, dissociating this FAST perceptual recurrence from the
slow xLSTM working memory downstream — two anatomically/temporally distinct recurrent processes, not a
redundant copy of one.

**Citations:** Lamme & Roelfsema (2000) TINS; Lamme (1995) J Neurosci; Kar et al. (2019) Nat Neurosci;
Kar & DiCarlo (2020) Neuron; Kietzmann et al. (2019) PNAS; Spoerer, McClure & Kriegeskorte (2017) Front
Psychol; Kubilius et al. (2019) NeurIPS (CORnet); Nayebi et al. (2022) Neural Comput; van Bergen &
Kriegeskorte (2020) Curr Opin Neurobiol.

## Run (later GPU piece — motion, MPS 3000-iter bursts)
Same as the affine motion burst, adding `--conv-frontend --conv-recurrent` (retain default 0.30):
`... python train_rl.py --task motion_zk --conv-frontend --conv-recurrent --feedback affine_ew --two-lstm --d-mem 128 ...`
Verified: `python test_convmgu.py` → 25/25 (shapes, retention=0.30 exact, bounded state, BPTT, JEPA+two_lstm,
guard, param delta).
