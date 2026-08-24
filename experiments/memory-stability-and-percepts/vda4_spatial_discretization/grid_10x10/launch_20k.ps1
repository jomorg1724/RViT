param(
    [ValidateRange(1, 20000)]
    [int]$Iterations = 20000,
    [ValidateRange(1, 64)]
    [int]$EpisodesPerIteration = 8,
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",
    [string]$RunTag = "production"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$Python = (Get-Command python -ErrorAction Stop).Source
$RunStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$RunId = [guid]::NewGuid().ToString("N").Substring(0, 12)
$RunRoot = Join-Path $env:USERPROFILE "Documents\RViT_runs"
$RunName = "vda4_affine_ew_grid10x10_d128_replay_excluded_seed0_{0}_{1}_{2}" -f $RunTag, $RunStamp, $RunId
$CheckpointDir = Join-Path $RunRoot $RunName

New-Item -ItemType Directory -Path $RunRoot -Force | Out-Null
New-Item -ItemType Directory -Path $CheckpointDir -ErrorAction Stop | Out-Null

$Arguments = @(
    "-u", (Join-Path $ProjectRoot "train_rl.py"),
    "--task", "vda4",
    "--T", "7",
    "--min-change-time", "5",
    "--max-change-time", "5",
    "--patch-grid-rows", "10",
    "--patch-grid-cols", "10",
    "--cell", "xlstm",
    "--feedback", "affine_ew",
    "--memory-decay", "1.0",
    "--conv-frontend",
    "--jepa-coef", "0.5",
    "--d-mem", "128",
    "--curriculum",
    "--init-mode", "fresh",
    "--checkpoint-dir", $CheckpointDir,
    "--experiment-launcher", $PSCommandPath,
    "--iters", [string]$Iterations,
    "--schedule-final-iteration", [string]($Iterations - 1),
    "--episodes-per-iter", [string]$EpisodesPerIteration,
    "--save-every", "50",
    "--log-every", "1",
    "--seed", "0",
    "--device", $Device
)

$LaunchManifest = [ordered]@{
    schema_version = 1
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    status = "launching"
    run_tag = $RunTag
    checkpoint_dir = $CheckpointDir
    python = $Python
    project_root = $ProjectRoot
    command = @($Python) + $Arguments
    registered_manipulation = [ordered]@{
        task = "vda4"
        task_grid = @(2, 2)
        sensory_patch_grid = @(10, 10)
        visual_tokens = 100
        feedback = "affine_ew"
        d_mem = 128
        memory_decay = 1.0
        seed = 0
        iterations = $Iterations
        episodes_per_iteration = $EpisodesPerIteration
        device = $Device
    }
}
$ManifestPath = Join-Path $CheckpointDir "launch_manifest.json"
$LaunchManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

Write-Host "VDA4 affine 10x10 sensory-grid run"
Write-Host "Output: $CheckpointDir"
Write-Host "Iterations: 0..$($Iterations - 1)"

Push-Location $ProjectRoot
try {
    $PreviousPythonIoEncoding = $env:PYTHONIOENCODING
    $PreviousPythonUtf8 = $env:PYTHONUTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $StdoutPath = Join-Path $CheckpointDir "train.stdout.log"
    $StderrPath = Join-Path $CheckpointDir "train.stderr.log"
    $Process = Start-Process -FilePath $Python -ArgumentList $Arguments `
        -WorkingDirectory $ProjectRoot -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
    if ($Process.ExitCode -ne 0) {
        throw "trainer exited with code $($Process.ExitCode); see $StderrPath"
    }
    $LaunchManifest.status = "completed"
    $LaunchManifest.completed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    $LaunchManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
}
catch {
    $LaunchManifest.status = "failed"
    $LaunchManifest.failed_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    $LaunchManifest.error = $_.Exception.Message
    $LaunchManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
    throw
}
finally {
    $env:PYTHONIOENCODING = $PreviousPythonIoEncoding
    $env:PYTHONUTF8 = $PreviousPythonUtf8
    Pop-Location
}
