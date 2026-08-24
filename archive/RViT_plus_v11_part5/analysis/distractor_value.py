"""The critic and signal-detection view. Does the value function explain the value
gate — i.e. does the critic judge that pressing on a low-value (blue) trial is not
worth it, driving the policy to bail? We track state value and the press-vs-wait
advantage by cue colour, the critic's calibration and uncertainty, and the agent's
signal-detection sensitivity (d') on engaged trials."""
import os, sys, numpy as np, torch
from math import erf, sqrt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
device = torch.device("cpu"); torch.manual_seed(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

def Phi_inv(p):  # probit
    p = np.clip(p, 1e-3, 1 - 1e-3)
    from scipy.stats import norm
    return norm.ppf(p)

# ---- (1) value & press-advantage by colour (forced-wait, full sequences) ----
Rw = dd.record_rollout_chunked(model, 1500, device, chunk=300, seed=21,
                               policy="wait", capture_value=True, distractor_prob=0.5)
qP = Rw["q_press"]; qW = Rw["q_wait"]; V = Rw["v_scalar"]; qstd = Rw["qstd_press"]  # (T,N)
T = qP.shape[0]
color = Rw["cue_color"].astype(str); ctime = Rw["change_time"]; ct = Rw["change_true"].astype(bool)
omag = np.abs(Rw["orientation_change"])

W, A = 9, 5
lags = np.arange(-W, A + 1)
def align(course, mask):
    rows = []
    for i in np.where(mask)[0]:
        c = int(ctime[i]); seg = np.full(W + A + 1, np.nan)
        for k, t in enumerate(range(c - W, c + A + 1)):
            if 0 <= t < T:
                seg[k] = course[t, i]
        rows.append(seg)
    return np.nanmean(rows, axis=0)

print("\n========== VALUE BY COLOUR (forced-wait, at change) ==========")
val_c, adv_c = {}, {}
for c in ["red", "green", "blue"]:
    m = ct & (color == c)
    val_c[c] = align(V, m); adv_c[c] = align(qP - qW, m)
    at0 = W  # index of lag 0 (change)
    print(f"  {c:5s} (reward {dd.COLOR_VALUE[c]})  V(change)={val_c[c][at0]:.3f}  "
          f"press-adv(change)={adv_c[c][at0]:+.3f}  press-adv(+3)={adv_c[c][min(at0+3,len(lags)-1)]:+.3f}")
print("  -> press-advantage turns POSITIVE (worth pressing) for which colours?")

# ---- (2) uncertainty vs change magnitude (just after change) ----
print("\n========== OUTCOME UNCERTAINTY vs EVIDENCE ==========")
mag_bins = [(0, 8), (8, 20), (20, 40), (40, 70)]
unc = []
for lo, hi in mag_bins:
    m = ct & (omag >= lo) & (omag < hi)
    # qstd at change+1 averaged
    vals = []
    for i in np.where(m)[0]:
        t = int(ctime[i]) + 1
        if t < T:
            vals.append(qstd[t, i])
    unc.append(np.mean(vals) if vals else np.nan)
    print(f"  |Δθ|∈[{lo},{hi})  qstd(change+1)={unc[-1]:.3f}  n={m.sum()}")

# ---- (3) SDT d' on engaged trials (from behavior cache) ----
print("\n========== SIGNAL-DETECTION (engaged trials) ==========")
bt = np.load(f"{OUT}/behavior_trials.npz", allow_pickle=True)
bcol = bt["color"].astype(str); bct = bt["ct"].astype(bool); bhit = bt["hit"]; bfa = bt["early_fa"]
dprime = {}
for c in ["red", "green"]:
    m = bct & (bcol == c)
    h = bhit[m].mean(); f = bfa[m].mean()
    dp = Phi_inv(h) - Phi_inv(f); crit = -0.5 * (Phi_inv(h) + Phi_inv(f))
    dprime[c] = dp
    print(f"  {c:5s}: hit={h:.3f} FA={f:.3f}  d'={dp:.2f}  criterion={crit:+.2f}")
mblue = bct & (bcol == "blue")
print(f"  blue : hit={bhit[mblue].mean():.3f} (bails: presses at t≈2 on every trial) — value gate, not a criterion")

# ---- (4) calibration: predicted V vs realised return (greedy) ----
print("\n========== CRITIC CALIBRATION (greedy) ==========")
Rg = dd.record_rollout_chunked(model, 1200, device, chunk=300, seed=31,
                               policy="argmax", capture_value=True, distractor_prob=0.5)
Vg = Rg["v_scalar"]; rew = Rg["reward"]; pidx = Rg["press_index"]; Tg = Vg.shape[0]
gamma = 0.99
pv, rv = [], []
for i in range(len(rew)):
    end = int(pidx[i]) if pidx[i] >= 0 else Tg - 1
    for t in range(0, end + 1):
        pv.append(Vg[t, i]); rv.append((gamma ** (end - t)) * rew[i])
pv = np.array(pv); rv = np.array(rv)
slope = np.polyfit(pv, rv, 1)[0]
ss = 1 - np.sum((rv - np.poly1d(np.polyfit(pv, rv, 1))(pv)) ** 2) / np.sum((rv - rv.mean()) ** 2)
print(f"  predicted V vs realised return: slope={slope:.2f}  R²={ss:.2f}  (n={len(pv)} states)")

# ================= FIGURE =================
fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
cmap = {"red": "#d62728", "green": "#2ca02c", "blue": "#1f77b4"}
for c in ["red", "green", "blue"]:
    ax[0].plot(lags, val_c[c], "o-", color=cmap[c], label=f"{c} (v={dd.COLOR_VALUE[c]})")
ax[0].axvline(0, color="k", ls=":", lw=1); ax[0].set_xlabel("frames from change")
ax[0].set_ylabel("state value"); ax[0].set_title("A  Value preserves reward order", loc="left", fontweight="bold")
ax[0].legend(fontsize=8, frameon=False)
for c in ["red", "green", "blue"]:
    ax[1].plot(lags, adv_c[c], "o-", color=cmap[c], label=c)
ax[1].axhline(0, color="k", ls="--", lw=.8); ax[1].axvline(0, color="k", ls=":", lw=1)
ax[1].set_xlabel("frames from change"); ax[1].set_ylabel("press − wait value advantage")
ax[1].set_title("B  Pressing never worth it for blue → bail", loc="left", fontweight="bold")
ax[1].legend(fontsize=8, frameon=False)
ax[2].scatter(pv, rv, s=3, alpha=0.15, color="#555")
lim = [min(pv.min(), rv.min()), max(pv.max(), rv.max())]
ax[2].plot(lim, lim, "k--", lw=.8, label="identity")
ax[2].plot(np.sort(pv), np.poly1d(np.polyfit(pv, rv, 1))(np.sort(pv)), color="#d62728", lw=1.5,
           label=f"slope {slope:.2f}, R²={ss:.2f}")
ax[2].set_xlabel("predicted value"); ax[2].set_ylabel("realised return")
ax[2].set_title("C  Critic calibration", loc="left", fontweight="bold"); ax[2].legend(fontsize=8, frameon=False)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/value.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/value.pdf", bbox_inches="tight")
print(f"saved {OUT}/value.png")
np.savez(f"{OUT}/value_summary.npz", lags=lags, **{f"val_{c}": val_c[c] for c in val_c},
         **{f"adv_{c}": adv_c[c] for c in adv_c}, unc=unc, slope=slope, r2=ss, dprime=list(dprime.values()))
