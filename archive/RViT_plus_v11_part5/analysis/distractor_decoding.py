"""What do the two streams represent? We probe per-quadrant latents two frames after
the target change and linearly decode (cross-validated, vs shuffled labels) the
changed (target) location, the distractor location, distractor presence, cue colour
(value) and cue side — from the actor's salience stream, the critic's top-down
stream, and the two memories. The key contrast: the target location should be
decodable from the actor's stream while the distractor location should not — the
representational signature of spatial filtering."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
device = torch.device("cpu"); torch.manual_seed(0); rng = np.random.RandomState(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

R = dd.record_rollout_chunked(model, 2400, device, chunk=300, seed=41,
                              policy="wait", probe_offset=2, distractor_prob=0.5)
ct = R["change_true"].astype(bool); dt_true = R["distractor_true"].astype(bool)
ctime = R["change_time"]; dtime = R["distractor_time"]
ci = R["change_index"]; di = R["distractor_index"]
color = R["cue_color"].astype(str); cue = R["cue_position"]
streams = {"z_sal (actor)": R["probe_zsal"], "z_td (critic)": R["probe_ztd"],
           "H1 (sensory)": R["probe_h1"], "H2 (deep)": R["probe_h2"]}

def decode(X, y, n_classes):
    """balanced-accuracy 5-fold CV; returns (acc, shuffled_acc)."""
    Xf = X.reshape(len(X), -1)
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.5))
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    acc = cross_val_score(clf, Xf, y, cv=cv, scoring="balanced_accuracy").mean()
    ysh = y.copy(); rng.shuffle(ysh)
    sh = cross_val_score(clf, Xf, ysh, cv=cv, scoring="balanced_accuracy").mean()
    return acc, sh

# decoding targets (mask, label, n_classes, chance)
dist_vis = dt_true & (dtime <= ctime + 2)        # distractor present & visible at probe
tasks = {
    "target location (4-way)":     (ct, ci, 4, 0.25),
    "distractor location (4-way)": (dist_vis, di, 4, 0.25),
    "distractor present (binary)": (ct, dt_true.astype(int) & (dtime <= ctime + 2).astype(int), 2, 0.5),
    "cue colour / value (3-way)":  (np.ones(len(ct), bool), np.array([{"red":0,"green":1,"blue":2}[c] for c in color]), 3, 0.33),
    "cue side (binary)":           (np.ones(len(ct), bool), (cue == "right").astype(int), 2, 0.5),
}

print(f"\n{'task':30s} " + " ".join(f"{s:16s}" for s in streams))
results = {t: {} for t in tasks}
for tname, (mask, lab, nc, chance) in tasks.items():
    row = f"{tname:30s} "
    for sname, arr in streams.items():
        y = lab[mask]
        if len(np.unique(y)) < 2:
            acc, sh = np.nan, np.nan
        else:
            acc, sh = decode(arr[mask], y, nc)
        results[tname][sname] = (acc, sh, chance)
        row += f"{acc:5.2f}({sh:4.2f})    "
    print(row + f"  [chance {chance:.2f}]")

# ================= FIGURE =================
fig, ax = plt.subplots(figsize=(10, 5))
tasknames = list(tasks); snames = list(streams)
x = np.arange(len(tasknames)); w = 0.2
colors = ["#2c7fb8", "#de2d26", "#74a9cf", "#fdae6b"]
for j, s in enumerate(snames):
    vals = [results[t][s][0] for t in tasknames]
    ax.bar(x + (j-1.5)*w, vals, w, label=s, color=colors[j], edgecolor="k", lw=.5)
for i, t in enumerate(tasknames):
    ch = tasks[t][3]
    ax.hlines(ch, i-0.5, i+0.5, color="k", ls="--", lw=.8)
ax.set_xticks(x); ax.set_xticklabels([t.replace(" (", "\n(") for t in tasknames], fontsize=8.5)
ax.set_ylabel("decoding balanced accuracy"); ax.set_ylim(0, 1)
ax.set_title("Linear decoding of task variables from each stream (2 frames after change)",
             loc="left", fontweight="bold", fontsize=11)
ax.legend(fontsize=8, frameon=False, ncol=2)
ax.annotate("target decodes,\ndistractor does not\n(actor stream)", xy=(1.0, 0.32), xytext=(1.6, 0.7),
            fontsize=8, color="#555", arrowprops=dict(arrowstyle="->", color="#555", lw=.8))
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/decoding.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/decoding.pdf", bbox_inches="tight")
print(f"saved {OUT}/decoding.png")
np.savez(f"{OUT}/decoding_summary.npz",
         **{f"{t}|{s}": np.array(results[t][s]) for t in tasks for s in streams})
