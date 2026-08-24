"""Quick diagnostic: MLP (non-linear) probe on the saved probe features.

Distinguishes 'info is non-linear' from 'info is absent': if an MLP recovers
cue/change above chance where the linear probe stayed at chance, the encoding is
non-linear; if it stays at chance too, the pretrained memory genuinely lacks the info.
"""
import numpy as np
import torch

data = np.load(r"C:\Users\jomor\Documents\RViT_runs\vda4_jepa_pretrain_20260821\probe_features.npz")
change = data["change"]
cue = data["cue"]


def mlp_probe(X, y, n_classes, device, epochs=200, lr=1e-3):
    X = torch.as_tensor(X, dtype=torch.float32)
    y = torch.as_tensor(y, dtype=torch.long)
    n = X.shape[0]
    perm = torch.randperm(n)
    n_tr = int(0.8 * n)
    tr, te = perm[:n_tr], perm[n_tr:]
    net = torch.nn.Sequential(
        torch.nn.Linear(X.shape[1], 256), torch.nn.ReLU(),
        torch.nn.Linear(256, n_classes),
    ).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    ce = torch.nn.CrossEntropyLoss()
    Xtr, ytr, Xte, yte = X[tr].to(device), y[tr].to(device), X[te].to(device), y[te].to(device)
    for _ in range(epochs):
        opt.zero_grad()
        loss = ce(net(Xtr), ytr)
        loss.backward()
        opt.step()
    with torch.no_grad():
        return (net(Xte).argmax(-1) == yte).float().mean().item()


device = "cuda" if torch.cuda.is_available() else "cpu"
for name in ["H2", "rawH2", "H1", "rawH1"]:
    X = data[name]
    acc_change = mlp_probe(X, change, 2, device)
    acc_cue = mlp_probe(X, cue, 4, device)
    print(f"[mlp] {name:<6} change_acc={acc_change:.3f} (chance 0.50)  cue_acc={acc_cue:.3f} (chance 0.25)")
