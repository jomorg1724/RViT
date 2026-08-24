#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -eq 0 ]] || { printf 'USAGE: %s\n' "$0" >&2; exit 2; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CONFIG="$SCRIPT_DIR/config_v1.json"
DESIGN="$SCRIPT_DIR/design_manifest.json"
LAUNCHER="$SCRIPT_DIR/launch_canary_v1.sh"
PREFLIGHT="$SCRIPT_DIR/preflight_contract_v1.py"
EXPECTED_CONFIG_SHA256="01971fd731e030ed377f0c7db1164f0cf8c01285fbb57e7eda7381aed2414eb7"
EXPECTED_DESIGN_SHA256="1ae15e32b35687501554463a714074b6774e70aed524780ff14a733d832ec97b"
PYTHON_BIN="${PYTHON_BIN:-/workspace/rvit_venv/bin/python}"

[[ -x "$PYTHON_BIN" ]] || { printf 'ERROR: Python is not executable: %s\n' "$PYTHON_BIN" >&2; exit 2; }

runtime_fingerprint() {
  "$PYTHON_BIN" - <<'PY'
import hashlib, json, platform, subprocess, sys
import torch
if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable")
p = torch.cuda.get_device_properties(0)
smi = subprocess.check_output(["nvidia-smi","--query-gpu=uuid,name,driver_version,memory.total","--format=csv,noheader,nounits","--id=0"],text=True).strip()
payload={"python_executable":sys.executable,"python_version":platform.python_version(),"torch_version":str(torch.__version__),"torch_cuda":str(torch.version.cuda),"cudnn":int(torch.backends.cudnn.version() or 0),"gpu_index":0,"gpu_name":p.name,"gpu_capability":[p.major,p.minor],"gpu_total_memory":int(p.total_memory),"nvidia_smi":smi}
print(hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",", ":")).encode()).hexdigest())
PY
}

# Fail both registered engineering cells closed before launching the first.
for MEMORY_NOISE_STD in 0.0 0.5; do
  "$PYTHON_BIN" "$PREFLIGHT" \
    --project-root "$PROJECT_ROOT" \
    --config "$CONFIG" \
    --design "$DESIGN" \
    --launcher "$LAUNCHER" \
    --expected-config-sha256 "$EXPECTED_CONFIG_SHA256" \
    --expected-design-sha256 "$EXPECTED_DESIGN_SHA256" \
    --memory-noise-std "$MEMORY_NOISE_STD" \
    --seed 0 \
    --run-kind canary
done

export VDA_PAIR_ID="canary_$("$PYTHON_BIN" -c 'from datetime import datetime,timezone; import uuid; print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"_"+uuid.uuid4().hex[:12])')"
export VDA_PAIR_RUNTIME_SHA256="$(runtime_fingerprint)"
printf 'QUEUE_PREFLIGHT_PASS|run_kind=canary|conditions=2|seed=0|pair_id=%s|runtime_sha256=%s|evidence=engineering_only\n' \
  "$VDA_PAIR_ID" "$VDA_PAIR_RUNTIME_SHA256"

for MEMORY_NOISE_STD in 0.0 0.5; do
  CURRENT_RUNTIME_SHA256="$(runtime_fingerprint)"
  [[ "$CURRENT_RUNTIME_SHA256" == "$VDA_PAIR_RUNTIME_SHA256" ]] || {
    printf 'ERROR: runtime/GPU fingerprint changed inside canary pair\n' >&2
    exit 2
  }
  bash "$LAUNCHER" "$MEMORY_NOISE_STD" 0
done

CURRENT_RUNTIME_SHA256="$(runtime_fingerprint)"
[[ "$CURRENT_RUNTIME_SHA256" == "$VDA_PAIR_RUNTIME_SHA256" ]] || {
  printf 'ERROR: runtime/GPU fingerprint changed after canary pair\n' >&2
  exit 2
}
printf 'QUEUE_COMPLETE|run_kind=canary|conditions=2|seed=0|pair_id=%s|scientific_evidence=false\n' "$VDA_PAIR_ID"
