"""
EXP 4 — Causal manipulation of attention: can we make v5 more / less responsive
to changes?

We inject an additive bias b into the PRE-SOFTMAX attention logits of a single
encoder (layer, head), targeting the patch keys (the image), and re-run the
behaviour under the argmax policy. b>0 forces that head to attend MORE to the
stimulus, b<0 to attend less (toward the recurrent memory instead). We sweep b
for every encoder head (8 heads: 2 layers × 4) and measure the causal effect on:
    P(hit), median RT, premature-press rate   (responsiveness to the change)
    mean V(press−wait) advantage, policy entropy, critic distributional spread
(read at a fixed near-threshold |Δθ| where there is room to move).

We also run a 'change-quadrant' variant that biases attention specifically toward
the changed quadrant (vs toward all patches) to test spatial vs global gating.

Honest expectation (per the user): a distributed, memory-as-tokens encoder may be
robust to single-head perturbation; we report the effect sizes as found.

Usage:
  .venv/bin/python -m RViT_plus_v5.analysis.deepdive.exp4_causal_attention \
      --n-trials 256 --device cpu
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


def behaviour_under_bias(model, device, env_kwargs, *, attn_bias, mag, ring,
                         change_time, n_trials, seed, mode="cued"):
    """argmax-policy rollout with an attention bias; returns behaviour + value/entropy."""
    rng = np.random.default_rng(seed)
    spec = bu.ForcedTrialSpec(proportion=ring, change_true=1, change_time=change_time,
                              change_index_mode=mode, orientation_mag=float(mag))
    envs, obs0 = bu.build_env_batch(spec, n_trials, rng, env_kwargs=env_kwargs,
                                    randomize_cue_position=True, randomize_color=True)
    rec = dd.record_rollout(model, envs, obs0, device, policy="argmax",
                            attn_bias=attn_bias, record_latents=False, record_quad=False)
    hit = rec["hit"]; rt = rec["rt"][~np.isnan(rec["rt"])]
    # value/entropy read at the change frame (index change_time) averaged over trials
    ct = change_time
    vadv = float((rec["q_press"][ct] - rec["q_wait"][ct]).mean())
    qent = float(rec["qent_press"][ct].mean())
    qstd = float(rec["qstd_press"][ct].mean())
    polent = float(rec["pol_entropy"][ct].mean())
    return {
        "hit_rate": float(hit.mean()), "median_rt": float(np.median(rt)) if rt.size else float("nan"),
        "premature_rate": float(rec["premature"].mean()),
        "v_press_minus_wait": vadv, "qent_press": qent, "qstd_press": qstd,
        "pol_entropy": polent, "n_hits": int(rt.size),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=256)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--ring", type=float, default=0.75)
    ap.add_argument("--mag", type=float, default=10.0, help="near-threshold |Δθ| with room to move")
    ap.add_argument("--biases", type=float, nargs="+",
                    default=[-6, -4, -2, -1, 0, 1, 2, 4, 6])
    ap.add_argument("--region", default="patch", choices=["patch", "quad"])
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True); os.makedirs(TABS, exist_ok=True)
    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device)
    it = dd.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    nL = model.encoder.n_layers
    nH = model.encoder.enc[0].self_attn.num_heads
    print(f"[loaded] {args.checkpoint} (iter={it}) device={device}  encoder {nL}L×{nH}H")
    print(f"[setup] near-threshold |Δθ|={args.mag} ring={args.ring} change@t={args.change_time} "
          f"n={args.n_trials} region={args.region}")

    base = behaviour_under_bias(model, device, env_kwargs, attn_bias=None, mag=args.mag,
                                ring=args.ring, change_time=args.change_time,
                                n_trials=args.n_trials, seed=args.seed)
    print(f"[baseline] hit={base['hit_rate']:.3f} rt={base['median_rt']:.2f} "
          f"prem={base['premature_rate']:.3f} Vadv={base['v_press_minus_wait']:.3f} "
          f"qent={base['qent_press']:.3f} Hpi={base['pol_entropy']:.3f}")

    # ── per-head global-patch sweep ──────────────────────────────────────────
    results = {"baseline": base, "biases": args.biases, "per_head": {}, "region": args.region,
               "mag": args.mag, "ring": args.ring, "change_time": args.change_time}
    # matched-seed b=0 reference so every bias level uses identical trials (paired Δ)
    b0_ref = behaviour_under_bias(model, device, env_kwargs, attn_bias=None, mag=args.mag,
                                  ring=args.ring, change_time=args.change_time,
                                  n_trials=args.n_trials, seed=args.seed + 1)
    for L in range(nL):
        for H in range(nH):
            key = f"L{L+1}H{H}"
            rows = []
            for b in args.biases:
                if b == 0:
                    rows.append({**b0_ref, "bias": 0.0}); continue
                if args.region == "patch":
                    bias = dd.make_attn_bias(model, device, layer=L, head=H, region="patch", value=float(b))
                else:
                    # bias toward the cued/changed quadrant requires per-trial quad; for the
                    # pooled sweep we bias S1 (top-left) — paired with cue-left trials below.
                    bias = dd.make_attn_bias(model, device, layer=L, head=H, region="quad", value=float(b), quad=0)
                r = behaviour_under_bias(model, device, env_kwargs, attn_bias=bias, mag=args.mag,
                                         ring=args.ring, change_time=args.change_time,
                                         n_trials=args.n_trials, seed=args.seed + 1)
                r["bias"] = float(b); rows.append(r)
            results["per_head"][key] = rows
            dh = rows[-1]["hit_rate"] - rows[0]["hit_rate"]
            print(f"  {key}: hit @b={args.biases[0]:+.0f}→{rows[0]['hit_rate']:.3f}  "
                  f"@b=0→{base['hit_rate']:.3f}  @b={args.biases[-1]:+.0f}→{rows[-1]['hit_rate']:.3f}  "
                  f"(Δ={dh:+.3f})")

    # ── all-heads-together sweep (bias EVERY head's patch attention) ──────────
    allrows = []
    b0_all = behaviour_under_bias(model, device, env_kwargs, attn_bias=None, mag=args.mag,
                                  ring=args.ring, change_time=args.change_time,
                                  n_trials=args.n_trials, seed=args.seed + 2)
    for b in args.biases:
        if b == 0:
            allrows.append({**b0_all, "bias": 0.0}); continue
        bias = torch.zeros(nL, nH, 3 * model.n_tokens, device=device)
        bias[:, :, :model.n_tokens] = float(b)
        r = behaviour_under_bias(model, device, env_kwargs, attn_bias=bias, mag=args.mag,
                                 ring=args.ring, change_time=args.change_time,
                                 n_trials=args.n_trials, seed=args.seed + 2)
        r["bias"] = float(b); allrows.append(r)
    results["all_heads"] = allrows
    print("[all-heads patch-gain] hit: " + "  ".join(f"{r['bias']:+.0f}:{r['hit_rate']:.3f}" for r in allrows))

    with open(f"{TABS}/exp4_causal.json", "w") as f:
        json.dump(results, f, indent=2)

    # ── plots ────────────────────────────────────────────────────────────────
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})
    biases = args.biases
    # per-head hit-rate curves
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    for key, rows in results["per_head"].items():
        L = key[1]
        c = "tab:blue" if key.startswith("L1") else "tab:red"
        axes[0].plot(biases, [r["hit_rate"] for r in rows], marker="o", lw=1.3, alpha=.8,
                     color=c, label=key)
        axes[1].plot(biases, [r["median_rt"] for r in rows], marker="o", lw=1.3, alpha=.8, color=c)
        axes[2].plot(biases, [r["premature_rate"] for r in rows], marker="o", lw=1.3, alpha=.8, color=c)
    for a, ttl, yl, bl in zip(axes, ["P(hit)", "median RT", "premature rate"],
                              ["P(hit)", "RT", "premature"],
                              [base["hit_rate"], base["median_rt"], base["premature_rate"]]):
        a.axvline(0, color="grey", ls=":"); a.axhline(bl, color="k", ls="--", alpha=.4, label="baseline")
        a.set_xlabel("attention bias b (logits) toward patch keys"); a.set_ylabel(yl); a.set_title(ttl); a.grid(alpha=.3)
    axes[0].legend(fontsize=6, ncol=2)
    fig.suptitle(f"Causal per-head attention bias → behaviour  ·  near-threshold |Δθ|={args.mag}  ·  n={args.n_trials}")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp4_perhead_behaviour.png", dpi=130, bbox_inches="tight"); plt.close(fig)

    # all-heads value/entropy effects
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    axes[0].plot(biases, [r["hit_rate"] for r in allrows], "o-", color="tab:green", label="P(hit)")
    axes[0].plot(biases, [r["premature_rate"] for r in allrows], "s--", color="tab:brown", label="premature")
    axes[0].set_ylabel("rate"); axes[0].set_title("All-heads patch gain → behaviour"); axes[0].legend(fontsize=8)
    axes[1].plot(biases, [r["v_press_minus_wait"] for r in allrows], "o-", color="tab:purple")
    axes[1].set_ylabel("Q(press)−Q(wait) at change"); axes[1].set_title("Value advantage")
    axes[2].plot(biases, [r["qent_press"] for r in allrows], "o-", color="tab:red", label="critic dist. entropy")
    ax2b = axes[2].twinx()
    ax2b.plot(biases, [r["pol_entropy"] for r in allrows], "s--", color="tab:blue", label="policy entropy")
    axes[2].set_ylabel("critic quantile entropy", color="tab:red")
    ax2b.set_ylabel("policy entropy (nats)", color="tab:blue")
    axes[2].set_title("Attention → uncertainty")
    for a in axes:
        a.axvline(0, color="grey", ls=":"); a.set_xlabel("attention bias b (all heads)"); a.grid(alpha=.3)
    fig.suptitle("All-heads patch-attention gain: behaviour, value, and uncertainty")
    fig.tight_layout(); fig.savefig(f"{FIGS}/exp4_allheads_value_entropy.png", dpi=130, bbox_inches="tight"); plt.close(fig)
    print(f"[saved] exp4 figures + {TABS}/exp4_causal.json")
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
