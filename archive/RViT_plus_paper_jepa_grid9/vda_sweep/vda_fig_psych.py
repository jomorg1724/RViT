"""Psychometrics + chronometrics for the VDA set-size sweep (vda1 vs vda4, both feedback variants).
Response rate and RT vs change-magnitude Δ, per cue condition (cued change at TL vs uncued at BR),
per validity/proportion. vda1 (1 stimulus) is cued-only (no uncued location exists). Compute -> npz;
a torch-free figure script renders it. CPU, thread-capped."""
import os, numpy as np, vda_core as C

DE = [0, 3, 6, 9, 12, 15, 18, 22, 26, 30]        # change magnitudes (deg)
PROPS = [0.25, 0.5, 0.75, 1.0]                    # cue validity
B = 300


def curve(m, task, prop, chg, color="red"):
    ci = C.TL if chg == "cued" else C.BR
    rates, rts = [], []
    for de in DE:
        r, rt = C.behavior(m, task, C.TL, prop, ci, float(de), color=color, ct=1, B=B)
        rates.append(r); rts.append(rt)
    fa, _ = C.behavior(m, task, C.TL, prop, ci, 0.0, color=color, ct=0, B=B)   # Δ=0 false-alarm
    return np.array(rates), np.array(rts), float(fa)


def main():
    out = {}
    for task in ("vda1", "vda2", "vda4", "vda9", "vda16"):
        for fb in ("crossattn1", "affine_ew"):
            m, it = C.load(task, fb, 128)
            out[f"{task}_{fb}_iter"] = it
            print(f"[psych] {task} {fb} iter={it}", flush=True)
            for prop in PROPS:
                rc, rtc, fac = curve(m, task, prop, "cued")
                out[f"{task}_{fb}_p{prop}_cued"] = rc
                out[f"{task}_{fb}_p{prop}_cued_rt"] = rtc
                out[f"{task}_{fb}_p{prop}_cued_fa"] = fac
                if task != "vda1":                                  # uncued needs >1 stimulus
                    ru, rtu, fau = curve(m, task, prop, "uncued")
                    out[f"{task}_{fb}_p{prop}_uncued"] = ru
                    out[f"{task}_{fb}_p{prop}_uncued_rt"] = rtu
                    out[f"{task}_{fb}_p{prop}_uncued_fa"] = fau
                # fitted cued threshold (position) for the summary panel
                fit = C.fit_logistic(DE, rc)
                out[f"{task}_{fb}_p{prop}_cued_thr"] = fit["position"]
                print(f"   p{prop} cued thr={fit['position']:.1f}° fa={fac:.2f}", flush=True)
    np.savez(os.path.join(C.FIGS, "psych.npz"), DE=np.array(DE), PROPS=np.array(PROPS), **out)
    print(f"[psych] saved -> {os.path.join(C.FIGS, 'psych.npz')}", flush=True)


if __name__ == "__main__":
    main()
