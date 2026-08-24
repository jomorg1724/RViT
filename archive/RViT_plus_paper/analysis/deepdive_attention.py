"""
Deep-dive #2 — attention allocation dynamics (Morgan & Herman attention figure).

The multiplicative ViT exposes a per-frame 4-patch attention map (softmax(QKᵀ), patch→patch).
attention_to_patch_j = mean_i attn[i,j] gives a 2×2 spatial saliency map per frame. We force
the agent to WAIT (so every trial yields the full 7-frame timecourse) and track attention to
the CUED vs UNCUED location over time, by cue validity. Paper claim: attention orients to the
cued location after the cue and the orienting scales with cue reliability.
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

CKPT = os.path.expanduser("~/rvit_plus_checkpoints/paper_vae_frozen")
OUT = os.path.join(_HERE, "analysis", "deepdive_out")
os.makedirs(OUT, exist_ok=True)
VALIDITIES = [0.25, 0.5, 0.75, 1.0]
T = 7
N = 200


def main():
    ck = sorted(glob.glob(CKPT + "/*.pt"), key=os.path.getmtime)[-1]
    m = RViTPaperModel(n_quantiles=5, seq_len=7, feedback="multiplicative")
    load_checkpoint_weights(m, ck, strict=True, device=torch.device("cpu")); m.eval()
    env = make_env("validity4", curriculum=False)

    att_cued = {v: np.zeros(T) for v in VALIDITIES}
    att_unc = {v: np.zeros(T) for v in VALIDITIES}
    maps = {v: np.zeros((T, 4)) for v in VALIDITIES}     # full 4-patch map over time

    print("[dd-attn] collecting attention timecourses ...")
    for val in VALIDITIES:
        c = 0
        for _ in range(N):
            o = env.reset(); env.proportion = float(val); env.change_true = 1
            cue = env.cue_index; opp = 3 if cue == 0 else 0
            env.change_index = cue
            env.orientation_change = 32.0 * (1 if np.random.rand() < 0.5 else -1)
            s = m.init_states(1)
            for t in range(T):
                x = torch.from_numpy(o).float().permute(2, 0, 1).unsqueeze(0)
                with torch.no_grad():
                    out = m.rl_step(x, s, return_attn=True); s = out["new_states"]
                    amap = out["attn"][0][0].mean(0).numpy()      # (4,) attention to each patch
                att_cued[val][t] += amap[cue]; att_unc[val][t] += amap[opp]
                maps[val][t] += amap
                o, _, done, _ = env.step(0)                       # FORCE WAIT → full timecourse
                if done: break
            c += 1
        att_cued[val] /= c; att_unc[val] /= c; maps[val] /= c

    np.savez(os.path.join(OUT, "attention.npz"),
             att_cued=np.array([att_cued[v] for v in VALIDITIES]),
             att_unc=np.array([att_unc[v] for v in VALIDITIES]),
             maps=np.array([maps[v] for v in VALIDITIES]), validities=VALIDITIES)

    print("\n=== attention to CUED location over time, by validity (cue at t=1, stim t=3-6) ===")
    print("        " + "".join(f"  t{t}" for t in range(T)))
    for v in VALIDITIES:
        print(f"val {int(v*100):>3}% " + "".join(f"{att_cued[v][t]:5.2f}" for t in range(T)))
    print("\ncued−uncued orienting at the change frame (t=5), by validity:")
    for v in VALIDITIES:
        print(f"  {int(v*100):>3}%: {att_cued[v][5]-att_unc[v][5]:+.3f}")

    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        for vi, v in enumerate(VALIDITIES):
            ax[0].plot(range(T), att_cued[v], "-o", color=plt.cm.viridis(vi/3), label=f"{int(v*100)}%")
        ax[0].axvline(1, ls=":", c="gray"); ax[0].text(1.05, ax[0].get_ylim()[1]*0.95, "cue", color="gray")
        ax[0].set(title="Attention to CUED location over time", xlabel="frame t", ylabel="attention"); ax[0].legend(title="validity")
        for vi, v in enumerate(VALIDITIES):
            ax[1].plot(range(T), att_cued[v]-att_unc[v], "-o", color=plt.cm.viridis(vi/3), label=f"{int(v*100)}%")
        ax[1].axhline(0, ls="-", c="k", lw=0.5)
        ax[1].set(title="Cued − uncued orienting over time", xlabel="frame t", ylabel="Δ attention"); ax[1].legend(title="validity")
        fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_attention.pdf"))
        print(f"\n[dd-attn] figure → {OUT}/fig_attention.pdf")
    except Exception as e:
        print(f"[dd-attn] figure skipped: {e}")
    print("[dd-attn] done.")


if __name__ == "__main__":
    main()
