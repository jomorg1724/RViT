"""Render the affine_cascade deep-dive figures from analysis/deepdive_out/affine_cascade/*.npz
(NO torch). Mirrors the lab's deep-dive figure set: behaviour, attention (both transformers),
latent decoding (H1 vs H2), causal split-readout dissociation, value/critic calibration."""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "serif", "font.size": 8.5, "axes.titlesize": 9,
                     "figure.dpi": 150, "savefig.bbox": "tight", "axes.spines.top": False,
                     "axes.spines.right": False})
SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "analysis", "deepdive_out", "affine_cascade")
FIG = os.path.join(SRC, "figs"); os.makedirs(FIG, exist_ok=True)
L = lambda f: np.load(os.path.join(SRC, f), allow_pickle=True)


def logistic4(x, g, l, s, p): return g + (1 - g - l) / (1 + np.exp(-s * (x - p)))
def fit(da, y):
    from scipy.optimize import curve_fit
    if np.ptp(y) < 0.12: return None
    try:
        return curve_fit(logistic4, da, y, p0=[.05, .05, .2, 16], bounds=([0, 0, 1e-3, 0], [.5, .5, 5, 80]), maxfev=20000)[0]
    except Exception: return None


def fig_behaviour():
    d = L("exp1_behaviour.npz"); resp, rt, fa = d["resp"], d["rt"], d["fa"]
    props = list(d["proportions"]); da = np.array(d["deltas"], float); xs = np.linspace(0, da.max(), 100)
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
    for vi, v in enumerate(props):
        c = plt.cm.viridis(vi / 3); ax[0].plot(da, resp[vi, :, 1], "o", color=c, ms=4)
        f = fit(da, resp[vi, :, 1])
        ax[0].plot(xs, logistic4(xs, *f), color=c, label=f"{int(v*100)}%") if f is not None else None
    ax[0].set(title="A. Cued psychometric by cue reliability", xlabel="Δ orientation (°)", ylabel="P(detect)", ylim=(-.03, 1.03))
    ax[0].legend(title="reliability", fontsize=7)
    vi = props.index(1.0)
    for ci, lab, col in [(1, "cued", "C0"), (0, "uncued", "C3")]:
        ax[1].plot(da, resp[vi, :, ci], "o", color=col, ms=4); f = fit(da, resp[vi, :, ci])
        ax[1].plot(xs, logistic4(xs, *f), color=col, label=lab) if f is not None else None
    ax[1].set(title="B. 100% cue: cued vs uncued", xlabel="Δ orientation (°)", ylabel="P(detect)", ylim=(-.03, 1.03)); ax[1].legend()
    for vi, v in enumerate(props):
        y = rt[vi, :, 1]
        if np.isfinite(y).any(): ax[2].plot(da, y, "-o", color=plt.cm.viridis(vi / 3), ms=4, label=f"{int(v*100)}%")
    ax[2].set(title="C. Chronometric: RT vs Δ (cued)", xlabel="Δ orientation (°)", ylabel="RT (frames)"); ax[2].legend(title="reliability", fontsize=7)
    thr = []
    for vi, v in enumerate(props):
        fc, fu = fit(da, resp[vi, :, 1]), fit(da, resp[vi, :, 0])
        thr.append(f"{int(v*100)}%: c{fc[3]:.0f}/u{fu[3]:.0f}" if (fc is not None and fu is not None) else f"{int(v*100)}%:—")
    fig.text(0.5, -0.04, "thresholds(°) " + " | ".join(thr) + "    FA " + " ".join(f"{int(v*100)}%:{fa[i]:.2f}" for i, v in enumerate(props)), ha="center", fontsize=7)
    fig.suptitle("affine_cascade — behaviour (T=7, validity4)", y=1.02, fontsize=10)
    fig.savefig(os.path.join(FIG, "fig_behaviour.pdf")); plt.close(fig)


def _g(a): return a.reshape(2, 2)
def fig_attention():
    d = L("exp2_attention.npz"); conds = d["conds"].item(); tc = d["timecourse"].item()
    T = conds["change"]["T1"].shape[0]
    fr = conds["change"]["frames"]
    rows = [("input", None, None)] + [(f"{s} {c}", c, s) for c in ("nochange", "change") for s in ("T1", "T2")]
    fig, ax = plt.subplots(len(rows), T, figsize=(0.95 * T, 0.95 * len(rows) + 0.3),
                           gridspec_kw=dict(wspace=0.08, hspace=0.16))
    for t in range(T):
        a = ax[0, t]
        f = fr[t].astype(float); f = (f - f.min()) / (np.ptp(f) + 1e-9)
        a.imshow(f if f.ndim == 2 else f.mean(-1), cmap="gray"); a.set_xticks([]); a.set_yticks([])
        a.set_title(("cue" if t == 1 else "chg" if t == 5 else f"t{t}"), fontsize=7)
        if t in (1, 5):
            for sp in a.spines.values(): sp.set_color("crimson" if t == 5 else "steelblue"); sp.set_linewidth(1.5)
    ax[0, 0].set_ylabel("input", fontsize=7, rotation=0, ha="right", va="center")
    for r, (lab, cond, src) in enumerate(rows[1:], start=1):
        maps = conds[cond][src]; vmax = max(maps.max(), 1e-6)
        for t in range(T):
            a = ax[r, t]; a.imshow(_g(maps[t]), cmap="magma", vmin=0, vmax=vmax); a.set_xticks([]); a.set_yticks([])
            for (i, j), val in np.ndenumerate(_g(maps[t])):
                a.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6, color="white" if val < .6 * vmax else "black")
            a.add_patch(Rectangle((-.5, -.5), 1, 1, fill=False, ec="cyan", lw=1.0))
        ax[r, 0].set_ylabel(lab.replace("nochange", "no-chg").replace("change", "chg"), fontsize=6.5, rotation=0, ha="right", va="center")
    fig.suptitle("affine_cascade — attention maps, 100% cue@S1 (T1→H1→critic, T2→H2→actor; cyan=cued/changed S1)", y=1.0, fontsize=9)
    fig.savefig(os.path.join(FIG, "fig_attention_maps.pdf")); plt.close(fig)
    # cue-following: per transformer (rows) x cue position (cols), attention to S1 vs S4 over
    # time (NO change → pure cue-driven). A cue-follower's peak swaps with the cue.
    fig2, ax2 = plt.subplots(2, 2, figsize=(9, 6), sharex=True, sharey=True)
    cols = [("cue0", "cue@S1  (cued = S1)"), ("cue3", "cue@S4  (cued = S4)")]
    for ri, src in enumerate(("T1", "T2")):
        for ci, (key, clbl) in enumerate(cols):
            a = ax2[ri, ci]
            a.plot(range(T), tc[key][f"{src}_S1"], "-o", color="C0", ms=4, label="attention → S1")
            a.plot(range(T), tc[key][f"{src}_S4"], "-s", color="C1", ms=4, label="attention → S4")
            a.axhline(0.25, ls=":", c="k", lw=.7); a.axvline(1, ls=":", c="steelblue", lw=.7)
            head = "H1 → critic" if src == "T1" else "H2 → actor"
            a.set_title(f"{src} ({head}) — {clbl}", fontsize=8.5)
            if ri == 1: a.set_xlabel("frame t")
            if ci == 0: a.set_ylabel(f"{src} attention")
            if ri == 0 and ci == 0: a.legend(fontsize=7, loc="upper left")
    fig2.suptitle("affine_cascade — cue-following (no change): T1's peak swaps with the cue (orients); "
                  "T2's does not", y=1.0, fontsize=9.5)
    fig2.tight_layout(); fig2.savefig(os.path.join(FIG, "fig_attention_timecourse.pdf")); plt.close(fig2)


def fig_decoding():
    d = L("exp3_decoding.npz"); T = len(d["cue_H1"]); x = range(T)
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.2))
    for k, (key, ttl, chance) in enumerate([("cue", "cue location (S1 vs S4)", 0.5),
                                            ("val", "high vs low reliability", 0.5),
                                            ("chgloc", "changed location (post-change)", 0.25)]):
        ax[k].plot(x, d[f"{key}_H1"], "-o", color="C1", ms=4, label="H1 (→critic)")
        ax[k].plot(x, d[f"{key}_H2"], "-s", color="C0", ms=4, label="H2 (→actor)")
        ax[k].axhline(chance, ls=":", c="k", lw=.8); ax[k].axvline(1, ls=":", c="steelblue", lw=.7); ax[k].axvline(5, ls=":", c="crimson", lw=.7)
        ax[k].set(title=f"{chr(65+k)}. Decode {ttl}", xlabel="frame t", ylabel="balanced acc", ylim=(0, 1.03)); ax[k].legend(fontsize=7)
    fig.suptitle("affine_cascade — temporal linear decoding from memory (H1 vs H2)", y=1.02, fontsize=10)
    fig.savefig(os.path.join(FIG, "fig_decoding.pdf")); plt.close(fig)


def fig_causal():
    d = L("exp4_causal.npz"); b = d["biases"]
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    ax[0].plot(b, d["hit_t1"], "-o", color="C1", label="T1 (→H1→critic)"); ax[0].plot(b, d["hit_t2"], "-s", color="C0", label="T2 (→H2→actor)")
    ax[0].set(title="A. Bias attention→changed S1: effect on DECISION", xlabel="attention bias b", ylabel="P(hit)"); ax[0].legend(fontsize=7); ax[0].axvline(0, ls=":", c="k", lw=.7)
    ax[1].plot(b, d["ent_t1"], "-o", color="C1", label="T1"); ax[1].plot(b, d["ent_t2"], "-s", color="C0", label="T2")
    ax[1].set(title="B. Same bias: effect on CRITIC uncertainty", xlabel="attention bias b", ylabel="critic quantile std"); ax[1].legend(fontsize=7); ax[1].axvline(0, ls=":", c="k", lw=.7)
    fig.suptitle("affine_cascade — causal attention (split-readout dissociation)", y=1.02, fontsize=10)
    fig.savefig(os.path.join(FIG, "fig_causal.pdf")); plt.close(fig)


def fig_value():
    d = L("exp5_value.npz"); T = len(d["vt_chg"]); da = np.array(d["deltas"], float)
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.2))
    ax[0].plot(range(T), d["vt_chg"], "-o", color="C3", ms=4, label="change"); ax[0].plot(range(T), d["vt_noc"], "-o", color="C0", ms=4, label="no-change")
    ax[0].axvline(5, ls=":", c="crimson", lw=.8); ax[0].set(title="A. State value over the trial", xlabel="frame t", ylabel="V (scalar)"); ax[0].legend(fontsize=7)
    p, r = d["preds"], d["rets"]; ax[1].scatter(r, p, s=8, alpha=.4, color="C2")
    lim = [min(r.min(), p.min()), max(r.max(), p.max())]; ax[1].plot(lim, lim, "k--", lw=.8)
    cc = np.corrcoef(p, r)[0, 1]
    ax[1].set(title=f"B. Critic calibration (r={cc:.2f})", xlabel="realised return", ylabel="predicted V")
    ax[2].plot(da, d["unc"], "-o", color="C4", ms=4); ax[2].set(title="C. Outcome uncertainty vs evidence", xlabel="Δ orientation (°)", ylabel="critic quantile std @ change")
    fig.suptitle("affine_cascade — value / critic calibration", y=1.02, fontsize=10)
    fig.savefig(os.path.join(FIG, "fig_value.pdf")); plt.close(fig)


def main():
    for name, fn in [("behaviour", fig_behaviour), ("attention", fig_attention), ("decoding", fig_decoding),
                     ("causal", fig_causal), ("value", fig_value)]:
        try: fn(); print(f"  wrote fig_{name}")
        except Exception as e: print(f"  SKIP {name}: {e}")
    print(f"FIGS -> {FIG}")


if __name__ == "__main__":
    main()
