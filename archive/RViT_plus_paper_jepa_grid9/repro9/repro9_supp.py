"""Supplementary-figure machinery (Figs 8-17) for the 9-stimulus grid9 variants, mirroring the conv
repro_supp but for a 3x3 grid: cues at corners S1(=0, top-left) and S9(=8, bottom-right); nine change
locations; K=18 keys (9 image + 9 memory) for crossattn1, K=9 for affine_ew (auto-detected). Decoding
(8-11), actor-logit geometry (12-13), value/TD/entropy (14-15), SDT criterion & sensitivity (16),
supervised-vs-RL (17). CPU/MPS; decoders are tiny MLPs trained on natural data."""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
_HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,_HERE)
import repro9_core as C
from scipy.stats import norm
T=C.T; NP=9; DMEM=128
LOCNAMES=["No chg"]+[f"S{i+1}" for i in range(NP)]     # 0=no change, 1..9 = S1..S9
CUED, UNCUED = 0, 8                                     # corner cue at S1(TL); its opposite corner S9(BR)

def n_keys(m):
    a=C.attn_maps(m,CUED,1.0,"red",0,-1,B=2); return int(a.shape[-1])

def rollout(m, V, clamp=None, clamp_from=5, want_attn=False):
    V=V.to(C.DEVICE); B=V.shape[0]; s=m.init_states(B,device=C.DEVICE); lo=[];vs=[];vd=[];rec=[];aw=[]
    for t in range(T):
        cl=clamp if (clamp and t>=clamp_from) else None
        with torch.no_grad():
            st=m.rl_step(V[:,t], s, attn_clamp=cl, return_attn=want_attn); s=st["new_states"]
        lo.append(st["actor_logits"]); vs.append(st["V_scalar"]); vd.append(st["V_dist"]); rec.append(st["rec"])
        if want_attn and st["attn"] is not None: aw.append(st["attn"][0])
    out=dict(logits=torch.stack(lo,1).cpu().numpy(), Vsc=torch.stack(vs,1).cpu().numpy(),
             Vd=torch.stack(vd,1).cpu().numpy(), rec=torch.stack(rec,1).cpu())
    if want_attn and aw: out["attn"]=torch.stack(aw,1).cpu().numpy()
    C.empty_cache(); return out

def actor_first_activation(m, rec_t):
    with torch.no_grad(): return m.actor_head.net[:2](rec_t.to(C.DEVICE)).cpu().numpy()

def gen_trials(cue, prop, N, p_change=0.5, mag_lo=1.0, mag_hi=60.0, seed=0):
    rng=np.random.default_rng(seed); vids=[]; loc=np.full(N,-1,int); dl=np.zeros(N)
    for n in range(N):
        if rng.random()<p_change:
            l=int(rng.integers(0,NP)); mag=float(rng.uniform(mag_lo,mag_hi)); loc[n]=l; dl[n]=mag
            vids.append(C.make_video(cue,prop,"red",1,l,mag))
        else:
            vids.append(C.make_video(cue,prop,"red",0,-1,0.0))
    return C._tens(vids), loc, dl
def occ(loc): return (loc>=0).astype(int)
def loc10(loc): return loc+1

def clamp_alpha(K,i,alpha,scale=6.0):
    b=scale*(2*float(alpha)-1.0); return {str(k):b for k in C._loc_keys(K,i)}
def clamp_spread(K,cued=0,b=4.0):
    d={}
    for j in range(NP):
        if j!=cued:
            for k in C._loc_keys(K,j): d[str(k)]=b
    return d

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

def det_rate(m,cue,prop,ct,ci,mag,clamp,clamp_from,B=300):
    p=C.press_times_clamp(m,cue,prop,"red",ct,ci,mag,clamp,clamp_from,B); return float((p>=5).mean())
def sdt(hit,fa,n=300):
    eps=1.0/(2*n); h=min(max(hit,eps),1-eps); f=min(max(fa,eps),1-eps)
    zh,zf=norm.ppf(h),norm.ppf(f); return dict(c=-0.5*(zh+zf),dprime=zh-zf,hit=hit,fa=fa)
