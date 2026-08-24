#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -eq 3 ]] || {
  printf 'USAGE: %s VISUAL_STREAMS MEMORY_STREAMS SEED\n' "$0" >&2
  exit 2
}
VISUAL_STREAMS="$1"
MEMORY_STREAMS="$2"
SEED="$3"

case "$VISUAL_STREAMS" in 4|100) ;; *) printf 'ERROR: VISUAL_STREAMS must be 4 or 100\n' >&2; exit 2 ;; esac
case "$MEMORY_STREAMS" in 4|100) ;; *) printf 'ERROR: MEMORY_STREAMS must be 4 or 100\n' >&2; exit 2 ;; esac
case "$SEED" in 0|1|2) ;; *) printf 'ERROR: production-v1 seed must be 0, 1, or 2\n' >&2; exit 2 ;; esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG="$SCRIPT_DIR/config_crossattn1_v1.json"
DESIGN="$SCRIPT_DIR/design_manifest.json"
LAUNCHER="$SCRIPT_DIR/launch_crossattn1_production_v1.sh"
PREFLIGHT="$SCRIPT_DIR/preflight_contract_v1.py"
EXPECTED_CONFIG_SHA256="f5b62e32e40e2d8c5ee97ae71e2c520737fbf431ff4b64f82b58c718b23eb6aa"
EXPECTED_DESIGN_SHA256="8a82292d725eb7519c4c394a0ddfe9037aac2a60fa02476e1ce241e76b9daf76"
PYTHON_BIN="${PYTHON_BIN:-/workspace/rvit_venv/bin/python}"

[[ -x "$PYTHON_BIN" ]] || { printf 'ERROR: Python is not executable: %s\n' "$PYTHON_BIN" >&2; exit 2; }
[[ -f "$PROJECT_ROOT/train_rl.py" ]] || { printf 'ERROR: project root is incomplete: %s\n' "$PROJECT_ROOT" >&2; exit 2; }

PREFLIGHT_ARGS=(
  --project-root "$PROJECT_ROOT"
  --config "$CONFIG"
  --design "$DESIGN"
  --launcher "$LAUNCHER"
  --expected-config-sha256 "$EXPECTED_CONFIG_SHA256"
  --expected-design-sha256 "$EXPECTED_DESIGN_SHA256"
  --visual-streams "$VISUAL_STREAMS"
  --memory-streams "$MEMORY_STREAMS"
  --seed "$SEED"
  --run-kind production
)
"$PYTHON_BIN" "$PREFLIGHT" "${PREFLIGHT_ARGS[@]}"

RUN_STAMP="$($PYTHON_BIN -c 'from datetime import datetime, timezone; import uuid; print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:12])')"
CHECKPOINT_DIR="/workspace/vda4_stream_factorial_crossattn1_visual${VISUAL_STREAMS}_memory${MEMORY_STREAMS}_seed${SEED}_production_v1_${RUN_STAMP}"
mkdir "$CHECKPOINT_DIR"
TRAIN_LOG="$CHECKPOINT_DIR/train.log"

TRAIN_ARGS=(
  --config "$CONFIG"
  --task vda4
  --T 7
  --frame-repeat 1
  --min-change-time 5
  --max-change-time 5
  --noise 5.0
  --patch-grid-rows 10
  --patch-grid-cols 10
  --effective-visual-streams "$VISUAL_STREAMS"
  --effective-memory-streams "$MEMORY_STREAMS"
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
  --seed "$SEED"
  --device cuda
  --experiment-launcher "$LAUNCHER"
)

"$PYTHON_BIN" "$PREFLIGHT" "${PREFLIGHT_ARGS[@]}" \
  --run-dir "$CHECKPOINT_DIR" --emit-json > "$CHECKPOINT_DIR/launch_contract.json"

printf 'RUN_DIR=%s\n' "$CHECKPOINT_DIR"
printf 'TRAIN_LOG=%s\n' "$TRAIN_LOG"
printf 'CONTRACT=%s\n' "$CHECKPOINT_DIR/launch_contract.json"
printf 'EVIDENCE_CLASS=scientific_only_after_terminal_and_heldout_validation\n'

export PYTHONUNBUFFERED=1
exec "$PYTHON_BIN" -u "$PROJECT_ROOT/train_rl.py" "${TRAIN_ARGS[@]}" \
  > >(tee -a "$TRAIN_LOG") 2>&1
