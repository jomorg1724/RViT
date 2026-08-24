[CmdletBinding()]
param(
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",

    [ValidateRange(1, 2147483647)]
    [int]$Iterations = 20000,

    [ValidateRange(1, 2147483647)]
    [int]$EpisodesPerIteration = 8,

    [int]$Seed = 0,

    # Keep frequently replaced checkpoints out of the OneDrive-synced source tree.
    [string]$OutputRoot = (Join-Path (Join-Path $env:USERPROFILE "Documents") "RViT_runs"),

    [string]$PythonExe = "python",

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# The archived sources print scientific symbols that fail under the default
# Windows cp1252 console encoding. Keep both Python and PowerShell on UTF-8.
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Trainer = Join-Path $ProjectRoot "train_rl.py"
if (-not (Test-Path -LiteralPath $Trainer -PathType Leaf)) {
    throw "Training entry point not found: $Trainer"
}

$PythonCommand = Get-Command $PythonExe -ErrorAction Stop
$Preflight = @'
import sys
import torch
from envs import TASKS

device = sys.argv[1]
if 'vda16' not in TASKS:
    raise SystemExit('vda16 is not registered in envs.TASKS')
if device == 'cuda' and not torch.cuda.is_available():
    raise SystemExit('CUDA was requested, but torch.cuda.is_available() is false')

print(f'[preflight] python={sys.executable}')
print(f'[preflight] torch={torch.__version__}')
if device == 'cuda':
    print(f'[preflight] cuda={torch.cuda.get_device_name(0)}')
'@

Push-Location $ProjectRoot
try {
    & $PythonCommand.Source -c $Preflight $Device
    if ($LASTEXITCODE -ne 0) {
        throw "Python/CUDA preflight failed with exit code $LASTEXITCODE"
    }

    $RunStamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
    $RunId = [Guid]::NewGuid().ToString("N").Substring(0, 12)
    $RunName = "vda16_affine_ew_d128_nodecay_replay_excluded_seed${Seed}_${RunStamp}_${RunId}"
    $CheckpointDir = Join-Path ([System.IO.Path]::GetFullPath($OutputRoot)) $RunName
    $ScheduleFinalIteration = $Iterations - 1

    $TrainingArguments = @(
        $Trainer,
        "--task", "vda16",
        "--T", "7",
        "--min-change-time", "5",
        "--max-change-time", "5",
        "--cell", "xlstm",
        "--feedback", "affine_ew",
        "--memory-decay", "1.0",
        "--conv-frontend",
        "--patch-grid-rows", "4",
        "--patch-grid-cols", "4",
        "--jepa-coef", "0.5",
        "--d-mem", "128",
        "--curriculum",
        "--init-mode", "fresh",
        "--checkpoint-dir", $CheckpointDir,
        "--iters", [string]$Iterations,
        "--schedule-final-iteration", [string]$ScheduleFinalIteration,
        "--episodes-per-iter", [string]$EpisodesPerIteration,
        "--save-every", "50",
        "--log-every", "1",
        "--seed", [string]$Seed,
        "--device", $Device,
        "--experiment-launcher", $PSCommandPath
    )

    Write-Host ""
    Write-Host "VDA16 fresh training plan"
    Write-Host "  feedback:       affine_ew"
    Write-Host "  memory decay:   1.0 (no added decay)"
    Write-Host "  device:         $Device"
    Write-Host "  iterations:     $Iterations"
    Write-Host "  episodes/iter:  $EpisodesPerIteration"
    Write-Host "  seed:           $Seed"
    Write-Host "  output:         $CheckpointDir"
    Write-Host ""
    Write-Host ("Command: {0} {1}" -f $PythonCommand.Source, ($TrainingArguments -join " "))

    if ($DryRun) {
        Write-Host ""
        Write-Host "Dry run complete; training was not started."
        return
    }

    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $CheckpointDir -ErrorAction Stop | Out-Null

    $Manifest = [ordered]@{
        schema_version            = 1
        created_at_utc           = [DateTime]::UtcNow.ToString("o")
        task                     = "vda16"
        feedback                 = "affine_ew"
        memory_decay             = 1.0
        d_mem                    = 128
        patch_grid_rows          = 4
        patch_grid_cols          = 4
        initialization           = "fresh"
        curriculum               = $true
        seed                     = $Seed
        device                   = $Device
        iterations               = $Iterations
        episodes_per_iteration   = $EpisodesPerIteration
        schedule_final_iteration = $ScheduleFinalIteration
        checkpoint_directory     = $CheckpointDir
        python                   = $PythonCommand.Source
        launcher                 = $PSCommandPath
        argv                     = @($PythonCommand.Source) + $TrainingArguments
    }
    $ManifestPath = Join-Path $CheckpointDir "launch_manifest.json"
    $ManifestJson = $Manifest | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText(
        $ManifestPath,
        $ManifestJson + [Environment]::NewLine,
        [System.Text.UTF8Encoding]::new($false)
    )

    Write-Host ""
    Write-Host "Starting training. Keep this terminal open."
    Write-Host "Rolling checkpoint: $(Join-Path $CheckpointDir 'rvit_plus_rl_latest.pt')"
    Write-Host "Metrics:            $(Join-Path $CheckpointDir 'metrics.csv')"
    Write-Host "Terminal log:       $(Join-Path $CheckpointDir 'train.log')"
    Write-Host ""

    $TrainLog = Join-Path $CheckpointDir "train.log"
    & $PythonCommand.Source @TrainingArguments 2>&1 | Tee-Object -FilePath $TrainLog
    $TrainingExitCode = $LASTEXITCODE
    if ($TrainingExitCode -ne 0) {
        throw "VDA16 training exited with code $TrainingExitCode"
    }
}
finally {
    Pop-Location
}
