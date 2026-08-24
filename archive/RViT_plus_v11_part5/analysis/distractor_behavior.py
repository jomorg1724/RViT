"""Behavioral characterization of the cross-talk agent on the distractor task:
overall signal-detection performance, the reliability-scaled cueing effect, the
psychometric/chronometric functions, and — the central question — how well the
agent SUPPRESSES responses to uncued distractor changes (and where it fails)."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
os.makedirs(OUT, exist_ok=True)
device = torch.device("cpu")
torch.manual_seed(0)

model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

N = 3000
R = dd.record_rollout_chunked(model, N, device, chunk=300, seed=7, policy="argmax", distractor_prob=0.5)

ct = R["change_true"].astype(bool); dt_true = R["distractor_true"].astype(bool)
pressed = R["pressed"]; prem = R["premature"]; hit = R["hit"]
ci = R["change_index"]; prop = R["proportion"]; cue = R["cue_position"]
ctime = R["change_time"]; dtime = R["distractor_time"]; pidx = R["press_index"]
color = R["cue_color"]; omag = np.abs(R["orientation_change"])

# primary (cued) quadrant per trial
primary = np.array([dd.SIDE_QUADRANTS[c]["primary"] for c in cue])
valid = ct & (ci == primary)            # target at the cued quadrant
invalid = ct & (ci != primary) & (ci >= 0)

# signal-detection outcomes
miss = ct & ~pressed
early_fa = prem.copy()                                   # pressed before target change
nochange_fa = (~ct) & pressed                            # pressed on a no-target trial
cr = (~ct) & ~pressed
acc = (hit | cr).mean()
hit_rate = hit[ct].mean()
fa_change = early_fa[ct].mean()                          # early FAs on target trials
fa_nochange = nochange_fa[~ct].mean()
rt = R["rt"][hit]

print("\n========== OVERALL ==========")
print(f"trials={N}  accuracy={acc:.3f}  hit-rate(target)={hit_rate:.3f}  "
      f"miss={miss[ct].mean():.3f}  early-FA(target trials)={fa_change:.3f}  "
      f"FA(no-target)={fa_nochange:.3f}  mean RT={np.nanmean(rt):.2f} frames")

# ---- distractor suppression: does the distractor drive false alarms? ----
# A distractor onsetting BEFORE the target is the temptation to suppress.
dist_before = dt_true & (dtime < ctime)
dist_after  = dt_true & (dtime >= ctime)
no_dist     = ~dt_true
print("\n========== DISTRACTOR SUPPRESSION (early-FA rate on TARGET trials) ==========")
for name, mask in [("no distractor", no_dist & ct), ("distractor AFTER target", dist_after & ct),
                   ("distractor BEFORE target", dist_before & ct)]:
    m = mask
    print(f"  {name:26s}  n={m.sum():5d}  early-FA={early_fa[m].mean():.3f}  hit={hit[m].mean():.3f}")
# of all early FAs on target trials, how many followed a distractor onset?
efa = early_fa & ct
followed_dist = efa & dt_true & (dtime <= pidx)
print(f"  -> of {efa.sum()} early-FAs on target trials, {followed_dist.sum()} "
      f"({100*followed_dist.mean()/max(efa.mean(),1e-9):.0f}%) occurred at/after a distractor onset")

# ---- cueing effect: hit rate primary vs secondary by reliability ----
print("\n========== CUEING EFFECT (hit rate, cued task within side) ==========")
print(f"  {'reliab':>7} {'hit|primary':>12} {'hit|secondary':>14} {'benefit':>9} {'n_p/n_s':>10}")
rel_primary, rel_secondary = [], []
for p in dd.PROPORTIONS:
    mp = ct & (prop == p) & (ci == primary)
    ms = ct & (prop == p) & (ci != primary) & (ci >= 0)
    hp = hit[mp].mean() if mp.sum() else np.nan
    hs = hit[ms].mean() if ms.sum() else np.nan
    rel_primary.append(hp); rel_secondary.append(hs)
    print(f"  {p:>7} {hp:>12.3f} {hs:>14.3f} {hp-hs:>+9.3f} {mp.sum():>5}/{ms.sum():<5}")

# ---- VALUE-DIRECTED DECOMPOSITION: how each cue color is handled ----
print("\n========== VALUE-DIRECTED STRATEGY (target-trial outcome by color) ==========")
print(f"  {'color':6s} {'reward':>6} {'hit':>6} {'early-FA':>9} {'miss':>6} {'med early-press t':>17}")
engaged = np.zeros(len(ct), dtype=bool)
for c in ["red", "green", "blue"]:
    m = ct & (color == c)
    h, e, ms = hit[m].mean(), early_fa[m].mean(), miss[m].mean()
    ept = pidx[m & early_fa]
    print(f"  {c:6s} {dd.COLOR_VALUE[c]:>6} {h:>6.3f} {e:>9.3f} {ms:>6.3f} {np.median(ept) if len(ept) else float('nan'):>17.1f}")
    if c in ("red", "green"):
        engaged |= (color == c)
# early-press timing: are they before any possible distractor (t<11)?
all_ep = pidx[early_fa & ct]
print(f"  early-press times: median={np.median(all_ep):.1f}, "
      f"{100*(all_ep < 11).mean():.0f}% before earliest distractor onset (t<11)")

# ---- cueing effect on ENGAGED (red/green) trials only — removes blue abandonment ----
print("\n========== CUEING EFFECT on ENGAGED (red+green) trials ==========")
print(f"  {'reliab':>7} {'hit|primary':>12} {'hit|secondary':>14} {'benefit':>9} {'n_p/n_s':>10}")
eng_primary, eng_secondary = [], []
for p in dd.PROPORTIONS:
    mp = ct & engaged & (prop == p) & (ci == primary)
    ms = ct & engaged & (prop == p) & (ci != primary) & (ci >= 0)
    hp = hit[mp].mean() if mp.sum() else np.nan
    hs = hit[ms].mean() if ms.sum() else np.nan
    eng_primary.append(hp); eng_secondary.append(hs)
    print(f"  {p:>7} {hp:>12.3f} {hs:>14.3f} {hp-hs:>+9.3f} {mp.sum():>5}/{ms.sum():<5}")

# ---- distractor suppression on ENGAGED trials (the meaningful test) ----
print("\n========== DISTRACTOR SUPPRESSION on ENGAGED (red+green) target trials ==========")
for name, mask in [("no distractor", no_dist & ct & engaged),
                   ("distractor BEFORE target", dist_before & ct & engaged)]:
    print(f"  {name:26s}  n={mask.sum():5d}  early-FA={early_fa[mask].mean():.3f}  hit={hit[mask].mean():.3f}")

# ---- psychometric: hit vs |change magnitude| ; chronometric ; value by color ----
mags = omag[ct & engaged]
edges = np.quantile(mags[mags > 0], np.linspace(0, 1, 7))
bx, by = [], []
for i in range(len(edges)-1):
    m = ct & engaged & (omag >= edges[i]) & (omag < edges[i+1])
    if m.sum() > 10:
        bx.append(0.5*(edges[i]+edges[i+1])); by.append(hit[m].mean())
print("\n========== VALUE STRUCTURE (by cue color / reward) ==========")
for c in ["red", "green", "blue"]:
    m = ct & (color == c)
    print(f"  {c:5s} (reward {dd.COLOR_VALUE[c]})  hit={hit[m].mean():.3f}  RT={np.nanmean(R['rt'][hit & (color==c)]):.2f}  n={m.sum()}")

# cache per-trial arrays so figures can be re-made without re-rolling
np.savez(f"{OUT}/behavior_trials.npz",
         ct=ct, engaged=engaged, color=color.astype(str), hit=hit, early_fa=early_fa,
         miss=miss, pidx=pidx, prop=prop, ci=ci, primary=primary, dt_true=dt_true,
         dtime=dtime, ctime=ctime, omag=omag, rt=R["rt"])

# ================= FIGURES =================
fig, ax = plt.subplots(2, 2, figsize=(11, 8))

# A: VALUE GATE — outcome by cue color (the headline strategy)
cols3 = ["red", "green", "blue"]; xc = np.arange(3); w = 0.27
H = [hit[ct & (color == c)].mean() for c in cols3]
E = [early_fa[ct & (color == c)].mean() for c in cols3]
Mi = [miss[ct & (color == c)].mean() for c in cols3]
ax[0,0].bar(xc - w, H, w, color="#2c7fb8", edgecolor="k", lw=.6, label="hit")
ax[0,0].bar(xc,     E, w, color="#de2d26", edgecolor="k", lw=.6, label="early-press / bail")
ax[0,0].bar(xc + w, Mi, w, color="#bdbdbd", edgecolor="k", lw=.6, label="miss")
ax[0,0].set_xticks(xc); ax[0,0].set_xticklabels([f"{c}\n(reward {dd.COLOR_VALUE[c]})" for c in cols3], fontsize=8.5)
ax[0,0].set_ylabel("proportion of target trials"); ax[0,0].set_ylim(0, 1.05)
ax[0,0].set_title("A  Value gate: engage high-reward, bail on low-reward", loc="left", fontweight="bold", fontsize=10.5)
ax[0,0].legend(fontsize=8, frameon=False, ncol=3, loc="upper center")

# B: distractor suppression on ENGAGED trials (the real test)
labels = ["no\ndistractor", "distractor\nBEFORE target"]
efa_eng = [early_fa[no_dist & ct & engaged].mean(), early_fa[dist_before & ct & engaged].mean()]
hit_eng = [hit[no_dist & ct & engaged].mean(), hit[dist_before & ct & engaged].mean()]
xb = np.arange(2); w2 = 0.38
ax[0,1].bar(xb - w2/2, hit_eng, w2, color="#2c7fb8", edgecolor="k", lw=.6, label="hit rate")
ax[0,1].bar(xb + w2/2, efa_eng, w2, color="#de2d26", edgecolor="k", lw=.6, label="false-alarm rate")
ax[0,1].set_xticks(xb); ax[0,1].set_xticklabels(labels, fontsize=9)
ax[0,1].set_ylabel("rate (engaged trials)"); ax[0,1].set_ylim(0, 1)
ax[0,1].set_title("B  Distractor is suppressed (no FA increase)", loc="left", fontweight="bold", fontsize=10.5)
ax[0,1].legend(fontsize=8, frameon=False)
ax[0,1].annotate("≈0 false alarms\neither way", xy=(1, 0.02), xytext=(0.5, 0.45), ha="center", fontsize=8.5,
                 color="#555", arrowprops=dict(arrowstyle="->", color="#555", lw=.8))

# C: cueing benefit (engaged) + psychometric inset-style on same axis (two y not needed)
xr = np.arange(4)
ax[1,0].plot(xr, eng_primary, "o-", color="#2c7fb8", label="cued quadrant (primary)")
ax[1,0].plot(xr, eng_secondary, "s--", color="#d95f0e", label="same-side (secondary)")
ax[1,0].set_xticks(xr); ax[1,0].set_xticklabels([f"{p:g}" for p in dd.PROPORTIONS])
ax[1,0].set_xlabel("cue reliability"); ax[1,0].set_ylabel("hit rate (engaged)")
ax[1,0].set_title("C  Cued-quadrant benefit", loc="left", fontweight="bold", fontsize=10.5)
ax[1,0].legend(fontsize=8, frameon=False); ax[1,0].set_ylim(0.5, 1)

# D: chronometric (RT histogram, engaged hits)
rte = R["rt"][hit & engaged]
ax[1,1].hist(rte[~np.isnan(rte)], bins=np.arange(-0.5, 10.5, 1), color="#41b6c4", edgecolor="k", lw=.5)
ax[1,1].axvline(np.nanmean(rte), color="k", ls="--", lw=1)
ax[1,1].set_xlabel("reaction time (frames after change)"); ax[1,1].set_ylabel("count of hits")
ax[1,1].set_title(f"D  Chronometric (mean {np.nanmean(rte):.2f} frames)", loc="left", fontweight="bold", fontsize=10.5)

for a in ax.ravel():
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(f"{OUT}/behavior.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/behavior.pdf", bbox_inches="tight")
print(f"\nsaved {OUT}/behavior.png")

np.savez(f"{OUT}/behavior_summary.npz",
         acc=acc, hit_rate=hit_rate, fa_change=fa_change, fa_nochange=fa_nochange,
         rt_mean=np.nanmean(rt), eng_primary=eng_primary, eng_secondary=eng_secondary,
         H=H, E=E, Mi=Mi, efa_eng=efa_eng, hit_eng=hit_eng, psy_x=bx, psy_y=by)
