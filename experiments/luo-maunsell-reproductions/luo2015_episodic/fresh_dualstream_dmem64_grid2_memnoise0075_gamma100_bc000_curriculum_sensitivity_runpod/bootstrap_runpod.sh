#!/usr/bin/env bash
set -euo pipefail
if [[ "$#" -ne 5 ]]; then echo "usage: $0 ARCHIVE SHA CELL RUN_ROOT SOURCE_DIR" >&2; exit 2; fi
ARCHIVE="$1"; EXPECTED_SHA="$2"; CELL="$3"; RUN_ROOT="$4"; SOURCE_DIR="$5"
case "$CELL" in sensitivity_loc0|sensitivity_loc3) ;; *) echo "invalid CELL: $CELL" >&2; exit 2;; esac
TASK=luo2015_sensitivity
EXPERIMENT=experiments/luo2015_episodic/fresh_dualstream_dmem64_grid2_memnoise0075_gamma100_bc000_curriculum_sensitivity_runpod
ACTUAL_SHA="$(sha256sum "$ARCHIVE" | cut -d' ' -f1)"; [[ "$ACTUAL_SHA" == "$EXPECTED_SHA" ]] || { echo archive-hash-mismatch >&2; exit 10; }
if [[ -d "$SOURCE_DIR" ]] && ! python3 - "$SOURCE_DIR" <<'PY'
from pathlib import Path
import sys
raise SystemExit(0 if not any(Path(sys.argv[1]).iterdir()) else 1)
PY
then echo refusing-nonempty-source-dir >&2; exit 11; fi
[[ ! -e "$RUN_ROOT" ]] || { echo refusing-preexisting-run-root >&2; exit 12; }
mkdir -p "$SOURCE_DIR"; tar --no-same-owner -xzf "$ARCHIVE" -C "$SOURCE_DIR"; cd "$SOURCE_DIR"
PYTHON_BIN=/workspace/rvit_venv/bin/python
[[ -x "$PYTHON_BIN" ]] || python3 -m venv --system-site-packages /workspace/rvit_venv
if ! "$PYTHON_BIN" - <<'PY'
import gymnasium,imageio,matplotlib,numpy,pandas,PIL,pytest,scipy,torch
PY
then "$PYTHON_BIN" -m pip install --no-cache-dir pytest pandas pillow matplotlib imageio gymnasium scipy; fi
"$PYTHON_BIN" - <<'PY'
import torch
assert torch.cuda.is_available(); print({'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0)})
PY
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PYTHON_BIN" -m pytest -q \
 tests/test_dual_actor_critic_streams.py tests/test_bc_alpha_cli.py \
 tests/test_luo2015_dualstream_dmem64_curriculum_runpod.py tests/test_luo2015_protocol.py \
 tests/test_luo2015_scientific_assay.py tests/test_luo2015_attention_allocation.py \
 tests/test_training_checkpoint.py
CANARY="/workspace/canary_luo_dualstream_dmem64_${CELL}"; rm -rf "$CANARY"
env CELL="$CELL" RUN_ROOT="$CANARY" PYTHON_BIN="$PYTHON_BIN" ITERS=1 START_ITERATION=20 SAVE_EVERY=1 DEVICE=cuda bash "$EXPERIMENT/launch_cell.sh" > "/workspace/canary_dualstream_dmem64_${CELL}.log" 2>&1
FINAL="$CANARY/rvit_paper_${TASK}_final.pt"; test -s "$FINAL"
env FINAL="$FINAL" CANARY="$CANARY" TASK="$TASK" "$PYTHON_BIN" - <<'PY'
import csv,math,os,torch
c=torch.load(os.environ['FINAL'],map_location='cpu',weights_only=False)
assert c['task']==os.environ['TASK']; assert c['iter']==20
assert c['initialization_contract']['mode']=='fresh'
assert math.isclose(float(c['ppo_config']['gamma']),1.0)
assert math.isclose(float(c['ppo_config']['bc_alpha']),0.0)
a=c['training_args']; assert a['dual_actor_critic_streams'] is True
assert int(a['d_mem'])==64
assert math.isclose(float(a['memory_noise_std']),0.075)
assert math.isclose(float(a['noise']),5.0); assert a['curriculum'] is True
assert int(a['curr_window'])==1000; assert math.isclose(float(a['curr_threshold']),0.85)
assert math.isclose(float(a['curr_step']),3.0); assert math.isclose(float(a['curr_floor']),8.0)
assert math.isclose(float(a['jepa_coef']),0.5)
e=c['environment_state']; assert e['curriculum'] is True
assert math.isclose(float(e['theta']),65.0); assert int(e['curr_window'])==1000
assert math.isclose(float(e['curr_threshold']),0.85); assert math.isclose(float(e['curr_step']),3.0)
assert math.isclose(float(e['theta_floor']),8.0)
assert int(c['model_kwargs']['d_mem'])==64
k=set(c['model_state_dict'])
assert any(x.startswith('critic_front.') for x in k)
assert any(x.startswith('critic_encoder.') for x in k)
assert any(x.startswith('jepa_branch_heads.0.') for x in k)
assert any(x.startswith('jepa_branch_heads.1.') for x in k)
with open(os.path.join(os.environ['CANARY'],'metrics.csv'),newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==1
for key in ('loss_jepa_actor','loss_jepa_critic','loss_policy','loss_value'):
    assert key in rows[0] and math.isfinite(float(rows[0][key]))
PY
CANARY_SHA="$(sha256sum "$FINAL" | cut -d' ' -f1)"; mkdir -p "$RUN_ROOT"
printf '{"source_archive_sha256":"%s","cell":"%s","grid":[2,2],"d_mem_per_branch":64,"dual_actor_critic_streams":true,"independent_jepa_branches":["actor","critic"],"jepa_coef_per_branch":0.5,"bc_alpha":0.0,"memory_noise_std":0.075,"sensory_noise_std":5.0,"gamma":1.0,"curriculum":{"enabled":true,"theta_start":65.0,"window":1000,"threshold":0.85,"step":3.0,"floor":8.0},"initialization":"fresh","canary_checkpoint_sha256":"%s"}\n' "$ACTUAL_SHA" "$CELL" "$CANARY_SHA" > "$RUN_ROOT/deployment_contract.json"
(
 set +e
 env CELL="$CELL" RUN_ROOT="$RUN_ROOT" PYTHON_BIN="$PYTHON_BIN" ITERS=20000 START_ITERATION=0 SAVE_EVERY=50 DEVICE=cuda bash "$EXPERIMENT/launch_cell.sh"
 code=$?; printf '%s\n' "$code" > "$RUN_ROOT/exit_code.txt"
 if [[ "$code" -eq 0 ]]; then touch "$RUN_ROOT/TRAINING_COMPLETE"; else touch "$RUN_ROOT/TRAINING_FAILED"; fi
 exit "$code"
) > "$RUN_ROOT/supervisor.log" 2>&1 </dev/null &
pid=$!; printf '%s\n' "$pid" > "$RUN_ROOT/supervisor.pid"
printf 'BOOTSTRAP_OK cell=%s d_mem=64 curriculum=true dual_streams=true bc_alpha=0.0 gamma=1.0 memory_noise=0.075 source_sha256=%s canary_sha256=%s pid=%s root=%s\n' "$CELL" "$ACTUAL_SHA" "$CANARY_SHA" "$pid" "$RUN_ROOT"
