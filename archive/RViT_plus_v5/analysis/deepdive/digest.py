"""Consolidate every deep-dive result file into one printed digest for the paper."""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(H, "tables")


def jload(p):
    with open(os.path.join(T, p)) as f:
        return json.load(f)


def sec(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

# ── EXP1 ──
sec("EXP1  psychometrics / chronometrics")
s = jload("exp1_summary.json")
print(f"fits: valid x50={s['fits']['valid']['x50']:.2f} w={s['fits']['valid']['width']:.2f} | "
      f"invalid x50={s['fits']['invalid']['x50']:.2f} w={s['fits']['invalid']['width']:.2f}")
print(f"cueing benefit Δx50 (invalid-valid) = {s['cueing_benefit_dx50']:.2f} deg")
print("core valid:  " + "  ".join(f"{r['mag']:.0f}:{r['hit_rate']:.2f}/{r['median_rt']:.1f}" for r in s['core']['valid']))
print("core invalid:" + "  ".join(f"{r['mag']:.0f}:{r['hit_rate']:.2f}/{r['median_rt']:.1f}" for r in s['core']['invalid']))
print("ring rows:")
for r in s['ring_rows']:
    print(f"  ring={r['ring']:.2f} {r['condition']:7s} x50={r['thresh50']:.2f} slope={r['slope']:.3f}")
print("value (color):")
for c in ['blue', 'green', 'red']:
    rows = s['value'][c]
    print(f"  {c:5s}(v={rows[0]['value']}): " + " ".join(f"{r['mag']:.0f}:{r['hit_rate']:.2f}" for r in rows))
print(f"criterion: CR={s['criterion']['correct_rejection']:.3f} FA={s['criterion']['false_alarm']:.3f}")

# ── EXP3 ──
sec("EXP3  latent decoding")
d = jload("exp3_decoding.json")
print(f"n_trials={d['n_trials']}  abs_time R2={d['abs_time_r2']:.3f} (shuffle {d['abs_time_shuffle']:.3f})")
for k, v in d['peaks'].items():
    print(f"  {k:18s} peak={v['peak']:.3f} (best={v['best_latent']}, shuffle={v['shuffle']:.3f})")
    print("       per-latent: " + " ".join(f"{l}={v['per_latent'][l]:.2f}" for l in v['per_latent']))

# ── EXP4 ──
sec("EXP4  causal attention")
c = jload("exp4_causal.json")
b = c['baseline']
print(f"baseline hit={b['hit_rate']:.3f} rt={b['median_rt']:.2f} prem={b['premature_rate']:.3f} "
      f"Vadv={b['v_press_minus_wait']:.3f} qent={b['qent_press']:.3f}")
print(f"biases: {c['biases']}")
print("per-head hit-rate (b_min, b=0, b_max) and max|Δ| across sweep:")
for k, rows in c['per_head'].items():
    hits = [r['hit_rate'] for r in rows]
    print(f"  {k}: {hits[0]:.3f} .. {hits[len(hits)//2]:.3f} .. {hits[-1]:.3f}   range={max(hits)-min(hits):+.3f}")
print("all-heads patch gain:")
for r in c['all_heads']:
    print(f"  b={r['bias']:+.0f}: hit={r['hit_rate']:.3f} prem={r['premature_rate']:.3f} "
          f"Vadv={r['v_press_minus_wait']:.3f} qent={r['qent_press']:.3f} Hpi={r['pol_entropy']:.3f}")

# ── EXP5 ──
sec("EXP5  value / entropy")
v = jload("exp5_value.json")
print(f"gamma={v['gamma']}  calibration: slope={v['calibration']['slope']:.3f} "
      f"int={v['calibration']['intercept']:.3f} R2={v['calibration']['r2']:.3f} n={v['calibration']['n']}")
print(f"entropy pre-change={v['entropy_pre_post']['pre']:.3f} post-change={v['entropy_pre_post']['post']:.3f}")
Tg = v['change_time']
for c in ['blue', 'green', 'red']:
    vc = v['v_by_color'][c]
    print(f"  V {c:5s}: cue(t2)={vc[2]:.2f} change(t{Tg})={vc[Tg]:.2f} max={max(vc):.2f}")
print("attn->value sweep:")
for r in v['attn_value_sweep']:
    print(f"  b={r['bias']:+.0f}: V(press)={r['v_press']:.2f} Qadv={r['q_adv']:.2f} qent={r['qent']:.3f} "
          f"Hpi={r['pol_ent']:.3f} P(press)={r['press_prob']:.3f}")
print("\n[digest complete]")
