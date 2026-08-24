"""Reproduction test for Baruni, Lau & Salzman (2015): is the trained baruni model's discrimination
controlled by RELATIVE value (LS > LL ~ SS > SL) — and does attention track value? Compute -> npz."""
import os, numpy as np, baruni_core as C


def main():
    out = {}
    for fb in ("crossattn1", "affine_ew"):
        m, it = C.load(fb); out[f"{fb}_iter"] = it
        print(f"[baruni] {fb} iter={it}", flush=True)
        for tilt in (4.0, 6.0, 8.0):     # span sensitive->ceiling so the relative-value effect is visible
            for name, (vq, vd) in C.PAIRS.items():
                b = C.behavior(m, vq, vd, tilt=tilt, B=300)
                out[f"{fb}_t{tilt:.0f}_{name}_acc"] = b["acc"]
                out[f"{fb}_t{tilt:.0f}_{name}_declare"] = b["declare"]
                out[f"{fb}_t{tilt:.0f}_{name}_rt"] = b["rt"]
                print(f"   t{tilt:.0f} {name} (q{vq:.0f}/d{vd:.0f}): "
                      f"acc={b['acc']:.3f} declare={b['declare']:.2f} rt={b['rt']:.1f}", flush=True)
        # attention by value: LS condition (queried HIGH, distractor LOW) -> alpha on high vs low cell
        aH, aL = C.attn_by_cell(m, C.V_L, C.V_S, C.ACTIVE[0])
        out[f"{fb}_attn_high"] = aH; out[f"{fb}_attn_low"] = aL
        print(f"   attn on high-value cell: cue(t1)={aH[1]:.3f} stim(t3-7)={aH[3:8].mean():.3f} | "
              f"low-value cell: cue(t1)={aL[1]:.3f} stim(t3-7)={aL[3:8].mean():.3f}", flush=True)
    np.savez(os.path.join(C.FIGS, "baruni_repro.npz"), **out)
    print(f"[baruni] saved -> {os.path.join(C.FIGS, 'baruni_repro.npz')}", flush=True)


if __name__ == "__main__":
    main()
