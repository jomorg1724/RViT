"""Reproduction core for the 9-stimulus grid9 variants (vda9: 3x3, 75x75, corner cues TL=0/BR=8, plus the
0-proportion = uninformative cue). Same analyses as the conv (4-stim) repro but for 9 patches. Handles
crossattn1 (9 image + 9 memory keys) and affine_ew (9x9 self). CPU/low-memory (no training)."""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
_ROOT="/Users/jonathanmorgan/AttentionManuscript/RViT_plus_paper_jepa_grid9"; sys.path.insert(0,_ROOT)
from model import RViTPaperModel
from envs import make_env
FIGS=os.path.join(os.path.dirname(os.path.abspath(__file__)),"figs"); os.makedirs(FIGS,exist_ok=True)
T=7; COLOR_VAL={"red":5,"green":3,"blue":1}
# Task-parametric: default vda9 reproduces the original 9-stim behaviour byte-for-byte.
TASK=os.environ.get("RVIT_REPRO_TASK","vda9")
_SPEC={"vda2":(2,2,50),"vda4":(2,2,50),"vda9":(3,3,75),"vda16":(4,4,100)}
GR,GC,ISZ=_SPEC[TASK]; NP=GR*GC; CUES=[0,NP-1]     # cue corners: S1 (idx 0) and S_last (idx NP-1)
UNC={CUES[0]:CUES[-1], CUES[-1]:CUES[0]}           # cued -> uncued corner mapping (task-parametric)
# Which grid cells actually carry a stimulus. CRITICAL for set-size<grid envs (vda1/vda2): the env
# randomizes `active` per reset, so a change at the cued cell is only rendered ~half the time unless we
# PIN it (else detection caps at 50%). vda4/9/16 fill the whole grid, so this is a no-op there.
_ACTIVE={"vda1":[0],"vda2":[0,NP-1]}
ACTIVE=_ACTIVE.get(TASK, list(range(NP)))
NSTIM=len(ACTIVE)                                  # number of actual stimuli (2 for vda2, 9 for vda9)
TAG=f"{TASK}: {NSTIM}-stim {GR}x{GC}"              # figure-title tag (replaces hardcoded 'grid9, 9-stim')
SLO="S1"; SHI=f"S{NSTIM}"                          # cued / uncued stimulus labels (S1 / S2 for vda2)
DEVICE=os.environ.get("RVIT_DEVICE") or ("mps" if torch.backends.mps.is_available() else "cpu")
def empty_cache():
    if DEVICE=="mps":
        try: torch.mps.empty_cache()
        except Exception: pass
def load(snap,feedback):
    ck=torch.load(snap,map_location="cpu",weights_only=False); sd=ck["model_state_dict"]
    m=RViTPaperModel(cell="xlstm",feedback=feedback,n_quantiles=5,seq_len=T,jepa_n_heads=4,jepa_proto_dim=256,
                     frame_repeat=1,d_mem=128,conv_frontend=True,grid_rows=GR,grid_cols=GC,image_size=ISZ)
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm,nn.LayerNorm): m.front.out_norm=nn.LayerNorm(128)
    r=m.load_state_dict(sd,strict=False); m.eval(); assert not r.missing_keys and not r.unexpected_keys,(r.missing_keys,r.unexpected_keys)
    m.to(DEVICE); return m,int(ck.get("iter",-1))
def _env(): return make_env(TASK,T=T,frame_repeat=1,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)
def make_video(cue,prop,color,ct,ci,mag=56.0):
    e=_env(); o=e.reset()
    while e.change_true!=ct: o=e.reset()
    if hasattr(e,"active"): e.active=list(ACTIVE)   # pin stimulus cells (fixes the vda1/vda2 50% cap)
    e.cue_index=int(cue); e.cue_color=color; e.proportion=float(prop)
    if ct: e.change_index=int(ci); e.orientation_change=float(mag)
    fr=[e._next_observation().copy()]
    for t in range(1,T): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)
def _tens(v): return torch.from_numpy(np.stack(v).astype(np.float32)).permute(0,1,4,2,3).contiguous()
def press_times(m,cue,prop,color,ct,ci,mag=56.0,B=300):
    with torch.no_grad():
        V=_tens([make_video(cue,prop,color,ct,ci,mag) for _ in range(B)]).to(DEVICE)
        act=m.forward_rl_sequence(V)["actor_logits_seq"].argmax(-1).cpu().numpy()
    empty_cache(); press=np.full(B,-1)
    for t in range(T):
        h=(act[:,t]==1)&(press<0); press[h]=t
    return press
def behavior(m,cue,prop,ci,mag,color="red",ct=1,B=300):
    p=press_times(m,cue,prop,color,ct,ci,mag,B); det=p>=5
    return float(det.mean()),(float(p[det].mean()) if det.any() else np.nan)
def attn_maps(m,cue,prop,color,ct,ci,mag=56.0,B=96):
    with torch.no_grad():
        V=_tens([make_video(cue,prop,color,ct,ci,mag) for _ in range(B)]).to(DEVICE)
        a=m.forward_rl_sequence(V,return_attn=True)["attn_seq"].cpu().numpy().mean(0)  # (7,9,K)
    empty_cache(); return a
def _loc_keys(K,i): return [i,NP+i] if K==2*NP else [i]
def clamp_on(K,i,b=100.0): return {str(k):b for k in _loc_keys(K,i)}
def clamp_off(K,i,b=-100.0): return {str(k):b for k in _loc_keys(K,i)}
def clamp_graded(K,a1,a9,scale=6.0):   # bias corner S1(0) by a1, corner S_last(NP-1) by a9, suppress the rest
    d={str(k):scale*float(a1) for k in _loc_keys(K,0)}; d.update({str(k):scale*float(a9) for k in _loc_keys(K,NP-1)})
    for j in range(1,NP-1):
        for k in _loc_keys(K,j): d[str(k)]=-20.0
    return d
def press_times_clamp(m,cue,prop,color,ct,ci,mag,clamp=None,clamp_from=5,B=300):
    V=_tens([make_video(cue,prop,color,ct,ci,mag) for _ in range(B)]).to(DEVICE); s=m.init_states(B,device=DEVICE); press=np.full(B,-1)
    for t in range(T):
        cl=clamp if (clamp and t>=clamp_from) else None
        with torch.no_grad(): st=m.rl_step(V[:,t],s,attn_clamp=cl); a=st["actor_logits"].argmax(-1).cpu().numpy(); s=st["new_states"]
        h=(a==1)&(press<0); press[h]=t
    empty_cache(); return press
def behavior_clamp(m,cue,prop,ci,mag,clamp,B=300):
    p=press_times_clamp(m,cue,prop,"red",1,ci,mag,clamp,B=B); det=p>=5
    return float(det.mean()),(float(p[det].mean()) if det.any() else np.nan)
def logistic4(d,A,B,C,D): return A+(1-A-B)/(1+np.exp(-(np.asarray(d)-D)/C))
def fit_logistic(deltas,rates):
    from scipy.optimize import curve_fit
    d=np.asarray(deltas,float); y=np.asarray(rates,float)
    p0=[max(y.min(),0.02),max(1-y.max(),0.02),5.0,d[np.argmin(np.abs(y-0.5))] if len(d) else 15.0]
    try:
        popt,_=curve_fit(logistic4,d,y,p0=p0,maxfev=20000,bounds=([0,0,0.5,-10],[0.5,0.5,40,60]))
        return dict(guess=float(popt[0]),lapse=float(popt[1]),slope=float(1/popt[2]),position=float(popt[3]),popt=popt)
    except Exception: return dict(guess=np.nan,lapse=np.nan,slope=np.nan,position=np.nan,popt=p0)
