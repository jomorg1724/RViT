"""
EXP 3 — What is linearly decodable from the v5_part2 recurrent latents?

Port of ``RViT_plus_v5/analysis/deepdive/exp3_latent_decoding.py`` adapted to the
v5_part2 architecture. We roll out a large bank of fully-randomised trials (cue
side/colour/proportion, change time/location/magnitude/presence all random),
forcing the model to WAIT so every trial runs the full episode, and record the
recurrent latents at every timestep via ``dd_core.record_rollout(_chunked)``:

    h1_mean, h2_mean   token-mean of each encoder LSTM memory state   (d=d_mem)
    h1_quad, h2_quad   per-quadrant pooled memory                     (4×d_mem)
    actor_cls          actor 1D-conv-trunk penultimate feature        (conv_ch·L')
    critic_press_cls   critic(press) 1D-conv-trunk penultimate feat   (conv_ch·L')

We then train cross-validated LINEAR decoders (5-fold; logistic for categories,
ridge for continua) for each task variable, from each latent, AT EACH TIMESTEP —
giving a temporal-decoding curve (when does the model represent each variable?)
and a summary table (peak decodability per variable per latent vs a shuffled-
label control).

** v5_part2 adaptation note. ** The v5 decoders had a CLS-token attention readout
(``actor_cls`` / ``critic_press_cls`` were genuine CLS latents). The v5_part2
decoders are tiny 1D-conv heads with NO CLS and NO attention, so those two
recorded latents are instead the FLATTENED conv-trunk penultimate features
(``head.trunk(x).flatten(1)``, see dd_core). Because the conv head pools over the
token (spatial) axis with stride, "where is the change held" is genuinely open —
so for change_location we explicitly compare the token-mean latents (h1_mean /
h2_mean) against the per-quadrant-pooled latents (h1_quad / h2_quad): if change
location is held spatially, per-quadrant pooling should decode it far better than
the spatially-collapsed token mean.

Targets:
  cue_color        3-way   (available from t>=2, after the cue)
  cue_proportion   4-way + ordinal regression (displayed reliability)
  change_location  4-way   (which quadrant changed; change trials, post-change)
  change_magnitude regression on |dtheta| (post-change)
  change_present   binary  has the change happened yet at time t (change trials)
  change_onset     regression on change_time (post-change)
  abs_time         regression on t (clock control)

Usage:
  .venv/bin/python -m RViT_plus_recur.analysis.deepdive.exp3_latent_decoding \
      --n-trials 2400 --device cpu
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_recur.analysis import _behav_utils as bu  # noqa: E402,F401
from RViT_plus_recur.analysis.deepdive import dd_core as dd  # noqa: E402

from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import balanced_accuracy_score, r2_score

FIGS = os.path.join(_HERE, "figs")
TABS = os.path.join(_HERE, "tables")
COLOR2I = {"red": 0, "green": 1, "blue": 2}
PROP2I = {1.0: 0, 0.75: 1, 0.5: 2, 0.25: 3}


def collect(model, device, env_kwargs, n_trials, seed):
    """Roll out n_trials fully-random forced-wait trials, recording latents at all t."""
    envs, obs0 = [], []
    for _ in range(n_trials):
        e = dd.bu.ChangeDetectionEnv(**env_kwargs)
        o = e.reset()                         # reset randomizes side/colour/prop/change
        envs.append(e); obs0.append(o)
    rec = dd.record_rollout_chunked(model, envs, obs0, device, chunk=400, policy="wait",
                                    record_latents=True, record_quad=True)
    return rec


def cv_classify(X, y, n_splits=5, seed=0):
    """Balanced-accuracy under stratified CV with a logistic decoder (+ shuffle)."""
    y = np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    if len(classes) < 2 or counts.min() < n_splits:
        return float("nan"), float("nan")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    accs, sh = [], []
    yp = np.random.default_rng(seed).permutation(y)
    for tr, te in skf.split(X, y):
        sc = StandardScaler().fit(X[tr])
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(sc.transform(X[tr]), y[tr])
        accs.append(balanced_accuracy_score(y[te], clf.predict(sc.transform(X[te]))))
        clf2 = LogisticRegression(max_iter=2000, C=1.0)
        clf2.fit(sc.transform(X[tr]), yp[tr])
        sh.append(balanced_accuracy_score(yp[te], clf2.predict(sc.transform(X[te]))))
    return float(np.mean(accs)), float(np.mean(sh))


def cv_regress(X, y, n_splits=5, seed=0):
    """R^2 under CV with a ridge decoder (+ shuffle control)."""
    y = np.asarray(y, float)
    if y.size < n_splits * 2 or np.ptp(y) == 0:
        return float("nan"), float("nan")
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    r2s, sh = [], []
    yp = np.random.default_rng(seed).permutation(y)
    for tr, te in kf.split(X):
        sc = StandardScaler().fit(X[tr])
        rg = Ridge(alpha=10.0).fit(sc.transform(X[tr]), y[tr])
        r2s.append(r2_score(y[te], rg.predict(sc.transform(X[te]))))
        rg2 = Ridge(alpha=10.0).fit(sc.transform(X[tr]), yp[tr])
        sh.append(r2_score(yp[te], rg2.predict(sc.transform(X[te]))))
    return float(np.mean(r2s)), float(np.mean(sh))


def feat(rec, name, t, mask=None):
    """Latent feature matrix (n,d) at timestep t for the requested latent."""
    a = rec[name][t]                      # (B, ...)
    a = a.reshape(a.shape[0], -1)
    return a if mask is None else a[mask]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=2400)
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True); os.makedirs(TABS, exist_ok=True)
    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device)
    it = dd.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}")

    print(f"[collect] {args.n_trials} forced-wait trials ...")
    rec = collect(model, device, env_kwargs, args.n_trials, args.seed)
    T = rec["n_steps"]; B = rec["hit"].size
    print(f"[collect] done: T={T}, B={B}, change-trials={int(rec['change_true'].sum())}")

    # labels
    color = np.array([COLOR2I[c] for c in rec["cue_color"]])
    prop = np.array([PROP2I[round(float(p), 2)] for p in rec["proportion"]])
    prop_val = rec["proportion"].astype(float)
    chg_true = rec["change_true"].astype(bool)
    chg_idx = rec["change_index"]            # -1 for no-change
    chg_time = rec["change_time"]
    mag = np.abs(rec["orientation_change"])

    latents = ["z_sal_mean", "z_td_mean", "h1_mean", "h2_mean",
               "z_sal_quad", "z_td_quad", "h1_quad", "h2_quad",
               "actor_cls", "critic_press_cls"]

    # temporal decoding curves
    targets = {
        "cue_color":       ("clf", color, None),
        "cue_proportion":  ("clf", prop, None),
        "cue_prop_reg":    ("reg", prop_val, None),
        "change_location": ("clf", chg_idx, chg_true),       # change trials only
        "change_magnitude":("reg", mag, chg_true),
        "change_onset":    ("reg", chg_time, chg_true),
        "abs_time":        ("reg", None, None),              # special; handled below
    }

    curves: Dict[str, Dict[str, List[float]]] = {}
    shuffles: Dict[str, Dict[str, List[float]]] = {}
    for tname, (kind, y, mask) in targets.items():
        if tname == "abs_time":
            continue
        curves[tname] = {}; shuffles[tname] = {}
        for lat in latents:
            cs, ss = [], []
            for t in range(T):
                X = feat(rec, lat, t, mask)
                yy = y[mask] if mask is not None else y
                if kind == "clf":
                    sc, shf = cv_classify(X, yy, seed=args.seed)
                else:
                    sc, shf = cv_regress(X, yy, seed=args.seed)
                cs.append(sc); ss.append(shf)
            curves[tname][lat] = cs; shuffles[tname][lat] = ss
        best = max((np.nanmax(curves[tname][l]) for l in latents))
        print(f"  {tname:18s} peak={best:.3f}")

    # abs_time: decode the absolute timestep from h2_mean pooled over all (trial,t)
    Xs, ys = [], []
    for t in range(T):
        Xs.append(rec["h2_mean"][t]); ys.append(np.full(B, t))
    Xall = np.concatenate(Xs, 0); yall = np.concatenate(ys, 0)
    abs_r2, abs_sh = cv_regress(Xall, yall, seed=args.seed)
    print(f"  abs_time (h2_mean pooled) R^2={abs_r2:.3f} (shuffle {abs_sh:.3f})")

    # change_present temporal: binary 'has change occurred' at each t (change trials)
    cp_lats = ["z_sal_mean", "z_td_mean", "h1_mean", "h2_mean", "actor_cls", "critic_press_cls"]
    cp_curve = {lat: [] for lat in cp_lats}
    cp_shuf = {lat: [] for lat in cp_lats}
    for lat in cp_curve:
        for t in range(T):
            m = chg_true
            occurred = (t >= chg_time)[m].astype(int)
            X = feat(rec, lat, t, m)
            sc, shf = cv_classify(X, occurred, seed=args.seed) if len(np.unique(occurred)) > 1 else (float("nan"), float("nan"))
            cp_curve[lat].append(sc); cp_shuf[lat].append(shf)

    # ── plots ────────────────────────────────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    plot_targets = ["cue_color", "cue_proportion", "change_location",
                    "change_magnitude", "change_onset"]
    latcol = {"z_sal_mean": "tab:blue", "z_td_mean": "tab:red",
              "h1_mean": "tab:cyan", "h2_mean": "tab:orange",
              "z_sal_quad": "navy", "z_td_quad": "darkred",
              "h1_quad": "teal", "h2_quad": "chocolate",
              "actor_cls": "tab:green", "critic_press_cls": "tab:purple"}
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.ravel()
    for ax, tname in zip(axes, plot_targets):
        kind = targets[tname][0]
        for lat in latents:
            ax.plot(range(T), curves[tname][lat], color=latcol[lat], lw=1.7, label=lat)
        if kind == "clf":
            yv = targets[tname][1]
            mv = targets[tname][2]
            nclass = len(np.unique(yv[mv] if mv is not None else yv))
            ax.axhline(1.0 / nclass, color="grey", ls=":", label="chance")
        else:
            ax.axhline(0.0, color="grey", ls=":")
        ax.axvline(1, color="k", ls=":", alpha=.4); ax.axvline(3, color="grey", ls=":", alpha=.3)
        ax.set_title(tname); ax.set_xlabel("timestep t")
        ax.set_ylabel("balanced acc" if kind == "clf" else "R^2"); ax.grid(alpha=.3)
    # last panel: change_present
    ax = axes[5]
    for lat in cp_curve:
        ax.plot(range(T), cp_curve[lat], color=latcol[lat], lw=1.7, label=lat)
    ax.axhline(0.5, color="grey", ls=":"); ax.set_title("change_present (has change occurred)")
    ax.set_xlabel("t"); ax.set_ylabel("balanced acc"); ax.grid(alpha=.3)
    axes[0].legend(fontsize=7, ncol=2)
    fig.suptitle(f"Temporal linear decoding of task variables from v11 dual-stream latents  ·  n={B} trials  ·  iter={it}", y=1.0)
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp3_temporal_decoding.png", dpi=130, bbox_inches="tight"); plt.close(fig)

    # ── change_location: token-mean vs per-quadrant-pooled comparison ─────────
    # v5_part2-specific question: the conv decoder pools the spatial token axis,
    # so where is the changed quadrant held? Compare spatially-collapsed (mean)
    # vs spatially-resolved (per-quadrant pooled) recurrent latents.
    cl_sources = ["z_sal_mean", "z_td_mean", "h1_mean", "h2_mean",
                  "z_sal_quad", "z_td_quad", "h1_quad", "h2_quad",
                  "actor_cls", "critic_press_cls"]
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    for lat in cl_sources:
        ax2.plot(range(T), curves["change_location"][lat], color=latcol[lat], lw=1.9, label=lat)
    nclass_cl = len(np.unique(chg_idx[chg_true]))
    ax2.axhline(1.0 / nclass_cl, color="grey", ls=":", label=f"chance (1/{nclass_cl})")
    ax2.axvline(1, color="k", ls=":", alpha=.4)
    ax2.set_title("change_location decodability: token-mean vs per-quadrant-pooled latents")
    ax2.set_xlabel("timestep t"); ax2.set_ylabel("balanced acc (4-way quadrant)")
    ax2.legend(fontsize=8); ax2.grid(alpha=.3)
    fig2.tight_layout(); fig2.savefig(f"{FIGS}/exp3_change_location_sources.png", dpi=130, bbox_inches="tight"); plt.close(fig2)

    # ── summary JSON ──────────────────────────────────────────────────────────
    summary = {"iter": it, "n_trials": B, "T": T,
               "change_trials": int(chg_true.sum()),
               "abs_time_r2": abs_r2, "abs_time_shuffle": abs_sh,
               "peaks": {}, "change_present": cp_curve, "change_present_shuffle": cp_shuf,
               "curves": {k: {l: curves[k][l] for l in latents} for k in curves},
               "shuffles": {k: {l: shuffles[k][l] for l in latents} for k in curves}}
    for tname in plot_targets:
        peaks = {lat: float(np.nanmax(curves[tname][lat])) for lat in latents}
        bestlat = max(peaks, key=lambda k: (peaks[k] if np.isfinite(peaks[k]) else -9))
        sh = float(np.nanmax(shuffles[tname][bestlat]))
        summary["peaks"][tname] = {"best_latent": bestlat, "peak": peaks[bestlat],
                                   "shuffle": sh, "per_latent": peaks}
    with open(f"{TABS}/exp3_decoding.json", "w") as f:
        json.dump(summary, f, indent=2)

    # ── human-readable CSV/markdown summary table ─────────────────────────────
    cp_peak = {lat: float(np.nanmax(cp_curve[lat])) for lat in cp_lats}
    cp_best = max(cp_peak, key=lambda k: (cp_peak[k] if np.isfinite(cp_peak[k]) else -9))
    rows = []
    rows.append(("variable", "kind", "best_latent", "peak", "shuffle", "delta"))
    for tname in plot_targets:
        p = summary["peaks"][tname]
        kind = "acc" if targets[tname][0] == "clf" else "R2"
        rows.append((tname, kind, p["best_latent"], f"{p['peak']:.3f}",
                     f"{p['shuffle']:.3f}", f"{p['peak'] - p['shuffle']:+.3f}"))
    rows.append(("change_present", "acc", cp_best, f"{cp_peak[cp_best]:.3f}",
                 f"{float(np.nanmax(cp_shuf[cp_best])):.3f}",
                 f"{cp_peak[cp_best] - float(np.nanmax(cp_shuf[cp_best])):+.3f}"))
    rows.append(("abs_time", "R2", "h2_mean(pooled)", f"{abs_r2:.3f}",
                 f"{abs_sh:.3f}", f"{abs_r2 - abs_sh:+.3f}"))
    with open(f"{TABS}/exp3_summary.csv", "w") as f:
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")

    # per-latent change_location peaks (the token-mean vs per-quad comparison)
    cl_rows = [("source", "peak_acc", "shuffle")]
    for lat in cl_sources:
        cl_rows.append((lat,
                        f"{float(np.nanmax(curves['change_location'][lat])):.3f}",
                        f"{float(np.nanmax(shuffles['change_location'][lat])):.3f}"))
    with open(f"{TABS}/exp3_change_location_by_source.csv", "w") as f:
        for r in cl_rows:
            f.write(",".join(str(x) for x in r) + "\n")

    print(f"[saved] {TABS}/exp3_decoding.json")
    print(f"[saved] {TABS}/exp3_summary.csv")
    print(f"[saved] {TABS}/exp3_change_location_by_source.csv")
    print(f"[saved] {FIGS}/exp3_temporal_decoding.png")
    print(f"[saved] {FIGS}/exp3_change_location_sources.png")
    print("[change_location by source]")
    for r in cl_rows[1:]:
        print(f"    {r[0]:18s} peak={r[1]} (shuffle {r[2]})")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
