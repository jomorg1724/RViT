"""dd3 — VALIDITY (cue proportion) and VALUE (cue colour) sweeps, and their effect on attention at
BOTH cue time (f1) and change time (f5,f6). Produces (a) raw maps at each proportion/colour and
(b) summary-metric-vs-proportion / vs-value line plots. Metrics are per-query (cued/non-cued), not
query-averaged. Also checks the load(unexpected) key to confirm it is a benign buffer."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd_core as C
SNAP=sys.argv[1]; m,IT,ld=C.load(SNAP); B=96
# confirm the 1 unexpected key is benign
ck=torch.load(SNAP,map_location="cpu",weights_only=False)
msd=set(ck["model_state_dict"]); cur=set(dict(m.state_dict()))
print(f"[dd3] iter={IT} load={ld} | checkpoint-only keys = {sorted(msd-cur)} (should be a stale buffer, not a weight)")

def metrics(cue, prop, color, ct, ci, mag=56.0):
    A=C.attn_maps(m,cue,prop,color,ct,ci,mag,B=B)            # (7,4,8)
    nonc=[q for q in range(4) if q!=cue]
    cue_read=float(np.mean([A[1,q,cue] for q in nonc]))      # f1: non-cued queries → cued IMAGE patch
    img_tot=lambda f: float(A[f,:,:4].sum(-1).mean())
    def chg_exc(f):
        if not ct: return 0.0
        mem=A[f,:,4:]; return float((mem[:,ci]-mem.sum(1)/4).max())
    return dict(A=A, cue_read=cue_read, img_f1=img_tot(1), img_f5=img_tot(5),
                chg_f5=chg_exc(5), chg_f6=chg_exc(6))

PROPS=[0.25,0.5,0.75,1.0]; COLORS=["blue","green","red"]  # value 1,3,5
# ---- PROPORTION sweep (cue@S1 red; valid change@S1) ----
PM={p:metrics(0,p,"red",1,0) for p in PROPS}
fig,ax=plt.subplots(1,2,figsize=(10,3.4))
ax[0].plot(PROPS,[PM[p]["cue_read"] for p in PROPS],"o-",label="cue-frame read (non-cued→cued image, f1)")
ax[0].set_xlabel("cue proportion (validity)"); ax[0].set_ylabel("attention"); ax[0].set_ylim(0,1.05); ax[0].set_title("CUE-TIME read vs validity",fontsize=9); ax[0].legend(fontsize=7)
ax[1].plot(PROPS,[PM[p]["chg_f5"] for p in PROPS],"s-",label="change-lock @ f5 (valid)")
ax[1].plot(PROPS,[PM[p]["chg_f6"] for p in PROPS],"^-",label="change-lock @ f6 (valid)")
ax[1].set_xlabel("cue proportion (validity)"); ax[1].set_ylabel("memory excess on changed token"); ax[1].set_title("CHANGE-TIME lock vs validity",fontsize=9); ax[1].legend(fontsize=7)
fig.suptitle(f"Cue VALIDITY (proportion) effect on attention — conv crossattn1 iter {IT}",fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dd3_proportion_metrics.png"),dpi=150,bbox_inches="tight"); plt.close(fig)

# ---- COLOUR (value) sweep (cue@S1 prop1.0; valid change@S1) ----
CM={c:metrics(0,1.0,c,1,0) for c in COLORS}
vals=[C.COLOR_VAL[c] for c in COLORS]
fig,ax=plt.subplots(1,2,figsize=(10,3.4))
ax[0].plot(vals,[CM[c]["cue_read"] for c in COLORS],"o-")
ax[0].set_xlabel("cue value (blue1 green3 red5)"); ax[0].set_ylabel("attention"); ax[0].set_ylim(0,1.05); ax[0].set_title("CUE-TIME read vs value",fontsize=9)
ax[1].plot(vals,[CM[c]["chg_f5"] for c in COLORS],"s-",label="lock @ f5"); ax[1].plot(vals,[CM[c]["chg_f6"] for c in COLORS],"^-",label="lock @ f6")
ax[1].set_xlabel("cue value (blue1 green3 red5)"); ax[1].set_ylabel("memory excess on changed token"); ax[1].set_title("CHANGE-TIME lock vs value",fontsize=9); ax[1].legend(fontsize=7)
fig.suptitle(f"Cue VALUE (colour) effect on attention — conv crossattn1 iter {IT}",fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dd3_colour_metrics.png"),dpi=150,bbox_inches="tight"); plt.close(fig)

# ---- raw maps at each proportion (memory keys, f1/f5/f6) so the structure is visible, not just metrics ----
def sweep_maps(items, getA, labels, fname, title):
    fig,ax=plt.subplots(len(items),3,figsize=(3*1.6,len(items)*1.55))
    vmax=max(getA(it)[f,:,4:].max() for it in items for f in [1,5,6])
    for r,it in enumerate(items):
        A=getA(it)
        for c,f in enumerate([1,5,6]):
            M=A[f,:,4:]; ax[r,c].imshow(M,cmap="magma",vmin=0,vmax=vmax)
            for (yy,xx),v in np.ndenumerate(M): ax[r,c].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5,color="white" if v<vmax*.6 else "black")
            ax[r,c].set_xticks(range(4)); ax[r,c].set_yticks(range(4)); ax[r,c].set_xticklabels(C.TOK,fontsize=4.5); ax[r,c].set_yticklabels(C.TOK,fontsize=4.5)
            if r==0: ax[r,c].set_title(["f1 cue","f5 chg","f6 post"][c],fontsize=7)
            if c==0: ax[r,c].set_ylabel(labels[r],fontsize=6)
    fig.suptitle(title,fontsize=8); fig.tight_layout(rect=[0,0,1,.96]); fig.savefig(os.path.join(C.FIGS,fname),dpi=150,bbox_inches="tight"); plt.close(fig)
sweep_maps(PROPS,lambda p:PM[p]["A"],[f"prop {p}" for p in PROPS],"dd3_proportion_maps.png",f"MEMORY-key maps by validity (cue@S1 valid change) — iter {IT}")
sweep_maps(COLORS,lambda c:CM[c]["A"],[f"{c}({C.COLOR_VAL[c]})" for c in COLORS],"dd3_colour_maps.png",f"MEMORY-key maps by value (cue@S1 valid change) — iter {IT}")

np.savez(os.path.join(C.FIGS,"..","summary_dd3.npz"),
         props=PROPS, prop_cue_read=[PM[p]["cue_read"] for p in PROPS], prop_chg_f5=[PM[p]["chg_f5"] for p in PROPS],
         prop_chg_f6=[PM[p]["chg_f6"] for p in PROPS], colors=COLORS, col_vals=vals,
         col_cue_read=[CM[c]["cue_read"] for c in COLORS], col_chg_f5=[CM[c]["chg_f5"] for c in COLORS], col_chg_f6=[CM[c]["chg_f6"] for c in COLORS])
print("PROP cue_read:",[round(PM[p]["cue_read"],3) for p in PROPS]," chg_f5:",[round(PM[p]["chg_f5"],3) for p in PROPS]," chg_f6:",[round(PM[p]["chg_f6"],3) for p in PROPS])
print("COLR cue_read:",[round(CM[c]["cue_read"],3) for c in COLORS]," chg_f5:",[round(CM[c]["chg_f5"],3) for c in COLORS]," chg_f6:",[round(CM[c]["chg_f6"],3) for c in COLORS])
print("saved dd3_* figs + summary_dd3.npz")
