"""A_H1[S4]:=1 timed to (a) t=3..6 and (b) t=6 only, vs existing curves."""
from __future__ import annotations
import json, os, sys
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from psychometric_kda_microstim import (
    build_model, make_trials, forward_seq_stim, S4, THETAS,
)
from envs import make_env
from train_rl import pick_device, seed_training_rngs

CKPT = r"C:/Users/jomor/remote-experiment-exports/v1ca020uvsqtgh/kda_convmem_final.pt"
OUT = r"C:/Users/jomor/remote-experiment-exports/v1ca020uvsqtgh/analysis/microstim_s4_ah1_timed"
N = 100
ANALYSIS = os.path.dirname(OUT)


def thresh(thetas, counts, n, fa):
    bar = fa * n + 0.5 * (n - fa * n)
    above = thetas[np.asarray(counts) >= bar]
    return float(above[0]) if len(above) else float("nan")


def run_window(model, env, device, thetas, t0, t1):
    counts = np.zeros(len(thetas), dtype=np.int64)
    with torch.no_grad():
        for ti, theta in enumerate(thetas):
            obs = make_trials(env, N, theta, 1, S4).to(device)
            R = forward_seq_stim(model, obs, stim_cell=S4, target="ah1",
                                 t_start=t0, t_end=t1)
            counts[ti] = int((model.classify(R[:, -1]).argmax(-1) == 1).sum().item())
            print(f"[timed] t={t0}-{t1} θ={theta:5.1f} {counts[ti]:3d}/{N}", flush=True)
        obs = make_trials(env, 2 * N, 0.0, 0, -1).to(device)
        R = forward_seq_stim(model, obs, stim_cell=S4, target="ah1",
                             t_start=t0, t_end=t1)
        fa = int((model.classify(R[:, -1]).argmax(-1) == 1).sum().item())
    print(f"[timed] t={t0}-{t1} FA {fa}/{2*N}", flush=True)
    return counts, fa


def main():
    os.makedirs(OUT, exist_ok=True)
    seed_training_rngs(0)
    device = pick_device("cuda")
    ckpt = torch.load(CKPT, map_location="cpu", weights_only=False)
    model = build_model(ckpt, device)
    env = make_env("vda16", T=7, frame_repeat=1, min_change_time=5, max_change_time=5,
                   noise_multiplier=5.0, curriculum=False, theta=65.0)
    thetas = THETAS

    c36, fa36 = run_window(model, env, device, thetas, 3, 6)
    c6, fa6 = run_window(model, env, device, thetas, 6, 6)

    ref = json.load(open(os.path.join(ANALYSIS, "psychometric", "psychometric_kda.json")))
    whole = json.load(open(os.path.join(ANALYSIS, "microstim_s4_ah1", "microstim_kda.json")))
    t35 = json.load(open(os.path.join(ANALYSIS, "microstim_s4_ah1_t3to5", "microstim_kda.json")))
    fa_ref = ref["counts_pinned_s1"][0][0] / ref["n_trials"]
    summary = {
        "thetas": thetas.tolist(),
        "n_trials": N,
        "t3_6": {"counts": c36.tolist(), "fa": fa36,
                 "thr": thresh(thetas, c36, N, fa36 / (2 * N))},
        "t6_only": {"counts": c6.tolist(), "fa": fa6,
                    "thr": thresh(thetas, c6, N, fa6 / (2 * N))},
        "ref_valid_thr": thresh(np.array(ref["thetas"]), ref["counts_pinned_s1"][0],
                                ref["n_trials"], fa_ref),
        "ref_invalid_thr": thresh(np.array(ref["thetas"]), ref["counts_pinned_s4"][0],
                                  ref["n_trials"], fa_ref),
        "whole_thr": thresh(np.array(whole["thetas"]), whole["counts_stim_invalid"],
                            whole["n_trials"], fa_ref),
        "t3_5_thr": thresh(np.array(t35["thetas"]), t35["counts_stim_invalid"],
                           t35["n_trials"], t35["fa_stim"] / (2 * t35["n_trials"])),
    }
    with open(os.path.join(OUT, "timed_ah1.json"), "w") as f:
        json.dump(summary, f, indent=2)
    np.savez(os.path.join(OUT, "timed_ah1.npz"), thetas=thetas, c36=c36, c6=c6, fa36=fa36, fa6=fa6)

    fig, ax = plt.subplots(figsize=(8.2, 5.3))
    ax.plot(ref["thetas"], np.array(ref["counts_pinned_s1"][0]), marker="o", ms=3, lw=1.4,
            color="tab:green", label=f"valid  thr={summary['ref_valid_thr']:.1f}°")
    ax.plot(ref["thetas"], np.array(ref["counts_pinned_s4"][0]), marker="s", ms=3, lw=1.4,
            color="tab:red", label=f"invalid  thr={summary['ref_invalid_thr']:.1f}°")
    ax.plot(whole["thetas"], np.array(whole["counts_stim_invalid"]), marker="^", ms=3, lw=1.2,
            color="tab:purple", label=f"A_H1[S4] whole trial  thr={summary['whole_thr']:.1f}°")
    ax.plot(t35["thetas"], np.array(t35["counts_stim_invalid"]), marker="x", ms=3.5, lw=1.2,
            color="tab:orange", label=f"A_H1[S4] t=3→5  thr={summary['t3_5_thr']:.1f}°")
    ax.plot(thetas, c36, marker="D", ms=4, lw=1.7, color="tab:blue",
            label=f"A_H1[S4] t=3→6  thr={summary['t3_6']['thr']:.1f}°")
    ax.plot(thetas, c6, marker="P", ms=5, lw=1.7, color="tab:cyan",
            label=f"A_H1[S4] t=6 only  thr={summary['t6_only']['thr']:.1f}°")
    ax.set_xlabel("change magnitude |Δθ| (degrees)")
    ax.set_ylabel(f'"change" declarations (out of {N})')
    ax.set_title("A_H1[S4]:=1 timing: does t=6 recover the whole-trial rescue?")
    ax.set_ylim(0, N + 4)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    png = os.path.join(OUT, "timed_ah1_psychometric.png")
    fig.savefig(png, dpi=140)
    plt.close(fig)
    print(f"[timed] saved {png}")
    print("[timed] thr valid={:.1f} invalid={:.1f} whole={:.1f} t3-5={:.1f} t3-6={:.1f} t6={:.1f}".format(
        summary["ref_valid_thr"], summary["ref_invalid_thr"], summary["whole_thr"],
        summary["t3_5_thr"], summary["t3_6"]["thr"], summary["t6_only"]["thr"]))
    print("[timed] DONE")


if __name__ == "__main__":
    main()
