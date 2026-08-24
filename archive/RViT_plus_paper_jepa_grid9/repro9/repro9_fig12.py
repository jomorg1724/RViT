"""Fig 12 reproduction --- actor-logit geometry. Scatter of the final actor logits at the change frame
(t=5): x = 'Wait' logit, y = 'Declare Change' logit. A: natural mixed trials. B-E: changes constrained
to S1/S2/S3/S4 (all change trials, uniform-random Δ). Left column of each: colored by Δ; right: by 2D
density. Reproduces the competitive (anti-correlated) Wait/Declare axis, graded by Δ, ~invariant to
change location. Usage: repro_fig12.py <snap> <feedback> <label>"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro9_core as C, repro9_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
N=int(sys.argv[4]) if len(sys.argv)>4 else 1500
m,IT=C.load(SNAP,FB); print(f"[fig12 {LAB}] iter={IT} N={N}")
def logits_at_change(vids):
    r=S.rollout(m,vids); return r["logits"][:,5,:]   # (N,2): [wait, declare]
# A natural (mixed), B-E per-location change trials
V,loc,dl=S.gen_trials(0,1.0,N,p_change=0.5,seed=1); LA=logits_at_change(V); DA=dl
sets=[("A natural (mixed)",LA,DA)]
# representative grid9 locations: corners S1(0, cued) / S3(2) / centre S5(4) / opposite corner S9(8)
for k,(loc,nm) in enumerate([(0,"B  $S_1$ (cued corner)"),(2,"C  $S_3$ changes"),(4,"D  $S_5$ (centre)"),(8,"E  $S_9$ (opp. corner)")]):
    mags=np.random.default_rng(20+k).uniform(1,60,N)            # all change trials at this location, uniform Δ
    Vi=C._tens([C.make_video(0,1.0,"red",1,loc,float(mg)) for mg in mags])
    sets.append((nm,logits_at_change(Vi),mags))
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig12_{LAB}.npz"),iter=IT,
         **{f"L{k}":s[1] for k,s in enumerate(sets)},**{f"D{k}":s[2] for k,s in enumerate(sets)})
fig,ax=plt.subplots(5,2,figsize=(9,18))
for k,(nm,L,D) in enumerate(sets):
    sc=ax[k,0].scatter(L[:,0],L[:,1],c=D,cmap="coolwarm",s=6,alpha=.6)
    plt.colorbar(sc,ax=ax[k,0],label="Δ (°)",fraction=.046)
    xy=np.vstack([L[:,0],L[:,1]])
    try: dens=gaussian_kde(xy)(xy)
    except Exception: dens=np.ones(L.shape[0])
    sc2=ax[k,1].scatter(L[:,0],L[:,1],c=dens,cmap="viridis",s=6,alpha=.6)
    plt.colorbar(sc2,ax=ax[k,1],label="density",fraction=.046)
    ax[k,0].set_ylabel("Declare-Change logit"); ax[k,0].set_title(nm+"  (by Δ)",fontsize=9)
    ax[k,1].set_title(nm+"  (by density)",fontsize=9)
    for a in ax[k]: a.set_xlabel("Wait logit")
fig.suptitle(f"Fig 12 --- actor logit geometry at change frame ({LAB}, iter {IT}; n={N})",fontsize=12,y=1.0)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,f"fig12_{LAB}.png"),dpi=140,bbox_inches="tight"); plt.close(fig)
print(f"saved fig12_{LAB}")
