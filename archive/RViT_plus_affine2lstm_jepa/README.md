# Affine Two-LSTM + Sequential JEPA

This is a fresh variant directory. It starts from the affine two-LSTM idea in
`RViT_plus_paper_affine2lstm`, but removes the VAE entirely.

## Hypothesis

The VAE may have stabilized the RL objective by imposing a predictive/structured
representation. This variant replaces that stabilizer with a simultaneous
sequential JEPA objective:

```text
frame -> conv 4x4 patchifier -> affine recurrent ViT -> H2_t

student: project(H2_t) -> predict z_{t+1}
teacher: EMA(model).project(H2_{t+1})
loss:    SmoothL1(norm(pred), norm(stopgrad(target)))
```

There is no masking and no pretraining. RL and JEPA update the encoder in the same
training loop. The RL objective supplies the task pressure that masking would
normally provide in V-JEPA-style training.

## Architecture

- Conv front-end: RGB `50x50` -> `4x4` tokens, `d_model=140`.
- Feedback: affine modulation, `X' = Gamma(H1) X + beta(H1)`, then self-attention.
- Memory: two xLSTMs, with `H1` feeding attention and `H2` feeding RL heads.
- JEPA: predicts EMA-teacher `H2_{t+1}` latents from online `H2_t`.

Checkpoints live outside the Drive-synced repo:

```text
~/rvit_plus_checkpoints/affine2lstm_jepa/
```

## Train

```bash
cd /Users/jonathanmorgan/AttentionManuscript
.venv/bin/python RViT_plus_affine2lstm_jepa/train_rl.py --device mps
```

Smoke test:

```bash
.venv/bin/python RViT_plus_affine2lstm_jepa/train_rl.py --iters 2 --device cpu --log-every 1
```
