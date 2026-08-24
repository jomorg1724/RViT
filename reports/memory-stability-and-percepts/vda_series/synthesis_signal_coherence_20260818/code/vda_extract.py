"""Extract the cross-experiment quantities for the VDA signal-coherence synthesis."""
import json
from pathlib import Path

VDA = Path(r"C:\Users\jomor\OneDrive\Desktop\RViT_plus_paper_jepa_grid9-20260718T193411Z-1-001"
           r"\RViT_plus_paper_jepa_grid9\reports\vda_series")

MAG = [0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 22.0, 26.0, 30.0]
I18 = MAG.index(18.0)


def load(p):
    return json.loads((VDA / p).read_text())


def cueing(d, idx=I18):
    """Return per-validity (delta d', delta c) at one magnitude."""
    out = []
    for v in range(len(d["dprime_valid"])):
        dd = d["dprime_valid"][v][idx] - d["dprime_invalid"][v][idx]
        dc = d["criterion_valid"][v][idx] - d["criterion_invalid"][v][idx]
        out.append((dd, dc))
    return out


print("=" * 78)
print("SET SIZE: historical lineage, terminal 19999, crossattn1, d_mem=128, nodecay")
print("=" * 78)
vda4 = load("memory_noise_comparison_20260804/memory_noise_no_noise.json")
vda16 = load("baseline_sdt_decomposition_20260726/baseline_sdt_vda16_crossattn1.json")
vda16a = load("baseline_sdt_decomposition_20260726/baseline_sdt_vda16_affine_ew.json")

for name, d in (("VDA4  crossattn", vda4), ("VDA16 crossattn", vda16), ("VDA16 affine_ew", vda16a)):
    rows = cueing(d)
    vals = d["validities"]
    dd = [r[0] for r in rows]
    dc = [r[1] for r in rows]
    common = [i for i, v in enumerate(vals) if v in (0.25, 0.5, 0.75)]
    print(f"\n{name}  (validities {vals})")
    print("  delta d' @18deg: " + "  ".join(f"{x:+.3f}" for x in dd))
    print("  delta c  @18deg: " + "  ".join(f"{x:+.3f}" for x in dc))
    print(f"  mean over common validities .25/.5/.75:  dd'={sum(dd[i] for i in common)/len(common):+.3f}"
          f"   dc={sum(dc[i] for i in common)/len(common):+.3f}")

r4 = cueing(vda4); r16 = cueing(vda16)
c4 = sum(r4[i][0] for i in range(3)) / 3
c16 = sum(r16[i][0] for i in range(3)) / 3
print(f"\n  SET-SIZE RATIO (crossattn, common validities): {c16/c4:.2f}x  ({c4:+.3f} -> {c16:+.3f})")

print("\n" + "=" * 78)
print("SOURCE-SEPARATED ALLOCATION: VDA4, clean vs memory-noise SD 0.5 (uniform = 0.25)")
print("=" * 78)
noisy = load("memory_noise_comparison_20260804/memory_noise_noise0p5.json")
for name, d in (("clean  (iter 19999)", vda4), ("noisy  (iter 15999)", noisy)):
    a = d["attention_near_18deg"]
    print(f"\n{name}")
    for k in ("cue_period_cued_image_mass", "cue_period_cued_memory_mass",
              "change_period_target_image_mass", "change_period_target_memory_mass"):
        vals = a[k]
        print(f"  {k:34s} " + "  ".join(f"{x:.3f}" for x in vals)
              + f"   mean={sum(vals)/len(vals):.3f}   validity-slope={vals[-1]-vals[0]:+.3f}")

print("\n  cueing effect, clean vs noisy (mean delta d' @18deg over .25/.5/.75):")
cn = sum(cueing(noisy)[i][0] for i in range(3)) / 3
print(f"    clean {c4:+.3f}   noisy {cn:+.3f}   difference {cn-c4:+.3f}")

print("\n" + "=" * 78)
print("CAUSAL INTERVENTION: VDA16 affine, forced-invalid, dose 0->1, clamp from frame 5")
print("=" * 78)
iv = load("vda16_affine_change_location_intervention_20260729_v2/SUMMARY.json")
print(f"  {'site':<22}{'loc':>5}{'resp suppress':>15}{'resp boost':>12}{'d resp':>9}{'d dprime':>10}{'mass nat':>10}")
for site in ("change", "cued", "control"):
    e = iv["effects"][site]
    print(f"  {site:<22}{e['target_location']:>5}{e['response_rate_suppress']:>15.3f}"
          f"{e['response_rate_boost']:>12.3f}{e['response_rate_boost_minus_suppress']:>+9.3f}"
          f"{e['dprime_boost_minus_suppress']:>+10.3f}{e['achieved_target_mass_natural']:>10.3f}")

print("\n" + "=" * 78)
print("DISCRETIZATION CONTROL: VDA4 task (4 physical regions) at 4/16/100 tokens")
print("=" * 78)
ss = json.loads((VDA / "spatial_scaling_evaluation_production_20260727"
                 / "synthesis_seed0_v3" / "SUMMARY.json").read_text())
print(f"  {'family':<18}{'tokens':>7}{'thresh cost':>13}{'AUC':>8}{'causal pp':>11}{'valid mass':>12}")
for r in ss["metrics_at_100pct_validity"]:
    print(f"  {r['model']:<18}{r['n_tokens']:>7}{r['threshold_cost_invalid_minus_valid_deg']:>13.2f}"
          f"{r['normalized_response_auc_valid_minus_invalid']:>8.3f}"
          f"{r['causal_dependence_natural_minus_disable_pp']:>11.1f}"
          f"{r['valid_tl_region0_mass_frames5_6']:>12.3f}")
print("\n  findings:")
for k, v in ss["interpretation"].items():
    if k.startswith("finding"):
        print(f"    - {v}")
