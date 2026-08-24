"""Base ATTENTION MAPS for affine_ew: raw 4x4 self-attention A[query patch→key patch] for all 7 frames
across the six cue×change conditions (prop 1.0, red), plus the timecourse of attention TO the cued and
TO the changed patch. All lessons applied: every frame shown (cue f1, change f5, post f6), dissociation
both ways, magnitudes (not argmax), mean over 96 trials."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dda_core as C
SNAP=sys.argv[1]; m,IT=C.load(SNAP); B=96
print(f"[dda-maps] iter={IT}")
CONDS=[("cue@S1 no-change",0,0,-1),("cue@S1 valid (chg@S1)",0,1,0),("cue@S1 invalid (chg@S4)",0,1,3),
       ("cue@S4 no-change",3,0,-1),("cue@S4 valid (chg@S4)",3,1,3),("cue@S4 invalid (chg@S1)",3,1,0)]
A={nm:C.attn_maps(m,cue,1.0,"red",ct,ci,B=B) for nm,cue,ct,ci in CONDS}
np.savez(os.path.join(C.FIGS,"..","data_dda_maps.npz"),iter=IT,**{f"a__{nm}":A[nm] for nm,*_ in CONDS})
# maps grid
vmax=max(A[nm].max() for nm,*_ in CONDS)
fig,ax=plt.subplots(len(CONDS),7,figsize=(7*1.5,len(CONDS)*1.55))
for r,(nm,cue,ct,ci) in enumerate(CONDS):
    for t in range(7):
        M=A[nm][t]; ax[r,t].imshow(M,cmap="magma",vmin=0,vmax=vmax)
        for (yy,xx),v in np.ndenumerate(M): ax[r,t].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5,color="white" if v<vmax*.6 else "black")
        ax[r,t].set_xticks(range(4)); ax[r,t].set_yticks(range(4)); ax[r,t].set_xticklabels(C.TOK,fontsize=4.5); ax[r,t].set_yticklabels(C.TOK,fontsize=4.5)
        if r==0: ax[r,t].set_title(f"f{t}"+(" cue" if t==1 else (" chg" if t==5 else (" post" if t==6 else ""))),fontsize=6.5)
        if t==0: ax[r,t].set_ylabel(nm,fontsize=5.5)
        ax[r,t].get_xticklabels()[cue].set_color("limegreen"); ax[r,t].get_xticklabels()[cue].set_fontweight("bold")
        if ct: ax[r,t].get_xticklabels()[ci].set_color("red")
fig.suptitle(f"affine_ew self-attention A[query→key] (mean/{B}); rows=cond, cols=frame; green=cued red=changed — iter {IT}",fontsize=9)
fig.tight_layout(rect=[0,0,1,.97]); fig.savefig(os.path.join(C.FIGS,"dda_maps.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
# timecourse: attention TO cued and TO changed
fig2,ax2=plt.subplots(1,2,figsize=(11,3.4))
for nm,cue,ct,ci in CONDS:
    ax2[0].plot(range(7),A[nm][:,:,cue].mean(1),marker="o",alpha=.7,label=nm if ct==0 else None)
    if ct: ax2[1].plot(range(7),A[nm][:,:,ci].mean(1),marker="o",alpha=.7,label=nm)
for a,t in zip(ax2,["attention TO the CUED patch","attention TO the CHANGED patch"]):
    a.axvline(1,ls=":",c="g",alpha=.5); a.axvline(5,ls=":",c="r",alpha=.5); a.axhline(0.25,ls=":",c="gray"); a.set_ylim(0,1.02)
    a.set_xlabel("frame"); a.set_ylabel("attention (mean over queries)"); a.set_title(t,fontsize=9); a.legend(fontsize=6)
fig2.suptitle(f"affine_ew attention timecourse — iter {IT} (uniform=0.25)",fontsize=10)
fig2.tight_layout(); fig2.savefig(os.path.join(C.FIGS,"dda_timecourse.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)
print("cued-patch attn by frame (cue@S1 valid):",[round(float(A['cue@S1 valid (chg@S1)'][t,:,0].mean()),2) for t in range(7)])
print("changed-patch attn f5/f6 — valid:",round(float(A['cue@S1 valid (chg@S1)'][5,:,0].mean()),2),round(float(A['cue@S1 valid (chg@S1)'][6,:,0].mean()),2),
      "| invalid:",round(float(A['cue@S1 invalid (chg@S4)'][5,:,3].mean()),2),round(float(A['cue@S1 invalid (chg@S4)'][6,:,3].mean()),2))
print("saved dda_maps / dda_timecourse + data_dda_maps.npz")
