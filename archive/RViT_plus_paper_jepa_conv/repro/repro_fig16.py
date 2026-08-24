"""Fig 16 reproduction --- the 'stimulation experiments': SDT CRITERION c and SENSITIVITY d' as
attention on S1 is biased parametrically, applied at CUE-time (t=1) vs CHANGE-time (t=5). Rows: c, d'.
Cols: manipulate@cue, manipulate@change. Four lines = {Cue 25/100%} x {change at S1 / S4}.
Hit = P(press>=5) on change trials (Δ fixed near threshold); FA = P(press>=5) on no-change trials.
c=-1/2(z(H)+z(FA)); d'=z(H)-z(FA). Usage: repro_fig16.py <snap> <feedback> <label>"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro_core as C, repro_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
B=int(sys.argv[4]) if len(sys.argv)>4 else 300
MAG=float(sys.argv[5]) if len(sys.argv)>5 else 18.0
m,IT=C.load(SNAP,FB); K=S.n_keys(m); print(f"[fig16 {LAB}] iter={IT} K={K} Δ={MAG} B={B}")
ALPHA=[0.0,0.25,0.5,0.75,1.0]                 # 0.5 ≈ natural (no bias)
COND=[(0.25,0,"Cue25 chg-S1","tab:blue"),(1.0,0,"Cue100 chg-S1","tab:green"),
      (0.25,3,"Cue25 chg-S4","tab:orange"),(1.0,3,"Cue100 chg-S4","tab:red")]
TIMES=[("manipulate @ cue (t=1)",1),("manipulate @ change (t=5)",5)]
res={}
for tlab,tf in TIMES:
    for prop,cl,name,col in COND:
        cc=[];dd=[]
        # FA uses no-change trials; still bias S1 attention the same way
        for a in ALPHA:
            clamp=S.clamp_alpha(K,0,a)
            hit=S.det_rate(m,0,prop,1,cl,MAG,clamp,tf,B)
            fa =S.det_rate(m,0,prop,0,-1,0.0,clamp,tf,B)
            s=S.sdt(hit,fa,B); cc.append(s["c"]); dd.append(s["dprime"])
        res[(tf,name)]=dict(c=cc,d=dd,col=col)
        print(f"[fig16 {LAB}] {tlab:26s} {name:14s} c={[round(x,2) for x in cc]}  d'={[round(x,2) for x in dd]}")
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig16_{LAB}.npz"),
         iter=IT,alpha=ALPHA,mag=MAG,**{f"c__{tf}__{n}":res[(tf,n)]["c"] for (tf,n) in res},
         **{f"d__{tf}__{n}":res[(tf,n)]["d"] for (tf,n) in res})
fig,ax=plt.subplots(2,2,figsize=(11,8))
for cj,(tlab,tf) in enumerate(TIMES):
    for prop,cl,name,col in COND:
        r=res[(tf,name)]
        ax[0,cj].plot(ALPHA,r["c"],"o-",color=col,label=name,ms=5)
        ax[1,cj].plot(ALPHA,r["d"],"o-",color=col,label=name,ms=5)
    ax[0,cj].set_title(tlab,fontsize=10); ax[0,cj].axvline(0.5,ls=":",c="0.6",lw=1)
    ax[1,cj].axvline(0.5,ls=":",c="0.6",lw=1)
    ax[1,cj].set_xlabel(r"attention bias on $S_1$  ($\alpha_1$: 0=suppress, 0.5=natural, 1=enhance)",fontsize=9)
for a in ax.flat: a.legend(fontsize=7); a.grid(alpha=.25)
ax[0,0].set_ylabel("Criterion  $c$"); ax[1,0].set_ylabel("Sensitivity  $d'$")
fig.suptitle(f"Fig 16 --- SDT criterion & sensitivity vs attention bias on $S_1$  ({LAB}, iter {IT}; Δ={MAG:.0f}°, n={B})",fontsize=11)
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig(os.path.join(C.FIGS,f"fig16_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print(f"saved fig16_{LAB}")
