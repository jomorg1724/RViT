"""Fig 13 reproduction --- actor logits (Wait vs Declare-Change, at t=5) for S1 changes under attention
modulation on S1: A natural, B α1=1 (enhance), C α1=0 (suppress). Colored by Δ + density. Enhancing
attention pushes mass toward Declare; suppressing withdraws it. Usage: repro_fig13.py <snap> <fb> <lab>"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro9_core as C, repro9_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
N=int(sys.argv[4]) if len(sys.argv)>4 else 1500
m,IT=C.load(SNAP,FB); K=S.n_keys(m); print(f"[fig13 {LAB}] iter={IT} K={K} N={N}")
mags=np.random.default_rng(3).uniform(1,60,N)
V=C._tens([C.make_video(0,1.0,"red",1,0,float(mg)) for mg in mags])   # S1 changes
def logch(clamp): return S.rollout(m,V,clamp=clamp,clamp_from=5)["logits"][:,5,:]
conds=[("A natural",None),("B  $\\alpha_1{=}1$ (enhance)",C.clamp_on(K,0)),("C  $\\alpha_1{=}0$ (suppress)",C.clamp_off(K,0))]
L={nm:logch(cl) for nm,cl in conds}
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig13_{LAB}.npz"),iter=IT,mags=mags,
         **{f"L{i}":L[nm] for i,(nm,_) in enumerate(conds)})
fig,ax=plt.subplots(3,2,figsize=(9,11))
for r,(nm,_) in enumerate(conds):
    Lc=L[nm]; sc=ax[r,0].scatter(Lc[:,0],Lc[:,1],c=mags,cmap="coolwarm",s=6,alpha=.6)
    plt.colorbar(sc,ax=ax[r,0],label="Δ (°)",fraction=.046)
    xy=np.vstack([Lc[:,0],Lc[:,1]])
    try: dens=gaussian_kde(xy)(xy)
    except Exception: dens=np.ones(Lc.shape[0])
    sc2=ax[r,1].scatter(Lc[:,0],Lc[:,1],c=dens,cmap="viridis",s=6,alpha=.6); plt.colorbar(sc2,ax=ax[r,1],label="density",fraction=.046)
    ax[r,0].set_ylabel("Declare logit"); ax[r,0].set_title(nm+" (by Δ)",fontsize=9); ax[r,1].set_title(nm+" (density)",fontsize=9)
    for a in ax[r]: a.set_xlabel("Wait logit")
fig.suptitle(f"Fig 13 --- actor logits under S1 attention modulation ({LAB}, iter {IT}; n={N})",fontsize=11)
fig.tight_layout(rect=[0,0,1,.98]); fig.savefig(os.path.join(C.FIGS,f"fig13_{LAB}.png"),dpi=140,bbox_inches="tight"); plt.close(fig)
print(f"saved fig13_{LAB}")
