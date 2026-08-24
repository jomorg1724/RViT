"""Shared core for the conv-model deep-dive (paper_jepa_conv_d128: conv front-end + crossattn1 + JEPA,
plain 7-step vda4). One model load, one set of conventions, reused by every dd*.py module.

CROSS-ATTENTION (how attention scores are computed — the load-bearing definition):
  token  X_i = [ ô_i(128) ‖ ρ_i(4) ‖ τ(8) ] ∈ ℝ^{140}, i∈{S1=TL,TR,BL,S4=BR} (row-major).
  Q = X W_q ∈ ℝ^{4×140};  K = [X W_kx ‖ H W_kh] ∈ ℝ^{8×140};  V = [X W_vx ‖ H W_vh] ∈ ℝ^{8×140}
  A = softmax( Q Kᵀ / √140 )  over the 8 keys (dim=-1) → A[i,j]: query patch i → key j
       (j∈0..3 = IMAGE patch j ; j∈4..7 = MEMORY token j-4 of the per-patch xLSTM cell H).
  Each query ROW of A sums to 1. Z = X + A V (residual = X). We report A; mean over trials only.
Token order [S1/TL, TR, BL, S4/BR]; cue/change indices use the same order (S1=0 … S4=3)."""
import os, sys, numpy as np, torch
torch.set_num_threads(3)
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env

TOK=["S1","TR","BL","S4"]; COLOR_VAL={"red":5,"green":3,"blue":1}; FIGS=os.path.join(_HERE,"figs")
T=7

def load(snap):
    """Load the EXACT trained architecture. The conv front-end's out-norm was LayerNorm at train
    time (later code uses RMSNorm); a LayerNorm checkpoint carries front.out_norm.bias, so we match
    it to avoid a silent semantic mismatch (RMSNorm omits the mean-subtraction + bias). Asserts a
    clean 0-missing/0-unexpected load so an arch mismatch can never pass silently again."""
    import torch.nn as nn
    ck=torch.load(snap,map_location="cpu",weights_only=False); sd=ck["model_state_dict"]
    m=RViTPaperModel(cell="xlstm",feedback="crossattn1",n_quantiles=5,seq_len=T,jepa_n_heads=4,
                     jepa_proto_dim=256,frame_repeat=1,d_mem=128,conv_frontend=True)
    if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm):
        m.front.out_norm = nn.LayerNorm(128)            # match the TRAINED out-norm
    r=m.load_state_dict(sd,strict=False); m.eval()
    assert not r.missing_keys and not r.unexpected_keys, f"ARCH MISMATCH missing={r.missing_keys} unexpected={r.unexpected_keys}"
    return m, int(ck.get("iter",-1)), (len(r.missing_keys),len(r.unexpected_keys))

def _env():
    return make_env("vda4",T=T,frame_repeat=1,min_change_time=5,max_change_time=5,
                    noise_multiplier=5.0,curriculum=False)

def make_video(cue, prop, color, change_true, change_idx, mag=56.0):
    """One forced-WAIT 7-frame episode with fully controlled cue/validity/value/change."""
    e=_env(); o=e.reset()
    while e.change_true!=change_true: o=e.reset()
    e.cue_index=int(cue); e.cue_color=color; e.proportion=float(prop)
    if change_true: e.change_index=int(change_idx); e.orientation_change=float(mag)
    fr=[e._next_observation().copy()]
    for t in range(1,T): o,_,_,_=e.step(0); fr.append(o.copy())
    return np.stack(fr)  # (7,50,50,3)

def attn_maps(m, cue, prop, color, change_true, change_idx, mag=56.0, B=96):
    """Mean-over-trials attention A (7,4,8): [frame, query patch, key]; keys 0-3 image, 4-7 memory."""
    V=torch.from_numpy(np.stack([make_video(cue,prop,color,change_true,change_idx,mag) for _ in range(B)])
                       .astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): a=m.forward_rl_sequence(V,return_attn=True)["attn_seq"].numpy()  # (B,7,4,8)
    return a.mean(0)

def press_times(m, cue, prop, color, change_true, change_idx, mag=56.0, B=300):
    """BATCHED open-loop greedy press extraction (forced-WAIT videos → one forward → first argmax=1 frame).
    Equivalent to closed-loop for the FIRST press (obs are identical up to the press). Returns press[B]
    (frame index of first declare, or -1). change_time=5: hit = press>=5, premature = 0<=press<5."""
    V=torch.from_numpy(np.stack([make_video(cue,prop,color,change_true,change_idx,mag) for _ in range(B)])
                       .astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): act=m.forward_rl_sequence(V)["actor_logits_seq"].argmax(-1).numpy()  # (B,7)
    press=np.full(B,-1)
    for t in range(T):
        hit=(act[:,t]==1)&(press<0); press[hit]=t
    return press

def rollout(m, cue=None, prop=None, color=None, change_true=None, change_idx=None, mag=56.0, n=400, seed=0):
    """Greedy rollouts with optional forced conditions. Returns dict of outcome arrays."""
    rng=np.random.default_rng(seed); out=dict(hit=[],miss=[],cr=[],fa=[],press=[],correct=[],reward=[],valid=[])
    for _ in range(n):
        e=_env(); o=e.reset()
        if change_true is not None:
            while e.change_true!=change_true: o=e.reset()
        if cue is not None: e.cue_index=int(cue)
        if color is not None: e.cue_color=color
        if prop is not None: e.proportion=float(prop)
        if change_true and change_idx is not None: e.change_index=int(change_idx)
        if change_true and mag is not None: e.orientation_change=float(mag)
        e.valid=int(e.change_true==1 and e.change_index==e.cue_index)
        s=m.init_states(1); pressed=-1; rw=0.0; o=e._next_observation()
        for t in range(T):
            x=torch.from_numpy(o.astype(np.float32)).permute(2,0,1).unsqueeze(0)
            with torch.no_grad(): st=m.rl_step(x,s); a=int(st["actor_logits"][0].argmax()); s=st["new_states"]
            o,r,d,_=e.step(a)
            if a==1 and pressed<0: pressed=t
            if d: rw=r; break
        ct=e.change_true; corr=rw>0
        out["correct"].append(corr); out["reward"].append(rw); out["press"].append(pressed); out["valid"].append(e.valid)
        out["hit"].append(ct==1 and corr); out["miss"].append(ct==1 and pressed<0)
        out["cr"].append(ct==0 and corr); out["fa"].append(pressed>=0 and not corr)
    return {k:np.array(v) for k,v in out.items()}
