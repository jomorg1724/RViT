"""Attentional microstimulation: on NO-CHANGE trials, inject attention (α clamp, sustained from stimulus
onset) onto a patch and ask whether it EVOKES a false detection — a false 'declare' when nothing changed.
Sweep injection strength (false-alarm rate vs α) at two locations (cued TL, uncued BR) to show the effect
is driven by the injection, not the site. The causal analog of evoking a percept by stimulating a
priority map. vda4 × both variants. MPS/CPU."""
import os, numpy as np, vda_core as C

ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0]
B, SEED = 250, 20250707


def fa_at(m, task, K, loc, alpha, videos):
    cl = C.clamp_alpha(K, m.n_tokens, loc, alpha)
    pf = C.press_times_clamp(m, task, C.TL, 1.0, "red", 0, -1, 18.0,
                             clamp=cl, clamp_from=3, videos=videos)
    return float((pf >= 5).mean())


def run_sweep(m, task, K, seed=SEED, B=B):
    videos = C.make_video_batch(
        task, C.TL, 1.0, "red", 0, -1, 18.0, B=B, seed=seed
    )
    fa_tl = [fa_at(m, task, K, C.TL, alpha, videos) for alpha in ALPHAS]
    fa_br = [fa_at(m, task, K, C.BR, alpha, videos) for alpha in ALPHAS]
    return fa_tl, fa_br


def main():
    out = {"ALPHAS": np.array(ALPHAS), "seed": np.int64(SEED), "n": np.int64(B)}
    for fb in ("crossattn1", "affine_ew"):
        m, it = C.load("vda4", fb, 128)
        K = 2 * m.n_tokens if fb == "crossattn1" else m.n_tokens
        faTL, faBR = run_sweep(m, "vda4", K)
        out[f"{fb}_TL"] = np.array(faTL); out[f"{fb}_BR"] = np.array(faBR)
        out[f"{fb}_iter"] = np.int64(it)
        print(f"vda4 {fb}: no-change FALSE-declare vs injected attention α")
        print(f"   inject@cued TL : {['%.2f' % x for x in faTL]}")
        print(f"   inject@uncued BR: {['%.2f' % x for x in faBR]}", flush=True)
    np.savez(os.path.join(C.FIGS, "microstim.npz"), **out)
    print("[microstim] saved", flush=True)


if __name__ == "__main__":
    main()
