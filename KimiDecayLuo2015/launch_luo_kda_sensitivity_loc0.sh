#!/usr/bin/env bash
# Luo–Maunsell 2015 sensitivity, high_loc=0, KDA conv-memory agent. NOT launched yet.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ROOT="${RUN_ROOT:-/workspace/runs/luo2015_kda_c64_loc0_seed0}"
DEVICE="${DEVICE:-cuda}"
mkdir -p "$RUN_ROOT/checkpoints"

exec "$HERE/.venv/bin/python" -u "$HERE/train_rl.py" \
  --task luo2015_sensitivity --curriculum --high-loc 0 \
  --theta-start 65.0 --curr-window 1000 --curr-threshold 0.85 \
  --curr-step 3.0 --curr-floor 8.0 \
  --T 7 --frame-repeat 1 --noise 5.0 \
  --accum-mode kda --accum-decay 0.5 --kda-heads 4 --kda-head-dim 16 \
  --n-channels 64 --map-size 16 --proto-dim 256 \
  --memory-noise-std 0.05 --mem-every 1 \
  --actor-coef 0.5 --value-coef 1.0 --jepa-coef 0.01 --bc-alpha 0.0 \
  --jepa-ema-decay 0.996 --jepa-var-coef 1.0 --jepa-cov-coef 0.01 \
  --iters 19999 --episodes-per-iter 8 --seed 0 \
  --device "$DEVICE" --save-every 200 --log-every 5 \
  --checkpoint-dir "$RUN_ROOT/checkpoints"
