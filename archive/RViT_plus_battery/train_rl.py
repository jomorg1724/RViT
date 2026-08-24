"""
Train the canonical Recurrent ViT on any battery task with the shared harness.

    python RViT_plus_battery/train_rl.py --task validity4 --iters 15000 --device mps
    python RViT_plus_battery/train_rl.py --task krauzlis  --iters 15000 --device mps
    python RViT_plus_battery/train_rl.py --task setsize9  --iters 15000 --device mps

One model class (RViTPlusModel), one harness (PER + PAC + QR-DQN). The only
per-task differences are the env (via --task) and the front-end grid (auto from the
task registry). Checkpoints go OUTSIDE the repo (Drive sync corrupts live .pt files).
"""
from __future__ import annotations

import argparse
import os
import sys

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from config.loader import load_config, cfg_get, load_checkpoint_weights  # noqa: E402
from envs import make_env, task_grid, TASKS                              # noqa: E402
from model import RViTPlusModel                                       # noqa: E402
from ppo import PPOConfig, train                                         # noqa: E402


def pick_device(name: str) -> torch.device:
    if name in ("mps", "cuda", "cpu"):
        return torch.device(name)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train the Recurrent ViT on a battery task")
    p.add_argument("--task", default="validity4", choices=sorted(TASKS))
    # task timeline — defaults are the paper's 7-step / change-at-t=5 structure
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--min-change-time", type=int, default=5)
    p.add_argument("--max-change-time", type=int, default=5)
    p.add_argument("--noise", type=float, default=5.0)
    p.add_argument("--config", default=os.path.join(_HERE, "config", "default.json"))
    p.add_argument("--init-mode", choices=["fresh", "warm_start", "resume"], default=None)
    p.add_argument("--checkpoint-path", default=None)
    p.add_argument("--checkpoint-dir", default=None)
    p.add_argument("--iters", type=int, default=None)
    p.add_argument("--episodes-per-iter", type=int, default=None)
    p.add_argument("--front-end", default="pixel", choices=["pixel", "patches", "conv", "mlp", "vae"],
                   help="pixel (1 token/stimulus, default) | patches (ViT patchification, "
                        "--patch-size 5 → 100 tokens, the v11_part2 resolution) | conv | mlp | "
                        "vae (4-patch pretrained-VAE encoder, 128-d tokens; use --vae-checkpoint)")
    p.add_argument("--patch-size", type=int, default=5, help="for --front-end patches (5 → 100 tokens)")
    p.add_argument("--vae-checkpoint", default=None,
                   help="pretrained PatchVAE ckpt; with --front-end vae, loads conv1/conv2/fc1 (frozen)")
    p.add_argument("--no-freeze-vae", action="store_true", help="fine-tune the VAE front-end")
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--d-mem", type=int, default=128)
    p.add_argument("--tx-heads", type=int, default=1)
    p.add_argument("--n-lstm", type=int, default=2)
    p.add_argument("--readout", default="Z", choices=["Z", "H1", "H2"],
                   help="what the actor/critic read: Z block output (default), or H1 / H2 memory")
    p.add_argument("--encoder", default="crosstalk",
                   choices=["filmblock", "codebook", "codebook_v12", "twolayer", "crosstalk",
                            "broadcast_film", "broadcast"],
                   help="filmblock (default) | codebook (FiLM Q/K + codebook V) | "
                        "codebook_v12 (v12-faithful: Q(X), K(H2), V=codebook) | "
                        "twolayer (T1 spread → T2 codebook) | "
                        "crosstalk (v11_part2 dual-stream μ→actor / q→critic, split readout) | "
                        "broadcast_film (broadcast self-attn + FiLM gate, same split) | "
                        "broadcast (straight additive broadcast self-attn, same split)")
    p.add_argument("--conv-channels", type=int, default=64)
    p.add_argument("--n-conv-layers", type=int, default=2)
    p.add_argument("--conv-kernel", type=int, default=3)
    p.add_argument("--n-quantiles", type=int, default=51)
    p.add_argument("--n-actions", type=int, default=2)
    p.add_argument("--init-action-bias", type=float, nargs=2, default=[0.0, -1.5])
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--gamma", type=float, default=None)
    p.add_argument("--entropy-coef", type=float, default=None)
    p.add_argument("--buffer-capacity", type=int, default=None,
                   help="PER episode-buffer capacity (default from config; config now 1000)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="")
    p.add_argument("--save-every", type=int, default=200)
    p.add_argument("--log-every", type=int, default=5)
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    cfg = {}
    if os.path.exists(args.config):
        cfg = load_config(args.config)

    torch.manual_seed(args.seed)
    device = pick_device(args.device or cfg_get(cfg, "run.device", ""))

    # ── env (+ grid) ─────────────────────────────────────────────────────────
    env = make_env(args.task, T=args.T, min_change_time=args.min_change_time,
                   max_change_time=args.max_change_time, noise_multiplier=args.noise)
    gr, gc = task_grid(args.task)
    seq_len = int(env.T)

    # ── model ────────────────────────────────────────────────────────────────
    model_kwargs = dict(
        in_channels=3, image_h=env.S, image_w=env.S,
        grid_rows=gr, grid_cols=gc, front_end=args.front_end, patch_size=args.patch_size,
        d_model=args.d_model, d_mem=args.d_mem, tx_heads=args.tx_heads,
        tx_layers=1, n_lstm=args.n_lstm, readout=args.readout, encoder=args.encoder,
        conv_channels=args.conv_channels,
        n_conv_layers=args.n_conv_layers, conv_kernel=args.conv_kernel,
        n_actions=args.n_actions, n_quantiles=args.n_quantiles,
        init_action_bias=list(args.init_action_bias), seq_len=seq_len,
    )
    model = RViTPlusModel(**model_kwargs).to(device)

    # pretrained VAE front-end (perception the task can't learn from reward)
    if args.vae_checkpoint:
        if args.front_end != "vae":
            raise ValueError("--vae-checkpoint requires --front-end vae")
        if not os.path.exists(args.vae_checkpoint):
            raise FileNotFoundError(f"--vae-checkpoint {args.vae_checkpoint} not found")
        blob = torch.load(args.vae_checkpoint, map_location=device, weights_only=False)
        enc = blob.get("encoder_state", blob)
        res = model.front.load_pretrained(enc, freeze=not args.no_freeze_vae)
        print(f"[RViT] loaded pretrained VAE front-end ({'FROZEN' if not args.no_freeze_vae else 'fine-tuned'}) "
              f"from {args.vae_checkpoint}: missing={len(res.missing_keys)} unexpected={len(res.unexpected_keys)}")

    n_params = sum(p.numel() for p in model.parameters())
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[RViT] task={args.task} grid={gr}x{gc} tokens={model.n_tokens} "
          f"front_end={args.front_end} params={n_params:,} (trainable {n_train:,}) device={device}")

    # ── checkpoint init ───────────────────────────────────────────────────────
    # checkpoint dir includes BOTH task and encoder so variants never overwrite each other.
    # Resolve it FIRST so resume can auto-discover the checkpoint from it.
    ckpt_dir = (args.checkpoint_dir or cfg_get(cfg, "run.checkpoint_dir", "")
                or os.path.expanduser(f"~/rvit_plus_checkpoints/{args.task}_{args.encoder}"))
    os.makedirs(ckpt_dir, exist_ok=True)

    init_mode = args.init_mode or cfg_get(cfg, "run.init_mode", "fresh")
    if init_mode in ("warm_start", "resume"):
        import glob
        # explicit path > the trainer's rolling latest > the run's final > newest .pt in dir
        ckpt_path = args.checkpoint_path or cfg_get(cfg, "run.checkpoint_path", "")
        if not ckpt_path:
            prefer = [os.path.join(ckpt_dir, "rvit_plus_rl_latest.pt"),
                      os.path.join(ckpt_dir, f"rvit_plus_{args.task}_{args.encoder}_final.pt")]
            found = [c for c in prefer if os.path.exists(c)]
            if not found:
                found = sorted(glob.glob(os.path.join(ckpt_dir, "*.pt")),
                               key=os.path.getmtime, reverse=True)
            ckpt_path = found[0] if found else ""
        if not ckpt_path or not os.path.exists(ckpt_path):
            raise FileNotFoundError(
                f"init_mode='{init_mode}' but NO checkpoint found. checkpoint_path is empty and "
                f"there is no .pt in {ckpt_dir}. Set run.checkpoint_path / --checkpoint-path / "
                f"--checkpoint-dir, or use init_mode='fresh' to start over.")
        info = load_checkpoint_weights(model, ckpt_path, strict=(init_mode == "resume"), device=device)
        print(f"[RViT] {init_mode} LOADED {ckpt_path}\n[RViT]   -> {info}")
    else:
        print("[RViT] init_mode=fresh (random init)")

    ppo_cfg = PPOConfig(
        lr=args.lr if args.lr is not None else float(cfg_get(cfg, "ppo.lr", 3e-4)),
        gamma=args.gamma if args.gamma is not None else float(cfg_get(cfg, "ppo.gamma", 0.99)),
        entropy_coef=args.entropy_coef if args.entropy_coef is not None
        else float(cfg_get(cfg, "ppo.entropy_coef", 0.01)),
        buffer_capacity=args.buffer_capacity if args.buffer_capacity is not None
        else int(cfg_get(cfg, "ppo.buffer_capacity", 200)),
    )
    iters = args.iters if args.iters is not None else int(cfg_get(cfg, "ppo.iters", 15000))
    eps = args.episodes_per_iter if args.episodes_per_iter is not None \
        else int(cfg_get(cfg, "ppo.episodes_per_iter", 8))

    history = train(
        model=model, env=env, n_iterations=iters, episodes_per_iter=eps,
        cfg=ppo_cfg, device=device, log_every=args.log_every,
        checkpoint_dir=ckpt_dir, save_every=args.save_every,
    )
    final = os.path.join(ckpt_dir, f"rvit_plus_{args.task}_{args.encoder}_final.pt")
    torch.save({"iter": iters, "model_state_dict": model.state_dict(),
                "model_kwargs": model_kwargs, "task": args.task, "encoder": args.encoder}, final)
    print(f"[RViT] saved {final}; iters logged={len(history)}")


if __name__ == "__main__":
    main()
