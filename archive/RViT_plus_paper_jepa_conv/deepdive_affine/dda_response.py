"""PROPORTION (validity) modulation of RESPONSE + whether proportion is even perceived.
(A) decode proportion / value / cue-pos / change from the recurrent cell (is the validity ring encoded?).
(B) psychometric: valid (change@cued) vs invalid (change@uncued) P(detect) over magnitude, at EACH
proportion 0.25..1.0 — does the cueing benefit (valid−invalid gap) scale with displayed validity?
(C) natural trials (change-location drawn cued-with-prob-=-proportion): overall detect + where."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dda_core as C
SNAP=sys.argv[1]; m,IT=C.load(SNAP); T=C.T; COLS=["blue","green","red"]
print(f"[dda-resp] iter={IT}")

# ---------- (A) is proportion perceived? decode from the cell ----------
def labeled(n, seed=0):
    rng=np.random.default_rng(seed); vids=[]; lab=dict(cue=[],prop=[],val=[],chg=[],loc=[])
    PRP=[0.25,0.5,0.75,1.0]
    for _ in range(n):
        cue=int(rng.integers(4)); p=PRP[int(rng.integers(4))]; col=COLS[int(rng.integers(3))]; ct=int(rng.random()<.5)
        loc=int(rng.integers(4)) if ct else -1
        vids.append(C.make_video(cue,p,col,ct,loc,56.0))
        lab["cue"].append(cue); lab["prop"].append(p); lab["val"].append(C.COLOR_VAL[col]); lab["chg"].append(ct); lab["loc"].append(loc)
    with torch.no_grad(): cell=m.forward_rl_sequence(C._tens(vids),return_cell=True)["cell_seq"].numpy()
    return cell.reshape(n,T,-1), {k:np.array(v) for k,v in lab.items()}
def dec(X,y):
    X=(X-X.mean(0))/(X.std(0)+1e-6); y=np.unique(y,return_inverse=True)[1]   # encode floats→class indices
    return cross_val_score(LogisticRegression(max_iter=300,C=0.3),X,y,cv=4,scoring="balanced_accuracy").mean()
cell,lab=labeled(440)
dprop=[dec(cell[:,t],lab["prop"]) for t in range(T)]; dval=[dec(cell[:,t],lab["val"]) for t in range(T)]
dcue=[dec(cell[:,t],lab["cue"]) for t in range(T)]
print(f"decode proportion(4-way,chance .25): {[round(x,2) for x in dprop]}")
print(f"decode value(3-way,chance .33):      {[round(x,2) for x in dval]}")
print(f"decode cue-pos(4-way,chance .25):     {[round(x,2) for x in dcue]}")

# ---------- (B) psychometric valid vs invalid at each proportion ----------
MAGS=[8,12,16,20,28]; PROPS=[0.25,0.5,0.75,1.0]; Bp=150
def rate(cue,ci,mag,prop): return C.detect_rate(m,cue,ci,mag,prop,B=Bp)
PSY={}  # (prop, 'valid'/'invalid') -> list over mags
for p in PROPS:
    v=[]; iv=[]
    for mg in MAGS:
        v.append(np.mean([rate(cue,cue,mg,p) for cue in (0,3)]))
        iv.append(np.mean([rate(cue,unc,mg,p) for cue,unc in ((0,3),(3,0))]))
    PSY[(p,"valid")]=v; PSY[(p,"invalid")]=iv
fig,ax=plt.subplots(1,len(PROPS),figsize=(3.1*len(PROPS),3.4),sharey=True)
for k,p in enumerate(PROPS):
    ax[k].plot(MAGS,PSY[(p,"valid")],"o-",c="tab:green",label="valid"); ax[k].plot(MAGS,PSY[(p,"invalid")],"s-",c="tab:red",label="invalid")
    ax[k].set_title(f"proportion {p}",fontsize=9); ax[k].set_xlabel("|Δθ| (deg)"); ax[k].set_ylim(-.02,1.02)
    if k==0: ax[k].set_ylabel("P(detect)"); ax[k].legend(fontsize=7)
fig.suptitle(f"RESPONSE: valid vs invalid psychometric at each validity — affine_ew iter {IT}",fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dda_resp_psych_by_prop.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
# cueing-benefit gap vs proportion, averaged over threshold mags 12-20
thr=[i for i,mg in enumerate(MAGS) if 12<=mg<=20]
gap=[float(np.mean([PSY[(p,"valid")][i]-PSY[(p,"invalid")][i] for i in thr])) for p in PROPS]
fig2,ax2=plt.subplots(figsize=(5,3.4)); ax2.plot(PROPS,gap,"o-",c="purple")
ax2.set_xlabel("displayed cue proportion (validity)"); ax2.set_ylabel("valid−invalid P(detect) gap\n(threshold mags 12–20°)")
ax2.set_title(f"Does the cueing benefit scale with validity? iter {IT}",fontsize=9); ax2.axhline(0,ls=":",c="gray")
fig2.tight_layout(); fig2.savefig(os.path.join(C.FIGS,"dda_resp_gap_vs_prop.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)

np.savez(os.path.join(C.FIGS,"..","summary_dda_resp.npz"), frames=list(range(T)), dprop=dprop, dval=dval, dcue=dcue,
         mags=MAGS, props=PROPS, gap=gap, **{f"psy__{p}__{k}":PSY[(p,k)] for p in PROPS for k in ("valid","invalid")})
print("psychometric valid/invalid by proportion:")
for p in PROPS: print(f"  prop {p}: valid={[round(x,2) for x in PSY[(p,'valid')]]}  invalid={[round(x,2) for x in PSY[(p,'invalid')]]}")
print(f"cueing-benefit gap (12-20°) vs proportion {PROPS}: {[round(g,3) for g in gap]}")
print("saved dda_resp_psych_by_prop / dda_resp_gap_vs_prop + summary_dda_resp.npz")
