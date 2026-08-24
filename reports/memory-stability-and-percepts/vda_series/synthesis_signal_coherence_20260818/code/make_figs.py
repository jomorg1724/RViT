#!/usr/bin/env python3
"""Figures for the VDA signal-coherence synthesis."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

VDA = Path(r"C:\Users\jomor\OneDrive\Desktop\RViT_plus_paper_jepa_grid9-20260718T193411Z-1-001"
           r"\RViT_plus_paper_jepa_grid9\reports\vda_series")
OUT = Path(r"C:\Users\jomor\runpod_rescue\20260817\vda_synth\figs")
OUT.mkdir(parents=True, exist_ok=True)

MAG = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0]
I18 = MAG.index(18.0)
UNIFORM = 0.25

BLUE, RED, GREEN, GREY, ORANGE = "#1f5fa8", "#b3282d", "#2e7d32", "#6b6b6b", "#b26a00"
plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.5,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150,
})


def load(p):
    return json.loads((VDA / p).read_text())


vda4 = load("memory_noise_comparison_20260804/memory_noise_no_noise.json")
noisy = load("memory_noise_comparison_20260804/memory_noise_noise0p5.json")
v16c = load("baseline_sdt_decomposition_20260726/baseline_sdt_vda16_crossattn1.json")
v16a = load("baseline_sdt_decomposition_20260726/baseline_sdt_vda16_affine_ew.json")
iv = load("vda16_affine_change_location_intervention_20260729_v2/SUMMARY.json")
ss = load("spatial_scaling_evaluation_production_20260727/synthesis_seed0_v3/SUMMARY.json")


def cue_curves(d, idx=I18):
    dd = [d["dprime_valid"][v][idx] - d["dprime_invalid"][v][idx]
          for v in range(len(d["dprime_valid"]))]
    dc = [d["criterion_valid"][v][idx] - d["criterion_invalid"][v][idx]
          for v in range(len(d["criterion_valid"]))]
    return d["validities"], dd, dc


# ── Figure 1: set-size effect is a sensitivity effect ────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
for d, colour, label, mark in ((vda4, BLUE, "VDA4 (4 items)", "o"),
                               (v16c, RED, "VDA16 (16 items)", "s")):
    vals, dd, dc = cue_curves(d)
    axes[0].plot(vals, dd, mark + "-", color=colour, lw=1.4, ms=5, label=label)
    axes[1].plot(vals, dc, mark + "-", color=colour, lw=1.4, ms=5, label=label)
axes[0].set_ylabel("valid $-$ invalid $d'$ at $18\\degree$")
axes[0].set_title("a  Sensitivity gain grows with set size", loc="left", fontweight="bold")
axes[0].axhline(0, color="k", lw=0.7)
axes[0].set_ylim(-0.1, 1.45)
axes[1].set_ylabel("valid $-$ invalid $c$ at $18\\degree$")
axes[1].set_title("b  Criterion also shifts", loc="left", fontweight="bold")
axes[1].axhline(0, color="k", lw=0.7)
for ax in axes:
    ax.set_xlabel("displayed cue validity")
    ax.set_xticks([0.25, 0.5, 0.75, 1.0])
    ax.legend(frameon=False, loc="best")
fig.tight_layout(); fig.savefig(OUT / "fig1_setsize_sdt.pdf"); plt.close(fig)

# ── Figure 2: the selection lives in the memory stream ───────────────────────
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
keys = [("cue_period_cued_image_mass", "image"), ("cue_period_cued_memory_mass", "memory")]
keys2 = [("change_period_target_image_mass", "image"), ("change_period_target_memory_mass", "memory")]
for ax, (title, kk) in zip(axes, [("a  Cue period: cued location", keys),
                                  ("b  Change period: true change location", keys2)]):
    width = 0.35
    x = np.arange(2)
    for offset, (d, colour, lab) in ((-width / 2, (vda4, BLUE, "clean")),
                                     (+width / 2, (noisy, ORANGE, "memory noise SD 0.5"))):
        vals = [np.mean(d["attention_near_18deg"][k]) for k, _ in kk]
        errs = [np.ptp(d["attention_near_18deg"][k]) / 2 for k, _ in kk]
        ax.bar(x + offset, vals, width, yerr=errs, capsize=3, color=colour, alpha=0.9, label=lab)
    ax.axhline(UNIFORM, color="k", ls="--", lw=0.9)
    ax.set_xticks(x); ax.set_xticklabels([lab for _, lab in kk])
    ax.set_xlabel("attention source")
    ax.set_title(title, loc="left", fontweight="bold")
axes[0].set_ylabel("attention mass")
axes[0].text(1.35, UNIFORM + 0.015, "uniform 0.25", fontsize=7)
axes[0].legend(frameon=False, loc="upper left")
axes[0].set_ylim(0, 0.72)
fig.tight_layout(); fig.savefig(OUT / "fig2_source_dissociation.pdf"); plt.close(fig)

# ── Figure 3: cue-conditioned grading, and its loss under noise ──────────────
fig, ax = plt.subplots(figsize=(4.3, 2.8))
vals = [0.25, 0.5, 0.75]
for d, colour, lab, ls in ((vda4, BLUE, "clean", "-"), (noisy, ORANGE, "memory noise SD 0.5", "--")):
    a = d["attention_near_18deg"]
    ax.plot(vals, a["change_period_target_memory_mass"], "o" + ls, color=colour, lw=1.5,
            ms=5, label=f"{lab}: change period")
    ax.plot(vals, a["cue_period_cued_memory_mass"], "s" + ls, color=colour, lw=1.2,
            ms=4, alpha=0.55, label=f"{lab}: cue period")
ax.axhline(UNIFORM, color="k", ls=":", lw=0.9)
ax.text(0.255, UNIFORM + 0.012, "uniform", fontsize=7)
ax.set_xlabel("displayed cue validity"); ax.set_ylabel("memory attention mass")
ax.set_xticks(vals)
ax.set_title("Cue-conditioned grading is lost under noise", loc="left", fontweight="bold")
ax.legend(frameon=False, fontsize=6.8, loc="upper left", ncol=1)
ax.set_ylim(0.1, 0.78)
fig.tight_layout(); fig.savefig(OUT / "fig3_validity_grading.pdf"); plt.close(fig)

# ── Figure 4: causal specificity ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
sites = [("change", "true change\nlocation (15)", GREEN),
         ("cued", "cued but wrong\nlocation (0)", RED),
         ("control", "neutral control\nlocation (5)", GREY)]
x = np.arange(3)
axes[0].bar(x, [iv["effects"][s]["dprime_boost_minus_suppress"] for s, _, _ in sites],
            0.6, color=[c for _, _, c in sites], alpha=0.9)
axes[0].set_ylabel("$\\Delta d'$ (boost $-$ suppress)")
axes[0].set_title("a  Routing is causally load-bearing", loc="left", fontweight="bold")
axes[0].axhline(0, color="k", lw=0.7)
for s, (site, _, _) in enumerate(sites):
    e = iv["effects"][site]
    axes[1].plot([0, 1, 2], [e["response_rate_suppress"], e["response_rate_natural"],
                             e["response_rate_boost"]], "o-", color=sites[s][2], lw=1.5, ms=5,
                 label=sites[s][1].replace("\n", " "))
axes[1].set_xticks([0, 1, 2]); axes[1].set_xticklabels(["suppress", "natural", "boost"])
axes[1].set_ylabel("detection rate")
axes[1].set_title("b  Rescue of a missed change", loc="left", fontweight="bold")
axes[1].legend(frameon=False, loc="lower right", fontsize=6.8)
for ax in (axes[0],):
    ax.set_xticks(x); ax.set_xticklabels([l for _, l, _ in sites], fontsize=7.5)
fig.tight_layout(); fig.savefig(OUT / "fig4_causal_specificity.pdf"); plt.close(fig)

# ── Figure 5: discretization control ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
rows = ss["metrics_at_100pct_validity"]
fams = {"Cross-attention": BLUE, "Affine EW": RED}
for fam, colour in fams.items():
    sel = sorted([r for r in rows if r["model"] == fam], key=lambda r: r["n_tokens"])
    toks = [r["n_tokens"] for r in sel]
    axes[0].plot(toks, [r["threshold_cost_invalid_minus_valid_deg"] for r in sel],
                 "o-", color=colour, lw=1.5, ms=5, label=fam)
    axes[1].plot(toks, [r["causal_dependence_natural_minus_disable_pp"] for r in sel],
                 "o-", color=colour, lw=1.5, ms=5, label=fam)
for ax, ylab, title in ((axes[0], "invalid $-$ valid threshold (deg)",
                         "a  Cueing cost does not grow with resolution"),
                        (axes[1], "natural $-$ disable response (pp)",
                         "b  Causal dependence is family-specific")):
    ax.set_xscale("log"); ax.set_xticks([4, 16, 100])
    ax.set_xticklabels(["4", "16", "100"])
    ax.set_xlabel("tokens (task fixed at 4 physical regions)")
    ax.set_ylabel(ylab); ax.set_title(title, loc="left", fontweight="bold")
    ax.legend(frameon=False, loc="best")
fig.tight_layout(); fig.savefig(OUT / "fig5_discretization.pdf"); plt.close(fig)

# ── Figure 6: lever magnitudes ───────────────────────────────────────────────
vals4, dd4, _ = cue_curves(vda4)
vals16, dd16, _ = cue_curves(v16c)
levers = [
    ("Routing intervention\n(true location, VDA16)", iv["effects"]["change"]["dprime_boost_minus_suppress"], GREEN),
    ("Cue validity within VDA16\n(0.25 $\\rightarrow$ 1.0)", dd16[-1] - dd16[0], BLUE),
    ("Cue validity within VDA4\n(0.25 $\\rightarrow$ 0.75)", dd4[2] - dd4[0], BLUE),
    ("Set size 4 $\\rightarrow$ 16\n(mean over validity)", np.mean(dd16[:3]) - np.mean(dd4[:3]), ORANGE),
    ("Memory noise SD 0.5\n(VDA4, mean over validity)",
     np.mean([noisy["dprime_valid"][v][I18] - noisy["dprime_invalid"][v][I18] for v in range(3)])
     - np.mean(dd4[:3]), GREY),
]
fig, ax = plt.subplots(figsize=(6.0, 2.9))
y = np.arange(len(levers))[::-1]
ax.barh(y, [v for _, v, _ in levers], 0.62, color=[c for _, _, c in levers], alpha=0.9)
ax.set_yticks(y); ax.set_yticklabels([n for n, _, _ in levers], fontsize=7.2)
ax.axvline(0, color="k", lw=0.7)
ax.set_xlabel("change in the cueing effect, $d'$ units")
ax.set_title("How much each lever moves the attention effect", loc="left", fontweight="bold")
for yy, (_, v, _) in zip(y, levers):
    ax.text(v + (0.045 if v >= 0 else -0.045), yy, f"{v:+.2f}",
            va="center", ha="left" if v >= 0 else "right", fontsize=7.5)
ax.set_xlim(-0.3, 2.65)
fig.tight_layout(); fig.savefig(OUT / "fig6_levers.pdf"); plt.close(fig)

print("wrote 6 figures to", OUT)
for name, v, _ in levers:
    print(f"  lever {name.splitlines()[0]:<42} {v:+.3f}")
