#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
PROJECT_ROOT="$WORKSPACE_ROOT/RViT_plus_paper_jepa_grid9"
source "$WORKSPACE_ROOT/.venv/bin/activate"

RUN_STAMP="$(python3 -c 'from datetime import datetime, timezone; import uuid; print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:12])')"
CHECKPOINT_ROOT="$WORKSPACE_ROOT/battery_sweep_results/spatial_discretization"
CHECKPOINT_DIR="$CHECKPOINT_ROOT/vda4_affine_ew_grid10x10_d128_replay_excluded_seed0_${RUN_STAMP}"
mkdir -p "$CHECKPOINT_ROOT"
mkdir "$CHECKPOINT_DIR"
printf 'VDA4 affine_ew 10x10 sensory-grid run: %s\n' "$CHECKPOINT_DIR"

export PYTHONUNBUFFERED=1
exec python3 -u "$PROJECT_ROOT/train_rl.py" \
  --task vda4 \
  --T 7 \
  --min-change-time 5 \
  --max-change-time 5 \
  --patch-grid-rows 10 \
  --patch-grid-cols 10 \
  --cell xlstm \
  --feedback affine_ew \
  --conv-frontend \
  --jepa-coef 0.5 \
  --d-mem 128 \
  --curriculum \
  --init-mode fresh \
  --checkpoint-dir "$CHECKPOINT_DIR" \
  --iters 20000 \
  --schedule-final-iteration 19999 \
  --episodes-per-iter 8 \
  --save-every 50 \
  --log-every 1 \
  --seed 0 \
  --device mps
