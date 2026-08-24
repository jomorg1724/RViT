"""Fig 14 reproduction --- RL value & TD-error signatures. From the distributional critic we read the
scalar value V(t) along the (open-loop) trajectory; the value-based TD surprise at the change frame is
δ = γ·V(6) − V(5) (reward is 0 under forced-wait rollout, so δ isolates the value jump at change onset).
A: δ@change vs Δ, cued (S1) vs uncued (S9) change.  B: V@change vs Δ.  C: δ@change vs enhancing
attention α4 on the uncued change.  D: hit rate vs α4.  Usage: repro_fig14.py <snap> <fb> <lab> [gamma]"""
import os,sys,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import repro9_core as C, repro9_supp as S
SNAP,FB,LAB=sys.argv[1],sys.argv[2],sys.argv[3]
GAMMA=float(sys.argv[4]) if len(sys.argv)>4 else 0.99
N=600; m,IT=C.load(SNAP,FB); K=S.n_keys(m); print(f"[fig14 {LAB}] iter={IT} K={K} γ={GAMMA}")
DE=[0,3,6,9,12,15,18,22,26,30]
def vd_curve(loc):
    dV=[];VV=[]
    for d in DE:
        if d==0: V=C._tens([C.make_video(0,1.0,"red",0,-1,0.0) for _ in range(N)])
        else:    V=C._tens([C.make_video(0,1.0,"red",1,loc,float(d)) for _ in range(N)])
        r=S.rollout(m,V); v5=r["Vsc"][:,5]; v6=r["Vsc"][:,6]
        dV.append(float(np.mean(GAMMA*v6-v5))); VV.append(float(np.mean(v5)))
    return np.array(dV),np.array(VV)
dS1,vS1=vd_curve(0); dS4,vS4=vd_curve(8)
# C,D: sweep α4 (enhance uncued change at S4), fixed Δ
A4=[0.0,0.25,0.5,0.75,1.0]; MAG=18.0; dA=[];hA=[]
for a in A4:
    cl=S.clamp_alpha(K,8,a); V=C._tens([C.make_video(0,1.0,"red",1,8,MAG) for _ in range(N)])
    r=S.rollout(m,V,clamp=cl,clamp_from=5); dA.append(float(np.mean(GAMMA*r["Vsc"][:,6]-r["Vsc"][:,5])))
    hA.append(S.det_rate(m,0,1.0,1,3,MAG,cl,5,B=N))
np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"data_fig14_{LAB}.npz"),iter=IT,DE=DE,
         dS1=dS1,vS1=vS1,dS4=dS4,vS4=vS4,A4=A4,dA=dA,hA=hA,gamma=GAMMA)
fig,ax=plt.subplots(2,2,figsize=(11,8))
ax[0,0].plot(DE,dS1,"o-",label="cued change (S1)"); ax[0,0].plot(DE,dS4,"s-",label="uncued change (S9)")
ax[0,0].set_title("A  TD surprise δ at change vs Δ"); ax[0,0].set_xlabel("Δ (°)"); ax[0,0].set_ylabel(r"$\delta=\gamma V_6-V_5$"); ax[0,0].legend(fontsize=8)
ax[0,1].plot(DE,vS1,"o-",label="cued (S1)"); ax[0,1].plot(DE,vS4,"s-",label="uncued (S9)")
ax[0,1].set_title("B  value V at change vs Δ"); ax[0,1].set_xlabel("Δ (°)"); ax[0,1].set_ylabel(r"$V_5$"); ax[0,1].legend(fontsize=8)
ax[1,0].plot(A4,dA,"o-",color="tab:purple"); ax[1,0].set_title(r"C  δ vs enhancing $\alpha_4$ (uncued change, Δ=18°)")
ax[1,0].set_xlabel(r"$\alpha_4$"); ax[1,0].set_ylabel(r"$\delta$")
ax[1,1].plot(A4,np.array(hA)*100,"o-",color="tab:red"); ax[1,1].set_title(r"D  hit rate vs $\alpha_4$ (uncued, Δ=18°)")
ax[1,1].set_xlabel(r"$\alpha_4$"); ax[1,1].set_ylabel("hit rate (%)")
for a in ax.flat: a.grid(alpha=.25)
fig.suptitle(f"Fig 14 --- TD error & value under change magnitude and attention ({LAB}, iter {IT})",fontsize=11)
fig.tight_layout(rect=[0,0,1,.96]); fig.savefig(os.path.join(C.FIGS,f"fig14_{LAB}.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print(f"[fig14 {LAB}] δ_S1={[round(x,3) for x in dS1]}"); print(f"saved fig14_{LAB}")
