"""
EXP 4 — Causal manipulation of attention (v11 dual-stream): which attention lever
moves the DECISION, and which only moves uncertainty / value?

v11 runs TWO parallel cross-attention streams, both querying with the patch tokens
X but reading different memories:
    SALIENCE (bottom-up): Q=X, K=V=H1, residual=X  → grounded image + change signal
    TOP-DOWN (gating):    Q=X, K=V=H2, residual=H2 → gated deep-memory readout
Each attention is (B, heads, N_query, N_key) with the N memory rows as keys
(memory row i ↔ patch position i). So the natural causal levers are per-STREAM,
per-(memory)-key gains:

  region "sal_all"   : add bias b to ALL salience (H1) keys of every head
                       (bottom-up sensory-readout gain)
  region "td_all"    : add bias b to ALL top-down (H2) keys of every head
                       (top-down expectation gain)
  region "sal_quad"  : add bias b to the salience keys of ONE quadrant (spatial,
                       bottom-up)
  region "td_quad"   : add bias b to the top-down keys of ONE quadrant (spatial,
                       top-down)

We inject the additive bias into the PRE-SOFTMAX logits of the chosen stream (all
heads, or one head), re-run behaviour under the argmax policy and measure the
causal effect on:
    P(hit), median RT, premature-press rate                  (the DECISION)
    Q(press)−Q(wait) advantage, critic quantile entropy/std, policy entropy
                                                             (VALUE / uncertainty)
read at a fixed near-threshold |Δθ| where there is room to move.

Spatial dissociation: change_index_mode="cued" makes the change land in the cued
quadrant (S1 for cue-left), so a per-trial quad bias targets the cued==changed
quadrant. The CUE POSITION IS FIXED (default 'left') so the quadrant-aligned levers
align with the cue/change on every trial (a randomized cue dilutes the lever ~2×).
We then run an INVALID-ALIGNMENT control (change ALWAYS at S1, cue FIXED right) to
ask whether biasing the changed-quadrant keys still moves behaviour when the change
is uncued — i.e. whether the salience lever is CHANGE-locked (bottom-up) rather
than cue-locked.

Usage:
  .venv/bin/python -m RViT_plus_recur.analysis.deepdive.exp4_causal_attention \
      --n-trials 200 --device cpu
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RViT_plus_recur.analysis import _behav_utils as bu  # noqa: E402
from RViT_plus_recur.analysis.deepdive import dd_core as dd  # noqa: E402

FIGS = os.path.join(_HERE, "figs")
TABS = os.path.join(_HERE, "tables")
LOG = os.path.join(_HERE, "exp4.log")

_LOGF = None


def log(msg: str = "") -> None:
    print(msg)
    if _LOGF is not None:
        _LOGF.write(msg + "\n")
        _LOGF.flush()


def behaviour_under_bias(model, device, env_kwargs, *, attn_bias, mag, ring,
                         change_time, n_trials, seed, mode, cue="left"):
    """argmax-policy rollout with an attention bias; returns behaviour + value/entropy.

    The CUE POSITION IS FIXED (`cue`, default 'left'); colour stays randomized.
    `mode` is forwarded as change_index_mode ("cued" → change in cued quadrant;
    int 0 → change always at S1)."""
    rng = np.random.default_rng(seed)
    spec = bu.ForcedTrialSpec(cue_position=cue, proportion=ring, change_true=1,
                              change_time=change_time,
                              change_index_mode=mode, orientation_mag=float(mag))
    envs, obs0 = bu.build_env_batch(spec, n_trials, rng, env_kwargs=env_kwargs,
                                    randomize_cue_position=False, randomize_color=True)
    rec = dd.record_rollout(model, envs, obs0, device, policy="argmax",
                            attn_bias=attn_bias, record_latents=False, record_quad=False)
    hit = rec["hit"]
    rt = rec["rt"][~np.isnan(rec["rt"])]
    ct = change_time
    vadv = float((rec["q_press"][ct] - rec["q_wait"][ct]).mean())
    qent = float(rec["qent_press"][ct].mean())
    qstd = float(rec["qstd_press"][ct].mean())
    polent = float(rec["pol_entropy"][ct].mean())
    return {
        "hit_rate": float(hit.mean()),
        "median_rt": float(np.median(rt)) if rt.size else float("nan"),
        "premature_rate": float(rec["premature"].mean()),
        "v_press_minus_wait": vadv, "qent_press": qent, "qstd_press": qstd,
        "pol_entropy": polent, "n_hits": int(rt.size),
    }


def _region_bias(model, device, *, stream, region, value, quad=None, head=None):
    """Build a (2, n_heads, N) attention-bias tensor for one stream/region.
    head=None → all heads (dd.make_attn_bias handles the all-heads fill)."""
    return dd.make_attn_bias(model, device, stream=stream, head=head,
                             region=region, value=float(value), quad=quad)


def sweep_region(model, device, env_kwargs, *, stream, region, biases, mag, ring,
                 change_time, n_trials, base_seed, mode, quad=None, per_head=False,
                 cue="left"):
    """Sweep an additive bias over `biases` for one (stream, region[, quad]).
    All bias levels (incl. b=0) use the SAME trial seed so the contrast is paired."""
    out: Dict[str, object] = {"all_heads": []}
    seed = base_seed
    for b in biases:
        bias = None if b == 0 else _region_bias(model, device, stream=stream,
                                                region=region, value=b, quad=quad, head=None)
        r = behaviour_under_bias(model, device, env_kwargs, attn_bias=bias, mag=mag,
                                 ring=ring, change_time=change_time, n_trials=n_trials,
                                 seed=seed, mode=mode, cue=cue)
        r["bias"] = float(b)
        out["all_heads"].append(r)
    if per_head:
        ph: Dict[str, List] = {}
        nH = model.encoder.n_heads
        for h in range(nH):
            rows = []
            for b in biases:
                bias = None if b == 0 else _region_bias(model, device, stream=stream,
                                                        region=region, value=b, quad=quad, head=h)
                r = behaviour_under_bias(model, device, env_kwargs, attn_bias=bias, mag=mag,
                                         ring=ring, change_time=change_time, n_trials=n_trials,
                                         seed=seed, mode=mode, cue=cue)
                r["bias"] = float(b)
                rows.append(r)
            ph[f"H{h}"] = rows
        out["per_head"] = ph
    return out


def _delta(rows, key):
    """Signed change from the most-negative to the most-positive bias level."""
    return rows[-1][key] - rows[0][key]


def main(argv=None):
    global _LOGF
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=dd.DEFAULT_CKPT)
    ap.add_argument("--config", default=None)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=200)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--ring", type=float, default=0.75)
    ap.add_argument("--mag", type=float, default=14.0,
                    help="near-threshold |Δθ| with room to move")
    ap.add_argument("--biases", type=float, nargs="+",
                    default=[-6, -4, -2, -1, 0, 1, 2, 4, 6])
    ap.add_argument("--per-head", action="store_true",
                    help="also run the (slow) per-head sweeps for sal_all & td_all")
    args = ap.parse_args(argv)

    os.makedirs(FIGS, exist_ok=True)
    os.makedirs(TABS, exist_ok=True)
    _LOGF = open(LOG, "w")

    device = dd.select_device(args.device)
    cfg = dd.load_config(args.config)
    model = dd.build_model(cfg, device)
    it = dd.load_checkpoint(model, args.checkpoint, device)
    env_kwargs = dict(min_change_time=int(cfg["environment"]["min_change_time"]),
                      max_change_time=int(cfg["environment"]["max_change_time"]))
    enc = model.encoder
    nH = enc.n_heads
    log(f"[loaded] {args.checkpoint} (iter={it}) device={device}  "
        f"dual-stream {nH}H/stream, N={model.n_tokens}  "
        f"(salience keys=H1 rows, top-down keys=H2 rows)")
    log(f"[setup] near-threshold |Δθ|={args.mag} ring={args.ring} "
        f"change@t={args.change_time} n={args.n_trials} biases={args.biases}")

    biases = args.biases
    seed0 = args.seed + 1  # paired trial seed shared across all sweeps

    base = behaviour_under_bias(model, device, env_kwargs, attn_bias=None, mag=args.mag,
                                ring=args.ring, change_time=args.change_time,
                                n_trials=args.n_trials, seed=seed0, mode="cued")
    log(f"[baseline cued] hit={base['hit_rate']:.3f} rt={base['median_rt']:.2f} "
        f"prem={base['premature_rate']:.3f} Vadv={base['v_press_minus_wait']:.3f} "
        f"qent={base['qent_press']:.3f} qstd={base['qstd_press']:.3f} "
        f"Hpi={base['pol_entropy']:.3f}")

    results: Dict[str, object] = {
        "checkpoint": args.checkpoint, "iter": it, "biases": biases,
        "mag": args.mag, "ring": args.ring, "change_time": args.change_time,
        "n_trials": args.n_trials, "baseline_cued": base, "sweeps": {},
    }

    # ── region sweeps (all-heads), change in CUED quadrant (cue fixed left=S1) ──
    log("\n=== ALL-HEADS region sweeps (change_index_mode='cued', cue=left → changed quad=S1) ===")
    CUED = bu.CUED_QUADRANT["left"]   # = 0 (S1)
    region_specs = [
        ("sal_all",   "sal", "all",  None, "salience keys (bottom-up readout gain), all heads"),
        ("td_all",    "td",  "all",  None, "top-down keys (expectation gain), all heads"),
        ("sal_cued",  "sal", "quad", CUED, "salience keys of the cued/changed quadrant (S1)"),
        ("td_cued",   "td",  "quad", CUED, "top-down keys of the cued/changed quadrant (S1)"),
        ("sal_uncued","sal", "quad", 3,    "salience keys of an UNCUED quadrant (S4)"),
    ]
    for name, stream, region, quad, desc in region_specs:
        sw = sweep_region(model, device, env_kwargs, stream=stream, region=region,
                          biases=biases, mag=args.mag, ring=args.ring,
                          change_time=args.change_time, n_trials=args.n_trials,
                          base_seed=seed0, mode="cued", quad=quad,
                          per_head=(args.per_head and name in ("sal_all", "td_all")))
        results["sweeps"][name] = sw
        rows = sw["all_heads"]
        log(f"\n[{name}] {desc}")
        log("  b      hit    rt    prem    Vadv    qent    qstd    Hpi")
        for r in rows:
            log(f"  {r['bias']:+5.1f}  {r['hit_rate']:.3f}  "
                f"{r['median_rt'] if not np.isnan(r['median_rt']) else float('nan'):>4}  "
                f"{r['premature_rate']:.3f}  {r['v_press_minus_wait']:+.3f}  "
                f"{r['qent_press']:+.3f}  {r['qstd_press']:.3f}  {r['pol_entropy']:.3f}")
        log(f"  Δ(full sweep): hit={_delta(rows,'hit_rate'):+.3f} "
            f"prem={_delta(rows,'premature_rate'):+.3f} "
            f"Vadv={_delta(rows,'v_press_minus_wait'):+.3f} "
            f"qent={_delta(rows,'qent_press'):+.3f} Hpi={_delta(rows,'pol_entropy'):+.3f}")

    # ── invalid-alignment control: change FIXED at S1, cue FIXED right (S4) ─────
    log("\n=== Invalid-alignment control: change ALWAYS at S1, cue FIXED right (cued quad=S4) ===")
    base_s1 = behaviour_under_bias(model, device, env_kwargs, attn_bias=None, mag=args.mag,
                                   ring=args.ring, change_time=args.change_time,
                                   n_trials=args.n_trials, seed=seed0, mode=0, cue="right")
    results["baseline_changeS1_cueright"] = base_s1
    log(f"[baseline changeS1/cueS4] hit={base_s1['hit_rate']:.3f} prem={base_s1['premature_rate']:.3f} "
        f"Vadv={base_s1['v_press_minus_wait']:+.3f} qent={base_s1['qent_press']:.3f}")
    for name, stream, region, quad in [("sal_changeS1_invalid", "sal", "quad", 0),
                                       ("td_changeS1_invalid",  "td",  "quad", 0),
                                       ("sal_all_invalid",      "sal", "all",  None),
                                       ("td_all_invalid",       "td",  "all",  None)]:
        sw = sweep_region(model, device, env_kwargs, stream=stream, region=region,
                          biases=biases, mag=args.mag, ring=args.ring,
                          change_time=args.change_time, n_trials=args.n_trials,
                          base_seed=seed0, mode=0, quad=quad, per_head=False, cue="right")
        results["sweeps"][name] = sw
        rows = sw["all_heads"]
        log(f"[{name}] Δ hit={_delta(rows,'hit_rate'):+.3f} "
            f"prem={_delta(rows,'premature_rate'):+.3f} "
            f"Vadv={_delta(rows,'v_press_minus_wait'):+.3f} "
            f"qent={_delta(rows,'qent_press'):+.3f}")

    # ── save JSON + a compact summary table ────────────────────────────────────
    with open(f"{TABS}/exp4_causal.json", "w") as f:
        json.dump(results, f, indent=2)

    def classify(rows):
        dh = abs(_delta(rows, "hit_rate"))
        dp = abs(_delta(rows, "premature_rate"))
        dv = abs(_delta(rows, "v_press_minus_wait"))
        de = abs(_delta(rows, "qent_press"))
        decision = max(dh, dp)
        uncertainty = max(dv, de)
        if decision >= 0.05 and decision >= uncertainty:
            verdict = "DECISION-moving"
        elif uncertainty >= 0.05:
            verdict = "uncertainty/value-moving"
        else:
            verdict = "inert"
        return decision, uncertainty, verdict

    lines = ["region\t|Δhit|\t|Δprem|\t|ΔVadv|\t|Δqent|\tdecision\tuncertainty\tverdict"]
    for name, sw in results["sweeps"].items():
        rows = sw["all_heads"]
        dec, unc, verdict = classify(rows)
        lines.append(f"{name}\t{abs(_delta(rows,'hit_rate')):.3f}\t"
                     f"{abs(_delta(rows,'premature_rate')):.3f}\t"
                     f"{abs(_delta(rows,'v_press_minus_wait')):.3f}\t"
                     f"{abs(_delta(rows,'qent_press')):.3f}\t"
                     f"{dec:.3f}\t{unc:.3f}\t{verdict}")
    with open(f"{TABS}/exp4_summary.tsv", "w") as f:
        f.write("\n".join(lines) + "\n")
    log("\n=== DECISION-vs-UNCERTAINTY summary ===")
    for ln in lines:
        log(ln)

    # ── plots ──────────────────────────────────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})

    cued_regions = ["sal_all", "td_all", "sal_cued", "td_cued", "sal_uncued"]
    cmap = plt.get_cmap("tab10")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    for i, name in enumerate(cued_regions):
        rows = results["sweeps"][name]["all_heads"]
        c = cmap(i)
        axes[0].plot(biases, [r["hit_rate"] for r in rows], "o-", color=c, lw=1.4, label=name)
        axes[1].plot(biases, [r["median_rt"] for r in rows], "o-", color=c, lw=1.4)
        axes[2].plot(biases, [r["premature_rate"] for r in rows], "o-", color=c, lw=1.4)
    for a, ttl, yl, bl in zip(axes, ["P(hit)", "median RT", "premature rate"],
                              ["P(hit)", "RT", "premature"],
                              [base["hit_rate"], base["median_rt"], base["premature_rate"]]):
        a.axvline(0, color="grey", ls=":")
        a.axhline(bl, color="k", ls="--", alpha=.4, label="baseline")
        a.set_xlabel("attention bias b (logits)")
        a.set_ylabel(yl); a.set_title(ttl); a.grid(alpha=.3)
    axes[0].legend(fontsize=7)
    fig.suptitle(f"Causal dual-stream attention bias → behaviour (all heads)  ·  "
                 f"change in cued quadrant  ·  |Δθ|={args.mag}  ·  n={args.n_trials}")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp4_region_behaviour.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    for name, c in [("sal_all", "tab:blue"), ("td_all", "tab:red")]:
        rows = results["sweeps"][name]["all_heads"]
        axes[0].plot(biases, [r["v_press_minus_wait"] for r in rows], "o-", color=c, label=name)
        axes[1].plot(biases, [r["qent_press"] for r in rows], "o-", color=c, label=name)
        axes[2].plot(biases, [r["pol_entropy"] for r in rows], "o-", color=c, label=name)
    axes[0].set_title("Q(press)−Q(wait) at change"); axes[0].set_ylabel("value advantage")
    axes[1].set_title("critic quantile entropy"); axes[1].set_ylabel("qent (press)")
    axes[2].set_title("policy entropy"); axes[2].set_ylabel("Hpi (nats)")
    for a in axes:
        a.axvline(0, color="grey", ls=":"); a.set_xlabel("attention bias b (all heads)")
        a.grid(alpha=.3); a.legend(fontsize=8)
    fig.suptitle("Salience (bottom-up) vs Top-down attention gain → value & uncertainty")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp4_salience_vs_topdown_value.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    have_perhead = any("per_head" in results["sweeps"][n] for n in ("sal_all", "td_all"))
    if have_perhead:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
        for ax, name in zip(axes, ["sal_all", "td_all"]):
            ph = results["sweeps"][name].get("per_head", {})
            for h, (key, rows) in enumerate(ph.items()):
                ax.plot(biases, [r["hit_rate"] for r in rows], "o-", lw=1.1, alpha=.8,
                        color=cmap(h), label=key)
            ax.axvline(0, color="grey", ls=":")
            ax.axhline(base["hit_rate"], color="k", ls="--", alpha=.4)
            ax.set_xlabel("attention bias b (single head)"); ax.set_ylabel("P(hit)")
            ax.set_title(f"per-head {name} bias"); ax.grid(alpha=.3); ax.legend(fontsize=6, ncol=2)
        fig.suptitle("Per-head causal bias on salience vs top-down keys → P(hit)")
        fig.tight_layout()
        fig.savefig(f"{FIGS}/exp4_perhead_hit.png", dpi=130, bbox_inches="tight")
        plt.close(fig)

    log(f"\n[saved] {TABS}/exp4_causal.json")
    log(f"[saved] {TABS}/exp4_summary.tsv")
    log(f"[saved] {FIGS}/exp4_region_behaviour.png, exp4_salience_vs_topdown_value.png"
        + (", exp4_perhead_hit.png" if have_perhead else ""))
    log("[done]")
    if _LOGF is not None:
        _LOGF.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
