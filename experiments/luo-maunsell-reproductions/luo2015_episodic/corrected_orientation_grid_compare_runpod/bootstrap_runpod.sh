#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 5 ]]; then
  echo "usage: $0 ARCHIVE EXPECTED_SHA256 GRID RUN_ROOT SOURCE_DIR" >&2
  exit 2
fi
ARCHIVE="$1"
EXPECTED_SHA256="$2"
GRID="$3"
RUN_ROOT="$4"
SOURCE_DIR="$5"

case "$GRID" in 20|2) ;; *) echo "invalid GRID=$GRID" >&2; exit 2;; esac
ACTUAL_SHA256="$(sha256sum "$ARCHIVE" | cut -d' ' -f1)"
if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
  echo "archive hash mismatch: expected=$EXPECTED_SHA256 actual=$ACTUAL_SHA256" >&2
  exit 10
fi

if [[ -d "$SOURCE_DIR" ]] && [[ -n "$(find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo "refusing to overwrite non-empty source directory: $SOURCE_DIR" >&2
  exit 11
fi
mkdir -p "$SOURCE_DIR"
tar --no-same-owner -xzf "$ARCHIVE" -C "$SOURCE_DIR"
cd "$SOURCE_DIR"

python3 -m venv --system-site-packages /workspace/rvit_venv
PYTHON_BIN=/workspace/rvit_venv/bin/python
if ! "$PYTHON_BIN" - <<'PY'
import gymnasium, imageio, matplotlib, numpy, pandas, PIL, pytest, scipy, torch
assert torch.cuda.is_available(), "CUDA is unavailable"
print({"torch": torch.__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)})
PY
then
  "$PYTHON_BIN" -m pip install --no-cache-dir pytest pandas pillow matplotlib imageio gymnasium scipy
fi
"$PYTHON_BIN" - <<'PY'
import torch
assert torch.cuda.is_available(), "CUDA is unavailable after dependency setup"
print({"torch": torch.__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)})
PY

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PYTHON_BIN" -m pytest -q \
  tests/test_luo2015_protocol.py \
  tests/test_luo2015_scientific_assay.py \
  tests/test_luo2015_attention_allocation.py \
  tests/test_luo2015_episodic_experiment.py \
  tests/test_luo2015_corrected_grid_runpod.py

CANARY_ROOT="/workspace/canary_luo_corrected_grid${GRID}"
rm -rf "$CANARY_ROOT"
env GRID="$GRID" RUN_ROOT="$CANARY_ROOT" PYTHON_BIN="$PYTHON_BIN" ITERS=1 SAVE_EVERY=1 DEVICE=cuda \
  bash experiments/luo2015_episodic/corrected_orientation_grid_compare_runpod/launch_neutral.sh \
  > "/workspace/canary_grid${GRID}.log" 2>&1
CANARY_CHECKPOINT="$CANARY_ROOT/rvit_paper_luo2015_criterion_final.pt"
test -s "$CANARY_CHECKPOINT"
CANARY_SHA256="$(sha256sum "$CANARY_CHECKPOINT" | cut -d' ' -f1)"

mkdir -p "$RUN_ROOT"
cat > "$RUN_ROOT/deployment_contract.json" <<JSON
{
  "source_archive_sha256": "$ACTUAL_SHA256",
  "grid": $GRID,
  "run_root": "$RUN_ROOT",
  "initialization": "fresh",
  "canary_checkpoint_sha256": "$CANARY_SHA256"
}
JSON

(
  set +e
  env GRID="$GRID" RUN_ROOT="$RUN_ROOT" PYTHON_BIN="$PYTHON_BIN" ITERS=20000 SAVE_EVERY=50 DEVICE=cuda \
    bash experiments/luo2015_episodic/corrected_orientation_grid_compare_runpod/launch_neutral.sh
  code=$?
  printf '%s\n' "$code" > "$RUN_ROOT/exit_code.txt"
  if [[ "$code" -eq 0 ]]; then touch "$RUN_ROOT/TRAINING_COMPLETE"; else touch "$RUN_ROOT/TRAINING_FAILED"; fi
  exit "$code"
) > "$RUN_ROOT/supervisor.log" 2>&1 </dev/null &
SUPERVISOR_PID=$!
printf '%s\n' "$SUPERVISOR_PID" > "$RUN_ROOT/supervisor.pid"

printf 'BOOTSTRAP_OK grid=%s source_sha256=%s canary_sha256=%s supervisor_pid=%s run_root=%s\n' \
  "$GRID" "$ACTUAL_SHA256" "$CANARY_SHA256" "$SUPERVISOR_PID" "$RUN_ROOT"
