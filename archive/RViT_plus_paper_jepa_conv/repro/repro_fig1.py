"""Reproduce Fig 1 (task / environment) for our vda4 task — a cartoon rendered from the actual env
(no model). A: the 7-step trial timeline (black, cue, black, four Gabors, change at t=5), with the
change / no-change branch. B: the cue configurations — cue image (validity ring) × cue position
(S1/S4) × validity {25,50,75,100}%, with the EMPIRICAL change-probability grid our env produces."""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from envs import make_env
FIGS=os.path.join(os.path.dirname(os.path.abspath(__file__)),"figs"); os.makedirs(FIGS,exist_ok=True)
def env(): return make_env("vda4",T=7,frame_repeat=1,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
def render_trial(cue,prop,color,change_true,change_idx,mag=56.0):
    e=env(); o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=cue; e.cue_color=color; e.proportion=prop
    if change_true: e.change_index=change_idx; e.orientation_change=mag
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return fr
# ---- A: timeline (change trial) + no-change branch for t5,t6 ----
chg=render_trial(0,1.0,"red",1,0); noc=render_trial(0,1.0,"red",0,-1)
fig=plt.figure(figsize=(12,3.4)); gs=fig.add_gridspec(2,7,height_ratios=[2,1])
lab={0:"$t_0$ black",1:"$t_1$ cue",2:"$t_2$ black",3:"$t_3$ stim onset",4:"$t_4$",5:"$t_5$ change",6:"$t_6$"}
for t in range(7):
    a=fig.add_subplot(gs[0,t]); a.imshow(np.clip(chg[t],0,1)); a.set_xticks([]); a.set_yticks([]); a.set_title(lab[t],fontsize=8)
# no-change branch (t5,t6)
for j,t in enumerate([5,6]):
    a=fig.add_subplot(gs[1,5+j]); a.imshow(np.clip(noc[t],0,1)); a.set_xticks([]); a.set_yticks([])
    if j==0: a.set_ylabel("no-change\nbranch",fontsize=7)
fig.add_subplot(gs[1,0]).axis("off")
fig.suptitle("Figure 1A — Task timeline (vda4): 7 steps; cue at $t_1$, stimuli from $t_3$, change (50% of trials) at $t_5$",fontsize=9)
fig.tight_layout(rect=[0,0,1,0.93]); fig.savefig(os.path.join(FIGS,"fig1A_task_timeline.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
# ---- B: cue configs (validity ring) × position, + empirical change-prob grid ----
def change_prob_grid(cue,prop,N=4000):
    e=env(); cnt=np.zeros(4)
    for _ in range(N):
        e.reset()
        while e.change_true!=1: e.reset()
        e.cue_index=cue; e.proportion=prop; cnt[e._draw_change_index()]+=1
    return (cnt/cnt.sum()).reshape(2,2)*100     # [[S1,TR],[BL,S4]] percent
VAL=[0.25,0.5,0.75,1.0]
fig2,ax=plt.subplots(len(VAL),4,figsize=(4*1.5,len(VAL)*1.5))
for r,p in enumerate(VAL):
    for c,(cue,nm) in enumerate([(0,"S1"),(3,"S4")]):
        e=env(); e.reset(); e.change_true=0; e.cue_index=cue; e.cue_color="white"; e.proportion=p; e.t=1
        img=e._next_observation()
        ax[r,2*c].imshow(np.clip(img,0,1)); ax[r,2*c].set_xticks([]); ax[r,2*c].set_yticks([])
        if r==0: ax[r,2*c].set_title(f"cue {nm}",fontsize=8)
        if c==0: ax[r,2*c].set_ylabel(f"{int(p*100)}%",fontsize=9)
        g=change_prob_grid(cue,p); ax[r,2*c+1].imshow(g,cmap="Greens",vmin=0,vmax=100)
        for (yy,xx),v in np.ndenumerate(g): ax[r,2*c+1].text(xx,yy,f"{v:.0f}",ha="center",va="center",fontsize=7,color="white" if v>60 else "black")
        ax[r,2*c+1].set_xticks([]); ax[r,2*c+1].set_yticks([])
        if r==0: ax[r,2*c+1].set_title("P(change) %",fontsize=7)
fig2.suptitle("Figure 1B — Cue configurations: validity ring (white) × position, with empirical change-location probability (our env)",fontsize=8)
fig2.tight_layout(rect=[0,0,1,0.95]); fig2.savefig(os.path.join(FIGS,"fig1B_cue_configs.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)
print("change-prob grid (cue S1): "+" | ".join(f"{int(p*100)}%={np.round(change_prob_grid(0,p).flatten(),0)}" for p in VAL))
print("saved fig1A_task_timeline + fig1B_cue_configs")
