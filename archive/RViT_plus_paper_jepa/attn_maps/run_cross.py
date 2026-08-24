"""RAW cross-attention maps for the CROSS-ATTN JEPA model (paper_jepa_crossattn_vda4, --feedback crossattn1).
Per (trial, frame): Q=W_q(X) (4 queries); K=[W_kx(X) ‖ W_kh(H)] (8 keys = 4 IMAGE patches + 4 MEMORY tokens);
scores=Q·Kᵀ/√d_token; attn=softmax(scores, dim=-1) over the 8 keys → attn[i,j]: query patch i → key j,
j∈[0..3]=image patch, j∈[4..7]=memory token (per-patch LSTM, so memory token k ↔ patch position k).
Each query ROW sums to 1 over the 8 keys (image + memory share one softmax). ONLY op = mean over trials.
Token order [S1/TL,TR,BL,S4/BR] (row-major, proven). Image keys = attn[...,:4]; memory keys = attn[...,4:]."""
import os, sys, numpy as np, torch
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env
SNAP=sys.argv[1]; OUT=_HERE
ck=torch.load(SNAP, map_location="cpu", weights_only=False)
m=RViTPaperModel(cell="xlstm",feedback="crossattn1",n_quantiles=5,seq_len=7,vae_in_channels=3,jepa_n_heads=4,jepa_proto_dim=256)
m.load_state_dict(ck["model_state_dict"]); m.eval()
TOK=["S1","TR","BL","S4"]; MAG=56.0; B=80
# verify learned + confirm (4,8) attn shape
cor=[]
for _ in range(120):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False); o=e.reset(); s=m.init_states(1); c=False
    for t in range(7):
        x=torch.from_numpy(o.astype(np.float32)).permute(2,0,1).unsqueeze(0)
        with torch.no_grad(): a=int(m.rl_step(x,s)["actor_logits"][0].argmax()); s=m.rl_step(x,s)["new_states"]
        o,rw,d,_=e.step(a)
        if d: c=(rw>0); break
    cor.append(c)
_probe=m.forward_rl_sequence(torch.randn(1,7,3,50,50), return_attn=True)["attn_seq"]
print(f"[VERIFY] iter={ck.get('iter')} greedy correct={np.mean(cor):.3f} | attn shape {tuple(_probe.shape)} (want B,7,4,8)")

def video(cue_pos, prop, color, change_true, change_idx):
    e=make_env("vda4",T=7,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=cue_pos; e.cue_color=color; e.proportion=prop
    if change_true: e.change_index=change_idx; e.orientation_change=MAG
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)

CONDS=[("cue@S1 prop1.0  NO-change",      0,1.0,0,-1),
       ("cue@S1 prop1.0  change@S1 Δ56°", 0,1.0,1, 0),
       ("cue@S1 prop1.0  change@S4 Δ56°", 0,1.0,1, 3),
       ("cue@S4 prop1.0  change@S4 Δ56°", 3,1.0,1, 3)]
A={}
for name,cue,prop,ch_t,ch_i in CONDS:
    V=torch.from_numpy(np.stack([video(cue,prop,"red",ch_t,ch_i) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): attn=m.forward_rl_sequence(V, return_attn=True)["attn_seq"].numpy()   # (B,7,4,8)
    A[name]=attn.mean(0)        # (7,4,8) raw mean
    img,mem=A[name][5,:,:4],A[name][5,:,4:]
    print(f"[{name}] f5 IMAGE-key map (query→image patch):\n{np.round(img,3)}\n  f5 MEMORY-key map (query→memory token):\n{np.round(mem,3)}")
np.savez(f"{OUT}/attn_raw_cross.npz", **{f"a__{k}":v for k,v in A.items()}, iter=int(ck.get("iter",-1)))

def make_fig(part, title, fname):
    sl=slice(0,4) if part=="image" else slice(4,8)
    vmax=max(A[k][:,:,sl].max() for k in A)
    fig,ax=plt.subplots(len(CONDS),7,figsize=(7*1.55,len(CONDS)*1.7))
    for r,(name,cue,prop,ch_t,ch_i) in enumerate(CONDS):
        for t in range(7):
            M=A[name][t,:,sl]; im=ax[r,t].imshow(M,cmap="magma",vmin=0,vmax=vmax)
            for (yy,xx),v in np.ndenumerate(M):
                ax[r,t].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5.5,color="white" if v<vmax*0.6 else "black")
            ax[r,t].set_xticks(range(4)); ax[r,t].set_yticks(range(4))
            ax[r,t].set_xticklabels(TOK,fontsize=5); ax[r,t].set_yticklabels(TOK,fontsize=5)
            if r==0: ax[r,t].set_title(f"f{t}"+(" (chg)" if t==5 else (" (cue)" if t==1 else "")),fontsize=6.5)
            if t==0: ax[r,t].set_ylabel(name,fontsize=6)
            ax[r,t].get_xticklabels()[cue].set_color("limegreen"); ax[r,t].get_xticklabels()[cue].set_fontweight("bold")
            if ch_t: ax[r,t].get_xticklabels()[ch_i].set_color("red")
    fig.suptitle(title,fontsize=8); fig.tight_layout(rect=[0,0,1,0.95]); fig.savefig(f"{OUT}/{fname}",dpi=150,bbox_inches="tight"); plt.close(fig)
    print("saved",fname)
it=ck.get('iter')
make_fig("image", f"RAW cross-attn → IMAGE keys (mean over {B}) — crossattn1 JEPA iter {it}; rows=query patch, cols=image patch [S1,TR,BL,S4]; green=cued, red=changed", "attn_cross_image.png")
make_fig("memory",f"RAW cross-attn → MEMORY keys (mean over {B}) — crossattn1 JEPA iter {it}; rows=query patch, cols=memory token [S1,TR,BL,S4]; green=cued, red=changed", "attn_cross_memory.png")
# per-query image-vs-memory total (description, not a plotted aggregation)
for name,_,_,_,_ in CONDS:
    im_tot=A[name][:,:,:4].sum(-1).mean(-1); me_tot=A[name][:,:,4:].sum(-1).mean(-1)
    print(f"[{name}] image-vs-memory total attention by frame: "+"  ".join(f"f{t}={im_tot[t]:.2f}/{me_tot[t]:.2f}" for t in range(7)))
