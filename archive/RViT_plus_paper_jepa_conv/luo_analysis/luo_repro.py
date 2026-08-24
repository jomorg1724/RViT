"""Luo-Maunsell reproduction: does the sensitivity session move d' (per-location, cued>uncued) and the
criterion session move c (global liberal bias, high FA)? Compute -> print + npz."""
import os, numpy as np, luo_core as C

MAGS = [12.0, 18.0, 26.0]
B = 400


def analyze(session, fb, mag):
    m, it = C.load(session, fb)
    hr_c = C.declare_rate(m, session, 1, C.CUE, mag, B)          # HR, change at CUED cell
    hr_u = C.declare_rate(m, session, 1, C.UNCUED, mag, B)       # HR, change at UNCUED cell
    fa = C.declare_rate(m, session, 0, -1, mag, B)               # FA, no-change
    dc, cc = C.sdt(hr_c, fa, B); du, cu = C.sdt(hr_u, fa, B)
    return it, hr_c, hr_u, fa, dc, du, cc


def main():
    out = {}
    print(f"{'model':28s} {'Δ':>3s} {'HRcue':>6s} {'HRunc':>6s} {'FA':>5s} "
          f"{'d′cue':>6s} {'d′unc':>6s} {'Δd′':>6s} {'crit_c':>7s}")
    for session in ("sensitivity", "criterion"):
        for fb in ("crossattn1", "affine_ew"):
            for mag in MAGS:
                it, hr_c, hr_u, fa, dc, du, cc = analyze(session, fb, mag)
                key = f"{session}_{fb}"
                out[f"{key}_m{mag:.0f}"] = np.array([hr_c, hr_u, fa, dc, du, dc - du, cc])
                out[f"{key}_iter"] = it
                print(f"{key:28s} {mag:3.0f} {hr_c:6.2f} {hr_u:6.2f} {fa:5.2f} "
                      f"{dc:6.2f} {du:6.2f} {dc-du:6.2f} {cc:7.2f}", flush=True)
    np.savez(os.path.join(C.FIGS, "luo_repro.npz"), **out)
    print(f"[luo] saved -> {os.path.join(C.FIGS, 'luo_repro.npz')}", flush=True)


if __name__ == "__main__":
    main()
