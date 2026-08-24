"""
Train the EXACT paper Recurrent ViT (Morgan/Albanna/Herman) with our PAC + QR-DQN +
PER harness and EMA targets, on the paper's cued orientation-change-detection task.

    python RViT_plus_paper_softmaxhead/train_rl.py --device mps          # 150k episodes (18,750 iters × 8)

The network is the paper's (VAE front-end → multiplicative ViT → spatial xLSTM →
flattened-H readout); the only departures from the paper, all locked with the user:
QR-DQN critic (our harness) with 5 particles, EMA target (instead of hard-copy), γ=0.95,
VAE trained end-to-end (no pretrain). If this does not reproduce the paper's cueing
behaviour, the problem is not the architecture.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import io
import os
import platform
import random
import sys
from datetime import datetime, timezone

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from config.loader import load_config, cfg_get, load_checkpoint_weights  # noqa: E402
from envs import make_env, task_grid, TASKS                              # noqa: E402
from model import RViTPaperModel                                         # noqa: E402
from ppo import PPOConfig, train                                         # noqa: E402


def pick_device(name: str) -> torch.device:
    if name in ("mps", "cuda", "cpu"):
        return torch.device(name)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def seed_training_rngs(seed: int) -> None:
    """Seed model and environment RNGs before environment construction."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)


def resolve_patch_grid(task: str, patch_grid_rows: int | None,
                       patch_grid_cols: int | None) -> tuple[int, int]:
    """Resolve sensory-token geometry independently from task/stimulus geometry."""
    if (patch_grid_rows is None) != (patch_grid_cols is None):
        raise ValueError("--patch-grid-rows and --patch-grid-cols must be provided together")
    if patch_grid_rows is None:
        return tuple(task_grid(task))
    if patch_grid_rows <= 0 or patch_grid_cols <= 0:
        raise ValueError("patch-grid dimensions must be positive")
    return int(patch_grid_rows), int(patch_grid_cols)


def resolve_schedule_overrun_compatibility(
    *,
    init_mode: str,
    phase_final_iteration: int,
    schedule_final_iteration: int,
    explicitly_allowed: bool,
) -> set[str]:
    """Return the bounded producer transition needed to continue past a saved schedule."""
    if schedule_final_iteration >= phase_final_iteration:
        return set()
    if not explicitly_allowed:
        raise ValueError(
            f"schedule final iteration {schedule_final_iteration} precedes phase end "
            f"{phase_final_iteration}; pass --allow-schedule-overrun-resume to preserve the "
            "saved schedule and clamp completed schedules at their endpoint"
        )
    if init_mode != "resume":
        raise ValueError("--allow-schedule-overrun-resume requires --init-mode resume")
    return {"train_rl.py", "ppo.py"}


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_warm_start_parent(model, checkpoint_path: str, *, expected_sha256: str, device):
    """Strictly load and cryptographically bind a weights-only initialization parent."""
    resolved_path = os.path.abspath(checkpoint_path)
    actual_sha256 = _sha256(resolved_path)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            f"warm-start parent hash mismatch: expected {expected_sha256}, got {actual_sha256}"
        )
    info = load_checkpoint_weights(model, resolved_path, strict=True, device=device)
    checkpoint = torch.load(resolved_path, map_location="cpu", weights_only=False)
    contract = {
        "mode": "warm_start",
        "checkpoint_path": resolved_path,
        "checkpoint_sha256": actual_sha256,
        "checkpoint_iteration": checkpoint.get("iter"),
        "checkpoint_task": checkpoint.get("task"),
        "strict": True,
    }
    return info, contract


def resume_initialization_contract(
    checkpoint: dict,
    *,
    expected_parent_sha256: str | None,
    resume_checkpoint_path: str,
    resume_checkpoint_sha256: str,
) -> dict:
    """Preserve the original initialization root across a child resume chain."""
    contract = dict(checkpoint.get("initialization_contract", {
        "mode": "legacy_resume_root",
        "checkpoint_path": os.path.abspath(resume_checkpoint_path),
        "checkpoint_sha256": resume_checkpoint_sha256,
    }))
    if expected_parent_sha256 is not None and (
        contract.get("mode") != "warm_start"
        or contract.get("strict") is not True
        or contract.get("checkpoint_sha256") != expected_parent_sha256
    ):
        raise ValueError(
            "resumed child initialization parent hash mismatch: "
            f"expected strict warm start {expected_parent_sha256}, got {contract}"
        )
    return contract


def _producer_hashes(config_path: str | None = None,
                     experiment_launcher: str | None = None) -> dict[str, str]:
    relative_paths = (
        "train_rl.py",
        "ppo.py",
        "model.py",
        "paper_encoder.py",
        "paper_heads.py",
        "conv_frontend.py",
        "envs/base.py",
        "envs/luo2015.py",
        "envs/tasks.py",
        "envs/__init__.py",
        "config/loader.py",
        "scripts/launch_vda16_fresh.sh",
        "experiments/vda4_spatial_discretization/grid_10x10/launch_20k.sh",
    )
    hashes = {
        relative_path: _sha256(os.path.join(_HERE, relative_path))
        for relative_path in relative_paths
    }
    if config_path and os.path.isfile(config_path):
        hashes["resolved_config"] = _sha256(os.path.abspath(config_path))
    if experiment_launcher:
        launcher_path = os.path.abspath(experiment_launcher)
        if not os.path.isfile(launcher_path):
            raise FileNotFoundError(f"--experiment-launcher {launcher_path} not found")
        hashes["experiment_launcher"] = _sha256(launcher_path)
    return hashes


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train the exact paper Recurrent ViT")
    p.add_argument("--task", default="vda4", choices=sorted(TASKS),
                   help="default vda4 = value+validity (coloured value cue red/green/blue → reward).")
    p.add_argument("--curriculum", action="store_true",
                   help="enable the paper's shrinking-θ difficulty curriculum (OFF by default → FIXED "
                        "difficulty). Paper: Δ~U(-θ,θ), θ starts 65; when success ≥85%% over 1000 trials, "
                        "drop θ by 3°, floored at --curr-floor.")
    p.add_argument("--theta-start", type=float, default=65.0, help="curriculum: starting max |Δ| (paper k=65)")
    p.add_argument("--curr-window", type=int, default=1000, help="curriculum: trials per evaluation window (paper 1000)")
    p.add_argument("--curr-threshold", type=float, default=0.85, help="curriculum: success rate to drop θ (paper 0.85)")
    p.add_argument("--curr-step", type=float, default=3.0, help="curriculum: degrees to drop max |Δ| per cleared window (paper 3)")
    p.add_argument("--curr-floor", type=float, default=8.0, help="curriculum: θ never drops below this many degrees")
    p.add_argument("--T", type=int, default=7, help="number of LOGICAL frames (physical T = T × frame-repeat).")
    p.add_argument("--frame-repeat", type=int, default=1,
                   help="hold each logical frame for this many physical steps (frozen pixels). 5 = held-frame task.")
    p.add_argument("--d-mem", type=int, default=1024,
                   help="recurrent memory embedding size per patch (default 1024; try 512/256/128).")
    p.add_argument("--memory-decay", type=float, default=1.0,
                   help="xLSTM carried-cell retention multiplier in [0,1]: "
                        "C_t=decay*(F_t*C_{t-1})+I_t*U_t (default 1.0, no added leak).")
    p.add_argument("--conv-frontend", action="store_true",
                   help="replace the VAE-shaped encoder with a capable small SE-ResNet conv front-end "
                        "(3ch colour, trained end-to-end); per-patch 25×25 → 128-d. No VAE checkpoint.")
    p.add_argument("--patch-grid-rows", type=int, default=None,
                   help="sensory patch rows; defaults to the task stimulus grid")
    p.add_argument("--patch-grid-cols", type=int, default=None,
                   help="sensory patch columns; defaults to the task stimulus grid")
    p.add_argument("--min-change-time", type=int, default=5)
    p.add_argument("--max-change-time", type=int, default=5)
    p.add_argument("--noise", type=float, default=5.0)
    # Luo & Maunsell reward structure (only used by the luo2015_* envs; ignored elsewhere).
    p.add_argument("--r-hit", type=float, default=None,
                   help="Luo criterion override: hit reward at --high-loc; the opposite location "
                        "receives the counterphased pair. Must be used with --r-cr.")
    p.add_argument("--r-cr", type=float, default=None,
                   help="Luo criterion override: correct-rejection reward at --high-loc.")
    p.add_argument("--high-reward", type=float, default=None,
                   help="Luo sensitivity session: mean correct-response reward at high-value location (default 5).")
    p.add_argument("--low-reward", type=float, default=None,
                   help="Luo sensitivity session: mean correct-response reward at low-value location (default 1).")
    p.add_argument("--high-loc", type=int, default=None,
                   help="Luo condition location: sensitivity high-value or criterion low-c location (0 or 3; default 0).")
    p.add_argument("--reward-scale", type=float, default=None,
                   help="multiply the correct-response reward magnitude (default 1.0)")
    p.add_argument("--qr-kappa", type=float, default=None,
                   help="quantile-Huber threshold (critic particles); scale WITH the reward magnitude "
                        "so the critic gradient isn't clipped in return-units (default from config, 1.0)")
    p.add_argument("--mpo-temperature", type=float, default=None,
                   help="MPO E-step temperature η (default from config, 0.1)")
    p.add_argument("--config", default=os.path.join(_HERE, "config", "default.json"))
    p.add_argument("--experiment-launcher", default=None,
                   help="optional launcher path to bind into checkpoint source provenance")
    p.add_argument("--init-mode", choices=["fresh", "warm_start", "resume"], default=None)
    p.add_argument("--checkpoint-path", default=None)
    p.add_argument("--expected-parent-sha256", default=None,
                   help="bind a strict warm start, or its resumed descendant, to this parent hash")
    p.add_argument("--checkpoint-dir", default=None)
    p.add_argument("--iters", type=int, default=None)
    p.add_argument("--schedule-final-iteration", type=int, default=None,
                   help="absolute final global iteration used by schedules such as PER beta")
    p.add_argument("--allow-schedule-overrun-resume", action="store_true",
                   help="explicitly continue a stateful resume beyond its saved schedule endpoint; "
                        "iteration-dependent schedules remain clamped at that saved endpoint")
    p.add_argument("--start-iteration", type=int, default=None,
                   help="global iteration number for this phase; resume defaults to checkpoint iter + 1")
    p.add_argument("--episodes-per-iter", type=int, default=None)
    p.add_argument("--n-quantiles", type=int, default=None, help="critic particles (default 5)")
    p.add_argument("--n-actions", type=int, default=2)
    p.add_argument("--two-lstm", action="store_true",
                   help="stack a 2nd xLSTM: LSTM1's H1 feeds the attention, LSTM2(H1)=H2 feeds the heads")
    p.add_argument("--feedback", default="film",
                   choices=["multiplicative", "film", "hyper", "hyper_codebook", "affine", "affine_ew", "dualhead", "crossattn", "crossattn1", "dualmem", "affine_cascade"],
                   # NOTE: default is FILM (not the paper's pure multiplicative) for --cell softmax_head:
                   # a softmax memory has ~1/head_dim values, so pure Q=(XW)⊙(CW) collapses the ViT's
                   # input/feedback gradients by ~6 orders vs FiLM (Z→X, the ViT does nothing). FiLM's
                   # (1+CW) keeps the sensory ViT alive; the memory→attention path is zero-init (learned).
                   help="how memory feedback enters Q/K/V: multiplicative (paper, Q=(XW)⊙(HW)) | "
                        "film (Q=(XW)⊙(1+HW), identity-init) | hyper (H GENERATES the Q/K/V "
                        "weights: W_P=reshape(G_P(bottleneck(H))), P=X·W_P — fast weights) | "
                        "hyper_codebook (hyper Q/K + V=codebook (H_CB), v12 downstream) | "
                        "affine (H derives scale-MATRIX Γ + shift β: X'=Γ(H)·X+β(H), then SA) | "
                        "affine_cascade (TWO affine transformers + TWO xLSTMs: T1(X,fb=H1)→Z1→H1, "
                        "T2(Z1,fb=H2)→Z2→H2; split readout actor←H2, critic←H1).")
    p.add_argument("--cell", default="softmax_head", choices=["xlstm", "softmax_head"],
                   help="recurrent cell: xlstm (paper (H,C,N,M)) | softmax_head (C-only, mem_heads "
                        "heads per patch, each softmax-normalised — a categorical memory).")
    p.add_argument("--mem-heads", type=int, default=4,
                   help="number of softmax heads per patch for --cell softmax_head (4 ⇒ 4×4 distributions).")
    p.add_argument("--init-action-bias", type=float, nargs=2, default=[0.0, -1.5])
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--gamma", type=float, default=None)
    p.add_argument("--entropy-coef", type=float, default=None)
    p.add_argument("--ema-decay", type=float, default=None, help="EMA target decay (default from config)")
    p.add_argument("--buffer-capacity", type=int, default=None)
    p.add_argument("--vae-checkpoint", default=None,
                   help="pretrained PatchVAE checkpoint; loads conv1/conv2/fc1 into the front-end")
    p.add_argument("--jepa-coef", type=float, default=0.0,
                   help="weight on the DINO/V-JEPA temporal self-distillation on the cell output (>0 enables).")
    p.add_argument("--jepa-heads", type=int, default=4,
                   help="structured softmax heads PER TOKEN (each head's embedding is softmaxed independently).")
    p.add_argument("--jepa-proto-dim", type=int, default=256,
                   help="softmax dim per head (prototypes within each embedding).")
    p.add_argument("--jepa-same-time", action="store_true",
                   help="ablation: same-time distillation instead of temporal t→t+1 (collapse-prone, OFF).")
    p.add_argument("--jepa-tau-student", type=float, default=0.1)
    p.add_argument("--jepa-tau-teacher-start", type=float, default=0.04)
    p.add_argument("--jepa-tau-teacher-end", type=float, default=0.07)
    p.add_argument("--jepa-tau-warmup", type=int, default=300)
    p.add_argument("--jepa-center-momentum", type=float, default=0.9)
    p.add_argument("--jepa-ema-decay", type=float, default=0.996)
    p.add_argument("--vae-color", action="store_true",
                   help="COLOUR (3ch) front-end so the value cue is visible; pair with the COLOUR VAE "
                        "(~/rvit_plus_checkpoints/paper_vae_color/vae_color.pt). A grayscale↔colour "
                        "mismatch is REFUSED at load.")
    p.add_argument("--no-freeze-vae", action="store_true",
                   help="fine-tune the pretrained VAE front-end instead of freezing it")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="")
    p.add_argument("--save-every", type=int, default=200)
    p.add_argument("--log-every", type=int, default=5)
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    cfg = load_config(args.config) if os.path.exists(args.config) else {}

    seed_training_rngs(args.seed)
    device = pick_device(args.device or cfg_get(cfg, "run.device", ""))

    # Pass Luo reward kwargs through ONLY when explicitly set, so non-Luo envs (which do not
    # accept them) are unaffected.
    _luo_kw = {k: v for k, v in (("r_hit", args.r_hit), ("r_cr", args.r_cr),
                                 ("high_reward", args.high_reward), ("low_reward", args.low_reward),
                                 ("high_loc", args.high_loc)) if v is not None}
    env = make_env(args.task, T=args.T, frame_repeat=args.frame_repeat, min_change_time=args.min_change_time,
                   max_change_time=args.max_change_time, noise_multiplier=args.noise,
                   reward_scale=(1.0 if args.reward_scale is None else args.reward_scale),
                   curriculum=args.curriculum, theta=args.theta_start, curr_window=args.curr_window,
                   curr_threshold=args.curr_threshold, curr_step=args.curr_step, theta_floor=args.curr_floor,
                   **_luo_kw)
    if _luo_kw:
        _tag = ""
        if args.r_hit is not None and args.r_cr is not None:
            _tag = ("  (LIBERAL criterion)" if args.r_hit > args.r_cr else
                    "  (CONSERVATIVE criterion)" if args.r_cr > args.r_hit else "  (neutral)")
        print(f"[luo] reward kwargs: {_luo_kw}{_tag}")
    if args.curriculum:
        print(f"[paper] CURRICULUM ON: Δ~U(-θ,θ), θ start={args.theta_start:.0f}°; drop {args.curr_step:.0f}° "
              f"when success≥{args.curr_threshold:.0%} over {args.curr_window} trials; floor={args.curr_floor:.0f}°. "
              f"θ is logged to metrics.csv each iteration.")
    seq_len = int(env.T)
    grid_rows, grid_cols = resolve_patch_grid(
        args.task, args.patch_grid_rows, args.patch_grid_cols
    )
    image_size = int(env.S)                            # 50 (2x2) or 75 (3x3/vda9)
    if (grid_rows, grid_cols) != tuple(task_grid(args.task)):
        print(f"[paper] sensory discretization override: task stimulus grid="
              f"{env.grid_rows}x{env.grid_cols}; patch/memory grid={grid_rows}x{grid_cols} "
              f"({grid_rows * grid_cols} tokens) over the unchanged {image_size}x{image_size} image")

    n_quantiles = args.n_quantiles if args.n_quantiles is not None \
        else int(cfg_get(cfg, "model.rl.n_quantiles", 5))
    model_kwargs = dict(
        n_actions=args.n_actions, n_quantiles=n_quantiles,
        init_action_bias=list(args.init_action_bias), seq_len=seq_len,
        feedback=args.feedback, two_lstm=args.two_lstm,
        cell=args.cell, mem_heads=args.mem_heads,
        vae_in_channels=(3 if args.vae_color else 1),
        jepa_n_heads=(args.jepa_heads if args.jepa_coef > 0 else 0),
        jepa_proto_dim=args.jepa_proto_dim,
        frame_repeat=args.frame_repeat, d_mem=args.d_mem,
        memory_decay=args.memory_decay,
        conv_frontend=args.conv_frontend,
        grid_rows=grid_rows, grid_cols=grid_cols, image_size=image_size,
    )
    model = RViTPaperModel(**model_kwargs).to(device)
    if args.conv_frontend:
        nf = sum(p.numel() for p in model.front.parameters())
        patch_shape = (f"{model.front.patch_height}×{model.front.patch_width}"
                       if model.front.patch_height is not None else "variable-size")
        print(f"[paper] CONV front-end: SE-ResNet (3ch colour, trained end-to-end), "
              f"per-patch {patch_shape}→128; "
              f"front params={nf:,}")
    elif args.vae_color:
        print("[paper] COLOUR front-end (3ch) — value cue (red/green/blue) is VISIBLE to perception")

    # pretrained VAE front-end (the user's hypothesis): load conv1/conv2/fc1, freeze by default
    vae_ckpt = args.vae_checkpoint or cfg_get(cfg, "model.vae_checkpoint", "")
    if args.conv_frontend and vae_ckpt:
        raise SystemExit("--vae-checkpoint is incompatible with --conv-frontend (the conv front-end is trained end-to-end)")
    if vae_ckpt and os.path.exists(vae_ckpt) and not args.conv_frontend:
        vae_blob = torch.load(vae_ckpt, map_location=device, weights_only=False)
        enc = vae_blob.get("encoder_state", vae_blob)
        res = model.front.load_pretrained(enc, freeze=not args.no_freeze_vae)
        mode = "FROZEN" if not args.no_freeze_vae else "fine-tuned"
        kind = vae_blob.get("kind", "grayscale(1ch)?"); vtask = vae_blob.get("task", "?")
        print(f"[paper] loaded {kind} VAE front-end ({mode}, task={vtask}) from {vae_ckpt}: "
              f"missing={len(res.missing_keys)} unexpected={len(res.unexpected_keys)}")
    elif vae_ckpt:
        raise FileNotFoundError(f"--vae-checkpoint {vae_ckpt} not found")

    n_params = sum(p.numel() for p in model.parameters())
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[paper] task={args.task} tokens={model.n_tokens} particles={n_quantiles} "
          f"feedback={args.feedback} memory_decay={args.memory_decay:.3f} "
          f"params={n_params:,} (trainable {n_train:,}) device={device}")

    # resolve the checkpoint dir FIRST so resume can auto-discover from it
    ckpt_dir = (args.checkpoint_dir or cfg_get(cfg, "run.checkpoint_dir", "")
                or os.path.expanduser(f"~/rvit_plus_checkpoints/paper_{args.task}"))
    os.makedirs(ckpt_dir, exist_ok=True)

    init_mode = args.init_mode or cfg_get(cfg, "run.init_mode", "fresh")
    checkpoint_info = None
    resume_checkpoint = None
    initialization_contract = {"mode": "fresh"}
    if init_mode in ("warm_start", "resume"):
        import glob
        # explicit path > the trainer's rolling latest > the run's final > newest .pt in dir
        ckpt_path = args.checkpoint_path or cfg_get(cfg, "run.checkpoint_path", "")
        if not ckpt_path:
            prefer = [os.path.join(ckpt_dir, "rvit_plus_rl_latest.pt"),
                      os.path.join(ckpt_dir, f"rvit_paper_{args.task}_final.pt")]
            found = [c for c in prefer if os.path.exists(c)]
            if not found:
                found = sorted(glob.glob(os.path.join(ckpt_dir, "*.pt")),
                               key=os.path.getmtime, reverse=True)
            ckpt_path = found[0] if found else ""
        if not ckpt_path or not os.path.exists(ckpt_path):
            raise FileNotFoundError(
                f"init_mode='{init_mode}' but NO checkpoint found. checkpoint_path is empty and "
                f"there is no .pt in {ckpt_dir}. Set run.checkpoint_path / --checkpoint-path, "
                f"or use init_mode='fresh' to start over.")
        parent_checkpoint_sha256 = None
        if init_mode == "resume":
            with open(ckpt_path, "rb") as stream:
                checkpoint_bytes = stream.read()
            parent_checkpoint_sha256 = hashlib.sha256(checkpoint_bytes).hexdigest()
            checkpoint_blob = torch.load(io.BytesIO(checkpoint_bytes), map_location=device, weights_only=False)
            if int(checkpoint_blob.get("checkpoint_schema_version", 0)) < 3:
                raise ValueError(
                    "resume requires a schema-v3 replay-excluded trainer checkpoint. Use --init-mode "
                    "warm_start for an intentional weights-only or older-checkpoint restart."
                )
            model.load_state_dict(checkpoint_blob["model_state_dict"], strict=True)
            checkpoint_info = {
                "path": ckpt_path, "ckpt_iter": checkpoint_blob.get("iter"),
                "ckpt_model_kwargs": checkpoint_blob.get("model_kwargs"),
                "strict": True, "loaded": len(checkpoint_blob["model_state_dict"]),
                "skipped": 0, "missing": [], "unexpected": [],
            }
            resume_checkpoint = checkpoint_blob
            initialization_contract = resume_initialization_contract(
                checkpoint_blob,
                expected_parent_sha256=args.expected_parent_sha256,
                resume_checkpoint_path=ckpt_path,
                resume_checkpoint_sha256=parent_checkpoint_sha256,
            )
        else:
            if args.expected_parent_sha256 is not None:
                checkpoint_info, initialization_contract = load_warm_start_parent(
                    model,
                    ckpt_path,
                    expected_sha256=args.expected_parent_sha256,
                    device=device,
                )
            else:
                checkpoint_info = load_checkpoint_weights(
                    model, ckpt_path, strict=False, device=device
                )
                checkpoint_blob = torch.load(
                    ckpt_path, map_location="cpu", weights_only=False
                )
                initialization_contract = {
                    "mode": "warm_start",
                    "checkpoint_path": os.path.abspath(ckpt_path),
                    "checkpoint_sha256": _sha256(ckpt_path),
                    "checkpoint_iteration": checkpoint_blob.get("iter"),
                    "checkpoint_task": checkpoint_blob.get("task"),
                    "strict": False,
                }
        print(f"[paper] {init_mode} LOADED {ckpt_path}\n[paper]   -> {checkpoint_info}")
    else:
        print("[paper] init_mode=fresh (random init)")

    g = lambda k, d: cfg_get(cfg, f"ppo.{k}", d)
    ppo_cfg = PPOConfig(
        lr=args.lr if args.lr is not None else float(g("lr", 3e-4)),
        gamma=args.gamma if args.gamma is not None else float(g("gamma", 0.95)),
        entropy_coef=args.entropy_coef if args.entropy_coef is not None else float(g("entropy_coef", 0.01)),
        mpo_temperature=args.mpo_temperature if args.mpo_temperature is not None else float(g("mpo_temperature", 0.1)),
        bc_alpha=float(g("bc_alpha", 0.1)),
        value_coef=float(g("value_coef", 0.5)),
        qr_kappa=args.qr_kappa if args.qr_kappa is not None else float(g("qr_kappa", 1.0)),
        burn_in_iters=int(g("burn_in_iters", 20)),
        target_update_period=int(g("target_update_period", 0)),
        ema_decay=args.ema_decay if args.ema_decay is not None else float(g("ema_decay", 0.0)),
        buffer_capacity=args.buffer_capacity if args.buffer_capacity is not None
        else int(g("buffer_capacity", 1000)),
        per_n_replay=int(g("per_n_replay", 4)),
        per_alpha=float(g("per_alpha", 0.6)),
        per_beta_start=float(g("per_beta_start", 0.4)),
        per_beta_end=float(g("per_beta_end", 1.0)),
        per_priority_clip=float(g("per_priority_clip", 50.0)),
        jepa_coef=args.jepa_coef, jepa_n_heads=args.jepa_heads, jepa_proto_dim=args.jepa_proto_dim,
        jepa_temporal=(not args.jepa_same_time),
        jepa_tau_student=args.jepa_tau_student,
        jepa_tau_teacher_start=args.jepa_tau_teacher_start,
        jepa_tau_teacher_end=args.jepa_tau_teacher_end,
        jepa_tau_teacher_warmup_iters=args.jepa_tau_warmup,
        jepa_center_momentum=args.jepa_center_momentum,
        jepa_ema_decay=args.jepa_ema_decay,
    )
    print(f"[paper] ppo: reward_scale={1.0 if args.reward_scale is None else args.reward_scale} "
          f"qr_kappa={ppo_cfg.qr_kappa} (critic particles) mpo_temperature={ppo_cfg.mpo_temperature} "
          f"value_coef={ppo_cfg.value_coef} entropy_coef={ppo_cfg.entropy_coef} gamma={ppo_cfg.gamma}")
    iters = args.iters if args.iters is not None else int(g("iters", 18750))
    eps = args.episodes_per_iter if args.episodes_per_iter is not None else int(g("episodes_per_iter", 8))
    if args.start_iteration is not None:
        start_iteration = args.start_iteration
    elif init_mode == "resume" and checkpoint_info is not None:
        checkpoint_iteration = checkpoint_info.get("ckpt_iter")
        if checkpoint_iteration is None:
            raise ValueError("resume checkpoint has no iteration; pass --start-iteration explicitly")
        start_iteration = int(checkpoint_iteration) + 1
    else:
        start_iteration = 0
    if start_iteration < 0:
        raise ValueError("--start-iteration must be non-negative")
    if init_mode == "resume" and checkpoint_info is not None:
        expected_start = int(checkpoint_info["ckpt_iter"]) + 1
        if start_iteration != expected_start:
            raise ValueError(
                f"resume must start at checkpoint iter + 1 ({expected_start}), got {start_iteration}"
            )
    end_iteration = start_iteration + iters - 1
    if init_mode == "resume":
        saved_schedule_final = resume_checkpoint.get("resume_contract", {}).get("schedule_final_iteration")
        if saved_schedule_final is None:
            raise ValueError("resume checkpoint has no absolute schedule_final_iteration")
        schedule_final_iteration = (args.schedule_final_iteration if args.schedule_final_iteration is not None
                                    else int(saved_schedule_final))
    else:
        schedule_final_iteration = (args.schedule_final_iteration if args.schedule_final_iteration is not None
                                    else end_iteration)
    allowed_resume_producer_changes = resolve_schedule_overrun_compatibility(
        init_mode=init_mode,
        phase_final_iteration=end_iteration,
        schedule_final_iteration=schedule_final_iteration,
        explicitly_allowed=args.allow_schedule_overrun_resume,
    )
    print(f"[paper] global iters {start_iteration}..{end_iteration}: {iters} iters × {eps} "
          f"episodes/iter = {iters*eps:,} episodes; schedule_end={schedule_final_iteration}; γ={ppo_cfg.gamma}")
    if allowed_resume_producer_changes:
        print(
            f"[resume] compatibility transition: phase continues past saved schedule end "
            f"{schedule_final_iteration}; completed schedules remain clamped and producer changes "
            f"are restricted to {sorted(allowed_resume_producer_changes)}"
        )

    producer_sha256 = _producer_hashes(args.config, args.experiment_launcher)
    runtime_versions = {
        "python": platform.python_version(),
        "torch": str(torch.__version__),
        "numpy": str(np.__version__),
        "platform": platform.platform(),
    }
    resume_contract = {
        "task": args.task,
        "model_kwargs": model_kwargs,
        "ppo_config": dataclasses.asdict(ppo_cfg),
        "episodes_per_iter": eps,
        "schedule_final_iteration": schedule_final_iteration,
        "training_backend": device.type,
        "runtime_versions": runtime_versions,
        "producer_sha256": producer_sha256,
    }
    checkpoint_metadata = {
        "task": args.task,
        "model_kwargs": model_kwargs,
        "ppo_config": dataclasses.asdict(ppo_cfg),
        "training_args": vars(args).copy(),
        "initialization_contract": initialization_contract,
        "launch_argv": [sys.executable, os.path.abspath(__file__), *sys.argv[1:]],
        "run_started_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_versions": runtime_versions,
        "producer_sha256": producer_sha256,
        "replay_buffer_persisted": False,
        "resume_fidelity": "replay_excluded_trainer_state",
        "resume_contract": resume_contract,
    }
    if resume_checkpoint is not None:
        checkpoint_metadata["parent_checkpoint_path"] = os.path.abspath(ckpt_path)
        checkpoint_metadata["parent_checkpoint_sha256"] = parent_checkpoint_sha256
    if allowed_resume_producer_changes:
        checkpoint_metadata["resume_compatibility_transition"] = {
            "kind": "schedule_overrun_with_saturated_schedules",
            "saved_schedule_final_iteration": schedule_final_iteration,
            "phase_final_iteration": end_iteration,
            "allowed_producer_changes": sorted(allowed_resume_producer_changes),
            "parent_producer_sha256": {
                path: resume_checkpoint["resume_contract"]["producer_sha256"][path]
                for path in sorted(allowed_resume_producer_changes)
            },
            "current_producer_sha256": {
                path: producer_sha256[path]
                for path in sorted(allowed_resume_producer_changes)
            },
        }

    history = train(
        model=model, env=env, n_iterations=iters, episodes_per_iter=eps,
        cfg=ppo_cfg, device=device, log_every=args.log_every,
        checkpoint_dir=ckpt_dir, save_every=args.save_every,
        start_iteration=start_iteration,
        schedule_final_iteration=schedule_final_iteration,
        resume_checkpoint=resume_checkpoint,
        checkpoint_metadata=checkpoint_metadata,
        allow_schedule_overrun=bool(allowed_resume_producer_changes),
        allowed_resume_producer_changes=allowed_resume_producer_changes,
    )
    print(f"[paper] replay-excluded trainer checkpoint saved in {ckpt_dir}; iters logged={len(history)}")


if __name__ == "__main__":
    main()
