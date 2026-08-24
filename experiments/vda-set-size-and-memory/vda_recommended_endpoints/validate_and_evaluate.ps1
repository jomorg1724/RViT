[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("vda16", "vda_fixed9")]
    [string]$Task,

    [Parameter(Mandatory = $true)]
    [int]$Seed,

    [Parameter(Mandatory = $true)]
    [string]$RunDir,

    [Parameter(Mandatory = $true)]
    [string]$TrainingLog,

    [Parameter(Mandatory = $true)]
    [string]$Launcher,

    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[0-9a-fA-F]{64}$")]
    [string]$ExpectedCheckpointSha256,

    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [string]$Label = "",
    [string]$Python = "python",
    [ValidateSet("cpu", "cuda")]
    [string]$Device = "cuda",
    [int]$Threads = 3,
    [int]$PsychometricTrials = 300,
    [int]$AttentionTrials = 128,
    [int]$InterventionTrials = 250,
    [string]$Config = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ResolvedRunDir = (Resolve-Path $RunDir).Path
$ResolvedLog = (Resolve-Path $TrainingLog).Path
$ResolvedLauncher = (Resolve-Path $Launcher).Path
if (-not $Config) {
    $Config = Join-Path $ProjectRoot "config\default.json"
}
$ResolvedConfig = (Resolve-Path $Config).Path
$FinalCheckpoint = Join-Path $ResolvedRunDir ("rvit_paper_{0}_final.pt" -f $Task)
$TerminalManifest = "{0}.TERMINAL_VALIDATION.json" -f $OutputRoot
if (-not $Label) {
    $Label = "{0}_crossattn1_seed{1}" -f $Task, $Seed
}

& $Python (Join-Path $ProjectRoot "analysis\vda_terminal_run_validation.py") `
    --run-dir $ResolvedRunDir `
    --task $Task `
    --expected-seed $Seed `
    --project-root $ProjectRoot `
    --launcher $ResolvedLauncher `
    --config $ResolvedConfig `
    --log $ResolvedLog `
    --expected-final-sha256 $ExpectedCheckpointSha256 `
    --output $TerminalManifest
if ($LASTEXITCODE -ne 0) {
    throw "Terminal validation failed with exit code $LASTEXITCODE"
}

& $Python (Join-Path $ProjectRoot "analysis\vda_endpoint_evaluation.py") `
    --label $Label `
    --task $Task `
    --expected-seed $Seed `
    --checkpoint $FinalCheckpoint `
    --expected-sha256 $ExpectedCheckpointSha256 `
    --output-root $OutputRoot `
    --device $Device `
    --threads $Threads `
    --psychometric-trials $PsychometricTrials `
    --attention-trials $AttentionTrials `
    --intervention-trials $InterventionTrials
if ($LASTEXITCODE -ne 0) {
    throw "Held-out evaluation failed with exit code $LASTEXITCODE"
}

Write-Host ("COMPLETE|task={0}|seed={1}|terminal={2}|evaluation={3}" -f `
    $Task, $Seed, $TerminalManifest, $OutputRoot)
