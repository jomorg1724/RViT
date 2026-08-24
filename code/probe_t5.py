"""Decisive check: is the change decodable from H2 at the DECISION timestep (t=5, right
after the change) vs trial end (t=6)? The RL actor/critic read H2 every timestep, so this
determines whether Phase 3 (RL heads on the pretrained trunk) has any chance of detecting
the change."""
import numpy as np
import torch

from envs import make_env
from model import RViTPaperModel
from train_rl import pick_device, seed_training_rngs

CKPT = r"C:\Users\jomor\Documents\RViT_runs\vda4_jepa_pretrain_conv_20260821\jepa_pretrain_latest.pt"
device = pick_device("cuda")
seed_training_rngs(0)
ckpt = torch.load(CKPT, map_location="cpu", weights_only=False)
model = RViTPaperModel(**ckpt["model_kwargs"]).to(device)
model.load_state_dict(ckpt["model_state_dict"])
model.encoder.fsq_levels = ckpt.get("fsq_levels", 2)
model.eval()
for p in model.parameters():
    p.requires_grad_(False)

env = make_env("vda4", T=7, frame_repeat=1, min_change_time=5, max_change_time=5,
               noise_multiplier=5.0, curriculum=False, theta=65.0)
T = 7

def probe(X, y, n_classes, epochs=200):
    X = torch.as_tensor(X, dtype=torch.float32)
    y = torch.as_tensor(y, dtype=torch.long)
    n = X.shape[0]
    p = torch.randperm(n)
    tr, te = p[:int(.8 * n)], p[int(.8 * n):]
    net = torch.nn.Sequential(torch.nn.Linear(X.shape[1], 256), torch.nn.ReLU(),
                              torch.nn.Linear(256, n_classes)).to(device)
    o = torch.optim.Adam(net.parameters(), 1e-3)
    ce = torch.nn.CrossEntropyLoss()
    Xt, yt, Xe, ye = X[tr].to(device), y[tr].to(device), X[te].to(device), y[te].to(device)
    for _ in range(epochs):
        o.zero_grad()
        ce(net(Xt), yt).backward()
        o.step()
    return (net(Xe).argmax(-1) == ye).float().mean().item()

feats = {t: {"H2": [], "rawH2": [], "H1": [], "rawH1": []} for t in (5, 6)}
change = []
with torch.no_grad():
    for _ in range(4000):
        env.reset()
        frames = [env.step(0)[0] for _ in range(T)]
        obs = torch.from_numpy(np.stack(frames)).unsqueeze(0).to(device, torch.float32)
        out = model.forward_rl_sequence(obs, return_cell=True, return_raw_memory=True)
        for t in (5, 6):
            c = out["cell_seq"][0, t]
            r = out["raw_memory_seq"][0, t]
            feats[t]["H2"].append(c[1].cpu().numpy())
            feats[t]["H1"].append(c[0].cpu().numpy())
            feats[t]["rawH2"].append(r[1].cpu().numpy())
            feats[t]["rawH1"].append(r[0].cpu().numpy())
        change.append(int(env.change_true))

change = np.array(change)
for t in (5, 6):
    for nm in ("H2", "rawH2", "H1", "rawH1"):
        X = np.stack(feats[t][nm]).reshape(len(change), -1)
        acc = probe(X, change, 2)
        print(f"[t={t}] {nm:6} change_acc={acc:.3f} (chance 0.50)")
