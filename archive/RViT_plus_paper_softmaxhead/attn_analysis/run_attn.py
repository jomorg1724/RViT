"""Attention analysis for the softmax-head (C-only) paper variant on vda4 T=7.
The attention is the RecTF (FiLM-multiplicative SA) 4x4 matrix over the 4 patch tokens,
modulated by the softmax memory C. Token k == quadrant k (row-major [TL/S1,TR,BL,BR]) — PROVEN
by a bright-quadrant probe before running this. Everything is CONTROLLED: cue fixed at S1,
colour=red, proportion=1.0; only the change condition varies. "Attention received by patch j" =
column j of the 4x4 matrix, averaged over the 4 query patches (so the 4 patch scores sum to 1)."""
import os, sys, numpy as np, torch
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE),"RViT_plus_paper_softmaxhead"))
from model import RViTPaperModel
from envs import make_env

SNAP=sys.argv[1]; OUT=_HERE; os.makedirs(OUT, exist_ok=True)
ck=torch.load(SNAP, map_location="cpu", weights_only=False)
m=RViTPaperModel(cell="softmax_head", mem_heads=4, feedback="film", n_quantiles=5, seq_len=7)
m.load_state_dict(ck["model_state_dict"]); m.eval()
QUAD=["S1 (TL, cued)","TR","BL","S4 (BR)"]; CHG=5; CUE=1   # cue/change visible frames

def gen_video(cue, change_true, change_index, color="red", prop=1.0):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=cue; e.cue_color=color; e.proportion=prop
    if change_true: e.change_index=change_index
    frames=[e._next_observation().copy()]                 # frame 0 with overrides
    for t in range(1,7): o,_,_,_=e.step(0); frames.append(o.copy())   # forced-wait
    return np.stack(frames), e.cue_index, (e.change_index if change_true else -1)

CONDS=[("cue@S1, no-change",   0, 0, 0),
       ("cue@S1, change@S1",   1, 0, 0),   # valid change (changed = cued)
       ("cue@S1, change@S4",   1, 3, 0)]   # invalid change (changed != cued)
B=80
attn_rx={}   # condition -> (T,4) attention received per patch per frame
ctrl={}
for name, ch_true, ch_idx, cue in CONDS:
    vids=[]; cues=set(); chgs=set()
    for _ in range(B):
        v,ci,gi=gen_video(cue, ch_true, ch_idx); vids.append(v); cues.add(ci); chgs.add(gi)
    V=torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0,1,4,2,3).contiguous()  # (B,7,3,50,50)
    with torch.no_grad():
        out=m.forward_rl_sequence(V, return_attn=True)
    A=out["attn_seq"].numpy()                              # (B,T,4,4) query x key
    rx=A.mean(axis=(0,2))                                  # received by key j = mean over trials & queries -> (T,4)
    attn_rx[name]=rx; ctrl[name]=(sorted(cues), sorted(chgs))
    print(f"[{name}] cue_idx={sorted(cues)} change_idx={sorted(chgs)} | S1-received/frame:", np.round(rx[:,0],3))
np.savez(f"{OUT}/attn_scores.npz", **{f"rx__{k}":v for k,v in attn_rx.items()},
         conds=[c[0] for c in CONDS], iter=int(ck.get("iter",-1)))

# ---- figure 1: attention-received timecourse (the "scores") ----
fig,ax=plt.subplots(1,3,figsize=(13,3.4),sharey=True)
col=["#d62728","#999999","#bbbbbb","#1f77b4"]
for k,(name,_,_,_) in enumerate(CONDS):
    rx=attn_rx[name]
    for j in range(4):
        ax[k].plot(range(7), rx[:,j], "-o", ms=3, color=col[j], lw=2 if j in (0,3) else 1.1,
                   label=QUAD[j] if k==0 else None)
    ax[k].axvline(CUE,color="0.6",ls=":",lw=1); ax[k].axvline(CHG,color="k",ls="--",lw=1)
    ax[k].set_title(name); ax[k].set_xlabel("frame"); ax[k].set_ylim(0,1)
ax[0].set_ylabel("attention received\n(col-mean of 4×4)"); ax[0].legend(frameon=False,fontsize=7,loc="upper left")
fig.suptitle(f"RecTF attention each patch RECEIVES — softmax-head model, iter {ck.get('iter')} (dotted=cue f1, dashed=change f5)",fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_attn_timecourse.png",dpi=130,bbox_inches="tight"); plt.close(fig)

# ---- figure 2: attention maps (2x2 grids) at key frames ----
tps=[1,4,5,6]
fig,ax=plt.subplots(len(CONDS),len(tps),figsize=(2.1*len(tps),2.1*len(CONDS)))
vmax=max(attn_rx[n].max() for n,_,_,_ in CONDS)
for r,(name,ch_true,ch_idx,cue) in enumerate(CONDS):
    for c,tp in enumerate(tps):
        grid=attn_rx[name][tp].reshape(2,2)
        im=ax[r,c].imshow(grid,cmap="magma",vmin=0,vmax=vmax)
        for (yy,xx),val in np.ndenumerate(grid): ax[r,c].text(xx,yy,f"{val:.2f}",ha="center",va="center",color="cyan",fontsize=8)
        ax[r,c].add_patch(plt.Rectangle((cue%2-0.5,cue//2-0.5),1,1,fill=False,ec="lime",lw=2))   # cued quadrant
        if ch_true: ax[r,c].add_patch(plt.Rectangle((ch_idx%2-0.5,ch_idx//2-0.5),1,1,fill=False,ec="red",lw=1.5,ls="--"))
        ax[r,c].set_xticks([]);ax[r,c].set_yticks([])
        if r==0: ax[r,c].set_title(f"frame {tp}"+("  (change)" if tp==CHG else ""),fontsize=8)
        if c==0: ax[r,c].set_ylabel(name,fontsize=8)
fig.suptitle("Attention-received maps (2×2 = TL TR / BL BR). green=cued S1, red dashed=changed patch",fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_attn_maps.png",dpi=130,bbox_inches="tight"); plt.close(fig)
# consistency self-check: map value == timecourse value (same array)
assert np.allclose(attn_rx[CONDS[1][0]][5].reshape(2,2)[0,0], attn_rx[CONDS[1][0]][5,0])
print("[consistency] map@frame5 S1 == timecourse@frame5 S1 ✓")
print("figs:", OUT)
