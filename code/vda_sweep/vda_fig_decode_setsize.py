"""Regenerate fig_decode_by_setsize.png from decode.npz, adding the VALUE (colour) decode overlay.
Left: per-frame validity decoding, one solid curve per set size, plus the value/colour decode
(pinned at 1.0 for every set size) as a single dashed reference line -> the visual contrast that
value is always maintained while validity decays unless load is high. Right: peak and maintained
validity decoding vs set size. Torch-free; reads decode.npz. Chance = 0.25."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
NPZ  = os.path.join(HERE, "figs", "decode.npz")
OUT  = "/Users/jonathanmorgan/AttentionManuscript/reports/upgraded_paper/manuscript/figures"
TASKS  = ["vda1", "vda2", "vda4", "vda9"]
LABELS = ["set size 1", "set size 2", "set size 4", "set size 9"]
SS     = [1, 2, 4, 9]


def main():
    d = np.load(NPZ, allow_pickle=True)
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(TASKS)))
    fig, ax = plt.subplots(1, 2, figsize=(12.0, 4.4))
    T = np.arange(7)

    peak, maint = [], []
    value_curves = []
    for k, t in enumerate(TASKS):
        v = np.asarray(d[f"{t}_affine_ew_validity"])
        col = np.asarray(d[f"{t}_affine_ew_colour"])
        ax[0].plot(T, v, "-o", color=cmap[k], label=LABELS[k])
        value_curves.append(col)
        peak.append(v.max()); maint.append(v[2:].mean())
    # value (colour) decode is ~1.0 for every set size -> one dashed reference line
    val_mean = np.mean(value_curves, axis=0)
    ax[0].plot(T, val_mean, "--", color="black", lw=1.6, label="value (all set sizes)")
    ax[0].axhline(0.25, ls=":", color="gray", lw=1, label="chance")
    ax[0].set_xlabel("frame"); ax[0].set_ylabel("decode (balanced acc.)")
    ax[0].set_title("Value is always held; validity is held\nmore, and longer, only at higher set size",
                    fontsize=11)
    ax[0].legend(fontsize=8, frameon=False, ncol=1)

    ax[1].plot(SS, peak,  "-o", color="#c0392b", label="validity: peak (at cue)")
    ax[1].plot(SS, maint, "--s", color="#2980b9", label="validity: maintained (mean $t_2$-$t_6$)")
    ax[1].axhline(1.0, ls="--", color="black", lw=1.2, label="value: peak & maintained")
    ax[1].axhline(0.25, ls=":", color="gray", lw=1)
    ax[1].set_xticks(SS); ax[1].set_xlabel("set size"); ax[1].set_ylabel("decode (balanced acc.)")
    ax[1].set_title("Validity encoding scales with set size", fontsize=11)
    ax[1].legend(fontsize=8, frameon=False)

    fig.tight_layout()
    p = os.path.join(OUT, "fig_decode_by_setsize.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    print("wrote", p)
    print("validity peak:", [round(x, 2) for x in peak], " maintained:", [round(x, 2) for x in maint])


if __name__ == "__main__":
    main()
