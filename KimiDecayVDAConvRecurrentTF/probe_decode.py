"""Decode probe: can each RL readout decode the change from a GOOD trunk?

Trunk = supervised token-attn checkpoint (acc ~85%, theta 35 at ckpt).
Frozen. Fresh VDA16 trials at fixed theta. Probes on R[:, -1]:
  a) mean-pool -> Linear            (RL v1 decode)
  b) SpatialConvReadout -> TinyHead (RL v2 decode)
  c) flatten(R) -> Linear           (max-info decode)
Null control: same probes on R[:, 0] (pre-stimulus) should be chance.
"""
from __future__ import annotations

import sys
import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, r"C:/Users/jomor/OneDrive/Desktop/RViT_plus_paper_jepa_grid9-20260718T193411Z-1-001/RViT/KimiDecayVDAConvRecurrentTF")

from kda_conv_memory_model import KDAConvMemoryModel
from kda_rl_model import SpatialConvReadout, TinyHead
from envs import make_env


class _MeanPoolHW(nn.Module):
    def forward(self, x):  # (B,C,H,W) -> (B,C)
        return x.mean(dim=(2, 3))

CKPT = r"C:/Users/jomor/Documents/RViT_runs/vda16_kda_token_attn_c128_seed0/checkpoints/kda_convmem_latest.pt"
THETA = 35.0
N_TRAIN, N_TEST = 4096, 1024
SEED = 123


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
            R = model.forward_seq(obs)                       # (B,T,4C,16,16)
            feats.append(R[:, t_index].float().cpu())
            labels.append(np.array(y_list))
            done += bs
    return torch.cat(feats), torch.from_numpy(np.concatenate(labels)).long()


def train_probe(make_probe, Xtr, ytr, Xte, yte, device, epochs=60):
    probe = make_probe().to(device)
    opt = torch.optim.Adam(probe.parameters(), lr=1e-3)
    ce = nn.CrossEntropyLoss()
    Xtr, ytr = Xtr.to(device), ytr.to(device)
    for ep in range(epochs):
        perm = torch.randperm(len(Xtr), device=device)
        for i in range(0, len(Xtr), 256):
            idx = perm[i:i + 256]
            loss = ce(probe(Xtr[idx]), ytr[idx])
            opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        acc = (probe(Xte.to(device)).argmax(-1) == yte.to(device)).float().mean().item()
    return acc, sum(p.numel() for p in probe.parameters())


def main():
    torch.manual_seed(SEED); np.random.seed(SEED)
    device = torch.device("cuda")
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    model = KDAConvMemoryModel(
        n_channels=128, map_size=16, proto_dim=256, mem_every=3,
        accum_mode="kda", accum_decay=0.5, kda_heads=4, kda_head_dim=32,
        attn_mode="token",
    ).to(device)
    model.load_state_dict(ck["model_state_dict"]); model.eval()
    print(f"trunk: collection={ck['collection']} theta={ck['theta']}")

    env = make_env("vda16", T=7, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False)
    env.theta = THETA

    print("collecting ...")
    Xtr_last, ytr = collect(env, model, N_TRAIN, device, t_index=-1)
    Xte_last, yte = collect(env, model, N_TEST, device, t_index=-1)
    Xtr_t0, ytr0 = collect(env, model, N_TRAIN, device, t_index=0)
    Xte_t0, yte0 = collect(env, model, N_TEST, device, t_index=0)
    print(f"base rate: {float(yte.float().mean()):.3f}")

    probes = {
        "meanpool_linear (RL v1)": lambda: nn.Sequential(
            _MeanPoolHW(), nn.Linear(512, 2)),
        "conv_readout+FFN (RL v2)": lambda: nn.Sequential(
            SpatialConvReadout(512, 16), TinyHead(SpatialConvReadout(512, 16).out_dim, 2, hidden=64)),
        "flatten_linear (max info)": lambda: nn.Sequential(
            nn.Flatten(1), nn.Linear(512 * 16 * 16, 2)),
    }

    for name, mk2 in probes.items():
        acc_last, nparams = train_probe(mk2, Xtr_last, ytr, Xte_last, yte, device)
        acc_t0, _ = train_probe(mk2, Xtr_t0, ytr0, Xte_t0, yte0, device, epochs=20)
        print(f"{name:32s} params={nparams:>9,}  R@last acc={acc_last:.3f}   R@t0 acc={acc_t0:.3f}")


if __name__ == "__main__":
    main()
