# Resume launcher v2 for vda4_modern_fsq2_c1_a01_j0001_lr2e4_s0_v1
# Continues resume-1 (killed 2026-08-20 at iter 10499) through schedule end 19999.
# Producer hashes verified identical to the resume-1 checkpoint's resume_contract.
param(
  [string]$RUN_ROOT = "C:\Users\jomor\Documents\RViT_runs\vda4_fsq2_c1_a01_j0001_lr2e4_s0_v1_prod_resume2_20260821",
  [string]$PYTHON_BIN = "C:\Python310\python.exe",
  [int]$ITERS = 9500
)
$ErrorActionPreference = "Continue"
$scheduleFinal = 19999
$parentCkpt = "C:\Users\jomor\Documents\RViT_runs\vda4_fsq2_c1_a01_j0001_lr2e4_s0_v1_prod_resume_20260819\rvit_plus_rl_latest.pt"

if (-not (Test-Path $parentCkpt)) { throw "parent checkpoint not found: $parentCkpt" }
if (Test-Path $RUN_ROOT) { throw "refusing pre-existing RUN_ROOT: $RUN_ROOT" }

$projRoot = "C:\Users\jomor\OneDrive\Desktop\RViT_plus_paper_jepa_grid9-20260718T193411Z-1-001\RViT_plus_paper_jepa_grid9"
$expDir = Join-Path $projRoot "experiments\vda4_transformer_memory\grid2x2_modern_fsq2_c1_a01_j0001_lr2e4_s0_v1"
$launcher = Join-Path $expDir "launch_local_v1.sh"

New-Item -ItemType Directory -Path $RUN_ROOT | Out-Null
New-Item -ItemType Directory -Path "$RUN_ROOT\provenance\source_snapshot\envs", "$RUN_ROOT\provenance\source_snapshot\tests" -Force | Out-Null

Copy-Item "$expDir\design_manifest.json" "$RUN_ROOT\design_manifest.json" -ErrorAction SilentlyContinue
foreach ($f in @("model.py", "paper_encoder.py", "paper_heads.py", "conv_frontend.py", "train_rl.py", "ppo.py")) {
  Copy-Item (Join-Path $projRoot $f) "$RUN_ROOT\provenance\source_snapshot\" -ErrorAction SilentlyContinue
}
Copy-Item "$projRoot\envs\base.py" "$RUN_ROOT\provenance\source_snapshot\envs\" -ErrorAction SilentlyContinue
foreach ($t in @("test_fsq_quantize.py", "test_fsq_integration.py", "test_modern_transformer_memory.py",
                 "test_softmax_memory_anticollapse.py", "test_loss_weight_hierarchy.py")) {
  Copy-Item (Join-Path $projRoot "tests\$t") "$RUN_ROOT\provenance\source_snapshot\tests\" -ErrorAction SilentlyContinue
}

$hashTargets = @("model.py", "paper_encoder.py", "paper_heads.py", "conv_frontend.py", "train_rl.py", "ppo.py",
                 "envs\base.py") + (Get-ChildItem "$RUN_ROOT\provenance\source_snapshot\tests" | ForEach-Object Name)
$hashLines = foreach ($rel in $hashTargets) {
  $p = Join-Path $projRoot $rel
  if (Test-Path $p) { "{0}  {1}" -f (Get-FileHash $p -Algorithm SHA256).Hash, $rel }
}
if (Test-Path "$expDir\design_manifest.json") { $hashLines += ("{0}  {1}" -f (Get-FileHash "$expDir\design_manifest.json" -Algorithm SHA256).Hash, "design_manifest.json") }
if (Test-Path $launcher) { $hashLines += ("{0}  {1}" -f (Get-FileHash $launcher -Algorithm SHA256).Hash, "launch_local_v1.sh") }
$hashLines | Sort-Object | Set-Content "$RUN_ROOT\provenance_sha256.txt"

@"
experiment=vda4_modern_fsq2_c1_a01_j0001_lr2e4_s0_v1 (RESUME 2)
parent_run_root=C:/Users/jomor/Documents/RViT_runs/vda4_fsq2_c1_a01_j0001_lr2e4_s0_v1_prod_resume_20260819
parent_killed_iter=10499
resume_mode=stateful (replay-excluded trainer state, schema-v3)
fsq_levels=2
objective_hierarchy=critic_1.0_gt_actor_0.1_gt_jepa_0.001__bc_alpha_0.0
lr=0.0002
run_root=$RUN_ROOT
resume_iters=$ITERS
schedule_final_iteration=$scheduleFinal
device=cuda
gamma=0.95
theta_contract=start65_window1000_threshold0.85_subtract3_floor8_nonoverlapping
"@ | Set-Content "$RUN_ROOT\launch_contract.txt"

$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"
$trainLog = "$RUN_ROOT\train.stdout.log"
& $PYTHON_BIN -u (Join-Path $projRoot "train_rl.py") `
  --task vda4 --T 7 --frame-repeat 1 --min-change-time 5 --max-change-time 5 --noise 5.0 `
  --patch-grid-rows 2 --patch-grid-cols 2 `
  --cell transformer_memory_2layer_softmax_modern --feedback crossattn1 `
  --d-mem 128 --mem-heads 4 --memory-decay 1.0 --memory-noise-std 0.0 --conv-frontend `
  --n-actions 2 --n-quantiles 5 --init-action-bias 0.0 -1.5 `
  --value-coef 1.0 --actor-coef 0.1 --jepa-coef 0.001 --bc-alpha 0.0 --fsq-levels 2 `
  --jepa-heads 4 --jepa-proto-dim 256 --jepa-tau-student 0.1 `
  --jepa-tau-teacher-start 0.03 --jepa-tau-teacher-end 0.05 --jepa-tau-warmup 300 `
  --jepa-center-momentum 0.9 --jepa-ema-decay 0.996 --jepa-sinkhorn-iters 3 `
  --jepa-var-coef 1.0 --jepa-cov-coef 0.01 `
  --curriculum --theta-start 65.0 --curr-window 1000 --curr-threshold 0.85 --curr-step 3.0 --curr-floor 8.0 `
  --lr 0.0002 --gamma 0.95 --entropy-coef 0.01 --ema-decay 0.995 --buffer-capacity 1000 `
  --qr-kappa 1.0 --mpo-temperature 0.1 `
  --init-mode resume --checkpoint-path $parentCkpt `
  --checkpoint-dir $RUN_ROOT `
  --iters $ITERS --schedule-final-iteration $scheduleFinal `
  --episodes-per-iter 8 --save-every 50 --log-every 1 --seed 0 --device cuda `
  --experiment-launcher $launcher *> $trainLog
exit $LASTEXITCODE
