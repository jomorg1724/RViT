"""Causal perturbation battery. On clean forced trials (cue-left, engaged/red, target
at the cued primary quad 0, distractor at quad 2) we inject an additive bias into the
pre-softmax attention logits of a chosen stream/region and sweep it over b in [-6,+6],
reading BOTH the decision (hit and false-alarm rate, greedy policy) and the critic
(state value and outcome uncertainty, at the pre-change frame where all trials are
live). This isolates which levers move the choice and which move the valuation, and
quantifies the protective spatial filter (distractor-side boost) and the agent's
reliance on the cued quad (cued-primary suppression), including the d' shift."""
import os, sys, numpy as np, torch
from scipy.stats import norm
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd
from RViT_plus_v11_part5.env import ChangeDetectionEnv

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
device = torch.device("cpu"); torch.manual_seed(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

CT, DT, MAG, N = 17, 13, 55.0, 700
Ntok, Hh = model.n_tokens, model.encoder.n_heads
qi = dd.quadrant_token_indices()
PRECHANGE = 11   # pre-change frame: all trials still live under greedy

rng = np.random.RandomState(5)
seeds = rng.randint(0, 2**31 - 1, size=N)
def forced(seeds):
    envs, obs0 = [], []
    for s in seeds:
        np.random.seed(int(s)); e = ChangeDetectionEnv(distractor_prob=0.5); e.reset()
        e.cue_position = "left"; e.cue_color = "red"; e.proportion = 1.0
        e.change_true = 1; e.change_index = 0; e.change_time = CT; e.orientation_change = MAG
        e.distractor_true = 1; e.distractor_index = 2; e.distractor_time = DT; e.distractor_change = MAG
        envs.append(e); obs0.append(e._next_observation())
    return envs, obs0

def bias(stream, block, quads, value):
    if stream == "sal":
        b = torch.zeros(Hh, 2 * Ntok, device=device); off = 0 if block == "H1" else Ntok
        for q in quads: b[:, off + qi[q]] = value
        return {"sal": b, "td": None}
    b = torch.zeros(Hh, Ntok, device=device)
    for q in quads: b[:, qi[q]] = value
    return {"sal": None, "td": b}

LEVERS = [
    ("salience @ cued-primary", "sal", "H2", [0]),
    ("salience @ distractor",   "sal", "H2", [2, 3]),
    ("salience @ cued-secondary","sal","H2", [1]),
    ("top-down @ cued-primary", "td",  None, [0]),
    ("top-down @ distractor",   "td",  None, [2, 3]),
]
BIASES = [-6, -3, 0, 3, 6]
res = {name: dict(hit=[], fa=[], val=[], unc=[]) for name, *_ in LEVERS}

for name, stream, block, quads in LEVERS:
    for b in BIASES:
        envs, obs0 = forced(seeds)
        R = dd.record_rollout(model, envs, obs0, device, policy="argmax",
                              attn_bias=bias(stream, block, quads, float(b)),
                              capture_value=True, run_full=True)
        res[name]["hit"].append(R["hit"].mean())
        res[name]["fa"].append(R["premature"].mean())
        res[name]["val"].append(R["v_scalar"][PRECHANGE].mean())
        res[name]["unc"].append(R["qstd_press"][PRECHANGE].mean())
    r = res[name]
    print(f"  {name:26s} hit {r['hit'][0]:.2f}->{r['hit'][-1]:.2f}  FA {r['fa'][0]:.2f}->{r['fa'][-1]:.2f}  "
          f"val {r['val'][0]:.2f}->{r['val'][-1]:.2f}  unc {r['unc'][0]:.2f}->{r['unc'][-1]:.2f}")

# d' shift under the distractor boost
print("\n===== d' under distractor-side salience boost =====")
dl = res["salience @ distractor"]
for i, b in enumerate(BIASES):
    h = np.clip(dl["hit"][i], 1e-3, 1-1e-3); f = np.clip(dl["fa"][i], 1e-3, 1-1e-3)
    print(f"  bias {b:+d}: hit={dl['hit'][i]:.3f} FA={dl['fa'][i]:.3f}  d'={norm.ppf(h)-norm.ppf(f):.2f}")

# ================= FIGURE =================
base = {n: dict(hit=np.array(res[n]["hit"]), fa=np.array(res[n]["fa"]),
                val=np.array(res[n]["val"]), unc=np.array(res[n]["unc"])) for n in res}
i0 = BIASES.index(0)
cmap = {"salience @ cued-primary": "#2c7fb8", "salience @ distractor": "#de2d26",
        "salience @ cued-secondary": "#74a9cf", "top-down @ cued-primary": "#238b45",
        "top-down @ distractor": "#fb6a4a"}
sty = {"salience @ cued-primary": "-o", "salience @ distractor": "-s",
       "salience @ cued-secondary": "-^", "top-down @ cued-primary": "--o", "top-down @ distractor": "--s"}
fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.6))
for n in res:
    ax[0].plot(BIASES, base[n]["hit"] - base[n]["hit"][i0], sty[n], color=cmap[n], label=n, ms=5)
ax[0].axhline(0, color="k", lw=.6); ax[0].set_xlabel("injected attention bias (logits)")
ax[0].set_ylabel("Δ hit rate (decision)")
ax[0].set_title("A  Decision lever", loc="left", fontweight="bold"); ax[0].legend(fontsize=7.5, frameon=False)
for n in res:
    ax[1].plot(BIASES, base[n]["unc"] - base[n]["unc"][i0], sty[n], color=cmap[n], ms=5)
ax[1].axhline(0, color="k", lw=.6); ax[1].set_xlabel("injected attention bias (logits)")
ax[1].set_ylabel("Δ outcome uncertainty (value)")
ax[1].set_title("B  Value/uncertainty lever", loc="left", fontweight="bold")
# C: distractor induction (FA) with d'
ax[2].plot(BIASES, base["salience @ distractor"]["fa"], "-s", color="#de2d26", label="false-alarm rate", ms=5)
ax[2].plot(BIASES, base["salience @ distractor"]["hit"], "-o", color="#2c7fb8", label="hit rate", ms=5)
ax[2].set_xlabel("distractor-side salience bias"); ax[2].set_ylabel("rate (engaged trials)")
ax[2].set_title("C  Forcing distractor attention", loc="left", fontweight="bold")
ax[2].legend(fontsize=8, frameon=False); ax[2].set_ylim(0, 1)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/causal_battery.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/causal_battery.pdf", bbox_inches="tight"); plt.close()
print(f"saved {OUT}/causal_battery.png")
np.savez(f"{OUT}/causal_battery_summary.npz", biases=BIASES,
         **{f"{n.replace(' ','_').replace('@','at')}_{k}": np.array(res[n][k]) for n in res for k in res[n]})
