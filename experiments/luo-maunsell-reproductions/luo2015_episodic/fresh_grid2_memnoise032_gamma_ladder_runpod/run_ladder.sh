#!/usr/bin/env bash
set -euo pipefail
CELL="${CELL:?set CELL}"
LADDER_ROOT="${LADDER_ROOT:?set LADDER_ROOT}"
PYTHON_BIN="${PYTHON_BIN:-python}"
case "$CELL" in
 sensitivity_loc0) TASK=luo2015_sensitivity; HIGH_LOC=0 ;;
 sensitivity_loc3) TASK=luo2015_sensitivity; HIGH_LOC=3 ;;
 criterion_loc0) TASK=luo2015_criterion; HIGH_LOC=0 ;;
 criterion_loc3) TASK=luo2015_criterion; HIGH_LOC=3 ;;
 *) echo "invalid CELL: $CELL" >&2; exit 2;;
esac
SCRIPT=experiments/luo2015_episodic/fresh_grid2_memnoise032_gamma_ladder_runpod/launch_cell.sh
if [[ "${DRY_RUN:-0}" == 1 ]]; then
 for spec in '0.8 gamma080' '0.9 gamma090' '1.0 gamma100'; do
  read -r gamma tag <<< "$spec"
  env DRY_RUN=1 CELL="$CELL" GAMMA="$gamma" RUN_ROOT="$LADDER_ROOT/$tag" PYTHON_BIN="$PYTHON_BIN" bash "$SCRIPT"
 done
 exit 0
fi
mkdir -p "$LADDER_ROOT"
cp experiments/luo2015_episodic/fresh_grid2_memnoise032_gamma_ladder_runpod/experiment_manifest.json "$LADDER_ROOT/experiment_manifest.json"
printf '{"cell":"%s","gammas":[0.8,0.9,1.0],"initialization_each_stage":"fresh_seed_0","weights_carried":false}\n' "$CELL" > "$LADDER_ROOT/ladder_contract.json"
for spec in '0.8 gamma080' '0.9 gamma090' '1.0 gamma100'; do
 read -r gamma tag <<< "$spec"; run_root="$LADDER_ROOT/$tag"; final="$run_root/rvit_paper_${TASK}_final.pt"
 if [[ -e "$run_root/STAGE_COMPLETE" ]]; then
  [[ -s "$final" ]] || { echo "$tag marked complete without final checkpoint" >&2; exit 20; }
  continue
 fi
 if [[ -e "$run_root/rvit_plus_rl_latest.pt" || -e "$final" ]]; then
  echo "incomplete pre-existing stage requires manual recovery: $run_root" >&2; exit 21
 fi
 printf '%s\n' "$gamma" > "$LADDER_ROOT/current_gamma.txt"
 env CELL="$CELL" GAMMA="$gamma" RUN_ROOT="$run_root" PYTHON_BIN="$PYTHON_BIN" ITERS=20000 SAVE_EVERY=50 DEVICE=cuda bash "$SCRIPT"
 env CHECKPOINT="$final" EXPECTED_GAMMA="$gamma" EXPECTED_TASK="$TASK" EXPECTED_LOC="$HIGH_LOC" "$PYTHON_BIN" - <<'PY'
import math, os, torch
p=os.environ['CHECKPOINT']; c=torch.load(p,map_location='cpu',weights_only=False)
assert int(c['iter']) == 19999
assert c['initialization_contract']['mode'] == 'fresh'
assert math.isclose(float(c['ppo_config']['gamma']), float(os.environ['EXPECTED_GAMMA']))
assert c['task'] == os.environ['EXPECTED_TASK']
assert int(c['training_args']['high_loc']) == int(os.environ['EXPECTED_LOC'])
assert c['training_args']['curriculum'] is False
assert math.isclose(float(c['environment_state']['theta']),65.0)
PY
 touch "$run_root/STAGE_COMPLETE"
done
touch "$LADDER_ROOT/LADDER_COMPLETE"
