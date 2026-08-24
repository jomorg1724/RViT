"""Is the value-modulation of the spatial filter graded? We repeat the matched forced
trial for all three reward levels (red=5, green=3, blue=1) and measure, peri-change,
the salience stream's attention to the target quadrant (filter sharpness) and to the
distractor quadrant (filter leak). If the filter is tuned by stake, sharpness should
fall and leak should rise monotonically as reward drops."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd
from RViT_plus_v11_part5.env import ChangeDetectionEnv

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
device = torch.device("cpu"); torch.manual_seed(0)
model = dd.build_model(dd.load_config(), device)
dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
CT, DT, MAG, N = 17, 13, 55.0, 300
qi = dd.quadrant_token_indices()
rng = np.random.RandomState(9)

def forced(color):
    envs, obs0 = [], []
    for _ in range(N):
        np.random.seed(int(rng.randint(0, 2**31 - 1)))
        e = ChangeDetectionEnv(distractor_prob=0.5); e.reset()
        e.cue_position = "left"; e.cue_color = color; e.proportion = 1.0
        e.change_true = 1; e.change_index = 0; e.change_time = CT; e.orientation_change = MAG
        e.distractor_true = 1; e.distractor_index = 2; e.distractor_time = DT; e.distractor_change = MAG
        envs.append(e); obs0.append(e._next_observation())
    return envs, obs0

COLORS = [("red", 5), ("green", 3), ("blue", 1)]
peri = slice(CT - 3, CT + 2)   # peri-change window
sharp, leak = [], []
for c, v in COLORS:
    envs, obs0 = forced(c)
    R = dd.record_rollout(model, envs, obs0, device, policy="wait", capture_map=True, run_full=True)
    sal = R["sal_map_h2"].mean(1)   # (T,N)
    tgt = sal[:, qi[0]].sum(1); dis = sal[:, qi[2]].sum(1)
    sharp.append(tgt[peri].mean()); leak.append(dis[peri].mean())
    print(f"  {c:5s} (v={v}): target-quad attn={sharp[-1]:.3f}  distractor-quad attn={leak[-1]:.3f}")

vals = [v for _, v in COLORS]
fig, ax = plt.subplots(1, 2, figsize=(10, 4.3))
cc = ["#d62728", "#2ca02c", "#1f77b4"]
ax[0].plot(vals, sharp, "-o", color="#333", ms=4, zorder=1)
ax[0].scatter(vals, sharp, c=cc, s=110, zorder=2, edgecolor="k")
ax[0].set_xlabel("reward at stake"); ax[0].set_ylabel("salience attn to target quad (peri-change)")
ax[0].set_title("A  Filter sharpness grades with value", loc="left", fontweight="bold")
ax[0].set_xticks(vals)
ax[1].plot(vals, leak, "-o", color="#333", ms=4, zorder=1)
ax[1].scatter(vals, leak, c=cc, s=110, zorder=2, edgecolor="k")
ax[1].set_xlabel("reward at stake"); ax[1].set_ylabel("salience attn to distractor quad (peri-change)")
ax[1].set_title("B  Distractor leak grades inversely", loc="left", fontweight="bold")
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/value_graded.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/value_graded.pdf", bbox_inches="tight")
print("saved value_graded.png")
np.savez(f"{OUT}/value_graded_summary.npz", vals=vals, sharp=sharp, leak=leak)
