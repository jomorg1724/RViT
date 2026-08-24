"""Value modulates the spatial filter. From the forced-trial attention maps we plot
the salience-stream attention to the target quadrant and to the distractor quadrant
over the trial, for a high-value (red) versus a low-value (blue) cue — same stimulus,
same cue side, same target/distractor locations. High value buys a sharp, target-
locked filter that holds the distractor near zero; low value gives a diffuse read that
leaks onto the distractor."""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from RViT_plus_v11_part5.analysis import distractor_dd as dd

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
d = np.load(f"{OUT}/maps_summary.npz")
qi = dd.quadrant_token_indices()
CT, DT = int(d["CT"]), int(d["DT"])
red, blue = "cue-left_red_+distractor_sal", "cue-left_BLUE_+distractor_sal"
T = d[red].shape[0]; tt = np.arange(T)
def quad(key, q): return d[key][:, qi[q]].sum(1)   # (T,)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
ax[0].plot(tt, quad(red, 0), "-", color="#d62728", lw=2.2, label="red (v=5) → target quad")
ax[0].plot(tt, quad(blue, 0), "-", color="#1f77b4", lw=2.2, label="blue (v=1) → target quad")
ax[0].axvline(DT, color="#888", ls=":", lw=1); ax[0].axvline(CT, color="#444", ls=":", lw=1)
ax[0].text(CT+.2, ax[0].get_ylim()[1]*0.93, "target", fontsize=8)
ax[0].set_xlabel("frame"); ax[0].set_ylabel("salience attention to target quad")
ax[0].set_title("A  High value → sharp target-locked filter", loc="left", fontweight="bold")
ax[0].legend(fontsize=8, frameon=False)
ax[1].plot(tt, quad(red, 2), "-", color="#d62728", lw=2.2, label="red (v=5) → distractor quad")
ax[1].plot(tt, quad(blue, 2), "-", color="#1f77b4", lw=2.2, label="blue (v=1) → distractor quad")
ax[1].axvline(DT, color="#888", ls=":", lw=1); ax[1].text(DT+.2, ax[1].get_ylim()[1]*0.9, "distractor on", fontsize=8)
ax[1].set_xlabel("frame"); ax[1].set_ylabel("salience attention to distractor quad")
ax[1].set_title("B  Low value → filter leaks onto the distractor", loc="left", fontweight="bold")
ax[1].legend(fontsize=8, frameon=False)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/value_attention.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/value_attention.pdf", bbox_inches="tight")
print("saved value_attention.png")
print(f"  target quad peak: red={quad(red,0).max():.3f} blue={quad(blue,0).max():.3f}")
print(f"  distractor quad (post-onset mean t={DT}-{CT+2}): red={quad(red,2)[DT:CT+2].mean():.3f} "
      f"blue={quad(blue,2)[DT:CT+2].mean():.3f}")
