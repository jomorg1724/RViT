"""dd4 — PSYCHOMETRICS. P(declare change) vs change magnitude |Δθ| (degrees) for VALID (change@cued)
vs INVALID (change@uncued) cues at proportion 1.0 — the cueing-benefit curve. Also: FA rate, RT (press
time) by validity, and a proportion sweep of the valid/invalid gap. Reward is location-independent
(declaring a change on any change trial is rewarded), so P(declare) isolates DETECTION, and a
valid>invalid gap means the model is monitoring the cued location (covert cueing benefit)."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd_core as C
SNAP=sys.argv[1]; m,IT,ld=C.load(SNAP); print(f"[dd4] iter={IT} load={ld}")
MAGS=[0,4,8,16,28,44,64]; N=160
def declare_rate(cue, change_idx, mag, prop=1.0, n=N):
    """P(correct detection)=P(press>=change_time 5) on a change trial at this magnitude; + mean RT among hits."""
    press=C.press_times(m, cue, prop, "red", 1, change_idx, mag, B=n)
    hit = press>=5
    return float(hit.mean()), (float(press[hit].mean()) if hit.any() else np.nan)

# valid (change@cued) vs invalid (change@uncued), averaged over cue∈{S1,S4}
valid_p, valid_rt, inval_p, inval_rt = [],[],[],[]
for mg in MAGS:
    vp=[]; vr=[]; ip=[]; ir=[]
    for cue,unc in [(0,3),(3,0)]:
        p,rt=declare_rate(cue,cue,mg); vp.append(p); vr.append(rt)
        p,rt=declare_rate(cue,unc,mg); ip.append(p); ir.append(rt)
    valid_p.append(np.mean(vp)); valid_rt.append(np.nanmean(vr)); inval_p.append(np.mean(ip)); inval_rt.append(np.nanmean(ir))
# FA (no-change) reference: any press on a no-change trial
fa=np.mean([(C.press_times(m,cue,1.0,"red",0,-1,0.0,B=N)>=0).mean() for cue in [0,3]])

fig,ax=plt.subplots(1,2,figsize=(11,3.6))
ax[0].plot(MAGS,valid_p,"o-",c="tab:green",label="VALID (change@cued)")
ax[0].plot(MAGS,inval_p,"s-",c="tab:red",label="INVALID (change@uncued)")
ax[0].axhline(fa,ls="--",c="gray",label=f"FA (no-change)={fa:.2f}")
ax[0].set_xlabel("change magnitude |Δθ| (deg)"); ax[0].set_ylabel("P(declare change)"); ax[0].set_ylim(-.02,1.02)
ax[0].set_title("Psychometric: cueing benefit (prop 1.0)",fontsize=9); ax[0].legend(fontsize=7)
ax[1].plot(MAGS,valid_rt,"o-",c="tab:green",label="VALID"); ax[1].plot(MAGS,inval_rt,"s-",c="tab:red",label="INVALID")
ax[1].axvline(0,alpha=0); ax[1].set_xlabel("change magnitude |Δθ| (deg)"); ax[1].set_ylabel("mean press frame (RT)")
ax[1].set_title("Detection latency by validity",fontsize=9); ax[1].legend(fontsize=7)
fig.suptitle(f"VALID vs INVALID psychometrics over change magnitude — conv crossattn1 iter {IT}",fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dd4_psychometric.png"),dpi=150,bbox_inches="tight"); plt.close(fig)

# proportion sweep of the valid/invalid gap at a fixed mid magnitude (does displayed validity change behavior?)
MID=28; props=[0.25,0.5,0.75,1.0]; gap=[]
for pr in props:
    v=np.mean([declare_rate(cue,cue,MID,prop=pr)[0] for cue in [0,3]])
    iv=np.mean([declare_rate(cue,unc,MID,prop=pr)[0] for cue,unc in [(0,3),(3,0)]])
    gap.append((v,iv))
fig,ax=plt.subplots(figsize=(5,3.4))
ax.plot(props,[g[0] for g in gap],"o-",c="tab:green",label="VALID"); ax.plot(props,[g[1] for g in gap],"s-",c="tab:red",label="INVALID")
ax.set_xlabel("displayed cue proportion (validity)"); ax.set_ylabel(f"P(declare), |Δθ|={MID}°"); ax.set_ylim(-.02,1.02)
ax.set_title(f"Does displayed validity change behaviour? (iter {IT})",fontsize=9); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dd4_validity_behaviour.png"),dpi=150,bbox_inches="tight"); plt.close(fig)

np.savez(os.path.join(C.FIGS,"..","summary_dd4.npz"), mags=MAGS, valid_p=valid_p, inval_p=inval_p,
         valid_rt=valid_rt, inval_rt=inval_rt, fa=fa, props=props, gap=np.array(gap))
print("MAGS      :",MAGS)
print("VALID P   :",[round(x,3) for x in valid_p])
print("INVALID P :",[round(x,3) for x in inval_p])
print("FA(no-chg):",round(float(fa),3))
print("VALID RT  :",[round(x,2) for x in valid_rt])
print("INVALID RT:",[round(x,2) for x in inval_rt])
print("prop sweep |Δθ|=28 (valid,inval):",[(round(v,2),round(i,2)) for v,i in gap])
print("saved dd4_psychometric / dd4_validity_behaviour + summary_dd4.npz")
