param(
    [string]$QueueTag = "production_20260727",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Python = (Get-Command python -ErrorAction Stop).Source
$Producer = Join-Path $ProjectRoot "analysis\vda4_spatial_scaling_evaluation.py"
$OutputRoot = Join-Path $ProjectRoot ("reports\vda_series\spatial_scaling_evaluation_{0}" -f $QueueTag)
$LogRoot = Join-Path $OutputRoot "queue_logs"
New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

$Jobs = @(
    [ordered]@{
        label = "vda4_affine_ew_grid10x10_seed0"
        checkpoint = "C:\Users\jomor\Documents\RViT_runs\vda4_affine_ew_grid10x10_d128_replay_excluded_seed0_production_20260726T165822Z_b863849f2288\rvit_paper_vda4_final.pt"
        sha256 = "0f0cfc5d0087a34de247dc02f7c343d8eae80eadb74478c564a6ea72c7244cb5"
    },
    [ordered]@{
        label = "vda4_crossattn1_grid10x10_seed0"
        checkpoint = "C:\Users\jomor\Documents\RViT_runs\vda4_crossattn1_grid10x10_d128_nodecay_seed0_pod\rvit_paper_vda4_final.pt"
        sha256 = "06382037f3693c454d494df220e931717bf7f09658b5fcc3c110b6114ebf5bdc"
    },
    [ordered]@{
        label = "vda4_crossattn1_grid2x2_seed0"
        checkpoint = "C:\Users\jomor\Documents\RViT_runs\vda4_crossattn1_d128_nodecay_seed0_pod\rvit_paper_vda4_final.pt"
        sha256 = "ea671f9758551e06b39ef19c06e85e888ce3ee74dda8a534c1532251a69ee4ca"
    },
    [ordered]@{
        label = "vda4_crossattn1_grid4x4_seed0"
        checkpoint = "C:\Users\jomor\Documents\RViT_runs\vda4_grid4x4_crossattn1_d128_nodecay_seed0_pod\rvit_paper_vda4_final.pt"
        sha256 = "306ce94d44461ea85cd0aced5a84eb210457f718d3f2e4ebf85e46ee1922e4bf"
    }
)

$ManifestPath = Join-Path $OutputRoot "QUEUE_MANIFEST.json"
$Manifest = [ordered]@{
    schema_version = 1
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    status = "running"
    current_step = "initializing"
    device = $Device
    python = $Python
    producer = $Producer
    jobs = $Jobs
    completed_evaluations = @()
    final_training_launcher = (Join-Path $PSScriptRoot "grid_2x2\launch_affine_ew_local.ps1")
}
$Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8

function Save-Manifest {
    $Manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
}

function Invoke-Evaluation([System.Collections.IDictionary]$Job) {
    $Label = [string]$Job.label
    $Output = Join-Path $OutputRoot $Label
    $Stdout = Join-Path $LogRoot ("{0}.stdout.log" -f $Label)
    $Stderr = Join-Path $LogRoot ("{0}.stderr.log" -f $Label)
    $Arguments = @(
        "-u", $Producer,
        "--label", $Label,
        "--checkpoint", [string]$Job.checkpoint,
        "--expected-sha256", [string]$Job.sha256,
        "--output-root", $Output,
        "--device", $Device,
        "--psychometric-trials", "300",
        "--attention-trials", "128",
        "--intervention-trials", "250",
        "--threads", "3"
    )
    $Manifest.current_step = "evaluate:$Label"
    Save-Manifest
    $Process = Start-Process -FilePath $Python -ArgumentList $Arguments `
        -WorkingDirectory $ProjectRoot -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr
    if ($Process.ExitCode -ne 0) {
        throw "evaluation $Label exited with code $($Process.ExitCode); see $Stderr"
    }
    $Manifest.completed_evaluations += $Label
    Save-Manifest
}

try {
    $PreviousPythonIoEncoding = $env:PYTHONIOENCODING
    $PreviousPythonUtf8 = $env:PYTHONUTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    foreach ($Job in $Jobs) {
        Invoke-Evaluation $Job
    }

    $Manifest.current_step = "train:vda4_affine_ew_grid2x2_seed0"
    Save-Manifest
    & (Join-Path $PSScriptRoot "grid_2x2\launch_affine_ew_local.ps1") `
        -Iterations 20000 -EpisodesPerIteration 8 -Device $Device -RunTag "matched_production"

    $Manifest.status = "completed"
    $Manifest.current_step = "complete"
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
finally {
    $env:PYTHONIOENCODING = $PreviousPythonIoEncoding
    $env:PYTHONUTF8 = $PreviousPythonUtf8
}
