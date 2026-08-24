#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CONFIG="$SCRIPT_DIR/config_v1.json"
LAUNCHER="$SCRIPT_DIR/launch_runpod_v1.sh"
PREFLIGHT="$SCRIPT_DIR/preflight_contract_v1.py"
PYTHON_BIN="${PYTHON_BIN:-/workspace/rvit_venv/bin/python}"

[[ -x "$PYTHON_BIN" ]] || { printf 'ERROR: Python is not executable: %s\n' "$PYTHON_BIN" >&2; exit 2; }
[[ -f "$PROJECT_ROOT/train_rl.py" ]] || { printf 'ERROR: project root is incomplete: %s\n' "$PROJECT_ROOT" >&2; exit 2; }

"$PYTHON_BIN" "$PREFLIGHT" \
  --project-root "$PROJECT_ROOT" \
  --config "$CONFIG" \
  --launcher "$LAUNCHER"

RUN_STAMP="$($PYTHON_BIN -c 'from datetime import datetime, timezone; import uuid; print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:12])')"
CHECKPOINT_DIR="/workspace/vda_fixed9_crossattn1_grid4x4_d128_nodecay_seed0_canary_v1_${RUN_STAMP}"
mkdir "$CHECKPOINT_DIR"
TRAIN_LOG="$CHECKPOINT_DIR/train.log"

TRAIN_ARGS=(
  --config "$CONFIG"
  --task vda_fixed9
  --T 7
  --frame-repeat 1
  --min-change-time 5
  --max-change-time 5
  --noise 5.0
  --patch-grid-rows 4
  --patch-grid-cols 4
  --cell xlstm
  --feedback crossattn1
  --d-mem 128
  --memory-decay 1.0
  --memory-noise-std 0.0
  --conv-frontend
  --n-actions 2
  --n-quantiles 5
  --init-action-bias 0.0 -1.5
  --jepa-coef 0.5
  --jepa-heads 4
  --jepa-proto-dim 256
  --jepa-tau-student 0.1
  --jepa-tau-teacher-start 0.04
  --jepa-tau-teacher-end 0.07
  --jepa-tau-warmup 300
  --jepa-center-momentum 0.9
  --jepa-ema-decay 0.996
  --curriculum
  --theta-start 65.0
  --curr-window 1000
  --curr-threshold 0.85
  --curr-step 3.0
  --curr-floor 8.0
  --lr 0.0003
  --gamma 0.95
  --entropy-coef 0.01
  --ema-decay 0.995
  --buffer-capacity 1000
  --qr-kappa 1.0
  --mpo-temperature 0.1
  --init-mode fresh
  --start-iteration 0
  --checkpoint-dir "$CHECKPOINT_DIR"
  --iters 20000
  --schedule-final-iteration 19999
  --episodes-per-iter 8
  --save-every 50
  --log-every 1
  --seed 0
  --device cuda
  --experiment-launcher "$LAUNCHER"
)

"$PYTHON_BIN" "$PREFLIGHT" \
  --project-root "$PROJECT_ROOT" \
  --config "$CONFIG" \
  --launcher "$LAUNCHER" \
  --run-dir "$CHECKPOINT_DIR" \
  --emit-json > "$CHECKPOINT_DIR/launch_contract.json"

printf 'RUN_DIR=%s\n' "$CHECKPOINT_DIR"
printf 'TRAIN_LOG=%s\n' "$TRAIN_LOG"
printf 'CONTRACT=%s\n' "$CHECKPOINT_DIR/launch_contract.json"

export PYTHONUNBUFFERED=1
exec "$PYTHON_BIN" -u "$PROJECT_ROOT/train_rl.py" "${TRAIN_ARGS[@]}" \
  > >(tee -a "$TRAIN_LOG") 2>&1
