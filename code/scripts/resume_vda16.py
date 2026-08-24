"""Safely resume the newest historical VDA16 checkpoint on an available GPU.

The historical rolling checkpoints contain model weights and a global iteration only.
They do not contain optimizer, target-network, JEPA-teacher, replay-buffer, environment,
or RNG state. This launcher therefore resumes the learned model at the next global
iteration, but records the unavoidable trainer-state discontinuity in a new run
directory rather than overwriting the historical artifacts.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import torch

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_WORKSPACE_ROOT = _PROJECT_ROOT.parent
_DEFAULT_CHECKPOINT_ROOT = _WORKSPACE_ROOT / "battery_sweep_results" / "pod2" / "ckpt2"
_DEFAULT_OUTPUT_ROOT = _WORKSPACE_ROOT / "battery_sweep_results" / "resumed"
_RUN_RE = re.compile(r"^vda16_(?P<feedback>affine_ew|crossattn1)_d(?P<d_mem>128|256)$")


@dataclasses.dataclass(frozen=True)
class ResumePlan:
    checkpoint: Path
    checkpoint_iteration: int
    start_iteration: int
    additional_iterations: int
    feedback: str
    d_mem: int
    device: str
    output_dir: Path
    command: tuple[str, ...]


def _load_checkpoint_metadata(path: Path) -> dict:
    blob = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(blob, dict) or "model_state_dict" not in blob:
        raise ValueError(f"not a trainer checkpoint with model_state_dict: {path}")
    iteration = blob.get("iter")
    if isinstance(iteration, bool) or not isinstance(iteration, int) or iteration < 0:
        raise ValueError(f"checkpoint has no valid non-negative integer iter: {path}")
    return blob


def find_latest_checkpoint(checkpoint_root: Path) -> Path:
    """Return the newest rolling VDA16 checkpoint by filesystem modification time."""
    checkpoint_root = Path(checkpoint_root).expanduser().resolve()
    candidates = [
        path
        for path in checkpoint_root.glob("vda16_*/rvit_plus_rl_latest.pt")
        if _RUN_RE.fullmatch(path.parent.name)
    ]
    if not candidates:
        raise FileNotFoundError(
            f"no VDA16 rolling checkpoints found under {checkpoint_root}; "
            "expected vda16_<feedback>_d<width>/rvit_plus_rl_latest.pt"
        )
    candidates.sort(key=lambda path: (path.stat().st_mtime_ns, str(path)), reverse=True)
    selected = candidates[0]
    _load_checkpoint_metadata(selected)
    return selected


def choose_gpu_device(requested: str = "auto") -> str:
    if requested != "auto":
        if requested == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available")
        if requested == "mps" and not torch.backends.mps.is_available():
            raise RuntimeError("MPS was requested but is not available")
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    raise RuntimeError("no GPU backend is available (checked CUDA and Apple MPS)")


def build_resume_plan(
    *,
    checkpoint: Path,
    trainer: Path,
    output_root: Path,
    device: str,
    target_iteration: int,
    run_stamp: str,
) -> ResumePlan:
    checkpoint = Path(checkpoint).expanduser().resolve()
    trainer = Path(trainer).expanduser().resolve()
    output_root = Path(output_root).expanduser().resolve()
    if not trainer.is_file():
        raise FileNotFoundError(f"training entry point not found: {trainer}")

    match = _RUN_RE.fullmatch(checkpoint.parent.name)
    if match is None:
        raise ValueError(f"cannot infer VDA16 architecture from directory name: {checkpoint.parent.name}")
    blob = _load_checkpoint_metadata(checkpoint)
    checkpoint_iteration = int(blob["iter"])
    start_iteration = checkpoint_iteration + 1
    additional_iterations = int(target_iteration) - start_iteration
    if additional_iterations <= 0:
        raise ValueError(
            f"checkpoint already reached target: next iteration is {start_iteration}, "
            f"target total iteration count is {target_iteration}"
        )

    feedback = match.group("feedback")
    d_mem = int(match.group("d_mem"))
    output_dir = output_root / (
        f"vda16_{feedback}_d{d_mem}_from_iter{start_iteration:04d}_{run_stamp}"
    )
    if output_dir == checkpoint.parent:
        raise ValueError("resume output directory must not overwrite the source run")

    command = (
        sys.executable,
        str(trainer),
        "--task", "vda16",
        "--T", "7",
        "--min-change-time", "5",
        "--max-change-time", "5",
        "--cell", "xlstm",
        "--feedback", feedback,
        "--conv-frontend",
        "--jepa-coef", "0.5",
        "--d-mem", str(d_mem),
        "--curriculum",
        "--seed", "0",
        "--init-mode", "warm_start",
        "--checkpoint-path", str(checkpoint),
        "--checkpoint-dir", str(output_dir),
        "--start-iteration", str(start_iteration),
        "--iters", str(additional_iterations),
        "--device", device,
    )
    return ResumePlan(
        checkpoint=checkpoint,
        checkpoint_iteration=checkpoint_iteration,
        start_iteration=start_iteration,
        additional_iterations=additional_iterations,
        feedback=feedback,
        d_mem=d_mem,
        device=device,
        output_dir=output_dir,
        command=command,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_manifest(plan: ResumePlan) -> Path:
    plan.output_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": 1,
        "task": "vda16",
        "parent_checkpoint": str(plan.checkpoint),
        "parent_checkpoint_sha256": _sha256(plan.checkpoint),
        "parent_checkpoint_iteration": plan.checkpoint_iteration,
        "start_iteration": plan.start_iteration,
        "target_total_iterations": plan.start_iteration + plan.additional_iterations,
        "additional_iterations": plan.additional_iterations,
        "feedback": plan.feedback,
        "d_mem": plan.d_mem,
        "device": plan.device,
        "command": list(plan.command),
        "resume_fidelity": "model_weights_and_global_iteration_only",
        "unavailable_parent_state": [
            "optimizer",
            "PAC_target_network",
            "JEPA_teacher",
            "replay_buffer",
            "environment_curriculum_window",
            "random_number_generators",
        ],
    }
    path = plan.output_dir / "resume_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-root", type=Path, default=_DEFAULT_CHECKPOINT_ROOT)
    parser.add_argument("--checkpoint", type=Path, default=None,
                        help="explicit checkpoint; default selects the newest VDA16 rolling checkpoint")
    parser.add_argument("--output-root", type=Path, default=_DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--target-iters", type=int, default=20_000,
                        help="target total iteration count, counting from historical iteration zero")
    parser.add_argument("--device", choices=("auto", "cuda", "mps"), default="auto")
    parser.add_argument("--launch", action="store_true",
                        help="start training; without this flag, print and validate the resume plan only")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    checkpoint = args.checkpoint or find_latest_checkpoint(args.checkpoint_root)
    device = choose_gpu_device(args.device)
    run_stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    plan = build_resume_plan(
        checkpoint=checkpoint,
        trainer=_PROJECT_ROOT / "train_rl.py",
        output_root=args.output_root,
        device=device,
        target_iteration=args.target_iters,
        run_stamp=run_stamp,
    )

    print(f"checkpoint: {plan.checkpoint}")
    print(f"checkpoint iteration: {plan.checkpoint_iteration}")
    print(f"resume iterations: {plan.start_iteration}..{plan.start_iteration + plan.additional_iterations - 1}")
    print(f"GPU backend: {plan.device}")
    print(f"new run directory: {plan.output_dir}")
    print("trainer-state caveat: historical checkpoint preserves model weights only")
    print("command:")
    print(subprocess.list2cmdline(plan.command))

    if not args.launch:
        print("dry run only; add --launch to start training")
        return 0

    manifest = _write_manifest(plan)
    print(f"wrote resume manifest: {manifest}")
    completed = subprocess.run(plan.command, cwd=_PROJECT_ROOT, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
