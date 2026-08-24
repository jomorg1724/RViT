#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -eq 0 ]] || {
  printf 'USAGE: %s\n' "$0" >&2
  exit 2
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$SCRIPT_DIR/launch_production_v1.sh"
PYTHON_BIN="${PYTHON_BIN:-/workspace/rvit_venv/bin/python}"

[[ -x "$PYTHON_BIN" ]] || {
  printf 'ERROR: Python is not executable: %s\n' "$PYTHON_BIN" >&2
  exit 2
}
[[ -f "$LAUNCHER" ]] || {
  printf 'ERROR: production launcher is missing: %s\n' "$LAUNCHER" >&2
  exit 2
}

runtime_fingerprint() {
  "$PYTHON_BIN" - <<'PY'
import hashlib
import json
import platform
import subprocess
import sys

import torch

if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable")
p = torch.cuda.get_device_properties(0)
smi = subprocess.check_output(
    [
        "nvidia-smi",
        "--query-gpu=uuid,name,driver_version,memory.total",
        "--format=csv,noheader,nounits",
        "--id=0",
    ],
    text=True,
).strip()
payload = {
    "python_executable": sys.executable,
    "python_version": platform.python_version(),
    "torch_version": str(torch.__version__),
    "torch_cuda": str(torch.version.cuda),
    "cudnn": int(torch.backends.cudnn.version() or 0),
    "gpu_index": 0,
    "gpu_name": p.name,
    "gpu_capability": [p.major, p.minor],
    "gpu_total_memory": int(p.total_memory),
    "nvidia_smi": smi,
}
print(
    hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
)
PY
}

export VDA_PAIR_ID="production_$(
  "$PYTHON_BIN" -c 'from datetime import datetime, timezone; import uuid; print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:12])'
)"
export VDA_PAIR_RUNTIME_SHA256="$(runtime_fingerprint)"

printf 'SCOPE_OVERRIDE|requested_condition=noise0p5|memory_noise_std=0.5|seed=0|iterations=20000|fresh=true|baseline_retraining=false|user_authorized=true\n'
printf 'HISTORICAL_CLEAN_REFERENCE|checkpoint_sha256=ea671f9758551e06b39ef19c06e85e888ce3ee74dda8a534c1532251a69ee4ca\n'
printf 'RUN_ID=%s\n' "$VDA_PAIR_ID"
printf 'RUNTIME_SHA256=%s\n' "$VDA_PAIR_RUNTIME_SHA256"

exec bash "$LAUNCHER" 0.5 0
