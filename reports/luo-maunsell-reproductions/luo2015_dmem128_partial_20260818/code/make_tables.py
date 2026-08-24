#!/usr/bin/env python3
"""Print the per-location SDT table and the d' threshold for specificity."""
import json
from pathlib import Path

REPORT = Path(r"C:\Users\jomor\runpod_rescue\20260817\report")
S = json.loads((REPORT / "analysis_summary.json").read_text())
PARENT = json.loads(Path(
    r"C:\Users\jomor\Documents\RViT_runs\analyses\luo_dualstream_dmem64_terminal_sdt_20260817"
    r"\results\selected_replication_results.json").read_text())

dlb = S["reward_schedule"]["delta_log_beta"]
print(f"delta ln beta = {dlb:.4f}")
print(f"d' needed for reward-optimal |dc| <= 0.2 (equal d' both locs): {dlb / 0.2:.3f}\n")

print(f"{'model':<28} {'loc':>4} {'d_prime':>8} {'c':>8} {'HR':>7} {'FA':>7} {'n_ch':>6} {'n_no':>6}")
for name, entry in sorted(S["own_theta"].items()):
    for loc in ("0", "3"):
        m = entry["locations"][loc]
        tag = " *" if int(loc) == entry["condition_loc"] else "  "
        print(f"{name + tag:<28} {loc:>4} {m['dprime']:>8.4f} {m['criterion']:>8.4f} "
              f"{m['hit_rate']:>7.4f} {m['false_alarm_rate']:>7.4f} "
              f"{m['n_change']:>6} {m['n_no_change']:>6}")
p = PARENT["models"][0]
for loc in ("0", "3"):
    m = p["locations"][loc]
    tag = " *" if int(loc) == p["condition_loc"] else "  "
    print(f"{'dmem64_sensitivity_loc3' + tag:<28} {loc:>4} {m['dprime']:>8.4f} {m['criterion']:>8.4f} "
          f"{m['hit_rate']:>7.4f} {m['false_alarm_rate']:>7.4f} "
          f"{m['n_change']:>6} {m['n_no_change']:>6}")
print("\n(* = high-priority / condition location)")

print("\n== ratio of observed to reward-optimal criterion shift ==")
for name, entry in sorted(S["own_theta"].items()):
    ro = entry["reward_optimal"]
    print(f"  {name}: obs/pred = {ro['delta_c_observed'] / ro['delta_c_pred']:.2f}")
pk = S["parent_dmem64"]
print(f"  dmem64_sensitivity_loc3: obs/pred = {pk['delta_criterion'] / pk['delta_c_pred']:.2f}")

print("\n== DiD table ==")
for theta in sorted(S["counterphased_did"], key=float):
    e = S["counterphased_did"][theta]
    d, c = e["dprime"], e["criterion"]
    print(f"  theta={float(theta):>4.0f}  d': {d['point']:+.4f} [{d['ci95'][0]:+.4f},{d['ci95'][1]:+.4f}]"
          f"   c: {c['point']:+.4f} [{c['ci95'][0]:+.4f},{c['ci95'][1]:+.4f}]"
          f"   c_pred: {S['reward_optimal_did'][theta]['delta_c_pred_did']:+.4f}")

print("\n== training ==")
for name, t in sorted(S["training"].items()):
    print(f"  {name}: rows={t['rows']} last_iter={t['last_iter']} "
          f"final_theta={t['final_theta']:g} final_rolling={t['final_rolling_correct']:.4f} "
          f"best_rolling={t['best_rolling_correct']:.4f}")
