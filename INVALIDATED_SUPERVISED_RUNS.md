# Invalidated supervised experiments

The reset-discarding supervised collector is retired. Its old weights, metrics, analyses, takeoff claims, and baselines are invalid and must not be reused or restored.

The corrected implementation is `KimiDecayVDAConvRecurrentTF/pretrain_kda_convmem.py`, with `envs/sequences.py` and a fresh-only `launch.py`. Its protocol `blank_first_v1` processes exactly seven observations: reset blank t0, cue t1, blank t2, samples t3/t4, and tests t5/t6. Changed-trial labels are 0000011. Old or mismatched sequence metadata is rejected before loading model weights. Focused tests exercise the actual model input and label path.

The replacement no-memory experiment starts from random initialization, not an old checkpoint. Unrelated reset-correct RL experiments remain separate.

Known affected artifacts and obsolete entrypoints were deleted from the current working trees and GitHub main. This notice contains no old results or weights. Historical Git commits, other clones, and cloud version/recycle-bin history have NOT been erased; do not recover invalid artifacts from those sources.
