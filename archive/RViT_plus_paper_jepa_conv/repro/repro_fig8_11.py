"""Figs 8-11 reproduction --- DECODING analysis. One data pass: train tiny MLP decoders on NATURAL
(unmodulated) states, then evaluate confusion matrices under attention modulation on S1.
  Fig 8  : change LOCATION (5-way) from the full mnemonic percept H, conditions {natural, spread,
           suppress-S1, enhance-S1} at t=5 (A-D) and t=6 (E-H).
  Fig 9  : change OCCURRENCE (2-way) from a single patch h1, {natural, enhance-S1, suppress-S1} × t=5/6.
  Fig 10 : LOCATION (5-way) + OCCURRENCE (2-way) from the actor's first activation layer.
  Fig 11 : S1-change vs no-change (2-way) from the actor activation, GRADED α1 inhibition (0→1), t=5/6.
Modulation applied from the change frame (clamp_from=5) so it shapes the decoded state.
Usage: repro_fig8_11.py <snap> <feedback> <label> [N_train] [N_test]"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro_core as C, repro_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
NTR=int(sys.argv[4]) if len(sys.argv)>4 else 3000
NTE=int(sys.argv[5]) if len(sys.argv)>5 else 2000
m,IT=C.load(SNAP,FB); K=S.n_keys(m); print(f"[fig8-11 {LAB}] iter={IT} K={K} Ntr={NTR} Nte={NTE}",flush=True)
FIGS=C.FIGS; HERE=os.path.dirname(os.path.abspath(__file__))

def feats(rollout_out, t):
    rec=rollout_out["rec"][:,t]                     # (B,512) tensor
    H=rec.numpy(); h1=rec[:, :S.DMEM].numpy(); act=S.actor_first_activation(m,rec)
    return H,h1,act

# ── training data (natural) ────────────────────────────────────────────────────────────────────────
print("[gen] train videos...",flush=True)
Vtr,loc,dl=S.gen_trials(0,1.0,NTR,p_change=0.5,seed=1); rtr=S.rollout(m,Vtr)
Hh={};h1h={};acth={}
for t in (5,6): Hh[t],h1h[t],acth[t]=feats(rtr,t)
yloc=S.loc5(loc); yocc=S.occ(loc)
# pool t=5 & t=6 for training
Xtr_H=np.concatenate([Hh[5],Hh[6]]); Xtr_h1=np.concatenate([h1h[5],h1h[6]]); Xtr_act=np.concatenate([acth[5],acth[6]])
yloc2=np.concatenate([yloc,yloc]); yocc2=np.concatenate([yocc,yocc])
print("[train] decoders...",flush=True)
decH_loc,nH=S.train_decoder(Xtr_H,yloc2,5)
dech1_occ,nh1=S.train_decoder(Xtr_h1,yocc2,2)
decAct_loc,nAl=S.train_decoder(Xtr_act,yloc2,5)
decAct_occ,nAo=S.train_decoder(Xtr_act,yocc2,2)

# ── shared test set (mixed) ─────────────────────────────────────────────────────────────────────────
print("[gen] test videos...",flush=True)
Vte,tloc,tdl=S.gen_trials(0,1.0,NTE,p_change=0.5,seed=2); tyloc=S.loc5(tloc); tyocc=S.occ(tloc)
CLAMPS=dict(natural=None, spread=S.clamp_spread(K,0), suppress=C.clamp_off(K,0), enhance=C.clamp_on(K,0))
cache={k:S.rollout(m,Vte,clamp=v,clamp_from=5) for k,v in CLAMPS.items()}   # roll test once per clamp

def cm_plot(ax,M,labels,title):
    Mn=M/np.clip(M.sum(1,keepdims=True),1,None)
    ax.imshow(Mn,cmap="Blues",vmin=0,vmax=1)
    for (i,j),v in np.ndenumerate(M): ax.text(j,i,str(v),ha="center",va="center",fontsize=6,color="white" if Mn[i,j]>.5 else "black")
    ax.set_xticks(range(len(labels))); ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels,fontsize=6,rotation=45); ax.set_yticklabels(labels,fontsize=6)
    ax.set_title(title,fontsize=8); ax.set_xlabel("pred",fontsize=6); ax.set_ylabel("true",fontsize=6)

# ── Fig 8: location from H ───────────────────────────────────────────────────────────────────────────
order=[("natural","no mod."),("spread","spread"),("suppress",r"$\alpha_1{=}0$"),("enhance",r"$\alpha_1{=}1$")]
fig,ax=plt.subplots(2,4,figsize=(17,10),layout="constrained")
for c,(ck,cn) in enumerate(order):
    for ri,t in enumerate((5,6)):
        H,_,_=feats(cache[ck],t); yhat=S.dec_predict(decH_loc,nH,H); M=S.confmat(tyloc,yhat,5)
        cm_plot(ax[ri,c],M,S.LOCNAMES,f"{cn}  t={t}")
fig.suptitle(f"Fig 8 --- decode change LOCATION from H, attention on S1 ({LAB}, iter {IT}; test n={NTE})",fontsize=12)
fig.savefig(os.path.join(FIGS,f"fig8_{LAB}.png"),dpi=130,bbox_inches="tight"); plt.close(fig)
print(f"saved fig8_{LAB}",flush=True)

# ── Fig 9: occurrence from single patch h1 ───────────────────────────────────────────────────────────
order3=[("natural","no mod."),("enhance",r"$\alpha_1{=}1$"),("suppress",r"$\alpha_1{=}0$")]
fig,ax=plt.subplots(2,3,figsize=(11,8))
for c,(ck,cn) in enumerate(order3):
    for ri,t in enumerate((5,6)):
        _,h1,_=feats(cache[ck],t); yhat=S.dec_predict(dech1_occ,nh1,h1); M=S.confmat(tyocc,yhat,2)
        cm_plot(ax[ri,c],M,["No change","Change"],f"{cn}  t={t}")
fig.suptitle(f"Fig 9 --- decode change OCCURRENCE from single patch $h_1$ ({LAB}, iter {IT}; n={NTE})",fontsize=12)
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig(os.path.join(FIGS,f"fig9_{LAB}.png"),dpi=140,bbox_inches="tight"); plt.close(fig)
print(f"saved fig9_{LAB}",flush=True)

# ── Fig 10: location + occurrence from actor first activation ─────────────────────────────────────────
fig,ax=plt.subplots(2,4,figsize=(16,10),layout="constrained")
for c,(ck,cn) in enumerate([("natural","no mod."),("enhance",r"$\alpha_1{=}1$")]):
    for ri,t in enumerate((5,6)):
        _,_,act=feats(cache[ck],t)
        M=S.confmat(tyloc,S.dec_predict(decAct_loc,nAl,act),5); cm_plot(ax[ri,c],M,S.LOCNAMES,f"loc: {cn} t={t}")
        M2=S.confmat(tyocc,S.dec_predict(decAct_occ,nAo,act),2); cm_plot(ax[ri,c+2],M2,["No change","Change"],f"occ: {cn} t={t}")
fig.suptitle(f"Fig 10 --- decode from actor first activation layer ({LAB}, iter {IT}; n={NTE})",fontsize=12)
fig.savefig(os.path.join(FIGS,f"fig10_{LAB}.png"),dpi=130,bbox_inches="tight"); plt.close(fig)
print(f"saved fig10_{LAB}",flush=True)

# ── Fig 11: S1-change vs no-change from actor activation, graded α1 ───────────────────────────────────
print("[gen] fig11 S1/no-change test...",flush=True)
rng=np.random.default_rng(7); NB=NTE
lab11=np.zeros(NB,int); vids=[]
for n in range(NB):
    if rng.random()<0.5: vids.append(C.make_video(0,0.25,"red",1,0,float(rng.uniform(1,60)))); lab11[n]=1
    else: vids.append(C.make_video(0,0.25,"red",0,-1,0.0))
V11=C._tens(vids)
GR=[0.0,0.25,0.5,0.75,1.0]
fig,ax=plt.subplots(2,5,figsize=(18,8.5),layout="constrained")
for c,a in enumerate(GR):
    ro=S.rollout(m,V11,clamp=S.clamp_alpha(K,0,a),clamp_from=5)
    for ri,t in enumerate((5,6)):
        _,_,act=feats(ro,t); yhat=S.dec_predict(decAct_occ,nAo,act); M=S.confmat(lab11,yhat,2)
        cm_plot(ax[ri,c],M,["No change","S1 change"],f"$\\alpha_1$={a}  t={t}")
fig.suptitle(f"Fig 11 --- decode S1-change vs no-change from actor activation, graded $\\alpha_1$ ({LAB}, iter {IT}; n={NB})",fontsize=12)
fig.savefig(os.path.join(FIGS,f"fig11_{LAB}.png"),dpi=130,bbox_inches="tight"); plt.close(fig)
print(f"saved fig11_{LAB}",flush=True)
np.savez(os.path.join(HERE,f"data_fig8_11_{LAB}.npz"),iter=IT,Ntr=NTR,Nte=NTE)
print(f"[fig8-11 {LAB}] DONE",flush=True)
