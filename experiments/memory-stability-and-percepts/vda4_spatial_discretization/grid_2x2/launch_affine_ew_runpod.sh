#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/workspace/rvit_venv/bin/python}"
ITERS="${ITERS:-20000}"
SEED="${SEED:-0}"
RUN_KIND="${RUN_KIND:-production}"

RUN_STAMP="$($PYTHON_BIN -c 'from datetime import datetime, timezone; import uuid; print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:12])')"
CHECKPOINT_DIR="/workspace/vda4_affine_ew_grid2x2_d128_nodecay_seed${SEED}_${RUN_KIND}_${RUN_STAMP}"
mkdir "$CHECKPOINT_DIR"
printf 'RUN_DIR=%s\n' "$CHECKPOINT_DIR"

export PYTHONUNBUFFERED=1
exec "$PYTHON_BIN" -u "$PROJECT_ROOT/train_rl.py" \
  --task vda4 \
  --T 7 \
  --min-change-time 5 \
  --max-change-time 5 \
  --patch-grid-rows 2 \
  --patch-grid-cols 2 \
  --cell xlstm \
  --feedback affine_ew \
  --memory-decay 1.0 \
  --conv-frontend \
  --jepa-coef 0.5 \
  --d-mem 128 \
  --curriculum \
  --init-mode fresh \
  --checkpoint-dir "$CHECKPOINT_DIR" \
  --iters "$ITERS" \
  --schedule-final-iteration 19999 \
  --episodes-per-iter 8 \
  --save-every 50 \
  --log-every 1 \
  --seed "$SEED" \
  --device cuda \
  --experiment-launcher "${BASH_SOURCE[0]}"
