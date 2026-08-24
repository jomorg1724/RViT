"""Render the two attention-level figures for the VDA battery section, torch-free, from attn.npz:
  (1) fig_attn_maps.png     — per-environment spatial attention map across the 7 trial frames,
                              EACH IN ITS NATIVE GRID: vda1/2/4 are 2x2 (4 patches), vda9 is 3x3
                              (9 patches). Value- and validity-averaged. The literal 'attention map'.
  (2) fig_attn_value_validity.png — cued-location attention vs cue VALUE (red/green/blue = 5/3/1) and
                              vs cue VALIDITY (proportion), one curve per environment, with the
                              per-grid uniform baseline (0.25 for 2x2, 1/9 for the 3x3 vda9).
Alphas re-derived by the FIXED loc_attn (uses the real patch count, so vda9 keeps all 9 locations).
Cued loc = token 0 (top-left) in every grid. All numbers audited from vda_sweep/figs/attn.npz."""
import os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
NPZ  = os.path.join(HERE, "figs", "attn.npz")
OUT  = "/Users/jonathanmorgan/AttentionManuscript/reports/upgraded_paper/manuscript/figures"

TASKS  = ["vda1", "vda2", "vda4", "vda9"]
LABELS = {"vda1": "set size 1", "vda2": "set size 2", "vda4": "set size 4", "vda9": "set size 9"}
GRIDSHAPE = {"vda1": (2, 2), "vda2": (2, 2), "vda4": (2, 2), "vda9": (3, 3)}   # native attention grid
NPATCH = {t: r * c for t, (r, c) in GRIDSHAPE.items()}
COLORS = ["red", "green", "blue"]           # value 5 / 3 / 1
PROPS  = [0.25, 0.5, 0.75, 1.0]
CUED   = 0                                   # token 0 = top-left = cued cell


def alpha(d, task, color, prop):
    return d[f"{task}_affine_ew_{color}_p{prop}_alpha"]      # (7, n_patch)


def fig_maps(d):
    """4 envs (rows) x 7 frames (cols): the spatial attention map in each env's NATIVE grid."""
    fig, axes = plt.subplots(len(TASKS), 7, figsize=(11.0, 6.6))
    grid = {t: np.mean([alpha(d, t, c, p) for c in COLORS for p in PROPS], axis=0) for t in TASKS}  # (7,n)
    vmax = float(max(g.max() for g in grid.values()))
    for r, task in enumerate(TASKS):
        stack, (gr, gc) = grid[task], GRIDSHAPE[task]
        for t in range(7):
            ax = axes[r, t]
            im = ax.imshow(stack[t].reshape(gr, gc), cmap="magma", vmin=0.0, vmax=vmax)
            ax.set_xticks([]); ax.set_yticks([])
            ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, 1, fill=False, ec="cyan", lw=1.8))  # cued cell (TL)
            if r == 0:
                ax.set_title(f"$t_{t}$", fontsize=10)
            if t == 0:
                ax.set_ylabel(f"{LABELS[task]}\n({gr}$\\times${gc}, unif={1/NPATCH[task]:.2f})", fontsize=9)
    fig.suptitle("Spatial attention map across the trial, each env in its native grid "
                 "(cyan = cued cell; value- and validity-averaged)", fontsize=11, y=0.98)
    cax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    fig.colorbar(im, cax=cax, label="attention weight")
    fig.tight_layout(rect=[0, 0, 0.91, 0.95])
    p = os.path.join(OUT, "fig_attn_maps.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    print("wrote", p)


def fig_value_validity(d):
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.2))
    cmap = plt.cm.viridis(np.linspace(0.15, 0.85, len(TASKS)))

    axA = axes[0]
    for k, task in enumerate(TASKS):
        y = [np.mean([alpha(d, task, c, p)[1:, CUED].mean() for p in PROPS]) for c in COLORS]
        axA.plot([5, 3, 1], y, "-o", color=cmap[k], label=LABELS[task])
    axA.axhline(0.25, ls=":", color="gray", lw=1); axA.axhline(1/9, ls=":", color="darkred", lw=1)
    axA.text(1.02, 0.25, "unif 2$\\times$2", color="gray", fontsize=7, va="bottom")
    axA.text(1.02, 1/9, "unif 3$\\times$3", color="darkred", fontsize=7, va="bottom")
    axA.set_xticks([1, 3, 5]); axA.invert_xaxis()
    axA.set_xlabel("cue value (reward level)"); axA.set_ylabel(r"attention on cued location $\alpha_c$")
    axA.set_title("Value does not steer the priority map"); axA.legend(fontsize=8, frameon=False)

    axB = axes[1]
    for k, task in enumerate(TASKS):
        y = [np.mean([alpha(d, task, c, p)[1:, CUED].mean() for c in COLORS]) for p in PROPS]
        axB.plot([25, 50, 75, 100], y, "-o", color=cmap[k], label=LABELS[task])
    axB.axhline(0.25, ls=":", color="gray", lw=1); axB.axhline(1/9, ls=":", color="darkred", lw=1)
    axB.set_xlabel("displayed cue validity (%)"); axB.set_ylabel(r"attention on cued location $\alpha_c$")
    axB.set_title("Validity steers the map only at high load"); axB.legend(fontsize=8, frameon=False)

    fig.tight_layout()
    p = os.path.join(OUT, "fig_attn_value_validity.png")
    fig.savefig(p, dpi=150); plt.close(fig)
    print("wrote", p)


def main():
    d = np.load(NPZ, allow_pickle=True)
    fig_maps(d)
    fig_value_validity(d)


if __name__ == "__main__":
    main()
