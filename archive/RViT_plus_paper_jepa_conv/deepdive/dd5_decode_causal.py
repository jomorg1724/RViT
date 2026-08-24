"""dd5 — (A) TEMPORAL DECODING: what task variables are linearly decodable from the recurrent xLSTM
cell H_t (B,4,128 → 512) at each frame — cue position, cue value (colour), change presence, change
location. (B) CAUSAL PERTURBATION: with attn_clamp now wired into CrossAttentionXH, suppress the model's
read of the cued / all memory tokens during the gabor phase and measure the hit-rate cost — tests whether
the memory change-lock is CAUSAL for detection or epiphenomenal (recurrence detecting via the Z=X+ residual)."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd_core as C
SNAP=sys.argv[1]; m,IT,ld=C.load(SNAP); print(f"[dd5] iter={IT} load={ld}")
T=C.T; COLS=["blue","green","red"]

# ---------- (A) decoding ----------
def labeled_trials(n, seed=0):
    rng=np.random.default_rng(seed); vids=[]; lab=dict(cue=[],val=[],chg=[],loc=[])
    for _ in range(n):
        cue=int(rng.integers(4)); col=COLS[int(rng.integers(3))]; ct=int(rng.random()<0.5)
        loc=int(rng.integers(4)) if ct else -1
        vids.append(C.make_video(cue,1.0,col,ct,loc,56.0))
        lab["cue"].append(cue); lab["val"].append(C.COLOR_VAL[col]); lab["chg"].append(ct); lab["loc"].append(loc)
    V=torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): cell=m.forward_rl_sequence(V,return_cell=True)["cell_seq"].numpy()  # (n,7,4,128)
    return cell.reshape(n,T,-1), {k:np.array(v) for k,v in lab.items()}

def dec(X,y):
    X=(X-X.mean(0))/(X.std(0)+1e-6)
    try: return cross_val_score(LogisticRegression(max_iter=300,C=0.3),X,y,cv=4,scoring="balanced_accuracy").mean()
    except Exception: return np.nan
NF=420; cell,lab=labeled_trials(NF,seed=0)
chgmask=lab["chg"]==1
curves={"cue position (4-way)":[], "cue value (3-way)":[], "change present (2-way)":[], "change location (4-way)":[]}
for t in range(T):
    curves["cue position (4-way)"].append(dec(cell[:,t],lab["cue"]))
    curves["cue value (3-way)"].append(dec(cell[:,t],lab["val"]))
    curves["change present (2-way)"].append(dec(cell[:,t],lab["chg"]))
    curves["change location (4-way)"].append(dec(cell[chgmask,t],lab["loc"][chgmask]))
chance={"cue position (4-way)":.25,"cue value (3-way)":1/3,"change present (2-way)":.5,"change location (4-way)":.25}
fig,ax=plt.subplots(figsize=(7,4))
for k,v in curves.items():
    ln,=ax.plot(range(T),v,marker="o",label=k); ax.axhline(chance[k],ls=":",c=ln.get_color(),alpha=.4)
ax.axvline(1,ls=":",c="g",alpha=.4); ax.axvline(5,ls=":",c="r",alpha=.4)
ax.set_xlabel("frame (1=cue, 5=change)"); ax.set_ylabel("CV balanced accuracy"); ax.set_ylim(0,1.02)
ax.set_title(f"Temporal decoding from the recurrent cell H_t — conv crossattn1 iter {IT}",fontsize=9); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dd5_decoding.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print("decoding (dotted=chance):")
for k,v in curves.items(): print(f"  {k}: "+" ".join(f"f{t}={v[t]:.2f}" for t in range(T))+f"  (chance {chance[k]:.2f})")

# ---------- (B) causal perturbation ----------
def press_clamp(videos, clamp=None, clamp_from=3):
    B=videos.shape[0]; s=m.init_states(B); press=np.full(B,-1)
    for t in range(T):
        cl=clamp if (clamp and t>=clamp_from) else None
        with torch.no_grad(): st=m.rl_step(videos[:,t], s, attn_clamp=cl); a=st["actor_logits"].argmax(-1).numpy(); s=st["new_states"]
        hit=(a==1)&(press<0); press[hit]=t
    return press
def vids(cue,ci,mag,B=160):
    return torch.from_numpy(np.stack([C.make_video(cue,1.0,"red",1,ci,mag) for _ in range(B)]).astype(np.float32)).permute(0,1,4,2,3).contiguous()
MAGS=[8,16,28,44,64]; conds={"baseline":None}  # plus suppress-cued-mem, suppress-all-mem (set per cue below)
res={k:[] for k in ["baseline","suppress cued-mem","suppress all-mem"]}
for mg in MAGS:
    acc={k:[] for k in res}
    for cue in [0,3]:
        Vv=vids(cue,cue,mg)                                   # VALID change (change@cued)
        acc["baseline"].append((press_clamp(Vv)>=5).mean())
        acc["suppress cued-mem"].append((press_clamp(Vv,{str(4+cue):-100.0})>=5).mean())
        acc["suppress all-mem"].append((press_clamp(Vv,{str(4+k):-100.0 for k in range(4)})>=5).mean())
    for k in res: res[k].append(float(np.mean(acc[k])))
fig,ax=plt.subplots(figsize=(6.5,4))
for k in ["baseline","suppress cued-mem","suppress all-mem"]:
    ax.plot(MAGS,res[k],marker="o",label=k)
ax.set_xlabel("change magnitude |Δθ| (deg)"); ax.set_ylabel("P(detect) on VALID trials"); ax.set_ylim(-.02,1.02)
ax.set_title(f"Causal: suppressing the memory read (gabor phase) — iter {IT}",fontsize=9); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(C.FIGS,"dd5_causal.png"),dpi=150,bbox_inches="tight"); plt.close(fig)
print("causal P(detect) valid: "+" | ".join(f"{k}={[round(x,2) for x in res[k]]}" for k in res))
np.savez(os.path.join(C.FIGS,"..","summary_dd5.npz"), frames=list(range(T)), **{f"dec__{k}":v for k,v in curves.items()},
         mags=MAGS, **{f"causal__{k}":res[k] for k in res})
print("saved dd5_decoding / dd5_causal + summary_dd5.npz")
