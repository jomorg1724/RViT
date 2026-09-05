"""Probe the RL-from-scratch trunk: is the change signal in R at all?

Same decode probes as probe_decode.py, but the trunk is the RL checkpoint
(KDARLModel, attn=token, from scratch, stuck at chance/theta=65).
R comes from forward_rl_sequence(return_cell=True) with memory noise OFF.
Probes at theta=65 (the RL training condition).
"""
from __future__ import annotations

import sys
import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, r"C:/Users/jomor/OneDrive/Desktop/RViT_plus_paper_jepa_grid9-20260718T193411Z-1-001/RViT/KimiDecayVDAConvRecurrentTF")

from kda_rl_model import KDARLModel, SpatialConvReadout, TinyHead
from envs import make_env

CKPTS = {
    "rl_token_jepa1_iter23k": r"C:/Users/jomor/Documents/RViT_runs/vda16_kda_rl_token_jepa1_seed0/checkpoints/rvit_plus_rl_latest.pt",
}
THETA = 65.0
N_TRAIN, N_TEST = 4096, 1024
SEED = 321


class _MeanPoolHW(nn.Module):
    def forward(self, x):
        return x.mean(dim=(2, 3))


def collect(env, model, n, device, t_index):
    feats, labels = [], []
    with torch.no_grad():
        done = 0
        while done < n:
            bs = min(64, n - done)
            obs_list, y_list = [], []
            for _ in range(bs):
                env.reset()
                frames = [env.step(0)[0] for _ in range(env.T)]
                obs_list.append(np.stack(frames))
                y_list.append(int(env.change_true))
            obs = torch.from_numpy(np.stack(obs_list)).to(device, torch.float32)
            out = model.forward_rl_sequence(obs, return_cell=True, inject_memory_noise=False)
            R = out["cell_seq"]                            # (B,T,4C,16,16)
            feats.append(R[:, t_index].float().cpu())
            labels.append(np.array(y_list))
            done += bs
    return torch.cat(feats), torch.from_numpy(np.concatenate(labels)).long()


def train_probe(mk, Xtr, ytr, Xte, yte, device, epochs=60):
    probe = mk().to(device)
    opt = torch.optim.Adam(probe.parameters(), lr=1e-3)
    ce = nn.CrossEntropyLoss()
    Xtr, ytr = Xtr.to(device), ytr.to(device)
    for _ in range(epochs):
        perm = torch.randperm(len(Xtr), device=device)
        for i in range(0, len(Xtr), 256):
            idx = perm[i:i + 256]
            loss = ce(probe(Xtr[idx]), ytr[idx])
            opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        acc = (probe(Xte.to(device)).argmax(-1) == yte.to(device)).float().mean().item()
    return acc


def main():
    torch.manual_seed(SEED); np.random.seed(SEED)
    device = torch.device("cuda")
    env = make_env("vda16", T=7, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False)
    env.theta = THETA

    probes = {
        "meanpool_linear": lambda: nn.Sequential(_MeanPoolHW(), nn.Linear(512, 2)),
        "conv_readout+FFN": lambda: nn.Sequential(
            SpatialConvReadout(512, 16), TinyHead(SpatialConvReadout(512, 16).out_dim, 2, hidden=64)),
    }

    for name, path in CKPTS.items():
        ck = torch.load(path, map_location="cpu", weights_only=False)
        meta = ck.get("training_args", {})
        model = KDARLModel(n_channels=128, map_size=16, proto_dim=256,
                           mem_every=3, accum_mode="kda", kda_heads=4, kda_head_dim=32,
                           attn_mode="token").to(device)
        # only the backbone matters for probing; heads differ across variants
        sd = {k: v for k, v in ck["model_state_dict"].items() if k.startswith("backbone.")}
        missing, unexpected = model.load_state_dict(sd, strict=False)
        model.eval()
        print(f"\n[{name}] iter={ck.get('iter')} theta_ckpt={ck.get('environment_state', {}).get('theta')}")
        print(f"  missing={len(missing)} unexpected={len(unexpected)}")
        if missing:
            print("  missing sample:", [m for m in missing if m.startswith('backbone')][:5], "...")

        Xtr, ytr = collect(env, model, N_TRAIN, device, t_index=-1)
        Xte, yte = collect(env, model, N_TEST, device, t_index=-1)
        for pname, mk in probes.items():
            acc = train_probe(mk, Xtr, ytr, Xte, yte, device)
            print(f"  {pname:20s} R@last acc={acc:.3f}")


if __name__ == "__main__":
    main()
