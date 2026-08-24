#!/usr/bin/env bash
set -euo pipefail

: "${RUN_ROOT:?set RUN_ROOT to a new local output directory}"
PYTHON_BIN="${PYTHON_BIN:-python}"
ITERS="${ITERS:-20000}"
DEVICE="${DEVICE:-cuda}"
SAVE_EVERY="${SAVE_EVERY:-50}"
SCHEDULE_FINAL_ITERATION="${SCHEDULE_FINAL_ITERATION:-19999}"

[[ "$ITERS" -gt 0 ]] || { printf 'ERROR: ITERS must be positive\n' >&2; exit 2; }
[[ "$SAVE_EVERY" -gt 0 ]] || { printf 'ERROR: SAVE_EVERY must be positive\n' >&2; exit 2; }
[[ ! -e "$RUN_ROOT" ]] || { printf 'ERROR: refusing pre-existing RUN_ROOT: %s\n' "$RUN_ROOT" >&2; exit 3; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PY_PROJECT_ROOT="$PROJECT_ROOT"
PY_LAUNCHER="$SCRIPT_DIR/launch_local_v1.sh"
if command -v cygpath >/dev/null 2>&1; then
  PY_PROJECT_ROOT="$(cygpath -w "$PROJECT_ROOT")"
  PY_LAUNCHER="$(cygpath -w "$PY_LAUNCHER")"
fi
mkdir -p "$(dirname "$RUN_ROOT")"
mkdir "$RUN_ROOT"
mkdir -p "$RUN_ROOT/provenance/source_snapshot/envs" "$RUN_ROOT/provenance/source_snapshot/tests"
cp "$SCRIPT_DIR/design_manifest.json" "$RUN_ROOT/design_manifest.json"
for f in model.py paper_encoder.py paper_heads.py conv_frontend.py train_rl.py ppo.py; do
  cp "$PROJECT_ROOT/$f" "$RUN_ROOT/provenance/source_snapshot/$f"
done
cp "$PROJECT_ROOT/envs/base.py" "$RUN_ROOT/provenance/source_snapshot/envs/base.py"
for f in test_teacher_actor_critic_ste.py test_teacher_actor_critic_ste_experiment_contract.py test_modern_transformer_memory.py test_softmax_memory_anticollapse.py; do
  cp "$PROJECT_ROOT/tests/$f" "$RUN_ROOT/provenance/source_snapshot/tests/$f"
done
sha256sum \
  "$PROJECT_ROOT/model.py" "$PROJECT_ROOT/paper_encoder.py" "$PROJECT_ROOT/paper_heads.py" \
  "$PROJECT_ROOT/conv_frontend.py" "$PROJECT_ROOT/train_rl.py" "$PROJECT_ROOT/ppo.py" \
  "$PROJECT_ROOT/envs/base.py" \
  "$PROJECT_ROOT/tests/test_teacher_actor_critic_ste.py" \
  "$PROJECT_ROOT/tests/test_teacher_actor_critic_ste_experiment_contract.py" \
  "$PROJECT_ROOT/tests/test_modern_transformer_memory.py" \
  "$PROJECT_ROOT/tests/test_softmax_memory_anticollapse.py" \
  "$SCRIPT_DIR/design_manifest.json" "$SCRIPT_DIR/launch_local_v1.sh" \
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
  --cell transformer_memory_2layer_softmax_modern
  --feedback crossattn1
  --d-mem 128
  --mem-heads 4
  --memory-decay 1.0
  --memory-noise-std 0.0
  --conv-frontend
  --n-actions 2
  --n-quantiles 5
  --init-action-bias 0.0 -1.5
  --value-coef 1.0
  --actor-coef 0.1
  --jepa-coef 0.001
  --bc-alpha 0.0
  --teacher-actor-critic-ste
  --jepa-heads 4
  --jepa-proto-dim 256
  --jepa-tau-student 0.1
  --jepa-tau-teacher-start 0.03
  --jepa-tau-teacher-end 0.05
  --jepa-tau-warmup 300
  --jepa-center-momentum 0.9
  --jepa-ema-decay 0.996
  --jepa-sinkhorn-iters 3
  --jepa-var-coef 1.0
  --jepa-cov-coef 0.01
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
  printf 'experiment=vda4_modern_teacherac_ste_c1_a01_j0001_s0_v1\n'
  printf 'representation_forward=detached_JEPA_EMA_teacher_H2\n'
  printf 'representation_backward=online_student_H2_via_STE\n'
  printf 'actor_critic_heads=trainable_online_heads\n'
  printf 'run_root=%s\n' "$RUN_ROOT"
  printf 'iterations=%s\n' "$ITERS"
  printf 'schedule_final_iteration=%s\n' "$SCHEDULE_FINAL_ITERATION"
  printf 'device=%s\n' "$DEVICE"
  printf 'gamma=0.95\n'
  printf 'theta_contract=start65_window1000_threshold0.85_subtract3_floor8_nonoverlapping\n'
  printf 'command='; printf '%q ' "$PYTHON_BIN" -u "$PY_PROJECT_ROOT/train_rl.py" "${TRAIN_ARGS[@]}"; printf '\n'
} > "$RUN_ROOT/launch_contract.txt"

printf 'RUN_ROOT=%s\n' "$RUN_ROOT"
printf 'EVIDENCE_CLASS=%s\n' "$([[ "$ITERS" == "20000" ]] && printf online_same_distribution_training || printf engineering_canary)"
export PYTHONUNBUFFERED=1
exec "$PYTHON_BIN" -u "$PY_PROJECT_ROOT/train_rl.py" "${TRAIN_ARGS[@]}"
