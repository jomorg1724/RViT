"""Torch-free renderer: alpha_1 line plots + per-colour attention-map super-figures, from attn.npz."""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "axes.spines.top": False, "axes.spines.right": False})
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
d = np.load(os.path.join(FIGS, "attn.npz"))
PROPS = [0.25, 0.5, 0.75, 1.0]; T = 7
VAL = {"red": 5, "green": 3, "blue": 1}

# alpha_1 over time, per validity, 2x2 (task x variant)
fig, ax = plt.subplots(2, 2, figsize=(9, 7))
for i, task in enumerate(("vda1", "vda4")):
    for j, fb in enumerate(("crossattn1", "affine_ew")):
        a = ax[i, j]
        for k, p in enumerate(PROPS):
            al = d[f"{task}_{fb}_red_p{p}_alpha"][:, 0]
            a.plot(range(T), al, "-o", ms=4, color=plt.cm.viridis(k / 3), label=f"V={int(p*100)}%")
        a.axhline(0.25, ls=":", c="gray"); a.axvline(1, ls=":", c="g"); a.axvline(5, ls=":", c="r")
        a.set_title(f"{task} · {fb}", fontsize=10); a.set_ylim(0.1, 0.9)
        a.set_xlabel("timestep"); a.set_ylabel(r"$\alpha_1$ (cued TL)")
        if i == 0 and j == 0:
            a.legend(fontsize=7, title="validity")
fig.suptitle(r"$\alpha_1$: attention on the cued patch (red cue).  green=cue(t1), red=change(t5), gray=uniform(0.25)")
fig.tight_layout(); fig.savefig(os.path.join(FIGS, "alpha1_lines.png"), dpi=140, bbox_inches="tight"); plt.close(fig)

# per-colour super-figure (rows=validity, cols=time), flagship = vda4 crossattn1
for color in ("red", "green", "blue"):
    fig, ax = plt.subplots(4, 7, figsize=(11, 6.6))
    for r, p in enumerate(PROPS):
        al = d[f"vda4_crossattn1_{color}_p{p}_alpha"]                  # (7,4)
        for t in range(7):
            ax[r, t].imshow(al[t].reshape(2, 2), cmap="Purples", vmin=0, vmax=0.8)
            ax[r, t].set_xticks([]); ax[r, t].set_yticks([])
            if r == 0:
                ax[r, t].set_title(f"t{t}" + ("·cue" if t == 1 else "·chg" if t == 5 else ""), fontsize=8)
        ax[r, 0].set_ylabel(f"V={int(p*100)}%", fontsize=10)
    fig.suptitle(f"vda4 · crossattn1 · {color} cue (value {VAL[color]}) — attention maps [no-change, cue TL]  "
                 r"cell layout [[S1,TR],[BL,S4]]", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(FIGS, f"super_vda4_crossattn1_{color}.png"), dpi=130,
                                    bbox_inches="tight"); plt.close(fig)
print("rendered:", os.listdir(FIGS))
