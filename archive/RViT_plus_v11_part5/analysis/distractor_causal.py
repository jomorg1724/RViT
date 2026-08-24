"""Causal attention perturbation. We inject a pre-softmax bias onto the salience
stream's memory keys for a chosen side, parametrically forcing attention toward or
away from it, and measure the behavioral consequence on the SAME (seeded) trials.

Central test: forcing attention onto the UNCUED (distractor) side should induce
false alarms — proving the agent's spatial filtering is causally protective. We
also boost the CUED side as a comparison. To bias a cue-dependent side with a single
global bias, we boost a fixed absolute side {2,3} or {0,1} and recombine by cue side:
on cue='left' the distractor side is {2,3}; on cue='right' it is {0,1}."""
import os, sys, numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "/Users/jonathanmorgan/AttentionManuscript")
from RViT_plus_v11_part5.analysis import distractor_dd as dd
from RViT_plus_v11_part5.env import ChangeDetectionEnv, SIDE_QUADRANTS

OUT = "/Users/jonathanmorgan/AttentionManuscript/RViT_plus_v11_part5/analysis/deepdive/figs"
device = torch.device("cpu"); torch.manual_seed(0)
model = dd.build_model(dd.load_config(), device)
it = dd.load_checkpoint(model, dd.DEFAULT_CKPT, device)
print(f"loaded v11_part5 (iter {it})")

N = 1000
qidx = dd.quadrant_token_indices(model.patch_embed.grid_h, model.patch_embed.grid_w)
Ntok = model.n_tokens; Hh = model.encoder.n_heads

def seeded_envs(seeds):
    envs = []
    for s in seeds:
        np.random.seed(int(s)); e = ChangeDetectionEnv(distractor_prob=0.5); e.reset(); envs.append(e)
    obs0 = [e._next_observation() for e in envs]
    return envs, obs0

def sal_bias_for_quads(quads, value):
    b = torch.zeros(Hh, 2 * Ntok, device=device)
    for q in quads:
        b[:, Ntok + qidx[q]] = value          # H2 half of the salience keys
    return {"sal": b, "td": None}

rng = np.random.RandomState(123)
seeds = rng.randint(0, 2**31 - 1, size=N)

def run(bias):
    envs, obs0 = seeded_envs(seeds)
    return dd.record_rollout(model, envs, obs0, device, policy="argmax", attn_bias=bias, run_full=True)

MAGS = [0.0, 2.0, 4.0, 6.0]
# For each magnitude, boost {2,3} and boost {0,1}; recombine into distractor-boost / cued-boost.
res = {"dist_fa": [], "dist_hit": [], "cued_fa": [], "cued_hit": []}
for b in MAGS:
    R23 = run(sal_bias_for_quads([2, 3], b))
    R01 = run(sal_bias_for_quads([0, 1], b))
    def engaged_target(R):
        col = R["cue_color"].astype(str)
        return R["change_true"].astype(bool) & np.isin(col, ["red", "green"])
    cue23 = R23["cue_position"]; cue01 = R01["cue_position"]
    et23 = engaged_target(R23); et01 = engaged_target(R01)
    # distractor-side boosted: cue=left in boost{2,3}  +  cue=right in boost{0,1}
    dmask23 = et23 & (cue23 == "left");  dmask01 = et01 & (cue01 == "right")
    # cued-side boosted: cue=right in boost{2,3}  +  cue=left in boost{0,1}
    cmask23 = et23 & (cue23 == "right"); cmask01 = et01 & (cue01 == "left")
    dist_fa = np.concatenate([R23["premature"][dmask23], R01["premature"][dmask01]])
    dist_hit = np.concatenate([R23["hit"][dmask23], R01["hit"][dmask01]])
    cued_fa = np.concatenate([R23["premature"][cmask23], R01["premature"][cmask01]])
    cued_hit = np.concatenate([R23["hit"][cmask23], R01["hit"][cmask01]])
    res["dist_fa"].append(dist_fa.mean()); res["dist_hit"].append(dist_hit.mean())
    res["cued_fa"].append(cued_fa.mean()); res["cued_hit"].append(cued_hit.mean())
    print(f"  boost={b:+.0f}  DISTRACTOR-side: FA={dist_fa.mean():.3f} hit={dist_hit.mean():.3f}  "
          f"(n={len(dist_fa)})   CUED-side: FA={cued_fa.mean():.3f} hit={cued_hit.mean():.3f} (n={len(cued_fa)})")

print("\n========== CAUSAL SUMMARY ==========")
print(f"  forcing attention onto the DISTRACTOR side: FA {res['dist_fa'][0]:.3f} (baseline) "
      f"-> {res['dist_fa'][-1]:.3f} (boost {MAGS[-1]:+.0f})  = induced distractor capture")
print(f"  forcing attention onto the CUED side:       FA {res['cued_fa'][0]:.3f} -> {res['cued_fa'][-1]:.3f}; "
      f"hit {res['cued_hit'][0]:.3f} -> {res['cued_hit'][-1]:.3f}")

fig, ax = plt.subplots(1, 2, figsize=(10, 4.3))
ax[0].plot(MAGS, res["dist_fa"], "o-", color="#de2d26", label="distractor-side boosted")
ax[0].plot(MAGS, res["cued_fa"], "s--", color="#2c7fb8", label="cued-side boosted")
ax[0].set_xlabel("attention bias injected (logits)"); ax[0].set_ylabel("false-alarm rate (engaged trials)")
ax[0].set_title("A  Forcing distractor attention induces FAs", loc="left", fontweight="bold")
ax[0].legend(fontsize=8, frameon=False)
ax[1].plot(MAGS, res["dist_hit"], "o-", color="#de2d26", label="distractor-side boosted")
ax[1].plot(MAGS, res["cued_hit"], "s--", color="#2c7fb8", label="cued-side boosted")
ax[1].set_xlabel("attention bias injected (logits)"); ax[1].set_ylabel("hit rate (engaged trials)")
ax[1].set_title("B  Effect on target detection", loc="left", fontweight="bold")
ax[1].legend(fontsize=8, frameon=False)
for a in ax:
    a.spines["top"].set_visible(False); a.spines["right"].set_visible(False); a.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(f"{OUT}/causal.png", dpi=160, bbox_inches="tight")
plt.savefig(f"{OUT}/causal.pdf", bbox_inches="tight")
print(f"saved {OUT}/causal.png")
np.savez(f"{OUT}/causal_summary.npz", mags=MAGS, **{k: np.array(v) for k, v in res.items()})
