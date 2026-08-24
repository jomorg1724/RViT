#!/usr/bin/env bash
set -euo pipefail
if [[ "$#" -ne 5 ]]; then echo "usage: $0 ARCHIVE SHA CELL RUN_ROOT SOURCE_DIR" >&2; exit 2; fi
ARCHIVE="$1"; EXPECTED_SHA="$2"; CELL="$3"; RUN_ROOT="$4"; SOURCE_DIR="$5"
case "$CELL" in sensitivity_loc0|sensitivity_loc3) TASK=luo2015_sensitivity;; criterion_loc0|criterion_loc3) TASK=luo2015_criterion;; *) exit 2;; esac
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
 tests/test_luo2015_protocol.py tests/test_luo2015_scientific_assay.py \
 tests/test_luo2015_attention_allocation.py tests/test_luo2015_episodic_experiment.py \
 tests/test_luo2015_fresh_gamma_ladder_runpod.py tests/test_luo2015_fresh_memnoise016_gamma080_runpod.py
CANARY="/workspace/canary_luo_memnoise016_gamma080_${CELL}"; rm -rf "$CANARY"
env CELL="$CELL" RUN_ROOT="$CANARY" PYTHON_BIN="$PYTHON_BIN" ITERS=1 SAVE_EVERY=1 DEVICE=cuda bash experiments/luo2015_episodic/fresh_grid2_memnoise016_gamma080_reward_matrix_runpod/launch_cell.sh > "/workspace/canary_memnoise016_${CELL}.log" 2>&1
FINAL="$CANARY/rvit_paper_${TASK}_final.pt"; test -s "$FINAL"
env FINAL="$FINAL" TASK="$TASK" "$PYTHON_BIN" - <<'PY'
import math,os,torch
c=torch.load(os.environ['FINAL'],map_location='cpu',weights_only=False)
assert c['task']==os.environ['TASK']; assert c['initialization_contract']['mode']=='fresh'; assert math.isclose(float(c['ppo_config']['gamma']),0.8)
a=c['training_args']; assert math.isclose(float(a['memory_noise_std']),0.16); assert math.isclose(float(a['noise']),5.0); assert a['curriculum'] is False
assert math.isclose(float(c['environment_state']['theta']),65.0)
PY
CANARY_SHA="$(sha256sum "$FINAL" | cut -d' ' -f1)"; mkdir -p "$RUN_ROOT"
printf '{"source_archive_sha256":"%s","cell":"%s","grid":[2,2],"memory_noise_std":0.16,"sensory_noise_std":5.0,"gamma":0.8,"initialization":"fresh","canary_checkpoint_sha256":"%s"}\n' "$ACTUAL_SHA" "$CELL" "$CANARY_SHA" > "$RUN_ROOT/deployment_contract.json"
(
 set +e
 env CELL="$CELL" RUN_ROOT="$RUN_ROOT" PYTHON_BIN="$PYTHON_BIN" ITERS=20000 SAVE_EVERY=50 DEVICE=cuda bash experiments/luo2015_episodic/fresh_grid2_memnoise016_gamma080_reward_matrix_runpod/launch_cell.sh
 code=$?; printf '%s\n' "$code" > "$RUN_ROOT/exit_code.txt"
 if [[ "$code" -eq 0 ]]; then touch "$RUN_ROOT/TRAINING_COMPLETE"; else touch "$RUN_ROOT/TRAINING_FAILED"; fi
 exit "$code"
) > "$RUN_ROOT/supervisor.log" 2>&1 </dev/null &
pid=$!; printf '%s\n' "$pid" > "$RUN_ROOT/supervisor.pid"
printf 'BOOTSTRAP_OK cell=%s gamma=0.8 memory_noise=0.16 source_sha256=%s canary_sha256=%s pid=%s root=%s\n' "$CELL" "$ACTUAL_SHA" "$CANARY_SHA" "$pid" "$RUN_ROOT"
