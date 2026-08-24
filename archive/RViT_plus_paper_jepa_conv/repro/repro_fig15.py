"""Fig 15 reproduction --- bias / value / entropy. A: policy entropy H(π) at the change frame vs graded
attention α1 on S1, for four {cue×change} conditions (entropy falls as attention resolves the decision).
B: criterion c vs value V, traced parametrically as α1 is swept (the value–criterion coupling: higher
value ↔ more liberal criterion). Usage: repro_fig15.py <snap> <feedback> <label>"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro_core as C, repro_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
N=400; MAG=18.0; m,IT=C.load(SNAP,FB); K=S.n_keys(m); print(f"[fig15 {LAB}] iter={IT} K={K}")
ALPHA=[0.0,0.25,0.5,0.75,1.0]
COND=[(0.25,0,"Cue25 chg-S1","tab:blue"),(1.0,0,"Cue100 chg-S1","tab:green"),
      (0.25,3,"Cue25 chg-S4","tab:orange"),(1.0,3,"Cue100 chg-S4","tab:red")]
def entropy(p):                       # p (N,2) softmax → mean binary entropy
    q=np.clip(p,1e-9,1); return float(np.mean(-(q*np.log(q)).sum(1)))
res={}
for prop,cl,name,col in COND:
    ent=[];cc=[];vv=[]
    for a in ALPHA:
        clamp=S.clamp_alpha(K,0,a)
        V=C._tens([C.make_video(0,prop,"red",1,cl,MAG) for _ in range(N)])
        r=S.rollout(m,V,clamp=clamp,clamp_from=5)
        lg=r["logits"][:,5,:]; pi=np.exp(lg-lg.max(1,keepdims=True)); pi/=pi.sum(1,keepdims=True)
        ent.append(entropy(pi)); vv.append(float(np.mean(r["Vsc"][:,5])))
        hit=S.det_rate(m,0,prop,1,cl,MAG,clamp,5,B=N); fa=S.det_rate(m,0,prop,0,-1,0.0,clamp,5,B=N)
        cc.append(S.sdt(hit,fa,N)["c"])
    res[name]=dict(ent=ent,c=cc,v=vv,col=col)
    print(f"[fig15 {LAB}] {name:14s} H={[round(x,3) for x in ent]}  c={[round(x,2) for x in cc]}  V={[round(x,2) for x in vv]}")
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig15_{LAB}.npz"),iter=IT,alpha=ALPHA,
         **{f"ent__{n}":res[n]["ent"] for n in res},**{f"c__{n}":res[n]["c"] for n in res},**{f"v__{n}":res[n]["v"] for n in res})
fig,ax=plt.subplots(1,2,figsize=(12,4.6))
for name in res:
    r=res[name]; ax[0].plot(ALPHA,r["ent"],"o-",color=r["col"],label=name)
    ax[1].plot(r["v"],r["c"],"o-",color=r["col"],label=name)
ax[0].set_xlabel(r"attention bias $\alpha_1$ on $S_1$"); ax[0].set_ylabel("policy entropy  H(π) (nats)"); ax[0].axvline(0.5,ls=":",c="0.6"); ax[0].set_title("A  entropy vs attention")
ax[1].set_xlabel("value  V"); ax[1].set_ylabel("criterion  c"); ax[1].set_title(r"B  criterion vs value (α$_1$ swept)")
for a in ax: a.legend(fontsize=7); a.grid(alpha=.25)
fig.suptitle(f"Fig 15 --- entropy & criterion–value coupling under attention ({LAB}, iter {IT}; Δ={MAG:.0f}°, n={N})",fontsize=11)
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig(os.path.join(C.FIGS,f"fig15_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print(f"saved fig15_{LAB}")
