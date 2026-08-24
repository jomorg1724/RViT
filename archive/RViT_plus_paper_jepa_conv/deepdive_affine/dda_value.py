"""VALUE (cue colour) modulation of ATTENTION and RESPONSE. Colour signals reward value
(red=5, green=3, blue=1). Does a higher-value cue (a) draw stronger/earlier attention, or (b) lower the
detection threshold (the agent more eager to catch a valuable change)? Attention metrics are attention
TO a key patch (mean over queries; uniform 0.25); response is P(detect) vs magnitude per colour."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dda_core as C
SNAP=sys.argv[1]; m,IT=C.load(SNAP); COLORS=["blue","green","red"]; VAL=[1,3,5]; B=96
print(f"[dda-value] iter={IT}")
# ---- attention vs value (valid change@cued, prop1.0, avg over cue S1/S4) ----
AM={}; met={"cue_focus":[],"vlock5":[],"vlock6":[]}
for col in COLORS:
    cf=[]; l5=[]; l6=[]
    for cue in (0,3):
        A=C.attn_maps(m,cue,1.0,col,1,cue,B=B); cf.append(float(A[1,:,cue].mean())); l5.append(float(A[5,:,cue].mean())); l6.append(float(A[6,:,cue].mean()))
    met["cue_focus"].append(np.mean(cf)); met["vlock5"].append(np.mean(l5)); met["vlock6"].append(np.mean(l6))
    AM[col]=C.attn_maps(m,0,1.0,col,1,0,B=B)
# ---- response vs value: P(detect) vs magnitude per colour (valid) ----
MAGS=[8,12,16,20,28]; Bp=150
PSY={col:[np.mean([C.detect_rate(m,cue,cue,mg,1.0,color=col,B=Bp) for cue in (0,3)]) for mg in MAGS] for col in COLORS}

fig,ax=plt.subplots(1,3,figsize=(13,3.5))
ax[0].plot(VAL,met["cue_focus"],"o-",label="cue focus (f1)"); ax[0].plot(VAL,met["vlock6"],"^-",label="change-lock (f6)")
ax[0].axhline(0.25,ls=":",c="gray"); ax[0].set_xlabel("cue value (blue1 green3 red5)"); ax[0].set_ylabel("attention to cued/changed"); ax[0].set_ylim(0,1.02); ax[0].set_title("ATTENTION vs value",fontsize=9); ax[0].legend(fontsize=7)
for col in COLORS: ax[1].plot(MAGS,PSY[col],"o-",label=f"{col}({C.COLOR_VAL[col]})",c={"blue":"tab:blue","green":"tab:green","red":"tab:red"}[col])
ax[1].set_xlabel("|Δθ| (deg)"); ax[1].set_ylabel("P(detect)"); ax[1].set_ylim(-.02,1.02); ax[1].set_title("RESPONSE (psychometric) vs value",fontsize=9); ax[1].legend(fontsize=7)
# threshold (interp to P=0.5) per value
def thr(p):
    p=np.array(p)
    for i in range(len(MAGS)-1):
        if p[i]<0.5<=p[i+1]: return MAGS[i]+(0.5-p[i])/(p[i+1]-p[i])*(MAGS[i+1]-MAGS[i])
    return np.nan
ax[2].plot(VAL,[thr(PSY[c]) for c in COLORS],"o-",c="purple"); ax[2].set_xlabel("cue value"); ax[2].set_ylabel("detection threshold |Δθ| @P=0.5 (deg)"); ax[2].set_title("Threshold vs value",fontsize=9)
fig.suptitle(f"VALUE (colour) modulation of attention & response — affine_ew iter {IT}",fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dda_value.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
# maps by value
fig2,ax2=plt.subplots(len(COLORS),3,figsize=(3*1.7,len(COLORS)*1.6)); vmax=max(AM[c][f].max() for c in COLORS for f in (1,5,6))
for r,col in enumerate(COLORS):
    for c,f in enumerate((1,5,6)):
        M=AM[col][f]; ax2[r,c].imshow(M,cmap="magma",vmin=0,vmax=vmax)
        for (yy,xx),v in np.ndenumerate(M): ax2[r,c].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=6,color="white" if v<vmax*.6 else "black")
        ax2[r,c].set_xticks(range(4)); ax2[r,c].set_yticks(range(4)); ax2[r,c].set_xticklabels(C.TOK,fontsize=5); ax2[r,c].set_yticklabels(C.TOK,fontsize=5)
        if r==0: ax2[r,c].set_title(["f1 cue","f5 chg","f6 post"][c],fontsize=8)
        if c==0: ax2[r,c].set_ylabel(f"{col}({C.COLOR_VAL[col]})",fontsize=8)
fig2.suptitle(f"affine_ew A[query→key] by cue value (cue@S1 valid) iter {IT}",fontsize=8); fig2.tight_layout(rect=[0,0,1,.96])
fig2.savefig(os.path.join(C.FIGS,"dda_value_maps.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)
np.savez(os.path.join(C.FIGS,"..","summary_dda_value.npz"), vals=VAL, mags=MAGS, **met, **{f"psy__{c}":PSY[c] for c in COLORS})
print("attention vs value:",{k:[round(x,3) for x in v] for k,v in met.items()})
print("response vs value (P detect over mags):",{c:[round(x,2) for x in PSY[c]] for c in COLORS})
print("saved dda_value / dda_value_maps + summary_dda_value.npz")
