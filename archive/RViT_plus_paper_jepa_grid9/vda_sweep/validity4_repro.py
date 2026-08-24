"""Validity4 reproduction — pure SPATIAL validity (a ring whose completeness = validity = P(change at cued)),
NO value colour. The clean complement to the value-VDA (which perceived-then-discarded validity): here,
with no competing value cue, does the model USE validity? Measure cued vs uncued detection and cued-patch
attention α₁ as a function of validity (ring completeness), per variant. crossattn1 vs affine_ew. MPS/CPU."""
import os, numpy as np
import vda_core as C
from krauzlis_repro import load_k

PROPS = [0.25, 0.5, 0.75, 1.0]                  # validity (ring completeness)
MAGS = [18.0, 26.0]                             # near-threshold magnitudes (where validity should bite)


def hit(m, ci, prop, mag, ct=1, B=250):
    p = C.press_times(m, "validity4", C.TL, prop, "red", ct, ci, mag, B=B)
    return float((p >= 5).mean())


def alpha1(m, prop, B=96):
    a = C.attn_maps(m, "validity4", C.TL, prop, "red", 0, -1, MAGS[-1], B=B)   # no-change trials
    return C.loc_attn(a)[:, C.TL].max()                                        # peak cued-patch attention


def main():
    out = {"PROPS": np.array(PROPS), "MAGS": np.array(MAGS)}
    for fb in ("crossattn1", "affine_ew"):
        m, it = load_k("validity4", fb)
        print(f"=== validity4 {fb} (iter {it}) — validity (ring completeness) sweep ===")
        hc26 = [hit(m, C.TL, p, 26.0) for p in PROPS]     # cued detection @ mag26
        hu26 = [hit(m, C.BR, p, 26.0) for p in PROPS]     # uncued detection @ mag26
        hc18 = [hit(m, C.TL, p, 18.0) for p in PROPS]     # cued detection @ mag18 (harder)
        a1 = [alpha1(m, p) for p in PROPS]                # cued-patch attention vs validity
        ben = np.array(hc26) - np.array(hu26)
        out[f"{fb}_cued26"] = np.array(hc26); out[f"{fb}_uncued26"] = np.array(hu26)
        out[f"{fb}_cued18"] = np.array(hc18); out[f"{fb}_alpha1"] = np.array(a1)
        print(f"  cued  det @mag26 = {['%.2f'%x for x in hc26]}   (validity 25→100%)")
        print(f"  uncued det @mag26= {['%.2f'%x for x in hu26]}")
        print(f"  cued−uncued BENEFIT = {['%.2f'%x for x in ben]}")
        print(f"  cued  det @mag18 = {['%.2f'%x for x in hc18]}   (harder)")
        print(f"  α₁ cued attention = {['%.2f'%x for x in a1]}   (uniform=0.25)", flush=True)
    np.savez(os.path.join(C.FIGS, "validity4.npz"), **out)
    print("[validity4] saved", flush=True)


if __name__ == "__main__":
    main()
