"""Render the T=29 per-model atlas from analysis_t29/out/*.npz (NO torch). Per model:
(1) attention atlas — input movie + 10x10 attention heat-maps at EVERY frame (29), for
    [cue100%@S1 no-change] and [cue100%@S1 visible change@S1], one row per token source
    (image / memory H1 / memory H2 for cross-attention; salience->H1/H2, topdown->H2 for
    dual-stream); (2) a behaviour panel — psychometric (cued vs uncued x validity),
    chronometric (RT), and the cued-quadrant attention TIMECOURSE (a readable summary of the
    29-frame maps). Writes to reports/thesis/figures/atlas_t29/."""
import os, glob, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "serif", "font.size": 7.5, "axes.titlesize": 8,
                     "figure.dpi": 140, "savefig.bbox": "tight"})
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "out")
FIG = os.path.join(HERE, "..", "reports", "thesis", "figures", "atlas_t29")
os.makedirs(FIG, exist_ok=True)
TITLES = {"v5": "v5 — memory-as-tokens self-attention", "v5_part2": "v5\\_part2 — cross-attention over memory",
          "v8": "v8 — cross-attention, $H_1$ residual", "v11": "v11 — parallel dual-stream",
          "v11_part2": "v11\\_part2 — split-readout cross-talk", "v11_part5": "v11\\_part5 — cross-talk (distractor task)"}
SRCDISP = lambda s: s.replace("->", r"$\to$").replace("salience", "sal.").replace("topdown", "td").replace("memory ", "")


def cued_quad(m):  # mean over the top-left 5x5 block (cue at S1 = top-left quadrant)
    h, w = m.shape[-2] // 2, m.shape[-1] // 2
    return m[..., :h, :w].mean(axis=(-2, -1))


def rgb(frame):
    f = frame.astype(float); lo, hi = f.min(), f.max()
    return np.clip((f - lo) / (hi - lo + 1e-9), 0, 1)


def attention_atlas(d):
    name = str(d["name"]); amaps = d["amaps"].item(); frames = d["frames"].item()
    srcs = list(amaps["change"].keys()); T = d["frames"].item()["change"].shape[0]
    ct = int(d["change_t"]); nrows = 1 + 2 * len(srcs)
    fig, ax = plt.subplots(nrows, T, figsize=(0.40 * T, 0.62 * nrows + 0.5),
                           gridspec_kw=dict(wspace=0.04, hspace=0.10))
    for t in range(T):
        a = ax[0, t]; a.imshow(rgb(frames["change"][t])); a.set_xticks([]); a.set_yticks([])
        if t in (1, ct) or t % 4 == 0: a.set_title(("cue" if t == 1 else "chg" if t == ct else f"{t}"), fontsize=6)
        if t in (1, ct):
            for s in a.spines.values(): s.set_color("crimson" if t == ct else "steelblue"); s.set_linewidth(1.4)
    ax[0, 0].set_ylabel("input", fontsize=6.5, rotation=0, ha="right", va="center")
    r = 1
    for cond in ("nochange", "change"):
        for s in srcs:
            maps = amaps[cond][s]; vmax = max(maps.max(), 1e-6)
            for t in range(T):
                a = ax[r, t]; a.imshow(maps[t], cmap="magma", vmin=0, vmax=vmax)
                a.set_xticks([]); a.set_yticks([])
                a.add_patch(Rectangle((-.5, -.5), 5, 5, fill=False, ec="cyan", lw=0.5))  # cued quad (TL)
            ax[r, 0].set_ylabel(("no-chg" if cond == "nochange" else "chg") + "\n" + SRCDISP(s),
                                fontsize=5.8, rotation=0, ha="right", va="center")
            r += 1
    fig.suptitle(f"{TITLES.get(name, name)} — attention maps, every frame (T=29), 100\\% cue at S1 "
                 f"(cyan = cued quadrant; chg @ t={ct})", fontsize=9, y=1.005)
    fig.savefig(os.path.join(FIG, f"atlas_t29_{name}_attention.pdf")); plt.close(fig)


def logistic4(x, g, l, s, p): return g + (1 - g - l) / (1 + np.exp(-s * (x - p)))


def fit(da, y):
    from scipy.optimize import curve_fit
    if np.ptp(y) < 0.15: return None
    try:
        p, _ = curve_fit(logistic4, da, y, p0=[0.05, 0.05, 0.2, 16],
                         bounds=([0, 0, 1e-3, 0], [0.5, 0.5, 5, 80]), maxfev=20000); return p
    except Exception: return None


def behavior_panel(d):
    name = str(d["name"]); resp = d["resp"]; rt = d["rt"]; fa = d["fa"]
    vals = list(d["validities"]); da = np.array(d["deltas"], float); xs = np.linspace(0, da.max(), 100)
    amaps = d["amaps"].item(); srcs = list(amaps["change"].keys()); ct = int(d["change_t"])
    fig, ax = plt.subplots(1, 4, figsize=(14, 3.2))
    for vi, v in enumerate(vals):
        c = plt.cm.viridis(vi / 3); ax[0].plot(da, resp[vi, :, 1], "o", color=c, ms=4)
        f = fit(da, resp[vi, :, 1])
        ax[0].plot(xs, logistic4(xs, *f), color=c, label=f"{int(v*100)}%") if f is not None else \
            ax[0].plot(da, resp[vi, :, 1], "-", color=c, alpha=.5, label=f"{int(v*100)}%")
    ax[0].set(title="A. Cued psychometric by validity", xlabel="Δ (deg)", ylabel="P(detect)", ylim=(-.03, 1.03))
    ax[0].legend(title="validity", fontsize=6)
    vi = 0  # validities[0] = 1.0 (100%)
    for ci, lab, col in [(1, "cued", "C0"), (0, "uncued", "C3")]:
        ax[1].plot(da, resp[vi, :, ci], "o", color=col, ms=4); f = fit(da, resp[vi, :, ci])
        ax[1].plot(xs, logistic4(xs, *f), color=col, label=lab) if f is not None else \
            ax[1].plot(da, resp[vi, :, ci], "-", color=col, alpha=.5, label=lab)
    ax[1].set(title=f"B. {int(vals[vi]*100)}% validity: cued vs uncued", xlabel="Δ (deg)", ylabel="P(detect)", ylim=(-.03, 1.03))
    ax[1].legend(fontsize=7)
    any_rt = False
    for vi, v in enumerate(vals):
        y = rt[vi, :, 1]
        if np.isfinite(y).any(): ax[2].plot(da, y, "-o", color=plt.cm.viridis(vi / 3), ms=4, label=f"{int(v*100)}%"); any_rt = True
    ax[2].set(title="C. Chronometric: RT vs Δ (cued)", xlabel="Δ (deg)", ylabel="RT (frames post-change)")
    if any_rt: ax[2].legend(title="validity", fontsize=6)
    # D: cued-quadrant attention timecourse (readable summary of the 29-frame maps)
    for s in srcs:
        tc_ch = cued_quad(amaps["change"][s]); tc_nc = cued_quad(amaps["nochange"][s])
        l, = ax[3].plot(range(len(tc_ch)), tc_ch, "-", lw=1.3, label=f"{SRCDISP(s)} (chg)")
        ax[3].plot(range(len(tc_nc)), tc_nc, "--", lw=1.0, color=l.get_color(), alpha=.6)
    ax[3].axvline(1, ls=":", c="steelblue", lw=0.8); ax[3].axvline(ct, ls=":", c="crimson", lw=0.8)
    ax[3].text(1, ax[3].get_ylim()[1], "cue", fontsize=6, color="steelblue", va="top")
    ax[3].text(ct, ax[3].get_ylim()[1], "chg", fontsize=6, color="crimson", va="top")
    ax[3].set(title="D. Attention to CUED quadrant over time", xlabel="frame t", ylabel="attention (cued quad)")
    ax[3].legend(fontsize=5.5, ncol=1)
    thr = []
    for vi, v in enumerate(vals):
        fc = fit(da, resp[vi, :, 1]); fu = fit(da, resp[vi, :, 0])
        thr.append(f"{int(v*100)}%: c{fc[3]:.0f}/u{fu[3]:.0f}" if (fc is not None and fu is not None) else f"{int(v*100)}%: -")
    fig.suptitle(f"{TITLES.get(name, name)} — behaviour (T=29)", fontsize=10, y=1.05)
    fig.text(0.5, -0.06, "thresholds(deg) " + " | ".join(thr) + "   FA: " +
             " ".join(f"{int(v*100)}%:{fa[i]:.2f}" for i, v in enumerate(vals)), ha="center", fontsize=6.5)
    fig.savefig(os.path.join(FIG, f"atlas_t29_{name}_behavior.pdf")); plt.close(fig)


def main():
    for fp in sorted(glob.glob(os.path.join(SRC, "*.npz"))):
        d = np.load(fp, allow_pickle=True)
        attention_atlas(d); behavior_panel(d)
        print(f"  {str(d['name'])}: figures written")
    print(f"DONE -> {FIG}")


if __name__ == "__main__":
    main()
