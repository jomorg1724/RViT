#!/usr/bin/env bash
set -euo pipefail

: "${RUN_ROOT:?set RUN_ROOT to a new local output directory}"
PYTHON_BIN="${PYTHON_BIN:-python}"
ITERS="${ITERS:-5000}"
DEVICE="${DEVICE:-cuda}"
SAVE_EVERY="${SAVE_EVERY:-50}"
SCHEDULE_FINAL_ITERATION="${SCHEDULE_FINAL_ITERATION:-4999}"
PARENT_CHECKPOINT="${PARENT_CHECKPOINT:-C:/Users/jomor/Documents/RViT_runs/vda4_transformer_memory_2layer_frozen_trunk_head_rescue_seed0_v1/trunk_parent_iter16949.pt}"
PARENT_SHA256="d9539ef2c4cb0b337da4c87023f10b6507581d189392c2c99c93a624ada10898"

[[ "$ITERS" -gt 0 ]] || { printf 'ERROR: ITERS must be positive\n' >&2; exit 2; }
[[ "$SAVE_EVERY" -gt 0 ]] || { printf 'ERROR: SAVE_EVERY must be positive\n' >&2; exit 2; }
[[ -f "$PARENT_CHECKPOINT" ]] || { printf 'ERROR: parent checkpoint missing: %s\n' "$PARENT_CHECKPOINT" >&2; exit 2; }
[[ ! -e "$RUN_ROOT" ]] || { printf 'ERROR: refusing pre-existing RUN_ROOT: %s\n' "$RUN_ROOT" >&2; exit 3; }
ACTUAL_PARENT_SHA256="$(sha256sum "$PARENT_CHECKPOINT" | cut -d' ' -f1)"
[[ "$ACTUAL_PARENT_SHA256" == "$PARENT_SHA256" ]] || {
  printf 'ERROR: parent SHA256 mismatch: expected %s got %s\n' "$PARENT_SHA256" "$ACTUAL_PARENT_SHA256" >&2
  exit 4
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PY_PROJECT_ROOT="$PROJECT_ROOT"
PY_LAUNCHER="$SCRIPT_DIR/launch_local_v1.sh"
PY_PARENT_CHECKPOINT="$PARENT_CHECKPOINT"
if command -v cygpath >/dev/null 2>&1; then
  PY_PROJECT_ROOT="$(cygpath -w "$PROJECT_ROOT")"
  PY_LAUNCHER="$(cygpath -w "$PY_LAUNCHER")"
  PY_PARENT_CHECKPOINT="$(cygpath -w "$PARENT_CHECKPOINT")"
fi
mkdir -p "$(dirname "$RUN_ROOT")"
mkdir "$RUN_ROOT"
cp "$SCRIPT_DIR/design_manifest.json" "$RUN_ROOT/design_manifest.json"
printf '%s  %s\n' "$PARENT_SHA256" "$PARENT_CHECKPOINT" > "$RUN_ROOT/parent_sha256.txt"
sha256sum \
  "$PROJECT_ROOT/model.py" \
  "$PROJECT_ROOT/paper_encoder.py" \
  "$PROJECT_ROOT/paper_heads.py" \
  "$PROJECT_ROOT/conv_frontend.py" \
  "$PROJECT_ROOT/train_rl.py" \
  "$PROJECT_ROOT/ppo.py" \
  "$SCRIPT_DIR/design_manifest.json" \
  "$SCRIPT_DIR/launch_local_v1.sh" \
  > "$RUN_ROOT/provenance_sha256.txt"

TRAIN_ARGS=(
  --task vda4
  --T 7
  --frame-repeat 1
  --min-change-time 5
  --max-change-time 5
  --noise 5.0
  --patch-grid-rows 2
  --patch-grid-cols 2
  --cell transformer_memory_2layer
  --feedback crossattn1
  --d-mem 128
  --mem-heads 4
  --memory-decay 1.0
  --memory-noise-std 0.0
  --conv-frontend
  --n-actions 2
  --n-quantiles 5
  --init-action-bias 0.0 0.0
  --jepa-coef 0.0
  --curriculum
  --theta-start 65.0
  --curr-window 1000
  --curr-threshold 0.85
  --curr-step 3.0
  --curr-floor 8.0
  --lr 0.0003
  --gamma 0.95
  --entropy-coef 0.1
  --ema-decay 0.995
  --buffer-capacity 1000
  --qr-kappa 1.0
  --mpo-temperature 0.1
  --init-mode frozen_trunk_probe
  --checkpoint-path "$PY_PARENT_CHECKPOINT"
  --expected-parent-sha256 "$PARENT_SHA256"
  --start-iteration 0
  --checkpoint-dir "$RUN_ROOT"
  --iters "$ITERS"
  --schedule-final-iteration "$SCHEDULE_FINAL_ITERATION"
  --episodes-per-iter 8
  --save-every "$SAVE_EVERY"
  --log-every 1
  --seed 0
  --device "$DEVICE"
  --experiment-launcher "$PY_LAUNCHER"
)

{
  printf 'experiment=vda4_grid2x2_crossattn1_transformer_memory_2layer_frozen_trunk_head_rescue_seed0_v1\n'
  printf 'run_root=%s\n' "$RUN_ROOT"
  printf 'parent=%s\n' "$PARENT_CHECKPOINT"
  printf 'parent_sha256=%s\n' "$PARENT_SHA256"
  printf 'iterations=%s\n' "$ITERS"
  printf 'schedule_final_iteration=%s\n' "$SCHEDULE_FINAL_ITERATION"
  printf 'device=%s\n' "$DEVICE"
  printf 'command='; printf '%q ' "$PYTHON_BIN" -u "$PY_PROJECT_ROOT/train_rl.py" "${TRAIN_ARGS[@]}"; printf '\n'
} > "$RUN_ROOT/launch_contract.txt"

printf 'RUN_ROOT=%s\n' "$RUN_ROOT"
printf 'EVIDENCE_CLASS=%s\n' "$([[ "$ITERS" == "5000" ]] && printf frozen_trunk_same_distribution_probe || printf engineering_canary)"
export PYTHONUNBUFFERED=1
exec "$PYTHON_BIN" -u "$PY_PROJECT_ROOT/train_rl.py" "${TRAIN_ARGS[@]}"
