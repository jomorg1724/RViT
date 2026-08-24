"""RAW cross-attention maps — CONV front-end + crossattn1 JEPA, plain 7-step vda4 (paper_jepa_conv_d128).
Per (trial, frame): Q=W_q(X) (4 queries); K=[W_kx(X) ‖ W_kh(H)] (8 keys = 4 IMAGE patches + 4 MEMORY tokens);
scores=Q·Kᵀ/√d_token; attn=softmax(scores, dim=-1) over the 8 keys → attn[i,j]: query patch i → key j,
j∈[0..3]=image patch, j∈[4..7]=memory token (per-patch LSTM, memory token k ↔ patch k). Each query ROW
sums to 1 over the 8 keys. ONLY op = mean over trials. Token order [S1/TL,TR,BL,S4/BR] (row-major, proven).
Front-end is the trained SE-ResNet conv (not VAE). 7-step task: cue@frame1, change@frame5, frame_repeat=1."""
import os, sys, numpy as np, torch
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env
SNAP=sys.argv[1]; OUT=_HERE
ck=torch.load(SNAP, map_location="cpu", weights_only=False)
m=RViTPaperModel(cell="xlstm",feedback="crossattn1",n_quantiles=5,seq_len=7,jepa_n_heads=4,jepa_proto_dim=256,
                 frame_repeat=1,d_mem=128,conv_frontend=True)
r=m.load_state_dict(ck["model_state_dict"],strict=False); m.eval()
TOK=["S1","TR","BL","S4"]; MAG=56.0; B=80
# verify learned + confirm (4,8) attn shape + token↔quadrant alignment (conv front-end)
cor=[]
for _ in range(120):
    e=make_env("vda4",T=7,frame_repeat=1,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False); o=e.reset(); s=m.init_states(1); c=False
    for t in range(7):
        x=torch.from_numpy(o.astype(np.float32)).permute(2,0,1).unsqueeze(0)
        with torch.no_grad(): a=int(m.rl_step(x,s)["actor_logits"][0].argmax()); s=m.rl_step(x,s)["new_states"]
        o,rw,d,_=e.step(a)
        if d: c=(rw>0); break
    cor.append(c)
_p=m.forward_rl_sequence(torch.randn(1,7,3,50,50),return_attn=True)["attn_seq"]
print(f"[VERIFY] iter={ck.get('iter')} load m/u={len(r.missing_keys)}/{len(r.unexpected_keys)} greedy correct={np.mean(cor):.3f} | attn {tuple(_p.shape)} (want B,7,4,8)")
base=m.front(m._to_bchw(torch.zeros(1,3,50,50)),0)[0,:,:128]
for qi,(r0,r1,c0,c1),nm in [(0,(0,25,0,25),"TL/S1"),(1,(0,25,25,50),"TR"),(2,(25,50,0,25),"BL"),(3,(25,50,25,50),"BR/S4")]:
    img=np.zeros((50,50,3),np.float32); img[r0:r1,c0:c1]=1.0
    with torch.no_grad(): d=(m.front(m._to_bchw(torch.from_numpy(img).permute(2,0,1).unsqueeze(0)),0)[0,:,:128]-base).abs().sum(-1)
    print(f"[ALIGN] bright {nm} → token {int(d.argmax())} (want {qi})")

def video(cue_pos, prop, color, change_true, change_idx):
    e=make_env("vda4",T=7,frame_repeat=1,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=cue_pos; e.cue_color=color; e.proportion=prop
    if change_true: e.change_index=change_idx; e.orientation_change=MAG
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)

CONDS=[("cue@S1 prop1.0  NO-change",      0,1.0,0,-1),
       ("cue@S1 prop1.0  change@S1 Δ56°", 0,1.0,1, 0),
       ("cue@S1 prop1.0  change@S4 Δ56°", 0,1.0,1, 3),   # cue≠change → dissociates cue-lock vs change-lock
       ("cue@S4 prop1.0  NO-change",      3,1.0,0,-1),
       ("cue@S4 prop1.0  change@S4 Δ56°", 3,1.0,1, 3),
       ("cue@S4 prop1.0  change@S1 Δ56°", 3,1.0,1, 0)]   # cue≠change (other side) → symmetric dissociation
A={}
for name,cue,prop,ch_t,ch_i in CONDS:
    V=torch.from_numpy(np.stack([video(cue,prop,"red",ch_t,ch_i) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): attn=m.forward_rl_sequence(V, return_attn=True)["attn_seq"].numpy()   # (B,7,4,8)
    A[name]=attn.mean(0)        # (7,4,8) raw mean
    # per-frame MEMORY-peak token for each query (surfaces the change-lock: peak re-points to the
    # CHANGED memory token one frame AFTER the change, i.e. at f6, when cue≠change)
    peaks=[A[name][t,:,4:].argmax(1).tolist() for t in range(7)]
    print(f"[{name}] cued={cue} chg={ch_i} | memory-peak token/query by frame: "
          + "  ".join(f"f{t}={peaks[t]}" for t in range(7)))
    print(f"  f5 MEMORY-keys:\n{np.round(A[name][5,:,4:],3)}\n  f6 MEMORY-keys:\n{np.round(A[name][6,:,4:],3)}")
np.savez(f"{OUT}/attn_raw_conv.npz", **{f"a__{k}":v for k,v in A.items()}, iter=int(ck.get("iter",-1)))

def make_fig(part, title, fname):
    sl=slice(0,4) if part=="image" else slice(4,8)
    vmax=max(A[k][:,:,sl].max() for k in A)
    fig,ax=plt.subplots(len(CONDS),7,figsize=(7*1.55,len(CONDS)*1.7))
    for rr,(name,cue,prop,ch_t,ch_i) in enumerate(CONDS):
        for t in range(7):
            M=A[name][t,:,sl]; im=ax[rr,t].imshow(M,cmap="magma",vmin=0,vmax=vmax)
            for (yy,xx),v in np.ndenumerate(M):
                ax[rr,t].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5.5,color="white" if v<vmax*0.6 else "black")
            ax[rr,t].set_xticks(range(4)); ax[rr,t].set_yticks(range(4))
            ax[rr,t].set_xticklabels(TOK,fontsize=5); ax[rr,t].set_yticklabels(TOK,fontsize=5)
            if rr==0: ax[rr,t].set_title(f"f{t}"+(" (chg)" if t==5 else (" (cue)" if t==1 else "")),fontsize=6.5)
            if t==0: ax[rr,t].set_ylabel(name,fontsize=6)
            ax[rr,t].get_xticklabels()[cue].set_color("limegreen"); ax[rr,t].get_xticklabels()[cue].set_fontweight("bold")
            if ch_t: ax[rr,t].get_xticklabels()[ch_i].set_color("red")
    fig.suptitle(title,fontsize=8); fig.tight_layout(rect=[0,0,1,0.95]); fig.savefig(f"{OUT}/{fname}",dpi=150,bbox_inches="tight"); plt.close(fig)
    print("saved",fname)
it=ck.get('iter')
make_fig("image", f"RAW cross-attn → IMAGE keys (mean/{B}) — CONV front-end crossattn1 JEPA iter {it}; rows=query patch, cols=image patch [S1,TR,BL,S4]; green=cued, red=changed", "attn_conv_image.png")
make_fig("memory",f"RAW cross-attn → MEMORY keys (mean/{B}) — CONV front-end crossattn1 JEPA iter {it}; rows=query patch, cols=memory token [S1,TR,BL,S4]; green=cued, red=changed", "attn_conv_memory.png")
for name,_,_,_,_ in CONDS:
    im=A[name][:,:,:4].sum(-1).mean(-1); me=A[name][:,:,4:].sum(-1).mean(-1)
    print(f"[{name}] image/memory total by frame: "+"  ".join(f"f{t}={im[t]:.2f}/{me[t]:.2f}" for t in range(7)))
