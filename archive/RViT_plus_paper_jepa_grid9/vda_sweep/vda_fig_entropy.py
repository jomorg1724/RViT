"""Distributional-critic entropy / uncertainty under attention manipulation — including the
'confidently-wrong' case: on a REAL change at the UNCUED patch, misdirect attention onto the cued
(no-change) patch and ask whether the model becomes MORE certain (lower policy entropy, tighter critic
quantiles) while MISSING the change. Measured at the change frame. vda4 × both variants. MPS/CPU."""
import os, numpy as np, vda_core as C

B, SEED = 250, 20250707


def pol_entropy(lg):
    e = np.exp(lg - lg.max(-1, keepdims=True)); p = e / e.sum(-1, keepdims=True); q = p[..., 1]
    return -(q * np.log(q + 1e-9) + (1 - q) * np.log(1 - q + 1e-9))


def measure(m, task, ci, clamp, videos, mag=18.0, ct=1):
    lg, Vsc, Vd, _ = C.rollout(
        m, task, C.TL, 1.0, "red", ct, ci, mag,
        clamp=clamp, clamp_from=3, videos=videos,
    )
    H = float(pol_entropy(lg)[:, 5].mean())                      # policy entropy @ change frame
    spread = float(Vd[:, 5].std(-1).mean())                     # distributional-critic quantile spread @ t5
    declare = float((lg[:, 5:].argmax(-1) == 1).any(1).mean())  # declared within the window?
    return H, spread, declare


def run_conditions(m, task, K, seed=SEED, B=B):
    """Run interventions on one matched change batch plus one no-change reference."""
    change_videos = C.make_video_batch(
        task, C.TL, 1.0, "red", 1, C.BR, 18.0, B=B, seed=seed
    )
    no_change_videos = C.make_video_batch(
        task, C.TL, 1.0, "red", 0, -1, 18.0, B=B, seed=seed + 1
    )
    nloc = m.n_tokens
    return [
        measure(m, task, C.BR, None, videos=change_videos),
        measure(
            m, task, C.BR, C.clamp_alpha(K, nloc, C.BR, 1.0),
            videos=change_videos,
        ),
        measure(
            m, task, C.BR, C.clamp_alpha(K, nloc, C.TL, 1.0),
            videos=change_videos,
        ),
        measure(m, task, -1, None, videos=no_change_videos, ct=0),
    ]


def main():
    out = {"seed": np.int64(SEED), "n": np.int64(B)}
    for fb in ("crossattn1", "affine_ew"):
        m, it = C.load("vda4", fb, 128)
        K = 2 * m.n_tokens if fb == "crossattn1" else m.n_tokens
        nat, atc, mis, nc = run_conditions(m, "vda4", K)
        out[f"{fb}"] = np.array([nat, atc, mis, nc])
        out[f"{fb}_iter"] = np.int64(it)
        print(f"vda4 {fb} — REAL change at UNCUED (BR):  [H=policy entropy, spread=critic quantiles, decl=declare rate]")
        print(f"   natural attention : H={nat[0]:.3f} spread={nat[1]:.2f} declare={nat[2]:.2f}")
        print(f"   attend the change : H={atc[0]:.3f} spread={atc[1]:.2f} declare={atc[2]:.2f}")
        print(f"   MISDIRECT (→cued) : H={mis[0]:.3f} spread={mis[1]:.2f} declare={mis[2]:.2f}   <- confident-wrong?")
        print(f"   [ref] true no-chg : H={nc[0]:.3f} spread={nc[1]:.2f} declare={nc[2]:.2f}", flush=True)
    np.savez(os.path.join(C.FIGS, "entropy.npz"), **out)
    print("[entropy] saved", flush=True)


if __name__ == "__main__":
    main()
