param(
    [string]$QueueTag = "production_20260727",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",
    [ValidateRange(5, 300)]
    [int]$PollSeconds = 30
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Python = (Get-Command python -ErrorAction Stop).Source
$Producer = Join-Path $ProjectRoot "analysis\vda4_spatial_scaling_evaluation.py"
$OutputRoot = Join-Path $ProjectRoot ("reports\vda_series\spatial_scaling_evaluation_{0}" -f $QueueTag)
$QueueManifestPath = Join-Path $OutputRoot "QUEUE_MANIFEST.json"
$LogRoot = Join-Path $OutputRoot "queue_logs"
$FollowupManifestPath = Join-Path $OutputRoot "AFFINE2_FOLLOWUP_MANIFEST.json"
$RunRoot = Join-Path $env:USERPROFILE "Documents\RViT_runs"
New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

$Manifest = [ordered]@{
    schema_version = 1
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    status = "waiting_for_primary_queue"
    queue_manifest = $QueueManifestPath
    device = $Device
    producer = $Producer
}

function Save-Manifest {
    $Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $FollowupManifestPath -Encoding UTF8
}

Save-Manifest

try {
    while ($true) {
        if (Test-Path -LiteralPath $QueueManifestPath) {
            $Queue = Get-Content -Raw -LiteralPath $QueueManifestPath | ConvertFrom-Json
            if ($Queue.status -eq "failed") {
                throw "primary queue failed: $($Queue.error)"
            }
            if ($Queue.status -eq "completed") {
                break
            }
            $Manifest.primary_queue_step = $Queue.current_step
            $Manifest.last_poll_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            Save-Manifest
        }
        Start-Sleep -Seconds $PollSeconds
    }

    $Manifest.status = "discovering_affine2_checkpoint"
    $Manifest.primary_queue_completed_at_utc = $Queue.completed_at_utc
    Save-Manifest

    $Candidates = Get-ChildItem -LiteralPath $RunRoot -Directory |
        Where-Object { $_.Name -like "vda4_affine_ew_grid2x2_d128_nodecay_seed0_matched_production_*" } |
        Sort-Object LastWriteTimeUtc -Descending

    $Selected = $null
    foreach ($Candidate in $Candidates) {
        $LaunchManifestPath = Join-Path $Candidate.FullName "launch_manifest.json"
        $CheckpointPath = Join-Path $Candidate.FullName "rvit_paper_vda4_final.pt"
        if (-not (Test-Path -LiteralPath $LaunchManifestPath) -or -not (Test-Path -LiteralPath $CheckpointPath)) {
            continue
        }
        $Launch = Get-Content -Raw -LiteralPath $LaunchManifestPath | ConvertFrom-Json
        if ($Launch.status -eq "completed" -and [int]$Launch.registered_manipulation.iterations -eq 20000) {
            $Selected = [pscustomobject]@{
                Directory = $Candidate.FullName
                Checkpoint = $CheckpointPath
                LaunchManifest = $LaunchManifestPath
            }
            break
        }
    }

    if ($null -eq $Selected) {
        throw "no completed 20,000-iteration matched-production affine 2x2 checkpoint found under $RunRoot"
    }

    $Sha256 = (Get-FileHash -LiteralPath $Selected.Checkpoint -Algorithm SHA256).Hash.ToLowerInvariant()
    $Label = "vda4_affine_ew_grid2x2_seed0"
    $EvaluationRoot = Join-Path $OutputRoot $Label
    $Stdout = Join-Path $LogRoot ("{0}.stdout.log" -f $Label)
    $Stderr = Join-Path $LogRoot ("{0}.stderr.log" -f $Label)

    $Manifest.status = "evaluating_affine2"
    $Manifest.checkpoint_directory = $Selected.Directory
    $Manifest.checkpoint = $Selected.Checkpoint
    $Manifest.checkpoint_sha256 = $Sha256
    $Manifest.evaluation_output = $EvaluationRoot
    Save-Manifest

    $Arguments = @(
        "-u", $Producer,
        "--label", $Label,
        "--checkpoint", $Selected.Checkpoint,
        "--expected-sha256", $Sha256,
        "--output-root", $EvaluationRoot,
        "--device", $Device,
        "--psychometric-trials", "300",
        "--attention-trials", "128",
        "--intervention-trials", "250",
        "--threads", "3"
    )

    $PreviousPythonIoEncoding = $env:PYTHONIOENCODING
    $PreviousPythonUtf8 = $env:PYTHONUTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    try {
        $Process = Start-Process -FilePath $Python -ArgumentList $Arguments `
            -WorkingDirectory $ProjectRoot -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr
        if ($Process.ExitCode -ne 0) {
            throw "affine 2x2 evaluation exited with code $($Process.ExitCode); see $Stderr"
        }
    }
    finally {
        $env:PYTHONIOENCODING = $PreviousPythonIoEncoding
        $env:PYTHONUTF8 = $PreviousPythonUtf8
    }

    $Manifest.status = "completed"
    $Manifest.completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    Save-Manifest
}
catch {
    $Manifest.status = "failed"
    $Manifest.failed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    $Manifest.error = $_.Exception.Message
    Save-Manifest
    throw
}
