"""
Phase 2 — decode cues/changes from the pretrained memory layers.

Freezes the pretrained trunk and asks a simple linear probe whether the memory
outputs H1/H2 at TRIAL COMPLETION (t = T-1) linearly encode:
  * whether a change occurred (change_true, 2-way, chance 50%)
  * which cell was cued (cue_index, 4-way, chance 25%)

The pretrained checkpoint (jepa_pretrain_latest.pt) supplies the trunk weights.
Features are the POST-nonlinearity memory outputs (binary under FSQ), collected
with inject_memory_noise=False (clean readout — we are measuring, not regularizing).
"""
from __future__ import annotations

import argparse
import os

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in __import__("sys").path:
    __import__("sys").path.insert(0, _HERE)

from envs import make_env  # noqa: E402
from model import RViTPaperModel  # noqa: E402
from train_rl import pick_device, seed_training_rngs  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Linear-probe the pretrained memory layers")
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--n-trials", type=int, default=20000)
    p.add_argument("--task", default="vda4")
    p.add_argument("--T", type=int, default=7)
    p.add_argument("--frame-repeat", type=int, default=1)
    p.add_argument("--min-change-time", type=int, default=5)
    p.add_argument("--max-change-time", type=int, default=5)
    p.add_argument("--noise", type=float, default=5.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="cuda")
    p.add_argument("--epochs", type=int, default=60)
    p.add_argument("--probe-lr", type=float, default=1e-3)
    p.add_argument("--out-dir", default=None)
    return p


def train_probe(X, y, n_classes, device, epochs, lr):
    """Train a single linear layer with cross-entropy; return test accuracy."""
    X = torch.as_tensor(X, dtype=torch.float32)
    y = torch.as_tensor(y, dtype=torch.long)
    n = X.shape[0]
    perm = torch.randperm(n)
    n_tr = int(0.8 * n)
    tr_idx, te_idx = perm[:n_tr], perm[n_tr:]
    probe = torch.nn.Linear(X.shape[1], n_classes).to(device)
    opt = torch.optim.Adam(probe.parameters(), lr=lr)
    ce = torch.nn.CrossEntropyLoss()
    Xtr, ytr = X[tr_idx].to(device), y[tr_idx].to(device)
    Xte, yte = X[te_idx].to(device), y[te_idx].to(device)
    for _ in range(epochs):
        opt.zero_grad()
        loss = ce(probe(Xtr), ytr)
        loss.backward()
        opt.step()
    with torch.no_grad():
        acc = (probe(Xte).argmax(-1) == yte).float().mean().item()
    return acc


def main() -> None:
    args = build_parser().parse_args()
    seed_training_rngs(args.seed)
    device = pick_device(args.device)

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    model_kwargs = ckpt["model_kwargs"]
    model = RViTPaperModel(**model_kwargs).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    model.encoder.fsq_levels = ckpt.get("fsq_levels", model.encoder.fsq_levels)
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)

    env = make_env(
        args.task, T=args.T, frame_repeat=args.frame_repeat,
        min_change_time=args.min_change_time, max_change_time=args.max_change_time,
        noise_multiplier=args.noise, curriculum=False, theta=65.0,
    )
    T = int(env.T)

    H1_list, H2_list = [], []
    rawH1_list, rawH2_list = [], []
    cue_list, change_list, prop_list, change_idx_list = [], [], [], []
    with torch.no_grad():
        for _ in range(args.n_trials):
            env.reset()
            frames = []
            for _ in range(T):
                o, _r, _d, _i = env.step(0)
                frames.append(o)
            obs = torch.from_numpy(np.stack(frames)).unsqueeze(0).to(device, torch.float32)  # (1,T,S,S,3)
            out = model.forward_rl_sequence(obs, return_cell=True, return_raw_memory=True)  # clean
            cell = out["cell_seq"][0, -1]  # (2, tokens, d_mem) = [H1, H2] at trial end
            H1_list.append(cell[0].cpu().numpy())
            H2_list.append(cell[1].cpu().numpy())
            raw = out["raw_memory_seq"][0, -1]  # (2, tokens, d_mem) pre-quantization
            rawH1_list.append(raw[0].cpu().numpy())
            rawH2_list.append(raw[1].cpu().numpy())
            cue_list.append(int(env.cue_index))
            change_list.append(int(env.change_true))
            prop_list.append(float(env.proportion))
            change_idx_list.append(int(env.change_index))

    H1 = np.stack(H1_list).reshape(args.n_trials, -1)
    H2 = np.stack(H2_list).reshape(args.n_trials, -1)
    rawH1 = np.stack(rawH1_list).reshape(args.n_trials, -1)
    rawH2 = np.stack(rawH2_list).reshape(args.n_trials, -1)
    cat = np.concatenate([H1, H2], axis=1)
    rawcat = np.concatenate([rawH1, rawH2], axis=1)
    cue = np.array(cue_list)
    change = np.array(change_list)

    results = {}
    for name, X in [("H1", H1), ("H2", H2), ("H1+H2", cat),
                    ("rawH1", rawH1), ("rawH2", rawH2), ("rawH1+rawH2", rawcat)]:
        acc_change = train_probe(X, change, 2, device, args.epochs, args.probe_lr)
        acc_cue = train_probe(X, cue, 4, device, args.epochs, args.probe_lr)
        results[name] = {"change_acc": acc_change, "cue_acc": acc_cue}
        print(f"[probe] {name:<11} change_acc={acc_change:.3f} (chance 0.50)  "
              f"cue_acc={acc_cue:.3f} (chance 0.25)")

    out_dir = args.out_dir or os.path.dirname(args.checkpoint)
    np.savez(
        os.path.join(out_dir, "probe_features.npz"),
        H1=H1, H2=H2, rawH1=rawH1, rawH2=rawH2, cue=cue, change=change,
        proportion=np.array(prop_list), change_index=np.array(change_idx_list),
    )
    import json
    with open(os.path.join(out_dir, "probe_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"[probe] saved features + results to {out_dir}")


if __name__ == "__main__":
    main()
