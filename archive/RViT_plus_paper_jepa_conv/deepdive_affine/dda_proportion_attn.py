"""PROPORTION (validity) modulation of ATTENTION — exercised properly. For each proportion
{0.25,0.5,0.75,1.0} we present VALID (change@cued) AND INVALID (change@uncued) changes (averaged over
the two cue positions) and ask whether the displayed validity ring changes (a) the cue-frame focus,
(b) how strongly the cued patch is monitored through the gabor phase, and (c) the change-lock onto the
changed patch for valid vs invalid changes. Attention A is (7,4,4): A[i,j]=query patch i→key patch j;
metrics are attention TO a key patch averaged over the 4 queries; uniform=0.25."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dda_core as C
SNAP=sys.argv[1]; m,IT=C.load(SNAP); B=96; PROPS=[0.25,0.5,0.75,1.0]
print(f"[dda-prop-attn] iter={IT}")
def to_key(A,f,k): return float(A[f,:,k].mean())   # attention TO key patch k at frame f, mean over queries
# average over cue positions S1(0)/S4(3); valid: change@cued; invalid: change@the-other
PAIRS=[(0,3),(3,0)]  # (cue, uncued-change-target)
rows=[]
MAPS={}  # (prop, kind) -> mean A over cue positions (7,4,4) aligned so col 'cued' & 'changed' interpretable per cue
for p in PROPS:
    met={"cue_focus":[], "mon_cued":[], "vlock5":[], "vlock6":[], "ilock5":[], "ilock6":[]}
    for cue,unc in PAIRS:
        Av=C.attn_maps(m,cue,p,"red",1,cue,B=B)      # VALID  (change@cued)
        Ai=C.attn_maps(m,cue,p,"red",1,unc,B=B)      # INVALID(change@uncued)
        met["cue_focus"].append(to_key(Av,1,cue))            # f1 attention to cued
        met["mon_cued"].append(np.mean([to_key(Av,f,cue) for f in (3,4)]))  # pre-change monitoring of cued
        met["vlock5"].append(to_key(Av,5,cue)); met["vlock6"].append(to_key(Av,6,cue))      # valid: lock on cued(=changed)
        met["ilock5"].append(to_key(Ai,5,unc)); met["ilock6"].append(to_key(Ai,6,unc))      # invalid: lock on uncued changed
    rows.append({k:float(np.mean(v)) for k,v in met.items()})
    MAPS[(p,"valid")]=C.attn_maps(m,0,p,"red",1,0,B=B); MAPS[(p,"invalid")]=C.attn_maps(m,0,p,"red",1,3,B=B)

# ---- metric curves vs proportion ----
fig,ax=plt.subplots(1,2,figsize=(11,3.6)); U=0.25
ax[0].plot(PROPS,[r["cue_focus"] for r in rows],"o-",label="cue-frame focus on cued (f1)")
ax[0].plot(PROPS,[r["mon_cued"] for r in rows],"s-",label="monitoring of cued (f3-4)")
ax[0].axhline(U,ls=":",c="gray",label="uniform 0.25"); ax[0].set_ylim(0,1.02)
ax[0].set_xlabel("cue proportion (validity)"); ax[0].set_ylabel("attention to cued patch"); ax[0].set_title("CUE-TIME attention vs validity",fontsize=9); ax[0].legend(fontsize=7)
ax[1].plot(PROPS,[r["vlock6"] for r in rows],"o-",c="tab:green",label="VALID lock on changed (f6)")
ax[1].plot(PROPS,[r["vlock5"] for r in rows],"o--",c="tab:green",alpha=.6,label="VALID f5")
ax[1].plot(PROPS,[r["ilock6"] for r in rows],"s-",c="tab:red",label="INVALID lock on changed (f6)")
ax[1].plot(PROPS,[r["ilock5"] for r in rows],"s--",c="tab:red",alpha=.6,label="INVALID f5")
ax[1].axhline(U,ls=":",c="gray"); ax[1].set_ylim(0,1.02)
ax[1].set_xlabel("cue proportion (validity)"); ax[1].set_ylabel("attention to CHANGED patch"); ax[1].set_title("CHANGE-TIME lock vs validity",fontsize=9); ax[1].legend(fontsize=6)
fig.suptitle(f"PROPORTION (validity) modulation of attention — affine_ew iter {IT} (valid+invalid both exercised)",fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dda_prop_attn_metrics.png"),dpi=150,bbox_inches="tight"); plt.close(fig)

# ---- raw 4x4 maps: proportions × {valid,invalid} at f1/f5/f6 ----
def grid(kind,fname):
    cols=[(p,f) for p in PROPS for f in (1,5,6)]; vmax=max(MAPS[(p,kind)][f].max() for p in PROPS for f in (1,5,6))
    fig,ax=plt.subplots(len(PROPS),3,figsize=(3*1.7,len(PROPS)*1.6))
    for r,p in enumerate(PROPS):
        for c,f in enumerate((1,5,6)):
            M=MAPS[(p,kind)][f]; ax[r,c].imshow(M,cmap="magma",vmin=0,vmax=vmax)
            for (yy,xx),v in np.ndenumerate(M): ax[r,c].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=6,color="white" if v<vmax*.6 else "black")
            ax[r,c].set_xticks(range(4)); ax[r,c].set_yticks(range(4)); ax[r,c].set_xticklabels(C.TOK,fontsize=5); ax[r,c].set_yticklabels(C.TOK,fontsize=5)
            if r==0: ax[r,c].set_title(["f1 cue","f5 chg","f6 post"][c],fontsize=8)
            if c==0: ax[r,c].set_ylabel(f"prop {p}",fontsize=8)
            ax[r,c].get_xticklabels()[0].set_color("limegreen")  # cue@S1 here
            ax[r,c].get_xticklabels()[0 if kind=="valid" else 3].set_color("red")  # changed col
    fig.suptitle(f"affine_ew self-attn A[query→key] — {kind} change, cue@S1 (green=cued, red=changed) iter {IT}",fontsize=8)
    fig.tight_layout(rect=[0,0,1,.96]); fig.savefig(os.path.join(C.FIGS,fname),dpi=150,bbox_inches="tight"); plt.close(fig)
grid("valid","dda_prop_maps_valid.png"); grid("invalid","dda_prop_maps_invalid.png")
np.savez(os.path.join(C.FIGS,"..","summary_dda_prop_attn.npz"), props=PROPS, **{k:[r[k] for r in rows] for k in rows[0]})
for k in rows[0]: print(f"  {k}: "+" ".join(f"p{p}={rows[i][k]:.3f}" for i,p in enumerate(PROPS)))
print("saved dda_prop_attn_metrics / dda_prop_maps_valid / dda_prop_maps_invalid")
