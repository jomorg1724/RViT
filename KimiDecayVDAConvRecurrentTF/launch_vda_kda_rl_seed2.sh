#!/usr/bin/env bash
# VDA16 KDA + PAC/QR RL, seed 2, 250k episodes. Fresh (not the supervised ckpt).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ROOT="${RUN_ROOT:-/workspace/runs/vda16_kda_rl_c128_seed2}"
DEVICE="${DEVICE:-cuda}"
mkdir -p "$RUN_ROOT/checkpoints"
RESUME_FLAGS=()
if [[ -n "${RESUME_CKPT:-}" ]]; then
  RESUME_FLAGS+=(--resume "$RESUME_CKPT")
fi
exec "$HERE/.venv/bin/python" -u "$HERE/train_rl_vda.py" \
  --task vda16 --curriculum \
  --theta-start 65.0 --curr-window 1000 --curr-threshold 0.85 \
  --curr-step 3.0 --curr-floor 8.0 \
  --T 7 --frame-repeat 1 --noise 5.0 \
  --accum-mode kda --accum-decay 0.5 --kda-heads 4 --kda-head-dim 32 \
  --n-channels 128 --map-size 16 --proto-dim 256 \
  --memory-noise-std 0.05 --mem-every 1 \
  --actor-coef 0.5 --value-coef 1.0 --jepa-coef 0.01 --bc-alpha 0.0 \
  --jepa-ema-decay 0.996 --jepa-var-coef 1.0 --jepa-cov-coef 0.01 \
  --iters 31250 --episodes-per-iter 8 --seed 2 \
  --device "$DEVICE" --save-every 200 --log-every 5 \
  --checkpoint-dir "$RUN_ROOT/checkpoints" \
  "${RESUME_FLAGS[@]}"
