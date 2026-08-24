"""Regenerate fig_sdt_by_setsize.png from sdt.npz with ONE consistent effect convention.

Effect magnitude = the clamp DYNAMIC RANGE (max - min of the SDT quantity over the attention
clamp sweep alpha in {0,.25,.5,.75,1}); applied identically to criterion c and sensitivity d'.
This matches the panel's own y-label ('clamp range') and removes the earlier mixed convention
(d' as max-min but c as endpoint). Numbers land: sensitivity 1.98/1.65/1.13/0.37 (monotone down),
criterion 1.02/1.38/1.62/1.05 (inverted-U, peak set size 4). Torch-free; reads sdt.npz."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
NPZ  = os.path.join(HERE, "figs", "sdt.npz")
OUT  = "/Users/jonathanmorgan/AttentionManuscript/reports/upgraded_paper/manuscript/figures"
TASKS  = ["vda1", "vda2", "vda4", "vda9"]
LABELS = ["set size 1", "set size 2", "set size 4", "set size 9"]


def main():
    d = np.load(NPZ, allow_pickle=True)
    A = np.asarray(d["ALPHAS"])
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(TASKS)))
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4.2))

    crit_eff, sens_eff = [], []
    for k, t in enumerate(TASKS):
        c  = np.asarray(d[f"{t}_affine_ew_c"])
        dp = np.asarray(d[f"{t}_affine_ew_d"])
        ax[0].plot(A, c,  "-o", color=cmap[k], label=LABELS[k])
        ax[1].plot(A, dp, "-o", color=cmap[k], label=LABELS[k])
        crit_eff.append(c.max() - c.min())      # consistent: clamp dynamic range
        sens_eff.append(dp.max() - dp.min())

    ax[0].axhline(0, color="gray", lw=0.8)
    ax[0].set_xlabel(r"attention clamp $\alpha_c$"); ax[0].set_ylabel("criterion $c$")
    ax[0].set_title(r"Attention $\rightarrow$ criterion"); ax[0].legend(fontsize=8, frameon=False)
    ax[1].set_xlabel(r"attention clamp $\alpha_c$"); ax[1].set_ylabel("sensitivity $d'$")
    ax[1].set_title(r"Attention $\rightarrow$ sensitivity")

    x = np.arange(len(TASKS)); w = 0.38
    ax[2].bar(x - w/2, crit_eff, w, color="#c0392b", label=r"criterion effect ($\Delta c$)")
    ax[2].bar(x + w/2, sens_eff, w, color="#2980b9", label=r"sensitivity effect ($\Delta d'$)")
    ax[2].set_xticks(x); ax[2].set_xticklabels(["ss1", "ss2", "ss4", "ss9"])
    ax[2].set_ylabel("effect magnitude (clamp dynamic range)")
    ax[2].set_title("Both effects vs set size"); ax[2].legend(fontsize=8, frameon=False)

    fig.tight_layout()
    p = os.path.join(OUT, "fig_sdt_by_setsize.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    print("wrote", p)
    print("criterion effect (max-min):", [round(v, 2) for v in crit_eff])
    print("sensitivity effect (max-min):", [round(v, 2) for v in sens_eff])


if __name__ == "__main__":
    main()
