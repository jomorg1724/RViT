"""Core for the affine_ew model deep-dive (conv front-end + ELEMENT-WISE AFFINE self-attention + JEPA,
7-step vda4). The feedback memory H modulates the visual features element-wise BEFORE a standard
self-attention over the 4 patches:
    γ = scale(H), β = broadcast(H)   (element-wise vectors, NO identity term)
    X' = γ ⊙ X + β
    Q,K,V = X'W_q, X'W_k, X'W_v ;  A = softmax(QKᵀ/√140) over the 4 KEY patches ;  Z = X + A V
So A is (T,4,4): A[i,j] = attention from query patch i to key patch j (the 4 image quadrants); there is
NO separate memory-key column — memory enters through γ,β. Token order [S1/TL,TR,BL,S4/BR].

THIS TIME the validity manipulation is EXERCISED, not forced: changes are presented at the cued patch
(valid) AND at an uncued patch (invalid) AND drawn naturally (cued with prob = proportion), so the
displayed proportion's MEANING actually varies."""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env
TOK=["S1","TR","BL","S4"]; COLOR_VAL={"red":5,"green":3,"blue":1}; FIGS=os.path.join(_HERE,"figs"); T=7
os.makedirs(FIGS, exist_ok=True)

def load(snap):
    ck=torch.load(snap,map_location="cpu",weights_only=False); sd=ck["model_state_dict"]
    m=RViTPaperModel(cell="xlstm",feedback="affine_ew",n_quantiles=5,seq_len=T,jepa_n_heads=4,
                     jepa_proto_dim=256,frame_repeat=1,d_mem=128,conv_frontend=True)
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm,nn.LayerNorm): m.front.out_norm=nn.LayerNorm(128)
    r=m.load_state_dict(sd,strict=False); m.eval()
    assert not r.missing_keys and not r.unexpected_keys, f"ARCH MISMATCH {r.missing_keys}/{r.unexpected_keys}"
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

def _tens(vids): return torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0,1,4,2,3).contiguous()

def attn_maps(m, cue, prop, color, change_true, change_idx, mag=56.0, B=96):
    """Mean-over-trials attention A (7,4,4): [frame, query patch, key patch]."""
    with torch.no_grad():
        a=m.forward_rl_sequence(_tens([make_video(cue,prop,color,change_true,change_idx,mag) for _ in range(B)]),
                                return_attn=True)["attn_seq"].numpy()  # (B,7,4,4)
    return a.mean(0)

def press_times(m, cue, prop, color, change_true, change_idx, mag=56.0, B=200):
    with torch.no_grad():
        act=m.forward_rl_sequence(_tens([make_video(cue,prop,color,change_true,change_idx,mag) for _ in range(B)]))["actor_logits_seq"].argmax(-1).numpy()
    press=np.full(B,-1)
    for t in range(T):
        h=(act[:,t]==1)&(press<0); press[h]=t
    return press

def detect_rate(m, cue, change_idx, mag, prop, color="red", B=200):
    """P(correct detection)=P(press>=change_time 5) on a change trial."""
    return float((press_times(m,cue,prop,color,1,change_idx,mag,B)>=5).mean())
