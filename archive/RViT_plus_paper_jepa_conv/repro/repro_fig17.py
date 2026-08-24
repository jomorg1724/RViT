"""Fig 17 analog --- supervised-vs-RL comparison. The original contrasts three training signals
(Supervised-Actions, Supervised-Beliefs, RL) across four behavioural rows. Our variants are RL-only, so
we faithfully reproduce the RL column and mark the two supervised columns as out-of-scope architectural
baselines (not trained for this variant). Rows: (1) response vs Δ, cued, 4 validities; (2) cued vs
uncued at 25%; (3) cued vs uncued at 100%; (4) attention on S1 at change vs Δ (cued vs uncued change).
Usage: repro_fig17.py <snap> <feedback> <label>"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro_core as C, repro_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
N=250; m,IT=C.load(SNAP,FB); K=S.n_keys(m); print(f"[fig17 {LAB}] iter={IT}")
DE=[0,3,6,9,12,15,18,22,26,30]; DEf=np.linspace(0,30,120); UNC={0:3,3:0}; VAL=[0.25,0.5,0.75,1.0]
def cued(prop): return np.array([np.mean([C.behavior(m,c,prop,c,float(d),B=N)[0] for c in (0,3)]) for d in DE])
def side(prop,s): return np.array([np.mean([C.behavior(m,c,prop,c if s=="cued" else UNC[c],float(d),B=N)[0] for c in (0,3)]) for d in DE])
A={p:cued(p) for p in VAL}; c25,u25=side(0.25,"cued"),side(0.25,"uncued"); c100,u100=side(1.0,"cued"),side(1.0,"uncued")
def a1_vs_delta(chg):
    out=[]
    for d in DE:
        a=C.attn_maps(m,0,1.0,"red",1 if d>0 else 0,chg,float(max(d,1)),B=64); v=a[5].mean(0)
        out.append(float(np.mean([v[k] for k in C._loc_keys(K,0)])))
    return np.array(out)
a1c=a1_vs_delta(0); a1u=a1_vs_delta(3)
fig,ax=plt.subplots(4,3,figsize=(13,15)); col=plt.cm.viridis(np.linspace(.12,.92,4))
for r in range(4):
    for c in range(2):   # supervised columns: mark N/A
        ax[r,c].axis("off"); ax[r,c].text(.5,.5,"Supervised\n(actions / beliefs)\n— not trained for\nthis RL-only variant",ha="center",va="center",fontsize=9,color="0.4")
ax[0,0].set_title("Supervised Actions",fontsize=10); ax[0,1].set_title("Supervised Beliefs",fontsize=10); ax[0,2].set_title("RL (this variant)",fontsize=10)
for i,p in enumerate(VAL):
    ax[0,2].plot(DE,A[p]*100,"o",color=col[i],ms=3); ax[0,2].plot(DEf,C.logistic4(DEf,*C.fit_logistic(DE,A[p])["popt"])*100,"-",color=col[i],lw=1.2,label=f"{int(p*100)}%")
ax[0,2].legend(fontsize=6); ax[0,2].set_ylabel("resp (%)")
ax[1,2].plot(DE,c25*100,"o-",label="cued"); ax[1,2].plot(DE,u25*100,"s-",label="uncued"); ax[1,2].legend(fontsize=6); ax[1,2].set_ylabel("resp (%) @25%")
ax[2,2].plot(DE,c100*100,"o-",label="cued"); ax[2,2].plot(DE,u100*100,"s-",label="uncued"); ax[2,2].legend(fontsize=6); ax[2,2].set_ylabel("resp (%) @100%")
ax[3,2].plot(DE,a1c,"o-",label="cued change"); ax[3,2].plot(DE,a1u,"s-",label="uncued change"); ax[3,2].legend(fontsize=6); ax[3,2].set_ylabel(r"$\alpha_1$ @change"); ax[3,2].set_xlabel("Δ (°)")
for r in range(4): ax[r,2].grid(alpha=.25)
fig.suptitle(f"Fig 17 analog --- supervised vs RL (RL column reproduced; supervised = out-of-scope baseline) ({LAB}, iter {IT})",fontsize=11)
fig.tight_layout(rect=[0,0,1,.97]); fig.savefig(os.path.join(C.FIGS,f"fig17_{LAB}.png"),dpi=130,bbox_inches="tight"); plt.close(fig)
print(f"saved fig17_{LAB}")
