"""RAW RecTF attention maps — CUE PROPORTION (validity) SWEEP, FiLM JEPA model.
Attention per (trial, frame): Q=W_XQ(X)⊙(1+W_HQ(H)), K=W_XK(X)⊙(1+W_HK(H)); scores=Q·Kᵀ (no 1/√d);
attn=softmax(scores, dim=-1) over the 4 KEY patches → attn[i,j] = query i → key j (row i sums to 1).
ONLY operation = mean over trials. Heat map = raw mean 4×4. Token order [S1/TL,TR,BL,S4/BR] (row-major)."""
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
TOK=["S1","TR","BL","S4"]; MAG=56.0; B=80; PROPS=[0.25,0.5,0.75,1.0]

# verify snapshot is the learned model
cor=[]
for _ in range(120):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False); o=e.reset(); s=m.init_states(1); c=False
    for t in range(7):
        x=torch.from_numpy(o.astype(np.float32)).permute(2,0,1).unsqueeze(0)
        with torch.no_grad(): a=int(m.rl_step(x,s)["actor_logits"][0].argmax()); s=m.rl_step(x,s)["new_states"]
        o,rw,d,_=e.step(a)
        if d: c=(rw>0); break
    cor.append(c)
print(f"[VERIFY] iter={ck.get('iter')} greedy correct={np.mean(cor):.3f}")

def video(cue_pos, prop, color, change_true, change_idx):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=cue_pos; e.cue_color=color; e.proportion=prop
    if change_true: e.change_index=change_idx; e.orientation_change=MAG
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)

# cue ALWAYS at S1 (token 0), colour=red, change frame t=5, |Δθ|=56°. Sweep proportion × {no-change, change@S1}.
CONDS=[(f"cue@S1 prop{p}  NO-change",      0, p, 0, -1) for p in PROPS] + \
      [(f"cue@S1 prop{p}  change@S1 Δ56°", 0, p, 1,  0) for p in PROPS]
A={}
for name, cue, prop, ch_t, ch_i in CONDS:
    V=torch.from_numpy(np.stack([video(cue,prop,"red",ch_t,ch_i) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): attn=m.forward_rl_sequence(V, return_attn=True)["attn_seq"].numpy()
    A[name]=attn.mean(0)        # (7,4,4) raw mean
# print the cue-ward attention (mean attention onto key S1, averaged over the 4 queries) per frame, by proportion
print("mean attention onto KEY S1 (col 0, averaged over 4 queries) — NO-change, by proportion & frame:")
for p in PROPS:
    a=A[f"cue@S1 prop{p}  NO-change"]; print(f"  prop {p}: "+"  ".join(f"f{t}={a[t,:,0].mean():.3f}" for t in range(7)))
np.savez(f"{OUT}/attn_raw_prop.npz", **{f"a__{k}":v for k,v in A.items()}, iter=int(ck.get("iter",-1)))

vmax=max(A[k].max() for k in A)
fig,ax=plt.subplots(len(CONDS),7,figsize=(7*1.5,len(CONDS)*1.5))
for r,(name,cue,prop,ch_t,ch_i) in enumerate(CONDS):
    for t in range(7):
        M=A[name][t]; im=ax[r,t].imshow(M,cmap="viridis",vmin=0,vmax=vmax)
        for (yy,xx),v in np.ndenumerate(M):
            ax[r,t].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5,color="white" if v<vmax*0.6 else "black")
        ax[r,t].set_xticks(range(4)); ax[r,t].set_yticks(range(4))
        ax[r,t].set_xticklabels(TOK,fontsize=4.5); ax[r,t].set_yticklabels(TOK,fontsize=4.5)
        if r==0: ax[r,t].set_title(f"frame {t}"+("\n(change)" if t==5 else ("\n(cue)" if t==1 else "")),fontsize=6)
        if t==0: ax[r,t].set_ylabel(name,fontsize=5.5)
        ax[r,t].get_xticklabels()[cue].set_color("limegreen"); ax[r,t].get_xticklabels()[cue].set_fontweight("bold")
        if ch_t: ax[r,t].get_xticklabels()[ch_i].set_color("red")
fig.suptitle(f"RAW RecTF attention (mean over {B} trials) — PROPORTION sweep, FiLM JEPA iter {ck.get('iter')}\n"
             f"cell=softmax(Q·Kᵀ)[query row→key col]; cue ALWAYS @S1 (green); top4 rows=NO-change, bottom4=change@S1 (red)",fontsize=8)
fig.tight_layout(rect=[0,0,1,0.95]); fig.savefig(f"{OUT}/attn_raw_prop.png",dpi=150,bbox_inches="tight"); plt.close(fig)
print("saved", f"{OUT}/attn_raw_prop.png")
