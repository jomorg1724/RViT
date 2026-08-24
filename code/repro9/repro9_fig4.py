"""Fig 4 (intrinsic attention dynamics) for a grid9 variant. A: averaged attention heatmaps per timestep
x validity, no-change cue-S1, as 3x3 spatial maps. B: attention on S1(α1, TL) and S9(α9, BR) vs time,
validities incl 0. C: α1 at t_change vs Δ for uncued change @S9 or cued change @S1.
crossattn1 K=18 (9 img + 9 mem); affine_ew K=9. Usage: repro9_fig4.py <snap> <feedback> <label>"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repro9_core as C
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
m,IT=C.load(SNAP,FB); print(f"[fig4-9 {LAB}] iter={IT}"); VAL=[0.0,0.25,0.5,0.75,1.0]; B=96
def loc_attn(A):     # A (7,9,K) -> (7,9): attention to each location (mean over queries)
    K=A.shape[-1]
    if K==2*C.NP: return np.stack([A[:,:,i].mean(1)+A[:,:,C.NP+i].mean(1) for i in range(C.NP)],axis=1)
    return np.stack([A[:,:,i].mean(1) for i in range(C.NP)],axis=1)
LA={p:loc_attn(C.attn_maps(m,0,p,"red",0,-1,B=B)) for p in VAL}     # (7,9)
vmax=max(LA[p].max() for p in VAL)
fig,ax=plt.subplots(len(VAL),7,figsize=(7*1.25,len(VAL)*1.35))
for r,p in enumerate(VAL):
    for t in range(7):
        M=LA[p][t].reshape(C.GR,C.GC); ax[r,t].imshow(M,cmap="Purples",vmin=0,vmax=vmax)
        for (yy,xx),v in np.ndenumerate(M): ax[r,t].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5,color="white" if v>vmax*.6 else "black")
        ax[r,t].set_xticks([]); ax[r,t].set_yticks([])
        if r==0: ax[r,t].set_title(f"t{t}"+(" cue" if t==1 else (" chg" if t==5 else "")),fontsize=7)
        if t==0: ax[r,t].set_ylabel(f"{int(p*100)}%",fontsize=8)
fig.suptitle(f"Fig 4A — {C.TAG}: attention {C.GR}×{C.GC} heatmaps per timestep × validity (no-change, cued)",fontsize=8)
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig(os.path.join(C.FIGS,f"fig4A_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
fig2,ax2=plt.subplots(figsize=(6,4)); BL=plt.cm.Blues(np.linspace(.35,.95,len(VAL))); RD=plt.cm.Oranges(np.linspace(.35,.95,len(VAL)))
for i,p in enumerate(VAL):
    ax2.plot(range(7),LA[p][:,0],"-o",color=BL[i],ms=3,label=f"α1 {int(p*100)}%")
    ax2.plot(range(7),LA[p][:,C.NP-1],"-s",color=RD[i],ms=3,label=f"α{C.NSTIM} {int(p*100)}%")
ax2.axvline(1,ls=":",c="g",alpha=.4); ax2.axvline(5,ls=":",c="r",alpha=.4)
ax2.set_xlabel("time step"); ax2.set_ylabel(f"attention (cued α1 blue / uncued α{C.NSTIM} orange)"); ax2.legend(fontsize=5,ncol=2)
ax2.set_title(f"Fig 4B — {C.TAG}: cued/uncued attention vs time (no-change) iter {IT}",fontsize=9)
fig2.tight_layout(); fig2.savefig(os.path.join(C.FIGS,f"fig4B_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)
DE=[0,6,12,18,24,30,40]
a1_unc={p:[loc_attn(C.attn_maps(m,0,p,"red",1,C.CUES[-1],float(d),B=64))[5,0] for d in DE] for p in VAL}
a1_cue={p:[loc_attn(C.attn_maps(m,0,p,"red",1,0,float(d),B=64))[5,0] for d in DE] for p in VAL}
fig3,ax3=plt.subplots(1,2,figsize=(10,3.6),sharey=True)
for i,p in enumerate(VAL):
    ax3[0].plot(DE,a1_unc[p],"-o",color=BL[i],ms=3,label=f"{int(p*100)}%")
    ax3[1].plot(DE,a1_cue[p],"-o",color=BL[i],ms=3,label=f"{int(p*100)}%")
ax3[0].set_title(f"uncued change @{C.SHI}",fontsize=9); ax3[1].set_title(f"cued change @{C.SLO}",fontsize=9)
for a in ax3: a.set_xlabel("Δ (°)"); a.set_ylabel("α1 at t_change"); a.legend(fontsize=6)
fig3.suptitle(f"Fig 4C — {C.TAG}: attention on {C.SLO} at change vs Δ (iter {IT})",fontsize=10)
fig3.tight_layout(rect=[0,0,1,.94]); fig3.savefig(os.path.join(C.FIGS,f"fig4C_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig3)
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig4_{LAB}.npz"),iter=IT,val=VAL,DE=DE,
         **{f"loc__{p}":LA[p] for p in VAL},**{f"a1unc__{p}":a1_unc[p] for p in VAL},**{f"a1cue__{p}":a1_cue[p] for p in VAL})
print(f"[fig4-9 {LAB}] α1@cue(t1) by val:",[round(LA[p][1,0],2) for p in VAL]," α1@chg(t5):",[round(LA[p][5,0],2) for p in VAL])
print(f"saved fig4A/B/C_{LAB} + data_fig4_{LAB}.npz")
