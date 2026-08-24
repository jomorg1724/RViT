"""dd1 — BEHAVIORAL PROFILE on NATURAL trials (env draws cue/value/validity/change itself; no forcing).
Greedy press extracted open-loop from forced-wait frames (pre-press observations are press-independent).
Makes the headline correct/hit/CR/FA/miss rate reproducible IN-ARTIFACT (the .tex previously carried the
0.84 number from a separate training eval). change_time=5: hit=change&press>=5, CR=no-change&no press."""
import os, sys, numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dd_core as C
SNAP=sys.argv[1]; m,IT,ld=C.load(SNAP); T=C.T; N=600
print(f"[dd1] iter={IT} load={ld}")
def natural(n, seed=0):
    vids=[]; ct=[]; prop=[]; val=[]
    for _ in range(n):
        e=C._env(); o=e.reset()                      # natural draw
        ct.append(int(e.change_true)); prop.append(float(e.proportion)); val.append(C.COLOR_VAL.get(e.cue_color,0))
        fr=[o.copy()]
        for t in range(1,T): o,_,_,_=e.step(0); fr.append(o.copy())
        vids.append(np.stack(fr))
    V=torch.from_numpy(np.stack(vids).astype(np.float32)).permute(0,1,4,2,3).contiguous()
    with torch.no_grad(): act=m.forward_rl_sequence(V)["actor_logits_seq"].argmax(-1).numpy()
    press=np.full(n,-1)
    for t in range(T):
        h=(act[:,t]==1)&(press<0); press[h]=t
    return press, np.array(ct), np.array(prop), np.array(val)
press,ct,prop,val=natural(N)
chg=ct==1; noc=ct==0
hit=(chg)&(press>=5); miss=(chg)&(press<0); cr=(noc)&(press<0); fa=(press>=0)&(((noc))|((chg)&(press<5)))
correct=hit|cr
rt=press[hit]
print(f"N={N}  correct={correct.mean():.3f}  hit(of change)={hit[chg].mean():.3f}  CR(of nochg)={cr[noc].mean():.3f}  "
      f"FA(of nochg)={(fa&noc).mean()/max(noc.mean(),1e-9):.3f}  miss(of change)={miss[chg].mean():.3f}  RT(hit)={rt.mean():.2f}±{rt.std():.2f}")
# correct by proportion / by value (natural)
byp={float(p):float(correct[np.isclose(prop,p)].mean()) for p in sorted(set(prop))}
byv={int(v):float(correct[val==v].mean()) for v in sorted(set(val))}
print("correct by proportion:",{k:round(v,3) for k,v in byp.items()})
print("correct by value:",{k:round(v,3) for k,v in byv.items()})
np.savez(os.path.join(C.FIGS,"..","summary_dd1.npz"), iter=IT, N=N, correct=float(correct.mean()),
         hit=float(hit[chg].mean()), cr=float(cr[noc].mean()), fa=float((fa&noc).mean()/max(noc.mean(),1e-9)),
         miss=float(miss[chg].mean()), rt_mean=float(rt.mean()), rt_std=float(rt.std()),
         byprop=np.array([byp[k] for k in sorted(byp)]), props=np.array(sorted(byp)),
         byval=np.array([byv[k] for k in sorted(byv)]), vals=np.array(sorted(byv)))
print("saved summary_dd1.npz")
