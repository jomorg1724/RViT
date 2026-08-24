#!/usr/bin/env bash
set -euo pipefail
if [[ "$#" -ne 5 ]]; then echo "usage: $0 ARCHIVE SHA CELL LADDER_ROOT SOURCE_DIR" >&2; exit 2; fi
ARCHIVE="$1"; EXPECTED_SHA="$2"; CELL="$3"; LADDER_ROOT="$4"; SOURCE_DIR="$5"
ACTUAL_SHA="$(sha256sum "$ARCHIVE" | cut -d' ' -f1)"; [[ "$ACTUAL_SHA" == "$EXPECTED_SHA" ]] || { echo archive-hash-mismatch >&2; exit 10; }
if [[ -d "$SOURCE_DIR" ]] && ! python3 - "$SOURCE_DIR" <<'PY'
from pathlib import Path
import sys
raise SystemExit(0 if not any(Path(sys.argv[1]).iterdir()) else 1)
PY
then echo refusing-nonempty-source-dir >&2; exit 11; fi
[[ ! -e "$LADDER_ROOT" ]] || { echo refusing-preexisting-ladder-root >&2; exit 12; }
mkdir -p "$SOURCE_DIR"; tar --no-same-owner -xzf "$ARCHIVE" -C "$SOURCE_DIR"; cd "$SOURCE_DIR"
PYTHON_BIN=/workspace/rvit_venv/bin/python
[[ -x "$PYTHON_BIN" ]] || python3 -m venv --system-site-packages /workspace/rvit_venv
if ! "$PYTHON_BIN" - <<'PY'
import gymnasium,imageio,matplotlib,numpy,pandas,PIL,pytest,scipy,torch
PY
then "$PYTHON_BIN" -m pip install --no-cache-dir pytest pandas pillow matplotlib imageio gymnasium scipy; fi
"$PYTHON_BIN" - <<'PY'
import torch
assert torch.cuda.is_available(); print({'torch':torch.__version__,'gpu':torch.cuda.get_device_name(0)})
PY
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PYTHON_BIN" -m pytest -q \
 tests/test_luo2015_protocol.py tests/test_luo2015_scientific_assay.py \
 tests/test_luo2015_attention_allocation.py tests/test_luo2015_episodic_experiment.py \
 tests/test_luo2015_fresh_gamma070_reward_matrix_runpod.py \
 tests/test_luo2015_fresh_gamma_ladder_runpod.py
case "$CELL" in sensitivity_*) TASK=luo2015_sensitivity;; criterion_*) TASK=luo2015_criterion;; *) exit 2;; esac
CANARY="/workspace/canary_luo_gamma080_${CELL}"; rm -rf "$CANARY"
env CELL="$CELL" GAMMA=0.8 RUN_ROOT="$CANARY" PYTHON_BIN="$PYTHON_BIN" ITERS=1 SAVE_EVERY=1 DEVICE=cuda bash experiments/luo2015_episodic/fresh_grid2_memnoise032_gamma_ladder_runpod/launch_cell.sh > "/workspace/canary_gamma080_${CELL}.log" 2>&1
FINAL="$CANARY/rvit_paper_${TASK}_final.pt"; test -s "$FINAL"; CANARY_SHA="$(sha256sum "$FINAL" | cut -d' ' -f1)"
mkdir -p "$LADDER_ROOT"
printf '{"source_archive_sha256":"%s","cell":"%s","gammas":[0.8,0.9,1.0],"initialization_each_stage":"fresh","canary_gamma":0.8,"canary_checkpoint_sha256":"%s"}\n' "$ACTUAL_SHA" "$CELL" "$CANARY_SHA" > "$LADDER_ROOT/deployment_contract.json"
(
 set +e
 env CELL="$CELL" LADDER_ROOT="$LADDER_ROOT" PYTHON_BIN="$PYTHON_BIN" bash experiments/luo2015_episodic/fresh_grid2_memnoise032_gamma_ladder_runpod/run_ladder.sh
 code=$?; printf '%s\n' "$code" > "$LADDER_ROOT/ladder_exit_code.txt"
 if [[ "$code" -eq 0 ]]; then touch "$LADDER_ROOT/LADDER_SUPERVISOR_COMPLETE"; else touch "$LADDER_ROOT/LADDER_FAILED"; fi
 exit "$code"
) > "$LADDER_ROOT/ladder_supervisor.log" 2>&1 </dev/null &
pid=$!; printf '%s\n' "$pid" > "$LADDER_ROOT/ladder_supervisor.pid"
printf 'LADDER_BOOTSTRAP_OK cell=%s gammas=0.8,0.9,1.0 source_sha256=%s canary_sha256=%s pid=%s root=%s\n' "$CELL" "$ACTUAL_SHA" "$CANARY_SHA" "$pid" "$LADDER_ROOT"
