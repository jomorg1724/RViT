"""Psychometric and chronometric functions with 4-parameter logistic fits. On forced
engaged (red) trials we vary the target's orientation-change magnitude and measure the
hit rate and reaction time, separately for VALID (target at the cued primary quadrant)
and INVALID (target at the same-side secondary quadrant) targets, at each displayed
cue reliability. This is the cued-attention behavioural signature: a validity benefit
that should scale with the cue's displayed reliability."""
import os, sys, numpy as np, torch
from scipy.optimize import curve_fit
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd
from RViT_plus_v11_part5.analysis import ddstyle as S
S.apply()
from RViT_plus_v11_part5.env import ChangeDetectionEnv, SIDE_QUADRANTS

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
device = torch.device("cpu"); torch.manual_seed(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

MAGS = np.array([3, 6, 10, 16, 24, 36, 52, 64], dtype=float)
RELIABS = [0.25, 0.5, 0.75, 1.0]
CT, DT = 17, 13
NPER = 150        # trials per (reliability, validity, magnitude)
rng = np.random.RandomState(3)

def forced_block(reliab, valid):
    """One rollout's worth of trials: cue-left red, target at primary (valid) or
    secondary (invalid), displayed reliability `reliab`, distractor present, magnitudes
    swept. Returns envs, obs0, and the per-trial magnitude."""
    prim, sec = SIDE_QUADRANTS["left"]["primary"], SIDE_QUADRANTS["left"]["secondary"]
    tq = prim if valid else sec
    envs, obs0, mag = [], [], []
    for m in MAGS:
        for _ in range(NPER):
            np.random.seed(int(rng.randint(0, 2**31 - 1)))
            e = ChangeDetectionEnv(distractor_prob=0.5); e.reset()
            e.cue_position = "left"; e.cue_color = "red"; e.proportion = reliab
            e.change_true = 1; e.change_index = tq; e.change_time = CT
            e.orientation_change = float(m) * (1 if np.random.rand() < .5 else -1)
            e.distractor_true = 1; e.distractor_index = 2; e.distractor_time = DT
            e.distractor_change = float(np.random.uniform(-64, 64))
            envs.append(e); obs0.append(e._next_observation()); mag.append(m)
    return envs, obs0, np.array(mag)

def logistic4(x, g, l, a, b):
    return g + (1 - g - l) / (1 + np.exp(-(x - a) / b))

def fit(x, y):
    try:
        p, _ = curve_fit(logistic4, x, y, p0=[0.0, 0.05, 15, 6],
                         bounds=([0, 0, 0, 0.5], [0.4, 0.5, 64, 40]), maxfev=20000)
        return p
    except Exception:
        return None

data = {}   # (reliab, valid) -> dict(hit[mag], rt[mag], fit)
for reliab in RELIABS:
    for valid in (True, False):
        envs, obs0, mag = forced_block(reliab, valid)
        R = dd.record_rollout(model, envs, obs0, device, policy="argmax", run_full=True)
        hit = R["hit"]; rt = R["rt"]
        hbym = np.array([hit[mag == m].mean() for m in MAGS])
        rbym = np.array([np.nanmedian(rt[(mag == m) & hit]) for m in MAGS])
        data[(reliab, valid)] = dict(hit=hbym, rt=rbym, fit=fit(MAGS, hbym))
    v = data[(reliab, True)]["fit"]; iv = data[(reliab, False)]["fit"]
    print(f"  reliab {reliab}: valid thresh={v[2]:.1f} slope={v[3]:.1f} | invalid thresh={iv[2]:.1f}  "
          f"| hit@16 valid={logistic4(16,*v):.2f} invalid={logistic4(16,*iv):.2f}  benefit={logistic4(16,*v)-logistic4(16,*iv):+.2f}")

# ================= FIGURE =================
xs = np.linspace(MAGS.min(), MAGS.max(), 100)
colors = {0.25: "#fdae6b", 0.5: "#fd8d3c", 0.75: "#e6550d", 1.0: "#a63603"}
fig, ax = plt.subplots(1, 3, figsize=(16.5, 5.4))
# A: psychometric, valid (solid) vs invalid (dashed), per reliability
for r in RELIABS:
    v, iv = data[(r, True)], data[(r, False)]
    ax[0].plot(MAGS, v["hit"], "o", color=colors[r], ms=4)
    ax[0].plot(MAGS, iv["hit"], "x", color=colors[r], ms=5)
    if v["fit"] is not None: ax[0].plot(xs, logistic4(xs, *v["fit"]), "-", color=colors[r], lw=1.6, label=f"valid r={r:g}")
    if iv["fit"] is not None: ax[0].plot(xs, logistic4(xs, *iv["fit"]), "--", color=colors[r], lw=1.2)
ax[0].set_xlabel("|orientation change| (deg)"); ax[0].set_ylabel("hit rate")
ax[0].set_title("A  Psychometric: valid (—) vs invalid (- -)", loc="left", fontweight="bold")
ax[0].legend(fontsize=7, frameon=False, ncol=2); ax[0].set_ylim(0, 1)
# B: chronometric (valid), per reliability
for r in RELIABS:
    ax[1].plot(MAGS, data[(r, True)]["rt"], "-o", color=colors[r], ms=4, label=f"r={r:g}")
ax[1].set_xlabel("|orientation change| (deg)"); ax[1].set_ylabel("median RT (frames)")
ax[1].set_title("B  Chronometric (valid targets)", loc="left", fontweight="bold"); ax[1].legend(fontsize=7, frameon=False)
# C: cueing signature — valid targets have a lower detection threshold at every reliability
v_thr = [data[(r, True)]["fit"][2] for r in RELIABS]
i_thr = [data[(r, False)]["fit"][2] for r in RELIABS]
thr_mag = 16
ben = [logistic4(thr_mag, *data[(r, True)]["fit"]) - logistic4(thr_mag, *data[(r, False)]["fit"]) for r in RELIABS]
ax[2].plot(RELIABS, v_thr, "-o", color="#2c7fb8", ms=6, label="valid target")
ax[2].plot(RELIABS, i_thr, "-s", color="#d95f0e", ms=6, label="invalid target")
ax[2].set_xlabel("displayed cue reliability"); ax[2].set_ylabel("detection threshold (deg)")
ax[2].set_title("C  Valid targets: lower threshold (more sensitive)", loc="left", fontweight="bold")
ax[2].legend(fontsize=8, frameon=False); ax[2].invert_yaxis()
plt.savefig(f"{OUT}/psychometric.png")
plt.savefig(f"{OUT}/psychometric.pdf"); plt.close()
print(f"saved {OUT}/psychometric.png")
print("\nvalidity benefit at 16deg by reliability:", {r: round(b, 3) for r, b in zip(RELIABS, ben)})
np.savez(f"{OUT}/psychometric_summary.npz", mags=MAGS, reliabs=RELIABS,
         **{f"r{r}_{'v' if vv else 'i'}_hit": data[(r, vv)]["hit"] for r in RELIABS for vv in (True, False)},
         benefit=ben)
