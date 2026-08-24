"""VDA attention maps + alpha_1, for the set-size sweep (vda1 vs vda4, both variants). No-change trials,
cue at TL, every colour (red/green/blue = value 5/3/1) × every validity/proportion → the per-timestep
2x2 attention map. Feeds the per-colour 4x7 (proportion×time) super-figures and the alpha_1 line plots.
Compute -> npz; a torch-free figure script renders. Run on MPS/CPU."""
import os, numpy as np, vda_core as C

COLORS = ["red", "green", "blue"]
PROPS = [0.25, 0.5, 0.75, 1.0]
B = 96


def main():
    out = {}
    for task in ("vda1", "vda2", "vda4", "vda9", "vda16"):
        for fb in ("crossattn1", "affine_ew"):
            m, it = C.load(task, fb, 128); out[f"{task}_{fb}_iter"] = it
            print(f"[attn] {task} {fb} iter={it}", flush=True)
            for color in COLORS:
                for prop in PROPS:
                    a = C.attn_maps(m, task, C.TL, prop, color, 0, -1, B=B)     # (7,4,K) no-change, cue TL
                    out[f"{task}_{fb}_{color}_p{prop}_map"] = a                 # raw map for the super-figure
                    out[f"{task}_{fb}_{color}_p{prop}_alpha"] = C.loc_attn(a)   # (7,4) per-location alpha
    np.savez(os.path.join(C.FIGS, "attn.npz"), **out)
    print(f"[attn] saved -> {os.path.join(C.FIGS, 'attn.npz')}", flush=True)


if __name__ == "__main__":
    main()
