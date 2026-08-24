"""Supplementary-figure machinery (Figs 8-17) for the conv 4-stimulus variants, built on repro_core.
Covers: change-location / change-occurrence DECODING from the mnemonic percept H, a single patch h1,
and the actor's first activation, under attention modulation (Figs 8-11); actor-LOGIT geometry
(Declare-Change vs Wait) by Δ and density (Figs 12-13); TD errors, value and ENTROPY under attention
bias (Figs 14-15); and the SDT CRITERION c & SENSITIVITY d' after biasing attention at cue-time vs
change-time --- the 'stimulation experiments' (Fig 16). Model-agnostic across crossattn1 (K=8) and
affine_ew (K=4); K auto-detected. CPU / low-memory; decoders are tiny MLPs trained on natural data."""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_HERE)
import repro_core as C
from scipy.stats import norm
T=C.T; NP=4; DMEM=128
LOCNAMES=["No change","S1","S2","S3","S4"]

# ── infer key count (8 crossattn = 4 image + 4 memory; 4 affine/self) ───────────────────────────────
def n_keys(m):
    a=C.attn_maps(m,0,1.0,"red",0,-1,B=2); return int(a.shape[-1])

# ── generic batched rollout: per-frame actor logits, value, value-dist, and the H_flat percept ──────
def rollout(m, V, clamp=None, clamp_from=5, want_attn=False):
    V=V.to(C.DEVICE); B=V.shape[0]; s=m.init_states(B,device=C.DEVICE); lo=[];vs=[];vd=[];rec=[];aw=[]
    for t in range(T):
        cl=clamp if (clamp and t>=clamp_from) else None
        with torch.no_grad():
            st=m.rl_step(V[:,t], s, attn_clamp=cl, return_attn=want_attn); s=st["new_states"]
        lo.append(st["actor_logits"]); vs.append(st["V_scalar"]); vd.append(st["V_dist"]); rec.append(st["rec"])
        if want_attn and st["attn"] is not None: aw.append(st["attn"][0])
    out=dict(logits=torch.stack(lo,1).cpu().numpy(), Vsc=torch.stack(vs,1).cpu().numpy(),
             Vd=torch.stack(vd,1).cpu().numpy(), rec=torch.stack(rec,1).cpu())   # rec kept as CPU tensor (B,T,512)
    if want_attn and aw: out["attn"]=torch.stack(aw,1).cpu().numpy()
    C.empty_cache(); return out

def actor_first_activation(m, rec_t):   # rec_t (N,512) tensor → first ELU activation (N,hidden)
    with torch.no_grad(): return m.actor_head.net[:2](rec_t.to(C.DEVICE)).cpu().numpy()

# ── labelled trial generator (mixed change / no-change, random location & Δ) ─────────────────────────
def gen_trials(cue, prop, N, p_change=0.5, mag_lo=1.0, mag_hi=60.0, seed=0):
    rng=np.random.default_rng(seed); vids=[]; loc=np.full(N,-1,int); dl=np.zeros(N)
    for n in range(N):
        if rng.random()<p_change:
            l=int(rng.integers(0,NP)); mag=float(rng.uniform(mag_lo,mag_hi)); loc[n]=l; dl[n]=mag
            vids.append(C.make_video(cue,prop,"red",1,l,mag))
        else:
            vids.append(C.make_video(cue,prop,"red",0,-1,0.0))
    return C._tens(vids), loc, dl
def occ(loc): return (loc>=0).astype(int)          # change occurred?
def loc5(loc): return loc+1                         # 0=no-change, 1..4 = S1..S4

# ── attention clamps (single location, graded; spread/uniform-ising) ─────────────────────────────────
def clamp_alpha(K,i,alpha,scale=6.0):               # alpha 0..1 (0.5≈natural, no bias)
    b=scale*(2*float(alpha)-1.0); return {str(k):b for k in C._loc_keys(K,i)}
def clamp_spread(K,cued=0,b=4.0):                   # bias the 3 non-cued image locations UP toward the cued level
    d={}
    for j in range(NP):
        if j!=cued:
            for k in C._loc_keys(K,j): d[str(k)]=b
    return d

# ── tiny MLP decoder (paper Eq 33-35: Linear→LN→ELU ×2 → Linear) ─────────────────────────────────────
class Dec(nn.Module):
    def __init__(s,din,dout):
        super().__init__()
        s.net=nn.Sequential(nn.Linear(din,512),nn.LayerNorm(512),nn.ELU(),
                            nn.Linear(512,256),nn.LayerNorm(256),nn.ELU(),nn.Linear(256,dout))
    def forward(s,x): return s.net(x)
def train_decoder(X,y,dout,epochs=120,bs=256,lr=1e-3,seed=0):
    torch.manual_seed(seed)
    Xt=torch.as_tensor(X,dtype=torch.float32); yt=torch.as_tensor(y,dtype=torch.long)
    mu=Xt.mean(0,keepdim=True); sd=Xt.std(0,keepdim=True)+1e-5; Xn=(Xt-mu)/sd
    d=Dec(Xt.shape[1],dout); opt=torch.optim.Adam(d.parameters(),lr=lr); lossf=nn.CrossEntropyLoss()
    n=Xt.shape[0]
    for ep in range(epochs):
        perm=torch.randperm(n)
        for i in range(0,n,bs):
            idx=perm[i:i+bs]; opt.zero_grad(); l=lossf(d(Xn[idx]),yt[idx]); l.backward(); opt.step()
    d.eval(); return d,(mu,sd)
def dec_predict(d,norm,X):
    mu,sd=norm; Xn=(torch.as_tensor(X,dtype=torch.float32)-mu)/sd
    with torch.no_grad(): return d(Xn).argmax(-1).numpy()
def confmat(y,yhat,nc):
    M=np.zeros((nc,nc),int)
    for a,b in zip(y,yhat): M[int(a),int(b)]+=1
    return M

# ── SDT: criterion & sensitivity (Fig 16) ────────────────────────────────────────────────────────────
def det_rate(m,cue,prop,ct,ci,mag,clamp,clamp_from,B=300):
    p=C.press_times_clamp(m,cue,prop,"red",ct,ci,mag,clamp,clamp_from,B); return float((p>=5).mean())
def sdt(hit,fa,n=300):
    eps=1.0/(2*n); h=min(max(hit,eps),1-eps); f=min(max(fa,eps),1-eps)
    zh,zf=norm.ppf(h),norm.ppf(f); return dict(c=-0.5*(zh+zf),dprime=zh-zf,hit=hit,fa=fa)
