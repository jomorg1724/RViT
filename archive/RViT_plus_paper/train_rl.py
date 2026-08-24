"""
Train the EXACT paper Recurrent ViT (Morgan/Albanna/Herman) with our PAC + QR-DQN +
PER harness and EMA targets, on the paper's cued orientation-change-detection task.

    python RViT_plus_paper/train_rl.py --device mps          # 150k episodes (18,750 iters × 8)

The network is the paper's (VAE front-end → multiplicative ViT → spatial xLSTM →
flattened-H readout); the only departures from the paper, all locked with the user:
QR-DQN critic (our harness) with 5 particles, EMA target (instead of hard-copy), γ=0.95,
VAE trained end-to-end (no pretrain). If this does not reproduce the paper's cueing
behaviour, the problem is not the architecture.
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


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Train the exact paper Recurrent ViT")
    p.add_argument("--task", default="validity4", choices=sorted(TASKS))
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
    p.add_argument("--n-quantiles", type=int, default=None, help="critic particles (default 5)")
    p.add_argument("--n-actions", type=int, default=2)
    p.add_argument("--two-lstm", action="store_true",
                   help="stack a 2nd xLSTM: LSTM1's H1 feeds the attention, LSTM2(H1)=H2 feeds the heads")
    p.add_argument("--feedback", default="multiplicative",
                   choices=["multiplicative", "film", "hyper", "hyper_codebook", "affine", "dualhead", "crossattn", "dualmem", "affine_cascade"],
                   help="how memory feedback enters Q/K/V: multiplicative (paper, Q=(XW)⊙(HW)) | "
                        "film (Q=(XW)⊙(1+HW), identity-init) | hyper (H GENERATES the Q/K/V "
                        "weights: W_P=reshape(G_P(bottleneck(H))), P=X·W_P — fast weights) | "
                        "hyper_codebook (hyper Q/K + V=codebook (H_CB), v12 downstream) | "
                        "affine (H derives scale-MATRIX Γ + shift β: X'=Γ(H)·X+β(H), then SA) | "
                        "affine_cascade (TWO affine transformers + TWO xLSTMs: T1(X,fb=H1)→Z1→H1, "
                        "T2(Z1,fb=H2)→Z2→H2; split readout actor←H2, critic←H1).")
    p.add_argument("--init-action-bias", type=float, nargs=2, default=[0.0, -1.5])
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--gamma", type=float, default=None)
    p.add_argument("--entropy-coef", type=float, default=None)
    p.add_argument("--ema-decay", type=float, default=None, help="EMA target decay (default from config)")
    p.add_argument("--buffer-capacity", type=int, default=None)
    p.add_argument("--vae-checkpoint", default=None,
                   help="pretrained PatchVAE checkpoint; loads conv1/conv2/fc1 into the front-end")
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

    torch.manual_seed(args.seed)
    device = pick_device(args.device or cfg_get(cfg, "run.device", ""))

    env = make_env(args.task, T=args.T, min_change_time=args.min_change_time,
                   max_change_time=args.max_change_time, noise_multiplier=args.noise)
    seq_len = int(env.T)

    n_quantiles = args.n_quantiles if args.n_quantiles is not None \
        else int(cfg_get(cfg, "model.rl.n_quantiles", 5))
    model_kwargs = dict(
        n_actions=args.n_actions, n_quantiles=n_quantiles,
        init_action_bias=list(args.init_action_bias), seq_len=seq_len,
        feedback=args.feedback, two_lstm=args.two_lstm,
    )
    model = RViTPaperModel(**model_kwargs).to(device)

    # pretrained VAE front-end (the user's hypothesis): load conv1/conv2/fc1, freeze by default
    vae_ckpt = args.vae_checkpoint or cfg_get(cfg, "model.vae_checkpoint", "")
    if vae_ckpt and os.path.exists(vae_ckpt):
        vae_blob = torch.load(vae_ckpt, map_location=device, weights_only=False)
        enc = vae_blob.get("encoder_state", vae_blob)
        res = model.front.load_pretrained(enc, freeze=not args.no_freeze_vae)
        mode = "FROZEN" if not args.no_freeze_vae else "fine-tuned"
        print(f"[paper] loaded pretrained VAE front-end ({mode}) from {vae_ckpt}: "
              f"missing={len(res.missing_keys)} unexpected={len(res.unexpected_keys)}")
    elif vae_ckpt:
        raise FileNotFoundError(f"--vae-checkpoint {vae_ckpt} not found")

    n_params = sum(p.numel() for p in model.parameters())
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[paper] task={args.task} tokens={model.n_tokens} particles={n_quantiles} "
          f"feedback={args.feedback} params={n_params:,} (trainable {n_train:,}) device={device}")

    # resolve the checkpoint dir FIRST so resume can auto-discover from it
    ckpt_dir = (args.checkpoint_dir or cfg_get(cfg, "run.checkpoint_dir", "")
                or os.path.expanduser(f"~/rvit_plus_checkpoints/paper_{args.task}"))
    os.makedirs(ckpt_dir, exist_ok=True)

    init_mode = args.init_mode or cfg_get(cfg, "run.init_mode", "fresh")
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
        info = load_checkpoint_weights(model, ckpt_path, strict=(init_mode == "resume"), device=device)
        print(f"[paper] {init_mode} LOADED {ckpt_path}\n[paper]   -> {info}")
    else:
        print("[paper] init_mode=fresh (random init)")

    g = lambda k, d: cfg_get(cfg, f"ppo.{k}", d)
    ppo_cfg = PPOConfig(
        lr=args.lr if args.lr is not None else float(g("lr", 3e-4)),
        gamma=args.gamma if args.gamma is not None else float(g("gamma", 0.95)),
        entropy_coef=args.entropy_coef if args.entropy_coef is not None else float(g("entropy_coef", 0.01)),
        mpo_temperature=float(g("mpo_temperature", 0.1)),
        bc_alpha=float(g("bc_alpha", 0.1)),
        value_coef=float(g("value_coef", 0.5)),
        qr_kappa=float(g("qr_kappa", 1.0)),
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
    )
    iters = args.iters if args.iters is not None else int(g("iters", 18750))
    eps = args.episodes_per_iter if args.episodes_per_iter is not None else int(g("episodes_per_iter", 8))
    print(f"[paper] {iters} iters × {eps} episodes/iter = {iters*eps:,} episodes; γ={ppo_cfg.gamma}")

    history = train(
        model=model, env=env, n_iterations=iters, episodes_per_iter=eps,
        cfg=ppo_cfg, device=device, log_every=args.log_every,
        checkpoint_dir=ckpt_dir, save_every=args.save_every,
    )
    final = os.path.join(ckpt_dir, f"rvit_paper_{args.task}_final.pt")
    torch.save({"iter": iters, "model_state_dict": model.state_dict(),
                "model_kwargs": model_kwargs, "task": args.task}, final)
    print(f"[paper] saved {final}; iters logged={len(history)}")


if __name__ == "__main__":
    main()
