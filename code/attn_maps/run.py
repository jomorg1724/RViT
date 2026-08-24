"""RAW cross-attention maps — NO-VAE + FRAME-REPEAT×5 cross-attn JEPA model (paper_jepa_cross_novae_fr).
Attention per (trial, physical step): Q=W_q(X) (4 queries); K=[W_kx(X)‖W_kh(H)] (8 keys=4 IMAGE + 4 MEMORY);
scores=Q·Kᵀ/√d; attn=softmax over 8 keys → attn[i,j]: query i → key j (j∈0..3 image patch, 4..7 memory token).
Each query ROW sums to 1. ONLY op = mean over trials. Token order [S1/TL,TR,BL,S4/BR] (row-major, proven).
Frame-repeat: 35 physical steps = 7 logical × 5; change at LOGICAL frame 5 = physical 25. The figure shows the
LAST physical step of each logical frame (steps 4,9,14,19,24,29,34) — a SELECTION (not an average); all 35 steps
are saved raw in the npz."""
import os, sys, numpy as np, torch
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env
SNAP=sys.argv[1]; OUT=_HERE; FR=5
ck=torch.load(SNAP, map_location="cpu", weights_only=False)
m=RViTPaperModel(cell="xlstm",feedback="crossattn1",n_quantiles=5,seq_len=35,vae_in_channels=3,
                 jepa_n_heads=4,jepa_proto_dim=256,frame_repeat=FR)
r=m.load_state_dict(ck["model_state_dict"],strict=False); m.eval()
TOK=["S1","TR","BL","S4"]; MAG=56.0; B=64
LOGREP=[L*FR+(FR-1) for L in range(7)]   # last physical step of each logical frame: 4,9,14,19,24,29,34

# verify learned + attn shape + alignment
cor=[]
for _ in range(100):
    e=make_env("vda4",T=7,frame_repeat=FR,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False); o=e.reset(); s=m.init_states(1); c=False
    for t in range(35):
        x=torch.from_numpy(o.astype(np.float32)).permute(2,0,1).unsqueeze(0)
        with torch.no_grad(): a=int(m.rl_step(x,s)["actor_logits"][0].argmax()); s=m.rl_step(x,s)["new_states"]
        o,rw,d,_=e.step(a)
        if d: c=(rw>0); break
    cor.append(c)
_p=m.forward_rl_sequence(torch.randn(1,35,3,50,50),return_attn=True)["attn_seq"]
print(f"[VERIFY] iter={ck.get('iter')} load m/u={len(r.missing_keys)}/{len(r.unexpected_keys)} greedy correct={np.mean(cor):.3f} | attn {tuple(_p.shape)} (want B,35,4,8)")
for qi,(r0,r1,c0,c1),nm in [(0,(0,25,0,25),"TL/S1"),(3,(25,50,25,50),"BR/S4")]:
    img=np.zeros((50,50,3),np.float32); img[r0:r1,c0:c1]=1.0
    with torch.no_grad(): d=(m.front(m._to_bchw(torch.from_numpy(img).permute(2,0,1).unsqueeze(0)),0)-m.front(m._to_bchw(torch.zeros(1,3,50,50)),0)).abs().sum(-1)[0]
    print(f"[ALIGN] bright {nm} → token {int(d.argmax())}")

def video(cue_pos, prop, color, change_true, change_idx):
    e=make_env("vda4",T=7,frame_repeat=FR,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
    o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=cue_pos; e.cue_color=color; e.proportion=prop
    if change_true: e.change_index=change_idx; e.orientation_change=MAG
    fr=[e._next_observation().copy()]
    for t in range(34): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)

CONDS=[("cue@S1 prop1.0 NO-change",      0,1.0,0,-1),
       ("cue@S1 prop1.0 change@S1 Δ56°", 0,1.0,1, 0),
       ("cue@S1 prop1.0 change@S4 Δ56°", 0,1.0,1, 3),
       ("cue@S4 prop1.0 change@S4 Δ56°", 3,1.0,1, 3)]
A={}
for name,cue,prop,ch_t,ch_i in CONDS:
    V=torch.from_numpy(np.stack([video(cue,prop,"red",ch_t,ch_i) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): attn=m.forward_rl_sequence(V, return_attn=True)["attn_seq"].numpy()  # (B,35,4,8)
    A[name]=attn.mean(0)        # (35,4,8) raw mean — ALL physical steps
    L5=A[name][LOGREP[5]]; print(f"[{name}] logical-frame 5 (phys {LOGREP[5]}, change) IMAGE-keys:\n{np.round(L5[:,:4],3)}\n  MEMORY-keys:\n{np.round(L5[:,4:],3)}")
np.savez(f"{OUT}/attn_raw_novae_fr.npz", **{f"a__{k}":v for k,v in A.items()}, iter=int(ck.get("iter",-1)), logrep=LOGREP)

def make_fig(part, fname, title):
    sl=slice(0,4) if part=="image" else slice(4,8)
    vmax=max(A[k][:,:,sl].max() for k in A)
    fig,ax=plt.subplots(len(CONDS),7,figsize=(7*1.55,len(CONDS)*1.7))
    for rr,(name,cue,prop,ch_t,ch_i) in enumerate(CONDS):
        for L in range(7):
            M=A[name][LOGREP[L],:,sl]; im=ax[rr,L].imshow(M,cmap="magma",vmin=0,vmax=vmax)
            for (yy,xx),v in np.ndenumerate(M): ax[rr,L].text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=5.5,color="white" if v<vmax*0.6 else "black")
            ax[rr,L].set_xticks(range(4)); ax[rr,L].set_yticks(range(4)); ax[rr,L].set_xticklabels(TOK,fontsize=5); ax[rr,L].set_yticklabels(TOK,fontsize=5)
            if rr==0: ax[rr,L].set_title(f"L{L}"+(" (chg)" if L==5 else (" (cue)" if L==1 else "")),fontsize=7)
            if L==0: ax[rr,L].set_ylabel(name,fontsize=6)
            ax[rr,L].get_xticklabels()[cue].set_color("limegreen"); ax[rr,L].get_xticklabels()[cue].set_fontweight("bold")
            if ch_t: ax[rr,L].get_xticklabels()[ch_i].set_color("red")
    fig.suptitle(title,fontsize=8); fig.tight_layout(rect=[0,0,1,0.95]); fig.savefig(f"{OUT}/{fname}",dpi=150,bbox_inches="tight"); plt.close(fig); print("saved",fname)
it=ck.get('iter')
make_fig("image", "attn_novaefr_image.png",  f"RAW cross-attn → IMAGE keys (mean/{B}) NO-VAE+FR×5 crossattn1 iter {it}; cols=logical frame (last phys step); rows=query, cols=image patch; green=cued red=changed")
make_fig("memory","attn_novaefr_memory.png", f"RAW cross-attn → MEMORY keys (mean/{B}) NO-VAE+FR×5 crossattn1 iter {it}; cols=logical frame; rows=query, cols=memory token; green=cued red=changed")
for name,_,_,_,_ in CONDS:
    im=A[name][:,:,:4].sum(-1).mean(-1); me=A[name][:,:,4:].sum(-1).mean(-1)
    print(f"[{name}] image/memory total by logical frame: "+"  ".join(f"L{L}={im[LOGREP[L]]:.2f}/{me[LOGREP[L]]:.2f}" for L in range(7)))
