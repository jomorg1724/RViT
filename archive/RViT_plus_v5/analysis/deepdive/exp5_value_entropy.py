"""
EXP 5 — Does the value function learn appropriate values, and how does attention
distort value & uncertainty?

Part 1 — VALUE APPROPRIATENESS
  * V(s_t) time-courses under forced-wait, split by cue colour (reward 5/3/1) and
    by change vs no-change. A well-calibrated critic should: track the discounted
    expected reward, rise as the (rewarded) change approaches, and be ordered
    red>green>blue.
  * Calibration: predicted V(s_t) vs the realised discounted return-to-go under
    the model's own greedy policy (Monte-Carlo), pooled over states → scatter +
    R² + slope. Done under the ARGMAX policy so the MC return matches what V is
    supposed to predict.
  * Q(press) vs Q(wait) advantage over time: should cross zero around change
    onset (press becomes worth more than waiting only once the change is visible).

Part 2 — CRITIC DISTRIBUTIONAL ENTROPY
  * The QR critic's value distribution spread (quantile entropy / std) over the
    episode: does outcome uncertainty collapse at detection?
  * Entropy split by cue value and by hit vs miss.

Part 3 — ATTENTION → VALUE / ENTROPY (causal)
  * Sweep an all-heads patch-attention bias and read V(press), Q-advantage,
    critic entropy, and policy entropy at the change frame — how does starving or
    flooding the encoder with stimulus evidence distort the value estimate?

Usage:
  .venv/bin/python -m RViT_plus_v5.analysis.deepdive.exp5_value_entropy \
      --n-trials 400 --device cpu
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_v5.analysis import _behav_utils as bu
from RViT_plus_v5.analysis.deepdive import dd_core as dd

FIGS = os.path.join(_HERE, "figs")
TABS = os.path.join(_HERE, "tables")


def mc_returns(rec, gamma):
    """Monte-Carlo discounted return-to-go for each (trial, t) under the policy
    that generated rec. Reward is delivered on the terminal step (env gives a
    single end-of-episode reward); we approximate per-step reward as 0 except a
    terminal payoff = rec['reward'] at the trial's press/timeout step. Returns
    array (T,B) of return-to-go and a validity mask (states actually visited)."""
    T = rec["v_scalar"].shape[0]; B = rec["hit"].size
    press = rec["press_index"]; ct = rec["change_time"]; ctrue = rec["change_true"]
    term = np.where(press >= 0, press, T - 1)             # terminal step index per trial
    rew = rec["reward"]                                    # terminal reward
    G = np.full((T, B), np.nan)
    for i in range(B):
        ti = int(term[i])
        for t in range(ti + 1):
            G[t, i] = (gamma ** (ti - t)) * rew[i]
    visited = ~np.isnan(G)
    return G, visited


def run_forced(model, device, env_kwargs, *, color, change_true, mag, ring, change_time,
               n_trials, seed):
    rng = np.random.default_rng(seed)
    spec = bu.ForcedTrialSpec(cue_color=color, proportion=ring, change_true=change_true,
                              change_time=change_time, change_index_mode="cued",
                              orientation_mag=(None if mag is None else float(mag)))
    envs, obs0 = bu.build_env_batch(spec, n_trials, rng, env_kwargs=env_kwargs,
                                    randomize_cue_position=True,
                                    randomize_color=(color is None))
    return dd.record_rollout_chunked(model, envs, obs0, device, chunk=400, policy="wait",
                                     record_latents=False, record_quad=False)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=400)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--ring", type=float, default=0.75)
    ap.add_argument("--mag", type=float, default=40.0)
    ap.add_argument("--biases", type=float, nargs="+", default=[-6, -4, -2, -1, 0, 1, 2, 4, 6])
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True); os.makedirs(TABS, exist_ok=True)
    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device)
    it = dd.load_checkpoint(model, args.checkpoint, device)
    gamma = float(cfg["ppo"]["gamma"])
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}  gamma={gamma}")

    summary = {"iter": it, "gamma": gamma, "change_time": args.change_time}

    # ── Part 1: value time-courses by colour (change trials) ─────────────────
    Tg = args.change_time
    vcurves = {}; qadv = {}; entc = {}
    for color in dd.COLORS:
        rec = run_forced(model, device, env_kwargs, color=color, change_true=1, mag=args.mag,
                         ring=args.ring, change_time=Tg, n_trials=args.n_trials,
                         seed=args.seed + hash(color) % 7919)
        vcurves[color] = rec["v_scalar"].mean(1)                 # (T,)
        qadv[color] = (rec["q_press"] - rec["q_wait"]).mean(1)   # (T,)
        entc[color] = rec["qent_press"].mean(1)
        print(f"  {color:5s}(v={dd.COLOR_VALUE[color]}): V@cue={vcurves[color][2]:.2f} "
              f"V@change={vcurves[color][Tg]:.2f} V@max={vcurves[color].max():.2f}")
    # no-change (for contrast) at fixed colour green
    rec_nc = run_forced(model, device, env_kwargs, color=None, change_true=0, mag=None,
                        ring=args.ring, change_time=Tg, n_trials=args.n_trials, seed=args.seed + 31)
    v_nochange = rec_nc["v_scalar"].mean(1)

    # ── Part 2: calibration under argmax ─────────────────────────────────────
    rng = np.random.default_rng(args.seed + 77)
    spec = bu.ForcedTrialSpec(proportion=args.ring, change_true=None, change_time=None,
                              change_index_mode="cued", orientation_mag=None)
    envs, obs0 = [], []
    for _ in range(args.n_trials * 3):
        e = dd.bu.ChangeDetectionEnv(**env_kwargs); o = e.reset(); envs.append(e); obs0.append(o)
    rec_g = dd.record_rollout_chunked(model, envs, obs0, device, chunk=400, policy="argmax",
                                      record_latents=False, record_quad=False)
    G, visited = mc_returns(rec_g, gamma)
    Vpred = rec_g["v_scalar"]
    vmask = visited & np.isfinite(Vpred)
    vp = Vpred[vmask]; gt = G[vmask]
    from numpy.polynomial import polynomial as P
    slope, intercept = np.polyfit(vp, gt, 1)
    ss_res = float(((gt - (slope * vp + intercept)) ** 2).sum())
    ss_tot = float(((gt - gt.mean()) ** 2).sum())
    calib_r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    print(f"[calibration] V vs MC return: slope={slope:.3f} intercept={intercept:.3f} R²={calib_r2:.3f} (n={vp.size})")
    summary["calibration"] = {"slope": float(slope), "intercept": float(intercept),
                              "r2": float(calib_r2), "n": int(vp.size)}

    # ── Part 2b: entropy by hit vs miss (change trials, near-threshold) ──────
    rec_nt = run_forced(model, device, env_kwargs, color=None, change_true=1, mag=10.0,
                        ring=args.ring, change_time=Tg, n_trials=args.n_trials * 2, seed=args.seed + 91)
    # use argmax to define hit/miss? forced-wait has no press; instead split by whether
    # the change is eventually detectable -> compare entropy pre/post change frame.
    ent_pre = float(rec_nt["qent_press"][:Tg].mean())
    ent_post = float(rec_nt["qent_press"][Tg + 1:].mean())
    print(f"[entropy] critic dist entropy pre-change={ent_pre:.3f}  post-change={ent_post:.3f}")
    summary["entropy_pre_post"] = {"pre": ent_pre, "post": ent_post}

    # ── Part 3: attention → value/entropy ────────────────────────────────────
    nL, nH, N = model.encoder.n_layers, model.encoder.enc[0].self_attn.num_heads, model.n_tokens
    sweep = []
    for b in args.biases:
        bias = None
        if b != 0:
            bias = torch.zeros(nL, nH, 3 * N, device=device)
            bias[:, :, :N] = float(b)
        # forced-wait so the encoder always sees the change; the bias is applied
        # inside record_rollout's encoder step.
        rng = np.random.default_rng(args.seed + 5)   # matched trials across biases (paired)
        spec = bu.ForcedTrialSpec(cue_color="green", proportion=args.ring, change_true=1,
                                  change_time=Tg, change_index_mode="cued", orientation_mag=float(args.mag))
        envs, obs0 = bu.build_env_batch(spec, args.n_trials, rng, env_kwargs=env_kwargs,
                                        randomize_cue_position=True, randomize_color=False)
        rb = dd.record_rollout_chunked(model, envs, obs0, device, chunk=400, policy="wait",
                                       attn_bias=bias, record_latents=False, record_quad=False)
        post = slice(Tg, min(Tg + 4, rb["v_scalar"].shape[0]))
        sweep.append({
            "bias": float(b),
            "v_press": float(rb["q_press"][post].mean()),
            "v_scalar": float(rb["v_scalar"][post].mean()),
            "q_adv": float((rb["q_press"] - rb["q_wait"])[post].mean()),
            "qent": float(rb["qent_press"][post].mean()),
            "qstd": float(rb["qstd_press"][post].mean()),
            "pol_ent": float(rb["pol_entropy"][post].mean()),
            "press_prob": float(rb["press_prob"][post].mean()),
        })
        print(f"  bias={b:+.0f}: V(press)={sweep[-1]['v_press']:.2f} Qadv={sweep[-1]['q_adv']:.2f} "
              f"qent={sweep[-1]['qent']:.3f} Hpi={sweep[-1]['pol_ent']:.3f} P(press)={sweep[-1]['press_prob']:.3f}")
    summary["attn_value_sweep"] = sweep
    summary["v_by_color"] = {c: vcurves[c].tolist() for c in dd.COLORS}
    summary["qadv_by_color"] = {c: qadv[c].tolist() for c in dd.COLORS}
    summary["ent_by_color"] = {c: entc[c].tolist() for c in dd.COLORS}
    summary["v_nochange"] = v_nochange.tolist()

    with open(f"{TABS}/exp5_value.json", "w") as f:
        json.dump(summary, f, indent=2)

    # ── plots ────────────────────────────────────────────────────────────────
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    T = vcurves["red"].shape[0]; tt = np.arange(T)
    vc = {"blue": "tab:blue", "green": "tab:green", "red": "tab:red"}

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for color in dd.COLORS:
        ax[0].plot(tt, vcurves[color], color=vc[color], lw=2, label=f"{color} (v={dd.COLOR_VALUE[color]})")
    ax[0].plot(tt, v_nochange, color="grey", lw=2, ls="--", label="no-change")
    ax[0].axvline(1, color="k", ls=":", alpha=.4); ax[0].axvline(Tg, color="orange", ls="--", alpha=.6)
    ax[0].set(xlabel="t", ylabel="V(s)", title="Value time-course by cue value"); ax[0].grid(alpha=.3); ax[0].legend(fontsize=7)
    for color in dd.COLORS:
        ax[1].plot(tt, qadv[color], color=vc[color], lw=2, label=color)
    ax[1].axhline(0, color="grey", ls=":"); ax[1].axvline(Tg, color="orange", ls="--", alpha=.6)
    ax[1].set(xlabel="t", ylabel="Q(press)−Q(wait)", title="Press advantage"); ax[1].grid(alpha=.3)
    for color in dd.COLORS:
        ax[2].plot(tt, entc[color], color=vc[color], lw=2, label=color)
    ax[2].axvline(Tg, color="orange", ls="--", alpha=.6)
    ax[2].set(xlabel="t", ylabel="critic quantile entropy", title="Outcome uncertainty (critic spread)"); ax[2].grid(alpha=.3)
    fig.suptitle(f"Value function appropriateness  ·  change@t={Tg}  ·  |Δθ|={args.mag}  ·  n={args.n_trials}/cell")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp5_value_timecourse.png", dpi=130, bbox_inches="tight"); plt.close(fig)

    # calibration scatter (subsample for plotting)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    idx = np.random.default_rng(0).choice(vp.size, size=min(4000, vp.size), replace=False)
    ax[0].scatter(vp[idx], gt[idx], s=4, alpha=.15, color="tab:blue")
    lo, hi = float(min(vp.min(), gt.min())), float(max(vp.max(), gt.max()))
    ax[0].plot([lo, hi], [lo, hi], "k--", label="identity")
    ax[0].plot([lo, hi], [slope * lo + intercept, slope * hi + intercept], "r-",
               label=f"fit (R²={calib_r2:.2f})")
    ax[0].set(xlabel="predicted V(s)", ylabel="realised MC return-to-go",
              title="Critic calibration (argmax policy)"); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
    # attention sweep
    b = [s["bias"] for s in sweep]
    ax[1].plot(b, [s["v_press"] for s in sweep], "o-", color="tab:purple", label="V(press) post-change")
    ax[1].plot(b, [s["q_adv"] for s in sweep], "s-", color="tab:green", label="Q(press)−Q(wait)")
    axb = ax[1].twinx()
    axb.plot(b, [s["qent"] for s in sweep], "^--", color="tab:red", label="critic entropy")
    ax[1].axvline(0, color="grey", ls=":")
    ax[1].set(xlabel="all-heads patch-attention bias b", ylabel="value")
    axb.set_ylabel("critic quantile entropy", color="tab:red")
    ax[1].set_title("Attention distorts value & uncertainty"); ax[1].legend(fontsize=8, loc="upper left"); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp5_calibration_attn.png", dpi=130, bbox_inches="tight"); plt.close(fig)
    print(f"[saved] exp5 figures + {TABS}/exp5_value.json")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
