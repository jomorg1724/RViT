"""Attention vs the 12 CUE VARIANTS (4 proportions x 3 colours) for the softmax-head model.
proportion = validity (ring completeness; also P(change at cued) in natural trials),
colour = value (red5/green3/blue1). Cue fixed at S1, no-change trials (isolate the cue response),
forced-wait. "attention received by patch j" = column j of the 4x4 RecTF attn, mean over queries+trials.
Token k == quadrant k (proven). Reports the cue-orienting score = S1 attention at the cue frame (t=1)."""
import os, sys, numpy as np, torch
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # the codebase dir (has model.py / envs/)
from model import RViTPaperModel
from envs import make_env
SNAP=sys.argv[1]; OUT=_HERE
ck=torch.load(SNAP, map_location="cpu", weights_only=False)
m=RViTPaperModel(cell="softmax_head", mem_heads=4, feedback="film", n_quantiles=5, seq_len=7)
m.load_state_dict(ck["model_state_dict"]); m.eval()
PROPS=[0.25,0.5,0.75,1.0]; COLORS=["blue","green","red"]; CVAL={"red":5,"green":3,"blue":1}
QUAD=["S1/TL","TR","BL","S4/BR"]; B=60

def video(prop,color):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    o=e.reset()
    while e.change_true!=0: o=e.reset()     # no-change → isolate the cue response
    e.cue_index=0; e.cue_color=color; e.proportion=prop
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)

rx={}                       # (prop,color) -> (7,4) attention received
for prop in PROPS:
    for color in COLORS:
        V=torch.from_numpy(np.stack([video(prop,color) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
        with torch.no_grad(): A=m.forward_rl_sequence(V, return_attn=True)["attn_seq"].numpy()  # (B,7,4,4)
        rx[(prop,color)]=A.mean(axis=(0,2))                                                       # (7,4)
# cue-orienting score = S1 received at the cue frame t=1
grid=np.array([[rx[(p,c)][1,0] for c in COLORS] for p in PROPS])   # (4 props, 3 colors)
print("S1 attention received at CUE frame (t=1), rows=proportion[0.25..1.0], cols=color[blue,green,red]:")
print(np.round(grid,3))
print("baseline S1 at t=0 (pre-cue):", round(float(np.mean([rx[k][0,0] for k in rx])),3))
np.savez(f"{OUT}/attn_cue12.npz", **{f"rx__{p}_{c}":rx[(p,c)] for p in PROPS for c in COLORS},
         grid=grid, props=PROPS, colors=COLORS, iter=int(ck.get("iter",-1)))

# ---- fig A: cue-orienting score vs validity, by value ----
fig,ax=plt.subplots(1,2,figsize=(9.5,3.6))
ccol={"red":"#d62728","green":"#2ca02c","blue":"#1f77b4"}
for ci,c in enumerate(COLORS):
    ax[0].plot(PROPS,[rx[(p,c)][1,0] for p in PROPS],"-o",color=ccol[c],label=f"{c} (val {CVAL[c]})")
ax[0].axhline(0.25,color="0.6",ls=":",lw=1); ax[0].set_xlabel("cue proportion (validity)")
ax[0].set_ylabel("S1 attention received at cue frame (t=1)"); ax[0].set_title("a  cue-orienting vs validity × value")
ax[0].legend(frameon=False,fontsize=8); ax[0].set_ylim(0,0.7)
im=ax[1].imshow(grid,cmap="magma",aspect="auto",vmin=0.25,vmax=max(0.55,grid.max()))
ax[1].set_xticks(range(3)); ax[1].set_xticklabels([f"{c}\n({CVAL[c]})" for c in COLORS])
ax[1].set_yticks(range(4)); ax[1].set_yticklabels(PROPS); ax[1].set_ylabel("proportion (validity)")
ax[1].set_title("b  S1@t=1 grid");
for (yy,xx),v in np.ndenumerate(grid): ax[1].text(xx,yy,f"{v:.2f}",ha="center",va="center",color="cyan",fontsize=8)
fig.colorbar(im,ax=ax[1],fraction=0.046)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_cue_validity_value.png",dpi=130,bbox_inches="tight"); plt.close(fig)

# ---- fig B: S1-received timecourse, all 12 variants ----
fig,ax=plt.subplots(1,3,figsize=(13,3.4),sharey=True)
for ci,c in enumerate(COLORS):
    for p in PROPS:
        a=0.35+0.65*PROPS.index(p)/3
        ax[ci].plot(range(7),[rx[(p,c)][t,0] for t in range(7)],"-o",ms=3,color=ccol[c],alpha=a,label=f"prop {p}")
    ax[ci].axvline(1,color="0.6",ls=":",lw=1); ax[ci].set_title(f"{c} (value {CVAL[c]})"); ax[ci].set_xlabel("frame")
    ax[ci].legend(frameon=False,fontsize=7)
ax[0].set_ylabel("S1 attention received"); fig.suptitle(f"Cue-orienting timecourse by validity (opacity) × value (colour) — iter {ck.get('iter')}",fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_cue_timecourse12.png",dpi=130,bbox_inches="tight"); plt.close(fig)
print("figs: fig_cue_validity_value.png, fig_cue_timecourse12.png")
