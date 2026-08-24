"""Attention allocation dynamics on the distractor task. Under a forced-wait policy
(so every trial yields a full, clean sequence), we extract the cross-attention the
agent places on each quadrant and ask: (i) does it concentrate on the CUED side and
suppress the DISTRACTOR side? (ii) what happens to distractor-side attention when a
distractor change onsets — is it captured or rejected? (iii) does the value gate
(blue) show up as disengaged attention?"""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
os.makedirs(OUT, exist_ok=True)
device = torch.device("cpu"); torch.manual_seed(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

N = 1500
R = dd.record_rollout_chunked(model, N, device, chunk=300, seed=11,
                              policy="wait", capture_attn=True, distractor_prob=0.5)
sal = R["sal_quad"]; td = R["td_quad"]          # (T, N, 4) attention mass per quadrant
T = sal.shape[0]
cue = R["cue_position"]; color = R["cue_color"].astype(str)
ctime = R["change_time"]; ct = R["change_true"].astype(bool)
dt_true = R["distractor_true"].astype(bool); dtime = R["distractor_time"]
prim = np.array([dd.SIDE_QUADRANTS[c]["primary"] for c in cue])
seco = np.array([dd.SIDE_QUADRANTS[c]["secondary"] for c in cue])
dquads = np.array([list(dd.SIDE_QUADRANTS[c]["distractor"]) for c in cue])  # (N,2)
engaged = np.isin(color, ["red", "green"])

def per_trial_quad(arr, quad_idx):
    """arr (T,N,4); quad_idx (N,) → (T,N) attention to each trial's chosen quadrant."""
    return np.take_along_axis(arr, quad_idx[None, :, None], axis=2)[:, :, 0]

def side_attn(arr, quads2):
    """sum attention over a trial's 2-quadrant side. quads2 (N,2) → (T,N)."""
    a = np.take_along_axis(arr, quads2.T[0][None, :, None], 2)[:, :, 0]
    b = np.take_along_axis(arr, quads2.T[1][None, :, None], 2)[:, :, 0]
    return a + b

# salience stream (drives the actor) attention to cued vs distractor regions
sal_prim = per_trial_quad(sal, prim)            # (T,N)
sal_seco = per_trial_quad(sal, seco)
sal_cued = sal_prim + sal_seco
sal_dist = side_attn(sal, dquads)
td_prim = per_trial_quad(td, prim)
td_cued = td_prim + per_trial_quad(td, seco)
td_dist = side_attn(td, dquads)

# ---- change-aligned time-course (window around target onset) ----
W, A = 9, 4
def align(course, times, mask):
    """course (T,N); align each trial to its `times`; window [-W,+A]. mean over masked trials."""
    rows = []
    idx = np.where(mask)[0]
    for i in idx:
        c = int(times[i]); lo, hi = c - W, c + A
        seg = np.full(W + A + 1, np.nan)
        for k, t in enumerate(range(lo, hi + 1)):
            if 0 <= t < T:
                seg[k] = course[t, i]
        rows.append(seg)
    return np.nanmean(np.array(rows), axis=0), len(idx)

lags = np.arange(-W, A + 1)
m_eng = engaged & ct
sc_prim, _ = align(sal_prim, ctime, m_eng)
sc_seco, _ = align(sal_seco, ctime, m_eng)
sc_dist, _ = align(sal_dist, ctime, m_eng)

# ---- distractor-onset-aligned (does distractor-side attention spike then suppress?) ----
m_dist = engaged & dt_true
dd_on, nd = align(sal_dist, dtime, m_dist)       # distractor-side attn around distractor onset
dd_off, _ = align(sal_dist, dtime, engaged & ~dt_true)  # same window, no-distractor trials (baseline)

# ---- spatial selectivity index (peri-change window, engaged) ----
peri = slice(W - 4, W + 1)  # the 5 frames up to change
sel_sal = (np.nanmean(sc_prim[peri]) + np.nanmean(sc_seco[peri])) - np.nanmean(sc_dist[peri])
print("\n========== SPATIAL SELECTIVITY (engaged, peri-change) ==========")
print(f"  salience attn  cued-primary={np.nanmean(sc_prim[peri]):.3f}  cued-secondary={np.nanmean(sc_seco[peri]):.3f}  "
      f"distractor-side={np.nanmean(sc_dist[peri]):.3f}")
print(f"  cued-vs-distractor selectivity (salience) = {sel_sal:+.3f}")

# ---- value gate in attention: cued-side attention engaged vs blue (peri-change) ----
print("\n========== VALUE GATE IN ATTENTION (cued-side salience attn, peri-change) ==========")
for label, mask in [("engaged (red/green)", engaged & ct), ("blue", (color == "blue") & ct)]:
    cc, n = align(sal_cued, ctime, mask)
    print(f"  {label:20s}  cued-side attn (peri-change) = {np.nanmean(cc[peri]):.3f}  (n={n})")

# ---- distractor capture metric: peak distractor-side attn rise after its onset ----
base = np.nanmean(dd_off[:W])                     # pre-onset baseline (no-distractor course)
peak_after = np.nanmax(dd_on[W:W+A+1])
print("\n========== DISTRACTOR CAPTURE ==========")
print(f"  distractor-side attn: baseline={base:.3f}  peak after onset={peak_after:.3f}  "
      f"rise={peak_after-base:+.3f}")

# ================= FIGURES =================
fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
# A: change-aligned salience attention
ax[0].plot(lags, sc_prim, "o-", color="#2c7fb8", label="cued quadrant (primary)")
ax[0].plot(lags, sc_seco, "s-", color="#7fcdbb", label="cued side (secondary)")
ax[0].plot(lags, sc_dist, "^--", color="#de2d26", label="distractor side (2 quads)")
ax[0].axvline(0, color="k", ls=":", lw=1); ax[0].text(0.2, ax[0].get_ylim()[1]*0.95, "change", fontsize=8)
ax[0].set_xlabel("frames from target change"); ax[0].set_ylabel("salience attention mass")
ax[0].set_title("A  Spatial allocation (change-aligned)", loc="left", fontweight="bold")
ax[0].legend(fontsize=8, frameon=False)
# B: distractor-onset-aligned distractor-side attention
ax[1].plot(lags, dd_on, "o-", color="#de2d26", label="distractor present")
ax[1].plot(lags, dd_off, "s--", color="#999999", label="no distractor (baseline)")
ax[1].axvline(0, color="k", ls=":", lw=1); ax[1].text(0.2, ax[1].get_ylim()[1]*0.95, "distractor\nonset", fontsize=8)
ax[1].set_xlabel("frames from distractor onset"); ax[1].set_ylabel("distractor-side attention")
ax[1].set_title("B  Distractor not captured", loc="left", fontweight="bold")
ax[1].legend(fontsize=8, frameon=False)
# C: value gate — cued-side attention engaged vs blue
cc_eng, _ = align(sal_cued, ctime, engaged & ct)
cc_blue, _ = align(sal_cued, ctime, (color == "blue") & ct)
ax[2].plot(lags, cc_eng, "o-", color="#2c7fb8", label="engaged (red/green)")
ax[2].plot(lags, cc_blue, "s--", color="#756bb1", label="blue (low value)")
ax[2].axvline(0, color="k", ls=":", lw=1)
ax[2].set_xlabel("frames from target change"); ax[2].set_ylabel("cued-side attention")
ax[2].set_title("C  Value gate in attention", loc="left", fontweight="bold")
ax[2].legend(fontsize=8, frameon=False)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/attention.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/attention.pdf", bbox_inches="tight")
print(f"\nsaved {OUT}/attention.png")
np.savez(f"{OUT}/attention_summary.npz", lags=lags, sc_prim=sc_prim, sc_seco=sc_seco, sc_dist=sc_dist,
         dd_on=dd_on, dd_off=dd_off, cc_eng=cc_eng, cc_blue=cc_blue, sel_sal=sel_sal)
