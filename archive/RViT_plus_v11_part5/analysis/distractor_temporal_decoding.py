"""Temporal decoding. With the target-change and distractor-onset times fixed (so
timesteps align across trials) but everything else random, we linearly decode each
task variable from the per-quadrant latents at every timestep, separately for the
actor's salience stream and the critic's top-down stream. The curves show when each
variable comes online and — the key result — that the distractor's location and
presence stay weakly decodable from the actor's stream throughout, even as the target
location rises sharply after the change: a dynamic signature of the spatial filter."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd
from RViT_plus_v11_part5.env import ChangeDetectionEnv

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
device = torch.device("cpu"); torch.manual_seed(0); rng = np.random.RandomState(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

CT, DT = 17, 13
def make_envs(n, seed):
    r = np.random.RandomState(seed); envs = []
    for _ in range(n):
        np.random.seed(int(r.randint(0, 2**31 - 1)))
        e = ChangeDetectionEnv(distractor_prob=0.5); e.reset()
        e.change_time = CT; e.distractor_time = DT   # fix timing; everything else random
        envs.append(e)
    return envs, [e._next_observation() for e in envs]

N = 1600
parts_zsal, parts_ztd, meta = [], [], {}
for s in range(0, N, 400):
    envs, obs0 = make_envs(400, seed=100 + s)
    R = dd.record_rollout(model, envs, obs0, device, policy="wait", capture_quadlat=True, run_full=True)
    parts_zsal.append(R["ql_zsal"]); parts_ztd.append(R["ql_ztd"])
    for k in ("change_true", "change_index", "distractor_true", "distractor_index",
              "cue_position", "cue_color", "proportion"):
        meta.setdefault(k, []).append(R[k])
ZSAL = np.concatenate(parts_zsal, 1); ZTD = np.concatenate(parts_ztd, 1)   # (T,N,4,d)
for k in meta: meta[k] = np.concatenate(meta[k])
T = ZSAL.shape[0]
ct = meta["change_true"].astype(bool); dtt = meta["distractor_true"].astype(bool)
labels = {
    "cue colour (value)": (np.array([{"red":0,"green":1,"blue":2}[c] for c in meta["cue_color"].astype(str)]),
                            np.ones(len(ct), bool), 0.333),
    "cue side":           ((meta["cue_position"].astype(str) == "right").astype(int), np.ones(len(ct), bool), 0.5),
    "target location":    (meta["change_index"], ct, 0.25),
    "distractor present": (dtt.astype(int), np.ones(len(ct), bool), 0.5),
    "distractor location":(meta["distractor_index"], dtt, 0.25),
}

def dec_at(Z, t, y, mask):
    X = Z[t][mask].reshape(mask.sum(), -1); yy = y[mask]
    if len(np.unique(yy)) < 2: return np.nan
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1500, C=0.5))
    return cross_val_score(clf, X, yy, cv=StratifiedKFold(3, shuffle=True, random_state=0),
                           scoring="balanced_accuracy").mean()

TS = list(range(1, T, 2))
curves = {"zsal": {}, "ztd": {}}
for vname, (y, mask, chance) in labels.items():
    curves["zsal"][vname] = [dec_at(ZSAL, t, y, mask) for t in TS]
    # decode target & distractor location from the critic stream too, for the dissociation
    if vname in ("target location", "distractor location", "distractor present"):
        curves["ztd"][vname] = [dec_at(ZTD, t, y, mask) for t in TS]
    print(f"  decoded '{vname}' across {len(TS)} timesteps (z_sal)")

# ================= FIGURE =================
fig, ax = plt.subplots(1, 2, figsize=(14, 4.8))
cols = {"cue colour (value)": "#6a51a3", "cue side": "#9e9ac8", "target location": "#238b45",
        "distractor present": "#fb6a4a", "distractor location": "#de2d26"}
for vname, (_, _, chance) in labels.items():
    ax[0].plot(TS, curves["zsal"][vname], "-o", ms=3, color=cols[vname], label=vname)
    ax[0].axhline(chance, color=cols[vname], ls=":", lw=.6, alpha=.5)
ax[0].axvline(DT, color="#de2d26", ls="--", lw=.8); ax[0].axvline(CT, color="#238b45", ls="--", lw=.8)
ax[0].text(DT-2.5, 1.02, "distractor\non", fontsize=7, color="#de2d26")
ax[0].text(CT+.3, 1.02, "target\nchange", fontsize=7, color="#238b45")
ax[0].set_xlabel("frame"); ax[0].set_ylabel("decoding balanced accuracy")
ax[0].set_title("A  Temporal decoding from the actor's salience stream", loc="left", fontweight="bold")
ax[0].legend(fontsize=7.5, frameon=False, loc="center left"); ax[0].set_ylim(0, 1.05)
# B: target vs distractor location, actor (sal) vs critic (td) streams
ax[1].plot(TS, curves["zsal"]["target location"], "-o", ms=3, color="#238b45", label="target loc — actor (z_sal)")
ax[1].plot(TS, curves["ztd"]["target location"], "--o", ms=3, color="#74c476", label="target loc — critic (z_td)")
ax[1].plot(TS, curves["zsal"]["distractor location"], "-s", ms=3, color="#de2d26", label="distractor loc — actor (z_sal)")
ax[1].plot(TS, curves["ztd"]["distractor location"], "--s", ms=3, color="#fc9272", label="distractor loc — critic (z_td)")
ax[1].axhline(0.25, color="k", ls=":", lw=.6); ax[1].axvline(DT, color="#de2d26", ls="--", lw=.8)
ax[1].axvline(CT, color="#238b45", ls="--", lw=.8)
ax[1].set_xlabel("frame"); ax[1].set_ylabel("location decoding accuracy")
ax[1].set_title("B  Distractor stays weak in the actor stream", loc="left", fontweight="bold")
ax[1].legend(fontsize=7.5, frameon=False); ax[1].set_ylim(0, 1.05)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/temporal_decoding.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/temporal_decoding.pdf", bbox_inches="tight"); plt.close()
print(f"saved {OUT}/temporal_decoding.png")
np.savez(f"{OUT}/temporal_decoding_summary.npz", ts=TS,
         **{f"zsal_{v.replace(' ','_')}": np.array(curves['zsal'][v]) for v in curves['zsal']},
         **{f"ztd_{v.replace(' ','_')}": np.array(curves['ztd'][v]) for v in curves['ztd']})
