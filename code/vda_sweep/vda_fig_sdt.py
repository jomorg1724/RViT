"""VDA SDT (criterion & sensitivity via the attention clamp). Sweep the attention bias α1 on the cued
TL patch (0=suppress → 0.5=natural → 1=enhance), applied from the change frame, and measure how the
decision variable's d' and criterion c move. HR = declare on a cued change (Δ=18); FA = declare on
no-change. vda1 vs vda4 × both variants. Compute -> npz + print. Run on MPS/CPU."""
import os, numpy as np, vda_core as C
from scipy.stats import norm

ALPHAS = [0.0, 0.25, 0.5, 0.75, 1.0]
MAG, B, SEED = 18.0, 250, 20250707


def sdt(hr, fa, n=B):
    hr = min(max(hr, 1 / (2 * n)), 1 - 1 / (2 * n)); fa = min(max(fa, 1 / (2 * n)), 1 - 1 / (2 * n))
    zh, zf = norm.ppf(hr), norm.ppf(fa)
    return zh - zf, -0.5 * (zh + zf)                            # (d', criterion c)


def hr_fa(m, task, K, alpha, hit_videos, false_alarm_videos):
    cl = C.clamp_alpha(K, m.n_tokens, C.TL, alpha)
    ph = C.press_times_clamp(m, task, C.TL, 1.0, "red", 1, C.TL, MAG,
                             clamp=cl, clamp_from=5, videos=hit_videos)
    pf = C.press_times_clamp(m, task, C.TL, 1.0, "red", 0, -1, MAG,
                             clamp=cl, clamp_from=5, videos=false_alarm_videos)
    return float((ph >= 5).mean()), float((pf >= 5).mean())


def run_sweep(m, task, K, seed=SEED, B=B):
    """Evaluate every clamp level on common-random-number condition batches."""
    hit_videos = C.make_video_batch(
        task, C.TL, 1.0, "red", 1, C.TL, MAG, B=B, seed=seed
    )
    false_alarm_videos = C.make_video_batch(
        task, C.TL, 1.0, "red", 0, -1, MAG, B=B, seed=seed + 1
    )
    ds, cs = [], []
    for alpha in ALPHAS:
        hr, fa = hr_fa(m, task, K, alpha, hit_videos, false_alarm_videos)
        dp, criterion = sdt(hr, fa, n=B)
        ds.append(dp); cs.append(criterion)
    return ds, cs


def main():
    out = {"ALPHAS": np.array(ALPHAS), "seed": np.int64(SEED), "n": np.int64(B)}
    print(f"{'model':22s} clamp α1 sweep → {ALPHAS}")
    for task in ("vda1", "vda2", "vda4", "vda9", "vda16"):
        for fb in ("crossattn1", "affine_ew"):
            m, it = C.load(task, fb, 128)
            K = 2 * m.n_tokens if fb == "crossattn1" else m.n_tokens
            ds, cs = run_sweep(m, task, K)
            out[f"{task}_{fb}_d"] = np.array(ds); out[f"{task}_{fb}_c"] = np.array(cs)
            out[f"{task}_{fb}_iter"] = np.int64(it)
            print(f"{task}_{fb:11s} d'={['%.2f' % x for x in ds]}  c={['%.2f' % x for x in cs]}", flush=True)
    np.savez(os.path.join(C.FIGS, "sdt.npz"), **out)
    print(f"[sdt] saved -> {os.path.join(C.FIGS, 'sdt.npz')}", flush=True)


if __name__ == "__main__":
    main()
