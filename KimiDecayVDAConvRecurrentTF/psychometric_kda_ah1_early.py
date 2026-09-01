"""A_H1[S4]:=1 on early steps only: t=0..2, t=0, t=1."""
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
OUT = r"C:/Users/jomor/remote-experiment-exports/v1ca020uvsqtgh/analysis/microstim_s4_ah1_early"
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
            print(f"[early] t={t0}-{t1} θ={theta:5.1f} {counts[ti]:3d}/{N}", flush=True)
        obs = make_trials(env, 2 * N, 0.0, 0, -1).to(device)
        R = forward_seq_stim(model, obs, stim_cell=S4, target="ah1",
                             t_start=t0, t_end=t1)
        fa = int((model.classify(R[:, -1]).argmax(-1) == 1).sum().item())
    print(f"[early] t={t0}-{t1} FA {fa}/{2*N}", flush=True)
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

    windows = {"t0_2": (0, 2), "t0": (0, 0), "t1": (1, 1)}
    results = {}
    for name, (a, b) in windows.items():
        c, fa = run_window(model, env, device, thetas, a, b)
        results[name] = {
            "counts": c.tolist(), "fa": fa,
            "thr": thresh(thetas, c, N, fa / (2 * N)),
            "t_start": a, "t_end": b, "arr": c,
        }

    ref = json.load(open(os.path.join(ANALYSIS, "psychometric", "psychometric_kda.json")))
    whole = json.load(open(os.path.join(ANALYSIS, "microstim_s4_ah1", "microstim_kda.json")))
    t35 = json.load(open(os.path.join(ANALYSIS, "microstim_s4_ah1_t3to5", "microstim_kda.json")))
    timed = json.load(open(os.path.join(ANALYSIS, "microstim_s4_ah1_timed", "timed_ah1.json")))
    fa_ref = ref["counts_pinned_s1"][0][0] / ref["n_trials"]
    dump = {
        "thetas": thetas.tolist(), "n_trials": N,
        "t0_2": {k: results["t0_2"][k] for k in ("counts", "fa", "thr", "t_start", "t_end")},
        "t0": {k: results["t0"][k] for k in ("counts", "fa", "thr", "t_start", "t_end")},
        "t1": {k: results["t1"][k] for k in ("counts", "fa", "thr", "t_start", "t_end")},
        "ref_valid_thr": thresh(np.array(ref["thetas"]), ref["counts_pinned_s1"][0],
                                ref["n_trials"], fa_ref),
        "ref_invalid_thr": thresh(np.array(ref["thetas"]), ref["counts_pinned_s4"][0],
                                  ref["n_trials"], fa_ref),
        "whole_thr": timed["whole_thr"],
        "t3_5_thr": timed["t3_5_thr"],
        "t3_6_thr": timed["t3_6"]["thr"],
        "t6_thr": timed["t6_only"]["thr"],
    }
    with open(os.path.join(OUT, "early_ah1.json"), "w") as f:
        json.dump(dump, f, indent=2)
    np.savez(os.path.join(OUT, "early_ah1.npz"), thetas=thetas,
             t0_2=results["t0_2"]["arr"], t0=results["t0"]["arr"], t1=results["t1"]["arr"])

    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    ax.plot(ref["thetas"], np.array(ref["counts_pinned_s1"][0]), marker="o", ms=3, lw=1.4,
            color="tab:green", label=f"valid  {dump['ref_valid_thr']:.1f}°")
    ax.plot(ref["thetas"], np.array(ref["counts_pinned_s4"][0]), marker="s", ms=3, lw=1.4,
            color="tab:red", label=f"invalid  {dump['ref_invalid_thr']:.1f}°")
    ax.plot(whole["thetas"], np.array(whole["counts_stim_invalid"]), marker="^", ms=3, lw=1.2,
            color="tab:purple", label=f"A_H1 whole t=0→6  {dump['whole_thr']:.1f}°")
    ax.plot(t35["thetas"], np.array(t35["counts_stim_invalid"]), marker="x", ms=3, lw=1.0,
            color="0.55", label=f"A_H1 t=3→5  {dump['t3_5_thr']:.1f}°")
    ax.plot(thetas, results["t0_2"]["arr"], marker="D", ms=4.5, lw=1.8, color="tab:blue",
            label=f"A_H1 t=0→2 (cue epoch)  {results['t0_2']['thr']:.1f}°")
    ax.plot(thetas, results["t0"]["arr"], marker="P", ms=5, lw=1.5, color="tab:cyan",
            label=f"A_H1 t=0 only  {results['t0']['thr']:.1f}°")
    ax.plot(thetas, results["t1"]["arr"], marker="v", ms=4, lw=1.5, color="tab:orange",
            label=f"A_H1 t=1 (cue) only  {results['t1']['thr']:.1f}°")
    ax.set_xlabel("change magnitude |Δθ| (degrees)")
    ax.set_ylabel(f'"change" declarations (out of {N})')
    ax.set_title("A_H1[S4]:=1 early only — is blank/cue enough to recover?")
    ax.set_ylim(0, N + 4)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    png = os.path.join(OUT, "early_ah1_psychometric.png")
    fig.savefig(png, dpi=140)
    plt.close(fig)
    print(f"[early] saved {png}")
    print("[early] thr valid={:.1f} invalid={:.1f} whole={:.1f} t0-2={:.1f} t0={:.1f} t1={:.1f}".format(
        dump["ref_valid_thr"], dump["ref_invalid_thr"], dump["whole_thr"],
        results["t0_2"]["thr"], results["t0"]["thr"], results["t1"]["thr"]))
    print("[early] DONE")


if __name__ == "__main__":
    main()
