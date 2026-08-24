"""RAW RecTF attention maps for the FiLM JEPA model (paper_jepa_vda4).
Attention per (trial, frame): Q=W_XQ(X)⊙(1+W_HQ(H)), K=W_XK(X)⊙(1+W_HK(H)); scores=Q·Kᵀ (no 1/√d);
attn=softmax(scores, dim=-1) over the 4 KEY patches → attn[i,j] = query patch i → key patch j (row i sums to 1).
ONLY operation applied = mean over trials. Heat map = that raw mean 4×4. No other aggregation.
Token order (rows=query, cols=key) = [S1/TL, TR, BL, S4/BR] (row-major; proven by a bright-quadrant probe)."""
import os, sys, numpy as np, torch
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env

SNAP=sys.argv[1]; OUT=_HERE
ck=torch.load(SNAP, map_location="cpu", weights_only=False)
m=RViTPaperModel(cell="xlstm",feedback="film",n_quantiles=5,seq_len=7,vae_in_channels=3,jepa_n_heads=4,jepa_proto_dim=256)
m.load_state_dict(ck["model_state_dict"]); m.eval()
TOK=["S1","TR","BL","S4"]; MAG=56.0; B=80

def video(cue_pos, prop, color, change_true, change_idx):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=cue_pos; e.cue_color=color; e.proportion=prop
    if change_true:
        e.change_index=change_idx; e.orientation_change=MAG
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)

# CONDITIONS — all: colour=red, proportion=1.0, change magnitude |Δθ|=56°, change frame t=5, T=7, noise σ=5°.
CONDS=[("cue@S1 prop1.0  NO-change",         0, 1.0, 0, -1),
       ("cue@S1 prop1.0  change@S1 Δ56°",    0, 1.0, 1,  0),
       ("cue@S1 prop1.0  change@S4 Δ56°",    0, 1.0, 1,  3),
       ("cue@S4 prop1.0  change@S4 Δ56°",    3, 1.0, 1,  3)]
A={}
for name, cue, prop, ch_t, ch_i in CONDS:
    V=torch.from_numpy(np.stack([video(cue,prop,"red",ch_t,ch_i) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad():
        attn=m.forward_rl_sequence(V, return_attn=True)["attn_seq"].numpy()    # (B,7,4,4) raw softmax
    A[name]=attn.mean(0)                                                       # (7,4,4) RAW mean over trials
    print(f"[{name}]  cue_idx={cue} change_idx={ch_i}  | mean attn frame5:\n{np.round(A[name][5],3)}")
np.savez(f"{OUT}/attn_raw.npz", **{f"a__{k}":v for k,v in A.items()}, iter=int(ck.get("iter",-1)))

# ── figure: rows = conditions, cols = frames 0..6, each cell = raw mean 4×4 (query rows × key cols) ──
vmax=max(A[k].max() for k in A)
fig,ax=plt.subplots(len(CONDS),7,figsize=(7*1.55,len(CONDS)*1.7))
for r,(name,cue,prop,ch_t,ch_i) in enumerate(CONDS):
    for t in range(7):
        M=A[name][t]
        im=ax[r,t].imshow(M,cmap="viridis",vmin=0,vmax=vmax)
        for (yy,xx),v in np.ndenumerate(M):
            ax[r,t].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5.5,
                         color="white" if v<vmax*0.6 else "black")
        ax[r,t].set_xticks(range(4)); ax[r,t].set_yticks(range(4))
        ax[r,t].set_xticklabels(TOK,fontsize=5); ax[r,t].set_yticklabels(TOK,fontsize=5)
        if r==0: ax[r,t].set_title(f"frame {t}"+("\n(change)" if t==5 else ("\n(cue)" if t==1 else "")),fontsize=7)
        if t==0: ax[r,t].set_ylabel(name,fontsize=6.5)
        # mark cued key (green) and changed key (red) on the x-axis (keys)
        ax[r,t].get_xticklabels()[cue].set_color("limegreen"); ax[r,t].get_xticklabels()[cue].set_fontweight("bold")
        if ch_t: ax[r,t].get_xticklabels()[ch_i].set_color("red")
fig.suptitle(f"RAW RecTF attention (mean over {B} trials) — FiLM JEPA model, iter {ck.get('iter')}\n"
             f"each cell = softmax(Q·Kᵀ)[query row → key col]; rows/cols = patches [S1,TR,BL,S4]; "
             f"green xtick=cued key, red xtick=changed key", fontsize=8)
fig.tight_layout(rect=[0,0,1,0.95]); fig.savefig(f"{OUT}/attn_raw_maps.png",dpi=150,bbox_inches="tight"); plt.close(fig)
print("saved", f"{OUT}/attn_raw_maps.png")
