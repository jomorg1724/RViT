# RViT+ v8 — the H1-residual: making visual attention load-bearing

**Status:** implemented + tested 2026-06-10. Fresh-init. Exact copy of
RViT_plus_v5_part2 (trained & deep-dived 2026-06-09) with **one change**.

## The change

v5_part2's cross-attention block put its residual on the visual queries:

    Z = X + attn( Q=norm(X), KV=[X ++ H1 ++ H2] )        # v5_part2

v8 puts it on the carried memory instead:

    Z = H1_prev + attn( Q=norm(X), KV=[X ++ H1 ++ H2] )   # v8 (raw H1 — no tag/pos)

One line in `tx_lstm_encoder.py` (plus the matching line in the deep-dive's
bias-injectable replica `analysis/deepdive/dd_core.py`). Everything else —
patch embed, stacked per-token LSTMs, 1D-conv decoders, PAC + QR-DQN + PER
trainer, every hyperparameter — is v5_part2 verbatim. For `tx_layers > 1`
only the first block uses the H1-residual; later blocks' inputs are already
attention-derived, so their standard residuals re-introduce no bypass.

## Why (the hypothesis)

The v5_part2 deep-dive found its cross-attention ~90% memory-dominated, with
the patch keys **causally inert** (exp4: biasing patch-key attention barely
moved decisions, |Δ| ≈ 0, while memory keys were decision-moving with
|Δhit| = 0.12). The X-residual explains how that's possible: current-frame
visual content rides the skip path into the LSTMs whether or not attention
ever looks at the patch keys — attention to the image is *optional*.

The H1-residual closes that bypass. The only route by which frame-t visual
information can reach the recurrent state (and hence the decoders) is the
attention's value stream over the patch keys. If the model wants to see, it
must attend — visual attention becomes necessary by construction, not a
modulatory extra. Queries still come from X (queries select but carry no
content), and the skip path now carries the temporal prior (H1) instead,
which is arguably the more natural recurrent backbone anyway.

Predicted signatures if the hypothesis is right (testable with the copied
deep-dive suite, which already mirrors the new forward):

1. Patch-key attention mass well above v5_part2's ~10%, concentrated on
   task-relevant locations (cued quadrant / change location).
2. Patch keys become causally decision-moving in exp4 (they were the inert
   ones in v5_part2; memory keys carried |Δhit|=0.12).
3. If instead the model can solve the task from memory dynamics alone, v8
   will under-perform v5_part2 — also informative: it would bound how much
   the X-residual was doing.

## Risks / what to watch

- t=0 has H1 = learned H0, so the first frame's content arrives purely via
  attention added to a generic prior — slower early learning is expected.
- The block output scale now starts near H0 + small-init attention; if early
  training stalls (return flat well past the v5_part2 schedule), suspect the
  attention values under-carrying and consider warming `out_proj` init up.

## Running

```bash
.venv/bin/python -m RViT_plus_v8.tests.test_v8        # 13 tests (incl. the no-bypass proof)
.venv/bin/python RViT_plus_v8/train_rl.py             # train (config → ~/rvit_plus_checkpoints/v8)
```

The no-bypass property is unit-tested: with the attention output projection
zeroed, the encoder's recurrent update is bit-identical across wildly
different input frames (impossible in v5_part2, whose X-residual leaks the
frame through).
