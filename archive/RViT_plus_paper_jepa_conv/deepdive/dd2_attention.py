"""dd2 — ATTENTION BATTERY: raw cross-attention maps across the 6 cue×change conditions, every frame,
with BOTH query-averaged maps (the 4 rows ARE the 4 query patches → per-query is visible) AND explicit
per-query summary stats (the cued query's own read — query-averaging dilutes it ~2×, so we report it
directly). Frame-gating, cue-frame read, and the f5 vs f6 change-lock are all surfaced with MAGNITUDES."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd_core as C
SNAP=sys.argv[1]; m,IT,ld=C.load(SNAP); B=96
print(f"[dd2] iter={IT} load(miss/unexp)={ld}")
CONDS=[("cue@S1 no-change",        0,1.0,"red",0,-1),
       ("cue@S1 change@S1 (valid)",0,1.0,"red",1, 0),
       ("cue@S1 change@S4 (inval)",0,1.0,"red",1, 3),
       ("cue@S4 no-change",        3,1.0,"red",0,-1),
       ("cue@S4 change@S4 (valid)",3,1.0,"red",1, 3),
       ("cue@S4 change@S1 (inval)",3,1.0,"red",1, 0)]
A={}
for nm,cue,prop,col,ct,ci in CONDS:
    A[nm]=C.attn_maps(m,cue,prop,col,ct,ci,B=B)            # (7,4,8)
np.savez(os.path.join(C.FIGS,"..","data_dd2.npz"), iter=IT, **{f"a__{n}":A[n] for n,*_ in CONDS})

# ---- Fig 1: frame-gating (image vs memory total), cued-query vs query-averaged ----
fig,ax=plt.subplots(1,2,figsize=(11,3.4))
for nm,cue,prop,col,ct,ci in CONDS:
    Aa=A[nm]
    img_q=Aa[:,cue,:4].sum(-1); mem_q=Aa[:,cue,4:].sum(-1)        # CUED query
    img_a=Aa[:,:,:4].sum(-1).mean(-1); mem_a=Aa[:,:,4:].sum(-1).mean(-1)  # query-avg
    ax[0].plot(range(7),img_q,marker="o",alpha=.6,label=nm if ct==0 else None)
    ax[1].plot(range(7),img_a,marker="o",alpha=.6)
for a,t in zip(ax,["CUED query: image-key total","query-averaged: image-key total"]):
    a.axvline(1,ls=":",c="g",alpha=.5); a.axvline(5,ls=":",c="r",alpha=.5); a.set_ylim(-.02,1.02)
    a.set_xlabel("frame (1=cue, 5=change)"); a.set_ylabel("Σ image-key attention"); a.set_title(t,fontsize=9)
ax[0].legend(fontsize=6,loc="center right")
fig.suptitle(f"Frame-gating of image vs memory attention — conv crossattn1 iter {IT} (memory = 1 − image)",fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dd2_framegate.png"),dpi=150,bbox_inches="tight"); plt.close(fig)

# ---- Fig 2/3: raw maps, query-avg, 7 frames × 6 conditions (rows of each 4×4 = the 4 query patches) ----
def maps_fig(part,fname,title):
    sl=slice(0,4) if part=="image" else slice(4,8); vmax=max(A[n][:,:,sl].max() for n,*_ in CONDS)
    fig,ax=plt.subplots(len(CONDS),7,figsize=(7*1.5,len(CONDS)*1.55))
    for r,(nm,cue,prop,col,ct,ci) in enumerate(CONDS):
        for t in range(7):
            M=A[nm][t,:,sl]; ax[r,t].imshow(M,cmap="magma",vmin=0,vmax=vmax)
            for (yy,xx),v in np.ndenumerate(M): ax[r,t].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5,color="white" if v<vmax*.6 else "black")
            ax[r,t].set_xticks(range(4)); ax[r,t].set_yticks(range(4)); ax[r,t].set_xticklabels(C.TOK,fontsize=4.5); ax[r,t].set_yticklabels(C.TOK,fontsize=4.5)
            if r==0: ax[r,t].set_title(f"f{t}"+(" cue" if t==1 else (" chg" if t==5 else (" post" if t==6 else ""))),fontsize=6.5)
            if t==0: ax[r,t].set_ylabel(nm,fontsize=5.5)
            ax[r,t].get_xticklabels()[cue].set_color("limegreen"); ax[r,t].get_xticklabels()[cue].set_fontweight("bold")
            if ct: ax[r,t].get_xticklabels()[ci].set_color("red")
    fig.suptitle(title,fontsize=9); fig.tight_layout(rect=[0,0,1,.97]); fig.savefig(os.path.join(C.FIGS,fname),dpi=150,bbox_inches="tight"); plt.close(fig)
maps_fig("image","dd2_maps_image.png",f"RAW cross-attn → IMAGE keys (mean/{B}); rows=query patch, cols=image patch [S1,TR,BL,S4]; green=cued red=changed — iter {IT}")
maps_fig("memory","dd2_maps_memory.png",f"RAW cross-attn → MEMORY keys (mean/{B}); rows=query patch, cols=memory token [S1,TR,BL,S4]; green=cued red=changed — iter {IT}")

# ---- per-query SUMMARY stats (the load-bearing numbers, NOT query-averaged) ----
def peak(v): return float(v.max())
print("\n[CUE-FRAME f1 read] cued-query own row:")
S={}
for nm,cue,prop,col,ct,ci in CONDS:
    row=A[nm][1,cue]; S[nm]={"f1_cue_img_self":float(row[cue]),"f1_cue_mem_self":float(row[4+cue]),
                              "f1_img_to_cued_meanNonCued":float(np.mean([A[nm][1,q,cue] for q in range(4) if q!=cue]))}
    print(f"  {nm}: cued-query IMG_self={row[cue]:.2f} MEM_self={row[4+cue]:.2f}; non-cued queries→cued IMG patch={S[nm]['f1_img_to_cued_meanNonCued']:.2f}")
print("\n[CHANGE-LOCK] memory excess on the CHANGED token over uniform, per query, f5 & f6:")
for nm,cue,prop,col,ct,ci in CONDS:
    if not ct: continue
    for f in [5,6]:
        mem=A[nm][f,:,4:]; unif=mem.sum(1,keepdims=True)/4; exc=mem[:,ci]-unif[:,0]
        S.setdefault(nm,{})[f"f{f}_chg_excess_max"]=float(exc.max())
        print(f"  {nm} f{f}: excess on changed token {ci} per query=[{','.join(f'{v:+.3f}' for v in exc)}] (max {exc.max():+.3f})")
np.savez(os.path.join(C.FIGS,"..","summary_dd2.npz"), **{f"{k}__{kk}":vv for k,d in S.items() for kk,vv in d.items()})
print("\nsaved dd2_framegate / dd2_maps_image / dd2_maps_memory + data_dd2.npz + summary_dd2.npz")
