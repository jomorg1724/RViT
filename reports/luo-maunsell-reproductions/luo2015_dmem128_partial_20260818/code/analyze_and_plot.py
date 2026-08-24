#!/usr/bin/env python3
"""Derive the reported quantities and figures for the d_mem=128 partial-run writeup."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RESCUE = Path(r"C:\Users\jomor\runpod_rescue\20260817")
REPORT = RESCUE / "report"
FIGS = REPORT / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

RESULTS = json.loads((RESCUE / "eval_tree" / "results" / "partial_sdt_results.json").read_text())
PARENT = json.loads(Path(
    r"C:\Users\jomor\Documents\RViT_runs\analyses\luo_dualstream_dmem64_terminal_sdt_20260817"
    r"\results\selected_replication_results.json").read_text())

BOUND = 0.2
# Sensitivity session reward schedule (envs/luo2015.py): mean reward and H:CR ratio.
HIGH_MEAN, HIGH_RATIO = 5.0, 0.7
LOW_MEAN, LOW_RATIO = 1.0, 1.1

BLUE, RED, GREY = "#1f5fa8", "#b3282d", "#666666"
plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150,
})


def hit_cr_pair(mean_reward: float, ratio: float) -> tuple[float, float]:
    cr = 2.0 * mean_reward / (1.0 + ratio)
    return ratio * cr, cr


def optimal_log_beta(ratio: float) -> float:
    """Reward-optimal log likelihood-ratio criterion for P(change)=0.5, miss=FA=0.

    beta = [P(no change)/P(change)] * [(R_CR - R_FA)/(R_H - R_miss)] = R_CR/R_H = 1/ratio.
    """
    r_hit, r_cr = hit_cr_pair(1.0, ratio)  # scale-free: beta depends only on the ratio
    return math.log(r_cr / r_hit)


LOG_BETA_HIGH = optimal_log_beta(HIGH_RATIO)
LOG_BETA_LOW = optimal_log_beta(LOW_RATIO)


def rows(branch, theta=None):
    if branch == "own_theta":
        return [r for r in RESULTS["own_theta"] if r["measurement_condition"] == "trained_noise"]
    return RESULTS["common_theta"][str(float(theta))]


def predicted_delta_c(row: dict) -> dict:
    """Reward-optimal criterion difference given the measured per-location d'."""
    cond, ctrl = int(row["condition_loc"]), int(row["control_loc"])
    d_cond = float(row["locations"][str(cond)]["dprime"])
    d_ctrl = float(row["locations"][str(ctrl)]["dprime"])
    c_cond = LOG_BETA_HIGH / d_cond
    c_ctrl = LOG_BETA_LOW / d_ctrl
    return {
        "condition_loc": cond, "d_condition": d_cond, "d_control": d_ctrl,
        "c_pred_condition": c_cond, "c_pred_control": c_ctrl,
        "delta_c_pred": c_cond - c_ctrl,
        "delta_c_observed": float(row["contrasts"]["condition_minus_control"]["criterion"]),
        "delta_d_observed": float(row["contrasts"]["condition_minus_control"]["dprime"]),
    }


summary: dict = {
    "reward_schedule": {
        "high_mean_reward": HIGH_MEAN, "high_hit_cr_ratio": HIGH_RATIO,
        "low_mean_reward": LOW_MEAN, "low_hit_cr_ratio": LOW_RATIO,
        "high_pair_hit_cr": hit_cr_pair(HIGH_MEAN, HIGH_RATIO),
        "low_pair_hit_cr": hit_cr_pair(LOW_MEAN, LOW_RATIO),
        "log_beta_high": LOG_BETA_HIGH, "log_beta_low": LOG_BETA_LOW,
        "delta_log_beta": LOG_BETA_HIGH - LOG_BETA_LOW,
    },
    "equivalence_bound": BOUND,
}

# ── per-model contrasts at own terminal theta ────────────────────────────────
own = {}
for row in rows("own_theta"):
    own[row["id"]] = {
        "iter": row["checkpoint_iteration"],
        "theta": row["evaluation_theta"],
        "condition_loc": row["condition_loc"],
        "delta_dprime": row["contrasts"]["condition_minus_control"]["dprime"],
        "delta_dprime_ci": row["contrasts"]["bootstrap_ci95"]["dprime"],
        "delta_criterion": row["contrasts"]["condition_minus_control"]["criterion"],
        "delta_criterion_ci": row["contrasts"]["bootstrap_ci95"]["criterion"],
        "strict": row["paper_like_tests"]["strict_behavioral_dissociation"],
        "locations": {loc: {k: row["locations"][loc][k]
                            for k in ("dprime", "criterion", "hit_rate", "false_alarm_rate",
                                      "n_change", "n_no_change")}
                      for loc in ("0", "3")},
        "reward_optimal": predicted_delta_c(row),
    }
summary["own_theta"] = own

# ── counterphased DiD ────────────────────────────────────────────────────────
summary["counterphased_did"] = RESULTS["counterphased_did"]

# predicted DiD for criterion at each common theta
pred_did = {}
for theta_key, models in RESULTS["common_theta"].items():
    by_cond = {int(m["condition_loc"]): m for m in models}
    preds = {cl: predicted_delta_c(m) for cl, m in by_cond.items()}
    # aligned contrasts (condition minus control) averaged = DiD
    pred_did[theta_key] = {
        "delta_c_pred_did": 0.5 * (preds[0]["delta_c_pred"] + preds[3]["delta_c_pred"]),
        "delta_c_obs_did": RESULTS["counterphased_did"][theta_key]["criterion"]["point"],
        "per_model": preds,
    }
summary["reward_optimal_did"] = pred_did

# ── parent d_mem=64 reference ────────────────────────────────────────────────
p = PARENT["models"][0]
summary["parent_dmem64"] = {
    "id": p["id"], "iter": p["checkpoint_iteration"],
    "theta": PARENT["evaluation_contract"]["theta"],
    "condition_loc": p["condition_loc"],
    "delta_dprime": p["contrasts"]["condition_minus_control"]["dprime"],
    "delta_dprime_ci": p["contrasts"]["bootstrap_ci95"]["dprime"],
    "delta_criterion": p["contrasts"]["condition_minus_control"]["criterion"],
    "delta_criterion_ci": p["contrasts"]["bootstrap_ci95"]["criterion"],
    "strict": p["paper_like_tests"]["strict_behavioral_dissociation"],
    "trials_per_status_per_location": PARENT["evaluation_contract"]["trials_per_status_per_location"],
}
# matched comparison: our loc3 cell on the common theta=50 bank
loc3_at_50 = [m for m in RESULTS["common_theta"]["50.0"] if m["condition_loc"] == 3][0]
summary["dmem128_loc3_at_theta50"] = {
    "delta_dprime": loc3_at_50["contrasts"]["condition_minus_control"]["dprime"],
    "delta_dprime_ci": loc3_at_50["contrasts"]["bootstrap_ci95"]["dprime"],
    "delta_criterion": loc3_at_50["contrasts"]["condition_minus_control"]["criterion"],
    "delta_criterion_ci": loc3_at_50["contrasts"]["bootstrap_ci95"]["criterion"],
}

# ── training curves ──────────────────────────────────────────────────────────
def load_metrics(path: Path):
    it, roll, theta, corr = [], [], [], []
    with path.open() as handle:
        for rec in csv.DictReader(handle):
            it.append(int(float(rec["iter"])))
            roll.append(float(rec["rolling/correct_rate"]))
            theta.append(float(rec["env/theta"]))
            corr.append(float(rec["rollout/correct_rate"]))
    return (np.array(it), np.array(roll), np.array(theta), np.array(corr))


curves = {
    "loc0": load_metrics(RESCUE / "loc0" / "run" / "metrics.csv"),
    "loc3": load_metrics(RESCUE / "loc3" / "run" / "metrics.csv"),
}
summary["training"] = {
    name: {"rows": int(len(c[0])), "last_iter": int(c[0][-1]),
           "final_theta": float(c[2][-1]), "final_rolling_correct": float(c[1][-1]),
           "best_rolling_correct": float(np.nanmax(c[1]))}
    for name, c in curves.items()
}

# ── Figure 1: training ───────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
for name, colour, label in (("loc0", BLUE, "high-priority loc 0"),
                            ("loc3", RED, "high-priority loc 3")):
    it, roll, theta, _ = curves[name]
    axes[0].plot(it, roll, color=colour, lw=0.9, label=label)
    axes[1].step(it, theta, color=colour, lw=1.1, where="post", label=label)
axes[0].axhline(0.85, color=GREY, ls="--", lw=0.8)
axes[0].text(300, 0.945, "curriculum threshold 0.85", color=GREY, fontsize=7)
axes[0].set_xlabel("PPO iteration"); axes[0].set_ylabel("rolling correct rate")
axes[0].set_ylim(0.3, 1.0); axes[0].legend(loc="lower right", frameon=False)
axes[0].set_title("a  Learning", loc="left", fontweight="bold")
axes[1].axhline(8.0, color=GREY, ls=":", lw=0.8)
axes[1].text(400, 9.5, "curriculum floor 8$\\degree$", color=GREY, fontsize=7)
axes[1].set_xlabel("PPO iteration"); axes[1].set_ylabel("change bound $\\theta$ (deg)")
axes[1].set_ylim(0, 70); axes[1].legend(loc="upper right", frameon=False)
axes[1].set_title("b  Curriculum depth", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(FIGS / "fig_training.pdf"); plt.close(fig)

# ── Figure 2: per-model contrasts vs equivalence band ────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7), sharey=True)
entries = [
    ("d$_{mem}$=64\nloc 3 (terminal)", summary["parent_dmem64"], GREY),
    ("d$_{mem}$=128\nloc 0 (partial)", own["dmem128_sensitivity_loc0"], BLUE),
    ("d$_{mem}$=128\nloc 3 (partial)", own["dmem128_sensitivity_loc3"], RED),
]
for ax, metric, title in ((axes[0], "delta_dprime", "a  Sensitivity effect $\\Delta d'$"),
                          (axes[1], "delta_criterion", "b  Criterion cross-effect $\\Delta c$")):
    for index, (label, entry, colour) in enumerate(entries):
        value = entry[metric]; lo, hi = entry[metric + "_ci"]
        ax.errorbar(index, value, yerr=[[value - lo], [hi - value]], fmt="o",
                    color=colour, capsize=3, ms=5, lw=1.4)
    ax.axhline(0, color="k", lw=0.7)
    if metric == "delta_criterion":
        ax.axhspan(-BOUND, BOUND, color="#2e7d32", alpha=0.13, lw=0)
        ax.text(2.42, 0.0, "equivalence\nband $\\pm$0.2", color="#2e7d32",
                fontsize=7, va="center", ha="left")
    ax.set_xticks(range(len(entries)))
    ax.set_xticklabels([e[0] for e in entries])
    ax.set_xlim(-0.5, 2.5)
    ax.set_title(title, loc="left", fontweight="bold")
axes[0].set_ylabel("condition $-$ control")
fig.tight_layout(); fig.savefig(FIGS / "fig_contrasts.pdf"); plt.close(fig)

# ── Figure 3: counterphased DiD across theta ─────────────────────────────────
thetas = sorted(float(t) for t in RESULTS["counterphased_did"])
fig, ax = plt.subplots(figsize=(4.4, 2.8))
offset = 0.55
for index, theta in enumerate(thetas):
    entry = RESULTS["counterphased_did"][str(theta)]
    for metric, colour, shift, label in (("dprime", BLUE, -offset / 2, "$\\Delta d'$ DiD"),
                                         ("criterion", RED, offset / 2, "$\\Delta c$ DiD")):
        value = entry[metric]["point"]; lo, hi = entry[metric]["ci95"]
        ax.errorbar(index + shift, value, yerr=[[value - lo], [hi - value]], fmt="o",
                    color=colour, capsize=3, ms=5, lw=1.4,
                    label=label if index == 0 else None)
ax.axhspan(-BOUND, BOUND, color="#2e7d32", alpha=0.13, lw=0)
ax.axhline(0, color="k", lw=0.7)
ax.set_xticks(range(len(thetas)))
ax.set_xticklabels([f"$\\theta$={t:g}$\\degree$" for t in thetas])
ax.set_ylabel("counterphased difference-in-differences")
ax.set_ylim(-0.05, 0.5)
ax.legend(frameon=False, loc="upper left")
ax.text(len(thetas) - 0.45, 0.0, "equivalence\nband $\\pm$0.2", color="#2e7d32",
        fontsize=7, va="center", ha="left")
ax.set_title("Counterphased effects, shared trial bank", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(FIGS / "fig_did.pdf"); plt.close(fig)

# ── Figure 4: observed vs reward-optimal criterion ───────────────────────────
fig, ax = plt.subplots(figsize=(4.4, 2.8))
labels, obs, pred, colours = [], [], [], []
for name, colour in (("dmem128_sensitivity_loc0", BLUE), ("dmem128_sensitivity_loc3", RED)):
    entry = own[name]
    labels.append(f"loc {entry['condition_loc']}\n($\\theta$={entry['theta']:g}$\\degree$)")
    obs.append(entry["delta_criterion"])
    pred.append(entry["reward_optimal"]["delta_c_pred"])
    colours.append(colour)
labels.append("d$_{mem}$=64\nloc 3 ($\\theta$=50$\\degree$)")
obs.append(summary["parent_dmem64"]["delta_criterion"])
p64 = summary["parent_dmem64"]
d_cond = PARENT["models"][0]["locations"]["3"]["dprime"]
d_ctrl = PARENT["models"][0]["locations"]["0"]["dprime"]
pred.append(LOG_BETA_HIGH / d_cond - LOG_BETA_LOW / d_ctrl)
colours.append(GREY)
summary["parent_dmem64"]["delta_c_pred"] = pred[-1]

x = np.arange(len(labels))
ax.bar(x - 0.19, pred, 0.36, color="none", edgecolor="k", lw=1.1, hatch="////",
       label="reward-optimal prediction")
ax.bar(x + 0.19, obs, 0.36, color=colours, alpha=0.85, label="observed")
ax.axhspan(-BOUND, BOUND, color="#2e7d32", alpha=0.13, lw=0)
ax.axhline(0, color="k", lw=0.7)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylim(-0.26, 0.62)
ax.set_ylabel("$\\Delta c$ (condition $-$ control)")
ax.legend(frameon=False, loc="upper left", fontsize=7.5)
ax.set_title("Criterion shift is reward-optimal", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(FIGS / "fig_reward_optimal.pdf"); plt.close(fig)

(REPORT / "analysis_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

print("== reward schedule ==")
print(f"  high loc: R_hit={hit_cr_pair(HIGH_MEAN, HIGH_RATIO)[0]:.4f} "
      f"R_cr={hit_cr_pair(HIGH_MEAN, HIGH_RATIO)[1]:.4f}  ln beta={LOG_BETA_HIGH:+.4f}")
print(f"  low  loc: R_hit={hit_cr_pair(LOW_MEAN, LOW_RATIO)[0]:.4f} "
      f"R_cr={hit_cr_pair(LOW_MEAN, LOW_RATIO)[1]:.4f}  ln beta={LOG_BETA_LOW:+.4f}")
print(f"  delta ln beta = {LOG_BETA_HIGH - LOG_BETA_LOW:+.4f}")
print("\n== own-theta contrasts (trained noise) ==")
for name, entry in own.items():
    ro = entry["reward_optimal"]
    print(f"  {name}: iter={entry['iter']} theta={entry['theta']:g} "
          f"dd'={entry['delta_dprime']:+.4f} dc_obs={entry['delta_criterion']:+.4f} "
          f"dc_pred={ro['delta_c_pred']:+.4f} strict={entry['strict']}")
print("\n== DiD: observed vs reward-optimal criterion ==")
for theta_key in sorted(pred_did, key=float):
    block = pred_did[theta_key]
    print(f"  theta={theta_key}: obs={block['delta_c_obs_did']:+.4f} "
          f"pred={block['delta_c_pred_did']:+.4f}")
print(f"\n== parent d_mem=64 (loc3 terminal, theta=50) ==")
print(f"  dd'={p64['delta_dprime']:+.4f} dc_obs={p64['delta_criterion']:+.4f} "
      f"dc_pred={summary['parent_dmem64']['delta_c_pred']:+.4f}")
print(f"\nwrote {REPORT / 'analysis_summary.json'} and 4 figures")
