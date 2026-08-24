param(
    [string]$QueueTag = "production_20260727",
    [ValidateSet("cuda", "cpu")]
    [string]$Device = "cuda",
    [ValidateRange(15, 300)]
    [int]$PollSeconds = 60,
    [string]$SshHostName = "193.183.22.54",
    [int]$SshPort = 1332,
    [string]$SshKey = "$HOME\.ssh\id_ed25519"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Python = (Get-Command python -ErrorAction Stop).Source
$Ssh = (Get-Command ssh -ErrorAction Stop).Source
$Scp = (Get-Command scp -ErrorAction Stop).Source
$Producer = Join-Path $ProjectRoot "analysis\vda4_spatial_scaling_evaluation.py"
$OutputRoot = Join-Path $ProjectRoot ("reports\vda_series\spatial_scaling_evaluation_{0}" -f $QueueTag)
$LogRoot = Join-Path $OutputRoot "queue_logs"
$Affine2FollowupManifestPath = Join-Path $OutputRoot "AFFINE2_FOLLOWUP_MANIFEST.json"
$WatcherManifestPath = Join-Path $OutputRoot "AFFINE4_RUNPOD_FOLLOWUP_MANIFEST.json"
$RemoteDirectory = "/workspace/vda4_affine_ew_grid4x4_d128_nodecay_seed0_production_20260726T231002Z_d5a8b2451bee"
$RemoteLog = "/workspace/vda4_affine_ew_grid4x4_production_20260726T231002Z.log"
$LocalFinal = Join-Path $env:USERPROFILE "Documents\RViT_runs\vda4_affine_ew_grid4x4_d128_nodecay_seed0_pod"
New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null

if (-not (Test-Path -LiteralPath $SshKey)) {
    throw "SSH key does not exist: $SshKey"
}

$Manifest = [ordered]@{
    schema_version = 1
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    status = "waiting_for_runpod_completion"
    pod_id = "onrylro4hhaaly"
    ssh_endpoint = ("{0}:{1}" -f $SshHostName, $SshPort)
    remote_directory = $RemoteDirectory
    remote_log = $RemoteLog
    local_destination = $LocalFinal
    device = $Device
    producer = $Producer
    pod_lifecycle_note = "This watcher never stops or terminates the pod; lifecycle control remains an independently verified action."
}

function Save-Manifest {
    $Manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $WatcherManifestPath -Encoding UTF8
}

Save-Manifest

$RemoteAuditCode = @'
import csv, pathlib, subprocess, sys, torch
D=pathlib.Path('/workspace/vda4_affine_ew_grid4x4_d128_nodecay_seed0_production_20260726T231002Z_d5a8b2451bee')
LOG=pathlib.Path('/workspace/vda4_affine_ew_grid4x4_production_20260726T231002Z.log')
p=subprocess.run(['pgrep','-af','train_rl.py'],capture_output=True,text=True)
active=[s for s in p.stdout.splitlines() if str(D) in s]
if active:
    print('NOT_READY|trainer_active')
    sys.exit(3)
final=D/'rvit_paper_vda4_final.pt'
latest=D/'rvit_plus_rl_latest.pt'
metrics=D/'metrics.csv'
for pth in (final,latest,metrics,LOG):
    if not pth.is_file():
        print('NOT_READY|missing|'+str(pth))
        sys.exit(3)
with metrics.open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
iters=[int(r['iter']) for r in rows]
if iters != list(range(20000)):
    print(f'NOT_READY|metrics|n={len(iters)}|first={iters[:1]}|last={iters[-1:]}')
    sys.exit(3)
x=torch.load(final,map_location='cpu',weights_only=False)
mk=x['model_kwargs']
ta=x['training_args']
checks=[
    x['checkpoint_schema_version']==3,
    x['iter']==19999,
    x['task']=='vda4',
    mk['grid_rows']==4,
    mk['grid_cols']==4,
    mk['feedback']=='affine_ew',
    mk['d_mem']==128,
    mk['memory_decay']==1.0,
    x['initialization_contract']=={'mode':'fresh'},
    ta['seed']==0,
    x['resume_fidelity']=='replay_excluded_trainer_state',
]
if not all(checks):
    print('NOT_READY|checkpoint_contract')
    sys.exit(3)
log=LOG.read_text(encoding='utf-8',errors='replace')
if 'Traceback' in log or 'iters logged=20000' not in log or 'saved replay-excluded trainer state' not in log:
    print('NOT_READY|log_gate')
    sys.exit(3)
print('READY|iter=19999|rows=20000|schema=3|fresh_seed0')
'@
$RemoteAuditBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($RemoteAuditCode))

try {
    while ($true) {
        $AuditOutput = & $Ssh -i $SshKey -o BatchMode=yes -o StrictHostKeyChecking=accept-new `
            -o ConnectTimeout=15 -p $SshPort "root@$SshHostName" `
            "echo $RemoteAuditBase64 | base64 -d | /workspace/rvit_venv/bin/python -" 2>&1
        $AuditExitCode = $LASTEXITCODE
        $AuditText = ($AuditOutput | Out-String).Trim()
        $Manifest.last_poll_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        $Manifest.last_remote_audit = $AuditText
        $Manifest.last_remote_audit_exit_code = $AuditExitCode
        Save-Manifest

        if ($AuditExitCode -eq 0 -and $AuditText -match "(?m)^READY\|") {
            break
        }
        Start-Sleep -Seconds $PollSeconds
    }

    $Manifest.status = "remote_ready_staging_pull"
    $Manifest.remote_ready_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    Save-Manifest

    if (Test-Path -LiteralPath $LocalFinal) {
        throw "destination already exists; refusing to overwrite: $LocalFinal"
    }

    $Stage = "$LocalFinal.pull-$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')).partial"
    New-Item -ItemType Directory -Path $Stage -ErrorAction Stop | Out-Null
    $Files = @(
        [pscustomobject]@{ Remote = "$RemoteDirectory/metrics.csv"; Local = "metrics.csv" },
        [pscustomobject]@{ Remote = "$RemoteDirectory/rvit_paper_vda4_final.pt"; Local = "rvit_paper_vda4_final.pt" },
        [pscustomobject]@{ Remote = "$RemoteDirectory/rvit_plus_rl_latest.pt"; Local = "rvit_plus_rl_latest.pt" },
        [pscustomobject]@{ Remote = $RemoteLog; Local = "train.log" }
    )
    $Verified = @()
    foreach ($File in $Files) {
        $HashOutput = & $Ssh -i $SshKey -o BatchMode=yes -o ConnectTimeout=15 `
            -p $SshPort "root@$SshHostName" "sha256sum '$($File.Remote)'" 2>&1
        $HashExitCode = $LASTEXITCODE
        $HashText = ($HashOutput | Out-String).Trim()
        if ($HashExitCode -ne 0 -or $HashText -notmatch "^([0-9a-f]{64})") {
            throw "remote hash failed for $($File.Remote): $HashText"
        }
        $RemoteHash = $Matches[1]
        $Source = "root@${SshHostName}:$($File.Remote)"
        $Destination = Join-Path $Stage $File.Local
        & $Scp -i $SshKey -o BatchMode=yes -o ConnectTimeout=15 -P $SshPort $Source $Destination
        if ($LASTEXITCODE -ne 0) {
            throw "SCP failed for $($File.Remote)"
        }
        $LocalHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Destination).Hash.ToLowerInvariant()
        if ($LocalHash -ne $RemoteHash) {
            throw "SHA-256 mismatch for $($File.Local): local=$LocalHash remote=$RemoteHash"
        }
        $Verified += [pscustomobject]@{
            file = $File.Local
            remote_path = $File.Remote
            sha256 = $LocalHash
            bytes = (Get-Item -LiteralPath $Destination).Length
        }
    }

    $LocalValidationCode = @'
import csv, pathlib, sys
import numpy as np
sys.modules.setdefault('numpy._core', np.core)
sys.modules.setdefault('numpy._core.multiarray', np.core.multiarray)
import torch
d=pathlib.Path(sys.argv[1])
with (d/'metrics.csv').open(newline='',encoding='utf-8') as f:
    rows=list(csv.DictReader(f))
iters=[int(r['iter']) for r in rows]
assert iters == list(range(20000)), (len(iters), iters[:1], iters[-1:])
x=torch.load(d/'rvit_paper_vda4_final.pt', map_location='cpu')
mk=x['model_kwargs']
ta=x['training_args']
assert x['checkpoint_schema_version']==3
assert x['iter']==19999 and x['task']=='vda4'
assert mk['grid_rows']==4 and mk['grid_cols']==4
assert mk['feedback']=='affine_ew' and mk['d_mem']==128 and mk['memory_decay']==1.0
assert x['initialization_contract']=={'mode':'fresh'} and ta['seed']==0
assert x['resume_fidelity']=='replay_excluded_trainer_state'
log=(d/'train.log').read_text(encoding='utf-8',errors='replace')
assert 'Traceback' not in log and 'iters logged=20000' in log
print('LOCAL_VALID|iter=19999|rows=20000|schema=3|fresh_seed0')
'@
    $LocalValidation = & $Python -c $LocalValidationCode $Stage 2>&1
    $LocalValidationExitCode = $LASTEXITCODE
    $LocalValidationText = ($LocalValidation | Out-String).Trim()
    if ($LocalValidationExitCode -ne 0 -or $LocalValidationText -notmatch "(?m)^LOCAL_VALID\|") {
        throw "local checkpoint contract validation failed: $LocalValidationText"
    }

    $PullManifest = [ordered]@{
        schema_version = 1
        pulled_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        pod_id = $Manifest.pod_id
        remote_ready_audit = $AuditText
        local_contract_audit = $LocalValidationText
        verified_files = $Verified
    }
    $PullManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $Stage "pull_manifest.json") -Encoding UTF8
    Move-Item -LiteralPath $Stage -Destination $LocalFinal -ErrorAction Stop

    $FinalCheckpoint = Join-Path $LocalFinal "rvit_paper_vda4_final.pt"
    $FinalSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $FinalCheckpoint).Hash.ToLowerInvariant()
    $Manifest.status = "pulled_and_verified_waiting_for_local_gpu"
    $Manifest.local_checkpoint = $FinalCheckpoint
    $Manifest.local_checkpoint_sha256 = $FinalSha256
    $Manifest.verified_files = $Verified
    $Manifest.pulled_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    Save-Manifest

    while ($true) {
        if (Test-Path -LiteralPath $Affine2FollowupManifestPath) {
            $Affine2Followup = Get-Content -Raw -LiteralPath $Affine2FollowupManifestPath | ConvertFrom-Json
            if ($Affine2Followup.status -eq "failed") {
                throw "affine 2x2 follow-up failed: $($Affine2Followup.error)"
            }
            if ($Affine2Followup.status -eq "completed") {
                break
            }
            $Manifest.affine2_followup_status = $Affine2Followup.status
            $Manifest.last_local_gpu_poll_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            Save-Manifest
        }
        Start-Sleep -Seconds $PollSeconds
    }

    $Label = "vda4_affine_ew_grid4x4_seed0"
    $EvaluationRoot = Join-Path $OutputRoot $Label
    $Stdout = Join-Path $LogRoot ("{0}.stdout.log" -f $Label)
    $Stderr = Join-Path $LogRoot ("{0}.stderr.log" -f $Label)
    $Arguments = @(
        "-u", $Producer,
        "--label", $Label,
        "--checkpoint", $FinalCheckpoint,
        "--expected-sha256", $FinalSha256,
        "--output-root", $EvaluationRoot,
        "--device", $Device,
        "--psychometric-trials", "300",
        "--attention-trials", "128",
        "--intervention-trials", "250",
        "--threads", "3"
    )

    $Manifest.status = "evaluating_affine4"
    $Manifest.evaluation_output = $EvaluationRoot
    Save-Manifest
    $PreviousPythonIoEncoding = $env:PYTHONIOENCODING
    $PreviousPythonUtf8 = $env:PYTHONUTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    try {
        $Process = Start-Process -FilePath $Python -ArgumentList $Arguments `
            -WorkingDirectory $ProjectRoot -NoNewWindow -Wait -PassThru `
            -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr
        if ($Process.ExitCode -ne 0) {
            throw "affine 4x4 evaluation exited with code $($Process.ExitCode); see $Stderr"
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
