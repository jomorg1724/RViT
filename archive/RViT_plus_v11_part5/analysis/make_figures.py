"""Regenerate all deep-dive figures from the cached *_summary.npz data with the shared
publication style and the Priority/Value terminology. No model or torch needed — the
heavy analysis scripts save their data; this script does the plotting. Run:
    .venv/bin/python -m RViT_plus_v11_part5.analysis.make_figures
"""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from RViT_plus_v11_part5.analysis import ddstyle as S
from RViT_plus_v11_part5.analysis import distractor_dd as dd

S.apply()
OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
def load(name): return np.load(f"{OUT}/{name}", allow_pickle=True)
def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png"); fig.savefig(f"{OUT}/{name}.pdf"); plt.close(fig)
    print(f"  {name}")

QI = dd.quadrant_token_indices()
QBOX = {0: (0, 0), 1: (5, 0), 2: (0, 5), 3: (5, 5)}   # (row0,col0)


# ── 1. behaviour ──────────────────────────────────────────────────────────────
def fig_behavior():
    b = load("behavior_summary.npz"); t = load("behavior_trials.npz")
    color = t["color"].astype(str); ct = t["ct"].astype(bool); eng = t["engaged"].astype(bool)
    hit = t["hit"]; rt = t["rt"]
    fig, ax = plt.subplots(2, 2, figsize=(13, 10))
    cols = ["red", "green", "blue"]; xc = np.arange(3); w = 0.26
    ax[0,0].bar(xc - w, b["H"], w, color=S.HIT, edgecolor="k", lw=.6, label="hit")
    ax[0,0].bar(xc,     b["E"], w, color=S.FA, edgecolor="k", lw=.6, label="early-press / bail")
    ax[0,0].bar(xc + w, b["Mi"], w, color=S.NEUTRAL, edgecolor="k", lw=.6, label="miss")
    ax[0,0].set_xticks(xc); ax[0,0].set_xticklabels([f"{c}\n(reward {v})" for c, v in zip(cols, [5,3,1])])
    ax[0,0].set_ylabel("proportion of target trials"); ax[0,0].set_ylim(0, 1.12)
    ax[0,0].set_title("A  Value gate: engage red/green, bail on blue")
    ax[0,0].legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.13), fontsize=11.5)
    labels = ["no\ndistractor", "distractor\nbefore target"]; xb = np.arange(2); w2 = 0.36
    ax[0,1].bar(xb - w2/2, b["hit_eng"], w2, color=S.HIT, edgecolor="k", lw=.6, label="hit rate")
    ax[0,1].bar(xb + w2/2, b["efa_eng"], w2, color=S.FA, edgecolor="k", lw=.6, label="false-alarm rate")
    ax[0,1].set_xticks(xb); ax[0,1].set_xticklabels(labels)
    ax[0,1].set_ylabel("rate (engaged trials)"); ax[0,1].set_ylim(0, 1)
    ax[0,1].set_title("B  Distractor is suppressed"); ax[0,1].legend()
    ax[0,1].annotate("≈ 0 false alarms\neither way", xy=(1, 0.03), xytext=(0.42, 0.62), ha="center",
                     fontsize=12, color="#555", arrowprops=dict(arrowstyle="->", color="#555", lw=1))
    xr = np.arange(4); R = [0.25, 0.5, 0.75, 1.0]
    ax[1,0].plot(xr, b["eng_primary"], "o-", color=S.TARGET, label="cued quadrant (primary)")
    ax[1,0].plot(xr, b["eng_secondary"], "s--", color="#d95f0e", label="same-side secondary")
    ax[1,0].set_xticks(xr); ax[1,0].set_xticklabels([f"{p:g}" for p in R])
    ax[1,0].set_xlabel("cue reliability"); ax[1,0].set_ylabel("hit rate (engaged)")
    ax[1,0].set_ylim(0.5, 1.0); ax[1,0].set_title("C  Cued-quadrant benefit"); ax[1,0].legend()
    rte = rt[hit & eng]; rte = rte[~np.isnan(rte)]
    ax[1,1].hist(rte, bins=np.arange(-0.5, 10.5, 1), color=S.PRIORITY, edgecolor="k", lw=.5)
    ax[1,1].axvline(np.median(rte), color="k", ls="--", lw=1.4)
    ax[1,1].set_xlabel("reaction time (frames after change)"); ax[1,1].set_ylabel("count of hits")
    ax[1,1].set_title(f"D  Chronometric (median {np.median(rte):.0f} frame" + ("s" if np.median(rte)!=1 else "") + ")")
    save(fig, "behavior")


# ── 2-3. spatial attention maps ───────────────────────────────────────────────
MAP_CONDS = [
    ("cue-left_red_+distractor",  "cue left, red,\n+ distractor",  0, 2),
    ("cue-right_red_+distractor", "cue right, red,\n+ distractor", 3, 1),
    ("cue-left_red_no_distractor","cue left, red,\nno distractor", 0, None),
    ("cue-left_BLUE_+distractor", "cue left, BLUE,\n+ distractor", 0, 2),
]
TPS = [("post-cue\n$t=3$", 3), ("distractor on\n$t=14$", 14), ("target change\n$t=17$", 17), ("post-change\n$t=19$", 19)]

def _draw(ax, vec, vmax, tq, dq):
    im = ax.imshow(vec.reshape(10, 10), cmap=S.MAPCMAP, vmin=0, vmax=vmax, interpolation="nearest")
    if tq is not None:
        r, c = QBOX[tq]; ax.add_patch(Rectangle((c-.5, r-.5), 5, 5, fill=False, ec=S.TARGET, lw=2.6))
    if dq is not None:
        r, c = QBOX[dq]; ax.add_patch(Rectangle((c-.5, r-.5), 5, 5, fill=False, ec=S.DISTRACT, lw=2.6, ls=(0, (4, 2))))
    ax.set_xticks([]); ax.set_yticks([])
    return im

def fig_maps(stream, title, fname):
    d = load("maps_summary.npz")
    vmax = max(np.percentile(d[f"{k}_{stream}"][[3,14,17,19]], 99) for k, *_ in MAP_CONDS)
    fig, ax = plt.subplots(len(MAP_CONDS), len(TPS), figsize=(11.5, 11.0))
    for i, (key, rowlab, tq, dq) in enumerate(MAP_CONDS):
        m = d[f"{key}_{stream}"]
        for j, (tlab, tt) in enumerate(TPS):
            im = _draw(ax[i, j], m[tt], vmax, tq, dq)
            if i == 0: ax[i, j].set_title(tlab, fontsize=14, loc="center", fontweight="normal")
        ax[i, 0].set_ylabel(rowlab, fontsize=13.5)
    fig.suptitle(title, fontweight="bold", fontsize=18)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02); cb.set_label("attention", fontsize=14)
    h = [plt.Line2D([], [], color=S.TARGET, lw=2.6, label="target quadrant"),
         plt.Line2D([], [], color=S.DISTRACT, lw=2.6, ls=(0, (4, 2)), label="distractor quadrant")]
    fig.legend(handles=h, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.035), fontsize=13)
    save(fig, fname)


# ── 4. per-quadrant attention time-courses ────────────────────────────────────
def fig_quad_timecourse():
    d = load("maps_summary.npz"); CT, DT = int(d["CT"]), int(d["DT"])
    nm = "cue-left_red_+distractor"
    def q(stream, qd): return d[f"{nm}_{stream}"][:, QI[qd]].sum(1)
    T = d[f"{nm}_sal"].shape[0]; tt = np.arange(T)
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.2))
    for a, stream, tit in [(ax[0], "sal", "A  Priority stream: locks target, ignores distractor"),
                           (ax[1], "td", "B  Value stream: broad, transiently reads distractor")]:
        a.plot(tt, q(stream, 0), color=S.TARGET, label="target quad (cued primary)")
        a.plot(tt, q(stream, 1), color=S.PRIORITY, lw=2.0, label="cued secondary quad")
        a.plot(tt, q(stream, 2), color=S.DISTRACT, ls=(0, (4, 2)), label="distractor quad")
        a.plot(tt, q(stream, 3), color=S.NEUTRAL, lw=1.6, ls=":", label="other uncued quad")
        a.axvline(DT, color=S.DISTRACT, ls=":", lw=1.2); a.axvline(CT, color=S.TARGET, ls=":", lw=1.2)
        a.set_xlabel("frame"); a.set_ylabel("attention to quadrant"); a.set_title(tit, fontsize=14.5)
        a.legend(fontsize=11.5)
    save(fig, "attn_quad_timecourse")


# ── 5. value reshapes the filter (red vs blue) ────────────────────────────────
def fig_value_attention():
    d = load("maps_summary.npz"); CT, DT = int(d["CT"]), int(d["DT"])
    red, blue = "cue-left_red_+distractor_sal", "cue-left_BLUE_+distractor_sal"
    T = d[red].shape[0]; tt = np.arange(T)
    def q(key, qd): return d[key][:, QI[qd]].sum(1)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.0))
    ax[0].plot(tt, q(red, 0), color=S.REWARD["red"], label="red ($v=5$) → target quad")
    ax[0].plot(tt, q(blue, 0), color=S.REWARD["blue"], label="blue ($v=1$) → target quad")
    ax[0].axvline(CT, color="#444", ls=":", lw=1.2)
    ax[0].set_xlabel("frame"); ax[0].set_ylabel("priority attention to target quad")
    ax[0].set_title("A  High value → sharp target-locked filter"); ax[0].legend()
    ax[1].plot(tt, q(red, 2), color=S.REWARD["red"], label="red ($v=5$) → distractor quad")
    ax[1].plot(tt, q(blue, 2), color=S.REWARD["blue"], label="blue ($v=1$) → distractor quad")
    ax[1].axvline(DT, color="#444", ls=":", lw=1.2)
    ax[1].set_xlabel("frame"); ax[1].set_ylabel("priority attention to distractor quad")
    ax[1].set_title("B  Low value → filter leaks onto distractor"); ax[1].legend()
    save(fig, "value_attention")


# ── 6. value-graded (engage-gated) ────────────────────────────────────────────
def fig_value_graded():
    d = load("value_graded_summary.npz"); sharp, leak = d["sharp"], d["leak"]
    cc = [S.REWARD["red"], S.REWARD["green"], S.REWARD["blue"]]
    lab = ["red\n($v$=5, engaged)", "green\n($v$=3, engaged)", "blue\n($v$=1, abandoned)"]
    x = [0, 1, 2]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    for a, y, tit, yl in [(ax[0], sharp, "A  Sharp filter on engaged colours, collapses on blue", "priority attn to target quad"),
                          (ax[1], leak, "B  Distractor leak only on abandoned blue", "priority attn to distractor quad")]:
        a.plot(x, y, "-", color="#999", zorder=1); a.scatter(x, y, c=cc, s=240, zorder=2, edgecolor="k", linewidth=1.2)
        a.set_xticks(x); a.set_xticklabels(lab); a.set_ylabel(yl + "\n(peri-change)"); a.set_ylim(bottom=0)
        a.set_title(tit, fontsize=14)
    save(fig, "value_graded")


# ── 7. single-timepoint decoding ──────────────────────────────────────────────
def fig_decoding():
    d = load("decoding_summary.npz")
    tasks = ["target location (4-way)", "distractor location (4-way)", "distractor present (binary)",
             "cue colour / value (3-way)", "cue side (binary)"]
    streams = [("z_sal (actor)", "priority stream", S.PRIORITY),
               ("z_td (critic)", "value stream", S.VALUE),
               ("H1 (sensory)", "sensory memory", "#74a9cf"),
               ("H2 (deep)", "deep memory", "#fdae6b")]
    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    x = np.arange(len(tasks)); w = 0.2
    for j, (skey, slab, col) in enumerate(streams):
        vals = [float(d[f"{tk}|{skey}"][0]) for tk in tasks]
        ax.bar(x + (j-1.5)*w, vals, w, label=slab, color=col, edgecolor="k", lw=.5)
    for i, tk in enumerate(tasks):
        ch = float(d[f"{tk}|z_sal (actor)"][2]); ax.hlines(ch, i-0.45, i+0.45, color="k", ls="--", lw=1)
    ax.set_xticks(x); ax.set_xticklabels([t.replace(" (", "\n(") for t in tasks], fontsize=12.5)
    ax.set_ylabel("decoding balanced accuracy"); ax.set_ylim(0, 1.05)
    ax.set_title("Linear decoding from each pathway / memory (2 frames after change)")
    ax.legend(ncol=2, loc="upper right")
    save(fig, "decoding")


# ── 8. temporal decoding ──────────────────────────────────────────────────────
def fig_temporal_decoding():
    d = load("temporal_decoding_summary.npz"); ts = d["ts"]; CT, DT = 17, 13
    cols = {"cue colour (value)": "#6a51a3", "cue side": "#9e9ac8", "target location": S.TARGET,
            "distractor present": "#fb6a4a", "distractor location": S.DISTRACT}
    chance = {"cue colour (value)": .333, "cue side": .5, "target location": .25,
              "distractor present": .5, "distractor location": .25}
    fig, ax = plt.subplots(1, 2, figsize=(15.5, 5.4))
    for v, c in cols.items():
        ax[0].plot(ts, d[f"zsal_{v.replace(' ','_')}"], "-o", ms=4, color=c, label=v)
        ax[0].axhline(chance[v], color=c, ls=":", lw=.7, alpha=.5)
    ax[0].axvline(DT, color=S.DISTRACT, ls="--", lw=1); ax[0].axvline(CT, color=S.TARGET, ls="--", lw=1)
    ax[0].set_xlabel("frame"); ax[0].set_ylabel("decoding balanced accuracy"); ax[0].set_ylim(0, 1.05)
    ax[0].set_title("A  Temporal decoding from the priority stream"); ax[0].legend(loc="center left", fontsize=11)
    ax[1].plot(ts, d["zsal_target_location"], "-o", ms=4, color=S.TARGET, label="target — priority stream")
    ax[1].plot(ts, d["ztd_target_location"], "--o", ms=4, color="#74c476", label="target — value stream")
    ax[1].plot(ts, d["zsal_distractor_location"], "-s", ms=4, color=S.DISTRACT, label="distractor — priority stream")
    ax[1].plot(ts, d["ztd_distractor_location"], "--s", ms=4, color="#fc9272", label="distractor — value stream")
    ax[1].axhline(.25, color="k", ls=":", lw=.7); ax[1].axvline(DT, color=S.DISTRACT, ls="--", lw=1)
    ax[1].axvline(CT, color=S.TARGET, ls="--", lw=1)
    ax[1].set_xlabel("frame"); ax[1].set_ylabel("location decoding accuracy"); ax[1].set_ylim(0, 1.05)
    ax[1].set_title("B  Distractor stays weak in the priority stream"); ax[1].legend(fontsize=11)
    save(fig, "temporal_decoding")


# ── 9. causal battery ─────────────────────────────────────────────────────────
def fig_causal_battery():
    d = load("causal_battery_summary.npz"); B = d["biases"]; i0 = list(B).index(0)
    levers = [("priority_at_cued-primary", "priority @ cued-primary", S.PRIORITY, "-o"),
              ("priority_at_distractor",   "priority @ distractor",   S.DISTRACT, "-s"),
              ("priority_at_cued-secondary","priority @ cued-secondary","#74a9cf", "-^"),
              ("value_at_cued-primary",    "value @ cued-primary",    S.VALUE, "--o"),
              ("value_at_distractor",      "value @ distractor",      "#c39bd3", "--s")]
    def get(lever, k):
        # caches were written with the old lever names (salience/top-down)
        old = lever.replace("priority", "salience").replace("value", "top-down")
        return d[f"{old}_{k}"]
    fig, ax = plt.subplots(1, 3, figsize=(16.5, 5.2))
    for key, lab, col, st in levers:
        ax[0].plot(B, get(key, "hit") - get(key, "hit")[i0], st, color=col, label=lab, ms=6)
    ax[0].axhline(0, color="k", lw=.7); ax[0].set_xlabel("injected attention bias (logits)")
    ax[0].set_ylabel("Δ hit rate (decision)"); ax[0].set_title("A  Decision lever"); ax[0].legend(fontsize=11)
    for key, lab, col, st in levers:
        ax[1].plot(B, get(key, "unc") - get(key, "unc")[i0], st, color=col, ms=6)
    ax[1].axhline(0, color="k", lw=.7); ax[1].set_xlabel("injected attention bias (logits)")
    ax[1].set_ylabel("Δ outcome uncertainty (value)"); ax[1].set_title("B  Value / uncertainty lever")
    ax[2].plot(B, get("priority_at_distractor", "fa"), "-s", color=S.FA, label="false-alarm rate", ms=6)
    ax[2].plot(B, get("priority_at_distractor", "hit"), "-o", color=S.HIT, label="hit rate", ms=6)
    ax[2].set_xlabel("distractor-side priority bias"); ax[2].set_ylabel("rate (engaged trials)")
    ax[2].set_ylim(0, 1); ax[2].set_title("C  Forcing distractor attention"); ax[2].legend()
    save(fig, "causal_battery")


# ── 10. critic / value ────────────────────────────────────────────────────────
def fig_value():
    d = load("value_summary.npz"); lags = d["lags"]
    rv = {"red": 5, "green": 3, "blue": 1}
    fig, ax = plt.subplots(1, 3, figsize=(16, 5.0))
    for c in ["red", "green", "blue"]:
        ax[0].plot(lags, d[f"val_{c}"], "-o", ms=4, color=S.REWARD[c], label=f"{c} ($v$={rv[c]})")
    ax[0].axvline(0, color="k", ls=":", lw=1); ax[0].set_xlabel("frames from change")
    ax[0].set_ylabel("state value"); ax[0].set_title("A  Value preserves reward order"); ax[0].legend()
    for c in ["red", "green", "blue"]:
        ax[1].plot(lags, d[f"adv_{c}"], "-o", ms=4, color=S.REWARD[c], label=c)
    ax[1].axhline(0, color="k", ls="--", lw=.9); ax[1].axvline(0, color="k", ls=":", lw=1)
    ax[1].set_xlabel("frames from change"); ax[1].set_ylabel("press − wait advantage")
    ax[1].set_title("B  Pressing never worth it for blue"); ax[1].legend()
    slope, r2 = float(d["slope"]), float(d["r2"])
    xx = np.linspace(0, 5, 50)
    ax[2].plot(xx, slope*xx, color=S.VALUE, lw=2.5, label=f"slope {slope:.2f}, $R^2$={r2:.2f}")
    ax[2].plot(xx, xx, "k--", lw=1, label="identity")
    ax[2].set_xlabel("predicted value"); ax[2].set_ylabel("realised return")
    ax[2].set_title("C  Critic calibration"); ax[2].legend()
    save(fig, "value")


# ── 11. supplementary timing ──────────────────────────────────────────────────
def fig_supp_timing():
    t = load("behavior_trials.npz")
    color = t["color"].astype(str); ct = t["ct"].astype(bool); hit = t["hit"]; eng = t["engaged"].astype(bool)
    pidx = t["pidx"]; rt = t["rt"]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.0))
    rte = rt[hit & eng]; rte = rte[~np.isnan(rte)]
    ax[0].hist(rte, bins=np.arange(-0.5, 10.5, 1), color=S.PRIORITY, edgecolor="k", lw=.5)
    ax[0].axvline(np.median(rte), color="k", ls="--", lw=1.4)
    ax[0].set_xlabel("reaction time (frames after change)"); ax[0].set_ylabel("count of hits")
    ax[0].set_title(f"A  Hit RT (engaged), median {np.median(rte):.0f} frame" + ("s" if np.median(rte)!=1 else ""))
    for c in ["red", "green", "blue"]:
        m = ct & (color == c) & (pidx >= 0)
        ax[1].hist(pidx[m], bins=np.arange(-0.5, 29.5, 1), histtype="step", lw=2.2, color=S.REWARD[c], label=c, density=True)
    ax[1].axvspan(11, 25, color="#e8e8e8", zorder=0); ax[1].text(18, ax[1].get_ylim()[1]*0.92, "target-change\nwindow", ha="center", fontsize=11)
    ax[1].set_xlabel("press frame"); ax[1].set_ylabel("density of presses")
    ax[1].set_title("B  Blue bails immediately ($t\\approx2$)"); ax[1].legend()
    save(fig, "supp_timing")


if __name__ == "__main__":
    print("regenerating figures:")
    fig_behavior()
    fig_maps("sal", "Priority stream spatial attention (drives the decision)", "maps_priority")
    fig_maps("td", "Value stream spatial attention (drives valuation)", "maps_value")
    fig_quad_timecourse()
    fig_value_attention()
    fig_value_graded()
    fig_decoding()
    fig_temporal_decoding()
    fig_causal_battery()
    fig_value()
    fig_supp_timing()
    print("done.")
