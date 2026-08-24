"""Grid9 attention maps (9-stimulus / 3x3 / 75x75 vda9), for crossattn1 (9 query × 18 keys: 9 image + 9
memory) OR affine_ew (9 query × 9 keys). Self-contained. Applies all lessons: per-query, magnitudes,
every frame (cue f1, change f5, post f6), dissociation BOTH cue corners, and EXERCISES validity (changes
at cued AND uncued). Features the NEW proportion 0.0 (uninformative cue, no ring) vs 1.0.
Usage: dd9_attn.py <snap> <feedback>   (feedback = crossattn1 | affine_ew)"""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env
SNAP=sys.argv[1]; FB=sys.argv[2]; FIGS=os.path.join(_HERE,"figs"); os.makedirs(FIGS,exist_ok=True); B=64
TOK=[f"P{i}" for i in range(9)]   # row-major: P0=TL P2=TR P6=BL P8=BR P4=center
# load (auto-match out_norm)
ck=torch.load(SNAP,map_location="cpu",weights_only=False); sd=ck["model_state_dict"]
m=RViTPaperModel(cell="xlstm",feedback=FB,n_quantiles=5,seq_len=7,jepa_n_heads=4,jepa_proto_dim=256,
                 frame_repeat=1,d_mem=128,conv_frontend=True,grid_rows=3,grid_cols=3,image_size=75)
if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm,nn.LayerNorm): m.front.out_norm=nn.LayerNorm(128)
r=m.load_state_dict(sd,strict=False); m.eval()
assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys,r.unexpected_keys)
def mkvid(cue,prop,color,ct,ci,mag=56.0):
    e=make_env("vda9"); o=e.reset()
    while e.change_true!=ct: o=e.reset()
    e.cue_index=cue; e.cue_color=color; e.proportion=prop
    if ct: e.change_index=ci; e.orientation_change=mag
    fr=[e._next_observation().copy()]
    for t in range(1,7): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)
def amaps(cue,prop,color,ct,ci,mag=56.0):
    V=torch.from_numpy(np.stack([mkvid(cue,prop,color,ct,ci,mag) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): return m.forward_rl_sequence(V,return_attn=True)["attn_seq"].numpy().mean(0)  # (7,9,K)
# greedy correct (natural vda9)
cor=[]
for _ in range(100):
    e=make_env("vda9"); o=e.reset(); s=m.init_states(1); rw=0
    for t in range(7):
        x=torch.from_numpy(o.astype(np.float32)).permute(2,0,1).unsqueeze(0)
        with torch.no_grad(): st=m.rl_step(x,s); a=int(st["actor_logits"][0].argmax()); s=st["new_states"]
        o,rr,d,_=e.step(a)
        if d: rw=rr; break
    cor.append(rw>0)
K=amaps(0,1.0,"red",0,-1).shape[-1]; NK=9; HASMEM=(K==18)
print(f"[dd9 {FB}] iter={ck.get('iter')} greedy_correct={np.mean(cor):.3f} attn_keys={K} ({'9 image+9 memory' if HASMEM else '9 self'})")
# conditions: cue@0(TL) and cue@8(BR); valid(chg@cued) & invalid(chg@other corner); prop 1.0 AND 0.0
UNC={0:8,8:0}
CONDS=[]
for cue in (0,8):
    for prop in (1.0,0.0):
        CONDS.append((f"cue@P{cue} p{prop} valid",  cue,prop,1,cue))
        CONDS.append((f"cue@P{cue} p{prop} inval",  cue,prop,1,UNC[cue]))
A={nm:amaps(cue,prop,"red",ct,ci) for nm,cue,prop,ct,ci in CONDS}
np.savez(os.path.join(_HERE,f"data_dd9_{FB}.npz"),iter=ck.get("iter"),keys=K,**{f"a__{nm}":A[nm] for nm,*_ in CONDS})

def imshow_grid(ax,M,vmax,labx):
    ax.imshow(M,cmap="magma",vmin=0,vmax=vmax)
    for (yy,xx),v in np.ndenumerate(M): ax.text(xx,yy,f"{v:.2f}",ha="center",va="center",fontsize=3.5,color="white" if v<vmax*.6 else "black")
    ax.set_xticks(range(M.shape[1])); ax.set_yticks(range(9)); ax.set_xticklabels(labx,fontsize=3.5); ax.set_yticklabels(TOK,fontsize=3.5)
# maps at cue/change/post frames for each condition (rows), 3 frames (cols)
def maps_fig(part):
    if part=="image": sl=slice(0,9); labx=TOK; tag="IMAGE keys"
    elif part=="memory": sl=slice(9,18); labx=TOK; tag="MEMORY keys"
    else: sl=slice(0,9); labx=TOK; tag="self-attn keys"
    vmax=max(A[nm][:,:,sl].max() for nm,*_ in CONDS)
    fig,ax=plt.subplots(len(CONDS),3,figsize=(3*2.0,len(CONDS)*1.9))
    for r,(nm,cue,prop,ct,ci) in enumerate(CONDS):
        for c,f in enumerate((1,5,6)):
            imshow_grid(ax[r,c],A[nm][f,:,sl],vmax,labx)
            if r==0: ax[r,c].set_title(["f1 cue","f5 chg","f6 post"][c],fontsize=7)
            if c==0: ax[r,c].set_ylabel(nm,fontsize=5)
            ax[r,c].get_xticklabels()[cue].set_color("limegreen"); ax[r,c].get_xticklabels()[ci if ct else cue].set_color("red")
    fig.suptitle(f"grid9 {FB} — {tag} A[query→key] (mean/{B}); green=cued red=changed; iter {ck.get('iter')}",fontsize=8)
    fig.tight_layout(rect=[0,0,1,.97]); fn=f"dd9_{FB}_{part}.png"; fig.savefig(os.path.join(FIGS,fn),dpi=150,bbox_inches="tight"); plt.close(fig); print("saved",fn)
if HASMEM: maps_fig("image"); maps_fig("memory")
else: maps_fig("self")

# summary metrics (per-query, magnitudes): cue read, change-lock valid/invalid, prop1 vs prop0
def to_key(M,f,k,memkeys=False): off=9 if (memkeys and HASMEM) else 0; return float(M[f,:,off+k].mean())
print("\n== cue-frame read (attention TO cued key) & change-lock (TO changed key) — prop 1.0 vs 0.0 ==")
for nm,cue,prop,ct,ci in CONDS:
    chk=HASMEM   # for crossattn use memory keys for the lock; for affine use the (only) self keys
    cueR=to_key(A[nm],1,cue,memkeys=False)                       # image/self attention to cued at f1
    l5=to_key(A[nm],5,ci,memkeys=chk); l6=to_key(A[nm],6,ci,memkeys=chk)
    print(f"  {nm}: cue-read(f1→cued img)={cueR:.3f}  change-lock f5={l5:.3f} f6={l6:.3f} (uniform={1/9:.3f})")
