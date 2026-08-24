"""Render the matched-family analysis into two publication figures for the thesis.
Reads variant_analysis.npz (no model loading). Writes PDFs into reports/thesis/figures/."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.titlesize": 9,
    "axes.labelsize": 9, "legend.fontsize": 7.5, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150,
})

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPZ = os.path.join(HERE, "analysis", "deepdive_out", "variant_analysis.npz")
FIGDIR = os.path.join(HERE, "..", "reports", "thesis", "figures")
LABEL = {"standard": "multiplicative", "affine": "affine", "dualhead": "dual-head",
         "two_lstm": "two-LSTM", "crossattn": "cross-attn", "dualmem": "dual-mem"}
COL = {"standard": "#444444", "affine": "#1b9e77", "dualhead": "#d95f02",
       "two_lstm": "#7570b3", "crossattn": "#e7298a", "dualmem": "#66a61e"}

d = np.load(NPZ, allow_pickle=True)
rows = list(d["rows"]); S1 = d["S1"].item()
order = [r[0] for r in rows]
T = 7; frames = np.arange(T)

# --- Figure 1: cued-patch attention timecourse (no-change) + orienting/spike bars ---
fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(7.2, 3.0))
for name in order:
    ax0.plot(frames, S1[name]["nochange_cued"], "-o", ms=3, lw=1.4,
             color=COL[name], label=LABEL[name])
ax0.axhline(0.25, ls=":", c="k", lw=0.8)
ax0.text(0.05, 0.255, "uniform (0.25)", fontsize=6.5, va="bottom")
ax0.axvline(1, ls="--", c="0.6", lw=0.8); ax0.text(1.05, ax0.get_ylim()[1], "cue", fontsize=6.5, va="top")
ax0.axvline(5, ls="--", c="0.6", lw=0.8); ax0.text(5.05, ax0.get_ylim()[1], "(change frame)", fontsize=6.5, va="top")
ax0.set_xlabel("frame"); ax0.set_ylabel("attention to cued patch")
ax0.set_title("Cue-orienting (no-change, 100% cue)")
ax0.legend(loc="upper left", frameon=False, ncol=2)

orient = np.array([float(r[6]) for r in rows]); spike = np.array([float(r[7]) for r in rows])
x = np.arange(len(order)); w = 0.38
ax1.bar(x - w/2, orient, w, color=[COL[n] for n in order], label="cue-orient (t3–4)")
ax1.bar(x + w/2, spike, w, color=[COL[n] for n in order], alpha=0.45, hatch="//", label="change-spike (t5)")
ax1.axhline(0, c="k", lw=0.8)
ax1.set_xticks(x); ax1.set_xticklabels([LABEL[n] for n in order], rotation=30, ha="right")
ax1.set_ylabel("attention above uniform")
ax1.set_title("Orienting vs. change-locking")
ax1.legend(frameon=False, loc="upper right")
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, "fig_variants_attention.pdf"), bbox_inches="tight")
print("wrote fig_variants_attention.pdf")

# --- Figure 2: behaviour (correct / hit / FA) ---
fig2, ax = plt.subplots(figsize=(4.6, 3.0))
correct = np.array([float(r[2]) for r in rows]); hit = np.array([float(r[3]) for r in rows])
fa = np.array([float(r[4]) for r in rows])
w = 0.27
ax.bar(x - w, correct, w, label="correct", color="#4c72b0")
ax.bar(x, hit, w, label="hit", color="#55a868")
ax.bar(x + w, fa, w, label="false alarm", color="#c44e52")
ax.axhline(0.5, ls=":", c="k", lw=0.8); ax.text(len(order)-0.5, 0.51, "chance", fontsize=6.5, ha="right")
ax.set_xticks(x); ax.set_xticklabels([LABEL[n] for n in order], rotation=30, ha="right")
ax.set_ylabel("rate"); ax.set_ylim(0, 1.05)
ax.set_title("Behaviour on validity4 (T=7, greedy)")
ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.02))
fig2.tight_layout(); fig2.savefig(os.path.join(FIGDIR, "fig_variants_behavior.pdf"), bbox_inches="tight")
print("wrote fig_variants_behavior.pdf")
