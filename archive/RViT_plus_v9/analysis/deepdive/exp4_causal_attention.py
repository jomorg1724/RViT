"""
EXP 4 — Causal manipulation of attention (v5_part2): which attention lever moves
the DECISION, and which only moves uncertainty / value?

v5_part2's encoder is a CROSS-ATTENTION-over-memory block: the N patch tokens are
the QUERIES and the keys/values are 3N tokens ordered [patch(0:N) ++ H1(N:2N) ++
H2(2N:3N)]. Empirically the model spends ~90% of its attention mass on the 2N
memory keys and only ~10% on the N patch keys, so the natural causal contrasts
differ from v5's "patch-gain only" sweep:

  region "patch"  : add bias b to all N patch keys of a head (image-gain lever)
  region "memory" : add bias b to the 2N memory keys (H1+H2) of a head
                    (recurrent-readout lever)  — the patch↔memory tug-of-war
  region "quad"   : add bias b to the patch tokens of ONE quadrant (spatial lever)
  region "memquad": add bias b to the memory tokens (both H1+H2) of ONE quadrant

We inject the additive bias into the PRE-SOFTMAX cross-attention logits of a
single (block, head) [there is only tx_layers=1 block × 8 heads], re-run the
behaviour under the argmax policy and measure the causal effect on:
    P(hit), median RT, premature-press rate                  (the DECISION)
    Q(press)−Q(wait) advantage, critic quantile entropy/std, policy entropy
                                                             (VALUE / uncertainty)
read at a fixed near-threshold |Δθ| where there is room to move.

Spatial dissociation:  change_index_mode="cued" makes the change land in the
cued quadrant (S1 for cue-left, S4 for cue-right), so a per-trial quad bias can
target the cued==changed quadrant.  We bias S1 toward/away under cue-left trials
(and the symmetric S4 lever is reachable via region="quad", quad=3).  We also run
change_index_mode=0 (change ALWAYS at S1, cue varies) as a separate condition to
check whether the patch-vs-memory gain still moves behaviour when the change is
spatially fixed.

NOTE vs v5:  v5 read decoder/CLS attention; v5_part2's decoders are 1D-conv heads
with NO attention, so there is no decoder-attention lever to perturb — every
intervention here is on the ENCODER cross-attention only. Where v5 used
``model.encoder.n_layers`` / ``enc[0].self_attn.num_heads`` we use
``encoder.tx_layers`` / ``encoder.n_heads``.

Usage:
  .venv/bin/python -m RViT_plus_v9.analysis.deepdive.exp4_causal_attention \
      --n-trials 256 --device cpu
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

from RViT_plus_v9.analysis import _behav_utils as bu  # noqa: E402
from RViT_plus_v9.analysis.deepdive import dd_core as dd  # noqa: E402

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

    `mode` is forwarded as change_index_mode ("cued" → change in cued quadrant,
    int 0 → change always at S1). The CUE POSITION IS FIXED (`cue`, default
    'left') — never randomized: the quadrant-aligned bias regions (quad_S1,
    memquad_S1) must align with the cue/change on EVERY trial, or the lever is
    diluted ~2× by misaligned trials (the bug this fixes). Colour stays
    randomized (it is not spatially aligned).
    """
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
    ct = change_time  # value/entropy read at the change frame, averaged over trials
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


def _region_bias(model, device, *, region, value, layer=0, head=None, quad=None):
    """Build an attention-bias tensor (tx_layers, n_heads, 2N).
    v9 keys are [patch(0:N) ++ H2(N:2N)] — H1 is the query/residual, not a key —
    so the key axis is 2N, not 3N.
    If head is None, apply to ALL heads of the block; else just that head."""
    enc = model.encoder
    nL, nH = enc.tx_layers, enc.n_heads
    n_kv = (1 + (enc.n_lstm - 1)) * model.n_tokens          # 2N for n_lstm=2
    if head is not None:
        return dd.make_attn_bias(model, device, layer=layer, head=head,
                                 region=region, value=float(value), quad=quad)
    # all-heads version: OR the per-head biases together
    bias = torch.zeros(nL, nH, n_kv, device=device)
    for h in range(nH):
        bias += dd.make_attn_bias(model, device, layer=layer, head=h,
                                  region=region, value=float(value), quad=quad)
    return bias


def sweep_region(model, device, env_kwargs, *, region, biases, mag, ring,
                 change_time, n_trials, base_seed, mode, quad=None, per_head=False,
                 cue="left"):
    """Sweep an additive bias over `biases` for one region.

    Returns dict: {"all_heads": [rows], "per_head": {LxHy: [rows]}}.
    All bias levels (incl. b=0) use the SAME trial seed so the contrast is paired.
    """
    out: Dict[str, object] = {"all_heads": []}
    seed = base_seed
    for b in biases:
        bias = None if b == 0 else _region_bias(model, device, region=region,
                                                 value=b, head=None, quad=quad)
        r = behaviour_under_bias(model, device, env_kwargs, attn_bias=bias, mag=mag,
                                 ring=ring, change_time=change_time, n_trials=n_trials,
                                 seed=seed, mode=mode, cue=cue)
        r["bias"] = float(b)
        out["all_heads"].append(r)
    if per_head:
        ph: Dict[str, List] = {}
        nH = model.encoder.n_heads
        for h in range(nH):
            key = f"L1H{h}"
            rows = []
            for b in biases:
                bias = None if b == 0 else _region_bias(model, device, region=region,
                                                         value=b, head=h, quad=quad)
                r = behaviour_under_bias(model, device, env_kwargs, attn_bias=bias, mag=mag,
                                         ring=ring, change_time=change_time, n_trials=n_trials,
                                         seed=seed, mode=mode, cue=cue)
                r["bias"] = float(b)
                rows.append(r)
            ph[key] = rows
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
    ap.add_argument("--device", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-trials", type=int, default=256)
    ap.add_argument("--change-time", type=int, default=15)
    ap.add_argument("--ring", type=float, default=0.75)
    ap.add_argument("--mag", type=float, default=10.0,
                    help="near-threshold |Δθ| with room to move")
    ap.add_argument("--biases", type=float, nargs="+",
                    default=[-6, -4, -2, -1, 0, 1, 2, 4, 6])
    ap.add_argument("--per-head", action="store_true",
                    help="also run the (slow) per-head sweeps for patch & memory regions")
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
    nL, nH, n_lstm = enc.tx_layers, enc.n_heads, enc.n_lstm
    log(f"[loaded] {args.checkpoint} (iter={it}) device={device}  "
        f"encoder cross-attn {nL}block×{nH}H, {n_lstm} mem-LSTMs, N={model.n_tokens} "
        f"(keys = {(1+n_lstm)}N = patch++H1++H2)")
    log(f"[setup] near-threshold |Δθ|={args.mag} ring={args.ring} "
        f"change@t={args.change_time} n={args.n_trials} biases={args.biases}")
    log("[note] v5_part2 decoders are 1D-conv heads (no attention) — every lever "
        "below perturbs the ENCODER cross-attention only.")

    biases = args.biases
    seed0 = args.seed + 1  # paired trial seed shared across all sweeps

    # baseline (unbiased), reported once
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

    # ── region sweeps (all-heads), change in cued quadrant ────────────────────
    log("\n=== ALL-HEADS region sweeps (change_index_mode='cued') ===")
    region_specs = [
        ("patch",   None, "patch keys (image gain), all heads"),
        ("memory",  None, "memory keys H1+H2 (recurrent readout), all heads"),
        ("quad_S1", "quad", "patch keys of S1 (top-left)"),
        ("quad_S4", "quad", "patch keys of S4 (bottom-right)"),
        ("memquad_S1", "memquad", "memory keys of S1 quadrant"),
    ]
    for name, region, desc in region_specs:
        q = None
        reg = region if region else name
        if name == "quad_S1":
            reg, q = "quad", 0
        elif name == "quad_S4":
            reg, q = "quad", 3
        elif name == "memquad_S1":
            reg, q = "memquad", 0
        sw = sweep_region(model, device, env_kwargs, region=reg, biases=biases,
                          mag=args.mag, ring=args.ring, change_time=args.change_time,
                          n_trials=args.n_trials, base_seed=seed0, mode="cued",
                          quad=q, per_head=(args.per_head and name in ("patch", "memory")))
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

    # ── invalid-alignment control: change FIXED at S1, cue FIXED at S4 ────────
    log("\n=== Invalid-alignment control: change ALWAYS at S1, cue FIXED right (S4) ===")
    base_s1 = behaviour_under_bias(model, device, env_kwargs, attn_bias=None, mag=args.mag,
                                   ring=args.ring, change_time=args.change_time,
                                   n_trials=args.n_trials, seed=seed0, mode=0, cue="right")
    results["baseline_changeS1_cueright"] = base_s1
    log(f"[baseline changeS1/cueS4] hit={base_s1['hit_rate']:.3f} prem={base_s1['premature_rate']:.3f} "
        f"Vadv={base_s1['v_press_minus_wait']:+.3f} qent={base_s1['qent_press']:.3f}")
    for name, reg, q in [("S1_patch_invalid", "quad", 0),
                         ("S4_patch_invalid", "quad", 3),
                         ("patch_invalid", "patch", None),
                         ("memory_invalid", "memory", None),
                         ("memquad_S1_invalid", "memquad", 0)]:
        sw = sweep_region(model, device, env_kwargs, region=reg, biases=biases,
                          mag=args.mag, ring=args.ring, change_time=args.change_time,
                          n_trials=args.n_trials, base_seed=seed0, mode=0, quad=q,
                          per_head=False, cue="right")
        results["sweeps"][name] = sw
        rows = sw["all_heads"]
        log(f"[{name}] Δ hit={_delta(rows,'hit_rate'):+.3f} "
            f"prem={_delta(rows,'premature_rate'):+.3f} "
            f"Vadv={_delta(rows,'v_press_minus_wait'):+.3f} "
            f"qent={_delta(rows,'qent_press'):+.3f}")

    # ── save JSON + a compact summary table ───────────────────────────────────
    with open(f"{TABS}/exp4_causal.json", "w") as f:
        json.dump(results, f, indent=2)

    # decision-vs-uncertainty classification table
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

    # ── plots ─────────────────────────────────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9})

    # Fig 1: region sweeps (cued) — behaviour
    cued_regions = ["patch", "memory", "quad_S1", "quad_S4", "memquad_S1"]
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
        a.set_ylabel(yl)
        a.set_title(ttl)
        a.grid(alpha=.3)
    axes[0].legend(fontsize=7)
    fig.suptitle(f"Causal encoder-attention bias → behaviour (all heads)  ·  "
                 f"change in cued quadrant  ·  |Δθ|={args.mag}  ·  n={args.n_trials}")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp4_region_behaviour.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # Fig 2: patch vs memory — value / uncertainty
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    for name, c in [("patch", "tab:blue"), ("memory", "tab:red")]:
        rows = results["sweeps"][name]["all_heads"]
        axes[0].plot(biases, [r["v_press_minus_wait"] for r in rows], "o-", color=c, label=name)
        axes[1].plot(biases, [r["qent_press"] for r in rows], "o-", color=c, label=name)
        axes[2].plot(biases, [r["pol_entropy"] for r in rows], "o-", color=c, label=name)
    axes[0].set_title("Q(press)−Q(wait) at change")
    axes[0].set_ylabel("value advantage")
    axes[1].set_title("critic quantile entropy")
    axes[1].set_ylabel("qent (press)")
    axes[2].set_title("policy entropy")
    axes[2].set_ylabel("Hpi (nats)")
    for a in axes:
        a.axvline(0, color="grey", ls=":")
        a.set_xlabel("attention bias b (all heads)")
        a.grid(alpha=.3)
        a.legend(fontsize=8)
    fig.suptitle("Patch (image) vs Memory (recurrent) attention gain → value & uncertainty")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/exp4_patch_vs_memory_value.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # Fig 3: per-head hit-rate curves for patch + memory (only if --per-head)
    have_perhead = any("per_head" in results["sweeps"][n] for n in ("patch", "memory"))
    if have_perhead:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
        for ax, name in zip(axes, ["patch", "memory"]):
            ph = results["sweeps"][name].get("per_head", {})
            for h, (key, rows) in enumerate(ph.items()):
                ax.plot(biases, [r["hit_rate"] for r in rows], "o-", lw=1.1, alpha=.8,
                        color=cmap(h), label=key)
            ax.axvline(0, color="grey", ls=":")
            ax.axhline(base["hit_rate"], color="k", ls="--", alpha=.4)
            ax.set_xlabel("attention bias b (single head)")
            ax.set_ylabel("P(hit)")
            ax.set_title(f"per-head {name}-key bias")
            ax.grid(alpha=.3)
            ax.legend(fontsize=6, ncol=2)
        fig.suptitle("Per-head causal bias on patch vs memory keys → P(hit)")
        fig.tight_layout()
        fig.savefig(f"{FIGS}/exp4_perhead_hit.png", dpi=130, bbox_inches="tight")
        plt.close(fig)

    log(f"\n[saved] {TABS}/exp4_causal.json")
    log(f"[saved] {TABS}/exp4_summary.tsv")
    log(f"[saved] {FIGS}/exp4_region_behaviour.png, exp4_patch_vs_memory_value.png"
        + (", exp4_perhead_hit.png" if have_perhead else ""))
    log("[done]")
    if _LOGF is not None:
        _LOGF.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
