"""Dedicated figure: stimulating the (uncued) change location rescues detection. On uncued-change trials
(cue at S1, change at the opposite location) the model naturally attends the cued location, AWAY from the
change; forcing attention ONTO the change location (alpha_change=1) is the largest single-manipulation
response gain. Built entirely from saved data_fig5_*.npz (natural vs stim across Δ) and data_fig14_*.npz
(graded dose-response of stimulation strength at a near-threshold Δ). No model re-run."""
import os, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
CONV="/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_conv/repro"
GRID="/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_grid9/repro9"
MODELS=[("conv crossattn1",f"{CONV}/data_fig5_crossattn1.npz",f"{CONV}/data_fig14_crossattn1.npz","a4","tab:blue"),
        ("conv affine_ew", f"{CONV}/data_fig5_affine_ew.npz", f"{CONV}/data_fig14_affine_ew.npz","a4","tab:orange"),
        ("grid9 crossattn1",f"{GRID}/data_fig5_crossattn1.npz",f"{GRID}/data_fig14_crossattn1.npz","a9","tab:green"),
        ("grid9 affine_ew", f"{GRID}/data_fig5_affine_ew.npz", f"{GRID}/data_fig14_affine_ew.npz","a9","tab:red")]
fig=plt.figure(figsize=(15,7.5)); gs=fig.add_gridspec(2,4,height_ratios=[1,1])
# ---- top row: per-model response vs Δ, natural (grey dashed) vs stimulate change location (colour), shaded gain ----
for j,(name,d5,d14,ck,col) in enumerate(MODELS):
    d=np.load(d5,allow_pickle=True); DE=np.asarray(d['DE'],float)
    nomod=d['resp__C_nomod']*100; stim=d['resp__C_'+ck]*100
    ax=fig.add_subplot(gs[0,j])
    ax.plot(DE,nomod,"o--",color="0.5",ms=3,lw=1.4,label="natural (attend cue)")
    ax.plot(DE,stim,"o-",color=col,ms=3,lw=1.8,label="stimulate change loc.")
    ax.fill_between(DE,nomod,stim,where=(stim>=nomod),color=col,alpha=.18)
    inc=(stim-nomod); k=int(np.argmax(inc))
    ax.annotate(f"+{inc[k]:.0f} pts\n@Δ={DE[k]:.0f}°",(DE[k],stim[k]),textcoords="offset points",xytext=(4,-24),fontsize=8,color=col)
    ax.set_title(name,fontsize=10); ax.set_xlabel("Δ (°)"); ax.set_ylim(-2,102); ax.grid(alpha=.25)
    if j==0: ax.set_ylabel("response rate (%)");
    ax.legend(fontsize=6,loc="upper left")
# ---- bottom-left: response INCREASE vs Δ, all models overlaid ----
axB=fig.add_subplot(gs[1,0:2])
for name,d5,d14,ck,col in MODELS:
    d=np.load(d5,allow_pickle=True); DE=np.asarray(d['DE'],float)
    inc=(d['resp__C_'+ck]-d['resp__C_nomod'])*100
    axB.plot(DE,inc,"o-",color=col,lw=1.8,ms=4,label=name)
axB.axhline(0,color="0.6",lw=.8); axB.set_xlabel("Δ (°)"); axB.set_ylabel("response increase (pts)")
axB.set_title("Gain from stimulating the (uncued) change location vs Δ",fontsize=10); axB.legend(fontsize=7); axB.grid(alpha=.25)
# ---- bottom-right: dose-response, hit rate vs stimulation bias on the change location (Δ=18, uncued) ----
# consistent sweep natural(bias 0) -> full(bias +100), matching the hard clamp used in the top row.
axC=fig.add_subplot(gs[1,2:4])
dose={"conv":np.load(f"{CONV}/data_dose_conv.npz",allow_pickle=True),
      "grid9":np.load(f"{GRID}/data_dose_grid9.npz",allow_pickle=True)}
fam={"conv crossattn1":("conv","crossattn1"),"conv affine_ew":("conv","affine_ew"),
     "grid9 crossattn1":("grid9","crossattn1"),"grid9 affine_ew":("grid9","affine_ew")}
BIAS=np.asarray(dose["conv"]["bias"],float); x=np.arange(len(BIAS))
for name,d5,d14,ck,col in MODELS:
    f,key=fam[name]; hits=np.asarray(dose[f][key],float)*100
    axC.plot(x,hits,"o-",color=col,lw=1.8,ms=4,label=name)
axC.set_xticks(x); axC.set_xticklabels([("nat." if b==0 else ("full" if b>=100 else f"{int(b)}")) for b in BIAS],fontsize=8)
axC.set_xlabel(r"stimulation on change location  (attention-logit bias: 0=natural $\to$ full clamp)")
axC.set_ylabel("hit rate (%)"); axC.set_title("Dose-response at Δ=18° (uncued change)",fontsize=10); axC.legend(fontsize=7); axC.grid(alpha=.25)
fig.suptitle("Stimulating the change location on UNCUED trials rescues detection (largest single-manipulation gain)",fontsize=12,weight="bold")
fig.tight_layout(rect=[0,0,1,.96])
for outdir in (CONV+"/figs",GRID+"/figs"):
    fig.savefig(os.path.join(outdir,"fig_uncued_stim.png"),dpi=150,bbox_inches="tight")
plt.close(fig); print("saved fig_uncued_stim.png to both figs dirs")
