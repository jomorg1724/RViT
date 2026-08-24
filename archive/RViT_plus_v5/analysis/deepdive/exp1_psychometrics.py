"""
EXP 1 — Comprehensive psychometrics & chronometrics for trained RViT+ v5.

Sweeps orientation-change magnitude |Δθ| and crosses it with every cue
valid/invalid combination, with the change placed at the cued S1 location for the
VALID condition and at a random uncued location for the INVALID condition.

Panels produced (all saved to figs/ + tables/):
  A. Core psychometric/chronometric: P(hit) and median RT vs |Δθ|, VALID vs
     INVALID (pooled over cue side & colour). Fitted logistic gives the 50%
     threshold and slope; the leftward threshold shift = the cueing benefit.
  B. Cue-side control: the same VALID/INVALID split done separately for cue-left
     (S1=top-left) and cue-right (S1=bottom-right) to check spatial symmetry.
  C. Validity (ring) × VALID/INVALID: psychometric threshold and the cueing
     benefit as functions of the *displayed* cue reliability ring ∈ {.25,.5,.75,1}.
  D. Value (colour) × |Δθ|: P(hit)/RT vs |Δθ| for blue/green/red cues (reward
     1/3/5) at the cued location — value-directed attention.
  E. Criterion / errors: premature-press rate vs |Δθ|, and the no-change
     correct-rejection rate (a separate change_true=0 sweep).

Usage:
  .venv/bin/python -m RViT_plus_v5.analysis.deepdive.exp1_psychometrics \
      --n-trials 400 --device cpu
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

from RViT_plus_v5.analysis import _behav_utils as bu
from RViT_plus_v5.analysis.deepdive import dd_core as dd

FIGS = os.path.join(_HERE, "figs")
TABS = os.path.join(_HERE, "tables")


def _binom_sem(p, n):
    return float(np.sqrt(max(p * (1 - p), 0.0) / n)) if n > 0 else 0.0


def _summ(out):
    hit = out["hit"]; n = int(hit.size)
    rt = out["rt"][~np.isnan(out["rt"])]
    return {
        "n": n,
        "hit_rate": float(hit.mean()) if n else float("nan"),
        "hit_sem": _binom_sem(float(hit.mean()) if n else 0.0, n),
        "median_rt": float(np.median(rt)) if rt.size else float("nan"),
        "mean_rt": float(rt.mean()) if rt.size else float("nan"),
        "rt_sem": float(1.2533 * rt.std() / np.sqrt(rt.size)) if rt.size > 1 else 0.0,
        "premature_rate": float(out["premature"].mean()) if n else float("nan"),
        "n_hits": int(rt.size),
    }


def _rollout(model, device, env_kwargs, *, mag, mode, ring, color=None,
             change_true=1, n_trials=400, change_time=15, seed=0):
    rng = np.random.default_rng(seed)
    spec = bu.ForcedTrialSpec(
        proportion=ring, change_true=change_true, change_time=change_time,
        change_index_mode=mode, orientation_mag=(None if mag is None else float(mag)),
        cue_color=color,
    )
    envs, obs0 = bu.build_env_batch(
        spec, n_trials, rng, env_kwargs=env_kwargs,
        randomize_cue_position=True, randomize_color=(color is None))
    return bu.batched_behavior_rollout(model, envs, obs0, device)


def _logistic_fit(x, y):
    """Fit p = 1/(1+exp(-(x-x50)/w)); return (x50, w, slope_at_mid). Robust to
    saturated data via scipy; falls back to NaN on failure."""
    from scipy.optimize import curve_fit
    x = np.asarray(x, float); y = np.asarray(y, float)

    def f(xx, x50, w):
        return 1.0 / (1.0 + np.exp(-(xx - x50) / np.clip(w, 1e-3, None)))
    try:
        p0 = [float(np.interp(0.5, y, x)) if np.ptp(y) > 0 else float(x.mean()), 5.0]
        popt, _ = curve_fit(f, x, y, p0=p0, maxfev=20000,
                            bounds=([x.min() - 20, 0.1], [x.max() + 20, 60]))
        x50, w = float(popt[0]), float(popt[1])
        return x50, w, 1.0 / (4.0 * w)
    except Exception:
        return float("nan"), float("nan"), float("nan")


# ── experiments ───────────────────────────────────────────────────────────────
def exp_core(model, device, env_kwargs, args):
    rows = {"valid": [], "invalid": []}
    for mag in args.mag_bins:
        for cond, mode in (("valid", "cued"), ("invalid", "uncued")):
            out = _rollout(model, device, env_kwargs, mag=mag, mode=mode,
                           ring=args.ring, n_trials=args.n_trials,
                           change_time=args.change_time,
                           seed=args.seed + int(mag * 100) + (0 if cond == "valid" else 7))
            s = _summ(out); s["mag"] = float(mag); s["condition"] = cond
            rows[cond].append(s)
        v, iv = rows["valid"][-1], rows["invalid"][-1]
        print(f"  |Δθ|={mag:5.1f}  VALID hit={v['hit_rate']:.3f} rt={v['median_rt']:.2f}"
              f"  | INVALID hit={iv['hit_rate']:.3f} rt={iv['median_rt']:.2f}")
    fits = {}
    for cond in ("valid", "invalid"):
        xs = [r["mag"] for r in rows[cond]]; ys = [r["hit_rate"] for r in rows[cond]]
        fits[cond] = _logistic_fit(xs, ys)
    return rows, fits


def exp_side(model, device, env_kwargs, args):
    out = {}
    cmags = args.mag_bins[::2]            # coarse grid for the control panels
    for side in ("left", "right"):
        cued = bu.CUED_QUADRANT[side]
        uncued = [q for q in range(4) if q != cued]
        for cond, idx in (("valid", cued), ("invalid", uncued[0])):
            key = f"{side}:{cond}"; out[key] = []
            for mag in cmags:
                rng = np.random.default_rng(args.seed + hash(key) % 9973 + int(mag * 10))
                spec = bu.ForcedTrialSpec(
                    cue_position=side, proportion=args.ring, change_true=1,
                    change_time=args.change_time, change_index_mode=int(idx),
                    orientation_mag=float(mag))
                envs, obs0 = bu.build_env_batch(spec, args.n_trials, rng,
                    env_kwargs=env_kwargs, randomize_cue_position=False, randomize_color=True)
                s = _summ(bu.batched_behavior_rollout(model, envs, obs0, device))
                s["mag"] = float(mag); out[key].append(s)
    return out


def exp_ring(model, device, env_kwargs, args):
    rows = []
    cmags = args.mag_bins[::2]            # coarse grid; only the threshold fit is needed
    for ring in dd.PROPORTIONS:
        for cond, mode in (("valid", "cued"), ("invalid", "uncued")):
            xs, ys = [], []
            for mag in cmags:
                out = _rollout(model, device, env_kwargs, mag=mag, mode=mode, ring=ring,
                               n_trials=args.n_trials, change_time=args.change_time,
                               seed=args.seed + int(ring * 1000) + int(mag * 7))
                s = _summ(out); xs.append(float(mag)); ys.append(s["hit_rate"])
            x50, w, slope = _logistic_fit(xs, ys)
            rows.append({"ring": ring, "condition": cond, "thresh50": x50,
                         "width": w, "slope": slope})
        print(f"  ring={ring:.2f}  valid x50={rows[-2]['thresh50']:.2f} "
              f"invalid x50={rows[-1]['thresh50']:.2f}  benefit(Δx50)={rows[-1]['thresh50']-rows[-2]['thresh50']:.2f}")
    return rows


def exp_value(model, device, env_kwargs, args):
    rows = {c: [] for c in dd.COLORS}
    for color in dd.COLORS:
        for mag in args.mag_bins:
            out = _rollout(model, device, env_kwargs, mag=mag, mode="cued",
                           ring=args.ring, color=color, n_trials=args.n_trials,
                           change_time=args.change_time,
                           seed=args.seed + hash(color) % 7919 + int(mag * 3))
            s = _summ(out); s["mag"] = float(mag); s["color"] = color
            s["value"] = bu.COLOR_VALUE[color]; rows[color].append(s)
    for color in dd.COLORS:
        print(f"  {color:5s}(v={bu.COLOR_VALUE[color]}) "
              + " ".join(f"{r['hit_rate']:.2f}" for r in rows[color]))
    return rows


def exp_crit(model, device, env_kwargs, args):
    """Premature rate vs |Δθ| (valid) and a no-change correct-rejection sweep."""
    prem = []
    for mag in args.mag_bins:
        out = _rollout(model, device, env_kwargs, mag=mag, mode="cued", ring=args.ring,
                       n_trials=args.n_trials, change_time=args.change_time,
                       seed=args.seed + 555 + int(mag * 9))
        prem.append({"mag": float(mag), "premature_rate": float(out["premature"].mean())})
    # no-change trials: correct rejection = never press (reward>0 at T)
    out0 = _rollout(model, device, env_kwargs, mag=None, mode=None, ring=args.ring,
                    change_true=0, n_trials=args.n_trials * 2, change_time=args.change_time,
                    seed=args.seed + 999)
    cr = float((~out0["pressed"]).mean())
    fa = float(out0["pressed"].mean())
    print(f"  no-change: correct-rejection={cr:.3f}  false-alarm(press)={fa:.3f}")
    return prem, {"correct_rejection": cr, "false_alarm": fa,
                  "n": int(out0["hit"].size)}


# ── plotting ──────────────────────────────────────────────────────────────────
def plot_all(core, fits, side, ring, value, prem, crit, args):
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})

    # Panel A
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    cmap = {"valid": "tab:blue", "invalid": "tab:red"}
    for cond in ("valid", "invalid"):
        r = core[cond]; x = [d["mag"] for d in r]
        ax[0].errorbar(x, [d["hit_rate"] for d in r], yerr=[d["hit_sem"] for d in r],
                       marker="o", color=cmap[cond], capsize=3, lw=2,
                       label=f"{cond} (x₅₀={fits[cond][0]:.1f}°)")
        ax[1].errorbar(x, [d["median_rt"] for d in r], yerr=[d["rt_sem"] for d in r],
                       marker="o", color=cmap[cond], capsize=3, lw=2, label=cond)
        xs = np.linspace(min(x), max(x), 200)
        x50, w, _ = fits[cond]
        if np.isfinite(x50):
            ax[0].plot(xs, 1 / (1 + np.exp(-(xs - x50) / w)), color=cmap[cond], ls="--", alpha=0.6)
    ax[0].axhline(0.5, color="grey", ls=":", alpha=0.5)
    ax[0].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="P(hit)", title="Psychometric", ylim=(-.02, 1.02))
    ax[1].set(xlabel=r"$|\Delta\theta|$ (deg)", ylabel="median RT (frames post-change)", title="Chronometric")
    for a in ax:
        a.grid(alpha=.3); a.legend(fontsize=8)
    db = fits["invalid"][0] - fits["valid"][0]
    fig.suptitle(f"Core psychometric/chronometric · ring={args.ring} · change@t={args.change_time} · "
                 f"cueing benefit Δx₅₀={db:.1f}°  ·  n={args.n_trials}/cell")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp1A_core.png", dpi=140, bbox_inches="tight"); plt.close(fig)

    # Panel B — cue side
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    sty = {"left:valid": ("tab:blue", "-"), "left:invalid": ("tab:red", "-"),
           "right:valid": ("tab:cyan", "--"), "right:invalid": ("tab:orange", "--")}
    for key, r in side.items():
        x = [d["mag"] for d in r]; c, ls = sty[key]
        ax[0].plot(x, [d["hit_rate"] for d in r], marker="o", color=c, ls=ls, label=key)
        ax[1].plot(x, [d["median_rt"] for d in r], marker="o", color=c, ls=ls, label=key)
    ax[0].set(xlabel=r"$|\Delta\theta|$", ylabel="P(hit)", title="P(hit) by cue side", ylim=(-.02, 1.02))
    ax[1].set(xlabel=r"$|\Delta\theta|$", ylabel="median RT", title="RT by cue side")
    for a in ax:
        a.grid(alpha=.3); a.legend(fontsize=7)
    fig.suptitle("Cue-side control (spatial symmetry of the cueing effect)")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp1B_side.png", dpi=140, bbox_inches="tight"); plt.close(fig)

    # Panel C — ring scaling of threshold & benefit
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    rings = dd.PROPORTIONS
    tv = {c: [next(r["thresh50"] for r in ring if r["ring"] == rr and r["condition"] == c) for rr in rings]
          for c in ("valid", "invalid")}
    ax[0].plot(rings, tv["valid"], "o-", color="tab:blue", label="valid")
    ax[0].plot(rings, tv["invalid"], "o-", color="tab:red", label="invalid")
    ax[0].set(xlabel="displayed cue reliability (ring)", ylabel="50% threshold |Δθ| (deg)",
              title="Threshold vs displayed validity")
    benefit = [tv["invalid"][i] - tv["valid"][i] for i in range(len(rings))]
    ax[1].plot(rings, benefit, "s-", color="tab:purple")
    ax[1].axhline(0, color="grey", ls=":")
    ax[1].set(xlabel="displayed cue reliability (ring)", ylabel="cueing benefit Δx₅₀ (invalid−valid)",
              title="Cueing benefit vs displayed validity")
    for a in ax:
        a.grid(alpha=.3)
    ax[0].legend(fontsize=8)
    fig.suptitle("Does the cueing benefit scale with displayed cue reliability?")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp1C_ring.png", dpi=140, bbox_inches="tight"); plt.close(fig)

    # Panel D — value
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    vc = {"blue": "tab:blue", "green": "tab:green", "red": "tab:red"}
    for color in dd.COLORS:
        r = value[color]; x = [d["mag"] for d in r]
        ax[0].plot(x, [d["hit_rate"] for d in r], marker="o", color=vc[color],
                   label=f"{color} (v={bu.COLOR_VALUE[color]})")
        ax[1].plot(x, [d["median_rt"] for d in r], marker="o", color=vc[color], label=color)
    ax[0].set(xlabel=r"$|\Delta\theta|$", ylabel="P(hit), cued", title="P(hit) by cue value", ylim=(-.02, 1.02))
    ax[1].set(xlabel=r"$|\Delta\theta|$", ylabel="median RT", title="RT by cue value")
    for a in ax:
        a.grid(alpha=.3); a.legend(fontsize=8)
    fig.suptitle("Value-directed attention: detection vs cue value (reward magnitude)")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp1D_value.png", dpi=140, bbox_inches="tight"); plt.close(fig)

    # Panel E — criterion/errors
    fig, ax = plt.subplots(1, 1, figsize=(6, 4.2))
    ax.plot([d["mag"] for d in prem], [d["premature_rate"] for d in prem], "o-", color="tab:brown",
            label="premature-press rate (valid)")
    ax.axhline(crit["false_alarm"], color="tab:gray", ls="--",
               label=f"no-change false-alarm = {crit['false_alarm']:.3f}")
    ax.set(xlabel=r"$|\Delta\theta|$", ylabel="error rate", title="Criterion / error rates", ylim=(-.02, None))
    ax.grid(alpha=.3); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp1E_criterion.png", dpi=140, bbox_inches="tight"); plt.close(fig)
    print(f"[saved] 5 figures to {FIGS}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=400)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--ring", type=float, default=0.75)
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
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}")

    print("\n[A] core valid/invalid psychometric"); core, fits = exp_core(model, device, env_kwargs, args)
    print("\n[B] cue-side control"); side = exp_side(model, device, env_kwargs, args)
    print("\n[C] ring × validity"); ring = exp_ring(model, device, env_kwargs, args)
    print("\n[D] value × magnitude"); value = exp_value(model, device, env_kwargs, args)
    print("\n[E] criterion/errors"); prem, crit = exp_crit(model, device, env_kwargs, args)

    summary = {
        "iter": it, "n_trials": args.n_trials, "ring": args.ring,
        "change_time": args.change_time, "mag_bins": args.mag_bins,
        "fits": {k: {"x50": v[0], "width": v[1], "slope": v[2]} for k, v in fits.items()},
        "cueing_benefit_dx50": fits["invalid"][0] - fits["valid"][0],
        "ring_rows": ring, "criterion": crit,
        "core": {k: core[k] for k in core},
        "value": {c: value[c] for c in value},
    }
    with open(f"{TABS}/exp1_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[saved] {TABS}/exp1_summary.json")
    plot_all(core, fits, side, ring, value, prem, crit, args)
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
