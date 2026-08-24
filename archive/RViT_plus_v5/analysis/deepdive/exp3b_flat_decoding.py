"""
EXP 3b — Decode from the FULL (flattened, un-pooled) latents.

R3 (exp3) decoded from pooled features (token-mean `*_mean`, per-quadrant `*_quad`)
and the decoder CLS read-outs. But the model never mean-pools its tokens — the
encoder memory is 100 token-vectors and the actor/critic read it through a CLS
token that attends over all of them. Mean/quad pooling is an analysis choice that
can only *under*-estimate what is linearly present. Here we add the faithful,
un-pooled feature: the **entire flattened memory** (100×128 = 12,800 dims) for H1,
for H2, and both concatenated (25,600), and decode the same targets from them at
diagnostic frames, head-to-head with mean / quad / CLS.

To bound memory we record the full token tensors only at two probe frames:
  t = 3   (just after the cue+blank)  → cue colour / proportion
  t = 28  (final frame, max post-change evidence) → change location / magnitude /
          onset / present
High-dimensional (p ≫ n) linear decoders are validated by label-shuffled controls:
a shuffle that stays at chance proves the real-label accuracy is genuine
information, not overfitting (held-out CV folds, no leakage).

Usage:
  .venv/bin/python -m RViT_plus_v5.analysis.deepdive.exp3b_flat_decoding \
      --n-trials 3000 --device cpu
"""
from __future__ import annotations
import argparse, json, os, sys
from typing import Dict, List
import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_v5.analysis.deepdive import dd_core as dd
from RViT_plus_v5.analysis.deepdive.exp3_latent_decoding import COLOR2I, PROP2I

from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.metrics import balanced_accuracy_score, r2_score

FIGS = os.path.join(_HERE, "figs"); TABS = os.path.join(_HERE, "tables")
PROBES = [3, 15, 28]


def _clf(C, pca_k):
    steps = [StandardScaler()]
    if pca_k:
        steps.append(PCA(n_components=pca_k, random_state=0))
    steps.append(LogisticRegression(max_iter=3000, C=C))
    return make_pipeline(*steps)


def _reg(alpha, pca_k):
    steps = [StandardScaler()]
    if pca_k:
        steps.append(PCA(n_components=pca_k, random_state=0))
    steps.append(Ridge(alpha=alpha))
    return make_pipeline(*steps)


def cvc(X, y, C=1.0, pca_k=None, n_splits=5, seed=0):
    """Balanced-accuracy CV logistic decode (+ shuffle). pca_k>0 → within-fold PCA
    (leakage-free linear dim-reduction for high-dim flat features)."""
    y = np.asarray(y); cl, ct = np.unique(y, return_counts=True)
    if len(cl) < 2 or ct.min() < n_splits:
        return float("nan"), float("nan")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    yp = np.random.default_rng(seed).permutation(y); accs, sh = [], []
    for tr, te in skf.split(X, y):
        k = None if not pca_k else min(pca_k, X[tr].shape[0] - 1, X.shape[1])
        m = _clf(C, k).fit(X[tr], y[tr])
        accs.append(balanced_accuracy_score(y[te], m.predict(X[te])))
        m2 = _clf(C, k).fit(X[tr], yp[tr])
        sh.append(balanced_accuracy_score(yp[te], m2.predict(X[te])))
    return float(np.mean(accs)), float(np.mean(sh))


def cvr(X, y, alpha=10.0, pca_k=None, n_splits=5, seed=0):
    """R² CV ridge decode (+ shuffle). pca_k>0 → within-fold PCA."""
    y = np.asarray(y, float)
    if y.size < n_splits * 2 or np.ptp(y) == 0:
        return float("nan"), float("nan")
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    yp = np.random.default_rng(seed).permutation(y); r2s, sh = [], []
    for tr, te in kf.split(X):
        k = None if not pca_k else min(pca_k, X[tr].shape[0] - 1, X.shape[1])
        m = _reg(alpha, k).fit(X[tr], y[tr])
        r2s.append(r2_score(y[te], m.predict(X[te])))
        m2 = _reg(alpha, k).fit(X[tr], yp[tr])
        sh.append(r2_score(yp[te], m2.predict(X[te])))
    return float(np.mean(r2s)), float(np.mean(sh))


@torch.no_grad()
def collect_flat(model, envs, obs0, device, probes):
    """Forced-wait rollout recording the FULL H1/H2 token tensors at `probes`,
    plus the actor/critic CLS at those frames, plus per-trial labels."""
    B = len(envs); model.eval()
    states = model.init_states(B, device=device)
    N = model.n_tokens
    obs = list(obs0); T = envs[0].T
    store = {p: {"h1": None, "h2": None, "acls": None, "ccls": None} for p in probes}
    t = 0; done = np.zeros(B, dtype=bool)
    while t < T:
        x = dd._obs_to_tensor(obs, device)
        tokens = model.patch_embed(x)
        states, rstates = dd.memtok_forward_step(model.encoder, tokens, states)
        if t in probes:
            logits, a_cls = dd.actor_decode(model.actor_head, rstates)
            _, c_cls = dd.critic_decode(model.critic_head, rstates, 1)
            store[t]["h1"] = rstates[0].reshape(B, -1).cpu().numpy().astype(np.float32)
            store[t]["h2"] = rstates[1].reshape(B, -1).cpu().numpy().astype(np.float32)
            store[t]["acls"] = a_cls.cpu().numpy().astype(np.float32)
            store[t]["ccls"] = c_cls.cpu().numpy().astype(np.float32)
        for i in range(B):
            if done[i]:
                continue
            o, r, d, _ = envs[i].step(0); obs[i] = o
            if d:
                done[i] = True
        t += 1
    labels = {
        "cue_color": np.array([COLOR2I[c] for c in [e.cue_color for e in envs]]),
        "cue_proportion": np.array([PROP2I[round(float(e.proportion), 2)] for e in envs]),
        "change_true": np.array([int(e.change_true) for e in envs], bool),
        "change_index": np.array([int(getattr(e, "change_index", -1)) for e in envs]),
        "change_time": np.array([int(e.change_time) for e in envs]),
        "mag": np.array([abs(float(e.orientation_change)) for e in envs], np.float32),
    }
    return store, labels


def collect_chunked(model, device, env_kwargs, n_trials, seed, probes, chunk=400):
    rng = np.random.default_rng(seed)
    store_all = {p: {k: [] for k in ("h1", "h2", "acls", "ccls")} for p in probes}
    lab_all: Dict[str, List] = {}
    made = 0
    while made < n_trials:
        b = min(chunk, n_trials - made)
        envs, obs0 = [], []
        for _ in range(b):
            e = dd.bu.ChangeDetectionEnv(**env_kwargs); o = e.reset(); envs.append(e); obs0.append(o)
        store, labels = collect_flat(model, envs, obs0, device, probes)
        for p in probes:
            for k in store[p]:
                store_all[p][k].append(store[p][k])
        for k, v in labels.items():
            lab_all.setdefault(k, []).append(v)
        made += b
    for p in probes:
        for k in store_all[p]:
            store_all[p][k] = np.concatenate(store_all[p][k], 0)
    for k in lab_all:
        lab_all[k] = np.concatenate(lab_all[k], 0)
    return store_all, lab_all


def feats_at(store, t, N=100, d=128):
    """Return the dict of candidate feature matrices at probe frame t."""
    h1 = store[t]["h1"]; h2 = store[t]["h2"]              # (B, 12800)
    h1g = h1.reshape(h1.shape[0], N, d); h2g = h2.reshape(h2.shape[0], N, d)
    qi = dd.quadrant_token_indices()
    def quad(g):
        return np.concatenate([g[:, qi[q]].mean(1) for q in range(4)], 1)  # (B,512)
    return {
        "h1_mean": h1g.mean(1), "h2_mean": h2g.mean(1),
        "h1_quad": quad(h1g), "h2_quad": quad(h2g),
        "h1_flat": h1, "h2_flat": h2, "both_flat": np.concatenate([h1, h2], 1),
        "actor_cls": store[t]["acls"], "critic_press_cls": store[t]["ccls"],
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=3500)
    ap.add_argument("--flat-pca", type=int, default=250, help="within-fold PCA components for flat features (0=raw)")
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True); os.makedirs(TABS, exist_ok=True)
    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device); it = dd.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}")
    print(f"[collect] {args.n_trials} forced-wait trials, full tokens at frames {PROBES} …")
    store, lab = collect_chunked(model, device, env_kwargs, args.n_trials, args.seed, PROBES)
    chg = lab["change_true"]
    print(f"[collect] done. change-trials={int(chg.sum())}")

    feat_order = ["h1_mean", "h1_quad", "h1_flat", "h2_flat", "both_flat", "actor_cls", "critic_press_cls"]
    # (target, kind, probe_frame, label, mask)
    tasks = [
        ("cue_color", "clf", 3, lab["cue_color"], None),
        ("cue_proportion", "clf", 3, lab["cue_proportion"], None),
        ("change_location", "clf", 28, lab["change_index"], chg),
        ("change_present", "clf", 15, None, None),     # built below; t=15 has a mix
        ("change_magnitude", "reg", 28, lab["mag"], chg),
        ("change_onset", "reg", 28, lab["change_time"], chg),
    ]
    results = {"iter": it, "n_trials": args.n_trials, "flat_pca": args.flat_pca, "probes": PROBES, "tasks": {}}
    for name, kind, pf, y, mask in tasks:
        F = feats_at(store, pf)
        if name == "change_present":
            y = (pf >= lab["change_time"]).astype(int); mask = chg     # mix of changed/not at t=15
        results["tasks"][name] = {"kind": kind, "probe": pf, "feats": {}}
        line = []
        for fk in feat_order:
            X = F[fk]; yy = y if mask is None else y[mask]
            Xx = X if mask is None else X[mask]
            isflat = fk.endswith("_flat")
            pca_k = args.flat_pca if isflat else None     # full latent decoded via leakage-free PCA
            if kind == "clf":
                acc, sh = cvc(Xx, yy, C=1.0, pca_k=pca_k, seed=args.seed)
            else:
                acc, sh = cvr(Xx, yy, alpha=10.0, pca_k=pca_k, seed=args.seed)
            results["tasks"][name]["feats"][fk] = {"score": acc, "shuffle": sh, "dim": int(X.shape[1])}
            line.append(f"{fk}={acc:.2f}")
        print(f"  {name:17s}(t={pf}): " + " ".join(line))

    with open(f"{TABS}/exp3b_flat_decoding.json", "w") as f:
        json.dump(results, f, indent=2)

    # comparison bar chart
    import matplotlib.pyplot as plt
    names = [t[0] for t in tasks]
    fig, axes = plt.subplots(2, 3, figsize=(16, 8)); axes = axes.ravel()
    colors = {"h1_mean": "#9ecae1", "h1_quad": "#4292c6", "h1_flat": "#08519c",
              "h2_flat": "#6a51a3", "both_flat": "#000000", "actor_cls": "#41ab5d",
              "critic_press_cls": "#807dba"}
    for ax, name in zip(axes, names):
        r = results["tasks"][name]; kind = r["kind"]
        ks = feat_order; sc = [r["feats"][k]["score"] for k in ks]; sh = [r["feats"][k]["shuffle"] for k in ks]
        xpos = np.arange(len(ks))
        ax.bar(xpos, sc, color=[colors[k] for k in ks])
        ax.plot(xpos, sh, "kx", ms=7, label="shuffle")
        ax.set_xticks(xpos); ax.set_xticklabels([k.replace("_", "\n") for k in ks], fontsize=7)
        ax.set_title(f"{name} (t={r['probe']})"); ax.grid(alpha=.3, axis="y")
        ax.set_ylabel("balanced acc" if kind == "clf" else "R²")
        if kind == "clf":
            ax.set_ylim(0, 1.05)
        ax.legend(fontsize=7)
    fig.suptitle(f"Decoding from FULL flattened latents vs pooled vs CLS  ·  n={args.n_trials}  (× = shuffled-label control)")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp3b_flat_decoding.png", dpi=130, bbox_inches="tight"); plt.close(fig)
    print(f"[saved] {FIGS}/exp3b_flat_decoding.png + {TABS}/exp3b_flat_decoding.json")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
