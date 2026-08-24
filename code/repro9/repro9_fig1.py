"""Fig 1 (task/environment) for the 9-stimulus grid9 task (vda9, 75x75, 3x3 Gabor grid, corner cues
S1=TL / S9=BR). A: 7-step trial timeline (blank, cue, blank, 9 Gabors from t3, change at t5) + no-change
branch. B: cue configurations (validity ring) x corner position, with the EMPIRICAL change-location
probability our env produces on the 3x3 grid."""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repro9_core as C
FIGS=C.FIGS
def render(cue,prop,color,ct,ci,mag=56.0):
    e=C._env(); o=e.reset()
    while e.change_true!=ct: o=e.reset()
    e.cue_index=int(cue); e.cue_color=color; e.proportion=float(prop)
    if ct: e.change_index=int(ci); e.orientation_change=float(mag)
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return fr
chg=render(0,1.0,"red",1,0); noc=render(0,1.0,"red",0,-1)
fig=plt.figure(figsize=(12,3.4)); gs=fig.add_gridspec(2,7,height_ratios=[2,1])
lab={0:"$t_0$ black",1:"$t_1$ cue",2:"$t_2$ black",3:"$t_3$ stim onset",4:"$t_4$",5:"$t_5$ change",6:"$t_6$"}
for t in range(7):
    a=fig.add_subplot(gs[0,t]); a.imshow(np.clip(chg[t],0,1)); a.set_xticks([]); a.set_yticks([]); a.set_title(lab[t],fontsize=8)
for j,t in enumerate([5,6]):
    a=fig.add_subplot(gs[1,5+j]); a.imshow(np.clip(noc[t],0,1)); a.set_xticks([]); a.set_yticks([])
    if j==0: a.set_ylabel("no-change\nbranch",fontsize=7)
fig.add_subplot(gs[1,0]).axis("off")
fig.suptitle("Figure 1A — Task timeline (vda9, 3×3 grid): 7 steps; corner cue at $t_1$, 9 Gabors from $t_3$, change (50%) at $t_5$",fontsize=8.5)
fig.tight_layout(rect=[0,0,1,0.93]); fig.savefig(os.path.join(FIGS,"fig1A_task_timeline.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
# ---- B: cue configs × corner, empirical 3x3 change-prob grid ----
def change_prob_grid(cue,prop,N=3000):
    e=C._env(); cnt=np.zeros(C.NP)
    for _ in range(N):
        e.reset()
        while e.change_true!=1: e.reset()
        e.cue_index=cue; e.proportion=prop; cnt[e._draw_change_index()]+=1
    return (cnt/cnt.sum()).reshape(3,3)*100
VAL=[0.0,0.25,0.5,0.75,1.0]
fig2,ax=plt.subplots(len(VAL),4,figsize=(4*1.6,len(VAL)*1.5))
for r,p in enumerate(VAL):
    for c,(cue,nm) in enumerate([(0,"S1 (TL)"),(8,"S9 (BR)")]):
        e=C._env(); e.reset(); e.change_true=0; e.cue_index=cue; e.cue_color="white"; e.proportion=p; e.t=1
        img=e._next_observation()
        ax[r,2*c].imshow(np.clip(img,0,1)); ax[r,2*c].set_xticks([]); ax[r,2*c].set_yticks([])
        if r==0: ax[r,2*c].set_title(f"cue {nm}",fontsize=8)
        if c==0: ax[r,2*c].set_ylabel(f"{int(p*100)}%",fontsize=9)
        g=change_prob_grid(cue,p); ax[r,2*c+1].imshow(g,cmap="Greens",vmin=0,vmax=100)
        for (yy,xx),v in np.ndenumerate(g): ax[r,2*c+1].text(xx,yy,f"{v:.0f}",ha="center",va="center",fontsize=6,color="white" if v>60 else "black")
        ax[r,2*c+1].set_xticks([]); ax[r,2*c+1].set_yticks([])
        if r==0: ax[r,2*c+1].set_title("P(change) %",fontsize=7)
fig2.suptitle("Figure 1B — Cue configs: validity ring × corner (S1/S9), empirical 3×3 change-location probability (our env)",fontsize=7.5)
fig2.tight_layout(rect=[0,0,1,0.95]); fig2.savefig(os.path.join(FIGS,"fig1B_cue_configs.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)
print("grid9 change-prob (cue S1): "+" | ".join(f"{int(p*100)}%={np.round(change_prob_grid(0,p).flatten(),0)}" for p in [0.0,0.25,1.0]))
print("saved fig1A_task_timeline + fig1B_cue_configs (grid9)")
