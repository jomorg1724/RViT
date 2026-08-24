"""
Deep analysis across the matched feedback family: behaviour + the cue-100%-S1 attention
contrast, for each variant on the IDENTICAL frozen-VAE base. Loads ONE model at a time
(CPU, thread-capped) so it is safe to run alongside / after training.

For mechanism-level comparison (why affine orients to the cue), see cue_orienting_diagnosis.py.

For each variant we report: maturity (iter), behaviour (correct/hit/FA/median RT on
validity4), and two attention measures for a 100% cue at S1:
  cue-orienting index = S1 attention at the pre-change stimulus frames (t3,t4) minus
                        uniform, in the NO-CHANGE condition (so any S1 bias is cue-driven);
  change-locked spike = S1 attention jump at the change frame (t5 minus t4), change cond.
The attention map per variant is sliced to the image/spatial keys appropriately.
"""
from __future__ import annotations
import sys, os, glob
import numpy as np
import torch

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _HERE)
from model import RViTPaperModel                       # noqa: E402
from config.loader import load_checkpoint_weights      # noqa: E402
from envs import make_env                              # noqa: E402

CK = os.path.expanduser("~/rvit_plus_checkpoints")
OUT = os.path.join(_HERE, "analysis", "deepdive_out")
T = 7
VARIANTS = [
    ("standard",  "paper_vae_frozen",    dict(feedback="multiplicative")),
    ("affine",    "paper_affine_vae",    dict(feedback="affine")),
    ("dualhead",  "paper_dualhead_vae",  dict(feedback="dualhead")),
    ("two_lstm",  "paper_2lstm_vae",     dict(feedback="multiplicative", two_lstm=True)),
    ("crossattn", "paper_crossattn_vae", dict(feedback="crossattn")),
    ("dualmem",   "paper_dualmem_vae",   dict(feedback="dualmem")),
]


def spatial_attn(feedback, out):
    A = out["attn"][0]
    if isinstance(A, list):              # dualhead → [sensory, feedback]; read the sensory head
        A = A[0]
    a = A[0]                             # (Q, K)
    if feedback in ("crossattn", "dualmem"):
        a = a[:, :4]                     # attend to the image/X keys only (first N)
    return a.mean(0).detach().cpu().numpy()   # (4,) attention received per spatial patch


def behaviour(m, env, N=250):
    hit = ch = fa = nc = 0; rts = []
    for _ in range(N):
        o = env.reset(); s = m.init_states(1); done = False; r = 0; pt = None; t = 0; cflag = env.change_true
        while not done:
            x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
            with torch.no_grad():
                out = m.rl_step(x, s); s = out["new_states"]; a = int(torch.argmax(out["actor_logits"], -1))
            o, r, done, _ = env.step(a)
            if a == 1 and pt is None: pt = t
            t += 1
        if cflag == 1:
            ch += 1; hit += (r > 0)
            if r > 0 and pt is not None: rts.append(pt)
        else:
            nc += 1; fa += (pt is not None and r == 0)
    return dict(correct=(hit+ (nc-fa))/(ch+nc), hit=hit/max(ch,1), fa=fa/max(nc,1),
                rt=float(np.median(rts)) if rts else float("nan"))


def attn_timecourse(m, env, feedback, change, N=200):
    """100%-reliable cue; record attention to the CUED patch vs the others over time.
    Forced-wait (action 0) so the timecourse is not truncated by an early press."""
    cued = np.zeros(T); other = np.zeros(T)
    for _ in range(N):
        o = env.reset()                                   # env picks cue_index ∈ {0,3}
        cue = env.cue_index; rest = [j for j in range(4) if j != cue]
        env.proportion = 1.0                              # fully reliable cue (full ring)
        env.change_true = 1 if change else 0
        env.change_index = cue                            # change at the cued location
        if change: env.orientation_change = 25.0 * (1 if np.random.rand() < .5 else -1)
        s = m.init_states(1)
        for t in range(T):
            x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
            with torch.no_grad():
                out = m.rl_step(x, s, return_attn=True); s = out["new_states"]
            a = spatial_attn(feedback, out)
            cued[t] += a[cue]; other[t] += a[rest].mean()
            o, _, done, _ = env.step(0)
    return cued / N, other / N


def main():
    env = make_env("validity4", curriculum=False)
    rows = []; S1 = {}
    for name, d, kw in VARIANTS:
        path = sorted(glob.glob(f"{CK}/{d}/*.pt"), key=os.path.getmtime, reverse=True)
        if not path:
            print(f"[{name}] no checkpoint, skipping"); continue
        path = path[0]
        try:
            m = RViTPaperModel(n_quantiles=5, seq_len=7, **kw)
            load_checkpoint_weights(m, path, strict=True, device=torch.device("cpu")); m.eval()
        except Exception as e:
            print(f"[{name}] load failed: {e}"); continue
        it = torch.load(path, map_location="cpu", weights_only=False).get("iter")
        beh = behaviour(m, env)
        ch_c, ch_o = attn_timecourse(m, env, kw["feedback"], change=True)
        nc_c, nc_o = attn_timecourse(m, env, kw["feedback"], change=False)
        orient = float(nc_c[3:5].mean() - 0.25)           # pre-change cued-patch bias (no change)
        spike = float(ch_c[5] - ch_c[4])                  # change-locked jump at t5
        rows.append((name, it, beh["correct"], beh["hit"], beh["fa"], beh["rt"], orient, spike))
        S1[name] = dict(change_cued=ch_c, change_other=ch_o,
                        nochange_cued=nc_c, nochange_other=nc_o)
        print(f"[{name}] iter={it} correct={beh['correct']:.3f} hit={beh['hit']:.3f} "
              f"FA={beh['fa']:.3f} RT={beh['rt']:.1f} | cue-orient(NC,t3-4)={orient:+.3f} "
              f"change-spike(t5)={spike:+.3f}")
        del m
    np.savez(os.path.join(OUT, "variant_analysis.npz"),
             rows=np.array(rows, dtype=object), S1=S1)
    print("\n=== SUMMARY ===")
    print(f"{'variant':>10} {'iter':>6} {'correct':>8} {'hit':>6} {'FA':>6} {'RT':>5} "
          f"{'cue-orient':>11} {'chg-spike':>10}")
    for r in rows:
        print(f"{r[0]:>10} {str(r[1]):>6} {r[2]:>8.3f} {r[3]:>6.3f} {r[4]:>6.3f} {r[5]:>5.1f} "
              f"{r[6]:>+11.3f} {r[7]:>+10.3f}")
    print("\ncue-orient > 0 ⇒ attends the cued location BEFORE the change (cue-driven).")


if __name__ == "__main__":
    main()
