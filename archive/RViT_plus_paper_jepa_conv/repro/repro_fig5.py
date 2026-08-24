"""Reproduce Fig 5 (attention manipulations) for one variant. Paper:
A-C response rate, D-F RT, for clamping α at t_change: A/D cue-S1|change-S1 @25% {no-mod, α1=1, α4=1};
B/E cue-S1|change-S1 @100% {no-mod, α1=1}; C/F cue-S1|change-S4 @100% {no-mod, α4=1, α1=0}.
G parametric α1↔α4 sweep → response-rate psychometrics; H-K fitted params vs the manipulation.
Usage: repro_fig5.py <snap> <feedback> <label>"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repro_core as C
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
m,IT=C.load(SNAP,FB); K=C.attn_maps(m,0,1.0,"red",0,-1,B=8).shape[-1]; print(f"[fig5 {LAB}] iter={IT} K={K}")
DE=[0,3,6,9,12,15,18,22,26,30]; N=200; DEf=np.linspace(0,30,120)
def sweep(prop, ci, clamp):    # response + RT over Δ
    R=[]; RT=[]
    for d in DE:
        if clamp is None: r,t=C.behavior(m,0,prop,ci,float(d),B=N)
        else: r,t=C.behavior_clamp(m,0,prop,ci,float(d),clamp,B=N)
        R.append(r); RT.append(t)
    return np.array(R),np.array(RT)
ON1,ON4,OFF1=C.clamp_on(K,0),C.clamp_on(K,3),C.clamp_off(K,0)
COND={ "A_nomod":(0.25,0,None),"A_a1":(0.25,0,ON1),"A_a4":(0.25,0,ON4),
       "B_nomod":(1.0,0,None),"B_a1":(1.0,0,ON1),
       "C_nomod":(1.0,3,None),"C_a4":(1.0,3,ON4),"C_a1off":(1.0,3,OFF1) }
D={k:dict(zip(("resp","rt"),sweep(*v))) for k,v in COND.items()}
# ---- G: parametric α1↔α4 (cue-S1 100% change-S1) ----
AL=[(1.0,0.0),(0.8,0.2),(0.6,0.4),(0.5,0.5),(0.4,0.6),(0.2,0.8),(0.1,0.9)]
G={ (a1,a4):dict(zip(("resp","rt"),sweep(1.0,0,C.clamp_graded(K,a1,a4)))) for a1,a4 in AL }
for v in list(D.values())+list(G.values()): v["fit"]=C.fit_logistic(DE,v["resp"])
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig5_{LAB}.npz"),iter=IT,DE=DE,
         **{f"resp__{k}":D[k]["resp"] for k in D},**{f"rt__{k}":D[k]["rt"] for k in D},
         AL=np.array(AL),**{f"g_resp__{i}":G[a]["resp"] for i,a in enumerate(AL)})

def pan(a,items,ylab,rt=False):
    for k,col,lab in items:
        y=D[k]["rt" if rt else "resp"]; a.plot(DE,y*(1 if rt else 100),"o",color=col,ms=4,label=lab)
        if not rt: a.plot(DEf,C.logistic4(DEf,*D[k]["fit"]["popt"])*100,"-",color=col,lw=1.3)
    a.set_xlabel("Δ (°)"); a.set_ylabel(ylab); a.legend(fontsize=6)
fig,ax=plt.subplots(2,3,figsize=(13,7))
pan(ax[0,0],[("A_nomod","gray","no-mod"),("A_a1","tab:green","α1=1"),("A_a4","tab:orange","α4=1")],"Response (%)"); ax[0,0].set_title("A cue-S1|chg-S1 25%",fontsize=9)
pan(ax[0,1],[("B_nomod","gray","no-mod"),("B_a1","tab:green","α1=1")],"Response (%)"); ax[0,1].set_title("B cue-S1|chg-S1 100%",fontsize=9)
pan(ax[0,2],[("C_nomod","gray","no-mod"),("C_a4","tab:orange","α4=1"),("C_a1off","tab:blue","α1=0")],"Response (%)"); ax[0,2].set_title("C cue-S1|chg-S4 100%",fontsize=9)
pan(ax[1,0],[("A_nomod","gray","no-mod"),("A_a1","tab:green","α1=1"),("A_a4","tab:orange","α4=1")],"RT (steps)",rt=True); ax[1,0].set_title("D",fontsize=9)
pan(ax[1,1],[("B_nomod","gray","no-mod"),("B_a1","tab:green","α1=1")],"RT (steps)",rt=True); ax[1,1].set_title("E",fontsize=9)
pan(ax[1,2],[("C_nomod","gray","no-mod"),("C_a4","tab:orange","α4=1"),("C_a1off","tab:blue","α1=0")],"RT (steps)",rt=True); ax[1,2].set_title("F",fontsize=9)
for a in ax[0]: a.set_ylim(-2,102)
fig.suptitle(f"Fig 5 A-F — {LAB}: attention clamps at t_change (conv d128 iter {IT}, n={N})",fontsize=11)
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig(os.path.join(C.FIGS,f"fig5AF_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
# ---- G + H-K ----
fig2=plt.figure(figsize=(13,4)); gs=fig2.add_gridspec(2,4)
axg=fig2.add_subplot(gs[:,0:2]); GRN=plt.cm.summer(np.linspace(0,1,len(AL)))
for i,(a1,a4) in enumerate(AL):
    axg.plot(DE,G[(a1,a4)]["resp"]*100,"o",color=GRN[i],ms=3); axg.plot(DEf,C.logistic4(DEf,*G[(a1,a4)]["fit"]["popt"])*100,"-",color=GRN[i],lw=1.2,label=f"{a1:.1f}/{a4:.1f}")
axg.set_xlabel("Δ (°)"); axg.set_ylabel("Response (%)"); axg.set_title("G  parametric α1/α4",fontsize=9); axg.legend(fontsize=5,ncol=2); axg.set_ylim(-2,102)
a1v=[a for a,_ in AL]
for j,(k,lb,s) in enumerate(zip(["guess","slope","lapse","position"],["Guess(%)","Slope(1/°)","Lapse(%)","Position(°)"],[100,1,100,1])):
    axp=fig2.add_subplot(gs[j//2,2+j%2]); axp.plot(a1v,[G[a]["fit"][k]*s for a in AL],"o-k",ms=3)
    axp.set_xlabel("α1 (α4=1-α1)"); axp.set_ylabel(lb,fontsize=7); axp.set_title("HIJK"[j],fontsize=8)
fig2.suptitle(f"Fig 5 G-K — {LAB}: parametric attention manipulation → psychometric params (iter {IT})",fontsize=10)
fig2.tight_layout(rect=[0,0,1,.94]); fig2.savefig(os.path.join(C.FIGS,f"fig5GK_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)
print(f"[fig5 {LAB}] C(uncued 100%) resp@Δ18: no-mod={D['C_nomod']['resp'][7]:.2f} α4=1={D['C_a4']['resp'][7]:.2f} α1=0={D['C_a1off']['resp'][7]:.2f}")
print(f"[fig5 {LAB}] G position(threshold) vs α1:",[round(G[a]['fit']['position'],1) for a in AL])
print(f"saved fig5AF_{LAB} + fig5GK_{LAB} + data_fig5_{LAB}.npz")
