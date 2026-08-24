"""
E7 — pathway dissociation for the crosstalk (μ/q) model: the representational test that
makes the split a neuroscience claim rather than an RL footnote.

The hypothesis: the image-grounded μ pathway (→ actor) carries the CHANGE-EVIDENCE / decision
variable, while the memory-grounded q pathway (→ critic) carries the VALUE / context variable.
We test it by decoding, from each stream's output at the change frame, two families of labels:
  • evidence variables  : change-present (binary), change-location (N-way on change trials)
  • value/context vars  : cue value (colour), cue reliability (proportion), cued location
A 2×(streams) decoding-accuracy table with the predicted cross-over (evidence ≫ from μ,
value/context ≫ from q) IS the double dissociation.

(Why not a behavioural clamp-q-vs-μ test? At INFERENCE the critic doesn't drive the action,
so "lesion q → detection spared" is trivially true and uninformative. The behavioural
dissociation lives at TRAINING time — the coupling-required / μ-must-drive result — and the
inference-time dissociation is representational, which is what this script measures.)

    python RViT_plus_battery/analysis/e7_pathway_dissociation.py \
        --checkpoint ~/rvit_plus_checkpoints/film_vda4_crosstalk/rvit_plus_vda4_crosstalk_final.pt \
        --task vda4 --n-trials 4000

Run on a value-cue task (vda4) so there's value to decode. DO NOT run while MPS training
jobs are live (CPU safety) — thread-capped + CPU default.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")

import argparse
import sys

import numpy as np
import torch

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
torch.set_num_threads(2)

from analysis.common import load_model           # noqa: E402
from envs import make_env                         # noqa: E402

_COLOR_TO_INT = {"red": 0, "green": 1, "blue": 2, "white": 0}


@torch.no_grad()
def collect(model, env, n_trials, device="cpu"):
    """Roll out; at the change frame grab each stream output (flattened) + trial labels."""
    n_streams = None
    Zs = {}          # stream_idx -> list of flattened vectors
    rows = []
    for _ in range(n_trials):
        obs = env.reset()
        states = model.init_states(1, device=device)
        ct = int(env.change_time)
        grabbed = None
        for t in range(env.T):
            x = torch.from_numpy(np.transpose(obs, (2, 0, 1))).float().unsqueeze(0).to(device)
            out = model.rl_step(x, states)
            states = out["new_states"]
            if t == ct:                                   # the change frame
                rec = out["rec"]
                grabbed = [z[0].reshape(-1).cpu().numpy() for z in rec]   # flatten (N*d) per stream
            act = int(torch.argmax(out["actor_logits"][0]))
            obs, r, done, info = env.step(act)
            if done:
                break
        if grabbed is None:
            continue
        if n_streams is None:
            n_streams = len(grabbed)
            for s in range(n_streams):
                Zs[s] = []
        for s in range(n_streams):
            Zs[s].append(grabbed[s])
        rows.append(dict(change=int(env.change_true),
                         change_index=int(env.change_index),
                         cued_index=int(env.cue_index),
                         value=_COLOR_TO_INT.get(getattr(env, "cue_color", "white"), 0),
                         prop=float(env.proportion)))
    Z = {s: np.stack(Zs[s]) for s in Zs}
    labels = {k: np.array([r[k] for r in rows]) for k in rows[0]}
    return Z, labels, n_streams


def linear_decode(X, y, device="cpu", epochs=400, seed=0):
    """Standardize, 80/20 split, train a linear softmax classifier; return (test_acc, chance)."""
    classes = sorted(set(int(v) for v in y))
    if len(classes) < 2:
        return float("nan"), float("nan")
    remap = {c: i for i, c in enumerate(classes)}
    y = np.array([remap[int(v)] for v in y])
    n_cls = len(classes)
    mu, sd = X.mean(0, keepdims=True), X.std(0, keepdims=True) + 1e-6
    X = (X - mu) / sd
    g = torch.Generator().manual_seed(seed)
    n = len(y); idx = torch.randperm(n, generator=g).numpy()
    ntr = int(0.8 * n)
    Xtr = torch.tensor(X[idx[:ntr]], dtype=torch.float32, device=device)
    ytr = torch.tensor(y[idx[:ntr]], dtype=torch.long, device=device)
    Xte = torch.tensor(X[idx[ntr:]], dtype=torch.float32, device=device)
    yte = torch.tensor(y[idx[ntr:]], dtype=torch.long, device=device)
    clf = torch.nn.Linear(X.shape[1], n_cls).to(device)
    opt = torch.optim.Adam(clf.parameters(), lr=1e-2, weight_decay=1e-3)
    lossf = torch.nn.CrossEntropyLoss()
    for _ in range(epochs):
        opt.zero_grad(); lossf(clf(Xtr), ytr).backward(); opt.step()
    with torch.no_grad():
        acc = (clf(Xte).argmax(1) == yte).float().mean().item()
    # chance = majority-class frequency in the test set
    _, counts = np.unique(y[idx[ntr:]], return_counts=True)
    chance = counts.max() / counts.sum()
    return acc, float(chance)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--task", default="vda4")
    ap.add_argument("--n-trials", type=int, default=4000)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    model = load_model(args.checkpoint, task=args.task, device=args.device)
    env = make_env(args.task)
    Z, labels, n_streams = collect(model, env, n_trials=args.n_trials, device=args.device)
    stream_names = (["Z_μ (actor)", "Z_q (critic)"] if n_streams == 2
                    else [f"stream{i}" for i in range(n_streams)])
    if n_streams < 2:
        print("[E7] WARNING: this model has a single shared stream (not crosstalk); the "
              "μ/q dissociation is only meaningful for --encoder crosstalk.")

    change = labels["change"] == 1
    # (label name, mask, values, family)
    targets = [
        ("change-present",  slice(None),  labels["change"],                 "evidence"),
        ("change-location", change,       labels["change_index"][change],   "evidence"),
        ("cue-value",       slice(None),  labels["value"],                   "value/context"),
        ("cue-reliability", slice(None),  (labels["prop"] * 4).round().astype(int), "value/context"),
        ("cued-location",   slice(None),  labels["cued_index"],              "value/context"),
    ]
    print(f"\nE7 pathway dissociation (task={args.task}, n={len(labels['change'])}):")
    hdr = f"  {'variable':<16} {'family':<14} " + " ".join(f"{s:>16}" for s in stream_names) + f" {'chance':>8}"
    print(hdr)
    for name, mask, yvals, family in targets:
        accs = []
        chance = None
        for s in range(n_streams):
            Xs = Z[s][mask] if not isinstance(mask, slice) else Z[s]
            acc, ch = linear_decode(Xs, yvals)
            accs.append(acc); chance = ch
        cells = " ".join(f"{a:>16.3f}" for a in accs)
        print(f"  {name:<16} {family:<14} {cells} {chance:>8.3f}")
    print("\nPredicted dissociation: 'evidence' rows decode higher from Z_μ; "
          "'value/context' rows decode higher from Z_q.")


if __name__ == "__main__":
    main()
