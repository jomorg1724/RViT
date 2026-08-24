"""Figs 5-7 analog --- FEEDBACK MECHANISM circuit + behaviour. The original compares three memory->vision
feedback mechanisms (concatenation / additive / multiplicative), each as a circuit diagram plus four
behavioural panels. Each of our papers instantiates ONE mechanism (crossattn1 = memory-as-tokens /
concatenation; affine_ew = element-wise multiplicative gating), so we render that variant's circuit and
its four panels in the same layout: A response rate vs Δ at four cue validities (cued); B behavioural
effect of enhancing vs suppressing attention on the cued change (Cue25); C cued vs uncued at 100%;
D deployment of attention (α on cued/uncued) at the change frame vs Δ.
Usage: repro_fig567.py <snap> <feedback> <label>"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro9_core as C, repro9_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
N=250; m,IT=C.load(SNAP,FB); K=S.n_keys(m); print(f"[fig567 {LAB}] iter={IT} K={K}")
DE=[0,3,6,9,12,15,18,22,26,30]; DEf=np.linspace(0,30,120); UNC=C.UNC
def curve_cued(prop):
    R=[]
    for d in DE:
        rr=[C.behavior(m,cue,prop,cue,float(d),B=N)[0] for cue in C.CUES]; R.append(np.mean(rr))
    return np.array(R)
def curve_side(prop,side):   # side: 'cued'|'uncued'
    R=[]
    for d in DE:
        rr=[]
        for cue in C.CUES:
            ci=cue if side=="cued" else UNC[cue]; rr.append(C.behavior(m,cue,prop,ci,float(d),B=N)[0])
        R.append(np.mean(rr))
    return np.array(R)
def curve_clamp(prop,cue,alpha):   # enhance/suppress cued at change; response on cued change
    R=[]
    for d in DE:
        if d==0: R.append(S.det_rate(m,cue,prop,0,-1,0.0,S.clamp_alpha(K,cue,alpha),5,B=N)); continue
        R.append(S.det_rate(m,cue,prop,1,cue,float(d),S.clamp_alpha(K,cue,alpha),5,B=N))
    return np.array(R)
VAL=[0.25,0.5,0.75,1.0]; A={p:curve_cued(p) for p in VAL}
Bc={a:curve_clamp(0.25,0,a) for a in (0.0,0.5,1.0)}
Cc={"cued":curve_side(1.0,"cued"),"uncued":curve_side(1.0,"uncued")}
# D: attention on cued vs uncued location at change frame vs Δ (uncued change)
def attn_vs_delta():
    ac=[];au=[]
    for d in DE:
        a=C.attn_maps(m,0,1.0,"red",1 if d>0 else 0,3,float(max(d,1)),B=64)   # cue S1, change at S4
        v=a[5].mean(0) if a[5].ndim>1 else a[5]                                # (K,) avg over query patches
        # location weight = image key i (+ memory key 4+i for crossattn)
        def w(i): return float(np.mean([v[k] for k in C._loc_keys(K,i)]))
        ac.append(w(0)); au.append(w(C.CUES[-1]))
    return np.array(ac),np.array(au)
aC,aU=attn_vs_delta()
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig567_{LAB}.npz"),iter=IT,DE=DE,
         **{f"A_{int(p*100)}":A[p] for p in VAL},**{f"B_{a}":Bc[a] for a in Bc},Ccued=Cc["cued"],Cuncued=Cc["uncued"],aC=aC,aU=aU)
fig=plt.figure(figsize=(15,4.2)); gs=fig.add_gridspec(1,5,width_ratios=[1.25,1,1,1,1])
# circuit diagram (variant-specific)
axd=fig.add_subplot(gs[0,0]); axd.axis("off"); axd.set_xlim(0,10); axd.set_ylim(0,10)
def bx(x,y,w,h,t,fc):
    axd.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.08",fc=fc,ec="k",lw=1.2)); axd.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=8)
if K==2*C.NP:
    bx(0.5,6.5,3,2,r"$X^{(t)}$",'#dfe8fb'); bx(0.5,1.5,3,2,r"$H^{(t-1)}$",'#f7e0c0'); bx(4.5,4,4,2.5,r"$K,V=[W_XX\,\Vert\,W_HH]$""\n"r"$Z=X+\mathrm{softmax}(QK^\top)V$",'#e9f5e9')
    axd.set_title("Memory-as-tokens (concatenation)\nfeedback circuit",fontsize=8)
else:
    bx(0.5,6.5,3,2,r"$X^{(t)}$",'#dfe8fb'); bx(0.5,1.5,3,2,r"$H^{(t-1)}$",'#f7e0c0'); bx(4.5,4,4,2.5,r"$X'=\gamma(H)\odot X+\beta(H)$""\n(multiplicative gating)",'#e9f5e9')
    axd.set_title("Element-wise multiplicative\nfeedback circuit",fontsize=8)
axd.annotate("",xy=(4.5,5.6),xytext=(3.5,7.3),arrowprops=dict(arrowstyle="-|>")); axd.annotate("",xy=(4.5,4.8),xytext=(3.5,2.6),arrowprops=dict(arrowstyle="-|>"))
axA=fig.add_subplot(gs[0,1]); col=plt.cm.viridis(np.linspace(.12,.92,4))
for i,p in enumerate(VAL):
    axA.plot(DE,A[p]*100,"o",color=col[i],ms=3); axA.plot(DEf,C.logistic4(DEf,*C.fit_logistic(DE,A[p])["popt"])*100,"-",color=col[i],lw=1.2,label=f"{int(p*100)}%")
axA.set_title("A cued, by validity",fontsize=9); axA.legend(fontsize=6); axA.set_xlabel("Δ (°)"); axA.set_ylabel("resp (%)")
axB=fig.add_subplot(gs[0,2])
for a,lb,cl in [(0.0,r"$\alpha{=}0$","tab:blue"),(0.5,"natural","0.4"),(1.0,r"$\alpha{=}1$","tab:red")]:
    axB.plot(DE,Bc[a]*100,"o-",color=cl,ms=3,label=lb)
axB.set_title("B attention modulation (Cue25)",fontsize=9); axB.legend(fontsize=6); axB.set_xlabel("Δ (°)")
axC=fig.add_subplot(gs[0,3])
axC.plot(DE,Cc["cued"]*100,"o-",label="cued",color="teal"); axC.plot(DE,Cc["uncued"]*100,"s-",label="uncued",color="tab:cyan")
axC.set_title("C cued vs uncued (100%)",fontsize=9); axC.legend(fontsize=6); axC.set_xlabel("Δ (°)")
axD=fig.add_subplot(gs[0,4]); axD.plot(DE,aC,"o-",label=r"$\alpha$ on $S_1$(cued)",color="tab:green"); axD.plot(DE,aU,"s-",label=r"$\alpha$ on $S_9$(change)",color="tab:purple")
axD.set_title("D attention deployment @change",fontsize=9); axD.legend(fontsize=6); axD.set_xlabel("Δ (°)"); axD.set_ylabel(r"$\alpha$")
fig.suptitle(f"Figs 5-7 analog --- feedback mechanism circuit & behaviour ({LAB}, iter {IT}; n={N})",fontsize=11)
fig.tight_layout(rect=[0,0,1,.95]); fig.savefig(os.path.join(C.FIGS,f"fig567_{LAB}.png"),dpi=140,bbox_inches="tight"); plt.close(fig)
print(f"saved fig567_{LAB}")
