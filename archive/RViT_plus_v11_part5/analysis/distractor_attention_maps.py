"""Spatial attention maps. We force clean trials (fixed cue side, target location,
and distractor location/timing) and average the model's full 10x10 cross-attention
map at each timestep, for the salience stream (which drives the policy) and the
top-down stream (which drives value). The maps show, condition by condition and
frame by frame, where the agent reads — concentrating on the cued side, anticipating
the target, locking onto the change, and leaving the distractor quadrant cold even as
it changes. We also render the change-aligned and distractor-aligned time-courses of
attention to the cued-primary, cued-secondary and distractor quadrants."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd
from RViT_plus_v11_part5.env import ChangeDetectionEnv, SIDE_QUADRANTS

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
os.makedirs(OUT, exist_ok=True)
device = torch.device("cpu"); torch.manual_seed(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

CT, DT = 17, 13       # fixed target-change time and distractor-onset time
MAG = 55.0            # fixed (clearly visible) orientation step

def forced_envs(n, *, cue, color, target_q, dist_q, rng):
    """Build n distractor-env trials with everything fixed except the random Gabor
    orientations (which average out). dist_q=None → no distractor."""
    envs, obs0 = [], []
    for _ in range(n):
        np.random.seed(int(rng.randint(0, 2**31 - 1)))
        e = ChangeDetectionEnv(distractor_prob=0.5); e.reset()
        e.cue_position = cue; e.cue_color = color; e.proportion = 1.0
        e.change_true = 1; e.change_index = target_q; e.change_time = CT
        e.orientation_change = MAG
        if dist_q is None:
            e.distractor_true = 0
        else:
            e.distractor_true = 1; e.distractor_index = dist_q
            e.distractor_time = DT; e.distractor_change = MAG
        envs.append(e); obs0.append(e._next_observation())
    return envs, obs0

rng = np.random.RandomState(7)
# canonical conditions (target/distractor fixed so maps are interpretable)
CONDS = [
    ("cue-left, red, +distractor",  dict(cue="left",  color="red",  target_q=0, dist_q=2)),
    ("cue-right, red, +distractor", dict(cue="right", color="red",  target_q=3, dist_q=1)),
    ("cue-left, red, no distractor",dict(cue="left",  color="red",  target_q=0, dist_q=None)),
    ("cue-left, BLUE, +distractor", dict(cue="left",  color="blue", target_q=0, dist_q=2)),
]
NPER = 240

maps = {}   # name -> dict(sal (T,N), td (T,N), spec)
for name, spec in CONDS:
    envs, obs0 = forced_envs(NPER, rng=rng, **spec)
    R = dd.record_rollout(model, envs, obs0, device, policy="wait", capture_map=True, run_full=True)
    maps[name] = dict(sal=R["sal_map_h2"].mean(1), td=R["td_map"].mean(1), spec=spec)   # (T,N)
    print(f"  {name}: captured maps (T={R['sal_map_h2'].shape[0]})")

# ---------- helper: draw one 10x10 map with target/distractor boxes ----------
QBOX = {0: (0, 0), 1: (5, 0), 2: (0, 5), 3: (5, 5)}   # (row0,col0) of each quadrant
def draw_map(ax, vec, vmax, target_q=None, dist_q=None):
    g = vec.reshape(10, 10)
    im = ax.imshow(g, cmap="magma", vmin=0, vmax=vmax, interpolation="nearest")
    if target_q is not None:
        r, c = QBOX[target_q]; ax.add_patch(Rectangle((c-.5, r-.5), 5, 5, fill=False, ec="#39ff14", lw=2))
    if dist_q is not None:
        r, c = QBOX[dist_q]; ax.add_patch(Rectangle((c-.5, r-.5), 5, 5, fill=False, ec="#ff2079", lw=2, ls="--"))
    ax.set_xticks([]); ax.set_yticks([])
    return im

TPS = [("post-cue\n(t=3)", 3), ("distractor on\n(t=14)", 14), ("target change\n(t=17)", 17), ("post-change\n(t=19)", 19)]

def map_figure(stream_key, title, fname):
    vmax = max(np.percentile(maps[n][stream_key][[3,14,17,19]], 99) for n in maps)
    fig, ax = plt.subplots(len(CONDS), len(TPS), figsize=(2.1*len(TPS)+0.6, 2.1*len(CONDS)))
    for i, (name, spec) in enumerate(CONDS):
        for j, (tlab, t) in enumerate(TPS):
            im = draw_map(ax[i, j], maps[name][stream_key][t], vmax,
                          target_q=spec["target_q"], dist_q=spec["dist_q"])
            if i == 0: ax[i, j].set_title(tlab, fontsize=9)
        ax[i, 0].set_ylabel(name, fontsize=9)
    fig.suptitle(title, fontweight="bold", fontsize=12, x=0.5, y=1.02)
    fig.subplots_adjust(right=0.9)
    cb = fig.colorbar(im, ax=ax, fraction=0.018, pad=0.02); cb.set_label("attention", fontsize=8)
    handles = [plt.Line2D([], [], color="#39ff14", lw=2, label="target quadrant"),
               plt.Line2D([], [], color="#ff2079", lw=2, ls="--", label="distractor quadrant")]
    fig.legend(handles=handles, fontsize=8, loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.02))
    plt.savefig(f"{OUT}/{fname}.png", dpi=150, bbox_inches="tight")
    plt.savefig(f"{OUT}/{fname}.pdf", bbox_inches="tight"); plt.close()
    print(f"saved {OUT}/{fname}.png")

map_figure("sal", "Salience-stream spatial attention (drives the policy)", "maps_salience")
map_figure("td",  "Top-down-stream spatial attention (drives value)", "maps_topdown")

# ---------- quantified time-courses from the forced maps ----------
def quad_course(name, stream, q):
    qi = dd.quadrant_token_indices()[q]
    return maps[name][stream][:, qi].sum(1)   # (T,)

T = maps[CONDS[0][0]]["sal"].shape[0]; tt = np.arange(T)
fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
# left: salience attention to target / distractor / cued-secondary quads (cue-left +distractor)
nm = "cue-left, red, +distractor"
ax[0].plot(tt, quad_course(nm, "sal", 0), color="#39ff14", lw=2, label="target quad (cued primary)")
ax[0].plot(tt, quad_course(nm, "sal", 1), color="#2c7fb8", lw=1.6, label="cued secondary quad")
ax[0].plot(tt, quad_course(nm, "sal", 2), color="#ff2079", lw=2, ls="--", label="distractor quad")
ax[0].plot(tt, quad_course(nm, "sal", 3), color="#999", lw=1.2, ls=":", label="other uncued quad")
ax[0].axvline(DT, color="#ff2079", ls=":", lw=1); ax[0].axvline(CT, color="#39ff14", ls=":", lw=1)
ax[0].text(DT+.2, ax[0].get_ylim()[1]*0.9, "distractor", fontsize=7, color="#ff2079")
ax[0].text(CT+.2, ax[0].get_ylim()[1]*0.8, "target", fontsize=7, color="#2a2")
ax[0].set_xlabel("frame"); ax[0].set_ylabel("salience attention to quadrant")
ax[0].set_title("A  Salience: locks the target, ignores the distractor", loc="left", fontweight="bold")
ax[0].legend(fontsize=8, frameon=False)
# right: same for top-down stream
ax[1].plot(tt, quad_course(nm, "td", 0), color="#39ff14", lw=2, label="target quad (cued primary)")
ax[1].plot(tt, quad_course(nm, "td", 1), color="#2c7fb8", lw=1.6, label="cued secondary quad")
ax[1].plot(tt, quad_course(nm, "td", 2), color="#ff2079", lw=2, ls="--", label="distractor quad")
ax[1].axvline(DT, color="#ff2079", ls=":", lw=1); ax[1].axvline(CT, color="#39ff14", ls=":", lw=1)
ax[1].set_xlabel("frame"); ax[1].set_ylabel("top-down attention to quadrant")
ax[1].set_title("B  Top-down: cue-anchored prior on the cued side", loc="left", fontweight="bold")
ax[1].legend(fontsize=8, frameon=False)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout(); plt.savefig(f"{OUT}/attn_quad_timecourse.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/attn_quad_timecourse.pdf", bbox_inches="tight"); plt.close()
print(f"saved {OUT}/attn_quad_timecourse.png")

# numeric summary for the writeup
print("\n===== attention to target vs distractor quad (salience, forced cue-left+distractor) =====")
for t in [3, 14, 17, 19]:
    print(f"  t={t:2d}  target={quad_course(nm,'sal',0)[t]:.3f}  distractor={quad_course(nm,'sal',2)[t]:.3f}  "
          f"cued-secondary={quad_course(nm,'sal',1)[t]:.3f}")
print("blue vs red salience attention to target quad (post-cue t=10):",
      f"red={quad_course('cue-left, red, +distractor','sal',0)[10]:.3f}  "
      f"blue={quad_course('cue-left, BLUE, +distractor','sal',0)[10]:.3f}")
np.savez(f"{OUT}/maps_summary.npz",
         **{f"{n.replace(',','').replace(' ','_')}_{s}": maps[n][s] for n in maps for s in ("sal", "td")},
         CT=CT, DT=DT)
