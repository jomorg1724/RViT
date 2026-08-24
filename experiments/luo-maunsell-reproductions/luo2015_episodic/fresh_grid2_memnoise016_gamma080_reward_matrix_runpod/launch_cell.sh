#!/usr/bin/env bash
set -euo pipefail
CELL="${CELL:?set CELL}"
case "$CELL" in
 sensitivity_loc0) TASK=luo2015_sensitivity; HIGH_LOC=0; REWARD_SCALE=0.3333333333333333 ;;
 sensitivity_loc3) TASK=luo2015_sensitivity; HIGH_LOC=3; REWARD_SCALE=0.3333333333333333 ;;
 criterion_loc0) TASK=luo2015_criterion; HIGH_LOC=0; REWARD_SCALE=1.0526315789473684 ;;
 criterion_loc3) TASK=luo2015_criterion; HIGH_LOC=3; REWARD_SCALE=1.0526315789473684 ;;
 *) echo "invalid CELL: $CELL" >&2; exit 2;;
esac
RUN_ROOT="${RUN_ROOT:?set RUN_ROOT}"
PYTHON_BIN="${PYTHON_BIN:-python}"
ITERS="${ITERS:-20000}"
DEVICE="${DEVICE:-cuda}"
SAVE_EVERY="${SAVE_EVERY:-50}"
[[ "$ITERS" -gt 0 ]] || { echo "ITERS must be positive" >&2; exit 2; }
FINAL_ITER=$((ITERS - 1))
cmd=("$PYTHON_BIN" -u train_rl.py --T 7
 --patch-grid-rows 2 --patch-grid-cols 2 --cell xlstm --feedback crossattn1
 --memory-decay 1.0 --memory-noise-std 0.16 --noise 5.0 --conv-frontend
 --jepa-coef 0.5 --d-mem 32 --episodes-per-iter 8 --gamma 0.8
 --save-every "$SAVE_EVERY" --log-every 1 --seed 0 --device "$DEVICE"
 --iters "$ITERS" --schedule-final-iteration "$FINAL_ITER" --checkpoint-dir "$RUN_ROOT"
 --experiment-launcher experiments/luo2015_episodic/fresh_grid2_memnoise016_gamma080_reward_matrix_runpod/launch_cell.sh
 --task "$TASK" --init-mode fresh --high-loc "$HIGH_LOC" --reward-scale "$REWARD_SCALE"
 --theta-start 65.0)
if [[ "${DRY_RUN:-0}" == 1 ]]; then printf '%q ' "${cmd[@]}"; printf '\n'; exit 0; fi
if [[ -e "$RUN_ROOT/rvit_plus_rl_latest.pt" || -e "$RUN_ROOT/rvit_paper_${TASK}_final.pt" ]]; then
 echo "refusing fresh launch into checkpoint-bearing root: $RUN_ROOT" >&2; exit 3
fi
mkdir -p "$RUN_ROOT"
cp experiments/luo2015_episodic/fresh_grid2_memnoise016_gamma080_reward_matrix_runpod/experiment_manifest.json "$RUN_ROOT/experiment_manifest.json"
printf 'cell=%s\ngamma=0.8\ninitialization=fresh\ntask=%s\ncondition_loc=%s\nreward_scale=%s\nmemory_noise_std=0.16\nsensory_noise_std=5.0\ntheta=65.0\ncurriculum=false\nrun_root=%s\n' "$CELL" "$TASK" "$HIGH_LOC" "$REWARD_SCALE" "$RUN_ROOT" > "$RUN_ROOT/launch_contract.txt"
exec "${cmd[@]}"
