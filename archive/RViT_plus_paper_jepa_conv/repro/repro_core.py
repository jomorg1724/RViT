"""Reproduction core for the Morgan/Albanna/Herman paper figures, using our conv-frontend d128 JEPA
variants (crossattn1 OR affine_ew) on the SAME 4-stimulus vda4 task (50x50, cue S1/S4, 4 Gabors, change
at t=5). CPU + low-memory (no training). Handles both feedbacks; extracts behaviour (response rate + RT),
attention maps, and fits the paper's 4-parameter logistic. Δ = orientation-change magnitude in degrees."""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env
FIGS=os.path.join(_HERE,"figs"); os.makedirs(FIGS,exist_ok=True)
TOK=["S1","TR","BL","S4"]; COLOR_VAL={"red":5,"green":3,"blue":1}; T=7
# device: MPS (Apple GPU) is ~19x faster on the forward pass and lighter on the CPU than an all-core
# CPU job; override with RVIT_DEVICE=cpu. The MPS caching allocator can balloon RAM, so we empty_cache().
DEVICE=os.environ.get("RVIT_DEVICE") or ("mps" if torch.backends.mps.is_available() else "cpu")
def empty_cache():
    if DEVICE=="mps":
        try: torch.mps.empty_cache()
        except Exception: pass

def load(snap, feedback):
    ck=torch.load(snap,map_location="cpu",weights_only=False); sd=ck["model_state_dict"]
    m=RViTPaperModel(cell="xlstm",feedback=feedback,n_quantiles=5,seq_len=T,jepa_n_heads=4,
                     jepa_proto_dim=256,frame_repeat=1,d_mem=128,conv_frontend=True)
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm,nn.LayerNorm): m.front.out_norm=nn.LayerNorm(128)
    r=m.load_state_dict(sd,strict=False); m.eval()
    assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys,r.unexpected_keys)
    m.to(DEVICE)
    return m, int(ck.get("iter",-1))

def _env(): return make_env("vda4",T=T,frame_repeat=1,min_change_time=5,max_change_time=5,noise_multiplier=5.0,curriculum=False)

def make_video(cue, prop, color, change_true, change_idx, mag=56.0):
    e=_env(); o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=int(cue); e.cue_color=color; e.proportion=float(prop)
    if change_true: e.change_index=int(change_idx); e.orientation_change=float(mag)
    fr=[e._next_observation().copy()]
    for t in range(1,T): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)

def _tens(v): return torch.from_numpy(np.stack(v).astype(np.float32)).permute(0,1,4,2,3).contiguous()

def press_times(m, cue, prop, color, change_true, change_idx, mag=56.0, B=300):
    """Batched open-loop greedy first-press frame (or -1). change_time=5: detection = press in {5,6}."""
    with torch.no_grad():
        V=_tens([make_video(cue,prop,color,change_true,change_idx,mag) for _ in range(B)]).to(DEVICE)
        act=m.forward_rl_sequence(V)["actor_logits_seq"].argmax(-1).cpu().numpy()
    empty_cache()
    press=np.full(B,-1)
    for t in range(T):
        h=(act[:,t]==1)&(press<0); press[h]=t
    return press

def behavior(m, cue, prop, change_idx, mag, color="red", change_true=1, B=300):
    """Returns (response_rate, mean_RT). response_rate = P(press>=5); RT = mean press frame among detections."""
    p=press_times(m,cue,prop,color,change_true,change_idx,mag,B); det=p>=5
    return float(det.mean()), (float(p[det].mean()) if det.any() else np.nan)

def attn_maps(m, cue, prop, color, change_true, change_idx, mag=56.0, B=96):
    with torch.no_grad():
        V=_tens([make_video(cue,prop,color,change_true,change_idx,mag) for _ in range(B)]).to(DEVICE)
        a=m.forward_rl_sequence(V,return_attn=True)["attn_seq"].cpu().numpy().mean(0)   # (7,4,K) K=8 crossattn / 4 affine
    empty_cache(); return a

# ---- attention manipulation (Fig 5): clamp α at t_change via attn_clamp on that location's keys ----
def _loc_keys(K, i): return [i, 4+i] if K == 8 else [i]     # crossattn: image i + memory 4+i; affine: self key i
def clamp_on(K, i, bias=100.0):  return {str(k): bias for k in _loc_keys(K, i)}    # α_i → 1 (force attention onto i)
def clamp_off(K, i, bias=-100.0): return {str(k): bias for k in _loc_keys(K, i)}   # α_i → 0 (suppress i)
def clamp_graded(K, a1, a4, scale=6.0):   # Fig 5G: bias S1/S4 by ~logit, suppress others → ratio ≈ softmax
    d={str(k): scale*float(a1) for k in _loc_keys(K,0)}; d.update({str(k): scale*float(a4) for k in _loc_keys(K,3)})
    for j in (1,2):
        for k in _loc_keys(K,j): d[str(k)] = -20.0
    return d
def press_times_clamp(m, cue, prop, color, ct, ci, mag, clamp=None, clamp_from=5, B=300):
    """Batched open-loop rollout applying attn_clamp at frames >= clamp_from (5 = t_change)."""
    V=_tens([make_video(cue,prop,color,ct,ci,mag) for _ in range(B)]).to(DEVICE); s=m.init_states(B,device=DEVICE); press=np.full(B,-1)
    for t in range(T):
        cl=clamp if (clamp and t>=clamp_from) else None
        with torch.no_grad():
            st=m.rl_step(V[:,t], s, attn_clamp=cl); a=st["actor_logits"].argmax(-1).cpu().numpy(); s=st["new_states"]
        h=(a==1)&(press<0); press[h]=t
    empty_cache(); return press
def behavior_clamp(m, cue, prop, ci, mag, clamp, B=300):
    p=press_times_clamp(m,cue,prop,"red",1,ci,mag,clamp,B=B); det=p>=5
    return float(det.mean()), (float(p[det].mean()) if det.any() else np.nan)

# ---- paper's 4-parameter logistic: P(Δ)=A + (1-A-B)/(1+exp(-(Δ-D)/C)) ; A guess, B lapse, C slope(°), D pos(°) ----
def logistic4(delta, A, B, C, D): return A + (1.0-A-B)/(1.0+np.exp(-(np.asarray(delta)-D)/C))
def fit_logistic(deltas, rates):
    from scipy.optimize import curve_fit
    d=np.asarray(deltas,float); y=np.asarray(rates,float)
    p0=[max(y.min(),0.02), max(1-y.max(),0.02), 5.0, d[np.argmin(np.abs(y-0.5))] if len(d) else 15.0]
    try:
        popt,_=curve_fit(logistic4,d,y,p0=p0,maxfev=20000,
                         bounds=([0,0,0.5,-10],[0.5,0.5,40,60]))
        return dict(guess=float(popt[0]), lapse=float(popt[1]), slope=float(1.0/popt[2]), position=float(popt[3]), popt=popt)
    except Exception as e:
        return dict(guess=np.nan,lapse=np.nan,slope=np.nan,position=np.nan,popt=p0)
