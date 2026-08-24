# Affine + dual-xLSTM paper Recurrent ViT

Combines two recent findings from the paper-VAE variant sweep:

1. **Affine feedback** (`paper_affine_vae`) — memory derives a scale matrix Γ and shift β,
   then applies plain self-attention on X′ = Γ·X + β. This was the **only variant that
   showed strong cue-orienting** at the cue frame (atlas: ~0.75 attention to cued patch at t=1
   vs ~0.25 for multiplicative). It collapsed late in training (always-wait policy).

2. **Dual xLSTM stack** (`paper_2lstm_vae`) — LSTM1's H1 feeds the attention block; LSTM2(H1)
   produces H2 for the actor/critic. This was the **most stable** multiplicative variant
   (~87% rolling correct, no collapse).

## Architecture

```
frame → frozen VAE front-end (4 × 140-d tokens)
      → AffineModulatedSA(H1):  X′ = Γ(H1)·X + β(H1);  Z = X + SA(X′)
      → LSTM1(Z) → H1
      → LSTM2(H1) → H2
      → actor / QR-critic read flatten(H2)
```

Same PAC + QR-DQN + PER harness as `RViT_plus_paper`. Checkpoints live outside the repo:

`~/rvit_plus_checkpoints/paper_affine2lstm_vae/`

## Train

```bash
python RViT_plus_paper_affine2lstm/train_rl.py --device mps
python RViT_plus_paper_affine2lstm/train_rl.py --iters 2 --device cpu   # smoke test
```

Start **fresh** — do not resume from plain `paper_affine_vae` or `paper_2lstm_vae` (different
state dict: extra LSTM2 + different head readout path).

## Analysis

Cue-orienting diagnosis (why affine orients when others do not):

```bash
python RViT_plus_paper/analysis/cue_orienting_diagnosis.py affine standard two_lstm
```

After training, add `affine2lstm` to the variant list in that script or run the family atlas.

## Status

Scaffold ready; not yet trained.
