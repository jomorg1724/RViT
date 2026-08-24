"""Fig 3 (psychometrics + chronometrics) for a grid9 (9-stimulus) variant. Validities INCLUDE the new
0-proportion (uninformative cue). A: response rate vs Δ, cued change, validities {0,25,50,75,100}%.
B: 0% cued vs uncued. C: 100% cued vs uncued. D-F: RT. Prints fitted threshold per validity — a
DECREASING threshold with validity means the model USES the validity ring (the hypothesis).
Usage: repro9_fig3.py <snap> <feedback> <label>"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repro9_core as C
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
m,IT=C.load(SNAP,FB); print(f"[fig3-9 {LAB}] iter={IT}")
VAL=[0.0,0.25,0.5,0.75,1.0]; DE=[0,3,6,9,12,15,18,22,26,30]; N=300; DEf=np.linspace(0,30,120)
UNC=C.UNC
def curve(prop,chg):
    R=[];RT=[]
    for d in DE:
        rr=[];tt=[]
        for cue in C.CUES:
            ci=cue if chg=="cued" else UNC[cue]
            r,t=C.behavior(m,cue,prop,ci,float(d),B=N); rr.append(r); tt.append(t)
        R.append(np.mean(rr)); RT.append(np.nanmean(tt))
    return np.array(R),np.array(RT)
data={}
for p in VAL: data[(p,"cued")]=dict(zip(("resp","rt"),curve(p,"cued")))
for p in [0.0,1.0]: data[(p,"uncued")]=dict(zip(("resp","rt"),curve(p,"uncued")))
for v in data.values(): v["fit"]=C.fit_logistic(DE,v["resp"])
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig3_{LAB}.npz"),iter=IT,DE=DE,val=VAL,
         **{f"resp__{p}__{c}":data[(p,c)]["resp"] for p,c in data},**{f"rt__{p}__{c}":data[(p,c)]["rt"] for p,c in data},
         **{f"fit__{p}__{c}":np.array([data[(p,c)]["fit"][k] for k in("guess","lapse","slope","position")]) for p,c in data})
BLU=plt.cm.viridis(np.linspace(0.12,0.92,len(VAL)))
fig,ax=plt.subplots(2,3,figsize=(13,7))
def pan(a,items,ylab,rt=False):
    for p,c,col,lab in items:
        y=data[(p,c)]["rt" if rt else "resp"]; a.plot(DE,y*(1 if rt else 100),"o",color=col,ms=4,label=lab)
        if not rt: a.plot(DEf,C.logistic4(DEf,*data[(p,c)]["fit"]["popt"])*100,"-",color=col,lw=1.4)
    a.set_xlabel("Orientation Change Δ (°)"); a.set_ylabel(ylab); a.legend(fontsize=7)
pan(ax[0,0],[(p,"cued",BLU[i],f"{int(p*100)}%") for i,p in enumerate(VAL)],"Response Rate (%)"); ax[0,0].set_title("A  Cued changes (validities incl 0)",fontsize=10)
pan(ax[0,1],[(0.0,"cued","tab:green","cued"),(0.0,"uncued","tab:olive","uncued")],"Response Rate (%)"); ax[0,1].set_title("B  0% (uninformative) cue",fontsize=10)
pan(ax[0,2],[(1.0,"cued","teal","cued"),(1.0,"uncued","tab:cyan","uncued")],"Response Rate (%)"); ax[0,2].set_title("C  100% cue validity",fontsize=10)
pan(ax[1,0],[(p,"cued",BLU[i],f"{int(p*100)}%") for i,p in enumerate(VAL)],"Mean RT (steps)",rt=True); ax[1,0].set_title("D",fontsize=10)
pan(ax[1,1],[(0.0,"cued","tab:green","cued"),(0.0,"uncued","tab:olive","uncued")],"Mean RT (steps)",rt=True); ax[1,1].set_title("E",fontsize=10)
pan(ax[1,2],[(1.0,"cued","teal","cued"),(1.0,"uncued","tab:cyan","uncued")],"Mean RT (steps)",rt=True); ax[1,2].set_title("F",fontsize=10)
for a in ax[0]: a.set_ylim(-2,102)
fig.suptitle(f"Fig 3 — {C.TAG} (iter {IT}); validities incl 0-proportion, n={N}/point",fontsize=11)
fig.tight_layout(rect=[0,0,1,.97]); fig.savefig(os.path.join(C.FIGS,f"fig3_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
fig2,ax2=plt.subplots(1,4,figsize=(14,3))
for j,(k,lb,s) in enumerate(zip(["guess","lapse","slope","position"],["Guess(%)","Lapse(%)","Slope(1/°)","Position(°)"],[100,100,1,1])):
    ax2[j].plot([int(p*100) for p in VAL],[data[(p,"cued")]["fit"][k]*s for p in VAL],"o-",label="cued")
    ax2[j].set_xlabel("cue validity (%)"); ax2[j].set_ylabel(lb); ax2[j].legend(fontsize=6)
fig2.suptitle(f"Fig 3 fitted params — {C.TAG} (iter {IT}); Position decreasing ⇒ uses validity",fontsize=10)
fig2.tight_layout(rect=[0,0,1,.94]); fig2.savefig(os.path.join(C.FIGS,f"fig3_{LAB}_params.png"),dpi=150,bbox_inches="tight"); plt.close(fig2)
pos=[data[(p,"cued")]["fit"]["position"] for p in VAL]
print(f"[fig3-9 {LAB}] fitted THRESHOLD (°) cued by validity {['%d%%'%(p*100) for p in VAL]}: {[round(x,1) for x in pos]}")
print(f"[fig3-9 {LAB}] → validity effect (thresh drop 0%→100%): {pos[0]-pos[-1]:+.1f}°  ({'USES validity' if pos[0]-pos[-1]>2 else 'validity-INVARIANT'})")
print(f"saved fig3_{LAB} + fig3_{LAB}_params")
