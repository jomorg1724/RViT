"""Render the per-model atlas figures from family_atlas/*.npz (NO torch / model loading).
Per model: (1) attention-map atlas — input frames + a 2x2 attention heatmap (with the numeric
score in each cell) at every frame, for [cue100@S1, no change] and [cue100@S1, visible change
@S1], with image vs memory token streams shown separately for the cross-attention variants;
(2) a behaviour panel — psychometric (cued vs uncued by validity, logistic fits + thresholds)
and chronometric (RT vs delta). Writes PDFs into reports/thesis/figures/atlas/."""
import os, glob, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.titlesize": 8,
                     "figure.dpi": 150, "savefig.bbox": "tight"})

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "analysis", "deepdive_out", "family_atlas")
FIG = os.path.join(HERE, "..", "reports", "thesis", "figures", "atlas")
os.makedirs(FIG, exist_ok=True)
T = 7
TITLES = {"standard": "Multiplicative (paper-faithful)", "two_lstm": "Two stacked xLSTMs",
          "crossattn": "Cross-attention (image+memory)", "dualmem": "Dual-memory",
          "dualhead": "Dual-head (sensory+feedback)", "affine": "Affine modulation",
          "hyper": "Fast-weight (hypernetwork)", "hypercb": "Fast-weight + codebook"}
SRCLBL = {"image": "image keys", "memory": "memory keys", "sensory": "sensory head",
          "feedback": "feedback head", "mem_H1": "memory $H_1$", "mem_H2": "memory $H_2$"}
STATUS = {"affine": "always-wait collapse", "hyper": "always-press collapse (iter 8999, incomplete)",
          "hypercb": "iter 999 — essentially untrained"}
COLW = ["$t_0$", "$t_1$\n(cue)", "$t_2$", "$t_3$", "$t_4$", "$t_5$\n(change)", "$t_6$"]


def gray(frame):
    f = frame.astype(float)
    if f.ndim == 3: f = f.mean(-1)
    lo, hi = f.min(), f.max()
    return (f - lo) / (hi - lo + 1e-9)


def attention_atlas(d):
    name = str(d["name"]); amaps = d["amaps"].item(); frames = d["frames"].item()
    sources = list(amaps["change"].keys())                 # e.g. ['image'] or ['image','memory']
    nrows = 1 + 2 * len(sources)                           # frames + (cond x source)
    fig, ax = plt.subplots(nrows, T, figsize=(1.15 * T, 1.15 * nrows + 0.4),
                           gridspec_kw=dict(wspace=0.08, hspace=0.18))
    if nrows == 1: ax = ax[None, :]
    # row 0 — input frames (change condition; S1 = top-left)
    for t in range(T):
        a = ax[0, t]; a.imshow(gray(frames["change"][t]), cmap="gray", vmin=0, vmax=1)
        a.set_xticks([]); a.set_yticks([])
        a.set_title(COLW[t], fontsize=7)
        if t in (1, 5):
            for s in a.spines.values(): s.set_color("crimson" if t == 5 else "steelblue"); s.set_linewidth(1.6)
    ax[0, 0].set_ylabel("input\n(S1=TL)", fontsize=7, rotation=0, ha="right", va="center")
    # attention rows
    r = 1
    for cond in ("nochange", "change"):
        for src in sources:
            maps = amaps[cond][src]                         # (T,4)
            vmax = max(maps.max(), 1e-6)
            for t in range(T):
                a = ax[r, t]; m = maps[t].reshape(2, 2)
                a.imshow(m, cmap="magma", vmin=0, vmax=vmax)
                a.set_xticks([]); a.set_yticks([])
                for (i, j), val in np.ndenumerate(m):
                    a.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6,
                           color="white" if val < 0.6 * vmax else "black")
                a.add_patch(Rectangle((-.5, -.5), 1, 1, fill=False, ec="cyan", lw=1.1))  # S1=TL
            lab = ("no change" if cond == "nochange" else "change@S1") + "\n" + SRCLBL.get(src, src)
            ax[r, 0].set_ylabel(lab, fontsize=6.5, rotation=0, ha="right", va="center")
            r += 1
    st = f"  [{STATUS[name]}]" if name in STATUS else ""
    fig.suptitle(f"{TITLES.get(name, name)} — attention maps, 100% cue at S1 (cyan = cued/changed patch){st}",
                 fontsize=9, y=1.0)
    fig.savefig(os.path.join(FIG, f"atlas_{name}_attention.pdf"))
    plt.close(fig)


def logistic4(x, g, l, s, p): return g + (1 - g - l) / (1 + np.exp(-s * (x - p)))


def fit(deltas, y):
    from scipy.optimize import curve_fit
    if np.ptp(y) < 0.15: return None                        # degenerate (flat) — no meaningful fit
    try:
        p, _ = curve_fit(logistic4, deltas, y, p0=[0.05, 0.05, 0.2, 16],
                         bounds=([0, 0, 1e-3, 0], [0.5, 0.5, 5, 80]), maxfev=20000)
        return p
    except Exception:
        return None


def behavior_panel(d):
    name = str(d["name"]); resp = d["resp"]; rt = d["rt"]; fa = d["fa"]
    vals = list(d["validities"]); da = np.array(d["deltas"], float); xs = np.linspace(0, da.max(), 100)
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.4))
    # A: cued psychometric by validity
    for vi, v in enumerate(vals):
        c = plt.cm.viridis(vi / 3)
        ax[0].plot(da, resp[vi, :, 1], "o", color=c, ms=4)
        f = fit(da, resp[vi, :, 1])
        if f is not None: ax[0].plot(xs, logistic4(xs, *f), color=c, label=f"{int(v*100)}%")
        else: ax[0].plot(da, resp[vi, :, 1], "-", color=c, alpha=.5, label=f"{int(v*100)}%")
    ax[0].set(title="A. Cued psychometric by validity", xlabel="Δ orientation (deg)",
              ylabel="P(detect)", ylim=(-.03, 1.03)); ax[0].legend(title="validity", fontsize=6)
    # B: cued vs uncued at 100% validity
    vi = len(vals) - 1
    for ci, lab, col in [(1, "cued", "C0"), (0, "uncued", "C3")]:
        ax[1].plot(da, resp[vi, :, ci], "o", color=col, ms=4)
        f = fit(da, resp[vi, :, ci])
        if f is not None: ax[1].plot(xs, logistic4(xs, *f), color=col, label=lab)
        else: ax[1].plot(da, resp[vi, :, ci], "-", color=col, alpha=.5, label=lab)
    ax[1].set(title=f"B. {int(vals[vi]*100)}% validity: cued vs uncued",
              xlabel="Δ orientation (deg)", ylabel="P(detect)", ylim=(-.03, 1.03)); ax[1].legend(fontsize=7)
    # C: chronometric RT vs delta (cued) by validity
    any_rt = False
    for vi, v in enumerate(vals):
        y = rt[vi, :, 1]
        if np.isfinite(y).any():
            ax[2].plot(da, y, "-o", color=plt.cm.viridis(vi / 3), ms=4, label=f"{int(v*100)}%"); any_rt = True
    ax[2].set(title="C. Chronometric: RT vs Δ (cued)", xlabel="Δ orientation (deg)", ylabel="RT (frames)")
    if any_rt: ax[2].legend(title="validity", fontsize=6)
    else: ax[2].text(.5, .5, "never presses", ha="center", va="center", transform=ax[2].transAxes, color="gray")
    # thresholds + FA annotation
    thr = []
    for vi, v in enumerate(vals):
        fc = fit(da, resp[vi, :, 1]); fu = fit(da, resp[vi, :, 0])
        tc = f"{fc[3]:.0f}" if fc is not None else "—"; tu = f"{fu[3]:.0f}" if fu is not None else "—"
        thr.append(f"{int(v*100)}%: cued {tc}/unc {tu}")
    note = "thresholds (deg) " + " | ".join(thr) + f"\nFA by validity: " + \
           " ".join(f"{int(v*100)}%:{fa[i]:.2f}" for i, v in enumerate(vals))
    st = f"   [{STATUS[name]}]" if name in STATUS else ""
    fig.suptitle(f"{TITLES.get(name, name)} — behaviour (T=7, validity4){st}", fontsize=10, y=1.04)
    fig.text(0.5, -0.07, note, ha="center", fontsize=6.5, color="black!70" and "#333333")
    fig.savefig(os.path.join(FIG, f"atlas_{name}_behavior.pdf"))
    plt.close(fig)


def main():
    files = sorted(glob.glob(os.path.join(SRC, "*.npz")))
    for fp in files:
        d = np.load(fp, allow_pickle=True)
        attention_atlas(d); behavior_panel(d)
        print(f"  {str(d['name'])}: atlas + behaviour figures written")
    print(f"DONE → {FIG}")


if __name__ == "__main__":
    main()
