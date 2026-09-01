#!/usr/bin/env bash
# KDA accumulator on VDA16 — seed 0 pilot. Exact scientific contract below;
# every flag is spelled out so default drift cannot silently change the run.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ROOT="${RUN_ROOT:-/workspace/runs/vda16_kda_c128_seed0}"
DEVICE="${DEVICE:-cuda}"
mkdir -p "$RUN_ROOT/checkpoints"

exec "$HERE/.venv/bin/python" -u "$HERE/pretrain_kda_convmem.py" \
  --task vda16 --label change \
  --T 7 --min-change-time 5 --max-change-time 5 \
  --noise 5.0 --memory-noise-std 0.05 \
  --accum-mode kda --accum-decay 0.5 --kda-heads 4 --kda-head-dim 32 \
  --n-channels 128 --map-size 16 --proto-dim 256 \
  --frame-window 1 --frame-stride 1 --mem-every 1 \
  --jepa-coef 1.0 --change-coef 1.0 \
  --jepa-ema-decay 0.996 --jepa-tau-student 0.1 \
  --jepa-tau-teacher-start 0.03 --jepa-tau-teacher-end 0.05 --jepa-tau-warmup 300 \
  --jepa-center-momentum 0.9 --jepa-sinkhorn-iters 3 \
  --jepa-var-coef 1.0 --jepa-cov-coef 0.01 \
  --theta-start 65.0 --curr-threshold 0.85 --curr-step 3.0 --curr-floor 8.0 \
  --n-trials 500000 --collection-size 1024 --epochs 5 --batch-size 64 \
  --lr 0.0003 --grad-clip 1.0 --seed 0 --amp \
  --device "$DEVICE" \
  --save-every 10 --log-every 1 \
  --checkpoint-dir "$RUN_ROOT/checkpoints"
