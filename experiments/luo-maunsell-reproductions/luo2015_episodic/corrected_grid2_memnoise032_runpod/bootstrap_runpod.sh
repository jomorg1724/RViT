#!/usr/bin/env bash
set -euo pipefail
if [[ "$#" -ne 4 ]]; then echo "usage: $0 ARCHIVE EXPECTED_SHA RUN_ROOT SOURCE_DIR" >&2; exit 2; fi
ARCHIVE="$1"; EXPECTED_SHA="$2"; RUN_ROOT="$3"; SOURCE_DIR="$4"
ACTUAL_SHA="$(sha256sum "$ARCHIVE" | cut -d' ' -f1)"
[[ "$ACTUAL_SHA" == "$EXPECTED_SHA" ]] || { echo "archive hash mismatch" >&2; exit 10; }
if [[ -d "$SOURCE_DIR" ]] && [[ -n "$(find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
  echo "refusing non-empty source dir: $SOURCE_DIR" >&2; exit 11
fi
mkdir -p "$SOURCE_DIR"; tar --no-same-owner -xzf "$ARCHIVE" -C "$SOURCE_DIR"; cd "$SOURCE_DIR"
python3 -m venv --system-site-packages /workspace/rvit_venv
PYTHON_BIN=/workspace/rvit_venv/bin/python
if ! "$PYTHON_BIN" - <<'PY'
import gymnasium,imageio,matplotlib,numpy,pandas,PIL,pytest,scipy,torch
assert torch.cuda.is_available()
PY
then
  "$PYTHON_BIN" -m pip install --no-cache-dir pytest pandas pillow matplotlib imageio gymnasium scipy
fi
"$PYTHON_BIN" - <<'PY'
import torch
assert torch.cuda.is_available(); print({'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0)})
PY
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$PYTHON_BIN" -m pytest -q \
 tests/test_luo2015_protocol.py tests/test_luo2015_scientific_assay.py \
 tests/test_luo2015_attention_allocation.py tests/test_luo2015_episodic_experiment.py \
 tests/test_luo2015_corrected_grid_runpod.py tests/test_luo2015_corrected_grid2_memnoise032_runpod.py
CANARY=/workspace/canary_luo_corrected_grid2_memnoise032; rm -rf "$CANARY"
env RUN_ROOT="$CANARY" PYTHON_BIN="$PYTHON_BIN" ITERS=1 SAVE_EVERY=1 DEVICE=cuda \
 bash experiments/luo2015_episodic/corrected_grid2_memnoise032_runpod/launch_neutral.sh \
 > /workspace/canary_grid2_memnoise032.log 2>&1
test -s "$CANARY/rvit_paper_luo2015_criterion_final.pt"
CANARY_SHA="$(sha256sum "$CANARY/rvit_paper_luo2015_criterion_final.pt" | cut -d' ' -f1)"
mkdir -p "$RUN_ROOT"
printf '{"source_archive_sha256":"%s","grid":2,"memory_noise_std":0.32,"initialization":"fresh","canary_checkpoint_sha256":"%s"}\n' "$ACTUAL_SHA" "$CANARY_SHA" > "$RUN_ROOT/deployment_contract.json"
(
 set +e
 env RUN_ROOT="$RUN_ROOT" PYTHON_BIN="$PYTHON_BIN" ITERS=20000 SAVE_EVERY=50 DEVICE=cuda \
  bash experiments/luo2015_episodic/corrected_grid2_memnoise032_runpod/launch_neutral.sh
 code=$?; printf '%s\n' "$code" > "$RUN_ROOT/exit_code.txt"
 if [[ "$code" -eq 0 ]]; then touch "$RUN_ROOT/TRAINING_COMPLETE"; else touch "$RUN_ROOT/TRAINING_FAILED"; fi
 exit "$code"
) > "$RUN_ROOT/supervisor.log" 2>&1 </dev/null &
pid=$!; printf '%s\n' "$pid" > "$RUN_ROOT/supervisor.pid"
printf 'BOOTSTRAP_OK grid=2 memory_noise_std=0.32 source_sha256=%s canary_sha256=%s supervisor_pid=%s run_root=%s\n' "$ACTUAL_SHA" "$CANARY_SHA" "$pid" "$RUN_ROOT"
