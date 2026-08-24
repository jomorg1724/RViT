"""Figures for the v11 frame-repeat deep dive. Reads out_framerepeat/*.npz, writes
paper/figs/*.png. Torch-free (numpy + matplotlib). Robust to missing npz."""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(_HERE, "out_framerepeat")
FIGS = os.path.join(_HERE, "paper_framerepeat", "figs"); os.makedirs(FIGS, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 130, "savefig.bbox": "tight"})
SAL, TD = "#1f77b4", "#d62728"
CCOL = {"red": "#d62728", "green": "#2ca02c", "blue": "#1f77b4"}
FR, CHG = 5, 25


def _ld(name):
    p = f"{OUT}/{name}.npz"
    return np.load(p, allow_pickle=True) if os.path.exists(p) else None


def _frame_grid(ax, T=35):
    for L in range(0, T + 1, FR):
        ax.axvline(L, color="0.9", lw=0.6, zorder=0)
    ax.axvline(CHG, color="k", ls="--", lw=1.0, zorder=1)


def fig_behaviour():
    d = _ld("exp1_behaviour")
    if d is None: return
    fig, ax = plt.subplots(1, 4, figsize=(13, 3.0))
    deltas = d["deltas"]
    # (0) SDT decomposition
    sdt = [float(d["overall"]), float(d["hit_rate"]), float(d["correct_reject"]), float(d["fa_nochange"])]
    ax[0].bar(["overall", "hit\n(change)", "corr-rej\n(no-chg)", "false\nalarm"], sdt,
              color=["0.4", "#2ca02c", "#1f77b4", "#d62728"])
    ax[0].set_ylim(0, 1); ax[0].set_ylabel("rate"); ax[0].set_title("a  signal detection")
    for i, v in enumerate(sdt): ax[0].text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
    # (1) hit/RT vs delta, valid vs invalid (ring 1.0)
    hit = d["hit"]; rt = d["rt"]
    ax[1].plot(deltas, hit[0, 0], "-o", color="#2ca02c", label="valid", ms=4)
    ax[1].plot(deltas, hit[0, 1], "--s", color="#d62728", label="invalid", ms=4)
    ax[1].set_xlabel("change magnitude |Δθ|"); ax[1].set_ylabel("P(hit | change)")
    ax[1].set_ylim(0, 1); ax[1].legend(frameon=False, fontsize=8); ax[1].set_title("b  psychometric (ring 1.0)")
    axr = ax[1].twinx(); axr.spines["top"].set_visible(False)
    axr.plot(deltas, rt[0, 0], ":", color="#2ca02c", lw=1); axr.plot(deltas, rt[0, 1], ":", color="#d62728", lw=1)
    axr.set_ylabel("median RT (physical steps after change)", fontsize=8)
    # (2) hit by proportion (reliability), valid, large delta
    props = d["proportions"]
    ax[2].plot(props, hit[:, 0, -1], "-o", color="0.2", ms=5)
    ax[2].set_xlabel("displayed cue reliability"); ax[2].set_ylabel("P(hit) at |Δθ|=1.0")
    ax[2].set_ylim(0, 1); ax[2].set_title("c  reliability scaling")
    # (3) value by colour
    vh = d["val_hit"]; colors = [str(c) for c in d["colors"]]
    ax[3].bar(colors, vh, color=[CCOL[c] for c in colors])
    ax[3].set_ylim(0, 1); ax[3].set_ylabel("P(hit) near threshold"); ax[3].set_title("d  value (cue colour)")
    for i, v in enumerate(vh): ax[3].text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
    fig.tight_layout(); fig.savefig(f"{FIGS}/fig_behaviour.png"); plt.close(fig)
    print("  fig_behaviour")


def fig_attention():
    d = _ld("exp2_attention")
    if d is None: return
    T = int(d["T"])
    # canonical valid cue: salience vs top-down per-quadrant timecourse
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.3), sharey=True)
    qn = ["S1 (cued, changes)", "S2", "S3", "S4"]
    qc = ["#000000", "#888888", "#bbbbbb", "#cf6679"]
    for j, (key, ttl) in enumerate([("sal_quad", "salience stream  (reads H1)"),
                                     ("td_quad", "top-down stream  (reads H2)")]):
        Q = d[key]                       # (T, 4)
        for q in range(4):
            ax[j].plot(range(T), Q[:, q], color=qc[q], lw=1.8 if q == 0 else 1.1,
                       label=qn[q] if j == 0 else None)
        _frame_grid(ax[j], T); ax[j].set_title(ttl); ax[j].set_xlabel("physical step")
    ax[0].set_ylabel("attention onto quadrant"); ax[0].legend(frameon=False, fontsize=7, loc="upper left")
    fig.suptitle("Per-quadrant attention, valid cue-left, ring 1.0, change at S1 (physical step 25; grey = held-frame boundaries)",
                 fontsize=9)
    fig.tight_layout(); fig.savefig(f"{FIGS}/fig_attention.png"); plt.close(fig)
    print("  fig_attention")

    # S1 timecourse across all conditions, valid vs invalid
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.3), sharey=True)
    S1s, S1t = d["S1_sal"], d["S1_td"]; conds = [str(c) for c in d["conds"]]
    for ci, c in enumerate(conds):
        prop, side = c.rsplit("_", 1)
        valid = side == "left"; alpha = 0.4 + 0.6 * (["0.25", "0.5", "0.75", "1.0"].index(prop) / 3)
        for j, S in enumerate([S1s, S1t]):
            ax[j].plot(range(S.shape[1]), S[ci], color="#2ca02c" if valid else "#d62728",
                       lw=1.2, alpha=alpha, ls="-" if valid else "--")
    for j, ttl in enumerate(["salience: S1 read", "top-down: S1 read"]):
        _frame_grid(ax[j], S1s.shape[1]); ax[j].set_title(ttl); ax[j].set_xlabel("physical step")
    ax[0].set_ylabel("attention onto S1 (changed quadrant)")
    ax[0].legend(handles=[Line2D([], [], color="#2ca02c", label="valid (cue→S1)"),
                          Line2D([], [], color="#d62728", ls="--", label="invalid (cue→S4)")],
                 frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(f"{FIGS}/attn_S1_timecourse.png"); plt.close(fig)
    print("  attn_S1_timecourse")

    # spatial maps at key physical timepoints
    gh, gw = int(d["grid_h"]), int(d["grid_w"])
    tps = [3, 12, 24, 26, 30]
    fig, ax = plt.subplots(2, len(tps), figsize=(2.0 * len(tps), 4.4))
    for r, (key, lab) in enumerate([("sal_map", "salience"), ("td_map", "top-down")]):
        M = d[key]                       # (T, n_tokens)
        vmax = np.percentile(M, 99)
        for c, tp in enumerate(tps):
            im = ax[r, c].imshow(M[tp].reshape(gh, gw), cmap="magma", vmin=0, vmax=vmax)
            ax[r, c].add_patch(plt.Rectangle((-0.5, -0.5), gw / 2 - 0.5 + 0.5, gh / 2 - 0.5 + 0.5,
                               fill=False, ec="cyan", lw=1.5))   # S1 = top-left block
            ax[r, c].set_xticks([]); ax[r, c].set_yticks([])
            if r == 0: ax[r, c].set_title(f"t={tp}" + ("  (change)" if tp == 26 else ""), fontsize=8)
            if c == 0: ax[r, c].set_ylabel(lab, fontsize=9)
    fig.suptitle("Spatial attention maps (cyan = cued/changed quadrant S1); change onset at physical step 25", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{FIGS}/attn_spatial.png"); plt.close(fig)
    print("  attn_spatial")


def fig_decoding():
    d = _ld("exp3_decoding")
    if d is None: return
    T = int(d["T"])
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.2), sharex=True)
    panels = [("cue_colour", float(d["chance_colour"]), "cue colour (value)"),
              ("cue_reliability", float(d["chance_rel"]), "cue reliability"),
              ("change_quadrant", float(d["chance_quad"]), "changed quadrant")]
    for k, (var, ch, ttl) in enumerate(panels):
        for mem, col in [("H1", SAL), ("H2", TD)]:
            y = d[f"{mem}_{var}"]
            ax[k].plot(range(T), y, color=col, lw=1.8, label=f"{mem} ({'salience-fed' if mem=='H1' else 'top-down'})")
        ax[k].axhline(ch, color="0.5", ls=":", lw=1)
        _frame_grid(ax[k], T); ax[k].set_ylim(0, 1.02); ax[k].set_title(ttl); ax[k].set_xlabel("physical step")
        if k == 0: ax[k].set_ylabel("CV balanced accuracy"); ax[k].legend(frameon=False, fontsize=7)
    fig.suptitle("Linear decoding of task variables from per-quadrant memory over time (dotted = chance)", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{FIGS}/fig_decoding.png"); plt.close(fig)
    print("  fig_decoding")


def fig_causal():
    d = _ld("exp4_causal")
    if d is None: return
    hit, ent, biases = d["hit"], d["ent"], d["biases"]; levers = [str(x) for x in d["levers"]]
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.3))
    # (a) decision effect = hit(+6) - hit(-6) per lever
    eff = hit[:, -1] - hit[:, 0]
    cols = ["#d62728" if "TD" in l else "#1f77b4" for l in levers]
    ax[0].barh(levers, eff, color=cols); ax[0].axvline(0, color="k", lw=0.8)
    ax[0].set_xlabel("Δ P(hit)  over bias sweep [−6,+6]"); ax[0].set_title("a  causal effect on the decision")
    for i, v in enumerate(eff): ax[0].text(v + (0.005 if v >= 0 else -0.005), i, f"{v:+.2f}",
                                           va="center", ha="left" if v >= 0 else "right", fontsize=8)
    # (b) hit vs bias curves
    for li, l in enumerate(levers):
        ax[1].plot(biases, hit[li], "-o", color="#d62728" if "TD" in l else "#1f77b4",
                   ls="-" if "S1" in l else "--", ms=4, label=l)
    ax[1].set_xlabel("injected attention bias"); ax[1].set_ylabel("P(hit | change@S1)")
    ax[1].legend(frameon=False, fontsize=7); ax[1].set_title("b  dose–response")
    fig.tight_layout(); fig.savefig(f"{FIGS}/fig_causal.png"); plt.close(fig)
    print("  fig_causal")


def fig_value():
    d = _ld("exp5_value")
    if d is None: return
    T = int(d["T"]); colors = [str(c) for c in d["colors"]]
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.2))
    for c in colors:
        ax[0].plot(range(T), d[f"vt_{c}"], color=CCOL[c], lw=1.8, label=c)
        ax[1].plot(range(T), d[f"adv_{c}"], color=CCOL[c], lw=1.8)
    ax[0].plot(range(T), d["vt_nochange"], color="0.5", lw=1.5, ls="--", label="no-change")
    ax[1].plot(range(T), d["adv_nochange"], color="0.5", lw=1.5, ls="--")
    _frame_grid(ax[0], T); _frame_grid(ax[1], T)
    ax[0].set_title("a  state value over time"); ax[0].set_ylabel("V(s)"); ax[0].set_xlabel("physical step")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].axhline(0, color="k", lw=0.7); ax[1].set_title("b  press − wait advantage")
    ax[1].set_xlabel("physical step")
    mags, em = d["mags"], d["ent_mag"]
    ax[2].plot(mags, em, "-o", color="0.2", ms=5); ax[2].set_title("c  outcome uncertainty vs evidence")
    ax[2].set_xlabel("change magnitude |Δθ|"); ax[2].set_ylabel("critic entropy just after change")
    fig.tight_layout(); fig.savefig(f"{FIGS}/fig_value.png"); plt.close(fig)
    print("  fig_value")


if __name__ == "__main__":
    for f in (fig_behaviour, fig_attention, fig_decoding, fig_causal, fig_value):
        try: f()
        except Exception as e: print("  SKIP", f.__name__, "->", repr(e))
    print("figs in", FIGS)
