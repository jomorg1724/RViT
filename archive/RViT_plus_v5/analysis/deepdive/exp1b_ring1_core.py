"""
Core valid-vs-invalid psychometric/chronometric at a SPECIFIED ring proportion
(default 1.0 — fully reliable cue), companion to exp1's Panel A which is at ring
0.75. Produces a standalone ring=1.0 panel and an overlay comparing ring 0.75 vs
1.0 (the 0.75 curves are loaded from exp1_summary.json so they are not recomputed).

Usage:
  .venv/bin/python -m RViT_plus_v5.analysis.deepdive.exp1b_ring1_core \
      --ring 1.0 --n-trials 300 --device cpu
"""
from __future__ import annotations
import argparse, json, os, sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_v5.analysis.deepdive import dd_core as dd
from RViT_plus_v5.analysis.deepdive import exp1_psychometrics as E1

FIGS = os.path.join(_HERE, "figs"); TABS = os.path.join(_HERE, "tables")


def run_core(model, device, env_kwargs, args, ring):
    rows = {"valid": [], "invalid": []}
    for mag in args.mag_bins:
        for cond, mode in (("valid", "cued"), ("invalid", "uncued")):
            out = E1._rollout(model, device, env_kwargs, mag=mag, mode=mode, ring=ring,
                              n_trials=args.n_trials, change_time=args.change_time,
                              seed=args.seed + int(mag * 100) + (0 if cond == "valid" else 7))
            s = E1._summ(out); s["mag"] = float(mag); rows[cond].append(s)
        v, iv = rows["valid"][-1], rows["invalid"][-1]
        print(f"  ring={ring} |Δθ|={mag:5.1f}  VALID hit={v['hit_rate']:.3f} rt={v['median_rt']:.2f}"
              f"  | INVALID hit={iv['hit_rate']:.3f} rt={iv['median_rt']:.2f}")
    fits = {c: E1._logistic_fit([r["mag"] for r in rows[c]], [r["hit_rate"] for r in rows[c]])
            for c in ("valid", "invalid")}
    return rows, fits


def plot_core(rows, fits, ring, out, n):
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    cmap = {"valid": "tab:blue", "invalid": "tab:red"}
    for cond in ("valid", "invalid"):
        r = rows[cond]; x = [d["mag"] for d in r]
        ax[0].errorbar(x, [d["hit_rate"] for d in r], yerr=[d["hit_sem"] for d in r],
                       marker="o", color=cmap[cond], capsize=3, lw=2,
                       label=f"{cond} (x₅₀={fits[cond][0]:.1f}°)")
        ax[1].errorbar(x, [d["median_rt"] for d in r], yerr=[d["rt_sem"] for d in r],
                       marker="o", color=cmap[cond], capsize=3, lw=2, label=cond)
        xs = np.linspace(min(x), max(x), 200); x50, w, _ = fits[cond]
        if np.isfinite(x50):
            ax[0].plot(xs, 1/(1+np.exp(-(xs-x50)/w)), color=cmap[cond], ls="--", alpha=.6)
    ax[0].axhline(0.5, color="grey", ls=":", alpha=.5)
    ax[0].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="P(hit)", title="Psychometric", ylim=(-.02, 1.02))
    ax[1].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="median RT (frames post-change)", title="Chronometric")
    for a in ax: a.grid(alpha=.3); a.legend(fontsize=8)
    db = fits["invalid"][0] - fits["valid"][0]
    fig.suptitle(f"Core psychometric/chronometric · ring={ring} (fully reliable cue) · "
                 f"cueing benefit Δx₅₀={db:.1f}°  ·  n={n}/cell")
    fig.tight_layout(); fig.savefig(out, dpi=140, bbox_inches="tight"); plt.close(fig)
    print(f"[saved] {out}")


def plot_compare(rows10, rows075, out, n):
    """Overlay ring 0.75 vs 1.0 for valid and invalid."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    style = {("valid", 1.0): ("tab:blue", "-"), ("invalid", 1.0): ("tab:red", "-"),
             ("valid", 0.75): ("tab:cyan", "--"), ("invalid", 0.75): ("tab:orange", "--")}
    for rows, ring in ((rows10, 1.0), (rows075, 0.75)):
        for cond in ("valid", "invalid"):
            r = rows[cond]; x = [d["mag"] for d in r]; c, ls = style[(cond, ring)]
            ax[0].plot(x, [d["hit_rate"] for d in r], marker="o", color=c, ls=ls, lw=1.8,
                       label=f"{cond} ring {ring}")
            ax[1].plot(x, [d["median_rt"] for d in r], marker="o", color=c, ls=ls, lw=1.8, label=f"{cond} {ring}")
    ax[0].axhline(0.5, color="grey", ls=":", alpha=.5)
    ax[0].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="P(hit)", title="Psychometric: ring 1.0 vs 0.75", ylim=(-.02, 1.02))
    ax[1].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="median RT", title="Chronometric: ring 1.0 vs 0.75")
    for a in ax: a.grid(alpha=.3); a.legend(fontsize=7)
    fig.suptitle(f"Valid/invalid psychometric & chronometric — full (1.0) vs partial (0.75) cue reliability · n={n}/cell")
    fig.tight_layout(); fig.savefig(out, dpi=140, bbox_inches="tight"); plt.close(fig)
    print(f"[saved] {out}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=300)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--ring", type=float, default=1.0)
    ap.add_argument("--mag-bins", type=float, nargs="+",
                    default=[2, 4, 6, 8, 10, 12, 14, 17, 20, 25, 32, 44, 64])
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True); os.makedirs(TABS, exist_ok=True)
    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device)
    it = dd.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}  ring={args.ring}")

    rows, fits = run_core(model, device, env_kwargs, args, args.ring)
    tag = f"{args.ring:.2f}".replace(".", "p")
    plot_core(rows, fits, args.ring, os.path.join(FIGS, f"exp1A_core_ring{tag}.png"), args.n_trials)

    # comparison vs the ring-0.75 core saved by exp1 (if present)
    j = os.path.join(TABS, "exp1_summary.json")
    if abs(args.ring - 1.0) < 1e-6 and os.path.exists(j):
        s = json.load(open(j))
        if abs(float(s.get("ring", -1)) - 0.75) < 1e-6:
            rows075 = {"valid": s["core"]["valid"], "invalid": s["core"]["invalid"]}
            plot_compare(rows, rows075, os.path.join(FIGS, "exp1_core_compare_ring.png"), args.n_trials)

    out = {"ring": args.ring, "n_trials": args.n_trials, "change_time": args.change_time,
           "iter": it, "fits": {c: {"x50": fits[c][0], "width": fits[c][1]} for c in fits},
           "cueing_benefit_dx50": fits["invalid"][0] - fits["valid"][0],
           "core": rows}
    with open(os.path.join(TABS, f"exp1_core_ring{tag}.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"[saved] {TABS}/exp1_core_ring{tag}.json")
    print(f"[summary] ring={args.ring}: valid x50={fits['valid'][0]:.2f}°  invalid x50={fits['invalid'][0]:.2f}°  "
          f"benefit Δx50={out['cueing_benefit_dx50']:.2f}°")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
