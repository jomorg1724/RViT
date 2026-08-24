"""dd9 PSYCHOMETRICS for the 9-stimulus (3x3 / vda9) task — the SS9 analogue of the conv dd4.
P(declare change) vs change magnitude |Δθ| for VALID (change@cued) vs INVALID (change@uncued corner),
plus FA and detection-latency (RT) by validity. Mirrors RViT_plus_paper_jepa_conv/deepdive/dd4_psychometric.py
exactly in protocol; reuses the model/env handling that dd9_attn.py already validated.

Run (ONE job, machine free — DO NOT stack on live training):
  OMP_NUM_THREADS=3 .venv/bin/python RViT_plus_paper_jepa_grid9/deepdive9/dd9_psych.py <snapshot.pt> crossattn1
"""
import os, sys, numpy as np, torch, torch.nn as nn
torch.set_num_threads(3)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
_HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(_HERE))
from model import RViTPaperModel
from envs import make_env

SNAP = sys.argv[1]; FB = sys.argv[2] if len(sys.argv) > 2 else "crossattn1"
FIGS = os.path.join(_HERE, "figs"); os.makedirs(FIGS, exist_ok=True)
MAGS = [0, 4, 8, 16, 28, 44, 64]; N = 128; CHANGE_FRAME = 5
UNC = {0: 8, 8: 0}                          # cue corner -> opposite (uncued) corner

# --- load (auto-match out_norm, mirrors dd9_attn.py) ---
ck = torch.load(SNAP, map_location="cpu", weights_only=False); sd = ck["model_state_dict"]
m = RViTPaperModel(cell="xlstm", feedback=FB, n_quantiles=5, seq_len=7, jepa_n_heads=4, jepa_proto_dim=256,
                   frame_repeat=1, d_mem=128, conv_frontend=True, grid_rows=3, grid_cols=3, image_size=75)
if "front.out_norm.bias" in sd and not isinstance(m.front.out_norm, nn.LayerNorm): m.front.out_norm = nn.LayerNorm(128)
r = m.load_state_dict(sd, strict=False); m.eval()
assert not r.missing_keys and not r.unexpected_keys, (r.missing_keys, r.unexpected_keys)
IT = ck.get("iter"); print(f"[dd9_psych {FB}] iter={IT}")

def press_time(cue, change_idx, mag, prop=1.0, change_true=1):
    """One greedy episode with a FORCED cue/change; return the frame the model declares (a==1), else -1."""
    e = make_env("vda9"); o = e.reset()
    while e.change_true != change_true: o = e.reset()
    e.cue_index = cue; e.cue_color = "red"; e.proportion = prop
    if change_true: e.change_index = change_idx; e.orientation_change = mag
    o = e._next_observation()                # frame-0 obs reflecting the forced cue (mirrors dd9_attn.mkvid)
    s = m.init_states(1)
    for t in range(7):
        x = torch.from_numpy(o.astype(np.float32)).permute(2, 0, 1).unsqueeze(0)
        with torch.no_grad():
            st = m.rl_step(x, s); a = int(st["actor_logits"][0].argmax()); s = st["new_states"]
        o, _, d, _ = e.step(a)
        if a == 1: return t                  # declared change at frame t
        if d: break
    return -1

def rate(cue, change_idx, mag, prop=1.0, n=N):
    pr = np.array([press_time(cue, change_idx, mag, prop) for _ in range(n)])
    hit = pr >= CHANGE_FRAME
    return float(hit.mean()), (float(pr[hit].mean()) if hit.any() else np.nan)

# VALID (change@cued) vs INVALID (change@uncued corner), averaged over cue in {P0, P8}
valid_p, valid_rt, inval_p, inval_rt = [], [], [], []
for mg in MAGS:
    vp, vr, ip, ir = [], [], [], []
    for cue, unc in [(0, 8), (8, 0)]:
        p, rt = rate(cue, cue, mg); vp.append(p); vr.append(rt)
        p, rt = rate(cue, unc, mg); ip.append(p); ir.append(rt)
    valid_p.append(np.mean(vp)); valid_rt.append(np.nanmean(vr))
    inval_p.append(np.mean(ip)); inval_rt.append(np.nanmean(ir))
fa = np.mean([(np.array([press_time(cue, -1, 0.0, 1.0, change_true=0) for _ in range(N)]) >= 0).mean() for cue in [0, 8]])

fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
ax[0].plot(MAGS, valid_p, "o-", c="tab:green", label="VALID (change@cued)")
ax[0].plot(MAGS, inval_p, "s-", c="tab:red", label="INVALID (change@uncued)")
ax[0].axhline(fa, ls="--", c="gray", label=f"FA (no-change)={fa:.2f}")
ax[0].set_xlabel("change magnitude |Δθ| (deg)"); ax[0].set_ylabel("P(declare change)"); ax[0].set_ylim(-.02, 1.02)
ax[0].set_title("Psychometric: cueing benefit (prop 1.0)", fontsize=9); ax[0].legend(fontsize=7)
ax[1].plot(MAGS, valid_rt, "o-", c="tab:green", label="VALID"); ax[1].plot(MAGS, inval_rt, "s-", c="tab:red", label="INVALID")
ax[1].set_xlabel("change magnitude |Δθ| (deg)"); ax[1].set_ylabel("mean press frame (RT)")
ax[1].set_title("Detection latency by validity", fontsize=9); ax[1].legend(fontsize=7)
fig.suptitle(f"VALID vs INVALID psychometrics — grid9 (3x3) {FB} iter {IT}", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(FIGS, f"dd9_psychometric_{FB}.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

np.savez(os.path.join(_HERE, f"summary_dd9_psych_{FB}.npz"), iter=IT, mags=MAGS, valid_p=valid_p, inval_p=inval_p,
         valid_rt=valid_rt, inval_rt=inval_rt, fa=fa)
print("MAGS      :", MAGS)
print("VALID P   :", [round(x, 3) for x in valid_p])
print("INVALID P :", [round(x, 3) for x in inval_p])
print("FA(no-chg):", round(float(fa), 3))
print(f"saved dd9_psychometric_{FB}.png + summary_dd9_psych_{FB}.npz")
