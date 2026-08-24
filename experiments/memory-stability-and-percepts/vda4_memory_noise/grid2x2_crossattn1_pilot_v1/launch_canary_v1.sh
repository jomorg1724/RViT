#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -eq 2 ]] || {
  printf 'USAGE: %s MEMORY_NOISE_STD SEED\n' "$0" >&2
  exit 2
}
MEMORY_NOISE_STD="$1"
SEED="$2"

case "$MEMORY_NOISE_STD" in 0.0|0.5) ;; *) printf 'ERROR: MEMORY_NOISE_STD must be 0.0 or 0.5\n' >&2; exit 2 ;; esac
[[ "$SEED" == "0" ]] || { printf 'ERROR: paired-pilot-v1 canaries are frozen to seed 0\n' >&2; exit 2; }
: "${VDA_PAIR_ID:?VDA_PAIR_ID must be set by queue_canaries_v1.sh}"
: "${VDA_PAIR_RUNTIME_SHA256:?VDA_PAIR_RUNTIME_SHA256 must be set by queue_canaries_v1.sh}"

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
[[ -f "$PROJECT_ROOT/train_rl.py" ]] || { printf 'ERROR: project root is incomplete: %s\n' "$PROJECT_ROOT" >&2; exit 2; }

runtime_fingerprint() {
  "$PYTHON_BIN" - <<'PY'
import hashlib, json, platform, subprocess, sys
import torch
if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable")
p = torch.cuda.get_device_properties(0)
smi = subprocess.check_output([
    "nvidia-smi", "--query-gpu=uuid,name,driver_version,memory.total",
    "--format=csv,noheader,nounits", "--id=0"
], text=True).strip()
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
blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
print(hashlib.sha256(blob).hexdigest())
PY
}

CURRENT_RUNTIME_SHA256="$(runtime_fingerprint)"
[[ "$CURRENT_RUNTIME_SHA256" == "$VDA_PAIR_RUNTIME_SHA256" ]] || {
  printf 'ERROR: runtime/GPU fingerprint changed before canary launch: %s != %s\n' \
    "$CURRENT_RUNTIME_SHA256" "$VDA_PAIR_RUNTIME_SHA256" >&2
  exit 2
}

PREFLIGHT_ARGS=(
  --project-root "$PROJECT_ROOT"
  --config "$CONFIG"
  --design "$DESIGN"
  --launcher "$LAUNCHER"
  --expected-config-sha256 "$EXPECTED_CONFIG_SHA256"
  --expected-design-sha256 "$EXPECTED_DESIGN_SHA256"
  --memory-noise-std "$MEMORY_NOISE_STD"
  --seed "$SEED"
  --run-kind canary
)
"$PYTHON_BIN" "$PREFLIGHT" "${PREFLIGHT_ARGS[@]}"

case "$MEMORY_NOISE_STD" in 0.0) CONDITION_ID="noise0p0" ;; 0.5) CONDITION_ID="noise0p5" ;; esac
RUN_STAMP="$("$PYTHON_BIN" -c 'from datetime import datetime, timezone; import uuid; print(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:12])')"
CHECKPOINT_DIR="/workspace/vda4_memory_noise_grid2x2_crossattn1_${CONDITION_ID}_seed${SEED}_canary_v1_${RUN_STAMP}"
mkdir "$CHECKPOINT_DIR"
TRAIN_LOG="$CHECKPOINT_DIR/train.log"

VDA_RUNTIME_OUTPUT="$CHECKPOINT_DIR/runtime_identity.json" \
  "$PYTHON_BIN" -c 'import json,os,subprocess; from datetime import datetime,timezone; p={"schema_version":1,"pair_id":os.environ["VDA_PAIR_ID"],"runtime_sha256":os.environ["VDA_PAIR_RUNTIME_SHA256"],"gpu_uuid":subprocess.check_output(["nvidia-smi","--query-gpu=uuid","--format=csv,noheader","--id=0"],text=True).strip(),"recorded_at_utc":datetime.now(timezone.utc).isoformat()}; open(os.environ["VDA_RUNTIME_OUTPUT"],"w",encoding="utf-8").write(json.dumps(p,indent=2,sort_keys=True)+"\n")'

TRAIN_ARGS=(
  --config "$CONFIG"
  --task vda4
  --T 7
  --frame-repeat 1
  --min-change-time 5
  --max-change-time 5
  --noise 5.0
  --patch-grid-rows 2
  --patch-grid-cols 2
  --cell xlstm
  --feedback crossattn1
  --d-mem 128
  --memory-decay 1.0
  --memory-noise-std "$MEMORY_NOISE_STD"
  --conv-frontend
  --n-actions 2
  --n-quantiles 5
  --init-action-bias 0.0 -1.5
  --jepa-coef 0.5
  --jepa-heads 4
  --jepa-proto-dim 256
  --jepa-tau-student 0.1
  --jepa-tau-teacher-start 0.04
  --jepa-tau-teacher-end 0.07
  --jepa-tau-warmup 300
  --jepa-center-momentum 0.9
  --jepa-ema-decay 0.996
  --curriculum
  --theta-start 65.0
  --curr-window 1000
  --curr-threshold 0.85
  --curr-step 3.0
  --curr-floor 8.0
  --lr 0.0003
  --gamma 0.95
  --entropy-coef 0.01
  --ema-decay 0.995
  --buffer-capacity 1000
  --qr-kappa 1.0
  --mpo-temperature 0.1
  --init-mode fresh
  --start-iteration 0
  --checkpoint-dir "$CHECKPOINT_DIR"
  --iters 50
  --schedule-final-iteration 19999
  --episodes-per-iter 8
  --save-every 50
  --log-every 1
  --seed "$SEED"
  --device cuda
  --experiment-launcher "$LAUNCHER"
)

"$PYTHON_BIN" "$PREFLIGHT" "${PREFLIGHT_ARGS[@]}" \
  --run-dir "$CHECKPOINT_DIR" --emit-json > "$CHECKPOINT_DIR/launch_contract.json"

printf 'RUN_DIR=%s\n' "$CHECKPOINT_DIR"
printf 'TRAIN_LOG=%s\n' "$TRAIN_LOG"
printf 'CONTRACT=%s\n' "$CHECKPOINT_DIR/launch_contract.json"
printf 'PAIR_ID=%s\n' "$VDA_PAIR_ID"
printf 'PAIR_RUNTIME_SHA256=%s\n' "$VDA_PAIR_RUNTIME_SHA256"
printf 'EVIDENCE_CLASS=engineering_only_not_scientific_evidence\n'

export PYTHONUNBUFFERED=1
exec "$PYTHON_BIN" -u "$PROJECT_ROOT/train_rl.py" "${TRAIN_ARGS[@]}" \
  > >(tee -a "$TRAIN_LOG") 2>&1
