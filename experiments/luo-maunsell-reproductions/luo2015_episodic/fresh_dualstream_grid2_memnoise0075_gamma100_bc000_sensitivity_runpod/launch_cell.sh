#!/usr/bin/env bash
set -euo pipefail
CELL="${CELL:?set CELL}"
case "$CELL" in
 sensitivity_loc0) HIGH_LOC=0 ;;
 sensitivity_loc3) HIGH_LOC=3 ;;
 *) echo "invalid CELL: $CELL" >&2; exit 2 ;;
esac
TASK=luo2015_sensitivity
REWARD_SCALE=0.3333333333333333
RUN_ROOT="${RUN_ROOT:?set RUN_ROOT}"
PYTHON_BIN="${PYTHON_BIN:-python}"
ITERS="${ITERS:-20000}"
START_ITERATION="${START_ITERATION:-0}"
DEVICE="${DEVICE:-cuda}"
SAVE_EVERY="${SAVE_EVERY:-50}"
[[ "$ITERS" -gt 0 ]] || { echo "ITERS must be positive" >&2; exit 2; }
[[ "$START_ITERATION" -ge 0 ]] || { echo "START_ITERATION must be non-negative" >&2; exit 2; }
FINAL_ITER=$((START_ITERATION + ITERS - 1))
EXPERIMENT=experiments/luo2015_episodic/fresh_dualstream_grid2_memnoise0075_gamma100_bc000_sensitivity_runpod
cmd=("$PYTHON_BIN" -u train_rl.py --T 7
 --patch-grid-rows 2 --patch-grid-cols 2 --cell xlstm --feedback crossattn1
 --dual-actor-critic-streams
 --memory-decay 1.0 --memory-noise-std 0.075 --noise 5.0 --conv-frontend
 --jepa-coef 0.5 --bc-alpha 0.0 --d-mem 32 --episodes-per-iter 8 --gamma 1.0
 --save-every "$SAVE_EVERY" --log-every 1 --seed 0 --device "$DEVICE"
 --start-iteration "$START_ITERATION" --iters "$ITERS"
 --schedule-final-iteration "$FINAL_ITER" --checkpoint-dir "$RUN_ROOT"
 --experiment-launcher "$EXPERIMENT/launch_cell.sh"
 --task "$TASK" --init-mode fresh --high-loc "$HIGH_LOC" --reward-scale "$REWARD_SCALE"
 --theta-start 65.0)
if [[ "${DRY_RUN:-0}" == 1 ]]; then printf '%q ' "${cmd[@]}"; printf '\n'; exit 0; fi
if [[ -e "$RUN_ROOT/rvit_plus_rl_latest.pt" || -e "$RUN_ROOT/rvit_paper_${TASK}_final.pt" ]]; then
 echo "refusing fresh launch into checkpoint-bearing root: $RUN_ROOT" >&2; exit 3
fi
mkdir -p "$RUN_ROOT"
cp "$EXPERIMENT/experiment_manifest.json" "$RUN_ROOT/experiment_manifest.json"
printf 'cell=%s\ntask=%s\ncondition_loc=%s\nreward_scale=%s\ngamma=1.0\ninitialization=fresh\ndual_actor_critic_streams=true\nactor_critic_parameter_sharing=none\nindependent_jepa_branches=actor,critic\njepa_coef_per_branch=0.5\nbc_alpha=0.0\nmemory_noise_std=0.075\nsensory_noise_std=5.0\ntheta=65.0\ncurriculum=false\nrun_root=%s\n' "$CELL" "$TASK" "$HIGH_LOC" "$REWARD_SCALE" "$RUN_ROOT" > "$RUN_ROOT/launch_contract.txt"
exec "${cmd[@]}"
